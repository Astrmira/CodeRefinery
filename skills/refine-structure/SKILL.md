---
name: refine-structure
description: Run a deep structural refinement campaign on a repository or module. Maps what already exists, then consolidates duplicated knowledge and reinvented wheels, repairs missing or wrong abstractions, settles who owns each decision and validated fact, and removes superseded paths, with behavior preserved. Use when the user asks for a deliberate structural pass over a codebase or module, such as deduplication, consolidating hand-rolled helpers, fixing abstractions, or an architecture or tech-debt cleanup. Not for routine coding, single bug fixes, or reviewing a small diff.
license: MIT
metadata:
  version: "0.1.0"
---

# Refine Structure

This is a campaign you run once, deliberately. It is not a style to apply while coding.

Most structural rot comes from decisions made with local information. Whoever wrote the third date formatter did not know the other two existed. Whoever added the fifth null check could not see that the value had been parsed and validated two layers up. Rules like "reuse existing code" or "avoid defensive checks" cannot fix this, because what was missing was knowledge, not intent. Your advantage in this campaign is that you can afford to build the global view those authors lacked, and restructure from it.

Think in terms of **knowledge and ownership**, not lines or files:

- Duplication: one piece of knowledge with several owners.
- Redundant defense: one fact with no clear establisher, so every layer re-checks it.
- Wrong abstraction: one owner forced to hold several pieces of knowledge that change for different reasons.
- Misplaced logic: a decision made far from the concept it is about.

## What a finished campaign looks like

- Each piece of business knowledge or capability in scope has one authoritative implementation, where its consumers would look for it. Callers use it. Superseded paths are deleted, not left beside it.
- Hand-rolled code that duplicates an installed dependency, the framework, or the standard library has been replaced wherever the contracts actually match.
- Every remaining abstraction earns its place: it captures shared knowledge, a real boundary, or a variation point that is actually used.
- Each important fact (validated input, invariant, permission) is established once, where it enters, and carried forward by type or contract instead of being re-checked.
- Behavior is preserved. Every intentional behavior change is listed and was approved by the user.
- Decisions that are cheap to enforce are locked in by types, lint rules, or architecture tests.
- A ledger records what was found, what was decided and why, what changed, how it was verified, and what was deliberately left alone.

"No change needed" is a legitimate result for any finding, and for the whole campaign.

## Scope

Take scope and goal from the user's request: a path, module, feature, or the whole repository. If it is ambiguous, infer it from context and ask only about decisions that would change the outcome. Map the full scope before executing anything. Record findings outside the scope; do not silently expand it.

## Campaign rhythm

The phases describe the shape of the work, not a script. Spend effort where the evidence leads.

### 1. Map: build the global view

Coverage means understanding the entry points, the main data flows, which module owns which concept, and what shared code and dependencies exist. It does not mean reading every file. Use cheap, broad means first (search, clone detection, dependency manifests, version history) and read deeply only where candidates appear.

Build these in the ledger:

- **Capability inventory**: in-repo helpers, utilities, and services, plus the relevant capabilities of installed dependencies, the framework, and the standard library at the versions actually in use. This is the knowledge the original authors were missing, and most other findings are checked against it.
- **Duplication clusters**: places that encode the same knowledge, including copies that look different. See [finding duplication](references/finding-duplication.md).
- **Ownership map**: for key concepts and decisions (a pricing rule, a permission check, a retry policy, an ID format), every place that currently decides it.
- **Fact map**: where external data enters, where it is validated, and where it is checked again. See [fact ownership](references/fact-ownership.md).
- **Abstraction suspects**: abstractions that look wrong, and places where one is missing. See [abstraction judgment](references/abstraction-judgment.md).
- **Verification baseline**: how to build and run the fastest relevant tests, the current pass/fail state, and which areas are weakly covered.

If your environment supports subagents or parallel workers, delegate mapping by area. Ask each worker to return findings with file:line evidence in the ledger's finding format, not file contents, so the main context holds conclusions. Size the fan-out to the repository; there is no fixed number.

Copies that have already drifted apart deserve the closest look. Each difference is either intentional and must survive consolidation, or accidental, which often means a latent bug.

### 2. Decide: one verdict per finding

Give each finding exactly one verdict:

| Verdict | Meaning |
|---|---|
| reuse | Migrate callers to an existing implementation, dependency, or standard feature. |
| extract | Create one small capability with a named contract, in the module that owns the knowledge. |
| split | Dismantle a wrong abstraction back into its callers, then look again for the real shared concept. |
| relocate | Move a decision or check to its rightful owner. |
| keep | The duplication or abstraction is justified. Say why. |
| defer | Out of scope, or blocked on information. Say what is missing. |

