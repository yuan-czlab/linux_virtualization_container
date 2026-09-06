# 实验10：Docker Compose多服务编排与运行维护

> 所属模块：模块二 Docker容器化应用构建与交付
>
> 建议学时：8学时
>
> 实验方式：个人为主，可2人互相验收
>
> 对应教材：《模块二 Docker容器化应用构建与交付》第10章
>
> 前置实验：实验9
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
mkdir -p ~/vc-course/lab10/techcorp-stack/{evidence,backup}
cd ~/vc-course/lab10/techcorp-stack
pwd
```

#### 步骤2：确认镜像

```bash
sudo docker image ls --digests
```

确认以下课程镜像均存在：

```text
<COURSE_REGISTRY>/vc/gateway:<COURSE_TAG>
<COURSE_REGISTRY>/vc/techcorp-api:<COURSE_TAG>
<COURSE_REGISTRY>/vc/mysql:<COURSE_TAG>
<COURSE_REGISTRY>/vc/redis:<COURSE_TAG>
```

缺少时从学校仓库拉取或导入实验10离线镜像包。不得临时改为Docker Hub上的浮动镜像。

### 任务二：管理配置变量

#### 步骤3：创建可提交模板

```bash
cat > .env.example <<'EOF'
VC_GATEWAY_IMAGE=<COURSE_REGISTRY>/vc/gateway:<COURSE_TAG>
VC_API_IMAGE=<COURSE_REGISTRY>/vc/techcorp-api:<COURSE_TAG>
VC_MYSQL_IMAGE=<COURSE_REGISTRY>/vc/mysql:<COURSE_TAG>
VC_REDIS_IMAGE=<COURSE_REGISTRY>/vc/redis:<COURSE_TAG>
VC_DB_NAME=vcdb
VC_DB_USER=vcuser
VC_DB_PASSWORD=replace_me
VC_DB_ROOT_PASSWORD=replace_me
VC_REDIS_PASSWORD=replace_me
EOF
```

复制为本地实验文件并填写教师规定的实验密码：

```bash
cp .env.example .env
chmod 600 .env
vim .env
```

创建忽略规则：

```bash
cat > .gitignore <<'EOF'
.env
backup/*.tar
backup/*.sql
evidence/
EOF
```

`.env`只是防止把密码直接写进Compose和误提交的基础方式，不等于生产级Secret管理。

### 任务三：编写Compose文件

#### 步骤4：创建compose.yaml

```bash
cat > compose.yaml <<'YAML'
name: vcstack

services:
  gateway:
    image: ${VC_GATEWAY_IMAGE}
    ports:
      - "8088:80"
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
YAML
```

`back-net`设为内部网络，数据库和缓存不需要直接访问外部。是否适合实际API初始化取决于镜像设计，课程镜像已提前验证。

#### 步骤5：检查YAML和变量解析

```bash
sudo docker compose --env-file .env config --quiet
sudo docker compose --env-file .env config --services
sudo docker compose --env-file .env config --images
```

不要把完整`docker compose config`输出提交，因为解析后的环境变量可能包含实验密码。

检查计划创建的镜像而不启动：

```bash
sudo docker compose --env-file .env pull --policy missing
```

在离线环境中，所有镜像应已存在，本命令不应依赖公网。

> **验收点**：Compose配置语法通过，服务恰好为gateway、api、db、cache，镜像全部来自课程清单。

### 任务四：启动和观察项目

#### 步骤6：检查宿主机端口与旧项目

```bash
sudo ss -lntp | grep ':8088' || true
sudo docker compose --env-file .env ps -a
```

如果8088被占用，先确认进程或容器来源。不要直接终止未知服务。

#### 步骤7：启动项目

```bash
sudo docker compose --env-file .env up -d
sudo docker compose --env-file .env ps -a
```

首次启动MySQL可能需要几十秒。重复观察健康状态：

```bash
sudo docker compose --env-file .env ps
```

最终db、cache和api应为healthy，gateway应为running。

#### 步骤8：查看项目资源

```bash
sudo docker container ls --filter label=com.docker.compose.project=vcstack
sudo docker network ls --filter name=vcstack
sudo docker volume ls --filter name=vcstack
```

Compose自动为资源添加项目名前缀和标签。实际名称通常类似`vcstack_front-net`和`vcstack_mysql-data`。

#### 步骤9：验证网络边界

```bash
sudo docker inspect vcstack-gateway-1 \
  --format '{{json .NetworkSettings.Networks}}'
sudo docker inspect vcstack-api-1 \
  --format '{{json .NetworkSettings.Networks}}'
sudo docker inspect vcstack-db-1 \
  --format '{{json .NetworkSettings.Networks}}'
sudo docker inspect vcstack-cache-1 \
  --format '{{json .NetworkSettings.Networks}}'
sudo docker port vcstack-gateway-1
sudo docker port vcstack-db-1
```

容器名称可能因Compose版本略有差异，可以先用`docker compose ps --format json`确认。db不应有宿主机发布端口。

### 任务五：功能与数据验证

#### 步骤10：从宿主机访问

```bash
curl --fail http://127.0.0.1:8088/health
curl --fail http://127.0.0.1:8088/api/info
curl --fail http://127.0.0.1:8088/api/visits
curl --fail http://127.0.0.1:8088/api/visits
```

预期：健康接口成功，info能够报告MySQL和Redis连接状态，visits连续调用时计数增加。

#### 步骤11：从另一台主机访问

在Rocky客户端：

```bash
curl --fail http://<UBUNTU_IP>:8088/health
curl --fail http://<UBUNTU_IP>:8088/api/info
curl --fail http://<UBUNTU_IP>:8088/api/visits
```

访问失败时先证明Ubuntu本机可用，再检查宿主机网络、端口发布和防火墙。

#### 步骤12：验证MySQL数据

```bash
set -a
. ./.env
set +a
sudo docker compose --env-file .env exec -T db \
  mysql -u"$VC_DB_USER" -p"$VC_DB_PASSWORD" "$VC_DB_NAME" \
  -e 'SHOW TABLES;'
unset VC_DB_PASSWORD VC_DB_ROOT_PASSWORD VC_REDIS_PASSWORD
```

只在当前终端临时读取实验变量，执行后清除敏感变量。具体业务表由教师API镜像初始化。

#### 步骤13：验证Redis

```bash
VC_REDIS_PASSWORD_VALUE=$(awk -F= '$1=="VC_REDIS_PASSWORD" {print substr($0,index($0,"=")+1)}' .env)
sudo docker compose --env-file .env exec -T cache \
  redis-cli -a "$VC_REDIS_PASSWORD_VALUE" PING
unset VC_REDIS_PASSWORD_VALUE
```

预期返回`PONG`。命令可能产生“命令行密码不安全”的提示，生产环境应采用更安全的凭据传递方案。

> **验收点**：客户端只通过8088访问，网关、API、MySQL和Redis形成完整功能证据链。

### 任务六：日志和运行维护

#### 步骤14：查看多服务日志

```bash
sudo docker compose --env-file .env logs --tail 50 gateway api
sudo docker compose --env-file .env logs --tail 30 db cache
```

持续跟随API日志并从另一终端发送请求：

```bash
sudo docker compose --env-file .env logs -f api
```

按`Ctrl+C`退出日志跟随，不会停止服务。

#### 步骤15：重建单个服务

```bash
sudo docker compose --env-file .env up -d --no-deps --force-recreate api
sudo docker compose --env-file .env ps api
curl --fail http://127.0.0.1:8088/api/info
```

确认重建API不会删除MySQL和Redis卷。

#### 步骤16：停止和恢复整个项目

```bash
sudo docker compose --env-file .env stop
sudo docker compose --env-file .env ps -a
sudo docker compose --env-file .env start
sudo docker compose --env-file .env ps
curl --fail http://127.0.0.1:8088/api/visits
```

### 任务七：故障注入与排查

#### 步骤17：错误镜像标签故障

备份文件：

```bash
cp compose.yaml backup/compose.yaml.good
```

临时把`VC_GATEWAY_IMAGE`在`.env`中改成不存在的标签，执行：

```bash
sudo docker compose --env-file .env pull gateway
```

记录`manifest unknown`或同类错误。恢复`.env`正确值，再验证：

```bash
sudo docker compose --env-file .env config --images
sudo docker compose --env-file .env up -d
```

#### 步骤18：数据库密码不一致故障

教师可临时修改API的`DB_PASSWORD`为错误值并重建API：

```bash
sudo docker compose --env-file .env up -d --no-deps --force-recreate api
sudo docker compose --env-file .env ps api
sudo docker compose --env-file .env logs --tail 80 api
curl -i http://127.0.0.1:8088/api/info
```

根据API日志和健康状态判断认证失败。恢复正确变量后重建API并复测。

#### 步骤19：端口冲突故障

先停止项目：

```bash
sudo docker compose --env-file .env stop
```

使用明确临时容器占用8088：

```bash
sudo docker run -d \
  --name vc-port-blocker \
  -p 8088:80 \
  <COURSE_REGISTRY>/vc/web:<COURSE_TAG>
sudo docker compose --env-file .env start gateway || true
sudo ss -lntp | grep ':8088'
sudo docker container ls --format '{{.Names}} {{.Ports}}'
```

确认冲突后清理明确对象：

```bash
sudo docker stop vc-port-blocker
sudo docker rm vc-port-blocker
sudo docker compose --env-file .env start
curl --fail http://127.0.0.1:8088/health
```

### 任务八：备份与可重复交付

#### 步骤20：导出数据库逻辑备份

```bash
VC_DB_ROOT_PASSWORD_VALUE=$(awk -F= '$1=="VC_DB_ROOT_PASSWORD" {print substr($0,index($0,"=")+1)}' .env)
sudo docker compose --env-file .env exec -T db \
  mysqldump -uroot -p"$VC_DB_ROOT_PASSWORD_VALUE" --databases vcdb \
  > backup/vcdb.sql
unset VC_DB_ROOT_PASSWORD_VALUE
test -s backup/vcdb.sql
sha256sum backup/vcdb.sql > backup/SHA256SUMS
```

#### 步骤21：停止并删除容器但保留卷

```bash
sudo docker compose --env-file .env down
sudo docker compose --env-file .env ps -a
sudo docker volume ls --filter name=vcstack
```

不得使用`down -v`。重新创建：

```bash
sudo docker compose --env-file .env up -d
sudo docker compose --env-file .env ps
curl --fail http://127.0.0.1:8088/api/visits
```

数据和访问计数应按照课程应用设计保持。

#### 步骤22：生成配置与资源清单

```bash
{
  date -Is
  sha256sum compose.yaml .env.example .gitignore
  sudo docker compose --env-file .env config --services
  sudo docker compose --env-file .env config --images
  sudo docker compose --env-file .env ps
  sudo docker volume ls --filter name=vcstack
  sudo docker network ls --filter name=vcstack
} > evidence/lab10-result.txt
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
ls -la .env .env.example
grep -E '^[A-Z0-9_]+=' .env | sed 's/=.*/=<hidden>/'
sudo docker compose --env-file .env config --quiet
```

不要把密码直接写回`compose.yaml`。

### 2. db一直为unhealthy

```bash
sudo docker compose --env-file .env ps db
sudo docker compose --env-file .env logs --tail 100 db
sudo docker inspect vcstack-db-1 --format '{{json .State.Health}}'
```

检查已有卷、镜像版本、初始化变量和健康检查，不直接删除卷。

### 3. gateway返回502

依次检查API状态、健康、网络和日志：

```bash
sudo docker compose --env-file .env ps api
sudo docker compose --env-file .env logs --tail 100 gateway api
sudo docker inspect vcstack-api-1 --format '{{json .NetworkSettings.Networks}}'
```

### 4. `down`后发现数据还在

这是命名卷的预期行为。只有明确使用`down -v`或删除卷才会清理数据。本课程综合项目结束前禁止随意删除卷。

### 5. 改了Compose但容器未更新

```bash
sudo docker compose --env-file .env config --quiet
sudo docker compose --env-file .env up -d --force-recreate <服务名>
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
sudo docker compose --env-file .env stop
```

- 实验11将使用同一项目完成Rocky/Ubuntu迁移和综合排障。

