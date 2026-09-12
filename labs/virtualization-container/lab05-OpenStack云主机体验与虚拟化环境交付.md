# 实验5：OpenStack云主机体验与虚拟化环境交付

> 所属模块：模块一 服务器虚拟化与云资源基础
>
> 建议学时：4学时
>
> 实验方式：个人
>
> 对应教材：《模块一 服务器虚拟化与云资源基础》第5章
>
> 知识前置：实验1—4中的虚拟机、镜像、规格和虚拟网络对象
>
> 状态依赖：实验4的KVM环境用于模块交付；另需教师预建OpenStack平台、账号、配额、镜像和网络
>
> 建议起点：保留实验2—4成果的当前环境
>
> 项目成果：OpenStack实例、网络与安全组操作记录，以及KVM环境归档和恢复说明

## 一、项目情境

你已经在单台Rocky主机中使用KVM和libvirt完成虚拟机、镜像和网络管理。企业云平台不会让每位用户直接登录计算节点执行`virsh`，而是通过统一身份、项目、配额、镜像、规格、网络和安全组提供自助服务。本实验要求你在教师预建OpenStack平台中创建一台云主机，把界面对象与前四个实验的KVM对象建立对应，并完成模块一环境交付。

## 二、实验目标

### 1. 知识目标

1. 说明OpenStack不是Hypervisor，而是云资源管理平台。
2. 说明Nova、Glance、Neutron、Keystone与Horizon在本实验中的基本职责。
3. 建立镜像、规格、实例、网络、子网、端口、安全组和密钥对的关系。
4. 说明OpenStack实例与KVM虚拟机的联系和管理边界。

### 2. 能力目标

1. 登录教师提供的OpenStack项目并识别项目配额。
2. 创建实验安全组和密钥对。
3. 从指定镜像、规格和网络启动实例。
4. 通过控制台或SSH验证实例，完成资源清理。
5. 归档KVM环境配置、镜像清单和恢复说明。

### 3. 素质目标

1. 遵守项目和命名空间边界，不操作他人资源。
2. 创建资源前检查配额，实验结束清理临时云资源。
3. 不把OpenStack密码、RC文件或私钥提交到公共仓库。

## 三、知识准备

### 1. OpenStack对象与KVM对象映射

| OpenStack对象 | KVM实验中的相近对象 | 说明 |
|---|---|---|
| Image镜像 | qcow2基础镜像 | 用于创建实例的系统模板 |
| Flavor规格 | `virt-install`中的vCPU、内存和磁盘 | 标准化资源组合 |
| Instance实例 | libvirt虚拟机定义和QEMU进程 | 用户看到的云主机 |
| Network/Subnet | libvirt虚拟网络、网段和DHCP | 提供实例网络 |
| Port端口 | 虚拟网卡及其MAC/IP绑定 | 实例连接网络的逻辑接口 |
| Security Group | 实例端口访问规则 | 不是客户机内部firewalld的同一个对象 |
| Key Pair密钥对 | SSH公钥注入 | 用于首次安全登录 |

### 2. 服务关系

```text
用户 → Horizon或OpenStack API
     → Keystone确认身份和项目
     → Glance提供镜像
     → Nova调度并创建实例
     → Neutron提供网络、端口和安全组
     → 计算节点上的Hypervisor运行虚拟机
```

### 3. 实验边界

本实验不安装OpenStack，不修改控制节点和计算节点配置，不讲生产高可用。学生只在自己的项目和教师指定网络中完成最终用户操作。

## 四、实验环境

- 教师提供`<OPENSTACK_URL>`、个人账号、项目名称和实验配额。
- 教师指定可用镜像、规格、网络和外部访问方式。
- 浏览器能够访问Horizon。
- 学生具有保存临时私钥的安全目录。
- OpenStack平台不可用时，使用教师提供的远程恢复平台补做；不能用观看截图替代全部验收。

## 五、项目任务

