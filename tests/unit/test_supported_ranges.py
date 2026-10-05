"""The declared input domain, and what happens at and outside its edges.

Regression cover for PL-0MLQ: `docs/MODEL.md` declared a closed supported
interval for each control, and only the delivered concentration's was
enforced. `AgentUptakeSystem.set_cardiac_output(1000.0)` was accepted and
simulated, and the interface's sliders were the only thing keeping a run
inside the domain the verification gates cover.

Since `PL-0YYV` each flow is a type - `FreshGasFlow`, `AlveolarVentilation`
and `CardiacOutput` - built only through its guard, and every field that
stores a flow takes the type. The tests under "Each flow is a type" hold that
the type admits and refuses exactly what its guard does, keeps the value it
was built from, and is required wherever a flow is stored. Since `PL-CN5S`
the case instant and the step count are types too, `CaseInstant` and
`StepCount`, and the tests under "The case instant and the step count are
types" hold them to the same.

The endpoints are tested as carefully as the rejections. Every range is
closed, and both ends are load-bearing: one reference gate trajectory holds
cardiac output at zero for its loading phase, and the envelope corner every
reference gate drives sits on all three maxima at once. A guard that quietly
excluded an endpoint would take a measured case out of the reachable domain
without failing anything.
"""

import copy
import pickle
import sys
from collections.abc import Callable
from dataclasses import replace
from math import inf, nan, nextafter
from typing import NamedTuple

import pytest

from anesthesia_sim.core.circuit import BreathingCircuit, DeliverableFreshGasFlowRange
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
)
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
    StepCount,
    describe_count,
    maximum_step_count,
    require_case_instant,
    require_step_count,
    require_supported_alveolar_ventilation,
    require_supported_cardiac_output,
    require_supported_case_instant,
    require_supported_fresh_gas_flow,
    require_supported_run_length,
    require_supported_step_count,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


class Control(NamedTuple):
    """One control: its guard, the type only that guard builds, the closed
    interval it declares, and the compartment of `AgentUptakeSystem` that
    stores it."""

    name: str
    guard: Callable[[float], None]
    flow_type: type[float]
    minimum: float
    maximum: float
    stored_on: str


CONTROLS = (
    Control(
        "fresh_gas_flow_l_min",
        require_supported_fresh_gas_flow,
        FreshGasFlow,
        MINIMUM_FRESH_GAS_FLOW_L_MIN,
        MAXIMUM_FRESH_GAS_FLOW_L_MIN,
        "circuit",
    ),
    Control(
        "alveolar_ventilation_l_min",
        require_supported_alveolar_ventilation,
        AlveolarVentilation,
        MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
        "alveoli",
    ),
    Control(
        "cardiac_output_l_min",
        require_supported_cardiac_output,
        CardiacOutput,
        MINIMUM_CARDIAC_OUTPUT_L_MIN,
        MAXIMUM_CARDIAC_OUTPUT_L_MIN,
        "patient",
    ),
)

