from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String, Text, JSON, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional

class Base(DeclarativeBase):
    pass

# ============ 用户与权限模块 ============

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True, nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码（加密）")
    email = Column(String(255), unique=True, nullable=True, comment="邮箱")
    phone = Column(String(20), nullable=True, comment="手机号")
    name = Column(String(128), nullable=False, comment="真实姓名")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    roles = relationship("UserRole", back_populates="user")
    staff_records = relationship("Staff", back_populates="user")
    order_logs = relationship("OrderStatusLog", back_populates="operator")
    inventory_logs = relationship("InventoryLog", back_populates="operator")
    purchase_orders = relationship("PurchaseOrder", foreign_keys="PurchaseOrder.created_by", back_populates="creator")
    
    __table_args__ = (
        Index("ix_users_username", "username"),
        Index("ix_users_email", "email"),
        Index("ix_users_phone", "phone"),
    )

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, comment="角色名称")
    description = Column(String(255), nullable=True, comment="角色描述")
    permissions = Column(JSON, nullable=True, comment="权限列表")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    user_roles = relationship("UserRole", back_populates="role")

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")

# ============ 店铺管理模块 ============

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, comment="公司名称")
    contact_person = Column(String(128), nullable=True, comment="联系人")
    contact_phone = Column(String(20), nullable=True, comment="联系电话")
    address = Column(Text, nullable=True, comment="地址")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    stores = relationship("Store", back_populates="company")

class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, comment="所属公司ID")
    name = Column(String(255), nullable=False, comment="店铺名称")
    address = Column(Text, nullable=True, comment="店铺地址")
    phone = Column(String(20), nullable=True, comment="联系电话")
    manager_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="店长ID")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    opening_hours = Column(JSON, nullable=True, comment="营业时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    company = relationship("Company", back_populates="stores")
    manager = relationship("User")
    tables = relationship("Table", back_populates="store")
    staff = relationship("Staff", back_populates="store")
    menu_categories = relationship("MenuCategory", back_populates="store")
    menu_items = relationship("MenuItem", back_populates="store")
    orders = relationship("Order", back_populates="store")
    inventory = relationship("Inventory", back_populates="store")
    purchase_orders = relationship("PurchaseOrder", back_populates="store")
    daily_revenues = relationship("DailyRevenue", back_populates="store")

class Table(Base):
    __tablename__ = "tables"
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="店铺ID")
    table_number = Column(String(50), nullable=False, comment="桌号")
    table_name = Column(String(128), nullable=True, comment="桌子名称")
    qrcode_url = Column(String(500), nullable=True, comment="二维码URL（存储在S3）")
    qrcode_content = Column(String(255), nullable=True, comment="二维码内容")
    seats = Column(Integer, nullable=True, comment="座位数")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否可用")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    store = relationship("Store", back_populates="tables")
    orders = relationship("Order", back_populates="table")
    
    __table_args__ = (
        Index("ix_tables_store_table", "store_id", "table_number"),
    )

class Staff(Base):
    __tablename__ = "staff"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="店铺ID")
    position = Column(String(50), nullable=False, comment="职位（厨师、服务员、传菜员等）")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否在职")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    user = relationship("User", back_populates="staff_records")
    store = relationship("Store", back_populates="staff")

# ============ 菜品管理模块 ============

class MenuCategory(Base):
    __tablename__ = "menu_categories"
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="店铺ID")
    name = Column(String(128), nullable=False, comment="分类名称")
    description = Column(Text, nullable=True, comment="分类描述")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否显示")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    store = relationship("Store", back_populates="menu_categories")
    menu_items = relationship("MenuItem", back_populates="category")

