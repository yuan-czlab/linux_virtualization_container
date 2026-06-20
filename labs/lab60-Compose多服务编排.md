# Lab60：Docker Compose 多服务编排

> 课时：2 | 类型：个人 | 前置：Lab59

## 一、你会学到什么
- 能用 Compose 编排 Web + API + DB + Cache 四层应用
- 能通过自定义网络让服务通过容器名互访
- 能使用数据卷持久化数据库和缓存
- 能编写完整可用的 compose.yaml

## 二、实验步骤

### 步骤1：WordPress 一键部署

```bash
mkdir -p /tmp/wp-compose && cd /tmp/wp-compose

cat > compose.yaml << 'EOF'
services:
  db:
    image: mysql:8.0
    volumes:
      - db_data:/var/lib/mysql
    environment:
      MYSQL_ROOT_PASSWORD: RootPass123!
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wpuser
      MYSQL_PASSWORD: WpPass123!
    networks:
      - wp-net
    restart: always

  wordpress:
    image: wordpress:php8.3-apache
    depends_on:
      - db
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wpuser
      WORDPRESS_DB_PASSWORD: WpPass123!
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wp_data:/var/www/html
    networks:
      - wp-net
    restart: always

volumes:
  db_data:
  wp_data:

networks:
  wp-net:
EOF
```

```bash
docker compose up -d

# 等 MySQL 初始化（约 20 秒）
sleep 25
docker compose ps
# 两个服务都应该 running

# 浏览器访问 http://VM_IP:8080 → WordPress 安装向导！
```

### 步骤2：验证网络和数据持久化

```bash
# wordpress 容器通过容器名 db 连接 MySQL
docker compose exec wordpress bash -c "getent hosts db"
# 172.x.x.x  db  ← 容器名被解析为 IP

# 数据持久化验证
docker compose exec db mysql -uwpuser -pWpPass123! wordpress -e "SHOW TABLES;"

# 删除所有容器
docker compose down

# 重新启动（volume 还在！）
docker compose up -d
sleep 15
# 浏览器访问 → 之前的配置还在！✓
```

### 步骤3：编排自定义四层应用

部署架构：
```
用户 → Nginx(80) → Python Flask(5000) → MySQL(3306)
                                       → Redis(6379)
```

```bash
mkdir -p /tmp/fullstack && cd /tmp/fullstack
mkdir backend

# 后端 Flask API
cat > backend/app.py << 'EOF'
from flask import Flask, jsonify, request
import redis, pymysql, os, datetime

app = Flask(__name__)
r = redis.Redis(host=os.getenv('REDIS_HOST','redis'), port=6379, decode_responses=True)

def get_db():
    return pymysql.connect(
        host=os.getenv('DB_HOST','db'), user='appuser',
        password='AppPass123!', database='appdb')

@app.route('/health')
def health():
    return jsonify({'status':'ok', 'time':str(datetime.datetime.now())})

@app.route('/api/count')
def count():
    c = r.incr('api_count')
    return jsonify({'count': c})

@app.route('/api/users')
def users():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, name, email FROM users")
    return jsonify(cur.fetchall())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
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
CMD ["python", "app.py"]
EOF

# compose.yaml
cat > compose.yaml << 'EOF'
services:
  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    networks:
      - app-net

  backend:
    build: ./backend
    environment:
      DB_HOST: db
      REDIS_HOST: redis
    depends_on:
      - db
      - redis
    networks:
      - app-net

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: RootPass123!
      MYSQL_DATABASE: appdb
      MYSQL_USER: appuser
      MYSQL_PASSWORD: AppPass123!
    volumes:
      - db_data:/var/lib/mysql
    networks:
      - app-net

  redis:
    image: redis:7-alpine
    networks:
      - app-net

volumes:
  db_data:

networks:
  app-net:
EOF
```

```bash
docker compose up -d --build
sleep 20

# 初始化数据库
docker compose exec db mysql -uappuser -pAppPass123! appdb -e "
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(100)
);
INSERT INTO users (name, email) VALUES ('Alice','alice@test.com'),('Bob','bob@test.com');
"

# 测试
curl http://localhost/health        # 需要 Nginx 反代配置
curl http://localhost:5000/health    # 直接访问 backend
```

---

## 五、练习题

### 练习1：Compose 文件分析（15分）

分析上面的四层 compose.yaml，回答：
1. 共有几个网络？几个数据卷？
2. backend 怎么知道 db 的地址？
3. `build: ./backend` 和 `image: nginx:alpine` 的区别

### 练习2：添加 Redis 密码（20分）

修改 compose.yaml 让 Redis 启用密码认证，backend 使用密码连接。

### 练习3：healthcheck 配置（25分）

给 db 服务添加 healthcheck：
```yaml
healthcheck:
  test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
  interval: 10s
  timeout: 5s
  retries: 3
```
backend 的 depends_on 添加 `condition: service_healthy`，确保 db 真正就绪后才启动 backend。

### 练习4：多环境配置文件（20分）

1. 创建 `docker-compose.override.yml`，在开发环境中：
   - frontend 挂载本地 html 目录
   - backend 设置 `FLASK_DEBUG=1`
   - 暴露所有调试端口

2. 验证 `docker compose up -d` → override 自动合并

### 练习5：从 Git 部署（20分）

写一份 SOP：用 Compose 从 Git 仓库部署应用的标准流程。包含：git clone → docker compose up -d → 验证 → 清理

## 七、常见问题

**Q: Compose 中多个服务怎么共享数据？**
A: 在 volumes 段声明命名数据卷，多个服务可以引用同一个卷。但要注意并发读写安全——MySQL 的 volume 不能两个实例同时使用。

**Q: Compose 环境变量优先级？**
A: ① docker-compose.override.yml 中的值 > compose.yaml 中的值；② shell 环境变量 > .env 文件 > compose 中写的值；③ `docker compose --env-file` 指定的文件优先级最高。

**Q: Compose 文件怎么管理多环境（dev/staging/prod）？**
A: 方案1：多个 compose 文件（compose.yaml + compose.override.yaml）。方案2：使用 `--env-file` 指定不同环境变量。方案3：使用 `-f` 指定不同配置文件。

## 八、课后思考

1. 本实验中你手动编排了 4 个服务（frontend/backend/db/redis）。如果 backend 需要扩展到 3 个实例实现负载均衡，Compose 怎么做？Nginx 怎么配置 upstream？

2. Docker Compose 和 Kubernetes 的 YAML 配置有什么异同？如果你学会了 Compose，迁移到 K8s 还需要学什么？
