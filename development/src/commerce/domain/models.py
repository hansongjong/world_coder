from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from src.core.database.v3_schema import Base  # 기존 Base 재사용

# --- Enums ---
class UserRole(str, enum.Enum):
    ADMIN = "admin"      # 시스템 관리자
    OWNER = "owner"      # 점주 (매장 소유자)
    MANAGER = "manager"  # 매니저 (일부 관리 권한)
    STAFF = "staff"      # 직원 (주문/결제만)

class OrderStatus(str, enum.Enum):
    PENDING = "pending"   # 주문 접수 중
    PAID = "paid"         # 결제 완료
    PREPARING = "preparing" # 제조 중
    READY = "ready"       # 픽업 대기
    COMPLETED = "completed" # 완료
    CANCELED = "canceled" # 취소

# --- 1. Auth & Member (인증/회원) ---
class CommerceUser(Base):
    __tablename__ = 'com_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 다대다 관계: 한 유저가 여러 매장에 접근 가능
    store_accesses = relationship("UserStoreAccess", back_populates="user")


# --- User-Store Access (다대다 연결 + Role) ---
class UserStoreAccess(Base):
    """유저-매장 연결 테이블 (다대다 + 역할)"""
    __tablename__ = 'com_user_store_access'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('com_users.id'), nullable=False)
    store_id = Column(Integer, ForeignKey('com_stores.id'), nullable=False)
    role = Column(String(20), default=UserRole.STAFF)  # OWNER, MANAGER, STAFF

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, nullable=True)  # 누가 이 권한을 부여했는지

    user = relationship("CommerceUser", back_populates="store_accesses")
    store = relationship("Store", back_populates="user_accesses")

# --- Business Types ---
class BizType(str, enum.Enum):
    CAFE = "cafe"
    RESTAURANT = "restaurant"
    RETAIL = "retail"
    BEAUTY = "beauty"
    GYM = "gym"
    HOSPITAL = "hospital"
    OTHER = "other"

# --- 2. Product & Store (상품/매장) ---
class Store(Base):
    __tablename__ = 'com_stores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    address = Column(String(255))
    biz_number = Column(String(20)) # 사업자 번호
    biz_type = Column(String(20), default=BizType.CAFE)  # Business type
    is_active = Column(Boolean, default=True)

    user_accesses = relationship("UserStoreAccess", back_populates="store")
    categories = relationship("Category", back_populates="store")
    orders = relationship("Order", back_populates="store")
    config = relationship("StoreConfig", uselist=False, back_populates="store")

# --- Store Configuration (Module Picking) ---
class StoreConfig(Base):
    __tablename__ = 'com_store_configs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey('com_stores.id'), unique=True)

    # Module flags
    mod_payment = Column(Boolean, default=True)
    mod_queue = Column(Boolean, default=False)
    mod_reservation = Column(Boolean, default=False)
    mod_inventory = Column(Boolean, default=False)
    mod_crm = Column(Boolean, default=False)
    mod_delivery = Column(Boolean, default=False)
    mod_iot = Column(Boolean, default=False)
    mod_subscription = Column(Boolean, default=False)
    mod_invoice = Column(Boolean, default=False)

    # UI Settings
    ui_mode = Column(String(30), default="KIOSK_LITE")  # KIOSK_LITE, TABLE_MANAGER, ADMIN_DASHBOARD
    table_count = Column(Integer, default=0)
    deposit_amount = Column(Integer, default=0)

    # JSON for additional settings
    extra_settings = Column(Text, nullable=True)  # JSON string

    store = relationship("Store", back_populates="config")

class Category(Base):
    __tablename__ = 'com_categories'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey('com_stores.id'))
    name = Column(String(50))
    display_order = Column(Integer, default=0)
    
    store = relationship("Store", back_populates="categories")
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = 'com_products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('com_categories.id'))
    name = Column(String(100))
    price = Column(Integer)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    is_soldout = Column(Boolean, default=False)
    
    category = relationship("Category", back_populates="products")

