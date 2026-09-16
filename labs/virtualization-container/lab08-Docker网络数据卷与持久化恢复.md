# 实验8：Docker网络、数据卷与持久化恢复

> 所属模块：模块二 Docker容器化应用构建与交付
>
> 建议学时：8学时
>
> 实验方式：个人
>
> 对应学习通章节：[2.3 Docker网络、存储与有状态数据](../../textbooks/virtualization-container/模块二/2.3-Docker网络、存储与有状态数据.md)
>
> 知识前置：实验7中的镜像、容器生命周期与离线交付
>
> 状态依赖：实验7保留的Docker环境和课程固定镜像；本实验网络和卷由本实验创建
>
> 建议起点：`VC-V2`
>
> 项目成果：自定义网络、多容器通信、命名卷和绑定挂载，以及数据删除与恢复验证

## 一、项目情境

TechCorp准备把Web、API和数据库拆成多个容器。数据库不能直接暴露给所有客户端，容器重建后业务数据也不能丢失。你需要设计前端与后端网络边界，让容器通过服务名称通信，并使用命名卷和绑定挂载保存数据。最后模拟容器和数据卷故障，从备份恢复数据并完成业务复测。

## 二、实验目标

### 1. 知识目标

1. 说明默认bridge、自定义bridge、容器DNS和端口发布的关系。
2. 区分`EXPOSE`、容器端口和宿主机发布端口。
3. 区分容器可写层、命名卷、绑定挂载和tmpfs。
4. 说明删除容器、删除卷和`docker compose down -v`的数据影响。
5. 理解Rocky SELinux对绑定挂载标签的影响。

### 2. 能力目标

1. 创建前端、后端自定义网络并控制容器连接范围。
2. 使用容器名称完成DNS解析和服务访问。
3. 使用命名卷持久化MySQL数据。
4. 使用绑定挂载发布和修改静态内容。
5. 备份和恢复命名卷，完成数据一致性验证。
6. 排查端口冲突、网络缺失、名称错误、挂载权限和SELinux问题。

### 3. 素质目标

1. 数据删除前先备份并验证备份可读。
2. 数据库不无条件发布到宿主机或校园网。
3. 不使用`chmod 777`或关闭SELinux解决挂载问题。

## 三、知识准备

### 1. 网络拓扑

```text
Ubuntu或Rocky客户端
        │ 宿主机8082
        ▼
vc-web（front-net）
        │ 容器名访问
        ▼
vc-api（front-net + back-net）
        │ 容器名vc-db:3306
        ▼
vc-db（back-net）
```

只有`vc-web`发布宿主机端口。数据库仅连接`back-net`，不使用`-p 3306:3306`。

### 2. 存储对比

| 存储方式 | 生命周期 | 主机可见性 | 适用场景 |
|---|---|---|---|
| 容器可写层 | 随容器删除 | 由Docker内部管理 | 临时状态 |
| 命名卷 | 独立于容器 | Docker管理 | 数据库和长期应用数据 |
| 绑定挂载 | 取决于主机目录 | 路径明确 | 配置、源代码和静态内容 |
| tmpfs | 随容器停止消失 | 仅内存 | 临时敏感或高速数据 |

### 3. 课程镜像

教师镜像清单至少提供：

```text
<COURSE_REGISTRY>/vc/web:<COURSE_TAG>
<COURSE_REGISTRY>/vc/api:<COURSE_TAG>
<COURSE_REGISTRY>/vc/mysql:<COURSE_TAG>
<COURSE_REGISTRY>/vc/toolbox:<COURSE_TAG>
```

离线包必须同时包含这些镜像，否则网络正常也无法完成多容器任务。

## 四、实验环境

- 主要在Rocky Docker主机完成，Ubuntu用于外部访问验证。
- Rocky与Ubuntu已完成实验7并保留课程镜像。
- 教师API镜像提供`/health`和`/info`接口，并能读取`DB_HOST`环境变量。
- 教师MySQL镜像与课程固定版本一致。
- 使用实验密码，不使用真实业务密码。
- Rocky的SELinux保持Enforcing，firewalld保持启用。

