# 实验19：Shell服务器巡检脚本

> 所属模块：模块三 企业服务器部署与综合运维
> 建议学时：2学时
> 实验方式：个人
> 对应教材：3.6 Shell服务器巡检
> 知识前置：已学习教材3.6，并完成实验14—18中的服务验收和Git操作
> 状态依赖：实验14的Nginx健康页、实验15—17的数据服务、实验18的`git-lab`仓库和三机网络
> 建议起点：保留实验14—18成果的连续环境
> 项目成果：逐段构建的巡检脚本、正常/故障/恢复记录、退出码证据和Git提交

## 一、项目情境

TechCorp的`rocky-server`运行MySQL、MongoDB、Redis和SSH，`rocky-web`提供Nginx健康页。管理员每天手工执行多条命令容易漏项，也无法让定时任务根据屏幕文字判断结果。

本实验将已经学会的只读命令逐步固化为`server-health.sh`。最终脚本需要：

- 输出检查时间、主机名、内核和负载；
- 判断根分区和可用内存是否达到阈值；
- 检查`mysqld`、`mongod`、`redis`和`sshd`；
- 检查22、3306、27017和6379端口；
- 从`rocky-server`访问`rocky-web`健康页；
- 使用0、1、2表达OK、WARN和CRITICAL；
- 只采集和报告，不自动重启或修改系统。

脚本不会一次性粘贴完成。每次只增加一个检查模块，随后立即进行语法检查和实际运行。

## 二、实验目标

### 1. 知识目标

1. 说明Shebang、变量、引用、命令替换和退出码。
2. 说明`if`、函数、数组和循环如何组织检查。
3. 区分标准输出、标准错误和脚本退出码。
4. 说明巡检、监控和自动修复的边界。

### 2. 能力目标

1. 先验证单条命令，再把它加入脚本。
2. 分7次迭代构建可执行巡检脚本。
3. 检查磁盘、内存、系统信息、服务、端口和Web入口。
4. 停止Redis制造受控故障，并在恢复后重新验证。
5. 把脚本和使用说明提交到实验18建立的Git仓库。

### 3. 安全与规范目标

1. 脚本不包含数据库或Redis密码。
2. 脚本不自动重启服务、开放端口或删除文件。
3. 异常测试前明确影响范围，测试后立即恢复。
4. 每次修改后先执行`bash -n`，再实际运行。
5. 日志和退出码证据保存在Git仓库外部。

## 三、巡检对象与判断标准

| 检查对象 | 采集方式 | 判断 | 异常级别 |
|---|---|---|---|
| 主机、内核、负载 | `hostnamectl`、`uname`、`/proc/loadavg` | 记录，不直接告警 | 信息 |
| 根分区 | `df -P /` | 使用率达到90% | WARN |
| 可用内存 | `/proc/meminfo` | 可用比例不高于10% | WARN |
| 本机服务 | `systemctl is-active` | 非active | CRITICAL |
| 本机端口 | `ss -lntH` | 未监听 | CRITICAL |
| Web健康页 | `curl --fail` | HTTP失败或超时 | CRITICAL |

阈值用于课程练习，不是所有生产系统的统一标准。服务和端口只检查`rocky-server`角色；Nginx运行在`rocky-web`，因此通过HTTP请求检查，而不是错误地检查本机`nginx`单元。

## 四、任务一：确认连续实验环境

### 步骤1：确认主机身份

```bash
hostnamectl --static
```

预期为`rocky-server`。

### 步骤2：确认Git工作仓库

```bash
git -C ~/m1-project/git-lab status --short --branch
```

应看到`main`分支，且没有未处理的已跟踪文件变化。如果目录不是Git仓库，应先完成实验18。

### 步骤3：确认脚本目录

```bash
mkdir -p ~/m1-project/git-lab/scripts
```

实验18已经规划该目录；由于空目录不会被Git跟踪，本步骤确保它实际存在。

### 步骤4：创建日志目录

```bash
mkdir -p ~/m1-project/logs
```

### 步骤5：创建证据目录

```bash
mkdir -p ~/m1-project/evidence
```

### 步骤6：确认服务名称

```bash
systemctl is-active mysqld
```

```bash
systemctl is-active mongod
```

```bash
systemctl is-active redis
```

```bash
systemctl is-active sshd
```

四项预期均为`active`。如果某项不存在或不正常，应回到对应实验修复，不能为了让脚本返回0而删除检查项。

### 步骤7：确认本机监听端口

