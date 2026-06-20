# Lab03：Ubuntu vs Rocky 命令对比

> 课时：2 | 类型：个人 | 前置：Lab01 + Lab02（两台 VM 都装好）

## 一、你会学到什么
- 能对比 Ubuntu（apt）和 Rocky（dnf）的包管理操作，手写出对应命令
- 能在两台不同发行版之间快速切换，不被"换了系统就不会用"卡住
- 能看懂 `PATH` 环境变量，知道命令从哪来
- 会查看系统版本、内核版本、已安装软件包

## 二、实验环境
- VM1：Ubuntu 22.04（Lab01），IP 随意（DHCP 即可）
- VM2：Rocky Linux 9（Lab02），IP 192.168.200.10

## 三、实验步骤

### 步骤1：基础系统信息对比

分别在两台 VM 上执行以下命令，**把输出填到表格里**：

```bash
# 系统版本
cat /etc/os-release | head -3

# 内核版本
uname -r

# 主机名
hostnamectl

# 当前运行级别/目标
systemctl get-default
```

| 对比项 | Ubuntu 22.04（填入实际输出） | Rocky Linux 9（填入实际输出） |
|--------|---------------------------|---------------------------|
| 系统版本 | | |
| 内核版本 | | |
| 默认运行目标 | | |

> **验收点**：两个 VM 的输出不同，能说出哪条是哪条。

### 步骤2：包管理命令对照 ⭐

这是本实验最核心的部分。**先在 Rocky 上执行左列，再在 Ubuntu 上执行右列**：

| 操作 | Rocky（dnf） | Ubuntu（apt） |
|------|-------------|---------------|
| 更新软件包列表 | `sudo dnf check-update` | `sudo apt update` |
| 升级所有软件包 | `sudo dnf update -y` | `sudo apt upgrade -y` |
| 搜索软件包 | `dnf search nginx` | `apt search nginx` |
| 查看软件包信息 | `dnf info nginx` | `apt show nginx` |
| 安装软件包 | `sudo dnf install -y nginx` | `sudo apt install -y nginx` |
| 卸载软件包 | `sudo dnf remove nginx` | `sudo apt remove nginx` |
| 查看已安装 | `dnf list installed \| wc -l` | `apt list --installed \| wc -l` |
| 清理缓存 | `sudo dnf clean all` | `sudo apt clean` |
| 查看仓库列表 | `dnf repolist` | `cat /etc/apt/sources.list` |

在 Rocky 上安装 nginx 测试：
```bash
sudo dnf install -y nginx
rpm -qi nginx          # 查看已安装包详细信息
rpm -ql nginx | head   # 查看包安装的文件列表
```

在 Ubuntu 上安装 nginx 测试：
```bash
sudo apt install -y nginx
dpkg -s nginx | head    # 查看已安装包详细信息
dpkg -L nginx | head    # 查看包安装的文件列表
```

> **验收点**：能不看文档，口头说出 dnf 和 apt 五个常用操作的对应命令。

### 步骤3：命令本质 — PATH 与命令位置

在两台 VM 上都执行：
```bash
# 查看 PATH 环境变量
echo $PATH

# 查看某个命令的实际位置
which ls
which vim
which systemctl

# 查看命令类型（内置/外部/别名）
type ls
type cd
type which
type ll   # Ubuntu 上有可能是别名
```

在 Rocky 上额外执行：
```bash
# 看看 /usr/bin 下有多少可执行文件
ls /usr/bin | wc -l

# 查看一个命令到底来自哪个包
rpm -qf /usr/bin/which     # Rocky
dpkg -S /usr/bin/which     # Ubuntu
```

> **验收点**：能解释为什么不同发行版的 `which vim` 可能返回不同路径，但结果仍然正确。

### 步骤4：服务管理对比

在两台 VM 上都执行：
```bash
# 查看所有已启用的服务
systemctl list-unit-files --type=service --state=enabled

# 查看服务数量
systemctl list-units --type=service | wc -l
```

> **验收点**：两台 VM 的服务数量不同，这是正常的——发行版默认安装的软件不同。

### 步骤5：目录结构差异

在两台 VM 上对比以下路径：

```bash
# 网卡配置文件
ls /etc/netplan/          # Ubuntu
ls /etc/NetworkManager/   # Rocky
ls /etc/sysconfig/network-scripts/  # Rocky（旧版 CentOS 风格）

# 软件源配置
ls /etc/apt/              # Ubuntu
ls /etc/yum.repos.d/      # Rocky

# 系统日志
ls /var/log/
```

> **验收点**：能说出至少 3 个 Ubuntu 和 Rocky 的目录结构差异。

## 五、验收标准
- [ ] 能独立在 Rocky 上完成 `dnf install nginx`，在 Ubuntu 上完成 `apt install nginx`
- [ ] 能口头说出 dnf 和 apt 的五个常用操作对应关系（教师抽查）
- [ ] 能解释 `PATH` 的作用：shell 在哪找命令
- [ ] 能说出至少 3 个 Ubuntu 和 Rocky 的实际差异（包管理/网络配置路径/默认软件）
- [ ] 在两台 VM 上都成功执行了 `systemctl` 相关命令

## 六、常见问题

**Q: 命令在两个系统上输出格式不一样？**
A: 对，这是正常的。比如 `rpm -qi` 输出是单行紧凑格式，`dpkg -s` 是多行缩进格式。运维需要习惯不同系统的"方言"。

**Q: `dnf search nginx` 在 Rocky 上找不到包？**
A: 先执行 `sudo dnf update` 更新缓存。如果还找不到，检查是否装了 epel-release：`sudo dnf install -y epel-release`。

**Q: 为什么有些命令在一个系统有、另一个没有？**
A: 因为默认安装的软件包集合不同。`netstat` 在 Rocky 上可能默认装了（来自 net-tools），Ubuntu 可能需要手动装。不同发行版的"最小安装"定义不同。

## 七、课后思考
- Google 或百度搜索"CentOS 停止维护 2024"，写一段话说明为什么现在用 Rocky Linux 而不是 CentOS。
- 如果你去一家公司面试运维，面试官问"你用 CentOS 还是 Ubuntu"，你该怎么回答才能显示你"会用就行，不挑系统"？
