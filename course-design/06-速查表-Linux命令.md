# Linux 命令速查卡

> 打印给学生 | 建议双面打印为一张A4纸

---

## 文件与目录

| 命令 | 说明 | 常用示例 |
|------|------|---------|
| `ls -la` | 列出所有文件（含隐藏） | `ls -lhS /var/log` |
| `cd` | 切换目录 | `cd ~` `cd -` `cd ..` |
| `pwd` | 当前目录 | |
| `mkdir -p` | 创建目录（含父目录） | `mkdir -p a/b/c` |
| `touch` | 创建空文件 | `touch file{1..10}.txt` |
| `cp -r` | 复制（递归） | `cp -a src/ dst/` |
| `mv` | 移动/重命名 | `mv old new` |
| `rm -rf` | 强制递归删除⚠️ | `rm -rf /tmp/test/` |
| `find` | 查找文件 | `find . -name "*.log" -mtime +7` |
| `ln -s` | 创建软链接 | `ln -s /opt/app /usr/bin/app` |
| `tar` | 压缩解压 | `tar -czf a.tar.gz dir/` `tar -xzf a.tar.gz` |

## 文件查看

| 命令 | 说明 | 常用示例 |
|------|------|---------|
| `cat` | 显示全部 | `cat file.txt` |
| `less` | 分页浏览 | `less /var/log/messages` |
| `head -n` | 看头N行 | `head -20 file.txt` |
| `tail -f` | 实时跟踪末尾 | `tail -f /var/log/nginx/access.log` |
| `grep` | 搜索文本 | `grep -i error /var/log/*.log` |
| `wc -l` | 统计行数 | `wc -l file.txt` |

## 权限管理

| 命令 | 说明 | 常用示例 |
|------|------|---------|
| `chmod 755` | 数字法改权限 | rwxr-xr-x = 755 |
| `chmod u+x` | 符号法加执行 | `chmod u+x script.sh` |
| `chown` | 改所有者 | `chown user:group file` |
| `chgrp` | 改组 | `chgrp dev file` |
| `ls -l` | 查看权限 | `-rw-r--r-- = 644` |
| `umask` | 默认权限掩码 | `umask 0022` |

**权限数字速记**：r=4 w=2 x=1 | 755=rwxr-xr-x | 644=rw-r--r-- | 600=rw-------

## 用户管理

| 命令 | 说明 |
|------|------|
| `useradd -m 用户名` | 创建用户（建家目录） |
| `usermod -aG 组 用户` | 追加到附加组 |
| `passwd 用户` | 设密码 |
| `userdel -r 用户` | 删除用户（含家目录） |
| `id 用户` | 查看UID/GID/组 |
| `who` | 查看当前登录用户 |
| `su - 用户` | 切换用户 |
| `sudo 命令` | 以root执行单条命令 |

## 进程管理

| 命令 | 说明 |
|------|------|
| `ps aux` | 进程快照 |
| `top` | 实时监控（P=CPU M=内存 k=杀进程 q=退出） |
| `kill PID` | 终止进程（默认SIGTERM） |
| `kill -9 PID` | 强制终止 |
| `pkill -f 关键词` | 按名称杀进程 |
| `jobs` / `bg` / `fg` | 后台任务管理 |
| `nohup 命令 &` | 后台运行（关终端不中断） |

## 磁盘与内存

| 命令 | 说明 |
|------|------|
| `df -h` | 分区使用率 |
| `du -sh 目录` | 目录大小 |
| `free -h` | 内存概况 |
| `lsblk` | 列出磁盘 |
| `mount` / `umount` | 挂载/卸载 |

## 网络

| 命令 | 说明 |
|------|------|
| `ip a` | 查看IP |
| `ip route` | 路由表 |
| `ss -tunlp` | 查看监听端口 |
| `ping -c 次数 IP` | 连通性测试 |
| `curl URL` | HTTP测试 |
| `nslookup 域名` | DNS查询 |
| `nc -zv IP 端口` | 端口可达性测试 |

## Vim 保命三连

| 场景 | 按键 |
|------|------|
| 编辑 | `i` 进入Insert→打字→`Esc` |
| 保存退出 | `:wq` |
| 不保存退出 | `:q!` |
| 搜索 | `/关键词` → `n`下一 `N`上一 |
| 删行 | `dd`（删整行）|
| 撤销 | `u` |
| 跳到行首/尾 | `gg` / `G` |
