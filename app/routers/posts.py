import os
import sys
from fastapi import APIRouter, Depends, Form, Query, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
# Функция для отправки по эмейлу
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
# Сессия БД
from sqlalchemy.ext.asyncio import AsyncSession
# Аннотации, Модели БД и Pydantic.
from typing import Annotated, List
# Функции работы с записями.
from sqlalchemy import  insert, select

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.db_depends import get_db
from models.posts import Post, Comment
from schemas.schemas import *


templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/posts", tags=["posts"])

# функция отображает все посты с пагинатором
@router.get("/", response_class=HTMLResponse, name="posts")
async def post_list(request: Request,
                    db: Annotated[AsyncSession, Depends(get_db)],
                    post_slug: Optional[str] = None,
                    items_per_page: int = Query(2, gt=0),  # Минимум 1 элемент на странице
                    page: int = Query(1, gt=0),  # Минимум 1 страница
                    ):
    
    # Получаем все опубликованные посты
    query = select(Post).where(Post.published.is_(True))
    
    if post_slug:
        post = db.scalar(select(Post).where(Post.slug == post_slug))
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return templates.TemplateResponse("spaceposts/detail.html", {"request": request, "post": post})

    # Получаем общее количество постов
    result = await db.execute(query)
    total_posts = result.scalars().all()  # Получаем скалярные результаты

    # Пагинация
    total_count = len(total_posts)
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_posts = total_posts[start:end]

    if total_count == 0 or not paginated_posts:
        return templates.TemplateResponse("posts/list.html", {"request": request})
    
    # Создаем контекст для шаблона
    context = {
        'request': request,
        'posts': paginated_posts,
        'page': page,
        'items_per_page': items_per_page,
        'total_count': total_count,
        'total_pages': (total_count + items_per_page - 1) // items_per_page,
        'has_previous': page > 1,
        'previous_page_number': page - 1 if page > 1 else None,
        'has_next': page < (total_count + items_per_page - 1) // items_per_page,
        'next_page_number': page + 1 if page < (total_count + items_per_page - 1) // items_per_page else None,
    }  

    return templates.TemplateResponse("posts/list.html", context)





# отображение деталей поста
@router.get("/{year}/{month}/{day}/{post}", response_class=HTMLResponse)
async def post_detail(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    year: int,
    month: int,
    day: int,
    post: str
    ):

    # Получаем пост по slug и дате публикации
    post_query = select(Post).where(
        Post.slug == post,
        Post.published.is_(True),
        Post.publish.year == year,
        Post.publish.month == month,
        Post.publish.day == day
    )
    
    post_obj = await db.execute(post_query).scalar_one_or_none()
    
    if post_obj is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # Получаем активные комментарии
    result = await db.query(Comment).filter(Comment.post_id == post_obj.id, Comment.active.is_(True))
    comments = result.all()
    
    # Обработка формы комментария
    new_comment = None
    comment_form = {
        'name': request.user.username if request.user.is_authenticated else '',
        'email': request.user.email if request.user.is_authenticated else ''
    }

    # Если запрос POST, обрабатываем новый комментарий
    if request.method == 'POST':
        data = await request.form()
        name = data.get('name')
        email = data.get('email')
        body = data.get('body')

        if name and email and body:  # Простейшая валидация
            new_comment = Comment(name=name, email=email, body=body, post=post_obj)
            db.add(new_comment)
            await db.commit()
            return templates.TemplateResponse("spaceposts/detail.html", {"request": request, "post": post_obj, "comments": comments, "new_comment": new_comment, "comment_form": comment_form})

    # Получаем похожие посты
    post_tags_ids = [tag.id for tag in post_obj.tags] if post_obj.tags else []
    similar_posts_query = (
        select(Post)
        .where(Post.published.is_(True))
        .filter(Post.tags.any(id.in_(post_tags_ids)))
        .filter(Post.id != post_obj.id)
        .order_by(Post.publish.desc())
    )
    
    result = await db.execute(similar_posts_query).scalars()
    similar_posts = result.all()[:4]

    # Создаем контекст для шаблона
    context = {
        'request': request,
        'post': post_obj,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts
    }

    return templates.TemplateResponse("posts/detail.html", context)























# для отображения формы для нового поста
@router.get("/all_comments", response_model=List[PostResponse])
async def create_comment_form(request: Request):
    return templates.TemplateResponse("admin/comments.html", {"request": request})

# для создания нового поста
@router.post("/all_comments", response_class=HTMLResponse)
async def create_comment(request: Request, 
                    post_id: Annotated[int, Form(description="слаг")],
                    name: Annotated[str, Form( description="название")],
                    email: Annotated[str, Form(description="текст")],
                    body: Annotated[int, Form(description="статус")],
                    db: Annotated[AsyncSession, Depends(get_db)]):
    
    # Проверка на существование поста с таким же телом
    existing_comment = await db.scalar(select(Comment).where(Comment.body == body))
    if existing_comment:
        raise HTTPException(status_code=404, detail='Post already exists')
    
    # Создание нового поста
    new_comment = {
        "post_id": post_id,
        "name": name,
        "email": email,
        "body": body
      }  
    
    db.execute(insert(Comment).values(new_comment))
    await db.commit()
    
    return templates.TemplateResponse("admin/posts.html", {"request": request, "new_comment": new_comment}) 

# Настройка почтового сервиса
# тестовый SMTP-сервер, который позволяет отправлять письма без 
# необходимости использования реальных учетных данных.
'''Пример настройки для Mailtrap
Если вы решили использовать Mailtrap, вам нужно зарегистрироваться на их сайте и получить учетные данные для SMTP. Пример настройки ConnectionConfig для Mailtrap:'''
'''from fastapi_mail import ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="your_mailtrap_username",  # Ваш Mailtrap username
    MAIL_PASSWORD="your_mailtrap_password",  # Ваш Mailtrap password
    MAIL_FROM="no-reply@mailtrap.io",         # Адрес электронной почты отправителя (можно использовать любой)
    MAIL_PORT=587,                            # Порт SMTP (обычно 587)
    MAIL_SERVER="smtp.mailtrap.io",           # SMTP-сервер Mailtrap
    MAIL_FROM_NAME="Test App",                 # Имя отправителя
    MAIL_TLS=True,                            # Использовать TLS
    MAIL_SSL=False,                           # Не использовать SSL
)'''


#функция для отправки поста
'''@router.post("/share/{post_id}", response_class=HTMLResponse)
async def post_share(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    post_id: int,
    form: EmailPostForm,
):
    # Получение статьи по id
    post = db.query(Post).filter(Post.id == post_id, Post.status == 'published').first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Отправка поста
    post_url = request.url_for("post_detail", year=post.publish.year, month=post.publish.month, day=post.publish.day, post=post.slug)
    subject = f"{form.name} ({form.email}) recommends you reading '{post.title}'"
    message = f'Read "{post.title}" at {post_url}\n\n{form.name}\'s comments:\n{form.comments}'

    # Отправка почты
    message = MessageSchema(
        subject=subject,
        recipients=[form.to],
        body=message,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

    # Контекст для шаблона
    context = {
        'post': post,
        'form': form,
        'sent': True
    }

    return templates.TemplateResponse("spaceposts/share.html", context)
'''