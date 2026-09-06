# 实验1：Linux系统认知、VMware虚拟化环境搭建与Rocky/Ubuntu双机安装

> 所属模块：模块一 Linux基础运维  
> 建议学时：4学时  
> 实验方式：个人  
> 对应教材：《模块一 Linux基础运维》第1—2章  
> 前置实验：无  
> 项目成果：可运行、可登录、可联网、可回退的Rocky Linux服务器和Ubuntu Server客户端，以及一份双机环境基线表

## 一、项目情境

你作为企业运维团队的新成员，需要为后续Linux服务部署课程准备Rocky Linux实验服务器和Ubuntu Server访问客户端。两台系统都运行在VMware Workstation提供的虚拟化环境中。

项目完成后，其他同学或教师应能够根据你的环境基线记录确认：

- 宿主机是否具备运行虚拟机的条件；
- VMware是否安装正常；
- Rocky Linux和Ubuntu Server使用了什么虚拟硬件；
- 系统版本、内核、CPU架构和主机名是什么；
- 虚拟机当前使用哪个IP地址和默认网关；
- 普通用户是否能够正常使用sudo；
- 系统出现问题后能否回到初始快照。

本实验建立的Rocky Linux服务器和Ubuntu Server客户端将继续用于后续网络、SSH、Nginx和数据库访问验证，不应在实验结束后删除。

## 二、实验目标

### 1. 知识目标

完成实验后，你应能够：

1. 说明UNIX、GNU、Linux内核和Linux发行版之间的基本关系。
2. 区分Linux内核版本与Linux发行版版本。
3. 说明RHEL、Rocky Linux、CentOS Stream以及Debian、Ubuntu之间的基本关系。
4. 区分物理机、宿主机、虚拟机、客户机、虚拟硬件和Hypervisor。
5. 说明Type 1与Type 2虚拟化的基本区别。
6. 解释ISO镜像、虚拟磁盘、虚拟网卡和快照在实验环境中的作用。

### 2. 能力目标

完成实验后，你应能够：

1. 检查Windows宿主机的CPU、内存、磁盘和硬件虚拟化状态。
2. 安装并启动VMware Workstation。
3. 根据给定规格创建Rocky Linux服务器和Ubuntu Server客户端虚拟机。
4. 完成Rocky Linux 9最小化安装和Ubuntu Server 22.04安装。
5. 使用命令查看两台系统的版本、用户、网络、内存和磁盘信息。
6. 创建并验证两台虚拟机的初始快照。

### 3. 素质目标

1. 形成先检查环境、再实施安装的操作习惯。
2. 形成使用普通用户进行日常操作、需要时再使用sudo的安全意识。
3. 形成变更前保留快照、变更后验证结果的运维习惯。
4. 养成准确记录环境参数和交付信息的职业习惯。

## 三、知识准备

### 1. 从UNIX到Linux

Linux并不是凭空出现的。理解下面的时间线，有助于认识今天Linux系统中各种工具的来源。

| 时间 | 事件 | 与Linux的关系 |
|---|---|---|
| 1969年 | 贝尔实验室开始开发UNIX | UNIX形成了多用户、目录树、权限和“用小工具组合完成任务”等思想 |
| 1983年 | Richard Stallman发起GNU计划 | GNU计划希望建立一个自由的类UNIX操作系统，并开发了大量命令、编译器和工具 |
| 1991年 | Linus Torvalds发布Linux内核 | Linux内核负责进程、内存、设备、文件系统和网络等底层管理 |
| 1992年前后 | Linux采用GNU GPL发布 | Linux内核与GNU工具等自由软件结合，形成可实际使用的GNU/Linux系统 |
| 此后 | 不同组织构建Linux发行版 | 发行版把内核、命令、软件包管理器、安装程序和维护服务组合为完整系统 |

日常所说的“Linux操作系统”通常指一个完整Linux发行版，而不仅仅是Linux内核。

```text
Linux发行版
├── Linux内核
├── GNU及其他命令行工具
├── Shell
├── systemd等系统服务
├── 软件包管理器和软件仓库
├── 安装程序
└── 发行版维护的默认配置与安全更新
```

### 2. Linux内核与发行版

Linux内核直接管理CPU、内存、磁盘、网卡和进程。Rocky Linux、Ubuntu Server等发行版在Linux内核外提供了可以直接安装和使用的完整系统。

安装完成后，将使用下面两条命令分别查看它们：

```bash
cat /etc/os-release
uname -r
```

- `cat /etc/os-release`查看发行版名称和版本。
- `uname -r`查看当前运行的Linux内核版本。

两条命令输出不同是正常现象，因为它们描述的不是同一个对象。

### 3. 常见Linux发行版家族

