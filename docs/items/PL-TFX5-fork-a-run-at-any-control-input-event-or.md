---
id: PL-TFX5
title: Fork a run at any control-input event or bookmark, flat rather than as a tree
priority: P2
effort: L
status: needs-decision
classes: feature
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core, tests/unit, tests/integration, docs/ARCHITECTURE.md
added: 2026-09-06
not-delegable: what is left is an answer rather than code - whether the bookmark clause stays in this item or moves to PL-B8MK - and no command proves a decision. The command that proved the code half is in the brief, and becomes this item's `verify:` if the answer closes it here
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

**Decision needed.** Does the bookmark clause stay in this item, or move to
`PL-B8MK` behind `PL-LPLD` and `PL-CTD7`? Recommendation: move it, and close
this item on the control-event half. It is the only clause outstanding, it
cannot be worked until bookmarks exist, and holding this item open holds
`PL-8PSW` and `PL-Z3W6` with it — `PL-8PSW`'s overlay needs the
trunk-and-branches structure, which is shipped, and nothing about bookmarks.

**The disposition is the project owner's**, because it re-words
`ROADMAP.md`'s Required-scope bullet for this item, which is the same reason
`PL-J2TD`'s narrowing was. Either this item closes on the control-event half
with the bookmark half carried by `PL-B8MK` behind `PL-LPLD` and `PL-CTD7` —
which also unblocks `PL-8PSW`, whose overlay needs the trunk-and-branches
structure and nothing about bookmarks — or it stays open until a bookmark can
be forked, and `PL-8PSW` and `PL-Z3W6` wait with it.

**What proved the code half, and why this item carries no `verify:` today.**
The command is:

```
uv run pytest tests/integration/test_controller.py && grep -q 'def test_a_case_forks_at_every_instant_the_trunk_offers' tests/integration/test_controller.py
```

It was run before being recorded and seen to fail for the right reason: against
`origin/main`'s copy of that file the pytest half passes its 90 tests and the
`grep` finds nothing, so the pair exits 1. It is *not* in `verify:` while this
item is open, because it passes on this branch and `docket check --verify`
rightly errors on an open item whose command already passes — an item whose
command passes has either landed and should close, or proves nothing. Neither
is true here: it proved the code half exactly, and what is open is the scope
answer above. `not-delegable:` is what the store has for work no command can
prove, and a decision is that. If the answer closes this item on the
control-event half, this command becomes its `verify:` in the same commit.

**Captured this session and not fixed here:** `PL-B8MK` (the bookmark routes),
`PL-9KP5` and `PL-4K9V` (`PL-2FM6`'s unswept sample-store prose in
`docs/ARCHITECTURE.md` and `app/formatting.py`), `PL-XJ37` (nothing lets a
learner take a fork or select between runs), `PL-NC62` (the settings-mismatch
refusal names one cause for every failure), `PL-LLBV` (the whole-step guard and
a typed time).
