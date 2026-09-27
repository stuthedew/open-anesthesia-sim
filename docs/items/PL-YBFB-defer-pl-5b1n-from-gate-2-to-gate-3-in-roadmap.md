---
id: PL-YBFB
title: Defer PL-5B1N from Gate 2 to Gate 3 in ROADMAP.md, recording the 2026-09-27 decision that its preview design is settled and its build is feature work for after v0.6.0 ships
priority: P2
effort: S
status: ready
classes: docs
touches: ROADMAP.md, docs/items/PL-5B1N-simulated-traces-should-be-solid-and-a-dotted.md
added: 2026-09-27
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

**Done when.** `ROADMAP.md` § "Debt gate: the frozen list" under v0.6.0
records `PL-5B1N` as deferred to Gate 3 beside the five `PL-DB64` moved, in a
paragraph whose lead-in is the string `verify:` pins, with the ratified clause
above and this item's id, and moved out of its lane group as those five were;
`PL-5B1N` stays written on the list and stays `ready`; and `bin/docket gate`
reports v0.6.0 without it, as it reports the five.