CONTROL_IDS = [control.name for control in CONTROLS]


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_accepts_both_endpoints_and_the_interior(control: Control) -> None:
    """The interval is closed, and the endpoints are the measured cases."""

    midpoint = (control.minimum + control.maximum) / 2.0

    for value in (control.minimum, midpoint, control.maximum):
        control.guard(value)


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_rejects_the_smallest_value_above_the_maximum(control: Control) -> None:
    """The refusal starts at the first float outside the interval.

    A guard written with `>=` instead of `>` would pass every other test in
    this module while making the envelope corner — the operating point the
    exact-step reference gate measures at — unreachable.
    """

    with pytest.raises(SimulationConfigurationError):
        control.guard(nextafter(control.maximum, inf))


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
@pytest.mark.parametrize("scale", (2.0, 10.0, 100.0))
def test_rejects_a_flow_far_outside_the_domain(control: Control, scale: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        control.guard(control.maximum * scale)


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
@pytest.mark.parametrize("value", (-1.0, -0.0001, nan, inf, -inf))
def test_rejects_a_value_that_is_negative_or_not_finite(control: Control, value: float) -> None:
    """One guard covers the whole domain, so NaN cannot slip past a comparison.

    `nan` compares false against every bound, so a range check written as two
    comparisons and nothing else would accept it and then poison every
    downstream state silently.
    """

    with pytest.raises(SimulationConfigurationError):
        control.guard(value)


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_the_refusal_names_the_setting_the_value_and_the_interval(control: Control) -> None:
    """A refusal a caller cannot act on is barely better than a wrong number."""

    rejected = control.maximum * 10.0

    with pytest.raises(SimulationConfigurationError) as raised:
        control.guard(rejected)

    message = str(raised.value)

    assert control.name in message
    assert str(rejected) in message
    assert f"{control.minimum} to {control.maximum} L/min" in message


# --- Each flow is a type, built only through its guard (PL-0YYV) ------------
#
# The guard above runs once, where a flow is built as its type, and every field
# and signature past that point takes the type, so the check is made nowhere
# else. That is only as good as the type: it has to hold the value it was built
# from exactly, refuse in the guard's own words, come back from a copy as
# itself, and be demanded wherever a bare float could otherwise be stored in
# its place.


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_the_type_holds_the_value_it_was_built_from_exactly(control: Control) -> None:
    """Built at either end and between, the type is the float it was given, bit for bit.

    A type that rounded or re-derived its value would move the envelope corner
    the reference gates measure at; `hex` compares the bits rather than the
    printed digits, and two of the values carry a full mantissa, since a
    rounding to any number of decimals leaves the endpoints where they are.
    """

    midpoint = (control.minimum + control.maximum) / 2.0
    full_mantissa = (nextafter(control.maximum, -inf), control.maximum / 3.0)

    for value in (control.minimum, midpoint, control.maximum, *full_mantissa):
        built = control.flow_type(value)

        assert isinstance(built, control.flow_type)
        assert isinstance(built, float)
        assert built.hex() == float(value).hex()


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_the_type_refuses_what_its_guard_refuses_in_the_guards_words(control: Control) -> None:
    """One check, so the type can neither admit what the guard refuses nor word it differently."""

    for value in (nextafter(control.maximum, inf), control.maximum * 10.0, -1.0, nan, inf, -inf):
        with pytest.raises(SimulationConfigurationError) as by_the_guard:
            control.guard(value)

        with pytest.raises(SimulationConfigurationError) as by_the_type:
            control.flow_type(value)

        assert str(by_the_type.value) == str(by_the_guard.value)


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_arithmetic_on_a_flow_is_a_plain_float(control: Control) -> None:
    """A quantity derived from a flow is not a checked flow, and must not read as one.

    Two flows at the maximum sum to a value past it; were the sum still the
    type, it would carry a promise of a check that never ran. A subclass of
    `float` returns `float` from every operator, which is what keeps the
    promise to what was actually built.
    """

    at_maximum = control.flow_type(control.maximum)

    assert type(at_maximum + at_maximum) is float
    assert type(at_maximum / 60.0) is float
    assert type(-at_maximum) is float


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_a_flow_survives_copy_and_pickle_as_its_type(control: Control) -> None:
    """A record copied or stored keeps its flows checked, not demoted to floats.

    `dataclasses.replace` copies the fields it is not given, and a saved run
    would come back through `pickle`; each rebuilds the flow through the
    type's own constructor, so the guard runs again and the type is kept.
    """

    built = control.flow_type(control.maximum)

    for copied in (copy.copy(built), copy.deepcopy(built), pickle.loads(pickle.dumps(built))):
        assert type(copied) is control.flow_type
        assert copied == built


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_a_bare_float_is_refused_wherever_a_flow_is_stored(control: Control) -> None:
    """A float never built as the type is refused where it would be stored, in range or not.

    The static half of the check is the annotation, which a caller outside
    `mypy`'s reach - a notebook, a test, a deserializer - never sees. The
    runtime half lives where a flow is stored: the compartment's setter, its
    constructor, and the settings record. Each refuses a bare float and names
    the type to build; the forwarding setter on `AgentUptakeSystem` reaches the
    same refusal. The value is the one already held, so what is refused is the
    missing check and not the number, and nothing changes on refusal.
    """

    system = AgentUptakeSystem.default()
    compartment = getattr(system, control.stored_on)
    setter = f"set_{control.name.removesuffix('_l_min')}"
    held = getattr(compartment, control.name)
    bare = float(held)
    refused = f"not built as {control.flow_type.__name__}"

    assert type(held) is control.flow_type

    with pytest.raises(TypeError, match=refused):
        getattr(compartment, setter)(bare)

    with pytest.raises(TypeError, match=refused):
        getattr(system, setter)(bare)

    with pytest.raises(TypeError, match=refused):
        replace(compartment, **{control.name: bare})

    with pytest.raises(TypeError, match=refused):
        replace(system.equation_settings(), **{control.name: bare})

    assert getattr(compartment, control.name) is held


@pytest.mark.parametrize("control", CONTROLS, ids=CONTROL_IDS)
def test_another_flows_type_is_refused_as_a_swapped_argument(control: Control) -> None:
    """A flow of another type is named as that, and not told to rebuild as this one.

    A fresh gas flow arriving where a cardiac output belongs is a swapped
    argument. A refusal that prescribed `CardiacOutput(4.0)` would have the
    caller check and store the wrong quantity under the right type, so the
    message names the type the value was built as and prescribes nothing.
    """

    system = AgentUptakeSystem.default()
    compartment = getattr(system, control.stored_on)
    setter = getattr(compartment, f"set_{control.name.removesuffix('_l_min')}")
    held = getattr(compartment, control.name)
    other = next(each for each in CONTROLS if each.flow_type is not control.flow_type)

    with pytest.raises(TypeError) as raised:
        setter(other.flow_type(float(held)))

    message = str(raised.value)

    assert f"was built as {other.flow_type.__name__}" in message
    assert f"{control.flow_type.__name__}(" not in message
    assert getattr(compartment, control.name) is held


# --- The supported run length (PL-Y5WR) -------------------------------------
#
# The fifth bound, and the only one on the run rather than on a setting. It is
# regression cover for a limit that was declared in conversation on 2026-08-25,
# recorded in a dropped item, and enforced nowhere: a run could reach day 45 of
# a cap set at 30 days and go on displaying two-decimal concentrations, in a
# regime `docs/MODEL.md` already declines to validate over.
#
# The boundary is pinned in both directions deliberately. A guard that refused
# one step early would take the endpoint out of a closed interval every other
# range in this module includes; one that refused a step late would let a run
# display a state outside the declared domain, which is the defect itself.


def test_the_supported_run_length_is_twenty_four_hours() -> None:
    """The declared number, pinned so a silent edit fails rather than ships.

    `docs/MODEL.md` § "Supported run length" argues this value from what the
    model omits, and `core/supported_ranges.py` carries the argument and its
    source. Moving it is a safety-critical change; moving it by accident is
    what this catches.

    It is the one test meant to fail when the number moves. The tests that
    check text or counts derived from the limit read
    `MAXIMUM_ELAPSED_SIMULATION_TIME_S` rather than restating it (`PL-T5J5`),
    so a deliberate move edits the constant, this test and that section of
    `docs/MODEL.md`.
    """

    assert MAXIMUM_ELAPSED_SIMULATION_TIME_S == 86_400.0
    assert MAXIMUM_ELAPSED_SIMULATION_TIME_S / 3600 == 24.0


@pytest.mark.parametrize(
    "simulation_step_s",
    [0.01, 0.05, 0.1, 0.2, 0.25, 0.5, 1.0, 768 / 1_000_000 * 100, 0.02304, 1e-12, 1e-300, 5e-304],
)
def test_the_last_supported_step_lands_inside_the_declared_span(simulation_step_s: float) -> None:
    """The step count is whole, and the run it allows stays inside the span.

    Checked across a spread of steps rather than only the shipped 0.1 s,
    because the count is derived from the step: a step that
    does not divide the span evenly must round *down*, leaving the last
    completed step at or below the boundary and never past it, and the next
    step past it.

    The last five are the regression cases (`PL-8H2R`). At
    `768 / 1_000_000 * 100` s, which is 0.07680000000000001, the floored
    quotient was one step too many and stopped at 86400.00000000001 s; at
    0.02304 s it was one short of the step that lands on 86400.0 s. At 1e-12
    s it was eight short and at 1e-300 s further still, where many counts
    round to one simulated time and only a search on that time finds the
    last. At 5e-304 s the count is near the largest a float holds, so a
    search bracket built by doubling the guess would itself overflow there.

    No run can take the last three since `PL-YZ17` put them below
    `MINIMUM_SIMULATION_STEP_S`, as none can take the four above 0.1 s. They
    stay because `maximum_step_count` is arithmetic on the step it is handed,
    and what they caught was in that arithmetic.
    """

    count = maximum_step_count(simulation_step_s)

    assert isinstance(count, int)
    assert count * simulation_step_s <= MAXIMUM_ELAPSED_SIMULATION_TIME_S
    assert (count + 1) * simulation_step_s > MAXIMUM_ELAPSED_SIMULATION_TIME_S


def test_every_step_in_a_family_that_rounds_both_ways_stops_inside_the_span() -> None:
    """Swept over a family of computed steps, not only the two found by hand.

    The steps `0.1 / n` held 54 counts one step too many and 104 one too few
    for n up to 2 000 before `PL-8H2R` (measured 2026-10-03), so this sweep
    fails in both directions on a count read off the quotient alone. Each
    step is checked on the two products that define the count, which is
    what a run's `elapsed_s` is, rather than on the quotient.
    """

    wrong = [
        n
        for n in range(1, 2_001)
        if not (
            maximum_step_count(0.1 / n) * (0.1 / n)
            <= MAXIMUM_ELAPSED_SIMULATION_TIME_S
            < (maximum_step_count(0.1 / n) + 1) * (0.1 / n)
        )
    ]

    assert wrong == []


def test_the_step_that_lands_on_the_limit_is_counted_at_a_step_the_quotient_undercounts() -> None:
    """0.02304 s divides 24 hours exactly in floating point, so the run reaches it.

    3 750 000 steps of 0.02304 s land on exactly 86400.0 s, and the quotient
    rounds down to 3 749 999, which stopped the run 0.02304 s short of the
    limit a learner would read (`PL-8H2R`).
    """

    assert maximum_step_count(0.02304) == 3_750_000
    assert 3_750_000 * 0.02304 == MAXIMUM_ELAPSED_SIMULATION_TIME_S


def test_a_step_whose_quotient_overcounts_stops_one_step_earlier() -> None:
    """The count whose last step lands a float past the limit is not allowed.

    1 125 000 steps of `768 / 1_000_000 * 100` s land at 86400.00000000001 s,
    which the case-instant guard refuses; the count stops at 1 124 999,
    the last whose simulated time is inside the span (`PL-8H2R`).
    """

    simulation_step_s = 768 / 1_000_000 * 100

    assert 1_125_000 * simulation_step_s > MAXIMUM_ELAPSED_SIMULATION_TIME_S
    assert maximum_step_count(simulation_step_s) == 1_124_999


def test_the_shipped_step_reaches_the_boundary_exactly() -> None:
    """At 0.1 s the span is a whole number of steps, and the run lands on it.

    Not implied by the test above, which only requires the last step to be
    inside the span. Here it is *on* it: the last step a run may take at
    0.1 s lands exactly on the limit, so a learner watching a run to its
    limit reads the limit itself rather than a value a tenth of a second
    short of it. A count one step either side lands a tenth away, so this
    pins the count as well.

    Not a property of every limit. Every whole number of hours from 1 to 720
    lands exactly in floating point (measured 2026-10-03, `PL-T5J5`); a limit
    that did not would fail here, because a learner would then read a value
    a tenth of a second short of it.
    """

    assert maximum_step_count(0.1) * 0.1 == MAXIMUM_ELAPSED_SIMULATION_TIME_S


def test_a_run_may_complete_the_step_that_reaches_the_boundary() -> None:
    """The interval is closed, like the three flow ranges above it."""

    require_supported_run_length(maximum_step_count(0.1) - 1, 0.1)


def test_the_step_that_would_cross_the_boundary_is_refused() -> None:
    """Standing exactly on the limit, the next step is the one refused."""

    with pytest.raises(SimulationDomainLimitError):
        require_supported_run_length(maximum_step_count(0.1), 0.1)


def test_a_run_already_past_the_boundary_is_refused_too() -> None:
    """A count beyond the limit refuses as well, rather than only equality.

    `>=` rather than `==`, so a count past the boundary cannot step on
    because it never met it exactly. A `SimulationState` can no longer be
    built standing there - `require_supported_step_count` refuses it first
    (`PL-BMY5`) - so on that path this is the second guard, not the only one.
    """

    with pytest.raises(SimulationDomainLimitError):
        require_supported_run_length(maximum_step_count(0.1) + 5_000, 0.1)


def test_the_run_length_refusal_says_what_was_reached_and_why() -> None:
    """A boundary with no reason reads as an arbitrary restriction.

    The message carries the time reached, the limit, and where the limit is
    argued, for the reason the flow refusals carry theirs: a reader who
    cannot trace a refusal to the domain it defends cannot tell a modelling
    limit from a bug.
    """

    with pytest.raises(SimulationDomainLimitError) as raised:
        require_supported_run_length(maximum_step_count(0.1), 0.1)

    message = str(raised.value)

    assert f"{MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s" in message
    assert f"({MAXIMUM_ELAPSED_SIMULATION_TIME_S / 3600:g} h)" in message
    assert "metabolism" in message
    assert "Supported run length" in message


def test_the_run_length_refusal_is_not_a_configuration_error() -> None:
    """Nothing handed in was wrong, so "correct it and carry on" is not offered.

    The type is what the interface reads to decide whether to tell a reader
    the simulator broke, so it is part of the displayed output rather than an
    implementation detail (`docs/MODEL.md`, "Supported run length").
    """

    with pytest.raises(SimulationDomainLimitError) as raised:
        require_supported_run_length(maximum_step_count(0.1), 0.1)

    assert not isinstance(raised.value, SimulationConfigurationError)
    assert isinstance(raised.value, SimulationExecutionError)


# --- A point on the span handed in rather than reached (PL-BMY5, PL-73ZN) ---
#
# A branch is built where its parent stood: a `SimulationState` at the parent's
# step count and a `RunDefinition` opening at one of its keyframes. Those are
# values a caller passes, so they are refused as configuration errors, and the
# step-count guard has to agree with the step's guard about where the span
# ends - or a branch taken where its parent stopped would be refused, or one
# no run could reach would be accepted.


@pytest.mark.parametrize(
    "simulation_step_s", [0.1, 0.07, 0.03, 0.025, 0.01, 768 / 1_000_000 * 100, 0.02304]
)
def test_a_run_may_be_built_where_stepping_stops_it_and_no_further(
    simulation_step_s: float,
) -> None:
    """The count a run stops on is legal to stand on and illegal to step from.

    Both guards read `maximum_step_count`, so they agree at every step,
    including the last two, at which the quotient alone put that count a step
    either side of the span (`PL-8H2R`). Where the count falls is the next
    test's question; this one asks only that the two count guards agree.
    """

    limit = maximum_step_count(simulation_step_s)

    require_supported_run_length(limit - 1, simulation_step_s)
    require_supported_step_count(limit, simulation_step_s)

    with pytest.raises(SimulationDomainLimitError):
        require_supported_run_length(limit, simulation_step_s)

    with pytest.raises(SimulationConfigurationError, match="supported run length"):
        require_supported_step_count(limit + 1, simulation_step_s)


def _accepted(guard: Callable[[], None]) -> bool:
    try:
        guard()
    except SimulationConfigurationError:
        return False

    return True


@pytest.mark.parametrize("steps_past_the_limit", [-1, 0, 1])
@pytest.mark.parametrize(
    "simulation_step_s", [0.1, 0.07, 0.03, 0.025, 0.01, 768 / 1_000_000 * 100, 0.02304]
)
def test_the_step_count_and_the_case_instant_bound_the_same_span(
    simulation_step_s: float, steps_past_the_limit: int
) -> None:
    """A count is accepted exactly where the instant it stands at is (`PL-8H2R`).

    A branch at a bookmark is built from its parent's step count and a branch
    at a control event from its parent's instant, so the two guards have to
    draw the span's end in the same place or the same fork is built one way
    and refused the other. At `768 / 1_000_000 * 100` s the count guard
    accepted a run standing at 86400.00000000001 s, which the instant guard
    refuses; at 0.02304 s it refused a count standing on 86400.0 s, which the
    instant guard accepts.
    """

    step_count = maximum_step_count(simulation_step_s) + steps_past_the_limit

    by_count = _accepted(lambda: require_supported_step_count(step_count, simulation_step_s))
    by_instant = _accepted(lambda: require_supported_case_instant(step_count * simulation_step_s))

    assert by_count == by_instant
    assert by_count == (steps_past_the_limit <= 0)


def test_the_step_count_refusal_names_the_count_the_step_and_the_limit() -> None:
    """Counts rather than a time, because the counts are exact.

    One step past the limit at a step that does not divide it would print as
    a time indistinguishable from the limit at the precision a message
    rounds to; the count beside the largest one allowed cannot be misread.
    The limit is read from its constant, which
    `test_the_supported_run_length_is_twenty_four_hours` pins.
    """

    limit = maximum_step_count(0.1)

    with pytest.raises(SimulationConfigurationError) as raised:
        require_supported_step_count(limit + 1, 0.1)

    message = str(raised.value)

    assert f"{limit + 1} steps of 0.1 s" in message
    assert f"at most {limit}" in message
    assert f"{MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s" in message
    assert f"({MAXIMUM_ELAPSED_SIMULATION_TIME_S / 3600:g} h)" in message
    assert "Supported run length" in message


def test_the_step_count_refusal_prints_the_step_it_was_given_in_full() -> None:
    """A computed step is named exactly, not rounded to one that reads as another.

    `768 / 1_000_000 * 100` is 0.07680000000000001; rounded to six figures it
    would read as 0.0768, a step the run was not taken at.
    """

    simulation_step_s = 768 / 1_000_000 * 100
    past = maximum_step_count(simulation_step_s) + 1

    with pytest.raises(SimulationConfigurationError) as raised:
        require_supported_step_count(past, simulation_step_s)

    assert f"{past} steps of 0.07680000000000001 s" in str(raised.value)


def test_a_step_count_too_long_to_print_is_refused() -> None:
    """Refused with the simulator's own error, named by how long it is (`PL-5F76`).

    CPython will not print an integer past `sys.get_int_max_str_digits`
    digits, so a refusal that printed the count raised `ValueError` while it
    was being written, and the run-length refusal, which multiplies it by the
    step, raised `OverflowError`. Either escaped the simulator's exceptions
    where every guard here promises one of its own.
    """

    too_long = 10**5000
    named = f"<more than {sys.get_int_max_str_digits():,} digits>"

    with pytest.raises(SimulationConfigurationError) as past_the_span:
        SimulationState(step_count=StepCount(too_long), simulation_step_s=SimulationStep(0.1))

    with pytest.raises(SimulationConfigurationError) as negative:
        StepCount(-too_long)

    with pytest.raises(SimulationDomainLimitError) as stepped_from:
        require_supported_run_length(StepCount(too_long), SimulationStep(0.1))

    with pytest.raises(SimulationConfigurationError) as without_a_step:
        SimulationState(step_count=StepCount(too_long))

    assert f"a run of {named} steps of 0.1 s" in str(past_the_span.value)
    assert f"not -{named}" in str(negative.value)
    assert f"reached {named} steps of 0.1 s" in str(stepped_from.value)
    assert f"step_count is {named} but no simulation_step_s" in str(without_a_step.value)


def test_a_count_too_long_to_print_is_named_when_it_was_not_built_as_one() -> None:
    """The type refusals name a bare count the way the range refusals do (`PL-CN5S`).

    Each prints what it was handed, so without `describe_count` a bare count
    past `sys.get_int_max_str_digits` digits would raise `ValueError` while
    the `TypeError` was being written, which is the escape `PL-5F76` closed.
    """

    too_long = 10**5000
    named = f"<more than {sys.get_int_max_str_digits():,} digits>"

    with pytest.raises(TypeError) as as_a_count:
        require_step_count(too_long)

    with pytest.raises(TypeError) as as_an_instant:
        require_case_instant("instant_s", too_long)

    assert f"step_count of {named} was not built as StepCount, it is int" in str(as_a_count.value)
    assert f"instant_s of {named} was not built as CaseInstant, it is int" in str(
        as_an_instant.value
    )


@pytest.mark.parametrize("instant_s", [0.0, 3_600.0, MAXIMUM_ELAPSED_SIMULATION_TIME_S])
def test_a_case_instant_is_supported_over_the_closed_span(instant_s: float) -> None:
    """Both ends included, like every interval here: a run may stand on the far end."""

    require_supported_case_instant(instant_s)


@pytest.mark.parametrize(
    "instant_s",
    [
        nextafter(MAXIMUM_ELAPSED_SIMULATION_TIME_S, inf),
        MAXIMUM_ELAPSED_SIMULATION_TIME_S + 3_600.0,
        nextafter(0.0, -inf),
        -1.0,
        nan,
        inf,
        -inf,
    ],
)
def test_a_case_instant_outside_the_span_is_refused(instant_s: float) -> None:
    """Refused on either side, and when it is not a finite number at all.

    `nan` fails every comparison, so a guard written only as a test against
    the maximum would let it through; one expression refuses every case with
    one message, as `_require_supported` does for the flows.
    """

    with pytest.raises(SimulationConfigurationError, match="supported run length"):
        require_supported_case_instant(instant_s)


def test_the_case_instant_refusal_names_the_instant_and_the_span() -> None:
    """The value is printed exactly, not rounded to look like the limit."""

    past = nextafter(MAXIMUM_ELAPSED_SIMULATION_TIME_S, inf)

    with pytest.raises(SimulationConfigurationError) as raised:
        require_supported_case_instant(past)

    message = str(raised.value)

    assert f"{past} s" in message
    assert f"{MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s is" not in message
    assert f"0 to {MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s" in message
    assert f"({MAXIMUM_ELAPSED_SIMULATION_TIME_S / 3600:g} h)" in message
    assert "Supported run length" in message


# --- The case instant and the step count are types (PL-CN5S) ----------------
#
# As each flow is above: the instant is checked against the span once, where it
# is built as a `CaseInstant`, and the count for what a count can be checked for
# alone - whole and nonnegative - once, where it is built as a `StepCount`. How
# many steps fit depends on the step, so that half stays with the record
# holding the pair, `SimulationState`. Each type holds what it was built from,
# refuses in its check's own words, and comes back from a copy as itself; the
# test modules of the records that store them hold each one to refusing a
# value that was never built as the type.


@pytest.mark.parametrize(
    "instant_s",
    [
        0.0,
        5e-324,
        3_600.0,
        86_400.0 / 3.0,
        nextafter(MAXIMUM_ELAPSED_SIMULATION_TIME_S, -inf),
        MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    ],
)
def test_a_case_instant_is_the_instant_it_was_built_from_exactly(instant_s: float) -> None:
    """Bit for bit, at both ends of the span and between, as each flow is."""

    built = CaseInstant(instant_s)

    assert type(built) is CaseInstant
    assert isinstance(built, float)
    assert built.hex() == float(instant_s).hex()


def test_a_case_instant_refuses_what_its_guard_refuses_in_the_guards_words() -> None:
    """One check, so the type can neither admit what the guard refuses nor word it differently."""

    for instant_s in (
        nextafter(MAXIMUM_ELAPSED_SIMULATION_TIME_S, inf),
        MAXIMUM_ELAPSED_SIMULATION_TIME_S + 3_600.0,
        nextafter(0.0, -inf),
        -1.0,
        nan,
        inf,
        -inf,
    ):
        with pytest.raises(SimulationConfigurationError) as by_the_guard:
            require_supported_case_instant(instant_s)

        with pytest.raises(SimulationConfigurationError) as by_the_type:
            CaseInstant(instant_s)

        assert str(by_the_type.value) == str(by_the_guard.value)


def _id(value: object) -> str:
    """A parameter's test id, naming a count too long to print by how long it is."""

    return describe_count(value) if isinstance(value, int) else repr(value)


@pytest.mark.parametrize("step_count", [0, 1, 864_000, 2**63, 10**5000], ids=_id)
def test_a_step_count_is_any_whole_nonnegative_count_however_long(step_count: int) -> None:
    """Whole and nonnegative is all a count is checked for alone.

    A count past the span is built here, because whether it is past the span
    depends on the step it is paired with: `SimulationState` refuses the
    pair, and names a count too long to print by how long it is.
    """

    built = StepCount(step_count)

    assert type(built) is StepCount
    assert isinstance(built, int)
    assert built == step_count


@pytest.mark.parametrize(
    "step_count", [-1, -(10**5000), 2.5, 2.0, nan, inf, True, False, "3", None], ids=_id
)
def test_a_step_count_refuses_what_is_not_a_whole_nonnegative_count(step_count: object) -> None:
    """In the words `SimulationState` used for it before the count was a type.

    `2.0` is whole and is still refused, as it was: a count is an `int`, so a
    `float` handed in is a sign that something computed it as a time. A
    `bool` is an `int` to Python and is refused here, which `SimulationState`
    did not do: `True` is not a count of steps.
    """

    with pytest.raises(SimulationConfigurationError, match="whole, nonnegative number of steps"):
        StepCount(step_count)  # type: ignore[arg-type]


def test_arithmetic_on_an_instant_or_a_count_is_a_plain_number() -> None:
    """What is derived from one is not checked, and must not read as checked.

    The instant one step past the end of the span is past it, and so is the
    count one step past the last a run may take at the coarsest step; were
    either sum still the type, it would carry a promise of a check that never
    ran. `SimulationState` builds the type again where it stores the next
    count and where it reports the instant it stands at.
    """

    at_the_end = CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S)
    at_the_limit = StepCount(maximum_step_count(SimulationStep(0.1)))

    assert type(at_the_end + 0.1) is float
    assert type(at_the_end - at_the_end) is float
    assert type(-at_the_end) is float
    assert type(at_the_limit + 1) is int
    assert type(at_the_limit * 0.1) is float
    assert type(-at_the_limit) is int


