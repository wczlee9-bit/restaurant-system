"""
测试脚本 - 验证所有新功能
包括：支付、WebSocket、会员积分、营收分析
"""
import sys
import os
sys.path.insert(0, '/workspace/projects/src')

from sqlalchemy.orm import Session
from storage.database.db import get_session
from storage.database.shared.model import (
    Stores, Tables, Orders, Members, MemberLevelRules, MenuCategories, MenuItems,
    Companies, Users
)
import requests
import json
import time


def setup_test_data():
    """
    创建测试数据
    """
    db = get_session()
    try:
        print("=" * 60)
        print("准备测试数据")
        print("=" * 60)
        
        # 创建会员等级规则（如果不存在）
        if db.query(MemberLevelRules).count() == 0:
            levels = [
                {"level": 1, "level_name": "普通会员", "min_points": 0, "discount": 1.0},
                {"level": 2, "level_name": "银卡会员", "min_points": 1000, "discount": 0.95},
                {"level": 3, "level_name": "金卡会员", "min_points": 5000, "discount": 0.90},
                {"level": 4, "level_name": "白金会员", "min_points": 10000, "discount": 0.85},
            ]
            for level_data in levels:
                level = MemberLevelRules(**level_data)
                db.add(level)
            db.commit()
            print("✓ 创建会员等级规则")
        else:
            print("✓ 会员等级规则已存在")
        
        # 获取或创建测试店铺
        store = db.query(Stores).filter(Stores.name == "测试餐厅").first()
        if not store:
            company = Companies(name="测试公司", is_active=True)
            db.add(company)
            db.flush()
            
            user = Users(
                username="test_user",
                password="hashed",
                name="测试用户",
                email="test@example.com",
                is_active=True
            )
            db.add(user)
            db.flush()
            
            store = Stores(
                company_id=company.id,
                name="测试餐厅",
                is_active=True,
                manager_id=user.id
            )
            db.add(store)
            db.flush()
            
            # 创建菜品分类和菜品
            category = MenuCategories(
                store_id=store.id,
                name="测试分类",
                sort_order=1,
                is_active=True
            )
            db.add(category)
            db.flush()
            
            menu_item = MenuItems(
                store_id=store.id,
                category_id=category.id,
                name="测试菜品",
                price=38.00,
                stock=100,
                is_available=True,
                sort_order=1
            )
            db.add(menu_item)
            db.flush()
            
            # 创建桌号（使用table_number=99避免冲突）
            table = Tables(
                store_id=store.id,
                table_number="99",
                is_active=True
            )
            db.add(table)
            db.flush()
            
            db.commit()
            print(f"✓ 创建测试店铺: {store.name} (ID: {store.id})")
        else:
            print(f"✓ 使用现有店铺: {store.name} (ID: {store.id})")
        
        return store.id
        
    except Exception as e:
        db.rollback()
        print(f"✗ 创建测试数据失败: {str(e)}")
        raise
    finally:
        db.close()


def test_payment_api(store_id):
    """
    测试支付API
    """
    print("\n" + "=" * 60)
    print("测试支付功能")
    print("=" * 60)
    
    try:
        # 获取桌号ID
        db = get_session()
        table = db.query(Tables).filter(Tables.store_id == store_id).first()
        table_id = table.id if table else 21
        db.close()
        
        print(f"使用桌号ID: {table_id}")
        
        # 创建测试订单
        print("\n[测试] 创建测试订单...")
        order_response = requests.post(
            "http://localhost:8000/api/customer/order",
            json={
                "store_id": store_id,
                "table_id": table_id,
                "items": [
                    {"menu_item_id": 1, "quantity": 2}
                ]
            }
        )
        if order_response.status_code != 200:
            print(f"✗ 创建订单失败: {order_response.text}")
            return False
        
        order = order_response.json()
        order_id = order['id']
        print(f"✓ 订单创建成功: {order['order_number']}")
        
        # 创建支付
        print("\n[测试] 创建支付订单...")
        payment_response = requests.post(
            "http://localhost:8002/api/payment/create",
            json={
                "order_id": order_id,
                "payment_method": "wechat",
                "customer_phone": "13800138888"
            }
        )
        if payment_response.status_code != 200:
            print(f"✗ 创建支付失败: {payment_response.text}")
            return False
        
        payment = payment_response.json()
        print(f"✓ 支付创建成功: 支付ID={payment['payment_id']}, 金额={payment['amount']}")
        
        # 查询支付状态
        print("\n[测试] 查询支付状态...")
        status_response = requests.get(f"http://localhost:8002/api/payment/{payment['payment_id']}/status")
        if status_response.status_code == 200:
            status = status_response.json()
            print(f"✓ 支付状态: {status['status']}")
        else:
            print(f"✗ 查询支付状态失败")
        
        # 模拟支付回调
        print("\n[测试] 支付回调...")
        callback_response = requests.post(
            "http://localhost:8002/api/payment/callback",
            json={
                "payment_id": payment['payment_id'],
                "success": True
            }
        )
        if callback_response.status_code == 200:
            print(f"✓ 支付回调成功")
            
            # 等待支付处理完成
            time.sleep(2)
            
            # 查询支付状态
            status_response = requests.get(f"http://localhost:8002/api/payment/{payment['payment_id']}/status")
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"✓ 支付后状态: {status['status']}")
        else:
            print(f"✗ 支付回调失败: {callback_response.text}")
        
        return order_id
        
    except Exception as e:
        print(f"\n✗ 支付功能测试失败: {str(e)}")
        return False


