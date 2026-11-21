"""Every core operation returns a correct result at every corner of the inputs it accepts.

Before `PL-58D7`, nine floating-point defects in `core/` were found one
operation at a time. In each, a product overflowed to `inf`, a quotient
underflowed to zero, or a subtraction lost its precision to cancellation. Each
happened at an extreme input that the constructors accepted. Each fix guarded
its own operation and said nothing about the next.

The `PL-58D7` fix gives every input a declared interval, and refuses a value
outside that interval when the value is built. `docs/MODEL.md` § "The numerical
envelope" lists the intervals. So every value inside its interval should give a
correct result, and every value outside it should be refused. This module tests
both halves of that claim.

**Every operation at every corner.** The first test runs every operation at
every corner of the intervals. It checks each result against what the equations
require there. A rate, a capacity or a time constant is a product or quotient of
positive inputs. Its logarithm is the inputs' logarithms added or subtracted. So
its largest and smallest values over the intervals lie at the intervals'
corners. An operation added later is tested at those corners without anyone
listing it, because the test runs whole operations rather than named formulas.

**One representable value past every edge.** The second test builds every input
at each edge of its interval. It then builds each input one representable value
past each edge, and expects the simulator's own refusal. So if a bound moves or
a guard stops firing, this test fails and names the input.
"""

import itertools
from collections.abc import Callable
from math import inf, isfinite, nextafter
from typing import NamedTuple

import pytest
from test_numerical_envelope import MOST_SQUARINGS, _squarings

from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidator, rejected_check
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.blood import VenousBloodCompartment
from anesthesia_sim.core.blood_flow import BloodFlow, PerfusionFraction
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.concentration import Fraction, Percent, percent_from_fraction
from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    SimulationConfigurationError,
)
from anesthesia_sim.core.governing_equations import (
    DELIVERED_AGENT_L,
    EXHAUSTED_AGENT_L,
    FIRST_TISSUE_FRACTION,
    STATE_SIZE,
    UNIT_STATE,
    Matrix,
    TissueGroupEquationSettings,
    UptakeEquationSettings,
    build_system_matrix,
)
from anesthesia_sim.core.numerical_envelope import (
    MAXIMUM_PARTITION_COEFFICIENT,
    MAXIMUM_VOLUME_L,
    MINIMUM_PARTITION_COEFFICIENT,
    MINIMUM_VOLUME_L,
    CompartmentVolume,
    PartitionCoefficient,
)
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES
from anesthesia_sim.core.patient import PatientCompartments
from anesthesia_sim.core.prediction import predicted_states
from anesthesia_sim.core.rounding import MACHINE_EPSILON, propagator_rounding, run_rounding
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MAXIMUM_INPUT_FRACTION,
    MAXIMUM_STEP_COUNT,
    MINIMUM_COMPARTMENT_STEP_S,
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
    StepCount,
    require_compartment_step,
    require_supported_step_count,
)
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import AgentUptakeSystem, UptakeStepResult


def _propagator_error(matrix: Matrix, interval_s: float) -> float:
    """Return the relative error that one propagator over `interval_s` may carry.

    The bound uses the squarings that this matrix and interval actually need,
    counted by `test_numerical_envelope._squarings` independently of the
    module's own code. A corner that needs few squarings is held to a tight
    bound, so a cancellation that loses digits there fails the sweep.
    """

    return propagator_rounding(_squarings(matrix, interval_s))


SMALLEST_SUBNORMAL = 5e-324
"""The smallest positive float. Each flow that may be zero is also run at this value."""

VOLUMES = (MINIMUM_VOLUME_L, MAXIMUM_VOLUME_L)

COEFFICIENT_CORNERS = (
    (MINIMUM_PARTITION_COEFFICIENT, 1.0),
    (MINIMUM_PARTITION_COEFFICIENT, MAXIMUM_PARTITION_COEFFICIENT),
    (1.0, MINIMUM_PARTITION_COEFFICIENT),
    (1.0, MAXIMUM_PARTITION_COEFFICIENT),
    (MAXIMUM_PARTITION_COEFFICIENT, MINIMUM_PARTITION_COEFFICIENT),
    (MAXIMUM_PARTITION_COEFFICIENT, 1.0),
)
"""Each pair is a blood:gas and a tissue:blood partition coefficient at one corner.

The two coefficients are not independent. Their product is the tissue:gas
coefficient, and all three must lie in the envelope of 0.001 to 10 000. On
logarithmic axes, the blood:gas and tissue:blood intervals make a square, and
the tissue:gas interval cuts a hexagon out of it. These pairs are the hexagon's
six vertices. A product or quotient of the coefficients takes its largest and
smallest values at them.
"""

PERFUSION_FRACTIONS = (0.75, 0.19, 0.06)
"""How cardiac output is split among the vessel-rich, muscle and fat groups here.

Each tissue's flow is a fraction of the cardiac output, so its extremes are
zero and the cardiac output itself. Every run uses zero cardiac output and the
largest share to represent those extremes.
"""