```bash
sudo ss -lntp | grep -E ':(22|3306|27017|6379)\b'
```

3306、27017和6379可能只监听本机或指定地址，这是安全设计，不要求全部监听`0.0.0.0`。

### 步骤8：确认跨机名称解析

```bash
getent hosts rocky-web
```

### 步骤9：确认健康页

```bash
curl --fail --max-time 3 -H 'Host: techcorp.test' http://rocky-web/health
```

如果手工请求失败，先排查实验14和三机网络，不要立即编写脚本掩盖基线问题。

### 步骤10：确认资源采集命令

```bash
df -P /
```

```bash
grep -E '^(MemTotal|MemAvailable):' /proc/meminfo
```

```bash
cat /proc/loadavg
```

## 五、任务二：第1次迭代——创建最小脚本

### 步骤1：进入仓库

```bash
cd ~/m1-project/git-lab
```

### 步骤2：创建脚本

```bash
vim scripts/server-health.sh
```

输入以下最小内容：

```bash-script
#!/usr/bin/env bash

set -u

DISK_WARN=90
MEM_AVAILABLE_WARN=10
STATUS=0

SERVICES=(mysqld mongod redis sshd)
PORTS=(22 3306 27017 6379)
WEB_URL='http://rocky-web/health'
WEB_HOST='techcorp.test'

printf '=== TechCorp Server Health Check ===\n'
printf 'host=%s\n' "$(hostnamectl --static)"
printf 'result_code=%d\n' "$STATUS"
exit "$STATUS"
```

这一步只建立配置和最小输出，不做复杂判断。

### 步骤3：检查语法

```bash
bash -n scripts/server-health.sh
```

没有输出表示未发现语法错误。

### 步骤4：赋予执行权限

```bash
chmod 750 scripts/server-health.sh
```

### 步骤5：执行最小脚本

```bash
./scripts/server-health.sh
```

### 步骤6：立即查看退出码

```bash
printf 'exit=%s\n' "$?"
```

预期返回0。此时只证明最小脚本可执行，不代表巡检功能已经完成。

## 六、任务三：第2次迭代——增加统一输出函数

重新打开脚本：

```bash
vim scripts/server-health.sh
```

在`WEB_HOST`配置之后、第一条`printf`之前加入三个函数：

```bash-script
ok() {
    printf '[OK]   %s\n' "$1"
}

warn() {
    printf '[WARN] %s\n' "$1"
    if (( STATUS < 1 )); then
        STATUS=1
    fi
}

crit() {
    printf '[CRIT] %s\n' "$1" >&2
    STATUS=2
}
```

三个函数统一输出格式。`warn`只在当前状态低于1时升级，`crit`直接升级到2。后续正常项不会把严重状态改回0。

保存后检查语法：

```bash
bash -n scripts/server-health.sh
```

执行当前版本：

```bash
./scripts/server-health.sh
```

这一版输出暂时与上一版相近，因为函数已经定义但尚未调用。

## 七、任务四：第3次迭代——增加系统与磁盘检查

重新编辑：

```bash
vim scripts/server-health.sh
```

在`crit`函数之后、底部执行区域之前加入：

```bash-script
check_system() {
    local load1 cpu_count
    load1=$(awk '{print $1}' /proc/loadavg)
    cpu_count=$(getconf _NPROCESSORS_ONLN)
    ok "内核版本为$(uname -r)"
    ok "1分钟负载为${load1}，CPU逻辑核数为${cpu_count}"
}

check_disk() {
    local used
    used=$(df -P / | awk 'NR==2 {gsub(/%/, "", $5); print $5}')
    if [[ ! "$used" =~ ^[0-9]+$ ]]; then
        crit '无法读取根分区使用率'
    elif (( used >= DISK_WARN )); then
        warn "根分区使用率为${used}%，阈值为${DISK_WARN}%"
    else
        ok "根分区使用率为${used}%"
    fi
}
```

在底部`result_code`输出之前加入两次调用：

```bash-script
check_system
check_disk
```

保存后检查语法：

```bash
bash -n scripts/server-health.sh
```

执行并观察：

```bash
./scripts/server-health.sh
```

将脚本输出与手工`df -P /`结果对照。使用率未达到90%时应显示`[OK]`。

## 八、任务五：第4次迭代——增加内存检查

重新编辑：

```bash
vim scripts/server-health.sh
```

在`check_disk`之后加入：

