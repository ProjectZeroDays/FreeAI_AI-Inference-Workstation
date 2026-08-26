# Harvested: frontend-testing

Source: `/root/.codex/skills/frontend-testing`

---
name: frontend-testing
description: Design and write frontend tests across unit, component, integration, and E2E layers using tools such as Jest, Vitest, Testing Library, Playwright, and Cypress.
metadata:
  source_dir: frontend-testing-1.0.1
---

# 前端测试（Frontend Testing）

帮助设计测试策略、编写单元/组件/集成/E2E 测试，以及 mock、断言与覆盖率考量。

## 触发场景

- 用户说「写测试」「单元测试」「组件测试」「E2E」「Jest」「Vitest」「Testing Library」
- 需求「提高覆盖率」「回归不放心」「改完怕坏」
- 已有测试框架，需要补用例或重构测试

## 测试分层与选型

| 类型 | 适用 | 常用工具 | 关注点 |
|------|------|----------|--------|
| 单元 | 纯函数、工具、hooks | Jest / Vitest | 输入输出、边界、副作用 |
| 组件 | 组件渲染与交互 | React Testing Library / Vue Test Utils | 用户行为、可访问性、状态 |
| 集成 | 多模块/请求/路由 | Jest+MSW / Vitest+MSW | 流程、接口 mock、错误态 |
| E2E | 关键用户路径 | Playwright / Cypress | 真实浏览器、稳定选择器、环境 |

## 执行流程

### 1. 先搞清楚用户要测什么

| 用户描述 | 实际需求 | 第一步 |
|---------|---------|-------|
| 「写测试」「补测试」 | 不知道从哪里开始 | 问：被测对象是什么（函数/组件/页面流程）？现有测试框架是什么？ |
| 「这个函数怎么测」「这个组件怎么测」 | 具体对象的测试 | 直接读代码，给出用例列表 + 关键用例的代码 |
| 「测试跑不过」「mock 不生效」 | 具体 bug | 看报错信息，定位问题，不要先讲测试理论 |
| 「覆盖率不够」 | 提高覆盖率 | 先问：覆盖率卡在哪个文件/模块？不要盲目追 100% |
| 「用 Jest 还是 Vitest」 | 选型 | 给明确推荐：新项目用 Vitest（更快、ESM 原生支持）；已有 Jest 的项目不要为了换而换 |

### 2. 拿到被测对象后，按这个顺序设计用例

**第一步：识别测试类型**
- 纯函数/工具函数 → 单元测试，直接测输入输出
- React/Vue 组件 → 组件测试，用 Testing Library 模拟用户行为
- 涉及接口/路由/多组件协作 → 集成测试，用 MSW mock 接口
- 关键用户路径（登录、下单、支付）→ E2E，用 Playwright

**第二步：列用例，覆盖这四类场景**
- 正向：主流程能跑通
- 边界：空值、最大值、特殊字符
- 异常：接口失败、权限不足、超时
- 交互：点击、输入、提交、取消（组件测试）

**第三步：给代码，不要只给用例列表**

至少给出 1-2 个完整的测试用例代码，包含 mock 设置、断言、cleanup。

### 3. 遇到这些情况，按以下方式处理

**用户没有测试框架**
→ 推荐：Vitest + React Testing Library + MSW（接口 mock）+ Playwright（E2E）
→ 给出安装命令和最小配置，不要只说「安装 X」

**组件测试找不到元素**
→ 优先用 `getByRole`（语义化，最稳定）
→ 其次 `getByLabelText`（表单）、`getByText`
→ 最后才用 `getByTestId`（加 `data-testid`）
→ 不要用 `querySelector`，测试不应该依赖 CSS 类名

**异步测试不稳定**
→ 用 `waitFor` 等待断言，不要用 `setTimeout`
→ 用 `findBy*` 代替 `getBy*` 处理异步渲染
→ 确保每个测试后清理 mock（`afterEach(() => server.resetHandlers())`）

**不知道 mock 什么**
→ 只 mock 系统边界：HTTP 请求（MSW）、时间（`vi.setSystemTime`）、环境变量
→ 不要 mock 被测模块内部的函数，那样测的是 mock 不是代码

### 4. 覆盖率的正确用法

- 覆盖率是发现**没测到的路径**的工具，不是目标
- 80% 覆盖率但覆盖了核心路径 > 100% 覆盖率但全是无意义的 snapshot
- 看覆盖率报告时，重点看**分支覆盖率**（branch coverage），不是行覆盖率

## 输出模板

```markdown
## 测试方案 / 用例说明

### 范围与工具
- 被测对象：…
- 框架：Jest / Vitest / RTL / Playwright / …

### 用例列表
| 场景 | 类型 | 要点 |
|------|------|------|
| … | 单元/组件/集成/E2E | … |

### Mock 与环境
- 接口：MSW handlers / …
- 路由/时间：…

### 示例代码（可选）
- 关键 1–2 个用例的代码片段
```

## 项目相关

- React：RTL + Jest/Vitest；hooks 用 renderHook；路由用 MemoryRouter
- Vue：Vue Test Utils + Jest/Vitest；Composition API 同 renderHook 思路
- Next.js：可测 App Router 页面用 testing-library；API 用 MSW 或 node mock
- E2E：Playwright 优先（多浏览器、稳定）；选择器优先 role > text > testid
