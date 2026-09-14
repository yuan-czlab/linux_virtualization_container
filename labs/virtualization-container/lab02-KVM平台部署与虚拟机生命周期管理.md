# 实验2：KVM平台部署与虚拟机生命周期管理

> 所属模块：模块一 服务器虚拟化与云资源基础
>
> 建议学时：6学时
>
> 实验方式：个人
>
> 对应教材：《模块一 服务器虚拟化与云资源基础》第2章
>
> 知识前置：实验1中的虚拟化层次、KVM、QEMU和libvirt关系
>
> 状态依赖：实验1中本机或本组已验证`vmx/svm`的`rocky-server`，或教师指定远程KVM主机；另需教师发布的轻量qcow2
>
> 建议起点：`VC-V0`
>
> 项目成果：可用的KVM/QEMU/libvirt平台、一台可启动客户机及完整生命周期操作记录

## 一、项目情境

TechCorp需要在一台Linux服务器中运行多台隔离的测试主机。你将把Rocky主机配置为KVM宿主机，使用libvirt管理虚拟化资源，并从教师提供的轻量qcow2镜像导入一台客户机。实验重点不是再次安装操作系统，而是理解并操作虚拟机从定义、启动、连接到安全停止和清理的完整生命周期。

## 二、实验目标

### 1. 知识目标

1. 说明KVM、QEMU、libvirt、`virsh`和`virt-install`的关系。
2. 区分宿主机软件包、内核模块、管理服务、虚拟机定义和磁盘镜像。
3. 区分正常关机、强制停止、取消定义和删除磁盘。
4. 理解RHEL 9系模块化libvirt守护进程和Socket激活方式。

### 2. 能力目标

1. 安装并验证KVM虚拟化平台。
2. 管理默认存储池和默认NAT网络。
3. 从教师基础镜像安全复制并导入虚拟机。
4. 使用`virsh`完成虚拟机生命周期管理、状态检查和控制台或SSH连接。

### 3. 素质目标

1. 不直接修改教师基础镜像。
2. 删除资源前区分“取消定义”和“删除数据”。
3. 通过多项证据验收平台，不只查看一条服务状态。

## 三、知识准备

### 1. KVM管理路径

```text
学生输入virsh或virt-install命令
→ libvirt检查权限、网络、存储和虚拟机XML
→ QEMU创建虚拟机进程和设备模型
→ KVM使用CPU硬件虚拟化执行客户机指令
```

在Rocky Linux 9中应优先通过libvirt工具管理QEMU，不直接拼接复杂的`qemu-system-*`命令。

### 2. 关键对象

| 对象 | 示例 | 说明 |
|---|---|---|
| 虚拟机定义 | `course-vm01` | libvirt保存的CPU、内存、磁盘和网卡配置 |
| 磁盘镜像 | `course-vm01.qcow2` | 客户机系统与数据所在文件 |
| 存储池 | `default` | libvirt统一管理的一组存储位置 |
| 虚拟网络 | `default` | libvirt提供的NAT网络 |
| 管理连接 | `qemu:///system` | 系统级QEMU/KVM管理范围 |

### 3. 生命周期命令差异

| 操作 | 典型命令 | 数据影响 |
|---|---|---|
| 正常开机 | `virsh start` | 无 |
| 请求客户机关机 | `virsh shutdown` | 无，需要客户机响应 |
| 强制断电 | `virsh destroy` | 不删除磁盘，但可能损坏客户机数据 |
| 取消定义 | `virsh undefine` | 删除libvirt定义，磁盘默认仍存在 |
| 删除卷 | `virsh vol-delete`或明确删除文件 | 会删除磁盘数据 |

## 四、实验环境

- Rocky主机已经完成实验1，能够看到`vmx`或`svm`。
- Rocky建议4 vCPU、6—8GB内存和30GB以上空闲空间。
- Ubuntu主机本实验可以关闭，释放宿主机资源。
- 教师提供适用于x86_64、启用串口控制台、具有`student`实验账号的轻量qcow2基础镜像。
- 基础镜像位置由教师发布，例如`<COURSE_MEDIA>/kvm/course-base.qcow2`。

## 五、项目任务

1. 安装虚拟化软件包。
2. 验证CPU、内核模块、设备、libvirt和主机能力。
3. 检查默认存储池和网络。
4. 复制教师镜像并创建虚拟机。
5. 完成启动、连接、重启、关机和异常停止。
6. 导出虚拟机配置和生命周期证据。

## 六、实验步骤

### 任务一：安装与验证KVM平台

#### 步骤1：建立安装前证据

在Rocky执行：

