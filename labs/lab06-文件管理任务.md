# Lab06：文件管理任务

> 课时：2 | 类型：个人 | 前置：Lab05

## 一、你会学到什么
- 能熟练使用 cp/mv/rm/mkdir/touch 完成文件增删改
- 理解通配符 * ? [] {} 的匹配规则
- 知道 rm -rf 有多危险，养成操作前"先 ls 确认"的习惯
- 会创建带时间戳的文件和目录

## 二、实验环境
- Rocky Linux 9 VM

## 三、实验步骤

### 步骤1：搭建实验目录

先在 /tmp 下创建一个沙盒环境，避免搞乱其他文件：

```bash
cd /tmp
mkdir lab06-workspace
cd lab06-workspace
pwd
# 应该输出 /tmp/lab06-workspace
```

> ⚠️ **安全规则**：本次实验所有危险操作（rm）都在这个沙盒里进行。以后做实验也养成这个习惯——先在 /tmp 建沙盒。

### 步骤2：touch 创建文件

```bash
# 创建空文件
touch file1.txt
touch file2.txt file3.txt       # 一次创建多个

# 批量创建
touch log_{1..5}.txt            # log_1.txt log_2.txt ... log_5.txt
touch report-{2026-01,2026-02,2026-03}.md

# 验证
ls -l

# touch 也可以更新时间戳
touch file1.txt                 # 把 file1.txt 的修改时间更新为现在
ls -l file1.txt
```

练习：
```bash
# 用通配符一次性创建 a.txt b.txt c.txt ... h.txt（共 8 个文件）
touch {a..h}.txt
ls -l ?.txt   # ? 匹配单个字符
```

> **验收点**：`ls *.txt` 能看到至少 15 个文件。

### 步骤3：mkdir 创建目录

```bash
# 创建目录
mkdir dir1
mkdir dir2 dir3                # 一次创建多个

# 创建嵌套目录
mkdir -p project/{src,docs,test,logs}
# 等价于：
# mkdir project
# mkdir project/src
# mkdir project/docs
# mkdir project/test
# mkdir project/logs

# 验证目录树
ls -R project/
# 或者
find project -type d
```

> **验收点**：`ls -R project/` 能看到 project 下 4 个子目录。

### 步骤4：cp 复制

```bash
# 复制文件
cp file1.txt file1-copy.txt
cp file1.txt dir1/

# 复制目录（必须加 -r）
cp -r project project-backup

# 保留属性复制（权限、时间戳、所有者）
cp -p file1.txt file1-preserved.txt
ls -l file1.txt file1-preserved.txt  # 看时间戳是否一致

# 复制并显示进度
cp -rv project project-backup2

# 避免覆盖已有文件
cp -i file1.txt dir1/          # 如果目标已有同名文件，会提示确认
# 或
cp -n file1.txt dir1/          # 不覆盖已有文件（静默跳过）
```

⚠️ **陷阱**：
```bash
# 看看这个命令会做什么（先分析，再执行）
cp file1.txt dir1/             # 复制到 dir1/ 里面
cp file1.txt dir1              # dir1 是目录，同上
cp file1.txt newfile           # newfile 不存在，会创建名为 newfile 的副本
cp file1.txt file2.txt         # file2.txt 已存在，会覆盖！内容变成 file1.txt 的内容
```

> **验收点**：能区分 "cp 源文件 目录/" 和 "cp 源文件 新文件名" 两种用法。

### 步骤5：mv 移动与重命名

```bash
# 重命名（mv 的核心功能）
mv file1.txt file-renamed.txt

# 移动到目录
mv file2.txt dir1/

# 批量移动
mv log_*.txt dir2/

# 移动整个目录
mv dir3 dir4                   # dir4 不存在 → dir3 被重命名为 dir4
                                # dir4 已存在 → dir3 被移动到 dir4 里面

# 验证
ls -l
ls -l dir1/
ls -l dir2/
```

