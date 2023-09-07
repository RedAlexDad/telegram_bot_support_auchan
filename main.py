import os
import telebot
from telebot import types
import json
import io
from datetime import datetime

# Конфигурации
from config import TG_BOT_TOKEN, IAM_TOKEN, FOLDER_ID, bucket_name
# ИИ ЧатГПТ
from chatGPT.chatGPT import chatGPT
# Голосовой синтез и распознавание
from SpeechKit.speechkit import voice_to_text, text_to_voice
# Распознавание изображение
from YandexVision.Vision import Vision
# БД PostgreSQL
from Database.ClassDatabase import DatabaseLogs
# Облачное хранилище OBJECT STORAGE
from Database.StorageDB import StorageDB

# Создание бота
bot = telebot.TeleBot(TG_BOT_TOKEN)

HELP = '''
/help - Меню переключателя
/start - chatGPT
'''

# Здесь будут храниться все переписки, которые пользователям не понравилось качество обслуживания
comments = {}

# Справочник
@bot.message_handler(commands=['help'])
def start(message):
    bot.send_message(message.chat.id, HELP)

# chatGPT
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, text=f"Привет, {message.from_user.first_name}! Я бот Ашан, cпрашивайте, буду рад помочь!")
    chat_auchan = chatGPT(message.from_user.id)

    # Создание БД
    DB = DatabaseLogs()
    # Подключение к БД
    DB.connect()
    # Удаление БД
    # DB.drop_table()
    # Создание новой таблицы
    # DB.create_table()

    # Получение уникального идентификатора пользователя
    ID_CLIENT = int(message.from_user.id)
    # Заполнения данных в БД
    DB.insert_client(ID_CLIENT, str(datetime.now()), 'last_time')

    # Голосовое распознавание
    VtoT = voice_to_text()
    # Синтез речи
    TtoV = text_to_voice()

    @bot.message_handler(content_types=["text"])
    def echo(message):
        # Получение промпта с чатГПТ
        chat_auchan.prompt(content=message.text)
        # Отправка сообщений в ТГ БОТ
        bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        # Вызов функции для синтеза речи с текста и отправка
        make_voice_and_push(message, TtoV)

        # Заполнение данных
        INSERT_DB(message, chat_auchan, DB)


    @bot.message_handler(content_types=['voice'])
    def voice_processing(message):
        # Получение название файла
        file_info = bot.get_file(message.voice.file_id)
        # Получение идентификатора файла
        file_id = message.voice.file_id
        downloaded_file = bot.download_file(file_info.file_path)
        file_extension = file_info.file_path.split(".")[-1]

        # Получите байтовое представление файла
        data_stream = io.BytesIO(downloaded_file)
        object_name = f'voice/{message.from_user.id}/{file_id}.{file_extension}'

        # Облачная БД
        SDB = StorageDB()

        try:
            SDB.load_object_in_bucket_string(
                bucket_name=bucket_name,
                object_name=object_name,
                body_name=data_stream,
                storage_class='COLD')

        except Exception as ex:
            print(ex)
            bot.send_message(message.from_user.id, f'ERROR: \n {ex}')

        # Получение данных фото с обалка
        voice_data = SDB.give_object(bucket_name=bucket_name, file_name=object_name)

        # Вызов класса для преобразования голосового сообщения в текст
        VtoT.translate(voice_data=voice_data)

        if (VtoT.text == None or VtoT.text == ''):
            bot.send_message(message.chat.id, f'Повторите попытку. Не удалось распознать голосовое сообщение.')
        else:
            # Отправляем текст с голосового сообщения
            bot.send_message(message.chat.id, f'Текст с голосового сообщения: {VtoT.text}')

        print('prompt:', VtoT.text)
        bot.send_message(message.chat.id, f'Ваш вопрос: {VtoT.text}')

        chat_auchan.prompt(content=VtoT.text, voice_file=True)

        bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        # Вызов функции для синтеза речи с текста и отправка
        make_voice_and_push(message, TtoV)

        # Заполнение данных
        INSERT_DB(message, chat_auchan, DB, voice_file=True)

    # Если пользователь прислал фото, то закидываем его в БД
    @bot.message_handler(content_types=["photo"])
    def echo(message):
        # Получение название файла
        file_info = bot.get_file(message.photo[-1].file_id)
        # Получение идентификатора файла
        file_id = message.photo[-1].file_id
        downloaded_file = bot.download_file(file_info.file_path)
        file_extension = file_info.file_path.split(".")[-1]

        # Получение байтовое представление файла
        data_stream = io.BytesIO(downloaded_file)
        object_name = f'photo/{message.from_user.id}/{file_id}.{file_extension}'

        # Облачная БД
        SDB = StorageDB()

        try:
            SDB.load_object_in_bucket_string(
                bucket_name=bucket_name,
                object_name=object_name,
                body_name=data_stream,
                storage_class='COLD')

        except Exception as ex:
            print(ex)
            bot.send_message(message.from_user.id, f'ERROR: \n {ex}')

        # Ответное сообщение к приложенному сообщению
        bot.reply_to(message, "Фото сохранено и принято. Передано в службу поддержки. Ожидайте решения.")

        # Вызов класса для распознавания текстов в фотографии
        CV = Vision(IAM_TOKEN, FOLDER_ID)

        # Получение данных фото с обалка
        image_data = SDB.give_object(bucket_name=bucket_name, file_name=object_name)
        # Получение текстового значения
        json_data = CV.request_analyze(image_data=image_data)

        # Преобразование в текста
        text = ' '.join(CV.extract_text(json_data))

        # Отправляем текст после распознавание фотографии
        # bot.send_message(message.chat.id, f'ТЕКСТ С ФОТО: \n {text}')

        chat_auchan.prompt(content=text, photo_file=True)

        bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        # Вызов функции для синтеза речи с текста и отправка
        make_voice_and_push(message, TtoV)

        # Заполнение данных
        INSERT_DB(message, chat_auchan, DB, photo_file=True)

