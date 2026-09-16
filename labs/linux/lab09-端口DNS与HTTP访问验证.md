# 实验9：端口、DNS与HTTP/HTTPS访问验证

> 所属模块：模块二 网络远程管理与基础防护
> 建议学时：2学时
> 实验方式：2～3人小组
> 对应教材：2.2 TCP、UDP、端口与服务监听；2.3 DNS解析与hosts；2.4 HTTP、HTTPS与curl
> 知识前置：实验8三机网络基线和2.2～2.4教材
> 状态依赖：三机静态地址、`/etc/hosts`和`~/m1-project/course-env.sh`已经通过实验8验收
> 建议起点：`Linux-L1`并保留实验8成果
> 项目成果：端口证据表、DNS对照表、HTTP验证记录、TLS证书验证记录

## 一、项目情境

用户报告“服务器网络能通，但网页打不开”。仅执行`ping`不能判断问题发生在服务进程、监听地址、防火墙、名称解析还是HTTP应用层。

本实验使用`rocky-server`运行临时服务，以`ubuntu-client`模拟外部用户，按以下证据链完成验证：

```text
主机身份
→ 名称解析
→ 服务进程
→ 监听地址与端口
→ 防火墙
→ TCP连接
→ HTTP响应
→ TLS证书
```

## 二、实验规则

1. 每个命令单独执行，观察结果后再进入下一步。
2. 服务在Rocky终端A前台运行，检查命令在Rocky终端B执行。
3. Ubuntu客户端使用独立终端访问，不把所有操作粘贴为脚本。
4. 看到失败先记录证据，不立即重装软件或关闭防火墙。
5. 实验结束必须停止临时服务并撤销临时端口规则。

## 三、实验环境

- 服务端：`rocky-server`，Rocky Linux 9。
- 客户端：`ubuntu-client`，Ubuntu 22.04 Desktop。
- `rocky-web`保持开机，用于确认三机环境仍然完整。
- VMware网卡使用实验8确定的NAT网络。
- 需要同时打开Rocky终端A、Rocky终端B和Ubuntu终端。

## 四、任务一：确认实验起点

### 4.1 在rocky-server确认身份

```bash
hostnamectl --static
```

预期输出：

```text
rocky-server
```

### 4.2 检查实验8地址文件

```bash
ls -l ~/m1-project/course-env.sh
```

查看内容：

```bash
cat ~/m1-project/course-env.sh
```

文件应只有`ROCKY_SERVER_IP`、`ROCKY_WEB_IP`和`UBUNTU_CLIENT_IP`三项，并且都已经替换成真实地址。

加载地址：

```bash
source ~/m1-project/course-env.sh
```

核对当前服务器地址：

```bash
printf '%s\n' "$ROCKY_SERVER_IP"
```

### 4.3 检查三机名称解析

```bash
getent hosts rocky-server
```

```bash
getent hosts rocky-web
```

```bash
getent hosts ubuntu-client
```

### 4.4 检查基础互通

在`ubuntu-client`执行：

```bash
ping -c 2 rocky-server
```

如果失败，先回到实验8恢复网络，不进入HTTP实验。

## 五、任务二：记录现有监听

在Rocky终端B查看TCP监听：

```bash
sudo ss -lntp
```

查看UDP监听：

```bash
sudo ss -lnup
```

记录22端口：

```bash
sudo ss -lntp | grep ':22 '
```

填写：

| 项目 | 实际结果 |
|---|---|
| SSH监听协议 | |
| SSH监听地址 | |
| SSH监听端口 | |
| 所属进程 | |

在`ubuntu-client`验证SSH端口的TCP握手：

```bash
nc -vz -w 3 rocky-server 22
```

如果提示`nc: command not found`，先更新索引：

```bash
sudo apt update
```

再安装：

```bash
sudo apt install -y netcat-openbsd
```

## 六、任务三：比较回环监听与全部地址监听

### 6.1 准备HTTP站点

在Rocky终端A创建目录：

```bash
mkdir -p ~/m1-project/http-test
```

打开首页：

```bash
vim ~/m1-project/http-test/index.html
```

写入：

```html
<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>Linux HTTP Test</title></head>
<body><h1>rocky-server HTTP service</h1></body>
</html>
```

保存并退出。

### 6.2 只监听127.0.0.1

