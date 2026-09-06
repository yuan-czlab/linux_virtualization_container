# 实验16：MongoDB数据库服务部署与安全配置

> 所属模块：模块三 企业服务部署与综合运维  
> 建议学时：4学时  
> 实验方式：个人  
> 对应教材：《模块三 企业服务部署与综合运维》第27章  
> 前置实验：实验15  
> 项目成果：MongoDB 8.0服务、基础文档数据、管理员和业务用户、身份认证、受限监听及连接故障记录

## 一、项目情境

TechCorp需要使用MongoDB保存结构灵活的设备巡检记录。你需要从Linux运维角度完成MongoDB Community Edition安装、服务管理、基础数据验证、用户认证、监听范围和日志排障。课程不把MongoDB作为数据库开发课程，不深入复杂查询、复制集和分片。

## 二、实验目标

### 1. 知识目标

1. 说明数据库、集合、文档和字段的基本关系。
2. 说明`mongod`、`mongosh`、配置文件、数据目录、日志和27017端口。
3. 说明认证数据库、用户角色、`bindIp`和网络暴露风险。

### 2. 能力目标

1. 检查平台和CPU条件，配置官方MongoDB 8.0仓库。
2. 安装并使用systemd管理mongod。
3. 使用mongosh插入、查询和统计基础文档。
4. 创建管理员与最小权限业务用户并启用authorization。
5. 根据服务、配置、端口、认证数据库和日志排查连接失败。

### 3. 素质目标

1. 不长期保留无认证MongoDB服务。
2. 不把27017直接开放给整个校园网或互联网。
3. 创建首个管理员后再启用认证，避免把自己锁在服务外。
4. 不在脚本、Git或截图中泄露数据库密码。

## 三、知识准备

### 1. 数据组织

```text
MongoDB服务
└── 数据库 company_db
    └── 集合 inspections
        ├── 文档1 {host, status, cpu, time}
        └── 文档2 {host, status, disk, tags, time}
```

文档类似JSON对象，不要求所有文档拥有完全相同字段。MongoDB实际使用BSON保存更多数据类型。

### 2. 连接和认证

```text
mongosh连接主机与27017端口
→ mongod根据bindIp接受或拒绝网络连接
→ 开启authorization后验证用户和认证数据库
→ 角色决定用户可以操作哪些数据库和集合
→ 日志记录启动、连接和错误信息
```

MongoDB用户创建在哪个数据库，通常就需要把该数据库作为`authenticationDatabase`。用户可以在认证数据库中保存身份，同时获得对其他数据库的角色。

### 3. 平台边界

MongoDB 8.0 Community支持RHEL/Rocky Linux 9的64位平台。x86_64上的现代MongoDB还要求CPU提供相应指令集；MongoDB 5.0及以后要求AVX。机房必须在开课前抽测，不能等学生安装后才发现CPU不兼容。

## 四、实验环境

- Rocky Linux 9 x86_64，建议4GB内存。
- 处理器应支持AVX。
- MongoDB Community Edition 8.0官方仓库或教师准备的同版本离线RPM。
- 服务名：`mongod`；端口：27017。
- 配置：`/etc/mongod.conf`；数据：`/var/lib/mongo`；日志通常为`/var/log/mongodb/mongod.log`。

## 五、项目任务

1. 检查系统、架构、CPU、内存和旧安装。
2. 配置官方MongoDB 8.0仓库并安装。
3. 启动mongod，检查配置、端口、数据和日志。
4. 创建company_db和巡检文档。
5. 创建课程管理员和业务账号。
6. 启用认证并验证允许和拒绝。
7. 保持仅本机监听，完成认证或配置故障排查。

## 六、实验步骤

### 任务一：平台和安装前检查

```bash
mkdir -p ~/m1-project/evidence ~/m1-project/backup/mongodb
{
    cat /etc/os-release
    uname -m
    free -h
    grep -m1 -o 'avx' /proc/cpuinfo || true
    rpm -qa | grep -E '^mongodb' || true
    sudo ss -lntp | grep ':27017' || true
} | tee ~/m1-project/evidence/lab16-mongodb-before.txt
```

