# Linux与虚拟化容器技术

> **版本提示**：本文件保留旧版知识点层级，暂作为知识库使用；课时、周次和单元编号已由v3.0进度表重排，排课请以《01-unit-index.md》和《04-18周课程进度表.md》为准。

## 模块一：Linux基础运维（知识点资源池）

### 1.1 走进Linux
- Linux是什么：操作系统内核
- Linux发行版家族
  - Debian系（Ubuntu Server 22.04 LTS）
  - RHEL系（Rocky Linux 9·主线）
  - 其他（Arch/SUSE/Alpine）
- 为什么主线用Rocky、对照用Ubuntu
  - RHEL兼容发行版常见于企业服务器环境
  - 部分运维岗位会要求CentOS/RHEL兼容系统经验
  - 学会两种包管理体系应对多数场景
- Linux在运维岗位中的作用
  - 服务器操作系统市场份额90%+
  - 云计算/容器化/大数据底层
  - 初级运维典型工作任务（装系统/巡检/管用户/排故障）
- Rocky Linux 9 最小化安装
  - VMware虚拟机创建
  - 磁盘分区方案（/boot / /home swap）
  - root与普通用户创建
- Ubuntu Server 22.04 对照安装
  - netplan网络配置 vs nmcli
  - apt vs dnf初识
- 命令行终端基本使用
  - 命令格式：命令 [-选项] [参数]
  - 基础命令：pwd/ls/cd/clear/whoami/hostname
  - 帮助命令：man（/搜索,q退出）/--help/history
  - Tab补全/Ctrl+C中断/Ctrl+R搜索历史
  - 命令类型：内置/外部/别名（type/which）

### 1.2 文件、目录与文本编辑
- Linux目录结构FHS
  - /etc配置文件（系统"设置"面板）
  - /var变化数据（日志/缓存/数据库）
  - /home用户家目录 /root超级用户家目录
  - /usr用户软件 /opt第三方软件
  - /tmp临时文件 /boot内核引导
  - /dev设备文件 /proc内核虚拟文件系统 /run运行时数据
- 文件与目录操作
  - touch创建/mkdir -p递归创建
  - cp -r递归/-p保留属性/-a归档
  - mv重命名=移动（本质相同）
  - rm -r/-f高危命令
  - rmdir只能删空目录
  - 通配符：*任意 ?单个 []字符集 {}展开
- 文件查看与查找
  - cat一次输出/less分页浏览/head -n头/tail -f跟踪
  - find -name按名/-type按类型/-size按大小/-mtime按时间/-exec执行
  - which找命令位置/whereis找相关文件/locate基于数据库
- 硬链接与软链接
  - inode=文件元数据（大小/权限/时间/块位置），不含文件名
  - 硬链接ln：同一inode多个名字，不能跨分区和目录
  - 软链接ln -s：指向路径的快捷方式，可跨分区和目录
  - 删除原文件：硬链接仍可用（inode还在），软链接断裂
- vim编辑器
  - 为什么必须学：服务器默认只有vi，visudo/git commit/crontab默认打开
  - 三种模式：Normal浏览命令/Insert编辑/Visual选中
  - 移动：hjkl左下上右/wb词/0$行首尾/ggG文件首尾
  - 编辑：x删字符/dd删行/yy复制/p粘贴/u撤销/Ctrl+r重做
  - 搜索替换：/关键词 n下一匹配 :%s/old/new/g全局
  - 保存退出：:w保存 :q退出 :wq保存退出 :q!强制退出
  - .vimrc配置（set number行号等）
- 压缩与解压
  - tar -czf创建gzip包/-xzf解压/-cjf bzip2
  - zip/unzip兼容Windows
  - gzip/gunzip单文件压缩

### 1.3 用户、用户组与权限
- root用户与普通用户
  - UID：root=0 系统=1-999 普通=1000+
  - 生产环境禁止root直接SSH，用普通用户+sudo
