#!/usr/bin/env python3
"""Generate the v3 XMind course knowledge map from the authoritative Markdown index."""

from __future__ import annotations

import base64
import json
import re
import uuid
import zipfile
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "01-unit-index.md"
SCHEDULE_FILE = BASE_DIR / "04-18周课程进度表.md"
OUTPUT_FILE = BASE_DIR / "03-xmind-两门课程知识图谱-v3.xmind"


def make_id(key: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_URL, f"course-map-v3:{key}").hex[:26]


def topic(title: str, children: list[dict] | None = None, *, key: str | None = None,
          folded: bool = False) -> dict:
    node = {"id": make_id(key or title), "class": "topic", "title": title}
    if folded:
        node["branch"] = "folded"
    if children:
        node["children"] = {"attached": children}
    return node


def leaf(title: str, key: str) -> dict:
    return topic(title, key=key)


def parse_units() -> dict[str, tuple[str, str]]:
    units: dict[str, tuple[str, str]] = {}
    pattern = re.compile(r"^\| (U\d{2}) \| ([^|]+?) \| ([^|]+?) \|$")
    for line in INDEX_FILE.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            units[match.group(1)] = (match.group(2).strip(), match.group(3).strip())
    if len(units) != 72:
        raise RuntimeError(f"Expected 72 units, found {len(units)}")
    return units


def parse_deliverables() -> dict[str, str]:
    deliverables: dict[str, str] = {}
    pattern = re.compile(
        r"^\| 第\d+周-\d \| (U\d{2}) \| [^|]+? \| ([^|]+?) \| [^|]+? \|$"
    )
    for line in SCHEDULE_FILE.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            deliverables[match.group(1)] = match.group(2).strip()
    if len(deliverables) != 72:
        raise RuntimeError(f"Expected 72 schedule mappings, found {len(deliverables)}")
    return deliverables


def unit_nodes(start: int, end: int, units: dict[str, tuple[str, str]],
               deliverables: dict[str, str]) -> list[dict]:
    result = []
    for number in range(start, end + 1):
        unit_id = f"U{number:02d}"
        name, core = units[unit_id]
        result.append(topic(
            f"{unit_id} {name}",
            [
                leaf(f"核心内容：{core}", f"{unit_id}:core"),
                leaf(f"实验/成果：{deliverables[unit_id]}", f"{unit_id}:deliverable"),
            ],
            key=unit_id,
            folded=True,
        ))
    return result


