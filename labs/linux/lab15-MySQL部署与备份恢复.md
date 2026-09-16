# 实验15：MySQL数据库服务部署与备份恢复

> 所属模块：模块三 企业服务器部署与综合运维
> 建议学时：4学时
> 实验方式：个人，远程访问由小组互查
> 对应教材：3.2 MySQL数据库服务
> 知识前置：MySQL数据库原理、systemd、firewalld和3.2教材
> 状态依赖：`rocky-server`无冲突数据库软件且课程软件源可用；不依赖实验14文件
> 建议起点：`Linux-L2`
> 项目成果：company_db、最小权限账号、远程访问边界、逻辑备份和恢复证据

## 一、项目情境

TechCorp需要在`rocky-server`运行MySQL保存员工数据。管理员需要完成安装、账号授权、一次受限远程访问以及误删后的恢复验证。验收后数据库恢复为仅本机监听。

## 二、实验规则

1. 仓库RPM使用本学期验证版本，不照抄旧下载链接。
2. 密码只在交互提示符输入，不写入脚本和报告。
3. 远程访问同时限制监听、MySQL账号来源和firewalld来源。
4. 不使用`'user'@'%'`。
5. 逻辑备份必须检查退出状态、文件内容和隔离恢复。
6. 误删前必须确认最新备份可用。

## 三、任务一：安装前检查

确认身份：

```bash
whoami
```

```bash
hostnamectl --static
```

检查冲突软件：

```bash
rpm -qa | grep -Ei '^(mysql|mariadb)'
```

创建目录：

```bash
mkdir -p ~/course-packages
```

```bash
mkdir -p ~/m1-project/backup/mysql
```

```bash
mkdir -p ~/m1-project/evidence
```

把教师提供的EL9仓库RPM放入`~/course-packages`，确认文件：

```bash
find ~/course-packages -maxdepth 1 -name 'mysql*-community-release-el9-*.noarch.rpm' -print
```

只应选择本学期明确验证的一个文件。

## 四、任务二：安装与首次启动

使用实际文件名安装仓库：

```text
sudo dnf install -y ~/course-packages/<实际仓库RPM文件名>
```

检查仓库：

```bash
sudo dnf repolist --enabled | grep -i mysql
```

安装服务端：

```bash
sudo dnf install -y mysql-community-server
```

检查软件包：

```bash
rpm -q mysql-community-server mysql-community-client
```

启动：

```bash
sudo systemctl enable --now mysqld
```

检查：

```bash
systemctl is-active mysqld
```

```bash
systemctl is-enabled mysqld
```

```bash
sudo ss -lntp | grep ':3306 '
```

查看日志：

```bash
sudo journalctl -u mysqld -n 30 --no-pager
```

## 五、任务三：设置管理员密码

只在本人屏幕读取临时密码：

```bash
sudo grep 'temporary password' /var/log/mysqld.log
```

登录：

```bash
mysql -u root -p
```

在`mysql>`提示符执行，替换密码占位符：

```sql
ALTER USER 'root'@'localhost' IDENTIFIED BY '<教师指定的强实验密码>';
```

检查版本：

```sql
SELECT VERSION();
```

退出：

```sql
EXIT;
```

## 六、任务四：创建业务数据和账号

重新登录：

```bash
mysql -u root -p
```

逐条执行：

```sql
CREATE DATABASE company_db CHARACTER SET utf8mb4;
```

```sql
USE company_db;
```

```sql
CREATE TABLE employees (id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(50) NOT NULL, department VARCHAR(50) NOT NULL);
```

```sql
INSERT INTO employees(name,department) VALUES ('Alice','Cloud'),('Bob','Network'),('Carol','Security');
```

```sql
SELECT * FROM employees;
```

创建Socket连接账号：

```sql
CREATE USER 'app_user'@'localhost' IDENTIFIED BY '<业务实验密码>';
```

授权：

```sql
GRANT SELECT, INSERT, UPDATE, DELETE ON company_db.* TO 'app_user'@'localhost';
```

查看：

```sql
SHOW GRANTS FOR 'app_user'@'localhost';
```

退出后测试：

```bash
mysql -u app_user -p company_db
```

执行查询：

```sql
SELECT COUNT(*) FROM employees;
```

## 七、任务五：检查本机运行边界

查看有效变量：

```bash
mysql -u root -p -e "SHOW VARIABLES WHERE Variable_name IN ('port','bind_address','datadir','log_error');"
```

查看监听：

```bash
sudo ss -lntp | grep ':3306 '
```

查看数据目录：

```bash
sudo ls -ld /var/lib/mysql
```

不要直接编辑数据目录中的表文件。

## 八、任务六：受限远程访问

### 8.1 备份配置

检查备份：

```bash
ls -ld ~/m1-project/backup/mysql/my.cnf.d.before-lab15
```

不存在时创建：

```bash
sudo cp -a /etc/my.cnf.d ~/m1-project/backup/mysql/my.cnf.d.before-lab15
```

### 8.2 临时扩大监听

编辑独立片段：

```bash
sudo vim /etc/my.cnf.d/course-network.cnf
```

写入：

```ini
[mysqld]
bind-address=0.0.0.0
```

重启：

```bash
sudo systemctl restart mysqld
```

确认：

```bash
systemctl is-active mysqld
```

```bash
sudo ss -lntp | grep ':3306 '
```

### 8.3 记录Ubuntu地址

在`ubuntu-client`执行：

```bash
ip -brief address
```

记录VMnet8网卡上的纯IPv4地址。

### 8.4 创建限定来源账号

在Rocky登录MySQL：

```bash
mysql -u root -p
```

替换真实地址和密码：

```sql
CREATE USER 'remote_app'@'<Ubuntu实际IPv4>' IDENTIFIED BY '<远程实验密码>';
```

