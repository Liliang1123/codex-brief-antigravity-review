# CHANGELOG

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-07-10

### Changed
- Narrow implicit routing to non-state-changing review or an existing valid Handoff.
- Add Brief Preflight Review and canonical execution SHA-256 consensus.
- Upgrade Handoff governance to schema 3 with hashed Report/Review evidence.
- Reject empty critical checks, blank blockers, unsafe evidence paths, and atomic final completion.
- Expand adversarial lifecycle tests and bind runtime evidence to
  role/result/batch/attempt/source fingerprints plus previous-status transitions.
- Add caveman as a presentation-compression mode and explicitly exclude
  governance routing and evidence artifacts from compression.

## [1.0.0] - 2026-06-23

### Added
- Initial release of `codex-brief-antigravity-review` skill.
- Core `SKILL.md` orchestrating the "Brief -> Dispatch -> Report -> Review" flow.
- Configured metadata in `agents/openai.yaml`.
- Reusable templates in `references/`:
  - `brief-template.md` (Step Brief specification)
  - `report-template.md` (Step Report feedback)
  - `review-template.md` (Step Review gatekeep)
  - `agy-dispatch-template.md` (External agent dispatch command syntax)
- Added default `AGENTS.md`, `.gitignore`, `CONTRIBUTING.md`, and `LICENSE`.
