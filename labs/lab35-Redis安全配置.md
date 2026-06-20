# Lab35：Redis 安全配置

> 课时：2 | 类型：个人 | 前置：Lab34

## 一、实验步骤

### 步骤1：设置密码认证

```bash
# 方法1：配置文件永久设置
sudo sed -i 's/^# requirepass.*/requirepass RedisSecure2026!/' /etc/redis/redis.conf
sudo systemctl restart redis

# 验证
redis-cli PING
# (error) NOAUTH Authentication required.
redis-cli -a RedisSecure2026! PING       # PONG
# 或
redis-cli
127.0.0.1:6379> AUTH RedisSecure2026!
OK
```

### 步骤2：限制监听地址

```bash
sudo sed -i 's/^bind .*/bind 127.0.0.1/' /etc/redis/redis.conf
sudo systemctl restart redis
ss -tlnp | grep :6379                    # 127.0.0.1:6379 ✓
```

### 步骤3：禁用危险命令

```bash
# 在 /etc/redis/redis.conf 中添加：
echo 'rename-command FLUSHDB ""' | sudo tee -a /etc/redis/redis.conf
echo 'rename-command FLUSHALL ""' | sudo tee -a /etc/redis/redis.conf
echo 'rename-command CONFIG ""' | sudo tee -a /etc/redis/redis.conf
sudo systemctl restart redis

# 验证
redis-cli -a RedisSecure2026! FLUSHDB
# (error) ERR unknown command
```

### 步骤4：防火墙双层保护

```bash
# 纵深防御：即使 Redis 配置有漏洞，防火墙也在前面挡着
sudo firewall-cmd --add-rich-rule='rule family="ipv4" source address="127.0.0.1" port port="6379" protocol="tcp" accept' --permanent
sudo firewall-cmd --reload
```

---

## 五、练习题

### 练习1：Redis 安全清单（20分）

| 检查项 | 安全配置 | 你的服务器状态 |
|--------|---------|-------------|
| 密码 | requirepass 强密码 | |
| 监听地址 | bind 127.0.0.1 | |
| 保护模式 | protected-mode yes | |
| 危险命令 | FLUSHDB/FLUSHALL/CONFIG 禁用 | |
| 端口 | 默认 6379 或改非标准 | |

### 练习2：真实案例研究（25分）

搜索"Redis 未授权访问 入侵"，回答：
1. 攻击者怎么发现公网 Redis 的？
2. 攻击者利用什么 Redis 命令写入 SSH 公钥？
3. 最少需要哪 2 个配置就能防止这种攻击？

### 练习3：Redis 安全对比（20分）

| 配置 | 安全性 | 风险 |
|------|--------|------|
| bind 0.0.0.0 + 无密码 | | |
| bind 0.0.0.0 + 有密码 | | |
| bind 127.0.0.1 + 无密码 | | |
| bind 127.0.0.1 + 有密码 + 防火墙 | | |

### 练习4：Redis ACL（20分）

Redis 6+ 支持 ACL。创建一个只读用户 `reader`，只能执行 GET 和 HGET。

### 练习5：Redis 端口安全规范（15分）

写一份 Redis 部署安全规范（至少 5 条），适用于生产环境。

## 七、常见问题

**Q: Redis 设置了密码但性能有影响吗？**
A: 几乎没有。密码认证只在连接建立时验证一次，后续命令不验证。QPS 下降可以忽略不计。

**Q: bind 0.0.0.0 + 有密码就一定安全吗？**
A: 不够。Redis 密码是明文传输的（协议没有加密），中间人可以截获密码。应该配合：① bind 内网 IP；② 防火墙限制来源；③ 使用 Redis ACL（Redis 6+）。

**Q: protected-mode 是什么？**
A: Redis 3.2+ 默认开启的保护机制。当 bind 非 127.0.0.1 + 无密码时，protected-mode=yes 会拒绝外部连接。这是一个安全兜底机制。

## 八、课后思考

1. 如果 Redis 被入侵，攻击者可能利用 Redis 做哪些恶意操作？（提示：写入 SSH 公钥、植入 crontab、写入 Webshell、作为跳板扫描内网）

2. 除了 Redis，还有哪些常见中间件存在"未授权访问"风险？如何批量检查公司的所有服务器？
