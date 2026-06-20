# Lab31：MariaDB 安装与安全配置

> 课时：2 | 类型：个人 | 前置：Lab13

## 一、你会学到什么
- 理解 MariaDB 与 MySQL 的关系
- 能安装 MariaDB 并完成安全初始化
- 能配置 bind-address 限制监听地址
- 能理解 3306 端口的安全风险

## 二、实验步骤

### 步骤1：安装与启动

```bash
sudo dnf install -y mariadb-server
sudo systemctl enable --now mariadb
systemctl status mariadb               # active (running)
ss -tlnp | grep :3306                  # 3306 在监听
```

### 步骤2：安全初始化（必需！）

```bash
sudo mysql_secure_installation
```

交互回答：
```
Enter current password for root: 直接回车（初始无密码）
Switch to unix_socket auth? → n
Change root password? → Y，设密码：DBroot123!
Remove anonymous users? → Y
Disallow root login remotely? → Y
Remove test database? → Y
Reload privilege tables? → Y
```

### 步骤3：连接测试

```bash
mysql -u root -p                      # 输入 DBroot123!
# 进入 MariaDB 命令行
SHOW DATABASES;
SELECT VERSION();
SELECT USER(), HOST();
EXIT;
```

### 步骤4：安全配置——只监听本地

```bash
ss -tlnp | grep :3306
# 如果 0.0.0.0:3306 → 对外暴露了！

# 配置只监听 127.0.0.1
echo "bind-address = 127.0.0.1" | sudo tee -a /etc/my.cnf.d/mariadb-server.cnf
sudo systemctl restart mariadb
ss -tlnp | grep :3306                 # 127.0.0.1:3306 ✓
```

**为什么**：数据库端口（3306）暴露在公网是严重安全隐患。应用通常和数据库在同一台服务器或通过内网/VPN连接。

### 步骤5：MariaDB 目录结构

```bash
ls -l /var/lib/mysql/                 # 数据库数据文件
ls -l /var/log/mariadb/               # 日志
ls -l /etc/my.cnf.d/                  # 配置文件
```

---

## 五、练习题

### 练习1：MariaDB vs MySQL（15分）

| 问题 | 答案 |
|------|------|
| MariaDB 和 MySQL 的关系 | |
| 为什么 RHEL/Rocky 默认装 MariaDB？ | |
| MariaDB 的命令和 MySQL 一样吗？ | |
| 默认端口是多少？ | |
| 默认数据目录在哪？ | |

### 练习2：安全审计（25分）

检查你的 MariaDB 安装是否安全：
1. root 密码是否设置？
2. 匿名用户是否删除？
3. root 是否允许远程登录？
4. test 数据库是否删除？
5. bind-address 是否为 127.0.0.1？

写一份安全审计报告。

### 练习3：数据库连接排障（25分）

以下故障，排查并修复：

| 故障 | 制造方式 | 现象 |
|------|---------|------|
| 服务未启动 | `sudo systemctl stop mariadb` | `mysql -u root -p` 报错 |
| 密码错误 | 故意输错密码 | Access denied |
| Socket 文件找不到 | mariadb 没启动 | `ERROR 2002` |

### 练习4：端口安全对比（20分）

对比以下配置的安全性：
- `bind-address = 0.0.0.0` + 无防火墙
- `bind-address = 0.0.0.0` + 防火墙只允许内网
- `bind-address = 127.0.0.1`

哪个最安全？如果应用和数据库不在同一台服务器，应该怎么配？

### 练习5：配置文件管理（15分）

1. MariaDB 的配置文件有哪些？加载顺序是什么？
2. 修改配置文件后如何让变更生效？
3. 如何查看当前 MariaDB 运行时的所有配置参数？

## 七、常见问题

**Q: MariaDB 和 MySQL 什么关系？**
A: MySQL 被 Oracle 收购后，原作者创建了 MariaDB 分支。RHEL/Rocky 默认装 MariaDB。API 和命令完全兼容，学 MariaDB = 学 MySQL。

**Q: mysql_secure_installation 是必须执行的吗？**
A: 生产环境必须。不执行的话：root 无密码、匿名用户存在、测试库存在——严重安全隐患。

**Q: 为什么 bind-address 要设为 127.0.0.1？**
A: 安全。数据库端口（3306）暴露在公网是严重安全风险。如果应用和数据库不在同一台服务器，应该通过内网/VPN 连接，而不是直接暴露 3306。

## 八、课后思考

1. 如果应用和数据库部署在同一台服务器，MySQL 连接用 localhost（走 Unix Socket）和用 127.0.0.1（走 TCP）有什么区别？哪种更快更安全？

2. 查资料：MySQL 8.0 和 MariaDB 10.x 现在有哪些主要差异？在生产环境选哪个更合适？