LOPSIDED_PERFUSION_FRACTIONS = (1.0, SMALLEST_SUBNORMAL, SMALLEST_SUBNORMAL)
"""A split that sends the whole cardiac output to one group and the smallest float to the other two.

A perfusion fraction is refused at zero but accepted at any positive float, so
a group can take a vanishing share of a full cardiac output. The three still
sum to exactly 1 in floating point. The coupled step runs at this split too.
"""

TISSUE_NAMES = ("vessel_rich", "muscle", "fat")

FULL_DIAL_PERCENT = 100.0
"""A dial at 100%. It is the vaporizer maximum here, and the dial for a compartment stepped alone.

The coupled model refuses a dial above `CEILING_DIAL_PERCENT`, so the coupled
runs below use that dial instead.
"""

CEILING = MAXIMUM_INPUT_FRACTION
"""The highest fraction the coupled model starts from, 0.99 of the ambient pressure.

Each coupled run opens at this fraction, or delivers it, so that every fraction
it computes is bounded by it. A run that opened at 1 could round a fraction
past 1, and the fraction check then refused it.
"""

CEILING_DIAL_PERCENT = percent_from_fraction(Fraction(CEILING))
"""The same ceiling as a dial setting, 99%."""

OPENINGS_AND_DIALS = ((0.0, CEILING_DIAL_PERCENT), (CEILING, 0.0), (CEILING, CEILING_DIAL_PERCENT))
"""Each coupled run's opening fraction and dial: a wash-in, a washout, and an equilibrium.

The wash-in opens empty with the dial at the ceiling. The washout opens at the
ceiling with the dial off. The equilibrium opens at the ceiling with the dial
there too, so that every fraction should stay at the ceiling.
"""


class Corner(NamedTuple):
    """One corner of the volumes and coefficients, with every tissue at the same corner.

    Each tissue's own rates are products and quotients of its own volume and
    coefficients. So the three groups do not need separate corners to reach the
    extremes of those rates. The groups interact only in the venous pool, which
    sums what each group returns.
    """

    circuit_l: float
    alveolar_l: float
    venous_l: float
    tissue_l: float
    blood_gas: float
    tissue_blood: float


CORNERS = tuple(
    Corner(circuit_l, alveolar_l, venous_l, tissue_l, blood_gas, tissue_blood)
    for circuit_l, alveolar_l, venous_l, tissue_l in itertools.product(VOLUMES, repeat=4)
    for blood_gas, tissue_blood in COEFFICIENT_CORNERS
)

FLOW_CORNERS = tuple(
    itertools.product(
        (0.0, SMALLEST_SUBNORMAL, MAXIMUM_FRESH_GAS_FLOW_L_MIN),
        (0.0, SMALLEST_SUBNORMAL, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN),
        (0.0, SMALLEST_SUBNORMAL, MAXIMUM_CARDIAC_OUTPUT_L_MIN),
    )
)
"""Each of the three flows at zero, at the smallest float and at its supported maximum."""


def _tissue_flows_l_min(cardiac_output_l_min: float) -> tuple[BloodFlow, BloodFlow, BloodFlow]:
    """Split the cardiac output so that the three shares sum to it exactly.

    The third share is what the first two leave, so it is not the output times
    a fraction. Each share is built as the whole of a cardiac output of its
    own size, which is the same number (`PL-GKG4`).
    """

    vessel_rich = cardiac_output_l_min * PERFUSION_FRACTIONS[0]
    muscle = cardiac_output_l_min * PERFUSION_FRACTIONS[1]
    fat = cardiac_output_l_min - vessel_rich - muscle

    return (
        BloodFlow(CardiacOutput(vessel_rich), PerfusionFraction(1.0)),
        BloodFlow(CardiacOutput(muscle), PerfusionFraction(1.0)),
        BloodFlow(CardiacOutput(fat), PerfusionFraction(1.0)),
    )


def _settings(
    corner: Corner, flows: tuple[float, float, float], dial_percent: float
) -> UptakeEquationSettings:
    fresh_gas_l_min, ventilation_l_min, cardiac_output_l_min = flows

    return UptakeEquationSettings(
        circuit_volume_l=CompartmentVolume(corner.circuit_l),
        alveolar_volume_l=CompartmentVolume(corner.alveolar_l),
        venous_volume_l=CompartmentVolume(corner.venous_l),
        fresh_gas_flow_l_min=FreshGasFlow(fresh_gas_l_min),
        alveolar_ventilation_l_min=AlveolarVentilation(ventilation_l_min),
        cardiac_output_l_min=CardiacOutput(cardiac_output_l_min),
        blood_gas_partition_coefficient=PartitionCoefficient(corner.blood_gas),
        delivered_concentration_percent=Percent(dial_percent),
        max_delivered_concentration_percent=Percent(FULL_DIAL_PERCENT),
        tissues=tuple(
            TissueGroupEquationSettings(
                name,
                CompartmentVolume(corner.tissue_l),
                flow_l_min,
                PartitionCoefficient(corner.tissue_blood),
            )
            for name, flow_l_min in zip(
                TISSUE_NAMES, _tissue_flows_l_min(cardiac_output_l_min), strict=True
            )
        ),
    )


def _opening_state(fraction: float) -> tuple[float, ...]:
    """Every compartment at `fraction`, nothing delivered or exhausted yet."""

    state = [fraction] * STATE_SIZE
    state[DELIVERED_AGENT_L] = 0.0
    state[EXHAUSTED_AGENT_L] = 0.0
    state[UNIT_STATE] = 1.0

    return tuple(state)


