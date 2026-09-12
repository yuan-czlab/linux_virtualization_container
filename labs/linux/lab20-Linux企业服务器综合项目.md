# 实验20：Linux企业服务器综合部署与故障排查

> 所属模块：模块三 企业服务部署与综合运维  
> 建议学时：6学时  
> 实验方式：个人为主，可两人互相验收  
> 对应教材：《模块三 企业服务部署与综合运维》第31章  
> 前置实验：实验1—19  
> 项目成果：由`ubuntu-client`、`rocky-web`和`rocky-server`组成的TechCorp三机交付环境，以及部署资料、备份、巡检结果、Git版本和故障排查记录

## 一、项目情境

TechCorp需要交付一套小型Linux业务环境。`rocky-web`使用Nginx提供网站和反向代理入口，`rocky-server`运行由systemd托管的后端进程，并保留MySQL、MongoDB、Redis、备份、Git和巡检成果；`ubuntu-client`承担SSH管理和外部访问验收。三台虚拟机共同形成“客户端—Web入口—业务服务器”的完整链路。

你已经在实验1—19分别完成这些能力。本实验不要求从零重装所有软件，而是要求检查、整合、修正、验证和交付。最终结果必须能被另一名同学按照交付文档复核。

## 二、实验目标

### 1. 知识目标

1. 说明网站入口、后端服务、数据库、缓存和运维工具之间的关系。
2. 说明“进程—端口—防火墙—SELinux—应用”的分层排查方法。
3. 理解部署完成、功能可用、安全边界和可恢复性是不同的验收维度。

### 2. 能力目标

1. 按角色整合Nginx、后端服务、MySQL、MongoDB和Redis。
2. 使用systemd管理自建服务，并通过日志排查启动失败。
3. 配置跨主机反向代理、来源受限端口和本地数据库监听边界。
4. 完成配置语法、认证、数据读写、备份恢复和健康检查。
5. 使用Git管理脱敏配置，使用Shell脚本完成服务器巡检。
6. 独立完成至少三项跨层故障诊断并恢复。

### 3. 素质目标

1. 任何修改先确认现状，重要配置先备份。
2. 不把真实密码、私钥、数据库文件和日志提交到Git。
3. 不以“服务显示active”代替业务验收。
4. 故障恢复后进行回归验证并留下证据。

## 三、交付架构

```text
ubuntu-client
  ├── SSH/22 ───────────────> rocky-web
  ├── SSH/22 ───────────────> rocky-server
  └── HTTP/80 ──────────────> rocky-web：Nginx + 静态站点
                                      │
                                      └── HTTP/5000（仅允许rocky-web来源）
                                                   ↓
                                          rocky-server：techcorp-api
                                                        MySQL 127.0.0.1:3306
                                                        MongoDB 127.0.0.1:27017
                                                        Redis 127.0.0.1:6379

运维保障：两台Rocky均使用systemd、journal、firewalld和SELinux；
          rocky-server集中保留数据库备份、Git版本和巡检证据。
```

### 端口验收基线

| 主机 | 端口 | 服务 | 期望监听 | firewalld |
|---|---:|---|---|---|
| `rocky-web` | 22 | SSH | 实验网络地址 | 放行ssh |
| `rocky-web` | 80 | Nginx | 实验网络地址 | 放行http |
| `rocky-server` | 22 | SSH | 实验网络地址 | 放行ssh |
| `rocky-server` | 5000 | techcorp-api | `rocky-server`实验地址 | 仅允许`rocky-web`来源 |
| `rocky-server` | 3306 | MySQL | 仅127.0.0.1 | 不放行 |
| `rocky-server` | 27017 | MongoDB | 仅127.0.0.1 | 不放行 |
| `rocky-server` | 6379 | Redis | 仅127.0.0.1/::1 | 不放行 |

> 实验15—17中为远程验证临时开放过数据库端口时，应先撤销临时规则。最终项目不要求Ubuntu直接访问数据库。

## 四、时间安排建议

本实验共6学时，即270分钟。以下时间用于课堂调度，不把一个项目割裂成多个独立小实验：

| 用时 | 工作内容 |
|---:|---|
| 约45分钟 | 阅读需求、检查三机基线、整理目录和备份 |
| 约75分钟 | 在两台Rocky上建立站点、后端systemd服务和Nginx入口 |
| 约45分钟 | 验证三类数据服务和安全边界 |
| 约30分钟 | 备份、Git和巡检整合 |
| 约45分钟 | 抽取故障卡、定位并恢复 |
| 约30分钟 | 交叉验收、整理报告和提交成果 |

若课堂进度不同，教师可以压缩说明时间或将交叉验收放到最后一节完成，但不能取消故障恢复和最终验证。

