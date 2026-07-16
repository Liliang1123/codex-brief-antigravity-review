# codex-brief-antigravity-review

[English](README.md) | [简体中文](README_cn.md)

`codex-brief-antigravity-review` is a Codex skill for writing scoped Antigravity/Codex prompts and reviewing diffs, reports, and evidence. It stays lightweight for standalone work and governs structured external-agent batches only after `openspec-superpower-change` hands them off.

It is intended for workflows where Codex should design, dispatch, and audit work, while a separate execution agent such as Antigravity CLI performs implementation under explicit file, command, and reporting boundaries.

## Highlights

- Writes or refines standalone task prompts, briefs, and checklists without requiring OpenSpec or Handoff state.
- Standalone Review requires an explicit user request, is request-scoped and findings-first, and is never auto-chained after change generation.
- Reviews ordinary diffs and evidence read-only without pretending to promote a governed batch.
- Converts approved implementation plans into attempt-specific batch briefs.
- Separates orchestration and review from implementation execution.
- Requires structured reports or abort reports from the external agent.
- Audits evidence before writing PASS, FAIL, or BLOCKED.
- Prevents false PASS claims when critical proof is missing.
- Preserves `FAIL`/`BLOCKED` attempt history and requires correction or recovery followed by another Review.
- Uses canonical `status.md` for shared state and returns final batch `PASS` to the change gate for final verification.
- Runs a current-revision Brief Preflight Review before dispatch.
- Uses schema-5 Handoff state and schema-2 evidence with product, instance,
  role, profile, provenance, Lease, and SHA-256 binding.
- Governs manually copied state-changing standard/strict Briefs through the same
  route and rejects same-instance self-review even for one product.
- Requires High Review of actual diffs, production wiring, claims/mechanisms,
  critical reruns, and an independent adversarial or business-chain probe.

## Why It Exists

Long implementation sessions are risky when a single agent owns every step. Common failure modes include:

- context overload and missed constraints;
- unclear planner/executor responsibility;
- missing raw evidence behind success claims;
- broad file edits outside the intended batch;
- skipped reruns of critical commands;
- advancing the next batch before the previous one is proven.

This skill creates a strict Brief -> Dispatch -> Report -> Review loop.

## Role Boundary

| Role | Responsibility |
|---|---|
| Codex standalone | Writes prompts/briefs/checklists or performs read-only diff/evidence review; no Handoff state or batch promotion. |
| Codex governor | Reads the approved plan, writes attempt briefs, dispatches the external agent, audits reports, reruns critical evidence, and writes PASS / FAIL / BLOCKED reviews. |
| External agent | Implements only the allowed scope, obeys forbidden files and abort rules, runs required checks, and writes a report. |
| Handoff Contract | Canonical `status.md` state for batch, attempt, lifecycle, blocker recovery, evidence, and final handback. |
| openspec-superpower-change | Owns request routing, OpenSpec approval status, risk profile, and implementation authorization before this skill takes over. |

Standalone use must not modify implementation. In handed-off use, Codex must not re-decide OpenSpec approval or risk classification.

## Caveman Output Mode

Caveman is a presentation and output-compression layer, not a governance
layer. It activates only after an explicit request such as `caveman`,
`少 token`, `更短`, or `更精简`. The base mode supports `lite`, `full`, and
`ultra`; `stop caveman` or `正常模式` disables persistent compression.

For this companion, Caveman may shorten Standalone prompt/Brief/checklist
wording, findings-first summaries, and user-facing explanations. Technical
terms, paths, commands, error strings, and required fields must remain exact.
Canonical Handoff state and governed Brief, Report, and Review artifacts keep
their standard templates. Compression must not remove lifecycle state,
artifact paths, evidence roles or results, instance bindings, revision
numbers, or SHA-256 constraints. Batch promotion and final handback rules
remain unchanged.

`caveman-commit`, `caveman-review`, and `caveman-compress` are specialized
skills for commit messages, review comments, and memory files. They provide no
routing, approval, evidence, lifecycle, batch-promotion, or completion
authority.

```text
caveman
/caveman lite
/caveman full
/caveman ultra
stop caveman
```

## Workflow

```text
Standalone: write/refine prompt or review diff/report -> return findings

Handed-off: read canonical Handoff Contract
-> read approved plan section for the current batch/attempt
-> write <NN>-attempt-<AA>-brief.md
-> bind canonical execution SHA-256 and Preflight Review the Brief
-> dispatch external agent
-> require attempt Report or Abort Report
-> audit report claims against evidence
-> rerun critical checks where possible
-> write step review: PASS / FAIL / BLOCKED
-> FAIL/BLOCKED: same batch, new attempt, review again
-> non-final PASS: next batch
-> final PASS: return to openspec-superpower-change for final verification
```

An explicitly requested standalone OpenSpec Review remains concise and checks:

- proposal scope;
- spec scenarios;
- design decisions and risks;
- task traceability; and
- cross-artifact consistency.

## Route Decision In Detail

There are two valid routes; a request must not drift from one into the other.

### Standalone Lightweight

