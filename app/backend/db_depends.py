'''Эта функция get_db предоставляет удобный способ получения и управления сессиями базы данных в асинхронном приложении. 
Она обеспечивает создание, использование и корректное закрытие сессии, что является важным аспектом работы с базами данных для предотвращения утечек ресурсов. 
В контексте фреймворков, таких как FastAPI, эту функцию часто используют в зависимости для обработки запросов к базе данных.'''

from app.backend.db import SessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

'''async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()'''

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as db:
        yield db  # Сессия будет закрыта автоматически после выхода из блока
