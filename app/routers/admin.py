import os
import sys
from fastapi import APIRouter, Depends, Form, HTTPException, Path, Request, status
# Сессия БД
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

# Аннотации, Модели БД и Pydantic.
from typing import Annotated, List

# Функции работы с записями.
from sqlalchemy import insert, select, update, delete
from slugify import slugify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.db_depends import get_db
from models.sign_in import User
from models.posts import Post, Comment
from models.store import Store
from schemas.schemas import *

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/admin", tags=["admin"])


# Функции для отображения админки
@router.get("/", response_class=HTMLResponse, name="admin")
async def admin_panel(request: Request):
    return templates.TemplateResponse("admin/admin.html", {"request": request})


"""------------------------------------------------------------------------------------- АДМИНКА ДЛЯ ПОЛЬЗОВАТЕЛЕЙ ------------------------------------------------------------------------------"""


# Функции для управления пользователями
@router.get("/all_users", response_model=List[UserResponse])
async def get_users(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User))
    users = result.all()
    return templates.TemplateResponse(
        "admin/users.html", {"request": request, "users": users}
    )

# для отображения формы для нового пользователя
@router.get("/user_form", response_model=List[UserResponse])
async def user_form(request: Request):
    return templates.TemplateResponse("admin/users.html", {"request": request})

