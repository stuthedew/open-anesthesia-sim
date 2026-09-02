---
id: PL-LXR3
title: bin/docket check runs every open item's verify command serially on every make check, costing 50 s and growing with the queue
priority: P2
effort: S
status: done
classes: perf, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_verify.py
added: 2026-09-02
closed: 2026-09-02
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -rq 'def test_verify_commands_run_concurrently' subprojects/docket/tests
---

**Problem.** `bin/docket check` executes the `verify:` command of every open
item that has one, serially, and `make check` runs it. Measured 2026-09-02 on
this checkout: **49.6 s** for the `check` step alone, across 48 commands. Some
of those commands are whole `pytest` runs and one class of them is a
`--cov` run over the full suite, so the cost is dominated by a handful of
entries and the rest is process startup.

**Why it matters, and the arithmetic.** This is paid by every `make check`, and
`make check` runs at least once before any session finishes and usually two or
three times while iterating. At two runs a session that is ~100 s a session, and
it scales with the queue: every item triaged to `ready` adds its command's
runtime permanently. The store holds 93 open items today against 48 commands
run, so the number grows as the older command-less items are given commands —
i.e. it gets worse exactly as the store gets healthier. Ninety-three open items
at two runs each is on the order of an hour of wall clock spent re-proving
commands whose answers did not change.

Two of the three advisories the run produces are already scoped to "the items
`next` is about to offer", so most of the 48 executions produce a result that
is reported for at most one advisory and otherwise discarded.

**Where.** `subprojects/docket/src/docket/verify.py` and whatever `checks.py`
calls to collect the already-passes set.

**Approach.** Three candidates, cheapest first; the implementing session should
measure before choosing.

- **Run them concurrently.** A thread pool over independent subprocesses. The
  simplest change and probably the largest single win, since the cost is
  wall-clock-bound rather than CPU-bound.
- **Cache by tree state.** Key a command's result on the hash of the working
  tree (or of the paths its item `touches`) and skip re-running an unchanged
  one. Correct, but a stale-cache bug here would report an item done that is
  not, which is the failure mode this check exists to prevent.
- **Run fewer.** The already-passes advisory is the only consumer that needs
  all of them; scope it the way the other two are scoped, to the items `next`
  will offer, and the run drops to a handful. Cheapest, at the cost of finding
  a landed-but-unclosed item later than today.

Concurrency and the third are compatible and neither risks a wrong answer.

**Found.** 2026-09-02, while cutting v0.2.9, after narrowing two newly written
`verify:` commands from the whole `docket` suite to one test file each saved
~37 s of the measured 49.6 s. That the fix for two items moved the number that
much is itself the argument that the total is not being watched.

**Done when.** `bin/docket check` on a store of this size completes in a few
seconds rather than tens, the reduction is measured and recorded in the item,
and no command's result is reported as passing without having been run against
the current tree.

**Approach decided 2026-09-02, at triage.** Concurrency, the first of the
three candidates above. It is the only one that changes no answer - every
command still runs against the current tree, so nothing can report a passing
item that is not - and the cost is wall-clock rather than CPU, so a thread
pool over the subprocesses is where the win is. "Run fewer" stays available
and compatible if the measurement afterwards says concurrency alone is not
enough; caching stays rejected while a cheaper option remains, because a stale
cache here reports an item done that is not, which is the one failure this
check exists to prevent.

The `verify:` command pairs `test_checks.py` rather than `test_verify.py`
deliberately: the latter is itself 9.5 s, which this item exists to stop
paying in every `make check`, and pinning it here would add that cost to every
run until the work lands. `test_checks.py` is 0.7 s and covers the caller that
collects the results; the recursive `grep` names the test the work owes
wherever it comes to live.

**Worked.** A thread pool over the candidate subprocesses in
`already_passing`, which is where `make check` pays. Measured on this
checkout, 48 candidate commands, four cores, the same tree before and after:

| | `bin/docket check` |
| --- | --- |
| Serial | **34.9 s** |
| Concurrent | **10.1 s** |

The two runs' output is byte-identical, which is the property that made
concurrency the right candidate: every command still runs, in the working
tree, against the current state, so the answer cannot move - only the wall
clock. Command execution alone was 33.9 s of the serial total across 49
candidates on the pre-restart store, 10.8 s at four workers and 10.1 s at
eight, so the knee is the core count and the pool doubles it to overlap the
interpreter startup that dominates the small commands. `landed_workers()`
carries that measurement and caps at eight.

The saving grows rather than holding: the serial number is the sum of the
commands, so every item triaged to `ready` adds its own runtime permanently,
while the concurrent number rises at roughly a quarter of that rate. Of the
33.9 s, four commands were 19.1 s and the other 45 were 14.8 s of `uv run`
plus collection startup - so the tail that grows with the queue is exactly
the part concurrency removes.

Two things were added beyond running them at once, both to keep the answer
identical rather than merely fast. `ThreadPoolExecutor.map` yields in the
order it was given, so the findings still follow the store's order rather
than whichever shell finished first - otherwise an unchanged store would
print a differently-ordered advisory each run. And each child gets its own
`COVERAGE_FILE`: coverage reads its data file back to decide
`--cov-fail-under`, so two `--cov` commands sharing the tree's default
`.coverage` could race and one fail on data the other truncated, which would
be a wrong answer introduced by this change. No open item carries a `--cov`
command today; eight closed ones do, so the guard is for the next one rather
than for a live fault.

Neither of the other two candidates was taken. "Run fewer" would drop the
already-passes advisory, which names nine real candidates on this store for
work that landed while its item stayed `ready`; caching stays rejected while
a cheaper option exists, because a stale cache reports an item done that is
not.
