# 实验12：firewalld与SELinux基础防护

> 所属模块：模块二 网络远程管理与基础防护
> 建议学时：4学时
> 实验方式：2～3人小组
> 对应教材：2.9 firewalld基础；2.10 firewalld规则、来源限制与回滚；2.11 SELinux与主机基础防护
> 知识前置：实验8网络、实验9端口证据链、实验10 SSH回退入口
> 状态依赖：`rocky-server`的firewalld和SELinux保持正常基线；不依赖实验11备份文件
> 建议起点：`Linux-L1`并保留实验8和实验10成果
> 项目成果：防火墙变更单、运行时与永久规则证据、来源限制证据、SELinux标签恢复记录

## 一、项目情境

服务器需要允许管理人员访问指定Web端口，但不能把所有端口对所有来源开放。本实验完成一次最小开放、持久化、来源限制和回滚，同时在独立目录中验证SELinux持久标签。

## 二、实验规则

1. 保持firewalld运行，不能通过停止防火墙完成验收。
2. 保持SELinux为Enforcing，不能用Permissive作为最终修复。
3. 所有网络修改在VMware控制台中执行，并保留SSH回退入口。
4. 规则中的zone和客户端地址必须来自实际环境。
5. 每条命令单独执行，观察结果后再继续。
6. 实验结束必须删除8080实验规则并停止临时服务。

## 三、任务一：记录安全基线

在`rocky-server`执行。

确认身份：

```bash
hostnamectl --static
```

检查firewalld：

```bash
systemctl is-active firewalld
```

```bash
firewall-cmd --state
```

检查活动zone：

```bash
firewall-cmd --get-active-zones
```

检查默认zone：

```bash
firewall-cmd --get-default-zone
```

检查SELinux：

```bash
getenforce
```

```bash
sestatus
```

填写：

| 项目 | 实际值 |
|---|---|
| 出口网卡 | |
| 活动zone | |
| 默认zone | |
| firewalld状态 | |
| SELinux模式 | |

后续所有`<实际活动区域>`必须替换为本表记录的zone。

保存运行时规则：

```text
firewall-cmd --zone=<实际活动区域> --list-all > ~/m1-project/evidence/lab12-firewall-runtime-before.txt
```

保存永久规则：

```text
firewall-cmd --permanent --zone=<实际活动区域> --list-all > ~/m1-project/evidence/lab12-firewall-permanent-before.txt
```

## 四、任务二：准备8080测试服务

打开Rocky终端A和终端B。

在终端A创建目录：

```bash
mkdir -p ~/m1-project/firewall-test
```

编辑首页：

```bash
vim ~/m1-project/firewall-test/index.html
```

写入：

```html
<h1>firewalld source test</h1>
```

在终端A启动前台服务：

```bash
python3 -m http.server 8080 --bind 0.0.0.0 --directory ~/m1-project/firewall-test
```

保持终端A运行。

在终端B检查监听：

```bash
ss -lnt
```

在Rocky本机访问：

```bash
curl http://127.0.0.1:8080/
```

在`ubuntu-client`访问：

```bash
curl --connect-timeout 3 http://rocky-server:8080/
```

如果外部访问已经成功，说明存在允许规则。先使用`--list-all`查明并记录来源，不能直接进入后续对照。

## 五、任务三：运行时规则

### 5.1 添加运行时端口

在Rocky终端B使用实际zone：

```text
sudo firewall-cmd --zone=<实际活动区域> --add-port=8080/tcp
```

查询：

```text
firewall-cmd --zone=<实际活动区域> --query-port=8080/tcp
```

查看端口列表：

```text
firewall-cmd --zone=<实际活动区域> --list-ports
```

### 5.2 从Ubuntu验证

```bash
nc -vz -w 3 rocky-server 8080
```

```bash
curl http://rocky-server:8080/
```

### 5.3 比较永久配置

```text
firewall-cmd --permanent --zone=<实际活动区域> --query-port=8080/tcp
```

此时运行时通常为`yes`，永久配置为`no`。

### 5.4 reload观察

```bash
sudo firewall-cmd --reload
```

