# 课程教学单元索引（v2.0 — 对齐教学大纲）

> 总课时：144 | 18周 × 8节/周 | 每教学单元 = 2课时（90分钟）
> 大纲依据：五模块 28/26/28/26/36
> 主线系统：Rocky Linux 9 | 对照系统：Ubuntu Server 24.04 LTS

---

## 模块一：Linux基础运维（U01-U14 · 28课时 · 第1-4周）

### 第1周：走进Linux（8课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U01 | 课程介绍 + Linux与运维岗位 | 理论 | 课程安排/考核方式；操作系统角色；Linux在服务器/云计算/运维中的作用；初级运维岗位典型工作任务 | — |
| U02 | Linux发行版家族 | 理论+实操 | 内核vs发行版；Debian系vs RHEL系；Rocky/Ubuntu Server/CentOS/RHEL关系；为什么主线用Rocky、对照用Ubuntu Server | Lab01：VMware安装Ubuntu Server 24.04 |
| U03 | Rocky Linux 9 安装 | 实操 | VMware创建VM；Rocky Linux 9最小化安装；root与普通用户；命令行终端初识 | Lab02：VMware安装Rocky Linux 9 |
| U04 | 基础命令入门 | 实操 | 命令格式/参数/选项；pwd/ls/cd/clear/whoami/hostname；man/--help/history；Tab补全 | Lab03：基础命令练习 |

### 第2周：文件、目录与文本编辑（8课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U05 | 目录结构与文件操作 | 理论+实操 | FHS目录树（/etc /var /home /usr /opt /tmp）；touch/cp/mv/rm/mkdir；通配符 | Lab04：目录导航与文件操作 |
| U06 | 文件查看与查找 | 实操 | cat/less/head/tail；find（-name/-type/-size/-mtime）；which/whereis；inode与链接 | Lab05：文件查看与查找 |
| U07 | vim文本编辑（上） | 实操 | vim三种模式；i/a/o进入编辑；hjkl移动；dd/yy/p/u基础编辑；:wq/:q! | Lab06：vim基础操作 |
| U08 | vim文本编辑（下）+ 压缩解压 | 实操 | 搜索替换（/ :%s）；分屏（:split :vsplit）；.vimrc配置；tar（-czf/-xzf）；zip/unzip | Lab07：vim进阶+归档 |

### 第3周：用户、权限与软件包（8课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U09 | 用户与用户组管理 | 实操 | root vs普通用户；/etc/passwd /etc/shadow /etc/group；useradd/usermod/userdel；passwd；groupadd；id/groups/who | Lab08：用户与组管理 |
| U10 | 文件权限管理 | 实操 | rwx（文件vs目录）；ugo模型；chmod（符号/数字）；chown/chgrp；umask | Lab09：权限场景练习 |
| U11 | sudo与最小权限 | 实操 | sudo原理；visudo配置；wheel组；免密码sudo；SUID/SGID/Sticky bit概述；sudo日志 | Lab10：sudo权限控制 |
| U12 | 软件包管理（dnf + apt对照） | 实操 | dnf（install/remove/search/update/repolist）；epel-release；apt对照；软件源与镜像源概念；rpm/dpkg基础查询 | Lab11：dnf+apt包管理对照 |

### 第4周：服务管理与系统监控（4课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U13 | systemd服务管理 | 理论+实操 | systemd设计理念；Unit类型（service/timer）；systemctl（start/stop/restart/status/enable/disable）；服务状态（active/inactive/failed） | Lab12：systemd服务管理 |
| U14 | 系统状态查看 | 实操 | CPU（top/uptime）；内存（free -h）；磁盘（df -h/du -sh）；进程（ps aux）；journalctl日志；sshd/nginx服务案例 | Lab13：系统状态监控 |

---

## 模块二：Linux网络、协议与远程管理（U15-U27 · 26课时 · 第4-7周）

### 第4-5周：网络基础与协议（8课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U15 | IP地址与网络接口 | 理论+实操 | IP地址/子网掩码/网关/DNS；网卡命名（ens33）；ip addr/ip route；hostnamectl；nmcli配置静态IP | Lab14：网络基础配置 |
| U16 | TCP/UDP与端口 | 理论+实操 | TCP vs UDP区别；服务与端口关系；常见端口（22/80/443/3306/6379/8080）；ss -tunlp；端口占用；"服务启动"vs"端口可访问" | Lab15：端口与服务 |
| U17 | DNS解析 | 理论+实操 | DNS作用；域名→IP过程；/etc/resolv.conf；/etc/hosts本地解析；nslookup/dig基础；IP能访问但域名不能访问的排障 | Lab16：DNS配置与排障 |
| U18 | HTTP/HTTPS与curl | 理论+实操 | HTTP vs HTTPS；80 vs 443端口；curl测试HTTP访问；状态码（200/301/403/404/502）；HTTPS证书概念 | Lab17：curl与HTTP测试 |

