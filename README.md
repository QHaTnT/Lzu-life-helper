# 兰州大学生活助手

## 项目简介

兰州大学生活助手是一个面向兰州大学师生的综合服务平台，提供二手市场、场馆预约、便捷出行、社团活动等功能。

## 技术栈

### 后端
- **框架**: FastAPI (Python 3.9+)
- **数据库**: MySQL 8.0
- **缓存**: Redis 7.0
- **ORM**: SQLAlchemy + SQLModel
- **认证**: JWT

### 前端
- **框架**: Vue 3 + Vite
- **UI**: Tailwind CSS
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP**: Axios

### 部署
- **容器化**: Docker + Docker Compose
- **Web服务器**: Nginx
- **架构支持**: ARM64 (华为鲲鹏/openEuler)

## 核心功能

1. **用户模块**: 校园统一身份认证、密码加密存储
2. **二手市场**: 商品发布、图片上传、分类检索、留言互动
3. **场馆预约**: 实时空闲查询、Redis分布式锁防超卖
4. **便捷出行**: 校车时刻表、座位预订
5. **生活圈**: 动态发布、标签分类、活动报名

## 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+

### 启动服务

```bash
# 克隆项目
git clone https://github.com/QHaTnT/Lzu-life-helper.git
cd Lzu-life-helper

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

访问地址：
- 前端: http://localhost:80
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 项目结构

```
.
├── backend/              # 后端服务
│   ├── app/
│   │   ├── api/         # API路由
│   │   ├── core/        # 核心配置
│   │   ├── models/      # 数据模型
│   │   ├── schemas/     # Pydantic模型
│   │   ├── services/    # 业务逻辑
│   │   └── utils/       # 工具函数
│   └── tests/           # 测试用例
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── components/  # 组件
│   │   ├── views/       # 页面
│   │   ├── router/      # 路由
│   │   ├── store/       # 状态管理
│   │   └── api/         # API调用
│   └── public/          # 静态资源
├── deployment/          # 部署配置
│   ├── docker/          # Dockerfile
│   └── nginx/           # Nginx配置
└── docs/                # 文档

```

## 开发指南

### 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

## Git 分支管理

- `main`: 生产环境分支
- `develop`: 开发分支
- `feature/*`: 功能分支

## 许可证

MIT License
