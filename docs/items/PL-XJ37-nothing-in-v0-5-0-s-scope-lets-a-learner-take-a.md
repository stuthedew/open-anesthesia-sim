---
id: PL-XJ37
title: Nothing in v0.5.0's scope lets a learner take a fork or select between runs, and SimulationView's run set is fixed at construction
status: untriaged
added: 2026-09-14
---

**Problem.** Nothing in v0.5.0's scope lets a learner take a fork or select between runs, and SimulationView's run set is fixed at construction

**Why it matters.** `ROADMAP.md`'s v0.5.0 Goal states the end state as "a
learner runs a case, marks the decision point, **forks there**, manages the two
branches differently, and reads both on one time axis", and its out-of-scope
list allows that "N branches may exist and be **selected between**". Neither
act has an item. The milestone could close with every Required-scope entry done
and no way for a learner to take a fork.

**What the eighteen Required-scope entries cover.** `PL-LPLD` creates, lists
and removes bookmarks; `PL-8PSW` overlays two branches that already exist;
`PL-1XPX` decides what the readouts say while two are shown. The fork itself is
`PL-J2TD` (the resumption) and `PL-TFX5` (the trunk-and-branches structure),
and both declare `touches` that exclude `simulation_view.py` and `main.py` —
correctly, since both are internal by design. Nothing picks up where they stop.

**What the code says, measured 2026-09-14.** `SimulationController` is
constructed in exactly two places in `src/`: `main.build_app` builds the trunk,
and `resumed_at` builds a branch. `resumed_at` has no production caller at all —
every call site is a test. `SimulationView.__init__` takes
`controllers: Sequence[SimulationController]` and freezes `self._runs` at
construction, with `MAX_DISPLAYED_RUNS = 2` and no add-run path: the page tree,
the per-run asyncio tasks and the chart's series list are each built once from
that tuple. So the dashboard can *render* a trunk and a branch if handed both
at startup, and cannot come to hold a branch taken during a session.

**What it would take.** `main.build_app` builds a `BranchedCase` rather than a
bare controller; `SimulationView` takes the case and a displayed-pair selection
instead of a fixed sequence, and gains a path that adds a `RunView` after
construction; and a control somewhere offers `BranchedCase.fork_points_s` and
calls `fork_at`. The first two are `simulation_view.py` work and sit naturally
beside `PL-8PSW`; whether they belong to it or to an item of their own is the
question here.

**A related edge, worth deciding with it.** A branch shown in a `RunView` gets
the same agent dropdown the trunk does, and `set_agent` now refuses on a branch
(`PL-TFX5`): a branch carries the agent of the case it continues. The refusal
reaches the view's ordinary refused-setting path, so nothing breaks — but a
control that always refuses is a control presenting itself as working, which is
the hidden mode this project's own `start()` docstring argues against.
