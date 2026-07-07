#!/usr/bin/env python3
"""Generate five detailed module XMind maps from the final course sources."""

from __future__ import annotations

import base64
import json
import re
import uuid
import zipfile
from collections import defaultdict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "01-unit-index.md"
SCHEDULE_FILE = BASE_DIR / "04-18周课程进度表.md"
THEORY_FILE = BASE_DIR / "14-课堂实施与理论讲授指南.md"
OUTPUT_DIR = BASE_DIR / "xmind-modules"


MODULES = [
    {
        "id": "M1", "name": "Linux基础运维", "units": (1, 12), "hours": 24,
        "weeks": "第1-3周", "course": "Linux操作系统",
        "goal": "能够安装、操作和管理一台Linux服务器，建立命令、文件、身份、权限、软件、服务、日志和资源之间的系统视图。",
        "principles": [
            "Linux层次：硬件→内核→系统调用→Shell/系统服务→应用",
            "对象主线：文件与inode、用户与UID/GID、进程与PID、服务与Unit、磁盘与挂载点",
            "管理闭环：查看现状→修改配置→验证结果→查看日志→保留回退",
            "双系统对照：Rocky Linux 9为主线，Ubuntu Server 22.04 LTS用于apt/dnf、路径和服务差异对比",
        ],
        "troubleshooting": "命令/路径→用户身份→文件权限→软件包→服务状态→journal日志→CPU/内存/磁盘",
    },
    {
        "id": "M2", "name": "网络、远程管理与基础防护", "units": (13, 24), "hours": 24,
        "weeks": "第4-6周", "course": "Linux操作系统",
        "goal": "能够配置Linux服务器网络和SSH入口，实施最小防火墙与SELinux防护，并按分层证据完成网络排障。",
        "principles": [
            "通信链：网卡→IP/掩码→路由/网关→DNS→TCP/UDP→端口→应用协议",
            "远程管理链：SSH客户端→网络→sshd监听→认证→授权→审计日志",
            "基础防护分层：文件权限/DAC→sudo授权→firewalld包过滤→SELinux/MAC→应用自身认证",
            "验证原则：本机、同网段、跨网段和应用层分别验证，不能只依赖ping",
        ],
        "troubleshooting": "VM/网卡→IP→路由→DNS→进程→监听端口→firewalld→SELinux→应用日志",
    },
    {
        "id": "M3", "name": "企业服务部署与Linux阶段项目", "units": (25, 36), "hours": 24,
        "weeks": "第7-9周", "course": "Linux操作系统",
        "goal": "以Nginx为Web重点，完成数据库、Redis、Git和Shell运维集成，交付可验证、可排障、可恢复的Linux服务项目。",
        "principles": [
            "请求链：客户端→Nginx静态/反向代理→Python应用→MariaDB/Redis",
            "服务上线闭环：安装→配置→语法检查→启动/重载→端口→访问→日志→安全",
            "数据可靠性：最小权限、监听范围、持久化、备份、恢复验证和RPO/RTO认知",
            "脚本接口：标准输出/错误输出、退出码、日志、幂等，为Paramiko/Ansible/Fabric提供单机能力",
        ],
        "troubleshooting": "客户端请求→DNS/端口→Nginx配置与日志→上游应用→数据库/Redis连接→权限/防火墙/SELinux",
    },
    {
        "id": "M4", "name": "虚拟化与多机环境", "units": (37, 52), "hours": 32,
        "weeks": "第10-13周", "course": "虚拟化容器技术",
        "goal": "能够规划、搭建、管理、排障和归档三机虚拟化环境，为自动化运维及大二下综合实训提供可恢复底座。",
        "principles": [
            "虚拟化层次：物理硬件→Hypervisor→虚拟CPU/内存/磁盘/网卡→客户机操作系统",
            "虚拟网络：虚拟网卡→虚拟交换机→NAT/桥接/仅主机→物理网络",
            "环境标准化：模板→克隆→唯一身份→IP规划→SSH入口→主机清单→服务验证",
            "交付不是复制目录：快照用于回退，OVA用于迁移，配置仓库和数据备份用于可审计恢复",
        ],
        "troubleshooting": "宿主VT/资源→VMware状态→虚拟网卡/VMnet→客户机IP/路由→SSH→跨主机端口→服务日志",
    },
    {
        "id": "M5", "name": "Docker容器化与综合项目", "units": (53, 72), "hours": 40,
        "weeks": "第14-18周", "course": "虚拟化容器技术",
        "goal": "能够使用Docker、Dockerfile和Compose交付多服务应用，处理镜像、端口、数据、网络、健康与资源故障，并体验K8s基本操作。",
        "principles": [
            "Docker架构：Client→Daemon→containerd/runc→容器，Registry负责镜像分发",
            "隔离与限制：namespace提供视图隔离，cgroup提供CPU/内存等资源控制",
            "交付链：源代码→Dockerfile→镜像→Registry/离线包→容器→Compose多服务→验收",
            "运行闭环：状态、日志、端口、卷、网络、healthcheck、资源限制、备份恢复",
            "K8s边界：本课程只做kubectl与应用对象体验，集群、网络、存储和调度留给《云计算应用》",
        ],
        "troubleshooting": "Docker daemon→镜像→容器状态/退出码→logs/inspect→端口→卷/SELinux→网络/DNS→健康检查→资源/OOM",
    },
]