```bash-script
check_memory() {
    local total_kb available_kb available_pct
    total_kb=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)
    available_kb=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)

    if [[ ! "$total_kb" =~ ^[0-9]+$ || ! "$available_kb" =~ ^[0-9]+$ || "$total_kb" -eq 0 ]]; then
        crit '无法读取有效内存数据'
        return
    fi

    available_pct=$(( available_kb * 100 / total_kb ))
    if (( available_pct <= MEM_AVAILABLE_WARN )); then
        warn "可用内存为${available_pct}%，阈值为${MEM_AVAILABLE_WARN}%"
    else
        ok "可用内存为${available_pct}%"
    fi
}
```

在底部`check_disk`之后加入调用：

```bash-script
check_memory
```

保存后检查语法：

```bash
bash -n scripts/server-health.sh
```

执行当前版本：

```bash
./scripts/server-health.sh
```

使用`free -h`和`/proc/meminfo`对照结果。脚本判断的是可用比例，不是`free`列中的字面空闲内存。

## 九、任务六：第5次迭代——增加服务循环

重新编辑：

```bash
vim scripts/server-health.sh
```

在`check_memory`之后加入：

```bash-script
check_services() {
    local service
    for service in "${SERVICES[@]}"; do
        if systemctl is-active --quiet "$service"; then
            ok "服务${service}处于active"
        else
            crit "服务${service}未处于active"
        fi
    done
}
```

在底部`check_memory`之后加入调用：

```bash-script
check_services
```

保存后检查语法：

```bash
bash -n scripts/server-health.sh
```

执行当前版本：

```bash
./scripts/server-health.sh
```

应看到4条服务结果。不要加入只存在于`rocky-web`的`nginx`服务。

## 十、任务七：第6次迭代——增加端口循环

重新编辑：

```bash
vim scripts/server-health.sh
```

在`check_services`之后加入：

```bash-script
check_ports() {
    local port
    for port in "${PORTS[@]}"; do
        if ss -lntH | awk '{print $4}' | grep -Eq ":${port}$"; then
            ok "TCP端口${port}正在监听"
        else
            crit "TCP端口${port}未监听"
        fi
    done
}
```

在底部`check_services`之后加入调用：

```bash-script
check_ports
```

保存后检查语法：

```bash
bash -n scripts/server-health.sh
```

执行当前版本：

```bash
./scripts/server-health.sh
```

将结果与`ss -lntH`对照。端口监听在`127.0.0.1`、业务IP或IPv6回环地址时，结尾都仍是`:端口号`。

## 十一、任务八：第7次迭代——增加Web检查和最终结果

重新编辑：

```bash
vim scripts/server-health.sh
```

在`check_ports`之后加入：

```bash-script
check_web() {
    if curl --silent --show-error --fail --max-time 3 -H "Host: ${WEB_HOST}" "$WEB_URL" >/dev/null; then
        ok 'rocky-web健康页返回成功'
    else
        crit 'rocky-web健康页访问失败'
    fi
}
```

在底部`check_ports`之后加入调用：

```bash-script
check_web
```

删除原来的单行`printf 'result_code...`，在所有检查调用之后加入最终汇总：

```bash-script
printf '\nresult_code=%d\n' "$STATUS"
case "$STATUS" in
    0) printf 'result=OK\n' ;;
    1) printf 'result=WARN\n' ;;
    2) printf 'result=CRITICAL\n' ;;
esac
exit "$STATUS"
```

同时在标题下补充检查时间：

```bash-script
printf 'time=%s\n' "$(date '+%F %T %z')"
```

确保文件末尾只保留一条`exit "$STATUS"`，不要重复退出。

保存后进行语法检查：

```bash
bash -n scripts/server-health.sh
```

立即读取语法检查退出码：

```bash
printf 'syntax_exit=%s\n' "$?"
```

预期为0。

执行最终版本：

```bash
./scripts/server-health.sh
```

立即读取脚本退出码：

```bash
printf 'health_exit=%s\n' "$?"
```

## 十二、最终脚本结构核对

不需要重新复制完整脚本。使用以下命令核对逐段构建的结果。

### 步骤1：查看前40行

```bash
nl -ba scripts/server-health.sh | sed -n '1,40p'
```

### 步骤2：查看中间部分

```bash
nl -ba scripts/server-health.sh | sed -n '41,100p'
```

### 步骤3：查看剩余部分

```bash
nl -ba scripts/server-health.sh | sed -n '101,180p'
```

最终结构应按顺序包含：

