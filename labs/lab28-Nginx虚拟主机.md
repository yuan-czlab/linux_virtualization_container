# Lab28：Nginx 虚拟主机

> 课时：2 | 类型：个人 | 前置：Lab27

## 一、你会学到什么
- 理解 server_name 和虚拟主机的概念
- 能在同一台服务器上部署多个不同域名的网站
- 能配置默认 server 处理未知域名

## 二、实验步骤

### 步骤1：准备两个网站

```bash
sudo mkdir -p /var/www/site-a /var/www/site-b

sudo tee /var/www/site-a/index.html << 'HTML'
<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Site A</title>
<style>body{font-family:sans-serif;margin:50px;background:#e8f5e9;}
h1{color:#2e7d32;}</style></head>
<body><h1>🏠 站点 A</h1><p>域名：www.site-a.local</p></body></html>
HTML

sudo tee /var/www/site-b/index.html << 'HTML'
<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Site B</title>
<style>body{font-family:sans-serif;margin:50px;background:#e3f2fd;}
h1{color:#1565c0;}</style></head>
<body><h1>📦 站点 B</h1><p>域名：www.site-b.local</p></body></html>
HTML
```

### 步骤2：创建虚拟主机配置

```bash
sudo tee /etc/nginx/conf.d/site-a.conf << 'EOF'
server {
    listen 80;
    server_name www.site-a.local;
    root /var/www/site-a;
    index index.html;
    access_log /var/log/nginx/site-a-access.log;
    error_log /var/log/nginx/site-a-error.log;
}
EOF

sudo tee /etc/nginx/conf.d/site-b.conf << 'EOF'
server {
    listen 80;
    server_name www.site-b.local;
    root /var/www/site-b;
    index index.html;
    access_log /var/log/nginx/site-b-access.log;
    error_log /var/log/nginx/site-b-error.log;
}
EOF

sudo nginx -t && sudo systemctl reload nginx
```

### 步骤3：用 /etc/hosts 模拟域名测试

```bash
echo "127.0.0.1 www.site-a.local www.site-b.local" | sudo tee -a /etc/hosts

# 测试（关键是 Host 头）
curl -H "Host: www.site-a.local" http://localhost    # → 站点A
curl -H "Host: www.site-b.local" http://localhost    # → 站点B
curl http://www.site-a.local                         # → 站点A（hosts生效）
```

### 步骤4：默认 server

```bash
# 没有匹配任何 server_name 的请求走 default_server
sudo tee /etc/nginx/conf.d/default.conf << 'EOF'
server {
    listen 80 default_server;
    server_name _;
    return 200 "No website configured for this domain.\n";
    add_header Content-Type text/plain;
}
EOF

sudo nginx -t && sudo systemctl reload nginx

# 测试未知域名
curl -H "Host: unknown.example.com" http://localhost
# → "No website configured for this domain."
```

### 步骤5：server_name 匹配规则

| 优先级 | 匹配方式 | 示例 |
|--------|---------|------|
| 1 | 精确匹配 | `server_name www.a.com;` |
| 2 | 通配符前缀 | `server_name *.a.com;` |
| 3 | 通配符后缀 | `server_name www.a.*;` |
| 4 | 正则表达式 | `server_name ~^www\.(.+)$;` |
| 5 | default_server | `listen 80 default_server;` |

---

## 五、练习题

### 练习1：虚拟主机配置（20分）

搭建第三个站点 `blog.site-a.local`，指向 `/var/www/blog/`。验证三个站点都正常工作。

### 练习2：访问控制（25分）

给 `www.site-b.local` 配置 IP 访问控制：只允许 127.0.0.1 和 192.168.200.0/24 访问，其他 IP 返回 403。

### 练习3：自定义错误页面（20分）

给站点 A 配置自定义 404 页面：创建 `/var/www/site-a/404.html`，在 Nginx 中配置 `error_page 404 /404.html;`

### 练习4：同一个 server_name 冲突（15分）

如果两个配置文件都写了 `server_name www.site-a.local;`，Nginx 选择哪一个？为什么？如何确定加载顺序？

### 练习5：多端口站点（20分）

在 8080 端口部署一个管理后台（根目录 `/var/www/admin`），只允许本机访问。

## 七、常见问题

**Q: server_name 写了 _（下划线）是什么意思？**
A: 无效的域名占位符，表示匹配所有没有在其他 server 块匹配到的请求。配合 `listen 80 default_server;` 实现兜底处理。

**Q: 两个虚拟主机都配了相同的 server_name 怎么办？**
A: Nginx 会选择先加载的那个（按配置文件名排序）。但不要依赖这个行为——server_name 应该唯一。

**Q: 配置文件改了但没生效？**
A: `nginx -t` 先检查语法，然后 `systemctl reload nginx`（不是 restart）。reload 不中断服务。

## 八、课后思考

1. 如果一台服务器需要托管 100 个网站，每个网站一个 server 块，怎么管理配置文件更合理？（提示：每个站点一个 .conf 文件，放在 conf.d/ 下）

2. Nginx 的 location 块可以匹配 URL 路径，`location /api/` 和 `location ~ \.php$` 有什么区别？（提示：前缀匹配 vs 正则匹配）
