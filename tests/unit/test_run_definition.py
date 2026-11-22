"""Check the record of the settings that each stretch of a run was stepped under.

A `RunDefinition` holds one stretch for each setting change: its settings, and
the second of the case at which it opened. It computes no state. The tests
here check what the record keeps when a setting changes, which stretch it
names for a second, and which openings and reaches it refuses.
"""

from dataclasses import replace
from math import inf, nan, nextafter

import pytest

from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import UptakeEquationSettings
from anesthesia_sim.core.run_definition import RunDefinition
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MAXIMUM_STEP_COUNT,
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
    StepCount,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

# The end of a shared guard's refusal message, which names the refused value and the reason
# (`PL-T137`). The guard's own tests check each reason. The tests here check the field name.
REFUSAL_REASON = r", and [^ ]+ is (?:not finite|not greater than zero|negative)$"


def test_a_run_under_unchanged_settings_is_one_segment() -> None:
    """Recording the settings already in force describes no change, so none is kept."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))
    definition.advance_to(CaseInstant(10))
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 1


def test_two_changes_at_one_instant_are_one_segment() -> None:
    """Two controls moved between the same two steps open one new segment, not two.

    The run was computed under whatever settings applied when the step ran, so a
    zero-length segment would describe a stretch of time that the model never integrated.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))
    definition.advance_to(CaseInstant(10))
    system.set_delivered_concentration_percent(Percent(3.0))
    definition.record_change(system.equation_settings())
    system.set_cardiac_output(CardiacOutput(4.0))
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 2
    assert definition.segments[-1].opened_at_s == 10.0
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
        definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))
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
        # The reproduction scaled the tissue flows to sum to the cardiac output. A tissue
        # flow is now built only as a fraction of a supported cardiac output (`PL-GKG4`), so
        # those scaled flows cannot be built either. The record refuses the cardiac output
        # before it compares the flows with it.
        changed: dict[str, object] = {field: value}

        return replace(held, **changed)

    definition = RunDefinition(held, opened_at_s=CaseInstant(0))
    definition.advance_to(CaseInstant(30))
    segments = definition.segments
    refused = f"not built as {flow_type.__name__}"

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        RunDefinition(rebuilt(flow_type(reproduced_l_min)), opened_at_s=CaseInstant(0))

    with pytest.raises(TypeError, match=refused):
        RunDefinition(rebuilt(reproduced_l_min), opened_at_s=CaseInstant(0))

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

    definition = RunDefinition(held, opened_at_s=CaseInstant(0))
    definition.advance_to(CaseInstant(30))
    segments = definition.segments

    with pytest.raises(SimulationConfigurationError, match=reproduced):
        RunDefinition(
            replace(held, delivered_concentration_percent=Percent(20.0)), opened_at_s=CaseInstant(0)
        )

    with pytest.raises(SimulationConfigurationError, match=reproduced):
        definition.record_change(replace(held, delivered_concentration_percent=Percent(20.0)))

    past_the_maximum = Percent(nextafter(maximum, inf))

    with pytest.raises(SimulationConfigurationError, match="exceeds the vaporizer maximum"):
        RunDefinition(
            replace(held, delivered_concentration_percent=past_the_maximum),
            opened_at_s=CaseInstant(0),
        )

    with pytest.raises(SimulationConfigurationError, match="exceeds the vaporizer maximum"):
        definition.record_change(replace(held, delivered_concentration_percent=past_the_maximum))

    assert definition.segments == segments

    at_the_maximum = replace(held, delivered_concentration_percent=maximum)
    opened = RunDefinition(at_the_maximum, opened_at_s=CaseInstant(0))
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
        definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))
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
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))
    definition.advance_to(CaseInstant(12))
    system.set_fresh_gas_flow(FreshGasFlow(1.5))
    definition.record_change(system.equation_settings())

    assert [segment.opened_at_s for segment in definition.segments] == [0, 12]


