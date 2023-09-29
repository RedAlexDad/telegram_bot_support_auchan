import os
import telebot
from telebot import types

from config import TG_BOT_TOKEN

from Llama2.Llama2Class import Llama2
from SpeechKIT.speechkit_voice_to_text import voice_to_text
from chatGPT.chatGPT import chatGPT

from database.ClassDatebase import DatabaseLogs
from datetime import datetime

import random

# Создание бота
bot = telebot.TeleBot(TG_BOT_TOKEN)

HELP = '''
/help - Меню переключателя
/chatGPT - chatGPT
/LlamaGPT - LlamaGPT
/voice - Перевод с голосового на текст 
/photo - Сохранение фото в БД
'''

# Справочник
@bot.message_handler(commands=['help'])
def start(message):
    bot.send_message(message.chat.id, HELP)

@bot.message_handler(commands=['DB'])
def start(message):
    bot.send_message(message.chat.id, 'DATEBASE')

    DB = DatabaseLogs()
    DB.connect()
    # DB.drop_table()
    # DB.create_table()

    # ID_correspondence = random.randint(0, 2 ** 31 - 1)
    # ID_CLIENT = random.randint(0, int(message.from_user.id) - 1)
    ID_CLIENT = int(message.from_user.id)

    DB.insert_client(ID_CLIENT)

    DB.insert_correspondence(ID_CLIENT, datetime.now(), 'last_time')

    @bot.message_handler(content_types=["text"])
    def echo(message):
        DB.connect()

        DB.insert_dialog(
            # ID=message.from_user.id,
            # Name=message.from_user.first_name,
            question=message.text,
            answer='answer from gpt',
            intent='all intent',
            common_token=1000,
            time_dialog=str(datetime.now()),
            voice_status=False,
            photo_status=False,
            ID_correspondence=DB.ID_correspondence
        )

        if(message.text in 'пока'):
            DB.update_correspondence_end_time(ID_CLIENT, datetime.now())

        DB.select_all()

        DB.close()





# Меню переключателя
@bot.message_handler(commands=['LlamaGPT'])
def start(message):
    bot.send_message(message.chat.id, text=f"Привет, {message.from_user.first_name}! Я бот Ашан, cпрашивайте, буду рад помочь!")
    # Пользовательский идентификатор
    # id_user = str(callback.from_user.id)

    # Пользовательский идентификатор
    id_user = str(message.from_user.id)

    # Чтение файла, чтобы понять вспомнить суть разговора или начать разговор
    Llama2Bot = Llama2(id_user)
    # Голосовое распознавание
    VtoT = voice_to_text()

    Llama2Bot.readfile(directory_file='*')

    bot.send_message(message.chat.id, '')

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
        print('prompt:', VtoT.text)
        bot.send_message(message.chat.id, f'Ваш вопрос: {VtoT.text}')

        Llama2Bot.answer(VtoT.text)

        logs = Llama2Bot.logs

        bot.send_message(message.chat.id, f'Ответ: {logs[id_user][0]["answer"]}')

