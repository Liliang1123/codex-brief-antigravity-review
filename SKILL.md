---
name: codex-brief-antigravity-review
description: "Use when Codex or another orchestrator must coordinate implementation through an external agent: writing step briefs, dispatching Antigravity CLI or other agents, reviewing reports, enforcing disk-based Brief/Report/Review records, or separating design/review from code execution. Triggers: 出 Brief, 外部 Agent 实施, Codex Review, 按协作流推进."
---

# Codex Brief & Antigravity CLI Review Change Gate

Use this skill to orchestrate and govern development changes when planning/review is decoupled from implementation. Codex acts as the **Orchestrator and Gatekeeper**, while Antigravity CLI (or any external agent) acts as the **Executor**.

Core principle: **Codex designs and reviews; external agents implement; every step leaves a physical audit trail.**

---

## 1. Core Responsibility

- **Decoupled Architecture**: When this skill is active, Codex SHALL NOT edit implementation files. Codex may only edit Brief, Review, planning, or design documentation unless the user explicitly switches back to Codex-implementation mode.
- **Physical Deliverables**: Every step of the collaboration must be documented physically on disk: Brief, Report, and Review.
- **Evidence-Based Gate**: Codex must rerun all verification commands marked `critical` in the Brief, and independently verify at least one non-critical command or changed behavior when possible, before granting passage to the next step.
- **External Agent Boundary**: Do not substitute Antigravity CLI with Codex multi-agents when the user explicitly requested external-agent implementation.
- **Executor Ownership Clarity**: Every next-step recommendation MUST explicitly name who executes each part: Codex, external agent (for example Antigravity CLI), or the user. Avoid ambiguous wording such as “we should continue” when responsibility matters.
- **Default External Execution**: Once the user chooses the Codex-design / external-agent-execution collaboration mode, complex implementation, code changes, E2E evidence collection, and heavy local runs default to the external agent. Codex owns Briefs, Reviews, verification spot-checks, gate decisions, and final guidance unless the user explicitly switches modes.

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
    G -->|Need Fix / 需修改| H[Update Brief or Dispatch Fix Prompt]
    H --> E
    G -->|Approved / 通过| I[Proceed to Next Step]
