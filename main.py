import os
import telebot
from telebot import types
import json
import io
import time
from datetime import datetime
from tabulate import tabulate


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

# Здесь хранится статус смайлика (статус обратного связи после завершения диалога)
smile_status = ''

# Создание БД
DB = DatabaseLogs()


# Справочник
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, HELP)

# Меню администратора
@bot.message_handler(commands=['administrator'])
def administrator(message):
    bot.send_message(message.chat.id, f'Приветствую Вас! Администратор, {message.from_user.first_name}. Введите специальные команды для взаимодействия с БД.')

    @bot.message_handler(content_types=["text"])
    def echo(message):
        # Удаление БД
        if(message.text in 'drop'):
            try:
                DB.connect()
                DB.drop_table()
                DB.close()
                bot.send_message(message.chat.id, '[INFO] Успешно удалены таблицы в базе данных')
            except Exception as ex:
                bot.send_message(message.chat.id, ex)
        # Создание новой таблицы
        if(message.text in 'create'):
            try:
                DB.connect()
                DB.create_table()
                DB.close()
                bot.send_message(message.chat.id, '[INFO] Успешно созданы таблицы в базе данных')
            except Exception as ex:
                bot.send_message(message.chat.id, ex)
        if(message.text in 'read'):
            try:
                DB.connect()
                DB.select_all()
                client, dialog = DB.select_all()

                headers_client = ['ID', 'ID_user', 'start_time', 'end_time', 'smile_status']
                headers_dialogs = ['ID', 'question', 'answer', 'intent', 'common_token', 'time_dialog', 'voice_file', 'photo_file', 'tonality', 'tonality_metric', 'ID_client']

                table = tabulate(client, headers_client, tablefmt="pretty")
                print(table)
                bot.send_message(message.chat.id, table)

                table = tabulate(dialog, headers_dialogs, tablefmt="pretty")
                print(table)
                bot.send_message(message.chat.id, table)

                DB.close()
            except Exception as ex:
                bot.send_message(message.chat.id, ex)

@bot.message_handler(commands=['administrator_request'])
def administrator_request(message):
    bot.send_message(message.chat.id, f'Введите здесь запрос для взаимодействия с БД')
    @bot.message_handler(content_types=["text"])
    def echo(message):
        try:
            DB.connect()
            response, column_names = DB.request(message.text)
            if(column_names==''): column_names='*'
            table = tabulate(response, column_names, tablefmt="pretty")
            print(table)
            bot.send_message(message.chat.id, table)
            DB.close()
        except Exception as ex:
            bot.send_message(message.chat.id, ex)


