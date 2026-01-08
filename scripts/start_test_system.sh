#!/bin/bash

# 餐饮点餐系统测试平台 - 启动脚本

echo "========================================"
echo "🍽️  餐饮点餐系统测试平台启动中..."
echo "========================================"

# 检查Python环境
echo "📌 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi
echo "✅ Python环境检查通过"

# 检查依赖
echo "📌 检查必要的Python包..."
python3 -c "import fastapi, uvicorn, sqlalchemy, pydantic, axios" 2>/dev/null || {
    echo "⚠️  部分依赖可能缺失，尝试安装..."
    pip install -q fastapi uvicorn sqlalchemy pydantic
}
echo "✅ 依赖检查通过"

# 启动API服务
echo ""
echo "🚀 启动API服务..."
echo "   - 访问地址: http://localhost:8000"
echo "   - API文档: http://localhost:8000/docs"
echo ""

cd /workspace/projects
python3 scripts/start_restaurant_api.py

echo ""
echo "========================================"
echo "🎉 启动完成！"
echo "========================================"
echo ""
echo "📱 测试页面: assets/restaurant_full_test.html"
echo ""
echo "💡 提示:"
echo "   1. 在浏览器中打开 restaurant_full_test.html"
echo "   2. 切换不同角色进行测试"
echo "   3. 详细说明请参考 assets/TEST_SYSTEM_GUIDE.md"
echo ""
