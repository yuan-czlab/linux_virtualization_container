# 实验18：Git项目获取与版本恢复

> 所属模块：模块三 企业服务部署与综合运维  
> 建议学时：2学时  
> 实验方式：个人  
> 对应教材：《模块三 企业服务部署与综合运维》第29章  
> 知识前置：教材第29章以及文件、文本和版本恢复概念\
> 状态依赖：`rocky-server`和可用软件源；仓库及全部练习文件由本实验创建，不依赖Redis数据\
> 建议起点：`Linux-L2`或当前连续实验环境\
> 项目成果：一个本地运维仓库、一个裸仓库、一个克隆副本、至少两次有效提交和一次版本恢复记录

## 一、项目情境

TechCorp服务器已经部署了多项服务。管理员需要记录站点说明、巡检文档和经过脱敏的配置模板，并能够在文件误改、误删后快速恢复。本实验使用本地仓库模拟团队仓库，不依赖GitHub等互联网平台。

> Git只能恢复已经提交或暂存过的内容。数据库文件、密码、私钥和运行日志不应直接提交到仓库。

## 二、实验目标

### 1. 知识目标

1. 说明工作区、暂存区、本地仓库和远程仓库的关系。
2. 区分`clone`、`pull`、`add`、`commit`和`restore`的用途。
3. 理解提交是可追溯的版本记录，不等同于普通文件复制。

### 2. 能力目标

1. 安装Git并完成用户身份配置。
2. 初始化仓库，编写`.gitignore`并完成两次提交。
3. 建立本地裸仓库，完成推送、克隆和拉取。
4. 恢复未提交的误改、误删文件，并验证恢复结果。

### 3. 素质目标

1. 提交前先检查差异，避免密码、私钥和临时文件进入仓库。
2. 使用能够说明变更目的的提交信息。
3. 恢复前先确认目标版本和影响范围，不盲目覆盖工作成果。

## 三、知识准备

```text
工作区 --git add--> 暂存区 --git commit--> 本地仓库
                                         |
                                         +--git push--> 裸仓库（模拟远程仓库）
                                                            |
                                                            +--git clone/pull--> 另一工作副本
```

| 命令 | 本实验中的用途 |
|---|---|
| `git status` | 查看文件处于未跟踪、已修改还是已暂存状态 |
| `git diff` | 查看尚未暂存的内容变化 |
| `git diff --cached` | 查看将要提交的内容 |
| `git add` | 将确认过的变化放入暂存区 |
| `git commit` | 形成一次有说明的本地版本记录 |
| `git log` | 查看历史提交 |
| `git restore` | 恢复工作区或暂存区文件 |
| `git clone` | 从已有仓库创建完整工作副本 |
| `git pull` | 获取并合并远端的新提交 |

## 四、实验环境

- `rocky-server`运行Rocky Linux 9，本实验回到数据与运维服务器完成。
- 普通用户具有`sudo`权限。
- 使用目录`~/m1-project/git-lab`。
- 本实验不要求注册外部代码托管账号。

## 五、项目任务

1. 安装Git并设置实验身份。
2. 建立运维资料仓库和忽略规则。
3. 完成初始版本和配置模板更新版本。
4. 建立本地裸仓库并完成首次推送。
5. 从裸仓库克隆，模拟另一名管理员提交更新。
6. 在原工作目录拉取更新。
7. 模拟文件误改和误删，使用Git恢复。

## 六、实验步骤

### 任务一：安装并检查Git

```bash
test "$(hostnamectl --static)" = 'rocky-server' && echo HOST_PASS || echo HOST_FAIL
```

```bash
sudo dnf install -y git
git --version
mkdir -p ~/m1-project/evidence ~/m1-project/backup ~/m1-project/git-lab
```

只在当前实验仓库内设置身份，避免修改其他课程仓库的全局配置：

```bash
cd ~/m1-project/git-lab
git init
git config user.name "Student Ops"
git config user.email "student@lab.local"
git config --local --list
```

预期能够看到`user.name`和`user.email`。

> **验收点**：Git可用，仓库初始化完成，身份配置只作用于当前仓库。

### 任务二：建立安全的运维仓库

#### 步骤1：创建目录和说明文件