## 五、项目约束

1. 使用实验1创建的三台虚拟机，不重新安装操作系统，不交换主机角色。
2. 复用实验14—19的服务和成果，缺失项回到对应实验补齐。
3. `rocky-web`只对外提供SSH和HTTP；`rocky-server`对外提供SSH，并仅向`rocky-web`开放5000端口。
4. 真实密码只在交互式客户端输入，不写入脚本、截图或Git。
5. 修改系统配置前保留带时间标识的备份。
6. 每项故障必须写出“现象、假设、证据、修复、复测”。
7. `ubuntu-client`是正式外部客户端；Windows宿主机浏览器只作可选展示。

### 操作位置约定

本实验所有命令都必须在标题指定的虚拟机中执行。没有标注时，默认在`rocky-server`执行；不要因为两个Rocky账号密码相同就忽略终端提示符。每次切换终端先执行：

```bash
printf 'host=%s user=%s\n' "$(hostname)" "$(whoami)"
```

## 六、项目准备

### 任务一：建立交付目录（两台Rocky）

在`rocky-server`执行：

```bash
mkdir -p ~/m1-project/final/{evidence,report,backup}
mkdir -p ~/m1-project/git-lab/{docs,templates,scripts}
date '+project_start=%F %T %z' | tee ~/m1-project/final/evidence/project-start.txt
```

在`rocky-web`执行：

```bash
mkdir -p ~/m1-project/final/{evidence,report,backup}
date '+project_start=%F %T %z' | tee ~/m1-project/final/evidence/project-start.txt
```

### 任务二：检查而不是猜测当前状态（两台Rocky）

先在`rocky-server`执行，结果保存为`baseline-rocky-server.txt`：

```bash
{
    printf '=== system ===\n'
    hostnamectl
    printf '\n=== addresses ===\n'
    ip -brief address
    printf '\n=== routes ===\n'
    ip route
    printf '\n=== services ===\n'
    for service in sshd techcorp-api mysqld mongod redis; do
        printf '%-10s %s\n' "$service" "$(systemctl is-active "$service" 2>/dev/null || true)"
    done
    printf '\n=== listening ===\n'
    sudo ss -lntp
    printf '\n=== firewall ===\n'
    sudo firewall-cmd --get-active-zones
    sudo firewall-cmd --list-all
    printf '\n=== selinux ===\n'
    getenforce
} | tee ~/m1-project/final/evidence/baseline-rocky-server.txt
```

再在`rocky-web`执行同类检查，但服务循环只检查`sshd nginx`，结果保存为`baseline-rocky-web.txt`。最后在`ubuntu-client`执行以下命令，确认能够解析并到达两台服务器：

```bash
hostnamectl --static
ip -brief address
ip route
getent hosts rocky-server rocky-web
ping -c 2 rocky-server
ping -c 2 rocky-web
```

根据结果填写：

| 检查项 | 当前值 | 是否符合 | 需要处理 |
|---|---|---|---|
| 主机名 |  |  |  |
| IPv4地址 |  |  |  |
| 默认路由 |  |  |  |
| DNS解析 |  |  |  |
| SSH |  |  |  |
| `rocky-web`上的Nginx |  |  |  |
| MySQL |  |  |  |
| MongoDB |  |  |  |
| Redis |  |  |  |
| SELinux |  |  |  |

> **停止点**：如果磁盘已满、网络不通或软件源不可用，先按实验7、8、13排查，不应继续叠加服务配置。

### 任务三：备份关键配置（按主机分别执行）

在`rocky-server`执行：

```bash
STAMP=$(date +%Y%m%d-%H%M%S)
FINAL_BACKUP="$HOME/m1-project/final/backup/$STAMP"
mkdir -p "$FINAL_BACKUP"

sudo cp -a /etc/my.cnf "$FINAL_BACKUP/my.cnf" 2>/dev/null || true
sudo cp -a /etc/my.cnf.d "$FINAL_BACKUP/my.cnf.d" 2>/dev/null || true
sudo cp -a /etc/mongod.conf "$FINAL_BACKUP/mongod.conf" 2>/dev/null || true

REDIS_CONF=$(rpm -ql redis 2>/dev/null | grep '/redis.conf$' | head -1)
if [[ -n "$REDIS_CONF" ]]; then
    sudo cp -p "$REDIS_CONF" "$FINAL_BACKUP/redis.conf"
fi

sudo chown -R "$USER:$USER" "$FINAL_BACKUP"
find "$FINAL_BACKUP" -maxdepth 2 -type f -ls | tee ~/m1-project/final/evidence/config-backup.txt
```

在`rocky-web`执行：

