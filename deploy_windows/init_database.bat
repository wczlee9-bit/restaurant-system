@echo off
chcp 65001
echo ========================================
echo 餐饮系统 - 数据库初始化脚本
echo ========================================
echo.

cd /d "%~dp0.."
set PROJECT_DIR=%cd%

echo 当前目录: %PROJECT_DIR%
echo.

REM 检查环境变量
if not defined PGDATABASE_URL (
    echo [错误] 未设置 PGDATABASE_URL 环境变量
    echo.
    echo 请先设置数据库连接字符串：
    echo set PGDATABASE_URL=postgresql://user:password@localhost:5432/restaurant_system
    echo.
    pause
    exit /b 1
)

echo 数据库连接: %PGDATABASE_URL%
echo.

echo 开始初始化数据库...
echo.

REM 运行初始化脚本
python src/storage/database/init_db.py

if errorlevel 1 (
    echo.
    echo [错误] 数据库初始化失败！
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo 数据库初始化完成！
echo ========================================
echo.
echo 数据已创建：
echo - 60 个菜品
echo - 43 个桌号
echo - 4 个公司
echo - 5 个店铺
echo.

pause
