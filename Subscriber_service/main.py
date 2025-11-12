from fastapi import FastAPI
from pydantic import BaseModel, field_validator, EmailStr
from datetime import date
import json
import os
import time

app = FastAPI()

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

class SubscriberAppeal(BaseModel):
    last_name: str
    first_name: str
    birth_date: date
    phone_number: str
    email: EmailStr

    def is_cyrillic(self, text: str) -> bool:
        cyrillic = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя- '
        return all(char.lower() in cyrillic for char in text)

    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls, value: str):
        if not value:
            raise ValueError('Фамилия не может быть пустой')
        if not value[0].isupper():
            raise ValueError('Фамилия должна начинаться с заглавной буквы')
        
        temp_instance = cls(last_name='', first_name='', birth_date=date(2000,1,1), 
                           phone_number='+70000000000', email='test@test.com')
        if not temp_instance.is_cyrillic(value):
            raise ValueError('Фамилия должна содержать только кириллические символы')
        return value

    @field_validator('first_name')
    @classmethod
    def validate_first_name(cls, value: str):
        if not value:
            raise ValueError('Имя не может быть пустым')
        if not value[0].isupper():
            raise ValueError('Имя должно начинаться с заглавной буквы')
        
        temp_instance = cls(last_name='', first_name='', birth_date=date(2000,1,1), 
                           phone_number='+70000000000', email='test@test.com')
        if not temp_instance.is_cyrillic(value):
            raise ValueError('Имя должно содержать только кириллические символы')
        return value

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, value: str):
        clean_phone = value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        if clean_phone.startswith('+7') and len(clean_phone) == 12:
            return value
        elif clean_phone.startswith('8') and len(clean_phone) == 11:
            return value
        else:
            raise ValueError('Телефон должен быть в формате: +7XXX... или 8XXX...')

@app.post("/appeal/")
async def create_appeal(appeal: SubscriberAppeal):
    filename = f"{DATA_DIR}/appeal_{int(time.time())}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(appeal.dict(), f, ensure_ascii=False, indent=2, default=str)
    
    return {
        "message": "Обращение успешно сохранено",
        "filename": filename
    }

@app.get("/")
async def root():
    return {"message": "Сервис для сбора обращений абонентов"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)