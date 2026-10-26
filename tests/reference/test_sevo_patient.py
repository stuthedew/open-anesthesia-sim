from math import isfinite

import pytest

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
from anesthesia_sim.core.simulation_step import (
    MAXIMUM_SIMULATION_STEP_S,
    MINIMUM_SIMULATION_STEP_S,
    SimulationStep,
)
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

EQUILIBRIUM_FRACTION_TOLERANCE = 1e-12

# The conservation bound that the reference runs must meet. It is restated
# here rather than imported, for the reason that
# `tests/unit/test_agent_simulation_validation.py` gives: a bound that followed
# the constant it tests would move wherever that constant moved.
# `docs/MODEL.md` § "Mass-balance identity" is the documented basis and gives
# the derivation.
#
# The bound is relative, not absolute. The mass-balance residual is rounding
# accumulated once per step, so it scales with how much agent a run has
# handled. Halving the dial halves `absolute_error_l` exactly and leaves
# `relative_error` unchanged to four significant figures. So asserting the
# absolute figure measured this test's own setup rather than conservation. An
# absolute bound would also be false after about an hour of simulated time. At
# these settings the absolute error first exceeds 1e-12 L at t = 3452 s, and
# these runs stop at 1200 s (`PL-4GN8`, measured 2026-09-06 on the shipped
# exact step).
MASS_BALANCE_RELATIVE_GATE = 1e-10

# The steps docs/MODEL.md § "Step-refinement test" specifies, coarsest first.
# All three are supported steps: the first is `MAXIMUM_SIMULATION_STEP_S`
# itself, and the finest is 25 times `MINIMUM_SIMULATION_STEP_S`.
STEP_REFINEMENT_STEPS_S = (0.1, 0.05, 0.025)
STEP_REFINEMENT_HORIZON_S = 60.0

# The release comparison tolerance, which docs/MODEL.md § "Step-refinement test"
# requires to be documented before tagging. It is unchanged from the two-step
# version of this gate under the operator split. Then the coarsest and finest
# steps differed by about 4e-4 relative in the alveolar fraction at 60 s, an
# order of magnitude within this tolerance. Under the exact step they differ by
# about 1.4e-13 relative (measured 2026-10-03).
STEP_REFINEMENT_RELATIVE_TOLERANCE = 5e-3
STEP_REFINEMENT_ABSOLUTE_TOLERANCE = 1e-8

# How far apart two supported steps may leave a fraction after 60 s.
#
# With the exact step, this gap is set by floating-point rounding rather than
# by a method error. Measured 2026-09-06, the worst gap between successive
# halvings across all four reported values is 8.1e-16, in the alveolar
# fraction. The two gaps for a given value sit within a factor of two of each
# other rather than halving. This bound allows about twelve times the worst
# measured gap. That leaves room for another machine's rounding, and it is
# still four orders of magnitude below the 1.4e-11 that a genuinely
# first-order method would show at these steps.
STEP_REFINEMENT_SETTLED_GAP = 1e-14

# How far the smallest supported step (the floor) may leave a fraction from
# the result of the largest (the ceiling) after the same 60 s (PL-YZ17).
#
# This bound is wider than the gap above, because the floor takes the minute
# in 60 000 steps rather than at most 2 400, and the residual is rounding
# accumulated once per step. Measured 2026-10-03, the gap is 2.4e-15 in the
# alveolar fraction, 3.6e-16 in vessel rich and 2.5e-16 in mixed venous. This
# bound allows about twelve times the worst, the same margin that the gap above
# allows. It is still more than nine orders of magnitude below one count of the
# last displayed digit, 1e-4. The gap depends on how the propagator rounds at
# that one step, and it does not vary smoothly with the step: steps near 1 ms
# reach 1.2e-14. So on a machine that rounds differently, the margin is nearer
# two and a half times.
FLOOR_SETTLED_GAP = 3e-14

# The floor at which that bound and docs/MODEL.md's figures were measured. It
# is pinned so that moving the floor without re-measuring them fails here
# instead of passing quietly. The gate also passes at floors ten times lower,
# so the gate alone cannot catch such a move.
FLOOR_MEASURED_AT_S = 1e-3


# The washout gate's run. It matches the wash-in and washout legs of
# `test_long_wash_in_and_washout_validate_agent_simulation`, so that the two
# gates describe the same trajectory: 600 s at the default dial to load the
# compartments, then 600 s at zero. `WASHOUT_STEP_S` equals
# `MAXIMUM_SIMULATION_STEP_S`, the coarsest supported step. That step is the
# hardest case for a claim that the mass falls at every step.
WASHOUT_LOAD_DURATION_S = 600.0
WASHOUT_DURATION_S = 600.0
WASHOUT_STEP_S = 0.1


def _run_for(system: AgentUptakeSystem, duration_s: float, simulation_step_s: float) -> None:
    """Advance a system for an exact number of fixed steps."""

    step_count = round(duration_s / simulation_step_s)

    for _ in range(step_count):
        system.advance(SimulationStep(simulation_step_s))


