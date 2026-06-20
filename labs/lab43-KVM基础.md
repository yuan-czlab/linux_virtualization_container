# Lab43：KVM 虚拟化基础

> 课时：2 | 类型：个人 | 前置：Lab14

## 一、你会学到什么
- 理解 KVM 架构（内核模块 + QEMU + libvirt）
- 能在 VMware 中开启嵌套虚拟化
- 能安装 KVM 工具链
- 能使用 virt-manager 和 virsh 管理虚拟机

## 二、KVM 架构理解

```
┌─────────────────────────────────┐
│  virsh / virt-manager (管理工具) │
├─────────────────────────────────┤
│  libvirtd (管理守护进程)         │
├─────────────────────────────────┤
│  QEMU (设备模拟：网卡/磁盘/显卡)  │
├─────────────────────────────────┤
│  kvm.ko (内核模块：CPU/内存虚拟化)│
├─────────────────────────────────┤
│  Linux Kernel                   │
├─────────────────────────────────┤
│  物理硬件 (CPU需支持VT-x/AMD-V)  │
└─────────────────────────────────┘
```

**KVM 是 Type 1 Hypervisor**（直接运行在硬件上），因为 kvm.ko 是内核模块。

## 三、实验步骤

### 步骤1：开启嵌套虚拟化

```text
VMware 操作（KVM 是在 VM 里跑 VM，需要嵌套虚拟化）：
1. 关闭 VM
2. 编辑虚拟机设置 → 处理器 → 勾选：
   ☑ 虚拟化 Intel VT-x/EPT 或 AMD-V/RVI
3. 启动 VM
```

```bash
# 验证 CPU 虚拟化支持
grep -E 'vmx|svm' /proc/cpuinfo | wc -l
# 输出 > 0 → 支持虚拟化 ✓
# vmx = Intel VT-x
# svm = AMD-V

# 检查 kvm 内核模块
lsmod | grep kvm
# kvm_intel  或  kvm_amd
# kvm
```

### 步骤2：安装 KVM 工具链

```bash
# 安装核心组件
sudo dnf install -y qemu-kvm libvirt virt-manager virt-install virt-viewer

# qemu-kvm       KVM 的 QEMU 后端
# libvirt        虚拟化管理库
# virt-manager   图形界面管理工具
# virt-install   命令行创建 VM
# virt-viewer    虚拟机控制台查看器
```

### 步骤3：启动 libvirtd

```bash
sudo systemctl enable --now libvirtd
systemctl status libvirtd           # active (running)

# 验证 virsh 可用
virsh --version
virsh list --all
# Id   Name   State
# （目前没有 VM）

# 查看 libvirt 网络
virsh net-list --all
# Name      State    Autostart
# default   active   yes
```

### 步骤4：使用 virt-manager 图形界面

```bash
# 启动 virt-manager（需要图形界面）
# 方式1：VM 有桌面环境
virt-manager &

# 方式2：通过 SSH X11 转发（从宿主机）
# ssh -X student@VM_IP
# virt-manager &
```

**virt-manager 操作流程**：
1. 连接到 QEMU/KVM（通常自动连接）
2. 点击"创建新虚拟机"
3. 选择 ISO 镜像
4. 配置内存和 CPU
5. 配置磁盘（qcow2 格式，10GB）
6. 配置网络（默认 NAT）
7. 开始安装

### 步骤5：virsh 命令行管理

```bash
# 查看所有 VM（包括关机的）
virsh list --all

# 查看 VM 基本信息
virsh dominfo VM名               # VM 详细信息
virsh domblklist VM名            # 磁盘列表
virsh domiflist VM名             # 网卡列表
virsh dommemstat VM名            # 内存统计
virsh vcpuinfo VM名              # CPU 信息

# 管理 VM
virsh start VM名                 # 启动
virsh shutdown VM名              # 优雅关机
virsh destroy VM名               # 强制断电（相当于拔电源）
virsh reboot VM名                # 重启

# 设置开机自启
virsh autostart VM名             # 启用自启
virsh autostart --disable VM名   # 禁用自启

# 删除 VM
virsh undefine VM名              # 删除定义（磁盘保留）
# 如果要同时删除磁盘：
# virsh undefine VM名 --remove-all-storage
```

