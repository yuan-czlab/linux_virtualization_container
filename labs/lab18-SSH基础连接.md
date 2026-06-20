# Lab18：SSH 远程登录基础

> 课时：2 | 类型：双人（或自己连localhost） | 前置：Lab14

## 一、实验步骤

### 步骤1：确认 sshd 运行

```bash
systemctl status sshd              # active (running)
ss -tlnp | grep :22               # 22 端口在监听
```

### 步骤2：SSH 密码登录

```bash
ssh student@localhost              # 首次连接输 yes 确认指纹
# 输入密码 → 登录成功
exit                               # 退出

cat ~/.ssh/known_hosts             # 查看保存的主机指纹
```

### 步骤3：sshd_config 关键配置

```bash
sudo grep -E "^(Port|PermitRootLogin|PasswordAuthentication|PubkeyAuthentication)" /etc/ssh/sshd_config
# Port 22
# PermitRootLogin yes（安全建议：no）
# PasswordAuthentication yes
# PubkeyAuthentication yes
```

### 步骤4：SSH 排障

```bash
# 端口不对
ssh -p 2222 student@localhost      # Connection refused

# 用户不存在
ssh nobody@localhost               # Permission denied

# 用 -v 调试（最重要！）
ssh -v student@localhost 2>&1 | head -30

# 查看登录日志
sudo grep "sshd" /var/log/secure | tail -10
sudo grep "Failed password" /var/log/secure | tail -5
```

### 步骤5：SSH 安全加固

```bash
# 生产环境建议
# ① PermitRootLogin no
# ② MaxAuthTries 3
# ③ 改默认端口（如 2222）减少扫描
# ④ PasswordAuthentication no（只用密钥）
```

---

## 五、练习题

### 练习1：SSH 故障速查（20分）

| 报错 | 含义 | 第一步排查 |
|------|------|----------|
| `Connection refused` | | |
| `Connection timed out` | | |
| `Permission denied (password)` | | |
| `Host key verification failed` | | |

### 练习2：SSH 安全检查（25分）

1. 查看你的 sshd_config，找出不符合安全最佳实践的配置
2. 写出改进建议和对应的配置修改

### 练习3：SSH 调试（25分）

1. 用 `ssh -v` 连接 localhost，记录关键步骤
2. 从日志中找出：TCP连接建立 → 密钥交换算法 → 认证方式 → 登录成功
3. 用 `ssh -vvv` 对比，多了哪些调试信息？

### 练习4：暴力破解检测（15分）

1. 用 `sudo grep "Failed password" /var/log/secure | wc -l` 统计失败次数
2. 用 `sudo grep "Failed password" /var/log/secure | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn | head -5` 看 Top5 失败来源 IP

### 练习5：SSH 安全加固方案（15分）

写出一份生产服务器 SSH 安全加固清单（至少 5 条），每条约一条配置命令。

---

## 六、验收标准
- [ ] 能用 ssh user@ip 成功登录远程服务器
- [ ] 能看懂 ~/.ssh/known_hosts 的内容
- [ ] 能说出 sshd_config 中 3 个重要配置项
- [ ] 能用 ssh -v 调试连接问题
- [ ] 练习 1-5 全部完成

## 七、常见问题

**Q: SSH 能连但非常慢（等 10-30 秒才出密码提示）？**
A: 经典问题！sshd 默认会做 DNS 反向查询（查登录者的 IP 对应什么域名），如果 DNS 不通就会超时等待。解决：在 `/etc/ssh/sshd_config` 加 `UseDNS no`，然后 `sudo systemctl reload sshd`。

**Q: 为什么不要用 root 直接 SSH 登录？**
A: ① root 用户名固定，攻击者只需要猜密码；② 无法追溯是谁操作的（多人共用 root）；③ 误操作风险大。应该用普通用户+sudo，操作有日志可追溯。

**Q: SSH 连接数有限制吗？**
A: 有，`MaxSessions` 和 `MaxStartups` 控制。一般不需要调，但压测或自动化脚本并发连接多时可能会碰到。查看：`grep -E "MaxSessions|MaxStartups" /etc/ssh/sshd_config`。

**Q: Connection refused 和 Connection timed out 在 SSH 场景下怎么区分？**
A: refused = 服务器收到了但 22 端口没人监听（sshd 没启动或端口不对）。timed out = 请求根本没到（防火墙 DROP、网络不通、IP 错误）。

## 八、课后思考

1. 如果必须在生产环境允许 root SSH 登录，有什么额外的安全措施可以弥补？（提示：限制来源 IP、使用密钥认证+私钥密码、fail2ban、改 SSH 端口）

2. 什么是 SSH 中间人攻击？known_hosts 机制如何防范中间人攻击？如果 known_hosts 中记录的指纹突然变了，你应该怎么做？
