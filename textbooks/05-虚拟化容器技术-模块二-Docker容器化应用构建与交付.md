# 模块二：Docker容器化应用构建与交付

> 适用课程：《虚拟化容器技术》  
> 对应实验：实验6—实验11｜建议学时：40学时  
> 主线环境：`rocky-server`、`ubuntu-client`、Docker Engine、Docker Compose、教师镜像仓库与离线包、教师预建Kubernetes集群

## 模块导读

模块一把完整操作系统封装为虚拟机，模块二进一步把应用及其依赖封装为容器镜像。课程在`rocky-server`（Rocky Linux 9）和`ubuntu-client`（Ubuntu 22.04 Desktop）两个环境中教学：安装阶段明确发行版差异，核心实验使用同一批固定版本镜像和项目文件，使学生能够验证容器交付的一致性与可迁移性。`rocky-web`继续保留Linux课程成果，但默认关机，不要求第三次重复安装Docker。

本模块不依赖Windows Docker Desktop或WSL，不把Docker Hub作为课堂成功的前提。教师通过学校镜像仓库发布课程镜像，同时准备带校验文件的`docker save`离线包；学生既要会在线拉取，也要会用U盘或共享目录导入。

完成本模块后，应能够：

1. 说明镜像、容器、仓库、客户端和守护进程之间的关系。
2. 在`rocky-server`与`ubuntu-client`中安装、启动和验证Docker Engine及Compose插件。
3. 使用固定标签和镜像摘要识别版本，完成在线与离线镜像交付。
4. 管理容器生命周期、端口、环境变量、日志和资源状态。
5. 使用自定义网络、绑定挂载和命名卷部署有状态应用并完成备份恢复。
6. 编写Dockerfile，使用构建上下文、缓存、`.dockerignore`和非root用户改进镜像。
7. 使用Docker Compose描述、启动、更新、排障和迁移多服务应用。
8. 在教师预建Kubernetes集群中操作Namespace、Deployment、Pod和Service。
9. 完成一个容器化综合项目，并通过个人操作或答辩证明真实能力。

## 学习路线与实验成果

| 实验 | 学时 | 本教材对应内容 | 核心成果 |
|---|---:|---|---|
| 实验6 | 4 | 第6章 | `rocky-server`、`ubuntu-client`双环境Docker基线 |
| 实验7 | 6 | 第7章 | 镜像清单、容器运行记录和离线交付包 |
| 实验8 | 8 | 第8章 | 多网络、有状态数据、备份恢复证据 |
| 实验9 | 6 | 第9章 | 可复现、安全且体积受控的应用镜像 |
| 实验10 | 8 | 第10章 | Compose多服务应用、迁移和故障恢复 |
| 实验11 | 8 | 第11章 | Kubernetes编排体验与课程综合项目 |

## 教材深度与课堂使用

本教材不把Docker和Kubernetes写成宽泛的产品介绍。各章按“交付问题—对象与机制—配置和命令入口—数据或网络路径—风险—排障—迁移”组织；实验手册再把这些知识落实为可以独立完成的项目步骤。教材与实验互相引用，但不重复粘贴整套命令。

模块二共40学时，建议课堂时间如下：

| 对应实验 | 教材讲授与任务导入 | 教师关键演示 | 学生独立操作 | 排障、验收与复盘 | 合计 |
|---|---:|---:|---:|---:|---:|
| 实验6 | 30分钟 | 20分钟 | 100分钟 | 30分钟 | 180分钟 |
| 实验7 | 40分钟 | 25分钟 | 155分钟 | 50分钟 | 270分钟 |
| 实验8 | 45分钟 | 30分钟 | 215分钟 | 70分钟 | 360分钟 |
| 实验9 | 40分钟 | 25分钟 | 155分钟 | 50分钟 | 270分钟 |
| 实验10 | 45分钟 | 30分钟 | 215分钟 | 70分钟 | 360分钟 |
| 实验11 | 40分钟 | 20分钟 | 220分钟 | 80分钟 | 360分钟 |
| **合计** | **240分钟** | **150分钟** | **1060分钟** | **350分钟** | **1800分钟** |

教材直接讲授约占13.3%。实验6—10应把更多时间交给学生搭建、验证和恢复；实验11应把最多时间留给综合交付、随机故障与个人答辩。镜像下载和平台等待不属于有效实践时间，必须通过课程Registry、离线包和预建集群消除。

## 学习环境与双发行版分工

| Docker主机 | 系统与主账号 | 主要任务 | 注意事项 |
|---|---|---|---|
| `rocky-server` | Rocky Linux 9；用户`rocky-server`，课堂密码`123456` | Docker环境A、DNF/SELinux差异、镜像构建或源端交付 | 开始前关闭KVM客户机，确认磁盘空间 |
| `ubuntu-client` | Ubuntu 22.04 Desktop；用户`ubuntu-client`，课堂密码`123456` | Docker环境B、APT差异、主要Compose目标或迁移目标 | 从Terminal执行Docker命令，桌面浏览器用于功能验收 |
| `rocky-web` | Linux课程保留的Nginx主机 | 默认不安装Docker | 通常关机；教师安排外部Web验证时再启动 |

两套环境不是把所有实验机械重复两遍。实验6在两台主机分别完成安装与基线；实验7验证离线迁移；实验8—10选择一台作为主要操作主机，关键成果再迁移到另一台验收。这样既体现发行版差异，也把课堂时间留给网络、数据卷、Dockerfile和Compose。

`123456`仍只适用于隔离课堂虚拟机。Registry、数据库、OpenStack和Kubernetes凭据按教师单独发布，不得沿用教学主机密码。

## 贯穿项目：TechCorp应用容器化交付

开发团队提供一个Web入口、Python API、MySQL数据库和Redis缓存组成的应用。学生从单个容器开始，逐步建立网络与数据持久化、构建业务镜像、编写Compose项目，最后把无状态组件放到教师预建Kubernetes集群中体验编排。

```text
用户请求
   ↓
Gateway/Web
   ↓
Python API
  ├── MySQL（持久化业务数据）
  └── Redis（缓存或计数）

交付通道
  ├── 学校课程Registry
  └── U盘/共享目录中的离线tar包 + SHA-256 + 镜像清单
```

---

# 第6章 Docker基础与双发行版部署

## 6.1 容器解决什么问题

应用在开发机正常、换到服务器却失败，常见原因是运行库、配置、文件路径和版本不同。容器镜像把应用及所需用户空间依赖组织成不可变层，并用统一方式启动，使环境更容易复制。

容器的主要优势包括：

- 启动快、资源开销通常小于完整虚拟机；
- 镜像可以版本化和重复分发；
- 应用依赖与宿主机用户空间相对隔离；
- 适合自动化构建、测试和部署；
- 为微服务和容器编排提供标准交付单元。

容器共享宿主机内核，因此不能把它简单理解为“更小的虚拟机”。Linux容器需要Linux内核提供namespace、cgroup、能力控制和文件系统等机制。

## 6.2 Docker架构

```text
docker客户端
      ↓ API
Docker daemon
├── 镜像
├── 容器
├── 网络
├── 卷
└── Registry通信
```

