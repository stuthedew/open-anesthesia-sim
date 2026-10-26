"""Every core operation gives a correct answer at every corner of the inputs it accepts.

Before `PL-58D7`, each of nine floating-point defects in `core/` was found one
operation at a time. A product overflowed to `inf`, a quotient underflowed to
zero, or a subtraction cancelled, at an extreme input that the constructors
accepted. Each fix guarded its own operation and said nothing about the next.

The fix gives every input a declared interval, and refuses a value outside it
when the value is built. `docs/MODEL.md` § "The numerical envelope" lists the
intervals. This module tests the two halves of that claim.

**Every operation at every corner.** The first test runs every operation at
every corner of the intervals and checks each result against what the equations
require there. A rate, a capacity or a time constant is a product or quotient of
positive inputs. Its logarithm is a sum of the inputs' logarithms, so its
largest and smallest values over the intervals lie at their corners. An
operation added later is tested at those corners without anyone listing it,
because the test runs whole operations rather than named formulas.

**One representable value past every edge.** The second test builds every input
at each edge of its interval, and then one representable value past each edge,
and expects the simulator's own refusal. So a bound that moves, or a guard that
stops firing, fails here by name.
"""

import itertools
import sys
from collections.abc import Callable
from math import inf, isfinite, nextafter
from typing import NamedTuple

import pytest

from anesthesia_sim.core.agent_simulation_validation import AgentSimulationValidator
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.blood import VenousBloodCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationNumericalError
from anesthesia_sim.core.governing_equations import (
    DELIVERED_AGENT_L,
    EXHAUSTED_AGENT_L,
    FIRST_TISSUE_FRACTION,
    STATE_SIZE,
    UNIT_STATE,
    TissueGroupEquationSettings,
    UptakeEquationSettings,
)
from anesthesia_sim.core.matrix_exponential import MAXIMUM_SQUARINGS
from anesthesia_sim.core.numerical_envelope import (
    MAXIMUM_PARTITION_COEFFICIENT,
    MAXIMUM_VOLUME_L,
    MINIMUM_PARTITION_COEFFICIENT,
    MINIMUM_VOLUME_L,
    CompartmentVolume,
    PartitionCoefficient,
)
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

PROPAGATOR_ERROR = 3.0 * 2.0**MAXIMUM_SQUARINGS * 2.0**-52
"""The largest relative error that one propagator may carry, from the bound its module states.

`core/matrix_exponential.py` states that after `s` squarings a propagator's
entries carry an error of up to about `2**s` times the machine epsilon,
`2**-52`, and that the measured worst entry stayed within 2.7 times that bound.
It refuses a propagator that would need more than `MAXIMUM_SQUARINGS`. So no
propagator it returns is further from the exact exponential than this, which
rounds 2.7 up to 3. A state reached by composing several propagators may carry
that error once for each of them.
"""

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
"""Each pair is a blood:gas coefficient and a tissue:blood coefficient at a corner.

The two are not independent. Their product is the tissue:gas coefficient, and
all three must lie in the envelope of 0.001 to 10 000. On logarithmic axes those
three intervals cut a hexagon out of the square. Its six vertices are these
pairs, and a product or quotient of the coefficients takes its extremes at
them.
"""

PERFUSION_FRACTIONS = (0.75, 0.19, 0.06)
"""How cardiac output is split among the vessel-rich, muscle and fat groups here.

Each tissue's flow is a fraction of the cardiac output, so its extremes are
zero and the cardiac output itself. Zero cardiac output and the largest share
stand for those extremes in every run.
"""

LOPSIDED_PERFUSION_FRACTIONS = (1.0, SMALLEST_SUBNORMAL, SMALLEST_SUBNORMAL)
"""A split that sends all of the cardiac output to one group and the smallest float to each other.

A perfusion fraction is refused at zero but accepted at any positive float, so
a group can take a vanishing share of a full cardiac output. The three still
sum to exactly 1 in floating point. The coupled step runs at this split too.
"""

TISSUE_NAMES = ("vessel_rich", "muscle", "fat")

