from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional


class StoreResponse(BaseModel):
    id: int
    title: str
    size: float
    description: str
    cost: float
    photo: str
    uploaded_at: datetime
    buyer_id: Optional[int] 

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    birthdate: date
    password: str

    class Config:
        orm_mode = True 

class RegistrationForm(BaseModel):
    username: str
    email: str
    birthdate: Optional[date] = Field(default=None)  # Делаем поле необязательным
    password1: str
    password2: str

    class Config:
        from_attributes = True
    

class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    body: str
    publish: bool
    created: datetime
    updated: datetime
    image: str
    published: bool
    tags: List[str] 

    class Config:
        orm_mode = True 

# Модель для формы отправки поста
class EmailPostForm(BaseModel):
    name: str
    email: str
    to: str
    comments: str

    class Config:
        orm_mode = True 

class CommentResponse(BaseModel):
    id: int
    post_id: int
    name: str
    email: str
    body: str
    active: bool

    class Config:
        orm_mode = True  # Это позволяет Pydantic работать с SQLAlchemy моделями

class PostResponse(BaseModel):
    id: int
    title: str
    slug: str
    body: str
    publish: bool
    created: datetime
    updated: datetime
    image: str
    published: bool
    tags: List[str] 

    class Config:
        from_attributes = True

