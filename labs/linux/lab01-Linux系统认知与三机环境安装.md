# 实验1：Linux系统认知、VMware虚拟化与三机环境安装

> 所属模块：模块一 Linux基础运维  
> 建议学时：4学时  
> 实验方式：个人  
> 对应教材：《模块一 Linux基础运维》第1—2章  
> 知识前置：计算机组成原理基础、IP地址基本概念\
> 状态依赖：无，使用具备虚拟化能力的Windows宿主机\
> 建议起点：干净宿主机与教师发布的ISO资源\
> 项目成果：两台Rocky Linux 9服务器、一台Ubuntu 22.04图形客户端、三机基线表和初始快照

## 一、项目情境

你需要为后续Linux系统管理、网络访问、Web服务、数据库服务和虚拟化容器课程建立一套可以持续使用的三机环境。三台虚拟机使用统一名称和固定教学账号，分别承担基础服务器、Web服务器和外部客户端角色。

```text
Windows 10/11宿主机
└── VMware Workstation（VMnet8 NAT）
    ├── rocky-server   Linux基础、数据库、Git、Shell、后续KVM
    ├── rocky-web      Nginx与Web服务
    └── ubuntu-client  图形界面、浏览器、SSH、curl和数据库客户端
```

实验结束后，三台虚拟机将继续用于两门课程，不得随意删除或改名。

## 二、统一身份标准

| VMware虚拟机名称 | 操作系统 | 主机名 | 普通用户名 | 教学密码 | 角色 |
|---|---|---|---|---|---|
| `rocky-server` | Rocky Linux 9最小化安装 | `rocky-server` | `rocky-server` | `123456` | 前期Linux主线、数据库与综合运维 |
| `rocky-web` | Rocky Linux 9最小化安装 | `rocky-web` | `rocky-web` | `123456` | Nginx与Web服务 |
| `ubuntu-client` | Ubuntu 22.04 Desktop | `ubuntu-client` | `ubuntu-client` | `123456` | 图形客户端与跨主机验证 |

> `123456`仅用于隔离的课堂实验环境，严禁用于互联网服务器、个人账号或生产环境。三台机器的VMware名称、主机名和主要用户名必须按表填写，不使用`student`、`rocky-vm`或“学号后缀”等其他名称。

## 三、实验目标

完成实验后，你应能够：

1. 说明UNIX、GNU、Linux内核和Linux发行版之间的关系。
2. 区分RHEL、Rocky Linux、CentOS Stream以及Debian、Ubuntu所属生态。
3. 区分物理机、宿主机、客户机、虚拟机、虚拟硬件和Hypervisor。
4. 在Windows中检查硬件虚拟化并安装VMware Workstation。
5. 按统一规格创建并安装三台Linux虚拟机。
6. 验证三台机器的身份、sudo、网络、时间、存储和VMware Tools。
7. 创建可以安全回退的初始快照并完成环境基线表。

## 四、知识准备

### 1. Linux的形成

| 时间 | 事件 | 意义 |
|---|---|---|
| 1969年 | 贝尔实验室开始开发UNIX | 形成多用户、权限、目录树和工具组合等思想 |
| 1983年 | Richard Stallman发起GNU计划 | 开发自由的编译器、Shell和大量系统工具 |
| 1991年 | Linus Torvalds发布Linux内核 | 提供进程、内存、设备、文件系统和网络管理核心 |
| 1992年前后 | Linux采用GNU GPL | Linux内核与GNU工具结合形成可用系统 |
| 此后 | 不同组织维护发行版 | 将内核、工具、安装程序、仓库和默认配置组合成产品 |

日常所说的“安装Linux”，通常是安装一个完整发行版。安装后可分别查看发行版和内核：

```bash
cat /etc/os-release
uname -r
```

### 2. 课程为什么使用两种发行版