| 家族 | 常见发行版 | 软件包 | 高层包管理器 | 课程定位 |
|---|---|---|---|---|
| RHEL兼容生态 | RHEL、Rocky Linux、AlmaLinux | RPM | DNF | Rocky Linux作为课程主线 |
| RHEL上游生态 | CentOS Stream | RPM | DNF | 了解其与RHEL兼容发行版的关系 |
| Debian生态 | Debian、Ubuntu | DEB | APT | Ubuntu Server作为课程客户端，本实验完成第二台虚拟机安装 |

本课程选择Rocky Linux 9作为服务器主线，主要是为了接近RHEL企业服务器生态，并学习DNF、firewalld和SELinux等常见运维对象；同时安装Ubuntu Server作为独立客户端，用于后续SSH、Nginx和数据库的跨主机访问验证。Ubuntu不重复承担全部服务器配置任务，但其安装、网络配置和客户端工具使用属于必做内容。

### 4. Linux在本课程中的位置

Linux是后续服务器、虚拟化、容器和自动化运维的共同基础：

```text
Windows宿主机
└── VMware Workstation
    └── Rocky Linux虚拟机
        ├── Linux系统管理
        ├── 网络与SSH
        ├── Nginx、MySQL、MongoDB和Redis
        ├── Git与Shell巡检
        └── 后续Docker与容器化环境
```

本课程先让你学会管理Linux服务器；后续《虚拟化容器技术》再系统学习虚拟机管理、Docker、Dockerfile和Compose。

### 5. 什么是虚拟化

虚拟化通过软件把物理计算机的CPU、内存、磁盘和网卡等资源组织成一台或多台虚拟计算机。

| 名称 | 含义 | 本实验示例 |
|---|---|---|
| 物理机 | 真实存在的计算机硬件 | 机房学生电脑 |
| 宿主机 | 运行虚拟化软件的系统 | Windows 10/11 |
| Hypervisor | 创建和管理虚拟机的软件层 | VMware Workstation |
| 虚拟机 | 由软件定义的一台计算机 | 新建的Rocky Linux VM |
| 客户机系统 | 安装在虚拟机中的操作系统 | Rocky Linux 9 |
| 虚拟硬件 | 分配给虚拟机的vCPU、内存、磁盘和网卡 | 2 vCPU、4GB内存、40GB磁盘、NAT网卡 |

### 6. Type 1与Type 2虚拟化

```text
Type 1：硬件 → Hypervisor → 虚拟机
Type 2：硬件 → 宿主操作系统 → 虚拟化软件 → 虚拟机
```

Type 1 Hypervisor通常直接运行在服务器硬件上，常见于数据中心。Type 2虚拟化软件运行在Windows、macOS或Linux宿主操作系统中，适合个人计算机和教学实验。

VMware Workstation属于Type 2虚拟化软件。

### 7. ISO、虚拟磁盘、虚拟网卡与快照

| 对象 | 作用 | 注意事项 |
|---|---|---|
| ISO镜像 | 相当于操作系统安装光盘 | 安装完成后应避免再次从ISO启动 |
| 虚拟磁盘 | 以文件形式模拟硬盘 | 虚拟磁盘文件损坏会导致客户机数据不可用 |
| 虚拟网卡 | 把客户机接入VMware虚拟网络 | 本课程默认使用NAT |
| 快照 | 保存虚拟机某一时刻的状态，用于短期回退 | 快照依赖原虚拟机文件，不等于独立备份 |

## 四、实验环境

### 1. 宿主机要求

| 项目 | 最低要求 | 建议配置 |
|---|---:|---:|
| 操作系统 | Windows 10/11 64位 | Windows 11 64位 |
| CPU | 4个逻辑处理器，支持Intel VT-x或AMD-V | 8个或更多逻辑处理器 |
| 内存 | 8GB | 16GB及以上 |
| 可用磁盘 | 50GB | 100GB及以上SSD空间 |
| 虚拟化软件 | 教师指定版本的VMware Workstation | 统一使用机房验证版本 |

### 2. 实验文件

- VMware Workstation安装程序：由教师或机房统一提供。
- Rocky Linux 9最小化安装ISO：由教师提供已经验证过的Rocky Linux 9.x x86_64镜像。
- Ubuntu Server 22.04 LTS安装ISO：由教师提供已经验证过的amd64镜像。
- 两个镜像的SHA256校验值：由教师与ISO一起提供。

不要从来源不明的网站下载修改过的系统镜像或安装程序。

### 3. 虚拟机建议规格

Rocky Linux服务器：

| 配置项 | 建议值 | 说明 |
|---|---:|---|
| 名称 | `Rocky9-学号` | 例如`Rocky9-20260101` |
| 客户机类型 | Red Hat Enterprise Linux 9 64-bit | 与Rocky Linux 9兼容 |
| vCPU | 2 | 不要占用宿主机全部CPU |
| 内存 | 4GB | 后续数据库综合实验建议使用4GB |
| 虚拟磁盘 | 40GB | 采用动态增长方式即可 |
| 网络 | NAT | 便于统一教学和访问软件源 |
| 主机名 | `rocky-vm` | 后续多机实验再采用角色化命名 |
| 普通用户 | `student` | 勾选管理员权限或加入wheel组 |
| 密码 | 教师指定的实验密码 | 不使用个人常用密码 |

