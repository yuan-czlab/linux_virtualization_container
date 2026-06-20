# Lab04：基础命令练习

> 课时：2 | 类型：个人 | 前置：Lab02（Rocky Linux 可用）

⚠️ **从本实验开始，所有操作在 Rocky Linux 9 上进行，Ubuntu VM 仅用作偶尔对照。**

## 一、你会学到什么
- 能熟练使用 ls/cd/pwd/man/history 完成日常目录操作
- 会用 Tab 补全减少打字量，会用 Ctrl+R 搜索历史命令
- 能看懂命令提示符的每一部分
- 会用 man 和 --help 自己查命令用法

## 二、实验环境
- Rocky Linux 9 VM，以 student 用户登录

## 三、实验步骤

### 步骤1：读懂命令提示符

你的终端上有一行类似这样的东西：
```
[student@rocky-vm ~]$
```

请说出每一部分的含义：

| 部分 | 含义 |
|------|------|
| `student` | ？ |
| `@` | ？ |
| `rocky-vm` | ？ |
| `~` | ？ |
| `$` | ？（提示：换成 root 这个符号会变） |

```bash
# 验证：切换到 root 观察提示符变化
sudo -i
# 提示符变成 [root@rocky-vm ~]#
exit
# 变回 [student@rocky-vm ~]$
```

> **验收点**：能口头解释 `$` 和 `#` 的区别（普通用户 vs root）。

### 步骤2：ls — 你最常用的命令

```bash
# 基本用法
ls              # 列出当前目录文件
ls -l           # 长格式（权限/所有者/大小/时间/名称）
ls -a           # 包括隐藏文件（以 . 开头）
ls -la          # 组合选项
ls -lh          # 人类可读的文件大小（K/M/G）
ls -lt          # 按时间排序，最新的在最前
ls -ltr         # 按时间倒序，最新的在最后
ls -d */        # 只列出目录
ls -l /etc/     # 列出指定目录
ls -l /etc/s*   # 通配符：列出 /etc/ 下 s 开头的
```

练习：不看文档，回答以下问题：
```bash
# 1. 如何列出 /var/log/ 下最大的 5 个文件？
ls -lhS /var/log/ | head -6

# 2. 如何列出 /etc/ 下所有 .conf 结尾的文件？
ls -l /etc/*.conf

# 3. 如何显示 /root/ 目录的内容？（不切换用户）
sudo ls -la /root/
```

> **验收点**：能独立使用 `ls -lhS` 找出当前目录最大的文件。

### 步骤3：cd 与路径

```bash
# 基本跳转
cd /etc         # 绝对路径
cd ..           # 上一级
cd ../..        # 上两级
cd -            # 回到上一次的目录（神奇！）
cd              # 回到 home 目录
cd ~            # 同上
cd /            # 去根目录

# 查看当前在哪
pwd
```

练习——不复制命令，自己敲：
```
用 cd 从 /etc/ssh 跳到 /var/log，再跳回 /etc/ssh（用最短命令），
再从 /etc/ssh 回到 home 目录，最后用 pwd 确认自己在 /home/student。
```

> **验收点**：能熟练使用 `cd -` 在两个目录之间来回跳。

### 步骤4：man 和 --help — 学会自学

```bash
# 用 man 查看完整手册（按 q 退出）
man ls
man man          # man 自己的手册！

# man 内部快捷键：
#  /关键字  搜索
#  n        下一个匹配
#  N        上一个匹配
#  g        跳到开头
#  G        跳到末尾
#  q        退出

# 用 --help 看精简版
ls --help

# 用 info 看详细版（如果有）
info ls
```

练习：
```bash
# 1. 用 man 查看 cp 命令，找到 -p 选项的含义，用你自己的话写下来
# 2. 用 man 查看 find 命令，找到 -mtime 选项，理解 +7 和 -7 的区别
# 3. 用 man hier 查看文件系统层次结构（hierarchy）
```

> **验收点**：能在 man 里用 `/关键字` 搜索，而不是一页页翻。

### 步骤5：history — 避免重复敲命令

```bash
# 查看历史
history
history 20          # 最后 20 条

# 重复执行历史命令
!123                # 执行历史编号 123 的命令
!!                  # 执行上一条（等价于按 ↑ 再按 Enter）
!ls                 # 执行最近一条以 ls 开头的命令
sudo !!             # 以 sudo 重新执行上一条命令（忘记 sudo 时救命！）

# 交互式搜索（这个最重要！）
# 按 Ctrl+R，然后输入关键词，会显示最近一条匹配的历史命令
# 再按 Ctrl+R 继续往前搜索
# 按 Enter 执行，按 Esc 退出搜索
```

练习：
```bash
# 1. 先随便敲 10 条命令（ls /etc, cd /tmp, pwd 等混着来）
# 2. 用 Ctrl+R 搜索其中一条
# 3. 用 ! 编号重复执行其中一条
# 4. 故意敲一条需要 sudo 的命令（比如 ls /root），看到 Permission denied 后，用 sudo !! 重来
```

> **验收点**：能独立使用 Ctrl+R 找回并执行一条历史命令。

### 步骤6：其他常用命令

```bash
# 查看当前用户
whoami

# 查看当前日期时间
date
date "+%Y-%m-%d %H:%M:%S"

# 查看日历
cal
cal 2026

# 清屏
clear
# 或 Ctrl+L

# 查看命令类型
type ls
type cd
type vim

# 查看命令位置
which ls
whereis ls

# 查看系统运行时间
uptime

# 查看已登录用户
who
w
```

> **验收点**：能说出 `which` 和 `type` 的区别。

## 五、验收标准
- [ ] 能解释命令提示符 `[student@rocky-vm ~]$` 每个部分的含义
- [ ] 能独立使用 `ls -la /var/log` 并看懂输出
- [ ] 能在两个目录之间用 `cd -` 快速跳转
- [ ] 能在 man 手册里搜索关键字（不是从头翻到尾）
- [ ] 能用 Ctrl+R 找回历史命令
- [ ] 会 `sudo !!` 重新执行上一条命令

## 六、常见问题

**Q: 命令打错了怎么改？**
A: 用方向键 ← → 移动光标，直接改。或者 Ctrl+A 跳到行首，Ctrl+E 跳到行尾，Ctrl+U 删除光标前所有内容。

**Q: Tab 补全不生效？**
A: 检查是否装了 bash-completion：`rpm -q bash-completion`。如果没有，`sudo dnf install -y bash-completion`，然后重新登录。

**Q: man 手册全是英文看不懂？**
A: 看关键的几部分：SYNOPSIS（语法）、DESCRIPTION（描述）、OPTIONS（选项）、EXAMPLES（示例）。不用从头读到尾，查字典一样用就行。运维必须习惯阅读英文技术文档。