| 家族 | 代表发行版 | 软件包 | 包管理器 | 本课程用途 |
|---|---|---|---|---|
| RHEL生态 | RHEL、Rocky Linux、CentOS Stream | RPM | DNF | 两台服务器主线 |
| Debian生态 | Debian、Ubuntu | DEB | APT | 图形客户端和发行版对照 |

Rocky Linux接近企业RHEL环境，适合学习DNF、systemd、firewalld和SELinux；Ubuntu Desktop既保留Linux终端，又能通过浏览器和图形工具模拟真实客户端。

### 3. 虚拟化基本对象

| 对象 | 本实验对应内容 |
|---|---|
| 物理机 | 机房计算机 |
| 宿主机 | Windows 10/11 |
| Hypervisor | VMware Workstation |
| 客户机 | 三台Linux虚拟机中的操作系统 |
| 虚拟硬件 | vCPU、内存、虚拟磁盘和虚拟网卡 |
| ISO | 操作系统安装介质 |
| 快照 | 依赖原虚拟磁盘的短期回退点，不等于独立备份 |

VMware Workstation运行在Windows之上，属于Type 2虚拟化软件。本课程默认使用VMnet8 NAT网络，使三台虚拟机处于同一实验网络并可经宿主机访问外部资源。

开始安装前，打开[VMware三种网络模式与课程三机拓扑动画](../../animations/01-vmware-network-modes/index.html)。依次观察三种模式的可达范围，再回答“为什么本课程初装统一使用NAT”。动画显示的是概念地址；本实验必须以虚拟网络编辑器和DHCP实际结果为准。

## 五、实验准备

### 1. 宿主机建议配置

| 项目 | 最低要求 | 建议配置 |
|---|---:|---:|
| CPU | 4个逻辑处理器并启用VT-x/AMD-V | 8个或更多逻辑处理器 |
| 内存 | 16GB | 32GB |
| 可用磁盘 | 100GB | 150GB以上SSD空间 |
| 宿主系统 | Windows 10/11 64位 | Windows 11 64位 |
| 虚拟化软件 | VMware Workstation 17 | 机房统一版本 |

内存不足时安装阶段只同时运行一至两台虚拟机；需要三机联调时，可临时把两台Rocky调整为2GB、Ubuntu调整为3GB。

### 2. 安装文件

- Rocky Linux 9.x x86_64 Minimal ISO；同一ISO用于两台Rocky。
- Ubuntu 22.04.x Desktop amd64 ISO，必须是图形桌面版而不是`live-server`版。
- VMware Workstation 17安装程序。
- 教师公布的三个文件SHA-256校验值。

### 3. 虚拟机规格

| 虚拟机 | vCPU | 内存 | 虚拟磁盘 | 网络 | 安装方式 |
|---|---:|---:|---:|---|---|
| `rocky-server` | 2 | 4GB | 50GB | VMnet8 NAT | Minimal Install |
| `rocky-web` | 2 | 2GB | 40GB | VMnet8 NAT | Minimal Install |
| `ubuntu-client` | 2 | 4GB | 40GB | VMnet8 NAT | Ubuntu Desktop |

Rocky-server后续承担数据库、KVM和Docker，可在相应模块开始前增加内存、vCPU和磁盘；第一次课不必直接分配到最大规格。

## 六、实验时间参考

本实验共180分钟。安装程序、ISO和校验值应在实验开始前从课程共享目录取得，不在课堂等待公网下载。

| 时间 | 教学与操作安排 |
|---:|---|
| 0—35分钟 | Linux起源、发行版、课程拓扑和虚拟化概念 |
| 35—55分钟 | 宿主机检查、VMware安装或版本核对、ISO校验 |
| 55—120分钟 | 创建三台虚拟机；两台Rocky错峰安装，Ubuntu安装等待时继续讲解 |
| 120—155分钟 | 三机首次登录、身份、sudo、网络和基础工具检查 |
| 155—180分钟 | 快照、三机基线、互访预检和验收 |

