# import subprocess
# import time

from Llama2Class import Llama2

mybot = Llama2('5435345')

mybot.readfile(directory_file='online_retail')

prompt = "Is there a PARIS FASHION YELLOW COAT RACK on the list?"

mybot.answer(prompt)

logs = mybot.logs

print('Вопрос:', logs['prompt'])
print('Ответ:', logs['answer'])