"""Check the circuit's wash-in against a closed form written from literals.

`test_circuit_wash_in.py` holds the v0.0.2 analytic wash-in test, and
`docs/MODEL.md` § "Preserved circuit reference tests" requires it to stay
unchanged. Its expected value reads the time constant from
`BreathingCircuit.time_constant_s` and the delivered fraction from
`fraction_from_percent`, and both are shipped code. A unit error shared by
them and by `BreathingCircuit.advance_fresh_gas` would move the expected value
and the observed value together, so that test would still pass (`PL-RXW0`).

This module writes the time constant and the delivered fraction as literals,
worked out by hand from the settings below. Nothing in its expected value
comes from the code under test.
"""

from math import exp

import pytest

from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.supported_ranges import FreshGasFlow

# tau_C = V_C / V_F = 6.0 L / 6.0 L/min = 1.0 min = 60.0 s.
TIME_CONSTANT_S = 60.0

# A dial of 8% is 8/100 of an atmosphere.
DELIVERED_FRACTION = 0.08


@pytest.mark.parametrize("elapsed_s", [30.0, 60.0, 120.0, 300.0])
def test_circuit_wash_in_matches_a_closed_form_written_from_literals(elapsed_s: float) -> None:
    """From an empty circuit, F_I(t) = F_D (1 - e^(-t / tau_C)), with F_D and tau_C as literals."""

    circuit = BreathingCircuit(
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=FreshGasFlow(6.0),
        delivered_concentration_percent=Percent(8.0),
    )

    circuit.advance(elapsed_s)

    expected_fraction = DELIVERED_FRACTION * (1.0 - exp(-elapsed_s / TIME_CONSTANT_S))
    assert circuit.inspired_partial_pressure_fraction == pytest.approx(expected_fraction, rel=1e-12)
