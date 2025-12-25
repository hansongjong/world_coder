from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.database.models import Base

# 엔진 생성 (SQLite 기준, 운영 시 PostgreSQL로 변경 가능)
engine = create_engine(
    settings.DB_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DB_URL else {}
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """데이터베이스 테이블 생성"""
    print(f"[*] Connecting to Database: {settings.DB_URL}")
    Base.metadata.create_all(bind=engine)
    print("[*] Database Schema Created Successfully.")

def get_db():
    """Dependency Injection용 DB 세션 제너레이터"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()