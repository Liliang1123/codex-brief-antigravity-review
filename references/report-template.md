# <change-id> Step <NN> Attempt <AA> 执行报告

文档类型：Execution Report
日志及版本：YYYY-MM-DD v1

<!-- COOP_EVIDENCE_MANIFEST_START -->
```yaml
evidence_schema_version: 1
evidence_role: attempt-report
evidence_result: pass
change_id: <change-id>
current_batch: <NN>
attempt: <AA>
contract_revision: <execution revision from Brief>
canonical_sha256: <execution canonical SHA-256 from Brief>
```
<!-- COOP_EVIDENCE_MANIFEST_END -->

将 `evidence_result` 改为本 Report 的实际 `pass`、`fail` 或
`blocked`。四个坐标字段必须回显 Brief 的同一 execution fingerprint；
保存并计算 SHA-256 后不得再改写 manifest 或正文。

## 结论

PASS / FAIL / BLOCKED

一句话依据：<不能只写“测试通过”；必须说明达到或未达到哪一层验收。>

> Report 的 `PASS` 只是执行者建议，不能推进批次或声明任务完成；必须经过 Codex Review。

## 修改文件列表

- [file](file:///absolute/path)

## Git / 工作区状态

执行前：

```bash
git status --short
```

结果：

```text
<before status>
```

执行后：

```bash
git status --short
```

结果：

```text
<after status>
```

Staged 改动：无 / 有，说明：<details>
Untracked 文件：无 / 有，说明：<details>
范围外改动：无 / 有，说明：<details>

## Diff Summary

```bash
git diff --stat
```

关键变更：
- `<path>:Lx-Ly` — <变更内容与目的>

## Evidence

### Handoff Contract Fingerprint

| 字段 | 值 |
|---|---|
| Contract marker count | <start/end count> |
| Canonical status path | `docs/agent-collab/<change-id>/status.md` |
| `schema_version` / `contract_revision` | `3` / `<n>` |
| canonical SHA-256 | `<same value as Brief>` |
| `change_id` | `<value>` |
| `risk_profile` | compact / standard / strict |
| `batch_profile` | single / cohesive / staged |
| `current_batch` / `planned_batches` | `<n>/<n>` |
| `attempt` / `lifecycle_state` | `<AA>` / `<state>` |
| readonly fields changed | no / yes |

如果 execution revision 或 canonical SHA-256 与 Brief 不一致，本 Report 只能
建议 `BLOCKED`。Codex 在状态转换前必须重新计算并核对。

### Commands

| 命令 | 级别 | 退出码 | 结果摘要 | 原始输出/日志路径 |
|---|---|---:|---|---|
| `<command>` | critical/supporting | 0/非0 | <summary> | `<path>` |

### Artifacts

| 产物 | 路径 | 用途 |
|---|---|---|
| raw SSE | `<path>` | 检查真实流式输出 |
| summary JSON | `<path>` | 检查字段计数 / 工具进入情况 |
| server log | `<path>` | 检查 server / API 错误 |

Report 保存后由 Codex 记录：

- `attempt_report_artifact.path`: `<project-relative report/abort path>`
- `attempt_report_artifact.sha256`: `<64 lowercase hex>`

### Key Assertions

| 断言 | 期望 | 实际 | 结论 | 证据路径 |
|---|---|---|---|---|
| <assertion> | <expected> | <actual> | PASS/FAIL/BLOCKED | `<path>` |

## 验证命令与结果

### Critical commands

```bash
<critical command>
```

结果：PASS / FAIL / BLOCKED

```text
<output summary>
```

### Supporting commands

```bash
<supporting command>
```

结果：PASS / FAIL / BLOCKED / not applicable

```text
<output summary>
```

## 业务验收分层

| 验收层级 | 是否执行 | 结果 | 证据 | 说明 |
|---|---:|---|---|---|
| 单元测试 | 是/否 | PASS/FAIL/BLOCKED | `<path>` | <details> |
| 管线测试 | 是/否 | PASS/FAIL/BLOCKED | `<path>` | <details> |
| server / API / `/chat` 回归 | 是/否 | PASS/FAIL/BLOCKED | `<path>` | <details> |
| 真实业务问题 | 是/否 | PASS/FAIL/BLOCKED | `<path>` | <details> |

> 如果 Brief 要求 server/API/真实业务回归但本报告未完成，则本报告结论必须是 `BLOCKED`，不得写 `PASS`。
> 如果真实业务回归已执行且仍复现原问题，则本报告结论必须是 `FAIL`。
> 如果外部依赖不可用导致无法判断业务修复，则本报告结论必须是 `BLOCKED`。

## 子问题覆盖矩阵

| 子问题 | 本步骤是否覆盖 | 验证方式 | 结果 | 不能泛化的边界 |
|---|---:|---|---|---|
| <子问题 A> | 是/否 | <command/artifact/assertion> | PASS/FAIL/BLOCKED | <boundary> |

## 副作用与边界

- 文件外副作用：无 / 有，说明：<command/network/db/env/cache/service/server>
- Allow-list 状态：未越界 / 有越界，说明：<details>
- 禁止范围触碰：无 / 有，说明：<details>

## 是否偏离 Brief

无偏离 / 有偏离：<说明偏离原因及影响>

## 建议状态

- Suggested Review result: PASS / FAIL / BLOCKED
- Suggested next state: ready-for-review / blocked
- `blocked_reason`: none / <reason>
- `blocker_owner`: none / <owner>
- `resume_condition`: none / <condition>

外部 Agent 不得直接编辑 canonical `status.md`。

## BLOCKED / FAIL 项

- <missing evidence / failed regression / external dependency block / scope violation>

## 剩余风险

- <risk 1>
- <risk 2>
