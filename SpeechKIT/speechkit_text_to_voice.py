import argparse
import requests
import config

TEXT = \
'''
Я Яндекс Спичк+ит. Я могу превратить любой текст в речь. Теперь и в+ы — можете!
'''

def synthesize():
   url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
   headers = {
       'Authorization': 'Bearer ' + config.IAM_TOKEN,
   }

   data = {
       'folderId': config.FOLDER_ID,
       'text': TEXT,
       'lang': 'ru-RU',
       # 'voice':'alena', # премиум - жрет в 10 раз больше денег
       'voice': 'filipp',  # oksana
       # 'emotion': 'evil',
       'speed': '0.5',
       # по умолчанию конвертит в oggopus, кот никто не понимает, зато занимат мало места
       # 'format': 'lpcm',
       # 'sampleRateHertz': 48000,
   }

   with requests.post(url, headers=headers, data=data, stream=True) as resp:
       if resp.status_code != 200:
           raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))

       for chunk in resp.iter_content(chunk_size=None):
           yield chunk

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   # parser.add_argument("--token", required=True, help="IAM token")
   # parser.add_argument("--FOLDER_ID", required=True, help="Folder id")
   # parser.add_argument("--text", required=True, help="Text for synthesize")
   # parser.add_argument("--output", required=True, help="Output file name")
   args = parser.parse_args()

   # with open(args.output, "wb") as f:
   with open('speech.ogg', "wb") as f:
       # for audio_content in synthesize(args.text):
       for audio_content in synthesize():
           f.write(audio_content)
