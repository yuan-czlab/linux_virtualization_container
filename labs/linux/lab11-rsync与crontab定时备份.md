# 实验11：rsync数据同步与crontab定时备份

> 所属模块：模块二 网络、远程管理与基础防护  
> 建议学时：2学时  
> 实验方式：个人  
> 对应教材：《模块二 网络、远程管理与基础防护》第20章  
> 知识前置：教材第20章的同步、定时任务、日志和恢复概念\
> 状态依赖：`rocky-server`和`~/m1-project`；源文件、脚本和备份目录由本实验创建，不依赖实验10的SSH密钥\
> 建议起点：`Linux-L1`或当前连续实验环境\
> 项目成果：网站增量备份脚本、定时任务、运行日志和一次恢复验证

## 一、项目情境

项目网站和配置每天都在变化。你需要使用rsync建立增量备份，通过cron自动执行并保存日志，然后模拟文件误删，从备份恢复并验证内容。仅看到备份目录存在不算完成。

## 二、实验目标

### 1. 知识目标

1. 说明rsync源目录末尾斜杠的语义。
2. 说明首次同步、增量同步、镜像删除和`--dry-run`。
3. 说明cron时间字段、非交互环境和日志重定向。

### 2. 能力目标

1. 使用rsync完成首次和增量同步。
2. 编写具有日志和退出码的备份脚本。
3. 配置并验证用户crontab。
4. 从备份恢复误删文件并比较内容。

### 3. 素质目标

1. 使用`--delete`前必须先执行`--dry-run`。
2. 备份任务必须有日志，备份必须做恢复验证。
3. 脚本使用绝对路径，避免依赖交互式Shell环境。

## 三、知识准备

```text
rsync比较源和目标
→ 只传输新增或变化内容
→ cron按时间启动脚本
→ 脚本记录开始、结束和退出码
→ 运维人员定期执行恢复演练
```

源目录末尾斜杠：

```text
rsync source/ backup/   同步source里面的内容
rsync source  backup/   在backup中形成source目录
```

cron五个时间字段依次为分钟、小时、日、月、星期。

实验开始前打开[rsync增量同步、cron与恢复闭环动画](../../animations/08-rsync-cron-backup-restore/index.html)。完成“路径语义”和“增量与删除”后再执行任务二；完成“定时执行”和“恢复验证”后再编写脚本与crontab。每一步先预测目录树、变化清单或证据结果，再使用本实验创建的文件验证。

## 四、实验环境

- Rocky Linux 9，rocky-server登录。
- 需要`rsync`和`cronie`。
- 源目录：`~/m1-project/web`。
- 备份目录：`~/backup-lab/web-current`。

## 五、项目任务

1. 检查工具和crond服务。
2. 完成首次同步并比较源和目标。
3. 修改源数据后完成增量同步。
4. 编写可记录退出码的备份脚本。
5. 配置每分钟测试任务并验证日志。
6. 模拟误删并完成恢复。

## 六、实验步骤

### 任务一：准备环境

```bash
command -v rsync || sudo dnf install -y rsync
rpm -q cronie || sudo dnf install -y cronie
sudo systemctl enable --now crond
systemctl is-active crond
mkdir -p ~/backup-lab/web-current ~/backup-lab/logs ~/backup-lab/restore-test
```

创建测试数据：

```bash
mkdir -p ~/m1-project/web/assets
printf '<h1>Version 1</h1>\n' > ~/m1-project/web/index.html
printf 'body { color: #333; }\n' > ~/m1-project/web/assets/site.css
```

> **验收点**：rsync可用，crond为active，源目录包含两个文件。

### 任务二：首次和增量同步

#### 步骤1：首次同步

```bash
rsync -av ~/m1-project/web/ ~/backup-lab/web-current/
find ~/backup-lab/web-current -type f -printf '%P %s bytes\n' | sort
diff -qr ~/m1-project/web ~/backup-lab/web-current
echo $?
```

`diff -qr`没有输出且退出码为0，说明当前内容一致。

#### 步骤2：增量变化

```bash
printf '<p>backup lab</p>\n' >> ~/m1-project/web/index.html
printf 'console.log("v2");\n' > ~/m1-project/web/assets/app.js
rsync -av --itemize-changes ~/m1-project/web/ ~/backup-lab/web-current/
diff -qr ~/m1-project/web ~/backup-lab/web-current
```

观察rsync只报告新增或变化对象。

> **验收点**：增量同步后源和备份再次一致。

#### 步骤3：认识安全删除预览

在备份中创建一个多余文件：

```bash
printf 'old data\n' > ~/backup-lab/web-current/obsolete.txt
rsync -av --delete --dry-run ~/m1-project/web/ ~/backup-lab/web-current/
```

预览应显示将删除`obsolete.txt`。本实验不执行真实`--delete`，保留文件说明普通备份与严格镜像的差异。

### 任务三：编写备份脚本

