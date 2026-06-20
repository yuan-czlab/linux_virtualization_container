# Lab07：查找与链接

> 课时：2 | 类型：个人 | 前置：Lab06

## 一、你会学到什么
- 能熟练使用 find 按名称/类型/大小/时间查找文件
- 理解 inode 是什么，能通过 inode 理解硬链接和软链接的本质区别
- 会在实际场景中选择硬链接还是软链接

## 二、实验环境
- Rocky Linux 9 VM

## 三、实验核心概念

```
软链接（ln -s）：快捷方式，指向路径名
  删除原文件 → 软链接变 "死链"（指向不存在的路径）
  可以跨分区

硬链接（ln）：同一 inode 的另一个名字
  删除原文件 → 硬链接仍然可用（inode 还在）
  不能跨分区，不能链接目录
```

## 四、实验步骤

### 步骤1：搭建实验环境

```bash
cd /tmp
mkdir lab07-workspace
cd lab07-workspace

# 创建测试目录和文件
mkdir -p deep/nested/dir
touch file1.txt
touch file2.log
touch file3.conf
dd if=/dev/zero of=bigfile.bin bs=1M count=50 2>/dev/null
dd if=/dev/zero of=small.txt bs=1K count=10 2>/dev/null

# 创建不同时间的文件
touch -t 202601010000 oldfile.txt      # 1月1日的文件
touch -t 202606010000 middlefile.txt   # 6月1日的文件
touch newfile.txt                       # 刚才创建的文件

# 查看
ls -lh
```

> **验收点**：`ls -lh` 能看到 bigfile.bin（50M）和 small.txt（10K）。

### 步骤2：find 按名称查找

```bash
# 在当前目录按名称查找
find . -name "*.txt"
find . -name "file*"                   # file 开头的
find . -iname "FILE*"                  # 不区分大小写（-iname）

# 在 /etc 下查找（限制深度，否则太慢）
find /etc -maxdepth 2 -name "*.conf" | head -10
find /etc -maxdepth 1 -name "host*"

# 按路径匹配
find /etc -path "*/ssh/*"
```

练习：
```bash
# 在 /etc 下查找所有 .conf 结尾的文件（最多两层深度），输出前 10 个
find /etc -maxdepth 2 -name "*.conf" 2>/dev/null | head -10
```

> **验收点**：能区分 `-name` 和 `-iname`。

### 步骤3：find 按类型查找

```bash
# 类型选项：f=文件 d=目录 l=软链接

# 只查目录
find . -type d

# 只查文件
find . -type f

# 查空文件
find . -type f -empty

# 查空目录
find . -type d -empty
```

> **验收点**：`find . -type d` 能看到 deep/nested/dir 嵌套目录。

### 步骤4：find 按大小查找

```bash
# 大小单位：c=字节 k=KB M=MB G=GB
# + 表示大于，- 表示小于

# 大于 10MB 的文件
find . -type f -size +10M

# 小于 100KB 的文件
find . -type f -size -100k

# 精确 50MB（块数匹配，不精确，建议用范围）
find . -type f -size 50M

# 查找 1KB 到 1MB 之间的文件
find . -type f -size +1k -size -1M
```

练习：
```bash
# 在 /var/log 下查找大于 1MB 的日志文件
find /var/log -type f -size +1M 2>/dev/null
```

> **验收点**：能找到当前目录 50MB 的 bigfile.bin。

### 步骤5：find 按时间查找

```bash
# -mtime：修改时间（天），+n 表示 n 天前，-n 表示 n 天内
# -mmin：修改时间（分钟）

# 最近 30 天修改过的文件
find . -type f -mtime -30

# 30 天前修改的文件
find . -type f -mtime +30

# 最近 10 分钟修改过的文件
find . -type f -mmin -10

# 按访问时间（-atime）、状态变更时间（-ctime）同理
```

> **验收点**：能找到 2026 年 1 月 1 日的 oldfile.txt（距今超过 30 天）。

### 步骤6：find 执行操作（-exec）

```bash
# 语法：find ... -exec 命令 {} \;
# {} 会被替换为找到的文件路径
# \; 表示命令结束

# 找到所有 .txt 并查看内容
find . -name "*.txt" -exec cat {} \;

# 找到所有 .log 并删除（先 ls 验证！）
find . -name "*.log" -ls            # 1. 先看找到什么
find . -name "*.log" -exec rm {} \; # 2. 确认后删除

# 找到所有 .conf 并移动到 backups/ 下
mkdir backups
find . -name "*.conf" -exec mv {} backups/ \;
ls backups/

# 批量修改权限
find . -type f -name "*.sh" -exec chmod +x {} \;

# 使用 -ok 替代 -exec（每个操作前确认）
find . -type f -name "*.txt" -ok rm {} \;
```

⚠️ **注意**：`-exec` 对每个文件执行一次命令，文件多时很慢。可以改用 `xargs`：
```bash
find . -name "*.txt" | xargs rm
# 或者使用 -exec + 语法（比 \; 快）
find . -name "*.txt" -exec rm {} +
```

