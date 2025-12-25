import sys
from pathlib import Path

# 프로젝트 루트 경로 설정
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from src.database.engine import engine
from src.core.database.v3_schema import Base

# [중요] 모든 모델을 Import해야 Base.metadata가 테이블을 인식합니다.
# 1. Core Models
from src.core.database import v3_schema
from src.core.database import v3_extensions
from src.core.database import v3_campaigns  # <-- 에러 원인 해결

# 2. Commerce Models
from src.commerce.domain import models
from src.commerce.domain import models_phase2
from src.commerce.domain import models_gap
from src.commerce.domain import models_gap_v2

def run_auto_migration():
    print("[*] Running Auto-Migration (Creating missing tables)...")
    try:
        # DB 엔진에 연결하여 정의된 모든 테이블 생성
        # checkfirst=True 옵션으로 이미 존재하는 테이블은 건너뜀
        Base.metadata.create_all(bind=engine)
        print("[+] Database Schema is up-to-date.")
        print("    - Core, Commerce, Campaigns, IoT, Booking, ERP tables checked.")
        
    except Exception as e:
        print(f"[!] Migration Failed: {e}")
        # 치명적 오류 시 프로세스 종료
        sys.exit(1)

if __name__ == "__main__":
    run_auto_migration()