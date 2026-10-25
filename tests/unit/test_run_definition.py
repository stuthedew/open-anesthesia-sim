"""Verification of the closed-form run against the stepped run it replaces.

The run definition claims that a run needs no stored samples. The settings that a run was
computed under determine every state it passed through, so a value can be recomputed
rather than recalled. That claim has to be checked against the stepped path itself,
because the two are meant to describe the same run. So the central tests here drive
`AgentUptakeSystem` step by step, build a run definition from exactly the same setting
changes at exactly the same instants, and compare the two.

The tolerances were measured, not chosen. They are stated as absolute differences in a
fraction of one atmosphere, because that is the quantity displayed. They were measured on
2026-09-07 over a 600 s sevoflurane run with two setting changes, in which the largest
fraction reaches 0.0316:

    canonical (`state_at`) against the stepped run    1.8e-14
    display   (`evaluate`) against the stepped run    3.7e-15

Both are eleven orders of magnitude below 1e-4, the smallest change that the two-decimal
percent readout can show, so neither path can change a displayed digit. The two paths differ
because they compose the same operations in a different order, not because of method error.
`docs/MODEL.md` § "The canonical evaluation rule" states which of the two paths a stored value
may come from. `tests/reference/test_canonical_evaluation.py` tests that rule. The tests
here check that the display path is refused where the rule says it must be.
"""

from bisect import bisect_right
from dataclasses import replace
from math import inf, nan, nextafter

import pytest

from anesthesia_sim.core import run_definition
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    DELIVERED_AGENT_L,
    EXHAUSTED_AGENT_L,
    FIRST_TISSUE_FRACTION,
    INSPIRED_FRACTION,
    STATE_SIZE,
    UNIT_STATE,
    VENOUS_FRACTION,
    UptakeEquationSettings,
    build_system_matrix,
)
from anesthesia_sim.core.matrix_exponential import Matrix, matrix_exponential
from anesthesia_sim.core.run_definition import (
    DisplayState,
    Keyframe,
    RunDefinition,
    RunSegment,
    SampledWindow,
)
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import MINIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
    StepCount,
    maximum_step_count,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

SIMULATION_STEP_S = SimulationStep(0.1)
COMPARTMENT_STATES = (
    INSPIRED_FRACTION,
    ALVEOLAR_FRACTION,
    VENOUS_FRACTION,
    FIRST_TISSUE_FRACTION,
    FIRST_TISSUE_FRACTION + 1,
    FIRST_TISSUE_FRACTION + 2,
)
"""The six compartment fractions, in the order `_compartments` reads them."""

WORST_CANONICAL_DIFFERENCE = 5e-14
WORST_DISPLAY_DIFFERENCE = 5e-14
"""Absolute agreement required with the stepped run, in a fraction of 1 atm.

Both differences were measured at or below 1.8e-14, as the module docstring records. Each
limit is rounded up to one significant figure, so that an ordinary floating-point wobble does
not fail the suite. Each is still far below the 1e-4 that a readout can show, so a real
divergence still fails it.
"""


# The end of a shared guard's refusal message, which names the refused value and the reason
# (`PL-T137`). The guard's own tests check each reason. The tests here check the field name.
REFUSAL_REASON = r", and [^ ]+ is (?:not finite|not greater than zero|negative)$"


def _compartments(system: AgentUptakeSystem) -> tuple[float, ...]:
    """Return the six compartment fractions that the run records, in state order."""

    return (
        system.circuit.inspired_partial_pressure_fraction,
        system.alveoli.partial_pressure_fraction,
        system.patient.mixed_venous_partial_pressure_fraction,
        *(tissue.partial_pressure_fraction for tissue in system.patient.tissues),
    )


def _stepped_run(
    steps: int = 6000, changes: dict[int, tuple[str, float]] | None = None
) -> tuple[AgentUptakeSystem, RunDefinition, dict[float, tuple[float, ...]]]:
    """Step a run and build the run definition of the same run, returning both and the samples.

    Each change is applied to the system and recorded on the run definition at the same
    instant, and in the same order, as the app layer does it. The setter runs first, so that
    the core has accepted the value. The run definition records the change next, and it reads
    the settings back out of the compartments rather than taking the argument.
    """

    if changes is None:
        changes = {
            300: ("set_delivered_concentration_percent", Percent(4.0)),
            1200: ("set_alveolar_ventilation", AlveolarVentilation(6.0)),
        }

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    stepped = {0.0: _compartments(system)}

    for step in range(1, steps + 1):
        system.advance(SIMULATION_STEP_S)
        elapsed_s = round(step * SIMULATION_STEP_S, 6)
        definition.advance_to(CaseInstant(elapsed_s))

        if step in changes:
            setter, value = changes[step]
            getattr(system, setter)(value)
            definition.record_change(system.equation_settings())

        stepped[elapsed_s] = _compartments(system)

    return system, definition, stepped


def test_evaluate_matches_a_stepped_run() -> None:
    """A window's states are the ones the stepped run actually reached.

    This one test checks the whole claim of the run definition. A run that recorded nothing
    returns a state for every instant that a run recording everything passed through. It
    does so across two setting changes, and to within a difference that no display can show.
    """

    _, definition, stepped = _stepped_run()
    window = definition.evaluate(0.0, 600.0, 601)

    assert len(window.states) == 601

    for elapsed_s, state in zip(window.times_s, window.states, strict=True):
        expected = stepped[round(elapsed_s, 6)]

        for compartment, want in zip(COMPARTMENT_STATES, expected, strict=True):
            assert abs(state.values[compartment] - want) < WORST_DISPLAY_DIFFERENCE


def test_state_at_matches_a_stepped_run() -> None:
    """The canonical path returns the same run's states, at whatever instants it is asked for."""

    _, definition, stepped = _stepped_run()

    for step in range(0, 6001, 37):
        elapsed_s = round(step * SIMULATION_STEP_S, 6)
        state = definition.state_at(elapsed_s)

        for compartment, want in zip(COMPARTMENT_STATES, stepped[elapsed_s], strict=True):
            assert abs(state[compartment] - want) < WORST_CANONICAL_DIFFERENCE


def test_the_canonical_path_answers_bit_identically_twice() -> None:
    """Two canonical evaluations of one definition at one instant agree exactly.

    The test uses no tolerance, because both evaluations perform the same sequence of
    operations on the same values. A keyframe, an export and a fork's starting state all rely
    on this property. `PL-P1Z3` states the property in `docs/MODEL.md` and keeps the display
    path from being used where the property is required.
    """

    _, definition, _ = _stepped_run(steps=900)

    for step in (0, 1, 299, 300, 301, 899, 900):
        elapsed_s = round(step * SIMULATION_STEP_S, 6)

        assert definition.state_at(elapsed_s) == definition.state_at(elapsed_s)


def test_the_accumulated_agent_matches_the_run_s_own_accounting() -> None:
    """Delivered and exhausted agent come back as running totals, not per-segment ones.

    The two accumulator rows have no diagonal entry, so a propagator maps each accumulator to
    itself with a coefficient of one. Carrying a cumulative total through every segment is
    therefore the same arithmetic as restarting the total in each segment. This is what lets
    the closed form compute the mass balance at any instant without stepping to it.
    """

    system, definition, _ = _stepped_run()
    accounting = system.agent_simulation_validation
    final = definition.state_at(600.0)

    assert final[DELIVERED_AGENT_L] == pytest.approx(accounting.delivered_agent_l, rel=1e-9)
    assert final[EXHAUSTED_AGENT_L] == pytest.approx(accounting.exhausted_agent_l, rel=1e-9)
    assert final[DELIVERED_AGENT_L] > definition.state_at(300.0)[DELIVERED_AGENT_L] > 0.0


