# Lab45：KVM 虚拟化网络

> 课时：2 | 类型：个人 | 前置：Lab44

## 一、你会学到什么
- 理解 libvirt 的三种网络类型（NAT/桥接/隔离）
- 能创建和管理虚拟网络
- 能配置多 VM 通过不同网络互通

## 二、实验步骤

### 步骤1：查看 libvirt 默认网络

```bash
# 列出所有虚拟网络
virsh net-list --all
# Name      State    Autostart   Persistent
# default   active   yes         yes

# 查看默认网络详情
virsh net-info default
# Name:           default
# UUID:           ...
# Active:         yes
# Persistent:     yes
# Autostart:      yes
# Bridge:         virbr0

# 查看默认网络的 XML 配置
virsh net-dumpxml default
```

关键配置解读：
```xml
<network>
  <name>default</name>
  <bridge name="virbr0"/>                  ← 虚拟网桥
  <forward mode="nat"/>                    ← NAT 模式
  <ip address="192.168.122.1" netmask="255.255.255.0">
    <dhcp>
      <range start="192.168.122.2" end="192.168.122.254"/>
    </dhcp>
  </ip>
</network>
```

### 步骤2：查看网桥

```bash
# 查看 virbr0 网桥
ip a show virbr0
# inet 192.168.122.1/24 ← 宿主机在 122.0 网段充当网关

# 查看网桥的端口
bridge link show
# 如果 VM 连接到 default 网络，会看到 vnet0 等接口挂载在 virbr0 下

# 查看 iptables NAT 规则（了解）
sudo iptables -t nat -L | grep 192.168.122
# KVM 通过 iptables 为 VM 做 SNAT 上网
```

### 步骤3：创建隔离网络

```bash
# 创建隔离网络 XML 定义
cat > /tmp/isolated-net.xml << 'EOF'
<network>
  <name>isolated</name>
  <bridge name="virbr1"/>
  <ip address="10.0.100.1" netmask="255.255.255.0">
    <dhcp>
      <range start="10.0.100.100" end="10.0.100.200"/>
    </dhcp>
  </ip>
</network>
EOF

# 定义网络
virsh net-define /tmp/isolated-net.xml

# 启动网络
virsh net-start isolated

# 设置开机自启
virsh net-autostart isolated

# 验证
virsh net-list --all
virsh net-info isolated

# 查看新网桥
ip a show virbr1
# inet 10.0.100.1/24
```

### 步骤4：三种网络类型对比

| 网络类型 | forward mode | VM 可出外网 | 外网可入 VM | 适用场景 |
|---------|-------------|-----------|-----------|---------|
| NAT | nat | ✓ | ✗ | VM 需上网下载软件 |
| 桥接 | bridge | ✓ | ✓ | VM 对外提供服务 |
| 隔离 | none（不写forward） | ✗ | ✗ | 安全隔离环境 |

```bash
# 查看网络类型
virsh net-dumpxml default | grep forward
# <forward mode='nat'/>

virsh net-dumpxml isolated | grep forward
# （无输出 = 隔离网络）
```

### 步骤5：VM 网络配置修改

```bash
# 查看 VM 当前网络配置
virsh domiflist VM名

# 编辑 VM 配置来修改网络
virsh edit VM名
# 修改 <interface> 段：
# <interface type='network'>
#   <source network='isolated'/>   ← 改为其他网络
#   <model type='virtio'/>
# </interface>

# 或通过 virsh 命令添加第二块网卡
# virsh attach-interface VM名 --type network --source default --model virtio --config
```

### 步骤6：多 VM 网络拓扑实验（概念）

```
VM-A（前端，双网卡）
  ├── 连接 default (NAT) → 可上网
  └── 连接 isolated (隔离) → 与 VM-B 通信

VM-B（后端，单网卡）
  └── 连接 isolated (隔离) → 只能与 VM-A 通信
```

这种架构模拟了企业 DMZ（隔离区）：
- 前端 VM 对外服务，同时与后端通信
- 后端 VM 完全隔离，外网无法直接访问

---

## 五、练习题

### 练习1：libvirt 网络命令（15分）

| 操作 | 命令 |
|------|------|
| 列出所有网络 | |
| 查看网络详情 | |
| 查看网络 XML | |
| 定义新网络 | |
| 启动网络 | |
| 设置自启 | |

### 练习2：创建自定义 NAT 网络（25分）

创建一个名为 `mynat` 的 NAT 网络：
- IP 范围：172.16.0.0/24
- 网关：172.16.0.1
- DHCP：172.16.0.100-172.16.0.200
- 写出 XML 定义和完整命令

### 练习3：网络模式选型（20分）

| 场景 | 网络模式 | 理由 |
|------|---------|------|
| Kali Linux 渗透测试 | | |
| Nginx 对外 Web 服务 | | |
| 内部数据库（MySQL） | | |
| 开发测试环境 | | |

### 练习4：网桥分析（20分）

1. `ip a show virbr0` 输出的各字段含义
2. 如果 VM 连到 default 网络，`bridge link show` 会显示什么？
3. virbr0 和 docker0 有什么相似之处？

### 练习5：多 VM 网络规划（20分）

设计一个包含 5 台 VM 的网络：
- 2 台 Web 前端（对外服务）
- 2 台应用后端（只与前端通信）
- 1 台数据库（只与后端通信）

画出网络拓扑，标注每台 VM 连接的网络和 IP 规划。

## 七、常见问题

**Q: VM 连到 default 网络后不能上网？**
A: 检查：① default 网络是否 active：`virsh net-info default`；② 宿主机 IP 转发是否开启：`sysctl net.ipv4.ip_forward`（应为 1）；③ 宿主机 NAT iptables 规则是否正确。

**Q: 桥接网络和 NAT 网络的核心区别？**
A: 桥接 = VM 和宿主机在同一个二层网络，VM 直接从物理路由器获取 IP，局域网可见。NAT = VM 在独立的虚拟网络，通过宿主机 SNAT 上网，外界看不到 VM。

**Q: 隔离网络中 VM 之间能通吗？**
A: 能。隔离网络只是不与外界通信（无 forward），同一隔离网络内的 VM 可以通过网桥互通。

## 八、课后思考

1. Docker 的自定义 bridge 网络也自带 DNS 功能，libvirt 的虚拟网络有吗？如果没有，KVM VM 之间怎么通过主机名互访？

2. 在云环境中（如阿里云 VPC），虚拟网络的管理从"手动创建 virbr"变成了"控制台配置 VPC 和交换机"。这两种方式在运维思维上有什么不同？
