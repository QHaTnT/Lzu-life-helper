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
    echo ✓ 系统已安装 Python
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
echo 请选择安装方式：
echo   [1] 自动下载并安装 Python 3.11（推荐，约 30MB）
echo   [2] 手动安装后重新运行本脚本
echo   [3] 退出
echo.
choice /c 123 /n /m "请输入选项 (1/2/3): "

if errorlevel 3 exit /b
if errorlevel 2 (
    echo.
    echo 请访问 https://www.python.org/downloads/ 下载并安装 Python
    echo 安装时务必勾选 "Add Python to PATH"
    pause
    exit /b
)

echo.
echo 正在下载 Python 嵌入式版本...
mkdir "%PYTHON_EMBEDDED%" 2>nul
powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile '%PROJECT%runtime\python.zip'}"
if errorlevel 1 (
    echo 下载失败，请检查网络连接或手动安装 Python
    pause
    exit /b 1
)

echo 正在解压...
powershell -Command "& {Expand-Archive -Path '%PROJECT%runtime\python.zip' -DestinationPath '%PYTHON_EMBEDDED%' -Force}"
del "%PROJECT%runtime\python.zip"

REM 配置 pip
echo 正在配置 pip...
powershell -Command "& {Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PYTHON_EMBEDDED%\get-pip.py'}"
"%PYTHON_EMBEDDED%\python.exe" "%PYTHON_EMBEDDED%\get-pip.py"

set PYTHON=%PYTHON_EMBEDDED%\python.exe
echo ✓ Python 安装完成

:check_node
REM ============================================================
REM 检查 Node.js
REM ============================================================
echo.
echo [2/2] 检查 Node.js...

where node >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 系统已安装 Node.js
    set NODE=node
    set NPM=npm
    goto :install_deps
)

if exist "%NODE_EMBEDDED%\node.exe" (
    echo ✓ 使用内置 Node.js
    set NODE=%NODE_EMBEDDED%\node.exe
    set NPM=%NODE_EMBEDDED%\npm.cmd
    goto :install_deps
)

echo.
echo ✗ 未检测到 Node.js 环境
echo.
echo 请选择安装方式：
echo   [1] 自动下载并安装 Node.js 20 LTS（推荐，约 30MB）
echo   [2] 手动安装后重新运行本脚本
echo   [3] 退出
echo.
choice /c 123 /n /m "请输入选项 (1/2/3): "

if errorlevel 3 exit /b
if errorlevel 2 (
    echo.
    echo 请访问 https://nodejs.org/ 下载并安装 Node.js LTS 版本
    pause
    exit /b
)

echo.
echo 正在下载 Node.js 便携版...
mkdir "%NODE_EMBEDDED%" 2>nul
powershell -Command "& {Invoke-WebRequest -Uri 'https://nodejs.org/dist/v20.12.2/node-v20.12.2-win-x64.zip' -OutFile '%PROJECT%runtime\node.zip'}"
if errorlevel 1 (
    echo 下载失败，请检查网络连接或手动安装 Node.js
    pause
    exit /b 1
)

echo 正在解压...
powershell -Command "& {Expand-Archive -Path '%PROJECT%runtime\node.zip' -DestinationPath '%PROJECT%runtime' -Force}"
move "%PROJECT%runtime\node-v20.12.2-win-x64" "%NODE_EMBEDDED%"
del "%PROJECT%runtime\node.zip"

set NODE=%NODE_EMBEDDED%\node.exe
set NPM=%NODE_EMBEDDED%\npm.cmd
echo ✓ Node.js 安装完成

:install_deps
REM ============================================================
REM 安装依赖
REM ============================================================
echo.
echo ========================================
echo   正在安装项目依赖...
echo ========================================
echo.

echo [1/2] 安装后端依赖...
cd /d "%PROJECT%backend"
if not exist "%PROJECT%backend\.deps_installed" (
    "%PYTHON%" -m pip install -r requirements.txt --quiet
    if errorlevel 1 (
        echo 后端依赖安装失败
        pause
        exit /b 1
    )
    echo. > .deps_installed
    echo ✓ 后端依赖安装完成
) else (
    echo ✓ 后端依赖已安装（跳过）
)

echo.
echo [2/2] 安装前端依赖...
cd /d "%PROJECT%frontend"
if not exist "%PROJECT%frontend\node_modules" (
    call "%NPM%" install
    if errorlevel 1 (
        echo 前端依赖安装失败
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
    echo 数据库初始化失败
    pause
    exit /b 1
)

REM 启动后端
echo [2/3] 启动后端...
start "兰大助手-后端 :8000" cmd /k "chcp 65001 >nul && cd /d %PROJECT%backend && set PYTHONIOENCODING=utf-8 && %PYTHON% -X utf8 -m uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

REM 启动前端
echo [3/3] 启动前端...
start "兰大助手-前端 :5173" cmd /k "cd /d %PROJECT%frontend && %NPM% run dev"

echo.
echo ========================================
echo  ✓ 启动完成！
echo.
echo  前端: http://localhost:5173
echo  后端: http://localhost:8000
echo  文档: http://localhost:8000/docs
echo.
echo  测试账号: zhangsan / 123456
echo ========================================
echo.
echo 关闭对应窗口即可停止服务。
echo 下次启动可直接双击 start-local.bat（更快）
pause