### 第5-6周：SSH与远程管理（8课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U19 | SSH原理与基础 | 理论+实操 | SSH在运维中的作用；sshd服务；ssh user@ip；端口22；密码认证；SSH排障（连接超时/拒绝连接/权限问题） | Lab18：SSH基础连接 |
| U20 | SSH密钥认证 | 实操 | 密钥认证优于密码认证；ssh-keygen（-t ed25519）；ssh-copy-id；authorized_keys；私钥权限600 | Lab19：SSH密钥认证 |
| U21 | SSH客户端进阶 | 实操 | ~/.ssh/config（Host/HostName/User/Port）；别名登录；ssh-agent/ssh-add；跳板机概念 | Lab20：SSH配置进阶 |
| U22 | 文件传输 | 实操 | scp（本地↔远程）；sftp交互；rsync（-avz增量同步）；FTP了解（不做重点） | Lab21：文件传输实战 |

### 第6-7周：防火墙与网络排障（10课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U23 | firewalld防火墙（上） | 实操 | 防火墙在运维中的作用；firewalld架构（zone/service）；firewall-cmd基础；查看规则（--list-all） | Lab22：firewalld基础 |
| U24 | firewalld防火墙（下） | 实操 | 开放端口（--add-port）；开放服务（--add-service）；--permanent + --reload；rich-rule简介；ufw对照 | Lab23：firewalld端口开放 |
| U25 | SELinux基础认知 | 理论+实操 | DAC vs MAC；三种模式（Enforcing/Permissive/Disabled）；上下文；常见SELinux故障场景；getenforce/setenforce | Lab24：SELinux初识 |
| U26 | 网络排障流程 | 实操 | 排障链：VM运行→IP正确→ping通→DNS正常→服务启动→端口监听→防火墙放行→日志报错；综合排障演练 | Lab25：网络排障综合 |
| U27 | 模块二综合练习 | 实操 | 多场景任务：远程管理+文件传输+防火墙配置+排障；模拟3个真实故障场景 | Lab26：模块二综合 |

---

## 模块三：企业常见服务部署与基础排障（U28-U41 · 28课时 · 第7-11周）

### 第7-8周：Nginx Web服务（8课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U28 | Nginx安装与基础 | 实操 | 安装Nginx；systemctl管理；默认站点结构；/usr/share/nginx/html；nginx.conf初识 | Lab27：Nginx安装部署 |
| U29 | Nginx虚拟主机 | 实操 | server块；server_name；root目录；多站点配置；修改默认网页 | Lab28：Nginx虚拟主机 |
| U30 | Nginx访问测试与日志 | 实操 | curl/浏览器访问测试；access.log格式解读；error.log排障；tail -f实时查看；403/404/502错误初识 | Lab29：Nginx日志分析 |
| U31 | Nginx + HTTPS基础 | 实操 | 443端口；SSL/TLS概念；自签名证书生成（openssl）；Nginx SSL配置；HTTP跳转HTTPS | Lab30：Nginx HTTPS配置 |

### 第8-9周：数据库与中间件（10课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U32 | MySQL/MariaDB安装部署 | 实操 | MariaDB安装；systemctl管理；3306端口；mysql_secure_installation安全初始化 | Lab31：MariaDB安装 |
| U33 | 数据库基础运维 | 实操 | 本机连接（mysql命令）；创建测试库和用户（CREATE DATABASE/GRANT）；简单远程连接；3306端口安全风险 | Lab32：数据库基础操作 |
| U34 | 数据库备份与日志 | 实操 | mysqldump基础备份；数据库日志查看；/var/log/mariadb/；慢查询日志概念 | Lab33：数据库备份 |
| U35 | Redis安装与基础 | 理论+实操 | Redis作用（缓存/键值）；安装Redis；6379端口；redis-cli连接测试（SET/GET/PING）；端口安全风险 | Lab34：Redis部署测试 |
| U36 | Redis持久化与安全 | 实操 | RDB/AOF持久化概念；requirepass密码认证；bind绑定地址；protected-mode；Redis与Docker Compose项目关系 | Lab35：Redis安全配置 |

