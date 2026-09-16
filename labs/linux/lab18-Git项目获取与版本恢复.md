# 实验18：Git项目获取与版本恢复

> 所属模块：模块三 企业服务器部署与综合运维
> 建议学时：2学时
> 实验方式：个人
> 对应教材：3.5 Git与运维版本管理
> 知识前置：已学习教材3.5，能够使用vim创建文本文件，理解工作区、暂存区和提交
> 状态依赖：`rocky-server`和可用课程软件源；不依赖实验17的Redis数据
> 建议起点：`Linux-L2`或当前连续实验环境
> 项目成果：运维工作仓库、裸仓库、协作副本、三次有效提交、稳定标签和版本恢复证据

## 一、项目情境

TechCorp已经部署Nginx、MySQL、MongoDB和Redis。配置经过多次修改后，仅靠“最终版”“最终版2”等文件名无法说明哪个版本通过验收，也不能可靠恢复误改。

你需要为团队建立一个Linux运维资料仓库，保存以下内容：

- 服务端口与开放策略；
- 脱敏后的Nginx配置模板；
- 运维交接检查表；
- 后续实验要加入的服务器巡检脚本。

同时必须确保密码、私钥、日志、数据库转储和运行数据不进入Git。实验使用同机裸仓库模拟团队远程仓库，不依赖互联网账号。

## 二、实验目标

### 1. 知识目标

1. 说明工作区、暂存区、本地仓库和远程仓库的关系。
2. 说明普通仓库与裸仓库的区别。
3. 区分`git diff`与`git diff --cached`。
4. 说明`.gitignore`的作用与边界。
5. 根据文件状态选择恢复方法。

### 2. 能力目标

1. 初始化以`main`为默认分支的仓库并配置本地身份。
2. 精确暂存文件，审查差异并形成小步提交。
3. 创建裸仓库，完成推送、克隆和快进拉取。
4. 恢复未暂存误改、误暂存和误删文件。
5. 形成可由实验19和实验20继续使用的仓库。

### 3. 安全与规范目标

1. 不使用`git add .`盲目暂存整个运维目录。
2. 不提交密码、令牌、私钥、日志或数据库备份。
3. 恢复前先查看状态和差异。
4. 不使用`git reset --hard`处理本实验的普通误改。
5. 不把同机裸仓库误认为异机备份。

## 三、最终目录规划

实验完成后应形成：

```text
~/m1-project/
├── git-lab/                         # 主工作仓库
│   ├── .git/
│   ├── .gitignore
│   ├── README.md
│   ├── docs/
│   │   ├── handover.md
│   │   └── service-map.md
│   ├── templates/
│   │   └── techcorp.conf.example
│   └── scripts/                     # 实验19继续使用
├── git-server/
│   └── techcorp.git/                # 模拟团队中心的裸仓库
├── git-review/                      # 模拟另一名管理员的副本
└── evidence/
    └── lab18-git-*.txt
```

所有目录和文件都会在下面明确创建。不得假设`README.md`、`docs`或模板已经存在。

## 四、任务一：检查环境并安装Git

### 步骤1：确认主机

```bash
hostnamectl --static
```

预期为`rocky-server`。如果不是，切换到正确虚拟机。

### 步骤2：确认项目根目录

```bash
ls -ld ~/m1-project
```

如果不存在，创建它：

```bash
mkdir -p ~/m1-project
```

### 步骤3：创建证据目录

```bash
mkdir -p ~/m1-project/evidence
```

### 步骤4：安装Git

```bash
sudo dnf install -y git
```

### 步骤5：查看版本

```bash
git --version
```

### 步骤6：检查本次实验路径

```bash
ls -ld ~/m1-project/git-lab ~/m1-project/git-server ~/m1-project/git-review
```

首次实验时，三个路径都不存在是正常结果。如果其中任何路径已经存在，先执行`git status`或查看目录内容，确认是否是之前的实验成果。不要直接删除、覆盖或重新初始化。

