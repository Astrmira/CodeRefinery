---
name: refine-performance
description: Run a measured performance refinement campaign on an application or module. Establishes representative workloads and a baseline, explains where the cost goes with profiles and a per-operation work ledger, then removes redundant work such as repeated validation, defensive copies, representation churn, chatty I/O, and invariant work redone on every call, keeping only changes that measure better without changing behavior. Use when the user asks for a deliberate performance pass over a codebase or feature, such as making it faster or cheaper, or cutting overhead, latency, memory, or query counts. Not for one-off micro-optimizations while coding or a single obvious fix.
license: MIT
metadata:
  version: "0.2.0"
---

# Refine Performance

This is a campaign you run once, deliberately, against real workloads. It is not a habit of micro-optimizing while coding.

What follows describes what matters and why. It is guidance for your judgment, not a procedure: follow the evidence, go back when a measurement surprises you, and skip what does not apply. The few things that are firm are marked as such and explain themselves.

## The idea

In application code, overhead is rarely one hot function. More often the same work is done many times along a path, by layers that cannot see each other. The handler validates, the service validates again, the repository validates a third time. Data is copied "for safety" at each hop, converted between three representations, serialized to cross an in-process boundary, fetched one row per query, and logged with formatting that runs even when the level is off. Each piece is small, so the profile is flat and nothing looks worth fixing. Together they are the cost.

So think in terms of **work per operation**: for a representative request, job, command, render, or startup, what work is done, how many times, and which of it the outcome actually needs. Profiles find concentrated cost; counting the work finds diffuse cost; measurement decides what stays.

## What done and deep mean

When the campaign is done:

- The workloads, metrics, and a reproducible baseline were agreed with the user.
- Every change that stayed removes or relocates work rather than disguising it, preserves behavior, and beats the measured noise on its target metric without making the guard metrics worse.
- Attempts that did not pay off were reverted and recorded, so nobody retries them blindly.
- Necessary protection (security checks, resource limits, data integrity, concurrency safety) is still in place, possibly cheaper.
- The wins are protected by cheap, stable regression guards.
- There is a record of the workloads, the baseline, each attempt, and the final numbers.

Depth is what separates a campaign from a few tweaks:

- For each workload you can account for where the cost goes, including what remains after your changes and why it stays.
- You have a sense of the floor: the least work the operation needs (the queries, the data movement, the computation), and how far the current path is from it. That gap, more than the top frame of a profile, is the opportunity.
- You looked for diffuse cost, not only hotspots.

"Already fast enough" and "the remaining cost is necessary" are legitimate results when they are earned by measurement.

## Scope and target

Take the target from the user: an operation that is slow, a resource that costs too much (CPU, memory, startup time, queries, cloud spend), or a module to make leaner. If there is no specific target, find the main entry paths and propose workloads before measuring. Agree on what "better" means before changing code.

Measure what production runs: an optimized build, production-like configuration (logging level, feature flags, pool sizes), and realistic data volume and distribution. Debug builds, development mode, and tiny fixtures distort exactly the costs this campaign is after.

## How the work tends to go

A campaign moves through framing, explaining, changing, and verifying. In practice these loop: a surprising measurement sends you back to explaining, and a failed hypothesis teaches you something about the system. Treat the sections below as concerns to keep in view, not steps to complete.

### Frame what you are measuring

The goal is a target you can measure and trust. Pick a few workloads that reflect what users actually do, not the ones that happen to be easy to benchmark, and decide for each whether cold start, first use, or steady state is the subject. Give each a primary metric and a few guard metrics (memory, tail latency, error rate, output equality), so a win on one axis cannot hide a loss on another. Build the smallest reproducible driver if none exists, preferring the project's own benchmark tooling.

Repeat the baseline until you know its spread; without a noise band you cannot tell a win from luck. Where it is cheap, also count the work per operation (queries, calls, allocations, validations). Counts are deterministic, so they show exactly whether a change removed what it targeted. [Measurement](references/measurement.md) covers harnesses, tools, conditions, and noise.

### Explain where the cost goes

A sampling profile shows concentrated cost; tie dominant frames to the code that owns them, and check for algorithmic problems first, since they are often the largest win. A [work ledger](references/work-ledger.md) shows diffuse cost: follow one representative operation from entry to exit and note each unit of work, how often it happens, and whether the outcome needs it. A flat profile, or one full of small frames in validation, mapping, logging, and framework layers, is the signal to reach for the ledger. When wall time far exceeds CPU time, the cost is waiting (I/O, locks, awaits in sequence), which on-CPU profiles miss and tracing or off-CPU tools show.

The [cost taxonomy](references/cost-taxonomy.md) helps you recognize what you find. What matters is roughly count × unit cost × how often the operation runs: a small check inside a loop on the busiest path outweighs a large one on an admin page.

If your environment supports subagents or parallel workers, delegate tracing of separate paths and ask for ledger rows with file:line evidence rather than file contents. Keep all benchmarking in one place, one run at a time.

Before changing code, show the user the workloads, the baseline, where the cost goes, and the hypotheses you would pursue first, unless they asked you to proceed on your own. They know which paths matter and which constraints are real, and that is cheap to learn now and expensive to learn later.

