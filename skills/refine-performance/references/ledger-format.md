# Ledger format

One markdown file per campaign, at `.refinery/<campaign>/ledger.md` unless the user chooses otherwise. Keep entries terse: it is your working record and the user's review document. Profiles, traces, and raw results go in the same directory. On resume, read the ledger first and re-establish the baseline on the current code before continuing.

~~~markdown
# Refinery ledger: <campaign> (performance)

Scope: <application, module, or feature>
Goal: <the user's target in one or two sentences>
Status: framing | explaining | optimizing | closed
Updated: <YYYY-MM-DD>

## Environment
- Machine, OS, runtime versions, build configuration: <...>
- Data set: <source, size, distribution>

## Workloads
### W-01 <name>
- Operation: <what is executed, with which inputs>
- Phase: cold start | first use | steady state
- Command: <exact command>
- Primary metric: <...>; guard metrics: <...>
- Counters: <what is counted per operation, and how>

## Baseline
| Workload | Metric | Median | Spread | Runs | Noise band | Commit |
|---|---|---|---|---|---|---|

## Where the cost goes
### W-01
- Profile: <top costs with file:line ownership>
- Work ledger:

| Step | Work | Kind | Count per op | Scales with N | Necessary? | Owner |
|---|---|---|---|---|---|---|

## Hypotheses
| ID | Hypothesis | Expected effect | Evidence | Status |
|---|---|---|---|---|

## Rounds
### R-01 <short name>
- Hypothesis: <...>
- Change: <files, commit>
- Correctness: <tests and output comparison, with results>
- Measurement: <command; baseline and candidate pairs; median and spread; counter changes>
- Decision: kept | reverted. <reason>

## Behavior changes
- <description, approved by the user on YYYY-MM-DD>

## Regression guards
- <test, assertion, or budget>: <what it protects>

## Final report
<written at close>
~~~
