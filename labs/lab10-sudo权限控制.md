# Lab10：sudo 权限控制练习

> 课时：2 | 类型：个人 | 前置：Lab09

## 一、你会学到什么
- 能解释 sudo 和 su 的区别
- 能用 visudo 安全编辑 sudoers 配置
- 能为特定用户配置细粒度 sudo 权限
- 能查看 sudo 操作日志

## 二、实验步骤

### 步骤1：认识 sudo 和 wheel 组

```bash
# student 为什么能用 sudo？
groups student
# student : student wheel ← 关键：属于 wheel 组

grep wheel /etc/sudoers
# %wheel  ALL=(ALL)       ALL
# 意思是：wheel 组成员可以从任何主机、以任何用户身份、执行任何命令

# su vs sudo
# su = 切换用户（需要目标用户的密码）
# sudo = 以 root 身份执行一条命令（需要自己密码）
```

### 步骤2：visudo 安全编辑

```bash
# ⚠️ 永远不要直接用 vim 编辑 /etc/sudoers！
# 正确方式：
sudo visudo
# 或创建独立配置文件（更推荐）
sudo visudo -f /etc/sudoers.d/my-rules
```

> ⚠️ visudo 保存时会检查语法。如果报错，按 e 重新编辑，不要按 Q 强制保存！

### 步骤3：创建测试用户

```bash
sudo useradd -m ops-admin
sudo useradd -m ops-viewer
echo "ops-admin:admin123" | sudo chpasswd
echo "ops-viewer:view123" | sudo chpasswd
```

### 步骤4：配置细粒度 sudo 权限

给 `ops-admin` 配置 sudo（能管理服务、装软件，但不能改 sudoers）：

```bash
sudo visudo -f /etc/sudoers.d/ops-admin
```

添加：
```
# ops-admin：运维管理员
ops-admin ALL=(ALL) /usr/bin/systemctl
ops-admin ALL=(ALL) /usr/bin/dnf
ops-admin ALL=(ALL) /usr/bin/journalctl, /usr/bin/tail, /usr/bin/cat
```

给 `ops-viewer` 配置 sudo（只能查看，不能修改）：

```bash
sudo visudo -f /etc/sudoers.d/ops-viewer
sudo chmod 440 /etc/sudoers.d/ops-viewer
```

添加：
```
# ops-viewer：只读运维
ops-viewer ALL=(ALL) /usr/bin/systemctl status *
ops-viewer ALL=(ALL) /usr/bin/journalctl
ops-viewer ALL=(ALL) /usr/bin/tail, /usr/bin/cat, /usr/bin/less
ops-viewer ALL=(ALL) /usr/bin/top, /usr/bin/ps, /usr/bin/free, /usr/bin/df
```

### 步骤5：验证 sudo 权限

```bash
# ops-admin：允许的
su ops-admin -c "sudo systemctl status sshd"     # ✓
su ops-admin -c "sudo dnf check-update"           # ✓

# ops-admin：禁止的
su ops-admin -c "sudo visudo"                     # ✗ 不在允许列表
su ops-admin -c "sudo useradd test"               # ✗ 不允许

# ops-viewer：允许的
su ops-viewer -c "sudo systemctl status sshd"     # ✓
su ops-viewer -c "sudo df -h"                     # ✓

# ops-viewer：禁止的
su ops-viewer -c "sudo systemctl restart sshd"    # ✗ 只能 status
```

### 步骤6：查看 sudo 日志

```bash
sudo grep "sudo" /var/log/secure | tail -10
# 每条 sudo 操作都记录了：谁、什么时候、执行的什么命令
```

### 步骤7：NOPASSWD 配置（可选）

```bash
# 某些场景（自动化脚本、CI/CD）需要免密码 sudo
sudo visudo -f /etc/sudoers.d/nopasswd-demo
# 添加：ops-admin ALL=(ALL) NOPASSWD: /usr/bin/systemctl
```

---

## 五、练习题

### 练习1：sudo vs su（10分）

| 场景 | 用什么 | 原因 |
|------|--------|------|
| 临时重启 nginx | | |
| 需要连续执行多条 root 命令 | | |
| 自动化脚本中执行管理命令 | | |

### 练习2：visudo 语法错误恢复（15分）

1. visudo 保存时提示语法错误，按什么键？
2. 如果强制保存了错误的 sudoers 文件导致 sudo 不能用，怎么修复？

### 练习3：配置应用部署用户（25分）

创建用户 `deployer`，配置 sudo 权限：
- 能重启 nginx
- 能查看 nginx 日志
- 能用 git pull 更新代码
- 不能安装软件
- 不能修改 sudo 配置
- 不能创建/删除用户

写出 `/etc/sudoers.d/deployer` 的完整内容。

### 练习4：安全审计（25分）

假设你是安全审计员：
1. 写命令查看今天所有 sudo 操作记录
2. 找出被拒绝的 sudo 操作（`COMMAND=` 那一行没有后续成功记录）
3. 写命令查看 `/etc/sudoers.d/` 下所有文件的权限是否符合安全要求（应为 440）

### 练习5：sudo 配置排错（25分）

以下 sudoers 规则有什么问题？写出正确写法。

```
# 规则A：允许重启 nginx 和查看状态
ops-app ALL=(ALL) /usr/bin/systemctl start nginx, /usr/bin/systemctl status nginx

# 规则B（想禁止改 root 密码）
ops-lead ALL=(ALL) /usr/bin/passwd, !/usr/bin/passwd root

# 规则C（通配符）
ops-viewer ALL=(ALL) /usr/bin/systemctl *
```

---

## 六、验收标准
- [ ] 能解释 sudo（单条命令提权）和 su（切换用户）的区别
- [ ] 能为用户配置细粒度 sudo 权限
- [ ] 能在 /var/log/secure 中查看 sudo 操作记录
- [ ] 练习 1-5 全部完成

## 七、清理
```bash
sudo userdel -r ops-admin 2>/dev/null
sudo userdel -r ops-viewer 2>/dev/null
sudo userdel -r deployer 2>/dev/null
sudo rm -f /etc/sudoers.d/ops-admin /etc/sudoers.d/ops-viewer /etc/sudoers.d/deployer /etc/sudoers.d/nopasswd-demo
```
