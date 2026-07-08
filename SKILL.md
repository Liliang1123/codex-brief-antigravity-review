---
name: codex-brief-antigravity-review
description: "Use when coordinating external-agent implementation, writing or breaking down implementation/task/step/batch briefs, dispatching Antigravity CLI, auditing reports or reviews, resuming shared status, or checking PASS evidence; also trigger on 实施 Brief、任务拆解、外部 Agent 实施、Codex Review、Report 审计."
---

# Codex Brief & Antigravity Review Gate

External execution governor for changes routed by `openspec-superpower-change`.
Codex designs and reviews; the named external agent implements; every batch
leaves auditable Brief, Report, Review, status, and evidence.

## Role Boundary

- Consume the existing Handoff Contract from `references/handoff-contract.md`.
- Do not re-decide OpenSpec route, approval status, or risk profile.
- Turn one complete business batch into a Brief.
- Dispatch the external agent and require a Report or Abort Report.
- Audit claims as evidence, then write `PASS`, `FAIL`, or `BLOCKED`.
- Update shared status and authorize the next batch only after `PASS`.

If the Handoff Contract is missing, contradictory, stale, or has multiple marker
blocks, stop with BLOCKED and return to `openspec-superpower-change` or the
user. Do not invent a new mode, approval status, or risk profile.

## Artifact Paths

| Artifact | Path |
|---|---|
| Brief | `docs/agent-collab/<change-id>/<NN>-brief.md` |
| Report | `docs/agent-collab/<change-id>/<NN>-report.md` |
| Abort Report | `docs/agent-collab/<change-id>/<NN>-report-abort.md` |
| Status / Handoff Contract | `docs/agent-collab/<change-id>/status.md` |
| Review | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-review.md` |
| Timeout Audit | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-timeout-audit.md` |

## State Machine

1. Read the Handoff Contract and active plan section for the current batch.
2. Write `<NN>-brief.md` with allow-list, block-list, profile, function map,
   data contract, invariants, error matrix, TDD path, wiring, acceptance layers,
   critical commands, abort path, and report path.
3. Dispatch the external agent using `references/agy-dispatch-template.md`.
4. Require `<NN>-report.md` or `<NN>-report-abort.md`.
5. Review the Report, rerun critical commands where possible, and independently
   check at least one behavior for `standard` or all required real layers for
   `strict`.
6. Write a Review whose first line is exactly `# Review Result: PASS`,
   `# Review Result: FAIL`, or `# Review Result: BLOCKED`.
7. Only `PASS` may advance `current_batch` or create the next Brief.

## Evidence Profiles

- `compact`: concise Brief/Report/Review; focused commands only; no heavy tables
  unless needed for the contract.
- `standard`: function map, data contract, invariants, error matrix, RED/GREEN
  evidence, production wiring, `step_critical`, and business acceptance layers.
  `final_critical` runs once at final batch unless later code changes invalidate
  the evidence.
- `strict`: security, auth, permission, public API/schema, persistence,
  migration, deletion/recovery, deployment/rollback, cross-tenant boundaries.
  Mock or unit-only evidence cannot replace required real acceptance.

## Non-Negotiables

- Codex does not edit implementation files while this skill is active unless the
  user explicitly changes mode.
- Do not substitute Codex subagents for the named external agent when external
  implementation was requested.
- Never run `git add`, `git commit`, `git reset`, or `git clean` unless the user
  explicitly commands it.
- Every Brief must list allowed files, forbidden files, abort conditions, report
  path, and critical evidence.
- External agents must not overwrite readonly Handoff Contract fields: `mode`,
  `approval_status`, `risk_profile`.
- Missing Report, missing critical evidence, missing required raw artifact,
  missing API/server/business-chain proof, or unreachable dependency is
  `BLOCKED`.
- Forbidden-scope edits, destructive git operations, or real regression still
  reproducing the failure are `FAIL`.
- Unit tests or `pytest` alone never prove API/server/real business success
  unless the Brief marks those layers `not-applicable`.

## Templates

- `references/brief-template.md`
- `references/report-template.md`
- `references/review-template.md`
- `references/agy-dispatch-template.md`
- `references/timeout-audit-template.md`
- `references/handoff-contract.md`

## Maintenance

When changing this skill, read `SKILL.md`, preserve the Brief -> Dispatch ->
Report -> Review loop, update templates and validator together, create a
temporary structured backup before editing, validate `scripts/validate_templates.py`,
then remove temporary backups and `.bak.*` files after validation passes.
Long-term history is managed by
`/Users/elvis/file/develop/opensource/codex-brief-antigravity-review`; never
leave backup copies under `/Users/elvis/.codex/skills/`, and do not push or run
prohibited git commands without explicit user approval.