```bash
STAMP=$(date +%Y%m%d-%H%M%S)
FINAL_BACKUP="$HOME/m1-project/final/backup/$STAMP"
mkdir -p "$FINAL_BACKUP"
sudo cp -a /etc/nginx "$FINAL_BACKUP/nginx" 2>/dev/null || true
sudo chown -R "$USER:$USER" "$FINAL_BACKUP"
find "$FINAL_BACKUP" -maxdepth 2 -type f -ls \
    | tee ~/m1-project/final/evidence/config-backup.txt
```

配置备份可能含密码，只存放在本机受控目录，不提交Git。

## 七、实验步骤

### 任务一：创建最小权限服务账户（两台Rocky）

先在`rocky-server`创建后端账户和目录：

检查是否已有账户：

```bash
getent passwd techcorp || true
```

若不存在，创建不可交互登录的系统账户：

```bash
sudo useradd --system --home-dir /srv/techcorp --shell /sbin/nologin techcorp
getent passwd techcorp
```

建立后端目录：

```bash
sudo mkdir -p /srv/techcorp/backend
sudo chown -R techcorp:techcorp /srv/techcorp
sudo chmod 755 /srv/techcorp /srv/techcorp/backend
```

再在`rocky-web`执行同样的账户检查与创建命令，然后只建立站点目录：

```bash
getent passwd techcorp >/dev/null || \
    sudo useradd --system --home-dir /srv/techcorp --shell /sbin/nologin techcorp
sudo mkdir -p /srv/techcorp/www
sudo chown -R techcorp:techcorp /srv/techcorp
sudo chmod 755 /srv/techcorp /srv/techcorp/www
```

### 任务二：准备网站与后端数据（按主机执行）

在`rocky-web`创建网站：

```bash
sudo tee /srv/techcorp/www/index.html >/dev/null <<'EOF'
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>TechCorp Linux Server</title>
</head>
<body>
  <h1>TechCorp Linux Server</h1>
  <p>Web service is running.</p>
  <ul>
    <li><a href="/health">Nginx health</a></li>
    <li><a href="/api/health.json">Backend health</a></li>
  </ul>
</body>
</html>
EOF

sudo chown -R techcorp:techcorp /srv/techcorp/www
sudo find /srv/techcorp/www -type f -exec chmod 644 {} \;
find /srv/techcorp/www -maxdepth 2 -printf '%M %u:%g %p\n'
```

在`rocky-server`创建后端健康数据：

```bash
sudo tee /srv/techcorp/backend/health.json >/dev/null <<'EOF'
{
  "service": "techcorp-api",
  "status": "ok",
  "course": "Linux operating system"
}
EOF

sudo chown -R techcorp:techcorp /srv/techcorp/backend
sudo find /srv/techcorp/backend -type f -exec chmod 644 {} \;
sed -n '1,20p' /srv/techcorp/backend/health.json
```

### 任务三：在`rocky-server`把后端程序交给systemd

确认Python可用：

```bash
python3 --version
command -v python3
```

创建服务单元：

```bash
sudo tee /etc/systemd/system/techcorp-api.service >/dev/null <<'EOF'
[Unit]
Description=TechCorp course backend service
After=network.target

[Service]
Type=simple
User=techcorp
Group=techcorp
WorkingDirectory=/srv/techcorp/backend
ExecStart=/usr/bin/python3 -m http.server 5000 --bind <ROCKY_SERVER_IP>
Restart=on-failure
RestartSec=3
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

sudo systemd-analyze verify /etc/systemd/system/techcorp-api.service
sudo systemctl daemon-reload
sudo systemctl enable --now techcorp-api
systemctl status techcorp-api --no-pager
sudo ss -lntp | grep ':5000'
curl --fail http://<ROCKY_SERVER_IP>:5000/health.json
```

创建单元文件时，必须把两处`<ROCKY_SERVER_IP>`替换为实验8记录的`rocky-server`静态IPv4地址，禁止使用`0.0.0.0`。随后在`rocky-server`上仅允许`rocky-web`访问5000端口，将占位符换成实际地址：

```bash
sudo firewall-cmd --permanent --zone=public \
  --add-rich-rule='rule family="ipv4" source address="<ROCKY_WEB_IP>/32" port port="5000" protocol="tcp" accept'
sudo firewall-cmd --reload
sudo firewall-cmd --zone=public --list-rich-rules
```

在`rocky-web`确认名称解析和后端访问：

```bash
getent hosts rocky-server
curl --fail http://rocky-server:5000/health.json
```

在`ubuntu-client`直接访问`http://rocky-server:5000/health.json`应失败。此失败是安全边界的验收结果，不要为方便而向整个网段放行5000。

