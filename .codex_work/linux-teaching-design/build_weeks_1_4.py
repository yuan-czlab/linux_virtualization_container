from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree


ROOT = Path("/Users/yuan/projects/linux_virtualization_container")
DOCX = ROOT / "教学资料/25级高职计算机应用技术专业《Linux操作系统》-教学设计-第1-4周.docx"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"
XML_NS = "http://www.w3.org/XML/1998/namespace"


def join_items(items: list[str]) -> str:
    return "；".join(items)


def make_objectives(s: dict) -> list[str]:
    return [
        f"1.文化基础知识：{s['culture']}。",
        f"2.专业基础知识：{s['knowledge']}。",
        "3.通用能力：能够从任务要求中提取操作对象、前置条件和验收标准，并用清晰的操作记录表达判断依据。",
        f"4.专业能力：{s['ability']}。",
        f"5.思想政治素质：{s['ideology']}。",
        "6.文化素质：理解开源协作、技术规范和知识产权之间的关系，能够尊重社区规则并正确引用学习资料。",
        "7.身心素质：在连续操作和故障处理过程中保持耐心，遇到异常先观察、再判断，形成稳定的学习节奏。",
        f"8.职业素质：{s['vocational']}。",
    ]


def make_design(s: dict) -> list[str]:
    return [
        f"1.任务导入：{s['intro']}",
        f"2.知识准备：围绕{join_items(s['key_points'])}建立本次课的知识框架。",
        f"3.教师示范：{join_items(s['demos'])}。",
        f"4.学生实践：{join_items(s['tasks'])}。",
        f"5.思政融入：{s['values_detail']}",
        f"6.排障与验收：{s['verification']}。",
        f"7.课堂小结与作业：归纳关键对象、命令和验证方法；{s['homework']}。",
    ]


COMMAND_GUIDES = {
    (1, 1): {
        "check": ["lscpu | grep -E 'Virtualization|Model name'", "free -h", "lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS", "sha256sum Rocky-9*.iso Ubuntu-22.04*.iso"],
        "demo1": ["uname -r", "cat /etc/os-release", "hostnamectl", "ip -br address"],
        "demo2": ["ip route", "df -hT", "timedatectl", "sudo shutdown -h now"],
        "practice": ["uname -r", "cat /etc/os-release", "ip -br address", "df -hT"],
        "verify": ["lscpu | grep Virtualization", "sha256sum <镜像文件>", "cat /etc/os-release"],
    },
    (1, 2): {
        "check": ["cat /etc/os-release", "hostnamectl", "ip -br address", "ip route"],
        "demo1": ["lsblk -f", "df -hT", "timedatectl status", "ping -c 4 <网关IP>"],
        "demo2": ["man ls", "ls --help | less", "type cd", "history | tail"],
        "practice": ["pwd", "ls -lah", "mkdir -p ~/linux-lab/{conf,logs,backup,docs}", "touch ~/linux-lab/docs/readme.txt", "find ~/linux-lab -maxdepth 2 -print"],
        "verify": ["hostnamectl --static", "ip -br address", "ip route", "find ~/linux-lab -maxdepth 2 -print"],
    },
    (1, 3): {
        "check": ["pwd", "ls -lah", "find ~/linux-lab -maxdepth 2 -print"],
        "demo1": ["mkdir -p project/{conf,logs,backup,docs}", "touch project/conf/app.conf", "cp -av project/conf/app.conf project/backup/", "mv project/docs project/manuals"],
        "demo2": ["cat -n project/conf/app.conf", "head -n 5 <文件>", "tail -n 10 <日志>", "less <长文本文件>"],
        "practice": ["pwd && ls -lah", "cp -a <源目录> <目标目录>", "mv <原文件名> <新文件名>", "rm -i <教师指定测试文件>"],
        "verify": ["find project -maxdepth 2 -type f -printf '%p\\n'", "stat <指定文件>", "history | tail -n 20"],
    },
    (2, 1): {
        "check": ["pwd", "find ~/linux-lab -maxdepth 2 -type f", "which vim", "vim --version | head"],
        "demo1": ["vim <文件>", "find /etc -maxdepth 2 -name '*.conf' 2>/dev/null", "which bash", "type cd"],
        "demo2": ["ln <源文件> <硬链接>", "ln -s <源路径> <软链接>", "ls -li <源文件> <硬链接>", "readlink -f <软链接>"],
        "practice": ["tar -czf config-backup.tar.gz project/conf", "tar -tzf config-backup.tar.gz", "mkdir restore && tar -xzf config-backup.tar.gz -C restore"],
        "verify": ["stat <源文件> <硬链接>", "find restore -type f -print", "diff -r project/conf restore/project/conf"],
    },
    (2, 2): {
        "check": ["whoami", "id", "getent passwd | tail", "getent group | tail"],
        "demo1": ["sudo groupadd project", "sudo useradd -m -s /bin/bash trainee1", "sudo usermod -aG project trainee1", "sudo passwd trainee1"],
        "demo2": ["ls -ld project", "sudo chown -R trainee1:project project", "chmod 750 project", "umask 027"],
        "practice": ["namei -l project/conf/app.conf", "sudo -l -U trainee1", "sudo visudo -c", "su - trainee1"],
        "verify": ["id trainee1", "getent group project", "stat -c '%U %G %A %n' project", "sudo -u trainee1 test -r project/conf/app.conf; echo $?"],
    },
    (2, 3): {
        "check": ["cat /etc/os-release", "rpm -q bash", "dpkg -l bash 2>/dev/null | tail -n 1"],
        "demo1": ["dnf repolist", "dnf search tree", "dnf info tree", "sudo dnf install -y tree"],
        "demo2": ["sudo apt update", "apt search tree", "apt show tree", "sudo apt install -y tree"],
        "practice": ["rpm -qi tree", "dpkg -L tree", "dnf history list | head", "grep -RE '^(baseurl|mirrorlist)' /etc/yum.repos.d/"],
        "verify": ["command -v tree", "tree --version", "rpm -V tree 2>/dev/null || true", "apt-cache policy tree 2>/dev/null"],
    },
    (3, 1): {
        "check": ["systemctl is-system-running", "systemctl --failed", "systemctl status sshd --no-pager"],
        "demo1": ["systemctl cat sshd", "systemctl status sshd --no-pager", "sudo systemctl restart sshd", "systemctl is-active sshd"],
        "demo2": ["sudo systemctl enable --now crond", "systemctl is-enabled crond", "journalctl -u sshd -n 30 --no-pager", "journalctl -p err -b --no-pager"],
        "practice": ["systemctl list-units --type=service --state=running", "systemctl show sshd -p ActiveState -p SubState", "journalctl --since '-10 min'"],
        "verify": ["systemctl is-active <服务名>", "systemctl is-enabled <服务名>", "journalctl -u <服务名> -n 20 --no-pager"],
    },
    (3, 2): {
        "check": ["uptime", "free -h", "df -hT", "ip -br address"],
        "demo1": ["top -b -n 1 | head -n 20", "ps aux --sort=-%mem | head", "lsblk -f", "du -sh /var/log/* 2>/dev/null | sort -h | tail"],
        "demo2": ["ip route", "nmcli device status", "nmcli connection show", "cat /etc/resolv.conf"],
        "practice": ["ip -br link", "ip -br address", "ip route show", "nmcli -f GENERAL,IP4 device show <网卡名>"],
        "verify": ["uptime", "free -h", "df -hT", "ip route", "getent hosts <目标主机名>"],
    },
    (3, 3): {
        "check": ["ip -br address", "ip route", "nmcli connection show", "cat /etc/netplan/*.yaml 2>/dev/null"],
        "demo1": ["sudo nmcli con mod '<连接名>' ipv4.method manual ipv4.addresses <IP/前缀> ipv4.gateway <网关> ipv4.dns <DNS>", "sudo nmcli con up '<连接名>'", "nmcli -f IP4 connection show '<连接名>'"],
        "demo2": ["sudo cp /etc/netplan/01-netcfg.yaml /etc/netplan/01-netcfg.yaml.bak", "sudoedit /etc/netplan/01-netcfg.yaml", "sudo netplan try", "sudo netplan apply"],
        "practice": ["ip -br address", "ip route", "ping -c 4 <网关IP>", "ping -c 4 <对端IP>", "getent hosts <对端主机名>"],
        "verify": ["ip addr show <网卡名>", "ip route get <对端IP>", "resolvectl status 2>/dev/null || cat /etc/resolv.conf", "arp -n 2>/dev/null || ip neigh"],
    },
    (4, 1): {
        "check": ["ping -c 2 <Rocky-IP>", "getent hosts <Rocky主机名>", "ss -lntup"],
        "demo1": ["ss -lntup", "sudo ss -lntp | grep -E ':80|:443'", "getent hosts <主机名>", "dig <主机名>"],
        "demo2": ["curl -I http://<Rocky-IP>/", "curl -I http://<主机名>/missing", "curl -vk https://<主机名>/", "openssl s_client -connect <主机名>:443 -servername <主机名>"],
        "practice": ["curl -sS -o /dev/null -w '%{http_code}\\n' http://<主机名>/", "nc -vz <Rocky-IP> 80", "nc -vz <Rocky-IP> 443"],
        "verify": ["getent hosts <主机名>", "ss -lntp", "curl -I http://<主机名>/", "curl -vk https://<主机名>/"],
    },
    (4, 2): {
        "check": ["ping -c 2 <Rocky-IP>", "sudo systemctl status sshd --no-pager", "sudo ss -lntp | grep ':22'"],
        "demo1": ["ssh-keygen -t ed25519 -C 'student-lab'", "ssh-keygen -lf ~/.ssh/id_ed25519.pub", "ssh-keyscan -t ed25519 <Rocky-IP>", "ssh <用户>@<Rocky-IP>"],
        "demo2": ["ssh-copy-id -i ~/.ssh/id_ed25519.pub <用户>@<Rocky-IP>", "chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys", "ssh -i ~/.ssh/id_ed25519 <用户>@<Rocky-IP>", "ssh -v <别名>"],
        "practice": ["scp <本地文件> <别名>:/tmp/", "sftp <别名>", "sha256sum <本地文件>", "ssh <别名> 'sha256sum /tmp/<文件名>'"],
        "verify": ["ssh -o PasswordAuthentication=no <别名> hostname", "sudo journalctl -u sshd -n 30 --no-pager", "stat -c '%a %n' ~/.ssh ~/.ssh/authorized_keys"],
    },
    (4, 3): {
        "check": ["ssh <备份端别名> hostname", "date", "find <源目录> -maxdepth 2 -type f -print"],
        "demo1": ["rsync -av --dry-run <源目录>/ <备份端>:<目标目录>/", "rsync -av <源目录>/ <备份端>:<目标目录>/", "rsync -av --delete --dry-run <源目录>/ <备份端>:<目标目录>/"],
        "demo2": ["crontab -e", "crontab -l", "systemctl status crond --no-pager", "journalctl -u crond -n 30 --no-pager"],
        "practice": ["/usr/bin/rsync -av <源目录>/ <目标目录>/ >> <日志文件> 2>&1", "tail -n 30 <日志文件>", "sha256sum <源文件> <恢复文件>"],
        "verify": ["crontab -l", "stat <备份文件>", "tail -n 30 <日志文件>", "diff <源文件> <恢复文件>"],
    },
}


