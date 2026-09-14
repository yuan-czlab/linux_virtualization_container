# 实验15：MySQL数据库服务部署与备份恢复

> 所属模块：模块三 企业服务部署与综合运维  
> 建议学时：4学时  
> 实验方式：个人，远程访问可两人互测  
> 对应教材：《模块三 企业服务部署与综合运维》第26章  
> 知识前置：模块二服务运维方法和教材第26章；不要求先掌握Nginx配置\
> 状态依赖：`Linux-L2`中的`rocky-server`，无冲突数据库软件和可用课程软件源；不依赖实验14的Nginx文件\
> 建议起点：`Linux-L2`或完成实验14后的当前环境\
> 项目成果：MySQL服务、业务数据库、最小权限账号、受限远程测试、逻辑备份和恢复验证

## 一、项目情境

TechCorp应用需要使用MySQL保存员工数据。你负责安装MySQL Community Server，完成初始管理员密码处理，创建业务账号，控制监听和网络访问，并通过`mysqldump`完成一次误删后的恢复验证。

## 二、实验目标

### 1. 知识目标

1. 说明MySQL服务进程、客户端、配置、数据目录、日志、监听地址和账号来源。
2. 说明`用户@来源`、管理员账号和业务最小权限。
3. 说明逻辑备份、RPO/RTO基础概念和恢复验证。

### 2. 能力目标

1. 使用官方MySQL Yum仓库或教师离线包安装MySQL 8.4 LTS。
2. 管理mysqld，处理初始临时密码并检查日志。
3. 创建数据库、测试表和最小权限业务账号。
4. 临时完成受限远程连接并恢复本地监听。
5. 使用`mysqldump`备份、恢复到测试库并比较数据。

### 3. 素质目标

1. 不把root账号用于业务程序或远程开放。
2. 不把数据库密码写入Git、截图或公开命令记录。
3. 备份文件必须检查、校验并实际恢复。

## 三、知识准备

```text
MySQL客户端
→ 连接主机、3306端口或本地Socket
→ mysqld验证用户、来源和密码
→ 授权系统检查数据库操作权限
→ 存储引擎读写数据文件
→ 错误日志和审计证据记录运行问题
```

MySQL账号不是单独的用户名，而是`'用户名'@'来源'`。`app_user@localhost`、`app_user@127.0.0.1`与`app_user@192.168.200.%`是不同账号。不同系统的名称解析设置可能使本机TCP连接匹配`localhost`或`127.0.0.1`，本实验分别建立Socket和本机TCP账号，避免把账号匹配问题误判为密码错误。

实验开始前打开[MySQL连接、访问边界与备份恢复动画](../../animations/13-mysql-access-backup/index.html)。先完成“对象与连接”和“远程访问边界”，在创建账号前完成“账号与授权”，进入任务七前完成“备份与恢复”。每一步先预测将经过的入口、匹配账号和允许操作，再用`ss`、`USER()`、`CURRENT_USER()`、`SHOW GRANTS`及恢复数据验证。

本实验使用MySQL 8.4 LTS官方Community包。仓库配置RPM的具体小版本文件名会更新，由教师每学期提供验证过的EL9版本和离线包，不在手册中固定过期下载链接。

## 四、实验环境

- `rocky-server`运行Rocky Linux 9 x86_64，建议4GB内存；MySQL只安装在该机。
- `ubuntu-client`已在实验8配置稳定静态地址，承担远程MySQL客户端验证。
- 使用干净环境，不得在已有MariaDB数据的系统上直接替换。
- 教师提供MySQL 8.4 EL9仓库配置RPM或完整离线包。
- 数据库：`company_db`；表：`employees`。
- 服务名：`mysqld`；默认TCP端口：3306。

## 五、项目任务

1. 检查MySQL/MariaDB冲突并建立安装前基线。
2. 安装MySQL 8.4 LTS并处理临时管理员密码。
3. 创建业务数据库、测试表和最小权限账号。
4. 检查配置、监听、日志和本地TCP连接。
5. 配置一次限定来源的远程访问并回收。
6. 完成逻辑备份、误删、测试恢复和数据验证。

## 六、实验步骤

