# daily.english

每天 5 个生活与职场高频英语词，音标 + 例句 + 记忆法，5 分钟学完。

> 拾起碎片时光，慢慢变厉害。

每天早上更新一期，5 个新词，永不重复。同步发布到微信公众号「词汇拾光」。

## 目录结构

| 路径 | 说明 |
|------|------|
| `archive/` | 每期 Markdown 归档，可直接阅读 |
| `wechat/words-episode-N.json` | 每期单词原始数据（音标、释义、例句、记忆贴士） |
| `wechat/lesson-episode-N.json` | 情境对话、用法辨析、易错点与练习（第 7 期起） |
| `outputs/words-episode-N.html` | 每期在线页面，带语音朗读 |
| `wechat/push_wechat.py` | 微信公众号推送脚本（建草稿 / 群发 / 自动生成封面） |
| `wechat/brand-copy.md` | 品牌文案：简介、自动回复、底部引导语 |

## 往期

| 期数 | 日期 | 单词 |
|------|------|------|
| [第 10 期：评审前的文件版本与权限](archive/2026-10-03.md) | 2026-10-03 | attachment · outdated · access · revise · resend |
| [第 9 期：买菜订单少货与退款](archive/2026-10-02.md) | 2026-10-02 | receipt · charge · verify · substitute · refund |
| [第 8 期：需求临时增加后的项目取舍](archive/2026-10-01.md) | 2026-10-01 | implement · prioritize · leverage · streamline · accommodate |
| [第 7 期：临时改期的工作沟通](archive/2026-09-30.md) | 2026-09-30 | retrieve · notify · arrange · optional · postpone |
| [第 6 期](archive/2026-09-29.md) | 2026-09-29 | compromise · elaborate · suspend · substantial · distinct |
| [第 5 期](archive/2026-09-28.md) | 2026-09-28 | schedule · confirm · purchase · reliable · maintain |
| [第 4 期](archive/2026-09-27.md) | 2026-09-27 | tackle · ambiguous · amend · diligent · prevalent |
| [第 3 期](archive/2026-09-26.md) | 2026-09-26 | coordinate · estimate · routine · resolve · flexible |
| [第 2 期](archive/2026-09-25.md) | 2026-09-25 | synergy · revenue · nominate · obstacle · genuine |
| [第 1 期](archive/2026-09-24.md) | 2026-09-24 | threshold · incentive · stringent · pragmatic · circumvent |

## 关于自动化

每日流程：选取 5 个新词（与历史去重）→ 围绕具体情境写对话、用法辨析、易错点与练习 → 生成在线页面、归档和公众号草稿 → 由运营者核查语言准确性、实际语境和原创表达后决定是否发布。

自动化仅准备草稿，不自动群发。AI 可以辅助整理，但不能替代真人选题、审稿和发布判断；内容质量与平台推荐量均无保证。

单词去重使用完整历史词库，因此公众号期数与内部累计期数是两套编号，公众号从第 1 期起算。

## 说明

- 公众号正文不支持 JavaScript，语音朗读通过「阅读原文」跳转在线页面实现。
- 仓库不含任何凭据文件（`wechat/config.json` 已在 .gitignore 中排除）。