COMMANDS: dict[int, list[str]] = {
    1: ["cat /etc/os-release", "uname -r", "uname -m", "hostnamectl", "whoami && id"],
    2: ["lscpu", "free -h", "lsblk", "ip -br addr", "sudo systemctl status open-vm-tools"],
    3: ["pwd；ls -lah；cd", "man COMMAND；COMMAND --help", "history；Ctrl+R；Tab补全", "type COMMAND；which COMMAND", "echo $?"],
    4: ["mkdir -p；touch", "cp -a；mv；rm -i", "路径：绝对路径/相对路径/./../~", "通配符：* ? [] {}"],
    5: ["cat；less；head；tail -f", "find PATH -name/-type/-size/-mtime", "which；whereis", "ln；ln -s；ls -li"],
    6: ["vim FILE", "tar -czf backup.tar.gz DIR", "tar -tzf backup.tar.gz", "tar -xzf backup.tar.gz -C DIR", "diff -ru SOURCE RESTORE"],
    7: ["useradd；usermod；userdel", "groupadd；gpasswd", "passwd；chage", "id；groups；getent passwd/group"],
    8: ["ls -l；stat", "chmod 640 FILE；chmod u+x FILE", "chown USER:GROUP FILE", "umask", "getfacl；setfacl（拓展）"],
    9: ["sudo -l", "sudo COMMAND", "sudo visudo", "usermod -aG wheel USER", "journalctl _COMM=sudo"],
    10: ["dnf repolist/search/info/install/remove", "rpm -q/-ql/-qf", "apt update/install/remove；apt-cache search", "dpkg -l/-L/-S", "备份并切换清华/阿里镜像源"],
    11: ["systemctl status/start/stop/restart/reload", "systemctl enable/disable/is-active/is-enabled", "systemctl cat UNIT", "journalctl -u UNIT -n 50 -f"],
    12: ["top；uptime；nproc", "free -h", "lsblk -f；findmnt", "df -h；df -i；du -sh", "ps aux；pgrep；ss -lntup"],
    13: ["ip -br addr；ip route", "nmcli device status", "nmcli connection show/modify/up", "hostnamectl", "cat /etc/resolv.conf；resolvectl（Ubuntu）"],
    14: ["ss -lntup；ss -tan", "nc -vz HOST PORT", "lsof -i :PORT", "curl --connect-timeout 3 URL"],
    15: ["getent hosts NAME", "dig NAME；dig @DNS NAME", "nslookup NAME", "cat /etc/hosts；cat /etc/resolv.conf"],
    16: ["curl -I URL", "curl -v URL", "curl -L URL", "curl -k https://URL", "openssl s_client -connect HOST:443 -servername NAME"],
    17: ["ssh USER@HOST；ssh -v USER@HOST", "systemctl status sshd", "ss -lntp | grep :22", "journalctl -u sshd -n 50"],
    18: ["ssh-keygen -t ed25519", "ssh-copy-id USER@HOST", "chmod 700 ~/.ssh；chmod 600 ~/.ssh/authorized_keys", "ssh-add；ssh-agent（拓展）"],
    19: ["~/.ssh/config：Host/HostName/User/IdentityFile", "scp SOURCE USER@HOST:PATH", "sftp USER@HOST", "sha256sum FILE"],
    20: ["rsync -avzP SOURCE/ USER@HOST:DEST/", "rsync -avn --delete-delay（先dry-run）", "crontab -e；crontab -l", "diff -qr SOURCE RESTORE"],
    21: ["firewall-cmd --state", "firewall-cmd --get-active-zones", "firewall-cmd --list-all", "firewall-cmd --add-service=http --permanent", "ufw status（Ubuntu对照）"],
    22: ["firewall-cmd --add-port=PORT/tcp --permanent", "firewall-cmd --add-rich-rule='rule family=ipv4 source address=CIDR service name=ssh accept'", "firewall-cmd --reload", "firewall-cmd --remove-*；--list-all"],
    23: ["getenforce；sestatus", "ls -Z；ps -eZ", "restorecon -Rv PATH", "ausearch -m AVC -ts recent", "setsebool -P BOOLEAN on（按需）"],
    24: ["ip/nmcli/ping", "dig/getent", "systemctl/ss/curl", "firewall-cmd/getenforce/ausearch", "journalctl/tail"],
    25: ["dnf install -y nginx", "systemctl enable --now nginx", "nginx -t；nginx -T", "curl -I http://HOST", "tail -f /var/log/nginx/access.log"],
    26: ["server_name/root/location/proxy_pass", "nginx -t && systemctl reload nginx", "curl -H 'Host: NAME' http://IP", "curl http://HOST/api/"],
    27: ["openssl req -x509 -newkey rsa:2048 ...", "curl -vk https://HOST", "tail -f access.log error.log", "awk/grep分析状态码", "journalctl -u nginx"],
    28: ["dnf install -y mariadb-server", "systemctl enable --now mariadb", "mysql_secure_installation", "mysql -u USER -p -h HOST", "ss -lntp | grep :3306"],
    29: ["mysqldump -u USER -p DB > backup.sql", "mysql -u USER -p RESTORE_DB < backup.sql", "test -s backup.sql；grep验证", "journalctl -u mariadb"],
    30: ["systemctl enable --now redis", "redis-cli PING/SET/GET/INFO", "redis-cli -a PASSWORD", "ss -lntp | grep :6379", "grep -E 'bind|protected-mode|requirepass' redis.conf"],
    31: ["git clone；git pull", "git status；git diff", "git log --oneline --graph", "git restore FILE", ".gitignore排除.env/私钥/备份"],
    32: ["bash SCRIPT；chmod +x SCRIPT", "stdout/stderr：> >> 2>", "echo $?；exit CODE", "logger；journalctl -t TAG", "jq验证JSON（可选）"],
    33: ["git init；git status", "hostnamectl；ip -br addr", "ss -lntup；systemctl --failed", "项目任务板/验收矩阵（文档操作）"],
    34: ["nginx -t；systemctl reload nginx", "mysql连接测试；redis-cli PING", "curl -f http://HOST/api/health", "./ops-check.sh"],
    35: ["systemctl/journalctl", "ss/curl", "firewall-cmd/ausearch", "mysqldump/mysql恢复", "故障报告：现象→证据→根因→修复→验证"],
    36: ["git log --oneline", "./ops-check.sh", "curl端到端演示", "随机故障现场命令", "提交Markdown报告"],
    37: ["systemd-detect-virt", "lscpu | grep Virtualization", "lsblk；free -h", "VMware界面：宿主/虚拟硬件/客户机"],
    38: ["lscpu；free -h；lsblk", "du -sh虚拟机目录（宿主）", "资源规格表：vCPU/内存/磁盘/网卡", "VMware设置与客户机识别对照"],
    39: ["hostnamectl", "cat /etc/machine-id", "ssh-keygen -A", "VMware快照/完整克隆/链接克隆", "ip -br addr验证克隆身份"],
    40: ["Windows：ipconfig /all；Get-NetAdapter", "Linux：ip -br addr；ip route", "nmcli connection show", "VMware虚拟网络编辑器：VMnet1/VMnet8"],
    41: ["ping网关/宿主/同网段VM", "curl -I外部或内网服务", "Test-NetConnection HOST -Port PORT", "traceroute/tracepath", "连接矩阵与数据流图"],
    42: ["ipcalc CIDR（可选）", "拓扑图+IP规划表+端口矩阵", "hostname/IP/MAC/角色/依赖清单", "检查地址冲突和网段一致性"],
    43: ["hostnamectl set-hostname", "systemd-machine-id-setup", "nmcli con modify ... ipv4.method manual", "getent hosts；ping矩阵", "ssh-keygen -A"],
    44: ["ssh-keygen；ssh-copy-id", "~/.ssh/config", "ssh web hostname；ssh db hostname", "inventory.ini：主机组/ansible_host/ansible_user"],
    45: ["curl http://web-server", "mysql -h db-server -u USER -p", "redis-cli -h db-server PING", "ss -lntup", "firewall-cmd --list-all"],
    46: ["ip route/getent/ping", "nc -vz HOST PORT", "ss -lntup；systemctl status", "firewall-cmd；ausearch", "journalctl/tail服务日志"],
    47: ["egrep -c '(vmx|svm)' /proc/cpuinfo", "lsmod | grep kvm", "virsh version；virsh list --all", "systemctl status libvirtd", "条件实验：嵌套虚拟化"],
    48: ["virsh list/start/shutdown/destroy", "virsh dominfo/edit", "qemu-img info/create", "virt-install（演示/选做）"],
    49: ["virsh net-list --all", "virsh net-dumpxml default", "virsh net-start/default --autostart", "ip addr show virbr0", "bridge link（选做）"],
    50: ["ESXi Host Client/vCenter界面操作", "数据中心→集群→主机→VM层次", "模板、资源池、数据存储、vSwitch概念", "本单元无强制CLI"],
    51: ["cloud-init status；cloud-init query", "curl云元数据地址（教师演示）", "安全组规则与firewalld对照", "镜像/快照/云盘操作（演示）"],
    52: ["sha256sum OVA；sha256sum -c", "systemctl --failed；ss -lntup", "mysqldump与配置归档", "VMware导出OVA/导入恢复", "README+inventory+恢复记录"],
    53: ["docker version；docker info", "uname -r", "ps/lsns（原理观察）", "docker system info", "虚拟机与容器对比表"],
    54: ["systemctl enable --now docker", "docker pull/load/images", "docker image inspect/history", "docker tag", "docker save -o IMAGE.tar IMAGE"],
    55: ["docker run；docker ps -a", "docker logs -f", "docker exec -it", "docker inspect", "docker stop/start/restart/rm"],
    56: ["docker run nginx/mysql/redis", "docker logs SERVICE", "docker exec客户端测试", "curl/redis-cli/mysql验证", "docker inspect环境变量与挂载"],
    57: ["docker run -p HOST:CONTAINER", "docker port CONTAINER", "ss -lntp", "curl http://HOST:PORT", "127.0.0.1绑定与0.0.0.0暴露对比"],
    58: ["docker volume create/ls/inspect", "docker run -v NAME:/path", "bind mount：-v HOST:CONTAINER", "tar备份/恢复volume", "docker compose down -v风险"],
    59: ["docker network ls/create/inspect", "docker network connect/disconnect", "docker exec ping/getent hosts", "bridge/host/none", "容器名DNS"],
    60: ["docker ps -a；docker logs；docker inspect", "--health-cmd/--health-interval", "docker stats --no-stream", "--memory；--cpus", "OOMKilled/ExitCode=137/journalctl -k"],
    61: ["docker build -t NAME:TAG .", "FROM/RUN/COPY/WORKDIR/EXPOSE/CMD", "docker run IMAGE", "docker history IMAGE", "构建上下文与.dockerignore"],
    62: ["docker build多阶段构建", "USER非root", "ARG/ENV", "docker history检查敏感信息", "镜像体积与层缓存对比"],
    63: ["docker tag IMAGE REGISTRY/NAME:TAG", "docker login/push/pull（演示）", "docker save/load离线交付", "docker image inspect --format '{{.RepoDigests}}'", "SHA256校验"],
    64: ["docker compose config", "docker compose up -d", "docker compose ps/logs", "docker compose down", "YAML：services/ports/volumes/networks"],
    65: ["docker compose up -d --build", "docker compose exec SERVICE COMMAND", "docker compose logs -f SERVICE", "服务名通信", "volume/network/environment"],
    66: ["healthcheck/test/interval/retries", "depends_on.condition: service_healthy", ".env；env_file；docker compose --env-file", "docker compose config检查展开结果", "敏感配置不提交Git"],
    67: ["git clone项目", "docker compose build/up/ps/logs", "curl端到端验证", "卷持久化删除重建验证", "docker compose down清理"],
    68: ["kubectl config current-context", "kubectl get nodes/pods/deploy/svc", "kubectl apply -f；kubectl delete -f", "kubectl describe/logs/exec", "kubectl scale；kubectl rollout status/undo"],
    69: ["导入/恢复OVA；sha256sum -c", "ip/route/SSH验证", "docker/compose版本检查", "需求、拓扑、端口、数据和验收矩阵"],
    70: ["docker build/tag", "docker compose up -d --build", "docker compose ps/logs", "curl/mysql/redis端到端验证", "健康检查和数据卷"],
    71: ["docker compose ps；logs；config", "ss/curl/firewall-cmd", "docker inspect/network/volume", "备份恢复命令", "故障报告证据链"],
    72: ["docker compose up与功能演示", "随机故障现场排查", "sha256sum归档", "OVA导入恢复验证", "提交报告/inventory/配置仓库"],
}