def _stored_agent_l(corner: Corner, state: tuple[float, ...]) -> float:
    """Return the agent held in the compartments, in litres of gas, from the state and the corner.

    Each gas compartment holds its volume times its fraction. The venous pool
    holds its volume times the blood:gas coefficient times its fraction. Each
    tissue holds its volume times its tissue:gas coefficient times its fraction
    (`docs/MODEL.md` § "Governing equations").
    """

    tissue_gas = corner.tissue_blood * corner.blood_gas

    return (
        corner.circuit_l * state[0]
        + corner.alveolar_l * state[1]
        + corner.venous_l * corner.blood_gas * state[2]
        + sum(
            corner.tissue_l * tissue_gas * state[FIRST_TISSUE_FRACTION + index]
            for index in range(len(TISSUE_NAMES))
        )
    )


def _require_what_the_equations_require(
    corner: Corner, opening: tuple[float, ...], state: tuple[float, ...], tolerance: float
) -> None:
    """Check one state of a run that opened at `opening`, with the dial at the ceiling or off.

    Every value is finite. Every fraction lies from 0 through 1, the range that
    a fraction is checked against, with no allowance. Every
    fraction also lies between its opening value and its equilibrium, which
    here always means from 0 to `CEILING`, to within a relative error of
    `tolerance`. Neither accumulator is negative. The agent held now, plus the
    agent exhausted, equals the agent held at the opening plus the agent
    delivered, to within `tolerance` too. `tolerance` is the sum of the bounds
    of the propagators that were composed to reach the state.
    """

    assert all(isfinite(value) for value in state), state

    for fraction in state[:DELIVERED_AGENT_L]:
        assert 0.0 <= fraction <= 1.0, state
        assert fraction <= CEILING * (1.0 + tolerance), state

    assert state[DELIVERED_AGENT_L] >= 0.0
    assert state[EXHAUSTED_AGENT_L] >= 0.0

    owed_l = _stored_agent_l(corner, opening) + state[DELIVERED_AGENT_L]
    unaccounted_l = owed_l - state[EXHAUSTED_AGENT_L] - _stored_agent_l(corner, state)

    assert abs(unaccounted_l) <= tolerance * max(owed_l, 1e-300), state


PREDICTED_SECONDS = 60
"""How many seconds each run is predicted for, one step for each second."""


def _require_the_run(corner: Corner) -> None:
    """Predict a run for `PREDICTED_SECONDS` seconds at every flow corner.

    Each run is a wash-in, a washout or an equilibrium, from
    `OPENINGS_AND_DIALS`, with the input ceiling as the highest fraction.
    `predicted_states` applies the propagator of one step once for each
    second, as a preview does, so the state at second `n` carries the error
    of `n` propagators. A run of the supported run length is predicted in
    `test_a_state_at_the_fraction_ceiling_stays_within_one_atmosphere`, at
    the two corners where rounding went furthest.
    """

    for flows in FLOW_CORNERS:
        for opening_fraction, dial_percent in OPENINGS_AND_DIALS:
            opening = _opening_state(opening_fraction)
            settings = _settings(corner, flows, dial_percent)
            step_error = _propagator_error(build_system_matrix(settings), SIMULATION_STEP_S)
            predicted = predicted_states(
                settings, opening, CaseInstant(0), CaseInstant(PREDICTED_SECONDS)
            )

            assert len(predicted) == PREDICTED_SECONDS + 1

            for second, state in enumerate(predicted[1:], start=1):
                _require_what_the_equations_require(corner, opening, state, second * step_error)


