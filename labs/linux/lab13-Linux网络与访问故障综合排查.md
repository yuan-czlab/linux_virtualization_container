# 实验13：Linux网络与访问故障综合排查

> 所属模块：模块二 网络、远程管理与基础防护  
> 建议学时：4学时  
> 实验方式：个人或两人互设故障  
> 对应教材：《模块二 网络、远程管理与基础防护》第24章  
> 知识前置：实验8—12全部网络、SSH、firewalld和SELinux内容\
> 状态依赖：实验8—12形成的三机网络、SSH密钥、客户端别名和正确安全基线\
> 建议起点：实验12结束后的正常状态，并先建立可回退快照\
> 项目成果：不少于3个不同层次故障的完整证据链和模块二网络验收报告

## 一、项目情境

用户报告“服务器访问不了”。这句话可能指域名解析失败、路由错误、服务停止、端口未监听、防火墙阻断、SELinux拒绝或账号认证失败。你需要先明确影响范围，再按层检查，避免没有证据地同时修改多个配置。

## 二、实验目标

### 1. 知识目标

1. 建立“客户端—名称解析—网络—服务—监听—主机防护—应用”的排障模型。
2. 区分现象、证据、判断、根因、修复和验证。
3. 说明一次故障可能包含多个连锁原因。

### 2. 能力目标

1. 根据错误信息缩小检查范围。
2. 使用`ip`、`getent`、`curl`、`ss`、`systemctl`、firewalld和journal收集证据。
3. 在保留回退的前提下修复网络与访问故障。
4. 完成端到端复测和故障报告。

### 3. 素质目标

1. 一次只修改一个经过证据支持的对象。
2. 不用重装系统、关闭防护或扩大权限代替排障。
3. 修复后从原始客户端和原始访问方式复测。

## 三、知识准备

推荐排障顺序：

```text
1. 明确谁访问谁、使用什么名称、协议和端口
2. 检查客户端自身网络和名称解析
3. 检查服务器IP、网卡和路由
4. 检查服务状态和启动日志
5. 检查监听地址和端口
6. 检查firewalld和SELinux
7. 检查应用配置、权限和应用日志
8. 修复后按原路径端到端复测
```

故障报告不能只写“重启后好了”，至少包含：

```text
现象 → 影响范围 → 证据 → 判断 → 根因 → 修复 → 验证 → 预防
```

## 四、实验环境

- 默认故障目标为`rocky-server`，`ubuntu-client`为正式客户端；教师可把一项Web类故障安排到`rocky-web`，但必须在故障单中明确目标主机。
- SSH和firewalld保持运行，SELinux保持Enforcing。
- 教师准备3—5个故障，至少覆盖三个不同层次。
- 学生开始前保留VMware快照或可回退配置。

## 五、项目任务

1. 建立无故障环境基线。
2. 从Ubuntu验证SSH和HTTP测试服务。
3. 接收教师故障单，不直接询问根因。
4. 逐个收集证据、定位和修复。
5. 执行端到端复测，确认没有第二个故障。
6. 提交模块二验收矩阵和故障报告。

## 六、实验步骤

### 任务一：建立正常基线

启动受控HTTP服务：

```bash
mkdir -p ~/m1-project/module2-check
printf '<h1>MODULE2_OK</h1>\n' > ~/m1-project/module2-check/index.html
cd ~/m1-project/module2-check
python3 -m http.server 8080 --bind 0.0.0.0 > ~/m1-project/logs/module2-http.log 2>&1 &
MODULE2_HTTP_PID=$!
sudo firewall-cmd --add-port=8080/tcp
```

服务器基线：

```bash
{
    hostname
    ip -br address
    ip route
    nmcli connection show --active
    systemctl is-active sshd firewalld
    sudo ss -lntp | grep -E ':(22|8080)'
    firewall-cmd --list-all
    getenforce
    curl -s http://127.0.0.1:8080/
} | tee ~/m1-project/evidence/lab13-baseline.txt
```

Ubuntu客户端基线：

```bash
ip route get <ROCKY_IP>
nc -vz -w 3 <ROCKY_IP> 22
nc -vz -w 3 <ROCKY_IP> 8080
curl --fail http://<ROCKY_IP>:8080/
ssh rocky-course "hostname; uptime"
```

> **验收点**：故障注入前SSH和HTTP从客户端均可用，基线已保存。

### 任务二：填写故障受理信息

每个故障先填写：

| 项目 | 记录 |
|---|---|
| 故障编号 |  |
| 报告人或客户端 |  |
| 访问目标 |  |
| 使用名称或IP |  |
| 协议和端口 |  |
| 完整错误 |  |
| 开始时间 |  |
| 影响一个用户还是全部用户 |  |
| 最近是否有变更 |  |

没有明确访问目标时，不应立即修改服务器。

### 任务三：按层收集证据

以下是检查工具箱，不要求每个故障机械执行全部命令。根据现象选择，并把关键输出放入报告。

#### 客户端和名称解析

Ubuntu客户端：

```bash
ip -brief address
ip route
getent hosts <目标名称>
nc -vz -w 3 <目标IP> <端口>
curl -v http://<目标IP>:<端口>/
ssh -vv rocky-course
```

服务器：

```bash
getent hosts <目标名称>
cat /etc/hosts
```

#### 服务器网络

```bash
ip -br link
ip -br address
ip route
ip route get <客户端或网关IP>
nmcli device status
nmcli connection show --active
```

#### 服务和监听

```bash
systemctl status sshd --no-pager
systemctl --failed --no-pager
sudo ss -lntup
ps -ef | grep -E '[s]shd|[h]ttp.server'
```

#### 防护和日志

