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
import sys
from collections.abc import Callable
from math import inf, isfinite, nextafter
from typing import NamedTuple

import pytest
from test_numerical_envelope import MOST_SQUARINGS, _squarings

from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidator
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.blood import VenousBloodCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.concentration import Fraction, Percent, percent_from_fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationNumericalError
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
from anesthesia_sim.core.run_definition import RunDefinition
from anesthesia_sim.core.simulation_step import (
    MAXIMUM_SIMULATION_STEP_S,
    MINIMUM_SIMULATION_STEP_S,
    SimulationStep,
)
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MAXIMUM_INPUT_FRACTION,
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
    StepCount,
    require_compartment_step,
    require_supported_step_count,
)
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

MACHINE_EPSILON = 2.0**-52
"""The spacing of doubles just above 1, the unit in which a rounding error is counted."""

PROPAGATOR_MARGIN = 3.0
"""The largest multiple of the stated bound that one propagator's error may reach here.

`core/matrix_exponential.py` states that after `s` squarings, a propagator's
entries carry an error of up to about `2**s` times `MACHINE_EPSILON`. It also
states that the worst entry measured stayed within 2.7 times that bound, so
this margin rounds 2.7 up to 3. On 2026-10-26 the worst result in this sweep
reached 2.5 times the bound for the squarings it used.
"""


def _propagator_error(matrix: Matrix, interval_s: float) -> float:
    """Return the relative error that one propagator over `interval_s` may carry.

    The bound uses the squarings that this matrix and interval actually need,
    counted by `test_numerical_envelope._squarings` independently of the
    module's own code. A corner that needs few squarings is held to a tight
    bound, so a cancellation that loses digits there fails the sweep.
    """

    return PROPAGATOR_MARGIN * 2.0 ** _squarings(matrix, interval_s) * MACHINE_EPSILON


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
"""The highest fraction the coupled model starts from, 0.99 of one atmosphere.

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


def _tissue_flows_l_min(cardiac_output_l_min: float) -> tuple[float, float, float]:
    """Split the cardiac output so that the three shares sum to it exactly."""

    vessel_rich = cardiac_output_l_min * PERFUSION_FRACTIONS[0]
    muscle = cardiac_output_l_min * PERFUSION_FRACTIONS[1]

    return vessel_rich, muscle, cardiac_output_l_min - vessel_rich - muscle


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


COLUMNS = 60
"""How many columns the display path samples across the run, about 1464 s apart."""

COLUMN_SPACING_S = MAXIMUM_ELAPSED_SIMULATION_TIME_S / (COLUMNS - 1)
"""The interval between two columns, which the display path's chained propagator spans."""


def _require_the_run(corner: Corner) -> None:
    """Evaluate a run across the supported run length at every flow corner.

    Each run is a wash-in, a washout or an equilibrium, from
    `OPENINGS_AND_DIALS`, with the input ceiling as the highest fraction. Each
    run is sampled
    on the display path at `COLUMNS` columns. The display path composes one
    propagator per column, so the `n`th column carries the error of `n`
    propagators. Each run is also sampled on the canonical path at five
    instants, from the smallest supported step to the end of the run. The
    canonical path forms one propagator from the opening to each instant. At the
    stiffest corners, the whole 86 400 s interval needs more than
    `MAXIMUM_SQUARINGS` squarings. So the instant at the end of the run may be
    refused there, with the simulator's own error naming the squarings. No
    other refusal is accepted.
    """

    for flows in FLOW_CORNERS:
        for opening_fraction, dial_percent in OPENINGS_AND_DIALS:
            opening = _opening_state(opening_fraction)
            settings = _settings(corner, flows, dial_percent)
            matrix = build_system_matrix(settings)
            run = RunDefinition(settings, opening, opened_at_s=CaseInstant(0.0))
            run.advance_to(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))
            window = run.evaluate(0.0, MAXIMUM_ELAPSED_SIMULATION_TIME_S, COLUMNS)
            column_error = _propagator_error(matrix, COLUMN_SPACING_S)

            for column, drawn in enumerate(window.states, start=1):
                _require_what_the_equations_require(
                    corner, opening, drawn.values, column * column_error
                )

            for instant_s in (MINIMUM_SIMULATION_STEP_S, 0.1, 60.0, 1440.0, 86_400.0):
                try:
                    state = run.state_at(instant_s)
                except SimulationConfigurationError as refusal:
                    assert instant_s == 86_400.0, refusal
                    assert "squarings" in str(refusal), refusal
                else:
                    _require_what_the_equations_require(
                        corner, opening, state, _propagator_error(matrix, instant_s)
                    )


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
            perfusion_fraction=perfusion_fraction,
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