def _system(
    corner: Corner,
    flows: tuple[float, float, float],
    fraction: float,
    dial_percent: float,
    perfusion_fractions: tuple[float, float, float] = PERFUSION_FRACTIONS,
    part_at_one: str | None = None,
) -> AgentUptakeSystem:
    """Build the coupled system at a corner, with every compartment at `fraction`.

    The dial is set to `dial_percent`. `part_at_one`, when given, names one part
    of `OPENING_PARTS` to set to a fraction of 1 instead. The other parts stay at
    `fraction`. So the only check that can reject the system is the opening check
    on that one part, which runs when the system is built.
    """

    fresh_gas_l_min, ventilation_l_min, cardiac_output_l_min = flows
    circuit = BreathingCircuit(
        max_delivered_concentration_percent=Percent(FULL_DIAL_PERCENT),
        circuit_volume_l=CompartmentVolume(corner.circuit_l),
        fresh_gas_flow_l_min=FreshGasFlow(fresh_gas_l_min),
        delivered_concentration_percent=Percent(dial_percent),
    )
    alveoli = AlveolarCompartment(
        gas_volume_l=CompartmentVolume(corner.alveolar_l),
        alveolar_ventilation_l_min=AlveolarVentilation(ventilation_l_min),
    )
    tissues = [
        TissueGroup(
            name=name,
            volume_l=CompartmentVolume(corner.tissue_l),
            perfusion_fraction=PerfusionFraction(perfusion_fraction),
            tissue_gas_partition_coefficient=PartitionCoefficient(
                corner.tissue_blood * corner.blood_gas
            ),
        )
        for name, perfusion_fraction in zip(TISSUE_NAMES, perfusion_fractions, strict=True)
    ]
    venous = VenousBloodCompartment(
        volume_l=CompartmentVolume(corner.venous_l),
        blood_gas_partition_coefficient=PartitionCoefficient(corner.blood_gas),
    )

    circuit.set_inspired_partial_pressure_fraction(Fraction(fraction))
    alveoli.set_partial_pressure_fraction(Fraction(fraction))
    venous.set_partial_pressure_fraction(Fraction(fraction))

    for tissue in tissues:
        tissue.set_partial_pressure_fraction(Fraction(fraction))

    parts = {
        "inspired": circuit.set_inspired_partial_pressure_fraction,
        "alveolar": alveoli.set_partial_pressure_fraction,
        "venous": venous.set_partial_pressure_fraction,
        **{tissue.name: tissue.set_partial_pressure_fraction for tissue in tissues},
    }

    if part_at_one is not None:
        parts[part_at_one](Fraction(1.0))

    patient = PatientCompartments(
        cardiac_output_l_min=CardiacOutput(cardiac_output_l_min),
        vessel_rich=tissues[0],
        muscle=tissues[1],
        fat=tissues[2],
        venous_blood=venous,
    )

    return AgentUptakeSystem(
        circuit=circuit,
        alveoli=alveoli,
        patient=patient,
        agent_simulation_validator=AgentSimulationValidator(),
    )


def _held_amounts_l(system: AgentUptakeSystem) -> tuple[float, ...]:
    """Return the agent each compartment of the system holds, in litres of gas."""

    return (
        system.circuit.agent_amount_l,
        system.alveoli.agent_amount_l,
        system.patient.venous_blood.agent_amount_l,
        *(getattr(system.patient, name).agent_amount_l for name in TISSUE_NAMES),
    )


def _step_unless_the_balance_check_refuses(system: AgentUptakeSystem) -> UptakeStepResult | None:
    """Take one step, and return None where the agent balance check refused it for rounding.

    `AgentUptakeSystem.advance` checks the agent balance after every step, to
    one part in 10**9, and refuses a step that fails that check. A step that
    needs fewer than 22 squarings passes the check at every corner. A step
    that needs 22 can fail it, because one propagator's rounding is then
    bounded by 9.3e-9 of the state (`propagator_rounding(22)`), which is above
    the check's limit. On 2026-11-21 the check refused 76 of the 864 first
    steps that need 22 squarings, at 8 of the 96 corners, and the largest
    imbalance was 1.7e-9 of the agent handled (`PL-SZ6G`). At the earlier step
    of 0.1 s every first step passed, and the stiffest corners failed within
    seconds (`PL-D88N`).

    A refusal is accepted only where the step needs `MOST_SQUARINGS`, only for
    an imbalance within that propagator bound, and only when the step was
    rolled back.
    """

    squarings = _squarings(build_system_matrix(system.equation_settings()), SIMULATION_STEP_S)
    before = system.state_vector()

    try:
        return system.advance()
    except AgentSimulationValidationError as refusal:
        check = rejected_check(refusal)

        assert squarings == MOST_SQUARINGS, (squarings, str(refusal))
        assert check is not None
        assert check.relative_error <= propagator_rounding(squarings)
        assert system.state_vector() == before

        return None


def _require_the_system(corner: Corner) -> None:
    """Step the coupled system once at every flow corner.

    Each step must either complete or be refused by the agent balance check
    for rounding, as `_step_unless_the_balance_check_refuses` accepts.

    A step that completes must do so from each opening and dial in
    `OPENINGS_AND_DIALS`. Before the input ceiling, a step from a state with every
    compartment at 1 could round a fraction past 1. The fraction check refused
    it, the step was rolled back, and this test accepted that refusal by name.
    The coupled model's inputs now stop at `CEILING`, so that refusal must not
    happen. Every fraction after the step must lie from 0 through 1. It must
    also exceed the ceiling by no more than one step's propagator bound, taken
    at the largest number of squarings that any corner's step needs.
    """

    largest_fraction = CEILING * (1.0 + propagator_rounding(MOST_SQUARINGS))

    for flows, (fraction, dial_percent), perfusion_fractions in itertools.product(
        FLOW_CORNERS, OPENINGS_AND_DIALS, (PERFUSION_FRACTIONS, LOPSIDED_PERFUSION_FRACTIONS)
    ):
        system = _system(corner, flows, fraction, dial_percent, perfusion_fractions)
        result = _step_unless_the_balance_check_refuses(system)

        if result is None:
            continue

        for computed in system.state_vector()[:DELIVERED_AGENT_L]:
            assert 0.0 <= computed <= 1.0
            assert computed <= largest_fraction, computed

        assert isfinite(result.circuit_to_alveolar_agent_l)
        assert isfinite(result.patient_agent_change_l)
        assert result.fresh_gas_exchange.delivered_agent_l >= 0.0
        assert result.fresh_gas_exchange.exhausted_agent_l >= 0.0
        assert result.agent_accounting.passes_validation

        for held_l in _held_amounts_l(system):
            assert isfinite(held_l)
            assert held_l >= 0.0


