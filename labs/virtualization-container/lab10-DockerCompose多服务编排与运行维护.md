# 实验10：Docker Compose多服务编排与运行维护

> 所属模块：模块二 Docker容器化应用构建与交付
>
> 建议学时：8学时
>
> 实验方式：个人为主，可2人互相验收
>
> 对应学习通章节：[2.5 Docker Compose多服务编排](../../textbooks/virtualization-container/模块二/2.5-Docker-Compose多服务编排.md)
>
> 知识前置：实验8—9中的网络、卷、Dockerfile和应用镜像构建
>
> 状态依赖：实验9保留的`vc-course-api:v2-optimized`或课程等价固定镜像，以及MySQL、Redis和Nginx课程镜像
>
> 建议起点：`VC-V2`并保留实验9成果
>
> 项目成果：Web、API、MySQL、Redis多服务Compose项目、健康检查、配置、日志和故障修复记录

## 一、项目情境

TechCorp的Web网关、Python API、MySQL和Redis已经分别完成镜像准备。手工执行多条`docker run`难以保证网络、卷、环境变量、启动顺序和重建过程一致。你需要使用Compose把四个服务定义为一个可重复部署的项目，只发布Web入口，持久化数据库和缓存数据，并通过健康检查、日志和故障注入完成运行维护。

## 二、实验目标

### 1. 知识目标

1. 说明Compose项目、服务、容器、网络和卷之间的关系。
2. 理解声明式配置和命令式`docker run`的差异。
3. 区分`depends_on`启动顺序和服务真正可用。
4. 说明健康检查、环境变量模板和数据卷在多服务应用中的作用。
5. 区分`docker compose down`与`down -v`的数据影响。

### 2. 能力目标

1. 阅读、校验并运行Compose YAML。
2. 配置前端和后端网络边界。
3. 配置MySQL、Redis持久化和服务健康检查。
4. 使用Compose统一查看状态、日志、配置和资源。
5. 更新、重建和恢复单个服务。
6. 排查镜像、端口、变量、健康检查、网络和卷故障。

### 3. 素质目标

1. 不把真实密码直接写入Compose并提交仓库。
2. 更新前检查配置，清理前判断卷是否仍有数据价值。
3. 从用户入口到后端数据形成完整证据链。

## 三、知识准备

### 1. 项目拓扑

```text
客户端
  │ 8088
  ▼
gateway（front-net）
  │ http://api:8080
  ▼
api（front-net + back-net）
  ├── db:3306（back-net + mysql-data）
  └── cache:6379（back-net + redis-data）
```

只有gateway发布宿主机端口。db和cache不向宿主机发布端口。

### 2. Compose对象映射

| Compose字段 | Docker对象 |
|---|---|
| `services` | 一组容器运行模板 |
| `image`或`build` | 使用或构建镜像 |
| `ports` | 宿主机与容器端口映射 |
| `networks` | 服务加入的网络 |
| `volumes` | 服务挂载与顶层卷定义 |
| `environment` | 注入容器运行环境变量 |
| `healthcheck` | 判断服务是否真正可用 |
| `depends_on` | 声明服务依赖和启动条件 |

## 四、实验环境

- 主要在Ubuntu Docker主机完成，Rocky用于客户端或后续迁移。
- Docker Engine和Compose插件可用。
- 教师课程仓库或离线包包含gateway、API、MySQL、Redis镜像。
- 教师API镜像支持`/health`、`/api/info`和`/api/visits`，能够连接MySQL与Redis。
- 工作目录：`~/vc-course/lab10/techcorp-stack`。
- 端口8088未被其他服务占用。

## 五、项目任务

1. 建立Compose项目目录和变量模板。
2. 编写并校验四服务Compose文件。
3. 启动并检查容器、网络、卷和健康状态。
4. 从客户端验证网关、API、MySQL和Redis数据链。
5. 查看日志并完成单服务更新。
6. 完成至少两类故障定位、修复和复测。
7. 备份数据和项目配置，证明项目可重复启动。

## 六、实验步骤

### 任务一：准备项目目录

#### 步骤1：创建目录

```bash
mkdir -p ~/vc-course/lab10/techcorp-stack/evidence ~/vc-course/lab10/techcorp-stack/backup
```

