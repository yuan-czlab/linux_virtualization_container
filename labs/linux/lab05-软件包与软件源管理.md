# 实验5：软件包与软件源管理

> 所属模块：模块一 Linux基础运维  
> 建议学时：2学时  
> 实验方式：个人  
> 对应教材：《模块一 Linux基础运维》第10章  
> 前置实验：实验4  
> 项目成果：软件源基线、指定软件安装查询卸载记录及仓库回退文件

## 一、项目情境

新服务器需要安装运维工具。你需要先确认软件来源可信、仓库可用，再完成软件搜索、安装、文件归属查询和卸载。软件源发生故障时，应能根据备份恢复，而不是从未知网站下载软件包或脚本。

## 二、实验目标

### 1. 知识目标

1. 说明RPM软件包、DNF、软件仓库、元数据、依赖和GPG签名的关系。
2. 区分“软件包已经安装”“仓库中可以获得”和“命令可以执行”。
3. 了解RPM/DNF与DEB/APT的对应关系。

### 2. 能力目标

1. 查看并保存当前软件源基线。
2. 搜索、安装、查询和卸载指定软件。
3. 查询命令来自哪个软件包、软件包安装了哪些文件。
4. 备份仓库配置并验证回退文件完整。

### 3. 素质目标

1. 不直接执行来源不明的在线安装脚本。
2. 修改仓库前先备份，修改后验证仓库和GPG设置。
3. 不在课程环境中随意进行不可控的全系统升级。

## 三、知识准备

```text
DNF读取仓库配置
→ 下载并刷新仓库元数据
→ 计算目标软件包及依赖
→ 校验来源与签名
→ 调用RPM数据库安装文件
→ 软件文件出现在系统目录中
```

| Rocky Linux | Ubuntu/Debian | 用途 |
|---|---|---|
| RPM | DEB | 软件包格式及底层数据库 |
| `rpm` | `dpkg` | 查询或操作本地软件包 |
| `dnf` | `apt` | 处理仓库和依赖的高层工具 |
| `/etc/yum.repos.d/*.repo` | `/etc/apt/sources.list*` | 软件源配置 |

## 四、实验环境

- Rocky Linux 9，student具备sudo权限。
- 使用教师已经验证的软件源或机房离线仓库。
- 本实验以`tree`和`jq`作为练习包；若离线仓库未提供，由教师替换为等价小工具。

## 五、项目任务

1. 保存系统、DNF和仓库基线。
2. 备份仓库配置。
3. 搜索并安装指定软件。
4. 查询包信息、文件、依赖和命令归属。
5. 卸载一个练习包并验证结果。
6. 保存操作历史和回退说明。

## 六、实验步骤

### 任务一：检查和备份软件源

#### 步骤1：记录基线

```bash
mkdir -p ~/m1-project/evidence ~/m1-project/backup/repos
{
    cat /etc/os-release
    dnf --version
    sudo dnf repolist --enabled
} | tee ~/m1-project/evidence/lab05-repo-baseline.txt
```

> **验收点**：文件中包含Rocky Linux版本、DNF版本和启用仓库列表。

#### 步骤2：备份仓库文件

```bash
sudo cp -a /etc/yum.repos.d/. ~/m1-project/backup/repos/
find ~/m1-project/backup/repos -maxdepth 1 -type f -printf '%f\n' | sort
```

确认备份非空：

```bash
test -n "$(find ~/m1-project/backup/repos -maxdepth 1 -type f -print -quit)"
echo $?
```

> **验收点**：退出码为0，备份目录中存在`.repo`文件。

#### 步骤3：检查仓库配置关键字段

```bash
grep -RHE '^\[(.+)\]|^baseurl=|^mirrorlist=|^metalink=|^enabled=|^gpgcheck=' /etc/yum.repos.d/*.repo | sed -n '1,100p'
```

重点确认仓库地址、是否启用以及`gpgcheck`。不要在不了解风险时把GPG校验统一关闭。

### 任务二：刷新元数据和搜索软件

#### 步骤4：验证仓库

