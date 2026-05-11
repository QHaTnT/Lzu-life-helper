# 兰大生活助手 - 代码学习顺序

## 第一层：入口和配置

| 顺序 | 文件 | 看什么 |
|------|------|--------|
| 1 | `backend/app/main.py` | 整个后端入口，路由注册、中间件、异常处理 |
| 2 | `backend/app/core/config.py` | 所有配置项（数据库、Redis、JWT、上传等） |
| 3 | `frontend/src/router/index.js` | 前端所有页面路由和守卫逻辑 |
| 4 | `frontend/src/api/request.js` | Axios 封装、Token 注入、响应解包 |

## 第二层：数据模型（理解业务）

| 顺序 | 文件 | 看什么 |
|------|------|--------|
| 5 | `backend/app/models/__init__.py` | 全部 13 张表的定义和关联关系 |
| 6 | `backend/init_db.py` | 种子数据，理解每个模块的业务含义 |

## 第三层：后端 API（请求怎么处理的）

| 顺序 | 文件 | 看什么 |
|------|------|--------|
| 7 | `backend/app/api/v1/__init__.py` | 路由注册，看所有接口的挂载方式 |
| 8 | `backend/app/api/v1/auth.py` | 登录注册，理解 JWT 鉴权流程 |
| 9 | `backend/app/api/v1/products.py` | 二手市场 CRUD，最典型的接口 |
| 10 | `backend/app/api/v1/community.py` | 生活圈，理解动态/评论/点赞/活动 |
| 11 | `backend/app/api/v1/venues.py` | 场馆预约，理解并发锁机制 |
| 12 | `backend/app/api/v1/bus.py` | 校车查询，最简单的接口 |

## 第四层：业务逻辑（核心难点）

| 顺序 | 文件 | 看什么 |
|------|------|--------|
| 13 | `backend/app/services/venue_service.py` | Redis 分布式锁 + MySQL 行锁，并发安全 |
| 14 | `backend/app/core/security.py` | JWT 生成/验证、密码哈希 |
| 15 | `backend/app/core/database.py` | 数据库连接池配置 |
| 16 | `backend/app/core/redis.py` | Redis 连接 |
| 17 | `backend/app/utils/serializers.py` | 数据序列化工具 |

## 第五层：前端页面（用户看到什么）

| 顺序 | 文件 | 看什么 |
|------|------|--------|
| 18 | `frontend/src/views/Login.vue` | 登录页，理解前端如何调后端 API |
| 19 | `frontend/src/views/Home.vue` | 首页，模块入口 |
| 20 | `frontend/src/views/Market.vue` | 二手市场，搜索/筛选/发布 |
| 21 | `frontend/src/views/ProductDetail.vue` | 商品详情，图片/留言/联系卖家 |
| 22 | `frontend/src/views/Community.vue` | 生活圈，发布动态/活动 |
| 23 | `frontend/src/views/Venue.vue` | 场馆预约，时段选择 |
| 24 | `frontend/src/views/Profile.vue` | 个人中心 |

## 第六层：公共组件

| 顺序 | 文件 | 看什么 |
|------|------|--------|
| 25 | `frontend/src/components/BottomNav.vue` | 底部导航，6 个 tab 的切换逻辑 |
| 26 | `frontend/src/store/auth.js` | Pinia 状态管理，登录状态持久化 |
| 27 | `frontend/src/api/index.js` | API 接口汇总定义 |

## 建议学习方法

1. **先跑起来**，用 Docker 一键启动
2. **从 `auth.py` 开始**，跟着登录流程走一遍：Login.vue → api/request.js → auth.py → security.py → 返回 token → 存入 localStorage
3. **再走一遍 products.py**，理解完整的 CRUD 流程
4. **最后看 venue_service.py**，这是最复杂的并发控制逻辑
5. 每个文件重点看：**函数参数 → 业务逻辑 → 返回值**，遇到不懂的类或函数就跳转去看定义
