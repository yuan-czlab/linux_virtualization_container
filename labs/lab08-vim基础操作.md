# Lab08：vim 基础操作

> 课时：2 | 类型：个人 | 前置：Lab04（会用终端即可）

## 一、你会学到什么
- 能用 vim 完成文件的新建、编辑、保存、退出
- 理解 vim 三种模式（Normal/Insert/Visual）以及如何切换
- 能用 hjkl 和常用快捷键在不碰鼠标的情况下高效移动光标
- 能独立完成一个配置文件的基本编辑

## 二、实验环境
- Rocky Linux 9 VM

## 三、为什么必须学 vim

```
1. 服务器只有命令行，没有 gedit/VS Code
2. 所有 Unix/Linux 默认装了 vi（vim 的祖先），一定有
3. visudo、crontab -e、git commit 默认打开的都是 vim
4. 你不会 vim，连退出都要百度——这很尴尬
```

本实验的目标不是让你变成 vim 高手，而是：
- **能进去、能编辑、能保存、能退出**
- **遇到 vim 不会恐慌**

## 四、实验步骤

### 步骤1：第一次进入和退出 vim

```bash
# 打开 vim（创建一个新文件）
vim myfirst.txt
```

你现在进入了 vim。屏幕底部应该显示 `"myfirst.txt" [New File]`。

**现在的状态：Normal 模式。你不能直接打字。**

试试以下操作（在 Normal 模式下直接按键，不需要加冒号）：

| 按键 | 效果 |
|------|------|
| `i` | 切换到 Insert 模式（左下角出现 -- INSERT --） |
| 随便打字 | 正常输入文本 |
| `Esc` | **回到 Normal 模式**（最重要的一步！） |
| `:w` 然后 Enter | 保存（write） |
| `:q` 然后 Enter | 退出（quit） |
| `:wq` 或 `ZZ` | 保存并退出 |

完整流程：
```
vim myfirst.txt  →  i  →  打字  →  Esc  →  :wq  →  Enter
(打开)            (编辑)  (写内容) (退出编辑) (保存退出)
```

> ⚠️ **救命口诀**：任何时候按 Esc 能回到 Normal 模式，然后 `:q!` 强制退出不保存。

> **验收点**：能独立完成"创建文件 → 编辑 → 保存退出 → `cat` 验证内容"的完整流程。

### 步骤2：三种模式的肌肉记忆

```bash
vim modes.txt
```

按 `i` 进入 Insert 模式，输入 5-10 行随便什么内容，然后 Esc 回 Normal。

**三种模式的关系**：
```
          i / a / o
  Normal ──────────→ Insert
    ↑                  │
    └──── Esc ─────────┘
    
    v / V / Ctrl+V
  Normal ──────────→ Visual
    ↑                  │
    └──── Esc ─────────┘
```

练习模式切换（在 Normal 模式下）：
```bash
i        # 进入 Insert，在光标前插入
a        # 进入 Insert，在光标后插入
o        # 进入 Insert，在下一行新开一行
O        # 进入 Insert，在上一行新开一行
Esc      # 回到 Normal（每完成一次编辑就按）

# 在 Visual 模式下
v        # 字符可视化模式
V        # 行可视化模式
Ctrl+v   # 块可视化模式
Esc      # 回到 Normal
```

> **验收点**：能自如地在 i → 打字 → Esc → :w 之间切换，不犹豫。

### 步骤3：Normal 模式下的移动（不碰鼠标）

```
        k (上)
h (左)           l (右)
        j (下)
```

练习：用 hjkl 在刚才的文件中移动光标 2 分钟，直到手指记住：

```bash
# 更多移动命令（Normal 模式）
w           # 跳到下一个单词开头
b           # 跳到上一个单词开头
e           # 跳到单词结尾
0           # 跳到行首
$           # 跳到行尾
gg          # 跳到文件开头
G           # 跳到文件末尾
:n          # 跳到第 n 行（例如 :10 跳到第 10 行）
Ctrl+f      # 向下翻一页（Forward）
Ctrl+b      # 向上翻一页（Backward）
```

练习文件：先搞一个长一点的测试文件
```bash
# 在 vim 里执行（Normal 模式输入）：
:r !seq 1 50
# 这会把 seq 1 50 命令的输出（数字 1 到 50）插入到当前文件
# 然后练习：gg 跳到开头，G 跳到末尾，:25 跳到第 25 行
```

> **验收点**：不看文档，能用 hjkl/w/b/gg/G 在文件中高效移动。

### 步骤4：Normal 模式下的编辑命令

```bash
vim editing.txt
```

先输入一些内容（用 i 进入 Insert 模式，粘贴或随意输入 20 行测试文字）：

然后 Esc 回到 Normal 模式，依次练习：

| 命令 | 说明 | 记忆方法 |
|------|------|---------|
| `x` | 删除光标所在字符 | 像用橡皮擦 |
| `dd` | 删除整行 | delete line |
| `yy` | 复制整行 | yank line |
| `p` | 粘贴到光标后 | paste |
| `P` | 粘贴到光标前 | |
| `u` | 撤销 | undo |
| `Ctrl+r` | 重做 | redo |
| `3dd` | 删除 3 行 | 数字+命令=重复 |
| `3yy` | 复制 3 行 | |
| `dw` | 删除一个单词 | delete word |
| `cw` | 修改一个单词（删除+进入 Insert） | change word |
| `ciw` | 修改光标所在的单词 | change inner word |
| `o` | 下一行新开一行（进入 Insert） | open below |
| `O` | 上一行新开一行（进入 Insert） | open above |
| `>>` | 向右缩进 | |
| `<<` | 向左缩进 | |
| `J` | 合并下一行到当前行 | join |

