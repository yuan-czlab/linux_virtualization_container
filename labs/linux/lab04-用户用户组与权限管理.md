# 实验4：Linux用户、用户组与权限管理

> 所属模块：模块一 Linux基础运维  
> 建议学时：4学时  
> 实验方式：个人，可两人互相验证  
> 对应教材：《模块一 Linux基础运维》第7—9章  
> 知识前置：实验3及教材第7—9章中的文件、用户和权限概念\
> 状态依赖：`rocky-server`普通管理账号；账号、组和共享目录由本实验创建\
> 建议起点：`Linux-L0`或保留实验3成果的当前环境\
> 项目成果：部门账号、用户组、共享目录、sudo最小授权和跨账号权限验证记录

## 一、项目情境

星云科技需要为开发、运维和审计人员分配Linux账号。开发人员可以协作修改项目文件，审计人员只读，普通人员不得访问，运维人员只能使用获批的管理命令。本实验要求通过真实账号切换验证权限，而不是只查看`ls -l`后判断完成。

## 二、实验目标

### 1. 知识目标

1. 说明UID、GID、主组、附加组、家目录和登录Shell。
2. 解释文件与目录上`rwx`权限含义的差异。
3. 说明所有者、所属组、其他用户、umask和sudo最小授权。

### 2. 能力目标

1. 创建、修改、锁定和检查实验账号与用户组。
2. 使用`chmod`、`chown`和`chgrp`配置权限。
3. 使用SGID和合理umask建立团队共享目录。
4. 使用`visudo`配置并验证命令级sudo授权。
5. 使用不同用户证明允许和拒绝结果符合设计。

### 3. 素质目标

1. 形成一人一账号、最小权限和操作留痕意识。
2. 不使用`chmod 777`掩盖权限设计问题。
3. 修改授权前保留管理员会话和回退方法。

## 三、知识准备

### 1. 用户和组

| 对象 | 常见文件 | 作用 |
|---|---|---|
| 用户基本信息 | `/etc/passwd` | 用户名、UID、主GID、家目录、Shell |
| 密码与过期信息 | `/etc/shadow` | 仅特权用户可读 |
| 用户组 | `/etc/group` | 组名、GID和成员 |

### 2. 文件和目录权限

| 权限 | 普通文件 | 目录 |
|---|---|---|
| `r` | 读取内容 | 列出目录项名称 |
| `w` | 修改内容 | 创建、删除或重命名目录项，通常还需要`x` |
| `x` | 作为程序执行 | 进入目录并访问其中对象 |

权限顺序为所有者、所属组、其他用户。例如`rwxr-x---`表示所有者7、组5、其他0，即`750`。

### 3. sudo

sudo不是共享root密码，而是根据规则授权指定用户执行指定命令，并留下日志。授权文件必须使用`visudo`检查语法。

## 四、实验环境

- Rocky Linux 9，rocky-server具备sudo权限。
- 保留一个rocky-server管理员会话，另开终端完成用户切换测试。
- 实验对象固定为`dev01`、`dev02`、`auditor`、`juniorops`、`project-dev`和`/srv/course-share`。

开始前确认主机身份、sudo能力，并检查是否存在同名旧对象：

```bash
hostnamectl --static
whoami
sudo -v
getent passwd dev01 dev02 auditor juniorops || true
getent group project-dev project-audit || true
sudo test -e /srv/course-share && sudo find /srv/course-share -maxdepth 2 -ls || true
```

主机名和用户名应均为`rocky-server`，`sudo -v`应成功。如果身份或sudo检查失败，停止实验并恢复`Linux-L0`。如果发现同名对象，先判断它们是否为前一次课程实验成果；不要重复创建，也不要直接删除未知账号或目录。

## 五、项目任务

1. 建立项目组和四个岗位账号。
2. 配置共享目录所有权、SGID、Sticky bit和访问权限。
3. 验证开发人员协作、审计人员只读和无关用户拒绝访问。
4. 检查umask对新文件默认权限的影响。
5. 验证共享成员不能删除其他成员拥有的文件。
6. 为初级运维人员授予查询Nginx运行状态的最小sudo权限。
7. 锁定测试账号并保留审计证据。

## 六、实验步骤

### 任务一：建立账号和组

#### 步骤1：检查现有名称

```bash
getent group project-dev || true
for u in dev01 dev02 auditor juniorops; do getent passwd "$u" || true; done
```

若名称已被其他实验占用，先确认来源，不要直接删除未知账号。

#### 步骤2：创建用户组和用户

```bash
sudo groupadd project-dev
sudo useradd -m -s /bin/bash -G project-dev dev01
sudo useradd -m -s /bin/bash -G project-dev dev02
sudo useradd -m -s /bin/bash auditor
sudo useradd -m -s /bin/bash juniorops
```

由教师统一设置实验密码，或使用下面命令逐个交互设置：

```bash
sudo passwd dev01
sudo passwd dev02
sudo passwd auditor
sudo passwd juniorops
```

