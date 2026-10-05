---
id: PL-1MGB
title: app/controller.py keeps its own copy of the vaporizer maximum beside the circuit's, so since PL-BBMG a maximum edited between a trunk and its branch is named twice in _disagreements_with's refusal, once from the settings record and once from the display references; read it off the circuit instead
priority: P3
effort: S
status: ready
classes: defect, refactor
feature: scenario-branching
touches: src/anesthesia_sim/app/controller.py, tests/integration/test_controller.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-05 triage pass
added: 2026-10-04
payoff: a branch refused over an edited vaporizer maximum names the one difference once, and the dial's maximum on screen is the one the core enforces rather than a second read of the file
verify: grep -q 'def test_a_vaporizer_maximum_edited_before_a_branch_is_named_once' tests/integration/test_controller.py
---

**Problem.** `SimulationController._build_state` stores
`agent_parameters.max_delivered_concentration_percent` as
`_max_delivered_concentration_percent` (`app/controller.py`), and `snapshot()`
hands that copy out as the snapshot's maximum - the dial's top
(`simulation_view.py`) and the MAC axis's (`dashboard_frame.py`). The circuit
holds its own, read from the same file by `AgentUptakeSystem.for_agent`, and
since `PL-BBMG` `equation_settings()` carries the circuit's into
`UptakeEquationSettings.max_delivered_concentration_percent`. So
`_disagreements_with`, which compares every settings field and then the
agent's "four displayed references", compares the maximum twice: a maximum
edited between a trunk and its branch is named twice in one refusal. Read it
off the circuit instead, and the second comparison has nothing left to compare.

**Reproduced 2026-10-05.** `_trunk_with_two_changes()` from
`tests/integration/test_controller.py`, with `load_agent_parameters` in both
`core.uptake_system` and `app.controller` returning sevoflurane at a 9.0%
maximum, then `resumed_at` the last segment's opening, under `uv run python -c`:
`SimulationConfigurationError: a branch at 60.0 s would be rebuilt from values
this run did not hold there, ... max_delivered_concentration_percent is 8.0 in
this run and 9.0 on the branch; max_delivered_concentration_percent is 8.0 in
this run and 9.0 on the branch` - one disagreement, named twice.

**Why it matters.** The refusal exists to name each value that differs
(`PL-NC62`), and one difference read as two sends its reader looking for a
second edit that was never made. The copy is the cause and the larger half: the
maximum a learner sees on the dial and the axis is a second read of the file,
not the one the core enforces, and only the build sequence keeps the two equal.
No supported setting reaches the doubled refusal - it needs a data file edited
between a trunk and its branch - which is why this is not top-band work.

**Done when.** `snapshot()` reads the maximum off the circuit,
`_max_delivered_concentration_percent` is gone, and `_disagreements_with`
compares the maximum once, through the settings record, with its docstring's
count of displayed references corrected to three.
`test_a_vaporizer_maximum_edited_before_a_branch_is_named_once` in
`tests/integration/test_controller.py`, beside
`test_a_branch_rebuilt_under_another_mac_is_refused`, edits the maximum as
above and asserts the refusal names it exactly once; it fails on today's tree.
