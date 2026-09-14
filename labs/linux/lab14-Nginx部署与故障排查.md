# 实验14：Nginx Web服务部署与故障排查

> 所属模块：模块三 企业服务部署与综合运维  
> 建议学时：4学时  
> 实验方式：个人  
> 对应教材：《模块三 企业服务部署与综合运维》第25章  
> 知识前置：模块二的服务、端口、HTTP、firewalld、SELinux和排障方法\
> 状态依赖：`Linux-L2`中的`rocky-web`静态网络、SSH和安全基线；不依赖实验13在`rocky-server`创建的临时服务\
> 建议起点：`Linux-L2`\
> 项目成果：TechCorp静态站点、虚拟主机、反向代理、访问日志及403/404/502故障记录

## 一、项目情境

TechCorp需要在专用Web服务器`rocky-web`发布企业官网，并由Nginx把`/api/`请求转发给测试应用。你需要把此前在`rocky-server`学到的网络、SSH、systemd、firewalld和SELinux方法迁移到Web角色，再完成配置和故障排查。

## 二、实验目标

### 1. 知识目标

1. 说明Web客户端、Nginx主进程、工作进程、站点目录、虚拟主机和日志的关系。
2. 说明`server_name`、`location`、`root`、`try_files`和`proxy_pass`的基本作用。
3. 区分403、404和502所处的故障层次。

### 2. 能力目标

1. 安装并使用systemd管理Nginx。
2. 使用独立目录发布静态网站并正确设置SELinux上下文。
3. 配置基于Host的虚拟主机和本地反向代理。
4. 使用`nginx -t`、`curl`、端口和日志完成验证与排障。

### 3. 素质目标

1. 修改配置前备份，应用前先做语法检查。
2. 不使用关闭SELinux或无限扩大权限解决Web访问问题。
3. 从客户端功能、服务状态、端口和日志多方面验收。

## 三、知识准备

```text
浏览器或curl
→ 目标IP的80端口
→ Nginx根据Host选择server
→ 根据URI选择location
→ 读取静态文件或转发给上游
→ 返回HTTP状态并写入access/error日志
```

| 状态码 | 本实验中的典型含义 | 优先检查 |
|---|---|---|
| 200 | 请求正常 | 内容是否符合预期 |
| 403 | 请求到达Nginx，但资源访问被拒绝 | 目录首页、权限、SELinux、规则 |
| 404 | Nginx可达，但目标资源不存在 | URI、root、文件路径 |
| 502 | Nginx作为代理无法获得有效上游响应 | 上游进程、地址、端口、SELinux |

复习服务状态与日志取证时，可打开[systemd服务状态、依赖与journal排障动画](../../animations/04-systemd-journal/index.html)的“运行与自启”和“日志证据链”。Nginx配置修改后应先执行配置语法检查，再根据`CanReload`和服务能力选择reload或restart。

复习HTTP请求路径与状态码时，打开[Socket、TCP、HTTP与TLS端到端访问动画](../../animations/06-socket-tcp-http-tls/index.html)的“HTTP消息”。重点观察Host如何选择虚拟主机、URI如何进入location，以及404和502分别把排障方向指向哪里。

配置非标准站点目录和反向代理前，打开[SELinux双重判定、上下文与AVC排障动画](../../animations/10-selinux-dac-context-avc/index.html)的“标签持久化”和“AVC排障”。区分站点文件类型`httpd_sys_content_t`与允许Web进程连接上游的策略能力，不能用`chmod 777`或关闭SELinux代替定位。

进入Nginx配置任务前打开[Nginx请求路由、静态资源与反向代理动画](../../animations/12-nginx-request-routing-proxy/index.html)。依次完成“监听与Server”“Location与路径”“反向代理”和“状态码与日志”，每一步先写出预期server、location、文件或上游路径，再执行`nginx -T`和`curl`验证。

## 四、实验环境

- `rocky-web`运行Rocky Linux 9，使用同名用户登录并具备sudo权限。
- 实验1、8准备的`ubuntu-client`，能够解析并访问`rocky-web`。
- 使用教师验证过的软件源或离线RPM。
- 端口80用于Nginx，5000用于仅本机访问的测试后端。
- firewalld保持启用，SELinux保持Enforcing。
- 虚拟主机名称：`techcorp.test`。`.test`是保留测试域，避免与mDNS使用的`.local`混淆。

## 五、项目任务