### 第9-10周：Git与项目获取（6课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U37 | Git基础与仓库操作 | 理论+实操 | Git在项目部署中的作用；安装Git；git clone；git pull；git log；GitHub/Gitee/GitLab作为代码仓库 | Lab36：Git基础操作 |
| U38 | Git分支与协作基础 | 实操 | git branch；git checkout/switch；.gitignore简介；git status/diff；简单协作流程 | Lab37：Git分支管理 |
| U39 | 模块三阶段项目启动 | 项目 | 发布"单机Linux Web服务部署与排障"项目；任务分解；从Git拉取项目初始文件 | — |

### 第10-11周：Shell脚本与监控（4课时 + 阶段项目）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U40 | Shell基础运维脚本 | 实操 | Shebang（#!/bin/bash）；变量/echo；if条件；for循环；管道\|和重定向>；crontab定时任务；系统巡检脚本；服务检查脚本 | Lab38：Shell运维脚本 |
| U41 | 阶段项目：单机Linux服务部署与排障 | 项目 | 安装Nginx→修改网页→开放80端口→安装MySQL→连接测试→备份→安装Redis→Shell巡检脚本→模拟2个故障→部署文档+排障记录 | 阶段项目交付 |

---

## 模块四：虚拟化技术与多机环境搭建（U42-U54 · 26课时 · 第11-14周）

### 第11-12周：虚拟化基础与VM管理（8课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U42 | 虚拟化与云计算认知 | 理论 | 虚拟化定义；物理机/虚拟机/云服务器关系；Type1 vs Type2；VMware/VirtualBox/UTM；虚拟化是云计算基础 | — |
| U43 | 虚拟机创建与Linux安装 | 实操 | CPU/内存/磁盘/网卡资源分配；ISO镜像使用；Rocky Linux安装回顾；Ubuntu Server对照安装；初始化主机名/用户/网络 | Lab39：创建多台VM |
| U44 | 快照、克隆与模板机 | 实操 | 快照的作用与原理；快照创建与恢复；完整克隆vs链接克隆；模板机制作；实验前快照规范 | Lab40：快照与克隆 |
| U45 | 虚拟网络模式（上） | 理论+实操 | NAT模式原理；桥接模式原理；仅主机模式原理；虚拟网段与DHCP | Lab41：虚拟网络模式 |

### 第12-13周：虚拟网络与多机环境（10课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U46 | 虚拟网络模式（下） | 实操 | 三种模式对比实验；IP冲突问题；网段不一致问题；无法上网排障；宿主机无法访问VM排障 | Lab42：网络模式对比 |
| U47 | KVM虚拟化入门 | 理论+实操 | KVM架构；libvirt；virt-manager图形界面；virsh基础命令；KVM vs VMware对比 | Lab43：KVM基础 |
| U48 | KVM虚拟机管理 | 实操 | virt-install命令行创建VM；virsh（list/start/shutdown/destroy）；存储池；qcow2格式 | Lab44：virsh管理VM |
| U49 | KVM虚拟化网络 | 实操 | NAT网络（virbr0）；桥接网络（bridge）；隔离网络；多VM网络互通 | Lab45：KVM网络 |
| U50 | 多机服务器环境搭建 | 项目 | web-server + db-server + client三台VM；三机互通；主机名/IP/hosts配置；宿主机SSH连接多台VM | Lab46：三机环境搭建 |

### 第13-14周：多机环境管理与文档（8课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U51 | 多机服务部署 | 实操 | web-server部署Nginx；db-server部署MySQL+Redis；client测试访问；跨主机服务连通 | Lab47：多机服务部署 |
| U52 | 云服务器与虚拟化拓展 | 理论+实操 | 云服务器概念（ECS/EC2）；镜像/快照/安全组与防火墙对应关系；cloud-init自动化；virt-builder快速构建 | Lab48：云服务概念体验 |
| U53 | 虚拟化综合练习 | 实操 | 多场景：创建/快照/克隆/网络切换/多机互通/服务部署/故障模拟 | Lab49：虚拟化综合 |
| U54 | 拓扑图与IP规划文档 | 项目 | 绘制拓扑图（draw.io或手绘）；编写IP地址规划表；编写部署文档；模块四成果整理 | 模块四文档交付 |

---

## 模块五：Docker容器化部署与综合项目（U55-U72 · 36课时 · 第14-18周）

