# codex-brief-antigravity-review

[English](README.md) | [简体中文](README_cn.md)

`codex-brief-antigravity-review` 是一个用于编写 Antigravity/Codex 任务提示并复核 diff、Report 和证据的 Codex Skill。独立提示词/只读 Review 保持轻量；只有 `openspec-superpower-change` 已完成交接后，才进入结构化外部执行治理。

## 亮点

- 独立编写或优化 task prompt、Brief、checklist，无需 OpenSpec/Handoff。
- 普通 diff/证据只读 Review 不伪造批次推进。
- 将已批准实施计划转化为带 attempt 的批次 Brief。
- 将编排与评审从具体实现执行中分离。
- 要求外部 Agent 输出结构化 Report 或 Abort Report。
- 在写出 PASS、FAIL 或 BLOCKED 前审计证据。
- 防止关键证明缺失时产生虚假 PASS。
- `FAIL`/`BLOCKED` 保留 attempt 历史，修正/解阻后必须再 Review。
- 只以 canonical `status.md` 保存共享状态，最终批次 PASS 回交总入口验证。
- Dispatch 前对当前 revision 的 Brief 执行 Preflight Review。
- schema 5 / schema 2 证据绑定产品、实例、角色、profile、决策来源、Lease
  与 SHA-256；同产品也禁止同实例自审。
- 手工复制的 state-changing standard/strict Brief 仍走 canonical Handoff；
  High Review 必须检查真实 diff、生产 wiring、机制证据和独立探针。

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
| Codex standalone | 编写 prompt/Brief/checklist 或只读 Review diff/证据；不维护 Handoff 或推进批次。 |
| Codex governor | 读取已批准计划，编写 attempt Brief，派发外部 Agent，审计 Report，复跑关键证据并写 Review。 |
| 外部 Agent | 只实现允许范围，遵守禁止文件与 abort 规则，运行要求的检查，并写出 Report。 |
| Handoff Contract | 只在 canonical `status.md` 保存 batch、attempt、lifecycle、阻塞恢复和最终回交状态。 |
| openspec-superpower-change | 在本 Skill 接手前，负责请求路由、OpenSpec 审批状态、风险等级和实施授权。 |

Standalone 路径不得修改实现；handed-off 路径不得重新判断 OpenSpec 审批或风险分类。

## 工作流

```text
Standalone：编写/优化 prompt 或只读 Review diff/Report -> 返回结论

Handed-off：读取 canonical Handoff Contract
-> 读取当前批次/attempt 的已批准计划
-> 写 <NN>-attempt-<AA>-brief.md
-> 绑定 canonical execution SHA-256 并 Preflight Review Brief
-> 派发外部 Agent
-> 要求 attempt Report 或 Abort Report
-> 根据证据审计 Report 声明
-> 在可行时复跑关键检查
-> 写 step review：PASS / FAIL / BLOCKED
-> FAIL/BLOCKED：同批次新 attempt，再次 Review
-> 非最终 PASS：下一批
-> 最终 PASS：回交 openspec-superpower-change 做最终验证
```

## 产物路径

| 产物 | 路径 |
|---|---|
| Brief | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-brief.md` |
| Report | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report.md` |
| Abort Report | `docs/agent-collab/<change-id>/<NN>-attempt-<AA>-report-abort.md` |
| Status / Handoff Contract | `docs/agent-collab/<change-id>/status.md` |
| Review | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-attempt-<AA>-review.md` |
| Timeout Audit | `docs/review/YYYY-MM-DD-<change-id>-step-<NN>-attempt-<AA>-timeout-audit.md` |

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
├── scripts/
│   └── validate_templates.py
└── tests/
    └── test_workflow_rules.py
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
- 每个外部 evidence profile 都必须有非空 step/final critical 命令。
- Report/Review 证据必须是项目相对路径、非空文件、SHA-256 匹配，并内嵌
  schema 1 role/result/change/batch/attempt/source fingerprint manifest。

## 安装

复制或链接到 Codex skills 目录：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R codex-brief-antigravity-review "${CODEX_HOME:-$HOME/.codex}/skills/codex-brief-antigravity-review"
```

## 验证

修改 Skill 后运行：

```bash
"${PYTHON_BIN:-python3}" "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" /path/to/codex-brief-antigravity-review
PYTHONDONTWRITEBYTECODE=1 python3 /path/to/codex-brief-antigravity-review/scripts/validate_templates.py /path/to/codex-brief-antigravity-review
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s /path/to/codex-brief-antigravity-review/tests -v
```

运行时状态还可使用 `--status <status.md>` 和
`--artifact-root <project-root>` 验证引用证据文件。
引入证据的 transition 应增加 `--previous-status <canonical-status>`；
`complete` 强制要求。proposed/previous 快照必须留在项目外，确保项目中仍
只有一个 canonical Handoff marker block。

`quick_validate.py` 需要 PyYAML；请通过 `PYTHON_BIN` 选择可用解释器。项目 validator 和测试会覆盖无 PyYAML fallback。

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

```text
Use codex-brief-antigravity-review standalone mode to improve this Antigravity task prompt. Do not create Handoff artifacts or modify project files.
```

## 维护说明

- 本 Skill 可独立处理 prompt/只读 Review；只有 handed-off 路径消费 `openspec-superpower-change` 的路由和审批决策。
- 当用户要求外部 Agent 实施时，不得用 Codex subagent 替代指定外部 Agent。
- 不得把 Report 当成证明；必须审计证据，并在可行时复跑关键检查。
- 除非 Review 结果为 PASS，否则不得推进共享状态。
- 最终批次 PASS 不等于任务完成，必须回交 `openspec-superpower-change`。

## License

MIT. See [LICENSE](LICENSE).
