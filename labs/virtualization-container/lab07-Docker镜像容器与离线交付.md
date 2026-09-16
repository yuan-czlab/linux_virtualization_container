# 实验7：Docker镜像、容器与离线交付

> 所属模块：模块二 Docker容器化应用构建与交付
>
> 建议学时：6学时
>
> 实验方式：个人
>
> 对应学习通章节：[2.2 镜像、容器、Registry与离线交付](../../textbooks/virtualization-container/模块二/2.2-镜像、容器、Registry与离线交付.md)
>
> 知识前置：实验6中的Docker架构、服务和双发行版差异
>
> 状态依赖：实验6在Rocky和Ubuntu部署的Docker Engine、Compose插件及课程Registry访问能力
>
> 建议起点：保留实验6成果的当前环境
>
> 项目成果：镜像和容器生命周期记录、课程仓库拉取结果、镜像导出导入包及SHA256校验

## 一、项目情境

学校网络访问公共Docker镜像站不稳定，因此TechCorp课程环境采用学校私有镜像仓库和U盘离线包双通道。你需要掌握镜像名称、标签、摘要、平台架构和分层，完成容器生命周期操作，并把Rocky中的课程镜像导出、校验、传递到Ubuntu后重新运行，证明镜像可以可靠交付。

## 二、实验目标

### 1. 知识目标

1. 区分镜像、镜像层、容器、容器可写层和仓库。
2. 解释镜像引用`仓库地址/命名空间/仓库:标签`。
3. 区分标签、镜像ID和内容摘要。
4. 说明`docker save/load`与容器文件复制的差异。

### 2. 能力目标

1. 从课程仓库拉取固定标签或摘要镜像。
2. 使用`create`、`start`、`run`、`exec`、`logs`、`inspect`、`stop`和`rm`管理容器。
3. 查看镜像平台、配置、历史和摘要。
4. 导出、校验、复制和导入离线镜像包。
5. 在Rocky与Ubuntu之间完成跨发行版运行验证。

### 3. 素质目标

1. 不以`latest`作为正式交付依据。
2. 不把Registry密码写入命令历史或实验报告。
3. 删除容器和镜像前先确认精确名称、依赖和用途。

## 三、知识准备

### 1. 镜像引用

```text
<COURSE_REGISTRY>/vc/web:<COURSE_TAG>
└────仓库主机────┘ └命名空间/仓库┘ └标签┘
```

标签便于人识别，但可以重新指向其他内容；摘要根据镜像内容生成，适合证明交付内容是否一致。

### 2. 镜像与容器

```text
只读镜像层
   +
容器可写层
   =
运行中的容器文件系统视图
```

删除容器会丢失其可写层中的未持久化数据，但不会自动删除镜像。持久化数据将在实验8通过卷处理。

### 3. 分发双通道

```text
在线：学校课程Registry → docker pull → 本地主机镜像库
离线：教师/学生docker save → tar归档 → SHA256 → U盘/共享目录
      → SHA256复核 → docker load
```

## 四、实验环境

- Rocky和Ubuntu均已完成实验6。
- 教师发布`<COURSE_REGISTRY>`、`<COURSE_TAG>`和镜像清单。
- 课程至少提供Web镜像与工具镜像。
- U盘或共享目录至少有10GB可用空间。
- 正式实验容器名称统一使用`vc-`前缀。

## 五、项目任务

1. 读取课程镜像清单并拉取或导入镜像。
2. 检查镜像身份、配置、层和平台。
3. 完成容器完整生命周期。
4. 验证端口发布和日志。
5. 在Rocky导出镜像并生成SHA256。
6. 在Ubuntu导入并复现相同服务。
7. 清理临时容器但保留课程镜像。

## 六、实验步骤

### 任务一：准备课程镜像

#### 步骤1：读取教师镜像清单

教师清单至少包含：

| 字段 | 示例含义 |
|---|---|
| 镜像完整名称 | Registry、命名空间和仓库 |
| 固定标签 | 本学期课程版本 |
| 摘要 | 内容一致性标识 |
| 架构 | 通常为linux/amd64 |
| 大小 | 估算磁盘和传输时间 |
| 使用实验 | 防止删除仍需使用的镜像 |
| 离线包文件名与SHA256 | 无网络回退 |

将教师发布的Web镜像记为：

```text
<COURSE_REGISTRY>/vc/web:<COURSE_TAG>
```

#### 步骤2：检查本地状态

在Rocky执行：

```bash
mkdir -p ~/vc-course/evidence ~/vc-course/offline
```

```bash
sudo docker image ls --digests
```

```bash
sudo docker container ls -a
```

```bash
df -hT /
```

```bash
sudo docker system df
```

不要先执行`docker system prune`。清理命令会删除未使用但可能属于后续实验的对象。

