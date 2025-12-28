from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.database.engine import get_db
from src.commerce.domain.models_gap_v2 import InventoryItem
from src.commerce.services.webhook_sender import webhook_sender

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
    return db.query(InventoryItem).filter_by(store_id=store_id).all()