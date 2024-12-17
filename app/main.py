from contextlib import asynccontextmanager
import os
import sys
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from .routers import admin, posts, sign_in, store
from backend.db import create_tables, delete_tables

'''
Удобное создание таблиц для отладки кода'''

@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    print('База очищена')
    await create_tables()
    print('База создана и готова к работе')
    yield
    print('Выключение')
    

app = FastAPI(lifespan=lifespan) 


# Укажите директорию для статических файлов
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# подключает директорию для обработки темплейда
templates = Jinja2Templates(directory="app/templates")

# Настройка SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key="260694")



@app.get("/", response_class=HTMLResponse, name="primary")
async def primary(request: Request) -> dict:
    return templates.TemplateResponse("store/primary.html", {"request": request})


#Подключение роутеров из других файлов
app.include_router(admin.router)
app.include_router(store.router)
app.include_router(posts.router)
app.include_router(sign_in.router)


# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])
'''dependencies=[Depends(verify_token), Depends(verify_key)]: Этот параметр dependencies указывает, 
что все маршруты, определенные в этом экземпляре приложения, будут использовать указанные зависимости.
при каждом запросе к любому маршруту в этом приложении будут автоматически вызываться функции verify_token и verify_key, 
что позволяет реализовать централизованную логику аутентификации и авторизации. Если одна из этих зависимостей не пройдет проверку, запрос может быть отклонен до того, 
как будет достигнут обработчик маршрута.'''





# Запуск сервера осуществите командой, приложение начнет работать на странице
# python -m uvicorn app.main:app
# или в режиме релоуда (перезапуск при изменениях)
# uvicorn app.main:app --reload
# или в режиме отладки
# uvicorn app.main:app --reload --log-level debug

# Инициализация Alembic в конкретной папке
# alembic init app/migrations

'''alembic.ini - sqlalchemy.url
Он должен выглядеть примерно так:
Для PostgreSQL: postgresql://user:password@localhost/dbname
Для MySQL: mysql+pymysql://user:password@localhost/dbname
Для SQLite: sqlite:///path/to/database.db'''

'''Если вы используете PostgreSQL, вам нужно установить psycopg2 или asyncpg:
pip install psycopg2
# или для асинхронной поддержки
pip install asyncpg
Если вы используете MySQL, вам может понадобиться установить pymysql:
pip install pymysql
Для SQLite обычно не требуется дополнительная установка, так как он включен в Python.'''

'''env.py
-------------
from alembic import context
from sqlalchemy import engine_from_config, pool
from myapp import mymodel  # Импортируйте ваши модели здесь
from myapp.database import Base  # Импортируйте Base, если используете его

# Получаем объект MetaData
target_metadata = Base.metadata  # Убедитесь, что вы используете правильный объект MetaData

config = context.config

# Настройка подключения
connectable = engine_from_config(
    config.get_section(config.config_ini_section),
    prefix='sqlalchemy.',
    poolclass=pool.NullPool,
)

'''
# миграция 
# alembic revision --autogenerate -m "Initial migration"

# Выполните команду 
# alembic upgrade head
# которая позволит вам применить последнюю миграцию и создать таблицы  и запись текущей версии миграции если таблицы создаются в файле evn

