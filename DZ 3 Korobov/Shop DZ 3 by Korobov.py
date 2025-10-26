# Коробов Денис

from typing import NoReturn

class Product:  
    def __init__(self, name: str, price: float, stock: int) -> NoReturn:
        self.name = name
        self.price = price
        self.stock = stock
    def update_stock(self, quantity: int) -> None:   # Метод изменения количества товаров на складе
        if self.stock + quantity >= 0:   # Проверка наличия товара на складе
            self.stock += quantity  # Увеличение количества товара на складе
        else:
            print(f'Error! The quantity of {self.name} is negative')    # Ошибка    
class Order:
    def __init__(self) -> NoReturn:
        self.products = {} # Определение словаря продукт:количество
    def add_product(self, product: Product, quantity: int) -> None:   # Метод добавления товаров в заказ
        if product.stock >= quantity:   # Проверка наличия товара на складе
            if product in self.products:    # Проверка наличия товара в словаре
                self.products[product] += quantity  # Если товар есть, прибавляем кол-во
            else:
                self.products[product] = quantity   # Если товара нет, добавляем
            product.update_stock(-quantity) # обновляем количество товара на складе
        else:
            print(f'Error! The quantity of {product.name} is less than the required quantity') # Сообщение об ошибке
    def calculate_total(self) -> float: # Метод для подсчета суммы стоимости продуктов в заказе
        total = sum(product.price * quantity for product, quantity in self.products.items()) # Вычисляем сумму произведения товара на кол-во
        return total
    def return_product(self, product: Product, quantity: int) -> None: # Метод для возврата товаров из заказа
        if product in self.products:    # Проверяем наличие товара в словаре
            current_quantity = self.products.get(product, 0)
            if current_quantity >= quantity:    # Проверяем количество товара
                self.products[product] -= quantity
                if self.products[product] <= 0:
                    del self.products[product]
                product.update_stock(+quantity)  # Вернули товар на склад
            else:
                print(f'Error! Cannot return more items than are present in the order ({current_quantity}).')
        else:
            print(f'Error! This product is not in your order.')
class Store:
    def __init__(self):
        self.products = []  # Создаем список продуктов
    def add_product(self, product: Product) -> None:  # Метод добавления товара в магазин
        self.products.append(product)   # Добавляем продукт в конец списка
    def list_products(self) -> None:   # Метод вывода ассортимента магазина
        print('Available products:')
        for product in self.products: 
            print(f'{product.name}: Price - {product.price} $, Quantity - {product.stock}') # Выводим на экран каждую позицию товара с ценой и кол-вом
    def create_order(self) -> Order:   # Метод создания заказа
        order = Order() 
        while True:
            choice = input('Do you want to add a new product in your order? a(add)/r(return)/n(no) ') # Добавляем выбор нового продукта да/нет
            if choice.lower() in ['n', 'no']: # Если пользлватель вводит "n", то выходим из цикла
                break
            elif choice.lower() in ['a', 'add']: # Если пользователь вводит "а", то добавляем товар
                product_name = (input('Product name: ')).strip() # Запрашиваем у пользователя название товара
                found_product = next((prod for prod in self.products if prod.name.lower() == product_name.lower()), None) # Ищем товар в списке товаровa
                if not found_product:
                    print('There is no such product')
                    continue
                while True:
                    try:    # Используем блок обработки исключений
                        quantity = int(input('Enter the quantity: '))   # Запрашиваем количество товара
                        if quantity <= 0:
                            raise ValueError('Quuantity must be positive! Please try again')
                        if found_product.stock < quantity:
                            print(f'The quantity of {found_product.name} is less then the required quantity')
                            continue
                        break
                    except ValueError:
                        print('Incorrect quantity! Please try again')   # В случае ошибки выводим на экран сообщение 
                order.add_product(found_product, quantity)  # Добавляем запрошенное количество товара в заказ
            elif choice.lower() in ['r', 'return']:    # Если пользователь вводит 'r' или 'return', возвращаем товар на склад
                if len(order.products) > 0:    # Проверка количества товаров в заказе
                    print("\nCurrent Order:")
                    for idx, (product, qty) in enumerate(order.products.items()):   # Выводим список продуктов на экран
                        print(f"{idx+1}. {product.name} x{qty}")
                    item_choice = input('Choose the number of the product to return (or type "q" to quit): ')   
                    if item_choice.isdigit():   # Проверка ввода и добавление продукта по индексу
                        index = int(item_choice) - 1
                        if 0 <= index < len(order.products):
                            selected_product = list(order.products.keys())[index]
                            returned_qty = int(input(f"How many units of '{selected_product.name}' do you want to return?: "))    # Вводим количество товара для возврата
                            order.return_product(selected_product, returned_qty)
                        else:
                            print("Invalid selection.")
                    elif item_choice.lower() == 'q':    # Обработка выхода из цикла возврата
                        pass
                    else:
                        print("Invalid option, please enter the digit or q ")   # Обработка ситуации с неверным вводом опции выбора
                else:
                    print("Your cart is empty!")    # Обработка ситуации с пустой корзиной               
            else:
                print('Unknow option, please enter a(add)/r(return)/n(no)')    # Обработка ситуации с неверным вводом опции выбора
        if len(order.products) > 0:    # Выводим на экран итоговый состав заказа
            print("\nFinal order:")
            for product, quantity in order.products.items():
                print(f"- {product.name}: {quantity} x ${product.price} (${(product.price * quantity)})")
            print(f"\nTotal cost of the order: ${order.calculate_total()}\n")
        else:
            print("No items were added to the order")    # Обрабатываем случай отсутствия товаров в заказе
        return order

if __name__ == '__main__':  # Проверка прямого запуска или импорта файла
    megastore = Store()     # Создание магазина класса Store
    iPhone_17 = Product('iPhone 17', 1000,  10) # Определяем ассортимент товаров
    iPhone_17_Pro = Product('iPhone 17 Pro', 1300,  7)
    iPhone_17_Pro_Max = Product('iPhone 17 Pro Max', 1600,  5)
    Galaxy_S25 = Product('Galaxy S25', 800, 15)
    Galaxy_S25_Plus = Product('Galaxy S25 Plus', 900, 10)
    Galaxy_S25_Ultra = Product('Galaxy S25 Ultra', 1300, 8)
    megastore.add_product(iPhone_17)    # Добавляем товары в магазин
    megastore.add_product(iPhone_17_Pro)
    megastore.add_product(iPhone_17_Pro_Max)
    megastore.add_product(Galaxy_S25)
    megastore.add_product(Galaxy_S25_Plus)
    megastore.add_product(Galaxy_S25_Ultra)
    megastore.list_products()   # Выводим на экран весь ассортимент магазина
    new_order = megastore.create_order() # Создаем новый заказ
   