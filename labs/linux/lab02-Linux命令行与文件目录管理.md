# 实验2：Linux命令行、文件与目录管理

> 所属模块：模块一 Linux基础运维  
> 建议学时：4学时  
> 实验方式：个人  
> 对应教材：《模块一 Linux基础运维》第3—4章  
> 知识前置：实验1中的Linux登录、终端和三机角色
> 状态依赖：实验1交付的`rocky-server`，普通账号及sudo可用
> 建议起点：`Linux-L0`
> 项目成果：规范的企业运维项目目录，以及文件整理和验证记录

## 一、项目情境

**星云科技**准备在新服务器上**部署内部应用**。开发人员交付了一批配置、网页、日志和备份文件，但文件尚未按Linux服务器规范整理。你需要使用命令行建立工作区，完成目录创建、文件查看、复制、移动、重命名和安全删除，为后续服务部署做好准备。

## 二、实验目标

### 1. 知识目标

1. 说明终端、Shell、命令、选项、参数和退出码的关系。
2. 区分绝对路径、相对路径、当前目录、上级目录和用户家目录。
3. 说明Linux单根目录树及主要系统目录的用途。
4. 说明通配符和输出重定向由Shell处理的基本机制。

### 2. 能力目标

1. 使用帮助、补全和历史功能查询命令用法。
2. 使用`pwd`、`cd`和`ls`完成目录导航。
3. 使用`mkdir`、`touch`、`cp`、`mv`和`rm`管理文件与目录。
4. 使用`cat`、`less`、`head`、`tail`和`wc`查看文本。
5. 使用通配符和重定向完成批量文件整理。

### 3. 素质目标

1. 形成执行命令前确认当前用户、工作目录和目标对象的习惯。
2. 形成删除前检查匹配结果、操作后验证结果的安全意识。
3. 养成按用途组织项目文件和保存操作证据的职业习惯。

## 三、知识准备

### 1. 命令执行过程

```text
终端接收输入
→ Shell解析命令、选项和参数
→ 执行内置命令或外部程序
→ 程序访问Linux资源
→ 输出结果或错误
→ 返回退出码
```

典型命令结构：

```text
命令 选项 参数
ls   -lh  /var/log
```

命令没有输出不代表一定成功。执行命令后可以查看退出码：

```bash
echo $?
```

`0`通常表示成功，非0表示错误或条件不满足。

### 2. Linux目录树

| 目录 | 主要用途 |
|---|---|
| `/etc` | 系统和服务配置 |
| `/var` | 日志、缓存、数据库等经常变化的数据 |
| `/home` | 普通用户家目录 |
| `/root` | root用户家目录 |
| `/usr` | 程序、库和共享数据 |
| `/opt` | 可选或第三方软件 |
| `/srv` | 服务对外提供的数据 |
| `/tmp` | 临时文件 |
| `/proc` | 内核和进程的虚拟视图，不是普通磁盘目录 |

### 3. 路径和通配符

| 写法 | 含义 |
|---|---|
| `/` | 根目录，绝对路径起点 |
| `.` | 当前目录 |
| `..` | 上一级目录 |
| `~` | 当前用户家目录 |
| `*` | 任意长度的任意字符 |
| `?` | 任意一个字符 |
| `[0-9]` | 指定范围中的一个字符 |

Shell会先展开通配符，再把匹配结果交给命令。删除前必须先检查匹配范围。

开始任务前打开[Linux目录树、路径与链接动画](../../animations/02-linux-filesystem-paths-links/index.html)，完成“目录树与/bin”和“绝对/相对路径”两个主题。动画用于预测路径解析结果，随后必须在`rocky-server`中用真实命令验证。

## 四、实验环境

- 使用实验1保留的Rocky Linux 9虚拟机。
- 使用`rocky-server`普通用户登录。
- 所有可删除内容限制在`~/m1-project`和`/tmp/lab02-*`。

开始前逐条执行，不要把下面的检查复制成一段脚本。

确认当前用户：

```bash
whoami
```

确认主机：

```bash
hostname
```

确认当前位置：

```bash
pwd
```

确认家目录所在文件系统有可用空间：

```bash
df -h ~
```

检查项目目录是否已经存在：

```bash
ls -ld ~/m1-project
```

第一次实验时，最后一条命令应提示目录不存在。若目录已经存在，先执行下面的命令确认来源：

```bash
find ~/m1-project -maxdepth 2 -print
```

