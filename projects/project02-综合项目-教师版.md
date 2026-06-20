# 综合项目：中小型企业基础运维环境搭建与容器化部署（教师版）

> 教师用详细版 | 对应 U66-U72 · 7次大课 · 14课时
> 学生拿到的是简版（project02-综合项目-学生版.md）——只有任务清单，没有具体命令

---

## 项目概述

项目名称：**TechCorp 企业官网 + 留言板系统**

最终效果：
```
用户浏览器
  → Nginx(80) 反向代理
    → / → 企业官网静态页面
    → /api/ → Python Flask API(5000)
              → MySQL(3306) 存储留言
              → Redis(6379) 留言计数
```

部署方式：Docker Compose 一键编排 4 个服务（frontend / backend / db / redis）

---

## 第1次大课：选题与Linux基础环境（U66 · 90分钟）

### 环节1：项目发布（20分钟）

**教师讲解**：
1. 展示最终效果 —— 浏览器访问 `http://VM_IP` 看到官网+留言板
2. 说明 12 项任务清单和 12 项交付物
3. 分组（2-3人/组），每组选题（4选1，或选"TechCorp官网+留言板"）
4. 评分标准说明（环境搭建20% + 服务部署20% + 容器化25% + 排障15% + 文档10% + 素养10%）

**不需要给学生看命令**。这是目标设定环节。

### 环节2：安装系统 + 基础配置（40分钟）

```bash
# === 确认环境 ===
cat /etc/os-release                  # Rocky Linux 9
hostname

# === 安装所有后续要用的基础工具 ===
sudo dnf install -y epel-release
sudo dnf install -y vim bash-completion man-pages \
  net-tools lsof wget curl git \
  nginx mariadb-server redis \
  python3 python3-pip

# === 用户和权限 ===
# 创建项目专用用户（可选，演示用）
sudo useradd -m deploy
echo "deploy:deploy123" | sudo chpasswd

# === 软件源确认 ===
dnf repolist
# 应该看到 baseos, appstream, epel
```

> **教师备忘**：这些工具一次性装好，后续所有步骤都不会缺命令。学生如果漏装某个工具，到后面步骤会卡住——这也是排障学习的机会。

### 环节3：编写项目需求文档（30分钟）

```bash
mkdir -p ~/techcorp-project
cd ~/techcorp-project

cat > REQUIREMENTS.md << 'DOC'
# TechCorp 企业官网 + 留言板系统

## 功能需求
1. 企业官网：展示公司信息、团队介绍、联系方式
2. 留言板：用户可提交留言，实时显示留言列表
3. 留言计数：显示总留言数量

## 技术架构
- 前端：Nginx 反向代理 + 静态HTML/JS
- 后端：Python Flask REST API
- 数据库：MySQL 8.0
- 缓存：Redis 7

## 部署方式
- 最终目标：Docker Compose 一键部署
- 中间步骤：传统方式部署（用于理解原理）

## 安全要求
- MySQL 密码不使用默认值
- Redis 启用密码认证
- 防火墙只开放 80/443/22 端口
- 数据库和 Redis 不对外暴露端口
DOC
```

---

## 第2次大课：网络与SSH + Nginx部署（U67 · 90分钟）

### 环节1：网络配置确认（15分钟）

```bash
# === 确认网络 ===
ip a show ens33 | grep inet
ip route show default
ping -c 2 223.5.5.5

# === 配置 /etc/hosts（模拟多机环境） ===
sudo tee -a /etc/hosts << 'EOF'
127.0.0.1  techcorp.local www.techcorp.local
EOF

# === 防火墙初始化 ===
sudo firewall-cmd --add-service=ssh --permanent
sudo firewall-cmd --add-service=http --permanent
sudo firewall-cmd --add-service=https --permanent
sudo firewall-cmd --reload
firewall-cmd --list-all
```

### 环节2：Nginx 部署——企业官网（40分钟）

