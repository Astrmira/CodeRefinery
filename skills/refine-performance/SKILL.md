---
name: refine-performance
description: Run a measured performance refinement campaign on an application or module. Establishes representative workloads and a baseline, explains where the cost goes with profiles and a per-operation work ledger, then removes redundant work such as repeated validation, defensive copies, representation churn, chatty I/O, and invariant work redone on every call, keeping only changes that measure better without changing behavior. Use when the user asks for a deliberate performance pass over a codebase or feature, such as making it faster or cheaper, or cutting overhead, latency, memory, or query counts. Not for one-off micro-optimizations while coding or a single obvious fix.
license: MIT
metadata:
  version: "0.1.0"
---

# Refine Performance

This is a campaign you run once, deliberately, against real workloads. It is not a habit of micro-optimizing while coding.

In application code, overhead is rarely one hot function. More often the same work is done many times along a path, by layers that cannot see each other. The handler validates, the service validates again, the repository validates a third time. Data is copied "for safety" at each hop, converted between three representations, serialized to cross an in-process boundary, fetched one row per query, and logged with formatting that runs even when the level is off. Each piece is small, so the profile is flat and nothing looks worth fixing. Together they are the cost.

So the unit of this campaign is **work per operation**: for a representative request, job, command, render, or startup, what work is done, how many times, and which of it is necessary. Profiles find concentrated cost; a work ledger finds diffuse cost. Measurement decides what stays.

## What a finished campaign looks like

- Representative workloads, metrics, and a reproducible baseline, agreed with the user.
- For each workload, an explanation of where the cost goes, from profiles, a work ledger, or both.
- Every retained change has a stated hypothesis, removes or relocates work rather than disguising it, preserves behavior, and shows a gain beyond the measured noise on its target metric without regressing the guard metrics.
- Changes that did not pay off were reverted and recorded, so they are not retried.
- Necessary protection (security checks, resource limits, data integrity, concurrency safety) is still in place, possibly cheaper.
- Cheap, stable regression guards protect the wins.
- A ledger records the workloads, the baseline, every round, and the final numbers.

"Already fast enough" and "the remaining cost is necessary" are legitimate results.

## Scope and target

Take the target from the user: an operation that is slow, a resource that costs too much (CPU, memory, startup time, queries, cloud spend), or a module to make leaner. If there is no specific target, find the main entry paths and propose workloads before measuring. Agree on what "better" means before changing code.

Measure what production runs: an optimized build, production-like configuration (logging level, feature flags, pool sizes), and realistic data volume and distribution. Debug builds, development mode, and tiny fixtures mislead.

## Campaign rhythm

The phases describe the shape of the work, not a script. Spend effort where the evidence leads.

### 1. Frame: workloads, metrics, baseline

- Choose one to three representative workloads. For each, define the operation, the input sizes and distribution, and whether cold start, first use, or steady state is the subject.
- Pick one primary metric per workload and a few guard metrics: memory, tail latency, error rate, output equality.
- If no driver exists, build the smallest reproducible one: a benchmark, a load script, a loop over the real path, a startup timer. Prefer the project's existing benchmark tooling.
- Record the baseline with its spread, and measure the noise band by repeating the baseline. A difference inside the noise is not a result.
- Add **work counters** where they are cheap: queries, network calls, allocations, validations, serializations per operation. Counts are deterministic, so they verify structural changes exactly where timings only approximate.

See [measurement](references/measurement.md).

### 2. Explain: where the cost goes

Use two complementary lenses:

- **Profile** the workload with a sampling profiler. If a few frames dominate, tie each to file and line ownership and start there. Look for algorithmic problems first; they are often the largest win.
- **Build a work ledger** for one representative operation: follow it from entry to exit, in code and with instrumentation, and record every unit of work with its count per operation and whether it is necessary. Redundant work shows up as the same fact checked repeatedly, the same data converted back and forth, per-item I/O, invariant work redone on every call, and results nobody uses. See [work ledger](references/work-ledger.md).

A flat profile, or one dominated by many small frames in validation, mapping, logging, and framework layers, means the work ledger is the right lens. When wall time far exceeds CPU time, the cost is waiting (I/O, locks, awaits in sequence, sleeps), and on-CPU profiles will not show it; use tracing, off-CPU, or async-aware tools.

