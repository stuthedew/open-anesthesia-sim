---
id: PL-XNF3
title: An item whose remaining work waits on a date has no field to say so: PL-R4Y2's re-measurement is due 2026-11-02, but show and next offer it as ready, so a session named to it on 2026-10-27 found nothing due but an interim reading
priority: P2
effort: S
status: done
classes: defect
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/README.md, subprojects/docket/tests/test_model.py, subprojects/docket/tests/test_checks.py, subprojects/docket/tests/test_plan.py, subprojects/docket/tests/test_roadmap.py, .claude/skills/docket/modes/triage.md, docs/items/PL-R4Y2-simulator-defects-per-product-item-closed-have.md
deferred-from: v0.7.0 - captured after the freeze; a queue-state defect in the workflow lane, not safety or science
added: 2026-10-27
closed: 2026-11-01
pr: 1904
payoff: an item whose remaining work waits on a date is not offered as work before that date, and the queue says when it becomes due
verify: grep -q 'def test_an_item_waiting_on_a_date_is_not_startable' subprojects/docket/tests/test_model.py
reenters: PL-RJLQ
---

**Problem.** An item whose remaining work waits on a date has no field to say so: PL-R4Y2's re-measurement is due 2026-11-02, but show and next offer it as ready, so a session named to it on 2026-10-27 found nothing due but an interim reading

**Checked 2026-10-31.** `Item.is_startable` in `subprojects/docket/src/docket/model.py` reads only the status, triage state and `blocked`. `blocked-by` takes an item or a roadmap version, not a date. `PL-R4Y2`'s brief says its re-measurement is due 2026-11-02, and `bin/docket show PL-R4Y2` reports it as `ready`. `PL-RB9W`, now closed, carried its own date in its title for the same reason.

**Why it matters.** `bin/docket next` and `show` offer such an item as work that can start now. A session named to it spends its opening on an item with nothing due. When the date does pass, nothing in the queue says the item has become due.

**Done when.** An item can record the date before which its remaining work cannot start. `Item.is_startable` reads that date, so `next`, `show` and `status` do not offer the item before the date. `bin/docket check` says when the date has passed, as it already does for an item whose blockers have all closed. A test pins both sides of the date.

**Generator check.** An instance of `PL-RJLQ`'s fact, filed after that head closed: an item's current queue state, meaning its status, what blocks it and what it must land after. A date is a blocker that nobody records, so `Item.is_startable` cannot read it.

**Built, 2026-11-01.** The date is a third kind of `blocked-by` entry, written `YYYY-MM-DD`, beside the item ids and milestone versions the field already takes. No new field was added. An item waiting on a date sits at `blocked`. `Item.is_startable` already refuses `blocked`, so `next`, `show` and `status` do not offer the item, and the model needs no clock. `docket check` is the one reader given the day. It refuses `ready` while the date is still to come, and from the date itself it advises that the item is ready to promote once every other blocker has cleared. The brief asked for `Item.is_startable` to read the date. That was not done, because the property would then need a day passed to it at every one of its callers, and the status already carries the answer. A date arrives with no closure, so it is advice, as a scoped milestone is, and `plan.promotable` never returns an item naming one. `show` prints `waits until:`, a gate counts a date apart from its open items, and an entry shaped like a date that is not one is an error. `PL-R4Y2` is the first use, at `blocked` with `blocked-by: 2026-11-02`.
