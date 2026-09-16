# 实验14：Nginx Web服务部署与故障排查

> 所属模块：模块三 企业服务器部署与综合运维
> 建议学时：4学时
> 实验方式：2～3人小组
> 对应教材：3.1 Nginx Web服务
> 知识前置：HTTP、systemd、firewalld、SELinux和模块二综合排障
> 状态依赖：`rocky-web`静态网络、SSH和安全基线正常；不依赖实验13临时服务
> 建议起点：`Linux-L2`
> 项目成果：TechCorp静态站点、健康检查、反向代理、日志和三类HTTP故障记录

## 一、项目情境

`rocky-web`正式承担Web入口：Nginx提供企业首页和健康检查，并把`/api/`请求转发到本机教学后端。实验20会把上游迁移到`rocky-server`。

## 二、实验规则

1. 所有Nginx配置修改先执行`nginx -t`，通过后才reload。
2. 服务端操作在`rocky-web`，外部验收在`ubuntu-client`。
3. firewalld保持启用，SELinux保持Enforcing。
4. 私有站点使用`/srv/techcorp`，不覆盖默认页面。
5. 每个故障必须保存状态码、配置或日志证据。
6. 本实验成果保留给实验20。

## 三、任务一：安装并记录基线

在`rocky-web`确认身份：

```bash
whoami
```

```bash
hostnamectl --static
```

安装：

```bash
sudo dnf install -y nginx
```

启动：

```bash
sudo systemctl enable --now nginx
```

检查：

```bash
systemctl is-active nginx
```

```bash
systemctl is-enabled nginx
```

```bash
sudo ss -lntp | grep ':80 '
```

创建备份和证据目录：

```bash
mkdir -p ~/m1-project/backup/nginx
```

```bash
mkdir -p ~/m1-project/evidence
```

检查备份：

```bash
ls -ld ~/m1-project/backup/nginx/etc-nginx-before-lab14
```

不存在时创建：

```bash
sudo cp -a /etc/nginx ~/m1-project/backup/nginx/etc-nginx-before-lab14
```

保存完整配置：

```bash
sudo nginx -T > ~/m1-project/evidence/lab14-nginx-before.txt 2>&1
```

## 四、任务二：发布静态站点

创建目录：

```bash
sudo mkdir -p /srv/techcorp/www/private
```

设置所有者：

```bash
sudo chown -R rocky-web:rocky-web /srv/techcorp
```

编辑首页：

```bash
vim /srv/techcorp/www/index.html
```

写入：

```html
<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>TechCorp</title></head>
<body><h1>TechCorp Cloud Operations</h1></body>
</html>
```

检查`semanage`：

```bash
command -v semanage
```

缺少时安装：

```bash
sudo dnf install -y policycoreutils-python-utils
```

查询已有规则：

```bash
sudo semanage fcontext -l | grep '/srv/techcorp/www'
```

没有输出时添加：

```bash
sudo semanage fcontext -a -t httpd_sys_content_t '/srv/techcorp/www(/.*)?'
```

应用标签：

```bash
sudo restorecon -RFv /srv/techcorp/www
```

检查：

```bash
ls -ldZ /srv/techcorp/www
```

## 五、任务三：配置虚拟主机

编辑：

```bash
sudo vim /etc/nginx/conf.d/techcorp.conf
```

写入：

```nginx
server {
    listen 80;
    server_name techcorp.test;
    root /srv/techcorp/www;
    index index.html;

    access_log /var/log/nginx/techcorp-access.log;
    error_log /var/log/nginx/techcorp-error.log warn;

    location = /health {
        default_type text/plain;
        return 200 "ok\n";
    }

    location / {
        try_files $uri $uri/ =404;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

检查语法：

```bash
sudo nginx -t
```

通过后重载：

```bash
sudo systemctl reload nginx
```

检查状态：

```bash
systemctl is-active nginx
```

本机使用Host头验证：

```bash
curl -H 'Host: techcorp.test' http://127.0.0.1/
```

验证健康检查：

```bash
curl -H 'Host: techcorp.test' http://127.0.0.1/health
```

## 六、任务四：开放HTTP并配置客户端名称

查看Rocky活动zone：

```bash
firewall-cmd --get-active-zones
```

记录实际区域后永久允许HTTP：

```text
sudo firewall-cmd --permanent --zone=<实际活动区域> --add-service=http
```

重载：

```bash
sudo firewall-cmd --reload
```

查询：

```text
firewall-cmd --zone=<实际活动区域> --query-service=http
```

在`ubuntu-client`检查hosts备份：

```bash
sudo ls -l /etc/hosts.before-techcorp
```

不存在时创建：

```bash
sudo cp -a /etc/hosts /etc/hosts.before-techcorp
```

编辑hosts：

```bash
sudo vim /etc/hosts
```

加入一行，地址使用实验8中`rocky-web`的真实IPv4：

```text
<rocky-web实际IPv4> techcorp.test
```

验证解析：

```bash
getent hosts techcorp.test
```

访问首页：

```bash
curl --fail http://techcorp.test/
```

访问健康检查：

```bash
curl --fail http://techcorp.test/health
```

## 七、任务五：建立本地教学后端

回到`rocky-web`。

创建目录：

```bash
sudo mkdir -p /srv/techcorp/backend
```

设置所有者：

```bash
sudo chown -R rocky-web:rocky-web /srv/techcorp/backend
```

编辑健康数据：

```bash
vim /srv/techcorp/backend/health.json
```

写入：

```json
{"service":"techcorp-backend","status":"ok"}
```

创建Unit：

```bash
sudo vim /etc/systemd/system/techcorp-backend.service
```

写入：

```ini
[Unit]
Description=TechCorp teaching backend
After=network.target