def _changed_at_12_and_30() -> RunDefinition:
    """A run opened at 0 s at 4 L/min, changed to 1.5 L/min at 12 s and to 6 L/min at 30 s."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    system.set_fresh_gas_flow(FreshGasFlow(4.0))
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))

    for instant_s, flow_l_min in ((12, 1.5), (30, 6.0)):
        definition.advance_to(CaseInstant(instant_s))
        system.set_fresh_gas_flow(FreshGasFlow(flow_l_min))
        definition.record_change(system.equation_settings())

    return definition


def test_the_reaching_stretch_at_a_keyframe_is_the_one_before_it() -> None:
    """At a keyframe the step that arrived ran under the stretch before it, not the one opening.

    The expected flows are the ones the helper dialled. Between keyframes
    the reaching stretch and `segment_at` are the same stretch. At a
    keyframe they are the stretches on either side of it (`PL-ZR49`).
    """

    definition = _changed_at_12_and_30()

    def flows(instant_s: float) -> tuple[float, float]:
        return (
            definition.reaching_segment_at(instant_s).settings.fresh_gas_flow_l_min,
            definition.segment_at(instant_s).settings.fresh_gas_flow_l_min,
        )

    assert flows(6.0) == (4.0, 4.0)
    assert flows(12.0) == (4.0, 1.5)
    assert flows(20.0) == (1.5, 1.5)
    assert flows(30.0) == (1.5, 6.0)


def test_the_reaching_stretch_at_the_opening_is_the_first_stretch() -> None:
    """No step reaches the opening, so the first stretch is the reaching stretch there."""

    definition = _changed_at_12_and_30()

    assert definition.reaching_segment_at(0.0) == definition.segments[0]


def test_a_change_at_the_reached_instant_never_replaces_the_reaching_stretch() -> None:
    """Setting the dial back at the reached instant removes the open stretch, not the reaching one.

    When a stretch already opens at the instant of a change, `record_change`
    folds the change into that stretch. The stretch that the reaching step ran
    under opens earlier, so no change made while the run stands at 30 s can
    touch it. That is what makes it a provenance that cannot later point at
    nothing.
    """

    definition = _changed_at_12_and_30()
    reaching = definition.reaching_segment_at(30.0)
    system = AgentUptakeSystem.for_agent("sevoflurane")

    for flow_l_min in (8.0, 1.5):
        system.set_fresh_gas_flow(FreshGasFlow(flow_l_min))
        definition.record_change(system.equation_settings())

        assert definition.reaching_segment_at(30.0) == reaching
        assert reaching in definition.segments

    assert [segment.opened_at_s for segment in definition.segments] == [0, 12]


@pytest.mark.parametrize("instant_s", [-0.1, 30.1, nan, inf])
def test_the_reaching_stretch_is_refused_outside_the_run(instant_s: float) -> None:
    """An instant the run has not covered has no reaching stretch, as it has no state."""

    with pytest.raises(SimulationConfigurationError):
        _changed_at_12_and_30().reaching_segment_at(instant_s)


def test_the_run_starts_where_the_system_does() -> None:
    """A definition has reached the second it opened at, and holds one stretch there."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))

    assert definition.reached_s == 0.0
    assert [segment.opened_at_s for segment in definition.segments] == [0]
    assert definition.segment_at(0.0).settings == system.equation_settings()


def test_advancing_to_the_time_already_reached_changes_nothing() -> None:
    """Advancing twice to the same instant is not an error."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))
    definition.advance_to(CaseInstant(5))
    definition.advance_to(CaseInstant(5))

    assert definition.reached_s == 5.0


@pytest.mark.parametrize("opened_at_s", [nan, inf, -inf, -1.0])
def test_an_opening_that_is_not_a_whole_second_cannot_be_built(opened_at_s: float) -> None:
    """The instant is refused where it is built, before any run can open at it (`PL-CN5S`).

    Every later result is measured from the opening instant. A definition opened at a
    non-finite instant would propagate over a non-finite interval and return a state of
    `nan`. No bounds check downstream could tell that state apart from a run that genuinely
    reached such a state. A non-finite number is a `float`, and an instant of the case is a
    whole number of seconds, so `CaseInstant` refuses it by its type. It refuses a finite
    `float` the same way, whatever its value.
    """

    with pytest.raises(TypeError, match="^instant_s of .* has type float, not int: "):
        CaseInstant(opened_at_s)  # type: ignore[arg-type]


@pytest.mark.parametrize("opened_at_s", [-1, -3600])
def test_an_opening_before_the_case_began_cannot_be_built(opened_at_s: int) -> None:
    """The case's time axis starts at induction, so no run on it opens before zero (`PL-CN5S`).

    `CaseInstant` refuses the instant in the words of the supported run length.
    """

    with pytest.raises(SimulationConfigurationError, match="outside the supported run length"):
        CaseInstant(opened_at_s)


@pytest.mark.parametrize("opened_at_s", [0, 30, 0.0, nan, -1.0])
def test_a_run_definition_refuses_an_opening_not_built_as_a_case_instant(
    opened_at_s: float,
) -> None:
    """The opening is refused whatever its value, because nothing has checked it (`PL-CN5S`).

    `mypy` refuses a bare `int` or `float` here. This test covers the callers that a type checker
    cannot check: a test, a notebook, or a value typed `Any`. The opening is refused before
    the definition exists. Every stretch of the run is placed by it.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")

    with pytest.raises(TypeError, match="opened_at_s of .* was not built as CaseInstant"):
        RunDefinition(
            system.equation_settings(),
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
        system.equation_settings(), opened_at_s=CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S)
    )

    assert definition.opened_at_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S
    assert (
        definition.segment_at(MAXIMUM_ELAPSED_SIMULATION_TIME_S).settings
        == system.equation_settings()
    )