### 任务一：安装前检查

先确认当前没有停留在`rocky-web`：

```bash
test "$(whoami)" = 'rocky-server' && echo USER_PASS || echo USER_FAIL
test "$(hostnamectl --static)" = 'rocky-server' && echo HOST_PASS || echo HOST_FAIL
```

```bash
mkdir -p ~/m1-project/evidence ~/m1-project/backup/mysql ~/course-packages
{
    cat /etc/os-release
    uname -m
    free -h
    rpm -qa | grep -Ei '^(mysql|mariadb)' || true
    sudo ss -lntp | grep ':3306' || true
} | tee ~/m1-project/evidence/lab15-mysql-before.txt
```

如果已经存在MariaDB或其他MySQL来源，停止安装并由教师决定恢复干净快照或迁移数据。不能让两个来源的软件包直接覆盖唯一数据库。

> **验收点**：确认架构为x86_64、内存满足要求、3306无冲突且没有旧数据库需要保护。

### 任务二：配置官方仓库并安装

#### 步骤1：安装教师提供的仓库RPM

把教师提供的`mysql84-community-release-el9-*.noarch.rpm`放入`~/course-packages`，确认目录中只有一个目标文件：

```bash
find ~/course-packages -maxdepth 1 -name 'mysql84-community-release-el9-*.noarch.rpm' -print
```

安装：

```bash
sudo dnf install -y ~/course-packages/mysql84-community-release-el9-*.noarch.rpm
sudo dnf repolist --enabled | grep -E 'mysql.*community'
```

预期启用MySQL 8.4 LTS Community子仓库。不要同时启用LTS和Innovation两个服务器系列。

#### 步骤2：安装服务器

```bash
sudo dnf install -y mysql-community-server
rpm -q mysql-community-server mysql-community-client
mysqld --version
mysql --version
```

无法联网时，使用教师准备的同版本完整RPM依赖包，不从第三方网盘混合安装。

> **验收点**：服务器和客户端均来自统一MySQL Community 8.4系列。

### 任务三：首次启动和管理员密码

#### 步骤3：启动并检查

```bash
sudo systemctl enable --now mysqld
systemctl is-active mysqld
systemctl is-enabled mysqld
sudo ss -lntp | grep ':3306'
sudo journalctl -u mysqld -n 30 --no-pager
```

首次启动会初始化空数据目录并生成`root@localhost`临时密码。

#### 步骤4：读取临时密码

在本人屏幕查看，不复制到实验报告：

```bash
sudo grep 'temporary password' /var/log/mysqld.log | tail -1
```

使用临时密码登录：

```bash
mysql -u root -p
```

在MySQL提示符中更改为教师指定的强实验密码：

```sql
ALTER USER 'root'@'localhost' IDENTIFIED BY '<教师指定的强实验密码>';
SELECT USER(), CURRENT_USER(), VERSION();
```

退出：

```sql
EXIT;
```

不要把实际密码保留在Markdown、截图或Git历史中。

> **验收点**：能够使用新密码登录，记录MySQL版本和当前账号，但不记录密码。

### 任务四：创建业务数据和最小权限账号

#### 步骤5：创建数据库和表

```bash
mysql -u root -p
```

```sql
CREATE DATABASE company_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE company_db;

CREATE TABLE employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    department VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO employees(name, department, email) VALUES
('Zhang San', 'IT', 'zhangsan@techcorp.local'),
('Li Si', 'OPS', 'lisi@techcorp.local'),
('Wang Wu', 'IT', 'wangwu@techcorp.local');

SELECT * FROM employees;
```

#### 步骤6：创建业务账号

把密码替换为教师指定的实验密码：

```sql
CREATE USER 'app_user'@'localhost' IDENTIFIED BY '<业务实验密码>';
CREATE USER 'app_user'@'127.0.0.1' IDENTIFIED BY '<业务实验密码>';
GRANT SELECT, INSERT, UPDATE, DELETE ON company_db.* TO 'app_user'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON company_db.* TO 'app_user'@'127.0.0.1';
SHOW GRANTS FOR 'app_user'@'localhost';
SHOW GRANTS FOR 'app_user'@'127.0.0.1';
EXIT;
```

