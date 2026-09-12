# 实验3：文本编辑、文件查找与归档恢复

> 所属模块：模块一 Linux基础运维  
> 建议学时：2学时  
> 实验方式：个人  
> 对应教材：《模块一 Linux基础运维》第5—6章  
> 前置实验：实验2  
> 项目成果：修改后的配置文件、文件查找记录、归档文件和恢复验证记录

## 一、项目情境

项目目录已经建立，但运维人员还需要修改配置、快速定位文件，并在变更前进行归档。你需要使用Vim修改实验配置，使用`find`定位目标，创建软链接和硬链接，最后对项目目录进行归档并验证能够恢复。

## 二、实验目标

### 1. 知识目标

1. 说明V中普通模式、插入模式和命令行模式的作用。
2. 区分文件名、inode、硬链接和软链接。
3. 区分归档和压缩，说明备份必须进行恢复验证的原因。

### 2. 能力目标

1. 使用Vim完成定位、修改、保存、撤销和退出。
2. 使用`find`按名称、类型、大小和时间查找文件。
3. 创建并验证软链接和硬链接。
4. 使用`tar`创建归档、查看内容并恢复到新目录。

### 3. 素质目标

1. 形成配置修改前备份、修改后比较和验证的习惯。
2. 形成不直接覆盖唯一备份的恢复意识。
3. 养成根据目标选择查找条件、避免扫描无关目录的习惯。

## 三、知识准备

### 1. Vim模式

| 模式 | 主要用途 | 常用操作 |
|---|---|---|
| 普通模式 | 移动、复制、删除、撤销 | `h j k l`、`dd`、`yy`、`p`、`u` |
| 插入模式 | 输入文本 | `i`、`a`、`o`进入，`Esc`返回 |
| 命令行模式 | 保存、退出、搜索替换 | `:w`、`:q`、`:wq`、`:%s/旧/新/g` |

### 2. 链接

- 硬链接是同一个inode的另一个文件名，删除一个名称后数据仍可通过其他硬链接访问。
- 软链接保存目标路径，可以跨文件系统，也可以指向目录；目标消失后软链接会失效。

### 3. 归档与压缩

`tar`先把多个文件组织成一个归档，也可以调用gzip等算法压缩。常用组合：

| 命令 | 作用 |
|---|---|
| `tar -cf` | 创建未压缩归档 |
| `tar -czf` | 创建gzip压缩归档 |
| `tar -tf` | 查看归档内容 |
| `tar -xzf` | 解压gzip归档 |

## 四、实验环境

- 使用实验2保留的`~/m1-project`。
- 使用`rocky-server`登录。
- 确认配置存在：

```bash
test -f ~/m1-project/config/app.conf
echo $?
```

退出码应为0。

## 五、项目任务

1. 备份并使用Vim修改配置。
2. 使用不同条件查找项目文件。
3. 创建并验证软链接和硬链接。
4. 创建带时间标记的项目归档。
5. 把归档恢复到新目录并比较关键文件。

## 六、实验步骤

### 任务一：使用Vim修改配置

#### 步骤1：创建变更前备份

```bash
cp -p ~/m1-project/config/app.conf ~/m1-project/backup/app.conf.before-vim
cmp ~/m1-project/config/app.conf ~/m1-project/backup/app.conf.before-vim
echo $?
```

> **验收点**：备份存在，`cmp`返回0。

#### 步骤2：使用Vim编辑

```bash
vim ~/m1-project/config/app.conf
```

在Vim中完成：

1. 按`i`进入插入模式。
2. 将`mode=development`改为`mode=training`。
3. 新增一行`log_level=info`。
4. 按`Esc`返回普通模式。
5. 输入`:wq`保存退出。

验证：

```bash
cat -n ~/m1-project/config/app.conf
diff -u ~/m1-project/backup/app.conf.before-vim ~/m1-project/config/app.conf
```

`diff`返回非0表示文件存在差异，本步骤中是预期结果。

> **验收点**：配置包含`mode=training`和`log_level=info`，能够解释`diff`结果。

#### 步骤3：练习搜索和不保存退出

```bash
vim ~/m1-project/config/app.conf
```

在普通模式输入`/log_level`搜索。按`n`查找下一个结果。临时修改任意字符后按`Esc`，输入`:q!`退出，再执行：

```bash
grep '^log_level=' ~/m1-project/config/app.conf
```

> **验收点**：临时修改没有保存，原配置仍为`log_level=info`。

### 任务二：查找文件

#### 步骤4：按名称和类型查找

```bash
find ~/m1-project -type f -name '*.conf' -print
find ~/m1-project -type f -name '*.log' -print
find ~/m1-project -type d -maxdepth 2 -print | sort
```

查找命令程序位置：

```bash
command -v tar
which vim
type cd
```

`find`搜索文件系统对象，`command -v`或`which`查找将执行的命令，二者用途不同。

> **验收点**：找到`app.conf`，并能说明`find`与`which`的区别。

#### 步骤5：按大小和时间查找

```bash
find ~/m1-project -type f -size +0c -printf '%s %p\n' | sort -n
find ~/m1-project -type f -mmin -30 -printf '%TY-%Tm-%Td %TH:%TM %p\n'
```

第一条查找非空文件，第二条查找最近30分钟修改的文件。实际结果与实验完成时间有关。

