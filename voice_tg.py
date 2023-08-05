import aiohttp
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

import config
import os

API_TOKEN = config.token
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

current_file_dir = os.path.dirname(os.path.abspath(__file__))

async def download_and_save_file(file_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(file_path) as response:
            if response.status == 200:
                content = await response.read()
                with open('new_file.ogg', 'wb') as new_file:
                    new_file.write(content)


@dp.message_handler(content_types=[types.ContentType.VOICE])
async def voice_processing(message: types.Message):
    file_info = await bot.get_file(current_file_dir + message.voice.file_id)

    try:
        await download_and_save_file(file_info.file_path)
    except Exception as e:
        print(f"Произошла ошибка при загрузке и сохранении файла: {e}")

    # Ваш код для дальнейшей обработки нового файла здесь


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(executor.start_polling(dp))
    loop.run_forever()
