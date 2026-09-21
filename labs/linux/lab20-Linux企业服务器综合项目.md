# 实验20：Linux企业服务器综合部署与故障排查

> 所属模块：模块三 企业服务器部署与综合运维
> 建议学时：6学时
> 实验方式：个人完成，小组内交叉验收与故障设置
> 对应教材：3.7 综合部署、验收与故障排查
> 知识前置：实验1—19的核心知识、服务成果、备份恢复、Git和巡检方法
> 状态依赖：`Linux-L3`，即实验14—19形成的Nginx、MySQL、MongoDB、Redis、Git、备份和巡检成果
> 建议起点：三台虚拟机固定身份与网络正常，实验19结束后建立的`Linux-L3`快照
> 项目成果：TechCorp三机业务环境、来源受限后端、隔离恢复证据、Git版本、巡检结果、三项故障记录和`Linux-L4`

## 一、项目情境

TechCorp需要交付一套小型Linux业务环境。此前各实验分别完成了文件、账号、服务、网络、安全、Web、数据库、Git和Shell任务。本实验不从空白系统重装软件，而是检查、整合、验证和交付已有成果。

最终要求：

- `ubuntu-client`能够SSH管理两台Rocky并访问统一Web入口；
- `rocky-web`使用Nginx提供首页、健康页和反向代理；
- `rocky-server`使用systemd运行课程后端；
- 5000端口只允许`rocky-web`访问；
- MySQL、MongoDB和Redis只允许`rocky-server`本机访问；
- 两台Rocky保持firewalld运行和SELinux Enforcing；
- 数据备份恢复到隔离目标后通过检查；
- 实验19巡检脚本继续使用并纳入后端检查；
- 另一名学习者能够按照交付文档复核结果。

## 二、实验目标

### 1. 知识目标

1. 说明客户端、Web入口、后端和数据服务的依赖关系。
2. 说明监听地址、firewalld、SELinux、认证和授权的不同作用。
3. 说明可运行、可访问、可使用、可保护、可恢复和可交付的区别。
4. 说明Linux原生部署成果与后续容器课程的对应关系。

### 2. 能力目标

1. 在三机固定网络上完成跨主机反向代理。
2. 使用低权限账户和systemd管理课程后端。
3. 使用来源限制保护5000端口，并保持数据库本机监听。
4. 验证MySQL、MongoDB和Redis的认证、数据和恢复依据。
5. 更新Git资料与服务器巡检脚本。
6. 独立完成至少三项故障的定位、修复和回归验证。

### 3. 安全与交付目标

1. 不关闭SELinux和firewalld换取访问成功。
2. 不使用`chmod 777`掩盖权限问题。
3. 不把密码、私钥、数据库转储和日志提交到Git。
4. 备份不覆盖实验15、16已经验证的原始备份。
5. 故障测试结束后恢复全部服务和安全边界。

## 三、交付架构

```text
ubuntu-client
  ├── SSH/22 ───────────────► rocky-web
  ├── SSH/22 ───────────────► rocky-server
  └── HTTP/80 ──────────────► rocky-web：Nginx
                                ├── /           静态站点
                                ├── /health     Nginx健康页
                                └── /api/ ─────► rocky-server:5000
                                                   techcorp-api
                                                     ├── MySQL 127.0.0.1:3306
                                                     ├── MongoDB 127.0.0.1:27017
                                                     └── Redis 127.0.0.1:6379
```

### 端口基线

| 主机 | 端口 | 服务 | 网络访问要求 |
|---|---:|---|---|
| `rocky-web` | 22 | SSH | 课程网络可达 |
| `rocky-web` | 80 | Nginx | `ubuntu-client`可达 |
| `rocky-server` | 22 | SSH | 课程网络可达 |
| `rocky-server` | 5000 | `techcorp-api` | 只允许`rocky-web`来源 |
| `rocky-server` | 3306 | MySQL | 仅回环地址，不开放 |
| `rocky-server` | 27017 | MongoDB | 仅回环地址，不开放 |
| `rocky-server` | 6379 | Redis | 仅回环地址，不开放 |

`ubuntu-client`无法直连5000、3306、27017和6379是预期的安全验收结果。

## 四、时间与角色安排

| 阶段 | 建议用时 | 主要成果 |
|---|---:|---|
| 基线与准备 | 35分钟 | 三机状态表、目录和配置备份 |
| 后端与来源限制 | 55分钟 | systemd服务、5000访问边界 |
| Nginx统一入口 | 45分钟 | 首页、健康页和跨机API |
| 数据与恢复 | 55分钟 | 三类数据验证和隔离恢复 |
| Git与巡检 | 25分钟 | 更新后的脚本、文档和提交 |
| 故障排查 | 40分钟 | 至少三份完整故障记录 |
| 交叉验收与答辩 | 15分钟 | 最终清单和`Linux-L4` |

同组成员可以互相设置故障和复核结果，但每名学习者必须亲自完成命令操作、故障判断和答辩。

## 五、操作约定

1. 未标注主机时，默认在`rocky-server`执行。
2. 切换终端后先确认主机身份。
3. 代码块按顺序逐条执行，不整段粘贴到Shell。
4. `vim`中输入的HTML、JSON、systemd和Nginx内容不是Shell命令。
5. 密码只在MySQL、MongoDB或Redis交互提示中输入。
6. 某一层验证失败时停止增加新配置，先恢复最近通过状态。

每次切换终端先执行：

```bash
printf 'host=%s user=%s\n' "$(hostnamectl --static)" "$(whoami)"
```

## 六、任务一：核对Linux-L3基线

### 1. 在rocky-server核对身份和网络

```bash
hostnamectl --static
```

```bash
ip -brief address
```

```bash
ip route
```

```bash
getent hosts rocky-web ubuntu-client
```

### 2. 在rocky-server核对安全控制

```bash
getenforce
```

预期为`Enforcing`。

```bash
sudo firewall-cmd --state
```

预期为`running`。

### 3. 在rocky-server核对已有服务

