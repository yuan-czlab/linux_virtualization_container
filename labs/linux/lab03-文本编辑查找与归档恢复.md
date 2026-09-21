# 实验3：文本编辑、文件查找与归档恢复

> 所属模块：模块一 Linux基础运维  
> 建议学时：2学时  
> 实验方式：个人  
> 对应教材：《模块一 Linux基础运维》第5—6章  
> 知识前置：实验2中的路径、文件和目录操作
> 状态依赖：实验2创建的`~/m1-project/config/app.conf`及项目目录树
> 建议起点：`Linux-L0`并保留实验2成果
> 项目成果：修改后的配置文件、文件查找记录、归档文件和恢复验证记录

## 一、项目情境

项目目录已经建立，但运维人员还需要修改配置、从真实项目文件中筛选信息、快速定位文件，并在变更前进行归档。你需要使用Vim修改实验配置，使用`grep`、`wc`、`sort`、`find`和管道形成审计证据，创建软链接和硬链接，最后对项目目录进行归档并验证能够恢复。

## 二、实验目标

### 1. 知识目标

1. 说明Vim中普通模式、插入模式和命令行模式的作用。
2. 区分文件名、inode、硬链接和软链接。
3. 区分归档和压缩，说明备份必须进行恢复验证的原因。

### 2. 能力目标

1. 使用Vim完成定位、修改、保存、撤销和退出。
2. 使用`grep`、`wc`、`sort`、`find`和管道分析真实项目文件。
3. 使用`find`按名称、类型、大小和时间查找文件。
4. 创建并验证软链接和硬链接。
5. 使用`tar`创建归档、查看内容并恢复到新目录。

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

操作前打开[Linux目录树、路径与链接动画](../../animations/02-linux-filesystem-paths-links/index.html)并切换到“inode与链接”。先预测删除原文件后的结果，再在本实验中用`ls -li`、`stat`和`cat`验证。

### 3. 文本筛选与文件查找

- `grep`根据内容筛选行，`find`根据文件名、类型、大小、时间等属性查找文件系统对象。
- `wc -l`统计输入行数，`sort -n`按数字排序，`sort -nr`按数字倒序。
- 管道应从左向右逐级构造。先单独验证前一条命令的输出，再增加下一段处理。
- `tee`可以把结果同时显示在屏幕并写入证据文件。

### 4. 归档与压缩

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
test -f "$HOME/m1-project/config/app.conf"
```

上一条命令没有报错才表示文件存在。若检查失败，停止实验并恢复实验2成果，不要创建同名空文件代替。检查通过后再查看项目文件：

```bash
find "$HOME/m1-project" -maxdepth 2 -type f -printf '%P\n' | sort
```

必须能够看到`config/app.conf`以及实验2保留的项目文件。

## 五、项目任务

1. 备份并使用Vim修改配置。
2. 筛选真实配置和日志内容，形成项目审计证据。
3. 使用不同条件查找项目文件。
4. 创建并验证软链接和硬链接。
5. 创建带时间标记的项目归档。
6. 把归档恢复到新目录并比较关键文件。

本实验按90分钟有效上机时间组织：Vim修改约15分钟，查找与内容审计约25分钟，链接验证约15分钟，归档恢复约25分钟，证据整理约10分钟。教材中的完整命令已经逐条练习，本实验只完成一次真实项目闭环，不追求把同类命令反复执行。

## 六、实验步骤

### 任务一：使用Vim修改配置

#### 步骤1：创建变更前备份

```bash
cp -p ~/m1-project/config/app.conf ~/m1-project/backup/app.conf.before-vim
```

```bash
cmp ~/m1-project/config/app.conf ~/m1-project/backup/app.conf.before-vim
```

`cmp`没有输出表示两个文件一致。再确认备份非空：

```bash
test -s ~/m1-project/backup/app.conf.before-vim
```

> **验收点**：备份存在且非空，`cmp`没有报告差异。

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
```

```bash
diff -u ~/m1-project/backup/app.conf.before-vim ~/m1-project/config/app.conf
```

`diff`返回非0表示文件存在差异，本步骤中是预期结果。

> **验收点**：配置包含`mode=training`和`log_level=info`，能够解释`diff`结果。

