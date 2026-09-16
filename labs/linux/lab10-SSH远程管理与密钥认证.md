# 实验10：SSH远程管理与密钥认证

> 所属模块：模块二 网络远程管理与基础防护
> 建议学时：4学时
> 实验方式：2～3人小组，每人完成自己的三机配置
> 对应教材：2.5 SSH远程管理；2.6 SSH密钥认证；2.7 SSH客户端配置与文件传输
> 知识前置：实验8三机网络、实验9端口证据链
> 状态依赖：实验8的静态地址、`/etc/hosts`和`course-env.sh`可用；不依赖实验9临时服务
> 建议起点：`Linux-L1`并保留实验8网络成果
> 项目成果：双服务器SSH基线、课程密钥、客户端别名、传输校验和权限故障记录

## 一、项目情境

企业运维人员需要从`ubuntu-client`统一管理`rocky-server`和`rocky-web`。本实验要求建立可验证、可回退的SSH管理入口，并完成一次真实的密钥权限故障排查。

## 二、实验规则

1. 修改SSH服务端时必须保留VMware控制台。
2. 密钥验证前不关闭密码认证。
3. 服务器主机指纹必须通过可信控制台核对。
4. 私钥只保存在`ubuntu-client`，不得复制到Rocky。
5. 每条命令单独执行，不把实验整体粘贴为脚本。
6. 修改服务端后使用第二个新会话验证，不能只依赖原连接。

## 三、任务一：检查两台Rocky的SSH服务

先在`rocky-server`的VMware控制台完成。

### 3.1 核对身份

```bash
whoami
```

```bash
hostnamectl --static
```

预期当前用户和主机名均为`rocky-server`。

### 3.2 检查软件包

```bash
rpm -q openssh-server
```

未安装时执行：

```bash
sudo dnf install -y openssh-server
```

### 3.3 启动服务

```bash
sudo systemctl enable --now sshd
```

检查运行状态：

```bash
systemctl is-active sshd
```

检查开机启动：

```bash
systemctl is-enabled sshd
```

检查22端口：

```bash
sudo ss -lntp | grep ':22 '
```

### 3.4 检查配置

语法检查：

```bash
sudo sshd -t
```

查看有效值：

```bash
sudo sshd -T | grep -E '^(port|listenaddress|permitrootlogin|passwordauthentication|pubkeyauthentication|maxauthtries) '
```

### 3.5 检查防火墙

```bash
sudo firewall-cmd --get-active-zones
```

根据输出记录实际活动区域。查询SSH服务的命令格式：

```text
sudo firewall-cmd --zone=<实际活动区域> --query-service=ssh
```

返回`no`时先添加运行时规则：

```text
sudo firewall-cmd --zone=<实际活动区域> --add-service=ssh
```

### 3.6 记录主机指纹

```bash
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

把SHA256指纹填写到记录表：

| 服务器 | Ed25519主机指纹 |
|---|---|
| rocky-server | |
| rocky-web | |

切换到`rocky-web`控制台，重复3.1～3.6。用户名和主机名应为`rocky-web`。

## 四、任务二：从Ubuntu首次连接

### 4.1 检查客户端身份与解析

在`ubuntu-client`执行：

```bash
hostnamectl --static
```

```bash
getent hosts rocky-server
```

```bash
getent hosts rocky-web
```

### 4.2 测试TCP 22

```bash
nc -vz -w 3 rocky-server 22
```

```bash
nc -vz -w 3 rocky-web 22
```

只有两个端口都成功，才进入SSH认证。

### 4.3 首次连接rocky-server

```bash
ssh rocky-server@rocky-server
```

出现主机真实性提示时：

1. 找到提示中的SHA256指纹。
2. 与任务一记录的`rocky-server`指纹比较。
3. 完全一致后输入`yes`。
4. 输入实验环境密码。

登录后确认用户：

```bash
whoami
```

确认主机：

```bash
hostnamectl --static
```

退出：

```bash
exit
```

### 4.4 首次连接rocky-web

```bash
ssh rocky-web@rocky-web
```

重复指纹核对和身份检查。

### 4.5 检查known_hosts

```bash
ssh-keygen -F rocky-server
```

```bash
ssh-keygen -F rocky-web
```

## 五、任务三：建立密钥认证

### 5.1 准备客户端SSH目录

```bash
mkdir -p ~/.ssh
```

```bash
chmod 700 ~/.ssh
```

检查课程密钥：

```bash
ls -l ~/.ssh/linux-course-ed25519
```

如果文件不存在，生成：

```bash
ssh-keygen -t ed25519 -a 64 -f ~/.ssh/linux-course-ed25519 -C 'linux-course@ubuntu-client'
```

如果文件已经存在，不得覆盖。查看公钥指纹：

```bash
ssh-keygen -lf ~/.ssh/linux-course-ed25519.pub
```

检查私钥权限：

```bash
stat -c '%A %a %U:%G %n' ~/.ssh/linux-course-ed25519
```

### 5.2 分发公钥

部署到`rocky-server`：

```bash
ssh-copy-id -i ~/.ssh/linux-course-ed25519.pub rocky-server@rocky-server
```

部署到`rocky-web`：

```bash
ssh-copy-id -i ~/.ssh/linux-course-ed25519.pub rocky-web@rocky-web
```

### 5.3 在服务器核对授权文件

在`rocky-server`执行：

```bash
stat -c '%A %a %U:%G %n' ~/.ssh ~/.ssh/authorized_keys
```

```bash
tail -n 1 ~/.ssh/authorized_keys
```

在`rocky-web`重复检查。

### 5.4 强制只使用课程密钥

回到`ubuntu-client`测试`rocky-server`：

```bash
ssh -o PasswordAuthentication=no -o IdentitiesOnly=yes -i ~/.ssh/linux-course-ed25519 rocky-server@rocky-server
```

成功后退出：

```bash
exit
```

测试`rocky-web`：

```bash
ssh -o PasswordAuthentication=no -o IdentitiesOnly=yes -i ~/.ssh/linux-course-ed25519 rocky-web@rocky-web
```

两次登录都不能回退到密码。成功才证明密钥部署正确。

## 六、任务四：配置SSH客户端别名

### 6.1 备份已有配置

检查：

```bash
ls -l ~/.ssh/config
```

文件存在且没有备份时执行：

```bash
cp -a ~/.ssh/config ~/.ssh/config.before-lab10
```

不要覆盖已有`config.before-lab10`。

### 6.2 编辑配置

```bash
vim ~/.ssh/config
```

写入或合并以下内容：

```sshconfig
Host rs rocky-server
    HostName rocky-server
    User rocky-server
    Port 22
    IdentityFile ~/.ssh/linux-course-ed25519
    IdentitiesOnly yes