```bash
systemctl is-active sshd mysqld mongod redis
```

四项都应为`active`。

### 4. 在rocky-server核对已有成果

```bash
test -s ~/backup-lab/mysql/company_db.sql
```

```bash
git -C ~/m1-project/git-lab status --short --branch
```

```bash
bash -n ~/m1-project/git-lab/scripts/server-health.sh
```

### 5. 在rocky-web核对基线

```bash
hostnamectl --static
```

```bash
getenforce
```

```bash
sudo firewall-cmd --state
```

```bash
systemctl is-active sshd nginx techcorp-backend
```

实验14留下的`techcorp-backend`此时可以仍为`active`，后面切换到跨机后端后会明确停用。

```bash
sudo nginx -t
```

```bash
test -f /srv/techcorp/www/index.html
```

### 6. 在ubuntu-client核对基线

```bash
hostnamectl --static
```

```bash
getent hosts rocky-server rocky-web techcorp.test
```

```bash
ssh -o BatchMode=yes rocky-server hostnamectl --static
```

```bash
ssh -o BatchMode=yes rocky-web hostnamectl --static
```

```bash
curl --fail --max-time 3 http://techcorp.test/health
```

### 基线停止点

如果主机名、固定IP、名称解析、SSH、SELinux、firewalld、服务、备份或Git成果缺失，应回到对应实验恢复。不得在多个未知故障上继续叠加配置。

## 七、任务二：建立最终交付目录

### 1. 在rocky-server创建目录

```bash
mkdir -p ~/m1-project/final/evidence
```

```bash
mkdir -p ~/m1-project/final/report
```

```bash
mkdir -p ~/m1-project/final/backup/config
```

```bash
mkdir -p ~/m1-project/final/backup/mysql
```

```bash
mkdir -p ~/m1-project/final/backup/mongodb
```

```bash
mkdir -p ~/m1-project/final/backup/redis
```

```bash
date '+project_start=%F %T %z' > ~/m1-project/final/evidence/project-start.txt
```

### 2. 在rocky-web创建目录

```bash
mkdir -p ~/m1-project/final/evidence
```

```bash
mkdir -p ~/m1-project/final/backup/config
```

```bash
mkdir -p ~/m1-project/final/backup/web-files
```

```bash
mkdir -p ~/m1-project/final/restore-test
```

### 3. 记录rocky-server基线

```bash
hostnamectl > ~/m1-project/final/evidence/baseline-rocky-server.txt
```

```bash
ip -brief address >> ~/m1-project/final/evidence/baseline-rocky-server.txt
```

```bash
ip route >> ~/m1-project/final/evidence/baseline-rocky-server.txt
```

```bash
sudo ss -lntp >> ~/m1-project/final/evidence/baseline-rocky-server.txt
```

```bash
getenforce >> ~/m1-project/final/evidence/baseline-rocky-server.txt
```

### 4. 记录rocky-web基线

```bash
hostnamectl > ~/m1-project/final/evidence/baseline-rocky-web.txt
```

```bash
ip -brief address >> ~/m1-project/final/evidence/baseline-rocky-web.txt
```

```bash
sudo ss -lntp >> ~/m1-project/final/evidence/baseline-rocky-web.txt
```

```bash
getenforce >> ~/m1-project/final/evidence/baseline-rocky-web.txt
```

## 八、任务三：备份最终项目将修改的配置

### 1. 在rocky-server备份已有配置

检查目标是否已经存在：

```bash
ls -l ~/m1-project/final/backup/config/mongod.conf.before-final
```

首次执行时提示不存在是正常结果。复制MongoDB配置：

```bash
sudo cp -p /etc/mongod.conf ~/m1-project/final/backup/config/mongod.conf.before-final
```

复制Redis配置：

```bash
sudo cp -p /etc/redis/redis.conf ~/m1-project/final/backup/config/redis.conf.before-final
```

复制MySQL主配置：

```bash
sudo cp -p /etc/my.cnf ~/m1-project/final/backup/config/my.cnf.before-final
```

如果`/etc/systemd/system/techcorp-api.service`已经存在，先检查来源和未提交成果；首次实验不应存在，不要盲目覆盖。

### 2. 在rocky-web备份Nginx配置

```bash
ls -l ~/m1-project/final/backup/config/techcorp.conf.before-final
```

首次执行提示不存在后再复制：

```bash
sudo cp -p /etc/nginx/conf.d/techcorp.conf ~/m1-project/final/backup/config/techcorp.conf.before-final
```

配置副本可能包含运行信息，只保存在受控备份目录，不提交Git。

## 九、任务四：在rocky-server建立课程后端

### 1. 确认Python

```bash
python3 --version
```

```bash
command -v python3
```

### 2. 检查低权限账户

```bash
getent passwd techcorp
```

如果没有输出，创建系统账户：

```bash
sudo useradd --system --home-dir /srv/techcorp --shell /sbin/nologin techcorp
```

再次确认：

```bash
getent passwd techcorp
```

### 3. 创建后端目录

```bash
sudo mkdir -p /srv/techcorp/backend
```

### 4. 创建健康数据

```bash
sudo vim /srv/techcorp/backend/health.json
```

输入：

```json
{
  "service": "techcorp-api",
  "status": "ok",
  "host": "rocky-server",
  "course": "Linux operating system"
}
```

### 5. 设置属主与权限

```bash
sudo chown -R techcorp:techcorp /srv/techcorp
```

```bash
sudo chmod 755 /srv/techcorp /srv/techcorp/backend
```

```bash
sudo chmod 644 /srv/techcorp/backend/health.json
```

### 6. 使用服务账户验证读取权限

```bash
sudo -u techcorp cat /srv/techcorp/backend/health.json
```

### 7. 确认rocky-server名称解析到本机地址

```bash
getent ahostsv4 rocky-server
```

结果应包含`rocky-server`的固定实验地址。

### 8. 创建systemd单元

```bash
sudo vim /etc/systemd/system/techcorp-api.service
```

