# codex-brief-antigravity-review

[English](README.md) | [简体中文](README_cn.md)

`codex-brief-antigravity-review` 是一个 Codex Skill，用于通过结构化 Brief、执行 Report、独立 Review 和证据门禁来协调外部 Agent 实施。

它适用于这样的工作流：Codex 负责设计、派发和审计，另一个执行 Agent（例如 Antigravity CLI）在明确的文件、命令和报告边界内完成实现。

## 亮点

- 将已批准的实施计划转化为批次级 Brief。
- 将编排与评审从具体实现执行中分离。
- 要求外部 Agent 输出结构化 Report 或 Abort Report。
- 在写出 PASS、FAIL 或 BLOCKED 前审计证据。
- 防止关键证明缺失时产生虚假 PASS。
- 使用共享 Handoff Contract 管理批次状态和推进控制。

## 为什么需要它

长时间实施任务如果由同一个 Agent 负责所有环节，风险很高。常见失败模式包括：

- 上下文过载并遗漏约束；
- 规划者与实施者职责不清；
- 成功声明缺少原始证据；
- 文件修改范围超出批次边界；
- 跳过关键命令复跑；
- 上一个批次尚未证明就推进下一批次。

该 Skill 固化了严格的 Brief -> Dispatch -> Report -> Review 循环。

## 角色边界

| 角色 | 职责 |
|---|---|
| Codex | 读取已批准计划，编写 Brief，派发外部 Agent，审计 Report，在可行时复跑关键证据，并写出 PASS / FAIL / BLOCKED Review。 |
| 外部 Agent | 只实现允许范围，遵守禁止文件与 abort 规则，运行要求的检查，并写出 Report。 |
| Handoff Contract | 保存 mode、approval status、risk profile、current batch、evidence profile 和 promotion rules 等共享状态。 |
| openspec-superpower-change | 在本 Skill 接手前，负责请求路由、OpenSpec 审批状态、风险等级和实施授权。 |

该 Skill 激活时，Codex 不应重新判断 OpenSpec 审批或风险分类。

## 工作流

```text
读取 Handoff Contract
-> 读取当前批次的已批准计划章节
-> 写 <NN>-brief.md
-> 派发外部 Agent
-> 要求 <NN>-report.md 或 <NN>-report-abort.md
-> 根据证据审计 Report 声明
-> 在可行时复跑关键检查
-> 写 step review：PASS / FAIL / BLOCKED
-> 只有 PASS 后才能推进
```

## 产物路径

| 产物 | 路径 |
|---|---|
| Brief | `docs/agent-collab/<change-id>/<NN>-brief.md` |
| Report | `docs/agent-collab/<change-id>/<NN>-report.md` |
| Abort Report | `docs/agent-collab/<change-id>/<NN>-report-abort.md` |
| Status / Handoff Contract | `docs/agent-collab/<change-id>/status.md` |
| Review | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-review.md` |
| Timeout Audit | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-timeout-audit.md` |

## 证据等级

| 等级 | 典型场景 |
|---|---|
| compact | 低风险批次，使用聚焦命令和简洁报告。 |
| standard | 默认实施批次，需要函数映射、数据合同、不变量、错误矩阵、RED/GREEN 证据和业务验收层。 |
| strict | 安全、认证、权限、公开 API/schema、持久化、迁移、部署、回滚或跨租户变更。 |

## 仓库结构

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── brief-template.md
│   ├── report-template.md
│   ├── review-template.md
│   ├── agy-dispatch-template.md
│   ├── timeout-audit-template.md
│   └── handoff-contract.md
└── scripts/
    └── validate_templates.py
```

## 关键参考文件

- `references/brief-template.md`：Brief 必填章节和证据要求。
- `references/report-template.md`：外部 Agent 实施报告格式。
- `references/review-template.md`：PASS / FAIL / BLOCKED Review 合同。
- `references/agy-dispatch-template.md`：派发 prompt 和命令结构。
- `references/timeout-audit-template.md`：超时或 Report 缺失审计格式。
- `references/handoff-contract.md`：Codex 与外部 Agent 的共享状态合同。

## 核心规则

- 每份 Brief 必须列出允许文件、禁止文件、abort 条件、report 路径和关键证据。
- 外部 Agent 不得覆盖由路由器拥有的 Handoff Contract 字段。
- Report 缺失、关键证据缺失、原始 artifact 缺失或依赖不可达，结论为 `BLOCKED`。
- 越界文件修改、破坏性 git 操作或回归仍可复现，结论为 `FAIL`。
- 除非明确声明相关层不适用，否则单元测试不能单独证明 API、服务或真实业务成功。
- 只有 `PASS` 才能推进批次指针或授权下一份 Brief。

## 安装

复制或链接到 Codex skills 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R codex-brief-antigravity-review "${CODEX_HOME:-$HOME/.codex}/skills/codex-brief-antigravity-review"
```

## 验证

修改 Skill 后运行：

```bash
python3 /Users/elvis/.codex/skills/.system/skill-creator/scripts/quick_validate.py /path/to/codex-brief-antigravity-review
python3 /path/to/codex-brief-antigravity-review/scripts/validate_templates.py /path/to/codex-brief-antigravity-review
```

## 示例 Prompt

```text
Use codex-brief-antigravity-review to write the next implementation brief from the approved plan. Do not edit implementation files.
```

```text
Use codex-brief-antigravity-review to audit the latest external-agent report, rerun critical evidence where possible, and write a PASS / FAIL / BLOCKED review.
```

```text
Use codex-brief-antigravity-review to resume shared status and determine whether the next batch may start.
```

## 维护说明

- 本 Skill 消费来自 `openspec-superpower-change` 的路由和审批决策。
- 当用户要求外部 Agent 实施时，不得用 Codex subagent 替代指定外部 Agent。
- 不得把 Report 当成证明；必须审计证据，并在可行时复跑关键检查。
- 除非 Review 结果为 PASS，否则不得推进共享状态。

## License

MIT. See [LICENSE](LICENSE).