## 五、任务二：创建主工作仓库

### 步骤1：创建工作目录

```bash
mkdir ~/m1-project/git-lab
```

如果命令提示目录已经存在，应返回上一步检查，不要加`-f`或改用删除命令。

### 步骤2：进入工作目录

```bash
cd ~/m1-project/git-lab
```

### 步骤3：初始化main分支

```bash
git init --initial-branch=main
```

预期提示已经初始化空Git仓库。

### 步骤4：查看隐藏目录

```bash
ls -la
```

应看到`.git`。不要手工修改其中内容。

### 步骤5：配置当前仓库作者姓名

```bash
git config --local user.name "Student Ops"
```

### 步骤6：配置当前仓库作者邮箱

```bash
git config --local user.email "student@example.test"
```

### 步骤7：查看配置来源

```bash
git config --list --show-origin
```

应看到姓名和邮箱来自当前仓库的`.git/config`，而不是要求修改全局配置。

### 步骤8：确认当前分支

```bash
git branch --show-current
```

预期返回`main`。

## 六、任务三：建立仓库内容与忽略规则

### 步骤1：创建文档目录

```bash
mkdir docs
```

### 步骤2：创建模板目录

```bash
mkdir templates
```

### 步骤3：创建脚本目录

```bash
mkdir scripts
```

空目录不会被Git单独跟踪。`scripts`会在实验19加入巡检脚本。

### 步骤4：编写仓库说明

```bash
vim README.md
```

逐行输入：

```markdown
# TechCorp Linux运维资料

本仓库保存经过脱敏的配置模板、巡检脚本和运维文档。

禁止提交密码、令牌、私钥、数据库转储和运行日志。
任何配置变更都应在提交前检查差异，并在提交后完成验证。
```

保存退出后查看：

```bash
sed -n '1,40p' README.md
```

### 步骤5：编写服务清单

```bash
vim docs/service-map.md
```

逐行输入：

```markdown
# TechCorp服务清单

| 服务 | 主机 | 端口 | 开放策略 |
|---|---|---:|---|
| SSH | 三台虚拟机 | 22 | 仅课程管理网络 |
| Nginx | rocky-web | 80 | 向ubuntu-client提供Web访问 |
| MySQL | rocky-server | 3306 | 仅指定客户端或本机 |
| MongoDB | rocky-server | 27017 | 仅本机 |
| Redis | rocky-server | 6379 | 仅本机 |
```

保存后检查：

```bash
sed -n '1,40p' docs/service-map.md
```

### 步骤6：编写忽略规则

```bash
vim .gitignore
```

逐行输入：

```gitignore
# 密码、令牌与私钥
.env
*.key
*.pem
secrets/

# 日志、数据库转储和运行数据
*.log
*.sql
*.bson
*.rdb
*.aof
runtime/
backup/
evidence/

# 编辑器临时文件
*~
*.swp
```

保存后检查：

```bash
sed -n '1,80p' .gitignore
```

## 七、任务四：验证忽略规则

本任务创建的是无真实秘密的测试文件，仅用于证明规则有效。

### 步骤1：创建测试运行目录

```bash
mkdir runtime
```

### 步骤2：创建测试秘密目录

```bash
mkdir secrets
```

### 步骤3：创建环境文件样例

```bash
printf 'DEMO_VALUE=not-a-real-secret\n' > .env
```

### 步骤4：创建日志样例

```bash
printf 'temporary test log\n' > runtime/app.log
```

### 步骤5：创建私钥文件名样例

```bash
printf 'ignore-rule-test-only\n' > secrets/server.key
```

### 步骤6：查看包含忽略项的状态

```bash
git status --short --ignored
```

预期：

- `README.md`、`.gitignore`和`docs/`显示为未跟踪；
- `.env`、`runtime/`和`secrets/`以`!!`显示为已忽略；
- 不应看到任何真实密码或私钥。

