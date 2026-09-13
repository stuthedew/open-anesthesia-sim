"""The contract every compartment closed form in `core/` meets.

`core/__init__.py` states it. An `advance()` on a compartment is that
compartment's own closed form against a constant stated input, not how a run
advances, and it branches on an exact zero flow rather than on a tolerance.
Both halves are properties rather than claims, so they are held here across
all three primitives at once rather than once per compartment: what is being
tested is the rule, and a fourth primitive added to `core/` without joining
`PRIMITIVES` below is the omission this module exists to make visible
(`PL-74R0`, `PL-79YX`).

**Every constant here was chosen by watching the guard removed.** Before
`PL-79YX`, deleting either zero-flow branch in `TissueGroup.advance()` or
`VenousBloodCompartment.advance()` left the whole suite green, and so did the
first draft of this module: at a loaded fraction of 0.25 against a driving
fraction of 1.0 the unguarded path is bit exact, because `d + (i - d)` is
exact wherever `i` and `d` are within a factor of two of each other. It is the
*ordinary* case that is not - a compartment well below the fraction driving
it - which is why `LOADED_FRACTION` is small.
"""

from collections.abc import Callable
from dataclasses import dataclass
from math import inf, ulp
from typing import Any

import pytest

from anesthesia_sim.core.blood import VenousBloodCompartment
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.tissue import TissueGroup

# The fraction each compartment is loaded to, and the constant input each is
# driven with: a compartment at the very start of a wash-in.
#
# Small against the driving fraction rather than comparable to it, and that is
# load-bearing. `d + (i - d) * 1.0` is what the closed form reduces to at zero
# flow, and it returns `i` bit for bit only while the two are within a factor
# of two. At these values the unguarded path lands one rounding away instead,
# which is what makes the no-op test below able to fail.
#
# Unequal for a second reason: a step that did nothing and a step that drove
# the compartment all the way to its input are the same measurement when the
# loaded and driving fractions agree.
LOADED_FRACTION = 1e-6
DRIVING_FRACTION = 1.0

# The one coarse step and the many fine ones a closed form must agree across.
COARSE_STEP_S = 60.0
FINE_STEP_S = 0.1
FINE_STEP_COUNT = 600

# Flows walked from zero upwards. The first is the smallest positive double
# there is, so if the exact branch and the general path ever disagree in a
# band above zero, this walk is inside it.
NEARLY_ZERO_FLOWS_L_MIN = (5e-324, 1e-300, 1e-30)

# The floor every comparison near zero flow sits on, as a fraction. The
# zero-flow closed form reduces to `d + (i - d)`, and that expression's
# rounding is set by the scale of the driving fraction rather than by the
# compartment's own - so it is relatively large for a compartment far below
# the input driving it, and it is what the exact branch exists to avoid. In
# litres it is a compartment's capacity times this.
ZERO_FLOW_ROUNDING_FRACTION = ulp(DRIVING_FRACTION)

# The first magnitude at which flow moves more agent than that rounding does.
# Measured 2026-09-13 across all three primitives: from 5e-324 up through
# 1e-15 L/min the difference from the zero-flow branch does not change at all,
# and here it does. Twelve orders below the smallest flow the model supports,
# so an epsilon anywhere a reader might reach for would freeze it.
FIRST_DIVERGING_FLOW_L_MIN = 1e-12


@dataclass(frozen=True, slots=True)
class CompartmentPrimitive:
    """One compartment closed form, and what it takes to exercise it.

    `build` takes the flow through the compartment and returns it loaded to
    `LOADED_FRACTION`, so that one table drives both the step-size test and
    the zero-flow walk.

    `step` returns the agent that step moved, in litres, as the compartment
    itself reports it: the signed change in store for the two patient
    compartments, the external exchange for the circuit. The two are different
    quantities and the same assertion - at zero flow each must be exactly
    zero, and the circuit's is what a `nan` exhaust would fail.
    """

    name: str
    build: Callable[[float], Any]
    step: Callable[[Any, float], float]
    stored_agent_l: Callable[[Any], float]
    time_constant_s: Callable[[Any], float]
    capacity_l: float
    nominal_flow_l_min: float

    @property
    def zero_flow_rounding_l(self) -> float:
        """How far the general path may land from the exact branch, in litres."""

        return self.capacity_l * ZERO_FLOW_ROUNDING_FRACTION


