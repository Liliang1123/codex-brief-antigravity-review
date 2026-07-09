# <change-id> Step <NN> Attempt <AA> Timeout Audit

文档类型：Timeout Audit
日志及版本：YYYY-MM-DD v1

## 结论

需修改

> timeout audit 的结论固定为 `需修改`，因为外部 Agent 未在约定时间内交付 Report 或 Abort Report，Codex 必须在审计后决定下一步行动。

## Review 范围

- Brief：`docs/agent-collab/<change-id>/<NN>-attempt-<AA>-brief.md`
- 预期但未收到的 Report：`docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report.md`
- 预期但未收到的 Abort Report：`docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report-abort.md`

## 超时情况

- 预计耗时：<Brief 中约定的时间限制>
- 实际等待时间：<从 dispatch 到 audit 的实际时长>
- 超时判定依据：<说明如何确认外部 Agent 未按时交付>

## Worktree 检查

- 工作树状态：`git status` 输出摘要
- 是否有部分改动：<是/否，说明发现的未完成改动>
- 改动是否在 Brief allow-list 范围内：<是/否>

## 验证记录

已运行的验证命令（如有）：

```bash
<command>
```

结果：<pass/fail/not applicable>

## 后续门禁

- Redispatch permission: yes/no
- 若 yes：<说明 redispatch 条件，例如是否需要修改 Brief、是否需要清理部分改动>
- 若 no：<说明阻塞原因和需要用户或 Codex 做的决策>
- Timeout audit required before redispatch: yes
- Handoff Contract status: present / missing / duplicated / unparsable
- Lifecycle: `blocked`; current batch unchanged; record `blocked_reason`, `blocker_owner`, and `resume_condition`
- Recovery must use a new attempt and fresh Review; do not overwrite the timeout attempt
- Next owner: Codex / external agent / user
