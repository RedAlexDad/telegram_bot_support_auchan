# https://cloud.yandex.ru/docs/vision/operations/ocr/text-detection

from requests import post
import json
import argparse
import base64

from config import IAM_TOKEN, FOLDER_ID


class Vision():

    def __init__(self):
        self.vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'
        self.iam_token = IAM_TOKEN
        self.folder_id = FOLDER_ID
        self.image_path = ''
        self.image_data = None

    # Функция отправляет на сервер запрос на распознавание изображения и возвращает ответ сервера.
    def request_analyze(self, image_path):
        # Преобразование фото
        try:
            with open(image_path, "rb") as f:
                self.image_data = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print('Ошибка! Тип ошибки:\n', e)

        try:
            response = post(self.vision_url, headers={'Authorization': 'Bearer ' + self.iam_token}, json={
                'folderId': self.folder_id,
                'analyzeSpecs': [
                    {
                        'content': self.image_data,
                        'features': [
                            {
                                'type': 'TEXT_DETECTION',
                                'textDetectionConfig': {'languageCodes': ['en', 'ru']}
                            }
                        ],
                    }
                ]})
            return response.json()
        except Exception as e:
            print('Ошибка! Тип ошибки:\n', e)

    # Функция для извлечения текста из JSON
    def extract_text(self, json_obj):
        text = []
        if isinstance(json_obj, dict):
            if "text" in json_obj:
                # print(json_obj['text'])
                text.append(json_obj['text'])
            for key, value in json_obj.items():
                text.extend(self.extract_text(value))  # Объединяем результаты рекурсивных вызовов
        elif isinstance(json_obj, list):
            for item in json_obj:
                text.extend(self.extract_text(item))  # Объединяем результаты рекурсивных вызовов
        return text  # Возвращаем список текстов после окончания всех рекурсивных вызовов


CV = Vision()

# image_path = '/home/redalexdad/Документы/GitHub/telegram_bot_support_auchan/YandexVision/photo_0.jpg'
# image_path = '/home/redalexdad/Документы/GitHub/telegram_bot_support_auchan/YandexVision/photo_01.jpg'
# image_path = '/home/redalexdad/Документы/GitHub/telegram_bot_support_auchan/YandexVision/photo_1.jpg'
image_path = '/home/redalexdad/Документы/GitHub/telegram_bot_support_auchan/YandexVision/photo_2.jpg'

json_data = CV.request_analyze(image_path)

text = CV.extract_text(json_data)
print(text)