1. Shebang和`set -u`；
2. 阈值、服务、端口和Web参数；
3. `ok`、`warn`、`crit`；
4. `check_system`、`check_disk`、`check_memory`；
5. `check_services`、`check_ports`、`check_web`；
6. 标题、时间和主机输出；
7. 六个检查函数调用；
8. 结果文字和`exit "$STATUS"`。

再次确认语法：

```bash
bash -n scripts/server-health.sh
```

## 十三、任务九：保存正常巡检结果

### 步骤1：执行并合并保存输出

```bash
./scripts/server-health.sh > ~/m1-project/logs/health-normal.log 2>&1
```

### 步骤2：立即保存退出码

```bash
printf '%s\n' "$?" > ~/m1-project/evidence/lab19-normal-exit.txt
```

### 步骤3：查看日志

```bash
cat ~/m1-project/logs/health-normal.log
```

### 步骤4：查看退出码证据

```bash
cat ~/m1-project/evidence/lab19-normal-exit.txt
```

资源都低于警告阈值且服务正常时，预期为0。如果为1，查看`[WARN]`并确认实际资源状态；不能只为得到0而删除检查或随意提高阈值。

### 步骤5：分开保存stdout和stderr

```bash
./scripts/server-health.sh > ~/m1-project/logs/health.stdout.log 2> ~/m1-project/logs/health.stderr.log
```

### 步骤6：立即查看退出码

```bash
printf 'split_output_exit=%s\n' "$?"
```

### 步骤7：比较文件行数

```bash
wc -l ~/m1-project/logs/health.stdout.log ~/m1-project/logs/health.stderr.log
```

正常环境中stderr通常为空；有`[CRIT]`时，错误文件应出现内容。

## 十四、任务十：停止Redis验证CRITICAL

本任务只停止Redis，不修改配置和数据。实验17已经完成RDB验证，正常停止服务不会清空业务键。

### 步骤1：记录故障前状态

```bash
systemctl is-active redis
```

预期为`active`。如果实验开始时就不正常，先恢复基线。

### 步骤2：停止Redis

```bash
sudo systemctl stop redis
```

### 步骤3：确认服务停止

```bash
systemctl is-active redis
```

预期返回`inactive`，该命令本身返回非0是正常故障证据。

### 步骤4：确认6379消失

```bash
ss -lntH | grep ':6379$'
```

没有输出是预期故障现象。

### 步骤5：运行巡检并保存故障日志

```bash
./scripts/server-health.sh > ~/m1-project/logs/health-fault.log 2>&1
```

### 步骤6：立即保存故障退出码

```bash
printf '%s\n' "$?" > ~/m1-project/evidence/lab19-fault-exit.txt
```

### 步骤7：查看故障日志

```bash
cat ~/m1-project/logs/health-fault.log
```

应至少看到Redis服务和6379端口两项`[CRIT]`。其他检查仍应继续执行。

### 步骤8：查看故障退出码

```bash
cat ~/m1-project/evidence/lab19-fault-exit.txt
```

预期为2。

## 十五、任务十一：恢复Redis并回归验证

### 步骤1：启动Redis

```bash
sudo systemctl start redis
```

### 步骤2：确认服务恢复

```bash
systemctl is-active redis
```

预期为`active`。

### 步骤3：确认端口恢复

```bash
ss -lntH | grep ':6379$'
```

### 步骤4：运行恢复后巡检

```bash
./scripts/server-health.sh > ~/m1-project/logs/health-recovered.log 2>&1
```

### 步骤5：立即保存恢复后退出码

```bash
printf '%s\n' "$?" > ~/m1-project/evidence/lab19-recovered-exit.txt
```

### 步骤6：查看恢复日志

```bash
cat ~/m1-project/logs/health-recovered.log
```

### 步骤7：查看恢复退出码

```bash
cat ~/m1-project/evidence/lab19-recovered-exit.txt
```

资源低于警告阈值时预期恢复为0；如果为1，应只剩资源WARN，不能再出现Redis或6379的CRITICAL。

### 步骤8：检查实验17的Redis数据仍存在

```bash
redis-cli
```

在Redis客户端中交互认证：

```text
AUTH <实验17设置的密码>
```

读取持久化测试键：

```text
GET persistence:check
```

预期返回`course-data`。退出客户端：

```text
EXIT
```

## 十六、任务十二：编写使用说明

### 步骤1：创建说明文件

```bash
vim docs/server-health.md
```

输入：

