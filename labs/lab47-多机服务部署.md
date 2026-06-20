# Lab47：跨主机服务部署与测试

> 课时：2 | 类型：双人 | 前置：Lab46

## 一、你会学到什么
- 能在三台 VM 上分别部署不同服务
- 能配置跨主机的服务互通
- 能测试远程数据库和缓存连接
- 能排查跨主机服务连通性问题

## 二、实验拓扑

```
web-server (192.168.200.10)  → Nginx
db-server  (192.168.200.20)  → MariaDB + Redis
client     (192.168.200.30)  → 测试客户端
```

## 三、实验步骤

### 步骤1：在 db-server 上部署 MariaDB + Redis

```bash
# 安装
sudo dnf install -y mariadb-server redis
sudo systemctl enable --now mariadb redis

# MariaDB：创建允许远程的测试用户
sudo mysql << 'SQL'
CREATE USER 'tester'@'192.168.200.%' IDENTIFIED BY 'TestPass123!';
GRANT SELECT ON *.* TO 'tester'@'192.168.200.%';
FLUSH PRIVILEGES;
SQL

# Redis：临时允许远程访问（仅测试！）
sudo sed -i 's/^bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf
sudo sed -i 's/^protected-mode yes/protected-mode no/' /etc/redis/redis.conf
sudo systemctl restart redis

# 防火墙放行 3306 和 6379
sudo firewall-cmd --add-port=3306/tcp --add-port=6379/tcp --permanent
sudo firewall-cmd --reload

# 确认端口监听
ss -tlnp | grep -E "3306|6379"
# 应该显示 0.0.0.0:3306 和 0.0.0.0:6379
```

### 步骤2：在 web-server 上部署 Nginx

```bash
sudo dnf install -y nginx
sudo systemctl enable --now nginx

# 创建测试页面
sudo tee /usr/share/nginx/html/index.html << 'HTML'
<h1>Web Server</h1>
<p>Host: web-server</p>
<p>Backend: db-server (MariaDB + Redis)</p>
HTML

sudo firewall-cmd --add-service=http --permanent
sudo firewall-cmd --reload
```

### 步骤3：在 client 上远程测试

```bash
# 1. 测试 HTTP
curl http://web-server
curl -I http://web-server

# 2. 测试 MariaDB 远程连接
mysql -u tester -h db-server -p -e "SELECT VERSION();"
# 输入密码 TestPass123!
# 应该看到 MariaDB 版本号

# 3. 测试 Redis 远程连接
redis-cli -h db-server PING
# PONG

redis-cli -h db-server SET remote-test "from client"
redis-cli -h db-server GET remote-test
# "from client"

# 4. 测试端口连通性
nc -zv -w 3 web-server 80
nc -zv -w 3 db-server 3306
nc -zv -w 3 db-server 6379
```

### 步骤4：验证跨主机服务架构

```
client ──curl──→ web-server:80 ──→ Nginx (响应)
client ──mysql──→ db-server:3306 ──→ MariaDB (响应)
client ──redis──→ db-server:6379 ──→ Redis (响应)
```

```bash
# 在 client 上写一个测试脚本
cat > ~/test-services.sh << 'SCRIPT'
#!/bin/bash
echo "=== 跨主机服务测试 ==="
echo "[1/3] Web Server..."
curl -s -o /dev/null -w "%{http_code}" http://web-server && echo " ✓" || echo " ✗"

echo "[2/3] MariaDB..."
mysql -u tester -h db-server -pTestPass123! -e "SELECT 1" &>/dev/null && echo " ✓" || echo " ✗"

echo "[3/3] Redis..."
redis-cli -h db-server PING &>/dev/null && echo " ✓" || echo " ✗"
SCRIPT

chmod +x ~/test-services.sh
./test-services.sh
```

### 步骤5：排障练习

```bash
# 场景1：防火墙忘记放行 3306
sudo firewall-cmd --remove-port=3306/tcp --permanent
sudo firewall-cmd --reload
# 在 client 测试 mysql 连接 → 失败
# 修复
sudo firewall-cmd --add-port=3306/tcp --permanent
sudo firewall-cmd --reload

# 场景2：Redis bind 没有改成 0.0.0.0
sudo sed -i 's/^bind 0.0.0.0/bind 127.0.0.1/' /etc/redis/redis.conf
sudo systemctl restart redis
# 在 client 测试 redis → 连接失败
# 修复
sudo sed -i 's/^bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf
sudo systemctl restart redis
```

---

## 五、练习题

### 练习1：跨主机服务依赖关系（15分）

画出 web-server 和 db-server 之间的服务依赖关系图，标注端口和数据流向。

### 练习2：安全评估（25分）

评估当前跨主机部署的安全性：
1. MariaDB 端口 3306 对外暴露有什么风险？
2. Redis 无密码对外暴露有什么风险？
3. 如何加固？写出每项的加固命令

### 练习3：性能测试（20分）

在 client 上用工具测试远程服务的响应时间：
1. `time curl http://web-server` → 记录总时间
2. `time mysql -u tester -h db-server -pTestPass123! -e "SELECT 1"` → 记录总时间
3. `redis-cli -h db-server --latency` → 记录延迟

### 练习4：故障注入与恢复（25分）

教师随机注入以下 1-2 个故障，学生排查并记录：
- 停止 db-server 上的 MariaDB
- 修改 web-server 的 /etc/hosts 错误指向
- 在 db-server 上添加防火墙规则拦截 6379

### 练习5：扩容方案（15分）

如果访问量增大，需要扩容：
1. 加第二台 web-server 怎么做？
2. 数据库读写分离怎么做？
3. Redis 做主从复制怎么做？
（只需要方案，不需要实际配置）

## 七、常见问题

**Q: 远程 MySQL 连接报 "Host is not allowed"？**
A: MySQL 用户由"用户名+来源主机"共同标识。检查 `SELECT User, Host FROM mysql.user;`，确认用户允许从 client 的 IP 连接。

**Q: Redis 远程连接被拒绝？**
A: 三步排查：① bind 是否为 0.0.0.0（不是 127.0.0.1）；② protected-mode 是否关闭（仅测试环境）；③ 防火墙是否放行 6379。

**Q: 跨主机服务架构中，怎么保证服务发现（web 怎么知道 db 的 IP 变了）？**
A: 小规模：/etc/hosts 手动维护。中规模：内部 DNS。大规模：Consul/etcd + 配置中心。云环境：云厂商的 DNS 服务。

## 八、课后思考

1. 本次实验的 db-server 同时开放了 3306 和 6379，这在生产环境是不可接受的。如果应用和数据库必须分离部署，如何保证通信安全？（提示：内网隔离、VPN、TLS 加密）

2. 这种"三台 VM 分别部署不同服务"的架构，和"一台 VM 上 Docker Compose 全部部署"相比，各有什么优缺点？