> **验收点**：能用 `-exec` 或 `xargs` 批量处理 find 的结果。

### 步骤7：理解 inode

```bash
# 查看文件的 inode 号
ls -li
# 输出：inode号 权限 链接数 所有者 组 大小 时间 文件名
#   ↑ 关注这一列

# 查看 inode 详情
stat file1.txt
# 关注：Inode、Links、Size、Blocks
```

> **验收点**：能说出 inode 存储了文件的元数据（大小/权限/时间/块位置），但不存储文件名。

### 步骤8：硬链接（ln）

```bash
# 创建硬链接
ln file1.txt hardlink-to-file1.txt
ls -li
# file1.txt 和 hardlink-to-file1.txt 有相同的 inode 号！

# 验证：修改一个，另一个也会变
echo "hello hard link" >> file1.txt
cat hardlink-to-file1.txt       # 能看到同样的内容！

# 验证：删除原文件，硬链接仍然可用
rm file1.txt
cat hardlink-to-file1.txt       # 内容还在！
ls -li hardlink-to-file1.txt    # inode 还在

# 再创建一个硬链接，链接数会增加
ln hardlink-to-file1.txt another-hardlink.txt
stat hardlink-to-file1.txt | grep Links   # Links: 2
```

关键理解：
```
创建硬链接时：同一个 inode 多了一个文件名
删除文件时：只是删掉一个文件名，inode 的链接计数减 1
只有当链接计数变为 0，磁盘空间才真正释放
```

> **验收点**：能解释为什么"删除 file1.txt 后 hardlink 还能用"。

### 步骤9：软链接（ln -s）

```bash
# 重建 file1.txt
echo "original content" > file1.txt

# 创建软链接
ln -s file1.txt symlink-to-file1.txt
ls -li
# file1.txt 和 symlink-to-file1.txt 有不同的 inode 号！
# 软链接的权限是 lrwxrwxrwx（不是真实权限）

# 验证：通过软链接访问
cat symlink-to-file1.txt        # 能看到 file1.txt 的内容

# 验证：删除原文件，软链接"断裂"
rm file1.txt
cat symlink-to-file1.txt        # No such file or directory！
ls -l symlink-to-file1.txt      # 显示为红色（如果有颜色），指向不存在的文件
# 这是"悬空链接"（dangling symlink）

# 重建原文件，软链接恢复
echo "new content" > file1.txt
cat symlink-to-file1.txt        # 又能读了！因为路径又存在了
```

> **验收点**：能对比硬链接和软链接在被删除原文件后的行为差异。

### 步骤10：硬链接 vs 软链接对比

```bash
# 不可跨分区（硬链接限制）
mkdir /tmp/other-mountpoint
ln file1.txt /tmp/other-mountpoint/link-to-file1
# ln: failed to create hard link: Invalid cross-device link

# 不可链接目录（硬链接限制，root 也不行）
ln deep link-to-deep
# ln: deep: hard link not allowed for directory

# 而软链接都可以：
ln -s /tmp/lab07-workspace/file1.txt /tmp/other-mountpoint/symlink
ls -l /tmp/other-mountpoint/symlink    # 可以
ln -s deep link-to-deep                # 可以
ls -l link-to-deep
```

> **验收点**：能说出硬链接的 2 个限制（不能跨分区、不能链接目录）。

## 五、验收标准
- [ ] 能独立用 `find -name`、`find -type`、`find -size` 找到目标文件
- [ ] 能解释 inode 是什么
- [ ] 能说出硬链接和软链接的 3 个区别（inode 是否相同/删原文件后的行为/能否跨分区和目录）
- [ ] 能用 `ls -li` 查看 inode 号
- [ ] 能说出生产环境中硬链接和软链接各自的适用场景

## 六、常见问题

**Q: 硬链接和原文件，谁才是"真正的"文件？**
A: 没有"真正的"文件。硬链接就是同一个 inode 的多个名字，完全平等。第一个创建的并不特殊。

**Q: 软链接的权限是 777，这不安全？**
A: 软链接本身的权限没有意义，实际访问时用的是目标文件的权限。`ls -l symlink` 看的是链接本身的 777，`ls -L symlink` 才会显示目标文件的真实权限。

**Q: `find` 查出来的文件太多怎么办？**
A: 用 `-maxdepth` 限制深度；或者在 `-exec` 中用 `+` 代替 `\;` 减少进程数；或者对结果先 `wc -l` 看数量。

**Q: 生产中硬链接的典型用途？**
A: 备份策略：`ln backup-2026-06-20 backup-2026-06-21` 然后对 6-21 做增量。两个名字指向同一个 inode，只占一份磁盘空间。另外 rsnapshot 这类备份工具就是利用硬链接节省空间的。

## 七、清理
```bash
rm -rf /tmp/lab07-workspace /tmp/other-mountpoint
```