它若是已经验收的实验2成果，应保留并直接进入后续实验；若要从头重做，应恢复`Linux-L0`。不要让旧文件混入本次结果，也不要直接删除来源不明的目录。

> **验收点**：当前用户为rocky-server，家目录可写，磁盘空间满足实验需要，项目目录没有混入旧文件。

## 五、项目任务

1. 认识命令格式、帮助、历史和补全。
2. 调查Linux主要目录。
3. 创建企业运维项目目录。
4. 创建并查看配置、网页和日志文件。
5. 完成复制、移动、重命名和批量整理。
6. 在确认目标后安全删除临时文件。
7. 生成项目文件清单和操作记录。

## 六、实验步骤

### 任务一：熟悉Shell和帮助系统

#### 步骤1：识别当前Shell和命令类型

逐条执行并比较输出。先查看当前Shell：

```bash
echo "$SHELL"
```

判断`cd`属于哪类命令：

```bash
type cd
```

判断`ls`属于哪类命令：

```bash
type ls
```

判断`cp`属于哪类命令：

```bash
type cp
```

查找`ls`最终执行位置：

```bash
command -v ls
```

`cd`通常是Shell内置命令，`cp`和`ls`通常是外部程序。`command -v`用于查找将被执行的命令。

> **验收点**：能够指出`cd`与`cp`在命令类型上的区别。

#### 步骤2：使用帮助、补全和历史

先查看`ls`内置帮助。内容较长时可滚动终端：

```bash
ls --help
```

再打开手册页：

```bash
man ls
```

查看近期历史命令：

```bash
history
```

在`man`中按`/`搜索，按`n`查看下一个结果，按`q`退出。输入命令或路径的一部分后按Tab，可以减少拼写错误。

故意执行一个不存在的命令，再查看退出码：

```bash
command-does-not-exist
```

再单独查看上一条命令的退出码：

```bash
echo $?
```

> **验收点**：能够使用`man`退出，能够看到失败命令返回非0退出码。

### 任务二：认识目录和路径

#### 步骤3：查看当前目录和主要目录

先查看当前位置：

```bash
pwd
```

观察根目录及常用系统目录：

```bash
ls -ld / /etc /var /home /usr /opt /srv /tmp /proc
```

观察自己的家目录：

```bash
ls -lah ~
```

切换并观察路径：

```bash
cd /var/log
```

```bash
pwd
```

```bash
cd ..
```

```bash
pwd
```

```bash
cd ~
```

```bash
pwd
```

```bash
cd -
```

```bash
pwd
```

最后回到家目录：

```bash
cd ~
```

> **验收点**：能分别使用绝对路径和相对路径回到家目录。

### 任务三：建立项目工作区

#### 步骤4：创建目录树

先创建项目根目录：

```bash
mkdir -p ~/m1-project
```

进入项目目录：

```bash
cd ~/m1-project
```

确认当前位置：

```bash
pwd
```

逐个创建子目录：

```bash
mkdir config
```

```bash
mkdir web
```

```bash
mkdir logs
```

```bash
mkdir scripts
```

```bash
mkdir backup
```

```bash
mkdir evidence
```

最后检查一级目录：

```bash
find . -maxdepth 1 -type d -print
```

`-p`可以创建缺失的父目录。`scripts`暂时为空，到“Shell服务器巡检”章节再创建脚本。

预期包含：

```text
m1-project
├── backup
├── config
├── evidence
├── logs
├── scripts
└── web
```

> **验收点**：六个子目录全部存在，没有拼写错误和多余层级。

#### 步骤5：创建项目文件

本步骤仍在`~/m1-project`中执行。先创建空配置文件：

```bash
touch config/app.conf
```

写入第一行配置。`>`会覆盖文件原内容：

```bash
echo 'server_name=training.local' > config/app.conf
```

追加第二行。`>>`会在文件末尾追加：

```bash
echo 'port=8080' >> config/app.conf
```

追加第三行：

```bash
echo 'mode=development' >> config/app.conf
```

创建网页文件：

```bash
echo '<h1>Linux Course Project</h1>' > web/index.html
```

创建部署日志：

```bash
date > logs/deploy.log
```

逐项验证：

```bash
cat config/app.conf
```

```bash
wc -l config/app.conf
```

```bash
find . -maxdepth 2 -type f -print
```

> **验收点**：存在配置、网页和日志3个项目文件，`app.conf`包含3行配置。

### 任务四：查看文本内容

#### 步骤6：使用不同工具查看文件

先完整查看短配置文件：

```bash
cat ~/m1-project/config/app.conf
```