def _require_the_system(corner: Corner) -> None:
    """Step the coupled system once per flow corner, at the smallest and largest supported step.

    `AgentUptakeSystem.advance` checks the agent balance after every step, to
    one part in 10**9. It refuses a step that fails that check. One step passes
    the check at every corner. Over many steps, the stiffest corners fail it, as
    `PL-D88N` measures.

    Every step must complete, from each opening and dial in
    `OPENINGS_AND_DIALS`. Before the input ceiling, a step from a state with every
    compartment at 1 could round a fraction past 1. The fraction check refused
    it, the step was rolled back, and this test accepted that refusal by name.
    The coupled model's inputs now stop at `CEILING`, so the refusal must not
    happen. Every fraction after the step must lie from 0 through 1. It must
    also exceed the ceiling by no more than one step's propagator bound, taken
    at the largest number of squarings that any corner's step needs.
    """

    largest_fraction = CEILING * (1.0 + PROPAGATOR_MARGIN * 2.0**MOST_SQUARINGS * MACHINE_EPSILON)

    for flows, (fraction, dial_percent), step_s, perfusion_fractions in itertools.product(
        FLOW_CORNERS,
        OPENINGS_AND_DIALS,
        (MINIMUM_SIMULATION_STEP_S, MAXIMUM_SIMULATION_STEP_S),
        (PERFUSION_FRACTIONS, LOPSIDED_PERFUSION_FRACTIONS),
    ):
        system = _system(corner, flows, fraction, dial_percent, perfusion_fractions)
        result = system.advance(SimulationStep(step_s))

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

    A compartment stepped alone accepts a step from `MINIMUM_SIMULATION_STEP_S`
    up to the supported run length, as `require_compartment_step` checks. A
    tissue or the venous pool accepts any finite blood flow that is not
    negative. So the blood flow also runs at the largest float. The circuit's
    exchange must close its own agent balance. Every amount must lie between its
    starting value and its equilibrium.
    """

    for step_s in (MINIMUM_SIMULATION_STEP_S, MAXIMUM_ELAPSED_SIMULATION_TIME_S):
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

            for blood_flow_l_min in (
                0.0,
                SMALLEST_SUBNORMAL,
                MAXIMUM_CARDIAC_OUTPUT_L_MIN,
                sys.float_info.max,
            ):
                tissue = TissueGroup(
                    name="corner",
                    volume_l=CompartmentVolume(corner.tissue_l),
                    perfusion_fraction=1.0,
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
                    venous.advance(target, step_s, blood_flow_l_min),
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
    empty or at the input ceiling. One refusal is accepted, with the
    simulator's own error: the canonical path's refusal of its single 86 400 s
    interval at the stiffest corners. Before the input ceiling, a second refusal
    was accepted: a step from a state at 1 that rounded a fraction past 1. A
    state at the ceiling must never be refused that way.
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


def _build_perfusion_fraction(value: float) -> TissueGroup:
    return TissueGroup(
        name="edge",
        volume_l=CompartmentVolume(1.0),
        perfusion_fraction=value,
        tissue_gas_partition_coefficient=PartitionCoefficient(1.0),
    )


def _build_step_count_at_the_run_step(value: float) -> int:
    count = StepCount(int(value))
    require_supported_step_count(count, SimulationStep(0.1))

    return count


def _build_window_columns(value: float) -> int:
    run = RunDefinition(
        _settings(CORNERS[0], (0.0, 0.0, 0.0), 0.0),
        _opening_state(0.0),
        opened_at_s=CaseInstant(0.0),
    )
    run.evaluate(0.0, 0.0, int(value))

    return int(value)


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
    Edge("SimulationStep", SimulationStep, 1e-3, 0.1),
    Edge("a compartment's own step", _build_compartment_step, 1e-3, 86_400.0),
    Edge("CaseInstant", CaseInstant, 0.0, 86_400.0),
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
    Edge("a tissue group's perfusion fraction", _build_perfusion_fraction, SMALLEST_SUBNORMAL, 1.0),
)
"""Every input with an interval of its own, and the interval that `docs/MODEL.md` records for it.

