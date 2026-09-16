# Linux操作系统与虚拟化容器技术课程资源

> 适用专业：高职计算机应用技术（云计算方向）
>
> 课程顺序：《Linux操作系统》64学时 → 《虚拟化容器技术》64学时
>
> 共同节奏：8周，每周8学时，按`2 + 4 + 2`三次到课
>
> 学时口径：1学时为45分钟
>
> 主线环境：Windows 10/11 + VMware Workstation + `rocky-server` + `rocky-web` + Ubuntu 22.04 Desktop `ubuntu-client`

## 当前课程结构

项目已整理为两门独立、连续开设的64学时课程：

- 《Linux操作系统》：3个模块、20个完整实验；
- 《虚拟化容器技术》：2个模块、11个完整实验；
- 教材用于原理讲授、预习和复习；
- 详细Markdown实验手册用于学生独立操作、验证、排障和提交；
- 离线交互动画用于解释数据流、状态变化和多层对象关系；
- 完整实验可以跨课次，课程进度表负责把实验映射到8周24次到课；
- 常用命令直接纳入教材和实验手册，不再单独维护速查表。

## 《Linux操作系统》

| 模块 | 学时 | 实验 | 核心能力 |
|---|---:|---|---|
| Linux基础运维 | 20 | 实验1—7 | 建立三机环境并在`rocky-server`完成基础运维 |
| 网络、远程管理与基础防护 | 20 | 实验8—13 | 网络、SSH、备份、防护与分层排障 |
| 企业服务部署与综合运维 | 24 | 实验14—20 | `rocky-web`部署Nginx，`rocky-server`部署数据库并完成三机交付 |
| **合计** | **64** | **20个实验** |  |

资料使用顺序：`course-design/04`实验项目索引 → `05`课程进度表 → `textbooks/linux/`学习通分章教材 → `labs/linux/`实验手册 → `textbooks/01—03`整册教材 → `06`知识图谱。

## 《虚拟化容器技术》

| 模块 | 学时 | 实验 | 核心能力 |
|---|---:|---|---|
| 服务器虚拟化与云资源基础 | 24 | 实验1—5 | 嵌套虚拟化、真实KVM、qcow2、虚拟网络与OpenStack云主机体验 |
| Docker容器化应用构建与交付 | 40 | 实验6—11 | Rocky/Ubuntu Docker、离线镜像、网络与卷、Dockerfile、Compose与Kubernetes体验 |
| **合计** | **64** | **11个实验** |  |

资料使用顺序：`course-design/07`实验项目索引 → `08`课程进度表 → `textbooks/virtualization-container/`学习通分章教材 → `labs/virtualization-container/`对应实验 → `09`知识图谱。`textbooks/04—05`保留为整册查阅版，不代替“先学一章、再做一个实验”的课堂顺序。

KVM由学生在`rocky-server`内真实操作。Docker同时安装在`rocky-server`和`ubuntu-client`中，后续通过同一镜像和项目验证跨发行版迁移。OpenStack和Kubernetes使用教师预建平台完成必做基础操作，不在本课程部署集群。

## 镜像与离线教学策略

正式实验不依赖Docker Hub持续可用：

1. 教师在学校课程Registry发布固定标签镜像；
2. 镜像清单记录完整引用、摘要、架构和课程批次；
3. 同时使用`docker save`制作离线归档；
4. U盘或共享目录中配套`SHA256SUMS`、`image-manifest.csv`和导入说明；
5. 学生在Rocky导出、Ubuntu导入并完成真实运行验证。

Windows不要求Docker Desktop或WSL。

## 目录说明

```text
linux_virtualization_container/
├── course-design/
│   ├── 00-课程资料导航.md
│   ├── 01-实验环境准备清单.md
│   ├── 02-考核量规与成果提交规范.md
│   ├── 03-开课前验证与待补充清单.md
│   ├── 04—06  Linux课程索引、进度表和知识图谱
│   ├── 07—09  虚拟化容器课程索引、进度表和知识图谱
│   └── 10      两门课程动画规划与素材选型
├── textbooks/
│   ├── 01—03  Linux三个模块教材
│   ├── linux/ 学习通使用的Linux 32个独立章节
│   ├── 04—05  虚拟化容器两个模块整册教材
│   └── virtualization-container/ 学习通使用的虚拟化容器11个独立章节
├── labs/
│   ├── linux/                       # 正式实验1—20
│   └── virtualization-container/    # 正式实验1—11，实验11为期末大项目
└── animations/                      # 可离线打开的课程交互动画
```