在Rocky终端A启动：

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory ~/m1-project/http-test
```

终端A会持续显示访问日志，保持它运行。

在Rocky终端B查看监听：

```bash
ss -lnt
```

应看到`127.0.0.1:8080`，而不是`0.0.0.0:8080`。

本机回环访问：

```bash
curl http://127.0.0.1:8080/
```

在`ubuntu-client`尝试访问：

```bash
curl --connect-timeout 3 http://rocky-server:8080/
```

外部访问应失败，因为服务没有监听Rocky的网卡地址。此时不要修改防火墙。

### 6.3 结束回环服务

回到Rocky终端A按`Ctrl+C`。

在Rocky终端B确认8080监听消失：

```bash
ss -lnt
```

### 6.4 监听所有IPv4地址

在Rocky终端A重新启动：

```bash
python3 -m http.server 8080 --bind 0.0.0.0 --directory ~/m1-project/http-test
```

在Rocky终端B检查：

```bash
ss -lnt
```

应看到`0.0.0.0:8080`。

使用服务器主机名在本机访问：

```bash
curl http://rocky-server:8080/
```

## 七、任务四：验证防火墙与外部访问

### 7.1 记录firewalld状态

在Rocky终端B执行：

```bash
sudo firewall-cmd --state
```

查看活动区域：

```bash
sudo firewall-cmd --get-active-zones
```

查看当前规则：

```bash
sudo firewall-cmd --list-all
```

### 7.2 从Ubuntu测试8080

```bash
nc -vz -w 3 rocky-server 8080
```

如果默认防火墙没有允许8080，测试通常失败。对照Rocky终端A和终端B：

- Python进程仍在运行。
- `ss`显示`0.0.0.0:8080`。
- 外部TCP连接失败。

此时故障范围应缩小到主机防火墙或中间网络策略。

### 7.3 临时允许8080

在Rocky终端B执行：

```bash
sudo firewall-cmd --add-port=8080/tcp
```

确认运行时规则：

```bash
sudo firewall-cmd --query-port=8080/tcp
```

这里不使用`--permanent`。永久规则、来源限制和回滚将在实验12系统学习。

### 7.4 从Ubuntu重新验证

测试TCP：

```bash
nc -vz -w 3 rocky-server 8080
```

访问HTTP：

```bash
curl http://rocky-server:8080/
```

只输出状态码和耗时：

```bash
curl -sS -o /dev/null -w 'code=%{http_code} total=%{time_total}\n' http://rocky-server:8080/
```

预期状态码为200。

## 八、任务五：比较名称解析工具

在`ubuntu-client`查看NSS顺序：

```bash
grep '^hosts:' /etc/nsswitch.conf
```

通过系统解析链查询课程主机：

```bash
getent hosts rocky-server
```

直接向DNS查询：

```bash
dig +short rocky-server
```

如果`dig`命令不存在：

```bash
sudo apt install -y dnsutils
```

实验8中的`rocky-server`通常来自`/etc/hosts`，所以`getent`可以成功，而`dig`可能没有结果。

对公共名称进行系统查询：

```bash
getent hosts mirrors.aliyun.com
```

对公共名称进行DNS查询：

```bash
dig +short mirrors.aliyun.com
```

填写：

| 查询对象 | getent结果 | dig结果 | 结果来源解释 |
|---|---|---|---|
| `rocky-server` | | | |
| `mirrors.aliyun.com` | | | |

外部网络受限时，公共名称失败只作为环境证据，不影响课程主机的局域网验收。

## 九、任务六：验证HTTP状态码

保持Rocky终端A中的HTTP服务运行，在`ubuntu-client`完成。

### 9.1 请求存在的资源

```bash
curl -I http://rocky-server:8080/
```

记录状态码和`Content-Type`。

### 9.2 请求不存在的资源

```bash
curl -sS -o /dev/null -w 'code=%{http_code}\n' http://rocky-server:8080/not-found
```

预期状态码为404。

### 9.3 把HTTP错误作为命令失败

```bash
curl --fail-with-body http://rocky-server:8080/not-found
```

紧接着查看退出状态：

```bash
echo $?
```

这两条命令必须在同一个终端连续执行。说明为什么“HTTP 404”与“TCP连接失败”不是同一类故障。

### 9.4 结束HTTP服务

回到Rocky终端A按`Ctrl+C`。

在Rocky终端B确认：

```bash
ss -lnt
```

8080监听应已经消失。

## 十、拓展任务：建立临时HTTPS服务

本任务用于课后或课堂机动时间，目标是观察TLS和证书验证，不计入2学时核心验收，也不代替模块三的Nginx HTTPS部署。

### 10.1 检查OpenSSL

在`rocky-server`终端A执行：

```bash
openssl version
```

### 10.2 准备TLS目录

```bash
mkdir -p ~/m1-project/tls-test
```

打开测试页面：

```bash
vim ~/m1-project/tls-test/index.html
```

写入：

```html
<h1>rocky-server HTTPS service</h1>
```

### 10.3 生成短期自签名证书

执行下面这一条命令：

```bash
openssl req -x509 -newkey rsa:2048 -nodes -days 7 -keyout ~/m1-project/tls-test/server.key -out ~/m1-project/tls-test/server.crt -subj '/CN=rocky-server' -addext 'subjectAltName=DNS:rocky-server'
```

限制私钥权限：

```bash
chmod 600 ~/m1-project/tls-test/server.key
```

查看证书身份、签发者和有效期：

```bash
openssl x509 -in ~/m1-project/tls-test/server.crt -noout -subject -issuer -dates
```

查看SAN：

```bash
openssl x509 -in ~/m1-project/tls-test/server.crt -noout -ext subjectAltName
```

私钥`server.key`只保存在`rocky-server`，不能上传、提交或复制给客户端。

### 10.4 启动TLS服务

在Rocky终端A进入目录：

```bash
cd ~/m1-project/tls-test
```

启动前台服务：

```bash
openssl s_server -accept 8443 -cert server.crt -key server.key -WWW
```

保持终端A运行。

### 10.5 检查监听并开放临时端口

在Rocky终端B检查：

```bash
ss -lnt
```

临时允许8443：

```bash
sudo firewall-cmd --add-port=8443/tcp
```

确认规则：

```bash
sudo firewall-cmd --query-port=8443/tcp
```

## 十一、拓展任务：对比TLS证书验证

### 11.1 在Ubuntu观察默认验证失败

```bash
curl -v https://rocky-server:8443/index.html
```

自签名证书不在Ubuntu系统信任库中，默认验证应失败。记录错误信息。

### 11.2 仅为诊断跳过验证

```bash
curl -vk https://rocky-server:8443/index.html
```

这一步能够确认TLS服务可以响应，但`-k`不等于修复证书信任问题。

### 11.3 在Rocky显式信任实验文件

在Rocky终端B执行：

```bash
curl --cacert ~/m1-project/tls-test/server.crt https://rocky-server:8443/index.html
```

由于访问名称`rocky-server`与证书SAN一致，并且明确指定了证书文件，本次应通过验证。

填写：

| 测试 | 是否成功 | 证书是否被验证 | 说明 |
|---|---|---|---|
| Ubuntu默认`curl -v` | | 是 | |
| Ubuntu`curl -vk` | | 否 | |
| Rocky`curl --cacert` | | 是 | |

## 十二、任务九：清理与复测

### 12.1 停止HTTPS服务

回到Rocky终端A按`Ctrl+C`。

在Rocky终端B确认8443监听消失：

```bash
ss -lnt
```

### 12.2 删除临时防火墙规则

删除8080运行时规则：

```bash
sudo firewall-cmd --remove-port=8080/tcp
```

删除8443运行时规则：

```bash
sudo firewall-cmd --remove-port=8443/tcp
```

确认8080已经不允许：

```bash
sudo firewall-cmd --query-port=8080/tcp
```

确认8443已经不允许：

```bash
sudo firewall-cmd --query-port=8443/tcp
```

`no`是预期结果。

### 12.3 确认基础环境未被破坏

在`ubuntu-client`确认课程名称仍可解析：

```bash
getent hosts rocky-server
```

确认SSH端口仍可连接：

```bash
nc -vz -w 3 rocky-server 22
```

## 十三、验收标准

- [ ] `rocky-server`和`ubuntu-client`身份正确。
- [ ] 实验8的三机地址文件和名称解析可用。
- [ ] 能从`ss`结果指出协议、监听地址、端口和进程。
- [ ] 已证明`127.0.0.1:8080`不能被Ubuntu直接访问。
- [ ] 已证明`0.0.0.0:8080`与临时防火墙规则共同影响外部访问。
- [ ] 能解释`getent`与`dig`结果不同的原因。
- [ ] 已记录HTTP 200和404，并区分HTTP错误与TCP失败。
- [ ] （拓展）已记录自签名证书默认失败、`-k`跳过验证和`--cacert`显式信任三种结果。
- [ ] 临时服务全部停止。
- [ ] 8080和8443临时防火墙规则全部删除。

## 十四、成果提交

1. SSH和临时服务的端口证据表。
2. 回环监听与全部地址监听的对照记录。
3. 防火墙规则加入前后的Ubuntu访问结果。
4. `getent`与`dig`对照表。
5. HTTP 200、404和curl退出状态记录。
6. 证书主题、有效期和SAN记录。
7. 三种TLS客户端验证结果。
8. 清理后的`ss`和firewalld复测结果。

## 十五、常见问题

### 15.1 Rocky本机成功，Ubuntu访问失败

按顺序检查：

```bash
getent hosts rocky-server
```

```bash
ss -lnt
```

```bash
sudo firewall-cmd --list-all
```

```bash
ip route
```

### 15.2 Python提示端口已被占用

检查8080：

```bash
sudo ss -lntp | grep ':8080 '
```

先找到已有进程的来源，不要直接随机终止进程。

### 15.3 getent成功但dig没有结果

检查NSS顺序和hosts：

```bash
grep '^hosts:' /etc/nsswitch.conf
```

```bash
grep -n 'rocky-server' /etc/hosts
```

这通常是`getent`读取了本地hosts，而`dig`只查询DNS。

### 15.4 curl提示证书不受信任

自签名证书没有公共CA背书，这是本实验的预期现象。生产环境应配置可信证书链，不能把`-k`作为长期方案。

### 15.5 Ctrl+C后端口仍在监听

重新查看所属进程：

```bash
sudo ss -lntp
```

确认自己结束的是正确终端中的前台进程。

## 十六、环境保留

保留以下学习成果：

- `~/m1-project/http-test/index.html`
- `~/m1-project/tls-test/server.crt`
- 实验记录和截图

`server.key`只能留在本机受限目录中，不提交到Git。

不要保留：

- 8080或8443临时监听进程。
- 8080或8443临时firewalld规则。

实验8的静态网络、`/etc/hosts`和`course-env.sh`必须继续保留，供SSH、备份、Nginx和容器课程使用。
