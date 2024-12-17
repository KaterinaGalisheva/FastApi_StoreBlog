
'''Работа с WEB страницами через fastapi'''

# pip install fastapi uvicorn jinja2 aiofiles
# pip install aiosqlite ассинхронный движок
# pip install passlib[bcrypt]
# passlib — это библиотека для работы с паролями, которая предоставляет удобные функции для хеширования и проверки паролей. Использование CryptContext из passlib позволяет легко управлять различными алгоритмами хеширования и их настройками.



# используем библиотеку, для работы с веб интерфейсами
from fastapi import Body, FastAPI, HTTPException, Path
from typing import Annotated

# пишем backend интерфейс

# инициализация приложения
app = FastAPI



# ключевые запросы
# Get - адрес в строке ?переменная=значение
# Post - оформление заказа, отправка данных на сервер
# Put - обновление, замена
# Delete - запрос на удаление


@app.get("/")
async def welcome() -> dict:
    return {"message": "Hello World"}

@app.get("/main")
async def welcome() -> dict:
    return {"message": "main page"}

# как запустить приложение? 
# пишем в терминале:
# python3 -m uvicorn main:app и энтер


# Как перейти на страницу с документацией этой страницы?
# в адресной строке добавить
# /docs


# обработка зараннее неизвестной ссылки
@app.get("/user/{first_name}/{last_name}")
async def news (first_name: str, last_name: str) -> dict:
    return {"message": f"hello, {first_name} {last_name}"}

  
# формируем гет запрос
@app.get("/id")
async def id_paginator(username: str, age: int) -> dict:
    return {"User": username, "Age":age}

# переменные по умолчанию
# async def id_paginator(username: str = Kate, age: int = 30) -> dict:

#если переменных по умолчанию нет, для гет запросов с переменными пишем в адресной строке 
# /id?username=Kate&age=30     & - соединяет переменные


'''Построение валидации входящих данных'''

# обработка зараннее неизвестной ссылки
# как проверять те данные, которые к нам приходят?
from fastapi import Path # для настройки элементов, контроль приходящих данных
from typing import Annotated

@app.get("/user/{username}/{id}")
async def news (username: str = Path(min_length=3, max_length=15, description='enter username'), id: int = Path(ge=0, le=100, description='enter id')) -> dict:
# или async def news (username: Annotated[str, Path(min_length=3, max_length=15, description='enter username'), id: int = Path(ge=0, le=100, description='enter id')]) -> dict:
   return {"message": f"hello, {username}:{id}"}




'''CRUD запросы. Запросы: Get, Post, Put Delete'''

# ключевые запросы
# Get - адрес в строке ?переменная=значение
# Post - оформление заказа, отправка данных на сервер
# Put - обновление, замена
# Delete - запрос на удаление

message_db = {'0':'First post in FastApi'}

@app.get('/')
async def get_all_messages() -> dict:
    return message_db


@app.get('/message/{message_id}')
async def get_message(message_id: str) -> dict:
    return message_db[message_id]


@app.post('/message')
async def create_messaage(message: str) -> str:
    current_index = str(int(max(message_db, key=int)) +1)
    message_db[current_index] = message
    return 'message created'


@app.put('/message/{message_id}')
async def update_message(message_id: str, message: str) -> str:
    message_db[message_id] = message
    return 'message apdated'


@app.delete('/message/{message_id}')
async def delete_message(message_id: str) -> str:
    message_db.pop(message_id)
    return f'message with {message_id} was deleted'


@app.delete('/')
async def delete_all_messeges() -> str:
    message_db.clear()
    return f'all messages was deleted'



'''Модели данных Pydantic'''

# для удобства форматирования некоторых данных
from pydantic import BaseModel

app = FastAPI()

messages_db = []

class Message(BaseModel):
    id: int = None
    text: str


@app.get('/')
def get_all_message() -> list[Message]:
    return messages_db


@app.get(path='/message/{message_id}')
def get_message(message_id: int) -> Message:
    try:
        return messages_db[message_id]
    except IndexError:
        raise HTTPException(status_code=404, detail='Message not found')
    

@app.post('/message')
def create_messaage(message: str) -> str:
    message.id = len(messages_db)
    messages_db.append(message)
    return 'message created'


@app.put('/message/{message_id}')
def update_message(message_id: int, message: str = Body()) -> str:
    try:
        edit_message = messages_db[message_id]
        edit_message.text = message
        return 'message apdated'
    except IndexError:
        raise HTTPException(status_code=404, detail='Message not found')


@app.delete('/message/{message_id}')
def delete_message(message_id: int) -> str:
    try:
        messages_db.pop(message_id)
        return f'message with {message_id} was deleted'
    except IndexError:
        raise HTTPException(status_code=404, detail='Message not found')


@app.delete('/')
def delete_all_messeges() -> str:
    messages_db.clear()
    return f'all messages was deleted'




'''Шаблонизатор Jinja 2. TemplateResponse.'''

# подключает директорию для обработки темплейда
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory='название нашей рабочей папки с файлами html')



'''SessionMiddleware, который предоставляет поддержку сессий для вашего приложения.'''

# pip install starlette itsdangerous

# starlette.middleware.sessions import SessionMiddleware

# app = FastAPI()

# Настройка SessionMiddleware
# app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

# Теперь вы можете использовать request.session в ваших маршрутах










