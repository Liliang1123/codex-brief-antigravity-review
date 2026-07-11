# 分层 Agent Brief/Report/Review 治理实施记录

- 文档类型：Major Self-Evolution Implementation Record
- 日志及版本：2026-07-11 v1（source implementation；runtime/archive pending authorization）

## 实施范围

本仓库继续只负责 standalone prompt/read-only Review 与已交接批次的
Brief -> Dispatch -> Report -> Review。新增 schema-5 assignment、schema-2
evidence、Confirmation Lease/provenance 字段、手工复制 Brief 治理和 High
Review 模板；不新增总控 Skill，也不赋予 executor promotion/completion 权限。

## 关键合同

- state-changing standard/strict Brief 即使通过 copy/paste 传递，仍绑定
  canonical status、instance/profile、allow-list、stop conditions 与 Report path。
- Report 只陈述事实、diff、命令、wiring 和 blocker；executor PASS 非权威。
- Review 必须检查 actual files/complete diff、copy/transform/production wiring、
  critical reruns、claim-to-mechanism 和独立 probe。
- same-product executor/reviewer 必须使用不同 `agent_instance_id`。
- 平台权限不替代 workflow scope 或 business/production approval；
  `confirmation_lease_status` 进入 `deferred/revoked` 后不可重激活。

## 验证结果

- validator PASS。
- unittest：`69` tests PASS。
- 共享 Handoff 合同 byte-identical；共享 validator core 保持一致。
- runtime/global sync 已在 Codex、Antigravity CLI、Grok CLI 全部 PASS；
managed block version 2 的块外原生字节保持不变，Grok discovery PASS。
OpenSpec 已归档为
`2026-07-11-add-tiered-agent-collaboration-governance`，归档后 strict validation
PASS。临时 backup 已经用户明确授权并清理；Git publication 仍受单独授权门禁。
