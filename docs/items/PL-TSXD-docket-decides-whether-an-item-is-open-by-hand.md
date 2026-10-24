---
id: PL-TSXD
title: docket decides whether an item is open by hand in 19 places (6 write status in OPEN_STATUSES, 13 write status not in CLOSED_STATUSES, which differ for a status in neither set) instead of reading Item.is_open, across checks.py, plan.py, cli.py, model.py, verify.py and three tools
priority: P3
effort: M
status: ready
classes: refactor
feature: one-source-of-truth
touches: subprojects/docket/src/docket/, tools/
added: 2026-10-19
payoff: a status added later cannot be open to one docket command and closed to another
verify: ! grep -rqE --include=*.py --exclude=claims.py '[^f]\.status (not )?in (OPEN|CLOSED)_STATUSES' subprojects/docket/src tools
reenters: PL-5DZ8
---

**Problem.** docket decides whether an item is open by hand in 19 places (6 write status in OPEN_STATUSES, 13 write status not in CLOSED_STATUSES, which differ for a status in neither set) instead of reading Item.is_open, across checks.py, plan.py, cli.py, model.py, verify.py and three tools

**Why it matters.** "Is this item open?" has one answer, `Item.is_open`. Code that tests `status in OPEN_STATUSES` and code that tests `status not in CLOSED_STATUSES` agree today only because every status is in one of the two sets. A status added to neither set would be open to one reader and closed to another. No status of that kind exists today, so this is a refactor rather than a defect.

**Done when.** Every test of whether an item is open or closed reads an `Item` property: `is_open`, and an `is_closed` if the work needs one. No `<item>.status in` or `not in` `OPEN_STATUSES` or `CLOSED_STATUSES` remains outside `model.py`'s own property in docket or `tools/`. `claims.py` reads a claim's status, not an item's, and is outside this item.

**Checked 2026-10-24.** A grep for `.status in` or `not in` either set finds 44 lines across `subprojects/docket/src/` and `tools/`. The capture counted 19 open tests; the rest are closed tests, which are the same question asked the other way. Two of the 44 are `self.status` inside `model.py` and `vcs.py`, and two are claim holds in `claims.py`.

**Generator check.** A re-entry of `PL-5DZ8`, closed 2026-10-12, at a sibling site. Its misread fact, "which spelling of a repeated predicate is the answer", is the one these sites spell by hand. `tools/fact_home_check.py` refuses a constant defined twice but does not see a predicate written inline.