# chatGPT
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, text=f"Привет, {message.from_user.first_name}! Я бот Ашан, cпрашивайте, буду рад помочь!")
    chat_auchan = chatGPT(message.from_user.id)

    # Подключение к БД
    DB.connect()

    # Получение уникального идентификатора пользователя
    ID_CLIENT = int(message.from_user.id)
    # Заполнения данных в БД
    DB.insert_client(ID_CLIENT, str(datetime.now()), 'last_time', smile_status)

    # Голосовое распознавание
    VtoT = voice_to_text()
    # Синтез речи
    TtoV = text_to_voice()

    @bot.message_handler(content_types=["text"])
    def echo(message):
        max_count_attempt = 10
        # Получение промпта с чатГПТ
        while(max_count_attempt != 0):
            try:
                chat_auchan.prompt(content=message.text)
                break
            except:
                msg = bot.send_message(message.chat.id, f'Большие нагрузки на бот.')
                # Устанавливаем начальное значение времени в секундах
                time_second = 60
                while time_second > 0:
                    # Через некоторое время меняем текст сообщения
                    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=f"Ожидайте. Осталось {time_second} секунд")
                    # Подождем 1 секунду
                    time.sleep(1)
                    # Уменьшим счетчик секунд на 1
                    time_second -= 1
                bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=f"Повторная попытка обратиться к боту")
                max_count_attempt -= 1

        if(max_count_attempt==0):
            bot.send_message(message.chat.id, f'У бота нагрузки огромные. Обратитесь к нему позже. Благодарю за понимание!')

        # Отправка сообщений в ТГ БОТ
        bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        # Вызов функции для синтеза речи с текста и отправка
        make_voice_and_push(message, chat_auchan.chat_response, TtoV)

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



        max_count_attempt = 10
        # Получение промпта с чатГПТ
        while (max_count_attempt != 0):
            try:
                chat_auchan.prompt(content=VtoT.text, voice_file=True)
                break
            except:
                msg = bot.send_message(message.chat.id, f'Большие нагрузки на бот.')
                # Устанавливаем начальное значение времени в секундах
                time_second = 60
                while time_second > 0:
                    # Через некоторое время меняем текст сообщения
                    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                          text=f"Ожидайте. Осталось {time_second} секунд")
                    # Подождем 1 секунду
                    time.sleep(1)
                    # Уменьшим счетчик секунд на 1
                    time_second -= 1
                bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                      text=f"Повторная попытка обратиться к боту")
                max_count_attempt -= 1

        if (max_count_attempt == 0):
            bot.send_message(message.chat.id,
                             f'У бота нагрузки огромные. Обратитесь к нему позже. Благодарю за понимание!')

        bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        # Вызов функции для синтеза речи с текста и отправка
        make_voice_and_push(message, chat_auchan.chat_response, TtoV)

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

        max_count_attempt = 10
        # Получение промпта с чатГПТ
        while (max_count_attempt != 0):
            try:
                chat_auchan.prompt(content=text, photo_file=True)
                break
            except:
                msg = bot.send_message(message.chat.id, f'Большие нагрузки на бот.')
                # Устанавливаем начальное значение времени в секундах
                time_second = 60
                while time_second > 0:
                    # Через некоторое время меняем текст сообщения
                    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                          text=f"Ожидайте. Осталось {time_second} секунд")
                    # Подождем 1 секунду
                    time.sleep(1)
                    # Уменьшим счетчик секунд на 1
                    time_second -= 1
                bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                      text=f"Повторная попытка обратиться к боту")
                max_count_attempt -= 1

        if (max_count_attempt == 0):
            bot.send_message(message.chat.id,
                             f'У бота нагрузки огромные. Обратитесь к нему позже. Благодарю за понимание!')

        bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        # Вызов функции для синтеза речи с текста и отправка
        make_voice_and_push(message, chat_auchan.chat_response, TtoV)

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
    # Объявляем переменную как глобальную
    global smile_status
    if call.data == 'sad':
        bot.send_message(call.message.chat.id, 'Жаль, что Вы остались недовольны обслуживанием! Будем признательны, если Вы оставите комментарий. \
            Так мы сможем учесть Ваши замечания и пожелания!')
        bot.send_message(call.message.chat.id, 'Спасибо за комментарий! Мы ценим Ваше мнение.')
        smile_status = 'sad'
    elif call.data == 'unhappy':
        bot.send_message(call.message.chat.id, 'Жаль, что Вы остались недовольны обслуживанием! Будем признательны, если Вы оставите комментарий. \
            Так мы сможем учесть Ваши замечания и пожелания!')
        bot.send_message(call.message.chat.id, 'Спасибо за комментарий! Мы ценим Ваше мнение.')
        smile_status = 'unhappy'
    elif call.data == 'neutral':
        bot.send_message(call.message.chat.id, 'Благодарим Вас за оценку!')
        smile_status = 'neutral'
    elif call.data == 'happy':
        bot.send_message(call.message.chat.id, 'Благодарим Вас за оценку! Всегда рады помочь!')
        smile_status = 'happy'
    elif call.data == 'smiling':
        bot.send_message(call.message.chat.id, 'Благодарим Вас за оценку! Всегда рады помочь!')
        smile_status = 'smiling'

# Синтез речи с текста и отправка
def make_voice_and_push(message, text, TtoV):
    # Преобразуем текст в речь с использованием Яндекс SpeechKit. А также преобразуем в побайтовом виде
    audio_data = b''.join(TtoV.translate(text))
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

    emotions_data = chat_auchan.emotion_text({"inputs": message.text})
    # Используем цикл для вставки данных в базу данных
    for emotion in emotions_data[0]:
        label = emotion['label']
        score = emotion['score']
        DB.insert_emotion(label=label, score=score, ID_dialog=DB.ID_dialog)

    if (chat_auchan.end_dialog):
        show_smiley_keyboard(message.chat.id)
        DB.update_correspondence_end_time(str(datetime.now()), smile_status, DB.ID_client)
        chat_auchan.end_dialog = False

    DB.close()


if __name__ == "__main__":
    bot.polling(none_stop=True)
