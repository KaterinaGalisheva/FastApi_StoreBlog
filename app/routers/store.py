import os
import sys
from fastapi import APIRouter, Depends, Path, Query, Request, status, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
# Сессия БД
from sqlalchemy.ext.asyncio import AsyncSession
# Аннотации, Модели БД и Pydantic.
from typing import Annotated, List
# Функции работы с записями.
from sqlalchemy import select


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.db_depends import get_db
from models.store import Store
from schemas.schemas import *

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/store", tags=["store"])


# функция отображает магазин с пагинацией
@router.get("/", response_class=HTMLResponse, name="store")
async def store(request: Request,
                db: Annotated[AsyncSession, Depends(get_db)],
                page: int = 1,
                size: int = Query(10, gt=0)):  
    
    offset = (page - 1) * size
    
    # Получаем общее количество продуктов
    total_products = await db.scalar(select(func.count()).select_from(Store))

    # Получаем продукты с учетом пагинации
    result = await db.scalars(select(Store).limit(size).offset(offset))
    products = result.all()

    context_1 = {
            "request": request,
            "products": [],
            "total_pages": 0,
            "current_page": page,
            "items_per_page": size,
            "has_previous": False,
            "has_next": False,
        }
    # Если нет продуктов, возвращаем пустой список
    if total_products == 0 or not products:
        return templates.TemplateResponse("store/store.html", context_1)
    
    # Вычисляем общее количество страниц
    total_pages = (total_products // size) + (1 if total_products % size > 0 else 0)
    
    context_2 = {
        "request": request,
        "products": products,
        "total_pages": total_pages,
        "current_page": page,
        "items_per_page": size,
        "has_previous": page > 1,
        "previous_page_number": page - 1 if page > 1 else None,
        "has_next": page < total_pages,
        "next_page_number": page + 1 if page < total_pages else None,
    }

    return templates.TemplateResponse("store/store.html", context_2)


# функция отображает базу данных товаров 
@router.get("/database", response_model=List[StoreResponse], name="store:database")
async def database(request: Request,
                db: Annotated[AsyncSession, Depends(get_db)]):
    
    result = await db.execute(select(Store))
    result = result.scalars()
    products = result.all()

    if not products:
        return templates.TemplateResponse("store/database.html", {"request": request, "products": []})
    
    return templates.TemplateResponse("store/database.html", {"request": request, "products": products})
    

# функция отображает корзину
@router.get("/cart", response_model=List[StoreResponse], name="store:cart")
async def cart(request: Request,
                db: Annotated[AsyncSession, Depends(get_db)]):
    cart_ids = request.session.get('cart', [])
    result = await db.scalars(select(Store).where(Store.id.in_(cart_ids)))
    products = result.all()
    total_cost = sum(product.cost for product in products)

    if not products:
        return templates.TemplateResponse("store/cart.html", {
            "request": request,
            "products": [],
            "total_cost": 0
        })
    
    return templates.TemplateResponse("store/cart.html", {"request": request, "products": products, "total_cost":total_cost})
    


# функции для покупки товара
@router.post("/cart/{product_id}", name='buy_product')
async def buy_product(request: Request, 
                      product_id: Annotated[int, Path(ge=1, le=100, description="Enter id", example=15)],
                      db: Annotated[AsyncSession, Depends(get_db)],):
    # Получаем продукт из базы данных
    product = await db.scalar(select(Store).where(Store.id == product_id))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    # Если корзина еще не создана, создаем ее
    if 'cart' not in request.session:
        request.session['cart'] = []
    # Добавляем продукт в корзину
    if product.id not in request.session['cart']:
        request.session['cart'].append(product.id)
        request.session.modified = True
    
    return {"message": "Product added to cart", "cart": request.session['cart']}


# функции для очистки корзины
@router.post("/cart")
async def clear_cart(request: Request):
    # Очищаем корзину
    request.session['cart'] = []
    request.session.modified = True
    return templates.TemplateResponse("store/cart.html", {"message": "Cart cleared successfully."})



