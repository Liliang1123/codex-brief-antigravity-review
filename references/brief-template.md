# <change-id> Step <NN> Brief

文档类型：Implementation Brief
日志及版本：YYYY-MM-DD v1
执行角色：Antigravity CLI / <step role>
预计耗时：<例如 30m；超过后 Codex 可写 timeout audit>

## 1. 项目路径

`<absolute project path>`

## 2. 任务目标

<只描述本步骤要完成的目标，禁止扩展范围。明确本步骤是修复、验证、调查还是只产出报告。>

## 3. 允许修改的文件

只允许修改：
- `<path>`

## 4. 禁止修改的范围

禁止修改：
- `<path>`
- qflow / prompt / 文档工具 / 配置 / 其他未授权范围：<按任务列出>
- 任何 git 操作（不要 `git add` / `git commit` / `git reset` / `git clean`）

## 5. Git / 工作区硬约束

- 执行前必须记录 `git status --short`。
- 禁止 `git add`。
- 禁止 `git commit`。
- 禁止 `git reset`。
- 禁止 `git clean`。
- 禁止丢弃用户已有 staged / unstaged / untracked 改动。
- 若存在 staged 改动且 Brief 未明确授权处理，必须停止并写 `<NN>-report-abort.md`。
- 若 Brief 明确允许处理 staged 状态，只能执行被授权的命令，并必须保留工作区改动和记录前后状态。

## 6. 允许副作用

默认不允许文件修改以外的副作用。若本步骤需要命令、网络、数据库、环境变量、缓存、后台服务、server 启停或外部 API 调用，必须在此列明：

- `<side effect>`：<目的、边界、回滚方式>

### 备份要求（若允许修改 skill / 模板，必须创建结构化备份）

- 备份目录：`/Users/elvis/.codex/skills-backups/<backup-dir-name>/`
- 结构规范：备份必须保留相对路径结构（例如 `codex-brief-antigravity-review/SKILL.md`），禁止使用扁平列表备份，以防回滚歧义。

## 7. 需求来源

- Plan：`docs/superpowers/plans/YYYY-MM-DD-<change-id>.md`
- OpenSpec delta：`openspec/changes/<change-id>/specs/.../spec.md`
- Previous Review：`docs/review/...`
- User issue / bug evidence：`<path or pasted summary>`

## 8. 子问题列表与覆盖边界

| 子问题 | 本步骤是否覆盖 | 验证方式 | 不覆盖时的说明 |
|---|---|---|---|
| <子问题 A> | 是/否 | <command/artifact/assertion> | <reason> |
| <子问题 B> | 是/否 | <command/artifact/assertion> | <reason> |

> 不得把某个子问题的局部修复泛化为整个业务问题已修复。

## 9. 必须执行的验证命令

Critical commands（Codex Review 必须重跑或给出阻塞说明）：

```bash
<critical command>
```

Supporting commands（执行者必须运行；Codex Review 至少抽查一项或检查对应行为）：

```bash
<supporting command>
```

## 10. 业务验收标准

明确区分以下层级，并标明哪些层级是本步骤 `PASS` 的必要条件：

| 验收层级 | 是否必须 | 验证方式 | PASS 条件 |
|---|---:|---|---|
| 单元测试 | 是/否 | `<pytest ...>` | <expected> |
| 管线测试 | 是/否 | `<command>` | <expected> |
| server / API / `/chat` 回归 | 是/否 | `<curl/script/raw SSE>` | <expected> |
| 真实业务问题 | 是/否 | <artifact/assertion> | <expected> |

如果本 Brief 要求 server / API / `/chat` 回归，则 pytest 通过不能替代业务链路通过，单元测试通过也不能替代业务链路通过。

## 11. Key Assertions（关键断言）

| 断言 | 期望 | 证据产物 |
|---|---|---|
| <例如 answer 中 forbidden string 次数> | 0 | `<raw/summary path>` |
| <例如 是否进入文档工具> | 是 | `<raw/summary path>` |
| <例如 server /chat 是否跑完整> | 是 | `<raw/summary path>` |

## 12. 阻塞处理

如果遇到依赖、LLM 502、server 无法启动、外部服务不可用、未进入目标工具、权限不足或验证命令无法完成：

- 不得声称 `PASS`。
- 必须生成 `<NN>-report-abort.md` 或在 report 结论写 `BLOCKED`。
- 必须写清楚阻塞命令、错误、已完成操作、raw 输出路径、下一步需要 Codex / 用户 / 外部服务做什么。

## 13. 质量门禁

```bash
git diff --check -- <allowed files>
```

## 14. 执行报告

执行完成后生成：
- `docs/agent-collab/<change-id>/<NN>-report.md`

报告必须包含：
- 修改文件列表
- `git status --short` 前后状态
- 验证命令与结果，区分 critical / supporting
- Evidence：Commands / Artifacts / Key Assertions
- raw / summary 产物路径
- 子问题覆盖矩阵
- 业务验收结论，区分单元测试、管线测试、server/API、真实业务问题
- Diff Summary：`git diff --stat` 与关键 hunk 摘要
- 是否偏离 Brief
- BLOCKED / FAIL 时的阻塞项或必修项
- 剩余风险
