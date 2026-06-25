# <change-id> Step <NN> Brief

文档类型：Implementation Brief
日志及版本：YYYY-MM-DD v1
执行角色：Antigravity CLI / <step role>
预计耗时：<例如 30m；超过后 Codex 可写 timeout audit>

## 背景

<说明 OpenSpec change、已完成步骤、当前只执行哪个 Superpowers plan task>

## 允许修改范围

只允许修改：
- `<path>`

禁止修改：
- `<path>`
- 任何 git 操作（不要 `git add` / `git commit` / `git reset` / `git clean`）

## 允许副作用

默认不允许文件修改以外的副作用。若本步骤需要命令、网络、数据库、环境变量、缓存、后台服务或其他副作用，必须在此列明：

- `<side effect>`：<目的、边界、回滚方式>

### 备份要求 (若允许修改 skill / 模板，必须创建结构化备份)

- 备份目录：`/Users/elvis/.codex/skills-backups/<backup-dir-name>/`
- 结构规范：备份必须保留相对路径结构（例如 `codex-brief-antigravity-review/SKILL.md` ），禁止使用扁平列表备份，以防回滚歧义。

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

Critical commands（Codex Review 必须重跑或给出阻塞说明）：

```bash
<critical command>
```

Supporting commands（执行者必须运行；Codex Review 至少抽查一项或检查对应行为）：

```bash
<supporting command>
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
- 验证命令与结果，区分 critical / supporting
- Diff Summary：`git diff --stat` 与关键 hunk 摘要
- 是否偏离 Brief
- 剩余风险