> **验收点**：后端由独立低权限账户运行，systemd状态为active；5000端口绑定`rocky-server`地址，但防火墙只允许`rocky-web`来源。

### 任务四：在`rocky-web`配置Nginx统一入口

备份同名旧配置：

```bash
FINAL_BACKUP=$(find "$HOME/m1-project/final/backup" \
  -mindepth 1 -maxdepth 1 -type d | sort | tail -1)
test -n "$FINAL_BACKUP" || { echo '未找到rocky-web配置备份目录'; exit 1; }
if [[ -f /etc/nginx/conf.d/techcorp.conf ]]; then
    sudo cp -p /etc/nginx/conf.d/techcorp.conf \
        "$FINAL_BACKUP/techcorp.conf.before-final"
fi
```

写入配置：

```bash
sudo tee /etc/nginx/conf.d/techcorp.conf >/dev/null <<'EOF'
server {
    listen 80;
    server_name techcorp.local;
    root /srv/techcorp/www;
    index index.html;

    access_log /var/log/nginx/techcorp_access.log;
    error_log  /var/log/nginx/techcorp_error.log;

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
EOF
```

处理SELinux文件标签并允许Nginx连接远程后端：

```bash
sudo dnf install -y policycoreutils-python-utils
sudo semanage fcontext -a -t httpd_sys_content_t '/srv/techcorp/www(/.*)?' 2>/dev/null || \
sudo semanage fcontext -m -t httpd_sys_content_t '/srv/techcorp/www(/.*)?'
sudo restorecon -Rv /srv/techcorp/www
sudo setsebool -P httpd_can_network_connect on
ls -Zd /srv/techcorp/www /srv/techcorp/www/index.html
getsebool httpd_can_network_connect
```

先检查语法，再重新加载：

```bash
sudo nginx -t
sudo systemctl enable --now nginx
sudo systemctl reload nginx
systemctl is-active nginx
curl --fail -H 'Host: techcorp.local' http://127.0.0.1/
curl --fail -H 'Host: techcorp.local' http://127.0.0.1/health
curl --fail -H 'Host: techcorp.local' http://127.0.0.1/api/health.json
```

在`ubuntu-client`确认`/etc/hosts`包含`rocky-web`实际地址。没有记录时添加：

```bash
echo '<ROCKY_WEB_IP> techcorp.local' | sudo tee -a /etc/hosts
getent hosts techcorp.local
```

将`<ROCKY_WEB_IP>`替换为实验8配置的`rocky-web`静态地址，然后从`ubuntu-client`执行：

```bash
curl --fail http://techcorp.local/
curl --fail http://techcorp.local/health
curl --fail http://techcorp.local/api/health.json
```

如需课堂图形展示，可以再从Windows宿主机浏览器访问：

```text
http://techcorp.local/
http://techcorp.local/api/health.json
```

此时按实验14在Windows hosts文件中加入`<rocky-web的IPv4地址> techcorp.local`，但Windows结果不替代Ubuntu命令行证据。

> **验收点**：`ubuntu-client`能够解析`techcorp.local`，静态首页、Nginx健康页和跨主机反向代理后端均能访问，访问日志中出现Ubuntu客户端地址。

### 任务五：在两台Rocky落实网络暴露边界

先在`rocky-web`确认活动zone和接口：

```bash
sudo firewall-cmd --get-active-zones
```

以下以`public`为例；如果活动zone不同，请替换为实际值：

```bash
sudo firewall-cmd --permanent --zone=public --add-service=ssh
sudo firewall-cmd --permanent --zone=public --add-service=http
sudo firewall-cmd --reload
sudo firewall-cmd --zone=public --list-all
```

检查`rocky-web`监听地址：

```bash
sudo ss -lntp | grep -E ':(22|80)\b'
```

再在`rocky-server`检查监听地址、普通规则和来源受限规则：

```bash
sudo ss -lntp | grep -E ':(22|5000|3306|27017|6379)\b'
sudo firewall-cmd --zone=public --list-services
sudo firewall-cmd --zone=public --list-ports
sudo firewall-cmd --zone=public --list-rich-rules
```

确认`rocky-server`的普通服务列表不含HTTP，普通端口列表不含`5000/tcp`、`3306/tcp`、`27017/tcp`或`6379/tcp`，5000只出现在限定`rocky-web`源地址的rich rule中。如果数据库端口由先前实验临时开放，应先确认规则的准确写法再删除并重载；不要删除不认识的其他业务规则。

最后从`ubuntu-client`验证80可达、5000不可直达，再从`rocky-web`验证5000可达。

> **验收点**：SSH按要求可达，80只由`rocky-web`提供；5000只允许`rocky-web`访问，三种数据库端口不对外提供。