再次查询运行时：

```text
firewall-cmd --zone=<实际活动区域> --query-port=8080/tcp
```

只存在于运行时的8080规则应消失。

## 六、任务四：永久规则与回滚

### 6.1 写入永久配置

```text
sudo firewall-cmd --permanent --zone=<实际活动区域> --add-port=8080/tcp
```

加载：

```bash
sudo firewall-cmd --reload
```

查询运行时：

```text
firewall-cmd --zone=<实际活动区域> --query-port=8080/tcp
```

查询永久配置：

```text
firewall-cmd --permanent --zone=<实际活动区域> --query-port=8080/tcp
```

从Ubuntu再次访问，预期成功。

### 6.2 回滚普通端口规则

删除永久规则：

```text
sudo firewall-cmd --permanent --zone=<实际活动区域> --remove-port=8080/tcp
```

加载：

```bash
sudo firewall-cmd --reload
```

确认运行时和永久配置均为`no`。

## 七、任务五：来源限制

### 7.1 取得Ubuntu实际地址

在`ubuntu-client`执行：

```bash
ip -brief address
```

记录VMnet8网卡上的IPv4地址，不使用`127.0.0.1`，也不包含`/24`：

| 项目 | 实际值 |
|---|---|
| Ubuntu网卡 | |
| Ubuntu IPv4 | |
| rich rule使用的来源 | 实际IPv4/32 |

### 7.2 确认不存在普通开放

在Rocky终端B执行：

```text
firewall-cmd --zone=<实际活动区域> --query-port=8080/tcp
```

必须为`no`。

### 7.3 添加运行时rich rule

把zone和IP替换成实际值：

```text
sudo firewall-cmd --zone=<实际活动区域> --add-rich-rule='rule family="ipv4" source address="<Ubuntu实际IPv4>/32" port port="8080" protocol="tcp" accept'
```

查看完整规则：

```text
firewall-cmd --zone=<实际活动区域> --list-rich-rules
```

### 7.4 验证允许来源

在Ubuntu执行：

```bash
curl http://rocky-server:8080/
```

小组中另一位同学可以从不同地址测试8080，预期不应被这条规则允许。

### 7.5 永久保存并复测

使用完全相同的规则写入永久配置：

```text
sudo firewall-cmd --permanent --zone=<实际活动区域> --add-rich-rule='rule family="ipv4" source address="<Ubuntu实际IPv4>/32" port port="8080" protocol="tcp" accept'
```

重载：

```bash
sudo firewall-cmd --reload
```

再次从Ubuntu访问，预期成功。

### 7.6 回滚rich rule

删除永久规则：

```text
sudo firewall-cmd --permanent --zone=<实际活动区域> --remove-rich-rule='rule family="ipv4" source address="<Ubuntu实际IPv4>/32" port port="8080" protocol="tcp" accept'
```

重载：

```bash
sudo firewall-cmd --reload
```

确认rich rule已经消失：

```text
firewall-cmd --zone=<实际活动区域> --list-rich-rules
```

## 八、任务六：SELinux状态与持久标签

### 8.1 安装管理工具

```bash
command -v semanage
```

缺少时安装：

```bash
sudo dnf install -y policycoreutils-python-utils
```

### 8.2 创建独立实验目录

```bash
sudo mkdir -p /srv/selinux-lab
```

创建文件：

```bash
sudo touch /srv/selinux-lab/index.html
```

查看当前标签：

```bash
ls -ldZ /srv/selinux-lab
```

```bash
ls -lZ /srv/selinux-lab/index.html
```

### 8.3 查询现有持久规则

```bash
sudo semanage fcontext -l | grep '/srv/selinux-lab'
```

没有输出时，添加规则：

```bash
sudo semanage fcontext -a -t httpd_sys_content_t '/srv/selinux-lab(/.*)?'
```

如果规则已存在，应核对类型，不要重复添加。

### 8.4 应用持久标签

```bash
sudo restorecon -RFv /srv/selinux-lab
```

检查：

```bash
ls -lZ /srv/selinux-lab/index.html
```

预期类型为`httpd_sys_content_t`。