1. 登录并检查项目和配额。
2. 建立最小安全组规则。
3. 创建或使用课程密钥对。
4. 从指定镜像启动实例。
5. 通过控制台或SSH验证实例。
6. 记录对象对应关系并清理云资源。
7. 归档模块一KVM环境。

## 六、实验步骤

### 任务一：登录并建立项目基线

#### 步骤1：登录Horizon

在浏览器打开教师发布的：

```text
<OPENSTACK_URL>
```

输入教师提供的域、用户名和密码。登录后确认右上角或项目选择器显示的是自己的课程项目。

禁止使用他人账号，也不要让浏览器保存公共机房密码。

#### 步骤2：检查配额

进入“项目 → 计算 → 概览”或教师指定的配额页面，记录：

- 实例数量；
- vCPU；
- 内存；
- 浮动IP；
- 安全组与规则；
- 卷或存储配额。

计算创建一台教师指定规格的实例后还剩多少资源。配额不足时先清理自己项目中确认无用的旧实验实例，不删除未知资源。

### 任务二：准备访问控制

#### 步骤3：创建课程安全组

进入“项目 → 网络 → 安全组”，创建：

```text
名称：vc-lab-<学号>
说明：虚拟化容器课程OpenStack体验
```

添加最小规则：

| 方向 | 协议 | 端口 | 来源 | 用途 |
|---|---|---|---|---|
| 入方向 | ICMP | 按平台界面 | 教师指定实验网段 | 连通性测试 |
| 入方向 | TCP | 22 | 教师指定实验网段 | SSH |

不要把SSH来源无条件设置为整个互联网。若平台只能选择`0.0.0.0/0`，必须在报告中说明这是教学平台限制，并在实验结束删除实例或规则。

#### 步骤4：创建密钥对

进入“项目 → 计算 → 密钥对”，创建：

```text
vc-key-<学号>
```

下载私钥后立即保存到个人目录，不通过聊天工具公开发送。在Linux终端中设置权限：

```bash
mkdir -p ~/vc-course/keys
mv <下载目录>/<私钥文件> ~/vc-course/keys/
chmod 600 ~/vc-course/keys/<私钥文件>
ls -l ~/vc-course/keys/<私钥文件>
```

如果平台由教师预置统一密钥，只使用教师指定路线，不重复创建导致配额浪费。

### 任务三：创建云主机实例

#### 步骤5：启动实例

进入“项目 → 计算 → 实例”，选择“创建实例”或“Launch Instance”，按教师清单填写：

| 字段 | 要求 |
|---|---|
| 实例名称 | `vc-os-<学号>` |
| 数量 | 1 |
| 引导源 | 教师指定课程镜像 |
| 规格 | 教师指定最小规格 |
| 网络 | 教师指定课程网络 |
| 安全组 | `vc-lab-<学号>` |
| 密钥对 | `vc-key-<学号>`或教师指定密钥 |

创建前最后核对：实例数量为1、镜像和网络正确、规格不超过配额、安全组不是默认全开放规则。

#### 步骤6：观察状态变化

刷新实例列表，记录状态从构建到运行的变化。打开实例详情，记录：

- 实例ID；
- 镜像；
- 规格；
- 项目网络IP；
- 安全组；
- 创建时间；
- 可用区或宿主信息中学生可见的字段。

如果实例进入ERROR，不反复连续点击创建。打开故障信息并报告教师，避免产生多台重复实例。

#### 步骤7：使用控制台验证

打开实例控制台或日志，确认操作系统已经启动。记录：

```bash
hostname
cat /etc/os-release
ip -brief address
```

若控制台只显示启动日志但不允许密码登录，继续使用SSH路线。

### 任务四：连接和验证实例

#### 步骤8：判断是否需要浮动IP

根据教师网络设计：

- 若学生终端能够直接访问项目网络IP，直接使用固定IP；
- 若必须通过外部网络访问，在教师指导下为实例关联浮动IP；
- 若只能从跳板机访问，先SSH到教师指定跳板机。

