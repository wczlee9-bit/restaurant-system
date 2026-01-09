from sqlalchemy import Boolean, DateTime, Double, ForeignKeyConstraint, Index, Integer, JSON, PrimaryKeyConstraint, String, Text, UniqueConstraint, text
from typing import Optional
import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Companies(Base):
    __tablename__ = 'companies'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='companies_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='公司名称')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='是否激活')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    contact_person: Mapped[Optional[str]] = mapped_column(String(128), comment='联系人')
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), comment='联系电话')
    address: Mapped[Optional[str]] = mapped_column(Text, comment='地址')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    stores: Mapped[list['Stores']] = relationship('Stores', back_populates='company')


class MemberLevelRules(Base):
    __tablename__ = 'member_level_rules'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='member_level_rules_pkey'),
        UniqueConstraint('level', name='member_level_rules_level_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, comment='等级')
    level_name: Mapped[str] = mapped_column(String(128), nullable=False, comment='等级名称')
    min_points: Mapped[int] = mapped_column(Integer, nullable=False, comment='最小积分要求')
    discount: Mapped[float] = mapped_column(Double(53), nullable=False, comment='折扣比例')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))


class Members(Base):
    __tablename__ = 'members'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='members_pkey'),
        UniqueConstraint('phone', name='members_phone_key'),
        Index('ix_members_phone', 'phone')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, comment='手机号')
    level: Mapped[int] = mapped_column(Integer, nullable=False, comment='会员等级')
    points: Mapped[int] = mapped_column(Integer, nullable=False, comment='积分')
    total_spent: Mapped[float] = mapped_column(Double(53), nullable=False, comment='累计消费金额')
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, comment='累计订单数')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    name: Mapped[Optional[str]] = mapped_column(String(128), comment='会员姓名')
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), comment='头像URL（存储在S3）')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    point_logs: Mapped[list['PointLogs']] = relationship('PointLogs', back_populates='member')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='roles_pkey'),
        UniqueConstraint('name', name='roles_name_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment='角色名称')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(String(255), comment='角色描述')
    permissions: Mapped[Optional[dict]] = mapped_column(JSON, comment='权限列表')

    user_roles: Mapped[list['UserRoles']] = relationship('UserRoles', back_populates='role')


class Suppliers(Base):
    __tablename__ = 'suppliers'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='suppliers_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='供应商名称')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    contact_person: Mapped[Optional[str]] = mapped_column(String(128), comment='联系人')
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), comment='联系电话')
    address: Mapped[Optional[str]] = mapped_column(Text, comment='地址')

    inventory: Mapped[list['Inventory']] = relationship('Inventory', back_populates='supplier')
    purchase_orders: Mapped[list['PurchaseOrders']] = relationship('PurchaseOrders', back_populates='supplier')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='users_pkey'),
        UniqueConstraint('email', name='users_email_key'),
        UniqueConstraint('username', name='users_username_key'),
        Index('ix_users_email', 'email'),
        Index('ix_users_phone', 'phone'),
        Index('ix_users_username', 'username')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(128), nullable=False, comment='用户名')
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment='密码（加密）')
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment='真实姓名')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='是否激活')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    email: Mapped[Optional[str]] = mapped_column(String(255), comment='邮箱')
    phone: Mapped[Optional[str]] = mapped_column(String(20), comment='手机号')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    stores: Mapped[list['Stores']] = relationship('Stores', back_populates='manager')
    user_roles: Mapped[list['UserRoles']] = relationship('UserRoles', back_populates='user')
    purchase_orders: Mapped[list['PurchaseOrders']] = relationship('PurchaseOrders', back_populates='users')
    staff: Mapped[list['Staff']] = relationship('Staff', back_populates='user')
    inventory_logs: Mapped[list['InventoryLogs']] = relationship('InventoryLogs', back_populates='operator')
    order_status_logs: Mapped[list['OrderStatusLogs']] = relationship('OrderStatusLogs', back_populates='operator')


