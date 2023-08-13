import openai
import tiktoken

# конфиг и файлы с базами знаний
from config import CHAT_GPT_API_KEY
# import auchan_data.info as INFO
# import auchan_data.shops as SHOPS
# import auchan_data.refund as REFUND

from config import IAM_TOKEN
class chatGPT():
    def __init__(self):
        SYSTEM = """Вы добрый отзывчивый помощник магазина Ашан и помогаете покупателям отвечая на их вопросы.
            Ваше имя Ашанчик.
            Инструкции:
            - Вы отвечаете только на вопросы, связанные с магазином Ашан. На посторонние вопросы отвечать строго запрещено.
            - Если вы не уверены в ответе, вы можете сказать "Я не знаю" или "Я не уверен" и предложить пользователю переключить его на сотрудника магазина.
        """

        ASSISTANT = """
            Спроси у покупателя какой товар он хочет вернуть.

            Правила возврата продовольственных товаров:
            - Продукты питания надлежащего качества, в неповрежденной упаковке и с действующим сроком годности возврату и обмену не подлежат. Вы можете отказаться от товаров при курьере или на кассе магазина. При том, частичная выдача заказа не предусмотрена.
            - Продукты питания ненадлежащего качества, при условии, что недостаток возник до передачи товара покупателю, в пределах срока годности, принимаются на экспертизу для дальнейшего обмена или возврата денежных средств.

            Правила возврата непродовольственных товаров:
            Непродовольственный товар надлежащего качества вы имеете право вернуть в магазин в течение 7 дней с момента его покупки без объяснения причин, если:
            - товар не был в употреблении;
            - сохранен первоначальный вид товара и ярлыки;
            - комплектация и упаковка не повреждены;
            - товар не относится к товарам-исключениям*;
            - сохранен товарный или кассовый чеки.

            *К товарам-исключениям относятся предметы личной гигиены и парфюмерно-косметические товары; швейные и трикотажные изделия; бытовая химия, пестициды и агрохимикаты; растения.

            Непродовольственный товар ненадлежащего качества при условии, что недостаток возник до передачи товара покупателю, принимается на экспертизу для дальнейшего обмена или возврата денежных средств не позднее, чем через 15 дней с момента покупки (исключения составляют случаи, описанные в Законе «О защите прав потребителей»).

            Круглосуточная клиентская служба:
            - Форма обратной связи (https://www.auchan.ru/feedback/)
            - Контактный центр 8-800-700-5-800 (звонок бесплатный)
            - Чат-бот (viber://pa?chatURI=auchanrusbot)

        """.strip()

        # print(SYSTEM)
        # self.model = "gpt-3.5-turbo"  # 4096 токенов
        # self.model = "gpt-3.5-turbo-16k"  # 16384 токена
        self.model = "gpt-4"  # 8192 токена
        openai.api_key = CHAT_GPT_API_KEY
        self.max_tokens = 1000
        self.temperature = 0.1
        self.token_limit = 8000

        # затравка, настраиваем роль и даем базу для ответов
        self.messages = [
            # системная роль, чтобы задать поведение помошника
            {"role": "system", "content": SYSTEM},
            # база знаний асистента
            {"role": "assistant", "content": ASSISTANT}
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

    def dialog(self, content):
        if content == '':
            content = 'Привет!'

        # добавляем сообщение пользователя
        self.messages.append({"role": "user", "content": content})

        # общее число токенов
        self.conv_history_tokens = self.num_tokens_from_messages(self.messages)
        print(f"Токенов: {self.conv_history_tokens}")

        # удаляем прошлые сообщения, если число токенов превышает лимиты
        while self.conv_history_tokens + self.max_tokens >= self.token_limit:
            del self.messages[2]
            self.conv_history_tokens = self.num_tokens_from_messages(self.messages)

        # формируем запрос
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

        # получаем ответ
        self.chat_response = completion.choices[0].message.content

        # выводим ответ
        print(f'''
    Ашанчик: {self.chat_response}
    ''')

        # сохраняем контекст диалога
        self.messages.append({"role": "assistant", "content": self.chat_response})