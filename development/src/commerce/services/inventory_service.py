"""
InventoryService - 재고 자동 차감 서비스
"""
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from src.commerce.domain.models import ProductRecipe
from src.commerce.domain.models_gap_v2 import InventoryItem
from src.commerce.services.webhook_sender import webhook_sender

logger = logging.getLogger(__name__)


class InventoryService:
    """재고 관리 서비스"""

    def __init__(self, db: Session):
        self.db = db

    def deduct_inventory_for_order(
        self,
        store_id: int,
        order_items: List[dict]
    ) -> dict:
        """
        주문 품목에 따라 재고 자동 차감

        Args:
            store_id: 매장 ID
            order_items: [{"product_id": 1, "quantity": 2}, ...]

        Returns:
            {"success": bool, "deducted": [...], "alerts": [...]}
        """
        deducted = []
        alerts = []

        for item in order_items:
            product_id = item.get("product_id")
            order_qty = item.get("quantity", 1)

            # 해당 제품의 레시피(BOM) 조회
            recipes = self.db.query(ProductRecipe).filter(
                ProductRecipe.product_id == product_id
            ).all()

            if not recipes:
                # 레시피가 없으면 스킵 (원재료 매핑 안됨)
                continue

            for recipe in recipes:
                # 필요 수량 계산
                required_qty = recipe.quantity_required * order_qty

                # 재고 조회
                inv_item = self.db.get(InventoryItem, recipe.inventory_item_id)
                if not inv_item:
                    logger.warning(f"Inventory item {recipe.inventory_item_id} not found")
                    continue

                # 재고 차감
                prev_qty = inv_item.current_qty
                inv_item.current_qty -= required_qty
                inv_item.last_updated = datetime.now()

                deducted.append({
                    "item_id": inv_item.id,
                    "item_name": inv_item.item_name,
                    "prev_qty": prev_qty,
                    "deducted": required_qty,
                    "new_qty": inv_item.current_qty
                })

                # 안전재고 미달 체크
                if inv_item.current_qty < inv_item.safety_stock:
                    alerts.append({
                        "item_id": inv_item.id,
                        "item_name": inv_item.item_name,
                        "current_qty": inv_item.current_qty,
                        "safety_stock": inv_item.safety_stock
                    })

        self.db.commit()

        return {
            "success": True,
            "deducted": deducted,
            "alerts": alerts
        }

    async def deduct_and_notify(
        self,
        store_id: int,
        order_items: List[dict]
    ) -> dict:
        """
        재고 차감 후 안전재고 미달 시 Webhook 발송

        Args:
            store_id: 매장 ID
            order_items: [{"product_id": 1, "quantity": 2}, ...]
        """
        result = self.deduct_inventory_for_order(store_id, order_items)

        # 안전재고 미달 항목에 대해 STOCK_LOW 이벤트 발송
        for alert in result.get("alerts", []):
            await webhook_sender.send_stock_low(
                store_id=store_id,
                item_code=f"INV{alert['item_id']:05d}",
                item_name=alert["item_name"],
                current_qty=int(alert["current_qty"]),
                min_qty=int(alert["safety_stock"])
            )
            logger.info(f"STOCK_LOW alert sent: {alert['item_name']}")

        return result

    def get_recipe(self, product_id: int) -> List[dict]:
        """제품의 레시피(BOM) 조회"""
        recipes = self.db.query(ProductRecipe).filter(
            ProductRecipe.product_id == product_id
        ).all()

        result = []
        for r in recipes:
            inv_item = self.db.get(InventoryItem, r.inventory_item_id)
            result.append({
                "recipe_id": r.id,
                "inventory_item_id": r.inventory_item_id,
                "item_name": inv_item.item_name if inv_item else "Unknown",
                "quantity_required": r.quantity_required,
                "unit": r.unit
            })
        return result

    def set_recipe(
        self,
        product_id: int,
        inventory_item_id: int,
        quantity: float,
        unit: str = "ea"
    ) -> ProductRecipe:
        """레시피 설정 (UPSERT)"""
        recipe = self.db.query(ProductRecipe).filter(
            ProductRecipe.product_id == product_id,
            ProductRecipe.inventory_item_id == inventory_item_id
        ).first()

        if recipe:
            recipe.quantity_required = quantity
            recipe.unit = unit
        else:
            recipe = ProductRecipe(
                product_id=product_id,
                inventory_item_id=inventory_item_id,
                quantity_required=quantity,
                unit=unit
            )
            self.db.add(recipe)

        self.db.commit()
        return recipe

    def delete_recipe(self, recipe_id: int) -> bool:
        """레시피 삭제"""
        recipe = self.db.get(ProductRecipe, recipe_id)
        if recipe:
            self.db.delete(recipe)
            self.db.commit()
            return True
        return False
