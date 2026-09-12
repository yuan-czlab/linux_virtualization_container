# 实验8：Linux网络配置与连通性诊断

> 所属模块：模块二 网络、远程管理与基础防护  
> 建议学时：4学时  
> 实验方式：个人  
> 对应教材：《模块二 网络、远程管理与基础防护》第13章  
> 前置实验：实验7  
> 项目成果：三机地址规划、持久静态网络、hosts名称解析、互通矩阵和一次网络故障恢复记录

## 一、项目情境

通过DHCP获得的地址可能发生变化，不利于SSH和服务访问。你需要先调查VMware NAT网络，再为`rocky-server`、`rocky-web`和`ubuntu-client`建立不冲突的持久静态地址，并能够按照“网卡—地址—路由—DNS—目标服务”的顺序判断网络问题。

## 二、实验目标

### 1. 知识目标

1. 说明网卡、连接配置、IP地址、前缀、默认网关和DNS各自解决的问题。
2. 区分`ip`显示的运行状态和NetworkManager保存的持久连接配置。
3. 说明本机、同网段、网关、外部IP和域名测试的不同意义。

### 2. 能力目标

1. 使用`ip`、`nmcli`、`hostnamectl`和`resolvectl`或配置文件检查网络。
2. 根据实际VMnet8网段制定不冲突的地址计划。
3. 创建、验证和回退三台机器的NetworkManager静态配置。
4. 完成三机互通、hosts解析和SSH端口预检。
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
| rocky-server静态IP | `192.168.200.10/24` |  |
| rocky-web静态IP | `192.168.200.20/24` |  |
| ubuntu-client静态IP | `192.168.200.30/24` |  |
| DNS | 教师指定地址 |  |
| 三台主机名 | `rocky-server`、`rocky-web`、`ubuntu-client` |  |

## 五、项目任务

1. 记录当前网络基线。
2. 核对VMnet8地址规划和IP冲突。
3. 建立持久静态连接。
4. 验证网卡、IP、路由、网关、DNS和软件源路径。
5. 制造一个可回退的DNS故障并完成修复。
6. 使用NetworkManager配置Ubuntu图形客户端静态地址。
7. 配置三台机器的hosts并完成互通矩阵。
8. 保存三机网络配置和排障记录。

## 六、实验步骤

### 任务一：记录rocky-server网络基线

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

### 任务五：核对主机名

```bash
hostnamectl --static
test "$(hostnamectl --static)" = 'rocky-server' && echo PASS || echo FAIL
```

本实验不重新命名主机。输出必须为`rocky-server`；不一致时回到实验1标准修正后再继续。

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

### 任务七：保存rocky-server最终配置

```bash
{
    hostnamectl
    ip -br address
    ip route
    nmcli connection show --active
    nmcli -f GENERAL,IP4 device show "$IFACE"
} > ~/m1-project/evidence/lab08-network-after.txt
```

### 任务八：在rocky-web重复建立静态网络

启动`rocky-web`并在VMware控制台登录。重复任务一至任务四，但必须使用教师分配给`rocky-web`的独立地址。连接名仍可使用`course-static`，因为它位于另一台主机。

核对身份：

```bash
test "$(whoami)" = 'rocky-web' && echo USER_PASS || echo USER_FAIL
test "$(hostnamectl --static)" = 'rocky-web' && echo HOST_PASS || echo HOST_FAIL
```

保存最终证据：

```bash
mkdir -p ~/m1-project/evidence
{
  hostnamectl
  ip -brief address
  ip route
  nmcli connection show --active
} > ~/m1-project/evidence/lab08-rocky-web-network-after.txt
```

> **验收点**：`rocky-web`与`rocky-server`地址不同，网关和DNS符合同一VMnet8规划。

### 任务九：配置Ubuntu Desktop静态网络

Ubuntu 22.04 Desktop默认由NetworkManager管理桌面连接。本实验使用图形设置观察配置，同时使用`nmcli`完成可复查的操作，不再套用Ubuntu Server的Netplan步骤。

在`ubuntu-client`打开Terminal：

```bash
mkdir -p ~/m1-project/evidence ~/m1-project/backup
hostnamectl --static
nmcli device status
nmcli connection show
ip -brief address
ip route
```

取得网卡和当前连接名：

```bash
CLIENT_IFACE=$(ip route show default | awk 'NR==1 {print $5}')
OLD_CLIENT_CON=$(nmcli -g GENERAL.CONNECTION device show "$CLIENT_IFACE")
nmcli connection show "$OLD_CLIENT_CON" > ~/m1-project/backup/ubuntu-dhcp-connection.txt
printf 'interface=%s old_connection=%s\n' "$CLIENT_IFACE" "$OLD_CLIENT_CON"
```

