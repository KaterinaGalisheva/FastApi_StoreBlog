import sys
import os
from sqlalchemy import Column, Float, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.db import Base
from models.sign_in import User



class Store(Base):
    __tablename__ = 'store' 
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    size = Column(Float)
    description = Column(Text)
    cost = Column(Integer)
    photo = Column(String)
    uploaded_at = Column(Boolean, default=False) #По умолчанию значение False
    buyers = relationship("User", secondary="user_store", back_populates="goods")
    
    def __str__(self):
        return self.title
    

class UserStore(Base):
    __tablename__ = 'user_store'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    store_id = Column(Integer, ForeignKey('store.id'), primary_key=True)

'''# проверка создания таблицы, можно использовать при необходимости
from sqlalchemy.schema import CreateTable
print(CreateTable(Store.__table__))'''