@pytest.mark.parametrize("built", [CaseInstant(600.0), StepCount(6_000)], ids=repr)
def test_an_instant_and_a_count_survive_copy_and_pickle_as_their_types(built: object) -> None:
    """Rebuilt through the type's own constructor, so the check runs again and the type is kept."""

    for copied in (copy.copy(built), copy.deepcopy(built), pickle.loads(pickle.dumps(built))):
        assert type(copied) is type(built)
        assert copied == built


def test_a_value_not_built_as_the_type_is_refused_whatever_it_holds() -> None:
    """The runtime half of each type refuses the missing check, not the number.

    An equal plain number, a `bool` and `None` are each refused by name, and
    the refusal says what to build without repeating the value as the thing
    to build it from: `CaseInstant(True)` would be built, as 1 s, and
    `StepCount(None)` would not.
    """

    for unbuilt in (600.0, 600, True, None):
        with pytest.raises(TypeError, match="was not built as CaseInstant") as raised:
            require_case_instant("instant_s", unbuilt)

        assert f"it is {type(unbuilt).__name__}" in str(raised.value)
        assert "build it as CaseInstant(...)" in str(raised.value)
        assert "Supported run length" in str(raised.value)

    for unbuilt in (6_000, 6_000.0, True, None):
        with pytest.raises(TypeError, match="was not built as StepCount") as raised:
            require_step_count(unbuilt)

        assert f"it is {type(unbuilt).__name__}" in str(raised.value)
        assert "build it as StepCount(...)" in str(raised.value)

    require_case_instant("instant_s", CaseInstant(600.0))
    require_step_count(StepCount(6_000))


