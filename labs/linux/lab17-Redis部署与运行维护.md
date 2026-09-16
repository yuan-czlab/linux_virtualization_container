# 实验17：Redis缓存服务部署与运行维护

> 所属模块：模块三 企业服务器部署与综合运维
> 建议学时：2学时
> 实验方式：个人
> 对应教材：3.4 Redis缓存服务
> 知识前置：已学习教材3.4，理解systemd、监听地址、端口、认证与持久化基础
> 状态依赖：`rocky-server`可以使用课程软件源；不依赖实验16的MongoDB账号和数据
> 实验主机：`rocky-server`
> 辅助验证主机：`ubuntu-client`
> 建议起点：`Linux-L2`或已经连续完成实验14—16的环境
> 项目成果：本机Redis缓存、认证、业务键、TTL、RDB验证、故障记录和验收证据

## 一、项目情境

TechCorp巡检平台需要缓存网站访问次数、服务器状态和临时验证码。应用与Redis部署在同一台`rocky-server`上，外部主机没有直接访问Redis的业务需求。

你需要交付一个满足以下条件的缓存服务：

- Redis由systemd管理并随系统启动；
- 只监听`127.0.0.1`和IPv6回环地址；
- 未认证会话不能读取数据；
- 可以完成状态、计数、对象和TTL操作；
- RDB后台保存成功，服务重启后关键数据仍存在；
- 能根据拒绝连接、`NOAUTH`和`WRONGPASS`判断故障层次；
- 提交材料中不出现实际密码。

## 二、实验目标

### 1. 知识目标

1. 说明Redis服务端、客户端、6379端口和键值模型。
2. 说明`bind`、保护模式和认证各自的作用。
3. 区分RDB与AOF的基本原理。
4. 说明TTL与缓存数据生命周期的关系。

### 2. 能力目标

1. 安装Redis并使用systemd管理服务。
2. 使用`redis-cli`逐条完成数据读写。
3. 配置本机监听和基础认证。
4. 验证RDB状态和重启后的数据恢复。
5. 使用状态、端口、客户端返回和journal排查故障。

### 3. 安全与规范目标

1. 不向校园网或互联网开放6379端口。
2. 不把密码写入Shell命令、脚本、截图和Git仓库。
3. 不执行`FLUSHDB`、`FLUSHALL`和不受控制的批量删除。
4. 配置变更前创建可识别的备份，变更后完成闭环验证。

## 三、环境与前置检查

本实验不依赖实验16的MongoDB数据，但会继续使用`~/m1-project`保存交付证据。实验结束后保留Redis，供实验19巡检和实验20综合验收使用。

### 步骤1：确认当前主机

```bash
hostnamectl --static
```

预期结果为`rocky-server`。如果不是，切换到正确虚拟机后再继续。

### 步骤2：确认操作系统

```bash
cat /etc/os-release
```

预期为Rocky Linux 9。

### 步骤3：确认课程项目目录

```bash
ls -ld ~/m1-project
```

如果提示目录不存在，创建项目目录：

```bash
mkdir -p ~/m1-project
```

创建证据目录：

```bash
mkdir -p ~/m1-project/evidence
```

创建Redis备份目录：

```bash
mkdir -p ~/m1-project/backup/redis
```

### 步骤4：检查旧服务与端口占用

```bash
rpm -q redis
```

未安装时出现`package redis is not installed`是正常基线，不是实验失败。

```bash
sudo ss -lntp | grep ':6379'
```

未安装或未启动Redis时没有输出是正常结果。如果已经有进程占用6379，应记录进程名称，不要直接覆盖已有服务。

## 四、任务一：安装并启动Redis

### 步骤1：查看可用软件包来源

```bash
sudo dnf repolist
```

实验应使用已经由教师验证的课程镜像源、阿里源、清华源或完整离线包。不要在同一台主机混装来自不同来源的Redis包。

