from math import exp, inf

import pytest

from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import MAXIMUM_FRESH_GAS_FLOW_L_MIN


def test_rejects_agent_amount_above_circuit_capacity() -> None:
    circuit = BreathingCircuit()

    with pytest.raises(
        SimulationConfigurationError, match="^agent_amount_l exceeds circuit capacity$"
    ):
        circuit.set_agent_amount(6.1)


def test_one_time_constant_reaches_expected_fraction() -> None:
    circuit = BreathingCircuit(
        circuit_volume_l=6.0, fresh_gas_flow_l_min=6.0, delivered_concentration_fraction=1.0
    )

    circuit.advance(circuit.time_constant_s)

    assert circuit.circuit_concentration_fraction == pytest.approx(1.0 - exp(-1.0))


def test_zero_fresh_gas_flow_preserves_concentration() -> None:
    circuit = BreathingCircuit(
        fresh_gas_flow_l_min=0.0,
        delivered_concentration_fraction=1.0,
        circuit_concentration_fraction=0.25,
    )

    circuit.advance(60.0)

    assert circuit.time_constant_s == inf
    assert circuit.circuit_concentration_fraction == 0.25


def test_zero_delivered_concentration_washes_out_circuit() -> None:
    circuit = BreathingCircuit(
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=6.0,
        delivered_concentration_fraction=0.0,
        circuit_concentration_fraction=1.0,
    )

    circuit.advance(circuit.time_constant_s)

    assert circuit.circuit_concentration_fraction == pytest.approx(exp(-1.0))


def test_exact_update_is_independent_of_step_size() -> None:
    one_step = BreathingCircuit()
    many_steps = BreathingCircuit()

    one_step.advance(60.0)

    for _ in range(600):
        many_steps.advance(0.1)

    assert many_steps.circuit_concentration_fraction == pytest.approx(
        one_step.circuit_concentration_fraction, rel=1e-12
    )


@pytest.mark.parametrize("circuit_volume_l", [0.0, -1.0, float("inf")])
def test_rejects_invalid_circuit_volume(circuit_volume_l: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        BreathingCircuit(circuit_volume_l=circuit_volume_l)


@pytest.mark.parametrize("fresh_gas_flow_l_min", [-1.0, float("nan")])
def test_rejects_invalid_fresh_gas_flow(fresh_gas_flow_l_min: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        BreathingCircuit(fresh_gas_flow_l_min=fresh_gas_flow_l_min)


@pytest.mark.parametrize("delivered_concentration_fraction", [-0.01, 1.01, float("nan")])
def test_rejects_invalid_delivered_concentration(delivered_concentration_fraction: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        BreathingCircuit(delivered_concentration_fraction=(delivered_concentration_fraction))


def test_rejects_delivered_concentration_above_the_vaporizer_maximum() -> None:
    """Regression (PL-015): the vaporizer limit is enforced in the core.

    Before the fix the limit lived only in the controller, as a silent
    clamp, and in the UI slider bounds.
    """

    circuit = BreathingCircuit(
        delivered_concentration_fraction=0.02, max_delivered_concentration_fraction=0.05
    )

    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        circuit.set_delivered_concentration(0.50)

    assert circuit.delivered_concentration_fraction == 0.02


def test_rejects_construction_above_the_vaporizer_maximum() -> None:
    with pytest.raises(SimulationConfigurationError, match="vaporizer maximum"):
        BreathingCircuit(
            delivered_concentration_fraction=0.08, max_delivered_concentration_fraction=0.05
        )


def test_accepts_delivered_concentration_exactly_at_the_vaporizer_maximum() -> None:
    circuit = BreathingCircuit(
        delivered_concentration_fraction=0.02, max_delivered_concentration_fraction=0.05
    )
    circuit.set_delivered_concentration(0.05)

    assert circuit.delivered_concentration_fraction == 0.05


def test_accepts_a_delivered_concentration_of_zero() -> None:
    """The vaporizer off is always a valid dial position: it is washout."""

    circuit = BreathingCircuit(
        delivered_concentration_fraction=0.02, max_delivered_concentration_fraction=0.05
    )
    circuit.set_delivered_concentration(0.0)

    assert circuit.delivered_concentration_fraction == 0.0


@pytest.mark.parametrize(
    "max_delivered_concentration_fraction", [0.0, -0.01, 1.01, float("nan"), float("inf")]
)
def test_rejects_invalid_vaporizer_maximum(max_delivered_concentration_fraction: float) -> None:
    with pytest.raises(SimulationConfigurationError):
        BreathingCircuit(
            delivered_concentration_fraction=0.0,
            max_delivered_concentration_fraction=(max_delivered_concentration_fraction),
        )


def test_accepts_fresh_gas_flow_at_both_ends_of_the_supported_range() -> None:
    """Zero is the vaporizer running into a closed system; the maximum is the
    corner of the settings envelope every reference gate measures at."""

    for fresh_gas_flow_l_min in (0.0, MAXIMUM_FRESH_GAS_FLOW_L_MIN):
        circuit = BreathingCircuit(fresh_gas_flow_l_min=fresh_gas_flow_l_min)

        assert circuit.fresh_gas_flow_l_min == fresh_gas_flow_l_min

        circuit.set_fresh_gas_flow(fresh_gas_flow_l_min)

        assert circuit.fresh_gas_flow_l_min == fresh_gas_flow_l_min


def test_rejects_fresh_gas_flow_above_the_supported_range() -> None:
    """Regression (PL-0MLQ): the range was documented but never enforced.

    A bare circuit is an exact exponential at any flow, so this guard is not
    about the circuit's own arithmetic — it is the model's declared input
    domain, and the circuit is where every path that can change the flow
    passes through, the same argument the vaporizer maximum above rests on.
    """

    circuit = BreathingCircuit(fresh_gas_flow_l_min=4.0)

    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        circuit.set_fresh_gas_flow(500.0)

    assert circuit.fresh_gas_flow_l_min == 4.0


def test_rejects_construction_with_fresh_gas_flow_above_the_supported_range() -> None:
    with pytest.raises(SimulationConfigurationError, match="supported input range"):
        BreathingCircuit(fresh_gas_flow_l_min=500.0)
