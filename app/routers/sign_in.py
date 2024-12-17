import os
import sys
from datetime import datetime

from fastapi import responses
from fastapi import APIRouter, Depends, Form, Path, Request, status, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
# Сессия БД
from sqlalchemy.ext.asyncio import AsyncSession
# Аннотации, Модели БД и Pydantic.
from typing import Annotated
# Функции работы с записями.
from sqlalchemy import insert, select


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.db_depends import get_db
from models.sign_in import User
from schemas.schemas import *
from schemas.forms import UserCreateForm

# Создаем контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

templates = Jinja2Templates(directory="app/templates")


router = APIRouter(prefix="/sign_in", tags=["sign_in"])


async def create_new_user(user: UserCreateForm, db: AsyncSession):
    new_user = User(
        username=user.username,
        email=user.email,
        birthdate=user.birthdate,
        password=user.password  # Не забудьте захешировать пароль перед сохранением
    )
    
    db.add(new_user)
    await db.commit()  # Сохраняем изменения
    await db.refresh(new_user)  # Обновляем объект, чтобы получить ID и другие поля
    return new_user


# для отображения формы для нового пользователя
@router.get("/", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("sign_in/sign_in.html", {"request": request})

# для создания нового пользователя
# Функция регистрации пользователя
@router.post("/", response_class=HTMLResponse, name="sign_in")
async def sign_in(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    form = UserCreateForm(request)
    await form.load_data()

    if await form.is_valid():
        hashed_password = pwd_context.hash(form.password1) 
        user = User(
            username=form.username, email=form.email, birthdate=form.birthdate, password=hashed_password
        )
        try:
            db.add(user)
            await db.commit()  
            await db.refresh(user) 
            form.__dict__.get("errors").append("Регистрация прошла успешно") 
            return templates.TemplateResponse("store/primary.html", form.__dict__)
        except IntegrityError:
            form.__dict__.get("errors").append("Такой пользователь уже существует")
            return templates.TemplateResponse("sign_in/sign_in.html", form.__dict__)
    
    return templates.TemplateResponse("sign_in/sign_in.html", form.__dict__)
    