> **验收点**：保存两种条件的查找结果，不能把“无结果”直接解释为命令失败。

### 任务三：链接实验

#### 步骤6：创建硬链接和软链接

```bash
mkdir -p ~/m1-project/links
ln ~/m1-project/config/app.conf ~/m1-project/links/app.conf.hard
ln -s ../config/app.conf ~/m1-project/links/app.conf.soft
ls -li ~/m1-project/config/app.conf ~/m1-project/links/app.conf.*
readlink ~/m1-project/links/app.conf.soft
```

观察：原文件和硬链接inode编号相同，软链接显示保存的目标路径。

#### 步骤7：验证链接行为

```bash
printf 'link_test=ok\n' >> ~/m1-project/links/app.conf.hard
tail -n 2 ~/m1-project/config/app.conf
cat ~/m1-project/links/app.conf.soft
```

通过硬链接追加内容后，原文件和软链接读取到相同变化，因为它们最终访问同一份数据。

> **验收点**：能根据`ls -li`和文件内容说明两种链接的区别。

### 任务四：归档与恢复

#### 步骤8：创建归档

```bash
mkdir -p ~/m1-project/backup/archives
ARCHIVE=~/m1-project/backup/archives/m1-project-$(date +%Y%m%d-%H%M).tar.gz
tar --exclude='m1-project/backup/archives' -czf "$ARCHIVE" -C ~ m1-project
printf 'archive=%s\n' "$ARCHIVE"
ls -lh "$ARCHIVE"
tar -tzf "$ARCHIVE" | sed -n '1,30p'
```

排除归档目录是为了避免把正在创建的归档再次打包进去。

> **验收点**：归档非空，内容列表包含`m1-project/config/app.conf`。

#### 步骤9：恢复到新目录

```bash
RESTORE_DIR=/tmp/lab03-restore
test ! -e "$RESTORE_DIR" || { printf 'restore directory already exists\n'; exit 1; }
mkdir -p "$RESTORE_DIR"
tar -xzf "$ARCHIVE" -C "$RESTORE_DIR"
find "$RESTORE_DIR/m1-project" -maxdepth 2 -type f -printf '%P\n' | sort
cmp ~/m1-project/config/app.conf "$RESTORE_DIR/m1-project/config/app.conf"
echo $?
```

恢复到新目录可以避免覆盖正在使用的数据。

> **验收点**：恢复后的配置与当前配置一致，`cmp`返回0。

#### 步骤10：生成校验值

```bash
sha256sum "$ARCHIVE" | tee ~/m1-project/evidence/lab03-archive.sha256
```

校验值可以帮助判断归档文件在复制或保存后是否发生变化，但不能证明业务数据一定满足需求，因此仍需要实际恢复。

> **验收点**：校验文件存在，归档已经完成一次真实恢复。

## 七、独立实践

1. 使用Vim把`port=8080`改为`port=9090`，修改前创建新的备份。
2. 使用`find`只列出`~/m1-project`中大于20字节的普通文件。
3. 为`web/index.html`创建一个相对路径软链接。
4. 创建一个只包含`config`和`web`的归档。
5. 恢复到另一个新目录，并比较两个关键文件。

## 八、验收标准

- [ ] 能使用Vim完成搜索、修改、保存和不保存退出。
- [ ] 配置修改前存在可用备份。
- [ ] 能使用`find`按名称、类型、大小和时间查找。
- [ ] 能通过inode和`readlink`区分硬链接与软链接。
- [ ] 归档文件非空且内容列表正确。
- [ ] 已把归档恢复到新目录。
- [ ] 恢复后的关键文件通过内容比较。
- [ ] 已保存归档SHA256和独立实践结果。

## 九、成果提交

1. 修改后的`config/app.conf`。
2. `backup/app.conf.before-vim`及独立实践备份。
3. 文件查找命令和结果。
4. 归档文件名称、大小和内容列表。
5. `evidence/lab03-archive.sha256`。
6. 恢复目录文件清单及`cmp`验证结果。

## 十、常见问题

### Q1：Vim界面无法输入文字

Vim启动后处于普通模式。按`i`进入插入模式，输入完成后按`Esc`返回普通模式。

### Q2：输入:q提示No write since last change

文件已经修改。需要保存时使用`:wq`；确认放弃修改时使用`:q!`。

### Q3：创建硬链接提示Invalid cross-device link

硬链接通常不能跨文件系统。改为在同一文件系统创建，或者根据需求使用软链接。

### Q4：tar提示file changed as we read it

通常是把归档文件创建在被归档目录内部且没有排除，导致tar读到了正在变化的归档。使用本实验的`--exclude`，或把归档放到被归档目录外。

### Q5：有归档文件为什么还要恢复

归档可能为空、损坏、路径错误或缺少关键文件。只有恢复并验证内容，才能证明当前备份具备基本可用性。

## 十一、课后思考与拓展

1. 为什么软链接可以指向目录，而普通用户通常不能给目录创建硬链接？
2. 如果恢复时直接覆盖生产目录，会产生什么风险？
3. SHA256校验通过和数据可恢复分别证明了什么？

## 十二、环境保留与清理

保留`~/m1-project`和归档文件。检查恢复目录后可清理：

```bash
find /tmp/lab03-restore -maxdepth 2 -print
rm -r /tmp/lab03-restore
```