```bash
# === 创建网站目录 ===
sudo mkdir -p /var/www/techcorp
sudo chown -R student:student /var/www/techcorp

# === 企业官网首页 ===
cat > /var/www/techcorp/index.html << 'HTML'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TechCorp - 科技创新引领未来</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;color:#333;line-height:1.6}
header{background:linear-gradient(135deg,#1a1a2e,#16213e);color:white;padding:60px 20px;text-align:center}
header h1{font-size:2.5em;margin-bottom:10px}
header p{font-size:1.2em;color:#a0a0b0}
nav{background:#0f3460;padding:15px;text-align:center;position:sticky;top:0;z-index:10}
nav a{color:white;margin:0 20px;text-decoration:none;font-size:15px}
nav a:hover{color:#e94560}
section{padding:60px 20px;max-width:900px;margin:0 auto}
section h2{font-size:1.8em;color:#1a1a2e;margin-bottom:20px;border-bottom:3px solid #e94560;display:inline-block;padding-bottom:5px}
.team{display:flex;gap:30px;flex-wrap:wrap;justify-content:center}
.member{background:#f8f9fa;padding:20px;border-radius:10px;text-align:center;flex:1;min-width:200px;max-width:250px}
.member img{width:80px;height:80px;border-radius:50%;background:#16213e;margin-bottom:15px}
footer{background:#1a1a2e;color:#a0a0b0;text-align:center;padding:20px;font-size:14px}
#message-board{margin-top:30px;background:#f8f9fa;padding:20px;border-radius:10px}
#message-board input{width:calc(100% - 100px);padding:10px;border:1px solid #ddd;border-radius:4px;font-size:14px}
#message-board button{padding:10px 20px;background:#e94560;color:white;border:none;border-radius:4px;cursor:pointer;font-size:14px}
#message-board button:hover{background:#c23152}
.msg-item{background:white;padding:10px 15px;margin:8px 0;border-radius:4px;border-left:3px solid #e94560}
</style>
</head>
<body>
<header>
  <h1>🚀 TechCorp</h1>
  <p>科技创新引领未来 — 企业级运维与云服务解决方案</p>
</header>
<nav>
  <a href="#about">关于我们</a><a href="#services">核心服务</a><a href="#team">团队介绍</a><a href="#message-board">留言板</a><a href="#contact">联系我们</a>
</nav>

<section id="about">
  <h2>关于 TechCorp</h2>
  <p>TechCorp 成立于2024年，是一家专注于企业级云计算、自动化运维和智能监控的技术服务公司。我们提供从数据中心基础设施到云原生应用的全栈运维解决方案。</p>
</section>

<section id="services">
  <h2>核心服务</h2>
  <ul style="list-style:none;padding:0">
    <li style="padding:12px;border-bottom:1px solid #eee"><strong>🖥 Linux服务器运维</strong> — 系统管理/性能调优/安全加固</li>
    <li style="padding:12px;border-bottom:1px solid #eee"><strong>🐳 Docker容器化</strong> — 微服务架构/Compose编排/CI/CD</li>
    <li style="padding:12px;border-bottom:1px solid #eee"><strong>📊 监控告警</strong> — Prometheus + Grafana 全栈监控</li>
    <li style="padding:12px;border-bottom:1px solid #eee"><strong>☁️ 云服务管理</strong> — 多云环境管理/成本优化/迁移</li>
  </ul>
</section>

<section id="team">
  <h2>核心团队</h2>
  <div class="team">
    <div class="member"><img src="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 80 80'><rect fill='%2316213e' width='80' height='80'/><text x='40' y='50' text-anchor='middle' fill='white' font-size='30'>张</text></svg>" alt=""><h3>张三</h3><p>CEO & 创始人</p></div>
    <div class="member"><img src="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 80 80'><rect fill='%2316213e' width='80' height='80'/><text x='40' y='50' text-anchor='middle' fill='white' font-size='30'>李</text></svg>" alt=""><h3>李四</h3><p>CTO</p></div>
    <div class="member"><img src="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 80 80'><rect fill='%2316213e' width='80' height='80'/><text x='40' y='50' text-anchor='middle' fill='white' font-size='30'>王</text></svg>" alt=""><h3>王五</h3><p>运维总监</p></div>
  </div>
</section>

<section id="message-board">
  <h2>📝 客户留言</h2>
  <div style="margin-bottom:10px">总留言数：<strong id="total-msgs">0</strong></div>
  <input id="msg-input" placeholder="留下您的宝贵意见..." maxlength="200">
  <button onclick="postMsg()">提交留言</button>
  <div id="msg-list" style="margin-top:15px"></div>
</section>

<section id="contact">
  <h2>联系我们</h2>
  <p>📧 Email：contact@techcorp.local</p>
  <p>📞 电话：+86 400-888-0000</p>
  <p>📍 地址：广东省深圳市南山区科技园路100号</p>
</section>

<footer>&copy; 2026 TechCorp | Powered by Nginx on Rocky Linux 9</footer>

<script>
const API='/api/messages';
async function loadMsgs(){try{const r=await fetch(API);const msgs=await r.json();
document.getElementById('msg-list').innerHTML=msgs.map(m=>`<div class="msg-item">${m.content}<br><small>${m.time}</small></div>`).join('')||'<div class="msg-item">暂无留言，快来第一个留言吧！</div>'}catch(e){document.getElementById('msg-list').innerHTML='<div class="msg-item">加载失败，请确认后端服务已启动</div>'}}
async function postMsg(){const i=document.getElementById('msg-input');const m=i.value.trim();if(!m)return;
try{const r=await fetch(API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
if(r.ok){i.value='';loadMsgs();loadStats()}}catch(e){}}
async function loadStats(){try{const r=await fetch('/api/stats');const s=await r.json();document.getElementById('total-msgs').textContent=s.total_messages}catch(e){}}
loadMsgs();loadStats();
</script>
</body></html>
HTML

# === Nginx 虚拟主机配置 ===
sudo tee /etc/nginx/conf.d/techcorp.conf << 'EOF'
server {
    listen 80;
    server_name techcorp.local www.techcorp.local;
    root /var/www/techcorp;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

sudo nginx -t
sudo systemctl enable --now nginx
sudo firewall-cmd --add-service=http --permanent && sudo firewall-cmd --reload

# === 验证 ===
curl -s http://techcorp.local | head -10
curl -I http://techcorp.local | grep "200 OK"
```

