# 实验7：系统状态、磁盘与容量巡检

> 所属模块：模块一 Linux基础运维  
> 建议学时：2学时  
> 实验方式：个人  
> 对应教材：《模块一 Linux基础运维》第12章  
> 前置实验：实验6  
> 项目成果：CPU、负载、内存、磁盘、文件系统、进程和容量巡检表

## 一、项目情境

在把服务器交给网络和应用团队前，需要确认它没有明显资源异常。你需要从CPU、系统负载、内存、进程、块设备、文件系统空间和inode等角度建立基线，并制造一个安全、可终止的CPU异常进行定位。

## 二、实验目标

### 1. 知识目标

1. 区分CPU利用率与系统负载。
2. 说明`free`中的available与单纯free的差异。
3. 区分块设备、分区、逻辑卷、文件系统和挂载点。
4. 区分磁盘容量耗尽与inode耗尽。

### 2. 能力目标

1. 使用`uptime`、`top`、`ps`和`free`检查系统资源。
2. 使用`lsblk`、`findmnt`、`df`和`du`定位存储使用情况。
3. 根据PID识别并终止实验异常进程。
4. 形成包含结论和证据的巡检报告。

### 3. 素质目标

1. 不凭单个数值草率判断系统故障。
2. 先定位进程和影响范围，再采取终止操作。
3. 不在系统目录制造磁盘写满实验。

## 三、知识准备

| 对象 | 关键问题 | 常用命令 |
|---|---|---|
| CPU | 谁在消耗CPU | `top`、`ps` |
| 负载 | 有多少任务等待CPU或不可中断资源 | `uptime`、`top` |
| 内存 | 当前可供新程序使用多少 | `free` |
| 块设备 | 系统识别了哪些磁盘和分区 | `lsblk` |
| 挂载 | 文件系统挂载到哪里 | `findmnt` |
| 空间 | 文件系统数据块是否充足 | `df -h` |
| inode | 是否还能创建文件 | `df -i` |
| 目录 | 哪些目录占用空间 | `du` |

## 四、实验环境

- Rocky Linux 9，rocky-server登录。
- 异常进程只使用`yes > /dev/null`，实验后必须终止。
- 不创建大文件，不在根文件系统执行写满实验。

## 五、项目任务

1. 记录服务器运行时间、负载、CPU和内存。
2. 找出CPU和内存占用较高的进程。
3. 识别磁盘、文件系统和挂载关系。
4. 检查空间、inode和项目目录大小。
5. 制造并定位一个CPU异常进程。
6. 形成服务器巡检报告。

## 六、实验步骤

### 任务一：检查CPU、负载和内存

```bash
uptime
nproc
free -h
top
```

在`top`中按`1`查看每个CPU，按`P`按CPU排序，按`M`按内存排序，按`q`退出。

不要看到`free`列很小就判断内存不足。Linux会利用空闲内存缓存数据，通常更应关注`available`和是否频繁使用Swap。

> **验收点**：记录CPU数量、1/5/15分钟负载、内存total/available和Swap使用。

### 任务二：检查进程

```bash
ps -eo pid,ppid,user,stat,%cpu,%mem,comm --sort=-%cpu | head -10
ps -eo pid,ppid,user,stat,%cpu,%mem,comm --sort=-%mem | head -10
ps -ef | wc -l
```

`ps`是某一时刻的快照，`top`提供持续更新的视图。短时间采样不一定代表长期趋势。

> **验收点**：记录CPU和内存占用最高的进程，并说明它是否为异常。

### 任务三：检查存储

```bash
lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS
findmnt
df -hT
df -i
du -sh ~/m1-project
du -h --max-depth=1 ~/m1-project | sort -h
```

`df`从文件系统角度显示总量和可用量，`du`累计目录中文件占用；删除但仍被进程打开的文件等情况可能使二者暂时不同。

> **验收点**：指出根文件系统所在设备、文件系统类型、空间使用率、inode使用率和项目目录大小。

### 任务四：制造和定位CPU异常

#### 步骤1：启动受控进程

