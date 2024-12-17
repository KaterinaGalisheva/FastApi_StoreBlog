import sys
import os
from sqlalchemy import Column, Date, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.db import Base

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = 'users' #указывает имя таблицы в базе данных, которая будет соответствовать этому классу
    id = Column(Integer, primary_key=True, index=True) #Каждый атрибут класса соответствует столбцу в таблице базы данных:
    # Column — это функция, которая определяет столбец в таблице.
    #Integer — тип данных столбца.
    #primary_key=True указывает, что этот столбец является первичным ключом.
    #index=True создает индекс для этого столбца, что ускоряет поиск по нему.
    username = Column(String)
    email = Column(String)
    birthday = Column(String)
    password = Column(String) 
    goods =  relationship("Store", secondary="user_store", back_populates="buyers")
    # relationship устанавливает связь между моделью store и моделью User . Это позволяет SQLAlchemy автоматически загружать связанные объекты.
    # back_populates="users" указывает, что в модели User  также будет связь, которая ссылается на store. 
    
    def __str__(self):
        return self.username
    
    # функции хеширования пароля
    def set_password(self, password: str):
        self.password = pwd_context.hash(password)

    def verify_password(self, password: str):
        return pwd_context.verify(password, self.password)


'''# проверка создания таблицы, можно использовать при необходимости
from sqlalchemy.schema import CreateTable
print(CreateTable(User.__table__))'''