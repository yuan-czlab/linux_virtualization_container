# Lab57：编写 Dockerfile 构建自定义镜像

> 课时：2 | 类型：个人 | 前置：Lab52

## 一、你会学到什么
- 能编写包含 FROM/COPY/RUN/CMD/WORKDIR 的基础 Dockerfile
- 能用 docker build 构建镜像
- 理解构建上下文和层缓存机制
- 能区分 CMD 和 ENTRYPOINT

## 二、实验步骤

### 步骤1：第一个 Dockerfile——自定义 Nginx

```bash
mkdir -p /tmp/dockerfile-lab && cd /tmp/dockerfile-lab

# 创建 Dockerfile
cat > Dockerfile << 'EOF'
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

# 创建网站文件
cat > index.html << 'HTML'
<!DOCTYPE html>
<html><body>
<h1>🚀 My First Docker Image</h1>
<p>Built from Dockerfile at <span id="time"></span></p>
<script>document.getElementById('time').textContent=new Date()</script>
</body></html>
HTML

# 构建镜像
docker build -t my-web:v1 .
# -t my-web:v1    名称:标签
# .               构建上下文路径（当前目录）
```

**构建输出解读**：
```
[+] Building 1.5s
 => [1/2] FROM nginx:alpine             0.0s  (缓存命中)
 => [2/2] COPY index.html ...           0.2s
 => exporting to image                  0.3s
```

### 步骤2：运行并验证

```bash
docker run -d --name my-web -p 8086:80 my-web:v1
curl http://localhost:8086
# 🚀 My First Docker Image ✓
docker rm -f my-web
```

### 步骤3：理解层缓存

```bash
# 第二次构建（什么都不改）→ 全部缓存命中
docker build -t my-web:v1 .
# => CACHED [1/2] FROM nginx:alpine
# => CACHED [2/2] COPY index.html ...
# 秒级完成！

# 修改 index.html → COPY 层失效 → 只用 FROM 层缓存
echo "<!-- updated -->" >> index.html
docker build -t my-web:v2 .
# => CACHED [1/2] FROM nginx:alpine      ← 缓存命中
# => [2/2] COPY index.html ...           ← 重新执行
```

**层缓存规则**：某层变化后，它之后的所有层都失效。所以**把变化频率低的指令放前面**。

### 步骤4：Dockerfile 核心指令详解

```dockerfile
FROM python:3.12-slim        # 基础镜像（必须第一条）
WORKDIR /app                 # 工作目录（不存在则自动创建）
COPY requirements.txt .      # 复制文件（推荐 COPY 而非 ADD）
RUN pip install --no-cache-dir -r requirements.txt   # 构建时运行
COPY app.py .                # 先 COPY 依赖 → 利用缓存
ENV FLASK_APP=app.py         # 环境变量
EXPOSE 5000                  # 声明端口（文档作用，不实际开放）
USER 1000                    # 以非 root 运行（安全）
CMD ["python", "app.py"]     # 启动默认命令
```

**最佳实践**：
- `COPY` 优先于 `ADD`（ADD 行为不透明：自动解压 tar、支持 URL）
- `RUN` 用 `&&` 串联命令减少层数：`RUN apt update && apt install -y pkg && rm -rf /var/lib/apt/lists/*`
- 先 COPY 依赖文件，再 COPY 源码（利用缓存加速构建）

### 步骤5：CMD vs ENTRYPOINT

```bash
# CMD：默认命令，可以被 docker run 后面的命令覆盖
docker run my-web:v1 echo "override"
# 执行 echo 而不是 nginx

# ENTRYPOINT：固定入口命令，CMD 作为默认参数
# ENTRYPOINT ["nginx"]
# CMD ["-g", "daemon off;"]
# docker run my-web:v1 -t  → 实际执行：nginx -t
# CMD 被替换但 ENTRYPOINT 不变
```

### 步骤6：.dockerignore

```bash
cat > .dockerignore << 'EOF'
.git
*.log
.env
*.md
node_modules/
__pycache__/
*.pyc
EOF

# 好处：
# 1. 减小构建上下文大小
# 2. 防止密码/密钥/日志被意外打入镜像
# 3. 加速构建
```

### 步骤7：容器化一个 Python 应用

```bash
mkdir -p /tmp/flask-docker && cd /tmp/flask-docker

cat > app.py << 'PYEOF'
from flask import Flask, jsonify
import datetime, os
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Flask in Docker</h1>'

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'time': str(datetime.datetime.now()),
        'hostname': os.uname().nodename
    })
PYEOF

cat > requirements.txt << 'EOF'
flask==3.0.0
EOF

cat > Dockerfile << 'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
USER 1000
CMD ["python", "app.py"]
EOF

docker build -t flask-api:v1 .
docker run -d --name flask1 -p 5000:5000 flask-api:v1
curl http://localhost:5000/health
# {"hostname":"xxx","status":"ok","time":"..."}
```

---

## 五、练习题

### 练习1：Dockerfile 指令填空（15分）

| 指令 | 作用 | 示例 |
|------|------|------|
| FROM | | |
| COPY | | |
| RUN | | |
| CMD | | |
| WORKDIR | | |
| ENV | | |
| EXPOSE | | |
| USER | | |

### 练习2：修复 Dockerfile 问题（20分）

以下 Dockerfile 有什么问题？写出修正版：

```dockerfile
FROM python:3.12
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD python app.py
```

### 练习3：镜像大小优化（25分）

1. 用 `docker images` 对比 `python:3.12`、`python:3.12-slim`、`python:3.12-alpine` 的大小
2. 用三个不同的基础镜像构建同一个 Flask 应用
3. 记录各镜像的最终大小
4. 总结镜像优化策略

### 练习4：层缓存利用（20分）

1. 构建一次镜像并计时
2. 修改 app.py → 再构建 → 计时
3. 修改 requirements.txt → 再构建 → 计时
4. 为什么修改 requirements.txt 比修改 app.py 构建更慢？

### 练习5：多阶段构建（20分）

研究多阶段构建（multi-stage build）：
1. 构建阶段做什么？
2. 运行阶段做什么？
3. 写一个两阶段的 Dockerfile（编译阶段 + 运行阶段）
4. 对比单阶段和多阶段的镜像大小

## 七、常见问题

**Q: COPY 和 ADD 有什么区别？什么时候用哪个？**
A: COPY 只做复制（简单直接，推荐）。ADD 有额外功能（自动解压 tar、支持 URL），但行为不透明。优先用 COPY，只有当确实需要 ADD 的额外功能时才用。

**Q: CMD 和 ENTRYPOINT 怎么配合使用？**
A: ENTRYPOINT 定义固定入口（如 `["nginx"]`），CMD 定义默认参数（如 `["-g", "daemon off;"]`）。`docker run 镜像 -t` 会用 `-t` 替换 CMD 的默认参数，但 ENTRYPOINT 不变→实际执行 `nginx -t`。

**Q: 构建时层缓存没生效？**
A: 某层指令或它 COPY 的文件发生变化，该层及之后所有层缓存失效。把变化少的指令（FROM、RUN install）放前面，变化多的（COPY 源码）放后面。

## 八、课后思考

1. Docker 构建时的层缓存和 Linux 的 Page Cache、Git 的 object store 都体现了"缓存不可变数据"的思想。这在计算机科学中叫什么原则？

2. 如果 Dockerfile 中某一步 RUN 命令失败了（如 `pip install` 网络超时），构建会停在那一层。如何利用这个"残骸"调试？（提示：docker run 最后成功构建的层 ID）
