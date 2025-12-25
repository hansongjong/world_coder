import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# TG-SYSTEM 엔터프라이즈 구조
DIRS = [
    "src",
    "src/core",                 # 시스템 핵심 설정, 보안, 유틸리티
    "src/database",             # Master DB V3 모델 및 마이그레이션
    "src/services",             # 개별 서비스 모듈 (Bot, Crawler, Manager 등)
    "src/services/catalog",     # 서비스 카탈로그 (Service List Dictionary)
    "src/services/deployment",  # 배포/실행 관리자 (Service-Deployment Mapper)
    "src/erp",                  # ERP 및 결제 모듈
    "src/legal",                # 법적 증빙 및 로그 보관
    "src/api",                  # 대시보드 및 외부 연동 API
    "scripts",                  # 유지보수 스크립트
    "config",                   # 환경 설정 파일
    "logs",                     # 시스템 로그
    "tests"
]

FILES = {
    "src/__init__.py": "",
    "src/core/__init__.py": "",
    "src/database/__init__.py": "",
    "src/services/__init__.py": "",
    "config/.env.template": """# TG-SYSTEM MASTER CONFIG
# Database
DB_URL=sqlite:///./tg_master_v3.db

# Security
SECRET_KEY=system_master_key_change_this
ALGORITHM=HS256

# Telegram Global Config (If needed for master controller)
TG_API_ID=
TG_API_HASH=

# System
DEBUG=True
LOG_LEVEL=INFO
""",
    "requirements.txt": """fastapi>=0.100.0
uvicorn>=0.22.0
sqlalchemy>=2.0.0
alembic>=1.11.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
loguru>=0.7.0
aiofiles>=23.0.0
"""
}

def init_system():
    print(f"[*] Initializing TG-SYSTEM Enterprise Architecture in: {BASE_DIR}")
    
    for d in DIRS:
        path = BASE_DIR / d
        path.mkdir(parents=True, exist_ok=True)
        print(f"    [DIR]  {d}")

    for f, content in FILES.items():
        path = BASE_DIR / f
        if not path.exists():
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)
            print(f"    [FILE] {f}")
        else:
            print(f"    [SKIP] {f} (Exists)")

    print("\n[SUCCESS] TG-SYSTEM Structure Ready.")
    print("Next Step: Implement Master DB Schema based on V3 Design.")

if __name__ == "__main__":
    init_system()