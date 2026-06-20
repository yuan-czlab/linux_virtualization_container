# Lab61：Compose 综合项目实战——留言板应用完整部署

> 课时：2 | 类型：双人/个人 | 前置：Lab60

## 一、项目目标

从零部署一个完整的多层 Web 应用：前端 HTML/JS → Nginx 反向代理 → Python Flask API → MySQL 存储 + Redis 计数。

## 二、项目结构

```
message-board/
├── compose.yaml
├── frontend/
│   ├── nginx.conf          # Nginx 反向代理配置
│   └── html/
│       └── index.html      # 留言板前端页面
├── backend/
│   ├── Dockerfile
│   ├── app.py              # Flask API
│   └── requirements.txt
└── init.sql                # 数据库初始化 SQL
```

## 三、实验步骤

### 步骤1：创建项目目录和文件

```bash
mkdir -p /tmp/message-board/{frontend/html,backend}
cd /tmp/message-board
```

### 步骤2：编写后端 Flask API

```bash
cat > backend/app.py << 'EOF'
from flask import Flask, jsonify, request
import redis, pymysql, os, datetime

app = Flask(__name__)
r = redis.Redis(host=os.getenv('REDIS_HOST','redis'), port=6379,
                password=os.getenv('REDIS_PASSWORD',''), decode_responses=True)

def get_db():
    return pymysql.connect(
        host=os.getenv('DB_HOST','db'), user='appuser',
        password='AppPass123!', database='message_board',
        autocommit=True)

@app.route('/api/health')
def health():
    try:
        r.ping()
        db_ok = "connected"
    except:
        db_ok = "error"
    return jsonify({'status':'ok','redis':r.ping(),'db':db_ok,
                    'time':str(datetime.datetime.now())})

@app.route('/api/messages', methods=['GET','POST'])
def messages():
    db = get_db()
    if request.method == 'POST':
        data = request.get_json()
        msg = data.get('message','')
        if msg.strip():
            cur = db.cursor()
            cur.execute("INSERT INTO messages (content) VALUES (%s)", (msg,))
            cur.close()
            r.incr('total_messages')
            return jsonify({'status':'ok'})
        return jsonify({'status':'error','msg':'empty message'}), 400

    cur = db.cursor()
    cur.execute("SELECT id, content, created_at FROM messages ORDER BY id DESC LIMIT 20")
    rows = cur.fetchall()
    cur.close()
    return jsonify([{'id':r[0],'content':r[1],'time':str(r[2])} for r in rows])

@app.route('/api/stats')
def stats():
    return jsonify({
        'total_messages': int(r.get('total_messages') or 0),
        'redis_keys': r.dbsize()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF

cat > backend/requirements.txt << 'EOF'
flask==3.0.0
redis==5.0.0
pymysql==1.1.0
EOF

cat > backend/Dockerfile << 'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
USER 1000
CMD ["python", "app.py"]
EOF
```

### 步骤3：编写前端

```bash
cat > frontend/nginx.conf << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        root /usr/share/nginx/html;
        index index.html;
    }

    location /api/ {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

cat > frontend/html/index.html << 'HTML'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>📝 留言板 - Docker Compose 项目</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;max-width:600px;margin:30px auto;padding:0 20px;background:#f5f5f5}
h1{color:#333;margin-bottom:20px;text-align:center}
.card{background:white;padding:15px;border-radius:8px;margin-bottom:15px;box-shadow:0 1px 3px rgba(0,0,0,0.1)}
.card small{color:#999;font-size:12px}
input{width:100%;padding:10px;margin:10px 0;border:1px solid #ddd;border-radius:4px;font-size:14px}
button{width:100%;padding:10px;background:#4CAF50;color:white;border:none;border-radius:4px;cursor:pointer;font-size:14px}
button:hover{background:#45a049}
.stats{text-align:center;color:#666;margin:15px 0;font-size:14px}
</style>
</head>
<body>
<h1>📝 Docker 留言板</h1>
<div class="stats" id="stats">加载中...</div>
<input id="msgInput" placeholder="输入留言..." maxlength="200">
<button onclick="sendMsg()">发送留言</button>
<div id="messages">加载中...</div>

<script>
const API = '/api/messages';
async function loadMsgs(){
    try{
        const r=await fetch(API);
        const msgs=await r.json();
        document.getElementById('messages').innerHTML=msgs.map(m=>
            `<div class="card">${m.content}<br><small>${m.time}</small></div>`
        ).join('')||'<div class="card">暂无留言</div>';
    }catch(e){document.getElementById('messages').innerHTML='<div class="card">加载失败</div>'}
}
async function sendMsg(){
    const msg=document.getElementById('msgInput').value.trim();
    if(!msg)return;
    await fetch(API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
    document.getElementById('msgInput').value='';
    loadMsgs();loadStats();
}
async function loadStats(){
    try{
        const r=await fetch('/api/stats');
        const s=await r.json();
        document.getElementById('stats').textContent=`总留言: ${s.total_messages} | Redis Keys: ${s.redis_keys}`;
    }catch(e){}
}
loadMsgs();loadStats();
</script>
</body></html>
HTML
```