### 任务六：在`rocky-server`验证MySQL

```bash
systemctl is-active mysqld
sudo ss -lntp | grep ':3306'
sudo grep -Rns '^[[:space:]]*bind-address' /etc/my.cnf /etc/my.cnf.d 2>/dev/null || true
```

使用实验15创建的管理员账号交互式登录：

```bash
mysql -u root -p
```

在MySQL客户端中执行：

```sql
SHOW DATABASES;
USE company_db;
SHOW TABLES;
SELECT COUNT(*) AS employee_count FROM employees;
SHOW VARIABLES LIKE 'bind_address';
EXIT;
```

若表或数据缺失，返回实验15的备份进行恢复，不要临时伪造截图。

再使用实验15创建的业务账号验证最小权限：

```bash
mysql --protocol=TCP -h 127.0.0.1 -P 3306 \
    -u app_user -p company_db
```

```sql
SELECT COUNT(*) AS employee_count FROM employees;
CREATE DATABASE should_be_denied;
EXIT;
```

查询应成功，创建新数据库应因权限不足而失败。若测试库意外创建成功，说明授权范围过大，应返回实验15检查`SHOW GRANTS`并整改。

### 任务七：在`rocky-server`验证MongoDB

```bash
systemctl is-active mongod
sudo ss -lntp | grep ':27017'
sudo grep -nE '^[[:space:]]*(bindIp|port|authorization):' /etc/mongod.conf
```

使用实验16创建的业务用户，不在命令行写密码：

```bash
mongosh --host 127.0.0.1 --port 27017 \
  --authenticationDatabase company_db \
  -u inspectionApp -p
```

在`mongosh`中执行：

```javascript
use company_db
db.runCommand({connectionStatus: 1})
db.inspections.find().limit(5)
db.inspections.countDocuments()
exit
```

未认证读取应被拒绝，认证后才能访问授权数据。

### 任务八：在`rocky-server`验证Redis

```bash
REDIS_CONF=$(rpm -ql redis | grep '/redis.conf$' | head -1)
printf 'redis_conf=%s\n' "$REDIS_CONF"
systemctl is-active redis
sudo ss -lntp | grep ':6379'
sudo grep -nE '^(bind|protected-mode|port|requirepass|save|appendonly)' "$REDIS_CONF" | sed -n '1,100p'
redis-cli
```

在`redis-cli`中交互输入：

```text
PING
AUTH <教师指定的Redis实验密码>
PING
SET final_project_status ready
INCR final_project_visits
GET final_project_status
GET final_project_visits
SAVE
EXIT
```

认证前的业务命令应返回NOAUTH，认证后读写成功。

> **验收点**：三类数据服务均通过“服务—监听—认证—数据”四层验证。

### 任务九：在两台Rocky完成备份与恢复抽查

#### 1. 在`rocky-web`备份站点和配置

```bash
mkdir -p ~/m1-project/final/backup/files
rsync -av /srv/techcorp/www/ ~/m1-project/final/backup/files/www/
sudo cp -p /etc/nginx/conf.d/techcorp.conf \
    ~/m1-project/final/backup/files/techcorp.conf
sudo chown -R "$USER:$USER" ~/m1-project/final/backup/files
```

先在`rocky-web`本机完成网站恢复抽查，不覆盖运行目录：

```bash
mkdir -p ~/m1-project/final/restore-test/www
rsync -av ~/m1-project/final/backup/files/www/ \
    ~/m1-project/final/restore-test/www/
diff -ru /srv/techcorp/www ~/m1-project/final/restore-test/www
```

再将站点备份汇总到`rocky-server`。以下命令在`rocky-web`执行：

```bash
rsync -av ~/m1-project/final/backup/files/ \
    rocky-server:~/m1-project/final/backup/web-files/
```

在`rocky-server`执行`find ~/m1-project/final/backup/web-files -type f -ls`确认已经收到文件。

#### 2. 在`rocky-server`完成MySQL逻辑备份

密码在提示符中输入：

```bash
mysqldump -u root -p --single-transaction \
    --routines --triggers company_db \
    > ~/m1-project/final/backup/company_db.sql
test -s ~/m1-project/final/backup/company_db.sql
```

#### 3. 在`rocky-server`完成MongoDB逻辑备份

```bash
mongodump --host 127.0.0.1 --port 27017 \
    --authenticationDatabase company_db \
    -u inspectionApp -p \
    --db company_db \
    --out ~/m1-project/final/backup/mongodb
find ~/m1-project/final/backup/mongodb -type f -ls
```

#### 4. 数据库恢复抽查

