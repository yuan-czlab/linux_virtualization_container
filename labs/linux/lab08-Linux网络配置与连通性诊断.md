# 实验8：Linux网络配置与连通性诊断

> 所属模块：模块二 网络远程管理与基础防护
> 建议学时：4学时
> 实验方式：2～3人小组，每人完成自己的三台虚拟机
> 对应教材：2.1 IP、网卡、路由与DNS客户端
> 知识前置：模块一全部内容、2.1教材与课前网络参数表
> 状态依赖：实验1交付的三台虚拟机、可用的VMware NAT网络和管理员控制台；不依赖实验7产生的文件
> 建议起点：`Linux-L1`
> 项目成果：三机静态网络、网络基线记录、互通矩阵、DNS故障单和课程环境文件

## 一、项目情境

某小型企业准备部署两台Linux服务器和一台运维客户端。服务器如果一直使用DHCP，地址可能变化，后续SSH、Nginx、数据库和容器实验就无法使用固定目标。

本实验需要完成以下工作：

1. 调查VMware NAT网络，不照抄他人的IP。
2. 为`rocky-server`、`rocky-web`和`ubuntu-client`配置三个不同的静态地址。
3. 验证网卡、IP、路由、网关和DNS。
4. 完成三机名称解析和互通测试。
5. 制造一次DNS故障，并按证据定位和恢复。
6. 保存后续实验继续使用的三机地址。

## 二、实验规则

### 2.1 一次只做一个动作

本实验中的命令按顺序逐条执行。执行一条，观察结果正确后，再执行下一条。不要把整个实验复制成脚本运行。

### 2.2 必须使用VMware控制台

修改当前网络连接可能中断远程会话。三台虚拟机都应从VMware控制台登录后再修改地址。

### 2.3 尖括号表示需要替换

例如：

```text
sudo arping -D -I <网卡名> -c 3 <准备使用的IPv4地址>
```

`<网卡名>`和`<准备使用的IPv4地址>`不是可以直接输入的文字。必须换成参数表中的实际值，并删除尖括号。

### 2.4 保留原DHCP连接

本实验只新增课程静态连接，不删除原DHCP连接。静态配置失败时，需要依靠原连接回退。

## 三、网络参数表

先根据VMware“虚拟网络编辑器”中的VMnet8信息和教师公布的地址规划填写“实际值”列。

| 项目 | 示例值 | 实际值 |
|---|---|---|
| VMnet8网段 | `192.168.200.0/24` | |
| VMnet8网关 | `192.168.200.2` | |
| DNS服务器 | `192.168.200.2` | |
| `rocky-server`地址 | `192.168.200.10/24` | |
| `rocky-web`地址 | `192.168.200.20/24` | |
| `ubuntu-client`地址 | `192.168.200.30/24` | |

> 示例值只用于说明格式。实际网段不是`192.168.200.0/24`时，不能照抄示例。

三台虚拟机必须满足：

- 三个IP位于同一个VMnet8网段。
- 三个IP互不相同。
- 不能使用网关地址、网络地址和广播地址。
- 不能与其他同学或DHCP地址池中的地址冲突。

【截图位置：VMware虚拟网络编辑器中的VMnet8子网、网关和DHCP范围】

## 四、任务一：记录三台虚拟机的网络基线

先在`rocky-server`的VMware控制台中执行。

### 4.1 创建实验目录

```bash
mkdir -p ~/m1-project/evidence
```

```bash
mkdir -p ~/m1-project/backup/network
```

### 4.2 记录主机身份

```bash
hostnamectl --static
```

预期主机名是`rocky-server`。如果不一致，应先回到实验1修正身份。

把结果写入证据文件：

```bash
hostnamectl --static | tee ~/m1-project/evidence/lab08-network-before.txt
```

### 4.3 观察网卡、IP和路由

```bash
ip -brief link
```

```bash
ip -brief address
```

```bash
ip route
```

