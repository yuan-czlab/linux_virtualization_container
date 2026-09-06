# 实验4：KVM虚拟网络与多机服务验证

> 所属模块：模块一 服务器虚拟化与云资源基础
>
> 建议学时：4学时
>
> 实验方式：个人
>
> 对应教材：《模块一 服务器虚拟化与云资源基础》第4章
>
> 前置实验：实验3
>
> 项目成果：libvirt虚拟网络、客户机地址记录、SSH或HTTP跨机访问和分层排障记录

## 一、项目情境

TechCorp已经通过镜像获得两台KVM客户机，但“虚拟机正在运行”不代表业务网络可用。你需要弄清客户机网卡、虚拟网桥、DHCP、宿主机转发和外部网络的关系，让两台客户机能够通信，并从Rocky KVM宿主机访问客户机中的服务。随后通过一次故障注入建立虚拟网络分层排障路径。

## 二、实验目标

### 1. 知识目标

1. 说明libvirt默认NAT网络的数据路径。
2. 区分虚拟机网卡、TAP接口、虚拟网桥、DHCP租约、NAT和端口发布。
3. 区分客户机间通信、宿主机访问客户机和外部网络访问客户机。
4. 理解虚拟网络故障需要从虚拟机、网卡、网络对象、地址、路由、服务和防火墙逐层排查。

### 2. 能力目标

1. 查看和解释libvirt网络定义、网桥和DHCP租约。
2. 让`course-vm01`与`course-vm02`通过默认虚拟网络通信。
3. 在客户机中发布简单HTTP服务并从另一主机访问。
4. 定位并恢复一种虚拟网卡、地址、服务或虚拟网络故障。

### 3. 素质目标

1. 不以反复重启代替网络证据采集。
2. 不把关闭客户机防火墙作为长期修复方法。
3. 修改虚拟网络前保存XML并明确影响范围。

## 三、知识准备

### 1. 默认NAT网络

```text
course-vm01 eth0 ─┐
                  ├─ 虚拟网桥virbr0 ─ Rocky宿主机转发/NAT ─ VMware网络 ─ 外部网络
course-vm02 eth0 ─┘
```

默认NAT通常可以满足：

- 客户机之间互访；
- Rocky宿主机访问客户机；
- 客户机通过Rocky和VMware继续访问外部网络。

Windows或Ubuntu VMware虚拟机通常不能直接访问嵌套KVM客户机，因为KVM网段隐藏在Rocky内部。外部访问需要路由、端口转发或桥接，本实验不以复杂外部发布为必做目标。

### 2. 分层检查顺序

```text
虚拟机状态
→ libvirt网卡是否连接
→ 虚拟网络是否active
→ 虚拟网桥是否存在
→ 客户机是否获得地址
→ 客户机路由与DNS
→ 目标服务是否监听
→ 客户机防火墙
→ 请求与日志
```

## 四、实验环境

- Rocky KVM宿主机。
- 实验3保留的`course-vm01`和`course-vm02`。
- 两台客户机使用DHCP并具有不同主机身份。
- 教师基础镜像已包含SSH、Python 3或可替代的轻量HTTP服务工具。
- libvirt默认网络名称为`default`。

## 五、项目任务

1. 绘制和验证虚拟网络数据路径。
2. 获得两台客户机的地址。
3. 验证客户机、宿主机和外部访问边界。
4. 发布HTTP测试服务。
5. 完成一次网络或服务故障排查。
6. 保存网络XML和验收证据。

## 六、实验步骤

### 任务一：检查虚拟网络对象

#### 步骤1：建立网络基线

在Rocky宿主机执行：

```bash
mkdir -p ~/vc-course/evidence ~/vc-course/manifests
{
  date -Is
  sudo virsh net-list --all
  sudo virsh net-info default
  ip -brief address
  ip route
} | tee ~/vc-course/evidence/lab04-network-before.txt
```

`default`应为active。若不是：

```bash
sudo virsh net-start default
sudo virsh net-autostart default
```

#### 步骤2：导出并阅读网络XML

```bash
sudo virsh net-dumpxml default \
  | tee ~/vc-course/manifests/default-network.xml > /dev/null
grep -E '<name>|<bridge|<forward|<ip |<range ' \
  ~/vc-course/manifests/default-network.xml
```

记录：

- 网络名称；
- 转发模式；
- 网桥名称；
- 网关地址和前缀；
- DHCP地址范围。

不要假定默认网段一定是`192.168.122.0/24`，以实际XML为准。

#### 步骤3：查看宿主机网络对象

```bash
ip -brief link | grep -E 'virbr|vnet' || true
ip -brief address | grep virbr || true
sudo virsh net-dhcp-leases default
```