数据库备份需至少完成“文件非空、工具可读、恢复命令说明”三项检查。若教师安排独立测试库，可按实验15、16执行真实恢复；不得在最终业务库上直接覆盖测试。

### 任务十：在`rocky-server`同步Git版本

复制脱敏模板，不复制含真实认证信息的完整配置：

```bash
cd ~/m1-project/git-lab
cp templates/techcorp.conf.example templates/techcorp-final.conf.example
sed -n '1,120p' templates/techcorp-final.conf.example
```

补充架构文档：

````bash
cat > docs/final-architecture.md <<'EOF'
# TechCorp Linux三机交付架构

- 客户端：ubuntu-client，负责SSH和HTTP验收。
- Web入口：rocky-web，提供SSH/22和Nginx/80。
- 业务服务器：rocky-server，提供SSH/22和techcorp-api/5000；5000只允许rocky-web访问。
- 本地数据：rocky-server上的MySQL/3306、MongoDB/27017、Redis/6379，均不对外开放。
- 运维保障：systemd、journal、firewalld、SELinux、跨机备份、Git、巡检脚本。
- 机密边界：密码、私钥、真实数据库转储和日志不进入Git。
EOF

git status --short --ignored
git diff
git add docs/final-architecture.md templates/techcorp-final.conf.example
git diff --cached
git commit -m "docs: record final server architecture"
git push origin main
````

如果`git diff --cached`中出现密码、私钥或备份，立即取消暂存并处理：

```bash
git restore --staged <文件路径>
```

### 任务十一：在`rocky-server`运行统一巡检

```bash
cd ~/m1-project/git-lab
bash -n scripts/server-health.sh
./scripts/server-health.sh \
    > ~/m1-project/final/evidence/health-final.log 2>&1
HEALTH_CODE=$?
cat ~/m1-project/final/evidence/health-final.log
printf 'health_exit_code=%s\n' "$HEALTH_CODE"
```

实验19脚本运行于`rocky-server`，不应检查只存在于`rocky-web`的Nginx和80端口。将服务和端口数组调整为：

```bash
SERVICES=(techcorp-api mysqld mongod redis sshd)
PORTS=(22 5000 3306 27017 6379)
```

修改后再次执行语法检查、运行和Git提交：

```bash
bash -n scripts/server-health.sh
./scripts/server-health.sh \
    > ~/m1-project/final/evidence/health-final-v2.log 2>&1
echo $?
git add scripts/server-health.sh
git commit -m "feat: include backend in server health check"
git push origin main
```

## 八、综合故障排查

教师从下列故障卡中为每名学生或每组抽取至少三项。学生也可在互相验收时由同伴设置故障。设置者必须记录改动，避免产生不可恢复状态。

### 通用排查记录模板

```text
故障编号：
观察到的现象：
影响范围：
第一条证据：
初步假设：
继续检查的命令与结果：
根因：
修复操作：
回归验证：
如何预防：
```

### 故障卡A：Nginx配置语法错误

本卡在`rocky-web`执行。设置者在实验配置中制造一处缺少分号或括号错误。排查者应使用：

```bash
sudo nginx -t
systemctl status nginx --no-pager
sudo journalctl -u nginx -n 50 --no-pager
```

修复后必须先`nginx -t`，再重新加载并验证三个URL。

### 故障卡B：后端服务工作目录错误

本卡在`rocky-server`执行。设置者先备份单元文件，再把`WorkingDirectory`改为不存在目录并重启。排查者应使用：

```bash
systemctl status techcorp-api --no-pager
sudo journalctl -u techcorp-api -n 50 --no-pager
sudo systemd-analyze verify /etc/systemd/system/techcorp-api.service
```

修复后执行`daemon-reload`、重启、检查5000端口和API URL。

### 故障卡C：SELinux阻止Nginx连接后端

本卡在`rocky-web`执行。设置者记录并临时关闭布尔值：

```bash
sudo setsebool httpd_can_network_connect off
```

排查者不能关闭SELinux，应检查：

```bash
getenforce
curl -i -H 'Host: techcorp.local' http://127.0.0.1/api/health.json
sudo tail -n 30 /var/log/nginx/techcorp_error.log
sudo ausearch -m AVC -ts recent | tail -n 30
```

确认根因后恢复正确布尔值并复测。

### 故障卡D：MySQL停止或监听异常

本卡在`rocky-server`执行，排查顺序如下：

```bash
systemctl status mysqld --no-pager
sudo ss -lntp | grep ':3306' || true
sudo journalctl -u mysqld -n 50 --no-pager
sudo grep -Rns '^[[:space:]]*bind-address' /etc/my.cnf /etc/my.cnf.d 2>/dev/null || true
```

恢复后用客户端认证并查询`company_db`，不能只看到端口就结束。