以业务账号测试：

```bash
mysql -u app_user -p company_db
```

```sql
SELECT COUNT(*) FROM employees;
INSERT INTO employees(name, department, email)
VALUES('Zhao Liu', 'QA', 'zhaoliu@techcorp.local');
DROP DATABASE company_db;
EXIT;
```

前两项应成功，`DROP DATABASE`应被拒绝。

> **验收点**：Socket业务账号能够进行获批操作，不能删除数据库；同时已为本机TCP创建同权限账号。

### 任务五：监听和本地TCP验证

#### 步骤7：检查有效变量和文件

```bash
mysql -u root -p -e "SHOW VARIABLES WHERE Variable_name IN ('port','bind_address','datadir','log_error');"
sudo ss -lntp | grep ':3306'
sudo ls -ld /var/lib/mysql
sudo tail -n 30 /var/log/mysqld.log
```

使用TCP而不是Unix Socket测试：

```bash
mysql --protocol=TCP -h 127.0.0.1 -P 3306 -u app_user -p company_db -e 'SELECT COUNT(*) AS employee_count FROM employees;'
```

> **验收点**：能够指出端口、监听地址、数据目录和错误日志位置；本地TCP查询成功，并能说明它匹配`app_user@127.0.0.1`或经名称解析后的最具体账号。

### 任务六：受限远程访问

该任务使用实验1、8准备的Ubuntu客户端，并从`~/m1-project/course-env.sh`读取其固定IP。

#### 步骤8：备份并调整监听

```bash
sudo cp -a /etc/my.cnf /etc/my.cnf.d ~/m1-project/backup/mysql/
sudo tee /etc/my.cnf.d/course-network.cnf > /dev/null <<'MYSQLCNF'
[mysqld]
bind-address=0.0.0.0
MYSQLCNF
sudo systemctl restart mysqld
systemctl is-active mysqld
sudo ss -lntp | grep ':3306'
```

`0.0.0.0`扩大了监听范围，因此必须同时限制MySQL账号来源和firewalld来源。

#### 步骤9：创建限定来源账号

登录MySQL：

```bash
source ~/m1-project/course-env.sh
REMOTE_SQL=~/m1-project/backup/mysql/lab15-remote-user.sql
cat > "$REMOTE_SQL" <<SQL
CREATE USER 'remote_app'@'$UBUNTU_CLIENT_IP' IDENTIFIED BY 'Lab15-Remote-Only!';
GRANT SELECT ON company_db.* TO 'remote_app'@'$UBUNTU_CLIENT_IP';
SHOW GRANTS FOR 'remote_app'@'$UBUNTU_CLIENT_IP';
SQL
chmod 600 "$REMOTE_SQL"
mysql -u root -p < "$REMOTE_SQL"
rm -f "$REMOTE_SQL"
```

这里使用仅限隔离实验环境的固定口令，便于从客户端验证；生产环境必须改为独立随机凭据或密钥管理系统。账号host必须是Ubuntu准确地址，不使用`%`开放所有来源。

#### 步骤10：配置来源防火墙

```bash
source ~/m1-project/course-env.sh
IFACE=$(ip route show default | awk 'NR==1 {print $5}')
ZONE=$(firewall-cmd --get-zone-of-interface="$IFACE" 2>/dev/null)
if [[ -z "$ZONE" || "$ZONE" == 'no zone' ]]; then ZONE=$(firewall-cmd --get-default-zone); fi
CLIENT_IP="$UBUNTU_CLIENT_IP"
RULE="rule family=\"ipv4\" source address=\"$CLIENT_IP/32\" port port=\"3306\" protocol=\"tcp\" accept"
printf '%s\n' "$ZONE" > ~/m1-project/backup/mysql/remote-zone.txt
printf '%s\n' "$CLIENT_IP" > ~/m1-project/backup/mysql/remote-client-ip.txt
printf '%s\n' "$RULE" > ~/m1-project/backup/mysql/remote-rule.txt
sudo firewall-cmd --zone="$ZONE" --add-rich-rule="$RULE"
sudo firewall-cmd --zone="$ZONE" --list-rich-rules
```

