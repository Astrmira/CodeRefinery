# Work ledger: finding diffuse cost

A profiler shows where time is spent. A work ledger shows what work is done and how many times, which is what you need when the cost is spread thin across layers. It turns "everything is a bit slow" into a list of specific, countable, removable work.

## Pick the operation

One representative operation per ledger: a request, a job, a command, a render, a startup. Use a typical input and note its size. If the cost depends on input size (N items), build the ledger for a realistic N and mark which entries scale with it.

A ledger needs the work that matters, not every line of code. Start coarse, one row per layer or major step, and go finer where a count surprises you or a step costs more than it should.

## Build it from two sides

- **Static trace**: read the path from entry to exit (handler, middleware, service, domain, repository, serializer, and back) and note what each hop does to the data.
- **Dynamic counts**: confirm against the running system. Cheap sources:
  - SQL and query logs (ORM logging, `pg_stat_statements`, slow query logs), plus `EXPLAIN ANALYZE` for the heavy queries;
  - HTTP and RPC client logs, tracing spans (OpenTelemetry), service mesh metrics;
  - allocation profilers and GC logs;
  - temporary counters or log lines around suspected functions (validators, mappers, serializers), removed afterwards;
  - syscall summaries (`strace -c`, ETW, dtruss) for file and network chatter.

Counts from the running system beat counts from reading code. Middleware, interceptors, proxies, ORM lazy loading, and framework hooks do work the code path does not show.

## What to record

For each piece of work: where it happens, what kind of work it is, how many times it runs per operation, whether that grows with N, whether the outcome needs it, and who owns it. For example:

| Step | Work | Kind | Count per op | Scales with N | Needed? | Owner |
|---|---|---|---|---|---|---|
| `OrderController.create` | validate order body | validation | 1 | no | yes: external boundary | handler |
| `OrderService.place` | validate order again | validation | 1 | no | no: same fact, already established | none |
| `OrderService.place` | load product per line | query | N | yes | no: one batched query suffices | repository |
| `AuditInterceptor` | serialize the whole order for a debug log | serialization | 1 | yes | no: debug level is off in production | logging |

Kinds of work to look for:

- **Validation**: the same fact checked more than once.
- **Copies**: defensive copies, clones, immutable rebuilds.
- **Conversion**: DTO to entity to view model and back; parsing and formatting dates, numbers, and IDs; JSON encode and decode inside one process.
- **I/O round trips**: queries, cache calls, network calls, file reads, and whether they run one after another.
- **Repeated invariant work**: parsing configuration, compiling regexes or templates, reflection lookups, permission resolution, the same derived value computed on every call or item.
- **Observability**: log formatting and object serialization regardless of level; metrics and spans inside tight loops.
- **Allocation churn**: per-item allocations, intermediate collections, string building in loops.
- **Synchronization**: locks taken, especially around I/O; contended atomics.
- **Retries, timeouts, sleeps**: and how many layers each one exists in.
- **Framework layers**: middleware and interceptors on paths that do not need them; ORM change tracking on read-only queries; hydration of columns and relations nobody reads.
- **Unused results**: work computed and discarded, eager loading, fields fetched and never read.

## Reading the ledger

| Pattern | Usually means | Usual direction |
|---|---|---|
| Same fact checked in several steps | No clear establisher | fact-ownership.md: hoist, encode in a type, or make cheap |
| Data converted back and forth | No canonical internal representation | Parse once at the boundary and pass the parsed form |
| I/O count equals N | Per-item access | Batch, join, prefetch |
| Independent waits in sequence | Accidental serialization | Run concurrently, or combine into one call |
| Same result recomputed per call or item | Work at the wrong scope | Compute once per process, request, or batch; memoize with a clear owner and lifetime |
| Result never used | Eager or leftover work | Make it lazy, or delete it |
| Retry or timeout in several layers | No single owner of the policy | One owner; the other layers propagate |
| Work in a layer the operation does not need | Over-broad middleware or hooks | Scope it to the paths that need it |

Prioritize by count × unit cost × frequency of the operation. A small check inside a loop over N items on the busiest endpoint matters more than a large one on an admin page.

## Verifying with the ledger

After each change, recount. Counts are exact: if a change was meant to remove two validations and N−1 queries, the ledger should show exactly that. Then confirm with timing that the removed work mattered.
