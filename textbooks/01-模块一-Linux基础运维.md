# 模块一：Linux基础运维

> 适用课程：《Linux操作系统》  
> 对应实验：实验1—实验7｜建议学时：22学时
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
|:--|---|---|---|
| 实验1（4学时） | 第1—2章 | Linux起源、发行版、VMware和三机安装 | 可运行、可登录、可联网、可回退的三机环境 |
| 实验2（4学时） | 第3—5章相关内容 | 命令行、目录、文件、查看和基础重定向 | 规范的项目目录树和操作记录 |
| 实验3（2学时） | 第5—6章 | 查找、链接、Vim、归档和恢复 | 配置修改、归档及恢复验证 |
| 实验4（4学时） | 第7—9章 | 用户、组、共享权限、umask和最小sudo | 部门账号、共享目录和授权证据 |
| 实验5（2学时） | 第10章 | DNF、RPM、仓库和GPG | 软件安装、查询、卸载与回退记录 |
| 实验6（2学时） | 第11章 | systemd、journal和启动故障 | 状态—日志—根因—修复记录 |
| 实验7（4学时） | 第12章 | CPU、内存、进程、普通挂载、LVM和容量 | 持久挂载、LVM扩容与系统巡检表 |

## 本册学习方式

本册按照第1—12章顺序学习。每章先理解对象和原理，再完成本章中的短练习，最后进入对应实验。教材中的短练习用于验证单项知识；实验1—7把多项知识组合成三机环境、账号权限、服务故障和巡检成果。

教材练习默认使用`~/course-practice/m1/chXX`等独立目录。练习会在首次使用前创建所需目录和文件，可以按章节说明清理。`~/m1-project`、`/srv/course-share`、实验账号、软件配置和服务状态属于贯穿项目成果，除非实验明确要求，不得因完成某一章练习而删除。

学习每章时完成下面的闭环：

```text
明确问题 → 阅读必学知识 → 预测命令结果 → 完成短练习
→ 使用命令验证 → 解释错误 → 进入对应实验 → 保存验收证据
```

正文用于建立完整知识体系；标为“拓展”的内容用于查阅，不作为为进入下一实验必须掌握的范围。实验中遇到路径、权限、服务或资源问题时，应返回对应章节按对象关系排查，而不是直接复制其他来源的修复命令。

### 代码块与任务标记

本册代码块分为三类：

| 标记 | 是否执行 | 用途 |
|---|---|---|
| 观察命令 | 可以执行 | 查看系统现状，不依赖课程项目成果 |
| 本章短练习 | 按顺序执行 | 使用`~/course-practice/m1/`中的独立对象，练习单项知识 |
| 实验衔接 | 转入对应实验后执行 | 创建或修改`~/m1-project`、系统账号、`/srv`目录、软件包和需保留的系统服务 |

没有标明“本章短练习”的代码块可能只是语法示例。先预测其作用和结果，再根据上下文决定是否执行，不应把教材中的每个代码块整段粘贴到终端。第11章会创建一个明确标记、完成后立即清理的临时服务；它不属于贯穿项目状态。

### 第1—12章学练顺序

| 章节 | 20—25分钟必学内容 | 本章短练习 | 对应实验 |
|---|---|---|---|
| 第1章 | 操作系统、内核、发行版、Shell与运维闭环 | 写出服务器交付八问 | 实验1任务导入 |
| 第2章 | VMware层次、NAT/桥接/仅主机、VMnet8与快照 | 完成三机资源和网络模式规划 | 实验1 |
| 第3章 | 命令格式、帮助、补全、引号与退出状态 | 查询命令类型并比较成功/失败退出码 | 实验2前半部分 |
| 第4章 | Linux目录树、路径、创建、复制、移动与删除 | 在`ch04`整理一组交付文件 | 实验2 |
| 第5章 | 查看、筛选、find、inode、链接与重定向 | 在`ch05`完成日志查找和链接验证 | 实验3前半部分 |
| 第6章 | Vim模式、配置备份、tar与恢复验证 | 在`ch06`完成配置修改和归档恢复 | 实验3 |
| 第7章 | UID/GID、主组、附加组、账号文件与密码 | 读取身份信息并设计账号矩阵 | 实验4前半部分 |
| 第8章 | 文件/目录rwx、umask、SGID、Sticky bit与ACL | 在个人目录预测并验证权限 | 实验4中段 |
| 第9章 | sudo、绝对命令路径、visudo与最小授权 | 阅读授权需求并写出规则草案 | 实验4后半部分 |
| 第10章 | RPM/DNF、DEB/APT、仓库、签名与回退 | 查询软件来源并预演安装或卸载 | 实验5 |
| 第11章 | 进程、Unit、active/enabled与journal | 创建并排查可清理的临时服务 | 实验6 |
| 第12章 | CPU、负载、内存、进程、磁盘、inode与端口 | 生成只读系统状态摘要 | 实验7 |

## 贯穿项目：新业务服务器基础交付

本模块不是十二组互不相关的命令练习。你将以初级Linux运维工程师身份，完成一台新业务服务器的基础交付。

### 项目背景

星云科技准备上线一个内部应用。网络和应用服务将在后续模块部署，本模块先交付操作系统基础环境。交付结果必须让后续人员知道服务器如何安装、文件放在哪里、谁有权限、软件从哪里安装、服务是否正常以及出现问题时如何回退。

### 贯穿成果

```text
Rocky Linux基础环境（实验8再配置静态地址）
├── ~/m1-project              项目工作区和操作证据
├── /srv/course-share         项目协作与权限验证目录
├── dev01、dev02              开发协作账号
├── auditor                   审计只读账号
├── juniorops                 初级运维受限sudo账号
├── project-dev、project-audit 项目开发组与审计组
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

### 本章短练习：定义交付标准

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
|:-:|:-:|:--:|:--:|:--:|:-:|
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

交互观察：打开[VMware三种网络模式与课程三机拓扑动画](../animations/01-vmware-network-modes/index.html)，依次切换NAT、桥接和仅主机模式，观察同网段通信、外网访问和外部主动访问的路径。动画中的地址只用于说明关系，实验1仍应记录本机实际VMnet8参数。

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
NAT_GATEWAY=$(ip route show default | awk 'NR==1 {print $3}')
ping -c 3 "$NAT_GATEWAY"
```

如果没有地址，先检查VMware虚拟网卡是否连接到NAT、安装器是否启用了网卡，再检查NetworkManager连接。静态IP、网关和DNS的修改方法在实验8集中学习，避免第一次课同时承担安装和网络规划两项高风险操作。

### 配置可用的软件源

机房不能稳定访问默认国外仓库，因此在安装其他工具前先切换到已验证的国内镜像。以下以阿里云Rocky镜像为例：

```bash
# 1. 备份原有源配置文件（防止误操作）
sudo cp -r /etc/yum.repos.d /etc/yum.repos.d.backup

# 2. 使用 sed 命令替换仓库地址为阿里云
sudo sed -e 's|^mirrorlist=|#mirrorlist=|g' \
         -e 's|^#baseurl=http://dl.rockylinux.org/$contentdir|baseurl=https://mirrors.aliyun.com/rockylinux|g' \
         -i.bak \
         /etc/yum.repos.d/rocky*.repo

# 3. 清理旧缓存并生成新缓存
sudo dnf clean all
sudo dnf makecache
```

`makecache`失败时不要继续安装。先查看错误并检查IP、默认路由、DNS和系统时间；若确认镜像配置不适用，读取刚才保存的路径并恢复：

```bash
ROCKY_REPO_BACKUP=$(cat /var/tmp/course-rocky-repo-backup.path)
sudo cp -a "$ROCKY_REPO_BACKUP"/. /etc/yum.repos.d/
sudo dnf clean all
sudo dnf makecache
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
. /etc/os-release
printf 'version=%s codename=%s arch=%s\n' \
  "$VERSION_ID" "$VERSION_CODENAME" "$(dpkg --print-architecture)"
```

只有结果为Ubuntu `22.04`、代号`jammy`且架构为`amd64`时，才使用下面的课程配置。先备份，再切换到开课前已验证的阿里云镜像：

```bash
UBUNTU_SOURCE_BACKUP="/etc/apt/sources.list.before-course.$(date +%F-%H%M%S)"
sudo cp -a /etc/apt/sources.list "$UBUNTU_SOURCE_BACKUP"
printf '%s\n' "$UBUNTU_SOURCE_BACKUP" | \
  sudo tee /var/tmp/course-ubuntu-source-backup.path

sudo tee /etc/apt/sources.list >/dev/null <<'EOF'
deb https://mirrors.aliyun.com/ubuntu/ jammy main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ jammy-updates main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ jammy-backports main restricted universe multiverse
deb https://mirrors.aliyun.com/ubuntu/ jammy-security main restricted universe multiverse
EOF

sudo apt clean
sudo apt update
sudo apt install -y open-vm-tools open-vm-tools-desktop openssh-server curl
sudo systemctl enable --now ssh
cat /etc/os-release
ip -br addr
ip route
```

Ubuntu 22.04 Desktop的软件源通常配置在`/etc/apt/sources.list`。不要直接复制其他发行版或其他Ubuntu版本的软件源配置。`apt update`失败时先排查网络、DNS、时间和镜像地址；需要回退时读取`/var/tmp/course-ubuntu-source-backup.path`中记录的实际文件名并恢复。

## 2.7 三机基础连通性验证

分别用`ip -br addr`记录三台机器的DHCP地址。网关可从默认路由自动取得；在`ubuntu-client`通过提示输入两台Rocky的实际地址：

两台Rocky分别测试网关；`ubuntu-client`测试两台服务器：

```bash
VMNET8_GATEWAY=$(ip route show default | awk 'NR==1 {print $3}')
ping -c 3 "$VMNET8_GATEWAY"

# ubuntu-client继续执行
read -r -p 'rocky-server当前IPv4地址：' ROCKY_SERVER_IP
read -r -p 'rocky-web当前IPv4地址：' ROCKY_WEB_IP
ping -c 3 "$ROCKY_SERVER_IP"
ping -c 3 "$ROCKY_WEB_IP"
```

Windows宿主机执行：