不要使用普通`--add-port=3306/tcp`，否则会绕过来源限制。

#### 步骤11：客户端验证

Ubuntu客户端安装MySQL命令行客户端：

```bash
sudo apt update
sudo apt install -y mysql-client
mysql --version
```

若机房离线，使用教师提供并验证过的客户端包。然后执行：

```bash
source ~/m1-project/course-env.sh
mysql -h "$ROCKY_SERVER_IP" -P 3306 -u remote_app -p \
  company_db -e 'SELECT id,name,department FROM employees;'
```

从另一非授权来源测试应失败。Ubuntu客户端只承担远程连接验证，不在客户端安装数据库服务端。

> **验收点**：Ubuntu客户端查询成功，账号权限只有SELECT，非授权来源不允许连接。

#### 步骤12：回收临时远程开放

服务器执行：

```bash
ZONE=$(cat ~/m1-project/backup/mysql/remote-zone.txt)
RULE=$(cat ~/m1-project/backup/mysql/remote-rule.txt)
sudo firewall-cmd --zone="$ZONE" --remove-rich-rule="$RULE"
sudo rm -f /etc/my.cnf.d/course-network.cnf
sudo tee /etc/my.cnf.d/course-local.cnf > /dev/null <<'MYSQLCNF'
[mysqld]
bind-address=127.0.0.1
MYSQLCNF
sudo systemctl restart mysqld
sudo ss -lntp | grep ':3306'
```

登录MySQL删除临时远程账号：

```bash
source ~/m1-project/course-env.sh
CLEANUP_SQL=~/m1-project/backup/mysql/lab15-drop-remote-user.sql
printf "DROP USER IF EXISTS 'remote_app'@'%s';\n" "$UBUNTU_CLIENT_IP" > "$CLEANUP_SQL"
chmod 600 "$CLEANUP_SQL"
mysql -u root -p < "$CLEANUP_SQL"
rm -f "$CLEANUP_SQL"
```

最终应看到`127.0.0.1:3306`，证明已恢复仅本机使用的监听策略。

### 任务七：逻辑备份和恢复

#### 步骤13：创建备份

```bash
mkdir -p ~/backup-lab/mysql
BACKUP=~/backup-lab/mysql/company_db-$(date +%Y%m%d-%H%M).sql
mysqldump -u root -p --single-transaction --routines --triggers company_db > "$BACKUP"
test -s "$BACKUP"
printf '%s\n' "$(readlink -f "$BACKUP")" \
  > ~/m1-project/backup/mysql/lab15-latest-backup.path
grep -E 'CREATE TABLE|INSERT INTO' "$BACKUP" | sed -n '1,10p'
sha256sum "$BACKUP" | tee "$BACKUP.sha256"
```

不要把密码放在命令行参数中。备份非空和包含SQL结构只是初步检查，还需要恢复。

#### 步骤14：记录数据基线并模拟误删

```bash
mysql -u root -p company_db -e 'SELECT COUNT(*) AS before_count FROM employees;'
mysql -u root -p company_db -e 'DROP TABLE employees;'
mysql -u root -p company_db -e 'SHOW TABLES;'
```

#### 步骤15：恢复到测试数据库

```bash
BACKUP=$(cat ~/m1-project/backup/mysql/lab15-latest-backup.path)
if [[ ! -s "$BACKUP" ]]; then
  echo "备份不存在或为空：$BACKUP"
else
  mysql -u root -p -e 'DROP DATABASE IF EXISTS company_restore; CREATE DATABASE company_restore CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;'
  sed 's/`company_db`/`company_restore`/g' "$BACKUP" > ~/backup-lab/mysql/company_restore.sql
  mysql -u root -p company_restore < ~/backup-lab/mysql/company_restore.sql
  mysql -u root -p company_restore -e 'SELECT COUNT(*) AS restored_count FROM employees; SELECT * FROM employees;'
fi
```

如果备份中没有`USE company_db`或数据库名，直接导入指定测试库即可，不需要sed替换。先查看备份内容再选择方法。

#### 步骤16：恢复正式实验库

确认测试恢复正确后：

