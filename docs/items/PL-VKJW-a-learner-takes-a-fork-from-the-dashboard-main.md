---
id: PL-VKJW
title: A learner takes a fork from the dashboard: main() builds a BranchedCase, SimulationView gains a run added after construction, and a control offers fork_points_s
priority: P2
effort: M
status: done
classes: feature, ux
feature: scenario-branching
touches: src/anesthesia_sim/app/main.py, src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/theme.py, docs/ARCHITECTURE.md, tests/integration/test_simulation_view.py, tests/integration/test_dark_appearance.py, tests/unit/test_dashboard_frame.py, tests/unit/test_bootstrap.py
added: 2026-09-20
closed: 2026-09-20
payoff: makes v0.5.0's Goal reachable - a learner can actually take the branch, instead of forking staying machinery no shipped entry point calls
verify: grep -q 'def test_taking_a_fork_adds_the_branch_to_the_dashboard' tests/integration/test_simulation_view.py
---

**Problem.** A learner takes a fork from the dashboard: main() builds a BranchedCase, SimulationView gains a run added after construction, and a control offers fork_points_s

**Why it matters.** `ROADMAP.md`'s v0.5.0 Goal states the end state as "a
learner runs a case, marks the decision point, **forks there**, manages the two
branches differently, and reads both on one time axis". Every mechanism under
that sentence has shipped and nothing calls any of it. `PL-TFX5` built
`BranchedCase`, `PL-J2TD` built the resumption a fork opens into, `PL-B9PY`
decomposed `SimulationView` so two runs render, and `PL-8PSW` drew the overlay -
yet a learner reaches none of them, so the milestone could close with every
other Required-scope entry done and forking still unreachable. That is the gap
`PL-XJ37` recorded and the project owner closed on 2026-09-20 by naming this
work as v0.5.0 scope.

**What the code says, measured 2026-09-20.**

- `main()` in `src/anesthesia_sim/app/main.py` builds one bare
  `SimulationController` and hands it over as `SimulationView((controller,))`.
  Nothing in `src/` constructs a `BranchedCase` at all - `grep -rn BranchedCase
  src/ --include='*.py'` matches only `app/controller.py`, where it is defined.
- `BranchedCase` is complete and tested: `trunk`, `branches` (stable order),
  `fork_points_s` and `fork_at` are all on it in `app/controller.py`, and
  `tests/integration/test_controller.py` covers twelve fork behaviours against
  them.
- `SimulationView.__init__` freezes the run set - `self._runs = tuple(RunView(
  controller, self) for controller in controllers)` - and the comment beside
  the legends' `set_run_count` calls states the invariant outright: "Said once,
  at construction, because the count cannot change while a dashboard is alive".
  Those two calls, the per-run `set_run_name` and `_build_page()` all run once
  off that tuple. There is no `add_run` or `set_runs` path.
- `MAX_DISPLAYED_RUNS` in `app/dashboard_frame.py` is 2, and stays 2.

So the dashboard can *render* a trunk and a branch if handed both at
construction, and cannot come to hold a branch taken during a session.

**What this item builds.** The shape the project owner chose (option C,
2026-09-20):

1. `main()` builds a `BranchedCase` and the dashboard is opened over its trunk.
2. `SimulationView` gains a path that adds a `RunView` after construction,
   which means the invariant quoted above is replaced rather than worked
   around: the legends' run count, the run naming and the page layout all have
   to follow the addition. Still capped at `MAX_DISPLAYED_RUNS`.
3. One control offers `BranchedCase.fork_points_s` and calls `fork_at`, and the
   branch it returns is what step 2 adds.

The learner-visible result is the Goal sentence verbatim: run a case, mark the
decision point, fork there, manage the two branches differently, read both on
one time axis.

**Not in scope, and already written into `ROADMAP.md` § "Explicitly out of
scope for v0.5.0": the run selector.** Choosing *which two* of N runs are
displayed is deferred, and with it comparing one branch directly against
another rather than each against the trunk, and returning to a branch the
learner has left. The display is capped at two runs either way, so a selector
buys the *choice* of pair rather than more curves.

