# 实验19：Shell服务器巡检脚本

> 所属模块：模块三 企业服务部署与综合运维  
> 建议学时：2学时  
> 实验方式：个人  
> 对应教材：《模块三 企业服务部署与综合运维》第30章  
> 知识前置：教材第30章、实验14—18中的服务验收与Git操作\
> 状态依赖：实验14的Nginx健康页、实验15—17的三个数据服务、实验18的Git仓库及三机网络\
> 建议起点：保留实验14—18成果的当前环境\
> 项目成果：可执行的服务器巡检脚本、正常与异常测试记录、版本提交

## 一、项目情境

TechCorp的`rocky-server`上已经运行MySQL、MongoDB和Redis，`rocky-web`提供Nginx健康页。每天逐条输入命令容易遗漏，管理员希望在`rocky-server`用一个Shell脚本检查本机资源、服务和监听端口，同时验证外部Web入口，并通过退出码让其他程序判断巡检结果。

本实验强调“把已经会做的检查固化为脚本”，不追求复杂Shell语法。脚本只采集和判断，不自动重启服务，不修改防火墙，也不保存数据库密码。

## 二、实验目标

### 1. 知识目标

1. 说明Shebang、变量、条件判断、函数和循环的作用。
2. 说明标准输出、标准错误和退出码的区别。
3. 理解巡检、监控和自动修复不是同一件事。

### 2. 能力目标

1. 编写并执行Bash巡检脚本。
2. 检查根分区、可用内存、系统负载、systemd服务和TCP端口。
3. 使用0、1、2退出码表示正常、警告和严重异常。
4. 通过主动制造一个受控故障验证脚本。
5. 将脚本和说明提交到Git仓库。

### 3. 素质目标

1. 脚本默认只读，自动化操作遵循最小影响原则。
2. 输出包含时间、主机和检查对象，便于追溯。
3. 测试故障后恢复环境并再次验证。

## 三、知识准备

```text
采集系统状态
      ↓
与阈值或期望状态比较
      ↓
输出 [OK] / [WARN] / [CRIT]
      ↓
返回 0 / 1 / 2
      ↓
人工或上层系统决定是否处理
```

| 退出码 | 含义 | 本实验处理方式 |
|---:|---|---|
| 0 | 全部正常 | 保存巡检记录 |
| 1 | 存在警告 | 分析容量或负载趋势 |
| 2 | 存在严重异常 | 检查服务、端口和日志 |

在Shell中，退出码0表示命令成功，非0表示不同类型的失败。脚本自己的退出码应当有明确约定。

## 四、实验环境

- 在`rocky-server`完成巡检脚本编写与异常验证。
- 脚本应能把主机名写入报告，避免把`rocky-web`结果误作数据库服务器结果。

- 已完成实验14—17，相关服务已安装。
- Bash、`systemctl`、`ss`、`df`、`awk`和`curl`可用。
- 项目目录：`~/m1-project/git-lab`。
- 如果某服务未安装，应先在对应实验中完成安装，不在本实验中跳过验收。

## 五、项目任务

1. 设计巡检对象、阈值和退出码。
2. 编写`server-health.sh`。
3. 检查语法、权限和正常输出。
4. 停止Redis制造受控故障，验证严重异常退出码。
5. 恢复Redis并再次验证。
6. 将脚本和使用说明提交Git。

## 六、实验步骤

### 任务一：确认巡检基线

```bash
test "$(hostnamectl --static)" = 'rocky-server' && echo HOST_PASS || echo HOST_FAIL
```

```bash
mkdir -p ~/m1-project/git-lab/scripts ~/m1-project/logs ~/m1-project/evidence
for service in mysqld mongod redis sshd; do
    printf '%-10s %s\n' "$service" "$(systemctl is-active "$service" 2>/dev/null || true)"
done
sudo ss -lntp | grep -E ':(22|3306|27017|6379)\b' || true
curl --fail -H 'Host: techcorp.test' http://rocky-web/health
df -h /
free -h
```