将结果追加到证据文件：

```bash
ip -brief link | tee -a ~/m1-project/evidence/lab08-network-before.txt
```

```bash
ip -brief address | tee -a ~/m1-project/evidence/lab08-network-before.txt
```

```bash
ip route | tee -a ~/m1-project/evidence/lab08-network-before.txt
```

从默认路由中找到`dev`后面的出口网卡名，并写入表格。

### 4.4 观察NetworkManager连接

```bash
nmcli device status
```

```bash
nmcli connection show --active
```

```bash
nmcli connection show
```

需要区分：

- `DEVICE`是网卡设备名，例如`ens33`。
- `NAME`是连接配置名，例如`ens33`或`Wired connection 1`。
- 后续`ifname`使用网卡名，回退时使用原连接名。

把`rocky-server`的实际信息写入下表：

| 项目 | 实际值 |
|---|---|
| 主机名 | |
| 出口网卡名 | |
| 原活动连接名 | |
| 原IPv4地址 | |
| 原默认网关 | |

在`rocky-web`和`ubuntu-client`上重复4.1～4.4，并分别记录信息。不要假定三台机器的网卡名和连接名完全相同。

## 五、任务二：检查静态地址是否可用

在每台虚拟机上检查自己准备使用的地址。命令格式如下：

```text
sudo arping -D -I <本机网卡名> -c 3 <本机准备使用的纯IPv4地址>
```

示例中的`192.168.200.10`不带`/24`：

```text
sudo arping -D -I ens33 -c 3 192.168.200.10
```

如果系统提示找不到`arping`，Rocky可以安装工具：

```bash
sudo dnf install -y iputils
```

Ubuntu可以安装工具：

```bash
sudo apt update
```

```bash
sudo apt install -y iputils-arping
```

判断结果：

- 没有收到其他主机应答：可继续结合地址分配表判断。
- 收到其他主机应答：该地址可能已被使用，立即停止并重新分配。
- 工具不可安装：以教师统一地址表为准，不因安装工具阻塞核心实验。

## 六、任务三：配置rocky-server静态网络

### 6.1 保存原连接信息

先确认备份目录中还没有同名备份：

```bash
ls -ld ~/m1-project/backup/network/system-connections-before-lab08
```

如果提示`No such file or directory`，说明可以创建第一次备份：

```bash
sudo cp -a /etc/NetworkManager/system-connections ~/m1-project/backup/network/system-connections-before-lab08
```

使用4.4记录的“原活动连接名”查看完整配置。下面是命令格式：

```text
nmcli connection show "<原活动连接名>"
```

确认名称后，把配置保存到文件：

```text
nmcli connection show "<原活动连接名>" > ~/m1-project/backup/network/rocky-server-old-connection.txt
```

如果连接名不含空格，也建议保留双引号。

### 6.2 创建新连接

根据实际参数拼写一条`nmcli connection add`命令：

```text
sudo nmcli connection add type ethernet con-name course-static ifname <网卡名> ipv4.method manual ipv4.addresses <静态IP/前缀> ipv4.gateway <网关> ipv4.dns <DNS> connection.autoconnect yes connection.autoconnect-priority 100
```

例如，只有实际参数与示例完全一致时，才可以写成：

```text
sudo nmcli connection add type ethernet con-name course-static ifname ens33 ipv4.method manual ipv4.addresses 192.168.200.10/24 ipv4.gateway 192.168.200.2 ipv4.dns 192.168.200.2 connection.autoconnect yes connection.autoconnect-priority 100
```

执行自己填写的命令后，检查保存结果：

```bash
nmcli connection show course-static
```

只查看本实验最重要的字段：

```bash
nmcli -f connection.id,connection.interface-name,ipv4.method,ipv4.addresses,ipv4.gateway,ipv4.dns connection show course-static
```

逐项与参数表比较。如果有一项错误，不要激活连接。使用下面的格式修改对应字段：