1. 核对当前机器确实是`rocky-web`，复查网络、SSH、防火墙和SELinux基线。
2. 安装并检查Nginx。
3. 建立TechCorp站点和正确SELinux上下文。
4. 配置虚拟主机并从`rocky-web`本机和`ubuntu-client`验证。
5. 启动本地后端并配置`/api/`反向代理。
6. 制造和识别403、404、502。
7. 保存配置、日志证据和故障报告。

## 六、实验步骤

### 任务一：安装和建立基线

#### 步骤1：确认端口和旧环境

```bash
test "$(whoami)" = 'rocky-web' && echo USER_PASS || echo USER_FAIL
test "$(hostnamectl --static)" = 'rocky-web' && echo HOST_PASS || echo HOST_FAIL
ip -brief address
getenforce
rpm -q nginx || true
sudo ss -lntp | grep ':80 ' || true
test -d /etc/nginx && sudo find /etc/nginx -maxdepth 2 -type f -print || true
```

如果80端口已被其他服务占用，先确认服务来源，不要直接终止未知进程。

#### 步骤2：安装Nginx

```bash
sudo dnf install -y nginx
nginx -v
rpm -q nginx
sudo systemctl enable --now nginx
systemctl is-active nginx
systemctl is-enabled nginx
sudo ss -lntp | grep ':80 '
```

课程使用教师统一验证的软件源。不同仓库的Nginx包在默认站点和配置布局上可能略有差异，不能混用多套仓库后照抄路径。

> **验收点**：nginx为active和enabled，TCP 80处于监听状态。

#### 步骤3：备份配置基线

```bash
mkdir -p ~/m1-project/backup/nginx ~/m1-project/evidence ~/m1-project/logs
sudo cp -a /etc/nginx/. ~/m1-project/backup/nginx/
sudo nginx -T > ~/m1-project/evidence/lab14-nginx-before.txt 2>&1
```

`nginx -T`检查并输出完整合并配置，便于确认实际生效内容。

### 任务二：发布静态站点

#### 步骤4：创建站点文件

```bash
sudo mkdir -p /srv/techcorp/www/assets /srv/techcorp/www/private
sudo tee /srv/techcorp/www/index.html > /dev/null <<'HTML'
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>TechCorp</title>
  <style>body{font-family:sans-serif;max-width:760px;margin:50px auto;color:#263238}code{background:#eef;padding:3px}</style>
</head>
<body>
  <h1>TechCorp Linux Service</h1>
  <p id="status">NGINX_STATIC_OK</p>
  <p>API入口：<code>/api/</code></p>
</body>
</html>
HTML
printf 'body { background: #f7f9fc; }\n' | sudo tee /srv/techcorp/www/assets/site.css
sudo chown -R root:root /srv/techcorp
sudo find /srv/techcorp -type d -exec chmod 755 {} +
sudo find /srv/techcorp -type f -exec chmod 644 {} +
```

#### 步骤5：设置持久SELinux上下文

```bash
command -v semanage || sudo dnf install -y policycoreutils-python-utils
sudo semanage fcontext -a -t httpd_sys_content_t '/srv/techcorp/www(/.*)?' 2>/dev/null || \
  sudo semanage fcontext -m -t httpd_sys_content_t '/srv/techcorp/www(/.*)?'
sudo restorecon -Rv /srv/techcorp/www
ls -ldZ /srv/techcorp/www
ls -lZ /srv/techcorp/www/index.html
```

> **验收点**：站点文件传统权限合理，SELinux类型为`httpd_sys_content_t`。

### 任务三：配置虚拟主机

#### 步骤6：创建配置

```bash
sudo tee /etc/nginx/conf.d/techcorp.conf > /dev/null <<'NGINX'
server {
    listen 80;
    server_name techcorp.test;

    root /srv/techcorp/www;
    index index.html;

    access_log /var/log/nginx/techcorp-access.log;
    error_log  /var/log/nginx/techcorp-error.log warn;

    location / {
        try_files $uri $uri/ =404;
    }

    location = /health {
        default_type text/plain;
        return 200 "ok\n";
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX
```

#### 步骤7：检查并重载

```bash
sudo nginx -t
sudo systemctl reload nginx
systemctl is-active nginx
curl -s -H 'Host: techcorp.test' http://127.0.0.1/ | grep NGINX_STATIC_OK
curl --fail -H 'Host: techcorp.test' http://127.0.0.1/health
```

如果`nginx -t`失败，不执行reload。根据错误中的文件和行号修复。

> **验收点**：语法检查成功，通过Host头访问得到`NGINX_STATIC_OK`。

#### 步骤8：开放HTTP并从Ubuntu客户端验证

