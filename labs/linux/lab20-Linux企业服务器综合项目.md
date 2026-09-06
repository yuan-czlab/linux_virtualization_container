# 实验20：Linux企业服务器综合部署与故障排查

> 所属模块：模块三 企业服务部署与综合运维  
> 建议学时：6学时  
> 实验方式：个人为主，可两人互相验收  
> 对应教材：《模块三 企业服务部署与综合运维》第31章  
> 前置实验：实验1—19  
> 项目成果：一台可由Ubuntu客户端验收的TechCorp Linux服务器、部署资料、备份、巡检结果、Git版本和故障排查记录

## 一、项目情境

TechCorp需要交付一台小型Linux业务服务器。服务器使用Nginx提供网站和反向代理入口，使用一个由systemd托管的本地后端进程提供健康数据，MySQL保存关系型业务数据，MongoDB保存文档数据，Redis保存访问计数。管理员通过SSH维护服务器，并使用防火墙、SELinux、备份、Git和巡检脚本保障运行。

你已经在实验1—19分别完成这些能力。本实验不要求从零重装所有软件，而是要求检查、整合、修正、验证和交付。最终结果必须能被另一名同学按照交付文档复核。

## 二、实验目标

### 1. 知识目标

1. 说明网站入口、后端服务、数据库、缓存和运维工具之间的关系。
2. 说明“进程—端口—防火墙—SELinux—应用”的分层排查方法。
3. 理解部署完成、功能可用、安全边界和可恢复性是不同的验收维度。

### 2. 能力目标

1. 整合Nginx、MySQL、MongoDB、Redis和本地后端服务。
2. 使用systemd管理自建服务，并通过日志排查启动失败。
3. 配置对外端口和本地数据库监听边界。
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
Ubuntu客户端 ── SSH/22 ─────────────────────────┐
                                                ↓
Ubuntu客户端 ── HTTP/80 ──> Nginx ──> 静态站点  Rocky服务器
                           └──> 127.0.0.1:5000 ──> techcorp-api

服务器本机：
  MySQL    127.0.0.1:3306   关系型数据
  MongoDB  127.0.0.1:27017  文档数据
  Redis    127.0.0.1:6379   计数和临时状态

运维保障：systemd + journal + firewalld + SELinux
          rsync/备份 + Git + server-health.sh
```

### 端口验收基线

| 端口 | 服务 | 期望监听 | firewalld |
|---:|---|---|---|
| 22 | SSH | 实验网络地址 | 放行ssh |
| 80 | Nginx | 所需网络地址 | 放行http |
| 5000 | techcorp-api | 仅127.0.0.1 | 不放行 |
| 3306 | MySQL | 仅127.0.0.1 | 不放行 |
| 27017 | MongoDB | 仅127.0.0.1 | 不放行 |
| 6379 | Redis | 仅127.0.0.1/::1 | 不放行 |

> 如果教师安排了“双虚拟机远程数据库”扩展场景，应按指定源地址开放；未安排时以仅本机监听为最终状态。

## 四、时间安排建议

本实验共6学时，即270分钟。以下时间用于课堂调度，不把一个项目割裂成多个独立小实验：

| 用时 | 工作内容 |
|---:|---|
| 约45分钟 | 阅读需求、检查基线、整理目录和备份 |
| 约75分钟 | 建立站点、后端systemd服务和Nginx入口 |
| 约45分钟 | 验证三类数据服务和安全边界 |
| 约30分钟 | 备份、Git和巡检整合 |
| 约45分钟 | 抽取故障卡、定位并恢复 |
| 约30分钟 | 交叉验收、整理报告和提交成果 |

若课堂进度不同，教师可以压缩说明时间或将交叉验收放到最后一节完成，但不能取消故障恢复和最终验证。

## 五、项目约束

1. 使用实验1创建的Rocky Linux虚拟机，不重新安装操作系统。
2. 复用实验14—19的服务和成果，缺失项回到对应实验补齐。
3. 最终只对外提供课程要求的SSH和HTTP。
4. 真实密码只在交互式客户端输入，不写入脚本、截图或Git。
5. 修改系统配置前保留带时间标识的备份。
6. 每项故障必须写出“现象、假设、证据、修复、复测”。
7. 使用实验1、8保留的Ubuntu Server作为正式外部客户端；Windows宿主机浏览器只作可选展示。

## 六、项目准备

### 任务一：建立交付目录

```bash
mkdir -p ~/m1-project/final/{evidence,report,backup}
mkdir -p ~/m1-project/git-lab/{docs,templates,scripts}
date '+project_start=%F %T %z' | tee ~/m1-project/final/evidence/project-start.txt
```

### 任务二：检查而不是猜测当前状态

```bash
{
    printf '=== system ===\n'
    hostnamectl
    printf '\n=== addresses ===\n'
    ip -brief address
    printf '\n=== routes ===\n'
    ip route
    printf '\n=== services ===\n'
    for service in sshd nginx mysqld mongod redis; do
        printf '%-10s %s\n' "$service" "$(systemctl is-active "$service" 2>/dev/null || true)"
    done
    printf '\n=== listening ===\n'
    sudo ss -lntp
    printf '\n=== firewall ===\n'
    sudo firewall-cmd --get-active-zones
    sudo firewall-cmd --list-all
    printf '\n=== selinux ===\n'
    getenforce
} | tee ~/m1-project/final/evidence/baseline.txt
```

根据结果填写：

| 检查项 | 当前值 | 是否符合 | 需要处理 |
|---|---|---|---|
| 主机名 |  |  |  |
| IPv4地址 |  |  |  |
| 默认路由 |  |  |  |
| DNS解析 |  |  |  |
| SSH |  |  |  |
| Nginx |  |  |  |
| MySQL |  |  |  |
| MongoDB |  |  |  |
| Redis |  |  |  |
| SELinux |  |  |  |

> **停止点**：如果磁盘已满、网络不通或软件源不可用，先按实验7、8、13排查，不应继续叠加服务配置。

### 任务三：备份关键配置

```bash
STAMP=$(date +%Y%m%d-%H%M%S)
FINAL_BACKUP="$HOME/m1-project/final/backup/$STAMP"
mkdir -p "$FINAL_BACKUP"

