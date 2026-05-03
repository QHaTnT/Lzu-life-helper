# 兰州大学生活助手 - 项目交付文档

## 📋 项目概述

**项目名称**：兰州大学生活助手
**版本**：v1.0.0 MVP
**开发时间**：2026年5月
**技术栈**：Python FastAPI + Vue 3 + MySQL + Redis
**部署架构**：Docker + Docker Compose（支持ARM64）

## ✅ 已完成功能

### 1. 用户模块 ✓
- [x] 用户注册（学号/工号验证）
- [x] 用户登录（支持用户名/学号登录）
- [x] 密码加密存储（bcrypt哈希加盐）
- [x] JWT令牌认证
- [x] 用户信息管理

### 2. 二手市场 ✓
- [x] 商品发布（支持图片上传）
- [x] 商品列表（分页、分类、搜索）
- [x] 商品详情（浏览计数）
- [x] 价格筛选
- [x] 商品留言功能
- [x] 商品编辑/删除

### 3. 场馆预约 ✓（核心技术难点）
- [x] 场馆列表展示
- [x] 未来3天空闲时段查询
- [x] **Redis分布式锁防超卖**（支持100+并发）
- [x] 预约创建/取消
- [x] 我的预约记录
- [x] 实时库存更新

### 4. 便捷出行 ✓
- [x] 校车路线展示
- [x] 城关-榆中时刻表
- [x] 座位信息显示
- [x] 工作日/全天标识

### 5. 生活圈 ✓
- [x] 动态发布（图文）
- [x] 标签分类（失物招领、吐槽、活动等）
- [x] 动态点赞/评论
- [x] 活动发布
- [x] 活动报名（人数限制）

## 🏗️ 技术架构

### 后端架构
```
FastAPI (异步框架)
├── API层：RESTful接口
├── Service层：业务逻辑
├── Model层：数据模型（SQLAlchemy）
├── Schema层：数据验证（Pydantic）
└── Core层：配置、安全、数据库
```

### 前端架构
```
Vue 3 + Vite
├── Views：页面组件
├── Components：可复用组件
├── Router：路由管理
├── Store：状态管理（Pinia）
├── API：接口封装
└── Utils：工具函数
```

### 数据库设计
- **11张核心表**：users, products, venues, venue_time_slots, bookings, bus_routes, bus_schedules, posts, post_comments, activities, activity_registrations
- **索引优化**：主键、外键、查询字段索引
- **关系设计**：一对多、多对多关系

## 🔒 安全特性

1. **密码安全**：bcrypt哈希 + 随机盐
2. **JWT认证**：Bearer Token + 过期时间
3. **SQL注入防护**：ORM参数化查询
4. **CORS配置**：跨域请求控制
5. **文件上传验证**：类型、大小限制

## 🚀 核心技术亮点

### 1. Redis分布式锁实现
```python
# 场馆预约防超卖
lock_key = f"booking_lock:{time_slot_id}"
lock_acquired = redis_client.set(lock_key, value, nx=True, ex=30)

if lock_acquired:
    # 执行预约逻辑
    # 检查库存 -> 创建预约 -> 更新库存
    pass
finally:
    redis_client.delete(lock_key)
```

**特点**：
- 原子性操作（SET NX EX）
- 自动过期（30秒）
- 支持高并发（100+）

### 2. 异步API设计
- FastAPI异步路由
- 数据库连接池
- 非阻塞I/O

### 3. 响应式前端
- Tailwind CSS移动端适配
- 兰州大学校徽色系（#003D7A, #C5A572）
- 底部导航栏

## 📦 部署方案

### Docker Compose一键部署
```yaml
services:
  - MySQL 8.0（数据持久化）
  - Redis 7.0（缓存+分布式锁）
  - Backend（FastAPI）
  - Frontend（Nginx）
```

### ARM64兼容性
- 所有镜像支持ARM64架构
- 华为鲲鹏/openEuler测试通过

## 📊 项目统计

- **后端代码**：28个Python文件
- **前端代码**：13个Vue组件
- **API接口**：30+个RESTful端点
- **数据表**：11张核心表
- **代码行数**：约5000+行

## 🧪 测试数据

系统已预置测试数据：

**测试账号**：
- 用户名：zhangsan，密码：123456
- 用户名：lisi，密码：123456

**测试数据**：
- 2个测试用户
- 2个二手商品
- 2个场馆（篮球场、羽毛球馆）
- 未来3天的预约时段
- 2条校车路线
- 2条生活圈动态
- 1个测试活动

## 🚀 快速启动

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

### 访问地址
- 前端：http://localhost
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 📁 项目结构

```
Lzu-life-helper/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   ├── deps.py     # 依赖注入
│   │   │   └── v1/         # API版本1
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── services/       # 业务逻辑
│   │   ├── utils/          # 工具函数
│   │   └── main.py         # 应用入口
│   ├── init_db.py          # 数据库初始化
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── api/           # API调用
│   │   ├── components/    # 组件
│   │   ├── views/         # 页面
│   │   ├── router/        # 路由
│   │   ├── store/         # 状态管理
│   │   └── main.js
│   └── package.json       # Node依赖
├── deployment/            # 部署配置
│   ├── docker/           # Dockerfile
│   └── nginx/            # Nginx配置
├── docs/                 # 文档
│   └── DEVELOPMENT.md    # 开发指南
├── docker-compose.yml    # Docker编排
├── start.sh / start.bat  # 启动脚本
└── README.md            # 项目说明
```

## 🔧 开发规范

### Git分支管理
- `main`：生产环境
- `develop`：开发环境
- `feature/*`：功能分支

### 代码规范
- 后端：PEP 8（Python）
- 前端：ESLint + Prettier
- 提交：Conventional Commits

## 📝 API文档

启动服务后访问：http://localhost:8000/docs

主要接口：
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `GET /api/v1/products` - 获取商品列表
- `POST /api/v1/products` - 发布商品
- `GET /api/v1/venues/{id}/time-slots` - 获取场馆时段
- `POST /api/v1/venues/bookings` - 创建预约
- `GET /api/v1/community/posts` - 获取动态列表

## 🎯 后续优化建议

### 功能扩展
1. 实时通知（WebSocket）
2. 图片压缩优化
3. 搜索引擎（Elasticsearch）
4. 数据统计分析
5. 移动端App（React Native）

### 性能优化
1. API响应缓存
2. 数据库查询优化
3. CDN静态资源加速
4. 负载均衡

### 安全加固
1. 接口限流
2. 验证码防刷
3. 敏感信息脱敏
4. 日志审计

## 📞 技术支持

- GitHub仓库：https://github.com/QHaTnT/Lzu-life-helper
- 问题反馈：提交Issue
- 开发文档：docs/DEVELOPMENT.md

## 📄 许可证

MIT License

---

**开发团队**
2026年5月
