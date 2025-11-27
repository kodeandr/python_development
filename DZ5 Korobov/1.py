import threading

def squares():
    for i in range(1,11):
        print(f'Square of {i} is {i * i}')

def cubes():
    for i in range(1,11):
        print(f'Cube of {i} is {i * i * i}')

thread1 = threading.Thread(target=squares)
thread2 = threading.Thread(target=cubes)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print("All threads have finished their work.")