`docker`命令是客户端，Docker daemon负责实际管理对象。客户端报告“无法连接守护进程”时，应先检查服务与权限，而不是重新拉取镜像。

```bash
sudo systemctl status docker
sudo docker info
sudo docker version
```

## 6.3 镜像与容器

镜像是只读模板，容器是镜像的一次运行实例。一个镜像可以创建多个容器；删除容器不会自动删除镜像。容器可写层适合运行时临时变化，不适合保存必须长期保留的业务数据。

```text
镜像只读层
├── 基础系统层
├── 运行库层
└── 应用层
      +
容器可写层
```

## 6.4 Rocky与Ubuntu的共同点和差异

| 项目 | Rocky Linux 9 | Ubuntu 22.04 Desktop |
|---|---|---|
| 软件包体系 | RPM/DNF | DEB/APT |
| Docker服务 | `docker.service` | `docker.service` |
| Compose | Docker Compose插件 | Docker Compose插件 |
| 防火墙常见实现 | firewalld | ufw或其他策略 |
| SELinux | 通常启用 | 通常不以SELinux为默认重点 |
| 核心Docker命令 | 相同 | 相同 |

课程不是重复讲两遍Docker。实验6分别完成安装，之后让相同镜像或Compose项目在两个系统上运行，比较宿主机差异与应用交付一致性。

## 6.5 软件来源与版本固定

课堂安装应由教师提前确定软件仓库、版本和离线包，不让学生临时搜索不明脚本。安装基线至少记录：

```bash
cat /etc/os-release
uname -r
docker version
docker info
docker compose version
```

版本固定不意味着永不更新，而是同一教学批次先使用已验证组合。教师完成兼容性测试后再统一升级。

## 6.6 Docker权限模型

Docker daemon通常拥有很高系统权限。能够访问Docker套接字的用户可创建特权较高的容器，因此加入`docker`组不是普通的低风险授权。本课程默认使用`sudo docker ...`以明确权限边界；若教师选择配置用户组，也必须说明风险并限制账号范围。

## 6.7 第一次运行的验证链

```text
服务已启动
→ 客户端能连接daemon
→ 镜像已存在
→ 容器能创建和运行
→ 端口或输出符合预期
→ 删除测试容器后环境可恢复
```

## 6.8 namespace：容器看到的世界

Linux namespace让一组进程看到独立的系统资源视图。容器不是因为有一个“容器开关”才隔离，而是运行时组合多类namespace、文件系统和权限设置得到隔离环境。

| namespace类型 | 主要隔离对象 | 容器中的表现 |
|---|---|---|
| PID | 进程编号空间 | 容器主进程可看到自己为PID 1 |
| Mount | 挂载点 | 容器拥有独立根文件系统视图 |
| Network | 网卡、地址、路由和端口 | 容器拥有自己的网络栈 |
| UTS | 主机名和域名 | 容器可设置独立hostname |
| IPC | 进程间通信资源 | 消息队列和共享内存相互隔离 |
| User | 用户与UID映射 | 容器内外用户身份可以映射 |
| Cgroup | cgroup视图 | 限制进程看到的控制组层次 |

namespace提供“看见什么”的隔离，不自动限制“能够使用多少”。资源限制主要由cgroup负责。

## 6.9 cgroup：资源统计与控制

cgroup把进程组织成层次结构，对CPU、内存、I/O和进程数量进行统计或限制。若没有限制，一个容器可以与宿主机其他进程竞争大量资源。

常见约束包括：

- CPU配额或权重：控制可用CPU时间和竞争优先级；
- 内存上限：超过限制时可能触发容器内进程被终止；
- PID数量：降低进程风暴影响；
- 块设备I/O：控制磁盘访问能力；
- 统计数据：为`docker stats`和监控提供来源。

容器显示`OOMKilled`时，要同时区分宿主机整体内存不足与容器cgroup内存限制。只看`free -h`可能无法发现容器自身上限。

## 6.10 OCI、containerd与runc

现代容器工具通过标准和分层组件协作：

```text
docker CLI
→ Docker daemon
→ containerd（镜像、容器生命周期管理）
→ OCI运行时runc（创建namespace/cgroup并启动进程）
→ Linux内核
```

OCI制定镜像格式和运行时等开放规范，使镜像能够在不同兼容工具和编排平台之间流转。Docker构建的标准Linux镜像可被Kubernetes所用，并不是Kubernetes必须远程控制Docker daemon。

## 6.11 分层文件系统与容器可写层

镜像由只读层组成，运行容器时在上方增加可写层。读取文件时从上到下查找；修改镜像层中的文件时，存储驱动通常先执行copy-up，再把变化写入容器层。

```text
容器可写层        运行时修改，删除容器后丢失
应用镜像层        应用代码
依赖镜像层        运行库
基础镜像层        基础用户空间
```

频繁修改大量文件或数据库文件放在容器层，会增加copy-on-write开销并难以备份。持久数据使用卷并不只是为了“删除后还在”，也为了让数据生命周期、性能和备份方式独立于镜像层。

## 6.12 PID 1、前台进程与信号

容器生命周期通常与PID 1绑定。主进程退出，容器就停止。应用如果错误地转入后台，启动脚本本身退出后容器也会结束。

停止容器时，Docker先向主进程发送终止信号，等待宽限时间后再强制结束。应用应正确接收信号、停止接收新请求、完成必要刷盘并退出。Shell形式的`CMD`可能引入额外Shell进程，使信号传递与参数处理更复杂；因此服务程序常使用JSON数组形式。

## 6.13 容器隔离的边界

容器共享宿主机内核。以下做法会显著削弱隔离：

- 使用`--privileged`；
- 挂载Docker套接字；
- 挂载宿主机根目录或敏感设备；
- 添加不必要Linux capabilities；
- 以root运行并开放可写宿主目录；
- 使用来源不明或长期不更新的镜像。

课程实验默认不使用`--privileged`。确需演示特殊能力时，必须在可回退隔离环境中说明原因、范围和替代方案。

### 本章小结

Docker由客户端、守护进程、镜像、容器、网络、卷和仓库等对象组成。Rocky与Ubuntu安装方式不同，但核心Docker对象和命令一致。课堂环境必须固定版本、保留离线路径并明确Docker管理权限的风险。

### 思考与练习

1. 为什么Docker客户端存在，不代表Docker服务正常？
2. 容器与虚拟机在内核隔离方面有什么差异？
3. 为什么本课程同时使用Rocky和Ubuntu，却不把所有实验重复两次？

---

# 第7章 镜像、容器、Registry与离线交付

## 7.1 镜像名称、标签与摘要

一个完整镜像引用通常包含：

```text
registry.example.edu/vc/web:2026.09
└────仓库地址────┘ └名称┘ └标签┘
```

标签是可读版本指针，可能被重新指向；摘要根据镜像内容计算，更适合精确确认内容。课程镜像必须使用教师发布的固定标签，镜像清单同时记录摘要、架构、归档文件和SHA-256。

```bash
sudo docker image ls
sudo docker image inspect 镜像引用
sudo docker image inspect 镜像引用 --format '{{json .RepoDigests}}'
```