@pytest.mark.parametrize(
    "opened_at_s", [MAXIMUM_ELAPSED_SIMULATION_TIME_S + 1, MAXIMUM_ELAPSED_SIMULATION_TIME_S + 3600]
)
def test_opening_past_the_supported_envelope_cannot_be_built(opened_at_s: int) -> None:
    """The opening is refused where it is built, not at the first step after it (`PL-73ZN`).

    The opening is the origin of every instant that a branch reports, so an opening past the
    envelope would carry the error into every value read from the run. The edge is the
    declared constant itself, and the next whole second past it is refused. The message
    names the exact value and the envelope that it is outside. Since `PL-CN5S`, the refusal
    comes from the `CaseInstant` that the opening is built as, so no definition is ever given
    such an opening.
    """

    with pytest.raises(SimulationConfigurationError, match="supported run length") as raised:
        CaseInstant(opened_at_s)

    assert f"a case instant of {opened_at_s} s" in str(raised.value)
    assert "0 to 86400 s" in str(raised.value)


def test_a_run_refuses_to_go_backwards() -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))
    definition.advance_to(CaseInstant(20))

    with pytest.raises(SimulationConfigurationError, match="cannot go back"):
        definition.advance_to(CaseInstant(19))


def test_a_non_finite_reach_cannot_be_built() -> None:
    """A non-finite reach is a `float`, which is refused when built (`PL-CN5S`).

    So no run can be moved to one.
    """

    with pytest.raises(TypeError, match="^instant_s of inf has type float, not int: "):
        CaseInstant(inf)  # type: ignore[arg-type]


@pytest.mark.parametrize("instant_s", [30, 30.0, inf])
def test_a_run_refuses_a_reach_not_built_as_a_case_instant(instant_s: float) -> None:
    """The reach is refused whatever its value, and before the reach moves (`PL-CN5S`)."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))
    definition.advance_to(CaseInstant(20))

    with pytest.raises(TypeError, match="instant_s of .* was not built as CaseInstant"):
        definition.advance_to(instant_s)  # type: ignore[arg-type]

    assert definition.reached_s == 20.0


def test_a_run_may_reach_the_end_of_the_supported_run_length() -> None:
    """The reach has the same closed bound as the opening, so a run may reach the far end."""

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))

    definition.advance_to(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))

    assert definition.reached_s == MAXIMUM_ELAPSED_SIMULATION_TIME_S


@pytest.mark.parametrize(
    "instant_s", [MAXIMUM_ELAPSED_SIMULATION_TIME_S + 1, MAXIMUM_ELAPSED_SIMULATION_TIME_S + 3600]
)
def test_a_reach_past_the_supported_run_length_cannot_be_built(instant_s: int) -> None:
    """A reach past the span cannot be built, so the run cannot be moved there.

    Until `PL-8H2R` the reach was unguarded. A run could then take a step of a length that
    the caller chose. At a length whose quotient rounded up, the last step that a run took
    landed on a float just past the span, and a bound here would have refused it. A run now
    stops on the last whole second inside the span, so the reach carries the opening's
    bound. Since `PL-CN5S`, that bound is enforced by the `CaseInstant` that the reach is
    moved to, which is refused when it is built.
    """

    with pytest.raises(SimulationConfigurationError, match="supported run length") as raised:
        CaseInstant(instant_s)

    assert f"a case instant of {instant_s} s" in str(raised.value)


def test_a_run_may_reach_the_last_step_it_is_allowed_to_take() -> None:
    """The reach follows the step count to its limit, never past it.

    The application moves the reach to each step's `elapsed_s`, so the guard on the reach
    must accept the last step that `SimulationState` allows. That step is the 86 400th, and
    it lands on the last second of the supported run length (`PL-8H2R`).
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))
    last_step_s = SimulationState(step_count=StepCount(MAXIMUM_STEP_COUNT)).elapsed_s

    definition.advance_to(last_step_s)

    assert definition.reached_s == last_step_s == 86_400


