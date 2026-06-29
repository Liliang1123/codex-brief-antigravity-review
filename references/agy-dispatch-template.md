# Antigravity CLI Dispatch Template

```bash
agy --print-timeout 30m --print "$(cat <<'EOF'
项目路径：<project-path>

请按以下 Brief 执行 <change-id> Step <NN>：
docs/agent-collab/<change-id>/<NN>-brief.md

执行完成后，请生成报告：
docs/agent-collab/<change-id>/<NN>-report.md

如果遇到越界、阻塞或需要 Codex 判断的问题，请停止并生成：
docs/agent-collab/<change-id>/<NN>-report-abort.md

硬性要求：
- 只允许修改 Brief 指定文件
- 禁止修改 Brief 禁止范围
- 禁止 git add / git commit / git reset / git clean
- 必须运行 Brief 中列出的验证命令
- 必须保留 Handoff Contract marker block，禁止改写 readonly fields：mode / approval_status / risk_profile
- 报告需包含修改文件、验证命令与结果、Evidence 表、raw/summary 产物路径、是否偏离 Brief、剩余风险
- 如果 Brief 要求 server/API/business-chain 回归，pytest 通过不能替代真实链路验证
- 缺少关键证据时必须写 BLOCKED，不得写 PASS
EOF
)"
```
