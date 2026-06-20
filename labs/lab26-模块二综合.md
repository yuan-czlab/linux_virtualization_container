# Lab26：模块二综合练习

> 课时：2 | 类型：个人 | 前置：Lab25

## 综合任务：部署一台可对外服务的 Web 服务器

从一台"裸" Rocky Linux 开始，完成以下所有任务。

---

## 任务清单

### 1. 网络配置
- [ ] 确保静态 IP 配置正确
- [ ] 网关和 DNS 配置正确
- [ ] `ping 223.5.5.5` 通
- [ ] `ping www.baidu.com` 通

### 2. SSH 远程管理
- [ ] sshd 运行
- [ ] 配置密钥免密登录
- [ ] ~/.ssh/config 中配置别名 `myserver`
- [ ] `ssh myserver` 能免密登录

### 3. 防火墙配置（最小开放原则）
- [ ] 只开放 22(SSH)、80(HTTP)、443(HTTPS)
- [ ] 所有规则为永久规则
- [ ] `firewall-cmd --list-all` 确认

### 4. Web 服务
- [ ] 安装 Nginx
- [ ] 修改默认页面显示 "Server: 主机名 - 当前时间"
- [ ] Nginx 开机自启
- [ ] curl http://localhost 返回自定义页面

### 5. SELinux 确保 Enforcing
- [ ] `getenforce` 输出 Enforcing
- [ ] Web 目录上下文正确
- [ ] 没有 SELinux 阻塞的 AVC 拒绝记录

### 6. 部署文档
创建 `/tmp/deploy-report.md`，包含：

```markdown
# 服务器部署报告

## 基本信息
- 主机名：xxx
- IP 地址：xxx
- 系统版本：xxx

## 网络配置
（ip a 和 ip route 的输出）

## 防火墙规则
（firewall-cmd --list-all 的输出）

## 运行服务
（systemctl list-units --type=service --state=running | grep -E "ssh|nginx"）

## 验证测试
- ping 外网：✓
- SSH 免密登录：✓
- curl http://localhost：✓
- SELinux Enforcing：✓
```

---

## 教师故障注入（2个）

完成上述任务后，教师注入 2 个故障（从 Lab25 的 5 个故障中选），学生排查并写出排障报告。

---

## 验收标准
- [ ] 6 项任务全部完成
- [ ] 部署报告内容完整
- [ ] 2 个注入故障在 5 分钟内定位并修复

---

**模块二完成。**

---

## 七、常见问题

**Q: 综合任务中卡在某个步骤怎么办？**
A: 回顾模块二的 10 步排障流程，逐层排查。不要一卡就从头重来，先定位问题在哪一层。

**Q: 部署文档需要写多详细？**
A: 标准：另一个运维拿着你的文档能独立复现整个部署。包含：每步命令、预期输出、配置内容、验证方法。

## 八、课后思考

1. 回顾模块二学到的所有技能，画出"一台新服务器从零到可对外服务"的完整流程图。

2. 如果你入职第一天，交接文档只有一句话"Nginx 在 80 端口"，你还需要知道什么信息才能管理好这台服务器？
