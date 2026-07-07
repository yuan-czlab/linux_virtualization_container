# 课程教学单元索引（v3.0 — 72+72分段实施）

> 总学时：144；18周 × 8学时/周；每教学单元2学时（90分钟）
>
> 第1—9周《Linux操作系统》72学时；第10—18周《虚拟化容器技术》72学时
> 详细实验组合、成果和实施说明以《04-18周课程进度表》为准。

## 模块与课时

| 模块 | 单元 | 学时 | 周次 | 所属课程 |
|---|---|---:|---|---|
| M1 Linux基础运维 | U01-U12 | 24 | 第1-3周 | Linux操作系统 |
| M2 网络、远程管理与基础防护 | U13-U24 | 24 | 第4-6周 | Linux操作系统 |
| M3 企业服务部署与阶段项目 | U25-U36 | 24 | 第7-9周 | Linux操作系统 |
| M4 虚拟化与多机环境 | U37-U52 | 32 | 第10-13周 | 虚拟化容器技术 |
| M5 Docker容器化与综合项目 | U53-U72 | 40 | 第14-18周 | 虚拟化容器技术 |

## M1 Linux基础运维（U01-U12）

| 单元 | 名称 | 核心内容 |
|---|---|---|
| U01 | 课程介绍、岗位认知与发行版 | Rocky主线、Ubuntu对照、课程成果与考核 |
| U02 | VMware环境与Rocky安装 | 最小化安装、用户、网络、快照起点 |
| U03 | 命令行与发行版对照 | 命令格式、帮助、历史、补全、dnf/apt差异认知 |
| U04 | 目录结构与文件管理 | FHS、touch/cp/mv/rm/mkdir |
| U05 | 文件查看、查找与链接 | cat/less/tail/find/which/link |
| U06 | vim、压缩与归档恢复 | vim基础、tar、备份与恢复验证 |
| U07 | 用户与用户组 | useradd/usermod/passwd/groupadd/id |
| U08 | 文件权限 | rwx、chmod、chown、umask |
| U09 | sudo与最小权限 | visudo、wheel、操作留痕 |
| U10 | dnf与apt软件包管理 | 软件源、清华/阿里镜像、包查询与安装 |
| U11 | systemd与journal日志 | 服务状态、自启、Unit和日志定位 |
| U12 | 系统状态、磁盘与容量识别 | top/free/lsblk/df/du/ps |

## M2 网络、远程管理与基础防护（U13-U24）

| 单元 | 名称 | 核心内容 |
|---|---|---|
| U13 | IP、网卡、路由与DNS客户端 | ip、nmcli、route、resolv.conf |
| U14 | TCP/UDP、端口与监听 | ss、nc、常见端口、服务与端口关系 |
| U15 | DNS解析与hosts | dig/nslookup、hosts、解析故障 |
| U16 | HTTP/HTTPS与curl | 请求、状态码、证书认知、访问验证 |
| U17 | SSH远程管理 | sshd、密码登录、连接排障 |
| U18 | SSH密钥认证 | keygen、authorized_keys、权限 |
| U19 | SSH客户端与文件传输 | ssh config、scp、sftp |
| U20 | rsync增量备份与定时任务 | rsync、crontab、恢复验证 |
| U21 | firewalld基础 | zone、service、port、最小开放 |
| U22 | firewalld规则与验证 | permanent、来源限制、验证和回滚 |
| U23 | SELinux与主机基础防护 | 上下文、Enforcing、权限分层 |
| U24 | 网络与安全综合排障 | IP→路由→服务→端口→防护→日志 |

## M3 企业服务部署与Linux阶段项目（U25-U36）

| 单元 | 名称 | 核心内容 |
|---|---|---|
| U25 | Nginx安装与静态网站 | 安装、目录、systemd、Web前端成果发布 |
| U26 | Nginx虚拟主机与反向代理 | server、location、proxy_pass |
| U27 | Nginx HTTPS、日志与故障 | 证书、access/error日志、403/404/502 |
| U28 | MariaDB部署与安全 | 安装、账号最小权限、监听、远程连接 |
| U29 | 数据库日志、备份与恢复 | mysqldump、恢复验证、备份脚本 |
| U30 | Redis部署、持久化与安全 | RDB/AOF、bind、认证、端口风险 |
| U31 | Git项目获取与版本恢复 | clone/pull/log/status/恢复文件 |
| U32 | Shell巡检与自动化接口 | 退出码、日志、结构化输出、幂等意识 |
| U33 | 阶段项目发布与设计 | 2-3人小组、需求、分工、部署计划 |
| U34 | 服务集成部署 | Nginx+MariaDB+Redis |
| U35 | 故障注入与验收 | 服务、防火墙、日志、备份恢复 |
| U36 | 项目答辩与Linux总结 | 实操演示、部署文档、排障记录 |

