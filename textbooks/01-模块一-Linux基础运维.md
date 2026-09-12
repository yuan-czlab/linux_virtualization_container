# 模块一：Linux基础运维

> 适用课程：《Linux操作系统》  
> 对应实验：实验1—实验7｜建议学时：20学时
> 主线环境：`rocky-server`、`rocky-web`｜Ubuntu 22.04 Desktop `ubuntu-client`

## 模块导读

Linux是服务器、云计算平台、网络设备、容器平台和自动化运维系统的重要基础。本模块从安装三机环境开始，逐步学习命令行、目录与文件、文本编辑、用户和权限、软件包、服务、日志以及系统资源检查。

完成本模块后，应能够：

1. 说明Linux内核、发行版和应用软件之间的关系。
2. 在VMware中安装`rocky-server`、`rocky-web`和Ubuntu 22.04 Desktop `ubuntu-client`，完成首次登录、基础网络验证和初始快照。
3. 使用命令行完成文件、目录、文本和归档管理。
4. 创建用户和用户组，正确配置文件权限和sudo授权。
5. 使用DNF和APT安装、查询、升级与卸载软件。
6. 使用systemd管理服务，并通过journal日志定位服务问题。
7. 检查CPU、负载、内存、磁盘、进程和监听端口。
8. 按“查看现状—修改配置—验证结果—查看日志—保留回退”的流程完成系统管理任务。

## 学习环境

| 项目 | 建议配置 |
|---|---|
| 宿主机 | Windows 10/11 64位 |
| 虚拟化软件 | VMware Workstation 17 |
| `rocky-server` | 2 vCPU、4GB内存、50GB磁盘、NAT；主机名和用户名均为`rocky-server` |
| `rocky-web` | 2 vCPU、2GB内存、40GB磁盘、NAT；主机名和用户名均为`rocky-web` |
| `ubuntu-client` | 2 vCPU、4GB内存、40GB磁盘、NAT；主机名和用户名均为`ubuntu-client` |
| 教学密码 | 三台机器统一为`123456`，仅用于隔离课堂环境 |
| 终端工具 | VMware控制台；后续可使用Windows Terminal、Xshell或MobaXterm |

实验2—13默认在`rocky-server`操作；实验14切换到`rocky-web`部署Nginx；实验15—19返回`rocky-server`；`ubuntu-client`全程作为浏览器、SSH、curl和数据库客户端。静态IP在实验8统一配置，实验1先让三台虚拟机通过DHCP联网并记录基线。

## 学习路线与成果

本教材保留12章完整知识结构，课堂按7个实验项目组织为20学时。教材用于讲解原理和补充练习，`labs/linux/`中的实验手册规定必做步骤、验证证据和成果提交要求。

| 实验 | 对应教材章节 | 项目重点 | 应形成的成果 |
|---|---|---|---|
| 实验1（4学时） | 第1—2章 | Linux起源、发行版、VMware和三机安装 | 可运行、可登录、可联网、可回退的三机环境 |
| 实验2（4学时） | 第3—5章相关内容 | 命令行、目录、文件、查看和基础重定向 | 规范的项目目录树和操作记录 |
| 实验3（2学时） | 第5—6章 | 查找、链接、Vim、归档和恢复 | 配置修改、归档及恢复验证 |
| 实验4（4学时） | 第7—9章 | 用户、组、共享权限、umask和最小sudo | 部门账号、共享目录和授权证据 |
| 实验5（2学时） | 第10章 | DNF、RPM、仓库和GPG | 软件安装、查询、卸载与回退记录 |
| 实验6（2学时） | 第11章 | systemd、journal和启动故障 | 状态—日志—根因—修复记录 |
| 实验7（2学时） | 第12章 | CPU、内存、进程、磁盘和容量 | 系统状态与容量巡检表 |

## 教材深度与课堂使用

本册详细解释Linux基础对象和命令，但课堂不逐页朗读。20学时建议分配为：教材讲授与任务导入175分钟、教师关键演示115分钟、学生独立操作455分钟、排障验收155分钟。实验1安装任务最紧，ISO、VMware安装包和校验值必须课前准备，两台Rocky与Ubuntu Desktop应错峰安装并交叉利用等待时间。

教材负责Linux历史、目录与权限模型、软件包、systemd和资源指标等机制；实验1—7负责把知识落实为三机环境、账号权限、服务故障和巡检成果。

## 贯穿项目：新业务服务器基础交付

本模块不是十二组互不相关的命令练习。你将以初级Linux运维工程师身份，完成一台新业务服务器的基础交付。

### 项目背景

星云科技准备上线一个内部应用。网络和应用服务将在后续模块部署，本模块先交付操作系统基础环境。交付结果必须让后续人员知道服务器如何安装、文件放在哪里、谁有权限、软件从哪里安装、服务是否正常以及出现问题时如何回退。

### 贯穿成果

```text
Rocky Linux基础环境（实验8再配置静态地址）
├── ~/m1-project              项目工作区和操作证据
├── /srv/course-share         运维团队共享目录
├── operator                  受限运维账号
├── ops-team                  项目协作组
├── 软件源与基础软件记录
├── systemd服务操作记录
├── systemd服务操作与日志证据
└── Linux基础环境巡检记录
```

各实验从相关章节选择必要原理和命令。Ubuntu安装属于实验1必做内容，固定IP属于实验8内容，综合交付脚本属于后续实验内容；必做范围以实验1—7手册为准。前文创建的虚拟机、目录、账号和配置会继续使用，不要提前删除。

---

# 第1章 Linux、操作系统与运维岗位

## 1.1 操作系统解决什么问题

一台计算机包含CPU、内存、磁盘、网卡等硬件。应用程序如果直接控制所有硬件，会面临三个问题：

- 每个程序都需要理解不同硬件的控制方式。
- 多个程序可能同时争抢CPU、内存和磁盘。
- 一个程序的错误可能破坏其他程序的数据。

操作系统位于硬件与应用之间，主要负责：

| 职责 | 示例 |
|---|---|
| 处理器管理 | 决定哪些进程获得CPU时间 |
| 内存管理 | 为进程分配、回收并隔离内存 |
| 文件系统 | 用目录和文件组织磁盘数据 |
| 设备管理 | 通过驱动程序管理磁盘、网卡等设备 |
| 用户与权限 | 判断谁可以访问哪些资源 |
| 网络通信 | 提供IP、TCP/UDP、Socket等能力 |
| 服务管理 | 启动、停止并监控后台服务 |

## 1.2 Linux内核与Linux发行版

Linux严格来说是一个操作系统内核。实际安装的Rocky Linux、Ubuntu Desktop并不只有内核，而是由以下部分组成：

```text
Linux发行版
├── Linux内核
├── GNU命令和基础工具
├── Shell
├── 软件包管理器和软件仓库
├── systemd等系统服务
├── 安装程序
└── 发行版维护的配置与安全更新
```

因此，“Linux发行版版本”和“Linux内核版本”不是同一个概念。

查看发行版：

```bash
cat /etc/os-release
```

查看内核：

```bash
uname -r
```

查看CPU架构：

```bash
uname -m
```

常见结果`x86_64`表示64位x86架构。ARM服务器上可能看到`aarch64`。

## 1.3 Rocky Linux与Ubuntu Desktop

| 对比项 | Rocky Linux 9 | Ubuntu 22.04 Desktop LTS |
|---|---|---|
| 发行版家族 | RHEL兼容 | Debian/Ubuntu |
| 软件包格式 | RPM | DEB |
| 高层包管理器 | DNF | APT |
| 底层包工具 | rpm | dpkg |
| 常见服务器场景 | 企业服务器、传统运维环境 | 云平台、开发和服务器环境 |
| 本课程定位 | 主线系统 | 对照系统 |

两者使用相同的Linux基本思想。`cd`、`cp`、`chmod`、`systemctl`等大量命令基本一致，主要差异集中在软件包、部分服务名称、默认配置和文件路径。

## 1.4 Linux系统的基本层次

```text
应用程序
   ↓
Shell / 系统服务 / 运行库
   ↓
系统调用接口
   ↓
Linux内核
   ↓
CPU / 内存 / 磁盘 / 网卡
```

Shell是接收命令并调用程序的命令解释器。Bash是常见Shell之一。Shell不是内核，终端也不是Shell：

- 终端负责输入和显示。
- Shell读取并解释命令。
- 命令程序完成具体工作。
- 内核负责访问硬件和管理资源。

## 1.5 Linux运维工作的基本方法

Linux管理不是“背命令”，而是围绕对象和证据工作：

```text
确认目标
→ 查看当前状态
→ 备份配置或创建快照
→ 修改最小必要内容
→ 检查语法或配置
→ 应用修改
→ 从使用者视角验证
→ 查看日志
→ 记录与复盘
```

## 1.6 云计算运维与网络工程岗位中的Linux

岗位工作通常不是完成一条孤立命令，而是交付一个可使用、可验证、可维护的系统结果：

| 工作对象 | 典型任务 | 可验收结果 |
|---|---|---|
| 操作系统 | 安装、初始化、软件源、时间和主机名 | 系统基线记录、可回退快照 |
| 身份与权限 | 创建账号、划分用户组、最小sudo授权 | 权限矩阵、授权文件、审计日志 |
| 服务 | 安装、配置、启停、自启和故障定位 | 服务状态、端口、功能测试、日志证据 |
| 网络与安全 | 地址、路由、DNS、远程连接和基础防护 | 连通性记录、访问控制与防火墙规则 |
| 自动化 | 批量检查和配置多台主机 | 可重复执行的脚本或自动化任务 |
| 虚拟化与容器 | 创建运行环境、发布应用、保存数据 | 可复现的虚拟机或容器化服务 |

本模块先建立单机Linux管理基础；后续模块继续学习网络与远程管理、基础防护、Nginx等企业服务、虚拟化、多机环境和Docker容器化。大二下册的云计算应用、网络安全基础和企业级综合实训会继续使用本课程形成的主机、网络、服务和排障记录。

### 本章任务：定义交付标准

此时Linux尚未安装，不执行Linux命令。先写出一台“可交付服务器”至少应回答的八个问题：当前用户是谁、主机名是什么、使用哪个发行版、内核版本是什么、CPU架构和核心数是多少、内存多大、磁盘如何组织、如何回退错误操作。第2章安装完成后将用真实命令填写这些信息。

### 本章检查

1. Linux内核与Rocky Linux发行版是什么关系？
2. Shell、终端和内核分别承担什么职责？
3. 为什么运维操作必须包含验证和回退？

---

# 第2章 VMware虚拟机与Linux安装

## 2.1 为什么使用虚拟机

虚拟机是在软件中模拟出的计算机。每台虚拟机拥有虚拟CPU、内存、磁盘和网卡，可以独立安装操作系统。

```text
Windows宿主机
└── VMware Workstation
    ├── rocky-server（基础运维、数据库与后续KVM）
    ├── rocky-web（Nginx与Web服务）
    └── ubuntu-client（Ubuntu 22.04 Desktop图形客户端）
```

