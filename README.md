# 星辰喵语 — 把 N.E.K.O 接进《群星》

一个 N.E.K.O 插件，外加它生成的《群星》顾问语音包工具链。

> 名字的三个位置是**不同的**，这是刻意的：
>
> | 位置 | 名字 | 为什么 |
> |---|---|---|
> | N.E.K.O 插件列表 | 星辰喵语 | 工具的名字 |
> | 创意工坊 / 启动器里的 mod | 星辰喵语 顾问语音包 | 别人在工坊只看名字决定点不点，所以写全 |
> | 游戏内 `设置 → 声音 → 顾问语音` | YUI | 那个列表全是「灵能」「军人」这种短裸名 |

---

## 这个项目做两件事

| | 游戏内顾问语音 | 实时解说 |
|---|---|---|
| 声音从**哪**出 | **游戏自己的音频通道** | N.E.K.O 的音频通道 |
| 时机 | 游戏事件触发那一刻，精确 | 读完日志后 1~3 秒内 |
| 内容 | 预生成，但**可以在游戏运行中被改写** | **每句都是当场生成** |

**产出是一个 mod，两半都装在同一个文件夹里**：

```
nekko_stellaris_advisor/
├── sound/              顾问语音：248 条录音 + soundgroup + voice type
├── localisation/       "YUI" 在游戏下拉框里的显示
├── gfx/                顾问图标
├── events/             ← 事件桥：47 个隐藏事件，只写日志
└── common/on_actions/  ← 事件桥：把那些事件挂到原版钩子上
```

之所以合成一个而不是拆成两个：**静默的半装**（只勾语音包忘了勾桥接，一切看起来都正常，只是解说变含糊——这种症状没人会来报）和**重复挂载**（两个 mod 给同一个 on_action 追加事件时，引擎会追加两次，每个事件触发两遍）。

---

## 目录

```
plugin/                 N.E.K.O 插件本体
├── plugin.toml         清单 + [stellaris] 配置
├── __init__.py         入口（12 个 entry + 3 个 lifecycle）
├── core/
│   ├── audiowav.py     任意 WAV → PCM16 单声道 44100
│   ├── tts.py          free 通道流式 TTS + 断点续传缓存 + 自适应节流
│   ├── ddsicon.py      手写未压缩 BGRA DDS（对齐原版 3492 字节）
│   ├── voicepack.py    语音包规划与产出（含 asset / localisation / 图标）
│   ├── combined.py     把语音包与事件桥合成一个 mod
│   ├── standalone.py   导出不依赖插件的独立语音包
│   ├── bridge.py       事件桥 mod 生成
│   ├── installer.py    安装/卸载 + Paradox 启动器播放集登记
│   ├── gamelog.py      game.log 增量尾随与解析
│   ├── livevoice.py    运行时再生：游戏开着时改写顾问将要说的话
│   ├── policy.py       解说策略与防刷屏
│   └── nekoconfig.py   复用用户 N.E.K.O 配置与路径发现
├── data/               从游戏里实测提取的数据（见下）
├── i18n/               插件自身的界面文案
├── assets/             顾问图标原图：生成游戏内 DDS 与工坊缩略图的来源
├── build_cli.py        不依赖宿主的命令行入口
└── smoke_offline.py    198 项离线回归检查（在宿主里跑是 200 项）
```

### `data/` 里的东西是提取出来的，不是猜的

| 文件 | 来源 |
|---|---|
| `advisor_sounds.json` | 解析《群星》4.5.2 的 `sound/soundeffects.asset`，得到默认顾问组能触及的 **82 个声音名** |
| `on_action_hooks.json` | 审计 `common/on_actions/` 得到 63 个钩子（61 个 verified），含作用域与事件类型 |
| `on_action_brief.md` | 审计结论与踩坑 |
| `lines.zh-CN.json` | 台词表：82 key / 386 条 |
| `persona_brief.md` | 人设结论（自称「本喵」、称玩家「碳基生物」的来源） |

游戏更新后这些可以**重新提取**，而不是靠猜。

---

## 安装

插件要装进 N.E.K.O 的插件目录：

```
<N.E.K.O>/plugin/plugins/neko_stellaris/
```

也就是把本仓库 `plugin/` 里的**内容**拷进去（目录名必须是 `neko_stellaris`，因为 `plugin.toml` 里的入口是 `plugin.plugins.neko_stellaris:...`）。

> N.E.K.O 也支持把外部目录注册成开发源（development registration），但那条路径要求入口写成 `plugins.<id>` 命名空间，和内置位置的写法不同，且需要在运行中的宿主里注册。这里不依赖它。

游戏 mod 由插件生成并安装，不需要手工放置。想手工用也可以：

```
python plugin/build_cli.py standalone         # 导出纯语音包 + zip，可自己装/发给别人
python plugin/build_cli.py combined --install # 生成整合版并装进游戏
python plugin/build_cli.py check              # 游戏里那份是否已过期
```

---

## 底线：198 项离线检查

```
python plugin/smoke_offline.py
```

**不联网、不碰 TTS、不碰游戏**，断言的是产出的**格式**——因为这里才是昂贵的错误所在。

`build_cli.py` 和 `smoke_offline.py` 都按**自己所在目录**去找 `core/`，所以在「已装进宿主」和「本仓库」两种布局下都能直接跑，不需要 N.E.K.O 在场。唯一的例外是有两项检查要经插件入口读 `Settings`，那需要宿主 SDK；在本仓库里跑时会**显式报告跳过**，结果是 198 项通过 + 2 项跳过，而不是静默少算两项。这条不变量本身也在检查里（`layout independence` 一节），所以它不会再悄悄退化。

这套检查在开发过程中抓到过这些真 bug：

