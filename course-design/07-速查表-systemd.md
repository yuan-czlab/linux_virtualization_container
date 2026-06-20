# systemd 与 journalctl 速查卡

> 打印给学生 | 单面A4

---

## systemctl 服务管理

| 操作 | 命令 | 说明 |
|------|------|------|
| 查看状态 | `systemctl status 服务名` | 看 Active 和 Loaded 两行 |
| 启动 | `sudo systemctl start 服务名` | 立即启动 |
| 停止 | `sudo systemctl stop 服务名` | 立即停止 |
| 重启 | `sudo systemctl restart 服务名` | stop+start（中断服务） |
| 重载配置 | `sudo systemctl reload 服务名` | 不中断服务（推荐） |
| 开机自启 | `sudo systemctl enable 服务名` | 下次开机自动启动 |
| 禁止自启 | `sudo systemctl disable 服务名` | |
| 是否运行 | `systemctl is-active 服务名` | 返回 active/inactive |
| 是否自启 | `systemctl is-enabled 服务名` | 返回 enabled/disabled |
| 彻底禁用 | `sudo systemctl mask 服务名` | 连手动启动都不行 |
| 取消彻底禁用 | `sudo systemctl unmask 服务名` | |
| 重载systemd | `sudo systemctl daemon-reload` | 改过Service文件后执行 |

## 状态判断

| status 输出 | 含义 |
|------------|------|
| `Active: active (running)` | 正在运行 ✓ |
| `Active: inactive (dead)` | 没在运行 |
| `Active: active (exited)` | oneshot服务执行完（正常） |
| `Active: failed` | 启动失败 ✗ |
| `Loaded: loaded (...; enabled)` | 开机自启 |
| `Loaded: loaded (...; disabled)` | 不开机自启 |

## 查看服务列表

| 命令 | 说明 |
|------|------|
| `systemctl list-units --type=service` | 所有已加载的服务 |
| `systemctl list-units --type=service --state=running` | 正在运行的 |
| `systemctl list-units --type=service --state=failed` | 启动失败的 |
| `systemctl list-unit-files --type=service` | 所有安装的服务 |
| `systemctl list-unit-files --state=enabled` | 开机自启的服务 |

## journalctl 日志

| 命令 | 说明 |
|------|------|
| `journalctl -u 服务名` | 某服务的全部日志 |
| `journalctl -u 服务名 -n 20` | 最后20行 |
| `journalctl -u 服务名 -f` | 实时跟踪（Ctrl+C退出） |
| `journalctl -u 服务名 --since "1 hour ago"` | 1小时内的日志 |
| `journalctl -u 服务名 -p err` | 只看error及以上级别 |
| `journalctl -b` | 本次启动以来的日志 |
| `journalctl -k` | 内核日志 |
| `journalctl --disk-usage` | 日志占用磁盘空间 |

## Service 文件模板

```ini
[Unit]
Description=我的服务
After=network.target

[Service]
Type=simple
ExecStart=/opt/myapp/start.sh
ExecStop=/opt/myapp/stop.sh
Restart=on-failure
RestartSec=5
User=nobody
WorkingDirectory=/opt/myapp

[Install]
WantedBy=multi-user.target
```
