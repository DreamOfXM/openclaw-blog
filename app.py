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
                status TEXT DEFAULT 'published',  # 默认就是已发布
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
        print("Database tables created successfully")
        
        # 🚀 关键修复：添加初始文章
        articles_count = db.execute('SELECT COUNT(*) as count FROM articles').fetchone()['count']
        print(f"当前文章数量: {articles_count}")
        
        if articles_count == 0:
            print("添加初始文章...")
            
            # 文章1: OpenClaw入门指南
            db.execute('''
                INSERT OR IGNORE INTO articles (title, slug, content, excerpt, tags, visibility, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                'OpenClaw入门指南：构建你的AI助手工作流',
                'openclaw-introduction',
                '<h2>什么是OpenClaw？</h2><p>OpenClaw是一个开源的个人AI助手平台，让你能够部署自己的智能助手，连接你的工具、数据和日常工作流。</p><h2>核心功能</h2><ul><li><strong>多平台集成</strong>：支持Telegram、Discord、微信等</li><li><strong>工具扩展</strong>：通过技能系统扩展功能</li><li><strong>本地部署</strong>：完全掌控你的数据</li><li><strong>自动化工作流</strong>：智能调度和任务执行</li></ul><h2>快速开始</h2><p>安装OpenClaw只需要几步：<ol><li>安装Node.js环境</li><li>通过npm安装OpenClaw</li><li>配置你的技能和工具</li><li>连接到你喜欢的通讯平台</li></ol></p><h2>技能系统</h2><p>OpenClaw的技能就像手机App，每个技能都提供特定功能：<ul><li><code>weather</code>：天气查询</li><li><code>cron</code>：定时任务</li><li><code>memory</code>：记忆管理</li><li><code>browser</code>：浏览器控制</li></ul></p><blockquote><p>💡 提示：你可以通过ClawHub发现和安装社区技能</p></blockquote><h2>最佳实践</h2><p>1. <strong>从简单开始</strong>：先配置基础功能<br>2. <strong>渐进式扩展</strong>：逐步添加需要的技能<br>3. <strong>定期维护</strong>：更新技能和配置<br>4. <strong>社区参与</strong>：分享你的使用经验</p><h2>资源链接</h2><ul><li>官方网站：<a href=\"https://openclaw.ai\">openclaw.ai</a></li><li>GitHub仓库：<a href=\"https://github.com/openclaw/openclaw\">github.com/openclaw/openclaw</a></li><li>文档：<a href=\"https://docs.openclaw.ai\">docs.openclaw.ai</a></li><li>社区：<a href=\"https://discord.com/invite/clawd\">Discord社区</a></li></ul>',
                'OpenClaw是一个开源的个人AI助手平台，让你能够部署自己的智能助手，连接你的工具、数据和日常工作流。',
                'OpenClaw,AI助手,自动化,开源',
                'public',
                'published'
            ))
            
            # 文章2: 量化交易系统
            db.execute('''
                INSERT OR IGNORE INTO articles (title, slug, content, excerpt, tags, visibility, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                '量化交易系统架构设计',
                'quant-trading-system',
                '<h2>系统架构概览</h2><p>一个完整的量化交易系统通常包含以下核心模块：</p><ul><li><strong>数据层</strong>：市场数据收集和存储</li><li><strong>策略层</strong>：交易逻辑和算法</li><li><strong>执行层</strong>：订单管理和风险控制</li><li><strong>监控层</strong>：性能分析和报警</li></ul><h2>关键技术栈</h2><h3>Python生态系统</h3><pre><code class=\"language-python\"># 核心库示例\nimport pandas as pd  # 数据处理\nimport numpy as np   # 数值计算\nimport talib         # 技术指标\nimport backtrader    # 回测框架</code></pre><h3>数据存储方案</h3><ul><li><strong>时序数据库</strong>：InfluxDB for tick数据</li><li><strong>关系数据库</strong>：PostgreSQL for 元数据</li><li><strong>缓存层</strong>：Redis for 实时数据</li></ul><h2>风险控制机制</h2><table><thead><tr><th>风险类型</th><th>控制措施</th><th>阈值</th></tr></thead><tbody><tr><td>最大回撤</td><td>仓位调整</td><td>≤20%</td></tr><tr><td>单日亏损</td><td>停止交易</td><td>≤5%</td></tr><tr><td>集中度风险</td><td>分散投资</td><td>≤15% per asset</td></tr></tbody></table><h2>回测框架设计</h2><p>有效的回测需要避免常见陷阱：</p><ol><li><strong>前瞻性偏差</strong>：确保不使用未来数据</li><li><strong>交易成本</strong>：考虑佣金和滑点</li><li><strong>数据质量</strong>：处理缺失值和异常值</li><li><strong>过拟合风险</strong>：使用交叉验证</li></ol><h2>部署架构</h2><pre><code class=\"language-yaml\"># Docker Compose配置示例\nversion: \'3.8\'\nservices:\n  data-collector:\n    image: python:3.11\n    command: python data_collector.py\n    \n  strategy-engine:\n    image: python:3.11  \n    depends_on:[data-collector]\n    \n  risk-manager:\n    image: python:3.11\n    environment:\n      - MAX_DRAWDOWN=0.20</code></pre><h2>监控和运维</h2><ul><li><strong>性能监控</strong>：Prometheus + Grafana</li><li><strong>日志管理</strong>：ELK Stack</li><li><strong>报警系统</strong>：基于规则的实时报警</li><li><strong>版本控制</strong>：Git + CI/CD</li></ul><h2>学习资源</h2><ul><li><strong>书籍</strong>：《量化交易：如何建立自己的算法交易事业》</li><li><strong>课程</strong>：Coursera \"Machine Learning for Trading\"</li><li><strong>开源项目</strong>：Zipline, Backtrader, QLib</li><li><strong>社区</strong>：QuantConnect, Kaggle</li></ul>',
                '量化交易系统设计需要综合考虑数据管理、策略开发、风险控制和系统部署等多个方面，建立健壮且可扩展的架构是关键。',
                '量化交易,Python,金融科技,系统架构',
                'public',
                'published'
            ))
            
            db.commit()
            print("✅ 成功添加2篇初始文章")
        else:
            print(f"✅ 数据库已有 {articles_count} 篇文章")
        
        return True
    except Exception as e:
        print(f"❌ Database init error: {e}")
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
        # 🚀 关键修复：简化查询，确保能获取文章
        articles = db.execute('''
            SELECT * FROM articles 
            WHERE status = 'published'
            ORDER BY created_at DESC
        ''').fetchall()
        
        print(f"📊 首页查询: 找到 {len(articles)} 篇文章")
        for article in articles:
            print(f"  - {article['title']} (visibility: {article['visibility']})")
        
        return render_template('index.html', articles=articles)
    except Exception as e:
        print(f"❌ 首页错误: {e}")
        import traceback
        traceback.print_exc()
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
        print(f"管理后台: 找到 {len(articles)} 篇文章")
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
    
    print(f"🚀 Starting Flask app on {host}:{port}")
    print(f"📁 Database file: {DATABASE}")
    print(f"🔑 App secret key configured")
    
    # 最后检查一次数据库
    db = get_db()
    count = db.execute('SELECT COUNT(*) as count FROM articles').fetchone()['count']
    print(f"📊 最终文章数量: {count}")
    
    app.run(host=host, port=port, debug=False)