```bash
mkdir -p ~/vc-course/evidence ~/vc-course/backup ~/vc-course/manifests
{
  date -Is
  grep -Ewo 'vmx|svm' /proc/cpuinfo | sort -u
  ls -l /dev/kvm 2>&1 || true
  rpm -q qemu-kvm libvirt virt-install 2>&1 || true
} | tee ~/vc-course/evidence/lab02-before.txt
```

如果CPU标志为空，停止安装并使用教师远程KVM环境。软件安装不能弥补未暴露的硬件虚拟化能力。

#### 步骤2：安装软件包

使用教师验证的软件源或离线RPM：

```bash
sudo dnf install -y \
  qemu-kvm \
  libvirt \
  virt-install \
  libvirt-daemon-config-network \
  libguestfs-tools-c
```

记录版本：

```bash
rpm -q qemu-kvm libvirt virt-install
virsh --version
virt-install --version
```

若机房使用离线包，将命令中的包名保持不变，仅由教师指定本地RPM目录。不要混用多个来源的libvirt核心包。

#### 步骤3：启动libvirt管理Socket

Rocky 9可能使用模块化守护进程。先执行：

```bash
sudo systemctl enable --now virtqemud.socket
sudo systemctl enable --now virtnetworkd.socket
sudo systemctl enable --now virtstoraged.socket
```

检查：

```bash
systemctl is-active virtqemud.socket
systemctl is-active virtnetworkd.socket
systemctl is-active virtstoraged.socket
sudo virsh -c qemu:///system uri
```

若统一镜像仍使用传统`libvirtd`单体服务，按教师基线执行：

```bash
sudo systemctl enable --now libvirtd
```

两种方式不要在不同学生机上随意混搭。以`virsh -c qemu:///system uri`能返回`qemu:///system`为最终连接证据。

#### 步骤4：验证内核与设备

```bash
sudo modprobe kvm
if grep -q vmx /proc/cpuinfo; then
  sudo modprobe kvm_intel
elif grep -q svm /proc/cpuinfo; then
  sudo modprobe kvm_amd
fi

lsmod | grep '^kvm'
ls -l /dev/kvm
sudo virt-host-validate qemu
```

重点查看：

- `/dev/kvm`存在；
- 对应的`kvm_intel`或`kvm_amd`已加载；
- `virt-host-validate`关于硬件虚拟化、`/dev/kvm`和网络设备的关键检查为PASS。

IOMMU未启用可能显示WARN，本课程不做设备直通时通常不构成阻塞。出现FAIL时必须记录完整项目并报告教师，不能把所有WARN和FAIL都忽略。

> **验收点**：`/dev/kvm`存在，系统级libvirt连接正常，关键主机验证项通过。

### 任务二：准备默认网络和存储

#### 步骤5：检查默认网络

```bash
sudo virsh net-list --all
```

如果`default`存在但未启动：

```bash
sudo virsh net-start default
sudo virsh net-autostart default
```

再次验证：

```bash
sudo virsh net-info default
ip -brief address | grep virbr || true
```

如果完全没有`default`网络，不要自行从网络复制未知XML。使用教师发布的`default-network.xml`：

```bash
source ~/vc-course/course-env.sh
sudo virsh net-define "$COURSE_MEDIA/kvm/default-network.xml"
sudo virsh net-start default
sudo virsh net-autostart default
```

#### 步骤6：检查默认存储池

```bash
sudo virsh pool-list --all
sudo mkdir -p /var/lib/libvirt/images
```

若`default`池不存在：

```bash
sudo virsh pool-define-as default dir --target /var/lib/libvirt/images
```

启动并设置自启动：

```bash
sudo virsh pool-start default 2>/dev/null || true
sudo virsh pool-autostart default
sudo virsh pool-info default
sudo virsh pool-refresh default
```

`pool-start`在池已经活动时可能提示已启动，因此使用后续`pool-info`判断最终状态。

### 任务三：准备客户机镜像

#### 步骤7：检查教师镜像而不直接启动

从实验1的统一参数文件读取教师发布的实际挂载目录：

```bash
source ~/vc-course/course-env.sh
[[ "$COURSE_MEDIA" != 'CHANGE_ME' && -d "$COURSE_MEDIA" ]]
ls -lh "$COURSE_MEDIA/kvm/course-base.qcow2"
sha256sum "$COURSE_MEDIA/kvm/course-base.qcow2"
qemu-img info "$COURSE_MEDIA/kvm/course-base.qcow2"
```

把校验值与教师清单比较。格式应为`qcow2`，校验不一致时重新复制。

#### 步骤8：复制为个人工作镜像

先检查目标不存在：

```bash
sudo test ! -e /var/lib/libvirt/images/course-vm01.qcow2
```

