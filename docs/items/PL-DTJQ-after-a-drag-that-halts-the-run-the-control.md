---
id: PL-DTJQ
title: After a drag that halts the run, the control-change panel lists the pre-drag record while the run holds a different one: _control_timeline_text is written only in refresh, from snapshot.control_timeline and the frame's undrawn marks, and no frame of a run whose snapshot refuses draws (found reviewing PL-85LJ)
priority: P2
effort: S
status: done
classes: defect, ux
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/controller.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-12
closed: 2026-10-17
pr: 1492
payoff: After a drag halts the run, the control-change panel lists the changes the run actually holds, not the record from before the drag.
verify: grep -q 'def test_a_drag_that_halts_the_run_lists_the_record_the_run_holds' tests/integration/test_simulation_view.py
---

**Problem.** After a drag that halts the run, the control-change panel lists the pre-drag record while the run holds a different one: _control_timeline_text is written only in refresh, from snapshot.control_timeline and the frame's undrawn marks, and no frame of a run whose snapshot refuses draws (found reviewing PL-85LJ)

**Reproduced 2026-10-17** (triage): `_paused_run_with_history()` (fresh gas
flow 4.0 -> 2.0 recorded at 1 min, paused), the alveolar quotient replaced
with 1.0000001 so the snapshot refuses, then the fresh-gas-flow dial dragged
back to 4.0. The run halts ("Stopped - simulation error"); the drag returns
the open adjustment to its starting value, so the controller's
`_control_timeline` is now empty, while the control-change panel still
reads "1m · Fresh gas flow 4.0 L/min -> 2.0 L/min". Script:
`scratchpad/ui-a/test_repro_ui_a.py::test_dtjq`.

**Why it matters.** The control-change panel is the reader's record of what
was done to the run; after this drag it lists a change the run no longer
holds, which is the dial-and-label disagreement `PL-85LJ` fixed for the
dials, one panel over. **Not reachable today:** a drag halts the run only
when its snapshot refuses (`PL-7DJK`, which no supported setting reaches)
or `apply()` raises outside `SimulationConfigurationError`, a latent fault -
so `defect`/`ux` at `P2`, beside `PL-85LJ`'s siblings.

**Done when.** `RunView.present_halt` writes the control-change panel (the
entries and the overflow line) from the run's own record, read through a
`SimulationController` accessor that builds no compartment value - the
record `snapshot().control_timeline` already hands out, as `settings()` does
for the dials - with no undrawn marks, since no frame draws. A test,
`test_a_drag_that_halts_the_run_lists_the_record_the_run_holds` in
`tests/integration/test_simulation_view.py`, repeats the reproduction above
and asserts the panel lists what the controller's record holds.

**Fixed 2026-10-17 under `PL-X7D5`'s second pull request.** `present_halt`
writes the control-change panel through `RunView._write_statement`, from
`record().control_timeline` with no undrawn marks. `record()`, built in
`PL-X7D5`'s first pull request, is the accessor the Done when asks for, so
`controller.py` is unchanged here. The regression test
`test_a_drag_that_halts_the_run_lists_the_record_the_run_holds` repeats the
reproduction and asserts that the panel reads "No settings changed yet in
this run." once the drag has taken the change off the record.
