@echo off
chcp 65001 >nul
echo ========================================
echo   兰大生活助手 - 一键启动（本地开发）
echo ========================================
echo.

set PYTHON=D:\app\anaconda3\python.exe
set PROJECT=%~dp0

REM 启动后端（新窗口）
echo [1/2] 启动后端...
start "兰大助手-后端 :8000" cmd /k "chcp 65001 >nul && cd /d %PROJECT%backend && set PYTHONIOENCODING=utf-8 && %PYTHON% -X utf8 -m uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

REM 启动前端（新窗口）
echo [2/2] 启动前端...
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