```powershell
$RockyServerIp = Read-Host '请输入rocky-server当前IPv4地址'
$RockyWebIp = Read-Host '请输入rocky-web当前IPv4地址'
$UbuntuClientIp = Read-Host '请输入ubuntu-client当前IPv4地址'

ping rocky-server当前IPv4地址
ping $RockyWebIp
ping $UbuntuClientIp
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

### 本章短练习：完成三机规划表

安装前先完成规划，避免边点击安装器边临时决定资源和网络。将以下内容记录到纸面或课程记录中：

| 项目 | rocky-server | rocky-web | ubuntu-client |
|---|---|---|---|
| 操作系统版本 | Rocky Linux 9 | Rocky Linux 9 | Ubuntu 22.04 Desktop |
| 主机名 |  |  |  |
| VMware网络 |  |  |  |
| vCPU/内存/磁盘 |  |  |  |
| 初始地址来源 |  |  |  |
| 主要用途 |  |  |  |

同时记录VMnet8实际子网、掩码、网关和DHCP范围。地址不能照抄教材示例，规划中的静态地址必须避开网关和DHCP动态分配区；本章只规划，实验8才正式配置固定地址。

### 实验衔接：实验1验收

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
touch file{1..3}.txt     # 创建file1.txt file2.txt file3.txt
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

### 本章短练习：查询命令并验证退出状态

在Rocky和Ubuntu中分别创建本章独立记录目录，然后按顺序执行：

```bash
mkdir -p ~/course-practice/m1/ch03
{
    printf '=== system ===\n'
    grep -E '^(NAME|VERSION_ID)=' /etc/os-release
    printf '\n=== command types ===\n'
    type cd
    type ls
    type echo
    printf '\n=== successful command ===\n'
    ls /etc/passwd
    printf 'success_exit_code=%s\n' "$?"
    printf '\n=== failed command ===\n'
    ls /path/not-exist
    printf 'failure_exit_code=%s\n' "$?"
} > ~/course-practice/m1/ch03/command-basics.txt 2>&1
```

继续完成两个不写入记录文件的交互任务：使用`man ls`找到按修改时间排序的选项；使用Tab补全进入`/etc/systemd/system`，再回到家目录。不要直接照抄完整路径来代替补全练习。

### 验收标准

- [ ] 能解释命令、选项和参数。
- [ ] 会使用`--help`、`man`、`type`和历史搜索。
- [ ] 能正确解释`$?`。
- [ ] 能说出DNF与APT的基本对应关系。
- [ ] `command-basics.txt`中成功命令退出码为0、失败命令退出码非0。

### 实验衔接：实验2前半部分

实验2会从命令解释和帮助查询转入真实文件目录工单。正式项目目录由实验2根据业务任务创建，不复制本章`ch03`记录目录。

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

在Rocky和Ubuntu分别验证。先观察这些路径本身：

```bash
ls -ld /bin /sbin /lib /lib64
```

如果Ubuntu提示`/lib64`不存在，只记录现象，不需要创建它。再逐条查看链接最终指向哪里：

```bash
readlink -f /bin
```

```bash
readlink -f /sbin
```

```bash
readlink -f /bin/ls
```

最后确认直接输入`ls`时会执行哪个程序：

```bash
command -v ls
```

因此`/bin`并没有消失。输入`/bin/ls`时，系统最终通常执行`/usr/bin/ls`。不同CPU架构的库目录名称可能不同，不能假设所有系统都一定存在`/lib64`。

交互观察：打开[Linux目录树、路径与链接动画](../animations/02-linux-filesystem-paths-links/index.html)，先完成“目录树与/bin”和“绝对/相对路径”两个主题。每一步先根据当前目录预测目标，再到Rocky中使用`pwd`、`ls -ld`和`readlink -f`验证。

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

先显示当前目录：

```bash
pwd
```

使用绝对路径进入日志目录：

```bash
cd /var/log
```

确认当前位置：

```bash
pwd
```

使用相对路径回到上一级：

```bash
cd ..
```

再次确认当前位置，然后返回家目录：

```bash
pwd
```

```bash
cd ~
```

```bash
pwd
```

`cd -`会返回上一次所在目录。执行前先预测结果：

```bash
cd -
```

## 4.3 创建文件和目录

本章先在独立练习目录中操作。业务部门交来了一组待整理文件，要求运维人员建立工作区、保留原始文件并形成清晰的交付目录。实验2会使用新的业务数据建立正式项目`~/m1-project`。

| 目录 | 用途 |
|---|---|
| `incoming` | 接收的原始文件，只做必要清理 |
| `config` | 当前使用的配置文件 |
| `data` | 项目数据和清单 |
| `logs` | 操作或应用日志 |
| `scripts` | 运维脚本 |
| `backup` | 初始配置和归档 |
| `docs` | 说明、证据和交付文档 |

### 本章短练习：准备交付文件

练习目录固定为`~/course-practice/m1/ch04`。本节按照“执行一条、观察一次”的顺序准备对象。

第一步，创建多级练习目录：

```bash
mkdir -p ~/course-practice/m1/ch04
```

`-p`表示缺少的父目录也一并创建；目录已经存在时，不会仅因这一点报错。

第二步，进入练习目录：

```bash
cd ~/course-practice/m1/ch04
```

立即确认当前位置。后续命令使用相对路径，避免反复输入很长的绝对路径：

```bash
pwd
```

第三步，逐个创建业务目录。每执行一条命令，就观察一次：

```bash
mkdir incoming
```

```bash
ls -ld incoming
```

```bash
mkdir config
```

```bash
mkdir data
```

```bash
mkdir logs
```

```bash
mkdir scripts
```

```bash
mkdir backup
```

```bash
mkdir docs
```

熟悉`mkdir`后，可以用一条`ls`同时检查这些目录：

```bash
ls -ld incoming config data logs scripts backup docs
```

第四步，创建一份空的目录规划文档：

```bash
touch docs/directory-plan.md
```

用`ls -l`确认对象类型和文件名：

```bash
ls -l docs/directory-plan.md
```

第五步，模拟业务部门交来的原始文件。这里暂时使用`echo 内容 > 文件`生成简短素材；`>`表示把输出写入文件，后续章节会专门学习重定向。

```bash
echo 'app_name=internal-demo' > incoming/app.conf.sample
```

```bash
echo 'rocky-server,data-and-ops,待实验8确定' > incoming/server-list.csv
```

```bash
echo '该文件为过期临时说明，确认后删除。' > incoming/obsolete-note.tmp
```

```bash
echo 'INFO service preparation started' > logs/app.log
```

`scripts`目录目前保持为空。第3.6章“Shell服务器巡检”才会正式编写脚本。

第六步，逐个确认后续任务需要的对象确实存在：

```bash
ls -l incoming/app.conf.sample
```

```bash
ls -l incoming/server-list.csv
```

```bash
ls -l incoming/obsolete-note.tmp
```

```bash
ls -l logs/app.log
```

最后查看两层目录结构：

```bash
find . -maxdepth 2 -print
```

只有`incoming`中的三个输入文件和`logs/app.log`都存在，才继续4.4节。

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

### 练习工单：整理业务部门交付文件

业务要求如下：

1. 原始配置样例必须保留在`incoming`。
2. 将配置样例复制为正式文件`config/app.conf`。
3. 在修改正式配置前，将其初始版本备份为`backup/app.conf.initial`。
4. 服务器清单属于交付文档，应移动到`docs/server-list.csv`。
5. 查看`obsolete-note.tmp`内容，确认确实过期后再删除。
6. 操作完成后，不能出现误删除的目录或额外副本。

先根据需求判断每一步使用`cp`、`mv`还是`rm`，再按下面的顺序逐条完成。

开始前确认仍位于本章练习目录：

```bash
pwd
```

预期路径以`/course-practice/m1/ch04`结尾。

第一步，复制配置样例，保留原文件：

```bash
cp incoming/app.conf.sample config/app.conf
```

观察源文件和副本是否同时存在：

```bash
ls -l incoming/app.conf.sample config/app.conf
```

第二步，备份正式配置：

```bash
cp config/app.conf backup/app.conf.initial
```

确认备份已经产生：

```bash
ls -l backup/app.conf.initial
```

第三步，把服务器清单移动到交付文档目录：

```bash
mv incoming/server-list.csv docs/server-list.csv
```

先检查新位置：

```bash
ls -l docs/server-list.csv
```

再检查原位置。下面这条命令应提示文件不存在，这正是移动成功的证据：

```bash
ls -l incoming/server-list.csv
```

第四步，删除前先查看临时说明：

```bash
cat incoming/obsolete-note.tmp
```

确认内容确实过期后，使用交互确认方式删除：

```bash
rm -i incoming/obsolete-note.tmp
```

输入`y`确认，再检查它已经不存在：

```bash
ls -l incoming/obsolete-note.tmp
```

这里出现`No such file or directory`是预期结果，因为目标已经被删除。

第五步，逐项查看最终对象：

```bash
ls -l incoming/app.conf.sample
```

```bash
ls -l config/app.conf
```

```bash
ls -l backup/app.conf.initial
```

```bash
ls -l docs/server-list.csv
```

## 4.5 隐藏文件和通配符

以`.`开头的名称通常不会被普通`ls`显示。回到练习目录并创建隐藏文件：

```bash
cd ~/course-practice/m1/ch04
```

```bash
touch .practice-meta
```

普通`ls`不会显示它：

```bash
ls
```

加入`-a`后可以看到：

```bash
ls -la
```

常用通配符：

| 通配符 | 含义 | 示例 |
|---|---|---|
| `*` | 任意长度字符 | `*.log` |
| `?` | 任意一个字符 | `file?.txt` |
| `[abc]` | 指定集合中的一个字符 | `file[123].txt` |
| `[0-9]` | 指定范围中的一个字符 | `log[0-9]` |

通配符由Shell展开后再交给命令。先用`printf '%s\n' pattern`或`ls`确认匹配结果，再执行批量复制或删除。

在`logs`目录创建三份空白练习文件：

```bash
touch logs/app-1.log
```

```bash
touch logs/app-2.log
```

```bash
touch logs/readme.txt
```

创建日志备份目录：

```bash
mkdir -p backup/logs
```

复制前先显示`*.log`实际匹配的对象：

```bash
ls -l logs/*.log
```

确认结果中没有`readme.txt`，再执行复制：

```bash
cp logs/*.log backup/logs/
```

检查目标目录：

```bash
ls -l backup/logs
```

`readme.txt`不匹配`*.log`，因此不会被复制。

## 4.6 文件类型

`ls -l`的第一个字符可以初步表示对象类型：

```bash
ls -l config/app.conf
```

`file`根据文件内容和特征判断类型：

```bash
file /bin/ls
```

```bash
file config/app.conf
```

`stat`显示inode、大小、权限和时间等详细元数据：

```bash
stat /etc/passwd
```

```bash
stat config/app.conf
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

### 本章练习验收

最终目录至少应包含：

```text
ch04
├── .practice-meta
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
└── scripts/
```

执行验收前先回到练习目录：

```bash
cd ~/course-practice/m1/ch04
```

查看目录和文件：

```bash
find . -maxdepth 3 -print
```

分别核对配置副本和备份内容：

```bash
cat config/app.conf
```

```bash
cat backup/app.conf.initial
```

`docs/directory-plan.md`已经作为待编写练习文档创建。用自己的语言补充各目录用途，并解释为什么原始配置、正式配置和备份配置不能只保留一份。

### 实验衔接：实验2

进入实验2后，不复制本练习目录。根据实验2的新业务工单，从空白状态建立`~/m1-project`并保存正式成果。这里练习的是单项文件操作，实验2验收的是能否根据业务要求独立组织文件。

---

# 第5章 文件查看、查找与链接

## 本章学习目标

完成本章后，应能够：

1. 根据文件大小和任务选择`cat`、`less`、`head`、`tail`。
2. 使用`grep`按内容筛选，并读懂常见正则表达式。
3. 使用`wc`统计行、单词和字节，说明“筛选”和“统计”的区别。
4. 使用`sort`、`uniq`和`cut`完成字段提取、排序与频次统计。
5. 使用`find`按名称、类型、大小、时间和所有者查找文件。
6. 理解标准输入、标准输出、标准错误、管道和重定向。
7. 区分inode、硬链接和符号链接，并预测删除原路径后的结果。

## 5.1 先准备真实的练习数据

文本处理命令不是为了背选项，而是为了从大量内容中回答问题。本章使用两类真实数据：

- 系统真实文件：`/etc/passwd`和`/etc/os-release`；
- 真实日志：使用`logger`把消息写入systemd journal，再用`journalctl`导出为普通文本文件。

`journalctl`的完整用法将在1.11学习。本章只把它当作日志数据来源。

### 步骤1：创建本章目录

```bash
mkdir -p ~/course-practice/m1/ch05/logs
```

```bash
mkdir -p ~/course-practice/m1/ch05/docs
```

```bash
mkdir -p ~/course-practice/m1/ch05/data/link-lab
```

```bash
mkdir -p ~/course-practice/m1/ch05/evidence
```

```bash
cd ~/course-practice/m1/ch05
```

本章前半部分为了便于观察，使用`logs/...`、`docs/...`等相对路径，它们都以`~/course-practice/m1/ch05`为起点。如果中途重新登录或更换终端，应先重新执行上面的`cd`命令；5.10综合任务改用绝对路径，避免提交时依赖当前目录。

### 步骤2：向系统日志写入一组可识别的事件

下面每条`logger`命令都会调用系统日志接口，不是直接向练习文件中伪造结果。`-t course-ch05`为日志设置统一标识，便于随后筛选。

```bash
logger -t course-ch05 'INFO service=web action=start result=success'
```

```bash
logger -t course-ch05 'INFO service=db action=start result=success'
```

```bash
logger -p user.warning -t course-ch05 'WARN service=web action=healthcheck result=slow'
```

```bash
logger -p user.err -t course-ch05 'ERROR service=db action=connect result=failed'
```

```bash
logger -t course-ch05 'INFO service=cache action=start result=success'
```

```bash
logger -p user.warning -t course-ch05 'WARN service=cache action=memory result=high'
```

```bash
logger -p user.err -t course-ch05 'ERROR service=web action=request result=timeout'
```

```bash
logger -t course-ch05 'INFO service=web action=recover result=success'
```

### 步骤3：从journal导出最近8条课程日志

```bash
sudo journalctl -t course-ch05 -n 8 --no-pager -o cat > logs/course-ch05.log
```

这里使用`-o cat`只保留消息正文，方便初学者观察文本处理过程。查看文件是否存在且非空：

```bash
test -s logs/course-ch05.log
```

```bash
echo $?
```

返回`0`表示检查成立。再查看行数：

```bash
wc -l logs/course-ch05.log
```

预期为8行。如果不是8行，重新执行八条`logger`命令和导出命令，不要创建同名空文件代替。

> **为什么要先导出为文件**：日志原本保存在journal中。导出副本后，后续筛选不会修改系统日志，也能反复对同一份输入进行观察。

## 5.2 查看文本文件

### cat：一次输出短文件

```bash
cat /etc/os-release
```

```bash
cat logs/course-ch05.log
```

`cat`适合内容较少、能够在一个屏幕中看完的文件。对数千行日志直接使用`cat`，重要内容会快速滚出屏幕。

显示行号时可使用：

```bash
cat -n logs/course-ch05.log
```

### less：分页查看长文件

```bash
less /etc/services
```

进入`less`后可使用：

| 按键 | 作用 |
|---|---|
| `Space`或`PageDown` | 向下翻页 |
| `b`或`PageUp` | 向上翻页 |
| `/ssh` | 向后搜索`ssh` |
| `n` | 跳到下一个匹配项 |
| `N` | 跳到上一个匹配项 |
| `g`、`G` | 跳到开头、结尾 |
| `q` | 退出 |

`less`只负责查看，不会因为搜索或翻页修改原文件。

### head和tail：查看开头或结尾

```bash
head -n 5 /etc/passwd
```

```bash
tail -n 3 logs/course-ch05.log
```

`head`常用于确认文件格式，`tail`常用于观察日志最新记录。

实时跟踪文件追加内容：

```bash
tail -f logs/course-ch05.log
```

当前导出文件不会自动接收journal的新消息，因此这里主要用于认识`tail -f`的等待状态；按`Ctrl+C`结束。真正跟踪journal可在1.11使用`journalctl -f`。

| 命令 | 适合场景 | 不适合场景 |
|---|---|---|
| `cat` | 短文件一次看完 | 大文件分页阅读 |
| `less` | 长文件分页、搜索 | 把内容交给下一命令 |
| `head` | 快速确认文件开头和字段格式 | 查看最新日志 |
| `tail` | 查看末尾、持续跟踪追加内容 | 阅读文件中间的大段内容 |

## 5.3 使用grep筛选需要的行

`grep`解决的问题是：**哪些行包含我关心的内容？**

基本格式：

```text
grep [选项] '匹配模式' 文件
```

### 从最简单的筛选开始

找出包含`ERROR`的行：

```bash
grep 'ERROR' logs/course-ch05.log
```

同时显示行号：

```bash
grep -n 'ERROR' logs/course-ch05.log
```

忽略大小写：

```bash
grep -ni 'error' logs/course-ch05.log
```

反向筛选，不显示包含`INFO`的行：

```bash
grep -v 'INFO' logs/course-ch05.log
```

只统计匹配行数：

```bash
grep -c 'WARN' logs/course-ch05.log
```

只判断是否存在，不输出匹配内容：

```bash
grep -q 'ERROR' logs/course-ch05.log
```

紧接着查看返回值：

```bash
echo $?
```

`grep`的返回值具有明确含义：

| 返回值 | 含义 |
|---|---|
| `0` | 找到至少一条匹配 |
| `1` | 没找到匹配，这不等于命令损坏 |
| `2` | 文件不存在、选项错误等真正的执行错误 |

再次验证“未找到”的情况：

```bash
grep -q 'FATAL' logs/course-ch05.log
```

```bash
echo $?
```

### 同时匹配多个关键词

`-E`启用扩展正则表达式，竖线`|`表示“或者”：

```bash
grep -nE 'WARN|ERROR' logs/course-ch05.log
```

只匹配完整单词可使用`-w`：

```bash
grep -w 'INFO' logs/course-ch05.log
```

查看匹配行的上下文：

```bash
grep -n -C 1 'ERROR' logs/course-ch05.log
```

其中`-C 1`显示匹配行前后各1行；`-A 2`只显示后2行，`-B 2`只显示前2行。

### 理解最常用的正则表达式

正则表达式描述的是文本特征，不是文件通配符。

| 写法 | 含义 | 示例 |
|---|---|---|
| `^root` | 行首是`root` | 查找root账号记录 |
| `bash$` | 行尾是`bash` | 查找登录Shell为bash的记录 |
| `.` | 任意单个字符 | `r..t`可匹配`root` |
| `[0-9]` | 任意一位数字 | 查找包含数字的行 |
| `*` | 前一个字符出现0次或多次 | `ro*t`可匹配`rt`、`rot`、`root` |
| `WARN\|ERROR` | 基本正则中的“或” | 不使用`-E`时需要转义 |
| `WARN|ERROR` | 扩展正则中的“或” | 需要配合`grep -E` |

查找以`root`开头的账号记录：

```bash
grep '^root:' /etc/passwd
```

查找以`bash`结尾的账号记录：

```bash
grep 'bash$' /etc/passwd
```

查找使用`bash`或`sh`作为登录Shell的账号：

```bash
grep -E '/(ba)?sh$' /etc/passwd
```

模式通常使用单引号，避免`$`、`*`、`|`等字符被Shell提前解释。

### 在目录中递归查找内容

`grep`找的是**文件内容**，不是文件名：

```bash
grep -RIn 'service=' ~/course-practice/m1/ch05
```

| 选项 | 作用 |
|---|---|
| `-R` | 递归读取目录中的文件 |
| `-I` | 忽略二进制文件 |
| `-n` | 显示行号 |
| `-i` | 忽略大小写 |
| `-v` | 反向选择 |
| `-w` | 匹配完整单词 |
| `-c` | 只输出匹配行数 |
| `-q` | 静默，只用返回值表示是否匹配 |
| `-E` | 使用扩展正则表达式 |

## 5.4 使用wc统计数量

`wc`解决的问题是：**一共有多少？**

```bash
wc logs/course-ch05.log
```

未指定选项时，依次显示行数、单词数、字节数和文件名。

```bash
wc -l logs/course-ch05.log
```

```bash
wc -w logs/course-ch05.log
```

```bash
wc -c logs/course-ch05.log
```

```bash
wc -m logs/course-ch05.log
```

| 选项 | 统计内容 |
|---|---|
| `-l` | 换行符数量，通常理解为行数 |
| `-w` | 由空白分隔的单词数量 |
| `-c` | 字节数量 |
| `-m` | 字符数量；包含中文时可能与字节数不同 |

### 先筛选，再统计

先只看异常日志：

```bash
grep -E 'WARN|ERROR' logs/course-ch05.log
```

确认筛选正确后，再统计异常行数：

```bash
grep -E 'WARN|ERROR' logs/course-ch05.log | wc -l
```

这条管道可以从左向右读成：“读取日志 → 保留WARN或ERROR行 → 统计保留下来的行数”。

`grep -c`也能统计匹配行，但两种写法关注点不同：

- `grep -c 'ERROR' 文件`：由`grep`直接报告该文件的匹配行数；
- `前一命令 | wc -l`：统计任何前一命令输出了多少行，更通用。

## 5.5 使用cut、sort和uniq整理结果

这三个命令各自只做一件事：

- `cut`：按分隔符取字段；
- `sort`：把行排成指定顺序；
- `uniq`：合并**相邻**的重复行。

### cut：从账号文件中提取字段

`/etc/passwd`每行使用冒号分隔。先查看前3行：

```bash
head -n 3 /etc/passwd
```

第1字段是用户名，第7字段是登录Shell。只提取用户名：

```bash
cut -d: -f1 /etc/passwd
```

只提取登录Shell：

```bash
cut -d: -f7 /etc/passwd
```

同时提取用户名和Shell：

```bash
cut -d: -f1,7 /etc/passwd
```

`-d:`指定冒号为分隔符，`-f1,7`选择第1和第7字段。`cut`适合分隔符明确的文本，不适合列宽不固定且连续空格较多的`ps aux`输出。

### sort：按字符或数字排序

对Shell路径按字符排序：

```bash
cut -d: -f7 /etc/passwd | sort
```

`sort`默认按字符顺序。处理数字时应明确使用`-n`：

```bash
find ~/course-practice/m1/ch05 -type f -printf '%s %p\n' | sort -n
```

按文件字节数从大到小排列：

```bash
find ~/course-practice/m1/ch05 -type f -printf '%s %p\n' | sort -nr
```

常用选项：

| 选项 | 作用 |
|---|---|
| `-n` | 按数值而不是字符排序 |
| `-r` | 反向排序 |
| `-h` | 识别`K`、`M`、`G`等易读单位 |
| `-u` | 排序并去除重复行 |
| `-t:` | 指定字段分隔符为冒号 |
| `-k2,2` | 以第2字段为排序键 |

### uniq：先让重复项相邻

直接执行：

```bash
cut -d: -f7 /etc/passwd | uniq -c
```

这个结果不一定正确统计全部Shell，因为`uniq`只能识别相邻重复行。先排序，再计数：

```bash
cut -d: -f7 /etc/passwd | sort | uniq -c
```

最后按出现次数从多到少排列：

```bash
cut -d: -f7 /etc/passwd | sort | uniq -c | sort -nr
```

不要急着背整条命令。它是四个可以单独验证的步骤：

1. `cut`提取Shell字段；
2. 第一个`sort`让相同Shell相邻；
3. `uniq -c`统计相邻重复项；
4. `sort -nr`按次数倒序。

### 对真实日志统计级别分布

日志第1字段是级别。先确认字段结构：

```bash
head -n 3 logs/course-ch05.log
```

提取第1字段：

```bash
cut -d' ' -f1 logs/course-ch05.log
```

排序并计数：

```bash
cut -d' ' -f1 logs/course-ch05.log | sort | uniq -c
```

按次数倒序：

```bash
cut -d' ' -f1 logs/course-ch05.log | sort | uniq -c | sort -nr
```

## 5.6 使用find查找文件系统对象

`grep`按**内容**找行，`find`按**名称、类型、大小、时间、所有者等属性**找文件系统对象。不要把两者混淆。

基本结构：

```text
find 起点 查找条件 输出或操作
```

例如：

```bash
find ~/course-practice/m1/ch05 -type f -name '*.log' -print
```

- 起点：`~/course-practice/m1/ch05`；
- 条件：普通文件，并且名称以`.log`结尾；
- 动作：`-print`输出路径。

### 按名称和类型查找

```bash
find /etc -maxdepth 2 -type f -name '*.conf'
```

```bash
find ~/course-practice/m1/ch05 -type d -print
```

```bash
find ~/course-practice/m1/ch05 -type l -print
```

`'*.conf'`必须加引号。加引号后，通配符由`find`处理；不加引号时，Shell可能在`find`启动前就把它展开，导致结果错误。

### 按大小查找

列出本章所有非空普通文件：

```bash
find ~/course-practice/m1/ch05 -type f -size +0c -printf '%s %p\n'
```

`c`表示字节。查找大于10MiB的文件：

```bash
find /var -type f -size +10M 2>/dev/null
```

`+10M`表示大于，`-10M`表示小于，`10M`表示按find的单位规则等于相应大小范围。

### 按修改时间查找

```bash
find ~/course-practice/m1/ch05 -type f -mmin -30 -print
```

`-mmin -30`表示最近30分钟内修改。按天计算时：

```bash
find /tmp -type f -mtime -1 -print
```

`-mtime -1`表示不足24小时，`-mtime +7`表示超过7个完整的24小时。结果为空不一定是命令失败，可能只是没有对象满足条件。

### 按所有者、权限和空文件查找

```bash
find ~/course-practice/m1/ch05 -user "$USER" -type f -print
```

```bash
find ~/course-practice/m1/ch05 -type f -empty -print
```

```bash
find ~/course-practice/m1/ch05 -type f -perm /002 -print
```

最后一条查找“其他用户具有写权限”的普通文件。权限条件将在1.8进一步学习。

### 组合多个条件

相邻条件默认是“并且”：

```bash
find ~/course-practice/m1/ch05 -type f -name '*.log' -size +0c -print
```

使用`-o`表示“或者”。括号需要转义，防止Shell解释：

```bash
find /etc -maxdepth 2 -type f \( -name '*.conf' -o -name '*.service' \) -print
```

### 控制输出格式

```bash
find ~/course-practice/m1/ch05 -type f -printf '%TY-%Tm-%Td %TH:%TM %s %p\n'
```

常用格式符：

| 格式符 | 含义 |
|---|---|
| `%p` | 完整路径 |
| `%f` | 文件名 |
| `%s` | 字节数 |
| `%u` | 所有者 |
| `%m` | 八进制权限 |
| `%TY-%Tm-%Td` | 修改日期 |

`-printf`是GNU find常用能力，Rocky Linux和Ubuntu均可使用。

### 对查找结果执行命令

先只打印，确认范围：

```bash
find ~/course-practice/m1/ch05 -type f -name '*.log' -print
```

确认无误后，再查看详细信息：

```bash
find ~/course-practice/m1/ch05 -type f -name '*.log' -exec ls -lh {} \;
```

`{}`代表当前找到的路径，`\;`表示每找到一个文件执行一次。若命令支持多个路径，可以用`+`批量执行，效率更高：

```bash
find ~/course-practice/m1/ch05 -type f -name '*.log' -exec ls -lh {} +
```

不要在尚未检查范围时把`-print`直接换成`-delete`或`-exec rm`。运维中的安全顺序是“先查找、再核对、后操作”。

### find常用条件汇总

| 条件 | 含义 |
|---|---|
| `-name '*.conf'` | 按名称，区分大小写 |
| `-iname '*.CONF'` | 按名称，不区分大小写 |
| `-type f`、`d`、`l` | 普通文件、目录、符号链接 |
| `-size +10M` | 大于10MiB |
| `-mmin -30` | 最近30分钟修改 |
| `-mtime +7` | 超过7个完整的24小时未修改 |
| `-user USER` | 所有者为指定用户 |
| `-empty` | 空文件或空目录 |
| `-maxdepth 2` | 最多向下搜索2层 |

## 5.7 管道、标准流与重定向

每个Linux进程通常具有三个标准流：

| 编号 | 名称 | 默认位置 |
|---|---|---|
| `0` | 标准输入stdin | 键盘 |
| `1` | 标准输出stdout | 终端 |
| `2` | 标准错误stderr | 终端 |

管道`|`只把左侧命令的**标准输出**交给右侧命令的标准输入。标准错误不会自动进入管道。

### 用逐级缩小范围的方法构造管道

第一步，查看全部日志：

```bash
cat logs/course-ch05.log
```

第二步，只保留异常：

```bash
grep -E 'WARN|ERROR' logs/course-ch05.log
```

第三步，只取异常级别：

```bash
grep -E 'WARN|ERROR' logs/course-ch05.log | cut -d' ' -f1
```

第四步，统计不同异常级别：

```bash
grep -E 'WARN|ERROR' logs/course-ch05.log | cut -d' ' -f1 | sort | uniq -c
```

第五步，按次数倒序：

```bash
grep -E 'WARN|ERROR' logs/course-ch05.log | cut -d' ' -f1 | sort | uniq -c | sort -nr
```

如果最终结果不对，应从第一步开始检查是哪一级首次出现偏差，而不是盲目修改整条命令。

### 把输出保存到文件

覆盖写入：

```bash
grep -E 'WARN|ERROR' logs/course-ch05.log > evidence/abnormal.log
```

查看保存结果：

```bash
cat evidence/abnormal.log
```

追加写入：

```bash
date >> evidence/abnormal.log
```

`>`会先清空目标文件，`>>`保留原内容并在末尾追加。执行前必须确认目标路径。

### 同时显示并保存：tee

```bash
grep -E 'WARN|ERROR' logs/course-ch05.log | tee evidence/abnormal.log
```

`tee`把输入同时写到屏幕和文件。追加模式使用：

```bash
date | tee -a evidence/abnormal.log
```

### 单独处理错误输出

故意访问不存在的路径：

```bash
ls /not-exist
```

只保存错误：

```bash
ls /not-exist 2> logs/command-error.log
```

```bash
cat logs/command-error.log
```

丢弃查找时的权限错误：

```bash
find /var -type f -size +10M 2>/dev/null
```

把标准输出和标准错误保存到同一文件：

```bash
find /var -type f -size +10M > docs/large-files.txt 2>&1
```

| 符号 | 作用 |
|---|---|
| `|` | 把前一命令的标准输出交给后一命令 |
| `>` | 覆盖标准输出到文件 |
| `>>` | 追加标准输出到文件 |
| `2>` | 覆盖标准错误到文件 |
| `2>>` | 追加标准错误到文件 |
| `2>&1` | 让标准错误去往当前标准输出的位置 |
| `tee FILE` | 屏幕显示的同时覆盖写入文件 |
| `tee -a FILE` | 屏幕显示的同时追加写入文件 |

> **注意**：管道默认只报告最后一个命令的退出状态。Shell脚本中的`set -o pipefail`会在模块四系统学习，本章先通过逐级执行检查每一步。

## 5.8 查找命令位置

文件查找和命令查找不是同一件事：

```bash
type ls
```

```bash
type cd
```

```bash
command -v grep
```

```bash
which grep
```

```bash
whereis grep
```

- `type`能识别别名、函数、Shell内建命令和外部命令；
- `command -v`适合确认Shell将执行哪个命令，也适合脚本检查依赖；
- `which`通常在`PATH`中查找可执行文件；
- `whereis`可能同时显示程序、源码和手册位置；
- `find`从指定目录递归查找文件系统对象，范围和用途完全不同。

## 5.9 inode与链接

目录中保存“文件名到inode”的对应关系。inode记录文件类型、权限、所有者、时间和数据块位置等元数据，但不保存文件名本身。

继续打开[Linux目录树、路径与链接动画](../animations/02-linux-filesystem-paths-links/index.html)的“inode与链接”主题，先预测创建硬链接、创建软链接和删除原文件后的inode与可读性，再执行真实命令。

清理本章上一次链接练习残留：

```bash
rm -f ~/course-practice/m1/ch05/data/link-lab/origin.txt
```

```bash
rm -f ~/course-practice/m1/ch05/data/link-lab/hard-link.txt
```

```bash
rm -f ~/course-practice/m1/ch05/data/link-lab/soft-link.txt
```

创建原文件：

```bash
echo 'important practice data' > ~/course-practice/m1/ch05/data/link-lab/origin.txt
```

```bash
ls -li ~/course-practice/m1/ch05/data/link-lab/origin.txt
```

创建硬链接：

```bash
ln ~/course-practice/m1/ch05/data/link-lab/origin.txt ~/course-practice/m1/ch05/data/link-lab/hard-link.txt
```

创建相对路径符号链接：

```bash
ln -s origin.txt ~/course-practice/m1/ch05/data/link-lab/soft-link.txt
```

```bash
ls -li ~/course-practice/m1/ch05/data/link-lab/*.txt
```

| 特性 | 硬链接 | 符号链接 |
|---|---|---|
| inode | 与原文件相同 | 拥有自己的inode |
| 保存内容 | 同一inode的另一个名称 | 目标路径字符串 |
| 跨文件系统 | 通常不可以 | 可以 |
| 链接目录 | 普通用户通常不可以 | 可以 |
| 删除原文件名后 | 数据仍可访问 | 链接失效 |

删除原文件名：

```bash
rm ~/course-practice/m1/ch05/data/link-lab/origin.txt
```

验证硬链接：

```bash
cat ~/course-practice/m1/ch05/data/link-lab/hard-link.txt
```

验证符号链接：

```bash
cat ~/course-practice/m1/ch05/data/link-lab/soft-link.txt
```

最后一条预期报告“没有那个文件或目录”。这不是实验失败，而是软链接目标已经消失。硬链接不能替代备份，因为它仍然指向同一份数据块；内容被误改时，所有硬链接读到的都是修改后的内容。

## 5.10 综合任务

### 本章短练习：提交真实日志与文件审计结果

### 任务情境

运维人员需要提交一份主机基础审计证据，回答以下问题：

1. 本次课程日志中有哪些WARN和ERROR？
2. WARN与ERROR各有多少条？
3. 当前主机使用了哪些登录Shell，各有多少账号？
4. `/etc`前两层中有哪些`.conf`文件？
5. 本章练习目录中哪些文件最大？

所有结果必须来自真实命令，不手工填写统计数字。

### 步骤1：再次确认输入

```bash
test -s ~/course-practice/m1/ch05/logs/course-ch05.log
```

```bash
echo $?
```

只有返回`0`才继续。

### 步骤2：保存异常日志

先在屏幕验证：

```bash
grep -nE 'WARN|ERROR' ~/course-practice/m1/ch05/logs/course-ch05.log
```

再显示并保存：

```bash
grep -nE 'WARN|ERROR' ~/course-practice/m1/ch05/logs/course-ch05.log | tee ~/course-practice/m1/ch05/evidence/abnormal-lines.txt
```

### 步骤3：统计异常级别

先验证提取结果：

```bash
grep -E 'WARN|ERROR' ~/course-practice/m1/ch05/logs/course-ch05.log | cut -d' ' -f1
```

再完成排序、计数和保存：

```bash
grep -E 'WARN|ERROR' ~/course-practice/m1/ch05/logs/course-ch05.log | cut -d' ' -f1 | sort | uniq -c | sort -nr | tee ~/course-practice/m1/ch05/evidence/abnormal-count.txt
```

### 步骤4：统计账号Shell

先确认字段：

```bash
cut -d: -f7 /etc/passwd | sort | uniq -c
```

再排序并保存：

```bash
cut -d: -f7 /etc/passwd | sort | uniq -c | sort -nr | tee ~/course-practice/m1/ch05/evidence/login-shell-count.txt
```

### 步骤5：查找配置文件

先确认范围：

```bash
find /etc -maxdepth 2 -type f -name '*.conf' 2>/dev/null
```

排序、取前20项并保存：

```bash
find /etc -maxdepth 2 -type f -name '*.conf' 2>/dev/null | sort | head -n 20 | tee ~/course-practice/m1/ch05/evidence/etc-conf-top20.txt
```

### 步骤6：按大小审计本章文件

先输出字节数和路径：

```bash
find ~/course-practice/m1/ch05 -type f -printf '%s %p\n'
```

按数字倒序并保存：

```bash
find ~/course-practice/m1/ch05 -type f ! -name 'ch05-files-by-size.txt' -printf '%s %p\n' | sort -nr | tee ~/course-practice/m1/ch05/evidence/ch05-files-by-size.txt
```

### 验收

```bash
find ~/course-practice/m1/ch05/evidence -maxdepth 1 -type f -size +0c -printf '%f\n' | sort
```

应至少看到：

- `abnormal-lines.txt`；
- `abnormal-count.txt`；
- `login-shell-count.txt`；
- `etc-conf-top20.txt`；
- `ch05-files-by-size.txt`。

随机抽查证据内容：

```bash
cat ~/course-practice/m1/ch05/evidence/abnormal-count.txt
```

```bash
head -n 5 ~/course-practice/m1/ch05/evidence/etc-conf-top20.txt
```

### 思考题

1. 为什么`uniq -c`之前通常需要`sort`？
2. 为什么`grep -c`和`grep | wc -l`都能统计，但适用范围不同？
3. 为什么`find -name '*.conf'`中的通配符需要单引号？
4. 为什么`2>/dev/null`只隐藏错误，不能解决权限问题本身？
5. 如果一个长管道结果错误，为什么应逐级查看中间结果？

## 实验衔接：实验3前半部分

实验3继续使用实验2保留的`~/m1-project`，对真实项目配置和日志执行内容筛选、数量统计、属性查找与证据保存，然后完成链接、归档和恢复。本章目录用于方法练习，实验3目录用于项目成果，二者不要混用。

---

# 第6章 vim与归档恢复

### 操作素材准备

本章不修改实验2的正式项目。先只建立章节目录，不提前用大段Shell命令生成练习内容：

```bash
mkdir -p ~/course-practice/m1/ch06
mkdir ~/course-practice/m1/ch06/config
mkdir ~/course-practice/m1/ch06/backup
mkdir ~/course-practice/m1/ch06/docs
```

说明文件和配置文件将在掌握vim最小操作闭环后逐个创建。

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

第一次使用vim时，只要求掌握“按`i`输入、按`Esc`返回、输入`:wq`保存退出”这一最小闭环。然后用vim逐个创建`README.md`和`config/app.conf`，不要使用尚未学习的多行Shell重定向代替编辑过程。文件正文和逐条步骤以学习通分章教材1.6为准。

搜索替换：

```vim
/keyword
n
:%s/old/new/g
```

编辑配置文件前先备份。项目配置使用时间戳保留修改前版本：

```bash
cp -a ~/course-practice/m1/ch06/config/app.conf \
  ~/course-practice/m1/ch06/backup/app.conf.before-vim.$(date +%F-%H%M%S)
vim ~/course-practice/m1/ch06/config/app.conf
```

## 6.3 归档与压缩

归档是把多个文件组合成一个文件，压缩是减少数据体积。`tar`常把两者结合：

```bash
archive="$HOME/course-practice/m1/ch06-$(date +%F-%H%M%S).tar.gz"
restore_dir=$(mktemp -d "$HOME/course-practice/m1/ch06-restore.XXXXXX")
printf '%s\n' "$archive" > ~/course-practice/m1/ch06/docs/last-archive.txt
printf '%s\n' "$restore_dir" > ~/course-practice/m1/ch06/docs/last-restore-dir.txt
tar -C "$HOME/course-practice/m1" -czf "$archive" ch06
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
archive=$(cat ~/course-practice/m1/ch06/docs/last-archive.txt)
restore_dir=$(cat ~/course-practice/m1/ch06/docs/last-restore-dir.txt)
tar -tzf "$archive" | head
tar -xzf "$archive" -C "$restore_dir"
find "$restore_dir" -maxdepth 3 -print
```

不要盲目以root身份解开来源不明的归档文件。归档中可能包含绝对路径、特殊权限或覆盖目标文件的内容。

## 6.4 zip与unzip（拓展阅读）

ZIP主要用于与Windows用户交换文件。本章只要求识别`zip -r`、`unzip -l`和`unzip -d`，不作为实验3必做内容；课堂实操优先完成tar归档、隔离恢复和内容比较。

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
restore_dir=$(cat ~/course-practice/m1/ch06/docs/last-restore-dir.txt)
diff -ru "$HOME/course-practice/m1/ch06" "$restore_dir/ch06"
```

归档路径和恢复目录分别记录在练习目录的`docs`中，因此重新登录后也可以继续验证。示例使用`tar -C`归档相对路径，恢复结果不依赖具体用户名。

### 本章短练习：修改配置并完成恢复验证

项目工单要求：

1. 使用vim把`README.md`中的状态改为“基础文件已整理”。
2. 使用vim完成`docs/directory-plan.md`，写出三个子目录的用途。
3. 修改完成后重新创建一份新归档，不复用6.3节修改前的演示归档。
4. 把新归档恢复到新的空目录，使用`diff -ru`验证。

完成第1—2项后执行下面的交付命令：

```bash
archive="$HOME/course-practice/m1/ch06-final-$(date +%F-%H%M%S).tar.gz"
restore_dir=$(mktemp -d "$HOME/course-practice/m1/ch06-final-restore.XXXXXX")
printf '%s\n' "$archive" > ~/course-practice/m1/ch06/docs/last-archive.txt
printf '%s\n' "$restore_dir" > ~/course-practice/m1/ch06/docs/last-restore-dir.txt
tar -C "$HOME/course-practice/m1" -czf "$archive" ch06
tar -tzf "$archive" | sed -n '1,30p'
tar -xzf "$archive" -C "$restore_dir"
```

`diff`无输出且退出状态为0，表示当前项目内容与恢复内容一致。

完成后检查：

```bash
test -s ~/course-practice/m1/ch06/docs/initialization-record.md
archive=$(cat ~/course-practice/m1/ch06/docs/last-archive.txt)
test -s "$archive"
restore_dir=$(cat ~/course-practice/m1/ch06/docs/last-restore-dir.txt)
diff -ru "$HOME/course-practice/m1/ch06" "$restore_dir/ch06"
echo "restore_compare=$?"
```

`restore_compare=0`才表示当前练习目录和恢复目录一致。

### 实验衔接：实验3

实验3会检查实验2创建的`~/m1-project/config/app.conf`。进入实验前先执行实验3的起点检查；文件缺失时恢复实验2成果，不使用本章`ch06`练习文件冒充正式项目文件。

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

交互观察：打开[Linux身份与权限判定动画](../animations/03-linux-permissions/index.html)的“身份与匹配”主题。分别代入`dev01`、`dev02`和`auditor`，先判断内核会选择owner、group还是other，再继续学习账号文件与管理命令。

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

下面是用户管理命令的语法示例。它们会改变系统账号，不属于本章短练习；真实项目账号统一在实验4中创建。

```bash
sudo useradd -m -s /bin/bash demo-user
sudo passwd demo-user
sudo usermod -c "Demo User" demo-user
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

下面的命令接续上一节假设的`demo-user`，用于说明组管理语法，不应在没有该账号时直接执行：

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

如果为了额外练习而实际创建了`demo-user`和`web-team`，检查无误后再清理；未创建则跳过：

```bash
ps -u demo-user
sudo find / -xdev -user demo-user 2>/dev/null
sudo userdel -r demo-user
sudo groupdel web-team
```

### 本章短练习：读取身份并设计账号矩阵

本练习不创建系统账号。先建立独立练习目录并保存当前身份信息：

```bash
mkdir -p ~/course-practice/m1/ch07
{
    printf 'current_user=%s\n' "$(whoami)"
    id
    getent passwd "$(whoami)"
    getent group "$(id -gn)"
} > ~/course-practice/m1/ch07/current-identity.txt
```

然后使用vim创建`~/course-practice/m1/ch07/account-plan.md`，按下表写出四类账号的职责、组要求和禁止事项：

项目需要四类角色：

| 账号 | 职责 | 组要求 |
|---|---|---|
| `dev01` | 开发人员，创建并维护项目文件 | 加入`project-dev` |
| `dev02` | 开发人员，协作修改项目文件 | 加入`project-dev` |
| `auditor` | 审计人员，只读查看项目文件 | 后续加入`project-audit` |
| `juniorops` | 初级运维人员，只能执行获批的管理命令 | 不加入`wheel` |

账号设计必须满足：一人一账号、不共享root密码；开发、审计和初级运维权限彼此分离；所有创建结果都能用`id`和`getent`验证。

```bash
test -s ~/course-practice/m1/ch07/current-identity.txt
test -s ~/course-practice/m1/ch07/account-plan.md
grep -E 'dev01|dev02|auditor|juniorops' \
  ~/course-practice/m1/ch07/account-plan.md
```

验收时应能解释UID与用户名、GID与组名、主组与附加组的区别，并指出为什么`juniorops`不能加入`wheel`。

### 实验衔接：实验4任务一

进入实验4后，根据本章账号矩阵创建`project-dev`、`dev01`、`dev02`、`auditor`和`juniorops`，并以实验手册中的起点检查、创建顺序和验收命令为准。不要在教材练习中提前创建同名账号。

---

# 第8章 文件权限与共享目录

## 8.1 rwx权限模型

实验4要求在`/srv/course-share`建立协作目录：`dev01`和`dev02`可以协作，`auditor`只读，`juniorops`无权访问。先学会读取一个文件的传统权限。下面是实验完成后可能看到的输出示例，不要求此时已经存在该文件：

```text
-rw-rw-r-- 1 dev01 project-dev 11 Jul 5 10:00 project.conf
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

继续使用[Linux身份与权限判定动画](../animations/03-linux-permissions/index.html)的“文件/目录rwx”“chmod与umask”和“共享目录”主题。动画中的判断必须在后续练习或实验4中通过真实账号、`stat`、`namei -l`和退出码验证。

## 8.3 chmod数字法

```text
r = 4
w = 2
x = 1
```

### 操作素材准备

下面的对象全部位于个人练习目录中。命令会创建输入文件并统一设置初始权限，可以按顺序执行：

```bash
mkdir -p ~/course-practice/m1/ch08/public-dir
printf 'token=practice-only\n' > ~/course-practice/m1/ch08/private.txt
printf 'listen=8080\n' > ~/course-practice/m1/ch08/config.ini
printf '<h1>status</h1>\n' > ~/course-practice/m1/ch08/index.html
printf '#!/bin/bash\necho permission-check\n' > ~/course-practice/m1/ch08/check.sh

chmod 600 ~/course-practice/m1/ch08/private.txt
chmod 640 ~/course-practice/m1/ch08/config.ini
chmod 644 ~/course-practice/m1/ch08/index.html
chmod 750 ~/course-practice/m1/ch08/check.sh
chmod 755 ~/course-practice/m1/ch08/public-dir
ls -l ~/course-practice/m1/ch08
```

不要用`chmod 777`掩盖权限设计问题。权限过宽会让无关用户修改程序、配置或数据。

## 8.4 chmod符号法

```bash
touch ~/course-practice/m1/ch08/shared.txt \
  ~/course-practice/m1/ch08/secret.txt
chmod u-x ~/course-practice/m1/ch08/check.sh
stat -c '%A %a %n' ~/course-practice/m1/ch08/check.sh
chmod u+x ~/course-practice/m1/ch08/check.sh
chmod g+w ~/course-practice/m1/ch08/shared.txt
chmod o-r ~/course-practice/m1/ch08/secret.txt
chmod u=rw,g=r,o= ~/course-practice/m1/ch08/config.ini
stat -c '%A %a %n' ~/course-practice/m1/ch08/{check.sh,shared.txt,secret.txt,config.ini}
```

对象：`u`所有者、`g`组、`o`其他、`a`全部。

## 8.5 所有者与所属组

`chown`和`chgrp`的基本格式如下。中文词表示需要替换的参数，不能原样执行。真实项目文件的所有者和组由实验4设置；不要对不明来源的系统目录递归执行这些命令。

```text
chown 用户名 文件
chgrp 组名 文件
chown 用户名:组名 文件
```

递归修改前使用`find`或`ls -lR`确认范围，避免把系统目录所有者整体改错。

## 8.6 umask

新文件通常从基础模式`666`屏蔽权限，新目录通常从`777`屏蔽权限。严格来说是按位屏蔽，不应把所有情况理解为普通算术减法。

```bash
old_umask=$(umask)
echo "old_umask=$old_umask"
umask 0022
touch ~/course-practice/m1/ch08/umask-file
mkdir -p ~/course-practice/m1/ch08/umask-dir
ls -ld ~/course-practice/m1/ch08/umask-file \
  ~/course-practice/m1/ch08/umask-dir
umask "$old_umask"
```

常见结果：

| umask | 新文件 | 新目录 | 场景 |
|---|---|---|---|
| `0022` | `644` | `755` | 普通共享读取 |
| `0002` | `664` | `775` | 同组协作 |
| `0077` | `600` | `700` | 私密数据 |

### 本章短练习：预测并验证个人目录权限

完成前面的`ch08`对象准备后，先不要再次执行`chmod`，在纸面或`permission-plan.md`中预测以下权限：

1. `private.txt`为什么应为`600`。
2. `config.ini`的所有者、所属组、其他用户分别能做什么。
3. `check.sh`为什么需要执行位，而普通配置文件通常不需要。
4. 在`umask 0022`下，新文件和新目录通常得到什么权限。

然后执行并核对实际结果：

```bash
stat -c '%A %a %U:%G %n' ~/course-practice/m1/ch08/*
test "$(stat -c %a ~/course-practice/m1/ch08/private.txt)" = 600
echo "private_mode_check=$?"
test -x ~/course-practice/m1/ch08/check.sh
echo "script_execute_check=$?"
```

两个检查结果都应为0。若预测与实际结果不同，应根据文件/目录语义以及u、g、o三组权限重新解释，而不是改成`777`。

## 8.7 特殊权限

本节的SGID、Sticky bit和ACL需要多个真实账号共同验证，属于实验4内容。先理解设计目标和命令含义，再进入实验执行；不要在本章短练习中提前创建`/srv/course-share`。

### SGID目录

目录设置SGID后，其中新建文件通常继承目录所属组：

```bash
sudo chown root:project-dev /srv/course-share
sudo chmod 2770 /srv/course-share
ls -ld /srv/course-share
```

### Sticky bit

在多人可写目录中，Sticky bit限制用户删除其他用户拥有的文件：

```bash
sudo chmod 3770 /srv/course-share
```

这里`3`同时包含SGID（2）和Sticky（1）。

### ACL

传统权限只能表达“所有者、所属组、其他用户”三类权限。当同一目录同时需要“开发组可写、审计组只读、其他用户禁止访问”时，可以使用ACL增加更细的访问规则：

```bash
command -v setfacl || sudo dnf install -y acl
sudo groupadd project-audit
sudo usermod -aG project-audit auditor
sudo setfacl -m g:project-audit:rx /srv/course-share
sudo setfacl -m g:project-audit:r-- /srv/course-share/project.conf
getfacl /srv/course-share /srv/course-share/project.conf
```

ACL输出中的`group:project-audit`表示额外授予审计组权限。设置ACL后仍要用实际账号验证，不能只看配置文件。

该规则只覆盖当前目录和已经存在的`project.conf`，不会自动应用到以后新建的文件。实验4只验收审计员对当前项目配置的只读访问；默认ACL作为课后拓展，不占用本次4课时实验。

### SUID

SUID可使可执行文件以文件所有者的有效身份运行，风险较高。本模块只要求识别：

```bash
find /usr/bin -perm -4000 -type f 2>/dev/null
```

不要随意给自编程序设置SUID。

## 8.8 实验衔接：实验4任务二至五

实验4会先创建账号和共享目录，再按以下思路完成跨账号验证。下面的命令依赖实验4已经创建的对象，只在实验4对应步骤执行：

```bash
sudo chown root:project-dev /srv/course-share
sudo chmod 3770 /srv/course-share

sudo -u dev01 bash -c \
  'umask 0002; echo dev01 > /srv/course-share/dev01.txt'
sudo -u dev02 bash -c \
  'umask 0002; echo dev02 > /srv/course-share/dev02.txt'
ls -l /srv/course-share

sudo -u dev02 cat /srv/course-share/dev01.txt
sudo -u dev02 rm /srv/course-share/dev01.txt
sudo -u auditor cat /srv/course-share/project.conf
sudo -u juniorops cat /srv/course-share/project.conf
```

`dev02`删除`dev01.txt`应因Sticky bit而失败；`auditor`读取`project.conf`应成功；`juniorops`读取`project.conf`应失败。验证权限时必须切换到实际目标用户，不能只看`ls -l`后凭感觉判断。

### 权限排障顺序

```text
确认当前身份id
→ 检查路径每一级目录的x权限
→ 检查目标对象rwx
→ 检查所有者和组
→ 检查ACL或特殊权限
→ 后续再检查SELinux
```

### 实验4验收要点

- `ls -ld /srv/course-share`显示组为`project-dev`，并具有SGID和Sticky bit。
- `dev01`和`dev02`都能创建文件。
- 新文件自动继承`project-dev`组。
- `dev02`可以读取团队文件，但不能删除`dev01`拥有的文件。
- `auditor`通过ACL只读访问，`juniorops`不能访问项目共享目录。

```bash
ls -ld /srv/course-share
find /srv/course-share -maxdepth 1 -printf '%M %u:%g %p\n'
getfacl /srv/course-share /srv/course-share/project.conf
sudo -u dev01 test -w /srv/course-share && echo 'dev01 can write'
sudo -u dev02 test -w /srv/course-share && echo 'dev02 can write'
sudo -u auditor test -r /srv/course-share/project.conf && echo 'auditor can read'
sudo -u juniorops test -r /srv/course-share/project.conf || echo 'juniorops cannot read'
```

`/srv/course-share`、`dev01`、`dev02`、`auditor`、`juniorops`、`project-dev`和`project-audit`都由实验4创建并作为贯穿项目资产保留。若这些对象不存在，应回到实验4的起点检查和任务一，不能只创建一个同名空目录绕过依赖。

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

以上两条是命令格式，不要把中文占位符直接复制到终端。本项目不能把`juniorops`加入`wheel`或`sudo`组，否则它会获得通用管理权限，无法验证最小授权。

## 9.3 使用visudo

不要用普通编辑器直接修改`/etc/sudoers`。`visudo`退出前会检查语法：

```bash
sudo visudo -c
```

### 本章短练习：编写最小授权草案

假设`juniorops`需要查询系统已有的chronyd服务是否正在运行，但不允许查看任意服务详情、重启服务、创建用户、安装软件或执行任意root命令。本练习只在个人目录编写草案，不修改`/etc/sudoers.d/`。

```bash
mkdir -p ~/course-practice/m1/ch09
command -v systemctl
printf '%s\n' \
  'juniorops ALL=(root) NOPASSWD: /usr/bin/systemctl is-active chronyd' \
  > ~/course-practice/m1/ch09/course-juniorops.draft
cat ~/course-practice/m1/ch09/course-juniorops.draft
```

草案使用绝对命令路径，是因为sudo要匹配被授权的具体程序。若`command -v systemctl`显示的路径不同，应将草案中的路径改为实际结果。回答下面三个问题：

1. 规则中的主体用户、目标身份、程序和参数分别是什么？
2. 为什么不能把`is-active chronyd`放宽成任意参数？
3. 为什么不能直接授予`ALL`？

检查草案非空且只包含一条授权规则：

```bash
test -s ~/course-practice/m1/ch09/course-juniorops.draft
echo "draft_nonempty_check=$?"
wc -l ~/course-practice/m1/ch09/course-juniorops.draft
```

`draft_nonempty_check=0`且`wc -l`结果为1，表示练习对象完整；它还不代表sudoers语法已经通过系统检查。

### 实验衔接：实验4任务六

实验4会在账号已存在的前提下，使用`sudo visudo -f /etc/sudoers.d/course-juniorops`写入正式规则，再设置`440`权限并执行语法、允许和拒绝测试。以下是实验中需要形成的验证闭环：

```bash
sudo visudo -cf /etc/sudoers.d/course-juniorops
sudo -l -U juniorops
sudo -u juniorops sudo /usr/bin/systemctl is-active chronyd
sudo -u juniorops sudo /usr/bin/systemctl restart chronyd
printf 'restart_exit_code=%s\n' "$?"
```

Rocky Linux 9课程镜像中的chronyd预期为`active`；若不是，应先排查服务基线，不能把服务故障误判为sudo授权故障。`restart chronyd`必须被sudo拒绝。

## 9.4 NOPASSWD风险

```sudoers
juniorops ALL=(root) NOPASSWD: /usr/bin/systemctl restart chronyd
```

`NOPASSWD`适合明确且受控的自动化命令，但会降低再次认证保护。不要写成：

```sudoers
juniorops ALL=(ALL) NOPASSWD: ALL
```

## 9.5 sudo日志

```bash
sudo journalctl _COMM=sudo --since today
if [[ -f /var/log/secure ]]; then
  sudo grep sudo /var/log/secure | tail
fi
```

不同发行版日志位置可能不同。Ubuntu认证日志常见于`/var/log/auth.log`。

### 实验4验收要点

- [ ] `juniorops`只能查询Nginx是否运行，不能重启服务。
- [ ] sudoers独立文件语法检查通过。
- [ ] 未授权命令被拒绝。
- [ ] 能从日志中找到sudo操作记录。

`juniorops`、`project-dev`、`project-audit`、`/srv/course-share`和sudoers文件都是实验4创建的模块综合交付对象。保存证据的命令也在实验4中执行，不在本章短练习中提前写入正式项目：

```bash
sudo -l -U juniorops > ~/m1-project/docs/juniorops-sudo.txt
sudo visudo -cf /etc/sudoers.d/course-juniorops
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
dnf history
```

全系统升级命令为`sudo dnf upgrade`，本课程只要求识别，不在普通课堂实验中统一执行。

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

`apt update`只更新本地软件索引，不等于升级已安装软件。全系统升级命令为`sudo apt upgrade`，本课程只要求识别，不在普通课堂实验中统一执行。

Ubuntu 22.04 Desktop的软件源通常位于`/etc/apt/sources.list`，APT操作记录可在`/var/log/dpkg.log`等位置查看。

交互操作可以使用`apt`；非交互脚本通常更适合使用`apt-get`，并明确处理失败状态。

## 10.4 配置国内镜像源并验证回退（参考操作）

本节用于解释“备份—修改—刷新—验证—回退”的完整方法，不是实验5必做步骤。只有课程初始源失效，并且教师确认镜像地址与机房网络可用时才执行，不能把不同版本的仓库配置混用。

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
sudo ls -dt /root/yum-repos-backup-* 2>/dev/null
read -r -p '输入本次确认要恢复的Rocky仓库备份目录：' backup_dir
sudo test -d "$backup_dir"
sudo cp -a "$backup_dir"/. /etc/yum.repos.d/
sudo dnf clean all
sudo dnf makecache
```

不要用`head -1`自动选择备份，因为最新目录未必就是要恢复的版本。应核对时间和内容后输入明确路径；不要在未确认路径时执行批量删除。

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
sudo ls -lt /etc/apt/sources.list.backup.* 2>/dev/null
read -r -p '输入本次确认要恢复的sources.list备份文件：' backup_file
sudo test -f "$backup_file"
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

### 本章短练习：查询软件来源并预演事务

本练习不安装、卸载或换源。分别在Rocky和Ubuntu上建立独立记录目录：

Rocky：

```bash
mkdir -p ~/course-practice/m1/ch10
{
    printf '=== enabled repositories ===\n'
    dnf repolist --enabled
    printf '\n=== tree information ===\n'
    dnf info tree
    printf '\n=== owner of /usr/bin/ls ===\n'
    rpm -qf /usr/bin/ls
} > ~/course-practice/m1/ch10/rocky-package-query.txt
sudo dnf install tree --assumeno
```

Ubuntu：

```bash
mkdir -p ~/course-practice/m1/ch10
{
    printf '=== configured sources ===\n'
    grep -RhE '^[[:space:]]*deb ' /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null
    printf '\n=== tree policy ===\n'
    apt-cache policy tree
    printf '\n=== owner of bash ===\n'
    dpkg -S /bin/bash
} > ~/course-practice/m1/ch10/ubuntu-package-query.txt
apt-get -s install tree
```

`--assumeno`和`apt-get -s`只展示计划，不提交安装事务。完成后检查两个记录文件非空，并说明“仓库中可获得”“本机已安装”“命令可执行”三种状态为什么不同。

### 实验衔接：实验5

实验5在`rocky-server`上完成仓库基线、配置备份、元数据刷新、`tree`和`jq`安装、包文件查询、受控卸载与DNF历史留证。所有系统修改和`~/m1-project/evidence`成果以实验5步骤为准；Ubuntu换源仍以实验1建立的课程镜像基线为准。

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

交互观察：打开[systemd服务状态、依赖与journal排障动画](../animations/04-systemd-journal/index.html)。先完成“运行与自启”，分别预测`start`、`enable`和`enable --now`执行后的active/enabled组合，再用`is-active`和`is-enabled`独立验证。

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

依赖关系与启动排序不能混为一谈：`Wants`和`Requires`主要回答“启动当前Unit时还需要拉入谁”，`After`和`Before`回答“当两者都在同一事务中时谁先执行”。`After=B`不会单独把B拉入事务；`Requires=B`也不单独规定A必须排在B之后。需要表达“拉入B并在B之后启动A”时，应按实际强弱要求组合`Wants/Requires`与`After`。

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

## 11.6 读懂简单服务

### 本章短练习：分析Unit并预测结果

完整的服务创建、故障注入和恢复放在实验6完成。本章只分析一个Unit，不在系统中创建第二套临时服务：

```ini
[Unit]
Description=Course demo service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 -m http.server 8088 --bind 127.0.0.1 --directory /home/student/m1-project/systemd/site
Restart=on-failure
User=student

[Install]
WantedBy=multi-user.target
```

阅读后应能指出`ExecStart`的程序与参数、`After`的启动顺序含义、`Restart`策略，以及`WantedBy`与当前运行状态的区别。先用`command -v python3`和`test -d ~/m1-project`检查前置对象；实验6会创建`systemd/site`专用站点目录。示例用户名及家目录`student`必须在实验6中替换为实际账号，不要直接复制后启动。

修改已安装的Unit后需要执行`systemctl daemon-reload`，但它只让systemd重新读取配置，并不会自动重启服务。

### 服务排障流程

```text
systemctl status
→ 检查Unit和ExecStart路径
→ 检查用户、权限和配置语法
→ journalctl -u查看日志
→ 修复后restart/reload
→ is-active和实际功能验证
```

### 实验衔接：实验6

实验6使用`course-demo.service`完成本章唯一一次完整实操：建立Unit，比较active/enabled，使用curl验证功能，制造`ExecStart`路径错误，保存日志证据并恢复。教材示例只用于阅读和预测，所有系统修改以实验6步骤为准。

---

# 第12章 系统状态、进程、磁盘与容量

## 本章学习目标

完成本章后，应能够：

1. 读取负载、CPU、内存、进程、磁盘空间和inode等状态。
2. 区分磁盘、分区、文件系统、挂载点和目录容量。
3. 在确认空白实验盘后创建分区、XFS文件系统并完成临时和持久挂载。
4. 说明PV、VG、LV、文件系统和挂载点的层次，完成逻辑卷创建与在线扩容。
5. 逐条采集证据并形成包含判断依据的系统健康摘要。

## 12.1 CPU与系统负载

```bash
uptime
```

```bash
nproc
```

```bash
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
```

```bash
ps aux --sort=-%mem | head
```

重点关注`available`而不是只看`free`。Linux会利用空闲内存作为缓存，并在应用需要时回收。Swap持续大量使用、系统频繁换页并伴随响应变慢，才更值得进一步调查。

## 12.3 进程

`ps`通常由`procps-ng`提供，`pstree`通常由`psmisc`提供。先检查并按需安装扩展工具：

```bash
command -v ps
```

```bash
command -v pstree
```

如果没有输出，再安装提供`pstree`的工具包：

```bash
sudo dnf install -y psmisc
```

```bash
ps aux
```

```bash
ps -ef
```

```bash
pgrep -a sshd
```

```bash
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
```

Shell会显示类似`[1] 2345`的结果，其中`2345`是本次练习进程PID。把实际数字记录下来。

先按下面格式查看进程，中文占位说明必须替换为刚记录的PID：

```text
ps -p 实际PID -o pid,stat,cmd
```

确认命令显示的是`sleep 300`后，再按格式发送正常终止信号：

```text
kill 实际PID
```

最后再次执行查询。没有显示该PID，表示进程已经结束：

```text
ps -p 实际PID -o pid,stat,cmd
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
```

```bash
findmnt
```

```bash
findmnt /
```

```bash
sudo blkid
```

如果系统使用LVM，还可能看到：

```text
物理卷PV → 卷组VG → 逻辑卷LV → 文件系统 → 挂载点
```

查看LVM结构：

```bash
command -v pvs
```

如果没有输出，再安装LVM管理工具：

```bash
sudo dnf install -y lvm2
```

```bash
sudo pvs
```

```bash
sudo vgs
```

```bash
sudo lvs
```

仅会查看还不足以承担基础运维工作。本课程要求在实验7提供的空白虚拟磁盘上完成下面这条最小能力链：

```text
识别空白磁盘
→ 创建GPT分区
→ 创建XFS文件系统
→ 临时挂载并验证读写
→ 使用UUID配置/etc/fstab
→ 创建PV、VG和LV
→ 创建并挂载逻辑卷文件系统
→ 扩展LV和XFS
→ 重启验证
```

不要求学习RAID、LUKS、LVM快照、thin pool、条带卷或缩容。

### 1. 存储操作的安全边界

分区、格式化、`pvcreate`都会改变磁盘结构。执行前必须同时确认：

1. 当前位于`rocky-server`，并已建立实验前快照。
2. VMware已经为该虚拟机增加一块8GiB空白实验盘。
3. 系统盘与根文件系统不在准备操作的磁盘上。
4. 课程标准实验盘为`/dev/sdb`；如果实际名称不同，停止并由教师确认，不能自行把命令中的设备名改成猜测值。

列出整块磁盘，不显示分区：

```bash
lsblk -dpno NAME,SIZE,TYPE,MODEL
```

确认根文件系统来自哪个设备：

```bash
findmnt -no SOURCE /
```

查看`/dev/sdb`是否已有文件系统或签名，但不修改它：

```bash
sudo wipefs -n /dev/sdb
```

查看现有分区表：

```bash
sudo parted /dev/sdb print
```

如果`/dev/sdb`已挂载、已有需要保留的数据、容量不是教师规定值，或者根文件系统位于该磁盘，立即停止。

### 2. 创建普通分区和XFS文件系统

实验7把8GiB空白盘分成两个区域：

```text
/dev/sdb1：约2GiB，普通XFS文件系统，挂载到/data
/dev/sdb2：剩余空间，作为LVM物理卷
```

安装所需工具：

```bash
sudo dnf install -y parted lvm2 xfsprogs
```

在已经完成安全确认的空白盘上建立GPT分区表：

```bash
sudo parted -s /dev/sdb mklabel gpt
```

创建约2GiB普通分区：

```bash
sudo parted -s /dev/sdb mkpart data xfs 1MiB 2049MiB
```

使用剩余空间创建LVM分区：

```bash
sudo parted -s /dev/sdb mkpart lvm 2049MiB 100%
```

为第2分区设置LVM标志：

```bash
sudo parted -s /dev/sdb set 2 lvm on
```

通知内核重新读取分区表：

```bash
sudo partprobe /dev/sdb
```

```bash
sudo udevadm settle
```

核对结果：

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS /dev/sdb
```

只有看到`sdb1`和`sdb2`后才继续。为普通分区创建XFS：

```bash
sudo mkfs.xfs -L DATA /dev/sdb1
```

`mkfs`创建的是文件系统，会覆盖目标分区上的原有文件系统信息。因此它只能作用于已确认的实验分区。

### 3. 临时挂载、验证与卸载

创建挂载点：

```bash
sudo mkdir -p /data
```

临时挂载：

```bash
sudo mount /dev/sdb1 /data
```

确认“设备—文件系统—挂载点”关系：

```bash
findmnt /data
```

```bash
df -hT /data
```

写入测试文件：

```bash
echo 'ordinary mount works' | sudo tee /data/mount-test.txt
```

读取验证：

```bash
cat /data/mount-test.txt
```

卸载前不能让终端当前目录停留在`/data`中。先返回主目录：

```bash
cd ~
```

卸载：

```bash
sudo umount /data
```

验证已经卸载：

```bash
findmnt /data
```

没有输出表示当前未挂载。卸载只解除访问关系，不会删除文件系统中的测试文件。

### 4. 使用UUID配置持久挂载

手工`mount`只在本次运行期间有效。持久挂载需要配置`/etc/fstab`。

修改前备份：

```bash
sudo cp -a /etc/fstab /etc/fstab.before-storage-lab
```

读取普通分区UUID：

```bash
sudo blkid /dev/sdb1
```

编辑：

```bash
sudo vim /etc/fstab
```

根据实际UUID增加一行，不能照抄`实际UUID`四个字：

```text
UUID=实际UUID  /data  xfs  defaults  0  0
```

六个字段依次表示：设备、挂载点、文件系统类型、挂载选项、dump标志和文件系统检查顺序。

先做语法和引用检查：

```bash
sudo findmnt --verify --verbose
```

再让系统按`fstab`挂载：

```bash
sudo mount -a
```

验证挂载和原测试文件：

```bash
findmnt /data
```

```bash
cat /data/mount-test.txt
```

只有`findmnt --verify`和`mount -a`都没有错误时，才允许重启。配置错误时先恢复备份：

```bash
sudo cp -a /etc/fstab.before-storage-lab /etc/fstab
```

### 5. 创建PV、VG和LV

LVM的层次不能省略：

```text
/dev/sdb2分区
→ PV物理卷
→ vg_data卷组
→ lv_app逻辑卷
→ XFS文件系统
→ /srv/appdata挂载点
```

把第2分区初始化为PV：

```bash
sudo pvcreate /dev/sdb2
```

创建卷组：

```bash
sudo vgcreate vg_data /dev/sdb2
```

查看卷组总量和剩余空间：

```bash
sudo vgs
```

创建2GiB逻辑卷：

```bash
sudo lvcreate -L 2G -n lv_app vg_data
```

核对每个层次及其底层设备：

```bash
sudo pvs
```

```bash
sudo vgs
```

```bash
sudo lvs -o lv_name,vg_name,lv_size,devices
```

### 6. 为逻辑卷创建文件系统并持久挂载

逻辑卷创建完成后仍不能直接保存普通文件，必须先创建文件系统：

```bash
sudo mkfs.xfs -L APPDATA /dev/vg_data/lv_app
```

```bash
sudo mkdir -p /srv/appdata
```

```bash
sudo mount /dev/vg_data/lv_app /srv/appdata
```

```bash
echo 'lvm mount works' | sudo tee /srv/appdata/lvm-test.txt
```

读取逻辑卷文件系统UUID：

```bash
sudo blkid /dev/vg_data/lv_app
```

再次编辑`/etc/fstab`，按实际UUID增加：

```text
UUID=逻辑卷文件系统的实际UUID  /srv/appdata  xfs  defaults  0  0
```

验证配置：

```bash
sudo findmnt --verify --verbose
```

```bash
sudo mount -a
```

```bash
findmnt /srv/appdata
```

### 7. 扩展逻辑卷与XFS

扩容前先记录两层容量：

```bash
sudo lvs /dev/vg_data/lv_app
```

```bash
df -hT /srv/appdata
```

先把LV扩大1GiB：

```bash
sudo lvextend -L +1G /dev/vg_data/lv_app
```

此时块设备已经变大，但已挂载XFS还需要扩展：

```bash
sudo xfs_growfs /srv/appdata
```

重新检查两层容量：

```bash
sudo lvs /dev/vg_data/lv_app
```

```bash
df -hT /srv/appdata
```

确认原文件仍可读取：

```bash
cat /srv/appdata/lvm-test.txt
```

`lvextend`扩展的是逻辑卷，`xfs_growfs`扩展的是文件系统。只完成前一步，`lvs`可能显示容量已经增加，但`df`仍看不到可用空间增加。

### 8. 本课程的LVM边界

必须掌握：

- PV、VG、LV、文件系统、挂载点的关系；
- `pvcreate`、`vgcreate`、`lvcreate`；
- `pvs`、`vgs`、`lvs`；
- 在卷组有空闲空间时扩展LV与XFS；
- 使用UUID持久挂载并在重启前验证。

只要求了解：

- `lvextend -r`可以尝试同时扩展LV与文件系统；
- 新增磁盘后可以通过`vgextend`为卷组增加PV。

本课程不做：

- XFS缩容，因为XFS不支持直接缩小；
- 在包含正式数据的卷上练习缩容；
- RAID、LUKS、LVM快照和thin pool。

执行存储修改的原则是：先识别层次和设备，再备份配置，修改后逐层验证，不在不明确的设备上尝试命令。

## 12.5 磁盘空间与inode

后面的“已删除但仍被占用文件”检查需要`lsof`：

```bash
command -v lsof
```

如果没有输出，再安装`lsof`：

```bash
sudo dnf install -y lsof
```

```bash
df -h
```

```bash
df -i
```

```bash
sudo du -sh /var/log
```

```bash
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
```

```bash
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

## 12.7 生成只读系统状态摘要

### 本章短练习：采集并解释系统状态

本练习只采集状态，不制造负载、不终止进程，也不修改服务。先创建本章独立目录：

```bash
mkdir -p ~/course-practice/m1/ch12
```

先把采集时间写入摘要文件。第一条使用`>`创建或覆盖文件：

```bash
date -Iseconds > ~/course-practice/m1/ch12/status-summary.txt
```

后续命令全部使用`>>`追加，避免覆盖已有结果：

```bash
hostname >> ~/course-practice/m1/ch12/status-summary.txt
```

```bash
uptime >> ~/course-practice/m1/ch12/status-summary.txt
```

```bash
nproc >> ~/course-practice/m1/ch12/status-summary.txt
```

```bash
free -h >> ~/course-practice/m1/ch12/status-summary.txt
```

```bash
ps -eo pid,user,stat,%cpu,%mem,comm --sort=-%cpu >> ~/course-practice/m1/ch12/status-summary.txt
```

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS >> ~/course-practice/m1/ch12/status-summary.txt
```

```bash
findmnt >> ~/course-practice/m1/ch12/status-summary.txt
```

```bash
sudo pvs >> ~/course-practice/m1/ch12/status-summary.txt
```

```bash
sudo vgs >> ~/course-practice/m1/ch12/status-summary.txt
```

```bash
sudo lvs >> ~/course-practice/m1/ch12/status-summary.txt
```

```bash
df -hT >> ~/course-practice/m1/ch12/status-summary.txt
```

```bash
df -i >> ~/course-practice/m1/ch12/status-summary.txt
```

```bash
systemctl --failed --no-pager >> ~/course-practice/m1/ch12/status-summary.txt
```

```bash
ss -lntup >> ~/course-practice/m1/ch12/status-summary.txt
```

检查文件非空，并用vim在末尾补充三条结论：当前CPU/负载、内存、磁盘是否存在明显风险，以及判断依据。

```bash
test -s ~/course-practice/m1/ch12/status-summary.txt
```

```bash
echo "summary_nonempty_check=$?"
```

```bash
sed -n '1,120p' ~/course-practice/m1/ch12/status-summary.txt
```

`summary_nonempty_check=0`只表示记录已生成，不表示系统一定健康；最终结论必须结合数值、时间点和业务背景。

### 实验衔接：实验7

实验7从保留的`~/m1-project`和教师准备的8GiB空白虚拟磁盘起步。学生需要先完成设备安全确认，再完成普通分区挂载、UUID持久挂载、LVM创建与扩容，最后进行可控CPU异常的“制造—定位—终止—复测”，并把正式报告写入`~/m1-project/evidence/lab07-health-report.txt`。本章摘要不能复制后改名冒充实验报告。

## 12.8 从人工巡检到自动化脚本

本章的重点是理解每个状态命令及其输出，暂不要求编写完整脚本。自动化巡检会把本章已经执行过的动作重新组织成以下流程：

```text
采集时间和主机身份
→ 采集负载、内存、文件系统和服务
→ 把数值与阈值比较
→ 输出正常项和告警项
→ 使用退出码表示整体结果
```

进入[3.6 Shell服务器巡检](linux/模块三/3.6-Shell服务器巡检.md)后，再学习变量、条件判断、循环、命令替换和退出码，并完成可执行巡检脚本。本章不把看不懂的脚本作为实验7的前置要求。

## 12.9 系统状态排障案例

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
磁盘 → 分区 → PV → VG → LV → 文件系统 → 挂载点
  ↓ 提供持久存储
CPU/内存/进程/端口
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
| 挂载与LVM | `mount`、`umount`、`findmnt`、`blkid`、`pvs`、`vgs`、`lvs`、`lvextend`、`xfs_growfs` |

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
12. 为什么扩展LV之后还需要扩展文件系统？
13. 为什么修改`/etc/fstab`后必须先执行验证再重启？
14. 服务启动失败时，应该按什么顺序收集证据？

## 拓展练习

1. 为`~/course-practice/m1/ch12/m1-health-check.sh`增加JSON输出模式。
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
