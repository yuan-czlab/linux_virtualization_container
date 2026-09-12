# 实验9：Dockerfile应用镜像构建与优化

> 所属模块：模块二 Docker容器化应用构建与交付
>
> 建议学时：6学时
>
> 实验方式：个人
>
> 对应教材：《模块二 Docker容器化应用构建与交付》第9章
>
> 知识前置：实验7—8中的镜像层、容器运行、网络和挂载；教材第9章
>
> 状态依赖：可用Docker环境和课程固定Python基础镜像；不依赖实验8的网络和数据卷继续存在
>
> 建议起点：`VC-V2`
>
> 项目成果：可重复构建的Python应用镜像、固定标签、构建记录和镜像检查结果

## 一、项目情境

TechCorp有一个使用Python标准库编写的健康检查API，需要在Rocky和Ubuntu中获得完全一致的运行结果。直接把源代码复制到服务器再安装环境容易产生差异。你需要编写Dockerfile，把运行时、代码、用户、端口、健康检查和启动命令固化成镜像，并通过构建缓存、`.dockerignore`和非root运行完成基础优化。

## 二、实验目标

### 1. 知识目标

1. 说明Dockerfile、构建上下文、镜像层、缓存和运行配置的关系。
2. 理解`FROM`、`WORKDIR`、`COPY`、`RUN`、`USER`、`EXPOSE`、`HEALTHCHECK`和`CMD`。
3. 区分构建时指令和容器运行时命令。
4. 说明固定基础镜像版本、非root用户和最小构建上下文的意义。

### 2. 能力目标

1. 编写无需公网依赖的Python HTTP应用。
2. 从课程基础镜像构建应用镜像。
3. 使用`.dockerignore`排除无关和敏感文件。
4. 检查镜像历史、配置、运行用户和健康状态。
5. 优化Dockerfile顺序并验证缓存。
6. 把镜像迁移到另一Linux发行版运行。

### 3. 素质目标

1. 不把密码、私钥和本地缓存加入镜像。
2. 不使用浮动`latest`基础镜像作为正式构建依据。
3. 构建完成后进行运行、健康、日志和身份多维验收。

## 三、知识准备

### 1. 构建过程

```text
Dockerfile + 构建上下文
        ↓ docker build
BuildKit逐条执行指令并复用缓存
        ↓
只读镜像层 + 默认运行配置
        ↓ docker run
容器可写层 + 运行时参数
```

### 2. 常用指令

| 指令 | 主要作用 | 本实验用途 |
|---|---|---|
| `FROM` | 指定基础镜像 | 使用课程Python基础镜像 |
| `WORKDIR` | 设置后续工作目录 | 固定为`/app` |
| `COPY` | 从构建上下文复制文件 | 复制应用代码 |
| `RUN` | 构建时执行命令并形成层 | 创建非root用户 |
| `USER` | 指定后续构建和运行用户 | 以appuser运行 |
| `EXPOSE` | 声明容器服务端口 | 声明8080，不自动发布 |
| `HEALTHCHECK` | 定义容器健康检查 | 请求本机`/health` |
| `CMD` | 默认启动命令 | 启动Python应用 |

### 3. 不依赖公网的设计

本实验应用只使用Python标准库，不执行`pip install`。基础镜像已经进入课程Registry和离线包，因此即使不能访问PyPI或Docker Hub，学生仍然能够完成构建。

## 四、实验环境

- 主要在Ubuntu Docker主机完成，Rocky用于跨发行版验证。
- 教师提供`<COURSE_REGISTRY>/vc/python-base:<COURSE_TAG>`。
- 基础镜像已经通过课程Registry拉取或离线导入。
- 两台主机Docker Buildx可用。
- 工作目录统一为`~/vc-course/lab09/course-api`。

## 五、项目任务

1. 创建Python健康检查API。
2. 创建`.dockerignore`和第一版Dockerfile。
3. 构建固定标签镜像并运行。
4. 检查健康状态、日志、端口和运行用户。
5. 修改构建上下文并观察缓存。
6. 完成基础安全和镜像结构优化。
7. 在Rocky导入并运行同一镜像。

## 六、实验步骤

### 任务一：建立项目目录

#### 步骤1：创建受控构建上下文

在Ubuntu执行：

