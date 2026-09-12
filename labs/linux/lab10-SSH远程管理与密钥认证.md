# 实验10：SSH远程管理与密钥认证

> 所属模块：模块二 网络、远程管理与基础防护  
> 建议学时：4学时  
> 实验方式：个人  
> 对应教材：《模块二 网络、远程管理与基础防护》第17—19章  
> 前置实验：实验9  
> 项目成果：`ubuntu-client`到两台Rocky服务器的SSH连接、Ed25519密钥认证、双别名、文件传输和认证故障记录

## 一、项目情境

运维人员通常不在服务器控制台前工作，而是从管理终端通过SSH连接服务器。你需要确认目标主机身份，完成密码和密钥认证，配置易识别的客户端别名，使用SCP/SFTP传输文件，并根据客户端调试信息和服务端日志处理一次认证失败。

## 二、实验目标

### 1. 知识目标

1. 说明SSH客户端、sshd服务、主机密钥、用户密钥和加密通道的关系。
2. 区分主机身份验证与用户身份验证。
3. 说明私钥、公钥、`authorized_keys`和`known_hosts`的作用。
4. 说明密码认证、密钥认证和最小开放的基本安全边界。

### 2. 能力目标

1. 检查sshd状态、监听地址、有效配置和日志。
2. 从Ubuntu客户端使用对应账号分别连接`rocky-server`和`rocky-web`。
3. 创建Ed25519密钥并正确部署公钥。
4. 使用SSH客户端配置、SCP和SFTP管理服务器。
5. 使用`ssh -v`和journal日志排查密钥权限问题。

### 3. 素质目标

1. 不共享、上传或提交私钥。
2. 不无条件删除`known_hosts`绕过主机密钥警告。
3. 修改远程管理配置时保留VMware控制台和已登录会话。

## 三、知识准备

```text
SSH客户端连接服务器22端口
→ 客户端核对服务器主机密钥
→ 双方建立加密通道
→ 服务器验证用户密码或公钥签名
→ 为用户创建远程Shell或文件传输会话
```

| 文件或对象 | 所在位置 | 作用 |
|---|---|---|
| 服务器主机私钥 | `/etc/ssh/ssh_host_*_key` | 证明服务器身份，不得复制给学生 |
| 服务器主机公钥 | `/etc/ssh/ssh_host_*_key.pub` | 生成主机指纹供客户端核对 |
| 客户端用户私钥 | Ubuntu用户`~/.ssh/`目录 | 证明客户端用户身份，必须保密 |
| 客户端用户公钥 | 私钥对应的`.pub`文件 | 可以部署到服务器 |
| `authorized_keys` | 服务器用户`~/.ssh/` | 列出允许登录该用户的公钥 |
| `known_hosts` | 客户端用户`~/.ssh/` | 记录已经确认的服务器身份 |

## 四、实验环境

- `rocky-server`和`rocky-web`已配置稳定IP。
- Ubuntu 22.04 Desktop `ubuntu-client`作为正式SSH客户端，已完成三机互通。
- 保留VMware控制台登录，避免SSH配置错误后失去管理入口。
- Ubuntu中应能执行`ssh`、`ssh-keygen`、`ssh-copy-id`、`scp`和`sftp`；Windows宿主机仅作可选辅助验证。

记录：

```text
ROCKY_SERVER_IP=________________
ROCKY_WEB_IP=___________________
SERVER_USER=rocky-server
WEB_USER=rocky-web
SSH_PORT=22
```

## 五、项目任务

1. 在两台Rocky检查和启动sshd。
2. 核对主机指纹并完成首次密码连接。
3. 创建独立实验密钥并部署公钥。
4. 验证密钥认证和私钥保护。
5. 配置SSH别名并完成SCP/SFTP传输。
6. 制造`authorized_keys`权限错误，收集证据并修复。

## 六、实验步骤

### 任务一：检查SSH服务端

#### 步骤1：检查服务和端口

在两台Rocky控制台分别执行：

```bash
sudo systemctl enable --now sshd
systemctl is-active sshd
systemctl is-enabled sshd
sudo ss -lntp | grep ':22'
```

> **验收点**：sshd为active和enabled，TCP 22处于监听状态。

#### 步骤2：检查有效配置

```bash
sudo sshd -t
sudo sshd -T | grep -E '^(port|listenaddress|passwordauthentication|pubkeyauthentication|permitrootlogin|maxauthtries) '
```

`sshd -t`检查语法，`sshd -T`显示合并后的有效配置，比只查看某一行配置更可靠。

> **验收点**：配置语法无错误，能够指出端口和认证方式。

#### 步骤3：生成主机指纹

