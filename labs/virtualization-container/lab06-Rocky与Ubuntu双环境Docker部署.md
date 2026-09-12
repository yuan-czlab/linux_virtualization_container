# 实验6：Rocky与Ubuntu双环境Docker部署

> 所属模块：模块二 Docker容器化应用构建与交付
>
> 建议学时：4学时
>
> 实验方式：个人
>
> 对应教材：《模块二 Docker容器化应用构建与交付》第6章
>
> 前置实验：实验5
>
> 项目成果：两套可用Docker Engine环境、版本与服务基线、课程验证镜像运行结果

## 一、项目情境

TechCorp同时使用RHEL系服务器和Ubuntu云主机。你需要在Linux课程保留的`rocky-server`与`ubuntu-client`中分别部署Docker Engine，比较DNF与APT安装流程、服务状态、存储驱动、安全机制和网络条件，并用同一个课程验证镜像证明两套环境都能运行容器。`rocky-web`保留但默认关机，不在其上重复安装Docker。

Windows宿主机不具备统一WSL环境，因此Docker Desktop不是本课程必需条件。正式实验全部在Linux虚拟机中完成。

## 二、实验目标

### 1. 知识目标

1. 区分Docker Engine、Docker CLI、containerd、runc、Buildx和Compose插件。
2. 说明Docker守护进程、镜像、容器和Linux内核之间的关系。
3. 比较Rocky与Ubuntu安装和安全环境的主要差异。
4. 理解Docker发布端口可能影响主机防火墙策略。

### 2. 能力目标

1. 对两台主机执行无破坏的安装前检查。
2. 使用教师验证的软件仓库或离线软件包安装Docker Engine。
3. 使用systemd管理并验证Docker。
4. 使用课程仓库或离线包运行同一验证镜像。
5. 形成Rocky/Ubuntu双环境基线。

### 3. 素质目标

1. 不直接执行来源不明的在线安装脚本。
2. 不因方便而忽略Docker组的高权限风险。
3. 不删除现有Podman、containerd或Docker数据，除非确认是课程空环境并得到教师指示。

## 三、知识准备

### 1. Docker运行路径

```text
docker命令
→ Docker API
→ dockerd
→ containerd
→ runc/OCI运行时
→ Linux namespace、cgroup、网络和文件系统
```

容器不是一台小型虚拟机。容器中的进程仍由宿主机Linux内核运行，只是获得了隔离的进程、网络、挂载和资源视图。

### 2. 双环境分工

| 环境 | 本课程用途 | 需要特别关注 |
|---|---|---|
| `rocky-server`（Rocky Linux 9） | Docker环境A、RHEL系服务器实践 | DNF、SELinux、firewalld、Podman冲突检查 |
| `ubuntu-client`（Ubuntu 22.04 Desktop） | Docker环境B、主要Compose目标 | APT、UFW/iptables规则、云环境常见路径 |

### 3. 权限提醒

Docker守护进程通常以root权限运行。能够访问Docker Socket的用户可以挂载宿主机目录、创建高权限容器，因此加入`docker`组并不等于普通低权限授权。本课程默认使用`sudo docker`；教师确认后，才可在两台主机上分别将`rocky-server`或`ubuntu-client`加入Docker组。

## 四、实验环境

- Linux课程保留的`rocky-server`与`ubuntu-client`；主机名和当前用户必须同名。
- 两台主机能够联网访问教师软件仓库，或能够访问`<COURSE_MEDIA>/docker-packages/`。
- 教师发布课程Docker软件版本和包清单。
- 教师提供验证镜像在线地址和离线归档，例如`<COURSE_REGISTRY>/vc/verify:<COURSE_TAG>`。
- KVM客户机与`rocky-web`均已关闭，释放宿主机资源。

## 五、项目任务

1. 检查两台主机现有容器软件和资源。
2. 在`rocky-server`安装Docker Engine与Compose插件。
3. 在`ubuntu-client`安装Docker Engine与Compose插件。
4. 验证服务、版本、存储、cgroup和网络。
5. 在两台主机运行同一课程验证镜像。
6. 保存双环境差异和基线证据。

## 六、实验步骤

### 任务一：安装前检查

#### 步骤1：在`rocky-server`建立基线

```bash
mkdir -p ~/vc-course/evidence ~/vc-course/backup
{
  date -Is
  cat /etc/os-release
  uname -r
  uname -m
  free -h
  df -hT /
  rpm -qa | grep -Ei 'docker|containerd|podman|runc' || true
  systemctl list-unit-files | grep -E 'docker|containerd|podman' || true
  getenforce
  firewall-cmd --state 2>/dev/null || true
} | tee ~/vc-course/evidence/lab06-rocky-before.txt
```