虚拟机适合学习环境的原因：

- 实验与宿主机相互隔离。
- 可以创建快照并快速恢复。
- 可以克隆多台服务器。
- 可以模拟网络和服务器环境。

快照用于短期回退，不等于独立备份。删除或损坏原虚拟机文件后，依赖原磁盘链的快照也可能失效。

## 2.2 VMware三种常用网络模式

虚拟机网卡连接到VMware提供的虚拟交换网络。三种模式解决的问题不同：

| 模式 | VMware常用网络 | 虚拟机能访问宿主机 | 虚拟机能访问外部网络 | 局域网其他主机能否直接访问虚拟机 | 适用场景 |
|---|---|---:|---:|---:|---|
| 桥接 | VMnet0 | 能 | 能 | 通常能 | 虚拟机直接加入真实局域网 |
| NAT | VMnet8 | 能 | 能，由宿主机转换地址 | 默认不能主动进入 | 稳定的课程实验网络 |
| 仅主机 | VMnet1 | 能 | 默认不能 | 默认不能 | 完全隔离或只与宿主机通信 |

表中的“能”以地址、路由和防火墙允许为前提，不表示任何端口天然开放。

### 桥接模式

桥接后，虚拟机像一台真实电脑接入宿主机所在局域网，通常从校园网或路由器获得地址。它受真实网络的DHCP、认证、无线网卡限制和地址策略影响。同学连接不同网络时，地址可能变化，部分校园网还会限制新增终端，因此不作为本课程默认模式。

### NAT模式

NAT模式把虚拟机放入VMnet8私有网络。虚拟机之间可以通信，也可以经宿主机访问外部网络；外部局域网默认不能直接向虚拟机发起连接。实验1先使用DHCP确认环境可用，实验8再根据教师提供的实际网段配置固定地址。

### 仅主机模式

仅主机模式通常使用VMnet1。虚拟机可以与宿主机及同一VMnet1中的虚拟机通信，但默认没有通向外部网络的NAT网关，适合恶意代码分析或隔离网络实验。本课程后续虚拟化模块会再次比较这些模式。

## 2.3 识别VMnet8实验网络

VMnet8的实际网段可能因机房、安装时间和已有配置而不同，因此教材中的`192.168.200.0/24`只能作为后续章节的讲解示例，不能在实验1直接照抄。

```text
校园网或互联网
      │
Windows宿主机物理网卡
      │ NAT地址转换
VMware VMnet8（实际网段以本机为准）
├── 宿主机虚拟网卡
├── NAT网关
└── Rocky Linux DHCP地址
```

在VMware Workstation中打开“编辑 → 虚拟网络编辑器”，查看并记录VMnet8的子网、掩码、NAT网关和DHCP范围。实验1以查看为主，不随意修改公共机房的虚拟网络配置。Windows执行`ipconfig`，核对VMware Network Adapter VMnet8的实际地址。

到实验8时，教师统一公布网段、网关、DNS和每位学生的静态地址，学生再完成持久配置与回退验证。

> <img src="./images/桥接、NAT、仅主机模式关系图.png" width="600">

> **<img src="./images/VMware虚拟网络编辑器中的VMnet8实际参数.png" width="600">**

## 2.4 创建Rocky Linux虚拟机

推荐配置：

| 配置项 | 建议值 |
|---|---|
| 虚拟机名称 | 第一台`rocky-server`，第二台`rocky-web` |
| 客户机类型 | Linux / RHEL 9 64-bit |
| vCPU | 2 |
| 内存 | 2-4GB |
| 磁盘 | 40GB，单个虚拟磁盘文件 |
| 网络 | NAT，对应VMnet8 |
| ISO | Rocky Linux 9 Minimal ISO |

> <img src="./images/rocky-server虚拟机的硬件配置.png" width="600">

虚拟磁盘只是宿主机中的文件。安装程序中的分区操作只应作用于本实验虚拟磁盘，不会修改Windows真实磁盘，但仍须核对虚拟机名称、磁盘容量和安装目标。

## 2.5 安装两台Rocky Linux 9并完成初始联网

从ISO启动后完成以下配置：

1. 选择语言和键盘。
2. 选择40GB实验磁盘。推荐使用自动LVM并让根文件系统获得主要空间；若使用自定义分区，`/boot`约1GiB、swap约2GiB，其余主要分配给`/`，根文件系统不得小于30GiB。不要在小容量实验盘中把`/home`单独分走大量空间，因为后续Docker数据默认位于根文件系统下的`/var/lib/docker`。
3. 软件选择使用Minimal Install（最小化安装、无图形桌面）。
4. 打开“Network & Host Name”并启用网卡；第一台主机名设置为`rocky-server`，第二台设置为`rocky-web`。
5. 保持IPv4自动获取（DHCP），打开网卡并确认安装界面显示已连接。
6. 记录安装阶段获得的地址；此地址可能变化，不把它写成全班统一固定值。
7. 设置root密码。
8. 第一台创建普通用户`rocky-server`，第二台创建普通用户`rocky-web`；密码均为`123456`并授予管理员权限。
9. 开始安装，完成后重启并断开ISO。

> **[截图占位 M1-04：Rocky安装器中网卡已启用并通过DHCP获得地址]**

> **[截图占位 M1-05：两台Rocky安装摘要、角色主机名和同名管理员账号]**
第一次登录后检查：

```bash
cat /etc/rocky-release
hostnamectl
ip -br addr
ip route
cat /etc/resolv.conf
df -h
```

将结果填入服务器基线表：

| 项目 | 当前值 |
|---|---|
| 当前用户 | |
| 主机名 | |
| 发行版 | |
| 内核版本 | |
| CPU架构与核心数 | |
| 总内存 | |
| 根文件系统容量 | |
| 默认网关 | |

预期应同时看到Rocky获得一个与实际VMnet8相符的IPv4地址、存在默认路由并具有可用DNS。具体数值因宿主机环境而异。

安装器已经创建NetworkManager自动连接，不需要在实验1额外创建静态连接。查看实际网卡和连接名：

```bash
nmcli device status
nmcli connection show --active
ping -c 3 <实际NAT网关>
```

如果没有地址，先检查VMware虚拟网卡是否连接到NAT、安装器是否启用了网卡，再检查NetworkManager连接。静态IP、网关和DNS的修改方法在实验8集中学习，避免第一次课同时承担安装和网络规划两项高风险操作。

### 配置可用的软件源

机房不能稳定访问默认国外仓库，因此在安装其他工具前先切换到已验证的国内镜像。以下以阿里云Rocky镜像为例：

```bash
sudo cp -a /etc/yum.repos.d /root/yum.repos.d.after-install
sudo find /etc/yum.repos.d -maxdepth 1 -type f -iname 'rocky*.repo' \
  -exec sed -e 's|^mirrorlist=|#mirrorlist=|g' \
  -e 's|^#baseurl=http://dl.rockylinux.org/$contentdir|baseurl=https://mirrors.aliyun.com/rockylinux|g' \
  -i.bak '{}' +
sudo dnf clean all
sudo dnf makecache
dnf repolist
```

如果课程统一使用清华镜像，应使用开课前已经实机验证的Rocky 9仓库配置。不能使用CentOS 7、Rocky 8或其他大版本的repo文件。

安装VMware Tools：

```bash
sudo dnf install -y open-vm-tools openssh-server chrony
sudo systemctl enable --now vmtoolsd
sudo systemctl enable --now sshd
sudo systemctl enable --now chronyd
systemctl status vmtoolsd --no-pager
```

创建快照前关机：

```bash
sudo systemctl poweroff
```

快照分别命名为`00-rocky-server-安装与基础工具完成`和`00-rocky-web-安装与基础工具完成`。

快照完成后重新启动两台Rocky并核对身份，然后安装Ubuntu图形客户端。

## 2.6 安装Ubuntu 22.04 Desktop客户端

Ubuntu Desktop使用图形安装程序。核心步骤：

1. 使用`ubuntu-22.04.x-desktop-amd64.iso`启动。
2. 选择语言和键盘。
3. 网络暂时保持安装程序自动获取地址（DHCP），确认网卡能够取得与VMnet8实际网段一致的IPv4地址。不要在实验1照抄固定地址；Ubuntu Desktop的NetworkManager静态连接在实验8统一完成。
4. 使用整个40GB虚拟磁盘完成正常的Ubuntu Desktop安装。
5. 计算机名、主机名和用户名均设置为`ubuntu-client`，密码为`123456`，不启用自动登录。
6. 完成安装并重启，进入图形桌面后打开Terminal。
7. 使用APT安装`open-vm-tools-desktop`、OpenSSH和curl等客户端工具。

> **[截图占位 M1-06：Ubuntu Desktop图形桌面、Terminal、DHCP地址和主机名]**

登录后执行：

```bash
sudo apt update
sudo apt install -y open-vm-tools open-vm-tools-desktop openssh-server curl
sudo systemctl enable --now ssh
cat /etc/os-release
ip -br addr
ip route
```

Ubuntu 22.04 Desktop的软件源通常配置在`/etc/apt/sources.list`。不要直接复制其他发行版或其他Ubuntu版本的软件源配置。

## 2.7 三机基础连通性验证

分别用`ip -br addr`记录三台机器的DHCP地址，下面用`<ROCKY_SERVER_IP>`、`<ROCKY_WEB_IP>`、`<UBUNTU_CLIENT_IP>`和`<VMNET8_GATEWAY>`表示。必须替换占位符。

两台Rocky分别测试网关；`ubuntu-client`测试两台服务器：

```bash
ping -c 3 <VMNET8_GATEWAY>
ping -c 3 <VMNET8_GATEWAY>
ping -c 3 <ROCKY_SERVER_IP>
ping -c 3 <ROCKY_WEB_IP>
```

Windows宿主机执行：

```powershell
ping <ROCKY_SERVER_IP>
ping <ROCKY_WEB_IP>
ping <UBUNTU_CLIENT_IP>
```

验证顺序是“本机地址→NAT网关→同一VMnet8中的其他虚拟机”，不要一开始只测试互联网地址。实验8会为三台虚拟机配置稳定静态地址和hosts解析。

## 2.8 安装故障排查

| 现象 | 检查方向 |
|---|---|
| 虚拟机无法启动64位系统 | BIOS/UEFI是否开启VT-x/AMD-V |
| 启动后找不到安装程序 | ISO是否正确挂载、启动顺序是否正确 |
| 重启后再次进入安装界面 | ISO未断开或光驱优先启动 |
| 安装时没有网络 | VMware网卡是否Connected、是否连接VMnet8 |
| 系统启动后无IP | 安装器静态配置、`ip link`、`nmcli device` |
| 能ping自己但不能ping网关 | VMnet8子网、网关、掩码或虚拟网卡连接错误 |
| 任意两台虚拟机地址相同 | 立即关闭冲突机器并在实验8统一修正 |
| 系统时间错误 | 时区、宿主机时间、时间同步服务 |

### 实践验收