```text
sudo nmcli connection modify course-static ipv4.addresses <正确IP/前缀>
```

```text
sudo nmcli connection modify course-static ipv4.gateway <正确网关>
```

```text
sudo nmcli connection modify course-static ipv4.dns <正确DNS>
```

### 6.3 激活并逐层验证

确认当前窗口是VMware控制台，然后激活：

```bash
sudo nmcli connection up course-static
```

检查活动连接：

```bash
nmcli connection show --active
```

检查地址：

```bash
ip -brief address
```

检查默认路由：

```bash
ip route
```

使用参数表中的实际网关执行测试：

```text
ping -c 3 <实际网关>
```

检查DNS：

```bash
nmcli -f IP4.DNS device show
```

```bash
getent hosts mirrors.rockylinux.org
```

机房无法访问公共网络时，网关可达而公共域名失败不一定说明静态地址错误。应记录限制，并使用校内测试名称复测。

### 6.4 失败时回退

静态连接无法正常使用时，在VMware控制台执行：

```text
sudo nmcli connection up "<原活动连接名>"
```

回退后重新查看地址和路由：

```bash
ip -brief address
```

```bash
ip route
```

不要删除`course-static`。先根据错误证据修改它，再重新激活。

## 七、任务四：配置rocky-web静态网络

切换到`rocky-web`的VMware控制台，重复第六部分。需要注意：

- 使用`rocky-web`自己的网卡名和原连接名。
- 连接名仍可使用`course-static`，因为它位于另一台虚拟机。
- 静态IP必须使用参数表中分配给`rocky-web`的地址。
- 网关和DNS通常与`rocky-server`一致，但仍要以实际表格为准。

先确认身份：

```bash
whoami
```

```bash
hostnamectl --static
```

配置后保存证据：

```bash
mkdir -p ~/m1-project/evidence
```

```bash
hostnamectl --static | tee ~/m1-project/evidence/lab08-network-after.txt
```

```bash
ip -brief address | tee -a ~/m1-project/evidence/lab08-network-after.txt
```

```bash
ip route | tee -a ~/m1-project/evidence/lab08-network-after.txt
```

```bash
nmcli connection show --active | tee -a ~/m1-project/evidence/lab08-network-after.txt
```

## 八、任务五：配置ubuntu-client静态网络

Ubuntu 22.04 Desktop作为辅助系统，本任务优先使用图形界面，命令行负责验证。

### 8.1 打开配置界面

依次进入：

```text
设置 → 网络 → 有线 → 齿轮 → IPv4
```

将IPv4方式从“自动(DHCP)”改为“手动”，填写：

- Address：`ubuntu-client`的纯IPv4地址。
- Netmask：根据实际前缀填写，例如`255.255.255.0`。
- Gateway：实际VMnet8网关。
- DNS：实际DNS服务器。

填写完毕后先与参数表逐项核对，再单击“应用”。

【截图位置：Ubuntu 22.04手动IPv4配置界面】

### 8.2 重新连接并验证

关闭再打开图形界面中的有线连接，然后打开终端。

检查身份：

```bash
hostnamectl --static
```

检查活动连接：

```bash
nmcli connection show --active
```

检查地址：

```bash
ip -brief address
```

检查路由：

```bash
ip route
```

测试实际网关：

```text
ping -c 3 <实际网关>
```

检查DNS：

```bash
nmcli -f IP4.DNS device show
```

如果配置失败，在图形界面中把IPv4方式恢复为“自动(DHCP)”，重新连接后检查地址和路由。

## 九、任务六：配置三机名称解析

三台虚拟机都需要完成本任务，并且`/etc/hosts`中的三行内容必须一致。

### 9.1 备份hosts

先检查备份是否已存在：

```bash
sudo ls -l /etc/hosts.before-lab08
```

如果提示文件不存在，创建第一次备份：

```bash
sudo cp -a /etc/hosts /etc/hosts.before-lab08
```

