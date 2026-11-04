---
id: PL-WV74
title: The halt-gate check misses a run-touching slot that is connected from outside RunView and SimulationView, or held in a variable before it is connected
priority: P3
effort: S
status: done
classes: test
feature: defect-review-2026-10
milestone: v0.6.15
touches: tests/integration/test_simulation_view.py
added: 2026-10-25
closed: 2026-11-03
pr: 1986
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

**Built, 2026-11-03.** `_outside_bypasses` parses every module under `src/anesthesia_sim/app/` outside the two views' own classes. It reports a callback whose attribute name is a view method that does not pass the gate, in any position a slot is passed. The match is by name alone, because the source does not say which object the name before the dot holds. A `self.<name>` callback is the enclosing class's own method and is not matched. A lambda that calls a view method from outside is not judged, and the docstring says so. `_followed` follows a local variable to every value the enclosing function assigns to it, in both checks. A name assigned by a loop, a `with` or an unpacking is not followed. On `main` today the outside check finds 48 connections and no view method among them, so it reports nothing, as the brief expected. The synthetic view gained one gated and one ungated variable, and `_wire_from_outside` holds a gated and an ungated method connected directly, through a variable, and through `partial`.

**Blind review, 2026-11-03.** One generalist pass found three gaps, all fixed on the branch. A name bound some other way as well, such as a parameter or a loop target, was judged only by its plain assignments, so `for slot in (self._ungated,): connect(slot)` passed where `main` reported it; such a name now also stands for itself. Skipping a `partial(...)` call's own arguments lost a `partial` stored on an attribute and later connected; the arguments are judged again, and `functools.partial` is unwrapped too. A conditional expression and a list held in a variable were not followed; both now are. Still out of reach: a callback another class stores as `self._callback = view._apply` and connects later, and a lambda from outside that calls a view method.
