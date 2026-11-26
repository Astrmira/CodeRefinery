# Ledger format

The campaign record has two jobs: letting you, or a later session, resume without redoing work, and letting the user review your reasoning. Anything that serves those jobs belongs in it; anything that doesn't is overhead. Keep entries terse.

Below is one shape that works for a structural campaign. Drop sections that do not apply, add what this campaign needs, and let the map grow only as detailed as the decisions require. On resume, read the record first and check open items against the current code, because the code may have moved on.

~~~markdown
# Refinery ledger: <campaign>

Scope: <paths, modules, or features>
Goal: <the user's goal in one or two sentences>
Status: <where the campaign stands, and what is next>
Updated: <YYYY-MM-DD>

## Verification
How to check a change quickly, how to run the full suite, the state at the start
(known failures), and where coverage is weak.

## Map
What exists and who owns what. Tables work well, for example:

| Capability | Authoritative location or dependency | Notes |
|---|---|---|

| Concept or decision | Decided at today | Should be owned by |
|---|---|---|

| Boundary | Facts established there | Checked again at |
|---|---|---|

## Findings
### F-01 <short name>
- What it is: <the knowledge or problem, in one sentence>
- Evidence: <file:line, ...>
- Differences that matter: <and whether each is intentional, accidental, or unknown>
- Conclusion: <what you propose and why>
- Cost and risk: <...>
- Status: <proposed, approved, done, rejected, deferred>
- Change and verification: <commit or PR, tests added, what was run, and whether the tests were seen to catch a deliberate mistake>
- Behavior change: <none, or what changed and when the user approved it>

## Lock-ins
<rule or type, and what it prevents>

## Out of scope
<finding, where, and why it was not handled>

## Final report
<written at close>
~~~