> **验收点**：`curl http://techcorp.local` 返回完整HTML。前端 JS 调用 /api/ 会失败（后端还没部署——这是正常的）。

### 环节3：Nginx 日志配置（15分钟）

```bash
# 查看当前日志
sudo tail -5 /var/log/nginx/access.log
sudo tail -5 /var/log/nginx/error.log

# 为项目单独配置日志
# 在 techcorp.conf 中添加：
# access_log /var/log/nginx/techcorp-access.log;
# error_log  /var/log/nginx/techcorp-error.log;
```

### 环节4：Git 初始化项目仓库（20分钟）

```bash
cd ~/techcorp-project
git init

# 收集已有文件
sudo cp /var/www/techcorp/index.html ./
sudo chown student:student index.html
sudo cp /etc/nginx/conf.d/techcorp.conf ./nginx-techcorp.conf.bak
sudo chown student:student nginx-techcorp.conf.bak

git add index.html nginx-techcorp.conf.bak REQUIREMENTS.md
git commit -m "v1.0: TechCorp官网 + Nginx配置 + 需求文档"

git log --oneline
```

> **教师备忘**：告诉学生——每次完成一个重要阶段就 commit 一次。这不仅是版本控制，更是"后悔药"（出错了可以 git checkout 回去）。

---

