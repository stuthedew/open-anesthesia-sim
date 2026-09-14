---
id: PL-TFX5
title: Fork a run at any control-input event, flat rather than as a tree
priority: P2
effort: L
status: done
classes: feature
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core, tests/unit, tests/integration, docs/ARCHITECTURE.md
added: 2026-09-06
closed: 2026-09-14
pr: 570
verify: uv run pytest tests/integration/test_controller.py && grep -q 'def test_a_case_forks_at_every_instant_the_trunk_offers' tests/integration/test_controller.py
---

**Problem.** Comparing two managements of the same case - coast on low flow
versus hold 0.5 MAC, then compare time to a wake-up threshold - currently means
building the whole case twice, and the two runs then differ by every small
thing that was not reproduced identically.

**Why it matters.** This is the educational payload of the whole milestone: it
isolates the variable under study. A learner reading a comparison of two
independently built runs cannot tell which differences they caused.

**Shape (project owner, 2026-08-25).** Flat, not a tree: one trunk run with N
branches taken from points on it. Sub-forks of forks are deliberately out -
they multiply without bound and buy little over re-branching from the trunk.

**Branch points.** Any recorded control-input-timeline event is a valid branch
point, not only a placed bookmark. This generalizes the reference simulator's
single-track truncate-and-continue behavior into true forking, where the
pre-change branch is kept rather than discarded so both are available for
comparison.

**What a branch inherits.** Its parent's agent and its patient, rather than
re-choosing either: changing agent is already an explicit new case (`PL-R3KB`,
v0.4.0), and a branch that could change it would be a second case wearing a
comparison's clothes.

**Where.** `src/anesthesia_sim/app/controller.py`;
`docs/ARCHITECTURE.md` records what a branch is and what it shares with its
parent.

**Done when.** A run can be forked at any recorded control event or bookmark;
the trunk survives the fork; branches of branches are refused rather than
silently flattened; and the branch carries its parent's agent and patient. The
reproduction property is `PL-Z3W6`.

---

## Session of 2026-09-14: four clauses of five delivered, and the fifth is a question