### 故障卡E：MongoDB认证或配置缩进错误

本卡在`rocky-server`执行。

```bash
systemctl status mongod --no-pager
sudo journalctl -u mongod -n 50 --no-pager
sudo sed -n '1,160p' /etc/mongod.conf
mongosh --host 127.0.0.1 --port 27017
```

区分服务未启动、认证数据库选择错误、用户名错误和YAML缩进错误。

### 故障卡F：Redis未认证或监听范围错误

本卡在`rocky-server`执行。

```bash
systemctl status redis --no-pager
sudo ss -lntp | grep ':6379' || true
sudo grep -nE '^(bind|protected-mode|port|requirepass)' "$REDIS_CONF"
redis-cli
```

不要把`protected-mode no`作为便利修复。最终状态应恢复认证与本机监听。

### 故障卡G：防火墙未开放HTTP

本卡在`rocky-web`执行。

```bash
curl --fail -H 'Host: techcorp.local' http://127.0.0.1/health
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --zone=public --list-all
```

`rocky-web`本机访问正常而`ubuntu-client`访问失败时，再检查客户端地址与路由、`rocky-web`活动zone、接口归属和HTTP服务规则。

### 故障卡H：站点文件标签或权限错误

本卡在`rocky-web`执行。

```bash
namei -l /srv/techcorp/www/index.html
ls -lZ /srv/techcorp/www/index.html
sudo tail -n 30 /var/log/nginx/techcorp_error.log
sudo ausearch -m AVC -ts recent | tail -n 30
```

恢复正确Unix权限和SELinux类型，不使用`chmod 777`，不关闭SELinux。

## 九、最终验收

### 1. 自动检查

在`ubuntu-client`创建验收脚本。实验10建立的`rocky-web`和`rocky-server`SSH别名及密钥必须可用：

```bash
mkdir -p ~/m1-project/final/evidence
vim ~/m1-project/final/acceptance.sh
```

写入：

```bash
#!/usr/bin/env bash
set -u

fail=0

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1" >&2; fail=$((fail + 1)); }

check_service() {
    local host="$1" service="$2"
    if ssh -o BatchMode=yes -o ConnectTimeout=3 "$host" \
        systemctl is-active --quiet "$service"; then
        pass "${host}: service ${service} active"
    else
        fail "${host}: service ${service} not active"
    fi
}

check_port() {
    local host="$1" port="$2"
    if ssh -o BatchMode=yes -o ConnectTimeout=3 "$host" \
        "ss -lntH 'sport = :${port}' | grep -q ."; then
        pass "${host}: tcp ${port} listening"
    else
        fail "${host}: tcp ${port} not listening"
    fi
}

for service in sshd nginx; do check_service rocky-web "$service"; done
for service in sshd techcorp-api mysqld mongod redis; do
    check_service rocky-server "$service"
done

for port in 22 80; do check_port rocky-web "$port"; done
for port in 22 5000 3306 27017 6379; do
    check_port rocky-server "$port"
done

for url in \
    http://techcorp.local/ \
    http://techcorp.local/health \
    http://techcorp.local/api/health.json; do
    if curl --silent --fail --max-time 3 "$url" >/dev/null; then
        pass "url ${url}"
    else
        fail "url ${url}"
    fi
done

if curl --silent --fail --max-time 3 \
    http://rocky-server:5000/health.json >/dev/null; then
    fail 'ubuntu-client can directly access rocky-server:5000'
else
    pass 'rocky-server:5000 rejects ubuntu-client as expected'
fi

if ssh rocky-web curl --silent --fail --max-time 3 \
    http://rocky-server:5000/health.json >/dev/null; then
    pass 'rocky-web can access rocky-server:5000'
else
    fail 'rocky-web cannot access rocky-server:5000'
fi

if ssh rocky-server 'test -s "$HOME/m1-project/final/backup/company_db.sql"'; then
    pass 'MySQL backup exists and is not empty'
else
    fail 'MySQL backup missing or empty'
fi

if ssh rocky-server \
    "find ~/m1-project/final/backup/mongodb -type f -print -quit 2>/dev/null | grep -q ."; then
    pass 'MongoDB backup files exist'
else
    fail 'MongoDB backup files missing'
fi

if ssh rocky-server \
    "git -C ~/m1-project/git-lab diff --quiet && git -C ~/m1-project/git-lab diff --cached --quiet"; then
    pass 'Git tracked working tree clean'
else
    fail 'Git tracked working tree has uncommitted changes'
fi

printf 'failed_checks=%d\n' "$fail"
(( fail == 0 ))
```

运行并保留结果，然后汇总到`rocky-server`：