输入：

```systemd
[Unit]
Description=TechCorp course backend service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=techcorp
Group=techcorp
WorkingDirectory=/srv/techcorp/backend
ExecStart=/usr/bin/python3 -m http.server 5000 --bind rocky-server --directory /srv/techcorp/backend
Restart=on-failure
RestartSec=3
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 9. 检查单元文件

```bash
sudo systemd-analyze verify /etc/systemd/system/techcorp-api.service
```

### 10. 让systemd重新读取单元

```bash
sudo systemctl daemon-reload
```

### 11. 启动并启用服务

```bash
sudo systemctl enable --now techcorp-api
```

### 12. 检查服务状态

```bash
systemctl is-active techcorp-api
```

### 13. 检查运行身份

```bash
systemctl show techcorp-api -p User -p Group -p MainPID
```

### 14. 检查5000监听

```bash
sudo ss -lntp | grep ':5000'
```

监听地址应为`rocky-server`对应的业务地址，不应是`0.0.0.0`。

### 15. 本机访问后端

```bash
curl --fail --max-time 3 http://rocky-server:5000/health.json
```

这一步通过后，才进入防火墙和跨主机测试。

## 十、任务五：只允许rocky-web访问5000

以下步骤在`rocky-server`执行。

### 1. 查看默认路由接口

```bash
ip route show default
```

### 2. 查看活动zone

```bash
sudo firewall-cmd --get-active-zones
```

### 3. 查询默认路由接口所属zone

```bash
sudo firewall-cmd --get-zone-of-interface="$(ip route show default | awk 'NR==1 {print $5}')"
```

如果返回实际zone名称，将它保存：

```bash
sudo firewall-cmd --get-zone-of-interface="$(ip route show default | awk 'NR==1 {print $5}')" > ~/m1-project/final/evidence/rocky-server-firewall-zone.txt
```

如果返回`no zone`，改为保存默认zone：

```bash
sudo firewall-cmd --get-default-zone > ~/m1-project/final/evidence/rocky-server-firewall-zone.txt
```

两条保存命令只执行符合当前实际情况的一条。

### 4. 核对保存的zone

```bash
cat ~/m1-project/final/evidence/rocky-server-firewall-zone.txt
```

结果不能是空字符串或`no zone`。

### 5. 确认三机地址文件

在当前终端载入实验8保存的三机地址：

```bash
source ~/m1-project/course-env.sh
```

继续在同一个终端核对`rocky-web`地址：

```bash
printf 'rocky_web=%s\n' "$ROCKY_WEB_IP"
```

### 6. 增加来源受限规则

```bash
sudo firewall-cmd --permanent --zone="$(cat ~/m1-project/final/evidence/rocky-server-firewall-zone.txt)" --add-rich-rule="rule family=ipv4 source address=${ROCKY_WEB_IP}/32 port port=5000 protocol=tcp accept"
```

### 7. 重新加载防火墙

```bash
sudo firewall-cmd --reload
```

### 8. 查看rich rule

```bash
sudo firewall-cmd --zone="$(cat ~/m1-project/final/evidence/rocky-server-firewall-zone.txt)" --list-rich-rules
```

规则中应同时出现`rocky-web`固定地址、5000和TCP。

### 9. 在rocky-web验证允许路径

```bash
curl --fail --max-time 3 http://rocky-server:5000/health.json
```

预期成功。

### 10. 在ubuntu-client验证拒绝路径

```bash
nc -vz -w 3 rocky-server 5000
```

预期失败。不要为了获得成功结果而开放5000。

## 十一、任务六：在rocky-web切换跨机Nginx入口

### 1. 确认原站点文件

```bash
test -f /srv/techcorp/www/index.html
```

```bash
sed -n '1,80p' /srv/techcorp/www/index.html
```

实验14已经创建该文件，本实验不重新生成无关站点。

### 2. 直接访问新后端

```bash
curl --fail --max-time 3 http://rocky-server:5000/health.json
```

成功后再修改Nginx。

### 3. 编辑现有虚拟主机

```bash
sudo vim /etc/nginx/conf.d/techcorp.conf
```

确保核心内容为：

```nginx
server {
    listen 80;
    server_name techcorp.test;
    root /srv/techcorp/www;
    index index.html;

    access_log /var/log/nginx/techcorp_access.log;
    error_log /var/log/nginx/techcorp_error.log;

    location = /health {
        default_type text/plain;
        return 200 "ok\n";
    }

    location /api/ {
        proxy_pass http://rocky-server:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 3s;
        proxy_read_timeout 5s;
    }
}
```

### 4. 检查站点路径权限

```bash
namei -l /srv/techcorp/www/index.html
```

### 5. 检查SELinux标签

```bash
ls -lZ /srv/techcorp/www/index.html
```

### 6. 确认持久文件上下文规则

```bash
sudo semanage fcontext -l | grep '/srv/techcorp/www'
```

如果没有规则，添加：

```bash
sudo semanage fcontext -a -t httpd_sys_content_t '/srv/techcorp/www(/.*)?'
```

如果规则存在但类型错误，修改：

```bash
sudo semanage fcontext -m -t httpd_sys_content_t '/srv/techcorp/www(/.*)?'
```

两条规则命令按实际情况选择一条。

### 7. 恢复正确标签

```bash
sudo restorecon -RFv /srv/techcorp/www
```

### 8. 允许Nginx建立上游连接

```bash
sudo setsebool -P httpd_can_network_connect on
```

### 9. 验证布尔值

```bash
getsebool httpd_can_network_connect
```

### 10. 检查Nginx语法

```bash
sudo nginx -t
```

### 11. 重新加载Nginx

```bash
sudo systemctl reload nginx
```

### 12. 检查三个本机URL

```bash
curl --fail -H 'Host: techcorp.test' http://127.0.0.1/
```

```bash
curl --fail -H 'Host: techcorp.test' http://127.0.0.1/health
```

```bash
curl --fail -H 'Host: techcorp.test' http://127.0.0.1/api/health.json
```

API响应中的`host`应为`rocky-server`，证明请求没有继续使用实验14的本机后端。

### 13. 停用实验14旧后端

```bash
sudo systemctl disable --now techcorp-backend
```

### 14. 确认旧服务已停用

```bash
systemctl is-enabled techcorp-backend
```

预期为`disabled`。

```bash
systemctl is-active techcorp-backend
```

预期为`inactive`。

### 15. 再次验证API

```bash
curl --fail -H 'Host: techcorp.test' http://127.0.0.1/api/health.json
```

旧后端停止后API仍成功，证明Nginx已经依赖`rocky-server`上的新后端。

## 十二、任务七：从ubuntu-client验收Web入口

### 1. 确认techcorp.test解析

```bash
getent hosts techcorp.test
```

应解析到`rocky-web`固定地址。如果错误，使用`sudo vim /etc/hosts`修正已有记录，不增加冲突的重复行。

### 2. 访问首页

```bash
curl --fail --max-time 3 http://techcorp.test/
```

### 3. 访问Nginx健康页

```bash
curl --fail --max-time 3 http://techcorp.test/health
```

### 4. 访问跨机API

```bash
curl --fail --max-time 3 http://techcorp.test/api/health.json
```

### 5. 查看HTTP状态和响应头

```bash
curl -i --max-time 3 http://techcorp.test/api/health.json
```

### 6. 在rocky-web检查访问日志

```bash
sudo tail -n 20 /var/log/nginx/techcorp_access.log
```

应能看到`ubuntu-client`来源地址和三个URL。

## 十三、任务八：验证最终网络暴露边界

### 1. 在rocky-web检查服务与监听

```bash
systemctl is-active sshd nginx
```

```bash
sudo ss -lntp | grep -E ':(22|80)\b'
```

### 2. 在rocky-web检查防火墙

```bash
sudo firewall-cmd --get-active-zones
```

```bash
sudo firewall-cmd --list-services
```

应包含`ssh`和`http`。

### 3. 在rocky-server检查服务与监听

```bash
systemctl is-active sshd techcorp-api mysqld mongod redis
```

```bash
sudo ss -lntp | grep -E ':(22|5000|3306|27017|6379)\b'
```

重点检查本地地址：5000绑定业务地址，三个数据库端口绑定回环地址。

### 4. 在rocky-server检查普通端口规则

```bash
sudo firewall-cmd --zone="$(cat ~/m1-project/final/evidence/rocky-server-firewall-zone.txt)" --list-ports
```

不能包含`5000/tcp`、`3306/tcp`、`27017/tcp`或`6379/tcp`的全来源开放。

### 5. 检查来源受限规则

```bash
sudo firewall-cmd --zone="$(cat ~/m1-project/final/evidence/rocky-server-firewall-zone.txt)" --list-rich-rules
```

5000只能出现在限定`rocky-web`地址的规则中。

### 6. 在ubuntu-client验证后端和数据库不可直连

```bash
nc -vz -w 3 rocky-server 5000
```

```bash
nc -vz -w 3 rocky-server 3306
```

```bash
nc -vz -w 3 rocky-server 27017
```

```bash
nc -vz -w 3 rocky-server 6379
```

四项都应失败。

### 7. 在rocky-web验证唯一允许的后端路径

```bash
curl --fail --max-time 3 http://rocky-server:5000/health.json
```

## 十四、任务九：验证MySQL

以下步骤在`rocky-server`执行。

### 1. 检查服务

```bash
systemctl is-active mysqld
```

### 2. 检查监听

```bash
sudo ss -lntp | grep ':3306'
```

应监听`127.0.0.1:3306`，不监听`0.0.0.0:3306`。

### 3. 检查bind配置

```bash
sudo grep -Rns '^[[:space:]]*bind-address' /etc/my.cnf /etc/my.cnf.d
```

### 4. 使用业务用户登录

```bash
mysql --protocol=TCP -h 127.0.0.1 -P 3306 -u app_user -p company_db
```

密码在提示符中输入。

### 5. 查询数据

```sql
SELECT COUNT(*) AS employee_count FROM employees;
```

预期为3。

```sql
SELECT id,name,department FROM employees ORDER BY id;
```

### 6. 验证最小权限

```sql
CREATE DATABASE should_be_denied;
```

预期被拒绝。随后退出：

```sql
EXIT;
```

如果创建成功，说明授权过大，应使用管理员检查`SHOW GRANTS`并整改。

## 十五、任务十：验证MongoDB

### 1. 检查服务

```bash
systemctl is-active mongod
```

### 2. 检查监听

```bash
sudo ss -lntp | grep ':27017'
```

应只监听`127.0.0.1:27017`。

### 3. 检查安全配置结构

```bash
sudo grep -nE '^(net:|  port:|  bindIp:|security:|  authorization:)' /etc/mongod.conf
```

### 4. 验证未认证读取被拒绝

```bash
mongosh --host 127.0.0.1 company_db --quiet --eval 'db.inspections.countDocuments({})'
```

预期出现未授权错误。

### 5. 使用业务用户登录

```bash
mongosh --host 127.0.0.1 --authenticationDatabase company_db -u inspectionApp -p company_db
```

### 6. 在mongosh中检查身份

```javascript
db.runCommand({connectionStatus:1})
```

### 7. 查询文档数

```javascript
db.inspections.countDocuments({})
```

预期至少为2。

### 8. 查询文档

```javascript
db.inspections.find().sort({_id:1})
```

退出：

```javascript
exit
```

## 十六、任务十一：验证Redis

### 1. 检查服务

```bash
systemctl is-active redis
```

### 2. 检查监听

```bash
sudo ss -lntp | grep ':6379'
```

只应监听回环地址。

### 3. 检查不含密码的配置摘要

```bash
sudo grep -nE '^(bind|protected-mode|port|save|appendonly|maxmemory|maxmemory-policy)' /etc/redis/redis.conf
```

### 4. 进入客户端

```bash
redis-cli
```

未认证执行：

```text
GET persistence:check
```

预期返回`NOAUTH`。

交互认证：

```text
AUTH <实验17设置的密码>
```

读取持久化键：

```text
GET persistence:check
```

预期返回`course-data`。

读取访问计数：

```text
GET website:visitors
```

创建最终项目状态：

```text
SET final:project:status ready
```

后台保存：

```text
BGSAVE
```

检查持久化状态：

```text
INFO persistence
```

确认`rdb_last_bgsave_status:ok`后退出：

```text
EXIT
```

## 十七、任务十二：完成网站文件备份和恢复抽查

以下前六步在`rocky-web`执行。

### 1. 备份站点目录

```bash
rsync -av /srv/techcorp/www/ ~/m1-project/final/backup/web-files/www/
```

### 2. 备份Nginx配置

```bash
cp -p ~/m1-project/final/backup/config/techcorp.conf.before-final ~/m1-project/final/backup/web-files/techcorp.conf.before-final
```

### 3. 创建隔离恢复目录

```bash
mkdir -p ~/m1-project/final/restore-test/www
```

### 4. 恢复到隔离目录

```bash
rsync -av ~/m1-project/final/backup/web-files/www/ ~/m1-project/final/restore-test/www/
```

### 5. 比较运行目录和恢复目录

```bash
diff -ru /srv/techcorp/www ~/m1-project/final/restore-test/www
```

没有输出表示内容一致。

### 6. 汇总到rocky-server

```bash
rsync -av ~/m1-project/final/backup/web-files/ rocky-server:~/m1-project/final/backup/web-files/
```

### 7. 在rocky-server确认收到备份

```bash
find ~/m1-project/final/backup/web-files -type f -ls
```

## 十八、任务十三：完成MySQL最终备份和隔离恢复

以下步骤在`rocky-server`执行。实验15原备份保持不变，本实验使用新的最终路径。

### 1. 确认目标文件尚不存在

```bash
ls -l ~/m1-project/final/backup/mysql/company_db.sql
```

首次执行提示不存在是正常结果。如果已存在，先确认它是否为当前项目成果，不要直接覆盖。

### 2. 创建当前逻辑备份

```bash
mysqldump -u root -p --single-transaction --routines --events --triggers --no-tablespaces company_db > ~/m1-project/final/backup/mysql/company_db.sql
```

### 3. 检查非空

```bash
test -s ~/m1-project/final/backup/mysql/company_db.sql
```

### 4. 检查包含employees表

```bash
grep -n 'CREATE TABLE.*employees' ~/m1-project/final/backup/mysql/company_db.sql
```

### 5. 保存校验值

```bash
sha256sum ~/m1-project/final/backup/mysql/company_db.sql > ~/m1-project/final/evidence/mysql-backup.sha256
```

### 6. 创建隔离恢复库

```bash
mysql -u root -p -e 'CREATE DATABASE company_final_restore CHARACTER SET utf8mb4;'
```

如果提示数据库已存在，说明此前恢复未清理，应先确认其中是否有需要保留的数据，不要直接覆盖。

### 7. 恢复备份

```bash
mysql -u root -p company_final_restore < ~/m1-project/final/backup/mysql/company_db.sql
```

### 8. 验证恢复后的行数

```bash
mysql -u root -p company_final_restore -e 'SELECT COUNT(*) AS restored_count FROM employees;'
```

预期为3。

### 9. 查看恢复后的数据

```bash
mysql -u root -p company_final_restore -e 'SELECT id,name,department FROM employees ORDER BY id;'
```

### 10. 删除隔离测试库

确认恢复证据已经保存后执行：

```bash
mysql -u root -p -e 'DROP DATABASE company_final_restore;'
```

正式`company_db`始终没有被覆盖。

## 十九、任务十四：完成MongoDB最终备份和隔离恢复

### 1. 确认目标目录尚不存在

```bash
ls -ld ~/m1-project/final/backup/mongodb/company-dump
```

首次执行提示不存在是正常结果。如果已存在，不直接覆盖。

### 2. 创建最终转储

```bash
mongodump --host 127.0.0.1 --port 27017 --authenticationDatabase company_db -u inspectionApp -p --db company_db --out ~/m1-project/final/backup/mongodb/company-dump
```

### 3. 查看备份文件

```bash
find ~/m1-project/final/backup/mongodb/company-dump -type f -ls
```

### 4. 恢复到隔离命名空间

```bash
mongorestore --host 127.0.0.1 --port 27017 --authenticationDatabase admin -u courseAdmin -p --nsFrom='company_db.*' --nsTo='company_final_restore.*' ~/m1-project/final/backup/mongodb/company-dump
```

### 5. 验证恢复后的文档数

```bash
mongosh --host 127.0.0.1 --authenticationDatabase admin -u courseAdmin -p company_final_restore --quiet --eval 'db.inspections.countDocuments({})'
```

预期至少为2。

### 6. 查看恢复后的文档

```bash
mongosh --host 127.0.0.1 --authenticationDatabase admin -u courseAdmin -p company_final_restore --quiet --eval 'db.inspections.find().forEach(printjson)'
```

### 7. 清理隔离恢复库

```bash
mongosh --host 127.0.0.1 --authenticationDatabase admin -u courseAdmin -p company_final_restore --quiet --eval 'db.dropDatabase()'
```

正式`company_db`没有被删除或覆盖。

## 二十、任务十五：保存Redis恢复依据

实验17已经验证过重启读取，本实验在`BGSAVE`成功后保存RDB副本。

### 1. 确认RDB存在且非空

```bash
sudo test -s /var/lib/redis/dump.rdb
```

### 2. 复制RDB

```bash
sudo cp -p /var/lib/redis/dump.rdb ~/m1-project/final/backup/redis/dump.rdb
```

### 3. 调整受控副本属主

```bash
sudo chown "$(id -un):$(id -gn)" ~/m1-project/final/backup/redis/dump.rdb
```

### 4. 保存校验值

```bash
sha256sum ~/m1-project/final/backup/redis/dump.rdb > ~/m1-project/final/evidence/redis-backup.sha256
```

### 5. 检查备份

```bash
ls -lh ~/m1-project/final/backup/redis/dump.rdb
```

课程不在最终业务实例上替换RDB做恢复测试，以免破坏三类服务综合环境；恢复能力由实验17的重启读取和本次非空副本、校验值共同证明。

## 二十一、任务十六：更新巡检脚本

实验19脚本还不知道新增的`techcorp-api`和5000端口。本任务只修改集中配置，不重写整个脚本。

### 1. 进入Git仓库

```bash
cd ~/m1-project/git-lab
```

### 2. 查看原数组

```bash
grep -nE '^(SERVICES|PORTS)=' scripts/server-health.sh
```

### 3. 编辑脚本

```bash
vim scripts/server-health.sh
```

将两行调整为：

```bash-script
SERVICES=(techcorp-api mysqld mongod redis sshd)
PORTS=(22 5000 3306 27017 6379)
```

不把`nginx`和80加入本机数组，因为它们运行在`rocky-web`；脚本原有的`check_web`继续验证跨机Web入口。

### 4. 查看差异

```bash
git diff -- scripts/server-health.sh
```

### 5. 检查语法

```bash
bash -n scripts/server-health.sh
```

### 6. 运行最终巡检

```bash
./scripts/server-health.sh > ~/m1-project/final/evidence/health-final.log 2>&1
```

### 7. 立即保存退出码

```bash
printf '%s\n' "$?" > ~/m1-project/final/evidence/health-final-exit.txt
```

### 8. 查看结果

```bash
cat ~/m1-project/final/evidence/health-final.log
```

### 9. 查看退出码

```bash
cat ~/m1-project/final/evidence/health-final-exit.txt
```

没有资源警告时预期为0。

## 二十二、任务十七：更新Git交付资料

### 1. 更新脱敏Nginx模板

```bash
cp templates/techcorp.conf.example templates/techcorp-final.conf.example
```

### 2. 编辑最终模板

```bash
vim templates/techcorp-final.conf.example
```

把`proxy_pass`调整为：

```nginx
proxy_pass http://rocky-server:5000/;
```

模板不得包含密码、私钥或完整运行配置中的秘密。

### 3. 创建架构说明

```bash
vim docs/final-architecture.md
```

输入：

```markdown
# TechCorp Linux三机交付架构

