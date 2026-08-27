# 指标含义与参考范围

本文档说明 Git 历史自查报告中各项指标的含义、计算方式与一般参考范围。

> ⚠️ 所有指标都是**描述性**统计，**不是**对个人能力、投入度或价值的评价。阅读这些数字时，请始终结合角色、时区、值班、休假等上下文。本工具产出**不应**用于绩效考核、个人排名或任何 HR 决策。

## 📝 提交习惯指标

| 指标 | 含义 | 计算方式 | 健康值范围 |
|------|------|---------|-----------| 
| Total Commits | 总提交次数 | 统计所有非过滤提交 | — |
| Merge Ratio | 合并提交占比 | merge_commits / total_commits | < 30% |
| Avg Commits/Active Day | 每个活跃日的平均提交数 | total_commits / unique_active_days | 2-8 |
| Avg Message Length | 平均提交消息长度(字符) | sum(msg_len) / count | 30-100 |
| Avg Lines Added | 平均每次提交新增行数 | sum(added) / count | 10-200 |
| Avg Lines Deleted | 平均每次提交删除行数 | sum(deleted) / count | 5-100 |
| Avg Files Changed | 平均每次提交修改文件数 | sum(files) / count | 1-10 |

## ⏰ 工作习惯指标

| 指标 | 含义 | 计算方式 | 关注阈值 |
|------|------|---------|---------| 
| Peak Hour | 提交最多的小时 | mode(commit_hours) | — |
| Weekend Ratio | 周末提交占比 | weekend_commits / total | > 20% 需关注 |
| Late Night Ratio | 深夜(22:00-05:00)提交占比 | late_night_commits / total | > 15% 需关注 |
| Longest Streak | 最长连续编码天数 | 连续日期计数 | — |
| Avg Gap Between Commits | 两次提交的平均间隔(小时) | avg(time_gaps) | — |

### 时段定义

| 时段 | 时间范围 |
|------|---------|
| Early Morning | 05:00 - 08:59 |
| Morning | 09:00 - 11:59 |
| Afternoon | 12:00 - 17:59 |
| Evening | 18:00 - 21:59 |
| Late Night | 22:00 - 04:59 |

## 🚀 研发效率指标

| 指标 | 含义 | 计算方式 | 健康值范围 |
|------|------|---------|-----------| 
| Churn Rate | 代码流失率（写了又删的比例） | total_deleted / total_added | < 50% |
| Rework Ratio | 返工率（7天内重复修改同一文件） | rework_mods / total_mods | < 30% |
| Lines per Commit | 每次提交的总变更行数 | (added + deleted) / commits | 20-300 |
| Ownership Ratio | 文件所有权比例（贡献 >50% 的文件） | owned_files / unique_files | — |
| Bus Factor | 仓库平均总线因子（每个文件的独立贡献者数） | avg(unique_authors_per_file) | > 2 为佳 |

### 指标解读

- **Churn Rate 高**: 可能表示需求变更频繁、技术方案不稳定或探索性编码
- **Rework Ratio 高**: 可能表示代码质量问题、需求不明确或 review 反馈多
- **Bus Factor 低**: 知识集中在少数人手中，团队有风险

## 🎨 代码风格指标

| 指标 | 含义 | 计算方式 | 建议 |
|------|------|---------|------| 
| Conventional Commit Ratio | 遵循 Conventional Commits 规范的比例 | conventional_count / total | > 80% 为佳 |
| Issue Reference Ratio | 提交消息中引用 Issue/Ticket 的比例 | issue_ref_count / total | > 50% 为佳 |
| Language Distribution | 修改的文件语言分布 | 按文件扩展名统计 | — |
| File Category Distribution | 修改的文件类别分布 | source/test/config/docs 等 | — |

### Conventional Commits 格式

```
<type>(<scope>): <description>
```

支持的 type: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

## 🔍 代码质量指标

| 指标 | 含义 | 计算方式 | 关注阈值 |
|------|------|---------|---------| 
| Bug Fix Ratio | Bug 修复提交占比 | bugfix_commits / total | > 40% 需关注 |
| Revert Ratio | 回滚提交占比 | revert_commits / total | > 5% 需关注 |
| Large Commit Ratio | 大提交(>500行变更)占比 | large_commits / total | > 20% 需关注 |
| Test Modification Ratio | 测试文件修改占文件修改总数的比例 | test_mods / total_mods | > 20% 为佳 |
| Doc Modification Ratio | 文档文件修改占比 | doc_mods / total_mods | — |
| Avg Python Complexity | Python 代码平均圈复杂度 | radon cc_visit 结果平均 | < 10 为佳 |

