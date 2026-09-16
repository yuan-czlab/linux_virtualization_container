# 实验11：rsync数据同步与crontab定时备份

> 所属模块：模块二 网络远程管理与基础防护
> 建议学时：2学时
> 实验方式：个人，远程拓展可由小组互查
> 对应教材：2.8 rsync增量备份与定时任务
> 知识前置：文件目录管理、vim、权限、systemd和2.8教材
> 状态依赖：`rocky-server`和`~/m1-project`可用；核心任务不依赖实验10密钥
> 建议起点：`Linux-L1`或当前连续实验环境
> 项目成果：网站备份、备份脚本、cron日志、隔离恢复和误删恢复证据

## 一、项目情境

网站文件每天都会变化。管理员需要建立一套能够重复执行的增量备份任务，并证明文件误删后可以恢复。

本实验不是“把文件复制一次”，而是完成：

```text
首次同步
→ 增量变化
→ 删除预览
→ 手工验证脚本
→ cron自动执行
→ 日志证明
→ 隔离恢复
→ 业务目录复原
```

## 二、实验规则

1. rsync源目录是否带末尾斜杠必须明确。
2. 使用`--delete`前必须先使用`--dry-run`。
3. 没有手工运行成功的命令不能放入cron。
4. cron脚本使用绝对路径并写入日志。
5. 恢复时先写入隔离目录，不直接覆盖源目录。
6. 每分钟任务只用于课堂验证，验收前必须改为合理频率。

## 三、任务一：准备工具和源数据

### 3.1 确认身份

```bash
whoami
```

```bash
hostnamectl --static
```

预期当前用户和主机名均为`rocky-server`。

### 3.2 安装rsync

```bash
command -v rsync
```

没有输出时安装：

```bash
sudo dnf install -y rsync
```

### 3.3 安装并启动crond

```bash
rpm -q cronie
```

未安装时执行：

```bash
sudo dnf install -y cronie
```

启动：

```bash
sudo systemctl enable --now crond
```

检查：

```bash
systemctl is-active crond
```

### 3.4 创建源目录

```bash
mkdir -p ~/m1-project/web/assets
```

创建首页：

```bash
vim ~/m1-project/web/index.html
```

写入：

```html
<h1>Backup Lab Version 1</h1>
```

创建样式文件：

```bash
vim ~/m1-project/web/assets/site.css
```

写入：

```css
body { color: #333; }
```

检查源数据：

```bash
find ~/m1-project/web -maxdepth 2 -type f -printf '%P\n'
```

预期至少包含`index.html`和`assets/site.css`。

## 四、任务二：首次同步与增量同步

### 4.1 创建备份目录

```bash
mkdir -p ~/backup-lab/web-current
```

### 4.2 预览首次同步

```bash
rsync -aivn ~/m1-project/web/ ~/backup-lab/web-current/
```

检查源路径末尾的`/`，确认目标将直接包含网站内容。

### 4.3 执行首次同步

```bash
rsync -aiv ~/m1-project/web/ ~/backup-lab/web-current/
```

比较：

```bash
diff -qr ~/m1-project/web ~/backup-lab/web-current
```

没有输出表示当前内容一致。

### 4.4 制造正常业务变化

用vim修改首页，把Version 1改成Version 2：

```bash
vim ~/m1-project/web/index.html
```

创建脚本文件：

```bash
vim ~/m1-project/web/assets/app.js
```

写入：

```javascript
console.log("backup lab v2");
```

### 4.5 预览增量

```bash
rsync -aivn ~/m1-project/web/ ~/backup-lab/web-current/
```

预期只出现修改的`index.html`和新增的`assets/app.js`。

### 4.6 执行增量同步

```bash
rsync -aiv ~/m1-project/web/ ~/backup-lab/web-current/
```

再次比较：

```bash
diff -qr ~/m1-project/web ~/backup-lab/web-current
```

## 五、任务三：安全观察--delete

