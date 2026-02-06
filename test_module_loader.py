"""
测试模块加载器
验证模块化架构是否正常工作
"""

import sys
import logging
from pathlib import Path

# 添加项目根目录到 Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.module_loader import ModuleLoader

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_module_loader():
    """测试模块加载器"""
    
    print("=" * 60)
    print("测试模块加载器")
    print("=" * 60)
    
    try:
        # 创建模块加载器
        loader = ModuleLoader()
        
        # 加载配置
        print("\n[1] 加载模块配置...")
        config = loader.load_config()
        print(f"✅ 配置加载成功，共 {len(config.get('modules', []))} 个模块")
        
        # 加载所有模块
        print("\n[2] 加载所有模块...")
        registry = loader.load_modules()
        print(f"✅ 模块加载成功")
        
        # 初始化所有模块
        print("\n[3] 初始化所有模块...")
        success = loader.initialize_all()
        if success:
            print("✅ 所有模块初始化成功")
        else:
            print("❌ 部分模块初始化失败")
            return False
        
        # 显示已加载模块
        print("\n[4] 已加载模块列表:")
        all_modules = registry.get_all_modules()
        for name, module in sorted(all_modules.items()):
            status = "✅" if module.health_check().get('status') == 'healthy' else "❌"
            print(f"  {status} {name} v{module.version}")
        
        # 健康检查
        print("\n[5] 执行健康检查...")
        health = registry.health_check()
        print(f"整体状态: {health['overall_status']}")
        
        # 获取所有路由
        print("\n[6] 获取所有路由...")
        routes = registry.get_all_routes()
        print(f"✅ 共 {len(routes)} 个路由")
        
        for i, router in enumerate(routes[:5], 1):  # 只显示前5个
            if hasattr(router, 'prefix'):
                print(f"  {i}. {router.prefix}")
            elif hasattr(router, 'routes'):
                print(f"  {i}. {len(router.routes)} routes")
        
        if len(routes) > 5:
            print(f"  ... 还有 {len(routes) - 5} 个路由")
        
        # 关闭所有模块
        print("\n[7] 关闭所有模块...")
        loader.shutdown_all()
        print("✅ 所有模块已关闭")
        
        print("\n" + "=" * 60)
        print("✅ 模块加载器测试通过！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 模块加载器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_module_loader()
    sys.exit(0 if success else 1)
