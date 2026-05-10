# 兰大生活助手

面向兰州大学师生的校园综合服务平台，提供二手市场、场馆预约、校车查询、生活圈、校园活动等功能。

## 技术栈

- **后端**：FastAPI + SQLAlchemy + MySQL 8.0 + Redis 7.0
- **前端**：Vue 3 + Vite + Tailwind CSS + Pinia
- **部署**：Docker Compose 四容器编排（MySQL + Redis + Backend + Frontend）

## 功能模块

| 模块 | 功能 |
|------|------|
| 二手市场 | 发布/浏览/搜索商品，留言议价，联系卖家 |
| 场馆预约 | 查看时段，在线预约，Redis 分布式锁防并发 |
| 校车服务 | 查看城关↔榆中校区班次时刻表 |
| 生活圈 | 发布动态/活动，点赞评论，图片上传 |
| 校园活动 | 发布/报名活动，防重复报名 |

---

## 快速启动

### 环境要求

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)（Windows/Mac/Linux）

### 一键启动

```bash
git clone https://github.com/QHaTnT/Lzu-life-helper.git
cd Lzu-life-helper
docker-compose up --build
```

首次启动会自动：
1. 拉取 MySQL 8.0 和 Redis 7.0 镜像
2. 构建后端 Python 镜像并安装依赖
3. 构建前端 Node 镜像并编译生产版本
4. 初始化数据库并写入种子数据

### 访问地址

| 地址 | 说明 |
|------|------|
| http://localhost | 前端页面 |
| http://localhost:8000/docs | Swagger API 文档 |
| http://localhost:8000/redoc | ReDoc API 文档 |

### 测试账号

| 用户名 | 密码 |
|--------|------|
| zhangsan | 123456 |
| lisi | 123456 |
| wangwu | 123456 |
| zhaoliu | 123456 |
| sunqi | 123456 |

### 停止服务

```bash
docker-compose down          # 停止容器
docker-compose down -v       # 停止并删除数据卷（清空数据库）
```

---

## 项目结构

```
Lzu-life-helper/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/            # 路由层
│   │   ├── core/              # 配置、数据库、Redis、安全
│   │   ├── models/            # SQLAlchemy 数据模型（13张表）
│   │   ├── services/          # 业务逻辑层
│   │   └── utils/             # 序列化工具
│   ├── init_db.py             # 数据库初始化 + 种子数据
│   └── requirements.txt
├── frontend/                   # Vue 3 前端
│   └── src/
│       ├── api/               # Axios 请求封装
│       ├── components/        # 公共组件
│       ├── store/             # Pinia 状态管理
│       └── views/             # 13个页面组件
├── deployment/
│   ├── docker/
│   │   ├── Dockerfile.backend
│   │   └── Dockerfile.frontend
│   └── nginx/
│       └── nginx.conf
├── docker-compose.yml
└── README.md
```

## Docker 架构

```
┌──────────────┐     ┌──────────────┐
│   Frontend   │     │   Backend    │
│  Nginx :80   │────▶│  FastAPI     │
│  (Vue SPA)   │     │  :8000       │
└──────────────┘     └──────┬───────┘
                     ┌──────┴───────┐
              ┌──────▼──────┐ ┌─────▼──────┐
              │   MySQL 8.0 │ │ Redis 7.0  │
              │   :3306     │ │  :6379     │
              └─────────────┘ └────────────┘
```

- **Nginx**：托管前端静态文件，反向代理 `/api/` 和 `/uploads/` 到后端
- **FastAPI**：RESTful API，统一响应封装 `{code, msg, data}`
- **MySQL**：主数据库，13张表，SQLAlchemy ORM
- **Redis**：场馆预约分布式锁，防止并发超额预约

## 常见问题

**Q: 端口被占用？**
A: 修改 `docker-compose.yml` 中的端口映射，例如 `"8080:80"`

**Q: 重新初始化数据库？**
A: `docker-compose down -v && docker-compose up --build`

**Q: 查看后端日志？**
A: `docker-compose logs -f backend`