`virbr0`等虚拟网桥通常在网络启动后存在；`vnet`接口只有虚拟机运行时才会出现。

### 任务二：启动客户机并获得地址

#### 步骤4：启动两台虚拟机

```bash
sudo virsh start course-vm01 2>/dev/null || true
sudo virsh start course-vm02 2>/dev/null || true
sudo virsh list
```

如果提示已经运行，以`virsh list`状态为准。

#### 步骤5：检查虚拟网卡连接

```bash
sudo virsh domiflist course-vm01
sudo virsh domiflist course-vm02
```

两台客户机的Source应为`default`，MAC地址必须不同。继续获取租约：

```bash
sudo virsh net-dhcp-leases default
sudo virsh domifaddr course-vm01 --source lease
sudo virsh domifaddr course-vm02 --source lease
```

把地址分别记为`<VM01_IP>`和`<VM02_IP>`。

#### 步骤6：从客户机内部确认

分别登录两台客户机：

```bash
hostnamectl --static
ip -brief address
ip route
cat /etc/resolv.conf
```

确认租约地址与客户机实际地址一致。

> **验收点**：两台客户机处于running，连接同一个libvirt网络，MAC和IP均不重复。

### 任务三：验证通信边界

#### 步骤7：从Rocky宿主机访问客户机

```bash
ping -c 3 <VM01_IP>
ping -c 3 <VM02_IP>
ssh student@<VM01_IP> 'hostname; ip -brief address'
ssh student@<VM02_IP> 'hostname; ip -brief address'
```

若ICMP被客户机策略限制，以SSH或目标服务连接作为功能证据，同时记录ICMP限制。

#### 步骤8：验证客户机之间通信

进入`course-vm01`执行：

```bash
ping -c 3 <VM02_IP>
ssh student@<VM02_IP> 'hostname; date -Is'
```

进入`course-vm02`反向验证`<VM01_IP>`。

#### 步骤9：观察外部访问边界

从Ubuntu VMware虚拟机尝试：

```bash
ping -c 2 <VM01_IP> || true
```

如果不能直接访问，不把它判定为KVM网络失败。结合拓扑解释：Ubuntu与KVM客户机之间没有到嵌套NAT网段的直接路由。

### 任务四：发布并验证HTTP服务

#### 步骤10：在course-vm01准备页面

登录`course-vm01`：

```bash
mkdir -p ~/lab04-web
cat > ~/lab04-web/index.html <<'HTML'
<!doctype html>
<meta charset="utf-8">
<title>KVM Network Lab</title>
<h1>KVM_NETWORK_OK</h1>
<p>service=course-vm01</p>
HTML
```

启动只用于实验的HTTP服务：

```bash
cd ~/lab04-web
nohup python3 -m http.server 8080 --bind 0.0.0.0 \
  > ~/lab04-http.log 2>&1 &
echo $! > ~/lab04-http.pid
ss -lntp | grep ':8080'
curl --fail http://127.0.0.1:8080/ | grep KVM_NETWORK_OK
```

#### 步骤11：处理客户机防火墙

如果客户机使用firewalld，按最小范围开放实验端口：

```bash
sudo firewall-cmd --add-port=8080/tcp
sudo firewall-cmd --query-port=8080/tcp
```

先使用运行时规则，实验结束后删除，不永久开放。

#### 步骤12：从另一台客户机和宿主机验证

在`course-vm02`：

```bash
curl --fail http://<VM01_IP>:8080/ | grep KVM_NETWORK_OK
```

在Rocky宿主机：

```bash
curl --fail http://<VM01_IP>:8080/ | grep KVM_NETWORK_OK
```

回到`course-vm01`查看日志：

```bash
tail -n 20 ~/lab04-http.log
```

日志中应出现来自`course-vm02`和Rocky虚拟网桥地址的请求。

> **验收点**：至少两个不同来源成功访问8080，服务日志存在对应请求。

### 任务五：故障注入与恢复

#### 步骤13：记录正常状态

在Rocky宿主机：

```bash
{
  sudo virsh list
  sudo virsh net-info default
  sudo virsh domiflist course-vm01
  sudo virsh net-dhcp-leases default
  curl -sS -o /dev/null -w 'http=%{http_code}\n' http://<VM01_IP>:8080/
} > ~/vc-course/evidence/lab04-good-state.txt
```

#### 步骤14：注入虚拟网卡断开故障

先从`domiflist`记录`course-vm01`的接口MAC，记为`<VM01_MAC>`。执行：

```bash
sudo virsh domif-setlink course-vm01 <VM01_MAC> down
sudo virsh domif-getlink course-vm01 <VM01_MAC>
```