#### 步骤3：使用搜索确认修改（有余量时练习不保存退出）

```bash
vim ~/m1-project/config/app.conf
```

在普通模式输入`/log_level`搜索，确认能够定位新增配置。时间充足时，可临时修改任意字符后按`Esc`，输入`:q!`退出，体会“放弃本次修改”。然后执行：

```bash
grep '^log_level=' ~/m1-project/config/app.conf
```

> **验收点**：能够在Vim中搜索`log_level`，退出后原配置仍为`log_level=info`。`:q!`练习不计入必交证据。

### 任务二：查找文件

#### 步骤4：按名称和类型查找

```bash
find ~/m1-project -type f -name '*.conf' -print
```

```bash
find ~/m1-project -type f -name '*.log' -print
```

```bash
find ~/m1-project -type d -maxdepth 2 -print | sort
```

`find`搜索文件系统中的目录和文件；`command -v`、`which`和`type`已经在教材1.5中用于判断命令来源，本实验不再重复。

> **验收点**：找到`app.conf`，并能说明这里查找的是文件系统对象而不是Shell命令来源。

#### 步骤5：按大小和时间查找

```bash
find ~/m1-project -type f -size +0c -printf '%s %p\n' | sort -n
```

```bash
find ~/m1-project -type f -mmin -30 -printf '%TY-%Tm-%Td %TH:%TM %p\n'
```

第一条查找非空文件，第二条查找最近30分钟修改的文件。实际结果与实验完成时间有关。

> **验收点**：保存两种条件的查找结果，不能把“无结果”直接解释为命令失败。

#### 步骤6：筛选项目内容并保存审计证据

本步骤只分析实验2和本实验已经产生的真实文件，不另外编造日志。先确认配置与部署日志都存在：

```bash
test -s ~/m1-project/config/app.conf
```

```bash
test -s ~/m1-project/logs/deploy-history.log
```

两条命令都没有报错才继续。先在`config`和`logs`目录中筛选关键配置与部署状态：

```bash
grep -RInE 'mode=|port=|deployment=' ~/m1-project/config ~/m1-project/logs
```

确认输出符合预期后，显示并保存同一结果：

```bash
grep -RInE 'mode=|port=|deployment=' ~/m1-project/config ~/m1-project/logs | tee ~/m1-project/evidence/lab03-content-audit.txt
```

统计审计结果共有多少行：

```bash
wc -l ~/m1-project/evidence/lab03-content-audit.txt
```

接着查看项目文件大小，不要立即拼接排序命令：

```bash
find ~/m1-project -maxdepth 2 -type f -printf '%s %p\n'
```

确认第一列是字节数后，按数字倒序并保存：

```bash
find ~/m1-project -maxdepth 2 -type f ! -name 'lab03-file-size-audit.txt' -printf '%s %p\n' | sort -nr | tee ~/m1-project/evidence/lab03-file-size-audit.txt
```

最后验证两份证据均存在且非空：

```bash
test -s ~/m1-project/evidence/lab03-content-audit.txt
```

```bash
test -s ~/m1-project/evidence/lab03-file-size-audit.txt
```

> **验收点**：能指出管道中每一段命令接收什么输入、产生什么输出；两份审计证据来自真实项目文件。

### 任务三：链接实验

#### 步骤7：创建硬链接和软链接

```bash
mkdir -p ~/m1-project/links
```

```bash
ln ~/m1-project/config/app.conf ~/m1-project/links/app.conf.hard
```

```bash
ln -s ../config/app.conf ~/m1-project/links/app.conf.soft
```

```bash
ls -li ~/m1-project/config/app.conf ~/m1-project/links/app.conf.*
```

```bash
readlink ~/m1-project/links/app.conf.soft
```

观察：原文件和硬链接inode编号相同，软链接显示保存的目标路径。

#### 步骤8：验证链接行为

```bash
printf 'link_test=ok\n' >> ~/m1-project/links/app.conf.hard
```

```bash
tail -n 2 ~/m1-project/config/app.conf
```

```bash
cat ~/m1-project/links/app.conf.soft
```

通过硬链接追加内容后，原文件和软链接读取到相同变化，因为它们最终访问同一份数据。

> **验收点**：能根据`ls -li`和文件内容说明两种链接的区别。