已经存在时不要覆盖它。

### 9.2 写入名称映射

打开文件：

```bash
sudo vim /etc/hosts
```

在原内容末尾增加三行，地址使用参数表中的实际值：

```text
<rocky-server的IPv4地址>  rocky-server
<rocky-web的IPv4地址>     rocky-web
<ubuntu-client的IPv4地址> ubuntu-client
```

不要写`/24`，也不要保留尖括号。

验证三个名称：

```bash
getent hosts rocky-server
```

```bash
getent hosts rocky-web
```

```bash
getent hosts ubuntu-client
```

每个名称都必须解析为参数表中的对应地址。

需要恢复时执行：

```bash
sudo cp -a /etc/hosts.before-lab08 /etc/hosts
```

## 十、任务七：建立后续实验共用地址文件

实验9以后需要反复使用三机地址。为了避免每次重新输入，在每台虚拟机上创建同一份`course-env.sh`。这里不编写自动化脚本，只保存三行环境变量。

打开文件：

```bash
vim ~/m1-project/course-env.sh
```

根据已经验证的`/etc/hosts`填写：

```text
export ROCKY_SERVER_IP='实际的rocky-server地址'
```

```text
export ROCKY_WEB_IP='实际的rocky-web地址'
```

```text
export UBUNTU_CLIENT_IP='实际的ubuntu-client地址'
```

文件中只保留上面三行，`实际的……地址`必须换成真实IPv4地址。

限制文件权限：

```bash
chmod 600 ~/m1-project/course-env.sh
```

把三行变量加载到当前终端：

```bash
source ~/m1-project/course-env.sh
```

逐项检查：

```bash
printf '%s\n' "$ROCKY_SERVER_IP"
```

```bash
printf '%s\n' "$ROCKY_WEB_IP"
```

```bash
printf '%s\n' "$UBUNTU_CLIENT_IP"
```

如果输出仍然包含“实际的”文字，说明没有完成替换，后续实验不能继续。

## 十一、任务八：完成三机互通矩阵

### 11.1 在ubuntu-client测试两台服务器

```bash
ping -c 3 rocky-server
```

```bash
ping -c 3 rocky-web
```

检查SSH端口：

```bash
nc -vz rocky-server 22
```

```bash
nc -vz rocky-web 22
```

缺少`nc`时安装：

```bash
sudo apt update
```

```bash
sudo apt install -y netcat-openbsd
```

### 11.2 在rocky-server测试另外两台主机

```bash
ping -c 3 rocky-web
```

```bash
ping -c 3 ubuntu-client
```

```bash
ip route get "$ROCKY_WEB_IP"
```

### 11.3 在rocky-web测试另外两台主机

```bash
ping -c 3 rocky-server
```

```bash
ping -c 3 ubuntu-client
```

```bash
ip route get "$ROCKY_SERVER_IP"
```

填写测试结果：

| 来源 | rocky-server | rocky-web | ubuntu-client |
|---|---|---|---|
| rocky-server | 本机 | | |
| rocky-web | | 本机 | |
| ubuntu-client | | | 本机 |

记录时不要只写“通”或“不通”，应写成“ICMP成功”“TCP 22成功”或“ICMP失败但TCP 22成功”。

## 十二、任务九：制造并恢复DNS故障

只在`rocky-server`上完成本任务。

### 12.1 记录正确DNS

```bash
nmcli -g ipv4.dns connection show course-static
```

把输出抄到故障记录中，作为恢复值。

### 12.2 写入错误DNS

`192.0.2.53`属于文档示例地址，本实验用它模拟不可用DNS：

```bash
sudo nmcli connection modify course-static ipv4.dns 192.0.2.53
```

重新激活连接：

```bash
sudo nmcli connection up course-static
```

### 12.3 比较IP连通与名称解析

使用实际网关测试：

```text
ping -c 3 <实际网关>
```

测试名称解析：

