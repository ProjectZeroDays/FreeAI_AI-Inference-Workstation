# 📊 代码分析技能 (Code Analysis Skills)

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.2.0-orange)](skill.yaml)

一个 **Git 历史自查报告**生成器：扫描 Git 仓库，把提交历史聚合成描述性的多维度统计 —— 涵盖 **提交模式**、**提交时段**、**变更模式**、**代码风格** 与 **代码质量痕迹**。

> ⚠️ **本工具仅适用于 (a) 自查或 (b) 在每位成员都明确同意的前提下进行团队复盘。**
> **严禁**用于绩效考核、个人排名、薪酬 / 晋升 / 处分决策、或对未同意者的监控。
> 详见下文「使用政策」。

---

## ✨ 功能特性

- 🔍 **仓库扫描** — 分析单个 Git 仓库，或递归扫描目录下所有 `.git` 仓库
- 📝 **提交模式** — 提交频率、提交大小分布、合并比例、提交信息长度
- ⏰ **提交时段统计** — 按小时分布、周末 / 深夜比例、连续提交天数（描述性，需结合上下文阅读）
- 🚀 **变更模式** — 代码流失率（churn）、返工比例、巴士因子（仓库级风险指标）、文件归属
- 🎨 **代码风格** — 编程语言分布、约定式提交合规率、文件分类
- 🔎 **代码质量痕迹** — Bug 修复比例、回退频率、大提交比例、测试覆盖率、Python 复杂度（基于 radon）
- 🪞 **自查摘要** — 描述性观察 / 可改进点 / 反思提示，每条背后都有具体的分量值。**不会**产出综合评分、字母等级、一句话定论。
- 🔒 **默认 self-scope** — 默认只分析当前本地 Git 用户自己的提交；分析他人需要额外传入 `--multi-author-team-retro` 与逐个 `--consented-author NAME`。不论何时都**不产出**排行榜或多人横向对比表。
- 📄 **多种输出格式** — Markdown / JSON / HTML / PDF，每种输出顶部强制带使用政策提示

## 📦 安装

### 前置要求

- Python 3.9+
- Git

### 安装依赖

```bash
pip install -r requirements.txt
```

或单独安装各依赖包：

```bash
pip install gitpython pydriller radon tabulate jinja2 click pyyaml reportlab
```

## 🚀 使用方法

> 所有命令都需要 `--i-have-consent`。不带这个开关时工具只会打印使用提示并退出。

### 基本命令

```bash
# 自查 / 已获团队全员同意
python -m src.main --i-have-consent -r /path/to/repo

# 递归扫描目录下所有 Git 仓库
python -m src.main --i-have-consent -r /path/to/projects --scan-all

# 已获全员知情同意的多作者团队复盘（每位被分析者都需先同意）
python -m src.main --i-have-consent --multi-author-team-retro \
    --consented-author "Alice <alice@example.com>" \
    --consented-author "Bob <bob@example.com>" \
    -r /path/to/repo

# 按日期范围过滤
python -m src.main --i-have-consent -r /path/to/repo -s 2024-01-01 -u 2024-12-31

# 生成 HTML 报告
python -m src.main --i-have-consent -r /path/to/repo -f html -o report.html

# 同时生成 Markdown + HTML + PDF
python -m src.main --i-have-consent -r /path/to/repo -f "markdown,html,pdf" -o report

# 生成 PDF 报告
python -m src.main --i-have-consent -r /path/to/repo -f pdf -o report.pdf

# 将 Markdown 报告保存到文件
python -m src.main --i-have-consent -r /path/to/repo -o report.md
```

### 命令行参数