#### 步骤3：从课程仓库拉取

如果仓库允许匿名只读：

```bash
source ~/vc-course/course-env.sh
sudo docker pull "$COURSE_REGISTRY/vc/web:$COURSE_TAG"
```

需要登录时，教师通过安全渠道提供个人或课程只读凭据。避免把密码直接写在命令参数：

```bash
source ~/vc-course/course-env.sh
read -rsp 'Registry password: ' VC_REGISTRY_PASSWORD
printf '%s' "$VC_REGISTRY_PASSWORD" \
  | sudo docker login "$COURSE_REGISTRY" \
      --username "$COURSE_REGISTRY_USER" \
      --password-stdin
unset VC_REGISTRY_PASSWORD
```

实验结束按教师要求退出：

```bash
source ~/vc-course/course-env.sh
sudo docker logout "$COURSE_REGISTRY"
```

#### 步骤4：离线导入回退

若仓库不可达，先验证教师归档：

```bash
source ~/vc-course/course-env.sh
sha256sum "$COURSE_MEDIA/docker-images/vc-web-$COURSE_TAG.tar"
```

与清单一致后：

```bash
source ~/vc-course/course-env.sh
sudo docker load -i "$COURSE_MEDIA/docker-images/vc-web-$COURSE_TAG.tar"
```

导入后完整镜像名称必须与后续命令一致。如果离线包中的标签不同，使用教师清单规定的`docker tag`补充，不能自行猜测仓库地址。

### 任务二：检查镜像

#### 步骤5：查看镜像身份

```bash
source ~/vc-course/course-env.sh
sudo docker image ls --digests \
  "$COURSE_REGISTRY/vc/web"
```

```bash
source ~/vc-course/course-env.sh
sudo docker image inspect \
  "$COURSE_REGISTRY/vc/web:$COURSE_TAG" \
  --format 'id={{.Id}} arch={{.Architecture}} os={{.Os}} size={{.Size}}'
```

```bash
source ~/vc-course/course-env.sh
sudo docker image inspect \
  "$COURSE_REGISTRY/vc/web:$COURSE_TAG" \
  --format '{{json .RepoDigests}}'
```

记录镜像ID、架构、操作系统和RepoDigest。离线导入的镜像在未从Registry拉取时可能没有RepoDigest，应使用镜像ID和归档SHA256共同验收。

#### 步骤6：查看历史与配置

```bash
source ~/vc-course/course-env.sh
sudo docker history --no-trunc \
  "$COURSE_REGISTRY/vc/web:$COURSE_TAG" | sed -n '1,15p'
```

```bash
source ~/vc-course/course-env.sh
sudo docker image inspect \
  "$COURSE_REGISTRY/vc/web:$COURSE_TAG" \
  --format 'entrypoint={{json .Config.Entrypoint}} cmd={{json .Config.Cmd}} ports={{json .Config.ExposedPorts}} user={{json .Config.User}}'
```

说明镜像默认启动命令、暴露端口和运行用户。

### 任务三：完成容器生命周期

#### 步骤7：使用create创建但不启动

先确认名称未占用：

```bash
sudo docker container inspect vc-web01 >/dev/null 2>&1 \
  && echo '名称已占用，请先确认来源' || true
```

确认没有同名课程容器后：

```bash
source ~/vc-course/course-env.sh
sudo docker create \
  --name vc-web01 \
  -p "$ROCKY_SERVER_IP:8081:80" \
  "$COURSE_REGISTRY/vc/web:$COURSE_TAG"
```

```bash
sudo docker container ls -a --filter name=vc-web01
```

状态应为Created，宿主机8081此时通常尚未监听。

#### 步骤8：启动并验证

```bash
sudo docker start vc-web01
```

```bash
sudo docker container ls --filter name=vc-web01
```

```bash
sudo docker port vc-web01
```

```bash
sudo ss -lntp | grep ':8081'
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$ROCKY_SERVER_IP:8081/" | grep VC_WEB_OK
```

跨主机验证前，在`rocky-server`记录发布地址和Docker过滤链：

```bash
sudo docker port vc-web01
```

```bash
sudo iptables -S DOCKER-USER 2>/dev/null || true
```

```bash
sudo firewall-cmd --state
```

Docker发布端口会建立自己的包过滤和转发规则，不能把`firewall-cmd --add-port`或“UFW显示拒绝”当成可靠的容器访问控制。本实验通过绑定`rocky-server`的指定IPv4地址和隔离的VMnet8网络限制暴露面；生产环境还应在`DOCKER-USER`链或上游防火墙实施来源策略。