The bounds are written out here rather than read from the modules that define
them. So a bound that moves fails this test and is noticed. A step count and a
window's column count are whole numbers, so they are in `WHOLE_EDGES`.
"""

WHOLE_EDGES = (
    Edge("StepCount at the 0.1 s step", _build_step_count_at_the_run_step, 0, 864_000),
    Edge("RunDefinition.evaluate columns", _build_window_columns, 1, 100_000),
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
maximums and no fresh gas, the display path drew 1.000033 here, the largest
drawn fraction in the sweep (measured 2026-10-31).
"""


def test_the_display_path_refuses_a_drawn_fraction_past_one_atmosphere() -> None:
    """A window that would draw a partial pressure above one atmosphere is refused, not returned.

    No supported opening reaches such a window. The stepped system refuses an
    opening above `CEILING`, and so does a settings record's dial. A
    `RunDefinition` opens from a state that a run passed through, which may lie
    a rounding error above the ceiling, so it checks its opening only from 0
    through 1. A caller can therefore still hand it a state at 1. Before
    the input ceiling, both display paths then returned fractions above 1 at this
    corner: 1.000033 across the whole run, and 1.0000000056 in the inspired
    fraction over the first 1000 s sampled every 100 s (measured 2026-10-31).
    Each now refuses the window with the simulator's own error, naming the
    state position that left the range. The window is short because the
    anchored path forms one propagator to its stop. At this corner, a propagator
    longer than about 1610 s needs more squarings than the module allows.
    """

    flows = (0.0, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN, MAXIMUM_CARDIAC_OUTPUT_L_MIN)
    run = RunDefinition(
        _settings(STIFFEST_DRAWN_CORNER, flows, 0.0),
        _opening_state(1.0),
        opened_at_s=CaseInstant(0.0),
    )
    run.advance_to(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))
    refusal = (
        r"^the display path computed a value it cannot draw: state\[\d\] \([^)]*\) "
        r"of 1\.0000\d+ is outside 0 to 1"
    )

    with pytest.raises(SimulationNumericalError, match=refusal):
        run.evaluate(0.0, 1000.0, 11)

    with pytest.raises(SimulationNumericalError, match=refusal):
        run.evaluate_anchored(0.0, 1000.0, 100.0)


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
    refusal = rf"^{named} of 1\.0 is above 0\.99 of one atmosphere"

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
    refusal = r"^delivered_concentration_percent of 100(\.0)?% is above 99% of one atmosphere"

    with pytest.raises(SimulationConfigurationError, match=refusal):
        _system(STIFFEST_DRAWN_CORNER, flows, 0.0, FULL_DIAL_PERCENT)


CEILING_REFUSAL_AT_A_FULL_DIAL = (
    "delivered_concentration_percent of 100.0% is above 99% of one atmosphere, the highest "
    "partial pressure the coupled model starts from. It is kept below 1 so that every partial "
    'pressure the model computes stays within one atmosphere (docs/MODEL.md, "The numerical '
    'envelope")'
)
"""The whole message a learner reads when a dial of 100% is refused, written out by hand."""


def test_a_full_dial_is_refused_in_full_by_the_setter_and_by_the_settings_record() -> None:
    """A dial of 100% is refused with the whole message, where the vaporizer allows 100%.

    The vaporizer maximum here is 100%, so the dial sits exactly at it. The
    setter must still check the ceiling at that maximum, not only below it.
    It must also leave the dial as it was. A dial passed in as a plain number
    is refused for its type, under the dial's own name. A mutation pass found
    these three names and the boundary at the maximum untested (2026-10-31).
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

The first drew the largest excess on the display path. The second, with the
circuit and lung at their floors and the venous pool and tissues at their
ceilings, took the largest excess in one step of the coupled system.
"""


