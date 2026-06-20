# Lab46：三机服务器环境搭建

> 课时：2 | 类型：双人 | 前置：Lab39

## 任务：搭建 Web + DB + Client 三机环境

### 环境要求
- web-server (192.168.200.10)：Nginx
- db-server (192.168.200.20)：MariaDB + Redis
- client (192.168.200.30)：测试客户端

### 任务清单
1. 三机 /etc/hosts 全部配置完成
2. 三机互 ping 通（用主机名）
3. SSH 免密登录互信（client → web-server, client → db-server）
4. web-server 部署 Nginx
5. db-server 部署 MariaDB + Redis（允许内网远程连接）
6. client 远程测试：curl web-server、mysql -h db-server、redis-cli -h db-server
7. 编写完整部署文档：拓扑图 + IP 规划表 + 配置记录

### 提交
- 拓扑图（截图或照片）
- IP 规划表
- 部署步骤文档
- 三机服务验证截图

## 七、常见问题

**Q: 三台 VM 互 ping 通但 SSH 连不上？**
A: 检查 sshd 是否在目标 VM 上运行，防火墙是否放行 22 端口，/etc/hosts 配置是否正确。

**Q: 在多台 VM 之间做免密登录有什么注意事项？**
A: 每对 VM 之间的密钥是独立管理的。建议从 client 统一管理，client 的密钥分发到所有服务器。生产环境建议用配置管理工具（Ansible）统一管理密钥。

**Q: IP 规划表有什么用？**
A: ①防止 IP 冲突；②新人接手时快速了解网络拓扑；③故障排查时快速定位服务位置；④合规审计需要。

## 八、课后思考

1. 三机环境的拓扑图你应该画成什么格式？（ASCII 图、draw.io、Visio、手绘）哪种方式最适合放在运维文档中？

2. 如果公司从 3 台服务器扩展到 50 台，你现在的部署方式（手动 SSH 逐台配置）还可行吗？有什么自动化方案？