```bash
cd ~/vc-course/lab10/techcorp-stack
```

```bash
pwd
```

#### 步骤2：确认镜像

```bash
source ~/vc-course/course-env.sh
sudo docker image inspect "$COURSE_REGISTRY/vc/gateway:$COURSE_TAG" "$COURSE_REGISTRY/vc/techcorp-api:$COURSE_TAG" "$COURSE_REGISTRY/vc/mysql:$COURSE_TAG" "$COURSE_REGISTRY/vc/redis:$COURSE_TAG" >/dev/null
```

```bash
sudo docker image ls --digests
```

确认以下课程镜像均存在：

命令会核验`gateway`、`techcorp-api`、`mysql`和`redis`四个本学期固定标签镜像；任意一个缺失都会返回非0。

缺少时从学校仓库拉取或导入实验10离线镜像包。不得临时改为Docker Hub上的浮动镜像。

### 任务二：管理配置变量

#### 步骤3：创建可提交模板

执行`vim ~/vc-course/lab10/techcorp-stack/.env.example`并输入以下模板。把四个镜像中的`课程仓库`和`课程标签`替换为教师发布的实际值：

```dotenv
VC_GATEWAY_IMAGE=课程仓库/vc/gateway:课程标签
VC_API_IMAGE=课程仓库/vc/techcorp-api:课程标签
VC_MYSQL_IMAGE=课程仓库/vc/mysql:课程标签
VC_REDIS_IMAGE=课程仓库/vc/redis:课程标签
VC_BIND_IP=CHANGE_ME
VC_DB_NAME=vcdb
VC_DB_USER=vcuser
VC_DB_PASSWORD=replace_me
VC_DB_ROOT_PASSWORD=replace_me
VC_REDIS_PASSWORD=replace_me
```

复制为本地实验文件并填写教师规定的实验密码：

```bash
cd ~/vc-course/lab10/techcorp-stack
```

```bash
cd ~/vc-course/lab10/techcorp-stack
cp .env.example .env
```

```bash
cd ~/vc-course/lab10/techcorp-stack
chmod 600 .env
```

执行`vim .env`，把`VC_BIND_IP`改为`ubuntu-client`实际地址，并为三个密码项设置仅用于课堂的不同密码；不得保留`CHANGE_ME`或`replace_me`。保存后检查文件权限：

```bash
cd ~/vc-course/lab10/techcorp-stack
ls -l .env .env.example
```

除三个实验密码外，还要确认`VC_BIND_IP`等于当前Ubuntu固定地址；任何`CHANGE_ME`或`replace_me`未处理时都不能启动项目。

创建忽略规则：

执行`vim ~/vc-course/lab10/techcorp-stack/.gitignore`并输入：

```gitignore
.env
backup/*.tar
backup/*.sql
evidence/
```

`.env`只是防止把密码直接写进Compose和误提交的基础方式，不等于生产级Secret管理。

### 任务三：编写Compose文件

#### 步骤4：创建compose.yaml

执行`vim ~/vc-course/lab10/techcorp-stack/compose.yaml`并输入：

```yaml
name: vcstack

services:
  gateway:
    image: ${VC_GATEWAY_IMAGE}
    ports:
      - "${VC_BIND_IP}:8088:80"
    depends_on:
      api:
        condition: service_healthy
    networks:
      - front-net
    restart: unless-stopped

  api:
    image: ${VC_API_IMAGE}
    environment:
      APP_ENV: compose-lab
      DB_HOST: db
      DB_PORT: "3306"
      DB_NAME: ${VC_DB_NAME}
      DB_USER: ${VC_DB_USER}
      DB_PASSWORD: ${VC_DB_PASSWORD}
      REDIS_HOST: cache
      REDIS_PORT: "6379"
      REDIS_PASSWORD: ${VC_REDIS_PASSWORD}
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_healthy
    networks:
      - front-net
      - back-net
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3)"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 10s
    restart: unless-stopped

  db:
    image: ${VC_MYSQL_IMAGE}
    environment:
      MYSQL_ROOT_PASSWORD: ${VC_DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${VC_DB_NAME}
      MYSQL_USER: ${VC_DB_USER}
      MYSQL_PASSWORD: ${VC_DB_PASSWORD}
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - back-net
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h 127.0.0.1 -uroot -p$${MYSQL_ROOT_PASSWORD} --silent"]
      interval: 10s
      timeout: 5s
      retries: 12
      start_period: 30s
    restart: unless-stopped

  cache:
    image: ${VC_REDIS_IMAGE}
    command: ["redis-server", "--appendonly", "yes", "--requirepass", "${VC_REDIS_PASSWORD}"]
    environment:
      VC_REDIS_PASSWORD: ${VC_REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    networks:
      - back-net
    healthcheck:
      test: ["CMD-SHELL", "redis-cli -a \"$${VC_REDIS_PASSWORD}\" ping | grep PONG"]
      interval: 10s
      timeout: 5s
      retries: 10
    restart: unless-stopped

networks:
  front-net:
    driver: bridge
  back-net:
    driver: bridge
    internal: true

volumes:
  mysql-data:
  redis-data:
```

