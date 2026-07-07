# Lab21：文件传输实战练习

> 课时：2 | 类型：个人 | 前置：Lab19（需要免密登录）

## 场景一：部署静态网站到远程服务器（40分）

**背景**：开发给了你一个网站目录，需要传输到远程服务器并部署。

**你的任务**：

### 1. 准备本地网站文件
```bash
mkdir -p /tmp/lab21-website/{css,js,images}
cat > /tmp/lab21-website/index.html << 'HTML'
<!DOCTYPE html><html lang="zh"><head><meta charset="UTF-8">
<title>部署测试</title></head>
<body><h1>文件传输实战</h1><p>部署时间：<script>document.write(new Date())</script></p></body></html>
HTML
echo "body { font-family: sans-serif; }" > /tmp/lab21-website/css/style.css
dd if=/dev/zero of=/tmp/lab21-website/images/banner.png bs=1K count=50 2>/dev/null
```

### 2. 用 scp 上传
- 将整个网站目录上传到远程 `/tmp/deployed-site/`
- 验证远程文件完整性（`ls -lR /tmp/deployed-site/`）

### 3. 用 rsync 增量同步
- 修改本地 `index.html`（改一句话）
- 修改 `css/style.css`
- 用 `rsync -avzP` 增量同步到远程，观察只传输了变化的文件
- 对比 `rsync` 和 `scp` 在增量更新时的行为差异

### 4. 远程排除文件
- 在本地创建一个 `node_modules/` 目录（随便放几个文件）
- 用 rsync 的 `--exclude='node_modules'` 排除它
- 验证远程没有 `node_modules` 目录

---

## 场景二：数据库备份传输（30分）

**背景**：需要把数据库备份文件从服务器下载到本地，然后上传到备份服务器。

**你的任务**：

1. 在 remote（localhost）创建模拟备份文件：
```bash
dd if=/dev/zero of=/tmp/mock-backup-$(date +%Y%m%d).tar.gz bs=1M count=30 2>/dev/null
```

2. 用 scp 从远程下载备份到本地 `/tmp/backups/`

3. "上传到备份服务器"（模拟，上传到 /tmp/backup-archive/）

4. **挑战**：如果备份文件 2GB，传输过程中网络断了一次，scp 重传需要重新传 2GB。用什么工具可以续传？（提示：rsync -P）

---

## 场景三：tmux 防止传输中断（30分）

**背景**：传输大文件时如果 SSH 断开，传输就失败了。

**你的任务**：

1. 安装 tmux：`sudo dnf install -y tmux`
2. 创建一个 tmux 会话：`tmux new -s transfer`
3. 在 tmux 中启动一个长时间任务（模拟大文件传输）：
   ```bash
   for i in $(seq 1 60); do echo "传输进度: $i/60"; sleep 1; done
   ```
4. 按 `Ctrl+b d` 分离会话（模拟 SSH 断开）
5. 退出终端，重新打开，用 `tmux attach -t transfer` 恢复
6. 观察到任务还在继续执行
7. 任务完成，退出 tmux

**回答问题**：
- tmux 的 session/window/pane 分别是什么概念？
- `Ctrl+b d` 和直接关闭终端窗口有什么区别？
- 除了文件传输，tmux 在运维中还有哪些用途？

---

## 场景四：rsync + crontab 自动增量备份

**背景**：网站目录每天需要备份到远程服务器，任务必须自动执行并保留日志。

### 1. 编写备份脚本

```bash
mkdir -p ~/bin ~/logs
cat > ~/bin/backup-website.sh <<'SCRIPT'
#!/bin/bash
set -u

SOURCE=/tmp/lab21-website/
TARGET=student@localhost:/tmp/backup-archive/website/
LOG=$HOME/logs/backup-website.log

echo "[$(date '+%F %T')] backup start" >> "$LOG"
if rsync -az --delete-delay "$SOURCE" "$TARGET" >> "$LOG" 2>&1; then
  echo "[$(date '+%F %T')] backup success" >> "$LOG"
  exit 0
else
  code=$?
  echo "[$(date '+%F %T')] backup failed: $code" >> "$LOG"
  exit "$code"
fi
SCRIPT
chmod +x ~/bin/backup-website.sh
~/bin/backup-website.sh
echo "exit_code=$?"
tail -n 10 ~/logs/backup-website.log
```

### 2. 先做dry-run再加入定时任务

```bash
rsync -azn --delete-delay /tmp/lab21-website/ student@localhost:/tmp/backup-archive/website/

(crontab -l 2>/dev/null; echo "*/10 * * * * $HOME/bin/backup-website.sh") | crontab -
crontab -l
```

### 3. 验证增量与恢复

1. 修改一个文件并新增一个文件，再手动执行脚本。
2. 检查日志，确认只同步变化内容。
3. 将远程备份恢复到`/tmp/restore-test/`。
4. 使用`diff -qr`验证恢复目录与源目录一致。

```bash
mkdir -p /tmp/restore-test
rsync -az student@localhost:/tmp/backup-archive/website/ /tmp/restore-test/
diff -qr /tmp/lab21-website/ /tmp/restore-test/
```

> **验收点**：定时任务存在、脚本有明确退出码、日志可追踪、恢复结果一致。

---

## 验收标准
- [ ] 场景一：scp 和 rsync 都能完成文件传输
- [ ] 场景一：能解释 rsync 比 scp 在增量同步时的优势
- [ ] 场景二：scp 下载+上传完成
- [ ] 场景二：知道 rsync -P 支持断点续传
- [ ] 场景三：会使用 tmux new/attach/detach
- [ ] 场景四：能用rsync+crontab完成自动备份并写日志
- [ ] 场景四：完成一次恢复并用diff验证一致性

## 清理
```bash
crontab -l 2>/dev/null | grep -v 'backup-website.sh' | crontab -
rm -rf /tmp/lab21-website /tmp/backups /tmp/backup-archive /tmp/deployed-site /tmp/restore-test /tmp/mock-backup-*.tar.gz
rm -f ~/bin/backup-website.sh ~/logs/backup-website.log
```
