# 实验12：firewalld与SELinux基础防护

> 所属模块：模块二 网络、远程管理与基础防护  
> 建议学时：4学时  
> 实验方式：个人  
> 对应教材：《模块二 网络、远程管理与基础防护》第21—23章  
> 知识前置：实验8—10中的地址、端口、服务和客户端验证；教材第21—23章\
> 状态依赖：实验8交付的三机网络，`rocky-server`的firewalld与SELinux保持正常基线；不依赖实验11的备份任务\
> 建议起点：`Linux-L1`并保留实验8网络成果\
> 项目成果：最小端口开放、运行时与永久规则、来源限制、SELinux上下文和规则回滚记录

## 一、项目情境

服务器需要允许管理人员使用SSH，并允许用户访问指定Web端口，但数据库和缓存端口不能随意暴露。你需要使用firewalld建立最小开放策略，并认识传统文件权限、firewalld和SELinux分别位于不同控制层。

## 二、实验目标

### 1. 知识目标

1. 说明zone、service、port、source以及运行时和永久规则。
2. 区分服务运行、端口监听和防火墙放行。
3. 说明传统DAC权限与SELinux强制访问控制的分层关系。
4. 说明Enforcing、Permissive和Disabled的区别。

### 2. 能力目标

1. 查看接口所属zone和当前规则。
2. 配置、验证、持久化和回滚端口或服务规则。
3. 使用rich rule限制来源地址。
4. 查看和恢复SELinux文件上下文，查询AVC日志。

### 3. 素质目标

1. 修改远程防火墙前保留控制台和SSH会话。
2. 不通过关闭firewalld或SELinux解决最终问题。
3. 数据库和Redis端口默认不向整个网络开放。

## 三、知识准备

```text
客户端请求到达Linux主机
→ 网络和路由正确
→ firewalld决定网络流量是否允许
→ 进程必须在目标地址和端口监听
→ 文件传统权限决定用户是否可访问
→ SELinux策略进一步检查进程类型与文件类型
→ 应用返回结果并记录日志
```

运行时规则立即生效，重载或重启后可能消失；永久规则保存在配置中，需要reload后进入运行时。先用运行时规则试验，确认不影响管理后再永久化。

## 四、实验环境

- 默认在`rocky-server`执行；保留VMware控制台和一个SSH会话。
- firewalld保持启用，SELinux保持Enforcing。
- `ubuntu-client`作为正式外部测试客户端。
- 临时Web端口8080。

## 五、项目任务

1. 保存firewalld和SELinux基线。
2. 启动临时Web服务，证明监听不等于外部可达。
3. 配置并验证运行时端口规则。
4. 将正确规则永久化并验证reload。
5. 使用rich rule仅允许指定来源。
6. 配置SELinux持久文件上下文并验证恢复。
7. 回滚临时规则并保存最终基线。

## 六、实验步骤

### 任务一：保存安全基线

```bash
mkdir -p ~/m1-project/evidence ~/m1-project/logs ~/m1-project/backup/security
{
    systemctl is-active firewalld
    firewall-cmd --get-active-zones
    firewall-cmd --get-default-zone
    firewall-cmd --list-all
    getenforce
    sestatus
} | tee ~/m1-project/evidence/lab12-security-before.txt
sudo firewall-cmd --list-all-zones > ~/m1-project/backup/security/firewalld-all-zones.txt
```

> **验收点**：firewalld为active，SELinux为Enforcing，已保存当前zone和规则。

### 任务二：准备测试服务

```bash
mkdir -p ~/m1-project/firewall-test
printf '<h1>firewalld test</h1>\n' > ~/m1-project/firewall-test/index.html
cd ~/m1-project/firewall-test
python3 -m http.server 8080 --bind 0.0.0.0 > ~/m1-project/logs/lab12-http.log 2>&1 &
LAB12_HTTP_PID=$!
ss -lntp | grep ':8080'
curl -I http://127.0.0.1:8080/
```

记录虚拟机IP：

```bash
VM_IP=$(ip -4 route get 1.1.1.1 | awk 'NR==1 {for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}')
printf 'vm_ip=%s\n' "$VM_IP"
```

在Ubuntu客户端测试：

```bash
nc -vz -w 3 <ROCKY_IP> 8080
curl --connect-timeout 3 -I http://<ROCKY_IP>:8080/
```

