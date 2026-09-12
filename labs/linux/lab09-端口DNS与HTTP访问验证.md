# 实验9：端口、DNS与HTTP/HTTPS访问验证

> 所属模块：模块二 网络、远程管理与基础防护  
> 建议学时：2学时  
> 实验方式：个人  
> 对应教材：《模块二 网络、远程管理与基础防护》第14—16章  
> 前置实验：实验8  
> 项目成果：`rocky-server`临时HTTP/HTTPS测试服务、端口监听，以及`ubuntu-client`名称解析和访问验证记录

## 一、项目情境

网络地址正常不代表应用一定可以访问。你需要启动临时Web服务，从进程、监听地址、端口、名称解析和HTTP响应等角度证明服务工作，并识别Connection refused、timeout和名称解析失败所代表的不同检查方向。

## 二、实验目标

### 1. 知识目标

1. 说明进程、Socket、监听地址、TCP/UDP和端口的关系。
2. 区分`127.0.0.1`、虚拟机IP和`0.0.0.0`监听范围。
3. 说明hosts、DNS客户端、HTTP状态码和TLS证书的基本作用。

### 2. 能力目标

1. 使用`ss`检查监听和进程。
2. 使用`getent`和`/etc/hosts`验证名称解析。
3. 使用`curl`检查HTTP响应头、状态码和HTTPS握手。
4. 根据错误现象判断优先检查层次。

### 3. 素质目标

1. 不把“进程存在”直接等同于“客户端可访问”。
2. 从客户端视角进行最终验证。
3. 实验结束后关闭临时服务和端口规则。

## 三、知识准备

```text
客户端使用名称访问
→ hosts或DNS得到目标IP
→ TCP连接目标IP和端口
→ 服务进程在相应地址监听
→ HTTP返回状态、Header和内容
→ HTTPS还需要TLS握手和证书验证
```

| 现象 | 常见方向 |
|---|---|
| Name or service not known | 名称解析 |
| Connection refused | 目标可达，但没有服务监听或被明确拒绝 |
| Connection timed out | 网络路径、防火墙或目标无响应 |
| HTTP 404 | Web服务可达，但资源不存在 |
| HTTP 500/502 | 服务内部或上游应用异常 |

## 四、实验环境

- `rocky-server`（Rocky Linux 9），静态IP已配置，本实验的临时服务均在此运行。
- 需要`python3`、`curl`和`openssl`。
- 临时HTTP端口8080，临时HTTPS端口8443。
- `ubuntu-client`（Ubuntu 22.04 Desktop）作为正式外部客户端，已在实验8完成三机静态网络配置。

## 五、项目任务

1. 检查现有TCP和UDP监听。
2. 启动临时HTTP服务并验证进程、监听和响应。
3. 配置实验名称并验证hosts解析。
4. 创建自签名证书并启动临时HTTPS服务。
5. 从Rocky本机和Ubuntu客户端分别测试。
6. 清理临时服务、证书和防火墙运行时规则。

## 六、实验步骤

### 任务一：检查现有监听

```bash
sudo ss -lntup
sudo ss -lntp | sed -n '1,30p'
```

`-l`表示监听，`-n`不解析名称，`-t/-u`表示TCP/UDP，`-p`显示进程信息。

> **验收点**：任选一个监听项，指出协议、地址、端口和进程。

### 任务二：启动HTTP服务

#### 步骤1：准备站点

```bash
mkdir -p ~/m1-project/http-test
printf '<h1>Linux HTTP Test</h1>\n' > ~/m1-project/http-test/index.html
```

#### 步骤2：监听所有IPv4地址

```bash
cd ~/m1-project/http-test
python3 -m http.server 8080 --bind 0.0.0.0 > ~/m1-project/logs/http-test.log 2>&1 &
HTTP_PID=$!
printf 'http_pid=%s\n' "$HTTP_PID"
```

验证进程和监听：

