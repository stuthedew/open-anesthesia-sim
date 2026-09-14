---
id: PL-B8MK
title: A bookmark instant is not forkable, and the obvious route to making one changes the case it marks
priority: P2
effort: M
status: blocked
blocked-by: PL-LPLD, PL-CTD7
classes: science, feature, anticipated
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core/run_definition.py, tests/unit, tests/integration, docs/MODEL.md, docs/ARCHITECTURE.md
added: 2026-09-14
---

**Problem.** A bookmark instant is not forkable, and the obvious route to making one changes the case it marks

**Why it matters.** `ROADMAP.md`'s v0.5.0 Definition of done asks for "a branch
taken at any recorded control event **or bookmark**", and `PL-TFX5`'s own
Done-when repeats it. The control-event half is shipped. The bookmark half is
not merely unbuilt: it is *refused* by the keyframe rule `PL-J2TD` deliberately
landed, so it is a design question rather than a missing feature, and answering
it is a precondition for `PL-Z3W6`'s bookmark assertion.

**Where it stands.** `SimulationController.resumed_at` accepts only instants
the trunk holds a keyframe for — its opening and every recorded setting change.
A bookmark's instant has no reason to be one of those: on the 120 s sevoflurane
run with two control changes that the fork tests use, 3 of the 1 201 step
instants a halt could land on are keyframes.

**Two routes, measured 2026-09-14 on a 3 600 s sevoflurane run with changes at
300 s and 600 s, forked at a bookmark of 655.3 s, compared element-wise across
the nine state entries at six probes out to an hour.**

- **Record a keyframe where the run halts.** The branch is then exact against
  the trunk it forked from — 0 of 54 elements differ. But the trunk is no
  longer the run it would have been: against the same case built without the
  bookmark, **48 of 54 elements differ, worst 8.07e-13**. Marking a run changes
  it. Recorded at the halt rather than retroactively, nothing *already
  computed* moves — every instant before the bookmark stays bit-identical — but
  everything the case goes on to say afterwards is displaced. It also needs new
  core API (`RunDefinition.record_change` drops a call whose settings equal the
  ones in force, and takes no instant, so it can only act at `duration_s`;
  `advance_to` refuses to rewind), and it breaks the invariant
  `test_a_setting_change_opens_a_segment_where_the_run_saw_it` asserts — that
  the control timeline's stamps are exactly the segment openings after the
  first — because a bookmark keyframe has no timeline entry behind it.
- **Open the branch's definition at the keyframe *before* the bookmark**, while
  its clock and its live uptake system stand at the bookmark instant. Every
  instant after the fork is then one propagation from the same keyframe the
  trunk propagates from, so the two compose identically: **0 of 54 elements
  differ, and the trunk is byte-identical to an unmarked case.** No new core
  API and no keyframe recorded.

**What the second route costs, which is not nothing.** `origin_s` and the fork
instant stop being one number, so every reader that subtracts one needs to know
which it wants; the branch's definition answers for instants between that
keyframe and the fork, which the branch did not live through, so `drawn_window`
would draw it back past its own beginning unless clipped; and `_open_at` — which
`reset()` shares — must restore the fork state rather than the segment's
opening state. Four named edits, all inside `app/controller.py`.

**Not decided here.** `PL-TFX5` shipped the control-event half and
`docs/ARCHITECTURE.md` § "What a branch is, and what it shares with its parent"
records that a bookmark is not yet a fork point and points here. The choice
belongs with `PL-LPLD` and `PL-CTD7`, which build the bookmark and its halt;
the measurements are recorded now because they were expensive to get and
because the obvious route is the worse one.

**Placed in v0.5.0's Required scope (project owner, 2026-09-14).** This began
as a capture made while `PL-TFX5` was built. The owner's decision that day
split `PL-TFX5`'s "at any control-input event **or bookmark**" clause in two
and gave the bookmark half to this item, so this is now a scope entry of its
own in `ROADMAP.md` § "Required scope" rather than a finding beside one. Two
things follow.

`ROADMAP.md`'s Definition of done for v0.5.0 asks that "a branch taken at any
recorded control event **or bookmark** reproduces its parent element-wise at
every sampled point up to the branch point". The control-event half is shipped.
This item is what makes the other half reachable at all, so the milestone is
not complete without it - it is not a nice-to-have left behind by the split.

And `PL-Z3W6` waits on this rather than on `PL-TFX5`. Its Done-when asks for "a
branch taken on a recorded sample **and** a branch taken between two of them",
and a branch between two recorded samples is precisely a fork at an instant the
run holds no keyframe for - this item's subject. Its `blocked-by` was moved
here when `PL-TFX5` closed.

**Triaged `science` rather than `feature` alone**, and banded `P2` under the
`blocked` exception the checker allows: what is decided here is a numerical
guarantee about a displayed comparison, not a capability. Route one moves the
trunk's own curve, which is a run changing because it was observed; route two
does not. Nothing is reachable today - no bookmark exists - which is why this
sits at `P2` beside `PL-Z3W6` rather than in the top band.