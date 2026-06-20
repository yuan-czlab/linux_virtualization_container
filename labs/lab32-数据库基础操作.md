# Lab32：数据库基础操作（运维视角）

> 课时：2 | 类型：个人 | 前置：Lab31

## 一、实验步骤

### 步骤1：创建数据库和用户

```sql
mysql -u root -p
```

```sql
CREATE DATABASE appdb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- utf8mb4 支持中文和 emoji，utf8 是阉割版（只支持3字节）

CREATE USER 'appuser'@'localhost' IDENTIFIED BY 'AppPass123!';
GRANT ALL PRIVILEGES ON appdb.* TO 'appuser'@'localhost';
FLUSH PRIVILEGES;

-- 查看用户
SELECT User, Host FROM mysql.user;
-- 查看权限
SHOW GRANTS FOR 'appuser'@'localhost';
```

### 步骤2：创建表和数据

```bash
mysql -u appuser -pAppPass123! appdb
```

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email) VALUES
    ('张三', 'zhangsan@example.com'),
    ('李四', 'lisi@example.com');

SELECT * FROM users;
EXIT;
```

### 步骤3：创建远程用户

```sql
mysql -u root -p

CREATE USER 'remoteuser'@'192.168.200.%' IDENTIFIED BY 'RemotePass456!';
GRANT SELECT, INSERT, UPDATE, DELETE ON appdb.* TO 'remoteuser'@'192.168.200.%';
FLUSH PRIVILEGES;
```

### 步骤4：运维排障常用 SQL

```sql
SHOW PROCESSLIST;                      -- 查看当前连接
SHOW STATUS LIKE 'Threads_connected';  -- 连接数
SHOW VARIABLES LIKE 'max_connections'; -- 最大连接数
SHOW VARIABLES LIKE '%buffer%';        -- 缓存配置
SHOW ENGINES;                          -- 存储引擎

-- 查数据库大小
SELECT table_schema, ROUND(SUM(data_length+index_length)/1024/1024,2) AS 'MB'
FROM information_schema.tables GROUP BY table_schema;

-- 杀掉卡住的连接
-- KILL 连接ID;
```

---

## 五、练习题

### 练习1：SQL 填空（15分）

| SQL 语句 | 作用 |
|---------|------|
| `CREATE DATABASE test;` | |
| `CREATE USER 'u'@'localhost' IDENTIFIED BY 'p';` | |
| `GRANT SELECT ON db.* TO 'u'@'localhost';` | |
| `FLUSH PRIVILEGES;` | |
| `SHOW PROCESSLIST;` | |

### 练习2：权限设计（25分）

为 Web 应用 `myblog` 设计数据库权限：
1. 创建数据库 `myblog`（utf8mb4）
2. 创建 localhost 用户 `blog_admin`（全部权限，运维用）
3. 创建内网用户 `blog_app`（SELECT/INSERT/UPDATE/DELETE，应用用，来源 192.168.200.%）
4. 创建只读用户 `blog_reader`（SELECT only，来源 192.168.200.%）

### 练习3：远程连接验证（25分）

1. 在 client VM 上尝试远程连接 db-server 的 MariaDB
2. 需要满足什么条件？（bind-address/防火墙/用户HOST限制）
3. 验证每种用户（blog_app/blog_reader）的实际权限

### 练习4：连接数问题（20分）

1. 模拟连接数超限：多次连接，达到 max_connections
2. 如何查看当前连接数和最大连接数？
3. 如何临时调大 max_connections？

### 练习5：数据库迁移（15分）

从一个服务器迁移到另一个：需要导出什么？用什么工具？写出完整步骤。

## 七、常见问题

**Q: GRANT 之后还是 Permission denied？**
A: 别忘了 `FLUSH PRIVILEGES;`。或者重新登录 MySQL，权限在连接时加载。

**Q: 'appuser'@'localhost' 和 'appuser'@'%' 有什么区别？**
A: MySQL 中用户由"用户名+来源主机"共同标识。localhost 表示只能本机连接，% 表示任何来源。出于安全，生产用户应指定具体来源 IP 或主机名。

**Q: utf8 和 utf8mb4 的区别？**
A: MySQL 的 utf8 是阉割版，最多 3 字节（不支持 emoji 和部分中日韩扩展字符）。utf8mb4 是真正的 UTF-8，最多 4 字节。建库一律用 utf8mb4。

## 八、课后思考

1. 如果开发说"数据库连不上了"，你的排查步骤是什么？（提示：服务运行？端口监听？防火墙？用户权限？来源 IP 限制？）

2. MySQL 用户权限中，`*.*` 和 `dbname.*` 的区别是什么？什么场景下应该授予全局权限，什么场景下应该只授予库级别权限？
