---
name: refine-structure
description: Run a deep structural refinement campaign on a repository or module. Maps what already exists, then consolidates duplicated knowledge and reinvented wheels, repairs missing or wrong abstractions, settles who owns each decision and validated fact, and removes superseded paths, with behavior preserved. Use when the user asks for a deliberate structural pass over a codebase or module, such as deduplication, consolidating hand-rolled helpers, fixing abstractions, or an architecture or tech-debt cleanup. Not for routine coding, single bug fixes, or reviewing a small diff.
license: MIT
metadata:
  version: "0.2.1"
---

# Refine Structure

This is a campaign you run once, deliberately. It is not a style to apply while coding.

What follows describes what matters and why. It is guidance for your judgment, not a procedure: order the work the way this codebase demands, go back when you learn something, and skip what does not apply. The few things that are firm are marked as such and explain themselves.

## The idea

Most structural rot comes from decisions made with local information. Whoever wrote the third date formatter did not know the other two existed. Whoever added the fifth null check could not see that the value had been parsed and validated two layers up. Rules like "reuse existing code" cannot fix this, because what was missing was knowledge, not intent. Your advantage is that you can afford to build the global view those authors lacked, and restructure from it.

Think in terms of **knowledge and ownership**, not lines or files:

- Duplication is one piece of knowledge with several owners.
- Redundant defense is a fact with no clear establisher, so every layer re-checks it.
- A wrong abstraction is one owner holding several pieces of knowledge that change for different reasons.
- Misplaced logic is a decision made far from the concept it is about.

## What done and deep mean

When the campaign is done:

- Each piece of business knowledge or capability in scope has one authoritative implementation, where its consumers would look for it. Callers use it, and the superseded paths are gone rather than left beside it.
- Hand-rolled code that duplicates an installed dependency, the framework, or the standard library has been replaced wherever the contracts actually match.
- Every remaining abstraction earns its place: it captures shared knowledge, a real boundary, or a variation point that is actually used.
- Important facts (validated input, invariants, permissions) are established once, where they enter, and carried forward by type or contract instead of being re-checked.
- Behavior is preserved, and every intentional change in behavior was approved by the user.
- Decisions that are cheap to enforce are enforced by tooling.
- There is a record of what you found, what you concluded and why, what changed, and what you deliberately left alone.

Depth is what separates a campaign from a cleanup:

- You can explain, for each area in scope, why the code has the shape it has and what shape it should have.
- Findings are traced to causes. Ten duplicated helpers often mean one missing concept; naming that concept is the finding.
- You looked past what tools report: duplicates that look different, decisions scattered across handlers, library features rebuilt by hand, copies that quietly diverged.
- Each conclusion survived the strongest counterexample you could find.
- What you did not examine is stated, not hidden.

A pass that only harvested what a clone detector reported, or stopped at the easy duplicates, is not finished. "No change needed" is still a legitimate conclusion, for a finding or the whole campaign, when it is earned by looking.

## Scope

Take scope and goal from the user's request: a path, a module, a feature, or the whole repository. If it is ambiguous, infer it from context and ask only about decisions that would change the outcome. Understand the whole scope before changing anything in it. Note findings outside the scope instead of quietly pursuing them.

## How the work tends to go

A campaign moves through understanding, deciding, changing, and making the change stick. In practice these overlap: deciding sends you back to look again, and one change reveals the next. Treat the sections below as concerns to keep in view, not steps to complete.

### Understand before changing

The goal is the global view the original authors lacked. That means knowing what capabilities already exist (in the repository, and in the dependencies, framework, and standard library at the versions actually in use), where the same knowledge lives in more than one place, who decides each important rule today, where outside data enters and where it is checked again, which abstractions look strained or missing, and how changes can be verified: the fastest relevant tests, and where coverage is weak.

Breadth here means entry points, data flows, and ownership, not reading every file. Cheap, broad means come first (search, clone detection, dependency manifests, version history), and depth goes where candidates appear. [Finding duplication](references/finding-duplication.md) has techniques for both.

The usual ways this goes wrong: stopping at what tools report, treating similar names as the same knowledge, and missing the history that explains why two copies differ. Copies that have already drifted apart deserve the closest look, because each difference is either intentional and must survive, or accidental and often a latent bug.

If your environment supports subagents or parallel workers, delegate by area, and ask each for conclusions with file:line evidence rather than file contents, so your own context holds the picture instead of the raw material.

### Decide what each finding really is

Deciding is where the real work is. For each finding, the question is: if someone who understood all of this code designed it today, would these pieces be one thing or several? The most useful test is whether they would change together, for the same reason. Similar shape is a lead, not an answer.

Conclusions usually take one of a few shapes: reuse what already exists, extract one small capability, split a wrong abstraction back apart, move a decision to its rightful owner, or leave things as they are. Name the conclusion that actually fits rather than forcing a label. [Abstraction judgment](references/abstraction-judgment.md) covers the signals and trade-offs, and [fact ownership](references/fact-ownership.md) covers validation, guards, and error handling.