```bash
ps -p "$HTTP_PID" -o pid,user,cmd
ss -lntp | grep ':8080'
```

`0.0.0.0:8080`表示接受发往本机任意IPv4地址的连接，不表示互联网一定能访问，还要考虑路由和防火墙。

#### 步骤3：验证HTTP

```bash
curl -I http://127.0.0.1:8080/
curl -s http://127.0.0.1:8080/
curl -s -o /dev/null -w 'status=%{http_code}\n' http://127.0.0.1:8080/missing.html
tail -n 10 ~/m1-project/logs/http-test.log
```

首页应返回200，缺失文件应返回404，日志应记录请求。

> **验收点**：进程、8080监听、200响应、404响应和访问日志互相印证。

### 任务三：名称解析

#### 步骤4：保存并修改hosts

```bash
sudo cp -p /etc/hosts ~/m1-project/backup/hosts.before-lab09
VM_IP=$(ip -4 route get 1.1.1.1 | awk 'NR==1 {for(i=1;i<=NF;i++) if($i=="src") print $(i+1)}')
printf 'vm_ip=%s\n' "$VM_IP"
printf '%s training-web.local\n' "$VM_IP" | sudo tee -a /etc/hosts
getent hosts training-web.local
curl -I http://training-web.local:8080/
```

`getent`按系统实际名称解析顺序查询，通常比只使用`nslookup`更适合验证应用会得到什么结果。

> **验收点**：实验名称解析为虚拟机实际IP，并能用于访问HTTP服务。

### 任务四：临时防火墙验证

如果firewalld正在运行，先查看8080是否开放：

```bash
systemctl is-active firewalld
sudo firewall-cmd --query-port=8080/tcp
```

为了从Ubuntu客户端测试，临时开放运行时端口：

```bash
sudo firewall-cmd --add-port=8080/tcp
sudo firewall-cmd --query-port=8080/tcp
```

这里不使用`--permanent`，详细规则管理在实验12学习。

先在Ubuntu客户端备份hosts并加入实验名称，替换Rocky实际IP：

```bash
sudo cp -p /etc/hosts ~/lab09-ubuntu-hosts.before
echo '<ROCKY_IP> training-web.local' | sudo tee -a /etc/hosts
getent hosts training-web.local
nc -vz -w 3 <ROCKY_IP> 8080
curl -I http://training-web.local:8080/
```

> **验收点**：Ubuntu能够把实验名称解析到Rocky，建立TCP连接并获得HTTP响应。

### 任务五：HTTPS和证书

#### 步骤5：创建实验自签名证书

```bash
mkdir -p ~/m1-project/tls
openssl req -x509 -newkey rsa:2048 -nodes -days 7 \
  -keyout ~/m1-project/tls/training.key \
  -out ~/m1-project/tls/training.crt \
  -subj '/CN=training-web.local'
openssl x509 -in ~/m1-project/tls/training.crt -noout -subject -issuer -dates
```

自签名证书可用于实验加密，但客户端默认不信任，不能冒充公共CA签发的生产证书。

#### 步骤6：启动HTTPS测试服务

```bash
openssl s_server -quiet -www -accept 8443 \
  -cert ~/m1-project/tls/training.crt \
  -key ~/m1-project/tls/training.key \
  > ~/m1-project/logs/https-test.log 2>&1 &
HTTPS_PID=$!
ss -lntp | grep ':8443'
sudo firewall-cmd --add-port=8443/tcp
```

先按默认信任测试：

```bash
curl -I https://training-web.local:8443/
```

预期可能因证书不受信任而失败。仅在本实验中使用`-k`跳过信任校验，观察加密连接和响应：

```bash
curl -kI https://training-web.local:8443/
curl -kv https://training-web.local:8443/ -o /dev/null
```

在Ubuntu客户端重复验证：

