# 本地开发环境搭建指南

## 问题诊断

你的系统**没有安装Docker**，所以Docker启动脚本无法运行。

有两种解决方案：

---

## 方案1：安装Docker（推荐）

### 优点
- ✅ 一键启动，无需配置
- ✅ 环境隔离，不影响系统
- ✅ 包含MySQL和Redis

### 安装步骤

#### Windows系统

1. **下载Docker Desktop**
   - 访问：https://www.docker.com/products/docker-desktop/
   - 下载Windows版本

2. **安装Docker Desktop**
   - 双击安装包
   - 按照向导完成安装
   - 重启电脑

3. **启动Docker Desktop**
   - 打开Docker Desktop应用
   - 等待Docker引擎启动（右下角图标变绿）

4. **验证安装**
   ```bash
   docker --version
   docker-compose --version
   ```

5. **运行项目**
   ```bash
   cd D:\可能有用\软件工程\Lzu-life-helper
   start.bat
   ```

---

## 方案2：本地开发环境（无需Docker）

### 需要安装的软件

#### 1. Python 3.9+
- 下载：https://www.python.org/downloads/
- 安装时勾选"Add Python to PATH"

#### 2. Node.js 18+
- 下载：https://nodejs.org/
- 选择LTS版本

#### 3. MySQL 8.0
- 下载：https://dev.mysql.com/downloads/mysql/
- 或使用XAMPP：https://www.apachefriends.org/

**MySQL配置：**
```sql
-- 创建数据库
CREATE DATABASE lzu_helper CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'lzu_user'@'localhost' IDENTIFIED BY 'lzu_password';

-- 授权
GRANT ALL PRIVILEGES ON lzu_helper.* TO 'lzu_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 4. Redis（可选，场馆预约功能需要）

**Windows安装Redis：**

**选项A：使用Memurai（推荐）**
- 下载：https://www.memurai.com/
- 免费的Windows Redis替代品

**选项B：使用WSL**
```bash
# 在WSL中安装Redis
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

**选项C：暂时禁用Redis**
- 修改 `backend/app/core/config.py`
- 注释掉Redis相关代码（场馆预约功能将不可用）

---

### 本地启动步骤

#### 方法1：使用启动脚本（推荐）

```bash
cd D:\可能有用\软件工程\Lzu-life-helper
start-local.bat
```

#### 方法2：手动启动

**1. 配置后端环境变量**
```bash
cd backend
copy .env.example .env
# 编辑.env文件，修改数据库连接信息
```

**2. 启动后端**
```bash
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**3. 启动前端（新命令行窗口）**
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

**4. 访问应用**
- 前端：http://localhost:5173
- 后端：http://localhost:8000
- API文档：http://localhost:8000/docs

---

## 快速对比

| 特性 | Docker方案 | 本地开发方案 |
|------|-----------|-------------|
| 安装难度 | ⭐⭐ | ⭐⭐⭐⭐ |
| 启动速度 | 慢（首次） | 快 |
| 环境隔离 | ✅ 完全隔离 | ❌ 影响系统 |
| 配置复杂度 | ⭐ 简单 | ⭐⭐⭐⭐ 复杂 |
| 适合场景 | 演示、部署 | 开发、调试 |

---

## 推荐方案

### 如果你是：
- **演示项目** → 安装Docker（方案1）
- **开发调试** → 本地环境（方案2）
- **快速测试** → 安装Docker（方案1）

---

## 常见问题

### Q1: Docker Desktop安装失败
**A:**
- 确保Windows版本是Windows 10/11 专业版或企业版
- 家庭版需要先安装WSL2
- 参考：https://docs.docker.com/desktop/install/windows-install/

### Q2: MySQL连接失败
**A:**
```bash
# 检查MySQL是否运行
# Windows: 任务管理器 -> 服务 -> MySQL

# 测试连接
mysql -u lzu_user -p
# 输入密码：lzu_password
```

### Q3: Redis连接失败
**A:**
```bash
# 如果暂时不需要场馆预约功能，可以跳过Redis
# 或者使用Memurai替代
```

### Q4: 端口被占用
**A:**
```bash
# 查看端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# 修改端口
# 后端：backend/app/main.py 修改port参数
# 前端：frontend/vite.config.js 修改server.port
```

---

## 下一步

1. **选择方案**：Docker（推荐）或本地开发
2. **安装软件**：按照上述步骤安装
3. **运行项目**：使用对应的启动脚本
4. **测试功能**：使用测试账号登录

---

**需要帮助？**
- 查看详细错误信息
- 检查软件版本是否符合要求
- 确保所有服务都已启动