不要在正式实验中只写`latest`，因为它不能说明实际版本，也会使重现实验变得困难。

## 7.2 拉取与本地镜像层

拉取镜像时，Docker下载本地尚不存在的内容层。多个镜像可以共享相同层，从而节省传输和存储。镜像拉取成功后应检查镜像ID、标签、摘要和架构，而不只看命令退出状态。

## 7.3 容器生命周期

```bash
sudo docker create --name demo 镜像引用
sudo docker start demo
sudo docker stop demo
sudo docker restart demo
sudo docker rm demo
```

`docker run`相当于创建并启动。常见参数：

| 参数 | 作用 |
|---|---|
| `--name` | 设置可读且唯一的容器名 |
| `-d` | 后台运行 |
| `--rm` | 退出后自动删除容器 |
| `-p 主机端口:容器端口` | 发布端口 |
| `-e` | 传递环境变量 |
| `-v`或`--mount` | 挂载目录或卷 |
| `--network` | 连接指定网络 |

## 7.4 状态、日志与容器内检查

```bash
sudo docker ps
sudo docker ps -a
sudo docker inspect 容器名
sudo docker logs --tail 50 容器名
sudo docker exec 容器名 进程或命令
sudo docker stats --no-stream
```

`exec`是在运行中容器里启动新进程，不等于SSH登录。精简镜像可能没有Bash、编辑器或网络工具，应从日志、inspect和专用工具容器等方式观察。

## 7.5 端口发布

容器内部监听端口不会自动向宿主机或外部网络开放。`-p 8081:80`表示把宿主机8081端口映射到容器80端口。验证应包含：

```bash
sudo docker port 容器名
sudo ss -tlnp | grep 8081
curl --fail http://127.0.0.1:8081/
```

远端仍无法访问时继续检查宿主机地址、防火墙、安全策略和访问路径。

## 7.6 在线课程仓库

课程Registry用于解决镜像来源可控与校园网络不稳定问题。基本流程是：教师构建和测试镜像，发布固定标签与清单，学生拉取并核对。需要认证时，应使用教师分配的只读账号，不把密码写入实验报告或Shell历史。

## 7.7 `save/load`与`export/import`

| 操作 | 对象 | 保留镜像层和标签 | 典型用途 |
|---|---|---:|---|
| `docker save` | 一个或多个镜像 | 是 | 镜像离线分发 |
| `docker load` | 镜像归档 | 是 | 导入离线镜像 |
| `docker export` | 容器文件系统 | 否 | 导出扁平文件系统 |
| `docker import` | 文件系统归档 | 否 | 创建新基础镜像 |

课堂离线交付使用`save/load`。示例：

```bash
sudo docker save -o vc-images.tar 镜像引用
sha256sum vc-images.tar > vc-images.tar.sha256
sha256sum -c vc-images.tar.sha256
sudo docker load -i vc-images.tar
```

## 7.8 离线包的四件套

```text
课程离线包
├── images/*.tar             docker save归档
├── SHA256SUMS               文件完整性校验
├── image-manifest.csv       镜像名、标签、摘要、架构、文件名
└── README.md                导入、验证与问题说明
```

U盘只是传输介质，不是版本管理。离线包也必须有版本目录和清单，避免学生导入旧镜像后得到不同结果。

## 7.9 镜像清理原则

清理前先确认容器引用关系：

```bash
sudo docker ps -a --filter ancestor=镜像引用
sudo docker image ls
sudo docker system df
```

不应在课堂中习惯性运行大范围清理命令。只删除实验明确创建、已经确认不再使用的容器和镜像。

## 7.10 镜像层与内容寻址

Docker镜像配置和文件系统层可以根据内容生成不可变标识。若两份镜像引用相同内容层，本地只需保存一份。拉取过程会校验内容摘要，从而发现传输内容与声明不一致。

一个镜像的摘要与压缩归档文件的SHA-256不是同一概念：

| 校验对象 | 示例用途 |
|---|---|
| Registry镜像摘要 | 精确引用仓库中的镜像内容 |
| 镜像ID | 标识本地镜像配置与层 |
| tar文件SHA-256 | 判断U盘或共享目录归档是否完整 |

离线交付清单应同时记录镜像引用和tar校验，不能用其中一个完全代替另一个。

## 7.11 标签策略

推荐为课程镜像建立可解释标签：

```text
registry.example.edu/vc/api:2026-fall-v1
registry.example.edu/vc/api:2026-fall-v2
```

标签应表达教学批次或发布版本。修复镜像时发布新标签，不覆盖已经进入全班环境的旧标签。这样出现差异时可以通过清单判断学生实际使用版本，也能够明确回退。

## 7.12 多架构镜像

同一个镜像名称可能对应一个manifest list，根据客户端架构选择`linux/amd64`或`linux/arm64`等具体镜像。机房以x86_64为主时，离线包仍应在清单标明`linux/amd64`，避免在ARM教师机导出后拿到课堂无法运行的内容。

```bash
sudo docker image inspect 镜像引用 --format '{{.Architecture}}/{{.Os}}'
```

虚拟化模拟可以跨架构运行，但性能和配置复杂度不同，本课程不把跨架构模拟作为必做内容。

## 7.13 Registry中的pull与push边界

拉取需要读取仓库内容，推送会改变共享仓库状态。学生课堂账号原则上只读；需要练习发布时，应为每人或每组划分独立命名空间，避免覆盖教师基线镜像。

一次推送通常包括检查本地层、上传缺失层和提交manifest。出现认证失败时要区分：

- 地址和端口是否正确；
- DNS和TLS证书是否可信；
- 用户是否登录；
- 账号对目标命名空间是否有权限；
- 标签是否符合仓库规则。

不要把关闭TLS校验作为长期解决方案。机房Registry应使用受信任证书，或由教师统一下发课程CA并验证指纹。

## 7.14 容器运行参数是交付的一部分

镜像只描述默认文件和启动配置，端口发布、卷、网络、秘密和资源限制通常在运行时提供。因此“把镜像文件给别人”不等于完成应用交付。

完整单容器交付至少记录：

```text
镜像引用与摘要
+ 运行命令或Compose文件
+ 配置变量说明
+ 端口和访问路径
+ 卷与数据恢复方法
+ 健康验证
+ 日志与故障处理
```

### 本章小结

镜像是可版本化交付物，容器是运行实例。固定标签、摘要、清单和校验值共同保证班级环境一致；课程Registry与`save/load`离线包构成两条互相备份的交付路径。

### 思考与练习

1. 标签与摘要分别解决什么问题？
2. 为什么迁移课程镜像应使用`save/load`而不是`export/import`？
3. 设计一份能够确认“全班使用同一镜像”的最小证据清单。

---

# 第8章 Docker网络、存储与有状态数据

## 8.1 容器网络对象

Docker网络连接容器，并为容器间通信提供隔离与名称解析。查看网络：

```bash
sudo docker network ls
sudo docker network inspect bridge
```

默认`bridge`网络适合基础测试。用户自定义bridge网络通常能为同一网络中的容器提供基于容器名的DNS解析，更适合多容器应用。

## 8.2 自定义网络与分层