The central test: **would these change together, for the same reason?** If yes, they are one piece of knowledge and should have one owner. If they only look alike, leave them apart. Similar shape is a lead, never a verdict.

For each verdict, record the evidence (callers, file:line), every behavioral difference between the copies and how it will be handled, the migration cost including tests, the blast radius if the shared code is wrong, and the expected payoff. Rank by payoff against risk. Knowledge that changes often, copies that have drifted, and many callers raise the payoff. Public contracts, weak test coverage, and dynamic usage raise the risk.

**Checkpoint.** Before large edits, present the verdict table and let the user choose and adjust, unless they told you to proceed on your own. Always surface behavior changes for explicit approval, including bugs you find in drifted copies; do not silently pick a winner.

### 3. Execute: reviewable units

- **One concept per change unit.** Establish the authoritative implementation, migrate every in-scope caller, and delete the superseded code in the same unit. Leave no compatibility shims unless an external consumer needs them, and then mark each with its removal condition.
- **Pin behavior first where coverage is weak.** Before migrating, write characterization tests for the observable contract: outputs, error types and messages that callers depend on, side effects, ordering, edge inputs. Tests that mirror implementation details do not count.
- **Prefer mechanical transformation for many call sites**: IDE refactorings, codemods, or structural rewrite tools such as ast-grep, comby, or OpenRewrite. Try the rule on a sample first. A rule-driven change is more consistent and easier to review than hand edits.
- **Verify in proportion.** Build or type-check plus targeted tests after each unit; the full suite at milestones and at the end. Keep builds incremental; do not clean and rebuild everything to check one change.
- **When a test fails**, judge it against the contract, not the new code. Change an expectation only when the old one is shown to be wrong, and log that as a behavior change.
- Update the ledger after each unit.

### 4. Lock in

Prevent regrowth with mechanisms that cost nothing at agent runtime and fail loudly:

- Types that carry established facts (parsed values, value objects, branded or newtype wrappers), so re-checks become unnecessary by construction.
- Lint or analyzer rules that ban the superseded path or import, such as `no-restricted-imports`, ruff `banned-api`, forbiddenapis, depguard, or .NET banned-API analyzers.
- Dependency or architecture rules for the boundaries you established, such as dependency-cruiser, import-linter, or ArchUnit.
- Obvious names and locations, so the authoritative implementation is what a search finds first.

Add rules only for decisions made in this campaign, and prefer tooling the repository already has. Locking in belongs in code and tooling, not in new prose instructions for agents.

### 5. Close

Stop when every in-scope finding has a verdict and each approved verdict is done or explicitly deferred, when the remaining payoff no longer justifies the risk, or when the user's goal is met. Then report:

- What changed in the shape of the codebase: the authoritative implementations and owners now in place.
- Each change unit: the problem, the new home, what was removed, the behavior preserved, and how it was verified.
- Behavior changes, with their approval.
- Lock-ins added.
- Findings kept, deferred, or out of scope, with reasons.
- Net size change, implementation and tests reported separately.
- Remaining risks and the limits of the evidence, such as unsearchable dynamic usage or weakly tested areas.

## Hard boundaries

- Do not change public APIs, wire or file formats, persisted schemas, or configuration contracts without explicit approval.
- Do not delete a check unless you can name where its fact is established and why nothing between there and here breaks it.
- An empty search is not proof that exported, reflective, dynamically dispatched, configuration-driven, or externally consumed code is unused. Record the limits of each search.
- Do not weaken or delete tests to get a pass.
- Do not create catch-all modules (`utils`, `common`, `helpers`) as a home for extractions. Code lives with the knowledge it encodes.
- Preserve unrelated work in the tree. No destructive version-control operations.

## Ledger

Keep the campaign state in `.refinery/<campaign>/ledger.md`, or wherever the user prefers. It outlives context limits and sessions: on resume, read it first, check it against the current code, and continue from the open items. Ask whether the user wants it committed or ignored.

## References

Read these when the work calls for them, not up front:

- [references/finding-duplication.md](references/finding-duplication.md): while mapping duplication and reinvented wheels.
- [references/abstraction-judgment.md](references/abstraction-judgment.md): while deciding verdicts on abstractions.
- [references/fact-ownership.md](references/fact-ownership.md): whenever a finding involves validation, guards, error handling, fallbacks, or defensive copies.
- [references/ledger-format.md](references/ledger-format.md): when creating or resuming the ledger.