```bash
cd ~/m1-project/git-lab
mkdir -p docs templates evidence runtime secrets
cat > README.md <<'EOF'
# TechCorp Linux运维资料

本仓库保存经过脱敏的配置模板、巡检说明和变更记录。
禁止提交密码、私钥、数据库数据文件和运行日志。
EOF

cat > docs/service-map.md <<'EOF'
# 服务清单

| 服务 | 端口 | 对外策略 |
|---|---:|---|
| SSH | 22 | 按课程网络范围开放 |
| Nginx | 80 | 对外提供Web访问 |
| MySQL | 3306 | 仅本机或指定管理主机 |
| MongoDB | 27017 | 仅本机 |
| Redis | 6379 | 仅本机 |
EOF
```

#### 步骤2：建立忽略规则

```bash
cat > .gitignore <<'EOF'
# 密钥与密码
*.key
*.pem
.env
secrets/

# 日志、数据库转储和运行数据
*.log
*.sql
*.dump
runtime/
evidence/

# 编辑器临时文件
*~
*.swp
EOF
```

创建几项用于验证的敏感或临时文件：

```bash
printf 'DB_PASSWORD=do-not-commit\n' > .env
printf 'temporary log\n' > runtime/app.log
printf 'dummy key material for ignore-rule test\n' > secrets/server.key
git status --short --ignored
```

预期`.env`、`runtime/`和`secrets/`显示为被忽略，不应出现在待提交文件中。

#### 步骤3：提交前检查

```bash
git status
git add README.md docs/service-map.md .gitignore
git diff --cached
git commit -m "docs: initialize operations repository"
git log --oneline --decorate -n 3
```

检查提交实际包含的文件：

```bash
git show --stat --oneline HEAD
git ls-files
```

> **验收点**：首次提交只包含README、服务清单和`.gitignore`，不包含任何敏感或运行文件。

### 任务三：提交脱敏配置模板

创建Nginx模板。模板中的地址和域名可以公开，不得写入数据库密码：

```bash
cat > templates/techcorp.conf.example <<'EOF'
server {
    listen 80;
    server_name _;
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
EOF

git status --short
git diff
git add templates/techcorp.conf.example
git diff --cached
git commit -m "feat: add sanitized nginx template"
git log --oneline --decorate --graph --all
```

给当前稳定版本添加标签：

```bash
git tag -a linux-lab18-v1 -m "Lab 18 verified version"
git tag
git show --stat linux-lab18-v1
```

> **验收点**：仓库至少包含两次提交和一个标签，第二次提交只增加脱敏模板。

### 任务四：用本地裸仓库模拟团队远程仓库

裸仓库没有工作区，通常用作多人交换提交的中心仓库。

```bash
mkdir -p ~/m1-project/git-server
git init --bare ~/m1-project/git-server/techcorp.git
cd ~/m1-project/git-lab
git branch -M main
git remote add origin ~/m1-project/git-server/techcorp.git
git remote -v
git push -u origin main
git push origin linux-lab18-v1
```

验证远程分支：

```bash
git ls-remote --heads --tags origin
```

> **验收点**：本地仓库的`main`分支和标签已推送到裸仓库。

### 任务五：模拟另一名管理员克隆和提交

```bash
cd ~/m1-project
git clone ~/m1-project/git-server/techcorp.git git-review
cd ~/m1-project/git-review
git config user.name "Reviewer Ops"
git config user.email "reviewer@lab.local"
git status
git log --oneline -n 3
```

如果克隆后提示远端HEAD没有指向分支，可在裸仓库中设置后重新克隆：

```bash
git --git-dir=~/m1-project/git-server/techcorp.git symbolic-ref HEAD refs/heads/main
```

在克隆副本中增加交接说明：

```bash
cat > docs/handover.md <<'EOF'
# 运维交接检查

1. 先看服务状态和端口。
2. 再检查配置语法和日志。
3. 修改前备份，修改后验证。
4. 提交前确认没有密码和私钥。
EOF

git add docs/handover.md
git diff --cached
git commit -m "docs: add operations handover checklist"
git push origin main
```

回到原工作目录获取变化：

```bash
cd ~/m1-project/git-lab
git status
git pull --ff-only
git log --oneline --decorate --graph -n 5
test -f docs/handover.md && echo 'PASS: handover file received'
```

使用`--ff-only`可以在历史无法直接快进时停止，避免未经判断自动产生合并提交。

### 任务六：恢复未提交的误改和误删

#### 场景1：误改文件

```bash
cd ~/m1-project/git-lab
printf '\n错误变更：所有数据库端口对公网开放。\n' >> docs/service-map.md
git status --short
git diff -- docs/service-map.md
```

