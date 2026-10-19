---
id: PL-M3M2
title: dashboard_frame.setting_readouts' ValueError for a control that can offer no setting, raised inside _apply_setting's deferred refresh, escapes the slot with no halt stated, since only apply() is inside the try; unreachable with shipped loaders, which refuse such a range at build (found reviewing PL-85LJ)
priority: P3
effort: S
status: done
classes: defect
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/run_view.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-12
closed: 2026-10-19
pr: 1675
payoff: A dial whose readouts cannot be built stops the run and says so on screen, instead of leaving it reading Paused with only a console traceback.
verify: grep -q 'def test_a_drag_whose_readouts_refuse_halts_the_run' tests/integration/test_simulation_view.py
---

**Problem.** dashboard_frame.setting_readouts' ValueError for a control that can offer no setting, raised inside _apply_setting's deferred refresh, escapes the slot with no halt stated, since only apply() is inside the try; unreachable with shipped loaders, which refuse such a range at build (found reviewing PL-85LJ)

**Reproduced 2026-10-17** (triage), with `run_view.setting_readouts`
monkeypatched to raise the `ValueError` it documents, then the fresh-gas-flow
dial dragged on a paused run: the toolkit printed a traceback ending in the
`ValueError`, the status word still read "Paused", the controller was not
failed and no banner was written. The raise leaves
`_refresh_against_last_frame` -> `refresh` -> `_write_settings`, outside the
`try` that holds only `apply()` and outside `_snapshot_for_a_control`'s
gate. Script: `scratchpad/ui-a/test_repro_ui_a.py::test_m3m2`.

**Why it matters.** A raise escaping a slot is the hidden failure
`PL-V2HC` removed from this method's snapshot read: the setting is applied
and nothing on screen says the run can no longer be presented. **Not
reachable with shipped data, which is what sets the band:** `setting_readouts`
raises only for a non-positive MAC or a control whose accepted range holds
no step of its resolution. Every shipped agent's MAC is positive, and the
one shipped machine (`data/machines/reference_circle_system.json`) declares
no deliverable range at all, so the 0.0 to 10.0 L/min envelope stands. The
title's "refuse such a range at build" is narrower than that: the circuit
refuses only a machine range sharing *no* flow with the envelope
(`BreathingCircuit._require_the_two_flow_claims_overlap`), so a future
profile declaring, say, 0.21 to 0.29 L/min would build and reach this. Until
one ships it takes new data first, and the failure is then loud in the
console rather than a plausible value, so `defect` at `P3`.

**Done when.** A raise out of `_apply_setting`'s deferred refresh halts the
run through `_halt_run`, so the status word, the transport and the banner
state the halt before any re-raise - `present_halt`'s own dial write may
still raise after them, as `test_a_halt_is_stated_before_its_dials_are_written`
already accepts. A test, `test_a_drag_whose_readouts_refuse_halts_the_run` in
`tests/integration/test_simulation_view.py`, drags a dial with
`setting_readouts` refusing and asserts "Stopped - simulation error", a
failed controller and a banner naming the `ValueError`.

**Regression check 2026-10-19.** Run with `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/integration/test_simulation_view.py -k <test>` against `src/` as `origin/main` 6fd84bd5 held it. `test_a_drag_whose_readouts_refuse_halts_the_run` fails on the code before the fix at `assert controller.has_failed is True`.