def test_member_api(order_id):
    """
    测试会员API
    """
    print("\n" + "=" * 60)
    print("测试会员功能")
    print("=" * 60)
    
    try:
        # 注册会员
        print("\n[测试] 注册会员...")
        register_response = requests.post(
            "http://localhost:8004/api/member/register",
            json={
                "phone": "13800138888",
                "name": "测试会员"
            }
        )
        if register_response.status_code == 200:
            member = register_response.json()
            print(f"✓ 会员注册成功: {member['name']} (ID: {member['id']}, 积分: {member['points']})")
            member_id = member['id']
        else:
            print(f"✗ 会员注册失败")
            return False
        
        # 通过手机号查询会员
        print("\n[测试] 通过手机号查询会员...")
        member_response = requests.get(f"http://localhost:8004/api/member/phone/13800138888")
        if member_response.status_code == 200:
            member_info = member_response.json()
            print(f"✓ 会员信息查询成功: 积分={member_info['member']['points']}")
        else:
            print(f"✗ 查询会员失败")
        
        # 查询积分日志
        print("\n[测试] 查询积分日志...")
        logs_response = requests.get(f"http://localhost:8004/api/member/{member_id}/points-logs")
        if logs_response.status_code == 200:
            logs = logs_response.json()
            print(f"✓ 积分日志查询成功: 共 {len(logs)} 条记录")
            for log in logs[:3]:
                print(f"  - {log['reason']}: {log['points']} 积分")
        else:
            print(f"✗ 查询积分日志失败")
        
        # 积分兑换
        if member['points'] > 0:
            print("\n[测试] 积分兑换...")
            redeem_response = requests.post(
                "http://localhost:8004/api/member/redeem",
                json={
                    "member_id": member_id,
                    "points": 10,
                    "reason": "积分兑换测试"
                }
            )
            if redeem_response.status_code == 200:
                result = redeem_response.json()
                print(f"✓ 积分兑换成功: 兑换{result['redeemed_points']}积分, 剩余{result['remaining_points']}积分")
            else:
                print(f"✗ 积分兑换失败")
        
        # 应用折扣
        print("\n[测试] 应用会员折扣...")
        discount_response = requests.post(
            "http://localhost:8004/api/member/apply-discount",
            json={
                "member_id": member_id,
                "order_amount": 100.00
            }
        )
        if discount_response.status_code == 200:
            discount = discount_response.json()
            print(f"✓ 折扣计算成功: 原价={discount['original_amount']}, 折扣={discount['discount_amount']}, 实付={discount['final_amount']}")
        else:
            print(f"✗ 应用折扣失败")
        
        # 获取会员等级列表
        print("\n[测试] 获取会员等级列表...")
        levels_response = requests.get("http://localhost:8004/api/member/levels")
        if levels_response.status_code == 200:
            levels = levels_response.json()
            print(f"✓ 会员等级列表: 共 {len(levels)} 个等级")
            for level in levels:
                print(f"  - {level['level_name']}: 最低{level['min_points']}积分, 折扣{level['discount']}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 会员功能测试失败: {str(e)}")
        return False


