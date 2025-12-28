from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from src.database.engine import get_db
from src.commerce.domain.models import Product, Category, Store
from src.commerce.auth.security import get_current_user

router = APIRouter(prefix="/products", tags=["Commerce: Products"])

# =====================================================
# DTOs (Data Transfer Objects)
# =====================================================

class ProductCreate(BaseModel):
    category_id: int
    name: str
    price: int
    description: Optional[str] = None
    image_url: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None

class ProductResponse(BaseModel):
    id: int
    category_id: int
    name: str
    price: int
    description: Optional[str]
    image_url: Optional[str]
    is_soldout: bool

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    store_id: int
    name: str
    display_order: Optional[int] = 0

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    display_order: Optional[int] = None

class CategoryResponse(BaseModel):
    id: int
    store_id: int
    name: str
    display_order: int

    class Config:
        from_attributes = True

class CategoryReorder(BaseModel):
    category_ids: List[int]  # Ordered list of category IDs

# =====================================================
# Product Endpoints
# =====================================================

@router.post("/", response_model=ProductResponse)
def create_product(
    item: ProductCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[상품 등록] 새 상품 추가"""
    if user["role"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only Owners can manage products")

    category = db.get(Category, item.category_id)
    if not category or category.store_id != user["store_id"]:
        raise HTTPException(status_code=400, detail="Invalid Category ID")

    new_product = Product(**item.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """[상품 조회] 단일 상품 상세"""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    item: ProductUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[상품 수정] 상품 정보 업데이트"""
    if user["role"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only Owners can manage products")

    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Verify ownership via category
    category = db.get(Category, product.category_id)
    if category.store_id != user["store_id"]:
        raise HTTPException(status_code=403, detail="Not your store's product")

    # Update fields
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[상품 삭제] 상품 제거"""
    if user["role"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only Owners can manage products")

    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    category = db.get(Category, product.category_id)
    if category.store_id != user["store_id"]:
        raise HTTPException(status_code=403, detail="Not your store's product")

    db.delete(product)
    db.commit()
    return {"status": "deleted", "product_id": product_id}

@router.put("/{product_id}/soldout")
def toggle_soldout(
    product_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[품절 토글] 상품 품절 상태 전환"""
    if user["role"] not in ["owner", "admin", "staff"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_soldout = not product.is_soldout
    db.commit()
    return {"product_id": product_id, "is_soldout": product.is_soldout}

@router.get("/list/{store_id}", response_model=List[ProductResponse])
def get_all_products(store_id: int, include_soldout: bool = True, db: Session = Depends(get_db)):
    """[상품 목록] 매장 전체 상품 (관리용)"""
    query = db.query(Product).join(Category).filter(Category.store_id == store_id)
    if not include_soldout:
        query = query.filter(Product.is_soldout == False)
    return query.all()

@router.get("/menu/{store_id}")
def get_store_menu(store_id: int, db: Session = Depends(get_db)):
    """[POS 메뉴] 키오스크/POS용 전체 메뉴 조회 (품절 제외)"""
    categories = db.query(Category).filter_by(store_id=store_id).order_by(Category.display_order).all()
    result = []
    for cat in categories:
        products = db.query(Product).filter_by(category_id=cat.id, is_soldout=False).all()
        result.append({
            "category_id": cat.id,
            "category_name": cat.name,
            "items": [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": p.price,
                    "description": p.description,
                    "image_url": p.image_url
                }
                for p in products
            ]
        })
    return result

# =====================================================
# Category Endpoints
# =====================================================

@router.post("/categories/", response_model=CategoryResponse)
def create_category(
    item: CategoryCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[카테고리 등록] 새 카테고리 추가"""
    if user["role"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only Owners can manage categories")

    if item.store_id != user["store_id"]:
        raise HTTPException(status_code=403, detail="Not your store")

    new_category = Category(**item.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get("/categories/{store_id}", response_model=List[CategoryResponse])
def get_categories(store_id: int, db: Session = Depends(get_db)):
    """[카테고리 목록] 매장의 모든 카테고리"""
    return db.query(Category).filter_by(store_id=store_id).order_by(Category.display_order).all()

@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    item: CategoryUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[카테고리 수정] 카테고리 정보 업데이트"""
    if user["role"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only Owners can manage categories")

    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.store_id != user["store_id"]:
        raise HTTPException(status_code=403, detail="Not your store's category")

    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category

@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[카테고리 삭제] 카테고리 제거 (상품이 없는 경우만)"""
    if user["role"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only Owners can manage categories")

    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category.store_id != user["store_id"]:
        raise HTTPException(status_code=403, detail="Not your store's category")

    # Check if category has products
    product_count = db.query(Product).filter_by(category_id=category_id).count()
    if product_count > 0:
        raise HTTPException(status_code=400, detail=f"Category has {product_count} products. Remove products first.")

    db.delete(category)
    db.commit()
    return {"status": "deleted", "category_id": category_id}

@router.put("/categories/reorder")
def reorder_categories(
    req: CategoryReorder,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    """[카테고리 순서] 카테고리 표시 순서 변경"""
    if user["role"] not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Only Owners can manage categories")

    for idx, cat_id in enumerate(req.category_ids):
        category = db.get(Category, cat_id)
        if category and category.store_id == user["store_id"]:
            category.display_order = idx

    db.commit()
    return {"status": "reordered", "new_order": req.category_ids}