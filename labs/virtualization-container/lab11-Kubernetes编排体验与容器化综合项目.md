# 实验11：Kubernetes编排体验与容器化综合项目

> 所属模块：模块二 Docker容器化应用构建与交付
>
> 建议学时：8学时
>
> 实验方式：2—3人协作，个人操作与个人答辩
>
> 对应学习通章节：[2.6 Kubernetes编排体验与综合项目](../../textbooks/virtualization-container/模块二/2.6-Kubernetes编排体验与综合项目.md)
>
> 知识前置：实验6—10全部容器能力和学习通章节2.6中的Kubernetes对象
>
> 状态依赖：实验10的`~/vc-course/lab10/techcorp-stack`、应用镜像、Compose运行证据和数据库备份；另需教师预建Kubernetes环境
>
> 建议起点：`VC-V3`
>
> 项目成果：Kubernetes Deployment/Service基础操作、Rocky/Ubuntu跨环境部署、离线交付包、故障报告和答辩材料

## 一、项目情境

TechCorp已经能用Compose在单台Linux主机运行多服务应用。下一阶段需要理解云平台如何在集群中维持期望副本、替换异常实例并提供稳定访问入口。你将连接教师预建Kubernetes集群，使用指定命名空间部署课程应用、查看Pod和日志、通过Service访问并完成扩缩容。随后按正式主流程把Compose项目从Ubuntu交付到Rocky，在无Docker Hub条件下完成部署、故障排查、恢复和答辩。Rocky到Ubuntu的反向迁移可在完成主流程后作为拓展，不能替代正式验收。

## 二、实验目标

### 1. 知识目标

1. 说明Docker/OCI镜像、容器、Pod、Deployment和Service之间的关系。
2. 理解Kubernetes控制面、Node、Namespace和声明式期望状态的基本作用。
3. 区分Compose单主机编排和Kubernetes集群编排。
4. 理解就绪探针、存活探针、扩缩容、日志和滚动更新的基础意义。

### 2. 能力目标

1. 使用教师提供的kubeconfig安全连接集群。
2. 在个人命名空间应用和检查Deployment、Pod、Service。
3. 使用端口转发访问应用并查看日志。
4. 完成手动扩缩容并观察Pod变化。
5. 将Compose项目及全部镜像跨Rocky/Ubuntu迁移。
6. 完成综合故障排查、数据验证和交付归档。

### 3. 素质目标

1. 只在个人命名空间操作，不删除集群级资源和他人资源。
2. 不公开kubeconfig、Token、Registry凭据和应用密码。
3. 小组成果必须能通过个人操作和问答证明真实参与。

## 三、知识准备

### 1. 对象关系

```text
Deployment：声明应用镜像、副本数和Pod模板
      ↓ 创建和维持
ReplicaSet
      ↓ 创建和替换
Pod：Kubernetes最小可部署对象，内部运行一个或多个容器
      ↑ 被选择
Service：为一组标签匹配的Pod提供稳定访问入口
```

### 2. Compose与Kubernetes

| 维度 | Docker Compose | Kubernetes |
|---|---|---|
| 主要范围 | 单台Docker主机 | 多节点集群 |
| 基本应用单元 | Service对应的容器 | Pod及其控制器 |
| 副本维持 | 有限 | 控制器持续协调期望状态 |
| 服务发现 | Compose网络中的服务名 | Service与集群DNS |
| 更新 | 重新创建服务容器 | Deployment滚动更新 |
| 课程深度 | 完整部署与排障 | 基础体验，不搭建集群 |

### 3. 权限边界

教师应为每位学生或小组预建：

```text
Namespace：vc-<学号或组号>
Context：<K8S_CONTEXT>
权限：仅管理本命名空间常用工作负载和Service
镜像拉取：课程Registry已由集群配置访问
```

## 四、实验环境