```bash
mkdir -p ~/vc-course/lab09/course-api ~/vc-course/evidence ~/vc-course/offline
cd ~/vc-course/lab09/course-api
pwd
```

确认当前目录只用于本实验，避免把整个用户主目录作为构建上下文。

#### 步骤2：编写应用

创建`app.py`：

```bash
cat > app.py <<'PY'
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import platform
import socket
from datetime import datetime, timezone


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"status": "API_HEALTH_OK"})
            return
        if self.path == "/info":
            self.send_json(200, {
                "service": "course-api",
                "hostname": socket.gethostname(),
                "python": platform.python_version(),
                "environment": os.getenv("APP_ENV", "unknown"),
                "time": datetime.now(timezone.utc).isoformat(),
            })
            return
        self.send_json(404, {"status": "NOT_FOUND", "path": self.path})

    def log_message(self, fmt, *args):
        print(f"client={self.client_address[0]} path={self.path} " + fmt % args, flush=True)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8080), Handler)
    print("course-api listening on 0.0.0.0:8080", flush=True)
    server.serve_forever()
PY
```

先在宿主机做语法检查：

```bash
python3 -m py_compile app.py
```

#### 步骤3：创建项目说明和敏感文件样例

```bash
cat > README.md <<'EOF'
# Course API

Endpoints:
- /health
- /info
EOF

printf 'DO_NOT_COPY_THIS_TOKEN\n' > local-secret.txt
mkdir -p __pycache__ evidence
```

`local-secret.txt`故意模拟不能进入镜像的本地敏感文件。

### 任务二：控制构建上下文

#### 步骤4：创建.dockerignore

```bash
cat > .dockerignore <<'EOF'
.git
.gitignore
__pycache__/
*.pyc
local-secret.txt
evidence/
*.log
EOF
```

验证文件：

```bash
sed -n '1,120p' .dockerignore
```

### 任务三：编写第一版Dockerfile

#### 步骤5：创建Dockerfile

```bash
cat > Dockerfile <<'DOCKERFILE'
# syntax=docker/dockerfile:1
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

LABEL org.opencontainers.image.title="VC Course API" \
      org.opencontainers.image.description="Virtualization and container course lab image"

RUN useradd --system --uid 10001 --create-home appuser

WORKDIR /app
COPY --chown=appuser:appuser app.py README.md ./

USER 10001
EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2).read()"]

CMD ["python", "-u", "/app/app.py"]
DOCKERFILE
```

`BASE_IMAGE`由构建命令明确传入，避免Dockerfile偷偷回退到公网镜像。

#### 步骤6：检查Dockerfile和上下文

```bash
sed -n '1,200p' Dockerfile
find . -maxdepth 2 -type f -printf '%P\n' | sort
sudo docker image inspect \
  <COURSE_REGISTRY>/vc/python-base:<COURSE_TAG> \
  --format 'id={{.Id}} arch={{.Architecture}}'
```

### 任务四：构建并运行镜像

#### 步骤7：第一次构建

```bash
sudo docker build \
  --build-arg BASE_IMAGE=<COURSE_REGISTRY>/vc/python-base:<COURSE_TAG> \
  --tag vc-course-api:v1 \
  --progress=plain \
  . | tee ~/vc-course/evidence/lab09-build-v1.log
```

如果使用`sudo`导致`tee`生成的日志所有者异常，构建后检查并调整个人文件所有者。构建成功应出现镜像标签`vc-course-api:v1`。

#### 步骤8：检查镜像

```bash
sudo docker image ls vc-course-api
sudo docker image inspect vc-course-api:v1 \
  --format 'id={{.Id}} user={{.Config.User}} workdir={{.Config.WorkingDir}} ports={{json .Config.ExposedPorts}} health={{json .Config.Healthcheck}}'
sudo docker history vc-course-api:v1
```

运行用户应为`10001`，工作目录为`/app`，暴露端口为8080。

#### 步骤9：确认敏感文件未进入镜像

```bash
sudo docker run --rm vc-course-api:v1 \
  sh -c 'test ! -e /app/local-secret.txt && echo SECRET_EXCLUDED'
```

预期返回`SECRET_EXCLUDED`。

#### 步骤10：运行应用