```bash
chmod 750 ~/m1-project/final/acceptance.sh
bash -n ~/m1-project/final/acceptance.sh
~/m1-project/final/acceptance.sh \
    > ~/m1-project/final/evidence/acceptance-final.log 2>&1
ACCEPT_CODE=$?
cat ~/m1-project/final/evidence/acceptance-final.log
printf 'acceptance_exit_code=%s\n' "$ACCEPT_CODE"
scp ~/m1-project/final/evidence/acceptance-final.log \
    rocky-server:~/m1-project/final/evidence/
```

自动检查不包含数据库密码和业务数据内容，因此还必须完成以下人工验收。

### 2. 人工验收清单

- [ ] 能说明三台虚拟机的主机名、IPv4地址、默认路由、DNS和各自角色。
- [ ] 能从`ubuntu-client`通过SSH登录两台Rocky。
- [ ] 能从`ubuntu-client`访问`rocky-web`上的首页、Nginx健康页和跨主机API健康数据。
- [ ] 5000只允许`rocky-web`访问，3306、27017和6379未直接对外开放。
- [ ] 两台Rocky的SELinux均为Enforcing，Nginx跨主机反向代理仍可用。
- [ ] MySQL认证后能查询关系型数据。
- [ ] MongoDB未认证访问被拒绝，认证后能查询文档。
- [ ] Redis未认证业务命令被拒绝，认证后能读写键值。
- [ ] MySQL和MongoDB备份存在，网站恢复抽查无差异。
- [ ] Git仓库没有真实密码、私钥、日志和数据库转储。
- [ ] `rocky-server`巡检脚本能检查本机系统、服务和端口，三机验收脚本能检查完整访问链路。
- [ ] 至少三项故障有完整证据链和恢复验证。

### 3. 交付材料

```text
~/m1-project/final/
├── acceptance.sh
├── backup/
│   ├── company_db.sql
│   ├── files/
│   └── mongodb/
├── evidence/
│   ├── acceptance-final.log
│   ├── baseline.txt
│   ├── health-final-v2.log
│   └── project-start.txt
└── report/
    ├── deployment-record.md
    └── troubleshooting-record.md

~/m1-project/git-lab/
├── README.md
├── docs/
├── scripts/server-health.sh
└── templates/
```

部署记录至少包含：环境、地址、服务、端口、配置文件、验证方法、备份位置和回退方法。故障记录使用本实验提供的统一模板。

## 十、评分建议

| 项目 | 分值 | 评价要点 |
|---|---:|---|
| 系统与网络基线 | 10 | 主机、网络、SSH、时间和软件源状态清楚 |
| Nginx与后端服务 | 20 | systemd托管、静态页、健康页、反向代理均可用 |
| 数据服务 | 20 | MySQL、MongoDB、Redis完成状态、监听、认证和数据验证 |
| 安全边界 | 15 | 防火墙合理、SELinux Enforcing、数据库不直接暴露、无秘密泄露 |
| 备份与恢复 | 10 | 文件和数据库备份有效，至少完成一次恢复抽查 |
| Git与巡检 | 10 | 脱敏资料有版本，巡检脚本与退出码正确 |
| 故障排查 | 10 | 至少三项故障有证据链、修复和回归验证 |
| 文档与交付 | 5 | 材料完整，另一名同学可以复核 |

### 一票否决项

出现以下任一项，安全部分不得分，并要求立即整改：

1. 将真实密码、SSH私钥或数据库转储推送到Git。
2. 为解决访问问题关闭SELinux或长期停用firewalld。
3. 使用`chmod 777`掩盖权限问题。
4. 将MySQL、MongoDB或Redis无认证暴露到不可信网络。
5. 故障测试结束后未恢复服务。

## 十一、项目复盘

请在报告中回答：

1. 哪一项检查最能说明“服务真正可用”，为什么？
2. 本项目中哪些端口必须对外，哪些必须仅本机？
3. systemd、firewalld和SELinux分别解决什么问题？
4. Git、文件备份和数据库逻辑备份为什么不能互相替代？
5. 三次故障排查中，哪一条证据最接近根因？
6. 如果这台服务器要进入真实生产环境，还缺少哪些能力？

## 十二、课程边界说明

本综合项目用于Linux系统管理入门，重点是单机部署和可验证运维。以下内容留到后续《虚拟化与容器技术》或更高阶课程：

- 容器镜像、Docker和Compose；
- Kubernetes编排；
- 数据库高可用、复制和集群；
- HTTPS证书自动化和完整域名体系；
- 专业监控告警平台与集中日志；
- CI/CD和生产级密钥管理。

掌握本项目的进程、端口、权限、网络、日志和恢复逻辑，是后续学习容器技术的直接基础。