```bash
IFACE=$(ip route show default | awk 'NR==1 {print $5}')
ZONE=$(firewall-cmd --get-zone-of-interface="$IFACE" 2>/dev/null)
if [[ -z "$ZONE" || "$ZONE" == 'no zone' ]]; then ZONE=$(firewall-cmd --get-default-zone); fi
printf '%s\n' "$ZONE" > ~/m1-project/backup/nginx/firewall-zone.txt
sudo firewall-cmd --zone="$ZONE" --add-service=http --permanent
sudo firewall-cmd --reload
sudo firewall-cmd --zone="$ZONE" --query-service=http
```

在`ubuntu-client`先直接携带Host头验证：

```bash
source ~/m1-project/course-env.sh
ROCKY_IP="$ROCKY_WEB_IP"
curl -i -H 'Host: techcorp.test' "http://$ROCKY_IP/"
curl --fail -H 'Host: techcorp.test' "http://$ROCKY_IP/health"
```

再检查`ubuntu-client`的hosts文件中`rocky-web`和`techcorp.test`是否指向同一地址：

```bash
source ~/m1-project/course-env.sh
mkdir -p ~/m1-project/backup/nginx
test -f ~/m1-project/backup/nginx/ubuntu-hosts.before-techcorp || \
  sudo cp -p /etc/hosts ~/m1-project/backup/nginx/ubuntu-hosts.before-techcorp
sudo sed -i '/[[:space:]]techcorp\.test\([[:space:]]\|$\)/d' /etc/hosts
printf '%s %s\n' "$ROCKY_WEB_IP" 'techcorp.test' | sudo tee -a /etc/hosts
```

验证系统解析和HTTP访问：

```bash
getent hosts techcorp.test
curl --fail http://techcorp.test/
curl --fail http://techcorp.test/health
```

若教师需要图形浏览器展示，也可以在Windows宿主机配置同名hosts记录后访问，但Ubuntu命令行结果是本实验的正式客户端证据。

> **验收点**：`ubuntu-client`能够访问TechCorp页面和`/health`，Nginx访问日志出现客户端地址。

### 任务四：配置反向代理

#### 步骤9：准备本地后端

```bash
mkdir -p ~/m1-project/backend
printf '{"service":"techcorp-api","status":"BACKEND_OK"}\n' > ~/m1-project/backend/index.html
cd ~/m1-project/backend
python3 -m http.server 5000 --bind 127.0.0.1 > ~/m1-project/logs/backend.log 2>&1 &
BACKEND_PID=$!
printf '%s\n' "$BACKEND_PID" > ~/m1-project/backend/backend.pid
ss -lntp | grep ':5000'
curl -s http://127.0.0.1:5000/
```

5000只监听127.0.0.1，不向外部网络直接发布。

#### 步骤10：允许Web进程连接上游

查看SELinux布尔值：

```bash
getsebool httpd_can_network_connect
```

为反向代理开启持久允许：

```bash
sudo setsebool -P httpd_can_network_connect on
getsebool httpd_can_network_connect
```

该布尔值允许受httpd策略管理的Web进程发起网络连接，因此仍应通过监听地址和防火墙限制上游暴露范围。

#### 步骤11：验证代理

```bash
curl -s -H 'Host: techcorp.test' http://127.0.0.1/api/
tail -n 10 /var/log/nginx/techcorp-access.log
tail -n 10 ~/m1-project/logs/backend.log
```

预期响应包含`BACKEND_OK`，两个日志都出现请求。

> **验收点**：客户端只访问80端口，Nginx成功转发到本机5000端口。

### 任务五：HTTP故障排查

#### 步骤12：404资源不存在

```bash
curl -s -o /dev/null -w 'status=%{http_code}\n' -H 'Host: techcorp.test' http://127.0.0.1/not-found.html
tail -n 5 /var/log/nginx/techcorp-access.log
tail -n 10 /var/log/nginx/techcorp-error.log
```

预期状态为404。Nginx和网络均可用，只是目标资源不存在。

#### 步骤13：403目录访问

`private`目录存在但没有首页，且默认不允许列目录：

```bash
curl -s -o /dev/null -w 'status=%{http_code}\n' -H 'Host: techcorp.test' http://127.0.0.1/private/
tail -n 10 /var/log/nginx/techcorp-error.log
```

通常返回403，并在错误日志中说明目录索引被禁止。

#### 步骤14：502上游失败