class Stores(Base):
    __tablename__ = 'stores'
    __table_args__ = (
        ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE', name='stores_company_id_fkey'),
        ForeignKeyConstraint(['manager_id'], ['users.id'], ondelete='SET NULL', name='stores_manager_id_fkey'),
        PrimaryKeyConstraint('id', name='stores_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='所属公司ID')
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='店铺名称')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='是否激活')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    address: Mapped[Optional[str]] = mapped_column(Text, comment='店铺地址')
    phone: Mapped[Optional[str]] = mapped_column(String(20), comment='联系电话')
    manager_id: Mapped[Optional[int]] = mapped_column(Integer, comment='店长ID')
    opening_hours: Mapped[Optional[dict]] = mapped_column(JSON, comment='营业时间')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    company: Mapped['Companies'] = relationship('Companies', back_populates='stores')
    manager: Mapped[Optional['Users']] = relationship('Users', back_populates='stores')
    daily_revenue: Mapped[list['DailyRevenue']] = relationship('DailyRevenue', back_populates='store')
    inventory: Mapped[list['Inventory']] = relationship('Inventory', back_populates='store')
    menu_categories: Mapped[list['MenuCategories']] = relationship('MenuCategories', back_populates='store')
    purchase_orders: Mapped[list['PurchaseOrders']] = relationship('PurchaseOrders', back_populates='store')
    staff: Mapped[list['Staff']] = relationship('Staff', back_populates='store')
    tables: Mapped[list['Tables']] = relationship('Tables', back_populates='store')
    menu_items: Mapped[list['MenuItems']] = relationship('MenuItems', back_populates='store')
    orders: Mapped[list['Orders']] = relationship('Orders', back_populates='store')
    role_configs: Mapped[list['RoleConfig']] = relationship('RoleConfig', cascade='all, delete-orphan')
    order_flow_configs: Mapped[list['OrderFlowConfig']] = relationship('OrderFlowConfig', cascade='all, delete-orphan')


class UserRoles(Base):
    __tablename__ = 'user_roles'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE', name='user_roles_role_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='user_roles_user_id_fkey'),
        PrimaryKeyConstraint('id', name='user_roles_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))

    role: Mapped['Roles'] = relationship('Roles', back_populates='user_roles')
    user: Mapped['Users'] = relationship('Users', back_populates='user_roles')


class DailyRevenue(Base):
    __tablename__ = 'daily_revenue'
    __table_args__ = (
        ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE', name='daily_revenue_store_id_fkey'),
        PrimaryKeyConstraint('id', name='daily_revenue_pkey'),
        Index('ix_daily_revenue_store_date', 'store_id', 'date')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='店铺ID')
    date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, comment='日期')
    total_orders: Mapped[int] = mapped_column(Integer, nullable=False, comment='总订单数')
    total_amount: Mapped[float] = mapped_column(Double(53), nullable=False, comment='总金额')
    total_discount: Mapped[float] = mapped_column(Double(53), nullable=False, comment='总折扣金额')
    total_refund: Mapped[float] = mapped_column(Double(53), nullable=False, comment='总退款金额')
    net_revenue: Mapped[float] = mapped_column(Double(53), nullable=False, comment='净营收')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    payment_methods: Mapped[Optional[dict]] = mapped_column(JSON, comment='支付方式统计')
    peak_hours: Mapped[Optional[dict]] = mapped_column(JSON, comment='高峰时段')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    store: Mapped['Stores'] = relationship('Stores', back_populates='daily_revenue')


class Inventory(Base):
    __tablename__ = 'inventory'
    __table_args__ = (
        ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE', name='inventory_store_id_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ondelete='SET NULL', name='inventory_supplier_id_fkey'),
        PrimaryKeyConstraint('id', name='inventory_pkey'),
        Index('ix_inventory_store_item', 'store_id', 'item_name')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='店铺ID')
    item_name: Mapped[str] = mapped_column(String(255), nullable=False, comment='物料名称')
    quantity: Mapped[float] = mapped_column(Double(53), nullable=False, comment='当前库存数量')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    category: Mapped[Optional[str]] = mapped_column(String(128), comment='物料分类')
    unit: Mapped[Optional[str]] = mapped_column(String(20), comment='单位')
    min_stock: Mapped[Optional[float]] = mapped_column(Double(53), comment='最低库存预警')
    max_stock: Mapped[Optional[float]] = mapped_column(Double(53), comment='最大库存')
    cost_price: Mapped[Optional[float]] = mapped_column(Double(53), comment='成本单价')
    supplier_id: Mapped[Optional[int]] = mapped_column(Integer, comment='供应商ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    store: Mapped['Stores'] = relationship('Stores', back_populates='inventory')
    supplier: Mapped[Optional['Suppliers']] = relationship('Suppliers', back_populates='inventory')
    inventory_logs: Mapped[list['InventoryLogs']] = relationship('InventoryLogs', back_populates='inventory')
    purchase_items: Mapped[list['PurchaseItems']] = relationship('PurchaseItems', back_populates='inventory')


class MenuCategories(Base):
    __tablename__ = 'menu_categories'
    __table_args__ = (
        ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE', name='menu_categories_store_id_fkey'),
        PrimaryKeyConstraint('id', name='menu_categories_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='店铺ID')
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment='分类名称')
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, comment='排序')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='是否显示')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text, comment='分类描述')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    store: Mapped['Stores'] = relationship('Stores', back_populates='menu_categories')
    menu_items: Mapped[list['MenuItems']] = relationship('MenuItems', back_populates='category')