`back-net`设为内部网络，数据库和缓存不需要直接访问外部。是否适合实际API初始化取决于镜像设计，课程镜像已提前验证。

#### 步骤5：检查YAML和变量解析

```bash
cd ~/vc-course/lab10/techcorp-stack
grep -En '=(CHANGE_ME|replace_me)$|课程仓库|课程标签' .env
```

该命令应无输出并返回1；只要显示一行占位内容，就回到`.env`修正。确认无占位符后逐项检查：

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env config --quiet
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env config --services
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env config --images
```

不要把完整`docker compose config`输出提交，因为解析后的环境变量可能包含实验密码。

检查计划创建的镜像而不启动：

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env pull --policy missing
```

在离线环境中，所有镜像应已存在，本命令不应依赖公网。

> **验收点**：Compose配置语法通过，服务恰好为gateway、api、db、cache，镜像全部来自课程清单。

### 任务四：启动和观察项目

#### 步骤6：检查宿主机端口与旧项目

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo ss -lntp | grep ':8088' || true
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env ps -a
```

如果8088被占用，先确认进程或容器来源。不要直接终止未知服务。

#### 步骤7：启动项目

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env up -d
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env ps -a
```

首次启动MySQL可能需要几十秒。重复观察健康状态：

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env ps
```

最终db、cache和api应为healthy，gateway应为running。

#### 步骤8：查看项目资源

```bash
sudo docker container ls --filter label=com.docker.compose.project=vcstack
```

```bash
sudo docker network ls --filter name=vcstack
```

```bash
sudo docker volume ls --filter name=vcstack
```

Compose自动为资源添加项目名前缀和标签。实际名称通常类似`vcstack_front-net`和`vcstack_mysql-data`。

#### 步骤9：验证网络边界

```bash
sudo docker inspect vcstack-gateway-1 \
  --format '{{json .NetworkSettings.Networks}}'
```

```bash
sudo docker inspect vcstack-api-1 \
  --format '{{json .NetworkSettings.Networks}}'
```

```bash
sudo docker inspect vcstack-db-1 \
  --format '{{json .NetworkSettings.Networks}}'
```

```bash
sudo docker inspect vcstack-cache-1 \
  --format '{{json .NetworkSettings.Networks}}'
```

```bash
sudo docker port vcstack-gateway-1
```

```bash
sudo docker port vcstack-db-1
```

容器名称可能因Compose版本略有差异，可以先用`docker compose ps --format json`确认。db不应有宿主机发布端口。

### 任务五：功能与数据验证

#### 步骤10：从宿主机访问

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$UBUNTU_CLIENT_IP:8088/health"
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$UBUNTU_CLIENT_IP:8088/api/info"
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$UBUNTU_CLIENT_IP:8088/api/visits"
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$UBUNTU_CLIENT_IP:8088/api/visits"
```

Compose把8088绑定到Ubuntu指定IPv4地址。Docker发布端口可能绕过UFW规则，因此不能只凭`ufw status`判断暴露边界；本实验依靠隔离VMnet8，生产环境还要配置`DOCKER-USER`链或上游防火墙。

预期：健康接口成功，info能够报告MySQL和Redis连接状态，visits连续调用时计数增加。

