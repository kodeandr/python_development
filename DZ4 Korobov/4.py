import functools
import logging

class BookNotAvailable(Exception):
    pass

def is_book_borrow(user: User, book_title: str) -> bool:
    book = find_book(book_title)
    if not book or not book.available:
        raise BookNotAvailable("Книга временно недоступна")
    else:
        book.available = False
        return True
    
logging.basicConfig(level=logging.INFO)

def log_operation(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__}: {result}")
        return result
    return wrapper