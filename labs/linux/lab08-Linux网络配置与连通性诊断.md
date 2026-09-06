# 实验8：Linux网络配置与连通性诊断

> 所属模块：模块二 网络、远程管理与基础防护  
> 建议学时：4学时  
> 实验方式：个人  
> 对应教材：《模块二 网络、远程管理与基础防护》第13章  
> 前置实验：实验7  
> 项目成果：Rocky服务器与Ubuntu客户端地址规划、静态网络配置、双机连通性验证和一次网络故障恢复记录

## 一、项目情境

通过DHCP获得的地址可能发生变化，不利于SSH和服务访问。你需要先调查VMware NAT网络，再为Rocky服务器和Ubuntu客户端建立不冲突的持久静态地址，并能够按照“网卡—地址—路由—DNS—目标服务”的顺序判断网络问题。

## 二、实验目标

### 1. 知识目标

1. 说明网卡、连接配置、IP地址、前缀、默认网关和DNS各自解决的问题。
2. 区分`ip`显示的运行状态、Rocky的NetworkManager配置和Ubuntu Server的Netplan配置。
3. 说明本机、同网段、网关、外部IP和域名测试的不同意义。

### 2. 能力目标

1. 使用`ip`、`nmcli`、`hostnamectl`和`resolvectl`或配置文件检查网络。
2. 根据实际VMnet8网段制定不冲突的地址计划。
3. 创建、验证和回退Rocky NetworkManager与Ubuntu Netplan静态配置。
4. 完成Rocky服务器与Ubuntu客户端双机互通。
5. 处理地址、网关或DNS配置错误。

### 3. 素质目标

1. 不在远程会话中盲目修改唯一管理地址。
2. 不照抄与实际VMnet8不匹配的示例IP。
3. 修改前保存原连接名和参数，修改后分层复测。

## 三、知识准备

```text
应用访问名称
→ DNS把名称解析为IP
→ 路由表选择出口和下一跳
→ 网卡使用本机IP发送数据
→ 目标主机上的服务处理请求
```

| 对象 | 作用 | 检查命令 |
|---|---|---|
| 网卡 | 收发数据帧 | `ip link`、`nmcli device` |
| IP和前缀 | 标识主机和直连网段 | `ip address` |
| 路由 | 决定目标从哪里发送 | `ip route`、`ip route get` |
| 默认网关 | 非直连网络的下一跳 | `ip route` |
| DNS | 把名称解析为IP | `getent hosts`、`nmcli` |
| NetworkManager连接 | 保存可持久激活的配置 | `nmcli connection` |

## 四、实验环境

- 使用VMware控制台操作，不通过SSH修改当前地址。
- VMware网卡模式为NAT。
- 教师提前公布VMnet8网段、网关、DNS和每位学生的静态IP。
- 下表示例不能直接照抄，必须换成实际规划：

| 项目 | 示例 | 实际值 |
|---|---|---|
| 网卡 | `ens33` |  |
| VMnet8网段 | `192.168.200.0/24` |  |
| 默认网关 | `192.168.200.2` |  |
| Rocky服务器静态IP | `192.168.200.10/24` |  |
| Ubuntu客户端静态IP | `192.168.200.20/24` |  |
| DNS | 教师指定地址 |  |
| 主机名 | `rocky-vm` |  |

## 五、项目任务

1. 记录当前网络基线。
2. 核对VMnet8地址规划和IP冲突。
3. 建立持久静态连接。
4. 验证网卡、IP、路由、网关、DNS和软件源路径。
5. 制造一个可回退的DNS故障并完成修复。
6. 使用Netplan配置Ubuntu客户端静态地址。
7. 完成服务器与客户端双向连通性验证。
8. 保存双机网络配置和排障记录。

## 六、实验步骤

### 任务一：记录网络基线

```bash
mkdir -p ~/m1-project/evidence ~/m1-project/backup/network
{
    hostnamectl
    ip -br link
    ip -br address
    ip route
    nmcli device status
    nmcli connection show --active
} | tee ~/m1-project/evidence/lab08-network-before.txt
```

取得默认出口和活动连接：

```bash
IFACE=$(ip route show default | awk 'NR==1 {print $5}')
OLD_CON=$(nmcli -g GENERAL.CONNECTION device show "$IFACE")
printf 'interface=%s\nold_connection=%s\n' "$IFACE" "$OLD_CON"
```

如果接口为空、连接名为`--`或结果明显异常，停止后续修改并先检查VMware网卡。

> **验收点**：已记录实际网卡、活动连接、DHCP地址和默认网关。

### 任务二：检查地址规划

#### 步骤1：确认实际网络

```bash
ip route
ip route get 1.1.1.1
nmcli -f GENERAL,IP4,DHCP4 device show "$IFACE"
```

从教师地址表取得目标IP。先检查本机是否已经使用：

```bash
ip address show | grep -F '<目标IP>' || true
```

再从同网段环境检查冲突。可使用：

```bash
arping -D -I "$IFACE" -c 3 '<目标IP>'
```

如果`arping`未安装，使用教师提供的地址分配表，不因安装工具阻塞核心实验。检测到响应时不要使用该IP。