## 第3次大课：数据库 + Redis + Shell脚本（U68 · 90分钟）

### 环节1：MariaDB 部署（30分钟）

```bash
# === 安全初始化 ===
sudo mysql_secure_installation
# 设root密码：DBroot123! ，其余全部Y

# === 创建项目数据库 ===
mysql -u root -p << 'SQL'
CREATE DATABASE techcorp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'techcorp_app'@'localhost' IDENTIFIED BY 'AppPass456!';
GRANT SELECT, INSERT, UPDATE, DELETE ON techcorp_db.* TO 'techcorp_app'@'localhost';

CREATE USER 'techcorp_app'@'127.0.0.1' IDENTIFIED BY 'AppPass456!';
GRANT SELECT, INSERT, UPDATE, DELETE ON techcorp_db.* TO 'techcorp_app'@'127.0.0.1';

FLUSH PRIVILEGES;
SELECT User, Host FROM mysql.user WHERE User='techcorp_app';
SQL

# === 创建留言表 ===
mysql -u techcorp_app -pAppPass456! techcorp_db << 'SQL'
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO messages (content) VALUES ('欢迎来到TechCorp！'), ('期待更多合作！');
SELECT * FROM messages;
SQL

# === 备份 ===
mkdir -p ~/techcorp-project/backups
mysqldump -u root -p techcorp_db > ~/techcorp-project/backups/techcorp_db-$(date +%Y%m%d).sql
```

### 环节2：Redis 部署（20分钟）

```bash
# === 安全配置 ===
sudo sed -i 's/^# requirepass.*/requirepass RedisPass2026!/' /etc/redis/redis.conf
sudo sed -i 's/^bind .*/bind 127.0.0.1/' /etc/redis/redis.conf
sudo systemctl enable --now redis

# === 验证 ===
redis-cli -a RedisPass2026! PING              # PONG
redis-cli -a RedisPass2026! SET test "hello"
redis-cli -a RedisPass2026! GET test
```

### 环节3：编写 Flask 后端 API（30分钟）

```bash
# === 安装 Python 依赖 ===
pip3 install --user flask redis pymysql
# 如果 pip3 不可用：sudo dnf install -y python3-pip

# === 创建后端目录 ===
mkdir -p ~/techcorp-project/backend
cd ~/techcorp-project/backend

# === Flask API ===
cat > app.py << 'PYEOF'
from flask import Flask, jsonify, request
import redis, pymysql, os, datetime

app = Flask(__name__)

# Redis 连接（密码从环境变量读取）
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'RedisPass2026!')
r = redis.Redis(host=os.getenv('REDIS_HOST', '127.0.0.1'), port=6379,
                password=REDIS_PASSWORD, decode_responses=True)

# MySQL 连接
def get_db():
    return pymysql.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        user='techcorp_app',
        password='AppPass456!',
        database='techcorp_db',
        autocommit=True,
        charset='utf8mb4')

@app.route('/api/health')
def health():
    try:
        r.ping()
        db = get_db()
        db.close()
        return jsonify({'status':'ok', 'redis':'connected', 'db':'connected',
                        'time':str(datetime.datetime.now())})
    except Exception as e:
        return jsonify({'status':'error', 'error':str(e)}), 500

@app.route('/api/messages', methods=['GET','POST'])
def messages():
    if request.method == 'POST':
        data = request.get_json()
        msg = data.get('message','').strip()
        if not msg:
            return jsonify({'status':'error','msg':'empty message'}), 400
        if len(msg) > 200:
            return jsonify({'status':'error','msg':'message too long'}), 400
        try:
            db = get_db()
            cur = db.cursor()
            cur.execute("INSERT INTO messages (content) VALUES (%s)", (msg,))
            cur.close()
            db.close()
            r.incr('total_messages')
            return jsonify({'status':'ok'})
        except Exception as e:
            return jsonify({'status':'error','msg':str(e)}), 500

    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, content, created_at FROM messages ORDER BY id DESC LIMIT 50")
        rows = cur.fetchall()
        cur.close()
        db.close()
        return jsonify([{'id':r[0],'content':r[1],'time':str(r[2])} for r in rows])
    except Exception as e:
        return jsonify({'status':'error','msg':str(e)}), 500

@app.route('/api/stats')
def stats():
    try:
        return jsonify({'total_messages': int(r.get('total_messages') or 0)})
    except:
        return jsonify({'total_messages': 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
PYEOF

# === 测试运行 ===
# 在另一个终端：
python3 ~/techcorp-project/backend/app.py &
sleep 2

# 测试 API
curl http://localhost:5000/api/health
curl http://localhost:5000/api/messages
curl -X POST http://localhost:5000/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello from Flask!"}'
curl http://localhost:5000/api/stats

# 停掉测试
pkill -f "python3.*app.py"
```

