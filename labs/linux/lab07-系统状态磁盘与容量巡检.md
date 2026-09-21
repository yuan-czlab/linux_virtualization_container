# 实验7：系统状态、磁盘挂载、LVM与容量巡检

> 所属模块：模块一 Linux基础运维
> 建议学时：4学时
> 实验方式：个人
> 对应教材：《模块一 Linux基础运维》第12章
> 知识前置：实验6中的进程、服务、日志和退出状态
> 状态依赖：实验2起持续保留的`~/m1-project`；`rocky-server`新增一块8GiB空白虚拟磁盘
> 建议起点：保留实验2—6成果并建立实验前快照
> 项目成果：普通数据盘、持久挂载、LVM逻辑卷、扩容验证和系统健康巡检报告

## 一、项目情境

服务器交付前不仅要检查CPU、内存和进程，还要把新增数据盘交付给业务使用。你需要识别空白虚拟磁盘，在不影响系统盘的前提下完成普通分区和LVM存储配置，验证重启后仍能挂载，再制造一个安全、可终止的CPU异常并形成巡检报告。

本实验完成后，`rocky-server`应形成以下结构：

```text
/dev/sdb（8GiB课程空白盘）
├── /dev/sdb1（约2GiB）→ XFS → /data
└── /dev/sdb2（剩余空间）→ PV → vg_data → lv_app（扩容后3GiB）
                                             └── XFS → /srv/appdata
```

## 二、实验目标

### 1. 知识目标

1. 区分CPU利用率与系统负载。
2. 说明`free`中的available与单纯free的差异。
3. 区分磁盘、分区、PV、VG、LV、文件系统和挂载点。
4. 说明临时挂载与`/etc/fstab`持久挂载的区别。
5. 说明扩展逻辑卷和扩展文件系统是两个层次的操作。

### 2. 能力目标

1. 使用`uptime`、`top`、`ps`和`free`检查系统资源。
2. 安全识别空白磁盘，创建GPT分区和XFS文件系统。
3. 使用`mount`、`umount`和UUID完成临时与持久挂载。
4. 使用`pvcreate`、`vgcreate`、`lvcreate`创建LVM存储。
5. 使用`lvextend`和`xfs_growfs`完成在线扩容。
6. 使用`lsblk`、`findmnt`、`df`、`pvs`、`vgs`和`lvs`形成验证证据。

### 3. 素质目标

1. 在任何格式化命令前确认设备身份和数据风险。
2. 修改`fstab`前备份，并在重启前使用`findmnt --verify`和`mount -a`验证。
3. 不凭单个资源数值草率判断系统故障。
4. 先定位进程和影响范围，再采取终止操作。

## 三、安全规则

1. 本实验只能操作教师为`rocky-server`新增的8GiB空白盘。
2. 课程标准设备名为`/dev/sdb`。如果实际名称不同，停止实验，由教师确认后再调整命令。
3. 禁止对包含根文件系统的磁盘执行`mklabel`、`mkfs`或`pvcreate`。
4. 禁止把`/dev/sda`、`/dev/nvme0n1`等系统盘照抄成实验目标。
5. `fstab`验证失败时禁止重启。
6. 本实验不进行XFS缩容、LVM缩容、RAID、LUKS或磁盘写满测试。

## 四、实验环境

- Rocky Linux 9，使用`rocky-server`。
- VMware中为`rocky-server`增加一块8GiB空白虚拟磁盘。
- 在增加磁盘后、开始分区前建立实验快照。
- 使用XFS、GPT和LVM2。
- 异常进程只使用`yes > /dev/null`，实验后必须终止。

确认项目目录存在：

```bash
test -d "$HOME/m1-project"
```

命令安静返回才继续。创建证据目录：

```bash
mkdir -p "$HOME/m1-project/evidence"
```

安装本实验工具：

```bash
sudo dnf install -y parted lvm2 xfsprogs
```

## 五、项目任务

1. 记录服务器运行时间、负载、CPU、内存和进程基线。
2. 安全识别新增空白盘，不触碰系统盘。
3. 创建普通XFS分区并完成UUID持久挂载。
4. 创建PV、VG、LV和XFS文件系统并持久挂载。
5. 把逻辑卷和XFS从2GiB扩展到3GiB并验证数据。
6. 重启验证两个挂载点及测试文件。
7. 制造、定位并终止一个CPU异常进程。
8. 形成服务器资源与存储巡检报告。

## 六、实验步骤

### 任务一：采集CPU、负载、内存和进程基线

```bash
uptime
```

```bash
nproc
```

```bash
free -h
```