def _require_the_compartments_alone(corner: Corner) -> None:
    """Step each compartment on its own at the shortest and the longest step it accepts.

    A compartment stepped alone accepts a step from `MINIMUM_COMPARTMENT_STEP_S`
    up to the supported run length, as `require_compartment_step` checks. The
    venous pool's blood flow is the cardiac output, and a tissue's is a
    perfusion fraction of it. So each runs at zero, at the smallest positive
    float and at the largest supported cardiac output, the largest flow that
    can be built (`PL-GKG4`). The circuit's exchange must close its own agent
    balance. Every amount must lie between its starting value and its
    equilibrium.
    """

    for step_s in (MINIMUM_COMPARTMENT_STEP_S, MAXIMUM_ELAPSED_SIMULATION_TIME_S):
        for fraction in (0.0, 1.0):
            target = Fraction(1.0 - fraction)

            for fresh_gas_l_min in (0.0, SMALLEST_SUBNORMAL, MAXIMUM_FRESH_GAS_FLOW_L_MIN):
                circuit = BreathingCircuit(
                    max_delivered_concentration_percent=Percent(FULL_DIAL_PERCENT),
                    circuit_volume_l=CompartmentVolume(corner.circuit_l),
                    fresh_gas_flow_l_min=FreshGasFlow(fresh_gas_l_min),
                    delivered_concentration_percent=Percent(FULL_DIAL_PERCENT * target),
                )
                circuit.set_inspired_partial_pressure_fraction(Fraction(fraction))
                held_l = circuit.agent_amount_l

                exchange = circuit.advance_fresh_gas(step_s)

                assert 0.0 <= circuit.inspired_partial_pressure_fraction <= 1.0
                assert exchange.delivered_agent_l >= 0.0
                assert exchange.exhausted_agent_l >= 0.0

                owed_l = held_l + exchange.delivered_agent_l
                unaccounted_l = owed_l - exchange.exhausted_agent_l - circuit.agent_amount_l

                # The circuit steps alone by a closed form, not a propagator, so
                # its balance is held to a few roundings: 0.73 of one measured.
                assert abs(unaccounted_l) <= 4 * MACHINE_EPSILON * max(owed_l, 1e-300)

            for cardiac_output_l_min in map(
                CardiacOutput, (0.0, SMALLEST_SUBNORMAL, MAXIMUM_CARDIAC_OUTPUT_L_MIN)
            ):
                # The tissue takes the whole cardiac output, so its flow runs to the
                # largest blood flow that can be built.
                blood_flow_l_min = BloodFlow(cardiac_output_l_min, PerfusionFraction(1.0))
                tissue = TissueGroup(
                    name="corner",
                    volume_l=CompartmentVolume(corner.tissue_l),
                    perfusion_fraction=PerfusionFraction(1.0),
                    tissue_gas_partition_coefficient=PartitionCoefficient(
                        corner.tissue_blood * corner.blood_gas
                    ),
                )
                tissue.set_partial_pressure_fraction(Fraction(fraction))
                venous = VenousBloodCompartment(
                    volume_l=CompartmentVolume(corner.venous_l),
                    blood_gas_partition_coefficient=PartitionCoefficient(corner.blood_gas),
                )
                venous.set_partial_pressure_fraction(Fraction(fraction))

                held_l_by_compartment = (tissue.agent_amount_l, venous.agent_amount_l)
                changes_l = (
                    tissue.advance(
                        target, step_s, blood_flow_l_min, PartitionCoefficient(corner.blood_gas)
                    ),
                    venous.advance(target, step_s, cardiac_output_l_min),
                )

                for compartment, held_l, change_l in zip(
                    (tissue, venous), held_l_by_compartment, changes_l, strict=True
                ):
                    assert isfinite(change_l)
                    assert change_l == compartment.agent_amount_l - held_l
                    assert (
                        min(held_l, compartment.capacity_l * target)
                        <= compartment.agent_amount_l
                        <= max(held_l, compartment.capacity_l * target)
                    )


def test_the_corners_are_the_96_that_the_envelope_has() -> None:
    """Sixteen volume corners times the six vertices of the coefficients' hexagon."""

    assert len(CORNERS) == 96
    assert len(set(CORNERS)) == 96


@pytest.mark.parametrize("corner", CORNERS, ids=lambda corner: "-".join(f"{v:g}" for v in corner))
def test_every_core_operation_holds_its_equations_at_every_envelope_corner(corner: Corner) -> None:
    """At each corner, every operation returns a finite result that the equations allow, or refuses.

    The corner fixes every volume and coefficient. At each corner, the flows run
    at zero, at the smallest float and at their supported maximums. The run opens
    empty or at the input ceiling. No refusal is accepted. Before the input
    ceiling, one was: a step from a state at 1 that rounded a fraction past
    1. A state at the ceiling must never be refused that way.
    """

    _require_the_run(corner)
    _require_the_system(corner)
    _require_the_compartments_alone(corner)


class Edge(NamedTuple):
    """One input, the closed interval it is refused outside, and how to build it from a value."""

    name: str
    build: Callable[[float], object]
    lowest: float
    highest: float