- 教师提供Kubernetes API访问、kubeconfig和个人命名空间。
- 学生在Ubuntu或Rocky安装与集群版本兼容的`kubectl`客户端。
- 集群能够拉取教师课程应用镜像。
- 实验10的Compose项目、`.env.example`、数据备份和镜像均保留。
- `ubuntu-client`是正式主流程的源环境，`rocky-server`是目标环境；两台主机均保留实验6的Docker基线和Linux课程的SSH管理路径。
- 最终项目端口由教师统一分配，避免小组冲突。

## 五、项目任务

1. 安全连接Kubernetes集群并确认命名空间。
2. 阅读并应用Deployment和Service YAML。
3. 查看Pod、事件、日志、探针和Service。
4. 访问应用并完成扩缩容。
5. 清理个人Kubernetes资源。
6. 打包Compose项目和全部镜像。
7. 在另一发行版恢复并验证。
8. 完成随机故障、交付文档和个人答辩。

## 六、实验步骤

### 任务一：连接Kubernetes集群

#### 步骤1：准备kubectl和kubeconfig

按教师方式安装离线`kubectl`，验证：

```bash
kubectl version --client
```

教师提供个人kubeconfig后保存：

```bash
mkdir -p ~/.kube ~/vc-course/lab11/k8s ~/vc-course/evidence
```

```bash
source ~/vc-course/course-env.sh
[[ "$KUBECONFIG_SOURCE" != 'CHANGE_ME' && -r "$KUBECONFIG_SOURCE" ]]
```

```bash
source ~/vc-course/course-env.sh
install -m 600 "$KUBECONFIG_SOURCE" ~/.kube/config
```

不得输出或提交完整kubeconfig。

#### 步骤2：检查Context和权限

```bash
kubectl config current-context
```

```bash
kubectl config get-contexts
```

```bash
kubectl cluster-info
```

```bash
source ~/vc-course/course-env.sh
kubectl auth can-i get pods -n "$K8S_NAMESPACE"
```

```bash
kubectl auth can-i delete namespaces
```

预期：能够在个人命名空间查看Pod，但不应有删除Namespace等集群级权限。

#### 步骤3：固定当前命名空间

先确认教师分配值，再执行：

```bash
source ~/vc-course/course-env.sh
[[ "$K8S_CONTEXT" != 'CHANGE_ME' && "$K8S_NAMESPACE" != 'CHANGE_ME' ]]
```

```bash
source ~/vc-course/course-env.sh
kubectl config use-context "$K8S_CONTEXT"
```

```bash
source ~/vc-course/course-env.sh
kubectl config set-context --current --namespace="$K8S_NAMESPACE"
```

```bash
kubectl config view --minify --output 'jsonpath={..namespace}'
```

命令输出必须与教师分配的命名空间一致。如果输出为空或错误，不得继续部署。

后续命令仍建议在关键删除操作中显式写`-n "$K8S_NAMESPACE"`。

> **验收点**：Context正确、个人命名空间正确、权限没有越过课程边界。

### 任务二：阅读Kubernetes YAML

#### 步骤4：创建课程应用清单

先查看教师发布的固定镜像完整名称：

```bash
source ~/vc-course/course-env.sh
printf '%s\n' "$K8S_IMAGE"
```

输出不得为`CHANGE_ME`。执行`vim ~/vc-course/lab11/k8s/vc-api.yaml`，输入下列清单，并把`registry.example.invalid/vc/techcorp-api:course-fixed`替换为刚才显示的完整镜像名称：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vc-api
  labels:
    app: vc-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: vc-api
  template:
    metadata:
      labels:
        app: vc-api
    spec:
      containers:
        - name: api
          image: registry.example.invalid/vc/techcorp-api:course-fixed
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8080
          env:
            - name: APP_ENV
              value: kubernetes-lab
          readinessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 3
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
          resources:
            requests:
              cpu: 25m
              memory: 32Mi
            limits:
              cpu: 200m
              memory: 128Mi
---
apiVersion: v1
kind: Service
metadata:
  name: vc-api
spec:
  selector:
    app: vc-api
  ports:
    - name: http
      port: 80
      targetPort: http
  type: ClusterIP