### 环节4：Shell 巡检脚本（10分钟）

```bash
cat > ~/techcorp-project/ops-check.sh << 'SCRIPT'
#!/bin/bash
echo "========================================="
echo "  TechCorp 服务器巡检 - $(date '+%H:%M:%S')"
echo "========================================="
echo "[负载] $(uptime | awk -F'load average:' '{print $2}')"
echo "[内存] $(free -h | grep Mem | awk '{print "已用:"$3" 可用:"$7}')"
echo "[磁盘] $(df -h / | tail -1 | awk '{print "已用:"$3"/"$2" ("$5")"}')"
echo ""
echo "[服务]"
for s in nginx mariadb redis; do
    systemctl is-active --quiet $s && echo "  $s ✓" || echo "  $s ✗"
done
echo ""
echo "[API检测]"
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/health 2>/dev/null
echo " <- Flask API"
echo "[Nginx]"
curl -s -o /dev/null -w "%{http_code}" http://localhost 2>/dev/null
echo " <- Nginx"
echo "========================================="
SCRIPT
chmod +x ~/techcorp-project/ops-check.sh
./ops-check.sh
```

> **教师备忘**：这个阶段完成后，传统方式部署就完成了。curl http://techcorp.local 能看到官网，/api/ 路径由 Nginx 反代到 Flask。下一阶段开始容器化改造。

---

## 第4次大课：虚拟化多机环境（U69 · 90分钟）

### 环节1：三机环境搭建（40分钟）

```bash
# 使用 VMware 克隆出三台 VM（如果环境允许）
# web-server: 192.168.200.10 - Nginx + Flask
# db-server:  192.168.200.20 - MariaDB + Redis  
# client:     192.168.200.30 - 测试客户端

# 在每台 VM 上配置 hosts
sudo tee -a /etc/hosts << 'EOF'
192.168.200.10  web-server
192.168.200.20  db-server
192.168.200.30  client
EOF

# === web-server 部署 ===
# Nginx 配置中的 proxy_pass 指向本机 Flask
# 如果需要连接远程 db-server：
# 修改 app.py 中 DB_HOST='db-server', REDIS_HOST='db-server'

# === db-server 部署 ===
# 修改 MariaDB bind-address = 0.0.0.0（允许远程连接）
# 修改 Redis bind 0.0.0.0
# 防火墙放行 3306 和 6379（仅内网）
sudo firewall-cmd --add-rich-rule='rule family="ipv4" source address="192.168.200.0/24" port port="3306" protocol="tcp" accept' --permanent
sudo firewall-cmd --add-rich-rule='rule family="ipv4" source address="192.168.200.0/24" port port="6379" protocol="tcp" accept' --permanent
sudo firewall-cmd --reload

# === client 测试 ===
curl http://web-server
mysql -u techcorp_app -h db-server -p -e "SELECT * FROM techcorp_db.messages;"
redis-cli -h db-server -a RedisPass2026! PING
```

