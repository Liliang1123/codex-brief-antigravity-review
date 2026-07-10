# 两 Skill 的 Caveman 融合设计 v1（Brief 视角）

文档类型：架构与工作流统一
日志及版本：2026-07-10 v1.0

## 结论

`caveman` 与 `codex-brief-antigravity-review`、`openspec-superpower-change` 的关系是：

- `caveman` = 人类可读输出压缩。
- `codex-brief-antigravity-review` = prompt/brief 与只读 Review 的业务入口；在 Handoff 批次中承担外部治理。
- `openspec-superpower-change` = OpenSpec/Superpowers 路由与最终完成 gate。

## 结合方式

1. 普通 standalone brief/review 场景：
   - skill 仍然是 `codex-brief-antigravity-review`。
   - 用户要求节省 token 时，输出可用 caveman 风格。
   - 证据路径、命令、文件边界不可被压缩省略。

2. 状态改变/执行修复场景：
   - 返回 `openspec-superpower-change`（brief skill 只在 route table 下发说明）。
   - 即使在最终汇总，仍保持 final 验证与 `PASS` 条件完整。

3. 外部批次场景（有 Handoff）：
   - review/brief 交互可压缩叙述，但 batch 结果和 status 路由必须严格按模板。
   - 所有 `FAIL`/`BLOCKED` 修正并再次 Review 的循环不受影响。

## 风险与禁区

- 禁止把 caveman 当作第三治理层（避免重复审批）。
- 禁止压缩结构化字段：review result、state transition、hash、artifact role/result。
- 禁止省略 `attempt`/`batch`/`review` 关键上下文。

## 与现有闭环兼容性

- 现有两 skill 的 evidence/proof-loop 不变：
  `Preflight -> 实施 -> 验证 -> Review -> 修正 -> 复核 -> final verification -> final review`。
- 本次变更仅补充角色边界和说明，不改变状态机。
