# Lab15：TCP/UDP 端口与服务

> 课时：2 | 类型：个人 | 前置：Lab14

## 一、你会学到什么
- 理解 TCP 和 UDP 的区别
- 能说出常见服务默认端口
- 能用 ss -tunlp 查看端口监听
- 能用 nc/telnet 测试端口可达性

## 二、实验步骤

### 步骤1：查看端口监听

```bash
ss -tunlp
# -t TCP  -u UDP  -n 数字端口  -l 监听中  -p 显示进程

# 关注 Local Address:Port 列：
# 0.0.0.0:22    → 所有网卡监听，外网可访问
# 127.0.0.1:3306 → 仅本机可访问
# :::80         → IPv6 所有地址监听
```

### 步骤2：常见端口速查

| 端口 | 协议 | 服务 |
|------|------|------|
| 22 | TCP | SSH |
| 80 | TCP | HTTP |
| 443 | TCP | HTTPS |
| 3306 | TCP | MySQL/MariaDB |
| 6379 | TCP | Redis |
| 53 | TCP+UDP | DNS |

### 步骤3：服务启动 ≠ 端口可访问

```bash
# 演示：服务启动 + 端口监听 + 防火墙拦截 = 外网访问不了
sudo systemctl start nginx 2>/dev/null
ss -tlnp | grep :80                # ✓ 端口监听
curl localhost                      # ✓ 本机能访问
# 从外部访问 → ✗ 如果防火墙没放行
```

### 步骤4：nc 测试端口

```bash
sudo dnf install -y nc

nc -zv -w 3 localhost 22          # 测试 SSH 端口
# Connection to localhost 22 port [tcp/ssh] succeeded!

nc -zv -w 3 localhost 9999        # 测试不存在的端口
# nc: connect to localhost port 9999 (tcp) failed: Connection refused

nc -zv -w 3 8.8.8.8 53            # 测试外网 DNS 端口
```

### 步骤5：端口冲突排查

```bash
# 模拟端口冲突
sudo python3 -m http.server 8888 &
sleep 1
ss -tlnp | grep :8888             # 查看谁占了端口
sudo lsof -i :8888                # 更详细的信息
sudo kill $(lsof -t -i :8888)     # 杀掉占用进程
```

---

## 五、练习题

### 练习1：TCP vs UDP（15分）

| 特性 | TCP | UDP |
|------|-----|-----|
| 是否面向连接 | | |
| 可靠性 | | |
| 速度 | | |
| 典型应用 | | |
| 三次握手 | | |

### 练习2：端口安全审计（25分）

```
在你的 VM 上执行 ss -tunlp，整理出完整的端口清单：

| 端口 | 协议 | 进程 | 监听地址 | 对外暴露？ | 安全评估 |
|------|------|------|---------|----------|---------|
| | | | | | |
```

判断：哪些端口对外暴露是不安全的？哪个应该改监听地址？

### 练习3：端口连通性测试（20分）

用 nc 测试以下目标的端口可达性：

| 目标 | 端口 | 预期 | 实际结果 |
|------|------|------|---------|
| localhost | 22 | 通 | |
| localhost | 80 | 取决于 nginx | |
| localhost | 9999 | 不通 | |
| 8.8.8.8 | 53 | 通 | |
| www.baidu.com | 80 | 通 | |

### 练习4：Connection refused vs timeout（20分）

1. `Connection refused` 说明什么？服务端收到了请求但端口没人监听
2. `Connection timed out` 说明什么？请求根本没到达（防火墙 DROP 或网络不通）
3. 设计实验验证这两种报错的差异

### 练习5：端口安全规范（20分）

写出生产环境的端口安全规范：
1. SSH 端口建议怎么做？
2. 数据库端口应该监听在哪里？
3. 哪些端口绝对不能对外开放？

---

## 六、验收标准
- [ ] 能用 ss -tunlp 查看所有监听端口及进程
- [ ] 能说出 SSH/HTTP/HTTPS/MySQL/Redis/DNS 的默认端口
- [ ] 能区分 0.0.0.0:端口 和 127.0.0.1:端口 的安全含义
- [ ] 能用 nc -zv 测试端口可达性
- [ ] 理解 Connection refused 和 Connection timed out 的根本区别
- [ ] 练习 1-5 全部完成

## 七、常见问题

**Q: `ss` 和 `netstat` 有什么区别？**
A: netstat 是老旧工具（net-tools 包），ss 是新一代替代品（iproute2 包），更快更强大。面试时先说 ss 再说 netstat 会加分。新版 Linux 默认没有安装 netstat。

**Q: 为什么 0-1023 端口需要 root 权限才能监听？**
A: 这是 Linux 的安全机制，1024 以下的知名端口（well-known ports）只有 root 才能绑定。Nginx 以 root 启动监听 80 端口，然后 worker 进程降权为 nginx 用户处理请求。

**Q: 一个端口可以被多个进程同时监听吗？**
A: 正常情况下不能，同一时刻一个端口只能被一个进程监听。但可以通过 SO_REUSEPORT 选项让多个进程监听同一端口（用于负载均衡）。

**Q: 如何区分"防火墙拦截"和"服务没启动"？**
A: 本机 `curl localhost:端口` 能通 → 服务正常，是防火墙问题。本机也通不了 → 先查 `ss -tlnp` 确认端口是否在监听，再查 `systemctl status 服务名`。

## 八、课后思考

1. 为什么生产环境中数据库端口（3306/6379）不应该对公网开放？如果应用和数据库不在同一台服务器上，怎么安全地连接？（提示：内网、VPN、SSH 隧道）

2. 查资料：什么是 DDoS 攻击？它利用的是 TCP 还是 UDP？为什么 UDP 更容易被用于 DDoS 放大攻击？