`uname -m`应为`x86_64`，CPU检查应输出`avx`。没有AVX时停止安装并使用教师验证过的替代机或演示环境，不通过换用未知旧版本绕过。

> **验收点**：平台和CPU满足要求，27017没有未知占用，旧数据已确认。

### 任务二：配置官方仓库并安装

#### 步骤1：创建仓库文件

```bash
sudo tee /etc/yum.repos.d/mongodb-org-8.0.repo > /dev/null <<'REPO'
[mongodb-org-8.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/9/mongodb-org/8.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://pgp.mongodb.com/server-8.0.asc
REPO
```

检查：

```bash
sudo dnf repolist --enabled | grep mongodb
grep -E '^(baseurl|gpgcheck|enabled|gpgkey)=' /etc/yum.repos.d/mongodb-org-8.0.repo
```

#### 步骤2：安装MongoDB

```bash
sudo dnf install -y mongodb-org
rpm -q mongodb-org mongodb-org-server mongodb-mongosh mongodb-database-tools
mongod --version | sed -n '1,10p'
mongosh --version
```

离线环境由教师提供同一8.0系列完整RPM集合。不要混装其他仓库的mongosh或工具包。

> **验收点**：mongod、mongosh和数据库工具均可用，版本来源一致。

### 任务三：启动和检查服务

```bash
sudo systemctl enable --now mongod
systemctl is-active mongod
systemctl is-enabled mongod
systemctl status mongod --no-pager
sudo ss -lntp | grep ':27017'
sudo journalctl -u mongod -n 30 --no-pager
sudo grep -E '^(  port:|  bindIp:|security:|  authorization:)' /etc/mongod.conf || true
```

默认通常只监听127.0.0.1且未启用authorization。当前无认证状态仅用于创建首个管理员，不应长期保留。

检查目录：

```bash
sudo ls -ld /var/lib/mongo /var/log/mongodb
sudo tail -n 30 /var/log/mongodb/mongod.log
```

> **验收点**：mongod为active和enabled，27017仅监听本机地址，数据和日志目录存在。

### 任务四：基础文档操作

#### 步骤3：连接并创建数据

```bash
mongosh
```

在mongosh中：

```javascript
show dbs
use company_db

db.inspections.insertMany([
  {
    host: "rocky-vm",
    status: "ok",
    cpu_percent: 18,
    disk_percent: 42,
    checked_at: new Date()
  },
  {
    host: "db-server",
    status: "warning",
    disk_percent: 81,
    tags: ["database", "capacity"],
    checked_at: new Date()
  },
  {
    host: "web-server",
    status: "ok",
    services: { nginx: "active", api: "active" },
    checked_at: new Date()
  }
])

db.inspections.find()
db.inspections.countDocuments({})
db.inspections.find({status: "warning"})
show collections
db
```

应有3个文档。课程只要求理解运维验证所需的基础操作。

> **验收点**：company_db中存在inspections集合，文档总数为3，能查询warning文档。

### 任务五：创建用户

#### 步骤4：创建课程管理员

仍在认证尚未启用的mongosh中：

```javascript
use admin
db.createUser({
  user: "courseAdmin",
  pwd: passwordPrompt(),
  roles: [
    {role: "userAdminAnyDatabase", db: "admin"},
    {role: "dbAdminAnyDatabase", db: "admin"},
    {role: "readWriteAnyDatabase", db: "admin"}
  ]
})
```

使用教师指定的强实验密码。`passwordPrompt()`避免密码直接出现在屏幕代码和历史中。

#### 步骤5：创建业务用户

```javascript
use company_db
db.createUser({
  user: "inspectionApp",
  pwd: passwordPrompt(),
  roles: [
    {role: "readWrite", db: "company_db"}
  ]
})
db.getUser("inspectionApp")
exit
```

