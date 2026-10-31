---
id: PL-XNF3
title: An item whose remaining work waits on a date has no field to say so: PL-R4Y2's re-measurement is due 2026-11-02, but show and next offer it as ready, so a session named to it on 2026-10-27 found nothing due but an interim reading
priority: P2
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/model.py, subprojects/docket/README.md, subprojects/docket/tests/test_model.py
deferred-from: v0.7.0 - captured after the freeze; a queue-state defect in the workflow lane, not safety or science
added: 2026-10-27
payoff: an item whose remaining work waits on a date is not offered as work before that date, and the queue says when it becomes due
verify: grep -q 'def test_an_item_waiting_on_a_date_is_not_startable' subprojects/docket/tests/test_model.py
reenters: PL-RJLQ
---

**Problem.** An item whose remaining work waits on a date has no field to say so: PL-R4Y2's re-measurement is due 2026-11-02, but show and next offer it as ready, so a session named to it on 2026-10-27 found nothing due but an interim reading

**Checked 2026-10-31.** `Item.is_startable` in `subprojects/docket/src/docket/model.py` reads only the status, triage state and `blocked`. `blocked-by` takes an item or a roadmap version, not a date. `PL-R4Y2`'s brief says its re-measurement is due 2026-11-02, and `bin/docket show PL-R4Y2` reports it as `ready`. `PL-RB9W`, now closed, carried its own date in its title for the same reason.

**Why it matters.** `bin/docket next` and `show` offer such an item as work that can start now. A session named to it spends its opening on an item with nothing due. When the date does pass, nothing in the queue says the item has become due.

**Done when.** An item can record the date before which its remaining work cannot start. `Item.is_startable` reads that date, so `next`, `show` and `status` do not offer the item before the date. `bin/docket check` says when the date has passed, as it already does for an item whose blockers have all closed. A test pins both sides of the date.

**Generator check.** An instance of `PL-RJLQ`'s fact, filed after that head closed: an item's current queue state, meaning its status, what blocks it and what it must land after. A date is a blocker that nobody records, so `Item.is_startable` cannot read it.
