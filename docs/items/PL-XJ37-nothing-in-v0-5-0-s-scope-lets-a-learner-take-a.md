---
id: PL-XJ37
title: Nothing in v0.5.0's scope lets a learner take a fork or select between runs, and SimulationView's run set is fixed at construction
priority: P2
effort: M
status: needs-decision
classes: planning, ux
feature: scenario-branching
touches: ROADMAP.md, docs/items
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

**Decision needed.** Whether the learner-facing half of forking - a control that
takes a fork, and a way to select which two runs are shown - belongs to
`PL-8PSW` (overlay two branches on one time axis) or to an item of its own, and
whether v0.5.0's `Required scope` is amended to name it.

This is the project owner's rather than a session's: it changes what v0.5.0
*is*. The milestone is called "the case you can branch", and on the code as it
stands a learner cannot take a branch - so either the scope is incomplete or the
milestone means something narrower than its name, and only the owner can say
which.

**The code claim, verified 2026-09-14.** `SimulationController` is constructed
in exactly two places in `src/`: `main.build_app` builds the trunk, and
`resumed_at` builds a branch. `resumed_at` has no production caller - every call
site is a test. `SimulationView.__init__` takes
`controllers: Sequence[SimulationController]` and freezes `self._runs` at
construction, with `MAX_DISPLAYED_RUNS = 2` and no add-run path. So the
dashboard can *render* a trunk and a branch if handed both at startup, and
cannot come to hold a branch taken during a session.

**What it would take**, so the two options can be priced: `main.build_app`
builds a `BranchedCase` rather than a bare controller; `SimulationView` takes
the case and a displayed-pair selection instead of a fixed sequence, and gains a
path that adds a `RunView` after construction; and a control offers
`BranchedCase.fork_points_s` and calls `fork_at`. The first two are
`simulation_view.py` work sitting naturally beside `PL-8PSW`. `PL-J2TD` and
`PL-TFX5` both declare `touches` that exclude `simulation_view.py` and `main.py`
deliberately, so nothing currently picks up where they stop.

**A related edge, worth deciding in the same breath.** A branch shown in a
`RunView` gets the same agent dropdown the trunk does, and `set_agent` now
refuses on a branch (`PL-TFX5`) because a branch carries the agent of the case
it continues. The refusal reaches the ordinary refused-setting path so nothing
breaks - but a control that always refuses is a control presenting itself as
working, which is the hidden mode this project's own `start()` docstring argues
against.

**Note for whoever answers it:** the Qt port now runs *ahead* of v0.5.0, and it
rewrites `simulation_view.py` wholesale. Building the selection on Flet first
would be building it where the port deletes it.

**Done when.** `ROADMAP.md` says whether taking a fork and selecting between runs
is inside v0.5.0, and if it is, the work is named - either folded into `PL-8PSW`
with that entry's scope widened to say so, or filed as its own item and added to
the `Required scope` list. The agent-dropdown edge above is disposed of in the
same answer rather than left to be rediscovered.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Still real, and the reason it
gave for deferring has expired.** The gap is unchanged:
`SimulationView.__init__` still takes `controllers: Sequence[...]` and freezes
`self._runs` at `simulation_view.py:181` with no `add_run` or `set_runs` path,
`MAX_DISPLAYED_RUNS` is 2 at `dashboard_frame.py:120`, v0.5.0's eighteen
`Required scope` entries contain neither act, and `ROADMAP.md:88` still cites
this item as live fact. `status: needs-decision` is correct.

Three corrections. The brief defers on "the Qt port now runs *ahead* of
v0.5.0 … building the selection on Flet first would be building it where the
port deletes it" - the port **shipped** in v0.4.26, so that reason is spent and
the item is stronger rather than weaker for it. `main.build_app` no longer
exists; the equivalent is `main.py:32-33`, `SimulationView((controller,))`
inside `main()`. And `resumed_at` does have a production caller now,
`controller.py:1261` inside `BranchedCase` - though nothing in `src/`
constructs a `BranchedCase`, so the gap one level up is exactly as described.