在目标目录创建源端不存在的文件：

```bash
touch ~/backup-lab/web-current/obsolete.txt
```

预览删除：

```bash
rsync -aivn --delete ~/m1-project/web/ ~/backup-lab/web-current/
```

输出应指出`obsolete.txt`将被删除。

确认预览没有真正删除：

```bash
ls -l ~/backup-lab/web-current/obsolete.txt
```

本实验不执行真实`--delete`。删除该测试文件：

```bash
rm ~/backup-lab/web-current/obsolete.txt
```

## 六、任务四：编写可定时执行的备份脚本

### 6.1 创建脚本目录

```bash
mkdir -p ~/m1-project/scripts
```

### 6.2 使用vim编写

```bash
vim ~/m1-project/scripts/backup-web.sh
```

逐行输入：

```text
#!/bin/bash
SOURCE=/home/rocky-server/m1-project/web/
TARGET=/home/rocky-server/backup-lab/web-current/
LOG=/home/rocky-server/backup-lab/logs/backup-web.log
mkdir -p "$TARGET" "$(dirname "$LOG")"
printf 'START %s\n' "$(date -Iseconds)" >> "$LOG"
/usr/bin/rsync -a --itemize-changes "$SOURCE" "$TARGET" >> "$LOG" 2>&1
rc=$?
printf 'END %s code=%s\n' "$(date -Iseconds)" "$rc" >> "$LOG"
exit "$rc"
```

本实验固定账号是`rocky-server`，因此脚本使用`/home/rocky-server`。如果身份检查不符合，不得照抄路径。

### 6.3 设置权限

```bash
chmod 750 ~/m1-project/scripts/backup-web.sh
```

### 6.4 检查语法

```bash
bash -n ~/m1-project/scripts/backup-web.sh
```

没有输出通常表示语法通过。

### 6.5 手工执行

```bash
~/m1-project/scripts/backup-web.sh
```

紧接着查看退出状态：

```bash
echo $?
```

预期为0。

### 6.6 检查日志

```bash
tail -n 20 ~/backup-lab/logs/backup-web.log
```

日志应同时包含`START`和`END ... code=0`。

## 七、任务五：配置并验证cron

### 7.1 保存当前任务

```bash
crontab -l
```

如果已有任务，先把内容保存到实验记录，不要覆盖或删除不认识的任务。

### 7.2 添加每分钟测试任务

```bash
crontab -e
```

加入：

```cron
* * * * * /usr/bin/flock -n /tmp/backup-web.lock /home/rocky-server/m1-project/scripts/backup-web.sh
```

保存后确认：

```bash
crontab -l
```

### 7.3 等待并检查

等待跨过下一个整分钟，再查看日志：

```bash
tail -n 20 ~/backup-lab/logs/backup-web.log
```

至少应出现一组新的`START`和`END ... code=0`。

查看服务日志：

```bash
sudo journalctl -u crond --since '5 minutes ago' --no-pager
```

## 八、任务六：模拟误删并隔离恢复

### 8.1 确保最新内容已备份

手工再执行一次：

```bash
~/m1-project/scripts/backup-web.sh
```

比较：

```bash
diff -qr ~/m1-project/web ~/backup-lab/web-current
```

### 8.2 保存误删前证据

```bash
mkdir -p ~/m1-project/evidence
```

```bash
cp -p ~/m1-project/web/index.html ~/m1-project/evidence/index.before-delete
```

计算哈希：

```bash
sha256sum ~/m1-project/evidence/index.before-delete
```

### 8.3 模拟误删

```bash
rm ~/m1-project/web/index.html
```

确认：

```bash
ls -l ~/m1-project/web/index.html
```

提示文件不存在是预期故障现象。

### 8.4 恢复到隔离目录

```bash
mkdir -p ~/backup-lab/restore-test/web
```

```bash
rsync -av ~/backup-lab/web-current/ ~/backup-lab/restore-test/web/
```

