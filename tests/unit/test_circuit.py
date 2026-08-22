from math import exp, inf

import pytest

from anesthesia_sim.core.circuit import BreathingCircuit


def test_one_time_constant_reaches_expected_fraction() -> None:
    circuit = BreathingCircuit(
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=6.0,
        delivered_concentration_fraction=1.0,
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
        one_step.circuit_concentration_fraction,
        rel=1e-12,
    )


@pytest.mark.parametrize(
    "circuit_volume_l",
    [0.0, -1.0, float("inf")],
)
def test_rejects_invalid_circuit_volume(
    circuit_volume_l: float,
) -> None:
    with pytest.raises(ValueError):
        BreathingCircuit(circuit_volume_l=circuit_volume_l)


@pytest.mark.parametrize(
    "fresh_gas_flow_l_min",
    [-1.0, float("nan")],
)
def test_rejects_invalid_fresh_gas_flow(
    fresh_gas_flow_l_min: float,
) -> None:
    with pytest.raises(ValueError):
        BreathingCircuit(fresh_gas_flow_l_min=fresh_gas_flow_l_min)


@pytest.mark.parametrize(
    "delivered_concentration_fraction",
    [-0.01, 1.01, float("nan")],
)
def test_rejects_invalid_delivered_concentration(
    delivered_concentration_fraction: float,
) -> None:
    with pytest.raises(ValueError):
        BreathingCircuit(delivered_concentration_fraction=(delivered_concentration_fraction))
