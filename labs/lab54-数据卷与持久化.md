# Lab54：Docker 数据卷深入实践

> 课时：2 | 类型：个人 | 前置：Lab53

## 一、你会学到什么
- 深入理解 bind mount 和 named volume 的区别和适用场景
- 能备份和恢复数据卷
- 能排查卷权限问题
- 能规划多容器数据共享方案

## 二、实验步骤

### 步骤1：bind mount 深入

```bash
# 创建宿主机目录
mkdir -p /tmp/bind-test/{html,logs}
echo "<h1>Bind Mount Deep Dive</h1>" > /tmp/bind-test/html/index.html

# 只读挂载（:ro）
docker run -d --name bind-ro \
  -v /tmp/bind-test/html:/usr/share/nginx/html:ro \
  -p 8086:80 \
  nginx:alpine

# 容器内尝试写入 → 失败
docker exec bind-ro touch /usr/share/nginx/html/test.txt
# touch: cannot touch '/usr/share/nginx/html/test.txt': Read-only file system

# 读写挂载（默认）
docker run -d --name bind-rw \
  -v /tmp/bind-test/logs:/var/log/nginx \
  nginx:alpine

# 容器内可以写入
docker exec bind-rw touch /var/log/nginx/test.log
ls -l /tmp/bind-test/logs/         # ✓ 宿主机能看到
```

### 步骤2：卷权限问题（SELinux）

```bash
# 在启用 SELinux 的系统上，bind mount 可能遇到权限问题
# 解决方案：在挂载选项后加 :z 或 :Z

# :z = 共享标签（多个容器共享这个目录）
# :Z = 私有标签（仅当前容器可用，更安全）

docker run -d --name selinux-test \
  -v /tmp/bind-test/html:/usr/share/nginx/html:ro,z \
  nginx:alpine
```

### 步骤3：named volume 深入

```bash
# 创建命名卷
docker volume create app-config
docker volume create app-data

# 查看卷的详细信息
docker volume inspect app-config
# "Mountpoint": "/var/lib/docker/volumes/app-config/_data"
# "Labels": {}
# "Scope": "local"

# 使用多个卷
docker run -d --name multi-vol \
  -v app-config:/etc/app/config \
  -v app-data:/var/lib/app/data \
  alpine sleep 3600

# 查看容器挂载
docker inspect multi-vol | grep -A10 '"Mounts"'
```

### 步骤4：数据卷备份与恢复

```bash
# 1. 创建测试数据
docker volume create test-data
docker run --rm -v test-data:/data alpine sh -c \
  "echo 'important data' > /data/file.txt && echo 'more data' > /data/file2.txt"

# 2. 备份：用临时容器打包 volume 内容
docker run --rm \
  -v test-data:/source:ro \
  -v /tmp/backup:/backup \
  alpine \
  tar czf /backup/test-data-backup.tar.gz -C /source .

ls -lh /tmp/backup/test-data-backup.tar.gz

# 3. 模拟数据丢失：删除 volume
docker volume rm test-data

# 4. 恢复：创建新 volume，从备份解压
docker volume create test-data-restored
docker run --rm \
  -v test-data-restored:/target \
  -v /tmp/backup:/backup \
  alpine \
  tar xzf /backup/test-data-backup.tar.gz -C /target

# 5. 验证恢复
docker run --rm -v test-data-restored:/data alpine cat /data/file.txt
# important data ✓

docker volume rm test-data-restored
```

### 步骤5：多容器共享数据卷

```bash
# 场景：Web 应用容器 + 日志收集容器 共享同一个 volume

docker volume create shared-logs

# Web 容器：写日志
docker run -d --name web-writer \
  -v shared-logs:/var/log/app \
  alpine sh -c "while true; do echo '[web] log entry' >> /var/log/app/web.log; sleep 5; done"

# 日志收集容器：读日志
docker run -d --name log-collector \
  -v shared-logs:/var/log/app \
  alpine sh -c "while true; do tail -1 /var/log/app/web.log 2>/dev/null; sleep 5; done"

# 查看日志收集容器的输出
sleep 15
docker logs log-collector | tail -5
# [web] log entry ✓ 两个容器共享同一份数据

docker rm -f web-writer log-collector
docker volume rm shared-logs
```

### 步骤6：tmpfs 内存临时存储

```bash
# tmpfs：数据存在内存，不写磁盘，重启消失
docker run --rm -it \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  alpine sh -c "echo 'in memory' > /tmp/test && cat /tmp/test"
# in memory（数据在内存中，速度快，但重启消失）

# 适用场景：临时缓存、敏感临时文件（不留磁盘痕迹）
```

---

## 五、练习题

### 练习1：卷类型对比（20分）

| 特性 | bind mount | named volume | tmpfs |
|------|-----------|-------------|-------|
| 存储位置 | | | |
| 可移植性 | | | |
| Docker 管理 | | | |
| 持久化 | | | |
| 适用场景 | | | |

### 练习2：MySQL 数据持久化完整方案（25分）

1. 创建 named volume `prod-mysql-data`
2. 启动 MySQL，数据卷持久化
3. 创建数据库和表，插入测试数据
4. 备份数据卷到宿主机 `/opt/backups/mysql/`
5. 删除容器和 volume
6. 从备份恢复数据
7. 验证数据完整

### 练习3：卷权限排错（20分）

以下场景，分析可能的原因并写出解决方案：

| 场景 | 现象 | 可能原因 |
|------|------|---------|
| bind mount 后容器写不进去 | Permission denied | |
| 容器内 MySQL 数据目录为空 | 数据没持久化 | |
| 两个容器共享 volume，一个有数据一个没有 | 挂载路径不同 | |

### 练习4：多容器数据共享架构（20分）

设计一个日志收集架构：
- 3 个 Web 容器各自写日志到不同的 volume
- 1 个日志收集容器读取所有日志并汇总
- 画出架构图并标注 volume 挂载关系

### 练习5：volume 管理脚本（15分）

写脚本 `~/docker-volume-backup.sh`：
1. 接受 volume 名作为参数
2. 将 volume 数据备份到 `/opt/docker-backups/卷名_日期.tar.gz`
3. 保留最近 7 天的备份，删除更早的

## 七、常见问题

**Q: bind mount 和 named volume，生产环境推荐哪个？**
A: named volume（Docker 管理，可移植，支持存储驱动，可通过 docker volume 管理）。bind mount 依赖宿主机路径，迁移麻烦，权限管理复杂。

**Q: 容器内写文件到 volume，宿主机能看到吗？**
A: 能。volume 就是宿主机上的一个目录（/var/lib/docker/volumes/卷名/_data），容器内的写操作直接反映到宿主机文件系统。

**Q: 备份 volume 时容器需要停止吗？**
A: 最好停止或至少暂停写入。不停也可以备份，但可能有数据不一致（备份过程中数据在变化）。数据库 volume 备份前建议先锁表或停机。

## 八、课后思考

1. Docker volume 的数据存在 `/var/lib/docker/volumes/` 下。如果这个目录所在的磁盘满了，会发生什么？你作为运维怎么监控和预防？

2. 云环境中有云硬盘（如阿里云云盘）可以直接挂载到 ECS。用云硬盘做 MySQL volume 和用 Docker named volume 相比，各有什么优缺点？