### 步骤4：编写 compose.yaml

```bash
cat > compose.yaml << 'EOF'
services:
  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./frontend/html:/usr/share/nginx/html:ro
    depends_on:
      - backend
    networks:
      - app-net
    restart: always

  backend:
    build: ./backend
    environment:
      DB_HOST: db
      REDIS_HOST: redis
      REDIS_PASSWORD: RedisPass2026!
    depends_on:
      db:
        condition: service_started
      redis:
        condition: service_started
    networks:
      - app-net
    restart: always

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: RootPass123!
      MYSQL_DATABASE: message_board
      MYSQL_USER: appuser
      MYSQL_PASSWORD: AppPass123!
    volumes:
      - db_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    networks:
      - app-net
    restart: always

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass RedisPass2026!
    volumes:
      - redis_data:/data
    networks:
      - app-net
    restart: always

volumes:
  db_data:
  redis_data:

networks:
  app-net:
EOF
```

### 步骤5：数据库初始化 SQL

```bash
cat > init.sql << 'EOF'
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
EOF
```

### 步骤6：一键部署并验证

```bash
docker compose up -d --build
sleep 25    # 等 MySQL 初始化

# 验证
docker compose ps                              # 4个服务都应该 Up

# 测试 API
curl http://localhost/api/health               # {"status":"ok",...}
curl http://localhost/api/stats                # {"total_messages":0,...}
curl -X POST http://localhost/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello Docker Compose!"}'     # {"status":"ok"}
curl http://localhost/api/messages             # 看到刚才的留言

# 浏览器访问 http://VM_IP → 完整的留言板界面
```

### 步骤7：持久化验证

```bash
# 停掉所有容器
docker compose down

# 确认 volume 还在
docker volume ls | grep message-board

# 重新启动
docker compose up -d
sleep 15

# 验证数据还在
curl http://localhost/api/messages
# ✓ 之前的留言还在
curl http://localhost/api/stats
# ✓ 计数仍然正确
```

---

## 五、练习题

### 练习1：架构图绘制（15分）

画出本项目的完整架构图，标注：用户 → Nginx → Flask → MySQL + Redis 的数据流向。

### 练习2：添加新功能（25分）

给留言板添加以下功能之一：
1. 删除留言功能（DELETE /api/messages/:id）
2. 留言点赞功能（PUT /api/messages/:id/like，用 Redis INCR）
3. 用户昵称（修改前端和后端）

### 练习3：故障恢复测试（25分）

1. 杀掉 backend 容器 → 验证自动重启
2. 杀掉 db 容器 → 验证数据不丢
3. 杀掉 redis 容器 → 验证计数恢复

### 练习4：Nginx 负载均衡（20分）

修改 compose.yaml，将 backend 扩展到 3 个实例（`docker compose up -d --scale backend=3`），验证 Nginx 默认轮询负载均衡。

### 练习5：部署文档编写（15分）

编写完整的部署文档，包含：
- 系统架构说明
- 部署步骤
- 配置说明
- 故障排查指南
- 数据备份方法

## 七、常见问题

**Q: 项目部署后前端跨域请求失败（CORS error）？**
A: 检查 Nginx 反向代理配置是否正确。前后端分离架构中，应由 Nginx 将 /api/ 路径代理到 backend，避免浏览器跨域问题。

**Q: Compose 启动后 MySQL 连接失败 "Connection refused"？**
A: MySQL 容器启动了但服务可能还没就绪（初始化需要 15-30 秒）。解决方案：① backend 添加重试逻辑；② 在 depends_on 中使用 healthcheck condition。

**Q: 生产环境 Compose 项目怎么更新？**
A: ① git pull 最新代码；② `docker compose up -d --build` 重建变化的服务；③ 验证新版本正常运行。建议配合 CI/CD 工具自动化。

## 八、课后思考

1. 回顾整个课程，你从"安装 Linux 系统"一路学到了"用 Docker Compose 部署完整应用"。画出你的技能成长路线图。

2. 下一步学什么？根据你的职业方向（系统运维/云计算运维/DevOps），列出 3 个接下来应该深入学习的技术。