# chatGPT
@bot.message_handler(commands=['chatGPT'])
def start(message):
    bot.send_message(message.chat.id, text=f"Привет, {message.from_user.first_name}! Я бот Ашан, cпрашивайте, буду рад помочь!")
    chat_auchan = chatGPT(message.from_user.id)
    # Голосовое распознавание
    VtoT = voice_to_text()

    @bot.message_handler(content_types=["text"])
    def echo(message):
        # bot.send_message(message.chat.id, f'DEBUGGER:\nСообщение: {message.text}')

        chat_auchan.prompt(content=message.text)

        # bot.send_message(message.chat.id, 'DEBUGGER:\nСообщение доставлено')

        # bot.send_message(message.chat.id, f"DEBUGGER:\nТокенов: {chat_auchan.conv_history_tokens}")

        # bot.send_message(message.chat.id, f"DEBUGGER:\n{chat_auchan.intent}")

        bot.send_message(message.chat.id, f'\nАшанчик: {chat_auchan.chat_response}\n')

    @bot.message_handler(content_types=['voice'])
    def voice_processing(message):
        # voice(message)

        VtoT = voice_to_text()

        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('SpeechKIT/speech.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)

        VtoT.translate()

        if (VtoT.text == None or VtoT.text == ''):
            bot.send_message(message.chat.id, f'Повторите попытку. Не удалось распознать голосовое сообщение.')
        else:
            # Отправляем текст с голосового сообщения
            bot.send_message(message.chat.id, f'Текст с голосового сообщения: {VtoT.text}')

        print('prompt:', VtoT.text)
        bot.send_message(message.chat.id, f'Ваш вопрос: {VtoT.text}')

        chat_auchan.dialog(content=VtoT.text)

        bot.send_message(message.chat.id, f'\nАшанчик: {chat_auchan.chat_response}\n')


# ГОЛОСОВОЕ СООБЩЕНИЕ
@bot.message_handler(commands=['voice'])
def start(message):
    bot.send_message(message.chat.id, 'Перевод с голосового сообщения на текст')
    # @bot.message_handler(content_types=['voice'])
    # def voice_processing(message):
    VtoT = voice_to_text()

    @bot.message_handler(content_types=['voice'])
    def voice_processing(message):
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('SpeechKIT/speech.ogg', 'wb') as new_file:
            new_file.write(downloaded_file)

        VtoT.translate()

        if(VtoT.text == None or VtoT.text == ''):
            bot.send_message(message.chat.id, f'Повторите попытку. Не удалось распознать голосовое сообщение.')
        else:
            # Отправляем текст с голосового сообщения
            bot.send_message(message.chat.id, f'Текст с голосового сообщения: {VtoT.text}')

# Инициализация состояния
user_states = {}

# РАЗВЕТВЛЕННОЕ УТОЧНЕНИЕ
@bot.message_handler(commands=['check'])
def start(message):
    bot.send_message(message.chat.id, 'Уточнение с сохранением предыдущего промпта')

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text="Продовольственный товар", callback_data='Продовольственный товар')
    btn2 = types.InlineKeyboardButton(text="Непродовольственный товар", callback_data='Непродовольственный товар')
    btn3 = types.InlineKeyboardButton(text="Чем они отличаются? Подсказать", callback_data='Чем они отличаются? Подсказать')
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, text='Уточните, какой вид товар у Вас?', reply_markup=markup)

    # Инициализация состояния
    user_states[message.from_user.id] = {
        'Вид товара': None,
        'Продукт с действующим сроком годности?': None,
        'Продукт в неповрежденной упаковке?': None,
        'Продукт передан покупателю?': None
    }



# Если пользователь прислал фото, то закидываем его в БД
@bot.message_handler(commands=['photo'])
def start(message):
    bot.send_message(message.chat.id, 'Сохранение фоток в БД')
    @bot.message_handler(content_types=["photo"])
    def echo(message):
        # Проверяем, существует ли папка уже
        if not os.path.exists(f'database_photo/{str(message.from_user.id)}'):
            # Создаем новую папку
            os.mkdir(f'database/photo/{str(message.from_user.id)}')
            # print(f"Папка '{str(message.from_user.id)}' создана.")
        else:
            # print(f"Папка '{str(message.from_user.id)}' уже существует.")
            pass

        file_info = bot.get_file(message.photo[-1].file_id)
        file_id = message.photo[-1].file_id
        downloaded_file = bot.download_file(file_info.file_path)
        file_extension = file_info.file_path.split(".")[-1]

        with open(f'database/photo/{message.from_user.id}/{file_id}.{file_extension}', 'wb') as new_file:
            new_file.write(downloaded_file)

        bot.reply_to(message, "Фото сохранено и принято. Передано в службу поддержки. Ожидайте решения.")

