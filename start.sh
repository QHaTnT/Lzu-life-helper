#!/bin/bash

echo "🚀 启动兰州大学生活助手..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 创建.env文件（如果不存在）
if [ ! -f backend/.env ]; then
    echo "📝 创建环境配置文件..."
    cp backend/.env.example backend/.env
fi

# 构建并启动服务
echo "🔨 构建Docker镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 10

# 初始化数据库
echo "📊 初始化数据库..."
docker-compose exec backend python init_db.py

echo ""
echo "✅ 启动完成！"
echo ""
echo "访问地址："
echo "  前端: http://localhost"
echo "  后端API: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "测试账号："
echo "  用户名: zhangsan, 密码: 123456"
echo "  用户名: lisi, 密码: 123456"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
