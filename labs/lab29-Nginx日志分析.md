# Lab29：Nginx 日志分析与排障

> 课时：2 | 类型：个人 | 前置：Lab28

## 一、你会学到什么
- 能读懂 access.log 的每个字段
- 能用 tail -f 实时监控访问日志
- 能根据 error.log 定位 403/404/502 等错误
- 能用 awk/sort/uniq 做日志统计分析

## 二、实验步骤

### 步骤1：理解 access.log 格式

```bash
# 查看一条完整的访问日志
sudo tail -1 /var/log/nginx/access.log
```

日志格式（默认 combined 格式）：
```
192.168.200.1 - - [21/Jun/2026:10:30:45 +0800] "GET / HTTP/1.1" 200 1234 "-" "curl/8.x"
 ① 客户端IP    ②③     ④ 时间戳                        ⑤ 请求行          ⑥ 状态码 ⑦ 大小 ⑧ Referer ⑨ UA
```

| 字段 | 含义 | 排障用途 |
|------|------|---------|
| $remote_addr | 客户端 IP | 定位请求来源 |
| $time_local | 时间戳 | 定位问题发生时间 |
| $request | 请求行（方法 URL 协议） | 知道访问了什么 |
| $status | HTTP 状态码 | 200正常/404不存在/500异常 |
| $body_bytes_sent | 响应体大小 | 流量统计 |
| $http_user_agent | 客户端软件 | 识别爬虫/攻击工具 |

### 步骤2：tail -f 实时监控

```bash
# 终端1：实时跟踪日志
sudo tail -f /var/log/nginx/access.log

# 终端2：发起不同请求
curl -s http://localhost > /dev/null
curl -s http://localhost/nonexistent > /dev/null
curl -s -H "User-Agent: Googlebot/2.1" http://localhost > /dev/null
curl -s -X POST http://localhost > /dev/null

# 终端1 观察每条请求的实时记录
# Ctrl+C 退出 tail -f
```

> **验收点**：能在 access.log 中找到自己刚发的 4 条请求，辨认每条的 URL 和状态码。

### 步骤3：error.log 排障

```bash
# 模拟 404 错误
curl -s http://localhost/no-such-file
sudo tail -3 /var/log/nginx/error.log
# 看到：open() ... failed (2: No such file or directory)

# 模拟 403 错误（文件权限问题）
echo "secret" | sudo tee /usr/share/nginx/html/secret.txt
sudo chmod 000 /usr/share/nginx/html/secret.txt
curl -s http://localhost/secret.txt
sudo tail -3 /var/log/nginx/error.log
# 看到：Permission denied
sudo rm /usr/share/nginx/html/secret.txt

# 502 Bad Gateway（模拟反代到不存在上游）
sudo tee /etc/nginx/conf.d/bad-gateway.conf << 'EOF'
server {
    listen 8089;
    location / { proxy_pass http://127.0.0.1:19999; }
}
EOF
sudo nginx -t && sudo systemctl reload nginx
curl -s http://localhost:8089
sudo tail -5 /var/log/nginx/error.log
# 看到：connect() failed (111: Connection refused)
sudo rm /etc/nginx/conf.d/bad-gateway.conf
sudo systemctl reload nginx
```

> **验收点**：能区分 404（找不到文件）、403（权限拒绝）、502（上游不可达）三类错误在日志中的表现。

### 步骤4：日志统计分析

```bash
# 先制造一些访问数据
for i in {1..20}; do curl -s http://localhost > /dev/null; done
for i in {1..5}; do curl -s http://localhost/nonexistent > /dev/null; done
curl -s -H "User-Agent: Googlebot/2.1" http://localhost > /dev/null
curl -s http://localhost/about > /dev/null
curl -s http://localhost/about > /dev/null

# 1. 总访问量
sudo wc -l /var/log/nginx/access.log

# 2. 访问 Top 5 IP
sudo awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -5

# 3. 状态码分布
sudo awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# 4. 访问最多的 URL Top 5
sudo awk '{print $7}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -5

# 5. 所有 404 的 URL
sudo awk '$9==404 {print $7}' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# 6. 独立 IP 数
sudo awk '{print $1}' /var/log/nginx/access.log | sort -u | wc -l

# 7. 查找爬虫访问
sudo grep -i "bot\|spider\|crawler" /var/log/nginx/access.log | head -5
```

