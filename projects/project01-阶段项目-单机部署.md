# 阶段项目：单机 Linux Web 服务部署与排障

> 对应单元：U33-U36｜课时：8（4次大课 × 90分钟）｜类型：2-3人小组
> 前置：U01-U32核心内容；Lab01-Lab38按进度表完成核心部分

## 一、项目目标

从一台"裸" Rocky Linux 服务器开始，搭建一套完整的 Web 服务环境：

```
用户 → Nginx(80/8080) → MariaDB(3306) + Redis(6379)
                                   ↑ Git 管理代码
                                   ↑ Shell 巡检脚本
```

---

## 二、四次大课实施安排

| 单元 | 阶段 | 课堂任务 | 当堂成果 |
|---|---|---|---|
| U33 | 项目发布与设计 | 需求、角色、端口、安全、验收标准；恢复干净快照并检查环境 | 项目计划、端口表、环境基线 |
| U34 | 服务集成部署 | Nginx、MariaDB、Redis、Git和Shell巡检 | 可运行服务、配置与脚本 |
| U35 | 故障注入与恢复 | 教师注入3-4个故障，学生按证据链定位 | 故障报告、恢复验证 |
| U36 | 文档、答辩与总结 | 整理部署文档、随机操作、个人问答 | 项目归档与答辩成绩 |

### U33：项目设计与环境基线（90分钟）

1. 阅读项目目标，画出单机服务关系和端口表。
2. 明确Nginx、MariaDB、Redis只是在同一服务器上分别提供服务，本阶段不开发业务系统。
3. 恢复干净快照，检查系统版本、IP、DNS、软件源、时间和磁盘空间。
4. 设计账号、数据库监听、Redis认证、防火墙和SELinux策略。
5. 建立Git仓库和任务清单，每完成一个阶段提交一次。

环境基线命令：

```bash
hostnamectl
ip -br addr
ip route
df -h
systemctl --failed
firewall-cmd --list-all
getenforce
```

> **U33验收**：提交服务关系图、端口与暴露范围表、环境基线和实施计划。

## 三、U34：服务集成部署（90分钟）

### 第一部分：Nginx 部署与虚拟主机（35分钟）

#### 步骤1：安装 Nginx

```bash
sudo dnf install -y nginx
sudo systemctl enable --now nginx
systemctl status nginx                    # active (running) ✓
ss -tlnp | grep :80                      # 80端口在监听 ✓
```

#### 步骤2：创建公司官网首页

```bash
sudo cp /usr/share/nginx/html/index.html /usr/share/nginx/html/index.html.bak

sudo tee /usr/share/nginx/html/index.html << 'HTML'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>极客科技 - 首页</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; line-height: 1.6; color: #333; }
header { background: #2c3e50; color: white; padding: 20px 0; }
header h1 { text-align: center; font-size: 2em; }
header p { text-align: center; margin-top: 5px; color: #bbb; }
nav { background: #34495e; padding: 10px 0; text-align: center; }
nav a { color: white; margin: 0 15px; text-decoration: none; font-size: 14px; }
nav a:hover { color: #3498db; }
main { max-width: 800px; margin: 30px auto; padding: 0 20px; }
section { margin-bottom: 30px; }
section h2 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; margin-bottom: 15px; }
footer { background: #2c3e50; color: #bbb; text-align: center; padding: 15px; margin-top: 40px; font-size: 13px; }
.service-list { list-style: none; padding: 0; }
.service-list li { padding: 10px; border-bottom: 1px solid #eee; }
.service-list li:before { content: "▸ "; color: #3498db; font-weight: bold; }
</style>
</head>
<body>
<header>
  <h1>🚀 极客科技</h1>
  <p>让运维更简单，让部署更高效</p>
</header>
<nav>
  <a href="/">首页</a><a href="/about">关于我们</a><a href="/services">核心服务</a><a href="/contact">联系我们</a>
</nav>
<main>
  <section>
    <h2>关于极客科技</h2>
    <p>极客科技成立于2024年，专注于云计算与自动化运维。为企业提供从服务器管理、容器化部署到监控告警的一站式运维解决方案。</p>
  </section>
  <section>
    <h2>核心服务</h2>
    <ul class="service-list">
      <li><strong>Linux 服务器运维</strong> — 系统安装、性能调优、安全加固、故障排查</li>
      <li><strong>Docker 容器化部署</strong> — 微服务架构、Compose编排、CI/CD流水线</li>
      <li><strong>监控告警系统</strong> — Prometheus + Grafana 监控面板</li>
      <li><strong>数据库管理与备份</strong> — MySQL/MariaDB 运维、主从复制、自动备份</li>
    </ul>
  </section>
</main>
<footer>
  <p>&copy; 2026 极客科技 | Powered by Nginx on Rocky Linux 9</p>
</footer>
</body>
</html>
HTML

# 放行防火墙
sudo firewall-cmd --add-service=http --permanent && sudo firewall-cmd --reload

# 验证
curl -s http://localhost | head -10
curl -I http://localhost | grep "200 OK"
```

