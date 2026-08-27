## Specialized Agents Skill — Complete (31 Agents)

**Date:** 2026-02-10
**Version:** 1.1.0
**Status:** ✅ Complete and tested

---

### 📊 Agent Count Verification

| Category | Count | Agents |
|----------|-------|--------|
| Research | 3 | web, academic, local |
| Content Writing | 8 | creative, technical, marketing, social, funny, educational, trendy, controversial |
| Development | 7 | python, javascript, frontend, backend, database, api_designer, devops |
| QA & Review | 5 | code_reviewer, security, performance, accessibility, test_engineer |
| Analysis | 3 | data, sentiment, trends |
| Documentation | 1 | documentation_writer |
| Meta Agents | 4 | creator, design_reviewer, refiner, orchestrator |
| **TOTAL** | **31** | — |

---

### ✅ All Agents Listed

#### Research (3)
1. ✅ `researcher_web` — Web research specialist
2. ✅ `researcher_academic` — Academic/scientific research
3. ✅ `researcher_local` — Local business/place research

#### Content Writing (8)
4. ✅ `writer_creative` — Creative writing
5. ✅ `writer_technical` — Technical documentation
6. ✅ `writer_marketing` — Marketing copy
7. ✅ `writer_social` — Social media content
8. ✅ `content_writer_funny` — Humorous writing
9. ✅ `content_writer_educational` — Teaching content
10. ✅ `content_writer_trendy` — Viral/trend content
11. ✅ `content_writer_controversial` — Hot takes

#### Development (7)
12. ✅ `coder_python` — Python development
13. ✅ `coder_javascript` — JS/TS/React
14. ✅ `frontend_developer` — React/Vue/Angular
15. ✅ `backend_developer` — FastAPI/Flask/Django
16. ✅ `database_architect` — Schema design
17. ✅ `api_designer` — REST/GraphQL APIs
18. ✅ `devops_engineer` — Docker/K8s/CI-CD

#### QA & Review (5)
19. ✅ `code_reviewer` — General code quality
20. ✅ `reviewer_security` — Security review
21. ✅ `reviewer_performance` — Performance optimization
22. ✅ `accessibility_reviewer` — WCAG/a11y compliance
23. ✅ `test_engineer` — Test coverage

#### Analysis (3)
24. ✅ `analyzer_data` — Data interpretation
25. ✅ `analyzer_sentiment` — Sentiment analysis
26. ✅ `analyzer_trends` — Trend forecasting

#### Documentation (1)
27. ✅ `documentation_writer` — READMEs, API docs

#### Meta Agents (4)
28. ✅ `agent_creator` — Design new agents
29. ✅ `agent_design_reviewer` — Review agent quality
30. ✅ `agent_refiner` — Improve agent designs
31. ✅ `agent_orchestrator` — Coordinate workflows

---

### ✅ Prompt Quality Verification

Each agent prompt includes:
- ✅ **Clear persona** — Who they are and their expertise
- ✅ **Workflow** — Step-by-step process they follow
- ✅ **Output format** — How to structure responses
- ✅ **Examples** — What good output looks like
- ✅ **Boundaries** — What they do/don't do
- ✅ **Model selection** — Optimized (Kimi/Sonnet/Opus)
- ✅ **Timeout** — Appropriate for task complexity

---

### 🧪 Test Results

```bash
$ python3 specialized_agents.py

Specialized Agents Skill
==================================================

Research (3 agents):
  • researcher_web              - Expert at finding and synthesizing information...
  • researcher_academic         - Expert at scientific and academic research synthes...
  • researcher_local            - Expert at finding local businesses, restaurants, v...

Content Writing (8 agents):
  • writer_creative             - Imaginative writer for stories, poetry, creative c...
  • writer_technical            - Clear, precise technical documentation and explana...
  ...

Development (7 agents):
  • coder_python                - Python coding, debugging, best practices...
  • coder_javascript            - JS/TS coding, React, Node.js, modern practices...
  ...

QA & Review (5 agents):
  • code_reviewer               - General code quality and best practices review...
  • reviewer_security           - Security-focused code review and vulnerability det...
  ...

Analysis (3 agents):
  • analyzer_data               - Data interpretation, visualization suggestions, in...
  • analyzer_sentiment          - Text sentiment analysis, emotional tone detection...
  • analyzer_trends             - Trend identification, pattern recognition, forecas...

Documentation (1 agents):
  • documentation_writer        - READMEs, API docs, guides, and tutorials...

Meta (Agent Creation) (4 agents):
  • agent_creator               - Designs new AI agents with prompts, schemas, and e...
  • agent_design_reviewer       - Validates agent designs for quality and completene...
  • agent_refiner               - Improves agent designs based on review feedback...
  • agent_orchestrator          - Master coordinator that plans and manages multi-ag...

==================================================
Total: 31 specialized agents
```

---

### 📁 Files Updated

| File | Status |
|------|--------|
| `specialized_agents.py` | ✅ 31 agents defined |
| `SKILL.md` | ✅ Documentation updated |
| `spawn_specialized_agent.tool.json` | ✅ Schema updated with all 31 |
| `examples.py` | ✅ New examples added |
| `INTEGRATION.md` | ✅ Integration guide (existing) |

---

### 💡 Key Features

1. **Comprehensive Coverage** — 31 agents across 7 categories
2. **Quality Prompts** — Each with detailed persona, workflow, output format
3. **Model Optimization** — Kimi for most, Sonnet for complex, Opus for orchestration
4. **Timeout Tuning** — Research gets 180s, writing 60s, meta agents up to 300s
5. **Tag System** — For filtering and categorization
6. **Command Dispatch** — Can spawn via `/specialized_agent agent_type|task`

---

### 🚀 Ready for Production

All 31 agents:
- ✅ Load without errors
- ✅ Have complete prompts
- ✅ Are properly categorized
- ✅ Have appropriate models/timeouts
- ✅ Can be spawned via API

**Status: COMPLETE** 🐕