### Change one idea at a time

Test one hypothesis per change. When two changes land together you cannot tell which one helped, and a regression can hide behind a win. State what you expect, for example: "the order is validated in three layers; establishing it once at the handler and passing a validated type removes two of them, about X per request." Then make the smallest change that tests it.

Prefer fixes that remove work: not doing it, doing it once, doing it at the right layer, changing the representation, batching it, moving it off the hot path. They tend to simplify the code as well. Micro-tweaks make the same work faster, usually add complexity, and need the strongest evidence. For validation, guards, error handling, and defensive copies, [fact ownership](references/fact-ownership.md) explains how to tell what can go; a necessary guard can often be made cheap instead.

A cache is a new owner of state, with its own invalidation and staleness bugs, so first ask whether the work can be removed; a cache that stays needs a defined key, invalidation, a size bound, and evidence of reuse. Concurrency helps independent waits, not CPU-bound work. When the fix is architectural (a canonical representation, one owner for validation, batching in the data layer), treat it as a structural change: pin behavior with tests first and migrate every caller in scope.

### Verify honestly

Correctness comes first: build, run the targeted tests, and compare the workload's outputs before and after. Then measure under the same conditions as the baseline, alternating baseline and candidate runs so that drift in the machine cannot pose as a result. How much rigor you need depends on how close the effect is to the noise.

Keep a change when the primary metric improves beyond the noise and the guard metrics hold; one that measurably removes work with neutral timing can stay if it also simplifies the code. Revert what sits within the noise and adds complexity, and anything that makes something worse. Record every attempt, reverted ones included: failures are knowledge about the system, and the record stops them being retried. Run the affected benchmarks each round, and the full benchmark set and test suite at milestones and before you close.

### Make the wins stick and close

Protect the wins with guards that are cheap and stable: deterministic assertions in tests (queries per request, allocations per call), or a benchmark budget in CI where the project already runs benchmarks reliably. Timing gates on noisy shared runners produce false alarms until people ignore them.

The campaign is over when the target is met, when the remaining cost is necessary or out of scope, or when the next ideas promise less than the noise or too little for their complexity. Report baseline and final numbers with their conditions, where the remaining cost lies and why, the attempts kept and reverted, behavior changes and their approval, the guards added, and the limits of the evidence.

## Thinking deeper

These are the questions that turn tuning into refinement. Return to them whenever the work starts to feel mechanical.

- What is the least work this operation could possibly do, and how far is the current path from it?
- Where would a tenfold improvement come from, rather than ten percent? Usually from work not done at all: a query not made, a conversion not needed, a validation already guaranteed.
- Why is this work here? Some exists for a past requirement, a bug fixed at the wrong layer, or an assumption that no longer holds.
- Is this cost necessary for the outcome, or only for the current structure?
- What is the cheapest experiment that would prove this hypothesis wrong? Run it before building the fix.
- Does the measurement reflect what users experience?
- When a result surprises you, understand it before moving on. A surprise is where your model of the system is wrong.

## Where to be careful

Most of this campaign is judgment. A few things decide whether its results can be trusted at all, so treat these as firm:

- **Behavior and contracts.** Performance work must not change what the code does. Users and other systems depend on outputs, formats, and public APIs in ways a benchmark never checks. Any change there needs explicit approval.
- **Benchmark integrity.** Numbers obtained by optimizing the benchmark instead of the product are false: special cases for benchmark inputs, a workload redefined to look better, caches keyed to the benchmark's shape. Claim an improvement only from before-and-after measurements under equivalent conditions, with the noise reported. Never run two benchmarks at once on one machine; they contaminate each other.
- **Protection.** Guards against attacks, resource exhaustion (size limits, timeouts, recursion depth), corruption, and races exist for inputs a benchmark never sends. Make them cheaper; do not remove them. For the same reason, do not disable safety checks globally or add unsafe compiler or runtime flags to win numbers.
- **Other people's work**: leave unrelated changes in the tree alone, and use no destructive version-control operations.

## Keeping a record

A campaign usually outlives one context window. Keep a record in `.refinery/<campaign>/ledger.md`, or wherever the user prefers, so that you or a later session can resume without redoing work and the user can check your reasoning and numbers. Raw profiles and results can sit beside it, usually uncommitted. On resume, re-establish the baseline on the current code: numbers from an older state are history, not a baseline. [Ledger format](references/ledger-format.md) shows one shape that works; keep what serves this campaign.

## References

Read these when the work calls for them, not up front:

- [references/measurement.md](references/measurement.md): harnesses, tools, conditions, noise, and comparing results.
- [references/work-ledger.md](references/work-ledger.md): counting the work along an operation to expose diffuse cost.
- [references/cost-taxonomy.md](references/cost-taxonomy.md): recognizing kinds of cost and the fixes that usually work.
- [references/fact-ownership.md](references/fact-ownership.md): validation, guards, error handling, fallbacks, and defensive copies.
- [references/ledger-format.md](references/ledger-format.md): one shape for the campaign record.