> **验收点**：记录当前服务和端口基线。若服务名与课程环境不同，应在脚本数组中使用实际服务名。

### 任务二：编写巡检脚本

```bash
cd ~/m1-project/git-lab
vim scripts/server-health.sh
```

输入以下完整内容：

```bash
#!/usr/bin/env bash

# TechCorp Linux服务器巡检脚本
# 退出码：0=正常，1=警告，2=严重异常

set -u

DISK_WARN=80
MEM_AVAILABLE_WARN=15
LOAD_WARN_FACTOR=2
STATUS=0

SERVICES=(mysqld mongod redis sshd)
PORTS=(22 3306 27017 6379)

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

check_memory() {
    local total_kb available_kb available_pct
    total_kb=$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)
    available_kb=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo)

    if [[ -z "$total_kb" || -z "$available_kb" || "$total_kb" -eq 0 ]]; then
        crit '无法读取内存信息'
        return
    fi

    available_pct=$(( available_kb * 100 / total_kb ))
    if (( available_pct <= MEM_AVAILABLE_WARN )); then
        warn "可用内存为${available_pct}%，阈值为${MEM_AVAILABLE_WARN}%"
    else
        ok "可用内存为${available_pct}%"
    fi
}

check_load() {
    local load1 cpu_count limit
    load1=$(awk '{print $1}' /proc/loadavg)
    cpu_count=$(getconf _NPROCESSORS_ONLN)
    limit=$(( cpu_count * LOAD_WARN_FACTOR ))

    if awk -v load="$load1" -v max="$limit" 'BEGIN {exit !(load >= max)}'; then
        warn "1分钟负载为${load1}，参考阈值为${limit}"
    else
        ok "1分钟负载为${load1}，CPU逻辑核数为${cpu_count}"
    fi
}

check_services() {
    local service state
    for service in "${SERVICES[@]}"; do
        state=$(systemctl is-active "$service" 2>/dev/null || true)
        if [[ "$state" == 'active' ]]; then
            ok "服务${service}处于active"
        else
            crit "服务${service}状态为${state:-unknown}"
        fi
    done
}

check_ports() {
    local port
    for port in "${PORTS[@]}"; do
        if ss -lntH | awk '{print $4}' | grep -Eq "(^|:|\\])${port}$"; then
            ok "TCP端口${port}正在监听"
        else
            crit "TCP端口${port}未监听"
        fi
    done
}

check_web() {
    if curl --silent --show-error --fail --max-time 3 \
        -H 'Host: techcorp.test' http://rocky-web/health >/dev/null; then
        ok 'rocky-web的Nginx健康检查返回成功'
    else
        crit 'rocky-web的Nginx健康检查失败'
    fi
}

main() {
    printf '=== TechCorp Server Health Check ===\n'
    printf 'time=%s\n' "$(date '+%F %T %z')"
    printf 'host=%s\n' "$(hostname -f 2>/dev/null || hostname)"
    printf 'kernel=%s\n' "$(uname -r)"
    printf '\n'

    check_disk
    check_memory
    check_load
    check_services
    check_ports
    check_web

    printf '\nresult_code=%d\n' "$STATUS"
    case "$STATUS" in
        0) printf 'result=OK\n' ;;
        1) printf 'result=WARN\n' ;;
        2) printf 'result=CRITICAL\n' ;;
    esac
    return "$STATUS"
}

main "$@"
```

保存退出后检查脚本：

```bash
chmod 750 scripts/server-health.sh
bash -n scripts/server-health.sh
head -n 5 scripts/server-health.sh
ls -l scripts/server-health.sh
```

`bash -n`没有输出且退出码为0，表示未发现Shell语法错误：

```bash
echo $?
```

> **验收点**：脚本语法检查通过，只有所有者和同组用户能够执行。

### 任务三：执行正常巡检