若已经存在Docker，停止并报告教师，不覆盖安装，也不删除`/var/lib/docker`。

#### 步骤2：在`ubuntu-client`建立基线

```bash
mkdir -p ~/vc-course/evidence ~/vc-course/backup
{
  date -Is
  cat /etc/os-release
  uname -r
  uname -m
  free -h
  df -hT /
  dpkg -l | grep -Ei 'docker|containerd|podman|runc' || true
  systemctl list-unit-files | grep -E 'docker|containerd|podman' || true
  sudo ufw status 2>/dev/null || true
} | tee ~/vc-course/evidence/lab06-ubuntu-before.txt
```

两台主机架构应与教师镜像清单一致，通常为`x86_64/amd64`。

### 任务二：在`rocky-server`安装Docker

#### 步骤3：处理冲突包

先查询，不直接删除：

```bash
rpm -q podman podman-docker runc containerd docker docker-client 2>/dev/null || true
```

若教师确认课程基线中的`podman-docker`、独立`runc`或`containerd`会与Docker CE冲突，再按教师清单删除明确包名。不要使用宽泛通配符，也不要删除已有业务容器数据。

#### 步骤4：配置教师验证的软件源

在线路线由教师提供经过验证的仓库文件。官方RHEL系示例流程为：

```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo \
  https://download.docker.com/linux/rhel/docker-ce.repo
sudo dnf makecache
```

机房无法稳定访问外网时，改用教师离线RPM目录：

```bash
ls -lh <COURSE_MEDIA>/docker-packages/rocky9/
sudo dnf install -y <COURSE_MEDIA>/docker-packages/rocky9/*.rpm
```

执行离线命令前必须确认目录只包含教师清单中的同一版本软件包。

#### 步骤5：安装固定课程版本

先查看可用版本：

```bash
dnf list docker-ce --showduplicates | sort -r | sed -n '1,15p'
```

教师发布`<ROCKY_DOCKER_VERSION>`后安装：

```bash
sudo dnf install -y \
  docker-ce-<ROCKY_DOCKER_VERSION> \
  docker-ce-cli-<ROCKY_DOCKER_VERSION> \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

如果使用离线RPM，前一步已经完成安装，不重复执行。

#### 步骤6：启动并验证Rocky Docker

```bash
sudo systemctl enable --now docker
systemctl is-active docker
systemctl is-enabled docker
sudo docker version
sudo docker compose version
sudo docker info
sudo ss -lx | grep docker.sock || true
```

记录Server Version、Storage Driver、Cgroup Driver、Docker Root Dir和Operating System。

> **验收点**：Rocky的Docker为active和enabled，客户端与服务端版本均可查询，Compose插件可用。

### 任务三：在`ubuntu-client`安装Docker

#### 步骤7：检查并处理冲突包

```bash
dpkg --get-selections \
  docker.io docker-compose docker-compose-v2 docker-doc \
  docker-buildx podman-docker containerd runc 2>/dev/null || true
```

只有教师确认是空白课程环境时，才删除明确冲突包。不要清除已有`/var/lib/docker`或`/var/lib/containerd`。

#### 步骤8：配置Docker APT仓库

在线路线：

```bash
sudo apt update
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

创建APT源：

```bash
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
```

若使用离线DEB包：

```bash
ls -lh <COURSE_MEDIA>/docker-packages/ubuntu22.04/
sudo apt install -y <COURSE_MEDIA>/docker-packages/ubuntu22.04/*.deb
```

#### 步骤9：安装固定课程版本

查看版本：

```bash
apt list --all-versions docker-ce 2>/dev/null | sed -n '1,15p'
```

教师发布`<UBUNTU_DOCKER_VERSION>`后执行：

```bash
sudo apt install -y \
  docker-ce=<UBUNTU_DOCKER_VERSION> \
  docker-ce-cli=<UBUNTU_DOCKER_VERSION> \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin
```

离线路线已安装时不重复执行。

#### 步骤10：验证Ubuntu Docker

```bash
sudo systemctl enable --now docker
systemctl is-active docker
systemctl is-enabled docker
sudo docker version
sudo docker compose version
sudo docker info
```

> **验收点**：Ubuntu的Docker与Compose插件可用，并记录与Rocky相同字段。

### 任务四：运行课程验证镜像

#### 步骤11：准备镜像

教师会给出在线和离线路线之一。

在线：

```bash
sudo docker pull <COURSE_REGISTRY>/vc/verify:<COURSE_TAG>
```

离线：

```bash
sha256sum <COURSE_MEDIA>/docker-images/vc-verify-<COURSE_TAG>.tar
sudo docker load -i <COURSE_MEDIA>/docker-images/vc-verify-<COURSE_TAG>.tar
```