Ubuntu Server客户端：

| 配置项 | 建议值 | 说明 |
|---|---:|---|
| 名称 | `UbuntuClient-学号` | 例如`UbuntuClient-20260101` |
| 客户机类型 | Ubuntu 64-bit | 与安装镜像匹配 |
| vCPU | 2 | 与服务器并行运行时关注宿主机负载 |
| 内存 | 2GB | 仅作为命令行访问客户端 |
| 虚拟磁盘 | 30GB | 动态增长即可 |
| 网络 | NAT | 与Rocky连接到同一VMnet8 |
| 主机名 | `ubuntu-client` | 明确客户端角色 |
| 普通用户 | `student` | 安装时创建并具备sudo权限 |
| 密码 | 教师指定的实验密码 | 不使用个人常用密码 |

## 五、项目任务

1. 检查宿主机硬件和硬件虚拟化状态。
2. 准备安装程序、ISO和虚拟机保存目录。
3. 安装并检查VMware Workstation。
4. 按统一规格创建Rocky Linux虚拟机。
5. 完成Rocky Linux最小化安装。
6. 完成主机名、时区、用户、网络和VMware Tools检查。
7. 使用命令采集服务器环境基线。
8. 创建并验证Rocky服务器初始快照。
9. 创建并安装Ubuntu Server客户端。
10. 检查Ubuntu用户、网络、sudo和VMware Tools。
11. 创建Ubuntu客户端初始快照并完成双机基线。

### 课堂时间建议

本实验共4学时，即180分钟。教师应在课前把两份已校验ISO和VMware安装程序放入机房共享目录，避免课堂时间消耗在公网下载上。建议节奏如下：

| 用时 | 主要内容 |
|---:|---|
| 约25分钟 | Linux起源、UNIX/GNU/Linux关系、内核与发行版谱系 |
| 约20分钟 | 虚拟化、宿主机、客户机、Hypervisor和三种VMware网络模式 |
| 约20分钟 | 宿主机检查、VMware安装或版本核对、目录和ISO校验 |
| 约45分钟 | 创建并安装Rocky服务器，完成首次登录 |
| 约35分钟 | 创建并安装Ubuntu客户端，完成首次登录 |
| 约20分钟 | 双机DHCP、工具、时间、账号和基本互通检查 |
| 约15分钟 | 两台虚拟机快照、基线表和验收 |

两台系统的安装等待时间可以错峰利用：一台复制文件或安装软件包时，教师讲解另一台的配置差异或带领学生填写基线表。机房性能不足时可先关闭已装好的Rocky再安装Ubuntu，但不能把Ubuntu安装改成选做。停课或调课时优先压缩重复演示和拓展讨论，不省略双机安装、联网、快照和最终验收。

## 六、实验步骤

### 任务一：检查宿主机

#### 步骤1：检查Windows版本、内存和磁盘

在Windows中按`Win + R`，输入：

```text
msinfo32
```

打开“系统信息”后，记录：

- 操作系统名称和版本；
- 系统类型，应为基于x64的电脑；
- 处理器型号；
- 已安装的物理内存。

再打开“此电脑”，确认用于保存虚拟机的磁盘至少还有50GB可用空间。

> **验收点**：完成宿主机检查表，并确认虚拟机不会保存在空间不足的系统临时目录中。

#### 步骤2：检查硬件虚拟化

按`Ctrl + Shift + Esc`打开任务管理器，进入：

```text
性能 → CPU
```

检查右侧信息中的“虚拟化”：

```text
虚拟化：已启用
```

如果显示“已禁用”，不要继续创建虚拟机，应先由教师或机房管理员在BIOS/UEFI中启用Intel VT-x、Intel Virtualization Technology、SVM Mode或AMD-V。

> **验收点**：任务管理器显示硬件虚拟化已启用。

### 任务二：准备软件与目录

#### 步骤3：建立规范目录

在非系统盘建立课程目录，示例：

```text
D:\LinuxCourse\
├── ISO\
├── VMwareInstaller\
├── VirtualMachines\
└── Evidence\
```

目录用途：

- `ISO`：保存系统安装镜像；
- `VMwareInstaller`：保存虚拟化软件安装程序；
- `VirtualMachines`：保存虚拟机文件；
- `Evidence`：保存环境基线和必要的验收材料。

如果机房规定了统一磁盘和目录，以教师要求为准。

> **验收点**：四个目录均已建立，`VirtualMachines`所在磁盘可用空间满足要求。

#### 步骤4：核对ISO文件

将教师提供的Rocky Linux和Ubuntu Server ISO放入`ISO`目录。不要双击解压ISO文件。

