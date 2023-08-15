import os
import telebot
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
    VtoT = voice_to_text()
    # Синтез речи
    TtoV = text_to_voice()

    @bot.message_handler(content_types=["text"])
    def echo(message):
        chat_auchan.prompt(content=message.text)

        bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        with open('SpeechKIT/speech.ogg', "wb") as f:
            for audio_content in TtoV.translate(chat_auchan.chat_response):
                f.write(audio_content)

        bot.send_voice(message.from_user.id, open('SpeechKIT/speech.ogg', 'rb'))


    @bot.message_handler(content_types=['voice'])
    def voice_processing(message):
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

        # print('prompt:', VtoT.text)
        # bot.send_message(message.chat.id, f'Ваш вопрос: {VtoT.text}')

        chat_auchan.prompt(content=VtoT.text, voice_status=True)

        bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        with open('SpeechKIT/speech.ogg', "wb") as f:
            for audio_content in TtoV.translate(chat_auchan.chat_response):
                f.write(audio_content)

        bot.send_voice(message.from_user.id, open('SpeechKIT/speech.ogg', 'rb'))

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

        with open('SpeechKIT/speech.ogg', "wb") as f:
            for audio_content in TtoV.translate(chat_auchan.chat_response):
                f.write(audio_content)

        bot.send_voice(message.from_user.id, open('SpeechKIT/speech.ogg', 'rb'))




bot.polling(none_stop=True)
