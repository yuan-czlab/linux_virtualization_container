# Lab51：Docker 容器基础操作

> 课时：2 | 类型：个人 | 前置：Lab50

## 一、你会学到什么
- 能手写 `docker run` 的常用参数
- 能管理容器生命周期（启动/停止/删除/查看日志/进入容器）
- 能区分容器的运行状态和退出原因

## 二、实验步骤

### 步骤1：运行第一个容器

```bash
# 运行 Nginx 容器（后台模式）
docker run -d --name web1 -p 8080:80 nginx:alpine

# 参数详解：
# -d              后台运行（detached），不占用终端
# --name web1     给容器命名（不指定则随机生成）
# -p 8080:80      端口映射：宿主机8080 → 容器80
# nginx:alpine    使用的镜像

# 验证
docker ps
# CONTAINER ID  IMAGE          PORTS                  NAMES
# a1b2c3d4e5f6  nginx:alpine   0.0.0.0:8080->80/tcp  web1

curl http://localhost:8080         # ✓ Nginx 欢迎页
```

### 步骤2：docker run 常用参数

```bash
# 交互式容器（进入命令行）
docker run -it --name test-alpine alpine sh
# 在容器内：ls /, cat /etc/os-release, exit 退出

# --rm：退出后自动删除容器（临时容器推荐）
docker run --rm -it alpine echo "I'm temporary"
docker ps -a | grep temporary     # 找不到，自动删了

# -e：设置环境变量
docker run -d --name mysql-test \
  -e MYSQL_ROOT_PASSWORD=TestPass123! \
  -p 3307:3306 \
  mysql:8.0

# --restart：容器退出时自动重启
# --restart=always   总是重启
# --restart=on-failure:3  失败时重启，最多3次
```

### 步骤3：容器生命周期管理

```bash
# 查看所有容器（包括已停止的）
docker ps -a
# STATUS 列：Up 2 minutes / Exited (0) 5 minutes ago / Exited (1) ...

# 停止容器
docker stop web1                    # 优雅停止（SIGTERM → 等10秒 → SIGKILL）
docker ps -a | grep web1           # STATUS: Exited (0)

# 启动已停止的容器
docker start web1
docker ps | grep web1              # STATUS: Up

# 重启
docker restart web1

# 暂停/恢复（暂停进程但不停止容器）
docker pause web1
docker unpause web1

# 强制删除（即使正在运行）
docker rm -f web1
docker rm -f test-alpine
```

### 步骤4：查看容器信息

```bash
docker run -d --name web2 -p 8081:80 nginx:alpine

# 查看日志
docker logs web2                     # 全部日志
docker logs --tail 10 web2           # 最后10行
docker logs -f web2                  # 实时跟踪（Ctrl+C退出）

# 查看容器详情（JSON格式，信息非常全）
docker inspect web2 | head -40
# 可以查到：IP地址、挂载信息、网络配置、环境变量...

# 查看资源使用
docker stats --no-stream web2
# CONTAINER  CPU %  MEM USAGE / LIMIT   MEM %  NET I/O      BLOCK I/O

# 查看容器内进程
docker top web2
```

### 步骤5：进入运行中的容器

```bash
# docker exec：在运行中的容器里执行命令
docker exec web2 nginx -v            # 查看 Nginx 版本
docker exec web2 ls /etc/nginx/      # 查看容器内文件

# 进入容器交互式 shell
docker exec -it web2 bash
# 现在你在容器内部！
# ls /, ps aux, cat /etc/nginx/nginx.conf
# exit 退出（容器继续运行）

# 对比：docker attach（连接到容器的主进程，不常用）
# Ctrl+P Ctrl+Q 可以安全脱离而不停止容器
```

### 步骤6：宿主机 ↔ 容器文件传输

```bash
# 从宿主机复制到容器
echo "<h1>Copied from host</h1>" > /tmp/host-file.html
docker cp /tmp/host-file.html web2:/usr/share/nginx/html/test.html
curl http://localhost:8081/test.html   # ✓ 能看到

# 从容器复制到宿主机
docker cp web2:/etc/nginx/nginx.conf /tmp/container-nginx.conf
head -5 /tmp/container-nginx.conf     # ✓ 容器里的配置
```

### 步骤7：容器退出状态码

```bash
# 成功退出
docker run --rm alpine echo "done"
docker ps -a | head -2               # 看不到（--rm 自动删除）
# 退出码 0 = 正常退出

# 异常退出
docker run --name bad alpine false
docker ps -a | grep bad
# STATUS: Exited (1) ...             # 退出码 1 = 异常
docker logs bad                       # 查看退出原因
docker rm bad
```

---

## 五、练习题

### 练习1：docker run 参数填空（15分）

| 需求 | 参数 | 完整命令示例 |
|------|------|------------|
| 后台运行 Nginx | | |
| 交互式进入 Alpine | | |
| 端口映射 9090→80 | | |
| 自动删除临时容器 | | |
| 设置环境变量 | | |

### 练习2：容器生命周期（20分）

画出容器生命周期状态图：created → running → paused → stopped → deleted

### 练习3：部署 MySQL + Redis（30分）

1. 用 Docker 部署 MySQL 容器（端口 3307，root 密码 MyPass123!）
2. 用 Docker 部署 Redis 容器（端口 6380）
3. 分别验证 MySQL 和 Redis 可用
4. 用 `docker ps` 确认两个容器都在运行
5. 用 `docker logs` 查看 MySQL 启动日志

### 练习4：容器调试（20分）

1. 进入 MySQL 容器内部，用 `mysql` 命令连接数据库
2. 进入 Redis 容器内部，用 `redis-cli` 测试
3. 从宿主机复制一个 SQL 文件到 MySQL 容器
4. 从 Nginx 容器复制配置文件到宿主机

### 练习5：容器退出码分析（15分）

| 退出码 | 含义 | 常见原因 |
|--------|------|---------|
| 0 | | |
| 1 | | |
| 137 | | |
| 143 | | |

## 七、常见问题

**Q: docker run 和 docker start 有什么区别？**
A: run = create + start（创建新容器并启动）。start = 启动一个已存在但停止的容器。每次 run 都创建新容器，start 不会。

**Q: 容器退出后数据还在吗？**
A: 容器的文件系统还在（docker ps -a 能看到），直到 `docker rm` 删除容器。但容器数据随容器删除而丢失，除非使用了 volume。这就是为什么需要数据卷。

**Q: docker exec 和 docker attach 有什么区别？**
A: exec 在运行中的容器里启动新进程（最常用）。attach 连接到容器的主进程的 stdin/stdout（退出会停止容器）。日常用 exec。

## 八、课后思考

1. 容器的文件系统是临时的（删容器=数据丢）。这和"不可变基础设施"的思想有什么关系？为什么这种"临时性"反而是优势？

2. docker run 有几十个参数。你不需要记住全部——哪些参数是日常必用的（Top 5）？哪些是安全和生产环境必加的？
