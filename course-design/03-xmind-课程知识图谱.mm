<map version="1.0.1">
<node TEXT="Linux与虚拟化容器技术">
<node TEXT="模块一：Linux基础运维（28课时·第1-4周）" FOLDED="true">
<node TEXT="1.1 走进Linux（第1周）">
<node TEXT="Linux与运维岗位认知"/>
<node TEXT="Linux内核与发行版家族"/>
<node TEXT="Ubuntu Server 24.04 LTS 安装与体验"/>
<node TEXT="Rocky Linux 9 最小化安装"/>
<node TEXT="发行版深度对比（apt vs dnf）"/>
<node TEXT="命令行终端基本使用"/>
<node TEXT="命令格式/参数/选项"/>
<node TEXT="帮助命令（man/--help/history）"/>
<node TEXT="Tab补全/Ctrl+R搜索"/>
</node>
<node TEXT="1.2 文件、目录与文本编辑（第2周）">
<node TEXT="Linux目录结构FHS"/>
<node TEXT="文件操作（touch/cp/mv/rm/mkdir）"/>
<node TEXT="通配符（* ? [] {}）"/>
<node TEXT="文件查看（cat/less/head/tail）"/>
<node TEXT="文件查找（find/which/whereis）"/>
<node TEXT="硬链接与软链接（inode）"/>
<node TEXT="vim编辑器（三模式/hjkl/搜索替换）"/>
<node TEXT="压缩与解压（tar/zip/unzip）"/>
</node>
<node TEXT="1.3 用户、权限与软件包（第3周）">
<node TEXT="root与普通用户"/>
<node TEXT="用户管理（useradd/passwd/usermod）"/>
<node TEXT="用户组管理（groupadd/groups/id）"/>
<node TEXT="文件权限rwx（对文件vs对目录）"/>
<node TEXT="chmod数字法+符号法"/>
<node TEXT="chown/chgrp/umask"/>
<node TEXT="特殊权限（SUID/SGID/Sticky）"/>
<node TEXT="sudo与visudo最小权限"/>
<node TEXT="ACL访问控制列表"/>
<node TEXT="dnf包管理（search/info/install/remove）"/>
<node TEXT="EPEL扩展仓库"/>
<node TEXT="rpm/dpkg包查询"/>
<node TEXT="dnf ↔ apt命令对照"/>
</node>
<node TEXT="1.4 服务管理与系统监控（第4周）">
<node TEXT="systemd设计理念（PID=1）"/>
<node TEXT="systemctl（start/stop/status/enable/disable）"/>
<node TEXT="服务状态（active/inactive/failed）"/>
<node TEXT="journalctl日志（-u/-f/-n/-p）"/>
<node TEXT="编写systemd Service文件"/>
<node TEXT="CPU监控（top/htop/uptime）"/>
<node TEXT="内存监控（free -h）"/>
<node TEXT="磁盘监控（df -h/du -sh）"/>
<node TEXT="进程监控（ps aux/pstree）"/>
<node TEXT="端口监控（ss -tunlp）"/>
</node>
</node>
<node TEXT="模块二：Linux网络、协议与远程管理（26课时·第4-7周）" FOLDED="true">
<node TEXT="2.1 网络基础与协议（第4-5周）">
<node TEXT="IP/子网掩码/CIDR/网关/DNS"/>
<node TEXT="网卡命名与ip命令"/>
<node TEXT="nmcli永久配置网络"/>
<node TEXT="hostnamectl主机名"/>
<node TEXT="ping/traceroute/curl/wget"/>
<node TEXT="TCP vs UDP区别"/>
<node TEXT="服务与端口关系"/>
<node TEXT="常见端口（22/80/443/3306/6379）"/>
<node TEXT="ss -tunlp端口监听"/>
<node TEXT="DNS解析流程（hosts→resolv.conf→递归）"/>
<node TEXT="nslookup/dig查询"/>
<node TEXT="HTTP/HTTPS与状态码"/>
<node TEXT="curl -v/-I/-L测试"/>
</node>
<node TEXT="2.2 SSH远程管理（第5-6周）">
<node TEXT="SSH协议原理（加密通信）"/>
<node TEXT="sshd服务与22端口"/>
<node TEXT="密码认证与密钥认证"/>
<node TEXT="ssh-keygen -t ed25519"/>
<node TEXT="ssh-copy-id分发公钥"/>
<node TEXT="私钥权限600"/>
<node TEXT="~/.ssh/config多主机别名"/>
<node TEXT="ssh-agent缓存密码"/>
<node TEXT="文件传输（scp/sftp/rsync）"/>
<node TEXT="tmux终端复用"/>
<node TEXT="SSH隧道（本地/远程/动态转发）"/>
<node TEXT="跳板机ProxyJump"/>
</node>
<node TEXT="2.3 防火墙与安全（第6-7周）">
<node TEXT="firewalld架构（zone+service）"/>
<node TEXT="firewall-cmd（--list-all/--add-port/--reload）"/>
<node TEXT="临时规则vs永久规则（--permanent）"/>
<node TEXT="rich-rule高级规则"/>
<node TEXT="端口转发（forward-port）"/>
<node TEXT="Ubuntu ufw对照"/>
<node TEXT="SELinux（DAC vs MAC）"/>
<node TEXT="Enforcing/Permissive/Disabled"/>
<node TEXT="安全上下文（ls -Z/ps -Z）"/>
<node TEXT="restorecon/chcon修复"/>
<node TEXT="ausearch审计日志"/>
<node TEXT="SELinux布尔值（getsebool/setsebool）"/>
<node TEXT="fail2ban防暴力破解"/>
</node>
<node TEXT="2.4 网络排障流程">
<node TEXT="十步排障链"/>
<node TEXT="VM运行→IP→ping→DNS→服务→端口→本机→防火墙→SELinux→日志"/>
<node TEXT="Connection refused vs timed out"/>
<node TEXT="排障报告模板"/>
</node>
</node>
<node TEXT="模块三：企业常见服务部署与基础排障（28课时·第7-11周）" FOLDED="true">
<node TEXT="3.1 Nginx Web服务（第7-8周）">
<node TEXT="Nginx安装与目录结构"/>
<node TEXT="master进程+worker进程"/>
<node TEXT="默认站点修改"/>
<node TEXT="虚拟主机（server_name+root）"/>
<node TEXT="default_server兜底"/>
<node TEXT="access.log格式解读"/>
<node TEXT="error.log排障（403/404/502）"/>
<node TEXT="tail -f实时跟踪"/>
<node TEXT="awk日志统计（Top IP/状态码/404URL）"/>
<node TEXT="logrotate日志轮转"/>
<node TEXT="HTTPS自签名证书（openssl）"/>
<node TEXT="ssl_certificate配置"/>
<node TEXT="HTTP→HTTPS 301跳转"/>
<node TEXT="Let's Encrypt概念"/>
</node>
<node TEXT="3.2 MySQL/MariaDB（第8-9周）">
<node TEXT="MariaDB与MySQL渊源"/>
<node TEXT="mysql_secure_installation"/>
<node TEXT="bind-address=127.0.0.1"/>
<node TEXT="建库建用户GRANT授权"/>
<node TEXT="utf8mb4 vs utf8"/>
<node TEXT="SHOW PROCESSLIST/STATUS/VARIABLES"/>
<node TEXT="mysqldump备份"/>
<node TEXT="--single-transaction不锁表"/>
<node TEXT="备份脚本+crontab自动化"/>
<node TEXT="3306端口安全风险"/>
</node>
<node TEXT="3.3 Redis缓存（第8-9周）">
<node TEXT="Redis=内存键值存储"/>
<node TEXT="PING/SET/GET/DEL/INCR/EXPIRE"/>
<node TEXT="排行榜ZSET/消息队列LIST"/>
<node TEXT="INFO server/stats/memory"/>
<node TEXT="requirepass密码认证"/>
<node TEXT="bind 127.0.0.1限制监听"/>
<node TEXT="protected-mode保护"/>
<node TEXT="rename-command禁用危险命令"/>
<node TEXT="未授权访问案例"/>
<node TEXT="RDB/AOF持久化概念"/>
</node>
<node TEXT="3.4 Git版本控制（第9-10周）">
<node TEXT="Git在运维部署中的作用"/>
<node TEXT="git clone/pull/log"/>
<node TEXT="git init/add/commit"/>
<node TEXT="git branch/checkout/merge"/>
<node TEXT=".gitignore敏感文件"/>
<node TEXT="git tag标记版本"/>
<node TEXT="分支=环境（main/staging/dev）"/>
</node>
<node TEXT="3.5 Shell运维脚本（第10-11周）">
<node TEXT="Shebang #!/bin/bash"/>
<node TEXT="变量/特殊变量（$1/$?/$#）"/>
<node TEXT="if条件判断（-f/-d/-eq/=）"/>
<node TEXT="for/while循环"/>
<node TEXT="管道|和重定向>/>/>"/>
<node TEXT="crontab定时任务"/>
<node TEXT="系统巡检脚本"/>
<node TEXT="服务检查+自动重启脚本"/>
<node TEXT="日志归档备份脚本"/>
<node TEXT="数据库备份脚本"/>
</node>
<node TEXT="3.6 阶段项目">
<node TEXT="单机Linux Web服务部署与排障"/>
<node TEXT="Nginx虚拟主机+MariaDB+Redis+Git+Shell"/>
<node TEXT="故障模拟与排查"/>
<node TEXT="部署文档+排障报告"/>
</node>
</node>
<node TEXT="模块四：虚拟化技术与多机环境搭建（26课时·第11-14周）" FOLDED="true">
<node TEXT="4.1 虚拟化基础（第11-12周）">
<node TEXT="虚拟化定义与类型（Type1/Type2）"/>
<node TEXT="物理机→虚拟机→云服务器演进"/>
<node TEXT="VMware快照（Copy-on-Write）"/>
<node TEXT="快照≠备份"/>
<node TEXT="完整克隆vs链接克隆"/>
<node TEXT="模板机制作与sysprep"/>
<node TEXT="NAT模式原理"/>
<node TEXT="桥接模式原理"/>
<node TEXT="仅主机模式原理"/>
<node TEXT="三种模式对比实验"/>
<node TEXT="虚拟网络编辑器"/>
</node>
<node TEXT="4.2 KVM虚拟化（第12-13周）">
<node TEXT="KVM架构（kvm.ko+QEMU+libvirt）"/>
<node TEXT="VT-x/AMD-V硬件辅助"/>
<node TEXT="virt-manager图形界面"/>
<node TEXT="virsh核心命令（list/start/shutdown/dominfo）"/>
<node TEXT="存储池管理"/>
<node TEXT="qcow2 vs raw格式"/>
<node TEXT="qemu-img磁盘管理"/>
<node TEXT="快照（snapshot-create/revert）"/>
<node TEXT="virt-clone克隆"/>
<node TEXT="KVM虚拟网络（NAT/桥接/隔离）"/>
<node TEXT="virbr0网桥"/>
<node TEXT="多VM网络拓扑"/>
</node>
<node TEXT="4.3 多机环境搭建（第13-14周）">
<node TEXT="三节点环境（web+db+client）"/>
<node TEXT="主机名/IP/hosts配置"/>
<node TEXT="SSH免密互信"/>
<node TEXT="跨主机服务部署"/>
<node TEXT="拓扑图绘制"/>
<node TEXT="IP地址规划表"/>
</node>
<node TEXT="4.4 云服务概念（第14周）">
<node TEXT="云服务器=虚拟化产品化"/>
<node TEXT="镜像↔ISO"/>
<node TEXT="安全组↔防火墙"/>
<node TEXT="弹性IP↔NAT端口映射"/>
<node TEXT="cloud-init自动化"/>
<node TEXT="virt-builder快速构建"/>
<node TEXT="国内云厂商对照"/>
</node>
</node>
<node TEXT="模块五：Docker容器化部署与综合项目（36课时·第14-18周）" FOLDED="true">
<node TEXT="5.1 容器化认知（第14周）">
<node TEXT="容器vs虚拟机（架构/速度/隔离性）"/>
<node TEXT="容器解决的核心问题"/>
<node TEXT="Docker架构（Client→Daemon→Registry）"/>
<node TEXT="镜像分层结构"/>
<node TEXT="namespace+cgroup+OverlayFS"/>
</node>
<node TEXT="5.2 Docker基础操作（第14-15周）">
<node TEXT="Docker Engine安装"/>
<node TEXT="docker pull/images/search/rmi/tag"/>
<node TEXT="docker run -d/-it/--name/--rm/-p/-v/-e"/>
<node TEXT="docker ps/logs/exec/inspect/stats"/>
<node TEXT="容器生命周期管理"/>
<node TEXT="端口映射-p（宿主机:容器）"/>
<node TEXT="端口冲突排查"/>
<node TEXT="数据卷Volume持久化"/>
<node TEXT="bind mount vs named volume"/>
<node TEXT="volume备份与恢复"/>
<node TEXT="tmpfs临时存储"/>
<node TEXT="自定义bridge网络+DNS"/>
<node TEXT="host/none网络模式"/>
<node TEXT="多网络连接"/>
</node>
<node TEXT="5.3 Docker镜像构建（第16-17周）">
<node TEXT="Dockerfile指令（FROM/COPY/RUN/CMD/WORKDIR）"/>
<node TEXT="docker build构建"/>
<node TEXT="层缓存机制"/>
<node TEXT="CMD vs ENTRYPOINT"/>
<node TEXT=".dockerignore"/>
<node TEXT="多阶段构建"/>
<node TEXT="镜像优化（alpine vs slim vs full）"/>
<node TEXT="USER非root运行"/>
<node TEXT="固定版本号（不用latest）"/>
</node>
<node TEXT="5.4 Docker Compose（第16-17周）">
<node TEXT="YAML语法"/>
<node TEXT="services/ports/volumes/networks"/>
<node TEXT="environment/env_file"/>
<node TEXT="depends_on启动顺序"/>
<node TEXT="docker compose up/down/ps/logs/exec"/>
<node TEXT="多环境管理（override.yml）"/>
<node TEXT=".env文件"/>
<node TEXT="WordPress编排案例"/>
<node TEXT="四层应用编排（Nginx+Flask+MySQL+Redis）"/>
</node>
<node TEXT="5.5 综合项目（第17-18周）">
<node TEXT="TechCorp企业官网+留言板"/>
<node TEXT="12项任务清单"/>
<node TEXT="12项交付物"/>
<node TEXT="Docker Compose一键部署"/>
<node TEXT="故障排查（3-5个）"/>
<node TEXT="项目答辩（方案阐述+实操+故障注入）"/>
<node TEXT="评分标准"/>
</node>
</node>
</node>
</map>