在PowerShell中执行：

```powershell
Get-FileHash 'D:\LinuxCourse\ISO\Rocky-9.x-x86_64-minimal.iso' -Algorithm SHA256
Get-FileHash 'D:\LinuxCourse\ISO\ubuntu-22.04-live-server-amd64.iso' -Algorithm SHA256
```

将路径和文件名替换为实际值，然后把输出与教师提供的SHA256值比较。

校验值一致说明文件在传输过程中没有发生变化；不一致时应重新复制镜像。

> **验收点**：两个ISO文件均存在，SHA256分别与教师提供的值一致。

### 任务三：安装VMware Workstation

#### 步骤5：运行安装程序

1. 使用教师提供的VMware Workstation安装程序。
2. 右键安装程序，选择“以管理员身份运行”。
3. 接受许可协议。
4. 安装路径使用机房统一要求；不确定时保留默认路径。
5. 保留必要的网络和增强键盘组件。
6. 是否检查更新、是否参加体验改进计划按机房要求选择。
7. 完成安装并按提示重启Windows。

不同版本的授权和登录界面可能不同，按教师提供的合法使用方式完成，不使用来源不明的激活程序。

#### 步骤6：检查VMware服务和虚拟网络

启动VMware Workstation，确认主界面可以正常打开。

在Windows PowerShell执行：

```powershell
Get-Service | Where-Object {$_.Name -like 'VMware*'}
```

再执行：

```powershell
ipconfig
```

正常安装后通常可以看到VMware相关服务，以及VMware Network Adapter VMnet1和VMnet8等虚拟网卡。不同机房策略可能隐藏或调整部分组件，以教师实际环境为准。

本课程默认使用VMnet8对应的NAT网络。NAT的地址转换和三种网络模式将在后续课程中进一步学习。

> **验收点**：VMware Workstation可以启动，系统中存在可用的VMware虚拟网络组件。

### 任务四：创建Rocky Linux虚拟机

#### 步骤7：新建虚拟机

在VMware Workstation中选择“创建新的虚拟机”，依次设置：

| 页面 | 选择 |
|---|---|
| 配置类型 | 典型；机房使用统一自定义模板时按教师要求 |
| 安装来源 | 稍后安装操作系统 |
| 客户机操作系统 | Linux |
| 版本 | Red Hat Enterprise Linux 9 64-bit |
| 虚拟机名称 | `Rocky9-学号` |
| 保存位置 | `D:\LinuxCourse\VirtualMachines\Rocky9-学号` |
| 磁盘容量 | 40GB |
| 磁盘文件 | 单个文件或拆分均可，按机房统一要求 |

选择“稍后安装操作系统”可以先完成虚拟硬件检查，避免VMware使用未经确认的自动安装参数。

> **验收点**：VMware左侧出现新虚拟机，状态为已关闭，保存位置和名称正确。

#### 步骤8：调整虚拟硬件

进入“编辑虚拟机设置”，配置：

| 硬件 | 设置 |
|---|---|
| 内存 | 4096MB；宿主机只有8GB时可临时使用2048MB |
| 处理器 | 1个处理器、2个内核，总计2 vCPU |
| CD/DVD | 使用ISO映像文件，选择教师提供的Rocky Linux ISO |
| 网络适配器 | NAT |
| USB、声卡、打印机 | 非本课程必需，可按机房要求保留或移除 |

不要把宿主机全部CPU和内存分配给虚拟机。宿主机本身和VMware也需要资源。

> **验收点**：虚拟机规格为2 vCPU、建议4GB内存、40GB磁盘、NAT网卡，CD/DVD已挂载正确ISO。

### 任务五：安装Rocky Linux 9

#### 步骤9：从ISO启动

启动虚拟机。看到安装菜单后选择：

```text
Install Rocky Linux 9.x
```

如果虚拟机直接显示找不到操作系统，应关机后检查CD/DVD是否选择了正确ISO，并确认“启动时连接”。

> **验收点**：进入Rocky Linux安装程序，而不是出现“No operating system was found”。

#### 步骤10：设置安装参数

在安装摘要页面完成以下设置：

| 项目 | 建议设置 | 说明 |
|---|---|---|
| 语言 | English (United States) | 便于识别服务器英文日志和错误信息 |
| 键盘 | English (US) | 与机房键盘一致 |
| 时间和日期 | Asia/Shanghai | 保证日志时间正确 |
| 安装目标 | 选择40GB虚拟磁盘，自动分区 | 本课程不在首次安装时展开复杂分区 |
| 软件选择 | Minimal Install或最小化服务器环境 | 不安装图形桌面 |
| 网络 | 打开网卡，使用DHCP | 静态IP留到实验8系统学习 |
| 主机名 | `rocky-vm` | 使用小写字母和连字符 |
| Root账号 | 可锁定或设置教师指定实验密码 | 日常操作不直接使用root |
| 普通用户 | `student`，使用教师指定实验密码 | 勾选管理员权限，使其加入wheel组 |