```bash
sudo dnf makecache
sudo dnf repolist --enabled
```

仓库暂时不可用时保留完整报错，先区分DNS、网络、证书、仓库地址和服务器端故障，不要直接删除全部repo文件。

> **验收点**：元数据刷新成功；离线环境能够访问教师指定仓库。

#### 步骤5：搜索练习包

```bash
dnf search tree
dnf info tree
dnf repoquery --available tree
```

如果`repoquery`子命令不可用，记录该现象，不影响前两项核心验收。

### 任务三：安装和查询

#### 步骤6：安装指定软件

```bash
sudo dnf install -y tree jq
rpm -q tree jq
command -v tree
command -v jq
```

> **验收点**：两个包已安装，两个命令可以找到。

#### 步骤7：查询软件包内容

```bash
rpm -qi tree
rpm -ql tree | sed -n '1,40p'
rpm -qf "$(command -v tree)"
dnf repoquery --requires tree | sed -n '1,40p'
```

分别回答：软件包版本是什么、安装了哪些主要文件、`tree`命令属于哪个包。

#### 步骤8：实际运行

```bash
tree -L 2 ~/m1-project
printf '{"course":"linux","status":"ready"}\n' | jq .
```

软件安装成功还需要验证命令能够完成预期功能。

> **验收点**：tree能显示项目目录，jq能格式化JSON。

### 任务四：卸载和保存证据

#### 步骤9：卸载练习包

先查看计划：

```bash
sudo dnf remove tree --assumeno
```

确认不会移除课程关键软件后执行：

```bash
sudo dnf remove -y tree
rpm -q tree
command -v tree || true
```

`rpm -q tree`应提示未安装，`command -v`不应再找到命令。

> **验收点**：tree已卸载，jq仍可使用。

#### 步骤10：保存历史

```bash
sudo dnf history | sed -n '1,20p' | tee ~/m1-project/evidence/lab05-dnf-history.txt
```

DNF历史可帮助定位谁在何时执行了安装或卸载，但生产环境是否回滚仍需评估依赖和数据风险。

## 七、独立实践

1. 搜索教师指定的一个小工具。
2. 安装后查询版本、命令位置和所属软件包。
3. 找出该包安装的一个手册或配置文件。
4. 实际运行一次并保存结果。
5. 判断是否需要保留；不需要时先使用`--assumeno`检查卸载计划。

## 八、验收标准

- [ ] 已保存软件源和DNF基线。
- [ ] 仓库配置已备份且非空。
- [ ] 能说明DNF、RPM、仓库和依赖的关系。
- [ ] 能搜索、安装、查询和卸载软件。
- [ ] 能查询命令属于哪个软件包。
- [ ] 能区分包已安装和命令功能正常。
- [ ] 未关闭GPG校验，未执行来源不明脚本。
- [ ] DNF历史和独立实践记录完整。

## 九、成果提交

1. `lab05-repo-baseline.txt`。
2. 仓库备份文件清单。
3. tree和jq的安装、查询、运行与卸载结果。
4. `lab05-dnf-history.txt`。
5. 独立实践记录和仓库回退说明。

## 十、常见问题

### Q1：提示Could not resolve host

优先检查IP、默认路由和DNS；这是网络或解析问题，不等于软件包不存在。

### Q2：提示No match for argument

检查包名拼写、启用仓库和元数据。使用`dnf search`确认真实名称。

### Q3：提示Failed to download metadata

保留完整报错，检查时间、证书、DNS、代理和仓库地址。使用教师提供的已验证仓库或离线方案。

### Q4：为什么不直接dnf update -y

全量更新可能改变内核和大量依赖，影响后续实验一致性。课程环境应由教师统一安排更新窗口和回退点。

## 十一、课后思考与拓展

1. 为什么企业需要内部软件仓库？
2. GPG签名能解决什么风险，不能解决什么风险？
3. 删除软件包前为什么要先检查依赖变化？

## 十二、环境保留

保留jq、仓库备份和证据文件。tree是否重新安装按后续实验需要决定：

```bash
sudo dnf install -y tree
```

