---
id: PL-XYJF
title: docket's checks._passage starts a passage at a soft-wrapped line opening with 17. or a pipe, which CommonMark keeps in the paragraph above, so _standing, _left_statuses and _ended_waits read a superseded passage as standing and advise on it; latent
priority: P3
effort: S
status: done
classes: defect
feature: one-answer
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/tests, tests/unit
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
closed: 2026-10-04
pr: 1352
payoff: a superseded marker covers its passage as CommonMark ends it, so a withdrawn claim wrapped before a later number or a pipe line draws no advisory
verify: grep -qF '"passage, ' tests/unit/test_doc_check.py
---

**Problem.** docket's checks._passage starts a passage at a soft-wrapped line opening with 17. or a pipe, which CommonMark keeps in the paragraph above, so _standing, _left_statuses and _ended_waits read a superseded passage as standing and advise on it; latent

**Found 2026-10-04 by `PL-R417`'s close-out sweep (`#1349`)**, a read-only pass over every reader outside the 2026-10-04 sweep, which reproduced it by importing the function; CommonMark readings checked with markdown-it-py 4.2.0. On a `ready` item, `[superseded 2026-09-30] ... count at\n17. It is left at "needs-decision" ...` makes the passage start at "17.", so `_standing` returns True and `_left_statuses` emits the brief-status advisory; the same text on one line gives []. An ordered list interrupts a paragraph only when it starts at 1 (CommonMark 0.31.2 § 5.2). Latent: no such split in the 293 open briefs.

**Reproduced 2026-10-04, at triage.** On a `ready` item, a `[superseded 2026-09-30]` paragraph wrapped before a line opening `17. It is left at` a status draws the advisory the marker retires, since `_passage` starts a passage at `17.`; on one line it draws none.

**Why it matters.** A superseded marker exists to retire the advisories on its passage, so a passage ended early leaves a withdrawn claim standing, and the advisory asks a session to answer it again.

**Generator check.** A member of `PL-R417`: the reader takes a physical line for a statement its format continues, the fact that head names.

**Done when.** A passage ends where CommonMark ends its paragraph or list item - an item numbered past 1, and a pipe line over no delimiter row, carry it on - pinned by `passage, ...` cases in `PL-R417`'s guard.

**Built 2026-10-04 (`#1352`).** `_passage` takes its passages from `roadmap.statement_lines` and from each fenced block, so a later number, a pipe line with no delimiter row, a placeholder or a code span carries one on, and an item numbered 1 still opens a claim of its own. `bin/docket check` over the store reports what it did before, 0 errors and 7 advisories. Two guard cases, each failing on main's reader.
