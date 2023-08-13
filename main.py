import telebot

from config import telegram_token

from chatGPT.chatGPT import chatGPT
from SpeechKIT.speechkit_voice_to_text import voice_to_text

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
    chat_auchan = chatGPT()
    # Голосовое распознавание
    VtoT = voice_to_text()

    @bot.message_handler(content_types=["text"])
    def echo(message):
        chat_auchan.dialog(content=message.text)

        bot.send_message(message.chat.id, f'\nАшанчик: {chat_auchan.chat_response}\n')

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

        print('prompt:', VtoT.text)
        # bot.send_message(message.chat.id, f'Ваш вопрос: {VtoT.text}')

        chat_auchan.dialog(content=VtoT.text)

        bot.send_message(message.chat.id, f'\nАшанчик: {chat_auchan.chat_response}\n')


bot.polling(none_stop=True)
