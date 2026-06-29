# Handoff Contract

The Handoff Contract is the only machine-readable state shared with
`openspec-superpower-change`.

## Marker Block

Use exactly one block in `docs/agent-collab/<change-id>/status.md`, the Brief,
or the active gate artifact:

````markdown
<!-- COOP_HANDOFF_CONTRACT_START -->
```yaml
schema_version: 1
change_id: add-example-change
mode: approved-implementation
approval_status: approved
risk_profile: standard
batch_profile: cohesive
current_batch: 1
planned_batches: 2
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
  step: run step_critical for each batch; review reruns critical plus one independent check
  final: run final_critical once on the final batch
readonly_fields:
  - mode
  - approval_status
  - risk_profile
```
<!-- COOP_HANDOFF_CONTRACT_END -->
````

## Governor Rules

- If the contract is missing, duplicated, stale, contradictory, or unparsable,
  write `BLOCKED` and return to `openspec-superpower-change` or the user.
- Do not invent or overwrite `mode`, `approval_status`, or `risk_profile`.
- Advance `current_batch` and `next_owner` only after a `PASS` review.
- Keep `step_critical` and `final_critical` separate; do not rerun
  `final_critical` per standard batch unless the contract requires it.
- `business_acceptance.unit`, `pipeline`, `api`, and `real_business` are
  separate layers. Unit tests do not imply API/server/business-chain success.
