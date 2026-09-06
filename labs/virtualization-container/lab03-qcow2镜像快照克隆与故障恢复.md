# 实验3：qcow2镜像、快照、克隆与故障恢复

> 所属模块：模块一 服务器虚拟化与云资源基础
>
> 建议学时：6学时
>
> 实验方式：个人
>
> 对应教材：《模块一 服务器虚拟化与云资源基础》第3章
>
> 前置实验：实验2
>
> 项目成果：基础镜像、差异克隆、快照或备份、故障恢复记录和校验结果

## 一、项目情境

测试人员需要快速获得多台环境相同的Linux主机，并能够在配置失败后恢复到已知状态。如果每次都从ISO安装，不仅耗时，也难以保证环境一致。你需要使用qcow2镜像、克隆和恢复点构建可复制、可回退的虚拟机交付流程，同时避免误改教师基础镜像。

## 二、实验目标

### 1. 知识目标

1. 区分镜像虚拟容量、宿主机实际占用、稀疏文件和写时复制。
2. 说明完整复制、后备文件差异镜像、虚拟机克隆和快照的关系。
3. 区分虚拟机配置XML、磁盘镜像和客户机内部数据。
4. 理解快照不是长期备份，恢复操作必须经过功能复测。

### 2. 能力目标

1. 使用`qemu-img`检查和创建qcow2镜像。
2. 使用`virt-clone`复制虚拟机定义和磁盘。
3. 清理克隆机的主机名、machine-id和SSH主机密钥冲突。
4. 创建恢复点、注入故障、执行恢复并验证数据与服务。
5. 安全归档虚拟机XML和磁盘校验信息。

### 3. 素质目标

1. 始终把教师基础镜像与个人工作镜像分开。
2. 恢复前确认目标，恢复后从使用者路径复测。
3. 认识到快照链过长、克隆身份重复和镜像散落都会形成运维风险。

## 三、知识准备

### 1. 镜像关系

```text
教师基础镜像（只读）
├── 完整复制 → course-vm01.qcow2
└── 后备文件 → course-vm02-overlay.qcow2
                 只保存相对基础镜像发生的变化
```

差异镜像依赖后备文件。如果移动、删除或修改基础镜像，差异镜像可能无法启动。因此正式交付必须记录后备链，并根据交付方式决定是否合并。

### 2. 三种恢复方式

| 方式 | 适用场景 | 主要风险 |
|---|---|---|
| VMware快照 | 整个Rocky KVM宿主环境回退 | 回退范围大，会同时影响多项实验 |
| libvirt/qcow2快照 | 单台KVM客户机短期实验恢复 | 快照链和运行状态管理较复杂 |
| 关机镜像备份 | 教学环境中最直观可靠的长期回退 | 复制耗时、占用空间较大 |

本实验以“关机一致性备份”为基础保障，再根据统一环境完成一次libvirt快照体验。

## 四、实验环境

- 实验2创建的`course-vm01`及其qcow2磁盘。
- `course-vm01`可以控制台或SSH登录。
- 默认存储池位于`/var/lib/libvirt/images`。
- `virt-clone`、`qemu-img`、`sha256sum`可用。
- 宿主机至少有12GB空闲空间；不足时使用差异镜像路线。

## 五、项目任务

1. 检查现有虚拟机和镜像关系。
2. 创建虚拟机配置和磁盘一致性备份。
3. 创建`course-vm02`克隆机并消除身份冲突。
4. 创建短期恢复点。
5. 注入配置故障并恢复。
6. 检查、校验和记录镜像交付信息。

## 六、实验步骤

### 任务一：建立镜像资产清单

#### 步骤1：确认虚拟机与磁盘

在Rocky KVM宿主机执行：

```bash
mkdir -p ~/vc-course/evidence ~/vc-course/backup/lab03 ~/vc-course/manifests
sudo virsh list --all
sudo virsh domblklist course-vm01 --details
sudo virsh dumpxml course-vm01 > ~/vc-course/manifests/course-vm01-before.xml
```

从`domblklist`找到系统磁盘路径，课程统一值应为：

```text
/var/lib/libvirt/images/course-vm01.qcow2
```

如果不同，以实际XML和教师基线为准，不盲目复制命令中的路径。

#### 步骤2：检查镜像信息和空间