**What was built, and why it is smaller than this brief reads.** `PL-J2TD`
shipped `SimulationController.resumed_at` the same day, and with it three of
this item's Done-when clauses outright: a fork at any recorded control event
(they are exactly the run's keyframes), the trunk surviving (`resumed_at` reads
`self` and writes nothing, and the branch's `AgentUptakeSystem` is its own), and
a branch of a branch refused. Its own test suite carries seventeen of them, one
named for this item. What was left was the shape rather than the mechanism.

- **`BranchedCase`** (`app/controller.py`) holds a trunk and the branches taken
  from it. `resumed_at` hands a branch back detached, so two calls produce two
  controllers that each know the instant they opened at and none of which knows
  the others exist — nothing could say that two curves on one axis are one
  patient under two managements rather than two patients, which is the
  relationship `ROADMAP.md` calls this milestone's capability boundary.
  `fork_points_s` names the instants a fork may be taken at. The flat shape
  stops being a refusal: the trunk is the only run it will fork, so a sub-fork
  is not an operation it can express, and a case rooted in a branch is refused
  at construction. `resumed_at` keeps its own refusal for the caller holding a
  branch directly — that one says *this run* cannot be forked, this one says
  there is no second generation to fork from.
- **`set_agent` refuses on a branch.** This item says a branch inherits its
  parent's agent "rather than re-choosing" it, and nothing enforced it.
  `set_agent` begins a new run, so `_build_state` cleared `opened_from` with
  everything else: the run silently stopped being a branch, `reset()` stopped
  returning it to its fork, `resumed_at` began accepting it as a trunk — a
  branch of a branch through the back door — and a `BranchedCase` went on
  listing it among the branches of a case it had left. Refused now, naming the
  fork instant. The trunk is untouched.
- **The clause's own test was passing through a fallback.**
  `test_a_branch_is_the_agent_and_patient_its_parent_was` never moved a patient
  quantity, so `_setting_at` fell through to the value in force now and the
  assertion proved that a branch rebuilds the same reference patient from the
  same data file rather than that it carries the one the case was computed
  under. Cardiac output is the only patient quantity a control can move; the
  replacement moves it mid-run and forks either side of the move.
- **`docs/ARCHITECTURE.md` § "What a branch is, and what it shares with its
  parent"**: the three objects, what a branch inherits and why each is not
  re-chosen, the two time frames and which readers are in which, and where a
  fork may be taken. It is an object map and points at `docs/MODEL.md` for
  every guarantee, after a first draft restated that document in three
  paragraphs and published a second measured figure for a phenomenon it already
  measures.

**The fifth clause is the question, and it is a scope question.** "A run can be
forked at any recorded control event **or bookmark**." Bookmarks are `PL-LPLD`
and are not built — and the half that matters is that a bookmark instant is not
merely unbuilt but *refused*: it is not in general a keyframe, and `PL-J2TD`
landed the keyframe-only rule deliberately. On the 120 s two-change run the
fork tests use, 3 of the 1 201 instants a halt could land on are keyframes.

`PL-B8MK` carries the two routes to a forkable bookmark, measured rather than
argued, and the obvious one is the worse: recording a keyframe where the run
halts makes the branch exact against its trunk while moving that trunk's own
later answers away from what the case would have said unmarked — 48 of 54
elements, worst 8.07e-13 — so marking a run changes it. Opening the branch's
definition at the keyframe *before* the bookmark costs the trunk nothing and is
exact too.

**Split, and this item closed on the control-event half (project owner,
2026-09-14).** The question put was whether the bookmark clause stays here or
moves, and it was the owner's because answering it re-words `ROADMAP.md`'s
Required-scope bullet for this item - the same reason `PL-J2TD`'s narrowing
three days earlier was. It moves. `PL-B8MK` carries it, behind `PL-LPLD` (the
bookmarks themselves) and `PL-CTD7` (the halt a keyframe would be recorded at),
and `ROADMAP.md`'s § "Required scope" now runs to nineteen entries with the
bookmark clause as one of its own rather than a clause inside this one - which
is what `PL-4PC5` says an id must be to be counted at all.

Two consequences, both intended. `PL-8PSW` (overlay two branches) has both its
blockers closed: its overlay needs the trunk-and-branches structure, which
shipped here, and nothing about bookmarks. `PL-Z3W6` (assert element-wise
reproduction) does not: its Done-when asks for "a branch taken on a recorded
sample **and** a branch taken between two of them", and the second of those is
exactly what `PL-B8MK` decides, so its `blocked-by` moves from this item to
that one rather than clearing.

**Clause 1 had a hole, found by an adversarial verification pass after the
first close-out was written, and fixed here.** "A run can be forked at any
recorded control event" binds two records that collapse redundant changes by
different rules, and it holds only while those rules agree.
`RunDefinition.record_change` compares whole settings against the previous
stretch, so it is order-independent. `_record_control_change` compared one
entry - and only the *newest* one.

Two dials nudged and both put back, **interleaved** - fresh gas flow up,
cardiac output up, flow back, output back - separates them: each move's
predecessor is the other control, so no collapse fires. Measured on a trunk at
a 30 s step boundary, four entries stood in `snapshot().control_timeline` at an
instant the run never changed at, while the definition correctly held no
keyframe there - so `resumed_at` refused the very instant the timeline was
showing as a control event. The **nested** order (F+ C+ C- F-) collapsed to
nothing in both records, which is why the defect was order-dependent and why
`test_a_setting_change_opens_a_segment_where_the_run_saw_it` did not catch it:
that test moves two controls once each, which cannot reach the case.

A learner reaches it while **paused**, where `advance()` is a no-op and every
control they touch carries one instant, so fiddling with two sliders and
putting both back is the direct path. What was on screen was four adjustments
the model never saw, drawn as control marks at an instant the run held
constant - the presentation failure `CLAUDE.md`'s standard names, rather than
only a fork that was refused.

The collapse now searches back across the entries at this instant instead of
reading `[-1]`, and `test_every_recorded_control_event_is_an_instant_the_run_
can_be_forked_at` asserts the property rather than the repair: every stamp a
reader is shown is an instant the run holds a keyframe for, and `resumed_at`
accepts each one. It fails on the tree without the fix, with the four extra
entries named in its output.

**What proved it.** The command is:

```
uv run pytest tests/integration/test_controller.py && grep -q 'def test_a_case_forks_at_every_instant_the_trunk_offers' tests/integration/test_controller.py
```

It was run before being recorded and seen to fail for the right reason: against
`origin/main`'s copy of that file the pytest half passes its 90 tests and the
`grep` finds nothing, so the pair exits 1.

It sat in `not-delegable:` rather than `verify:` for the hours this item stood
at `needs-decision`, and that is worth recording because the reason was not the
usual one. `docket check --verify` errors on an open item whose command already
passes, offering two readings - the work landed unclosed, or the command does
not discriminate - and neither was true: it discriminated exactly, and what was
open was the scope answer above. A decision is work no command proves, which is
what `not-delegable:` is for. Closing the item is what makes a passing command
the right field again, so the two moved back in this commit.

**Captured this session and not fixed here:** `PL-B8MK` (the bookmark routes),
`PL-9KP5` and `PL-4K9V` (`PL-2FM6`'s unswept sample-store prose in
`docs/ARCHITECTURE.md` and `app/formatting.py`), `PL-XJ37` (nothing lets a
learner take a fork or select between runs), `PL-NC62` (the settings-mismatch
refusal names one cause for every failure), `PL-LLBV` (the whole-step guard and
a typed time).

**Amended 2026-09-14 by `PL-ZMRT`** (one simulated-time frame). The close-out
above says it wrote "the two time frames and which readers are in which" into
`docs/ARCHITECTURE.md` § "What a branch is, and what it shares with its
parent". That passage now reads "**One time frame, and every reader is in
it.**" - the second frame it described was removed the same day, along with
`SimulationController.origin_s` and the subtractions in `advance` and
`drawn_window`. What this item delivered is unchanged; only the paragraph it
points at has been rewritten under it.