重点练习——组合玩出花：
```bash
# 复制 5 行，然后粘贴
5yy  →  p

# 删除 3 个单词
3dw

# 修改从光标到行尾的内容
C

# 删除从光标到行尾
D
```

> **验收点**：能不查资料完成 dd/yy/p/u/o 的操作。

### 步骤5：搜索与替换

```bash
# 打开一个有内容的文件
vim /etc/ssh/sshd_config
```

在 Normal 模式下：
```bash
# 搜索
/Port          # 向下搜索"Port"
?Port          # 向上搜索"Port"
n              # 跳到下一个匹配
N              # 跳到上一个匹配

# 关闭高亮（搜完之后关键词一直亮着很烦）
:noh           # no highlight

# 替换（整篇）
:%s/#Port/Port/g     # 把所有的 #Port 替换为 Port
                      # % = 所有行
                      # s = substitute
                      # g = 这一行里替换所有匹配（不加 g 只替换每行第一个）

# 替换（确认模式）
:%s/yes/no/gc        # 每个替换都问你是否确认（y/n/q）
```

练习：
```bash
# 1. 用 / 搜索 "PermitRootLogin"，用 n/N 浏览所有出现位置
# 2. 统计 sshd_config 里有多少行注释（以 # 开头的行）
#    Normal 模式输入：:%s/^#.*//n
#    这个命令不会真正替换（n 标志表示计数），会告诉你注释行数
# 3. :q! 退出（不要保存！这是系统配置文件，不要修改）
```

> **验收点**：能用 `/关键字` 搜索，用 `n` 浏览匹配，用 `:noh` 取消高亮。

### 步骤6：实战——编辑一个配置文件

```bash
# 创建一个测试用的"配置文件"
cd /tmp
vim myserver.conf
```

在 vim 中输入以下内容（带错误，你需要修改）：
```
# My Server Config

server_name=ld_server
port=8080
max_connections=100
#debug_mode=false
log_path=/var/log/myserver/
```

练习编辑任务：
```bash
# 1. 修改 server_name：光标移到 ld_server，按 ciw 删除并输入 prod-server-01
# 2. 修改端口号 port=8080 为 port=9090
# 3. 取消注释 debug_mode（删除 #）
# 4. 在第 4 行后插入一行：listen_address=0.0.0.0
# 5. 在文件末尾加一行：admin_email=admin@example.com
# 6. 把 log_path 从 /var/log/myserver/ 改为 /data/logs/myserver/
# 7. 保存退出，cat 验证内容正确
```

> **验收点**：不退出 vim 的情况下，完成全部 7 个编辑任务。

### 步骤7：分屏编辑

```bash
# 在 vim 中（Normal 模式）
:split /etc/hostname       # 水平分屏打开另一个文件
# Ctrl+w 然后按 j/k 在上下窗口间切换

:vsplit /etc/hosts         # 垂直分屏
# Ctrl+w 然后按 h/l 在左右窗口间切换

:close                     # 关闭当前窗口
:only                      # 只保留当前窗口，关闭其他
```

> **验收点**：能分屏同时编辑两个文件，并在窗口间切换。

## 五、验收标准
- [ ] 能完成 vim 的完整流程：打开 → i编辑 → Esc → :wq保存退出
- [ ] 遇到 vim 不会恐慌，知道 `:q!` 强制退出
- [ ] 能区分三种模式（Normal/Insert/Visual），能随时按 Esc 回到 Normal
- [ ] 能使用 dd/yy/p/u/o 完成常用编辑操作
- [ ] 能用 `/关键词` 搜索，用 `:%s/old/new/g` 全局替换
- [ ] 完成"实战编辑配置文件"的 7 个任务

## 六、常见问题

**Q: 不小心按了 Ctrl+S 导致终端卡死？**
A: Ctrl+S 是"暂停输出"（XON/XOFF 流控），按 Ctrl+Q 恢复。这个坑几乎所有新手都会踩。

**Q: 怎么选中多行复制粘贴？**
A: 方法1：Normal 模式 `V` 进入行选中 → j/k 选中多行 → `y` 复制 → 移动光标 → `p` 粘贴。方法2：`5yy` 复制当前行下面 5 行。

**Q: vim 粘贴外部内容时缩进乱了？**
A: vim 的自动缩进干扰了粘贴。解决办法：粘贴前 `:set paste`，粘贴完 `:set nopaste`。

**Q: 怎么显示行号？**
A: `:set number`（简写 `:set nu`）。要永久生效，在 `~/.vimrc` 中加 `set number`。

**Q: vim 学得会但用不熟怎么办？**
A: 正常。vim 是肌肉记忆，不是知识记忆。建议：**强制自己一周内只用 vim 编辑文件**，不用 nano、不用 VS Code 远程编辑。一周后速度就上来了。推荐装 `vimtutor`（vim 自带教程）：命令行输入 `vimtutor`。

## 七、vim 速查卡（打印给学生）

```
┌────────────── vim 保命三连 ──────────────┐
│ Esc  →  回到 Normal 模式                  │
│ :q!  →  强制退出（放弃修改）              │
│ :wq  →  保存并退出                        │
├────────────── 基本操作 ──────────────────┤
│  i   插入    a   追加    o   新行         │
│  x   删字符  dd  删行    u   撤销         │
│  yy  复制行  p   粘贴                      │
├────────────── 移动 ──────────────────────┤
│  hjkl  左下上右                           │
│  w/b   下一词/上一词                      │
│  0/$   行首/行尾                          │
│  gg/G  文件头/文件尾                      │
├────────────── 搜索替换 ──────────────────┤
│  /xxx  搜索      n/N  下一/上一匹配       │
│  :%s/old/new/g  全局替换                  │
└──────────────────────────────────────────┘
```
