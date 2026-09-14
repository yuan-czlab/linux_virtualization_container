# 实验1：虚拟化技术认知与嵌套虚拟化环境准备

> 所属模块：模块一 服务器虚拟化与云资源基础
>
> 建议学时：4学时
>
> 实验方式：个人
>
> 对应教材：《模块一 服务器虚拟化与云资源基础》第1章
>
> 知识前置：《Linux操作系统》核心能力、计算机组成原理和网络基础
>
> 状态依赖：Linux课程保留的三台VM及`Linux-L4`；本机或本组指定机位能够启用嵌套虚拟化
>
> 建议起点：`Linux-L4`
>
> 项目成果：虚拟化层次图、三机继承检查表、`rocky-server`嵌套虚拟化能力记录和可回退快照

## 一、项目情境

你将继续使用Linux课程留下的`rocky-server`、`rocky-web`和`ubuntu-client`进入虚拟化与容器课程。后续`rocky-server`承担KVM宿主机和Docker环境A，`ubuntu-client`承担Docker环境B；`rocky-web`保留Linux课程成果，平时关机节省资源。若不先核对CPU虚拟化、内存、磁盘、网络、SSH和快照，后面的KVM失败很难判断究竟是硬件、VMware还是Rocky配置造成的。

本实验先建立可证明、可回退的课程基线，再在`rocky-server`中确认是否获得了嵌套虚拟化能力。

## 二、实验目标

### 1. 知识目标

1. 区分物理机、宿主机、客户机、Hypervisor、虚拟机和容器。
2. 说明Type 1与Type 2 Hypervisor的基本差异。
3. 说明Windows、VMware、Rocky KVM宿主机和KVM客户机的嵌套层次。
4. 说明VMware、KVM、QEMU、libvirt、OpenStack的基本关系。

### 2. 能力目标

1. 检查Windows和VMware中的硬件虚拟化条件。
2. 核对三台Linux虚拟机身份、快照、资源和网络基线。
3. 在`rocky-server`中检查CPU虚拟化标志和`/dev/kvm`条件。
4. 建立清晰命名的课程快照和环境记录。

### 3. 素质目标

1. 先检查、再修改，避免把环境问题误判为命令问题。
2. 形成资源预算、操作留痕和可恢复意识。
3. 不随意删除Linux课程留下的实验成果。

## 三、知识准备

### 1. 本课程的虚拟化层次

```text
L0 Windows物理机
└── VMware Workstation（桌面Hypervisor）
    ├── L1 rocky-server（Rocky Linux虚拟机）
    │   ├── KVM/QEMU/libvirt
    │   └── L2 KVM客户机
    ├── L1 ubuntu-client（Ubuntu Desktop虚拟机）
    └── L1 rocky-web（保留Linux课程成果，按需启动）
```

嵌套虚拟化是指L1虚拟机继续充当Hypervisor运行L2虚拟机。它适合教学、开发和测试，性能与稳定性不能等同于裸机生产环境。

### 2. 组件关系

```text
virsh / virt-install
        ↓
      libvirt
        ↓
       QEMU
        ↓
   KVM内核模块
        ↓
CPU硬件虚拟化能力
```

OpenStack不是另一种CPU虚拟化技术。它通过计算、镜像、网络等服务统一管理大量云资源，计算节点通常可以使用KVM和libvirt创建实例。

### 3. 资源预算

| 对象 | 建议资源 | 说明 |
|---|---|---|
| `rocky-server` KVM宿主机 | 4 vCPU、6—8GB内存、至少30GB可用空间 | 做KVM实验时关闭另外两台L1虚拟机 |
| `ubuntu-client` Docker主机 | 2 vCPU、2—4GB内存、至少20GB可用空间 | 模块二再与`rocky-server`同时开启 |
| `rocky-web`保留主机 | 沿用Linux课程资源 | 默认关机，不删除磁盘和快照 |
| 单台KVM客户机 | 1 vCPU、1—2GB内存、4—8GB磁盘 | 使用教师轻量镜像 |

实际配置以机房统一基线为准。宿主机总资源不足时不能简单把两台VM都调大。

## 四、实验环境

- Windows 10/11学生机，BIOS/UEFI已启用Intel VT-x或AMD-V。
- VMware Workstation已安装。
- Linux课程保留的`rocky-server`、`rocky-web`和`ubuntu-client`三台虚拟机。
- 三台主机分别使用同名主账号，课堂密码均为`123456`且具备sudo权限；`ubuntu-client`能够通过SSH访问两台Rocky。
- 教师发布《机房资源与VMware设置表》。

## 五、项目任务

