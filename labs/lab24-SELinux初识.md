# Lab24：SELinux 初识与排错

> 课时：2 | 类型：个人 | 前置：Lab22

## 一、实验步骤

### 步骤1：查看 SELinux 状态

```bash
getenforce                         # Enforcing / Permissive / Disabled
sestatus                           # 详细状态
cat /etc/selinux/config            # 配置文件
```

### 步骤2：查看安全上下文

```bash
ls -lZ /usr/share/nginx/html/      # 文件上下文
# ... system_u:object_r:httpd_sys_content_t:s0 ...
#                          ↑ 类型（最重要）

ps -Z aux | grep nginx             # 进程上下文
# ... system_u:system_r:httpd_t:s0 ...

# 核心理解：httpd_t（进程）只能读 httpd_sys_content_t（文件）
# 上下文不对 → Permission denied（即使权限 777！）
```

### 步骤3：经典故障——改网站目录后 403

```bash
sudo mkdir -p /custom-web
echo "<h1>Test</h1>" | sudo tee /custom-web/index.html
sudo chmod -R 755 /custom-web

# 配置 Nginx 指向 /custom-web（端口 8088）
sudo tee /etc/nginx/conf.d/custom.conf << 'EOF'
server { listen 8088; root /custom-web; index index.html; }
EOF
sudo nginx -t && sudo systemctl reload nginx

curl http://localhost:8088
# 403 Forbidden（即使 chmod 755！）

# 排查：
sudo tail -3 /var/log/nginx/error.log    # "Permission denied"
sudo ausearch -m avc -ts recent | grep denied  # SELinux 拒绝记录

# 修复：
ls -lZ /custom-web/                       # 上下文是 default_t
sudo restorecon -Rv /custom-web/          # 恢复正确的上下文
curl http://localhost:8088                # ✓
```

### 步骤4：SELinux 排错命令

```bash
# 临时切 Permissive 验证（确认是不是 SELinux 的问题）
sudo setenforce 0
curl http://localhost:8088                # 通了→确认是 SELinux
sudo setenforce 1                         # 切回来，修复问题

# 查看审计日志
sudo ausearch -m avc -ts recent | tail -10

# 查看布尔值
getsebool -a | grep httpd
sudo setsebool -P httpd_can_network_connect on  # 允许 Nginx 反代
```

---

## 五、练习题

### 练习1：SELinux vs 文件权限（15分）

| 场景 | 是文件权限问题？ | 是 SELinux 问题？ |
|------|----------------|-----------------|
| chmod 000 的文件 | | |
| chmod 755 但还是 403 | | |
| chmod 777 但还是 403 | | |

### 练习2：SELinux 排障流程（25分）

写出完整的"SELinux 导致 403 → 排查 → 修复"流程（每步的命令+判断）。

### 练习3：上下文修复（20分）

```bash
# 改变文件上下文
sudo chcon -t user_home_t /usr/share/nginx/html/index.html
curl http://localhost                    # 403
```

1. 用 restorecon 修复
2. chcon 和 restorecon 有什么区别？
3. 用 `semanage fcontext` 设置永久默认上下文怎么做？

### 练习4：SELinux 日常运维（20分）

写出 3 个 SELinux 常见故障及修复方案：
1. Nginx 改了网站目录 → 403
2. Nginx 反向代理 → 502（httpd_can_network_connect=off）
3. SSH 改了端口 → 连不上

### 练习5：安全认知（20分）

1. 生产环境能不能关 SELinux？为什么？
2. `setenforce 0` 是"修复"还是"调试"？
3. SELinux Enforcing + Firewalld + 文件权限 → 这叫什么安全策略？

---

## 六、验收标准
- [ ] 能查看 SELinux 运行模式（getenforce/sestatus）
- [ ] 能用 ls -Z/ps -Z 查看安全上下文
- [ ] 能排查 SELinux 导致的 Permission denied
- [ ] 能用 restorecon 修复文件上下文
- [ ] 练习 1-5 全部完成

## 七、常见问题

**Q: 生产环境能不能关掉 SELinux？**
A: 不建议。SELinux 是重要安全防线，历史上很多著名漏洞（Redis 未授权访问、Docker 容器逃逸）在启用 SELinux 的系统上被有效阻止。遇到问题应该是修上下文/布尔值，而不是关 SELinux。

**Q: SELinux 这么麻烦，为什么不用 AppArmor（Ubuntu 的 MAC）？**
A: 都可以，但 SELinux 更精细（基于 inode 级别的标签），企业 RHEL 系环境标配 SELinux。AppArmor 基于路径，配置更简单但粒度较粗。

**Q: chcon 和 restorecon 有什么区别？**
A: chcon 直接改上下文（手动指定），restorecon 恢复到"策略规定的默认上下文"。restorecon 更安全——它是"恢复到正确值"而非"设成你想要的"。

**Q: setenforce 0 是修复还是调试？**
A: 是调试手段，不是修复方案。用 setenforce 0 验证"问题是不是 SELinux 导致的"，如果是，应该修复上下文/布尔值，然后 setenforce 1 切回来。

## 八、课后思考

1. SELinux 的 Enforcing 模式和 Permissive 模式在日志记录上有什么不同？如果只开 Permissive 不开 Enforcing，会有什么安全隐患？

2. 容器（Docker/Podman）和 SELinux 的关系是什么？容器内进程的 SELinux 上下文是怎么设置的？