class PurchaseOrders(Base):
    __tablename__ = 'purchase_orders'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL', name='purchase_orders_created_by_fkey'),
        ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE', name='purchase_orders_store_id_fkey'),
        ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], ondelete='SET NULL', name='purchase_orders_supplier_id_fkey'),
        PrimaryKeyConstraint('id', name='purchase_orders_pkey'),
        UniqueConstraint('order_number', name='purchase_orders_order_number_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='店铺ID')
    order_number: Mapped[str] = mapped_column(String(50), nullable=False, comment='采购单号')
    total_amount: Mapped[float] = mapped_column(Double(53), nullable=False, comment='总金额')
    status: Mapped[str] = mapped_column(String(50), nullable=False, comment='状态')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    supplier_id: Mapped[Optional[int]] = mapped_column(Integer, comment='供应商ID')
    delivery_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='交货日期')
    created_by: Mapped[Optional[int]] = mapped_column(Integer, comment='创建人ID')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped[Optional['Users']] = relationship('Users', back_populates='purchase_orders')
    store: Mapped['Stores'] = relationship('Stores', back_populates='purchase_orders')
    supplier: Mapped[Optional['Suppliers']] = relationship('Suppliers', back_populates='purchase_orders')
    purchase_items: Mapped[list['PurchaseItems']] = relationship('PurchaseItems', back_populates='purchase_order')


class Staff(Base):
    __tablename__ = 'staff'
    __table_args__ = (
        ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE', name='staff_store_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='staff_user_id_fkey'),
        PrimaryKeyConstraint('id', name='staff_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='用户ID')
    store_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='店铺ID')
    position: Mapped[str] = mapped_column(String(50), nullable=False, comment='职位（厨师、服务员、传菜员等）')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='是否在职')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    store: Mapped['Stores'] = relationship('Stores', back_populates='staff')
    user: Mapped['Users'] = relationship('Users', back_populates='staff')


class Tables(Base):
    __tablename__ = 'tables'
    __table_args__ = (
        ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE', name='tables_store_id_fkey'),
        PrimaryKeyConstraint('id', name='tables_pkey'),
        Index('ix_tables_store_table', 'store_id', 'table_number')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='店铺ID')
    table_number: Mapped[str] = mapped_column(String(50), nullable=False, comment='桌号')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='是否可用')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    table_name: Mapped[Optional[str]] = mapped_column(String(128), comment='桌子名称')
    qrcode_url: Mapped[Optional[str]] = mapped_column(String(500), comment='二维码URL（存储在S3）')
    qrcode_content: Mapped[Optional[str]] = mapped_column(String(255), comment='二维码内容')
    seats: Mapped[Optional[int]] = mapped_column(Integer, comment='座位数')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    store: Mapped['Stores'] = relationship('Stores', back_populates='tables')
    orders: Mapped[list['Orders']] = relationship('Orders', back_populates='table')


