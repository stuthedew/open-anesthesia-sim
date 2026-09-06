import pytest
from mass_balance_gate import MASS_BALANCE_RELATIVE_GATE

from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.parameters import (
    AgentParameters,
    load_reference_adult_parameters,
    parse_agent_parameters,
)
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

EQUILIBRIUM_FRACTION_TOLERANCE = 1e-12

# The steps docs/MODEL.md § "Step-refinement test" specifies, coarsest first.
# All three are supported steps: the first is `MAXIMUM_SIMULATION_STEP_S`
# itself, and refinement only moves inward.
STEP_REFINEMENT_STEPS_S = (0.1, 0.05, 0.025)
STEP_REFINEMENT_HORIZON_S = 60.0

# The release comparison tolerance docs/MODEL.md § "Step-refinement test"
# requires be documented before tagging. Unchanged from the two-step version
# of this gate: at 60 s the coarsest and finest steps differ by about 4e-4
# relative in the alveolar fraction, an order of magnitude inside this.
STEP_REFINEMENT_RELATIVE_TOLERANCE = 5e-3
STEP_REFINEMENT_ABSOLUTE_TOLERANCE = 1e-8

# How far two supported steps may leave a fraction apart after 60 s.
#
# The exact step puts this at the floating-point floor rather than at a
# method error: measured 2026-09-06, the worst successive-halving gap across
# all four reported values is 8.1e-16 in the alveolar fraction, and the two
# gaps for a given value sit within a factor of two of each other rather than
# halving. This bound allows about twelve times the worst measured, which is
# room for another machine's rounding and still four orders below the 1.4e-11
# a genuinely first-order method would show at these steps.
STEP_REFINEMENT_SETTLED_GAP = 1e-14


def _run_for(system: AgentUptakeSystem, duration_s: float, simulation_step_s: float) -> None:
    """Advance a system for an exact number of fixed steps."""

    step_count = round(duration_s / simulation_step_s)

    for _ in range(step_count):
        system.advance(simulation_step_s)


