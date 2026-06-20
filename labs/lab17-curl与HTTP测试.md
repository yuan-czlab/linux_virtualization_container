# Lab17：curl 与 HTTP 测试

> 课时：2 | 类型：个人 | 前置：Lab15

## 一、实验步骤

### 步骤1：HTTP 请求响应

```bash
sudo systemctl start nginx 2>/dev/null

curl http://localhost                    # GET 请求
curl -I http://localhost                 # 只看响应头
curl -v http://localhost 2>&1 | head -30 # 详细过程
# > 开头 = 请求头，< 开头 = 响应头
```

### 步骤2：curl 常用操作

```bash
curl -o /tmp/nginx.html http://localhost    # 下载保存
curl -L http://www.baidu.com -o /tmp/baidu.html  # 跟随重定向
curl -H "Accept-Language: zh-CN" http://localhost  # 自定义请求头
curl --connect-timeout 5 --max-time 10 http://10.0.0.1  # 超时设置
curl -k https://localhost                    # 忽略 SSL 证书错误
```

### 步骤3：HTTP 状态码识别

```bash
# 200 OK
curl -o /dev/null -s -w "%{http_code}\n" http://localhost

# 404 Not Found
curl -o /dev/null -s -w "%{http_code}\n" http://localhost/nonexistent

# 403 Forbidden（权限问题或 SELinux）
# sudo chmod 000 /usr/share/nginx/html/index.html
# curl ... → 403
```

### 步骤4：用浏览器 F12 配合

从宿主机浏览器访问 `http://VM_IP`，按 F12 → Network 标签 → 刷新 → 点击请求 → Headers/Response/Timing

---

## 五、练习题

### 练习1：状态码速查（15分）

| 状态码 | 含义 | 运维排查方向 |
|--------|------|------------|
| 200 | | |
| 301 | | |
| 403 | | |
| 404 | | |
| 500 | | |
| 502 | | |
| 503 | | |

### 练习2：curl 巡检脚本（30分）

写脚本 `~/http-check.sh`，接受 URL 列表文件，输出每个 URL 的状态码和响应时间：

```bash
# URL 列表文件
echo "http://localhost" > /tmp/urls.txt
echo "http://localhost/nonexistent" >> /tmp/urls.txt
echo "http://www.baidu.com" >> /tmp/urls.txt
```

输出格式：`[状态码] URL - 响应时间s`

### 练习3：HTTP vs HTTPS 对比（20分）

1. 用 curl -v 对比访问 http://localhost 和 https://localhost（如果有）
2. 记录 HTTP 和 HTTPS 的端口、握手过程差异

### 练习4：curl 性能测试（20分）

1. 对 localhost 连续 20 次请求，计算平均响应时间
2. 用 `curl -w` 输出各阶段耗时：DNS解析 / TCP连接 / SSL握手 / 首字节 / 总时间

### 练习5：Connection refused 排障（15分）

停止 Nginx：`sudo systemctl stop nginx` → `curl localhost` → Connection refused
- 为什么不是 timeout？（refused = 收到了但没人监听 / timeout = 根本没到）

---

## 六、验收标准
- [ ] 能说出 HTTP 请求和响应的基本结构
- [ ] 能识别常见状态码（200/301/403/404/500/502）
- [ ] 能用 curl -v/-I/-L/-o 测试 HTTP 服务
- [ ] 能根据 curl 报错判断问题类型
- [ ] 练习 1-5 全部完成

## 七、常见问题

**Q: curl 返回空但浏览器能访问？**
A: 可能网站检测 User-Agent 做了反爬。`curl -H "User-Agent: Mozilla/5.0" URL` 伪造浏览器 UA 试试。

**Q: curl: (60) SSL certificate problem？**
A: 访问自签名 HTTPS 站点时报错。测试环境用 `curl -k` 跳过证书验证。生产环境不要用 -k，应该配置正确的 CA 证书。

**Q: Connection refused vs Connection timed out 区别？**
A: Connection refused = 对方收到了请求但该端口没人监听（服务没启动/监听其他端口）。Connection timed out = 请求根本没到达（防火墙 DROP、网络不通、对方机器不存在）。前者是"到了但没人"，后者是"根本没到"。

**Q: 怎么用 curl 测试一个 API 接口的性能？**
A: `curl -o /dev/null -s -w "time_total: %{time_total}s\n" URL` 输出总耗时。还可以用 `%{time_namelookup}`、`%{time_connect}`、`%{time_starttransfer}` 分别看 DNS、TCP、首字节耗时。

## 八、课后思考

1. 浏览器 F12 Network 标签中，Timing 的各个阶段（DNS Lookup、Initial Connection、SSL、TTFB）分别对应什么？如果 TTFB 很长，可能是什么原因？

2. HTTP/1.1 和 HTTP/2 有什么区别？现在主流网站用的是哪个版本？怎么用 curl 查看网站支持的 HTTP 版本？
