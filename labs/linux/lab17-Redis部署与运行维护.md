# 实验17：Redis缓存服务部署与运行维护

> 所属模块：模块三 企业服务部署与综合运维  
> 建议学时：2学时  
> 实验方式：个人  
> 对应教材：《模块三 企业服务部署与综合运维》第28章  
> 知识前置：教材第28章以及服务、监听、认证和持久化基础\
> 状态依赖：`rocky-server`可用课程软件源；不依赖MongoDB数据和账号\
> 建议起点：`Linux-L2`或当前连续实验环境\
> 项目成果：Redis服务、基础数据读写、认证、仅本机监听、RDB/AOF检查和连接故障记录

## 一、项目情境

TechCorp应用需要使用Redis保存访问计数和临时状态。你需要安装Redis，完成PING、SET、GET和INCR验证，检查认证、监听和持久化，并避免把6379直接暴露给不可信网络。

## 二、实验目标

### 1. 知识目标

1. 说明Redis作为内存键值服务的主要用途。
2. 说明redis服务、redis-cli、6379端口、bind和认证。
3. 区分RDB快照与AOF追加日志的基本特点。

### 2. 能力目标

1. 安装并使用systemd管理Redis。
2. 使用redis-cli完成基础数据读写和计数。
3. 配置认证和仅本机监听。
4. 通过服务、端口、客户端错误和日志排查连接问题。

### 3. 素质目标

1. 不把Redis直接开放到校园网或互联网。
2. 不把密码写入命令行、脚本或Git。
3. 不在不了解影响时执行`FLUSHALL`、`FLUSHDB`等删除命令。

## 三、知识准备

```text
应用或redis-cli
→ 连接127.0.0.1:6379
→ Redis验证认证状态
→ 在内存中读写键值
→ 根据RDB或AOF策略保存持久化数据
→ 服务日志记录运行问题
```

| 方式 | 基本特点 |
|---|---|
| RDB | 在特定条件下生成某一时刻的数据快照，文件紧凑 |
| AOF | 记录写命令，通常可提供更细的恢复点，但文件和写入开销更大 |

本课程只要求识别和验证基础配置，不展开复制、哨兵和集群。

## 四、实验环境

- `rocky-server`运行Rocky Linux 9；Redis只安装在该机。
- `ubuntu-client`承担端口、认证和远程访问验证。
- 使用教师验证的软件源。优先使用课程统一版本，避免同时混装Rocky原生包和Redis官方包。
- 服务名通常为`redis`，配置通常为`/etc/redis/redis.conf`，以`rpm -ql redis`实际结果为准。

## 五、项目任务

1. 检查旧安装和6379端口。
2. 安装、启动并检查Redis。
3. 完成基础键值和计数操作。
4. 备份并配置认证与仅本机监听。
5. 检查RDB和AOF设置，执行受控持久化验证。
6. 完成一次未认证或密码错误故障排查。

## 六、实验步骤

### 任务一：安装和基线

```bash
test "$(whoami)" = 'rocky-server' && echo USER_PASS || echo USER_FAIL
test "$(hostnamectl --static)" = 'rocky-server' && echo HOST_PASS || echo HOST_FAIL
```

```bash
mkdir -p ~/m1-project/evidence ~/m1-project/backup/redis
{
    rpm -q redis || true
    sudo ss -lntp | grep ':6379' || true
} | tee ~/m1-project/evidence/lab17-redis-before.txt
sudo dnf install -y redis
rpm -q redis
rpm -ql redis | grep -E '/redis\.conf$|systemd.*redis|/redis-server$|/redis-cli$'
sudo systemctl enable --now redis
systemctl is-active redis
systemctl is-enabled redis
sudo ss -lntp | grep ':6379'
```

> **验收点**：Redis已安装，服务为active和enabled，记录实际配置路径和监听地址。

### 任务二：基础数据验证

```bash
redis-cli
```

在客户端中：

```text
PING
SET company TechCorp
GET company
SET visitors 0
INCR visitors
INCR visitors
GET visitors
TYPE visitors
INFO server
EXIT
```

预期PING返回PONG，company返回TechCorp，visitors返回2。

> **验收点**：PING、SET、GET和INCR结果正确。

### 任务三：配置认证和监听

#### 步骤1：定位并备份配置

```bash
REDIS_CONF=$(rpm -ql redis | grep '/redis.conf$' | head -1)
printf 'redis_conf=%s\n' "$REDIS_CONF"
test -f ~/m1-project/backup/redis/redis.conf.before-auth || \
  sudo cp -p "$REDIS_CONF" ~/m1-project/backup/redis/redis.conf.before-auth
sudo grep -nE '^(bind|protected-mode|port|requirepass|save|appendonly|dir|dbfilename)' "$REDIS_CONF" | sed -n '1,100p'
```

如果变量为空，停止并根据`rpm -ql redis`查找实际配置。

#### 步骤2：编辑配置

```bash
REDIS_CONF=$(rpm -ql redis | grep '/redis.conf$' | head -1)
test -n "$REDIS_CONF"
sudo vim "$REDIS_CONF"
```

确认：

```text
bind 127.0.0.1 -::1
protected-mode yes
port 6379
requirepass <教师指定的Redis实验密码>
```

