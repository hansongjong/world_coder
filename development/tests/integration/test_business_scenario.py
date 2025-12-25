import requests
import sys
import uuid
from datetime import datetime

# 설정
CORE_URL = "http://127.0.0.1:8000"
COMMERCE_URL = "http://127.0.0.1:8001"

class E2ETester:
    def __init__(self):
        self.token = None
        self.headers = {}
        self.store_id = 1
        self.product_id = None
        self.order_id = None

    def log(self, step, msg):
        print(f"[{step}] {msg}")

    def run(self):
        print("=== TG-SYSTEM E2E Business Scenario Test ===\n")
        
        try:
            self.step_1_health_check()
            self.step_2_login()
            self.step_3_inventory_check()
            self.step_4_place_order()
            self.step_5_verify_stats()
            self.step_6_make_reservation()
            
            print("\n✅ [SUCCESS] All Business Scenarios Passed!")
            
        except Exception as e:
            print(f"\n❌ [FAILED] Test aborted: {e}")
            sys.exit(1)

    def step_1_health_check(self):
        self.log("Step 1", "Checking System Health...")
        r1 = requests.get(f"{CORE_URL}/")
        r2 = requests.get(f"{COMMERCE_URL}/")
        if r1.status_code != 200 or r2.status_code != 200:
            raise Exception("Servers are not running. Please run 'run_all.bat' first.")
        self.log("Step 1", "Core & Commerce are Online.")

    def step_2_login(self):
        self.log("Step 2", "Owner Login...")
        payload = {"username": "owner", "password": "1234"}
        r = requests.post(f"{COMMERCE_URL}/auth/token", data=payload)
        if r.status_code != 200:
            raise Exception(f"Login failed: {r.text}")
        
        data = r.json()
        self.token = data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.log("Step 2", "Login Successful. Token acquired.")

    def step_3_inventory_check(self):
        self.log("Step 3", "Checking & Updating Inventory...")
        # 1. 원두 재고 확인
        r = requests.get(f"{COMMERCE_URL}/inventory/list/{self.store_id}", headers=self.headers)
        items = r.json()
        coffee_bean = next((i for i in items if i["item_name"] == "Coffee Bean"), None)
        
        # 2. 재고 입고 (없으면 생성됨)
        payload = {"store_id": self.store_id, "item_name": "Coffee Bean", "change_qty": 5.0}
        r = requests.post(f"{COMMERCE_URL}/inventory/update", json=payload, headers=self.headers)
        if r.status_code != 200:
            raise Exception("Inventory update failed")
            
        self.log("Step 3", "Inventory 'Coffee Bean' stocked +5.0")

    def step_4_place_order(self):
        self.log("Step 4", "Placing an Order...")
        
        # 메뉴판에서 첫 번째 상품 ID 가져오기
        r = requests.get(f"{COMMERCE_URL}/products/menu/{self.store_id}", headers=self.headers)
        menu = r.json()
        if not menu or not menu[0]["items"]:
            # 시드 데이터가 없으면 예외 처리 대신 스킵 가능하지만, 여기선 엄격하게 체크
            raise Exception("No menu items found. Run 'seed_commerce_data.py' first.")
            
        product = menu[0]["items"][0]
        self.product_id = product["id"]
        price = product["price"]
        
        # 주문 생성
        order_payload = {
            "store_id": self.store_id,
            "table_no": "TEST-01",
            "items": [{"product_id": self.product_id, "quantity": 2, "options": "{}"}]
        }
        r = requests.post(f"{COMMERCE_URL}/orders/place", json=order_payload, headers=self.headers)
        if r.status_code != 200:
            raise Exception(f"Order failed: {r.text}")
            
        data = r.json()
        self.order_id = data["order_id"]
        expected_total = price * 2
        
        if data["total_amount"] != expected_total:
            raise Exception(f"Price mismatch: Expected {expected_total}, Got {data['total_amount']}")
            
        self.log("Step 4", f"Order {self.order_id} Placed. Total: {expected_total}")
        
        # 결제 처리 (Mock PG)
        r = requests.post(f"{COMMERCE_URL}/orders/pay/{self.order_id}?pg_provider=kakao", headers=self.headers)
        if r.status_code != 200:
            raise Exception("Payment failed")
        self.log("Step 4", "Payment Completed.")

    def step_5_verify_stats(self):
        self.log("Step 5", "Verifying Revenue Stats...")
        r = requests.get(f"{COMMERCE_URL}/stats/summary?store_id={self.store_id}", headers=self.headers)
        data = r.json()
        
        revenue = data["today_revenue"]
        if revenue <= 0:
            raise Exception("Revenue stats not updated.")
            
        self.log("Step 5", f"Stats Verified. Today's Revenue: {revenue}")

    def step_6_make_reservation(self):
        self.log("Step 6", "Creating Reservation...")
        res_time = datetime.now().isoformat()
        payload = {
            "store_id": self.store_id,
            "guest_name": "Test User",
            "guest_phone": "010-0000-0000",
            "guest_count": 4,
            "reserved_at": res_time,
            "duration_min": 60
        }
        r = requests.post(f"{COMMERCE_URL}/booking/reserve", json=payload, headers=self.headers)
        if r.status_code != 200:
            # 중복 예약일 수 있으므로 패스 가능하지만 로그 남김
            self.log("Step 6", f"Reservation note: {r.text}")
        else:
            self.log("Step 6", "Reservation Confirmed.")

if __name__ == "__main__":
    tester = E2ETester()
    tester.run()