Use this route only when the user explicitly asks for prompt/Brief/checklist
wording or a read-only Review of a diff, Report, evidence set, or OpenSpec
artifact. It returns wording or findings for that request only. It does not edit
project files, create or mutate `status.md`, dispatch an implementation batch,
promote lifecycle state, decide final completion, or auto-chain another Review
after producing an artifact. Any request to fix findings or change behavior
returns to `openspec-superpower-change`.

### Canonical Handoff

Use this route only when a valid canonical Handoff Contract already records the
router's approval, risk/evidence profile, batch/attempt, owners, and current
lifecycle state. This skill may then Preflight the current Brief, dispatch the
bound executor, audit the attempt Report, bind Review evidence, and record
`PASS`, `FAIL`, or `BLOCKED`. A failure stays in the same batch with a new
attempt; a non-final PASS may advance; a final batch PASS returns
`awaiting-final-verification` to the router. It never impersonates router
approval and never converts batch PASS into whole-task completion.

## Artifact Layout

| Artifact | Path |
|---|---|
| Brief | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-brief.md` |
| Report | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report.md` |
| Abort Report | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report-abort.md` |
| Status / Handoff Contract | `docs/agent-collab/<change-id>/status.md` |
| Review | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-attempt-<AA>-review.md` |
| Timeout Audit | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-attempt-<AA>-timeout-audit.md` |

## Evidence Profiles

| Profile | Typical Use |
|---|---|
| compact | Low-risk batches with focused commands and concise reports. |
| standard | Default implementation batches with function maps, data contracts, invariants, error matrices, RED/GREEN evidence, and business acceptance layers. |
| strict | Security, auth, permission, public API/schema, persistence, migration, deployment, rollback, or cross-tenant changes. |

## Repository Structure

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── brief-template.md
│   ├── report-template.md
│   ├── review-template.md
│   ├── agy-dispatch-template.md
│   ├── timeout-audit-template.md
│   └── handoff-contract.md
├── scripts/
│   └── validate_templates.py
└── tests/
    └── test_workflow_rules.py
```

## Key References

- `references/brief-template.md`: required brief sections and evidence expectations.
- `references/report-template.md`: external-agent implementation report format.
- `references/review-template.md`: PASS / FAIL / BLOCKED review contract.
- `references/agy-dispatch-template.md`: dispatch prompt and command structure.
- `references/timeout-audit-template.md`: timeout and missing-report audit format.
- `references/handoff-contract.md`: shared status contract between Codex and the external agent.

## Key Rules

- Every brief must list allowed files, forbidden files, abort conditions, report path, and critical evidence.
- External agents must not overwrite Handoff Contract fields owned by the router.
- Missing reports, missing critical evidence, missing raw artifacts, or unreachable dependencies are `BLOCKED`.
- Forbidden-scope edits, destructive git operations, or still-reproducing regressions are `FAIL`.
- Unit tests alone do not prove API, server, or real business success unless those layers are explicitly not applicable.
- Only `PASS` may advance the batch pointer or authorize the next brief.
- Every external profile requires non-blank step/final critical commands.
- Report and Review evidence must be project-relative, non-empty, SHA-256
  matched, and carry the schema-1 role/result/change/batch/attempt/source
  fingerprint manifest plus the producing agent identity and role.
- Portable changes to this Skill are incomplete until every declared required
  Codex/Antigravity/Grok runtime passes the shared cross-CLI sync gate.

## Installation

Copy or link this skill into your Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R codex-brief-antigravity-review "${CODEX_HOME:-$HOME/.codex}/skills/codex-brief-antigravity-review"
```

## Validation

Run validation after editing the skill:

```bash
"${PYTHON_BIN:-python3}" "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" /path/to/codex-brief-antigravity-review
PYTHONDONTWRITEBYTECODE=1 python3 /path/to/codex-brief-antigravity-review/scripts/validate_templates.py /path/to/codex-brief-antigravity-review
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s /path/to/codex-brief-antigravity-review/tests -v
```

Runtime status validation additionally accepts `--status <status.md>` with
`--artifact-root <project-root>` to verify referenced evidence files.
Transitions that introduce evidence should add `--previous-status <canonical-status>`;
`complete` requires it. Keep proposed/previous snapshots outside the project so
there is still exactly one canonical Handoff marker block.

`quick_validate.py` requires PyYAML; set `PYTHON_BIN` accordingly. The project validator and tests exercise the dependency-free fallback.

## Example Prompts

```text
Use codex-brief-antigravity-review to write the next implementation brief from the approved plan. Do not edit implementation files.
```

```text
Use codex-brief-antigravity-review to audit the latest external-agent report, rerun critical evidence where possible, and write a PASS / FAIL / BLOCKED review.
```

```text
Use codex-brief-antigravity-review to resume shared status and determine whether the next batch may start.
```

```text
Use codex-brief-antigravity-review standalone mode to improve this Antigravity task prompt. Do not create Handoff artifacts or modify project files.
```

## Maintenance Notes

- This skill works standalone for prompt/read-only review tasks and consumes routing decisions only for handed-off execution.
- Do not use Codex subagents as a substitute for the named external agent when external implementation was requested.
- Do not treat a report as proof; audit the evidence and rerun critical checks where possible.
- Do not advance shared status unless the review result is PASS.
- A final batch PASS is not task completion; return it to `openspec-superpower-change`.

## License

MIT. See [LICENSE](LICENSE).