- 用户管理
  - /etc/passwd：用户名:x:UID:GID:描述:家目录:Shell
  - /etc/shadow：用户名:加密密码:修改时间:过期策略
  - /etc/group：组名:x:GID:成员列表
  - useradd -m建家/-s指定shell/-G附加组
  - usermod -aG追加组/-s改shell/-L锁定
  - userdel -r删家目录
  - passwd改密码/chage密码过期策略
- 用户组管理
  - groupadd/groupmod/groupdel
  - groups查看组/id查看UID+GID
  - 主组（/etc/passwd指定）vs附加组
- 文件权限rwx
  - 对文件：r读内容/w写内容/x执行
  - 对目录：r列出文件列表/w创建删除文件/x进入目录
  - 三级权限：所有者user/所属组group/其他人other
  - 符号法rwxrwxr-- 数字法755/644/600
  - chmod符号u+x,g-w/数字755
  - chown改所有者/chgrp改组
  - umask默认权限掩码
- 特殊权限
  - SUID(4)：以文件所有者身份执行
  - SGID(2)：目录下新文件继承目录组
  - Sticky(1)：只有文件所有者能删除（/tmp）
- sudo与最小权限原则
  - sudo=以root身份执行单条命令
  - visudo安全编辑/etc/sudoers（语法检查）
  - 精细化控制：用户/组/命令/免密码
  - wheel组=全部sudo权限
  - sudo日志/var/log/secure
- ACL访问控制列表
  - getfacl查看/setfacl设置
  - 比ugo更精细的权限控制

### 1.4 软件包与基础服务管理
- Rocky软件包管理dnf
  - search搜索/info详情/install安装/remove卸载
  - update升级/check-update检查/list installed已安装
  - repolist仓库列表/provides查找命令来源
  - clean清理缓存/makecache重建
- Ubuntu对照apt
  - update更新索引/upgrade升级/install/remove
  - search搜索/show详情/list --installed