确认这项修改应被丢弃后恢复：

```bash
git restore docs/service-map.md
git status --short
tail -n 5 docs/service-map.md
```

#### 场景2：误删文件

```bash
rm templates/techcorp.conf.example
git status --short
git diff -- templates/techcorp.conf.example
git restore templates/techcorp.conf.example
test -f templates/techcorp.conf.example && echo 'PASS: template restored'
```

> 此处删除的是实验仓库中已提交的模板，并立即用Git恢复；不要把此命令套用到其他目录。

#### 场景3：恢复到指定历史版本的内容

先比较当前README与标签版本：

```bash
git diff linux-lab18-v1 -- README.md
git show linux-lab18-v1:README.md | sed -n '1,20p'
```

本实验不要求回退整个仓库。如果确需从标签取回单个文件，应先备份当前内容，再执行：

```bash
cp README.md ~/m1-project/backup/README.md.before-restore
git restore --source=linux-lab18-v1 -- README.md
git diff -- README.md
```

如果文件本来没有差异，`git diff`为空属于正常现象。

### 任务七：形成实验记录

```bash
cd ~/m1-project/git-lab
{
    printf '=== repository ===\n'
    git status --short --branch
    printf '\n=== remotes ===\n'
    git remote -v
    printf '\n=== history ===\n'
    git log --oneline --decorate --graph --all -n 10
    printf '\n=== tracked files ===\n'
    git ls-files
    printf '\n=== ignored sample ===\n'
    git status --short --ignored | sed -n '1,30p'
} | tee ~/m1-project/evidence/lab18-git-final.txt
```

## 七、故障排查

### 故障1：提交时提示身份未知

```bash
git config --local user.name
git config --local user.email
git config user.name "Student Ops"
git config user.email "student@lab.local"
```

### 故障2：文件明明存在却没有出现在状态中

```bash
git check-ignore -v 文件路径
```

如果是应该跟踪的模板，调整`.gitignore`；如果是密码、密钥或日志，应继续忽略。

### 故障3：推送提示没有上游分支

```bash
git branch --show-current
git remote -v
git push -u origin main
```

### 故障4：拉取时无法快进

```bash
git status
git log --oneline --graph --decorate --all -n 10
```

不要直接强制覆盖。先保存本地改动，确认分支历史，再决定提交、暂存或合并。本实验要求保持单线历史，正常情况下应能快进。

### 故障5：把敏感文件加入了暂存区但尚未提交

```bash
git restore --staged 文件路径
git status
```

随后补充`.gitignore`。如果已经推送，单纯删除最新文件并不能从历史中彻底清除秘密，应立即更换凭据并联系教师处理历史清理。

## 八、项目验收

### 1. 必做成果

- `~/m1-project/git-lab`工作仓库。
- `~/m1-project/git-server/techcorp.git`裸仓库。
- `~/m1-project/git-review`克隆副本。
- 至少两次个人提交和一次模拟协作提交。
- 标签`linux-lab18-v1`。
- `lab18-git-final.txt`证据文件。

### 2. 现场操作

1. 使用`git status`说明当前仓库状态。
2. 使用`git log`指出某次提交的目的。
3. 说明`.gitignore`为什么不能代替密码管理。
4. 现场误改一个已提交文件，展示差异并恢复。

### 3. 评分建议

| 项目 | 分值 | 评价要点 |
|---|---:|---|
| 仓库与身份配置 | 15 | Git可用，配置范围正确 |
| 安全忽略规则 | 20 | 密码、私钥、日志和数据文件未提交 |
| 提交质量 | 20 | 至少两次提交，信息清楚，提交前检查差异 |
| 克隆、推送与拉取 | 20 | 本地团队流程完整 |
| 误改误删恢复 | 15 | 能说明并正确使用`git restore` |
| 证据与现场说明 | 10 | 记录完整、表述准确 |

## 九、独立练习

1. 修改`docs/handover.md`，增加“备份恢复必须验证”，提交并推送。
2. 在克隆副本执行`git pull --ff-only`，确认收到新提交。
3. 使用`git show <提交号>:docs/handover.md`读取历史内容，但不改变工作区。

## 十、实验总结

请用自己的语言回答：

1. 工作区、暂存区和仓库分别保存什么？
2. 为什么配置模板可以进入Git，而真实密码和私钥不可以？
3. `git restore`能恢复什么，不能替代什么？
4. 为什么运维提交应当小而清晰？
