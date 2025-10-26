class Product:  
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock
    def update_stock(self, quantity):   # Метод изменения количества товаров на складе
        if self.stock + quantity >= 0:   # Проверка наличия товара на складе
            self.stock += quantity  # Увеличение количества товара на складе
        else:
            print(f'Error! The quantity of {self.name} is negative')    # Ошибка
class Order:
    def __init__(self):
        self.products = {} # Определение словаря продукт:количество
    def add_product(self, product, quantity):   # Метод добавления товаров в заказ
        if product.stock >= quantity:   # Проверка наличия товара на складе
            if product in self.products:    # Проверка наличия товара в словаре
                self.products[product] += quantity  # Если товар есть, прибавляем кол-во
            else:
                self.products[product] = quantity   # Если товара нет, добавляем
            product.update_stock(-quantity) # обновляем количество товара на складе
        else:
            print(f'Error! The quantity of {product.name} is less than the required quantity') # Сообщение об ошибке
    def calculate_total(self): # Метод для подсчета суммы стоимости продуктов в заказе
        total = sum(product.price * quantity for product, quantity in self.products.items()) # Вычисляем сумму произведения товара на кол-во
        return total
    def return_product(self, product, quantity): # Метод для возврата товаров из заказа
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
    def add_product(self, product):  # Метод добавления товара в магазин
        self.products.append(product)   # Добавляем продукт в конец списка
    def list_products(self):   # Метод вывода ассортимента магазина
        print('Available products:')
        for product in self.products: 
            print(f'{product.name}: Price - {product.price} $, Quantity - {product.stock}') # Выводим на экран каждую позицию товара с ценой и кол-вом
    def create_order(self):   # Метод создания заказа
        order = Order() 
        while True:
            choice = input('Do you want to add a new product? y/n: ') # Добавляем выбор нового продукта да/нет
            if choice.lower() != 'y':   # Как только вводим не у, выходим из цикла
                break
            product_name = (input('Product name: ')).strip() # Запрашиваем у пользователя название товара
            found_product = next((prod for prod in self.products if prod.name.lower() == product_name.lower()), None) # Ищем товар в списке товаров
            if not found_product:
                print('There is no such product')
                continue
            try:    # Используем блок обработки исключений
                quantity = int(input('Enter the quantity: '))   # Запрашиваем количество товара
                order.add_product(found_product, quantity)  # Добавляем запрошенное количество товара в заказ
            except ValueError:
                print('Incorrect quantity')   # В случае ошибки выводим на экран сообщение 
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
    print(f'Total cost of the order: ${new_order.calculate_total()}')   # Выводим сообщение с итоговой стоимостью заказа