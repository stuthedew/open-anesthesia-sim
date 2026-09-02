---
id: PL-LXR3
title: bin/docket check runs every open item's verify command serially on every make check, costing 50 s and growing with the queue
status: untriaged
added: 2026-09-02
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
