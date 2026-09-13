---
id: PL-JSRH
title: A closed item's closed: and milestone: are records too, and nothing stops a branch rewriting either
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-05
closed: 2026-09-13
pr: 504
verify: uv run pytest subprojects/docket/tests/test_checks.py && grep -q 'def test_rewriting_a_landed_closed_date_is_reported' subprojects/docket/tests/test_checks.py
---

**Problem.** `PL-JZ1D` established that a closed item's `verify:` is the record
of what proved it, and `checks._check_records` now errors where a branch
rewrites one. The same argument covers two fields beside it and neither is
guarded. `closed:` is when the work landed and `milestone:` is which release
shipped it; both are read by `docket release`, `wave` and `gate`, and both are
silently rewritable by any branch long after the merge. `pr:` is the third and
is already covered from the other side - `docket record` refuses to overwrite a
different number - which is what makes the gap in the other two visible.

**Why it matters.** A rewritten `milestone:` moves an item between releases, so
the notes for two of them are wrong and nothing says so. A rewritten `closed:`
moves it across a debt-gate freeze. Both are the failure `CLAUDE.md` names for
tooling: a record that looks authoritative and is not, reached from a true one
rather than an absent one.

**Approach.** `records_on_base` already reads the whole base item and returns
only its `verify:`; widening `BaseRecord` to carry `closed` and `milestone` is
the read. The judgment half is not identical to `verify:`'s and is the work
here: correcting a mistyped `closed:` date is a legitimate repair in a way
re-pointing a command is not, so this may want an advisory where `verify:`
takes an error. Decide that before writing the check.

**Done when.** A branch that rewrites a landed item's `closed:` or `milestone:`
is told so by `docket check`, at whichever severity the question above settles
on, with a test for each field.

**Decided while closing, 2026-09-13: `milestone:` errors, `closed:` is an
advisory.** The item's **Approach** left this open and it is the whole judgment
half. `docket release` writes `milestone:`, so no hand-edit of it is a repair and
the rule is exact - a rewritten value makes the notes for the release it left and
the release it joined both wrong, with nothing else reporting it. `closed:` is a
date a human typed, and correcting a mistyped one is a legitimate repair, so the
reader is told what changed and decides rather than being refused. That is
`CLAUDE.md`'s own split: hard failure for exact rules, an advisory for a signal
needing context.