@pytest.mark.parametrize("instant_s", [nan, inf])
def test_a_run_definition_refuses_a_non_finite_instant(instant_s: float) -> None:
    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))

    with pytest.raises(SimulationConfigurationError, match="not a finite instant"):
        definition.segment_at(instant_s)


def _opening_after_zero() -> RunDefinition:
    """Return a definition that opens at 600 s, as a branch forked at that instant does.

    Since `PL-ZMRT` it is built through the public constructor. The run opens on the case's
    own time axis at 600 s and records a change at 900 s. So the guards below are exercised
    against the arrangement that `SimulationController` actually builds, not against a
    synthesized one.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    system.set_delivered_concentration_percent(Percent(2.0))
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(600))

    definition.advance_to(CaseInstant(900))
    system.set_delivered_concentration_percent(Percent(0.5))
    definition.record_change(system.equation_settings())

    definition.advance_to(CaseInstant(1200))

    return definition


def test_a_run_definition_reports_the_instant_it_opens_at() -> None:
    """This is the one place where a definition's own opening is named, and it is not the reach.

    The test reads the opening directly rather than through a caller, because since `PL-B8MK` the
    app layer has its own instant for where a branch begins. A branch's *beginning* is its fork, and
    a bookmark fork puts that fork after the keyframe that its definition opens at. So
    `SimulationController.began_at_s` is what clips a drawn axis, and the opening tested here says
    where the definition's first stretch opens. The two were one number until a bookmark became
    forkable, and a test that reached the opening through the app layer could not tell them apart.
    """

    trunk_shaped = RunDefinition(
        AgentUptakeSystem.for_agent("sevoflurane").equation_settings(), opened_at_s=CaseInstant(0)
    )

    assert trunk_shaped.opened_at_s == 0.0

    branch_shaped = _opening_after_zero()

    # The opening is the first segment's own instant. Recording changes, and advancing the
    # reach past them, leaves the opening where it was.
    assert branch_shaped.opened_at_s == 600.0
    assert branch_shaped.segments[0].opened_at_s == 600.0
    assert branch_shaped.reached_s == 1200.0


def test_a_run_definition_that_opens_after_zero_refuses_the_span_before_it() -> None:
    """The lower bound is the run's own opening, never the literal zero.

    A bound fixed at zero would not cause a wrong refusal. It would cause a silent wrong
    result. `_segment_index_at` returns `-1` for an instant before the first opening, and
    Python treats that index as the *last* segment. So the caller would be given the
    settings of the run's last stretch for an instant when the run did not exist. The
    definition here opens at 600 s under a 2% dial and holds a 0.5% dial from 900 s.
    """

    definition = _opening_after_zero()

    for elapsed_s in (0.0, 100.0, 599.9):
        with pytest.raises(SimulationConfigurationError, match="before it began"):
            definition.segment_at(elapsed_s)

        with pytest.raises(SimulationConfigurationError, match="before it began"):
            definition.reaching_segment_at(elapsed_s)

    assert definition.segment_at(600.0).settings.delivered_concentration_percent == 2.0


def test_a_run_definition_is_under_no_settings_before_it_opens() -> None:
    """This tests the second of the two guards, which only a direct call can reach.

    `_require_within_run` refuses the instant on every public path. So this guard can never
    fire through `segment_at` while that bound is correct. The test exists because the two
    guards protect against the same silent wrong result by different means. The bound says
    that the run had not begun at that instant, and this guard says that the segment search
    found no segment. A future caller that reaches the search without the bound meets a
    refusal rather than the last segment's settings.
    """

    definition = _opening_after_zero()

    with pytest.raises(SimulationConfigurationError, match="under no settings"):
        definition._segment_index_at(599.9)


def test_a_change_undone_before_a_step_runs_leaves_no_segment() -> None:
    """A dial moved and moved back between two steps describes no change at all.

    The stretch that the change opened is dropped, rather than kept with the settings it
    started from. Keeping it would put a stretch in the run definition that opens at an
    instant the run passed through with nothing of note. The interface's own control timeline drops
    the matching entry for the same reason.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))
    definition.advance_to(CaseInstant(10))
    system.set_delivered_concentration_percent(Percent(3.0))
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 2

    # Back to the opening dial: sevoflurane's 1.80%, its MAC at age 40.
    system.set_delivered_concentration_percent(Percent(1.8))
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 1
    assert definition.segments[0].opened_at_s == 0.0