1. 绘制本机虚拟化层次图。
2. 检查Windows与VMware环境。
3. 核对三台Linux虚拟机身份和基线。
4. 为`rocky-server`启用嵌套虚拟化。
5. 在`rocky-server`内部确认CPU虚拟化标志。
6. 建立课程基线快照和环境检查表。

## 六、实验步骤

### 任务一：识别现有环境

#### 步骤1：记录Windows宿主机资源

在Windows中打开“任务管理器 → 性能”，记录：

- CPU型号、逻辑处理器数量；
- 内存总量与当前可用量；
- 磁盘剩余空间；
- CPU页面中“虚拟化”是否显示“已启用”。

如果显示“已禁用”，停止后续KVM实验并报告教师。BIOS/UEFI修改由教师或机房管理员统一处理。

#### 步骤2：核对VMware虚拟机

确认VMware虚拟机列表中存在且名称完全一致：

```text
rocky-server
rocky-web
ubuntu-client
```

若名称不一致，先对照Linux实验1核实虚拟机身份，再在VMware中改正显示名称；不要新建重复虚拟机。三台机器的网络适配器继续使用Linux课程确定的同一VMnet。

在修改任何VMware硬件设置前，确认三台VM均有Linux课程结束时建立的`Linux-L4`快照，并核对快照说明中的日期、IP和服务清单。还应确认教师保存的`Linux-L4`独立VM副本可定位；只有快照而没有独立副本，不能应对虚拟机目录被机房还原或损坏。

### 任务二：检查三机基线

#### 步骤3：在`rocky-server`记录基线

登录`rocky-server`执行：

```bash
hostnamectl
cat /etc/os-release
uname -r
lscpu | sed -n '1,25p'
free -h
df -hT /
ip -brief address
ip route
systemctl is-active sshd
getenforce
```

将结果保存：

```bash
mkdir -p ~/vc-course/evidence ~/vc-course/backup
{
  date -Is
  hostnamectl
  cat /etc/os-release
  uname -r
  lscpu
  free -h
  df -hT
  ip -brief address
  ip route
  nmcli connection show --active
  test -d ~/m1-project && echo 'm1_project=present' || echo 'm1_project=missing'
  systemctl is-active sshd
  systemctl is-active firewalld
  getenforce
} > ~/vc-course/evidence/lab01-rocky-server-baseline.txt
```

预期：系统为Rocky Linux 9，`course-static`或教师登记的静态连接处于活动状态，`~/m1-project`存在，SSH与firewalld为active，根文件系统空间满足后续镜像需要，SELinux保持Enforcing。缺失项应先从`Linux-L4`恢复，不能在第二门课创建空目录冒充成果。

#### 步骤3A：建立第二门课程统一参数文件

课程媒体目录、镜像仓库和平台地址会随学期或机房变化，但它们不应散落在每条命令中反复手填。在`rocky-server`创建统一参数文件；如果文件已存在则保留原内容：

```bash
mkdir -p ~/vc-course
if [[ ! -f ~/vc-course/course-env.sh ]]; then
  cat > ~/vc-course/course-env.sh <<'EOF'
[[ -r "$HOME/m1-project/course-env.sh" ]] && source "$HOME/m1-project/course-env.sh"
export COURSE_MEDIA='CHANGE_ME'
export COURSE_REGISTRY='CHANGE_ME'
export COURSE_REGISTRY_USER='CHANGE_ME'
export COURSE_TAG='CHANGE_ME'
export ROCKY_DOCKER_VERSION='CHANGE_ME'
export UBUNTU_DOCKER_VERSION='CHANGE_ME'
export OPENSTACK_URL='CHANGE_ME'
export OPENSTACK_KEY_SOURCE='CHANGE_ME'
export OPENSTACK_IMAGE_USER='CHANGE_ME'
export OPENSTACK_INSTANCE_IP='CHANGE_ME'
export K8S_CONTEXT='CHANGE_ME'
export K8S_NAMESPACE='CHANGE_ME'
export K8S_IMAGE='CHANGE_ME'
export KUBECONFIG_SOURCE='CHANGE_ME'
EOF
  chmod 600 ~/vc-course/course-env.sh
fi
nano ~/vc-course/course-env.sh
```

将教师本学期已经发布的值写在等号右侧，变量值保留单引号。尚未创建的OpenStack实例地址、个人私钥下载路径等动态值可以暂时保留`CHANGE_ME`，但进入对应实验前必须填写并通过该实验的单项检查。文件只保存地址、目录、命名空间和非机密标签，不保存平台密码或仓库密码。保存后核验本阶段立即要用的三项：