> **验收点1**：curl 返回 200 OK，浏览器访问 `http://你的VM_IP` 看到完整官网。

#### 步骤3：配置虚拟主机（管理后台）

```bash
# 创建管理后台
sudo mkdir -p /var/www/admin
sudo tee /var/www/admin/index.html << 'HTML'
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>管理后台</title>
<style>
body{font-family:sans-serif;margin:30px;background:#f5f6fa;color:#2c3e50}
h1{color:#e74c3c;text-align:center}
.stats{display:flex;gap:20px;margin:30px 0}
.card{background:white;padding:20px;border-radius:8px;flex:1;min-width:180px;box-shadow:0 2px 4px rgba(0,0,0,0.1);text-align:center}
.card h3{color:#7f8c8d;font-size:14px;margin-bottom:10px}
.card .value{font-size:28px;font-weight:bold;color:#2c3e50}
table{width:100%;border-collapse:collapse;background:white;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
th{background:#34495e;color:white;padding:10px;text-align:left}
td{padding:10px;border-bottom:1px solid #eee}
</style></head>
<body>
<h1>🔐 极客科技 - 管理后台</h1>
<div class="stats">
  <div class="card"><h3>服务器状态</h3><div class="value" style="color:#27ae60">● 正常</div></div>
  <div class="card"><h3>今日访问</h3><div class="value">1,234</div></div>
  <div class="card"><h3>活跃用户</h3><div class="value">89</div></div>
  <div class="card"><h3>系统负载</h3><div class="value">0.15</div></div>
</div>
<h2>服务运行状态</h2>
<table>
<tr><th>服务</th><th>端口</th><th>状态</th></tr>
<tr><td>Nginx</td><td>80,8080</td><td style="color:#27ae60">● 运行中</td></tr>
<tr><td>MariaDB</td><td>3306</td><td style="color:#27ae60">● 运行中</td></tr>
<tr><td>Redis</td><td>6379</td><td style="color:#27ae60">● 运行中</td></tr>
</table>
</body></html>
HTML

# 配置虚拟主机
sudo tee /etc/nginx/conf.d/admin.conf << 'EOF'
server {
    listen 8080;
    server_name _;
    root /var/www/admin;
    index index.html;
    allow 127.0.0.1;
    allow 192.168.200.0/24;
    deny all;
    access_log /var/log/nginx/admin-access.log;
    error_log  /var/log/nginx/admin-error.log;
}
EOF

sudo nginx -t && sudo systemctl reload nginx

# 验证
curl -s http://localhost:8080 | head -5       # ✓ 管理后台
curl -s http://localhost | head -5             # ✓ 官网首页
```

> **验收点2**：80端口=官网，8080端口=管理后台。外部 IP 无法访问 8080（IP 白名单生效）。

---

### 第二部分：MariaDB 数据库部署（25分钟）

#### 步骤4：安装与安全初始化

```bash
sudo dnf install -y mariadb-server
sudo systemctl enable --now mariadb

# 安全初始化
sudo mysql_secure_installation
# Enter current password: 直接回车 → n(socket auth) → Y(设密码) → DBroot123!
# → Y(删匿名) → Y(禁root远程) → Y(删test库) → Y(刷权限)

# 安全：只监听本地
echo "bind-address = 127.0.0.1" | sudo tee -a /etc/my.cnf.d/mariadb-server.cnf
sudo systemctl restart mariadb
ss -tlnp | grep :3306                       # 127.0.0.1:3306 ✓
```

#### 步骤5：创建数据库、用户和测试数据

```sql
mysql -u root -p
```

```sql
CREATE DATABASE company_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE USER 'db_admin'@'localhost' IDENTIFIED BY 'AdminPass123!';
GRANT ALL PRIVILEGES ON company_db.* TO 'db_admin'@'localhost';

CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'AppPass456!';
GRANT SELECT, INSERT, UPDATE, DELETE ON company_db.* TO 'app_user'@'localhost';

CREATE USER 'readonly'@'localhost' IDENTIFIED BY 'ReadPass789!';
GRANT SELECT ON company_db.* TO 'readonly'@'localhost';

FLUSH PRIVILEGES;
SELECT User, Host FROM mysql.user WHERE User IN ('db_admin','app_user','readonly');
```

