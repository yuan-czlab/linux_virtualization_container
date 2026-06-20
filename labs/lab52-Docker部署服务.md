# Lab52：Docker 数据卷与网络

> 课时：2 | 类型：个人 | 前置：Lab51

## 一、你会学到什么
- 理解容器删除=数据丢失，需要用 Volume 持久化
- 能创建和使用 named volume
- 能区分 bind mount 和 volume
- 能用自定义网络让容器通过名称互相访问

## 二、实验步骤

### 第一部分：数据卷

### 步骤1：演示数据丢失问题

```bash
# 创建 MySQL 容器并建库
docker run -d --name temp-mysql \
  -e MYSQL_ROOT_PASSWORD=pass123 \
  mysql:8.0

sleep 20  # 等 MySQL 启动
docker exec temp-mysql mysql -uroot -ppass123 -e "CREATE DATABASE testdb;"
docker exec temp-mysql mysql -uroot -ppass123 -e "SHOW DATABASES;" | grep testdb
# testdb ✓

# 删除容器
docker rm -f temp-mysql

# 重新运行 → 数据库没了！
docker run -d --name temp-mysql2 \
  -e MYSQL_ROOT_PASSWORD=pass123 \
  mysql:8.0
sleep 15
docker exec temp-mysql2 mysql -uroot -ppass123 -e "SHOW DATABASES;" | grep testdb
# ✗ 没有 testdb！数据丢了
docker rm -f temp-mysql2
```

### 步骤2：使用 Volume 持久化

```bash
# 创建命名数据卷
docker volume create mysql-data

# 查看数据卷
docker volume ls
docker volume inspect mysql-data
# "Mountpoint": "/var/lib/docker/volumes/mysql-data/_data"
# 这就是数据在宿主机上的实际存储位置

# 使用数据卷启动 MySQL
docker run -d --name mysql-persist \
  -e MYSQL_ROOT_PASSWORD=RootPass123! \
  -v mysql-data:/var/lib/mysql \
  -p 3307:3306 \
  mysql:8.0

# -v 数据卷名:容器内路径
# mysql-data → 挂载到容器的 /var/lib/mysql（MySQL 数据目录）
```

### 步骤3：验证数据持久化

```bash
sleep 20
# 创建数据库和表
docker exec mysql-persist mysql -uroot -pRootPass123! -e "
CREATE DATABASE myapp;
USE myapp;
CREATE TABLE users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50));
INSERT INTO users (name) VALUES ('Alice'), ('Bob');
SELECT * FROM users;
"

# 删除容器（但保留 volume！）
docker rm -f mysql-persist

# 用同一个 volume 重新启动
docker run -d --name mysql-restored \
  -e MYSQL_ROOT_PASSWORD=RootPass123! \
  -v mysql-data:/var/lib/mysql \
  mysql:8.0

sleep 10
docker exec mysql-restored mysql -uroot -pRootPass123! -e "SELECT * FROM myapp.users;"
# ✓ Alice, Bob 数据还在！
```

### 步骤4：bind mount vs volume

```bash
# bind mount：宿主机具体路径 → 容器路径（开发常用）
mkdir /tmp/nginx-html
echo "<h1>Bind Mount Test</h1>" > /tmp/nginx-html/index.html

docker run -d --name bind-demo -p 8082:80 \
  -v /tmp/nginx-html:/usr/share/nginx/html:ro \
  nginx:alpine
# :ro = 只读挂载，容器不能修改

curl http://localhost:8082        # ✓ Bind Mount Test

# 修改宿主机文件
echo "<h1>Updated on host</h1>" > /tmp/nginx-html/index.html
curl http://localhost:8082        # ✓ Updated on host（实时生效！）

# named volume：Docker 管理（生产推荐）
# bind mount：宿主机路径直接映射（开发调试方便）

docker rm -f bind-demo
```

### 步骤5：Volume 备份

```bash
# 用临时容器备份 volume 数据
docker run --rm \
  -v mysql-data:/data \
  -v /tmp/backup:/backup \
  alpine \
  tar czf /backup/mysql-backup-$(date +%Y%m%d).tar.gz -C /data .

ls -lh /tmp/backup/
```

### 第二部分：Docker 网络