先完整完成`rocky-server`，再依据统一参数独立完成`rocky-web`；Ubuntu部分重点关注图形安装界面、软件源和账号配置与Rocky的差异。

## 七、实验步骤

### 任务一：检查宿主机与VMware

#### 步骤1：检查Windows资源

按`Win + R`输入：

```text
msinfo32
```

记录Windows版本、系统类型、CPU和内存。打开任务管理器的“性能 → CPU”，确认：

```text
虚拟化：已启用
```

再确认虚拟机保存磁盘具有足够空间。虚拟化未启用时停止操作，由教师或机房管理员处理BIOS/UEFI设置。

#### 步骤2：建立课程目录

示例：

```text
D:\LinuxCourse\
├── ISO\
├── VMwareInstaller\
├── VirtualMachines\
└── Evidence\
```

三台虚拟机必须分别保存到独立子目录，不得共用虚拟磁盘。

#### 步骤3：校验安装文件

在PowerShell中执行，文件名按教师实际版本替换：

```powershell
Get-FileHash 'D:\LinuxCourse\ISO\Rocky-9.x-x86_64-minimal.iso' -Algorithm SHA256
Get-FileHash 'D:\LinuxCourse\ISO\ubuntu-22.04.x-desktop-amd64.iso' -Algorithm SHA256
Get-FileHash 'D:\LinuxCourse\VMwareInstaller\VMware-workstation-full.exe' -Algorithm SHA256
```

输出必须与教师公布值一致。不一致时重新复制，不能继续安装。

#### 步骤4：安装并检查VMware

使用教师提供的合法安装包完成安装。打开VMware后检查：

1. 可以进入主界面。
2. Windows中存在VMware Network Adapter VMnet8。
3. “编辑 → 虚拟网络编辑器”中VMnet8使用NAT并启用DHCP。
4. 记录VMnet8子网、掩码、NAT网关和DHCP范围，不照抄教材示例地址。

### 任务二：创建三台虚拟机

#### 步骤5：建立虚拟机外壳

在VMware中选择“创建新的虚拟机”，统一选择“稍后安装操作系统”，分别设置：

| 设置 | rocky-server | rocky-web | ubuntu-client |
|---|---|---|---|
| 客户机类型 | RHEL 9 64-bit | RHEL 9 64-bit | Ubuntu 64-bit |
| VMware名称 | `rocky-server` | `rocky-web` | `ubuntu-client` |
| 保存目录 | `VirtualMachines\rocky-server` | `VirtualMachines\rocky-web` | `VirtualMachines\ubuntu-client` |
| vCPU | 2 | 2 | 2 |
| 内存 | 4096MB | 2048MB | 4096MB |
| 磁盘 | 50GB | 40GB | 40GB |
| CD/DVD | Rocky Minimal ISO | Rocky Minimal ISO | Ubuntu Desktop ISO |
| 网络 | NAT | NAT | NAT |

> **验收点**：VMware左侧恰好出现`rocky-server`、`rocky-web`、`ubuntu-client`，名称没有学号后缀或大小写变化。

### 任务三：安装rocky-server

#### 步骤6：进入Rocky安装程序

启动`rocky-server`，选择`Install Rocky Linux 9.x`。若提示找不到操作系统，关机检查CD/DVD是否挂载正确ISO并勾选“启动时连接”。

#### 步骤7：填写安装参数

| 项目 | 设置 |
|---|---|
| 语言、键盘 | English (United States) / English (US) |
| 时间 | Asia/Shanghai |
| 安装目标 | 选择50GB虚拟磁盘，自动LVM |
| 软件选择 | Minimal Install，不安装图形界面 |
| 网络 | 启用网卡，IPv4暂用DHCP |
| 主机名 | `rocky-server` |
| Root账号 | 锁定；日常不直接使用root |
| 普通用户 | 用户名`rocky-server`，密码`123456`，勾选管理员权限 |

安装完成后重启并断开ISO。登录提示应包含：

```text
rocky-server login:
```

