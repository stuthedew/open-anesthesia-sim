---
id: PL-YBFB
title: Defer PL-5B1N from Gate 2 to Gate 3 in ROADMAP.md, recording the 2026-09-27 decision that its preview design is settled and its build is feature work for after v0.6.0 ships
priority: P2
effort: S
status: done
classes: docs
touches: ROADMAP.md, docs/items/PL-5B1N-simulated-traces-should-be-solid-and-a-dotted.md
added: 2026-09-27
closed: 2026-10-03
pr: 1309
payoff: puts the owner's decision to defer the preview's build in the gate section beat 3 reads, so Gate 2 stops holding an M feature it was never going to build
verify: grep -qF '**`PL-5B1N` is deferred to Gate 3' ROADMAP.md
---

**Problem.** Defer PL-5B1N from Gate 2 to Gate 3 in ROADMAP.md, recording the 2026-09-27 decision that its preview design is settled and its build is feature work for after v0.6.0 ships
**Where this came from.** The presentation-safety design round of 2026-09-27
(`PL-5B1N`'s "Design round 2026-09-27: recommendations", Q5) recommended
recording the preview's design, setting the item `ready` and deferring its
build to Gate 3 the way `PL-DB64` moved five entries, because deciding clears
nothing by itself: the gate counts an entry cleared at `done` or `dropped`,
and `PL-5B1N` is `feature`-classed, so once decided it is debt no longer but
still open on the frozen list. The project owner answered "Agree" to the round
on 2026-09-27, so the deferral is recorded as **(project owner, 2026-09-27,
ratified, over building the preview now as the next item of the
presentation-safety chain)**. Until `ROADMAP.md`'s gate section says so, the
decision lives only in the item and a thread reply, and § "The cadence" beat 3
counts only what the gate's own section records.

**Why it matters.** Until the gate section says so, the decision lives only in
`PL-5B1N`'s brief and a thread reply, and § "The cadence" beat 3 counts only
what the gate's own section records, so Gate 2 would go on holding an M
feature that v0.6.0 was never going to build before its implementation began.
It can defer on beat 3's terms: the chart it draws on is the pyqtgraph one
v0.6.0 wraps in an Area rather than rewrites, so nothing is done twice
whichever gate builds it; it is `feature`-classed rather than `safety`, so
beat 3's hazard clause does not reach it; and its hazard is not live in any
case, since no preview is drawn today and nothing on screen can be mistaken
for one.

**Re-confirmed 2026-10-03, with two clauses of the done-when changed.** The
brief still held against the tree at `9ea31db2`: `PL-5B1N` was `ready`, in
Gate 2's product-lane group, and `bin/docket wave` counted it among the 30
entries the gate can clear. Two of the done-when's clauses could not both
hold, though. `wave` reads no group heading (`PL-18BD`), so it counts an entry
apart from the work the gate can clear only where the entry's `blocked-by`
leaves the frozen list, and a `ready` item naming a blocker says the work both
can and cannot start. So `PL-5B1N` moved to `blocked`, with `blocked-by:
v0.7.0`, as `PL-Y04W` was for its own Gate 3 deferral: that is the half the
payoff needs, and it also stops `bin/docket next` offering a build the owner
chose not to start now. The design round set `ready` to leave
`needs-decision`, and its design stands. The last clause also named
`bin/docket gate`, which lists open debt across the store and never listed
`PL-5B1N`, a `feature` item; the gate count it means is `wave`'s. Taken here
as an obvious call under the project owner's 2026-09-27 instruction on them,
rather than put back as a choice.

**Done when.** `ROADMAP.md` § "Debt gate: the frozen list" under v0.6.0
records `PL-5B1N` as deferred to Gate 3 beside the five `PL-DB64` moved, in a
paragraph whose lead-in is the string `verify:` pins, with the ratified clause
above and this item's id, and moved out of its lane group into a group of its
own, as those five were; `PL-5B1N` is still written on the list, at `blocked`
with `blocked-by: v0.7.0`; and `bin/docket wave` counts it among the Gate 2
entries waiting outside the list rather than among those the gate can clear,
as it counts the five.

[superseded 2026-10-03: two clauses changed, per the paragraph above; the
current done-when precedes this] **Done when.** `ROADMAP.md` § "Debt gate: the frozen list" under v0.6.0
records `PL-5B1N` as deferred to Gate 3 beside the five `PL-DB64` moved, in a
paragraph whose lead-in is the string `verify:` pins, with the ratified clause
above and this item's id, and moved out of its lane group as those five were;
`PL-5B1N` stays written on the list and stays `ready`; and `bin/docket gate`
reports v0.6.0 without it, as it reports the five.