```sql
USE company_db;
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    department VARCHAR(50),
    email VARCHAR(100),
    hire_date DATE
);
INSERT INTO employees (name, department, email, hire_date) VALUES
    ('张三','技术部','zhangsan@company.com','2024-03-15'),
    ('李四','运维部','lisi@company.com','2024-06-01'),
    ('王五','技术部','wangwu@company.com','2025-01-10'),
    ('赵六','市场部','zhaoliu@company.com','2025-04-20'),
    ('钱七','运维部','qianqi@company.com','2025-08-01');
SELECT * FROM employees;
EXIT;
```

#### 步骤6：数据库备份

```bash
mkdir -p ~/backups
mysqldump -u root -p company_db > ~/backups/company_db-$(date +%Y%m%d).sql
ls -lh ~/backups/
grep "INSERT INTO" ~/backups/company_db-*.sql
```

> **验收点3**：mysql 可登录，employees 表有 5 条数据，备份文件完整。

---

### 第三部分：Redis 缓存部署（15分钟）

#### 步骤7：安装与安全配置

```bash
sudo dnf install -y redis

# 安全配置
sudo sed -i 's/^# requirepass.*/requirepass RedisPass2026!/' /etc/redis/redis.conf
sudo sed -i 's/^bind .*/bind 127.0.0.1/' /etc/redis/redis.conf
echo 'rename-command FLUSHDB ""' | sudo tee -a /etc/redis/redis.conf
echo 'rename-command FLUSHALL ""' | sudo tee -a /etc/redis/redis.conf
echo 'rename-command CONFIG ""' | sudo tee -a /etc/redis/redis.conf

sudo systemctl enable --now redis

# 验证
redis-cli -a RedisPass2026! PING           # PONG
redis-cli -a RedisPass2026! SET company "极客科技"
redis-cli -a RedisPass2026! GET company
redis-cli -a RedisPass2026! INCR visitors
redis-cli -a RedisPass2026! INFO server | head -5
```

> **验收点4**：PING→PONG，SET/GET 正常，FLUSHDB 被禁用。

---

### 第四部分：Git 管理代码（10分钟）

#### 步骤8：创建仓库并跟踪项目文件

```bash
mkdir -p ~/web-project && cd ~/web-project
git init

sudo cp /usr/share/nginx/html/index.html ./index.html
sudo chown student:student ./index.html
sudo cp -r /var/www/admin ./admin
sudo chown -R student:student ./admin

git add index.html admin/
git commit -m "v1.0: 极客科技官网 + 管理后台上线"

echo "<!-- v1.1 -->" >> index.html
git add index.html
git commit -m "v1.1: 添加页面版本标记"

cat > README.md << 'DOC'
# 极客科技 Web 项目
- Nginx：80端口(官网) + 8080端口(管理后台)
- MariaDB：company_db (employees表,5条记录)
- Redis：缓存服务
DOC

git add README.md
git commit -m "v1.2: 添加项目说明"

git log --oneline
```

> **验收点5**：`git log --oneline` 显示至少 3 次提交。

---

### 第五部分：Shell 巡检脚本（5分钟）

#### 步骤9：编写自动化巡检脚本

```bash
cat > ~/ops-check.sh << 'SCRIPT'
#!/bin/bash
echo "========================================="
echo "  极客科技 服务器巡检报告"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S') | 主机: $(hostname)"
echo "========================================="
echo ""
echo "【系统负载】$(uptime | awk -F'load average:' '{print $2}')"
echo ""
echo "【内存使用】"
free -h | grep -E "^Mem|^Swap"
echo ""
echo "【磁盘使用】"
df -h | grep -E "^/dev|Filesystem"
echo ""
echo "【服务状态】"
for s in nginx mariadb redis sshd; do
    systemctl is-active --quiet $s && echo "  [$s] ✓" || echo "  [$s] ✗ FAULT!"
done
echo ""
echo "【监听端口】"
ss -tlnp | grep -E ":(80|3306|6379|22|8080) " | awk '{print $4, $NF}'
echo ""
echo "【Nginx访问量】$(sudo wc -l /var/log/nginx/access.log 2>/dev/null | awk '{print $1}') 次"
echo ""
echo "========================================="
SCRIPT

chmod +x ~/ops-check.sh
./ops-check.sh
```