```bash
firewall-cmd --get-active-zones
firewall-cmd --list-all
getenforce
sudo ausearch -m AVC,USER_AVC -ts recent 2>/dev/null | tail -50
sudo journalctl -u sshd --since '-20 min' --no-pager | tail -50
tail -n 50 ~/m1-project/logs/module2-http.log
```

### 任务四：完成教师故障

教师从下列故障卡选择，学生只接收故障现象，不提前查看修复答案。

#### 故障卡A：错误IP或连接未激活

- 典型现象：原IP不可达，SSH和HTTP同时失败。
- 证据方向：`ip -br address`、活动连接、地址规划。
- 修复原则：激活正确连接或恢复正确地址，不复制其他学生IP。

#### 故障卡B：DNS或hosts错误

- 典型现象：IP访问成功，名称访问失败或访问错误主机。
- 证据方向：`getent hosts`、hosts、连接DNS。
- 修复原则：恢复正确解析记录，分别用名称和IP复测。

#### 故障卡C：sshd停止

- 典型现象：主机可达，22端口拒绝连接。
- 证据方向：sshd状态、22监听和journal。
- 修复原则：确认配置语法后启动服务，不先改防火墙。

#### 故障卡D：服务只监听回环地址

- 典型现象：服务器本机访问成功，Ubuntu访问失败。
- 证据方向：`ss -lntp`中的监听地址。
- 修复原则：按业务范围调整监听，不盲目使用0.0.0.0。

#### 故障卡E：firewalld阻断

- 典型现象：服务active且监听正确，本机成功，外部超时。
- 证据方向：接口zone、运行时规则和客户端端口测试。
- 修复原则：最小开放目标端口或来源，保留SSH管理通道。

#### 故障卡F：SSH密钥权限错误

- 典型现象：密钥被拒绝，可能退回密码认证。
- 证据方向：`ssh -vv`、`.ssh`权限、所有权和sshd日志。
- 修复原则：目录700、文件600、所有者正确。

#### 故障卡G：SELinux上下文错误

- 典型现象：传统权限正常但服务被拒绝。
- 证据方向：`ls -Z`、AVC日志和持久fcontext规则。
- 修复原则：使用`semanage fcontext`与`restorecon`，不关闭SELinux。

### 任务五：端到端复测

每修复一个故障后，必须返回Ubuntu按原始路径复测：

```bash
nc -vz -w 3 <ROCKY_IP> 22
nc -vz -w 3 <ROCKY_IP> 8080
curl --fail http://<ROCKY_IP>:8080/
ssh rocky-course "hostname; uptime"
```

服务器再次检查：

```bash
systemctl --failed --no-pager
sudo ss -lntp | grep -E ':(22|8080)'
firewall-cmd --list-all
getenforce
```

只修复第一个发现的问题不代表故障结束，必须验证完整服务路径。

### 任务六：故障报告模板

每个故障使用：

```markdown
# 故障编号与标题

## 1. 故障现象与影响范围
## 2. 正常基线和最近变更
## 3. 检查过程与关键证据
## 4. 判断与根因
## 5. 修复操作
## 6. 客户端和服务端复测
## 7. 回退方法
## 8. 预防措施
```

## 七、独立实践

由两名同学互相设置一个不破坏唯一管理入口的故障。设置者记录原值和恢复方法，但不告诉排障者根因。排障者完成报告后，双方核对是否恢复到正确状态。

禁止设置：

- 删除虚拟磁盘或系统关键目录；
- 删除`rocky-server`主账号和唯一管理员；
- 修改后无法通过VMware控制台恢复的故障；
- 清空防火墙全部规则；
- 禁用SELinux作为最终状态。

## 八、验收标准

- [ ] 故障前存在完整、可复测的正常基线。
- [ ] 每个故障先明确客户端、目标、协议、端口和错误。
- [ ] 完成不少于3个不同层次故障。
- [ ] 每个报告均包含现象、证据、判断、根因、修复和验证。
- [ ] 没有同时无依据修改多个配置。
- [ ] 修复后从Ubuntu按原方式复测。
- [ ] SSH、HTTP、firewalld和SELinux回到课程要求状态。
- [ ] 完成一次同伴独立故障任务。

## 九、成果提交

1. `lab13-baseline.txt`。
2. Ubuntu客户端正常基线结果。
3. 不少于3份故障报告。
4. 同伴故障报告。
5. 最终服务、端口、规则和SELinux状态。
6. 一张模块二分层排障流程图。

## 十、常见问题

### Q1：不知道先查什么

先问清“谁通过什么名称、协议和端口访问谁”，再判断是全部访问失败还是只有某一种方式失败。

### Q2：修好服务后客户端仍然失败

继续检查监听地址、防火墙、名称解析和客户端缓存。一个事件可能包含多个故障。

### Q3：重启虚拟机后恢复了，报告怎么写

如果没有找到根因，不能把重启写成完成。应查阅启动前后的journal、服务状态和配置变化，说明证据不足并继续缩小范围。

### Q4：为什么不能关闭firewalld和SELinux

关闭防护只会绕开控制层，不能说明原业务规则正确，也会扩大暴露范围。

## 十一、课后思考与拓展

1. 如何通过影响范围快速区分客户端问题和服务器问题？
2. 为什么排障时需要记录最近变更？
3. 什么样的验证才能证明故障真正恢复？

## 十二、环境清理与保留

```bash
test -n "${MODULE2_HTTP_PID:-}" && kill "$MODULE2_HTTP_PID" 2>/dev/null || true
sudo firewall-cmd --remove-port=8080/tcp 2>/dev/null || true
```

保留SSH、静态网络、正确的firewalld和SELinux配置，供模块三服务部署使用。建议创建快照：

```text
01-Linux网络与安全基础完成
```