先在“设置 → 网络 → 有线 → 齿轮 → IPv4”中找到手动地址界面，核对教师地址表，但暂不点击应用。回到Terminal，用实际值执行：

```bash
CLIENT_IP='<ubuntu-client地址/前缀>'
GATEWAY='<VMnet8网关>'
DNS1='<教师指定DNS>'

sudo nmcli connection add type ethernet \
  con-name course-client-static ifname "$CLIENT_IFACE" \
  ipv4.method manual \
  ipv4.addresses "$CLIENT_IP" \
  ipv4.gateway "$GATEWAY" \
  ipv4.dns "$DNS1" \
  connection.autoconnect yes
```

在VMware控制台激活：

```bash
sudo nmcli connection up course-client-static
ip -brief address show dev "$CLIENT_IFACE"
ip route
nmcli -g IP4.DNS device show "$CLIENT_IFACE"
```

失败时回退：

```bash
sudo nmcli connection up "$OLD_CLIENT_CON"
```

> **验收点**：桌面网络界面和`nmcli`显示同一静态地址、网关与DNS，重启后配置仍然生效。

### 任务十：配置三机名称解析

把教师分配的三个实际地址写入三台机器的`/etc/hosts`。下面只表示格式：

```text
<ROCKY_SERVER_IP>  rocky-server
<ROCKY_WEB_IP>     rocky-web
<UBUNTU_CLIENT_IP> ubuntu-client
```

修改前备份：

```bash
sudo cp -a /etc/hosts "/etc/hosts.before-lab08.$(date +%Y%m%d-%H%M%S)"
sudo vim /etc/hosts
getent hosts rocky-server rocky-web ubuntu-client
```

三台机器的内容必须一致，地址不得照抄示例。

### 任务十一：完成三机互通矩阵

在`ubuntu-client`执行：

```bash
ping -c 3 rocky-server
ping -c 3 rocky-web
nc -vz rocky-server 22
nc -vz rocky-web 22
```

缺少`nc`时安装：

```bash
sudo apt update
sudo apt install -y netcat-openbsd
```

在两台Rocky之间双向测试，并分别测试客户端：

```bash
ping -c 3 <另一台Rocky主机名>
ping -c 3 ubuntu-client
ip route get <目标IP>
```

填写矩阵：

| 来源 | rocky-server | rocky-web | ubuntu-client |
|---|---|---|---|
| rocky-server | 本机 |  |  |
| rocky-web |  | 本机 |  |
| ubuntu-client | SSH/ICMP | SSH/ICMP | 本机 |

若ICMP被策略禁止但TCP 22成功，应记录差异，不能把ping失败直接等同于主机离线。

> **验收点**：三机名称均能解析为规划地址，地址不冲突，客户端可以连接两台Rocky的22端口。

## 七、独立实践

1. 使用`ip route get`判断访问教师指定地址时使用的出口、源地址和下一跳。
2. 分别说明“没有IP”“没有默认路由”和“DNS错误”的典型现象。
3. 写出从静态连接回退到原DHCP连接的命令，但不删除当前有效连接。
4. 解释为什么静态IP配置不能照抄其他同学的地址。
5. 比较Ubuntu桌面网络设置与`nmcli`显示的连接参数为什么应保持一致。

## 八、验收标准

- [ ] 地址规划与实际VMnet8一致，没有IP冲突。
- [ ] 原连接名称和配置已保存。
- [ ] 两台Rocky的`course-static`分别使用规划的静态IP、网关和DNS。
- [ ] 网卡状态、IP、路由、网关和DNS均已验证。
- [ ] 主机名符合规范。
- [ ] 已完成一次DNS故障定位、修复和复测。
- [ ] 能写出回退到原连接的方法。
- [ ] 修改过程在VMware控制台完成，没有失去唯一管理通道。
- [ ] Ubuntu客户端的NetworkManager静态连接重启后仍有效。
- [ ] hosts内容一致，三机互通矩阵已完成，Ubuntu能连接两台Rocky的22端口。

## 九、成果提交

1. 地址规划表。
2. `lab08-network-before.txt`和`lab08-network-after.txt`。
3. 静态连接关键参数。
4. 分层连通性验证记录。
5. DNS故障报告。
6. Ubuntu NetworkManager配置、前后证据和三机互通矩阵。
7. 独立实践答案和三台机器的回退说明。

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

保留两台Rocky的`course-static`和Ubuntu的`course-client-static`，供后续SSH和服务实验使用。不要删除原DHCP连接；在教师确认全班三机静态网络稳定前保留回退入口。