```bash
ps -eo pid,ppid,user,stat,%cpu,%mem,comm --sort=-%cpu | head -10
```

```bash
ps -eo pid,ppid,user,stat,%cpu,%mem,comm --sort=-%mem | head -10
```

启动`top`：

```bash
top
```

在`top`中按`1`查看每个CPU，按`P`按CPU排序，按`M`按内存排序，按`q`退出。

> **验收点**：记录CPU数量、1/5/15分钟负载、内存total/available和当前资源占用较高的进程。

### 任务二：识别系统盘和空白实验盘

列出整块磁盘：

```bash
lsblk -dpno NAME,SIZE,TYPE,MODEL
```

查看包含文件系统和挂载点的完整关系：

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,UUID,MOUNTPOINTS
```

确认根文件系统来源：

```bash
findmnt -no SOURCE /
```

只读检查课程实验盘签名：

```bash
sudo wipefs -n /dev/sdb
```

只读查看分区表：

```bash
sudo parted /dev/sdb print
```

空白盘可能提示无法识别磁盘标签，这是尚未创建分区表的正常现象。如果`/dev/sdb`已挂载、存在文件系统签名、包含分区数据、容量不是8GiB，或者根文件系统位于该磁盘，停止实验。

把安全确认结果写入证据文件：

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,UUID,MOUNTPOINTS | tee ~/m1-project/evidence/lab07-before-storage.txt
```

> **验收点**：能够明确指出系统盘和实验盘，并由教师检查`lab07-before-storage.txt`后再继续。

### 任务三：创建普通分区和持久挂载

#### 步骤1：建立GPT分区

下面命令只允许在确认无数据的`/dev/sdb`执行：

```bash
sudo parted -s /dev/sdb mklabel gpt
```

创建约2GiB普通分区：

```bash
sudo parted -s /dev/sdb mkpart data xfs 1MiB 2049MiB
```

创建占用剩余空间的LVM分区：

```bash
sudo parted -s /dev/sdb mkpart lvm 2049MiB 100%
```

设置LVM标志：

```bash
sudo parted -s /dev/sdb set 2 lvm on
```

让内核重新读取：

```bash
sudo partprobe /dev/sdb
```

```bash
sudo udevadm settle
```

查看结果：

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS /dev/sdb
```

> **验收点**：看到`sdb1`和`sdb2`，且没有修改系统盘分区。

#### 步骤2：创建XFS并临时挂载

```bash
sudo mkfs.xfs -L DATA /dev/sdb1
```

```bash
sudo mkdir -p /data
```

```bash
sudo mount /dev/sdb1 /data
```

```bash
findmnt /data
```

```bash
df -hT /data
```

写入可持续验证的文件：

```bash
echo 'ordinary mount works' | sudo tee /data/mount-test.txt
```

```bash
cat /data/mount-test.txt
```

#### 步骤3：配置UUID持久挂载

备份原配置：

```bash
sudo cp -a /etc/fstab /etc/fstab.before-lab07
```

确认当前没有本实验残留条目：

```bash
grep -nE '[[:space:]]/data[[:space:]]|[[:space:]]/srv/appdata[[:space:]]' /etc/fstab
```

首次实验预期没有输出。有输出时停止并确认是否来自本实验上次执行，不能继续追加重复条目。

读取实际UUID：

```bash
sudo blkid /dev/sdb1
```

编辑配置：

```bash
sudo vim /etc/fstab
```

把`实际UUID`替换为上一条命令显示的值：

```text
UUID=实际UUID  /data  xfs  defaults  0  0
```

离开挂载点后卸载：

```bash
cd ~
```

```bash
sudo umount /data
```

先检查配置：

```bash
sudo findmnt --verify --verbose
```

再按`fstab`执行挂载：

```bash
sudo mount -a
```

```bash
findmnt /data
```

```bash
cat /data/mount-test.txt
```

> **验收点**：`findmnt --verify`无错误，`/data`按UUID挂载，测试文件仍可读取。

### 任务四：创建和扩展LVM逻辑卷

#### 步骤4：创建PV、VG和LV

```bash
sudo pvcreate /dev/sdb2
```

```bash
sudo vgcreate vg_data /dev/sdb2
```

```bash
sudo vgs
```

创建2GiB逻辑卷：

```bash
sudo lvcreate -L 2G -n lv_app vg_data
```

逐层核对：

```bash
sudo pvs
```

```bash
sudo vgs
```

```bash
sudo lvs -o lv_name,vg_name,lv_size,devices
```

#### 步骤5：创建并挂载逻辑卷文件系统

```bash
sudo mkfs.xfs -L APPDATA /dev/vg_data/lv_app
```

```bash
sudo mkdir -p /srv/appdata
```

```bash
sudo mount /dev/vg_data/lv_app /srv/appdata
```

```bash
echo 'lvm mount works' | sudo tee /srv/appdata/lvm-test.txt
```

```bash
sudo blkid /dev/vg_data/lv_app
```

编辑`fstab`：

```bash
sudo vim /etc/fstab
```

使用逻辑卷文件系统的实际UUID增加：

```text
UUID=逻辑卷文件系统的实际UUID  /srv/appdata  xfs  defaults  0  0
```

验证：

```bash
sudo findmnt --verify --verbose
```

```bash
sudo mount -a
```

```bash
findmnt /srv/appdata
```

> **验收点**：能说明`/dev/sdb2 → PV → vg_data → lv_app → XFS → /srv/appdata`的完整关系。

#### 步骤6：从2GiB扩展到3GiB

扩容前记录：

```bash
sudo lvs /dev/vg_data/lv_app
```

```bash
df -hT /srv/appdata
```

扩展逻辑卷：

```bash
sudo lvextend -L +1G /dev/vg_data/lv_app
```

再次执行`df`，观察文件系统容量不会自动随所有环境立即变化：

```bash
df -hT /srv/appdata
```

在线扩展XFS：

```bash
sudo xfs_growfs /srv/appdata
```

最终核对：

```bash
sudo lvs /dev/vg_data/lv_app
```

```bash
df -hT /srv/appdata
```

```bash
cat /srv/appdata/lvm-test.txt
```

> **验收点**：LV和XFS均接近3GiB，原测试文件仍可读取，并能解释两次扩容命令分别修改哪一层。

### 任务五：重启验证持久挂载

重启前最后检查：

```bash
sudo findmnt --verify --verbose
```

```bash
sudo mount -a
```

两条命令无错误后重启：

```bash
sudo reboot
```

重新登录`rocky-server`，验证两个挂载点：

```bash
findmnt /data
```

```bash
findmnt /srv/appdata
```

```bash
cat /data/mount-test.txt
```

```bash
cat /srv/appdata/lvm-test.txt
```

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,UUID,MOUNTPOINTS
```