> **验收点**：至少完成 4 项统计，理解每条 awk 命令的含义。

### 步骤5：自定义日志格式

```bash
# 查看当前日志格式定义
grep "log_format" /etc/nginx/nginx.conf

# 在虚拟主机中可以使用不同的日志格式
# access_log /var/log/nginx/custom.log 自定义格式名;
```

### 步骤6：日志轮转

```bash
# Nginx 日志轮转配置
cat /etc/logrotate.d/nginx

# 手动触发一次轮转
sudo logrotate -f /etc/logrotate.d/nginx
ls -l /var/log/nginx/                # 看到 .gz 归档文件
```

关键参数理解：

| 参数 | 含义 |
|------|------|
| daily | 每天轮转一次 |
| rotate 14 | 保留 14 个归档文件 |
| compress | 归档后压缩 |
| delaycompress | 延迟压缩（保留最近一个不压缩） |
| missingok | 日志文件不存在不报错 |
| notifempty | 空文件不轮转 |
| postrotate ... endscript | 轮转后执行的命令（如 reload nginx） |

---

## 五、练习题

### 练习1：日志字段识别（15分）

以下是一条 access.log 记录，写出每个字段的含义：

```
10.0.0.5 - admin [21/Jun/2026:14:30:00 +0800] "POST /api/login HTTP/1.1" 401 12 "http://site/login" "Mozilla/5.0"
```

| 字段 | 值 | 含义 |
|------|-----|------|
| 客户端IP | | |
| 远程用户 | | |
| 认证用户 | | |
| 时间 | | |
| 请求方法 | | |
| URL | | |
| 状态码 | | 401 = ? |
| 响应大小 | | |
| Referer | | |
| User-Agent | | |

### 练习2：日志统计脚本（25分）

写一个脚本 `~/analyze-nginx-log.sh`，接受一个 access.log 文件路径，输出：
1. 总请求数
2. 独立 IP 数
3. 状态码分布（200/301/403/404/500 各多少）
4. Top 10 访问 URL
5. Top 10 客户端 IP

### 练习3：日志排障场景（25分）

以下 3 个场景，写出如何通过日志定位问题：

| 场景 | 查什么日志 | 搜什么关键词 | 期望找到什么 |
|------|----------|------------|------------|
| 用户反馈网站打不开 | | | |
| 安全部门说有人在扫描 | | | |
| 某 URL 突然大量 500 | | | |

### 练习4：监控告警脚本（20分）

写一个脚本 `~/watch-nginx-error.sh`，每分钟检查一次 `/var/log/nginx/error.log`，如果出现新的 `error` 或 `crit` 级别日志，输出告警消息。用 crontab 每分钟执行。

### 练习5：日志轮转配置（15分）

1. 修改 Nginx 的 logrotate 配置：改为保留 30 天，按大小轮转（超过 100MB）
2. 手动测试轮转是否正常
3. 如果日志文件被删了，logrotate 会报错吗？（提示：missingok）

## 七、常见问题

**Q: access.log 太大怎么办（几十GB）？**
A: ①配置 logrotate 定期轮转压缩；②用 `logrotate` 按大小轮转（size 100M）；③开启 `access_log off;` 关闭不需要的日志；④用 cron 定期清理旧归档。

**Q: Nginx error.log 级别怎么调？**
A: `error_log /var/log/nginx/error.log warn;` 可选级别：debug/info/notice/warn/error/crit/alert/emerg。生产环境用 warn 或 error，debug 会产生海量日志。

**Q: 怎么区分正常流量和恶意扫描？**
A: 看 User-Agent、请求频率、请求 URL 特征。大量 404、奇怪的 URL（/wp-admin、/.env、/admin.php）、非浏览器 UA 都是扫描特征。

## 八、课后思考

1. 如果你的网站突然访问量暴增（可能是被攻击或上热搜），仅靠 tail -f access.log 能应对吗？生产环境一般用什么工具做日志集中管理和分析？（提示：ELK、Loki、阿里云 SLS）

2. 日志中如果看到大量来自某个 IP 的 404 请求，你应该怎么办？这是攻击吗？怎么防护？