Host rw rocky-web
    HostName rocky-web
    User rocky-web
    Port 22
    IdentityFile ~/.ssh/linux-course-ed25519
    IdentitiesOnly yes

Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

设置权限：

```bash
chmod 600 ~/.ssh/config
```

同一组配置保留短别名和完整主机名，因此后续实验中的`ssh rocky-server`、`rsync rocky-server:...`仍会使用课程密钥。

检查`rs`最终参数：

```bash
ssh -G rs | grep -E '^(hostname|user|port|identityfile|identitiesonly) '
```

检查`rw`最终参数：

```bash
ssh -G rw | grep -E '^(hostname|user|port|identityfile|identitiesonly) '
```

验证远端身份：

```bash
ssh rs 'whoami; hostnamectl --static'
```

```bash
ssh rw 'whoami; hostnamectl --static'
```

## 七、任务五：配置服务端安全基线

分别在两台Rocky的VMware控制台完成。先从`rocky-server`开始。

### 7.1 备份主配置

检查备份是否存在：

```bash
sudo ls -l /etc/ssh/sshd_config.before-lab10
```

不存在时创建：

```bash
sudo cp -a /etc/ssh/sshd_config /etc/ssh/sshd_config.before-lab10
```

### 7.2 创建课程配置片段

```bash
sudo vim /etc/ssh/sshd_config.d/20-course-baseline.conf
```

写入：

```sshdconfig
PermitRootLogin no
MaxAuthTries 3
PubkeyAuthentication yes
PasswordAuthentication yes
```

当前仍保留普通用户密码登录，避免密钥故障造成锁定。

### 7.3 检查并加载

语法检查：

```bash
sudo sshd -t
```

只有没有语法错误才能继续。

重新加载：

```bash
sudo systemctl reload sshd
```

查看最终值：

```bash
sudo sshd -T | grep -E '^(permitrootlogin|maxauthtries|pubkeyauthentication|passwordauthentication) '
```

### 7.4 使用第二个新会话复测

保留当前控制台，从Ubuntu新开终端执行：

```bash
ssh rs
```

新会话成功后退出：

```bash
exit
```

再对`rocky-web`重复7.1～7.4，并使用`ssh rw`复测。

## 八、任务六：SCP上传、下载与校验

在`ubuntu-client`创建目录：

```bash
mkdir -p ~/course-practice/m2/lab10
```

打开源文件：

```bash
vim ~/course-practice/m2/lab10/ssh-transfer.txt
```

写入姓名、日期和“SSH transfer test”，保存后计算哈希：

```bash
sha256sum ~/course-practice/m2/lab10/ssh-transfer.txt
```

上传：

```bash
scp ~/course-practice/m2/lab10/ssh-transfer.txt rs:/tmp/
```

远端计算哈希：

```bash
ssh rs 'sha256sum /tmp/ssh-transfer.txt'
```

远端检查文件：

```bash
ssh rs 'ls -l /tmp/ssh-transfer.txt'
```

下载为另一个文件名：

```bash
scp rs:/tmp/ssh-transfer.txt ~/course-practice/m2/lab10/ssh-transfer-return.txt
```