```bash
sudo docker run -d \
  --name vc-api-built \
  -p 8083:8080 \
  -e APP_ENV=lab09 \
  vc-course-api:v1
sudo docker container ls --filter name=vc-api-built
curl --fail http://127.0.0.1:8083/health
curl --fail http://127.0.0.1:8083/info
```

#### 步骤11：检查健康、身份和日志

```bash
sudo docker inspect vc-api-built \
  --format 'status={{.State.Status}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}'
sudo docker exec vc-api-built id
sudo docker exec vc-api-built ps
sudo docker logs --tail 30 vc-api-built
```

等待健康状态变为`healthy`。`id`应显示UID 10001而不是root。

从Rocky或另一客户端访问Ubuntu：

```bash
curl --fail http://<UBUNTU_IP>:8083/health
```

> **验收点**：API返回`API_HEALTH_OK`，容器为healthy，进程以非root用户运行，日志出现请求。

### 任务五：观察构建缓存

#### 步骤12：不修改内容再次构建

```bash
sudo docker build \
  --build-arg BASE_IMAGE=<COURSE_REGISTRY>/vc/python-base:<COURSE_TAG> \
  --tag vc-course-api:v1-cache \
  --progress=plain \
  . | tee ~/vc-course/evidence/lab09-build-cache.log
```

观察哪些步骤显示缓存命中。

#### 步骤13：只修改README重新构建

```bash
printf '\nBuild time: %s\n' "$(date -Is)" >> README.md
sudo docker build \
  --build-arg BASE_IMAGE=<COURSE_REGISTRY>/vc/python-base:<COURSE_TAG> \
  --tag vc-course-api:v2 \
  --progress=plain \
  . | tee ~/vc-course/evidence/lab09-build-v2.log
```

因为`app.py`和`README.md`在同一个`COPY`指令中，修改README会使该层及后续层失去缓存。记录构建日志中的差异。

#### 步骤14：优化复制顺序

把Dockerfile中的单个COPY修改为：

```dockerfile
COPY --chown=appuser:appuser README.md ./
COPY --chown=appuser:appuser app.py ./
```

讨论：如果频繁变化的是`app.py`，稳定文件和变化文件怎样排序能提高缓存利用率。重新构建：

```bash
sudo docker build \
  --build-arg BASE_IMAGE=<COURSE_REGISTRY>/vc/python-base:<COURSE_TAG> \
  --tag vc-course-api:v2-optimized \
  --progress=plain \
  . | tee ~/vc-course/evidence/lab09-build-optimized.log
```

### 任务六：增加运行时限制验证

#### 步骤15：只读根文件系统运行

先删除旧测试容器：

```bash
sudo docker stop vc-api-built
sudo docker rm vc-api-built
```

使用只读根文件系统和临时目录启动：

```bash
sudo docker run -d \
  --name vc-api-built \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m \
  --memory 256m \
  --cpus 0.50 \
  -p 8083:8080 \
  -e APP_ENV=lab09-locked \
  vc-course-api:v2-optimized
```

验证：

```bash
curl --fail http://127.0.0.1:8083/health
sudo docker inspect vc-api-built \
  --format 'readonly={{.HostConfig.ReadonlyRootfs}} memory={{.HostConfig.Memory}} nano_cpus={{.HostConfig.NanoCpus}}'
sudo docker stats --no-stream vc-api-built
```

这不是完整容器安全方案，但能让学生理解镜像和运行参数共同决定最终环境。

### 任务七：跨发行版验证

#### 步骤16：导出应用镜像

在Ubuntu：

```bash
sudo docker save \
  -o ~/vc-course/offline/vc-course-api-v2-optimized.tar \
  vc-course-api:v2-optimized
sudo chown "$(id -u):$(id -g)" \
  ~/vc-course/offline/vc-course-api-v2-optimized.tar
sha256sum ~/vc-course/offline/vc-course-api-v2-optimized.tar \
  | tee ~/vc-course/offline/vc-course-api-SHA256SUMS
```

复制到Rocky并校验后：

```bash
sudo docker load -i ~/vc-course/offline/vc-course-api-v2-optimized.tar
sudo docker run -d \
  --name vc-api-rocky \
  -p 8083:8080 \
  -e APP_ENV=rocky-verify \
  vc-course-api:v2-optimized
curl --fail http://127.0.0.1:8083/health
sudo docker exec vc-api-rocky id
sudo docker inspect vc-api-rocky \
  --format 'image={{.Image}} status={{.State.Status}}'
```

