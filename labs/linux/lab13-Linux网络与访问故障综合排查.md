# 实验13：Linux网络与访问故障综合排查

> 所属模块：模块二 网络远程管理与基础防护
> 建议学时：4学时
> 实验方式：2～3人小组互设故障
> 对应教材：2.12 网络与安全综合排障
> 知识前置：实验8～12
> 状态依赖：三机网络、SSH密钥、客户端配置、firewalld和SELinux均处于正确基线
> 建议起点：实验12结束后的正常状态，并先创建可回退快照
> 项目成果：正常基线、至少3份不同层次故障报告、模块二验收矩阵

## 一、项目情境

用户只报告“服务器访问不了”。排障人员需要补全信息、从客户端复现、按层取证，并在不破坏SSH和安全基线的前提下恢复业务。

## 二、实验规则

1. 设置者保存原值和恢复方法，排障者不提前查看答案。
2. 不设置会破坏VMware控制台的故障。
3. 不删除唯一管理员账号、课程私钥或原网络连接。
4. 不关闭firewalld，不把SELinux改为Disabled。
5. 排障者一次只修改一个因素。
6. 修复后必须从`ubuntu-client`按原路径复测。
7. 每组至少完成3个不同层次故障。

## 三、任务一：建立可重复测试服务

在`rocky-server`的VMware控制台完成。

### 3.1 准备目录

```bash
sudo mkdir -p /srv/module2-web
```

```bash
sudo chown rocky-server:rocky-server /srv/module2-web
```

编辑首页：

```bash
vim /srv/module2-web/index.html
```

写入：

```html
<h1>Module 2 baseline OK</h1>
```

### 3.2 创建systemd Unit

```bash
sudo vim /etc/systemd/system/module2-web.service
```

写入：

```ini
[Unit]
Description=Module 2 troubleshooting web service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=rocky-server
WorkingDirectory=/srv/module2-web
ExecStart=/usr/bin/python3 -m http.server 8080 --bind 0.0.0.0 --directory /srv/module2-web
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

加载Unit：

```bash
sudo systemctl daemon-reload
```

启动：

```bash
sudo systemctl enable --now module2-web
```

检查：

```bash
systemctl status module2-web --no-pager
```

检查监听：

```bash
sudo ss -lntp | grep ':8080 '
```

### 3.3 配置实验运行时规则

查看活动zone：

```bash
firewall-cmd --get-active-zones
```

记录实际zone：

| 项目 | 实际值 |
|---|---|
| 活动zone | |
| 对应网卡 | |

添加运行时规则：

```text
sudo firewall-cmd --zone=<实际活动区域> --add-port=8080/tcp
```

查询：

```text
firewall-cmd --zone=<实际活动区域> --query-port=8080/tcp
```

## 四、任务二：保存无故障基线

### 4.1 服务端基线

```bash
systemctl is-active module2-web
```

```bash
curl --fail http://127.0.0.1:8080/
```

```bash
sudo ss -lntp | grep ':8080 '
```

```bash
systemctl is-active sshd
```

```bash
systemctl is-active firewalld
```

```bash
getenforce
```

### 4.2 客户端基线

在`ubuntu-client`执行：

```bash
getent hosts rocky-server
```

```bash
nc -vz -w 3 rocky-server 8080
```

```bash
curl --fail http://rocky-server:8080/
```

```bash
ssh rocky-server 'hostnamectl --static'
```

所有结果符合预期后，创建“模块二正常基线”快照。

## 五、任务三：填写故障受理单

每个故障开始前，排障者填写：

| 项目 | 内容 |
|---|---|
| 故障编号 | |
| 客户端 | |
| 目标主机 | |
| 名称或IP | |
| 协议和端口 | |
| 原始操作 | |
| 原始错误 | |
| 首次发生时间 | |
| 影响范围 | |
| 最近已知变更 | |

## 六、任务四：按证据选择检查

不要求机械执行全部命令。根据当前现象选择下一条。

### 6.1 客户端

名称：

```bash
getent hosts rocky-server
```

地址：

```bash
ip -brief address
```

路由：

```bash
ip route
```

端口：

```bash
nc -vz -w 3 rocky-server 8080
```

HTTP：

```bash
curl -v --connect-timeout 3 http://rocky-server:8080/
```

SSH：

```bash
ssh -v rocky-server
```

### 6.2 服务端

服务：

```bash
systemctl status module2-web --no-pager
```

监听：

```bash
sudo ss -lntp | grep ':8080 '
```

本机访问：

```bash
curl -v http://127.0.0.1:8080/
```

活动zone：

```bash
firewall-cmd --get-active-zones
```

规则：

```text
firewall-cmd --zone=<实际活动区域> --list-all
```

服务日志：

```bash
sudo journalctl -u module2-web --since '20 minutes ago' --no-pager
```

SSH日志：

```bash
sudo journalctl -u sshd --since '20 minutes ago' --no-pager
```

SELinux：

```bash
getenforce
```

AVC：

```bash
sudo ausearch -m AVC,USER_AVC -ts recent
```

## 七、故障卡

以下操作只由设置者执行。设置者先记录原值，排障者不得查看当前故障卡。

### 故障卡A：服务停止

设置：

```bash
sudo systemctl stop module2-web
```

恢复：

```bash
sudo systemctl start module2-web
```

关键证据：服务inactive、8080无监听、客户端通常立即拒绝。

### 故障卡B：只监听回环地址

设置者先备份Unit：

```bash
sudo ls -l /etc/systemd/system/module2-web.service.before-fault
```

文件不存在时才执行下一条；如果已经存在，不得覆盖：

```bash
sudo cp -a /etc/systemd/system/module2-web.service /etc/systemd/system/module2-web.service.before-fault
```

编辑Unit：

```bash
sudo vim /etc/systemd/system/module2-web.service
```

把`--bind 0.0.0.0`改为`--bind 127.0.0.1`，然后加载：

```bash
sudo systemctl daemon-reload
```

重启：

```bash
sudo systemctl restart module2-web
```

恢复Unit：

```bash
sudo cp -a /etc/systemd/system/module2-web.service.before-fault /etc/systemd/system/module2-web.service
```

恢复后再次执行`daemon-reload`和`restart`。

关键证据：Rocky本机成功，`ss`显示`127.0.0.1:8080`，Ubuntu失败。

### 故障卡C：firewalld缺少规则

设置：

```text
sudo firewall-cmd --zone=<实际活动区域> --remove-port=8080/tcp
```

恢复：

```text
sudo firewall-cmd --zone=<实际活动区域> --add-port=8080/tcp
```

关键证据：服务active、`0.0.0.0:8080`监听、本机成功、Ubuntu超时或被拒绝。

### 故障卡D：客户端hosts错误

只在Ubuntu设置。先检查备份：

```bash
sudo ls -l /etc/hosts.before-lab13-fault
```

文件不存在时才执行下一条；如果已经存在，不得覆盖：

```bash
sudo cp -a /etc/hosts /etc/hosts.before-lab13-fault
```

编辑：

```bash
sudo vim /etc/hosts
```

把`rocky-server`对应地址临时改为`192.0.2.10`。

恢复：

```bash
sudo cp -a /etc/hosts.before-lab13-fault /etc/hosts
```

关键证据：`getent`返回错误地址，通过正确IP访问仍可能成功。

### 故障卡E：SSH授权目录权限错误

只在`rocky-server`设置，并保持VMware控制台和密码认证可用。

设置：

```bash
chmod 777 ~/.ssh
```

```bash
chmod 666 ~/.ssh/authorized_keys
```

恢复：

```bash
chmod 700 ~/.ssh
```

```bash
chmod 600 ~/.ssh/authorized_keys
```

```bash
restorecon -RFv ~/.ssh
```

关键证据：22端口成功，但强制公钥认证失败，sshd日志记录权限问题。

## 八、任务五：修复后的端到端复测

每张故障修复后，在Ubuntu重新执行原始操作：

```bash
getent hosts rocky-server
```

```bash
curl --fail http://rocky-server:8080/
```

```bash
ssh -o PasswordAuthentication=no rocky-server 'hostnamectl --static'
```

在Rocky检查：

```bash
systemctl is-active module2-web
```

```bash
sudo ss -lntp | grep ':8080 '
```

```bash
systemctl is-active firewalld
```

```bash
getenforce
```

只修复第一个问题不代表故障结束，必须通过完整回归矩阵。

## 九、故障报告模板

```markdown
# 故障编号与标题

