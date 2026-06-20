# Lab16：DNS 配置与排障

> 课时：2 | 类型：个人 | 前置：Lab14

## 一、实验步骤

### 步骤1：DNS 配置查看

```bash
cat /etc/resolv.conf                    # DNS 服务器地址
cat /etc/hosts                          # 本地静态解析（优先级最高）
cat /etc/nsswitch.conf | grep hosts     # 解析顺序：files→dns
```

### 步骤2：nslookup 查询

```bash
nslookup www.baidu.com                 # 正向解析
nslookup www.baidu.com 8.8.8.8         # 指定 DNS 服务器查询
nslookup -type=MX baidu.com            # 邮件记录
nslookup -type=NS baidu.com            # 域名服务器记录
```

### 步骤3：dig 详细诊断

```bash
dig www.baidu.com                       # 完整 DNS 响应
dig +short www.baidu.com                # 只看结果
dig +trace www.baidu.com                # 追踪解析全过程
dig www.baidu.com | grep "Query time"   # 查询耗时
```

### 步骤4：/etc/hosts 本地解析

```bash
echo "192.168.200.10 myserver.local" | sudo tee -a /etc/hosts
ping -c 2 myserver.local               # 解析到 192.168.200.10
curl http://myserver.local              # 如果有 Web 服务

# 优先级验证：hosts > DNS
# 如果 hosts 里有，就不会去查 DNS
```

### 步骤5：DNS 排障

```bash
# 排障流程：IP能通但域名不通 → DNS问题
ping -c 2 8.8.8.8                      # ✓ 网络通
ping -c 2 www.baidu.com               # ✗ 域名不通？
# → 检查 /etc/resolv.conf
# → 检查 /etc/hosts 有没有错误条目
# → nslookup 测试 DNS 服务器是否可达
```

---

## 五、练习题

### 练习1：DNS 记录类型（15分）

| 记录类型 | 全称 | 用途 |
|---------|------|------|
| A | | |
| AAAA | | |
| CNAME | | |
| MX | | |
| NS | | |

### 练习2：DNS 排障场景（25分）

完成以下 3 个排障场景：

**场景A**：`ping www.baidu.com` 返回 `ping: www.baidu.com: Name or service not known`
- 排查：`ping 8.8.8.8` 通 → 网络没问题 → `cat /etc/resolv.conf` → DNS 服务器配置错了
- 修复

**场景B**：`ping www.baidu.com` 返回 `PING www.baidu.com (127.0.0.1)`
- 排查：`cat /etc/hosts | grep baidu` → 有人错误添加了 `127.0.0.1 www.baidu.com`
- 修复

**场景C**：nslookup 能解析但 curl 不能
- 为什么 nslookup 和 curl 的行为不同？（nslookup 绕过 /etc/hosts）

### 练习3：内网 DNS 规划（30分）

三台内网服务器，没有 DNS 服务器：
1. 在每台机器的 /etc/hosts 中添加所有机器的记录
2. 验证三台机器能通过主机名互相 ping 通

### 练习4：dig 深度追踪（15分）

1. 用 `dig +trace www.taobao.com` 追踪完整解析
2. 记录经过了几级 DNS 服务器
3. 对比用 `dig www.taobao.com`（不走追踪）的查询时间

### 练习5：DNS 安全（15分）

1. DNS 劫持是什么？/etc/hosts 被篡改会有什么后果？
2. 如何检测 /etc/hosts 被篡改？
3. 写一个命令对比 nslookup 结果和 /etc/hosts 内容是否一致

---

## 六、验收标准
- [ ] 能说出 DNS 解析的优先级（hosts → resolv.conf → DNS递归）
- [ ] 能用 /etc/hosts 做本地域名解析
- [ ] 能用 nslookup 和 dig 查询 DNS 记录
- [ ] 能排查"IP能访问但域名不能访问"的故障
- [ ] 练习 1-5 全部完成

## 七、常见问题

**Q: /etc/resolv.conf 改了但重启就还原？**
A: 因为 NetworkManager 或 systemd-resolved 在管理它。正确改法：`sudo nmcli con mod 连接名 ipv4.dns "DNS地址"` 然后 `sudo nmcli con up 连接名`。

**Q: nslookup 能解析，但 curl/ping 不能？**
A: nslookup 直接向 DNS 服务器查询，绕过 /etc/nsswitch.conf。但 ping/curl 按 nsswitch.conf 的顺序解析。可能 /etc/hosts 里有错误条目覆盖了，或者 DNS 缓存问题。检查 `/etc/nsswitch.conf` 的 hosts 行。

**Q: dig 和 nslookup 用哪个？**
A: 排障用 dig（信息更全，+trace 无敌），快速看一下用 nslookup（输出更简洁）。面试时两个都要会。

**Q: 什么时候需要在 /etc/hosts 加记录？**
A: ①开发/测试环境用假域名；②内网服务器之间用主机名代替 IP 通信；③临时屏蔽广告/恶意域名；④DNS 服务器故障时的紧急临时方案。

## 八、课后思考

1. DNS 劫持是什么？攻击者怎么做到的？如何检测和防范？
2. 如果公司内网有 500 台服务器，用什么方案替代每台机器手动维护 /etc/hosts？（提示：内部 DNS 服务器、CoreDNS、Consul）