对比Ubuntu与Rocky的镜像ID和API响应。

### 任务八：保存成果

#### 步骤17：生成构建清单

在项目目录：

```bash
{
  date -Is
  sha256sum Dockerfile .dockerignore app.py README.md
  sudo docker image ls vc-course-api
  sudo docker image inspect vc-course-api:v2-optimized \
    --format 'id={{.Id}} user={{.Config.User}} health={{json .Config.Healthcheck}}'
} > ~/vc-course/evidence/lab09-result.txt
```

## 七、独立实践

在不复制最终Dockerfile的情况下，为应用增加`/version`接口，并构建`vc-course-api:v3`。要求：

- 返回学生自定义课程版本；
- 保持非root运行；
- 保持健康检查；
- `local-secret.txt`仍不在镜像中；
- 在Rocky或Ubuntu运行并验证；
- 说明哪些构建层使用了缓存。

## 八、验收标准

- [ ] 项目目录与构建上下文范围正确。
- [ ] Python语法检查通过。
- [ ] `.dockerignore`排除缓存、日志和敏感文件。
- [ ] Dockerfile使用课程固定基础镜像。
- [ ] 镜像成功构建并具有固定课程标签。
- [ ] 容器能够返回`API_HEALTH_OK`和`/info`数据。
- [ ] 健康状态为healthy，进程以UID 10001运行。
- [ ] `local-secret.txt`不在镜像中。
- [ ] 已通过构建日志解释缓存命中和失效。
- [ ] 只读根文件系统和资源限制下应用仍可运行。
- [ ] 镜像归档校验通过，并在另一发行版运行成功。

## 九、成果提交

```text
lab09-学号-姓名/
├── app.py
├── Dockerfile
├── .dockerignore
├── README.md
├── lab09-build-v1.log
├── lab09-build-cache.log
├── lab09-build-optimized.log
├── lab09-result.txt
├── vc-course-api-SHA256SUMS
└── optimization-report.md
```

镜像tar上传到教师指定的大文件位置，不进入普通Git仓库。

## 十、常见问题

### 1. 基础镜像无法获取

确认Dockerfile的`BASE_IMAGE`来自课程Registry，或已经使用教师离线包导入。不要把`FROM`临时改成不可控的公网`latest`。

### 2. Dockerfile解析错误

检查指令拼写、续行反斜杠、引号和构建参数。使用：

```bash
sed -n '1,200p' Dockerfile
sudo docker build --progress=plain .
```

错误通常会指出Dockerfile行号。

### 3. 容器启动后立即退出

```bash
sudo docker container ls -a --filter name=vc-api-built
sudo docker logs vc-api-built
sudo docker inspect vc-api-built --format '{{json .State}}'
```

前台主进程退出后容器随之停止。

### 4. 健康状态一直为starting或unhealthy

先直接请求应用，再查看健康检查日志：

```bash
curl -v http://127.0.0.1:8083/health
sudo docker inspect vc-api-built \
  --format '{{json .State.Health}}'
```

检查路径、端口、启动时间和基础镜像中Python是否可用。

### 5. Rocky运行时出现端口或SELinux问题

本实验应用不使用主机绑定挂载，因此优先检查端口占用、Docker状态和主机访问路径。不能通过关闭SELinux判断所有Docker故障。

## 十一、课后思考与拓展

1. 为什么`EXPOSE 8080`不会自动让宿主机8080可以访问？
2. 为什么健康检查应访问应用功能，而不只检查进程存在？
3. 固定基础镜像摘要和及时获得安全更新之间如何权衡？
4. Kubernetes中的镜像、容器、健康探针如何延续本实验设计？

## 十二、环境保留或清理

- 保留`vc-course-api:v2-optimized`和学生独立实践镜像。
- 保留项目源代码、Dockerfile和镜像归档。
- 停止并删除临时容器，释放8083：

```bash
sudo docker stop vc-api-built vc-api-rocky 2>/dev/null || true
sudo docker rm vc-api-built vc-api-rocky 2>/dev/null || true
```

- 不删除基础镜像，实验10继续使用。

