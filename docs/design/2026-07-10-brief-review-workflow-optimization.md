# Codex Brief / Antigravity Review 工作流优化设计

文档类型：Skill 工作流优化设计
日志及版本：2026-07-10 v1.1（schema 3 证据绑定校正）

## 定位

本 Skill 不再要求所有请求都先具备 Handoff，而是提供两个互斥入口：

1. **Standalone Lightweight**：编写/优化 task prompt、Brief、checklist，或只读 Review diff、Report、evidence；不需要 OpenSpec、Superpowers plan、Handoff 或批次产物。
2. **Handed-off External Execution**：已有 `openspec-superpower-change` 创建的有效 canonical Handoff 时，负责 Brief、dispatch、Report、Review、修正 attempt 和批次推进。

任何“Review 并修复”、文件修改、行为变化、OpenSpec/风险判断和最终完成声明都回到 `openspec-superpower-change`。

## 外部执行闭环

Canonical state 固定为 `docs/agent-collab/<change-id>/status.md`。Brief/Report/Review 只记录 fingerprint，不复制 marker。

```text
transition ready-for-execution -> 写 attempt Brief -> dispatch
-> attempt Report/Abort -> transition ready-for-review
-> Codex Review
-> FAIL: needs-fix，同 batch attempt+1，再实施/验证/Review
-> BLOCKED: 记录 reason/owner/resume_condition，恢复后新 attempt 再 Review
-> PASS 非最终: 下一 batch
-> PASS 最终: awaiting-final-verification，回交 change gate
```

产物路径带 `<NN>-attempt-<AA>`，保留失败、阻塞和超时历史。Report 的 PASS 只是执行者建议，只有 Codex Review PASS 才能推进；最终批次 PASS 不等于任务完成。

## Schema v3 约束

- 执行合同只允许 `approved-implementation`、`direct-change` 或已批准 `self-evolution`。
- `executor=external-agent`，`governor=codex-brief-antigravity-review`。
- `change_id` 必须为 path-safe kebab-case slug。
- 任何 profile 的 critical commands 和 stop conditions 都有明确类型。
- `FAIL`/`BLOCKED` 不得推进 batch；普通 transition 不得跳 attempt/owner。
- `complete` 要求 batch Review、final Review、final verification 全部 PASS，且为终态。
- 四类 evidence reference 使用项目相对路径与 SHA-256；文件内 schema-1
  manifest 绑定 role/result/change/batch/attempt/source revision/SHA-256。
- Preflight 只使用 PASS/BLOCKED，不能替代 batch Review；`complete` 运行态
  校验必须提供 actual previous status。

## 验证

- `scripts/validate_templates.py` 支持无 PyYAML fallback，并严格使用传入 target path。
- 标准库 `unittest` 覆盖 standalone/handed-off 路由、canonical status、attempt 历史、非法 mode/approval、非法 transition、compact 类型、终态和跨仓 schema parity。
- `agents/openai.yaml` 与新的 prompt/diff review 触发范围一致。

## 回滚与待办

- 回滚备份：`/private/tmp/two-codex-skills-self-evolution-20260710-064702/`。
- runtime 同步、四份验证、19 个本仓测试和独立 Review 已通过。
- 已提交并 push：`codex-brief-antigravity-review@c888eb0`。
- 临时备份已在验证和 push 完成后清理，无遗留备份待办。