- ubuntu-client：SSH管理与HTTP外部验收。
- rocky-web：提供SSH/22、Nginx/80、静态站点和反向代理。
- rocky-server：提供SSH/22和techcorp-api/5000。
- 5000只允许rocky-web来源访问。
- MySQL/3306、MongoDB/27017和Redis/6379只监听本机。
- 两台Rocky保持firewalld运行与SELinux Enforcing。
- Git只保存脱敏模板、脚本和文档，不保存密码、私钥、日志或数据库转储。
```

### 4. 查看状态

```bash
git status --short --ignored
```

### 5. 暂存巡检脚本

```bash
git add scripts/server-health.sh
```

### 6. 暂存Nginx模板

```bash
git add templates/techcorp-final.conf.example
```

### 7. 暂存架构文档

```bash
git add docs/final-architecture.md
```

### 8. 审查提交内容

```bash
git diff --cached
```

### 9. 检查暂存文件名

```bash
git diff --cached --name-only
```

只能包含明确的脚本、模板和文档。

### 10. 形成提交

```bash
git commit -m "feat: integrate final three-node service checks"
```

### 11. 推送

```bash
git push origin main
```

### 12. 确认仓库干净

```bash
git status --short
```

## 二十三、任务十八：交叉故障排查

每名学习者至少抽取三张不同层次的故障卡。设置者必须先记录原值或建立备份；排查者只得到现象，不直接得到根因。完成后必须恢复正确基线。

### 统一故障记录

```text
故障编号：
故障开始时间：
观察主机与客户端：
现象：
仍然正常的功能：
影响范围：
第一条证据：
初步假设：
下一条用于证实或证伪的命令：
证据与判断：
根因：
修复前备份或原值：
修复操作：
原路径复测：
相邻功能回归：
预防方法：
```

### 故障卡A：techcorp-api停止

现象：`/api/health.json`返回502，首页和`/health`正常。

优先检查：

```bash
systemctl status techcorp-api --no-pager
```

```bash
sudo journalctl -u techcorp-api -n 50 --no-pager
```

```bash
sudo ss -lntp | grep ':5000'
```

修复后必须从`rocky-server`、`rocky-web`和`ubuntu-client`分别复测正确路径。

### 故障卡B：Nginx上游端口错误

现象同样可能为502，但`techcorp-api`和5000实际正常。

优先检查：

```bash
sudo nginx -T | grep -n 'proxy_pass'
```

```bash
curl --fail --max-time 3 http://rocky-server:5000/health.json
```

```bash
sudo tail -n 30 /var/log/nginx/techcorp_error.log
```

修复前使用任务八的`techcorp.conf.before-final`作为回退依据，修复后先`nginx -t`再重新加载。

### 故障卡C：SELinux阻止Nginx连接后端

现象：`rocky-web`可以直接curl后端，但通过Nginx访问API失败。

优先检查：

```bash
getenforce
```

```bash
getsebool httpd_can_network_connect
```

```bash
sudo ausearch -m AVC -ts recent | tail -n 30
```

不得关闭SELinux。恢复正确布尔值后验证API、首页和SELinux状态。

### 故障卡D：5000来源规则缺失

现象：`rocky-server`本机访问5000成功，`rocky-web`访问超时或失败。

优先检查：

```bash
sudo firewall-cmd --zone="$(cat ~/m1-project/final/evidence/rocky-server-firewall-zone.txt)" --list-rich-rules
```

```bash
sudo ss -lntp | grep ':5000'
```

```bash
source ~/m1-project/course-env.sh
```

继续在同一个终端核对规则中应出现的来源地址：

```bash
printf 'expected_source=%s\n' "$ROCKY_WEB_IP"
```

恢复规则后既要证明`rocky-web`成功，也要证明`ubuntu-client`仍失败。

### 故障卡E：站点文件权限或标签错误

现象：首页返回403，但Nginx健康页可能仍正常。

优先检查：

```bash
namei -l /srv/techcorp/www/index.html
```

```bash
ls -lZ /srv/techcorp/www/index.html
```

```bash
sudo tail -n 30 /var/log/nginx/techcorp_error.log
```

```bash
sudo ausearch -m AVC -ts recent | tail -n 30
```

使用最小Unix权限和`restorecon`恢复，不使用`chmod 777`。

### 故障卡F：MongoDB认证数据库错误

现象：服务和27017都正常，但`inspectionApp`登录失败。

对照错误命令中的认证库并检查：

```bash
systemctl is-active mongod
```

```bash
sudo ss -lntp | grep ':27017'
```

```bash
mongosh --host 127.0.0.1 --authenticationDatabase company_db -u inspectionApp -p company_db
```

本卡不修改服务配置，重点区分网络、认证和授权。

### 故障卡G：MySQL服务停止

现象：本机TCP连接被拒绝，其他服务仍正常。

优先检查：

```bash
systemctl status mysqld --no-pager
```

```bash
sudo journalctl -u mysqld -n 50 --no-pager
```

```bash
sudo ss -lntp | grep ':3306'
```

恢复后必须使用`app_user`重新查询`employees`，不能只看端口。

### 故障卡H：Git中的模板误改

现象：脱敏模板上游地址错误，但运行服务可能仍正常。

先查看：

```bash
git status --short
```

```bash
git diff -- templates/techcorp-final.conf.example
```

确认误改后恢复：

```bash
git restore templates/techcorp-final.conf.example
```

本卡说明运行配置、模板和Git历史是不同对象，不能把模板恢复误认为线上配置已经恢复。

## 二十四、任务十九：最终人工验收

不再编写第二个大型验收脚本。使用已有巡检脚本和以下单条命令逐层验收，并把结果填入验收表。

### 1. 在ubuntu-client验收入口

```bash
ssh -o BatchMode=yes rocky-web hostnamectl --static
```

```bash
ssh -o BatchMode=yes rocky-server hostnamectl --static
```

```bash
curl --fail --max-time 3 http://techcorp.test/
```

```bash
curl --fail --max-time 3 http://techcorp.test/health
```

```bash
curl --fail --max-time 3 http://techcorp.test/api/health.json
```

```bash
nc -vz -w 3 rocky-server 5000
```

最后一项预期失败。

### 2. 在rocky-web验收入口与上游

```bash
systemctl is-active nginx
```

```bash
sudo nginx -t
```

```bash
curl --fail --max-time 3 http://rocky-server:5000/health.json
```

```bash
getenforce
```

```bash
getsebool httpd_can_network_connect
```

### 3. 在rocky-server验收后端与数据服务

```bash
systemctl is-active techcorp-api mysqld mongod redis sshd
```

```bash
sudo ss -lntp | grep -E ':(22|5000|3306|27017|6379)\b'
```

```bash
getenforce
```

```bash
sudo firewall-cmd --state
```

```bash
~/m1-project/git-lab/scripts/server-health.sh
```

### 4. 验收备份

```bash
test -s ~/m1-project/final/backup/mysql/company_db.sql
```

```bash
find ~/m1-project/final/backup/mongodb/company-dump -type f -print -quit
```

```bash
test -s ~/m1-project/final/backup/redis/dump.rdb
```

```bash
find ~/m1-project/final/backup/web-files -type f -print
```

### 5. 验收Git

```bash
git -C ~/m1-project/git-lab status --short --branch
```

```bash
git -C ~/m1-project/git-lab log --oneline --decorate -n 8
```

```bash
git -C ~/m1-project/git-lab ls-files
```

确认跟踪清单不含`.env`、私钥、日志、SQL、BSON、RDB或AOF。

### 最终验收表

| 编号 | 验收项 | 执行主机 | 预期 | 实际 | 通过 |
|---:|---|---|---|---|---|
| 1 | 三机身份与固定IP | 三台VM | 与规划一致 |  |  |
| 2 | SSH密钥管理 | ubuntu-client | 两台Rocky可登录 |  |  |
| 3 | 首页和健康页 | ubuntu-client | HTTP成功 |  |  |
| 4 | 跨机API | ubuntu-client | 返回rocky-server数据 |  |  |
| 5 | 5000来源限制 | Ubuntu/Web | Ubuntu失败，Web成功 |  |  |
| 6 | 数据端口边界 | ubuntu-client | 3306/27017/6379失败 |  |  |
| 7 | SELinux | 两台Rocky | Enforcing |  |  |
| 8 | firewalld | 两台Rocky | running且规则最小 |  |  |
| 9 | MySQL业务数据 | rocky-server | 3条员工数据 |  |  |
| 10 | MongoDB业务数据 | rocky-server | 至少2条巡检文档 |  |  |
| 11 | Redis业务数据 | rocky-server | 认证后可读取 |  |  |
| 12 | 隔离恢复 | rocky-server | MySQL/MongoDB恢复成功 |  |  |
| 13 | 巡检脚本 | rocky-server | 无CRITICAL |  |  |
| 14 | Git仓库 | rocky-server | 干净且无秘密 |  |  |
| 15 | 故障记录 | 个人 | 至少3项完整闭环 |  |  |

## 二十五、任务二十：完成交付文档

### 1. 创建部署记录

```bash
vim ~/m1-project/final/report/deployment-record.md
```

至少包含：

```markdown
# TechCorp Linux三机部署记录

