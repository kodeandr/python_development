from pydantic import BaseModel
class Library(BaseModel):
    books: List[Book]
    users: List[User]
    