# CodeRefinery

面向 AI 编码 agent 的深度代码精炼 skills。[English](README.md)

CodeRefinery 的 skill 是**主动发起的专项战役**，不是跟着每次编码常驻的规则。大部分结构腐化和多余开销，来自只掌握局部信息时做的决定：写的人不知道已经有现成实现，或者看不到上游已经校验过这个值。常驻规则（"要复用""别过度校验"）补不上这些缺失的信息，反而让 agent 变得刻板、变慢。专项运行能负担得起建立全局视图、按证据判断、完成重构，然后结束。

## Skills

| Skill | 版本 | 作用 |
|---|---|---|
| [`refine-structure`](skills/refine-structure/SKILL.md) | 0.2.0 | 测绘仓库或模块的已有能力、重复知识、职责归属和已校验事实；合并重复知识和重复造的轮子；修正缺失或错误的抽象；删除被取代的旧路径；用类型、lint 或架构规则固化决定。 |
| [`refine-performance`](skills/refine-performance/SKILL.md) | 0.2.0 | 建立代表性负载和基线；用 profile 和"按操作计数的工作账本"解释开销在哪；去掉重复校验、防御性拷贝、表示之间来回转换、零碎的 I/O、每次调用都重做的不变计算等多余工作；只保留实测更好的改动。 |

每个 skill 的 description 都刻意写得很窄：你明确要做一次专项精炼时（用斜杠命令或直接用自然语言说），agent 才会加载它；日常编码不会触发。

两个 skill 共用一个核心观点：重复、冗余防御和很多运行开销，都源于所有权不清，包括知识、已校验事实和工作本身的所有权。`refine-structure` 理清所有权；`refine-performance` 实测这类多余工作在运行时的代价。先做结构整理，往往能在测量之前就消掉一部分开销。

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

**手动安装：** 把 `skills/` 下的某个目录整个复制到 agent 的 skills 目录，例如 `.claude/skills/`（Claude Code）或 `.agents/skills/`（Codex 及读取通用位置的其他 agent）。

## 使用

| Agent | 调用方式 |
|---|---|
| Claude Code | `/refine-structure <范围和目标>`（插件方式：`/coderefinery:refine-structure`） |
| Codex | `$refine-structure <范围和目标>` |
| Cursor | `/refine-structure <范围和目标>` |
| 其他 | 让 agent 使用 `refine-structure` skill |

`refine-performance` 用法相同。也可以直接描述任务，比如"这个仓库到处是重复的工具函数，做一次结构整理"，支持自动选择 skill 的 agent 会加载对应的 skill。

示例：

```
/refine-structure 整个仓库；合并重复的校验逻辑和手写的 HTTP 工具函数
/refine-structure src/billing；定价规则散落在各个 handler 里
/refine-performance POST /orders 压测下很慢，profile 很平
/refine-performance 缩短 CLI 的启动时间
```

建议在单独的会话里跑一次战役。skill 一旦加载，多数 agent 会把正文留在整个会话上下文里，所以结束后另开新会话做日常开发。战役状态保存在 `.refinery/<campaign>/ledger.md`，可以跨多个会话续作。

## 设计要点

- **指导而不是流程。** 每个 skill 写的是：好结果长什么样、什么算深入、怎么判断、什么算证据、何时停止，方法留给 agent 自己定。不设配额、分数、固定 agent 数或行数阈值，这些东西容易让代理指标取代真实目标。
- **标准定高，方法放开。** 标准落在结果上：发现要追到根因，开销要解释清楚，结论要经得起反例检验，而不是落在"按步骤做完"上。每个 skill 都带一组开放问题，用来把思考往深处推，比如"这个操作理论上最少需要做多少工作？"
- **硬规则少，而且每条都讲原因。** 自由度与脆弱程度匹配：只有静默失败或难以撤销的操作才是硬规则，包括删除检查、改契约、削弱测试、破坏测量公正性、移除保护。每条都写明原因，让 agent 理解着执行，而不是字面执行。
- **以知识和所有权为单位。** 重复 = 一份知识有多个所有者；冗余防御 = 一个事实没有明确的建立者；错误抽象 = 一个所有者承载了因不同原因变化的知识。
- **先建全局视图。** 结构战役先测绘已有能力（包括依赖和标准库）、重复、决策归属和事实在哪里建立；性能战役先确定负载、基线，并解释开销在哪。
- **分散的开销靠计数，不靠猜。** 分摊在各层的开销在 profile 里是平的。工作账本按操作统计校验、拷贝、转换、查询的次数；次数是确定的，能精确证明改动确实去掉了目标工作。
- **保留与否由测量决定。** 性能改动只有在超出实测噪声、且不拖累守护指标时才保留；其余回退并记录。
- **"不用改"是合法结论。**
- **靠工具固化，不靠提示词。** 类型、lint、架构测试、确定性的工作次数断言，在 agent 运行时零成本。
- **渐进加载。** `SKILL.md` 保持简短，详细判据放在 `references/`，需要时才读。

## 兼容性说明

- 完全遵循 [Agent Skills 规范](https://agentskills.io/specification)，没有扩展字段，任何兼容的 agent 都能加载。
- 是否触发只由 description 决定。如果想让某个 skill 只能手动调用：Claude Code 和 Cursor 在 frontmatter 加 `disable-model-invocation: true`；Codex 加一个 `agents/openai.yaml`，写 `policy: { allow_implicit_invocation: false }`。
- 每个 skill 目录自包含，因为安装器按目录单独复制。`references/fact-ownership.md` 由两个 skill 共用，有意复制了两份。

## 开发

`python scripts/check_skills.py` 会按规范检查 frontmatter、解析所有相对链接，并在共享参考文件的副本不一致时报错。CI 在每次 push 时运行它。

## 许可证

[MIT](LICENSE)
