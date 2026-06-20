# Lab14：Linux 网络基础配置

> 课时：2 | 类型：个人 | 前置：Lab02

## 一、你会学到什么
- 能查看和修改 IP、网关、DNS 配置
- 能用 ip 命令临时修改，用 nmcli 永久配置
- 能用 hostnamectl 设置主机名
- 能配置 /etc/hosts 实现本地域名解析

## 二、实验步骤

### 步骤1：查看当前网络

```bash
ip a                               # 查看所有网卡和 IP
ip a show ens33 | grep inet        # 只看 ens33 的 IP

ip route show                      # 路由表
# default via 192.168.200.2 → 默认网关

cat /etc/resolv.conf               # DNS 配置
hostname                           # 当前主机名
```

### 步骤2：ip 命令临时修改

```bash
# 添加临时 IP（重启失效）
sudo ip addr add 192.168.200.100/24 dev ens33
ip a show ens33 | grep inet        # 两个 IP
sudo ip addr del 192.168.200.100/24 dev ens33  # 删除
```

### 步骤3：nmcli 永久配置

```bash
nmcli connection show              # 查看所有连接

# 查看连接的详细配置
nmcli con show static-net | grep -E "ipv4|DNS|gateway"

# 修改 DNS
sudo nmcli con mod static-net ipv4.dns "223.5.5.5 8.8.8.8"
sudo nmcli con up static-net

# 验证
cat /etc/resolv.conf
```

### 步骤4：hostnamectl

```bash
hostnamectl
sudo hostnamectl set-hostname server01
hostname                           # 验证
cat /etc/hostname                  # 永久生效
sudo hostnamectl set-hostname rocky-vm  # 改回来
```

### 步骤5：/etc/hosts 本地解析

```bash
cat /etc/hosts
# 添加自定义解析
echo "192.168.200.10 myapp.local" | sudo tee -a /etc/hosts
ping -c 2 myapp.local              # 解析为 192.168.200.10

# /etc/hosts 优先级高于 DNS
cat /etc/nsswitch.conf | grep hosts
# hosts: files dns → 先查 files(/etc/hosts)，再查 dns

# 清理测试条目
sudo sed -i '/myapp.local/d' /etc/hosts
```

### 步骤6：网络连通性测试

```bash
ping -c 3 127.0.0.1               # 本地网络栈
ping -c 3 192.168.200.2            # 网关
ping -c 3 223.5.5.5               # 外网 IP
ping -c 3 www.baidu.com           # 域名解析
traceroute 223.5.5.5               # 路径跟踪
```

---

## 五、练习题

### 练习1：网络配置填空（15分）

服务器更换机房后需要重新配置网络。填写以下配置对应的命令：

| 配置项 | 新值 | 命令 |
|--------|------|------|
| IP 地址 | 10.0.0.50/24 | |
| 网关 | 10.0.0.1 | |
| DNS | 10.0.0.1, 223.5.5.5 | |
| 主机名 | web-prod-01 | |

### 练习2：网络排障（25分）

以下现象，逐层排查并写出判断：

| 现象 | 最先检查什么 | 可能原因 |
|------|------------|---------|
| ping www.baidu.com 不通 | | |
| curl http://localhost 不通 | | |
| ping 8.8.8.8 通但 ping www.baidu.com 不通 | | |
| 本机服务正常但外部无法访问 | | |

### 练习3：/etc/hosts 应用（20分）

1. 在 /etc/hosts 中添加三条记录，模拟内网三台服务器（web/db/cache）
2. 验证通过主机名 ping 通
3. 把 www.baidu.com 临时解析到 127.0.0.1，观察 curl 行为
4. 删除临时解析
5. /etc/hosts 有什么安全风险？（DNS 劫持）

### 练习4：多网卡配置（20分）

如果服务器有两张网卡 ens33（业务网 192.168.200.0/24）和 ens37（管理网 10.0.0.0/24），各需要配置什么？写出两条 nmcli 命令。

### 练习5：网络配置文件（20分）

1. NetworkManager 的连接配置文件存在哪个目录？
2. 直接编辑配置文件修改 IP，然后怎么让它生效？
3. nmcli 方式和直接编辑配置文件各有什么优缺点？

---

## 六、验收标准
- [ ] ip a 和 ip route 查看网络信息
- [ ] nmcli 永久修改网络配置
- [ ] /etc/hosts 本地解析配置
- [ ] 网络四层连通（本机→网关→外网→域名）
- [ ] 练习 1-5 全部完成

---

## 七、常见问题

**Q: nmcli 修改 IP 后 ping 不通网关？**
A: 三步排查：① `ip a` 确认 IP 和子网掩码正确（/24 不能写成 /32）；② `ip route` 确认默认网关配置正确；③ VMware 虚拟网络编辑器中 NAT 子网是否与 VM IP 同一网段。

**Q: 改了 /etc/resolv.conf 但重启后还原？**
A: 因为 NetworkManager 在管理它。正确改法：`sudo nmcli con mod 连接名 ipv4.dns "DNS地址"` 然后 `sudo nmcli con up 连接名`。不要直接编辑 /etc/resolv.conf。

**Q: ping 域名时特别慢（等好几秒才出结果）？**
A: 可能 DNS 服务器响应慢。换个 DNS 试试：`sudo nmcli con mod static-net ipv4.dns "223.5.5.5 119.29.29.29"`。也可以用 `dig` 命令测量 DNS 查询耗时。

**Q: 桥接模式下 VM 拿不到 IP？**
A: 检查 VMware 虚拟网络编辑器中桥接模式是否绑定了正确的物理网卡（WiFi 和有线是不同的网卡）。换一个网卡试试，或者改用 NAT 模式。

---

## 八、课后思考

1. 如果公司有 100 台服务器，每台都手动配置 /etc/hosts 会有什么问题？有什么更好的方案？（提示：DNS 服务器、Ansible、Consul）
2. 为什么服务器的 IP 通常配置为静态 IP 而不是 DHCP？什么场景下 DHCP 是更好的选择？

---

## 九、清理
```bash
sudo hostnamectl set-hostname rocky-vm  # 如果改了主机名就恢复
sudo sed -i '/myserver.local/d' /etc/hosts
```