> **验收点**：重启后两个挂载点自动恢复，两个测试文件均存在。

### 任务六：制造和定位CPU异常

启动受控进程：

```bash
yes > /dev/null &
```

保存最新`yes`进程PID：

```bash
pgrep -n -x yes | tee ~/m1-project/evidence/lab07-cpu.pid
```

查看资源占用：

```bash
ps -p "$(cat ~/m1-project/evidence/lab07-cpu.pid)" -o pid,ppid,user,stat,%cpu,%mem,etime,cmd
```

```bash
top -b -n 1 -p "$(cat ~/m1-project/evidence/lab07-cpu.pid)" | tail -5
```

核对命令名：

```bash
ps -p "$(cat ~/m1-project/evidence/lab07-cpu.pid)" -o comm= | grep -qx 'yes'
```

上一条安静返回时，终止该PID：

```bash
kill "$(cat ~/m1-project/evidence/lab07-cpu.pid)"
```

复查：

```bash
ps -p "$(cat ~/m1-project/evidence/lab07-cpu.pid)" -o pid,stat,cmd
```

复查预期只显示表头或提示进程不存在。普通`kill`发送TERM；只有确认程序无法响应时才考虑KILL信号。

> **验收点**：异常进程已经不存在，能够解释单线程接近100%不等于占满整台多核机器。

### 任务七：生成系统与存储巡检报告

创建报告：

```bash
date -Iseconds > ~/m1-project/evidence/lab07-health-report.txt
```

逐项追加：

```bash
hostname >> ~/m1-project/evidence/lab07-health-report.txt
```

```bash
uptime >> ~/m1-project/evidence/lab07-health-report.txt
```

```bash
nproc >> ~/m1-project/evidence/lab07-health-report.txt
```

```bash
free -h >> ~/m1-project/evidence/lab07-health-report.txt
```