```bash
sudo qemu-img info --backing-chain /var/lib/libvirt/images/course-vm01.qcow2
sudo qemu-img check /var/lib/libvirt/images/course-vm01.qcow2
sudo du -h /var/lib/libvirt/images/course-vm01.qcow2
sudo du -h --apparent-size /var/lib/libvirt/images/course-vm01.qcow2
df -h /var/lib/libvirt/images
```

比较实际占用与表面大小。`qemu-img check`应在没有宿主机I/O错误的情况下完成；对正在大量写入的镜像不做破坏性修复。

### 任务二：创建一致性备份

#### 步骤3：正常关闭虚拟机

```bash
sudo virsh shutdown course-vm01
```

确认已关闭：

```bash
sudo virsh domstate course-vm01
```

只有返回`shut off`后才继续复制。若迟迟不关机，先进入客户机检查，不直接强制断电。

#### 步骤4：备份配置和磁盘

```bash
sudo virsh dumpxml course-vm01 > ~/vc-course/backup/lab03/course-vm01-baseline.xml
sudo cp --sparse=always \
  /var/lib/libvirt/images/course-vm01.qcow2 \
  ~/vc-course/backup/lab03/course-vm01-baseline.qcow2
sudo chown "$(id -u):$(id -g)" \
  ~/vc-course/backup/lab03/course-vm01-baseline.qcow2
sha256sum \
  ~/vc-course/backup/lab03/course-vm01-baseline.qcow2 \
  > ~/vc-course/backup/lab03/SHA256SUMS
```

验证：

```bash
sha256sum -c ~/vc-course/backup/lab03/SHA256SUMS
qemu-img info ~/vc-course/backup/lab03/course-vm01-baseline.qcow2
```

> **验收点**：XML与磁盘备份同时存在，校验通过，源虚拟机仍处于关闭状态。

### 任务三：创建克隆虚拟机

#### 步骤5：检查目标名称和文件

```bash
sudo virsh dominfo course-vm02 2>/dev/null || true
sudo test ! -e /var/lib/libvirt/images/course-vm02.qcow2
```

如果目标已经存在，确认其来源。不能直接覆盖或使用模糊删除命令。

#### 步骤6：使用virt-clone完整克隆

```bash
sudo virt-clone \
  --original course-vm01 \
  --name course-vm02 \
  --file /var/lib/libvirt/images/course-vm02.qcow2
```

检查：

```bash
sudo virsh list --all
sudo virsh domuuid course-vm01
sudo virsh domuuid course-vm02
sudo virsh domblklist course-vm02
sudo qemu-img info /var/lib/libvirt/images/course-vm02.qcow2
```

两个libvirt UUID必须不同，磁盘路径也必须不同。

#### 步骤7：启动克隆并修改身份

```bash
sudo virsh start course-vm02
sudo virsh net-dhcp-leases default
```

通过控制台或SSH登录`course-vm02`，执行：

```bash
sudo hostnamectl set-hostname kvm-node02
sudo rm -f /etc/ssh/ssh_host_*
sudo ssh-keygen -A
sudo systemctl restart sshd
```

重新生成machine-id需要重启，先执行：

```bash
sudo truncate -s 0 /etc/machine-id
sudo rm -f /var/lib/dbus/machine-id
sudo systemd-machine-id-setup
sudo reboot
```

重新获得地址并登录后验证：

```bash
hostnamectl --static
cat /etc/machine-id
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

在`course-vm01`中执行同类命令，证明两台主机的machine-id和SSH主机密钥指纹不同。

如果教师基础镜像使用NetworkManager连接配置，确保克隆机使用DHCP。固定相同静态地址会造成冲突。

> **验收点**：`course-vm01`和`course-vm02`可以同时运行，地址、libvirt UUID、machine-id和SSH主机密钥均不相同。

### 任务四：体验差异镜像

#### 步骤8：创建后备文件差异镜像

先把实验2的教师基础镜像路径记为实际值，然后执行：

```bash
sudo qemu-img create \
  -f qcow2 \
  -F qcow2 \
  -b <COURSE_MEDIA>/kvm/course-base.qcow2 \
  /var/lib/libvirt/images/course-overlay-demo.qcow2
sudo chown qemu:qemu /var/lib/libvirt/images/course-overlay-demo.qcow2
sudo restorecon -v /var/lib/libvirt/images/course-overlay-demo.qcow2
sudo qemu-img info --backing-chain \
  /var/lib/libvirt/images/course-overlay-demo.qcow2
