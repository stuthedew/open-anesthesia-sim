---
id: PL-YRYR
title: test_cli.py and test_verify.py spend ~50s of the suite's 272s serial cost on per-test git fixtures - 304 tests, no test above 1.3s, a git init plus config plus add plus commit in each
status: untriaged
feature: verify-replay-cost
added: 2026-09-19
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

**Done when** the two files' serial cost is materially down with every test
still running against a tree no other test has touched, or the item records
that the sharing cannot be made safe.
