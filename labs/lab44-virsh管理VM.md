# Lab44：virsh 管理 KVM 虚拟机

> 课时：2 | 类型：教师演示/学生选做 | 前置：Lab43 | 条件：KVM可用

## 一、你会学到什么
- 能用 virsh 管理虚拟机的完整生命周期
- 能管理 KVM 存储池和磁盘镜像
- 能理解 qcow2 格式的优势

## 二、实验步骤

### 步骤1：virsh 核心命令

```bash
# 列出所有 VM
virsh list --all

# 启动 VM
virsh start VM名
# VM 变成 running

# 优雅关机（发送 ACPI 关机信号）
virsh shutdown VM名

# 强制断电（相当于拔电源，可能丢数据）
virsh destroy VM名

# 重启
virsh reboot VM名

# 查看 VM 信息
virsh dominfo VM名
# Id / Name / UUID / OS Type / State / CPU(s) / Memory
```

### 步骤2：查看 VM 资源

```bash
# 查看磁盘
virsh domblklist VM名
# Target   Source
# vda      /var/lib/libvirt/images/VM名.qcow2

# 查看网卡
virsh domiflist VM名
# Interface  Type    Source   Model   MAC
# vnet0      bridge  virbr0   virtio  52:54:00:xx:xx:xx

# 查看内存使用
virsh dommemstat VM名

# 查看 CPU 信息
virsh vcpuinfo VM名
```

### 步骤3：编辑 VM 配置

```bash
# 编辑 VM 的 XML 配置（类似 VMware 的"编辑设置"）
virsh edit VM名
# 可以修改：内存、CPU、磁盘、网卡、启动顺序...

# 常见修改示例：
# 修改内存：
#   <memory unit='KiB'>2097152</memory>  ← 改为 2GB
#   <currentMemory unit='KiB'>2097152</currentMemory>

# 修改 CPU：
#   <vcpu placement='static'>2</vcpu>  ← 改为 2 核

# 保存退出后配置立即生效（需要重启 VM）
```

### 步骤4：存储池管理

```bash
# 查看存储池
virsh pool-list
# Name      State    Autostart
# default   active   yes
# images    active   yes

# 查看存储池详情
virsh pool-info default
virsh pool-info images

# 查看存储池中的卷（磁盘镜像）
virsh vol-list --pool images
# Name           Path
# VM名.qcow2     /var/lib/libvirt/images/VM名.qcow2
```

### 步骤5：qcow2 磁盘镜像管理

```bash
# 创建 qcow2 磁盘（10GB，稀疏分配）
qemu-img create -f qcow2 /var/lib/libvirt/images/test-disk.qcow2 10G

# 查看磁盘信息
qemu-img info /var/lib/libvirt/images/test-disk.qcow2
# image: test-disk.qcow2
# file format: qcow2
# virtual size: 10 GiB (10737418240 bytes)
# disk size: 196 KiB          ← 稀疏分配：实际只占 196KB！
# cluster_size: 65536

# 查看实际文件大小
ls -lh /var/lib/libvirt/images/test-disk.qcow2
# -rw-r--r--. 1 root root 193K ... test-disk.qcow2  ← 只有 193KB！

# 扩容磁盘（只能扩大不能缩小）
qemu-img resize /var/lib/libvirt/images/test-disk.qcow2 +5G
qemu-img info /var/lib/libvirt/images/test-disk.qcow2 | grep "virtual size"
# virtual size: 15 GiB

# 转换格式
# qemu-img convert -f raw -O qcow2 old.raw new.qcow2
# qemu-img convert -f qcow2 -O raw old.qcow2 new.raw

# 清理
sudo rm /var/lib/libvirt/images/test-disk.qcow2
```

### 步骤6：VM 的 XML 配置结构

```bash
# 导出一台 VM 的完整配置
virsh dumpxml VM名 | head -50

# XML 结构：
# <domain type='kvm'>
#   <name>VM名</name>
#   <memory>...</memory>        # 内存配置
#   <vcpu>...</vcpu>            # CPU 配置
#   <os>...</os>                # 启动设置
#   <devices>
#     <disk>...</disk>          # 磁盘
#     <interface>...</interface> # 网卡
#     <graphics>...</graphics>  # 图形控制台
#   </devices>
# </domain>
```

---

## 五、练习题

### 练习1：virsh 命令填空（15分）

| 操作 | 命令 |
|------|------|
| 列出所有 VM | |
| 启动 VM | |
| 优雅关机 | |
| 强制断电 | |
| 查看磁盘列表 | |
| 查看网卡列表 | |
| 编辑配置 | |
| 设置开机自启 | |
| 删除 VM 定义 | |

### 练习2：qcow2 实验（25分）

1. 创建 5GB 的 qcow2 磁盘
2. 用 `ls -lh` 和 `qemu-img info` 查看
3. 解释为什么 `virtual size` 和 `disk size` 差这么多
4. 用 `qemu-img resize` 扩容到 8GB
5. 对比 raw 格式创建同样是 5GB 的文件大小

### 练习3：VM 资源配置（20分）

用 `virsh edit` 修改 VM 的以下配置，写出修改的 XML 片段：
1. 内存从 1GB 改为 2GB
2. CPU 从 1 核改为 2 核
3. 添加第二块磁盘

### 练习4：存储池操作（20分）

1. 创建一个目录存储池 `/var/lib/libvirt/images/backups`
2. 在该存储池中创建一个 5GB 的 qcow2 卷
3. 查看存储池和卷的信息
4. 删除卷和存储池

### 练习5：virsh 脚本管理（20分）

写一个 Shell 脚本 `~/vm-control.sh`：
1. 接受两个参数：操作（start/stop/status/list）和 VM 名（可选）
2. start：启动 VM 并等待 10 秒后显示状态
3. stop：优雅关机，如果 30 秒还没关则强制断电
4. status：显示 VM 的 dominfo
5. list：显示所有 VM 及其状态

## 七、常见问题

**Q: virsh destroy 和 shutdown 有什么区别？**
A: shutdown 是优雅关机（发送 ACPI 信号，类似按电源键），VM 可以安全关闭服务、保存数据。destroy 是强制断电（类似拔电源），可能导致数据丢失。日常用 shutdown，卡死时用 destroy。

**Q: qemu-img resize 扩容后 VM 内还是旧大小？**
A: resize 只改了虚拟磁盘的大小，VM 内的分区和文件系统不会自动扩容。还需要在 VM 内扩容分区（fdisk/gdisk 删分区重建）和文件系统（xfs_growfs/resize2fs）。

**Q: undefine 之后怎么恢复 VM？**
A: 磁盘文件还在的话，用 `virsh define /path/to/backup.xml` 重新导入配置。或直接用 `virt-install --import` 导入已有磁盘镜像创建新 VM。

## 八、课后思考

1. libvirt 的 XML 配置方式和 VMware 的图形界面配置方式各有什么优缺点？如果你是云平台开发者，要向用户暴露 VM 管理 API，你会选择什么方式？

2. qcow2 的稀疏分配让"显示 100GB，实际占 2GB"成为可能。但这带来了什么风险？（提示：如果多个 VM 的虚拟磁盘总大小超过了物理磁盘容量……）
