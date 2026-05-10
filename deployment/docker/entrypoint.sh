#!/bin/bash
set -e

echo "等待 MySQL 就绪..."
python -c "
import time, pymysql
for i in range(30):
    try:
        pymysql.connect(host='mysql', user='lzu_user', password='lzu_password', database='lzu_helper')
        print('MySQL 已就绪')
        break
    except Exception:
        print(f'等待中... ({i+1}/30)')
        time.sleep(2)
else:
    print('MySQL 连接超时，退出')
    exit(1)
"

echo "初始化数据库..."
python -X utf8 init_db.py

echo "启动后端服务..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
