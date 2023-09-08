import io
import time
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Конфигурации
from config import TG_BOT_TOKEN, IAM_TOKEN, FOLDER_ID, bucket_name
# ИИ ЧатГПТ
from chatGPT.chatGPT import chatGPT
# Голосовой синтез и распознавание
# from SpeechKit.speechkit import voice_to_text, text_to_voice
# Распознавание изображение
# from YandexVision.Vision import Vision
# БД PostgreSQL
from Database.ClassDatabase import DatabaseLogs
# Облачное хранилище OBJECT STORAGE
from Database.StorageDB import StorageDB

from Database.ClassDatabase import DatabaseLogs

# Создайте экземпляр бота с использованием aiogram
bot = Bot(token=TG_BOT_TOKEN)
dp = Dispatcher(bot)

DB = DatabaseLogs()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    chat_auchan = chatGPT(message.from_user.id)

    # Подключение к БД
    DB.connect()

    # Получение уникального идентификатора пользователя
    ID_CLIENT = int(message.from_user.id)
    # Заполнения данных в БД
    DB.insert_client(ID_CLIENT, str(datetime.now()), 'last_time')

    @bot.message_handler(content_types=["text"])
    def echo(message):
        # Получение промпта с чатГПТ
        while (True):
            try:
                try:
                    # chat_auchan.prompt(content=message.text)
                    bot.send_message(chat_id=message.chat.id, text='ТЕСТ ПРОЙДЕН')
                    break
                except:
                    msg = bot.send_message(message.chat.id, f'Большие нагрузки на бот.')
            except:
                # Через некоторое время меняем текст сообщения
                time_second = 30  # Устанавливаем начальное значение времени в секундах
                while time_second > 0:
                    bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id,
                                          text=f"Ожидайте. Осталось {time_second} секунд")
                    time.sleep(1)  # Подождем 1 секунду
                    time_second -= 1  # Уменьшим счетчик секунд на 1

        # Отправка сообщений в ТГ БОТ
        # bot.send_message(message.chat.id, f'{chat_auchan.chat_response}')

        # Заполнение данных
        INSERT_DB(message, chat_auchan, DB)

    await bot.send_message(chat_id=message.chat.id, text=f"Привет, {message.from_user.first_name}! Я бот Ашан, cпрашивайте, буду рад помочь!")


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

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)