实验14已在`rocky-web`配置`/health`。先从`rocky-server`手工验证该地址，再执行巡检：

```bash
getent hosts rocky-web
curl --fail -H 'Host: techcorp.test' http://rocky-web/health
```

```bash
cd ~/m1-project/git-lab
./scripts/server-health.sh > ~/m1-project/logs/health-normal.log 2>&1
RESULT=$?
cat ~/m1-project/logs/health-normal.log
printf 'exit_code=%s\n' "$RESULT"
```

如果所有服务和端口正常，预期退出码为0。如果出现1或2，不要为了得到0而删掉检查项，应根据输出排查实际问题。

查看标准输出和标准错误的区别：

```bash
./scripts/server-health.sh \
    > ~/m1-project/logs/health.stdout.log \
    2> ~/m1-project/logs/health.stderr.log
printf 'exit_code=%s\n' "$?"
wc -l ~/m1-project/logs/health.stdout.log ~/m1-project/logs/health.stderr.log
```

脚本把`[CRIT]`写入标准错误，普通信息写入标准输出。

### 任务四：制造并验证受控故障

本任务只在`rocky-server`停止Redis，完成后必须立即恢复。先保存原状态：

```bash
REDIS_BEFORE=$(systemctl is-active redis 2>/dev/null || true)
printf 'redis_before=%s\n' "$REDIS_BEFORE"
sudo systemctl stop redis
systemctl is-active redis || true
```

执行脚本并单独保存退出码：

```bash
./scripts/server-health.sh > ~/m1-project/logs/health-fault.log 2>&1
FAULT_CODE=$?
printf '%s\n' "$FAULT_CODE" > ~/m1-project/evidence/lab19-fault-exit.txt
cat ~/m1-project/logs/health-fault.log
printf 'fault_exit_code=%s\n' "$FAULT_CODE"
```

预期至少出现：

- Redis服务状态为严重异常；
- 6379端口未监听；
- `rocky-web`健康检查仍成功，证明故障影响范围不是全部服务；
- 最终退出码为2。

立即恢复并再次验证：

```bash
sudo systemctl start redis
systemctl is-active redis
sudo ss -lntp | grep ':6379'
curl --fail -H 'Host: techcorp.test' http://rocky-web/health
./scripts/server-health.sh > ~/m1-project/logs/health-recovered.log 2>&1
RECOVERED_CODE=$?
printf '%s\n' "$RECOVERED_CODE" > ~/m1-project/evidence/lab19-recovered-exit.txt
cat ~/m1-project/logs/health-recovered.log
printf 'recovered_exit_code=%s\n' "$RECOVERED_CODE"
```

> **验收点**：异常时退出码为2；恢复后Redis、6379端口和远程Web健康检查均正常。

### 任务五：为脚本编写说明并提交Git

````bash
cd ~/m1-project/git-lab
cat > docs/server-health.md <<'EOF'
# 服务器巡检脚本说明

## 用途

检查`rocky-server`的根分区、可用内存、系统负载、MySQL/MongoDB/Redis/SSH服务及常用端口，并访问`rocky-web`健康页。

## 使用

```bash
./scripts/server-health.sh
echo $?
```

退出码：0表示正常，1表示警告，2表示严重异常。

## 边界

脚本只检查，不自动重启服务，不修改配置，不保存数据库密码。
EOF

git status --short
git diff -- scripts/server-health.sh docs/server-health.md
git add scripts/server-health.sh docs/server-health.md
git diff --cached
git commit -m "feat: add server health check script"
git push origin main
git log --oneline --decorate -n 5
````

日志目录已在实验18的`.gitignore`中排除，不应被提交。

### 任务六：保存实验结果