- 软件源与镜像源
  - /etc/yum.repos.d/*.repo（RHEL系）
  - /etc/apt/sources.list（Debian系）
  - EPEL扩展仓库
- RPM包 vs DEB包
  - rpm -qi包信息/-ql文件列表/-qf文件属于哪个包
  - dpkg -s包信息/-L文件列表/-S文件所属
- systemd服务管理
  - systemd是PID=1的初始化系统
  - Unit类型：service服务/timer定时器/socket/mount/target
  - systemctl start/stop/restart/status/enable/disable
  - 服务状态：active运行/inactive未运行/failed失败
  - journalctl -u服务名/-f跟踪/-n行数/--since时间
- 基础服务案例
  - sshd：SSH远程登录，端口22
  - nginx：Web服务，端口80/443
- 系统状态监控
  - CPU：top/htop交互/uptime负载/P排序/M排序
  - 内存：free -h/available真正可用/buff/cache可释放
  - 磁盘：df -h分区使用/du -sh目录占用/df -i inode
  - 进程：ps aux快照/pstree树/pgrep按名查PID
  - 端口：ss -tunlp监听列表/0.0.0.0对外vs 127.0.0.1本地
  - 日志：journalctl -u/-f/-p err/--since

## 模块二：Linux网络、协议与远程管理（知识点资源池）

### 2.1 Linux网络基础
- IP地址与子网掩码
  - 公网IP vs 私网IP（10.x/172.16-31.x/192.168.x）
  - CIDR表示法 /24 = 255.255.255.0
  - 子网掩码决定网络位和主机位
- 网关与DNS
  - 默认网关=不同网段通信的出入口
  - DNS=域名→IP翻译服务
  - 解析顺序：hosts→DNS服务器→递归查询
- 网卡配置
  - 命名规则：ens33/ens160（新）vs eth0（旧）
  - ip addr查看/ip route路由/ip link链路
  - nmcli配置连接（永久）
  - 静态IP vs DHCP
  - hostnamectl set-hostname
- 连通性测试
  - ping -c次数/-i间隔
  - traceroute路径跟踪
  - curl -v详细/-I头部/-o下载
  - wget下载
- TCP/UDP与端口
  - TCP面向连接可靠（三次握手四次挥手）
  - UDP无连接低延迟（DNS/视频/游戏）
  - 端口0-65535，知名0-1023需root
  - 常见端口：SSH=22 HTTP=80 HTTPS=443 MySQL=3306 Redis=6379
  - ss -tunlp查看监听（比netstat更快）
  - "服务启动"≠"端口可访问"（防火墙拦截）
- DNS解析
  - 查询过程：浏览器缓存→hosts→本地DNS→根→递归
  - /etc/hosts本地静态解析（优先级最高）
  - /etc/resolv.conf指定DNS服务器
  - nslookup查询/dig +trace追踪
  - 能访问IP不能访问域名=DNS问题
- HTTP/HTTPS与curl
  - HTTP明文80端口/HTTPS加密443端口/TLS证书
  - curl -v详细/-I头部/-L跟随重定向
  - 状态码：200成功/301永久跳转/403禁止/404不存在/502网关错
  - Nginx作为Web服务初识
  - 浏览器F12 Network标签查看请求

### 2.2 SSH远程管理
- SSH协议原理
  - 加密远程登录，替代telnet明文
  - 两阶段：密钥交换建立加密通道→身份认证
  - 服务端sshd守护进程，客户端ssh命令
  - 默认端口22 /etc/ssh/sshd_config配置
- SSH密码认证
  - ssh user@host -p端口
  - 首次连接指纹确认（known_hosts）
  - ssh -v调试/-vvv最详细
- SSH密钥认证（更安全）
  - 密钥对：私钥自己保管/公钥放服务器
  - ssh-keygen -t ed25519生成
  - ssh-copy-id分发公钥
  - 权限必须600（否则SSH拒绝使用）
  - ssh-agent缓存私钥密码
- SSH客户端进阶
  - ~/.ssh/config别名/HostName/User/Port/IdentityFile
  - ssh -i指定私钥
  - ServerAliveInterval心跳防断线
- 文件传输
  - scp本地↔远程（简单直观）
  - sftp交互式管理（可浏览/删除/重命名）
  - rsync -avzP增量同步（备份首选）
  - FTP了解（不加密/双端口/基本淘汰）
- tmux终端复用
  - session/window/pane三层
  - 防止SSH断线导致任务中断
  - Ctrl+b d分离/Ctrl+b c新窗口

### 2.3 防火墙与安全
- firewalld防火墙
  - zone信任级别：public不信任/drop丢弃/trusted全信/internal内网
  - service预定义端口组合：http=80 https=443 ssh=22
  - firewall-cmd --list-all查看完整规则
  - --add-port开放端口/--add-service开放服务
  - 临时规则（立即生效）vs永久规则（--permanent+--reload）
  - --runtime-to-permanent固化临时规则
  - rich-rule高级规则：限制IP/限制频率/记录日志/端口转发
- SELinux基础
  - DAC自主访问控制vs MAC强制访问控制
  - 三种模式：Enforcing强制/Permissive宽容/Disabled关闭
  - 安全上下文：ls -Z文件/ps -Z进程
  - type类型（_t结尾）最关键
  - 经典故障：改Nginx目录→403→SELinux阻止
  - restorecon修复上下文/ausearch查审计日志
  - setenforce 0调试用（不用作修复方案！）
- fail2ban防暴力破解
  - 扫描日志→匹配规则→临时封禁
  - 配置jail保护sshd

### 2.4 网络排障流程
- 十步排障链
  - ①VM运行？②IP正确？③ping通？④DNS正常？
  - ⑤服务启动？⑥端口监听？⑦本机可访问？
  - ⑧防火墙放行？⑨SELinux阻止？⑩日志报错？
- 常见报错速查
  - Connection refused=端口没人监听
  - Connection timed out=网络不通或防火墙DROP
  - Permission denied=密码/密钥/权限/SELinux
  - Name or service not known=DNS解析失败

## 模块三：企业常见服务部署与基础排障（知识点资源池）

### 3.1 Nginx Web服务
- Nginx安装与目录结构
  - /etc/nginx/nginx.conf主配置
  - /etc/nginx/conf.d/*.conf虚拟主机
  - /usr/share/nginx/html默认根目录
  - /var/log/nginx/日志目录
- systemctl管理：start/stop/restart/reload/enable
- 虚拟主机server块
  - server_name匹配域名
  - root网站根目录
  - listen监听端口
  - default_server兜底
- curl/浏览器测试：curl -I/-v
- 日志分析
  - access.log格式：IP 时间 请求 状态码 大小 UA
  - error.log排障：403权限/404路径/502上游
  - tail -f实时跟踪
  - awk统计Top IP/状态码分布/404 URL
- HTTPS证书
  - 自签名证书：openssl req -x509 -nodes -days 365
  - Nginx SSL配置：listen 443 ssl/ssl_certificate/ssl_certificate_key
  - HTTP→HTTPS自动跳转：return 301

### 3.2 MySQL/MariaDB
- MariaDB=MySQL分支，RHEL系默认
- 安装与安全初始化：mysql_secure_installation
- 3306端口/bind-address=127.0.0.1只监听本地
- 运维SQL（不深入开发）
  - CREATE DATABASE/USER
  - GRANT授权/FLUSH PRIVILEGES刷新
  - SHOW DATABASES/PROCESSLIST/VARIABLES
  - 用户主机限制：localhost vs 192.168.% vs %
- 数据库备份
  - mysqldump逻辑备份（SQL文本）
  - --single-transaction不锁表/--no-data只要结构
  - 恢复：mysql < backup.sql
  - 备份脚本+crontab自动化
- 安全风险：3306不对公网开放

### 3.3 Redis缓存
- Redis=内存键值存储，用作缓存/会话/计数/队列
- 6379端口/redis-cli命令行
- 基础操作：PING/SET/GET/DEL/INCR/EXPIRE/TTL/KEYS/INFO
- 安全配置
  - requirepass设置密码
  - bind 127.0.0.1限制监听
  - protected-mode保护模式
  - 真实案例：公网Redis无密码被入侵挖矿
- Redis与Docker Compose项目关系

### 3.4 Git版本控制
- Git在运维部署中的作用：拉代码+版本控制+回滚
- 基础操作
  - git clone克隆仓库
  - git pull获取更新（=fetch+merge）
  - git log查看历史
  - git checkout切换分支/版本
- 分支管理
  - git branch查看/git checkout -b创建切换
  - git merge合并
  - 部署模式：分支=环境（main生产/dev开发/staging预发布）
- .gitignore忽略密码/日志/临时文件
- 代码平台：GitHub/Gitee/GitLab

### 3.5 Shell运维脚本
- 脚本定位：自动化日常任务，不是应用程序开发
- 基础语法
  - Shebang #!/bin/bash
  - 变量定义引用/$1位置参数/$?退出码
  - if条件判断（数值-eq/字符串=/文件-f）
  - for/while循环
  - 管道|和重定向>/>>
- crontab定时任务
  - 格式：分 时 日 月 周 命令
  - crontab -e编辑/-l查看
- 实战脚本
  - 系统巡检：CPU/内存/磁盘/服务/端口/登录失败
  - 服务检查：检测挂掉自动重启并记录日志
  - 日志归档：压缩+删除N天前的旧日志
  - 数据库备份：mysqldump+压缩+保留策略

### 3.6 阶段项目：单机Linux Web服务部署与排障
- 任务：Nginx→MariaDB→Redis→Git→Shell巡检→故障模拟→文档
- 10项任务分解（单元索引中有完整清单）
- 产出：一台完整Web+DB+Cache服务器+部署文档+排障记录

## 模块四：虚拟化技术与多机环境搭建（知识点资源池）

### 4.1 虚拟化基础认知
- 虚拟化定义：一台物理机抽象为多台逻辑独立VM
- 物理机→虚拟机→容器演进
- 云服务器=云厂商通过虚拟化切分物理机
- Hypervisor类型
  - Type 1裸金属：KVM/VMware ESXi/Hyper-V
  - Type 2宿主型：VMware Workstation/VirtualBox/UTM
- VMware快照
  - 原理：Copy-on-Write写时复制
  - 操作：拍快照（实验前）→搞砸→恢复（回到正常状态）
  - 快照≠备份（基础磁盘坏了快照也废）
- 克隆
  - 完整克隆：独立副本，占空间大
  - 链接克隆：共享父盘，省空间但依赖父盘
- 模板机
  - 最小化+基础工具→以此为模板克隆
  - 清除：SSH host key/机器ID/MAC/日志

### 4.2 虚拟网络
- NAT模式：VM通过宿主机上网，外网不能主动访问VM
- 桥接模式：VM直接接入物理网络，局域网可见
- 仅主机模式：VM只能与宿主机通信，隔离环境
- 虚拟网络编辑器：修改子网IP/关闭DHCP/选择桥接网卡
- 常见问题：IP冲突/网段不一致/无法上网/宿主机不能访问VM

### 4.3 KVM虚拟化（条件/选做资源）
- KVM架构：kvm.ko内核模块+QEMU设备模拟+libvirt管理
- 工具链：virsh命令行/virt-manager图形/virt-install创建
- virsh核心命令
  - list --all列出VM
  - start/shutdown/destroy/reboot
  - dominfo详细信息/domblklist磁盘/domiflist网卡
  - undefine删除定义/edit编辑XML
- 存储管理
  - qcow2格式：稀疏分配/快照/压缩/加密
  - raw格式：裸磁盘/性能最好/不支持快照
  - qemu-img create/convert/info
- KVM虚拟网络
  - NAT网络default：virbr0，VM可出不可入
  - 桥接网络bridge：VM直接桥接物理网卡
  - 隔离网络isolated：只有VM之间通信
  - 多VM网络拓扑：前端双网卡做网关+后端隔离

### 4.4 多机环境搭建
- 三节点实验环境
  - web-server：Nginx Web服务
  - db-server：MySQL+Redis数据缓存
  - client：测试客户端
- 配置步骤
  - 主机名/hosts/静态IP
  - SSH免密互信
  - 跨主机服务连通测试
- 文档产出
  - 拓扑图（draw.io或手绘）
  - IP地址规划表
  - 部署步骤文档

### 4.5 云服务概念
- 云服务器与虚拟化对照
  - 镜像Image↔ISO/模板机
  - 快照Snapshot↔VM快照
  - 安全组Security Group↔防火墙规则
  - 弹性公网IP↔NAT端口映射
  - 云硬盘↔虚拟磁盘
- cloud-init：云实例首次启动自动化
- virt-builder：快速构建预配置Linux镜像

## 模块五：Docker容器化部署与综合项目（知识点资源池）

### 5.1 容器化认知
- 容器=应用+依赖打包，"一次构建到处运行"
- Docker=本课程采用的容器构建与运行平台
- 镜像只读模版→容器运行实例
- 容器vs虚拟机
  - 容器共享内核/进程级隔离/秒级启动/MB级
  - 虚拟机独立内核/硬件级隔离/分钟级启动/GB级
- 容器解决的核心问题：环境一致/快速部署/隔离运行/便于迁移
- Docker架构：Client→Daemon(dockerd)→containerd+runc→Registry

### 5.2 Docker基础操作
- 安装Docker Engine
  - dnf添加Docker官方仓库
  - docker-ce + docker-ce-cli + containerd.io + compose-plugin
  - systemctl启动/用户加入docker组
- 镜像管理
  - docker pull拉取/docker images查看
  - docker search搜索/docker rmi删除/docker tag标签
  - 镜像分层：共享底层节省磁盘
  - docker history查看分层历史
- 容器管理
  - docker run -d后台/-it交互/--name命名/--rm自动删/-p端口/-v卷/-e环境
  - docker ps查看/logs日志/exec进入/inspect详情
  - 生命周期：created→running→paused→stopped→deleted
  - docker stop/start/restart/rm -f

### 5.3 Docker端口、数据卷与网络
- 端口映射-p
  - 宿主机端口:容器端口
  - 端口冲突排查：ss -tlnp
  - -P随机端口/docker port查看映射
- 数据卷Volume
  - 容器删除=数据丢失→Volume持久化
  - bind mount：宿主机目录映射到容器
  - named volume：Docker管理的卷（推荐）
  - docker volume create/ls/inspect/rm/prune
  - MySQL/Redis数据持久化案例
- Docker网络
  - bridge默认：docker0，容器间IP通信
  - 自定义bridge：容器名DNS解析（推荐）
  - host：共享宿主机网络栈
  - none：无网络
  - docker network create/ls/inspect/rm
  - 多容器通过自定义网络互相访问

### 5.4 Dockerfile镜像构建
- Dockerfile=镜像的"安装说明书"
- 核心指令
  - FROM基础镜像（alpine>slim>full）
  - COPY复制文件（推荐）/ADD自动解压
  - RUN构建时执行（&&串联减少层数）
  - WORKDIR工作目录
  - ENV环境变量/ARG构建参数
  - CMD默认命令/ENTRYPOINT固定入口
  - EXPOSE声明端口/USER非root运行
- 构建流程
  - docker build -t 名称:标签 上下文路径
  - 层缓存机制：不变层从缓存读取
  - docker history查看构建历史
  - .dockerignore排除不需要的文件
- 镜像优化
  - 选轻量基础镜像（alpine~5MB vs full~1GB）
  - RUN命令&&串联+清理缓存
  - 多阶段构建：构建阶段→运行阶段只拷产物
  - 非root用户运行（安全）
  - 固定版本号（不用latest）

### 5.5 Docker Compose多服务编排
- Compose解决的问题：一键管理多容器应用
- YAML语法：缩进表示层级/键值对/列表(-)
- 文件结构
  - services：定义容器（image/build/ports/volumes/environment/depends_on/restart/networks）
  - networks：自定义网络
  - volumes：命名数据卷
- 常用命令
  - docker compose up -d启动/--build重建
  - docker compose down停止删除/-v删卷
  - docker compose ps/logs/exec
  - docker compose start/stop/restart单个服务
- 多环境管理
  - docker-compose.override.yml开发覆盖
  - .env文件环境变量
- 实战案例
  - WordPress（Nginx+WordPress+MySQL）
  - 自定义多服务应用（前端Nginx+后端Flask+MySQL+Redis）

### 5.6 综合项目：企业基础运维环境搭建与容器化部署
- 项目阶段（10项核心任务，以学生任务书为准）
  - Linux基础：安装系统/用户权限/软件源
  - 网络远程：IP/SSH/DNS/hosts/防火墙
  - Web服务：Nginx部署+日志
  - 数据服务：MySQL+Redis部署+备份
  - Git：拉取项目代码
  - Shell：巡检/服务检查/备份脚本
  - 虚拟化：三机环境搭建
  - Docker：Docker部署三服务
  - Compose：docker-compose.yml一键编排
  - 排障：3-5个故障模拟排查
  - 文档：拓扑图/IP规划/部署文档/排障记录
- 10项核心交付物（详见Project02学生任务书）
- 答辩评分：环境搭建20%+服务部署20%+容器化25%+排障15%+文档10%+素养10%
