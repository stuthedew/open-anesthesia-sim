---
id: PL-SV0D
title: bin/docket new recorded PL-DHGC as a recurrence of PL-JLBD on 2026-10-01 when the two shared only docs/items, a path every branch that files an item changes, so a capture can be counted toward an unrelated item's recurrences; it was withdrawn by hand
priority: P2
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/duplicates.py, subprojects/docket/tests/test_duplicates.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-01 triage pass
added: 2026-10-01
payoff: a recurrence on a head means the same mechanism came back, never that two captures both live in docs/items
verify: grep -q 'def test_sharing_only_the_item_store_is_not_a_recurrence' subprojects/docket/tests/test_duplicates.py
---

**Problem.** bin/docket new recorded PL-DHGC as a recurrence of PL-JLBD on 2026-10-01 when the two shared only docs/items, a path every branch that files an item changes, so a capture can be counted toward an unrelated item's recurrences; it was withdrawn by hand

**Why it matters.** A recurrence counts toward a head's post-close instances, which triage reads as a fix that did not hold, so a false one can make a spent head look live; and `docs/items` is changed by every branch that files an item, so the false match is open to every capture. 18 of the store's 82 recurrence entries carry `withdrawn` (counted 2026-10-01); how many of those shared only `docs/items` is not counted here.

**Done when.** A capture whose only shared path with an open item is the store directory is not recorded as its recurrence, with a test, and a shared code path still selects as before.

**Reproduced 2026-10-01.** `subprojects/docket/src/docket/duplicates.py` selects on any shared `touches` path and names no exception for the store's own directory.

**Generator check.** The fact is `PL-TZ7T`'s - whether an open item already describes the mechanism a new capture names - filed after that head closed: its matcher reads a shared store path as a shared mechanism. With `PL-TH7P` (2026-08-30) that is two post-close instances, below the three that count as a fix that did not hold.
