# Abstraction judgment

The aim is to remove repeated knowledge and unnecessary coupling, not to maximize sharing. Both directions are legitimate: extract a missing abstraction, or dismantle a wrong one.

The signals below are reasons to look closer, not verdicts. One signal rarely settles anything; several pointing the same way, together with the history of the code, usually do.

## The test for sharing

Two pieces of code should share one implementation when they encode the same knowledge:

- They would change together, for the same reason.
- They belong to the same owner: the same concept.
- Their contracts match: inputs, outputs, errors, side effects, and performance, security, and deployment constraints.

Similar shape without these is coincidence. Merging coincidental code creates coupling, and a later change for one caller breaks the other.

When only a generic mechanism is shared (iteration, retry plumbing, formatting machinery), share the mechanism and leave the business rules with their owners.

## The reuse ladder

Prefer the lowest rung that fits:

1. An existing implementation in the repository.
2. An installed dependency, the framework, or the standard library.
3. A new, small capability extracted from the duplicates.
4. Keeping the duplication.

Every rung requires a contract comparison, not a name match.

## Designing an extraction

- **Name the knowledge.** If you cannot say in one sentence what the shared code knows, it is not one piece of knowledge.
- **Home it with its owner**, the module whose concept it is. A catch-all `utils` module hides the knowledge again and becomes the next junk drawer.
- **Keep the contract narrow.** Callers' differences stay with the callers: they pass a function, compose a smaller piece, or keep their own variant. Mode flags and option bags that select behavior are how a wrong abstraction starts.
- **Consider the blast radius.** A bug in shared code reaches every caller at once. Shared code on a critical path may deserve more tests than the copies had.
- **Count the cost honestly.** Lines removed and added, implementation and tests separately; migration risk; one more indirection for every future reader. Saving ten lines at the price of a hop through three files is a loss.

## Signals of a wrong abstraction

- Boolean or mode parameters that switch behavior.
- Branches on the caller's identity or type.
- Parameters only some callers pass; options most callers ignore.
- Callers that work around it: the same pre- or post-processing at every call site.
- The name no longer describes what it does.
- Changes made for one caller regularly break others.
- Pass-through layers that add no decision: a service that forwards to a repository with an identical signature, a wrapper that only renames a library function.

To fix it, inline the abstraction back into each caller, keep in each caller only what that caller uses, then look again for what is really shared. Do it in one change unit so the code never sits half-migrated. (Sandi Metz, "The Wrong Abstraction".)

## Signals of a missing abstraction

- **Primitive obsession**: IDs, money, email addresses, and units as bare strings and numbers, with their validation and formatting scattered. A value type removes the duplication and the repeated checks together.
- **Data clumps**: the same group of parameters passed together through several functions.
- **Repeated conditionals**: the same switch on the same status or type in many places. One table, one polymorphic dispatch, or one decision function.
- **Repeated protocols**: the same sequence of steps (acquire, try, release; begin, work, commit or roll back) written out at every use. A higher-order function or scoped construct.
- **Shotgun surgery**: one logical change requires edits in many files.
- **Scattered decisions**: a policy (permissions, pricing, eligibility) decided in many handlers instead of asked of one owner.

## Single-implementation abstractions

Counting implementations does not settle it. An interface or adapter with one implementation is justified when it:

- isolates an external system, I/O, or a vendor that tests need to replace or that the project genuinely expects to swap;
- marks a plugin, extension, or module boundary, or keeps a public API stable;
- is required by the framework (dependency injection, SPI);
- breaks a dependency cycle.

It is suspect when nothing depends on the interface except the implementation and its registration, it mirrors the class method for method, and tests could use the concrete type or a plain function.

## Duplication worth keeping

- Code across deployment, language, or process boundaries with no practical shared contract.
- Copies owned by different teams or release cycles that are expected to diverge.
- Tests, where readability beats sharing. Shared builders and fixtures are fine; shared assertions that hide intent are not.
- Small duplication where a shared helper would cost more in indirection than it saves.

Record why it was kept, so the next pass does not rediscover it.

## Where a decision should live

Closest to the data or concept it is about. One place decides; others ask. When a decision is spread across layers, consolidating its ownership often removes duplication and redundant checks in the same move.
