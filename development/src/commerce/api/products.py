from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from src.database.engine import get_db
from src.commerce.domain.models import Product, Category, Store
from src.commerce.auth.security import get_current_user

router = APIRouter(prefix="/products", tags=["Commerce: Products"])

# DTO
class ProductCreate(BaseModel):
    category_id: int
    name: str
    price: int
    description: Optional[str] = None

class ProductResponse(ProductCreate):
    id: int
    is_soldout: bool

@router.post("/", response_model=ProductResponse)
def create_product(
    item: ProductCreate, 
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    # 권한 체크: 점주만 상품 등록 가능
    if user["role"] != "owner":
        raise HTTPException(status_code=403, detail="Only Owners can manage products")
    
    # 카테고리 검증 (내 매장의 카테고리인지)
    category = db.get(Category, item.category_id)
    if not category or category.store_id != user["store_id"]:
        raise HTTPException(status_code=400, detail="Invalid Category ID")
        
    new_product = Product(**item.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/menu/{store_id}")
def get_store_menu(store_id: int, db: Session = Depends(get_db)):
    """POS/키오스크용 전체 메뉴 조회 API"""
    categories = db.query(Category).filter_by(store_id=store_id).order_by(Category.display_order).all()
    result = []
    for cat in categories:
        products = db.query(Product).filter_by(category_id=cat.id, is_soldout=False).all()
        result.append({
            "category_name": cat.name,
            "items": products
        })
    return result