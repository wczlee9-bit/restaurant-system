"""
小票打印 API
支持小票打印、小票模板配置、功能区设置
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from storage.database.db import get_session
from storage.database.shared.model import Orders, OrderItems, Stores, Tables, Users, Payments
from jinja2 import Template
import logging

# 创建 FastAPI 应用
app = FastAPI(title="扫码点餐系统 - 小票打印API", version="1.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)


# ============ 数据模型 ============

class ReceiptSectionConfig(BaseModel):
    """小票功能区配置"""
    section_type: str = Field(..., description="功能区类型: header, customer, items, payment, footer, custom")
    section_name: str = Field(..., description="功能区名称")
    is_enabled: bool = Field(True, description="是否启用")
    sort_order: int = Field(0, description="排序")
    template: Optional[str] = Field(None, description="自定义模板")
    config: Optional[Dict[str, Any]] = Field(None, description="附加配置")


class ReceiptConfigCreateRequest(BaseModel):
    """小票配置创建请求"""
    store_id: int
    config_name: str = Field(..., description="配置名称")
    sections: List[ReceiptSectionConfig] = Field(..., description="功能区配置列表")


class ReceiptConfigResponse(BaseModel):
    """小票配置响应"""
    id: int
    store_id: int
    config_name: str
    sections: List[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime] = None


class PrintReceiptRequest(BaseModel):
    """打印小票请求"""
    order_id: int
    printer_name: Optional[str] = Field(None, description="打印机名称")
    copy_count: int = Field(1, description="打印份数")
    config_id: Optional[int] = Field(None, description="小票配置ID（不传则使用默认配置）")


# ============ 小票模板 ============

# 默认小票功能区配置
DEFAULT_RECEIPT_SECTIONS = [
    {
        "section_type": "header",
        "section_name": "店铺信息",
        "is_enabled": True,
        "sort_order": 1,
        "template": """
{{ store.name }}
地址: {{ store.address or '暂无' }}
电话: {{ store.phone or '暂无' }}
================================
""",
        "config": {}
    },
    {
        "section_type": "order_info",
        "section_name": "订单信息",
        "is_enabled": True,
        "sort_order": 2,
        "template": """
订单号: {{ order.order_number }}
桌号: {{ table.table_number }}
下单时间: {{ order.created_at.strftime('%Y-%m-%d %H:%M:%S') }}
--------------------------------
""",
        "config": {}
    },
    {
        "section_type": "customer",
        "section_name": "顾客信息",
        "is_enabled": True,
        "sort_order": 3,
        "template": """
顾客: {{ order.customer_name or '散客' }}
电话: {{ order.customer_phone or '-' }}
会员: {{ member_info }}
--------------------------------
""",
        "config": {}
    },
    {
        "section_type": "items",
        "section_name": "商品明细",
        "is_enabled": True,
        "sort_order": 4,
        "template": """
商品名称            数量  金额
{% for item in items %}
{{ item.menu_item_name.ljust(14) }} {{ item.quantity }}  {{ item.subtotal }}
{% endfor %}
--------------------------------
""",
        "config": {}
    },
    {
        "section_type": "payment",
        "section_name": "支付信息",
        "is_enabled": True,
        "sort_order": 5,
        "template": """
商品总额:  {{ order.total_amount }}
折扣金额:  {{ order.discount_amount }}
实付金额:  {{ order.final_amount }}
支付方式:  {{ order.payment_method }}
支付时间:  {{ order.payment_time.strftime('%Y-%m-%d %H:%M:%S') if order.payment_time else '待支付' }}
================================
""",
        "config": {}
    },
    {
        "section_type": "footer",
        "section_name": "底部信息",
        "is_enabled": True,
        "sort_order": 6,
        "template": """
