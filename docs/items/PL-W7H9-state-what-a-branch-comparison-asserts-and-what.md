---
id: PL-W7H9
title: State what a branch comparison asserts and what it does not, in docs/MODEL.md and docs/ARCHITECTURE.md
priority: P1
effort: S
status: done
classes: docs, safety, anticipated
feature: scenario-branching
milestone: v0.5.0
touches: docs/MODEL.md, docs/ARCHITECTURE.md
added: 2026-09-06
closed: 2026-09-21
pr: 849
payoff: writes down the limits of the most persuasive thing this simulator draws, before a learner reads a difference between two curves as a result about patients
verify: grep -q 'What a branch comparison asserts' docs/MODEL.md && grep -q 'What a branch comparison asserts' docs/ARCHITECTURE.md
---

**Problem.** A side-by-side comparison of two branches makes a claim, and
nothing states what the claim is or where it stops.

**Why it matters.** A comparison is the most persuasive thing this simulator
draws: two curves, one difference, an obvious conclusion. That persuasiveness
is exactly why its limits have to be written down. A reader can otherwise take
"low flow woke this patient 12 minutes sooner" as a result about patients
rather than about one parameter set, one reference adult, and a model with no
inter-individual variability at all.

**What has to be stated.**

- What two branches share - patient, agent, parameter set, model version, and
  every control value up to the branch point - and what therefore *can* be
  attributed to the settings that differ.
- That the pre-branch history is identical by construction rather than by
  measurement, and what that does and does not guarantee after the branch
  point.
- That neither branch is a prediction for a patient: the model has one
  reference adult and no inter-individual variability, so a difference between
  branches is a property of the model, not an expected clinical difference.
- Any divergence bound `PL-Z3W6` could not eliminate.

**Where.** `docs/MODEL.md` (a subsection beside the reproducibility guarantee)
and `docs/ARCHITECTURE.md` (what a branch is, structurally).

**Done when.** Both documents carry the statements above, and the interface
does not assert anything about a comparison that they do not support.

## Groomed 2026-09-20 under `PL-JFQ3`: `PL-8PSW` removed one prerequisite; the hazard is not live

**The question this item was groomed to answer.** `PL-JFQ3` (the nine blocked
items whose blockers have closed) singles this one out, because since `PL-ZF2G`
the `anticipated` carve-out in `tools/doc_check.py`'s `check_gate_reentries`
holds only while `anticipated` and `status: blocked` hold *together*. Promoting
this item is therefore the event that returns a `safety`-classed finding to the
debt gate, and the question is whether `PL-8PSW` closing made its hazard live
or merely removed one prerequisite.

**It removed one prerequisite. The hazard is not live.** The hazard here is a
*reader* taking two curves as a claim about patients, and no reader can reach
two curves. Checked against the tree on 2026-09-20:

- `PL-8PSW` (overlay two branches on one time axis) landed the drawing:
  `SimulationView` is documented as "The dashboard over one or two runs on one
  agent", and `docs/MODEL.md:181` records the two-run hover conventions as
  shipped.
- `src/anesthesia_sim/app/main.py` constructs `SimulationView((controller,))` —
  one run — and its own docstring opens "The application entry point: one run,
  one window, two timers".
- Neither `main.py` nor `simulation_view.py` mentions `branch`, `BranchedCase`
  or `ResumePoint` at all. `grep -rnE 'branch|BranchedCase|ResumePoint'` over
  both returns nothing. Nothing in the shipped application opens a fork.

So `PL-8PSW` made a comparison *drawable*, not *reachable*, and a statement
about what a comparison asserts has no reader until a learner can take one.

**The real blocker, now declared.** `PL-XJ37` (nothing in v0.5.0's scope lets a
learner take a fork or select between runs, and `SimulationView`'s run set is
fixed at construction) is `needs-decision` and is the item that makes a
comparison reachable. It is written into `blocked-by` beside `PL-8PSW`, which
is kept because the sequence is the record: this item waited on the overlay,
the overlay landed, and it now waits on the route to it.

**What that costs, recorded rather than claimed away.** The carve-out holds
only while this stays `blocked`, so the moment `PL-XJ37` resolves, this item
becomes a live `safety` finding that `checks.py` pins to `P1` — and the
promotion is a grooming pass, not an automatic consequence. That window is
`PL-ZF2G`'s own accepted cost and is unchanged by this pass; what has changed
is that the edge now names something open, so the advisory that would have
carried it is no longer firing against a closed blocker.

**One thing this pass did *not* find, and it is worth saying.** Neither
document carries the statements this item asks for. `docs/MODEL.md`'s only "not
a prediction for the patient" sentence (line 5639) is about the MAC-awake band,
a different claim; `docs/ARCHITECTURE.md` § "What a branch is" describes the
structure in full and states what a branch *guarantees* without stating what a
comparison of two of them does not. Nothing here is overtaken, so the work is
intact and waiting.

## Re-pointed 2026-09-20 under `PL-XJ37`: the blocker is `PL-VKJW`

`PL-XJ37` was a decision item, and the project owner answered it on
2026-09-20: forking is v0.5.0's scope and the run selector is deferred. The
implementation that answer names is `PL-VKJW` (a learner takes a fork from the
dashboard), and that is what `blocked-by` now carries in `PL-XJ37`'s place.
`PL-8PSW` is kept beside it for the reason the last pass kept it - the
sequence is the record.

**Nothing in the grooming above changes.** The finding it made is unaltered:
`PL-8PSW` made a comparison drawable and not reachable, and a statement about
what a comparison asserts has no reader until a learner can take one.
`PL-VKJW` is the item that makes one, so the edge now points at the work
rather than at the decision about the work.

