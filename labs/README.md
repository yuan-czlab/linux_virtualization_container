# 实验资料说明

## 《Linux操作系统》正式实验

64学时正式实验位于`linux/`：

- `linux/00-实验手册编写规范.md`
- `linux/lab01`至`linux/lab20`

学生、教师和课程进度表均以这20篇实验为准。课程使用`rocky-server`、`rocky-web`和Ubuntu 22.04 Desktop `ubuntu-client`三机环境，包含网络、SSH、Nginx、MySQL、MongoDB、Redis、Git、Shell与综合运维。

## 《虚拟化容器技术》正式实验

64学时正式实验位于`virtualization-container/`：

- `virtualization-container/00-实验手册编写规范.md`
- `virtualization-container/lab01`至`virtualization-container/lab11`

这11篇实验按两个模块组织：

| 模块 | 学时 | 实验 |
|---|---:|---|
| 服务器虚拟化与云资源基础 | 24 | 实验1—5 |
| Docker容器化应用构建与交付 | 40 | 实验6—11 |

KVM为嵌套环境中的真实操作；Docker同时使用Rocky和Ubuntu；OpenStack与Kubernetes连接教师预建平台完成基础对象操作。课程镜像以学校Registry为主、`docker save/load`离线包为回退，不依赖Docker Hub持续可用。

## 期末大项目位置

虚拟化容器技术的大项目没有取消，而是放入正式实验流程：实验10完成Web、API、MySQL、Redis四服务Compose应用；实验11是8学时期末综合大项目，包含Kubernetes操作、跨发行版迁移、离线镜像、数据恢复、3—5项故障和个人答辩。

旧版根目录`lab39`至`lab63`以及`../projects/project02`已经删除，需要时可从Git历史恢复。

旧版Linux实验`lab01`至`lab38`及旧实验模板已被新的20篇Linux手册替代并删除，仍可从Git历史恢复。