def build_content() -> list[dict]:
    units = parse_units()
    deliverables = parse_deliverables()

    module_1 = topic(
        "M1 Linux基础运维｜24学时｜第1-3周｜U01-U12",
        [
            leaf("目标：能够安装、操作和管理一台Linux服务器", "m1:goal"),
            *unit_nodes(1, 12, units, deliverables),
        ], key="m1", folded=True,
    )
    module_2 = topic(
        "M2 网络、远程管理与基础防护｜24学时｜第4-6周｜U13-U24",
        [
            leaf("目标：能够远程管理服务器，完成最小防护和逐层排障", "m2:goal"),
            *unit_nodes(13, 24, units, deliverables),
        ], key="m2", folded=True,
    )
    module_3 = topic(
        "M3 企业服务部署与Linux阶段项目｜24学时｜第7-9周｜U25-U36",
        [
            leaf("目标：以Nginx为Web重点，完成数据库、中间件、脚本和项目交付", "m3:goal"),
            *unit_nodes(25, 36, units, deliverables),
        ], key="m3", folded=True,
    )
    module_4 = topic(
        "M4 虚拟化与多机环境｜32学时｜第10-13周｜U37-U52",
        [
            leaf("目标：创建、管理、排障并归档可跨学期复用的三机环境", "m4:goal"),
            leaf("实施约束：KVM取决于嵌套虚拟化；未验证时教师演示/学生选做", "m4:kvm"),
            *unit_nodes(37, 52, units, deliverables),
        ], key="m4", folded=True,
    )
    module_5 = topic(
        "M5 Docker容器化与综合项目｜40学时｜第14-18周｜U53-U72",
        [
            leaf("目标：使用Docker/Compose交付多服务应用，具备基础容器排障能力", "m5:goal"),
            leaf("K8s边界：本学期只做操作体验；大二下《云计算应用》系统讲授", "m5:k8s-boundary"),
            *unit_nodes(53, 72, units, deliverables),
        ], key="m5", folded=True,
    )

    overview = topic("课程总体设计", [
        leaf("专业：计算机应用技术｜就业：云计算运维、Linux运维、网络工程、系统实施", "overview:major"),
        leaf("总学时：144｜18周｜每周8学时｜每单元2学时", "overview:hours"),
        leaf("前9周：《Linux操作系统》72学时", "overview:linux"),
        leaf("后9周：《虚拟化容器技术》72学时", "overview:virt"),
        leaf("操作系统：Rocky Linux 9主线 + Ubuntu Server 22.04 LTS对照", "overview:os"),
        leaf("教学方式：讲解演示 + 上机实操 + 故障注入 + 项目答辩", "overview:method"),
        leaf("组织方式：2-3人小组｜全部上机考核｜项目与答辩", "overview:assessment"),
    ], key="overview", folded=True)

    prerequisites = topic("课程衔接", [
        topic("先修课程", [
            leaf("大一上：C语言程序设计、Web前端、计算机组成原理", "pre:first"),
            leaf("大一下：Python程序设计、计算机网络技术、数据库原理及应用（MySQL）", "pre:second"),
        ], key="pre", folded=True),
        topic("同学期课程", [
            leaf("交换路由技术：eNSP、交换机、路由器、VLAN和路由协议", "parallel:network"),
            leaf("Python自动化运维：Paramiko、Ansible、Fabric", "parallel:python"),
            leaf("本课程提供：IP规划、SSH密钥、主机清单、退出码和结构化巡检结果", "parallel:interface"),
        ], key="parallel", folded=True),
        topic("大二下后续课程", [
            leaf("网络安全基础：防火墙原理、安全加固、日志审计和攻防基础", "after:security"),
            leaf("云计算应用：重点讲Kubernetes和云平台应用", "after:cloud"),
            leaf("企业级综合实训：eNSP网络→Linux服务器→安全→服务/容器→通信验收", "after:project"),
        ], key="after", folded=True),
    ], key="prerequisites", folded=True)

    technology_focus = topic("技术重点与边界", [
        topic("重点掌握", [
            leaf("Linux命令、用户权限、软件包、systemd、日志、备份恢复", "focus:linux"),
            leaf("SSH、DNS客户端、端口、firewalld、SELinux和综合排障", "focus:network"),
            leaf("Nginx静态发布、虚拟主机、反向代理、HTTPS、日志和403/404/502", "focus:nginx"),
            leaf("MariaDB运行维护、Redis安全、Git部署、Shell巡检", "focus:services"),
            leaf("VMware、多机环境、Docker、Dockerfile、Compose和项目交付", "focus:platform"),
        ], key="focus", folded=True),
        topic("了解/教师演示", [
            leaf("Apache/Tomcat、FTP、NFS/iSCSI", "awareness:web"),
            leaf("ESXi/vCenter、KVM条件实验、Registry/Harbor", "awareness:platform"),
            leaf("LVS/Keepalived、Zabbix/Prometheus、Jenkins", "awareness:ops"),
        ], key="awareness", folded=True),
        topic("后续课程深入", [
            leaf("nftables/iptables、安全审计与系统加固", "later:security"),
            leaf("Kubernetes集群、网络、存储、调度、Helm、监控和日志", "later:k8s"),
            leaf("云厂商产品、CI/CD和企业级高可用", "later:cloud"),
        ], key="later", folded=True),
    ], key="technology-focus", folded=True)

    projects = topic("实验、项目与考核", [
        leaf("实验资源池：Lab01-Lab63，按核心/拓展组合使用", "projects:labs"),
        topic("Linux阶段项目｜第9周", [
            leaf("Nginx + MariaDB + Redis + Shell巡检", "projects:stage-stack"),
            leaf("故障注入、部署文档、排障记录和答辩", "projects:stage-delivery"),
        ], key="projects:stage", folded=True),
        topic("虚拟化容器综合项目｜第18周", [
            leaf("三机环境 + 多服务容器化 + Compose", "projects:final-stack"),
            leaf("网络/服务/容器/数据故障验收", "projects:final-fault"),
            leaf("提交OVA、拓扑图、IP表、配置仓库和运维报告", "projects:final-delivery"),
        ], key="projects:final", folded=True),
        leaf("考核：过程实操 + 项目交付 + 文档与答辩；不单设笔试", "projects:assessment"),
    ], key="projects", folded=True)

    environment = topic("实验环境与跨学期复用", [
        leaf("宿主机：Windows 10/11 + VMware Workstation", "env:host"),
        leaf("软件源：清华源/阿里源 + 教师离线包回退", "env:mirrors"),
        leaf("Docker镜像：使用教师已有获取方案，不依赖Docker Hub", "env:docker"),
        leaf("三机标准：web-server / db-server / client", "env:hosts"),
        leaf("统一保存：OVA、快照、IP规划、SSH清单、配置仓库、数据库备份、Compose文件", "env:archive"),
        leaf("大二下延续：eNSP Cloud节点接入VMware/Linux环境，继续安全、云计算和综合实训", "env:continuity"),
    ], key="environment", folded=True)

    classroom = topic("课堂实施与内容增强", [
        leaf("90分钟：导入5 + 理论20-25 + 演示10-15 + 核心实验30 + 独立任务15-20 + 复盘5", "classroom:flow"),
        leaf("每单元讲清：解决什么问题、处于哪一层、正常条件、验证方法、故障证据", "classroom:theory"),
        leaf("理论指南：14-课堂实施与理论讲授指南.md", "classroom:guide"),
        topic("本轮增强实验", [
            leaf("Lab13：磁盘/分区/文件系统/挂载点与容量阈值", "classroom:lab13"),
            leaf("Lab21：rsync+crontab自动备份、日志和恢复验证", "classroom:lab21"),
            leaf("Lab41：NAT/桥接/仅主机数据路径与连接矩阵", "classroom:lab41"),
            leaf("Lab46：三机身份、IP、SSH入口和自动化主机清单", "classroom:lab46"),
            leaf("Lab56：healthcheck、资源限制与OOM排障", "classroom:lab56"),
            leaf("Lab62：Kubernetes操作体验", "classroom:lab62"),
            leaf("Lab63：跨学期环境归档、校验和恢复", "classroom:lab63"),
        ], key="classroom:enhanced-labs", folded=True),
        topic("负载控制", [
            leaf("核心实验：课堂完成关键步骤和验收", "classroom:core"),
            leaf("合并/拓展实验：选择核心场景，其余课后完成", "classroom:extension"),
            leaf("KVM条件实验：嵌套虚拟化验证通过才全员实施", "classroom:conditional"),
            leaf("Lab63跨U52/U72分阶段完成", "classroom:cross-unit"),
        ], key="classroom:load", folded=True),
    ], key="classroom", folded=True)

    root = topic(
        "《Linux操作系统》+《虚拟化容器技术》课程知识图谱",
        [
            overview,
            topic("课程一：《Linux操作系统》｜72学时｜第1-9周", [module_1, module_2, module_3], key="course-linux"),
            topic("课程二：《虚拟化容器技术》｜72学时｜第10-18周", [module_4, module_5], key="course-virt"),
            technology_focus,
            classroom,
            projects,
            prerequisites,
            environment,
        ], key="root",
    )
    root["structureClass"] = "org.xmind.ui.map.clockwise"

    return [{
        "id": make_id("sheet"),
        "class": "sheet",
        "title": "两门课程知识图谱",
        "rootTopic": root,
    }]


def write_xmind(content: list[dict]) -> None:
    metadata = {
        "dataStructureVersion": "2",
        "layoutEngineVersion": "3",
        "creator": {"name": "Course Design Generator", "version": "3.0"},
        "activeSheetId": make_id("sheet"),
    }
    manifest = {
        "file-entries": {
            "content.json": {},
            "metadata.json": {},
            "Thumbnails/thumbnail.png": {},
        }
    }
    transparent_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )

    with zipfile.ZipFile(OUTPUT_FILE, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("content.json", json.dumps(content, ensure_ascii=False, separators=(",", ":")))
        archive.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False, separators=(",", ":")))
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, separators=(",", ":")))
        archive.writestr("Thumbnails/thumbnail.png", transparent_png)


if __name__ == "__main__":
    document = build_content()
    write_xmind(document)
    print(OUTPUT_FILE)
