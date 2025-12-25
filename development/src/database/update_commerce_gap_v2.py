import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.database.engine import engine
from src.commerce.domain.models_gap_v2 import DeliveryCall, MemberPoint, PointHistory, InventoryItem

def update_commerce_gaps_v2():
    print("[*] Applying GAP V2 Schema (Delivery, Point, Inventory)...")
    try:
        DeliveryCall.__table__.create(bind=engine, checkfirst=True)
        MemberPoint.__table__.create(bind=engine, checkfirst=True)
        PointHistory.__table__.create(bind=engine, checkfirst=True)
        InventoryItem.__table__.create(bind=engine, checkfirst=True)
        print("[SUCCESS] Phase 2.5 Extra Tables Created.")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    update_commerce_gaps_v2()