### 步骤6：virt-install 命令行创建 VM

```bash
# 创建 VM 的命令行方式（了解，不要求实际执行）
# sudo virt-install \
#   --name test-vm \
#   --ram 1024 \
#   --vcpus 1 \
#   --disk path=/var/lib/libvirt/images/test-vm.qcow2,size=10,format=qcow2 \
#   --os-variant rocky9 \
#   --network network=default \
#   --graphics none \
#   --console pty,target_type=serial \
#   --location /path/to/Rocky-9.iso \
#   --extra-args 'console=ttyS0,115200n8 serial'
```

---

## 五、练习题

### 练习1：KVM 架构填空（15分）

| 组件 | 作用 | 属于哪一层 |
|------|------|-----------|
| kvm.ko | | |
| QEMU | | |
| libvirtd | | |
| virsh | | |
| virt-manager | | |

### 练习2：KVM vs VMware（20分）

| 对比 | KVM | VMware Workstation |
|------|-----|--------------------|
| 类型 | | |
| 开源 | | |
| 管理工具 | | |
| 企业数据中心主流 | | |
| 嵌套虚拟化性能 | | |

### 练习3：qcow2 vs raw（20分）

| 对比 | qcow2 | raw |
|------|-------|-----|
| 稀疏分配 | | |
| 快照支持 | | |
| 性能 | | |
| 文件大小（空盘） | | |

用 `qemu-img create` 创建 10GB 的 qcow2 和 raw 磁盘，用 `ls -lh` 对比文件大小。

### 练习4：libvirt 网络探索（25分）

1. 查看 default 网络的 XML 配置：`virsh net-dumpxml default`
2. 找到网络的 IP 范围、DHCP 范围、网桥名称
3. 在宿主机上执行 `ip a show virbr0`，查看网桥 IP
4. 为什么 libvirt 的默认网络也用的 NAT 模式？

### 练习5：KVM 在企业中的应用（20分）

1. 哪些云厂商使用了 KVM？
2. 为什么企业数据中心选 KVM 而不是 VMware Workstation？
3. OpenStack 和 KVM 是什么关系？


## 七、常见问题

**Q: 在 VMware 里跑 KVM 性能很差？**
A: 正常，嵌套虚拟化有两层性能损耗（VMware 虚拟化 + KVM 虚拟化）。学校实验室环境用于学习 KVM 命令够用，生产环境 KVM 应该直接跑在物理机上。

**Q: virt-manager 连不上 libvirtd？**
A: 检查 libvirtd 是否启动：`systemctl status libvirtd`。如果没启动：`sudo systemctl start libvirtd`。

**Q: qcow2 和 raw 选哪个？**
A: 测试/开发/一般生产 → qcow2（稀疏分配省空间、支持快照）。极致性能场景 → raw（无写时复制开销）。云环境普遍用 qcow2。

**Q: 删 VM 时用 undefine 还是 undefine --remove-all-storage？**
A: undefine 只删定义（XML），磁盘文件保留（可以重新 define 恢复）。--remove-all-storage 连磁盘一起删（不可恢复）。不确定就先 undefine 保留磁盘。

## 八、课后思考

1. KVM 是 Linux 内核自带的虚拟化方案，Docker 用的是 Linux namespace + cgroup。两者都利用了 Linux 内核的特性。虚拟化和容器化在隔离性、性能、启动速度上各有什么优劣？什么场景用虚拟化，什么场景用容器化？

2. 云计算厂商（阿里云、AWS）底层大多用 KVM 实现虚拟机隔离。如果你购买了一台云服务器，它实际上是一台在物理机上运行的 KVM 虚拟机。你的 Docker 容器跑在这台云服务器上，这样就形成了"容器跑在虚拟机里"的嵌套结构。这种架构有什么优缺点？
