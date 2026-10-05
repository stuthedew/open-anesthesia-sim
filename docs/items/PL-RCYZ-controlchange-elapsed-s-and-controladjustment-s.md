---
id: PL-RCYZ
title: ControlChange.elapsed_s, and ControlAdjustment's started_at_s and ended_at_s, are annotated float though every one is taken from a CaseInstant - SimulationState.elapsed_s - so the control record is the one holder of a case instant PL-CN5S left untyped (app/control_record.py and app/control_timeline.py were outside its touches)
priority: P3
effort: S
status: ready
classes: refactor
feature: parse-dont-validate
touches: src/anesthesia_sim/app/control_record.py, src/anesthesia_sim/app/control_timeline.py, tests/unit/test_control_timeline.py, tests/unit/test_dashboard_frame.py, tests/unit/test_chart_frame.py, tests/integration/test_qt_chart.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-04 triage pass
added: 2026-10-04
payoff: every holder of a case instant carries the checked type, so no recorded control change or adjustment can be stamped with an instant outside the supported run length
verify: grep -q 'def test_a_recorded_change_and_an_adjustment_refuse_an_instant_not_built_as_one' tests/unit/test_control_timeline.py
---

**Problem.** ControlChange.elapsed_s, and ControlAdjustment's started_at_s and ended_at_s, are annotated float though every one is taken from a CaseInstant - SimulationState.elapsed_s - so the control record is the one holder of a case instant PL-CN5S left untyped (app/control_record.py and app/control_timeline.py were outside its touches)

**Reproduced 2026-10-04, at triage.** On Python 3.14.7, against `main` at
`8cc0698d`,
`uv run python -c "from anesthesia_sim.app.control_record import CONTROL_INPUT_UNITS, ControlChange, ControlInput; from anesthesia_sim.app.control_timeline import ControlAdjustment, format_adjustment, group_adjustments; change = ControlChange(elapsed_s=1e9, adjustment=1, control=ControlInput.FRESH_GAS_FLOW, previous_value=6.0, new_value=2.0, unit=CONTROL_INPUT_UNITS[ControlInput.FRESH_GAS_FLOW]); print(type(change.elapsed_s).__name__, format_adjustment(group_adjustments([change])[0])); print(ControlAdjustment(ControlInput.FRESH_GAS_FLOW, float('nan'), -60.0, 6.0, 2.0, 'L/min', 1))"`
printed `float 277777h46m40s · Fresh gas flow 6.0 L/min -> 2.0 L/min`, then a
`ControlAdjustment` holding `started_at_s=nan` and `ended_at_s=-60.0`. Both
records were built from bare floats, one a billion seconds past the 24 h
supported run length and rendered as the line the control-change panel lists,
the other not a number at all; `format_elapsed` refuses the `nan` and the
negative only when a line is drawn. The premise holds: a
`SimulationController` started and given
`set_fresh_gas_flow(FreshGasFlow(2.0))` recorded a change whose `elapsed_s` is
a `CaseInstant`, and `group_adjustments` kept that type on the adjustment, so
every instant `src/` hands these records is already one. Four test modules
build either record from a bare number: `tests/unit/test_control_timeline.py`,
`tests/unit/test_dashboard_frame.py` and `tests/unit/test_chart_frame.py`
through one helper each, and `tests/integration/test_qt_chart.py` at one site.

**Why it matters.** No wrong value is shown today, since the controller's one
`ControlChange` takes `self._state.elapsed_s` and the timeline passes it
through. What the `float` annotation costs is the check: a caller building a
record itself, such as a test or a notebook, can stamp a change or an
adjustment with an instant outside the supported run length and see it listed
in the control-change panel with no refusal. And a reader of
`app/control_record.py` meets a `float` where every other holder of a case
instant says `CaseInstant`, the one gap `PL-CN5S` left in this feature's
pattern.

**Done when.** `ControlChange.elapsed_s` and `ControlAdjustment`'s
`started_at_s` and `ended_at_s` are annotated `CaseInstant`, and each record
refuses one not built as a `CaseInstant` at construction through
`require_case_instant`, the existing case-instant check, so a bare `float` is
refused with its `TypeError` naming the field. The controller's
`ControlChange` and `group_adjustments` hand the state's instant through
unchanged, and the four test modules above build the instant as a
`CaseInstant`. A test in `tests/unit/test_control_timeline.py` named
`test_a_recorded_change_and_an_adjustment_refuse_an_instant_not_built_as_one`
pins it.