```

这里采用手工编辑，是为了让学习者读懂Deployment和Service的层级、缩进及对应关系，不使用脚本代替这一过程。

#### 步骤5：检查清单对象

```bash
grep -E '^kind:|^  name:|image:|replicas:|path:|type:' ~/vc-course/lab11/k8s/vc-api.yaml
```

```bash
grep -n 'registry.example.invalid' ~/vc-course/lab11/k8s/vc-api.yaml
```

第二条命令应无输出。如果仍显示示例镜像，回到`vim`修改，不得带着占位值部署。

```bash
source ~/vc-course/course-env.sh
kubectl apply --dry-run=server -f ~/vc-course/lab11/k8s/vc-api.yaml -n "$K8S_NAMESPACE"
```

服务端dry-run通过后再实际应用。若学生权限不允许server dry-run，使用`--dry-run=client`并由教师统一验证。

### 任务三：部署和观察应用

#### 步骤6：应用YAML

```bash
source ~/vc-course/course-env.sh
kubectl apply -f ~/vc-course/lab11/k8s/vc-api.yaml -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl rollout status deployment/vc-api --timeout=120s -n "$K8S_NAMESPACE"
```

查看对象：

```bash
source ~/vc-course/course-env.sh
kubectl get deployment,replicaset,pod,service -o wide -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl get pods -l app=vc-api --show-labels -n "$K8S_NAMESPACE"
```

#### 步骤7：查看Deployment和Pod细节

```bash
source ~/vc-course/course-env.sh
kubectl describe deployment vc-api -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl describe pods -l app=vc-api -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl get events --sort-by=.metadata.creationTimestamp -n "$K8S_NAMESPACE" | tail -n 30
```

重点观察镜像、期望/可用副本、节点、Pod IP、探针、重启次数和事件。

#### 步骤8：查看日志

```bash
source ~/vc-course/course-env.sh
kubectl logs deployment/vc-api --tail=50 -n "$K8S_NAMESPACE"
```

如果有多个Pod，查看具体Pod：

```bash
source ~/vc-course/course-env.sh
kubectl get pods -l app=vc-api -n "$K8S_NAMESPACE"
```

为了体验查看某一个Pod的日志，下面保留一个小型Shell变量用法：先取得第一个匹配的Pod名称，再传给日志命令。它只服务于当前任务，不是批量脚本：

```bash
source ~/vc-course/course-env.sh
POD_NAME=$(kubectl get pods -l app=vc-api -n "$K8S_NAMESPACE" -o jsonpath='{.items[0].metadata.name}')
kubectl logs "$POD_NAME" --tail=50 -n "$K8S_NAMESPACE"
```

### 任务四：访问Service

#### 步骤9：检查Service与后端

```bash
source ~/vc-course/course-env.sh
kubectl get service vc-api -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl get endpointslice -l kubernetes.io/service-name=vc-api -n "$K8S_NAMESPACE"
```

Service的ClusterIP通常只在集群内部可达。使用端口转发建立本地体验通道：

```bash
source ~/vc-course/course-env.sh
kubectl port-forward service/vc-api 18080:80 -n "$K8S_NAMESPACE"
```

保持终端A运行，在终端B执行：

```bash
curl --fail http://127.0.0.1:18080/health
```

```bash
curl --fail http://127.0.0.1:18080/info
```

预期返回`API_HEALTH_OK`和`APP_ENV=kubernetes-lab`相关信息。按`Ctrl+C`结束端口转发。

> **验收点**：Deployment保持2个Ready Pod，Service选择到后端，端口转发访问成功，日志中出现请求。

### 任务五：扩缩容和自愈观察

#### 步骤10：扩容到3个副本

```bash
source ~/vc-course/course-env.sh
kubectl scale deployment/vc-api --replicas=3 -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl rollout status deployment/vc-api --timeout=120s -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl get pods -l app=vc-api -o wide -n "$K8S_NAMESPACE"
```

记录新增Pod和所在节点。

#### 步骤11：删除一个Pod观察恢复

先列出Pod，观察名称和创建时间：

```bash
source ~/vc-course/course-env.sh
kubectl get pods -l app=vc-api -o wide -n "$K8S_NAMESPACE"
```

为防止删错对象，将第一个匹配的Pod名称持久保存：

```bash
source ~/vc-course/course-env.sh
kubectl get pods -l app=vc-api -n "$K8S_NAMESPACE" -o jsonpath='{.items[0].metadata.name}' > ~/vc-course/evidence/lab11-selected-pod.txt
```

```bash
cat ~/vc-course/evidence/lab11-selected-pod.txt
```

确认输出不是空值，并且名称带有当前Deployment生成的`vc-api-`前缀。

执行删除前重新读取并验证对象，防止换终端后变量丢失或旧Pod名称已经失效：

```bash
source ~/vc-course/course-env.sh
POD_NAME=$(cat ~/vc-course/evidence/lab11-selected-pod.txt)
kubectl get pod "$POD_NAME" -n "$K8S_NAMESPACE" -o jsonpath='{.metadata.labels.app}'
```

只有上一条命令明确输出`vc-api`时才执行删除：

```bash
source ~/vc-course/course-env.sh
POD_NAME=$(cat ~/vc-course/evidence/lab11-selected-pod.txt)
kubectl delete pod "$POD_NAME" -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl get pods -l app=vc-api -w -n "$K8S_NAMESPACE"
```

看到旧Pod删除且新Pod创建后按`Ctrl+C`。Deployment期望副本仍为3。

#### 步骤12：缩容回2个副本

```bash
source ~/vc-course/course-env.sh
kubectl scale deployment/vc-api --replicas=2 -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl rollout status deployment/vc-api --timeout=120s -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl get deployment vc-api -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl get pods -l app=vc-api -n "$K8S_NAMESPACE"
```

把YAML中的`replicas`也保持为2，避免下次`apply`覆盖命令式扩缩容结果而产生理解偏差。

### 任务六：清理Kubernetes资源

#### 步骤13：保存证据

```bash
script -q ~/vc-course/evidence/lab11-k8s-result.txt
```

录制开始后逐条执行：

```bash
date -Is
```

```bash
kubectl config current-context
```

```bash
source ~/vc-course/course-env.sh
kubectl get deployment,replicaset,pod,service -o wide -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl describe deployment vc-api -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl get events --sort-by=.metadata.creationTimestamp -n "$K8S_NAMESPACE"
```

```bash
exit
```

检查文件不包含Token或证书内容。

#### 步骤14：按文件清理

确认当前命名空间：

```bash
kubectl config view --minify --output 'jsonpath={..namespace}'
```

执行：

```bash
source ~/vc-course/course-env.sh
kubectl delete -f ~/vc-course/lab11/k8s/vc-api.yaml -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl get all -n "$K8S_NAMESPACE"
```

不要执行删除整个命名空间或集群范围资源的命令。

### 任务七：制作Compose项目交付包

#### 步骤15：在源主机停止并检查项目

进入实验10目录：

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
curl --fail "http://$UBUNTU_CLIENT_IP:8088/health"
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$UBUNTU_CLIENT_IP:8088/api/info"
```