### 步骤2：查看软件包信息

```bash
sudo dnf info redis
```

如果找不到软件包，停止安装，检查课程软件源，不要随意下载不明RPM。

### 步骤3：安装Redis

```bash
sudo dnf install -y redis
```

### 步骤4：确认已安装版本

```bash
rpm -q redis
```

### 步骤5：确认服务端和客户端版本

```bash
redis-server --version
```

```bash
redis-cli --version
```

### 步骤6：定位配置文件

```bash
rpm -ql redis | grep '/redis\.conf$'
```

官方RPM通常使用`/etc/redis/redis.conf`。如果实际路径不同，后续命令应使用屏幕上显示的真实路径，不能凭空创建另一个配置文件。

### 步骤7：启动服务并设置开机启动

```bash
sudo systemctl enable --now redis
```

### 步骤8：验证服务状态

```bash
systemctl is-active redis
```

预期返回`active`。

```bash
systemctl is-enabled redis
```

预期返回`enabled`。

### 步骤9：查看初始监听

```bash
sudo ss -lntp | grep ':6379'
```

记录本地地址。最终必须限制为回环地址。

## 五、任务二：备份并配置安全基线

### 步骤1：确认主配置存在

```bash
sudo test -f /etc/redis/redis.conf
```

返回码为0且没有输出表示文件存在。如实际软件包使用其他路径，应将本实验后续路径统一替换为真实路径。

### 步骤2：检查是否已有实验备份

```bash
ls -l ~/m1-project/backup/redis/redis.conf.before-auth
```

如果提示不存在，执行下一步；如果已经存在，不要覆盖它。

### 步骤3：首次创建配置备份

```bash
sudo cp -p /etc/redis/redis.conf ~/m1-project/backup/redis/redis.conf.before-auth
```

### 步骤4：查看备份

```bash
ls -l ~/m1-project/backup/redis/redis.conf.before-auth
```

### 步骤5：查看修改前的关键配置

```bash
sudo grep -nE '^(bind|protected-mode|port|save|appendonly|maxmemory|maxmemory-policy)' /etc/redis/redis.conf
```

此命令故意不显示`requirepass`，避免密码进入终端截图。

### 步骤6：编辑配置

```bash
sudo vim /etc/redis/redis.conf
```

在vim中找到并确认以下设置。密码由学习者在实验现场自行设置，不要把下面的占位符原样写入配置。

```text
bind 127.0.0.1 -::1
protected-mode yes
port 6379
requirepass <自行设置的长密码>
```

修改时注意：

- 只保留一条生效的`bind`；
- 只保留一条生效的`protected-mode`；
- 取消目标`requirepass`行前的注释符，并替换占位内容；
- 不关闭保护模式；
- 不把监听地址改为`0.0.0.0`；
- 不修改MySQL、MongoDB或Nginx配置。

### 步骤7：检查是否误用了Tab

```bash
sudo grep -n $'\t' /etc/redis/redis.conf
```

没有输出表示未发现Tab字符。Redis配置不是YAML，但使用清晰一致的空格仍有利于检查。

### 步骤8：检查关键配置，但隐藏密码

```bash
sudo grep -nE '^(bind|protected-mode|port|save|appendonly|maxmemory|maxmemory-policy)' /etc/redis/redis.conf
```

### 步骤9：重启Redis

```bash
sudo systemctl restart redis
```

### 步骤10：检查服务状态

```bash
systemctl is-active redis
```

如果不是`active`，不要反复重启，立即查看日志：

```bash
sudo journalctl -u redis -b -n 80 --no-pager
```

### 步骤11：确认监听范围

```bash
sudo ss -lntp | grep ':6379'
```

只应看到`127.0.0.1:6379`和可能存在的`[::1]:6379`，不应看到`0.0.0.0:6379`或服务器业务IP上的6379。

## 六、任务三：验证未认证与认证行为

### 步骤1：进入客户端

