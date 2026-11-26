# Finding duplication and reinvented wheels

Duplication is repeated knowledge, not repeated text. Tools find text; you decide whether the knowledge is the same. Everything below produces leads, not verdicts, and none of it is a required pass: use what fits this codebase.

## Where to look first

Rot concentrates where people keep working.

- **Churn**: the files changed most often recently.
  `git log --since=12.months --format= --name-only | sort | uniq -c | sort -rn | head -50`
- **Co-change**: files that keep changing together in the same commits usually share hidden knowledge (shotgun surgery). Look at commits that touch several similar files.
- **Repeated fixes**: commit messages like "fix X in A and B", or the same fix landing in different places over time.
- **Parallel names**: similarly named files or functions in different modules (`formatDate`, `fmtDate`, `toDateString`; `UserDto`, `UserModel`, `UserView`).

## Kinds of duplication

### 1. Copies (textual or structural clones)

Copy-paste, possibly renamed or reformatted. Clone detectors find these well:

- jscpd covers many languages: `npx jscpd --min-tokens 50 --reporters console,json <path>`
- PMD CPD for JVM, C-family, and other languages; `dupl` for Go; pylint `duplicate-code` for Python.

Check each tool's `--help` first, since flags change between versions. Exclude generated, vendored, and fixture code, and trace generated copies back to their templates. Start with default thresholds, then lower them in the hot areas.

### 2. Same knowledge, different code

The most valuable kind, and the kind clone detectors miss. Search by concept:

- **Vocabulary**: `parse`, `format`, `normalize`, `validate`, `sanitize`, `convert`, `to*`/`from*`, `map*`, `build*`, `retry`, `cache`, `*Util*`, `*Helper*`, `*Manager*`.
- **Literals**: the same regex, format string, magic number, error message, URL, header name, or table name in several places.
- **API usage**: every place that calls the same low-level API with the same surrounding steps, such as manual date arithmetic around the same clock call, or the same open/try/close sequence.
- **Structure**: a structural search such as `ast-grep run -p '<pattern>' -l <lang>` for a shape you have seen once, to find its siblings.
- **Data shape**: the same concept modeled more than once (two `User` types, an enum mirrored across layers or languages, a status mapping table copied around). Hand-written mapping code between them is itself a signal.
- **Decisions**: the same business rule decided in several places, such as a permission check or eligibility condition repeated across handlers.

### 3. Reinvented wheels

Hand-written versions of something the project already has access to. Start from the dependency manifests and lockfiles and the framework and language versions in use, and ask what they already provide.

| Category | Typical hand-rolled code | Often already available from |
|---|---|---|
| Collections | grouping, chunking, unique-by, deep equality, deep clone or merge | the standard library (`Object.groupBy`, `structuredClone`, `itertools`, Go `slices`/`maps`, Java streams), lodash or similar |
| Timing | debounce, throttle, sleep with jitter | utility libraries, framework schedulers |
| Resilience | retry loops, backoff, timeouts, circuit breaking | the HTTP or RPC client, a resilience library already present |
| Time | date arithmetic, formatting, time zones | the date library in the lockfile, the standard library |
| Text and data | CSV/JSON/YAML parsing, query strings, URLs, paths, UUIDs | the standard library, existing parsers |
| Validation | field-by-field checks of request bodies | the schema library already in use (zod, pydantic, Bean Validation, ...) |
| Concurrency | worker pools, concurrency limits, manual promise or future juggling | runtime primitives, existing utility libraries |
| Data access | manual joins, per-item queries, hand-built SQL strings | the ORM or query builder in use |
| Framework | custom middleware, DI wiring, serializers, config loading, logging wrappers | the framework's own facilities |

Before recommending reuse, confirm the installed version supports the feature, and compare contracts: edge cases, error behavior, time zone and locale handling, performance. A partial match is a reason to keep a thin wrapper, not the whole reimplementation.

### 4. Divergent copies

When you find a cluster, compare the members side by side. Every difference has a reason, and the reason decides what happens to it:

- **Intentional**: a caller depends on it. It must survive consolidation, as an argument that caller passes, a composition at the call site, or a separate function.
- **Accidental**: one copy was fixed or extended and the others were not. Usually a latent bug. Consolidating changes behavior for some callers, so it needs the user's approval.
- **Unknown**: the history (`git log -L`, blame, the linked issue) usually explains it. Find out before deciding.

## What makes a finding useful

A finding is useful when someone can decide on it: what knowledge it encodes, in one sentence; where each copy lives; how the copies differ and why; and where the knowledge could live instead. Often the most valuable finding is not one cluster but the missing concept behind several of them.
