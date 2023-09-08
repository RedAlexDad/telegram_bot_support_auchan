FROM python:3.9.16

# Копируем файлы и папки из текущего контекста сборки в контейнер
COPY chatGPT /app/chatGPT
COPY config.py /app/config.py
COPY Database /app/Database
COPY img /app/img
COPY main.py /app/main.py
COPY SpeechKit /app/SpeechKit
COPY YandexVision /app/YandexVision

# Устанавливаем зависимости из файла requirements.txt
RUN pip install  \
    pyTelegramBotAPI==4.12.0  \
    pyTelegramBotAPI==4.12.0 \
    boto3==1.28.41 \
    openai==0.27.8 \
    tiktoken==0.4.0 \
    psycopg2==2.9.7

CMD python /app/main.py

# 0.
# Запустить приложение Docker у себя, и включить сервер

# 1.

# В терминале написать, чтобы создать контейнер:
# docker build .
# либо
# docker build . -f Dockerfile
# И нужно подождать, пока не завершится сборка

# 2.

# Затем написать:
# docker image ls
# Чтобы увидеть файл IMAGE ID для выполнения кода

# 3.

# Скорпируйте ID с IMAGE ID, затем написать:
# docker run `ID`

# 4.
# Удалить все контейеры можно:
# docker system prune -a