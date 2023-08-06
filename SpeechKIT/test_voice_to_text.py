# https://cloud.yandex.ru/docs/speechkit/stt/api/request-examples

import urllib.request
import json

import config

with open("speech.ogg", "rb") as f:
    data = f.read()

params = "&".join([
    "topic=general",
    "folderId=%s" % config.FOLDER_ID,
    "lang=ru-RU"
])

url = urllib.request.Request("https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?%s" % params, data=data)
url.add_header("Authorization", "Bearer %s" % config.IAM_TOKEN)

responseData = urllib.request.urlopen(url).read().decode('UTF-8')
decodedData = json.loads(responseData)

if decodedData.get("error_code") is None:
    print(decodedData.get("result"))

'''
Где:

FOLDER_ID — идентификатор каталога.
IAM_TOKEN — IAM-токен.
speech.ogg — имя аудиофайла для распознавания.
topic — языковая модель.
lang — язык, для которого будет выполнено распознавание.
'''