```

观察新文件实际占用：

```bash
sudo du -h /var/lib/libvirt/images/course-overlay-demo.qcow2
```

本文件仅用于理解写时复制关系，不在本实验中定义第三台长期虚拟机。

> **风险说明**：不要移动或删除后备文件。差异镜像本身不是一个完全独立的交付包。

### 任务五：创建恢复点并注入故障

#### 步骤9：为course-vm01创建关机快照

确保`course-vm01`关闭：

```bash
sudo virsh shutdown course-vm01
sudo virsh domstate course-vm01
```

状态为`shut off`后：

```bash
sudo virsh snapshot-create-as \
  course-vm01 \
  lab03-clean \
  --description '实验3故障注入前恢复点'
sudo virsh snapshot-list course-vm01
sudo virsh snapshot-info course-vm01 lab03-clean
```

如果统一环境不支持该快照方式，保留前面已完成的关机镜像备份作为正式恢复点，并在报告中记录“不支持”的完整提示。

#### 步骤10：写入基线标记

启动并进入`course-vm01`：

```bash
sudo virsh start course-vm01
```

在客户机执行：

```bash
echo 'LAB03_BASELINE_OK' | sudo tee /etc/course-lab03-marker
sudo cp /etc/hosts /etc/hosts.lab03.bak
hostname
cat /etc/course-lab03-marker
```

由于标记写在快照创建之后，它用于观察回退效果。另在个人报告中记录当前IP和主机名。

#### 步骤11：注入可恢复故障

在客户机中把主机名修改为错误值，并追加错误hosts记录：

```bash
sudo hostnamectl set-hostname broken-node
echo '192.0.2.99 wrong.course.local' | sudo tee -a /etc/hosts
echo 'BROKEN_STATE' | sudo tee /etc/course-broken-state
```

验证故障状态确实存在：

```bash
hostnamectl --static
tail -n 3 /etc/hosts
cat /etc/course-broken-state
```

不要制造无法确定恢复范围的磁盘破坏。

### 任务六：恢复并复测

#### 步骤12：从libvirt快照恢复

回到Rocky宿主机，正常关闭客户机：

```bash
sudo virsh shutdown course-vm01
sudo virsh domstate course-vm01
```

状态为`shut off`后：

```bash
sudo virsh snapshot-revert course-vm01 lab03-clean --running
```

重新登录客户机，验证：

```bash
hostnamectl --static
test ! -e /etc/course-broken-state && echo 'BROKEN_STATE_REMOVED'
grep -F 'wrong.course.local' /etc/hosts || echo 'WRONG_HOSTS_REMOVED'
test ! -e /etc/course-lab03-marker && echo 'POST_SNAPSHOT_MARKER_REMOVED'
```

因为快照创建在标记和故障之前，恢复后这两个后写文件都不应存在。

#### 步骤13：使用镜像备份恢复的替代路线

若快照不可用，先关闭并取消当前定义，但保留故障磁盘用于证据：

```bash
sudo virsh shutdown course-vm01
sudo virsh domstate course-vm01
sudo virsh undefine course-vm01
sudo mv \
  /var/lib/libvirt/images/course-vm01.qcow2 \
  /var/lib/libvirt/images/course-vm01-broken.qcow2
sudo cp --sparse=always \
  ~/vc-course/backup/lab03/course-vm01-baseline.qcow2 \
  /var/lib/libvirt/images/course-vm01.qcow2
