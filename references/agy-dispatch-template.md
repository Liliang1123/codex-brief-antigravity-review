# Antigravity CLI Dispatch Template

```bash
agy --print-timeout 30m --print "$(cat <<'EOF'
项目路径：<project-path>

请按以下 Brief 执行 <change-id> Step <NN>：
docs/agent-collab/<change-id>/<NN>-brief.md

执行完成后，请生成报告：
docs/agent-collab/<change-id>/<NN>-report.md

硬性要求：
- 只允许修改 Brief 指定文件
- 禁止修改 Brief 禁止范围
- 禁止 git add / git commit / git reset / git clean
- 必须运行 Brief 中列出的验证命令
- 报告需包含修改文件、验证命令与结果、是否偏离 Brief、剩余风险
EOF
)"
```
