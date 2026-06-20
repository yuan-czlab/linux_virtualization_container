# Lab39：VMware 多机环境搭建

> 课时：2 | 类型：双人 | 前置：Lab02

## 一、你会学到什么
- 能从现有 VM 克隆出多台独立虚拟机
- 能规划多台 VM 的 IP 地址和主机名
- 能配置 /etc/hosts 使多台 VM 通过主机名互通
- 能编写 IP 地址规划表

## 二、实验拓扑

```
宿主机 (Windows 10) - 192.168.200.1
  └── VMware NAT 网络 192.168.200.0/24
        ├── web-server  192.168.200.10
        ├── db-server   192.168.200.20
        └── client      192.168.200.30
```

## 三、实验步骤

### 步骤1：克隆虚拟机

在 VMware 中操作（非命令行）：
```text
1. 关闭 Rocky-9 VM
2. 右键 → 管理 → 克隆 → 下一步
3. 克隆来源：虚拟机中的当前状态 → 下一步
4. 克隆类型：创建完整克隆 → 下一步
5. 虚拟机名称：db-server → 完成
6. 重复步骤 2-5，创建 client
```

**为什么选完整克隆**：完整克隆是完全独立的副本，不依赖原始 VM。链接克隆更省空间但依赖父盘存在。

### 步骤2：配置主机名

分别在 db-server 和 client 上操作：

```bash
# 在 db-server 上
sudo hostnamectl set-hostname db-server
hostname                           # 验证
cat /etc/hostname                  # 确认永久生效

# 在 client 上
sudo hostnamectl set-hostname client
hostname
```

### 步骤3：配置静态 IP

克隆出来的 VM 和原始 VM 有相同的 IP。需要修改：

```bash
# 在 db-server 上
sudo nmcli con mod static-net ipv4.addresses 192.168.200.20/24
sudo nmcli con up static-net
ip a show ens33 | grep inet       # 确认 192.168.200.20

# 在 client 上
sudo nmcli con mod static-net ipv4.addresses 192.168.200.30/24
sudo nmcli con up static-net
ip a show ens33 | grep inet       # 确认 192.168.200.30

# 在 web-server（原 VM）上确认 IP 还是 192.168.200.10
```

### 步骤4：配置 /etc/hosts

**在三台 VM 上都执行相同的 hosts 配置**：

```bash
sudo tee -a /etc/hosts << 'EOF'
192.168.200.10  web-server
192.168.200.20  db-server
192.168.200.30  client
EOF
```

### 步骤5：验证互通

```bash
# 在每台 VM 上分别执行
ping -c 2 web-server
ping -c 2 db-server
ping -c 2 client

# 用主机名 ping → 必须能通
```

### 步骤6：宿主机 SSH 连接

在 Windows 宿主机 PowerShell 或 CMD：
```powershell
ssh student@192.168.200.10    # web-server
ssh student@192.168.200.20    # db-server
ssh student@192.168.200.30    # client
```

### 步骤7：编写 IP 地址规划表

创建文档 `/tmp/ip-plan.md`：

```markdown
# IP 地址规划表

| 主机名 | IP 地址 | 角色 | 开放端口 |
|--------|---------|------|---------|
| web-server | 192.168.200.10 | Web 服务器 | 22, 80, 443 |
| db-server | 192.168.200.20 | 数据库+缓存 | 22, 3306, 6379 |
| client | 192.168.200.30 | 测试客户端 | 22 |

## 网络信息
- 网络模式：VMware NAT
- 网段：192.168.200.0/24
- 网关：192.168.200.2
- DNS：223.5.5.5
```

---

## 五、练习题

### 练习1：虚拟机资源规划（15分）

如果要创建以下服务器，各需要分配多少资源（CPU/内存/磁盘）？

| 服务器 | 建议 CPU | 建议内存 | 建议磁盘 | 理由 |
|--------|---------|---------|---------|------|
| Web 服务器（Nginx） | | | | |
| 数据库服务器（MySQL） | | | | |
| 测试客户端 | | | | |

### 练习2：排障（25分）

三台 VM 配好后，发现 web-server 能 ping 通 client 但 ping 不通 db-server。写出排查步骤和可能原因（至少 3 种）。

### 练习3：/etc/hosts vs DNS（20分）

1. 三台 VM 通过 /etc/hosts 互通有什么缺点？（提示：如果有 100 台服务器呢？）
2. 企业内部一般用什么方案替代 /etc/hosts？（DNS 服务器 / Ansible hosts）
3. 如果 /etc/hosts 中 db-server 的 IP 写错了，会发生什么？

### 练习4：克隆后的清理（20分）

克隆出来的 VM 有哪些配置需要修改？（至少列出 5 项）
1. 主机名
2. IP 地址
3. SSH host key
4. machine-id
5. ?

### 练习5：绘制拓扑图（20分）

用 draw.io 或手绘，画出三台 VM + 宿主机 + 外网的完整拓扑图，标注 IP、网段、网关。

## 七、常见问题

**Q: 克隆出来的 VM 和原 VM IP 冲突怎么办？**
A: 克隆后立即修改：①主机名 `hostnamectl`；②IP 地址 `nmcli con mod`；③重启网络生效。如果不改 IP，两台 VM 用同一个 IP 会导致网络异常。

**Q: 为什么 /etc/hosts 比 DNS 优先？**
A: Linux 的 `/etc/nsswitch.conf` 中 hosts 配置为 `files dns`，表示先查 files(/etc/hosts)，再查 dns。这是历史设计，也方便本地覆盖 DNS。

**Q: 三台 VM 之间 ping 不通？**
A: 检查：①VMware 网络模式是否一致（都应该是 NAT）；②IP 是否在同一网段；③防火墙是否拦截 ICMP：`sudo firewall-cmd --add-protocol=icmp --permanent`。

## 八、课后思考

1. 如果公司有 50 台服务器，手动维护每台的 /etc/hosts 显然不现实。企业内网一般用什么方案实现主机名互访？（提示：内部 DNS、Consul、Ansible hosts 管理）

2. 为什么生产环境建议使用静态 IP 而不是 DHCP？云服务器（如阿里云 ECS）的 IP 是怎么管理的？
