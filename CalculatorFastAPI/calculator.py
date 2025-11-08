from typing import List, Union, Dict

class Calculator:
    def __init__(self):
        self.expression = ''
        self.variables = {}
        self.operations = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y if y != 0 else None
        }
        self.priority = {
            '+': 1,
            '-': 1,
            '*': 2,
            '/': 2            
        }

 # 1. Простые операции    
    def simple_operation(self, a: float, op: str, b: float) -> float:
        if op not in self.operations:
            raise ValueError(f'Unsupported operation: {op}')
        if op == '/' and b == 0:
            raise ValueError(f'Zero division error')
        result = self.operations[op](a, b)
        self.expression = f'({a} {op} {b})'
        return result

# 2. Установка выражения    
    def set_expression(self, expression: str):
        self.expression = expression.strip()

 # 3. Добавление переменной   
    def add_variable(self, name: str, value: float):
        self.variables[name] = value

# 4. Получение текущего выражения
    def get_expression(self) -> str:
        return self.expression 

# 5. Простое вычисление выражения   
    def evaluate_simple(self) -> float:
        if not self.expression:
            raise ValueError('There is no expression')
        expr = self.expression
        for var, value in self.variables.items():
            expr = expr.replace(var, str(value))
        try:
            return eval(expr)
        except:
            raise ValueError('Calculation error')

# 6. Вычисление конкретного выражения
    def evaluate_custom(self, expression: str) -> float:
        original_expr = self.expression # Сохраняем оригинальное выражение, которое было установлено ранее
        self.expression = expression  # Устанавливаем новое временное выражение
        result = self.evaluate_simple() # Оцениваем новое выражение методом evaluate_simple()
        self.expression = original_expr # Восстанавливаем старое состояние выражения
        return result
    
calculator = Calculator()