```bash
source ~/vc-course/course-env.sh
printf 'media=%s\nregistry=%s\ntag=%s\n' \
  "$COURSE_MEDIA" "$COURSE_REGISTRY" "$COURSE_TAG"
[[ "$COURSE_MEDIA" != 'CHANGE_ME' && -d "$COURSE_MEDIA" ]]
[[ "$COURSE_REGISTRY" != 'CHANGE_ME' ]]
[[ "$COURSE_TAG" != 'CHANGE_ME' ]]
```

任一核验命令返回非0时先修正参数，不继续执行依赖该参数的实验。此文件随`VC-V0`及后续检查点保留；在`ubuntu-client`进入Docker阶段时，从`rocky-server`安全复制同一份非机密参数文件。

#### 步骤4：在`ubuntu-client`和`rocky-web`记录基线

登录Ubuntu执行：

```bash
mkdir -p ~/vc-course/evidence ~/vc-course/backup
{
  date -Is
  hostnamectl
  cat /etc/os-release
  uname -r
  lscpu
  free -h
  df -hT
  ip -brief address
  ip route
  nmcli connection show --active
  test -d ~/m1-project && echo 'm1_project=present' || echo 'm1_project=missing'
  test -f ~/.ssh/config && sed -n '/^Host rocky-server$/,/^$/p' ~/.ssh/config || true
  systemctl is-active ssh
} > ~/vc-course/evidence/lab01-ubuntu-baseline.txt
```

确认`ubuntu-client`可以连接两台Rocky：

```bash
ping -c 3 rocky-server
ping -c 3 rocky-web
ssh rocky-server 'hostname; date -Is'
ssh rocky-web 'hostname; date -Is'
```

若实验10没有保留SSH别名，使用`rocky-server@<ROCKY_SERVER_IP>`和`rocky-web@<ROCKY_WEB_IP>`连接。

最后登录`rocky-web`执行以下轻量检查并保存结果：

```bash
mkdir -p ~/vc-course/evidence
{
  date -Is
  hostnamectl
  cat /etc/os-release
  ip -brief address
  nmcli connection show --active
  test -d ~/m1-project && echo 'm1_project=present' || echo 'm1_project=missing'
  systemctl is-active sshd
  systemctl is-active firewalld
  systemctl is-active nginx
} > ~/vc-course/evidence/lab01-rocky-web-baseline.txt
```

> **验收点**：三台Linux主机的身份与基线文件均已确认，`ubuntu-client`能够通过原有SSH路径连接两台Rocky。

### 任务三：在VMware启用嵌套虚拟化

#### 步骤5：安全关闭三台虚拟机

先分别正常关闭三台虚拟机。以下命令在每台Linux中执行：

```bash
sudo systemctl poweroff
```

等待VMware显示三台虚拟机均已完全关闭。不能在挂起状态修改处理器虚拟化设置。

#### 步骤6：调整`rocky-server`虚拟机资源

在VMware中打开`rocky-server`虚拟机设置：

1. 选择“处理器”。
2. 根据机房表设置处理器数量和每个处理器核心数，总vCPU建议为4。
3. 勾选名称类似“虚拟化Intel VT-x/EPT或AMD-V/RVI”的选项。
4. 内存调整为机房统一值，建议6—8GB。
5. 不修改原有虚拟网卡模式。

不同VMware版本的中文名称可能不同，应以“向客户机暴露硬件辅助虚拟化能力”为判断标准。

如果选项不可勾选或启动时报“VMware与Hyper-V不兼容”“不支持嵌套虚拟化”等错误，记录完整提示，不自行关闭Windows安全功能或删除虚拟机。先切换到本组课前已经验证通过的KVM机位；若整组机位都不支持，再使用教师准备的远程KVM环境。分组共享只改变操作入口，每名学生仍需独立完成命令解释、证据记录和答辩。

#### 步骤7：只启动`rocky-server`并检查CPU标志

启动后执行：

```bash
grep -Ewo 'vmx|svm' /proc/cpuinfo | sort -u
lscpu | grep -E 'Virtualization|虚拟化' || true
```

Intel处理器通常应看到`vmx`，AMD处理器通常应看到`svm`。继续统计标志出现次数：

```bash
grep -Eoc '(vmx|svm)' /proc/cpuinfo
```

正常结果应大于0。如果为0，说明Rocky没有获得硬件虚拟化能力，后续即使安装软件包也不能正常使用KVM加速。本机不继续实验2，按前一步切换到已验证机位或远程KVM主机；不要把纯QEMU软件模拟的慢速结果冒充KVM验收。

#### 步骤8：检查内核设备准备状态

当前尚未安装KVM软件包时，部分对象可能不存在，先记录：

```bash
ls -l /dev/kvm 2>/dev/null || echo '/dev/kvm 尚不存在'
lsmod | grep '^kvm' || echo 'KVM模块尚未加载'
```

