# Lab01：VMware 安装 Ubuntu Server 24.04 LTS

> 课时：2 | 类型：个人 | 前置：无

## 一、你会学到什么
- 能在 VMware Workstation 中创建一台新的虚拟机
- 能独立完成 Ubuntu Server 24.04 LTS 的完整安装流程
- 能在纯命令行环境（无桌面）中完成系统初始化
- 能用 apt 完成第一次系统更新
- 能对比 Ubuntu Server 和后续 Rocky Linux 的安装差异

## 二、实验环境
- 宿主机：Windows 10/11，VMware Workstation 17 Pro（已安装）
- 安装镜像：ubuntu-24.04.1-live-server-amd64.iso（教师提供，放在 D:\ISO\）
- 宿主机剩余磁盘空间 ≥ 30GB

## 三、为什么装 Ubuntu Server 而不是 Desktop

本课程主线系统是 Rocky Linux 9（最小化安装、无桌面），Ubuntu Server 作为对照系统。
- Server 版 = 命令行界面，与生产环境一致
- 与本课程后续的 Rocky Linux 9 操作方式统一
- 运维工程师日常工作就是命令行，早点适应

## 三、实验步骤

### 步骤1：创建虚拟机
在 VMware 中新建一台虚拟机，参数如下：

| 配置项 | 值 |
|--------|-----|
| 典型/自定义 | 典型（推荐） |
| 安装来源 | 稍后安装操作系统 |
| 客户机操作系统 | Linux → Ubuntu 64 位 |
| 虚拟机名称 | `Ubuntu-22.04-学号`（如 Ubuntu-22.04-20240101） |
| 磁盘容量 | 40GB（选择"将虚拟磁盘存储为单个文件"） |
| 内存 | 4GB（4096 MB） |
| 处理器 | 2 核 |

> **验收点**：VMware 左侧列表出现你的虚拟机，状态为"已关闭"。

### 步骤2：挂载 ISO 并启动
1. 右键虚拟机 → 设置 → CD/DVD → 使用 ISO 映像文件 → 浏览选择 `D:\ISO\ubuntu-22.04.5-desktop-amd64.iso`
2. 启动虚拟机
3. 看到 Ubuntu 启动菜单后，选择 "Try or Install Ubuntu" 回车

> **验收点**：进入 Ubuntu 图形化安装界面，看到语言选择页面。

### 步骤3：安装 Ubuntu
按以下选项依次操作：

| 步骤 | 选择 |
|------|------|
| 语言 | English（后续可通过设置添加中文） |
| 键盘布局 | Chinese → Chinese (Hanyu Pinyin) |
| 安装类型 | Normal installation（勾选 Download updates，不勾选 Install third-party software） |
| 磁盘分区 | Erase disk and install Ubuntu（这是虚拟磁盘，放心擦除） |
| 时区 | Shanghai |
| 用户信息 | Your name: `student` / Computer name: `ubuntu-vm` / Username: `student` / Password: `student123` |

点击 Install Now → Continue 确认写入磁盘 → 等待安装完成 → Restart Now

⚠️ **陷阱**：重启时可能卡在黑屏提示"Please remove the installation medium"。按 Enter 或手动断开 VMware 的 CD/DVD 连接即可。

> **验收点**：系统重启后进入 Ubuntu 登录界面，输入密码 `student123` 能成功登录桌面。

### 步骤4：安装后配置
打开终端（右键桌面 → Open in Terminal），依次执行：

```bash
# 1. 更新软件包列表
sudo apt update

# 2. 升级已安装的软件包
sudo apt upgrade -y

# 3. 安装 VMware Tools（增强分辨率自适应、剪贴板共享）
# VMware 菜单 → VM → Install VMware Tools → 弹出光盘后：
sudo apt install open-vm-tools-desktop -y

# 4. 重启使 VMware Tools 生效
sudo reboot
```

> **验收点**：重启后，VMware 窗口大小变化时 Ubuntu 桌面分辨率自动跟随；宿主机和虚拟机之间可以双向复制粘贴文本。

### 步骤5：安装中文输入法（可选）
```bash
# 安装 IBus 拼音
sudo apt install ibus-libpinyin -y

# Settings → Region & Language → Input Sources → + → Chinese → Chinese (Intelligent Pinyin)
# 重启或注销后生效
```

> **验收点**：Super（Win键）+ 空格能切换到中文输入法，可以在终端或文本编辑器输入中文。

## 五、验收标准
- [ ] Ubuntu 22.04 正常启动到桌面
- [ ] 能打开终端（Ctrl+Alt+T）
- [ ] `sudo apt update` 能成功连接到软件源
- [ ] 宿主机 ↔ 虚拟机可以双向复制粘贴
- [ ] 执行 `uname -a` 能看到 Linux 内核版本信息
- [ ] 执行 `lsb_release -a` 能看到 Ubuntu 22.04

## 六、常见问题

**Q: 虚拟机启动后黑屏？**
A: 关闭虚拟机 → 设置 → 显示器 → 取消勾选"加速3D图形" → 再启动。

**Q: 安装时提示"This computer currently has no detected operating systems"？**
A: 正常现象，这是虚拟磁盘，本来就没有系统。直接选"Erase disk and install Ubuntu"。

**Q: apt update 报错 "Temporary failure resolving"？**
A: 虚拟机网络没通。检查 VMware 网络模式是否为 NAT（默认）。`ping 8.8.8.8` 如果不通则检查宿主机网络。

**Q: 虚拟机运行很卡？**
A: 检查内存是否给够 4GB；检查宿主机是否开启了"虚拟化支持"（任务管理器 → 性能 → CPU → 虚拟化：已启用）。

## 七、清理环境
本实验不清理，这台 Ubuntu VM 后续实验继续使用。