- [ ] Rocky Linux 9可以使用普通用户登录。
- [ ] `rocky-server`和`rocky-web`分别能使用同名普通用户登录并使用sudo。
- [ ] 已记录VMnet8的实际子网、网关和DHCP范围，没有照抄示例地址。
- [ ] Rocky通过DHCP获得IPv4地址，默认路由和名称解析可用。
- [ ] `open-vm-tools`处于active状态。
- [ ] 已创建干净快照。

- [ ] Ubuntu 22.04 Desktop客户端能够使用`ubuntu-client`登录、打开Terminal并使用sudo。
- [ ] `ubuntu-client`通过DHCP联网，已创建安装完成快照。
- [ ] 三台虚拟机地址不重复，能够访问NAT网关；三机固定地址和互通在实验8完成。

---

# 第3章 命令行基础与双发行版对照

## 3.1 理解Shell提示符

常见提示符：

```text
[rocky-server@rocky-server ~]$
[root@rocky-server ~]#
```

- 第一个`rocky-server`是当前用户。
- 第二个`rocky-server`是主机名。
- `~`代表当前用户家目录。
- `$`通常表示普通用户。
- `#`通常表示root用户。

不要把教材代码块前的说明文字复制到终端。命令中的`$`和`#`如果只是提示符，也不属于命令本身。

## 3.2 命令的基本格式

```text
命令 [选项] [参数对象]
```

例如：

```bash
ls -l /etc
```

- 命令：`ls`
- 选项：`-l`
- 参数：`/etc`

Linux命令和文件名通常区分大小写。`File.txt`与`file.txt`是两个不同名称。

## 3.3 获取帮助

```text
command --help
man command
type command
which command
```

这里的`command`表示需要查询的真实命令名，不是要求输入的固定单词。下面使用`ls`、`cd`等真实对象练习。

示例：

```bash
ls --help | less
man ls
type cd
type ls
which ls
```

`cd`通常是Shell内建命令，因此`which cd`可能找不到；`type cd`能说明它是Shell builtin。

Minimal安装若没有`man`：

```bash
sudo dnf install -y man-db man-pages
```

## 3.4 常用入门命令

```bash
pwd                  # 当前目录
ls                   # 列出目录内容
ls -lah              # 长格式、含隐藏文件、易读大小
cd /etc              # 进入目录
cd ..                # 返回上一级
cd ~                 # 回到家目录
clear                # 清屏
whoami               # 当前用户名
hostname             # 主机名
date                  # 日期时间
```

## 3.5 历史、补全和快捷键

| 操作 | 功能 |
|---|---|
| `history` | 查看命令历史 |
| `!!` | 再次执行上一条命令，使用前先确认 |
| `Ctrl+R` | 反向搜索历史 |
| `Tab` | 补全命令或路径 |
| `Ctrl+C` | 中断当前前台命令 |
| `Ctrl+L` | 清屏 |
| `Ctrl+A` / `Ctrl+E` | 移到行首/行尾 |

历史命令可能包含密码或敏感参数，不应把密码直接写在命令行中。

## 3.6 引号与Shell展开

```bash
name=Rocky
echo "$name Linux"       # 双引号：变量会展开
echo '$name Linux'       # 单引号：原样输出
echo file{1..3}.txt      # 花括号展开
echo *.txt               # 通配符展开
```

包含空格的路径需要引用：

```bash
mkdir -p "$HOME/My Project"
cd "$HOME/My Project"
pwd
cd ~
```

## 3.7 退出状态

程序结束时会返回退出状态。通常0表示成功，非0表示失败：

```bash
ls /etc/passwd
echo $?

ls /path/not-exist
echo $?
```

“没有输出”不等于成功，“有输出”也不等于失败。脚本和自动化工具主要依赖退出状态判断结果。

## 3.8 Rocky与Ubuntu常见命令对照

| 任务 | Rocky Linux 9 | Ubuntu 22.04 Desktop |
|---|---|---|
| 更新软件索引 | `dnf makecache` | `apt update` |
| 安装软件 | `dnf install 包名` | `apt install 包名` |
| 查询软件 | `dnf search 关键词` | `apt search 关键词` |
| 查询已安装包 | `rpm -q 包名` | `dpkg -l 包名` |
| 防火墙 | firewalld | ufw常见，也可使用nftables |
| 网络管理 | NetworkManager/nmcli | netplan/systemd-networkd常见 |

### 实践任务

1. 分别在Rocky和Ubuntu中查看`/etc/os-release`。
2. 使用`type`判断`cd`、`ls`、`echo`是什么类型的命令。
3. 使用`man`找到`ls`按修改时间排序的选项。
4. 执行成功和失败命令，记录退出状态。
5. 使用Tab补全进入`/etc/systemd/system`。

### 验收标准

- [ ] 能解释命令、选项和参数。
- [ ] 会使用`--help`、`man`、`type`和历史搜索。
- [ ] 能正确解释`$?`。
- [ ] 能说出DNF与APT的基本对应关系。

---

# 第4章 Linux目录结构与文件管理

## 4.1 单根目录树

Windows常用`C:\`、`D:\`区分不同驱动器。Linux从一个根目录`/`开始组织所有文件系统：

```text
/
├── bin -> usr/bin
├── sbin -> usr/sbin
├── lib -> usr/lib
├── lib64 -> usr/lib64
├── boot
├── dev
├── etc
├── home
├── media
├── mnt
├── opt
├── proc
├── root
├── run
├── srv
├── sys
├── tmp
├── usr
└── var
```

| 目录 | 主要用途 |
|---|---|
| `/bin` | 基本用户命令；现代Rocky和Ubuntu通常链接到`/usr/bin` |
| `/sbin` | 系统管理命令；现代系统通常链接到`/usr/sbin` |
| `/lib`、`/lib64` | 基础共享库和动态链接器；通常链接到`/usr/lib*` |
| `/etc` | 系统和服务配置 |
| `/home` | 普通用户家目录 |
| `/root` | root用户家目录 |
| `/usr` | 用户空间程序、库、文档和共享只读数据 |
| `/usr/bin` | 大量普通命令，如`ls`、`cp` |
| `/usr/sbin` | 大量系统管理命令 |
| `/usr/local` | 本机自行安装的软件和脚本，避免被发行版包覆盖 |
| `/var` | 日志、缓存、数据库等变化数据 |
| `/var/log` | 系统与服务日志 |
| `/tmp` | 临时文件，可能被定期清理 |
| `/boot` | 引导加载器、内核和启动文件 |
| `/dev` | 设备文件 |
| `/proc` | 进程和内核运行信息的虚拟视图 |
| `/sys` | 设备和内核对象的虚拟视图 |
| `/run` | 本次启动期间的运行时数据 |
| `/opt` | 可选的第三方应用 |
| `/srv` | 服务对外提供的数据 |
| `/mnt` | 管理员临时挂载文件系统 |
| `/media` | U盘、光盘等可移动介质的挂载位置 |

### 为什么/bin会指向/usr/bin

早期Unix和Linux把系统启动所需的基本命令放在`/bin`，把其他命令放在`/usr/bin`。现代发行版普遍采用usr-merge，把程序和库集中到`/usr`，同时保留旧路径作为符号链接，兼容仍然使用`/bin/ls`等路径的脚本。

在Rocky和Ubuntu分别验证：

```bash
ls -ld /bin /sbin /lib /lib64 2>/dev/null
readlink -f /bin
readlink -f /sbin
readlink -f /bin/ls
command -v ls
```

因此`/bin`并没有消失。输入`/bin/ls`时，系统最终通常执行`/usr/bin/ls`。不同CPU架构的库目录名称可能不同，不能假设所有系统都一定存在`/lib64`。

### 磁盘目录和虚拟目录

`/etc`、`/home`和`/var`等内容通常保存在磁盘文件系统中；`/proc`和`/sys`主要由内核动态提供，不是普通磁盘数据。`/dev`中的设备文件也不是设备内容本身，而是访问设备的接口。

不要把所有个人文件都放到`/root`或`/tmp`。配置、程序、数据和日志应放在职责明确的位置。

## 4.2 绝对路径与相对路径

- 绝对路径从`/`开始，例如`/etc/ssh/sshd_config`。
- 相对路径从当前目录开始，例如`docs/report.md`。

特殊路径：

| 表示 | 含义 |
|---|---|
| `.` | 当前目录 |
| `..` | 上一级目录 |
| `~` | 当前用户家目录 |
| `-` | `cd`中代表上一次目录 |

```bash
pwd
cd /var/log
cd ..
cd ~
cd -
```

## 4.3 创建文件和目录

本章开始建立贯穿项目。业务部门交来了一组待整理文件，要求运维人员建立工作区、保留原始文件并形成清晰的交付目录。

| 目录 | 用途 |
|---|---|
| `incoming` | 接收的原始文件，只做必要清理 |
| `config` | 当前使用的配置文件 |
| `data` | 项目数据和清单 |
| `logs` | 操作或应用日志 |
| `scripts` | 运维脚本 |
| `backup` | 初始配置和归档 |
| `docs` | 说明、证据和交付文档 |

先创建目录：

```bash
mkdir -p ~/m1-project/{incoming,config,data,logs,scripts,backup,docs}
touch ~/m1-project/docs/directory-plan.md
```

`mkdir -p`可以创建多级目录，已存在时不会因目录本身已经存在而报错。花括号会被Shell展开成多个路径。`touch`可以创建空文件，也可以更新已有文件的时间戳。

现在模拟业务部门交来的原始文件。后续复制、移动和删除都以这些真实文件为对象：

```bash
cat > ~/m1-project/README.md <<'EOF'
# 新业务服务器基础交付

- 服务器：rocky-server
- 负责人：rocky-server
- 状态：初始化中
EOF

cat > ~/m1-project/incoming/app.conf.sample <<'EOF'
app_name=internal-demo
listen_port=8080
data_dir=/srv/internal-demo/data
log_level=info
EOF

cat > ~/m1-project/incoming/server-list.csv <<'EOF'
hostname,role,ip
rocky-server,data-and-ops,<ROCKY_SERVER_IP>
rocky-web,web,<ROCKY_WEB_IP>
ubuntu-client,client,<UBUNTU_CLIENT_IP>
EOF

printf '该文件为过期临时说明，确认后删除。\n' \
  > ~/m1-project/incoming/obsolete-note.tmp

cat > ~/m1-project/logs/app.log <<'EOF'
2026-07-05 09:00:01 INFO service preparation started
2026-07-05 09:00:03 WARN configuration not deployed
2026-07-05 09:00:05 ERROR sample connection failed
2026-07-05 09:00:08 INFO waiting for operator
EOF