然后从另一台Linux主机执行：

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$ROCKY_SERVER_IP:8081/" | grep VC_WEB_OK
```

如果跨主机失败，结合绑定地址、Rocky路由、Docker端口映射和`DOCKER-USER`链排查，不通过关闭防火墙长期解决。

#### 步骤9：查看日志、进程和配置

```bash
sudo docker logs --tail 20 vc-web01
```

```bash
sudo docker top vc-web01
```

```bash
sudo docker stats --no-stream vc-web01
```

```bash
sudo docker inspect vc-web01 \
  --format 'status={{.State.Status}} ip={{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}} image={{.Image}}'
```

发送一次请求后，Web访问日志应增加。

#### 步骤10：进入容器检查

教师Web镜像支持`/bin/sh`时：

```bash
sudo docker exec vc-web01 hostname
```

```bash
sudo docker exec vc-web01 id
```

```bash
sudo docker exec vc-web01 cat /etc/os-release
```

```bash
sudo docker exec vc-web01 ps
```

容器内发行版信息来自镜像用户空间，不等于宿主机发行版。容器仍共享宿主机内核。

#### 步骤11：停止、启动和重启

```bash
sudo docker stop --time 10 vc-web01
```

```bash
sudo docker container ls -a --filter name=vc-web01
```

```bash
source ~/vc-course/course-env.sh
curl --connect-timeout 2 "http://$ROCKY_SERVER_IP:8081/" || true
```

```bash
sudo docker start vc-web01
```

```bash
sudo docker restart vc-web01
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$ROCKY_SERVER_IP:8081/" | grep VC_WEB_OK
```

#### 步骤12：run与create+start比较

```bash
source ~/vc-course/course-env.sh
sudo docker run --rm \
  --name vc-once \
  "$COURSE_REGISTRY/vc/verify:$COURSE_TAG"
```

```bash
sudo docker container ls -a --filter name=vc-once
```

`run`组合了创建和启动；`--rm`使退出后的临时容器自动删除。

### 任务四：镜像标签与离线导出

#### 步骤13：创建课程交付标签

```bash
source ~/vc-course/course-env.sh
sudo docker tag \
  "$COURSE_REGISTRY/vc/web:$COURSE_TAG" \
  "vc-offline/web:$COURSE_TAG"
```

```bash
sudo docker image ls --digests | grep -E 'vc/web|vc-offline/web'
```

两个标签应指向同一镜像ID，标签本身不会复制所有层。

#### 步骤14：导出镜像归档

```bash
source ~/vc-course/course-env.sh
sudo docker save \
  -o "$HOME/vc-course/offline/vc-web-$COURSE_TAG-amd64.tar" \
  "$COURSE_REGISTRY/vc/web:$COURSE_TAG" \
  "vc-offline/web:$COURSE_TAG"
```

```bash
source ~/vc-course/course-env.sh
sudo chown "$(id -u):$(id -g)" \
  "$HOME/vc-course/offline/vc-web-$COURSE_TAG-amd64.tar"
```

```bash
source ~/vc-course/course-env.sh
ls -lh "$HOME/vc-course/offline/vc-web-$COURSE_TAG-amd64.tar"
```

```bash
source ~/vc-course/course-env.sh
(cd ~/vc-course/offline && sha256sum "vc-web-$COURSE_TAG-amd64.tar" | tee SHA256SUMS)
```

校验清单必须记录相对文件名。若把`/home/rocky-server/...`绝对路径写入清单，复制到`ubuntu-client`后会因用户主目录不同而无法校验。

复制到U盘或共享目录后，在目标位置再次执行：

```bash
sha256sum -c SHA256SUMS
```

校验失败时重新复制，不能继续导入损坏文件。

### 任务五：在Ubuntu导入和运行

#### 步骤15：确认Ubuntu目标环境

在Ubuntu执行：

```bash
sudo docker version
```

```bash
sudo docker container ls -a
```

```bash
sudo docker image ls --digests
```

```bash
df -hT /
```

#### 步骤16：导入离线包

将归档和`SHA256SUMS`复制到Ubuntu的`~/vc-course/offline/`，执行：

```bash
cd ~/vc-course/offline
```

```bash
sha256sum -c SHA256SUMS
```

```bash
source ~/vc-course/course-env.sh
sudo docker load -i "$HOME/vc-course/offline/vc-web-$COURSE_TAG-amd64.tar"
```

```bash
sudo docker image ls --digests | grep -E 'vc/web|vc-offline/web'
```

#### 步骤17：在Ubuntu复现服务

```bash
source ~/vc-course/course-env.sh
sudo docker run -d \
  --name vc-web-ubuntu \
  -p 8081:80 \
  "vc-offline/web:$COURSE_TAG"