def test_a_window_reads_only_the_segments_it_covers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Frame cost follows the window, not the run's length.

    `PL-T691` exists to make this claim true. The test checks it structurally rather than
    with a clock. A window pays for matrix exponentials in each segment it covers, so
    counting the exponentials shows whether the run's other 1 498 segments were touched. A
    timing assertion would check the same thing, but it would fail on a busy machine.

    The run fills the supported run length and no more, because a run that reaches past
    that length is refused (`PL-8H2R`). The claim needs many segments behind the window, not
    any particular length.
    """

    exponentials = 0
    exact = run_definition.matrix_exponential

    def counting_exponential(matrix: Matrix, interval_s: float) -> Matrix:
        nonlocal exponentials
        exponentials += 1

        return exact(matrix, interval_s)

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    total_s = MAXIMUM_ELAPSED_SIMULATION_TIME_S

    for change in range(1, 1501):
        definition.advance_to(CaseInstant(change * total_s / 1501))
        system.set_delivered_concentration_percent(Percent(1.0 + 0.5 * (change % 4)))
        definition.record_change(system.equation_settings())

    definition.advance_to(CaseInstant(total_s))

    assert len(definition.segments) == 1501

    monkeypatch.setattr(run_definition, "matrix_exponential", counting_exponential)
    definition.evaluate(total_s - 100.0, total_s, 600)

    # This run changes a setting every 57.6 s, so the last 100 s covers at most three
    # segments. Each segment costs two propagators: one for the offset from its keyframe
    # to its first column, and one for the column spacing. An implementation that walked
    # the whole run instead of the window would touch on the order of the 1 501 segments
    # behind it.
    assert exponentials <= 6
    assert exponentials < len(definition.segments) / 100


def test_a_run_under_unchanged_settings_is_one_segment() -> None:
    """Recording the settings already in force describes no change, so none is kept."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    definition.advance_to(CaseInstant(10.0))
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 1


def test_two_changes_at_one_instant_are_one_segment() -> None:
    """Two controls moved between the same two steps open one new segment, not two.

    The run was computed under whatever settings applied when the step ran, so a
    zero-length segment would describe a stretch of time that the model never integrated.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    definition.advance_to(CaseInstant(10.0))
    system.set_delivered_concentration_percent(Percent(3.0))
    definition.record_change(system.equation_settings())
    system.set_cardiac_output(CardiacOutput(4.0))
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 2
    assert definition.segments[-1].opening.instant_s == 10.0
    assert definition.segments[-1].settings.cardiac_output_l_s == pytest.approx(4.0 / 60.0)
    assert definition.segments[-1].settings.delivered_concentration_percent == 3.0


def _configured_from(settings: UptakeEquationSettings) -> AgentUptakeSystem:
    """Return a fresh system set to the four live controls that a recorded segment stores."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    system.set_fresh_gas_flow(settings.fresh_gas_flow_l_min)
    system.set_delivered_concentration_percent(settings.delivered_concentration_percent)
    system.set_alveolar_ventilation(settings.alveolar_ventilation_l_min)
    system.set_cardiac_output(settings.cardiac_output_l_min)

    return system


@pytest.mark.parametrize(
    ("control", "maximum_l_min", "flow_type"),
    [
        ("cardiac_output", MAXIMUM_CARDIAC_OUTPUT_L_MIN, CardiacOutput),
        ("fresh_gas_flow", MAXIMUM_FRESH_GAS_FLOW_L_MIN, FreshGasFlow),
        ("alveolar_ventilation", MAXIMUM_ALVEOLAR_VENTILATION_L_MIN, AlveolarVentilation),
    ],
)
def test_a_recorded_setting_round_trips_to_what_was_set(
    control: str, maximum_l_min: float, flow_type: type[float]
) -> None:
    """A segment stores each flow as it was set, so it rebuilds the settings it ran under.

    `PL-SM5V`. Segments used to store flows in litres per second. Multiplying them back by
    sixty rebuilt different settings for 7 of the 101 cardiac outputs on this grid:
    1.9, 3.8, 3.9 and 7.6 to 7.9 L/min. The cause was that each tissue's flow is cardiac
    output times its perfusion fraction, formed in litres per minute before the division.
    The test checks every setting on a 0.1 L/min grid across the supported range, for each
    of the three flow controls, and names each setting that fails.
    """

    set_control = getattr(AgentUptakeSystem, f"set_{control}")
    unrecovered: list[float] = []

    for tenths in range(round(maximum_l_min * 10) + 1):
        set_l_min = tenths / 10
        system = AgentUptakeSystem.for_agent("sevoflurane")
        set_control(system, flow_type(set_l_min))
        definition = RunDefinition(
            system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
        )
        recorded = definition.segments[-1].settings

        if (
            getattr(recorded, f"{control}_l_min") != set_l_min
            or _configured_from(recorded).equation_settings() != recorded
        ):
            unrecovered.append(set_l_min)

    assert unrecovered == []


@pytest.mark.parametrize(
    ("field", "flow_type", "reproduced_l_min"),
    [
        ("cardiac_output_l_min", CardiacOutput, 1000.0),
        ("fresh_gas_flow_l_min", FreshGasFlow, 500.0),
        ("alveolar_ventilation_l_min", AlveolarVentilation, 200.0),
    ],
)
def test_a_run_cannot_open_or_change_under_a_flow_outside_the_supported_ranges(
    field: str, flow_type: type[float], reproduced_l_min: float
) -> None:
    """Neither way into a run can be handed a record whose flow is outside its range.

    `PL-HSFV`, reproduced 2026-10-04. The settings that a system holds were rebuilt with
    `replace` to a cardiac output of 1000 L/min, with the tissue flows scaled to sum to it.
    That record opened a run, and it was also recorded as a change to a run. The run
    returned finite, plausible fractions. The cause was that the record checked only the sum
    of the flows, and the range guards ran only in the compartments, which a run built from
    a record never calls. The same was true for a fresh gas flow of 500 L/min and an
    alveolar ventilation of 200 L/min.

    Each flow field now takes a type that only its guard builds (`PL-0YYV`), so such a
    record cannot exist. A flow built as its type is refused by the guard, in the guard's
    own words, before `replace` runs. A flow handed in as a bare float is refused by the
    record itself. Neither `RunDefinition(...)` nor `record_change` is entered, because its
    argument is refused first. The two calls remain in the test as the entry points that the
    reproduction went through. Either way, the run keeps the segments it had, and the run
    checks nothing of its own.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    held = system.equation_settings()

    def rebuilt(value: float) -> UptakeEquationSettings:
        changed: dict[str, object] = {field: value}

        if field == "cardiac_output_l_min":
            changed["tissues"] = tuple(
                replace(
                    tissue,
                    blood_flow_l_min=tissue.blood_flow_l_min / held.cardiac_output_l_min * value,
                )
                for tissue in held.tissues
            )

        return replace(held, **changed)

    definition = RunDefinition(held, system.state_vector(), opened_at_s=CaseInstant(0.0))
    definition.advance_to(CaseInstant(30.0))
    segments = definition.segments
    refused = f"not built as {flow_type.__name__}"

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        RunDefinition(
            rebuilt(flow_type(reproduced_l_min)),
            system.state_vector(),
            opened_at_s=CaseInstant(0.0),
        )

    with pytest.raises(TypeError, match=refused):
        RunDefinition(
            rebuilt(reproduced_l_min), system.state_vector(), opened_at_s=CaseInstant(0.0)
        )

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        definition.record_change(rebuilt(flow_type(reproduced_l_min)))

    with pytest.raises(TypeError, match=refused):
        definition.record_change(rebuilt(reproduced_l_min))

    assert definition.segments == segments


def test_a_run_cannot_open_or_change_under_a_dial_above_the_vaporizer_maximum() -> None:
    """Neither way into a run can be handed a record whose dial the vaporizer cannot deliver.

    `PL-BBMG`, reproduced 2026-10-04. The settings that a sevoflurane system holds were
    rebuilt with `replace` to a 20% dial setting, against the agent's 8% maximum. That
    record opened a run, and it was also recorded as a change to a run. The run returned an
    alveolar fraction of 0.033306 at 60 s. The cause was that the record stored no maximum
    and bounded the dial only at 100%, and the circuit that refuses the dial is never built
    on this path.

    The record now carries the maximum that its dial was set under, read from the circuit.
    It refuses a dial above that maximum, with the circuit's own message, before `replace`
    returns. So neither `RunDefinition(...)` nor `record_change` is entered. The two calls
    remain in the test as the entry points that the reproduction went through. A dial at the
    maximum itself opens a run and records a change, and the first percent above the maximum
    is refused by both. Either way, the run keeps the segments it had.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    held = system.equation_settings()
    maximum = system.circuit.max_delivered_concentration_percent
    reproduced = r"exceeds the vaporizer maximum \(20% requested, 8% maximum\)"

    assert held.max_delivered_concentration_percent == maximum == 8.0

    definition = RunDefinition(held, system.state_vector(), opened_at_s=CaseInstant(0.0))
    definition.advance_to(CaseInstant(30.0))
    segments = definition.segments

    with pytest.raises(SimulationConfigurationError, match=reproduced):
        RunDefinition(
            replace(held, delivered_concentration_percent=Percent(20.0)),
            system.state_vector(),
            opened_at_s=CaseInstant(0.0),
        )

    with pytest.raises(SimulationConfigurationError, match=reproduced):
        definition.record_change(replace(held, delivered_concentration_percent=Percent(20.0)))

    past_the_maximum = Percent(nextafter(maximum, inf))

    with pytest.raises(SimulationConfigurationError, match="exceeds the vaporizer maximum"):
        RunDefinition(
            replace(held, delivered_concentration_percent=past_the_maximum),
            system.state_vector(),
            opened_at_s=CaseInstant(0.0),
        )

    with pytest.raises(SimulationConfigurationError, match="exceeds the vaporizer maximum"):
        definition.record_change(replace(held, delivered_concentration_percent=past_the_maximum))

    assert definition.segments == segments

    at_the_maximum = replace(held, delivered_concentration_percent=maximum)
    opened = RunDefinition(at_the_maximum, system.state_vector(), opened_at_s=CaseInstant(0.0))
    definition.record_change(at_the_maximum)

    assert opened.segments[0].settings.delivered_concentration_percent == maximum
    assert definition.segments[-1].settings.delivered_concentration_percent == maximum