def make_id(key: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_URL, f"module-xmind-v1:{key}").hex[:26]


def topic(title: str, children: list[dict] | None = None, *, key: str,
          folded: bool = False) -> dict:
    node: dict = {"id": make_id(key), "class": "topic", "title": title}
    if folded:
        node["branch"] = "folded"
    if children:
        node["children"] = {"attached": children}
    return node


def leaves(items: list[str], key_prefix: str) -> list[dict]:
    return [topic(item, key=f"{key_prefix}:{index}") for index, item in enumerate(items, 1)]


def parse_units() -> dict[int, tuple[str, str]]:
    result: dict[int, tuple[str, str]] = {}
    pattern = re.compile(r"^\| U(\d{2}) \| ([^|]+?) \| ([^|]+?) \|$")
    for line in INDEX_FILE.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            result[int(match.group(1))] = (match.group(2).strip(), match.group(3).strip())
    if sorted(result) != list(range(1, 73)):
        raise RuntimeError("Unit index must contain U01-U72 exactly once")
    return result


def parse_schedule() -> tuple[dict[int, str], dict[int, str]]:
    weeks: dict[int, str] = {}
    deliverables: dict[int, str] = {}
    pattern = re.compile(
        r"^\| 第(\d+)周-\d \| U(\d{2}) \| [^|]+? \| ([^|]+?) \| [^|]+? \|$"
    )
    for line in SCHEDULE_FILE.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            unit = int(match.group(2))
            weeks[unit] = f"第{match.group(1)}周"
            deliverables[unit] = match.group(3).strip()
    if sorted(weeks) != list(range(1, 73)):
        raise RuntimeError("Schedule must contain U01-U72 exactly once")
    return weeks, deliverables


