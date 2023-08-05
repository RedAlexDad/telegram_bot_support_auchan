import subprocess
import time

# Запоминаем текущее время перед выполнением кода
start_time = time.time()

# Вывод списка установленных пакетов
result = subprocess.check_output(['pip', 'list'])
print(result.decode('utf-8'))

# Вывод версии Python
result = subprocess.check_output(['python3', '--version'])
print(result.decode('utf-8'))

# Запоминаем текущее время после завершения кода
end_time = time.time()

# Вычисляем время выполнения
time_taken = end_time - start_time

print(f"Время выполнения: {time_taken:.6f} секунд")