使用`rocky-server`和`123456`登录。

### 任务四：安装rocky-web

#### 步骤8：独立完成第二台Rocky安装

启动`rocky-web`，参照步骤6—7完成安装，仅替换以下身份：

| 项目 | 设置 |
|---|---|
| VMware名称 | `rocky-web` |
| 主机名 | `rocky-web` |
| 普通用户名 | `rocky-web` |
| 密码 | `123456` |
| 磁盘 | 40GB |

不得把`rocky-server`虚拟磁盘直接挂给`rocky-web`。本实验采用独立安装，避免首次课引入克隆后machine-id、SSH主机密钥和网络身份重复问题。

### 任务五：安装ubuntu-client

#### 步骤9：完成Ubuntu Desktop安装

启动`ubuntu-client`并进入Ubuntu 22.04 Desktop图形安装程序。不同小版本界面文字可能略有变化，遵循以下标准：

| 项目 | 设置 |
|---|---|
| 安装类型 | Ubuntu Desktop正常安装 |
| 语言、键盘 | 可选中文界面；键盘按机房实际选择 |
| 网络 | VMnet8 NAT，安装阶段使用DHCP |
| 磁盘 | 擦除虚拟磁盘并安装；只会作用于40GB虚拟磁盘 |
| 计算机名 | `ubuntu-client` |
| 用户名 | `ubuntu-client` |
| 密码 | `123456` |
| 自动登录 | 不启用 |

安装完成后重启并断开ISO。应进入Ubuntu图形登录界面，使用`ubuntu-client`登录并打开Terminal。

### 任务六：初始化两台Rocky

#### 步骤10：核对身份和sudo

在`rocky-server`执行：

```bash
whoami
hostnamectl --static
id
sudo whoami
```

预期依次确认当前用户和主机名都是`rocky-server`，用户属于`wheel`组，`sudo whoami`输出`root`。

在`rocky-web`执行同样命令，当前用户和主机名都应为`rocky-web`。

#### 步骤11：核对系统、时间和资源

两台Rocky分别执行：

```bash
cat /etc/rocky-release
uname -r
uname -m
timedatectl
ip -brief address
ip route
free -h
lsblk -f
df -h /
systemctl --failed
```

若时区不正确：

```bash
sudo timedatectl set-timezone Asia/Shanghai
```

#### 步骤12：配置课程软件源并安装基础工具

两台Rocky分别确认版本、架构、地址、路由和DNS：

```bash
cat /etc/rocky-release
uname -m
ip -brief address
ip route
cat /etc/resolv.conf
```

只有系统为Rocky Linux 9 x86_64且基础网络正常时才继续。先备份仓库配置并记录实际备份位置：

```bash
ROCKY_REPO_BACKUP="/root/yum-repos-before-course-$(date +%F-%H%M%S)"
sudo mkdir -p "$ROCKY_REPO_BACKUP"
sudo cp -a /etc/yum.repos.d/. "$ROCKY_REPO_BACKUP/"
printf '%s\n' "$ROCKY_REPO_BACKUP" | \
  sudo tee /var/tmp/course-rocky-repo-backup.path
```

使用开课前已验证的阿里云Rocky镜像配置：

```bash
sudo find /etc/yum.repos.d -maxdepth 1 -type f -iname 'rocky*.repo' \
  -exec sed -e 's|^mirrorlist=|#mirrorlist=|g' \
  -e 's|^#baseurl=http://dl.rockylinux.org/$contentdir|baseurl=https://mirrors.aliyun.com/rockylinux|g' \
  -i.bak '{}' +
sudo dnf clean all
sudo dnf makecache
dnf repolist
```

如果`makecache`失败，停止安装，保留报错并检查地址、路由、DNS、系统时间和镜像配置。需要回退时执行：

```bash
ROCKY_REPO_BACKUP=$(cat /var/tmp/course-rocky-repo-backup.path)
sudo cp -a "$ROCKY_REPO_BACKUP"/. /etc/yum.repos.d/
sudo dnf clean all
sudo dnf makecache
```

