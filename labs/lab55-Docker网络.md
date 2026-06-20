# Lab55：Docker 网络深入实践

> 课时：2 | 类型：个人 | 前置：Lab54

## 一、你会学到什么
- 深入理解 Docker 四种网络模式
- 能创建和管理自定义网络
- 能实现跨网络容器通信
- 能排查容器网络不通的问题

## 二、实验步骤

### 步骤1：查看 Docker 网络

```bash
# 列出所有网络
docker network ls
# NETWORK ID   NAME      DRIVER    SCOPE
# abc123def    bridge    bridge    local
# def456ghi    host      host      local
# ghi789jkl    none      null      local

# 查看 bridge 网络详情
docker network inspect bridge | head -30
# "Subnet": "172.17.0.0/16",
# "Gateway": "172.17.0.1"
```

### 步骤2：默认 bridge vs 自定义 bridge

```bash
# 默认 bridge：只有 IP 互通，没有 DNS
docker run -d --name d1 nginx:alpine
docker run -d --name d2 nginx:alpine

docker exec d2 ping -c 2 172.17.0.2    # ✓ IP 能通
docker exec d2 ping -c 2 d1            # ✗ ping: bad address
# 默认 bridge 没有内置 DNS！

docker rm -f d1 d2

# 自定义 bridge：自带 DNS
docker network create my-bridge
docker run -d --name c1 --network my-bridge nginx:alpine
docker run -d --name c2 --network my-bridge nginx:alpine

docker exec c2 ping -c 2 c1            # ✓ 容器名能通！
# 自定义 bridge 内置 DNS 服务器（127.0.0.11）
```

### 步骤3：host 网络模式

```bash
# host 模式：容器直接使用宿主机网络栈
docker run -d --name host-nginx --network host nginx:alpine

# 不需要 -p！容器直接占用宿主机 80 端口
curl http://localhost              # ✓
ss -tlnp | grep :80
# 看不到 docker-proxy，因为是直接监听

# 性能：host > bridge（少一层 NAT 转发）
# 隔离性：bridge > host（端口可能冲突）
# 端口冲突演示：
docker run -d --name host-nginx2 --network host nginx:alpine
# nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)

docker rm -f host-nginx host-nginx2
```

### 步骤4：none 网络模式

```bash
# none 模式：容器没有网络接口
docker run --rm --network none alpine ip a
# 只有 lo 回环接口，没有 eth0

# 适用场景：
# 1. 不需要网络的批处理任务
# 2. 手动配置网络的特殊场景
# 3. 安全隔离（完全切断网络）
```

### 步骤5：容器连接多个网络

```bash
# 创建两个网络
docker network create front-net
docker network create back-net

# 创建容器连接到 front-net
docker run -d --name frontend --network front-net nginx:alpine

# 创建容器连接到 back-net
docker run -d --name backend --network back-net alpine sleep 3600

# 验证：不同网络之间不互通
docker exec frontend ping -c 1 backend
# ping: bad address 'backend' ← 不在同一网络

# 把 backend 也连接到 front-net
docker network connect front-net backend

# 现在能通了！
docker exec frontend ping -c 2 backend   # ✓

# 查看 backend 的网络
docker inspect backend | grep -A20 '"Networks"'
# 能看到两个网络：front-net 和 back-net

docker network disconnect front-net backend
docker rm -f frontend backend
docker network rm front-net back-net
```

### 步骤6：网络排障工具

```bash
# 1. 查看容器 IP 和网络
docker inspect c1 | grep IPAddress

# 2. 查看网络配置
docker network inspect my-bridge

# 3. 进入容器测试网络
docker exec c1 ip a
docker exec c1 ip route
docker exec c1 ping -c 2 c2

# 4. 查看 iptables 规则（Docker 网络依赖 iptables）
sudo iptables -t nat -L DOCKER | head -10

# 5. 查看 docker-proxy 进程
ps aux | grep docker-proxy

docker rm -f c1 c2
docker network rm my-bridge
```

---

## 五、练习题

### 练习1：网络模式选型（15分）

| 场景 | 推荐模式 | 理由 |
|------|---------|------|
| 高性能反向代理 | | |
| 多容器微服务 | | |
| 安全沙箱（无需网络） | | |
| 简单单机测试 | | |

### 练习2：多网络架构设计（25分）

设计一个三层网络架构：
- Web 层（3 个 Nginx）→ front-net
- App 层（2 个 Python）→ front-net + back-net
- DB 层（1 个 MySQL + 1 个 Redis）→ back-net

画出网络拓扑，标注每层的网络连接。

### 练习3：网络排障（25分）

以下场景排查并修复：

| 现象 | 排查步骤 |
|------|---------|
| 容器 A 能 ping 通容器 B 的 IP，但 ping 不通容器名 | |
| 容器 A 完全 ping 不通容器 B | |
| 容器内能 ping 通外网 IP，但 ping 不通域名 | |

### 练习4：--link vs 自定义网络（20分）

1. `--link`（旧方式）和自定义网络的 DNS 有什么区别？
2. 为什么现在不推荐 `--link`？
3. 自定义网络比 `--link` 好在哪？

### 练习5：Docker 网络底层（15分）

1. docker0 网桥和 virbr0（KVM）有什么相似之处？
2. `docker-proxy` 进程的作用是什么？
3. Docker 网络和 iptables 有什么关系？

## 七、常见问题

**Q: 自定义 bridge 的 DNS 是怎么实现的？**
A: Docker 内嵌 DNS 服务器（监听 127.0.0.11），容器内的 /etc/resolv.conf 指向它。当容器查询另一个容器名时，DNS 服务器返回对应容器的 IP。

**Q: 一个容器能同时连接多个网络吗？**
A: 能。`docker network connect 网络名 容器名`。这对"前端容器连 front-net，后端容器同时连 front-net 和 back-net"的架构很有用。

**Q: host 网络和 bridge 网络性能差多少？**
A: bridge 模式多了一层 NAT 转发（docker-proxy + iptables），高吞吐场景下可能有 5-10% 性能损耗。大多数场景可以忽略，追求极致性能用 host 模式。

## 八、课后思考

1. Docker 的网络隔离通过 Linux network namespace 实现。同一个容器内的进程看到的是独立的网络栈（独立 IP、路由表、iptables）。这种隔离和虚拟机网络隔离有什么本质区别？

2. Kubernetes 的网络模型和 Docker Compose 有什么不同？K8s 中 Pod 内容器共享网络命名空间，这种设计有什么好处？