```markdown
# 服务器巡检脚本说明

## 用途

脚本运行在rocky-server，检查系统资源、MySQL、MongoDB、Redis、SSH、本机监听端口和rocky-web健康页。

## 使用

执行：`./scripts/server-health.sh`

退出码：0表示正常，1表示资源警告，2表示严重异常。

## 安全边界

脚本只检查，不自动重启服务，不修改网络或防火墙，不保存数据库密码。

## 验证

先使用`bash -n`检查语法，再分别完成正常、Redis停止和Redis恢复测试。
```

### 步骤2：查看说明

```bash
sed -n '1,100p' docs/server-health.md
```

## 十七、任务十三：审查并提交Git

### 步骤1：查看仓库状态

```bash
git status --short --ignored
```

应看到脚本和说明文档待提交，不应看到`~/m1-project/logs`中的日志进入仓库。

### 步骤2：查看脚本差异

```bash
git diff -- scripts/server-health.sh
```

新文件尚未跟踪时，普通`git diff`可能不显示其内容，应结合`git status`，暂存后使用`git diff --cached`审查。

### 步骤3：精确暂存脚本

```bash
git add scripts/server-health.sh
```

### 步骤4：精确暂存说明

```bash
git add docs/server-health.md
```

### 步骤5：审查即将提交的内容

```bash
git diff --cached
```

确认没有密码、日志、私钥或数据库转储。

### 步骤6：提交脚本

```bash
git commit -m "feat: add server health check script"
```

### 步骤7：推送到实验裸仓库

```bash
git push origin main
```

### 步骤8：查看提交历史

```bash
git log --oneline --decorate -n 6
```

### 步骤9：确认仓库干净

```bash
git status --short
```

## 十八、任务十四：形成最终证据

### 步骤1：保存语法检查结果

```bash
bash -n scripts/server-health.sh
```

### 步骤2：立即保存语法退出码

```bash
printf '%s\n' "$?" > ~/m1-project/evidence/lab19-syntax-exit.txt
```

### 步骤3：保存脚本权限

```bash
ls -l scripts/server-health.sh > ~/m1-project/evidence/lab19-script-mode.txt
```

### 步骤4：保存Git状态

```bash
git status --short --branch > ~/m1-project/evidence/lab19-git-status.txt
```

### 步骤5：保存最近提交

```bash
git log --oneline -n 6 > ~/m1-project/evidence/lab19-git-history.txt
```

### 步骤6：检查所有退出码证据

```bash
ls -l ~/m1-project/evidence/lab19-*-exit.txt
```

### 步骤7：并排查看正常、故障和恢复退出码

```bash
paste ~/m1-project/evidence/lab19-normal-exit.txt ~/m1-project/evidence/lab19-fault-exit.txt ~/m1-project/evidence/lab19-recovered-exit.txt
```

典型结果为`0  2  0`。如果恢复结果为1，应能从日志指出具体WARN；不得仍包含Redis故障。

## 十九、项目验收

### 1. 构建过程

- [ ] 单条巡检命令在写脚本前已经验证。
- [ ] 脚本经过7次小迭代，不是一次粘贴后直接运行。
- [ ] 每个迭代完成后都执行了`bash -n`和实际运行。
- [ ] 能指出函数定义区、配置区和执行区。

### 2. 脚本功能

- [ ] 输出时间、主机、内核和负载信息。
- [ ] 检查根分区和可用内存阈值。
- [ ] 检查4项本机服务和4个TCP端口。
- [ ] 访问`rocky-web`健康页。
- [ ] 不检查本机不存在的Nginx服务。
- [ ] 正确累计最高严重程度。

### 3. 异常与恢复

- [ ] Redis停止后仍完成其他检查。
- [ ] 故障日志包含Redis服务和6379端口CRITICAL。
- [ ] `lab19-fault-exit.txt`为2。
- [ ] Redis恢复后不再出现对应CRITICAL。
- [ ] `persistence:check`数据仍可读取。

### 4. 安全与版本

- [ ] 脚本只读，不自动修改系统。
- [ ] 脚本、日志和Git中没有密码。
- [ ] 日志与退出码证据位于仓库外。
- [ ] 脚本和说明已经形成目的明确的Git提交。

## 二十、提交材料

1. `scripts/server-health.sh`；
2. `docs/server-health.md`；
3. `health-normal.log`、`health-fault.log`和`health-recovered.log`；
4. `lab19-normal-exit.txt`；
5. `lab19-fault-exit.txt`；
6. `lab19-recovered-exit.txt`；
7. 语法、权限和Git证据文件；
8. 一份脚本结构说明，能够解释每个函数的输入、判断和输出。

