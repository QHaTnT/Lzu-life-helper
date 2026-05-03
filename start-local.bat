@echo off
chcp 65001 >nul
echo ========================================
echo   兰州大学生活助手 - 本地开发启动
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Node.js，请先安装Node.js 18+
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Python和Node.js已安装
echo.

REM 询问是否需要安装MySQL和Redis
echo ⚠️  注意：本地开发需要MySQL和Redis
echo.
echo 选项1: 我已经安装了MySQL和Redis
echo 选项2: 我需要安装指南
echo.
set /p choice="请选择 (1/2): "

if "%choice%"=="2" (
    echo.
    echo 📦 MySQL安装:
    echo   1. 下载MySQL 8.0: https://dev.mysql.com/downloads/mysql/
    echo   2. 安装后创建数据库: CREATE DATABASE lzu_helper;
    echo   3. 创建用户: CREATE USER 'lzu_user'@'localhost' IDENTIFIED BY 'lzu_password';
    echo   4. 授权: GRANT ALL PRIVILEGES ON lzu_helper.* TO 'lzu_user'@'localhost';
    echo.
    echo 📦 Redis安装:
    echo   Windows推荐使用Memurai: https://www.memurai.com/
    echo   或者使用WSL安装Redis
    echo.
    pause
    exit /b 0
)

echo.
echo 🚀 开始启动服务...
echo.

REM 启动后端
echo [1/3] 启动后端服务...
cd /d "%~dp0backend"

REM 检查虚拟环境
if not exist "venv" (
    echo 创建Python虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境并安装依赖
call venv\Scripts\activate.bat

echo 安装Python依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple >nul 2>&1

REM 检查.env文件
if not exist ".env" (
    echo 创建环境配置文件...
    copy .env.example .env
    echo.
    echo ⚠️  请编辑 backend\.env 文件，配置数据库连接信息
    echo.
    pause
)

REM 初始化数据库
echo 初始化数据库...
python init_db.py

REM 启动后端（新窗口）
echo 启动FastAPI服务器...
start "兰大助手-后端" cmd /k "cd /d %~dp0backend && venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

REM 启动前端
echo.
echo [2/3] 启动前端服务...
cd /d "%~dp0frontend"

REM 检查node_modules
if not exist "node_modules" (
    echo 安装Node.js依赖（首次运行需要几分钟）...
    call npm install
)

REM 启动前端（新窗口）
echo 启动Vue开发服务器...
start "兰大助手-前端" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo ✅ 启动完成！
echo ========================================
echo.
echo 访问地址：
echo   前端: http://localhost:5173
echo   后端API: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo.
echo 测试账号：
echo   用户名: zhangsan, 密码: 123456
echo   用户名: lisi, 密码: 123456
echo.
echo 提示：
echo   - 两个命令行窗口会保持打开状态
echo   - 关闭窗口即可停止服务
echo   - 如需重启，再次运行此脚本
echo.
pause
