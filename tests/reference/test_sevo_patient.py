from math import isfinite

import pytest

from anesthesia_sim.app import wash_in
from anesthesia_sim.app.wash_in import WashInDomain, read_wash_in
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.parameters import (
    AgentParameters,
    load_reference_adult_parameters,
    load_reference_circle_system_parameters,
    parse_agent_parameters,
)
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

EQUILIBRIUM_FRACTION_TOLERANCE = 1e-12

# The conservation bound that the reference runs must meet. It is restated
# here rather than imported, for the reason that
# `tests/unit/test_agent_simulation_validation.py` gives: a bound that followed
# the constant it tests would move wherever that constant moved.
# `docs/VERIFICATION.md` § "Mass-balance identity" is the documented basis and gives
# the derivation.
#
# The bound is relative, not absolute. The mass-balance residual is rounding
# accumulated once per step, so it scales with how much agent a run has
# handled. Halving the dial halves `absolute_error_l` exactly and leaves
# `relative_error` unchanged to four significant figures. So asserting the
# absolute figure measured this test's own setup rather than conservation. An
# absolute bound would also be false after about an hour of simulated time. At
# these settings the absolute error first exceeds 1e-12 L at t = 3452 s, and
# these runs stop at 1200 s (`PL-4GN8`, measured 2026-09-06 on the exact step,
# which was then 0.1 s long).
MASS_BALANCE_RELATIVE_GATE = 1e-10

# The washout gate's run. It matches the wash-in and washout legs of
# `test_long_wash_in_and_washout_validate_agent_simulation`, so that the two
# gates describe the same trajectory: 600 s at the default dial to load the
# compartments, then 600 s at zero. Both legs run at `SIMULATION_STEP_S`, the
# one-second step that every run takes.
WASHOUT_LOAD_DURATION_S = 600
WASHOUT_DURATION_S = 600