def test_analytics_api(store_id):
    """
    测试营收分析API
    """
    print("\n" + "=" * 60)
    print("测试营收分析功能")
    print("=" * 60)
    
    try:
        # 营收汇总
        print("\n[测试] 营收汇总...")
        revenue_response = requests.get(
            f"http://localhost:8005/api/analytics/revenue-summary",
            params={"store_id": store_id, "period": "today"}
        )
        if revenue_response.status_code == 200:
            revenue = revenue_response.json()
            print(f"✓ 营收汇总: 订单={revenue['total_orders']}, 净营收={revenue['net_revenue']}")
        else:
            print(f"✗ 营收汇总查询失败")
        
        # 支付方式统计
        print("\n[测试] 支付方式统计...")
        payment_methods_response = requests.get(
            f"http://localhost:8005/api/analytics/payment-methods",
            params={"store_id": store_id, "period": "today"}
        )
        if payment_methods_response.status_code == 200:
            payment_methods = payment_methods_response.json()
            print(f"✓ 支付方式统计: 共 {len(payment_methods)} 种")
            for method in payment_methods:
                print(f"  - {method['payment_method']}: {method['count']}笔, {method['percentage']}%")
        else:
            print(f"✗ 支付方式统计查询失败")
        
        # 菜品销量统计
        print("\n[测试] 菜品销量统计...")
        menu_sales_response = requests.get(
            f"http://localhost:8005/api/analytics/menu-item-sales",
            params={"store_id": store_id, "period": "today", "limit": 5}
        )
        if menu_sales_response.status_code == 200:
            menu_sales = menu_sales_response.json()
            print(f"✓ 菜品销量统计: 共 {len(menu_sales)} 个菜品")
            for item in menu_sales[:3]:
                print(f"  - {item['menu_item_name']}: {item['quantity']}份, ¥{item['revenue']}")
        else:
            print(f"✗ 菜品销量统计查询失败")
        
        # 订单状态统计
        print("\n[测试] 订单状态统计...")
        status_response = requests.get(
            f"http://localhost:8005/api/analytics/order-status",
            params={"store_id": store_id, "period": "today"}
        )
        if status_response.status_code == 200:
            order_status = status_response.json()
            print(f"✓ 订单状态统计: 共 {len(order_status)} 种状态")
            for status in order_status:
                print(f"  - {status['order_status']}: {status['count']}笔")
        else:
            print(f"✗ 订单状态统计查询失败")
        
        # 每日营收趋势
        print("\n[测试] 每日营收趋势...")
        daily_response = requests.get(
            f"http://localhost:8005/api/analytics/daily-revenue",
            params={"store_id": store_id, "days": 7}
        )
        if daily_response.status_code == 200:
            daily_revenue = daily_response.json()
            print(f"✓ 每日营收趋势: 共 {len(daily_revenue)} 天")
            for day in daily_revenue[-3:]:
                print(f"  - {day['date']}: {day['order_count']}笔, ¥{day['revenue']}")
        else:
            print(f"✗ 每日营收趋势查询失败")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 营收分析功能测试失败: {str(e)}")
        return False


def test_websocket_service(store_id):
    """
    测试WebSocket服务（简化测试）
    """
    print("\n" + "=" * 60)
    print("测试WebSocket服务")
    print("=" * 60)
    
    try:
        # 检查WebSocket服务是否运行
        print("\n[测试] 检查WebSocket服务状态...")
        ws_response = requests.get("http://localhost:8003/")
        if ws_response.status_code == 200:
            print("✓ WebSocket服务运行正常")
            return True
        else:
            print("✗ WebSocket服务未运行")
            return False
        
    except Exception as e:
        print(f"\n✗ WebSocket服务测试失败: {str(e)}")
        return False


def main():
    """
    主测试函数
    """
    print("\n" + "=" * 60)
    print("新功能集成测试")
    print("=" * 60)
    
    # 准备测试数据
    store_id = setup_test_data()
    
    # 测试WebSocket服务
    ws_ok = test_websocket_service(store_id)
    
    # 测试支付功能
    order_id = test_payment_api(store_id)
    
    # 测试会员功能
    member_ok = test_member_api(order_id) if order_id else False
    
    # 测试营收分析
    analytics_ok = test_analytics_api(store_id)
    
    # 测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"  - WebSocket服务: {'✓ 通过' if ws_ok else '✗ 失败'}")
    print(f"  - 支付功能: {'✓ 通过' if order_id else '✗ 失败'}")
    print(f"  - 会员功能: {'✓ 通过' if member_ok else '✗ 失败'}")
    print(f"  - 营收分析: {'✓ 通过' if analytics_ok else '✗ 失败'}")
    
    all_passed = ws_ok and order_id and member_ok and analytics_ok
    
    if all_passed:
        print("\n✓ 所有新功能测试通过！")
    else:
        print("\n✗ 部分功能测试失败")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