仓库刷新成功后安装基础工具：

```bash
sudo dnf install -y \
  open-vm-tools vim-enhanced curl wget git tar \
  bash-completion openssh-server openssh-clients chrony

sudo systemctl enable --now vmtoolsd sshd chronyd
```

验证：

```bash
for cmd in vim curl wget git tar ssh; do
  command -v "$cmd" || echo "MISSING $cmd"
done
systemctl is-active vmtoolsd sshd chronyd
```

暂不预装`tree`和`jq`，保留给实验5的软件包管理任务；也不提前安装Nginx、数据库、KVM和Docker。

### 任务七：初始化Ubuntu图形客户端

#### 步骤13：检查身份和系统

在Ubuntu图形桌面打开Terminal：

```bash
whoami
hostnamectl --static
id
sudo whoami
cat /etc/os-release
ip -brief address
ip route
```

预期当前用户和主机名均为`ubuntu-client`，`sudo whoami`输出`root`。

#### 步骤14：安装客户端工具

先确认Ubuntu版本、代号和架构：

```bash
. /etc/os-release
printf 'version=%s codename=%s arch=%s\n' \
  "$VERSION_ID" "$VERSION_CODENAME" "$(dpkg --print-architecture)"
```

只有结果为`22.04`、`jammy`、`amd64`时才执行下面的课程源配置：

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
```

`apt update`失败时停止安装，检查网络、DNS、时间和镜像配置。需要回退时读取`/var/tmp/course-ubuntu-source-backup.path`并恢复原文件。索引刷新成功后安装：

```bash
sudo apt install -y \
  open-vm-tools open-vm-tools-desktop \
  openssh-client openssh-server curl wget git vim

sudo systemctl enable --now ssh
sudo reboot
```

重启后确认图形桌面、鼠标、分辨率和Terminal正常，再检查：

```bash
systemctl is-active ssh
command -v ssh
command -v curl
```

### 任务八：完成三机网络基线

#### 步骤15：记录DHCP地址

三台虚拟机分别执行：

```bash
hostnamectl --static
ip -brief address
ip route
```

将结果填写到表中：

| VMware名称 | 主机名 | 用户名 | 网卡名 | DHCP IPv4地址 | 默认网关 |
|---|---|---|---|---|---|
| rocky-server | rocky-server | rocky-server |  |  |  |
| rocky-web | rocky-web | rocky-web |  |  |  |
| ubuntu-client | ubuntu-client | ubuntu-client |  |  |  |

三台地址必须互不重复，并属于实际VMnet8网络。本实验只验证DHCP和NAT基线，实验8再统一配置静态地址和三机名称解析。

#### 步骤16：验证网关

三台机器分别执行：

```bash
GATEWAY=$(ip route show default | awk 'NR==1 {print $3}')
printf 'gateway=%s\n' "$GATEWAY"
ping -c 3 "$GATEWAY"
```

公共互联网或公共DNS不可用不等于Linux安装失败；以VMnet8网关和校内资源验证为准。

### 任务九：创建初始快照

#### 步骤17：安全关机

两台Rocky执行：

```bash
sudo poweroff
```

Ubuntu通过右上角系统菜单正常关机，或在Terminal执行同一命令。虚拟机完全关闭后创建快照：

| 虚拟机 | 快照名称 |
|---|---|
| rocky-server | `00-rocky-server-安装与基础工具完成` |
| rocky-web | `00-rocky-web-安装与基础工具完成` |
| ubuntu-client | `00-ubuntu-client-桌面与客户端工具完成` |

快照完成后重新开机，确认三台机器仍能使用规定账号登录。

## 八、独立实践

1. 分别使用什么命令查看发行版版本和Linux内核版本？
2. VMware Workstation为什么属于Type 2 Hypervisor？
3. 为什么三台虚拟机必须使用不同主机名和不同IP地址？
4. 为什么`ubuntu-client`使用图形桌面，而两台Rocky使用最小化安装？
5. 为什么本实验使用DHCP，静态IP留到实验8？
6. 为什么不能把快照当作独立备份？
7. 为什么只在隔离实验环境使用`123456`？
8. 为什么前期主要操作`rocky-server`，但仍需在第一节课准备`rocky-web`？

## 九、验收标准

- [ ] 能说明Linux内核、GNU工具和发行版的关系。
- [ ] Windows硬件虚拟化已启用，VMware和VMnet8可用。
- [ ] 三个ISO/安装文件校验值与教师公布值一致。
- [ ] VMware中存在且只使用规定名称的三台虚拟机。
- [ ] 两台Rocky均为最小化命令行环境，Ubuntu为22.04图形桌面。
- [ ] 三台机器的主机名、用户名和密码符合统一身份表。
- [ ] 两台Rocky普通用户属于wheel组并能使用sudo。
- [ ] Ubuntu客户端能进入桌面、打开Terminal并使用sudo。
- [ ] 三台机器均获得互不重复的DHCP地址并能访问VMnet8网关。
- [ ] VMware Tools、SSH和基础工具检查通过。
- [ ] 三台虚拟机均已建立规定名称的初始快照。
- [ ] 三机环境基线表由实际命令结果填写。

## 十、成果提交

提交目录：

```text
学号-姓名-实验01/
├── README.md
├── host-check.md
├── three-host-baseline.md
└── evidence/
    ├── vmware-three-hosts.png
    ├── rocky-server-baseline.txt
    ├── rocky-web-baseline.txt
    ├── ubuntu-client-desktop.png
    └── snapshots.png