def test_a_change_undone_at_one_instant_keeps_every_earlier_stretch() -> None:
    """Undoing a change drops only the stretch that the change opened.

    The docstring of `record_change` gives the rule. When a second change, at an instant that
    already opened a stretch, returns to the previous stretch's settings, "the stretch goes
    entirely". That stretch is the one opened at that instant, and no earlier one. This run
    has three stretches before the undo. With only two, the wrong slice `segments[:1]` keeps
    the same list as the right one, `segments[:-1]`, and every earlier test of this branch
    used two (`PL-ZH1F`).

    Neither expected value is read from the definition under test. The stretches are
    literals, and the expected record comes from a second definition that was never given
    the 5% change.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    system.set_delivered_concentration_percent(Percent(2.0))
    opening_settings = system.equation_settings()
    undone = RunDefinition(opening_settings, opened_at_s=CaseInstant(0))
    never_changed = RunDefinition(opening_settings, opened_at_s=CaseInstant(0))

    for definition in (undone, never_changed):
        definition.advance_to(CaseInstant(10))
    system.set_delivered_concentration_percent(Percent(3.0))
    for definition in (undone, never_changed):
        definition.record_change(system.equation_settings())
        definition.advance_to(CaseInstant(20))
    system.set_delivered_concentration_percent(Percent(5.0))
    undone.record_change(system.equation_settings())

    assert len(undone.segments) == 3

    system.set_delivered_concentration_percent(Percent(3.0))
    undone.record_change(system.equation_settings())

    assert [
        (segment.opened_at_s, segment.settings.delivered_concentration_percent)
        for segment in undone.segments
    ] == [(0.0, 2.0), (10.0, 3.0)]

    for definition in (undone, never_changed):
        definition.advance_to(CaseInstant(600))

    assert undone.segments == never_changed.segments
    assert undone.segment_at(600.0) == never_changed.segment_at(600.0)


def test_the_first_stretch_is_kept_even_when_a_change_returns_to_it() -> None:
    """There is no earlier stretch to fold the opening stretch back into.

    The run's first segment opens at zero and carries the settings that the run began
    under. So a change recorded at zero replaces those settings, rather than dropping a
    stretch that nothing comes before.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))
    system.set_delivered_concentration_percent(Percent(5.0))
    definition.record_change(system.equation_settings())

    assert len(definition.segments) == 1
    assert definition.segments[0].settings.delivered_concentration_percent == 5.0


def test_recording_a_change_copies_no_segment_already_recorded() -> None:
    """Each accepted change adds one segment and leaves every earlier one as it was.

    The record grows by what the change adds and by nothing else. It stores references, so
    a change copies at most one pointer per segment and never copies a segment's settings.
    The test checks identity rather than equality, because an equal copy of a segment is
    exactly what the test rules out. Three hundred changes is the count over which `PL-1PSX`
    measured this record and the control timeline growing one-for-one.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))

    for change in range(1, 301):
        before = definition.segments
        definition.advance_to(CaseInstant(change * 10))
        system.set_delivered_concentration_percent(Percent(1.0 + 0.5 * (change % 4)))
        definition.record_change(system.equation_settings())
        after = definition.segments

        assert len(after) == len(before) + 1
        assert all(kept is held for kept, held in zip(after[:-1], before, strict=True))


def test_a_record_handed_out_is_not_changed_by_later_changes() -> None:
    """`segments` returns the run as it stood, whatever the run records next.

    This lets a caller read the run without being able to advance it.
    `tests/integration/simulation_view/` relies on it when it compares
    `run_segments` before and after an action. A view that followed the run would make that
    comparison pass whatever the action did. The test exercises every kind of change that
    `record_change` can make, because each one changes the record differently. A change can
    replace the open segment at the instant it opened, drop that segment on a dial-back, or
    append a new segment after it.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    definition = RunDefinition(system.equation_settings(), opened_at_s=CaseInstant(0))
    definition.advance_to(CaseInstant(10))
    system.set_delivered_concentration_percent(Percent(3.0))
    definition.record_change(system.equation_settings())
    held = definition.segments
    contents = list(held)

    # 1.8 is the opening dial, sevoflurane's MAC at age 40.
    for percent, reach_s in ((4.0, 10), (1.8, 10), (5.0, 20)):
        definition.advance_to(CaseInstant(reach_s))
        system.set_delivered_concentration_percent(Percent(percent))
        definition.record_change(system.equation_settings())

        assert len(held) == len(contents)
        assert all(kept is was for kept, was in zip(held, contents, strict=True))

    assert [segment.opened_at_s for segment in definition.segments] == [0.0, 20.0]
