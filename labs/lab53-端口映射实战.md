# Lab53：Docker 端口映射实战

> 课时：2 | 类型：个人 | 前置：Lab51

## 一、你会学到什么
- 能正确使用 -p 进行端口映射
- 能理解宿主机端口和容器端口的区别
- 能排查端口冲突
- 能用 docker port 查看映射关系

## 二、实验步骤

### 步骤1：端口映射基础

```bash
# -p 宿主机端口:容器端口
docker run -d --name web-a -p 8081:80 nginx:alpine
docker run -d --name web-b -p 8082:80 nginx:alpine

# 查看映射
docker ps --format "table {{.Names}}\t{{.Ports}}"
# web-a   0.0.0.0:8081->80/tcp
# web-b   0.0.0.0:8082->80/tcp

# 验证
curl http://localhost:8081        # → web-a
curl http://localhost:8082        # → web-b
```

**关键理解**：
- 宿主机 8081 → 容器 web-a 的 80
- 宿主机 8082 → 容器 web-b 的 80
- 两个容器内部都用 80 端口，不冲突（网络命名空间隔离）
- 但宿主机端口不能重复

### 步骤2：多端口映射

```bash
# 一个容器映射多个端口
docker run -d --name multi-port \
  -p 8083:80 \
  -p 8443:443 \
  nginx:alpine

docker ps --format "table {{.Names}}\t{{.Ports}}" | grep multi-port
# multi-port   0.0.0.0:8083->80/tcp, 0.0.0.0:8443->443/tcp
```

### 步骤3：指定监听地址

```bash
# 默认 0.0.0.0:宿主机端口 → 所有网卡都可访问
# 限制只监听特定 IP
docker run -d --name restricted-web \
  -p 127.0.0.1:8084:80 \
  nginx:alpine

# 127.0.0.1:8084 → 只有本机能访问
curl http://localhost:8084         # ✓
# 从其他机器访问 VM_IP:8084 → ✗（127.0.0.1 限制）
```

### 步骤4：随机端口

```bash
# -P：自动映射 EXPOSE 声明的端口到宿主机随机端口
docker run -d -P --name random-port nginx:alpine

# 查看随机分配的端口
docker port random-port
# 80/tcp -> 0.0.0.0:32768

# 用随机端口访问
curl http://localhost:32768
```

### 步骤5：端口冲突排查

```bash
# 模拟端口冲突
docker run -d --name conflict-test -p 8081:80 nginx:alpine
# Error: driver failed programming... Bind for 0.0.0.0:8081 failed: port is already allocated

# 查看谁占了 8081
ss -tlnp | grep :8081
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep 8081

# 解决方法1：停掉冲突容器
docker rm -f web-a

# 解决方法2：换端口
docker run -d --name conflict-test -p 8085:80 nginx:alpine

docker rm -f conflict-test
```

### 步骤6：docker port 命令

```bash
# 查看容器的所有端口映射
docker port web-b
# 80/tcp -> 0.0.0.0:8082

# 查看特定端口
docker port web-b 80
# 0.0.0.0:8082

# 用 inspect 获取更详细的信息
docker inspect web-b | grep -A5 "Ports"
```

### 步骤7：实际部署场景

```bash
# 部署一个开发环境：MySQL + Redis + Nginx
# 设计端口规划：

# MySQL: 宿主机 3307 → 容器 3306（避免和宿主机 MySQL 冲突）
docker run -d --name dev-mysql \
  -p 3307:3306 \
  -e MYSQL_ROOT_PASSWORD=DevPass123! \
  mysql:8.0

# Redis: 宿主机 6380 → 容器 6379
docker run -d --name dev-redis \
  -p 6380:6379 \
  redis:7-alpine

# Nginx: 宿主机 80 → 容器 80
docker run -d --name dev-nginx \
  -p 80:80 \
  nginx:alpine

# 所有端口互不冲突
ss -tlnp | grep -E "3307|6380|:80 "
```

---

## 五、练习题

### 练习1：端口映射方案设计（20分）

你需要在同一台服务器上运行 3 个 MySQL 实例（分别给 dev/staging/prod 环境），设计端口映射方案。

| 环境 | 宿主机端口 | 容器端口 | 用途 |
|------|-----------|---------|------|
| dev | | 3306 | |
| staging | | 3306 | |
| prod | | 3306 | |

### 练习2：端口冲突排查流程（20分）

写出端口冲突的完整排查流程：发现问题 → 定位占用 → 解决方案。

### 练习3：docker port 使用（15分）

1. 运行一个多端口容器（-p 8080:80 -p 8443:443）
2. 用 `docker port` 查看所有映射
3. 用 `docker inspect` 查看 Ports 字段的 JSON 结构

### 练习4：安全性分析（25分）

以下端口映射方案有什么安全问题？如何改进？

```bash
docker run -d --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root mysql:8.0
docker run -d --name redis -p 6379:6379 redis:7-alpine
docker run -d --name api -p 5000:5000 my-api:v1
```

### 练习5：端口规划文档（20分）

为一套微服务应用（8 个容器）设计端口映射规划表，确保无冲突且安全。

## 七、常见问题

**Q: 为什么同一个宿主机端口只能映射给一个容器？**
A: 宿主机端口是全局共享资源。就像一台机器只能有一个进程监听 80 端口一样。如果需要多个容器共享，用反向代理（Nginx）根据域名/路径转发。

**Q: -p 和 -P 有什么区别？**
A: -p 手动指定端口映射（-p 8080:80）。-P 自动将 Dockerfile 中 EXPOSE 声明的端口映射到宿主机随机端口。生产环境推荐手动 -p，端口规划更可控。

**Q: 容器内部端口和宿主机端口可以相同吗？**
A: 可以。`-p 80:80` 是把宿主机 80 映射到容器 80。如果宿主机 80 没被占就可以。容器内部 80 端口只在容器的网络命名空间里，和宿主机隔离。

## 八、课后思考

1. Docker Compose 中多个服务之间通过容器名通信，不需要端口映射。那端口映射（-p）在微服务架构中主要是给谁用的？

2. 如果一台服务器上跑了 50 个容器，每个都需要对外暴露端口，手动管理端口规划显然不现实。有什么自动化的服务发现和端口管理方案？
