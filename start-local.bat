@echo off
chcp 65001 >nul
echo ========================================
echo   兰大生活助手 - 一键启动（本地开发）
echo ========================================
echo.

set PYTHON=D:\app\anaconda3\python.exe
set PROJECT=%~dp0

REM 关闭旧的后端/前端进程（避免端口占用）
echo [0/3] 清理旧进程...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq 兰大助手-后端*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq 兰大助手-前端*" >nul 2>&1
timeout /t 1 /nobreak >nul

REM 初始化数据库（每次启动都确保数据库和种子数据存在）
echo [1/3] 初始化数据库...
cd /d "%PROJECT%backend"
set PYTHONIOENCODING=utf-8
%PYTHON% -X utf8 init_db.py
if errorlevel 1 (
    echo 数据库初始化失败，请检查错误信息
    pause
    exit /b 1
)

REM 启动后端（新窗口）
echo [2/3] 启动后端...
start "兰大助手-后端 :8000" cmd /k "chcp 65001 >nul && cd /d %PROJECT%backend && set PYTHONIOENCODING=utf-8 && %PYTHON% -X utf8 -m uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

REM 启动前端（新窗口）
echo [3/3] 启动前端...
if not exist "%PROJECT%frontend\node_modules" (
    echo 首次运行，安装前端依赖（约1分钟）...
    cd /d "%PROJECT%frontend"
    call npm install
)
start "兰大助手-前端 :5173" cmd /k "cd /d %PROJECT%frontend && npm run dev"

echo.
echo ========================================
echo  前端: http://localhost:5173
echo  后端: http://localhost:8000
echo  文档: http://localhost:8000/docs
echo  账号: zhangsan / 123456
echo ========================================
echo.
echo 关闭对应窗口即可停止服务。
pause