## 主机与网络

| 主机 | IPv4 | 角色 | 默认路由 |
|---|---|---|---|

## 服务与端口

| 服务 | 主机 | 配置路径 | 监听 | 防火墙边界 | 验证命令 |
|---|---|---|---|---|---|

## Web访问链路

- 客户端入口：
- Nginx上游：
- 后端服务：
- SELinux设置：

## 数据服务

- MySQL：
- MongoDB：
- Redis：

## 备份与恢复

| 对象 | 备份路径 | 恢复目标 | 验证结果 |
|---|---|---|---|

## Git与巡检

- 仓库：
- 最终提交：
- 脚本：
- 退出码：

## 已知限制

- Python http.server仅用于课程演示。
- 本项目未实现生产级HTTPS、高可用、集中日志和秘密管理。
```

### 2. 创建故障记录

```bash
vim ~/m1-project/final/report/troubleshooting-record.md
```

使用任务十八的统一模板记录至少三项故障。不能只写“重启后恢复”。

### 3. 检查报告

```bash
ls -l ~/m1-project/final/report
```

```bash
sed -n '1,200p' ~/m1-project/final/report/deployment-record.md
```

```bash
sed -n '1,240p' ~/m1-project/final/report/troubleshooting-record.md
```

## 二十六、提交成果

### 1. 目录要求

```text
~/m1-project/final/
├── backup/
│   ├── config/
│   ├── mysql/company_db.sql
│   ├── mongodb/company-dump/
│   ├── redis/dump.rdb
│   └── web-files/
├── evidence/
│   ├── baseline-rocky-server.txt
│   ├── health-final.log
│   ├── health-final-exit.txt
│   ├── mysql-backup.sha256
│   ├── project-start.txt
│   ├── redis-backup.sha256
│   └── rocky-server-firewall-zone.txt
└── report/
    ├── deployment-record.md
    └── troubleshooting-record.md