def _build_circuit(fresh_gas_flow_l_min: float) -> BreathingCircuit:
    return BreathingCircuit(
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=fresh_gas_flow_l_min,
        delivered_concentration_fraction=DRIVING_FRACTION,
        circuit_concentration_fraction=LOADED_FRACTION,
    )


def _step_circuit(circuit: BreathingCircuit, simulation_step_s: float) -> float:
    exchange = circuit.advance_fresh_gas(simulation_step_s)

    return exchange.delivered_agent_l + exchange.exhausted_agent_l


def _build_tissue(blood_flow_l_min: float) -> TissueGroup:
    tissue = TissueGroup(
        name="vessel_rich",
        volume_l=6.0,
        perfusion_fraction=0.76,
        blood_gas_partition_coefficient=0.65,
        tissue_gas_partition_coefficient=1.0,
        blood_flow_l_min=blood_flow_l_min,
    )
    tissue.set_partial_pressure_fraction(LOADED_FRACTION)

    return tissue


def _build_venous_blood(blood_flow_l_min: float) -> VenousBloodCompartment:
    venous_blood = VenousBloodCompartment(
        volume_l=1.222, blood_gas_partition_coefficient=0.65, blood_flow_l_min=blood_flow_l_min
    )
    venous_blood.set_concentration_fraction(LOADED_FRACTION)

    return venous_blood


PRIMITIVES = (
    CompartmentPrimitive(
        name="BreathingCircuit.advance_fresh_gas",
        build=_build_circuit,
        step=_step_circuit,
        stored_agent_l=lambda circuit: circuit.agent_amount_l,
        time_constant_s=lambda circuit: circuit.time_constant_s,
        capacity_l=6.0,
        nominal_flow_l_min=6.0,
    ),
    CompartmentPrimitive(
        name="TissueGroup.advance",
        build=_build_tissue,
        step=lambda tissue, step_s: tissue.advance(
            arterial_fraction=DRIVING_FRACTION, simulation_step_s=step_s
        ),
        stored_agent_l=lambda tissue: tissue.agent_amount_l,
        time_constant_s=lambda tissue: tissue.time_constant_s,
        capacity_l=6.0 * 1.0,
        nominal_flow_l_min=3.8,
    ),
    CompartmentPrimitive(
        name="VenousBloodCompartment.advance",
        build=_build_venous_blood,
        step=lambda venous_blood, step_s: venous_blood.advance(
            tissue_return_fraction=DRIVING_FRACTION, simulation_step_s=step_s
        ),
        stored_agent_l=lambda venous_blood: venous_blood.agent_amount_l,
        time_constant_s=lambda venous_blood: venous_blood.time_constant_s,
        capacity_l=1.222 * 0.65,
        nominal_flow_l_min=5.0,
    ),
)

_PRIMITIVE_CASES = pytest.mark.parametrize(
    "primitive", PRIMITIVES, ids=[primitive.name for primitive in PRIMITIVES]
)


@_PRIMITIVE_CASES
def test_the_closed_form_is_independent_of_step_size(primitive: CompartmentPrimitive) -> None:
    """Exactness at any step size is what separates a closed form from a split.

    A first-order sub-step would move here: `PatientCompartments.advance()`,
    the composition `PL-74R0` deleted, put its mixed venous fraction 25% apart
    across exactly this comparison.
    """

    one_step = primitive.build(primitive.nominal_flow_l_min)
    many_steps = primitive.build(primitive.nominal_flow_l_min)
    loaded_agent_l = primitive.stored_agent_l(one_step)

    primitive.step(one_step, COARSE_STEP_S)

    for _ in range(FINE_STEP_COUNT):
        primitive.step(many_steps, FINE_STEP_S)

    assert primitive.stored_agent_l(one_step) > loaded_agent_l
    assert primitive.stored_agent_l(many_steps) == pytest.approx(
        primitive.stored_agent_l(one_step), rel=1e-12
    )


