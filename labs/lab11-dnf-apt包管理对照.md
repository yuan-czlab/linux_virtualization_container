# Lab11：dnf 与 apt 包管理练习

> 课时：2 | 类型：个人 | 前置：Lab02（Rocky 可用）+ Lab01（Ubuntu 可用）

## 一、你会学到什么
- 能熟练使用 dnf 完成软件包的搜索、安装、更新、卸载
- 能安装 EPEL 扩展仓库
- 能用 rpm 查看已安装包信息
- 能在 Rocky(dnf) 和 Ubuntu(apt) 之间快速对应

## 二、实验步骤

### 步骤1：认识 Rocky 的软件源

```bash
dnf repolist                              # 已启用的仓库
ls /etc/yum.repos.d/                      # 仓库配置文件位置
cat /etc/yum.repos.d/rocky.repo | head -15
# 观察：name/baseurl/gpgcheck/enabled 字段
```

### 步骤2：安装 EPEL

```bash
sudo dnf install -y epel-release
dnf repolist                              # 多了 epel 和 epel-next
```

### 步骤3：dnf 核心操作

```bash
# 搜索
dnf search nginx
dnf info nginx                            # 版本、描述、大小、来源仓库

# 安装/卸载
sudo dnf install -y nginx vim bash-completion
sudo dnf remove nginx

# 更新
dnf check-update                          # 检查有哪些更新（不装）
sudo dnf update -y                        # 升级所有

# 查找文件属于哪个包
dnf provides /usr/bin/ssh                 # → openssh-clients
dnf provides /usr/bin/which               # → which
dnf provides */nginx.conf                 # → nginx
```

### 步骤4：rpm 包查询

```bash
rpm -qi nginx                             # 包详细信息
rpm -ql nginx | head -20                  # 包安装了哪些文件
rpm -qc nginx                             # 只列配置文件
rpm -qf /etc/nginx/nginx.conf             # 这个文件属于哪个包
rpm -qR nginx                             # 依赖哪些包
```

### 步骤5：dnf ↔ apt 对照（在 Ubuntu 上操作或对照表格）

| 操作 | Rocky (dnf) | Ubuntu (apt) |
|------|------------|--------------|
| 更新包索引 | `dnf check-update` | `sudo apt update` |
| 升级所有包 | `sudo dnf update -y` | `sudo apt upgrade -y` |
| 搜索包 | `dnf search nginx` | `apt search nginx` |
| 查看包信息 | `dnf info nginx` | `apt show nginx` |
| 安装包 | `sudo dnf install -y nginx` | `sudo apt install -y nginx` |
| 卸载包 | `sudo dnf remove nginx` | `sudo apt remove nginx` |
| 已安装列表 | `dnf list installed` | `apt list --installed` |
| 文件属于哪个包 | `rpm -qf /path` | `dpkg -S /path` |
| 包安装的文件 | `rpm -ql 包名` | `dpkg -L 包名` |
| 清理缓存 | `sudo dnf clean all` | `sudo apt clean` |

---

## 五、练习题

### 练习1：查找命令来源（15分）

找出以下命令/文件由哪个软件包提供：

| 命令/文件 | 命令 | 答案（软件包名） |
|-----------|------|----------------|
| /usr/bin/vim | | |
| /usr/sbin/tcpdump | | |
| /usr/bin/ssh | | |
| /usr/share/doc/ | | |

### 练习2：离线环境安装（25分）

某服务器不能联网。在有网的 Rocky VM 上：
1. 用 `dnf download --resolve --destdir=/tmp/offline-nginx nginx` 下载 nginx 及所有依赖的 rpm
2. 统计下载了多少个 rpm 包
3. 写出在离线服务器上安装这些包的命令
4. `rpm -ivh *.rpm` 和 `dnf localinstall *.rpm` 有什么区别？

### 练习3：dnf history（20分）

1. 用 `dnf history` 查看最近 5 次 dnf 操作
2. 用 `dnf history info 编号` 查看某次操作的详情
3. 如果用 `sudo dnf history undo 编号`，会发生什么？

### 练习4：仓库管理（20分）

1. 临时禁用 EPEL 仓库：`sudo dnf config-manager --set-disabled epel`
2. 搜索 htop → 能找到吗？
3. 重新启用 EPEL → 搜索 htop → 能找到吗？
4. 写出一条命令：只从 EPEL 仓库安装某个包（不从其他仓库找）

### 练习5：Rocky↔Ubuntu 命令互译（20分）

写出以下 Ubuntu apt 命令对应的 Rocky dnf 命令：

| Ubuntu (apt) | Rocky (dnf) |
|-------------|------------|
| `sudo apt update` | |
| `sudo apt install nginx` | |
| `apt search redis` | |
| `apt show nginx` | |
| `apt list --installed` | |
| `sudo apt autoremove` | |

---

## 六、验收标准
- [ ] dnf search/info/install/remove/update 都能独立操作
- [ ] rpm -qi/-ql/-qf 三个查询命令熟练
- [ ] dnf provides 能找到任意文件的来源包
- [ ] 练习 1-5 全部完成