sudo cp -a /etc/nginx "$FINAL_BACKUP/nginx" 2>/dev/null || true
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

配置备份可能含密码，只存放在本机受控目录，不提交Git。

## 七、实验步骤

### 任务一：创建最小权限的后端服务账户

检查是否已有账户：

```bash
getent passwd techcorp || true
```

若不存在，创建不可交互登录的系统账户：

```bash
sudo useradd --system --home-dir /srv/techcorp --shell /sbin/nologin techcorp
getent passwd techcorp
```

建立目录：

```bash
sudo mkdir -p /srv/techcorp/{www,backend}
sudo chown -R techcorp:techcorp /srv/techcorp
sudo chmod 755 /srv/techcorp /srv/techcorp/www /srv/techcorp/backend
```

### 任务二：准备网站与后端数据

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

sudo tee /srv/techcorp/backend/health.json >/dev/null <<'EOF'
{
  "service": "techcorp-api",
  "status": "ok",
  "course": "Linux operating system"
}
EOF

sudo chown -R techcorp:techcorp /srv/techcorp
sudo find /srv/techcorp -type f -exec chmod 644 {} \;
```

验证文件内容和权限：

```bash
find /srv/techcorp -maxdepth 2 -printf '%M %u:%g %p\n'
sed -n '1,20p' /srv/techcorp/backend/health.json
```

### 任务三：把后端程序交给systemd

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
ExecStart=/usr/bin/python3 -m http.server 5000 --bind 127.0.0.1
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
curl --fail http://127.0.0.1:5000/health.json
```

最终必须监听`127.0.0.1:5000`，不能是`0.0.0.0:5000`。

> **验收点**：后端由独立低权限账户运行，systemd状态为active，重启策略明确，5000端口仅本机监听。

### 任务四：配置Nginx统一入口

备份同名旧配置：

```bash
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
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 3s;
        proxy_read_timeout 5s;
    }
}
EOF
```

处理SELinux文件标签并允许Nginx连接本机后端：

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

在Ubuntu客户端确认`/etc/hosts`包含Rocky服务器实际地址。没有记录时添加：

```bash
echo '<ROCKY_IP> techcorp.local' | sudo tee -a /etc/hosts
getent hosts techcorp.local
```

将`<ROCKY_IP>`替换为实验8配置的Rocky静态地址，然后从Ubuntu执行：

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

此时按实验14在Windows hosts文件中加入`<Rocky服务器IPv4地址> techcorp.local`，但Windows结果不替代Ubuntu命令行证据。

> **验收点**：Ubuntu客户端能够解析`techcorp.local`，静态首页、Nginx健康页和反向代理后端均能访问，访问日志中出现Ubuntu客户端地址。

### 任务五：落实网络暴露边界

确认活动zone和接口：

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

检查监听地址：

```bash
sudo ss -lntp | grep -E ':(22|80|5000|3306|27017|6379)\b'
```

检查数据库服务和端口未被防火墙显式开放：

```bash
sudo firewall-cmd --zone=public --list-services
sudo firewall-cmd --zone=public --list-ports
```