```sql
GRANT SELECT ON company_db.* TO 'remote_app'@'<Ubuntu实际IPv4>';
```

```sql
SHOW GRANTS FOR 'remote_app'@'<Ubuntu实际IPv4>';
```

### 8.5 添加来源受限防火墙规则

查看活动zone：

```bash
firewall-cmd --get-active-zones
```

使用实际zone和Ubuntu地址：

```text
sudo firewall-cmd --zone=<实际活动区域> --add-rich-rule='rule family="ipv4" source address="<Ubuntu实际IPv4>/32" port port="3306" protocol="tcp" accept'
```

### 8.6 Ubuntu远程验证

安装客户端：

```bash
sudo apt install -y default-mysql-client
```

连接：

```text
mysql -h <rocky-server实际IPv4> -P 3306 -u remote_app -p company_db
```

查询：

```sql
SELECT USER(), CURRENT_USER();
```

```sql
SELECT * FROM employees;
```

尝试建表应被最小权限拒绝：

```sql
CREATE TABLE should_fail(id INT);
```

### 8.7 回收远程入口

在Rocky删除运行时规则：

```text
sudo firewall-cmd --zone=<实际活动区域> --remove-rich-rule='rule family="ipv4" source address="<Ubuntu实际IPv4>/32" port port="3306" protocol="tcp" accept'
```

登录MySQL删除远程账号：

```sql
DROP USER 'remote_app'@'<Ubuntu实际IPv4>';
```

把配置片段改为本机监听：

```bash
sudo vim /etc/my.cnf.d/course-network.cnf
```

内容：

```ini
[mysqld]
bind-address=127.0.0.1
```

重启并检查：

```bash
sudo systemctl restart mysqld
```

```bash
sudo ss -lntp | grep ':3306 '
```

## 九、任务七：逻辑备份

创建目录：

```bash
mkdir -p ~/backup-lab/mysql
```

检查是否已有同名备份：

```bash
ls -l ~/backup-lab/mysql/company_db.sql
```

已有文件时先核对并另行保存，不得无提示覆盖。

执行备份：

```bash
mysqldump -u root -p --single-transaction --routines --events --triggers --no-tablespaces company_db > ~/backup-lab/mysql/company_db.sql
```

紧接着检查退出状态：

```bash
echo $?
```

检查非空：

```bash
test -s ~/backup-lab/mysql/company_db.sql
```

查找目标表：

```bash
grep -n 'CREATE TABLE.*employees' ~/backup-lab/mysql/company_db.sql
```

计算哈希：

```bash
sha256sum ~/backup-lab/mysql/company_db.sql
```

## 十、任务八：误删与隔离恢复

记录原始行数：

```bash
mysql -u root -p company_db -e 'SELECT COUNT(*) AS before_count FROM employees;'
```

确认备份通过检查后，模拟误删：

```bash
mysql -u root -p company_db -e 'DROP TABLE employees;'
```

创建隔离数据库：

```bash
mysql -u root -p -e 'DROP DATABASE IF EXISTS company_restore; CREATE DATABASE company_restore CHARACTER SET utf8mb4;'
```

恢复到隔离库：

```bash
mysql -u root -p company_restore < ~/backup-lab/mysql/company_db.sql
```

验证行数：

```bash
mysql -u root -p company_restore -e 'SELECT COUNT(*) AS restored_count FROM employees;'
```

查看关键数据：

```bash
mysql -u root -p company_restore -e 'SELECT * FROM employees ORDER BY id;'
```

隔离恢复正确后，恢复正式库：

```bash
mysql -u root -p company_db < ~/backup-lab/mysql/company_db.sql
```

最终验证：

```bash
mysql -u root -p company_db -e 'SELECT COUNT(*) AS final_count FROM employees; SELECT * FROM employees ORDER BY id;'
```

## 十一、验收标准

- [ ] mysqld为active和enabled。
- [ ] company_db包含employees表和3条初始数据。
- [ ] app_user只具有业务库数据权限。
- [ ] 远程账号只匹配Ubuntu真实IPv4且只有SELECT。
- [ ] firewalld只临时允许Ubuntu来源访问3306。
- [ ] 远程验证后账号和防火墙规则已回收。
- [ ] mysqld最终只监听127.0.0.1。
- [ ] 备份退出状态为0、文件非空且包含employees。
- [ ] 隔离恢复的行数和数据正确。
- [ ] 正式库已经恢复。

## 十二、成果提交

1. 软件版本、服务状态和监听结果。
2. app_user与remote_app的`SHOW GRANTS`。
3. Ubuntu远程查询及越权失败结果。
4. 远程入口回收结果。
5. 备份文件大小、哈希和关键SQL。
6. 误删前、隔离恢复和正式恢复的数据对照。

## 十三、常见问题

### 13.1 找不到临时密码

检查错误日志：

```bash
sudo tail -n 80 /var/log/mysqld.log
```

不要重复初始化已有数据目录。

### 13.2 密码被策略拒绝

使用符合长度、大小写、数字和特殊字符要求的强实验密码，不降低策略。

### 13.3 TCP可达但Access denied

检查`USER()`、`CURRENT_USER()`、账号host和授权，不要反复开放防火墙。

### 13.4 备份文件存在但无法恢复

检查mysqldump退出状态、文件是否非空以及是否包含目标建表语句。

## 十四、环境保留

保留mysqld、company_db、app_user和`~/backup-lab/mysql/company_db.sql`供实验20使用。

删除隔离恢复库前先查看：

```bash
mysql -u root -p -e 'SHOW DATABASES;'
```

确认验收完成后可删除`company_restore`。数据库保持仅本机监听，不保留3306防火墙规则。
