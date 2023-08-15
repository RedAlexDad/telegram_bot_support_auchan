# https://cloud.yandex.ru/docs/vision/operations/ocr/text-detection

from requests import post
import json
import argparse
import base64

from config import IAM_TOKEN, FOLDER_ID

# Функция возвращает IAM-токен для аккаунта на Яндексе.
def get_iam_token(iam_url, oauth_token):
    response = post(iam_url, json={"yandexPassportOauthToken": oauth_token})
    json_data = json.loads(response.text)
    if json_data is not None and 'iamToken' in json_data:
        return json_data['iamToken']
    return None

# Функция отправляет на сервер запрос на распознавание изображения и возвращает ответ сервера.
def request_analyze(vision_url, iam_token, folder_id, image_data):
    response = post(vision_url, headers={'Authorization': 'Bearer '+iam_token}, json={
        'folderId': folder_id,
        'analyzeSpecs': [
            {
                'content': image_data,
                'features': [
                    {
                        'type': 'TEXT_DETECTION',
                        'textDetectionConfig': {'languageCodes': ['en', 'ru']}
                    }
                ],
            }
        ]})
    return response.json()

# Функция для извлечения текста из JSON
def extract_text(json_obj):
    if isinstance(json_obj, dict):
        if "text" in json_obj:
            print(json_obj["text"])
        for key, value in json_obj.items():
            extract_text(value)
    elif isinstance(json_obj, list):
        for item in json_obj:
            extract_text(item)

def main():
    parser = argparse.ArgumentParser()

    # parser.add_argument('--folder-id', required=True)
    # parser.add_argument('--oauth-token', required=True)
    # parser.add_argument('--image-path', required=True)
    # args = parser.parse_args()

    iam_url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    vision_url = 'https://vision.api.cloud.yandex.net/vision/v1/batchAnalyze'

    image_path = '/home/redalexdad/Документы/GitHub/telegram_bot_support_auchan/YandexVision/photo_0.jpg'
    # image_path = '/home/redalexdad/Документы/GitHub/telegram_bot_support_auchan/YandexVision/photo_1.jpg'
    # image_path = '/home/redalexdad/Документы/GitHub/telegram_bot_support_auchan/YandexVision/photo_2.jpg'

    # with open(args.image_path, "rb") as f:
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    response_text = request_analyze(vision_url, IAM_TOKEN, FOLDER_ID, image_data)
    # print(response_text)

    # with open("output.json", "w") as json_file:
        # json.dump(response_text, json_file, indent=4, sort_keys=True)

    print('='*100)

    extract_text(response_text)

if __name__ == '__main__':
    main()