# 综合项目：TechCorp基础运维环境与容器化交付

> 准备阶段：U65-U67｜核心实施与答辩：U69-U72（4次大课，8学时）
>
> 类型：2-3人小组｜前置：U01-U67核心内容｜Starter：`projects/project02-starter/`

## 一、项目目标

把Linux、网络、Nginx、MySQL、Redis、Git、Shell、虚拟化和Docker Compose连接为一个可部署、可验证、可排障、可恢复的项目。

```text
client：浏览器、curl、自动验收
   │
   ▼
web-server：Docker Compose
   ├── frontend：Nginx，对外发布Web端口
   ├── backend：Flask/Gunicorn，仅内部访问
   ├── db：MySQL，仅内部访问，数据持久化
   └── redis：仅内部访问，数据持久化

db-server：保存数据库备份、配置仓库和跨学期归档
```

核心项目使用单台Docker主机运行Compose。Compose本身不是跨主机编排工具。能力较强的小组可选做“双Compose跨主机部署”，但不影响核心成绩。

## 二、四次大课安排

| 单元 | 阶段 | 核心任务 | 当堂成果 |
|---|---|---|---|
| U69 | 设计与恢复 | 恢复三机、检查IP/SSH、理解starter、确定端口和验收标准 | 拓扑、IP表、任务分工、环境基线 |
| U70 | 容器化部署 | 修改环境变量、构建镜像、启动四服务、完成功能验收 | Compose运行、acceptance.log |
| U71 | 故障与恢复 | 注入3-5个故障、数据库备份恢复、同步到db-server | 故障报告、备份及恢复记录 |
| U72 | 答辩与归档 | 随机故障、个人问答、OVA/配置/校验归档 | 运维报告和跨学期环境 |

U65-U67已经完成Compose基础和留言板练习，U69不重新从零编写应用代码。

## 三、部署步骤入口

```bash
cp -a projects/project02-starter ~/techcorp-project
cd ~/techcorp-project

cp .env.example .env
vim .env

docker compose config
docker compose up -d --build
docker compose ps

bash ops/acceptance.sh
```

验收输出必须出现：

```text
ACCEPTANCE_OK
```

## 四、10项核心任务

| # | 任务 | 验收标准 |
|---|---|---|
| 1 | 恢复三机环境 | client、web-server、db-server的IP、主机名和SSH符合规划 |
| 2 | 阅读并修改starter | 能解释四服务、两网络、两个数据卷和依赖关系 |
| 3 | 配置管理 | `.env`不提交，`.env.example`不含真实密码 |
| 4 | 镜像构建 | frontend/backend镜像可重复构建，backend以非root用户运行 |
| 5 | Compose部署 | 四服务正常启动，MySQL/Redis/backend不发布宿主端口 |
| 6 | 健康与资源 | 四服务healthcheck合理，CPU/内存限制可解释 |
| 7 | 自动验收 | `ops/acceptance.sh`生成`ACCEPTANCE_OK`和日志 |
| 8 | 故障排查 | 完成3-5个不同层次故障，记录完整证据链 |
| 9 | 备份与恢复 | 数据库备份非空、校验通过、恢复后数据可查询 |
| 10 | 跨学期归档 | 配置仓库、备份、inventory、README、OVA/模板和校验值完整 |

## 五、故障范围

教师从不同层次选择故障，避免全部只是“停止容器”：

| 层次 | 示例 |
|---|---|
| Linux/网络 | IP错误、防火墙拦截、磁盘空间不足 |
| Nginx | 配置语法、proxy_pass目标或端口错误 |
| Compose | `.env`缺失、YAML错误、依赖服务不健康 |
| 容器 | 端口冲突、退出码、资源限制、镜像构建失败 |
| 数据 | MySQL认证错误、Redis密码错误、卷误删后的恢复 |

每个故障记录：现象→影响范围→命令和输出→判断→根因→修复→验证→预防。

## 六、10项交付物

1. `README.md`：架构、成员、部署、验证、恢复和已知问题。
2. 拓扑图、IP规划表和服务端口表。
3. Git仓库：有意义的提交记录和最终tag。
4. `compose.yaml`、Dockerfile和`.env.example`。
5. Nginx配置、Flask代码和数据库初始化脚本。
6. `acceptance.log`与最终`docker compose ps`结果。
7. Shell巡检脚本及执行结果。
8. 3-5份故障排查记录。
9. 数据库备份、SHA256和恢复验证记录。
10. Lab63要求的跨学期归档和恢复README。

截图可以作为辅助证据，但不能替代命令、配置、日志和自动验收文本。

## 七、答辩

- 架构和技术选择：3分钟。
- Compose部署与自动验收：5分钟。
- 随机故障或随机操作：4分钟。
- 个人问答：3分钟。

教师随机指定成员操作，所有成员必须能解释核心架构和安全边界。

## 八、评分

| 指标 | 权重 |
|---|---:|
| 架构、环境与网络 | 15% |
| 容器化与服务功能 | 25% |
| 健康、资源和安全 | 15% |
| 自动验收与故障排查 | 20% |
| 备份恢复与跨学期归档 | 15% |
| 文档、Git与个人答辩 | 10% |

个人最终项目分按照《15-考核量规与成果提交规范》计算。

## 九、选做挑战

将MySQL和Redis部署到db-server，Nginx和Flask部署到web-server：

- 拆分为两个Compose项目，不能声称单个Compose跨主机编排。
- 只允许web-server访问db-server的3306和6379。
- 数据服务端口不得对整个校园网开放。
- 在`.env`配置跨主机地址并完成端到端验收。
- 比较单主机Compose与拆分部署的复杂度、故障面和安全边界。