def _build_compartment_step(value: float) -> float:
    require_compartment_step("compartment simulation_step_s", value)

    return value


def _build_step_count_of_a_supported_run(value: float) -> int:
    count = StepCount(int(value))
    require_supported_step_count(count)

    return count


def _build_case_instant(value: float) -> CaseInstant:
    return CaseInstant(int(value))


def _build_dial_in_a_settings_record(value: float) -> UptakeEquationSettings:
    return _settings(CORNERS[0], (0.0, 0.0, 0.0), value)


def _build_dial_of_the_coupled_system(value: float) -> AgentUptakeSystem:
    system = _system(CORNERS[0], (0.0, 0.0, 0.0), 0.0, 0.0)
    system.set_delivered_concentration_percent(Percent(value))

    return system


def _build_coupled_system_opening_at(value: float) -> AgentUptakeSystem:
    return _system(CORNERS[0], (0.0, 0.0, 0.0), value, 0.0)


EDGES = (
    Edge("CompartmentVolume", CompartmentVolume, 1e-2, 1e4),
    Edge("PartitionCoefficient", PartitionCoefficient, 1e-3, 1e4),
    Edge("FreshGasFlow", FreshGasFlow, 0.0, 10.0),
    Edge("AlveolarVentilation", AlveolarVentilation, 0.0, 12.0),
    Edge("CardiacOutput", CardiacOutput, 0.0, 10.0),
    Edge("a compartment's own step", _build_compartment_step, 1e-3, 86_400.0),
    Edge("Fraction", Fraction, 0.0, 1.0),
    Edge("Percent", Percent, 0.0, 100.0),
    Edge(
        "the delivered concentration a settings record holds",
        _build_dial_in_a_settings_record,
        0.0,
        99.0,
    ),
    Edge("the coupled system's dial", _build_dial_of_the_coupled_system, 0.0, 99.0),
    Edge("a fraction the coupled system opens from", _build_coupled_system_opening_at, 0.0, 0.99),
    Edge("PerfusionFraction", PerfusionFraction, SMALLEST_SUBNORMAL, 1.0),
)
"""Every input with an interval of its own, and the interval that `docs/MODEL.md` records for it.

The bounds are written out here rather than read from the modules that define
them. So a bound that moves fails this test and is noticed. A case instant and
a step count are whole numbers, so they are in `WHOLE_EDGES`.
"""

WHOLE_EDGES = (
    Edge("CaseInstant", _build_case_instant, 0, 86_400),
    Edge("StepCount of a supported run", _build_step_count_of_a_supported_run, 0, 86_400),
)


@pytest.mark.parametrize("edge", EDGES + WHOLE_EDGES, ids=lambda edge: edge.name)
def test_every_core_operation_refuses_inputs_outside_its_floating_point_domain(edge: Edge) -> None:
    """Each input is built at both edges of its interval and refused one value past either.

    For a float, one value past an edge is the next representable float
    outward, `nextafter`. For a whole number it is the next whole number. The
    refusal must be the simulator's own `SimulationConfigurationError`, so a
    caller that catches the simulator's errors catches it.
    """

    whole = edge in WHOLE_EDGES
    below = edge.lowest - 1 if whole else nextafter(edge.lowest, -inf)
    above = edge.highest + 1 if whole else nextafter(edge.highest, inf)

    edge.build(edge.lowest)
    edge.build(edge.highest)

    for outside in (below, above):
        with pytest.raises(SimulationConfigurationError):
            edge.build(outside)


STIFFEST_DRAWN_CORNER = Corner(
    MINIMUM_VOLUME_L,
    MINIMUM_VOLUME_L,
    MINIMUM_VOLUME_L,
    MINIMUM_VOLUME_L,
    MAXIMUM_PARTITION_COEFFICIENT,
    MINIMUM_PARTITION_COEFFICIENT,
)
"""Every volume at its floor, blood:gas at its ceiling and tissue:blood at its floor.

From a state at 1 with the dial off, ventilation and cardiac output at their
maximums and no fresh gas, a state computed by formula across 24 hours reached
1.000033 here, before the input ceiling. It was the largest fraction in the
sweep (measured 2026-10-31).
"""


OPENING_PARTS = (
    ("inspired", "inspired_partial_pressure_fraction"),
    ("alveolar", "alveolar partial_pressure_fraction"),
    ("venous", "venous partial_pressure_fraction"),
    ("vessel_rich", "vessel_rich partial_pressure_fraction"),
    ("muscle", "muscle partial_pressure_fraction"),
    ("fat", "fat partial_pressure_fraction"),
)
"""Each part that holds a fraction at the opening, and the name its refusal gives."""


@pytest.mark.parametrize(("part", "named"), OPENING_PARTS, ids=[part for part, _ in OPENING_PARTS])
def test_each_part_of_the_opening_is_checked_against_the_input_ceiling(
    part: str, named: str
) -> None:
    """A system with one part at 1 and the rest at 0 is rejected, and the error names that part.

    The other tests start every part at the same fraction. In those tests, the
    first part checked rejects the system, so no test notices when the check
    is removed from any other part. On 2026-10-31, an adversarial mutation pass
    deleted each part's check in turn, and the suite still passed.
    """

    flows = (0.0, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN, MAXIMUM_CARDIAC_OUTPUT_L_MIN)
    refusal = rf"^{named} of 1\.0 is above 0\.99 of the ambient pressure"

    _system(STIFFEST_DRAWN_CORNER, flows, 0.0, 0.0)

    with pytest.raises(SimulationConfigurationError, match=refusal):
        _system(STIFFEST_DRAWN_CORNER, flows, 0.0, 0.0, part_at_one=part)


