---
id: PL-WV74
title: The halt-gate check misses a run-touching slot that is connected from outside RunView and SimulationView, or held in a variable before it is connected
priority: P3
effort: S
status: ready
classes: test
feature: defect-review-2026-10
touches: tests/integration/test_simulation_view.py
added: 2026-10-25
payoff: a dashboard slot that bypasses the halt gate fails a test even when it is connected from another module or through a variable
verify: grep -q 'def test_the_halt_gate_check_finds_a_slot_connected_from_outside_the_view' tests/integration/test_simulation_view.py
---

**Problem.** The halt-gate check misses a run-touching slot that is connected from outside RunView and SimulationView, or held in a variable before it is connected

`test_every_slot_that_touches_a_run_passes_the_halt_gate` in `tests/integration/test_simulation_view.py` reads only the source of `RunView` and `SimulationView`. Two kinds of bypass are therefore invisible to it, and `_halt_gate_bypasses` says so in its docstring:

- A function or class outside the two views connects a signal to a view method that is not gated, or to a lambda that reads or changes a run.
- A callback is assigned to a variable first and passed on later, as in `callback = self._apply; button.clicked.connect(callback)`. The check judges the name `callback` and not the method that it holds.

The coverage review of `PL-HJKN` found both on 2026-10-25. No code does either today.

**Why it matters.** PySide6 prints an exception raised inside a slot and then carries on, so a slot that bypasses the gate and raises leaves the run reading "Running" or "Paused" with no halt on screen. That is stale state on a clinical display. `PL-HJKN` was meant to make the next such slot fail a test, but a slot written in either of these two shapes still passes. Six separate reviews found this defect one slot at a time before the gate existed (`PL-YK2V`, `PL-7DJK`, `PL-V2HC`, `PL-08SS`, `PL-F2T2`, `PL-M3M2`).

**Done when.** The check also reads every module under `src/anesthesia_sim/app/` for callbacks that resolve to a method of either view. It follows a local variable back to the callback assigned to it. The synthetic class in `test_the_halt_gate_check_finds_each_way_around_the_gate`, or a second synthetic module, holds one bypass of each shape, and `test_the_halt_gate_check_finds_a_slot_connected_from_outside_the_view` fails if the check misses either one. The sentence about the limit in `_halt_gate_bypasses`'s docstring is removed or narrowed to what is still out of reach.
