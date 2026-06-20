# Lab33：数据库备份与恢复

> 课时：2 | 类型：个人 | 前置：Lab32

## 一、实验步骤

### 步骤1：mysqldump 逻辑备份

```bash
# 单库备份
mysqldump -u root -p appdb > /tmp/appdb-backup.sql
head -30 /tmp/appdb-backup.sql         # 看备份内容

# 只备份结构（不含数据）
mysqldump -u root -p --no-data appdb > /tmp/appdb-schema.sql

# 全库备份
mysqldump -u root -p --all-databases > /tmp/all-db.sql

# 生产级备份参数
mysqldump -u root -p --single-transaction --routines --triggers appdb > /tmp/appdb-prod.sql
# --single-transaction: 不锁表（InnoDB适用）
```

### 步骤2：恢复备份

```bash
# 模拟数据丢失
mysql -u root -p appdb -e "DROP TABLE users;"
mysql -u root -p appdb -e "SHOW TABLES;"   # Empty

# 恢复
mysql -u root -p appdb < /tmp/appdb-backup.sql
mysql -u root -p appdb -e "SELECT * FROM users;"  # ✓ 数据回来了
```

### 步骤3：备份脚本

```bash
sudo tee /opt/scripts/db-backup.sh << 'SCRIPT'
#!/bin/bash
BACKUP_DIR="/opt/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7
mkdir -p "$BACKUP_DIR"

mysqldump -u root -p'DBroot123!' --single-transaction appdb \
  | gzip > "$BACKUP_DIR/appdb_$DATE.sql.gz"

find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete
echo "Backup: appdb_$DATE.sql.gz"
SCRIPT

sudo chmod +x /opt/scripts/db-backup.sh
```

### 步骤4：crontab 定时备份

```bash
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/scripts/db-backup.sh >> /var/log/db-backup.log 2>&1") | crontab -
crontab -l
```

---

## 五、练习题

### 练习1：备份恢复验证（20分）
1. 在 users 表中插入 3 条新数据
2. 备份数据库
3. 删除 users 表
4. 从备份恢复
5. 验证 3 条数据是否恢复

### 练习2：逻辑备份 vs 物理备份（20分）

| 对比 | mysqldump（逻辑） | 物理备份 |
|------|-----------------|---------|
| 备份内容 | | |
| 可读性 | | |
| 大库速度 | | |
| 恢复方式 | | |
| 适用场景 | | |

### 练习3：增量备份（25分）
假设你有一个 100GB 的数据库，每天全量备份不现实。有什么增量备份方案？（提示：binlog）

### 练习4：备份安全（20分）
1. 备份文件包含敏感数据吗？怎么保护？
2. 备份脚本中密码硬编码安全吗？怎么改进？
3. 备份文件应该存在哪？（本机/远程/云端）

### 练习5：灾难恢复演练（15分）
写出数据库完全丢失后的恢复步骤（按顺序）。

## 七、常见问题

**Q: mysqldump 备份时数据库会锁住吗？**
A: 加 `--single-transaction`（InnoDB 适用）不锁表，备份期间应用可以正常读写。MyISAM 表会锁，需要 `--lock-tables`。

**Q: 备份文件里有密码吗？怎么保护？**
A: mysqldump 不备份密码，只备份数据。但备份文件本身包含敏感数据，应该：①设置文件权限 600；②加密存储；③不要放在 Web 可访问目录。

**Q: 大库备份太慢怎么办？**
A: ①用物理备份（Percona XtraBackup）代替逻辑备份；②主从架构中在从库备份；③分库分表分别备份；④使用云厂商的自动备份服务。

## 八、课后思考

1. 如果数据库有 500GB，每天全量备份需要 4 小时且占用大量磁盘。有什么更高效的备份策略？（提示：全量+增量、binlog、延迟从库）

2. 备份文件应该存哪里？如果存在本机，本机磁盘坏了怎么办？设计一个 3-2-1 备份策略。