## 二十一、常见问题与排查

### 1. Permission denied

查看权限：

```bash
ls -l scripts/server-health.sh
```

重新设置：

```bash
chmod 750 scripts/server-health.sh
```

### 2. bad interpreter或出现^M

查看文件类型：

```bash
file scripts/server-health.sh
```

如果由Windows换行导致，转换后重新检查：

```bash
sed -i 's/\r$//' scripts/server-health.sh
```

```bash
bash -n scripts/server-health.sh
```

### 3. unbound variable

`set -u`发现了未定义变量。检查变量名称是否拼错、是否在使用前赋值，以及可选位置参数是否使用了默认值。不要直接删除`set -u`掩盖错误。

### 4. 某服务始终显示失败

确认实际单元名：

```bash
systemctl list-unit-files | grep -E 'mysql|mongo|redis|ssh'
```

如果对应实验使用了不同服务名，应修改数组为真实名称；如果服务没有安装，应回到对应实验完成部署。

### 5. 端口实际存在但脚本报告失败

查看脚本实际解析的字段：

```bash
ss -lntH | awk '{print $4}'
```

确认监听地址最后是否为`:端口号`，并检查`PORTS`数组是否误写。

### 6. Web健康检查失败

先检查名称解析：

```bash
getent hosts rocky-web
```

再手工请求：

```bash
curl --verbose --max-time 3 -H 'Host: techcorp.test' http://rocky-web/health
```

根据结果检查网络、Nginx、虚拟主机和健康页，不要删除Web检查来换取退出码0。

### 7. 恢复Redis后仍返回2

查看恢复日志中的每一条`[CRIT]`。可能还有其他服务、端口或Web故障。脚本的价值就是显示多个检查结果，不能只看最后一个数字。

### 8. 正常环境返回1

查看`[WARN]`。如果资源确实达到阈值，应记录现象并分析；如果阈值不适合当前教学环境，应在说明中给出调整依据，而不是任意修改数字。

## 二十二、独立实践：验证WARN路径

先确保脚本已经提交且工作区干净。

### 步骤1：查看当前根分区使用率

```bash
df -P /
```

### 步骤2：临时把DISK_WARN改为1

```bash
vim scripts/server-health.sh
```

只把`DISK_WARN=90`改为`DISK_WARN=1`，其他内容保持不变。

### 步骤3：检查差异

```bash
git diff -- scripts/server-health.sh
```

### 步骤4：检查语法

```bash
bash -n scripts/server-health.sh
```

### 步骤5：执行WARN测试

```bash
./scripts/server-health.sh > ~/m1-project/logs/health-warn.log 2>&1
```

### 步骤6：立即保存退出码

```bash
printf '%s\n' "$?" > ~/m1-project/evidence/lab19-warn-exit.txt
```

预期退出码为1，前提是没有其他CRITICAL故障。

### 步骤7：恢复已提交版本

```bash
git restore scripts/server-health.sh
```

### 步骤8：确认阈值恢复

```bash
grep '^DISK_WARN=90$' scripts/server-health.sh
```

### 步骤9：再次检查语法和仓库状态

```bash
bash -n scripts/server-health.sh
```

```bash
git status --short
```

## 二十三、环境保留

保留以下成果供实验20使用：

- `~/m1-project/git-lab/scripts/server-health.sh`；
- `~/m1-project/git-lab/docs/server-health.md`；
- 脚本的Git提交和`origin/main`；
- 正常、故障、恢复日志；
- `lab19-fault-exit.txt`和`lab19-recovered-exit.txt`等退出码证据；
- MySQL、MongoDB、Redis、SSH和`rocky-web`恢复到正常状态。

实验20会在`rocky-server`增加`techcorp-api`服务和5000端口。届时应修改`SERVICES`与`PORTS`数组、重新测试并形成新的Git提交，不能重新编写一套无关脚本。

实验19验收完成后建立或更新`Linux-L3`快照。机房还原时从该快照继续实验20。

## 二十四、官方参考

- [GNU Bash参考手册](https://www.gnu.org/software/bash/manual/)
- [Bash条件表达式](https://www.gnu.org/software/bash/manual/html_node/Bash-Conditional-Expressions.html)
- [Bash数组](https://www.gnu.org/software/bash/manual/html_node/Arrays.html)
- [GNU Coreutils：标准输出](https://www.gnu.org/software/coreutils/manual/html_node/Standard-output.html)
- [ShellCheck](https://www.shellcheck.net/)