## 五、项目任务

1. 建立容器网络和存储基线。
2. 创建`front-net`与`back-net`。
3. 验证同网容器名称解析和跨网隔离。
4. 使用绑定挂载发布静态内容。
5. 使用命名卷运行MySQL并写入验证数据。
6. 备份卷、删除重建容器并证明数据仍在。
7. 模拟卷数据丢失并从归档恢复。
8. 完成网络或挂载故障排查。

## 六、实验步骤

### 任务一：建立基线

#### 步骤1：确认课程镜像

在Rocky执行：

```bash
mkdir -p ~/vc-course/evidence ~/vc-course/lab08/site ~/vc-course/lab08/backup
```

执行`vim ~/vc-course/lab08/images.sh`并输入：

```text
source "$HOME/vc-course/course-env.sh"
export VC_WEB_IMAGE="$COURSE_REGISTRY/vc/web:$COURSE_TAG"
export VC_API_IMAGE="$COURSE_REGISTRY/vc/api:$COURSE_TAG"
export VC_MYSQL_IMAGE="$COURSE_REGISTRY/vc/mysql:$COURSE_TAG"
export VC_TOOLBOX_IMAGE="$COURSE_REGISTRY/vc/toolbox:$COURSE_TAG"
```

设置权限并检查：

```bash
chmod 600 ~/vc-course/lab08/images.sh
```

```bash
source ~/vc-course/lab08/images.sh
sudo docker image inspect "$VC_WEB_IMAGE" "$VC_API_IMAGE" \
  "$VC_MYSQL_IMAGE" "$VC_TOOLBOX_IMAGE" >/dev/null
```

```bash
sudo docker image ls --digests
```

上述`docker image inspect`返回0才表示四个固定标签镜像全部存在。缺少时从课程仓库拉取或导入教师离线包。若中途重新打开终端，先执行`source ~/vc-course/lab08/images.sh`再继续本实验。

#### 步骤2：确认名称未占用

```bash
sudo docker container ls -a \
  --filter name=vc-web \
  --filter name=vc-api \
  --filter name=vc-db
```

```bash
sudo docker network ls
```

```bash
sudo docker volume ls
```

```bash
sudo ss -lntp | grep ':8082' || true
```

如果发现同名对象，先确认是否为自己的未完成实验。不要使用模糊过滤后批量删除。

### 任务二：创建网络并验证DNS

#### 步骤3：创建前后端网络

```bash
sudo docker network create --driver bridge vc-front-net
```

```bash
sudo docker network create --driver bridge vc-back-net
```

```bash
sudo docker network ls --filter name=vc-
```

```bash
sudo docker network inspect vc-front-net
```

```bash
sudo docker network inspect vc-back-net
```

记录两张网络的Subnet、Gateway和ID。Docker自动分配的网段不得与机房网段冲突；若冲突，由教师统一指定子网重新创建。

#### 步骤4：运行API容器

```bash
source ~/vc-course/lab08/images.sh
sudo docker run -d \
  --name vc-api \
  --network vc-front-net \
  -e APP_ENV=lab08 \
  -e DB_HOST=vc-db \
  "$VC_API_IMAGE"
```

把API再连接到后端网络：

```bash
sudo docker network connect vc-back-net vc-api
```

```bash
sudo docker inspect vc-api \
  --format '{{json .NetworkSettings.Networks}}'
```

#### 步骤5：使用工具容器验证名称解析

```bash
source ~/vc-course/lab08/images.sh
sudo docker run --rm \
  --network vc-front-net \
  "$VC_TOOLBOX_IMAGE" \
  getent hosts vc-api
```

继续访问健康接口，实际命令以工具镜像包含的客户端为准：

