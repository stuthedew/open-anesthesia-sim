---
id: PL-NJPB
title: A vaporizer setting cannot be recovered as dialled from RunSegment.settings: fraction times 100 misses the percent for 126 of the dial's 801 settings
priority: P3
effort: M
status: done
classes: defect, anticipated
feature: scenario-branching
touches: docs/MODEL.md, docs/machine-survey.md, src/anesthesia_sim/app/control_record.py, src/anesthesia_sim/app/control_timeline.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/dashboard_frame.py, src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/concentration.py, src/anesthesia_sim/core/governing_equations.py, src/anesthesia_sim/core/run_definition.py, src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/validation.py, tests/integration/test_controller.py, tests/integration/test_qt_chart.py, tests/integration/test_qt_rendering.py, tests/integration/test_qt_widgets.py, tests/integration/test_sevo_controller.py, tests/integration/test_simulation_view.py, tests/reference/test_canonical_evaluation.py, tests/reference/test_circuit_wash_in.py, tests/reference/test_control_resolution.py, tests/reference/test_coupled_dynamics.py, tests/reference/test_late_washout_against_published_fits.py, tests/reference/test_multi_agent.py, tests/reference/test_published_wash_in_and_elimination.py, tests/reference/test_sevo_patient.py, tests/unit/test_bookmarks.py, tests/unit/test_chart_frame.py, tests/unit/test_circuit.py, tests/unit/test_compartment_primitives.py, tests/unit/test_concentration.py, tests/unit/test_control_timeline.py, tests/unit/test_dashboard_frame.py, tests/unit/test_formatting.py, tests/unit/test_governing_equations.py, tests/unit/test_resume_at.py, tests/unit/test_run_definition.py, tests/unit/test_simulation.py, tests/unit/test_state_capture.py, tests/unit/test_uptake_system_failure.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-28 triage pass
added: 2026-09-27
closed: 2026-10-01
pr: 1274
payoff: a recorded segment gives back the vaporizer percent the learner dialled, so save and load can restore it exactly
verify: grep -q 'def test_a_recorded_segment_gives_back_each_vaporizer_percent_as_dialled' tests/unit/test_run_definition.py
---

**Problem.** A vaporizer setting cannot be recovered as dialled from RunSegment.settings: fraction times 100 misses the percent for 126 of the dial's 801 settings

**Found by `PL-SM5V`, 2026-09-27, and not worked there.** That item made a
recorded segment hold each flow in the litres per minute that was set, because
dividing by sixty does not run backwards. The vaporizer has the same shape one
layer up: the dial is set in percent and the settings hold
`delivered_partial_pressure_fraction`. Measured in the container's Python:
`p / 100 * 100 != p` for 13 of the 81 settings from 0.0 to 8.0 % at 0.1 %
(0.9, 1.7, 1.8, 3.3 to 3.7, 6.6, 6.8, 7.0, 7.2 and 7.4); 0.9 reads back as
0.9000000000000001. Rebuilding settings from the fraction is exact, since the
compartment holds the fraction too, so nothing inside `core/` is affected.
What is not recoverable is the percent the learner dialled, which a save and
load format (planned item 9) or anything else recovering the dial from a
segment would need. Where the percent becomes a fraction was not located;
start by finding that conversion and whether the control timeline records the
percent as dialled.

**Why it matters.** A save and load format (planned item 9), or anything
else restoring the dial from a recorded segment, would restore
0.9000000000000001 % where the learner dialled 0.9 %. Nothing reads it back
today, hence `anticipated`, but each recorded shape built on the fraction before
then adds to what has to change.

**Where, located at triage, 2026-09-28.** `src/anesthesia_sim/app/controller.py`
builds the setting's fraction (its `delivered_partial_pressure_fraction=Fraction(`
construction), and `core/uptake_system.py` converts the agent's percent with
`fraction_from_percent`. Whether the control timeline records the percent as
dialled was not checked.