不能把“分配浮动IP”机械理解为所有OpenStack都必须执行的步骤。

#### 步骤9：检查安全组效果

从教师指定客户端执行：

```bash
ping -c 3 <INSTANCE_ACCESS_IP>
nc -vz <INSTANCE_ACCESS_IP> 22
```

ICMP可能因平台规则关闭而失败，必须结合22端口和SSH判断。

#### 步骤10：使用SSH密钥登录

镜像默认用户名由教师清单发布，常见值可能是`cloud-user`、`rocky`或`ubuntu`。执行：

```bash
ssh -i ~/vc-course/keys/<私钥文件> \
  <IMAGE_USER>@<INSTANCE_ACCESS_IP>
```

登录后：

```bash
hostnamectl
cat /etc/os-release
ip -brief address
ip route
curl -s http://169.254.169.254/ 2>/dev/null | head || true
```

最后一条仅观察镜像和平台是否提供元数据服务，不把无法访问视为本实验失败。

> **验收点**：实例处于运行状态，网络、安全组、镜像和规格正确，并能通过控制台或SSH获得系统级证据。

### 任务五：对比KVM与OpenStack

#### 步骤11：完成对象对应表

在报告中完成：

| 直接KVM操作 | OpenStack操作 | 背后可能使用的服务 |
|---|---|---|
| 复制qcow2并创建虚拟机 | 从Image启动Instance | Glance、Nova |
| 指定vCPU和内存 | 选择Flavor | Nova |
| 连接libvirt网络 | 选择Network/Subnet | Neutron |
| 配置访问规则 | 选择Security Group | Neutron |
| 配置SSH公钥 | 选择Key Pair | Nova元数据或配置注入 |

用100—200字说明为什么云用户通常不直接登录计算节点执行`virsh`。

### 任务六：清理OpenStack资源

#### 步骤12：保存证据后删除实例

先确认实例名称和ID属于自己：

```text
vc-os-<学号>
```

在实例菜单选择删除，等待资源从实例列表消失。确认配额释放。

#### 步骤13：清理临时网络对象

若安全组和密钥对仅用于本实验，按以下顺序处理：

1. 确认没有其他实例引用安全组；
2. 删除`vc-lab-<学号>`安全组；
3. 删除平台中的`vc-key-<学号>`公钥记录；
4. 安全保存或按教师要求删除本地私钥；
5. 释放本实验单独申请的浮动IP。

教师要求后续继续使用时保留，并在资源清单中注明用途。

### 任务七：交付模块一环境

#### 步骤14：关闭KVM客户机并导出配置

回到Rocky KVM宿主机：

```bash
sudo virsh shutdown course-vm01
sudo virsh shutdown course-vm02
sudo virsh list --all
sudo virsh dumpxml course-vm01 > ~/vc-course/manifests/course-vm01-final.xml
sudo virsh dumpxml course-vm02 > ~/vc-course/manifests/course-vm02-final.xml
sudo virsh net-dumpxml default > ~/vc-course/manifests/default-network-final.xml
```

只有两台虚拟机都显示`shut off`后才制作镜像校验。

#### 步骤15：生成资源清单

```bash
{
  date -Is
  echo '=== host ==='
  hostnamectl
  sudo virt-host-validate qemu
  echo '=== domains ==='
  sudo virsh list --all
  echo '=== networks ==='
  sudo virsh net-list --all
  echo '=== pools ==='
  sudo virsh pool-list --all
  echo '=== images ==='
  sudo qemu-img info /var/lib/libvirt/images/course-vm01.qcow2
  sudo qemu-img info /var/lib/libvirt/images/course-vm02.qcow2
} > ~/vc-course/evidence/module1-inventory.txt
```

生成校验值：

