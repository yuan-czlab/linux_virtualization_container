# 实验6：systemd服务与journal日志管理

> 所属模块：模块一 Linux基础运维  
> 建议学时：2学时  
> 实验方式：个人  
> 对应教材：《模块一 Linux基础运维》第11章  
> 知识前置：实验5中的软件安装与文件来源；教材第11章的服务和日志
> 状态依赖：用户名和主机名均为`rocky-server`；实验目录和Unit由本实验创建
> 建议起点：`Linux-L0`或当前连续实验环境
> 项目成果：服务生命周期管理记录和一次启动故障的日志证据链

## 一、项目情境

服务器上的应用通常以后台服务运行。你需要区分“服务正在运行”和“服务开机自启”，并使用systemd状态和journal日志定位一次人为制造的启动失败。

## 二、实验目标

### 1. 知识目标

1. 说明进程、服务、Unit、systemd和PID 1的关系。
2. 区分active、inactive、failed，以及enabled和disabled。
3. 说明配置检查、服务重载、重启和日志验证的基本顺序。

### 2. 能力目标

1. 使用`systemctl`查看、启停、重启、重载和设置自启。
2. 使用`journalctl`按服务、时间和级别查询日志。
3. 创建简单自定义服务并定位启动失败原因。

### 3. 素质目标

1. 不把反复重启当作排障方法。
2. 修改服务配置前保留备份，修复后完成状态和功能复测。
3. 根据证据解释故障根因。

## 三、知识准备

```text
systemd作为PID 1
→ 读取Unit及依赖
→ 创建和监督服务进程
→ 记录状态与退出结果
→ journal保存服务输出和系统日志
```

| 状态 | 含义 |
|---|---|
| active | 当前正在运行或任务成功完成 |
| inactive | 当前没有运行 |
| failed | 启动或运行发生失败 |
| enabled | 已配置为随目标启动 |
| disabled | 未配置自动启动 |

enabled不代表当前一定运行，active也不代表一定开机自启。

开始任务前打开[systemd服务状态、依赖与journal排障动画](../../animations/04-systemd-journal/index.html)。依次完成运行与自启、依赖与顺序、进程与信号、日志证据链四个主题；每一步先判断状态或下一条取证命令，再在`course-demo.service`中验证。

## 四、实验环境

- Rocky Linux 9，rocky-server具备sudo权限。
- 使用本实验自建的`course-demo.service`，避免破坏关键系统服务。
- 工作文件位于`~/m1-project/systemd/site`和`/etc/systemd/system/course-demo.service`。

Unit中的`ExecStart`使用课程固定路径，开始前必须确认身份：

```bash
whoami
```

```bash
hostnamectl --static
```

```bash
sudo -v
```

用户名和主机名都必须为`rocky-server`，`sudo -v`必须成功。否则停止实验并恢复正确课程环境；不能直接照抄后续Unit中的固定路径。

继续检查本实验对象是否被旧任务占用：

```bash
systemctl status course-demo.service --no-pager
```

```bash
ls -l /etc/systemd/system/course-demo.service
```

```bash
ls -ld "$HOME/m1-project/systemd/site"
```

新实验环境中应提示这些对象不存在。若存在，先确认它们是否为已经验收的实验6成果；需要从头重做时执行文末清理并恢复适当起点，不覆盖来源不明的同名Unit或目录。

## 五、项目任务

1. 检查systemd和现有服务状态。
2. 创建测试页面和能够持续运行的Unit。
3. 管理运行状态和开机自启。
4. 制造ExecStart路径错误。
5. 使用状态和日志定位、修复并验证。

## 六、实验步骤

### 任务一：检查systemd

```bash
ps -p 1 -o pid,comm,args
```

```bash
systemctl is-system-running
```

```bash
systemctl --failed
```

```bash
systemctl list-unit-files --type=service | sed -n '1,30p'
```

> **验收点**：PID 1为systemd，记录当前失败服务数量。

### 任务二：创建实验服务

#### 步骤1：准备服务内容

本实验尚未进入Shell脚本章节，因此使用Python自带的简单HTTP服务器作为systemd管理对象，不要求编写循环脚本。先创建站点目录：

```bash
mkdir -p ~/m1-project/systemd/site ~/m1-project/evidence
```

创建测试页面：

```bash
printf 'course-demo service is running\n' > ~/m1-project/systemd/site/index.html
```

确认Python解释器路径：

```bash
command -v python3
```

> **验收点**：页面文件存在，`command -v python3`输出`/usr/bin/python3`。

#### 步骤2：创建Unit

使用Vim创建Unit：

```bash
sudo vim /etc/systemd/system/course-demo.service
```

输入以下Unit正文：

