# codex-brief-antigravity-review

A reusable Codex Skill for decoupling planning, task dispatching, and quality review from direct implementation execution.

[English](#english) | [中文说明](#中文说明)

---

## English

`codex-brief-antigravity-review` is a governance and orchestration framework designed for AI-assisted software engineering. 

### Why Decouple Planning from Execution?

In complex or legacy codebases, allowing a single AI agent to plan, execute, and verify its own code often leads to context explosion, uncontrolled git modifications, and cumulative regression bugs. 

This skill enforces a strict **Decoupled Architecture**:
1. **Codex (Orchestrator)**: Focuses on interpreting OpenSpec plans, writing structured task briefs, and performing rigorous code reviews. It is restricted from direct file edits.
2. **Antigravity CLI / agy (Executor)**: Runs locally under strict file boundaries to implement the brief, test changes, and generate structured reports.

```
+------------------+                   +--------------------+
|  Codex (Planner) | --[Step Brief]--> |  Antigravity CLI   |
|                  |                   |    (Executor)      |
|  [Gatekeeper]    | <--[Step Report]- |                    |
+------------------+                   +--------------------+
         |
  [Runs Verification]
         |
  [Writes Step Review] ---> (Pass / Need Fix)
```

### Installation

To install this skill locally, clone it and link or copy it to your Codex configuration folder:

```bash
mkdir -p ~/.codex/skills
ln -s "/path/to/codex-brief-antigravity-review" ~/.codex/skills/codex-brief-antigravity-review
```

### File Structure

- `SKILL.md`: Core routing, boundaries, and hard constraints.
- `agents/openai.yaml`: UI metadata for agent integration.
- `references/`:
  - `brief-template.md`: Template for defining step scopes, allowlists, blocklists, and verification steps.
  - `report-template.md`: Template for execution results, deviations, and residual risks.
  - `review-template.md`: Template for step approval and local verification gates.
  - `agy-dispatch-template.md`: Template for the command used to invoke `agy`.

---

## 中文说明

`codex-brief-antigravity-review` 是为 AI 辅助软件工程设计的轻量级治理与协作流框架。

### 为什么将“规划评审”与“代码实施”分离？

在大型或复杂的现有代码库中，如果让同一个大模型同时负责方案规划、代码修改以及自我审查，往往容易导致以下问题：
1. **上下文过载**：因阅读大量代码及日志导致推理能力下降。
2. **代码失控**：Agent 擅自进行大范围无序的修改或未授权的 `git` 操作。
3. **缺乏客观审计**：自我审查容易遗漏边界缺陷。

本项目通过固化 **规划（Codex）与实施（Antigravity CLI）分离** 的协作流来解决这一痛点：
- **Codex (协调与门禁)**：只负责解析计划、编写单步 Brief、派发指令、运行本地二次重测以及编写 Review 报告。**禁止直接编辑业务代码**。
- **Antigravity CLI / agy (执行器)**：在被明确限制的目录和文件沙箱内，执行具体代码修改，跑通测试，并回传结构化执行报告。

### 工作流步骤

1. **出 Brief**：Codex 依据 OpenSpec 和 Plan，生成 `docs/agent-collab/<change-id>/<NN>-brief.md`。
2. **派发任务**：Codex 生成带有路径和边界约束的 `agy` 调度指令。
3. **回收 Report**：Antigravity CLI 完成任务，并写回报告 `docs/agent-collab/<change-id>/<NN>-report.md`。
4. **验证与 Review**：Codex 在本地复现验证，并在 `docs/review/` 下输出评审结果。
5. **放行或返工**：根据结论（`通过` / `需修改`），决定是进入下一阶段还是触发修复循环。

### 本地安装

```bash
mkdir -p ~/.codex/skills
ln -s "/Users/elvis/file/develop/opensource/codex-brief-antigravity-review" ~/.codex/skills/codex-brief-antigravity-review
```

---

## License

This project is open-sourced under the [MIT License](LICENSE).