class InventoryLogs(Base):
    __tablename__ = 'inventory_logs'
    __table_args__ = (
        ForeignKeyConstraint(['inventory_id'], ['inventory.id'], ondelete='CASCADE', name='inventory_logs_inventory_id_fkey'),
        ForeignKeyConstraint(['operator_id'], ['users.id'], ondelete='SET NULL', name='inventory_logs_operator_id_fkey'),
        PrimaryKeyConstraint('id', name='inventory_logs_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inventory_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='库存ID')
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False, comment='操作类型（in, out, adjust）')
    quantity: Mapped[float] = mapped_column(Double(53), nullable=False, comment='变动数量')
    before_quantity: Mapped[float] = mapped_column(Double(53), nullable=False, comment='变动前数量')
    after_quantity: Mapped[float] = mapped_column(Double(53), nullable=False, comment='变动后数量')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    reason: Mapped[Optional[str]] = mapped_column(Text, comment='变动原因')
    operator_id: Mapped[Optional[int]] = mapped_column(Integer, comment='操作人ID')

    inventory: Mapped['Inventory'] = relationship('Inventory', back_populates='inventory_logs')
    operator: Mapped[Optional['Users']] = relationship('Users', back_populates='inventory_logs')


class MenuItems(Base):
    __tablename__ = 'menu_items'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['menu_categories.id'], ondelete='SET NULL', name='menu_items_category_id_fkey'),
        ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE', name='menu_items_store_id_fkey'),
        PrimaryKeyConstraint('id', name='menu_items_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='店铺ID')
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment='菜品名称')
    price: Mapped[float] = mapped_column(Double(53), nullable=False, comment='价格')
    stock: Mapped[int] = mapped_column(Integer, nullable=False, comment='库存数量')
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='是否可售')
    is_recommended: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='是否推荐')
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, comment='排序')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    category_id: Mapped[Optional[int]] = mapped_column(Integer, comment='分类ID')
    description: Mapped[Optional[str]] = mapped_column(Text, comment='菜品描述')
    original_price: Mapped[Optional[float]] = mapped_column(Double(53), comment='原价')
    image_url: Mapped[Optional[str]] = mapped_column(String(500), comment='菜品图片URL（存储在S3）')
    unit: Mapped[Optional[str]] = mapped_column(String(20), comment='单位（份、个、斤等）')
    cooking_time: Mapped[Optional[int]] = mapped_column(Integer, comment='烹饪时间（分钟）')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    category: Mapped[Optional['MenuCategories']] = relationship('MenuCategories', back_populates='menu_items')
    store: Mapped['Stores'] = relationship('Stores', back_populates='menu_items')
    order_items: Mapped[list['OrderItems']] = relationship('OrderItems', back_populates='menu_item')


class Orders(Base):
    __tablename__ = 'orders'
    __table_args__ = (
        ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE', name='orders_store_id_fkey'),
        ForeignKeyConstraint(['table_id'], ['tables.id'], ondelete='SET NULL', name='orders_table_id_fkey'),
        PrimaryKeyConstraint('id', name='orders_pkey'),
        UniqueConstraint('order_number', name='orders_order_number_key'),
        Index('ix_orders_order_number', 'order_number'),
        Index('ix_orders_store_created', 'store_id', 'created_at'),
        Index('ix_orders_table', 'table_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='店铺ID')
    order_number: Mapped[str] = mapped_column(String(50), nullable=False, comment='订单号')
    total_amount: Mapped[float] = mapped_column(Double(53), nullable=False, comment='订单总金额')
    discount_amount: Mapped[float] = mapped_column(Double(53), nullable=False, comment='折扣金额')
    final_amount: Mapped[float] = mapped_column(Double(53), nullable=False, comment='实付金额')
    payment_status: Mapped[str] = mapped_column(String(50), nullable=False, comment='支付状态')
    order_status: Mapped[str] = mapped_column(String(50), nullable=False, comment='订单状态')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    table_id: Mapped[Optional[int]] = mapped_column(Integer, comment='桌号ID')
    customer_name: Mapped[Optional[str]] = mapped_column(String(128), comment='顾客姓名')
    customer_phone: Mapped[Optional[str]] = mapped_column(String(20), comment='顾客手机号')
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), comment='支付方式')
    payment_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='支付时间')
    special_instructions: Mapped[Optional[str]] = mapped_column(Text, comment='特殊要求')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    store: Mapped['Stores'] = relationship('Stores', back_populates='orders')
    table: Mapped[Optional['Tables']] = relationship('Tables', back_populates='orders')
    order_items: Mapped[list['OrderItems']] = relationship('OrderItems', back_populates='order')
    order_status_logs: Mapped[list['OrderStatusLogs']] = relationship('OrderStatusLogs', back_populates='order')
    payments: Mapped[list['Payments']] = relationship('Payments', back_populates='order')
    point_logs: Mapped[list['PointLogs']] = relationship('PointLogs', back_populates='order')