```systemd
[Unit]
Description=Linux course demonstration service
After=network.target

[Service]
Type=simple
User=rocky-server
ExecStart=/usr/bin/python3 -m http.server 8088 --bind 127.0.0.1 --directory /home/rocky-server/m1-project/systemd/site
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

保存后检查Unit：

```bash
sudo systemd-analyze verify /etc/systemd/system/course-demo.service
```

检查通过后通知systemd重新读取Unit：

```bash
sudo systemctl daemon-reload
```

如果rocky-server家目录不是`/home/rocky-server`，应把`ExecStart`改成实际绝对路径。systemd的Unit中不能依赖交互式Shell的`~`展开。

### 任务三：管理服务

```bash
sudo systemctl enable --now course-demo.service
```

```bash
systemctl is-active course-demo.service
```

```bash
systemctl is-enabled course-demo.service
```

```bash
systemctl status course-demo.service --no-pager
```

访问服务以产生一条访问日志：

```bash
curl --fail http://127.0.0.1:8088/
```

```bash
journalctl -u course-demo.service -n 10 --no-pager
```

停止后比较状态：

```bash
sudo systemctl stop course-demo.service
```

```bash
systemctl is-active course-demo.service
```

```bash
systemctl is-enabled course-demo.service
```

```bash
sudo systemctl start course-demo.service
```

> **验收点**：能证明服务停止时仍可保持enabled，重新启动后恢复active。

### 任务四：制造并排查故障

#### 步骤3：备份并写入错误路径

```bash
sudo cp -p /etc/systemd/system/course-demo.service /etc/systemd/system/course-demo.service.bak
```

把正确的Python路径改成一个不存在的路径：

```bash
sudo sed -i 's#/usr/bin/python3#/usr/bin/python3-missing#' /etc/systemd/system/course-demo.service
```

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl restart course-demo.service
```

重启预期失败。依次收集证据：

```bash
systemctl status course-demo.service --no-pager
```

```bash
systemctl show course-demo.service -p ActiveState -p SubState -p Result -p ExecMainStatus
```

```bash
journalctl -u course-demo.service -n 30 --no-pager
```

不要立即恢复文件，先在记录中写明现象、关键日志、判断和根因。

> **验收点**：能够从ExecStart相关错误判断Python程序路径不存在。

#### 步骤4：恢复并复测

```bash
sudo cp -p /etc/systemd/system/course-demo.service.bak /etc/systemd/system/course-demo.service
```

```bash
sudo systemd-analyze verify /etc/systemd/system/course-demo.service
```

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl reset-failed course-demo.service
```

```bash
sudo systemctl restart course-demo.service
```

```bash
systemctl is-active course-demo.service
```

```bash
curl --fail http://127.0.0.1:8088/
```

```bash
journalctl -u course-demo.service -n 5 --no-pager
```

> **验收点**：服务恢复active；执行curl访问后，日志重新出现HTTP访问记录。

### 任务五：保存证据

```bash
systemctl is-active course-demo.service > ~/m1-project/evidence/lab06-systemd.txt
```

```bash
systemctl is-enabled course-demo.service >> ~/m1-project/evidence/lab06-systemd.txt
```

```bash
systemctl show course-demo.service -p ActiveState -p SubState -p Result >> ~/m1-project/evidence/lab06-systemd.txt
```

```bash
journalctl -u course-demo.service -n 10 --no-pager >> ~/m1-project/evidence/lab06-systemd.txt
```

## 七、独立实践（课堂余量或课后巩固）

核心服务已经完成“创建—运行—故障—日志—恢复”闭环后，再进行端口迁移练习。该任务不计入2学时课堂的基本验收：

1. 把Unit中的端口由8088改为8089。
2. 使用`systemd-analyze verify`检查Unit。
3. 只执行`daemon-reload`但不重启服务，观察旧端口是否变化。
4. 重启后分别检查8088和8089，并用日志证明新端口生效。
5. 解释为什么修改Unit后需要`daemon-reload`和服务重启两个动作。

## 八、验收标准

- [ ] 能区分active与enabled。
- [ ] 自定义Unit通过语法检查。
- [ ] 服务以rocky-server身份运行。
- [ ] 服务状态和日志能够互相印证。
- [ ] 已制造、记录并修复ExecStart路径故障。
- [ ] 修复后状态和日志均已复测。
- [ ] `lab06-systemd.txt`及核心故障证据完整；独立实践为拓展任务。

## 九、成果提交

1. `site/index.html`和`course-demo.service`。
2. 故障报告：现象、证据、判断、根因、修复和验证。
3. `lab06-systemd.txt`。
4. 独立实践记录（拓展任务完成时提交）。

## 十、常见问题

### Q1：修改Unit后状态没有变化

执行`sudo systemctl daemon-reload`，再重新启动服务。`daemon-reload`让systemd重新读取Unit，不等于重启服务。

### Q2：命令手动能运行，服务中提示找不到文件

检查绝对路径、执行权限、Unit中的用户和家目录。systemd服务环境与交互式Shell不同。

### Q3：日志中看不到新内容

确认查看的是正确Unit，扩大时间范围：

```bash
journalctl -u course-demo.service --since '-10 min' --no-pager
```

## 十一、课后思考与拓展

1. 为什么enabled服务可能处于inactive？
2. 为什么生产服务重启前通常要先检查配置？
3. `Restart=on-failure`可能掩盖哪些问题？

## 十二、环境保留与清理

教师验收后可清理：

```bash
sudo systemctl disable --now course-demo.service
```

```bash
sudo rm -f /etc/systemd/system/course-demo.service /etc/systemd/system/course-demo.service.bak
```

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl reset-failed
```

保留`~/m1-project/systemd`和证据文件。