@_PRIMITIVE_CASES
def test_zero_flow_is_an_exact_no_op(primitive: CompartmentPrimitive) -> None:
    """`docs/MODEL.md` states the no-flow case as an equality, so it is one.

    Exactly the loaded amount and exactly zero agent moved, not within a
    tolerance of either. Both assertions fail with the compartment's zero-flow
    branch removed, and they fail for different reasons: the circuit's
    exhausted-agent integral becomes `nan`, where the two patient compartments
    come back one unit in the last place away from where they started.
    """

    compartment = primitive.build(0.0)
    loaded_agent_l = primitive.stored_agent_l(compartment)

    agent_moved_l = primitive.step(compartment, COARSE_STEP_S)

    assert primitive.time_constant_s(compartment) == inf
    assert agent_moved_l == 0.0
    assert primitive.stored_agent_l(compartment) == loaded_agent_l


@_PRIMITIVE_CASES
def test_the_zero_flow_branch_agrees_with_the_limit_from_above(
    primitive: CompartmentPrimitive,
) -> None:
    """Why the guard is `== 0.0` and not a tolerance.

    Walked down to the smallest positive double, the general path lands the
    *same* distance from the branch at every magnitude - that distance being
    the one rounding of `d + (i - d)`, not flow moving agent. Nothing changes
    across 294 orders of magnitude, so there is no band of nearly-zero flows
    for an epsilon to catch, and one would create the discontinuity it looks
    like it is removing, by freezing flows the model says still move.

    Not asserted bit for bit, deliberately: it is at these loaded fractions
    that the rounding exists at all, and asserting equality here is what the
    item's own 2026-09-02 walk did - at a loaded fraction comparable to the
    driving one, where `d + (i - d)` happens to be exact and the question
    therefore never arose.
    """

    at_zero_flow = primitive.build(0.0)
    primitive.step(at_zero_flow, FINE_STEP_S)
    branch_agent_l = primitive.stored_agent_l(at_zero_flow)

    differences_l = set()

    for flow_l_min in NEARLY_ZERO_FLOWS_L_MIN:
        nearly_zero = primitive.build(flow_l_min)
        primitive.step(nearly_zero, FINE_STEP_S)
        difference_l = primitive.stored_agent_l(nearly_zero) - branch_agent_l

        assert abs(difference_l) <= primitive.zero_flow_rounding_l, (
            f"{primitive.name} leaves its zero-flow branch by more than one rounding "
            f"at {flow_l_min:g} L/min"
        )
        differences_l.add(difference_l)

    assert len(differences_l) == 1


@_PRIMITIVE_CASES
def test_a_real_flow_moves_more_agent_than_the_rounding_does(
    primitive: CompartmentPrimitive,
) -> None:
    """The other end of the walk above, which is what makes it a claim.

    Without this, a primitive frozen below some epsilon - or one that had
    stopped responding to flow entirely - would pass every other assertion in
    this module.
    """

    at_zero_flow = primitive.build(0.0)
    primitive.step(at_zero_flow, FINE_STEP_S)

    diverging = primitive.build(FIRST_DIVERGING_FLOW_L_MIN)
    primitive.step(diverging, FINE_STEP_S)
    difference_l = primitive.stored_agent_l(diverging) - primitive.stored_agent_l(at_zero_flow)

    assert abs(difference_l) > primitive.zero_flow_rounding_l
    assert abs(difference_l) < 1e-12
