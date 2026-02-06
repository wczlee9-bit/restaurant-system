from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    real_name = Column(String(100))
    phone = Column(String(20))
    email = Column(String(100))
    role = Column(String(20), nullable=False)  # admin, manager, chef, waiter, cashier
    is_active = Column(Boolean, default=True)
    points = Column(Integer, default=0)  # 会员积分
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    orders = relationship("Order", back_populates="user")

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(Text)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    tables = relationship("Table", back_populates="store")
    menu_items = relationship("MenuItem", back_populates="store")
    orders = relationship("Order", back_populates="store")

class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    table_number = Column(String(20), nullable=False)
    capacity = Column(Integer, default=4)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    store = relationship("Store", back_populates="tables")
    orders = relationship("Order", back_populates="table")

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    name = Column(String(100), nullable=False)
    category = Column(String(50))  # 菜品分类
    description = Column(Text)
    price = Column(Float, nullable=False)
    image_url = Column(String(500))
    stock = Column(Integer, default=999)
    low_stock_threshold = Column(Integer, default=10)  # 低库存阈值
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    store = relationship("Store", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")

    # 添加约束
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_positive'),
        CheckConstraint('stock >= 0', name='check_stock_positive'),
    )

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default='pending')  # pending, confirmed, preparing, ready, serving, completed, cancelled
    payment_status = Column(String(20), nullable=False, default='unpaid')  # unpaid, paid, refunded
    special_requirements = Column(Text)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    store = relationship("Store", back_populates="orders")
    table = relationship("Table", back_populates="orders")
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order")

    # 添加约束
    __table_args__ = (
        CheckConstraint('total_amount >= 0', name='check_total_amount_positive'),
    )

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # 单价
    subtotal = Column(Float, nullable=False)  # 小计
    special_instructions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")

    # 添加约束
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('price >= 0', name='check_item_price_positive'),
        CheckConstraint('subtotal >= 0', name='check_subtotal_positive'),
    )