Before settling, look for what would prove you wrong: the one caller with a different contract, the history that explains the split, the copy that diverged on purpose. Then write down enough for someone else to judge: the evidence, the differences that matter and how each will be handled, and what the change would cost and risk. Value rises with how often the knowledge changes, how far copies have already drifted, and how many callers benefit. Risk rises with public contracts, weak tests, and dynamic usage.

Before large edits, show the user what you found and what you propose, and let them choose, unless they asked you to proceed on your own. They often know which differences are intentional and which areas are about to change; their input is cheap, and the mistakes it prevents are not. Any change in behavior, including fixing a bug you found in a drifted copy, needs their explicit approval.

### Change in units someone can review

Make each change about one concept: establish the authoritative implementation, migrate the callers in scope, and delete the superseded code in the same unit. A half-migrated state is worse than either end, and a focused unit is easy to review and to revert. Leave a compatibility shim only when an external consumer needs one, and note when it can go.

Where coverage is weak, pin the current behavior before moving it: outputs, the errors callers depend on, side effects, ordering, edge inputs. Passing tests prove nothing about behavior they never exercised.

Two cheap checks make that evidence much stronger. First, see whether the tests can fail: make the mistake you are most likely to make, such as merging an edge case the wrong way or dropping an error path, and watch whether anything goes red. If nothing does, the suite is not yet evidence for this change. Second, where the old and new code can run side by side, compare them on many inputs, including the error cases and the types of error raised. A differential check asks the questions nobody thought to write as tests.

When many call sites need the same edit, a mechanical transformation (an IDE refactoring, a codemod, a structural rewrite with a tool such as ast-grep or comby) is more consistent and easier to review than a hundred hand edits.

Verify in proportion: a build or type check and the targeted tests for each unit, the full suite at milestones. When a test fails, judge it against the contract, not against your new code.

### Make it stick

Prose instructions decay; tooling does not. Where it is cheap, lock decisions in with types that carry established facts (parsed values, value objects, branded or newtype wrappers), lint rules that ban the superseded path or import, dependency rules for the boundaries you drew, and names and locations that make the authoritative implementation the first thing a search finds. Add rules only for decisions made in this campaign, and prefer tooling the repository already has.

### Close

The campaign is over when every finding in scope has a considered conclusion and the approved work is done or deliberately deferred, when the remaining value no longer justifies the risk, or when the user's goal is met. Report what changed in the shape of the codebase, each change and how it was verified, behavior changes and their approval, what you locked in, what you kept or deferred and why, the net size change (implementation and tests separately), and the limits of what you could see.

## Thinking deeper

These are the questions that turn a cleanup into a refinement. Return to them whenever the work starts to feel mechanical.

- Why does the code look like this? A past requirement, a deadline, a constraint that no longer holds? The reason a duplication exists often tells you whether it should.
- If this area were designed today by someone who understood all of it, what would it look like, and which differences from the current code actually matter?
- Do several findings share one cause? Scattered validations may be one missing type; five similar handlers may be one missing concept.
- What would prove this conclusion wrong, and have you looked for it?
- Is the problem the user named the real one, or a symptom of something nearby?
- When the evidence changes your mind, change the plan and say so.

## Where to be careful

Most of this campaign is judgment. A few moves fail silently or are hard to undo, so treat these as firm:

- **Deleting a check** is the one move here that fails silently: the code compiles, tests pass, and the missing protection surfaces months later as corruption or a security hole. Before deleting one, be able to say where its fact is established and why nothing on the way breaks it. If you can't, hoisting it to the boundary or encoding it in a type gets most of the benefit without the risk.
- **Public contracts** (APIs, wire and file formats, persisted schemas, configuration) are depended on in ways the repository cannot show you. Change them only with explicit approval.
- **"Unused" is a claim about every consumer.** An empty search proves little for exported, reflective, dynamically dispatched, configuration-driven, or externally consumed code. Say what your search could not see.
- **Tests are the evidence** that behavior survived. Weakening one to get a pass destroys that evidence. Change an expectation only when the old one is shown to be wrong, and report it as a behavior change.
- **Other people's work**: leave unrelated changes in the tree alone, and use no destructive version-control operations.

## Keeping a record

A campaign usually outlives one context window. Keep a record in `.refinery/<campaign>/ledger.md`, or wherever the user prefers, with two jobs: letting you or a later session resume without redoing work, and letting the user review your reasoning. On resume, read it first and check it against the current code. [Ledger format](references/ledger-format.md) shows one shape that works; keep what serves this campaign. Ask whether the user wants it committed.

## References

Read these when the work calls for them, not up front:

- [references/finding-duplication.md](references/finding-duplication.md): techniques for finding duplicated knowledge and reinvented wheels.
- [references/abstraction-judgment.md](references/abstraction-judgment.md): when sharing helps, when it hurts, and how to tell wrong and missing abstractions.
- [references/fact-ownership.md](references/fact-ownership.md): validation, guards, error handling, fallbacks, and defensive copies.
- [references/ledger-format.md](references/ledger-format.md): one shape for the campaign record.
