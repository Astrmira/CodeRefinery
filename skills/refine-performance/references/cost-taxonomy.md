# Cost taxonomy

Classify each cost before choosing a fix. Each category lists how it shows up, the fixes that usually work, and what to watch out for. Fixes that remove work beat fixes that make the same work faster.

## Algorithmic

- **Shows up as**: cost growing faster than the input; nested loops hidden inside helpers, such as `contains` on a list inside a loop, repeated sorting, string concatenation in loops, recursive recomputation.
- **Fix**: the right data structure (a set or map for lookups), a better algorithm, computing once outside the loop.
- **Watch**: often the biggest single win; check for it first in any hotspot.

## Redundant validation and defensive checks

- **Shows up as**: the same fact checked in several layers; checks inside per-item loops; exception construction and message formatting on hot paths.
- **Fix**: see fact-ownership.md. Hoist to the boundary, encode in a type, make the guard cheap, or validate once per batch.
- **Watch**: never remove protection against attacks, resource exhaustion, corruption, or races.

## Defensive copies

- **Shows up as**: collections or objects copied on the way in and out of each layer; deep clones "for safety".
- **Fix**: clarify ownership with immutable types, read-only views, or explicit transfer.
- **Watch**: data that really is shared and mutated concurrently.

## Representation churn

- **Shows up as**: mapping between DTOs, entities, and view models on every hop; JSON or other serialization between in-process layers; repeated parsing and formatting of dates, numbers, and IDs; reflection-based mappers dominating a profile.
- **Fix**: one canonical internal representation, parsed once at the boundary, converted only at the edges; generated or hand-written mappers where reflection dominates.
- **Watch**: representations that exist for a real reason, such as public API stability or the persistence schema.

## I/O patterns

- **Shows up as**: N+1 queries; chatty calls to the same service; independent awaits in sequence; over-fetching rows, columns, or relations; missing indexes; transactions or locks wider than needed; no pagination.
- **Fix**: batch, join, prefetch; select only needed fields; run independent calls concurrently; add the index the query plan asks for (check with `EXPLAIN`); narrow transactions.
- **Watch**: concurrency limits of downstream systems; consistency requirements that justify a transaction.

## Repeated invariant work

- **Shows up as**: configuration or environment parsed per request; regexes, templates, or serializers built per call; reflection or metadata lookups per call; permissions resolved per item; derived values recomputed.
- **Fix**: compute once at the right scope (process start, request, batch); memoize with a clear owner and lifetime.
- **Watch**: values that really do change, such as hot-reloaded configuration or per-tenant settings.

## Caching mistakes

- **Shows up as**: expensive pure work repeated with the same inputs (a missing cache); or low hit rates, unbounded growth, stampedes, several layers caching the same thing, invalidation so frequent the cache never helps.
- **Fix**: measure the hit rate before and after; one owner per cached value; a bounded size; explicit invalidation.
- **Watch**: a cache is state. Removing the work is better than caching it.

## Eager and unused work

- **Shows up as**: eager loading of relations; computing fields nobody reads; initializing every module at startup; building debug data in production.
- **Fix**: delete it, make it lazy, or move it off the critical path.
- **Watch**: moving cost from startup to the first request defers it; it does not remove it.

## Logging and telemetry

- **Shows up as**: messages formatted and objects serialized regardless of level; logging inside tight loops; synchronous log I/O on hot paths; high-cardinality metrics.
- **Fix**: lazy or level-guarded arguments, sampling, asynchronous appenders, coarser metrics.
- **Watch**: audit logs and other records that are requirements, not diagnostics.

## Allocation and memory

- **Shows up as**: per-item allocations in hot loops; intermediate collections in long chains; boxing; buffers that grow repeatedly; high GC time.
- **Fix**: presize, reuse, stream instead of materializing, and use value types or primitive collections where the language supports them.
- **Watch**: object pools add lifetime bugs; use them only with evidence.

## Concurrency and waiting

- **Shows up as**: wall time far above CPU time; lock contention; locks held during I/O; thread-pool starvation; blocking calls inside async code; polling with sleeps; timeouts used as control flow.
- **Fix**: narrow critical sections, never hold locks across I/O, use async end to end, replace polling with events, run independent work concurrently.
- **Watch**: more threads do not fix starvation caused by blocking.

## Exceptions as control flow

- **Shows up as**: exceptions thrown and caught on normal paths, such as parse attempts or lookups that usually fail; stack-trace capture in a profile.
- **Fix**: return values or try-style APIs for expected outcomes.
- **Watch**: keep exceptions for genuinely exceptional failures; this is about the expected path only.

## Framework and abstraction overhead

- **Shows up as**: middleware, interceptors, filters, or proxies running on every request whether needed or not; dependency resolution per call; ORM change tracking on read-only queries; deep wrapper chains that add no decision.
- **Fix**: scope cross-cutting concerns to the paths that need them; use no-tracking reads; resolve dependencies once; remove pass-through layers (the `refine-structure` skill covers the structural side).
- **Watch**: cross-cutting concerns that enforce security or auditing.
