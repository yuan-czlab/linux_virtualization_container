# Lab05：目录导航与探索

> 课时：2 | 类型：个人 | 前置：Lab04

## 一、你会学到什么
- 能画出 Linux 文件系统层次结构（FHS）的关键目录
- 能说出 /etc /var /usr /home /tmp /proc /dev 各自存什么
- 能在陌生系统中快速定位配置文件、日志、可执行文件

## 二、实验环境
- Rocky Linux 9 VM，以 student 用户登录

## 三、实验核心概念

```
/                   根目录，一切从这里开始
├── /bin            基本命令（软链接到 /usr/bin）
├── /boot           内核和引导文件
├── /dev            设备文件（一切皆文件）
├── /etc            配置文件（系统的"设置"菜单）
├── /home           普通用户的家目录
│   └── student/    你的家目录（~）
├── /root           root 用户的家目录
├── /run            运行时数据（内存中，重启就没了）
├── /tmp            临时文件（所有人可写，重启可能清空）
├── /usr            用户软件和库（/usr/bin, /usr/lib）
├── /var            经常变化的数据（日志/缓存/数据库）
└── /proc           进程和内核信息（虚拟文件系统，在内存中）
```

## 四、实验步骤

### 步骤1：探索 /etc — 系统的设置面板

```bash
cd /etc
ls -l | head -20

# 看几个关键配置文件的前几行
head -5 /etc/passwd          # 用户账号数据库
head -5 /etc/group           # 用户组数据库
head -5 /etc/shadow          # 用户密码哈希（需要 sudo）
sudo head -5 /etc/shadow     # 和 /etc/passwd 对比，密码字段在哪？
cat /etc/hostname            # 你的主机名
cat /etc/os-release          # 系统版本信息
cat /etc/resolv.conf         # DNS 配置
```

练习：
```bash
# 1. 查看 /etc/passwd，找到你的账号 student 的那一行
grep student /etc/passwd

# 2. 解释这一行各个字段（用 : 分隔的）
# student:x:1000:1000:student:/home/student:/bin/bash
#    ①     ②  ③   ④     ⑤        ⑥           ⑦
# ①用户名 ②密码占位符(x表示密码在shadow) ③UID ④GID ⑤描述 ⑥家目录 ⑦登录Shell

# 3. 查看 /etc/ssh/sshd_config，找到 Port 和 PermitRootLogin
grep -E "^(Port|PermitRootLogin)" /etc/ssh/sshd_config
```

> **验收点**：能解释 /etc/passwd 一行 7 个字段的含义。

### 步骤2：探索 /var — 系统的"变化数据"

```bash
cd /var/log
ls -lh

# 查看系统主日志
sudo tail -20 /var/log/messages    # 系统主日志

# 查看安全相关日志
sudo tail -10 /var/log/secure      # SSH 登录/认证日志

# 查看 dnf 包管理日志
sudo tail -10 /var/log/dnf.log

# 查看 last 命令对应的登录日志
last | head -10                     # 最近登录记录
sudo lastb | head -5                # 最近登录失败记录（如果有）
```

练习：
```bash
# 用一条命令查看 /var/log/messages 中包含 "error" 的行（不区分大小写）
sudo grep -i error /var/log/messages | tail -10
```

> **验收点**：能独立查看 `/var/log/secure` 找到自己刚才的登录记录。

### 步骤3：探索 /proc 和 /sys — 系统内核的"窗口"

```bash
# /proc 是虚拟文件系统，内容在内存中
cd /proc

# CPU 信息
cat /proc/cpuinfo | head -10
grep "model name" /proc/cpuinfo | head -1
grep -c processor /proc/cpuinfo   # CPU 核心数

# 内存信息
cat /proc/meminfo | head -5
free -h                            # 更友好的内存查看

# 内核版本与参数
cat /proc/version
cat /proc/cmdline                  # 内核启动参数

# 系统运行信息
cat /proc/uptime                   # 运行秒数
cat /proc/loadavg                  # 系统负载

# 查看当前 shell 的进程信息
echo $$                            # 当前 shell 的 PID
cat /proc/$$/status | head -10     # 当前进程状态
ls /proc/$$/fd/                    # 当前进程打开的文件描述符
```

