# Lab58：Dockerfile 实战——镜像优化与多阶段构建

> 课时：2 | 类型：个人 | 前置：Lab57

## 一、你会学到什么
- 能用多阶段构建优化镜像体积
- 能应用镜像安全最佳实践
- 能对比不同基础镜像的大小差异
- 能用 .dockerignore 加速构建

## 二、实验步骤

### 步骤1：三种基础镜像对比

```bash
mkdir -p /tmp/dockerfile-optimize && cd /tmp/dockerfile-optimize

cat > app.py << 'EOF'
from flask import Flask
app = Flask(__name__)
@app.route('/')
def home():
    return '<h1>Flask App</h1>'
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF

cat > requirements.txt << 'EOF'
flask==3.0.0
EOF
```

**方案A：完整版（python:3.12）**

```dockerfile
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

```bash
docker build -t flask-full:v1 -f Dockerfile.full .
docker images flask-full:v1
# ~1GB
```

**方案B：slim 版（python:3.12-slim）**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
USER 1000
CMD ["python", "app.py"]
```

```bash
docker build -t flask-slim:v2 -f Dockerfile.slim .
docker images flask-slim:v2
# ~150MB
```

**方案C：Alpine 版（python:3.12-alpine）**

```dockerfile
FROM python:3.12-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
USER 1000
CMD ["python", "app.py"]
```

```bash
docker build -t flask-alpine:v3 -f Dockerfile.alpine .
docker images flask-alpine:v3
# ~80MB
```

**对比**：

```bash
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep flask
# flask-full    v1    1.02GB
# flask-slim    v2    152MB
# flask-alpine  v3    78MB
```

### 步骤2：多阶段构建

```dockerfile
# ===== 阶段1：构建阶段 =====
FROM python:3.12-alpine AS builder
WORKDIR /app
COPY requirements.txt .
# 安装依赖到 /root/.local（非系统路径）
RUN pip install --user --no-cache-dir -r requirements.txt

# ===== 阶段2：运行阶段 =====
FROM python:3.12-alpine
WORKDIR /app
# 只从构建阶段拷贝已安装的依赖
COPY --from=builder /root/.local /root/.local
COPY app.py .
# 让 Python 能找到 /root/.local 下的包
ENV PATH=/root/.local/bin:$PATH
EXPOSE 5000
USER 1000
CMD ["python", "app.py"]
```

```bash
docker build -t flask-multistage:v4 -f Dockerfile.multistage .
docker images | grep flask-multistage
# ~75MB（比单阶段 alpine 更小，因为连 pip 都没有）
```

**多阶段构建的好处**：
1. 最终镜像不包含构建工具（编译器、pip、git 等）
2. 最终镜像不包含中间文件
3. 显著减小镜像体积

### 步骤3：.dockerignore

```bash
cat > .dockerignore << 'EOF'
# Python
__pycache__/
*.pyc
*.pyo
venv/
.env

# Git
.git/
.gitignore

# IDE
.vscode/
.idea/

# 文档
*.md
README*

# 测试
tests/
*.test.py

# Docker
Dockerfile*
docker-compose*
.dockerignore

# 日志
*.log
logs/

# 临时文件
*.tmp
*.swp
EOF

# 对比构建上下文大小
# 没有 .dockerignore 时：可能几百 MB（包含 venv/ 和 .git/）
# 有 .dockerignore 时：只有几 MB
```

### 步骤4：镜像安全最佳实践

```dockerfile
# 安全 Dockerfile 模板
FROM python:3.12-slim

# 1. 固定基础镜像版本（不用 latest）
# FROM python:3.12-slim@sha256:abc123...

# 2. 创建非 root 用户
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# 3. 先 COPY 依赖文件（利用缓存）
COPY requirements.txt .

# 4. 不缓存安装包
RUN pip install --no-cache-dir -r requirements.txt

# 5. COPY 源码
COPY app.py .

# 6. 修改文件所有权
RUN chown -R appuser:appuser /app

# 7. 切换到非 root 用户
USER appuser

EXPOSE 5000

# 8. 使用 exec 形式的 CMD
CMD ["python", "app.py"]
```

### 步骤5：优化效果对比

| 优化手段 | 效果 |
|---------|------|
| alpine 基础镜像 | 1GB → 80MB |
| 多阶段构建 | 80MB → 75MB |
| --no-cache-dir | 节省 ~10MB |
| .dockerignore | 加速构建（上下文变小） |
| USER 非 root | 安全提升 |

---

## 五、练习题

### 练习1：镜像优化策略总结（15分）

写出 5 种 Docker 镜像优化手段，按优先级排序。

### 练习2：多阶段构建实战（25分）

为一个 Go 应用（或任意编译型语言）写两阶段 Dockerfile：
- 阶段1：编译源码（需要 Go 编译器和依赖）
- 阶段2：只包含编译好的二进制文件（不需要 Go）

### 练习3：镜像大小分析（20分）

1. 用 `docker history` 查看 flask-alpine:v3 各层的大小
2. 找出最大的 3 层
3. 有没有可以进一步优化的层？

### 练习4：.dockerignore 优化（15分）

1. 构建一次镜像，记录构建时间
2. 添加完整的 .dockerignore
3. 再构建一次，对比构建时间

### 练习5：安全审计（25分）

审查以下 Dockerfile 的安全问题，写出修正版：

```dockerfile
FROM python:latest
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENV DB_PASSWORD=super_secret_123
CMD python app.py
```

## 七、常见问题

**Q: 多阶段构建和单阶段构建的本质区别？**
A: 单阶段：构建环境和运行环境在同一个镜像里（包含编译器、构建工具、中间文件）。多阶段：构建环境在阶段1，只把产物（二进制/依赖）复制到阶段2的运行镜像。最终镜像更小更安全。

**Q: 如何选择基础镜像？alpine vs slim vs full？**
A: alpine（~5MB，极致小巧，用 musl libc）适合简单应用，slim（~80MB，精简 Debian）适合大多数 Python/Node 应用，full（~1GB）适合需要编译或调试的场景。生产优先 alpine > slim > full。

**Q: .dockerignore 和 .gitignore 有什么区别？**
A: 作用类似（排除不需要的文件），但目标不同。.gitignore 排除不该进版本控制的文件，.dockerignore 排除不该进镜像的文件（如 node_modules、.git、日志），减小构建上下文。

## 八、课后思考

1. 镜像优化到极致就是"distroless 镜像"（连 shell 都没有）。如果容器连 shell 都没有，你怎么进去调试？（提示：docker debug、ephemeral containers、kubectl debug）

2. Docker 镜像的安全扫描（如 docker scout、trivy）可以发现镜像中的已知漏洞。作为运维，你应该在 CI/CD 的哪个环节做安全扫描？