```bash
mkdir -p ~/m1-project/scripts
cat > ~/m1-project/scripts/backup-web.sh <<'SCRIPT'
#!/bin/bash
set -u

SOURCE=/home/rocky-server/m1-project/web/
TARGET=/home/rocky-server/backup-lab/web-current/
LOG=/home/rocky-server/backup-lab/logs/backup-web.log

printf 'START time=%s source=%s target=%s\n' "$(date '+%F %T')" "$SOURCE" "$TARGET" >> "$LOG"
/usr/bin/rsync -a --itemize-changes "$SOURCE" "$TARGET" >> "$LOG" 2>&1
rc=$?
printf 'END time=%s exit_code=%s\n' "$(date '+%F %T')" "$rc" >> "$LOG"
exit "$rc"
SCRIPT

chmod 750 ~/m1-project/scripts/backup-web.sh
bash -n ~/m1-project/scripts/backup-web.sh
~/m1-project/scripts/backup-web.sh
echo $?
tail -n 20 ~/backup-lab/logs/backup-web.log
```

如果rocky-server家目录不同，应修改三个绝对路径。cron环境中的PATH和工作目录可能不同，因此脚本不使用`~`和相对命令路径。

> **验收点**：脚本语法正确，日志包含START、END和`exit_code=0`。

### 任务四：配置定时任务

先保存现有任务：

```bash
crontab -l > ~/backup-lab/crontab.before 2>/dev/null || true
```

编辑：

```bash
crontab -e
```

加入每分钟测试任务：

```text
* * * * * /home/rocky-server/m1-project/scripts/backup-web.sh
```

等待一个执行周期后检查：

```bash
crontab -l
tail -n 30 ~/backup-lab/logs/backup-web.log
sudo journalctl -u crond --since '-5 min' --no-pager | tail -30
```

不要只观察文件时间；日志应出现新的START和END记录。

> **验收点**：至少存在一次由cron触发的成功记录。

### 任务五：恢复验证

先确认备份：

```bash
test -s ~/backup-lab/web-current/index.html
sha256sum ~/backup-lab/web-current/index.html
```

模拟误删源文件：

```bash
cp -p ~/m1-project/web/index.html ~/m1-project/evidence/index.before-delete
rm ~/m1-project/web/index.html
test ! -e ~/m1-project/web/index.html
```

从备份恢复到测试目录：

```bash
rm -rf ~/backup-lab/restore-test/web
mkdir -p ~/backup-lab/restore-test/web
rsync -av ~/backup-lab/web-current/ ~/backup-lab/restore-test/web/
cmp ~/m1-project/evidence/index.before-delete ~/backup-lab/restore-test/web/index.html
echo $?
```

验证通过后恢复生产实验目录：

```bash
cp -p ~/backup-lab/restore-test/web/index.html ~/m1-project/web/index.html
cmp ~/m1-project/evidence/index.before-delete ~/m1-project/web/index.html
```

> **验收点**：先在测试目录恢复，再恢复源目录，关键文件内容一致。

### 任务六：恢复合理的cron频率

每分钟任务只用于课堂测试。验证后执行：

```bash
crontab -e
```

删除每分钟测试行，或按教师要求改为每日任务，例如：

```text
30 18 * * * /home/rocky-server/m1-project/scripts/backup-web.sh
```

再次执行`crontab -l`确认。

## 七、独立实践

1. 为`~/m1-project/config`编写第二个备份任务。
2. 备份目标不能与web备份混用。
3. 记录运行日志和退出码。
4. 修改一个配置文件后证明只同步了变化内容。
5. 恢复到新目录并使用`diff -qr`验证。

## 八、验收标准

- [ ] 能解释源目录末尾斜杠。
- [ ] 首次和增量同步均已完成。
- [ ] 使用`--delete`前执行了`--dry-run`，没有误删数据。
- [ ] 备份脚本使用绝对路径并返回rsync退出码。
- [ ] crond运行，日志证明cron至少成功触发一次。
- [ ] 每分钟测试任务已经删除或改为合理频率。
- [ ] 已完成误删、测试恢复、内容比较和正式恢复。
- [ ] 独立实践完整。

## 九、成果提交

1. `backup-web.sh`。
2. crontab最终内容。
3. `backup-web.log`。
4. 首次和增量同步结果。
5. `--delete --dry-run`预览。
6. 误删和恢复验证记录。
7. 独立实践脚本和结果。

## 十、常见问题

### Q1：cron中执行失败，手工执行成功

检查绝对路径、脚本权限、环境变量和日志重定向。cron不一定加载交互式Shell配置。

### Q2：备份目录中多了一层web

检查源目录末尾斜杠。`web/`表示同步目录内容，`web`表示同步目录本身。

### Q3：日志存在但没有END

脚本可能在rsync前后异常退出。手工运行并查看退出码，再检查目录权限和磁盘空间。

### Q4：为什么不直接从备份覆盖源目录

先恢复到测试目录可以确认备份结构和内容，降低把错误备份覆盖现有数据的风险。

## 十一、课后思考与拓展

1. 同步镜像和历史版本备份有什么区别？
2. 如果源文件损坏后cron立即同步，备份会发生什么？
3. 为什么备份策略还需要保留多个时间点和异地副本？

## 十二、环境保留

保留备份脚本、日志、web备份和最终cron任务，供实验20综合项目使用。清理恢复测试目录前先检查：

```bash
find ~/backup-lab/restore-test -maxdepth 3 -print
rm -rf ~/backup-lab/restore-test/web
```