def parse_theory() -> dict[int, list[str]]:
    result: dict[int, list[str]] = defaultdict(list)
    lines = THEORY_FILE.read_text(encoding="utf-8").splitlines()
    heading = re.compile(r"^### U(\d{2})(?:-U(\d{2}))?\s+(.+)$")
    current: tuple[int, int] | None = None
    section_bullets: list[str] = []

    def flush() -> None:
        nonlocal current, section_bullets
        if not current:
            return
        start, end = current
        for unit in range(start, end + 1):
            label = f"U{unit:02d}："
            specific = [b[len(label):].strip() for b in section_bullets if b.startswith(label)]
            generic = [b for b in section_bullets if not re.match(r"^U\d{2}：", b)]
            result[unit].extend(specific if specific else generic)
        current = None
        section_bullets = []

    for line in lines:
        match = heading.match(line)
        if match:
            flush()
            start = int(match.group(1))
            end = int(match.group(2) or match.group(1))
            current = (start, end)
            continue
        if current and line.startswith("- "):
            section_bullets.append(line[2:].strip())
        elif current and line.startswith("### "):
            flush()
    flush()

    missing = [unit for unit in range(1, 73) if not result[unit]]
    if missing:
        raise RuntimeError(f"Theory guide missing units: {missing}")
    return dict(result)