确认目标磁盘是40GB虚拟磁盘。实验环境中的自动分区只会修改该虚拟磁盘，不应涉及Windows真实磁盘。

设置完成后开始安装，等待安装结束并重启虚拟机。

> **验收点**：系统重启后出现`rocky-vm login:`登录提示。

#### 步骤11：断开安装ISO

系统第一次重启后，检查VMware的CD/DVD设置。可以取消“启动时连接”，也可以将设备改回自动检测。

如果再次进入安装界面，关闭虚拟机，断开ISO后重新启动。不要再次执行安装。

### 任务六：首次登录与初始化检查

#### 步骤12：使用普通用户登录

在登录提示中输入：

```text
login: student
Password: 教师指定的实验密码
```

Linux输入密码时通常不显示星号或圆点，这是正常的安全设计。输入完成后按Enter。

登录成功后执行：

```bash
whoami
id
pwd
```

预期结果：

- `whoami`显示`student`；
- `id`的组列表中包含`wheel`；
- `pwd`显示`/home/student`。

> **验收点**：使用student登录成功，当前目录为student家目录，账号属于wheel组。

#### 步骤13：验证sudo权限

执行：

```bash
sudo -v
sudo whoami
```

输入`student`账号自己的密码。第二条命令应输出：

```text
root
```

这表示普通用户经过授权后可以临时以管理员身份执行命令，不表示当前Shell已经永久变成root。

> **验收点**：`sudo whoami`输出`root`，普通的`whoami`仍输出`student`。

#### 步骤14：检查发行版、内核和CPU架构

执行：

```bash
cat /etc/os-release
uname -r
uname -m
hostnamectl
```

重点记录：

- Rocky Linux发行版版本；
- Linux内核版本；
- CPU架构，x86-64环境通常显示`x86_64`；
- Static hostname，应为`rocky-vm`。

如果主机名不正确，执行：

```bash
sudo hostnamectl set-hostname rocky-vm
hostnamectl
```

> **验收点**：能够分别指出发行版版本、内核版本、CPU架构和主机名。

#### 步骤15：检查时间和时区

执行：

```bash
timedatectl
date
```

时区应为：

```text
Asia/Shanghai
```

如果时区不正确，执行：

```bash
sudo timedatectl set-timezone Asia/Shanghai
timedatectl
```

正确时间对日志分析、定时任务和故障复盘非常重要。

> **验收点**：时区为Asia/Shanghai，系统日期和时间没有明显错误。

### 任务七：检查网络和系统资源

#### 步骤16：查看IP地址和路由

执行：

```bash
ip -br address
ip route
```

找到状态为`UP`的网卡。常见名称包括`ens33`、`ens160`或`enp0s3`，不要假定所有计算机都使用同一个网卡名。

正常情况下应看到：

- 网卡处于`UP`状态；
- 网卡通过DHCP获得一个IPv4地址；
- 路由表中存在以`default via`开头的默认路由。

记录实际IP和默认网关，不要在本实验中强行改成固定示例地址。静态地址将在实验8中统一配置。

> **验收点**：记录实际网卡名、IPv4地址、前缀和默认网关。

#### 步骤17：验证局域网和名称解析

自动取得默认网关：

```bash
GATEWAY=$(ip route show default | awk 'NR==1 {print $3}')
printf 'default_gateway=%s\n' "$GATEWAY"
```

确认输出不是空值后，测试网关：

```bash
ping -c 3 "$GATEWAY"
```

检查名称解析：

```bash
getent hosts mirrors.rockylinux.org
```

如果机房不允许访问互联网，只要虚拟机获得实验网地址并能访问NAT网关，就可以完成本实验。公共域名解析和软件源状态应记录为“当前机房网络受限”，不能简单判断为Linux安装失败。

> **验收点**：虚拟机能访问NAT网关；互联网受限时已如实记录限制和本地网络验证结果。

#### 步骤18：查看CPU、内存和磁盘

执行：

```bash
lscpu | sed -n '1,20p'
free -h
lsblk -f
df -h
```

重点观察：

- 系统识别到多少vCPU；
- 总内存是否接近分配值；
- 虚拟磁盘、分区或逻辑卷之间的关系；
- 根文件系统挂载到哪里以及还有多少可用空间。

虚拟机中看到的是VMware提供的虚拟硬件，不是宿主机全部真实硬件。

> **验收点**：系统识别到2个vCPU、分配的内存和约40GB虚拟磁盘；能够指出根文件系统挂载点。

#### 步骤19：检查失败服务

执行：

```bash
systemctl --failed
```

正常情况下不应存在影响课程的失败服务。部分硬件相关服务在虚拟机中可能显示异常，应记录服务名称，不能仅为了清空列表而随意禁用。