```bash
sudo sha256sum \
  /var/lib/libvirt/images/course-vm01.qcow2 \
  /var/lib/libvirt/images/course-vm02.qcow2 \
  | sudo tee ~/vc-course/evidence/module1-image-SHA256SUMS > /dev/null
sudo chown "$(id -u):$(id -g)" ~/vc-course/evidence/module1-image-SHA256SUMS
```

#### 步骤16：编写恢复说明

`module1-restore.md`至少写明：

1. Rocky宿主机资源要求；
2. KVM与libvirt软件包；
3. 镜像实际位置和校验方法；
4. 导入XML前需要修改的路径；
5. 定义网络、定义虚拟机和启动的顺序；
6. 获取客户机地址和验证SSH的方法；
7. 已知限制与远程KVM回退方案。

## 七、独立实践

教师随机提问一个对象，学生需要在自己的OpenStack记录和KVM环境中指出对应证据，例如：

- Flavor与vCPU/内存；
- Image与qcow2；
- Instance与libvirt Domain；
- Security Group与客户机firewalld的差异；
- Network与libvirt默认NAT网络。

## 八、验收标准

- [ ] 能说明OpenStack和KVM不是同一层技术。
- [ ] 登录的是个人课程项目并检查过配额。
- [ ] 安全组只开放教师要求的ICMP和SSH来源。
- [ ] 实例名称、镜像、规格、网络、密钥和安全组正确。
- [ ] 实例成功运行，并有控制台或SSH系统证据。
- [ ] 完成KVM与OpenStack对象对应表。
- [ ] 临时实例和不再使用的资源已按要求清理。
- [ ] 两台KVM客户机已安全关闭。
- [ ] 模块一XML、资源清单、镜像校验和恢复说明完整。

## 九、成果提交

```text
lab05-学号-姓名/
├── openstack-quota.png
├── openstack-instance-details.png
├── openstack-console-or-ssh.txt
├── kvm-openstack-mapping.md
├── course-vm01-final.xml
├── course-vm02-final.xml
├── default-network-final.xml
├── module1-inventory.txt
├── module1-image-SHA256SUMS
└── module1-restore.md
```

提交前检查并删除密码、私钥、OpenStack RC文件和Token。

## 十、常见问题

### 1. 实例长时间处于Scheduling或Building

不要重复创建。记录实例ID、状态和故障信息，由教师检查计算节点资源、镜像、网络和调度。学生只能操作项目范围内的资源。

### 2. 实例运行但SSH不通

依次检查：

```text
访问地址是否正确
→ 是否需要浮动IP或跳板机
→ 安全组22端口和来源
→ 密钥对是否在创建时选中
→ 镜像默认用户名
→ 实例内部sshd和网络
```

不能只检查安全组，也不能通过开放所有端口替代定位。

### 3. 私钥权限过宽

```bash
chmod 600 ~/vc-course/keys/<私钥文件>
```

再次检查文件所有者和路径。不要上传私钥截图或内容。

### 4. 创建实例提示超出配额

检查自己项目中的旧实例、卷、浮动IP和端口。只清理确认属于自己的资源；不能通过选择更大规格继续尝试。

### 5. 平台当天不可用

先完成教材中的对象映射和模块一KVM交付。教师恢复平台后安排补做，实验5的OpenStack操作证据仍为正式成果，不以普通截图讲解完全替代。

## 十一、课后思考与拓展

1. OpenStack为什么把镜像、计算和网络拆成不同服务？
2. 安全组与客户机内部firewalld为什么可能需要同时配置？
3. 从用户点击“创建实例”到KVM虚拟机运行，可能经过哪些服务？

## 十二、环境保留或清理

- OpenStack临时实例和不再使用的安全组、密钥对、浮动IP应清理。
- Rocky中的KVM客户机保持关闭并保留到课程结束，不删除镜像。
- 为Rocky创建VMware快照`VC-01-KVM模块完成`。
- 模块二开始前确认Rocky仍有足够磁盘空间安装Docker和保存镜像。