Classify what you find with the [cost taxonomy](references/cost-taxonomy.md), and rank by count × unit cost × how often the operation runs.

If your environment supports subagents or parallel workers, delegate tracing of separate paths or modules, and have each return ledger rows with file:line evidence rather than file contents. Never run benchmarks in parallel workers on the same machine.

**Checkpoint.** Before changing code, present the workloads, the baseline, where the cost goes, and the ranked hypotheses, and let the user adjust, unless they told you to proceed on your own.

### 3. Change: one hypothesis per round

- State one hypothesis and its expected effect, for example: "the order is validated in three layers; establishing it once at the handler and passing a validated type removes two of them, about X per request."
- Make the smallest change that tests it. Prefer structural fixes: remove the work, do it once, move it to the right layer, change the representation, batch it, or take it off the hot path. Micro-tweaks come last and need the strongest evidence.
- For validation, guards, error handling, and defensive copies, use [fact ownership](references/fact-ownership.md). A necessary guard can often be made cheap instead of removed.
- A cache is a new owner of state. Add one only with a defined key, invalidation, size bound, and evidence of reuse, and first ask whether the work can be removed instead.
- Run independent waits concurrently; do not add threads to CPU-bound work without evidence.
- When the fix is architectural (a canonical representation, one owner for validation, batching in the data layer), treat it as a structural change unit: pin behavior with tests first and migrate every caller in scope.

### 4. Verify: correctness, then measurement

- **Correctness first**: build, run targeted tests, and compare the workload's outputs before and after the change.
- **Measure under the same conditions**: the same command, inputs, and machine state; one benchmark at a time; baseline and candidate alternated in short adjacent runs rather than all of one followed by all of the other. Compare medians and spread, and percentiles for latency.
- **Decide**: keep a change when the primary metric improves beyond the noise and the guard metrics hold. A change that removes work (counters drop) with neutral timing may stay if it also simplifies the code. Revert a change that is within the noise and adds complexity, or that regresses anything.
- **Log every round** in the ledger, reverted ones included: hypothesis, change, commands, numbers, decision.
- Run the affected benchmarks each round; run the full benchmark set and test suite at milestones and at the end.

### 5. Lock in and close

Protect the wins with cheap, stable guards: deterministic assertions in tests (queries per request, allocations per call), or a benchmark budget in CI where the project already runs benchmarks. Timing gates on noisy shared runners cause more trouble than they prevent.

Stop when the target is met, when the remaining cost is necessary or out of scope, or when the next hypotheses promise less than the noise band or too little to justify their complexity. Then report:

- Baseline and final numbers per workload, with spread and conditions.
- Where the remaining cost lies, and why it stays.
- Kept and reverted rounds, with reasons.
- Behavior changes, with their approval.
- Regression guards added.
- Limits of the evidence, such as differences between the measurement environment and production.

## Hard boundaries

- Do not change behavior, output, wire formats, or public APIs without explicit approval.
- Optimize the product, not the benchmark: no special cases for benchmark inputs, no changes to the workload definition to look better, no caches keyed to the benchmark's shape.
- Do not remove protection against attacks, resource exhaustion (size limits, timeouts, recursion depth), data corruption, or races. Make it cheaper instead.
- Do not claim an improvement without before-and-after measurements under equivalent conditions, and report the noise.
- Do not disable safety checks globally or add unsafe compiler or runtime flags to win numbers.
- Never run two benchmarks at once on one machine.
- Preserve unrelated work in the tree. No destructive version-control operations.

## Ledger

Keep the campaign state in `.refinery/<campaign>/ledger.md`, or wherever the user prefers. Put profiles, traces, and raw results beside it; they usually should not be committed. On resume, read the ledger first, re-establish the baseline on the current code, and continue from the open hypotheses.

## References

Read these when the work calls for them, not up front:

- [references/measurement.md](references/measurement.md): when building the harness, establishing the baseline, and comparing results.
- [references/work-ledger.md](references/work-ledger.md): when explaining diffuse cost along an operation.
- [references/cost-taxonomy.md](references/cost-taxonomy.md): when classifying costs and choosing fixes.
- [references/fact-ownership.md](references/fact-ownership.md): whenever a cost involves validation, guards, error handling, fallbacks, or defensive copies.
- [references/ledger-format.md](references/ledger-format.md): when creating or resuming the ledger.