cat > ~/m1-project/scripts/precheck.sh <<'EOF'
#!/bin/bash
echo "host=$(hostname) time=$(date -Iseconds)"
EOF
chmod 750 ~/m1-project/scripts/precheck.sh
```

检查所有输入对象已经存在：

```bash
find ~/m1-project -maxdepth 2 -printf '%y %p\n' | sort
```

其中`d`表示目录、`f`表示普通文件。只有这一步结果完整，才继续4.4节。

## 4.4 复制、移动和删除

```text
cp 源路径 目标路径
mv 源路径 目标路径
rm 文件路径
```

上面三行是命令格式，中文占位符不是要直接执行的文件名。`cp`保留源对象，`mv`移动或重命名后原路径消失，`rm`删除对象且不经过通用回收站。

重要选项：

| 命令 | 选项 | 作用 |
|---|---|---|
| `cp` | `-a` | 尽量保留属性并递归复制 |
| `cp` | `-i` | 覆盖前询问 |
| `mv` | `-i` | 覆盖前询问 |
| `rm` | `-i` | 删除前询问 |
| `rm` | `-r` | 递归删除目录 |

`rm`没有通用回收站。执行递归删除前应完成三项检查：

```text
pwd
ls -ld 待删除路径
find 待删除路径 -maxdepth 2 -print
```

“待删除路径”是占位说明，必须替换为经过确认的真实路径。

不要在不理解路径展开结果时使用`rm -rf`。

### 项目任务：整理业务部门交付文件

业务要求如下：

1. 原始配置样例必须保留在`incoming`。
2. 将配置样例复制为正式文件`config/app.conf`。
3. 在修改正式配置前，将其初始版本备份为`backup/app.conf.initial`。
4. 服务器清单属于交付文档，应移动到`docs/server-list.csv`。
5. 查看`obsolete-note.tmp`内容，确认确实过期后再删除。
6. 操作完成后，不能出现误删除的目录或额外副本。

先根据需求判断每一步使用`cp`、`mv`还是`rm`。完成后再展开参考实现核对。

<details>
<summary>参考实现：完成任务后展开</summary>

```bash
cp -a ~/m1-project/incoming/app.conf.sample \
  ~/m1-project/config/app.conf

cp -a ~/m1-project/config/app.conf \
  ~/m1-project/backup/app.conf.initial

mv ~/m1-project/incoming/server-list.csv \
  ~/m1-project/docs/server-list.csv

cat ~/m1-project/incoming/obsolete-note.tmp
rm -i ~/m1-project/incoming/obsolete-note.tmp
```

</details>

逐项验证：

```bash
test -f ~/m1-project/incoming/app.conf.sample && echo 'OK original sample'
test -f ~/m1-project/config/app.conf && echo 'OK active config'
test -f ~/m1-project/backup/app.conf.initial && echo 'OK initial backup'
test -f ~/m1-project/docs/server-list.csv && echo 'OK server list'
test ! -e ~/m1-project/incoming/obsolete-note.tmp && echo 'OK obsolete file removed'
```

## 4.5 隐藏文件和通配符

以`.`开头的名称通常不会被普通`ls`显示：

```bash
printf 'project_id=M1-BASELINE\n' > ~/m1-project/.project-meta
ls -la ~/m1-project
```

常用通配符：

| 通配符 | 含义 | 示例 |
|---|---|---|
| `*` | 任意长度字符 | `*.log` |
| `?` | 任意一个字符 | `file?.txt` |
| `[abc]` | 指定集合中的一个字符 | `file[123].txt` |
| `[0-9]` | 指定范围中的一个字符 | `log[0-9]` |

通配符由Shell展开后再交给命令。先用`printf '%s\n' pattern`或`ls`确认匹配结果，再执行批量复制或删除。

在项目中创建三份文件，只复制扩展名为`.log`的日志：

```bash
printf 'INFO day1\n' > ~/m1-project/logs/app-1.log
printf 'INFO day2\n' > ~/m1-project/logs/app-2.log
printf 'not a log file\n' > ~/m1-project/logs/readme.txt
mkdir -p ~/m1-project/backup/logs