```bash
redis-cli
```

### 步骤2：未认证执行PING

```text
PING
```

预期得到：

```text
NOAUTH Authentication required.
```

这证明连接已经到达Redis，认证机制正在阻止未认证命令。

### 步骤3：交互认证

```text
AUTH <刚才设置的密码>
```

预期返回`OK`。密码只在交互式客户端中输入，不要截取包含密码的输入画面。

### 步骤4：再次执行PING

```text
PING
```

预期返回`PONG`。

### 步骤5：查看当前ACL身份

```text
ACL WHOAMI
```

使用`requirepass`完成基础认证时，通常返回`default`。

### 步骤6：退出客户端

```text
EXIT
```

## 七、任务四：创建巡检平台业务数据

再次进入客户端：

```bash
redis-cli
```

先交互认证：

```text
AUTH <实验密码>
```

以下命令必须逐条输入。每执行一条，先观察返回值，再继续下一条。

### 步骤1：创建服务状态

```text
SET service:nginx:status active
```

### 步骤2：创建数据库状态

```text
SET service:mysql:status active
```

### 步骤3：创建MongoDB状态

```text
SET service:mongodb:status active
```

### 步骤4：创建访问计数

```text
SET website:visitors 0
```

### 步骤5：将计数增加一次

```text
INCR website:visitors
```

### 步骤6：再次增加计数

```text
INCR website:visitors
```

### 步骤7：读取计数

```text
GET website:visitors
```

预期返回`2`。

### 步骤8：创建服务器对象

```text
HSET server:rocky-server ip 192.168.10.10 role database status active
```

如果课程三机规划使用其他地址，将IP替换为`rocky-server`的真实固定地址。

### 步骤9：读取服务器对象

```text
HGETALL server:rocky-server
```

### 步骤10：创建120秒临时键

```text
SET verification:code 482916 EX 120
```

### 步骤11：立即查看TTL

```text
TTL verification:code
```

预期得到小于等于120的正整数。

### 步骤12：创建持久化验证键

```text
SET persistence:check course-data
```

### 步骤13：确认键类型

```text
TYPE persistence:check
```

预期返回`string`。

### 步骤14：退出客户端

```text
EXIT
```

## 八、任务五：验证RDB持久化

### 步骤1：进入客户端并认证

```bash
redis-cli
```

```text
AUTH <实验密码>
```

### 步骤2：查看持久化配置

```text
CONFIG GET save
```

```text
CONFIG GET appendonly
```

```text
CONFIG GET dir
```

```text
CONFIG GET dbfilename
```

如果课程安全策略禁用了`CONFIG`命令，则改为从`/etc/redis/redis.conf`读取相应配置。

### 步骤3：发起后台快照

```text
BGSAVE
```

预期返回`Background saving started`。如果已有后台任务，按错误提示等待并检查状态，不要连续反复执行。

### 步骤4：查看持久化状态

```text
INFO persistence
```

等待`rdb_bgsave_in_progress`回到`0`，并确认`rdb_last_bgsave_status:ok`。

### 步骤5：查看最近保存时间

```text
LASTSAVE
```

### 步骤6：退出客户端

```text
EXIT
```

### 步骤7：检查持久化文件

```bash
sudo find /var/lib/redis -maxdepth 2 -type f -ls
```

如果`CONFIG GET dir`显示的目录不是`/var/lib/redis`，应检查实际目录，不要新建一个同名空目录冒充结果。

### 步骤8：重启服务

```bash
sudo systemctl restart redis
```

### 步骤9：确认服务恢复

```bash
systemctl is-active redis
```

### 步骤10：重新进入客户端

```bash
redis-cli
```

### 步骤11：重新认证

```text
AUTH <实验密码>
```

### 步骤12：读取持久化验证键

```text
GET persistence:check
```

预期返回`course-data`。这证明最小的“写入—后台保存—重启—加载—读取”链路成功。

