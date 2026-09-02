---
id: PL-LXR3
title: bin/docket check runs every open item's verify command serially on every make check, costing 50 s and growing with the queue
priority: P2
effort: S
status: ready
classes: perf, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_verify.py
added: 2026-09-02
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

**Measurements taken 2026-09-02 while triaging the same item on a parallel
branch.** They support the decision above rather than reopening it, and three
of them correct or sharpen the brief.

- `bin/docket check`: **39.8 s** over **49** candidate commands, ~0.81 s each.
  The 49.6 s / 48 figure in the brief above was measured the same day; treat
  either as the order of magnitude rather than a fixed number.
- **Nothing in the candidate set runs the full suite today.** The six `--cov`
  full-suite commands (~50 s each) all belong to `done` items, so
  `LANDED_STATUSES` excludes them. The **Problem.** section reads as though
  they are in the run; they are not, and the cost is not dominated by a handful
  of heavy entries.
- The cost is process startup, not test execution: `python3
  tools/doc_check.py check` is 0.20 s, a scoped `uv run pytest <one file>` is
  0.38 s warm. That is what makes a thread pool the right instrument.
- Per-command cost is skewed rather than flat - the slowest in the set is
  `test_verify.py`, measured at 7.5 s here and 9.5 s above. A pool's floor is
  therefore the slowest single command, roughly 8-10 s, not near-zero. Worth
  recording the result against that floor rather than against zero.
- **Deduplicating identical commands is not the win.** Of the 49 candidates 45
  are distinct, and the one repeated command is `python3 tools/doc_check.py
  check` at 0.20 s, so dedup saves about 1 s. Recorded so the implementing
  session does not re-derive it.

**The growth risk is concrete, and larger than "grows with the queue".**
`PL-NC2P` and `PL-YMY7` are open, `ready`, in `core-guard-coverage`, and carry
no command yet. Every coverage item in that feature has taken the shape `uv run
pytest --cov=<module> --cov-fail-under=100`, which is a full-suite run at ~50 s.
Giving those two the same shape takes `bin/docket check` from ~40 s to ~140 s -
one triage pass, a 3.5x regression.

**A constraint the concurrency approach has to meet.** Two `--cov` runs in one
working directory both write `.coverage` and race. None are candidates today,
but the paragraph above puts them there, so the pool needs a per-worker
`COVERAGE_FILE` or a rule that runs `--cov` commands serially. Getting this
wrong makes coverage results wrong rather than slow, which is worse than the
problem being fixed.

**One stale comment to fix on the way past.** `LANDED_TIMEOUT`'s comment in
`subprojects/docket/src/docket/verify.py` records "Measured against this store
on 2026-09-01, the 29 candidate commands took 18s in total and 5.1s at worst".
It is now ~50 commands and ~40 s. That comment is the only record of the number
anyone reading the constant will see, so update it with whatever this item
measures rather than leaving a figure that understates the cost by half.
