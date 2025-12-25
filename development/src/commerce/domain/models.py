from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from src.core.database.v3_schema import Base  # 기존 Base 재사용

# --- Enums ---
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OWNER = "owner" # 점주
    STAFF = "staff" # 직원

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
    role = Column(String(20), default=UserRole.STAFF)
    store_id = Column(Integer, ForeignKey('com_stores.id'), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    store = relationship("Store", back_populates="staff")

# --- 2. Product & Store (상품/매장) ---
class Store(Base):
    __tablename__ = 'com_stores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    address = Column(String(255))
    biz_number = Column(String(20)) # 사업자 번호
    is_active = Column(Boolean, default=True)
    
    staff = relationship("CommerceUser", back_populates="store")
    categories = relationship("Category", back_populates="store")
    orders = relationship("Order", back_populates="store")

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
    
    id = Column(String(50), primary_key=True) # UUID (Order Number)
    store_id = Column(Integer, ForeignKey('com_stores.id'))
    table_no = Column(String(10), nullable=True) # 키오스크/테이블 번호
    total_amount = Column(Integer)
    status = Column(String(20), default=OrderStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
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
    
    id = Column(String(50), primary_key=True) # Transaction ID
    order_id = Column(String(50), ForeignKey('com_orders.id'))
    pg_provider = Column(String(20)) # kakao, toss, naver
    amount = Column(Integer)
    status = Column(String(20)) # PAID, REFUNDED
    paid_at = Column(DateTime(timezone=True), server_default=func.now())
    
    order = relationship("Order", back_populates="payment")