> **验收点6**：所有服务显示 ✓，端口和访问量数据正常。

---

## 四、U35-U36：排障实战、文档与答辩

### U35：故障模拟与排查（90分钟）

教师从以下 6 个故障中选 3-4 个注入。

| # | 故障 | 教师操作 | 现象 | 关键排查命令 |
|---|------|---------|------|------------|
| F1 | Nginx停止 | `sudo systemctl stop nginx` | curl Connection refused | `systemctl status nginx` |
| F2 | 防火墙拦截80 | `sudo firewall-cmd --remove-service=http --permanent && reload` | 本机curl通，外部不通 | `firewall-cmd --list-all` |
| F3 | SELinux 403 | `sudo chcon -t user_home_t /usr/share/nginx/html/index.html` | curl 403 | `sudo ausearch -m avc -ts recent` |
| F4 | MariaDB停止 | `sudo systemctl stop mariadb` | mysql连接失败 | `systemctl status mariadb` |
| F5 | Redis密码错误 | 改requirepass重启 | NOAUTH | `redis-cli PING`报错 |
| F6 | 端口占用 | `sudo python3 -m http.server 80 &` | Nginx起不来 | `ss -tlnp \| grep :80` |

#### 排障报告模板

```markdown
### 故障#X：____
**现象**：
**排查过程**：
| 步骤 | 命令 | 输出 | 判断 |
|------|------|------|------|
| 1 | | | |
| 2 | | | |
**根因**：
**修复**：
**验证**：
```

### U36第一部分：项目文档整理（35分钟）

```bash
cat > ~/deploy-report.md << 'DOC'
# 单机 Linux Web 服务部署报告

## 服务器信息
- 主机名：_ | IP：_ | 系统：Rocky Linux 9

## 运行服务
| 服务 | 端口 | 状态 | 自启 |
|------|------|------|------|
| Nginx | 80,8080 | running | enabled |
| MariaDB | 3306(本地) | running | enabled |
| Redis | 6379(本地) | running | enabled |

## 防火墙规则
（粘贴 firewall-cmd --list-all 输出）

## 数据库
- DB: company_db | 表: employees(5条)
- 用户: db_admin(localhost) / app_user(localhost) / readonly(localhost只读)

## 验证清单
- [ ] curl官网200OK  [ ] curl管理后台200OK
- [ ] mysql可登录    [ ] Redis PING→PONG
- [ ] git ≥3次提交   [ ] ops-check.sh输出✓

## 排障记录
（粘贴3-4份排障报告）

## 项目文件
- /usr/share/nginx/html/index.html
- /etc/nginx/conf.d/admin.conf
- ~/backups/company_db-*.sql
- ~/web-project/ (Git仓库)
- ~/ops-check.sh
DOC
```

### U36第二部分：提交与自动验收（20分钟）

```
□ 1. deploy-report.md 完整内容
□ 2. 浏览器访问官网截图
□ 3. 浏览器访问管理后台截图
□ 4. MySQL SELECT * FROM employees 截图
□ 5. Redis PING + SET/GET 截图
□ 6. git log --oneline 截图
□ 7. ops-check.sh 执行截图
□ 8. 3-4份排障报告
□ 9. Nginx admin.conf 内容
□ 10. ops-check.sh 源码
```

### U36第三部分：答辩与随机操作（35分钟）

- 项目结构和安全设计说明：5分钟。
- 服务、端口、日志、备份和巡检演示：10分钟。
- 教师随机指定一个故障或配置变更：10分钟。
- 个人问答与项目复盘：10分钟。

随机任务示例：

- 找出Nginx当前加载的配置和监听端口。
- 证明MariaDB只监听预期地址。
- 从备份恢复一张测试表并验证数据。
- 找出Redis认证或服务启动失败的日志证据。
- 修改巡检脚本，使服务异常时返回非0退出码。

---

## 五、评分标准

| 评分项 | 满分 | 要点 |
|--------|------|------|
| Nginx | 15 | 安装/80端口/虚拟主机/自定义HTML |
| MariaDB | 15 | 安全初始化/bind-address/建库建用户/备份 |
| Redis | 10 | 密码认证/bind限制/危险命令禁用 |
| Git | 10 | 仓库/≥3次提交/README |
| Shell脚本 | 10 | 可执行/输出完整/覆盖关键指标 |
| 安全配置 | 10 | 防火墙/DB监听/Redis密码/SELinux |
| 排障报告 | 15 | 步骤清晰/根因准确/修复正确 |
| 部署文档 | 15 | 格式规范/内容完整 |