class MenuItem(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="店铺ID")
    category_id = Column(Integer, ForeignKey("menu_categories.id", ondelete="SET NULL"), nullable=True, comment="分类ID")
    name = Column(String(255), nullable=False, comment="菜品名称")
    description = Column(Text, nullable=True, comment="菜品描述")
    price = Column(Float, nullable=False, comment="价格")
    original_price = Column(Float, nullable=True, comment="原价")
    image_url = Column(String(500), nullable=True, comment="菜品图片URL（存储在S3）")
    stock = Column(Integer, default=0, nullable=False, comment="库存数量")
    unit = Column(String(20), nullable=True, comment="单位（份、个、斤等）")
    cooking_time = Column(Integer, nullable=True, comment="烹饪时间（分钟）")
    is_available = Column(Boolean, default=True, nullable=False, comment="是否可售")
    is_recommended = Column(Boolean, default=False, nullable=False, comment="是否推荐")
    sort_order = Column(Integer, default=0, nullable=False, comment="排序")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    store = relationship("Store", back_populates="menu_items")
    category = relationship("MenuCategory", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")

# ============ 订单模块 ============

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="店铺ID")
    table_id = Column(Integer, ForeignKey("tables.id", ondelete="SET NULL"), nullable=True, comment="桌号ID")
    order_number = Column(String(50), unique=True, nullable=False, comment="订单号")
    customer_name = Column(String(128), nullable=True, comment="顾客姓名")
    customer_phone = Column(String(20), nullable=True, comment="顾客手机号")
    total_amount = Column(Float, default=0.0, nullable=False, comment="订单总金额")
    discount_amount = Column(Float, default=0.0, nullable=False, comment="折扣金额")
    final_amount = Column(Float, default=0.0, nullable=False, comment="实付金额")
    payment_status = Column(String(50), default="unpaid", nullable=False, comment="支付状态")
    payment_method = Column(String(50), nullable=True, comment="支付方式")
    payment_time = Column(DateTime(timezone=True), nullable=True, comment="支付时间")
    order_status = Column(String(50), default="pending", nullable=False, comment="订单状态")
    special_instructions = Column(Text, nullable=True, comment="特殊要求")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    store = relationship("Store", back_populates="orders")
    table = relationship("Table", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_logs = relationship("OrderStatusLog", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="order", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_orders_order_number", "order_number"),
        Index("ix_orders_store_created", "store_id", "created_at"),
        Index("ix_orders_table", "table_id"),
    )

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, comment="订单ID")
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="SET NULL"), nullable=True, comment="菜品ID")
    menu_item_name = Column(String(255), nullable=False, comment="菜品名称（快照）")
    menu_item_price = Column(Float, nullable=False, comment="菜品价格（快照）")
    quantity = Column(Integer, nullable=False, comment="数量")
    subtotal = Column(Float, nullable=False, comment="小计")
    special_instructions = Column(Text, nullable=True, comment="特殊要求")
    status = Column(String(50), default="pending", nullable=False, comment="状态")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")

class OrderStatusLog(Base):
    __tablename__ = "order_status_logs"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, comment="订单ID")
    from_status = Column(String(50), nullable=True, comment="原状态")
    to_status = Column(String(50), nullable=False, comment="新状态")
    operator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="操作人ID")
    operator_name = Column(String(128), nullable=True, comment="操作人姓名")
    notes = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    order = relationship("Order", back_populates="status_logs")
    operator = relationship("User", back_populates="order_logs")

# ============ 支付模块 ============

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, comment="订单ID")
    payment_method = Column(String(50), nullable=False, comment="支付方式")
    amount = Column(Float, nullable=False, comment="支付金额")
    transaction_id = Column(String(255), nullable=True, comment="交易号")
    payment_time = Column(DateTime(timezone=True), nullable=True, comment="支付时间")
    status = Column(String(50), default="success", nullable=False, comment="支付状态")
    refund_amount = Column(Float, default=0.0, nullable=False, comment="退款金额")
    refund_time = Column(DateTime(timezone=True), nullable=True, comment="退款时间")
    refund_reason = Column(Text, nullable=True, comment="退款原因")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    order = relationship("Order", back_populates="payments")

# ============ 会员管理模块 ============

class Member(Base):
    __tablename__ = "members"
    
    id = Column(Integer, primary_key=True)
    phone = Column(String(20), unique=True, nullable=False, comment="手机号")
    name = Column(String(128), nullable=True, comment="会员姓名")
    avatar_url = Column(String(500), nullable=True, comment="头像URL（存储在S3）")
    level = Column(Integer, default=1, nullable=False, comment="会员等级")
    points = Column(Integer, default=0, nullable=False, comment="积分")
    total_spent = Column(Float, default=0.0, nullable=False, comment="累计消费金额")
    total_orders = Column(Integer, default=0, nullable=False, comment="累计订单数")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    point_logs = relationship("PointLog", back_populates="member")
    
    __table_args__ = (
        Index("ix_members_phone", "phone"),
    )

class MemberLevelRule(Base):
    __tablename__ = "member_level_rules"
    
    id = Column(Integer, primary_key=True)
    level = Column(Integer, unique=True, nullable=False, comment="等级")
    level_name = Column(String(128), nullable=False, comment="等级名称")
    min_points = Column(Integer, default=0, nullable=False, comment="最小积分要求")
    discount = Column(Float, default=1.0, nullable=False, comment="折扣比例")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class PointLog(Base):
    __tablename__ = "point_logs"
    
    id = Column(Integer, primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False, comment="会员ID")
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, comment="订单ID")
    points = Column(Integer, nullable=False, comment="积分变动")
    reason = Column(String(255), nullable=True, comment="变动原因")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    member = relationship("Member", back_populates="point_logs")

