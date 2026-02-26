from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import sqlite3
import os
import json
from datetime import datetime
import hashlib

app = Flask(__name__)
# 硬编码secret key，避免环境变量问题
app.secret_key = 'dev-secret-key-for-deployment-2026'

# 数据库配置
DATABASE = 'blog.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    print("Initializing database...")
    try:
        db = get_db()
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
        db.commit()
        
        # 创建默认管理员
        default_password = hashlib.sha256('openclaw2026'.encode()).hexdigest()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 检查是否已有管理员
        existing = db.execute('SELECT id FROM users WHERE username = ?', ('admin',)).fetchone()
        if not existing:
            db.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
                      ('admin', default_password, 'admin'))
        
        db.commit()
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"Database init warning: {e}")
        return False

# 初始化数据库
init_db()

# 辅助函数
def check_auth():
    return 'username' in session

def check_admin():
    return check_auth() and session.get('role') == 'admin'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def index():
    try:
        db = get_db()
        articles = db.execute('''
            SELECT * FROM articles 
            WHERE status = 'published' AND visibility IN ('public', 'password')
            ORDER BY created_at DESC
        ''').fetchall()
        return render_template('index.html', articles=articles)
    except Exception as e:
        return f"Error loading articles: {e}", 500

@app.route('/post/<slug>')
def view_post(slug):
    try:
        db = get_db()
        article = db.execute('SELECT * FROM articles WHERE slug = ?', (slug,)).fetchone()
        
        if not article:
            abort(404)
        
        # 检查权限
        if article['visibility'] == 'private' and not check_auth():
            abort(403)
        elif article['visibility'] == 'password':
            if 'unlocked_' + slug not in session:
                return redirect(url_for('password_prompt', slug=slug))
        
        return render_template('post.html', article=article)
    except Exception as e:
        return f"Error loading post: {e}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = hash_password(password)
        
        try:
            db = get_db()
            user = db.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', 
                             (username, password_hash)).fetchone()
            
            if user:
                session['username'] = user['username']
                session['role'] = user['role']
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='用户名或密码错误')
        except Exception as e:
            return f"Login error: {e}", 500
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if not check_admin():
        abort(403)
    
    try:
        db = get_db()
        articles = db.execute('SELECT * FROM articles ORDER BY created_at DESC').fetchall()
        return render_template('admin.html', articles=articles)
    except Exception as e:
        return f"Admin error: {e}", 500

@app.route('/password/<slug>', methods=['GET', 'POST'])
def password_prompt(slug):
    if request.method == 'POST':
        password = request.form['password']
        try:
            db = get_db()
            article = db.execute('SELECT * FROM articles WHERE slug = ?', (slug,)).fetchone()
            
            if article and article['password_hash'] == hash_password(password):
                session['unlocked_' + slug] = True
                return redirect(url_for('view_post', slug=slug))
            else:
                return render_template('password_prompt.html', slug=slug, error='密码错误')
        except Exception as e:
            return f"Password check error: {e}", 500
    
    return render_template('password_prompt.html', slug=slug)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Starting Flask app on {host}:{port}")
    print(f"Database file: {DATABASE}")
    print(f"App secret key configured")
    
    app.run(host=host, port=port, debug=False)