如果命令没有输出且退出状态为0，执行：

```bash
source ~/vc-course/course-env.sh
sudo cp --reflink=auto --sparse=always \
  "$COURSE_MEDIA/kvm/course-base.qcow2" \
  /var/lib/libvirt/images/course-vm01.qcow2
sudo chown qemu:qemu /var/lib/libvirt/images/course-vm01.qcow2
sudo restorecon -v /var/lib/libvirt/images/course-vm01.qcow2
sudo virsh pool-refresh default
sudo virsh vol-list default
```

如果目标已存在，先使用`qemu-img info`和`virsh domblklist`确认是否属于已有实验，不能直接覆盖。

> **验收点**：教师基础镜像未改变，个人工作镜像位于默认存储池且校验、格式正常。

### 任务四：导入KVM客户机

#### 步骤9：确认名称尚未被占用

```bash
sudo virsh list --all
sudo virsh dominfo course-vm01 2>/dev/null || true
```

如果已有同名虚拟机，判断是否为自己前一次实验结果。不要创建重复定义。

#### 步骤10：使用virt-install导入

```bash
sudo virt-install \
  --connect qemu:///system \
  --name course-vm01 \
  --memory 1536 \
  --vcpus 1 \
  --disk path=/var/lib/libvirt/images/course-vm01.qcow2,format=qcow2,bus=virtio \
  --network network=default,model=virtio \
  --import \
  --os-variant generic \
  --graphics none \
  --console pty,target_type=serial \
  --noautoconsole
```

参数含义：

- `--import`表示使用已有系统镜像，不启动安装程序；
- `--disk`明确指定个人工作镜像和virtio磁盘；
- `--network network=default`连接libvirt NAT网络；
- `--graphics none`配合已启用串口的教师镜像；
- `--noautoconsole`创建后不立即占用当前终端。

检查定义和状态：

```bash
sudo virsh list --all
sudo virsh dominfo course-vm01
sudo virsh domblklist course-vm01
sudo virsh domiflist course-vm01
```

### 任务五：连接并验收客户机

#### 步骤11：获取DHCP租约

```bash
sudo virsh net-dhcp-leases default
sudo virsh domifaddr course-vm01 --source lease
```

启动后的前几十秒可能尚未获得地址，可以稍后重试。记录MAC地址与IPv4地址的对应关系。

租约出现后自动提取IPv4地址，并写回后续实验共用的参数文件：

```bash
KVM_GUEST_IP=$(sudo virsh domifaddr course-vm01 --source lease | \
  awk '/ipv4/ {split($4,a,"/"); print a[1]; exit}')
if [[ -z "$KVM_GUEST_IP" ]]; then
  echo '尚未取得客户机IPv4地址，请等待启动完成后重试'
else
  sed -i '/^export KVM_GUEST_IP=/d' ~/vc-course/course-env.sh
  printf 'export KVM_GUEST_IP=%q\n' "$KVM_GUEST_IP" >> ~/vc-course/course-env.sh
  printf 'kvm_guest_ip=%s\n' "$KVM_GUEST_IP"
fi
```

#### 步骤12：使用控制台连接

```bash
sudo virsh console course-vm01
```

出现空白时按一次Enter。使用教师发布的`student`实验账号登录。退出控制台使用：

```text
Ctrl + ]
```

不能使用关闭终端窗口代替正确退出。

如果教师镜像只提供SSH，执行：

```bash
source ~/vc-course/course-env.sh
ssh student@"$KVM_GUEST_IP"
```

登录客户机后检查：

```bash
hostnamectl
ip -brief address
ip route
df -hT /
```

#### 步骤13：从宿主机验证虚拟机进程

退出客户机回到Rocky宿主机：

```bash
sudo virsh list
ps -eo pid,cmd | grep '[q]emu-system' | sed -n '1,3p'
sudo virsh vcpucount course-vm01
sudo virsh dommemstat course-vm01
```

这证明虚拟机在宿主机上表现为由libvirt管理的QEMU进程，同时通过KVM获得硬件加速。

### 任务六：完成生命周期操作

#### 步骤14：正常关机与启动

```bash
sudo virsh shutdown course-vm01
```

循环观察，等待状态变为shut off：

```bash
sudo virsh list --all
```

若客户机安装并运行ACPI支持，通常会正常关机。确认后重新启动：

```bash
sudo virsh start course-vm01
sudo virsh list
```

#### 步骤15：重启与强制断电对比

先尝试正常重启：

```bash
sudo virsh reboot course-vm01
```

确认重新上线。随后仅在没有重要写入任务时体验强制断电：

```bash
sudo virsh destroy course-vm01
sudo virsh list --all
```