class PurchaseItems(Base):
    __tablename__ = 'purchase_items'
    __table_args__ = (
        ForeignKeyConstraint(['inventory_id'], ['inventory.id'], ondelete='SET NULL', name='purchase_items_inventory_id_fkey'),
        ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], ondelete='CASCADE', name='purchase_items_purchase_order_id_fkey'),
        PrimaryKeyConstraint('id', name='purchase_items_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    purchase_order_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='采购订单ID')
    item_name: Mapped[str] = mapped_column(String(255), nullable=False, comment='物料名称')
    quantity: Mapped[float] = mapped_column(Double(53), nullable=False, comment='数量')
    unit_price: Mapped[float] = mapped_column(Double(53), nullable=False, comment='单价')
    subtotal: Mapped[float] = mapped_column(Double(53), nullable=False, comment='小计')
    received_quantity: Mapped[float] = mapped_column(Double(53), nullable=False, comment='已收货数量')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    inventory_id: Mapped[Optional[int]] = mapped_column(Integer, comment='库存ID')

    inventory: Mapped[Optional['Inventory']] = relationship('Inventory', back_populates='purchase_items')
    purchase_order: Mapped['PurchaseOrders'] = relationship('PurchaseOrders', back_populates='purchase_items')


class OrderItems(Base):
    __tablename__ = 'order_items'
    __table_args__ = (
        ForeignKeyConstraint(['menu_item_id'], ['menu_items.id'], ondelete='SET NULL', name='order_items_menu_item_id_fkey'),
        ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE', name='order_items_order_id_fkey'),
        PrimaryKeyConstraint('id', name='order_items_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='订单ID')
    menu_item_name: Mapped[str] = mapped_column(String(255), nullable=False, comment='菜品名称（快照）')
    menu_item_price: Mapped[float] = mapped_column(Double(53), nullable=False, comment='菜品价格（快照）')
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, comment='数量')
    subtotal: Mapped[float] = mapped_column(Double(53), nullable=False, comment='小计')
    status: Mapped[str] = mapped_column(String(50), nullable=False, comment='状态')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    menu_item_id: Mapped[Optional[int]] = mapped_column(Integer, comment='菜品ID')
    special_instructions: Mapped[Optional[str]] = mapped_column(Text, comment='特殊要求')

    menu_item: Mapped[Optional['MenuItems']] = relationship('MenuItems', back_populates='order_items')
    order: Mapped['Orders'] = relationship('Orders', back_populates='order_items')


class OrderStatusLogs(Base):
    __tablename__ = 'order_status_logs'
    __table_args__ = (
        ForeignKeyConstraint(['operator_id'], ['users.id'], ondelete='SET NULL', name='order_status_logs_operator_id_fkey'),
        ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE', name='order_status_logs_order_id_fkey'),
        PrimaryKeyConstraint('id', name='order_status_logs_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='订单ID')
    to_status: Mapped[str] = mapped_column(String(50), nullable=False, comment='新状态')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    from_status: Mapped[Optional[str]] = mapped_column(String(50), comment='原状态')
    operator_id: Mapped[Optional[int]] = mapped_column(Integer, comment='操作人ID')
    operator_name: Mapped[Optional[str]] = mapped_column(String(128), comment='操作人姓名')
    notes: Mapped[Optional[str]] = mapped_column(Text, comment='备注')

    operator: Mapped[Optional['Users']] = relationship('Users', back_populates='order_status_logs')
    order: Mapped['Orders'] = relationship('Orders', back_populates='order_status_logs')


class Payments(Base):
    __tablename__ = 'payments'
    __table_args__ = (
        ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE', name='payments_order_id_fkey'),
        PrimaryKeyConstraint('id', name='payments_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='订单ID')
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False, comment='支付方式')
    amount: Mapped[float] = mapped_column(Double(53), nullable=False, comment='支付金额')
    status: Mapped[str] = mapped_column(String(50), nullable=False, comment='支付状态')
    refund_amount: Mapped[float] = mapped_column(Double(53), nullable=False, comment='退款金额')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    transaction_id: Mapped[Optional[str]] = mapped_column(String(255), comment='交易号')
    payment_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='支付时间')
    refund_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='退款时间')
    refund_reason: Mapped[Optional[str]] = mapped_column(Text, comment='退款原因')

    order: Mapped['Orders'] = relationship('Orders', back_populates='payments')


class PointLogs(Base):
    __tablename__ = 'point_logs'
    __table_args__ = (
        ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE', name='point_logs_member_id_fkey'),
        ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='SET NULL', name='point_logs_order_id_fkey'),
        PrimaryKeyConstraint('id', name='point_logs_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='会员ID')
    points: Mapped[int] = mapped_column(Integer, nullable=False, comment='积分变动')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    order_id: Mapped[Optional[int]] = mapped_column(Integer, comment='订单ID')
    reason: Mapped[Optional[str]] = mapped_column(String(255), comment='变动原因')

    member: Mapped['Members'] = relationship('Members', back_populates='point_logs')
    order: Mapped[Optional['Orders']] = relationship('Orders', back_populates='point_logs')


class RoleConfig(Base):
    """角色配置表 - 支持店铺自定义角色"""
    __tablename__ = 'role_config'
    __table_args__ = (
        ForeignKeyConstraint(['店铺ID'], ['stores.id'], ondelete='CASCADE', name='role_config_store_id_fkey'),
        PrimaryKeyConstraint('id', name='role_config_pkey'),
        UniqueConstraint('店铺ID', '角色名称', name='role_config_store_role_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    店铺ID: Mapped[int] = mapped_column(Integer, nullable=False, comment='店铺ID')
    角色名称: Mapped[str] = mapped_column(String(50), nullable=False, comment='角色名称')
    角色描述: Mapped[Optional[str]] = mapped_column(String(255), comment='角色描述')
    是否启用: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment='是否启用')
    排序: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment='排序序号')
    创建时间: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    更新时间: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='更新时间')


class OrderFlowConfig(Base):
    """订单流程配置表 - 将订单状态的操作权限分配给角色"""
    __tablename__ = 'order_flow_config'
    __table_args__ = (
        ForeignKeyConstraint(['店铺ID'], ['stores.id'], ondelete='CASCADE', name='order_flow_config_store_id_fkey'),
        PrimaryKeyConstraint('id', name='order_flow_config_pkey'),
        UniqueConstraint('店铺ID', '角色名称', '订单状态', name='order_flow_config_store_role_status_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    店铺ID: Mapped[int] = mapped_column(Integer, nullable=False, comment='店铺ID')
    角色名称: Mapped[str] = mapped_column(String(50), nullable=False, comment='角色名称（关联role_config）')
    订单状态: Mapped[str] = mapped_column(String(50), nullable=False, comment='订单状态：待确认, 制作中, 待传菜, 上菜中, 已完成')
    操作方式: Mapped[str] = mapped_column(String(50), nullable=False, default='逐项确认', comment='操作方式：逐项确认, 订单确认, 自动跳过, 忽略不显示')
    是否启用: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment='是否启用该配置')
    排序: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment='排序序号')
    创建时间: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    更新时间: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='更新时间')


# 更新 Stores 模型添加关系（需要在 Stores 类中添加）
# Stores.workflow_configs = relationship('WorkflowConfig', back_populates='store', cascade='all, delete-orphan')


# ============ 跨店铺结算与第三方积分互通系统 ============

class StorePointSettlements(Base):
    """店铺积分结算表 - 记录不同店铺之间的积分结算关系"""
    __tablename__ = 'store_point_settlements'
    __table_args__ = (
        ForeignKeyConstraint(['source_store_id'], ['stores.id'], ondelete='CASCADE', name='store_point_settlements_source_store_fkey'),
        ForeignKeyConstraint(['target_store_id'], ['stores.id'], ondelete='CASCADE', name='store_point_settlements_target_store_fkey'),
        ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE', name='store_point_settlements_member_fkey'),
        PrimaryKeyConstraint('id', name='store_point_settlements_pkey'),
        Index('ix_store_point_settlements_source_target', 'source_store_id', 'target_store_id'),
        Index('ix_store_point_settlements_date', 'settlement_date')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_store_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='积分来源店铺ID')
    target_store_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='积分目标店铺ID')
    member_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='会员ID')
    points: Mapped[int] = mapped_column(Integer, nullable=False, comment='积分数量')
    settlement_date: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, comment='结算日期')
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='pending', comment='结算状态: pending, completed, cancelled')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    order_id: Mapped[Optional[int]] = mapped_column(Integer, comment='关联订单ID')
    point_log_id: Mapped[Optional[int]] = mapped_column(Integer, comment='关联积分日志ID')
    settlement_rate: Mapped[float] = mapped_column(Double(53), nullable=False, default=1.0, comment='结算汇率')
    settlement_amount: Mapped[Optional[float]] = mapped_column(Double(53), comment='结算金额')
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='完成时间')
    remarks: Mapped[Optional[str]] = mapped_column(Text, comment='备注')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    source_store: Mapped['Stores'] = relationship('Stores', foreign_keys=[source_store_id])
    target_store: Mapped['Stores'] = relationship('Stores', foreign_keys=[target_store_id])
    member: Mapped['Members'] = relationship('Members')


