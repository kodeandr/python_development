my_str = input('Enter the string: ')
try:
    number = float(my_str)
except ValueError:
   print('ValueError')
else:
    print(number)