### 步骤7：查明.env由哪条规则忽略

```bash
git check-ignore -v .env
```

### 步骤8：确认.env尚未被跟踪

```bash
git ls-files -- .env
```

没有输出是预期结果。

## 八、任务五：形成第一次提交

### 步骤1：再次查看状态

```bash
git status --short
```

### 步骤2：精确暂存仓库说明

```bash
git add README.md
```

### 步骤3：精确暂存服务清单

```bash
git add docs/service-map.md
```

### 步骤4：精确暂存忽略规则

```bash
git add .gitignore
```

### 步骤5：观察暂存状态

```bash
git status --short
```

左列应显示`A`，表示三个文件已加入暂存区。

### 步骤6：审查即将提交的内容

```bash
git diff --cached
```

逐行确认没有密码、私钥、日志和数据库转储。

### 步骤7：形成提交

```bash
git commit -m "docs: initialize operations repository"
```

### 步骤8：查看提交

```bash
git log --oneline --decorate -n 3
```

### 步骤9：确认实际跟踪文件

```bash
git ls-files
```

预期只有`.gitignore`、`README.md`和`docs/service-map.md`。

## 九、任务六：增加脱敏Nginx模板

### 步骤1：创建模板文件

```bash
vim templates/techcorp.conf.example
```

逐行输入：

```nginx
server {
    listen 80;
    server_name techcorp.test;
    root /srv/techcorp/www;
    index index.html;

    location /health {
        default_type text/plain;
        return 200 "ok\n";
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

这是供审查和部署参考的脱敏模板，不包含数据库密码，也不直接覆盖`/etc/nginx`中的运行配置。

### 步骤2：查看工作区变化

```bash
git status --short
```

### 步骤3：暂存模板

```bash
git add templates/techcorp.conf.example
```

### 步骤4：审查暂存差异

```bash
git diff --cached
```

### 步骤5：形成第二次提交

```bash
git commit -m "feat: add sanitized nginx template"
```

### 步骤6：查看图形化历史

```bash
git log --oneline --decorate --graph --all
```

### 步骤7：标记已验收基线

```bash
git tag -a linux-lab18-v1 -m "Lab 18 verified baseline"
```

### 步骤8：查看标签

```bash
git tag
```

## 十、任务七：创建团队裸仓库并推送

创建裸仓库时直接指定`main`，避免裸仓库的`HEAD`错误指向没有创建的`master`分支。

### 步骤1：创建父目录

```bash
mkdir ~/m1-project/git-server
```

### 步骤2：创建裸仓库

```bash
git init --bare --initial-branch=main ~/m1-project/git-server/techcorp.git
```

### 步骤3：回到主工作仓库

```bash
cd ~/m1-project/git-lab
```

### 步骤4：添加远程

```bash
git remote add origin ~/m1-project/git-server/techcorp.git
```

### 步骤5：检查远程

```bash
git remote -v
```

### 步骤6：首次推送main

```bash
git push -u origin main
```

### 步骤7：推送标签

```bash
git push origin linux-lab18-v1
```

### 步骤8：检查远程引用

```bash
git ls-remote --heads --tags origin
```

应看到`refs/heads/main`和`refs/tags/linux-lab18-v1`。

## 十一、任务八：模拟另一名管理员协作

### 步骤1：回到项目根目录

```bash
cd ~/m1-project
```

### 步骤2：克隆团队仓库

```bash
git clone ~/m1-project/git-server/techcorp.git git-review
```

克隆后不应出现“remote HEAD refers to nonexistent ref”。如果出现该提示，说明裸仓库的初始分支设置不正确，应停止并检查任务七，而不是在空工作区继续提交。

### 步骤3：进入协作副本

```bash
cd ~/m1-project/git-review
```

### 步骤4：确认分支

```bash
git branch --show-current
```

预期为`main`。

### 步骤5：配置模拟审核员姓名

```bash
git config --local user.name "Reviewer Ops"
```

### 步骤6：配置模拟审核员邮箱

```bash
git config --local user.email "reviewer@example.test"
```

### 步骤7：创建交接文档

```bash
vim docs/handover.md
```

逐行输入：

```markdown
# 运维交接检查