如果之前实验遗留8080规则，应先记录并删除，否则无法观察规则变化。

> **验收点**：本机HTTP成功，外部结果已经记录；能说明监听和防火墙是两个条件。

### 任务三：运行时规则

#### 步骤1：确认接口所属zone

```bash
IFACE=$(ip route show default | awk 'NR==1 {print $5}')
ZONE=$(firewall-cmd --get-zone-of-interface="$IFACE")
printf 'interface=%s zone=%s\n' "$IFACE" "$ZONE"
```

如果返回`no zone`或空值，使用`firewall-cmd --get-active-zones`确认实际zone，不要盲目修改默认zone。

#### 步骤2：开放运行时端口

```bash
sudo firewall-cmd --zone="$ZONE" --add-port=8080/tcp
sudo firewall-cmd --zone="$ZONE" --query-port=8080/tcp
sudo firewall-cmd --zone="$ZONE" --list-ports
```

在Ubuntu重新测试：

```bash
nc -vz -w 3 <ROCKY_IP> 8080
curl --connect-timeout 3 -I http://<ROCKY_IP>:8080/
```

> **验收点**：端口规则为yes，Ubuntu获得HTTP响应。

#### 步骤3：验证运行时与永久差异

```bash
sudo firewall-cmd --zone="$ZONE" --query-port=8080/tcp
sudo firewall-cmd --permanent --zone="$ZONE" --query-port=8080/tcp
```

第一条应为yes，第二条可能为no。

### 任务四：永久规则和回滚

```bash
sudo firewall-cmd --permanent --zone="$ZONE" --add-port=8080/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --zone="$ZONE" --query-port=8080/tcp
sudo firewall-cmd --permanent --zone="$ZONE" --query-port=8080/tcp
```

reload后两种查询都应为yes。

回滚永久规则：

```bash
sudo firewall-cmd --permanent --zone="$ZONE" --remove-port=8080/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --zone="$ZONE" --query-port=8080/tcp
```

Ubuntu再次测试应失败，但Rocky本机访问127.0.0.1仍可成功。

> **验收点**：完成配置、永久化、重载和回滚完整闭环。

### 任务五：来源限制

#### 步骤4：取得管理端地址

在Ubuntu客户端执行：

```bash
ip -brief address
ip route get <ROCKY_IP>
```

记录访问Rocky时实际使用的IPv4地址，写为`<CLIENT_IP>`。该地址是本实验允许访问8080的管理来源。

#### 步骤5：配置rich rule

```bash
CLIENT_IP='<UBUNTU_CLIENT_IP>'
sudo firewall-cmd --zone="$ZONE" --add-rich-rule="rule family=ipv4 source address=$CLIENT_IP/32 port port=8080 protocol=tcp accept"
sudo firewall-cmd --zone="$ZONE" --list-rich-rules
```

从Ubuntu测试8080，应成功。若用Windows宿主机VMnet8地址作为另一个来源进行可选测试，应被拒绝或超时。

不要在同一zone同时保留普通8080端口开放，否则普通规则会允许所有来源，rich rule限制失去意义。

> **验收点**：8080只通过来源规则开放，能够解释为何不能同时保留全局端口规则。

清理运行时rich rule：

```bash
sudo firewall-cmd --zone="$ZONE" --remove-rich-rule="rule family=ipv4 source address=$CLIENT_IP/32 port port=8080 protocol=tcp accept"
```

### 任务六：SELinux状态与上下文

#### 步骤6：检查模式和日志工具

```bash
getenforce
sestatus
command -v semanage || sudo dnf install -y policycoreutils-python-utils
sudo ausearch -m AVC,USER_AVC -ts recent 2>/dev/null | tail -30
```

没有AVC记录不代表命令失败，可能表示近期没有发生SELinux拒绝。

#### 步骤7：建立服务内容目录

```bash
sudo mkdir -p /srv/selinux-lab
printf '<h1>SELinux content</h1>\n' | sudo tee /srv/selinux-lab/index.html
ls -ldZ /srv/selinux-lab
ls -lZ /srv/selinux-lab/index.html
```

#### 步骤8：设置持久上下文规则

