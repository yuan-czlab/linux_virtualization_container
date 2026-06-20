# Lab42：VMware 虚拟网络模式对比实验

> 课时：2 | 类型：个人 | 前置：Lab41

## 一、你会学到什么
- 能通过实际操作对比 NAT、桥接、仅主机三种模式的行为差异
- 能根据需求选择正确的网络模式
- 能排查虚拟网络不通的常见问题

## 二、实验步骤

### 步骤1：确认当前网络模式

```bash
# 查看当前 IP 和网关
ip a show ens33 | grep inet
ip route show default

# 在 VMware 中查看当前网络模式
# 编辑虚拟机设置 → 网络适配器 → 当前模式
```

### 步骤2：三种模式逐个测试

用同一台 VM，依次切换到三种模式，记录以下测试结果。

**切换方法**：VM 关机 → 编辑虚拟机设置 → 网络适配器 → 选择模式 → 启动 VM

#### NAT 模式测试

```bash
ip a show ens33 | grep inet    # 记录 IP
ip route show default           # 记录网关
ping -c 2 8.8.8.8              # 能否上网？
ping -c 2 192.168.200.1         # 能否 ping 通宿主机？（VMware NAT 网关 IP）
# 从宿主机 ping VM 的 IP → ？
```

#### 桥接模式测试

```bash
# 先确认宿主机 IP 和网段（Windows: ipconfig）
ip a show ens33 | grep inet    # 应与宿主机同网段
ping -c 2 8.8.8.8              # 能否上网？
ping -c 2 宿主机IP              # 能否 ping 通宿主机？
# 从宿主机 ping VM 的 IP → ？
# 从同一局域网其他设备 ping VM → ？
```

#### 仅主机模式测试

```bash
ip a show ens33 | grep inet    # 应与 VMnet1 同网段
ping -c 2 8.8.8.8              # 能否上网？
ping -c 2 宿主机 VMnet1 IP      # 能否 ping 通宿主机？
# 从宿主机 ping VM 的 IP → ？
```

### 步骤3：填写对比表

| 测试项 | NAT | 桥接 | 仅主机 |
|--------|-----|------|--------|
| VM 获取的 IP 网段 | | | |
| VM → 外网 (8.8.8.8) | | | |
| VM → 宿主机 | | | |
| 宿主机 → VM | | | |
| 局域网其他设备 → VM | | | |
| 同模式其他 VM → 本 VM | | | |
| 适用场景 | | | |

### 步骤4：VMware 虚拟网络编辑器

```text
VMware → 编辑 → 虚拟网络编辑器

VMnet0 → 桥接模式（自动桥接到物理网卡）
VMnet1 → 仅主机模式（默认 192.168.137.0/24）
VMnet8 → NAT 模式（默认 192.168.200.0/24）

可修改：子网 IP、DHCP 范围、NAT 设置
```

```bash
# 查看宿主机侧的虚拟网卡（Windows 命令行）
# ipconfig
# VMware Network Adapter VMnet1 → 仅主机
# VMware Network Adapter VMnet8 → NAT
```

### 步骤5：常见问题排查

```bash
# 问题1：NAT 模式下 VM 不能上网
# 排查：
ip route show default           # 检查网关
ping 网关IP                     # 网关可达？
cat /etc/resolv.conf            # DNS 配置？
# 宿主机 VMware NAT Service 是否启动？（Windows: services.msc）

# 问题2：桥接模式拿不到 IP
# 排查：
sudo nmcli con up ens33         # 手动激活连接
# 检查是否选对了桥接的物理网卡（WiFi vs 有线）

# 问题3：仅主机模式 VM 和宿主机不通
# 排查：
ip a                           # VM IP 是否在 VMnet1 网段？
# Windows: ipconfig → VMnet1 IP
# 防火墙是否拦截了 ping？
```

---

## 五、练习题

### 练习1：场景选型（20分）

| 场景 | 推荐模式 | 理由 |
|------|---------|------|
| VM 需要安装软件包（yum update） | | |
| VM 作为 Web 服务器对外提供服务 | | |
| 搭建隔离的渗透测试靶场 | | |
| 多台 VM 组成集群，需要固定 IP | | |
| 笔记本带到不同网络环境，VM 不需要改 IP | | |

### 练习2：NAT 深入理解（20分）

1. NAT 模式下，VM 怎么上网的？（画出数据流）
2. 为什么宿主机不能主动连接 NAT 模式的 VM？
3. 如果想让宿主机访问 NAT 模式的 VM，怎么做？（端口转发）

### 练习3：桥接模式排障（25分）

桥接模式下 VM 不能上网，写出你的排查步骤（至少 5 步）。

### 练习4：仅主机模式应用（15分）

1. 仅主机模式下，VM 不能上网怎么安装软件？
2. 有什么方法让仅主机模式的 VM 也能上网？（宿主机做 NAT/共享网络）
3. 仅主机模式适合什么场景？

### 练习5：虚拟网络规划（20分）

设计一个实验环境：3 台 VM（Web/DB/Client），要求：
- Web 和 DB 之间通过隔离网络通信（不能让外界访问）
- Web 还需要对外提供 HTTP 服务
- Client 用于测试，不需要固定 IP

画出网络拓扑并标注每台 VM 的网卡数量和网络模式。

## 七、常见问题

**Q: 三种网络模式怎么选？**
A: VM 只需上网 → NAT；VM 需要对外提供服务 → 桥接；隔离测试环境 → 仅主机。

**Q: NAT 模式下宿主机怎么访问 VM？**
A: 配置端口转发。VMware 虚拟网络编辑器 → NAT 设置 → 添加端口转发规则。或给 VM 加第二块网卡配置仅主机模式。

**Q: 桥接模式选 WiFi 还是有线网卡？**
A: 优先选有线网卡（更稳定）。如果只有 WiFi，某些场景下桥接可能不兼容（取决于 WiFi 驱动），此时建议用 NAT + 端口转发。

## 八、课后思考

1. Docker 的网络模式（bridge/host/none）和 VMware 的网络模式（NAT/桥接/仅主机）有什么对应关系？它们在原理上有哪些相似之处？

2. 在云服务器（如阿里云 ECS）上，你不需要关心 NAT 还是桥接，而是配置"安全组"和"弹性公网 IP"。这和 VMware 网络配置有什么本质区别？