> **教师备忘**：如果环境只有单台 VM，三机部分可以做简化——用不同的端口模拟不同的"服务器"，或者跳过这个环节直接进入 Docker 部分。重点让学生理解"服务可以分布在不同机器上，通过 TCP 通信"。

### 环节2：绘制拓扑图 + IP 规划表（30分钟）

```markdown
# TechCorp 部署拓扑图

               互联网
                 │
          ┌──────┴──────┐
          │  Nginx(80)  │ ← web-server: 192.168.200.10
          │  Flask(5000)│
          └──────┬──────┘
                 │
      ┌──────────┼──────────┐
      │                     │
┌─────┴─────┐       ┌───────┴──────┐
│ MariaDB   │       │    Redis     │
│ (3306)    │       │   (6379)     │
└───────────┘       └──────────────┘
  db-server: 192.168.200.20
```

### 环节3：Git 提交当前进度（20分钟）

```bash
cd ~/techcorp-project
# 把后端代码、巡检脚本、配置都纳入版本控制
cp -r backend/ .
cp ops-check.sh .

git add backend/ ops-check.sh
git commit -m "v2.0: 后端Flask API + 巡检脚本 + 传统方式部署完成"

# 打 tag 标记传统部署版本
git tag traditional-deploy-v1
git log --oneline
```

---

## 第5次大课：Docker 容器化（U70 · 90分钟）

### 环节1：Docker 安装（10分钟）

```bash
sudo dnf config-manager --add-repo https://download.docker.com/linux/rhel/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker student
newgrp docker
docker --version
```

### 环节2：编写 Dockerfile（30分钟）

```bash
cd ~/techcorp-project

# === 后端 Dockerfile ===
mkdir -p docker/backend
cp backend/app.py docker/backend/
cp backend/requirements.txt docker/backend/ 2>/dev/null

# 如果还没有 requirements.txt：
cat > docker/backend/requirements.txt << 'EOF'
flask==3.0.0
redis==5.0.0
pymysql==1.1.0
EOF

cat > docker/backend/Dockerfile << 'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
USER 1000
CMD ["python", "app.py"]
EOF

# === 构建后端镜像 ===
docker build -t techcorp-backend:v1 -f docker/backend/Dockerfile docker/backend/
docker images | grep techcorp

# === 前端 Nginx 配置（容器版） ===
mkdir -p docker/frontend
cp /var/www/techcorp/index.html docker/frontend/

# 容器版 Nginx 配置：proxy_pass 指向容器名 backend
cat > docker/frontend/nginx.conf << 'EOF'
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /api/ {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF
```

### 环节3：创建 Docker 网络并测试（30分钟）

```bash
# === 创建自定义网络 ===
docker network create techcorp-net

# === 启动 MySQL 容器 ===
docker run -d --name db \
  --network techcorp-net \
  -e MYSQL_ROOT_PASSWORD=DBroot123! \
  -e MYSQL_DATABASE=techcorp_db \
  -e MYSQL_USER=techcorp_app \
  -e MYSQL_PASSWORD=AppPass456! \
  -v db-data:/var/lib/mysql \
  mysql:8.0

# 等待 MySQL 就绪
sleep 20

# === 初始化数据库表 ===
docker exec db mysql -utechcorp_app -pAppPass456! techcorp_db -e "
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO messages (content) VALUES ('欢迎来到TechCorp！'), ('Docker部署成功！');
"

# === 启动 Redis 容器 ===
docker run -d --name redis \
  --network techcorp-net \
  redis:7-alpine redis-server --requirepass RedisPass2026!

# === 启动 Backend 容器 ===
docker run -d --name backend \
  --network techcorp-net \
  -e DB_HOST=db \
  -e REDIS_HOST=redis \
  -e REDIS_PASSWORD=RedisPass2026! \
  -p 5000:5000 \
  techcorp-backend:v1

sleep 3

# === 测试 Backend ===
curl http://localhost:5000/api/health
curl http://localhost:5000/api/messages

# === 启动 Frontend 容器 ===
docker run -d --name frontend \
  --network techcorp-net \
  -p 80:80 \
  -v $(pwd)/docker/frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
  -v $(pwd)/docker/frontend/index.html:/usr/share/nginx/html/index.html:ro \
  nginx:alpine

sleep 2

# === 全链路测试 ===
curl -s http://localhost | head -5          # 前端页面
curl http://localhost/api/stats             # API 统计
curl -X POST http://localhost/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"Docker全链路通了！"}'
curl http://localhost/api/messages | python3 -m json.tool
```

