import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session
from src.database.engine import engine
from src.core.database.v3_schema import FunctionCatalog

def update_catalog():
    session = Session(engine)
    new_functions = [
        {
            "code": "FN_GROUP_SCRAPER_V1",
            "name": "TG Group User Scraper",
            "handler": "src.handlers.tg_scraper.ScraperFunction",
            "spec": {"timeout": 120, "type": "data_mining"}
        },
        {
            "code": "FN_CHANNEL_JOINER_V1",
            "name": "TG Auto Joiner",
            "handler": "src.handlers.tg_joiner.JoinerFunction",
            "spec": {"timeout": 300, "type": "marketing"}
        }
    ]
    
    try:
        for fn in new_functions:
            existing = session.query(FunctionCatalog).filter_by(function_code=fn["code"]).first()
            if not existing:
                new_fn = FunctionCatalog(
                    function_code=fn["code"],
                    function_name=fn["name"],
                    handler_path=fn["handler"],
                    resource_spec=fn["spec"],
                    is_active=True
                )
                session.add(new_fn)
                print(f"[+] Added to Catalog: {fn['name']}")
        session.commit()
        print("[SUCCESS] Catalog Updated.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        session.close()

if __name__ == "__main__":
    update_catalog()