```bash
sudo semanage fcontext -a -t httpd_sys_content_t '/srv/selinux-lab(/.*)?'
sudo restorecon -Rv /srv/selinux-lab
ls -ldZ /srv/selinux-lab
ls -lZ /srv/selinux-lab/index.html
```

预期类型为`httpd_sys_content_t`。`chcon`只修改当前标签，可能被`restorecon`恢复；`semanage fcontext`定义持久路径规则。

#### 步骤9：制造错误标签并恢复

```bash
sudo chcon -t user_tmp_t /srv/selinux-lab/index.html
ls -lZ /srv/selinux-lab/index.html
sudo restorecon -v /srv/selinux-lab/index.html
ls -lZ /srv/selinux-lab/index.html
```

> **验收点**：错误类型被`restorecon`恢复为持久规则定义的类型。

### 任务七：保存最终证据

```bash
{
    firewall-cmd --get-active-zones
    firewall-cmd --list-all
    getenforce
    ls -ldZ /srv/selinux-lab
    ls -lZ /srv/selinux-lab/index.html
    semanage fcontext -l | grep '/srv/selinux-lab'
} > ~/m1-project/evidence/lab12-security-after.txt
```

## 七、独立实践

1. 临时启动8081端口服务。
2. 先证明监听存在但外部访问不一定成功。
3. 只允许Ubuntu客户端地址访问8081。
4. 保存规则和客户端验证结果。
5. 删除该运行时规则并证明外部访问再次失败。
6. 为`/srv/web-content`定义持久`httpd_sys_content_t`并使用`restorecon`应用。

## 八、验收标准

- [ ] firewalld保持active，SELinux保持Enforcing。
- [ ] 能指出实验网卡所属zone。
- [ ] 完成运行时端口开放和客户端验证。
- [ ] 完成永久化、reload和回滚。
- [ ] 来源限制规则没有被普通端口规则绕过。
- [ ] 能说明监听、firewalld和SELinux处于不同层。
- [ ] 已设置并验证持久SELinux上下文。
- [ ] 没有使用关闭防火墙、关闭SELinux或chmod 777作为最终方案。
- [ ] 临时规则和服务已清理。

## 九、成果提交

1. `lab12-security-before.txt`和`lab12-security-after.txt`。
2. 8080运行时、永久和回滚证据。
3. rich rule及来源验证。
4. SELinux上下文变更和恢复记录。
5. 独立实践结果。

## 十、常见问题

### Q1：开放端口后外部仍不通

检查服务是否监听虚拟机IP或0.0.0.0、规则是否在正确zone、客户端目标IP是否正确，以及VMware网络是否连通。

### Q2：rich rule配置后所有主机仍能访问

检查是否仍存在普通`--add-port`或service规则。允许规则叠加时，普通开放可能扩大范围。

### Q3：restorecon没有改变类型

先用`semanage fcontext -l`确认路径规则，再确认路径正则和目标文件。仅使用`chcon`不建立持久规则。

### Q4：为什么不把SELinux改为Permissive

Permissive只记录而不阻止，适合受控诊断，不是完成安全配置的标准答案。本实验应在Enforcing下修复标签和策略边界。

## 十一、课后思考与拓展

1. 云安全组已经开放端口，主机firewalld为什么仍可能阻止？
2. 本机curl成功、外部失败时应该优先检查哪些对象？
3. 文件权限正确但Web服务仍被拒绝时，SELinux提供了什么额外线索？

## 十二、环境清理

```bash
test -n "${LAB12_HTTP_PID:-}" && kill "$LAB12_HTTP_PID" 2>/dev/null || true
sudo firewall-cmd --remove-port=8080/tcp 2>/dev/null || true
sudo firewall-cmd --permanent --remove-port=8080/tcp 2>/dev/null || true
sudo firewall-cmd --reload
```

`/srv/selinux-lab`只用于本实验验证持久上下文，实验14会在`rocky-web`创建独立的`/srv/techcorp`规则，两者没有状态依赖。完成截图和证据保存后，先核对对象，再清理本实验路径和规则，避免后续误认为它是Nginx站点：

```bash
sudo find /srv/selinux-lab -maxdepth 2 -ls
sudo semanage fcontext -d '/srv/selinux-lab(/.*)?'
sudo rm -rf /srv/selinux-lab
```