def test_a_system_built_with_its_dial_above_the_input_ceiling_is_refused() -> None:
    """Building a system from a circuit whose dial is at 100% fails at once, before any step.

    The circuit in this test allows a dial setting up to 100%, so only the
    system's own check can reject the setting. Without that check, the system
    was built, and the error came only when the first step built its settings
    record.
    """

    flows = (0.0, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN, MAXIMUM_CARDIAC_OUTPUT_L_MIN)
    refusal = r"^delivered_concentration_percent of 100(\.0)?% is above 99% of the ambient pressure"

    with pytest.raises(SimulationConfigurationError, match=refusal):
        _system(STIFFEST_DRAWN_CORNER, flows, 0.0, FULL_DIAL_PERCENT)


CEILING_REFUSAL_AT_A_FULL_DIAL = (
    "delivered_concentration_percent of 100.0% is above 99% of the ambient pressure, the highest "
    "partial pressure the coupled model starts from. It is kept below 1 so that no partial "
    "pressure the model computes exceeds the ambient pressure, which the model fixes at one "
    'atmosphere (docs/MODEL.md, "The numerical envelope")'
)
"""The whole message a learner reads when a dial of 100% is refused, written out by hand."""


def test_a_full_dial_is_refused_in_full_by_the_setter_and_by_the_settings_record() -> None:
    """A dial of 100% is refused with the whole message, even though the vaporizer allows 100%.

    The vaporizer maximum here is 100%, so the dial is exactly at that maximum.
    The setter must still check the input ceiling of 99% when the dial equals
    the maximum, not only when it is below it. The setter must also leave the
    dial as it was. A dial passed in as a plain number is refused because of
    its type, and the error names the dial. On 2026-10-31, a mutation pass
    found that no test checked the dial's name in these three messages, or the
    setter's check at the maximum.
    """

    flows = (0.0, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN, MAXIMUM_CARDIAC_OUTPUT_L_MIN)
    system = _system(STIFFEST_DRAWN_CORNER, flows, 0.0, 0.0)

    with pytest.raises(SimulationConfigurationError) as raised:
        system.set_delivered_concentration_percent(Percent(FULL_DIAL_PERCENT))

    assert str(raised.value) == CEILING_REFUSAL_AT_A_FULL_DIAL
    assert system.circuit.delivered_concentration_percent == 0.0

    with pytest.raises(SimulationConfigurationError) as raised:
        _settings(STIFFEST_DRAWN_CORNER, flows, FULL_DIAL_PERCENT)

    assert str(raised.value) == CEILING_REFUSAL_AT_A_FULL_DIAL

    with pytest.raises(TypeError, match=r"^delivered_concentration_percent of 4\.0 was not built"):
        system.set_delivered_concentration_percent(4.0)  # type: ignore[arg-type]


ROUNDING_CORNERS = (
    STIFFEST_DRAWN_CORNER,
    Corner(
        MINIMUM_VOLUME_L,
        MINIMUM_VOLUME_L,
        MAXIMUM_VOLUME_L,
        MAXIMUM_VOLUME_L,
        MAXIMUM_PARTITION_COEFFICIENT,
        MINIMUM_PARTITION_COEFFICIENT,
    ),
)
"""The corners where a computed fraction went furthest past its inputs, measured 2026-10-31.

The first reached the largest excess in a state computed by formula across 24
hours, a path that `PL-Z6C8` removed. The second, with the
circuit and lung at their floors and the venous pool and tissues at their
ceilings, took the largest excess in one step of the coupled system.
"""


def test_a_state_at_the_fraction_ceiling_stays_within_one_atmosphere() -> None:
    """From the input ceiling, a step and a 24-hour prediction both stay from 0 through 1.

    A fraction is a partial pressure as a fraction of the ambient pressure, which
    the model fixes at one atmosphere. No gas's partial pressure can exceed the
    ambient pressure, so no fraction can exceed 1. Before the input ceiling, a state with every
    compartment at 1 could not be stepped reliably: one step rounded a fraction
    to 1.0000000000349965, the check refused it, and the run halted. The
    coupled model now starts from no more than `CEILING`, and the system
    refuses to be built above it. This test steps the system, and predicts
    every second of 24 hours, at the two corners where rounding went
    furthest, from each opening and dial in `OPENINGS_AND_DIALS`. Where the
    agent balance check refuses the step for rounding, the step is rolled
    back and the state checked is the opening one. Every fraction must lie
    from 0 through 1, and none may pass the ceiling by more than 1e-4 of it,
    about three times the largest excess measured.
    """

    flows = (0.0, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN, MAXIMUM_CARDIAC_OUTPUT_L_MIN)

    for corner in ROUNDING_CORNERS:
        with pytest.raises(
            SimulationConfigurationError, match=r"of 1\.0 is above 0\.99 of the ambient"
        ):
            _system(corner, flows, 1.0, 0.0)

        for fraction, dial_percent in OPENINGS_AND_DIALS:
            system = _system(corner, flows, fraction, dial_percent)
            _step_unless_the_balance_check_refuses(system)
            predicted = predicted_states(
                _settings(corner, flows, dial_percent),
                _opening_state(fraction),
                CaseInstant(0),
                CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S),
            )

            for state in (system.state_vector(), *predicted):
                for computed in state[:DELIVERED_AGENT_L]:
                    assert 0.0 <= computed <= 1.0, state
                    assert computed <= CEILING * (1.0 + 1e-4), state