def test_a_recorded_segment_gives_back_each_vaporizer_percent_as_dialled() -> None:
    """A segment stores the vaporizer setting as the percent dialled, at every dial position.

    `PL-NJPB`. Segments used to store a fraction, which the interface formed by dividing the
    dial's percent by a hundred. A fraction times a hundred misses the percent it came from
    for 126 of the 801 positions that a 0 to 8% dial makes in 0.01% steps. The first is
    0.23%, and 0.9% reads back as 0.9000000000000001. So the setting could not be recovered
    as dialled. The test checks every position of sevoflurane's dial, formed the way
    `dashboard_frame.slider_value` forms it, and names each position that fails.
    """

    circuit = AgentUptakeSystem.for_agent("sevoflurane").circuit
    maximum_percent = circuit.max_delivered_concentration_percent
    unrecovered: list[float] = []

    for hundredths in range(round(maximum_percent * 100) + 1):
        dialled_percent = Percent(hundredths / 100)
        system = AgentUptakeSystem.for_agent("sevoflurane")
        system.set_delivered_concentration_percent(dialled_percent)
        definition = RunDefinition(
            system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
        )
        recorded = definition.segments[-1].settings

        if (
            recorded.delivered_concentration_percent != dialled_percent
            or _configured_from(recorded).equation_settings() != recorded
        ):
            unrecovered.append(dialled_percent)

    assert unrecovered == []


def test_a_change_opens_a_segment_at_the_run_s_own_reach() -> None:
    """A recorded change opens its segment at the instant the run had reached, and nowhere else."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    definition.advance_to(CaseInstant(12.5))
    system.set_fresh_gas_flow(FreshGasFlow(1.5))
    definition.record_change(system.equation_settings())

    assert [segment.opening.instant_s for segment in definition.segments] == [0.0, 12.5]
    assert definition.segments[-1].opening.state == definition.state_at(12.5)


def test_the_run_starts_where_the_system_does() -> None:
    """A definition opened from a system's state returns that state at time zero."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )

    assert definition.reached_s == 0.0
    assert definition.state_at(0.0) == system.state_vector()


def test_advancing_to_the_time_already_reached_changes_nothing() -> None:
    """Advancing twice to the same instant is not an error."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    definition.advance_to(CaseInstant(5.0))
    definition.advance_to(CaseInstant(5.0))

    assert definition.reached_s == 5.0


def test_a_one_column_window_is_the_instant_asked_for() -> None:
    """`columns` of one returns `start_s` alone, with no spacing to divide by."""

    _, definition, stepped = _stepped_run(steps=100)
    window = definition.evaluate(4.0, 10.0, 1)

    assert window.times_s == (4.0,)
    assert len(window.states) == 1

    for compartment, want in zip(COMPARTMENT_STATES, stepped[4.0], strict=True):
        assert abs(window.states[0].values[compartment] - want) < WORST_DISPLAY_DIFFERENCE


def test_a_window_of_no_width_repeats_one_instant() -> None:
    """Every column of a zero-width window is the same state, not a divide by zero."""

    _, definition, _ = _stepped_run(steps=100)
    window = definition.evaluate(6.0, 6.0, 5)

    assert window.times_s == (6.0,) * 5
    assert set(window.states) == {DisplayState(definition.state_at(6.0))}


def test_a_window_opening_on_a_keyframe_needs_no_propagation() -> None:
    """The state at a segment's own opening is that segment's keyframe, unaltered."""

    _, definition, _ = _stepped_run(steps=600)
    window = definition.evaluate(30.0, 60.0, 4)

    assert window.states[0].values == definition.segments[1].opening.state


def test_a_segment_too_short_to_hold_a_column_is_skipped() -> None:
    """A window whose columns straddle a whole segment still uses the right segment.

    A walk that assumed one segment per column would give the column after the gap the
    skipped segment's settings. It would then draw a stretch of the run under settings that
    the run was never computed under.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )

    for elapsed_s, flow in ((10.0, 1.5), (10.5, 3.0), (60.0, 5.0)):
        definition.advance_to(CaseInstant(elapsed_s))
        system.set_fresh_gas_flow(FreshGasFlow(flow))
        definition.record_change(system.equation_settings())

    definition.advance_to(CaseInstant(120.0))
    window = definition.evaluate(0.0, 120.0, 5)

    assert len(definition.segments) == 4
    assert window.times_s == (0.0, 30.0, 60.0, 90.0, 120.0)

    for elapsed_s, state in zip(window.times_s, window.states, strict=True):
        canonical = definition.state_at(elapsed_s)

        for compartment in COMPARTMENT_STATES:
            difference = abs(state.values[compartment] - canonical[compartment])

            assert difference < WORST_DISPLAY_DIFFERENCE


def test_a_run_definition_refuses_a_display_state_as_its_opening_state() -> None:
    """A fork that opens from a drawn value is the failure that the wrapper exists to stop.

    `RunDefinition.__init__` is the canonical sink that a display value is most likely to
    reach by accident. A fork's opening state and a drawn column are the same nine numbers in
    the same order. Refusing the display value is what makes the two different things, rather
    than the same thing described differently.
    """

    _, definition, _ = _stepped_run(steps=100)
    drawn = definition.evaluate(0.0, 10.0, 5).states[0]
    system = AgentUptakeSystem.for_agent("sevoflurane")

    with pytest.raises(SimulationConfigurationError, match="came from the display path"):
        RunDefinition(system.equation_settings(), drawn, opened_at_s=CaseInstant(0.0))  # type: ignore[arg-type]


def test_a_display_state_is_not_a_state_vector() -> None:
    """This tests the structural half of the guarantee, which protects a sink that has no check.

    A tuple subclass would have passed every test above, while flowing silently into an
    exporter or a save format that indexes a state and checks nothing. What prevents that is
    that a display state is not a sequence at all.
    """

    _, definition, _ = _stepped_run(steps=100)
    drawn = definition.evaluate(0.0, 10.0, 5).states[0]

    assert not isinstance(drawn, tuple)
    assert isinstance(drawn.values, tuple)
    assert len(drawn.values) == STATE_SIZE


def test_a_run_definition_refuses_a_state_of_the_wrong_length() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")

    with pytest.raises(SimulationConfigurationError, match=f"the equations carry {STATE_SIZE}"):
        RunDefinition(system.equation_settings(), (0.0, 1.0), opened_at_s=CaseInstant(0.0))


def test_a_run_definition_refuses_a_non_finite_state() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    state = list(system.state_vector())
    state[ALVEOLAR_FRACTION] = nan

    with pytest.raises(SimulationConfigurationError, match="which is not finite"):
        RunDefinition(system.equation_settings(), tuple(state), opened_at_s=CaseInstant(0.0))