### 任务四：归档与恢复

#### 步骤9：创建归档

本实验使用固定归档名，避免后续步骤依赖只存在于旧终端中的变量。先创建归档目录：

```bash
mkdir -p ~/m1-project/backup/archives
```

创建归档：

```bash
tar --exclude='m1-project/backup/archives' -czf ~/m1-project/backup/archives/lab03-m1-project.tar.gz -C ~ m1-project
```

把归档的绝对路径保存到证据文件，保证更换终端后仍能找到同一份归档：

```bash
readlink -f ~/m1-project/backup/archives/lab03-m1-project.tar.gz > ~/m1-project/evidence/lab03-latest-archive.path
```

确认文件非空：

```bash
test -s "$(cat ~/m1-project/evidence/lab03-latest-archive.path)"
```

查看大小：

```bash
ls -lh ~/m1-project/backup/archives/lab03-m1-project.tar.gz
```

查看前30项内容：

```bash
tar -tzf ~/m1-project/backup/archives/lab03-m1-project.tar.gz | sed -n '1,30p'
```

排除归档目录是为了避免把正在创建的归档再次打包进去。

> **验收点**：归档非空，内容列表包含`m1-project/config/app.conf`。

#### 步骤10：恢复到新目录

```bash
test -s ~/m1-project/backup/archives/lab03-m1-project.tar.gz
```

检查恢复目录是否已经存在：

```bash
ls -ld /tmp/lab03-restore
```

首次实验预期提示目录不存在。若目录存在，先确认它确实是上次本实验的恢复目录，再按文末清理步骤删除。确认名称可用后创建目录：

```bash
mkdir /tmp/lab03-restore
```

解包到新目录：

```bash
tar -xzf "$(cat ~/m1-project/evidence/lab03-latest-archive.path)" -C /tmp/lab03-restore
```

查看恢复结果：

```bash
find /tmp/lab03-restore/m1-project -maxdepth 2 -type f -printf '%P\n' | sort
```

比较关键配置：

```bash
cmp ~/m1-project/config/app.conf /tmp/lab03-restore/m1-project/config/app.conf
```

恢复到新目录可以避免覆盖正在使用的数据。

> **验收点**：恢复后的配置与当前配置一致，`cmp`返回0。

#### 步骤11：生成校验值

```bash
sha256sum "$(cat ~/m1-project/evidence/lab03-latest-archive.path)" | tee ~/m1-project/evidence/lab03-archive.sha256
```

校验值可以帮助判断归档文件在复制或保存后是否发生变化，但不能证明业务数据一定满足需求，因此仍需要实际恢复。

> **验收点**：校验文件存在，归档已经完成一次真实恢复。

## 七、独立实践（课后任选一项）

课堂必做任务全部完成后，从下面选择一项巩固，不计入实验基本验收：

1. 使用`find`只列出`~/m1-project`中大于20字节的普通文件。
2. 为`web/index.html`创建一个相对路径软链接，并解释其目标路径。
3. 创建一个只包含`config`和`web`的归档，恢复到新目录后比较两个关键文件。

## 八、验收标准

- [ ] 能使用Vim完成搜索、修改、保存和不保存退出。
- [ ] 配置修改前存在可用备份。
- [ ] 能使用`grep`、`wc`、`sort`和管道生成真实项目审计证据。
- [ ] 能使用`find`按名称、类型、大小和时间查找。
- [ ] 能通过inode和`readlink`区分硬链接与软链接。
- [ ] 归档文件非空且内容列表正确。
- [ ] 已把归档恢复到新目录。
- [ ] 恢复后的关键文件通过内容比较。
- [ ] 已保存归档SHA256；独立实践为课后选做。

## 九、成果提交

1. 修改后的`config/app.conf`。
2. `backup/app.conf.before-vim`。
3. `evidence/lab03-content-audit.txt`和`evidence/lab03-file-size-audit.txt`。
4. 文件查找命令和结果。
5. 归档文件名称、大小和内容列表。
6. `evidence/lab03-archive.sha256`。
7. 恢复目录文件清单及`cmp`验证结果。

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
```

确认输出只属于本实验后再删除：

```bash
rm -r /tmp/lab03-restore
```