```bash
sudo docker network create vc-front-net
sudo docker network create vc-back-net
```

一个网关容器可连接前端和后端网络，数据库只连接后端网络：

```text
客户端
  ↓ 宿主机发布端口
Gateway ── vc-front-net
  │
  └── vc-back-net ── API ── MySQL/Redis
```

“未发布数据库端口”不等于数据库完全安全，但可以减少不必要的宿主机暴露面。容器之间通过网络名和容器名通信，不应依赖会变化的容器IP。

## 8.3 网络排障顺序

```text
容器是否运行
→ 是否连接预期网络
→ 名称能否解析
→ 目标进程是否监听
→ 容器内部端口是否可达
→ 宿主机端口是否正确发布
→ 主机防火墙和远端路径
```

常用命令：

```bash
sudo docker inspect 容器名 --format '{{json .NetworkSettings.Networks}}'
sudo docker network inspect 网络名
sudo docker logs 容器名
sudo docker exec 容器名 命令
```

## 8.4 容器可写层为什么不适合业务数据

容器删除后，可写层随之删除。即使容器仍在，容器可写层也不便于独立备份、迁移和权限管理。业务数据应使用绑定挂载或命名卷。

## 8.5 绑定挂载与命名卷

| 对比项 | 绑定挂载 | 命名卷 |
|---|---|---|
| 存储位置 | 用户指定宿主机路径 | Docker管理 |
| 可见性 | 宿主机直接可见 | 通过Docker对象管理 |
| 适用 | 配置、开发源码、明确目录 | 数据库数据、一般持久化 |
| 可移植性 | 依赖宿主路径 | Compose中更易描述 |
| 权限关注 | UID/GID、SELinux、只读 | 容器用户、备份与卷生命周期 |

推荐使用明确路径和只读标记：

```bash
sudo docker run --mount \
  type=bind,src=/明确路径,dst=/容器路径,readonly \
  镜像引用
```

Rocky启用SELinux时，还需要理解挂载标签。实验中可按手册使用`:Z`，但生产环境应根据是否共享挂载选择合适策略，不能用关闭SELinux代替排障。

## 8.6 命名卷生命周期

```bash
sudo docker volume create vc-db-data
sudo docker volume ls
sudo docker volume inspect vc-db-data
```

删除数据库容器不应删除命名卷；重新创建容器并挂载同一卷后，数据应仍存在。删除卷则可能不可恢复，操作前必须确认备份和引用关系。

## 8.7 数据库初始化与秘密信息

许多数据库镜像只在数据目录为空时执行初始化环境变量或脚本。修改密码变量后直接重启旧容器，不一定会重置已有数据库密码。应区分：

- 初始化参数；
- 运行中数据库账号变更；
- 应用连接配置；
- 数据卷中已存在的数据状态。

密码不应写进公开的Compose文件、截图或提交仓库。课堂可使用`.env`并提供`.env.example`，提交时隐藏真实值。

## 8.8 备份与恢复

有状态服务的备份应根据应用选择：数据库逻辑备份、文件一致性备份或存储快照。直接打包正在写入的数据目录可能不一致。

课堂验证至少完成：

```text
写入可识别测试数据
→ 生成备份并记录校验值
→ 模拟删除或创建空环境
→ 执行恢复
→ 从应用或数据库查询原数据
```

对命名卷进行文件级备份时可使用专用工具容器，但要理解挂载方向与只读设置，避免把空目录覆盖到源数据。

## 8.9 容量与清理

```bash
sudo docker system df
sudo docker volume ls
sudo docker ps -a --size
df -hT
```

Docker占用与宿主机文件系统容量相互影响。镜像层、容器日志、构建缓存和数据卷都可能增长。清理必须精确指定课程对象，不能用“一键清理”掩盖容量管理问题。

## 8.10 容器网络的数据路径

在自定义bridge网络中，一个对外请求通常经过：

```text
远端客户端
→ 宿主机物理/虚拟网卡
→ 宿主机防火墙与端口转发规则
→ Docker bridge
→ veth宿主端
→ veth容器端
→ 容器网络namespace
→ 应用监听端口
```

两个同网络容器通信时不需要经过宿主机发布端口，而是通过容器网络和内部端口直接连接。`ports`解决外部进入，`expose`或应用监听描述容器内部能力，二者不能混为一谈。

## 8.11 veth与bridge

veth是一对虚拟以太网接口，数据从一端进入会从另一端出来。Docker通常把一端放入容器network namespace，另一端连接宿主机bridge：

```text
容器eth0 ←→ veth pair ←→ Docker bridge
```

容器删除后对应veth通常消失。只在宿主机看到bridge存在，不能证明目标容器仍连接；应结合`docker network inspect`和容器内地址判断。

## 8.12 内置DNS和服务名

用户自定义网络中的容器可以通过Docker内置DNS解析同网络容器名或网络别名。名称解析的前提是两个容器至少共享一个网络。服务名能解析但连接失败时，再检查目标程序监听地址、内部端口和认证。

把容器IP写死进配置会使重建失败，因为新容器可能获得不同地址。Compose使用服务名，是把应用配置与实例地址变化分离。

## 8.13 常见网络模式边界

| 模式 | 特征 | 适用范围 |
|---|---|---|
| bridge | 独立容器网络栈，通过bridge通信 | 本课程主要模式 |
| host | 与宿主机共享网络namespace | 性能或特殊网络需求，隔离较弱 |
| none | 仅保留最小网络接口 | 完全不需要联网的任务 |
| container | 与指定容器共享网络namespace | 紧密协作的特殊场景 |

生产编排平台还可能使用overlay或CNI网络。本课程在Kubernetes章节建立概念入口，不在Docker实验中部署跨主机overlay。

## 8.14 Docker与宿主机防火墙

Docker为了实现端口发布会调整宿主机网络规则。不同Docker和发行版版本可能使用iptables兼容层或nftables后端。排障时不要只查看firewalld服务是否运行，还应检查容器端口发布、Docker网络规则以及从远端到宿主机的实际路径。

安全设计原则是：只发布必须被外部访问的入口；数据库和缓存留在后端网络；需要来源限制时在经过验证的规则位置配置。不能因为规则复杂就关闭防火墙。

## 8.15 存储驱动与卷的区别

存储驱动管理镜像层和容器可写层，例如overlay2；卷负责持久业务数据。二者都使用宿主磁盘，但生命周期和管理目的不同。

```bash
sudo docker info --format '{{.Driver}}'
sudo docker system df -v
```

不要直接修改Docker数据根目录中的存储驱动内部文件。需要迁移容器应用时，使用镜像导出、Compose配置和应用级数据备份。

## 8.16 UID、GID与挂载权限

宿主目录的数字UID/GID会被容器进程用于权限判断。容器内用户名与宿主用户名即使文字相同，数字ID也未必相同。排障应比较：

```bash
id
sudo docker exec 容器名 id
ls -ln 宿主路径
sudo docker exec 容器名 ls -ln 容器路径
```

正确修复是选择合适运行用户、目录所有权、组权限或只读模式，而不是`chmod 777`。Rocky还需把Unix权限检查与SELinux标签检查分开。