def _synthetic_agent(blood_gas_partition_coefficient: float) -> AgentParameters:
    """Build an agent identical to sevoflurane except for solubility.

    The tissue:gas partition coefficients are held fixed. So only the
    blood:gas coefficient differs between systems, and with it the blood
    capacity and every derived tissue:blood coefficient.
    """

    payload = {
        "schema_version": 4,
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
            delivered_concentration_percent=agent.mac_percent,
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

    _run_for(system, duration_s=300.0, simulation_step_s=0.1)

    validation = system.agent_simulation_validation

    assert system.total_stored_agent_l == 0.0
    assert validation.delivered_agent_l == 0.0
    assert validation.exhausted_agent_l == 0.0
    assert validation.unaccounted_agent_l == 0.0
    assert validation.passes_validation is True


def test_zero_ventilation_prevents_patient_delivery() -> None:
    system = AgentUptakeSystem.default()
    system.set_alveolar_ventilation(AlveolarVentilation(0.0))

    _run_for(system, duration_s=120.0, simulation_step_s=0.1)

    assert system.circuit.inspired_partial_pressure_fraction > 0.0
    assert system.alveoli.agent_amount_l == 0.0
    assert system.patient.total_agent_amount_l == 0.0
    assert system.agent_simulation_validation.passes_validation is True


def test_zero_cardiac_output_prevents_patient_uptake() -> None:
    system = AgentUptakeSystem.default()
    system.set_cardiac_output(CardiacOutput(0.0))

    _run_for(system, duration_s=120.0, simulation_step_s=0.1)

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

    _run_for(system, duration_s=120.0, simulation_step_s=0.1)

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

    _run_for(lower_output, duration_s=60.0, simulation_step_s=0.1)
    _run_for(higher_output, duration_s=60.0, simulation_step_s=0.1)

    assert higher_output.patient.total_agent_amount_l > lower_output.patient.total_agent_amount_l
    assert (
        higher_output.alveoli.partial_pressure_fraction
        < lower_output.alveoli.partial_pressure_fraction
    )
    assert higher_output.agent_simulation_validation.passes_validation is True
    assert lower_output.agent_simulation_validation.passes_validation is True


def test_higher_ventilation_increases_early_alveolar_fraction() -> None:
    lower_ventilation = AgentUptakeSystem.default()
    higher_ventilation = AgentUptakeSystem.default()

    lower_ventilation.set_alveolar_ventilation(AlveolarVentilation(2.0))
    higher_ventilation.set_alveolar_ventilation(AlveolarVentilation(8.0))

    _run_for(lower_ventilation, duration_s=30.0, simulation_step_s=0.1)
    _run_for(higher_ventilation, duration_s=30.0, simulation_step_s=0.1)

    assert (
        higher_ventilation.alveoli.partial_pressure_fraction
        > lower_ventilation.alveoli.partial_pressure_fraction
    )


def _states_after_one_minute(simulation_step_s: float) -> dict[str, float]:
    """Return the three compared states after 60 s at one step size."""

    system = AgentUptakeSystem.default()
    _run_for(system, duration_s=STEP_REFINEMENT_HORIZON_S, simulation_step_s=simulation_step_s)

    return {
        "alveolar": system.alveoli.partial_pressure_fraction,
        "vessel rich": system.patient.vessel_rich.partial_pressure_fraction,
        "mixed venous": system.patient.mixed_venous_partial_pressure_fraction,
    }


def test_step_refinement_converges() -> None:
    """Compare the three steps that docs/MODEL.md specifies, not the two this test once compared.

    Two steps can only show that a pair of runs agree. Three steps show what
    the section is named for: the supported steps produce one solution rather
    than three nearby ones. Two points cannot distinguish that from
    coincidence.

    **What the third point tests changed with `PL-GS5X`, and it is now a
    stronger statement.** Under the operator split, this test asserted that
    the gaps *shrank*. That was a first-order error halving with the step,
    converging to a limit that none of the three steps reached. The step is
    now the exact solution of the governing equations. So each of the three
    steps is already at that limit, and there is no convergence left to
    observe. The gaps sit at the level of floating-point rounding, an order of
    magnitude below the smallest difference that the split's finest step could
    reach. Asserting that they still shrink would fail correct arithmetic, and
    asserting nothing would give up the gate. Instead, the test asserts that
    the step does not affect the result at all.

    Each comparison is between successive halvings rather than against the
    finest step. That is the ordinary grid-refinement idiom. It also keeps the
    documented tolerance meaning exactly what it meant when this gate compared
    two steps. Under the operator split, comparing 0.1 s directly with 0.025 s
    spanned a larger step ratio, and it exceeded the relative tolerance in
    mixed venous alone. At 60 s that compartment is only starting to fill, so
    the split's difference of 1.4e-6 in fraction was 0.55% of its value. Under
    the exact step, the two steps land about 4e-17 apart there (measured
    2026-10-03).

    This is not the reference gate. `tests/reference/test_coupled_dynamics.py`
    asks whether the shipped composition converges to the *right* answer, by
    comparing it against an independent integration. A wrong transfer rate
    applied consistently at every step size still refines consistently, so it
    would pass here. This gate checks self-consistency across the supported
    steps. That is what makes an error bound measured at one step mean
    anything at the others.
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


def test_the_smallest_supported_step_lands_on_the_ceilings_solution() -> None:
    """The smallest supported step (the floor) is checked here, as the largest is (PL-YZ17).

    `MINIMUM_SIMULATION_STEP_S` is set at the finest step at which the solution
    has been shown to be the shipped one, and this test is that showing. A
    minute of the default wash-in taken in steps of the floor lands within
    accumulated rounding of the same minute taken in steps of the ceiling, the
    largest supported step. Below the floor, that rounding is a growing
    share of what each step changes. So a lower floor has to pass this test
    before it can be declared.

    The test compares against the ceiling rather than the finest step of the
    gate above, because the claim is that the two ends of the supported
    interval agree. The successive halvings above cover the steps between.
    """

    assert MINIMUM_SIMULATION_STEP_S == FLOOR_MEASURED_AT_S, (
        f"the floor moved to {MINIMUM_SIMULATION_STEP_S} s; FLOOR_SETTLED_GAP and the "
        'figures in docs/MODEL.md "Supported simulation step" were measured at '
        f"{FLOOR_MEASURED_AT_S} s, so re-measure them at the new floor before moving it"
    )

    ceiling = _states_after_one_minute(MAXIMUM_SIMULATION_STEP_S)
    floor = _states_after_one_minute(MINIMUM_SIMULATION_STEP_S)

    for label, value in ceiling.items():
        gap = abs(value - floor[label])

        assert gap <= FLOOR_SETTLED_GAP, (
            f"{label} after a minute of {MINIMUM_SIMULATION_STEP_S} s steps is {gap:.1e} from "
            f"the {MAXIMUM_SIMULATION_STEP_S} s solution, above the {FLOOR_SETTLED_GAP:.0e} "
            "the floor of the supported steps may sit from it"
        )


def test_long_wash_in_and_washout_validate_agent_simulation() -> None:
    system = AgentUptakeSystem.default()

    _run_for(system, duration_s=600.0, simulation_step_s=0.1)

    system.set_delivered_concentration_percent(Percent(0.0))

    _run_for(system, duration_s=600.0, simulation_step_s=0.1)

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
    """`docs/MODEL.md` § "Washout test".

    After loading the compartments, setting $F_D=0$ must produce finite,
    nonnegative washout without spontaneous increases in total system mass.

    The mass is sampled at every step rather than at the endpoints, because
    the claim is about *spontaneous* increases. A rise and a matching fall
    inside the run leave the endpoints in the right order, and such a rise is
    exactly what this test is meant to catch.

    The test checks total stored mass only. MODEL.md states in the same section that
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
    run on 2026-09-07, no step rose at all, and the smallest single-step fall
    was 6.69e-06 L. That is about 2.4e11 ulps, eleven orders of magnitude
    above rounding. So an exact assertion is not at risk of a floating-point
    flake, and a tolerance would only blind the gate to a real reversal.
    """

    system = AgentUptakeSystem.default()

    _run_for(system, duration_s=WASHOUT_LOAD_DURATION_S, simulation_step_s=WASHOUT_STEP_S)

    loaded_agent_l = system.total_stored_agent_l

    assert loaded_agent_l > 0.0

    system.set_delivered_concentration_percent(Percent(0.0))

    previous_agent_l = loaded_agent_l
    step_count = round(WASHOUT_DURATION_S / WASHOUT_STEP_S)

    for step_index in range(step_count):
        system.advance(SimulationStep(WASHOUT_STEP_S))

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

    result = system.advance(SimulationStep(0.1))

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

    Required test from docs/MODEL.md: increasing the blood:gas partition
    coefficient must increase blood capacity and slow this ratio's approach
    to one, in an otherwise identical synthetic system.
    """

    low_solubility = _build_system_with_blood_gas_coefficient(0.3)
    high_solubility = _build_system_with_blood_gas_coefficient(3.0)

    _run_for(low_solubility, duration_s=60.0, simulation_step_s=0.1)
    _run_for(high_solubility, duration_s=60.0, simulation_step_s=0.1)

    low_ratio = (
        low_solubility.alveoli.partial_pressure_fraction
        / low_solubility.circuit.inspired_partial_pressure_fraction
    )
    high_ratio = (
        high_solubility.alveoli.partial_pressure_fraction
        / high_solubility.circuit.inspired_partial_pressure_fraction
    )

    assert high_ratio < low_ratio