def _synthetic_agent(blood_gas_partition_coefficient: float) -> AgentParameters:
    """Build an agent identical to sevoflurane except for solubility.

    Holds tissue:gas partition coefficients fixed so that only the
    blood:gas coefficient (and therefore blood capacity and every
    derived tissue:blood coefficient) differs between systems.
    """

    payload = {
        "schema_version": 1,
        "id": "synthetic-solubility-test-agent",
        "display_name": "Synthetic solubility test agent",
        "blood_gas_partition_coefficient": blood_gas_partition_coefficient,
        "tissue_gas_partition_coefficients": {"vessel_rich": 1.1, "muscle": 2.4, "fat": 34.0},
        "max_delivered_concentration_percent": 8.0,
        "mac_percent": 2.0,
        "mac_awake": {
            "fraction_of_mac": 0.34,
            "standard_deviation_fraction_of_mac": 0.05,
            "mac_reference_basis": "synthetic; no reference band is drawn in this test",
        },
        "sources": [
            {
                "citation": "Synthetic parameters for directional solubility testing only.",
                "url": "https://example.com/synthetic-test-agent",
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
            delivered_concentration_fraction=(agent.mac_percent / 100.0),
            max_delivered_concentration_fraction=(
                agent.max_delivered_concentration_percent / 100.0
            ),
        ),
        alveoli=AlveolarCompartment(
            gas_volume_l=patient_parameters.alveolar_gas_volume_l,
            alveolar_ventilation_l_min=(patient_parameters.default_alveolar_ventilation_l_min),
        ),
        patient=PatientCompartments.from_parameters(agent=agent, patient=patient_parameters),
    )


def test_no_delivered_agent_keeps_every_store_zero() -> None:
    system = AgentUptakeSystem.default()
    system.set_delivered_concentration(0.0)

    _run_for(system, duration_s=300.0, simulation_step_s=0.1)

    validation = system.agent_simulation_validation

    assert system.total_stored_agent_l == 0.0
    assert validation.delivered_agent_l == 0.0
    assert validation.exhausted_agent_l == 0.0
    assert validation.unaccounted_agent_l == 0.0
    assert validation.passes_validation is True


def test_zero_ventilation_prevents_patient_delivery() -> None:
    system = AgentUptakeSystem.default()
    system.set_alveolar_ventilation(0.0)

    _run_for(system, duration_s=120.0, simulation_step_s=0.1)

    assert system.circuit.circuit_concentration_fraction > 0.0
    assert system.alveoli.agent_amount_l == 0.0
    assert system.patient.total_agent_amount_l == 0.0
    assert system.agent_simulation_validation.passes_validation is True


def test_zero_cardiac_output_prevents_patient_uptake() -> None:
    system = AgentUptakeSystem.default()
    system.set_cardiac_output(0.0)

    _run_for(system, duration_s=120.0, simulation_step_s=0.1)

    assert system.alveoli.concentration_fraction > 0.0
    assert system.patient.total_agent_amount_l == 0.0
    assert system.agent_simulation_validation.passes_validation is True


def test_higher_ventilation_increases_early_alveolar_fraction() -> None:
    lower_ventilation = AgentUptakeSystem.default()
    higher_ventilation = AgentUptakeSystem.default()

    lower_ventilation.set_alveolar_ventilation(2.0)
    higher_ventilation.set_alveolar_ventilation(8.0)

    _run_for(lower_ventilation, duration_s=30.0, simulation_step_s=0.1)
    _run_for(higher_ventilation, duration_s=30.0, simulation_step_s=0.1)

    assert (
        higher_ventilation.alveoli.concentration_fraction
        > lower_ventilation.alveoli.concentration_fraction
    )


def _states_after_one_minute(simulation_step_s: float) -> dict[str, float]:
    """The three compared states after 60 s at one step size."""

    system = AgentUptakeSystem.default()
    _run_for(system, duration_s=STEP_REFINEMENT_HORIZON_S, simulation_step_s=simulation_step_s)

    return {
        "alveolar": system.alveoli.concentration_fraction,
        "vessel rich": system.patient.vessel_rich.partial_pressure_fraction,
        "mixed venous": system.patient.mixed_venous_fraction,
    }


def test_step_refinement_converges() -> None:
    """The three steps docs/MODEL.md specifies, not the two this compared.

    Two steps can only show that a pair of runs agree. Three show the thing
    the section is named for: that the solution the supported steps produce
    is one solution rather than three nearby ones, which two points cannot
    distinguish from coincidence.

    **What the third point tests changed with `PL-GS5X`, and it is now a
    stronger statement.** Under the operator split this asserted that the
    gaps *shrank* — a first-order error halving with the step, converging to
    a limit none of the three steps reached. The step is now the exact
    solution of the governing equations, so every one of the three is already
    at that limit and there is no convergence left to observe: the gaps sit
    at the floating-point floor, an order of magnitude below the smallest
    difference the split's finest step could reach. Asserting they still
    shrink would fail correct arithmetic, and asserting nothing would give
    the gate up. What is asserted instead is that the step does not enter the
    answer at all.

    Each comparison is between successive halvings rather than against the
    finest step, which is the ordinary grid-refinement idiom and is also
    what leaves the documented tolerance meaning exactly what it did when
    this gate compared two steps. Comparing 0.1 s straight to 0.025 s is a
    longer lever and does exceed the relative tolerance, in mixed venous
    alone: at 60 s that compartment is only starting to fill, so 1.4e-6 in
    fraction - a seventh of a count of the last displayed digit - is 0.55%
    of it. Loosening a release tolerance to accommodate that would be a
    change to what the gate certifies, and this item did not measure one.

    This is not the reference gate. `tests/reference/test_coupled_dynamics.py`
    asks whether the shipped composition converges to the *right* answer, by
    comparing it against an independent integration; a wrong transfer rate
    applied consistently at every step size still refines consistently and
    would pass here. What this gate holds is self-consistency across the
    supported steps, which is what makes an error bound measured at one of
    them mean anything at the others.
    """

    by_step_s = {step_s: _states_after_one_minute(step_s) for step_s in STEP_REFINEMENT_STEPS_S}
    successive = list(zip(STEP_REFINEMENT_STEPS_S, STEP_REFINEMENT_STEPS_S[1:], strict=False))

    for coarse_step_s, fine_step_s in successive:
        for label, value in by_step_s[coarse_step_s].items():
            assert value == pytest.approx(
                by_step_s[fine_step_s][label],
                rel=STEP_REFINEMENT_RELATIVE_TOLERANCE,
                abs=STEP_REFINEMENT_ABSOLUTE_TOLERANCE,
            ), f"{label} at {coarse_step_s} s disagrees with the {fine_step_s} s solution"

    for label in by_step_s[STEP_REFINEMENT_STEPS_S[-1]]:
        gaps = [
            abs(by_step_s[coarse_step_s][label] - by_step_s[fine_step_s][label])
            for coarse_step_s, fine_step_s in successive
        ]

        assert max(gaps) <= STEP_REFINEMENT_SETTLED_GAP, (
            f"{label} has not settled across the supported steps: successive "
            f"halvings move it by {gaps}, above the {STEP_REFINEMENT_SETTLED_GAP:.1e} "
            "a solution that does not depend on the step may move by"
        )


def test_long_wash_in_and_washout_validate_agent_simulation() -> None:
    system = AgentUptakeSystem.default()

    _run_for(system, duration_s=600.0, simulation_step_s=0.1)

    system.set_delivered_concentration(0.0)

    _run_for(system, duration_s=600.0, simulation_step_s=0.1)

    validation = system.agent_simulation_validation

    assert validation.passes_validation is True
    # The relative residual, not the absolute one: the absolute figure scales
    # with the dial and the run length, so asserting it measures this test's
    # setup rather than conservation (`PL-4GN8`). `mass_balance_gate` carries
    # the measurements the bound comes from.
    assert validation.relative_error <= MASS_BALANCE_RELATIVE_GATE
    assert validation.delivered_agent_l > 0.0
    assert validation.exhausted_agent_l > 0.0


def test_reset_clears_system_and_validation_accounting() -> None:
    system = AgentUptakeSystem.default()

    _run_for(system, duration_s=60.0, simulation_step_s=0.1)

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

    Required test from docs/MODEL.md: if F_C = F_A = F_a = F_v = F_i, every
    internal transfer rate must be zero. Fresh gas flow is held at zero so
    the only transfers under test are the internal circuit-alveolar,
    tissue, and venous exchanges.
    """

    system = AgentUptakeSystem.default()
    system.set_fresh_gas_flow(0.0)

    equilibrium_fraction = 0.05

    system.circuit.set_agent_amount(system.circuit.circuit_volume_l * equilibrium_fraction)
    system.alveoli.set_concentration_fraction(equilibrium_fraction)
    system.patient.vessel_rich.set_partial_pressure_fraction(equilibrium_fraction)
    system.patient.muscle.set_partial_pressure_fraction(equilibrium_fraction)
    system.patient.fat.set_partial_pressure_fraction(equilibrium_fraction)
    system.patient.venous_blood.set_concentration_fraction(equilibrium_fraction)

    # Re-baseline agent accounting: the compartment stores above were set
    # directly rather than delivered, so the validator's initial reference
    # amount must match the state actually under test.
    system.agent_simulation_validator.reset(initial_agent_l=system.total_stored_agent_l)

    result = system.advance(0.1)

    assert result.circuit_to_alveolar_agent_l == pytest.approx(
        0.0, abs=EQUILIBRIUM_FRACTION_TOLERANCE
    )
    assert result.patient_agent_change_l == pytest.approx(0.0, abs=EQUILIBRIUM_FRACTION_TOLERANCE)
    assert system.circuit.circuit_concentration_fraction == pytest.approx(equilibrium_fraction)
    assert system.alveoli.concentration_fraction == pytest.approx(equilibrium_fraction)
    assert system.patient.vessel_rich.partial_pressure_fraction == pytest.approx(
        equilibrium_fraction
    )
    assert system.patient.muscle.partial_pressure_fraction == pytest.approx(equilibrium_fraction)
    assert system.patient.fat.partial_pressure_fraction == pytest.approx(equilibrium_fraction)
    assert system.patient.mixed_venous_fraction == pytest.approx(equilibrium_fraction)
    assert system.agent_simulation_validation.passes_validation is True


def test_higher_blood_gas_solubility_slows_alveolar_to_circuit_rise() -> None:
    """Higher blood:gas solubility must slow the rise of F_A / F_C.

    Required test from docs/MODEL.md: increasing the blood:gas partition
    coefficient must increase blood capacity and slow this ratio's approach
    to one, in an otherwise identical synthetic system.
    """

    low_solubility = _build_system_with_blood_gas_coefficient(0.3)
    high_solubility = _build_system_with_blood_gas_coefficient(3.0)

    _run_for(low_solubility, duration_s=60.0, simulation_step_s=0.1)
    _run_for(high_solubility, duration_s=60.0, simulation_step_s=0.1)

    low_ratio = (
        low_solubility.alveoli.concentration_fraction
        / low_solubility.circuit.circuit_concentration_fraction
    )
    high_ratio = (
        high_solubility.alveoli.concentration_fraction
        / high_solubility.circuit.circuit_concentration_fraction
    )

    assert high_ratio < low_ratio