```bash
source ~/vc-course/lab08/images.sh
sudo docker run --rm \
  --network vc-front-net \
  "$VC_TOOLBOX_IMAGE" \
  curl --fail http://vc-api:8080/health
```

预期返回课程定义的`API_HEALTH_OK`。

#### 步骤6：验证网络隔离

仅连接`vc-front-net`的临时容器不应解析尚未创建的`vc-db`。数据库创建后再次验证：

```bash
source ~/vc-course/lab08/images.sh
sudo docker run --rm \
  --network vc-front-net \
  "$VC_TOOLBOX_IMAGE" \
  getent hosts vc-db || echo 'DB_NOT_VISIBLE_ON_FRONT_NET'
```

后续`vc-db`只连接`vc-back-net`，因此前端网络中的普通容器不能通过服务名访问数据库。

> **验收点**：API同时连接前后端网络；同一自定义网络中可以使用容器名解析；不共享网络的对象被隔离。

### 任务三：使用绑定挂载发布Web内容

#### 步骤7：创建主机静态文件

执行`vim ~/vc-course/lab08/site/index.html`并输入：

```html
<!doctype html>
<meta charset="utf-8">
<title>VC Storage Lab</title>
<h1>VC_BIND_MOUNT_OK</h1>
<p>course=virtualization-container</p>
```

```bash
chmod 644 ~/vc-course/lab08/site/index.html
```

#### 步骤8：在Rocky运行绑定挂载容器

Rocky启用SELinux时使用`:Z`为此容器私有重标记：

```bash
source ~/vc-course/course-env.sh
source ~/vc-course/lab08/images.sh
sudo docker run -d \
  --name vc-web \
  --network vc-front-net \
  -p "$ROCKY_SERVER_IP:8082:80" \
  -v "$(readlink -f ~/vc-course/lab08/site):/usr/share/nginx/html:ro,Z" \
  "$VC_WEB_IMAGE"
```

使用`readlink -f`得到明确的绝对路径，可以避免因当前工作目录不同而挂载错误。检查挂载源：

```bash
readlink -f ~/vc-course/lab08/site
```

```bash
sudo docker inspect vc-web --format '{{json .Mounts}}'
```

如果前面的容器因路径错误未成功创建，确认目标名称后删除并按正确路径重建。

#### 步骤9：验证绑定挂载

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$ROCKY_SERVER_IP:8082/" | grep VC_BIND_MOUNT_OK
```

```bash
sudo docker logs --tail 20 vc-web
```

```bash
ls -lZ ~/vc-course/lab08/site
```

跨主机验证前，记录Docker实际发布地址和过滤链：

```bash
sudo docker port vc-web
```

```bash
sudo iptables -S DOCKER-USER 2>/dev/null || true
```

```bash
sudo firewall-cmd --state
```

Docker发布端口可能绕过只看firewalld zone所得出的直觉结论，因此本实验不使用“临时开放8082”来证明安全。端口只绑定`rocky-server`的指定地址并运行在隔离VMnet8中；生产来源限制应使用`DOCKER-USER`链或上游防火墙。

然后切换到Ubuntu执行：

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$ROCKY_SERVER_IP:8082/" | grep VC_BIND_MOUNT_OK
```

如跨主机访问失败，按Linux课程方法检查绑定地址、Docker发布端口、Rocky路由和`DOCKER-USER`链。记录Docker规则与firewalld的实际交互，不永久关闭防火墙。

#### 步骤10：修改主机文件并观察容器

```bash
sed -i 's/VC_BIND_MOUNT_OK/VC_BIND_MOUNT_UPDATED/' \
  ~/vc-course/lab08/site/index.html
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$ROCKY_SERVER_IP:8082/" | grep VC_BIND_MOUNT_UPDATED
```

不重建容器即可看到变化，说明容器直接读取主机挂载目录。

### 任务四：使用命名卷运行MySQL

#### 步骤11：创建命名卷

```bash
sudo docker volume create vc-mysql-data
```