## 8.17 数据库备份一致性

数据库把数据分散在数据文件、日志、缓存和事务状态中。简单打包正在写入的卷，可能得到各文件时间点不一致的副本。课程优先使用`mysqldump`等逻辑备份形成可检查文本，再通过新环境导入验证。

逻辑备份的优点是可读、跨环境兼容性较好；缺点是大数据量速度慢，且必须处理账号、存储过程和一致性选项。卷级备份适合补充学习，但不能跳过恢复测试。

### 本章小结

Docker网络负责容器连接与服务发现，端口发布负责从宿主机进入容器；绑定挂载和命名卷负责把数据从容器生命周期中分离。真正的数据持久化必须通过删除重建和恢复测试证明。

### 思考与练习

1. 为什么应用应通过容器名而不是容器IP访问数据库？
2. 删除数据库容器后数据仍在，能够证明备份有效吗？为什么？
3. Rocky绑定挂载访问被拒绝时，为什么不应直接关闭SELinux？

---

# 第9章 Dockerfile与应用镜像构建

## 9.1 从手工容器到可复现镜像

进入容器手工安装软件，得到的是难以审计和重现的运行实例。Dockerfile用文本声明构建步骤，可纳入Git、代码评审和自动化流水线。

```dockerfile
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
USER 10001
EXPOSE 8080
CMD ["python", "app.py"]
```

## 9.2 常用指令

| 指令 | 作用 | 注意点 |
|---|---|---|
| `FROM` | 选择基础镜像 | 使用课程固定标签或摘要 |
| `ARG` | 构建时变量 | 不用于保存秘密 |
| `ENV` | 运行环境变量 | 会留在镜像配置中 |
| `WORKDIR` | 设置工作目录 | 比连续`cd`更清晰 |
| `COPY` | 复制构建上下文文件 | 只复制所需内容 |
| `RUN` | 构建时执行命令 | 形成镜像层并利用缓存 |
| `USER` | 设置默认运行用户 | 尽量避免root |
| `EXPOSE` | 声明容器端口 | 不等于宿主机端口发布 |
| `CMD` | 默认命令或参数 | 运行时可覆盖 |
| `ENTRYPOINT` | 固定入口程序 | 与`CMD`组合要明确 |

## 9.3 构建上下文

执行`docker build ... .`时，最后的`.`是构建上下文。Docker只能通过`COPY`访问上下文内文件。上下文过大会拖慢构建，还可能把密钥、虚拟环境或Git历史发送给构建器。

`.dockerignore`示例：

```text
.git
.env
__pycache__/
*.log
venv/
```

## 9.4 缓存与Dockerfile顺序

Docker按指令计算缓存。变化频繁的源码应放在依赖安装之后：先复制依赖清单并安装，再复制应用源码。这样只改源代码时可以复用依赖层。

判断优化效果时应比较两次构建日志和耗时，不能只凭感觉。需要强制验证完整构建时可按实验要求禁用缓存，但日常构建应合理利用缓存。

## 9.5 基础镜像与供应链

基础镜像决定操作系统用户空间、运行库和初始风险。课程通过教师仓库发布经过测试的基础镜像，学生记录：

- 完整镜像引用；
- 标签与摘要；
- 架构；
- 发布时间与课程批次；
- 上游来源和许可证信息；
- 已知限制。

镜像能成功运行不代表没有漏洞。后续企业运维和安全课程还会学习镜像扫描、签名、SBOM和流水线策略。

## 9.6 非root运行与最小化

容器进程默认root并不等于宿主机root，但一旦存在错误配置或内核漏洞，权限过大会增加影响。因此业务镜像应在构建阶段创建普通用户、调整文件所有权并用`USER`运行。

镜像优化原则：

- 选择满足运行需要的可信基础镜像；
- 不安装无关编辑器和调试工具；
- 清理包管理缓存；
- 将编译工具留在构建阶段；
- 用多阶段构建只复制最终产物；
- 通过`.dockerignore`缩小上下文；
- 不把密码、私钥和令牌写进镜像层。

## 9.7 多阶段构建

```dockerfile
FROM build-image AS builder
WORKDIR /src
COPY . .
RUN 构建命令

FROM runtime-image
COPY --from=builder /src/产物 /app/产物
USER 10001
CMD ["/app/产物"]
```

第一阶段包含编译工具，最终阶段只包含运行所需产物，可降低体积和攻击面。

## 9.8 构建、标记和验收

```bash
sudo docker build -t vc/techcorp-api:课程标签 .
sudo docker image inspect vc/techcorp-api:课程标签
sudo docker history vc/techcorp-api:课程标签
sudo docker run --rm -p 8083:8080 vc/techcorp-api:课程标签
curl --fail http://127.0.0.1:8083/health
```

镜像验收不仅看构建成功，还要检查进程用户、健康接口、配置注入、日志输出、镜像大小和跨主机运行结果。

## 9.9 常见失败

| 现象 | 优先检查 |
|---|---|
| `COPY`找不到文件 | 构建上下文、路径、`.dockerignore` |
| 依赖下载失败 | 课程软件源、基础镜像、代理或离线依赖 |
| 容器启动即退出 | `docker logs`、CMD、应用错误 |
| 端口不通 | 应用监听地址、EXPOSE与`-p`区别 |
| 非root无权限 | 文件所有权、目录权限、监听端口 |
| 改代码却使用旧结果 | 缓存命中、标签是否正确、容器是否重建 |

## 9.10 `RUN`、`CMD`与`ENTRYPOINT`

- `RUN`只在构建镜像时执行，并把文件系统变化形成镜像层。
- `CMD`定义容器启动时的默认命令或默认参数，可以被运行命令覆盖。
- `ENTRYPOINT`定义主要入口程序，运行命令通常作为附加参数传入。

```dockerfile
ENTRYPOINT ["python", "app.py"]
CMD ["--port", "8080"]
```

运行时追加`--port 9090`会替换CMD参数，但仍使用Python入口。若同时使用Shell形式，要理解引号、变量展开和信号传递由Shell参与处理。

## 9.11 缓存失效链

某一步输入变化后，该步骤和后续步骤的缓存通常都需要重新计算。因此下面两种顺序差异很大：

```dockerfile
# 容易频繁重装依赖
COPY . .
RUN pip install -r requirements.txt
```

