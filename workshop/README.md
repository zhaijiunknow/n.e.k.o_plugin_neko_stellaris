# 创意工坊发布清单

发布时要填的东西都在这个目录里。名称、描述、标签三者互相独立，别混用：

| 位置 | 名字 |
|---|---|
| 工坊条目名 / 启动器列表 | 星辰喵语 顾问语音包 |
| 游戏内 `设置 → 声音 → 顾问语音` | YUI |

## 1. 描述

| 文件 | 用途 |
|---|---|
| `description.zh-CN.bbcode` | 正文，**可直接整段粘贴**（Steam 用 BBCode，不是 Markdown） |
| `description-bridge-section.bbcode` | 仅当上传的包**含事件桥**（整合版）时，接在正文末尾 |

如果上传的是纯语音包（`standalone` 导出，257 个文件、只有 `Sound` 标签、不含 `common/` 与 `events/`），
就**不要**接那段 —— 那个包里根本没有事件桥，写了就是假的。

## 2. 简短描述（启动器上传窗口里的 `Short description` 字段）

```
把《群星》顾问语音全部换成一只傲娇猫娘的中文录音：覆盖原版 82 个声音名、共 248 条，含多套变体，随机抽取。
```

## 3. 标签

- 纯语音包：`Sound`
- 整合版（含事件桥）：`Sound`、`Gameplay`、`Utilities`

## 4. 封面

启动器的发布流程**自动读取 mod 根目录的 `thumbnail.png`**，不需要手动选文件：

```
<mod目录>/thumbnail.png        512×512 PNG，254 KB
```

上限 1 MiB（超过会警告并跳过），格式接受 `jpeg` / `jpg` / `png`。本机其他工坊 mod 的封面缓存实测为
512×512、520×520、500×500 与 958×682 —— 方形是主流，我们这张符合。

想手动选图的话：把 `thumbnail.png` 拷到别处改个名再选即可。

## 5. 发布前必须做的一件事

**先自己进一次游戏，确认日志干净。** 因为：

- `logs/error.log` 里最后一整段（22:10 那次运行）是**修复前**的资产产生的：
  64 行 `No sound scripted for soundoverride`、55,019 行 `unsupported scope`、5 行
  `advisor voice type` 缺本地化。
- 这些都是后来修掉的设计，当前已装的包是新结构（166 条顶层 `sound = {}` 声明
  + 82 条覆盖 = 248 条录音，事件类型按钩子分配）。
- **但修复后的包还没有被游戏加载过。** 游戏上次运行是 01:43，而重建是 03:01 / 04:33。

所以发布前请启动一次游戏、玩几分钟、退出，然后：

```
文档\Paradox Interactive\Stellaris\logs\error.log   → 搜 nekko_stellaris，应为 0 行
                                            → 搜 No sound scripted / unsupported scope，应为 0 行
文档\Paradox Interactive\Stellaris\logs\game.log    → 搜 NEKO|，应能看到事件（含心跳）
```

搜出来是 0 行，才说明这套资产在真机里是好的。在此之前发布，用户拿到的是 5 万行报错。
