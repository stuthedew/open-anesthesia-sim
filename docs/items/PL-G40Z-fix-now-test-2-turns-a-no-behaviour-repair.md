---
id: PL-G40Z
title: Fix-now test 2 turns a no-behaviour repair outside the finder's touches into an item: eleven items filed 09-20 to 09-22 are repairs citation-drift.md says need none, because that licence loads only after the decision to file
priority: P2
effort: S
status: done
classes: planning, docs
feature: generator-identification
touches: CLAUDE.md, .claude/rules/citation-drift.md
added: 2026-09-22
closed: 2026-09-22
payoff: a one-line repair to another item's brief rides the current commit instead of becoming an item to triage, rank and work
verify: grep -qF 'is not a fix-now use at all' CLAUDE.md
---

**Problem.** Fix-now test 2 bars edits outside the current item's `touches`, so
a no-behaviour repair to another item's brief or to `docs/WORKING_NOTES.md` got
filed as an item instead. Eleven items filed 2026-09-20 to 09-22 were such
repairs, among them `PL-2J5X`, `PL-X4RX`, `PL-RL8S`, `PL-LDHD`, `PL-TJTV` and
`PL-L1D3` (`PL-KVDK`'s first pass). `.claude/rules/citation-drift.md` already
licensed repairing drift in place, but it is path-scoped, so it loads only after
a session has decided to file. It also claimed that `bin/docket verify --self`
expects such edits, which is false: `verify.sanctioned_queue_edit` sanctions only
capture, `pr:` and recurrence edits.

**Decision.** The project owner agreed with the recommendation on 2026-09-22
(ratified, chosen over leaving the licence in the path-scoped rule).
`CLAUDE.md`'s fix-now test 2 now says that such a repair is not a fix-now use:
the file is declared in the current item's `touches`, and the repair rides the
current commit without counting against the cap. `citation-drift.md` now carries
the corrected verify claim.

**Why it matters.** Each such repair became an item that had to be triaged,
ranked and worked, and it was one of the recurring sources of workflow inflow.

**Done when.** `CLAUDE.md` states the licence where fix-now is read.
