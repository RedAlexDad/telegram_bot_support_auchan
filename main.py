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
# from SpeechKit.speechkit import voice_to_text, text_to_voice
# Распознавание изображение
from YandexVision.Vision import Vision
# БД PostgreSQL
# from Database.ClassDatabase import DatabaseLogs
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
    # DB = DatabaseLogs()
    # DB.connect()
    # DB.drop_table()
    # DB.create_table()

    ID_CLIENT = int(message.from_user.id)
    # DB.insert_client(ID_CLIENT, str(datetime.now()), 'last_time')

    # Голосовое распознавание
    # VtoT = voice_to_text()
    # Синтез речи
    # TtoV = text_to_voice()

    @bot.message_handler(content_types=["text"])
    def echo(message):
        chat_auchan.prompt(content=message.text)

        bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        # Сохранение файла голосового синтеза

        # save_file_speech(message, TtoV, chat_auchan)

        # Заполнение данных
        # INSERT_DB(message, chat_auchan, DB, ID_CLIENT)


    @bot.message_handler(content_types=['voice'])
    def voice_processing(message):
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('SpeechKit/speech.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)

        # VtoT.translate()

        # if (VtoT.text == None or VtoT.text == ''):
        #     bot.send_message(message.chat.id, f'Повторите попытку. Не удалось распознать голосовое сообщение.')
        # else:
        #     # Отправляем текст с голосового сообщения
        #     bot.send_message(message.chat.id, f'Текст с голосового сообщения: {VtoT.text}')

        # print('prompt:', VtoT.text)
        # bot.send_message(message.chat.id, f'Ваш вопрос: {VtoT.text}')

        # chat_auchan.prompt(content=VtoT.text, voice_status=True)

        bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        # Сохранение файла голосового синтеза
        # save_file_speech(message, TtoV, chat_auchan)

        # Заполнение данных
        # INSERT_DB(message, chat_auchan, DB, ID_CLIENT, voice_status=True)

    # Если пользователь прислал фото, то закидываем его в БД
    @bot.message_handler(content_types=["photo"])
    def echo(message):
        file_info = bot.get_file(message.photo[-1].file_id)
        file_id = message.photo[-1].file_id
        downloaded_file = bot.download_file(file_info.file_path)
        file_extension = file_info.file_path.split(".")[-1]

        # Получите байтовое представление файла
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

        bot.reply_to(message, "Фото сохранено и принято. Передано в службу поддержки. Ожидайте решения.")

        CV = Vision(IAM_TOKEN, FOLDER_ID)

        # Получение данных фото с обалка
        image_data = SDB.give_object(bucket_name=bucket_name, file_name=object_name)
        # Получение текстового значения
        json_data = CV.request_analyze(image_data=image_data)

        text = ' '.join(CV.extract_text(json_data))

        # Отправляем текст после распознавание фотографии
        # bot.send_message(message.chat.id, f'ТЕКСТ С ФОТО: \n {text}')

        chat_auchan.prompt(content=text, photo_status=True)

        bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        # Сохранение файла голосового синтеза
        # save_file_speech(message, TtoV, chat_auchan)

        # Заполнение данных
        # INSERT_DB(message, chat_auchan, DB, ID_CLIENT, name_file_photo=f'{file_id}.{file_extension}', photo_status=True)

@bot.message_handler(commands=['test'])
def start(message):
    SDB = StorageDB()

    image_data = SDB.give_object(bucket_name=bucket_name, file_name='photo/testphoto.jpg')

    CV = Vision(IAM_TOKEN, FOLDER_ID)

    json_data = CV.request_analyze(image_data=image_data)

    text = ' '.join(CV.extract_text(json_data))

    bot.send_message(message.chat.id, f'{text}')


def save_file_speech(message, TtoV, chat_auchan):
    with open('SpeechKit/speech.ogg', "wb") as f:
        for audio_content in TtoV.translate(chat_auchan.chat_response):
            f.write(audio_content)

    bot.send_voice(message.from_user.id, open('SpeechKit/speech.ogg', 'rb'))


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

# def INSERT_DB(message, chat_auchan, DB, ID_CLIENT, name_file_photo=None, voice_status=False, photo_status=False):
#     DB.connect()
#     DB.insert_dialog(
#         question=message.text,
#         answer=chat_auchan.chat_response,
#         intent=chat_auchan.intent,
#         common_token=chat_auchan.conv_history_tokens,
#         time_dialog=str(datetime.now()),
#         voice_status=voice_status,
#         photo_status=photo_status,
#         name_file_photo=name_file_photo,
#         ID_client=DB.ID_client
#     )
#
#     if (chat_auchan.end_dialog):
#         show_smiley_keyboard(message.chat.id)
#         DB.update_correspondence_end_time(str(datetime.now()), DB.ID_client)
#         chat_auchan.end_dialog = False
#
#     DB.select_all()
#     DB.close()



def save_comment(message, emoji):
    comment = message.text
    comments[emoji] = comment
    with open('comments.json', 'w') as file:
        json.dump(comments, file)
    bot.send_message(message.chat.id, 'Спасибо за комментарий! Мы ценим Ваше мнение.')



bot.polling(none_stop=True)
