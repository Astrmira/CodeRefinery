# CodeRefinery

Deep code refinement skills for AI coding agents.

CodeRefinery skills are **campaigns you start on purpose**, not rules that ride along with every coding task. Most structural rot and overhead come from decisions made with local information: the author did not know a helper already existed, or could not see that a value had already been validated upstream. Resident rules ("reuse code", "don't over-validate") cannot supply that missing knowledge; they mostly make agents rigid and slower. A dedicated pass can afford to build the global view, decide from evidence, and restructure, and then it ends.

## Skills

| Skill | Status | What it does |
|---|---|---|
| [`refine-structure`](skills/refine-structure/SKILL.md) | 0.1.0 | Maps capabilities, duplication, ownership, and validated facts across a repository or module; consolidates duplicated knowledge and reinvented wheels; repairs missing or wrong abstractions; removes superseded paths; locks decisions in with types, lint, or architecture rules. |
| `refine-performance` | planned | Measured reduction of runtime overhead: diffuse defensive costs along request paths, redundant work, and architecture-level inefficiency. |

Each skill's description is deliberately narrow: an agent loads it when you ask for a deliberate refinement pass, in a slash command or in plain words, and not during ordinary coding.

## Install

**Any agent supported by the [skills CLI](https://github.com/vercel-labs/skills)** (Claude Code, Codex, Cursor, OpenCode, Gemini CLI, GitHub Copilot, and many more):

```bash
npx skills add Astrmira/CodeRefinery
```

**Claude Code as a plugin:**

```
/plugin marketplace add Astrmira/CodeRefinery
/plugin install coderefinery@coderefinery
```

**Manually:** copy `skills/refine-structure/` into your agent's skills directory, for example `.claude/skills/` (Claude Code) or `.agents/skills/` (Codex and other agents that read the shared location). Copy the whole directory; the skill reads its `references/` on demand.

## Use

| Agent | Invoke |
|---|---|
| Claude Code | `/refine-structure <scope and goal>` (as a plugin: `/coderefinery:refine-structure`) |
| Codex | `$refine-structure <scope and goal>` |
| Cursor | `/refine-structure <scope and goal>` |
| Others | Ask the agent to use the `refine-structure` skill |

You can also just describe the task, for example "the repo is full of duplicated helpers, do a structural cleanup pass", and agents that support automatic skill selection will load it.

Examples:

```
/refine-structure whole repo; consolidate duplicated validation and the hand-rolled HTTP helpers
/refine-structure src/billing; the pricing rules are scattered across handlers
```

Run a campaign in its own session. Once a skill is loaded, most agents keep its text in the session context, so start a fresh session for ordinary work afterwards. Campaign state lives in `.refinery/<campaign>/ledger.md`, so a campaign can span several sessions.

## Design

- **Guidance, not procedure.** Each skill states what a good result looks like, how to judge, what counts as evidence, and when to stop. There are no quotas, scores, fixed agent counts, or line-count thresholds; those tend to replace the goal with a proxy.
- **Knowledge and ownership as the unit.** Duplication is one piece of knowledge with several owners; redundant defense is a fact nobody clearly establishes; a wrong abstraction is one owner holding knowledge that changes for different reasons.
- **Global view first.** The first output of a campaign is a map: existing capabilities (including dependencies and the standard library), duplication clusters, decision owners, and where facts are established.
- **"No change needed" is a valid result.**
- **Lock-in through tooling, not prose.** Types, lint rules, and architecture tests enforce decisions at zero agent-runtime cost.
- **Progressive disclosure.** `SKILL.md` stays short; detailed judgment material lives in `references/` and is read only when needed.

## Compatibility notes

- Skills follow the [Agent Skills specification](https://agentskills.io/specification) with no extension fields, so any compliant agent can load them.
- Triggering is controlled by the description alone. If you want a skill to be strictly manual, add `disable-model-invocation: true` to its frontmatter (Claude Code, Cursor) or an `agents/openai.yaml` with `policy: { allow_implicit_invocation: false }` (Codex).
- Each skill directory is self-contained, because installers copy skill directories individually. Reference files shared between skills are duplicated on purpose and must be kept identical.

## License

[MIT](LICENSE)
