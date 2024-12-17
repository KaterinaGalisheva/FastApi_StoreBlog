'''Этот код создает асинхронную настройку для работы с базой данных SQLite, 
определяет базовый класс для моделей и предоставляет функции для создания и удаления таблиц в базе данных.'''

from sqlalchemy.orm import DeclarativeBase  
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


engine = create_async_engine('sqlite+aiosqlite:///Mystore.db', echo=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):  
    pass



'''
Эта функция создает все таблицы, определенные в ваших моделях, используя метаданные, связанные с базовым классом Base. 
Она использует асинхронный контекстный менеджер для управления соединением с базой данных.
В данном проекте таблицы создаются в файле evn'''

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

'''Эта функция удаляет все таблицы, определенные в ваших моделях. Она также использует асинхронный контекстный менеджер для работы с соединением.'''

async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        