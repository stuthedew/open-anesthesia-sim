---
id: PL-YRYR
title: test_cli.py and test_verify.py spend ~50s of the suite's 272s serial cost on per-test git fixtures - 304 tests, no test above 1.3s, a git init plus config plus add plus commit in each
priority: P3
effort: M
status: ready
classes: perf, test
feature: verify-replay-cost
touches: subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_verify.py
added: 2026-09-19
verify: grep -q 'repository_template' subprojects/docket/tests/test_cli.py subprojects/docket/tests/test_verify.py
recurrences: 2026-09-05 PL-W6NY
---

**Problem.** test_cli.py and test_verify.py spend ~50s of the suite's 272s serial cost on per-test git fixtures - 304 tests, no test above 1.3s, a git init plus config plus add plus commit in each

**Where it comes from.** `PL-FZ58` re-measured the whole suite serially on
2026-09-19 (3,180 tests, 272 s accounted). `subprojects/docket/tests/test_verify.py`
is 27.2 s over 121 timed tests and `test_cli.py` 21.2 s over 119, and neither
has an outlier to remove: their slowest single tests are 0.6 s and 1.26 s. The
shape is flat per-test cost, and `user + sys` runs well under wall on both
(13.4 s of 22.6 s, 14.9 s of 28.5 s), which is the signature of waiting on
subprocesses rather than computing. Each test that needs history builds its own
repository — `git init`, two or more `git config`, `git add -A`, `git commit`,
sometimes a tag, a branch and a merge.

**Why it is filed rather than fixed.** It is a real cost and a modest one. The
suite already runs at `-n $(cpu*2) --dist worksteal` and comes in at 77.8 s
wall against 272 s serial on four cores — within 11% of the CPU floor — so
halving these two files buys roughly 6 s of that run. `PL-FZ58` is the item
that went looking for a saving here and concluded the replay's cost was never
where this would help.

**The shape a fix would take**, so a later session does not re-derive it: build
one repository per session in a module-scoped fixture and copy the directory
per test, rather than re-running git. `shutil.copytree` of a small `.git` is
one syscall-bound operation against five to eight process spawns. The tests
that need a *different* history (a squash merge, a rewritten base, a bare
remote) keep building their own; the win is in the majority that need only "a
repository with one commit on it".

**What must not be traded for it.** These are the tests that keep `docket`
correct about refs, and `.claude/rules/apparatus-standard.md` sets the bar at
"its absence would let a real defect through". A shared fixture that leaks
state between tests would do exactly that, silently — so the fix is worth
taking only if each test still gets an independent tree.

**Why it matters, and why it is filed at P3.** The honest case is modest and
the brief above says so: roughly 6 s off a 77.8 s parallel run, on a suite
already within 11% of its CPU floor. What makes it worth recording rather than
dropping is the direction of travel - this is per-test cost rather than an
outlier, so it scales with the number of tests these two files carry, and they
are the files that grow every time `docket` learns something new about refs.
`PL-FZ58` measured the whole suite looking for a saving and concluded the
replay's cost was never here; this is the residue that measurement left, filed
so the next person to go looking does not re-derive it.

The reason it is `perf` and `test` rather than either alone is that the risk
and the reward sit in different places. The reward is wall-clock; the risk is
correctness, because these are the tests that keep `docket` honest about refs
and a fixture leaking state between them would let a real defect through
silently. `.claude/rules/apparatus-standard.md` sets that bar - "its absence
would let a real defect through" - and it is the bar this fix has to clear, not
the stopwatch.

**Done when** the two files' serial cost is materially down with every test
still running against a tree no other test has touched, or the item records
that the sharing cannot be made safe.

**`PL-W6NY` is this same finding and is dropped in its favour** (`PL-JKML`'s
duplicate sweep, 2026-09-20, confirmed on independent refutation). It measured
`test_verify.py`'s `_repo` fixture on 2026-09-05 - 22.5 s for the file, about
12 s of it non-sleep, across what were then 64 call sites and are 113 today -
and filed it as `PL-VJ7W`'s residue. This item reaches the same fixture from
`PL-FZ58`'s whole-suite serial run and additionally carries `test_cli.py`, so
containment runs one way: finishing this leaves nothing of `PL-W6NY` standing,
while finishing `PL-W6NY` would leave `test_cli.py`'s 21.2 s untouched. That
asymmetry is what makes it a drop rather than a grouping.

**Two things from `PL-W6NY` that are carried rather than lost.** Its fallback
is stricter than this item's: where the fixture cannot be made cheaper safely,
`PL-W6NY` requires the negative result to land **as a comment on `_repo` in the
code**, not only in the item - so the next session to open the fixture reads
why it is shaped as it is, rather than re-deriving it. And its framing of the
constraint is the one to keep: the fixture leaks state between tests that
commit into their own repository, so correctness, not speed, sets the ceiling
on any rework.