```bash
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

记录SHA256指纹，首次连接时与Ubuntu显示的指纹核对。

### 任务二：首次远程连接

#### 步骤4：测试端口

在`ubuntu-client`执行，分别替换两个实际IP：

```bash
ip -brief address
ip route get <ROCKY_SERVER_IP>
nc -vz -w 3 <ROCKY_SERVER_IP> 22
nc -vz -w 3 <ROCKY_WEB_IP> 22
```

如果失败，依次检查虚拟机IP、sshd状态、22端口监听、VMware NAT和firewalld。

#### 步骤5：密码连接并确认主机身份

```bash
ssh rocky-server@<ROCKY_SERVER_IP>
ssh rocky-web@<ROCKY_WEB_IP>
```

首次连接会显示主机指纹。分别与对应Rocky控制台记录的指纹核对，确认后输入`yes`，密码均为课堂口令`123456`。

登录后执行：

```bash
whoami
hostname
printf 'client=%s\n' "$SSH_CLIENT"
exit
```

> **验收点**：两次远程登录的用户名与主机名分别为`rocky-server`和`rocky-web`，能够说明主机指纹核对的意义。

### 任务三：配置密钥认证

#### 步骤6：在Ubuntu创建独立实验密钥

在Ubuntu客户端执行：

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keygen -t ed25519 -a 64 \
  -f ~/.ssh/linux-course-ed25519 \
  -C "ubuntu-client-linux-course"
```

按课程要求设置私钥口令。生成：

```text
linux-course-ed25519       私钥，不得提交或发送
linux-course-ed25519.pub   公钥，可以部署到服务器
```

查看公钥指纹：

```bash
ssh-keygen -lf ~/.ssh/linux-course-ed25519.pub
```

> **验收点**：私钥和公钥均存在，能够指出哪一个绝不能提交。

#### 步骤7：把公钥部署到服务器

使用`ssh-copy-id`部署公钥：

```bash
ssh-copy-id -i ~/.ssh/linux-course-ed25519.pub rocky-server@<ROCKY_SERVER_IP>
ssh-copy-id -i ~/.ssh/linux-course-ed25519.pub rocky-web@<ROCKY_WEB_IP>
```

在两台Rocky控制台分别检查：

```bash
stat -c '%A %a %U:%G %n' ~/.ssh ~/.ssh/authorized_keys
tail -n 1 ~/.ssh/authorized_keys
```

推荐权限为目录700、文件600，所有者应为当前机器的课程用户。

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chown -R "$USER:$USER" ~/.ssh
```

> **验收点**：`authorized_keys`包含实验公钥，目录和文件权限正确。

#### 步骤8：使用密钥登录

在Ubuntu客户端执行：

```bash
ssh -i ~/.ssh/linux-course-ed25519 rocky-server@<ROCKY_SERVER_IP>
ssh -i ~/.ssh/linux-course-ed25519 rocky-web@<ROCKY_WEB_IP>
```

如果设置了私钥口令，客户端会要求输入私钥口令，而不是服务器账号密码。

登录后执行：

```bash
whoami
hostname
exit
```

> **验收点**：指定私钥后可登录两台服务器，不再输入服务器账号密码。

### 任务四：配置客户端别名

#### 步骤9：编辑Ubuntu SSH配置

编辑：

```text
~/.ssh/config
```

加入：

```text
Host rocky-server
    HostName <ROCKY_SERVER_IP>
    User rocky-server
    Port 22
    IdentityFile ~/.ssh/linux-course-ed25519
    IdentitiesOnly yes

Host rocky-web
    HostName <ROCKY_WEB_IP>
    User rocky-web
    Port 22
    IdentityFile ~/.ssh/linux-course-ed25519
    IdentitiesOnly yes
```

把两个IP占位符替换为实际地址。测试：

```bash
chmod 600 ~/.ssh/config
ssh -G rocky-server | grep -E '^(hostname|user|port|identityfile) '
ssh rocky-server hostname
ssh rocky-web hostname
```

> **验收点**：两个别名分别进入正确服务器，不出现角色串线。

### 任务五：文件传输

#### 步骤10：使用SCP上传和下载

在Ubuntu创建文件：

```bash
printf '%s\n' 'SSH transfer test' > /tmp/ssh-transfer.txt
sha256sum /tmp/ssh-transfer.txt
scp /tmp/ssh-transfer.txt rocky-server:~/m1-project/
```

在Rocky Linux中：

```bash
sha256sum ~/m1-project/ssh-transfer.txt
```

对比两端SHA256。下载服务器基线：

```bash
mkdir -p ~/course-downloads
scp rocky-server:~/m1-project/evidence/lab08-network-after.txt ~/course-downloads/
```

> **验收点**：上传文件哈希一致，能够完成一次下载。

#### 步骤11：使用SFTP

```bash
sftp rocky-server
```

在SFTP提示符中执行：

```text
pwd
lpwd
ls
lls
put 本地文件路径
get 远程文件名
exit
```

`pwd/ls`作用于远程端，`lpwd/lls`作用于本地端。

### 任务六：密钥权限故障排查

#### 步骤12：制造错误权限

保持一个已经登录的SSH会话和VMware控制台。在Rocky Linux执行：

```bash
chmod 777 ~/.ssh
chmod 666 ~/.ssh/authorized_keys
```

这是故障注入，不是最终配置。在Ubuntu新开终端，执行：

```bash
ssh -vv -o PreferredAuthentications=publickey \
  -o PasswordAuthentication=no \
  -i ~/.ssh/linux-course-ed25519 rocky-server@<ROCKY_SERVER_IP>