> **验收点**：记录失败服务数量；存在失败服务时保留名称和状态供教师检查。

### 任务八：检查VMware Tools和基础软件

#### 步骤20：检查open-vm-tools

执行：

```bash
rpm -q open-vm-tools
systemctl is-active vmtoolsd
```

如果已经安装并运行，预期看到软件包版本和：

```text
active
```

如果没有安装，而且课程软件源可用，执行：

```bash
sudo dnf install -y open-vm-tools
sudo systemctl enable --now vmtoolsd
systemctl is-active vmtoolsd
```

如果软件源暂时不可用，记录问题并使用教师提供的离线方案。本实验不能因为公共网络不可用而要求学生重装系统。

> **验收点**：vmtoolsd处于active；暂时无法安装时已经记录原因和待处理项。

#### 步骤21：安装或检查课程基础工具

先检查：

```bash
for cmd in vim curl wget git tar; do
    command -v "$cmd" || printf 'MISSING %s\n' "$cmd"
done
```

如果显示缺少命令且软件源可用，执行：

```bash
sudo dnf install -y vim curl wget git tar bash-completion
```

再次运行检查命令，确认缺失项已经消失。

不要在首次安装后直接执行没有版本和回退计划的全系统大规模升级。课程需要的软件更新由教师统一安排。

> **验收点**：记录基础工具检查结果；缺失工具已安装或已有明确的离线补充安排。

### 任务九：创建初始快照

#### 步骤22：关闭虚拟机并创建快照

先保存所有记录，然后执行：

```bash
sudo poweroff
```

等待VMware显示虚拟机已关闭，再创建快照：

```text
快照名称：00-Rocky9-安装与初始化完成
描述：Rocky Linux 9最小化安装；student账号；NAT DHCP；基础工具检查完成
```

快照菜单位置会随VMware版本变化，通常位于“虚拟机”菜单或快照管理器中。

快照完成后重新启动虚拟机，确认仍能使用`student`登录。

> **验收点**：快照管理器中存在名称正确的快照，虚拟机重启后能够正常登录。

#### 步骤23：完成服务器环境基线表

将下面表格复制到个人实验记录中，并填写实际值：

| 项目 | 实际值 |
|---|---|
| 学号和姓名 |  |
| 宿主机操作系统 |  |
| 宿主机内存 |  |
| 宿主机硬件虚拟化 | 已启用 / 未启用 |
| VMware版本 |  |
| 虚拟机名称 |  |
| 虚拟机保存位置 |  |
| vCPU |  |
| 虚拟内存 |  |
| 虚拟磁盘 |  |
| 网络模式 |  |
| Linux发行版 |  |
| Linux内核版本 |  |
| CPU架构 |  |
| 主机名 |  |
| 当前普通用户 |  |
| 网卡名 |  |
| IPv4地址和前缀 |  |
| 默认网关 |  |
| 根文件系统可用空间 |  |
| 失败服务数量 |  |
| VMware Tools状态 |  |
| 初始快照名称 |  |

### 任务十：安装Ubuntu Server客户端

Rocky服务器基线记录完成后，可以暂时关闭Rocky以释放宿主机内存，再创建Ubuntu客户端。

#### 步骤24：创建Ubuntu客户端虚拟机

在VMware Workstation选择“创建新的虚拟机”，按下表设置：

| 页面或硬件 | 设置 |
|---|---|
| 安装方式 | 稍后安装操作系统 |
| 客户机类型 | Linux / Ubuntu 64-bit |
| 虚拟机名称 | `UbuntuClient-学号` |
| 保存位置 | `D:\LinuxCourse\VirtualMachines\UbuntuClient-学号` |
| vCPU | 2 |
| 内存 | 2048MB |
| 虚拟磁盘 | 30GB，动态增长 |
| CD/DVD | 教师提供的Ubuntu Server 22.04 ISO |
| 网络适配器 | NAT，与Rocky使用同一VMnet8 |

> **验收点**：Ubuntu虚拟机名称、保存目录、ISO和NAT网卡正确，不与Rocky共用虚拟磁盘。

#### 步骤25：完成Ubuntu Server安装

启动虚拟机，进入Ubuntu Server安装程序。不同小版本的界面文字可能略有区别，按以下原则配置：

| 项目 | 设置 | 说明 |
|---|---|---|
| 语言与键盘 | English / English (US) | 便于识别英文日志 |
| 安装类型 | Ubuntu Server | 不安装图形桌面 |
| 网络 | DHCP自动获取 | 静态地址在实验8统一配置 |
| 代理 | 机房没有代理时留空 | 不照抄他人代理地址 |
| 镜像源 | 教师验证的地址 | 无网络时使用离线方案 |
| 存储 | 使用30GB虚拟磁盘 | 核对目标，允许默认LVM布局 |
| 主机名 | `ubuntu-client` | 明确客户端角色 |
| 用户名 | `student` | 使用教师指定实验密码 |
| OpenSSH Server | 勾选安装 | 后续可进行双向SSH练习 |
| 额外软件 | 暂不选择 | 需要时再使用APT安装 |

