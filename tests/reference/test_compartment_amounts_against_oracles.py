"""Check each compartment's agent amount on the snapshot against oracles independent of `core/`.

`SimulationSnapshot.compartment_agent_amounts` passes on the amount that each
compartment in `core/` holds (`PL-KFTM`). The planned compartment schematic
will label its containers with these amounts and draw its share bar from them.
So a wrong pairing, a wrong capacity or a wrong unit here would put a plausible
but wrong number on a container. Two oracles check the amounts, and neither
reads the code under test.

The first is a closed form. With alveolar ventilation at zero, no agent moves
from the circuit to the alveoli, so the circuit fills from empty as
$`M_C(t) = V_C F_D (1 - e^{-t \\dot V_F / V_C})`$ and every other compartment
stays empty (`docs/MODEL.md` § "Governing equations").

The second is the coupled six-state solution that
`tests/reference/test_coupled_dynamics.py` integrates with its own fourth-order
Runge-Kutta method. Its fractions at 60 s and 600 s are transcribed below from
that module's `PINNED_REFERENCE_STATES`, which pins them to the oracle and not
to the shipped solver. Each expected amount is that fraction times the
compartment's capacity, written out from `docs/MODEL.md` § "Agent amount" with
the parameter loaders' values. The test modules do not import one another, so
the twelve states are restated here rather than imported.

**What the comparison can detect.** The tolerance is one part in a billion of
the amount. The shipped step matches the oracle's fractions to within 1e-12
(`HELD_RUN_ROUNDING_BOUND` in that module), and the transcribed fractions carry
thirteen significant figures. So the test fails on any error as large as a
whole capacity term: two compartments' amounts swapped, a tissue's capacity
taken with the blood:gas coefficient instead of its own tissue:gas coefficient,
or an amount reported in millilitres where litres are meant. An error smaller
than one part in a billion of an amount passes, but no displayed precision is
fine enough to show such an error (`docs/INTERFACE.md` § "Displayed precision").
"""

from math import exp

import pytest

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow

# The shipped step, restated rather than imported for the reason
# `test_coupled_dynamics.py` gives for its own `SHIPPED_STEP_S`.
SHIPPED_STEP_S = 0.1

# `PINNED_REFERENCE_STATES` was computed at this operating point: a 5% dial,
# 4.0 L/min of fresh gas into a 6.0 L circuit, and the reference adult's default
# ventilation and cardiac output.
DELIVERED_PERCENT = 5.0
FRESH_GAS_FLOW_L_MIN = 4.0
CIRCUIT_VOLUME_L = 6.0

# The order of each tuple below, which is the oracle's state order.
STATE_ORDER = (
    RecordedQuantity.CIRCUIT,
    RecordedQuantity.ALVEOLAR,
    RecordedQuantity.MIXED_VENOUS,
    RecordedQuantity.VESSEL_RICH,
    RecordedQuantity.MUSCLE,
    RecordedQuantity.FAT,
)

# Partial-pressure fractions transcribed from `PINNED_REFERENCE_STATES` in
# `tests/reference/test_coupled_dynamics.py`, as re-derived from the RK4 oracle
# on 2026-09-07 (`PL-8ZJQ`).
ORACLE_FRACTIONS: dict[tuple[str, float], tuple[float, ...]] = {
    ("desflurane", 60.0): (
        2.028404136125e-02,
        9.281420915853e-03,
        7.876663535405e-04,
        1.712991053952e-03,
        4.697597715896e-05,
        2.667678019825e-06,
    ),
    ("desflurane", 600.0): (
        4.315734014009e-02,
        3.701331546615e-02,
        2.624076126831e-02,
        3.419351995732e-02,
        2.964053373816e-03,
        1.752741904675e-04,
    ),
    ("isoflurane", 60.0): (
        1.979040100781e-02,
        6.424722270858e-03,
        4.911457693498e-04,
        1.043825468899e-03,
        2.349820689350e-05,
        1.148589299382e-06,
    ),
    ("isoflurane", 600.0): (
        3.617208687621e-02,
        2.299235500822e-02,
        1.518165093660e-02,
        1.999176551660e-02,
        1.209506966652e-03,
        6.075357967569e-05,
    ),
    ("sevoflurane", 60.0): (
        2.012553561074e-02,
        8.326553885664e-03,
        5.694784215021e-04,
        1.234707386216e-03,
        2.706958058365e-05,
        1.452557155924e-06,
    ),
    ("sevoflurane", 600.0): (
        4.021622895670e-02,
        3.116010711424e-02,
        2.067189318209e-02,
        2.720937451485e-02,
        1.572056775422e-03,
        8.654143975784e-05,
    ),
}