sudo chown qemu:qemu /var/lib/libvirt/images/course-vm01.qcow2
sudo restorecon -v /var/lib/libvirt/images/course-vm01.qcow2
sudo virsh define ~/vc-course/backup/lab03/course-vm01-baseline.xml
sudo virsh start course-vm01
```

只有在教师确认使用替代路线时执行。每一步目标均为明确文件，不能改用宽泛通配符。

#### 步骤14：完成使用者路径复测

无论使用哪种恢复方式，都要检查：

```bash
sudo virsh list --all
sudo virsh domifaddr course-vm01 --source lease
```

进入客户机检查：

```bash
hostnamectl
ip -brief address
ip route
systemctl is-active sshd
```

从Rocky宿主机使用SSH连接客户机。恢复成功不能只以`virsh`返回成功判断。

### 任务七：生成资产与恢复记录

#### 步骤15：输出镜像清单

```bash
{
  date -Is
  echo '=== domains ==='
  sudo virsh list --all
  echo '=== disks ==='
  sudo virsh domblklist course-vm01
  sudo virsh domblklist course-vm02
  echo '=== snapshots ==='
  sudo virsh snapshot-list course-vm01
  echo '=== image info ==='
  sudo qemu-img info /var/lib/libvirt/images/course-vm01.qcow2
  sudo qemu-img info /var/lib/libvirt/images/course-vm02.qcow2
  sudo qemu-img info --backing-chain /var/lib/libvirt/images/course-overlay-demo.qcow2
} > ~/vc-course/evidence/lab03-assets.txt
```

## 七、独立实践

根据以下要求，自行设计一个新的可恢复故障：

- 只能影响`course-vm02`；
- 不能破坏磁盘分区或删除系统目录；
- 恢复前要证明故障真实存在；
- 恢复后要从SSH或服务功能路径复测；
- 报告必须说明选择快照还是镜像备份以及原因。

## 八、验收标准

- [ ] 能解释虚拟容量和实际占用的区别。
- [ ] `course-vm01`已形成XML与关机一致性镜像备份。
- [ ] 备份SHA256校验通过。
- [ ] `course-vm02`与原机的UUID、IP、machine-id和SSH主机密钥不重复。
- [ ] 差异镜像能够显示正确后备链。
- [ ] 完成一次快照或镜像备份恢复。
- [ ] 故障注入前后均有可观察证据。
- [ ] 恢复后网络、SSH和客户机身份复测通过。
- [ ] 能说明快照为什么不能替代长期备份。

## 九、成果提交

```text
lab03-学号-姓名/
├── course-vm01-baseline.xml
├── SHA256SUMS
├── lab03-assets.txt
├── clone-identity-check.md
├── backing-chain.txt
├── fault-and-recovery.md
└── screenshots/
```

不提交体积较大的qcow2文件，只提交校验值和教师指定的共享存储位置。

## 十、常见问题

### 1. 复制镜像后宿主机空间不足

立即停止创建更多完整副本，检查：

```bash
df -h /var/lib/libvirt/images
sudo du -sh /var/lib/libvirt/images/*
```

由教师决定使用差异镜像还是释放明确的旧实验资源，不能自行删除未知镜像。

### 2. 克隆机与原机IP相同

检查客户机是否写死静态地址，以及NetworkManager连接是否携带相同标识。课程克隆模板应使用DHCP。先关闭其中一台，修改克隆机网络身份后再同时启动。

### 3. SSH提示远程主机标识改变

确认这是克隆机身份重建造成的预期变化，而不是中间人攻击。使用明确地址删除对应旧记录：

```bash
ssh-keygen -R <KVM_GUEST_IP>
```

重新连接前核对控制台中显示的SSH主机密钥指纹。

### 4. 快照恢复失败

检查虚拟机状态、磁盘格式、快照列表和日志：

```bash
sudo virsh domstate course-vm01
sudo virsh snapshot-list course-vm01
sudo qemu-img info /var/lib/libvirt/images/course-vm01.qcow2
sudo journalctl -u virtqemud -n 80 --no-pager
```

改用已验证的关机一致性镜像备份，不反复执行不明恢复命令。

### 5. 差异镜像提示找不到后备文件

```bash
sudo qemu-img info --backing-chain /var/lib/libvirt/images/course-overlay-demo.qcow2
```

恢复后备文件原路径。不要随意使用`rebase -u`修改链条；需要合并时由教师演示并先备份。

## 十一、课后思考与拓展

1. 为什么克隆虚拟机后不能只修改主机名？
2. 差异镜像节省空间的代价是什么？
3. OpenStack从镜像创建多台实例时，需要解决哪些身份和网络冲突？

## 十二、环境保留或清理

- 保留`course-vm01`和`course-vm02`，实验4需要两台客户机。
- 保留`lab03-clean`恢复点到实验5结束。
- `course-overlay-demo.qcow2`未定义为虚拟机，可在教师验收后明确删除：

```bash
sudo test -f /var/lib/libvirt/images/course-overlay-demo.qcow2
sudo rm /var/lib/libvirt/images/course-overlay-demo.qcow2
```

- 保留`~/vc-course/backup/lab03`和`~/vc-course/evidence/lab03-assets.txt`。