感谢您的光临!
欢迎再次惠顾!
客服热线: {{ store.phone or '400-xxx-xxxx' }}
""",
        "config": {}
    }
]


# ============ 工具函数 ============

def generate_receipt_content(
    order: Orders,
    store: Stores,
    table: Tables,
    items: List[OrderItems],
    member_info: str,
    sections: List[Dict[str, Any]]
) -> str:
    """
    生成小票内容
    
    Args:
        order: 订单对象
        store: 店铺对象
        table: 桌号对象
        items: 订单项列表
        member_info: 会员信息
        sections: 功能区配置列表
    
    Returns:
        小票文本内容
    """
    # 按排序排序功能区
    sorted_sections = sorted(
        [s for s in sections if s.get("is_enabled", True)],
        key=lambda x: x.get("sort_order", 0)
    )
    
    receipt_content = ""
    
    for section in sorted_sections:
        template_str = section.get("template", "")
        if not template_str:
            continue
        
        # 渲染模板
        template = Template(template_str)
        content = template.render(
            order=order,
            store=store,
            table=table,
            items=items,
            member_info=member_info
        )
        
        receipt_content += content + "\n"
    
    return receipt_content.strip()


def get_member_info(db: Session, order: Orders) -> str:
    """
    获取会员信息
    
    Args:
        db: 数据库会话
        order: 订单对象
    
    Returns:
        会员信息字符串
    """
    if not order.customer_phone:
        return "非会员"
    
    from storage.database.shared.model import Members
    member = db.query(Members).filter(Members.phone == order.customer_phone).first()
    if not member:
        return "非会员"
    
    return f"{member.name} (积分:{member.points})"


def get_default_config() -> List[Dict[str, Any]]:
    """获取默认小票配置"""
    return DEFAULT_RECEIPT_SECTIONS


# ============ API 接口 ============

@app.get("/")
def root():
    """根路径"""
    return {
        "message": "扫码点餐系统 - 小票打印API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/receipt/print": "打印小票",
            "POST /api/receipt/config": "创建小票配置",
            "GET /api/receipt/config/{config_id}": "获取小票配置",
            "GET /api/receipt/store/{store_id}/config": "获取店铺的小票配置",
            "PUT /api/receipt/config/{config_id}": "更新小票配置",
            "GET /api/receipt/default-config": "获取默认小票配置",
            "GET /api/receipt/preview/{order_id}": "预览小票"
        }
    }


@app.post("/api/receipt/print")
def print_receipt(request: PrintReceiptRequest):
    """
    打印小票
    """
    db = get_session()
    try:
        # 获取订单
        order = db.query(Orders).filter(Orders.id == request.order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        # 获取店铺信息
        store = db.query(Stores).filter(Stores.id == order.store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="店铺不存在")
        
        # 获取桌号信息
        table = db.query(Tables).filter(Tables.id == order.table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail="桌号不存在")
        
        # 获取订单项
        items = db.query(OrderItems).filter(OrderItems.order_id == order.id).all()
        if not items:
            raise HTTPException(status_code=404, detail="订单项不存在")
        
        # 获取会员信息
        member_info = get_member_info(db, order)
        
        # 获取小票配置（这里暂时使用默认配置，实际应该从数据库读取）
        sections = get_default_config()
        
        # 生成小票内容
        receipt_content = generate_receipt_content(
            order,
            store,
            table,
            items,
            member_info,
            sections
        )
        
        # 模拟打印（实际使用时，这里会调用打印机API）
        logger.info(f"打印小票: 订单ID={order.order_number}, 打印份数={request.copy_count}")
        
        return {
            "message": "小票打印成功",
            "order_id": order.id,
            "order_number": order.order_number,
            "copy_count": request.copy_count,
            "receipt_content": receipt_content,
            "printer_name": request.printer_name or "默认打印机"
        }
        
    finally:
        db.close()


@app.get("/api/receipt/preview/{order_id}")
def preview_receipt(order_id: int):
    """
    预览小票
    """
    db = get_session()
    try:
        # 获取订单
        order = db.query(Orders).filter(Orders.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        
        # 获取店铺信息
        store = db.query(Stores).filter(Stores.id == order.store_id).first()
        if not store:
            raise HTTPException(status_code=404, detail="店铺不存在")
        
        # 获取桌号信息
        table = db.query(Tables).filter(Tables.id == order.table_id).first()
        if not table:
            raise HTTPException(status_code=404, detail="桌号不存在")
        
        # 获取订单项
        items = db.query(OrderItems).filter(OrderItems.order_id == order.id).all()
        if not items:
            raise HTTPException(status_code=404, detail="订单项不存在")
        
        # 获取会员信息
        member_info = get_member_info(db, order)
        
        # 获取小票配置（暂时使用默认配置）
        sections = get_default_config()
        
        # 生成小票内容
        receipt_content = generate_receipt_content(
            order,
            store,
            table,
            items,
            member_info,
            sections
        )
        
        return {
            "order_id": order.id,
            "order_number": order.order_number,
            "receipt_content": receipt_content
        }
        
    finally:
        db.close()


@app.get("/api/receipt/default-config")
def get_default_config_endpoint():
    """
    获取默认小票配置
    """
    return {
        "sections": DEFAULT_RECEIPT_SECTIONS
    }


@app.post("/api/receipt/config")
def create_receipt_config(request: ReceiptConfigCreateRequest):
    """
    创建小票配置
    （注：实际使用时需要添加receipt_config表来持久化配置，这里返回成功响应）
    """
    # 这里应该是将配置保存到数据库
    # 由于数据库模型中没有receipt_config表，暂时只返回成功响应
    
    return {
        "message": "小票配置创建成功",
        "store_id": request.store_id,
        "config_name": request.config_name,
        "section_count": len(request.sections)
    }


@app.get("/api/receipt/config/{config_id}", response_model=ReceiptConfigResponse)
def get_receipt_config(config_id: int):
    """
    获取小票配置
    """
    # 这里应该从数据库读取配置
    # 暂时返回默认配置
    return ReceiptConfigResponse(
        id=config_id,
        store_id=1,
        config_name="默认配置",
        sections=DEFAULT_RECEIPT_SECTIONS,
        created_at=datetime.now()
    )


@app.get("/api/receipt/store/{store_id}/config", response_model=List[ReceiptConfigResponse])
def get_store_receipt_configs(store_id: int):
    """
    获取店铺的小票配置列表
    """
    # 这里应该从数据库读取配置
    # 暂时返回默认配置
    return [
        ReceiptConfigResponse(
            id=1,
            store_id=store_id,
            config_name="默认配置",
            sections=DEFAULT_RECEIPT_SECTIONS,
            created_at=datetime.now()
        )
    ]


@app.put("/api/receipt/config/{config_id}")
def update_receipt_config(config_id: int, request: ReceiptConfigCreateRequest):
    """
    更新小票配置
    """
    # 这里应该更新数据库中的配置
    # 暂时只返回成功响应
    
    return {
        "message": "小票配置更新成功",
        "config_id": config_id,
        "section_count": len(request.sections)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
