# Lab62：Kubernetes应用操作体验

> 课时：2 | 类型：2-3人小组 | 前置：Lab61 | 环境：教师提供可用集群和kubeconfig

## 一、你会学到什么

- 能识别Cluster、Node、Pod、Deployment和Service的最小关系
- 能使用kubectl查看、创建、修改和删除应用对象
- 能通过logs、describe和exec获取排障证据
- 能体验副本、自愈和滚动更新
- 能明确本课程只要求“会操作”，集群原理与完整平台留到《云计算应用》

## 二、实验边界与环境

本实验不安装Kubernetes集群，不讲CNI、CSI、调度、Helm和高可用。教师提前完成：

- 提供可访问的教学集群或每组独立namespace
- 将课程所需Nginx镜像预拉取到节点或配置可用镜像仓库
- 提供受限kubeconfig，不使用集群管理员凭据

学生确认：

```bash
kubectl version --client
kubectl cluster-info
kubectl get nodes
kubectl config current-context
```

> **验收点**：能够连接集群，并说明当前context和namespace。

## 三、对象关系

```text
Deployment（声明期望副本和版本）
    └── ReplicaSet（维护副本数量）
          └── Pod（运行一个或多个容器）

Service（为一组Pod提供稳定访问入口）
```

先回答：Pod被删除后，谁负责创建新Pod？Service如何找到新Pod？

## 四、实验步骤

### 步骤1：创建独立namespace

```bash
export NS=group01
kubectl create namespace "$NS"
kubectl config set-context --current --namespace="$NS"
kubectl get namespace "$NS"
```

班级共用集群时，namespace名称必须按教师分配，不能使用其他小组名称。

### 步骤2：使用YAML部署应用

```bash
cat > course-web.yaml <<'YAML'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: course-web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: course-web
  template:
    metadata:
      labels:
        app: course-web
    spec:
      containers:
        - name: nginx
          image: nginx:1.25-alpine
          ports:
            - containerPort: 80
          resources:
            requests:
              cpu: 50m
              memory: 32Mi
            limits:
              cpu: 200m
              memory: 128Mi
---
apiVersion: v1
kind: Service
metadata:
  name: course-web
spec:
  selector:
    app: course-web
  ports:
    - port: 80
      targetPort: 80
  type: ClusterIP
YAML

kubectl apply -f course-web.yaml
kubectl get deployment,replicaset,pod,service -o wide
kubectl rollout status deployment/course-web
```

> **验收点**：Deployment READY为2/2，Service存在，两个Pod为Running/Ready。

### 步骤3：查看对象和事件

```bash
kubectl describe deployment course-web
kubectl describe pod -l app=course-web
kubectl get events --sort-by=.lastTimestamp | tail -20
```

记录：镜像、节点、Pod IP、重启次数、最近事件。

### 步骤4：日志、容器内命令和访问测试

```bash
POD=$(kubectl get pod -l app=course-web -o jsonpath='{.items[0].metadata.name}')
kubectl logs "$POD"
kubectl exec "$POD" -- nginx -v
kubectl exec "$POD" -- cat /etc/os-release

# 临时创建测试Pod，从集群内部访问Service
kubectl run curl-test --rm -it --restart=Never \
  --image=curlimages/curl:8.5.0 -- curl -I http://course-web
```

如果测试镜像不可用，教师可预置或改用集群已有工具Pod。

### 步骤5：体验副本和自愈

```bash
kubectl scale deployment course-web --replicas=3
kubectl get pods -l app=course-web -w
```

另一个终端删除一个Pod：

```bash
POD=$(kubectl get pod -l app=course-web -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod "$POD"
kubectl get pod -l app=course-web -w
```

记录旧Pod名称、新Pod名称和恢复时间。

> **验收点**：能够说明“删除Pod后自动恢复”来自Deployment声明的期望副本，而不是Pod自身复活。

### 步骤6：滚动更新与回退

```bash
kubectl set image deployment/course-web nginx=nginx:1.27-alpine
kubectl rollout status deployment/course-web
kubectl rollout history deployment/course-web
kubectl get pods -l app=course-web -o wide
```

若新镜像不可用，观察：

```bash
kubectl get pods
kubectl describe pod 新Pod名称
kubectl rollout undo deployment/course-web
kubectl rollout status deployment/course-web
```

### 步骤7：基础故障排查

教师从以下场景选择一个：

- image标签不存在，出现ImagePullBackOff
- Service selector写错，Service没有Endpoints
- 容器端口或Service targetPort写错
- YAML缩进或字段错误

排障顺序：

```bash
kubectl get all
kubectl describe deployment course-web
kubectl describe pod Pod名称
kubectl logs Pod名称
kubectl get service,endpoints
kubectl get events --sort-by=.lastTimestamp
```

提交“现象→对象状态→事件/日志→根因→修复→验证”。

## 五、验收标准

- [ ] 能用YAML创建Deployment和Service
- [ ] 能使用get/describe/logs/exec获取信息
- [ ] 完成扩容、删除Pod自愈和滚动更新/回退
- [ ] 能定位一个镜像、标签、端口或YAML故障
- [ ] 能说明本课程K8s教学边界

## 六、清理环境

```bash
kubectl delete -f course-web.yaml
kubectl config set-context --current --namespace=default
kubectl delete namespace "$NS"
rm -f course-web.yaml
```

## 七、课后思考

1. Docker Compose的service与Kubernetes Deployment/Service分别有什么相似和不同？
2. Deployment有3个Pod时，Service如何把请求转发到这些Pod？这个问题将在《云计算应用》中继续学习。