```dockerfile
# 依赖文件不变时可以复用依赖层
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

缓存正确命中是优化，错误地复制旧产物则是构建输入没有描述完整。构建必须把生成结果需要的文件、参数和版本纳入可追溯输入。

## 9.12 多阶段构建的责任分离

构建阶段可以包含编译器、头文件和测试工具；运行阶段只保留产物、运行库、证书和必要用户。除了减小体积，多阶段构建还能减少生产镜像中可被滥用的工具。

从构建阶段复制文件时，应明确路径、所有权和执行权限。若产物动态链接，还要确认运行阶段包含对应运行库，不能只看文件已经复制。

## 9.13 构建参数与秘密

`ARG`适合控制非敏感构建选项，例如基础镜像引用或构建模式。秘密不应通过`ARG`或普通`ENV`写入，因为它们可能出现在镜像历史、缓存或检查结果中。

需要访问私有依赖时，现代构建器提供构建秘密挂载等方式，使凭据只在特定构建步骤临时可见。课程基础实验不要求配置复杂秘密后端，但必须能识别“把Token写进Dockerfile再删除”仍可能把Token留在旧层中的风险。

## 9.14 健康检查与镜像元数据

健康检查应轻量、稳定，并测试应用真正准备好的最低能力。检查间隔过短会增加负载，依赖外部系统过多又会把外部波动误判为容器故障。

镜像可使用label记录课程、源码版本和维护信息。标签不是安全签名，但有助于追溯：

```dockerfile
LABEL org.opencontainers.image.title="TechCorp API"
LABEL org.opencontainers.image.version="课程版本"
LABEL org.opencontainers.image.source="课程仓库路径"
```

最终验收应把镜像label、标签、摘要、应用版本接口和Git提交对应起来。

### 本章小结

Dockerfile把应用镜像构建变成可审查、可重复的工程过程。构建上下文、缓存顺序、基础镜像、非root用户和多阶段构建共同影响速度、体积、安全与可维护性。

### 思考与练习

1. 为什么`EXPOSE 8080`不会自动开放宿主机8080端口？
2. 为什么不能通过删除全部缓存来代替正确安排Dockerfile顺序？
3. 设计一次实验，证明镜像在`rocky-server`构建后可以在`ubuntu-client`运行。

---

# 第10章 Docker Compose多服务编排

## 10.1 为什么需要Compose

多服务应用需要反复管理镜像、网络、端口、环境变量、卷和依赖关系。只保存一长串`docker run`命令难以维护。Compose用YAML描述期望状态，并以项目为边界管理多个服务。

```text
compose.yaml
├── services
│   ├── gateway
│   ├── api
│   ├── mysql
│   └── redis
├── networks
└── volumes
```

## 10.2 Compose核心对象

| 对象 | 含义 |
|---|---|
| service | 一类容器的运行定义 |
| image/build | 使用现成镜像或构建镜像 |
| ports | 宿主机端口发布 |
| environment/env_file | 运行配置注入 |
| networks | 服务连接的网络 |
| volumes | 持久化和文件挂载 |
| depends_on | 服务启动依赖声明 |
| healthcheck | 从应用角度判断健康状态 |

## 10.3 YAML与配置展开

YAML依赖缩进，Tab和空格混用、层级错误或冒号格式问题都会改变结构。修改后先让Compose解析：

```bash
sudo docker compose --env-file .env config
```

该命令可能展开环境变量，输出中可能出现秘密信息，因此展示或提交前应脱敏。配置能解析仍不代表应用可用，还需启动和业务验证。

## 10.4 环境变量与秘密

`.env.example`只放变量名和示例说明，可以提交；`.env`放本地实际值，应限制权限且不提交：

```text
.env.example
.env
compose.yaml
README.md
```

环境变量比把密码写死在镜像里更灵活，但它仍可能通过进程环境或检查接口暴露。生产环境应进一步使用专门的秘密管理能力。

## 10.5 服务依赖与健康检查

容器进程启动不代表服务已经可接受请求。数据库可能还在初始化，API可能因此连接失败。健康检查应测试应用真实能力，例如HTTP健康端点或数据库响应。

`depends_on`可以表达启动顺序或健康条件，但不能代替应用自身的重试、超时和故障恢复设计。分布式环境中依赖随时可能短暂不可用。

## 10.6 常用生命周期命令

```bash
sudo docker compose config
sudo docker compose pull
sudo docker compose up -d
sudo docker compose ps
sudo docker compose logs --tail 100
sudo docker compose restart 服务名
sudo docker compose up -d --force-recreate 服务名
sudo docker compose down
```

`down`默认移除项目容器和网络，不一定删除命名卷；带删除卷的选项会造成数据丢失，必须按实验手册执行并提前备份。

## 10.7 更新与回退

可靠更新流程：

```text
记录当前镜像和健康状态
→ 备份有状态数据
→ 获取或导入新镜像
→ 校验配置
→ 只重建目标服务
→ 检查健康、日志和业务
→ 失败时恢复旧标签与数据
```

不要使用同一个可变标签覆盖新旧版本后期待可靠回退。至少保留明确旧标签和新标签，并记录镜像ID或摘要。

## 10.8 从Rocky迁移到Ubuntu

迁移对象包括：

- Compose文件和`.env.example`；
- 实际环境配置的安全传递；
- 固定版本镜像或离线归档；
- 数据库逻辑备份或经验证的数据卷备份；
- 镜像、配置和备份的校验值；
- 目标端口、防火墙和容量要求；
- 启动、验收与回退步骤。

不能只复制正在使用的数据卷目录。跨宿主机用户ID、存储驱动和安全标签可能不同，优先使用应用级备份恢复。

## 10.9 Compose排障树

```text
项目无法访问
├── 配置：docker compose config
├── 容器：docker compose ps
├── 日志：docker compose logs
├── 健康：healthcheck与应用端点
├── 网络：服务名解析和网络连接
├── 配置：环境变量、秘密、端口
├── 数据：卷、初始化状态、权限
└── 外部：宿主机地址、防火墙、客户端路径
```

故障修复后必须重新走完整业务请求，例如访问网关、调用API、写入与读取数据库，而不是只看容器状态变为`running`。

## 10.10 Compose项目身份与资源命名

Compose以项目名组织容器、网络和卷。项目名可能来自顶层`name`、命令参数、环境变量或目录名。相同Compose文件在不同目录运行时，如果项目名改变，可能创建另一套资源，使学生误以为旧数据丢失。

排障时同时检查：

```bash
sudo docker compose ls
sudo docker compose ps -a
sudo docker volume ls
sudo docker network ls
```

课程使用固定顶层项目名，并在迁移文档中记录，避免源主机和目标主机资源命名不可预测。

## 10.11 变量来源与优先级意识

Compose配置可能同时受到Shell环境、`.env`、`--env-file`、Compose中的`environment`和镜像默认值影响。具体优先级应按当前Compose官方文档核对，但排障原则稳定：先查看最终展开配置和容器实际环境，再判断变量来自哪里。

```bash
sudo docker compose --env-file .env config
sudo docker inspect 容器名 --format '{{json .Config.Env}}'
```

完整输出可能包含密码，课堂展示和提交前必须脱敏。变量“在文件中存在”不等于最终进入容器的值正确。

## 10.12 重启策略与健康状态

重启策略根据容器进程退出状态决定是否重新启动，健康检查则报告运行中应用是否健康。容器进程仍运行但应用返回错误时，重启策略不一定采取动作；健康状态为unhealthy也不必然由单机Docker自动替换容器。

因此Compose运维必须结合：

- 进程状态和退出码；
- 健康检查输出；
- 应用日志；
- 依赖服务状态；
- 用户请求结果。

## 10.13 数据依赖与初始化顺序

`depends_on`能够帮助安排容器启动关系，健康条件可以延迟依赖服务启动，但应用仍应实现连接重试。数据库第一次初始化、从备份恢复和普通重启所需时间不同，固定等待若干秒并不可靠。

有状态服务升级前，要记录镜像版本、数据格式兼容性和回退方式。直接把旧数据卷挂给任意新版本数据库，可能触发不可逆升级。

## 10.14 配置变更与最小重建

Compose声明改变后，`up -d`会判断哪些服务需要创建或重建。为了降低影响，应先执行配置检查，再只处理目标服务，并观察依赖链：

```text
修改前基线
→ 配置展开与差异
→ 数据备份
→ 获取固定新镜像
→ 重建目标服务
→ 健康和业务验证
→ 失败时恢复旧配置与旧标签
```

`restart`只重启现有容器，不一定应用Compose文件中的所有新配置。需要应用镜像、环境或挂载变化时应使用适当的重新创建流程。

## 10.15 日志、轮转与可观测性

Docker默认日志会占用宿主机磁盘。`docker compose logs`适合聚合查看项目输出，但长期环境还需控制日志驱动、单文件大小和保留数量。应用应把运行日志写向标准输出/错误输出，并避免在日志中打印数据库密码和Token。

容器运维的最小观察面包括：

```text
容器状态与重启次数
+ 健康状态
+ CPU和内存
+ 宿主磁盘和卷容量
+ 应用请求与错误日志
+ 数据库连接和业务响应
```

### 本章小结

Compose把多条运行命令转化为声明式项目文件，使多服务应用可复现、可迁移和可维护。配置解析、健康检查、固定镜像、数据备份、最小更新和业务验证共同构成交付闭环。

### 思考与练习

1. `depends_on`为什么不能保证依赖服务永远可用？
2. `docker compose down`前要确认哪些数据对象？
3. 列出将Compose应用从Rocky迁移到Ubuntu时不能遗漏的五类信息。

---

# 第11章 Kubernetes编排体验与综合项目

## 11.1 为什么还需要Kubernetes

Compose适合在单台Docker主机上组织多服务应用。当容器需要跨多台主机运行，还会出现副本调度、故障重建、滚动更新、服务发现和统一声明等问题。Kubernetes以集群为范围管理容器化工作负载。

本课程只使用教师预建集群体验核心对象和操作，不部署Kubernetes集群。集群安装、网络插件、存储、控制平面和OpenStack集成将在后续《云计算应用》课程深入学习。

## 11.2 集群与控制入口

```text
kubectl
   ↓ kubeconfig中的集群、用户和context