~/m1-project/git-lab/
├── README.md
├── docs/
│   ├── final-architecture.md
│   ├── handover.md
│   ├── server-health.md
│   └── service-map.md
├── scripts/server-health.sh
└── templates/
    ├── techcorp.conf.example
    └── techcorp-final.conf.example
```

### 2. 答辩要求

现场随机完成：

1. 解释一条从`ubuntu-client`到后端的请求路径；
2. 说明为什么5000和三个数据库端口使用不同安全边界；
3. 从一条故障现象提出假设并选择第一条证据命令；
4. 展示一次隔离恢复结果；
5. 说明Git、数据库备份和VMware快照的区别；
6. 运行巡检脚本并解释退出码。

## 二十七、评分建议

| 项目 | 分值 | 评价要点 |
|---|---:|---|
| 三机基线 | 10 | 身份、地址、解析、SSH和安全状态正确 |
| Nginx与后端 | 20 | systemd、跨机代理和三个URL均通过 |
| 网络安全边界 | 15 | 5000来源受限，数据库不对外，SELinux与防火墙启用 |
| 数据服务 | 15 | 三类服务完成认证、权限和数据验证 |
| 备份恢复 | 15 | 文件对比、MySQL与MongoDB隔离恢复、Redis恢复依据完整 |
| Git与巡检 | 10 | 复用已有仓库和脚本，提交清晰且无秘密 |
| 故障排查 | 10 | 至少三项包含证据、根因、修复与回归 |
| 文档与答辩 | 5 | 他人能够复核，回答准确 |

### 一票否决项

出现以下任一项，安全部分不得分并要求立即整改：

1. 将真实密码、令牌或SSH私钥提交到Git或报告；
2. 为通过验收关闭SELinux或长期停止firewalld；
3. 使用`chmod 777`掩盖权限问题；
4. 将MySQL、MongoDB或Redis无认证暴露到课程网络；
5. 把5000向所有来源开放；
6. 故障测试结束后未恢复服务和规则；
7. 伪造命令输出、截图、Git历史或恢复结果。

## 二十八、环境保留与课程衔接

全部验收通过后建立`Linux-L4`快照，并保留独立副本。`Linux-L4`是《虚拟化容器技术》的唯一正式起点。

必须保留：

- 三台虚拟机的主机名、固定IP、hosts、SSH密钥和网络模式；
- 两台Rocky的firewalld与SELinux正确状态；
- `rocky-web`上的Nginx、站点和跨机代理；
- `rocky-server`上的`techcorp-api`、MySQL、MongoDB和Redis；
- `~/m1-project`中的备份、报告、Git和巡检脚本；
- 实验20故障记录和最终验收表。

第二门课程为释放内存可以临时停止MySQL、MongoDB、Redis和`rocky-web`，但不得卸载服务、删除VM或覆盖`~/m1-project`。虚拟化与容器课程统一使用新的`~/vc-course`目录，并将容器化结果与本次Linux原生部署进行对照。

## 二十九、项目复盘

1. 哪一条证据最能说明Web服务真正可用？为什么单独的`active`不够？
2. 为什么后端5000监听业务地址，而数据库仍监听回环地址？
3. 502、403、连接拒绝和认证失败分别优先检查哪些层？
4. 为什么隔离恢复比直接恢复到正式数据库更安全？
5. 实验14旧后端为什么必须在跨机后端通过后停用？
6. 为什么最终验收复用实验19脚本，而不再编写第二个大型脚本？
7. Git、配置副本、数据库备份和`Linux-L4`快照分别解决什么问题？
8. 哪些Linux能力会直接迁移到Docker和Kubernetes学习中？

## 三十、官方参考

- [Nginx反向代理模块](https://nginx.org/en/docs/http/ngx_http_proxy_module.html)
- [systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html)
- [RHEL 9 firewalld使用与配置](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_firewalls_and_packet_filters/using-and-configuring-firewalld_firewall-packet-filters)
- [RHEL 9 SELinux使用](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/)
- [MySQL 8.4 mysqldump](https://dev.mysql.com/doc/refman/8.4/en/mysqldump.html)
- [MongoDB数据库工具](https://www.mongodb.com/docs/database-tools/)
- [Redis持久化](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)
- [Git官方参考](https://git-scm.com/docs)
- [GNU Bash参考手册](https://www.gnu.org/software/bash/manual/)