```bash
yes > /dev/null &
LAB07_PID=$!
printf 'lab07_pid=%s\n' "$LAB07_PID"
```

当前Shell变量`LAB07_PID`保存刚启动进程的PID。不要关闭终端。

#### 步骤2：收集证据

```bash
ps -p "$LAB07_PID" -o pid,ppid,user,stat,%cpu,%mem,etime,cmd
top -b -n 1 -p "$LAB07_PID" | tail -5
uptime
```

在多核系统中，一个单线程进程接近100%通常表示占满一个逻辑CPU，不等于占满整台机器全部CPU。

#### 步骤3：终止并复测

```bash
kill "$LAB07_PID"
sleep 1
ps -p "$LAB07_PID" -o pid,stat,cmd
printf 'ps_exit_code=%s\n' "$?"
```

普通`kill`发送TERM信号，让程序有机会正常退出。只有确认程序无法响应时才考虑KILL信号。

> **验收点**：异常进程已经不存在，记录终止前后证据。

### 任务五：生成巡检报告

```bash
REPORT=~/m1-project/evidence/lab07-health-report.txt
{
    printf '=== BASIC ===\n'
    date
    hostname
    uptime
    printf '\n=== CPU AND MEMORY ===\n'
    nproc
    free -h
    printf '\n=== TOP PROCESSES ===\n'
    ps -eo pid,user,%cpu,%mem,comm --sort=-%cpu | head -10
    printf '\n=== STORAGE ===\n'
    lsblk -o NAME,TYPE,SIZE,FSTYPE,MOUNTPOINTS
    df -hT
    df -i
    printf '\n=== FAILED SERVICES ===\n'
    systemctl --failed --no-pager
} > "$REPORT"
wc -l "$REPORT"
sed -n '1,120p' "$REPORT"
```

在报告末尾手工补充三条结论：当前是否存在CPU、内存或磁盘风险，判断依据是什么。

## 七、独立实践

1. 找出`/var`下一层目录中占用空间最大的5项；权限不足的错误应单独处理或使用sudo。
2. 列出运行时间最长的5个进程。
3. 检查根文件系统空间和inode，分别设定一个课堂告警阈值。
4. 用一段话解释“当前数值正常”为什么不等于“服务器长期没有问题”。

## 八、验收标准

- [ ] 能区分CPU利用率和系统负载。
- [ ] 能正确解读内存available。
- [ ] 能说明磁盘、分区、文件系统和挂载点的关系。
- [ ] 已检查空间和inode使用率。
- [ ] 已定位并终止实验CPU进程，没有残留。
- [ ] 巡检报告包含时间、主机、资源、存储、进程和失败服务。
- [ ] 报告包含基于证据的结论和独立实践。

## 九、成果提交

1. `lab07-health-report.txt`。
2. CPU异常的PID、资源占用和终止验证。
3. `/var`目录占用Top 5。
4. 空间和inode阈值说明。
5. 三条服务器健康结论。

## 十、常见问题

### Q1：free很小是不是内存不够

不一定。结合available、Swap、应用响应和一段时间趋势判断，不能只看free列。

### Q2：df和du结果为什么不同

二者统计角度不同；预留空间、文件系统元数据、挂载覆盖以及已删除但仍被打开的文件都可能造成差异。

### Q3：kill后进程还存在

确认PID没有被写错，检查进程状态。先等待或再次发送TERM，确认无法正常退出后才使用`kill -KILL <PID>`。

### Q4：关闭终端后忘记PID怎么办

使用`pgrep -a yes`查找，但先确认结果确实是本实验进程，不要按名称批量杀死共享服务器上的未知任务。

## 十一、课后思考与拓展

1. 为什么负载高不一定等于CPU利用率高？
2. 文件系统空间充足时，为什么仍可能无法创建新文件？
3. 服务器巡检为什么需要保存时间和主机名？

## 十二、环境保留与清理

确认没有遗留实验进程：

```bash
pgrep -a yes || true
```

若存在本实验创建的`yes`进程，只终止对应PID。保留巡检报告供模块验收。

