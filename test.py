import subprocess
import time
import requests
from config import telegram_token

api_url = f'https://api.telegram.org/bot{telegram_token}/METHOD_NAME'

try:
    response = requests.get(api_url, timeout=30)
    # Обработка ответа от сервера Telegram

    # Запоминаем текущее время перед выполнением кода
    start_time = time.time()

    # Вывод списка установленных пакетов
    result = subprocess.check_output(['pip', 'list'])
    print(result.decode('utf-8'))

    # Вывод версии Python
    result = subprocess.check_output(['python3', '--version'])
    print(result.decode('utf-8'))

    # Запоминаем текущее время после завершения кода
    end_time = time.time()

    # Вычисляем время выполнения
    time_taken = end_time - start_time

    print(f"Время выполнения: {time_taken:.6f} секунд")
except requests.exceptions.ReadTimeout:
    print("Произошел таймаут при запросе к серверу Telegram")


