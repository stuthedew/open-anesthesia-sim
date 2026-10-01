---
id: PL-JLBD
title: PL-MT3R is done and bin/docket generators lists it drained, yet its front matter still carries generator: live and docket check is silent, so the field and the register disagree about one head while the pause rule reads only open items
priority: P3
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py, docs/items
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: a closed head's record and the generator register agree, so whether the pause binds is read from the store rather than measured
verify: grep -q 'def test_a_closed_head_cannot_stay_live' subprojects/docket/tests/test_checks.py
---

**Problem.** PL-MT3R is done and bin/docket generators lists it drained, yet its front matter still carries generator: live and docket check is silent, so the field and the register disagree about one head while the pause rule reads only open items

**Recorded alternative, from the 2026-10-01 survey.** Either the close-out writes `generator: spent - <why>` on a drained head, or `docket check` refuses `generator: live` on a closed item; which is the triage question. Found 2026-10-01 while measuring whether the generator pause still binds: it does not, since no open item carries the field.

**Why it matters.** `bin/docket generators` lists `PL-MT3R` drained while its front matter says live, so the one record of a head's mechanism and the register built from it disagree, and a reader believes whichever it opens first. Today it mis-ranks nothing - `plan.py` and the pause rule read open items only - but a reader of the file, the session that filed this included, had to measure whether the pause still bound rather than read it, and nothing refuses the next one.

**Reproduced 2026-10-01.** `docs/items/PL-MT3R-*.md` carries `status: done` beside `generator: live - five readers ...`; `bin/docket check` exits 0 and names `PL-MT3R` nowhere; `_check_generator_verdicts` (`subprojects/docket/src/docket/checks.py:2335`) holds the field to its vocabulary and a reason, never to the item's status.

**Done when.** `docket check` errors on a closed item whose `generator:` reads live - closed, its mechanism can hand it no member it would record, so the verdict is `spent - <why>` or the item is reopened - and `PL-MT3R`'s line is rewritten spent with the register's reason. Decided at triage, 2026-10-01, over the close-out writing spent itself: a hard rule on a decidable fact, where the close-out's write would have scripted the reason.

**Generator check.** A one-off, bookkeeping. No head's `misread:` states what a head records about itself; `PL-Q4DF`'s fact is the ranking, which this does not touch. Work on what a head records, which the pause exempts (`PL-5MYR`).