比较：

```bash
diff ~/course-practice/m2/lab10/ssh-transfer.txt ~/course-practice/m2/lab10/ssh-transfer-return.txt
```

`diff`无输出表示内容相同。

## 九、任务七：SFTP交互传输

从Ubuntu连接：

```bash
sftp rw
```

在`sftp>`提示符中逐条执行：

```text
pwd
lpwd
cd /tmp
lcd ~/course-practice/m2/lab10
put ssh-transfer.txt
ls -l ssh-transfer.txt
get ssh-transfer.txt sftp-return.txt
exit
```

退出后比较：

```bash
diff ~/course-practice/m2/lab10/ssh-transfer.txt ~/course-practice/m2/lab10/sftp-return.txt
```

## 十、任务八：制造密钥权限故障并恢复

只在`rocky-server`制造故障，并保持VMware控制台可用。

### 10.1 记录正确权限

```bash
stat -c '%A %a %U:%G %n' ~/.ssh ~/.ssh/authorized_keys
```

### 10.2 制造错误权限

```bash
chmod 777 ~/.ssh
```

```bash
chmod 666 ~/.ssh/authorized_keys
```

### 10.3 从Ubuntu强制测试公钥

```bash
ssh -v -o PasswordAuthentication=no -o IdentitiesOnly=yes -i ~/.ssh/linux-course-ed25519 rocky-server@rocky-server
```

预期公钥认证失败。记录`ssh -v`中客户端提供密钥和服务器拒绝认证的证据。

### 10.4 查看服务端日志

回到Rocky控制台：

```bash
sudo journalctl -u sshd --since '10 minutes ago' --no-pager
```

查找与所有权或权限相关的记录。

### 10.5 修复

```bash
chmod 700 ~/.ssh
```

```bash
chmod 600 ~/.ssh/authorized_keys
```

```bash
restorecon -RFv ~/.ssh
```

### 10.6 重新验证

从Ubuntu执行：

```bash
ssh -o PasswordAuthentication=no -o IdentitiesOnly=yes -i ~/.ssh/linux-course-ed25519 rocky-server@rocky-server
```

成功后确认身份并退出。

## 十一、验收标准

- [ ] 两台Rocky的`sshd`均为active和enabled。
- [ ] 两台服务器22端口正常监听，firewalld规则明确。
- [ ] 两个服务器主机指纹均通过控制台核对。
- [ ] Ubuntu的课程私钥没有复制到服务器。
- [ ] 指定密钥能够登录两台Rocky，且不回退到密码。
- [ ] `rs`和`rw`别名的最终参数正确。
- [ ] 服务端有效配置显示禁止root登录、最大尝试次数为3。
- [ ] SCP和SFTP均完成上传与下载，哈希或`diff`验证通过。
- [ ] 密钥权限故障已经制造、定位、修复并复测。
- [ ] 原DHCP网络和VMware控制台回退入口仍然可用。

## 十二、成果提交

1. 两台服务器的SSH服务、监听端口和主机指纹记录。
2. `known_hosts`查询结果。
3. 课程公钥指纹及两次强制公钥登录证据。
4. `ssh -G rs`与`ssh -G rw`结果。
5. 服务端`sshd -T`安全基线结果。
6. SCP和SFTP传输方向、哈希或`diff`结果。
7. 权限故障的客户端日志、服务端日志和修复结果。

## 十三、常见问题

### 13.1 Connection refused

先在服务端检查：

```bash
systemctl is-active sshd
```

```bash
sudo ss -lntp | grep ':22 '
```

### 13.2 Connection timed out

检查客户端路由、VMware网络和服务端防火墙，不要先重置用户密码。

### 13.3 Permission denied

检查客户端实际使用的身份：

```bash
ssh -v rs
```

检查服务端授权文件：

```bash
stat -c '%A %a %U:%G %n' ~/.ssh ~/.ssh/authorized_keys
```

### 13.4 主机密钥发生变化

先在VMware控制台重新取得服务器指纹。确认是合法重装后，才能删除对应旧记录：

```bash
ssh-keygen -R rocky-server
```

### 13.5 修改配置后新会话无法登录

保持原控制台，不要退出。检查：

```bash
sudo sshd -t
```

```bash
sudo journalctl -u sshd -n 50 --no-pager
```

修正配置片段后重新加载。

## 十四、环境保留

保留：

- 两台Rocky的SSH服务和`20-course-baseline.conf`。
- Ubuntu的`linux-course-ed25519`课程密钥。
- Ubuntu的`~/.ssh/config`、`rs`和`rw`别名。
- 两台Rocky的`authorized_keys`正确权限和SELinux上下文。

密码认证本实验仍保持开启。后续确需关闭时，必须重新执行“双会话验证”流程。

这些SSH成果将由实验11的`rsync`、后续Python自动化运维以及虚拟化容器课程继续复用。