| 参数 | 说明 | 默认值 |
|---|---|---|
| `-r, --repo` | Git 仓库或父目录路径 | *（必填）* |
| `--i-have-consent` | 必填。确认你已读过使用政策、获得每位被分析开发者的知情同意，并不会用于绩效 / 排名 / HR 决策。**没有**环境变量绕过 | *（必填）* |
| `--multi-author-team-retro` | 退出 self-scope 模式，运行已获全员同意的多作者复盘。需要至少一个 `--consented-author` 项 | `false`（即默认 self-scope） |
| `--consented-author NAME` | 已知情同意纳入此次复盘的作者名/邮箱（可重复使用）。**只有**列出的作者会被分析 | `[]`（self-scope 时只分析当前 Git 用户） |
| `--scan-all` | 递归扫描所有 `.git` 仓库（每个仓库内仍受 self-scope / consented-authors 约束） | `false` |
| `-s, --since` | 起始日期（ISO 格式：`YYYY-MM-DD`） | — |
| `-u, --until` | 截止日期（ISO 格式：`YYYY-MM-DD`） | — |
| `-b, --branch` | 要分析的分支 | 当前分支 |
| `-f, --format` | 输出格式：`markdown`、`json`、`html`、`pdf`（逗号分隔可多选） | `markdown` |
| `-o, --output` | 输出文件路径 | 标准输出 |

> **注意**：本工具不再提供 `-a/--author` 这类直接的"按作者过滤"参数。要分析他人，必须显式启用 `--multi-author-team-retro` 并逐个传入 `--consented-author`，否则只分析当前本地 Git 用户自己。

## 📁 项目结构

```
code-analysis-skills/
├── src/
│   ├── main.py                 # CLI 入口
│   ├── scanner.py              # 仓库扫描器（单仓库 & 递归扫描）
│   ├── analyzers/
│   │   ├── base_analyzer.py    # 基础分析器（Git 遍历 & 作者过滤）
│   │   ├── commit_analyzer.py  # 提交模式分析
│   │   ├── work_habit_analyzer.py  # 工作习惯分析
│   │   ├── efficiency_analyzer.py  # 开发效率分析
│   │   ├── code_style_analyzer.py  # 代码风格分析
│   │   ├── code_quality_analyzer.py # 代码质量痕迹分析
│   │   └── cadence_signal_analyzer.py # 节奏信号分析（不输出综合分 / 等级 / 排名）
│   ├── narrator/
│   │   └── reflection_narrator.py  # 自查叙述生成器（中性观察 / 讨论点 / 反思提示，无评分）
│   ├── reporters/
│   │   ├── base_reporter.py    # 报告生成器基类
│   │   ├── markdown_reporter.py # Markdown 报告生成器
│   │   ├── json_reporter.py    # JSON 报告生成器
│   │   ├── html_reporter.py    # 带样式的 HTML 报告生成器
│   │   └── pdf_reporter.py     # PDF 报告生成器
│   └── utils/
│       └── helpers.py          # 工具函数
├── tests/
│   ├── test_analyzers.py       # 分析器单元测试
│   └── test_scanner.py         # 扫描器单元测试
├── references/
│   └── metrics-guide.md        # 指标定义与健康范围参考
├── SKILL.md                    # ClawHub 技能定义
├── skill.yaml                  # 技能配置文件
├── requirements.txt            # Python 依赖清单
├── pyproject.toml              # 项目元数据
└── pytest.ini                  # 测试配置
```

## 📊 分析维度详解

> 所有维度都是**描述性统计**，不是对人的评估。每份报告顶部都强制带使用政策提示。

### 1. 📝 提交模式
- 提交频率（日/周维度）
- 提交规模（每次提交的增删行数）
- 合并提交占比
- 提交信息长度

### 2. ⏰ 提交时段统计
- 工作时段热力图（按小时分布）
- 周末提交百分比（描述性，需结合时区 / 工作模式阅读）
- 深夜提交百分比（22:00–06:00，描述性）
- 最长连续提交天数

> ⚠️ 这些数字仅反映**提交时间戳**，不能直接当作工作时长 / 加班 / 投入度的代理。

### 3. 🚀 变更模式
- 代码流失率（删除行数 / 新增行数）
- 返工比例（对近期修改文件的再次修改）
- 巴士因子（**仓库级**风险指标，不是个人评分）
- 文件归属分布

