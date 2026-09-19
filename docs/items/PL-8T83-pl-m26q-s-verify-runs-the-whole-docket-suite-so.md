---
id: PL-8T83
title: PL-M26Q's verify: runs the whole docket suite, so any change under subprojects/docket/tests now puts a 62.6s command into the scoped pull-request replay
priority: P3
effort: S
status: done
classes: perf, infra
feature: verify-replay-cost
milestone: v0.4.28
touches: docs/items
added: 2026-09-17
closed: 2026-09-19
pr: 699
verify: grep -q '^verify: grep' docs/items/PL-M26Q-bin-docket-gate-prints-no-product-workflow-lane.md
---

**Problem.** PL-M26Q's verify: runs the whole docket suite, so any change under subprojects/docket/tests now puts a 62.6s command into the scoped pull-request replay

**Where it comes from.** `PL-XMNC` widened the pull-request replay's scope from
the items a branch edited to those plus the open items whose `verify:` command
reads a file it changed. `PL-M26Q`'s command is `uv run pytest -q
subprojects/docket/tests && grep -rq 'def test_gate_reports_lanes'
subprojects/docket/tests`, which names the directory, so *any* change under
`subprojects/docket/tests/` now pulls it in.

**Measured 2026-09-17** on `claude/kind-bardeen-11q5uh`, which edited
`test_verify.py` and `test_cli.py`: the scoped replay ran 29 commands in 92.5 s
wall (535.6 s serially), and `PL-M26Q` alone was 62.6 s of that. A pool cannot
finish before its slowest member, so that one command sets the floor for every
apparatus branch that touches a docket test file — which is most of them.

**The repair is the one the project already prescribes** for a `verify:` that
runs a whole suite: pair the file's own suite with a `grep` for the test the
work adds, rather than running the lot. The `grep -rq` half already names a
single test, so the pytest half is what wants narrowing to the file that test
lives in.

**Why it matters.** A pool cannot finish before its slowest member, so this one
command sets the floor for the scoped replay on every apparatus branch that
touches a docket test file - which is most of them. Nothing reports it: the
answer is right, the slow-command advisory is silent for the reason `PL-G6J5`
diagnoses, and the cost is simply paid on each run.

**The prescribed repair changed after this was filed, and the brief above is
stale on it (2026-09-19).** The paragraph above says to pair the file's own
suite with a `grep`. That paired shape was retired the same week: `PL-6TP8`
ratified that a `verify:` records the discriminator alone, because a
prerequisite clause proved nothing and was 99.7% of the replay's serial cost.
So the repair here is to delete the `uv run pytest -q subprojects/docket/tests`
clause outright rather than narrow it, leaving the `grep` for
`def test_gate_reports_lanes` and pointing it at the file that test lives in.
Read "runs a named test file" in the **Done when** below as "carries no
suite-running clause at all".

**Not urgent, and not a correctness problem.** Nothing is wrong with the answer;
the command is simply the most expensive one in the store and is now in scope
far more often than it was.

**Done when** `PL-M26Q`'s `verify:` runs a named test file rather than the whole
docket suite, having been run and seen to fail first.


**Done 2026-09-19.** `PL-M26Q`'s command is now `grep -rq 'def
test_gate_reports_lanes' subprojects/docket/tests` - the discriminator that was
already there, with the `uv run pytest -q subprojects/docket/tests` clause
removed. Measured at **2 ms, exit 1** on this checkout, against the 62.6 s it
replaced.

What that returns is the scoped replay's floor rather than 62.6 s of its
serial time: a pool cannot finish before its slowest member, and this command
was pulled into the scope of *any* branch touching a docket test file. On the
2026-09-17 measurement the pool was 29 commands in 92.5 s wall against 535.6 s
serial, so removing its slowest member is the difference between a 92.5 s floor
and one set by whatever is next.

The stale repair paragraph above is left as written rather than edited, per the
same reading that `PL-6TP8`'s brief records: what was prescribed when the item
was filed is part of why it says what it says.
