# codex-brief-antigravity-review

[English](README.md) | [简体中文](README_cn.md)

`codex-brief-antigravity-review` is a Codex skill for writing scoped Antigravity/Codex prompts and reviewing diffs, reports, and evidence. It stays lightweight for standalone work and governs structured external-agent batches only after `openspec-superpower-change` hands them off.

It is intended for workflows where Codex should design, dispatch, and audit work, while a separate execution agent such as Antigravity CLI performs implementation under explicit file, command, and reporting boundaries.

## Highlights

- Writes or refines standalone task prompts, briefs, and checklists without requiring OpenSpec or Handoff state.
- Reviews ordinary diffs and evidence read-only without pretending to promote a governed batch.
- Converts approved implementation plans into attempt-specific batch briefs.
- Separates orchestration and review from implementation execution.
- Requires structured reports or abort reports from the external agent.
- Audits evidence before writing PASS, FAIL, or BLOCKED.
- Prevents false PASS claims when critical proof is missing.
- Preserves `FAIL`/`BLOCKED` attempt history and requires correction or recovery followed by another Review.
- Uses canonical `status.md` for shared state and returns final batch `PASS` to the change gate for final verification.
- Runs a current-revision Brief Preflight Review before dispatch.
- Uses schema-3 project-relative Report/Review paths plus SHA-256 fingerprints.

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
  fingerprint manifest.

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