确认服务列表中只有课程需要的`ssh`和`http`等项目，端口列表中没有`3306/tcp`、`27017/tcp`或`6379/tcp`。如果这些数据库端口由先前实验临时开放，应在确认无远程实验需求后删除对应规则，再重载。不要删除不认识的其他业务规则。

> **验收点**：22和80按要求可达；5000、3306、27017和6379不直接对外提供。

### 任务六：验证MySQL

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

### 任务七：验证MongoDB

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

### 任务八：验证Redis

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

### 任务九：完成备份与恢复抽查

#### 1. 站点和脱敏配置备份

```bash
mkdir -p ~/m1-project/final/backup/files
rsync -av /srv/techcorp/www/ ~/m1-project/final/backup/files/www/
sudo cp -p /etc/nginx/conf.d/techcorp.conf \
    ~/m1-project/final/backup/files/techcorp.conf
sudo chown -R "$USER:$USER" ~/m1-project/final/backup/files
```

#### 2. MySQL逻辑备份

密码在提示符中输入：

```bash
mysqldump -u root -p --single-transaction \
    --routines --triggers company_db \
    > ~/m1-project/final/backup/company_db.sql
test -s ~/m1-project/final/backup/company_db.sql
```

#### 3. MongoDB逻辑备份

```bash
mongodump --host 127.0.0.1 --port 27017 \
    --authenticationDatabase company_db \
    -u inspectionApp -p \
    --db company_db \
    --out ~/m1-project/final/backup/mongodb
find ~/m1-project/final/backup/mongodb -type f -ls
```

#### 4. 恢复抽查

网站恢复抽查不覆盖生产目录：

```bash
mkdir -p ~/m1-project/final/restore-test/www
rsync -av ~/m1-project/final/backup/files/www/ \
    ~/m1-project/final/restore-test/www/
diff -ru /srv/techcorp/www ~/m1-project/final/restore-test/www
```

数据库备份需至少完成“文件非空、工具可读、恢复命令说明”三项检查。若教师安排独立测试库，可按实验15、16执行真实恢复；不得在最终业务库上直接覆盖测试。

### 任务十：同步Git版本

复制脱敏模板，不复制含真实认证信息的完整配置：

```bash
cd ~/m1-project/git-lab
cp templates/techcorp.conf.example templates/techcorp-final.conf.example
sed -n '1,120p' templates/techcorp-final.conf.example
```

补充架构文档：

````bash
cat > docs/final-architecture.md <<'EOF'
# TechCorp Linux服务器交付架构

- 对外入口：SSH/22、Nginx/80。
- 本地后端：techcorp-api，监听127.0.0.1:5000。
- 本地数据：MySQL/3306、MongoDB/27017、Redis/6379。
- 运维保障：systemd、journal、firewalld、SELinux、备份、Git、巡检脚本。
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

### 任务十一：运行统一巡检

```bash
cd ~/m1-project/git-lab
bash -n scripts/server-health.sh
./scripts/server-health.sh \
    > ~/m1-project/final/evidence/health-final.log 2>&1
HEALTH_CODE=$?
cat ~/m1-project/final/evidence/health-final.log
printf 'health_exit_code=%s\n' "$HEALTH_CODE"
```

实验19脚本尚未检查5000端口和`techcorp-api`服务。将它们分别加入数组：