> **验收点**：浏览器访问 `http://VM_IP` → 官网页面 + 留言板功能正常。

### 环节4：Git 提交（20分钟）

```bash
cd ~/techcorp-project
mkdir -p docker-compose
cp -r docker/ docker-compose/ 2>/dev/null

git add docker/ docker-compose/
git commit -m "v3.0: Docker容器化完成 - 4个容器独立运行"
git tag docker-deploy-v1
git log --oneline
```

---

## 第6次大课：Docker Compose 编排 + 排障（U71 · 90分钟）

### 环节1：编写 compose.yaml（30分钟）

```bash
cd ~/techcorp-project

# 创建初始化 SQL
cat > init.sql << 'EOF'
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT INTO messages (content) VALUES ('欢迎来到TechCorp！'), ('Compose编排部署成功！');
EOF

# 编写 compose.yaml
cat > compose.yaml << 'EOF'
services:
  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./docker/frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./docker/frontend/index.html:/usr/share/nginx/html/index.html:ro
    depends_on:
      - backend
    networks:
      - techcorp-net
    restart: always

  backend:
    build: ./docker/backend
    environment:
      DB_HOST: db
      REDIS_HOST: redis
      REDIS_PASSWORD: RedisPass2026!
    depends_on:
      - db
      - redis
    networks:
      - techcorp-net
    restart: always

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: DBroot123!
      MYSQL_DATABASE: techcorp_db
      MYSQL_USER: techcorp_app
      MYSQL_PASSWORD: AppPass456!
    volumes:
      - db_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - techcorp-net
    restart: always

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass RedisPass2026!
    volumes:
      - redis_data:/data
    networks:
      - techcorp-net
    restart: always

volumes:
  db_data:
  redis_data:

networks:
  techcorp-net:
EOF
```

### 环节2：一键部署（20分钟）

```bash
# 先停掉之前手动启动的容器
docker rm -f frontend backend db redis 2>/dev/null

# 一键启动
docker compose up -d --build

# 等 MySQL 初始化
sleep 25

# 查看状态
docker compose ps
# 应该4个服务都是 Up

# 查看日志
docker compose logs backend | tail -10

# 全链路测试
curl -s http://localhost | head -5
curl http://localhost/api/health
curl -X POST http://localhost/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"Compose一键部署成功！"}'
curl http://localhost/api/messages | python3 -m json.tool
curl http://localhost/api/stats
```

### 环节3：数据持久化验证（10分钟）

```bash
# 停掉所有容器
docker compose down

# 确认 volume 还在
docker volume ls | grep techcorp

# 重新启动
docker compose up -d
sleep 15

# 验证数据还在
curl http://localhost/api/messages
# ✓ 之前的留言还在
curl http://localhost/api/stats
# ✓ 计数没有归零
```

### 环节4：故障模拟与排查（30分钟）

教师注入以下 3-4 个故障，学生排查。

