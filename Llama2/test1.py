# import subprocess
# import time

from Llama2Class import Llama2

mybot = Llama2()

mybot.readfile()

prompt = "Who is Scott William"

mybot.answer(prompt)

logs = mybot.logs

print('Вопрос:', logs['prompt'])
print('Ответ:', logs['answer'])