Kubernetes API
   ↓
Namespace中的资源
├── Deployment
├── ReplicaSet
├── Pod
└── Service
```

`kubeconfig`可能包含访问凭据，应限制文件权限，不上传公开仓库。`context`决定连接哪个集群、使用哪个身份和默认Namespace；执行删除前必须再次确认。

## 11.3 Namespace

Namespace为同一集群中的资源提供逻辑分组和名称范围。课程为每位学生或每组提供独立Namespace和配额。Namespace不是完整安全边界，权限仍由RBAC、网络策略等机制决定。

```bash
kubectl config current-context
kubectl get namespace
kubectl auth can-i get pods -n 课程命名空间
```

## 11.4 Pod与Deployment

Pod是Kubernetes调度的基本单元，一个Pod包含一个或多个紧密协作的容器。Pod本身可能被替换，名称和IP不应作为长期固定入口。

Deployment声明应用镜像、副本数和Pod模板，并通过ReplicaSet维持期望副本：

```text
Deployment
└── ReplicaSet
    ├── Pod
    ├── Pod
    └── Pod
```

删除某个由Deployment管理的Pod后，控制器会创建新Pod恢复副本数。这体现了声明式管理和控制循环。

## 11.5 Service

Service为一组通过标签选择的Pod提供稳定访问入口。Pod可以变化，只要标签匹配，Service就能把流量转发到新的后端。

```text
客户端
  ↓
Service（稳定名称/地址）
  ↓ selector匹配标签
Pod A   Pod B   Pod C
```

Service没有端点时，优先比较Service selector与Pod labels，而不是反复重建集群。

## 11.6 声明式YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vc-web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vc-web
  template:
    metadata:
      labels:
        app: vc-web
    spec:
      containers:
        - name: web
          image: 教师发布的固定镜像
          ports:
            - containerPort: 8080
```

正式应用前先检查文件和目标Namespace：

```bash
kubectl apply --dry-run=client -f vc-web.yaml
kubectl apply -f vc-web.yaml -n 课程命名空间
kubectl get deployment,pod -n 课程命名空间
```

## 11.7 观察、日志与扩缩容

```bash
kubectl get deployment,pod,service -n 课程命名空间
kubectl describe pod Pod名称 -n 课程命名空间
kubectl logs Pod名称 -n 课程命名空间 --tail=50
kubectl scale deployment vc-web --replicas=3 -n 课程命名空间
kubectl rollout status deployment/vc-web -n 课程命名空间
```

`get`用于概览，`describe`显示事件和详细状态，`logs`显示容器应用输出。镜像拉取失败、探针失败、资源不足和配置错误会呈现不同事件，排障应保留原始信息。

## 11.8 Docker Compose与Kubernetes的联系

| 需求 | Docker Compose | Kubernetes |
|---|---|---|
| 管理范围 | 主要为单主机项目 | 多节点集群 |
| 应用单元 | service/容器 | Deployment/Pod等 |
| 稳定访问 | 项目网络与服务名 | Service |
| 副本维护 | 基础副本能力 | 控制器持续维持期望状态 |
| 更新与恢复 | 由Compose与运维流程管理 | Deployment滚动更新与重建 |
| 学习定位 | 本课程重点 | 本课程体验、后续课程深入 |

Compose文件不能直接等同于Kubernetes清单。迁移时要重新设计健康检查、配置、秘密、存储、服务暴露和资源限制。

## 11.9 综合项目验收

实验11为2—3人小组项目，但成绩不能只由共同报告决定。每位学生必须完成个人操作或答辩。建议成果结构：

```text
综合项目提交包
├── README.md
├── compose.yaml
├── .env.example
├── Dockerfile与应用源码
├── kubernetes/*.yaml
├── image-manifest.csv
├── SHA256SUMS
├── backup/
├── evidence/
└── report.md
```

验收关注：

- 是否能解释架构与对象关系；
- 是否使用课程固定镜像或自主构建的明确版本；
- 是否完成Rocky或Ubuntu上的Compose部署；
- 是否完成数据备份与恢复验证；
- 是否在Kubernetes中完成Deployment、Pod、Service、日志、扩缩容和删除；
- 是否能面对随机故障独立定位；
- 是否清理个人Namespace中的临时资源。

## 11.10 与后续课程衔接

| 后续课程 | 本模块留下的问题 |
|---|---|
| 云计算应用 | 如何部署和管理OpenStack、Kubernetes集群 |
| Python自动化运维 | 如何用API和脚本批量构建、发布、检查资源 |
| 网络安全基础 | 如何扫描镜像、管理秘密、隔离网络、限制权限 |
| 企业级项目运维 | 如何监控、集中日志、CI/CD、灰度发布和回滚 |
| 智能开发实战 | 如何容器化AI服务并使用新型算力和推理平台 |

## 11.11 控制面与工作节点

