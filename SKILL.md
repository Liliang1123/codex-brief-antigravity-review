---
name: codex-brief-antigravity-review
description: "Use when writing or refining Antigravity/Codex task prompts or briefs, reviewing diffs/reports/evidence, auditing PASS/FAIL/BLOCKED decisions, or governing an already-handed-off external-agent batch; also trigger on 任务提示、实施 Brief、Codex Review、diff 复核、Report 审计、外部批次复核."
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
   implementation, behavior change, OpenSpec/risk decision, or final task
   completion decision.

“Review and fix” is not standalone review. Do not silently switch from review
to implementation.

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

Consume the router-owned contract from
`docs/agent-collab/<change-id>/status.md`. Do not re-decide mode, approval,
risk, planned batches, or final verification commands. Missing, stale,
duplicated, contradictory, or unparsable canonical state is `BLOCKED`.

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
2. Transition canonical status to `ready-for-execution`, increment its
   revision, then write the current attempt Brief using that execution
   fingerprint and dispatch the named agent.
3. Require the attempt Report or Abort Report using the execution revision;
   then transition status to `ready-for-review` with a new review revision.
4. Audit scope, evidence, critical commands, production wiring, and required
   acceptance layers. Rerun critical commands where possible.
5. Write a Review whose first line is exactly `# Review Result: PASS`,
   `# Review Result: FAIL`, or `# Review Result: BLOCKED`.
6. Apply the transition:
   - `FAIL` -> same batch `needs-fix`, increment attempt, create a correction
     Brief, verify, and Review again;
   - `BLOCKED` -> same batch `blocked`, record owner/reason/resume condition,
     then use a fresh attempt and Review after recovery;
   - non-final `PASS` -> increment one batch, reset attempt, next Brief;
   - final `PASS` -> `awaiting-final-verification`, return to
     `openspec-superpower-change` without claiming task completion.

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

## Non-Negotiables

- Codex does not edit implementation files while this skill is active; return
  to the change gate if the user requests implementation.
- Do not substitute Codex subagents for the named external executor.
- Every governed Brief lists allowed/forbidden files, abort conditions, attempt
  Report path, critical evidence, and canonical status fingerprint.
- External agents must not edit canonical status or readonly fields.
- Missing Report/evidence/required real acceptance is `BLOCKED`.
- Scope violation, destructive git operation, or reproduced regression is
  `FAIL`.
- Unit tests alone never prove API/server/real business success unless those
  layers are `not-applicable`.
- Never advance a batch or claim completion from `FAIL`, `BLOCKED`, or stale
  evidence.
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