def _run_for(system: AgentUptakeSystem, duration_s: int) -> None:
    """Advance a system by `duration_s`, a whole number of seconds, one step at a time."""

    for _ in range(duration_s // SIMULATION_STEP_S):
        system.advance()


def _synthetic_agent(blood_gas_partition_coefficient: float) -> AgentParameters:
    """Build an agent identical to sevoflurane except for solubility.

    The tissue:gas partition coefficients are held fixed. So only the
    blood:gas coefficient differs between systems, and with it the blood
    capacity and every derived tissue:blood coefficient.
    """

    payload = {
        "schema_version": 5,
        "id": "synthetic-solubility-test-agent",
        "display_name": "Synthetic solubility test agent",
        "blood_gas_partition_coefficient": blood_gas_partition_coefficient,
        "tissue_gas_partition_coefficients": {"vessel_rich": 1.1, "muscle": 2.4, "fat": 34.0},
        "max_delivered_concentration_percent": 8.0,
        "mac_at_age_40_percent": 2.0,
        "mac_awake": {
            "fraction_of_mac": 0.34,
            "standard_deviation_fraction_of_mac": 0.05,
            "mac_reference_basis": "synthetic; no reference band is drawn in this test",
        },
        # Sevoflurane's liquid properties. This test reads neither of them.
        "molar_mass_g_mol": 200.05,
        "liquid_density": {
            "g_ml": 1.5203,
            "standard_deviation_g_ml": 0.0008,
            "measured_at_celsius": 20.0,
        },
        "sources": [
            {
                "citation": "Synthetic parameters for directional solubility testing only.",
                "url": "https://example.com/synthetic-test-agent",
                "tier": "primary",
                "adopted": True,
                "authority_for": ["blood_gas_partition_coefficient"],
                "note": "Not a real agent; isolates the effect of blood:gas solubility only.",
            }
        ],
    }
    return parse_agent_parameters(payload)


def _build_system_with_blood_gas_coefficient(
    blood_gas_partition_coefficient: float,
) -> AgentUptakeSystem:
    """Build a synthetic-agent system, differing only in blood:gas solubility.

    The circuit starts at the synthetic agent's own 1 MAC under its own
    vaporizer maximum, the same convention `AgentUptakeSystem.for_agent()`
    uses for the built-in agents. `_synthetic_agent()` holds both of those
    fixed, so the two systems compared below run at one identical dial.
    """

    agent = _synthetic_agent(blood_gas_partition_coefficient)
    patient_parameters = load_reference_adult_parameters()

    return AgentUptakeSystem(
        circuit=BreathingCircuit(
            circuit_volume_l=load_reference_circle_system_parameters().circuit_volume_l,
            delivered_concentration_percent=agent.mac_at_age_40_percent,
            max_delivered_concentration_percent=agent.max_delivered_concentration_percent,
        ),
        alveoli=AlveolarCompartment(
            gas_volume_l=patient_parameters.alveolar_gas_volume_l,
            alveolar_ventilation_l_min=AlveolarVentilation(
                patient_parameters.default_alveolar_ventilation_l_min
            ),
        ),
        patient=PatientCompartments.from_parameters(agent=agent, patient=patient_parameters),
    )


def test_no_delivered_agent_keeps_every_store_zero() -> None:
    system = AgentUptakeSystem.default()
    system.set_delivered_concentration_percent(Percent(0.0))

    _run_for(system, duration_s=300)

    validation = system.agent_simulation_validation

    assert system.total_stored_agent_l == 0.0
    assert validation.delivered_agent_l == 0.0
    assert validation.exhausted_agent_l == 0.0
    assert validation.unaccounted_agent_l == 0.0
    assert validation.passes_validation is True


def test_zero_ventilation_prevents_patient_delivery() -> None:
    system = AgentUptakeSystem.default()
    system.set_alveolar_ventilation(AlveolarVentilation(0.0))

    _run_for(system, duration_s=120)

    assert system.circuit.inspired_partial_pressure_fraction > 0.0
    assert system.alveoli.agent_amount_l == 0.0
    assert system.patient.total_agent_amount_l == 0.0
    assert system.agent_simulation_validation.passes_validation is True


def test_zero_cardiac_output_prevents_patient_uptake() -> None:
    system = AgentUptakeSystem.default()
    system.set_cardiac_output(CardiacOutput(0.0))

    _run_for(system, duration_s=120)

    assert system.alveoli.partial_pressure_fraction > 0.0
    assert system.patient.total_agent_amount_l == 0.0
    assert system.agent_simulation_validation.passes_validation is True


def test_mixed_venous_blood_lags_the_flow_weighted_tissue_return() -> None:
    """Venous blood is a pool, so it trails what drains into it.

    The test checks the coupled run rather than a patient-side step.
    `PL-74R0` deleted `PatientCompartments.advance()`, which held the tissue
    return constant across a step. So that method could only ever show this lag
    at the size of one step. Here the return rises continuously and the pool
    follows behind it. That is the property `docs/MODEL.md` § "Venous blood"
    states, and the one a reader of the mixed-venous trace is looking at.
    """

    system = AgentUptakeSystem.default()

    _run_for(system, duration_s=120)

    assert system.patient.mixed_venous_partial_pressure_fraction > 0.0
    assert (
        system.patient.mixed_venous_partial_pressure_fraction
        < system.patient.tissue_return_partial_pressure_fraction
    )


def test_higher_cardiac_output_increases_early_uptake_and_lowers_alveolar_fraction() -> None:
    """Both halves of the cardiac-output lesson, on one pair of runs.

    More perfusion carries more agent away from the lung per unit time, so
    the patient stores more of it and the alveolar fraction rises more
    slowly. The second assertion makes this a coupled-model test rather than a
    compartment test. The fall in `F_A` is feedback that the patient-side step,
    which `PL-74R0` deleted, could not produce. That step took the arterial
    fraction as an argument instead of solving for it.
    """

    lower_output = AgentUptakeSystem.default()
    higher_output = AgentUptakeSystem.default()

    lower_output.set_cardiac_output(CardiacOutput(2.5))
    higher_output.set_cardiac_output(CardiacOutput(7.5))

    _run_for(lower_output, duration_s=60)
    _run_for(higher_output, duration_s=60)

    assert higher_output.patient.total_agent_amount_l > lower_output.patient.total_agent_amount_l
    assert (
        higher_output.alveoli.partial_pressure_fraction
        < lower_output.alveoli.partial_pressure_fraction
    )
    assert higher_output.agent_simulation_validation.passes_validation is True
    assert lower_output.agent_simulation_validation.passes_validation is True


def _plotted_wash_in_ratio(system: AgentUptakeSystem) -> float:
    """Return the F_A / F_I that the wash-in curve plots for this state.

    The ratio comes from `read_wash_in`, the one function that computes the
    plotted value, so this test checks the quotient a user sees. The result
    of `read_wash_in` must lie in the wash-in domain, where agent has reached
    the circuit and F_A / F_I lies between 0 and 1. Outside that domain the
    curve plots nothing, and the lesson has nothing to compare.

    The plot also draws no ratio for a state reached at zero alveolar
    ventilation, which `read_wash_in` cannot see. So the reading is also
    checked against `read_wash_in_with_ventilation`, which applies that rule
    as well and gives the reading the plot draws (`PL-ZZLW`).
    """

    reading = read_wash_in(
        system.alveoli.partial_pressure_fraction, system.circuit.inspired_partial_pressure_fraction
    )

    assert reading.domain is WashInDomain.WASH_IN
    assert reading.plotted_ratio is not None
    # Each run here keeps one ventilation from its start, so the system's
    # ventilation is the ventilation of the step that reached this state.
    assert (
        wash_in.read_wash_in_with_ventilation(
            system.alveoli.partial_pressure_fraction,
            system.circuit.inspired_partial_pressure_fraction,
            system.alveoli.alveolar_ventilation_l_min,
        )
        == reading
    )

    return reading.plotted_ratio


def test_higher_ventilation_closes_the_alveolar_to_inspired_gap_faster() -> None:
    """Higher alveolar ventilation must bring F_A toward F_I faster.

    Required test from docs/VERIFICATION.md § "Directional ventilation test". Two
    default sevoflurane wash-ins run side by side, at 2 and 8 L/min of
    alveolar ventilation. At every whole second of the first minute, F_A / F_I
    must be higher in the 8 L/min run.

    The test compares the ratio because F_A alone measures the approach to
    F_I only when F_I is the same in both runs, and here it is not. The
    circle system rebreathes, and more ventilation carries more agent into
    the patient. So F_I rises more slowly at 8 L/min than at 2 L/min. On
    2026-11-01, F_I at 30 s measured 0.0047 at 8 L/min against 0.0053 at
    2 L/min. The final assertion keeps the older claim that F_A itself is
    higher at 30 s in the 8 L/min run, because a user reading the F_A trace
    sees that too.
    """

    lower_ventilation = AgentUptakeSystem.default()
    higher_ventilation = AgentUptakeSystem.default()

    lower_ventilation.set_alveolar_ventilation(AlveolarVentilation(2.0))
    higher_ventilation.set_alveolar_ventilation(AlveolarVentilation(8.0))

    for elapsed_s in range(1, 61):
        _run_for(lower_ventilation, duration_s=1)
        _run_for(higher_ventilation, duration_s=1)

        assert _plotted_wash_in_ratio(higher_ventilation) > _plotted_wash_in_ratio(
            lower_ventilation
        ), f"F_A/F_I at 8 L/min is not ahead of 2 L/min at {elapsed_s} s"

        if elapsed_s == 30:
            assert (
                higher_ventilation.alveoli.partial_pressure_fraction
                > lower_ventilation.alveoli.partial_pressure_fraction
            )


def test_long_wash_in_and_washout_validate_agent_simulation() -> None:
    system = AgentUptakeSystem.default()

    _run_for(system, duration_s=600)

    system.set_delivered_concentration_percent(Percent(0.0))

    _run_for(system, duration_s=600)

    validation = system.agent_simulation_validation

    assert validation.passes_validation is True
    # Assert the relative residual, not the absolute one. The absolute figure
    # scales with the dial and the run length, so asserting it measures this
    # test's setup rather than conservation (`PL-4GN8`). `mass_balance_gate`
    # gives the measurements that the bound comes from.
    assert validation.relative_error <= MASS_BALANCE_RELATIVE_GATE
    assert validation.delivered_agent_l > 0.0
    assert validation.exhausted_agent_l > 0.0


def test_washout_never_increases_total_system_mass() -> None:
    """`docs/VERIFICATION.md` § "Washout test".

    After loading the compartments, setting $F_D=0$ must produce finite,
    nonnegative washout without spontaneous increases in total system mass.

    The mass is sampled at every step rather than at the endpoints, because
    the claim is about *spontaneous* increases. A rise and a matching fall
    inside the run leave the endpoints in the right order, and such a rise is
    exactly what this test is meant to catch.

    The test checks total stored mass only. The same section of `docs/VERIFICATION.md` states that
    individual tissue concentrations may temporarily rise through
    redistribution, so this test must not require every compartment to fall,
    and deliberately asserts nothing about any compartment on its own.

    The mass-balance identity cannot serve as this gate. That identity holds
    by construction whatever the transfer rates are, because every internal
    transfer is applied as an equal-and-opposite pair. This was confirmed by
    mutation on 2026-09-07, not only argued. Dropping the write-back in
    `AgentUptakeSystem.set_delivered_concentration_percent`, so that the dial
    never actually reaches zero, fails this test at the first washout step,
    while `test_long_wash_in_and_washout_validate_agent_simulation` still
    passes.

    A reversed exhaust term is not a good example for this test, although the
    item that asked for the test used it. Both forms of that mutation are
    caught before this gate. Reversing the accumulator alone trips the
    mass-balance validator during loading. Reversing the circuit's own exhaust
    drain in `build_system_matrix` is refused by the propagator's Metzler
    precondition, which requires every off-diagonal entry to be nonnegative.

    The comparison is exact rather than within a tolerance. Measured on this
    run on 2026-11-21, at the one-second step, no step rose at all, and the
    smallest single-step fall was 6.70e-05 L. That is about 2.4e12 ulps,
    twelve orders of magnitude above rounding. So an exact assertion is not at
    risk of a floating-point flake, and a tolerance would only blind the gate
    to a real reversal.
    """

    system = AgentUptakeSystem.default()

    _run_for(system, duration_s=WASHOUT_LOAD_DURATION_S)

    loaded_agent_l = system.total_stored_agent_l

    assert loaded_agent_l > 0.0

    system.set_delivered_concentration_percent(Percent(0.0))

    previous_agent_l = loaded_agent_l

    for step_index in range(WASHOUT_DURATION_S // SIMULATION_STEP_S):
        system.advance()

        current_agent_l = system.total_stored_agent_l

        assert isfinite(current_agent_l), f"step {step_index} left total mass non-finite"
        assert current_agent_l >= 0.0, f"step {step_index} drove total mass negative"
        assert current_agent_l <= previous_agent_l, (
            f"step {step_index} raised total stored mass with the vaporizer off: "
            f"{previous_agent_l!r} -> {current_agent_l!r}"
        )

        previous_agent_l = current_agent_l

    # Not vacuous: the run has to have actually washed out.
    assert previous_agent_l < loaded_agent_l


def test_reset_clears_system_and_validation_accounting() -> None:
    system = AgentUptakeSystem.default()

    _run_for(system, duration_s=60)

    assert system.total_stored_agent_l > 0.0
    assert system.agent_simulation_validation.delivered_agent_l > 0.0

    system.reset()

    validation = system.agent_simulation_validation

    assert system.total_stored_agent_l == 0.0
    assert validation.initial_agent_l == 0.0
    assert validation.delivered_agent_l == 0.0
    assert validation.exhausted_agent_l == 0.0
    assert validation.currently_stored_agent_l == 0.0
    assert validation.unaccounted_agent_l == 0.0
    assert validation.absolute_error_l == 0.0
    assert validation.passes_validation is True


def test_equilibrium_produces_no_net_internal_transfer() -> None:
    """All connected compartments at one fraction must not exchange agent.

    Required test from docs/VERIFICATION.md: if F_C = F_A = F_a = F_v = F_i, every
    internal transfer rate must be zero. Fresh gas flow is held at zero so
    the only transfers under test are the internal circuit-alveolar,
    tissue, and venous exchanges.
    """

    system = AgentUptakeSystem.default()
    system.set_fresh_gas_flow(FreshGasFlow(0.0))

    equilibrium_fraction = Fraction(0.05)

    system.circuit.set_agent_amount(system.circuit.circuit_volume_l * equilibrium_fraction)
    system.alveoli.set_partial_pressure_fraction(equilibrium_fraction)
    system.patient.vessel_rich.set_partial_pressure_fraction(equilibrium_fraction)
    system.patient.muscle.set_partial_pressure_fraction(equilibrium_fraction)
    system.patient.fat.set_partial_pressure_fraction(equilibrium_fraction)
    system.patient.venous_blood.set_partial_pressure_fraction(equilibrium_fraction)

    # Re-baseline agent accounting: the compartment stores above were set
    # directly rather than delivered, so the validator's initial reference
    # amount must match the state actually under test.
    system.agent_simulation_validator.reset(initial_agent_l=system.total_stored_agent_l)

    result = system.advance()

    assert result.circuit_to_alveolar_agent_l == pytest.approx(
        0.0, abs=EQUILIBRIUM_FRACTION_TOLERANCE
    )
    assert result.patient_agent_change_l == pytest.approx(0.0, abs=EQUILIBRIUM_FRACTION_TOLERANCE)
    assert system.circuit.inspired_partial_pressure_fraction == pytest.approx(equilibrium_fraction)
    assert system.alveoli.partial_pressure_fraction == pytest.approx(equilibrium_fraction)
    assert system.patient.vessel_rich.partial_pressure_fraction == pytest.approx(
        equilibrium_fraction
    )
    assert system.patient.muscle.partial_pressure_fraction == pytest.approx(equilibrium_fraction)
    assert system.patient.fat.partial_pressure_fraction == pytest.approx(equilibrium_fraction)
    assert system.patient.mixed_venous_partial_pressure_fraction == pytest.approx(
        equilibrium_fraction
    )
    assert system.agent_simulation_validation.passes_validation is True


def test_higher_blood_gas_solubility_slows_alveolar_to_circuit_rise() -> None:
    """Higher blood:gas solubility must slow the rise of F_A / F_C.

    Required test from docs/VERIFICATION.md: increasing the blood:gas partition
    coefficient must increase blood capacity and slow this ratio's approach
    to one, in an otherwise identical synthetic system.
    """

    low_solubility = _build_system_with_blood_gas_coefficient(0.3)
    high_solubility = _build_system_with_blood_gas_coefficient(3.0)

    _run_for(low_solubility, duration_s=60)
    _run_for(high_solubility, duration_s=60)

    low_ratio = (
        low_solubility.alveoli.partial_pressure_fraction
        / low_solubility.circuit.inspired_partial_pressure_fraction
    )
    high_ratio = (
        high_solubility.alveoli.partial_pressure_fraction
        / high_solubility.circuit.inspired_partial_pressure_fraction
    )

    assert high_ratio < low_ratio
