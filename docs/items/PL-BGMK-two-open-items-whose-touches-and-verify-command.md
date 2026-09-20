---
id: PL-BGMK
title: Two open items whose touches and verify: command overlap are never compared, so PL-1YDK and PL-8PT6 were filed and worked as one finding twice and only docket check --verify on main caught it
priority: P2
effort: M
status: needs-decision
classes: defect, infra
feature: open-item-overlap-detection
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-13
---

**Problem.** Two open items whose touches and verify: command overlap are never compared, so PL-1YDK and PL-8PT6 were filed and worked as one finding twice and only docket check --verify on main caught it

**Why it matters.** `PL-1YDK` and `PL-8PT6` were filed separately, triaged
separately and worked separately on one finding. Nothing in the store compared
them, and what eventually noticed was `bin/docket check --verify` on `main` -
after both had merged, which is the most expensive moment available. Two
sessions had already been spent, and the merge that reddened `main` is what
made it visible at all.

The store holds the evidence that would have caught it. `touches` is declared
on almost every open item and `concurrency.py` already builds a graph from it;
`verify:` is a command string, and two items proposing the same command are
proposing the same work by definition. Neither is read for this, so the only
thing standing between the queue and a duplicate is whether one session happens
to recognise another session's title.

**Decision needed.** Whether an overlap signal can be made specific enough to
be worth having, and what it fires on. `touches` alone is far too broad - Gate
1's science half all declares `docs/MODEL.md`, so a pairwise comparison would
report dozens of pairs on every run, and `CLAUDE.md` retires a check that fires
every run without changing a decision. The narrow reading is `verify:`: two
open items whose commands are equal, or whose `grep` halves name the same test,
are near-certainly one finding, and that is rare enough to be an error rather
than an advisory. Whether `touches` adds anything on top of it - as a second
condition rather than a first - is the part to measure before building.

Name the number first, per `.claude/rules/expert-review.md`: count how many
open pairs each candidate rule reports against this store today, and what
fraction of them are real duplicates. A rule reporting more than a handful has
failed regardless of how sound it looks.

**Done when.** The question is answered against that count, and either a check
lands carrying the rule that survived it, or the item closes recording that no
rule was specific enough and what the count was.

**Grouped as `feature: open-item-overlap-detection`** (`PL-JKML`'s duplicate
sweep, 2026-09-20, confirmed on independent refutation). `PL-5GBV` and
`PL-BGMK` are two halves of one problem: nothing in this project ever compares
**two items that are already open**. `PL-5GBV` is what that costs downstream -
two items for one defect both reaching `ready` and both entering the frozen
v0.5.0 gate, so the gate counted the same work twice - and `PL-BGMK` is the
comparison that would have caught it, over overlapping `touches` and `verify:`.
Fixing either alone leaves the other standing: a comparison nobody runs at gate
freeze does not stop double-counting, and a gate that de-duplicates does not
stop two sessions working one finding.

**Deliberately not named for the filing-time warning.** `PL-TZ7T` and
`PL-X5JR` cover a *new capture* checked against the store as it is filed. This
group is the other direction - two items already in the store, neither of them
new - which nothing in the recurrence-signal design reaches.