def test_a_run_definition_refuses_a_state_whose_unit_is_not_one() -> None:
    """The forcing terms are multiplied by this entry, so its value must be one and is not free."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    state = list(system.state_vector())
    state[UNIT_STATE] = 0.5

    with pytest.raises(SimulationConfigurationError, match="the constant one"):
        RunDefinition(system.equation_settings(), tuple(state), opened_at_s=CaseInstant(0.0))


@pytest.mark.parametrize("opened_at_s", [nan, inf, -inf, -1.0])
def test_an_opening_no_case_reaches_cannot_be_built(opened_at_s: float) -> None:
    """The instant is refused where it is built, before any run can open at it (`PL-CN5S`).

    Every later result is measured from the opening instant. A definition opened at a
    non-finite instant would propagate over a non-finite interval and return a state of
    `nan`. No bounds check downstream could tell that state apart from a run that genuinely
    reached such a state. The case's time axis also starts at induction, so no run on it
    opens before zero. `CaseInstant` refuses both kinds of value, in the words of the
    supported run length.
    """

    with pytest.raises(SimulationConfigurationError, match="outside the supported run length"):
        CaseInstant(opened_at_s)


@pytest.mark.parametrize("opened_at_s", [0.0, nan, -1.0])
def test_a_run_definition_refuses_an_opening_not_built_as_a_case_instant(
    opened_at_s: float,
) -> None:
    """The opening is refused whatever its value, because nothing has checked it (`PL-CN5S`).

    `mypy` refuses a bare `float` here. This test covers the callers that a type checker
    cannot check: a test, a notebook, or a value typed `Any`. The opening is refused before
    the definition exists, alongside the state vector and for the same reason. The opening
    is half of what the run is measured from.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")

    with pytest.raises(TypeError, match="opened_at_s of .* was not built as CaseInstant"):
        RunDefinition(
            system.equation_settings(),
            system.state_vector(),
            opened_at_s=opened_at_s,  # type: ignore[arg-type]
        )


def test_a_run_may_open_at_the_end_of_the_supported_run_length() -> None:
    """The span is closed, so a run may open exactly at its far end (`PL-73ZN`).

    A branch taken where its trunk stopped at the limit opens exactly there, so refusing
    that instant would refuse the branch. The branch opens with no time left to run. That
    means the parent's span is used up, which is not an error.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(),
        system.state_vector(),
        opened_at_s=CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S),
    )

    assert definition.opened_at_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S
    assert definition.state_at(MAXIMUM_ELAPSED_SIMULATION_TIME_S) == system.state_vector()


@pytest.mark.parametrize(
    "opened_at_s",
    [nextafter(MAXIMUM_ELAPSED_SIMULATION_TIME_S, inf), MAXIMUM_ELAPSED_SIMULATION_TIME_S + 0.1],
)
def test_opening_past_the_supported_envelope_cannot_be_built(opened_at_s: float) -> None:
    """The opening is refused where it is built, not at the first step after it (`PL-73ZN`).

    The opening is the origin of every instant that a branch reports, so an opening past the
    envelope would carry the error into every value read from the run. The edge is the
    declared constant itself, and the next float past it is refused. The message names the
    exact value and the envelope that it is outside. Since `PL-CN5S`, the refusal comes from
    the `CaseInstant` that the opening is built as, so no definition is ever given such an
    opening.
    """

    with pytest.raises(SimulationConfigurationError, match="supported run length") as raised:
        CaseInstant(opened_at_s)

    assert f"{opened_at_s} s" in str(raised.value)
    assert f"0 to {MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s" in str(raised.value)


def test_a_run_refuses_to_go_backwards() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    definition.advance_to(CaseInstant(20.0))

    with pytest.raises(SimulationConfigurationError, match="cannot go back"):
        definition.advance_to(CaseInstant(19.9))


def test_a_keyframe_refuses_an_instant_not_built_as_a_case_instant() -> None:
    """A keyframe stores its instant, so it checks the type where it is built (`PL-CN5S`).

    A definition builds every keyframe it holds from an opening or a reach that it has
    already checked. This test covers the way in for any other caller.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")

    with pytest.raises(TypeError, match="instant_s of 5.0 was not built as CaseInstant"):
        Keyframe(5.0, system.state_vector())  # type: ignore[arg-type]


def test_a_non_finite_reach_cannot_be_built() -> None:
    """A non-finite reach is refused when built, so no run can be moved to one (`PL-CN5S`)."""

    with pytest.raises(SimulationConfigurationError, match="outside the supported run length"):
        CaseInstant(inf)


@pytest.mark.parametrize("instant_s", [30.0, inf])
def test_a_run_refuses_a_reach_not_built_as_a_case_instant(instant_s: float) -> None:
    """The reach is refused whatever its value, and before the reach moves (`PL-CN5S`)."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    definition.advance_to(CaseInstant(20.0))

    with pytest.raises(TypeError, match="instant_s of .* was not built as CaseInstant"):
        definition.advance_to(instant_s)  # type: ignore[arg-type]

    assert definition.reached_s == 20.0


def test_a_run_may_reach_the_end_of_the_supported_run_length() -> None:
    """The reach has the same closed bound as the opening, so a run may reach the far end."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )

    definition.advance_to(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))

    assert definition.reached_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S


@pytest.mark.parametrize(
    "instant_s",
    [nextafter(MAXIMUM_ELAPSED_SIMULATION_TIME_S, inf), MAXIMUM_ELAPSED_SIMULATION_TIME_S + 0.1],
)
def test_a_reach_past_the_supported_run_length_cannot_be_built(instant_s: float) -> None:
    """A reach past the span cannot be built, so the run cannot be moved or evaluated there.

    Until `PL-8H2R` the reach was unguarded. At a step size whose quotient rounded up, the
    last step that a run took landed on a float just past the span, and a bound here would
    have refused it. The step count now stops on the last step inside the span, so the reach
    carries the opening's bound. Since `PL-CN5S`, that bound is enforced by the `CaseInstant`
    that the reach is moved to, which is refused when it is built.
    """

    with pytest.raises(SimulationConfigurationError, match="supported run length") as raised:
        CaseInstant(instant_s)

    assert f"{instant_s} s" in str(raised.value)


@pytest.mark.parametrize("simulation_step_s", [0.1, 768 / 1_000_000 * 100, 0.02304])
def test_a_run_may_reach_the_last_step_it_is_allowed_to_take(simulation_step_s: float) -> None:
    """The reach follows the step count to its limit at every step size, never past it.

    The application moves the reach to each step's `elapsed_s`, so the guard on the reach
    must accept the last step that `SimulationState` allows. At a step of
    `768 / 1_000_000 * 100` s, that last step stood at 86400.00000000001 s before `PL-8H2R`,
    and this guard would have refused it after the step had been taken.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    last_step_s = SimulationState(
        step_count=StepCount(maximum_step_count(simulation_step_s)),
        simulation_step_s=SimulationStep(simulation_step_s),
    ).elapsed_s

    definition.advance_to(last_step_s)

    assert definition.reached_s == last_step_s


@pytest.mark.parametrize("instant_s", [nan, inf])
def test_a_run_definition_refuses_a_non_finite_instant(instant_s: float) -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )

    with pytest.raises(SimulationConfigurationError, match="not a finite instant"):
        definition.state_at(instant_s)


def test_a_run_definition_has_no_state_before_the_run_began() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )

    with pytest.raises(SimulationConfigurationError, match="before it began"):
        definition.state_at(-0.1)


def _opening_after_zero() -> RunDefinition:
    """Return a definition that opens at 600 s, as a branch forked at that instant does.

    Since `PL-ZMRT` it is built through the public constructor. The run opens on the case's
    own time axis at 600 s and records a change at 900 s. So the guards below are exercised
    against the arrangement that `SimulationController` actually builds, not against a
    synthesized one.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    system.set_delivered_concentration_percent(Percent(2.0))
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(600.0)
    )

    definition.advance_to(CaseInstant(900.0))
    system.set_delivered_concentration_percent(Percent(0.5))
    definition.record_change(system.equation_settings())

    definition.advance_to(CaseInstant(1200.0))

    return definition


