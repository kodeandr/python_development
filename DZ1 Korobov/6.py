import math

def calculate_square_root():
    try:
        # Запрашиваем у пользователя число
        number = float(input("Введите положительное число: "))
        
        # Проверка, является ли число положительным
        if number < 0:
            raise ValueError("Отрицательные числа недопустимы")
            
        # Рассчитываем квадратный корень
        result = math.sqrt(number)
        
        # Выводим результат
        print(f"Квадратный корень из {number} равен {result:.2f}")
    
    except ImportError as e:
        print("Ошибка импорта модуля:", str(e))
    
    except ValueError as ve:
        print(str(ve))
    
    except Exception as ex:
        print("Возникла непредвиденная ошибка:", str(ex))

calculate_square_root()