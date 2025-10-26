def division(a, b):
    return (a / b)
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