- `soundfileoverrides` **只能覆盖已存在的名字，不能创建新名字**（`_02` 及以后的变体全被引擎拒绝，error.log 里 64 行 `No sound scripted`）
- 事件类型与作用域不匹配（`country_event` 挂在行星钩子上，error.log 里 **55,019 行** `unsupported scope`）
- 本地化文件头漏了 `l_` 前缀（`Missing localisation for advisor voice type`）——**而当时的测试断言写的是错的写法，把它固化了下来**
- 去重逻辑把「从未见过」当成「在 t=0 见过」
- 两条缓存路径各写了一遍，导致 CLI 重建时从零重打 TTS
- 质量契约一类的设计错误：`check_freshness` 原来接受调用方传入的 plan，于是"改了一行台词"报告成"0 条要重做"——**在这个函数唯一要回答的问题上给了错误答案**

---

## 已实测确认的游戏事实

前两版都在这上面栽过，每条都有 `error.log` / `game.log` 作为证据：

| 事实 | 证据 |
|---|---|
| **引擎在播放时从磁盘读 wav**：名字不变、只改内容，即刻生效 | 游戏运行中覆盖 248 个槽位，触发顾问语音听到的却是探针句；进程 PID 未变 |
| **`soundfileoverrides` 不能创建新名字** | 见上 |
| **事件类型必须匹配作用域** | 见上；正确类型可从原版机械读取 |
| **on_action 的 MERGE 语义成立**（重复顶层名即追加） | `game.log` 里出现 `NEKO\|v1\|heartbeat\|` |
| **`log` 里的数据引用有效** | `NEKO\|v1\|first_contact_with_empire\|a=联合圣约国\|b=不明帝国\|system=泰伊格\|` |
| 玩家过滤正确 | 642 条桥接事件全部只属于玩家国家，0 条 AI 国家漏入 |
| **不存在的作用域链会让脚本报错而不是静默跳过** | `owner = { … }` 用在刚勘测完（尚未被殖民）的行星上，引擎每次触发都记一行 `Invalid context switch [owner] from <planet>` —— 单个事件在一局里刷了 **32,383 行**。同理 `on_destroying_station`（中立站无主）。修法是先 `exists = owner` 再切换，勘测那条则改用原版注释写明的作用域（`From = Country`） |
| **自造的声音名绝不能和原版同名** | 顶层 `sound` 块是全局的，重名时先声明者胜：我们的变体名 `advisor_..._02` 与 `soundgroups.asset` 里为流派语音池准备的别名撞名，引擎报 102 行 `already scripted` 并保留原版那份，于是每个池子 4 个候选里 3 个播的是原版顾问语音（也就是「有些语音漏了」）。组内的 `soundfileoverrides` / `soundeffectoverrides` 才是组作用域 |
| **手装的本地 mod 在启动器里没有封面可设** | 启动器只在有 `thumbnailUrl`（Steam/PDX 服务）时才填 `thumbnailPath`；它对本地 mod 的那条 metadata 路径要求 `formatVersion == 1.1`，而它自己的游戏注册表里 `stellaris` 是 `formatVersion: null`。描述符里的 `picture=` 它根本不读（29 MB 的启动器包里 0 命中） |

---

## 已知限制

1. **逐事件实时做不到**：游戏在事件后约 100 毫秒就播了，而生成一句要 2~4 秒。这是结构性的。现在的做法是**池轮换**：每次事件只重写该池的一个槽位，K 次事件覆盖整池。
2. **语音包尚未在真机游戏里验证过**（mod 结构、资产语法、DDS 格式都是逐字段对着原版核出来的）。
3. 屏幕上的**顾问通知文本仍是原版的**——游戏只让 mod 换音频，不让换那行字。
4. **天灾降临、经济赤字、游戏结束没有 on_action 可挂**。
5. 免费 TTS 端点的限流**罚的是连接数、不是请求速率**：实测单连接连发 16 条零错误，而每条重开连接（哪怕同时只开 2 条）约一半请求会吃到 `1008 Too many concurrent requests`，每次重试还要几秒退避。现在整批只开一个连接并复用，248 条约 3 分钟（改动前约 8~9 分钟）。
6. **手装的本地 mod 在启动器里没有封面**：这是启动器的限制，不是 mod 能设的——它只在有 `thumbnailUrl`（走 Steam/PDX 服务）时才填封面，本地 mod 的 `.metadata/thumbnail.png` 那条路又要求 `formatVersion == 1.1`，而群星在启动器注册表里是 `null`。发布于创意工坊后封面就会正常显示（工坊预览图用的正是 mod 根目录的 `thumbnail.png`，上限 1 MiB）。
7. **发布之后，本地那份会被启动器删掉。** 订阅自己的工坊条目时，启动器把本地安装"迁移"走：删掉 `Documents/.../mod/<mod_id>/` 与它的 `.mod` 存根，改为启用 `mod/ugc_<id>.mod`。此后只有 Steam 会写那个目录，所以工具链不再假设文件在自己放过的地方——它会通过存根里的 `path=` 找到工坊副本，把它当作"已装包"（`check` 报的是它的状态），并且**拒绝再装第二份**（同名两份会同时出现在启动器列表里，两个都勾选时桥接的钩子被追加两次，每个事件触发两遍）。要更新工坊版本请重新上传；确实需要本地一份做测试，用命令行 `build_cli.py combined --install`。

---

## 许可

Apache-2.0。插件源码派生自 [N.E.K.O](https://github.com/Project-N-E-K-O)，文件头保留原版权声明；详见 `LICENSE` 与 `NOTICE`。

《群星》顾问语音包本身是**纯游戏数据**（音频 + 资产 + 本地化），不包含也不依赖本程序的任何代码，可独立分发。
