---
id: PL-R3KB
title: Selecting an agent silently discards the running case
priority: P2
effort: S
status: done
classes: defect, ux
feature: teachable-case
milestone: v0.4.0
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/formatting.py, tests/unit/test_simulation_view.py, tests/unit/test_formatting.py, tests/integration/test_controller.py, docs/MODEL.md, README.md, tools/contrast_check.py
added: 2026-08-25
closed: 2026-09-05
pr: 326
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_a_declined_agent_change_leaves_the_run_and_the_selector_untouched' tests/unit/test_simulation_view.py
---

**Problem.** Picking a different agent from the header dropdown destroys the
current run and its whole recorded history, with no confirmation and no
statement that it happened. `SimulationController.set_agent` pauses, then
rebuilds state from scratch at the new agent's 1 MAC; the view calls it
straight from the dropdown's `on_select`. The dropdown is disabled while
running, so this can only happen from a paused run - but a paused run is
precisely when a learner is most likely to browse the selector, and a pause
that has accumulated forty minutes of simulated history is the case with the
most to lose.

**Why it matters.** Discarding the run is the correct behavior - mid-run
switching with residual washout is a separate, harder feature that this model
does not support, and carrying the old agent's dial across would be worse. The
defect is that a destructive action is presented as a mode selector. A control
that reads as "show me this agent" and instead means "throw away this case"
is the surprising-default, hidden-mode failure `CLAUDE.md`'s human-factors
standard exists to prevent, and the loss is unrecoverable: there is no undo
and no saved state. It gets worse over the v0.3.0 milestone, which makes runs
long enough to be worth losing and adds a control-input timeline to lose with
them.

**Where.** `app/simulation_view.py:881` (`_handle_agent_change`) and
`app/controller.py:182` (`set_agent`, whose docstring already records that it
always begins a new run).

**Done when.** Changing agent is an explicit new-case action rather than a
silent side effect of a selector: the user is told that the current run and
its history will be discarded, and confirms, before any state is rebuilt.
Declining leaves the run and the selector both untouched. A test asserts that
a declined switch preserves elapsed time, agent id, and history length.