def show_smiley_keyboard(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    keyboard.add(
        types.InlineKeyboardButton('😢', callback_data='sad'),
        types.InlineKeyboardButton('😞', callback_data='unhappy'),
        types.InlineKeyboardButton('😐', callback_data='neutral'),
        types.InlineKeyboardButton('😊', callback_data='happy'),
        types.InlineKeyboardButton('😃', callback_data='smiling')
    )
    bot.send_message(chat_id, 'Пожалуйста, оцените качество обслуживания:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    chat_id = call.message.chat.id
    if call.data == 'sad':
        bot.send_message(chat_id, 'Жаль, что Вы остались недовольны обслуживанием! Будем признательны, если Вы оставите комментарий. \
            Так мы сможем учесть Ваши замечания и пожелания!')
        bot.register_next_step_handler(call.message, save_comment, call.data)
    elif call.data == 'unhappy':
        bot.send_message(chat_id, 'Жаль, что Вы остались недовольны обслуживанием! Будем признательны, если Вы оставите комментарий. \
            Так мы сможем учесть Ваши замечания и пожелания!')
        bot.register_next_step_handler(call.message, save_comment, call.data)
    elif call.data == 'neutral':
        bot.send_message(call.message.chat.id, 'Благодарим Вас за оценку!')
    elif call.data == 'happy':
        bot.send_message(call.message.chat.id, 'Благодарим Вас за оценку! Всегда рады помочь!')
    elif call.data == 'smiling':
        bot.send_message(call.message.chat.id, 'Благодарим Вас за оценку! Всегда рады помочь!')

# Синтез речи с текста и отправка
def make_voice_and_push(message, TtoV):
    # Преобразуем текст в речь с использованием Яндекс SpeechKit. А также преобразуем в побайтовом виде
    audio_data = b''.join(TtoV.translate(message.text))
    # audio_data = TtoV.translate(chat_auchan.chat_response)
    # Отправляем голосовое сообщение в чат Telegram
    voice_message_stream = io.BytesIO(audio_data)
    # Имя файла для голосового сообщения
    voice_message_stream.name = 'voice.ogg'
    # Отправка голосового сообщения в ТГ БОТ
    bot.send_voice(message.chat.id, voice_message_stream)

# Заполнение данных в БД
def INSERT_DB(message, chat_auchan, DB, voice_file=None, photo_file=None):
    DB.connect()
    DB.insert_dialog(
        question=message.text,
        answer=chat_auchan.chat_response,
        intent=chat_auchan.intent,
        common_token=chat_auchan.conv_history_tokens,
        time_dialog=str(datetime.now()),
        voice_file=str(voice_file),
        photo_file=str(photo_file),
        ID_client=DB.ID_client
    )

    if (chat_auchan.end_dialog):
        show_smiley_keyboard(message.chat.id)
        DB.update_correspondence_end_time(str(datetime.now()), DB.ID_client)
        chat_auchan.end_dialog = False

    DB.select_all()
    DB.close()

def save_comment(message, emoji):
    comment = message.text
    comments[emoji] = comment
    with open('comments.json', 'w') as file:
        json.dump(comments, file)
    bot.send_message(message.chat.id, 'Спасибо за комментарий! Мы ценим Ваше мнение.')


bot.polling(none_stop=True)