不要因为`/dev/kvm`暂时不存在就直接修改系统；实验2安装软件并加载模块后再次验证。

### 任务四：建立可回退基线

#### 步骤9：生成环境检查表

在`rocky-server`执行：

```bash
{
  echo 'course=virtualization-container'
  echo "checked_at=$(date -Is)"
  echo "host=$(hostname)"
  echo "arch=$(uname -m)"
  echo "kernel=$(uname -r)"
  echo "virtualization_flags=$(grep -Ewo 'vmx|svm' /proc/cpuinfo | sort -u | paste -sd, -)"
  echo "memory=$(free -h | awk '/^Mem:/ {print $2}')"
  echo "root_free=$(df -hP / | awk 'NR==2 {print $4}')"
  echo "ipv4=$(ip -4 -brief address | awk '$1!="lo" {print $3}' | paste -sd, -)"
} | tee ~/vc-course/evidence/lab01-environment-check.txt
```

打开文件核对，不能出现关键字段为空而不说明原因。

#### 步骤10：创建VMware快照

为三台虚拟机分别创建快照。`rocky-server`应先正常关闭，另外两台此时本来就应处于关机状态：

```text
VC-V0-课程基线
```

快照说明至少写明：

- 创建日期；
- 三台虚拟机的版本与角色；
- 当前IP；
- Linux课程成果是否保留；
- `rocky-server`已启用嵌套虚拟化；
- Docker和KVM尚未安装或当前状态。

重新启动`rocky-server`，确认SSH和网络仍正常；`rocky-web`与`ubuntu-client`保持关机，直到实验步骤明确需要。

## 七、独立实践

不查看教师示例，用自己的环境绘制一张层次图，至少包含：

```text
Windows → VMware → rocky-server → KVM/libvirt → KVM客户机
Windows → VMware → rocky-server / ubuntu-client → Docker
Windows → VMware → rocky-web（Linux课程Web角色，按需启动）
```

在图中标出哪一层是物理资源、哪一层是虚拟机、哪一层以后运行容器。

## 八、验收标准

- [ ] 能解释物理机、宿主机、客户机和Hypervisor。
- [ ] Windows任务管理器显示虚拟化已启用，或已记录教师确认的替代环境。
- [ ] 三台虚拟机的身份、角色和基线文件完整。
- [ ] `ubuntu-client`能够通过SSH连接两台Rocky。
- [ ] 三机静态连接、`~/m1-project`、firewalld、SELinux和Linux服务成果已经核对。
- [ ] `rocky-server`的`vmx`或`svm`统计值大于0。
- [ ] `rocky-server`资源满足机房统一要求。
- [ ] 三台VM均存在`VC-V0-课程基线`快照。
- [ ] 虚拟化层次图对象与上下层关系正确。

## 九、成果提交

```text
lab01-学号-姓名/
├── virtualization-layers.png或.pdf
├── lab01-rocky-server-baseline.txt
├── lab01-rocky-web-baseline.txt
├── lab01-ubuntu-baseline.txt
├── lab01-environment-check.txt
├── vmware-settings.png
└── snapshot-record.png
```

截图不得包含真实密码、私钥或其他学生信息。

## 十、常见问题

### 1. Rocky中没有`vmx`或`svm`

按以下顺序检查：

1. Windows任务管理器是否显示虚拟化已启用；
2. Rocky是否完全关机后再修改设置；
3. VMware处理器设置是否勾选嵌套虚拟化；
4. Windows是否启用了与当前VMware版本冲突的Hyper-V/VBS功能；
5. 机房是否提供远程KVM回退环境。

不要在不清楚机房策略时自行关闭Windows安全功能。

### 2. 分配资源后Windows非常卡

关闭暂时不用的Ubuntu虚拟机，恢复教师规定的内存与vCPU值。分配给虚拟机的总内存不能接近或超过物理机可用内存。

### 3. Ubuntu无法SSH连接Rocky

依次检查Rocky地址、VMware网卡模式、两机地址与路由、`sshd`、22端口和防火墙，不因本课程开始而重新配置一套无关网络。

## 十一、课后思考与拓展

1. 为什么嵌套虚拟化适合教学，却通常不作为生产虚拟机的首选运行方式？
2. KVM在Linux内核中工作，QEMU、libvirt和`virsh`分别承担什么职责？
3. OpenStack为什么仍然需要底层Hypervisor？

## 十二、环境保留或清理

- 保留三台虚拟机及各自的`VC-V0-课程基线`快照。
- 保留`~/vc-course/evidence`。
- 不安装或删除KVM、Docker；安装从对应实验开始。
