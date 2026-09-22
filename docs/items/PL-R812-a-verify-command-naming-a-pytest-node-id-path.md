---
id: PL-R812
title: A verify: command naming a pytest node id (path::test) exits 4 before the work when the test is new and re-proves make check when it exists, and both the prerequisite rule and PL-Q8RQ's -k rule leave it alone: six commands have used the shape, one still open (PL-ZLNN)
status: untriaged
feature: verify-command-health
added: 2026-09-22
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
