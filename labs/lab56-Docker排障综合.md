# Lab56：Docker 常见故障排查

> 课时：2 | 类型：个人 | 前置：Lab55

## 一、你会学到什么
- 掌握 Docker 故障排查的标准流程
- 能根据错误日志定位根因
- 能解决端口冲突、权限、网络、启动失败等常见问题

## 二、排障核心流程

```
容器出问题 → docker ps -a（看状态）→ docker logs（看日志）
           → docker inspect（看配置）→ 定位根因 → 修复
```

## 三、实验步骤

### 故障1：端口冲突

```bash
# 制造冲突
docker run -d --name web1 -p 80:80 nginx:alpine
docker run -d --name web2 -p 80:80 nginx:alpine
# Error: Bind for 0.0.0.0:80 failed: port is already allocated

# 排查步骤：
# 1. 查看谁占用了 80 端口
ss -tlnp | grep :80
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep :80

# 2. 解决方案：换端口或停掉冲突容器
docker rm -f web1 web2
```

### 故障2：容器启动后立即退出

```bash
# 场景A：默认命令需要交互
docker run --name bad-alpine alpine
docker ps -a | grep bad-alpine
# STATUS: Exited (0) ← 启动了但马上就退出了

docker logs bad-alpine
# 没有日志输出

# 根因：alpine 镜像默认 CMD 是 sh，没有 -it 就退出了
# 修复：
docker rm bad-alpine
docker run -d --name good-alpine alpine sleep 3600

# 场景B：应用程序启动失败
docker run -d --name bad-app alpine sh -c "exit 1"
docker ps -a | grep bad-app
# STATUS: Exited (1) ← 退出码 1 表示异常

docker logs bad-app           # 查看退出原因
docker inspect bad-app | grep -A5 '"State"'
# "ExitCode": 1

docker rm bad-app good-alpine
```

### 故障3：镜像拉取失败

```bash
# 场景A：镜像不存在
docker pull nonexistent-image:v99
# Error: manifest for nonexistent-image:v99 not found

# 场景B：网络问题
# docker pull nginx
# Error: Get https://registry-1.docker.io/v2/: dial tcp: i/o timeout

# 排查步骤：
# 1. ping registry-1.docker.io 是否能通
# 2. 检查是否需要配置镜像加速器
# 3. 检查 DNS 配置

# 国内常用镜像加速器配置：
# sudo tee /etc/docker/daemon.json << 'EOF'
# {
#   "registry-mirrors": ["https://mirror.ccs.tencentyun.com"]
# }
# EOF
# sudo systemctl restart docker
```

### 故障4：Volume 权限问题

```bash
# 场景：bind mount 后容器写不进去
mkdir /tmp/readonly-dir
chmod 444 /tmp/readonly-dir

docker run --rm -v /tmp/readonly-dir:/data alpine touch /data/test
# touch: /data/test: Permission denied

# 排查步骤：
# 1. 检查宿主机目录权限：ls -ld /tmp/readonly-dir
# 2. 检查容器内用户 UID
# 3. 检查 SELinux（如果有）

# 修复：
chmod 755 /tmp/readonly-dir
rmdir /tmp/readonly-dir
```

### 故障5：容器网络不通

```bash
# 场景A：不在同一网络
docker run -d --name net-a nginx:alpine
docker run -d --name net-b nginx:alpine

docker exec net-b ping -c 1 net-a
# ping: bad address 'net-a' ← 默认 bridge 无 DNS

# 排查：docker network ls + docker inspect 查网络
# 修复：创建自定义网络或通过 IP 通信
docker rm -f net-a net-b

# 场景B：DNS 解析失败
docker run -d --name dns-test alpine sleep 3600
docker exec dns-test ping google.com
# ping: bad address 'google.com'

# 排查容器 DNS 配置
docker exec dns-test cat /etc/resolv.conf
# nameserver 8.8.8.8 ← 是否可达？

# 设置自定义 DNS
docker run --rm --dns 223.5.5.5 alpine ping -c 1 www.baidu.com
# ✓

docker rm -f dns-test
```

### 故障6：磁盘空间不足

```bash
# 查看 Docker 磁盘使用
docker system df
# TYPE           TOTAL   ACTIVE   SIZE     RECLAIMABLE
# Images         5       3        1.2GB    800MB (66%)
# Containers     3       3        50MB     0B (0%)
# Local Volumes  2       2        200MB    0B (0%)

# 清理不用的资源
docker system prune -a --volumes
# ⚠️ 慎用！会删除所有停止的容器、未使用的网络、悬空镜像、构建缓存
```

---

## 五、练习题

### 练习1：排障决策树（20分）

画出 Docker 容器故障的决策树：
容器启动失败 → 查 exit code → 查 logs → 分类处理

### 练习2：综合排障（30分）

教师注入 3 个故障（从上面 6 个中选），学生排查并写排障报告：

```
故障#：__
现象：__
排查过程（每一步的命令+输出+判断）：
根因：__
修复方法：__
验证结果：__
```

### 练习3：Docker 资源清理（20分）

1. 查看 Docker 占用了多少磁盘空间
2. 清理停止的容器、无用的镜像、悬挂的 volume
3. 写一个定期清理脚本

### 练习4：Docker daemon 故障（15分）

1. `sudo systemctl stop docker` → docker 命令会报什么错？
2. Docker daemon 起不来，怎么排查？
3. `docker info` vs `docker version` 哪个能帮助判断 daemon 状态？

### 练习5：容器安全排障（15分）

1. 容器以 root 运行有什么风险？
2. 怎么查看容器内的用户？
3. 容器能访问宿主机的 /proc 吗？有什么安全隐患？

## 七、常见问题

**Q: 容器问题第一步查什么？**
A: `docker ps -a` 看状态（Exited? Up? Restarting?），`docker logs 容器名` 看日志。90% 的问题都能从这两条命令找到线索。

**Q: exited (137) 是什么意思？**
A: 137 = 128 + 9，表示容器被 SIGKILL（kill -9）杀掉了。常见原因：OOM Killer（内存超限被内核杀）、手动 docker kill、宿主机资源不足。

**Q: Docker daemon 挂了怎么办？**
A: `sudo systemctl status docker` 查状态。常见原因：磁盘满了（df -h）、配置语法错误（daemon.json 格式不对）、与 firewalld 冲突。修复后 `sudo systemctl restart docker`。

## 八、课后思考

1. 生产环境中容器故障的"自愈"机制怎么实现？（提示：restart policy、healthcheck、Kubernetes liveness probe、监控告警+自动重启）

2. Docker 的排障和传统 Linux 排障有什么异同？容器化的引入让排障变简单了还是变复杂了？
