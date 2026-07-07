# Lab52：Docker部署Nginx、MySQL与Redis

> 课时：2 | 类型：个人 | 前置：Lab51

## 一、你会学到什么

- 能从镜像说明识别端口、环境变量、配置和数据目录
- 能使用容器部署Nginx、MySQL和Redis
- 能用日志、端口和客户端命令验证服务，而不只看容器状态
- 能避免把数据库和Redis端口无条件暴露到外部网络
- 能形成三种服务的容器运行参数表

## 二、原理速览

```text
镜像 + 运行参数（名称/端口/环境变量/卷/网络）= 可运行容器
容器状态Up ≠ 应用已就绪
```

服务验证至少包含三层：

1. `docker ps`：容器进程是否运行。
2. `docker logs`和容器内客户端：应用是否初始化成功。
3. 宿主机或测试容器访问：服务是否真的可用。

本实验只引入必要的数据卷和自定义网络。卷备份、SELinux标签和网络深入分别在Lab54、Lab55学习。

## 三、实验环境

- Rocky Linux 9，Docker Engine与Compose插件已安装
- 教师已提供或预加载：`nginx:alpine`、`mysql:8.0`、`redis:7-alpine`
- 建议可用内存不少于4GB、磁盘不少于10GB

创建实验网络：

```bash
docker network create lab52-net 2>/dev/null || true
docker network inspect lab52-net
```

## 四、实验步骤

### 步骤1：部署Nginx静态网站

```bash
mkdir -p ~/lab52/html
cat > ~/lab52/html/index.html <<'HTML'
<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>Lab52</title></head>
<body><h1>Nginx container is running</h1></body>
</html>
HTML

docker run -d --name lab52-nginx \
  --network lab52-net \
  -p 8080:80 \
  -v "$HOME/lab52/html:/usr/share/nginx/html:ro,Z" \
  nginx:alpine

docker ps --filter name=lab52-nginx
docker logs lab52-nginx
curl -fsS http://127.0.0.1:8080
```

检查容器配置：

```bash
docker inspect --format 'Image={{.Config.Image}} IP={{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' lab52-nginx
docker port lab52-nginx
ss -lntp | grep :8080
```

> **验收点**：宿主机访问8080返回自定义页面；能够说明宿主8080和容器80的区别。

### 步骤2：部署MySQL并等待就绪

```bash
docker volume create lab52-mysql-data

docker run -d --name lab52-mysql \
  --network lab52-net \
  -e MYSQL_ROOT_PASSWORD='LabRoot2026!' \
  -e MYSQL_DATABASE='lab52db' \
  -e MYSQL_USER='labuser' \
  -e MYSQL_PASSWORD='LabUser2026!' \
  -v lab52-mysql-data:/var/lib/mysql \
  mysql:8.0

docker ps --filter name=lab52-mysql
docker logs -f lab52-mysql
```

看到`ready for connections`后按`Ctrl+C`退出日志，再验证：

```bash
docker exec lab52-mysql \
  mysql -ulabuser -pLabUser2026! -e 'SELECT VERSION(); SHOW DATABASES;'

docker exec lab52-mysql \
  mysql -ulabuser -pLabUser2026! lab52db -e '
    CREATE TABLE IF NOT EXISTS health(id INT PRIMARY KEY, message VARCHAR(50));
    INSERT INTO health VALUES(1,"mysql-ok") ON DUPLICATE KEY UPDATE message="mysql-ok";
    SELECT * FROM health;'
```

> **验收点**：MySQL未发布宿主端口，但在容器内部正常工作；删除容器后数据卷仍存在。

### 步骤3：部署带密码的Redis

```bash
docker volume create lab52-redis-data

docker run -d --name lab52-redis \
  --network lab52-net \
  -v lab52-redis-data:/data \
  redis:7-alpine \
  redis-server --appendonly yes --requirepass 'RedisLab2026!'

docker logs lab52-redis
docker exec lab52-redis redis-cli -a 'RedisLab2026!' PING
docker exec lab52-redis redis-cli -a 'RedisLab2026!' SET course docker
docker exec lab52-redis redis-cli -a 'RedisLab2026!' GET course
```

无密码测试应失败：

```bash
docker exec lab52-redis redis-cli PING
# 预期：NOAUTH Authentication required
```

> **验收点**：有密码返回PONG，无密码被拒绝；Redis未发布到宿主机端口。

### 步骤4：从同一网络使用服务名访问

Nginx、MySQL和Redis位于`lab52-net`，容器名可作为DNS名称。

```bash
docker run --rm --network lab52-net mysql:8.0 \
  mysql -h lab52-mysql -ulabuser -pLabUser2026! \
  -e 'SELECT message FROM lab52db.health;'

docker run --rm --network lab52-net redis:7-alpine \
  redis-cli -h lab52-redis -a 'RedisLab2026!' GET course

docker run --rm --network lab52-net curlimages/curl:8.5.0 \
  curl -fsS http://lab52-nginx
```

若`curlimages/curl`未预加载，可使用教师提供的测试镜像或在宿主机验证Nginx。

> **验收点**：三个服务都能通过容器名访问，说明自定义网络提供容器DNS。

### 步骤5：完成运行参数表

| 服务 | 镜像 | 容器端口 | 宿主端口 | 数据目录 | 认证方式 | 外部是否需要访问 |
|---|---|---:|---:|---|---|---|
| Nginx | | | | | | |
| MySQL | | | | | | |
| Redis | | | | | | |

讨论：为什么只发布Nginx端口，而MySQL和Redis保持在容器内部网络？

### 步骤6：故障挑战

教师选择一个故障：

- Nginx宿主端口8080被占用
- MySQL密码环境变量错误
- Redis客户端忘记认证
- 测试容器未加入`lab52-net`
- bind mount缺少`:Z`导致SELinux拒绝访问

排障顺序：

```bash
docker ps -a
docker logs 容器名
docker inspect 容器名
docker network inspect lab52-net
ss -lntp
```

## 五、验收标准

- [ ] Nginx通过宿主8080返回自定义页面
- [ ] MySQL完成初始化、建表和查询
- [ ] Redis密码认证与AOF参数生效
- [ ] 三个服务通过自定义网络和容器名互访
- [ ] MySQL/Redis未无条件发布宿主端口
- [ ] 完成运行参数表和一个故障报告

## 六、常见问题

**Q：MySQL容器Up但连接失败？**

A：首次初始化需要时间。查看`docker logs lab52-mysql`，等待`ready for connections`，不要用固定`sleep`判断服务一定就绪。

**Q：为什么实验密码直接写在命令中？**

A：这里只用于隔离实验。综合项目必须使用`.env`或其他配置方式，并提交`.env.example`而不是实际密码文件。

**Q：为什么不在本实验深入卷备份和Docker网络模式？**

A：本实验目标是服务部署与验证。Lab54专门处理卷、权限和恢复，Lab55专门处理网络和DNS，避免重复占用课堂时间。

## 七、清理环境

```bash
docker rm -f lab52-nginx lab52-mysql lab52-redis 2>/dev/null || true
docker network rm lab52-net 2>/dev/null || true
docker volume rm lab52-mysql-data lab52-redis-data 2>/dev/null || true
rm -rf ~/lab52
```

如后续课程继续使用数据，先完成Lab54备份后再删除数据卷。
