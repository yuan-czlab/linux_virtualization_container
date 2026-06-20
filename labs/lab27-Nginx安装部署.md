# Lab27：Nginx 安装与基础部署

> 课时：2 | 类型：个人 | 前置：Lab13

## 一、你会学到什么
- 能独立完成 Nginx 的安装和启动
- 能理解 Nginx 的目录结构和进程架构
- 能修改默认网页并验证
- 能用 nginx -t 检查配置语法

## 二、Nginx 核心目录结构

```
/etc/nginx/nginx.conf        主配置文件
/etc/nginx/conf.d/*.conf     虚拟主机配置
/usr/share/nginx/html/       默认网站根目录
/var/log/nginx/access.log    访问日志
/var/log/nginx/error.log     错误日志（排障关键）
```

## 三、实验步骤

### 步骤1：安装与启动

```bash
sudo dnf install -y nginx
sudo systemctl enable --now nginx
systemctl status nginx              # active (running)

# 确认 80 端口在监听
ss -tlnp | grep :80
# LISTEN *:80 → nginx 监听所有地址的 80 端口

# 防火墙放行
sudo firewall-cmd --add-service=http --permanent
sudo firewall-cmd --reload
```

### 步骤2：验证与测试

```bash
curl -s http://localhost | head -10  # 默认欢迎页
curl -I http://localhost             # 只看响应头
# HTTP/1.1 200 OK
# Server: nginx/1.x
```

从宿主机浏览器访问 `http://你的VM_IP` → 看到 Nginx 欢迎页。

### 步骤3：理解 Nginx 进程

```bash
ps aux | grep nginx
# root     xxx  nginx: master process    ← master（读配置，管worker）
# nginx    xxx  nginx: worker process    ← worker（处理请求）

grep "^user" /etc/nginx/nginx.conf       # worker 以 nginx 用户运行
grep "worker_processes" /etc/nginx/nginx.conf  # worker 数量
```

### 步骤4：修改默认网站

```bash
# 备份原页面
sudo cp /usr/share/nginx/html/index.html /usr/share/nginx/html/index.html.bak

# 创建自己的首页
sudo tee /usr/share/nginx/html/index.html << 'HTML'
<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>运维实战</title></head>
<body>
  <h1>🚀 Nginx 部署成功</h1>
  <p>主机名：<strong>__HOSTNAME__</strong></p>
  <p>部署时间：<strong>__TIME__</strong></p>
</body>
</html>
HTML

# 动态替换
sudo sed -i "s/__HOSTNAME__/$(hostname)/g" /usr/share/nginx/html/index.html
sudo sed -i "s/__TIME__/$(date)/g" /usr/share/nginx/html/index.html

curl -s http://localhost | head -5
```

### 步骤5：nginx -t 检查配置

```bash
sudo nginx -t
# nginx: the configuration file ... syntax is ok
# nginx: configuration file ... test is successful

# 养成习惯：改配置 → nginx -t → systemctl reload
```

### 步骤6：Nginx 目录探索

```bash
# 不查资料，用命令探索 Nginx 的文件布局
rpm -ql nginx | head -30            # Nginx 安装的所有文件
rpm -qc nginx                        # 只列配置文件
ls -l /etc/nginx/                    # 配置目录
ls -l /var/log/nginx/                # 日志目录
```

---

## 五、练习题

### 练习1：Nginx 目录填空（15分）

| 路径 | 作用 |
|------|------|
| `/etc/nginx/nginx.conf` | |
| `/etc/nginx/conf.d/` | |
| `/usr/share/nginx/html/` | |
| `/var/log/nginx/access.log` | |
| `/var/log/nginx/error.log` | |

### 练习2：制作公司官网首页（20分）

修改默认页面，做一个完整的 HTML 页面，包含：公司名称（标题）、导航栏（3 个菜单项）、一段介绍文字、底部版权信息。用浏览器访问并截图。

### 练习3：配置变更流程（20分）

写出修改 Nginx 配置的标准操作流程（SOP）：从编辑文件到确认生效，每步带命令。

### 练习4：排障（25分）

制造以下故障并排查修复：
1. Nginx 停止 → curl 报什么错？
2. 配置语法错误（nginx.conf 里随便删一个分号）→ nginx -t 报什么？
3. 80 端口被占用 → Nginx 启动报什么？怎么定位占用进程？

### 练习5：Nginx 性能测试（20分）

用 `ab`（Apache Bench）做简单压力测试：
```bash
sudo dnf install -y httpd-tools
ab -n 1000 -c 10 http://localhost/
```
记录：Requests per second、Time per request、Failed requests（如果有）

## 七、常见问题

**Q: nginx -t 通过但网页 404？**
A: root 路径配置错了。检查 `grep "root" /etc/nginx/nginx.conf`，确认目录存在且有 index.html。

**Q: 网页返回 403 Forbidden？**
A: 三步排查：① 文件权限 `ls -l` 确认 nginx 用户可读；② 目录权限需要 x 权限；③ SELinux 上下文 `ls -lZ` 是否为 httpd_sys_content_t。

**Q: Nginx 启动报 "could not bind to 0.0.0.0:80"？**
A: 80 端口被占用了。`ss -tlnp | grep :80` 找出谁在占，停掉或用不同端口。

**Q: reload 和 restart 什么时候用哪个？**
A: 日常用 reload（改配置后不中断服务），restart 只在 Nginx 进程出问题时用。reload 不中断已有连接，restart 会。

## 八、课后思考

1. Nginx 的 worker_processes 设为 auto 是什么意思？如果服务器有 8 核 CPU，worker 数应该设为多少？为什么不是越多越好？

2. Nginx 除了做 Web 服务器，还能做什么？（提示：反向代理、负载均衡、HTTP 缓存、邮件代理）