## 九、任务七：制造错误标签并恢复

### 9.1 制造当前标签错误

```bash
sudo chcon -t user_home_t /srv/selinux-lab/index.html
```

查看：

```bash
ls -lZ /srv/selinux-lab/index.html
```

### 9.2 查询策略默认值

```bash
matchpathcon /srv/selinux-lab/index.html
```

当前标签与默认值应不同。

### 9.3 使用restorecon恢复

```bash
sudo restorecon -v /srv/selinux-lab/index.html
```

再次查看：

```bash
ls -lZ /srv/selinux-lab/index.html
```

应恢复为`httpd_sys_content_t`。这证明`chcon`只改变当前标签，`semanage fcontext`建立的持久映射决定`restorecon`结果。

### 9.4 检查AVC日志

```bash
sudo ausearch -m AVC,USER_AVC -ts recent
```

本任务主要验证标签持久性，不保证一定产生AVC。没有AVC时如实记录，不能伪造拒绝日志。

## 十、任务八：清理与最终检查

### 10.1 停止临时HTTP服务

回到Rocky终端A按`Ctrl+C`。

确认8080监听消失：

```bash
ss -lnt
```

### 10.2 确认没有遗留防火墙规则

```text
firewall-cmd --zone=<实际活动区域> --query-port=8080/tcp
```

```text
firewall-cmd --permanent --zone=<实际活动区域> --query-port=8080/tcp
```

```text
firewall-cmd --zone=<实际活动区域> --list-rich-rules
```

8080普通规则应为`no`，实验rich rule不应存在。

### 10.3 清理SELinux实验规则

删除持久映射：

```bash
sudo semanage fcontext -d '/srv/selinux-lab(/.*)?'
```

删除实验目录前核对：

```bash
sudo find /srv/selinux-lab -maxdepth 2 -ls
```

确认只有实验文件后删除：

```bash
sudo rm -rf /srv/selinux-lab
```

### 10.4 确认安全基线

```bash
systemctl is-active firewalld
```

```bash
getenforce
```

预期分别为`active`和`Enforcing`。

## 十一、验收标准

- [ ] 实际活动zone和网卡已经记录。
- [ ] 8080运行时规则、reload消失现象已验证。
- [ ] 8080永久规则在reload后仍生效，并已回滚。
- [ ] 来源限制使用Ubuntu真实IPv4/32。
- [ ] 没有同时保留面向所有来源的普通8080规则。
- [ ] rich rule已经完成添加、持久化、验证和回滚。
- [ ] SELinux始终保持Enforcing。
- [ ] `/srv/selinux-lab`持久规则和`restorecon`结果已验证。
- [ ] 错误标签已经恢复为`httpd_sys_content_t`。
- [ ] 临时服务、8080规则和SELinux实验目录均已清理。

## 十二、成果提交

1. 防火墙基线表。
2. 运行时与永久8080规则对照。
3. reload前后结果。
4. 来源限制变更单和Ubuntu访问结果。
5. SELinux模式、当前标签、默认标签和恢复结果。
6. 清理后的firewalld与SELinux状态。

## 十三、常见问题

### 13.1 添加规则后外部仍不通

依次检查`ss`监听、实际活动zone、规则、客户端地址和路由。

### 13.2 rich rule存在但所有来源都能访问

检查是否仍有普通8080端口或包含8080的service。

### 13.3 reload后规则消失

说明规则只加入运行时，没有写入永久配置。

### 13.4 restorecon没有改变标签

查询持久规则：

```bash
sudo semanage fcontext -l | grep '/srv/selinux-lab'
```

检查正则是否覆盖目标路径。

### 13.5 为什么不关闭SELinux

关闭SELinux只是移除了保护层，没有修复错误标签、应用配置或策略需求。本实验要求在Enforcing下完成恢复。

## 十四、环境保留

保留firewalld服务、SELinux Enforcing状态、SSH规则和实验10远程管理入口。

不保留8080实验规则、临时HTTP进程和`/srv/selinux-lab`。模块三会在`rocky-web`为Nginx建立独立的正式目录和SELinux规则。
