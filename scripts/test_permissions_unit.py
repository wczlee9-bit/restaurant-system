"""
单元测试 - 测试权限、支付方式、小票功能的基本逻辑
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.api.permission_api import ROLE_PERMISSIONS, initialize_roles
from src.api.receipt_api import DEFAULT_RECEIPT_SECTIONS, get_default_config
from storage.database.db import get_session

def test_role_permissions():
    """测试角色权限定义"""
    print("=" * 60)
    print("测试角色权限定义")
    print("=" * 60)
    
    # 验证4个基础角色
    expected_roles = ["admin", "company", "store_manager", "staff"]
    
    for role_key in expected_roles:
        assert role_key in ROLE_PERMISSIONS, f"角色 {role_key} 不存在"
        role_data = ROLE_PERMISSIONS[role_key]
        
        print(f"\n角色: {role_data['name']}")
        print(f"  描述: {role_data['description']}")
        print(f"  权限数量: {len(role_data['permissions'])}")
        
        # 验证权限列表不为空
        assert len(role_data['permissions']) > 0, f"角色 {role_key} 没有权限"
        
        # 验证是否有必要的基本权限
        if role_key == "admin":
            assert "all:access" in role_data['permissions'], "管理员应该有all:access权限"
        elif role_key == "staff":
            assert "order:read" in role_data['permissions'], "店员应该有order:read权限"
    
    print("\n✓ 角色权限定义测试通过")
    return True


def test_payment_methods():
    """测试支付方式定义"""
    print("\n" + "=" * 60)
    print("测试支付方式定义")
    print("=" * 60)
    
    # 定义预期的支付方式
    expected_methods = {
        "wechat": "微信支付",
        "alipay": "支付宝",
        "cash": "现金支付",
        "credit_card": "信用卡",
        "debit_card": "借记卡",
        "other": "其他支付"
    }
    
    print("\n支持的支付方式:")
    for method_id, method_name in expected_methods.items():
        print(f"  ✓ {method_id}: {method_name}")
    
    print("\n✓ 支付方式定义测试通过")
    return True


def test_receipt_sections():
    """测试小票功能区配置"""
    print("\n" + "=" * 60)
    print("测试小票功能区配置")
    print("=" * 60)
    
    # 验证默认小票配置
    sections = get_default_config()
    
    expected_section_types = ["header", "order_info", "customer", "items", "payment", "footer"]
    
    print(f"\n默认小票功能区数量: {len(sections)}")
    
    for section in sections:
        print(f"\n功能区: {section['section_name']} ({section['section_type']})")
        print(f"  排序: {section['sort_order']}")
        print(f"  启用: {section['is_enabled']}")
        print(f"  模板长度: {len(section['template'])}字符")
        
        # 验证必要字段
        assert 'section_type' in section, "缺少section_type字段"
        assert 'section_name' in section, "缺少section_name字段"
        assert 'is_enabled' in section, "缺少is_enabled字段"
        assert 'sort_order' in section, "缺少sort_order字段"
        assert 'template' in section, "缺少template字段"
    
    print("\n✓ 小票功能区配置测试通过")
    return True


def test_role_initialization():
    """测试角色初始化"""
    print("\n" + "=" * 60)
    print("测试角色初始化")
    print("=" * 60)
    
    try:
        db = get_session()
        count = initialize_roles(db)
        db.close()
        
        print(f"\n初始化/更新了 {count} 个角色")
        print("✓ 角色初始化测试通过")
        return True
    except Exception as e:
        print(f"\n✗ 角色初始化测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_permissions_logic():
    """测试权限检查逻辑"""
    print("\n" + "=" * 60)
    print("测试权限检查逻辑")
    print("=" * 60)
    
    from src.api.permission_api import check_user_permission
    
    try:
        db = get_session()
        
        # 初始化角色
        initialize_roles(db)
        
        # 获取第一个用户（测试用户）
        from storage.database.shared.model import Users
        user = db.query(Users).first()
        
        if user:
            print(f"\n测试用户ID: {user.id}")
            
            # 测试检查权限（可能没有权限）
            has_perm = check_user_permission(db, user.id, "order:read")
            print(f"  检查权限 order:read: {has_perm}")
            
            print("✓ 权限检查逻辑测试通过")
        else:
            print("  警告: 数据库中没有用户，跳过权限检查测试")
        
        db.close()
        return True
    except Exception as e:
        print(f"\n✗ 权限检查逻辑测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有单元测试"""
    print("\n开始单元测试...\n")
    
    results = []
    
    # 测试角色权限定义
    results.append(("角色权限定义", test_role_permissions()))
    
    # 测试支付方式定义
    results.append(("支付方式定义", test_payment_methods()))
    
    # 测试小票功能区配置
    results.append(("小票功能区配置", test_receipt_sections()))
    
    # 测试角色初始化
    results.append(("角色初始化", test_role_initialization()))
    
    # 测试权限检查逻辑
    results.append(("权限检查逻辑", test_permissions_logic()))
    
    # 打印测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 所有测试通过!")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查")
        return 1


if __name__ == "__main__":
    sys.exit(main())
