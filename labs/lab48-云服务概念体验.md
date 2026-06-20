# Lab48：云服务概念与虚拟化对照

> 课时：2 | 类型：个人 | 前置：Lab47

## 一、你会学到什么
- 理解云服务器 = 虚拟化技术的产品化封装
- 能将虚拟化概念一一对应到云服务概念
- 了解 cloud-init 自动化部署
- 了解 virt-builder 快速构建

## 二、虚拟化 → 云服务 概念对照

| 虚拟化概念 | 云服务对应 | 说明 |
|-----------|-----------|------|
| ISO 镜像 | 云镜像（Image） | 创建实例的模板 |
| VM 快照 | 云快照（Snapshot） | 数据备份和恢复 |
| 防火墙规则 | 安全组（Security Group） | 控制进出流量 |
| NAT/端口映射 | 弹性公网 IP（EIP） | 对外服务 |
| 虚拟磁盘 | 云硬盘（Cloud Disk） | 持久化存储 |
| virt-install | 云控制台/API 创建实例 | 创建服务器 |
| 模板机 | 自定义镜像 | 预装软件的系统模板 |

## 三、实验步骤

### 步骤1：cloud-init 自动化体验

cloud-init 是云实例首次启动时自动执行的初始化工具。AWS/阿里云/腾讯云都使用它。

```bash
# 安装 cloud-init 相关工具
sudo dnf install -y cloud-init

# 查看 cloud-init 版本
cloud-init --version

# 创建 user-data 文件（云实例的"初始化脚本"）
cat > /tmp/user-data.yaml << 'EOF'
#cloud-config
hostname: auto-deploy
users:
  - name: webadmin
    sudo: ALL=(ALL) NOPASSWD:ALL
    groups: wheel
    shell: /bin/bash
    lock_passwd: false
    passwd: $6$rounds=4096$...   # 加密后的密码（这里用明文示意）

packages:
  - nginx
  - vim
  - bash-completion

write_files:
  - path: /var/www/html/index.html
    content: |
      <h1>Auto-deployed by cloud-init</h1>
      <p>Deployment time: $(date)</p>

runcmd:
  - systemctl enable --now nginx
  - echo "cloud-init deployment completed" > /var/log/deploy.log
EOF

# 说明：在真正的云环境中，创建实例时粘贴这段 YAML，
# 实例启动后自动安装 nginx、创建用户、部署网页
```

### 步骤2：virt-builder 快速构建

```bash
# virt-builder 是快速构建 Linux VM 镜像的工具
sudo dnf install -y libguestfs-tools-c

# 查看可用的模板
virt-builder --list | head -20
# rocky-9.0           x86_64     Rocky Linux 9.0
# ubuntu-22.04        x86_64     Ubuntu 22.04 LTS
# ...

# 快速构建一台 VM（示例，不需要实际执行）
# virt-builder rocky-9.0 \
#   --size 20G \
#   --format qcow2 \
#   --hostname web-auto \
#   --root-password password:root123 \
#   --install "nginx,vim,bash-completion" \
#   --output /var/lib/libvirt/images/web-auto.qcow2

# 参数说明：
# --size        磁盘大小
# --format      磁盘格式（qcow2/raw）
# --hostname    主机名
# --root-password  设置 root 密码
# --install     预装软件包
# --output      输出文件路径
```

### 步骤3：理解安全组

```
安全组 = 云端的防火墙规则

传统环境：
  VM ← firewalld 防火墙规则

云环境：
  云实例 ← 安全组（在云平台配置，独立于实例本身）
  
  入方向规则（Inbound）：
    允许 0.0.0.0/0 TCP:22     # SSH 对所有 IP 开放
    允许 0.0.0.0/0 TCP:80     # HTTP 对所有 IP 开放
    允许 10.0.0.0/8 TCP:3306  # MySQL 只对内网开放
  
  出方向规则（Outbound）：
    允许 0.0.0.0/0 ALL        # 默认允许所有出站流量
```

### 步骤4：国内主流云厂商对照

| 产品 | 阿里云 | 腾讯云 | 华为云 | AWS |
|------|--------|--------|--------|-----|
| 虚拟机 | ECS | CVM | ECS | EC2 |
| 镜像 | 镜像 | 镜像 | 镜像 | AMI |
| 快照 | 快照 | 快照 | 快照 | Snapshot |
| 安全组 | 安全组 | 安全组 | 安全组 | Security Group |
| 公网 IP | 弹性公网 IP | 弹性公网 IP | EIP | Elastic IP |
| 云硬盘 | 云盘 | 云硬盘 | 云硬盘 | EBS |
| 容器 | ACK | TKE | CCE | EKS |

---

## 五、练习题

### 练习1：概念对照（15分）

| 虚拟化操作 | 云服务操作 |
|-----------|-----------|
| 用 ISO 创建 VM | |
| 给 VM 拍快照 | |
| 配置 firewalld | |
| 配置端口转发 | |
| 克隆 VM | |

### 练习2：cloud-init 应用（25分）

写一个 cloud-init user-data，满足以下需求：
1. 主机名：web-prod-01
2. 创建用户 deployer，sudo 免密码
3. 安装 nginx、git、python3
4. 从 Git 仓库克隆网站代码到 /var/www/
5. 启动 nginx

### 练习3：安全组规则设计（25分）

云上的 Web 应用（Nginx + MySQL + Redis），设计安全组规则：

| 端口 | 来源 | 协议 | 用途 |
|------|------|------|------|
| 22 | ? | TCP | SSH 管理 |
| 80 | ? | TCP | HTTP |
| 443 | ? | TCP | HTTPS |
| 3306 | ? | TCP | MySQL |
| 6379 | ? | TCP | Redis |

### 练习4：云服务器成本估算（20分）

假设需要部署一个中等规模的 Web 应用，估算以下配置的月成本（参考阿里云/腾讯云官网）：
- 2 台 4C8G Web 服务器
- 1 台 8C16G 数据库服务器
- 100GB 云硬盘
- 10Mbps 带宽

### 练习5：传统 IDC vs 云服务（15分）

| 对比 | 传统 IDC | 云服务 |
|------|---------|--------|
| 硬件采购周期 | | |
| 扩容速度 | | |
| 前期成本 | | |
| 运维复杂度 | | |
| 适合场景 | | |

## 七、常见问题

**Q: 云服务器和传统虚拟机有什么区别？**
A: 底层都是虚拟化技术。区别在于：云服务器按需付费/弹性伸缩/API 管理/免运维硬件，传统虚拟化需要自己管理物理机和虚拟化平台。

**Q: 安全组和 firewalld 有什么区别？**
A: 安全组是云平台层面的网络 ACL（在实例外部生效），firewalld 是操作系统层面的防火墙（在实例内部生效）。两者配合使用形成纵深防御。

**Q: cloud-init 脚本写错了怎么办？**
A: cloud-init 只在首次启动时执行。如果写错了，需要重新创建实例或重置实例。所以云环境强调"不可变基础设施"——出问题就重建，而不是修复。

## 八、课后思考

1. 云厂商的"弹性伸缩"是怎么实现的？它和你在 M4 学到的虚拟化技术有什么关系？

2. 如果公司决定"上云"，你作为运维需要掌握哪些新技能？（提示：VPC、安全组、云监控、对象存储、云数据库、Terraform/ROS）
