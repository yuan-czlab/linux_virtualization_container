# Mac 环境适配说明

> 课程原设计：Windows 10/11 + VMware Workstation 17 Pro
> 本文档：macOS 上的替代方案和差异说明

## 一、核心判断：可以复现

所有实验操作都在 **Linux 虚拟机内部** 完成，和宿主机操作系统无关。需要适配的只是虚拟机软件和少量宿主机侧操作。

## 二、虚拟机软件选择

### Apple Silicon（M1/M2/M3）推荐 UTM

| 项目 | UTM | VMware Fusion |
|------|-----|---------------|
| 价格 | 免费（App Store）或官网免费下载 | 免费（个人使用） |
| Apple Silicon 支持 | ✅ 原生 | ⚠️ 仅限 ARM Linux |
| x86_64 模拟 | ✅ QEMU模拟（慢） | ❌ 不支持 |
| 快照 | ✅ 支持 | ✅ 支持 |
| 网络模式 | NAT/桥接/仅主机 | NAT/桥接/仅主机 |
| 稳定性 | 好 | 好 |

**建议**：Apple Silicon Mac 用户用 UTM，安装 Rocky Linux 9 ARM64 版。

### Intel Mac 推荐 VMware Fusion

VMware Fusion 和 Workstation 功能几乎一样，快照、克隆、虚拟网络编辑器都有。

## 三、ISO 镜像选择

| Mac 类型 | Rocky Linux 9 | Ubuntu Server |
|----------|-------------|---------------|
| Intel Mac (x86_64) | Rocky-9.4-x86_64-minimal.iso | ubuntu-24.04.1-live-server-amd64.iso |
| Apple Silicon (ARM64) | Rocky-9.4-aarch64-minimal.iso | ubuntu-24.04.1-live-server-arm64.iso |

> ARM64 版本功能完全一致，dnf/packages 无差异。

## 四、实验手册需修改的地方

### 改动1：客户机操作系统选择

原手册写 "Red Hat Enterprise Linux 9 64 位"，Mac 上：
- **UTM**：选择 "Linux" → 导入 ISO → 自动识别
- **VMware Fusion**：选择 "Linux" → "Red Hat Enterprise Linux 9"

### 改动2：ISO 存放路径

原手册 `D:\ISO\`，Mac 上改为：
- `~/Downloads/` 或 `~/ISO/`

### 改动3：宿主机终端

原手册提到 Windows PowerShell `ssh` 命令，Mac 上：
- Mac 自带终端 + `ssh` 命令，**完全一样**
- 推荐用 VS Code 终端（和原设计一致）

### 改动4：虚拟机软件 UI 操作

| 操作 | Windows VMware Workstation | Mac UTM | Mac VMware Fusion |
|------|--------------------------|---------|-------------------|
| 创建VM | 典型→ISO选择 | + → Virtualize → Linux | + → New → Linux |
| 拍快照 | VM → 快照 → 拍摄快照 | 右键VM → Snapshot | 快照 → 拍摄 |
| 恢复快照 | 快照管理器 | 右键VM → Restore | 快照 → 恢复 |
| 克隆 | 管理 → 克隆 | 右键 → Clone | 右键 → 创建完整克隆 |
| 网络编辑器 | 编辑 → 虚拟网络编辑器 | UTM → 首选项 → 网络 | 偏好设置 → 网络 |

> 功能完全一致，只是菜单位置不同。建议第1节课带着学生在 Mac 上走一遍对应操作。

### 改动5：嵌套虚拟化

模块四 KVM 实验需要在 VM 里跑 VM（嵌套虚拟化）：
- **UTM (Apple Silicon)**：创建 VM 时勾选 "Enable hardware virtualization" 即可
- **VMware Fusion (Intel)**：VM 设置 → 处理器 → 勾选 "Enable hypervisor applications"
- 性能会比 Windows 原生差，但学习 KVM 命令够用

### 改动6：网络 IP 网段

原课程 NAT 网段设为 `192.168.200.0/24`：
- **UTM**：默认 NAT 网段可能是 `192.168.64.0/24`，在 UTM 首选项 → 网络中可修改
- **VMware Fusion**：默认 NAT 网段 `192.168.200.0/24`（可编辑）

如果不想改实验手册中的 IP，把 NAT 网段统一改为 `192.168.200.0/24` 即可。

## 五、无需改动的部分

以下内容在 Mac 上**完全一样**，零改动：

- ✅ 所有 Linux 命令（ssh/vim/systemctl/dnf/docker/git...）
- ✅ VS Code + Markdown 预览 → 和原设计一致
- ✅ XMind → Mac 有原生版
- ✅ 浏览器访问 http://VM_IP
- ✅ Docker/Docker Compose（在 VM 里跑）
- ✅ KVM（在 VM 里跑）

## 六、建议配置

| Mac 类型 | 虚拟化软件 | Linux 镜像 | 内存分配 |
|----------|-----------|-----------|---------|
| M1 8GB | UTM | Rocky 9 ARM64 | VM 2GB（勿超 4GB） |
| M2/M3 16GB+ | UTM | Rocky 9 ARM64 | VM 4GB |
| Intel 16GB+ | VMware Fusion | Rocky 9 x86_64 | VM 4GB |

## 七、给学生的话（可放进第一节课PPT）

```
本课程主线环境：Rocky Linux 9 虚拟机
配套软件：UTM（免费）或 VMware Fusion（免费）

Mac 用户：
  1. 下载 UTM（mac.getutm.app）
  2. 下载 Rocky-9-ARM64.iso（rockylinux.org/download）
  3. UTM → + → Virtualize → Linux → 选择ISO → 4GB内存 → 完成

Windows 用户：
  1. 下载 VMware Workstation 17 Pro
  2. 下载 Rocky-9-x86_64-minimal.iso
  3. 按照 Lab02 实验手册操作

所有实验在虚拟机内完成，Mac 和 Windows 没有区别
```
