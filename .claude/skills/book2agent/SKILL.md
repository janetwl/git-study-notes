---
name: book2agent
description: 把一本书(PDF/EPUB/DOCX)蒸馏成专属"实践教练" agent。用户说"/book2agent"或"喂我一本书/把这本书做成教练"时使用:提取文本→蒸馏知识库→实例化教练 agent→冒烟测试→验收。
---

# book2agent：把书变成可对话的实践教练

## 总目标
产出两样东西，全部落在工作区内：
1. 知识库 `book-agents/<slug>/`（notes/00-overview.md + chNN 逐章笔记 + methods/*.md 方法卡 + quotes.md 金句 + journal.md 由教练自管 + raw/ 提取全文）
2. 教练 agent `.claude/agents/<slug>-coach.md`（由 `book-agents/coach-template.md` 实例化）

默认教练人设（已由 _loki 打磨进模板，除非用户点名改）：**直接开方案、严格只用书中内容、蒸馏笔记为唯一知识源、咨询日志跨会话记忆**。换书只换 4 个占位符。

## 步骤

### 0. 定位输入与环境
- 用户未给路径时，列 `books/` 目录，找尚未处理的文件（对照 `book-agents/README.md` 已入库清单）。
- 工具检查：`pdftotext`(mingw) / `pandoc` / `iconv` / `python`。缺 pandoc 时 docx/epub 用 python zipfile+正则兜底（epub 是 zip 内 xhtml；docx 是 word/document.xml）。

### 1. 建目录与提取
- 取 slug（小写连字符），`mkdir -p book-agents/<slug>/{raw,notes/methods}`。
- **PDF**：`pdftotext -layout "file.pdf" raw/fulltext.txt`
  - ⚠️ 输出常是 cp1252，立即 `iconv -f cp1252 -t utf-8//IGNORE` 原地转 UTF-8，否则后续 Read 报警、引文带乱码。
- **EPUB**：`pandoc -f epub -t plain --wrap=none -o raw/fulltext.txt`
- **DOCX**：`pandoc -f docx -t plain --wrap=none -o raw/fulltext.txt`
- 提取后记录行数/字数；>30k 行的书考虑按部分分章并行蒸馏（派多个 subagent，各领行区间+统一格式规范）。

### 2. 结构测绘
- `grep -nE` 找全部章节标题（英文书：全大写行 `^[A-Z][A-Z&  ]{4,}$`；中文书：`第[一二三四五六七八九十百0-9]+[章节篇]`）。
- 建"标题→行号"地图，划出每章行区间；剔除版权页/序（除非有内容）/广告页。
- ⚠️ 页码在提取中不可靠，**笔记出处一律用"第X部分 · 章节名"**，模板与 agent 提示词中保持此约定。

### 3. 蒸馏（质量核心）
分块通读全文，**读完一部立即写该部笔记**（防遗忘、省 context）。每篇 `chNN-<name>.md` 包含：定位段、核心论点（方法论优先：步骤/适用场景/案例 > 概念）、逐字摘录（引号内必须逐字）、`## 辅导提示`（什么问题→用什么框架）。
然后写：
- `methods/*.md`（8-14 张卡）：一张卡=一个可执行方法，含"何时使用/原理/用法步骤/边界/出处"。卡是教练回答时的第一检索目标。
- `00-overview.md`：全书一句话 + 三部逻辑流 + 章节导航表（"什么问题→看哪章"）+ 方法卡目录（"什么场景→用哪张卡"）+ 使用规则。
- `quotes.md`：精选逐字金句，逐条标（部分·章节）。**教练被授权逐字引用的唯一仓库，零容忍转写。**

引文纪律（本流水线血泪教训）：
- 摘录当场从正在读的行复制，不凭记忆重写；
- 跨段合并用省略号，或拆成两个引号各自注"另句原文"；
- 原书拼写错误原样保留并注（though[sic] 类）；
- 术语列表不要包在引号里冒充原文。

### 4. 引文校验（硬性门禁）
```
python -I book-agents/tools/verify_quotes.py book-agents/<slug>/raw/fulltext.txt book-agents/<slug>/notes
```
必须 `total fails = 0`。有 MISS 就回原文逐条改笔记，不许"顺手改写引文使其匹配"。

### 5. 实例化教练
复制 `book-agents/coach-template.md` → `.claude/agents/<slug>-coach.md`：替换 `{{BOOK_TITLE}} {{BOOK_SLUG}} {{KNOWLEDGE_DIR}} {{BOOK_DOMAIN}}`（路径用正斜杠），删除"实例化方法"节，description 里补 3-5 个该书主题触发词。

### 6. 冒烟测试
⚠️ 新建 agent 类型**要新会话才注册**，本会话不能直接按名调用。用 general-purpose subagent 模拟：prompt = "Read .claude/agents/<slug>-coach.md 作为你的完整 system prompt，严格逐条执行，回答此问题：…"，选一个书中真有答案的问题（最好带陷阱：通识答案与书答案相反，测它跟不跟书走）。
验收清单：不反问／四段结构无额外收尾／逐字引用+章节出处／书外内容标"非书中原文"／书中未涉及如实承认／journal 正确创建追加。

### 7. 收尾
- 冒烟测试产生的 journal 条目：询问用户保留或删除。
- 更新 `book-agents/README.md` 入库登记表。
- 告知用户：新开会话即可"用《书名》教练看看我的问题：…"直接调用。

## 已知坑（勿再踩）
- pdftotext 编码（见上）；-layout 折行会拆开引文单词，校验脚本已按"仅字母数字(+汉字)"匹配穿越。
- 蒸馏笔记"大意"与"逐字"混淆是最大质量风险——中文行文里的意译不要加引号。**实测：即使把这条纪律原文下发给每个 worker，仍会有 ~17% 的"金句/辅导提示"是转写**（第二本书 53 辑抓到 19 处）——所以第 4 步门禁是唯一可信的防线，worker 报告自称"0 不符"也不许跳过。
- 校验脚本的引号配对：ASCII `"` 不分开合，必须按奇偶交替配对取引文；中文弯引号 “ ” 用正则配对。若一行里混用会漏检/误检——笔记统一"外层直引号、内层弯引号"。
- 大书（>20k 行）分区间并行蒸馏很有效（实测 5 路/2.4k token·min 级），分工四要素：行区间+去重规则(普通版/★版)+引文铁律全文照抄+要求回传"跨篇概念清单"（主线程靠它写方法卡，不必重读全书）。
- worker 的临时脚本/分片金句放 notes/ 会污染教练检索——分片必须合并进 quotes.md 后删除，临时脚本目录清理掉。
- Agent 工具报 "not found"：先想 agent 注册时机（扫描发生在会话/命令边界），别改代码。
- journal 里的测试脏数据会被下次咨询当真实历史"跟进"。
- 主线程自己产出的卡片/总览同样要过门禁，无一例外。