def split_theory(items: list[str]) -> tuple[list[str], list[str]]:
    risk_words = ("易错点", "检查问题", "安全", "风险", "强调", "边界", "故障")
    risks = [item for item in items if item.startswith(risk_words)]
    principles = [item for item in items if item not in risks]
    return principles or items, risks or ["按状态→配置→日志→验证形成证据链；禁止只凭现象猜测。"]


def build_module(module: dict, units: dict[int, tuple[str, str]], weeks: dict[int, str],
                 deliverables: dict[int, str], theory: dict[int, list[str]]) -> list[dict]:
    start, end = module["units"]
    week_nodes = []
    grouped: dict[str, list[int]] = defaultdict(list)
    for unit in range(start, end + 1):
        grouped[weeks[unit]].append(unit)

    for week, week_units in grouped.items():
        unit_nodes = []
        for unit in week_units:
            unit_id = f"U{unit:02d}"
            name, core = units[unit]
            principles, risks = split_theory(theory[unit])
            unit_nodes.append(topic(
                f"{unit_id} {name}",
                [
                    topic("学习目标与知识范围", leaves([core], f"{unit_id}:goal"), key=f"{unit_id}:goal-root"),
                    topic("原理与讲授重点", leaves(principles, f"{unit_id}:theory"), key=f"{unit_id}:theory-root", folded=True),
                    topic("关键命令/操作", leaves(COMMANDS[unit], f"{unit_id}:commands"), key=f"{unit_id}:commands-root", folded=True),
                    topic("实验/成果", leaves([deliverables[unit]], f"{unit_id}:lab"), key=f"{unit_id}:lab-root"),
                    topic("排障、安全与检查", leaves(risks, f"{unit_id}:risk"), key=f"{unit_id}:risk-root", folded=True),
                ], key=unit_id, folded=True,
            ))
        week_nodes.append(topic(week, unit_nodes, key=f"{module['id']}:{week}", folded=True))

    overview = topic("模块总览", [
        topic(f"所属课程：{module['course']}", key=f"{module['id']}:course"),
        topic(f"课时与周次：{module['hours']}学时｜{module['weeks']}", key=f"{module['id']}:hours"),
        topic(f"单元范围：U{start:02d}-U{end:02d}", key=f"{module['id']}:range"),
        topic(f"模块目标：{module['goal']}", key=f"{module['id']}:goal"),
        topic("课堂节奏：问题导入5分钟→理论20-25→演示10-15→核心实验30→独立任务15-20→复盘5", key=f"{module['id']}:flow"),
    ], key=f"{module['id']}:overview", folded=True)

    principles_node = topic(
        "模块核心原理",
        leaves(module["principles"], f"{module['id']}:principles"),
        key=f"{module['id']}:principles-root", folded=True,
    )
    troubleshooting = topic("模块排障主线", [
        topic(module["troubleshooting"], key=f"{module['id']}:troubleshooting-path"),
        topic("记录格式：现象→范围→命令与输出→判断→根因→修复→验证→预防", key=f"{module['id']}:troubleshooting-report"),
        topic("验证要求：命令不报错不等于业务正常，必须从客户端或下一层对象完成验收", key=f"{module['id']}:troubleshooting-proof"),
    ], key=f"{module['id']}:troubleshooting", folded=True)

    root = topic(
        f"{module['id']}《{module['name']}》详细知识图谱",
        [overview, principles_node, *week_nodes, troubleshooting],
        key=f"{module['id']}:root",
    )
    root["structureClass"] = "org.xmind.ui.map.clockwise"
    return [{
        "id": make_id(f"{module['id']}:sheet"),
        "class": "sheet",
        "title": f"{module['id']} {module['name']}",
        "rootTopic": root,
    }]


def write_xmind(path: Path, content: list[dict], module_id: str) -> None:
    metadata = {
        "dataStructureVersion": "2",
        "layoutEngineVersion": "3",
        "creator": {"name": "Course Module XMind Generator", "version": "1.0"},
        "activeSheetId": make_id(f"{module_id}:sheet"),
    }
    manifest = {"file-entries": {
        "content.json": {}, "metadata.json": {}, "Thumbnails/thumbnail.png": {}
    }}
    transparent_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("content.json", json.dumps(content, ensure_ascii=False, separators=(",", ":")))
        archive.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False, separators=(",", ":")))
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, separators=(",", ":")))
        archive.writestr("Thumbnails/thumbnail.png", transparent_png)


def main() -> None:
    units = parse_units()
    weeks, deliverables = parse_schedule()
    theory = parse_theory()
    if sorted(COMMANDS) != list(range(1, 73)):
        raise RuntimeError("COMMANDS must contain U01-U72 exactly once")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for module in MODULES:
        filename = f"{module['id']}-{module['name']}-详细知识图谱.xmind"
        path = OUTPUT_DIR / filename
        write_xmind(path, build_module(module, units, weeks, deliverables, theory), module["id"])
        print(path)


if __name__ == "__main__":
    main()
