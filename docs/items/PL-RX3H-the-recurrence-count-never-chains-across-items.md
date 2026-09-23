---
id: PL-RX3H
title: The recurrence count never chains across items, so one mechanism re-filed as three different items (PL-X9NB on PL-P757, PL-T441 on PL-K5PW, PL-WF3X on PL-T441) is never summed toward the generator tier
priority: P3
effort: M
status: ready
classes: feature
feature: generator-identification
touches: subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/duplicates.py, subprojects/docket/src/docket/plan.py, subprojects/docket/tests/test_duplicates.py
added: 2026-09-22
payoff: a mechanism re-filed at sibling sites is counted as one cluster even after the item it first matched closes, instead of restarting at one filing per item
not-delegable: its first step re-runs the chain count, and that count decides between building the chaining and dropping the item with the count recorded; no command can prove an outcome the count has not chosen yet
---

**Problem.** The recurrence count never chains across items, so one mechanism re-filed as three different items (PL-X9NB on PL-P757, PL-T441 on PL-K5PW, PL-WF3X on PL-T441) is never summed toward the generator tier

**Reproduced 2026-09-23.** Read through `model.recurrence_count`, each of
`PL-P757`, `PL-K5PW` and `PL-T441` holds one recurrence: `PL-X9NB`, `PL-T441`
and `PL-WF3X` respectively. That is below `MIN_RECURRENCES` of two, so none was
ever named as a promotion candidate. `PL-K5PW` ← `PL-T441` ← `PL-WF3X` is the
only chain among the 30 items that carry recurrences. Chaining would gather two
of the title's three filings, not all three. `PL-X9NB` on `PL-P757` shares no
recurrence edge with the other two, and only `PL-NGBM`'s hand-written
`root-cause-of:` joins them (`spent`, closed 2026-09-23). The split happened
because `duplicates.near_duplicates` drops closed items. `PL-K5PW` had already
closed when `PL-WF3X` was filed, so `duplicates.anchor` could only attach the
new filing to `PL-T441`.

**Why it matters.** `anchor` exists because a cluster whose evidence is split
across items is a cluster nothing surfaces. Its shortlist cannot follow a
mechanism past the item it anchored on once that item closes. A mechanism
re-filed at sibling sites is then counted one filing at a time, and only a
session reading the briefs adds it up, as `PL-KVDK` did here.

**This is not `impairs-generators:`, and that was checked** (triage,
2026-09-23). The count does what `subprojects/docket/README.md` specifies: it
counts the distinct captures `docket new` matched to one item. Nothing specifies
chaining, and `anchor`'s docstring limits it to reordering a shortlist of open
items. Chaining would be new behaviour in the generator machinery.

**Pause.** `PL-6Q9L`'s pause holds this. While any open item carries
`generator: live`, no new check or re-specification of the generator rule is
built. `blocked-by` names the three open items that carried one on 2026-09-23.
When they close, confirm that `bin/docket next` shows the generator tier empty
before unblocking, because any new `live` head keeps the pause in force.

**Unblocked 2026-09-23 by `PL-1P5V`, the last open item on the generator
tier.** `PL-BBT8` and `PL-DSPM`, the two machinery defects that shared it, merged
the same hour, so the tier is empty once `PL-1P5V`'s pull request lands and the
pause above has ended.

**Done when.** The chain count is re-run first. Then one of two outcomes:
either recurrence evidence follows a closed anchor to the open item that
absorbed its successor, with a test on the `PL-K5PW` ← `PL-T441` ← `PL-WF3X`
shape, or the item is dropped with the count recorded.

**Recommended.** Re-count before building. One chain in the three days since
the signal landed (2026-09-20), for a mechanism that was found by hand anyway,
does not yet pay for a change to the generator machinery.

**Generator check.** A one-off at the edge of the recurrence signal that
`PL-TZ7T`'s cluster built. It is not a post-close instance of that head's
mechanism, because all three re-filings were noticed and recorded, which is
what its fix does. The design fact is that `anchor` chooses among open items
only, so the evidence starts over when its anchor closes.
`duplicates.near_duplicates` documents that choice, and no other open item
stands on it.