printf '%s\n' ~/m1-project/logs/*.log
cp -a ~/m1-project/logs/*.log ~/m1-project/backup/logs/
find ~/m1-project/backup/logs -maxdepth 1 -type f -print
```

`readme.txt`不匹配`*.log`，因此不会被复制。

## 4.6 文件类型

```bash
ls -l ~/m1-project/config/app.conf
file /bin/ls
file ~/m1-project/config/app.conf
file ~/m1-project/scripts/precheck.sh
stat /etc/passwd
stat ~/m1-project/config/app.conf
```

`ls -l`首字符常见含义：

| 字符 | 类型 |
|---|---|
| `-` | 普通文件 |
| `d` | 目录 |
| `l` | 符号链接 |
| `c` | 字符设备 |
| `b` | 块设备 |
| `s` | Socket |
| `p` | 命名管道 |

### 本章项目验收

最终目录至少应包含：

```text
m1-project
├── .project-meta
├── README.md
├── backup/app.conf.initial
├── backup/logs/
├── config/app.conf
├── docs/directory-plan.md
├── docs/server-list.csv
├── incoming/app.conf.sample
├── logs/app.log
├── logs/app-1.log
├── logs/app-2.log
├── logs/readme.txt
└── scripts/precheck.sh
```

执行验收：

```bash
find ~/m1-project -maxdepth 3 -printf '%M %u:%g %p\n' | sort
~/m1-project/scripts/precheck.sh
```

`docs/directory-plan.md`已经作为待编写交付文档创建。第6章学习vim后，用自己的语言补充各目录用途，并解释为什么原始配置、正式配置和备份配置不能只保留一份。

---

# 第5章 文件查看、查找与链接

## 5.1 查看文本文件

```bash
cat /etc/os-release
cat ~/m1-project/logs/app.log
less ~/m1-project/logs/app.log
head -n 20 /etc/passwd
tail -n 3 ~/m1-project/logs/app.log
tail -f ~/m1-project/logs/app.log
```

`tail -f`会持续等待新内容，按`Ctrl+C`结束。Rocky系统若存在`/var/log/messages`，通常需要使用`sudo less /var/log/messages`或`sudo tail /var/log/messages`读取；部分最小化环境主要使用systemd journal，第11章将专门练习。

适用场景：

| 命令 | 适合场景 |
|---|---|
| `cat` | 较短文件一次输出 |
| `less` | 分页查看较长文件，可搜索 |
| `head` | 查看开头 |
| `tail` | 查看结尾或跟踪日志 |

在`less`中：

- `/error`搜索error。
- `n`跳到下一个结果。
- `g`到开头，`G`到结尾。
- `q`退出。

## 5.2 筛选、统计与排序

`grep`按内容筛选行，`wc`统计数量，`sort`排序，`uniq`处理相邻重复行，`cut`按字段提取内容：

```bash
grep 'bash$' /etc/passwd
grep -n -i 'error' ~/m1-project/logs/app.log
wc -l /etc/passwd
cut -d: -f7 /etc/passwd
cut -d: -f7 /etc/passwd | sort | uniq -c | sort -nr
```

| 命令或选项 | 含义 |
|---|---|
| `grep PATTERN FILE` | 输出匹配模式的行 |
| `grep -n` | 显示行号 |
| `grep -i` | 忽略大小写 |
| `grep -v` | 输出不匹配的行 |
| `wc -l` | 统计行数 |
| `sort` | 按行排序，使相同内容相邻 |
| `uniq -c` | 对相邻重复行计数，通常先配合`sort` |
| `sort -nr` | 按数字倒序排列 |
| `cut -d: -f7` | 以冒号分隔并提取第7字段 |

正则表达式中的`$`表示行尾，因此`grep 'bash$' /etc/passwd`匹配以`bash`结尾的账号记录。模式应使用单引号，避免Shell提前解释特殊字符。

## 5.3 使用find查找

```bash
find /etc -name '*.conf'
find /var/log -type f
find /var -type f -size +100M 2>/dev/null
find /tmp -type f -mtime -1
find ~/m1-project -maxdepth 2 -print
```

常用条件：

| 条件 | 含义 |
|---|---|
| `-name` | 按名称，区分大小写 |
| `-iname` | 按名称，不区分大小写 |
| `-type f/d/l` | 文件/目录/链接 |
| `-size +100M` | 大于100MiB |
| `-mtime -1` | 24小时内修改 |
| `-user USER` | 指定所有者 |
| `-maxdepth N` | 限制递归深度 |

对查找结果执行操作前先打印确认。相比拼接字符串，`-exec`能够更安全地处理空格：

```bash
find ~/m1-project -type f -name '*.log' -exec ls -lh {} \;
```

## 5.4 查找命令位置

```bash
type ls
command -v ls
which ls
whereis ls
```

- `type`能识别别名、函数、内建命令和外部命令。
- `command -v`适合脚本检查命令是否存在。
- `whereis`可能同时显示程序、源码和手册位置。

## 5.5 inode与链接

文件名是目录中的记录，inode保存文件类型、权限、所有者、时间和数据块位置等元数据。

```bash
mkdir -p ~/m1-project/data/link-lab
echo 'important project data' > ~/m1-project/data/link-lab/origin.txt
ls -li ~/m1-project/data/link-lab/origin.txt

ln ~/m1-project/data/link-lab/origin.txt \
  ~/m1-project/data/link-lab/hard-link.txt
ln -s origin.txt ~/m1-project/data/link-lab/soft-link.txt
ls -li ~/m1-project/data/link-lab/*.txt
```

| 特性 | 硬链接 | 符号链接 |
|---|---|---|
| inode | 与原文件相同 | 拥有自己的inode |
| 跨文件系统 | 通常不可以 | 可以 |
| 链接目录 | 通常禁止 | 可以 |
| 删除原文件后 | 数据仍可访问 | 链接失效 |
| 保存内容 | 指向同一inode | 保存目标路径 |

验证：

```bash
rm ~/m1-project/data/link-lab/origin.txt
cat ~/m1-project/data/link-lab/hard-link.txt
cat ~/m1-project/data/link-lab/soft-link.txt
```

符号链接适合把稳定路径指向不同版本，例如`current -> releases/v2`。硬链接不能替代备份，因为对同一inode的内容修改会同时体现。

## 5.6 管道与重定向入门

```bash
ps aux | less
find /var/log -type f | wc -l
ls -lah ~/m1-project > ~/m1-project/docs/files.txt
date >> ~/m1-project/docs/files.txt
ls /not-exist 2> ~/m1-project/logs/command-error.log
```

| 符号 | 含义 |
|---|---|
| `|` | 把前一命令标准输出交给后一命令 |
| `>` | 覆盖写入文件 |
| `>>` | 追加写入文件 |
| `2>` | 重定向标准错误 |

### 实践任务

项目经理要求提交一次文件审计：

1. 找出`/etc`下前20个`.conf`文件。
2. 找出`/var`下大于10MiB的文件，不显示权限错误。
3. 从项目日志中提取包含`WARN`或`ERROR`的行。
4. 解释删除源文件后硬链接仍可读、软链接失效的原因。
5. 将以上查找命令和结果整理到`~/m1-project/docs/find-result.txt`。

验收：

```bash
test -s ~/m1-project/docs/find-result.txt
grep -E 'WARN|ERROR' ~/m1-project/logs/app.log
ls -l ~/m1-project/data/link-lab
```

---

# 第6章 vim与归档恢复

## 6.1 为什么需要文本编辑器

Linux服务器的大量配置使用文本文件。图形界面不可用时，终端文本编辑器是必要工具。

先确认完整的vim命令可用。Rocky Linux最小化安装通常需要安装`vim-enhanced`，Ubuntu使用`vim`包：

Rocky执行：

```bash
command -v vim || sudo dnf install -y vim-enhanced
vim --version | head
```

Ubuntu对照执行：

```bash
command -v vim || sudo apt install -y vim
vim --version | head
```

第2章已经完成国内镜像配置。如果此处仓库不可达，应先排查第2章的IP、网关、DNS和仓库配置，不要跳过错误或从未知网站下载安装脚本。

vim具有模式概念：

```text
普通模式 ←Esc→ 插入模式
   │
   └─ : → 命令行模式
```

## 6.2 vim基本操作

打开文件：

```bash
vim ~/m1-project/README.md
```

普通模式常用操作：

| 按键 | 功能 |
|---|---|
| `h j k l` | 左下上右移动 |
| `w` / `b` | 下一个/上一个单词 |
| `0` / `$` | 行首/行尾 |
| `gg` / `G` | 文件开头/结尾 |
| `dd` | 删除当前行 |
| `yy` | 复制当前行 |
| `p` | 粘贴 |
| `u` | 撤销 |
| `Ctrl+R` | 重做 |

进入插入模式：

| 按键 | 功能 |
|---|---|
| `i` | 光标前插入 |
| `a` | 光标后插入 |
| `o` | 下一行新建并插入 |

保存与退出：

| 命令 | 功能 |
|---|---|
| `:w` | 保存 |
| `:q` | 退出 |
| `:wq` | 保存并退出 |
| `:q!` | 放弃未保存修改 |

搜索替换：

```vim
/keyword
n
:%s/old/new/g
```

编辑配置文件前先备份。项目配置使用时间戳保留修改前版本：

```bash
cp -a ~/m1-project/config/app.conf \
  ~/m1-project/backup/app.conf.before-vim.$(date +%F-%H%M%S)
vim ~/m1-project/config/app.conf
```

## 6.3 归档与压缩

归档是把多个文件组合成一个文件，压缩是减少数据体积。`tar`常把两者结合：

```bash
archive="$HOME/m1-project-$(date +%F-%H%M%S).tar.gz"
restore_dir=$(mktemp -d "$HOME/m1-restore.XXXXXX")
printf '%s\n' "$archive" > ~/m1-project/docs/last-archive.txt
printf '%s\n' "$restore_dir" > ~/m1-project/docs/last-restore-dir.txt
tar -C "$HOME" -czf "$archive" m1-project
echo "$archive"
```

常用参数：

| 参数 | 含义 |
|---|---|
| `-c` | 创建归档 |
| `-x` | 解开归档 |
| `-t` | 列出归档内容 |
| `-z` | 使用gzip |
| `-f` | 后面指定归档文件名 |
| `-v` | 显示处理过程，可选 |
| `-C` | 切换到目标目录再操作 |

先检查再恢复：

```bash
archive=$(cat ~/m1-project/docs/last-archive.txt)
restore_dir=$(cat ~/m1-project/docs/last-restore-dir.txt)
tar -tzf "$archive" | head
tar -xzf "$archive" -C "$restore_dir"
find "$restore_dir" -maxdepth 3 -print
```

不要盲目以root身份解开来源不明的归档文件。归档中可能包含绝对路径、特殊权限或覆盖目标文件的内容。

## 6.4 zip与unzip

```bash
sudo dnf install -y zip unzip
(cd "$HOME" && zip -r "$HOME/m1-project.zip" m1-project)
unzip -l "$HOME/m1-project.zip"
zip_restore=$(mktemp -d "$HOME/m1-zip-restore.XXXXXX")
unzip "$HOME/m1-project.zip" -d "$zip_restore"
echo "$zip_restore"
```

## 6.5 备份必须验证恢复

备份文件存在不等于可恢复。最小验证流程：

```text
创建备份
→ 检查文件非空
→ 列出归档内容
→ 恢复到新目录
→ 对比关键文件
→ 记录恢复时间和问题
```

```bash
restore_dir=$(cat ~/m1-project/docs/last-restore-dir.txt)
diff -ru "$HOME/m1-project" "$restore_dir/m1-project"
```

归档路径和恢复目录分别记录在项目`docs`中，因此重新登录后也可以继续验证。示例使用`tar -C "$HOME"`归档相对路径，恢复结果不依赖具体用户名。

### 实践任务

项目工单要求：

1. 使用vim把`README.md`中的状态改为“基础文件已整理”。
2. 使用vim完成`docs/directory-plan.md`。
3. 创建`docs/initialization-record.md`，至少记录固定IP、网关、DNS、目录规划和当前日期。
4. 使用搜索与替换确认文档中的主机名统一为`rocky-server`。
5. 将`~/m1-project`归档并记录归档路径。
6. 恢复到新目录，使用`diff -ru`验证。

`diff`无输出且退出状态为0，表示当前项目内容与恢复内容一致。

---

# 第7章 用户与用户组

## 7.1 Linux身份模型

Linux内核主要使用数字ID判断身份：

- UID：用户ID。
- GID：组ID。
- 主组：用户创建文件时默认使用的组。
- 附加组：用户额外加入的组。

```bash
id
id rocky-server
groups rocky-server
```

root用户的UID为0，拥有极高权限。管理员日常操作应使用普通账号，需要时通过sudo临时提权。

## 7.2 账号相关文件

### `/etc/passwd`

示例结构：

```text
rocky-server:x:1000:1000:Rocky Server:/home/rocky-server:/bin/bash
```

字段依次表示：用户名、密码占位、UID、主GID、说明、家目录、登录Shell。

### `/etc/shadow`

保存密码哈希和密码有效期，只允许特权用户读取。不要直接手工修改，优先使用`passwd`和`chage`。

### `/etc/group`

保存组名、GID和附加成员。

使用系统接口查询比直接grep更稳妥：

```bash
getent passwd rocky-server
getent group wheel
```

## 7.3 用户管理

```bash
sudo useradd -m -s /bin/bash demo-user
sudo passwd demo-user
sudo usermod -c "Demo Operator" demo-user
sudo usermod -L demo-user       # 锁定密码
sudo usermod -U demo-user       # 解锁密码
id demo-user
```

删除账号前检查其文件和运行进程：

```bash
ps -u demo-user
sudo find / -xdev -user demo-user 2>/dev/null
```

`userdel -r`会尝试删除家目录和邮件目录，执行前必须确认数据已备份或允许删除。

## 7.4 用户组管理

```bash
sudo groupadd web-team
sudo usermod -aG web-team demo-user
id demo-user
getent group web-team
```

`usermod -aG`中的`-a`表示追加。如果只使用`-G`，可能覆盖用户原有附加组。

用户加入新组后，已有登录会话可能仍保留旧组列表。目标用户应重新登录。在测试环境中，目标用户也可执行`newgrp web-team`启动一个采用新组身份的子Shell，完成验证后执行`exit`返回原Shell。

## 7.5 密码有效期

```bash
sudo chage -l demo-user
sudo chage -M 90 -m 1 -W 7 demo-user
sudo chage -d 0 demo-user
```

- `-M 90`：最长90天。
- `-m 1`：最短1天后才能再次修改。
- `-W 7`：到期前7天警告。
- `-d 0`：下次登录要求修改密码。

课程实验密码不能用于真实生产系统。真实密码应足够长、唯一，并按组织策略管理。

检查无误后清理演示账号和演示组：

```bash
ps -u demo-user
sudo find / -xdev -user demo-user 2>/dev/null
sudo userdel -r demo-user
sudo groupdel web-team
```

### 项目工单：建立运维协作团队

项目需要两种角色：

| 账号 | 职责 | 组要求 |
|---|---|---|
| `operator` | 执行日常服务检查和受控运维操作 | 加入`ops-team` |
| `appdev` | 提交应用文件，但没有系统管理权限 | 加入`ops-team` |

约束：练习账号必须相互独立，不能共享课程主账号或root密码；创建后必须通过`id`和`getent`验证。

<details>
<summary>参考实现：完成工单后展开</summary>

```bash
sudo groupadd ops-team
sudo useradd -m -s /bin/bash operator
sudo useradd -m -s /bin/bash appdev
sudo passwd operator
sudo passwd appdev
sudo usermod -aG ops-team operator
sudo usermod -aG ops-team appdev
id operator
id appdev
getent group ops-team
```

</details>

这些账号、家目录和`ops-team`将在第8、9章以及模块综合交付中继续使用，不要在本章删除。

---

# 第8章 文件权限与共享目录

## 8.1 rwx权限模型

项目要求在`/srv/course-share`建立协作目录。`operator`和`appdev`都能创建文件，新文件应自动属于`ops-team`，但任何人都不能随意删除其他成员的文件。

先建立SGID共享目录并创建一份真实报告：

```bash
sudo mkdir -p /srv/course-share
sudo chown root:ops-team /srv/course-share
sudo chmod 2770 /srv/course-share
sudo -u operator bash -c \
  'echo "operator baseline report" > /srv/course-share/operator-report.txt'
ls -ld /srv/course-share
ls -l /srv/course-share/operator-report.txt
```

```bash
ls -l /srv/course-share/operator-report.txt
```

示例：

```text
-rw-r--r-- 1 operator ops-team 25 Jul 5 10:00 operator-report.txt
```

拆分：

```text
-  rw-  r--  r--
│   │    │    └─ 其他用户
│   │    └────── 所属组
│   └─────────── 所有者
└─────────────── 文件类型
```

## 8.2 文件和目录上的rwx不同

| 权限 | 普通文件 | 目录 |
|---|---|---|
| `r` | 读取文件内容 | 列出目录项名称 |
| `w` | 修改文件内容 | 创建、删除、重命名目录项 |
| `x` | 作为程序执行 | 进入目录并访问其中对象 |

目录有`r`但无`x`时，可能看到名称却无法访问属性或内容；有`x`但无`r`时，知道准确名称可能访问对象，但不能正常列出目录。

## 8.3 chmod数字法

```text
r = 4
w = 2
x = 1
```

```bash
mkdir -p ~/m1-project/permissions/public-dir
touch ~/m1-project/permissions/private.txt
cp ~/m1-project/config/app.conf ~/m1-project/permissions/config.ini
printf '<h1>status</h1>\n' > ~/m1-project/permissions/index.html
cp ~/m1-project/scripts/precheck.sh ~/m1-project/permissions/check.sh

chmod 600 ~/m1-project/permissions/private.txt
chmod 640 ~/m1-project/permissions/config.ini
chmod 644 ~/m1-project/permissions/index.html
chmod 750 ~/m1-project/permissions/check.sh
chmod 755 ~/m1-project/permissions/public-dir
ls -l ~/m1-project/permissions
```

不要用`chmod 777`掩盖权限设计问题。权限过宽会让无关用户修改程序、配置或数据。

## 8.4 chmod符号法

```bash
touch ~/m1-project/permissions/shared.txt ~/m1-project/permissions/secret.txt
chmod u+x ~/m1-project/permissions/check.sh
chmod g+w ~/m1-project/permissions/shared.txt
chmod o-r ~/m1-project/permissions/secret.txt
chmod u=rw,g=r,o= ~/m1-project/permissions/config.ini
```

对象：`u`所有者、`g`组、`o`其他、`a`全部。

## 8.5 所有者与所属组

```bash
sudo chown operator /srv/course-share/operator-report.txt
sudo chgrp ops-team /srv/course-share/operator-report.txt
sudo chown operator:ops-team /srv/course-share/operator-report.txt
ls -l /srv/course-share/operator-report.txt
```

递归修改前使用`find`或`ls -lR`确认范围，避免把系统目录所有者整体改错。

## 8.6 umask

新文件通常从基础模式`666`屏蔽权限，新目录通常从`777`屏蔽权限。严格来说是按位屏蔽，不应把所有情况理解为普通算术减法。

```bash
old_umask=$(umask)
echo "old_umask=$old_umask"
umask 0022
touch ~/m1-project/permissions/umask-file
mkdir ~/m1-project/permissions/umask-dir
ls -ld ~/m1-project/permissions/umask-file \
  ~/m1-project/permissions/umask-dir
umask "$old_umask"
```

常见结果：

| umask | 新文件 | 新目录 | 场景 |
|---|---|---|---|
| `0022` | `644` | `755` | 普通共享读取 |
| `0002` | `664` | `775` | 同组协作 |
| `0077` | `600` | `700` | 私密数据 |

## 8.7 特殊权限

### SGID目录

目录设置SGID后，其中新建文件通常继承目录所属组：

```bash
sudo chown root:ops-team /srv/course-share
sudo chmod 2770 /srv/course-share
ls -ld /srv/course-share
```

### Sticky bit

在多人可写目录中，Sticky bit限制用户删除其他用户拥有的文件：

```bash
sudo chmod 3770 /srv/course-share
```

这里`3`同时包含SGID（2）和Sticky（1）。

### SUID

SUID可使可执行文件以文件所有者的有效身份运行，风险较高。本模块只要求识别：

```bash
find /usr/bin -perm -4000 -type f 2>/dev/null
```

不要随意给自编程序设置SUID。

## 8.8 验证共享目录

```bash
sudo chown root:ops-team /srv/course-share
sudo chmod 3770 /srv/course-share

sudo -u operator bash -c \
  'echo operator > /srv/course-share/operator.txt'
sudo -u appdev bash -c \
  'echo appdev > /srv/course-share/appdev.txt'
ls -l /srv/course-share

sudo -u appdev cat /srv/course-share/operator.txt
sudo -u appdev rm /srv/course-share/operator.txt
```

最后一条应因Sticky bit而失败。验证权限时必须切换到实际目标用户，不能只看`ls -l`后凭感觉判断。

### 权限排障顺序

```text
确认当前身份id
→ 检查路径每一级目录的x权限
→ 检查目标对象rwx
→ 检查所有者和组
→ 检查ACL或特殊权限
→ 后续再检查SELinux
```

### 本章项目验收

- `ls -ld /srv/course-share`显示组为`ops-team`，并具有SGID和Sticky bit。
- `operator`和`appdev`都能创建文件。
- 新文件自动继承`ops-team`组。
- `appdev`可以读取团队文件，但不能删除`operator`拥有的文件。

```bash
ls -ld /srv/course-share
find /srv/course-share -maxdepth 1 -printf '%M %u:%g %p\n'
sudo -u operator test -w /srv/course-share && echo 'operator can write'
sudo -u appdev test -w /srv/course-share && echo 'appdev can write'
```

`/srv/course-share`、`operator`、`appdev`和`ops-team`都是贯穿项目资产，后续章节继续使用，不在此处清理。

---

# 第9章 sudo与最小权限

## 9.1 为什么不长期使用root

root几乎可以绕过传统文件权限。长期直接使用root存在风险：

- 输错路径可能破坏整个系统。
- 多人共用root难以追踪责任。
- 应用或脚本被利用后获得过高权限。
- 无法落实“只授予完成任务所需权限”。

sudo允许已授权用户以另一个身份执行指定命令，并留下记录。

## 9.2 sudo基本操作

```bash
sudo -l
sudo id
sudo systemctl status chronyd
```

`sudo -l`列出当前账号允许执行的命令。sudo通常验证当前用户密码，而不是root密码。

Rocky Linux常通过`wheel`组授予通用sudo能力：

```text
sudo usermod -aG wheel 用户名
```

Ubuntu常使用`sudo`组：

```text
sudo usermod -aG sudo 用户名
```

以上两条是命令格式，不要把中文占位符直接复制到终端。本项目不能把`operator`加入`wheel`或`sudo`组，否则它会获得通用管理权限，无法验证最小授权。

## 9.3 使用visudo

不要用普通编辑器直接修改`/etc/sudoers`。`visudo`退出前会检查语法：

```bash
sudo visudo -c
```

### 项目工单：只授权operator管理时间同步服务

`operator`需要查看和重启`chronyd`，但不允许创建用户、安装软件或执行任意root命令。使用`/etc/sudoers.d/`独立文件实现：

```bash
sudo visudo -f /etc/sudoers.d/operator-chronyd
```

写入：

```sudoers
operator ALL=(root) /usr/bin/systemctl status chronyd, /usr/bin/systemctl restart chronyd
```

设置正确权限：

```bash
sudo chmod 440 /etc/sudoers.d/operator-chronyd
sudo visudo -cf /etc/sudoers.d/operator-chronyd
```

切换到operator验证：

```bash
su - operator
sudo -l
sudo systemctl status chronyd
sudo systemctl restart chronyd
sudo useradd should-fail
exit
```

`sudo useradd should-fail`必须被拒绝。`exit`返回课程主账号`rocky-server`，后面的日志检查由该账号执行。

## 9.4 NOPASSWD风险

```sudoers
operator ALL=(root) NOPASSWD: /usr/bin/systemctl restart chronyd
```

`NOPASSWD`适合明确且受控的自动化命令，但会降低再次认证保护。不要写成：

```sudoers
operator ALL=(ALL) NOPASSWD: ALL
```

## 9.5 sudo日志

```bash
sudo journalctl _COMM=sudo --since today
if [[ -f /var/log/secure ]]; then
  sudo grep sudo /var/log/secure | tail
fi
```

不同发行版日志位置可能不同。Ubuntu认证日志常见于`/var/log/auth.log`。

### 实践验收

- [ ] `operator`只能查看和重启chronyd。
- [ ] sudoers独立文件语法检查通过。
- [ ] 未授权命令被拒绝。
- [ ] 能从日志中找到sudo操作记录。

`operator`、`ops-team`、`/srv/course-share`和sudoers文件是模块综合交付的验收对象，当前不要清理。保存证据：

```bash
sudo -l -U operator > ~/m1-project/docs/operator-sudo.txt
sudo visudo -cf /etc/sudoers.d/operator-chronyd
```

---

# 第10章 软件包、仓库与DNF/APT

## 10.1 软件包解决什么问题

软件通常包含程序、库、配置模板、文档和安装脚本。软件包系统记录这些文件属于哪个包、依赖哪些包以及如何卸载。

```text
软件仓库
→ 仓库元数据
→ DNF/APT解决依赖
→ 下载RPM/DEB
→ rpm/dpkg安装文件
→ 数据库记录已安装状态
```

不要随意从未知网站下载并执行安装脚本。软件源和软件包签名是供应链安全的一部分。

## 10.2 Rocky Linux的RPM与DNF

### 仓库和缓存

```bash
dnf repolist
sudo dnf makecache
```

Rocky仓库配置通常位于：

```bash
ls /etc/yum.repos.d/
```

切换镜像源前必须备份原配置，并使用课程已经验证的Rocky 9镜像配置。不要使用CentOS 7或其他大版本的repo文件。

### 搜索和查询

```bash
dnf search tree
dnf info tree
dnf list installed
rpm -q bash
rpm -ql bash | head
rpm -qf /usr/bin/ls
```

- `rpm -q`查询包是否安装。
- `rpm -ql`列出包安装的文件。
- `rpm -qf`查询某文件属于哪个包。

### 安装和卸载

```bash
sudo dnf install -y tree
tree --version
sudo dnf remove -y tree
command -v tree || echo 'tree removed'
sudo dnf install -y tree
tree --version
```

删除前阅读事务摘要，确认不会连带删除重要依赖。

### 更新

```bash
dnf check-update
sudo dnf upgrade
dnf history
```

`dnf check-update`发现存在可更新软件包时会返回退出码100，这表示“有更新”，不是普通故障；返回0表示没有可用更新。脚本不能把所有非0状态都简单解释为失败。

课程或生产环境执行全量更新前应确认维护窗口、磁盘空间、内核更新和重启影响。

## 10.3 Ubuntu的DEB与APT

Ubuntu 22.04 Desktop常用：

```bash
sudo apt update
apt search tree
apt show tree
sudo apt install -y tree
dpkg -l tree
dpkg -L tree
dpkg -S "$(command -v tree)"
sudo apt remove tree
```

Ubuntu 22.04采用合并后的`/usr`目录布局时，`/bin`与`/usr/bin`之间可能存在兼容符号链接。`dpkg -S`按包数据库记录的路径查询，不应假定`/usr/bin/ls`一定是数据库中的原始路径；查询刚安装且路径明确的`tree`更稳定。

`apt update`只更新本地软件索引，不等于升级已安装软件。升级软件使用：

```bash
sudo apt upgrade
```

Ubuntu 22.04 Desktop的软件源通常位于`/etc/apt/sources.list`，APT操作记录可在`/var/log/dpkg.log`等位置查看。

交互操作可以使用`apt`；非交互脚本通常更适合使用`apt-get`，并明确处理失败状态。

## 10.4 配置国内镜像源并验证回退

第2章为了保证后续命令可安装，已经完成一次国内镜像初始化。本节从包管理角度重新检查其原理、配置、验证和回退，不要求重复创建另一套仓库。镜像源不是“复制一段命令就结束”，完整操作必须包含版本确认、原配置备份、修改、刷新缓存、安装验证和回退验证。以下以阿里云公开镜像为例；若课程环境统一使用清华镜像，应使用镜像站针对当前发行版生成的配置，不能混用其他版本代号。

### Rocky Linux 9镜像配置

先确认系统版本和架构：

```bash
cat /etc/rocky-release
uname -m
```

确认结果为Rocky Linux 9后，备份当前仓库配置：

```bash
backup_dir="/root/yum-repos-backup-$(date +%F-%H%M%S)"
sudo mkdir -p "$backup_dir"
sudo cp -a /etc/yum.repos.d/. "$backup_dir/"
echo "backup=$backup_dir"
```

将Rocky仓库的镜像列表切换为阿里云基础地址：

```bash
sudo find /etc/yum.repos.d -maxdepth 1 -type f -iname 'rocky*.repo' \
  -exec sed -e 's|^mirrorlist=|#mirrorlist=|g' \
  -e 's|^#baseurl=http://dl.rockylinux.org/$contentdir|baseurl=https://mirrors.aliyun.com/rockylinux|g' \
  -i.bak '{}' +

sudo dnf clean all
sudo dnf makecache
dnf repolist
```

验证不能只看命令是否返回0，还要实际查询和安装一个小软件包：

```bash
dnf info tree
sudo dnf install -y tree
tree --version
```

如果镜像配置不可用，恢复本次修改前的配置：

```bash
sudo cp -a "$backup_dir"/. /etc/yum.repos.d/
sudo dnf clean all
sudo dnf makecache
```

`backup_dir`变量只在当前Shell会话中有效。重新登录后，应先执行`sudo ls -dt /root/yum-repos-backup-* | head -1`确认实际备份目录，再赋值恢复。不要在未确认路径时执行批量删除。

### Ubuntu 22.04 Desktop镜像配置

先确认版本代号和CPU架构：

```bash
. /etc/os-release
printf 'version=%s codename=%s\n' "$VERSION_ID" "$VERSION_CODENAME"
dpkg --print-architecture
```

以下配置只适用于Ubuntu 22.04、代号`jammy`、x86-64/`amd64`环境。确认无误后备份：

```bash
backup_file="/etc/apt/sources.list.backup.$(date +%F-%H%M%S)"
sudo cp -a /etc/apt/sources.list "$backup_file"
echo "backup=$backup_file"
```

写入阿里云镜像配置：

```bash
sudo tee /etc/apt/sources.list >/dev/null <<'EOF'
deb https://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse
EOF

sudo apt clean
sudo apt update
apt-cache policy tree
sudo apt install -y tree
tree --version
```

如果镜像不可用，回退并重新刷新索引：

```bash
sudo cp -a "$backup_file" /etc/apt/sources.list
sudo apt clean
sudo apt update
```

镜像站会有同步延迟。生产系统必须评估安全更新时效；课程环境也应保留原配置，不应通过关闭GPG验证来绕过签名错误。

> **[截图占位 M1-07：Rocky与Ubuntu切换镜像后刷新缓存、查询软件包的成功结果]**

## 10.5 DNF与APT对照

| 任务 | DNF | APT |
|---|---|---|
| 更新索引 | `dnf makecache` | `apt update` |
| 搜索 | `dnf search NAME` | `apt search NAME` |
| 详情 | `dnf info NAME` | `apt show NAME` |
| 安装 | `dnf install NAME` | `apt install NAME` |
| 卸载 | `dnf remove NAME` | `apt remove NAME` |
| 升级 | `dnf upgrade` | `apt upgrade` |
| 底层查询 | `rpm -q` | `dpkg -l` |

## 10.6 包管理排障

| 现象 | 检查 |
|---|---|
| 域名解析失败 | DNS、`/etc/resolv.conf` |
| 仓库不可达 | 网络、镜像站、repo URL |
| 找不到包 | 仓库是否启用、包名、缓存 |
| 数据库被锁 | 是否有另一个包管理进程 |
| GPG检查失败 | 包来源、系统时间、密钥，不能直接长期关闭验证 |
| 磁盘空间不足 | `df -h`、`df -i`、包缓存 |

### 实践任务

在Rocky和Ubuntu中分别完成：

1. 搜索`tree`。
2. 查看软件详情和来源。
3. 安装并验证命令。
4. 查询命令文件属于哪个包。
5. 卸载并确认结果。
6. 找到相应的包管理日志或历史。
7. 选择Rocky或Ubuntu完成一次“备份—换源—刷新—安装验证—回退”闭环，并保留终端记录。
8. 如果实验中卸载了`tree`，结束前重新安装；模块综合验收要求Rocky保留`tree`和`vim-enhanced`。

---

# 第11章 systemd服务与journal日志

## 11.1 进程与服务

进程是正在运行的程序实例。服务通常是长期在后台运行并向系统或网络提供能力的进程。

systemd在Rocky Linux 9和Ubuntu 22.04 Desktop中通常作为PID 1运行，负责启动系统、管理服务依赖和收集服务状态。

```bash
ps -p 1 -o pid,comm,args
```

## 11.2 Unit

systemd使用Unit描述管理对象：

| 类型 | 用途 |
|---|---|
| `.service` | 服务进程 |
| `.socket` | Socket激活 |
| `.timer` | 定时任务 |
| `.mount` | 挂载点 |
| `.target` | 一组Unit的同步目标 |

查看Unit：

```bash
systemctl list-units --type=service
systemctl list-unit-files --type=service
```

## 11.3 服务状态与开机自启

```bash
systemctl status chronyd
sudo systemctl start chronyd
sudo systemctl stop chronyd
sudo systemctl restart chronyd
sudo systemctl enable chronyd
sudo systemctl disable chronyd
systemctl is-active chronyd
systemctl is-enabled chronyd
systemctl show chronyd -p CanReload
```

- active表示当前运行状态。
- enabled表示开机时计划启动。
- enabled不代表当前一定正在运行。
- running也不代表已经设置开机自启。
- reload要求Unit明确支持重新加载配置，通常比restart影响小。Rocky Linux 9的`chronyd.service`通常显示`CanReload=no`，因此不要对它机械执行`systemctl reload chronyd`。

`enable --now`可以同时启用并立即启动：

```bash
sudo systemctl enable --now chronyd
```

## 11.4 查看Unit来源和依赖

```bash
systemctl cat chronyd
systemctl show chronyd -p ActiveState -p SubState -p MainPID
systemctl list-dependencies chronyd
```

不要直接修改`/usr/lib/systemd/system`中的供应商Unit。需要覆盖参数时使用：

```bash
sudo systemctl edit chronyd
```

## 11.5 journalctl

```bash
journalctl -u chronyd
journalctl -u chronyd -n 50
journalctl -u chronyd --since today
journalctl -p err
journalctl -b
journalctl -b -1
```

`journalctl -b -1`查看上一次启动；如果日志未持久化或系统没有可用的上次启动记录，查不到内容是允许结果，不应伪造输出。

持续跟踪日志需要单独执行，观察后按`Ctrl+C`退出：

```bash
journalctl -u chronyd -f
```

| 选项 | 作用 |
|---|---|
| `-u` | 指定Unit |
| `-n` | 最后若干行 |
| `-f` | 持续跟踪 |
| `--since` | 指定开始时间 |
| `-p` | 按优先级过滤 |
| `-b` | 指定本次或历史启动 |

服务启动失败时不要反复restart。先读取`systemctl status`和`journalctl -u`给出的首个有效错误。

## 11.6 创建简单服务

创建脚本：

```bash
sudo tee /usr/local/bin/course-heartbeat.sh <<'SCRIPT'
#!/bin/bash
while true; do
  echo "heartbeat host=$(hostname) time=$(date -Iseconds)"
  sleep 10
done
SCRIPT
sudo chmod 755 /usr/local/bin/course-heartbeat.sh
```

创建Unit：

```bash
sudo tee /etc/systemd/system/course-heartbeat.service <<'UNIT'
[Unit]
Description=Course heartbeat example
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/course-heartbeat.sh
Restart=on-failure
User=nobody

[Install]
WantedBy=multi-user.target
UNIT
```

加载和验证：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now course-heartbeat
systemctl status course-heartbeat --no-pager
journalctl -u course-heartbeat -n 10
systemctl show course-heartbeat -p MainPID -p User -p ActiveState
```

修改Unit后必须执行`daemon-reload`。修改脚本内容不一定需要reload，但需要restart服务才能重新启动脚本进程。

制造一次故障：

```bash
sudo chmod 644 /usr/local/bin/course-heartbeat.sh
sudo systemctl restart course-heartbeat
systemctl status course-heartbeat --no-pager
journalctl -u course-heartbeat -n 20 --no-pager
```

修复：

```bash
sudo chmod 755 /usr/local/bin/course-heartbeat.sh
sudo systemctl restart course-heartbeat
systemctl is-active course-heartbeat
```

清理：

```bash
sudo systemctl disable --now course-heartbeat
sudo rm -f /etc/systemd/system/course-heartbeat.service
sudo rm -f /usr/local/bin/course-heartbeat.sh
sudo systemctl daemon-reload
```

### 服务排障流程

```text
systemctl status
→ 检查Unit和ExecStart路径
→ 检查用户、权限和配置语法
→ journalctl -u查看日志
→ 修复后restart/reload
→ is-active和实际功能验证
```

---

# 第12章 系统状态、进程、磁盘与容量

## 12.1 CPU与系统负载

```bash
uptime
nproc
top
```

`uptime`中的三个load average值分别对应过去1、5、15分钟。Linux负载不仅包含正在等待CPU的可运行任务，也可能包含不可中断I/O等待任务，因此负载高不一定等于CPU使用率100%。

判断时应：

1. 对比CPU逻辑核心数。
2. 观察负载是否持续升高。
3. 查看CPU使用率和I/O等待。
4. 找出具体进程并结合业务判断。

`top`常用按键：

| 按键 | 功能 |
|---|---|
| `1` | 显示每个CPU |
| `P` | 按CPU排序 |
| `M` | 按内存排序 |
| `k` | 发送信号，操作前确认PID |
| `q` | 退出 |

## 12.2 内存

```bash
free -h
ps aux --sort=-%mem | head
```

重点关注`available`而不是只看`free`。Linux会利用空闲内存作为缓存，并在应用需要时回收。Swap持续大量使用、系统频繁换页并伴随响应变慢，才更值得进一步调查。

## 12.3 进程

`ps`通常由`procps-ng`提供，`pstree`通常由`psmisc`提供。先检查并按需安装扩展工具：

```bash
command -v ps
command -v pstree || sudo dnf install -y psmisc
```

```bash
ps aux
ps -ef
pgrep -a sshd
pstree -p
```

进程常见状态：

| 状态 | 含义 |
|---|---|
| `R` | 运行或可运行 |
| `S` | 可中断睡眠 |
| `D` | 不可中断睡眠，常与I/O有关 |
| `T` | 停止或被跟踪 |
| `Z` | 僵尸进程 |

终止进程优先使用正常信号：

```bash
sleep 300 &
TEST_PID=$!
ps -p "$TEST_PID" -o pid,stat,cmd
kill "$TEST_PID"
wait "$TEST_PID" 2>/dev/null || true
ps -p "$TEST_PID" || echo 'test process stopped'
```

只有进程无法正常退出并确认影响后，才考虑：

```text
kill -9 实际PID
```

上面是应急命令格式，不要输入字面量“实际PID”，也不要对未确认身份的进程执行。SIGKILL不给进程清理数据和释放业务资源的机会。

服务进程优先通过`systemctl`管理，而不是直接kill主进程。

## 12.4 磁盘、分区、文件系统与挂载点

这些对象不能混为一谈：

```text
磁盘 /dev/sda
└── 分区 /dev/sda1
    └── 文件系统 xfs/ext4
        └── 挂载到目录 /
```

查看：

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,FSAVAIL,FSUSE%,MOUNTPOINTS
findmnt
findmnt /
sudo blkid
```

如果系统使用LVM，还可能看到：

```text
物理卷PV → 卷组VG → 逻辑卷LV → 文件系统 → 挂载点
```

本模块只要求识别：

```bash
command -v pvs || sudo dnf install -y lvm2
sudo pvs
sudo vgs
sudo lvs
```

不要在不了解存储结构时执行扩容、缩容或格式化命令。

## 12.5 磁盘空间与inode

后面的“已删除但仍被占用文件”检查需要`lsof`：

```bash
command -v lsof || sudo dnf install -y lsof
```

```bash
df -h
df -i
sudo du -sh /var/log
sudo du -xhd1 /var | sort -h
```

- `df`查看文件系统整体空间。
- `du`统计目录树中可见文件占用。
- `df -i`查看inode使用。

磁盘空间充足但inode耗尽时，仍然无法创建新文件。`df`与`du`差异很大时，可能存在已删除但仍被进程打开的文件：

```bash
sudo lsof +L1
```

不要发现日志大就直接删除。应先确认服务、日志轮转和保留要求。

## 12.6 端口和基础网络状态

```bash
ss -lntup
ss -tan state established
```

监听地址含义：

| 地址 | 含义 |
|---|---|
| `127.0.0.1:PORT` | 仅本机IPv4访问 |
| `0.0.0.0:PORT` | 所有IPv4接口 |
| `[::1]:PORT` | 仅本机IPv6 |
| `[::]:PORT` | 所有IPv6接口，是否同时接受IPv4取决于配置 |

监听所有接口意味着可能被外部访问，但实际仍受路由、防火墙和上层认证控制。

## 12.7 编写系统巡检脚本

创建脚本：

```bash
cat > ~/m1-project/scripts/m1-health-check.sh <<'SCRIPT'
#!/bin/bash
set -u

status=0
echo "=== health check $(date -Iseconds) host=$(hostname) ==="

echo "[load]"
uptime

echo "[memory]"
free -h

echo "[filesystem]"
df -h -x tmpfs -x devtmpfs

while read -r filesystem size used available percent mountpoint; do
  usage=${percent%%%}
  if [[ $usage =~ ^[0-9]+$ ]] && (( usage >= 80 )); then
    echo "WARNING filesystem=$mountpoint usage=${usage}%"
    status=1
  fi
done < <(df -P -x tmpfs -x devtmpfs | tail -n +2)

echo "[failed services]"
failed_count=$(systemctl list-units --type=service --state=failed --no-legend --no-pager | grep -c . || true)
systemctl list-units --type=service --state=failed --no-pager
if (( failed_count > 0 )); then
  echo "WARNING failed_services=$failed_count"
  status=1
fi

echo "[important services]"
for service in sshd chronyd; do
  if systemctl is-active --quiet "$service"; then
    echo "OK service=$service"
  else
    echo "WARNING service=$service"
    status=1
  fi
done

echo "[listening ports]"
ss -lntup

echo "result=$status"
exit "$status"
SCRIPT

chmod +x ~/m1-project/scripts/m1-health-check.sh
~/m1-project/scripts/m1-health-check.sh
echo "exit_code=$?"
```

脚本中的关键结构：

| 结构 | 作用 |
|---|---|
| `status=0` | 先假定巡检正常 |
| `$(命令)` | 捕获命令输出并赋值 |
| `while read ...; do ...; done` | 逐行读取`df`结果 |
| `< <(命令)` | 把命令输出作为循环输入，这是Bash进程替换 |
| `[[ ... ]]` | 进行模式或条件判断 |
| `(( ... ))` | 进行整数条件判断 |
| `for ...; do ...; done` | 依次检查多个服务 |
| `exit "$status"` | 正常时退出0，发现告警时退出1 |

脚本将结果展示给人，同时用退出状态告诉自动化工具是否发现磁盘、关键服务或失败Unit问题。该版本按Rocky主线环境检查`sshd`和`chronyd`；迁移到Ubuntu前，应先用`systemctl list-unit-files`确认对应Unit名称。后续Python自动化运维课程可以通过SSH批量执行这类脚本。

## 12.8 系统状态排障案例

### 案例1：根分区使用率过高

```text
df -h确认文件系统
→ du -xhd1 /定位大目录
→ 继续逐层du
→ find查找大文件
→ 确认文件用途和进程
→ 归档、轮转或安全清理
→ 再次df验证
```

### 案例2：服务启动失败

```text
systemctl status SERVICE
→ journalctl -u SERVICE
→ 检查配置、权限、端口和资源
→ 修复并重启
→ is-active + 实际功能验证
```

### 案例3：CPU高

```text
uptime/nproc
→ top按P排序
→ ps查看命令和用户
→ 判断是否正常任务
→ 优先正常停止或服务级处理
→ 验证负载是否恢复
```

---

# 模块综合实践（教材拓展）：交付一台可管理的Linux基础服务器

## 任务背景

一台新安装的Rocky Linux 9服务器需要交付给后续网络和服务部署模块。它必须具备明确的身份、规范的用户权限、可用的软件源、受控的sudo授权、正常的基础服务和可执行的健康检查。

## 任务清单

1. 主机名保持为`rocky-server`；若尚未进入实验8，保留当前DHCP地址并记录，完成实验8后再使用教师分配的稳定静态地址。
2. 保留普通账号`rocky-server`，不得日常共用root。
3. 确认`ops-team`组以及`operator`、`appdev`账号符合第7章角色矩阵。
4. 确认`/srv/course-share`只允许`ops-team`成员协作，新文件继承组且成员不能删除他人文件。
5. 保留sudoers独立文件，只允许`operator`查看和重启`chronyd`。
6. 验证DNF软件源，安装`tree`和`vim-enhanced`。
7. 确认`chronyd`和`sshd`运行且开机自启。
8. 运行`~/m1-project/scripts/m1-health-check.sh`，不存在未解释的失败项。
9. 归档`~/m1-project`并完成恢复验证。
10. 提交服务器基线报告。

## 基线报告模板

```markdown
# Linux基础服务器交付报告

## 1. 系统信息
- 主机名：
- 发行版：
- 内核：
- CPU/内存/磁盘：

## 2. 用户和组
- 管理账号：
- 项目组：
- sudo授权：

## 3. 文件和权限
- 共享目录：
- 所有者和组：
- 权限与特殊权限：

## 4. 软件与服务
- 软件源：
- 已安装软件：
- active/enabled服务：

## 5. 资源与健康
- 磁盘使用率：
- inode使用率：
- 失败服务：
- 巡检脚本退出码：

## 6. 备份恢复
- 归档文件：
- 恢复目录：
- diff验证结果：

## 7. 已知问题
```

## 综合验收命令

```bash
hostnamectl
cat /etc/os-release
ip -br addr
ip route
id rocky-server
id operator
id appdev
getent group ops-team
ls -ld /srv/course-share
sudo -l -U operator
dnf repolist
rpm -q tree vim-enhanced
systemctl is-active chronyd sshd
systemctl is-enabled chronyd sshd
systemctl --failed
df -h
df -i
~/m1-project/scripts/m1-health-check.sh
```

---

# 模块复习

## 核心对象关系

```text
发行版 = 内核 + GNU工具 + Shell + 包管理 + systemd + 配置

用户/组
  ↓ 决定身份
文件所有者/组/rwx/特殊权限
  ↓ 决定传统访问权限
sudo
  ↓ 提供受控提权
软件包与仓库
  ↓ 安装程序和服务
systemd + journal
  ↓ 管理运行状态和日志
CPU/内存/磁盘/进程/端口
  ↓ 提供运行证据
```

## 常用命令速查

| 任务 | 命令 |
|---|---|
| 系统版本 | `cat /etc/os-release`、`uname -r` |
| 当前身份 | `whoami`、`id`、`groups` |
| 目录文件 | `pwd`、`ls`、`mkdir`、`cp`、`mv`、`rm` |
| 查看查找 | `cat`、`less`、`head`、`tail`、`find` |
| 编辑归档 | `vim`、`tar`、`zip`、`unzip` |
| 用户组 | `useradd`、`usermod`、`passwd`、`groupadd` |
| 权限 | `chmod`、`chown`、`chgrp`、`umask` |
| sudo | `sudo -l`、`visudo` |
| Rocky软件 | `dnf`、`rpm` |
| Ubuntu软件 | `apt`、`dpkg` |
| 服务日志 | `systemctl`、`journalctl` |
| 资源状态 | `top`、`free`、`lsblk`、`df`、`du`、`ps`、`ss` |

## 复习题

1. 为什么Linux发行版版本与内核版本不同？
2. 绝对路径、相对路径、工作目录分别是什么？
3. `cp -a`和普通`cp`的应用场景有什么差异？
4. 硬链接与符号链接在删除原文件后有什么区别？
5. 为什么目录的`x`权限非常重要？
6. `umask 0022`通常会产生什么文件和目录权限？
7. 为什么不应使用`chmod 777`作为通用修复方案？
8. `systemctl enable`和`systemctl start`有什么区别？
9. `apt update`是否会升级所有已安装软件？
10. 为什么判断内存是否不足应关注`available`？
11. `df -h`有空间但无法创建文件，下一步应检查什么？
12. 服务启动失败时，应该按什么顺序收集证据？

## 拓展练习

1. 为`~/m1-project/scripts/m1-health-check.sh`增加JSON输出模式。
2. 使用systemd timer代替cron每小时运行一次巡检脚本。
3. 比较Rocky和Ubuntu中SSH服务Unit名称、日志位置和网络配置方式。
4. 查找系统中的SUID文件，分析其中三个程序为什么需要SUID。
5. 模拟磁盘空间告警，完成定位、清理和验证记录。

---

# 参考资料

- [Rocky Linux 9安装文档](https://docs.rockylinux.org/guides/9_6_installation/)
- [Rocky Linux DNF包管理文档](https://docs.rockylinux.org/guides/package_management/dnf_package_manager/)
- [Ubuntu Desktop安装文档](https://documentation.ubuntu.com/desktop/en/24.04/tutorial/install-ubuntu-desktop/)
- [Ubuntu Desktop软件安装文档](https://documentation.ubuntu.com/desktop/en/latest/how-to/software/install-an-application/)
- [阿里云Rocky Linux镜像配置说明](https://developer.aliyun.com/mirror/rockylinux)
- [阿里云Ubuntu镜像配置说明](https://developer.aliyun.com/mirror/ubuntu)
- [清华大学Ubuntu镜像配置说明](https://mirrors.tuna.tsinghua.edu.cn/help/ubuntu/)
- [GNU Coreutils手册](https://www.gnu.org/software/coreutils/manual/coreutils.html)
- [systemd项目文档](https://systemd.io/)
- [systemctl手册](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html)
- [journalctl手册](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html)
- [Vim帮助与用户手册](https://vimhelp.org/)

本教材中的命令应在课程虚拟机或快照环境中执行。涉及删除、权限递归修改、软件升级和系统服务变更时，必须先确认目标路径、影响范围和回退方式。