### 步骤6：默认 bridge 网络的局限

```bash
docker run -d --name net-a nginx:alpine
docker run -d --name net-b nginx:alpine

# 获取 net-a 的 IP
docker inspect net-a | grep IPAddress
# "IPAddress": "172.17.0.2"

# net-b 可以通过 IP ping 通 net-a
docker exec net-b ping -c 2 172.17.0.2    # ✓

# 但用容器名不行（默认 bridge 没有 DNS）
docker exec net-b ping -c 2 net-a
# ping: bad address 'net-a'               # ✗

docker rm -f net-a net-b
```

### 步骤7：自定义网络（推荐）

```bash
# 创建自定义 bridge 网络
docker network create my-net

# 查看网络
docker network ls
docker network inspect my-net | head -20

# 两个容器都加入 my-net
docker run -d --name web --network my-net nginx:alpine
docker run -d --name app --network my-net alpine sleep 3600

# 现在可以通过容器名互相访问！
docker exec app ping -c 2 web
# PING web (172.18.0.2): 56 data bytes
# 64 bytes from 172.18.0.2: ... ✓
# 自定义网络自带 DNS 解析！
```

### 步骤8：网络模式对比

```bash
# bridge（默认）：docker0 网桥，容器间 IP 通信，无 DNS
# 自定义 bridge：自带 DNS，推荐生产使用

# host 模式：容器共享宿主机网络栈
docker run -d --name host-nginx --network host nginx:alpine
# 不需要 -p！直接占用宿主机 80 端口
curl http://localhost              # ✓
docker rm -f host-nginx

# none 模式：无网络
docker run --rm --network none alpine ip a
# 只有 lo 回环，没有 eth0
```

---

## 五、练习题

### 练习1：Volume 持久化验证（20分）

1. 创建 Redis 容器，使用 volume 持久化
2. 写入数据（SET mykey "persistent"）
3. 删除容器
4. 重新创建容器（用同一个 volume）
5. 验证数据还在（GET mykey）

### 练习2：多容器自定义网络（25分）

1. 创建网络 `app-network`
2. 在网络上启动 Nginx + 2 个 Alpine 容器
3. 验证三个容器可以通过容器名互相 ping 通
4. 对比：如果不用自定义网络，容器名能 ping 通吗？

### 练习3：bind mount 开发场景（20分）

模拟开发场景：
1. 本地有一个网站目录 `/tmp/my-site/`，包含 index.html
2. 用 bind mount 挂载到 Nginx 容器
3. 修改本地 index.html → 验证容器内实时生效
4. 为什么开发环境推荐 bind mount？（实时修改，不需要重建镜像）

### 练习4：Volume 数据备份恢复（20分）

1. 备份 mysql-data 卷的数据
2. 删除 mysql-data 卷
3. 从备份恢复数据到新卷
4. 验证数据完整

### 练习5：容器网络排障（15分）

以下场景，排查网络问题：

| 现象 | 排查步骤 |
|------|---------|
| 容器 A ping 不通容器 B 的 IP | |
| 容器 A ping 不通容器 B 的容器名 | |
| 容器内 curl 不通外网 | |

## 七、常见问题

**Q: volume 和 bind mount 什么时候用哪个？**
A: 生产环境数据 → named volume（Docker 管理，可移植，支持驱动）。开发调试 → bind mount（实时同步本地文件）。数据库数据 → named volume 或外挂磁盘。

**Q: 容器间通信推荐什么方式？**
A: 自定义 bridge 网络（自带 DNS，容器名互访）。不推荐默认 bridge（无 DNS，依赖 IP 会变）和 --link（已废弃）。

**Q: host 网络模式有什么风险？**
A: 容器直接使用宿主机端口，端口冲突风险高，隔离性差。仅适合高性能场景或需要访问宿主机网络的特殊情况。

## 八、课后思考

1. Docker 网络和你在 M4 学的 KVM 虚拟网络（NAT/桥接/隔离）有哪些相似之处？Docker 的自定义 bridge 对应 KVM 的哪种网络？

2. 如果 MySQL 容器删了但 volume 还在，磁盘空间会不会被 volume 占满？你作为运维怎么监控和清理 Docker 占用的磁盘空间？
