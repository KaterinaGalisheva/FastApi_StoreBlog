from datetime import date, datetime
from typing import List, Optional
from fastapi import Request
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreateForm():
    def __init__(self, request:Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str]=None
        self.email: Optional[str]=None
        self.birthdate: Optional[str]=None
        self.password1: Optional[str]=None
        self.password2: Optional[str]=None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get('username')
        self.email = form.get('email')
        self.birthdate = form.get('birthdate')
        self.password1 = form.get('password1')
        self.password2 = form.get('password2')

    
    # функции хеширования пароля
    def set_password(self, password: str):
        self.password = pwd_context.hash(password)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password)

        
    async def is_valid(self):
        if not self.username or not len(self.username) > 5:
            self.errors.append('Имя должно быть более 5 символов')
        if not self.email or not (self.email.__contains__("@")):
            self.errors.append('Некорректный email')
        if not self.birthdate:
            self.errors.append('Дата рождения обязательна')
        if not self.password1 or not len(self.password1) > 6:
            self.errors.append('Создайте пароль от 6 символов')
        if self.password1 != self.password2:
            self.errors.append('Пароли не совпадают')


            

