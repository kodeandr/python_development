from pydantic import BaseModel, EmailStr, validator
from typing import List


class Book(BaseModel):
    title: str
    author: str
    year: int
    available: bool = True


class User(BaseModel):
    name: str
    email: EmailStr
    membership_id: str


class Library(BaseModel):
    books: List[Book]
    users: List[User]

    def total_books(self) -> int:
         return len(self.books)     


class ExtendedBook(Book):
    categories: List[str]

    @validator('categories')
    def validate_categories(cls, value):
        if len(value) > 5:
            raise ValueError("Количество категорий должно быть меньше пяти.")
        return value