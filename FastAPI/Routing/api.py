from fastapi import FastAPI, Path, Query
from typing import Annotated
app = FastAPI()

@app.get("/")
async def welcome() -> dict:
    return {"message": "Hello, FastAPI!"}

@app.get("/user")
async def login(username:str, age: int | None = None) -> dict:
    return{"user": username, "age": age}

async def search(people: Annotated[list[str], Query(
        min_length=1, max_length=15, description="List of user names", example=["Tom", "Sam"])]) -> dict:
    return {"user": people}

@app.get("/user/profile")
async def profile() -> dict:
    return {"profile": "View profile user"}

@app.get("/user/{username}")
async def login(username: Annotated [str, Path(
    min_length=3, max_length=15, description='Enter your username', example='Denis')],
    age: int) -> dict:
    return{"user": username, "age": age}
async def login_reg(
        username: Annotated[
            str, Path(min_length=3, max_length=15, description='Enter your username', 
                      example='Denis')],
        first_name: Annotated[
            str | None, Query(max_length=10, pattern="^J|s$")] = None) -> dict:
    return {"user": username, "Name":first_name}


@app.get("/user/{firstname}/{age}")
async def login(firstname: str = Path(min_length=3, max_length=15, description='Enter your username', example='Denis'),
                      age: int = Path(ge=0, le=100, description='Enter your age')) -> dict:
    return{"user": firstname, "age": age}

@app.get("/user/{name}")
async def login(
    name: Annotated[str, Path(min_length=3, max_length=15, description='Enter your name',
                              example='Denis')],
                              first_name: Annotated[str| None, Query(max_length=10)] = None) -> dict:
    return {"user ": name, "Name ": first_name}

@app.get("/hello/{user}")
async def welcome_user(user: str) -> dict:
    return {"user": f'Hello, {user} !'}

@app.get("/hello/{first_name}/{last_name}")
async def welcome_user_name(first_name: str, last_name: str) -> dict:
    return {"user": f'Hello, {first_name} {last_name}!'}

@app.get("/order/{order_id}")
async def order(order_id: int) -> dict:
    return {"id": order_id}

@app.get("/employee/{name}/company/{company}") 
async def get_employee(name: str, department: str, company: str) -> dict:
    return {"Employee": name, "Company": company, "Department": department}

@app.get("/products/{product_id}")
async def detail_view(product_id: int) -> dict:
    return {'product': f'Stock number {product_id}'}