逻辑备份：

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env exec -T db \
  sh -c 'mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --databases "$MYSQL_DATABASE"' \
  > backup/vcdb-final.sql
```

```bash
cd ~/vc-course/lab10/techcorp-stack
test -s backup/vcdb-final.sql
```

#### 步骤16：导出全部课程镜像

获取Compose实际镜像清单：

```bash
cd ~/vc-course/lab10/techcorp-stack
sudo docker compose --env-file .env config --images | sort -u | tee evidence/compose-images.txt
```

建立独立交付目录。后续校验文件统一使用交付目录内的相对文件名，避免复制到目标主机后路径失效：

```bash
install -d -m 700 ~/vc-course/lab11/delivery
```

教师提供经过审核的明确导出命令。示例：

```bash
cd ~/vc-course/lab10/techcorp-stack
source ~/vc-course/course-env.sh
sudo docker save \
  -o ~/vc-course/lab11/delivery/vcstack-images.tar \
  "$COURSE_REGISTRY/vc/gateway:$COURSE_TAG" \
  "$COURSE_REGISTRY/vc/techcorp-api:$COURSE_TAG" \
  "$COURSE_REGISTRY/vc/mysql:$COURSE_TAG" \
  "$COURSE_REGISTRY/vc/redis:$COURSE_TAG"