```bash
ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu | head -10 >> ~/m1-project/evidence/lab07-health-report.txt
```

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,UUID,MOUNTPOINTS >> ~/m1-project/evidence/lab07-health-report.txt
```

```bash
sudo pvs >> ~/m1-project/evidence/lab07-health-report.txt
```

```bash
sudo vgs >> ~/m1-project/evidence/lab07-health-report.txt
```

```bash
sudo lvs -o lv_name,vg_name,lv_size,devices >> ~/m1-project/evidence/lab07-health-report.txt
```

```bash
findmnt /data >> ~/m1-project/evidence/lab07-health-report.txt
```

```bash
findmnt /srv/appdata >> ~/m1-project/evidence/lab07-health-report.txt
```

```bash
df -hT >> ~/m1-project/evidence/lab07-health-report.txt
```

```bash
df -i >> ~/m1-project/evidence/lab07-health-report.txt
```

```bash
systemctl --failed --no-pager >> ~/m1-project/evidence/lab07-health-report.txt
```

查看报告：

```bash
less ~/m1-project/evidence/lab07-health-report.txt
```

使用Vim在报告末尾补充以下结论：

1. 当前CPU、负载和内存是否存在明显风险及依据。
2. 根文件系统空间和inode是否存在风险及依据。
3. `/data`和`/srv/appdata`分别来自什么设备和存储层次。
4. LV和XFS扩容前后容量如何变化。
5. 为什么当前两个挂载点能够在重启后自动恢复。

## 七、独立实践

不再创建新磁盘或新逻辑卷，使用已经完成的环境独立回答：

1. 只使用`lsblk`、`pvs`、`vgs`、`lvs`和`findmnt`，画出`/srv/appdata`的存储链。
2. 找出`/var`下一层目录中占用空间最大的5项。
3. 检查根文件系统空间和inode，分别设定课堂告警阈值。
4. 说明为什么`lvs`显示3GiB而`df`仍显示2GiB时，不能再次盲目执行`lvextend`。
5. 说明错误`fstab`条目为什么必须在重启前发现。

## 八、验收标准

- [ ] 能明确区分系统盘与空白实验盘。
- [ ] `/dev/sdb1`为XFS并按UUID持久挂载到`/data`。
- [ ] 能说明PV、VG、LV、文件系统和挂载点的关系。
- [ ] `vg_data/lv_app`已创建并挂载到`/srv/appdata`。
- [ ] LV和XFS均已从2GiB扩展到3GiB。
- [ ] 重启后两个挂载点和测试文件仍然存在。
- [ ] `/etc/fstab`已经备份且验证无错误。
- [ ] 能正确解读负载、内存available、空间和inode。
- [ ] 已定位并终止实验CPU进程，没有残留。
- [ ] 巡检报告包含资源、存储层次、容量变化和判断依据。

## 九、成果提交

1. `evidence/lab07-before-storage.txt`。
2. `evidence/lab07-health-report.txt`。
3. `lsblk -f`及`findmnt /data`、`findmnt /srv/appdata`结果。
4. `pvs`、`vgs`、`lvs -o lv_name,vg_name,lv_size,devices`结果。
5. 扩容前后的`lvs`和`df -hT /srv/appdata`结果。
6. 重启后的挂载和测试文件验证。
7. CPU异常的PID、资源占用和终止验证。

## 十、常见问题

### Q1：找不到/dev/sdb

不要把其他设备名直接替换进去。关机后检查VMware是否确实为`rocky-server`增加了独立虚拟磁盘，再由教师核对`lsblk`结果。

### Q2：parted提示设备忙

停止操作并检查`lsblk`和`findmnt`。设备可能已经挂载或不是空白盘，不能使用强制覆盖解决。

### Q3：umount提示target is busy

确认当前终端不在挂载目录：

```bash
pwd
```

使用下面的命令检查占用者：

```bash
sudo fuser -vm /data
```

不要直接使用懒卸载掩盖仍在访问的数据。

### Q4：mount -a报告UUID不存在

使用`blkid`重新读取UUID，检查是否抄错、是否把普通分区UUID和逻辑卷UUID混淆。修正后重新执行`findmnt --verify --verbose`和`mount -a`。

### Q5：fstab修改后系统可能无法正常启动

实验要求重启前完成验证。若尚未重启且无法修正，可恢复备份：

```bash
sudo cp -a /etc/fstab.before-lab07 /etc/fstab
```

恢复后再次验证，不带错误配置重启。

### Q6：lvextend成功但df容量没有变化

`lvextend`只扩大LV，XFS还需要对已挂载的挂载点执行`xfs_growfs /srv/appdata`。

### Q7：能否缩小XFS

不能直接缩小。本课程不进行文件系统或LV缩容操作。

## 十一、环境保留与清理

检查CPU实验进程：

```bash
pgrep -a -x yes
```

若存在本实验创建的`yes`进程，只终止对应PID。

保留`/data`、`/srv/appdata`、`vg_data/lv_app`、测试文件、`fstab`配置和巡检报告。实验验收后建立`Linux-L1`检查点，供网络实验和后续《虚拟化容器技术》继续使用。不要在VMware中移除仍被`fstab`引用的虚拟磁盘。

---
