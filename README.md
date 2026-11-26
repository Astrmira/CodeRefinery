# CodeRefinery

Deep code refinement skills for AI coding agents. [中文](README.zh-CN.md)

CodeRefinery skills are **campaigns you start on purpose**, not rules that ride along with every coding task. Most structural rot and overhead come from decisions made with local information: the author did not know a helper already existed, or could not see that a value had already been validated upstream. Resident rules ("reuse code", "don't over-validate") cannot supply that missing knowledge; they mostly make agents rigid and slower. A dedicated pass can afford to build the global view, decide from evidence, and restructure, and then it ends.

## Skills

| Skill | Version | What it does |
|---|---|---|
| [`refine-structure`](skills/refine-structure/SKILL.md) | 0.2.1 | Maps capabilities, duplication, ownership, and validated facts across a repository or module; consolidates duplicated knowledge and reinvented wheels; repairs missing or wrong abstractions; removes superseded paths; locks decisions in with types, lint, or architecture rules. |
| [`refine-performance`](skills/refine-performance/SKILL.md) | 0.2.1 | Sets up representative workloads and a baseline; explains where the cost goes with profiles and a per-operation work ledger; removes redundant work such as repeated validation, defensive copies, representation churn, chatty I/O, and invariant work redone per call; keeps only changes that measure better. |

Each skill's description is deliberately narrow: an agent loads it when you ask for a deliberate refinement pass, in a slash command or in plain words, and not during ordinary coding.

The two skills share one idea. Duplication, redundant defense, and much runtime overhead all come from unclear ownership: of knowledge, of validated facts, of work. `refine-structure` fixes the ownership; `refine-performance` measures what that, and other redundant work, costs at runtime. Running structure first often removes overhead before it has to be measured.

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

**Manually:** copy a directory from `skills/` into your agent's skills directory, for example `.claude/skills/` (Claude Code) or `.agents/skills/` (Codex and other agents that read the shared location). Copy the whole directory; each skill reads its `references/` on demand.

## Use

| Agent | Invoke |
|---|---|
| Claude Code | `/refine-structure <scope and goal>` (as a plugin: `/coderefinery:refine-structure`) |
| Codex | `$refine-structure <scope and goal>` |
| Cursor | `/refine-structure <scope and goal>` |
| Others | Ask the agent to use the `refine-structure` skill |

The same forms work for `refine-performance`. You can also just describe the task, for example "the repo is full of duplicated helpers, do a structural cleanup pass", and agents that support automatic skill selection can load the matching skill.

Examples:

```
/refine-structure whole repo; consolidate duplicated validation and the hand-rolled HTTP helpers
/refine-structure src/billing; the pricing rules are scattered across handlers
/refine-performance POST /orders is slow under load; profile is flat
/refine-performance cut startup time of the CLI
```

Run a campaign in its own session. Once a skill is loaded, most agents keep its text in the session context, so start a fresh session for ordinary work afterwards. Campaign state lives in `.refinery/<campaign>/ledger.md`, so a campaign can span several sessions.

## Design

- **Guidance, not procedure.** Each skill states what a good result looks like, what depth means, how to judge, what counts as evidence, and when to stop, then leaves the method to the agent. There are no quotas, scores, fixed agent counts, or line-count thresholds; those tend to replace the goal with a proxy.
- **A high bar, a free hand.** The bar is set on the outcome (findings traced to causes, costs accounted for, conclusions tested against counterexamples), not on following steps. Each skill includes open questions meant to push the thinking further, such as "what is the least work this operation could possibly do?"
- **Few firm rules, each with its reason.** Freedom is matched to fragility. Only moves that fail silently or are hard to undo are firm: deleting checks, changing contracts, weakening tests, compromising benchmark integrity, removing protection. Each says why, so it is applied with understanding rather than literally.
- **Knowledge and ownership as the unit.** Duplication is one piece of knowledge with several owners; redundant defense is a fact nobody clearly establishes; a wrong abstraction is one owner holding knowledge that changes for different reasons.
- **Global view first.** A structure campaign starts with a map of existing capabilities (including dependencies and the standard library), duplication, decision owners, and where facts are established. A performance campaign starts with workloads, a baseline, and an explanation of where the cost goes.
- **Diffuse cost is counted, not guessed.** Overhead spread thin across layers leaves a flat profile. A work ledger counts the work per operation (validations, copies, conversions, queries), and counts are exact evidence that a change removed what it targeted.
- **Measurement decides what stays.** Performance changes are kept only when they beat the measured noise without regressing guard metrics; the rest are reverted and recorded.
- **"No change needed" is a valid result.**
- **Lock-in through tooling, not prose.** Types, lint rules, architecture tests, and deterministic work-count assertions enforce decisions at zero agent-runtime cost.
- **Progressive disclosure.** `SKILL.md` stays short; detailed judgment material lives in `references/` and is read only when needed.

## Compatibility notes

- Skills follow the [Agent Skills specification](https://agentskills.io/specification) with no extension fields, so any compliant agent can load them.
- The description is what lets an agent recognize a request as a refinement campaign. Whether a skill is enabled, whether it is loaded, and which copy wins when the same name is installed twice are decided by the host and its configuration. To make a skill strictly manual, add `disable-model-invocation: true` to its frontmatter (Claude Code, Cursor) or an `agents/openai.yaml` with `policy: { allow_implicit_invocation: false }` (Codex).
- Each skill directory is self-contained, because installers copy skill directories individually. `references/fact-ownership.md` is shared by both skills and duplicated on purpose.

## Development

`python scripts/check_skills.py` (requires PyYAML) parses each skill's frontmatter as YAML and checks it against the specification, fails if an expected skill is missing, resolves every relative link in the skills and the READMEs, and fails if the copies of a shared reference file differ. `--self-test` runs the checks against deliberately broken copies of the repository to confirm they fail. CI runs both on every push, then installs the skills with the skills CLI and confirms that every expected skill was installed, because the CLI skips a skill it cannot parse without failing.

## License

[MIT](LICENSE)
