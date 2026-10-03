"""The declared input domain, and what happens at and outside its edges.

Regression cover for PL-0MLQ: `docs/MODEL.md` declared a closed supported
interval for each control, and only the delivered concentration's was
enforced. `AgentUptakeSystem.set_cardiac_output(1000.0)` was accepted and
simulated, and the interface's sliders were the only thing keeping a run
inside the domain the verification gates cover.

The endpoints are tested as carefully as the rejections. Every range is
closed, and both ends are load-bearing: one reference gate trajectory holds
cardiac output at zero for its loading phase, and the envelope corner every
reference gate drives sits on all three maxima at once. A guard that quietly
excluded an endpoint would take a measured case out of the reachable domain
without failing anything.
"""

from collections.abc import Callable
from math import inf, nan, nextafter
from typing import NamedTuple

import pytest

from anesthesia_sim.core.circuit import BreathingCircuit, DeliverableFreshGasFlowRange
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
)
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
    maximum_step_count,
    require_supported_alveolar_ventilation,
    require_supported_cardiac_output,
    require_supported_case_instant,
    require_supported_fresh_gas_flow,
    require_supported_run_length,
    require_supported_step_count,
)


class Control(NamedTuple):
    """One control's guard and the closed interval it declares."""

    name: str
    guard: Callable[[float], None]
    minimum: float
    maximum: float


CONTROLS = (
    Control(
        "fresh_gas_flow_l_min",
        require_supported_fresh_gas_flow,
        MINIMUM_FRESH_GAS_FLOW_L_MIN,
        MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    ),
    Control(
        "alveolar_ventilation_l_min",
        require_supported_alveolar_ventilation,
        MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    ),
    Control(
        "cardiac_output_l_min",
        require_supported_cardiac_output,
        MINIMUM_CARDIAC_OUTPUT_L_MIN,
        MAXIMUM_CARDIAC_OUTPUT_L_MIN,
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
    """

    assert MAXIMUM_ELAPSED_SIMULATION_TIME_S == 86_400.0
    assert MAXIMUM_ELAPSED_SIMULATION_TIME_S / 3600 == 24.0


@pytest.mark.parametrize("simulation_step_s", [0.01, 0.05, 0.1, 0.2, 0.25, 0.5, 1.0])
def test_the_last_supported_step_lands_inside_the_declared_span(simulation_step_s: float) -> None:
    """The step count is whole, and the run it allows stays inside the span.

    Checked across every step a run might be taken at rather than only the
    shipped 0.1 s, because the count is derived from the step: a step that
    does not divide the span evenly must round *down*, leaving the last
    completed step at or below the boundary and never past it.
    """

    count = maximum_step_count(simulation_step_s)

    assert isinstance(count, int)
    assert count * simulation_step_s <= MAXIMUM_ELAPSED_SIMULATION_TIME_S
    assert (count + 1) * simulation_step_s > MAXIMUM_ELAPSED_SIMULATION_TIME_S


def test_the_shipped_step_reaches_the_boundary_exactly() -> None:
    """At 0.1 s the span is a whole number of steps, and the run lands on it.

    Not implied by the test above, which only requires the last step to be
    inside the span. Here it is *on* it: 864 000 steps of 0.1 s reach exactly
    86 400.0 s, so a learner watching a run to its limit reads a round 24
    hours rather than a value a tenth of a second short of one.
    """

    assert maximum_step_count(0.1) == 864_000
    assert 864_000 * 0.1 == MAXIMUM_ELAPSED_SIMULATION_TIME_S


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

    assert "86400 s" in message
    assert "24 h" in message
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

    Both guards read `maximum_step_count`, so they agree at every step - even
    the last two, where at the 24-hour limit that count is itself off by one
    (`PL-8H2R`): `768 / 1_000_000 * 100` takes one step too many and stops at
    86400.00000000001 s, and `0.02304` stops one step short of the step that
    lands on 86400.0 s. Agreeing with the step's guard is what this guard
    promises; where that guard puts the limit is `PL-8H2R`'s to fix.
    """

    limit = maximum_step_count(simulation_step_s)

    require_supported_run_length(limit - 1, simulation_step_s)
    require_supported_step_count(limit, simulation_step_s)

    with pytest.raises(SimulationDomainLimitError):
        require_supported_run_length(limit, simulation_step_s)

    with pytest.raises(SimulationConfigurationError, match="supported run length"):
        require_supported_step_count(limit + 1, simulation_step_s)


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
        circuit.set_fresh_gas_flow(0.2)

    with pytest.raises(SimulationConfigurationError) as above_the_model:
        circuit.set_fresh_gas_flow(MAXIMUM_FRESH_GAS_FLOW_L_MIN + 1.0)

    assert "machine" in str(below_the_machine.value)
    assert "0.5 to 15.0 L/min" in str(below_the_machine.value)

    assert "compartment model is claimed to represent a patient over" in str(above_the_model.value)
    assert f"{MINIMUM_FRESH_GAS_FLOW_L_MIN} to {MAXIMUM_FRESH_GAS_FLOW_L_MIN} L/min" in str(
        above_the_model.value
    )

    assert circuit.fresh_gas_flow_l_min == 4.0
