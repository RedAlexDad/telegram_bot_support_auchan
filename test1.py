import requests

url = "https://api.telegram.org/bot{token}/{method}".format(
    token='6504579093:AAHO2i3asO13buUpdikBFr8oU43TBonaYYc',
    method='setWebhook'
    # method='getWebhookinfo'
)

data = {'url': 'https://functions.yandexcloud.net/d4e1kimsqkcedh90j0fj'}

r = requests.post(url, data = data)

print(r.json())