**The accepted cost it recorded is unchanged too, and is worth restating
because the window has moved rather than closed.** The `anticipated` carve-out
in `tools/doc_check.py`'s `check_gate_reentries` holds only while
`anticipated` and `status: blocked` hold together, so this item becomes a live
`safety` finding pinned to `P1` when its blocker clears - which is now
`PL-VKJW` closing rather than `PL-XJ37` closing. That is `PL-ZF2G`'s own
accepted cost and needs no action here; what the re-point buys is that the
edge names something that can actually be worked.

**One thing `PL-VKJW` adds to what this item has to state.** Under the shape
the owner chose there is exactly one comparison at a time - the trunk and one
branch - and a second fork is refused rather than replacing the displayed
branch. So what a comparison asserts is a claim about *two* managements of one
case, never about N, and the documents should say that rather than leaving the
reader to infer a general facility from a capped one.

## Re-pointed 2026-09-20 under `PL-VKJW`: both recorded blockers are closed, and it is still blocked

`PL-8PSW` drew the overlay and `PL-VKJW` made it reachable, so the two ids this
item carried are both `done`. It was not promoted on that, because the field
could not see what actually holds it: the fourth thing this item has to state
is "any divergence bound `PL-Z3W6` could not eliminate", and `PL-Z3W6` is open.
Writing this section before that measurement exists means either stating a
bound nobody has measured or leaving the one clause a reader most needs.

`blocked-by` now names `PL-Z3W6` alone. The chain behind it is `PL-B8MK` (make
a bookmark's instant forkable) → `PL-Z3W6` (assert a branch reproduces its
parent element-wise up to the fork) → this item, and all three are in v0.5.0's
Required scope.

## `PL-Z3W6`'s answer to the fourth bullet, 2026-09-21

**There is no residual bound to state: it is zero.** A branch and its parent
agree element for element at every instant they share, at a fork on a keyframe
and at a fork between two of them, and `docs/MODEL.md` § "What this requires of
a branch" now says so in its own paragraph - "So nothing is left over to bound,
and there is nothing to show a learner" - with the tests that hold it named.
So the bullet is answered by quoting that, not by measuring anything.

**The third bullet is the one that still needs care, and the reason is in the
same section.** The two divergences that *do* exist are real and neither is a
residue of the guarantee: the display path's, which puts a few units in the
last place between two runs' drawn columns where a reader comparing traces
might take it for a disagreement about the case, and the restart the program
refuses, which no branch it builds ever takes. Both are orders below anything
a readout resolves. A comparison section that says "identical before the fork"
without saying which path that is true of would be wrong about the one a
learner is looking at.

## Landed 2026-09-21

**`docs/MODEL.md` § "What a branch comparison asserts, and what it does not"**,
a new top-level section in four parts: what is compared and what the two runs
share (eight inherited things, each naming the test that holds it); that the
shared history is identical by construction rather than by measurement, and
what that does *not* guarantee; that neither run is a prediction for a patient;
and what the interface may and may not assert about a comparison.

**`docs/ARCHITECTURE.md` § "What a branch comparison asserts, and which part of
it is structural"** replaces the placeholder paragraph that named this item.
It carries the three claims the object map itself decides - that the comparison
is a trunk and one branch, that what may be attributed to the differing
settings is the complement of what a branch inherits, and that the shared
history is the same object rather than a reproduction - and routes the rest to
`docs/MODEL.md`.

**All four bullets of "What has to be stated" are answered.** The fourth -
"any divergence bound `PL-Z3W6` could not eliminate" - is answered by quoting
the zero `PL-Z3W6` established, and the section says in its own words why
nothing is drawn for it. The third is stated with the two divergences that do
exist named beside it: the display path's, which is what a learner comparing
traces is actually looking at, and the restart no branch this program builds
ever takes.

**Two judgments worth recording, neither of which changed the deliverable.**

- **Placement.** The brief said "a subsection beside the reproducibility
  guarantee". The guarantee sits under § "Conventions" -> § "Time", which files
  a statement about what a drawn comparison claims under a units-and-frames
  heading. It is a top-level `##` immediately before § "Interface boundary"
  instead - the last thing said about the model before the document turns to
  what may be displayed - and the reproducibility guarantee, the zero-bound
  paragraph under § "The canonical evaluation rule" and `docs/ARCHITECTURE.md`
  all now point at it, so a reader arriving at any of the three is one link
  away.
- **The heading name came from this item's own `verify:`**, which greps both
  documents for `What a branch comparison asserts`. The drafted headings read
  "a comparison of two runs"; they were renamed to satisfy the pre-written
  check rather than the check rewritten to match the prose.

**One statement was narrowed after an audit of the shipped interface.** The
prohibition first read "no time-to-wake-up or time-to-any-endpoint figure",
which the bookmark halt would have contradicted: two runs halted at one marked
height do read two instants. The section now draws the line where it belongs -
an instant a run *reached* is not a figure predicted for an endpoint it has not
- and says the same of each run's control-change record, which states its own
run's inputs rather than the difference between the two.

**Interface audit, 2026-09-21.** `src/anesthesia_sim/app/dashboard_frame.py`,
`src/anesthesia_sim/app/chart_frame.py` and
`src/anesthesia_sim/app/qt_chart.py` assert nothing about a comparison beyond
the branch-point legend entry, the per-run naming the hazard table already
requires, and the two standing disclaimers. No difference trace, no ranking, no
wake-up figure. The "Done when" clause about the interface holds as shipped.