class ThirdPartyPointAgreements(Base):
    """第三方积分协议表 - 记录与第三方公司的积分合作协议"""
    __tablename__ = 'third_party_point_agreements'
    __table_args__ = (
        ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE', name='third_party_agreements_store_fkey'),
        ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE', name='third_party_agreements_company_fkey'),
        PrimaryKeyConstraint('id', name='third_party_point_agreements_pkey'),
        Index('ix_third_party_agreements_store', 'store_id'),
        Index('ix_third_party_agreements_status', 'status')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='本店铺ID')
    company_id: Mapped[Optional[int]] = mapped_column(Integer, comment='第三方公司ID（内部公司）')
    third_party_name: Mapped[str] = mapped_column(String(255), nullable=False, comment='第三方公司名称')
    third_party_store_id: Mapped[Optional[str]] = mapped_column(String(255), comment='第三方店铺ID（外部系统）')
    agreement_type: Mapped[str] = mapped_column(String(50), nullable=False, default='bidirectional', comment='协议类型: bidirectional(双向), inbound(只进), outbound(只出)')
    exchange_rate: Mapped[float] = mapped_column(Double(53), nullable=False, default=1.0, comment='积分兑换比例: 1第三方积分 = 本方积分')
    max_points_per_day: Mapped[Optional[int]] = mapped_column(Integer, comment='每日最大兑换积分数')
    max_points_per_order: Mapped[Optional[int]] = mapped_column(Integer, comment='单笔订单最大兑换积分数')
    settlement_cycle: Mapped[str] = mapped_column(String(50), nullable=False, default='daily', comment='结算周期: daily, weekly, monthly')
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='active', comment='状态: active, suspended, terminated')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    valid_from: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='生效日期')
    valid_until: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='到期日期')
    api_endpoint: Mapped[Optional[str]] = mapped_column(String(500), comment='第三方API地址')
    api_key: Mapped[Optional[str]] = mapped_column(String(255), comment='第三方API密钥')
    contact_person: Mapped[Optional[str]] = mapped_column(String(128), comment='联系人')
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), comment='联系电话')
    settlement_balance: Mapped[float] = mapped_column(Double(53), nullable=False, default=0.0, comment='结算余额')
    last_settlement_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='上次结算日期')
    remarks: Mapped[Optional[str]] = mapped_column(Text, comment='备注')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    store: Mapped['Stores'] = relationship('Stores')
    company: Mapped[Optional['Companies']] = relationship('Companies')


