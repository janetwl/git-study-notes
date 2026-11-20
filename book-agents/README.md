# book-agents · 书籍教练流水线

## 已入库
| 书名 | slug | 格式 | 入库日期 | 教练 agent | 引文校验 |
|---|---|---|---|---|---|
| The Art of Focus — Dan Koe (2023) | `art-of-focus` | PDF | 2026-10-19 | `.claude/agents/art-of-focus-coach.md` | ✅ 0 fails（2026-10-19 grill 修复 25 处后） |
| 通往财富自由之路 — 李笑来 (2016-17 专栏) | `road-to-financial-freedom` | EPUB | 2026-10-19 | `.claude/agents/road-to-financial-freedom-coach.md` | ✅ 0 fails（53 辑/13 卡/75 金句；修复 19 处工人转写违规） |
| 通往财富自由之路 · 批判性思维向导（同库第二人格） | `road-to-financial-freedom` | EPUB | 2026-10-23 | `.claude/agents/critical-thinking-guide.md`（新增 `notes/principles.md` 21 条可执行原则；日志独立于教练，走 `journal-guide.md`） | ✅ 0 fails（principles.md 入库复验 2026-10-23） |
| 超越感觉：批判性思考指南 — Vincent Ruggiero（中译本） | `beyond-feelings` | EPUB | 2026-11-12 | `.claude/agents/beyond-feelings-guide.md`（思维向导向：`notes/principles.md` 24 条可执行原则+毛病对照表；14 张方法卡；日志走 `journal-guide.md`） | ✅ 0 fails（全库含卡片/principles，两轮修复共 20 处） |

## 目录约定
```
book-agents/
  coach-template.md        # _loki 打磨的教练提示词模板（4 占位符）
  tools/verify_quotes.py   # 引文逐字校验脚本（入库门禁）
  README.md                # 本登记表
  <slug>/
    raw/fulltext.txt       # 提取全文（UTF-8）
    notes/
      00-overview.md       # 全书地图 + 导航
      ch*.md               # 逐章蒸馏笔记（方法论优先，逐字摘录+章节出处）
      methods/*.md         # 方法卡
      quotes.md            # 逐字金句库
      principles.md        # （可选）可执行原则清单，思维向导类 agent 第一检索目标
    journal.md             # 咨询日志（教练自管；同库其他人格用独立文件如 journal-guide.md，避免互相污染）
```

## 用法
- 喂新书：`/book2agent`（或把文件丢进 `books/` 后说"把这本书做成教练"）
- 用教练：**新开会话**后说"用《书名》教练看看我的问题：×××"
