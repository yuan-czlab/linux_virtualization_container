# Lab12：systemd 服务管理练习

> 课时：2 | 类型：个人 | 前置：Lab11

## 一、你会学到什么
- 理解 systemd 的角色（PID=1，管一切）
- 能用 systemctl 管理服务（启停/状态/自启）
- 能用 journalctl 查看服务日志
- 能编写一个简单的 systemd Service 文件

## 二、实验步骤

### 步骤1：认识 systemd

```bash
ps -p 1 -o comm=                    # systemd 就是 PID=1
systemctl get-default               # 默认运行级别
# multi-user.target = 命令行多用户模式
```

### 步骤2：服务启停（以 sshd 为例）

```bash
systemctl status sshd               # 查看状态
# Active: active (running) → 正在运行
# Loaded: loaded (...; enabled) → 开机自启

systemctl is-active sshd
systemctl is-enabled sshd

sudo systemctl stop sshd             # 停止
systemctl is-active sshd            # inactive

sudo systemctl start sshd            # 启动
systemctl is-active sshd            # active

sudo systemctl restart sshd          # 重启（stop+start）
sudo systemctl reload sshd           # 重载配置（不中断服务，推荐）
```

### 步骤3：开机自启管理

```bash
# 以 nginx 为例
sudo dnf install -y nginx

systemctl is-enabled nginx          # disabled（刚装完默认不自启）
sudo systemctl enable nginx         # 设置开机自启
systemctl is-enabled nginx          # enabled

# enable 的本质：在 target 目录下创建符号链接
ls -l /etc/systemd/system/multi-user.target.wants/ | grep nginx

sudo systemctl disable nginx
sudo systemctl mask nginx           # 彻底禁用（连手动启动都不行）
sudo systemctl unmask nginx
```

### 步骤4：查看服务列表

```bash
systemctl list-units --type=service --state=running    # 正在运行的
systemctl list-units --type=service --state=failed     # 启动失败的
systemctl list-unit-files --type=service --state=enabled # 开机自启的
```

### 步骤5：journalctl 查日志

```bash
journalctl -u sshd                  # sshd 所有日志
journalctl -u sshd -n 20            # 最后 20 行
journalctl -u sshd -f               # 实时跟踪
journalctl -u sshd --since "1 hour ago"
journalctl -u sshd -p err           # 只看 error 及以上
journalctl -b                       # 本次启动以来的日志
journalctl --disk-usage             # 日志占用空间
```

### 步骤6：编写 systemd Service

```bash
# 创建服务脚本
sudo mkdir -p /opt/hello-svc
sudo tee /opt/hello-svc/hello.sh << 'EOF'
#!/bin/bash
while true; do
  echo "[$(date)] Hello from systemd service"
  sleep 60
done
EOF
sudo chmod +x /opt/hello-svc/hello.sh

# 创建 Service 文件
sudo tee /etc/systemd/system/hello.service << 'EOF'
[Unit]
Description=Hello Service
After=network.target

[Service]
Type=simple
ExecStart=/opt/hello-svc/hello.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start hello
systemctl status hello              # active (running)
journalctl -u hello -n 5            # 看到输出日志
```

> **验收点**：hello.service 启动成功，journalctl 能看到定时输出。

---

## 五、练习题

### 练习1：服务状态判断（15分）

观察以下 `systemctl status` 输出，判断服务当前状态和开机自启状态：

| 输出 | active/inactive? | enabled/disabled? |
|------|-----------------|-------------------|
| `Active: active (running) ... Loaded: loaded (...; enabled)` | | |
| `Active: inactive (dead) ... Loaded: loaded (...; disabled)` | | |
| `Active: active (running) ... Loaded: loaded (...; disabled)` | | |
| `Active: failed ... Loaded: loaded (...; enabled)` | | |

### 练习2：排查服务故障（25分）

以下服务启动失败，写出排查步骤：

```bash
# 模拟故障服务
sudo tee /etc/systemd/system/bad-service.service << 'EOF'
[Unit]
Description=Bad Service
[Service]
Type=simple
ExecStart=/usr/bin/nonexistent-command
Restart=no
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl start bad-service
```

1. 用 `systemctl status` 看报错信息
2. 用 `journalctl -u bad-service` 看日志
3. 修复后验证

### 练习3：编写应用服务（30分）

将 Lab12 步骤6 的 hello.service 改为：
1. 以 `nobody` 用户运行（User=nobody）
2. 工作目录设为 `/opt/hello-svc`（WorkingDirectory）
3. 标准输出和标准错误都输出到 journald
4. 崩溃后 5 秒自动重启（Restart=on-failure, RestartSec=5）

### 练习4：crontab 定时任务（15分）

1. 用 `crontab -e` 添加一条定时任务：每天凌晨 2:00 执行 `systemctl restart hello`
2. 用 `crontab -l` 验证
3. crontab 格式每个字段的含义是什么？

### 练习5：systemd Timer（15分）

不用 crontab，用 systemd Timer 实现同样的定时重启（每 60 分钟重启一次 hello.service）。提示：需要创建 `.timer` 文件和对应的 `.service` 文件。

---

## 六、验收标准
- [ ] systemctl start/stop/status/enable/disable 熟练操作
- [ ] journalctl -u/-f/-n/-p 常用选项掌握
- [ ] 能编写 systemd Service 文件
- [ ] 练习 1-5 全部完成

## 七、清理
```bash
sudo systemctl disable --now hello 2>/dev/null
sudo systemctl disable --now bad-service 2>/dev/null
sudo rm /etc/systemd/system/hello.service /etc/systemd/system/bad-service.service
sudo rm -rf /opt/hello-svc
sudo systemctl daemon-reload
```