只查看开头两行：

```bash
head -n 2 ~/m1-project/config/app.conf
```

只查看末尾两行：

```bash
tail -n 2 ~/m1-project/config/app.conf
```

统计行数、单词数和字节数：

```bash
wc -l -w -c ~/m1-project/config/app.conf
```

使用分页方式查看日志：

```bash
less ~/m1-project/logs/deploy.log
```

`cat`适合短文件，`less`适合分页查看较长文件，`head`和`tail`用于查看开头和结尾。

`less`进入分页界面后按`q`返回Shell，再继续后续步骤。

> **验收点**：能说明五个查看命令分别适合什么场景。

#### 步骤7：练习追加和覆盖重定向

追加当前时间：

```bash
date >> ~/m1-project/logs/deploy.log
```

追加部署状态：

```bash
echo 'deployment=ready' >> ~/m1-project/logs/deploy.log
```

查看追加结果：

```bash
cat ~/m1-project/logs/deploy.log
```

`>`会覆盖原内容，`>>`会在文件末尾追加。对配置和日志操作时必须区分二者。

> **验收点**：`deploy.log`保留第一次日期，并新增第二次日期和状态行。

### 任务五：复制、移动和重命名

#### 步骤8：备份配置文件

复制配置并尽量保留原属性：

```bash
cp -p ~/m1-project/config/app.conf ~/m1-project/backup/app.conf.bak
```

观察源文件和备份：

```bash
ls -l ~/m1-project/config/app.conf ~/m1-project/backup/app.conf.bak
```

比较两个文件内容：

```bash
cmp ~/m1-project/config/app.conf ~/m1-project/backup/app.conf.bak
```

`cmp`内容相同时通常没有输出。继续检查退出码：

```bash
echo $?
```

`-p`尽量保留时间和权限等属性。`cmp`没有输出且退出码为0，说明两个文件内容一致。

> **验收点**：备份文件存在，`cmp`返回0。

#### 步骤9：移动和重命名

先重命名日志：

```bash
mv ~/m1-project/logs/deploy.log ~/m1-project/logs/deploy-history.log
```

确认新文件存在：

```bash
ls -l ~/m1-project/logs/deploy-history.log
```

把网页复制到临时目录：

```bash
cp ~/m1-project/web/index.html /tmp/lab02-index.html
```

再把临时副本移动到项目备份目录并重命名：

```bash
mv /tmp/lab02-index.html ~/m1-project/backup/index.html.copy
```

查看当前项目文件：

```bash
find ~/m1-project -maxdepth 2 -type f -print
```

同一文件系统中，`mv`既可以移动文件，也可以修改文件名。

> **验收点**：原`deploy.log`不再存在，新文件和网页副本位于正确目录。

### 任务六：批量整理和安全删除

#### 步骤10：创建并筛选测试文件

先确认本实验临时名称未被占用：

```bash
ls -ld /tmp/lab02-sort
```

第一次实验时应提示目录不存在。若它是上次未完成的实验残留，先核对内容，再按本实验末尾的清理步骤处理。

创建临时目录：

```bash
mkdir -p /tmp/lab02-sort
```

逐个创建测试文件：

```bash
touch /tmp/lab02-sort/app1.log
```

```bash
touch /tmp/lab02-sort/app2.log
```

```bash
touch /tmp/lab02-sort/app3.log
```

```bash
touch /tmp/lab02-sort/config1.bak
```

```bash
touch /tmp/lab02-sort/config2.bak
```

```bash
touch /tmp/lab02-sort/readme.txt
```

先观察`*`匹配范围：

```bash
ls -l /tmp/lab02-sort/*
```

再观察`?`匹配范围：

```bash
ls -l /tmp/lab02-sort/app?.log
```

最后观察扩展名匹配：

```bash
ls -l /tmp/lab02-sort/*.bak
```

观察`*`、`?`和扩展名匹配范围。

#### 步骤11：确认后删除指定文件

先检查将要删除的对象：

```bash
printf '%s\n' /tmp/lab02-sort/*.bak
```

确认只匹配两个`.bak`文件后执行：

```bash
rm /tmp/lab02-sort/*.bak
```

删除后检查剩余文件：

```bash
find /tmp/lab02-sort -maxdepth 1 -type f -print
```

不要把未经验证的变量、路径或通配符与`rm -rf`组合使用。

> **验收点**：两个`.bak`文件被删除，三个日志和`readme.txt`仍然存在。

### 任务七：生成项目清单

