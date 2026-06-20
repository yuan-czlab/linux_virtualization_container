# Lab22：firewalld 防火墙基础

> 课时：2 | 类型：个人 | 前置：Lab15

## 一、实验步骤

### 步骤1：理解 zone 和 service

```bash
firewall-cmd --get-default-zone          # 通常是 public
firewall-cmd --get-active-zones          # 网卡绑定的 zone

firewall-cmd --list-all                  # 查看完整规则
# services: ssh dhcpv6-client ← 当前放行的服务
# ports: ← 当前放行的端口（空）

firewall-cmd --info-service=ssh          # ssh = 22/tcp
firewall-cmd --info-service=http         # http = 80/tcp
```

### 步骤2：临时规则（立即生效，重启丢失）

```bash
sudo firewall-cmd --add-port=8080/tcp    # 临时开放
firewall-cmd --list-all | grep ports     # 能看到
sudo firewall-cmd --reload               # 重载→消失
```

### 步骤3：永久规则

```bash
sudo firewall-cmd --add-service=http --permanent
sudo firewall-cmd --add-service=https --permanent
sudo firewall-cmd --reload               # 永久规则生效

firewall-cmd --list-all | grep services
# services: ssh dhcpv6-client http https
```

### 步骤4：删除规则

```bash
sudo firewall-cmd --remove-service=http --permanent
sudo firewall-cmd --remove-port=8080/tcp --permanent
sudo firewall-cmd --reload
```

### 步骤5：rich-rule 高级规则

```bash
# 只允许特定 IP 访问 SSH
sudo firewall-cmd --add-rich-rule='rule family="ipv4" source address="192.168.200.0/24" port port="22" protocol="tcp" accept' --permanent

# 封禁 IP
sudo firewall-cmd --add-rich-rule='rule family="ipv4" source address="10.0.0.99" drop' --permanent

sudo firewall-cmd --reload
firewall-cmd --list-rich-rules
```

---

## 五、练习题

### 练习1：防火墙规则设计（25分）

Web 服务器防火墙需求：
- 允许：22(SSH)、80(HTTP)、443(HTTPS)
- MySQL(3306) 只允许本机访问
- Redis(6379) 只允许本机访问

写出完整的 firewall-cmd 命令。

### 练习2：临时 vs 永久（15分）

1. 加一条不带的 --permanent 规则 → 重载 → 还在吗？
2. 加一条带 --permanent 的规则 → 不重载 → 生效吗？
3. 已有临时规则，怎么把它变成永久的？

### 练习3：rich-rule 实战（25分）

用 rich-rule 实现：
1. 只允许 192.168.200.0/24 网段访问 80 端口
2. 限制 80 端口每 IP 每分钟最多 30 个连接
3. 对 22 端口的连接记录日志

### 练习4：zone 切换（20分）

1. 查看 internal zone 的默认规则
2. 如果服务器搬到内网，把网卡切换到 internal zone
3. internal 和 public 的默认规则有什么区别？

### 练习5：firewalld vs iptables vs ufw（15分）

1. firewalld 和 iptables 什么关系？
2. Ubuntu 的 ufw 对应什么命令？
3. 为什么推荐用 firewalld 而不是直接操作 iptables？

---

## 六、验收标准
- [ ] 能解释 firewalld 的 zone 和 service 概念
- [ ] 能用 firewall-cmd --list-all 查看当前规则
- [ ] 能区分临时规则和永久规则
- [ ] 能用 rich-rule 做精细化控制
- [ ] 练习 1-5 全部完成

## 七、常见问题

**Q: 加了永久规则也 reload 了，但规则还是不生效？**
A: 检查网卡是否绑定了其他 zone。`firewall-cmd --get-active-zones` 确认网卡在哪个 zone，规则要加到对应的 zone 才生效。

**Q: --reload 会中断现有连接吗？**
A: 不会。`--reload` 只重载规则，不断开已建立连接。`--complete-reload` 会重置所有状态（可能短暂影响），一般不用。

**Q: firewalld 和 iptables 什么关系？**
A: firewalld 是 iptables/nftables 的上层封装，提供 zone/service 等友好概念。firewalld 底层最终还是操作 iptables/nftables 规则。

**Q: 如何临时关闭防火墙测试是不是防火墙的问题？**
A: 不建议 `systemctl stop firewalld`（可能导致网络异常）。建议 `sudo firewall-cmd --set-default-zone=trusted` 临时放行所有流量，测试完切回来：`sudo firewall-cmd --set-default-zone=public`。

## 八、课后思考

1. 防火墙的"默认拒绝"和"默认允许"策略各有什么优缺点？企业生产环境一般用哪种？为什么？

2. 除了 firewalld，你听说过 nftables 吗？它和 iptables 相比有什么优势？（提示：nftables 是 iptables 的下一代替代品）