def _capacities_l(agent_id: str) -> tuple[float, ...]:
    """Return each compartment's capacity, the amount per unit partial-pressure fraction.

    Each capacity is written out from `docs/MODEL.md` § "Agent amount", in the
    oracle's state order: $`V_C`$, $`V_A`$, $`V_v \\lambda_{b:g}`$, and
    $`V_i \\lambda_{i:b} \\lambda_{b:g}`$ for each tissue group. Only the
    parameter loaders are read.
    """

    agent = load_agent_parameters(agent_id)
    patient = load_reference_adult_parameters()
    blood_gas = agent.blood_gas_partition_coefficient

    def tissue(volume_l: float, tissue_gas: float) -> float:
        return volume_l * (tissue_gas / blood_gas) * blood_gas

    return (
        CIRCUIT_VOLUME_L,
        patient.alveolar_gas_volume_l,
        patient.venous_pool_volume_l * blood_gas,
        tissue(patient.vessel_rich_volume_l, agent.vessel_rich_tissue_gas_partition_coefficient),
        tissue(patient.muscle_volume_l, agent.muscle_tissue_gas_partition_coefficient),
        tissue(patient.fat_volume_l, agent.fat_tissue_gas_partition_coefficient),
    )


def _run_for(controller: SimulationController, duration_s: float) -> None:
    """Start `controller` and advance it by `duration_s` in shipped steps."""

    controller.start()

    for _ in range(round(duration_s / SHIPPED_STEP_S)):
        controller.advance(SimulationStep(SHIPPED_STEP_S))


@pytest.mark.parametrize(("agent_id", "duration_s"), sorted(ORACLE_FRACTIONS))
def test_each_amount_matches_the_coupled_oracle(agent_id: str, duration_s: float) -> None:
    """Each compartment's amount equals its oracle fraction times its capacity."""

    patient = load_reference_adult_parameters()
    controller = SimulationController(
        agent_id=agent_id,
        circuit_volume_l=CompartmentVolume(CIRCUIT_VOLUME_L),
        fresh_gas_flow_l_min=FreshGasFlow(FRESH_GAS_FLOW_L_MIN),
        delivered_concentration_percent=Percent(DELIVERED_PERCENT),
        alveolar_ventilation_l_min=AlveolarVentilation(patient.default_alveolar_ventilation_l_min),
        cardiac_output_l_min=CardiacOutput(patient.default_cardiac_output_l_min),
    )
    _run_for(controller, duration_s)
    amounts = controller.snapshot().compartment_agent_amounts

    for compartment, fraction, capacity_l in zip(
        STATE_ORDER, ORACLE_FRACTIONS[(agent_id, duration_s)], _capacities_l(agent_id), strict=True
    ):
        assert amounts.of(compartment) == pytest.approx(fraction * capacity_l, rel=1e-9), (
            f"{agent_id} at {duration_s:.0f} s: the {compartment.value} amount "
            f"{amounts.of(compartment)!r} L differs from the oracle's "
            f"{fraction * capacity_l!r} L"
        )


# With no ventilation, only the fresh gas exchanges with the circuit. With
# 6.0 L/min of fresh gas into a 6.0 L circuit, the circuit's time constant tau_C
# is 60 s. A 2% dial is 0.02 of an atmosphere, so the circuit approaches
# 6.0 L x 0.02 = 0.12 L of vapour.
CLOSED_FORM_FRESH_GAS_FLOW_L_MIN = 6.0
CLOSED_FORM_TIME_CONSTANT_S = 60.0
CLOSED_FORM_FULL_CIRCUIT_L = 0.12


@pytest.mark.parametrize("elapsed_s", [30.0, 60.0, 300.0])
def test_without_ventilation_only_the_circuit_holds_agent_and_it_fills_in_closed_form(
    elapsed_s: float,
) -> None:
    """The circuit fills as $`M_C = V_C F_D (1 - e^{-t/\\tau_C})`$, and the patient stays empty.

    With no ventilation, no agent moves from the circuit to the alveoli, so
    no agent reaches the blood or the tissues either.
    """

    controller = SimulationController(
        agent_id="sevoflurane",
        circuit_volume_l=CompartmentVolume(CIRCUIT_VOLUME_L),
        fresh_gas_flow_l_min=FreshGasFlow(CLOSED_FORM_FRESH_GAS_FLOW_L_MIN),
        delivered_concentration_percent=Percent(2.0),
        alveolar_ventilation_l_min=AlveolarVentilation(0.0),
    )
    _run_for(controller, elapsed_s)
    amounts = controller.snapshot().compartment_agent_amounts

    assert amounts.of(RecordedQuantity.CIRCUIT) == pytest.approx(
        CLOSED_FORM_FULL_CIRCUIT_L * (1.0 - exp(-elapsed_s / CLOSED_FORM_TIME_CONSTANT_S)), rel=1e-9
    )

    for compartment in STATE_ORDER[1:]:
        assert amounts.of(compartment) == 0.0, (
            f"with no ventilation the {compartment.value} compartment holds "
            f"{amounts.of(compartment)!r} L, where no agent can reach it"
        )
