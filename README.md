# codex-brief-antigravity-review

[English](README.md) | [简体中文](README_cn.md)

`codex-brief-antigravity-review` is a Codex skill for coordinating external-agent implementation with structured briefs, execution reports, independent reviews, and evidence gates.

It is intended for workflows where Codex should design, dispatch, and audit work, while a separate execution agent such as Antigravity CLI performs implementation under explicit file, command, and reporting boundaries.

## Highlights

- Converts approved implementation plans into batch-level briefs.
- Separates orchestration and review from implementation execution.
- Requires structured reports or abort reports from the external agent.
- Audits evidence before writing PASS, FAIL, or BLOCKED.
- Prevents false PASS claims when critical proof is missing.
- Maintains a shared Handoff Contract for batch status and promotion control.

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
| Codex | Reads the approved plan, writes briefs, dispatches the external agent, audits reports, reruns critical evidence where possible, and writes PASS / FAIL / BLOCKED reviews. |
| External agent | Implements only the allowed scope, obeys forbidden files and abort rules, runs required checks, and writes a report. |
| Handoff Contract | Holds shared state: mode, approval status, risk profile, current batch, evidence profile, and promotion rules. |
| openspec-superpower-change | Owns request routing, OpenSpec approval status, risk profile, and implementation authorization before this skill takes over. |

Codex must not re-decide OpenSpec approval or risk classification while this skill is active.

## Workflow

```text
Read Handoff Contract
-> read approved plan section for the current batch
-> write <NN>-brief.md
-> dispatch external agent
-> require <NN>-report.md or <NN>-report-abort.md
-> audit report claims against evidence
-> rerun critical checks where possible
-> write step review: PASS / FAIL / BLOCKED
-> advance only after PASS
```

## Artifact Layout

| Artifact | Path |
|---|---|
| Brief | `docs/agent-collab/<change-id>/<NN>-brief.md` |
| Report | `docs/agent-collab/<change-id>/<NN>-report.md` |
| Abort Report | `docs/agent-collab/<change-id>/<NN>-report-abort.md` |
| Status / Handoff Contract | `docs/agent-collab/<change-id>/status.md` |
| Review | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-review.md` |
| Timeout Audit | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-timeout-audit.md` |

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
└── scripts/
    └── validate_templates.py
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

## Installation

Copy or link this skill into your Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R codex-brief-antigravity-review "${CODEX_HOME:-$HOME/.codex}/skills/codex-brief-antigravity-review"
```

## Validation

Run validation after editing the skill:

```bash
python3 /Users/elvis/.codex/skills/.system/skill-creator/scripts/quick_validate.py /path/to/codex-brief-antigravity-review
python3 /path/to/codex-brief-antigravity-review/scripts/validate_templates.py /path/to/codex-brief-antigravity-review
```

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

## Maintenance Notes

- This skill consumes routing and approval decisions from `openspec-superpower-change`.
- Do not use Codex subagents as a substitute for the named external agent when external implementation was requested.
- Do not treat a report as proof; audit the evidence and rerun critical checks where possible.
- Do not advance shared status unless the review result is PASS.

## License

MIT. See [LICENSE](LICENSE).