`destroy`类似拔掉电源，不等于删除虚拟机。立即重新启动并检查客户机文件系统和日志：

```bash
sudo virsh start course-vm01
```

进入客户机后：

```bash
sudo journalctl -b -p warning --no-pager | tail -n 20
```

#### 步骤16：设置宿主机启动时自动启动

```bash
sudo virsh autostart course-vm01
sudo virsh dominfo course-vm01 | grep -i autostart
```

课堂环境若不希望占用资源，验收后取消：

```bash
sudo virsh autostart --disable course-vm01
```

### 任务七：保存配置与证据

#### 步骤17：导出虚拟机XML

```bash
sudo virsh dumpxml course-vm01 | tee ~/vc-course/manifests/course-vm01.xml > /dev/null
```

从XML中查找名称、内存、vCPU、磁盘和网络：

```bash
grep -E '<name>|<memory|<vcpu|source file=|source network=' \
  ~/vc-course/manifests/course-vm01.xml
```

#### 步骤18：生成验收记录

```bash
{
  date -Is
  sudo virsh version
  sudo virsh list --all
  sudo virsh dominfo course-vm01
  sudo virsh domblklist course-vm01
  sudo virsh domiflist course-vm01
  sudo virsh net-dhcp-leases default
  sudo virsh pool-info default
} > ~/vc-course/evidence/lab02-kvm-result.txt
```

## 七、独立实践

不查看实验步骤，根据以下任务单完成一次状态转换并记录每一步：

```text
运行 → 正常关机 → 关闭 → 启动 → 运行 → 强制断电 → 关闭 → 再次启动
```

用一句话分别解释`shutdown`和`destroy`的风险差异。

## 八、验收标准

- [ ] CPU虚拟化标志存在，`/dev/kvm`可用。
- [ ] 系统级libvirt连接返回`qemu:///system`。
- [ ] `virt-host-validate`关键项目通过，警告已解释。
- [ ] `default`网络和存储池处于active状态。
- [ ] 教师基础镜像校验值正确且未被修改。
- [ ] `course-vm01`可以启动并通过控制台或SSH登录。
- [ ] 能展示虚拟机CPU、内存、磁盘、网卡和IP信息。
- [ ] 完成正常关机、启动、重启和一次受控强制断电。
- [ ] 已导出XML和完整验收记录。

## 九、成果提交

```text
lab02-学号-姓名/
├── lab02-before.txt
├── lab02-kvm-result.txt
├── course-vm01.xml
├── image-checksum.txt
├── guest-login.txt或截图
└── lifecycle-record.md
```

## 十、常见问题

### 1. `virt-host-validate`提示hardware virtualization FAIL

返回实验1检查CPU标志和VMware嵌套虚拟化。不能通过将虚拟机类型改成纯QEMU模拟来掩盖问题，因为性能会显著下降且不符合本实验KVM目标。

### 2. 无法连接`qemu:///system`

依次检查软件包、`virtqemud.socket`或教师统一的`libvirtd`、当前命令是否使用sudo，以及日志：

```bash
systemctl status virtqemud.socket --no-pager
sudo journalctl -u virtqemud -n 50 --no-pager
```

### 3. `default`网络不存在

确认`libvirt-daemon-config-network`已经安装，再使用教师提供的XML定义。不要从不可信网站复制带有未知网段或转发规则的配置。

### 4. 客户机启动但没有IP

检查：

```bash
sudo virsh domiflist course-vm01
sudo virsh net-info default
sudo virsh net-dhcp-leases default
ip -brief address | grep virbr
```

然后通过控制台检查客户机网卡是否启用DHCP。

### 5. `virsh console`无输出

先按Enter；确认教师镜像已启用串口控制台。若镜像只支持SSH，以`net-dhcp-leases`获得地址后SSH连接。

### 6. 镜像权限或SELinux错误

```bash
ls -lZ /var/lib/libvirt/images/course-vm01.qcow2
sudo restorecon -v /var/lib/libvirt/images/course-vm01.qcow2
sudo journalctl -u virtqemud -n 50 --no-pager
```

不要使用`chmod 777`。

## 十一、课后思考与拓展

1. 为什么取消虚拟机定义通常不会自动删除磁盘？
2. 为什么管理工具应通过libvirt操作，而不是让每个用户直接启动QEMU？
3. `destroy`没有删除磁盘，为什么仍然属于高风险操作？

## 十二、环境保留或清理

- 保留KVM软件包、默认网络、默认存储池和`course-vm01`。
- 关闭`course-vm01`以节省资源，但不取消定义、不删除磁盘。
- 保留教师基础镜像和个人工作镜像，实验3继续使用。

