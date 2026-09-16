# 实验16：MongoDB数据库服务部署与安全配置

> 所属模块：模块三 企业服务器部署与综合运维
> 建议学时：4学时
> 实验方式：个人
> 对应教材：3.3 MongoDB文档数据库
> 知识前置：数据库基础、systemd、YAML、认证授权和备份恢复
> 状态依赖：`rocky-server`软件源可用且CPU满足MongoDB要求；不依赖实验15数据
> 建议起点：`Linux-L2`
> 项目成果：company_db文档、认证与RBAC配置、BSON备份和隔离恢复证据

## 一、项目情境

TechCorp需要使用MongoDB保存巡检文档。数据库只供本机应用使用，需要启用身份认证，为管理员和业务程序分配不同角色，并通过逻辑备份证明数据能够恢复。

## 二、实验规则

1. MongoDB最终只监听`127.0.0.1`，不开放27017。
2. 首个管理员创建完成后再启用认证。
3. 密码通过`passwordPrompt()`或`-p`交互输入。
4. 业务用户不授予用户管理权限。
5. 修改`mongod.conf`前保存原文件。
6. 备份必须恢复到`company_restore`验证。
7. YAML使用空格缩进，不使用Tab。

## 三、任务一：平台与安装前检查

确认身份：

```bash
whoami
```

```bash
hostnamectl --static
```

检查架构：

```bash
uname -m
```

检查CPU：

```bash
lscpu
```

检查AVX标志：

```bash
lscpu | grep -i avx
```

检查已有MongoDB包：

```bash
rpm -qa | grep '^mongodb'
```

创建目录：

```bash
mkdir -p ~/m1-project/backup/mongodb
```

```bash
mkdir -p ~/m1-project/evidence
```

## 四、任务二：配置仓库并安装

使用官方仓库或教师提供的同版本镜像。编辑仓库文件：

```bash
sudo vim /etc/yum.repos.d/mongodb-org-8.0.repo
```

官方EL9 x86_64示例：

```ini
[mongodb-org-8.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/9/mongodb-org/8.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://pgp.mongodb.com/server-8.0.asc
```

机房不能访问官方仓库时，把`baseurl`替换为教师提供的已验证镜像或使用完整离线RPM集合。

检查仓库：

```bash
sudo dnf repolist --enabled | grep mongodb
```

安装：

```bash
sudo dnf install -y mongodb-org
```

检查组件：

```bash
rpm -q mongodb-org mongodb-org-server mongodb-mongosh mongodb-database-tools
```

查看版本：

```bash
mongod --version
```

```bash
mongosh --version
```

```bash
mongodump --version
```

## 五、任务三：启动并检查默认边界

启动：

```bash
sudo systemctl enable --now mongod
```

检查：

```bash
systemctl is-active mongod
```

```bash
systemctl is-enabled mongod
```

查看监听：

```bash
sudo ss -lntp | grep ':27017 '
```

预期只监听`127.0.0.1:27017`。

查看配置关键行：

```bash
sudo grep -nE '^(net:|  port:|  bindIp:|security:|  authorization:)' /etc/mongod.conf
```

查看目录：

```bash
sudo ls -ld /var/lib/mongo /var/log/mongodb
```

查看日志：

```bash
sudo tail -n 30 /var/log/mongodb/mongod.log
```

## 六、任务四：创建首个管理员

认证尚未启用，但服务只监听回环地址。在Rocky本机连接：

```bash
mongosh --host 127.0.0.1 --port 27017
```

切换到admin：

```javascript
use admin
```

创建课程管理员：

```javascript
db.createUser({user:"courseAdmin", pwd:passwordPrompt(), roles:[{role:"userAdminAnyDatabase",db:"admin"},{role:"readWriteAnyDatabase",db:"admin"},{role:"dbAdminAnyDatabase",db:"admin"}]})
```

查看用户：

```javascript
db.getUser("courseAdmin")
```

退出：

```javascript
exit
```

## 七、任务五：启用身份认证

### 7.1 保存原配置

检查备份：

```bash
ls -l ~/m1-project/backup/mongodb/mongod.conf.before-auth
```

不存在时创建：

```bash
sudo cp -a /etc/mongod.conf ~/m1-project/backup/mongodb/mongod.conf.before-auth
```

### 7.2 编辑配置

```bash
sudo vim /etc/mongod.conf
```

确保`net`部分包含：

```yaml
net:
  port: 27017
  bindIp: 127.0.0.1
```

在顶层增加：

```yaml
security:
  authorization: enabled
```

检查是否存在Tab：

```bash
sudo grep -n $'\t' /etc/mongod.conf
```

没有输出是预期结果。

### 7.3 重启并检查

```bash
sudo systemctl restart mongod
```

```bash
systemctl is-active mongod
```

失败时查看：

```bash
sudo journalctl -u mongod -n 60 --no-pager
```

需要回退配置时：

```bash
sudo cp -a ~/m1-project/backup/mongodb/mongod.conf.before-auth /etc/mongod.conf
```

回退仅用于修复配置，最终仍需正确启用认证。

## 八、任务六：验证认证并创建业务用户

### 8.1 未认证访问

```bash
mongosh --host 127.0.0.1 --quiet --eval 'db.adminCommand({listDatabases:1})'
```

预期提示需要认证。

### 8.2 管理员认证

```bash
mongosh --host 127.0.0.1 --authenticationDatabase admin -u courseAdmin -p
```

确认身份：

```javascript
db.runCommand({connectionStatus:1})
```

切换业务库：

```javascript
use company_db
```

创建业务用户：

```javascript
db.createUser({user:"inspectionApp", pwd:passwordPrompt(), roles:[{role:"readWrite",db:"company_db"}]})
```

退出：

```javascript
exit
```

