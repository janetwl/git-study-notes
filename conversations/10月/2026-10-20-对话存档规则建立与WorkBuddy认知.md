# 对话记录:建立对话存档规则 + WorkBuddy 是什么

- **日期**:2026-10-20
- **工作目录**:E:\git-workspace
- **主题**:① 把"每次对话存到 conversations"固化为长期规则;② 查询 WorkBuddy 是什么

> 本次会话前段(设置默认模型 qwen3.8-flash)已单独存档于 `2026-10-20-设置默认模型-qwen3-8-flash.md`,本文件记录其后的对话。

---

## 1. 用户请求一:导出对话

> 将上述对话保存到 E:\git-workspace\conversations

**处理**:创建 `conversations` 目录,写入 `2026-10-20-设置默认模型-qwen3-8-flash.md`,内容含:原始请求 → 处理过程(读 settings、排查 env 来源、两处编辑、JSON 验证)→ 最终配置 → 生效逻辑 → 经验小结。

## 2. 用户请求二:固化存档规则

> 每次对话都放这里,你给的命名规则很不错,时间+问题简单总结的形式,以后就这样吧

**处理**:
1. 新建长期记忆 `feedback-save-conversation-digest.md`(type: feedback),规则:
   - 对话自然收尾时,写 markdown 记录到 `E:\git-workspace\conversations\`
   - 命名 `YYYY-MM-DD-问题简单总结.md`(中文短语、连字符分隔)
   - 结构:原始请求 → 处理过程 → 最终结果 → 经验小结
   - 同日同主题已有文件 → 更新原文件,不建副本
2. 在 `MEMORY.md` 索引追加一行指针。

**向用户说明的边界**:
- 该记忆只在本工作区(E:\git-workspace)的会话自动加载;
- 会话被硬强关时来不及写——下次开新会说"存一下"可补写,线索全断则如实说明。

## 3. 用户请求三:WorkBuddy 是什么

**处理**:先 Grep 工作区(无匹配,确认不是本地文件/项目)→ WebSearch 中文检索。

**结论**:WorkBuddy 是**腾讯推出的桌面端 AI Agent 办公工作台**,腾讯云 CodeBuddy 团队打造,2026-03-09 发布。定位"专属 AI 同事":

- 自然语言下达任务,自主拆解、规划、调用工具、自我校验,直接操作本机文件
- 交付文档 / 表格 / PPT 等多模态成果;支持多 Agent 并行协作
- 内置混元、DeepSeek、GLM、Kimi 等国产模型;支持 Skills/插件/知识库扩展
- Mac/Windows 桌面端,商用闭源,面向职场人/团队/小微企业,零门槛开箱即用
- 对比:OpenClaw=开源框架面向极客;WorkBuddy=成品面向普通职场人;玩法上与"Claude Code + skills + 网关"同属桌面 Agent 一类

**来源**:
- https://www.codebuddy.cn/work/
- https://www.workbuddy.ai/docs/zh/workbuddy/Overview
- https://cloud.tencent.com/product/workbuddy
- https://zhuanlan.zhihu.com/p/2019479042693314442
- https://www.cnblogs.com/hogwarts/p/20185222
- https://baike.baidu.com/item/WorkBuddy/67362053

## 4. 本次产出文件

| 文件 | 说明 |
|---|---|
| `conversations/2026-10-20-设置默认模型-qwen3-8-flash.md` | 上一主题对话存档 |
| `conversations/2026-10-20-对话存档规则建立与WorkBuddy认知.md` | 本文件 |
| `memory/feedback-save-conversation-digest.md` | 存档规则长期记忆 |
| `memory/MEMORY.md` | 索引追加一行 |

## 5. 经验小结

- "以后每次都 X"类行为约定 → 存 `feedback` 记忆 + 更新 MEMORY.md 索引,新会话自动加载即生效;它依赖我在收尾时执行,硬关会话是死角。
- 回答"是什么"式名词提问:先花一步 Grep 本地(排除"是不是我自己的文件"),再上网查,避免答错语境。
- 同一会话可能有多个主题:存档时按主题分文件,并在文件里互相引用,比一个大杂烩文件更好回看。