检查恢复文件：

```bash
ls -l ~/backup-lab/restore-test/web/index.html
```

与误删前证据比较：

```bash
cmp ~/m1-project/evidence/index.before-delete ~/backup-lab/restore-test/web/index.html
```

`cmp`没有输出且退出状态为0，才能继续。

### 8.5 恢复业务文件

```bash
cp -p ~/backup-lab/restore-test/web/index.html ~/m1-project/web/index.html
```

再次比较：

```bash
cmp ~/m1-project/evidence/index.before-delete ~/m1-project/web/index.html
```

## 九、任务七：恢复合理的cron频率

再次编辑：

```bash
crontab -e
```

把每分钟任务改为每天18:30：

```cron
30 18 * * * /usr/bin/flock -n /tmp/backup-web.lock /home/rocky-server/m1-project/scripts/backup-web.sh
```

确认最终结果：

```bash
crontab -l
```

验收时不得保留`* * * * *`测试频率。

## 十、拓展任务：通过SSH远程备份

本任务需要实验10的SSH密钥，只作为完成核心实验后的拓展。

在`ubuntu-client`安装rsync：

```bash
sudo apt install -y rsync
```

确认SSH配置：

```bash
ssh -G rocky-server | grep -E '^(hostname|user|identityfile) '
```

创建本地备份目录：

```bash
mkdir -p ~/course-backup/rocky-server-web
```

先预览：

```bash
rsync -aivn rocky-server:~/m1-project/web/ ~/course-backup/rocky-server-web/
```

确认方向后同步：

```bash
rsync -aiv rocky-server:~/m1-project/web/ ~/course-backup/rocky-server-web/
```

远程自动备份还要处理私钥口令、主机指纹和非交互认证，本实验不把它直接加入cron。

## 十一、验收标准

- [ ] rsync和crond可用。
- [ ] 能解释源目录末尾斜杠的含义。
- [ ] 首次同步和增量同步均通过`diff`检查。
- [ ] `--delete --dry-run`只进行了预览。
- [ ] 备份脚本使用绝对路径、日志和rsync退出状态。
- [ ] 手工运行脚本成功后才配置cron。
- [ ] 日志证明cron至少触发一次且退出状态为0。
- [ ] 误删文件先恢复到隔离目录并通过`cmp`验证。
- [ ] 业务文件已经恢复。
- [ ] 每分钟测试任务已经改为合理频率。

## 十二、成果提交

1. 首次同步和增量同步输出。
2. `--delete --dry-run`结果。
3. `backup-web.sh`及逐行说明。
4. cron触发日志。
5. 误删前哈希、隔离恢复`cmp`结果和业务恢复结果。
6. 最终`crontab -l`。

## 十三、常见问题

### 13.1 目标多了一层web目录

检查源路径是否写成`~/m1-project/web`而不是`~/m1-project/web/`。

### 13.2 手工成功但cron失败

检查绝对路径、脚本权限和日志：

```bash
ls -l ~/m1-project/scripts/backup-web.sh
```

```bash
tail -n 50 ~/backup-lab/logs/backup-web.log
```

### 13.3 日志只有START没有END

检查脚本是否完整保存，再手工执行并查看退出状态。

### 13.4 flock找不到

Rocky中的`flock`通常由`util-linux`提供：

```bash
command -v flock
```

### 13.5 恢复文件仍然错误

停止覆盖业务目录，检查备份时间、备份文件内容和误删前哈希。备份存在不等于备份正确。

## 十四、环境保留

保留：

- `~/m1-project/web`
- `~/backup-lab/web-current`
- `~/m1-project/scripts/backup-web.sh`
- `~/backup-lab/logs/backup-web.log`
- 最终每天18:30的cron任务

这些成果将在模块三服务部署和实验20综合项目中复用。隔离恢复目录在验收后可以删除，但不得删除当前备份。