#### 步骤12：保存文件清单和关键内容

先保存文件清单：

```bash
find ~/m1-project -maxdepth 2 -print > ~/m1-project/evidence/file-list.txt
```

把当前用户写入摘要文件：

```bash
whoami > ~/m1-project/evidence/lab02-summary.txt
```

追加主机名：

```bash
hostname >> ~/m1-project/evidence/lab02-summary.txt
```

追加当前目录：

```bash
pwd >> ~/m1-project/evidence/lab02-summary.txt
```

追加当前时间：

```bash
date >> ~/m1-project/evidence/lab02-summary.txt
```

分别查看两个证据文件：

```bash
cat ~/m1-project/evidence/file-list.txt
```

```bash
cat ~/m1-project/evidence/lab02-summary.txt
```

> **验收点**：两个证据文件不为空，文件清单包含项目目录和已创建文件。

## 七、独立实践

不照抄上面的目录名，独立完成：

1. 在`~/m1-project`中创建`docs`和`packages`目录。
2. 创建`docs/deploy-guide.md`，写入不少于3行部署说明。
3. 创建`packages/app-v1.tar`和`packages/app-v2.tar`两个空文件。
4. 把`app-v1.tar`复制到`backup`并改名为`app-current.tar`。
5. 只使用一条查看命令显示`deploy-guide.md`的前2行。
6. 用命令证明源文件和备份副本内容一致。
7. 把最终文件列表追加到`evidence/file-list.txt`。

## 八、验收标准

- [ ] 能使用`man`、`--help`、Tab和`history`查询或复用命令。
- [ ] 能解释绝对路径和相对路径。
- [ ] 能说明`/etc`、`/var`、`/home`、`/srv`和`/tmp`的主要用途。
- [ ] `~/m1-project`目录结构完整且用途清楚。
- [ ] 配置、网页、日志和备份文件位于正确目录，`scripts`目录已为后续课程保留。
- [ ] 能根据文件长度选择`cat`、`less`、`head`或`tail`。
- [ ] 能区分`>`覆盖和`>>`追加。
- [ ] 配置备份通过`cmp`验证。
- [ ] 能在删除前检查通配符匹配结果。
- [ ] 独立实践全部完成。
- [ ] `file-list.txt`和`lab02-summary.txt`存在且不为空。

## 九、成果提交

提交：

1. `~/m1-project`完整目录。
2. `evidence/file-list.txt`。
3. `evidence/lab02-summary.txt`。
4. 独立实践的命令记录和验证结果。
5. 一段不超过200字的安全操作总结：删除文件前应检查哪些内容。

## 十、常见问题

### Q1：执行命令后提示No such file or directory

先检查当前目录和目标路径：

```bash
pwd
```

再检查相关路径：

```bash
ls -ld ~/m1-project ~/m1-project/backup
```

注意Linux路径和文件名区分大小写。

### Q2：提示Permission denied

先用`whoami`确认用户，再用`ls -ld`查看目录权限。本实验工作区位于rocky-server家目录，通常不需要sudo。不要为了消除错误直接使用`chmod 777`。

### Q3：复制目录时提示omitting directory

`cp`默认只复制文件。复制目录时使用：

```bash
cp -a ~/m1-project/config ~/m1-project/backup/config-copy
```

复制后再检查：

```bash
find ~/m1-project/backup/config-copy -maxdepth 2 -type f -print
```

`-a`适合保留目录结构和属性。

### Q4：文件被`>`清空了怎么办

`>`会先截断目标文件再写入。重要文件修改前应先复制备份。本实验可从`backup/app.conf.bak`恢复配置。

### Q5：为什么不允许随意使用rm -rf

`-r`递归处理目录，`-f`跳过大部分确认。路径、变量或通配符错误时会扩大破坏范围。先在明确的实验目录中用`printf`、`find`或`ls`确认目标。

## 十一、课后思考与拓展

1. 为什么Linux把配置、日志和用户数据放在不同目录？
2. 为什么运维工作中复制完成后还需要比较内容或校验值？
3. 如果文件名中包含空格，Shell命令需要如何保护这个路径？

## 十二、环境保留与清理

保留`~/m1-project`，后续实验继续使用。

清理本实验临时目录前先确认路径：

```bash
find /tmp/lab02-sort -maxdepth 1 -print
```

确认输出只属于本实验后再删除：

```bash
rm -r /tmp/lab02-sort
```

不要删除`~/m1-project`和实验1创建的虚拟机快照。

