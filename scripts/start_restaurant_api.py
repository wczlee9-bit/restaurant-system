"""
启动餐饮系统API服务
"""
import uvicorn
import sys
import os

# 添加项目路径到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def main():
    print("=" * 60)
    print("🍽️ 多店铺扫码点餐系统 - API服务")
    print("=" * 60)
    print()
    print("服务信息:")
    print("  - 服务地址: http://localhost:8000")
    print("  - API文档: http://localhost:8000/docs")
    print("  - 健康检查: http://localhost:8000/health")
    print()
    print("功能模块:")
    print("  - 顾客端: 扫码点餐、购物车、订单提交")
    print("  - 订单管理: 订单查询、状态更新、小票打印")
    print("  - 厨房制作: 查看待制作订单、更新菜品状态")
    print("  - 传菜管理: 查看待传菜订单、确认上菜")
    print("  - 菜品管理: 菜品增删改查、上下架")
    print("  - 桌号管理: 桌号增删改查、二维码生成")
    print()
    print("=" * 60)
    print("正在启动服务...")
    print("=" * 60)
    print()
    
    # 启动FastAPI应用
    from src.api.restaurant_api import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
