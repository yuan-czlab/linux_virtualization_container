# Lab41：VMware 虚拟网络模式与数据路径

> 课时：2 | 类型：个人/双人 | 前置：Lab40

## 一、你会学到什么

- 能说清NAT、桥接、仅主机三种模式的数据路径
- 能从虚拟机、宿主机和局域网设备三个视角验证连通性
- 能根据上网、对外服务、隔离实验等需求选择网络模式
- 能区分“网卡已连接、获得IP、路由正确、服务可访问”四种状态
- 能在切换网络模式失败后恢复原有网络

## 二、实验环境

- 宿主机：Windows 10/11 + VMware Workstation
- 虚拟机：Rocky Linux 9，主机名`web-server`
- 推荐先创建快照：`before-lab41-network`
- 记录宿主机物理网卡、VMnet8（NAT）、VMnet1（仅主机）的IPv4地址

> 桥接模式可能受到校园网认证、Wi-Fi驱动或地址准入限制。若无法获得地址，仍需完成数据路径分析和故障记录，不以“强行联网”为目标。

## 三、先画模型再操作

### NAT模式

```text
web-server → VMnet8虚拟交换机 → VMware NAT → 宿主机物理网卡 → 外部网络
```

### 桥接模式

```text
web-server虚拟网卡 → VMware桥接 → 宿主机物理网卡所在局域网
```

### 仅主机模式

```text
web-server ↔ VMnet1虚拟交换机 ↔ 宿主机VMnet1网卡
                 └── 默认不通外网
```

理论检查：分别指出三种模式下，虚拟机的默认网关通常由谁提供。

## 四、实验步骤

### 步骤1：保存当前网络基线

```bash
mkdir -p ~/lab41
ip -br addr | tee ~/lab41/before-ip.txt
ip route | tee ~/lab41/before-route.txt
cat /etc/resolv.conf | tee ~/lab41/before-dns.txt
nmcli connection show | tee ~/lab41/before-nmcli.txt
```

在Windows PowerShell记录：

```powershell
ipconfig /all
Get-NetAdapter | Format-Table Name,Status,MacAddress,LinkSpeed
```

> **验收点**：能够指出Rocky当前IP、默认网关、DNS和对应VMnet。

### 步骤2：测试NAT模式

1. 关闭虚拟机，将网卡切换为NAT并确认“已连接”。
2. 启动虚拟机，重新激活连接：

```bash
sudo nmcli networking off
sudo nmcli networking on
sudo nmcli connection up "$(nmcli -t -f NAME connection show --active | head -1)"
ip -br addr
ip route
```

3. 按顺序验证：

```bash
ping -c 2 默认网关IP
ping -c 2 宿主机VMnet8地址
curl -I --connect-timeout 5 https://mirrors.aliyun.com
```

4. 宿主机反向测试虚拟机IP，并记录是否成功。

> **验收点**：画出NAT模式中数据包离开虚拟机后的下一跳，记录IP、网关和测试结果。

### 步骤3：测试桥接模式

1. 关闭虚拟机，将网卡切换为桥接。
2. 在“虚拟网络编辑器”中明确桥接到有线或无线物理网卡，避免自动选择错误接口。
3. 启动后查看地址：

```bash
ip -br addr
ip route
nmcli device show | grep -E 'GENERAL.DEVICE|IP4.ADDRESS|IP4.GATEWAY|IP4.DNS'
```

4. 验证宿主机、默认网关和同一局域网另一台设备。
5. 若无地址，依次记录：网卡状态、DHCP结果、校园网是否限制新MAC、Wi-Fi是否允许桥接。

> **验收点**：能够解释桥接模式下虚拟机为什么像一台独立的局域网设备。

### 步骤4：测试仅主机模式

1. 关闭虚拟机，将网卡切换为仅主机模式。
2. 启动并查看VMnet1网段地址和路由。
3. 完成以下验证：

```bash
ping -c 2 宿主机VMnet1地址
ping -c 2 另一台仅主机模式虚拟机IP
ip route
curl -I --connect-timeout 3 https://mirrors.aliyun.com
```

4. 解释为什么宿主机互通但外部访问通常失败。

> **验收点**：仅主机网络能够用于隔离实验，且学生能用路由表说明无法访问外网的原因。

### 步骤5：完成连接矩阵

| 测试项 | NAT | 桥接 | 仅主机 | 证据命令 |
|---|---|---|---|---|
| VM→宿主机 | | | | `ping` |
| 宿主机→VM | | | | `ping`/`Test-NetConnection` |
| VM→同模式VM | | | | `ping` |
| VM→默认网关 | | | | `ping`/`ip route` |
| VM→外部HTTP | | | | `curl -I` |
| 局域网设备→VM | | | | `ping`/`curl` |

### 步骤6：场景选型与故障排查

为每个场景选择模式并写出理由：

1. 学生虚拟机需要稳定下载软件包，但不希望暴露给校园网。
2. 局域网同学需要直接访问虚拟机中的Web服务。
3. 网络安全课程需要搭建完全隔离的攻击与靶机环境。
4. 三台服务器既要内部互通，又要通过一台机器访问外部网络。

教师从以下故障中选择一个：

- 虚拟网卡未勾选“已连接”
- 静态IP与当前VMnet网段不一致
- 默认路由仍指向切换前网关
- 桥接到了未联网的物理网卡

学生必须按“链路→IP→路由→DNS→服务”的顺序排查。

### 步骤7：恢复课程标准网络

将虚拟机恢复到课程统一的NAT网络，并验证：

```bash
ip -br addr
ip route
ping -c 2 默认网关IP
```

必要时恢复实验前快照。

## 五、验收标准

- [ ] 三种模式均有IP、路由和连通性记录
- [ ] 完成连接矩阵和三张数据流简图
- [ ] 能为四个业务场景选择网络模式并说明理由
- [ ] 能定位至少一个网络模式切换故障
- [ ] 实验结束恢复课程统一NAT环境

## 六、常见问题

**Q：桥接模式无法获得IP，是Linux配置错了吗？**

A：不一定。先确认桥接的物理网卡、校园网DHCP、Wi-Fi驱动和新MAC准入。保留证据后可改用NAT，不要把环境限制误判为Linux命令错误。

**Q：NAT模式下宿主机能否访问虚拟机？**

A：通常可以访问VMnet8内的虚拟机地址；局域网其他设备一般不能直接访问。具体取决于宿主防火墙和VMware网络配置。

**Q：为什么切换模式后仍然保留旧IP？**

A：NetworkManager连接配置可能是静态地址，或旧租约尚未释放。检查`nmcli connection show`，确认地址和当前VMnet匹配。

## 七、课后思考

1. Docker的bridge/host/none与VMware网络模式有哪些相似点，哪些不能直接对应？
2. 云服务器中的VPC、子网、路由表、公网IP和安全组分别对应实验中的哪些对象？
