# Cross-CLI Brief Governance Design Closeout

文档类型：Major Self-Evolution Companion Design / Closeout Record
日志及版本：2026-07-11 v4（archived；Final Review PASS；local closeout complete）

## Contract and role

- 上游 OpenSpec change：`align-cross-cli-skill-governance`
- 本 Skill 继续只拥有 standalone wording/read-only Review，或在有效 Handoff
  下治理 Brief/Report/Review attempt；最终完成权仍属于 Codex change router。
- Antigravity CLI 与 Grok CLI 可作为明确绑定的 executor 或 independent
  reviewer，但其结果仅是 Codex 审计所消费的证据。

## Implemented design

- Shared Handoff Contract 升级到 schema 4，并与主仓库保持字节一致。
- Brief、Report、Review、timeout audit 与 dispatch template 绑定
  `agent_identity`/`agent_role`，拒绝身份冒用和 independent self-review。
- Final batch PASS 仍只返回 `awaiting-final-verification`；fresh final evidence、
  Final Review 和 complete transition 由主 Skill 负责。
- 本仓库的 portable files 由主仓库 manifest allowlist 管理，并参与 Codex、
  Antigravity CLI、Grok CLI 三端 parity/discovery gate。

## Validation and pending gates

- Source quick/template validators 与 55 tests PASS。
- Codex、Antigravity CLI、Grok CLI 三端 portable parity、managed block 与本
  Skill installed validators PASS；Grok discovery PASS。
- Antigravity 首次同步暴露 stale `agents/openai.yaml`，目标已先完整回滚；
  manifest metadata target 经 TDD 修正后，第二次同步与验证 PASS。
- 上游 OpenSpec 已 archive；archive 后 strict validation、两仓完整 diff、
  sensitive audit 与 Final Review PASS。
- 用户明确选择本地闭环；未执行 Git staging/commit/push。临时 backup root
  已按明确授权清理并确认原路径不存在。
- Runtime/global 写入、archive、backup 删除以及 Git add/commit/push 继续等待
  用户对应的明确授权。

## Rollback

- 临时结构化备份：`/private/tmp/cross-cli-skill-sync-major-20260711`
- Source 历史最终由 Git 管理；临时备份仅在全部验证、同步与 Review 决策完成后，
  经用户授权清理。
