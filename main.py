import os
import telebot
from telebot import types
import json

# Конфигурации
from config import telegram_token, IAM_TOKEN, FOLDER_ID
# ИИ ЧатГПТ
from chatGPT.chatGPT import chatGPT
# Голосовой синтез и распознавание
from SpeechKIT.speechkit import voice_to_text, text_to_voice
# Распознавание изображение
from YandexVision.Vision import Vision

# Создание бота
bot = telebot.TeleBot(telegram_token)

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

    # Голосовое распознавание
    # VtoT = voice_to_text()
    # Синтез речи
    # TtoV = text_to_voice()

    @bot.message_handler(content_types=["text"])
    def echo(message):
        chat_auchan.prompt(content=message.text)

        bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        # with open('SpeechKIT/speech.ogg', "wb") as f:
        #     for audio_content in TtoV.translate(chat_auchan.chat_response):
        #         f.write(audio_content)
        #
        # bot.send_voice(message.from_user.id, open('SpeechKIT/speech.ogg', 'rb'))

        bot.send_message(message.chat.id, f'DEBUGGER: статус диалога, TRUE - завершен: {chat_auchan.end_dialog}')

        if (chat_auchan.end_dialog):
            show_smiley_keyboard(message.chat.id)


    @bot.message_handler(content_types=['voice'])
    def voice_processing(message):
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open('SpeechKIT/speech.ogg', 'wb') as new_file:
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

        # with open('SpeechKIT/speech.ogg', "wb") as f:
        #     for audio_content in TtoV.translate(chat_auchan.chat_response):
        #         f.write(audio_content)
        #
        # bot.send_voice(message.from_user.id, open('SpeechKIT/speech.ogg', 'rb'))

        bot.send_message(message.chat.id, f'status end dialog: {chat_auchan.end_dialog}')

        if (chat_auchan.end_dialog):
            show_smiley_keyboard(message.chat.id)

    # Если пользователь прислал фото, то закидываем его в БД
    @bot.message_handler(content_types=["photo"])
    def echo(message):
        # Проверяем, существует ли папка уже
        if not os.path.exists(f'database/photo/{str(message.from_user.id)}'):
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

        CV = Vision(IAM_TOKEN, FOLDER_ID)

        json_data = CV.request_analyze(image_path=f'database/photo/{message.from_user.id}/{file_id}.{file_extension}')

        text = ' '.join(CV.extract_text(json_data))

        # Отправляем текст после распознавание фотографии
        # bot.send_message(message.chat.id, f'{text}')

        chat_auchan.prompt(content=text, photo_status=True)

        bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        # with open('SpeechKIT/speech.ogg', "wb") as f:
        #     for audio_content in TtoV.translate(chat_auchan.chat_response):
        #         f.write(audio_content)
        #
        # bot.send_voice(message.from_user.id, open('SpeechKIT/speech.ogg', 'rb'))

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

def save_comment(message, emoji):
    comment = message.text
    comments[emoji] = comment
    with open('comments.json', 'w') as file:
        json.dump(comments, file)
    bot.send_message(message.chat.id, 'Спасибо за комментарий! Мы ценим Ваше мнение.')



bot.polling(none_stop=True)
