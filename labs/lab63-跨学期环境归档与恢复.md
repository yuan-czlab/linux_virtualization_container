# Lab63：三机环境归档、校验与恢复演练

> 课时：2 | 类型：2-3人小组 | 前置：Lab40、Lab46 | 使用：U52与U72成果归档

## 一、你会学到什么

- 能区分快照、克隆、OVA导出、配置仓库和数据备份的作用
- 能清理临时数据并形成可交付的虚拟机模板
- 能生成文件校验值和版本清单
- 能在另一目录或另一台机器完成恢复验证
- 能为大二下eNSP、网络安全、云计算和企业实训保留统一环境

## 二、归档成果结构

```text
group01-course-environment/
├── README.md
├── topology/
│   ├── network-topology.png
│   └── ip-plan.csv
├── inventory/
│   ├── inventory.ini
│   └── service-port-list.csv
├── config/
│   ├── nginx/
│   ├── scripts/
│   └── compose/
├── backup/
│   ├── database.sql
│   └── restore.md
├── ova/
│   ├── web-server.ova
│   ├── db-server.ova
│   └── client.ova
└── SHA256SUMS.txt
```

严禁归档真实密码、私钥、个人Token和未经脱敏的敏感数据。

## 三、实验步骤

### 步骤1：冻结环境版本

三台机器记录：

```bash
sudo mkdir -p /opt/course-handoff
{
  echo "hostname=$(hostname)"
  echo "os=$(cat /etc/rocky-release 2>/dev/null || cat /etc/os-release | head -1)"
  echo "kernel=$(uname -r)"
  echo "ip=$(hostname -I)"
  echo "date=$(date -Iseconds)"
  rpm -q nginx mariadb-server redis docker-ce 2>/dev/null || true
} | sudo tee /opt/course-handoff/version.txt
```

保存服务和端口状态：

```bash
systemctl --no-pager --type=service --state=running > /tmp/running-services.txt
ss -lntup > /tmp/listening-ports.txt
```

### 步骤2：备份配置和数据

按实际环境执行：

```bash
mkdir -p ~/course-archive/{config,backup,inventory,topology}
sudo cp -a /etc/nginx ~/course-archive/config/ 2>/dev/null || true
cp -a ~/bin ~/course-archive/config/scripts 2>/dev/null || true

# 数据库逻辑备份示例
mysqldump -u root -p --all-databases > ~/course-archive/backup/database.sql

# 验证SQL文件不是空文件
test -s ~/course-archive/backup/database.sql
grep -m1 -E 'MariaDB dump|MySQL dump' ~/course-archive/backup/database.sql
```

编写`backup/restore.md`，记录恢复命令和验证方法。

### 步骤3：清理不应进入模板的内容

```bash
sudo dnf clean all
sudo journalctl --vacuum-time=7d
rm -rf ~/.cache/*
history -c
```

检查但不要误删课程成果：

```bash
sudo du -xhd1 / | sort -h
docker system df 2>/dev/null || true
```

不得把“清理空间”理解为执行未经确认的`docker system prune -a --volumes`。

### 步骤4：创建最终快照并正常关机

```bash
sudo systemctl --failed
sudo shutdown -h now
```

在VMware中分别创建快照：`semester-ready-v1`。

记录快照时间、虚拟机状态和恢复用途。快照只用于短期回退，不能替代OVA和数据备份。

### 步骤5：导出OVA

在VMware Workstation中对关机虚拟机执行：

```text
文件 → 导出为OVF/OVA → 选择小组归档目录
```

如果机房空间不足，可至少导出一台标准模板机，并在README中说明如何克隆为三机及如何恢复角色配置。

### 步骤6：生成校验值

Windows PowerShell：

```powershell
Get-ChildItem .\ova\*.ova | Get-FileHash -Algorithm SHA256 |
  ForEach-Object { "$($_.Hash)  $($_.Path | Split-Path -Leaf)" } |
  Set-Content .\SHA256SUMS.txt

Get-Content .\SHA256SUMS.txt
```

Linux：

```bash
sha256sum ova/*.ova > SHA256SUMS.txt
sha256sum -c SHA256SUMS.txt
```

### 步骤7：编写交接README

README至少包含：

1. 环境用途、系统版本和制作日期
2. 三机角色、资源规格、IP和端口
3. 默认账号说明和首次登录后修改密码要求
4. 导入OVA、网络适配和启动顺序
5. SSH验证、服务验证和数据库恢复方法
6. 与eNSP Cloud节点连接时需要调整的网卡和网段
7. 已知问题、KVM嵌套虚拟化结论和镜像获取方式

### 步骤8：恢复演练

至少选择一台OVA导入到新目录，且不要覆盖原虚拟机。

验证：

```bash
hostnamectl
ip -br addr
ip route
systemctl --failed
ss -lntup
```

恢复测试必须记录：导入时间、网络调整、启动问题、服务状态和修复操作。

> **验收点**：没有恢复演练的归档不能判定为可用成果。

## 四、验收标准

- [ ] 拓扑、IP表、inventory、配置和数据库备份完整
- [ ] OVA或标准模板机能够导入启动
- [ ] SHA256校验通过
- [ ] README能指导另一组完成恢复
- [ ] 不包含私钥、真实密码和敏感Token
- [ ] 恢复后网络、SSH和核心服务验证通过

## 五、常见问题

**Q：有VMware快照为什么还要导出OVA？**  
A：快照依赖原虚拟磁盘链，适合短期回退；OVA更适合跨目录、跨机器交付。配置仓库和数据库备份则解决可读、可审计和数据恢复问题。

**Q：三台OVA太大怎么办？**  
A：导出一台干净模板机，另外保存三种角色的配置、IP表和自动化清单，并验证能从模板重新构建三机。

**Q：能否把SSH私钥一起打包方便下学期使用？**  
A：不建议。归档公钥和账号说明，私钥由使用者安全保存或下学期重新生成。

## 六、提交成果

- 小组归档目录或压缩包
- SHA256SUMS.txt
- 恢复演练记录
- 5分钟环境交接演示
