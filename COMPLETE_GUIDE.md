# 🎯 Docker安装与项目启动 - 完整流程

## 当前状态

✅ **Docker安装包已下载完成**
- 位置：`D:\app\Docker\DockerDesktopInstaller.exe`
- 大小：618 MB
- 状态：安装程序已打开

---

## 📋 完整操作流程（请按顺序执行）

### 步骤1：完成Docker安装（约5分钟）

#### 1.1 在安装向导中操作

Docker Desktop安装窗口应该已经打开，请：

1. **Configuration页面**
   - ✅ 勾选 `Use WSL 2 instead of Hyper-V (recommended)`
   - ✅ 勾选 `Add shortcut to desktop`
   - 点击 `Ok` 开始安装

2. **等待安装**
   - 显示进度条，约2-3分钟
   - 不要关闭窗口

3. **安装完成**
   - 显示 "Installation succeeded"
   - ⚠️ **必须点击 "Close and restart"**
   - ⚠️ **电脑会自动重启**

#### 1.2 如果提示需要WSL 2

如果安装时提示需要WSL 2：

```bash
# 打开PowerShell（管理员），运行：
wsl --install

# 然后重启电脑
# 重启后再次运行：D:\app\Docker\DockerDesktopInstaller.exe
```

---

### 步骤2：重启后启动Docker（约2分钟）

#### 2.1 打开Docker Desktop

重启电脑后：
- 桌面双击 "Docker Desktop" 图标
- 或从开始菜单搜索 "Docker Desktop"

#### 2.2 首次启动配置

1. **服务协议**
   - 如果提示，点击 "Accept" 接受协议

2. **登录（可选）**
   - 可以点击 "Skip" 跳过登录
   - 不需要Docker账号也能使用

3. **等待启动**
   - 等待Docker引擎启动（1-2分钟）
   - 右下角系统托盘出现Docker图标
   - 图标变为**绿色**表示启动成功

---

### 步骤3：验证Docker安装（约1分钟）

打开命令行（CMD或PowerShell）：

```bash
# 检查Docker版本
docker --version
# 应该显示：Docker version 24.x.x, build xxxxx

# 检查Docker Compose版本
docker-compose --version
# 应该显示：Docker Compose version v2.x.x

# 测试Docker运行
docker run hello-world
# 应该显示：Hello from Docker!
```

如果以上命令都正常，说明Docker安装成功！✅

---

### 步骤4：启动项目（约30秒）

#### 4.1 运行启动脚本

```bash
# 进入项目目录
cd D:\可能有用\软件工程\Lzu-life-helper

# 运行启动脚本
start.bat
```

启动脚本会自动：
1. 检测Docker环境
2. 构建Docker镜像
3. 启动所有服务（MySQL、Redis、后端、前端）
4. 初始化数据库

#### 4.2 等待服务启动

首次启动需要约30秒，你会看到：
```
🚀 启动兰州大学生活助手...
✅ Docker已安装并运行
🔨 构建Docker镜像...
🚀 启动服务...
⏳ 等待数据库启动...
📊 初始化数据库...
✅ 启动完成！
```

---

### 步骤5：访问应用

启动完成后，打开浏览器访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端** | http://localhost | Vue 3应用 |
| **后端API** | http://localhost:8000 | FastAPI服务 |
| **API文档** | http://localhost:8000/docs | Swagger UI |

#### 测试账号

| 用户名 | 密码 | 说明 |
|--------|------|------|
| zhangsan | 123456 | 测试用户1 |
| lisi | 123456 | 测试用户2 |

---

## 🎓 功能测试

登录后可以测试以下功能：

### 1. 二手市场
- 浏览商品列表
- 搜索和筛选
- 查看商品详情
- 发布商品（点击右下角+按钮）
- 添加留言

### 2. 场馆预约
- 查看场馆列表
- 查看未来3天可预约时段
- 创建预约
- 查看我的预约

### 3. 校车服务
- 查看校车路线
- 查看时刻表
- 查看座位信息

### 4. 生活圈
- 浏览动态
- 发布动态
- 点赞评论
- 查看活动

---

## 🛠️ 常用命令

### Docker管理

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重新构建并启动
docker-compose up -d --build
```

### 数据库操作

```bash
# 进入MySQL容器
docker-compose exec mysql bash

# 连接MySQL
docker-compose exec mysql mysql -u root -p
# 密码：password

# 重新初始化数据库
docker-compose exec backend python init_db.py
```

---

## 🐛 常见问题

### Q1: Docker Desktop无法启动

**症状**：Docker图标一直是灰色或黄色

**解决方案**：
1. 确保已重启电脑
2. 以管理员身份运行Docker Desktop
3. 检查Windows版本（需要Windows 10 1903+）
4. 检查BIOS中是否启用虚拟化

### Q2: start.bat提示Docker未运行

**解决方案**：
1. 打开Docker Desktop应用
2. 等待右下角图标变绿
3. 重新运行start.bat

### Q3: 端口被占用

**症状**：提示80或8000端口被占用

**解决方案**：
```bash
# 查看端口占用
netstat -ano | findstr :80
netstat -ano | findstr :8000

# 杀死进程
taskkill /PID <进程ID> /F
```

### Q4: 访问localhost无响应

**解决方案**：
1. 检查Docker容器是否运行：`docker-compose ps`
2. 查看日志：`docker-compose logs -f`
3. 重启服务：`docker-compose restart`

### Q5: 数据库连接失败

**解决方案**：
```bash
# 等待MySQL完全启动（约10秒）
# 重新初始化数据库
docker-compose exec backend python init_db.py
```

---

## 📚 文档索引

| 文档 | 位置 | 说明 |
|------|------|------|
| Docker安装指南 | `D:\app\Docker\INSTALL_GUIDE.md` | 详细安装步骤 |
| 项目启动指南 | `START_HERE.md` | 完整启动说明 |
| 快速参考 | `SOLUTION.md` | 问题解决方案 |
| 开发指南 | `docs/DEVELOPMENT.md` | 开发文档 |
| 快速参考手册 | `docs/QUICK_REFERENCE.md` | 常用命令 |
| 项目总结 | `docs/PROJECT_SUMMARY.md` | 技术总结 |

---

## 🎯 时间线总结

| 步骤 | 预计时间 | 状态 |
|------|---------|------|
| 下载Docker | - | ✅ 已完成 |
| 安装Docker | 2-3分钟 | ⏳ 进行中 |
| 重启电脑 | 1-2分钟 | ⏳ 待执行 |
| 启动Docker | 1-2分钟 | ⏳ 待执行 |
| 启动项目 | 30秒 | ⏳ 待执行 |
| **总计** | **约5-10分钟** | - |

---

## 💡 提示

### 如果Docker安装遇到问题

可以使用本地开发环境（无需Docker）：

```bash
# 查看本地开发指南
type docs\LOCAL_SETUP.md

# 使用本地启动脚本
start-local.bat
```

本地开发需要：
- Python 3.9+
- Node.js 18+
- MySQL 8.0
- Redis（可选）

---

## 📞 需要帮助？

1. 查看对应的文档文件
2. 检查错误信息
3. 搜索常见问题解决方案

---

**祝你使用愉快！** 🚀

---

**下一步：完成Docker安装向导，重启电脑，然后运行 start.bat**
