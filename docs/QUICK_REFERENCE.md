# 快速参考指南

## 🚀 一键启动

### Windows
```bash
cd D:\可能有用\软件工程\Lzu-life-helper
start.bat
```

### Linux/Mac
```bash
cd /path/to/Lzu-life-helper
chmod +x start.sh
./start.sh
```

## 🔑 测试账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| zhangsan | 123456 | 学生 |
| lisi | 123456 | 学生 |

## 🌐 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost | Vue 3应用 |
| 后端API | http://localhost:8000 | FastAPI服务 |
| API文档 | http://localhost:8000/docs | Swagger UI |
| MySQL | localhost:3306 | 数据库 |
| Redis | localhost:6379 | 缓存 |

## 📱 功能模块

### 1. 二手市场
- 发布商品：点击右下角"+"按钮
- 搜索商品：顶部搜索框
- 筛选分类：分类标签
- 查看详情：点击商品卡片
- 留言互动：商品详情页底部

### 2. 场馆预约
- 选择场馆：点击场馆卡片
- 查看时段：显示未来3天可预约时段
- 立即预约：点击"预约"按钮
- 查看记录：个人中心-我的预约

### 3. 校车服务
- 查看路线：显示所有校车路线
- 时刻表：点击"查看时刻"
- 座位信息：显示剩余座位数

### 4. 生活圈
- 发布动态：点击右下角"+"按钮
- 分类浏览：顶部分类标签
- 点赞评论：动态详情页
- 活动报名：活动列表

## 🛠️ 常用命令

### Docker管理
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 查看状态
docker-compose ps

# 进入容器
docker-compose exec backend bash
docker-compose exec mysql bash
```

### 数据库操作
```bash
# 初始化数据库
docker-compose exec backend python init_db.py

# 连接MySQL
docker-compose exec mysql mysql -u root -p
# 密码：password

# 备份数据库
docker-compose exec mysql mysqldump -u root -p lzu_helper > backup.sql

# 恢复数据库
docker-compose exec -T mysql mysql -u root -p lzu_helper < backup.sql
```

### 本地开发

#### 后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### 前端
```bash
cd frontend
npm install
npm run dev
```

## 🔧 配置文件

### 后端环境变量 (backend/.env)
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/lzu_helper
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DEBUG=True
```

### 前端代理配置 (frontend/vite.config.js)
```javascript
server: {
  proxy: {
    '/api': 'http://localhost:8000',
    '/uploads': 'http://localhost:8000',
  }
}
```

## 📊 数据库表结构

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| users | 用户表 | student_id, username, hashed_password |
| products | 商品表 | title, price, category, seller_id |
| venues | 场馆表 | name, venue_type, capacity |
| venue_time_slots | 时段表 | venue_id, date, start_time, capacity |
| bookings | 预约表 | user_id, time_slot_id, status |
| bus_routes | 路线表 | name, from_campus, to_campus |
| bus_schedules | 时刻表 | route_id, departure_time, seats |
| posts | 动态表 | author_id, content, category |
| activities | 活动表 | title, start_time, max_participants |

## 🐛 常见问题

### 1. 端口被占用
```bash
# Windows查看端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :3306

# 杀死进程
taskkill /PID <进程ID> /F

# Linux查看端口占用
lsof -i :8000
kill -9 <进程ID>
```

### 2. Docker启动失败
```bash
# 清理Docker资源
docker-compose down -v
docker system prune -a

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

### 3. 数据库连接失败
- 检查MySQL容器是否启动：`docker-compose ps`
- 查看MySQL日志：`docker-compose logs mysql`
- 等待MySQL完全启动（约10秒）

### 4. 前端无法访问API
- 检查CORS配置
- 确认后端服务运行正常
- 检查浏览器控制台错误

### 5. Redis连接失败
- 检查Redis容器状态
- 验证Redis配置
- 测试连接：`docker-compose exec redis redis-cli ping`

## 📝 API测试示例

### 用户注册
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "320200003",
    "username": "wangwu",
    "password": "123456",
    "real_name": "王五"
  }'
```

### 用户登录
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "zhangsan",
    "password": "123456"
  }'
```

### 获取商品列表
```bash
curl http://localhost:8000/api/v1/products?category=books
```

### 创建预约（需要Token）
```bash
curl -X POST http://localhost:8000/api/v1/venues/bookings \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"time_slot_id": 1}'
```

## 🎨 UI色彩规范

| 颜色名称 | 色值 | 用途 |
|---------|------|------|
| 兰大蓝 | #003D7A | 主色调、按钮、导航 |
| 兰大金 | #C5A572 | 强调色、图标 |
| 浅蓝 | #E8F4F8 | 背景、标签 |

## 📚 相关文档

- [项目总结](./PROJECT_SUMMARY.md)
- [开发指南](./DEVELOPMENT.md)
- [需求规格说明书](../兰大生活助手%20-%20软件需求规格说明书.docx)

## 🔗 有用链接

- FastAPI文档：https://fastapi.tiangolo.com/
- Vue 3文档：https://vuejs.org/
- Tailwind CSS：https://tailwindcss.com/
- Docker文档：https://docs.docker.com/

---

**最后更新**：2026年5月2日
