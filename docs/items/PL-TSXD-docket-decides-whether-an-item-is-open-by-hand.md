---
id: PL-TSXD
title: docket decides whether an item is open by hand in 19 places (6 write status in OPEN_STATUSES, 13 write status not in CLOSED_STATUSES, which differ for a status in neither set) instead of reading Item.is_open, across checks.py, plan.py, cli.py, model.py, verify.py and three tools
priority: P3
effort: M
status: done
classes: defect
feature: one-source-of-truth
milestone: v0.6.3
touches: subprojects/docket/src/docket/, tools/, subprojects/docket/tests/, tests/unit/test_branch_sweep.py
added: 2026-10-19
closed: 2026-10-24
pr: 1738
payoff: a status added later cannot be open to one docket command and closed to another
verify: ! grep -rqE --include=*.py --exclude=claims.py '[^f]\.status (not )?in (OPEN|CLOSED)_STATUSES' subprojects/docket/src tools
reenters: PL-5DZ8
---

**Problem.** docket decides whether an item is open by hand in 19 places (6 write status in OPEN_STATUSES, 13 write status not in CLOSED_STATUSES, which differ for a status in neither set) instead of reading Item.is_open, across checks.py, plan.py, cli.py, model.py, verify.py and three tools

**Why it matters.** "Is this item open?" has one answer, `Item.is_open`. Code that tests `status in OPEN_STATUSES` and code that tests `status not in CLOSED_STATUSES` agree today only because every status is in one of the two sets. A status added to neither set would be open to one reader and closed to another. A second copy of a predicate breaks a rule this repository states, the one-source-of-truth principle in `CLAUDE.md`. Condition 1 of `CLAUDE.md`'s fix-in-place rule counts a break of a stated rule as a defect, whether or not it gives a wrong answer today, so this is classed `defect` (project owner, 2026-10-24). It does give one on a store that `docket check` refuses: an item with no `status:` line has the empty status, which is in neither set.

**Done when.** Every test of whether an item is open or closed reads an `Item` property: `is_open`, and an `is_closed` if the work needs one. No `<item>.status in` or `not in` `OPEN_STATUSES` or `CLOSED_STATUSES` remains outside `model.py`'s own property in docket or `tools/`. `claims.py` reads a claim's status, not an item's, and is outside this item.

**Checked 2026-10-24.** A grep for `.status in` or `not in` either set finds 44 lines across `subprojects/docket/src/` and `tools/`. The capture counted 19 open tests; the rest are closed tests, which are the same question asked the other way. Two of the 44 are `self.status` inside `model.py` and `vcs.py`, and two are claim holds in `claims.py`.

**Generator check.** A re-entry of `PL-5DZ8`, closed 2026-10-12, at a sibling site. Its misread fact, "which spelling of a repeated predicate is the answer", is the one these sites spell by hand. `tools/fact_home_check.py` refuses a constant defined twice but does not see a predicate written inline. Recorded 2026-10-24 as a member of the head `PL-N4FP`, which names that gap.

**Done 2026-10-24.** `tools/fact_home_check.py`'s new rule found 48 hand
tests of a status set outside `docket/model.py` on the base tree (3f1e5913),
in 13 files. The branch replaced all 48, and the three inside `model.py`
besides:

- 34 tested an `Item` and now read `Item.is_open`, or `not item.is_open`
  for "closed". No `is_closed` property was needed.
- 13 tested a status read as text from a copy at a ref, where the empty string
  means no copy. Those are 5 in `claims.py`, 4 in `vcs.py`, 3 in `cli.py`
  (claim holds and base copies) and 1 in `claiming.py`. They now call the new
  `model.is_closed_status`, which keeps their behaviour. `claims.py` was
  outside this brief, but the check refuses every membership test, so its
  five tests moved too.
- 1 in `checks.py`'s stale-thread advisory now reads the closed set from the
  items.

`Item.is_open` is now `not is_closed_status(self.status)`, so open means "not
recorded closed" and the two predicates cannot disagree. This changes one
thing, and only on a store `docket check` already refuses. An item whose
status is in neither set, such as an empty or misspelt status, used to be
closed to the readers that tested `OPEN_STATUSES` and open to those that
tested `CLOSED_STATUSES`. It is now open to every reader, so every check keeps
holding it to the rules for open work until it is recorded closed. That is the
direction that hides nothing, and it is what `doc_check`'s live-brief test
expects of a brief with no front matter. `Item.is_startable` now also requires
a valid status, so `next` still never offers such an item.

`tests/unit/test_branch_sweep.py` built its items as bare namespaces with a
`status` and no `is_open`, so it now builds them with `parse_item`.
