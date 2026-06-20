# Lab13：系统状态监控练习

> 课时：2 | 类型：个人 | 前置：Lab12

## 一、你会学到什么
- 能用 top/htop 实时监控 CPU 和进程
- 能用 free/df/du 查看内存和磁盘
- 能理解 load average 的含义
- 能用 ps/ss 查看进程和网络连接

## 二、实验步骤

### 步骤1：CPU 和负载

```bash
# top 交互式监控（按 q 退出）
top
# 交互键：1 看每核CPU  P 按CPU排序  M 按内存排序  k 杀进程

# uptime 关注负载
uptime
# load average: 0.05, 0.10, 0.08
# 三个数字 = 1分钟/5分钟/15分钟平均负载
# 判断：< CPU核心数 → 正常；> CPU核心数 → 有进程排队

nproc                              # CPU 核心数

# htop（更友好）
sudo dnf install -y htop && htop
```

### 步骤2：内存

```bash
free -h
# Mem: total/used/free/shared/buff/cache/available
# 关键看 available（真正可用的内存）
# buffer/cache 是 Linux 借用空闲内存做缓存，需要时可释放

# 谁在用内存 Top 5
ps aux --sort=-%mem | head -6
```

### 步骤3：磁盘

```bash
df -h                             # 分区使用率，关注 Use% 接近 100% 的
df -i                             # inode 使用率

du -sh /var/log/                  # 目录大小
du -sh /* 2>/dev/null | sort -rh | head -10  # 根下最大10个目录

# 找大文件
sudo find /var -type f -size +100M -exec ls -lh {} \; 2>/dev/null
```

### 步骤4：进程

```bash
ps aux | head -10                 # BSD 风格快照
ps -ef | head -10                 # Unix 风格
pstree -p | head -20              # 进程树

# 监控特定进程
pgrep -a nginx                    # 找 nginx 的 PID
```

### 步骤5：端口和网络

```bash
ss -tlnp                          # TCP 监听端口
ss -tunlp                         # TCP+UDP 监听端口
ss -tanp | grep ESTAB | wc -l     # 当前建立连接数
```

### 步骤6：写巡检脚本

```bash
cat > ~/health-check.sh << 'SCRIPT'
#!/bin/bash
echo "========== 系统巡检 $(date) =========="
echo "[负载]"; uptime
echo "[内存]"; free -h | grep -E "^Mem|^Swap"
echo "[磁盘]"; df -h | grep -E "^/dev|Filesystem"
echo "[服务]"
for s in sshd nginx mariadb redis; do
  systemctl is-active --quiet $s && echo "  $s: ✓" || echo "  $s: ✗"
done
echo "[端口]"; ss -tlnp | tail -n +2 | awk '{print $4}' | sort -u
echo "========================================="
SCRIPT
chmod +x ~/health-check.sh
./health-check.sh
```

---

## 五、练习题

### 练习1：load average 判断（15分）

服务器有 4 个 CPU 核心，以下负载值是否正常？

| load average | 正常/异常 | 说明 |
|-------------|----------|------|
| 0.10, 0.15, 0.08 | | |
| 3.50, 2.80, 2.20 | | |
| 8.00, 7.50, 7.00 | | |
| 0.05, 0.03, 15.00 | | |

### 练习2：磁盘空间排查（25分）

模拟磁盘告警场景：

```bash
dd if=/dev/zero of=/tmp/bigfile bs=1M count=100 2>/dev/null
dd if=/dev/zero of=/tmp/bigfile2 bs=1M count=50 2>/dev/null
```

1. 用 `df -h` 找到使用率最高的分区
2. 用 `du -sh` 逐层定位到 `/tmp` 是主要占用者
3. 用 `find` 找出 `/tmp` 下大于 10MB 的文件
4. 判断哪些可以安全删除
5. 如果 df -h 显示 80% 但 df -i 显示 95%，问题是什么？

### 练习3：进程排障（20分）

```bash
# 制造一个异常进程
dd if=/dev/zero of=/dev/null bs=1M &
PID=$!
```

1. 用 top 找到这个进程（按 CPU 排序）
2. 用 `ps -fp $PID` 查看详细信息
3. 用 `cat /proc/$PID/status` 查看进程状态
4. 用 `sudo lsof -p $PID` 查看打开的文件
5. 用 kill 终止它

### 练习4：端口安全检查（20分）

1. 用 `ss -tlnp` 列出所有监听端口
2. 标注每个端口的监听地址（0.0.0.0 vs 127.0.0.1）
3. 判断哪些端口对外暴露是不安全的
4. 对于不安全端口，写出加固建议

### 练习5：完善巡检脚本（20分）

改进 `health-check.sh`，增加：
1. 自动检测磁盘使用率超过 80% 的分区并输出 WARNING
2. 统计内存使用率百分比并输出
3. 输出最近 5 条 sudo 失败记录（如果有）

---

## 六、验收标准
- [ ] top/free/df/ps/ss 五个命令熟练使用
- [ ] 能解释 load average 的含义和判断标准
- [ ] health-check.sh 能正常运行并输出完整报告
- [ ] 练习 1-5 全部完成

## 七、清理
```bash
rm -f /tmp/bigfile /tmp/bigfile2
pkill -f "dd if=/dev/zero of=/dev/null" 2>/dev/null
```