练习：
```bash
# 查看你的 Rocky VM 有多少 CPU 核心、多少内存
grep -c processor /proc/cpuinfo
grep MemTotal /proc/meminfo
```

> **验收点**：能说出 /proc 和 /etc 的本质区别（/proc 是内核数据在内存中的映射，/etc 是磁盘上的真实文件）。

### 步骤4：探索 /dev — 设备文件

```bash
cd /dev
ls | head -20

# 磁盘设备
ls -l sd*                     # SATA/SAS 磁盘
ls -l /dev/disk/by-uuid/      # 按 UUID 访问磁盘

# 特殊设备
ls -l /dev/null               # 数据黑洞（写入即丢弃）
ls -l /dev/zero               # 无限输出零字节
ls -l /dev/random             # 随机数

# 实验：感受 /dev/null
echo "hello" > /dev/null      # 输出被丢弃
cat /dev/null                 # 读取永远是空

# 实验：感受 /dev/zero
dd if=/dev/zero of=/tmp/testfile bs=1M count=10 2>/dev/null
ls -lh /tmp/testfile          # 生成了一个 10MB 全是零的文件
rm /tmp/testfile
```

> **验收点**：能解释"一切皆文件"——连磁盘、终端、黑洞都是一个文件路径。

### 步骤5：目录探索挑战

不借助任何资料，根据你对 FHS 的理解，找到以下内容：

| 任务 | 提示 | 写下你找到的路径 |
|------|------|----------------|
| 找到 nginx（或 httpd）的配置文件 | 在 /etc 下 | |
| 找到系统安装过的 yum/dnf 仓库定义 | 在 /etc 下 | |
| 找到网卡的配置文件 | 在 /etc 下 | |
| 找到当前内核文件 | 在 /boot 下 | |
| 找到你的家目录下的隐藏文件 | ~ 下以 . 开头 | |
| 找到 /tmp 下你之前留下的文件 | /tmp | |

```bash
# 验证你的答案：
ls /etc/nginx/                     # nginx 配置（如果装了的话）
ls /etc/yum.repos.d/               # dnf 仓库
ls /etc/NetworkManager/system-connections/  # 网卡配置（或 /etc/sysconfig/network-scripts/）
ls /boot/vmlinuz-*                 # 内核文件
ls -la ~                           # 隐藏文件
ls /tmp/
```

> **验收点**：至少答对 5/6 题。

## 五、验收标准
- [ ] 能手绘 FHS 的 10 个关键目录（/etc /var /usr /home /root /tmp /boot /dev /proc /run）
- [ ] 能说出 /etc/passwd 一行 7 个字段的含义
- [ ] 能在 /var/log 中找到并查看至少 3 种不同的日志文件
- [ ] 能用 /proc/cpuinfo 和 /proc/meminfo 查看 CPU 和内存信息
- [ ] 理解 /dev/null 的作用（数据丢弃）
- [ ] 完成目录探索挑战 6 题中的 5 题

## 六、常见问题

**Q: /proc 下的文件用 vim 打开修改会怎样？**
A: 有些只读（改了报错），有些可写（改了会立即改变内核行为）。比如 `echo 1 > /proc/sys/net/ipv4/ip_forward` 会立即开启 IP 转发。但重启后恢复，永久修改要改 /etc/sysctl.conf。

**Q: /usr 和 /usr/local 什么区别？**
A: /usr 是包管理器（dnf/yum）管理的软件；/usr/local 是管理员手动编译安装的软件。这样包管理器不会覆盖你手动装的东西。

**Q: 怎么记住这么多目录？**
A: 不用背，查 `man hier`。但 /etc（配置）、/var/log（日志）、/home（用户）、/tmp（临时）这 4 个必须记住——运维每天打交道。
