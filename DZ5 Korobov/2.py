import threading
import time

# функция для вывода чисел с задержкой 1 сек
def count_and_delay():
    for num in range(1,11):
        print(num)
        time.sleep(1)

num_threads = 4    # Укажем количество задействованных потоков

threads = []    # Список для хранения потоков

for _ in range(num_threads):    # создание и запуск потоков
    thread = threading.Thread(target = count_and_delay)
    threads.append(thread)
    thread.start()

for t in threads:    # ожидание завершения потоков
    t.join()

print('All threads have finished their work')