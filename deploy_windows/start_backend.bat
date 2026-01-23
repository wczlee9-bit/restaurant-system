@echo off
chcp 65001
echo ========================================
echo 餐饮系统 - 后端服务启动脚本
echo ========================================
echo.

cd /d "%~dp0.."
set PROJECT_DIR=%cd%

echo 当前目录: %PROJECT_DIR%
echo.

REM 检查环境变量
if not defined PGDATABASE_URL (
    echo [警告] 未设置 PGDATABASE_URL 环境变量
    echo.
    echo 请设置数据库连接字符串，例如：
    echo set PGDATABASE_URL=postgresql://user:password@localhost:5432/restaurant_system
    echo.
    pause
    exit /b 1
)

echo 数据库连接: %PGDATABASE_URL%
echo.

echo 启动后端服务...
echo 后端地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.

python -m uvicorn src.api.restaurant_api:app --host 0.0.0.0 --port 8000 --reload

echo.
echo 后端服务已停止
pause
