@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║        兰州大学生活助手 - 环境检测与启动向导              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM 检测Docker
echo [1/5] 检测Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未安装或未启动
    set DOCKER_OK=0
) else (
    docker info >nul 2>&1
    if errorlevel 1 (
        echo ❌ Docker未启动
        set DOCKER_OK=0
    ) else (
        echo ✅ Docker已安装并运行
        set DOCKER_OK=1
    )
)

REM 检测Python
echo [2/5] 检测Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装
    set PYTHON_OK=0
) else (
    echo ✅ Python已安装
    set PYTHON_OK=1
)

REM 检测Node.js
echo [3/5] 检测Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js未安装
    set NODE_OK=0
) else (
    echo ✅ Node.js已安装
    set NODE_OK=1
)

REM 检测MySQL
echo [4/5] 检测MySQL...
mysql --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  MySQL未检测到（本地开发需要）
    set MYSQL_OK=0
) else (
    echo ✅ MySQL已安装
    set MYSQL_OK=1
)

REM 检测Redis
echo [5/5] 检测Redis...
redis-cli --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Redis未检测到（场馆预约功能需要）
    set REDIS_OK=0
) else (
    echo ✅ Redis已安装
    set REDIS_OK=1
)

echo.
echo ════════════════════════════════════════════════════════════
echo.

REM 根据检测结果给出建议
if %DOCKER_OK%==1 (
    echo 🎉 推荐方案：使用Docker启动（最简单）
    echo.
    echo 执行命令：
    echo   cd /d "%~dp0"
    echo   docker-compose up -d
    echo.
    set /p confirm="是否现在启动Docker版本？(Y/N): "
    if /i "%confirm%"=="Y" (
        echo.
        echo 🚀 正在启动Docker服务...
        docker-compose up -d
        echo.
        echo ⏳ 等待服务启动（约30秒）...
        timeout /t 30 /nobreak >nul
        echo.
        echo 📊 初始化数据库...
        docker-compose exec backend python init_db.py
        echo.
        echo ✅ 启动完成！
        echo.
        echo 访问地址：
        echo   前端: http://localhost
        echo   后端: http://localhost:8000
        echo   文档: http://localhost:8000/docs
        echo.
        echo 测试账号：zhangsan / 123456
        echo.
        pause
        exit /b 0
    )
) else if %PYTHON_OK%==1 if %NODE_OK%==1 (
    echo 💡 推荐方案：使用本地开发环境
    echo.
    if %MYSQL_OK%==0 (
        echo ⚠️  警告：需要先安装MySQL
        echo    下载地址: https://dev.mysql.com/downloads/mysql/
        echo    或使用XAMPP: https://www.apachefriends.org/
        echo.
    )
    if %REDIS_OK%==0 (
        echo ⚠️  警告：需要安装Redis（可选）
        echo    Windows推荐: https://www.memurai.com/
        echo    或暂时跳过（场馆预约功能不可用）
        echo.
    )
    echo 执行命令：
    echo   start-local.bat
    echo.
    set /p confirm="是否现在启动本地开发版本？(Y/N): "
    if /i "%confirm%"=="Y" (
        call start-local.bat
        exit /b 0
    )
) else (
    echo ❌ 环境不完整，无法启动项目
    echo.
    echo 请选择以下方案之一：
    echo.
    echo 【方案1：安装Docker（推荐）】
    echo   1. 下载Docker Desktop
    echo      https://www.docker.com/products/docker-desktop/
    echo   2. 安装并启动Docker Desktop
    echo   3. 重新运行此脚本
    echo.
    echo 【方案2：安装本地开发环境】
    echo   1. 安装Python 3.9+
    echo      https://www.python.org/downloads/
    echo   2. 安装Node.js 18+
    echo      https://nodejs.org/
    echo   3. 安装MySQL 8.0
    echo      https://dev.mysql.com/downloads/mysql/
    echo   4. 安装Redis（可选）
    echo      https://www.memurai.com/
    echo   5. 重新运行此脚本
    echo.
)

echo ════════════════════════════════════════════════════════════
echo.
echo 📚 详细文档：
echo   - 本地环境搭建: docs\LOCAL_SETUP.md
echo   - 快速参考指南: docs\QUICK_REFERENCE.md
echo   - 开发指南: docs\DEVELOPMENT.md
echo.
pause
