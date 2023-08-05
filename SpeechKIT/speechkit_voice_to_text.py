# https://cloud.yandex.ru/docs/speechkit/stt/api/request-examples

import urllib.request
import json
import os

from SpeechKIT.config import *

class voice_to_text():
    def __init__(self):
        # Объединить с относительным путем к папке
        self.current_file_dir = os.path.dirname(os.path.abspath(__file__))

        self.params = "&".join([
            "topic=general",
            "folderId=%s" % FOLDER_ID,
            "lang=ru-RU"
        ])

        self.text = None

    def translate(self):
        try:
            with open(self.current_file_dir + "/" + "speech.ogg", "rb") as f:
                data = f.read()

            url = urllib.request.Request(
                "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?%s" % self.params, data=data)

            url.add_header("Authorization", "Bearer %s" % IAM_TOKEN)
            responseData = urllib.request.urlopen(url).read().decode('UTF-8')
            decodedData = json.loads(responseData)

            if decodedData.get("error_code") is None:
                print(f'Текст с голосового сообщения: {decodedData.get("result")}')
                self.text = decodedData.get("result")
        except:
            print('Не существует файл')


'''
Где:

FOLDER_ID — идентификатор каталога.
IAM_TOKEN — IAM-токен.
speech.ogg — имя аудиофайла для распознавания.
topic — языковая модель.
lang — язык, для которого будет выполнено распознавание.
'''