# <change-id> Step <NN> Review

文档类型：Review
日志及版本：YYYY-MM-DD v1

## 结论

通过 / 有风险 / 需修改

## Review 范围

- [Brief](file:///absolute/path)
- [Report](file:///absolute/path)
- [Changed file](file:///absolute/path)

## 主要发现

### 阻塞问题

- <issue>

### 已通过项

- <item>

## 验证记录

Critical commands from Brief（必须全部重跑，或写明无法运行的阻塞原因）：

```bash
<critical command>
```

结果：<pass/fail/blocking reason>

Supporting / spot-check commands（至少抽查一项或检查对应行为）：

```bash
<supporting command or behavior check>
```

结果：<pass/fail/not applicable>

## 最终建议

<next action>

## 后续门禁

- Next-step permission: yes/no
- 若结论为 `有风险`，必须同时满足：风险不触及 OpenSpec-required categories；每个风险有后续验证步骤；下一步约束已明确。
- Next-step execution ownership: Codex / external agent / user
- Timeout audit required before redispatch: yes/no
