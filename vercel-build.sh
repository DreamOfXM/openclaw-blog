#!/bin/bash
# Vercel构建脚本

echo "开始构建博客系统..."
pip install -r requirements.txt --quiet

echo "创建数据库..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('数据库创建完成')
"

echo "构建完成！