## 九、任务七：创建和查询文档

使用业务用户连接：

```bash
mongosh --host 127.0.0.1 --authenticationDatabase company_db -u inspectionApp -p company_db
```

插入第一条：

```javascript
db.inspections.insertOne({host:"rocky-server",service:{name:"mongod",port:27017},status:"ok",tags:["database","course"]})
```

插入第二条：

```javascript
db.inspections.insertOne({host:"rocky-server",service:{name:"mysqld",port:3306},status:"ok",tags:["database","course"]})
```

查询：

```javascript
db.inspections.find()
```

统计：

```javascript
db.inspections.countDocuments({})
```

按嵌套字段查询：

```javascript
db.inspections.find({"service.port":27017})
```

业务用户尝试创建其他用户应失败：

```javascript
db.createUser({user:"shouldFail",pwd:passwordPrompt(),roles:[]})
```

## 十、任务八：认证数据库故障

故意使用错误认证数据库：

```bash
mongosh --host 127.0.0.1 --authenticationDatabase admin -u inspectionApp -p company_db
```

预期认证失败。检查服务仍正常：

```bash
systemctl is-active mongod
```

查看日志：

```bash
sudo tail -n 50 /var/log/mongodb/mongod.log
```

使用正确认证数据库复测：

```bash
mongosh --host 127.0.0.1 --authenticationDatabase company_db -u inspectionApp -p company_db
```

## 十一、任务九：逻辑备份

创建父目录：

```bash
mkdir -p ~/backup-lab/mongodb
```

检查目标是否已经存在：

```bash
ls -ld ~/backup-lab/mongodb/company-dump
```

已存在时不得直接覆盖，应先核对、归档或从课程检查点重新开始。

执行备份：

```bash
mongodump --host 127.0.0.1 --port 27017 --authenticationDatabase company_db -u inspectionApp -p --db company_db --out ~/backup-lab/mongodb/company-dump
```

紧接着查看退出状态：

```bash
echo $?
```

检查文件：

```bash
find ~/backup-lab/mongodb/company-dump -type f -ls
```

## 十二、任务十：误删与隔离恢复

使用业务用户记录数量：

```bash
mongosh --host 127.0.0.1 --authenticationDatabase company_db -u inspectionApp -p company_db --quiet --eval 'db.inspections.countDocuments({})'
```

确认备份成功后删除集合：

```bash
mongosh --host 127.0.0.1 --authenticationDatabase company_db -u inspectionApp -p company_db --quiet --eval 'db.inspections.drop()'
```

恢复到独立数据库：

```bash
mongorestore --host 127.0.0.1 --port 27017 --authenticationDatabase admin -u courseAdmin -p --nsFrom='company_db.*' --nsTo='company_restore.*' ~/backup-lab/mongodb/company-dump
```

检查数量：

```bash
mongosh --host 127.0.0.1 --authenticationDatabase admin -u courseAdmin -p company_restore --quiet --eval 'db.inspections.countDocuments({})'
```

检查关键文档：

```bash
mongosh --host 127.0.0.1 --authenticationDatabase admin -u courseAdmin -p company_restore --quiet --eval 'db.inspections.find().forEach(printjson)'
```

隔离恢复正确后恢复正式库：

```bash
mongorestore --host 127.0.0.1 --port 27017 --authenticationDatabase admin -u courseAdmin -p --drop --nsInclude='company_db.*' ~/backup-lab/mongodb/company-dump
```

最终验证：

```bash
mongosh --host 127.0.0.1 --authenticationDatabase company_db -u inspectionApp -p company_db --quiet --eval 'db.inspections.find().forEach(printjson)'
```

## 十三、任务十一：验证网络边界

在Rocky确认只监听回环地址：

```bash
sudo ss -lntp | grep ':27017 '
```

确认没有27017防火墙开放：

```bash
firewall-cmd --list-all
```

在Ubuntu测试：

```bash
nc -vz -w 3 rocky-server 27017
```

远程连接失败是本实验的安全验收结果。

## 十四、验收标准

- [ ] 体系结构和CPU检查完成。
- [ ] MongoDB服务端、mongosh和Database Tools来自统一来源。
- [ ] mongod为active和enabled。
- [ ] 27017只监听127.0.0.1。
- [ ] authorization已经启用。
- [ ] courseAdmin能够管理用户，inspectionApp仅有company_db的readWrite。
- [ ] 错误认证数据库故障已经验证。
- [ ] 业务用户不能创建用户。
- [ ] 备份退出状态为0且BSON文件存在。
- [ ] company_restore文档数量和关键字段正确。
- [ ] company_db已经恢复。
- [ ] Ubuntu不能直接连接27017。

## 十五、成果提交

1. 平台、版本、服务和监听结果。
2. `mongod.conf`的net与security关键部分。
3. 两个用户的角色证据。
4. 嵌套文档查询和越权失败结果。
5. 错误认证数据库的故障记录。
6. 备份文件、退出状态和隔离恢复结果。
7. 本地监听与Ubuntu远程失败证据。

## 十六、常见问题

### 16.1 mongod启动失败

查看systemd和MongoDB日志，重点检查YAML缩进和Tab。

### 16.2 Illegal instruction

检查宿主CPU和VMware是否向虚拟机暴露所需指令集，不能靠重复安装解决。

### 16.3 Authentication failed

确认用户创建在哪个数据库，并使用正确`--authenticationDatabase`。

### 16.4 Unauthorized

说明身份可能已经验证，但角色不允许当前操作。检查业务用户角色，不随意提升为管理员。

## 十七、环境保留

保留mongod、认证配置、company_db、courseAdmin、inspectionApp和`company-dump`供实验20使用。

MongoDB保持只监听`127.0.0.1`，不添加27017防火墙规则。`company_restore`验收后可以删除。