```bash
SERVICES=(nginx techcorp-api mysqld mongod redis sshd)
PORTS=(22 80 5000 3306 27017 6379)
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

设置者在实验配置中制造一处缺少分号或括号错误。排查者应使用：

```bash
sudo nginx -t
systemctl status nginx --no-pager
sudo journalctl -u nginx -n 50 --no-pager
```

修复后必须先`nginx -t`，再重新加载并验证三个URL。

### 故障卡B：后端服务工作目录错误

设置者先备份单元文件，再把`WorkingDirectory`改为不存在目录并重启。排查者应使用：

```bash
systemctl status techcorp-api --no-pager
sudo journalctl -u techcorp-api -n 50 --no-pager
sudo systemd-analyze verify /etc/systemd/system/techcorp-api.service
```

修复后执行`daemon-reload`、重启、检查5000端口和API URL。

### 故障卡C：SELinux阻止Nginx连接后端

设置者记录并临时关闭布尔值：

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

排查顺序：

```bash
systemctl status mysqld --no-pager
sudo ss -lntp | grep ':3306' || true
sudo journalctl -u mysqld -n 50 --no-pager
sudo grep -Rns '^[[:space:]]*bind-address' /etc/my.cnf /etc/my.cnf.d 2>/dev/null || true
```

恢复后用客户端认证并查询`company_db`，不能只看到端口就结束。

### 故障卡E：MongoDB认证或配置缩进错误

```bash
systemctl status mongod --no-pager
sudo journalctl -u mongod -n 50 --no-pager
sudo sed -n '1,160p' /etc/mongod.conf
mongosh --host 127.0.0.1 --port 27017
```

区分服务未启动、认证数据库选择错误、用户名错误和YAML缩进错误。

### 故障卡F：Redis未认证或监听范围错误

```bash
systemctl status redis --no-pager
sudo ss -lntp | grep ':6379' || true
sudo grep -nE '^(bind|protected-mode|port|requirepass)' "$REDIS_CONF"
redis-cli
```

不要把`protected-mode no`作为便利修复。最终状态应恢复认证与本机监听。

### 故障卡G：防火墙未开放HTTP

```bash
curl --fail -H 'Host: techcorp.local' http://127.0.0.1/health
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --zone=public --list-all
```

本机访问正常而Ubuntu客户端访问失败时，再检查Ubuntu地址与路由、Rocky活动zone、接口归属和HTTP服务规则。

### 故障卡H：站点文件标签或权限错误

```bash
namei -l /srv/techcorp/www/index.html
ls -lZ /srv/techcorp/www/index.html
sudo tail -n 30 /var/log/nginx/techcorp_error.log
sudo ausearch -m AVC -ts recent | tail -n 30
```

恢复正确Unix权限和SELinux类型，不使用`chmod 777`，不关闭SELinux。

## 九、最终验收

### 1. 自动检查

创建验收脚本：

```bash
vim ~/m1-project/final/acceptance.sh
```

写入：

```bash
#!/usr/bin/env bash
set -u

fail=0

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1" >&2; fail=$((fail + 1)); }

for service in sshd nginx techcorp-api mysqld mongod redis; do
    if systemctl is-active --quiet "$service"; then
        pass "service ${service} active"
    else
        fail "service ${service} not active"
    fi
done

for port in 22 80 5000 3306 27017 6379; do
    if ss -lntH | awk '{print $4}' | grep -Eq "(^|:|\\])${port}$"; then
        pass "tcp ${port} listening"
    else
        fail "tcp ${port} not listening"
    fi
done

for url in \
    http://127.0.0.1/ \
    http://127.0.0.1/health \
    http://127.0.0.1/api/health.json; do
    if curl --silent --fail --max-time 3 \
        -H 'Host: techcorp.local' "$url" >/dev/null; then
        pass "url ${url}"
    else
        fail "url ${url}"
    fi
done

if [[ -s "$HOME/m1-project/final/backup/company_db.sql" ]]; then
    pass 'MySQL backup exists and is not empty'
else
    fail 'MySQL backup missing or empty'
fi

if find "$HOME/m1-project/final/backup/mongodb" -type f -print -quit 2>/dev/null | grep -q .; then
    pass 'MongoDB backup files exist'
else
    fail 'MongoDB backup files missing'
fi

if git -C "$HOME/m1-project/git-lab" diff --quiet && \
   git -C "$HOME/m1-project/git-lab" diff --cached --quiet; then
    pass 'Git tracked working tree clean'
else
    fail 'Git tracked working tree has uncommitted changes'
fi

printf 'failed_checks=%d\n' "$fail"
(( fail == 0 ))
```

运行并保留结果：

```bash
chmod 750 ~/m1-project/final/acceptance.sh
bash -n ~/m1-project/final/acceptance.sh
~/m1-project/final/acceptance.sh \
    > ~/m1-project/final/evidence/acceptance-final.log 2>&1
ACCEPT_CODE=$?
cat ~/m1-project/final/evidence/acceptance-final.log
printf 'acceptance_exit_code=%s\n' "$ACCEPT_CODE"
```

自动检查不包含数据库密码和业务数据内容，因此还必须完成以下人工验收。

### 2. 人工验收清单

- [ ] 能说明当前主机名、IPv4地址、默认路由和DNS。
- [ ] 能从Ubuntu客户端通过SSH登录Rocky服务器。
- [ ] 能从Ubuntu客户端访问首页、Nginx健康页和API健康数据。
- [ ] 5000、3306、27017、6379未直接对外开放。
- [ ] SELinux为Enforcing，Nginx反向代理仍可用。
- [ ] MySQL认证后能查询关系型数据。
- [ ] MongoDB未认证访问被拒绝，认证后能查询文档。
- [ ] Redis未认证业务命令被拒绝，认证后能读写键值。
- [ ] MySQL和MongoDB备份存在，网站恢复抽查无差异。
- [ ] Git仓库没有真实密码、私钥、日志和数据库转储。
- [ ] 巡检脚本能检查系统、服务、端口和Web健康页。
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
