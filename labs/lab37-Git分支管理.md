# Lab37：Git 分支管理与 .gitignore

> 课时：2 | 类型：个人 | 前置：Lab36

## 一、实验步骤

### 步骤1：创建和切换分支

```bash
cd /tmp && mkdir git-branch-lab && cd git-branch-lab
git init

echo "v1.0" > version.txt
git add . && git commit -m "v1.0: initial"

# 创建分支
git branch dev                    # 创建 dev 分支
git branch                        # 查看所有分支（* 表示当前）
#   dev
# * main

# 切换分支
git checkout dev                  # 或 git switch dev
git branch                        # * dev

# 在 dev 上修改
echo "v1.1-dev-feature" > version.txt
git add . && git commit -m "dev: new feature"

# 切回 main → 内容恢复到 v1.0
git checkout main
cat version.txt                   # v1.0
```

### 步骤2：合并分支

```bash
# 把 dev 的修改合并到 main
git merge dev -m "merge dev branch"
cat version.txt                   # v1.1-dev-feature（dev的内容合过来了）

git log --oneline --graph --all
# *   merge dev branch (main)
# |\
# | * dev: new feature (dev)
# |/
# * v1.0: initial
```

### 步骤3：多环境分支模拟

```bash
# 从 main 创建 staging（预发布）分支
git checkout main
git checkout -b staging
echo "v1.1-rc1" > version.txt
git add . && git commit -m "staging: release candidate"

# 三个分支：main(生产) / staging(预发布) / dev(开发)
git branch
#   dev
# * staging
#   main

git checkout dev && cat version.txt      # v1.1-dev-feature
git checkout staging && cat version.txt  # v1.1-rc1
git checkout main && cat version.txt     # v1.1-dev-feature（已被dev合并）
```

### 步骤4：.gitignore 保护敏感信息

```bash
# 创建不应提交的文件
echo "DB_PASSWORD=secret123" > .env
echo "API_KEY=sk-abcdef" > .env.local
mkdir logs && touch logs/app.log
mkdir __pycache__ && touch __pycache__/test.pyc

git status
# 这些文件出现在 Untracked files 中

# 创建 .gitignore
cat > .gitignore << 'EOF'
# 环境配置文件（含密码/密钥）
.env
.env.local
*.key
*.pem

# 日志
logs/
*.log

# Python 缓存
__pycache__/
*.pyc

# IDE 配置
.vscode/
.idea/

# 操作系统
.DS_Store
Thumbs.db
EOF

git add .gitignore
git commit -m "add .gitignore"

git status
# .env / logs/ / __pycache__/ 不再出现 ✓
```

### 步骤5：tag 标记版本

```bash
# 打 tag 标记稳定版本
git tag v1.0.0 -m "first stable release"
git tag v1.1.0 -m "added new feature"

git tag                          # 查看所有 tag
git show v1.0.0                  # 查看 tag 详情

# 通过 tag 回滚
git checkout v1.0.0
cat version.txt                  # v1.0 的内容
git checkout main                # 回到最新
```

---

## 五、练习题

### 练习1：分支操作（20分）

从 main 创建 hotfix 分支 → 修复 bug → 合并回 main → 删除 hotfix 分支。写出完整命令序列。

### 练习2：.gitignore 编写（20分）

为一个 Python Web 项目写 `.gitignore`，需要忽略：
- 虚拟环境目录 `venv/`
- Python 缓存 `__pycache__/` `*.pyc`
- 环境变量 `.env`
- IDE 配置 `.vscode/` `.idea/`
- 日志 `*.log` `logs/`
- 上传目录 `uploads/`

### 练习3：分支策略理解（25分）

| 分支 | 用途 | 谁能合并 |
|------|------|---------|
| main | | |
| staging | | |
| dev | | |
| hotfix | | |

画出 Git Flow 分支模型图。

### 练习4：tag 操作（15分）

1. 给当前版本打 tag `v2.0.0`
2. 模拟发现 v2.0.0 有 bug → 回滚到 v1.0.0
3. 从 v1.0.0 开 hotfix 分支修复 → 打 tag `v2.0.1`
4. tag 和 branch 有什么区别？什么时候用哪个？

### 练习5：运维部署的分支策略（20分）

设计一套适合运维部署的 Git 策略：
1. 开发在 dev 分支开发
2. 测试环境用 staging 分支
3. 生产环境用 main 分支 + tag 版本号
4. 写出从"开发者提交代码"到"生产部署"的完整流程

## 七、常见问题

**Q: merge 和 rebase 有什么区别？**
A: merge 保留完整分支历史（产生合并提交），rebase 把提交"搬"到目标分支顶部（线性历史）。运维部署场景一般用 merge，更安全直观。

**Q: .gitignore 写好了但文件已经被跟踪了怎么办？**
A: .gitignore 只对未跟踪（Untracked）文件生效。已被跟踪的文件需要用 `git rm --cached 文件名` 从跟踪列表移除，再提交。

**Q: tag 和 branch 有什么区别？**
A: tag 是静态标记（指向某个 commit 不变），branch 是动态的（随着新提交移动）。发布版本用 tag，日常开发用 branch。

## 八、课后思考

1. Git Flow、GitHub Flow、GitLab Flow 三种分支模型有什么区别？运维部署场景更适合用哪种？

2. 生产环境部署时，应该用 `git checkout main` 还是 `git checkout v2.0.0`（tag）？为什么 tag 更可控？
