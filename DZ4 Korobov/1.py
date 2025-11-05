
from pydantic import BaseModel, EmailStr

class Book(BaseModel):
    title: str
    author: str
    year: int
    available: bool = True

class User(BaseModel):
    name: str
    email: EmailStr
    membership_id: str

