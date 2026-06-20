# Lab23：firewalld 高级规则练习

> 课时：2 | 类型：个人 | 前置：Lab22

## 场景一：多区域防火墙策略（40分）

**背景**：服务器有两张网卡：ens33 连接公司内网，ens37 连接管理网段。不同网卡需要不同的防火墙策略。

**你的任务**（用不同 zone 模拟，不需要真的两张网卡）：

### 策略要求

| 网卡/Zone | 信任级别 | 允许的端口 |
|-----------|---------|-----------|
| ens33 → public（默认） | 不信任 | 22, 80, 443 |
| "管理网卡" → internal | 较信任 | 22, 3306, 6379, 8080-8090 |

### 完成步骤

1. 查看 internal zone 的默认配置
2. 在 internal zone 中添加服务/端口规则
3. 验证 public 和 internal zone 的规则互不影响
4. 写出把 ens33 切换到 internal zone 的命令（只写不执行）
5. 回答：如果在 public zone 加了 `--add-port=3306/tcp --permanent` 但没有 reload，这时切换到 internal zone，3306 端口会怎样？

---

## 场景二：rich-rule 实战（30分）

**你的任务**：用 rich-rule 实现以下 4 个需求。

| # | 需求 | rich-rule 命令 |
|---|------|---------------|
| 1 | 只允许 192.168.200.0/24 网段访问 SSH（22端口） | |
| 2 | 拒绝 10.0.0.99 的所有访问 | |
| 3 | 限制 80 端口每 IP 每分钟最多 30 个新连接（防CC攻击） | |
| 4 | 对 22 端口的连接尝试记录日志（前缀 "SSH-ACCESS: "） | |

**提示**：
- 需求1：先移除默认的 ssh service，再加 rich-rule
- 需求3：`limit value="30/m"`
- 需求4：`log prefix="SSH-ACCESS: " level="info"`

---

## 场景三：临时规则 vs 永久规则（30分）

**你的任务**：理解临时规则和永久规则的区别。

1. 加一条临时端口规则（不加 --permanent）：
   ```bash
   sudo firewall-cmd --add-port=9999/tcp
   firewall-cmd --list-all | grep 9999    # ✓ 有
   ```

2. 重载 firewall-cmd：
   ```bash
   sudo firewall-cmd --reload
   firewall-cmd --list-all | grep 9999    # ✗ 没了！
   ```

3. 再加一条临时规则，用 `--runtime-to-permanent` 保存它

4. 重载后验证规则还在

5. 回答：
   - `--reload` 和 `--complete-reload` 有什么区别？
   - 什么场景下适合先用临时规则测试再固化？

---

## 验收标准
- [ ] 场景一：理解 zone 与网卡绑定的概念
- [ ] 场景一：会配置不同 zone 的规则
- [ ] 场景二：4 个 rich-rule 全部配置正确
- [ ] 场景三：理解临时/永久规则的区别和转换

## 清理
```bash
sudo firewall-cmd --remove-port=9999/tcp --permanent 2>/dev/null
sudo firewall-cmd --reload
```

---

## 六、验收标准
- [ ] 能根据需求配置防火墙放行策略
- [ ] 能用 rich-rule 限制特定 IP 访问
- [ ] 能配置端口转发
- [ ] 理解临时规则和永久规则的区别
- [ ] 练习 1-5 全部完成

## 七、常见问题

**Q: firewall-cmd 命令敲完没报错，但规则没有生效？**
A: 检查是否忘了 `--reload`（永久规则需要 reload 才生效），或者 `--permanent` 和临时规则搞混了。用 `firewall-cmd --list-all` 和 `firewall-cmd --list-all --permanent` 分别查看两类规则。

**Q: rich-rule 中 source address 怎么写网段？**
A: `source address="192.168.200.0/24"`。注意 CIDR 格式，/24 表示子网掩码 255.255.255.0。如果写成 /32 就只能匹配单个 IP。

**Q: firewalld 规则太多，怎么管理和备份？**
A: 规则存储在 `/etc/firewalld/zones/` 下的 XML 文件中。备份时直接复制这个目录，恢复时覆盖回去再 reload 即可。

## 八、课后思考

1. 生产环境防火墙的"最小开放原则"具体怎么实施？如果你接手一台已有服务器的防火墙，怎么审计现有规则是否合理？

2. Docker 会自动修改 iptables 规则来实现容器网络，firewalld 也操作 iptables。两者会冲突吗？如果有冲突怎么排查？
