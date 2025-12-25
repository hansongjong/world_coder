import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DIRS = [
    "src/commerce",
    "src/commerce/domain",  # DB Models (Store, Product, Order)
    "src/commerce/auth",    # JWT & Role Management
    "src/commerce/api",     # POS/Kiosk APIs
    "src/commerce/engine",  # Order & Payment Processing Logic
]

def init_commerce():
    print("[*] Initializing Phase 1: Core & Pay Architecture...")
    for d in DIRS:
        path = BASE_DIR / d
        path.mkdir(parents=True, exist_ok=True)
        print(f"    [DIR] {d}")
    
    # Init files
    for d in DIRS:
        init_file = BASE_DIR / d / "__init__.py"
        if not init_file.exists():
            with open(init_file, "w") as f:
                f.write("")

    print("[SUCCESS] Phase 1 Structure Ready.")

if __name__ == "__main__":
    init_commerce()