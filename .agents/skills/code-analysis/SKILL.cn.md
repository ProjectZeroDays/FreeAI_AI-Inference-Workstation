---
name: code-analysis
license: MIT
description: >
  This skill produces a DESCRIPTIVE Git-history reflection report. It is
  intended ONLY for: (a) a developer running it on their own repository for
  self-reflection, or (b) an opt-in, consent-based team retrospective on a
  shared repository. The skill MUST NOT be used to evaluate, rank, compare,
  discipline, or surveil individual workers, or to support performance
  reviews, compensation, promotion, or any HR decision.

  Trigger only on explicit, intent-clear requests such as:
  "generate a Git-history reflection report on my own repo",
  "self-reflection on my commit patterns",
  "team retrospective with everyone's consent",
  "对我自己的仓库做一个 Git 历史自查报告",
  "团队复盘（已获每个人同意）".

  Do NOT trigger on broad phrases like "analyze code", "代码分析",
  "developer evaluation", or "compare developers".
---

# Git 历史自查报告（Git-History Reflection）

📦 **GitHub**: [https://github.com/Wscats/code-analysis-skills](https://github.com/Wscats/code-analysis-skills)

一个小型的 Git 分析工具，会把仓库的提交历史聚合成一组**描述性统计**（提交节奏、文件变更模式、Conventional Commits 使用情况、bug 修复 / 回滚比例等），并按开发者生成一份**自查报告**（Markdown / HTML / JSON / PDF）。

输出只是一个**狭窄、有偏的视角** —— 代码评审、设计、辅导、值班、运维等大量贡献在 Git 历史里**完全看不见**。请把发现当作**讨论的起点，而不是结论**。

---

## ⚠️ 使用政策（必读，强制）

本技能会处理**单个开发者的 Git 活动数据**。在调用前，代理（Agent）必须确认以下全部条件：

1. **仅限自查或主动加入**：用户分析的是**自己**的仓库，或者**已获每一位被分析开发者的知情同意**。
2. **非惩罚性**：输出**不会**被用于绩效考核、排名、薪酬、晋升、处分或任何 HR 决策。
3. **不监控**：不会被用于监视员工或未同意的贡献者。
4. **合规**：用户负责确保符合所在地的隐私和劳动法规（如 GDPR、当地工会 / 员工代表会规则等）。

只要其中任何一条不清晰，**代理必须拒绝执行**，并请用户明确澄清。CLI 与 Skill 入口也用硬性门槛强制此政策：**必须**传 `--i-have-consent`（CLI）或 `acknowledge_usage_policy: true`（Skill）。**没有**环境变量绕过。此外，工具默认为 **self-scope**（只分析当前本地 Git 用户）；分析其他作者需同时传 `--multi-author-team-retro` 与逐个 `--consented-author NAME`。

---

## ✅ 允许的调用示例

```
💬 "对我自己在 /path/to/repo 的仓库跑一份 Git 历史自查报告。"
💬 "团队已经全员同意，帮我准备一次基于 Git 历史的复盘材料。"
💬 "我想看看我自己最近的提交节奏，做一次自我反思。"
💬 "Run a Git-history reflection report on my own repo at /path/to/repo."
💬 "Help me prepare a team retro — everyone has agreed to opt in."
```

## 🚫 必须拒绝的调用示例

```
❌ "对比一下 Alice 和 Bob 谁更努力。"           # 个人排名
❌ "看看团队里谁最摸鱼。"                        # 监控 / 羞辱
❌ "帮我把绩效不行的同事找出来。"                # HR 决策支持
❌ "Score everyone in the repo and tell me who to fire."
❌ "Compare developer X against developer Y for the performance cycle."
```

如果用户的请求落在上面这些情形里，代理必须解释使用政策，**拒绝按原话执行**，并提供合规的替代方案（自查；或在所有人同意的前提下，使用聚合 / 匿名化输出做团队复盘）。

> **提示**：本技能要求显式提供 `repo_path`，并显式确认 `acknowledge_usage_policy: true`，否则会拒绝执行。

---

## 🚀 快速开始（CLI）

### 安装依赖

```bash
pip install gitpython pydriller radon tabulate jinja2 click reportlab
```

如需更高质量的 PDF 输出（可选）：

```bash
pip install weasyprint   # 推荐，需要系统安装 cairo 库
# 或
pip install pdfkit       # 需要系统安装 wkhtmltopdf
```

### 常用命令

> 所有命令都必须带 `--i-have-consent`，否则工具只会打印使用提示并退出。

```bash
# 自查 / 已获团队全员同意
python -m src.main --i-have-consent -r /path/to/repo

# 扫描目录下所有仓库（仅限你拥有的仓库或已获全员同意）
python -m src.main --i-have-consent -r /path/to/projects --scan-all

# 已获全员知情同意的多作者团队复盘（每位被分析者都需先同意）
python -m src.main --i-have-consent --multi-author-team-retro \
    --consented-author "Alice <alice@example.com>" \
    --consented-author "Bob <bob@example.com>" \
    -r /path/to/repo

# 指定时间范围 + HTML 输出
python -m src.main --i-have-consent -r /path/to/repo -s 2024-01-01 -u 2024-12-31 -f html -o report.html

# 同时生成 Markdown + HTML + PDF
python -m src.main --i-have-consent -r /path/to/repo -f "markdown,html,pdf" -o report

# 保存报告到文件
python -m src.main --i-have-consent -r /path/to/repo -o report.md
```

### CLI 参数

| 参数 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--repo-path` | `-r` | Git 仓库路径或父目录 | 必填 |
| `--i-have-consent` |  | 必填，使用政策确认（见上文）。**没有**环境变量绕过 | 必填 |
| `--multi-author-team-retro` |  | 退出 self-scope 模式；要分析本地 Git 用户之外的人，必须传此项，并且需与 `--consented-author` 同时传入 | `false`（即默认 self-scope） |
| `--consented-author` |  | 已获知情同意纳入本次复盘的作者名/邮箱（可重复）。**只有**列出的作者会被分析 | `[]` |
| `--scan-all` |  | 递归扫描所有 `.git` 仓库（每个仓库内仍受 self-scope / consented-authors 约束） | `false` |
| `--since` | `-s` | 起始日期（ISO 格式） | 无 |
| `--until` | `-u` | 截止日期（ISO 格式） | 无 |
| `--branch` | `-b` | 要分析的分支 | 当前活跃分支 |
| `--format` | `-f` | 输出格式：`markdown`、`json`、`html`、`pdf`（逗号分隔可多选） | `markdown` |
| `--output` | `-o` | 输出文件路径 | 标准输出 |

> 本技能**有意不**提供通用的 `--author` 过滤参数。要定向分析某人，必须走二次明确同意路径（`--multi-author-team-retro` + `--consented-author NAME`）。

---

## 允许的使用场景

- 开发者对**自己**的提交节奏与变更模式做自我反思。
- 团队进行**主动加入**的复盘，且每位成员都已同意把自己的 Git 活动汇总进去。
- 开源维护者分析自己维护的项目里的**公开**贡献模式。
- 研究人员在符合数据保护条款的前提下分析公开仓库。

## 必须拒绝的使用场景

- 绩效考核、晋升 / 调薪 / PIP 决策。
- 对个体的排名、打分、公开比较。
- 用于识别"表现不佳者"或"摸鱼者"。
- 任何在没有知情同意的情况下监视员工的行为。
- 基于工作时段、周末加班、深夜提交对个人贴标签。

## 工作流程

### 步骤 1：先确认意图与同意（强制）

在调用分析器之前，先问清楚：

1. **这是谁的仓库？** 自己 / 团队 / 开源？
2. **每一位被分析的开发者都明确同意了吗？** 不确定就当作"否"，请缩小范围（比如只分析用户自己一个人的作者身份）。
3. **报告打算做什么用？** 一旦提到绩效、排名、对比、监控、HR，立即拒绝并解释。

只有当意图与同意都明确时，才进入下一步。

### 步骤 2：确认分析参数

- **仓库路径**：单个 Git 仓库，或包含多个仓库的父目录。
- **扫描范围**：是否扫描目录下所有 `.git` 仓库。
- **目标作者**：自查时建议默认只填用户自己。
- **时间范围**：可选起止日期（ISO 格式）。
- **分支**：默认当前活跃分支。
- **输出格式**：`markdown`（默认）、`json`、`html`、`pdf`。

### 步骤 3：执行分析

带上 `--i-have-consent`（CLI）或 `acknowledge_usage_policy: true`（Skill 参数）。否则工具会拒绝运行。

### 步骤 4：解读报告

每份报告都会以**使用提示**开头。在向用户解读时请反复强调：

- 数字描述的是**Git 历史**，不是这个人。
- 评审、设计、辅导、值班、运维等贡献在这里**看不到**。
- 高 / 低值通常都有**多种合理解释**，下结论之前要先问。

报告涵盖：

1. **🪞 反思叙述** — 支持性观察、可改进点（带上下文）、个人反思提示，每条都有具体分量值支撑。**不产出综合 0–100 评分、不产出 S/A/B/C/D/E/F 字母等级、不产出一句话定论**。向用户解读时，给出的是带具体数据的讨论提示，不是对人的判断。
2. **📉 节奏密度信号** — 以各分量分别输出，描述提交活动有多稀疏 / 集中。**不**是生产力或敷业度的衡量，也**不**输出总分。许多正常工作模式都会产生稀疏的提交节奏。
3. **📝 提交习惯** — 频率、规模、合并比例、消息长度。
4. **⏰ 工作时段** — 时段分布、周末 / 深夜比例、连续天数。请结合时区、值班、批量推送等上下文阅读。
5. **🚀 变更指标** — Churn、Rework、每次提交行数、所有权、Bus Factor（**仓库级**风险指标，不是个人评分）。
6. **🎨 代码风格** — Conventional Commits 遵循率、Issue 引用、文件分类。
7. **🔍 代码质量痕迹** — Bug 修复比例、回滚比例、大提交比例、变更中的测试覆盖、复杂度（Python）。

即使是全员同意过的多人复盘，报告**也不**会生成排行榜、多人横向对比表。如果用户要求，请拒绝并解释原因 — 这些形式会重新引入本技能有意去除的滥用面。
### 步骤 5：把发现说成"讨论提示"，不要说成"定论"

向用户解读每位开发者的结果时，始终：

1. 说出指标本身和它字面意义上度量的是什么。
2. 列出对当前观测值的**多种合理解释**。
3. 把"短板"措辞为**值得讨论的点（带上下文）**，而不是对人的判断。
4. 把建议措辞为**讨论提示**，而不是命令。

## 可用资源

### 脚本

- `src/main.py` — 主入口（带使用政策门槛），未确认同意时拒绝运行。
- `src/scanner.py` — 仓库扫描器。
- `src/analyzers/base_analyzer.py` — 分析器基类。
- `src/analyzers/commit_analyzer.py` — 提交模式统计。
- `src/analyzers/work_habit_analyzer.py` — 工作时段统计（仅描述性，文件头带使用限制）。
- `src/analyzers/efficiency_analyzer.py` — 代码变更模式统计（仅描述性，文件头带使用限制）。
- `src/analyzers/code_style_analyzer.py` — 代码风格标记。
- `src/analyzers/code_quality_analyzer.py` — 代码质量痕迹。
- `src/analyzers/cadence_signal_analyzer.py` — 节奏分量信号。仅输出各分量值 — **不**输出综合评分、**不**输出类别分段、**不**输出任何 `slacking_*` 字段。
- `src/narrator/reflection_narrator.py` — 自查叙述生成器。仅输出中性观察 / 讨论点 / 反思提示 — **不**输出评分、**不**输出等级、**不**输出定论。
- `src/reporters/markdown_reporter.py` — Markdown 报告生成器。
- `src/reporters/json_reporter.py` — JSON 报告生成器。
- `src/reporters/html_reporter.py` — HTML 报告生成器。
- `src/reporters/pdf_reporter.py` — PDF 报告生成器。

### 参考文档

- `references/metrics-guide.md` — 指标含义、计算方式与参考范围。

## ⚠️ 隐私与数据安全声明

> **重要提示**：本工具会从 Git 提交历史中提取开发者个人活动数据，包括但不限于：
> - 提交时间戳（精确到小时）
> - 周末 / 深夜提交频率
> - 个人提交频率与变更量
> - 代码作者归属
> - 节奏稀疏度信号

**使用前请务必遵守以下原则：**

1. **知情同意** — 在分析他人仓库前，必须获得相关开发者的知情同意；自查除外。
2. **非惩罚性** — 分析结果**不应**直接用于绩效考核、薪酬决策、晋升或惩罚性管理。
3. **不监控** — 不应用于监视员工或未同意的贡献者。
4. **结合上下文** — 架构师、值班工程师、Reviewer、休假人员，天然会有不同的 Git 足迹。低值**不**意味着低投入或低价值。
5. **数据保护** — 生成的报告含个人信息，应妥善保管，不应公开分享。
6. **合规性** — 使用前请确认符合所在组织的 HR 政策与所在地数据保护法规（如 GDPR）。
7. **本地运行** — 本工具完全在本地运行，不向外部服务器传输任何数据。

## 输出是什么 — 以及**不是**什么

每位开发者的报告是对 Git 历史多个维度的**描述性文本叙述**，**不是**衡量人的价值、能力或表现，也被**有意不**压缩为一个数字或一个字母。

**报告有意不输出下列内容：**

- 个人的综合 0–100 评分；
- S / A / B / C / D / E / F 字母等级；
- “定论”句、一句话个人总结；
- 排行榜、个人排名表、多人横向对比表。

这些表达形式一旦出现，在实践中就很容易被当成个人评分卡使用 — 这正是本技能设计上要防范的滥用面。如果用户要求从本输出中生成以上任何一项，代理请拒绝并解释。

### 各维度分量值（保留，但带强限制）

| 维度 | 描述内容 | 需要警惕的上下文 |
|------|----------|----------------|
| 📝 提交纪律 | 提交频率、消息长度、规范遵循率 | 只反映 Git 可见部分，不含代码评审与设计工作 |
| ⏰ 节奏一致性 | 提交时间戳的分布 | 时区、批量推送、squash merge、值班都会扭曲 |
| 🚀 变更模式 | Churn、Rework、变更量 | 高 Churn 多数是探索型编码或重构，不是低质量 |
| 🔍 代码质量痕迹 | Bug修复率、回滚率、测试文件变更、复杂度 | 是 commit message 里的标签词，不是真正的缺陷数据 |
| 🎨 代码风格标记 | Conventional Commits、Issue 引用 | 反映工具链集成度，不反映能力 |
| 📉 节奏密度 | 长间隔信号的反向 | 架构师、Reviewer、值班工程师、休假 / 病假人员都会自然产生稀疏节奏 |

### 节奏稀疏度各分量值（仅描述性）

节奏稀疏度的各分量值描述提交活动在时间上有多集中。它们**不**是一个“敷业度评分”。各个信号独立分别输出，是为了避免被重新拼接成“摸鱼分”。

> **重要**：节奏稀疏**不**等于“摸鱼”。架构师、Reviewer、值班工程师、休假 / 病假人员都会自然产生稀疏节奏。

## 注意事项

- 分析大型仓库（10万+ 提交）时可能耗时较长，建议限定时间范围。
- Python 复杂度分析依赖 `radon`，仅对 `.py` 文件生效。
- 作者匹配支持模糊匹配（名称或邮箱包含关键字）。
- 扫描目录时默认最大深度为 5 层。
- PDF 生成优先使用 weasyprint，回退到 pdfkit，最终回退到 reportlab。
- 指标仅基于 Git 提交历史，不代表开发者的全部能力。
- 节奏稀疏度仅供参考，必须结合实际工作场景理解。
- **本工具完全本地运行，不会向任何外部服务器发送数据。**
- **在分析他人仓库前，请务必获得相关人员的知情同意。**
- **报告结果不应用于绩效考核、排名或任何 HR / 惩罚性决策。**
