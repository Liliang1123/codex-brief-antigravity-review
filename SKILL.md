---
name: codex-brief-antigravity-review
description: "Use for standalone non-state-changing Antigravity/Codex prompt or brief wording, read-only diff/report/evidence review that does not request fixes or decide final completion, or dispatch/review/resume of an external-agent batch with an existing valid Handoff Contract. Do not use for file edits, review-and-fix, final completion, or workflow/template changes. 可按用户要求用 caveman 风格压缩表达。"
---

# Codex Brief & Antigravity Review

Focused prompt and review skill with two mutually exclusive paths. It stays
lightweight for standalone wording/read-only review and becomes an external
execution governor only when a valid Handoff Contract already exists.

## Route Selection

1. Use **Standalone Lightweight** when the request only writes/refines a
   prompt, Brief, checklist, or performs read-only diff/Report/evidence review.
2. Use **Handed-off External Execution** when canonical `status.md` contains a
   valid Handoff Contract and the task is dispatch, Report audit, retry,
   recovery, or batch promotion.
3. Return to `openspec-superpower-change` before any file modification,
   implementation, behavior change, workflow/template edit, OpenSpec/risk
   decision, or final task completion decision.

“Review and fix” is not standalone review. Do not silently switch from review
to implementation.

## Token-lean / Caveman output mode

`caveman` 在本 skill 里仅用于**输出压缩**，不参与治理决策。

- 触发：用户明确要求“少 token/更短/像 caveman 说”。
- 允许：`Standalone Lightweight` 的提示词、brief/review 结论、可执行项清单。
- 禁止：篡改 `SKILL.md`、`references/handoff-contract.md`、`reports`/`reviews`
  的结构化必填字段；不能代替证据复核。
- 生成 `Handoff Contract`、`Brief/Report/Review` 证明链时，使用标准模板内容；
  用户侧可读解释可再压缩，不得省略状态、文件、证据命名和哈希约束。

## Standalone Lightweight

This path does not require an OpenSpec proposal, Handoff Contract, Superpowers
plan, or collaboration artifact. Produce the requested prompt/Brief/checklist
or a findings-first read-only review directly in chat unless the user requests
another output location.

- State the reviewed scope and evidence actually inspected.
- For a diff review, list actionable findings by severity and location.
- Do not write batch `PASS`, advance shared status, or imply implementation was
  verified when no governed batch exists.
- If the user asks to save files, apply fixes, dispatch implementation, or
  change workflow behavior, return to the change gate first.

## Handed-off External Execution

Consume the router-owned schema-version-4 contract from
`docs/agent-collab/<change-id>/status.md`. Do not re-decide mode, approval,
risk, planned batches, or final verification commands. Missing, stale,
duplicated, contradictory, or unparsable canonical state is `BLOCKED`.

The contract binds canonical `executor_agent`, `independent_reviewer_agent`,
and `decision_owner` identities. Codex remains the decision owner. Antigravity
CLI or Grok CLI may execute or independently Review a batch, but an auxiliary
result is advisory evidence until Codex validates the identity/role binding,
reruns required evidence where possible, and records the transition.

### Artifact Paths

| Artifact | Path |
|---|---|
| Canonical status | `docs/agent-collab/<change-id>/status.md` |
| Brief | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-brief.md` |
| Report | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report.md` |
| Abort Report | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report-abort.md` |
| Review | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-attempt-<AA>-review.md` |
| Timeout Audit | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-attempt-<AA>-timeout-audit.md` |

Attempt-specific paths preserve history. Never overwrite evidence from an
earlier `FAIL`, `BLOCKED`, or timeout attempt.

### State Machine

1. Validate canonical contract revision, lifecycle, batch, attempt, and owner.
2. Transition canonical status to `ready-for-execution`, increment its revision,
   hash the canonical status file, and write the current attempt Brief with that
   execution revision and canonical SHA-256.
3. Run a current-revision **Preflight Review** before dispatch for scope,
   acceptance, exact commands, rollback/stop conditions, Git authority, and
   placeholders. Preflight uses only `PASS`/`BLOCKED`; any finding moves to
   `blocked`, revises the Brief in a new attempt, and must be reviewed again.
   Unchanged revisions do not repeat ceremony. Dispatch only after Preflight
   PASS.
4. Require the attempt Report or Abort Report using the execution revision and
   matching SHA-256;
   then transition status to `ready-for-review` with a new review revision.
5. Audit scope, evidence, critical commands, production wiring, and required
   acceptance layers. When an independent auxiliary reviewer is assigned,
   consume its Review only if its identity and role match the contract and differ
   from the executor. Rerun critical commands where possible.
6. Write a Review whose first line is exactly `# Review Result: PASS`,
   `# Review Result: FAIL`, or `# Review Result: BLOCKED`.