只保留一条有效`requirepass`。不要把实际密码复制进实验报告。

#### 步骤3：重启和检查

```bash
sudo systemctl restart redis
systemctl is-active redis
sudo ss -lntp | grep ':6379'
sudo journalctl -u redis -n 30 --no-pager
```

最终监听应限于回环地址。

### 任务四：验证认证

未认证测试：

```bash
redis-cli
```

```text
GET company
```

预期返回NOAUTH。然后执行：

```text
AUTH <教师指定的Redis实验密码>
PING
GET company
ACL WHOAMI
EXIT
```

密码只在交互式客户端输入。不要使用包含明文密码的`redis://` URI或把`-a 密码`写入报告。

> **验收点**：未认证读取被拒绝，认证后PING和GET成功。

### 任务五：持久化检查

```bash
REDIS_CONF=$(rpm -ql redis | grep '/redis.conf$' | head -1)
test -n "$REDIS_CONF"
sudo grep -nE '^(save|appendonly|appendfilename|dir|dbfilename)' "$REDIS_CONF" | sed -n '1,100p'
```

认证进入redis-cli：

```text
AUTH <实验密码>
SET persistent_key course-data
SAVE
LASTSAVE
EXIT
```

取得目录和文件名时可在认证客户端执行：

```text
CONFIG GET dir
CONFIG GET dbfilename
CONFIG GET appendonly
```

如果课程安全配置禁止`CONFIG`命令，则从配置文件读取。检查RDB文件：

```bash
sudo find /var/lib/redis -maxdepth 2 -type f -ls 2>/dev/null || true
```

重启服务后认证查询：

```bash
sudo systemctl restart redis
redis-cli
```

```text
AUTH <实验密码>
GET persistent_key
EXIT
```

> **验收点**：能够指出当前RDB/AOF配置，重启后`persistent_key`仍可读取。

### 任务六：故障排查和证据

使用错误密码执行AUTH，记录错误；再使用正确密码恢复。检查：

```bash
REDIS_CONF=$(rpm -ql redis | grep '/redis.conf$' | head -1)
test -n "$REDIS_CONF"
systemctl status redis --no-pager
sudo ss -lntp | grep ':6379'
sudo journalctl -u redis -n 50 --no-pager
sudo grep -nE '^(bind|protected-mode|port|requirepass|save|appendonly)' "$REDIS_CONF"
```

保存不含密码的证据：

```bash
REDIS_CONF=$(rpm -ql redis | grep '/redis.conf$' | head -1)
test -n "$REDIS_CONF"
{
    redis-server --version
    systemctl is-active redis
    systemctl is-enabled redis
    sudo ss -lntp | grep ':6379'
    sudo grep -nE '^(bind|protected-mode|port|save|appendonly)' "$REDIS_CONF"
} > ~/m1-project/evidence/lab17-redis-final.txt
```

## 七、独立实践

1. 创建`service:nginx`、`service:mysql`和`service:mongodb`三个键。
2. 使用一个计数键记录巡检次数。
3. 执行一次受控SAVE并重启服务。
4. 证明重启后键仍存在。
5. 写出错误密码和服务停止两种故障的检查差异。

## 八、验收标准

- [ ] Redis服务为active和enabled。
- [ ] 6379只监听本机回环地址。
- [ ] PING、SET、GET和INCR结果正确。
- [ ] 未认证操作被拒绝，正确认证后成功。
- [ ] 配置保持protected-mode并使用实验认证。
- [ ] 能指出RDB与AOF当前设置。
- [ ] 重启后持久化测试键仍可读取。
- [ ] 已完成错误密码故障记录。
- [ ] 提交材料中没有Redis密码。

## 九、成果提交

1. `lab17-redis-before.txt`和`lab17-redis-final.txt`。
2. Redis版本、服务、端口和配置路径。
3. 基础数据操作结果。
4. 未认证与认证结果对比。
5. 持久化配置和重启验证。
6. 故障记录和独立实践。

## 十、常见问题

### Q1：配置文件路径与手册不同

使用`rpm -ql redis`定位当前软件包安装的配置，不要在多个猜测路径同时修改。

### Q2：重启后服务失败

检查配置字段、重复指令、权限和journal：

```bash
sudo journalctl -u redis -n 80 --no-pager
```

必要时从备份恢复，再重新正确配置认证。

### Q3：NOAUTH Authentication required

网络连接已经到达Redis，但当前会话尚未认证。使用AUTH和正确实验密码，不需要修改防火墙。

### Q4：数据重启后丢失

检查SAVE是否成功、RDB/AOF配置、数据目录权限和服务日志。内存写入成功不等于持久化已经完成。

## 十一、课后思考与拓展

1. Redis为什么比普通Web端口更不应该直接公网开放？
2. RDB和AOF在恢复点、文件大小和写入开销上有哪些基本差异？
3. 只有密码、但监听所有地址并向全网开放6379，为什么仍然不安全？

## 十二、环境保留

保留Redis认证、仅本机监听、测试数据和持久化配置供实验20使用。不得执行`FLUSHALL`或删除持久化文件。

## 十三、官方参考

- [Redis：在Rocky Linux 8/9使用RPM安装](https://redis.io/docs/latest/operate/oss_and_stack/install/install-stack/rpm/)