### 步骤13：确认访问计数也存在

```text
GET website:visitors
```

预期返回`2`。

### 步骤14：退出客户端

```text
EXIT
```

## 九、任务六：完成三类故障判断

本任务只制造可立即恢复的小故障，不修改网络配置，不删除业务数据。

### 故障一：未认证

进入客户端：

```bash
redis-cli
```

未认证读取业务键：

```text
GET website:visitors
```

记录`NOAUTH`。它表示TCP与Redis响应正常，问题位于认证层。

退出：

```text
EXIT
```

### 故障二：错误密码

进入客户端：

```bash
redis-cli
```

输入一个故意错误的密码：

```text
AUTH ThisIsAnIntentionalWrongPassword
```

记录`WRONGPASS`，随后在同一会话使用真实密码恢复认证。不要把真实密码写入报告。

```text
AUTH <实验密码>
```

确认恢复：

```text
PING
```

退出：

```text
EXIT
```

### 故障三：服务停止

停止Redis：

```bash
sudo systemctl stop redis
```

连接Redis：

```bash
redis-cli
```

此时通常出现`Connection refused`，它与`NOAUTH`不同：客户端尚未进入Redis命令与认证阶段。

重新启动服务：

```bash
sudo systemctl start redis
```

确认恢复：

```bash
systemctl is-active redis
```

检查端口恢复：

```bash
sudo ss -lntp | grep ':6379'
```

## 十、任务七：验证远程主机不能直连Redis

由于Redis只供`rocky-server`本机应用使用，`ubuntu-client`不应直接连接6379。

### 步骤1：在rocky-server确认业务IP

```bash
hostname -I
```

记录`rocky-server`在三机实验网络中的固定IP。

### 步骤2：切换到ubuntu-client测试端口

```bash
nc -vz rocky-server 6379
```

预期连接失败。该失败是安全设计的验收结果，不需要开放防火墙，也不需要把Redis改为监听`0.0.0.0`。

如果命令提示`nc: command not found`，安装Ubuntu客户端工具：

```bash
sudo apt install -y netcat-openbsd
```

安装后重新执行端口测试。

## 十一、任务八：形成不含密码的验收证据

以下步骤回到`rocky-server`执行。

### 步骤1：保存Redis版本

```bash
redis-server --version > ~/m1-project/evidence/lab17-redis-version.txt
```

### 步骤2：追加服务状态

```bash
systemctl is-active redis >> ~/m1-project/evidence/lab17-redis-version.txt
```

### 步骤3：保存监听证据

```bash
sudo ss -lntp | grep ':6379' > ~/m1-project/evidence/lab17-redis-listen.txt
```

### 步骤4：保存不含密码的配置摘要

```bash
sudo grep -nE '^(bind|protected-mode|port|save|appendonly|maxmemory|maxmemory-policy)' /etc/redis/redis.conf > ~/m1-project/evidence/lab17-redis-config.txt
```

### 步骤5：检查证据文件

```bash
ls -l ~/m1-project/evidence/lab17-redis-*.txt
```

### 步骤6：确认提交文件没有密码配置行

```bash
grep -Rni 'requirepass' ~/m1-project/evidence
```

没有输出是预期结果。如果出现匹配，删除或脱敏对应证据后重新生成。

业务键读取、TTL、`INFO persistence`、`NOAUTH`、`WRONGPASS`与远程连接失败可使用截图提交，但截图不得包含真实密码。

## 十二、实验验收

### 1. 功能验收

- [ ] `redis`服务为`active`和`enabled`。
- [ ] `PING`在认证后返回`PONG`。
- [ ] `website:visitors`最终值为`2`。
- [ ] 能使用hash读取`server:rocky-server`字段。
- [ ] 能创建并解释带TTL的临时键。

### 2. 安全验收

