import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.database.engine import engine
from src.commerce.domain.models_gap import WaitingTicket, CustomerSurvey, AttendanceLog

def update_commerce_gaps():
    print("[*] Applying Missing Business Logic Schema (Waiting, Survey, HR)...")
    try:
        WaitingTicket.__table__.create(bind=engine, checkfirst=True)
        CustomerSurvey.__table__.create(bind=engine, checkfirst=True)
        AttendanceLog.__table__.create(bind=engine, checkfirst=True)
        print("[SUCCESS] Tables for Waiting, Survey, HR created.")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    update_commerce_gaps()