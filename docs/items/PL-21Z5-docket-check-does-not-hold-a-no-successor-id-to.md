---
id: PL-21Z5
title: docket check does not hold a no-successor: id to an item: an id naming no item, the item itself, or a closed item that is not done is accepted with 0 errors, so a typo either answers nothing or answers the wrong re-entered line (found reviewing PL-C4F0)
priority: P3
effort: S
status: done
classes: defect
feature: generator-heads
milestone: v0.5.33
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/model.py, subprojects/docket/tests/test_checks.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-18 triage pass
added: 2026-10-18
closed: 2026-10-19
pr: 1620
payoff: docket check refuses a no-successor: id that names no item, the item itself, or a closed item that is not done
verify: grep -q 'def test_a_no_successor_id_that_answers_nothing_is_refused' subprojects/docket/tests/test_checks.py
---

**Problem.** docket check does not hold a no-successor: id to an item: an id naming no item, the item itself, or a closed item that is not done is accepted with 0 errors, so a typo either answers nothing or answers the wrong re-entered line (found reviewing PL-C4F0)

Found by the review of `PL-C4F0` on 2026-10-18. `checks.py` holds `reenters:`
ids through `model.reentry_faults`, and nothing does the same for
`no-successor:`. Reproduced: `no-successor: PL-NOPE, PL-V9L3, PL-4097` on an
item passes `bin/docket check` with 0 errors. Left out of `PL-C4F0` because
`checks.py` was declared by another thread's open work that day.

**Why it matters.** A `no-successor:` id takes a re-entered line off
`bin/docket inflow`'s unanswered list. A typo there either answers nothing, so
the line stays listed and the answer looks lost, or answers a different line,
which then reads as decided when nobody decided it. `docket check` is the only
place a mistyped id would be caught before a session trusts the listing.

**Done when.** `docket check` reports an error for a `no-successor:` id that
names no item, names the item itself, or names an item closed as anything other
than `done`. A test in `subprojects/docket/tests/test_checks.py` pins each case.

**Generator check.** Not an instance of a closed head's fact. `reenters:` ids
are already checked through `model.reentry_faults`; this is the same check
missing on a field added on 2026-10-18 (`PL-C4F0`), so the fix should reuse
that function rather than write a second id check.

**Done 2026-10-19.** `model.no_successor_faults` holds each `no-successor:` id
to another `done` item, through `_done_item_faults`, the id check it now
shares with `reentry_faults`. `checks._check_reentries` reports both fields.
It also refuses an id naming an open item, which the Done-when did not list:
a re-entered line is a `done` item that `reenters:` ids named, so an open item
cannot be one. `test_a_no_successor_id_that_answers_nothing_is_refused` pins
the four cases, and the real store passes `bin/docket check` unchanged.