[Service]
Type=simple
User=rocky-web
ExecStart=/usr/bin/python3 -m http.server 5000 --bind 127.0.0.1 --directory /srv/techcorp/backend
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

加载：

```bash
sudo systemctl daemon-reload
```

启动：

```bash
sudo systemctl enable --now techcorp-backend
```

验证上游：

```bash
curl --fail http://127.0.0.1:5000/health.json
```

允许Nginx连接网络上游：

```bash
sudo setsebool -P httpd_can_network_connect on
```

从Ubuntu验证代理：

```bash
curl --fail http://techcorp.test/api/health.json
```

查看访问日志：

```bash
sudo tail -n 10 /var/log/nginx/techcorp-access.log
```

## 八、任务六：三类HTTP故障

### 8.1 404资源不存在

在Ubuntu执行：

```bash
curl -i http://techcorp.test/not-found
```

查看日志：

```bash
sudo tail -n 10 /var/log/nginx/techcorp-access.log
```

结论：TCP和HTTP均已成功，目标资源不存在。

### 8.2 403目录无索引

访问空目录：

```bash
curl -i http://techcorp.test/private/
```

查看错误日志：

```bash
sudo tail -n 10 /var/log/nginx/techcorp-error.log
```

不要用`chmod 777`处理。空目录没有索引且未启用目录列表时，403是预期。

### 8.3 502上游停止

在Rocky停止后端：

```bash
sudo systemctl stop techcorp-backend
```

在Ubuntu访问：

```bash
curl -i http://techcorp.test/api/health.json
```

查看错误日志：

```bash
sudo tail -n 10 /var/log/nginx/techcorp-error.log
```

恢复后端：

```bash
sudo systemctl start techcorp-backend
```

重新验证：

```bash
curl --fail http://techcorp.test/api/health.json
```

## 九、任务七：配置语法故障

先检查故障备份：

```bash
sudo ls -l /etc/nginx/conf.d/techcorp.conf.before-fault
```

文件不存在时才执行下一条；如果已经存在，不得覆盖：

```bash
sudo cp -a /etc/nginx/conf.d/techcorp.conf /etc/nginx/conf.d/techcorp.conf.before-fault
```

用vim临时删除一处分号：

```bash
sudo vim /etc/nginx/conf.d/techcorp.conf
```

检查：

```bash
sudo nginx -t
```

语法失败时不执行reload。恢复：

```bash
sudo cp -a /etc/nginx/conf.d/techcorp.conf.before-fault /etc/nginx/conf.d/techcorp.conf
```

再次检查：

```bash
sudo nginx -t
```

通过后重载：

```bash
sudo systemctl reload nginx
```

## 十、最终验收

在Ubuntu逐条执行：

```bash
curl --fail http://techcorp.test/
```

```bash
curl --fail http://techcorp.test/health
```

```bash
curl --fail http://techcorp.test/api/health.json
```

在Rocky检查：

```bash
sudo nginx -t
```

```bash
systemctl is-active nginx
```

```bash
systemctl is-active techcorp-backend
```

```bash
getenforce
```

## 十一、验收标准

- [ ] Nginx为active和enabled。
- [ ] `techcorp.test`解析为`rocky-web`真实地址。
- [ ] 首页、`/health`和`/api/health.json`均成功。
- [ ] 站点目录具有持久`httpd_sys_content_t`标签。
- [ ] HTTP服务已加入实际活动zone的永久配置。
- [ ] 每次配置修改均先通过`nginx -t`。
- [ ] 404、403、502均有状态码和日志解释。
- [ ] 配置语法故障未加载到运行服务。
- [ ] firewalld保持active，SELinux保持Enforcing。

## 十二、成果提交

1. `techcorp.conf`。
2. 首页和后端健康数据。
3. `nginx -T`关键配置。
4. Ubuntu三条最终curl结果。
5. 404、403、502故障记录。
6. 配置语法故障与恢复记录。
7. firewalld、SELinux和服务状态。

## 十三、环境保留

保留Nginx、`/srv/techcorp`、`techcorp.conf`、HTTP防火墙服务、`techcorp.test`客户端解析和`techcorp-backend.service`，供实验20继续使用。

私有后端只监听`127.0.0.1:5000`，不为5000开放firewalld规则。