```bash
nc -vz -w 3 <ROCKY_IP> 8443
curl -I https://training-web.local:8443/
curl -kI https://training-web.local:8443/
```

第一条`curl`预期因自签名证书不受信任而失败，第二条仅用于确认实验TLS服务能够响应。不要把`-k`作为生产环境证书错误的长期处理办法。

> **验收点**：能够说明Ubuntu默认验证失败的原因，并证明跨主机TLS连接与HTTP响应均已建立。

### 任务六：拒绝连接观察

停止HTTP服务：

```bash
kill "$HTTP_PID"
sleep 1
ss -lntp | grep ':8080' || true
curl --connect-timeout 3 http://127.0.0.1:8080/
printf 'curl_exit_code=%s\n' "$?"
```

本机目标没有服务监听时通常出现Connection refused。

> **验收点**：记录服务运行和停止时的结果差异。

## 七、独立实践

1. 重新在`127.0.0.1:8081`启动HTTP服务。
2. 证明本机可以访问。
3. 从Ubuntu客户端验证无法通过Rocky网卡地址访问，并说明原因。
4. 将监听改为`0.0.0.0:8081`后再次比较。
5. 使用日志证明请求到达服务。

## 八、验收标准

- [ ] 能从监听输出识别协议、地址、端口和进程。
- [ ] HTTP首页返回200，缺失资源返回404。
- [ ] hosts名称解析为实际虚拟机IP。
- [ ] Ubuntu客户端能够解析实验名称并访问Rocky临时HTTP服务。
- [ ] 能区分127.0.0.1与0.0.0.0监听范围。
- [ ] 能说明自签名证书默认不受信任的原因。
- [ ] 能根据拒绝连接判断服务监听方向。
- [ ] 进程、端口、响应和日志证据一致。

## 九、成果提交

1. HTTP/HTTPS进程和监听记录。
2. 200、404和证书错误结果。
3. hosts修改和`getent`结果。
4. Ubuntu客户端的名称解析、端口、HTTP和HTTPS连接结果。
5. 独立实践对比记录。
6. 一张“名称—IP—端口—进程—HTTP响应”关系图。

## 十、常见问题

### Q1：Rocky本机curl成功，Ubuntu访问失败

检查服务是否只监听127.0.0.1，再检查虚拟机IP、VMware网络和firewalld运行时规则。

### Q2：端口已经被占用

```bash
sudo ss -lntp | grep ':8080'
```

先识别占用进程，不要直接杀死未知服务。改用教师指定备用端口。

### Q3：curl提示证书不受信任

自签名证书默认没有受信任CA背书，这是预期现象。`-k`只用于本实验观察，不是生产修复方案。

### Q4：getent解析结果不是hosts中的地址

检查`/etc/nsswitch.conf`中的hosts解析顺序、hosts是否写错，以及是否存在重复名称。

## 十一、课后思考与拓展

1. 服务进程存在为什么仍可能无法从外部访问？
2. Connection refused与timeout分别说明了什么线索？
3. HTTPS提供了哪些保护，为什么不等于网站绝对安全？

## 十二、环境清理

```bash
test -n "${HTTP_PID:-}" && kill "$HTTP_PID" 2>/dev/null || true
test -n "${HTTPS_PID:-}" && kill "$HTTPS_PID" 2>/dev/null || true
sudo cp -p ~/m1-project/backup/hosts.before-lab09 /etc/hosts
sudo firewall-cmd --remove-port=8080/tcp 2>/dev/null || true
sudo firewall-cmd --remove-port=8443/tcp 2>/dev/null || true
ss -lntp | grep -E ':(8080|8443)' || true
```

在Ubuntu客户端恢复hosts：

```bash
test -f ~/lab09-ubuntu-hosts.before && \
  sudo cp -p ~/lab09-ubuntu-hosts.before /etc/hosts
getent hosts training-web.local || true
```

保留站点文件、证书和实验记录，确保临时进程和运行时端口规则已清除。
