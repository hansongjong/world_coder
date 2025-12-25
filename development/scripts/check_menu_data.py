import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from sqlalchemy.orm import Session
from src.database.engine import engine
from src.commerce.domain.models import Product, Category

def check_data():
    session = Session(engine)
    try:
        categories = session.query(Category).all()
        products = session.query(Product).all()
        
        print(f"\n=== MENU DATA CHECK ===")
        print(f"Total Categories: {len(categories)}")
        print(f"Total Products:   {len(products)}")
        print("-" * 30)
        
        if not products:
            print("❌ NO DATA FOUND! (DB is empty)")
        else:
            for cat in categories:
                count = session.query(Product).filter_by(category_id=cat.id).count()
                print(f"[{cat.name}]: {count} items")
            print("\n✅ Data exists in DB.")
            
    finally:
        session.close()

if __name__ == "__main__":
    check_data()