> **验收点**：目标IP属于实际VMnet8网段，没有与已知地址重复。

### 任务三：备份并创建静态连接

#### 步骤2：保存连接参数

```bash
nmcli connection show "$OLD_CON" > ~/m1-project/backup/network/old-connection.txt
sudo cp -a /etc/NetworkManager/system-connections/. ~/m1-project/backup/network/system-connections/
```

保存`OLD_CON`名称，回退时需要重新激活它。

#### 步骤3：设置实验变量

按实际地址替换：

```bash
STATIC_IP='<本机IP/前缀>'
GATEWAY='<默认网关>'
DNS1='<教师指定DNS>'
printf 'iface=%s ip=%s gateway=%s dns=%s\n' "$IFACE" "$STATIC_IP" "$GATEWAY" "$DNS1"
```

不要保留尖括号。把输出与教师地址表逐项核对后再继续。

#### 步骤4：创建连接

```bash
sudo nmcli connection add type ethernet con-name course-static ifname "$IFACE" \
  ipv4.addresses "$STATIC_IP" \
  ipv4.gateway "$GATEWAY" \
  ipv4.dns "$DNS1" \
  ipv4.method manual \
  connection.autoconnect yes
```

检查保存值：

```bash
nmcli -f connection.id,connection.interface-name,ipv4.method,ipv4.addresses,ipv4.gateway,ipv4.dns connection show course-static
```

> **验收点**：静态连接参数和实际规划完全一致。

#### 步骤5：激活静态连接

确保正在VMware控制台中操作，然后执行：

```bash
sudo nmcli connection up course-static
ip -br address show dev "$IFACE"
ip route
```

若立即失去网络但控制台仍可用，回退：

```bash
sudo nmcli connection up "$OLD_CON"
```

> **验收点**：网卡显示目标静态IP，默认路由指向实际NAT网关。

### 任务四：分层验证

#### 步骤6：检查本机和路由

```bash
ip -br link show dev "$IFACE"
ip -br address show dev "$IFACE"
ip route
ip route get "$GATEWAY"
```

#### 步骤7：测试网关和名称解析

```bash
ping -c 3 "$GATEWAY"
getent hosts mirrors.rockylinux.org
```

公共网络受限时，网关可达仍可证明本地NAT网络的关键部分正常。记录互联网限制，不把它误判为静态IP配置失败。

#### 步骤8：检查有效DNS配置

```bash
nmcli -g IP4.DNS device show "$IFACE"
cat /etc/resolv.conf
```

在NetworkManager管理的系统中，直接编辑`/etc/resolv.conf`可能被覆盖。持久DNS应写入连接配置。

> **验收点**：完成网卡、地址、路由、网关和DNS五层验证。

### 任务五：主机名配置

```bash
sudo hostnamectl set-hostname rocky-vm
hostnamectl
hostname
```

主机名用于识别服务器角色，不替代DNS。修改主机名后，旧Shell提示符可能在重新登录后更新。

### 任务六：DNS故障与恢复

#### 步骤9：保存正确DNS并写入错误值

```bash
GOOD_DNS=$(nmcli -g ipv4.dns connection show course-static)
printf 'good_dns=%s\n' "$GOOD_DNS"
sudo nmcli connection modify course-static ipv4.dns '192.0.2.53'
sudo nmcli connection up course-static
```

`192.0.2.0/24`为文档示例地址段，本实验用它制造不可用DNS。观察：

```bash
ping -c 2 "$GATEWAY"
getent hosts training-name.invalid
getent hosts mirrors.rockylinux.org
```

网关仍可能可达，域名查询失败，说明故障集中在名称解析层。

#### 步骤10：恢复DNS

```bash
sudo nmcli connection modify course-static ipv4.dns "$GOOD_DNS"
sudo nmcli connection up course-static
nmcli -g IP4.DNS device show "$IFACE"
getent hosts mirrors.rockylinux.org
```

如果公共域名受机房网络限制，使用教师提供的校内测试名称完成复测。

> **验收点**：记录故障现象、网关证据、DNS证据、根因、修复和复测。

### 任务七：保存最终配置

```bash
{
    hostnamectl
    ip -br address
    ip route
    nmcli connection show --active
    nmcli -f GENERAL,IP4 device show "$IFACE"
} > ~/m1-project/evidence/lab08-network-after.txt
```

### 任务八：配置Ubuntu客户端静态网络

在Ubuntu Server客户端的VMware控制台操作。先记录DHCP状态和实际网卡名：

```bash
mkdir -p ~/m1-project/evidence ~/m1-project/backup
{
    hostnamectl
    ip -brief address
    ip route
    ls -l /etc/netplan
    sudo netplan get
} | tee ~/m1-project/evidence/lab08-client-network-before.txt

UBUNTU_IFACE=$(ip route show default | awk 'NR==1 {print $5}')
printf 'ubuntu_interface=%s\n' "$UBUNTU_IFACE"
```

如果接口变量为空，停止配置并检查VMware NAT网卡。备份Netplan目录：