def test_a_run_definition_reports_the_instant_it_opens_at() -> None:
    """This is the one place where a definition's own opening is named, and it is not the reach.

    The test reads the opening directly rather than through a caller, because since `PL-B8MK` the
    app layer has its own instant for where a branch begins. A branch's *beginning* is its fork, and
    a bookmark fork puts that fork after the keyframe that its definition opens at. So
    `SimulationController.began_at_s` is what clips a drawn axis, and the opening tested here says
    where the definition may be evaluated from. The two were one number until a bookmark became
    forkable, and a test that reached the opening through the app layer could not tell them apart.
    """

    trunk_shaped = RunDefinition(
        AgentUptakeSystem.for_agent("sevoflurane").equation_settings(),
        AgentUptakeSystem.for_agent("sevoflurane").state_vector(),
        opened_at_s=CaseInstant(0.0),
    )

    assert trunk_shaped.opened_at_s == 0.0

    branch_shaped = _opening_after_zero()

    # The opening is the first segment's own instant. Recording changes, and advancing the
    # reach past them, leaves the opening where it was.
    assert branch_shaped.opened_at_s == 600.0
    assert branch_shaped.segments[0].opening.instant_s == 600.0
    assert branch_shaped.reached_s == 1200.0


def test_a_run_definition_that_opens_after_zero_refuses_the_span_before_it() -> None:
    """The lower bound is the run's own opening, never the literal zero.

    A bound fixed at zero would not cause a wrong refusal. It would cause a silent wrong
    result. `_segment_index_at` returns `-1` for an instant before the first opening, and
    Python treats that index as the *last* segment. `_propagator` then returns `None` for
    the non-positive interval that follows. So the caller is given that segment's keyframe
    as the state at an instant when the run did not exist. This was measured on this
    definition before the guard existed. `state_at(0.0)`, `state_at(100.0)` and
    `state_at(599.9)` all returned the same 0.005664 alveolar fraction instead of refusing.
    `evaluate_anchored(0.0, 500.0, 100.0)` drew a varying curve across a span that the run
    had no state for.
    """

    definition = _opening_after_zero()

    for elapsed_s in (0.0, 100.0, 599.9):
        with pytest.raises(SimulationConfigurationError, match="before it began"):
            definition.state_at(elapsed_s)

    with pytest.raises(SimulationConfigurationError, match="before it began"):
        definition.evaluate_anchored(0.0, 500.0, 100.0)

    with pytest.raises(SimulationConfigurationError, match="before it began"):
        definition.evaluate(0.0, 500.0, 6)


def test_a_run_definition_answers_at_its_own_opening() -> None:
    """The bound accepts the opening itself, which is the instant of the run's first keyframe."""

    definition = _opening_after_zero()

    assert definition.state_at(600.0) == definition.segments[0].opening.state


def test_a_run_definition_is_under_no_settings_before_it_opens() -> None:
    """This tests the second of the two guards, which only a direct call can reach.

    `_require_within_run` refuses the instant on every public path. So this guard can never
    fire through `state_at`, `evaluate` or `evaluate_anchored` while that bound is correct.
    The test exists because the two guards protect against the same silent wrong result by
    different means. The bound says that the run has no state at that instant, and this
    guard says that the segment search found no segment. A future caller that reaches the
    search without the bound meets a refusal rather than the last segment's keyframe.
    `_canonical_state_at` is already such a caller, by design.
    """

    definition = _opening_after_zero()

    with pytest.raises(SimulationConfigurationError, match="under no settings"):
        definition._segment_index_at(599.9)


def test_a_run_definition_refuses_to_predict_past_the_run() -> None:
    """A state past the run would be a prediction that could not be told apart from the run."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    definition.advance_to(CaseInstant(30.0))

    with pytest.raises(SimulationConfigurationError, match="rather than the run"):
        definition.state_at(30.1)


def test_a_window_needs_at_least_one_column() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )

    with pytest.raises(SimulationConfigurationError, match="at least one column"):
        definition.evaluate(0.0, 0.0, 0)


def test_a_window_refuses_to_end_before_it_begins() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    definition.advance_to(CaseInstant(30.0))

    with pytest.raises(SimulationConfigurationError, match="ends before it begins"):
        definition.evaluate(20.0, 10.0, 5)


def test_a_window_refuses_to_reach_past_the_run() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    definition.advance_to(CaseInstant(30.0))

    with pytest.raises(SimulationConfigurationError, match="rather than the run"):
        definition.evaluate(10.0, 30.1, 5)


def test_a_sampled_window_pairs_each_state_with_one_instant() -> None:
    """Times and states of different lengths would draw a trace off its own axis."""

    with pytest.raises(SimulationConfigurationError, match="belongs to one instant"):
        SampledWindow(times_s=(0.0, 1.0), states=(DisplayState((0.0,) * STATE_SIZE),))


def test_a_segment_carries_the_state_its_settings_start_from() -> None:
    """A recorded run gives back the pairing that `RunSegment` exists to hold."""

    _, definition, _ = _stepped_run(steps=600)
    segment = definition.segments[1]

    assert isinstance(segment, RunSegment)
    assert isinstance(segment.opening, Keyframe)
    assert segment.opening.instant_s == 30.0
    assert len(segment.opening.state) == STATE_SIZE
    assert segment.opening.state[UNIT_STATE] == 1.0


def test_a_change_undone_before_a_step_runs_leaves_no_segment() -> None:
    """A dial moved and moved back between two steps describes no change at all.

    The stretch that the change opened is dropped, rather than kept with the settings it
    started from. Keeping it would put a keyframe in the run definition for an instant that
    the run passed through with nothing of note. The interface's own control timeline drops
    the matching entry for the same reason.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    definition.advance_to(CaseInstant(10.0))
    system.set_delivered_concentration_percent(Percent(3.0))
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 2

    system.set_delivered_concentration_percent(Percent(2.0))
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 1
    assert definition.segments[0].opening.instant_s == 0.0


def test_a_change_undone_at_one_instant_keeps_every_earlier_stretch() -> None:
    """Undoing a change drops only the stretch that the change opened.

    The docstring of `record_change` gives the rule. When a second change, at an instant that
    already opened a stretch, returns to the previous stretch's settings, "the stretch goes
    entirely". That stretch is the one opened at that instant, and no earlier one. This run
    has three stretches before the undo. With only two, the wrong slice `segments[:1]` keeps
    the same list as the right one, `segments[:-1]`, and every earlier test of this branch
    used two (`PL-ZH1F`).

    Neither expected value is read from the definition under test. The stretches are
    literals, and the expected state comes from a second definition that was never given
    the 5% change.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    system.set_delivered_concentration_percent(Percent(2.0))
    opening_settings = system.equation_settings()
    opening_state = system.state_vector()
    undone = RunDefinition(opening_settings, opening_state, opened_at_s=CaseInstant(0.0))
    never_changed = RunDefinition(opening_settings, opening_state, opened_at_s=CaseInstant(0.0))

    for definition in (undone, never_changed):
        definition.advance_to(CaseInstant(10.0))
    system.set_delivered_concentration_percent(Percent(3.0))
    for definition in (undone, never_changed):
        definition.record_change(system.equation_settings())
        definition.advance_to(CaseInstant(20.0))
    system.set_delivered_concentration_percent(Percent(5.0))
    undone.record_change(system.equation_settings())

    assert len(undone.segments) == 3

    system.set_delivered_concentration_percent(Percent(3.0))
    undone.record_change(system.equation_settings())

    assert [
        (segment.opening.instant_s, segment.settings.delivered_concentration_percent)
        for segment in undone.segments
    ] == [(0.0, 2.0), (10.0, 3.0)]

    for definition in (undone, never_changed):
        definition.advance_to(CaseInstant(600.0))

    assert undone.state_at(600.0) == never_changed.state_at(600.0)


def test_the_first_stretch_is_kept_even_when_a_change_returns_to_it() -> None:
    """There is no earlier stretch to fold the opening stretch back into.

    The run's first segment opens at zero and carries the settings that the run began
    under. So a change recorded at zero replaces those settings, rather than dropping a
    stretch that nothing comes before.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    system.set_delivered_concentration_percent(Percent(5.0))
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 1
    assert definition.segments[0].settings.delivered_concentration_percent == 5.0


