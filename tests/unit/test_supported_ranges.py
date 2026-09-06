"""The declared input domain, and what happens at and outside its edges.

Regression cover for PL-0MLQ: `docs/MODEL.md` declared a closed supported
interval for each control, and only the delivered concentration's was
enforced. `AgentUptakeSystem.set_cardiac_output(1000.0)` was accepted and
simulated, and the interface's sliders were the only thing keeping a run
inside the domain the verification gates cover.

The endpoints are tested as carefully as the rejections. Every range is
closed, and both ends are load-bearing: the splitting-error bound's own
worst case is measured on a trajectory holding cardiac output at zero, and
the envelope corner every reference gate drives sits on all three maxima at
once. A guard that quietly excluded an endpoint would take a measured case
out of the reachable domain without failing anything.
"""

from collections.abc import Callable
from math import inf, nan, nextafter
from typing import NamedTuple

import pytest

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
    require_supported_alveolar_ventilation,
    require_supported_cardiac_output,
    require_supported_fresh_gas_flow,
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