def command_block(s: dict, *phases: str) -> str:
    guide = COMMAND_GUIDES[(s["week"], s["lesson"])]
    commands: list[str] = []
    for phase in phases:
        commands.extend(guide.get(phase, []))
    return "\n".join(f"  $ {cmd}" for cmd in commands)


def make_process(s: dict) -> tuple[list[str], list[str]]:
    demos = s["demos"]
    tasks = s["tasks"]
    if s["hours"] == 2:
        process = [
            f"【考勤与环境检查】\n【教师】清点人数，要求学生先观察环境、后执行命令；抽查虚拟机电源、快照、网络和上次成果。\n【学生】报告异常并记录当前基线。快速检查命令：\n{command_block(s, 'check')}",
            f"【任务导入与成果说明】\n【教师】{s['intro']}展示任务单、完成样例和评分点，说明本次必须提交“操作命令—关键输出—判断结论—异常处理”四类证据。\n【学生】在任务单中写出操作对象、预期结果、风险点和回退方法，小组口述执行顺序。",
            f"【知识讲解与教师示范】\n【教师】结合终端输出讲解{join_items(s['key_points'])}。按“先查询状态—再修改—立即验证”的顺序示范{join_items(demos)}；逐条解释命令、参数、路径、权限和预期输出，不把无报错直接等同于成功。\n【命令示例】\n{command_block(s, 'demo1', 'demo2')}",
            f"【跟随练习】\n【教师】将示范拆成若干检查点，每完成一步就抽问“当前对象是什么、输出说明什么、下一步为什么这样做”，发现学生路径或权限错误时要求先停止并用查询命令定位。\n【学生】在自己的虚拟机逐条复现，使用history保留命令，圈出关键输出，并与教师示例比较。练习命令：\n{command_block(s, 'practice')}",
            f"【独立任务与记录】\n【教师】发布不完全相同的参数或文件对象，巡视检查学生是否直接照抄命令、是否替换占位符以及是否验证结果。\n【学生】独立完成{join_items(tasks)}；每项任务至少保留一条执行命令、一条验证命令和一句结果判断，出现错误时记录原始报错后再处理。",
            f"【规范教育与思政融入】\n【教师】{s['values_detail']}结合本次命令明确授权范围、数据责任和操作后果，要求学生说明一次不规范操作可能影响的具体用户、文件、服务或网络。\n【学生】把岗位规范落实到当前任务：操作前核对对象和权限，操作中如实保存成功与失败输出，操作后与同伴交叉核验；不复制他人截图、不隐藏报错、不越权测试。",
            f"【排障与验收】\n【教师】设置一项安全、可回退的小故障，限制学生先看现象再查原因，不允许直接重装或跳过失败步骤。\n【学生】按“现象—状态查询—原因假设—最小修改—复测”完成{s['verification']}。验收命令参考：\n{command_block(s, 'verify')}",
            f"【总结与作业】\n【教师】以一张对象关系图归纳本次课的技术主线、关键参数和安全边界，点评共性错误。\n【学生】口述一条查询命令、一条修改命令和一条验证命令，整理课堂记录。作业：{s['homework']}。",
        ]
        times = [
            "考勤与环境检查（2分钟）",
            "任务导入（8分钟）",
            "讲解与示范（20分钟）",
            "跟随练习（20分钟）",
            "独立任务与记录（15分钟）",
            "规范教育与思政融入（10分钟）",
            "排障与验收（10分钟）",
            "总结与作业（5分钟）",
        ]
    else:
        demo_mid = max(1, len(demos) // 2)
        task_mid = max(1, len(tasks) // 2)
        process = [
            f"【考勤与环境检查】\n【教师】清点人数，抽查双机电源、快照、网络和上次课成果，要求所有变更从可复现的基线开始。\n【学生】报告异常，执行基础检查并记录关键输出：\n{command_block(s, 'check')}",
            f"【任务导入与任务分解】\n【教师】{s['intro']}展示最终成果、验收表和常见失败样例，说明四课时分为“基础操作—阶段检查—进阶操作—故障恢复”。\n【学生】划分角色和步骤，标出修改对象、验证命令、备份点和回退路径。",
            f"【知识讲解与示范一】\n【教师】讲解{join_items(s['key_points'][:max(1, len(s['key_points']) // 2)])}，示范{join_items(demos[:demo_mid])}。每条命令均说明执行身份、参数含义、作用对象、预期输出和失败表现。\n【命令示例】\n{command_block(s, 'demo1')}",
            f"【学生实践一与阶段检查】\n【教师】按任务节点巡视，重点检查起始状态、路径、对象和权限；用提问代替代操作，要求学生根据输出自行判断。\n【学生】完成{join_items(tasks[:task_mid])}，使用查询命令确认阶段成果，保存原始输出和报错。练习命令参考：\n{command_block(s, 'practice')}",
            f"【规范教育与思政融入】\n【教师】{s['values_detail']}组织学生围绕本次真实命令讨论：错误对象、越权操作、伪造记录或跳过验证会给哪些用户、数据和服务造成什么后果；共同提出预防、回退和责任记录要求。\n【学生】核对同伴的命令对象、权限范围和证据真实性，发现风险立即停止并报告，把规范写入任务单后再继续。",
            f"【知识讲解与示范二】\n【教师】继续讲解{join_items(s['key_points'][max(1, len(s['key_points']) // 2):])}，示范{join_items(demos[demo_mid:])}。通过正常输出与错误输出对比，说明配置变化如何影响系统状态，并演示最小化修改和回退。\n【命令示例】\n{command_block(s, 'demo2')}",
            f"【学生实践二与交叉验证】\n【教师】提供不同账号、地址、路径或服务状态的任务参数，记录共性问题并进行短暂停讲。\n【学生】完成{join_items(tasks[task_mid:])}，互换终端进行只读验证；每组形成“执行命令—输出证据—判断结论—回退结果”的记录。",
            f"【故障诊断训练】\n【教师】注入一项安全、可恢复的故障，只提供现象和验收标准，引导学生从底层状态逐层排查。\n【学生】按“复现现象—收集输出—提出假设—一次只改一项—沿原路径复测”处理，禁止无证据地反复重启或重装。",
            f"【成果验收】\n【教师】依据验收表随机抽查学生解释命令参数和输出含义，确认结果来自当前环境。\n【学生】完成{s['verification']}，提交阶段截图、终端文本和结论。验收命令参考：\n{command_block(s, 'verify')}",
            f"【总结与作业】\n【教师】梳理对象关系、关键命令、常见报错和安全边界，点评具有代表性的规范操作。\n【学生】用自己的话复述一条查询、修改、验证和回退命令，整理成果。作业：{s['homework']}。",
        ]
        times = [
            "考勤与环境检查（2分钟）",
            "任务导入（8分钟）",
            "讲解与示范一（25分钟）",
            "学生实践一与阶段检查（35分钟）",
            "规范教育与思政融入（10分钟）",
            "讲解与示范二（25分钟）",
            "学生实践二与交叉验证（35分钟）",
            "故障诊断训练（20分钟）",
            "成果验收（15分钟）",
            "总结与作业（5分钟）",
        ]
    return process, times


def paragraph_with_text(template, text: str):
    p = deepcopy(template)
    p_pr = p.find(f"./{W}pPr")
    run_template = p.find(f".//{W}r")
    r_pr = deepcopy(run_template.find(f"./{W}rPr")) if run_template is not None and run_template.find(f"./{W}rPr") is not None else None
    for child in list(p):
        if child is not p_pr:
            p.remove(child)
    if text:
        for i, part in enumerate(text.split("\n")):
            if i:
                br_run = etree.SubElement(p, f"{W}r")
                if r_pr is not None:
                    br_run.append(deepcopy(r_pr))
                etree.SubElement(br_run, f"{W}br")
            run = etree.SubElement(p, f"{W}r")
            if r_pr is not None:
                run.append(deepcopy(r_pr))
            t = etree.SubElement(run, f"{W}t")
            if text.startswith(" ") or text.endswith(" "):
                t.set(f"{{{XML_NS}}}space", "preserve")
            t.text = part
    return p


def set_cell_text(tc, lines: list[str]):
    templates = tc.findall(f"./{W}p")
    if not templates:
        templates = [etree.Element(f"{W}p")]
    for p in tc.findall(f"./{W}p"):
        tc.remove(p)
    if not lines:
        tc.append(paragraph_with_text(templates[0], ""))
        return
    for i, line in enumerate(lines):
        tc.append(paragraph_with_text(templates[min(i, len(templates) - 1)], line))


def table_rows(tbl):
    return tbl.findall(f"./{W}tr")


def row_cells(row):
    return row.findall(f"./{W}tc")


def fill_session(tbl, s: dict):
    rows = table_rows(tbl)
    set_cell_text(row_cells(rows[0])[1], ["2026 年    月    日（星期    ）"])
    set_cell_text(row_cells(rows[0])[3], [str(s["hours"])])
    set_cell_text(row_cells(rows[1])[1], s["project"].split("\n"))
    set_cell_text(row_cells(rows[2])[1], make_objectives(s))
    set_cell_text(row_cells(rows[3])[1], [s["analysis"]])
    set_cell_text(row_cells(rows[4])[1], [f"{i + 1}.{x}" for i, x in enumerate(s["key_points"])])
    set_cell_text(row_cells(rows[5])[1], [f"{i + 1}.{x}" for i, x in enumerate(s["difficulties"])])
    set_cell_text(row_cells(rows[6])[1], [s["methods"]])
    set_cell_text(row_cells(rows[7])[1], make_design(s))
    process, times = make_process(s)
    set_cell_text(row_cells(rows[9])[0], process)
    set_cell_text(row_cells(rows[9])[1], times)
    set_cell_text(row_cells(rows[10])[1], s["board"])
    set_cell_text(row_cells(rows[11])[1], [])


SESSIONS = [
    {
        "week": 1, "lesson": 1, "hours": 2,
        "project": "模块一 Linux基础运维\n实验1 Linux系统认知、VMware虚拟化环境搭建与双机安装（第一部分）",
        "culture": "了解UNIX、GNU和Linux的发展脉络，认识自由软件与开源协作对现代信息技术的影响",
        "knowledge": "理解操作系统、Linux内核、发行版、宿主机、客户机和Hypervisor等基本概念，能够区分RHEL、Rocky Linux、CentOS Stream、Debian和Ubuntu",
        "ability": "能够检查宿主机硬件虚拟化条件，完成VMware Workstation环境检查并开始创建Rocky Linux服务器虚拟机",
        "ideology": "认识关键基础软件自主可控的重要性，形成尊重许可证、核验软件来源和维护网络安全的责任意识",
        "vocational": "形成先确认需求和环境、再实施安装，并完整记录软硬件参数的工作习惯",
        "analysis": "学生具备Windows基本操作和计算机组成基础，但对Linux、虚拟化和服务器角色较陌生，容易混淆Linux内核与发行版，也可能忽略宿主机资源和硬件虚拟化条件。教学中应借助对象关系图和真实环境检查表建立直观认识。",
        "key_points": ["Linux内核与发行版的关系", "主流发行版及课程双机角色", "宿主机、客户机与Hypervisor", "VMware环境检查和虚拟机资源规划"],
        "difficulties": ["区分Linux内核、发行版和软件生态", "理解宿主机资源与多台客户机资源之间的约束", "根据课程要求规划双机目录和虚拟硬件"],
        "methods": "问题导入、理论讲授、对象关系图示、教师演示、学生操作",
        "intro": "以“为新业务准备一台可管理的Linux服务器”为工作任务，展示服务器交付单，追问为什么不能直接在唯一上反复安装和试错。",
        "demos": ["检查CPU、内存、磁盘空间和硬件虚拟化状态", "核对VMware版本、NAT网络和虚拟机保存位置", "创建Rocky服务器虚拟机并解释CPU、内存、磁盘、网卡参数"],
        "tasks": ["完成宿主机与VMware环境检查表", "准备Rocky Linux 9和Ubuntu Server 22.04镜像并记录来源", "建立双机目录并创建Rocky服务器虚拟机"],
        "values_detail": "教师展示来源不明镜像、未核验校验值和随意突破软件授权边界可能带来的供应链风险，引导学生核对官方网站、版本、架构和哈希信息。学生在环境检查表中记录镜像来源与校验结果，明确使用开源软件仍需遵守许可证和学校网络管理规定。",
        "verification": "复核每台宿主机的虚拟化支持、VMware网络和Rocky虚拟硬件参数，发现资源不足时先调整方案而不是盲目启动安装",
        "homework": "补全环境检查表，准备两套ISO，并记录镜像文件名、版本、架构、来源和校验值",
        "board": ["Linux课程实验环境", "├─ 宿主机：Windows 10或11", "├─ Hypervisor：VMware Workstation", "├─ Rocky Linux 9：服务器", "├─ Ubuntu Server 22.04：客户端", "└─ 交付要求：可运行、可联网、可验证、可回退"],
    },
    {
        "week": 1, "lesson": 2, "hours": 4,
        "project": "模块一 Linux基础运维\n完成实验1 双机安装与环境基线\n实验2 Linux命令行、文件与目录管理（第一部分）",
        "culture": "了解Linux命令行传统及其在服务器、云计算和自动化领域长期保留的原因",
        "knowledge": "掌握Rocky与Ubuntu安装要点、首次登录与DHCP联网检查，理解Shell提示符、命令格式、帮助系统、Linux目录结构以及绝对路径和相对路径",
        "ability": "能够完成Rocky服务器和Ubuntu客户端安装，建立初始快照，并使用基础命令获取帮助、切换目录和创建规定的项目目录树",
        "ideology": "理解标准化安装、真实记录和可回退机制对公共信息系统稳定运行的意义，拒绝伪造成功结果",
        "vocational": "形成安装前核对参数、安装后建立基线、重大操作前创建快照并验证结果的职业习惯",
        "analysis": "学生已完成虚拟化环境检查，但首次同时安装两种发行版，容易在磁盘分配、账号密码、网络选项和系统角色上出错。学生对命令行可能有畏难情绪，需要通过帮助系统、补全和可见结果降低入门难度。",
        "key_points": ["Rocky与Ubuntu安装流程及角色差异", "首次登录、DHCP联网和环境基线", "Shell提示符、命令格式、帮助与补全", "Linux目录结构、绝对路径和相对路径"],
        "difficulties": ["交叉利用安装等待时间完成双机部署", "通过版本、地址、磁盘和网络输出证明环境真实可用", "在目录树中正确判断当前路径和目标路径"],
        "methods": "理实一体、操作演示、任务驱动、双机对照、结果验收",
        "intro": "出示“服务器安装完成但无法联网、无法确认版本、无法恢复”的失败交付案例，让学生明确安装结束不等于环境交付完成。",
        "demos": ["演示Rocky最小化安装、账号创建和网络启用", "演示Ubuntu Server安装与OpenSSH选择", "使用hostnamectl、ip、lsblk和df建立双机基线", "使用man、--help、Tab补全和history获取命令帮助"],
        "tasks": ["完成Rocky服务器与Ubuntu客户端安装和首次登录", "检查双机DHCP地址、系统版本、主机名、时间和磁盘", "建立初始快照并按统一规则命名", "练习pwd、cd、ls、mkdir和touch，创建规定项目目录树"],
        "values_detail": "教师用“只截取成功画面、隐瞒安装报错”的反例讨论技术诚信，要求所有基线数据来自学生当前虚拟机，并保留失败现象和处理记录。学生互查系统版本、IP和快照名称，发现数据不一致时重新执行命令，不复制他人结果。",
        "verification": "从两台虚拟机分别检查系统版本、主机名、IP、默认路由和磁盘，完成双向基础连通测试，并恢复一次初始快照后确认系统可启动",
        "homework": "提交双机环境基线和目录树结果，整理今天使用过的帮助命令及其用途",
        "board": ["双机环境交付", "├─ 安装：Rocky服务器与Ubuntu客户端", "├─ 基线：版本、主机名、IP、路由、磁盘", "├─ 快照：统一命名并验证", "└─ 命令行：命令 参数 对象", "路径", "├─ 绝对路径：从 / 开始", "└─ 相对路径：从当前位置开始"],
    },
    {
        "week": 1, "lesson": 3, "hours": 2,
        "project": "模块一 Linux基础运维\n完成实验2 Linux命令行、文件与目录管理",
        "culture": "理解Linux以文本、目录和小工具组合组织系统管理工作的技术传统",
        "knowledge": "掌握pwd、cd、ls、mkdir、touch、cp、mv、rm、cat、less、head和tail的基本用途及常用参数",
        "ability": "能够按照企业项目目录要求创建、复制、移动、查看和清理文件，并用命令记录证明结果",
        "ideology": "认识数据和文件属于业务资产，形成谨慎删除、尊重他人劳动成果和保护公共资源的责任意识",
        "vocational": "执行复制、移动和删除前确认源与目标，删除后核验结果，对高风险命令保持审慎",
        "analysis": "学生已能定位路径和创建简单目录，但对复制目录、移动重命名、通配符和递归删除的影响范围认识不足，容易因当前位置判断错误操作到错误对象。需要以项目文件整理任务强化“先定位、再操作、后检查”。",
        "key_points": ["文件与目录的创建、复制、移动和删除", "文本文件的完整查看与分段查看", "相对路径、绝对路径和通配符的综合使用", "企业项目目录整理和结果验证"],
        "difficulties": ["判断cp和mv的源、目标及最终路径", "理解rm删除不可直接撤销的风险", "根据任务描述构造正确目录树"],
        "methods": "任务驱动、教师示范、独立实践、同伴互查、结果验收",
        "intro": "提供一组目录混乱、文件命名不规范的新业务资料，要求学生在不丢失文件的前提下整理为标准项目结构。",
        "demos": ["对比cp、mv和rm对源对象及目标位置的影响", "使用cat、less、head和tail查看不同长度文件", "用pwd和ls在操作前后核对当前位置与结果"],
        "tasks": ["创建业务、配置、日志、备份和文档目录", "复制模板文件并完成移动和重命名", "查看指定文件首尾内容", "清理测试文件并保存命令历史"],
        "values_detail": "教师结合误删生产目录导致业务中断的案例，要求学生在执行rm前口头说明当前路径、目标对象和是否存在备份。学生使用ls或find确认删除范围，先删除教师指定的测试文件，严禁在根目录或不确定路径下尝试递归删除。",
        "verification": "对照目录清单检查层级、文件名和文件内容，随机指定一个文件让学生说明其来源、当前位置和操作记录",
        "homework": "提交规范目录树和关键命令记录，并写出三条安全使用rm的规则",
        "board": ["文件管理闭环", "1. pwd确认位置", "2. ls确认对象", "3. cp或mv实施变更", "4. 再次ls验证结果", "5. rm前确认范围与备份", "查看文件：cat less head tail"],
    },
    {
        "week": 2, "lesson": 1, "hours": 2,
        "project": "模块一 Linux基础运维\n实验3 文本编辑、文件查找与归档恢复",
        "culture": "了解Unix文本工具和可组合命令对软件配置、运维记录及知识共享的影响",
        "knowledge": "掌握Vim基本模式与保存退出，理解find、which、软链接、硬链接、tar归档和恢复的基本原理",
        "ability": "能够修改指定配置文件，查找文件和命令位置，创建链接，并完成目录归档、解包与恢复验证",
        "ideology": "认识备份文件只有经过恢复验证才具备实际价值，形成对数据完整性和交付质量负责的意识",
        "vocational": "修改配置前保留副本，归档后检查内容和校验结果，能够记录恢复步骤",
        "analysis": "学生掌握基本文件操作，但不熟悉Vim模式切换，容易出现无法输入、保存或退出的问题；对软硬链接和归档压缩的区别也容易混淆。需要通过对象变化和恢复实验建立理解。",
        "key_points": ["Vim普通模式、插入模式和命令行模式", "find与which的查找范围", "软链接与硬链接", "tar归档、解包和恢复验证"],
        "difficulties": ["正确切换Vim模式并安全保存退出", "理解链接、inode和原文件之间的关系", "区分生成归档文件与真正完成可用备份"],
        "methods": "教师演示、学生操作、恢复验证、对比教学",
        "intro": "模拟配置文件被误改和项目目录被误删的场景，要求学生找到正确文件并从归档中恢复。",
        "demos": ["用Vim完成进入、编辑、撤销、保存和退出", "使用find按名称和类型查找并用which定位命令", "创建软硬链接并观察原文件变化", "使用tar归档、列出内容、解包和恢复"],
        "tasks": ["修改指定配置文件并保留原始副本", "按条件查找文件和命令", "创建并验证软链接与硬链接", "归档项目目录、模拟删除并恢复"],
        "values_detail": "教师展示“备份文件存在但无法解包”的质量事故，说明备份责任包括可读、完整和可恢复。学生在归档后必须列出内容并执行一次恢复，比较恢复前后文件数量和内容；只报告“tar命令没有报错”不计为完成。",
        "verification": "检查配置文件修改、链接指向、归档清单和恢复目录，比较恢复前后的文件结构与内容",
        "homework": "提交配置修改、查找、归档和恢复证据，整理Vim最小操作流程",
        "board": ["Vim模式", "普通模式 ↔ 插入模式", "普通模式 → 命令行模式", "查找：find文件 which命令", "链接：软链接与硬链接", "备份：归档 → 检查 → 模拟丢失 → 恢复 → 对比"],
    },
    {
        "week": 2, "lesson": 2, "hours": 4,
        "project": "模块一 Linux基础运维\n实验4 Linux用户、用户组与权限管理",
        "culture": "理解多用户操作系统通过身份、权限和审计规则保障协作秩序的设计思想",
        "knowledge": "掌握用户、用户组、UID、GID、主组、附加组、rwx、chmod、chown、umask、sudo和wheel的作用",
        "ability": "能够按企业部门情境创建账号和用户组，配置共享目录权限与sudo最小授权，并使用不同账号完成正反向验证",
        "ideology": "理解账号和权限代表责任边界，树立依法用权、最小授权、保护个人信息和公共数据的意识",
        "vocational": "做到一人一号、权限按需、授权有依据、变更可审计，并避免长期使用root完成日常工作",
        "analysis": "学生会使用基本文件命令，但容易把所有权限问题归结为chmod 777，也可能混淆文件和目录上的rwx含义、主组和附加组。需要用部门协作场景和多账号测试建立最小权限思维。",
        "key_points": ["用户、用户组、UID与GID", "文件和目录上的rwx权限", "chmod、chown与umask", "sudo、wheel和最小授权", "共享目录的多人验证"],
        "difficulties": ["理解目录执行权限与进入、创建和删除之间的关系", "组合所有者、所属组和其他用户权限", "只授权完成任务所需的sudo命令"],
        "methods": "情境教学、任务驱动、多人账号验证、错误案例分析",
        "intro": "以开发、测试和运维人员共同使用项目目录为情境，要求既能协作又不能越权读取、修改或管理系统服务。",
        "demos": ["查看passwd、group等身份信息并创建用户组", "配置共享目录所有者、所属组和SGID", "使用数字法和符号法调整权限", "通过visudo配置最小sudo授权并查看使用记录"],
        "tasks": ["创建开发、测试和运维账号及对应用户组", "建立共享目录并设置合理所有权和权限", "使用多个账号验证允许和拒绝行为", "为指定运维账号配置一项最小sudo权限"],
        "values_detail": "教师以共享账号无法追责、chmod 777导致数据泄露为案例，要求学生根据岗位任务逐项说明“谁需要什么权限、为什么需要、何时回收”。学生不得交换个人密码，不得为了通过验收扩大权限；互查时既验证授权成功，也必须验证未授权操作确实被拒绝。",
        "verification": "分别以开发、测试、运维和普通账号登录，验证目录读取、创建、修改、删除和sudo操作的允许与拒绝结果，并核对sudo日志",
        "homework": "提交账号与组关系表、共享目录权限结果和最小授权验证记录，解释为什么不能使用chmod 777解决所有问题",
        "board": ["身份与权限", "用户 → UID", "用户组 → GID", "权限对象：所有者 所属组 其他人", "rwx：文件与目录含义不同", "最小授权", "├─ 普通账号完成日常工作", "├─ sudo只授权所需命令", "└─ 成功与拒绝都要验证"],
    },
    {
        "week": 2, "lesson": 3, "hours": 2,
        "project": "模块一 Linux基础运维\n实验5 软件包与软件源管理",
        "culture": "了解Linux软件仓库、数字签名和社区发行模式对软件分发方式的影响",
        "knowledge": "掌握RPM、DNF、DEB、APT、软件仓库、镜像源、元数据和GPG签名的基本关系",
        "ability": "能够检查软件源，查询、安装、验证、更新和卸载指定软件，并记录镜像源变更与回退方法",
        "ideology": "树立软件正版化、供应链安全和网络安全意识，不绕过签名检查，不使用来源不明的软件包",
        "vocational": "变更软件源前备份配置，安装后核对包名、版本、来源和服务状态，保留回退记录",
        "analysis": "学生已有安装应用程序的经验，但容易把Linux包管理理解为从网页随意下载文件，不清楚仓库元数据、依赖和签名的作用。需要通过DNF与APT对照和来源核验建立软件供应链意识。",
        "key_points": ["RPM包、DNF仓库与依赖关系", "查询、安装、更新和卸载流程", "镜像源、元数据和GPG签名", "DNF与APT的基本对照"],
        "difficulties": ["区分软件包文件与仓库提供的软件集合", "判断仓库不可用、网络失败和GPG校验失败", "修改镜像源后的验证与回退"],
        "methods": "演示教学、任务实践、对比教学、供应链案例分析",
        "intro": "展示“同名软件来自未知网站”和“由发行版签名仓库提供”两种安装路径，让学生判断哪一种更容易确认来源、依赖和更新。",
        "demos": ["使用dnf repolist、search和info检查仓库与软件", "安装并查询指定包的版本和来源", "演示APT对应命令", "备份软件源配置并验证回退"],
        "tasks": ["记录当前仓库并刷新元数据", "查询、安装和验证指定软件", "对照DNF与APT命令", "完成一次卸载或源配置回退"],
        "values_detail": "教师结合恶意软件包和篡改镜像案例，说明包管理器的签名校验是软件供应链责任链的一部分。学生必须记录仓库名称、软件版本和来源，遇到GPG错误先停止安装并查明原因，不以关闭签名校验作为快捷处理办法。",
        "verification": "检查仓库状态、软件版本、包来源和安装前后变化，模拟一个不可用源后恢复原配置并重新验证",
        "homework": "提交软件源、包查询、安装验证和回退记录，制作一张DNF与APT常用操作对照表",
        "board": ["软件供应链", "仓库 → 元数据 → 软件包 → 依赖", "GPG签名：确认来源与完整性", "DNF：repolist search info install remove", "APT：update search show install remove", "变更闭环：备份 配置 验证 回退"],
    },
    {
        "week": 3, "lesson": 1, "hours": 2,
        "project": "模块一 Linux基础运维\n实验6 systemd服务与journal日志管理",
        "culture": "了解Linux从传统启动脚本到systemd统一服务管理的发展，以及日志在工程协作中的作用",
        "knowledge": "掌握进程、服务、Unit、systemctl和journalctl的基本概念，理解服务状态、开机自启和日志之间的关系",
        "ability": "能够启动、停止、重启、启用和检查服务，并依据状态和日志定位一次服务启动失败",
        "ideology": "形成尊重事实、依据日志作出判断的态度，认识维护公共服务稳定运行是运维岗位的基本责任",
        "vocational": "服务变更前确认影响范围，变更后检查状态、自启、端口和日志，不用反复重启代替故障分析",
        "analysis": "学生已具备软件安装和权限基础，但容易把进程与服务混为一谈，遇到启动失败常直接重复执行restart，不会阅读状态和日志。教学中应以一次可恢复的服务故障训练证据链。",
        "key_points": ["进程、服务和Unit", "systemctl服务生命周期管理", "开机自启与当前运行状态", "journalctl日志筛选", "服务启动故障证据链"],
        "difficulties": ["理解enable与start的区别", "从systemctl status和journalctl中提取关键错误", "区分故障现象、直接原因和根因"],
        "methods": "故障导向、教师演示、学生排障、证据链复盘",
        "intro": "给出“服务显示已安装但客户端无法使用”的运维工单，要求学生判断服务是否运行、是否自启以及失败原因。",
        "demos": ["使用systemctl查看、启停和启用服务", "查看Unit文件来源和有效状态", "使用journalctl按Unit和时间筛选日志", "制造配置错误并依据状态和日志定位"],
        "tasks": ["完成指定服务的启停、重启和自启设置", "采集服务状态与日志", "修复一次启动失败", "按现象、证据、原因、修复和复测填写记录"],
        "values_detail": "教师展示“没有查看日志就把故障归因于网络”的错误工单，强调技术结论必须有可复核证据。学生只能依据当前状态、退出码和日志提出原因，不能删除失败日志或编造成功结果；修复后须保留修复前后证据，体现对服务使用者负责。",
        "verification": "停止、启动和重启指定服务，核对active状态和开机自启状态；注入配置错误后用status与journal定位，修复并复测",
        "homework": "提交服务故障的“状态—日志—原因—修复—验证”记录，并解释start与enable的区别",
        "board": ["systemd服务管理", "Unit → 服务定义", "systemctl", "├─ start stop restart", "├─ enable disable", "└─ status", "journalctl -u 服务", "排障：状态 → 日志 → 配置 → 修复 → 复测"],
    },
    {
        "week": 3, "lesson": 2, "hours": 4,
        "project": "模块一 Linux基础运维与模块二网络管理\n实验7 系统状态、磁盘与容量巡检\n实验8 Linux网络配置与连通性诊断（第一部分）",
        "culture": "理解监测数据、网络标准和分层模型在大规模信息系统协作中的共同价值",
        "knowledge": "掌握CPU、负载、内存、进程、磁盘、文件系统和容量指标，并理解IP地址、前缀、网关、DNS、网卡、连接和路由的关系",
        "ability": "能够完成服务器基础巡检，识别明显资源异常，并根据VMnet8实际参数制定Rocky与Ubuntu双机地址规划",
        "ideology": "树立节约计算资源、保护公共设备和以数据支撑判断的意识，认识网络地址规划必须遵守统一规则",
        "vocational": "巡检数据注明采集时间和单位，网络配置前先记录现状并准备回退方案",
        "analysis": "学生能执行命令但对负载、内存可用量、磁盘与文件系统的关系认识零散，也容易只记IP地址而忽略前缀、网关、DNS和路由。需要将资源巡检表与网络对象关系图结合。",
        "key_points": ["CPU、负载、内存和进程状态", "磁盘、分区、文件系统、挂载点和容量", "IP地址、前缀、网关与DNS", "NetworkManager中的网卡与连接", "双机实验网络地址规划"],
        "difficulties": ["避免把单个瞬时指标直接判定为故障", "区分磁盘设备、文件系统和挂载点", "根据实际NAT网段选择不冲突的静态地址"],
        "methods": "巡检实践、理论讲授、教师演示、数据解读、规划任务",
        "intro": "以“服务器变慢且磁盘告警，同时下节课需要改静态地址”为连续工单，要求先形成资源基线，再依据真实VMnet8参数进行网络规划。",
        "demos": ["使用uptime、top、free和ps采集资源状态", "使用lsblk、df和du检查存储层次与容量", "使用ip addr、ip route和nmcli查看网络现状", "读取VMware NAT网段、网关和DHCP范围并制定地址表"],
        "tasks": ["完成CPU、负载、内存和进程巡检", "完成磁盘、文件系统和容量巡检", "记录Rocky与Ubuntu当前网络基线", "制定包含IP、前缀、网关、DNS和主机名的双机地址规划"],
        "values_detail": "教师结合机房公共计算资源被无效进程长期占用的情况，引导学生用数据判断资源使用是否合理，并讨论节约算力和保障他人学习环境的责任。网络规划环节要求学生服从统一地址规则，不抢占他人地址；发现冲突先沟通和修正规划，不通过关闭他人网络解决问题。",
        "verification": "随机抽取一个资源指标让学生说明含义和证据；检查双机地址是否属于实际网段、避开DHCP冲突并包含完整网关和DNS信息",
        "homework": "提交系统巡检表和双机网络规划表，标明每项数据的命令来源和判断结论",
        "board": ["系统巡检", "CPU与负载 → uptime top", "内存 → free", "进程 → ps top", "存储 → lsblk df du", "网络五要素", "IP 前缀 网关 DNS 路由", "配置前：记录基线与回退"],
    },
    {
        "week": 3, "lesson": 3, "hours": 2,
        "project": "模块二 网络、远程管理与基础防护\n完成实验8 Linux网络配置与连通性诊断",
        "culture": "理解TCP/IP开放标准使不同操作系统和设备能够互联互通的工程价值",
        "knowledge": "掌握Rocky中ip与nmcli、Ubuntu中Netplan的基本配置方法，理解临时配置、永久配置和路由优先级",
        "ability": "能够为Rocky与Ubuntu配置静态IP、网关、DNS和主机名，完成双向连通验证并恢复一次错误配置",
        "ideology": "形成遵守网络管理制度、避免地址冲突和不擅自改变公共网络参数的纪律意识",
        "vocational": "远程或网络变更前保留原连接和回退入口，按本机、网关、目标主机、DNS逐层验证",
        "analysis": "学生已完成网络规划，但首次修改永久网络配置，容易写错前缀、网关或DNS，也可能在配置生效后未检查路由。需要使用控制台和回退连接降低失联风险。",
        "key_points": ["Rocky的ip与nmcli", "Ubuntu的Netplan", "静态IP、网关、DNS和主机名", "分层连通测试", "网络配置回退"],
        "difficulties": ["区分临时网络状态与永久连接配置", "修改远程网络时避免失联", "依据测试失败层次判断IP、路由或DNS问题"],
        "methods": "分层排障、双机操作、对比教学、结果复测",
        "intro": "按照上次课的地址规划，将两台DHCP主机改为固定地址，并保证修改后仍能互通、解析名称且能够恢复。",
        "demos": ["使用nmcli修改Rocky连接并重新激活", "编辑和应用Ubuntu Netplan配置", "按本机、网关、目标主机和DNS顺序测试", "使用备份连接或控制台恢复错误配置"],
        "tasks": ["配置Rocky静态网络和主机名", "配置Ubuntu静态网络和主机名", "完成双向ping、路由和DNS检查", "模拟一个IP或DNS错误并恢复"],
        "values_detail": "教师说明擅自占用他人IP会影响同学实验和机房网络秩序，要求每组使用批准的地址表，并在改动前记录原配置。学生发现冲突时保存arp、ping等证据并报告，不攻击、不断开他人设备；恢复后主动通知受影响同伴共同复测。",
        "verification": "分别在Rocky和Ubuntu检查地址、路由、DNS和主机名，完成双向互通；注入IP或DNS错误后按分层路径定位、恢复并复测",
        "homework": "提交双机配置、互通结果和一次网络故障记录，绘制本机到目标主机的访问路径",
        "board": ["双机网络", "Rocky：nmcli", "Ubuntu：Netplan", "配置：IP 前缀 网关 DNS 主机名", "测试顺序", "1. 本机接口", "2. 网关", "3. 目标IP", "4. 名称解析", "5. 应用访问", "失败后按原路回退"],
    },
    {
        "week": 4, "lesson": 1, "hours": 2,
        "project": "模块二 网络、远程管理与基础防护\n实验9 端口、DNS与HTTP/HTTPS访问验证",
        "culture": "了解DNS、HTTP和HTTPS等开放协议如何支撑全球互联网的信息访问与可信通信",
        "knowledge": "掌握TCP与UDP、进程、Socket、监听地址、端口、hosts、DNS客户端、HTTP状态码和自签名证书的基本关系",
        "ability": "能够从Ubuntu检查Rocky的名称解析、监听端口以及HTTP与HTTPS访问结果，并依据状态码定位基础问题",
        "ideology": "认识网络访问应遵守授权边界，形成保护通信数据、尊重网络秩序和依法使用测试工具的意识",
        "vocational": "测试端口和服务只针对课程授权目标，记录请求、响应、证书和状态码，不把能ping通等同于应用可用",
        "analysis": "学生已能配置IP和DNS，但容易把网络连通、名称解析、端口监听和Web响应混为一层，也可能忽视HTTPS证书提示。需要用Ubuntu到Rocky的完整访问链逐层验证。",
        "key_points": ["TCP、UDP、Socket与端口", "监听地址对访问范围的影响", "hosts与DNS解析顺序", "curl与HTTP状态码", "HTTPS和自签名证书"],
        "difficulties": ["区分网络可达、端口开放和应用响应", "判断解析结果来自hosts还是DNS", "理解证书身份校验与加密连接的关系"],
        "methods": "问题导向、双机验证、协议观察、操作实践",
        "intro": "提供“ping正常但网页打不开”和“IP能访问、域名不能访问”两个现象，要求学生找出它们位于访问链的哪一层。",
        "demos": ["使用ss查看进程、协议、监听地址和端口", "使用getent、dig或nslookup观察解析结果", "使用curl查看HTTP请求、响应头和状态码", "访问自签名HTTPS并解释证书警告"],
        "tasks": ["从Ubuntu验证Rocky名称解析", "检查目标服务监听端口和地址", "访问HTTP与HTTPS并记录状态码", "对比正常、404和证书校验失败的现象"],
        "values_detail": "教师明确端口扫描和网络探测只能在课程授权的两台实验主机之间进行，未经许可测试他人设备可能违反网络安全管理规定。学生在任务单中写明目标IP、端口和授权范围，发现开放服务只记录并报告，不尝试越权登录或获取数据。",
        "verification": "从Ubuntu按名称解析、目标IP、监听端口、HTTP状态码和HTTPS证书顺序形成证据表，并解释两种失败现象的层次",
        "homework": "提交端口、解析和HTTP/HTTPS验证记录，解释200、403、404和连接拒绝分别说明什么",
        "board": ["访问证据链", "客户端名称", "↓ hosts或DNS", "目标IP", "↓ TCP或UDP端口", "监听Socket与进程", "↓ HTTP或HTTPS", "状态码与证书", "不能用ping替代应用验证"],
    },
    {
        "week": 4, "lesson": 2, "hours": 4,
        "project": "模块二 网络、远程管理与基础防护\n实验10 SSH远程管理与密钥认证",
        "culture": "了解SSH取代明文远程协议的背景及公钥密码技术对现代系统管理的贡献",
        "knowledge": "掌握sshd、主机密钥、用户密钥、首次连接指纹、密码认证、公钥认证、authorized_keys、客户端配置、scp和sftp的作用",
        "ability": "能够从Ubuntu安全连接Rocky，完成Ed25519密钥认证、客户端别名和远程文件传输，并排查常见连接故障",
        "ideology": "树立密码和私钥保护、身份可信、授权访问和安全运维意识，认识远程管理权限必须用于合法工作目的",
        "vocational": "不共享私钥，不盲目接受变化的主机指纹；修改sshd前检查配置、保留会话并准备回退",
        "analysis": "学生已理解端口和服务，但对SSH中的客户端、服务端、主机密钥和用户密钥角色容易混淆，可能随意复制私钥或忽略文件权限。教学中应通过握手角色图和正反向验证建立安全边界。",
        "key_points": ["sshd服务和22端口", "首次连接与主机指纹", "密码认证与Ed25519公钥认证", "authorized_keys权限", "SSH客户端别名与scp、sftp", "SSH日志和分层排障"],
        "difficulties": ["区分主机密钥与用户密钥", "理解私钥留在客户端、公钥进入服务端", "修改认证配置时避免把自己锁在服务器外", "根据客户端调试输出和服务端日志定位失败阶段"],
        "methods": "双机实训、任务驱动、安全案例、故障排查、结果验收",
        "intro": "以“管理员需要远程维护服务器，但密码登录既不便于管理又容易被攻击”为任务，要求建立可验证、可回退的密钥登录通道。",
        "demos": ["检查sshd状态、监听端口和有效配置", "首次连接并核对主机指纹", "在Ubuntu生成Ed25519密钥并只传送公钥", "检查authorized_keys目录和文件权限", "配置客户端别名并使用scp与sftp传输", "结合ssh -v和服务端日志排查失败"],
        "tasks": ["从Ubuntu完成Rocky密码登录并确认身份", "生成独立实验密钥并完成公钥认证", "配置SSH客户端别名", "使用scp和sftp双向传输并校验文件", "模拟权限或服务故障并恢复"],
        "values_detail": "教师展示把私钥上传到群聊、代码仓库或共享盘导致服务器失陷的案例，明确私钥等同于个人数字身份凭证。学生只能在自己的Ubuntu客户端生成和保存私钥，只把公钥写入Rocky；首次连接时核对指纹，指纹异常先停止并报告，不用删除known_hosts掩盖风险。",
        "verification": "强制指定实验私钥完成登录，核对远端用户名和主机名；传输文件后比较SHA-256；注入authorized_keys权限或sshd状态故障并按日志恢复",
        "homework": "提交密钥登录、客户端别名、文件哈希和故障排查记录，画出SSH客户端、服务端、公钥和私钥的位置关系",
        "board": ["SSH安全连接", "Ubuntu客户端", "├─ 私钥：只保留在本机", "├─ known_hosts：保存主机指纹", "└─ ssh config：客户端别名", "Rocky服务端", "├─ sshd与22端口", "└─ authorized_keys：保存公钥", "排障：网络 → 端口 → 服务 → 配置 → 权限 → 日志"],
    },
    {
        "week": 4, "lesson": 3, "hours": 2,
        "project": "模块二 网络、远程管理与基础防护\n实验11 rsync数据同步与crontab定时备份",
        "culture": "理解自动化任务和增量同步技术对长期系统维护、数据保存与工作效率的价值",
        "knowledge": "掌握rsync源目录末尾斜杠、首次同步、增量同步、dry-run、crontab、日志重定向和恢复验证",
        "ability": "能够建立本地或双机增量备份任务，配置定时执行和日志记录，并从备份恢复一次误删文件",
        "ideology": "认识数据安全关系到组织和个人权益，形成定期备份、验证恢复、保护备份数据和诚实记录任务结果的责任意识",
        "vocational": "使用--delete等高风险参数前先dry-run，定时任务使用绝对路径并记录日志，定期开展恢复演练",
        "analysis": "学生已具备SSH和文件操作基础，但容易忽略rsync源目录斜杠造成的目录层级差异，也可能认为写入crontab即代表任务成功。需要通过首次、增量、定时和恢复四次验证形成闭环。",
        "key_points": ["rsync源目录斜杠", "首次同步与增量同步", "dry-run和--delete风险", "crontab环境与绝对路径", "日志重定向和恢复验证"],
        "difficulties": ["判断带斜杠与不带斜杠的同步结果", "解决交互密码、环境变量和路径导致的定时任务失败", "证明备份能够恢复而不是只证明文件存在"],
        "methods": "项目任务、实践操作、风险演示、恢复验证",
        "intro": "模拟项目配置文件被误删，要求先建立自动增量备份，再通过日志证明任务执行，最后完成恢复。",
        "demos": ["使用rsync同步目录并对比源路径末尾斜杠", "使用--dry-run预览变化", "编写可由cron执行的备份脚本并重定向日志", "模拟误删后从备份恢复并比较内容"],
        "tasks": ["完成首次同步和增量同步", "配置定时备份与运行日志", "模拟删除指定文件", "从备份恢复并验证完整性"],
        "values_detail": "教师结合勒索软件、误删除和备份介质同时损坏的案例，要求学生说明备份副本的位置、访问权限和恢复方法。学生不能为了显示成功手工复制文件冒充定时任务结果，必须用时间戳、日志和文件内容证明cron实际执行；恢复后比较哈希或内容。",
        "verification": "检查首次与增量同步差异、crontab条目和运行日志；删除源文件后从备份恢复，并比较恢复前记录的内容或哈希",
        "homework": "提交备份脚本、crontab、运行日志和恢复验证，写出使用rsync --delete前必须完成的检查",
        "board": ["备份闭环", "源目录 → rsync → 备份目录", "首次同步 → 增量同步", "高风险操作：先--dry-run", "cron执行", "├─ 绝对路径", "├─ 非交互运行", "└─ 日志", "有效备份：能恢复并验证"],
    },
]


def main():
    with ZipFile(DOCX, "r") as zin:
        infos = zin.infolist()
        parts = {info.filename: zin.read(info.filename) for info in infos}
    root = etree.fromstring(parts["word/document.xml"])
    tables = root.findall(f".//{W}tbl")
    if len(tables) != 13:
        raise RuntimeError(f"模板应包含1张基本信息表和12张课次表，实际为{len(tables)}张")
    if len(SESSIONS) != 12:
        raise RuntimeError("第1-4周必须包含12次课")
    for table, session in zip(tables[1:], SESSIONS):
        fill_session(table, session)
    parts["word/document.xml"] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone="yes")
    with NamedTemporaryFile(dir=DOCX.parent, suffix=".docx", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
    try:
        with ZipFile(tmp_path, "w", compression=ZIP_DEFLATED) as zout:
            for info in infos:
                zout.writestr(info, parts[info.filename])
        tmp_path.replace(DOCX)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


if __name__ == "__main__":
    main()