### 圈复杂度参考

| 复杂度 | 等级 | 说明 |
|--------|------|------|
| 1-5 | A | 低风险，容易维护 |
| 6-10 | B | 中等，仍可接受 |
| 11-20 | C | 高风险，建议重构 |
| 21-50 | D | 非常高，应当拆分 |
| 50+ | F | 不可维护 |

## 📉 节奏稀疏度信号（Cadence-Sparsity Signals）

节奏稀疏度是一组描述性信号，描述 Git 提交活动**有多稀疏 / 集中**。**不输出 0–100 综合评分**，各信号分别输出。

> ⚠️ 本信号组**仅描述性**。高值不等于"摸鱼"，也不等于低投入度。架构师、Reviewer、值班工程师、休假 / 病假人员，都会自然产生稀疏节奏。
> 本信号组**不应**用于绩效考核、排名或任何 HR 决策。

### 信号说明

| 信号 | 含义 | 计算方式 | 常见多种解释 |
|------|------|---------|---------------|
| Sparsity (稀疏度) | 活跃天数占总时间跨度的比例 | 1 - (unique_days / span_days) | 架构师 / 设计导向 / 休假 / 值班 |
| Trivial-change ratio (琐碎提交) | 变更 ≤5 行的提交占比 | trivial_count / total | 配置微调 / 紧急修复 / hot-fix |
| Long-gap ratio (长间隔) | 超72小时无提交的间隔占比 | large_gap_count / total_gaps | 项目间隔 / 休假 / 跨仓库工作 |
| Low daily volume (低日量) | 每活跃日的变更行数 | total_lines / unique_days | review-heavy / 调研 / 调试 |
| Non-code-only (仅非代码提交) | 仅修改配置/文档的提交占比 | non_code_commits / total | 文档维护 / CI 调整 |
| Late-week skew (周内偏后) | 周五提交多、周一提交少的趋势 | friday_ratio - monday_ratio | 周独立完整交付节奏 / 重要会议周一 |
| Add/delete imbalance (增删失衡) | 新增/删除行比率过高 | added / deleted > 10 | 仓库初始化 / 引入依赖 / 生成代码 |

### 重要提醒

- 信号仅基于 Git 提交行为，不反映代码评审、设计、会议、指导同事、值班、运维等非编码贡献
- 某些角色（架构师、技术经理、Reviewer）天然提交较少，需结合角色理解
- 信号被有意以各分量表达，而非拼接为单一评分，以免被重新包装为“摸鱼分”
- **信号绝不应用于绩效考核、个人排名或惩罚性管理**

## 🪞 自查报告体系

### 输出是什么

每位开发者的自查仅包含**文本叙述**，并且背后都有具体的分量值支撑：

1. **支持性观察**：每条基于具体数据
2. **值得讨论的点（带上下文）**：中性、不带个人贬损
3. **个人反思提示**：可拿去思考的问题

### 输出有意**不**输出的内容

为了防止本工具被重包装为个人评分卡，报告有意不输出下列内容：

- **0–100 综合评分**。跨维度加权总分会被当作个人评分使用。
- **S / A / B / C / D / E / F 字母等级**。字母段在语义上与评级等同，哪怕处处加“描述性”三字也难以避免误读。
- **"verdict" 定论句**。一句话总结在实践中总被作为“个人评价”转载。
- **排行榜、多人横向对比表**。跨作者的同页表格在结构上就是“个人排名”的原料。

### 各维度（仅以分量表达）

以下维度以原始指标表现，从不加权为单一评分：

| 维度 | 描述内容 |
|------|----------|
| Commit Discipline (提交纪律) | 提交频率、消息长度、规范遵循率 |
| Cadence Consistency (节奏一致性) | 提交时间戳的分布 |
| Change Patterns (变更模式) | Churn、Rework、变更量 |
| Code Quality artefacts (代码质量痕迹) | Bug 修复率、回滚率、变更中的测试覆盖、复杂度 |
| Code Style markers (代码风格) | Conventional Commits、Issue 引用 |
| Cadence Density (节奏密度) | 长间隔信号的反向 |

> ⚠️ 本报告**是讨论的起点，不是定论**。**不应**被用于绩效考核、薪酬 / 晋升 / 处分决策，或对个人的排名。
