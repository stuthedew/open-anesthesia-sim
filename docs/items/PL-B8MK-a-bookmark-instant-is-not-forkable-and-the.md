---
id: PL-B8MK
title: A bookmark instant is not forkable, and the obvious route to making one changes the case it marks
priority: P1
effort: M
status: done
classes: science, feature, anticipated
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/bookmarks.py, src/anesthesia_sim/core/run_definition.py, tests/unit, tests/integration, docs/MODEL.md, docs/ARCHITECTURE.md, ROADMAP.md
added: 2026-09-14
closed: 2026-09-20
payoff: makes v0.5.0's Definition of done reachable - a learner can branch at a bookmark, which the roadmap asks for and the tree still refuses - without the act of marking a run changing the run
verify: grep -q 'def test_a_branch_taken_at_a_bookmark_reproduces_its_parent_without_changing_it' tests/integration/test_controller.py
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
  ones in force, and takes no instant, so it can only act at `reached_s`;
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

**Re-priced 2026-09-14, and the second route got cheaper rather than only
different** (`PL-ZMRT`, which left the application one simulated-time frame).
The paragraph above is kept because it is what the measurement was weighed
against; two of its four costs have since been paid or deleted outright, and
neither is owed by this route any more:

- **`origin_s` no longer exists**, with both subtractions. There is no reader
  that subtracts one and so none that needs to know which number it wants.
  What the route now asks for is a `RunDefinition` opened at the keyframe
  before the bookmark while the clock stands at the bookmark — two different
  case instants on one axis, which the constructor already takes as
  `opened_at_s` and the clock already carries. The distinction the old cost
  described was between two *frames*; there is one.
- **`drawn_window` already clips at the definition's own opening** —
  `first_s = max(start_s, self._run_definition.opened_at_s)` in
  `app/controller.py`. Drawing a branch back past its own beginning is
  refused in the shipped tree rather than owed by this route. `PL-3LZB`
  landed the refusal underneath it, so asking a run for an instant before it
  opened raises rather than answering from the nearest keyframe.

What survives is `_open_at` restoring the fork state rather than the segment's
opening state, which is this route's own work and was always the substantive
half. So: **two named edits rather than four**, and the route this item already
recommends is the one that got cheaper. Re-read the four-edit count above as
history, not as the price.

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

## Promoted 2026-09-20 (`PL-D9K3`), and why the hazard is not live

**Both blockers closed on 2026-09-20** - `PL-LPLD` and `PL-CTD7` - and
`PL-CTD7` closed naming this item outright: "Not built here, and not in scope:
forking *at* a halt is `PL-B8MK`, which this unblocks." So the promotion is
what its own blocker asked for rather than an inference from the `blocked-by`
field having gone stale.

**Read against the tree, nothing else holds it.** The two things this item
said it waited on are both present. `PL-CTD7` landed the crossing detection in
`app/bookmarks.py` as pure functions over two readings, with the halt and
`bookmark_halt` / `bookmark_standings` on the controller's snapshot, so there
is a halt instant to fork *at*. And the route question this item deferred to
`PL-LPLD` and `PL-CTD7` is answered by the measurement already in the brief
above rather than by anything either of them decided: route 2 leaves 0 of 54
elements differing and the trunk byte-identical to an unmarked case, where
route 1 displaces 48 of 54. That is an engineering choice settled by a
measurement this repository has already run, not a question about what the
project is for, so it does not hold the item at `needs-decision`.

**`science, anticipated`, and leaving `blocked` returns it to the debt gate**
(`PL-ZF2G`) - so this is the judgment `PL-JFQ3` and `PL-8G48` each had to make,
and it goes the same way `PL-8PS6` did. **The hazard is not live.** Forking at
a bookmark is *refused* today by the keyframe rule `PL-J2TD` landed, so the
application raises rather than computing a branch from a keyframe it has no
right to - which is the safety-critical standard's own preference for an
obvious failure over a plausible-looking number. Nothing displayed is wrong
and nothing is misattributed. What changed is **startability**, not liveness:
the work is buildable now and was not before. That is the same distinction
`PL-8G48` drew between `PL-8PS6` and `PL-WZVZ`.

**Banded `P1` because the `science` class requires it** once the item is
startable, which is what `docket check` holds every `science`-classed item to
outside `blocked`. It is also v0.5.0 `Required scope` - `ROADMAP.md`'s
Definition of done asks for "a branch taken at any recorded control event **or
bookmark**", and the control-event half shipped with `PL-TFX5` - so the
milestone cannot close without it either way.