```bash
BACKEND_PID=$(cat ~/m1-project/backend/backend.pid)
ps -p "$BACKEND_PID" -o args= | grep -Fq 'http.server 5000' && kill "$BACKEND_PID"
sleep 1
ss -lntp | grep ':5000' || true
curl -s -o /dev/null -w 'status=%{http_code}\n' -H 'Host: techcorp.test' http://127.0.0.1/api/
tail -n 10 /var/log/nginx/techcorp-error.log
```

预期返回502，错误日志通常包含连接127.0.0.1:5000失败。

重新启动后端并复测：

```bash
cd ~/m1-project/backend
python3 -m http.server 5000 --bind 127.0.0.1 > ~/m1-project/logs/backend.log 2>&1 &
BACKEND_PID=$!
printf '%s\n' "$BACKEND_PID" > ~/m1-project/backend/backend.pid
curl -s -H 'Host: techcorp.test' http://127.0.0.1/api/
```

> **验收点**：分别提供403、404、502的状态、日志、根因和恢复结果。

### 任务六：保存最终证据

```bash
{
    nginx -v 2>&1
    systemctl is-active nginx
    sudo nginx -t 2>&1
    sudo ss -lntp | grep -E ':(80|5000) '
    firewall-cmd --query-service=http
    getenforce
    ls -ldZ /srv/techcorp/www
    curl -s -o /dev/null -w 'home=%{http_code}\n' -H 'Host: techcorp.test' http://127.0.0.1/
    curl -s -o /dev/null -w 'api=%{http_code}\n' -H 'Host: techcorp.test' http://127.0.0.1/api/
} > ~/m1-project/evidence/lab14-nginx-final.txt
```

## 七、独立实践

1. 新增`status.techcorp.test`虚拟主机，站点目录为`/srv/techcorp/status`。
2. 页面必须包含`STATUS_SITE_OK`。
3. 设置正确传统权限和SELinux上下文。
4. 使用`curl -H 'Host: status.techcorp.test'`验证。
5. 为该虚拟主机使用独立访问日志。
6. 故意写错一次配置，在不影响现有服务的情况下通过`nginx -t`发现并修复。

## 八、验收标准

- [ ] Nginx已安装、运行并开机自启。
- [ ] 修改前已保存完整配置基线。
- [ ] TechCorp站点目录、权限和SELinux上下文正确。
- [ ] 配置通过`nginx -t`后才重载。
- [ ] `rocky-web`本机和`ubuntu-client`均能访问虚拟主机与健康页。
- [ ] 5000端口只监听127.0.0.1。
- [ ] `/api/`反向代理返回`BACKEND_OK`。
- [ ] 403、404和502均有状态与日志证据。
- [ ] 故障修复后首页和API均恢复200。
- [ ] 独立虚拟主机完成并使用独立日志。

## 九、成果提交

1. `/etc/nginx/conf.d/techcorp.conf`。
2. TechCorp站点文件。
3. `lab14-nginx-before.txt`和`lab14-nginx-final.txt`。
4. Ubuntu客户端的名称解析、首页和健康页访问验证。
5. 403、404、502三份简短故障记录。
6. 独立虚拟主机配置和日志。

## 十、常见问题

### Q1：配置文件修改后服务启动失败

使用`sudo nginx -t`取得准确文件和行号，修复后再reload。不要反复restart。

### Q2：文件权限正确但仍然403

检查父目录执行权限、SELinux上下文和错误日志：

```bash
namei -l /srv/techcorp/www/index.html
ls -lZ /srv/techcorp/www/index.html
sudo ausearch -m AVC -ts recent | tail -30
```

### Q3：代理返回502

检查上游服务、127.0.0.1:5000监听、`proxy_pass`和Nginx错误日志，再检查SELinux布尔值。

### Q4：直接访问IP显示默认页面

本虚拟主机按`server_name techcorp.test`匹配。使用正确Host头或本地域名，不要把默认站点误判为配置未加载。

## 十一、课后思考与拓展

1. 修改配置后为什么优先reload而不是restart？
2. 反向代理为什么不需要把后端5000端口开放给外部客户端？
3. 403、404和502分别能证明网络路径中的哪些部分已经正常？

## 十二、环境保留

保留Nginx、站点、HTTP防火墙服务和后端文件，供实验20使用。实验结束或虚拟机关机前终止临时后端：

```bash
if test -f ~/m1-project/backend/backend.pid; then
  BACKEND_PID=$(cat ~/m1-project/backend/backend.pid)
  ps -p "$BACKEND_PID" -o args= 2>/dev/null | grep -Fq 'http.server 5000' && kill "$BACKEND_PID" || true
fi
```
