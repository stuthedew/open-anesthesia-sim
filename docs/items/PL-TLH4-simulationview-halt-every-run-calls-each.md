---
id: PL-TLH4
title: SimulationView._halt_every_run calls each RunView.present_halt in an unguarded loop, and present_halt documents a ValueError, so a raise there skips _restate_fork_panel and _restate_bookmark_panel and leaves both panels on the last frame's state (found reviewing PL-YHR3)
priority: P3
effort: S
status: done
classes: defect, ux
feature: every-control-restates-the-halt
milestone: v0.6.0
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-19 product-defect sweep
added: 2026-10-19
closed: 2026-10-19
pr: 1675
payoff: a halt whose dial write fails for one run still stops every run and restates the branch and bookmark panels, rather than leaving them on the last frame
verify: grep -q 'def test_a_dial_write_that_refuses_on_a_halt_still_restates_every_panel' tests/integration/test_simulation_view.py
---

**Problem.** SimulationView._halt_every_run calls each RunView.present_halt in an unguarded loop, and present_halt documents a ValueError, so a raise there skips _restate_fork_panel and _restate_bookmark_panel and leaves both panels on the last frame's state (found reviewing PL-YHR3)

**Why it matters.** `present_halt` writes the dials last and raises a
`ValueError` when `setting_readouts` cannot build them, which
`test_a_halt_is_stated_before_its_dials_are_written` accepts for that run alone.
Inside `_halt_every_run` the raise also leaves the loop, so a second run is never
told it halted, the branch panel keeps offering a fork over a failed trunk, and the
bookmark panel keeps the last frame's standings. Reproduced 2026-10-19 by setting
`BreathingCircuit.accepted_fresh_gas_flow_range_l_min` to 0.21 to 0.29 L/min, as
that test does, and failing every frame: the raise left the loop before either
panel was restated. No shipped machine declares such a range, so it takes new data
first.

**Done when.** A presentation that raises for one run does not stop the halt path:
every run states its halt, every dashboard panel is restated, the frame is tried,
and only then does the first raise escape. An integration test makes the dial
write refuse with every frame failing and asserts all of that.

**Regression check 2026-10-19.** Run with `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/integration/test_simulation_view.py -k <test>` against `src/` as `origin/main` 6fd84bd5 held it. `test_a_dial_write_that_refuses_on_a_halt_still_restates_every_panel` fails on the code before the fix at `assert here.isHidden() is True`: the raise left the halt path before the branch panel was restated.
