# Lab38：Shell 运维脚本实战

> 课时：2 | 类型：个人 | 前置：Lab13

## 一、实验步骤

### 步骤1：Shell 脚本基础

```bash
# 第一个脚本
cat > ~/hello.sh << 'EOF'
#!/bin/bash
# 这是我的第一个脚本
NAME="Student"
echo "Hello, $NAME!"
echo "当前时间: $(date)"
echo "当前目录: $(pwd)"
echo "脚本名: $0"
echo "参数个数: $#"
EOF

chmod +x ~/hello.sh
./hello.sh arg1 arg2 arg3
```

### 步骤2：变量和条件判断

```bash
cat > ~/check-disk.sh << 'EOF'
#!/bin/bash
# 检查磁盘使用率

THRESHOLD=80
USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')

echo "根分区使用率: ${USAGE}%"

if [ "$USAGE" -gt "$THRESHOLD" ]; then
    echo "[WARNING] 磁盘使用率超过 ${THRESHOLD}%！"
else
    echo "[OK] 磁盘使用率正常"
fi

# 检查文件是否存在
if [ -f /etc/nginx/nginx.conf ]; then
    echo "Nginx 配置存在"
else
    echo "Nginx 未安装"
fi
EOF

chmod +x ~/check-disk.sh
./check-disk.sh
```

### 步骤3：循环和函数

```bash
cat > ~/check-services.sh << 'EOF'
#!/bin/bash
# 批量检查服务状态

check_service() {
    local svc=$1
    if systemctl is-active --quiet $svc 2>/dev/null; then
        echo "  [$svc] ✓ running"
        return 0
    else
        echo "  [$svc] ✗ NOT running"
        return 1
    fi
}

echo "========== 服务状态检查 =========="
FAIL_COUNT=0

SERVICES="sshd nginx mariadb redis"
for svc in $SERVICES; do
    check_service $svc || ((FAIL_COUNT++))
done

echo "=================================="
echo "异常服务数: $FAIL_COUNT"
EOF

chmod +x ~/check-services.sh
./check-services.sh
```

### 步骤4：系统巡检脚本

```bash
cat > ~/system-check.sh << 'EOF'
#!/bin/bash
echo "========================================="
echo "  系统巡检报告 - $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================="
echo ""

echo ">>> 系统运行时间"
uptime
echo ""

echo ">>> 内存概况"
free -h
echo ""

echo ">>> 磁盘使用"
df -h | grep -E "^/dev|Filesystem"
echo ""

echo ">>> CPU 使用率 Top 3"
ps aux --sort=-%cpu | head -4 | tail -3
echo ""

echo ">>> 内存使用率 Top 3"
ps aux --sort=-%mem | head -4 | tail -3
echo ""

echo ">>> 监听端口"
ss -tlnp | tail -n +2
echo ""

echo ">>> 失败的 systemd 服务"
systemctl list-units --type=service --state=failed --no-legend 2>/dev/null
echo ""

echo "========================================="
echo "  巡检完成"
echo "========================================="
EOF

chmod +x ~/system-check.sh
./system-check.sh
```

### 步骤5：crontab 定时任务

```bash
# 编辑 crontab
crontab -e
# 格式：分 时 日 月 周 命令
# 0 8 * * * /home/student/system-check.sh >> /var/log/system-check.log 2>&1  ← 每天早上8点巡检

# 查看已配置的定时任务
crontab -l

# 常用 crontab 时间写法：
# */10 * * * *  每10分钟
# 0 2 * * *     每天凌晨2点
# 0 2 * * 0     每周日凌晨2点
# 0 0 1 * *     每月1号0点
```

### 步骤6：备份脚本（综合实战）

```bash
sudo mkdir -p /opt/scripts

sudo tee /opt/scripts/backup-web.sh << 'EOF'
#!/bin/bash
# Web 文件和数据库备份脚本

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

mkdir -p "$BACKUP_DIR"

# 1. 备份网站文件
echo "[$(date)] 开始备份网站文件..."
tar -czf "$BACKUP_DIR/web_$DATE.tar.gz" /usr/share/nginx/html/

# 2. 备份数据库
echo "[$(date)] 开始备份数据库..."
mysqldump -u root -p'DBroot123!' --single-transaction appdb 2>/dev/null \
  | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# 3. 清理旧备份
echo "[$(date)] 清理 ${RETENTION_DAYS} 天前的备份..."
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete

echo "[$(date)] 备份完成"
ls -lh "$BACKUP_DIR" | tail -5
EOF

sudo chmod +x /opt/scripts/backup-web.sh
sudo /opt/scripts/backup-web.sh
```

---

## 五、练习题

### 练习1：脚本填空（15分）

补全以下脚本，实现"检查 nginx 是否在运行，不在就重启并记录"：

```bash
#!/bin/bash
LOG="/var/log/nginx-watchdog.log"
if _______; then
    echo "$(date): nginx is running" >> $LOG
else
    echo "$(date): nginx DOWN, restarting..." >> $LOG
    _______
    echo "$(date): restart result: $(_______)" >> $LOG
fi
```

### 练习2：编写日志清理脚本（25分）

写 `/opt/scripts/log-cleaner.sh`：
1. 查找 `/var/log/` 下所有超过 30 天的 `.log` 文件
2. 用 tar 压缩归档到 `/opt/log-archive/`
3. 归档后清空原文件（用 `truncate -s 0`，不要直接 rm）
4. 记录清理日志

### 练习3：编写批量用户创建脚本（25分）

写 `/opt/scripts/batch-users.sh`，接受一个 CSV 文件作为参数：
```
用户名,密码,附加组
dev1,Pass123!,developers
ops1,OpsPass456!,wheel
```

脚本功能：读取 CSV → 创建用户 → 设置密码 → 加入附加组 → 输出创建结果

### 练习4：编写服务监控脚本（20分）

写 `/opt/scripts/service-watchdog.sh`：
1. 检查 nginx/mariadb/redis 三个服务
2. 挂了的自动重启
3. 连续重启 3 次失败则发出告警（写入日志）
4. 配置 crontab 每 5 分钟执行

### 练习5：Shell 排错（15分）

以下脚本有什么问题？写出修正后的版本：

```bash
#!/bin/bash
THRESHOLD = 80                          # 错误1
USAGE = $(df -h / | tail -1)            # 错误2
if [ $USAGE > $THRESHOLD ]              # 错误3
    echo "WARNING"
fi
```

## 七、常见问题

**Q: 脚本中密码硬编码不安全，怎么改进？**
A: ①从环境变量读取 `$DB_PASSWORD`；②从配置文件读取（权限 600）；③用 `source /etc/secrets.conf`；④用密钥管理工具（Vault）。绝对不要硬编码密码！

**Q: `#!/bin/bash` 和 `#!/bin/sh` 有什么区别？**
A: sh 是 POSIX 标准 shell（功能少但兼容性好），bash 是增强版（支持数组、`[[`、`$()` 等扩展）。运维脚本建议用 bash。

**Q: crontab 中脚本不执行怎么办？**
A: ①检查 crontab 格式（分 时 日 月 周）；②crontab 中命令用绝对路径；③重定向错误输出到日志 `>> /tmp/script.log 2>&1`；④检查脚本有无执行权限。

## 八、课后思考

1. Shell 脚本和 Python 脚本在运维自动化中各有什么优势？什么场景用 Shell，什么场景用 Python？

2. 如果你写了 100 个 Shell 脚本散落在各台服务器上，怎么统一管理和版本控制？（提示：Git 仓库 + Ansible/SaltStack 分发）
