# <change-id> Step <NN> Brief

文档类型：Implementation Brief
日志及版本：YYYY-MM-DD v1
执行角色：Antigravity CLI / <step role>

## 背景

<说明 OpenSpec change、已完成步骤、当前只执行哪个 Superpowers plan task>

## 允许修改范围

只允许修改：
- `<path>`

禁止修改：
- `<path>`
- 任何 git 操作（不要 `git add` / `git commit` / `git reset` / `git clean`）

## 需求来源

- Plan：`docs/superpowers/plans/YYYY-MM-DD-<change-id>.md`
- OpenSpec delta：`openspec/changes/<change-id>/specs/.../spec.md`
- Previous Review：`docs/review/...`

## 目标

<本步骤目标>

## 必须完成

1. <明确任务 1>
2. <明确任务 2>

## 必跑验证

```bash
<command>
```

## 质量门禁

```bash
git diff --check -- <allowed files>
```

## 执行报告

执行完成后生成：
- `docs/agent-collab/<change-id>/<NN>-report.md`

报告需包含：
- 修改文件列表
- 验证命令与结果
- 是否偏离 Brief
- 剩余风险