SUPPORTED_SETTING_CORNERS = tuple(
    itertools.product(
        (0.0, MAXIMUM_FRESH_GAS_FLOW_L_MIN),
        (0.0, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN),
        (0.0, MAXIMUM_CARDIAC_OUTPUT_L_MIN),
    )
)
"""Each supported flow at either end of its range."""

MOST_SQUARINGS_IN_A_SHIPPED_STEP = 3
"""The most squarings that a shipped agent's one-second step needs, measured on 2026-11-21.

Each shipped agent needs 2 at its default flows and 3 with every flow at the
top of its supported range.
"""

STEPS_OF_A_DAY_AT_THE_EARLIER_STEP = StepCount(864_000)
"""The steps in a 24-hour run at 0.1 s, the step that the interface took until `PL-SZ6G`.

No shipped agent's step of 0.1 s needed a squaring. The project owner kept the
mass-balance tolerance fixed on 2026-10-31 with that run in reach (`PL-D88N`).
"""


@pytest.mark.parametrize("agent_id", tuple(AGENT_DATA_FILENAMES))
def test_every_shipped_agent_steps_with_at_most_three_squarings_at_any_supported_setting(
    agent_id: str,
) -> None:
    """A shipped agent's step needs at most three squarings, which the fixed tolerance was kept for.

    `AgentUptakeSystem.advance` refuses a step whose agent balance is off by
    more than one part in 10**9 (`AGENT_ACCOUNTING_RELATIVE_TOLERANCE`). Each
    squaring in a step's propagator can double its rounding error. At the
    stiffest envelope corners a step needs 22, and the check then halts a
    correct run within seconds (`docs/MODEL.md` § "The numerical envelope").

    The tolerance is fixed, and it is below the derived bound on a long run's
    rounding. `run_rounding` gives that bound as a share of the largest
    fraction in the run. For 24 h at the earlier step of 0.1 s, with no
    squaring, it was 864 000 steps times 10 units, which is 1.9e-9. For 24 h
    at the one-second step, with three squarings, it is 86 400 steps times 80
    units, which is 1.5e-9. So the one-second step did not move the derived
    bound further above the tolerance, and this test asserts that. A fourth
    squaring would double the bound to 3.1e-9.

    A measurement checks the bound. Over 24 h a correct run's balance stayed
    within 9.8e-12 of closing. The worst run was sevoflurane at its highest
    dial, with fresh gas at 0.5 L/min, alveolar ventilation at 12 L/min and
    cardiac output at 10 L/min (2026-11-21, `PL-SZ6G`).

    So this test takes each shipped agent with the patient and the machine
    that `AgentUptakeSystem.for_agent` builds, which are the ones the
    application runs, and counts the squarings of its step with each flow at
    either end of its supported range. A stiffer profile, such as a small
    patient, fails here on the day it ships. That is the moment to set the
    tolerance again.
    """

    system = AgentUptakeSystem.for_agent(agent_id)
    most = 0

    for fresh_gas_l_min, ventilation_l_min, cardiac_output_l_min in SUPPORTED_SETTING_CORNERS:
        system.set_fresh_gas_flow(FreshGasFlow(fresh_gas_l_min))
        system.set_alveolar_ventilation(AlveolarVentilation(ventilation_l_min))
        system.set_cardiac_output(CardiacOutput(cardiac_output_l_min))
        squarings = _squarings(build_system_matrix(system.equation_settings()), SIMULATION_STEP_S)
        most = max(most, squarings)

        assert squarings <= MOST_SQUARINGS_IN_A_SHIPPED_STEP, (
            f"{agent_id} at {fresh_gas_l_min} L/min fresh gas, {ventilation_l_min} L/min "
            f"alveolar ventilation and {cardiac_output_l_min} L/min cardiac output needs "
            f"{squarings} squarings in a step. The mass-balance check's fixed tolerance of "
            f"1e-9 was kept for at most {MOST_SQUARINGS_IN_A_SHIPPED_STEP}, so it could "
            "halt a correct long run. Set the tolerance again from "
            "`run_rounding` for the longest run, as PL-D88N and PL-SZ6G record."
        )

    assert most == MOST_SQUARINGS_IN_A_SHIPPED_STEP
    assert run_rounding(
        MOST_SQUARINGS_IN_A_SHIPPED_STEP, StepCount(MAXIMUM_STEP_COUNT)
    ) <= run_rounding(0, STEPS_OF_A_DAY_AT_THE_EARLIER_STEP)