### 第14-15周：Docker基础（8课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U55 | 容器化技术认知 | 理论 | 容器是什么；Docker是什么；镜像与容器关系；容器vs虚拟机（架构/速度/资源/隔离性）；容器解决的核心问题（环境一致/快速部署/隔离运行/便于迁移）；Docker在DevOps和云计算中位置 | — |
| U56 | Docker安装与镜像管理 | 实操 | 安装Docker Engine；systemctl status docker；docker pull/images/search/rmi/tag；镜像分层概念；命名规范 | Lab50：Docker安装与镜像 |
| U57 | Docker容器基础操作 | 实操 | docker run（-d/-it/--name/--rm/-p）；docker ps/logs/stop/start/restart/rm；docker exec -it进入容器；docker inspect | Lab51：Docker容器操作 |
| U58 | Docker部署常见服务 | 实操 | Docker部署Nginx；Docker部署MySQL；Docker部署Redis；端口映射验证；docker logs查看日志 | Lab52：Docker部署服务 |

### 第15-16周：Docker端口、数据卷与网络（8课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U59 | Docker端口映射 | 实操 | -p（宿主机端口:容器端口）；端口冲突排查；多个容器端口规划；ss -tunlp验证 | Lab53：端口映射实战 |
| U60 | Docker数据卷 | 实操 | -v挂载（bind mount vs volume）；docker volume create/ls/inspect；数据持久化验证；MySQL数据卷案例；卷权限问题 | Lab54：数据卷与持久化 |
| U61 | Docker网络（上） | 实操 | bridge网络（docker0）；自定义网络（docker network create）；容器名DNS解析；容器间通信 | Lab55：Docker网络 |
| U62 | Docker网络（下）+ 排障 | 实操 | host/none网络模式；网络不通排障（端口冲突/卷权限/容器启动失败/网络不通）；多容器网络场景 | Lab56：Docker网络排障 |

### 第16-17周：Dockerfile与Compose（10课时）

| 编号 | 单元名称 | 类型 | 核心内容 | 配套实验 |
|------|---------|------|---------|---------|
| U63 | Dockerfile基础 | 实操 | Dockerfile作用；FROM/RUN/COPY/WORKDIR/EXPOSE/CMD指令；docker build；构建上下文；层缓存 | Lab57：编写Dockerfile |
| U64 | Dockerfile实战 | 实操 | 自定义Nginx静态网页镜像；ENV/ARG参数化；.dockerignore；docker history查看构建历史 | Lab58：Dockerfile实战 |
| U65 | Docker Compose入门 | 实操 | Compose作用；YAML语法；services/ports/volumes；docker compose up -d/down/ps/logs | Lab59：Compose入门 |
| U66 | Docker Compose多服务 | 实操 | networks/environment/depends_on；多服务编排（Nginx+MySQL+Redis）；docker compose logs查看多服务日志 | Lab60：Compose多服务编排 |
| U67 | Docker Compose项目实战 | 实操 | 从Git拉取项目代码→编写Compose文件→一键启动→数据卷持久化→自定义网络→访问验证→docker compose down清理 | Lab61：Compose项目实战 |

### 第17-18周：综合项目（10课时）

| 编号 | 单元名称 | 类型 | 核心内容 |
|------|---------|------|---------|
| U68 | 综合项目发布与选题 | 项目 | 发布"中小型企业基础运维环境搭建与容器化部署"项目；分组（2-3人）；选题与需求分析；架构设计 |
| U69 | Linux基础环境搭建 | 项目 | 安装Rocky Linux；配置用户权限/软件源；配置IP/SSH/DNS/hosts/防火墙 |
| U70 | 服务部署与虚拟化 | 项目 | 部署Nginx+MySQL+Redis；Git拉取代码；Shell脚本；搭建多机环境（web-server/db-server/client） |
| U71 | Docker容器化部署 | 项目 | 编写Dockerfile；Docker Compose编排；数据卷持久化；多服务联调；故障模拟与排查（3-5个故障） |
| U72 | 项目答辩与课程总结 | 答辩 | 每组15分钟（方案阐述+实操演示+故障注入+问答）；提交拓扑图/IP规划表/部署文档/排障报告/Compose文件 |

---

## 实验清单汇总

