import openai
import tiktoken
import re

# конфиг и файлы с базами знаний
import chatGPT.auchan_config as CFG
import chatGPT.auchan_data.intents as INTENT                # определение интента запроса
import chatGPT.auchan_data.common as COMMON                 # начальная настройка
import chatGPT.auchan_data.delivery as DELIVERY             # "условия доставки"
import chatGPT.auchan_data.delivery_alk as DELIVERY_ALK     # "доставка 18+"
import chatGPT.auchan_data.delivery_faq as DELIVERY_FAQ     # "вопросы доставки"
import chatGPT.auchan_data.delivery_free as DELIVERY_FREE   # "бесплатная доставка"
import chatGPT.auchan_data.info as INFO                     # "об ашане"
import chatGPT.auchan_data.refund_exceptions as REFUND_EXC  # "возврат исключения"
import chatGPT.auchan_data.refund_food as REFUND_FOOD       # "возврат продовольственного"
import chatGPT.auchan_data.refund_nonfood as REFUND_NONFOOD # "возврат непродовольственного"
import chatGPT.auchan_data.shops as SHOPS                   # "адреса ашан"
import chatGPT.auchan_data.city as CITY                   # Города в РФ


from config import CHAT_GPT_API_KEY

from config import IAM_TOKEN
class chatGPT():
    def __init__(self):
        # print(SYSTEM)
        # self.model = "gpt-3.5-turbo"  # 4096 токенов
        # self.model = "gpt-3.5-turbo-16k"  # 16384 токена
        self.model = "gpt-4"  # 8192 токена
        openai.api_key = CHAT_GPT_API_KEY
        self.max_tokens = 1000
        self.temperature = 0.1
        self.token_limit = 8000

        # настройка роли асистента для определения темы сообщения
        self.intent_prompt = [
            {"role": "system", "content": INTENT.SYSTEM},
            {"role": "assistant", "content": INTENT.ASSISTANT}
        ]

        # настраиваем роли и даем базу для ответов
        self.messages = [
            # системная роль, чтобы задать поведение помошника
            {"role": "system", "content": CFG.SYSTEM},
            # промт для выяснения темы проблемы клиента
            {"role": "assistant", "content": COMMON.ASSISTANT}
        ]
    def review_model(self):
        self.model = openai.Model.list()
        for model in self.model.data:
           print(model.id)

    # функция подсчета числа токенов
    def num_tokens_from_messages(self, messages):
        encoding = tiktoken.encoding_for_model(self.model)
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # каждое сообщение следует за <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # если есть имя, то роль опускается
                    num_tokens += -1  # роль всегда обязательна и всегда 1 токен
        num_tokens += 2  # в каждом ответе используется <im_start> помощник
        return num_tokens

    # функция делает запрос и возвращает ответ модели
    def get_response(self, model="gpt-4", msg="", tokens=100, temp=0.1):
        # формируем запрос к модели
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=msg,
            max_tokens=tokens,
            temperature=temp
        )
        # получаем ответ
        chat_response = completion.choices[0].message.content
        return chat_response

    def dialog(self, content):
        if content == "":
            content = "Привет! Как тебя зовут?"
            # добавляем сообщение пользователя

        self.messages.append({"role": "user", "content": content})
        self.intent_prompt.append({"role": "user", "content": content})

        # пытаемся получить тему сообщения
        self.intent = self.get_response(model=self.model, msg=self.intent_prompt, tokens=100, temp=0.1)

        # определяем совапдения по темам и загружаем нужный промт
        if "возврат продовольственного" in self.intent:
            self.messages[1] = {"role": "assistant", "content": REFUND_FOOD.ASSISTANT}
        elif "возврат непродовольственного" in self.intent:
            self.messages[1] = {"role": "assistant", "content": REFUND_NONFOOD.ASSISTANT}
        elif "возврат исключения" in self.intent:
            self.messages[1] = {"role": "assistant", "content": REFUND_EXC.ASSISTANT}
        elif "условия доставки" in self.intent:
            self.messages[1] = {"role": "assistant", "content": DELIVERY.ASSISTANT}
        elif "бесплатная доставка" in self.intent:
            self.messages[1] = {"role": "assistant", "content": DELIVERY_FREE.ASSISTANT}
        elif "вопросы доставки" in self.intent:
            self.messages[1] = {"role": "assistant", "content": DELIVERY_FAQ.ASSISTANT}
        elif "доставка 18+" in self.intent:
            self.messages[1] = {"role": "assistant", "content": DELIVERY_ALK.ASSISTANT}
        elif "адреса ашан" in self.intent:
            # buff = self.messages[2]['content']
            # self.messages[2]['content'] = self.messages[2]['content'] + ' Какой город я написал? Ответьте только на последний вопрос - назовите город.'
            # Адрес Ашана много, поэтому еще обратимся к chatGPT, чтобы подбирали конкретные адреса
            # self.messages[1] = {"role": "assistant", "content": "Если в тексте присутствуется название города, то сообщите название города"}
            #
            # пытаемся получить названия города
            # city = self.get_response(model=self.model, msg=self.messages, tokens=30, temp=0.1)
            # print('-'*100)
            # print('Город:', city)

            # Используем регулярное выражение для поиска названий городов Москва
            # pattern = r'.+г\.\s+' + city + '.+'
            # list_shops = re.findall(pattern, SHOPS.ASSISTANT)

            # print('Список магазинов:')
            # for shop in list_shops:
            #     print(shop)
            # print('-'*100)

            # self.messages[2]['content'] = buff
            self.messages[1] = {"role": "assistant", "content": SHOPS.MSW_SCB}
        elif "об ашане" in self.intent:
            self.messages[1] = {"role": "assistant", "content": INFO.ASSISTANT}
        else:
            self.messages[1] = {"role": "assistant", "content": COMMON.ASSISTANT}

        # общее число токенов
        conv_history_tokens = self.num_tokens_from_messages(self.messages)
        print(f"Токенов: {conv_history_tokens}, интент: {self.intent}")

        # удаляем прошлые сообщения, если число токенов превышает лимиты
        while conv_history_tokens + self.max_tokens >= self.token_limit:
            del self.messages[2]
            conv_history_tokens = self.num_tokens_from_messages(self.messages)

        # формируем запрос и получаем ответ
        self.chat_response = self.get_response(model=self.model, msg=self.messages, tokens=self.max_tokens, temp=self.temperature)

        # выводим ответ
        print(f'''
        Ашанчик: {self.chat_response}
        ''')

        # сохраняем контекст диалога
        self.messages.append({"role": "assistant", "content": self.chat_response})

# chat = chatGPT()
#
# # chat.review_model()
#
# # ввод пользователя
# content = ''
#
# while not 'пока' in content.lower():
#     content = input("Пользователь: ").strip()
#     chat.dialog(content=content)
