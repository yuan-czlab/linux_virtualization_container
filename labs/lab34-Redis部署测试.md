# Lab34：Redis 部署与基础操作

> 课时：2 | 类型：个人 | 前置：Lab31

## 一、实验步骤

### 步骤1：安装与启动

```bash
sudo dnf install -y redis
sudo systemctl enable --now redis
ss -tlnp | grep :6379            # 确认 6379 监听
# 应该显示 127.0.0.1:6379
```

### 步骤2：redis-cli 基础操作

```bash
redis-cli
```

```redis
PING                              → PONG
SET name "Alice"
GET name                          → "Alice"
SET counter 1
INCR counter                      → 2
INCR counter                      → 3
SET temp "expire" EX 10           # 10秒过期
TTL temp                          # 查看剩余时间
KEYS *                            # 列出所有key
DEL name                          # 删除
DBSIZE                            # key总数
INFO server                       # 服务器信息
INFO stats                        # 命中率统计
INFO memory                       # 内存使用
```

### 步骤3：典型应用场景

```redis
# 缓存用户会话
SET user:1001:session "token-abc123" EX 3600
GET user:1001:session

# 计数器（文章浏览量）
SET article:view:post-42 0
INCR article:view:post-42
INCR article:view:post-42

# 排行榜（有序集合）
ZADD scoreboard 100 "alice" 200 "bob" 150 "charlie"
ZREVRANGE scoreboard 0 -1 WITHSCORES
```

### 步骤4：批量操作与监控

```bash
# 管道批量写入
echo -e "SET k1 v1\nSET k2 v2\nSET k3 v3" | redis-cli

# 查看内存
redis-cli INFO memory | grep used_memory_human

# 监控实时命令
# redis-cli MONITOR    # Ctrl+C 退出
```

---

## 五、练习题

### 练习1：Redis 数据结构（20分）

| 命令 | 数据类型 | 应用场景 |
|------|---------|---------|
| SET/GET | | |
| INCR | | |
| EXPIRE | | |
| LPUSH/RPOP | | |
| ZADD/ZRANGE | | |

### 练习2：缓存击穿实验（25分）

1. 写一个简单的逻辑：查 Redis → 有则返回，无则查 MySQL → 写入 Redis
2. 如果 Redis 挂了，这个逻辑会发生什么？（缓存击穿/穿透）
3. 有什么防护方案？

### 练习3：Redis 性能测试（20分）

```bash
sudo dnf install -y redis-benchmark 2>/dev/null || redis-benchmark
redis-benchmark -t set,get -n 10000 -q
```
记录 SET 和 GET 的 QPS。

### 练习4：Redis vs Memcached（15分）

对比两者的区别：数据类型、持久化、集群、使用场景。

### 练习5：Redis 数据持久化（20分）

1. RDB 和 AOF 分别是什么？有什么区别？
2. Redis 重启后数据还在吗？取决于什么？

## 七、常见问题

**Q: Redis 数据都在内存里，重启会丢吗？**
A: 取决于持久化配置。RDB 定期快照，AOF 记录每条写命令。默认开启 RDB。完全不配置持久化的话，重启确实会丢数据。

**Q: Redis 为什么这么快？**
A: ①纯内存操作；②单线程模型（Redis 6+ 支持多线程 IO），避免锁竞争；③高效的数据结构（SDS、ziplist、skip list）；④epoll 多路复用。

**Q: KEYS * 命令有什么问题？**
A: KEYS * 会遍历所有 key，生产环境有数百万 key 时会导致 Redis 阻塞几秒。替代方案：用 SCAN 游标分批遍历。

## 八、课后思考

1. Redis 可以做消息队列吗？List（LPUSH/BRPOP）和 Stream 类型分别适合什么消息队列场景？

2. 缓存和数据库的一致性怎么保证？先更新数据库还是先更新缓存？为什么？