校验值必须与教师镜像清单一致。

#### 步骤12：在`rocky-server`运行

```bash
sudo docker image ls --digests
sudo docker run --rm \
  --name vc-verify-rocky \
  <COURSE_REGISTRY>/vc/verify:<COURSE_TAG>
```

预期输出至少包含课程定义的`VC_DOCKER_OK`、容器架构和运行时信息。

#### 步骤13：在`ubuntu-client`运行

在`ubuntu-client`执行同一命令，只修改容器名称：

```bash
sudo docker run --rm \
  --name vc-verify-ubuntu \
  <COURSE_REGISTRY>/vc/verify:<COURSE_TAG>
```

两台主机应运行同一镜像摘要并得到相同应用结果。

### 任务五：比较双环境

#### 步骤14：输出结构化基线

在两台主机分别执行：

```bash
{
  date -Is
  cat /etc/os-release
  sudo docker version
  sudo docker compose version
  sudo docker info
  sudo docker image ls --digests
} > ~/vc-course/evidence/lab06-docker-result.txt
```

将两台文件分别重命名为：

```text
lab06-rocky-docker-result.txt
lab06-ubuntu-docker-result.txt
```

完成比较表：

| 项目 | Rocky | Ubuntu | 是否影响Docker使用方式 |
|---|---|---|---|
| 软件包管理器 |  |  |  |
| Docker服务名称 |  |  |  |
| 存储驱动 |  |  |  |
| Cgroup Driver |  |  |  |
| SELinux |  |  |  |
| 防火墙工具 |  |  |  |
| 验证镜像摘要 |  |  |  |

## 七、独立实践

在不查看前面命令的情况下，分别在`rocky-server`和`ubuntu-client`完成：

1. 确认Docker服务状态；
2. 输出Docker服务端版本；
3. 输出Compose版本；
4. 查找Docker根目录；
5. 运行课程验证镜像并自动删除容器。

## 八、验收标准

- [ ] Rocky和Ubuntu均完成安装前基线记录。
- [ ] 使用教师验证的在线源或离线包，没有执行来源不明的安装脚本。
- [ ] 两台主机Docker服务均为active和enabled。
- [ ] 两台主机Docker客户端、服务端、Buildx和Compose插件可用。
- [ ] 能说明Docker Engine、containerd和runc的基本关系。
- [ ] 同一课程验证镜像在`rocky-server`和`ubuntu-client`运行成功。
- [ ] 两台主机镜像摘要一致。
- [ ] 已完成双环境差异表。
- [ ] 能说明Docker组为什么属于高权限授权。

## 九、成果提交

```text
lab06-学号-姓名/
├── lab06-rocky-before.txt
├── lab06-ubuntu-before.txt
├── lab06-rocky-docker-result.txt
├── lab06-ubuntu-docker-result.txt
├── image-checksum.txt
└── rocky-ubuntu-comparison.md
```

## 十、常见问题

### 1. 软件仓库无法访问

停止反复重试，确认DNS、时间和教师仓库地址；改用教师离线RPM/DEB包。Docker安装包离线不代表Docker业务镜像也已安装，二者需要分别准备。

### 2. Docker服务启动失败

```bash
systemctl status docker --no-pager
sudo journalctl -u docker -n 100 --no-pager
sudo dockerd --validate 2>/dev/null || true
df -hT /
```

优先根据日志判断配置、存储、依赖或权限问题。

### 3. 普通用户提示无法访问docker.sock

默认使用：

```bash
sudo docker info
```

不要直接把Socket权限改成666。教师允许时才能加入docker组，并必须说明其root级风险。

### 4. Rocky出现Podman相关冲突

先使用`rpm -q`确认具体包和数据，再按教师软件清单处理。不能把删除全部容器工具作为通用做法。

### 5. Ubuntu使用UFW但发布端口仍可访问

Docker会创建自己的包过滤规则，发布端口可能绕过预期的UFW规则。记录现象，后续在容器网络与安全章节分析，不通过停止Docker解决。

## 十一、课后思考与拓展

1. 为什么同一个Linux容器镜像能够在Rocky和Ubuntu宿主机上运行？
2. 容器共享宿主机内核，这对跨操作系统能力有什么限制？
3. 为什么课程不把Windows Docker Desktop作为必做环境？

## 十二、环境保留或清理

- 保留Rocky和Ubuntu的Docker Engine、Compose插件和验证镜像。
- 不清理`/var/lib/docker`。
- 分别创建VMware快照`VC-02-Docker双环境完成`。
- 下一实验继续使用两台Docker主机。