```bash
getent hosts mirrors.rockylinux.org
```

如果网关仍可达而域名解析失败，说明地址和路由仍然工作，故障集中在DNS层。

### 12.4 恢复正确DNS

使用12.1记录的真实值：

```text
sudo nmcli connection modify course-static ipv4.dns <12.1记录的正确DNS>
```

重新激活：

```bash
sudo nmcli connection up course-static
```

验证有效DNS：

```bash
nmcli -g IP4.DNS device show
```

再次验证名称解析：

```bash
getent hosts mirrors.rockylinux.org
```

故障记录至少包含：现象、网关证据、DNS证据、根因、修复命令和复测结果。

## 十三、任务十：验证持久化

在三台虚拟机完成全部配置并保存证据后，依次重启，不要同时重启三台。

```bash
sudo reboot
```

系统启动后重新检查活动连接：

```bash
nmcli connection show --active
```

检查地址：

```bash
ip -brief address
```

检查路由：

```bash
ip route
```

检查三机名称：

```bash
getent hosts rocky-server rocky-web ubuntu-client
```

再完成一次互通矩阵。重启前成功、重启后失败，通常说明修改只进入运行状态，没有正确保存为持久配置。

## 十四、验收标准

- [ ] 网络参数表全部来自实际VMnet8和统一地址规划。
- [ ] 三台机器的网卡名、原连接名、原IP和原网关已记录。
- [ ] 两台Rocky保留原连接，并建立`course-static`。
- [ ] Ubuntu图形界面中的静态参数与命令行观察结果一致。
- [ ] 三个静态IP互不冲突，网关和DNS填写正确。
- [ ] 三台机器的`/etc/hosts`内容一致。
- [ ] `course-env.sh`只包含三个正确的地址变量。
- [ ] 三机名称解析和互通矩阵已完成。
- [ ] DNS故障已经制造、定位、恢复并复测。
- [ ] 重启后静态配置仍然生效。

## 十五、成果提交

1. 已填写的网络参数表。
2. 三台机器的网络基线记录。
3. 两台Rocky的`course-static`关键参数截图或文本。
4. Ubuntu手动IPv4配置截图。
5. 三机`/etc/hosts`和`course-env.sh`内容。
6. 三机互通矩阵。
7. DNS故障记录。
8. 重启后的网络验证结果。

## 十六、常见问题

### 16.1 `nmcli connection up course-static`提示找不到连接

先检查连接名称：

```bash
nmcli connection show
```

连接名必须与命令完全一致。

### 16.2 有静态IP但没有默认路由

检查连接中的地址和网关：

```bash
nmcli -f ipv4.addresses,ipv4.gateway connection show course-static
```

### 16.3 网关能通，域名不能解析

检查连接保存的DNS：

```bash
nmcli -g ipv4.dns connection show course-static
```

检查当前生效的DNS：

```bash
nmcli -g IP4.DNS device show
```

### 16.4 名称解析到了错误地址

检查`/etc/hosts`：

```bash
grep -nE 'rocky-server|rocky-web|ubuntu-client' /etc/hosts
```

一个主机名不要保留多条相互冲突的地址记录。

### 16.5 重启后又使用DHCP

检查连接是否自动启动及其优先级：

```bash
nmcli -f connection.id,connection.autoconnect,connection.autoconnect-priority connection show course-static
```

不要急于删除DHCP连接。先确认静态连接参数正确，再调整自动连接策略。

## 十七、环境保留

本实验结果是后续Linux和虚拟化容器课程的共同基础：

- 保留两台Rocky的`course-static`。
- 保留Ubuntu静态网络配置。
- 保留三台机器的`/etc/hosts`。
- 保留三台机器的`~/m1-project/course-env.sh`。
- 保留原DHCP连接作为回退入口。

机房还原前，按课程统一要求保存三台虚拟机或创建课程检查点。恢复后必须先通过本实验的“任务十：验证持久化”，再进入实验9。
