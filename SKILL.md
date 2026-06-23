---
name: codex-brief-antigravity-review
description: Use when Codex manages planning, specification, and review, while delegating the implementation tasks to Antigravity CLI (agy) or other external execution agents. It guides Codex to read OpenSpec plans, write Step Briefs, dispatch agy commands, wait for Step Reports, perform independent verification, and write Review gate records. Triggers include "Codex 出 Brief", "Antigravity CLI 实施", "Codex Review", "其他 agent 实施", "按 Brief/Report 协作流推进", or any request to separate orchestration/governance from execution.
---

# Codex Brief & Antigravity CLI Review Change Gate

Use this skill to orchestrate and govern development changes when planning/review is decoupled from implementation. Codex acts as the **Orchestrator and Gatekeeper**, while Antigravity CLI (or any external agent) acts as the **Executor**.

---

## 1. Core Responsibility

- **Decoupled Architecture**: Codex must NOT write or modify implementation code directly unless explicitly requested by the user. 
- **Physical Deliverables**: Every step of the collaboration must be documented physically on disk (Brief, Report, and Review).
- **Evidence-Based Gate**: Codex must rerun verification commands locally on the implementation report before granting passage to the next step.

---

## 2. Standard Collaboration Flow (标准协作流程)

```mermaid
graph TD
    A[Confirm Change ID & Step NN] --> B[Read Controlling Artifacts]
    B --> C[Write Step Brief]
    C --> D[Generate & Dispatch agy Command]
    D --> E[Wait & Read Step Report]
    E --> F[Codex Local Verification]
    F --> G[Codex Write Step Review]
    G -->|Need Fix / 需修改| H[Update Brief & Dispatch Fix Prompt]
    H --> E
    G -->|Approved / 通过| I[Proceed to Next Step]
```

1. **State Synchronization**: Confirm the current `change-id` and step index `NN` (starting at `01`).
2. **Context Discovery**: Read project instructions, the active plan (`docs/superpowers/plans/YYYY-MM-DD-<change-id>.md`), and specifications (`openspec/changes/<change-id>/*`).
3. **Step Briefing**: Generate the implementation brief at `docs/agent-collab/<change-id>/<NN>-brief.md`.
4. **Task Dispatch**: Create the shell command to execute the brief with Antigravity CLI (`agy`) and present it to the user.
5. **Execution Reporting**: Read the implementation report at `docs/agent-collab/<change-id>/<NN>-report.md`.
6. **Independent Verification**: Codex runs verification commands locally to cross-check the reporter's claim.
7. **Quality Gate Review**: Write the final assessment to `docs/review/YYYY-MM-DD-<change-id>-step-NN-review.md`.
8. **Fix Loop**: If the review conclusion is `需修改` (Need Fix), dispatch a correction request and return to step 5.
9. **Promotion**: If the review conclusion is `通过` (Approved), proceed to step `NN + 1`.

---

## 3. Non-negotiables (硬约束)

- **No Implicit Substitution**: Do not substitute Antigravity CLI with Codex multi-agents if the user explicitly requested external agent implementation.
- **Git Restrictions**: Never run `git add`, `git commit`, `git reset`, or `git clean` unless explicitly commanded by the user.
- **Scope Isolation**: Every Step Brief must explicitly list the allowed target files (allow-list) and forbidden areas (block-list).
- **Strict Review Output**: Every review must be persisted inside `docs/review/` and start with one of the following conclusions: `通过` (Approved), `有风险` (Risky), or `需修改` (Need Fix).
- **Dashboard Integrity**: If a status dashboard exists, only modify `development-log.json`. Do not edit generated markdown or HTML pages directly; these should be compiled via scripts.

---

## 4. agy Dispatch Standard (agy 调用与调度规范)

When dispatching execution tasks, Codex must output the following command block:

```bash
agy --print-timeout 30m --print "$(cat <<'EOF'
项目路径：<project-path>

请按以下 Brief 执行 <change-id> Step <NN>：
docs/agent-collab/<change-id>/<NN>-brief.md

执行完成后，请生成报告：
docs/agent-collab/<change-id>/<NN>-report.md

硬性要求：
- 只允许修改 Brief 指定文件
- 禁止修改 Brief 禁止范围
- 禁止 git add / git commit / git reset / git clean
- 必须运行 Brief 中列出的验证命令
- 报告需包含修改文件、验证命令与结果、是否偏离 Brief、剩余风险
EOF
)"
```

---

## 5. Reference Guide

- **Step Brief Template**: See `references/brief-template.md`
- **Step Report Template**: See `references/report-template.md`
- **Step Review Template**: See `references/review-template.md`
- **Dispatch Template**: See `references/agy-dispatch-template.md`
