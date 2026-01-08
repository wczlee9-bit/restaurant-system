"""
数据库迁移脚本：添加跨店铺结算和第三方积分互通功能

功能：
1. 创建店铺积分结算表 (store_point_settlements)
2. 创建第三方积分协议表 (third_party_point_agreements)
3. 创建积分兑换日志表 (point_exchange_logs)
4. 扩展现有的积分系统，支持跨店铺和第三方积分
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from src.storage.database.shared.model import (
    Base, Stores, Members, PointLogs,
    StorePointSettlements, ThirdPartyPointAgreements, PointExchangeLogs
)
from src.storage.database.db import get_db_url

# 使用数据库连接函数获取 URL
DATABASE_URL = get_db_url()

def migrate_database():
    """执行数据库迁移"""
    print("=" * 80)
    print("开始执行数据库迁移：跨店铺结算和第三方积分互通")
    print("=" * 80)
    
    # 创建数据库引擎
    engine = create_engine(DATABASE_URL, echo=True)
    
    # 创建会话
    SessionLocal = sessionmaker(bind=engine)
    session: Session = SessionLocal()
    
    try:
        # 步骤1：创建新的表
        print("\n[1/4] 创建新的跨店铺结算和第三方积分表...")
        Base.metadata.create_all(bind=engine)
        print("✓ 新表创建完成")
        
        # 步骤2：验证表结构
        print("\n[2/4] 验证表结构...")
        with engine.connect() as conn:
            # 检查 store_point_settlements 表
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'store_point_settlements'
            """))
            if result.scalar() > 0:
                print("  ✓ store_point_settlements 表已创建")
            
            # 检查 third_party_point_agreements 表
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'third_party_point_agreements'
            """))
            if result.scalar() > 0:
                print("  ✓ third_party_point_agreements 表已创建")
            
            # 检查 point_exchange_logs 表
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'point_exchange_logs'
            """))
            if result.scalar() > 0:
                print("  ✓ point_exchange_logs 表已创建")
        
        # 步骤3：获取店铺和会员统计
        print("\n[3/4] 获取系统统计信息...")
        store_count = session.query(Stores).filter(Stores.is_active == True).count()
        member_count = session.query(Members).count()
        
        print(f"  ✓ 活跃店铺数：{store_count}")
        print(f"  ✓ 会员总数：{member_count}")
        
        # 步骤4：打印功能说明
        print("\n[4/4] 功能说明：")
        print("\n1. 跨店铺结算系统 (store_point_settlements)")
        print("   - 记录不同店铺之间的积分流转")
        print("   - 支持会员在一个店铺消费，使用另一个店铺的积分")
        print("   - 追踪积分的来源和去向，便于结算")
        print("\n2. 第三方积分协议 (third_party_point_agreements)")
        print("   - 管理与第三方公司的积分合作协议")
        print("   - 定义积分兑换比例和规则")
        print("   - 支持双向、单向积分互通")
        print("\n3. 积分兑换日志 (point_exchange_logs)")
        print("   - 记录所有第三方积分兑换操作")
        print("   - 追踪兑换状态和错误信息")
        print("   - 支持对账和问题排查")
        
        # 打印使用示例
        print("\n" + "=" * 80)
        print("使用示例：")
        print("=" * 80)
        
        if store_count >= 2:
            print("\n✓ 可以创建跨店铺结算协议（需要至少2个店铺）")
            print("  示例：会员在店铺A消费，使用店铺B的积分")
            print("  - source_store_id: 店铺B（积分来源）")
            print("  - target_store_id: 店铺A（消费店铺）")
            print("  - settlement_rate: 1.0（1:1结算）")
        else:
            print("\n⚠ 需要至少2个店铺才能创建跨店铺结算协议")
            print("  请先创建更多店铺，然后使用 API 创建结算协议")
        
        print("\n✓ 可以创建第三方积分合作协议")
        print("  示例：与'星巴克咖啡'的积分互通")
        print("  - third_party_name: '星巴克咖啡'")
        print("  - exchange_rate: 0.8（1星巴克积分 = 0.8本方积分）")
        print("  - agreement_type: 'bidirectional'（双向互通）")
        
        # 打印下一步操作
        print("\n" + "=" * 80)
        print("下一步操作：")
        print("=" * 80)
        print("1. 使用 API 创建跨店铺结算协议")
        print("   POST /api/settlement/agreements")
        print("2. 使用 API 创建第三方积分合作协议")
        print("   POST /api/settlement/third-party-agreements")
        print("3. 在订单支付时自动计算跨店铺积分结算")
        print("4. 支持顾客使用第三方积分进行支付")
        print("5. 定期查看结算报表和对账")
        
    except Exception as e:
        print(f"\n❌ 迁移失败：{str(e)}")
        import traceback
        traceback.print_exc()
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