```

```bash
sudo chown "$(id -u):$(id -g)" ~/vc-course/lab11/delivery/vcstack-images.tar
```

```bash
cd ~/vc-course/lab10/techcorp-stack
cp backup/vcdb-final.sql ~/vc-course/lab11/delivery/
```

#### 步骤17：打包项目配置

`.env`中的实际凭据不得进入公开交付包。复制可公开配置、镜像清单并生成项目归档：

```bash
cd ~/vc-course/lab10/techcorp-stack
test -s ~/vc-course/lab11/delivery/vcstack-images.tar
```

```bash
cd ~/vc-course/lab10/techcorp-stack
test -s ~/vc-course/lab11/delivery/vcdb-final.sql
```

```bash
cd ~/vc-course/lab10/techcorp-stack
cp compose.yaml .env.example .gitignore ~/vc-course/lab11/delivery/
```

```bash
cd ~/vc-course/lab10/techcorp-stack
cp evidence/compose-images.txt ~/vc-course/lab11/delivery/image-manifest.txt
```

```bash
cd ~/vc-course/lab10/techcorp-stack
tar -czf ~/vc-course/lab11/delivery/vcstack-project.tar.gz \
  compose.yaml .env.example .gitignore evidence/compose-images.txt
```

```bash
cd ~/vc-course/lab11/delivery
sha256sum vcstack-images.tar vcdb-final.sql vcstack-project.tar.gz compose.yaml .env.example .gitignore image-manifest.txt > SHA256SUMS
```

```bash
cd ~/vc-course/lab11/delivery
sha256sum -c SHA256SUMS
```

```bash
find ~/vc-course/lab11/delivery -maxdepth 1 -type f -printf '%f\n' | sort
```

交付清单必须说明`.env`或实际凭据由接收方安全提供，不包含在公开项目包中。此时`delivery`目录至少包含镜像归档、数据库备份、项目配置、镜像清单、项目归档和`SHA256SUMS`。

### 任务八：在目标发行版恢复

#### 步骤18：传输并校验

先在Ubuntu源主机确认交付目录存在且Rocky目标目录尚未被旧成果占用：

```bash
source ~/vc-course/course-env.sh
test -d ~/vc-course/lab11/delivery
```

```bash
ssh rocky-server \
  'mkdir -p ~/vc-course && test ! -e ~/vc-course/final-delivery && install -d -m 700 ~/vc-course/final-delivery'
```

```bash
scp -r ~/vc-course/lab11/delivery/. \
  rocky-server:~/vc-course/final-delivery/
```

```bash
ssh rocky-server \
  'test -s ~/vc-course/final-delivery/SHA256SUMS && test -s ~/vc-course/final-delivery/vcstack-images.tar'
