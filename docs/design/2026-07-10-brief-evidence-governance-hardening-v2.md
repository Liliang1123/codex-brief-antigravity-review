# Codex Brief / Antigravity Review 证据治理强化设计（v2）

文档类型：Skill 工作流 Review 与实施闭环
日志及版本：2026-07-10 v2.0

## 定位

本 Skill 有且只有两个入口：

1. **Standalone Lightweight**：非状态改变的 prompt/Brief 文案，或不要求
   修复、也不裁决 whole-task completion 的只读 diff/Report/evidence Review。
2. **Handed-off External Execution**：消费 `openspec-superpower-change`
   已创建的有效 schema-3 Handoff，治理 Brief、dispatch、Report、Review、
   correction attempt 与 batch promotion。

文件修改、Review-and-fix、workflow/template 变化、OpenSpec/risk 决策和最终
完成声明必须返回 change gate；本 Skill 不与总入口抢路由。

## 外部批次闭环

```text
读取 canonical status
-> 生成当前 attempt Brief
-> Preflight PASS/BLOCKED
-> dispatch -> Report/Abort
-> proposed ready-for-review transition + previous-status validation
-> batch Review
-> FAIL/BLOCKED: 同 batch 新 attempt，重新验证与 Review
-> PASS: 下一 batch；最终 batch 回交 router
```

- Preflight 只使用 PASS/BLOCKED，任何 finding 都是 BLOCKED；它不替代
  batch Review，也不能成为 batch PASS evidence。
- Report 的 PASS 只是执行者建议；只有 Codex `batch-review: pass` 才可推进。
- 任何 actionable finding 必须修正、重新验证并再次 Review；仅明确接受且有
  owner/决策的观察项可记录为 residual risk。

## Evidence Manifest

Report、batch/preflight/final Review、timeout audit 和 final verification
使用项目相对 path + SHA-256，并在文件中内嵌 schema-1 manifest：

- `evidence_role` / `evidence_result`；
- `change_id` / `current_batch` / `attempt`；
- 来源 `contract_revision` / `canonical_sha256`。

Validator 同时校验存在性、非空、路径逃逸、symlink、hash、role/state、
result/status、batch/attempt freshness 和 source transition。仅同一份
`timeout-audit: blocked` 可同时作为 Report 与 blocking Review；其他角色不能
复用。`complete` 必须由 router 结合 actual previous status 验证。

## 与 change gate / Superpowers / AGENTS.md 协同

- change gate 决定 Direct/OpenSpec、risk profile、batch profile 与 final gates。
- 本 Skill 不重做 OpenSpec/Superpowers 设计审批，只执行已交接的批次合同。
- public/API restoration 即使是 Direct Change，仍保持 strict，不因 external
  execution 自动降级 compact。
- 项目 `AGENTS.md` 定义本仓验证与 Git 权限边界；Brief/Plan 本身不授权 Git。
- standalone path 不要求 OpenSpec、plan、Handoff 或 schema manifest。

## 验证与回滚

- Source unittest：`48/48 PASS`。
- Source/runtime `validate_templates.py` 与 `quick_validate.py`：PASS。
- 与 router 共用的 Handoff 文档和 validator core：byte-identical。
- 对抗测试覆盖无 Review promotion、被审 Report 替换、Preflight/timeout
  冒充 PASS、旧 batch/attempt、原子 final gate、blocked recovery 与单快照
complete。

该校验以当前 canonical prior state 和已保存的逐跳 PASS 输出为信任锚；
`--previous-status` 只证明当前一跳，不提供恶意本地 actor 场景下的完整历史
签名或 append-only journal。
- 临时结构化备份在发布成功前保留，随后按 router closeout 规则清理。

## 待办

- 无未决设计或实现项。最终 publication 与备份清理结果记录在本次用户
  closeout 报告中。