## M4 虚拟化与多机环境（U37-U52）

| 单元 | 名称 | 核心内容 |
|---|---|---|
| U37 | 虚拟化与云计算认知 | Type 1/2、VM、容器、云服务器 |
| U38 | 虚拟机资源与虚拟磁盘 | CPU、内存、磁盘和网卡规划 |
| U39 | 快照、克隆与模板机 | 可恢复、可复制、可延续环境 |
| U40 | 虚拟网络模式 | NAT、桥接、仅主机原理 |
| U41 | 网络模式对比实验 | 上网、宿主访问、VM互访和排障 |
| U42 | 多机拓扑与IP规划 | web/db/client、地址与角色规划 |
| U43 | 三机环境搭建 | 主机名、静态IP、hosts |
| U44 | 多机SSH信任与运维入口 | SSH密钥、清单，为自动化课程准备 |
| U45 | 跨主机服务部署 | Nginx、MySQL、Redis分层通信 |
| U46 | 虚拟网络与服务综合排障 | IP冲突、路由、端口、防火墙 |
| U47 | KVM/libvirt架构认知 | 条件实验；嵌套虚拟化未验证时教师演示 |
| U48 | virsh与qcow2操作体验 | 条件实验；不作为必做考核 |
| U49 | KVM网络认知 | virbr0、NAT与桥接，教师演示/选做 |
| U50 | ESXi与vCenter认知 | 企业虚拟化架构和管理入口 |
| U51 | 云服务器、镜像和安全组 | cloud-init、镜像、快照、安全组 |
| U52 | 虚拟化模块综合交付 | OVA、拓扑图、IP表、配置仓库 |

## M5 Docker容器化与综合项目（U53-U72）

| 单元 | 名称 | 核心内容 |
|---|---|---|
| U53 | 容器与虚拟机对比 | Docker架构、镜像和容器 |
| U54 | Docker安装与镜像准备 | 服务、镜像获取、离线/教师方案 |
| U55 | 容器生命周期与日志 | run/ps/logs/exec/inspect |
| U56 | 容器部署常见服务 | Nginx/MySQL/Redis |
| U57 | 端口映射 | 端口规划、冲突和访问验证 |
| U58 | 数据卷与备份恢复 | bind、volume、持久化 |
| U59 | Docker网络 | bridge、自定义网络、容器DNS |
| U60 | 健康检查、资源限制与排障 | healthcheck、CPU/内存、日志 |
| U61 | Dockerfile基础 | FROM/RUN/COPY/WORKDIR/CMD |
| U62 | Dockerfile优化与安全 | 多阶段构建、非root、敏感信息 |
| U63 | 镜像版本与Registry概念 | tag、推拉流程、Harbor认知 |
| U64 | Docker Compose入门 | YAML、services、up/down/ps/logs |
| U65 | Compose多服务编排 | network/volume/environment |
| U66 | Compose健康检查与配置分离 | depends_on、healthcheck、.env |
| U67 | Compose项目实战 | 多服务联调、持久化、排障 |
| U68 | K8s操作体验 | apply/get/logs/describe/exec/Service |
| U69 | 综合项目设计与环境恢复 | 复用三机模板、需求与架构 |
| U70 | 多机服务容器化部署 | Nginx+应用+MySQL+Redis |
| U71 | 故障注入与综合验收 | 网络、服务、容器、数据恢复 |
| U72 | 项目答辩与环境归档 | 报告、OVA、配置仓库，供大二下续用 |

## 实验资源使用原则

现有Lab01-Lab63作为实验资源池，不再机械规定“一个单元必须对应一个完整Lab”。教师按《04-18周课程进度表》组合核心实验、拓展实验和项目任务。Lab62用于K8s操作体验，Lab63用于虚拟化阶段和学期末的环境归档恢复。这样可以在严格的72+72课时边界内保留现有材料，同时避免为了完成实验数量挤压项目、排障和答辩时间。