#### 步骤11：从另一台主机访问

在Rocky客户端：

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$UBUNTU_CLIENT_IP:8088/health"
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$UBUNTU_CLIENT_IP:8088/api/info"
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$UBUNTU_CLIENT_IP:8088/api/visits"
```

访问失败时先证明Ubuntu本机可用，再检查宿主机网络、端口发布和防火墙。

#### 步骤12：验证MySQL数据

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env exec -T db \
  sh -c 'mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE" -e "SHOW TABLES;"'
```

这条命令在数据库容器内读取已注入的实验变量，宿主机终端不需要再导出密码。具体业务表由课程API镜像初始化。

#### 步骤13：验证Redis

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env exec -T cache \
  sh -c 'redis-cli -a "$VC_REDIS_PASSWORD" PING'
```

预期返回`PONG`。命令可能产生“命令行密码不安全”的提示，生产环境应采用更安全的凭据传递方案。

> **验收点**：客户端只通过8088访问，网关、API、MySQL和Redis形成完整功能证据链。

### 任务六：日志和运行维护

#### 步骤14：查看多服务日志

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env logs --tail 50 gateway api
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env logs --tail 30 db cache
```

持续跟随API日志并从另一终端发送请求：

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env logs -f api
```

按`Ctrl+C`退出日志跟随，不会停止服务。

#### 步骤15：重建单个服务

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env up -d --no-deps --force-recreate api
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env ps api
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$UBUNTU_CLIENT_IP:8088/api/info"
```

确认重建API不会删除MySQL和Redis卷。

#### 步骤16：停止和恢复整个项目

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env stop
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env ps -a
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env start
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env ps
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$UBUNTU_CLIENT_IP:8088/api/visits"
```

### 任务七：故障注入与排查

#### 步骤17：错误镜像标签故障

备份文件：

```bash
cd ~/vc-course/lab10/techcorp-stack
cp compose.yaml backup/compose.yaml.good
```

临时把`VC_GATEWAY_IMAGE`在`.env`中改成不存在的标签，执行：

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env pull gateway
```

记录`manifest unknown`或同类错误。恢复`.env`正确值，再验证：

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env config --images
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env up -d
```

#### 步骤18：数据库密码不一致故障

教师可临时修改API的`DB_PASSWORD`为错误值并重建API：

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env up -d --no-deps --force-recreate api
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env ps api
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env logs --tail 80 api
```

```bash
source ~/vc-course/course-env.sh
curl -i "http://$UBUNTU_CLIENT_IP:8088/api/info"
```

根据API日志和健康状态判断认证失败。恢复正确变量后重建API并复测。

#### 步骤19：端口冲突故障

先停止项目：

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env stop
```

使用明确临时容器占用8088：

```bash
cd ~/vc-course/lab10/techcorp-stack
```

```bash
source ~/vc-course/course-env.sh
sudo docker run -d \
  --name vc-port-blocker \
  -p "$UBUNTU_CLIENT_IP:8088:80" \
  "$COURSE_REGISTRY/vc/web:$COURSE_TAG"
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env start gateway || true
```

```bash
sudo ss -lntp | grep ':8088'
```

```bash
sudo docker container ls --format '{{.Names}} {{.Ports}}'
```

确认冲突后清理明确对象：

```bash
sudo docker stop vc-port-blocker
```

```bash
sudo docker rm vc-port-blocker
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env start
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$UBUNTU_CLIENT_IP:8088/health"
```

### 任务八：备份与可重复交付

#### 步骤20：导出数据库逻辑备份

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env exec -T db \
  sh -c 'mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --databases "$MYSQL_DATABASE"' \
  > backup/vcdb.sql
```

```bash
cd ~/vc-course/lab10/techcorp-stack
test -s backup/vcdb.sql
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sha256sum backup/vcdb.sql > backup/SHA256SUMS
```

#### 步骤21：停止并删除容器但保留卷

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env down
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env ps -a
```

```bash
sudo docker volume ls --filter name=vcstack
```

不得使用`down -v`。重新创建：

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env up -d
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env ps
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$UBUNTU_CLIENT_IP:8088/api/visits"
```

数据和访问计数应按照课程应用设计保持。

#### 步骤22：生成配置与资源清单

