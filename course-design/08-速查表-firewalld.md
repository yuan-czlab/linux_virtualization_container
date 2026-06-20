# firewalld 防火墙速查卡

> 打印给学生 | 单面A4

---

## 查看规则

| 命令 | 说明 |
|------|------|
| `firewall-cmd --list-all` | 查看当前zone完整规则 |
| `firewall-cmd --list-all --permanent` | 查看永久规则（未reload的） |
| `firewall-cmd --get-default-zone` | 查看默认zone（通常是public） |
| `firewall-cmd --get-active-zones` | 查看网卡绑定的zone |
| `firewall-cmd --list-services` | 查看当前zone放行的服务 |
| `firewall-cmd --list-ports` | 查看当前zone放行的端口 |
| `firewall-cmd --list-rich-rules` | 查看高级规则 |

## 放行/拒绝

| 操作 | 命令 |
|------|------|
| 放行服务（临时） | `sudo firewall-cmd --add-service=http` |
| 放行服务（永久） | `sudo firewall-cmd --add-service=http --permanent` |
| 放行端口（永久） | `sudo firewall-cmd --add-port=8080/tcp --permanent` |
| 放行端口范围 | `sudo firewall-cmd --add-port=8000-8100/tcp --permanent` |
| 删除规则 | `sudo firewall-cmd --remove-service=http --permanent` |
| 重载生效 | `sudo firewall-cmd --reload` |
| 临时规则固化 | `sudo firewall-cmd --runtime-to-permanent` |

## 预定义 service

| service名 | 端口 |
|-----------|------|
| ssh | 22/tcp |
| http | 80/tcp |
| https | 443/tcp |
| mysql | 3306/tcp |
| redis | 6379/tcp |
| nfs | 2049/tcp |
| cockpit | 9090/tcp |

## rich-rule 常用

| 需求 | 命令 |
|------|------|
| 限制IP访问端口 | `--add-rich-rule='rule family="ipv4" source address="192.168.200.0/24" port port="22" protocol="tcp" accept'` |
| 封禁IP | `--add-rich-rule='rule family="ipv4" source address="10.0.0.99" drop'` |
| 限制连接频率 | `--add-rich-rule='rule ... port port="80" protocol="tcp" accept limit value="30/m"'` |
| 端口转发 | `--add-forward-port=port=8080:proto=tcp:toport=80` |

## zone 说明

| zone | 信任级别 | 默认放行 |
|------|---------|---------|
| public | 不信任(默认) | ssh, dhcpv6-client |
| internal | 较信任 | ssh, dhcpv6-client, mdns, samba |
| trusted | 完全信任 | 所有流量 |
| drop | 最严格 | 无（全部丢弃，无回应） |

## 排障流程

```
外部访问不了服务？
  → firewall-cmd --list-all（看 services/ports）
  → 没有对应端口 → 放行 + reload
  → 有对应端口 → 检查网卡是否在正确的 zone
  → firewall-cmd --get-active-zones（确认）
```

## Ubuntu ufw 对照

| firewalld | ufw |
|-----------|-----|
| `--list-all` | `sudo ufw status verbose` |
| `--add-service=http` | `sudo ufw allow http` |
| `--add-port=80/tcp` | `sudo ufw allow 80/tcp` |
| `--add-rich-rule='...'` | `sudo ufw allow from IP to any port XX` |
