# Lab59：Docker Compose 入门

> 课时：2 | 类型：个人 | 前置：Lab52

## 一、你会学到什么
- 理解 Compose 解决的问题（一键管理多容器应用）
- 能编写 compose.yaml 定义多服务应用
- 能用 docker compose up/down 一键启停
- 理解 depends_on 和 networks 在 Compose 中的作用

## 二、为什么需要 Compose

```
传统方式：docker run web → docker run db → 手动创建网络 → 手动连接...
Compose方式：一个 YAML 文件定义所有服务 → docker compose up -d → 全部启动
```

## 三、实验步骤

### 步骤1：YAML 语法快速入门

```yaml
# YAML 用缩进表示层级（不能用 Tab！）
# 键值对
name: John
age: 25

# 列表
fruits:
  - apple
  - banana

# 字典
server:
  host: localhost
  port: 8080

# 多行字符串
description: |
  第一行
  第二行
```

### 步骤2：第一个 compose.yaml

```bash
mkdir -p /tmp/compose-lab && cd /tmp/compose-lab
mkdir html
echo "<h1>Compose Demo</h1>" > html/index.html

cat > compose.yaml << 'EOF'
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
    networks:
      - app-net

  redis:
    image: redis:7-alpine
    networks:
      - app-net

networks:
  app-net:
EOF
```

### 步骤3：Compose 核心命令

```bash
# 一键启动所有服务
docker compose up -d
# ✔ Network compose-lab_app-net  Created
# ✔ Container compose-lab-redis   Started
# ✔ Container compose-lab-web     Started

# 查看状态
docker compose ps
# NAME                  IMAGE           STATUS
# compose-lab-redis     redis:7-alpine  running
# compose-lab-web       nginx:alpine    running

# 查看日志
docker compose logs
docker compose logs web                # 只看 web 服务
docker compose logs -f                 # 实时跟踪

# 在服务中执行命令
docker compose exec redis redis-cli PING    # PONG
docker compose exec web nginx -v

# 重启单个服务
docker compose restart web

# 停止并删除所有资源
docker compose down
# docker compose down -v   ← 同时删除数据卷（慎用！）
```

### 步骤4：Compose 文件完整结构

```yaml
services:               # 定义容器
  web:                  # 服务名（容器名=目录名-服务名-序号）
    image: nginx:alpine # 使用已有镜像
    # 或 build: ./dir   # 从 Dockerfile 构建
    ports:
      - "8080:80"       # 端口映射
    volumes:
      - ./html:/usr/share/nginx/html:ro  # 卷挂载
      - db-data:/var/lib/mysql
    environment:        # 环境变量
      - ENV=production
      - DB_HOST=db
    env_file:           # 或从文件加载
      - .env
    depends_on:         # 启动顺序依赖
      - db
    restart: always     # 重启策略
    networks:
      - app-net

  db:
    image: mysql:8.0
    ...

volumes:                # 命名数据卷
  db-data:

networks:               # 自定义网络
  app-net:
```

### 步骤5：depends_on 的理解

```yaml
depends_on:
  - db
```

**作用**：控制启动顺序（先 db 后 web）。

**局限**：只等容器启动了，不等服务就绪！MySQL 容器启动了 ≠ MySQL 服务可接受连接了（可能需要 10-20 秒初始化）。

**生产解决方案**：在应用启动脚本中添加"等待数据库就绪"的逻辑（如 `wait-for-it.sh`），或使用 `healthcheck`。

### 步骤6：环境变量管理

```bash
# 创建 .env 文件
cat > .env << 'EOF'
MYSQL_ROOT_PASSWORD=SecretPass123!
MYSQL_DATABASE=myapp
REDIS_PASSWORD=RedisPass456!
EOF

# 在 compose.yaml 中引用
# environment:
#   MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
```

---

## 五、练习题

### 练习1：Compose 与 docker run 互译（20分）

将以下 docker run 命令转换成 compose.yaml：

```bash
docker run -d --name my-nginx -p 80:80 -v /data:/usr/share/nginx/html nginx:alpine
docker run -d --name my-redis -p 6379:6379 redis:7-alpine
```

### 练习2：WordPress 一键部署（30分）

用 Compose 部署 WordPress（wordpress + mysql 两个服务），参考 Lab60 的结构自己写 compose.yaml。

### 练习3：Compose 生命周期（20分）

1. `docker compose down` 和 `docker compose down -v` 的区别
2. `docker compose stop` 和 `docker compose down` 的区别
3. `docker compose restart` 和 `docker compose down && docker compose up -d` 的区别

### 练习4：多环境 Compose（15分）

1. 创建 `docker-compose.override.yml` 用于开发环境（暴露调试端口、挂载本地代码）
2. Compose 如何自动合并多个文件？

### 练习5：Compose 排障（15分）

| 问题 | 排查方法 |
|------|---------|
| 服务启动失败 | |
| 服务间网络不通 | |
| depends_on 不生效 | |

## 七、常见问题

**Q: docker compose 和 docker-compose 有什么区别？**
A: docker compose（空格）是 Docker 插件（docker compose plugin），docker-compose（横杠）是老旧的独立 Python 工具。新版 Docker 内置了 compose 插件，推荐用 `docker compose`。

**Q: depends_on 能保证服务就绪吗？**
A: 不能。depends_on 只控制启动顺序，MySQL 容器启动了 ≠ MySQL 服务可接受连接了（可能需要 10-20 秒初始化）。生产环境建议用 healthcheck + depends_on condition: service_healthy。

**Q: docker compose down 和 docker compose down -v 的区别？**
A: down 停止并删除容器和网络。加 -v 同时删除 volumes（数据永久删除！）。生产环境注意不要带 -v 除非你确定要删除数据。

## 八、课后思考

1. Docker Compose 适合单机部署。如果公司有 10 台服务器需要部署同一套应用，Docker Compose 还够用吗？需要什么工具？（提示：Docker Swarm、Kubernetes、Nomad）

2. Compose 文件中可以写 `build:` 从 Dockerfile 构建，也可以写 `image:` 使用已构建的镜像。生产部署时应该用哪种方式？为什么？
