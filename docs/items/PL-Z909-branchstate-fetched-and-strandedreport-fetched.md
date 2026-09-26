---
id: PL-Z909
title: BranchState.fetched and StrandedReport.fetched duplicate Snapshot.fresh now that cli sets both from the one snapshot (PL-XBV4); retire the two fields or derive them, so a report cannot carry a freshness the snapshot disagrees with
priority: P3
effort: S
status: ready
classes: refactor
feature: one-snapshot
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_vcs.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-26 triage pass
added: 2026-09-26
payoff: freshness is carried by one field, Snapshot.fresh, so no report can say its refs are this command's own fetch when the snapshot says they are not
verify: ! grep -qF 'fetched: bool = False' subprojects/docket/src/docket/vcs.py
---

**Problem.** BranchState.fetched and StrandedReport.fetched duplicate Snapshot.fresh now that cli sets both from the one snapshot (PL-XBV4); retire the two fields or derive them, so a report cannot carry a freshness the snapshot disagrees with

Measured 2026-09-26 against `origin/main` (`17c9f3ed`): nothing under
`subprojects/docket/src/` reads either field. `cli._stranded` sets
`StrandedReport.fetched` from `_snapshot(args).fresh`. `vcs.snapshot` sets
`BranchState.fetched` to `outcome == FETCHED`, which is exactly what
`Snapshot.fresh` returns. The only reads are four assertions in
`subprojects/docket/tests/test_vcs.py`. `stranded()` and `branch_state()` still
take `fetched` as an argument, so a caller can pass its own word for it.

**Why it matters.** Nothing is wrong today. But the next reader of a report's
freshness finds three fields that look authoritative, of which one is, and a new
caller of `stranded()` or `branch_state()` can again state freshness for itself.
That is the digest's wrong `False` that `PL-XBV4` removed.

**Done when.** `BranchState` and `StrandedReport` have no `fetched` field,
`stranded()` and `branch_state()` take no `fetched` argument, and the tests that
asserted either field assert `Snapshot.fresh` instead. The fields are retired
rather than derived, because nothing reads them.

**Generator check.** Bookkeeping left by `PL-XBV4`'s own fix, and filed in its
closing commit (`d2b879ca`, #1054). These fields are the caller's own word for
freshness, which that head replaced with the snapshot. Nothing reads them, so
nothing misreads freshness from them, and this is not that head's fact coming
back.