FULL_DIAL_PERCENT = 100.0
"""The dial at its widest, so that the delivered fraction is 1 and every bound below is 1."""


class Corner(NamedTuple):
    """One corner of the volumes and coefficients, with every tissue at the same corner.

    Each tissue's own rates are products and quotients of its own volume and
    coefficients, so the three groups do not need separate corners for those.
    They meet only in the venous pool, which sums what each returns.
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
    """The agent the compartments hold, in litres of gas, worked from the state and the corner.

    Each gas compartment holds its volume times its fraction. The venous pool
    holds its volume times the blood:gas coefficient times its fraction, and
    each tissue its volume times its tissue:gas coefficient times its fraction
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
    corner: Corner, opening: tuple[float, ...], state: tuple[float, ...], propagators: int
) -> None:
    """Check one state of a run that opened at `opening` under the full dial or none.

    Every value is finite. Every fraction lies between its opening and its
    equilibrium, which here always means between 0 and 1. Neither accumulator
    is negative. The agent held, plus what was exhausted, equals what was held
    at the opening plus what was delivered. Each of the last two holds to within
    `PROPAGATOR_ERROR` for each of the `propagators` that were composed to reach
    the state.
    """

    tolerance = propagators * PROPAGATOR_ERROR

    assert all(isfinite(value) for value in state), state

    for fraction in state[:DELIVERED_AGENT_L]:
        assert 0.0 <= fraction <= 1.0 + tolerance, state

    assert state[DELIVERED_AGENT_L] >= 0.0
    assert state[EXHAUSTED_AGENT_L] >= 0.0

    owed_l = _stored_agent_l(corner, opening) + state[DELIVERED_AGENT_L]
    unaccounted_l = owed_l - state[EXHAUSTED_AGENT_L] - _stored_agent_l(corner, state)

    assert abs(unaccounted_l) <= tolerance * max(owed_l, 1e-300), state


COLUMNS = 60
"""How many columns the display path samples across the run, 1440 s apart."""


def _require_the_run(corner: Corner) -> None:
    """Evaluate a run across the supported run length at every flow corner.

    Each run opens either empty under the full dial, a wash-in, or full under
    the dial at zero, a washout. It is sampled on the display path at
    `COLUMNS` columns. The display path composes one propagator per column, so
    its last column carries `COLUMNS` propagators' error. It is also sampled on
    the canonical path at five instants from the step's floor to the run's end.
    The canonical path forms one propagator from the opening to each instant.
    At the stiffest corners the whole 86 400 s interval needs more squarings
    than `MAXIMUM_SQUARINGS`, so that one instant may be refused, with the
    simulator's own error. No other refusal is accepted.
    """

    for flows in FLOW_CORNERS:
        for opening_fraction, dial_percent in ((0.0, FULL_DIAL_PERCENT), (1.0, 0.0)):
            opening = _opening_state(opening_fraction)
            run = RunDefinition(
                _settings(corner, flows, dial_percent), opening, opened_at_s=CaseInstant(0.0)
            )
            run.advance_to(CaseInstant(MAXIMUM_ELAPSED_SIMULATION_TIME_S))
            window = run.evaluate(0.0, MAXIMUM_ELAPSED_SIMULATION_TIME_S, COLUMNS)

            for column, drawn in enumerate(window.states, start=1):
                _require_what_the_equations_require(corner, opening, drawn.values, column)

            for instant_s in (MINIMUM_SIMULATION_STEP_S, 0.1, 60.0, 1440.0, 86_400.0):
                try:
                    state = run.state_at(instant_s)
                except SimulationConfigurationError:
                    assert instant_s == 86_400.0
                else:
                    _require_what_the_equations_require(corner, opening, state, 1)


