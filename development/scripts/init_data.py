import sys
import os
# 프로젝트 루트를 path에 추가하여 모듈 import 가능하게 함
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from src.database.engine import engine, init_db
from src.database.models import User, ServiceCatalog

def seed_data():
    print("[*] Seeding Initial Data...")
    init_db() # 테이블 생성 확인
    
    with Session(engine) as db:
        # 1. Create Admin User
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(username="admin", email="admin@tg-system.com", role="admin")
            db.add(admin)
            print("    [CREATED] User: admin")
        
        # 2. Create Default Services
        services = [
            {
                "code": "TG_SENDER_BASIC",
                "name": "TG Message Sender (Basic)",
                "desc": "Standard text message broadcaster for marketing.",
                "price": 50000,
                "config": {"target_list": "file_path", "msg_delay": 5}
            },
            {
                "code": "TG_GROUP_SCRAPER",
                "name": "TG Group User Scraper",
                "desc": "Extract user info from public groups.",
                "price": 30000,
                "config": {"group_url": "string", "limit": 1000}
            }
        ]
        
        for svc in services:
            exists = db.query(ServiceCatalog).filter(ServiceCatalog.service_code == svc["code"]).first()
            if not exists:
                new_svc = ServiceCatalog(
                    service_code=svc["code"],
                    service_name=svc["name"],
                    description=svc["desc"],
                    base_price=svc["price"],
                    config_schema=svc["config"]
                )
                db.add(new_svc)
                print(f"    [CREATED] Service: {svc['name']}")
        
        db.commit()
    print("[SUCCESS] Data Seeding Complete.")

if __name__ == "__main__":
    seed_data()