```bash
sudo docker volume inspect vc-mysql-data
```

记录Mountpoint，但日常不直接修改`/var/lib/docker/volumes`内部文件。

#### 步骤12：启动数据库容器

```bash
source ~/vc-course/lab08/images.sh
sudo docker run -d \
  --name vc-db \
  --network vc-back-net \
  -e MYSQL_ROOT_PASSWORD='LabRoot-ChangeMe!' \
  -e MYSQL_DATABASE='vcdb' \
  -e MYSQL_USER='vcuser' \
  -e MYSQL_PASSWORD='LabUser-ChangeMe!' \
  -v vc-mysql-data:/var/lib/mysql \
  "$VC_MYSQL_IMAGE"
```

本密码仅用于隔离课程环境，不提交到Git。实验10将使用环境变量模板统一管理。

#### 步骤13：等待数据库就绪

```bash
sudo docker logs -f vc-db
```

看到教师清单规定的“ready for connections”类信息后按`Ctrl+C`退出日志跟随，容器不会停止。验证：

```bash
sudo docker exec vc-db \
  mysqladmin ping -uroot -p'LabRoot-ChangeMe!'
```

#### 步骤14：写入验证数据

```bash
sudo docker exec vc-db mysql \
  -uvcuser -p'LabUser-ChangeMe!' vcdb \
  -e "CREATE TABLE IF NOT EXISTS evidence(id INT PRIMARY KEY, marker VARCHAR(64)); INSERT INTO evidence VALUES (1,'VOLUME_DATA_OK') ON DUPLICATE KEY UPDATE marker='VOLUME_DATA_OK'; SELECT * FROM evidence;"
```

预期查询返回`VOLUME_DATA_OK`。

#### 步骤15：从API网络验证数据库名称

API已连接`vc-back-net`，检查解析：

```bash
sudo docker exec vc-api getent hosts vc-db
```

如果API镜像没有`getent`，使用工具容器：

```bash
source ~/vc-course/lab08/images.sh
sudo docker run --rm \
  --network vc-back-net \
  "$VC_TOOLBOX_IMAGE" \
  getent hosts vc-db
```

不发布3306到宿主机也不影响同一后端网络中的容器访问。

> **验收点**：MySQL数据位于命名卷，数据库只连接后端网络且没有宿主机3306端口发布。

### 任务五：证明卷独立于容器

#### 步骤16：删除并重建数据库容器

先再次查询并保存数据证据：

```bash
sudo docker exec vc-db mysql \
  -uvcuser -p'LabUser-ChangeMe!' vcdb \
  -e 'SELECT * FROM evidence;'
```

确认后删除容器但不删除卷：

```bash
sudo docker stop vc-db
```

```bash
sudo docker rm vc-db
```

```bash
sudo docker volume ls --filter name=vc-mysql-data
```

使用相同卷重建：

```bash
source ~/vc-course/lab08/images.sh
sudo docker run -d \
  --name vc-db \
  --network vc-back-net \
  -e MYSQL_ROOT_PASSWORD='LabRoot-ChangeMe!' \
  -e MYSQL_DATABASE='vcdb' \
  -e MYSQL_USER='vcuser' \
  -e MYSQL_PASSWORD='LabUser-ChangeMe!' \
  -v vc-mysql-data:/var/lib/mysql \
  "$VC_MYSQL_IMAGE"
```

等待就绪后查询：

```bash
sudo docker exec vc-db mysql \
  -uvcuser -p'LabUser-ChangeMe!' vcdb \
  -e 'SELECT * FROM evidence;'
```

仍应看到`VOLUME_DATA_OK`。

### 任务六：备份与恢复命名卷

#### 步骤17：停止数据库形成一致性备份

```bash
sudo docker stop vc-db
```

数据库备份生产环境通常优先使用数据库逻辑备份或一致性工具。本实验为了学习Docker卷归档，在已停止容器的前提下复制卷文件。

#### 步骤18：使用工具镜像归档卷

