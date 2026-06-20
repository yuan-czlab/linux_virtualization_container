# Lab36：Git 基础操作

> 课时：2 | 类型：个人 | 前置：无

## 一、你会学到什么
- 理解 Git 在运维部署中的作用（拉代码+版本控制+回滚）
- 能 clone 远程仓库、pull 更新、查看历史
- 能初始化本地仓库并提交

## 二、实验步骤

### 步骤1：安装与配置

```bash
sudo dnf install -y git
git --version

# 全局配置（提交时使用的身份信息）
git config --global user.name "YourName"
git config --global user.email "yourstudentid@example.com"
git config --global init.defaultBranch main

# 查看配置
git config --list
cat ~/.gitconfig
```

### 步骤2：克隆远程仓库

```bash
cd /tmp

# 克隆 Nginx 官方示例仓库（或任何公开仓库）
git clone https://gitee.com/mirrors/nginx-demos.git 2>/dev/null || \
git clone https://github.com/nginxinc/NGINX-Demos.git

cd NGINX-Demos 2>/dev/null || cd nginx-demos

# 查看仓库内容
ls -la
ls -la .git/                  # Git 的所有数据都在这里
# HEAD  config  objects/  refs/  logs/  ...
```

### 步骤3：查看提交历史

```bash
# 简洁版历史
git log --oneline | head -10
# a1b2c3d 修复了登录页面样式
# e4f5g6h 添加了用户认证功能
# ...

# 图形化分支历史
git log --oneline --graph --all | head -20

# 查看某次提交的详细变更
git show HEAD
# 或 git show 某个commitID

# 查看最近 3 次提交的文件变更列表
git log --stat -3
```

### 步骤4：git pull 拉取更新

```bash
git pull origin main
# Already up to date.

# git pull = git fetch（拉取远程数据） + git merge（合并到本地）
# 分步执行：
git fetch origin
git merge origin/main
```

### 步骤5：创建本地仓库并提交

```bash
mkdir /tmp/my-project && cd /tmp/my-project
git init

echo "# My Project" > README.md
echo "<h1>Hello</h1>" > index.html

git status                      # 查看状态（Untracked files）
git add README.md index.html    # 添加到暂存区
git status                      # Changes to be committed

git commit -m "first commit: add README and index"

# 查看提交记录
git log --oneline

# 修改文件后再提交
echo "<p>Updated</p>" >> index.html
git status                      # modified: index.html
git diff                        # 查看具体改了什么
git add index.html
git commit -m "update index.html"
```

### 步骤6：理解 Git 工作区

```
工作区 (Working Directory)    暂存区 (Staging)      本地仓库 (Local Repo)
    │                              │                      │
    │  git add ──────────────────→ │                      │
    │                              │  git commit ──────→ │
    │                              │                      │
    │                    git status 查看                  │
    │                    git diff 比较                    │
```

---

## 五、练习题

### 练习1：Git 基本概念（15分）

| 概念 | 解释 |
|------|------|
| Working Directory | |
| Staging Area | |
| Local Repository | |
| Remote Repository | |
| HEAD | |

### 练习2：日常部署流程（20分）

模拟运维部署流程：
1. 在 `/tmp/deploy-test` 初始化 Git 仓库
2. 提交 3 个版本的代码（v1 → v2 → v3）
3. 用 `git log --oneline` 查看历史
4. 用 `git diff HEAD~1 HEAD` 查看最新一次改了什么

### 练习3：git clone vs 下载 ZIP（20分）

1. `git clone` 和直接从网页下载 ZIP 有什么区别？
2. `.git` 目录里存了什么？删了 `.git` 会怎样？
3. 如果仓库有 1000 次提交历史，`git clone` 会下载全部吗？

### 练习4：git pull 冲突模拟（25分）

1. 克隆一个仓库到两个目录（模拟两台服务器）
2. 在两个目录中分别修改同一个文件
3. 在目录A中提交并（模拟）推送
4. 在目录B中 `git pull` → 观察冲突
5. 了解：冲突怎么解决？（不要求深入，知道概念即可）

### 练习5：运维部署中的 Git（20分）

1. 为什么运维部署推荐用 `git clone/pull` 而不是 scp 传文件？
2. 怎么用 `git checkout 某个commit` 做版本回滚？
3. 怎么用 `git tag` 标记稳定版本？
4. 写一份"用 Git 部署 Web 应用"的标准操作流程（SOP）

## 七、常见问题

**Q: git clone 和 git pull 有什么区别？**
A: clone = 首次下载整个仓库。pull = 已有仓库的情况下拉取最新更新（= fetch + merge）。服务器部署时，第一次用 clone，后续更新用 pull。

**Q: .git 目录能删吗？**
A: 删了 .git 目录就变成普通文件夹了，所有版本控制信息丢失。除非你确定不需要版本历史（如打包发布），否则不要删。

**Q: git clone 下载到一半断了怎么办？**
A: git clone 不支持断点续传。可以用 `git clone --depth 1` 浅克隆减少下载量，或者改用 SSH 协议（比 HTTPS 更稳定）。

## 八、课后思考

1. 运维用 Git 部署代码时，是直接在服务器上 `git pull` 好，还是用 CI/CD 工具（如 Jenkins）构建好再部署？各有什么优缺点？

2. Git 的 .git 目录会越来越大吗？服务器上部署了 3 年的项目，.git 目录可能有几 GB，怎么清理？