class PointExchangeLogs(Base):
    """积分兑换日志表 - 记录第三方积分兑换详情"""
    __tablename__ = 'point_exchange_logs'
    __table_args__ = (
        ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE', name='point_exchange_logs_member_fkey'),
        ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE', name='point_exchange_logs_store_fkey'),
        ForeignKeyConstraint(['agreement_id'], ['third_party_point_agreements.id'], ondelete='CASCADE', name='point_exchange_logs_agreement_fkey'),
        ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='SET NULL', name='point_exchange_logs_order_fkey'),
        PrimaryKeyConstraint('id', name='point_exchange_logs_pkey'),
        Index('ix_point_exchange_logs_member', 'member_id'),
        Index('ix_point_exchange_logs_store', 'store_id'),
        Index('ix_point_exchange_logs_date', 'created_at')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='会员ID')
    store_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='店铺ID')
    agreement_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='第三方协议ID')
    exchange_type: Mapped[str] = mapped_column(String(50), nullable=False, comment='兑换类型: inbound(第三方->本方), outbound(本方->第三方)')
    source_points: Mapped[int] = mapped_column(Integer, nullable=False, comment='源积分数量')
    target_points: Mapped[int] = mapped_column(Integer, nullable=False, comment='目标积分数量')
    exchange_rate: Mapped[float] = mapped_column(Double(53), nullable=False, comment='兑换比例')
    order_id: Mapped[Optional[int]] = mapped_column(Integer, comment='关联订单ID')
    third_party_order_no: Mapped[Optional[str]] = mapped_column(String(100), comment='第三方订单号')
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='pending', comment='状态: pending, success, failed, cancelled')
    error_message: Mapped[Optional[str]] = mapped_column(Text, comment='错误信息')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='完成时间')
    remarks: Mapped[Optional[str]] = mapped_column(Text, comment='备注')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    member: Mapped['Members'] = relationship('Members')
    store: Mapped['Stores'] = relationship('Stores')
    agreement: Mapped['ThirdPartyPointAgreements'] = relationship('ThirdPartyPointAgreements')
    order: Mapped[Optional['Orders']] = relationship('Orders')


