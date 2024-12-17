from datetime import datetime, timezone
import sys
import os
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.db import Base


class Post(Base):
    __tablename__ = 'posts' 
    id = Column(Integer, primary_key=True, index=True)  
    title = Column(String, nullable=False)  
    slug = Column(String, unique=True, index=True)  # Уникальный идентификатор (читаемая часть URL)
    body = Column(String, nullable=False)  
    publish = Column(DateTime, default=datetime.now(timezone.utc))  # Дата и время публикации updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Дата и время последнего обновления
    status = Column(String, default='draft')  # Статус задачи (например, 'draft', 'published'')
    image = Column(String, nullable=True)  
    published = Column(Boolean, default=False)  # Флаг, указывающий, опубликована ли задача
    tags = Column(String, nullable=True)  # Теги задачи (можно хранить как строку, разделенную запятыми)
    comments = relationship("Comment", back_populates="post")

    def __str__(self):
        return self.title


class Comment(Base):
    __tablename__ = 'comments' 

    id = Column(Integer, primary_key=True)  
    post_id = Column(ForeignKey('posts.id'), nullable=False)  
    name = Column(String(80), nullable=False)  
    email = Column(String, nullable=False)  
    body = Column(Text, nullable=False)
    created = Column(DateTime, default=datetime.now(timezone.utc))  # Дата и время создания комментарияupdated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)
    # Определение связи с моделью Post
    post = relationship('Post', back_populates='comments')

    class Meta:
        ordering = ('created', )

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'



'''# проверка создания таблицы, можно использовать при необходимости
from sqlalchemy.schema import CreateTable
print(CreateTable(Post.__table__))
print(CreateTable(Comment.__table__))'''