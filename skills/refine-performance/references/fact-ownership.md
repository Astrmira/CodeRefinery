# Fact ownership: validation, guards, and defensive code

Checks, guards, try/catch blocks, fallbacks, and defensive copies pile up when each author cannot see what is already guaranteed. The result is noise, root causes hidden behind default values, runtime cost, and often weaker safety than it appears: the one check that matters is lost among many that do not.

The goal is not fewer checks. It is **each fact established once, in the right place, and trusted after that**.

## Questions for each check

1. **What fact does it assert?** Non-null, in range, well-formed, authorized, unique, initialized, not yet disposed, and so on.
2. **Where does the value come from?** Trace it back to its origin.
3. **Who establishes the fact, if anyone?** A parser, a constructor, schema validation, a database constraint, the type system, the framework.
4. **Is the fact preserved from there to here?** Things that break it:
   - mutation after it was established, especially of shared mutable state;
   - concurrency: check-then-act races, state changed by another thread or task;
   - deserialization, reflection, or ORM hydration that bypasses constructors;
   - crossing a process, network, FFI, plugin, or callback boundary;
   - configuration reloaded at runtime;
   - time: expiry, or filesystem state checked and then used.
5. **What happens if it is violated and the check is gone?** A clear failure right here is cheap. Silent corruption, a security hole, data loss, resource exhaustion, or a confusing failure far away is expensive.
6. **Does a downstream operation already handle it in a controlled way?** A bounds-checked access with a clear error, a database constraint, framework validation.
7. **What does it cost?** How often it runs, what it allocates (exceptions, messages, copies), whether it sits on a hot path.

Types are evidence, not proof. Many languages erase or do not enforce them (TypeScript at runtime, Python hints, Java nullability), and data from outside the type system can violate them. Inside strictly type-checked code that only receives values from other typed code, a non-nullable parameter is strong evidence.

## Boundaries

Facts are established where data enters: a public library API; HTTP, RPC, CLI, and message handlers; parsing of files, configuration, environment, database rows, and network responses; IPC and FFI; plugin and callback boundaries; deserialization; user-supplied code. Treat this as a starting list. Identify the project's actual boundaries during the campaign, and record them in the ledger.

A common finding is interior code full of checks because the boundary validates too little. The fix is to strengthen the boundary, then remove the interior checks it makes redundant.

## Verdicts

| Verdict | When |
|---|---|
| delete | The fact is established upstream and preserved; a violation could only come from our own bug, and it would fail clearly nearby anyway. You must be able to name the establisher. |
| hoist | The same check repeats across layers. Keep one, at the boundary where the value enters. |
| encode in a type | The same fact is checked in many places. Parse once into a type that can only hold valid values, accept that type internally, and the checks disappear by construction ("parse, don't validate"). |
| strengthen the boundary | Interior checks exist because the real boundary does not validate. Move the protection there, then delete the interior copies. |
| make it cheap | A necessary guard on a hot path: keep the success path to a primitive branch, move exception and message construction to a cold path, validate once per batch instead of per element. |
| keep | It guards a real boundary, or something on the path breaks the fact. If that is not obvious from context, name the boundary in a short comment. |

If you cannot name the establisher, do not delete. Hoist, encode in a type, or keep.

## Error handling

- **Catch and return a default, or log and continue**: hides the root cause and turns a clear failure into a wrong value discovered much later. Keep it only when failure is a normal business outcome with a defined caller response, and then make it explicit (a typed result, an Optional, a documented return value). Otherwise let it propagate to the layer that can actually handle it, such as the request, job, or UI-event boundary, and translate it once there.
- **Broad catches** (`catch (Exception)`, `except Exception`, empty catch blocks) also swallow programming errors. Catch what you can name.
- **Catching what you cannot explain**: if you cannot say when the exception is thrown, you cannot handle it correctly.
- **Retries**: only for transient failures of idempotent operations, with one owner of the policy. Retries at several layers multiply: three layers of three attempts is twenty-seven calls.
- **Fallbacks**: must be semantically equivalent, or visible to the caller. A silent switch to different data, a different implementation, or a default configuration is a bug carrier.
- **Workarounds for third-party defects**: keep, with a note naming the library, version, condition, and when it can be removed, but only facts you have verified. An invented issue number is worse than no note.

## Defensive copies and repeated null handling

- Copying collections or objects on the way in and out "for safety" is needed only when data is shared, mutable, and of unclear ownership. Fix the ownership instead: immutable types, read-only views, explicit transfer.
- The same value null-checked at every hop: establish it once at the boundary (optional or nullable there, non-null after) and remove the rest.

## Before deleting a check

- Search every caller, including dynamic, reflective, serialized, and configuration-driven entry points.
- Read the history of the check (`git log -L`, blame, linked issues). A guard added right after an incident usually encodes a real failure, possibly at the wrong layer; move it rather than drop it.
- Make sure a test or a type would still catch the violation where the fact is established.

## Finding candidates cheaply

Search first, read second. Count matches per file or module, look where the density is highest, and classify with the questions above. These patterns are starting points; adapt them to the project's style.

```bash
# Java / Kotlin
rg -c -t java -t kotlin 'Objects\.requireNonNull|Preconditions\.check|checkNotNull|requireNotNull' --glob '!**/test/**'
rg -U -t java -t kotlin 'catch \([^)]*\) \{\s*(return (null|false|Optional\.empty\(\))|log)' --glob '!**/test/**'

# TypeScript / JavaScript
rg -c -t ts -t js 'if \(!\w+\) (throw|return)' --glob '!**/*.test.*'
rg -U -t ts -t js 'catch( \(\w+\))? \{\s*(return|console\.)' --glob '!**/*.test.*'

# Python
rg -c -t py 'if \w+ is None:|isinstance\(' --glob '!**/test*'
rg -U -t py 'except( [\w.]+)?( as \w+)?:\s*(pass|return None|log)'

# Go
rg -U -t go 'if err != nil \{\s*return [^\n]*nil\s*\}' --glob '!**/*_test.go'
rg -t go '_ = \w+[.(]' --glob '!**/*_test.go'

# C#
rg -c -t csharp 'ArgumentNullException\.ThrowIfNull|\?\? throw' --glob '!**/*Tests*/**'

# Rust
rg -c -t rust '\.unwrap_or_default\(\)|\.ok\(\);|let _ = ' --glob '!**/tests/**'
```

Density alone decides nothing. A parsing module is supposed to be full of checks.
