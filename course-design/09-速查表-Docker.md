# Docker 命令速查卡

> 打印给学生 | 双面A4

---

## 镜像管理

| 命令 | 说明 |
|------|------|
| `docker pull 镜像:标签` | 拉取镜像 |
| `docker images` | 查看本地镜像 |
| `docker search 关键词` | 搜索镜像 |
| `docker rmi 镜像` | 删除镜像 |
| `docker tag 源 新名:标签` | 打标签 |
| `docker save 镜像 -o 文件.tar` | 导出镜像 |
| `docker load -i 文件.tar` | 导入镜像 |
| `docker history 镜像` | 查看分层历史 |
| `docker image prune -a` | 清理无用镜像 ⚠️ |

## 容器管理

| 命令 | 说明 |
|------|------|
| `docker run -d --name 名 -p 80:80 镜像` | 后台运行+端口映射 |
| `docker run -it 镜像 sh` | 交互式运行 |
| `docker run --rm 镜像` | 退出自动删除 |
| `docker ps` | 查看运行中容器 |
| `docker ps -a` | 查看所有容器 |
| `docker stop 容器` | 停止 |
| `docker start 容器` | 启动已停止的 |
| `docker restart 容器` | 重启 |
| `docker rm 容器` | 删除已停止容器 |
| `docker rm -f 容器` | 强制删除 |
| `docker logs 容器` | 查看日志 |
| `docker logs -f 容器` | 实时跟踪日志 |
| `docker exec -it 容器 bash` | 进入容器 |
| `docker inspect 容器` | 查看详情JSON |
| `docker cp 宿主机:容器路径` | 文件复制 |
| `docker stats` | 资源使用统计 |
| `docker top 容器` | 容器内进程 |

## docker run 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-d` | 后台运行 | |
| `-it` | 交互模式 | |
| `--name` | 容器名 | `--name my-nginx` |
| `--rm` | 退出自动删 | |
| `-p` | 端口映射 | `-p 8080:80` |
| `-P` | 随机端口映射 | |
| `-v` | 目录/卷挂载 | `-v /data:/data` |
| `-e` | 环境变量 | `-e MYSQL_ROOT_PASSWORD=123` |
| `--restart` | 重启策略 | `--restart=always` |
| `--network` | 指定网络 | `--network my-net` |

## 数据卷

| 命令 | 说明 |
|------|------|
| `docker volume create 卷名` | 创建命名卷 |
| `docker volume ls` | 列出所有卷 |
| `docker volume inspect 卷名` | 查看卷详情 |
| `docker volume rm 卷名` | 删除卷 |
| `docker volume prune` | 清理无用卷 ⚠️ |

## 网络

| 命令 | 说明 |
|------|------|
| `docker network ls` | 列出网络 |
| `docker network create 网络名` | 创建自定义bridge |
| `docker network inspect 网络名` | 查看网络详情 |
| `docker network connect 网络 容器` | 容器加入网络 |
| `docker network disconnect 网络 容器` | 容器离开网络 |
| `docker network rm 网络名` | 删除网络 |

**网络模式**：bridge(默认IP通信) / 自定义bridge(推荐,DNS) / host(共享宿主机) / none(无网络)

## Dockerfile 指令

| 指令 | 说明 |
|------|------|
| `FROM 镜像` | 基础镜像（必须第一条） |
| `WORKDIR 路径` | 工作目录 |
| `COPY 源 目标` | 复制文件（推荐） |
| `ADD 源 目标` | 复制+自动解压tar |
| `RUN 命令` | 构建时执行 |
| `ENV 变量=值` | 环境变量 |
| `EXPOSE 端口` | 声明端口（文档作用） |
| `CMD ["命令","参数"]` | 默认启动命令 |
| `ENTRYPOINT ["命令"]` | 固定入口命令 |
| `USER 用户名` | 运行用户 |

```bash
docker build -t 名:标签 .        # 构建镜像
docker build --no-cache -t 名:标签 .  # 不用缓存
```

## Compose

```bash
docker compose up -d              # 一键启动
docker compose up -d --build      # 重建并启动
docker compose down               # 停止删除容器网络
docker compose down -v            # 同时删除卷 ⚠️
docker compose ps                 # 查看状态
docker compose logs               # 看日志
docker compose logs -f 服务名     # 实时跟踪
docker compose exec 服务 命令     # 在服务中执行
docker compose restart 服务名     # 重启某服务
```

## 排障

```bash
docker ps -a                     # 先看状态
docker logs 容器名               # 再看日志
docker inspect 容器名            # 看配置
docker system df                 # 磁盘占用
docker system prune -a --volumes # 大扫除 ⚠️
```