## 教学材料分工

| 材料 | 用途 |
|---|---|
| Textbooks | 概念、原理、关系、风险、排障方法和章末问题 |
| 实验手册 | 情境、目标、准备、任务、详细操作、预期、故障、验收和提交 |
| 课程进度表 | 把完整实验安排到8周24次到课中 |
| XMind | 课程导入、模块复盘和知识关系展示，可直接用XMind打开和编辑 |
| 交互动画 | 解释网络路径、对象关系和状态变化；用于讲授、提问和复盘，不替代实验 |
| 环境与考核文件 | 机房准备、镜像回退、平台验证、成绩与答辩规范 |

## 自动验证

修改教材、实验或进度表后，在项目根目录执行：

```powershell
python tools/validate_course.py
```

这里的“验证”是对课程内容可执行性的验证：检查教材顺序、实验输入输出、先创建后使用、跨代码块变量与工作目录、配置语法、清理与保留关系。它不会创建、启动、重装或修改任何VM，也不会代替机房软件源、OpenStack和Kubernetes平台的开课前抽测。

该命令检查教材章节与练习、实验数量和元数据、64学时进度、Markdown结构、本地链接、XMind、可执行占位符、跨代码块变量生命周期、Compose/Kubernetes关键结构以及旧课程口径。Windows存在WSL、或Linux存在Bash时，还会对全部Bash代码块执行语法检查，并在隔离的临时目录中实际完成文件创建、复制、移动、归档、恢复、PID保护、跨目录SHA256校验和三机SSH审计的成功/失败判定；临时数据在测试结束后自动删除。

也可以单独执行这组不需要root和网络的运行冒烟测试：

```bash
bash tools/smoke-filesystem-workflows.sh
```

真实机房应把`tools/course-preflight.sh`复制到相应虚拟机，并按恢复点执行只读验证，例如：

```bash
bash course-preflight.sh linux-l2
bash course-preflight.sh linux-l4
bash course-preflight.sh vc-v0
bash course-preflight.sh vc-v3
bash course-preflight.sh final
```

脚本只读取对象与服务状态，不创建、覆盖或删除课程成果。`FAIL`必须处理；`WARN`表示非核心工具或平台条件需要人工确认。VMware快照本身仍需在宿主机界面核对。

检查点适用主机如下：`linux-l0`、`linux-l2`和`linux-l4`可在三台VM核验；`linux-l1`、`vc-v0`和`vc-v1`主要在`rocky-server`；`vc-v2`在`rocky-server`与`ubuntu-client`；`vc-v3`在Ubuntu源端；`final`分别在Ubuntu源端和Rocky目标端执行。

在Windows宿主机执行`powershell -ExecutionPolicy Bypass -File .\tools\host-preflight.ps1 -CourseStage Linux`，可只读检查Windows版本、内存、CPU虚拟化状态、VMware程序、VMnet8、NAT和DHCP。提供VMX、ISO及虚拟机根目录参数时，还会按Linux阶段核对最低资源、三机NAT、`Linux-L0`快照、文件存在性和磁盘余量。进入第二门课前改用`-CourseStage Virtualization`，此时`rocky-server`必须达到至少6GB/4 vCPU、启用嵌套虚拟化，三机必须具有`Linux-L4`恢复点。

三台虚拟机启动并获得地址后，可在具有`sshpass`的Linux或WSL中执行只读身份审计。密码只通过当前进程环境传入，不写进脚本；参数格式为`角色,IPv4,规范用户名`：

```bash
read -rsp 'Course SSH password: ' COURSE_SSH_PASSWORD
export COURSE_SSH_PASSWORD
bash tools/ssh-course-audit.sh \
  'ubuntu-client,192.168.88.130,ubuntu-client' \
  'rocky-server,192.168.88.131,rocky-server' \
  'rocky-web,192.168.88.132,rocky-web'
unset COURSE_SSH_PASSWORD
```

脚本会检查实际登录账号、主机名、发行版、内核、全局IPv4、SSH服务和VMware Tools；为识别旧镜像，它会在规范账号失败后尝试`student`，但使用旧账号会计为失败，不能作为课程基线通过。示例IP只是一次DHCP观测值，执行时必须替换为机房实际地址。

## 综合项目说明

虚拟化容器课程的实验10形成四服务Compose前置成果，实验11作为8学时期末综合大项目，完成Kubernetes体验、跨发行版迁移、离线交付、数据恢复、随机故障和个人答辩。