Kubernetes集群可从职责上分为控制面和工作节点：

| 组件 | 位置 | 主要职责 |
|---|---|---|
| API Server | 控制面 | 统一资源API、认证、授权和请求入口 |
| etcd | 控制面 | 保存集群期望状态和关键数据 |
| Scheduler | 控制面 | 为未调度Pod选择节点 |
| Controller Manager | 控制面 | 运行多类控制循环 |
| kubelet | 每个节点 | 根据Pod声明管理本节点容器 |
| 容器运行时 | 每个节点 | 拉取镜像并运行容器 |
| kube-proxy或替代实现 | 节点网络 | 协助实现Service转发规则 |

学生使用`kubectl`访问API Server，而不是逐台登录节点运行容器。不同集群可能使用不同容器运行时和网络实现，但Kubernetes API对象保持相对统一。

## 11.12 声明式状态与控制循环

用户提交Deployment时描述期望副本、镜像和Pod模板。控制器不断比较期望状态与实际状态，并采取创建、删除或更新动作：

```text
读取期望状态
→ 观察实际状态
→ 计算差异
→ 执行协调动作
→ 再次观察
```

删除一个Pod后出现新Pod，不是原Pod“复活”，而是Deployment经ReplicaSet发现副本不足后创建替代实例。排障时既要看当前Pod，也要看它的Owner References、ReplicaSet和Deployment状态。

## 11.13 Pod生命周期与重启

Pod从Pending进入Running，最终可能Succeeded或Failed。一个Pod内的容器还拥有等待、运行和终止等状态。`CrashLoopBackOff`表示容器反复启动失败并进入退避等待，不是具体根因。

检查顺序：

```bash
kubectl get pod Pod名称 -o wide
kubectl describe pod Pod名称
kubectl logs Pod名称 --previous
kubectl get events --sort-by=.metadata.creationTimestamp
```

`--previous`可查看上一次已退出容器的日志，对反复重启故障很重要。

## 11.14 就绪、存活与启动探针

| 探针 | 回答的问题 | 失败后的典型影响 |
|---|---|---|
| readinessProbe | 当前能否接收流量 | 从Service就绪后端中移除 |
| livenessProbe | 进程是否陷入需要重启的故障 | kubelet重启容器 |
| startupProbe | 慢启动应用是否已经完成启动 | 成功前抑制其他探针 |

探针路径错误会制造故障；存活探针过于激进可能导致应用永远启动不起来。探针必须围绕应用真实行为设计，并设置合理初始延迟、周期、超时与失败阈值。

## 11.15 Deployment更新与回退

修改Deployment的Pod模板，例如镜像标签，会触发新的ReplicaSet并按策略逐步替换Pod。观察命令：

```bash
kubectl rollout status deployment/vc-api
kubectl rollout history deployment/vc-api
kubectl get replicaset
```

回退只能恢复Deployment声明，不能自动回退数据库格式、外部配置和业务数据。发布前仍需固定镜像、备份数据和定义验收指标。

## 11.16 Service、EndpointSlice与选择器

Service通过selector找到带匹配label的Pod，控制器再维护EndpointSlice。访问失败时可沿关系检查：

```text
Service端口与targetPort
→ Service selector
→ Pod labels
→ EndpointSlice地址
→ Pod readiness
→ 容器监听地址和端口
```

Pod存在但未Ready时，通常不会成为可用后端。Service对象存在却没有EndpointSlice地址，多数是标签或就绪状态问题。

## 11.17 ConfigMap与Secret入口

应用配置不应全部写死在镜像。Kubernetes可用ConfigMap保存非敏感配置，用Secret保存需要受控分发的数据，并通过环境变量或文件挂载给Pod。

Secret的名称不代表内容天然加密或绝对安全。权限、etcd保护、日志、备份和应用读取方式都影响安全。课程实验只建立对象与边界认知，不把真实Registry密码或数据库凭据写进提交YAML。

## 11.18 requests、limits与调度

`requests`表示调度时预留和承诺的资源基线，`limits`表示允许使用的上限。CPU超过限制通常受到节流，内存超过限制可能导致容器被终止。

资源值过小会造成应用频繁失败，过大则可能使Pod因节点没有足够可分配资源而Pending。排障应查看Pod事件、节点可分配资源和实际使用，而不是盲目提高所有限制。

## 11.19 Namespace、RBAC与资源范围

Namespace提供名称和管理范围，RBAC决定身份能对哪些资源执行哪些动作。课程账号应只能在分配Namespace中管理常用工作负载和Service，不能删除Node、Namespace或其他学生资源。

每次批量查询或删除前确认context和Namespace：

```bash
kubectl config current-context
kubectl config view --minify --output 'jsonpath={..namespace}'; echo
kubectl auth can-i delete deployments -n 课程命名空间
```

## 11.20 Kubernetes排障总路径

```text
kubectl命令能否连接API
→ context、身份、RBAC和Namespace
→ 工作负载期望副本与滚动状态
→ Pod调度、镜像拉取、容器启动和探针
→ Service selector、EndpointSlice和端口
→ 配置、Secret、卷和应用依赖
→ 日志、事件与用户路径复测
```

本课程不要求学生修复控制面、CNI和集群存储故障，但应能提供足够证据，判断问题属于自己的Namespace还是需要平台管理员处理。

### 本章小结

Kubernetes通过声明式对象和控制循环在集群中管理容器。实验重点是Namespace、Deployment、Pod、Service、日志、扩缩容与清理，让学生建立从单机容器到集群编排的清晰入口，为后续云计算课程留下真实操作基础。

### 模块综合问题

1. 分别用一句话解释镜像、容器、Pod、Deployment和Service。
2. 删除一个Deployment管理的Pod后为什么会出现新Pod？
3. Service存在但没有Endpoints时，应对照哪两类字段？
4. 设计在线Registry不可用时，全班在20分钟内完成镜像导入和版本核对的流程。
5. 说明Compose综合项目迁移到Kubernetes时必须重新考虑的内容。

## 模块命令索引

以下索引用于复习，不替代实验手册中的先后顺序和风险检查：

| 目标 | 常用命令 |
|---|---|
| Docker基线 | `docker version`、`docker info`、`docker compose version` |
| 镜像 | `docker pull`、`image ls`、`image inspect`、`history` |
| 容器 | `docker run`、`ps -a`、`logs`、`inspect`、`exec`、`rm` |
| 离线交付 | `docker save`、`docker load`、`sha256sum` |
| 网络 | `docker network create`、`network ls`、`network inspect` |
| 存储 | `docker volume create`、`volume ls`、`volume inspect` |
| 构建 | `docker build`、`.dockerignore`、`docker history` |
| Compose | `docker compose config/up/ps/logs/down` |
| Kubernetes上下文 | `kubectl config current-context`、`kubectl auth can-i` |
| Kubernetes资源 | `kubectl apply/get/describe/logs/scale/delete` |

## 官方资料方向

课后查阅资料时，优先选择Docker和Kubernetes官方文档，并结合教师发布的课程镜像清单。镜像、安装仓库和集群版本可能更新，课堂环境以本学期经过验证的固定版本为准。