```bash
cd ~/vc-course/lab10/techcorp-stack
script -q evidence/lab10-result.txt
```

```bash
cd ~/vc-course/lab10/techcorp-stack
date -Is
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sha256sum compose.yaml .env.example .gitignore
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env config --services
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env config --images
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env ps
```

```bash
sudo docker volume ls --filter name=vcstack
```

```bash
sudo docker network ls --filter name=vcstack
```

```bash
exit
```

## 七、独立实践

教师从以下故障中随机选择两项：

- 镜像标签错误；
- 8088端口被占用；
- API数据库密码错误；
- Redis密码错误；
- API缺少`back-net`；
- 健康检查路径错误；
- MySQL卷挂载名称错误；
- 学生误把`depends_on`理解为应用必然可用。

学生必须提交每项故障的状态、日志、配置、根因、最小修复和客户端复测。

## 八、验收标准

- [ ] Compose文件语法和变量解析通过。
- [ ] 项目恰好包含gateway、api、db、cache四个服务。
- [ ] gateway只连接前端网络，db和cache只连接后端网络，api连接两者。
- [ ] 只有gateway发布宿主机8088。
- [ ] MySQL和Redis使用命名卷。
- [ ] db、cache和api最终健康，gateway正常运行。
- [ ] 本机和另一Linux主机均可通过网关访问。
- [ ] API能够证明MySQL、Redis连接和计数功能。
- [ ] 能用Compose查看状态、日志、镜像、网络和卷。
- [ ] 完成单服务重建并保持数据。
- [ ] 完成至少两类故障排查。
- [ ] `down`后卷仍存在，重新`up`功能恢复。
- [ ] 数据库逻辑备份非空并有SHA256。

## 九、成果提交

```text
lab10-学号-姓名/
├── compose.yaml
├── .env.example
├── .gitignore
├── service-topology.png或.pdf
├── evidence/lab10-result.txt
├── backup/SHA256SUMS
├── fault-01.md
├── fault-02.md
└── deployment-and-restore.md
```

不得提交`.env`、数据库真实备份内容、密码、私钥或Registry Token。

## 十、常见问题

### 1. Compose提示变量未设置

```bash
cd ~/vc-course/lab10/techcorp-stack
ls -la .env .env.example
```

```bash
cd ~/vc-course/lab10/techcorp-stack
grep -E '^[A-Z0-9_]+=' .env | sed 's/=.*/=<hidden>/'
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env config --quiet
```

不要把密码直接写回`compose.yaml`。

### 2. db一直为unhealthy

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env ps db
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env logs --tail 100 db
```

```bash
sudo docker inspect vcstack-db-1 --format '{{json .State.Health}}'
```

检查已有卷、镜像版本、初始化变量和健康检查，不直接删除卷。

### 3. gateway返回502

依次检查API状态、健康、网络和日志：

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env ps api
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env logs --tail 100 gateway api
```

```bash
sudo docker inspect vcstack-api-1 --format '{{json .NetworkSettings.Networks}}'
```

### 4. `down`后发现数据还在

这是命名卷的预期行为。只有明确使用`down -v`或删除卷才会清理数据。本课程综合项目结束前禁止随意删除卷。

### 5. 改了Compose但容器未更新

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env config --quiet
```

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env up -d --force-recreate api
```

先确认改的是当前目录中的文件和当前项目。

## 十一、课后思考与拓展

1. `depends_on: condition: service_healthy`解决了什么问题，仍然不能解决什么？
2. 为什么数据库和Redis不应该发布到宿主机？
3. Compose和Kubernetes都使用声明式配置，但适用范围有什么差异？
4. 如果进入CI/CD，哪些文件应该进入Git，哪些凭据应由平台注入？

## 十二、环境保留或清理

- 保留完整`techcorp-stack`目录、镜像、网络和数据卷。
- 项目保持运行或按教师要求停止，不删除卷：

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env stop
```

- 在Ubuntu的Compose配置、镜像、卷备份和运行证据均验收通过后创建VMware检查点`VC-V3-Compose项目完成`；恢复记录中简称`VC-V3`。
- 实验11将使用同一项目完成Rocky/Ubuntu迁移和综合排障。