# для создания нового пользователя
@router.post("/create_user", response_class=HTMLResponse)
async def create_user(
    request: Request,
    username: Annotated[str, Form(description="Имя пользователя")],
    email: Annotated[str, Form(description="Электронная почта пользователя")],
    birthdate: Annotated[str, Form(description="Дата рождения в формате %Y-%m-%d")],
    password: Annotated[str, Form(description="Пароль")],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    # Проверка на существование пользователя с таким же именем
    existing_user = await db.scalar(select(User).where(User.username == username))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    '''ИЗМЕНЕН СПОСОБ ДОБАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯ. ЕСЛИ ЗАРАБОТАЕТ, ОСТАЛЬНОЕ ТОЖЕ ПЕРЕДЕЛАТЬ'''
    # Создание нового пользователя
    hashed_password = pwd_context.hash(password)
    new_user = User(username=username,
        email=email,
        birthdate=birthdate,
        password=hashed_password,
        slug=slugify(username),
    )  # Генерация slug

    try:
        db.add(new_user)  
        await db.commit()  
    except Exception as e:
        await db.rollback()  # В случае ошибки откатываем изменения
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occurred while creating user") from e

    return templates.TemplateResponse("admin/users.html", {"request": request, "new_user": new_user})


@router.put("/update_user/{user_id}", response_model=UserResponse)
async def update_user(
    request: Request,
    user_id: int,
    username: Annotated[str, Form(description="Имя пользователя")],
    email: Annotated[str, Form(description="Электронная почта пользователя")],
    birthdate: Annotated[str, Form(description="Дата рождения в формате ДД-ММ-ГГГГ")],
    password: Annotated[str, Form(description="Пароль")],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    # Преобразование строки даты в объект даты
    birthdate_obj = datetime.strptime(birthdate, "%Y-%m-%d").date()

    user1 = select(User).where(User.id == user_id)
    result = await db.execute(user1)
    user = result.scalar_one_or_none()  # Получаем единственного пользователя или None
    if not user:
        raise HTTPException(status_code=404, detail="User  not found")

    # Создание нового пользователя
    hashed_password = pwd_context.hash(password)
    update_user = {
        "username": username,
        "email": email,
        "birthdate": birthdate_obj,
        "password": hashed_password,
        "slug": slugify(username),
    }  # Генерация slug

    db.execute(update(User).values(update_user))
    await db.commit()
    return templates.TemplateResponse("admin/users.html", {"request": request, "update_user": update_user})


@router.delete("/delete_user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    request: Request, user_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    user1 = select(User).where(User.id == user_id)
    result = await db.execute(user1)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User  not found")
    db.delete(user)
    await db.commit()
    return templates.TemplateResponse("admin/users.html", {"request": request, "user": user})


"""------------------------------------------------------------------------------------- АДМИНКА ДЛЯ ТОВАРОВ ------------------------------------------------------------------------------"""


# Функции для управления товарами
@router.get("/store_all", response_model=List[StoreResponse])
async def get_stores(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Store))
    store = result.all()
    return templates.TemplateResponse("admin/store.html", {"request": request, "store": store})


# для отображения формы для нового продукта
@router.get("/store_form", response_model=List[StoreResponse])
async def store_form(request: Request):
    return templates.TemplateResponse("admin/store.html", {"request": request})


# для создания нового продукта
@router.post("/store_create", response_class=HTMLResponse)
async def create_store(
    request: Request,
    title: Annotated[str, Form(description="название")],
    size: Annotated[float, Form(description="размер")],
    description: Annotated[str, Form(description="описание")],
    cost: Annotated[int, Form(description="Стоимость")],
    photo: Annotated[str, Form(description="фото товара")],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    # Проверка на существование товара с таким же именем
    existing_product = await db.scalar(select(Store).where(Store.title == title))
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Product already exists"
        )

    # Создание нового пользователя
    new_product = Store(
        title=title,
        size=size,
        description=description,
        cost=cost,
        photo=photo,
        slug=slugify(title))  # Генерация slug

    try:
        db.add(new_product)  
        await db.commit()  
    except Exception as e:
        await db.rollback()  # В случае ошибки откатываем изменения
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error occurred while creating user") from e

    return templates.TemplateResponse("admin/store.html", {"request": request, "new_product": new_product})


@router.put("/store_update/{store_id}", response_model=StoreResponse)
async def store_apdate(
    request: Request,
    store_id: int,
    title: Annotated[str, Form(description="название")],
    size: Annotated[float, Form(description="размер")],
    description: Annotated[str, Form(description="описание")],
    cost: Annotated[int, Form(description="Стоимость")],
    photo: Annotated[str, Form(description="фото товара")],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    store1 = select(Store).where(Store.id == store_id)
    result = await db.execute(store1)
    store = result.scalar_one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    # Создание нового пользователя
    update_product = {
        "title": title,
        "size": size,
        "description": description,
        "cost": cost,
        "photo": photo,
        "slug": slugify(title),
    }  # Генерация slug

    db.execute(update(Store).values(update_product))
    await db.commit()

    return templates.TemplateResponse("admin/store.html", {"request": request, "update_product": update_product})


@router.delete("/store_delete/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
async def store_delete(
    request: Request, store_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    store1 = select(Store).where(Store.id == store_id)
    result = await db.execute(store1)
    store = result.scalar_one_or_none()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    await db.delete(store)
    await db.commit()
    return templates.TemplateResponse("admin/store.html", {"request": request, "store": store})


"""------------------------------------------------------------------------------------- АДМИНКА ДЛЯ ПОСТОВ -----------------------------------------------------------------------------------"""


# Функции для управления постами
@router.get("/all_posts", response_model=List[PostResponse])
async def get_posts(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Post))
    posts = result.all()
    return templates.TemplateResponse(
        "admin/posts.html", {"request": request, "posts": posts}
    )


# для отображения формы для нового поста
@router.get("/posts_form", response_model=List[PostResponse])
async def post_form(request: Request):
    return templates.TemplateResponse("admin/posts.html", {"request": request})


# для создания нового поста
@router.post("/create_post", response_class=HTMLResponse)
async def create_post(
    request: Request,
    title: Annotated[str, Form(description="название")],
    slug: Annotated[float, Form(description="слаг")],
    body: Annotated[str, Form(description="текст")],
    status: Annotated[int, Form(description="статус")],
    image: Annotated[str, Form(description="изображение")],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    # Проверка на существование поста с таким же именем
    existing_post = await db.scalar(select(Post).where(Post.title == title))
    if existing_post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Post already exists")

    # Создание нового поста
    new_post = {
        "title": title,
        "slug": slug,
        "body": body,
        "status": status,
        "image": image,
        "slug": slugify(title),
    }  # Генерация slug

    db.execute(insert(Post).values(new_post))
    await db.commit()

    return templates.TemplateResponse("admin/posts.html", {"request": request, "new_post": new_post})


@router.put("/update_post/{post_id}", response_model=PostResponse)
async def update_post(
    request: Request,
    post_id: int,
    title: Annotated[str, Form(description="название")],
    slug: Annotated[float, Form(description="слаг")],
    body: Annotated[str, Form(description="текст")],
    status: Annotated[int, Form(description="статус")],
    image: Annotated[str, Form(description="изображение")],
    db: Annotated[AsyncSession, Depends(get_db)],
):

    post1 = select(Post).where(Post.id == post_id)
    result = await db.execute(post1)
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Создание нового поста
    update_post = {
        "title": title,
        "slug": slug,
        "body": body,
        "status": status,
        "image": image,
        "slug": slugify(title),
    }  # Генерация slug

    db.execute(update(Post).values(update_post))
    await db.commit()

    return templates.TemplateResponse("admin/posts.html", {"request": request, "update_post": update_post})


@router.delete("/delete_post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    request: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    post1 = select(Post).where(Post.id == post_id)
    result = await db.execute(post1)
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(post)
    await db.commit()
    return templates.TemplateResponse("admin/posts.html", {"request": request, "post": post})


"""------------------------------------------------------------------------------------- АДМИНКА ДЛЯ КОМЕНТАРИЕВ -----------------------------------------------------------------------------------"""


# Функции для управления комментариями
@router.get("/all_comments", response_model=List[CommentResponse])
async def get_comments(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(Comment))
    comments = result.all()
    return templates.TemplateResponse("admin/comments.html", {"request": request, "comments": comments})


@router.delete("/all_comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    request: Request, comment_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    comment1 = select(Comment).where(Comment.id == comment_id)
    result = await db.execute(comment1)
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    await db.commit()
    return templates.TemplateResponse("admin/comments.html", {"request": request, "comment": comment})