```

`delivery/.`表示复制交付目录中的内容，而不是再套一层`delivery`目录。如果目标目录已存在，远程命令会在创建前停止；先登录Rocky检查并归档旧成果，不直接覆盖或删除。传输完成后，在Rocky目标主机执行：

```bash
cd ~/vc-course/final-delivery
sha256sum -c SHA256SUMS
```

```bash
cd ~/vc-course/final-delivery
sudo docker load -i vcstack-images.tar
```

```bash
sudo docker image ls --digests
```

复制`.env.example`为`.env`并填入教师实验值：

```bash
cd ~/vc-course/final-delivery
cp .env.example .env
```

```bash
ip -br -4 address show
```

根据网卡输出确认Rocky的固定IPv4地址。执行`vim ~/vc-course/final-delivery/.env`，把`VC_BIND_IP`和三个课堂密码项改为目标环境实际值。不使用批量替换脚本，让学习者逐项确认迁移配置。

```bash
cd ~/vc-course/final-delivery
chmod 600 .env
```

检查占位值：

```bash
cd ~/vc-course/final-delivery
grep -En '=(CHANGE_ME|replace_me)$|课程仓库|课程标签' .env
```

该命令应无输出；只要显示一行就不得启动。

#### 步骤19：在目标主机启动

```bash
cd ~/vc-course/final-delivery
sudo docker compose --env-file .env config --quiet
```

```bash
cd ~/vc-course/final-delivery
sudo docker compose --env-file .env up -d
```

```bash
cd ~/vc-course/final-delivery
sudo docker compose --env-file .env ps
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$ROCKY_SERVER_IP:8088/health"
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$ROCKY_SERVER_IP:8088/api/info"
```

如果需要恢复源数据库数据，在目标MySQL健康后执行：

```bash
cd ~/vc-course/final-delivery
sudo docker compose --env-file .env exec -T db \
  sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD"' \
  < vcdb-final.sql
```

```bash
source ~/vc-course/course-env.sh
curl --fail "http://$ROCKY_SERVER_IP:8088/api/info"
```

从另一台主机访问目标地址，形成外部功能证据。

> **验收点**：目标主机不访问Docker Hub也能导入全部镜像，Compose配置通过，四服务正常，数据库可恢复，客户端访问成功。

### 任务九：综合故障排查与答辩

#### 步骤20：教师随机注入故障

故障从以下层次抽取3—5项：

- Docker服务停止；
- 缺少一个镜像或标签错误；
- 8088端口冲突；
- Compose变量缺失；
- API不在后端网络；
- MySQL或Redis认证错误；
- 数据卷名称错误；
- 健康检查路径错误；
- 网关上游配置错误；
- 离线包SHA256不一致；
- Kubernetes镜像拉取失败、标签不匹配或Service selector错误。

学生必须按以下顺序记录：

```text
用户现象
→ 主机与Docker/Kubernetes状态
→ 容器或Pod状态
→ 端口、网络和Service
→ 配置与变量
→ 日志和事件
→ 数据卷或数据库
→ 根因
→ 最小修复
→ 原始客户端路径复测
```

#### 步骤21：个人答辩

每人随机完成至少一项操作并回答问题：

- 解释KVM虚拟机与Docker容器差异；
- 从课程Registry或离线包恢复镜像；
- 判断Compose服务所在网络；
- 证明MySQL数据位于卷；
- 查看容器健康和日志；
- 解释Deployment、Pod和Service关系；
- 在个人Namespace中完成扩缩容；
- 根据错误现象定位一项故障。

## 七、独立实践

每位学生在小组项目中选择一项个人负责人任务：

- 镜像与离线包负责人；
- Compose与网络负责人；
- 数据备份恢复负责人；
- Kubernetes体验与证据负责人；
- 故障排查与验证负责人。

负责人不代表其他成员可以完全不操作。答辩会从非本人主责区域抽取一道基础操作。

## 八、验收标准

### Kubernetes体验

- [ ] Context和Namespace正确，权限边界明确。
- [ ] YAML包含Deployment和Service并通过dry-run。
- [ ] 2个Pod Ready，Service具有后端EndpointSlice。
- [ ] 通过端口转发访问`/health`成功。
- [ ] 能查看Deployment、Pod、事件和日志。
- [ ] 完成扩容、自愈观察和缩容。
- [ ] 已清理个人应用资源，未删除Namespace和他人资源。

### 综合交付

- [ ] 源主机Compose项目功能正常并完成数据备份。
- [ ] 全部镜像进入离线归档，镜像清单完整。
- [ ] 镜像、数据库和项目包SHA256通过。
- [ ] 目标主机完成镜像导入和Compose部署。
- [ ] Rocky与Ubuntu至少完成一次跨发行版迁移。
- [ ] Web、API、MySQL、Redis状态和功能均有证据。
- [ ] 数据备份在目标环境完成恢复验证。
- [ ] 完成3—5项故障的证据化排查。
- [ ] 交付包不含密码、Token、私钥和kubeconfig。
- [ ] 每位成员完成个人操作和个人答辩。

## 九、成果提交

```text
lab11-组号/
├── README.md
├── architecture.png或.pdf
├── compose.yaml
├── .env.example
├── image-manifest.txt
├── SHA256SUMS
├── deployment-guide.md
├── backup-and-restore.md
├── k8s/
│   ├── vc-api.yaml
│   └── k8s-result.txt
├── faults/
│   ├── fault-01.md
│   ├── fault-02.md
│   └── fault-03.md
└── individual/
    ├── 学号1.md
    ├── 学号2.md
    └── 学号3.md