def test_a_state_at_the_fraction_ceiling_stays_within_one_atmosphere() -> None:
    """From the input ceiling, a step and a drawn window both stay from 0 through 1.

    A fraction is a partial pressure, and no compartment can hold more than one
    atmosphere of agent. Before the input ceiling, a state with every
    compartment at 1 could not be stepped reliably: one step rounded a fraction
    to 1.0000000000349965, the check refused it, and the run halted. The
    display path drew 1.000033 from the same state. The coupled model now
    starts from no more than `CEILING`, and the system refuses to be built
    above it. This test steps the system and draws a 24-hour window at the two
    corners where rounding went furthest, from each opening and dial in
    `OPENINGS_AND_DIALS`. Every fraction must lie from 0 through 1, and none
    may pass the ceiling by more than 1e-4 of it, about three times the largest
    excess measured.
    """

    flows = (0.0, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN, MAXIMUM_CARDIAC_OUTPUT_L_MIN)

    for corner in ROUNDING_CORNERS:
        with pytest.raises(SimulationConfigurationError, match=r"of 1\.0 is above 0\.99 of one"):
            _system(corner, flows, 1.0, 0.0)

        for fraction, dial_percent in OPENINGS_AND_DIALS:
            system = _system(corner, flows, fraction, dial_percent)
            system.advance(SimulationStep(MAXIMUM_SIMULATION_STEP_S))
            run = RunDefinition(
                _settings(corner, flows, dial_percent),
                _opening_state(fraction),
                opened_at_s=CaseInstant(0.0),
            )
            run.advance_to(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))
            window = run.evaluate(0.0, MAXIMUM_ELAPSED_SIMULATION_TIME_S, COLUMNS)
            drawn = [state.values for state in window.states]

            for state in (system.state_vector(), *drawn):
                for computed in state[:DELIVERED_AGENT_L]:
                    assert 0.0 <= computed <= 1.0, state
                    assert computed <= CEILING * (1.0 + 1e-4), state


SUPPORTED_SETTING_CORNERS = tuple(
    itertools.product(
        (0.0, MAXIMUM_FRESH_GAS_FLOW_L_MIN),
        (0.0, MAXIMUM_ALVEOLAR_VENTILATION_L_MIN),
        (0.0, MAXIMUM_CARDIAC_OUTPUT_L_MIN),
        (MINIMUM_SIMULATION_STEP_S, MAXIMUM_SIMULATION_STEP_S),
    )
)
"""Each supported flow at either end of its range, at the step's floor and its ceiling."""


@pytest.mark.parametrize("agent_id", tuple(AGENT_DATA_FILENAMES))
def test_every_shipped_agent_steps_without_squarings_at_any_supported_setting(
    agent_id: str,
) -> None:
    """The mass-balance tolerance stays at 1e-9 only while no reachable step needs a squaring.

    `AgentUptakeSystem.advance` refuses a step whose agent balance is off by
    more than one part in 10**9 (`AGENT_ACCOUNTING_RELATIVE_TOLERANCE`). Each
    squaring in a step's propagator can double its rounding error. At the
    stiffest envelope corners a step needs 19, and the check then halts a
    correct run within seconds (`docs/MODEL.md` § "The numerical envelope").
    `PL-D88N` kept the tolerance fixed, because every setting a learner can
    reach needs none (project owner, 2026-10-31, ratified, over a tolerance
    summed from the propagator's bound, which would loosen the check up to 58
    times on a long run at the 1 ms step).

    So this test steps each shipped agent with the patient and the machine
    that `AgentUptakeSystem.for_agent` builds, which are the ones the
    application runs. Each flow is at either end of its supported range, at the
    smallest and the largest supported step. A stiffer profile, such as a
    small patient, fails here on the day it ships. That is the moment to choose
    a tolerance that widens only by what the squarings add.
    """

    system = AgentUptakeSystem.for_agent(agent_id)

    for (
        fresh_gas_l_min,
        ventilation_l_min,
        cardiac_output_l_min,
        step_s,
    ) in SUPPORTED_SETTING_CORNERS:
        system.set_fresh_gas_flow(FreshGasFlow(fresh_gas_l_min))
        system.set_alveolar_ventilation(AlveolarVentilation(ventilation_l_min))
        system.set_cardiac_output(CardiacOutput(cardiac_output_l_min))
        squarings = _squarings(build_system_matrix(system.equation_settings()), step_s)

        assert squarings == 0, (
            f"{agent_id} at {fresh_gas_l_min} L/min fresh gas, {ventilation_l_min} L/min "
            f"alveolar ventilation, {cardiac_output_l_min} L/min cardiac output and a "
            f"{step_s} s step needs {squarings} squarings. The mass-balance check's fixed "
            "tolerance of 1e-9 assumes none, so it would halt a correct long run. Choose a "
            "tolerance that widens only by what the squarings add, about "
            "3 * (2**s - 1) * 2**-52 per step summed over the accounting period, as PL-D88N "
            "records."
        )
