# Antigravity CLI Dispatch Template

```bash
agy --print-timeout 30m --print "$(cat <<'EOF'
项目路径：<project-path>

请按以下 Brief 执行 <change-id> Step <NN>：
docs/agent-collab/<change-id>/<NN>-attempt-<AA>-brief.md

Canonical status（只读，不得修改）：
docs/agent-collab/<change-id>/status.md
Execution revision / canonical SHA-256：<revision> / <64 lowercase hex>
Executor identity：antigravity-cli
Independent reviewer identity：<grok-cli / codex / compact not-applicable>
Decision owner：codex

执行完成后，请生成报告：
docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report.md

如果遇到越界、阻塞或需要 Codex 判断的问题，请停止并生成：
docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report-abort.md

硬性要求：
- 只允许修改 Brief 指定文件
- 禁止修改 Brief 禁止范围
- 禁止 git add / git commit / git reset / git clean
- 必须运行 Brief 中列出的验证命令
- 不得修改 canonical status 或复制 Handoff Contract marker block
- 报告必须记录 schema_version 4 / contract_revision / batch / attempt 指纹和
  与 Brief 相同的 canonical SHA-256
- 报告必须内嵌完整 schema-1 `attempt-report` evidence manifest；role、result、
  change、batch、attempt、execution revision/SHA-256、
  `agent_identity: antigravity-cli`、`agent_role: executor` 缺一不可；禁止别名或冒充
- 报告需包含修改文件、验证命令与结果、Evidence 表、raw/summary 产物路径、是否偏离 Brief、剩余风险
- 如果 Brief 要求 server/API/business-chain 回归，pytest 通过不能替代真实链路验证
- 缺少关键证据时必须写 BLOCKED，不得写 PASS
- FAIL/BLOCKED 后不得推进 batch；修正或恢复必须由 Codex 分配新 attempt
EOF
)"
```
