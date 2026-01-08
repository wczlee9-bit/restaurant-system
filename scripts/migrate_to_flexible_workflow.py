"""
数据库迁移脚本：从固定角色流程配置迁移到灵活的功能分配配置

功能：
1. 删除旧的 workflow_config 表
2. 创建新的 role_config 和 order_flow_config 表
3. 为所有现有店铺初始化默认角色和流程配置
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from src.storage.database.shared.model import Base, RoleConfig, OrderFlowConfig, Stores

# 数据库连接配置
DATABASE_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/restaurant"
)

def migrate_database():
    """执行数据库迁移"""
    print("=" * 80)
    print("开始执行数据库迁移：固定角色流程 -> 灵活功能分配配置")
    print("=" * 80)
    
    # 创建数据库引擎
    engine = create_engine(DATABASE_URL, echo=True)
    
    # 创建会话
    SessionLocal = sessionmaker(bind=engine)
    session: Session = SessionLocal()
    
    try:
        # 步骤1：删除旧的 workflow_config 表（如果存在）
        print("\n[1/5] 删除旧的 workflow_config 表...")
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS workflow_config CASCADE"))
            conn.commit()
        print("✓ 旧表删除完成")
        
        # 步骤2：创建新的表
        print("\n[2/5] 创建新的 role_config 和 order_flow_config 表...")
        Base.metadata.create_all(bind=engine)
        print("✓ 新表创建完成")
        
        # 步骤3：获取所有店铺
        print("\n[3/5] 获取所有店铺...")
        stores = session.query(Stores).filter(Stores.是否启用 == True).all()
        print(f"✓ 找到 {len(stores)} 个活跃店铺")
        
        if not stores:
            print("⚠ 警告：没有找到活跃店铺，跳过初始化")
            return
        
        # 步骤4：为每个店铺初始化默认角色
        print("\n[4/5] 为每个店铺初始化默认角色...")
        default_roles = [
            {"角色名称": "店长", "角色描述": "店铺管理者，拥有所有权限", "排序": 1},
            {"角色名称": "厨师", "角色描述": "负责制作菜品", "排序": 2},
            {"角色名称": "传菜员", "角色描述": "负责传菜和上菜", "排序": 3},
            {"角色名称": "收银员", "角色描述": "负责收银和订单管理", "排序": 4},
            {"角色名称": "服务员", "角色描述": "负责服务顾客", "排序": 5},
        ]
        
        for store in stores:
            print(f"  - 店铺 [{store.id}] {store.名称}：")
            for role_data in default_roles:
                # 检查是否已存在
                existing = session.query(RoleConfig).filter(
                    RoleConfig.店铺ID == store.id,
                    RoleConfig.角色名称 == role_data["角色名称"]
                ).first()
                
                if not existing:
                    role_config = RoleConfig(
                        店铺ID=store.id,
                        **role_data,
                        是否启用=True
                    )
                    session.add(role_config)
                    print(f"    ✓ 创建角色：{role_data['角色名称']}")
        
        session.commit()
        print("✓ 默认角色初始化完成")
        
        # 步骤5：为每个店铺初始化默认订单流程配置
        print("\n[5/5] 为每个店铺初始化默认订单流程配置...")
        
        # 默认流程配置（角色名 -> 状态 -> 操作方式）
        default_flow_config = [
            # 厨师：负责确认订单和制作
            {"角色名称": "厨师", "订单状态": "待确认", "操作方式": "逐项确认", "是否启用": True, "排序": 1},
            {"角色名称": "厨师", "订单状态": "制作中", "操作方式": "订单确认", "是否启用": True, "排序": 2},
            
            # 传菜员：负责传菜和上菜
            {"角色名称": "传菜员", "订单状态": "待传菜", "操作方式": "订单确认", "是否启用": True, "排序": 3},
            {"角色名称": "传菜员", "订单状态": "上菜中", "操作方式": "逐项确认", "是否启用": True, "排序": 4},
            
            # 收银员：负责确认订单完成和收银
            {"角色名称": "收银员", "订单状态": "已完成", "操作方式": "订单确认", "是否启用": True, "排序": 5},
            
            # 店长：所有状态都可以监控（忽略不显示操作）
            {"角色名称": "店长", "订单状态": "待确认", "操作方式": "忽略不显示", "是否启用": True, "排序": 10},
            {"角色名称": "店长", "订单状态": "制作中", "操作方式": "忽略不显示", "是否启用": True, "排序": 11},
            {"角色名称": "店长", "订单状态": "待传菜", "操作方式": "忽略不显示", "是否启用": True, "排序": 12},
            {"角色名称": "店长", "订单状态": "上菜中", "操作方式": "忽略不显示", "是否启用": True, "排序": 13},
            {"角色名称": "店长", "订单状态": "已完成", "操作方式": "忽略不显示", "是否启用": True, "排序": 14},
        ]
        
        for store in stores:
            print(f"  - 店铺 [{store.id}] {store.名称}：")
            for config_data in default_flow_config:
                # 检查是否已存在
                existing = session.query(OrderFlowConfig).filter(
                    OrderFlowConfig.店铺ID == store.id,
                    OrderFlowConfig.角色名称 == config_data["角色名称"],
                    OrderFlowConfig.订单状态 == config_data["订单状态"]
                ).first()
                
                if not existing:
                    flow_config = OrderFlowConfig(
                        店铺ID=store.id,
                        **config_data
                    )
                    session.add(flow_config)
                    print(f"    ✓ 添加配置：{config_data['角色名称']} -> {config_data['订单状态']} -> {config_data['操作方式']}")
        
        session.commit()
        print("✓ 默认流程配置初始化完成")
        
        # 打印统计信息
        print("\n" + "=" * 80)
        print("迁移完成！统计信息：")
        print("=" * 80)
        
        role_count = session.query(RoleConfig).count()
        flow_count = session.query(OrderFlowConfig).count()
        
        print(f"✓ 总角色数：{role_count}")
        print(f"✓ 总流程配置数：{flow_count}")
        
        print("\n新表结构：")
        print("  - role_config：角色配置表（支持动态创建角色）")
        print("  - order_flow_config：订单流程配置表（将功能分配给角色）")
        
        print("\n使用说明：")
        print("  1. 角色可以动态创建、编辑、删除")
        print("  2. 订单状态（待确认、制作中、待传菜、上菜中、已完成）可以分配给任意角色")
        print("  3. 每个角色对每个状态的操作方式可以独立配置：")
        print("     - 逐项确认：逐个确认每个订单项")
        print("     - 订单确认：一次性确认整个订单")
        print("     - 自动跳过：该角色不需要处理此状态，自动流转到下一个状态")
        print("     - 忽略不显示：该角色可以看到但不需要操作")
        
        print("\n灵活性示例：")
        print("  - 传菜员角色可以不配置（删除或禁用）")
        print("  - 传菜功能可以分配给收银员")
        print("  - 一个角色可以拥有多个功能（例如收银员也可以做上菜）")
        print("  - 不同店铺可以有不同的流程配置")
        
    except Exception as e:
        print(f"\n❌ 迁移失败：{str(e)}")
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()
    
    print("\n" + "=" * 80)
    print("✓ 数据库迁移成功完成！")
    print("=" * 80)


if __name__ == "__main__":
    migrate_database()
