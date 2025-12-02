from pydantic import BaseModel, EmailStr, HttpUrl, PositiveInt, Field, field_validator, model_validator
from typing import Optional, List, Dict, Annotated
from pydantic.types import StringConstraints

class Author(BaseModel):
    name: str
    email: EmailStr    

class Message(BaseModel):
    id: int = Field(..., gt=0)
    content: str = Field(min_length=1, max_length=500, pattern=r"^[a-zA-Z0-9\s!,.?]*$")  
    # Строка 1-500 символов, только буквы, цифры, пробелы и знаки

    tags: Optional[list[str]] = None
    mems: list[str] | None
    priority: float = Field(default=0.0, ge=0.0, le=10.0) # Число от 0 до 10
    email: EmailStr
    website: HttpUrl
    age: PositiveInt
    author = Author(name="ALice", email="alice@example.ru")
    data = list[str] # Список строк
    metadata = dict[str, int] # Словарь с ключами-строками и значениями-числами

    @field_validator('content')
    @classmethod
    def check_forbidden_words(cls, value):
        forbidden_words = ["spam", "offensive"]:
        if any(word in value.lower() for word in forbidden_words):
            raise ValueError("Message contains forbidden words")
        return value

class User(BaseModel):
    name: str
    age: int
    email: str

    @model_validator(mode='after')
    def check_age_and_email(self):
        if  self.age < 18 and self.email:
            raise ValueError("Несовершеннолетним нельзя указывать email")
        return self
    
data = {"name": "Alice", "age": 16, "email": "alice@example.com"}
try:
    user = User.model_validate(data)
except ValueError as e:
    print(e)  # Выведет: Несовершеннолетним нельзя указывать email

message = Message(id=1, content='Hello, Pydantic!')
print(message.model_dump()) # Сериализация в словарь: {'id': 1, 'content': 'Hello, Pydantic!'}
print(message.model_dump_json()) # Сериализация в JSON: {"id": 1, "content": "Hello, Pydantic!"}
