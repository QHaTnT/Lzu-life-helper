# 兰大生活助手

面向兰州大学师生的校园综合服务平台，提供二手市场、场馆预约、校车查询、生活圈、校园活动等功能。

## 功能模块

| 模块 | 功能 |
|------|------|
| 二手市场 | 发布/浏览/搜索二手商品，留言议价，联系卖家 |
| 场馆预约 | 查看可用时段，在线预约体育场馆/自习室 |
| 校车服务 | 查看城关↔榆中校区班次时刻表 |
| 生活圈 | 发布动态（失物招领/吐槽/问答/分享），点赞评论 |
| 校园活动 | 发布/报名校园活动，查看报名名单 |
| 个人中心 | 管理个人信息、我的商品、我的动态、我的活动 |

## 技术栈

- **后端**：FastAPI + SQLAlchemy + SQLite（零配置）
- **前端**：Vue 3 + Vite + Tailwind CSS + Pinia
- **认证**：JWT Token

---

## 快速开始（普通用户 - 推荐）

### 方式一：离线完整包（推荐，开箱即用）

> 适合不想安装任何环境的用户，下载后直接运行

**下载地址**：[百度网盘 / 阿里云盘链接]（待提供）

**使用步骤**：
1. 下载 `兰大助手-完整版.zip`（约 200MB）
2. 解压到任意文件夹，例如 `C:\兰大助手\`
3. 双击 `启动.bat`
4. 等待约 10 秒，浏览器自动打开 http://localhost:5173

**说明**：
- 内置 Python 和 Node.js 运行时，无需安装任何环境
- 每次启动会重置数据库到初始状态（含测试数据）
- 关闭两个黑色窗口即可停止服务

---

### 方式二：自动配置版（需联网）

> 适合有网络的用户，首次运行会自动下载并配置环境

**下载地址**：本项目 GitHub 仓库

**使用步骤**：
1. 点击右上角绿色 `Code` 按钮 → `Download ZIP`
2. 解压到任意文件夹
3. 双击 `setup-and-start.bat`
4. 根据提示选择自动安装 Python 和 Node.js（首次约 3-5 分钟）
5. 安装完成后自动启动，浏览器访问 http://localhost:5173

**说明**：
- 首次运行需要联网下载环境（Python 30MB + Node.js 30MB）
- 后续启动直接双击 `start-local.bat` 即可（秒开）
- 如果下载失败，请使用方式一或手动安装环境后使用方式三

---

### 方式三：手动安装环境（开发者）

> 适合已有 Python/Node.js 环境的开发者

**环境要求**：
- Python 3.9+
- Node.js 18+

**使用步骤**：
1. 克隆或下载项目
2. 双击 `start-local.bat`
3. 脚本会自动安装依赖并启动服务

---

## 测试账号

| 用户名 | 密码 | 备注 |
|--------|------|------|
| zhangsan | 123456 | 普通学生 |
| lisi | 123456 | 普通学生 |
| wangwu | 123456 | 普通学生 |

---

## 开发者指南（团队协作）

### 环境要求

| 工具 | 版本 | 说明 |
|------|------|------|
| Python | 3.9+ | 推荐使用 Anaconda |
| Node.js | 18+ | 附带 npm |
| Git | 任意 | 用于克隆项目 |

### 克隆项目

```bash
git clone https://github.com/QHaTnT/Lzu-life-helper.git
cd Lzu-life-helper
```

### 安装依赖

**后端：**
```bash
cd backend
pip install -r requirements.txt
```

**前端：**
```bash
cd frontend
npm install
```

### 启动服务

**一键启动（推荐）：**
```bash
# Windows
start-local.bat

# Linux/Mac
./start-local.sh  # 需要先创建此脚本
```

**手动启动：**
```bash
# 后端
cd backend
python init_db.py          # 首次或重置数据时执行
python -m uvicorn app.main:app --reload --port 8000

# 前端（新终端）
cd frontend
npm run dev
```

### 访问地址

| 地址 | 说明 |
|------|------|
| http://localhost:5173 | 前端页面 |
| http://localhost:8000/docs | 后端 API 文档（Swagger UI） |
| http://localhost:8000/redoc | 后端 API 文档（ReDoc） |

### 项目结构

```
Lzu-life-helper/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/         # 路由层（products, venues, bus, community, auth...）
│   │   ├── core/           # 配置、数据库、安全、Redis
│   │   ├── models/         # SQLAlchemy 数据模型
│   │   ├── services/       # 业务逻辑层
│   │   └── utils/          # 工具函数（序列化等）
│   ├── uploads/            # 上传文件存储目录（自动创建）
│   ├── init_db.py          # 数据库初始化 + 种子数据
│   └── requirements.txt
├── frontend/                # Vue 3 前端
│   └── src/
│       ├── api/            # API 请求封装
│       ├── components/     # 公共组件（BottomNav 等）
│       ├── store/          # Pinia 状态管理
│       └── views/          # 页面组件
├── setup-and-start.bat      # 自动配置并启动（首次运行）
├── start-local.bat          # 快速启动（已配置环境）
└── README.md
```

### 常见问题

**Q: 启动后端报 `No module named 'xxx'`**  
A: 依赖未安装，执行 `pip install -r requirements.txt`

**Q: 前端报 `Cannot connect to backend`**  
A: 确认后端已启动，访问 http://localhost:8000/docs 检查

**Q: 图片上传失败**  
A: `backend/uploads/` 目录会自动创建，确保后端正常运行

**Q: 数据库出错或想重置数据**  
A: 删除 `backend/lzu_helper.db`，重新运行 `python init_db.py`

**Q: `start-local.bat` 找不到 Python**  
A: 修改脚本第 8 行 `set PYTHON=` 为你的 Python 路径（执行 `where python` 查看）

---

## 功能说明

### 二手市场
- 浏览商品列表，支持分类筛选（电子产品/图书/日用品/运动/服装/其他）
- 搜索商品，价格区间筛选
- 发布商品（标题/描述/价格/分类/图片，最多 9 张）
- 商品详情页查看卖家信息和联系方式
- 留言板与卖家沟通

### 场馆预约
- 查看所有场馆（羽毛球/乒乓球/篮球/自习室等）
- 查看未来 3 天可预约时段
- 在线预约，实时显示剩余名额

### 校车服务
- 查看城关↔榆中校区班次
- 显示发车时间、座位数、是否仅工作日

### 生活圈
- 发布动态（失物招领/吐槽/问答互助/分享/活动/其他）
- 发布校园活动（标题/描述/主办方/地点/时间/人数限制）
- 上传图片（最多 9 张）
- 点赞、评论、浏览数统计

### 个人中心
- 查看和编辑个人信息
- 管理我的商品（删除）
- 管理我的动态（删除）
- 管理我的活动（我报名的/我发布的）

---

## 注意事项

1. **数据持久化**：`start-local.bat` 每次启动会重置数据库。如需保留数据，注释掉脚本中的 `init_db.py` 行
2. **端口占用**：确保 8000 和 5173 端口未被占用
3. **浏览器兼容**：推荐使用 Chrome/Edge/Firefox 最新版
4. **文件上传**：图片大小建议不超过 5MB

---

## 许可证

MIT License