```bash
cd ~/vc-course/lab08
```

```bash
source ~/vc-course/lab08/images.sh
sudo docker run --rm \
  -v vc-mysql-data:/source:ro \
  -v "$PWD/backup:/backup:Z" \
  "$VC_TOOLBOX_IMAGE" \
  sh -c 'cd /source && tar -cpf /backup/vc-mysql-data.tar .'
```

```bash
sudo chown "$(id -u):$(id -g)" backup/vc-mysql-data.tar
```

```bash
ls -lh backup/vc-mysql-data.tar
```

```bash
sha256sum backup/vc-mysql-data.tar \
  | tee backup/SHA256SUMS
```

```bash
tar -tf backup/vc-mysql-data.tar | sed -n '1,20p'
```

备份文件必须非空，能够列出内容并通过校验。

#### 步骤19：创建新卷并恢复

为降低风险，不立即删除原卷，先恢复到新卷：

```bash
cd ~/vc-course/lab08
```

```bash
sudo docker volume create vc-mysql-restored
```

```bash
source ~/vc-course/lab08/images.sh
sudo docker run --rm \
  -v vc-mysql-restored:/target \
  -v "$PWD/backup:/backup:ro,Z" \
  "$VC_TOOLBOX_IMAGE" \
  sh -c 'cd /target && tar -xpf /backup/vc-mysql-data.tar'
```

```bash
sudo docker volume inspect vc-mysql-restored
```

#### 步骤20：使用恢复卷启动验证容器

```bash
source ~/vc-course/lab08/images.sh
sudo docker run -d \
  --name vc-db-restored \
  --network vc-back-net \
  -e MYSQL_ROOT_PASSWORD='LabRoot-ChangeMe!' \
  -e MYSQL_DATABASE='vcdb' \
  -e MYSQL_USER='vcuser' \
  -e MYSQL_PASSWORD='LabUser-ChangeMe!' \
  -v vc-mysql-restored:/var/lib/mysql \
  "$VC_MYSQL_IMAGE"
```

等待就绪后：

```bash
sudo docker exec vc-db-restored mysql \
  -uvcuser -p'LabUser-ChangeMe!' vcdb \
  -e 'SELECT * FROM evidence;'
```

必须返回`VOLUME_DATA_OK`。这比仅证明tar文件存在更可靠。

> **验收点**：使用新卷恢复并启动了独立数据库容器，业务数据查询通过。

### 任务七：故障排查

#### 步骤21：注入错误网络名称

创建一次预期失败：

```bash
source ~/vc-course/lab08/images.sh
sudo docker run --rm \
  --network vc-wrong-net \
  "$VC_TOOLBOX_IMAGE" \
  true
```

记录Docker返回的“network not found”类错误。检查：

```bash
sudo docker network ls
```

根据业务拓扑选择`vc-front-net`或`vc-back-net`，不通过随意创建拼错名称的网络掩盖问题。

#### 步骤22：检查挂载与SELinux证据

```bash
sudo docker inspect vc-web --format '{{json .Mounts}}'
```

```bash
ls -ldZ ~/vc-course/lab08/site
```

```bash
sudo docker logs --tail 30 vc-web
```

教师可删除`:Z`后重建一个故障容器，让学生通过日志、挂载路径和审计信息判断。标准修复是恢复正确标签或挂载选项，不关闭SELinux。

### 任务八：生成验收记录

#### 步骤23：输出网络、端口和存储清单

```bash
script -q ~/vc-course/evidence/lab08-result.txt
```

```bash
date -Is
```

```bash
hostname
```

```bash
sudo docker container ls -a
```

```bash
sudo docker network ls
```

```bash
sudo docker network inspect vc-front-net vc-back-net
```

```bash
sudo docker volume ls
```

```bash
sudo docker volume inspect vc-mysql-data vc-mysql-restored
```

```bash
sudo docker port vc-web
```

```bash
exit
```

## 七、独立实践