```

```bash
sudo docker container ls --filter name=vc-web-ubuntu
```

```bash
curl --fail http://127.0.0.1:8081/ | grep VC_WEB_OK
```

```bash
sudo docker logs --tail 20 vc-web-ubuntu
```

对比Rocky与Ubuntu中的镜像ID、页面标记和容器内`/etc/os-release`。

> **验收点**：Ubuntu不访问Docker Hub也能通过Rocky导出的归档运行同一服务。

### 任务六：安全清理临时容器

#### 步骤18：列出精确目标

在Rocky：

```bash
sudo docker container ls -a \
  --filter name=vc-web01 \
  --filter name=vc-once
```

确认后：

```bash
sudo docker stop vc-web01 2>/dev/null || true
```

```bash
sudo docker rm vc-web01
```

在Ubuntu：

```bash
sudo docker stop vc-web-ubuntu
```

```bash
sudo docker rm vc-web-ubuntu
```

保留镜像和离线归档，后续实验仍需使用。

### 任务七：保存证据

#### 步骤19：生成镜像交付记录

在两台主机分别使用终端录制并标注主机名：

```bash
script -q ~/vc-course/evidence/lab07-image-result.txt
```

```bash
date -Is
```

```bash
hostname
```

```bash
sudo docker image ls --digests
```

```bash
source ~/vc-course/course-env.sh
sudo docker image inspect "vc-offline/web:$COURSE_TAG" --format 'id={{.Id}} arch={{.Architecture}} os={{.Os}}'
```

```bash
exit
```

## 七、独立实践

教师提供第二个体积较小的课程镜像，学生独立完成：

```text
获取 → 检查 → 创建 → 启动 → 验证 → 查看日志
→ 停止 → 导出 → 校验 → 在另一主机导入 → 再验证 → 清理容器
```

报告中必须记录镜像完整名称、标签、镜像ID、摘要或归档SHA256和架构。

## 八、验收标准

- [ ] 能正确解释镜像名称各部分。
- [ ] 正式镜像使用固定标签，不依赖`latest`。
- [ ] 已查看镜像ID、摘要、架构、默认命令、端口和历史。
- [ ] 完成create、start、run、exec、logs、inspect、stop、restart和rm。
- [ ] Rocky的8081服务可从客户端访问，日志存在请求。
- [ ] 使用`docker save`生成归档和SHA256。
- [ ] 归档复制到Ubuntu后校验通过。
- [ ] Ubuntu使用`docker load`导入并运行成功。
- [ ] Rocky和Ubuntu应用结果及镜像ID一致。
- [ ] 临时容器已清理，课程镜像和离线包仍保留。

## 九、成果提交

```text
lab07-学号-姓名/
├── image-manifest.md
├── rocky-lifecycle.txt
├── rocky-image-result.txt
├── ubuntu-image-result.txt
├── SHA256SUMS
├── offline-transfer-record.md
└── troubleshooting.md
```

镜像tar只上传到教师指定大文件位置，不提交普通Git仓库。

## 十、常见问题

### 1. `docker pull`超时

确认使用的是`<COURSE_REGISTRY>`而不是Docker Hub。检查DNS、课程仓库地址和证书；仓库不可用时立即切换到教师离线包，不反复消耗课堂时间。

### 2. Registry证书错误

使用教师发布的CA证书和安装说明。不要通过在所有主机配置`insecure-registries`绕过本应可信的HTTPS验证，除非教师明确将隔离的教学HTTP Registry作为实验对象。

### 3. 端口8081已被占用

```bash
sudo ss -lntp | grep ':8081'
```

```bash
sudo docker container ls --format '{{.Names}} {{.Ports}}'
```

确认占用者后选择教师允许的其他端口，不直接终止未知进程。

### 4. 无法删除镜像

先检查哪些容器引用镜像：

```bash
source ~/vc-course/course-env.sh
sudo docker container ls -a --filter "ancestor=vc-offline/web:$COURSE_TAG"
```

本实验不要求删除课程镜像。

### 5. `docker load`后镜像名称与预期不同

`load`恢复归档中保存的标签。使用`docker image ls`检查，再按教师清单添加准确标签；不能假设导入后自动使用当前课程仓库名称。

## 十一、课后思考与拓展

1. 标签为什么不能单独证明镜像内容没有变化？
2. `docker save`为什么适合课程离线分发，而复制容器目录不适合？
3. 镜像已经跨Rocky和Ubuntu运行，哪些内容仍然依赖宿主机内核？

## 十二、环境保留或清理

- 保留课程Web、验证和工具镜像。
- 保留`~/vc-course/offline`中的归档和SHA256清单。
- 删除本实验临时容器，释放8081。
- 不执行`docker system prune`。
- 在Rocky和Ubuntu均完成固定镜像与离线导入验收后，分别创建VMware检查点`VC-V2-Docker与离线交付完成`；恢复记录中简称`VC-V2`。

本实验没有修改永久firewalld规则；容器删除后8081发布规则随之消失。