```bash
FAULT_CODE=$(cat ~/m1-project/evidence/lab19-fault-exit.txt)
RECOVERED_CODE=$(cat ~/m1-project/evidence/lab19-recovered-exit.txt)
{
    printf '=== syntax ===\n'
    bash -n ~/m1-project/git-lab/scripts/server-health.sh
    printf 'syntax_exit=%s\n' "$?"
    printf '\n=== script ===\n'
    ls -l ~/m1-project/git-lab/scripts/server-health.sh
    printf '\n=== git ===\n'
    git -C ~/m1-project/git-lab status --short --branch
    git -C ~/m1-project/git-lab log --oneline -n 5
    printf '\n=== test exit codes ===\n'
    printf 'fault=%s recovered=%s\n' "$FAULT_CODE" "$RECOVERED_CODE"
} | tee ~/m1-project/evidence/lab19-shell-final.txt
```

## 七、脚本阅读提示

### 1. 为什么使用函数

函数把磁盘、内存、服务、端口等检查分开。某项规则变化时，只需修改对应函数，也便于定位错误。

### 2. 为什么变量名使用大写

本脚本用大写表示全局阈值和状态，用小写表示函数内的局部变量。这是可读性约定，不是Shell强制语法。

### 3. 为什么命令后有`|| true`

`systemctl is-active`在服务不正常时本来就返回非0。这里需要读取它的文本状态并继续完成全部检查，因此在明确位置容纳非0结果，而不是让脚本提前退出。

### 4. 为什么不启用`set -e`

巡检脚本的目的正是收集失败项。若任意检查失败就立即退出，后续故障可能无法被发现。本脚本使用自己的状态累计逻辑。

### 5. 为什么端口正常仍不能证明业务正常

端口监听只能说明进程正在接收连接。`curl /health`进一步检查HTTP请求是否能够得到成功响应；数据库还需使用对应客户端进行认证和读写验证。

## 八、常见故障

### 故障1：`Permission denied`

```bash
ls -l scripts/server-health.sh
chmod 750 scripts/server-health.sh
```

### 故障2：`bad interpreter`或出现`^M`

文件可能使用Windows换行。检查并转换：

```bash
file scripts/server-health.sh
sed -i 's/\r$//' scripts/server-health.sh
bash -n scripts/server-health.sh
```

### 故障3：某服务显示unknown

```bash
systemctl list-unit-files | grep -E 'mysql|mongo|redis|ssh'
```

确认实际单元名，再修改`SERVICES`数组。不要仅为了通过检查而删除业务必需项。

### 故障4：端口在监听但脚本报告未监听

```bash
ss -lntH
```

检查当前系统输出格式和脚本正则。IPv4可能显示`127.0.0.1:3306`，IPv6可能显示`[::1]:6379`。

### 故障5：正常环境仍返回1

查看`[WARN]`行。资源使用率达到阈值并不等于命令失败，应结合持续时间和业务影响判断，而不是随意提高阈值。

## 九、项目验收

| 项目 | 分值 | 评价要点 |
|---|---:|---|
| 脚本结构 | 20 | Shebang、变量、函数、循环和主函数清楚 |
| 系统检查 | 20 | 磁盘、内存和负载判断正确 |
| 服务与端口 | 20 | 四项本机服务、四个端口及`rocky-web`健康页均被检查 |
| 输出与退出码 | 15 | OK/WARN/CRIT清楚，0/1/2符合约定 |
| 故障验证 | 15 | 有异常、恢复和退出码证据 |
| 文档与版本 | 10 | 使用说明完整，Git提交合理，无日志和秘密 |

## 十、独立练习

1. 将磁盘阈值临时改为当前使用率以下，验证WARN和退出码1，然后恢复原值。
2. 增加对`chronyd`服务的检查。
3. 思考：如果脚本加入自动重启，可能带来哪些误操作和故障掩盖风险？

## 十一、实验总结

1. 巡检脚本为什么不应默认自动修复？
2. 标准输出、标准错误和退出码分别服务于谁？
3. 为什么既要检查服务，又要检查端口和应用健康页？
4. 哪些值适合做阈值，阈值应如何根据环境调整？