def test_recording_a_change_copies_no_segment_already_recorded() -> None:
    """Each accepted change adds one segment and leaves every earlier one as it was.

    The record grows by what the change adds and by nothing else. It stores references, so
    a change copies at most one pointer per segment and never copies a keyframe. `PL-7TXJ`
    measured on 2026-09-27 that a segment takes about 900 bytes, 408 of them for its
    keyframe, and that the tuple rebuilt on each change copies an 8-byte reference to it.
    The test checks identity rather than equality, because an equal copy of a keyframe is
    exactly what the test rules out. A segment is frozen, so the same segment carries the
    same keyframe. Three hundred changes is the count over which `PL-1PSX` measured this
    record and the control timeline growing one-for-one.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )

    for change in range(1, 301):
        before = definition.segments
        definition.advance_to(CaseInstant(change * 10.0))
        system.set_delivered_concentration_percent(Percent(1.0 + 0.5 * (change % 4)))
        definition.record_change(system.equation_settings())
        after = definition.segments

        assert len(after) == len(before) + 1
        assert all(kept is held for kept, held in zip(after[:-1], before, strict=True))


def test_a_record_handed_out_is_not_changed_by_later_changes() -> None:
    """`segments` returns the run as it stood, whatever the run records next.

    This lets a caller read the run without being able to advance it.
    `tests/integration/test_simulation_view.py` relies on it when it compares
    `run_segments` before and after an action. A view that followed the run would make that
    comparison pass whatever the action did. The test exercises every kind of change that
    `record_change` can make, because each one changes the record differently. A change can
    replace the open segment at the instant it opened, drop that segment on a dial-back, or
    append a new segment after it.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    definition.advance_to(CaseInstant(10.0))
    system.set_delivered_concentration_percent(Percent(3.0))
    definition.record_change(system.equation_settings())
    held = definition.segments
    contents = list(held)

    for percent, reach_s in ((4.0, 10.0), (2.0, 10.0), (5.0, 20.0)):
        definition.advance_to(CaseInstant(reach_s))
        system.set_delivered_concentration_percent(Percent(percent))
        definition.record_change(system.equation_settings())

        assert len(held) == len(contents)
        assert all(kept is was for kept, was in zip(held, contents, strict=True))

    assert [segment.opening.instant_s for segment in definition.segments] == [0.0, 20.0]


def test_anchored_columns_land_on_multiples_of_the_spacing() -> None:
    """The grid is measured from the case's zero, not from the window's left edge.

    This is what lets a following window reuse its column times. `evaluate` deliberately
    does not have this property.
    """

    _, definition, _ = _stepped_run()
    spacing_s = 7.0
    window = definition.evaluate_anchored(103.0, 297.0, spacing_s)
    interior = [time_s for time_s in window.times_s if time_s not in (103.0, 297.0)]
    events = {segment.opening.instant_s for segment in definition.segments}

    assert interior
    for time_s in interior:
        if time_s in events:
            continue
        assert time_s % spacing_s == pytest.approx(0.0, abs=1e-9)


def test_a_following_window_reuses_every_column_time_but_its_edge() -> None:
    """A frame moves one point rather than all of them.

    `PL-Q197` measured that every drawn point moving on every frame was what saturated the
    client. Anchoring the evaluation times to the run applies that fix to the closed-form
    path. So a window that advances by less than the spacing keeps every interior column it
    had.
    """

    _, definition, _ = _stepped_run()
    spacing_s = 4.0
    # Neither edge is a multiple of the spacing, which is the ordinary case. The right edge
    # is whatever instant the run has reached in this frame.
    before = set(definition.evaluate_anchored(0.0, 401.0, spacing_s).times_s)
    after = set(definition.evaluate_anchored(0.0, 402.0, spacing_s).times_s)

    # Only the old right-hand bound leaves, and only the new one arrives. Every interior
    # column keeps the instant it had, so its drawn point does not move and the client is
    # not sent it.
    assert before - after == {401.0}
    assert after - before == {402.0}


def test_every_control_event_inside_the_window_is_a_column() -> None:
    """The drawn chart reproduces every control change.

    A grid alone steps over a dial change. The trajectory's only sharp features are at
    events, so a window that misses one draws a straight line through the single instant
    that a reader is looking for.
    """

    _, definition, _ = _stepped_run()
    # The spacing is far wider than the gap between the two recorded changes, so no grid
    # column could land on either change by luck.
    window = definition.evaluate_anchored(0.0, 600.0, 250.0)
    events = {
        segment.opening.instant_s
        for segment in definition.segments
        if 0.0 < segment.opening.instant_s < 600.0
    }

    assert events
    assert events <= set(window.times_s)


def test_an_event_column_is_its_own_keyframe_exactly() -> None:
    """An event column is read, not propagated, so it carries no interval, error or cost."""

    _, definition, _ = _stepped_run()
    window = definition.evaluate_anchored(0.0, 600.0, 250.0)
    by_time = dict(zip(window.times_s, window.states, strict=True))

    for segment in definition.segments:
        if 0.0 < segment.opening.instant_s < 600.0:
            assert by_time[segment.opening.instant_s].values == segment.opening.state


def test_anchored_matches_a_stepped_run() -> None:
    """Every anchored column is the state the stepped run actually reached."""

    _, definition, stepped = _stepped_run()
    window = definition.evaluate_anchored(0.0, 600.0, SIMULATION_STEP_S * 10)

    for elapsed_s, state in zip(window.times_s, window.states, strict=True):
        expected = stepped[round(elapsed_s, 6)]

        for compartment, want in zip(COMPARTMENT_STATES, expected, strict=True):
            assert abs(state.values[compartment] - want) < WORST_DISPLAY_DIFFERENCE


def test_both_bounds_are_columns_so_the_trace_ends_where_the_readouts_do() -> None:
    """The right-hand end of a trace is the instant the readouts are showing."""

    _, definition, _ = _stepped_run()
    window = definition.evaluate_anchored(103.0, 297.5, 7.0)

    assert window.times_s[0] == 103.0
    assert window.times_s[-1] == 297.5


def test_an_anchored_window_of_no_width_is_one_column() -> None:
    """Both bounds are the same instant, so the window is that instant alone."""

    _, definition, _ = _stepped_run(steps=100)
    window = definition.evaluate_anchored(6.0, 6.0, 1.0)

    assert window.times_s == (6.0,)
    assert window.states[0] == DisplayState(definition.state_at(6.0))


@pytest.mark.parametrize("spacing_s", [0.0, -1.0, float("inf"), float("nan")])
def test_an_anchored_window_refuses_a_spacing_that_is_not_an_interval(spacing_s: float) -> None:
    """A column spacing must be a positive, finite interval."""

    _, definition, _ = _stepped_run(steps=100)

    with pytest.raises(
        SimulationConfigurationError,
        match="^spacing_s must be positive and finite" + REFUSAL_REASON,
    ):
        definition.evaluate_anchored(0.0, 10.0, spacing_s)


def test_an_anchored_window_refuses_a_spacing_that_is_not_a_number() -> None:
    """Python treats `True` as 1, but a spacing of `True` seconds is not what a caller meant."""

    _, definition, _ = _stepped_run(steps=100)

    with pytest.raises(TypeError, match="^spacing_s of True has type bool"):
        definition.evaluate_anchored(0.0, 10.0, True)


@pytest.mark.parametrize("spacing_s", [5e-324, 1e-310])
def test_an_anchored_window_refuses_a_spacing_too_fine_to_count(spacing_s: float) -> None:
    """A spacing whose grid cannot be counted is refused by name (`PL-YZ17`).

    `_anchored_columns` takes `int(stop_s // spacing_s)`. That quotient is infinite here,
    so `int()` raised a bare `OverflowError`, which is not one of the simulator's own
    exceptions.
    """

    _, definition, _ = _stepped_run(steps=100)

    with pytest.raises(SimulationConfigurationError, match="than can be counted") as raised:
        definition.evaluate_anchored(6.0, 7.0, spacing_s)

    assert f"{spacing_s} s" in str(raised.value)


def test_an_anchored_window_draws_a_spacing_finer_than_the_smallest_step_exactly() -> None:
    """A spacing below `MINIMUM_SIMULATION_STEP_S` is accepted, and on purpose.

    The minimum step exists because a run chains its step without limit, so the rounding in
    each step's change accumulates over the run. A grid chains its spacing at most once per
    column, so its rounding cannot accumulate. Every column here still lands on the run's
    own state to within the display tolerance. Applying the same minimum to the spacing
    would refuse narrow axes that the controller draws today (`PL-YZ17`).
    """

    _, definition, _ = _stepped_run(steps=100)
    spacing_s = MINIMUM_SIMULATION_STEP_S / 10.0
    window = definition.evaluate_anchored(6.0, 6.01, spacing_s)

    assert len(window.times_s) > 90

    for time_s, state in zip(window.times_s, window.states, strict=True):
        exact = definition.state_at(time_s)

        for index in COMPARTMENT_STATES:
            assert abs(state.values[index] - exact[index]) < WORST_DISPLAY_DIFFERENCE