**Done when.** A branch can be taken at a bookmark instant, by opening the
branch's `RunDefinition` at the keyframe before the bookmark while its clock
and uptake system stand at the bookmark - route 2 above - so that the branch
reproduces its parent at every instant they share **and** the trunk is
byte-identical to the same case built without the bookmark. `_open_at`
restores the fork state rather than the segment's opening state, which is this
route's remaining substantive edit. `docs/ARCHITECTURE.md` § "What a branch
is, and what it shares with its parent" stops saying a bookmark is not yet a
fork point, and `docs/MODEL.md` records that marking a run does not change it.

**Two sessions promoted this within four minutes of each other, and this file
is the reconciliation** (2026-09-20). `PL-D9K3` on
`claude/amazing-wozniak-yz3dgv` wrote the promotion at 17:26 and this branch
wrote a second one at 17:29; they agreed on every field that matters - `ready`,
`P1`, route two - which is worth recording, since the two reached it from
different directions and neither could see the other. The first commit holds
the item, so the section above, `payoff:` and `verify:` are `PL-D9K3`'s
unchanged. What follows is what only the second pass had, kept because it is
evidence rather than wording. The `blocked-by: PL-LPLD, PL-CTD7` line both
copies inherited is gone: both are closed, and a `ready` item naming them makes
`bin/docket concurrent` report this item as unable to run alongside two items
nobody can start.

**The fault, reproduced 2026-09-20 on `b2b3ffe`** through the shipped path,
now that `PL-CTD7`'s halt exists to produce it. Watching a `verify:` command
fail proves the fix is absent; it does not prove the fault is present, and
these are different claims. A default `SimulationController` carrying
`TimeBookmark(30.0)`, started and stepped at 0.1 s, halts at exactly 30.0 s on
`BookmarkCrossing(instant_s=30.0, time_bookmarks=(TimeBookmark(instant_s=30.0,
label=None),), mac_targets=())`. `run_segments` then holds a single keyframe,
at 0.0 s, and `resumed_at(30.0)` raises `SimulationConfigurationError: this run
holds no keyframe at 30.0 s, so opening there would restart from two
propagations where the run took one and would not reproduce it element-wise; it
holds keyframes at [0.0] s`. That is the whole item in one run: the learner is
standing on the instant they marked, and it is the one instant the fork
refuses.

**One question left to the implementing session, with a default rather than an
open end.** Whether the fork is offered at *any* instant the run holds live
state for, or only at the halt the run is standing on. Route two needs the
state at the fork instant, and a halt is where the run has it, so the default
is the halt: the fork is reached from `snapshot().bookmark_halt` rather than
from an arbitrary float, and
`test_an_instant_between_keyframes_is_refused_rather_than_approximated` keeps
its refusal unchanged for an instant the run is not standing on. Widening it
past that is `PL-Z3W6`'s to ask for, not this item's.

**The re-pricing above is wrong on `drawn_window`, and the cost is three named
edits rather than two** (project owner, 2026-09-20). Its second bullet reads
the shipped clip - `first_s = max(start_s, self._run_definition.opened_at_s)`
in `app/controller.py` - as already refusing to draw a branch back past its own
beginning. That is true only while `opened_at_s` *is* the fork instant, which
is exactly the identity this route gives up: the definition opens at the
keyframe before the fork, so the clip lands at that keyframe and the branch
becomes drawable across an interval it never lived, showing the trunk's
trajectory under the branch's identity. The comment on those lines says "a
branch opens at its fork" and would stop being true with it. So the fork
instant has to be carried explicitly and the clip read from it - not the
`origin_s` subtraction `PL-ZMRT` deleted, which converted between two frames,
but a second case instant on the one frame, beside `opened_at_s`. The three
edits are: `_open_at` restoring the fork state rather than the segment's
opening state, the fork instant carried on the controller, and `drawn_window`
clipping at it.

`docs/MODEL.md` § "What this requires of a branch" now records which of its two
conditions this route relaxes and why the element-wise guarantee survives it,
and `docs/ARCHITECTURE.md` records that the route is chosen and not yet built.
Both were amended ahead of the implementation deliberately: the section states
two conditions a branch satisfies, a bookmark fork cannot satisfy both, and a
reader meeting the unqualified pair would conclude a bookmark fork is
impossible rather than that one condition was always the special case of a
weaker one.
