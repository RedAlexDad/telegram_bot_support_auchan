# import subprocess
# import time

from Llama2Class import Llama2

mybot = Llama2('369350478')

mybot.readfile(directory_file='OrderGoods')

prompt = "Можно ли вернуть продукт, если продукт в поврежденном упаковке?"

mybot.answer(prompt)

logs = mybot.logs

print('Вопрос:', logs['369350478']['prompt'])
print('Ответ:', logs['369350478']['answer'])