安装结束后选择重启。若提示移除安装介质，在VMware中断开Ubuntu ISO，然后按Enter继续。

> **验收点**：重启后出现Ubuntu登录提示，能够使用`student`登录。

#### 步骤26：检查Ubuntu客户端基线

登录后执行：

```bash
whoami
id
sudo whoami
cat /etc/os-release
uname -r
hostnamectl
ip -brief address
ip route
free -h
df -h /
```

预期：

- `whoami`输出`student`；
- `sudo whoami`输出`root`；
- `/etc/os-release`显示Ubuntu 22.04 LTS；
- 主机名为`ubuntu-client`；
- NAT网卡通过DHCP获得IPv4地址；
- 存在默认路由。

检查NAT网关和名称解析：

```bash
GATEWAY=$(ip route show default | awk 'NR==1 {print $3}')
printf 'gateway=%s\n' "$GATEWAY"
ping -c 3 "$GATEWAY"
getent hosts ubuntu.com
```

公共名称受机房网络限制时，以教师提供的校内名称为准，不因公共站点失败直接重装系统。

#### 步骤27：检查VMware Tools和客户端工具

```bash
systemctl status open-vm-tools --no-pager || true
command -v ssh
command -v scp
command -v curl
```

若`open-vm-tools`或基础客户端缺失，且APT源可用：

```bash
sudo apt update
sudo apt install -y open-vm-tools openssh-client curl
sudo systemctl enable --now open-vm-tools
```

> **验收点**：VMware Tools、SSH客户端和curl可用；软件源不可用时已经保留错误信息并使用教师离线方案。

#### 步骤28：创建Ubuntu初始快照

```bash
sudo poweroff
```

虚拟机完全关闭后创建快照：

```text
快照名称：00-UbuntuClient-安装与初始化完成
描述：Ubuntu Server 22.04客户端；student账号；NAT DHCP；SSH客户端与curl检查完成
```

重新启动Ubuntu，确认仍能登录。

#### 步骤29：完成客户端基线表

| 项目 | 实际值 |
|---|---|
| 虚拟机名称和保存位置 |  |
| vCPU、内存、磁盘 |  |
| Ubuntu发行版版本 |  |
| Linux内核版本 |  |
| 主机名 |  |
| 普通用户与sudo |  |
| 网卡名 |  |
| DHCP IPv4地址和前缀 |  |
| 默认网关 |  |
| SSH客户端版本 |  |
| curl版本 |  |
| VMware Tools状态 |  |
| 初始快照名称 |  |

最后同时启动两台虚拟机，分别执行`ip -brief address`，确认地址不重复。实验1只验证两台机器都能接入NAT网络；稳定静态地址和双机互通在实验8完成。

## 七、独立实践

不要直接复制教材原句，使用自己的话回答：

1. Linux内核版本和Rocky Linux发行版版本为什么不同？分别使用什么命令查看？
2. VMware Workstation属于Type 1还是Type 2虚拟化？它运行在哪一层？
3. 虚拟机配置40GB虚拟磁盘后，Windows磁盘为什么不一定立即减少完整40GB？
4. 为什么快照适合实验回退，却不能代替独立备份？
5. 为什么本实验先使用DHCP，而不是直接照抄`192.168.200.10`？
6. 普通用户执行`sudo whoami`得到root，与直接长期登录root有什么区别？
7. 后续服务为什么使用Ubuntu客户端访问Rocky服务器，而不只在服务器本机测试？

## 八、验收标准

- [ ] 能简要说明UNIX、GNU、Linux内核和Linux发行版的关系。
- [ ] 能区分Rocky Linux发行版版本与Linux内核版本。
- [ ] 能说明Rocky Linux、RHEL、CentOS Stream和Ubuntu分属什么生态。
- [ ] 能区分宿主机、Hypervisor、虚拟机和客户机系统。
- [ ] Windows任务管理器显示硬件虚拟化已启用。
- [ ] VMware Workstation能够正常启动并存在可用NAT网络组件。
- [ ] Rocky Linux虚拟机规格、名称和保存位置符合要求。
- [ ] Rocky Linux能够启动到命令行并使用student登录。
- [ ] Rocky中的student属于wheel组，`sudo whoami`能够输出root。
- [ ] 主机名为`rocky-vm`，时区为`Asia/Shanghai`。
- [ ] Ubuntu Server客户端规格、名称和保存位置符合要求。
- [ ] Ubuntu能够使用student登录并通过sudo获得临时管理权限。
- [ ] Ubuntu主机名为`ubuntu-client`，SSH客户端和curl可用。
- [ ] 两台虚拟机均获得不重复的IPv4地址，存在默认路由，并能访问NAT网关。
- [ ] 能使用命令查看CPU、内存、磁盘和根文件系统空间。
- [ ] 已记录两台系统的VMware Tools状态。
- [ ] 已创建并验证Rocky和Ubuntu两个初始快照。
- [ ] 双机环境基线表填写完整，内容来自实际命令结果。

