class EvenNumberError(Exception):
    def __init__(self, message="Список содержит четное число"):
        self.message = message
        super().__init__(self.message)

class NegativeNumberError(Exception):
    def __init__(self, message="Список содержит отрицательное число"):
        self.message = message
        super().__init__(self.message)
def division(a, b):
    return (a / b)

# Функция для вычисления суммы списка
def sum_list(numbers):
    for number in numbers:
        if number % 2 == 0:
            raise EvenNumberError()
        if number < 0:
            raise NegativeNumberError()
    return sum(numbers)

# Пример использования
try:
    n = int(input('Enter the number of numbers: '))
    numbers = [int(input('Enter the number: ')) for _ in range(n)]
    result = sum_list(numbers)
    print(result)
except EvenNumberError:
    print('EvenNumberError')
except NegativeNumberError:
    print('NegativeNumberError')
'''
while True:
    try:
        a = int(input('Enter 1st number: '))
        b = int(input('Enter 2nd number: '))
        result = division(a, b)
    except ZeroDivisionError:
        print('Division by zero detected')
    except ValueError:
        print('Enter a number')
    else:
        print(f'The result of divining {a} by {b} is equal {result}')
        break
'''

