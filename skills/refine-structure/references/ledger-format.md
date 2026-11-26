# Ledger format

One markdown file per campaign, at `.refinery/<campaign>/ledger.md` unless the user chooses otherwise. Keep entries terse: it is your working record and the user's review document. On resume, read it first and check the open items against the current code before continuing.

~~~markdown
# Refinery ledger: <campaign>

Scope: <paths, modules, or features>
Goal: <the user's goal in one or two sentences>
Status: mapping | deciding | executing | closed
Updated: <YYYY-MM-DD>

## Verification
- Fast check: <build or type-check command>
- Targeted tests: <how to run the tests for one area>
- Full suite: <command>; state at start: <pass/fail counts, known failures>
- Weakly covered areas: <...>

## Map
### Capabilities
| Capability | Authoritative location or dependency | Notes |
|---|---|---|

### Ownership
| Concept or decision | Decided at today | Intended owner |
|---|---|---|

### Boundaries and facts
| Boundary | Facts established there | Re-checked at |
|---|---|---|

## Findings
### F-01 <short name>
- Kind: duplication | reinvented-wheel | wrong-abstraction | missing-abstraction | misplaced-decision | redundant-defense
- Knowledge: <one sentence>
- Evidence: <file:line, ...>
- Differences: <difference: intentional / accidental / unknown>
- Verdict: reuse | extract | split | relocate | keep | defer. <reason>
- Payoff and risk: <...>
- Status: proposed | approved | done | rejected | deferred
- Change: <commit or PR>; tests added: <...>; verified by: <commands and results>
- Behavior change: none | <description, approved by the user on YYYY-MM-DD>

## Lock-ins
- <rule or type>: <what it prevents>

## Out of scope
- <finding, location, why it was not handled>

## Final report
<written at close>
~~~