> **验收点**：courseAdmin创建在admin，inspectionApp创建在company_db且只有readWrite角色。

### 任务六：启用身份认证

#### 步骤6：备份配置

```bash
sudo cp -p /etc/mongod.conf ~/m1-project/backup/mongodb/mongod.conf.before-auth
sudo grep -nE '^(net:|  port:|  bindIp:|security:|  authorization:)' /etc/mongod.conf
```

#### 步骤7：编辑配置

```bash
sudo vim /etc/mongod.conf
```

确认或调整为以下结构。YAML使用空格缩进，不能使用Tab；原文件已有`net:`时应修改现有块，不能重复创建第二个`net:`：

```yaml
net:
  port: 27017
  bindIp: 127.0.0.1

security:
  authorization: enabled
```

检查关键行和Tab：

```bash
sudo grep -nE '^(net:|  port:|  bindIp:|security:|  authorization:)' /etc/mongod.conf
sudo grep -n $'\t' /etc/mongod.conf || true
```

#### 步骤8：重启并检查

```bash
sudo systemctl restart mongod
systemctl is-active mongod
sudo ss -lntp | grep ':27017'
sudo journalctl -u mongod -n 30 --no-pager
```

如果启动失败，先看日志和配置缩进。可从备份恢复：

```bash
sudo cp -p ~/m1-project/backup/mongodb/mongod.conf.before-auth /etc/mongod.conf
sudo systemctl restart mongod
```

恢复后仍需重新正确启用认证，不能以无认证状态结束实验。

> **验收点**：认证已启用，服务运行，27017仍只监听127.0.0.1。

### 任务七：验证认证和权限

#### 步骤9：未认证访问

```bash
mongosh --quiet --eval 'db.adminCommand({connectionStatus: 1})'
```

未认证客户端可能建立网络连接并查看有限信息，但读取业务数据应被拒绝：

```bash
mongosh --quiet company_db --eval 'db.inspections.findOne()'
```

#### 步骤10：业务用户认证

```bash
mongosh --authenticationDatabase company_db -u inspectionApp -p company_db
```

按提示输入密码：

```javascript
db.inspections.find()
db.inspections.insertOne({host: "client", status: "ok", checked_at: new Date()})
db.inspections.countDocuments({})
use admin
db.getUsers()
exit
```

业务数据读写应成功，管理admin用户应被拒绝。

#### 步骤11：管理员认证

```bash
mongosh --authenticationDatabase admin -u courseAdmin -p
```

```javascript
use admin
db.runCommand({connectionStatus: 1})
use company_db
db.inspections.countDocuments({})
exit
```

> **验收点**：未认证读取失败，业务用户只能处理company_db，管理员能够查看授权和业务状态。

### 任务八：连接故障排查

#### 步骤12：使用错误认证数据库

```bash
mongosh --authenticationDatabase admin -u inspectionApp -p company_db
```

即使用户名和密码正确，也会因用户实际创建在company_db而认证失败。检查：

```bash
systemctl is-active mongod
sudo ss -lntp | grep ':27017'
sudo tail -n 50 /var/log/mongodb/mongod.log
```

使用正确认证数据库重新连接：

```bash
mongosh --authenticationDatabase company_db -u inspectionApp -p company_db
```

> **验收点**：能根据错误和用户创建位置判断authenticationDatabase错误，而不是修改防火墙。

#### 步骤13：配置错误观察

由教师在备份存在的情况下制造一处YAML缩进或字段错误。学生执行：

```bash
systemctl status mongod --no-pager
sudo journalctl -u mongod -n 60 --no-pager
sudo tail -n 60 /var/log/mongodb/mongod.log
sudo grep -nE '^(net:|  port:|  bindIp:|security:|  authorization:)' /etc/mongod.conf
```

修复后重启并完成认证查询复测。

### 任务九：保存证据