| 编号 | 实验名称 | 所属单元 | 模块 |
|------|---------|---------|------|
| Lab01 | VMware安装Ubuntu Server 24.04 | U02 | M1 |
| Lab02 | VMware安装Rocky Linux 9 | U03 | M1 |
| Lab03 | 基础命令练习 | U04 | M1 |
| Lab04 | 目录导航与文件操作 | U05 | M1 |
| Lab05 | 文件查看与查找 | U06 | M1 |
| Lab06 | vim基础操作 | U07 | M1 |
| Lab07 | vim进阶+归档 | U08 | M1 |
| Lab08 | 用户与组管理 | U09 | M1 |
| Lab09 | 权限场景练习 | U10 | M1 |
| Lab10 | sudo权限控制 | U11 | M1 |
| Lab11 | dnf+apt包管理对照 | U12 | M1 |
| Lab12 | systemd服务管理 | U13 | M1 |
| Lab13 | 系统状态监控 | U14 | M1 |
| Lab14 | 网络基础配置 | U15 | M2 |
| Lab15 | 端口与服务 | U16 | M2 |
| Lab16 | DNS配置与排障 | U17 | M2 |
| Lab17 | curl与HTTP测试 | U18 | M2 |
| Lab18 | SSH基础连接 | U19 | M2 |
| Lab19 | SSH密钥认证 | U20 | M2 |
| Lab20 | SSH配置进阶 | U21 | M2 |
| Lab21 | 文件传输实战 | U22 | M2 |
| Lab22 | firewalld基础 | U23 | M2 |
| Lab23 | firewalld端口开放 | U24 | M2 |
| Lab24 | SELinux初识 | U25 | M2 |
| Lab25 | 网络排障综合 | U26 | M2 |
| Lab26 | 模块二综合 | U27 | M2 |
| Lab27 | Nginx安装部署 | U28 | M3 |
| Lab28 | Nginx虚拟主机 | U29 | M3 |
| Lab29 | Nginx日志分析 | U30 | M3 |
| Lab30 | Nginx HTTPS配置 | U31 | M3 |
| Lab31 | MariaDB安装 | U32 | M3 |
| Lab32 | 数据库基础操作 | U33 | M3 |
| Lab33 | 数据库备份 | U34 | M3 |
| Lab34 | Redis部署测试 | U35 | M3 |
| Lab35 | Redis安全配置 | U36 | M3 |
| Lab36 | Git基础操作 | U37 | M3 |
| Lab37 | Git分支管理 | U38 | M3 |
| Lab38 | Shell运维脚本 | U40 | M3 |
| Lab39 | 创建多台VM | U43 | M4 |
| Lab40 | 快照与克隆 | U44 | M4 |
| Lab41 | 虚拟网络模式 | U45 | M4 |
| Lab42 | 网络模式对比 | U46 | M4 |
| Lab43 | KVM基础 | U47 | M4 |
| Lab44 | virsh管理VM | U48 | M4 |
| Lab45 | KVM网络 | U49 | M4 |
| Lab46 | 三机环境搭建 | U50 | M4 |
| Lab47 | 多机服务部署 | U51 | M4 |
| Lab48 | 云服务概念体验 | U52 | M4 |
| Lab49 | 虚拟化综合 | U53 | M4 |
| Lab50 | Docker安装与镜像 | U56 | M5 |
| Lab51 | Docker容器操作 | U57 | M5 |
| Lab52 | Docker部署服务 | U58 | M5 |
| Lab53 | 端口映射实战 | U59 | M5 |
| Lab54 | 数据卷与持久化 | U60 | M5 |
| Lab55 | Docker网络 | U61 | M5 |
| Lab56 | Docker网络排障 | U62 | M5 |
| Lab57 | 编写Dockerfile | U63 | M5 |
| Lab58 | Dockerfile实战 | U64 | M5 |
| Lab59 | Compose入门 | U65 | M5 |
| Lab60 | Compose多服务编排 | U66 | M5 |
| Lab61 | Compose项目实战 | U67 | M5 |

---

## 统计

| 模块 | 课时 | 单元数 | 实验数 | 周次 | 占比 |
|------|------|--------|--------|------|------|
| M1 Linux基础运维 | 28 | 14 | 13 | 1-4 | 19% |
| M2 网络、协议与远程管理 | 26 | 13 | 13 | 4-7 | 18% |
| M3 企业常见服务部署与排障 | 28 | 14 | 12+阶段项目 | 7-11 | 19% |
| M4 虚拟化技术与多机环境 | 26 | 13 | 11+文档 | 11-14 | 18% |
| M5 Docker容器化与综合项目 | 36 | 18 | 12+综合项目 | 14-18 | 25% |
| **合计** | **144** | **72** | **61+2项目** | **1-18** | **100%** |
