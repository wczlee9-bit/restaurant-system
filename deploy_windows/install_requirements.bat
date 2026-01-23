@echo off
chcp 65001
echo ========================================
echo 餐饮系统 - 安装 Python 依赖
echo ========================================
echo.

cd /d "%~dp0.."
set PROJECT_DIR=%cd%

echo 当前目录: %PROJECT_DIR%
echo.

echo 检查 Python 版本...
python --version
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo.
echo 开始安装依赖...
echo.

pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-multipart pillow python-dotenv qrcode requests
pip install pandas openpyxl xlsxwriter
pip install passlib[bcrypt] python-jose[cryptography]
pip install httpx websockets

echo.
echo ========================================
echo 依赖安装完成！
echo ========================================
echo.

pause