```bash
# === 故障A：停止某个服务 ===
docker compose stop backend
# 现象：curl /api/messages 返回 502 Bad Gateway
# 排查：docker compose ps → backend 是 Exited
# 修复：docker compose start backend

# === 故障B：修改 Nginx 配置后不生效 ===
# 修改 docker/frontend/nginx.conf 中 proxy_pass 为错误地址
# 现象：curl /api/ 返回 502
# 排查：docker compose logs frontend → 看到 upstream 连接失败
# 修复：改回正确的 proxy_pass → docker compose restart frontend

# === 故障C：端口冲突 ===
# 用 Python 占 80 端口：sudo python3 -m http.server 80 &
# 现象：docker compose up -d 失败
# 排查：ss -tlnp | grep :80
# 修复：sudo kill PID

# === 故障D：MySQL 数据损坏（模拟） ===
# docker compose exec db mysql -uroot -pDBroot123! -e "DROP TABLE techcorp_db.messages;"
# 现象：curl /api/messages 返回空或报错
# 排查：docker compose logs backend → 看到 MySQL 错误
# 修复：杀掉 db 容器 → docker compose up -d → init.sql 重新建表（但数据丢了！）
# 教学点：这就是为什么需要备份。如果之前有 volume 备份，就能恢复。
```

---

## 第7次大课：项目答辩与课程总结（U72 · 90分钟）

### 环节1：项目最终整理（20分钟）

```bash
cd ~/techcorp-project

# 最终 Git 提交
git add compose.yaml init.sql docker/
git commit -m "v4.0: Docker Compose编排完成 - 最终版本"
git tag final-v1.0

# 查看完整提交历史
git log --oneline --graph --all

# 生成项目文件清单
cat > FILE_LIST.md << 'EOF'
# TechCorp 项目文件清单

## 代码
- docker/backend/app.py          Flask API 源码
- docker/backend/Dockerfile      后端镜像构建文件
- docker/frontend/index.html     前端页面
- docker/frontend/nginx.conf     Nginx配置

## 部署
- compose.yaml                   Compose编排文件
- init.sql                       数据库初始化脚本

## 文档
- REQUIREMENTS.md                需求文档
- FILE_LIST.md                   文件清单
- backups/                       数据库备份

## 脚本
- ops-check.sh                   巡检脚本
EOF

git add FILE_LIST.md
git commit -m "docs: 项目文件清单"
```

### 环节2：答辩（50分钟）

每组 15 分钟：
- **方案阐述（5分钟）**：架构设计、技术选型、项目亮点
- **实操演示（8分钟）**：从 `docker compose up -d` 开始，展示各服务正常访问
- **故障注入（2分钟）**：教师随机选 1 个故障（停止某容器/修改配置/端口占用），学生现场排查

### 环节3：课程总结（20分钟）

```
教师回顾五模块技能链：

模块一 Linux基础运维
  → 命令行、文件权限、用户管理、systemd
  
模块二 网络与远程管理
  → IP/端口/DNS、SSH、防火墙、SELinux、排障流程

模块三 企业服务部署
  → Nginx虚拟主机、MariaDB运维、Redis缓存、Git、Shell脚本

模块四 虚拟化技术
  → VMware快照克隆、KVM基础、多机环境、云服务概念

模块五 Docker容器化
  → Dockerfile、Docker网络存储、Compose编排

最终综合项目
  → 全部技能的集成应用
```

---

## 附录：教师排障速查表

| 常见学生问题 | 原因 | 教师引导提示 |
|------------|------|------------|
| Nginx 启动失败 | 80端口被占 | "先用 ss -tlnp 看看谁在用 80" |
| Flask API 500 错误 | MySQL/Redis 没连上 | "curl /api/health 看看报什么错" |
| Docker build 失败 | 网络连不上 Docker Hub | "先 ping 外网，再检查 DNS" |
| docker compose up 报错 | YAML 缩进不对 | "检查缩进——必须用空格，不能用 Tab" |
| MySQL 容器连不上 | 没等就绪就连接 | "docker logs db 看是否 ready for connections" |
| 前端 JS 调用 API 失败 | CORS 或 Nginx 反代没配 | "检查 /api/ 是否被 Nginx proxy_pass" |
| Volume 数据丢了 | docker compose down -v 了 | "记住：-v 会删数据！" |