重新访问：

```bash
ping -c 2 <VM01_IP> || true
curl --connect-timeout 3 http://<VM01_IP>:8080/ || true
```

预期：虚拟机仍然running，但网络和HTTP访问失败。这证明“虚拟机状态正常”不能代表业务可用。

#### 步骤15：按层次采集证据

```bash
sudo virsh domstate course-vm01
sudo virsh domiflist course-vm01
sudo virsh domif-getlink course-vm01 <VM01_MAC>
sudo virsh net-info default
sudo virsh net-dhcp-leases default
```

判断根因是客户机虚拟网卡链路为down，不需要重建网络或虚拟机。

#### 步骤16：恢复并复测

```bash
sudo virsh domif-setlink course-vm01 <VM01_MAC> up
sudo virsh domif-getlink course-vm01 <VM01_MAC>
```

等待客户机恢复连接，执行：

```bash
ping -c 3 <VM01_IP>
curl --fail http://<VM01_IP>:8080/ | grep KVM_NETWORK_OK
```

如果地址变化，重新通过DHCP租约获得实际地址后复测。

### 任务六：保存证据

#### 步骤17：生成实验报告数据

```bash
{
  date -Is
  sudo virsh net-info default
  sudo virsh net-dumpxml default
  sudo virsh list --all
  sudo virsh domiflist course-vm01
  sudo virsh domiflist course-vm02
  sudo virsh net-dhcp-leases default
  ip -brief address | grep -E 'virbr|vnet' || true
} > ~/vc-course/evidence/lab04-network-result.txt
```

## 七、独立实践

教师从以下故障中选择一种，学生不得提前知道：

- HTTP进程停止；
- 客户机8080端口规则被删除；
- 虚拟网卡链路断开；
- `default`虚拟网络停止；
- 学生使用了过期的DHCP地址。

必须按照“现象—证据—判断—根因—修复—复测”完成报告，不以重启全部设备作为第一步。

## 八、验收标准

- [ ] 能解释默认NAT网络的数据路径。
- [ ] 已导出并阅读`default`网络XML。
- [ ] 两台客户机连接同一网络且MAC、IP不同。
- [ ] Rocky宿主机能够通过SSH访问两台客户机。
- [ ] 两台客户机能够互访。
- [ ] 8080服务从客户机和宿主机路径验证成功。
- [ ] 日志中存在不同来源请求。
- [ ] 完成一次虚拟网卡或教师指定故障的定位、修复和复测。
- [ ] 能解释Ubuntu不能直接访问嵌套网段时为什么不等于KVM网络失败。

## 九、成果提交

```text
lab04-学号-姓名/
├── kvm-network-topology.png或.pdf
├── default-network.xml
├── lab04-network-before.txt
├── lab04-good-state.txt
├── lab04-network-result.txt
├── http-access-and-log.txt
└── fault-report.md
```

## 十、常见问题

### 1. 客户机没有DHCP租约

检查网络、网卡、链路和客户机DHCP：

```bash
sudo virsh net-info default
sudo virsh domiflist course-vm01
sudo virsh domif-getlink course-vm01 <VM01_MAC>
sudo virsh net-dhcp-leases default
```

通过控制台进入客户机检查`ip -brief address`和NetworkManager，不直接重建磁盘。

### 2. 能ping但不能访问8080

在服务端客户机检查：

```bash
ss -lntp | grep ':8080'
curl -v http://127.0.0.1:8080/
sudo firewall-cmd --query-port=8080/tcp 2>/dev/null || true
tail -n 30 ~/lab04-http.log
```

### 3. 停止default网络失败

活动虚拟机正在使用该网络时，停止会影响所有客户机。本实验不要求学生自行停止整个网络，故障由教师统一注入并说明恢复步骤。

### 4. 地址与上次不同

DHCP地址可能变化。每次以`net-dhcp-leases`和客户机内部地址为准，不在报告中把临时地址写成永久事实。

## 十一、课后思考与拓展

1. NAT网络为什么便于客户机访问外部，却不便于外部直接访问客户机？
2. KVM的`default`网络与VMware NAT网络有什么相同和不同？
3. OpenStack中的网络、子网、端口、安全组和浮动IP分别可以映射到本实验哪些对象？

## 十二、环境保留或清理

在`course-vm01`停止HTTP服务并删除临时运行时端口规则：

```bash
kill "$(cat ~/lab04-http.pid)" 2>/dev/null || true
sudo firewall-cmd --remove-port=8080/tcp 2>/dev/null || true
```

保留两台KVM客户机、默认网络、镜像和证据。实验5继续使用这些成果。

