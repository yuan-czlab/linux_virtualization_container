# Lab09：文件权限管理练习

> 课时：2 | 类型：个人 | 前置：Lab08（用户与组管理）

## 一、你会学到什么
- 能解释 rwx 对文件和目录的不同含义
- 能用 chmod 数字法和符号法修改权限
- 能用 chown/chgrp 修改文件所属
- 能排查"Permission denied"问题
- 理解 umask 如何影响默认权限

## 二、实验环境
- Rocky Linux 9 VM，以 student 用户登录

## 三、实验核心概念

| 权限 | 字母 | 数字 | 对文件 | 对目录 |
|------|------|------|--------|--------|
| 读 | r | 4 | 读取内容（cat） | 列出文件名（ls） |
| 写 | w | 2 | 修改内容（vim >） | 创建/删除文件（touch/rm） |
| 执行 | x | 1 | 执行程序（./script） | 进入目录（cd） |

**数字速查**：7=rwx  6=rw-  5=r-x  4=r--  2=-w-  1=--x  0=---

## 四、实验步骤

### 步骤1：搭建实验环境
```bash
cd /tmp && mkdir lab09 && cd lab09
touch file1.txt
echo "#!/bin/bash\necho hello" > script.sh
mkdir testdir
echo "data" > testdir/data.txt

# 创建两个测试用户
sudo useradd -m alice 2>/dev/null
sudo useradd -m bob 2>/dev/null
echo "alice:alice123" | sudo chpasswd
echo "bob:bob123" | sudo chpasswd
```

### 步骤2：chmod 数字法

```bash
# 默认权限 644 = rw-r--r--
ls -l file1.txt

# 改为只有自己能读写（私密文件）
chmod 600 file1.txt
ls -l file1.txt               # 期望：-rw-------

# 改为所有人可读（网页文件）
chmod 644 file1.txt
ls -l file1.txt               # 期望：-rw-r--r--

# 改为可执行脚本
chmod 755 script.sh
ls -l script.sh               # 期望：-rwxr-xr-x

# 改为完全开放（不推荐）
chmod 777 file1.txt
ls -l file1.txt               # 期望：-rwxrwxrwx
```

> **验收点**：`ls -l` 确认权限与 chmod 数字值一致。

### 步骤3：chmod 符号法

```bash
chmod u+x script.sh           # 所有者加执行权限
chmod g-w file1.txt           # 组去掉写权限
chmod o= file1.txt            # 其他人去掉所有权限
chmod a+r file1.txt           # 所有人加读权限
chmod u=rwx,g=rx,o= script.sh # 同时设置三组
ls -l
```

> **验收点**：能用符号法独立完成权限修改。

### 步骤4：chown 和 chgrp

```bash
sudo chown alice file1.txt
ls -l file1.txt               # 所有者变成 alice

sudo chgrp bob file1.txt
ls -l file1.txt               # 组变成 bob

sudo chown root:root file1.txt  # 同时改所有者和组
```

### 步骤5：目录权限实验（重点！）

```bash
# 场景A：目录有 rwx (755) — 正常
chmod 755 testdir
ls testdir/                   # ✓ 能列出
cd testdir && pwd && cd ..    # ✓ 能进入
cat testdir/data.txt          # ✓ 能读文件

# 场景B：目录只有 r 没有 x (444)
chmod 444 testdir
ls testdir/                   # ✓ 能看到文件名
cd testdir                    # ✗ Permission denied
# 结论：没有 x 进不去，即使有 r 也白搭

# 场景C：目录只有 x 没有 r (111)
chmod 111 testdir
ls testdir/                   # ✗ Permission denied
cd testdir                    # ✓ 能进入！
cat data.txt                  # ✓ 知道文件名就能读（盲目录）
cd ..

# 恢复
chmod 755 testdir
```

> **验收点**：能说出"目录没有x权限的三个后果"。

### 步骤6：多用户权限场景

