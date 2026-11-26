# Measurement

Measurements decide what stays, and they are only as good as their conditions.

## Choose the harness for the question

| Question | Harness |
|---|---|
| Is this function faster? | Microbenchmark |
| Is this module faster with its real dependencies? | Component benchmark |
| Is the request, job, or command faster for users? | End-to-end run or load test |
| Does the application start faster? | Repeated cold starts with a timer |
| Is less work being done? | Counters: queries, calls, allocations, validations per operation |

A microbenchmark gain does not prove a product gain. Confirm important wins on the end-to-end workload.

Common tools, to be checked against the versions the project uses (the tool's `--help` overrides any example here):

- Benchmarks: JMH (JVM), BenchmarkDotNet (.NET), Go `testing.B` with `benchstat`, Rust criterion, Python pyperf or pytest-benchmark, JavaScript tinybench or mitata, hyperfine for whole commands, and k6, wrk, oha, or vegeta for HTTP load.
- CPU profilers: async-profiler or JFR (JVM), dotnet-trace and dotnet-counters (.NET), pprof (Go), py-spy or Scalene (Python), perf or samply (native code, Rust, C++), `node --cpu-prof` or Chrome DevTools (JavaScript).
- Memory: heap snapshots and allocation profilers for the runtime in use, memray (Python).
- Databases: `EXPLAIN ANALYZE`, slow query logs, `pg_stat_statements` or its equivalent.
- Waiting and distributed cost: tracing spans (OpenTelemetry), off-CPU profiling.

Prefer what the project already uses.

## Conditions

- An optimized build and production-like configuration: logging level, feature flags, pool sizes, runtime settings.
- Realistic data volume and distribution. Tiny fixtures hide per-item costs and change query plans.
- Warm up JITs, caches, and connection pools unless cold behavior is the subject. Measure cold start, first use, and steady state separately.
- The same machine state for compared runs: close heavy processes, keep power settings fixed, run one benchmark at a time.
- Record the commit, the environment (hardware, OS, runtime version, configuration), the exact commands, and the raw numbers.

## Noise

Repeat the baseline several times before changing anything. The spread you see is the noise band for this machine and workload. Report the median with its spread (interquartile range, or min and max), and percentiles (p50, p95, p99) for latency; averages hide tails.

A difference inside the noise band is no difference. Do not keep adding iterations until the result you want appears.

## Comparing baseline and candidate

- Alternate short adjacent runs: baseline, candidate, baseline, candidate. If all baseline samples run first and all candidate samples later, drift in machine state can masquerade as a result.
- Keep everything identical except the code: command, inputs, warmup, iteration count.
- Use the statistical comparison your tool provides where it exists (benchstat, BenchmarkDotNet, pyperf `compare_to`, hyperfine's summary).
- Record every pair. Exclude one only with objective evidence of contamination (a competing process, a load spike, an interruption), and record the exclusion. Never exclude by the direction of the result.
- If results conflict or drift, stop changing code and fix the measurement first.

## Counters

Counts of queries, calls, allocations, and validations per operation are deterministic, so compare them exactly. They are the cleanest evidence that a structural change removed the work it targeted. Confirm with timing at milestones that the removed work mattered.

## Reading results

- Startup faster but first request slower: the cost was deferred, not removed.
- Mean faster but p99 slower: a regression for most interactive systems.
- Throughput up but memory or error rate up: check the guard metrics before claiming a win.
- Memory: distinguish the managed heap from process memory, and a bounded cache from a leak.
- A benchmark gain with no change in the product metric: the benchmark missed the critical path, used unrealistic inputs, or optimized a cost that does not dominate.

## Keep the loop short

Benchmarks are slow. Use small, fast runs to explore and larger runs to decide. Run only the benchmarks the current round affects, and the full set at milestones and at the end. Keep builds incremental.
