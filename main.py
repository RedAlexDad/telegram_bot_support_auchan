import telebot
from telebot import types

import random
import time

import config

from Llama2.Llama2Class import Llama2
from SpeechKIT.speechkit_voice_to_text import voice_to_text

# Создание бота
bot = telebot.TeleBot(config.telegram_token)

HELP = '''
/start - Меню переключателя
/gpt - CHAT-GPT 
/voice - Перевод с голосового на текст 
/discount - Акция, скидка
'''

# Справочник
@bot.message_handler(commands=['help'])
def start(message):
    bot.send_message(message.chat.id, HELP)


# Меню переключателя
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text="Спросить что-то", callback_data='btn1')
    btn2 = types.InlineKeyboardButton(text="Посмотреть акции, скидки", callback_data='btn2')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id,
                     text=f"Привет, {message.from_user.first_name}! Я бот Ашан, выберите следующие действия",
                     reply_markup=markup)

# Функция переключателя
@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback):
    # Пользовательский идентификатор
    # id_user = str(callback.from_user.id)

    if (callback.data == "btn1"):
        # Пользовательский идентификатор
        id_user = str(callback.from_user.id)
        
        # Чтение файла, чтобы понять вспомнить суть разговора или начать разговор
        Llama2Bot = Llama2(id_user)

        Llama2Bot.readfile(directory_file='*')

        bot.send_message(callback.message.chat.id, 'Спрашивайте, буду рад помочь!')

        @bot.message_handler(content_types=["text"])
        def echo(message):
            # bot.send_message(message.chat.id, f'Ваш ID: {id_user}')
            # print('ID пользователя:', id_user)

            prompt = message.text
            print('prompt:', prompt)
            bot.send_message(message.chat.id, f'Ваш вопрос: {prompt}')

            Llama2Bot.answer(prompt)

            logs = Llama2Bot.logs

            bot.send_message(message.chat.id, f'Ответ: {logs[id_user][0]["answer"]}')

        @bot.message_handler(content_types=['voice'])
        def voice_processing(message):
            VtoT = voice_to_text()

            file_info = bot.get_file(message.voice.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            with open('SpeechKIT/speech.ogg', 'wb') as new_file:
                new_file.write(downloaded_file)

            VtoT.translate()
            text = VtoT.text

            # Отправляем текст с голосового сообщения
            bot.send_message(message.chat.id, f'Текст с голосового сообщения: {text}')

            print('prompt:', text)
            bot.send_message(message.chat.id, f'Ваш вопрос: {text}')

            Llama2Bot.answer(text)

            logs = Llama2Bot.logs

            bot.send_message(message.chat.id, f'Ответ: {logs[id_user][0]["answer"]}')


    elif(callback.data == "btn2"):
        bot.send_message(callback.message.chat.id, 'Список акции (В РАЗРАБОТКЕ)')

    else:
        bot.send_message(callback.chat.id, 'Нет такой команды. Введите /help')


# ЧАТ-ГПТ
@bot.message_handler(commands=['gpt'])
def start(message):
    # Пользовательский идентификатор
    id_user = str(message.from_user.id)

    # Чтение файла, чтобы понять вспомнить суть разговора или начать разговор
    Llama2Bot = Llama2(id_user)

    Llama2Bot.readfile(directory_file='*')

    bot.send_message(message.chat.id, 'Спрашивайте, буду рад помочь!')

    @bot.message_handler(content_types=["text"])
    def echo(message):
        # bot.send_message(message.chat.id, f'Ваш ID: {id_user}')
        # print('ID пользователя:', id_user)

        prompt = message.text
        print('prompt:', prompt)
        bot.send_message(message.chat.id, f'Ваш вопрос: {prompt}')

        Llama2Bot.answer(prompt)

        logs = Llama2Bot.logs

        bot.send_message(message.chat.id, f'Ответ: {logs[id_user][0]["answer"]}')


# ГОЛОСОВОЕ СООБЩЕНИЕ
@bot.message_handler(commands=['voice'])
def start(message):
    bot.send_message(message.chat.id, 'Перевод с голосового сообщения на текст')

    @bot.message_handler(content_types=['voice'])
    def voice_processing(message):
        VtoT = voice_to_text()

        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('SpeechKIT/speech.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)

        VtoT.translate()
        text = VtoT.text

        # Отправляем текст с голосового сообщения
        bot.send_message(message.chat.id, f'Текст с голосового сообщения: {text}')





bot.polling(none_stop=True)