```bash
# 创建共享目录
sudo mkdir -p /shared/project
sudo groupadd dev-team 2>/dev/null
sudo usermod -aG dev-team alice
sudo usermod -aG dev-team bob
sudo chown root:dev-team /shared/project
sudo chmod 770 /shared/project

# alice 创建文件
su alice -c "echo 'alice work' > /shared/project/alice.txt"
# bob 能读吗？
su bob -c "cat /shared/project/alice.txt"
# student 能读吗？
cat /shared/project/alice.txt
```

> **验收点**：理解组权限让同组用户共享目录。

### 步骤7：umask

```bash
umask                         # 查看当前值（通常是 0022）

# umask=0022 下：
# 文件默认 = 666-022 = 644 (rw-r--r--)
# 目录默认 = 777-022 = 755 (rwxr-xr-x)

# 验证
touch umask-test-file
mkdir umask-test-dir
ls -l umask-test-file         # -rw-r--r--
ls -ld umask-test-dir         # drwxr-xr-x

# 临时修改 umask 看效果
umask 0002
touch umask2-file
mkdir umask2-dir
ls -l umask2-file             # -rw-rw-r--
ls -ld umask2-dir              # drwxrwxr-x

umask 0022                    # 恢复默认
```

---

## 五、练习题（做完实验步骤后完成）

### 练习1：权限计算（20分）

写出以下权限的 chmod 数字值和含义：

| 权限字符串 | 数字 | 含义（谁有什么权限） |
|-----------|------|-------------------|
| -rwxr-xr-x | | |
| -rw-r--r-- | | |
| -rw------- | | |
| drwx------ | | |
| -rwxrwxrwx | | |

### 练习2：目录权限判断（20分）

目录 `/data` 的权限是 `d--x--x--x` (111)，文件 `/data/file.txt` 的权限是 `-rw-r--r--` (644)。

| 操作 | 能/不能？ | 原因 |
|------|----------|------|
| `ls /data/` | | |
| `cd /data/` | | |
| `cat /data/file.txt` | | |
| `echo "x" >> /data/file.txt` | | |
| `touch /data/new.txt` | | |
| `rm /data/file.txt` | | |

### 练习3：搭建 Web 开发团队共享环境（30分）

**场景**：创建共享目录 `/srv/webapp`，满足：
1. 创建组 `web-team`，用户 `alice`、`bob` 加入该组
2. `/srv/webapp` 目录：所有者和组都是 `root:web-team`，权限 770
3. 目录下的新建文件自动继承 `web-team` 组（SGID）
4. 每个人只能删除自己创建的文件（sticky bit）
5. 验证：alice 和 bob 都能在目录中创建和修改文件，但互相不能删对方的文件

### 练习4：SSH 私钥权限问题（15分）

```bash
# 生成测试密钥
ssh-keygen -t ed25519 -f /tmp/test-key -N "" 2>/dev/null
chmod 644 /tmp/test-key
```

用 `ssh -v` 连接时，SSH 会报什么错？权限应该是多少？写出修复命令。

### 练习5：umask 应用（15分）

1. 想让新建文件的默认权限是 660（组可读写），umask 应该设为多少？
2. 想让新建目录的默认权限是 770，umask 应该设为多少？
3. 如何让 umask 永久生效？

---

## 六、验收标准
- [ ] chmod 数字法（755/644/600）和符号法（u+x/g-w/o=）都能熟练使用
- [ ] 理解目录 rwx 的特殊性（x 是通行证）
- [ ] 练习 1-5 全部完成
- [ ] 练习 3 的共享目录环境搭建正确并验证通过

## 七、清理
```bash
sudo userdel -r alice 2>/dev/null
sudo userdel -r bob 2>/dev/null
sudo groupdel dev-team 2>/dev/null
sudo groupdel web-team 2>/dev/null
sudo rm -rf /shared /srv/webapp /tmp/lab09 /tmp/test-key /tmp/test-key.pub
```
