---
id: PL-XRN8
title: A setting written onto the core past SimulationController moves the steps but not the run's definition: system.set_cardiac_output or another core setter called past the controller changes what the steps run at, but the controller records no change, so the readouts (from the steps) and the chart (from the definition) disagree until Reset
priority: P1
effort: S
status: done
classes: defect, safety
feature: cardiac-output-write-consistency
milestone: v0.5.29
touches: src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core/uptake_system.py, docs/MODEL.md, tests/integration/test_controller.py, tests/integration/test_simulation_view.py
added: 2026-10-18
closed: 2026-10-18
pr: 1574
payoff: a setting that reaches the core without the controller recording it halts the run with a banner, instead of letting the readouts and the chart show two different runs
verify: grep -q 'def test_a_setting_written_onto_the_core_past_the_controller_refuses_the_next_step' tests/integration/test_controller.py && grep -q 'def settings_key' src/anesthesia_sim/core/uptake_system.py
---

**Problem.** A setting written onto the core past SimulationController moves the steps but not the run's definition: system.set_cardiac_output or another core setter called past the controller changes what the steps run at, but the controller records no change, so the readouts (from the steps) and the chart (from the definition) disagree until Reset

**Why it matters.** The readouts come from the steps, which run at whatever the
core holds. The chart comes from the run definition, which holds only the
settings `SimulationController` recorded. A setting written onto the core past
the controller makes the two describe different runs, and a reader comparing a
readout with the curve beside it has no way to know. `CLAUDE.md`'s
safety-critical standard prefers an obvious failure to that.

**How reachable it is, checked 2026-10-18** on `PL-HQF5`'s branch
(`origin/claude/project-thread-va33zk`, pull request 1537). Nothing in `src/`
writes to the core past the controller. The view calls only the controller's
four setters, and `ruff check --select SLF001 src` finds no access to the
controller's private `_state` (its eight findings are all in
`app/qt_chart.py`, on pyqtgraph and legend-swatch internals). Only tests reach
the core directly. So this is latent: a guard for the next caller, not a fix
for one a learner can reach.

**What was built.** Before each step, `SimulationController.advance()` compares
the core's settings with the settings the run definition last recorded. A
mismatch refuses the step, and the view halts the run with a banner, on the
last step at which the readouts and the chart agree.

- `AgentUptakeSystem.settings_key()` is new and public. It is the settings
  half of the propagator cache key, which already had to be a bijection of
  `equation_settings()`. `_propagator_cache_key()` now prepends the step to it,
  so the two cannot drift apart. Measured 2026-10-18: building the key costs
  1.8 us, building `equation_settings()` 11.0 us, and a step 49.2 us. The check
  therefore adds about 4% to a step.
- The controller notes the key at each of the four places the definition takes
  settings: where a run is built, where a branch opens, at Reset, and at a
  recorded control change. A missed place would halt an ordinary run, which
  the existing controller and view suites would show.
- Where the settings on the core fail the record's own checks, the record's
  refusal is raised instead, because its message names the two values that
  disagree. That keeps `PL-M4M0`'s and `PL-VCP4`'s stale-fraction messages.
- The check is not run in the controller's setters. Run there, it would refuse
  a perfusion fraction written past its guard before `_record_control_change`
  could write the setting back, which `PL-VCP4`'s tests hold.

**What is left, deliberately.** A setting written past the controller while
the run is paused, followed by a setting changed through the controller, is
absorbed: `_record_control_change` records the whole settings record, so the
definition matches the core again and no halt follows. The readouts and the
chart then agree. Only the control timeline lacks an entry for the change
nobody made through a control. No learner can reach this, and closing it
would mean checking in the setters, which the paragraph above rules out.

**Done when.** A step after a setting written onto the core past the controller
is refused, on the trunk and on a branch; the view halts the run and says why;
and Reset starts a run at the setting the core holds.

**Regression proof, 2026-10-18.** With this branch's tests and the source
before the fix (`git stash push src`), `pytest -p no:randomly
tests/integration/test_controller.py tests/integration/test_simulation_view.py
-k "past_the_controller or past_its_controller"` fails all seven new tests: six
with `Failed: DID NOT RAISE SimulationExecutionError`, and the view test with
`assert controller.has_failed is True` / `assert False is True`.