def test_an_anchored_window_refuses_bounds_the_run_has_not_reached() -> None:
    """A window past the run's duration would be a prediction rather than the run."""

    _, definition, _ = _stepped_run(steps=100)

    with pytest.raises(SimulationConfigurationError):
        definition.evaluate_anchored(0.0, definition.reached_s + 1.0, 1.0)

    with pytest.raises(SimulationConfigurationError):
        definition.evaluate_anchored(5.0, 1.0, 1.0)


"""Keeping the chart's propagators from one frame to the next (`PL-CNCF`).

A frame asks `evaluate_anchored` for nearly every propagator that the frame before it used,
so the run definition keeps them. The claim has three parts, and they are tested
separately. First, a window drawn from kept propagators is bit for bit the window drawn
with nothing kept. Second, the propagators are kept at all. Without that second test, the
first would pass on a store that keeps nothing. Third, no canonical result reads them.
"""

CHART_SPACING_S = 900.0 / 1068
"""A 15-minute time base across 1 069 columns, as the dashboard divides it."""

WINDOW_OPENING_S = 1100.0
WINDOW_CLOSING_S = 2000.0
"""A 15-minute window that ends at the run's reach and contains both of the run's changes."""


def _a_run_with_two_changes_in_view() -> tuple[AgentUptakeSystem, RunDefinition]:
    """Return a sevoflurane run that reaches 2000 s, with changes at 1300 s and 1600 s.

    The system is returned too, so that a test can record a further change the way the app
    layer does: the setter first, then the settings that the system now holds.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    definition.advance_to(CaseInstant(1300.0))
    system.set_delivered_concentration_percent(Percent(3.0))
    definition.record_change(system.equation_settings())
    definition.advance_to(CaseInstant(1600.0))
    system.set_fresh_gas_flow(FreshGasFlow(1.0))
    definition.record_change(system.equation_settings())
    definition.advance_to(CaseInstant(WINDOW_CLOSING_S))

    # A change to a setting already in force records nothing. So a value equal to the
    # agent's default would leave one stretch fewer than the tests count on.
    assert len(definition.segments) == 3

    return system, definition


def _afresh(definition: RunDefinition) -> RunDefinition:
    """Return the same run rebuilt from its own segments, so it holds nothing a window kept."""

    first, *rest = definition.segments
    twin = RunDefinition(first.settings, first.opening.state, opened_at_s=first.opening.instant_s)

    for segment in rest:
        twin.advance_to(segment.opening.instant_s)
        twin.record_change(segment.settings)

    twin.advance_to(definition.reached_s)

    assert twin.segments == definition.segments

    return twin


def _bits(window: SampledWindow) -> list[tuple[str, ...]]:
    """Return every drawn value as its exact bits, so that even the sign of a zero is compared."""

    return [tuple(value.hex() for value in state.values) for state in window.states]


class _NothingKept:
    """A stand-in for `run_definition._WindowPropagators` that forms each propagator afresh.

    This is the reference that a store of kept propagators is compared against. If the
    reference were drawn through the same code with reuse in place, a store that returned
    the propagator for the wrong stretch would agree with itself. It would then also agree
    with a reference that kept propagators the same way.
    """

    def __init__(self, kept: object) -> None:
        self.used: dict[object, Matrix] = {}

    def over(self, settings: UptakeEquationSettings, interval_s: float) -> Matrix:
        return matrix_exponential(build_system_matrix(settings), interval_s)


def _drawn_with_nothing_kept(
    definition: RunDefinition,
    monkeypatch: pytest.MonkeyPatch,
    start_s: float,
    stop_s: float,
    spacing_s: float,
) -> SampledWindow:
    """Return the window that a rebuilt copy of the run draws, forming every propagator afresh."""

    twin = _afresh(definition)

    with monkeypatch.context() as patch:
        patch.setattr(run_definition, "_WindowPropagators", _NothingKept)

        return twin.evaluate_anchored(start_s, stop_s, spacing_s)


def test_a_window_drawn_from_kept_propagators_is_the_window_drawn_afresh(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Keeping propagators across frames moves no drawn value by so much as a bit.

    The test draws frame after frame of a window that follows the run. The window's left edge passes
    a grid column every few frames. The run records a change along the way, which brings into view a
    stretch that nothing was kept for. The window also switches to a new time base, whose spacing is
    one that no propagator was kept for. Each frame is compared with the same run drawn with nothing
    kept. So a propagator kept under the wrong key, either the wrong stretch's or the wrong
    interval's, shows up as a drawn value that moved.
    """

    system, definition = _a_run_with_two_changes_in_view()
    spacing_s = CHART_SPACING_S

    for frame in range(1, 13):
        reach_s = CaseInstant(WINDOW_CLOSING_S + 0.2 * frame)
        definition.advance_to(reach_s)

        if frame == 3:
            system.set_delivered_concentration_percent(Percent(3.5))
            definition.record_change(system.equation_settings())

            assert len(definition.segments) == 4

        if frame == 8:
            spacing_s = 2 * CHART_SPACING_S

        start_s = reach_s - 1068 * spacing_s
        drawn = definition.evaluate_anchored(start_s, reach_s, spacing_s)
        afresh = _drawn_with_nothing_kept(definition, monkeypatch, start_s, reach_s, spacing_s)

        assert drawn.times_s == afresh.times_s
        assert _bits(drawn) == _bits(afresh)


