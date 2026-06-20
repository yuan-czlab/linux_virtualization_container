# Lab50：Docker 安装与镜像管理

> 课时：2 | 类型：个人 | 前置：Lab13

## 一、你会学到什么
- 理解 Docker 架构（Client → Daemon → Registry）
- 能安装 Docker Engine 并配置用户权限
- 能搜索、拉取、查看、删除镜像
- 理解镜像分层结构和标签机制

## 二、Docker 架构速览

```
docker CLI (客户端)
    ↓ REST API
dockerd (守护进程)
    ↓
containerd + runc (容器运行时)
    ↓
Registry (镜像仓库: Docker Hub / Harbor / 阿里云)
```

## 三、实验步骤

### 步骤1：安装 Docker Engine

```bash
# 添加 Docker 官方 yum 仓库
sudo dnf config-manager --add-repo \
  https://download.docker.com/linux/rhel/docker-ce.repo

# 安装 Docker CE + CLI + containerd + Compose 插件
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动并设置开机自启
sudo systemctl enable --now docker
systemctl status docker              # active (running)

# 验证
sudo docker version
sudo docker info | head -20
```

### 步骤2：配置非 root 用户使用 Docker

```bash
# 把 student 加入 docker 组
sudo usermod -aG docker student

# 刷新组权限（不需要重新登录）
newgrp docker

# 验证：不需要 sudo 了
docker ps
# 如果报错 permission denied，退出重新 SSH 登录
```

### 步骤3：拉取镜像

```bash
# 搜索镜像
docker search nginx | head -5
docker search mysql | head -5

# 拉取常用镜像
docker pull nginx:latest             # Nginx 最新版（Debian 基础）
docker pull nginx:1.25-alpine        # Nginx Alpine 版（超轻量，~43MB）
docker pull mysql:8.0                # MySQL 8.0
docker pull redis:7-alpine           # Redis Alpine 版（~32MB）

# 查看本地镜像
docker images
# REPOSITORY   TAG           IMAGE ID       CREATED        SIZE
# nginx        latest        abc123def456   2 days ago     187MB
# nginx        1.25-alpine   ghi789jkl012   2 days ago     43MB
# mysql        8.0           mno345pqr678   3 days ago     576MB
# redis        7-alpine      stu901vwx234   1 week ago     32MB
```

> **验收点**：`docker images` 看到 4 个镜像，注意 Alpine 版本比普通版小很多。

### 步骤4：理解镜像分层

```bash
# 查看镜像的构建历史（每一行是一个层）
docker history nginx:alpine
# IMAGE          CREATED BY                     SIZE
# <missing>      CMD ["nginx" "-g" "daemon...   0B
# <missing>      EXPOSE map[80/tcp:{}]           0B
# <missing>      COPY ...                        2KB
# <missing>      RUN /bin/sh -c ...              5MB
# <missing>      ADD alpine-minirootfs...        38MB   ← 最底层：Alpine 基础

# 分层的好处：
# 1. 不同镜像共享相同的基础层，节省磁盘
# 2. 拉取新版本只需拉取变化的层
# 3. 构建时利用缓存加速
```

### 步骤5：镜像标签管理

```bash
# 给镜像打标签（不是复制，是同一个镜像的多个名字）
docker tag nginx:alpine my-nginx:v1.0
docker images | grep my-nginx
# nginx        alpine        xxx   43MB
# my-nginx     v1.0          xxx   43MB   ← 同一个 IMAGE ID

# 拉取特定版本
docker pull nginx:1.23      # 特定版本
docker pull nginx:mainline   # 主线版本

# 命名规范：
# [registry/][namespace/]repository:tag
# 例：docker.io/library/nginx:latest
#     cr.aliyuncs.com/myteam/myapp:v2.0
```

### 步骤6：删除镜像

```bash
# 删除标签（只删标签，不删镜像数据）
docker rmi my-nginx:v1.0

# 删除镜像（删最后一个标签时才真正删除）
docker rmi nginx:1.25-alpine

# 强制删除（即使有容器在使用）
# docker rmi -f 镜像ID

# 清理无用镜像（没有被任何容器使用的）
docker image prune -a
# 慎用！会删除所有未使用的镜像
```

### 步骤7：镜像导入导出（离线环境用）

```bash
# 导出镜像为 tar 文件
docker save nginx:alpine -o /tmp/nginx-alpine.tar
ls -lh /tmp/nginx-alpine.tar          # 约 43MB

# 删除本地镜像
docker rmi nginx:alpine

# 从 tar 文件导入
docker load -i /tmp/nginx-alpine.tar
docker images | grep nginx            # ✓ 又回来了

# 适用场景：离线/内网环境部署
```

---

## 五、练习题

### 练习1：镜像对比分析（20分）

拉取以下镜像并对比大小，解释为什么差异这么大：

| 镜像 | 大小 | 基础 OS | 适用场景 |
|------|------|---------|---------|
| nginx:latest | | | |
| nginx:alpine | | | |
| python:3.12 | | | |
| python:3.12-slim | | | |
| python:3.12-alpine | | | |

### 练习2：镜像分层实验（20分）

1. 用 `docker history` 对比 nginx:latest 和 nginx:alpine
2. 数一数各有多少层
3. 最底层的 SIZE 差异说明了什么？

### 练习3：镜像标签管理（15分）

1. 给 nginx:alpine 打三个标签：`my-app:v1`、`my-app:latest`、`my-app:stable`
2. 删除 `my-app:v1`，镜像还在吗？
3. 删除所有标签后，镜像还在吗？

### 练习4：离线部署方案（25分）

设计一套离线环境部署 Docker 的方案：
1. 在有网络的机器上需要做什么？
2. 如何传输到离线机器？
3. 离线机器上如何加载？
4. 写出完整的命令流程

### 练习5：Docker 镜像仓库（20分）

1. Docker Hub 是什么？默认 registry 地址是什么？
2. 国内为什么需要镜像加速器？怎么配置？
3. 企业内部一般用什么搭建私有镜像仓库？（Harbor）
4. `docker pull nginx` 完整路径是什么？（包含 registry）

## 七、常见问题

**Q: docker pull 太慢怎么办？**
A: 配置国内镜像加速器。`sudo tee /etc/docker/daemon.json <<< '{"registry-mirrors":["https://mirror.ccs.tencentyun.com"]}'`，然后 `sudo systemctl restart docker`。

**Q: 镜像分层有什么好处？**
A: ①不同镜像共享相同基础层，节省磁盘；②拉取新版本只拉变化的层；③构建时利用缓存。坏处：层太多会影响容器启动时的文件系统组装性能。

**Q: latest 标签有什么问题？**
A: latest 是"最新版本"的别名，但具体是哪个版本取决于镜像维护者。生产环境应使用具体版本号（如 nginx:1.25.3）以保证部署一致性。

## 八、课后思考

1. Docker 镜像的分层思想和 Git 的 commit 历史有什么相似之处？它们都使用了什么核心技术？（提示：内容寻址、写时复制）

2. 如果公司内网不能访问 Docker Hub，你会怎么搭建内部镜像仓库？（提示：Harbor、docker save/load、代理缓存）
