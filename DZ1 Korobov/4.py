def enter_the_list():
    n = int(input('Enter the length of list: '))
    return [int(input('Enter the number: ')) for _ in range(n)]
numbers = enter_the_list()
while True:
    i = input('Enter the index or type "exit" to quit: ')
    if i.lower() == 'exit':
        break
    try:
        i = int(i)
        print(numbers[i])
    except ValueError:
        print('Invalid input. Please enter a valid integer.')
    except IndexError:
        print('Index is out of list')
    else:
        print('There are no errors!')