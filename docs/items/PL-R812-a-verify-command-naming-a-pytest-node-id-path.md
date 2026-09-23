---
id: PL-R812
title: A verify: command naming a pytest node id (path::test) exits 4 before the work when the test is new and re-proves make check when it exists, and both the prerequisite rule and PL-Q8RQ's -k rule leave it alone: six commands have used the shape, one still open (PL-ZLNN)
priority: P3
effort: S
status: dropped
classes: defect
feature: verify-command-health
touches: subprojects/docket/src/docket/checks.py
added: 2026-09-22
closed: 2026-09-23
reason: No rule earned: shaped like its sibling rules (open items, from a capture-date cutover) it would have refused none of the seven node-id commands ever recorded - two written 2026-09-02 before either cutover, five in the commits that closed their items - and the one open instance, PL-ZLNN, leads with its grep and loses the trailing clause when started. Recorded as a member of PL-1P5V, whose recommended allowlist refuses the shape by default.
---

**Problem.** A verify: command naming a pytest node id (path::test) exits 4 before the work when the test is new and re-proves make check when it exists, and both the prerequisite rule and PL-Q8RQ's -k rule leave it alone: six commands have used the shape, one still open (PL-ZLNN)

**What the capturing session saw** (`PL-Q8RQ`, 2026-09-22). Over the trees
`collected_test_paths` names, a node id is the `-k` argument without the
substring hazard: it names a test that already exists and passes (exit 0, which
`make check` already proves - `PL-ZLNN`'s shape, ahead of its `grep`), or one the
work will add (exit 4 before the work, a usage error rather than an evaluation;
the `docket` skill's triage table measured it). Neither rule reads it:
`_pytest_targets` returns `None` on any `::`, so `_redundant_pytest_clause`
exempts it, and `_k_selector_clause` reads `-k` alone. Counted on `origin/main`
that day: six `verify:` commands have ever carried a node id - `PL-F5GN`,
`PL-B1WW`, `PL-WXX8`, `PL-ZPDM`, `PL-W7WL` closed, `PL-ZLNN` open. Whether that
is enough recurrence to earn a rule, beside the skill's table that already
names the shape, is triage's call.

**Reproduced 2026-09-23.** Both halves hold on today's tree. `uv run pytest
'tests/reference/test_coupled_dynamics.py::test_no_such_test'` exits 4.
`PL-ZLNN`'s node id, `::test_lockstep_oracle_step_matches_the_pinned_one`,
exits 0 in 0.11 s. Fed a node id through the store's own config, ahead of a
`grep` or behind one, `_redundant_pytest_clause` and `_k_selector_clause` both
return `None`, while the same file path without `::` is caught by the first.
The count is **seven** commands, not six: `PL-SZJ2` (closed 2026-09-22) carries
one too. `PL-4MHK` and `PL-NDKC` have `::` inside a `grep` string, not a node
id.

**Why it matters.** Less than the shape suggests. Before the work its 4 reads
like a typo'd path, and after it the command re-proves what `make check`
proves. No instance has been recorded as costing anything.

**Generator check.** Member of `PL-1P5V` (`verify:` is an opaque shell string,
so each way it fails to discriminate gets its own rule after it fails). It was
filed after `PL-6TP8` closed and is recorded there.

**Dropped 2026-09-23: no rule earned, and the head's fix covers it.** Its
sibling rules read open items only, from a capture-date cutover. A rule shaped
like them would have refused **none** of the seven. `git log -G
'^verify:.*pytest[^|]*::' -- docs/items` shows two written onto open items on
2026-09-02, before either cutover (`PL-F5GN`, `PL-ZLNN`). The other five were
written in the commits that closed their items (`PL-B1WW` 09-07, `PL-W7WL` and
`PL-WXX8` 09-20, `PL-ZPDM` 09-21, `PL-SZJ2` 09-22), where every shape rule
stands aside because a closed command is a record.

The one open instance, `PL-ZLNN`, has led with its `grep` since `#920`. It
fails with an ordinary 1 before the work, and its trailing clause is removed
when that item starts.

The rule would also be a new check, one more entry in the list of refused
shapes that `PL-1P5V` exists to end; the allowlist recommended there refuses a
node id by default. Keeping this item open for `PL-ZLNN` buys nothing that
item's own start does not.
