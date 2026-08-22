from math import exp

import pytest

from anesthesia_sim.core.circuit import BreathingCircuit


@pytest.mark.parametrize(
    "elapsed_s",
    [0.0, 30.0, 60.0, 120.0, 300.0],
)
def test_circuit_matches_analytic_wash_in(elapsed_s: float) -> None:
    circuit = BreathingCircuit(
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=6.0,
        delivered_concentration_fraction=0.08,
    )

    if elapsed_s > 0.0:
        circuit.advance(elapsed_s)

    expected_concentration_fraction = 0.08 * (1.0 - exp(-elapsed_s / circuit.time_constant_s))

    assert circuit.circuit_concentration_fraction == pytest.approx(
        expected_concentration_fraction,
        rel=1e-12,
        abs=1e-15,
    )


def test_wash_in_is_monotonic_and_never_overshoots() -> None:
    circuit = BreathingCircuit(delivered_concentration_fraction=0.08)
    observed_concentrations = [circuit.circuit_concentration_fraction]

    for _ in range(1_200):
        circuit.advance(0.1)
        observed_concentrations.append(circuit.circuit_concentration_fraction)

    assert observed_concentrations == sorted(observed_concentrations)
    assert observed_concentrations[-1] < circuit.delivered_concentration_fraction
