# DeepSeek Harness(DSH)提示词学习 — 会话记录

## 我的提问

我想学习 DeepSeek 的项目 DeepSeek Harness（DSH），重点是 DSH 自身的提示词写法，不是通用提示词工程教程；目标是学完能独立写出稳定可用的 DSH 提示词。

我的水平： 用过 DeepSeek 模型但没用过 DSH
我的使用场景：Agent 工作流

回答前先完成一轮确认（一次性问完，不要提前输出教学内容）：
1. 向我要 DSH 的官方文档或代码仓库地址，或让我粘贴关键内容——你对 DSH 的了解可能有限或已过时，不得凭猜测作答。
2. 若上面两个问题我没有填写，一并问我的水平和使用场景。

确认后，请给出一份一次性、尽可能完整的教程，包含：
- DSH 是什么、与直接调用 DeepSeek 模型的区别（一段话以内，以我提供的资料为准）
- DSH 提示词的结构要素：角色、任务、输出格式、约束各自怎么写，需结合 DSH 自身的机制而非泛泛而谈
- 一个可直接套用的 DSH 提示词模板，需要我填写的部分用 [方括号占位符] 标出
- 一个基于我场景的完整示例：粗糙版 vs 改进版，并说明每处改动的原因
- 3 个最常见的错误写法及对应修正
- 教程中凡不是出自我所提供资料的内容，标注为"通用经验"，不得把猜测当作 DSH 的事实陈述

教程结尾列出值得进一步展开的主题清单，由我决定是否追问、继续多轮深入。

完成标准：我照着模板就能为自己的场景写出一个合格的 DSH 提示词。

---

## Claude 的回复（确认轮）

好的,先按你的要求完成这一轮确认(一次性问完)。我先做了检索,找到了官方仓库,但为避免凭过时或猜测的内容作答,需要你确认以下几点:

**1. 确认对象是不是这个项目**
我检索到的官方仓库是 [github.com/deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)(CLI 名为 `dsh`,口号 "Everything is a Plugin",另有中文架构文档 [docs/architecture.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.zh.md) 和产品页 [deepseek.com/en/harness](https://www.deepseek.com/en/harness/))。请确认这就是你要学的 DSH,还是另一个同名项目?

**2. 资料怎么给我(二选一,或混合)**
- 直接粘贴:README、docs/ 目录里与提示词相关的文档(如系统提示词、插件 manifest、skill 定义格式)、你手头任何内部资料的**关键内容**;
- 或者授权我自行 WebFetch 上述官方仓库的文档来作为教学依据——这样教程会标注哪些内容出自官方文档。

如果你有具体版本号(比如已安装 `dsh --version` 的输出),一并告诉我,以你这份资料为准。

**3. "DSH 提示词"的具体范围**
按我的理解,在 DSH 里写提示词可能涉及好几个层面(系统提示词配置、插件内的指令、skill/任务定义等)——但这正是我不能凭猜测展开的部分。请告诉我你最想先掌握哪一层,还是全部?

**4. Agent 工作流场景的一句话细节**
你的水平(用过 DeepSeek 模型、没用过 DSH)和场景(Agent 工作流)已收到。粗糙版 vs 改进版的示例需要一个具体场景——比如"多步代码审查""定时数据抓取汇总""文档批处理"之类,给我一个你真实想做的,示例会更可用。

你的水平和使用场景不用再填,已按你提供的记录。回复这几点后,我会给出一次性完整教程。

Sources:
- [DeepSeek Harness: Everything is a Plugin (GitHub)](https://github.com/deepseek-ai/deepseek-harness)
- [deepseek-harness README](https://github.com/deepseek-ai/deepseek-harness/blob/master/README.md)
- [DeepSeek Harness 官方产品页](https://www.deepseek.com/en/harness/)
- [DeepSeek Harness 架构文档(中文)](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.zh.md)
