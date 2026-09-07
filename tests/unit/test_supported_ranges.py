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
    require_supported_fresh_gas_flow,
    require_supported_run_length,
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

    `>=` rather than `==`, so a state constructed part-way through a run -
    which `SimulationState` explicitly supports - cannot step on from past
    the boundary because it never met it exactly.
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
