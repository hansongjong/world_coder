from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.engine import get_db
from src.commerce.domain.models_gap_v2 import InventoryItem
from src.commerce.domain.models import ProductRecipe
from src.commerce.services.webhook_sender import webhook_sender
from src.commerce.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Commerce: Inventory (SCM)"])

class StockUpdate(BaseModel):
    store_id: int
    item_name: str
    change_qty: float # +입고, -사용

@router.post("/update")
async def update_stock(
    req: StockUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """[SCM] 재고 수량 변경 (입고/사용)"""
    item = db.query(InventoryItem).filter_by(store_id=req.store_id, item_name=req.item_name).first()

    if not item:
        # 신규 자재 등록
        item = InventoryItem(
            store_id=req.store_id,
            item_name=req.item_name,
            current_qty=0.0,
            unit="ea",
            last_updated=datetime.now()
        )
        db.add(item)

    item.current_qty += req.change_qty
    item.last_updated = datetime.now()
    db.commit()

    # 안전재고 체크 및 STOCK_LOW 이벤트 발송
    alert = False
    if item.current_qty < item.safety_stock:
        alert = True
        # TgMain에 STOCK_LOW Webhook 발송 (백그라운드)
        background_tasks.add_task(
            webhook_sender.send_stock_low,
            store_id=req.store_id,
            item_code=f"INV{item.id:05d}",
            item_name=item.item_name,
            current_qty=int(item.current_qty),
            min_qty=int(item.safety_stock)
        )

    return {
        "item": item.item_name,
        "current_qty": item.current_qty,
        "low_stock_alert": alert
    }

@router.get("/list/{store_id}")
def get_inventory_list(store_id: int, db: Session = Depends(get_db)):
    """[SCM] 전체 재고 현황"""
    items = db.query(InventoryItem).filter_by(store_id=store_id).all()
    return [
        {
            "id": item.id,
            "item_name": item.item_name,
            "current_qty": item.current_qty,
            "safety_stock": item.safety_stock,
            "unit": item.unit,
            "low_stock": item.current_qty < item.safety_stock,
            "last_updated": str(item.last_updated) if item.last_updated else None
        }
        for item in items
    ]


# =====================================================
# Recipe (BOM) Management
# =====================================================

class RecipeCreate(BaseModel):
    product_id: int
    inventory_item_id: int
    quantity_required: float
    unit: str = "ea"


@router.get("/recipe/{product_id}")
def get_product_recipe(product_id: int, db: Session = Depends(get_db)):
    """[BOM] 제품 레시피 조회"""
    inv_service = InventoryService(db)
    return inv_service.get_recipe(product_id)


@router.post("/recipe")
def set_product_recipe(req: RecipeCreate, db: Session = Depends(get_db)):
    """[BOM] 제품 레시피 설정 (UPSERT)"""
    inv_service = InventoryService(db)
    recipe = inv_service.set_recipe(
        product_id=req.product_id,
        inventory_item_id=req.inventory_item_id,
        quantity=req.quantity_required,
        unit=req.unit
    )
    return {
        "success": True,
        "recipe_id": recipe.id,
        "message": "Recipe saved"
    }


@router.delete("/recipe/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """[BOM] 레시피 삭제"""
    inv_service = InventoryService(db)
    success = inv_service.delete_recipe(recipe_id)
    if not success:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return {"success": True, "message": "Recipe deleted"}