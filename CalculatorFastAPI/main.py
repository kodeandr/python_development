from fastapi import FastAPI
from pydantic import BaseModel
from typing import ClassVar 

# Создаем веб-приложение
app = FastAPI(
    title='Simple calculator',
    description='Calculator with base operations', 
    version='1.0.0'
)

# Класс для простых операций
class SimpleOperation(BaseModel):
    a: float
    op: str
    b: float

# Класс для выражений 
class ExpressionRequest(BaseModel):
    expression: str

current_expression = ''
variables = {}

def simple_calculate(a, op, b):
    if op == '+':
        return a + b
    elif op == '-':
        return a - b
    elif op == '*':
        return a * b
    elif op == '/':
        if b == 0:
            return "Zero division error"
        return a / b
    else:
        return 'Unknown operation'  # ← исправил опечатку
    
def evaluate_expression(expression):
    try:
        # Безопасное вычисление выражения
        result = eval(expression, {"__builtins__": None}, variables)
        return result
    except Exception as e:
        return f"Ошибка: {str(e)}"    
    
@app.get('/')
async def home():
    return {'message': 'Welcome to my calculator!'}

@app.post('/calculate')
async def calculate_simple(operation: SimpleOperation):
    result = simple_calculate(operation.a, operation.op, operation.b)
    return {
        "operation": f"{operation.a} {operation.op} {operation.b}",
        "result": result
    }

@app.post('/set_expression')
async def set_expression(expr: ExpressionRequest):
    global current_expression
    current_expression = expr.expression
    
    return {
        "message": "Выражение установлено", 
        "expression": current_expression
    }

@app.post("/evaluate")
async def evaluate_current():
    global current_expression
    
    if not current_expression:
        return {"error": "Нет выражения для вычисления"}
    
    result = evaluate_expression(current_expression)
    
    return {
        "expression": current_expression,
        "result": result
    }

@app.get("/expression")
async def get_expression():
    return {
        "current_expression": current_expression,
        "variables": variables
    }

@app.post("/variable/{name}/{value}")
async def add_variable(name: str, value: float):
    variables[name] = value
    
    return {
        "message": f"Переменная {name} = {value}",
        "variables": variables
    }

@app.get("/calc/{a}/{op}/{b}")
async def quick_calculate(a: float, op: str, b: float):
    op_symbols = {
        "plus": "+",
        "minus": "-", 
        "multiply": "*",
        "divide": "/"
    }
    
    operation = op_symbols.get(op, op)
    result = simple_calculate(a, operation, b)
    
    return {
        "operation": f"{a} {operation} {b}",
        "result": result
    }