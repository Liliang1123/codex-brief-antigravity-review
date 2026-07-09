# Handoff Contract

The Handoff Contract is the single machine-readable state shared by
`openspec-superpower-change` and `codex-brief-antigravity-review`.

## Canonical Location

Keep exactly one mutable marker block in
`docs/agent-collab/<change-id>/status.md`. Brief, Report, Review, Gate, and chat
output must not embed another mutable block; they reference the canonical path
and record `contract_revision`, batch, attempt, and a fingerprint.

## Marker Block

````markdown
<!-- COOP_HANDOFF_CONTRACT_START -->
```yaml
schema_version: 2
change_id: add-example-change
mode: approved-implementation
approval_status: approved
risk_profile: standard
batch_profile: cohesive
current_batch: 1
planned_batches: 2
attempt: 1
contract_revision: 1
lifecycle_state: ready-for-brief
last_review_result: not-run
blocked_reason: none
blocker_owner: none
resume_condition: none
final_verification: pending
final_review_result: pending
executor: external-agent
governor: codex-brief-antigravity-review
next_owner: codex-brief-antigravity-review
step_critical:
  - focused test command
final_critical:
  - full test matrix
business_acceptance:
  unit: required
  pipeline: optional
  api: required
  real_business: required
stop_conditions:
  - scope expansion
  - contract ambiguity
verification_strategy:
  step: run step_critical per batch; review reruns critical plus an independent check
  final: openspec-superpower-change runs final_critical after final batch Review PASS
readonly_fields:
  - schema_version
  - change_id
  - mode
  - approval_status
  - risk_profile
  - batch_profile
  - planned_batches
  - executor
  - governor
  - final_critical
  - step_critical
  - business_acceptance
  - stop_conditions
  - verification_strategy
  - readonly_fields
```
<!-- COOP_HANDOFF_CONTRACT_END -->
````

## Required Fields And Values

Required fields include all fields in the example. Key values:

- `lifecycle_state`: `ready-for-brief`, `ready-for-execution`,
  `ready-for-review`, `needs-fix`, `blocked`,
  `awaiting-final-verification`, or `complete`.
- `last_review_result`: `not-run`, `pass`, `fail`, or `blocked`.
- `final_verification`: `pending`, `pass`, `fail`, or `blocked`.
- `final_review_result`: `pending`, `pass`, `fail`, or `blocked`.
- `attempt` and `contract_revision`: positive integers.
- `next_owner`: `openspec-superpower-change`,
  `codex-brief-antigravity-review`, `external-agent`, or `user`.

`standard` and `strict` require non-empty `step_critical` and
`final_critical`. Business acceptance must define `unit`, `pipeline`, `api`,
and `real_business` as `required`, `optional`, or `not-applicable`.
Both critical-command fields are string lists for every profile;
`stop_conditions` is a non-empty string list and `verification_strategy` is a
mapping with string `step` and `final` entries.

This is an external execution contract: `executor` is `external-agent`,
`governor` is `codex-brief-antigravity-review`, and mode is
`approved-implementation`, approved `self-evolution`, or `direct-change`.

## Lifecycle And Review Loop

```text
ready-for-brief -> ready-for-execution -> ready-for-review
FAIL -> needs-fix -> increment attempt -> same batch execution/review
BLOCKED -> blocked -> satisfy resume_condition -> same batch fresh review
PASS non-final -> increment batch, reset attempt -> ready-for-brief
PASS final -> awaiting-final-verification -> router final review/verification
router final verification + final Review PASS -> complete
```

Rules:

- Every state change increments `contract_revision` by one.
- `FAIL` and `BLOCKED` never advance `current_batch`.
- `FAIL` increments `attempt`; new attempt-specific artifacts must not
  overwrite earlier Brief/Report/Review evidence.
- `blocked` requires non-`none` `blocked_reason`, `blocker_owner`, and
  `resume_condition`, plus `last_review_result: blocked`; recovered work
  refreshes evidence before Review.
- Final batch `PASS` keeps `current_batch == planned_batches`, sets
  `awaiting-final-verification`, `last_review_result: pass`, and
  `next_owner: openspec-superpower-change`.
- `complete` requires final batch, `last_review_result: pass`,
  `final_verification: pass`, `final_review_result: pass`, and
  `next_owner: user`. `complete` is terminal.
- Any missing, stale, duplicated, contradictory, or unparsable contract is
  `BLOCKED` and returns to the router or user.

## Ownership

The router creates the contract, owns readonly routing fields and final
verification, and may mark `complete`. The brief governor may update batch,
attempt, lifecycle, review result, blocker, revision, and next owner according
to the lifecycle, but cannot re-decide approval or risk. External agents do not
edit canonical status.