```bash
BACKUP=$(cat ~/m1-project/backup/mysql/lab15-latest-backup.path)
if [[ -s "$BACKUP" ]]; then
  mysql -u root -p company_db < "$BACKUP"
  mysql -u root -p company_db -e 'SELECT COUNT(*) AS final_count FROM employees;'
else
  echo "备份不存在或为空：$BACKUP"
fi
```

> **验收点**：误删前、测试恢复和正式恢复的记录数一致，数据可查询。

### 任务八：保存最终证据

```bash
{
    mysqld --version
    systemctl is-active mysqld
    systemctl is-enabled mysqld
    sudo ss -lntp | grep ':3306'
    mysql -u root -p -e "SELECT user,host FROM mysql.user WHERE user IN ('root','app_user');"
    mysql -u root -p company_db -e 'SELECT COUNT(*) AS employee_count FROM employees;'
    ls -lh ~/backup-lab/mysql
} > ~/m1-project/evidence/lab15-mysql-final.txt
```

该命令组会交互询问密码，不要把密码改成命令行明文。

## 七、独立实践

1. 创建只读账号`report_user@localhost`。
2. 证明它可以查询但不能插入和删除。
3. 为`company_db`创建第二份备份。
4. 恢复到`company_verify`并比较记录数。
5. 删除测试恢复库前先确认正式库和备份均正常。

## 八、验收标准

- [ ] 安装前确认没有需要保护的MariaDB或旧MySQL。
- [ ] MySQL Community Server来自统一8.4 LTS系列。
- [ ] mysqld为active和enabled，版本与端口已记录。
- [ ] root临时密码已更改且未出现在提交材料中。
- [ ] company_db和employees数据完整。
- [ ] app_user遵循最小权限，不能删除数据库。
- [ ] 受限远程访问同时限制账号来源和防火墙来源。
- [ ] 临时远程开放和账号已经回收。
- [ ] 备份非空并生成SHA256。
- [ ] 已完成误删、测试恢复、正式恢复和记录数比较。
- [ ] report_user独立实践完成。

## 九、成果提交

1. `lab15-mysql-before.txt`和`lab15-mysql-final.txt`。
2. 软件仓库和MySQL版本记录。
3. 业务账号授权输出，不包含密码。
4. 受限远程连接和回收记录。
5. 备份文件名、大小、SHA256和恢复验证。
6. 独立只读账号验证。

## 十、常见问题

### Q1：找不到临时密码

确认数据目录是否首次初始化、服务是否成功启动，并检查：

```bash
sudo journalctl -u mysqld -n 80 --no-pager
sudo tail -n 80 /var/log/mysqld.log
```

不要反复删除数据目录重新初始化。

### Q2：新密码被策略拒绝

MySQL默认密码策略通常要求长度、大小写、数字和特殊字符。使用教师指定的强实验密码，不降低策略绕过要求。

### Q3：本地Socket能连接，TCP连接失败

检查`--protocol=TCP`、bind_address、3306监听和账号来源。Socket连接和TCP连接不是同一路径。

### Q4：远程端口可达但Access denied

网络路径已经到达MySQL，继续检查`用户@来源`、密码和授权，不要再扩大防火墙规则。

### Q5：恢复后提示表已存在

恢复前确认目标数据库状态。优先恢复到新的验证库，不要在不清楚现有数据时使用覆盖或删除选项。

## 十一、课后思考与拓展

1. 为什么数据库账号必须同时考虑用户名和来源？
2. 有SQL备份文件为什么不能直接证明可恢复？
3. RPO和RTO会怎样影响备份频率与恢复流程？

## 十二、环境保留

保留mysqld、company_db、两个本机app_user账号和有效备份供实验20使用。删除临时验证库前执行：

```bash
mysql -u root -p -e 'SHOW DATABASES;'
```

确认后可删除`company_restore`和`company_verify`，不要删除`company_db`。

## 十三、官方参考

- [MySQL 8.4：使用MySQL Yum仓库安装](https://dev.mysql.com/doc/refman/8.4/en/linux-installation-yum-repo.html)
- [MySQL 8.4：RPM安装布局](https://dev.mysql.com/doc/refman/8.4/en/linux-installation-rpm.html)