```

`README.md`回答独立实践问题；基线文件记录三台机器的身份、版本、资源、地址、网关、工具和快照。截图不得包含除本课程统一教学口令以外的个人密码、Token或私钥。

## 十一、常见问题

### 1. VMware提示无法运行64位客户机

检查任务管理器中的虚拟化状态；若关闭，由机房管理员进入BIOS/UEFI启用VT-x或AMD-V。不要自行关闭Windows安全策略。

### 2. 安装完成后再次进入安装界面

虚拟机仍从ISO启动。关闭虚拟机，在CD/DVD设置中断开ISO，再启动虚拟磁盘。

### 3. Rocky用户不能使用sudo

通过教师保留的管理员入口检查用户组：

```bash
id rocky-server
id rocky-web
```

相应用户应属于`wheel`组。只修正当前虚拟机对应用户，不把两个角色账号混装到同一台机器。

### 4. Ubuntu安装后只有命令行

先检查是否误用了`ubuntu-22.04.x-desktop-amd64.iso`。本课程要求Ubuntu 22.04 Desktop；镜像用错时恢复到安装前状态并使用教师提供的Desktop ISO重新安装。

### 5. 三台虚拟机同时运行很卡

先关闭无关程序；安装阶段错峰启动。前期练习只运行`rocky-server`和按需使用的`ubuntu-client`，到Nginx实验再重点运行`rocky-web`，不要求三台始终同时开机。

### 6. 虚拟机没有IPv4地址

检查VMware网络适配器是否为NAT、是否勾选“已连接”和“启动时连接”，再执行：

```bash
ip -brief link
ip route
```

Rocky继续使用`nmcli device status`检查；Ubuntu使用桌面网络设置或`nmcli`检查。不要照抄其他同学地址。

## 十二、环境保留

- 保留`rocky-server`、`rocky-web`和`ubuntu-client`三台虚拟机。
- 保留三个初始快照以及ISO校验记录。
- 实验2—13主要在`rocky-server`操作，`ubuntu-client`按需进行外部验证。
- `rocky-web`在实验8完成静态网络和SSH基线，实验14正式承担Nginx服务。
- 不提前安装Nginx、MySQL、MongoDB、Redis、KVM或Docker。