教师随机选择一种故障：

- `vc-api`只连接错误网络；
- 客户端使用容器端口而不是宿主机发布端口；
- `vc-web`绑定挂载路径拼错；
- Rocky SELinux标签错误；
- MySQL容器重建时忘记挂载原卷；
- 学生误以为删除容器等于删除卷。

学生必须从拓扑、`inspect`、端口、日志和数据查询中证明根因，修复后按原始客户端路径复测。

## 八、验收标准

- [ ] 能绘制前端网络和后端网络拓扑。
- [ ] `vc-api`连接前后两张网络，数据库只连接后端网络。
- [ ] 同网容器可以通过容器名解析和访问。
- [ ] 数据库未发布宿主机3306端口。
- [ ] Rocky绑定挂载使用合理权限和SELinux标签。
- [ ] 修改主机静态文件能够反映到容器。
- [ ] MySQL数据写入命名卷并返回`VOLUME_DATA_OK`。
- [ ] 删除并重建容器后数据仍存在。
- [ ] 卷归档具有SHA256并能列出内容。
- [ ] 数据恢复到新卷后能够启动数据库并查询原数据。
- [ ] 完成至少一次网络或挂载故障排查。

## 九、成果提交

```text
lab08-学号-姓名/
├── docker-network-topology.png或.pdf
├── lab08-result.txt
├── bind-mount-check.md
├── mysql-volume-query.txt
├── backup/SHA256SUMS
├── restore-query.txt
└── fault-report.md
```

卷归档按教师要求保存到大文件目录，不提交普通Git仓库，也不提交实验密码。

## 十、常见问题

### 1. 容器之间使用IP能通，名称不能解析

确认使用自定义bridge而不是默认bridge，并检查两个容器是否共享同一网络：

```bash
sudo docker inspect vc-api --format '{{json .NetworkSettings.Networks}}'
```

业务配置应使用稳定的容器或服务名称，不记录临时容器IP。

### 2. 宿主机访问8082失败

```bash
sudo docker container ls --filter name=vc-web
```

```bash
sudo docker port vc-web
```

```bash
sudo ss -lntp | grep ':8082'
```

```bash
source ~/vc-course/course-env.sh
curl -v "http://$ROCKY_SERVER_IP:8082/"
```

```bash
sudo docker logs --tail 50 vc-web
```

先证明本机路径，再检查远程网络和防火墙。

### 3. MySQL不断重启

```bash
sudo docker container ls -a --filter name=vc-db
```

```bash
sudo docker logs --tail 100 vc-db
```

```bash
sudo docker inspect vc-db --format '{{json .State}}'
```

```bash
sudo docker inspect vc-db --format '{{json .Mounts}}'
```

常见原因包括现有卷数据版本不兼容、初始化环境变量错误或权限问题。不要直接删除卷。

### 4. 恢复归档后数据库无法启动

确认备份时数据库已停止、归档保留权限、恢复目录正确、镜像版本与源环境一致。保留原卷，优先在新卷反复验证。

### 5. 绑定挂载返回403或Permission denied

检查主机路径、传统权限、SELinux类型和`:Z`选项。不能用关闭SELinux或`chmod 777`替代定位。

## 十一、课后思考与拓展

1. 为什么数据库容器通常不需要向宿主机发布3306？
2. 命名卷比绑定挂载更适合哪些场景？
3. 文件级卷归档和`mysqldump`分别解决什么问题？
4. Kubernetes中的Service和PersistentVolume与本实验哪些对象相似？

## 十二、环境保留或清理

保留`vc-front-net`、`vc-back-net`、`vc-mysql-data`、`vc-mysql-restored`和课程镜像。停止容器节省资源：

```bash
sudo docker stop vc-web vc-api vc-db-restored 2>/dev/null || true
```

```bash
sudo docker container ls -a --filter name=vc-
```

如果`vc-db`仍处于停止状态则保留。不要删除卷；实验10会迁移到Compose管理。