**The consequence that follows, decided here rather than discovered in the
pull request: refuse a second fork while a comparison is shown.** With no
selector, a learner who forks twice has no way to say which branch is
displayed, and silently replacing the shown branch while the first lives on
inside `BranchedCase` is hidden state of exactly the kind
`SimulationController.start()`'s own docstring argues against. So the fork
control is refused - visibly, in the same disabled-and-hidden form the
transport already uses, with the reason readable - while two runs are on the
chart, and Reset is how the learner gets back to one. One comparison at a
time.

**The agent-dropdown disposition, which is also `PL-QRD1`'s answer.** A branch
shown in a `RunView` gets the same agent dropdown the trunk does, and
`SimulationController.set_agent` refuses on a branch (`PL-TFX5`): a branch
carries the agent of the case it continues. The refusal reaches the ordinary
refused-setting path, so nothing breaks - but a control that always refuses is
a control presenting itself as working.

**A branch's `RunView` shows the running-agent chip instead of the dropdown**,
using the `setDisabled(locked)`-beside-`setHidden(locked)` pair
`RunView._write_transport` already writes. That needs a branch test to reach
`dashboard_frame.transport`, which today computes
`selector_locked=snapshot.is_running` and sees only a `SimulationSnapshot`;
`SimulationController.opened_from` is the fact, and `chart_frame._run_frame`
already reads it to mark the branch point. Whether the snapshot carries it or
`transport` gains a second argument is the implementing session's call; what is
decided is the behaviour.

**The half the chip does not cover, found while filing this item on
2026-09-20: the *trunk's* selector.** The disposition above answers the branch,
where `set_agent` refuses and the control is therefore a lie. It does not
answer the trunk, where `set_agent` *succeeds* - and that is the case
`PL-QRD1` actually describes, made reachable for the first time by this item.

Traced through the shipped code: with a branch displayed and the trunk paused,
`dashboard_frame.transport` computes `selector_locked=snapshot.is_running`, so
the trunk's dropdown is live. Choosing another agent reaches
`RunView._confirm_new_case`, which asks before discarding a recorded run and
names the count of control changes about to be lost - it says nothing about the
branch, because nothing told it there is one. On confirmation the trunk
restarts under the new agent, `BranchedCase` goes on listing a branch of a run
that no longer exists, and `assemble_chart_frame` then refuses the frame
because two agents cannot share one MAC axis, so `_halt_every_run` fails
*both* runs over an input to one of them. That is `PL-QRD1`'s failure ordering
exactly: the controller switches first and the refusal arrives afterwards.

**So this item may not land the trunk's selector as it stands**, or it ships a
control that destroys the case a comparison is of. Two answers are defensible
and the project owner has the point:

- **Prevent** - lock the trunk's selector too while two runs are shown, which
  is the behaviour `PL-QRD1` asked for and makes the rule on screen simply
  "no agent change while comparing", with Reset as the way out. It is also the
  gesture already chosen for a second fork, so it adds no mode.
- **Warn** - keep the selector live and grow `_confirm_new_case`'s dialog a
  second clause about the branches it would orphan. The existing confirm flow
  is the precedent for this, and a dialog enumerating two kinds of loss is
  where readers click through.

`CLAUDE.md`'s expert-review standard prefers interfaces that prevent an error
over interfaces that warn after one, so **prevent** is the recommendation. Under
it `PL-QRD1` closes against this item rather than after it; under **warn** it
stays open and needs a place in v0.5.0's scope, since this item is what makes
its defect reachable.

**Done when.**

1. `uv run anesthesia-sim` opens a dashboard over a `BranchedCase`, and a
   learner can take a fork from it and see the branch drawn beside the trunk on
   one time axis.
2. A second fork is refused while two runs are shown, visibly and with its
   reason readable, rather than replacing the displayed branch.
3. A branch's `RunView` shows the running-agent chip in place of the agent
   dropdown, so no control on screen refuses every input it accepts.
4. Tests cover all three, including the run added after construction, and
   `make check` passes.