# Функция переключателя
@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback_data(callback):
    # Пользовательский идентификатор
    # id_user = str(callback.from_user.id)
    if (callback.data == "Продовольственный товар"):
        bot.send_message(callback.message.chat.id, 'Вы выбрал продовольственный товар')
        user_states[callback.message.chat.id]['Вид товара'] = callback.data

        # print(user_states)

        if (user_states[callback.message.chat.id]['Продукт с действующим сроком годности?'] == None):
            markup = types.InlineKeyboardMarkup(row_width=2)
            yes = types.InlineKeyboardButton(text="Да", callback_data='Да')
            no = types.InlineKeyboardButton(text="Нет", callback_data='Нет')
            markup.add(yes, no)
            bot.send_message(callback.message.chat.id, text='Продукт с действующим сроком годности?', reply_markup=markup)
        elif (user_states[callback.message.chat.id]['Продукт в неповрежденной упаковке?'] == None):
            markup = types.InlineKeyboardMarkup(row_width=2)
            yes = types.InlineKeyboardButton(text="Да", callback_data='Да')
            no = types.InlineKeyboardButton(text="Нет", callback_data='Нет')
            markup.add(yes, no)
            bot.send_message(callback.message.chat.id, text='Продукт в неповрежденной упаковке?', reply_markup=markup)
        elif (user_states[callback.message.chat.id]['Продукт передан покупателю?'] == None):
            markup = types.InlineKeyboardMarkup(row_width=2)
            yes = types.InlineKeyboardButton(text="Да", callback_data='Да')
            no = types.InlineKeyboardButton(text="Нет", callback_data='Нет')
            markup.add(yes, no)
            bot.send_message(callback.message.chat.id, text='Продукт передан покупателю?', reply_markup=markup)
        else:
            bot.send_message(callback.message.chat.id, text='Данные заполнены. Запрашиваем помощь ИИ по юридическам вопросам.')
            # bot.send_message(callback.message.chat.id, text=f'Ваши ответы: {user_states[callback.message.chat.id]}')



    elif (callback.data == "Непродовольственный товар"):
        user_states[callback.message.chat.id]['Вид товара'] = callback.data
        bot.send_message(callback.message.chat.id, 'Вы выбрал непродовольственный товар')

        markup = types.InlineKeyboardMarkup(row_width=2)
        yes = types.InlineKeyboardButton(text="Да", callback_data='Да')
        no = types.InlineKeyboardButton(text="Нет", callback_data='Нет')
        markup.add(yes, no)
        bot.send_message(callback.message.chat.id, text='Продукт с действующим сроком годности?', reply_markup=markup)

    elif (callback.data == "Чем они отличаются? Подсказать"):
        bot.send_message(callback.message.chat.id, 'Продовольственный товар - продукты в натуральном или переработанном виде, которые употребляются человеком в пищу')
        bot.send_message(callback.message.chat.id, 'Продовольственный товар - товары, которые не предназначены для употребления в пищу; они не являются сырьем для приготовления пищи.')

        markup = types.InlineKeyboardMarkup(row_width=1)
        btn1 = types.InlineKeyboardButton(text="Продовольственный товар", callback_data='btn1')
        btn2 = types.InlineKeyboardButton(text="Непродовольственный товар", callback_data='btn2')
        markup.add(btn1, btn2)
        bot.send_message(callback.chat.id, text='Уточните, какой вид товар у Вас?', reply_markup=markup)

    elif callback.data == "Да":
        user_states[callback.message.chat.id][callback.message.html_text] = 'Да'
        # print(user_states)

        current_option = user_states[callback.message.chat.id][callback.message.html_text]
        # print(current_option)

        # UPD: 22:10,  11 августа После изменения словаря user_states перестал присваивать значение вид товара, а просто слово ДА
        callback.data = user_states[callback.message.chat.id]['Вид товара']

        # print('Вид товара:', user_states[callback.message.chat.id]['Вид товара'])

        markup = types.InlineKeyboardMarkup(row_width=1)
        back = types.InlineKeyboardButton(text=user_states[callback.message.chat.id]['Вид товара'], callback_data=user_states[callback.message.chat.id]['Вид товара'])
        markup.add(back)
        bot.send_message(callback.message.chat.id, text='Back', reply_markup=markup)

    elif callback.data == "Нет":
        user_states[callback.message.chat.id][callback.message.html_text] = 'Нет'

        current_option = user_states[callback.message.chat.id][callback.message.html_text]
        print(current_option)
        print(user_states)
        print('Вид товара:', user_states[callback.message.chat.id]['Вид товара'])

        markup = types.InlineKeyboardMarkup(row_width=1)
        back = types.InlineKeyboardButton(text=user_states[callback.message.chat.id]['Вид товара'], callback_data=user_states[callback.message.chat.id]['Вид товара'])
        markup.add(back)
        bot.send_message(callback.message.chat.id, text='Back', reply_markup=markup)
    else:
        bot.send_message(callback.message.chat.id, 'Нет такого пункта')



bot.polling(none_stop=True)
# bot.infinity_polling(timeout=10, long_polling_timeout = 5)

