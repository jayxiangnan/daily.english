# daily.english

每天 5 个生活与职场高频英语词，音标 + 例句 + 记忆法，5 分钟学完。

> 拾起碎片时光，慢慢变厉害。

公众号「词汇拾光」采用每日主副两篇内容：头条是「每日 5 词」，次条是英文全文在前、完整中文译文在后的历史阅读。两篇同属一个目标日期，自动化只准备草稿，由运营者审阅后决定是否发布。

## 目录结构

| 路径 | 说明 |
|------|------|
| `archive/` | 每期 Markdown 归档，可直接阅读 |
| `wechat/words-episode-N.json` | 每期单词原始数据（音标、释义、例句、记忆贴士） |
| `wechat/lesson-episode-N.json` | 情境对话、用法辨析、易错点与练习（第 7 期起） |
| `outputs/words-episode-N.html` | 每期在线页面，带语音朗读 |
| `wechat/push_wechat.py` | 微信公众号草稿脚本，支持单篇及「单词头条 + 历史次条」多图文 |
| `wechat/history-YYYY-MM-DD.json` | 每日英文历史的双语正文、练习和来源数据，独立于每日五词期数 |
| `wechat/history_article.py` | 生成历史文章归档、页面与多图文次条素材 |
| `wechat/history-card-YYYY-MM-DD.json` | 含完整双语正文和封面的公众号次条素材 |
| `wechat/brand-copy.md` | 品牌文案：简介、自动回复、底部引导语 |

## 往期

| 期数 | 日期 | 单词 |
|------|------|------|
| [第 32 期：Word 作业转 PDF 后提交](archive/2026-10-28.md) | 2026-10-28 | format · convert · preview · upload · submit |
| [第 31 期：酒店夜间噪声与换房](archive/2026-10-27.md) | 2026-10-27 | noise · disturb · report · offer · switch |
| [第 30 期：登机口变更后的信息核对](archive/2026-10-26.md) | 2026-10-26 | announcement · gate · screen · board · depart |
| [第 29 期：新毛衣分开洗](archive/2026-10-25.md) | 2026-10-25 | label · fabric · shrink · separate · gentle |
| [第 28 期：视频会议回声排查](archive/2026-10-24.md) | 2026-10-24 | echo · speaker · microphone · mute · headset |
| [第 27 期：打印机卡纸后核对打印件](archive/2026-10-23.md) | 2026-10-23 | jam · tray · remove · resume · copy |
| [第 26 期：密码重置链接失效后的处理](archive/2026-10-22.md) | 2026-10-22 | spam · request · link · expire · reset |
| [第 25 期：核对估算电费账单](archive/2026-10-21.md) | 2026-10-21 | meter · reading · usage · adjustment · credit |
| [第 24 期：听错交稿时间后的澄清与跟进](archive/2026-10-20.md) | 2026-10-20 | mishear · clarify · assume · recap · follow-up |
| [第 23 期：出发前核对随身行李](archive/2026-10-17.md) | 2026-10-17 | dimension · allowance · weigh · exceed · repack |
| [第 22 期：报名表人数核对](archive/2026-10-16.md) | 2026-10-16 | duplicate · filter · exclude · subtotal · validate |
| [第 21 期：进阶工作坊的候补与正式报名](archive/2026-10-15.md) | 2026-10-15 | prerequisite · eligible · waitlist · enroll · withdraw |
| [第 20 期：小组展示中的来源核查与标注](archive/2026-10-14.md) | 2026-10-14 | credible · paraphrase · attribute · citation · plagiarism |
| [第 19 期：活动午餐订单人数核对](archive/2026-10-13.md) | 2026-10-13 | discrepancy · provisional · specify · reconcile · finalize |
| [第 18 期：退租押金扣款核对](archive/2026-10-12.md) | 2026-10-12 | inspection · inventory · deduction · itemize · dispute |
| [第 17 期：入职门禁的授权与应变](archive/2026-10-10.md) | 2026-10-10 | authorization · pending · escalate · temporary · contingency |
| [第 16 期：包裹显示送达却找不到](archive/2026-10-09.md) | 2026-10-09 | parcel · tracking · doorstep · recipient · claim |
| [第 15 期：咖啡污渍的应急处理](archive/2026-10-08.md) | 2026-10-08 | stain · blot · rinse · soak · air-dry |
| [第 14 期：图书续借失败与归还](archive/2026-10-07.md) | 2026-10-07 | borrow · due · renew · overdue · return |
| [第 13 期：视频会议断网后的接入方案](archive/2026-10-06.md) | 2026-10-06 | outage · battery · hotspot · reconnect · backup |
| [第 12 期：公交绕行后的换乘选择](archive/2026-10-05.md) | 2026-10-05 | commute · detour · route · transfer · fare |
| [第 11 期：会议室撞期后换地点](archive/2026-10-04.md) | 2026-10-04 | overlap · capacity · available · reserve · relocate |
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

## 每日英文历史

每日英文历史是独立文章，不占用或改写“每日 5 词”的期数。先读英文全文，再按相同段落序号阅读完整中文译文；文后附重点表达、阅读理解与史料链接。

| 日期 | 文章 | 在线页面 |
|------|------|----------|
| 2026-10-28 | [姓名、粮食与文书：居延汉简中的边塞日常](archive/history-2026-10-28.md) | [阅读页面](outputs/history-2026-10-28.html) |
| 2026-10-27 | [战事之后：河西走廊如何成为汉朝边郡](archive/history-2026-10-27.md) | [阅读页面](outputs/history-2026-10-27.html) |
| 2026-10-26 | [三角城的城墙与种子：一座聚落的两种时间](archive/history-2026-10-26.md) | [阅读页面](outputs/history-2026-10-26.html) |
| 2026-10-25 | [丝路之前，海藏遗址的种子如何讲述生计变化？](archive/history-2026-10-25.md) | [阅读页面](outputs/history-2026-10-25.html) |
| 2026-10-24 | [丝路之前：河西走廊是怎样形成的？](archive/history-2026-10-24.md) | [阅读页面](outputs/history-2026-10-24.html) |
| 2026-10-22 | [河西走廊如何成为通往中亚的要道](archive/history-2026-10-22.md) | [阅读页面](outputs/history-2026-10-22.html) |

## 关于自动化

每日主稿：选取 5 个新词（与历史去重）→ 围绕具体情境写对话、用法辨析、易错点与练习 → 生成在线页面和归档。

每日副稿：另写一篇有可靠来源的英文历史文章，英文全文在前、逐段完整中文译文在后，独立归档；它不占「每日 5 词」的期数，文章里的重点表达也不计为本期新词。两篇齐备后，按单词头条、历史次条的顺序准备**同一份**公众号多图文草稿。若同日已有单篇草稿且无法安全补充次条，则保留原稿并报告，不再建立重复草稿。

草稿组合由历史文章任务执行：先用 `history_article.py --export-secondary` 输出次条素材，再用 `push_wechat.py --lesson --auto-cover --secondary-article` 一次提交双篇。已存在的双篇草稿按原 media_id 更新；单篇旧稿不由脚本转换。

自动化仅准备草稿，不自动群发。AI 可以辅助整理，但不能替代真人选题、审稿和发布判断；内容质量与平台推荐量均无保证。

单词去重使用完整历史词库，因此公众号期数与内部累计期数是两套编号，公众号从第 1 期起算。

## 说明

- 公众号正文不支持 JavaScript，语音朗读通过「阅读原文」跳转在线页面实现。
- 仓库不含任何凭据文件（`wechat/config.json` 已在 .gitignore 中排除）。