不要把密码直接写入实验报告或Shell历史。

#### 步骤3：验证身份信息

```bash
getent group project-dev
id dev01
id dev02
id auditor
id juniorops
```

> **验收点**：dev01和dev02的附加组包含project-dev，其他两个账号不属于该组。

### 任务二：配置共享目录

#### 步骤4：创建目录和初始文件

```bash
sudo mkdir -p /srv/course-share
sudo chown root:project-dev /srv/course-share
sudo chmod 2770 /srv/course-share
sudo -u dev01 bash -c 'umask 0002; printf "project=v1\n" > /srv/course-share/project.conf'
ls -ld /srv/course-share
ls -l /srv/course-share/project.conf
```

目录权限前面的`2`设置SGID，使新建文件继承目录所属组`project-dev`。

> **验收点**：目录权限包含`s`，`project.conf`所属组为project-dev。

#### 步骤5：验证开发协作

```bash
sudo -u dev02 cat /srv/course-share/project.conf
sudo -u dev02 bash -c 'printf "updated_by=dev02\n" >> /srv/course-share/project.conf'
sudo -u dev01 tail -n 2 /srv/course-share/project.conf
```

> **验收点**：dev02可以读取并追加，dev01能看到更新。

#### 步骤6：验证无关用户被拒绝

```bash
sudo -u auditor cat /srv/course-share/project.conf
printf 'exit_code=%s\n' "$?"
```

当前应提示Permission denied并返回非0，因为auditor不属于project-dev。

> **验收点**：记录拒绝访问的命令、错误和退出码。

### 任务三：配置审计只读访问

#### 步骤7：创建审计组并授权

仅靠传统所有者/组/其他三组权限，很难同时表达开发可写、审计只读和其他拒绝。本实验使用ACL实现第二类组权限。

确认`setfacl`可用：

```bash
command -v setfacl || sudo dnf install -y acl
```

创建审计组并添加用户：

```bash
sudo groupadd project-audit
sudo usermod -aG project-audit auditor
sudo setfacl -m g:project-audit:rx /srv/course-share
sudo setfacl -m g:project-audit:r-- /srv/course-share/project.conf
getfacl /srv/course-share /srv/course-share/project.conf
```

用户组变化对新的登录会话生效。使用`sudo -u`验证时系统会读取账号组信息。

#### 步骤8：验证只读

```bash
sudo -u auditor cat /srv/course-share/project.conf
sudo -u auditor bash -c 'printf "audit-change\n" >> /srv/course-share/project.conf'
printf 'write_exit_code=%s\n' "$?"
```

读取应成功，写入应失败。

> **验收点**：auditor只读，juniorops仍不能访问共享目录。

### 任务四：观察umask

#### 步骤9：比较不同umask

```bash
sudo -u dev01 bash -c 'umask 0022; touch /srv/course-share/from-0022.txt'
sudo -u dev01 bash -c 'umask 0002; touch /srv/course-share/from-0002.txt'
ls -l /srv/course-share/from-*.txt
```

普通文件的基础权限通常从`666`中屏蔽umask位，因此结果通常分别为`644`和`664`。目录的基础权限通常从`777`计算。

> **验收点**：能够说明为什么团队共享目录更适合组可写的默认权限。

### 任务五：防止成员误删他人文件

共享目录允许组成员创建和修改目录项。只有SGID时，`dev02`也可能删除`dev01`创建的文件。为目录同时增加Sticky bit：

```bash
sudo chmod 3770 /srv/course-share
ls -ld /srv/course-share
sudo -u dev01 touch /srv/course-share/dev01-owned.txt
sudo -u dev02 rm /srv/course-share/dev01-owned.txt
printf 'delete_exit_code=%s\n' "$?"
test -f /srv/course-share/dev01-owned.txt
printf 'file_still_exists=%s\n' "$?"
```

权限数字`3`由SGID的`2`和Sticky bit的`1`组成。`dev02`应能够在目录中协作写入，但不能删除`dev01`拥有的文件；`delete_exit_code`应为非0，`file_still_exists`应为0。

> **验收点**：目录同时显示SGID和Sticky bit，组成员不能删除其他成员拥有的文件。

### 任务六：配置最小sudo授权

#### 步骤10：确认命令绝对路径

```bash
command -v systemctl
```

记录实际路径。Rocky Linux 9通常为`/usr/bin/systemctl`。

#### 步骤11：使用visudo创建规则

```bash
sudo visudo -f /etc/sudoers.d/course-juniorops
```

写入一行；若`systemctl`路径不同，应使用实际路径：

```text
juniorops ALL=(root) NOPASSWD: /usr/bin/systemctl is-active nginx
```

保存后检查：

```bash
sudo visudo -cf /etc/sudoers.d/course-juniorops
sudo chmod 440 /etc/sudoers.d/course-juniorops
sudo -l -U juniorops
```

> **验收点**：语法检查通过，授权列表只包含查询Nginx运行状态的命令。

#### 步骤12：验证允许和拒绝