def _counting_exponentials(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Count every matrix exponential the run definition forms, by its interval."""

    formed: list[float] = []
    exact = run_definition.matrix_exponential

    def counting_exponential(matrix: Matrix, interval_s: float) -> Matrix:
        formed.append(interval_s)

        return exact(matrix, interval_s)

    monkeypatch.setattr(run_definition, "matrix_exponential", counting_exponential)

    return formed


def test_a_window_drawn_again_forms_only_what_it_did_not_keep(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The propagators are kept, so the test above is not passing on a store that keeps nothing.

    The test counts exponentials rather than timing them, as
    `test_a_window_reads_only_the_segments_it_covers` does. The claim is about which matrix
    exponentials a frame forms, and a clock would check the same thing less reliably.
    """

    _, definition = _a_run_with_two_changes_in_view()
    formed = _counting_exponentials(monkeypatch)

    definition.evaluate_anchored(WINDOW_OPENING_S, WINDOW_CLOSING_S, CHART_SPACING_S)

    # Three stretches are in view, with two propagators each: the offset to the stretch's
    # first grid column, and the spacing. There is also one propagator for each bound.
    assert len(formed) == 3 * 2 + 2

    formed.clear()
    definition.evaluate_anchored(WINDOW_OPENING_S, WINDOW_CLOSING_S, CHART_SPACING_S)

    assert formed == []

    # One frame later, with the window following the run, only the two bounds have moved.
    # The window's left edge stays short of its next grid column, so the offset to the first
    # column that it draws in that stretch is the one already kept.
    first_column = int(WINDOW_OPENING_S // CHART_SPACING_S) + 1

    assert WINDOW_OPENING_S + 0.2 < first_column * CHART_SPACING_S < WINDOW_OPENING_S + 0.6

    definition.advance_to(CaseInstant(WINDOW_CLOSING_S + 0.2))
    definition.evaluate_anchored(WINDOW_OPENING_S + 0.2, WINDOW_CLOSING_S + 0.2, CHART_SPACING_S)

    assert sorted(formed) == pytest.approx(
        [WINDOW_CLOSING_S + 0.2 - 1600.0, WINDOW_OPENING_S + 0.2]
    )

    # Once the left edge passes that column, the stretch that the window opens in starts at
    # the next column, so that stretch's offset is formed too. That is the most a following
    # frame forms when no stretch is newly in view.
    formed.clear()
    definition.advance_to(CaseInstant(WINDOW_CLOSING_S + 0.6))
    definition.evaluate_anchored(WINDOW_OPENING_S + 0.6, WINDOW_CLOSING_S + 0.6, CHART_SPACING_S)

    assert sorted(formed) == pytest.approx(
        [
            WINDOW_CLOSING_S + 0.6 - 1600.0,
            WINDOW_OPENING_S + 0.6,
            (first_column + 1) * CHART_SPACING_S,
        ]
    )


def test_only_the_last_window_s_propagators_are_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    """What is kept is bounded by one window, rather than grown by every window drawn.

    A window at another spacing and with other bounds asks for none of the first window's
    propagators. So after that window, the first window forms all of its propagators again.
    This shows that the store was replaced, not added to, and that a run drawn for hours
    keeps no more than one window's worth.
    """

    _, definition = _a_run_with_two_changes_in_view()
    formed = _counting_exponentials(monkeypatch)

    definition.evaluate_anchored(WINDOW_OPENING_S, WINDOW_CLOSING_S, CHART_SPACING_S)
    first = sorted(formed)
    definition.evaluate_anchored(WINDOW_OPENING_S - 100.0, WINDOW_CLOSING_S - 50.0, 1.0)
    formed.clear()
    definition.evaluate_anchored(WINDOW_OPENING_S, WINDOW_CLOSING_S, CHART_SPACING_S)

    assert sorted(formed) == first


class _Untouchable:
    """A store that fails on any read, so a canonical result that consults it is caught."""

    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"a canonical answer read `{name}` on the chart's kept propagators")


def test_a_canonical_answer_reads_nothing_the_chart_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    """`state_at` and the keyframes come from the definition alone, whatever a window kept.

    Comparing results cannot show this. A kept propagator read under its own key is exact,
    so a canonical path that consulted the store would agree with one that did not, until a
    key was wrong. So the test swaps the store for one that fails on any read, under any key.
    """

    system, definition = _a_run_with_two_changes_in_view()
    instants = (650.0, 1300.0, 1450.25, WINDOW_CLOSING_S)
    before = [definition.state_at(instant_s) for instant_s in instants]

    definition.evaluate_anchored(WINDOW_OPENING_S, WINDOW_CLOSING_S, CHART_SPACING_S)
    monkeypatch.setattr(definition, "_last_window_propagators", _Untouchable())

    assert [definition.state_at(instant_s) for instant_s in instants] == before

    # A keyframe recorded now is the same one that the run, rebuilt from its settings, records.
    definition.advance_to(CaseInstant(WINDOW_CLOSING_S + 30.0))
    system.set_delivered_concentration_percent(Percent(3.5))
    definition.record_change(system.equation_settings())

    assert _afresh(definition).segments == definition.segments


"""Why a branch's definition opens at a keyframe, measured rather than asserted (`PL-TFX5`).

No way of opening a fork restarts a definition at the fork, and `docs/MODEL.md` § "The canonical
evaluation rule" says why. Restarting from the canonical state, at an instant for which the run
holds no keyframe, replaces one propagation over an interval with two propagations over its halves.
A fork between two keyframes opens its definition at the earlier keyframe instead
(`SimulationController._open_at`). So when `resumed_at` refuses such an instant, the refusal is
about the scope of that method, not about this arithmetic (`PL-54V0`). That section measures what
the substitution costs. The test here measures that it costs anything at all, which is the half that
the design rests on. Without this test, nothing would catch a way of opening a fork being rebuilt as
a restart, on the grounds that the difference is too small to matter.
"""

# The divergence one hour past a fork at 655.3 s, on the two-change sevoflurane run below.
# It is pinned as a ceiling rather than as an equality, because it is a floating-point
# composition difference. A compiler, a platform or an unrelated change in
# `matrix_exponential` may move it. The claim needs only that the divergence is real and
# this small. Its order of magnitude agrees with the 5.3e-13 accumulator figure that
# `docs/MODEL.md` records for the same substitution on a different run. That section is the
# authority for the size, and this constant is not a second claim about it.
FORK_OFF_KEYFRAME_DIVERGENCE_CEILING = 1e-12

FORK_S = 655.3
PROBES_S = (700.0, 800.0, 900.0, 1200.0, 1800.0, 3600.0)


def _two_change_run() -> RunDefinition:
    """Return a one-hour sevoflurane run that carries two setting changes."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )

    definition.advance_to(CaseInstant(300.0))
    system.set_delivered_concentration_percent(Percent(2.0))
    definition.record_change(system.equation_settings())
    definition.advance_to(CaseInstant(600.0))
    system.set_fresh_gas_flow(FreshGasFlow(1.0))
    definition.record_change(system.equation_settings())
    definition.advance_to(CaseInstant(3600.0))

    return definition


def _worst(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return max(abs(a - b) for a, b in zip(left, right, strict=True))


def test_opening_a_branch_off_a_keyframe_does_not_reproduce_the_run() -> None:
    """This test measures the reason for the refusal as a number.

    A branch opened from the canonical state, at an instant for which the run holds no
    keyframe, reaches that state by one propagation and then continues by a second. The run
    computes the state at the same later instant with one propagation over the whole span. The two
    results are the same exact solution rounded differently, which is precisely what
    `PL-Z3W6`'s element-wise requirement refuses. So this test asserts that the disagreement
    is non-zero as well as small. A test that only bounded it would still pass if forking
    became exact by accident, and it would then stop describing anything.

    Both runs are asked for the same instant as the same float, because the branch opens at
    the fork on the case's own time axis (`PL-ZMRT`). So the measurement contains one
    propagation against two and nothing else. A branch re-based to its own zero would have
    carried a frame conversion into the same number.
    """

    parent = _two_change_run()
    branch = RunDefinition(
        parent.segments[-1].settings, parent.state_at(FORK_S), opened_at_s=CaseInstant(FORK_S)
    )
    branch.advance_to(CaseInstant(3600.0))

    divergences = [_worst(branch.state_at(p), parent.state_at(p)) for p in PROBES_S]

    assert all(divergence > 0.0 for divergence in divergences)
    assert max(divergences) < FORK_OFF_KEYFRAME_DIVERGENCE_CEILING


def test_a_pixel_wide_chord_misses_an_extremum_by_under_the_readout_s_resolution() -> None:
    """This checks `PL-GS3R`'s guarantee at the one point where the pixel argument does not apply.

    Take two drawn instants that are both exact and no more than a pixel of time apart.
    Between them, a *monotone* run and the straight segment drawn between them cross every
    level inside the same pixel. Where the run turns between two dial changes, it can rise
    above both drawn values inside one interval, and the line falls short of it there. The
    run turns because the alveoli and the venous blood keep filling for a moment after the
    vaporizer is turned down. The worst case, measured on 2026-09-14 over the supported
    envelope, is this one. It is a desflurane overpressure induction at the fastest
    supported settings, turned down at 600 s, and drawn at the twelve-hour time base on a
    1 000 px plot. There the mixed venous trace rises 0.0028 pp above the drawn line at
    t = 609 s. The limit is set at half the readout's resolution, so a real regression fails
    and the closed form's floating-point wobble does not. The true values are taken over the
    1 800 s after each change, which is where every measured departure lies. Beyond that
    span, the same run stays within 0.0024 pp, even at the 290 s chord that the fixed budget
    used to draw.
    """

    system = AgentUptakeSystem.for_agent("desflurane")
    system.set_fresh_gas_flow(FreshGasFlow(10.0))
    system.set_alveolar_ventilation(AlveolarVentilation(12.0))
    system.set_cardiac_output(CardiacOutput(10.0))
    system.set_delivered_concentration_percent(Percent(12.0))
    definition = RunDefinition(
        system.equation_settings(), system.state_vector(), opened_at_s=CaseInstant(0.0)
    )
    definition.advance_to(CaseInstant(600.0))
    system.set_delivered_concentration_percent(Percent(6.0))
    definition.record_change(system.equation_settings())
    definition.advance_to(CaseInstant(43_200.0))

    pixel_s = 43_200.0 / 1000.0
    drawn = definition.evaluate_anchored(0.0, 43_200.0, pixel_s)
    last = len(drawn.states) - 1
    fractions = (
        INSPIRED_FRACTION,
        ALVEOLAR_FRACTION,
        VENOUS_FRACTION,
        FIRST_TISSUE_FRACTION,
        FIRST_TISSUE_FRACTION + 1,
        FIRST_TISSUE_FRACTION + 2,
    )
    worst = 0.0

    for opening_s in (0.0, 600.0):
        truth = definition.evaluate_anchored(opening_s, opening_s + 1800.0, 0.1)

        for instant_s, state in zip(truth.times_s, truth.states, strict=True):
            after = bisect_right(drawn.times_s, instant_s)
            left = drawn.states[max(after - 1, 0)].values
            right = drawn.states[min(after, last)].values

            for index in fractions:
                low, high = min(left[index], right[index]), max(left[index], right[index])
                worst = max(worst, state.values[index] - high, low - state.values[index])

    assert worst * 100.0 < 0.005
