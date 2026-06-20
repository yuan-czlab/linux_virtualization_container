# Lab20：SSH 配置进阶与文件传输

> 课时：2 | 类型：个人 | 前置：Lab19

## 一、实验步骤

### 步骤1：~/.ssh/config 多服务器管理

```bash
cat > ~/.ssh/config << 'EOF'
Host myserver
    HostName localhost
    User student
    Port 22
    IdentityFile ~/.ssh/id_ed25519

Host myserver-root
    HostName localhost
    User root
    Port 22

Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF
chmod 600 ~/.ssh/config

ssh myserver "hostname"            # 用别名连接
ssh myserver-root "whoami"         # root 登录
```

### 步骤2：SSH 远程执行命令

```bash
ssh myserver "df -h /"                     # 远程执行单条命令
ssh myserver "uptime && free -h"           # 多条命令
ssh -t myserver "sudo systemctl status sshd"  # -t 分配终端
echo 'echo $(hostname): $(date)' | ssh myserver bash -s  # 本地脚本远程执行
```

### 步骤3：scp 文件传输

```bash
echo "local file" > /tmp/local.txt
scp /tmp/local.txt myserver:/tmp/         # 本地→远程
scp myserver:/etc/hostname /tmp/remote-hostname.txt  # 远程→本地
scp -r /tmp/testdir/ myserver:/tmp/       # 传目录
```

### 步骤4：rsync 增量同步

```bash
sudo dnf install -y rsync

mkdir /tmp/sync-source && echo "hello" > /tmp/sync-source/test.txt
rsync -avzP /tmp/sync-source/ myserver:/tmp/sync-dest/
# -a 归档模式 -v 详细 -z 压缩 -P 进度+续传

# 增量同步：只传变化的文件
echo "world" > /tmp/sync-source/test.txt
rsync -avzP /tmp/sync-source/ myserver:/tmp/sync-dest/  # 只传变化的部分
```

### 步骤5：tmux 防断线

```bash
sudo dnf install -y tmux
tmux new -s work                    # 创建会话
# 在 tmux 里执行：sleep 120
# Ctrl+b → d（分离）
tmux ls                             # 查看会话
tmux attach -t work                 # 重新连接→任务还在跑
```

---

## 五、练习题

### 练习1：scp vs rsync（15分）

| 对比 | scp | rsync |
|------|-----|-------|
| 增量同步 | | |
| 断点续传 | | |
| 压缩传输 | | |
| 是否需要服务端安装 | | |
| 最适合场景 | | |

### 练习2：批量远程操作（25分）

用 `ssh myserver "命令"` 方式，完成：
1. 查看三台服务器（用 localhost 模拟）的磁盘使用情况
2. 在三台服务器上同时创建同一个文件
3. 写一个脚本 `remote-check.sh`，接受主机名列表，批量执行巡检

### 练习3：tmux 使用场景（20分）

1. 创建 tmux 会话，分两个 pane（Ctrl+b %）
2. 左 pane 监控日志：`sudo journalctl -f`
3. 右 pane 模拟操作：重启 nginx，看日志变化

### 练习4：rsync 备份方案（25分）

写一个备份脚本，用 rsync 将 `/var/log/` 增量同步到 `/backup/logs/`，要求：
1. 排除 `*.gz` 压缩文件
2. 保留文件权限和时间戳
3. 显示进度
4. 删除目标端多余的文件（镜像同步）

### 练习5：~/.ssh/config 安全配置（15分）

在 config 的 `Host *` 段添加：
1. 连接保活（防断线）
2. 禁止 X11 转发
3. 禁止 agent 转发
4. 解释每一条的作用

---

## 六、验收标准
- [ ] 能用 ~/.ssh/config 配置 Host 别名
- [ ] 能用 ssh 远程执行命令
- [ ] 能用 scp 和 rsync 传输文件
- [ ] 能使用 tmux 防止断线
- [ ] 练习 1-5 全部完成

## 七、常见问题

**Q: ~/.ssh/config 的 Host 可以模糊匹配吗？**
A: 可以。`Host dev-*` 匹配所有 dev- 开头的；`Host *` 匹配所有。常用套路：前面写特定配置，最后 `Host *` 写全局默认值。

**Q: scp 和 rsync 谁更快？**
A: 第一次传输差不多。增量更新时 rsync 快得多（只传差异部分）。但 rsync 需要两端都安装，scp 只要有 SSH 就能用。

**Q: rsync 的 --delete 很危险？**
A: 是的，会把目标多出来的文件删掉。建议先用 `--dry-run` 干跑看效果，确认再执行。生产环境备份时一般不用 --delete。

**Q: tmux 断开后任务还在运行吗？**
A: 在。tmux 的 session 在服务器上独立于 SSH 连接。SSH 断了、终端关了、电脑休眠了，tmux 里的任务都还在运行。

## 八、课后思考

1. 如果有 50 台服务器需要同时执行同一条命令（如更新配置），你有哪些方案？比较 ssh 循环、Ansible、SaltStack 的优缺点。

2. rsync 的增量同步原理是什么？它是怎么判断"文件有变化"的？（提示：时间戳、文件大小、checksum）
