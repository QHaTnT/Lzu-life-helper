@echo off
chcp 65001 >nul
title 兰大生活助手 - 自动配置与启动
color 0A

echo.
echo ========================================
echo   兰大生活助手 - 自动配置与启动
echo ========================================
echo.
echo 正在检查运行环境...
echo.

set PROJECT=%~dp0
set PYTHON_EMBEDDED=%PROJECT%runtime\python
set NODE_EMBEDDED=%PROJECT%runtime\node

REM ============================================================
REM 检查 Python
REM ============================================================
echo [1/2] 检查 Python...

where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo ✓ 系统已安装 %%i
    set PYTHON=python
    goto :check_node
)

if exist "%PYTHON_EMBEDDED%\python.exe" (
    echo ✓ 使用内置 Python
    set PYTHON=%PYTHON_EMBEDDED%\python.exe
    goto :check_node
)

echo.
echo ✗ 未检测到 Python 环境
echo.
echo 正在自动下载 Python 3.11 安装包（约 25MB）...
echo 请稍候，下载速度取决于网络状况...
echo.

mkdir "%PROJECT%runtime" 2>nul
powershell -Command "& { $ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%PROJECT%runtime\python_installer.exe' }"
if errorlevel 1 (
    echo.
    echo 下载失败！请手动安装 Python：
    echo   1. 访问 https://www.python.org/downloads/
    echo   2. 下载并安装 Python 3.11
    echo   3. 安装时务必勾选 "Add Python to PATH"
    echo   4. 安装完成后重新运行本脚本
    pause
    exit /b 1
)

echo 正在安装 Python（静默安装，无需操作）...
"%PROJECT%runtime\python_installer.exe" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0 Include_doc=0
if errorlevel 1 (
    echo.
    echo 静默安装失败，正在尝试手动安装模式...
    "%PROJECT%runtime\python_installer.exe"
)
del "%PROJECT%runtime\python_installer.exe" 2>nul

REM 刷新 PATH
call refreshenv 2>nul
set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Python 安装后仍未找到，请重启本脚本或手动安装。
    pause
    exit /b 1
)
set PYTHON=python
echo ✓ Python 安装完成

:check_node
REM ============================================================
REM 检查 Node.js
REM ============================================================
echo.
echo [2/2] 检查 Node.js...

where node >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do echo ✓ 系统已安装 Node.js %%i
    set NPM=npm
    goto :install_deps
)

if exist "%NODE_EMBEDDED%\node.exe" (
    echo ✓ 使用内置 Node.js
    set "PATH=%NODE_EMBEDDED%;%PATH%"
    set NPM=npm
    goto :install_deps
)

echo.
echo ✗ 未检测到 Node.js 环境
echo.
echo 正在自动下载 Node.js 20 LTS 便携版（约 30MB）...
echo 请稍候，下载速度取决于网络状况...
echo.

mkdir "%PROJECT%runtime" 2>nul
powershell -Command "& { $ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.12.2/node-v20.12.2-win-x64.zip' -OutFile '%PROJECT%runtime\node.zip' }"
if errorlevel 1 (
    echo.
    echo 下载失败！请手动安装 Node.js：
    echo   1. 访问 https://nodejs.org/
    echo   2. 下载并安装 Node.js LTS 版本
    echo   3. 安装完成后重新运行本脚本
    pause
    exit /b 1
)

echo 正在解压 Node.js...
powershell -Command "& { $ProgressPreference='SilentlyContinue'; Expand-Archive -Path '%PROJECT%runtime\node.zip' -DestinationPath '%PROJECT%runtime\node_tmp' -Force }"
for /d %%i in ("%PROJECT%runtime\node_tmp\node-*") do move "%%i" "%NODE_EMBEDDED%" >nul
rmdir "%PROJECT%runtime\node_tmp" 2>nul
del "%PROJECT%runtime\node.zip" 2>nul

set "PATH=%NODE_EMBEDDED%;%PATH%"
set NPM=npm
echo ✓ Node.js 安装完成

:install_deps
REM ============================================================
REM 安装依赖
REM ============================================================
echo.
echo ========================================
echo   正在安装项目依赖（首次约需 3-5 分钟）
echo ========================================
echo.

echo [1/2] 安装后端依赖...
cd /d "%PROJECT%backend"
if not exist ".deps_installed" (
    "%PYTHON%" -m pip install -r requirements.txt -q --no-warn-script-location
    if errorlevel 1 (
        echo.
        echo 后端依赖安装失败，请检查网络连接后重试。
        pause
        exit /b 1
    )
    echo installed > .deps_installed
    echo ✓ 后端依赖安装完成
) else (
    echo ✓ 后端依赖已安装（跳过）
)

echo.
echo [2/2] 安装前端依赖...
cd /d "%PROJECT%frontend"
if not exist "node_modules" (
    call %NPM% install --loglevel=error
    if errorlevel 1 (
        echo.
        echo 前端依赖安装失败，请检查网络连接后重试。
        pause
        exit /b 1
    )
    echo ✓ 前端依赖安装完成
) else (
    echo ✓ 前端依赖已安装（跳过）
)

REM ============================================================
REM 启动服务
REM ============================================================
echo.
echo ========================================
echo   正在启动服务...
echo ========================================
echo.

REM 关闭旧进程
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq 兰大助手-后端*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq 兰大助手-前端*" >nul 2>&1
timeout /t 1 /nobreak >nul

REM 初始化数据库
echo [1/3] 初始化数据库...
cd /d "%PROJECT%backend"
set PYTHONIOENCODING=utf-8
"%PYTHON%" -X utf8 init_db.py
if errorlevel 1 (
    echo 数据库初始化失败，请查看上方错误信息。
    pause
    exit /b 1
)

REM 启动后端
echo [2/3] 启动后端服务...
start "兰大助手-后端 :8000" cmd /k "chcp 65001 >nul && cd /d %PROJECT%backend && set PYTHONIOENCODING=utf-8 && %PYTHON% -X utf8 -m uvicorn app.main:app --reload --port 8000"

REM 等待后端就绪
echo 等待后端启动...
timeout /t 4 /nobreak >nul

REM 启动前端
echo [3/3] 启动前端服务...
start "兰大助手-前端 :5173" cmd /k "cd /d %PROJECT%frontend && %NPM% run dev"

REM 等待前端编译
echo 等待前端编译（约 10 秒）...
timeout /t 10 /nobreak >nul

REM 自动打开浏览器
echo 正在打开浏览器...
start "" "http://localhost:5173"

echo.
echo ========================================
echo  ✓ 启动完成！浏览器已自动打开
echo.
echo  如浏览器未打开，请手动访问：
echo  http://localhost:5173
echo.
echo  测试账号：zhangsan  密码：123456
echo ========================================
echo.
echo 使用说明：
echo  - 不要关闭"兰大助手-后端"和"兰大助手-前端"两个黑色窗口
echo  - 关闭这两个窗口即可停止服务
echo  - 下次启动直接双击 start-local.bat（更快）
echo.
pause
