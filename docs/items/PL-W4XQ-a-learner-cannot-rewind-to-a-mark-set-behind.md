---
id: PL-W4XQ
title: A learner cannot rewind to a mark set behind the clock: resumed_at refuses any instant that is not a keyframe and resumed_at_halt needs the run to be standing on the crossing, so marking 1 h while paused at 3 h gives a mark nothing can return to
status: untriaged
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, docs/MODEL.md, tests/integration/test_controller.py
added: 2026-09-20
---

**Problem.** A learner cannot rewind to a mark set behind the clock: resumed_at refuses any instant that is not a keyframe and resumed_at_halt needs the run to be standing on the crossing, so marking 1 h while paused at 3 h gives a mark nothing can return to

**Raised by the project owner, 2026-09-20**, describing what a time bookmark is
for: "I'm paused at like 3 hours of anesthesia or whatever, and I want to see
what happened if I changed something earlier. So I might set a bookmark at say
1 hour or whatever, and then rewind to that specific point (or just use it as
an event note)."

**Measured the same day** against `4c282700`. A trunk was stepped to 30 min, a
fresh gas flow change recorded there, and stepped on to 3 h. `TimeBookmark`
at 3600.0 s was then added.

- `resumed_at(3600.0)` refuses: "this run holds no keyframe at 3600.0 s, so
  opening there would restart from two propagations where the run took one and
  would not reproduce it element-wise; it holds keyframes at [0.0, 1800.0] s."
- `resumed_at_halt()` refuses: the run is not standing on a crossing, because
  the mark was added after the clock had passed it, so no step ever crossed it.

So both doors are shut, and the marked instant is one nothing can return to.
The rest of the described behaviour already works: rewinding to the 30 min
keyframe gives a branch whose row for the 1 h mark is blank, and that branch
halts at exactly 3600.0 s - the "acts like a future bookmark" half needs
nothing.

**Why it matters.** The one act the owner described the feature *for* is the
one the model refuses. A mark a learner cannot return to is an event note, and
an event note is the lesser of the two things they asked for.

**It is not `PL-TYWQ`.** That item offers the fork the run is *standing on*
through the panel, which is the halt case. This is the case where no halt ever
happened, so there is nothing for a panel to offer and the refusal is in the
model.

**What it runs into.** `_resume_point_at`'s keyframe restriction is not
arbitrary: opening between two keyframes restarts from two propagations where
the run took one, which is the element-wise reproduction `ROADMAP.md` item 12
asks for. `PL-B8MK` bought the bookmark-halt fork by
having the run *be* at the fork with live state; a mark behind the clock has no
such state, so the honest routes are to re-propagate from the nearest keyframe
and declare what that costs, to record a keyframe when a mark is added behind
the clock (which moves the run's own later answers - the failure `PL-B8MK`
measured at 48 of 54 elements and rejected), or to refuse the act at entry and
say so rather than accepting a mark nothing can use.

**Done when.** A learner who marks an instant the run has already passed can
either branch there, or is told at the moment of marking that they cannot and
why; and whichever is chosen, `docs/MODEL.md` states what a fork at a
non-keyframe instant does and does not reproduce.
