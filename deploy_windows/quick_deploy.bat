@echo off
chcp 65001
title 餐饮系统 - Windows 云服务器快速部署

echo.
echo ========================================
echo 餐饮系统 - Windows 云服务器快速部署
echo ========================================
echo.
echo 本脚本将帮助你快速部署餐饮系统到 Windows 云服务器
echo.

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [提示] 建议以管理员身份运行此脚本
    echo.
)

:MENU
echo.
echo 请选择操作：
echo.
echo 1. 安装 Python 依赖
echo 2. 初始化数据库
echo 3. 启动后端服务
echo 4. 复制前端文件到宝塔目录
echo 5. 生成配置文件
echo 6. 查看部署状态
echo 7. 全部完成
echo 0. 退出
echo.

set /p choice=请输入选项 (0-7):

if "%choice%"=="1" goto INSTALL_DEPS
if "%choice%"=="2" goto INIT_DB
if "%choice%"=="3" goto START_BACKEND
if "%choice%"=="4" goto COPY_FRONTEND
if "%choice%"=="5" goto GEN_CONFIG
if "%choice%"=="6" goto CHECK_STATUS
if "%choice%"=="7" goto ALL_DONE
if "%choice%"=="0" goto END

echo.
echo [错误] 无效的选项，请重新选择
goto MENU

:INSTALL_DEPS
echo.
echo ========================================
echo 安装 Python 依赖
echo ========================================
echo.
call install_requirements.bat
goto MENU

:INIT_DB
echo.
echo ========================================
echo 初始化数据库
echo ========================================
echo.
if not defined PGDATABASE_URL (
    echo [警告] 未设置 PGDATABASE_URL 环境变量
    echo.
    set /p db_url=请输入数据库连接字符串 (postgresql://user:password@localhost:5432/restaurant_system):
    if defined db_url (
        set PGDATABASE_URL=%db_url%
    ) else (
        echo [错误] 未输入数据库连接字符串
        pause
        goto MENU
    )
)
call init_database.bat
goto MENU

:START_BACKEND
echo.
echo ========================================
echo 启动后端服务
echo ========================================
echo.
if not defined PGDATABASE_URL (
    echo [警告] 未设置 PGDATABASE_URL 环境变量
    echo.
    set /p db_url=请输入数据库连接字符串:
    if defined db_url (
        set PGDATABASE_URL=%db_url%
    ) else (
        echo [错误] 未输入数据库连接字符串
        pause
        goto MENU
    )
)
call start_backend.bat
goto MENU

:COPY_FRONTEND
echo.
echo ========================================
echo 复制前端文件到宝塔目录
echo ========================================
echo.

set /p dest_dir=请输入宝塔网站目录 (默认 C:\wwwroot\restaurant):
if "%dest_dir%"=="" set dest_dir=C:\wwwroot\restaurant

echo.
echo 目标目录: %dest_dir%
echo.

if not exist "%dest_dir%" (
    echo [提示] 目标目录不存在，正在创建...
    mkdir "%dest_dir%"
)

echo.
echo 正在复制文件...
echo.
xcopy /E /I /Y "%~dp0..\assets\*" "%dest_dir%\"

if errorlevel 1 (
    echo.
    echo [错误] 文件复制失败！
) else (
    echo.
    echo [成功] 前端文件已复制到：%dest_dir%
)

echo.
pause
goto MENU

:GEN_CONFIG
echo.
echo ========================================
echo 生成配置文件
echo ========================================
echo.

REM 创建环境变量配置文件
set CONFIG_FILE=%~dp0..\.env.production

echo 正在生成配置文件: %CONFIG_FILE%
echo.

(
echo # 餐饮系统生产环境配置
echo PGDATABASE_URL=postgresql://username:password@localhost:5432/restaurant_system
echo.
echo # 其他配置...
echo SECRET_KEY=your-secret-key-here
echo.
) > "%CONFIG_FILE%"

echo.
echo [成功] 配置文件已创建：%CONFIG_FILE%
echo.
echo 请编辑此文件，设置正确的数据库连接信息
echo.

notepad "%CONFIG_FILE%"

goto MENU

:CHECK_STATUS
echo.
echo ========================================
echo 部署状态检查
echo ========================================
echo.

echo 1. 检查 Python...
python --version
if errorlevel 1 (
    echo [X] Python 未安装
) else (
    echo [OK] Python 已安装
)

echo.
echo 2. 检查依赖包...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo [X] FastAPI 未安装
) else (
    echo [OK] FastAPI 已安装
)

echo.
echo 3. 检查环境变量...
if defined PGDATABASE_URL (
    echo [OK] PGDATABASE_URL 已设置
    echo    值: %PGDATABASE_URL:~0,30%...
) else (
    echo [X] PGDATABASE_URL 未设置
)

echo.
echo 4. 检查后端服务...
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo [X] 后端服务未运行
) else (
    echo [OK] 后端服务正在运行
    curl -s http://localhost:8000/health
)

echo.
echo 5. 检查前端文件...
if exist "C:\wwwroot\restaurant\portal.html" (
    echo [OK] 前端文件已部署
) else (
    echo [X] 前端文件未部署
)

echo.
pause
goto MENU

:ALL_DONE
echo.
echo ========================================
echo 部署完成
echo ========================================
echo.
echo 所有步骤已完成！
echo.
echo 接下来你需要：
echo.
echo 1. 在宝塔面板配置 Nginx 反向代理
echo 2. 访问网站测试功能
echo 3. （可选）配置 SSL 证书
echo.
echo 详细的配置说明，请查看：
echo %~dp0..\WINDOWS_CLOUD_DEPLOYMENT_GUIDE.md
echo.
pause
goto END

:END
echo.
echo 感谢使用餐饮系统！
echo.