如果尚未安装Nginx，`is-active nginx`可能输出`unknown`或`inactive`并返回非0；只要没有出现sudo拒绝信息，授权匹配仍可验证。

```bash
sudo -u juniorops sudo /usr/bin/systemctl is-active nginx
sudo -u juniorops sudo /usr/bin/systemctl restart nginx
printf 'restart_exit_code=%s\n' "$?"
```

这里使用`NOPASSWD`只为便于在实验环境中验证这一条精确查询命令，不代表可以对任意命令免密授权。`is-active nginx`应被sudo规则允许，重启命令应被拒绝。没有授权`systemctl status`，也避免免密命令进入交互式分页器。

> **验收点**：提供一条允许证据和一条拒绝证据。

### 任务七：锁定账号和保存证据

#### 步骤13：锁定并检查juniorops

```bash
sudo passwd -l juniorops
sudo passwd -S juniorops
```

锁定密码不会自动终止已登录会话，也不一定阻止所有其他认证方式，因此不能把锁定密码理解为删除账号。

需要继续进行sudo测试时，由教师决定是否解锁：

```bash
sudo passwd -u juniorops
```

#### 步骤14：保存权限证据

```bash
mkdir -p ~/m1-project/evidence
{
    getent group project-dev
    getent group project-audit
    ls -ld /srv/course-share
    ls -l /srv/course-share
    getfacl /srv/course-share /srv/course-share/project.conf
    sudo -l -U juniorops
} > ~/m1-project/evidence/lab04-permissions.txt
```

> **验收点**：证据文件包含用户组、目录、ACL和sudo授权信息。

## 七、独立实践

1. 创建`operator01`账号和`web-ops`用户组。
2. 创建`/srv/web-content`，要求web-ops成员可协作写入，其他用户无权访问。
3. 让`operator01`创建文件后，证明文件所属组符合设计。
4. 为auditor配置该目录的只读ACL。
5. 分别用operator01、auditor和juniorops验证允许与拒绝结果。
6. 不使用`chmod 777`。

## 八、验收标准

- [ ] 四个项目账号和两个项目组符合设计。
- [ ] dev01、dev02能协作写入共享目录。
- [ ] SGID使新文件继承项目组。
- [ ] Sticky bit阻止成员删除其他成员拥有的文件。
- [ ] auditor能够读取但不能写入。
- [ ] juniorops不能访问项目共享目录。
- [ ] 能说明文件和目录上rwx含义的差异。
- [ ] 能解释0022与0002对默认权限的影响。
- [ ] sudoers文件通过`visudo -cf`检查。
- [ ] juniorops只能执行被授权的运行状态查询，不能重启服务。
- [ ] 独立实践和证据文件完整。

## 九、成果提交

1. 账号和用户组清单。
2. `/srv/course-share`权限及ACL输出。
3. 允许和拒绝访问的命令、错误与退出码。
4. sudo最小授权文件内容和语法检查结果。
5. `~/m1-project/evidence/lab04-permissions.txt`。
6. 独立实践结果。

## 十、常见问题

### Q1：用户加入组后，当前终端仍没有权限

新的附加组通常在重新登录后生效。退出该用户会话后重新登录，或使用新的`sudo -u`测试。

### Q2：目录有r权限却无法进入

目录的`x`表示穿越和访问目录内对象。只有`r`通常只能看到名称，不能正常访问文件。

### Q3：共享目录中新文件的组不正确

检查目录SGID和创建进程的组：

```bash
ls -ld /srv/course-share
id <用户>
```

### Q4：sudoers修改后sudo报语法错误

保留原管理员会话，使用`visudo -cf`检查并修复。不要用普通编辑器直接修改`/etc/sudoers`。

### Q5：为什么不能直接chmod 777

777允许所有本地用户读、写和执行，破坏最小权限，也无法表达岗位差异。应通过所有者、组、SGID、umask和ACL解决。

## 十一、课后思考与拓展

1. 删除用户时为什么不能默认删除其家目录和所有文件？
2. sudo的命令参数为什么会影响授权边界？
3. ACL与传统三组权限分别适合什么场景？

## 十二、环境保留与清理

`dev01`、`dev02`、`auditor`、`juniorops`、`project-dev`、`project-audit`和`/srv/course-share`会继续用于模块一教材中的权限、ACL和sudo综合检查。实验4完成后不要立即删除。只有在整门Linux课程结束、或者明确要求重置环境时，才执行以下清理命令：

```bash
sudo rm -f /etc/sudoers.d/course-juniorops
sudo visudo -c
sudo rm -rf /srv/course-share /srv/web-content
for u in dev01 dev02 auditor juniorops operator01; do
    id "$u" >/dev/null 2>&1 && sudo userdel -r "$u"
done
for g in project-dev project-audit web-ops; do
    getent group "$g" >/dev/null && sudo groupdel "$g"
done
```

删除前必须确认这些名称确为本实验创建，不得在共享服务器执行整段清理命令。