@pytest.mark.parametrize(
    "other",
    [
        StepCount(600),
        SimulationStep(0.1),
        FreshGasFlow(4.0),
        AlveolarVentilation(4.0),
        CardiacOutput(5.0),
    ],
    ids=lambda other: type(other).__name__,
)
def test_another_quantity_handed_in_as_an_instant_is_refused_as_a_swapped_argument(
    other: object,
) -> None:
    """Named as the quantity it was built as, and not told to rebuild as an instant.

    A count of 600 steps, or the 0.1 s step, arriving where an instant belongs
    is a swapped argument. A refusal that prescribed `CaseInstant(600)` would
    have the caller build an instant of 600 s from it, which passes every
    check and is the wrong quantity, so the message prescribes nothing.
    """

    with pytest.raises(TypeError) as raised:
        require_case_instant("instant_s", other)

    message = str(raised.value)

    assert f"was built as {type(other).__name__}, which is not CaseInstant" in message
    assert "it is another quantity" in message
    assert "CaseInstant(" not in message


@pytest.mark.parametrize(
    "other",
    [
        CaseInstant(600.0),
        SimulationStep(0.1),
        FreshGasFlow(4.0),
        AlveolarVentilation(4.0),
        CardiacOutput(5.0),
    ],
    ids=lambda other: type(other).__name__,
)
def test_another_quantity_handed_in_as_a_count_is_refused_as_a_swapped_argument(
    other: object,
) -> None:
    """Named as the quantity it was built as, and not told to rebuild as a count."""

    with pytest.raises(TypeError) as raised:
        require_step_count(other)

    message = str(raised.value)

    assert f"was built as {type(other).__name__}, which is not StepCount" in message
    assert "it is another quantity" in message
    assert "StepCount(" not in message