## 1. 故障现象与影响范围

## 2. 正常基线与最近变更

## 3. 检查过程与关键证据

## 4. 判断与根因

## 5. 修复操作

## 6. 原客户端复测与回归检查

## 7. 回退方法

## 8. 预防措施
```

## 十、模块二最终验收

| 项目 | 验证命令 | 结果 |
|---|---|---|
| 三机名称 | `getent hosts rocky-server rocky-web ubuntu-client` | |
| rocky-server SSH | `ssh rocky-server hostname` | |
| rocky-web SSH | `ssh rocky-web hostname` | |
| Web服务 | `curl --fail http://rocky-server:8080/` | |
| firewalld | `systemctl is-active firewalld` | |
| SELinux | `getenforce` | |
| rsync备份 | `diff -qr ~/m1-project/web ~/backup-lab/web-current` | |
| cron频率 | `crontab -l` | |

## 十一、验收标准

- [ ] 故障前存在可重复验证的正常基线。
- [ ] 每张故障先填写受理单。
- [ ] 完成至少3个不同层次故障。
- [ ] 每次根据证据选择下一条检查，而不是粘贴全部命令。
- [ ] 每次只修改一个因素。
- [ ] 每次从Ubuntu按原路径复测。
- [ ] SSH、firewalld和SELinux最终状态正确。
- [ ] 每张报告包含证据、根因、修复、回退和预防措施。

## 十二、环境清理

删除8080运行时规则：

```text
sudo firewall-cmd --zone=<实际活动区域> --remove-port=8080/tcp
```

停止服务：

```bash
sudo systemctl disable --now module2-web
```

删除Unit：

```bash
sudo rm /etc/systemd/system/module2-web.service
```

故障卡B已经恢复且确认备份不再需要时，删除实验Unit备份：

```bash
sudo rm -f /etc/systemd/system/module2-web.service.before-fault
```

重新加载：

```bash
sudo systemctl daemon-reload
```

检查测试目录：

```bash
sudo find /srv/module2-web -maxdepth 2 -ls
```

确认只有本实验文件后删除：

```bash
sudo rm -rf /srv/module2-web
```

保留实验8网络、实验10 SSH密钥与客户端配置、正确的firewalld和SELinux基线，供模块三服务部署继续使用。
