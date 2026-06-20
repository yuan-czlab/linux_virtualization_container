# Lab30：Nginx HTTPS 与 SSL 证书

> 课时：2 | 类型：个人 | 前置：Lab29

## 一、你会学到什么
- 理解 HTTPS = HTTP + TLS/SSL 加密
- 能生成自签名证书用于测试环境
- 能配置 Nginx 监听 443 端口
- 能配置 HTTP 自动跳转 HTTPS

## 二、实验步骤

### 步骤1：生成自签名证书

```bash
sudo mkdir -p /etc/nginx/ssl

# 一条命令生成：私钥 + 自签名证书（有效期 365 天）
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/server.key \
  -out /etc/nginx/ssl/server.crt \
  -subj "/C=CN/ST=Guangdong/L=Shenzhen/O=MySchool/CN=www.site-a.local"

# 参数解释：
# -x509          自签名证书格式
# -nodes         私钥不加密（no DES，测试环境用）
# -days 365      证书有效期
# -newkey rsa:2048  新生成 2048 位 RSA 密钥
# -keyout        私钥输出路径
# -out           证书输出路径
# -subj          证书主题（CN=域名 最重要）

# 私钥必须保密！
sudo chmod 600 /etc/nginx/ssl/server.key
sudo chmod 644 /etc/nginx/ssl/server.crt
```

### 步骤2：查看证书信息

```bash
# 查看证书内容
openssl x509 -in /etc/nginx/ssl/server.crt -text -noout | head -30

# 关键信息
openssl x509 -in /etc/nginx/ssl/server.crt -noout -subject   # 主题
openssl x509 -in /etc/nginx/ssl/server.crt -noout -issuer    # 签发者（自签=主题）
openssl x509 -in /etc/nginx/ssl/server.crt -noout -dates     # 有效期
openssl x509 -in /etc/nginx/ssl/server.crt -noout -fingerprint  # 指纹
```

### 步骤3：配置 HTTPS 虚拟主机

```bash
sudo tee /etc/nginx/conf.d/site-a-ssl.conf << 'EOF'
# HTTP → HTTPS 自动跳转
server {
    listen 80;
    server_name www.site-a.local;
    return 301 https://$host$request_uri;
}

# HTTPS 站点
server {
    listen 443 ssl;
    server_name www.site-a.local;

    ssl_certificate     /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;

    # SSL 安全配置（禁用不安全协议和算法）
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /var/www/site-a;
    index index.html;
}
EOF

# 放行 443 端口
sudo firewall-cmd --add-service=https --permanent
sudo firewall-cmd --reload

sudo nginx -t && sudo systemctl reload nginx
```

### 步骤4：测试 HTTPS

```bash
# 1. curl -k 跳过证书验证（自签名证书不被系统信任）
curl -k https://www.site-a.local
# ✓ 返回站点 A 的内容

# 2. 不加 -k 会报错
curl https://www.site-a.local
# curl: (60) SSL certificate problem: self-signed certificate

# 3. HTTP 自动跳转 HTTPS
curl -I http://www.site-a.local
# HTTP/1.1 301 Moved Permanently
# Location: https://www.site-a.local/

# 4. 查看证书详情
openssl s_client -connect www.site-a.local:443 -servername www.site-a.local < /dev/null 2>/dev/null | openssl x509 -noout -subject -dates
```

### 步骤5：理解证书信任链

```bash
# 自签名证书 = 自己给自己签发 → 浏览器不信任 → 警告"不安全"
# CA 证书 = 受信任的 CA 机构签发 → 浏览器信任 → 显示锁图标

# 查看系统信任的 CA 证书
ls /etc/pki/ca-trust/source/anchors/
# 或 /etc/ssl/certs/

# 浏览器访问 https://你的VM_IP → 观察证书警告页面
```

### 步骤6：证书过期检查

```bash
# 查看证书剩余有效天数
openssl x509 -in /etc/nginx/ssl/server.crt -noout -enddate

# 写一个检查脚本
cat > ~/check-ssl-expiry.sh << 'SCRIPT'
#!/bin/bash
CERT="/etc/nginx/ssl/server.crt"
END_DATE=$(openssl x509 -in "$CERT" -noout -enddate | cut -d= -f2)
END_EPOCH=$(date -d "$END_DATE" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($END_EPOCH - $NOW_EPOCH) / 86400 ))
echo "证书到期日期: $END_DATE"
echo "剩余天数: $DAYS_LEFT 天"
if [ $DAYS_LEFT -lt 30 ]; then
    echo "[WARNING] 证书即将过期，请及时更新！"
fi
SCRIPT
chmod +x ~/check-ssl-expiry.sh
./check-ssl-expiry.sh
```

---

## 五、练习题

### 练习1：HTTPS vs HTTP 对比（15分）

| 对比项 | HTTP | HTTPS |
|--------|------|-------|
| 默认端口 | | |
| 是否加密 | | |
| 是否验证服务器身份 | | |
| curl 直接访问 | | |
| 证书要求 | | |

### 练习2：自签名 vs CA 证书（20分）

| 对比 | 自签名证书 | CA 签发证书 |
|------|----------|-----------|
| 谁签发 | | |
| 浏览器表现 | | |
| 费用 | | |
| 适用场景 | | |
| 有效期 | | |

生产环境如何免费获取受信任的证书？（提示：Let's Encrypt）

### 练习3：证书排障（25分）

1. 如果私钥丢了，证书还能用吗？
2. 如果证书过期了，curl 访问会怎样？
3. 如果 nginx.conf 中 ssl_certificate 路径写错了，`nginx -t` 会报什么错？
4. Nginx 配了 HTTPS 但 443 端口不通，排查步骤是什么？

### 练习4：SSL 安全评分（20分）

1. 用 `openssl s_client` 查看你的 Nginx 支持的 TLS 版本和加密套件
2. TLS 1.0 和 1.1 为什么不安全？应该禁用吗？
3. 在 Nginx 中禁用 TLS 1.0 和 TLS 1.1 的配置是什么？

### 练习5：Let's Encrypt 自动续期（20分）

研究 Let's Encrypt + certbot：
1. certbot 怎么自动获取证书？
2. 证书有效期只有 90 天，怎么自动续期？
3. 写出 certbot 获取 + 自动续期的命令流程

---

## 六、清理
```bash
sudo rm -f /etc/nginx/conf.d/site-a-ssl.conf /etc/nginx/ssl/server.key /etc/nginx/ssl/server.crt
sudo rmdir /etc/nginx/ssl 2>/dev/null
sudo systemctl reload nginx
```

## 七、常见问题

**Q: 自签名证书和生产证书的区别？**
A: 自签 = 自己给自己签发，浏览器会警告"不安全"。生产证书 = 受信任的 CA 签发，浏览器显示锁图标。测试环境用自签，生产用 Let's Encrypt 或付费 CA。

**Q: 私钥泄露了怎么办？**
A: ①立即在服务器上替换为新私钥+新证书；②吊销旧证书（如果是 CA 签发的）；③排查泄露途径；④检查是否有利用旧证书的攻击痕迹。

**Q: curl: (60) SSL certificate problem？**
A: 自签名证书不受系统信任。测试环境用 `curl -k` 跳过，或把自签名证书加到系统信任链。生产环境必须用 CA 证书。

## 八、课后思考

1. Let's Encrypt 提供免费 SSL 证书，有效期只有 90 天。生产环境如何实现自动续期？如果不自动续期会发生什么？

2. HTTPS 加密了哪些内容？中间人还能看到什么？（提示：域名、IP、端口仍然可见——SNI 和 TCP 头不加密）