1. 先确认主机身份、IP地址和时间。
2. 检查服务状态、监听端口和防火墙。
3. 检查配置语法和journal日志。
4. 修改前备份，修改后验证。
5. 提交前确认没有密码、私钥和运行数据。
6. 备份必须通过恢复验证。
```

### 步骤8：查看未跟踪文件

```bash
git status --short
```

### 步骤9：精确暂存交接文档

```bash
git add docs/handover.md
```

### 步骤10：审查暂存内容

```bash
git diff --cached
```

### 步骤11：形成第三次提交

```bash
git commit -m "docs: add operations handover checklist"
```

### 步骤12：推送审核员提交

```bash
git push origin main
```

## 十二、任务九：在主仓库获取协作变化

### 步骤1：回到主工作仓库

```bash
cd ~/m1-project/git-lab
```

### 步骤2：确认工作区干净

```bash
git status --short --branch
```

拉取前不能有未处理的本地修改。

### 步骤3：只允许快进拉取

```bash
git pull --ff-only
```

### 步骤4：查看协作历史

```bash
git log --oneline --decorate --graph --all -n 6
```

应看到作者为`Reviewer Ops`的交接文档提交。

### 步骤5：确认文件已到达

```bash
test -f docs/handover.md
```

没有输出且返回码为0表示文件存在。

### 步骤6：查看交接内容

```bash
sed -n '1,40p' docs/handover.md
```

## 十三、任务十：恢复未暂存的误改

被修改的`docs/service-map.md`已经在任务五创建并提交，因此本任务不会引用不存在的文件。

### 步骤1：加入一条故意错误的策略

```bash
printf '\n错误策略：所有数据库端口对互联网开放。\n' >> docs/service-map.md
```

### 步骤2：查看状态

```bash
git status --short
```

预期看到` M docs/service-map.md`。

### 步骤3：查看差异

```bash
git diff -- docs/service-map.md
```

确认新增策略违反本项目安全边界。

### 步骤4：恢复工作区文件

```bash
git restore docs/service-map.md
```

### 步骤5：确认错误内容消失

```bash
grep '所有数据库端口' docs/service-map.md
```

没有输出是预期结果。

### 步骤6：确认状态恢复

```bash
git status --short
```

## 十四、任务十一：撤销误暂存

### 步骤1：加入一条待检查的变化

```bash
printf '\n临时内容：尚未完成审核。\n' >> docs/handover.md
```

### 步骤2：将修改加入暂存区

```bash
git add docs/handover.md
```

### 步骤3：查看短状态

```bash
git status --short
```

预期左列出现`M`，说明变化已经暂存。

### 步骤4：查看已暂存差异

```bash
git diff --cached -- docs/handover.md
```

### 步骤5：撤销暂存

```bash
git restore --staged docs/handover.md
```

### 步骤6：再次查看状态

```bash
git status --short
```

此时`M`应位于右列，说明修改仍在工作区，只是退出了暂存区。

### 步骤7：查看仍然存在的工作区差异

```bash
git diff -- docs/handover.md
```

### 步骤8：确认不需要后恢复工作区

```bash
git restore docs/handover.md
```

### 步骤9：确认仓库恢复干净

```bash
git status --short
```

## 十五、任务十二：恢复误删文件

被删除的模板已经在任务六创建并提交，可以通过Git恢复。

### 步骤1：删除实验模板

```bash
rm templates/techcorp.conf.example
```

此命令只删除实验仓库中的已提交模板，不得替换为其他系统路径。

### 步骤2：查看删除状态

```bash
git status --short
```

### 步骤3：查看删除差异

```bash
git diff -- templates/techcorp.conf.example
```

### 步骤4：恢复模板

```bash
git restore templates/techcorp.conf.example
```

### 步骤5：确认模板存在

```bash
test -f templates/techcorp.conf.example
```

### 步骤6：查看模板开头

```bash
sed -n '1,20p' templates/techcorp.conf.example
```

### 步骤7：确认仓库干净

```bash
git status --short
```

## 十六、任务十三：读取并恢复指定版本

本任务不回退整个仓库，只比较和恢复单个文件。

### 步骤1：查看标签版本中的README

```bash
git show linux-lab18-v1:README.md
```

### 步骤2：比较当前README与标签版本

```bash
git diff linux-lab18-v1 -- README.md
```

如果没有输出，说明当前README与标签中的内容相同。

### 步骤3：模拟修改README

```bash
printf '\n临时错误说明。\n' >> README.md
```

### 步骤4：查看当前差异

```bash
git diff -- README.md
```

### 步骤5：从标签恢复单个文件

```bash
git restore --source=linux-lab18-v1 -- README.md
```

### 步骤6：确认恢复结果

```bash
git diff -- README.md
```

没有输出是预期结果。`docs/handover.md`仍然保留，因为只恢复了README，没有回退整个仓库。

## 十七、任务十四：形成验收证据

所有证据写入仓库外部的`~/m1-project/evidence`，避免运行证据进入版本库。

### 步骤1：保存分支状态

```bash
git status --short --branch > ~/m1-project/evidence/lab18-git-status.txt
```

### 步骤2：保存远程信息

```bash
git remote -v > ~/m1-project/evidence/lab18-git-remotes.txt
```

### 步骤3：保存提交历史

```bash
git log --oneline --decorate --graph --all -n 10 > ~/m1-project/evidence/lab18-git-history.txt
```

### 步骤4：保存已跟踪文件清单

```bash
git ls-files > ~/m1-project/evidence/lab18-git-tracked.txt
```

### 步骤5：保存忽略规则证明

```bash
git check-ignore -v .env runtime/app.log secrets/server.key > ~/m1-project/evidence/lab18-git-ignored.txt
```

### 步骤6：检查证据文件

```bash
ls -l ~/m1-project/evidence/lab18-git-*.txt
```

### 步骤7：确认仓库中没有跟踪.env

```bash
git ls-files -- .env
```

没有输出是预期结果。

### 步骤8：确认仓库最终干净

```bash
git status --short
```

没有输出表示已跟踪文件没有未提交变化。已忽略的测试文件仍可存在，但不会进入提交。

## 十八、实验验收

### 1. 仓库与历史

- [ ] 主仓库为`~/m1-project/git-lab`，当前分支为`main`。
- [ ] 本地作者为`Student Ops`，协作副本作者为`Reviewer Ops`。
- [ ] 历史中至少有三次目的明确的提交。
- [ ] 标签`linux-lab18-v1`存在。
- [ ] 主仓库最终没有未提交的已跟踪变化。

### 2. 安全边界

- [ ] `.env`、`*.key`、日志和数据库转储规则已经配置。
- [ ] `.env`、测试日志和测试key没有进入跟踪清单。
- [ ] 没有真实密码、令牌或私钥进入仓库和截图。
- [ ] 能说明`.gitignore`不能清除已经提交的秘密。

### 3. 协作流程

- [ ] 裸仓库的默认分支正确指向`main`。
- [ ] `main`和标签已经推送。
- [ ] `git-review`克隆后直接得到正常工作区。
- [ ] 协作副本的提交能够推送，主仓库能以`--ff-only`拉取。

### 4. 恢复能力

- [ ] 能恢复未暂存的误改。
- [ ] 能撤销误暂存并说明工作区修改仍然存在。
- [ ] 能恢复误删的已跟踪模板。
- [ ] 能从标签读取并恢复单个文件。
- [ ] 每次恢复前都查看了状态或差异。

## 十九、提交材料

1. `lab18-git-status.txt`；
2. `lab18-git-remotes.txt`；
3. `lab18-git-history.txt`；
4. `lab18-git-tracked.txt`；
5. `lab18-git-ignored.txt`；
6. 三种恢复场景的操作记录或不含秘密的截图；
7. 150—300字说明：Git适合保存哪些运维资产，为什么同机裸仓库不能替代备份。

## 二十、常见问题与排查

### 1. `git commit`提示Please tell me who you are

检查当前仓库身份：

```bash
git config --local user.name
```

```bash
git config --local user.email
```

缺少哪项就回到任务二设置哪项，不需要修改系统范围配置。

### 2. 文件存在，但git status没有显示

检查它是否被忽略：

```bash
git check-ignore -v .env
```

如果是密码、密钥或日志，应继续忽略；如果是应当跟踪的脱敏模板，应检查规则是否过宽。

### 3. git add后，git diff没有输出

变化已经进入暂存区，应查看：

```bash
git diff --cached
```

### 4. git restore后文件没有恢复到预期版本

先检查文件现在是工作区修改、已暂存修改，还是希望从某个历史版本恢复。查看：

```bash
git status --short
```

```bash
git diff
```

```bash
git diff --cached
```

根据状态选择`git restore`、`git restore --staged`或带`--source`的恢复命令。

### 5. clone提示remote HEAD refers to nonexistent ref

裸仓库的HEAD没有指向已存在的默认分支。检查：

```bash
git --git-dir=~/m1-project/git-server/techcorp.git symbolic-ref HEAD
```

本实验应在创建裸仓库时使用`--initial-branch=main`，并在克隆前完成首次`main`推送。

### 6. push被拒绝

先查看全部历史：

```bash
git log --oneline --decorate --graph --all -n 10
```

再获取远程状态：

```bash
git fetch origin
```

不要立即使用`--force`。确认是否有其他提交、当前工作目录是否正确，再决定拉取或处理分歧。

### 7. pull --ff-only拒绝更新

说明本地与远程不能直接快进，或者本地工作区尚未处理。检查：

```bash
git status
```

```bash
git log --oneline --decorate --graph --all -n 10
```

本实验的正常流程保持单线历史，应能直接快进。出现分歧时保留现场并分析，不强制覆盖。

## 二十一、独立实践

在`git-review`副本中完成以下任务：

1. 为`docs/handover.md`增加“验证备份能否恢复”；
2. 查看工作区差异；
3. 只暂存该文件并查看暂存差异；
4. 使用自己的提交信息形成一次提交；
5. 推送到裸仓库；
6. 回到`git-lab`使用`git pull --ff-only`获取提交；
7. 使用`git show`读取该提交中的文档，而不修改工作区。

验收时需要解释每一步时数据位于工作区、暂存区、本地仓库还是裸仓库。

## 二十二、环境保留

保留以下成果供实验19和实验20使用：

- `~/m1-project/git-lab`及其完整`.git`历史；
- `~/m1-project/git-server/techcorp.git`；
- `~/m1-project/git-review`；
- `main`分支和`linux-lab18-v1`标签；
- `docs`、`templates`和空的`scripts`目录规划；
- `~/m1-project/evidence/lab18-git-*.txt`。

实验19将在`git-lab/scripts`中创建`server-health.sh`并提交。实验20继续增加最终架构与交付记录。机房还原前必须保存课程快照或独立副本，因为同机三个Git目录会随虚拟机还原一起丢失。

## 二十三、官方参考

- [Git教程](https://git-scm.com/docs/gittutorial)
- [git init](https://git-scm.com/docs/git-init)
- [git status](https://git-scm.com/docs/git-status)
- [git diff](https://git-scm.com/docs/git-diff)
- [git restore](https://git-scm.com/docs/git-restore)
- [gitignore](https://git-scm.com/docs/gitignore)
- [git pull](https://git-scm.com/docs/git-pull)