# ============ 库存管理模块 ============

class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="店铺ID")
    item_name = Column(String(255), nullable=False, comment="物料名称")
    category = Column(String(128), nullable=True, comment="物料分类")
    unit = Column(String(20), nullable=True, comment="单位")
    quantity = Column(Float, default=0.0, nullable=False, comment="当前库存数量")
    min_stock = Column(Float, nullable=True, comment="最低库存预警")
    max_stock = Column(Float, nullable=True, comment="最大库存")
    cost_price = Column(Float, nullable=True, comment="成本单价")
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, comment="供应商ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    store = relationship("Store", back_populates="inventory")
    supplier = relationship("Supplier")
    logs = relationship("InventoryLog", back_populates="inventory")
    purchase_items = relationship("PurchaseItem", back_populates="inventory")
    
    __table_args__ = (
        Index("ix_inventory_store_item", "store_id", "item_name"),
    )

class InventoryLog(Base):
    __tablename__ = "inventory_logs"
    
    id = Column(Integer, primary_key=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id", ondelete="CASCADE"), nullable=False, comment="库存ID")
    operation_type = Column(String(50), nullable=False, comment="操作类型（in, out, adjust）")
    quantity = Column(Float, nullable=False, comment="变动数量")
    before_quantity = Column(Float, nullable=False, comment="变动前数量")
    after_quantity = Column(Float, nullable=False, comment="变动后数量")
    reason = Column(Text, nullable=True, comment="变动原因")
    operator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="操作人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    inventory = relationship("Inventory", back_populates="logs")
    operator = relationship("User", back_populates="inventory_logs")

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, comment="供应商名称")
    contact_person = Column(String(128), nullable=True, comment="联系人")
    contact_phone = Column(String(20), nullable=True, comment="联系电话")
    address = Column(Text, nullable=True, comment="地址")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="店铺ID")
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, comment="供应商ID")
    order_number = Column(String(50), unique=True, nullable=False, comment="采购单号")
    total_amount = Column(Float, default=0.0, nullable=False, comment="总金额")
    status = Column(String(50), default="pending", nullable=False, comment="状态")
    delivery_date = Column(DateTime(timezone=True), nullable=True, comment="交货日期")
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    store = relationship("Store", back_populates="purchase_orders")
    supplier = relationship("Supplier")
    creator = relationship("User", foreign_keys=[created_by], back_populates="purchase_orders")
    items = relationship("PurchaseItem", back_populates="purchase_order", cascade="all, delete-orphan")

class PurchaseItem(Base):
    __tablename__ = "purchase_items"
    
    id = Column(Integer, primary_key=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, comment="采购订单ID")
    inventory_id = Column(Integer, ForeignKey("inventory.id", ondelete="SET NULL"), nullable=True, comment="库存ID")
    item_name = Column(String(255), nullable=False, comment="物料名称")
    quantity = Column(Float, nullable=False, comment="数量")
    unit_price = Column(Float, nullable=False, comment="单价")
    subtotal = Column(Float, nullable=False, comment="小计")
    received_quantity = Column(Float, default=0.0, nullable=False, comment="已收货数量")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 关系
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    inventory = relationship("Inventory", back_populates="purchase_items")

# ============ 营收统计模块 ============

class DailyRevenue(Base):
    __tablename__ = "daily_revenue"
    
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, comment="店铺ID")
    date = Column(DateTime(timezone=True), nullable=False, comment="日期")
    total_orders = Column(Integer, default=0, nullable=False, comment="总订单数")
    total_amount = Column(Float, default=0.0, nullable=False, comment="总金额")
    total_discount = Column(Float, default=0.0, nullable=False, comment="总折扣金额")
    total_refund = Column(Float, default=0.0, nullable=False, comment="总退款金额")
    net_revenue = Column(Float, default=0.0, nullable=False, comment="净营收")
    payment_methods = Column(JSON, nullable=True, comment="支付方式统计")
    peak_hours = Column(JSON, nullable=True, comment="高峰时段")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # 关系
    store = relationship("Store", back_populates="daily_revenues")
    
    __table_args__ = (
        Index("ix_daily_revenue_store_date", "store_id", "date"),
    )

