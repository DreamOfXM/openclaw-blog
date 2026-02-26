from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import sqlite3
import os
import json
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# 数据库配置
DATABASE = 'blog.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        # 创建文章表
        db.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                excerpt TEXT,
                status TEXT DEFAULT 'draft',
                visibility TEXT DEFAULT 'public',
                password_hash TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建用户表
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建默认管理员（如果不存在）
        # 用户名：admin，密码：openclaw2026
        default_password = hashlib.sha256('openclaw2026'.encode()).hexdigest()
        existing = db.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
        if not existing:
            db.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                       ('admin', default_password, 'admin'))
        
        db.commit()

# 初始化数据库
init_db()

# 辅助函数
def check_auth():
    return 'username' in session

def check_admin():
    return check_auth() and session.get('role') == 'admin'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
