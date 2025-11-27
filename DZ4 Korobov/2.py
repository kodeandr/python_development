from pydantic import BaseModel, EmailStr
from typing import Optional

class Book(BaseModel):
    title: str
    author: str
    year: int
    available: bool = True

class User(BaseModel):
    name: str
    email: EmailStr
    membership_id: str

def add_book(bool: Book) -> None:
    # Descriotion of the logic for adding a book to the database
    print('The book {book.title} has been added successfully')

def find_book(title: str) -> Optional[Book]:
    # Descriotion of the logic for searching a book in the database
    return next((b for b in library.books if b.title == title), None)

def is_book_borrow(user: User, book_title: str) -> bool:
    # Descriotion of the logic of book accessibility
    book = find_book(book_title)
    if not book or not book.available:
        raise Exception('The book is temporarily unavailable')
    else:
        book.available = False
        return True

def return_book(book_title: str) -> bool:
    # Descriotion of the logic for returning a book
    if book:
        book.available = True
        return True
    return False