练习：
```bash
# 1. 把 file3.txt 重命名为 myfile.txt
# 2. 把 .md 结尾的文件全部移到 project/docs/ 下
# 3. 如果把 dir1 移动到 newdir（不存在），newdir 里有什么？
```

> **验收点**：能区分 mv 的"重命名"和"移动"两种语义，理解它们本质相同（改 inode 的路径名）。

### 步骤6：rm 删除（危险操作）

```bash
# ⚠️ 在沙盒里随便玩，但养成一个习惯：
# 删除前先用 ls 确认要删什么！

# 删除文件（确认后再敲）
ls *.txt                       # 1. 先看看有哪些 txt
rm file1-copy.txt              # 2. 确认后删除

# 强制删除（跳过确认）
rm -f file1-preserved.txt

# 删除目录
rm -r dir2/                    # 删除目录及其中所有内容

# ⚠️ 终极危险命令（千万不要在根目录执行）
# rm -rf /                     # 删库跑路！会尝试删除整个系统！

# 安全的批量删除示例
ls /tmp/lab06-workspace/*.bak 2>/dev/null  # 先看看有没有 .bak 文件
# 如果确认无误：
# rm /tmp/lab06-workspace/*.bak
```

```bash
# 交互式删除（每次确认）
rm -i *.txt                    # 每个文件都问 "rm: remove regular file?"
                               # 回答 y 删除，n 跳过
```

> **验收点**：能说出 `rm -rf /` 为什么危险，以及如何避免（用绝对路径时永远先 pwd 确认自己在哪里）。

### 步骤7：通配符综合练习

```bash
cd /tmp/lab06-workspace
# 重新创建一批测试文件
touch file{1..20}.txt
touch report{1..5}.md
touch data-{a,b,c}-{1,2,3}.csv
mkdir subdir{1..5}

# 练习：不看答案，写出命令
# ① 列出 file1.txt 到 file9.txt（一位数的）
ls file?.txt

# ② 列出 file10.txt 到 file20.txt（两位数的）
ls file[1-9][0-9].txt    # 或者 file1?.txt

# ③ 列出所有 .md 和 .csv 文件
ls *.md *.csv

# ④ 列出以 data- 开头的文件
ls data-*

# ⑤ 列出 file1.txt file3.txt file5.txt（奇数）
ls file[13579].txt file1[13579].txt 2>/dev/null

# ⑥ 删除所有 .txt 文件（先 ls 确认！）
ls *.txt
# rm *.txt        # 确认后再执行

# ⑦ 删除所有不是 .md 的文件
ls
# rm !(*.md)      # 需要 extglob: shopt -s extglob
```

> **验收点**：能独立写出用 `* ? []` 组合的通配符命令。

## 五、验收标准
- [ ] 能创建嵌套目录 `mkdir -p a/b/c/d`
- [ ] 能批量创建 `touch file_{01..10}.txt`
- [ ] 能区分 `cp file dir/` 和 `cp file newname`
- [ ] 知道 `rm -rf` 的危险性，养成"先 ls 再 rm"的习惯
- [ ] 能用 `* ? []` 写通配符匹配文件名
- [ ] `ls /tmp/lab06-workspace` 的目录内容符合预期

## 六、常见问题

**Q: `cp -r` 和 `cp -a` 有什么区别？**
A: `-r` 只递归复制；`-a` 是归档模式（= -r + 保留权限/时间戳/软链接/所有者），更完整。建议复制重要目录时用 `cp -a`。

**Q: 不小心 `rm` 删除了重要文件怎么恢复？**
A: Linux 没有回收站，rm 就是彻底删除。恢复极其困难（需要专业工具且需立即停止写入磁盘）。所以：**重要文件用 `cp -a` 先备份，删除前先 `ls` 确认。** 生产环境建议用 `trash-cli` 代替裸 rm。

**Q: 通配符 `*` 会匹配隐藏文件吗？**
A: 不会，`*` 不匹配 `.` 开头的隐藏文件。要匹配隐藏文件用 `.*`，但注意 `.*` 也会匹配 `.` 和 `..`。

## 七、清理
```bash
rm -rf /tmp/lab06-workspace
```
