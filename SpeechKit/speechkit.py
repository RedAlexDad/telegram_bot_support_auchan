# https://cloud.yandex.ru/docs/speechkit/stt/api/request-examples
import requests
import urllib.request
import json
import os
import base64

from config import FOLDER_ID, IAM_TOKEN

class text_to_voice():
    def __init__(self):
        self.url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
        self.headers = {
            'Authorization': 'Bearer ' + IAM_TOKEN,
        }
    def translate(self, TEXT):
        data = {
            'folderId': FOLDER_ID,
            'text': TEXT,
            'lang': 'ru-RU',
            # 'voice':'alena', # премиум - жрет в 10 раз больше денег
            'voice': 'filipp',  # oksana
            # 'emotion': 'evil',
            'speed': '1.0',
            # по умолчанию конвертит в oggopus, кот никто не понимает, зато занимат мало места
            # 'format': 'lpcm',
            # 'sampleRateHertz': 48000,
        }

        with requests.post(self.url, headers=self.headers, data=data, stream=True) as resp:
            if resp.status_code != 200:
                raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))

            for chunk in resp.iter_content(chunk_size=None):
                yield chunk

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

    def translate(self, voice_path=None, voice_data=None):
        try:
            if not(voice_path==None):
                # with open(self.current_file_dir + "/" + "speech.ogg", "rb") as f:
                with open(voice_path, "rb") as f:
                    self.voice_data = f.read()

            url = urllib.request.Request(
                "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?%s" % self.params, data=voice_data)

            url.add_header("Authorization", "Bearer %s" % IAM_TOKEN)
            responseData = urllib.request.urlopen(url).read().decode('UTF-8')
            decodedData = json.loads(responseData)

            if decodedData.get("error_code") is None:
                print(f'Текст с голосового сообщения: {decodedData.get("result")}')
                self.text = decodedData.get("result")
        except Exception as e:
            print('Ошибка! Тип ошибки:', e)


'''
Где:

FOLDER_ID — идентификатор каталога.
IAM_TOKEN — IAM-токен.
speech.ogg — имя аудиофайла для распознавания.
topic — языковая модель.
lang — язык, для которого будет выполнено распознавание.
'''