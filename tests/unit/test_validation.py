"""The shared numeric guards raise inside the project's hierarchy.

Covered separately from the compartments that call them because the
guard functions are the single place the type is decided: a guard that
reverted to a bare `ValueError` would leave `app/` unable to recognise a
core failure, without any individual compartment test noticing.
"""

from math import inf, nan

import pytest

from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.validation import (
    require_nonnegative_finite,
    require_positive_finite,
    require_within_vaporizer_maximum,
)


@pytest.mark.parametrize("value", [0.0, -1.0, inf, -inf, nan])
def test_require_positive_finite_rejects_within_the_hierarchy(value: float) -> None:
    with pytest.raises(SimulationConfigurationError, match="volume_l must be positive and finite"):
        require_positive_finite("volume_l", value)


@pytest.mark.parametrize("value", [-0.1, inf, -inf, nan])
def test_require_nonnegative_finite_rejects_within_the_hierarchy(value: float) -> None:
    with pytest.raises(
        SimulationConfigurationError, match="agent_amount_l must be nonnegative and finite"
    ):
        require_nonnegative_finite("agent_amount_l", value)


@pytest.mark.parametrize(
    ("guard", "value"), [(require_positive_finite, 0.5), (require_nonnegative_finite, 0.0)]
)
def test_guards_accept_their_boundary_values(guard, value: float) -> None:
    """A fraction's own edges are its constructor's since `PL-4R3W`, in `test_concentration.py`."""

    guard("value", value)


def test_require_within_vaporizer_maximum_rejects_within_the_hierarchy() -> None:
    """The one relation among the guards refuses in the circuit's sentence (`PL-BBMG`)."""

    with pytest.raises(
        SimulationConfigurationError,
        match=r"delivered_concentration_percent exceeds the vaporizer maximum "
        r"\(20% requested, 8% maximum\)",
    ):
        require_within_vaporizer_maximum(
            "delivered_concentration_percent", Percent(20.0), Percent(8.0)
        )


@pytest.mark.parametrize("dialled", [0.0, 7.999, 8.0])
def test_require_within_vaporizer_maximum_accepts_up_to_the_maximum(dialled: float) -> None:
    require_within_vaporizer_maximum(
        "delivered_concentration_percent", Percent(dialled), Percent(8.0)
    )