```

1. **State Synchronization**: Confirm the current `change-id` and step index `NN` (starting at `01`).
2. **Context Discovery**: Read project instructions, the active plan (`docs/superpowers/plans/YYYY-MM-DD-<change-id>.md`), and specifications (`openspec/changes/<change-id>/*`).
3. **Step Briefing**: Generate the implementation brief at `docs/agent-collab/<change-id>/<NN>-brief.md`.
4. **Task Dispatch**: Create the shell command to execute the brief with Antigravity CLI (`agy`) and present it to the user.
5. **Execution Reporting**: Read the implementation report at `docs/agent-collab/<change-id>/<NN>-report.md` or abort report at `docs/agent-collab/<change-id>/<NN>-report-abort.md`.
6. **Independent Verification**: Codex runs verification commands locally where possible to cross-check the reporter's claim.
7. **Quality Gate Review**: Write the final assessment to `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-review.md`.
8. **Fix Loop**: If the review conclusion is `需修改` (Need Fix), dispatch a correction request and return to step 5.
9. **Promotion**: If the review conclusion is `通过` (Approved), proceed to step `NN + 1`.

---

## 3. Physical Artifact Contract (物理落盘约定)

Use this path contract unless the user or project instructions explicitly override it:

| Artifact | Path |
|---|---|
| Step Brief | `docs/agent-collab/<change-id>/<NN>-brief.md` |
| Step Report | `docs/agent-collab/<change-id>/<NN>-report.md` |
| Abort Report | `docs/agent-collab/<change-id>/<NN>-report-abort.md` |
| Codex Review | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-review.md` |
| Plan | `docs/superpowers/plans/YYYY-MM-DD-<change-id>.md` |
| OpenSpec change | `openspec/changes/<change-id>/` |
| Timeout Audit | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-timeout-audit.md` |
| Status File | `docs/agent-collab/<change-id>/status.md` |

Brief and Report stay together in `docs/agent-collab/<change-id>/`. Codex-owned Review records and Timeout Audits stay in `docs/review/`. The Status File lives alongside Brief/Report to help new windows discover the current step and MUST be updated after each Review (or explaining blocking reasons in the Review).

---

## 4. Step State Machine (步骤推进规则)

- Step `NN` MUST start with `docs/agent-collab/<change-id>/<NN>-brief.md`.
- The external agent MUST produce either `<NN>-report.md` or `<NN>-report-abort.md`.
- If the external agent produces neither report nor abort report after the agreed timeout, Codex MUST stop waiting, inspect the worktree status, and write a timeout audit under `docs/review/` using `references/timeout-audit-template.md` before any next dispatch.
- Codex MUST write a Review before any next step is created.
- Only a Review conclusion of `通过` permits creating `<NN+1>-brief.md`.
- A Review conclusion of `有风险` permits continuation only when all conditions hold: risks do not touch OpenSpec-required categories, each risk has a concrete follow-up verification step, and the Review states next-step constraints explicitly.
- A Review conclusion of `需修改` blocks promotion; Codex must dispatch a fix prompt or create a revised Brief.

---

## 5. Non-negotiables (硬约束)

- **No Implementation Code by Codex**: Codex must not edit implementation files while this skill is active unless the user explicitly changes the collaboration mode.
- **No Implicit Substitution**: Do not replace Antigravity CLI or the named external agent with Codex subagents when external-agent implementation was requested.
- **Git Restrictions**: Never run `git add`, `git commit`, `git reset`, or `git clean` unless explicitly commanded by the user.
- **Scope Isolation**: Every Step Brief must explicitly list allowed target files (allow-list) and forbidden areas (block-list).
- **Structured Backup**: When modifying skill files or project templates, the executor must create a structured backup that preserves relative path directory structures (e.g., `codex-brief-antigravity-review/SKILL.md` instead of a flat list) under the backup directory.
- **Strict Review Output**: Every review must be persisted inside `docs/review/` and start with one of: `通过`, `有风险`, or `需修改`.
- **Abort Discipline**: If the executor hits a boundary violation, unclear failure, dependency need, architecture/spec change need, permission problem, or unsafe operation, it must stop and write `<NN>-report-abort.md`.
- **Dashboard Integrity**: If a status dashboard exists, only modify `development-log.json`. Do not edit generated markdown or HTML pages directly; compile them via scripts.

---

## 6. Step Brief Requirements

Every Step Brief must include:

- Change ID and step number.
- Executor role.
- Required reading list.
- Allowed files and forbidden files.
- Exact goals for the step only.
- Required commands and expected evidence, with critical verification commands clearly marked.
- Abort protocol and abort report path.
- Report path and report format.
- Gate conditions for Codex review.

Briefs should be narrow. If a step needs files outside the allow-list, the executor must abort instead of improvising.

### Fallback When Skill Is Unavailable (兜底规则)

- If the executing agent (Codex or external) cannot auto-trigger this skill, it SHOULD first attempt to manually read this `SKILL.md` from `~/.codex/skills/codex-brief-antigravity-review/SKILL.md` (or equivalent global installation path) before proceeding.
- If the skill file is still unreachable, the Step Brief MUST be self-contained: it must embed all critical boundary constraints (allow-list, block-list, abort protocol, verification commands) so the agent can execute independently without skill context.
- Codex SHOULD verify skill activation at the start of each new window or session. If activation cannot be confirmed, Codex must include a note in the Brief stating that the executor should treat the Brief as the sole source of truth for execution boundaries.

### Lightweight Status File Convention (状态文件约定)

To help new windows or sessions resume an in-progress collaboration without requiring the user to manually restate the `change-id` and current step:

- After every persisted Codex Review (conclusion `通过`, `有风险`, or `需修改`), Codex MUST update `docs/agent-collab/<change-id>/status.md` with the current step number, conclusion, and next-step owner. If Codex cannot write this file, the Review MUST explain the blocking reasons or risks.
- This file is **mandatory** for state synchronization across windows. If the file cannot be written due to environment or permissions, Codex must explicitly document this block in the Review.
- Format:
  ```
  change-id: <change-id>
  current-step: <NN>
  last-conclusion: 通过 / 有风险 / 需修改
  next-step-owner: Codex / external agent / user
  updated: YYYY-MM-DD HH:MM
  ```
- A new Codex window discovering this file may use it to auto-populate the `change-id` and step index for context discovery (§2 step 1).

---

## 7. Report and Abort Requirements

A normal Step Report must include:

- Conclusion: `通过` / `有风险` / `需修改`.
- Changed files.
- Implementation summary.
- Verification commands and results, including all critical commands.
- Diff summary with `git diff --stat` and key changed hunks.
- RED/GREEN evidence when TDD applies.
- Scope deviation status.
- Remaining risks and questions for Codex.

An Abort Report must include:

- Conclusion beginning with `需修改`.
- Abort reason.
- Already executed operations.
- Error logs or blocked command output.
- Current worktree status.
- Required Codex decision.

Codex must treat an abort report as a blocking gate until reviewed.

---

## 8. Codex Review Requirements

Every Codex Review must include:

- Conclusion: `通过` / `有风险` / `需修改`.
- Review scope with links or paths to Brief, Report, changed files, plan, and specs.
- Code facts with file/line evidence when implementation files changed.
- Positive checks.
- Negative searches / scope drift checks.
- Independent verification records, including every critical command from the Brief or a blocking explanation for commands that cannot run locally.
- Residual risks.
- Next-step permission: yes/no and constraints.
- Next-step execution ownership: explicitly state which tasks belong to Codex, the external agent, and the user.

Codex must not approve a step solely because the external agent claims success. Verification evidence comes before approval.

---

## 9. agy Dispatch Standard (agy 调用与调度规范)

When dispatching execution tasks, Codex must output the following command block:

```bash
agy --print-timeout 30m --print "$(cat <<'EOF'
项目路径：<project-path>

请按以下 Brief 执行 <change-id> Step <NN>：
docs/agent-collab/<change-id>/<NN>-brief.md

执行完成后，请生成报告：
docs/agent-collab/<change-id>/<NN>-report.md

如果遇到越界、阻塞或需要 Codex 判断的问题，请停止并生成：
docs/agent-collab/<change-id>/<NN>-report-abort.md

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

## 10. Skill Maintenance Notes

When updating this skill itself:

- Read `SKILL.md` before changing the skill package.
- Do not modify `references/` or `agents/` without updating `SKILL.md` or explaining why no navigation change is needed.
- Validate template formatting before completion.
- Never run `git add` or `git commit` unless the user explicitly requests it.
- Do not weaken the Brief → Dispatch → Report → Review quality loop during self-evolution.

---

## 11. Reference Guide

- **Step Brief Template**: See `references/brief-template.md`
- **Step Report Template**: See `references/report-template.md`
- **Step Review Template**: See `references/review-template.md`
- **Dispatch Template**: See `references/agy-dispatch-template.md`
- **Timeout Audit Template**: See `references/timeout-audit-template.md`