```bash
sudo cp -a /etc/netplan ~/m1-project/backup/netplan-before-static
sudo chown -R "$USER:$USER" ~/m1-project/backup/netplan-before-static
```

教师为每台Ubuntu客户端分配地址。记录实际值：

```text
UBUNTU_IFACE=________________
UBUNTU_IP_CIDR=______________
GATEWAY=_____________________
DNS1=________________________
DNS2=________________________
ROCKY_IP=____________________
```

Ubuntu Server 22.04通常使用Netplan保存网络配置。创建课程配置：

```bash
sudo vim /etc/netplan/99-course-static.yaml
```

按照实际网卡和地址填写；下面示例不能直接照抄：

```yaml
network:
  version: 2
  ethernets:
    ens33:
      dhcp4: false
      addresses:
        - 192.168.200.20/24
      routes:
        - to: default
          via: 192.168.200.2
      nameservers:
        addresses:
          - 223.5.5.5
          - 119.29.29.29
```

YAML只能使用空格缩进，不使用Tab。先检查生成配置：

```bash
sudo netplan generate
```

没有错误后，在VMware控制台使用安全试用：

```bash
sudo netplan try
```

确认新网络可用后按提示接受。若网络失效且未确认，Netplan会在超时后尝试回退。随后执行：

```bash
sudo netplan apply
ip -brief address show dev "$UBUNTU_IFACE"
ip route
getent hosts mirrors.ubuntu.com
```

> **验收点**：Ubuntu使用教师分配的静态地址，存在正确默认路由和DNS；重启后配置仍生效。

### 任务九：完成双机验证

在Ubuntu客户端测试Rocky服务器：

```bash
ping -c 3 <ROCKY_IP>
nc -vz <ROCKY_IP> 22
```

如果`nc`尚未安装，可使用：

```bash
sudo apt update
sudo apt install -y netcat-openbsd
```

在Rocky服务器测试Ubuntu客户端：

```bash
ping -c 3 <UBUNTU_IP>
ip route get <UBUNTU_IP>
```

若机房策略禁止ICMP，但后续TCP连接成功，应记录策略差异，不把ping失败直接等同于主机离线。

在Ubuntu保存最终证据：

```bash
{
    hostnamectl
    ip -brief address
    ip route
    sudo netplan get
    getent hosts mirrors.ubuntu.com
} > ~/m1-project/evidence/lab08-client-network-after.txt
```

> **验收点**：两台机器地址不冲突；Ubuntu能够连接Rocky的22端口；双机最终网络参数均有记录。

## 七、独立实践

1. 使用`ip route get`判断访问教师指定地址时使用的出口、源地址和下一跳。
2. 分别说明“没有IP”“没有默认路由”和“DNS错误”的典型现象。
3. 写出从静态连接回退到原DHCP连接的命令，但不删除当前有效连接。
4. 解释为什么静态IP配置不能照抄其他同学的地址。
5. 比较Rocky NetworkManager连接与Ubuntu Netplan YAML分别如何保存持久网络配置。

## 八、验收标准

- [ ] 地址规划与实际VMnet8一致，没有IP冲突。
- [ ] 原连接名称和配置已保存。
- [ ] `course-static`使用持久静态IP、网关和DNS。
- [ ] 网卡状态、IP、路由、网关和DNS均已验证。
- [ ] 主机名符合规范。
- [ ] 已完成一次DNS故障定位、修复和复测。
- [ ] 能写出回退到原连接的方法。
- [ ] 修改过程在VMware控制台完成，没有失去唯一管理通道。
- [ ] Ubuntu客户端的Netplan语法检查通过，静态地址重启后仍有效。
- [ ] Ubuntu能够连接Rocky的22端口，双机地址不冲突。

## 九、成果提交

1. 地址规划表。
2. `lab08-network-before.txt`和`lab08-network-after.txt`。
3. 静态连接关键参数。
4. 分层连通性验证记录。
5. DNS故障报告。
6. Ubuntu配置文件、前后网络证据和双机验证结果。
7. 独立实践答案和Rocky/Ubuntu回退说明。

## 十、常见问题

### Q1：激活后没有默认路由

检查`ipv4.gateway`和前缀是否正确：

```bash
nmcli -f ipv4.addresses,ipv4.gateway connection show course-static
```

### Q2：网关能通但域名不能解析

检查有效DNS、`/etc/resolv.conf`和`getent hosts`。不要先重装网络服务。

### Q3：静态IP激活后与其他主机冲突

立即激活原连接或修改为教师重新分配的地址。不要继续使用冲突IP。

### Q4：重启后又回到DHCP连接

检查两个连接的`connection.autoconnect`和优先级。教师可统一禁用旧连接自动启动，但应保留回退能力。

## 十一、课后思考与拓展

1. 有IP为什么仍可能无法访问外部网络？
2. `/etc/resolv.conf`为什么可能被NetworkManager覆盖？
3. 静态地址与DHCP固定租约各有什么优缺点？

## 十二、环境保留

保留Rocky的`course-static`和Ubuntu的`99-course-static.yaml`用于后续SSH和服务实验。不要删除Rocky旧连接或Ubuntu备份；在教师确认全班双机静态网络稳定前保留回退入口。