```

大文件镜像归档和数据库备份放教师指定存储，只在提交目录记录位置与SHA256。

## 十、常见问题

### 1. kubectl无法连接集群

```bash
kubectl config current-context
```

```bash
kubectl config view --minify
```

```bash
kubectl cluster-info
```

检查教师地址、网络、证书有效期和kubeconfig权限，不公开文件内容。

### 2. Pod为ImagePullBackOff

```bash
source ~/vc-course/course-env.sh
kubectl describe pods -l app=vc-api -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl get events --sort-by=.metadata.creationTimestamp -n "$K8S_NAMESPACE" | tail -n 30
```

检查镜像完整名称、固定标签、集群到课程Registry的网络和教师预置拉取凭据。

### 3. Pod Running但不Ready

查看探针和应用日志：

```bash
source ~/vc-course/course-env.sh
kubectl describe pods -l app=vc-api -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl logs deployment/vc-api --tail=100 -n "$K8S_NAMESPACE"
```

Running只说明容器进程存在，不代表应用通过就绪检查。

### 4. Service没有后端

```bash
source ~/vc-course/course-env.sh
kubectl get service vc-api -o yaml -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl get pods --show-labels -n "$K8S_NAMESPACE"
```

```bash
source ~/vc-course/course-env.sh
kubectl get endpointslice -l kubernetes.io/service-name=vc-api -n "$K8S_NAMESPACE"
```

重点比较Service selector与Pod label。

### 5. 目标主机Compose启动失败

先做离线清单和配置检查：

```bash
cd ~/vc-course/final-delivery
sha256sum -c SHA256SUMS
```

```bash
sudo docker image ls --digests
```

```bash
cd ~/vc-course/final-delivery
sudo docker compose --env-file .env config --quiet
```

```bash
cd ~/vc-course/final-delivery
sudo docker compose --env-file .env config --images
```

```bash
cd ~/vc-course/final-delivery
sudo docker compose --env-file .env ps -a
```

```bash
cd ~/vc-course/final-delivery
sudo docker compose --env-file .env logs --tail 100
```

不要在目标主机临时改用公网镜像掩盖交付包缺失。

### 6. 恢复数据库后数据不正确

核对备份SHA256、目标数据库名称、导入日志和API查询。保留源数据，不在唯一卷上反复清空。

## 十一、课后思考与拓展

1. Kubernetes为什么管理Pod而不是直接把单个Docker容器作为最高层对象？
2. 删除Pod后应用能够恢复，说明Deployment在做什么？
3. OpenStack和Kubernetes分别更接近管理哪一层资源？
4. 企业级项目运维课程可以在本项目上增加哪些监控、部署和CI/CD能力？
5. AI应用如果要部署到云环境，本课程提供了哪些基础？

## 十二、环境保留或清理

- Kubernetes个人应用资源按文件删除，保留YAML和证据。
- Compose项目、镜像、卷和交付包按教师要求保留到答辩结束。
- 答辩完成后，先备份再清理明确项目：

```bash
cd ~/vc-course/final-delivery
sudo docker compose --env-file .env down
```

- 默认不加`-v`，数据卷是否删除由教师统一决定。
- 分别为Rocky和Ubuntu创建最终快照`VC-FINAL-课程综合项目完成`。该快照是课程归档点，不替代实验10形成的`VC-V3`恢复起点。