7. Apply the transition:
   - `FAIL` -> same batch `needs-fix`, increment attempt, create a correction
     Brief, verify, and Review again;
   - `BLOCKED` -> same batch `blocked`, record owner/reason/resume condition,
     then use a fresh attempt and Review after recovery;
   - non-final `PASS` -> increment one batch, reset attempt, next Brief;
   - final `PASS` -> `awaiting-final-verification`, return to
     `openspec-superpower-change` without claiming task completion.

Before applying any transition that introduces an artifact, write the proposed
status outside the project, run the project validator with current canonical
status as `--previous-status`, preserve the PASS output, then atomically replace
the one canonical block. Never persist the proposed/previous snapshot in the
project.

Only Review `PASS` may promote a batch. `FAIL` and `BLOCKED` must be reviewed
again after correction or recovery; a chat acknowledgment is not closure.

## Evidence Profiles

- `compact`: concise Brief/Report/Review and focused commands; omit heavy tables
  unless the contract needs them.
- `standard`: function map, data contract, invariants, error matrix, RED/GREEN,
  production wiring, `step_critical`, and an independent behavior check.
- `strict`: required real security/API/schema/migration/rollback/business-chain
  evidence; mocks and unit tests cannot substitute for required real layers.

The governor runs `step_critical` for each attempt. The router runs
`final_critical` after final batch Review PASS; later implementation changes
invalidate that final evidence.

Every external profile has at least one non-blank `step_critical` and
`final_critical`. Status references the attempt Report and Review by safe
project-relative path plus SHA-256. Each artifact embeds a schema-1 manifest
binding role, result, change, batch, attempt, source canonical
revision/SHA-256, producing agent identity, and producing role. Review records
from/to revision and canonical SHA-256 transition evidence; `complete` runtime
validation requires the actual previous status.

## Non-Negotiables

- Codex does not edit implementation files while this skill is active; return
  to the change gate if the user requests implementation.
- Do not substitute Codex subagents for the named external executor.
- Every governed Brief lists allowed/forbidden files, abort conditions, attempt
  Report path, critical evidence, and canonical status fingerprint.
- External agents must not edit canonical status or readonly fields.
- External executor and independent reviewer identities must match the canonical
  assignment; standard/strict work forbids same-agent self-review.
- Auxiliary `PASS` is advisory. Only Codex may record the authoritative batch or
  final decision.
- Missing Report/evidence/required real acceptance is `BLOCKED`.
- Scope violation, destructive git operation, or reproduced regression is
  `FAIL`.
- Unit tests alone never prove API/server/real business success unless those
  layers are `not-applicable`.
- Never advance a batch or claim completion from `FAIL`, `BLOCKED`, or stale
  evidence.
- Every actionable Review finding must be fixed and reviewed again. Record a
  non-actionable observation only as an accepted residual risk with an owner or
  decision; do not leave it as an unresolved finding under PASS.
- Never run `git add`, `git commit`, `git reset`, or `git clean` unless the user
  explicitly commands it; never push without explicit approval.

## Templates

- `references/brief-template.md`
- `references/report-template.md`
- `references/review-template.md`
- `references/agy-dispatch-template.md`
- `references/timeout-audit-template.md`
- `references/handoff-contract.md`

## Maintenance

Create a temporary structured backup before editing. Editorial changes that do
not alter triggers, required fields, lifecycle, evidence, or PASS conditions may
use compact Direct Change. Semantic workflow changes are Major Self-Evolution
and must return to `openspec-superpower-change` for an approved contract,
RED/GREEN forward-test, validation, Review, rollback, runtime/source sync, and
final reporting. Remove temporary backups only after all checks pass.