- [ ] 6379只监听本机回环地址。
- [ ] 未认证命令返回`NOAUTH`。
- [ ] 错误密码返回`WRONGPASS`，正确密码能够恢复访问。
- [ ] `ubuntu-client`不能直接连接`rocky-server:6379`。
- [ ] 证据、截图和Git中没有真实密码。

### 3. 持久化与排障验收

- [ ] `BGSAVE`完成且`rdb_last_bgsave_status`为`ok`。
- [ ] 能找到实际持久化文件。
- [ ] 服务重启后`persistence:check`仍可读取。
- [ ] 能说明`Connection refused`、`NOAUTH`和`WRONGPASS`所在的故障层次。
- [ ] 能使用systemd、journal和`ss`检查服务。

## 十三、提交材料

1. `lab17-redis-version.txt`；
2. `lab17-redis-listen.txt`；
3. `lab17-redis-config.txt`；
4. 业务键读写和TTL截图；
5. `INFO persistence`与重启后读取截图；
6. 三类故障现象与判断记录；
7. `ubuntu-client`远程连接失败截图；
8. 150—300字项目说明，解释为什么Redis只允许本机访问，以及RDB与备份的区别。

## 十四、常见问题

### 1. `dnf`找不到redis

检查课程软件源是否启用。使用课程统一镜像源或完整离线包，不要混装多个来源的软件包。

### 2. 配置文件不是`/etc/redis/redis.conf`

执行：

```bash
rpm -ql redis | grep '/redis\.conf$'
```

后续统一使用软件包列出的真实配置路径。

### 3. 修改配置后服务启动失败

查看本次启动日志：

```bash
sudo journalctl -u redis -b -n 80 --no-pager
```

根据第一处明确错误检查配置。必要时用`redis.conf.before-auth`恢复，再重新修改。

### 4. 连接后出现NOAUTH

连接已经到达Redis，但当前会话还没有认证。执行交互式`AUTH`，不需要修改监听或防火墙。

### 5. 正确密码仍然出现WRONGPASS

检查输入是否多了空格，配置中是否存在多条生效的`requirepass`，以及服务重启后是否加载了所编辑的配置文件。检查配置时不要将实际密码输出到报告。

### 6. 重启后键丢失

检查`INFO persistence`、RDB保存状态、数据目录、文件权限和journal。写入内存成功并不能证明后台保存成功。

### 7. ubuntu-client不能连接6379

这是本实验的预期安全结果。Redis只供`rocky-server`本机应用使用，不应为了得到“连接成功”而扩大监听范围或开放防火墙。

## 十五、独立实践

不参照实验中的具体键名，为“课程签到系统”设计以下缓存：

1. 一个累计签到人数的计数键；
2. 一个保存班级名称、课程名称和当前状态的hash；
3. 一个5分钟后自动失效的签到口令；
4. 一个保存不重复签到学号的set；
5. 一份说明每个数据类型选择理由的表格。

要求逐条执行命令，并证明临时口令的TTL随时间减少。不要执行任何全库清空命令。

## 十六、环境保留

保留以下状态供实验19和实验20使用：

- `redis`服务保持`active`和`enabled`；
- Redis只监听回环地址；
- 认证保持启用，但密码不写入项目仓库；
- 保留`service:*`、`website:visitors`和`persistence:check`等业务键；
- 保留`~/m1-project/backup/redis/redis.conf.before-auth`；
- 保留`~/m1-project/evidence/lab17-redis-*.txt`。

机房还原前，应按照课程统一方式保存实验镜像或导出所需证据。下一次课程如果从还原后的环境开始，应使用课程快照恢复，而不是假设Redis仍然存在。

## 十七、官方参考

- [Redis Open Source：Rocky Linux 8/9 RPM安装](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/rpm/)
- [Redis安全与保护模式](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)
- [Redis访问控制列表ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/)
- [Redis持久化](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Redis BGSAVE命令](https://redis.io/docs/latest/commands/bgsave/)
