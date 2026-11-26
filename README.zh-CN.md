# CodeRefinery

面向 AI 编码 agent 的深度代码精炼 skills。[English](README.md)

CodeRefinery 的 skill 是**主动发起的专项战役**，不是跟着每次编码常驻的规则。大部分结构腐化和多余开销，来自只掌握局部信息时做的决定：写的人不知道已经有现成实现，或者看不到上游已经校验过这个值。常驻规则（"要复用""别过度校验"）补不上这些缺失的信息，反而让 agent 变得刻板、变慢。专项运行能负担得起建立全局视图、按证据判断、完成重构，然后结束。

## Skills

| Skill | 状态 | 作用 |
|---|---|---|
| [`refine-structure`](skills/refine-structure/SKILL.md) | 0.1.0 | 测绘仓库或模块的已有能力、重复知识、职责归属和已校验事实；合并重复知识和重复造的轮子；修正缺失或错误的抽象；删除被取代的旧路径；用类型、lint 或架构规则固化决定。 |
| `refine-performance` | 计划中 | 以实测为准降低运行开销：沿请求路径分散的防御性开销、重复工作、架构层面的低效。 |

每个 skill 的 description 都刻意写得很窄：你明确要做一次专项精炼时（用斜杠命令或直接用自然语言说），agent 才会加载它；日常编码不会触发。

## 安装

**skills CLI 支持的任意 agent**（Claude Code、Codex、Cursor、OpenCode、Gemini CLI、GitHub Copilot 等）：

```bash
npx skills add Astrmira/CodeRefinery
```

**Claude Code 插件方式：**

```
/plugin marketplace add Astrmira/CodeRefinery
/plugin install coderefinery@coderefinery
```

**手动安装：** 把 `skills/refine-structure/` 整个目录复制到 agent 的 skills 目录，例如 `.claude/skills/`（Claude Code）或 `.agents/skills/`（Codex 及读取通用位置的其他 agent）。

## 使用

| Agent | 调用方式 |
|---|---|
| Claude Code | `/refine-structure <范围和目标>`（插件方式：`/coderefinery:refine-structure`） |
| Codex | `$refine-structure <范围和目标>` |
| Cursor | `/refine-structure <范围和目标>` |
| 其他 | 让 agent 使用 `refine-structure` skill |

也可以直接描述任务，比如"这个仓库到处是重复的工具函数，做一次结构整理"，支持自动选择 skill 的 agent 会自己加载它。

建议在单独的会话里跑一次战役。skill 一旦加载，多数 agent 会把正文留在整个会话上下文里，所以结束后另开新会话做日常开发。战役状态保存在 `.refinery/<campaign>/ledger.md`，可以跨多个会话续作。

## 设计要点

- **指导而不是流程。** 每个 skill 写的是：好结果长什么样、怎么判断、什么算证据、何时停止。不设配额、分数、固定 agent 数或行数阈值，这些东西容易让代理指标取代真实目标。
- **以知识和所有权为单位。** 重复 = 一份知识有多个所有者；冗余防御 = 一个事实没有明确的建立者；错误抽象 = 一个所有者承载了因不同原因变化的知识。
- **先建全局视图。** 战役的第一个产出是一张图：已有能力（包括依赖和标准库）、重复簇、决策归属、事实在哪里建立。
- **"不用改"是合法结论。**
- **靠工具固化，不靠提示词。** 类型、lint、架构测试在 agent 运行时零成本。
- **渐进加载。** `SKILL.md` 保持简短，详细判据放在 `references/`，需要时才读。

## 兼容性说明

- 完全遵循 [Agent Skills 规范](https://agentskills.io/specification)，没有扩展字段，任何兼容的 agent 都能加载。
- 是否触发只由 description 决定。如果想让某个 skill 只能手动调用：Claude Code 和 Cursor 在 frontmatter 加 `disable-model-invocation: true`；Codex 加一个 `agents/openai.yaml`，写 `policy: { allow_implicit_invocation: false }`。
- 每个 skill 目录自包含，因为安装器按目录单独复制。多个 skill 共用的参考文件会有意复制多份，必须保持一致。

## 许可证

[MIT](LICENSE)