# --- 3. Order & Payment (주문/결제) ---
class Order(Base):
    __tablename__ = 'com_orders'

    id = Column(String(50), primary_key=True)  # UUID (Order Number)
    store_id = Column(Integer, ForeignKey('com_stores.id'))
    table_no = Column(String(10), nullable=True)  # 키오스크/테이블 번호
    total_amount = Column(Integer)
    status = Column(String(20), default=OrderStatus.PENDING)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey('com_users.id'), nullable=True)  # 주문 생성한 직원
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)  # 마지막 수정한 직원

    store = relationship("Store", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payment = relationship("Payment", uselist=False, back_populates="order")

class OrderItem(Base):
    __tablename__ = 'com_order_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(50), ForeignKey('com_orders.id'))
    product_name = Column(String(100)) # 상품명 스냅샷 (가격 변동 대비)
    unit_price = Column(Integer)
    quantity = Column(Integer)
    options = Column(Text, nullable=True) # JSON String for options (e.g., {"size": "L", "ice": "Hot"})
    
    order = relationship("Order", back_populates="items")

class Payment(Base):
    __tablename__ = 'com_payments'

    id = Column(String(50), primary_key=True)  # Transaction ID
    order_id = Column(String(50), ForeignKey('com_orders.id'))
    pg_provider = Column(String(20))  # kakao, toss, naver, card, cash
    amount = Column(Integer)
    status = Column(String(20))  # PAID, REFUNDED

    # Audit fields
    paid_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_by = Column(Integer, ForeignKey('com_users.id'), nullable=True)  # 결제 처리한 직원

    order = relationship("Order", back_populates="payment")


# --- 4. TgMain Integration (연동) ---
class ExpectedDeliveryStatus(str, enum.Enum):
    PENDING = "pending"       # 입고 대기
    RECEIVED = "received"     # 입고 완료
    PARTIAL = "partial"       # 부분 입고
    CANCELLED = "cancelled"   # 취소됨


class ExpectedDelivery(Base):
    """입고 예정 (TgMain 발주서 수신)"""
    __tablename__ = 'expected_deliveries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey('com_stores.id'), nullable=False)
    po_number = Column(String(50), unique=True, index=True)  # TgMain 발주번호
    vendor_id = Column(Integer, nullable=True)
    vendor_name = Column(String(100))
    expected_date = Column(DateTime, nullable=True)
    status = Column(String(20), default=ExpectedDeliveryStatus.PENDING)
    total_amount = Column(Integer, default=0)
    notes = Column(Text, nullable=True)

    received_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    items = relationship("ExpectedDeliveryItem", back_populates="delivery")


class ExpectedDeliveryItem(Base):
    """입고 예정 품목"""
    __tablename__ = 'expected_delivery_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    delivery_id = Column(Integer, ForeignKey('expected_deliveries.id'), nullable=False)
    item_code = Column(String(50))
    item_name = Column(String(100))
    quantity = Column(Integer, default=0)
    unit = Column(String(10), default="EA")
    unit_price = Column(Integer, default=0)
    received_qty = Column(Integer, default=0)

    delivery = relationship("ExpectedDelivery", back_populates="items")


class SyncDirection(str, enum.Enum):
    INBOUND = "IN"    # TgMain → World
    OUTBOUND = "OUT"  # World → TgMain


class SyncLog(Base):
    """연동 로그 (Idempotency 포함)"""
    __tablename__ = 'sync_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    idempotency_key = Column(String(100), unique=True, index=True)
    direction = Column(String(10))  # IN, OUT
    event_type = Column(String(50))  # ORDER_PAID, STOCK_LOW, PURCHASE_ORDER 등
    endpoint = Column(String(255), nullable=True)
    payload = Column(Text, nullable=True)  # JSON string
    response = Column(Text, nullable=True)  # JSON string
    status = Column(String(20), default="PENDING")  # PENDING, SUCCESS, FAILED, RETRYING
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime, nullable=True)


class Vendor(Base):
    """거래처 (TgMain에서 동기화)"""
    __tablename__ = 'vendors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey('com_stores.id'), nullable=False)
    external_id = Column(Integer, nullable=True)  # TgMain vendor_id
    name = Column(String(100), nullable=False)
    contact_name = Column(String(50), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# --- 5. BOM (Bill of Materials - 제품-원재료 매핑) ---
class ProductRecipe(Base):
    """
    제품 레시피 (BOM)
    예: 아메리카노 1잔 = 원두 20g + 물 200ml
    """
    __tablename__ = 'product_recipes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('com_products.id'), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey('com_inventory.id'), nullable=False)
    quantity_required = Column(Float, default=1.0)  # 필요 수량
    unit = Column(String(10), default="ea")  # 단위

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product")