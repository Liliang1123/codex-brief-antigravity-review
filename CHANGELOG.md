# CHANGELOG

All notable changes to this project will be documented in this file.

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