def _system(
    corner: Corner,
    flows: tuple[float, float, float],
    fraction: float,
    perfusion_fractions: tuple[float, float, float] = PERFUSION_FRACTIONS,
) -> AgentUptakeSystem:
    """Build the coupled system at a corner, every compartment at `fraction`."""

    fresh_gas_l_min, ventilation_l_min, cardiac_output_l_min = flows
    circuit = BreathingCircuit(
        max_delivered_concentration_percent=Percent(FULL_DIAL_PERCENT),
        circuit_volume_l=CompartmentVolume(corner.circuit_l),
        fresh_gas_flow_l_min=FreshGasFlow(fresh_gas_l_min),
        delivered_concentration_percent=Percent(FULL_DIAL_PERCENT * (1.0 - fraction)),
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
            blood_gas_partition_coefficient=PartitionCoefficient(corner.blood_gas),
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


def _require_the_system(corner: Corner) -> None:
    """Step the coupled system once, at the run's floor and at its ceiling, at every flow corner.

    `AgentUptakeSystem.advance` checks the agent balance after every step, to
    one part in 10**9, and refuses a step that misses it. One step passes that
    check at every corner. Over many steps the stiffest corners do not, which
    `PL-D88N` measures.

    A step from a full state may be refused, and only with the one refusal
    `PL-9B1M` describes: rounding takes a fraction a few units in the last place
    past 1, the fraction check refuses it, and the step is rolled back.
    """

    for flows, fraction, step_s, perfusion_fractions in itertools.product(
        FLOW_CORNERS,
        (0.0, 1.0),
        (MINIMUM_SIMULATION_STEP_S, MAXIMUM_SIMULATION_STEP_S),
        (PERFUSION_FRACTIONS, LOPSIDED_PERFUSION_FRACTIONS),
    ):
        system = _system(corner, flows, fraction, perfusion_fractions)

        try:
            result = system.advance(SimulationStep(step_s))
        except SimulationNumericalError as refusal:
            assert fraction == 1.0, refusal
            assert "is outside 0 to 1" in str(refusal), refusal
            continue

        assert isfinite(result.circuit_to_alveolar_agent_l)
        assert isfinite(result.patient_agent_change_l)
        assert result.fresh_gas_exchange.delivered_agent_l >= 0.0
        assert result.fresh_gas_exchange.exhausted_agent_l >= 0.0
        assert result.agent_accounting.passes_validation

        for held_l in (
            system.circuit.agent_amount_l,
            system.alveoli.agent_amount_l,
            system.patient.venous_blood.agent_amount_l,
            *(getattr(system.patient, name).agent_amount_l for name in TISSUE_NAMES),
        ):
            assert isfinite(held_l)
            assert held_l >= 0.0


def _require_the_compartments_alone(corner: Corner) -> None:
    """Step each compartment on its own at its step's floor and its ceiling.

    A compartment stepped alone takes a step from `MINIMUM_SIMULATION_STEP_S` to
    the supported run length (`require_compartment_step`), and a tissue or the
    venous pool takes any finite blood flow that is not negative. So the blood
    flow also runs at the largest float. The circuit's exchange must close its
    own balance, and every amount must lie between where it started and its
    equilibrium.
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

                assert abs(unaccounted_l) <= PROPAGATOR_ERROR * max(owed_l, 1e-300)

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
                    blood_gas_partition_coefficient=PartitionCoefficient(corner.blood_gas),
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

                for compartment in (tissue, venous):
                    held_l = compartment.agent_amount_l
                    change_l = compartment.advance(target, step_s, blood_flow_l_min)

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
    """At each corner, every operation gives a finite answer that the equations allow, or refuses.

    The corner fixes every volume and coefficient. Inside it, the flows run at
    zero, the smallest float and their tops, and the run opens either empty or
    full. The only refusal accepted is the canonical path's single 86 400 s
    interval at the stiffest corners.
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
        blood_gas_partition_coefficient=PartitionCoefficient(1.0),
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
    Edge("a tissue group's perfusion fraction", _build_perfusion_fraction, SMALLEST_SUBNORMAL, 1.0),
)
"""Every input with an interval of its own, and the interval as `PL-58D7` records it.

The bounds are written out here rather than read from the modules that hold
them, so that a bound which moves fails this test and is noticed. A step count
and a window's column count are whole numbers, so they are in `WHOLE_EDGES`.
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
