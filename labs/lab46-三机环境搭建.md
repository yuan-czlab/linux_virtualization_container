# Lab46：三机服务器环境搭建与运维入口

> 课时：2 | 类型：2-3人小组 | 前置：Lab39-Lab42

## 一、你会学到什么

- 能把模板机克隆为web、db、client三种角色
- 能处理克隆后的主机名、machine-id、IP和SSH主机密钥问题
- 能完成三机IP规划、名称解析、连通性和SSH验证
- 能以client作为统一运维入口建立SSH配置和主机清单
- 能形成供Paramiko、Ansible、Fabric及大二下综合实训复用的环境成果

## 二、实验拓扑

```text
                  VMware NAT：192.168.200.0/24
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
 web-server              db-server            client
 192.168.200.10          192.168.200.20       192.168.200.30
 Nginx/应用               MariaDB/Redis         运维入口/测试端
```

> 地址仅为课程模板。若机房VMnet8不是该网段，必须先统一调整规划，不能直接照抄。

## 三、角色分工

| 角色 | 建议负责人 | 主要任务 |
|---|---|---|
| 网络与虚拟机 | 成员A | 克隆、网卡、IP、路由、连通性 |
| 系统与SSH | 成员B | 主机名、hosts、账号、密钥和清单 |
| 文档与验收 | 成员C | 拓扑、IP表、验证矩阵、归档 |

两人小组时由成员B兼任文档；每名成员必须能解释全部环境。

## 四、实验步骤

### 步骤1：填写IP与资源规划表

| 主机名 | vCPU | 内存 | 磁盘 | IP | 网关 | 角色端口 |
|---|---:|---:|---:|---|---|---|
| web-server | | | | | | 22/80/443/5000 |
| db-server | | | | | | 22/3306/6379 |
| client | | | | | | 22 |

要求说明资源分配理由，并预留后续Docker实验所需磁盘空间。

### 步骤2：从模板克隆三台虚拟机

1. 确认模板机关机并存在干净快照。
2. 优先使用完整克隆；磁盘紧张时可使用链接克隆，但必须记录对父模板的依赖。
3. 分别命名为`web-server`、`db-server`、`client`。
4. 确认三台虚拟机MAC地址不同。

> **验收点**：三台虚拟机可独立启动，VMware清单名称和角色一致。

### 步骤3：修改Linux身份信息

在每台机器分别执行对应主机名：

```bash
sudo hostnamectl set-hostname web-server
# 另外两台分别改为 db-server、client

sudo rm -f /etc/machine-id
sudo systemd-machine-id-setup
cat /etc/machine-id
hostnamectl
```

检查三台machine-id不得相同。

若克隆后SSH主机密钥完全相同，重新生成：

```bash
sudo rm -f /etc/ssh/ssh_host_*
sudo ssh-keygen -A
sudo systemctl restart sshd
```

> **验收点**：主机名、machine-id和SSH主机指纹均能区分三台服务器。

### 步骤4：配置静态IP

先查连接名：

```bash
nmcli connection show
ip route
```

以web-server为例：

```bash
CON_NAME=$(nmcli -t -f NAME connection show --active | head -1)
sudo nmcli connection modify "$CON_NAME" \
  ipv4.method manual \
  ipv4.addresses 192.168.200.10/24 \
  ipv4.gateway 192.168.200.2 \
  ipv4.dns "223.5.5.5 119.29.29.29"
sudo nmcli connection up "$CON_NAME"
```

db-server和client分别使用`.20`、`.30`。网关必须以实际VMnet8配置为准。

```bash
ip -br addr
ip route
nmcli device show | grep -E 'IP4.ADDRESS|IP4.GATEWAY|IP4.DNS'
```

> **验收点**：三台IP不冲突、处于同一网段、默认网关正确。

### 步骤5：统一名称解析

三台机器都配置：

```bash
sudo tee -a /etc/hosts <<'EOF'
192.168.200.10 web-server
192.168.200.20 db-server
192.168.200.30 client
EOF

getent hosts web-server db-server client
```

防止重复追加：再次执行前先检查`grep 192.168.200 /etc/hosts`。

### 步骤6：完成连通性验证矩阵

| 来源\目标 | web-server | db-server | client |
|---|---|---|---|
| web-server | — | | |
| db-server | | — | |
| client | | | — |

每台至少执行：

```bash
ping -c 2 web-server
ping -c 2 db-server
ping -c 2 client
```

如果失败，依次检查VM是否运行、网卡是否连接、IP、掩码、VMnet、路由和防火墙。

### 步骤7：建立client统一SSH入口

在client上：

```bash
ssh-keygen -t ed25519 -C "class-client-admin"
ssh-copy-id student@web-server
ssh-copy-id student@db-server

cat > ~/.ssh/config <<'EOF'
Host web
    HostName web-server
    User student
    IdentityFile ~/.ssh/id_ed25519

Host db
    HostName db-server
    User student
    IdentityFile ~/.ssh/id_ed25519
EOF
chmod 600 ~/.ssh/config

ssh web hostname
ssh db hostname
```

> **验收点**：client执行`ssh web hostname`和`ssh db hostname`无需输入远程账号密码。

### 步骤8：准备自动化课程主机清单

在client上创建：

```bash
mkdir -p ~/course-environment
cat > ~/course-environment/inventory.ini <<'EOF'
[web]
web-server ansible_host=192.168.200.10

[database]
db-server ansible_host=192.168.200.20

[linux:children]
web
database

[linux:vars]
ansible_user=student
ansible_ssh_private_key_file=~/.ssh/id_ed25519
EOF
```

当前课程不要求安装Ansible，但要逐项核对清单中的IP、用户和密钥路径。

### 步骤9：生成环境验收报告

在client创建`~/course-environment/acceptance.md`，至少包含：

- 拓扑图和IP规划表
- 三台系统版本、主机名、IP、MAC和machine-id末8位
- 三机ping矩阵
- client到web/db的SSH验证命令与结果
- 当前快照名称和恢复说明
- 已知问题与大二下继续使用时的注意事项

## 五、故障挑战

教师随机注入一个故障：

1. db-server主机名未修改
2. web-server仍使用模板机IP
3. client的`/etc/hosts`地址写错
4. SSH私钥权限改为0644
5. 某虚拟机网卡未连接

小组提交“现象→证据→根因→修复→验证”记录。

## 六、验收标准

- [ ] 三台虚拟机身份信息唯一
- [ ] IP、网关、DNS和hosts配置符合规划
- [ ] 三机ping矩阵全部通过
- [ ] client可通过别名免密登录web和db
- [ ] inventory.ini信息准确
- [ ] 拓扑、IP表、验收报告和恢复说明完整

## 七、常见问题

**Q：克隆后两台机器IP冲突怎么办？**

A：先断开其中一台网卡，再分别修改连接配置；同时确认MAC和machine-id不重复。

**Q：ping通但SSH失败？**

A：检查sshd状态、22端口监听、防火墙、账号、密钥权限和`journalctl -u sshd`日志。

**Q：为什么只从client管理服务器？**

A：统一运维入口便于控制密钥、记录操作并衔接自动化工具。生产中可进一步演化为堡垒机或运维管理节点。

## 八、清理与保留

本实验环境不删除。三台机器分别创建快照`three-node-ready`，并保存IP表、inventory和验收报告，后续Lab47、Docker综合项目及大二下课程继续使用。