### 4. 🎨 代码风格
- 编程语言分布
- 约定式提交（Conventional Commits）合规率
- 文件类型分类（源码 / 测试 / 配置 / 文档）

### 5. 🔍 代码质量痕迹
- Bug 修复提交占比
- 回退（Revert）提交频率
- 大提交占比
- 测试文件覆盖率
- Python 代码复杂度（基于 radon 的圈复杂度分析）

### 6. 📉 节奏密度信号（仅描述性）
- 以**各分量分别输出**描述提交活动有多稀疏 / 集中：稀疏度、琐碎提交、长间隔、低日量、非代码提交、周内偏后、增删失衡
- **不输出 0–100 综合分**，也不输出从“活跃密集”到“节奏非常稀疏”的总分段。这里仅以分量表述，是为了避免被当作“摸鱼分”使用。

> ⚠️ 高稀疏度 **不等于** "摸鱼"。架构师、Reviewer、值班工程师、休假 / 病假人员都会自然产生稀疏节奏。请结合上下文阅读。

### 7. 🪞 自查摘要
- 支持性观察、可改进点（带上下文）、个人反思提示 — 每条都有具体分量值支撑
- **不产出综合 0–100 评分、不产出 S/A/B/C/D/E/F 字母等级、不产出一句话定论** — 这些表达一旦出现就会被当成个人评分卡，所以被明确从输出中删除了
- 每位作者的报告都挂一个必填的 `interpretation_notice` 字段，下游渲染时应一并输出

## 🧪 测试

```bash
# 运行所有测试
pytest

# 详细输出模式
pytest -v

# 运行指定测试文件
pytest tests/test_analyzers.py
```

## ⚠️ 注意事项

- 分析大型仓库（10 万+ 提交）可能耗时较长，建议限定日期范围
- Python 复杂度分析依赖 `radon`，仅适用于 `.py` 文件
- 作者匹配支持模糊匹配（名称或邮箱子串匹配）
- 目录扫描默认最大深度为 5 层，避免过深递归
- PDF 生成优先使用 weasyprint，回退到 pdfkit，最终回退到 reportlab
- 指标仅基于 Git 提交历史数据，不代表开发者的全部能力
- 节奏密度信号仅供参考，必须结合实际工作场景理解

## ⚠️ 使用政策（必读）

> **重要提示**：本工具会从 Git 提交历史中提取开发者个人活动数据（提交时间、频率、行为模式等）。

**使用前请务必遵守：**

- ✅ 本工具**完全本地运行**，不会向任何外部服务器传输数据
- ✅ 仅适用于：(1) 你对**自己**仓库的自查；(2) 团队在**每位成员都明确同意**前提下的复盘
- ⚠️ 分析他人仓库前，请**获得每位相关开发者的知情同意**
- 🚫 分析结果**不应**直接用于绩效考核、薪酬决策、晋升 / 处分管理
- 🚫 分析结果**不应**用于对个人的排名、打分或公开比较
- 🚫 分析结果**不应**用于监视员工或未同意的贡献者
- 🔒 生成的报告包含个人信息，请**妥善保管**，不应公开分享
- 📋 使用前请确认符合组织的 HR 政策和当地数据保护法规（如 GDPR）

**结构性门槛（不只是免责声明）：**

1. **显式同意标志（无环境变量绕过）** — CLI 必须传 `--i-have-consent`，Skill 必须传 `acknowledge_usage_policy: true`。**没有**环境变量绕过。
2. **默认 self-scope** — 不传其他选项时，分析器被锁定到当前本地 Git 用户身份；仓库内其他作者的提交会被完全跳过。
3. **多人分析需二次明确 opt-in** — 需同时传 `--multi-author-team-retro` 和逐个 `--consented-author NAME`。未列名的作者不会被隐含地加入分析。
4. **任何输出都不生成**综合评分、字母等级、排行榜、多人横向对比表，哪怕是多人复盘模式。

## 📄 许可证

本项目基于 MIT 许可证开源 — 详见 [LICENSE](LICENSE) 文件。