```

该命令强制只使用公钥并关闭密码回退，因此权限错误时应明确失败。观察调试信息中客户端是否提供了正确公钥，以及服务端为何拒绝认证。

在服务器查看日志：

```bash
sudo journalctl -u sshd --since '-10 min' --no-pager | tail -50
```

#### 步骤13：修复并复测

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chown -R "$USER:$USER" ~/.ssh
```

再次在Ubuntu执行：

```bash
ssh -vv -o PreferredAuthentications=publickey \
  -o PasswordAuthentication=no \
  -i ~/.ssh/linux-course-ed25519 rocky-server@<ROCKY_SERVER_IP>
```

> **验收点**：记录故障现象、客户端证据、服务端日志、根因、修复和密钥认证复测。

### 任务七：保存服务端证据

```bash
{
    systemctl is-active sshd
    sudo ss -lntp | grep ':22'
    sudo sshd -T | grep -E '^(port|passwordauthentication|pubkeyauthentication|permitrootlogin) '
    stat -c '%A %a %U:%G %n' ~/.ssh ~/.ssh/authorized_keys
    sudo journalctl -u sshd --since '-30 min' --no-pager | tail -40
} > ~/m1-project/evidence/lab10-ssh.txt
```

## 七、独立实践

1. 在Ubuntu为`rocky-server`和`rocky-web`都显式设置`ConnectTimeout 5`。
2. 使用别名执行远程单条命令：`hostname && uptime`。
3. 上传一个目录并在服务器比较文件数量。
4. 查看`known_hosts`中目标主机记录，但不要删除。
5. 说明服务器IP发生变化和服务器主机密钥发生变化应如何区别处理。

## 八、验收标准

- [ ] sshd服务、22端口和有效配置已检查。
- [ ] 首次连接前核对了服务器主机指纹。
- [ ] Ubuntu客户端使用各自主账号成功登录两台Rocky。
- [ ] 已创建独立Ed25519密钥，私钥未提交。
- [ ] `~/.ssh`为700，`authorized_keys`为600。
- [ ] 使用密钥和两个客户端别名成功登录对应服务器。
- [ ] SCP上传文件的SHA256一致，并完成一次下载。
- [ ] 能区分SFTP本地与远程命令。
- [ ] 已完成一次密钥权限故障排查和复测。
- [ ] VMware控制台和管理入口始终可用。

## 九、成果提交

1. SSH服务状态、端口和有效配置。
2. 服务器主机指纹和用户公钥指纹。
3. 密钥登录和客户端别名验证。
4. SCP/SFTP传输及哈希结果。
5. 密钥权限故障报告。
6. `lab10-ssh.txt`。

严禁提交：

- `linux-course-ed25519`私钥；
- 个人常用密码；
- 其他同学的密钥；
- 真实生产服务器地址和凭据。

## 十、常见问题

### Q1：Connection refused

目标IP可达但22端口没有接受连接。检查sshd状态、监听端口和连接目标是否正确。

### Q2：Connection timed out

优先检查目标IP、路由、VMware网络和防火墙。超时与密码错误不是同一阶段。

### Q3：Permission denied publickey,password

使用`ssh -vv`检查客户端尝试了哪个密钥，再检查服务器`authorized_keys`内容、所有权、权限和sshd日志。

### Q4：出现REMOTE HOST IDENTIFICATION HAS CHANGED

先确认服务器是否重装、IP是否分配给了另一台虚拟机，以及新主机指纹是否可信。不能无条件删除known_hosts记录。

### Q5：SCP完成后为什么还要校验

文件存在不能证明内容完整。通过SHA256或内容比较确认传输前后一致。

## 十一、课后思考与拓展

1. 主机密钥和用户密钥分别证明谁的身份？
2. 为什么私钥口令不能完全替代服务器端账号管理？
3. 修改SSH端口能减少扫描噪声，但为什么不能替代真正的身份认证和访问控制？

## 十二、环境保留

保留SSH服务、Ubuntu客户端别名、公钥和正确权限，后续备份与综合项目继续使用。私钥只保存在本人Ubuntu客户端的`~/.ssh/`目录中，不复制到Rocky服务器或Windows公共目录。
