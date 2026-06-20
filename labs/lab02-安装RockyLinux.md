# Lab02：VMware 安装 Rocky Linux 9

> 课时：2 | 类型：个人 | 前置：Lab01

## 一、你会学到什么
- 能独立完成 Rocky Linux 9 的最小化安装
- 会配置静态 IP 地址
- 能在纯命令行环境（无桌面）中完成系统初始化
- 会用 dnf 完成第一次系统更新

## 二、实验环境
- 宿主机：Windows 10/11，VMware Workstation 17 Pro
- 安装镜像：Rocky-9.4-x86_64-minimal.iso（教师提供，放在 D:\ISO\）
- 宿主机剩余磁盘空间 ≥ 30GB

## 三、实验拓扑
```
宿主机 (Windows 10)
  └── VMware
        ├── Ubuntu-22.04 VM (Lab01 创建的)
        └── Rocky-9 VM (本次创建)
              IP: 192.168.200.10/24
              GW: 192.168.200.2
              DNS: 223.5.5.5
```

⚠️ **重点**：Rocky Linux 这次装**最小化版（无桌面）**。后续所有课程都以命令行方式操作，这是运维的日常工作模式。

## 四、实验步骤

### 步骤1：创建虚拟机
VMware 中新建虚拟机：

| 配置项 | 值 |
|--------|-----|
| 客户机操作系统 | Linux → Red Hat Enterprise Linux 9 64 位 |
| 虚拟机名称 | `Rocky-9-学号` |
| 磁盘容量 | 30GB（单文件） |
| 内存 | 2GB |
| 处理器 | 2 核 |
| 网络 | NAT |

> **验收点**：VMware 左侧出现你的 Rocky VM。

### 步骤2：挂载 ISO 并开始安装
1. 挂载 `Rocky-9.4-x86_64-minimal.iso`
2. 启动虚拟机
3. 在 GRUB 菜单选择 "Install Rocky Linux 9.4" 回车

> **验收点**：进入 Rocky Linux 图形化安装向导（Anaconda）。

### 步骤3：安装配置

**3.1 语言**：English (United States)

⚠️ **为什么不选中文？** 命令行环境中文可能显示乱码，且生产服务器默认都是英文。学生需要适应英文错误信息。

**3.2 Installation Destination**（磁盘分区）：
- 选择 30GB 虚拟磁盘 → 勾选 "Custom" → Done
- 选择 "Standard Partition" 方案，手动创建：

| 挂载点 | 大小 | 文件系统 | 说明 |
|--------|------|---------|------|
| /boot | 1G | xfs | 引导分区 |
| / | 15G | xfs | 根分区 |
| /home | 8G | xfs | 用户目录 |
| swap | 2G | swap | 交换分区 |
| 剩余空间 | 约4G | — | 留给后面 LVM 实验用 |

点击 Done → Accept Changes

**3.3 Root Password**：
- 设置 root 密码：`redhat123`
- 不勾选 "Lock root account"

**3.4 User Creation**：
- Full name: `student`
- Username: `student`
- Password: `student123`
- 勾选 "Make this user administrator"（自动加入 wheel 组）

**3.5 Network & Host Name**：
- Host name: `rocky-vm`
- 先不配置网络（等安装完成后手动配置）

**3.6 Software Selection**：
- 保持默认 "Server"（最小化安装，无桌面）

> 一切无误后点 Begin Installation → 等待完成 → Reboot System

> **验收点**：重启后看到一个纯黑色的命令行登录提示：`rocky-vm login: _`

### 步骤4：首次登录与网络配置
用 student 账号登录：

```bash
rocky-vm login: student
Password: student123
```

查看当前网络状态：
```bash
ip addr show
# 或简写
ip a
```

你会看到网卡（通常是 ens33 或 ens160）没有 IPv4 地址，因为默认是 DHCP 但可能没获取到。手动配置静态 IP：

```bash
# 切换到 root
sudo -i

# 查看网卡名称
nmcli device status

# 假设网卡名称是 ens33，创建静态 IP 连接
nmcli connection add type ethernet con-name static-net ifname ens33 \
  ipv4.addresses 192.168.200.10/24 \
  ipv4.gateway 192.168.200.2 \
  ipv4.dns 223.5.5.5 \
  ipv4.method manual

# 激活连接
nmcli connection up static-net

# 验证
ip a | grep 192.168
ping -c 3 223.5.5.5
```

> **验收点**：`ip a` 能看到 `192.168.200.10`；`ping 223.5.5.5` 通。

### 步骤5：系统更新与基础工具
```bash
# 更新系统
dnf update -y

# 安装基础工具（这些后续实验都要用）
dnf install -y vim bash-completion man-pages \
  net-tools lsof wget curl \
  epel-release

# 启用 bash 补全
echo 'source /etc/bash_completion' >> ~/.bashrc
source ~/.bashrc

# 验证
dnf --version
vim --version | head -1
```

> **验收点**：`dnf update` 完成无报错；`vim` 能正常打开；Tab 补全能提示命令和路径。

## 五、验收标准
- [ ] Rocky Linux 9 启动后进入命令行登录界面
- [ ] 能用 `student` 账号登录
- [ ] `ip a` 显示静态 IP `192.168.200.10/24`
- [ ] `ping 223.5.5.5` 通（网络正常）
- [ ] `dnf update` 成功连接软件源并完成更新
- [ ] `vim --version` 能正常输出（vim 已安装）
- [ ] Tab 补全功能正常（输入 `syst` 按 Tab 能补全为 `systemctl`）

## 六、常见问题

**Q: Rocky Linux 安装界面鼠标不能用？**
A: VMware 中按 Ctrl+Alt 释放鼠标，用 Tab/方向键/空格/Enter 纯键盘操作安装向导。

**Q: 安装完成后重启直接黑屏？**
A: 等 30 秒，最小化安装首次启动慢（在初始化服务）。如果超过 2 分钟没反应，强制重启。

**Q: nmcli 配置网络后 ping 不通？**
A: 检查 VMware 虚拟网络编辑器 → NAT 模式的子网地址是否也是 `192.168.200.0`。如果不一致，把 VM 的 IP 改为与 NAT 子网同网段。或者更简单的——把连接方式改为 DHCP：
```bash
nmcli connection add type ethernet con-name auto-net ifname ens33 ipv4.method auto
nmcli connection up auto-net
```

**Q: 为什么要学生先在 / 分区后面留 4GB 未分配空间？**
A: 为 Lab21（LVM 逻辑卷管理）预留实验空间，到时候教学生如何在已有系统中用未分配空间创建 LVM。

## 七、清理环境
本实验不清理。这台 Rocky VM 是后续所有实验的核心环境。

---

## 备忘：Ubuntu vs Rocky 快速对照（讲课时用）

| 维度 | Ubuntu 22.04 | Rocky Linux 9 |
|------|-------------|---------------|
| 所属家族 | Debian 系 | RHEL 系 |
| 包管理器 | apt（.deb） | dnf（.rpm） |
| 默认桌面 | GNOME（完整） | 最小化安装无桌面 |
| 内核版本 | 6.x（HWE） | 5.14（长期稳定） |
| 更新策略 | 激进 | 保守 |
| 企业使用 | 互联网/AI 公司多 | 银行/国企/传统企业多 |
| systemd | ✓ | ✓ |
| SELinux | AppArmor（默认） | SELinux（默认） |
| 配置文件风格 | /etc/apt/sources.list | /etc/yum.repos.d/*.repo |
