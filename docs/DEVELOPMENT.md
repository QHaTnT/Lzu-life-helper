# 开发指南

## 环境准备

### 必需软件
- Docker 20.10+
- Docker Compose 2.0+
- Git

### 可选软件（本地开发）
- Python 3.9+
- Node.js 18+
- MySQL 8.0
- Redis 7.0

## 快速开始

### 使用Docker（推荐）

```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

### 本地开发

#### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库连接

# 初始化数据库
python init_db.py

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 项目结构

```
backend/
├── app/
│   ├── api/          # API路由
│   │   ├── deps.py   # 依赖注入
│   │   └── v1/       # API v1版本
│   ├── core/         # 核心配置
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── redis.py
│   │   └── security.py
│   ├── models/       # 数据模型
│   ├── schemas/      # Pydantic模型
│   ├── services/     # 业务逻辑
│   ├── utils/        # 工具函数
│   └── main.py       # 应用入口
├── tests/            # 测试用例
├── init_db.py        # 数据库初始化
└── requirements.txt

frontend/
├── src/
│   ├── api/          # API调用
│   ├── components/   # 组件
│   ├── views/        # 页面
│   ├── router/       # 路由
│   ├── store/        # 状态管理
│   ├── App.vue
│   └── main.js
├── public/
├── index.html
└── package.json
```

## API文档

启动服务后访问：http://localhost:8000/docs

## 数据库设计

### 核心表

- **users**: 用户表
- **products**: 二手商品表
- **venues**: 场馆表
- **venue_time_slots**: 场馆时段表
- **bookings**: 预约记录表
- **bus_routes**: 校车路线表
- **bus_schedules**: 校车时刻表
- **posts**: 生活圈动态表
- **activities**: 活动表

## 技术要点

### 后端

#### 密码加密
使用bcrypt进行密码哈希加盐：
```python
from app.core.security import get_password_hash, verify_password

hashed = get_password_hash("password")
is_valid = verify_password("password", hashed)
```

#### JWT认证
```python
from app.core.security import create_access_token

token = create_access_token(data={"sub": user_id})
```

#### Redis分布式锁
场馆预约使用Redis分布式锁防止超卖：
```python
lock_key = f"booking_lock:{time_slot_id}"
lock_acquired = redis_client.set(lock_key, value, nx=True, ex=30)
```

### 前端

#### 状态管理
使用Pinia进行状态管理：
```javascript
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
await authStore.login(credentials)
```

#### API调用
```javascript
import { productAPI } from '@/api'

const products = await productAPI.getProducts({ category: 'books' })
```

## 测试

### 后端测试
```bash
cd backend
pytest
```

### 前端测试
```bash
cd frontend
npm run test
```

## 部署

### Docker部署（推荐）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 生产环境配置

1. 修改`backend/.env`：
   - 设置强密码
   - 配置生产数据库
   - 关闭DEBUG模式

2. 配置HTTPS（使用Nginx + Let's Encrypt）

3. 配置防火墙规则

## 常见问题

### 1. 数据库连接失败
检查MySQL是否启动，端口是否正确

### 2. Redis连接失败
检查Redis是否启动，配置是否正确

### 3. 前端无法访问API
检查CORS配置，确保前端域名在允许列表中

### 4. Docker构建失败
检查网络连接，尝试使用国内镜像源

## Git工作流

### 分支管理
- `main`: 生产环境
- `develop`: 开发环境
- `feature/*`: 功能分支

### 提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

## 联系方式

如有问题，请提交Issue或联系开发团队。
