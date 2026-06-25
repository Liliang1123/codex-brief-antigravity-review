# <change-id> Step <NN> 执行报告

## 结论

PASS / FAIL / BLOCKED

一句话依据：<不能只写“测试通过”；必须说明达到或未达到哪一层验收。>

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

## BLOCKED / FAIL 项

- <missing evidence / failed regression / external dependency block / scope violation>

## 剩余风险

- <risk 1>
- <risk 2>