class DiscountConfig(Base):
    """优惠配置表 - 店铺或公司设置的优惠规则"""
    __tablename__ = 'discount_config'
    __table_args__ = (
        ForeignKeyConstraint(['store_id'], ['stores.id'], ondelete='CASCADE', name='discount_config_store_id_fkey'),
        ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE', name='discount_config_company_id_fkey'),
        PrimaryKeyConstraint('id', name='discount_config_pkey'),
        Index('ix_discount_config_store', 'store_id'),
        Index('ix_discount_config_company', 'company_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    store_id: Mapped[Optional[int]] = mapped_column(Integer, comment='店铺ID（店铺级别优惠）')
    company_id: Mapped[Optional[int]] = mapped_column(Integer, comment='公司ID（公司级别优惠）')
    discount_type: Mapped[str] = mapped_column(String(50), nullable=False, comment='优惠类型: percentage(百分比), fixed(固定金额), points(积分抵扣)')
    discount_value: Mapped[float] = mapped_column(Double(53), nullable=False, comment='优惠值')
    min_amount: Mapped[Optional[float]] = mapped_column(Double(53), comment='最低消费金额')
    max_discount: Mapped[Optional[float]] = mapped_column(Double(53), comment='最大优惠金额')
    member_level: Mapped[Optional[int]] = mapped_column(Integer, comment='适用会员等级(不填则所有等级)')
    points_required: Mapped[Optional[int]] = mapped_column(Integer, comment='所需积分')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment='是否启用')
    valid_from: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='生效日期')
    valid_until: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='到期日期')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    description: Mapped[Optional[str]] = mapped_column(Text, comment='优惠描述')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    store: Mapped[Optional['Stores']] = relationship('Stores')
    company: Mapped[Optional['Companies']] = relationship('Companies')


class MemberQRCodes(Base):
    """会员二维码表 - 存储会员的二维码信息"""
    __tablename__ = 'member_qrcodes'
    __table_args__ = (
        ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE', name='member_qrcodes_member_id_fkey'),
        PrimaryKeyConstraint('id', name='member_qrcodes_pkey'),
        UniqueConstraint('member_id', name='member_qrcodes_member_id_key')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    member_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='会员ID')
    qr_code_url: Mapped[str] = mapped_column(String(500), nullable=False, comment='二维码URL（存储在S3）')
    qr_code_key: Mapped[str] = mapped_column(String(255), nullable=False, comment='二维码对象键')
    valid_from: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'), comment='生效时间')
    valid_until: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='到期时间')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment='是否有效')
    scan_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, comment='扫描次数')
    last_scan_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True), comment='最后扫描时间')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    member: Mapped['Members'] = relationship('Members')