**Located, 2026-10-01, and the open question answered.** The percent
becomes a fraction in the interface, before the controller sees it:
`RunView._handle_delivered_concentration_change` in
`src/anesthesia_sim/app/run_view.py` takes the dial's percent - the slider
position over a hundred, since `CONCENTRATION_DISPLAY_DECIMALS` is 2 - and
passes it through `dashboard_frame.delivered_fraction`, which is
`fraction_from_percent(Percent(percent))`, so the controller is handed the
fraction. Every holder after that takes the fraction:
`BreathingCircuit.delivered_partial_pressure_fraction` in `core/circuit.py`;
`UptakeEquationSettings`, which `AgentUptakeSystem.equation_settings()` copies
from the circuit and `RunDefinition` records per segment; and the control
timeline, which `SimulationController.set_delivered_partial_pressure_fraction`
writes as `ControlInput.DELIVERED` with the circuit's fraction and
`control_timeline.format_control_value` reads back through
`format_percent(Fraction(value))`. So the timeline does not hold the percent
as dialled either. A fork is exact today only because `_branch_from` rebuilds
from the timeline's fraction and compares it with the segment's fraction.

**The dial steps at 0.01 %, so the count was low.** The 0.1 % grid above is a
subset of the dial's: re-measured, the same 13 of its 81 settings miss, and
over the dial's own 801 settings from 0.00 to 8.00 % **126** miss, the first
at 0.23 %. The title and "Done when" now name the dial's step.

**What recovering it costs.** The percent has to reach the record, so the
controller has to receive it and the circuit and the settings have to hold
it. That is 122 writer call sites (setter calls and constructor keywords) in
29 files: 11 in `core/circuit.py`, `core/uptake_system.py`,
`app/controller.py` and `app/run_view.py`, and 111 in 25 test files - plus
`core/governing_equations.py`, `app/dashboard_frame.py`,
`app/control_timeline.py`, `app/control_record.py`'s docstring and
`docs/MODEL.md` § "Concentrations". Readers of
`delivered_partial_pressure_fraction` can stay as they are if it becomes a
derived property. `tests/` is outside the `mypy` gate (`pyproject.toml`,
`[tool.mypy] files`), so `Fraction` and `Percent` guard the 11 source sites
and only the tests themselves guard the 111. Effort is M, not S.

**The decision that was put.** Build the recovery now, or leave it to the save and load
format (planned item 9), which is its only consumer?

1. **Now: the percent dialled is the record, and the fraction is derived** -
   `PL-SM5V`'s shape one layer up. The interface hands the controller the
   percent; `BreathingCircuit` and `UptakeEquationSettings` store
   `delivered_concentration_percent` and each derive
   `delivered_partial_pressure_fraction` through `fraction_from_percent`; the
   setter becomes `set_delivered_concentration_percent(Percent)` on the
   circuit, the system and the controller; the timeline records the percent;
   equality, hashing and the propagator key compare it. A run driven from the
   interface stays bit-identical, because the division is the one
   `delivered_fraction` makes today, moved rather than added.
2. **Later: drop this item and hand the requirement to planned item 9.**
   Costs nothing now; what has to change grows with each shape recorded on the
   fraction first, and the timeline and the branch comparison already are.

Refused: carrying the percent beside the fraction in a segment (two copies
that can disagree, and the controller still has to receive the percent -
`PL-SM5V` refused the same shape); and recovering by rounding the fraction
times 100 to the dial's step (snaps any value off that step silently, and
writes the interface's resolution into `core/`).

**Recommended.** Option 1, now: its cost only grows, it is the rule `PL-SM5V`
already chose for flows, so a run records what was set one way rather than
two, and it moves the one conversion rather than adding one.

**Decided.** Option 1, built now (project owner, 2026-10-01, ratified, over
deferring it to the save and load format, planned item 9).

**Built, 2026-10-01.** As option 1 describes, with two things the case did not
carry. The snapshot the dashboard reads holds the percent too, so the dial is
drawn from what was dialled. And the runtime guard against a missing
conversion narrowed: a fraction passed where the dial's percent is wanted lands
under 1%, below every agent's vaporizer maximum, so no range check refuses it,
where a percent passed as a fraction used to exceed 1 and be refused. `mypy`
refuses that call in `src/`, every writer of the dial passes a value already in
percent, and a branch rebuilt from the timeline is compared against its
recorded segment, so the narrower guard was judged not to reopen the decision;
`core/concentration.py` states it. `dashboard_frame.delivered_fraction` is
gone, having no caller once the dial passed its percent straight through.

**Done when.** A recorded segment gives back every setting the dial can make,
0.00 to 8.00 % at 0.01 %, exactly as dialled, held by a test in
`tests/unit/test_run_definition.py` beside `PL-SM5V`'s flow round-trip.
