from flask import Flask, render_template, request, redirect, url_for, session, jsonify, abort
import sqlite3
import os
import hashlib

app = Flask(__name__)
# 硬编码secret key
app.secret_key = 'dev-secret-key-for-deployment-2026'

# 数据库配置
DATABASE = 'blog.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    print("🚀 开始初始化数据库...")
    try:
        db = get_db()
        
        # 创建文章表
        db.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                excerpt TEXT,
                status TEXT DEFAULT 'published',
                visibility TEXT DEFAULT 'public',
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建用户表
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'admin'
            )
        ''')
        
        db.commit()
        print("✅ 数据库表创建完成")
        
        # 添加默认管理员
        default_password = hashlib.sha256('openclaw2026'.encode()).hexdigest()
        db.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES ('admin', ?, 'admin')",
            (default_password,)
        )
        
        # 添加测试文章
        test_article = db.execute("SELECT id FROM articles WHERE slug = 'welcome'").fetchone()
        if not test_article:
            db.execute('''
                INSERT INTO articles (title, slug, content, excerpt, tags)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                '欢迎使用OpenClaw博客系统',
                'welcome',
                '<h2>恭喜！您的博客已成功部署</h2><p>这是一个功能完整的博客系统，包含以下特性：</p><ul><li>响应式设计，支持移动设备</li><li>多级权限管理（公开/私密/密码保护）</li><li>管理员后台管理</li><li>文章标签分类</li><li>现代化界面设计</li></ul><h3>下一步建议</h3><p>1. 在管理后台添加更多文章</p><p>2. 自定义博客样式</p><p>3. 配置更多功能</p>',
                'OpenClaw博客系统已成功部署，具备完整功能',
                'OpenClaw,博客,技术'
            ))
            print("✅ 添加测试文章")
        
        # 再添加一篇文章
        second_article = db.execute("SELECT id FROM articles WHERE slug = 'openclaw-guide'").fetchone()
        if not second_article:
            db.execute('''
                INSERT INTO articles (title, slug, content, excerpt, tags)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                'OpenClaw平台介绍',
                'openclaw-guide',
                '<h2>OpenClaw是什么？</h2><p>OpenClaw是一个开源的个人AI助手平台，让你能够部署自己的智能助手，连接你的工具、数据和日常工作流。</p><h2>核心功能</h2><ul><li><strong>多平台集成</strong>：支持Telegram、Discord、微信等</li><li><strong>技能系统</strong>：通过技能扩展功能</li><li><strong>本地部署</strong>：完全掌控数据</li><li><strong>自动化工作流</strong>：智能调度和任务执行</li></ul>',
                'OpenClaw是一个开源的个人AI助手平台',
                'AI助手,自动化,开源'
            ))
            print("✅ 添加第二篇文章")
        
        db.commit()
        
        # 验证数据
        article_count = db.execute("SELECT COUNT(*) as count FROM articles").fetchone()['count']
        user_count = db.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
        
        print(f"📊 初始化完成：{article_count}篇文章，{user_count}个用户")
        return True
        
    except Exception as e:
        print(f"❌ 数据库初始化错误: {e}")
        import traceback
        traceback.print_exc()
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
            SELECT id, title, slug, excerpt, tags, created_at
            FROM articles 
            WHERE status = 'published'
            ORDER BY created_at DESC
        ''').fetchall()
        
        print(f"📄 首页查询：找到 {len(articles)} 篇文章")
        
        # 如果没有文章，强制初始化
        if len(articles) == 0:
            print("⚠️ 没有文章，重新初始化...")
            init_db()
            articles = db.execute("SELECT id, title, slug, excerpt, tags, created_at FROM articles").fetchall()
            print(f"🔄 重新初始化后：{len(articles)} 篇文章")
        
        return render_template('index.html', articles=articles)
    except Exception as e:
        print(f"❌ 首页错误: {e}")
        return f"Error loading articles: {e}", 500

@app.route('/post/<slug>')
def view_post(slug):
    try:
        db = get_db()
        article = db.execute('SELECT * FROM articles WHERE slug = ?', (slug,)).fetchone()
        
        if not article:
            abort(404)
        
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
                print(f"✅ 用户 {username} 登录成功")
                return redirect(url_for('index'))
            else:
                print(f"❌ 登录失败：用户名或密码错误")
                return render_template('login_safe.html', error='用户名或密码错误')
        except Exception as e:
            print(f"❌ 登录错误: {e}")
            return f"Login error: {e}", 500
    
    return render_template('login_safe.html')

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

@app.route('/debug')
def debug():
    """数据库诊断页面"""
    try:
        db = get_db()
        
        # 检查表
        tables = db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        
        # 文章表数据
        articles_count = db.execute("SELECT COUNT(*) as count FROM articles").fetchone()['count']
        articles = db.execute("SELECT id, title, slug, status, visibility FROM articles ORDER BY id").fetchall()
        
        # 用户表数据
        users_count = db.execute("SELECT COUNT(*) as count FROM users").fetchone()['count']
        users = db.execute("SELECT id, username, role FROM users ORDER BY id").fetchall()
        
        return f'''
<!DOCTYPE html>
<html>
<head><title>数据库诊断</title></head>
<body style="font-family: monospace; padding: 20px;">
<h2>📊 数据库诊断页面</h2>

<h3>📁 数据库表：</h3>
<ul>
{''.join(f'<li>{table["name"]}</li>' for table in tables)}
</ul>

<h3>📝 文章表（{articles_count} 篇）：</h3>
<table border="1" cellpadding="5">
<tr><th>ID</th><th>标题</th><th>Slug</th><th>状态</th><th>可见性</th></tr>
{''.join(f'<tr><td>{a["id"]}</td><td>{a["title"]}</td><td>{a["slug"]}</td><td>{a["status"]}</td><td>{a["visibility"]}</td></tr>' for a in articles)}
</table>

<h3>👤 用户表（{users_count} 个）：</h3>
<table border="1" cellpadding="5">
<tr><th>ID</th><th>用户名</th><th>角色</th></tr>
{''.join(f'<tr><td>{u["id"]}</td><td>{u["username"]}</td><td>{u["role"]}</td></tr>' for u in users)}
</table>

<p><a href="/">返回首页</a></p>
</body>
</html>
'''
    except Exception as e:
        return f"诊断错误: {e}", 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"🚀 启动博客应用 {host}:{port}")
    print(f"📁 数据库文件: {DATABASE}")
    
    # 最终检查
    db = get_db()
    article_count = db.execute("SELECT COUNT(*) as count FROM articles").fetchone()['count']
    print(f"📊 最终文章数量: {article_count}")
    
    if article_count == 0:
        print("⚠️ 警告：数据库中没有文章，重新初始化...")
        init_db()
    
    app.run(host=host, port=port, debug=False)