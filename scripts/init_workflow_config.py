"""
初始化订单流程配置表
为每个店铺创建默认的工作流程配置
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from storage.database.db import get_session
from storage.database.shared.model import Stores, WorkflowConfig

def init_workflow_config():
    """初始化工作流程配置"""
    db = get_session()
    try:
        # 检查表是否存在
        result = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'workflow_config'
            )
        """))
        table_exists = result.scalar()

        if not table_exists:
            print("创建 workflow_config 表...")
            db.execute(text("""
                CREATE TABLE workflow_config (
                    id SERIAL PRIMARY KEY,
                    store_id INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
                    role VARCHAR(50) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    action_mode VARCHAR(50) NOT NULL DEFAULT 'per_item',
                    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE,
                    UNIQUE(store_id, role, status)
                )
            """))
            db.commit()
            print("✅ workflow_config 表创建成功")
        else:
            print("✅ workflow_config 表已存在")

        # 获取所有店铺
        stores = db.query(Stores).all()
        print(f"\n找到 {len(stores)} 个店铺")

        # 默认配置
        default_configs = [
            # 厨师配置
            {
                'role': 'kitchen',
                'status': 'pending',
                'action_mode': 'per_item',  # 默认：逐项确认每道菜
                'is_enabled': True,
                'description': '待确认订单'
            },
            {
                'role': 'kitchen',
                'status': 'preparing',
                'action_mode': 'per_item',  # 默认：逐项确认每道菜
                'is_enabled': True,
                'description': '制作中'
            },
            # 传菜员配置
            {
                'role': 'waiter',
                'status': 'ready',
                'action_mode': 'per_order',  # 默认：按订单确认
                'is_enabled': True,
                'description': '待传菜'
            },
            {
                'role': 'waiter',
                'status': 'serving',
                'action_mode': 'per_order',  # 默认：按订单确认
                'is_enabled': True,
                'description': '上菜中'
            },
            # 收银员配置
            {
                'role': 'cashier',
                'status': 'completed',
                'action_mode': 'skip',  # 默认：自动完成
                'is_enabled': False,  # 默认不启用（自动流转）
                'description': '订单完成'
            },
            # 店长配置
            {
                'role': 'manager',
                'status': 'completed',
                'action_mode': 'skip',  # 默认：自动完成
                'is_enabled': True,
                'description': '订单完成确认'
            }
        ]

        # 为每个店铺创建配置
        for store in stores:
            print(f"\n📋 为店铺 '{store.name}' 创建配置...")

            # 检查是否已有配置
            existing_count = db.query(WorkflowConfig).filter(
                WorkflowConfig.store_id == store.id
            ).count()

            if existing_count > 0:
                print(f"  ⚠️  已存在 {existing_count} 条配置，跳过")
                continue

            created_count = 0
            for config in default_configs:
                # 检查是否已存在
                existing = db.query(WorkflowConfig).filter(
                    WorkflowConfig.store_id == store.id,
                    WorkflowConfig.role == config['role'],
                    WorkflowConfig.status == config['status']
                ).first()

                if not existing:
                    new_config = WorkflowConfig(
                        store_id=store.id,
                        role=config['role'],
                        status=config['status'],
                        action_mode=config['action_mode'],
                        is_enabled=config['is_enabled']
                    )
                    db.add(new_config)
                    created_count += 1
                    print(f"  ✅ 创建配置: {config['role']} - {config['status']} ({config['action_mode']})")

            db.commit()
            print(f"  📊 共创建 {created_count} 条配置")

        print("\n" + "="*60)
        print("✅ 订单流程配置初始化完成！")
        print("="*60)
        print("\n配置说明:")
        print("  role: 角色（kitchen=厨师, waiter=传菜员, cashier=收银员, manager=店长）")
        print("  status: 订单状态（pending, preparing, ready, serving, completed）")
        print("  action_mode: 操作模式")
        print("    - per_item: 逐项确认（每道菜单独确认）")
        print("    - per_order: 订单确认（整个订单一起确认）")
        print("    - skip: 跳过（自动流转到下一状态）")
        print("    - ignore: 忽略（不显示该状态）")
        print("  is_enabled: 是否启用该环节")
        print("\n可以在店铺设置页面修改这些配置")

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("="*60)
    print("🍽️ 订单流程配置初始化工具")
    print("="*60)
    print()
    init_workflow_config()