# --- The model envelope against the machine's range (PL-8PS6) ---------------

# The two claims coincided in one pair of constants until PL-8PS6. The module
# above declares the *model's* envelope; a machine profile declares what that
# machine can physically set, and the effective limit on the control is the
# intersection. What the test below pins is that neither can be mistaken for
# the other: a machine range narrower than the envelope refuses in the
# machine's name, and a flow outside the envelope refuses in the model's name
# even on a machine that could deliver it.


def test_machine_deliverable_flow_range_is_separate_from_model_envelope() -> None:
    """Each side refuses in its own name, so a reader can tell which bound bit.

    The safety property is the second assertion rather than the first. A
    machine whose flowmeter runs past the envelope must not widen the domain
    the compartment model is claimed over - so the flow it *can* deliver is
    still refused, and the refusal says the model is what refused it.
    """

    machine_range = DeliverableFreshGasFlowRange(
        minimum_l_min=0.5, maximum_l_min=MAXIMUM_FRESH_GAS_FLOW_L_MIN + 5.0
    )
    circuit = BreathingCircuit(deliverable_fresh_gas_flow_range=machine_range)

    with pytest.raises(SimulationConfigurationError) as below_the_machine:
        circuit.set_fresh_gas_flow(FreshGasFlow(0.2))

    with pytest.raises(SimulationConfigurationError) as above_the_model:
        circuit.set_fresh_gas_flow(FreshGasFlow(MAXIMUM_FRESH_GAS_FLOW_L_MIN + 1.0))

    assert "machine" in str(below_the_machine.value)
    assert "0.5 to 15.0 L/min" in str(below_the_machine.value)

    assert "compartment model is claimed to represent a patient over" in str(above_the_model.value)
    assert f"{MINIMUM_FRESH_GAS_FLOW_L_MIN} to {MAXIMUM_FRESH_GAS_FLOW_L_MIN} L/min" in str(
        above_the_model.value
    )

    assert circuit.fresh_gas_flow_l_min == 4.0
