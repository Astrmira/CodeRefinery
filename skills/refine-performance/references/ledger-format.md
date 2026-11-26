# Ledger format

The campaign record has two jobs: letting you, or a later session, resume without redoing work, and letting the user check your reasoning and numbers. Anything that serves those jobs belongs in it; anything that doesn't is overhead. Keep entries terse, and keep raw profiles, traces, and benchmark output in files beside it rather than pasted in.

Below is one shape that works for a performance campaign. Drop sections that do not apply and add what this campaign needs. The parts most worth keeping are the exact commands and conditions, because without them no number can be reproduced, and the record of reverted attempts, because they are the cheapest knowledge to lose. On resume, re-establish the baseline on the current code before comparing anything.

~~~markdown
# Refinery ledger: <campaign> (performance)

Scope: <application, module, or feature>
Goal: <the user's target in one or two sentences>
Status: <where the campaign stands, and what is next>
Updated: <YYYY-MM-DD>

## Environment
Machine, OS, runtime versions, build configuration, and the data set
(source, size, distribution).

## Workloads
### W-01 <name>
- Operation: <what is executed, with which inputs; cold start, first use, or steady state>
- Role: <primary, guard, or a diagnostic added later>
- Command: <exact command>
- Metrics: <primary metric; guard metrics>
- Counters: <what is counted per operation, and how>

## Baseline
| Workload | Metric | Median | Spread | Runs | Commit |
|---|---|---|---|---|---|

Noise band: <how much the baseline varies between repeated runs, and what an A/A
comparison reported>

## Where the cost goes
Per workload: a profile summary with the code that owns the top costs, and a work
ledger where cost is diffuse, for example:

| Step | Work | Kind | Count per op | Scales with N | Needed? | Owner |
|---|---|---|---|---|---|---|

## Ideas
| Idea | Expected effect | Evidence | Status |
|---|---|---|---|

## Attempts
### A-01 <short name>
- Hypothesis: <...>
- Change: <files, commit>
- Correctness: <tests and output comparison, with results>
- Measurement: <command; baseline and candidate runs; median and spread; counter changes>
- Outcome: <kept as faster, kept as less work, or reverted, and why>

## Behavior changes
<what changed, and when the user approved it>

## Regression guards
<test, assertion, or budget, and what it protects>

## Final report
<written at close>
~~~