## 九、成果提交

提交一个以“学号-姓名-实验01”命名的目录，至少包含：

```text
学号-姓名-实验01/
├── README.md             # 独立实践7个问题的回答
├── host-check.md         # 宿主机与VMware检查结果
├── server-baseline.md    # Rocky Linux服务器环境基线表
├── client-baseline.md    # Ubuntu Server客户端环境基线表
└── evidence/             # 必要界面证据，不要求堆积重复截图
```

`evidence`建议保留：

1. Windows任务管理器“虚拟化：已启用”。
2. VMware中的两台虚拟机硬件规格。
3. Rocky Linux和Ubuntu Server登录后的关键基线结果。
4. VMware快照管理器中的两个初始快照。

截图应同时包含操作对象和关键结果，不能只截取一个“成功”提示。

## 十、常见问题

### Q1：任务管理器显示“虚拟化：已禁用”怎么办？

不要继续尝试安装客户机。先进入BIOS/UEFI启用Intel Virtualization Technology、VT-x、SVM Mode或AMD-V。机房计算机无法自行修改时联系教师或管理员。

### Q2：VMware提示与Hyper-V、VBS或内存完整性冲突怎么办？

不同VMware和Windows版本的兼容情况不同。记录完整错误信息，由教师使用机房统一方案处理。不要自行删除Windows安全组件或执行来源不明的系统修改脚本。

### Q3：虚拟机启动后提示找不到操作系统怎么办？

关闭虚拟机并检查：

1. CD/DVD是否选择了与当前虚拟机匹配的Rocky或Ubuntu ISO；
2. 是否勾选“启动时连接”；
3. ISO校验值是否正确；
4. 启动顺序是否允许从CD/DVD启动。

### Q4：安装结束后又回到安装界面怎么办？

虚拟机再次从ISO启动了。关闭虚拟机，断开CD/DVD中的ISO，再从虚拟磁盘启动。不要重复安装。

### Q5：输入Linux密码时屏幕没有显示字符，是不是键盘坏了？

不是。Linux终端输入密码时默认不显示字符、圆点或星号。正常输入后按Enter即可。

### Q6：student不能使用sudo怎么办？

先执行：

```bash
id student
```

检查是否包含`wheel`组。若安装时没有勾选管理员权限，由教师通过root或恢复模式将student加入wheel组：

```bash
usermod -aG wheel student
```

重新登录后再检查`id`。不要在无法确认管理员账号的情况下随意修改sudo配置。

### Q7：虚拟机没有IPv4地址怎么办？

依次检查：

```bash
ip -br link
nmcli device status
nmcli connection show --active
```

然后检查VMware中网络适配器是否存在、是否勾选“已连接”和“启动时连接”、网络模式是否为NAT。静态IP问题留到实验8处理，不要在本实验照抄其他同学的IP。

### Q8：能访问网关，但软件安装失败怎么办？

网关可达只能证明局域网路径基本正常。继续检查：

```bash
getent hosts mirrors.rockylinux.org
sudo dnf repolist
```

可能原因包括DNS、软件源、代理、校园网策略或公共镜像站不可用。保留错误信息并使用教师提供的软件源或离线包，不要直接重装系统。

### Q9：虚拟机运行很卡怎么办？

检查宿主机剩余内存和磁盘空间，不要同时启动无关软件。如果宿主机只有8GB内存，安装阶段可以只启动一台虚拟机；需要双机验证时可暂时将Rocky和Ubuntu分别调整为2GB和1.5—2GB。到数据库综合实验前再按教师安排提高Rocky内存或分组使用环境。

### Q10：快照创建后虚拟机文件是不是可以删除？

不可以。快照依赖原虚拟机的配置和虚拟磁盘链。删除原虚拟机文件后，快照通常无法独立恢复。

## 十一、课后思考与拓展

1. 如果直接在物理机安装Rocky Linux，与在VMware中安装相比，各有什么优缺点？
2. 为什么服务器教学通常采用最小化安装，而不是默认安装图形桌面？
3. 查阅课程教材，说明Type 1虚拟化为什么更常用于数据中心。
4. 对比RPM/DNF和DEB/APT，它们分别属于哪些发行版生态？

## 十二、环境保留

- 保留Rocky Linux服务器和Ubuntu Server客户端，不执行清理。
- 保留两个ISO原文件和SHA256记录。
- 保留两台虚拟机的初始快照，不在该快照上反复创建长期分支。
- 下一实验继续使用两台机器的`student`账号和当前NAT网络。
- 不要提前配置固定IP；静态网络配置将在实验8完成。
