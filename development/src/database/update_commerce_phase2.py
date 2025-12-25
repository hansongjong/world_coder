import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.database.engine import engine
from src.commerce.domain.models_phase2 import Reservation, IoTDevice

def update_commerce_phase2():
    print("[*] Applying Commerce Phase 2 Schema (Booking & IoT)...")
    try:
        Reservation.__table__.create(bind=engine, checkfirst=True)
        IoTDevice.__table__.create(bind=engine, checkfirst=True)
        print("[SUCCESS] Phase 2 Tables Created.")
    except Exception as e:
        print(f"[ERROR] Failed to update schema: {e}")

if __name__ == "__main__":
    update_commerce_phase2()