```bash
{
    mongod --version | sed -n '1,5p'
    mongosh --version
    systemctl is-active mongod
    systemctl is-enabled mongod
    sudo ss -lntp | grep ':27017'
    sudo grep -nE '^(net:|  port:|  bindIp:|security:|  authorization:)' /etc/mongod.conf
    getenforce
} > ~/m1-project/evidence/lab16-mongodb-final.txt
```

业务数据统计使用交互认证执行并记录结果，不把密码放入URI。

## 七、独立实践

1. 创建只读用户`inspectionReader`，认证数据库为company_db。
2. 证明它能够查询inspections但不能插入文档。
3. 将一条status为warning的文档改为resolved，并记录修改前后。
4. 使用错误密码、错误端口或错误认证数据库制造一次连接失败。
5. 写出“服务—端口—监听—认证数据库—用户角色—日志”检查结果。

## 八、验收标准

- [ ] 平台为Rocky Linux 9 64位，CPU满足AVX要求。
- [ ] MongoDB 8.0服务器、mongosh和数据库工具来自统一来源。
- [ ] mongod为active和enabled，数据与日志目录已识别。
- [ ] company_db包含inspections集合和不少于3个文档。
- [ ] courseAdmin和inspectionApp创建在正确认证数据库。
- [ ] authorization已启用，未认证业务读取被拒绝。
- [ ] inspectionApp能读写company_db但不能管理admin用户。
- [ ] 27017只监听127.0.0.1，未向整个网络开放。
- [ ] 已完成认证数据库故障和配置故障排查。
- [ ] inspectionReader只读验证完成。
- [ ] 密码未出现在Git、截图、命令URI和提交材料中。

## 九、成果提交

1. `lab16-mongodb-before.txt`和`lab16-mongodb-final.txt`。
2. MongoDB版本、服务、端口、配置和日志位置。
3. 文档插入、查询和统计结果。
4. 管理员、业务用户和只读用户的角色信息，不包含密码。
5. 未认证、正确认证和越权操作验证。
6. 两份故障记录。

## 十、常见问题

### Q1：mongod启动后立即失败

检查YAML缩进、字段名称、数据目录和日志：

```bash
sudo journalctl -u mongod -n 80 --no-pager
sudo tail -n 80 /var/log/mongodb/mongod.log
```

### Q2：提示Illegal instruction

优先检查CPU是否支持AVX和虚拟机是否向客户机暴露该特性。这是平台兼容问题，不是账号或防火墙问题。

### Q3：Authentication failed但服务和端口正常

检查用户名、密码和`--authenticationDatabase`。用户创建在company_db时不能默认用admin认证。

### Q4：启用认证后没有管理员可以登录

说明启用顺序错误。实验必须先创建首个管理员再启用认证。使用配置备份恢复到受控状态，由教师指导创建管理员后重新启用，不能长期关闭认证。

### Q5：远程主机连接不到27017

本实验最终设计为只监听127.0.0.1，这是预期安全结果。需要远程访问时应同时规划bindIp、账号角色、认证、TLS和来源防火墙，不能只把端口开放给所有来源。

## 十一、课后思考与拓展

1. MongoDB文档结构灵活，为什么仍需要数据规范？
2. 认证和授权分别解决什么问题？
3. `bindIp`和firewalld为什么需要同时考虑？
4. 使用`mongodump`和`mongorestore`完成备份恢复时，为什么仍需验证文档数量和内容？

## 十二、环境保留

保留mongod、认证、仅本机监听、company_db和用户，供实验20使用。不要删除管理员账号，不要把27017永久开放到实验网络。

## 十三、官方参考

- [MongoDB 8.0：在RHEL及Rocky Linux安装Community Edition](https://www.mongodb.com/docs/v8.0/tutorial/install-mongodb-on-red-hat/)
- [MongoDB 8.0：基于角色的访问控制](https://www.mongodb.com/docs/v8.0/core/authorization/)
- [MongoDB 8.0：创建数据库用户](https://www.mongodb.com/docs/v8.0/tutorial/create-users/)

