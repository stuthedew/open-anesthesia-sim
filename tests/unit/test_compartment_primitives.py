"""The contract every compartment closed form in `core/` meets.

`core/__init__.py` states it. An `advance()` on a compartment is that
compartment's own closed form against a constant stated input, not how a run
advances, and it is exact at zero flow on its own, with the one `== 0.0`
branch in `time_constant_s` and none in the closed form. Both halves are
properties rather than claims, so they are held here across all three
primitives at once rather than once per compartment: what is being tested is
the rule, and a fourth primitive added to `core/` without joining
`PRIMITIVES` below is the omission this module exists to make visible
(`PL-74R0`, `PL-79YX`).

**Every constant here was chosen by watching the guard removed.** Before
`PL-79YX`, deleting either zero-flow branch in `TissueGroup.advance()` or
`VenousBloodCompartment.advance()` left the whole suite green, and so did the
first draft of this module: at a loaded fraction of 0.25 against a driving
fraction of 1.0 the unguarded path was bit exact, because `d + (i - d)` is
exact wherever `i` and `d` are within a factor of two of each other. It is the
*ordinary* case that was not - a compartment well below the fraction driving
it - which is why `LOADED_FRACTION` is small. The branches are gone since
`PL-XWFP`, because the two closed forms were rewritten anchored at the amount
each compartment holds for a step closing up to half the gap, zero flow among
them (`core/exponential_approach.py`); the same loaded fraction is what fails
the no-op test below if the form anchored at the driving fraction is ever
written back.
"""

import fractions
from collections.abc import Callable
from dataclasses import dataclass
from math import inf, isfinite, ulp
from typing import Any

import pytest

from anesthesia_sim.core.blood import VenousBloodCompartment
from anesthesia_sim.core.circuit import BreathingCircuit, FreshGasExchange
from anesthesia_sim.core.concentration import Fraction, Percent, fraction_from_percent
from anesthesia_sim.core.supported_ranges import FreshGasFlow
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.units import SECONDS_PER_MINUTE

# The fraction each compartment is loaded to, and the constant input each is
# driven with: a compartment at the very start of a wash-in.
#
# Small against the driving fraction rather than comparable to it, and that is
# load-bearing. `d + (i - d) * 1.0` is what a closed form anchored at the
# driving fraction reduces to at zero flow, and it returns `i` bit for bit
# only while the two are within a factor of two. At these values that form
# lands one rounding away instead, which is what makes the no-op test below
# able to fail if it is ever written back. Every closed form here reduces to
# `i + (d - i) * 0.0` instead - the circuit's since `PL-YT8N`, the patient
# compartments' since `PL-XWFP` - which is `i` at any values.
#
# Unequal for a second reason: a step that did nothing and a step that drove
# the compartment all the way to its input are the same measurement when the
# loaded and driving fractions agree.
#
# The driving input is written as a percent because the circuit's is its
# vaporizer dial, which is set in percent (`PL-NJPB`). The fraction the two
# patient compartments are driven with is derived from it, so all three are
# driven by the same number.
LOADED_FRACTION = Fraction(1e-6)
DRIVING_PERCENT = Percent(100.0)
DRIVING_FRACTION = fraction_from_percent(DRIVING_PERCENT)

# The one coarse step and the many fine ones a closed form must agree across.
COARSE_STEP_S = 60.0
FINE_STEP_S = 0.1
FINE_STEP_COUNT = 600

# Flows walked from zero upwards. The first is the smallest positive double
# there is, so if the exact branch and the general path ever disagree in a
# band above zero, this walk is inside it.
NEARLY_ZERO_FLOWS_L_MIN = (5e-324, 1e-300, 1e-30)

# Two flows the model admits at which the circuit's time constant,
# `60 * circuit_volume_l / flow`, overflows to `inf`: every flow below about
# 2e-306 L/min does, for a 6 L circuit (`PL-B26Y`). At the first the agent
# delivered rounds to zero, so the bound below holds the exhaust to exactly
# zero; the second, 2**-1023 L/min, still delivers a subnormal amount, so the
# bound is one a wrong exhaust could break by being too large.
OVERFLOWING_FLOWS_L_MIN = (5e-324, 1.1125369292536007e-308)

# The floor every comparison near zero flow sits on, as a fraction. A closed
# form anchored at the driving fraction reduces to `d + (i - d)` at zero flow,
# and that expression's rounding is set by the scale of the driving fraction
# rather than by the compartment's own - so it is relatively large for a
# compartment far below the input driving it, and it is the distance the two
# patient compartments landed from their zero-flow branches until `PL-XWFP`.
# No primitive lands any distance from its zero-flow result now, so for each
# this is a bound rather than the distance, and the real-flow test below is
# what keeps it a claim rather than a tolerance nothing reaches. In litres it
# is a compartment's capacity times this.
ZERO_FLOW_ROUNDING_FRACTION = ulp(DRIVING_FRACTION)

# The first decade at which every primitive's flow moves more agent over one
# fine step than that rounding could hide. Measured 2026-10-12 with all three
# closed forms anchored at what they hold: each first moves at all where its
# own gap term stops rounding to zero - the circuit from 3.8e-19 L/min and the
# tissue from 3.9e-19, the venous pool from 4.9e-20, so at 1e-18 and 1e-19 on
# this module's grid of one and three times each decade - and from there what
# moves grows in proportion to the flow, passing the rounding at 1e-12 L/min for the circuit
# (measured 2026-10-11), 3e-12 for the tissue and 3e-13 for the venous pool.
# Far below any flow a learner can set, so an epsilon anywhere a reader might
# reach for would freeze it.
FIRST_DIVERGING_FLOW_L_MIN = 1e-11

# The flows across which the circuit's exhaust came out below zero, by as
# much as 3.3e-16 L, while it was written as what was delivered less what the
# circuit kept: 1e-15 to 1e-6 L/min, walked here by decade (`PL-YT8N`).
CANCELLING_FLOWS_L_MIN = tuple(10.0**-exponent for exponent in range(15, 5, -1))

# The circuit states that walk is taken from. `washing-in` is the state the
# negative exhaust was found in. The two empty ones are what tell a fix by
# sign from a fix by digits: with `1 - exp(-dt/tau)` taken by `expm1`
# throughout and the exhaust still written as delivered less kept, a circuit
# filling from empty kept nearly all it was given and still exhausted
# -1.9e-34 L at 1e-15 L/min under a 100% dial and -3.9e-34 L at 1e-13 L/min
# under a 2% one, each over 0.1 s (measured 2026-10-11).
CIRCUIT_STATES = (
    pytest.param(DRIVING_PERCENT, LOADED_FRACTION, id="washing-in"),
    pytest.param(DRIVING_PERCENT, Fraction(0.0), id="empty"),
    pytest.param(Percent(2.0), Fraction(0.0), id="empty-at-2%"),
    pytest.param(Percent(0.0), Fraction(0.02), id="washing-out"),
)

# The walk `PL-XWFP` records: flows from 1e-30 to 3 L/min at one and three
# times each decade, three steps, and five states, each a driving fraction and
# the fraction the compartment holds. Written `d + (i - d) * exp(-dt/tau)` on
# the fraction, the tissue form reported a change of the sign opposite to its
# gradient in 100 of the walk's 930 cases and the venous form in 94, all at
# flows from 1e-30 to 3e-13 L/min, the largest -3.2e-18 L (measured
# 2026-10-11).
GRADIENT_FLOWS_L_MIN = tuple(
    mantissa * 10.0**-exponent for exponent in range(30, -1, -1) for mantissa in (1.0, 3.0)
)
GRADIENT_STATES = (
    pytest.param(DRIVING_FRACTION, LOADED_FRACTION, id="washing-in"),
    pytest.param(Fraction(0.02), Fraction(0.0), id="empty-at-2%"),
    pytest.param(Fraction(0.08), Fraction(1e-9), id="nearly-empty-at-8%"),
    pytest.param(Fraction(0.0), Fraction(0.02), id="washing-out"),
    pytest.param(LOADED_FRACTION, DRIVING_FRACTION, id="full-washing-out"),
)

# Amounts below both capacities above that the round trip through a fraction,
# `capacity * (amount / capacity)`, returns one ulp away - through the 6.0 L
# tissue capacity and the 0.7943 L venous one alike (found 2026-10-12). No
# `set_partial_pressure_fraction` stores them, since it stores that product; a
# test or a notebook writing the amount does (`PL-19Y0`), and a closed form
# written on the fraction and re-formed would move each of them at any flow,
# zero included, in whichever direction the rounding fell.
ROUND_TRIP_MOVED_AMOUNTS_L = (
    0.40250137443750783,
    0.437154095683643,
    0.3998343256124454,
    0.42401107649955255,
)


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
        max_delivered_concentration_percent=Percent(100.0),
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=FreshGasFlow(fresh_gas_flow_l_min),
        delivered_concentration_percent=DRIVING_PERCENT,
        inspired_partial_pressure_fraction=LOADED_FRACTION,
    )


def _step_circuit(circuit: BreathingCircuit, simulation_step_s: float) -> float:
    exchange = circuit.advance_fresh_gas(simulation_step_s)

    return exchange.delivered_agent_l + exchange.exhausted_agent_l


@dataclass(frozen=True, slots=True)
class _Perfused[CompartmentT: (TissueGroup, VenousBloodCompartment)]:
    """A patient compartment and the blood flow its closed form is read at.

    Neither patient compartment stores a flow since `PL-HQF5`, so the flow a
    case walks is carried beside the compartment and passed to each call.
    """

    compartment: CompartmentT
    blood_flow_l_min: float


def _build_tissue(blood_flow_l_min: float) -> _Perfused[TissueGroup]:
    tissue = TissueGroup(
        name="vessel_rich",
        volume_l=6.0,
        perfusion_fraction=0.76,
        blood_gas_partition_coefficient=0.65,
        tissue_gas_partition_coefficient=1.0,
    )
    tissue.set_partial_pressure_fraction(LOADED_FRACTION)

    return _Perfused(tissue, blood_flow_l_min)


def _build_venous_blood(blood_flow_l_min: float) -> _Perfused[VenousBloodCompartment]:
    venous_blood = VenousBloodCompartment(volume_l=1.222, blood_gas_partition_coefficient=0.65)
    venous_blood.set_partial_pressure_fraction(LOADED_FRACTION)

    return _Perfused(venous_blood, blood_flow_l_min)


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
        step=lambda tissue, step_s: tissue.compartment.advance(
            arterial_partial_pressure_fraction=DRIVING_FRACTION,
            simulation_step_s=step_s,
            blood_flow_l_min=tissue.blood_flow_l_min,
        ),
        stored_agent_l=lambda tissue: tissue.compartment.agent_amount_l,
        time_constant_s=lambda tissue: tissue.compartment.time_constant_s(tissue.blood_flow_l_min),
        capacity_l=6.0 * 1.0,
        nominal_flow_l_min=3.8,
    ),
    CompartmentPrimitive(
        name="VenousBloodCompartment.advance",
        build=_build_venous_blood,
        step=lambda venous_blood, step_s: venous_blood.compartment.advance(
            tissue_return_partial_pressure_fraction=DRIVING_FRACTION,
            simulation_step_s=step_s,
            blood_flow_l_min=venous_blood.blood_flow_l_min,
        ),
        stored_agent_l=lambda venous_blood: venous_blood.compartment.agent_amount_l,
        time_constant_s=lambda venous_blood: venous_blood.compartment.time_constant_s(
            venous_blood.blood_flow_l_min
        ),
        capacity_l=1.222 * 0.65,
        nominal_flow_l_min=5.0,
    ),
)

_PRIMITIVE_CASES = pytest.mark.parametrize(
    "primitive", PRIMITIVES, ids=[primitive.name for primitive in PRIMITIVES]
)


@dataclass(frozen=True, slots=True)
class PatientPrimitive:
    """One patient compartment closed form, driven from a chosen state.

    `build` takes the flow and the fraction the compartment holds; `step`
    takes the compartment, the driving fraction and the step, and returns the
    change the compartment reports. `PRIMITIVES` fixes both fractions, because
    its walks compare one state across the three primitives; the gradient
    walk below takes five states across the two that store an amount.
    """

    name: str
    build: Callable[[float, Fraction], Any]
    step: Callable[[Any, Fraction, float], float]
    stored_agent_l: Callable[[Any], float]
    capacity_l: Callable[[Any], float]


def _tissue_holding(blood_flow_l_min: float, held_fraction: Fraction) -> _Perfused[TissueGroup]:
    tissue = _build_tissue(blood_flow_l_min)
    tissue.compartment.set_partial_pressure_fraction(held_fraction)

    return tissue


def _venous_blood_holding(
    blood_flow_l_min: float, held_fraction: Fraction
) -> _Perfused[VenousBloodCompartment]:
    venous_blood = _build_venous_blood(blood_flow_l_min)
    venous_blood.compartment.set_partial_pressure_fraction(held_fraction)

    return venous_blood


PATIENT_PRIMITIVES = (
    PatientPrimitive(
        name="TissueGroup.advance",
        build=_tissue_holding,
        step=lambda tissue, driving_fraction, step_s: tissue.compartment.advance(
            arterial_partial_pressure_fraction=driving_fraction,
            simulation_step_s=step_s,
            blood_flow_l_min=tissue.blood_flow_l_min,
        ),
        stored_agent_l=lambda tissue: tissue.compartment.agent_amount_l,
        capacity_l=lambda tissue: tissue.compartment.capacity_l,
    ),
    PatientPrimitive(
        name="VenousBloodCompartment.advance",
        build=_venous_blood_holding,
        step=lambda venous_blood, driving_fraction, step_s: venous_blood.compartment.advance(
            tissue_return_partial_pressure_fraction=driving_fraction,
            simulation_step_s=step_s,
            blood_flow_l_min=venous_blood.blood_flow_l_min,
        ),
        stored_agent_l=lambda venous_blood: venous_blood.compartment.agent_amount_l,
        capacity_l=lambda venous_blood: venous_blood.compartment.capacity_l,
    ),
)

_PATIENT_CASES = pytest.mark.parametrize(
    "primitive", PATIENT_PRIMITIVES, ids=[primitive.name for primitive in PATIENT_PRIMITIVES]
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
    tolerance of either. No closed form has a zero-flow branch: each is exact
    at zero flow on its own, the circuit's since `PL-YT8N` and the patient
    compartments' since `PL-XWFP`, because each is anchored at what the
    compartment holds and its gap term is a product with `expm1` of zero.
    Written anchored at the driving fraction, `d + (i - d) * exp(-dt/tau)`,
    each fails here, one rounding of `d + (i - d)` from where it started: the
    circuit held 6.000000000172534e-06 L where it held 6e-06 (measured
    2026-10-05), and a 6 L tissue group the same 6.000000000172534e-06 L
    (measured 2026-10-12), which is what their branches bought until the form
    changed.
    Before `PL-B26Y` the circuit's exhausted-agent integral became `nan`.
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
    """Why the one guard left is `== 0.0` and not a tolerance.

    Walked down to the smallest positive double, each closed form lands
    exactly where its zero-flow result does: the flows are real, and the
    agent they move over 0.1 s is below the resolution of what the
    compartment holds, so the amount is unchanged rather than nearly so.
    Nothing changes across 294 orders of magnitude, so there is no band of
    nearly-zero flows for an epsilon to catch, and one would create the
    discontinuity it looks like it is removing, by freezing flows the model
    says still move.

    The one-rounding bound stays beside the equality as the distance the form
    anchored at the driving fraction landed at, which the two patient
    compartments' branches held them to until `PL-XWFP`. It is at these
    loaded fractions that its rounding existed at all; asserting equality
    alone is what the item's own 2026-09-02 walk did, at a loaded fraction
    comparable to the driving one, where `d + (i - d)` happens to be exact
    and the question never arose.

    The agent each step reports moving is held to the same rounding, the
    circuit's external exchange included: the patient compartments report
    exactly none, and the circuit the agent such a flow delivers and
    exhausts. Until `PL-B26Y` the walk compared only what each compartment
    stored and discarded what the step returned, so the circuit's `nan`
    exhaust at the smallest of these flows passed it.
    """

    at_zero_flow = primitive.build(0.0)
    primitive.step(at_zero_flow, FINE_STEP_S)
    branch_agent_l = primitive.stored_agent_l(at_zero_flow)

    differences_l = set()

    for flow_l_min in NEARLY_ZERO_FLOWS_L_MIN:
        nearly_zero = primitive.build(flow_l_min)
        agent_moved_l = primitive.step(nearly_zero, FINE_STEP_S)
        difference_l = primitive.stored_agent_l(nearly_zero) - branch_agent_l

        assert abs(difference_l) <= primitive.zero_flow_rounding_l, (
            f"{primitive.name} leaves its zero-flow branch by more than one rounding "
            f"at {flow_l_min:g} L/min"
        )
        assert abs(agent_moved_l) <= primitive.zero_flow_rounding_l, (
            f"{primitive.name} reports {agent_moved_l!r} L moved at {flow_l_min:g} L/min, "
            "where its zero-flow branch reports none"
        )
        assert difference_l == 0.0, (
            f"{primitive.name} lands {difference_l!r} L from its zero-flow result "
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


@pytest.mark.parametrize("fresh_gas_flow_l_min", OVERFLOWING_FLOWS_L_MIN)
@pytest.mark.parametrize(
    "inspired_partial_pressure_fraction",
    (LOADED_FRACTION, DRIVING_FRACTION),
    ids=("washing-in", "at-the-dial"),
)
def test_the_circuit_exhaust_is_finite_where_its_time_constant_overflows(
    fresh_gas_flow_l_min: float, inspired_partial_pressure_fraction: Fraction
) -> None:
    """A flow the model admits gets an exhaust, not a `nan` (`PL-B26Y`).

    The exhaust is the flow times the inspired fraction integrated over the
    step, and the inspired fraction stays between where it started and the
    dial, so the exhaust lies between zero and the flow times the step times
    the larger of the two. The closed form used to carry the time constant as
    a factor, `tau * (1 - exp(-dt/tau))`, which at these flows is
    `inf * 0.0`, and the exhaust came back `nan` from either state. It forms
    no time constant at all since `PL-YT8N`.
    """

    circuit = _build_circuit(fresh_gas_flow_l_min)
    circuit.set_inspired_partial_pressure_fraction(inspired_partial_pressure_fraction)
    larger_fraction = max(inspired_partial_pressure_fraction, DRIVING_FRACTION)
    # Associated as the closed form associates the agent it delivers, so the
    # bound is exact rather than one rounding either side of what it bounds.
    exhaust_bound_l = larger_fraction * (fresh_gas_flow_l_min / SECONDS_PER_MINUTE * FINE_STEP_S)

    exchange = circuit.advance_fresh_gas(FINE_STEP_S)

    assert circuit.time_constant_s == inf
    assert isfinite(exchange.exhausted_agent_l)
    assert 0.0 <= exchange.exhausted_agent_l <= exhaust_bound_l


def _advance_circuit_in_state(
    fresh_gas_flow_l_min: float,
    delivered_concentration_percent: Percent,
    inspired_partial_pressure_fraction: Fraction,
    simulation_step_s: float,
) -> tuple[BreathingCircuit, Fraction, FreshGasExchange]:
    """Step a 6 L circuit once from a state; return it, its starting fraction and the exchange."""

    circuit = _build_circuit(fresh_gas_flow_l_min)
    circuit.set_delivered_concentration_percent(delivered_concentration_percent)
    circuit.set_inspired_partial_pressure_fraction(inspired_partial_pressure_fraction)

    return circuit, inspired_partial_pressure_fraction, circuit.advance_fresh_gas(simulation_step_s)


@pytest.mark.parametrize("fresh_gas_flow_l_min", CANCELLING_FLOWS_L_MIN)
@pytest.mark.parametrize("simulation_step_s", (FINE_STEP_S, 1.0, COARSE_STEP_S))
@pytest.mark.parametrize(
    ("delivered_concentration_percent", "inspired_partial_pressure_fraction"), CIRCUIT_STATES
)
def test_the_circuit_exhaust_is_never_negative_at_an_admitted_flow(
    fresh_gas_flow_l_min: float,
    simulation_step_s: float,
    delivered_concentration_percent: Percent,
    inspired_partial_pressure_fraction: Fraction,
) -> None:
    """An exhaust is agent leaving the circuit, so it is never negative (`PL-YT8N`).

    Written as what was delivered less what the circuit kept, it was the
    difference of two amounts agreeing to more digits than a double holds
    wherever the circuit kept nearly all it was given, and it took the
    rounding's sign: -3.3e-16 L at 1e-12 L/min over 0.1 s in the `washing-in`
    state, beside 1.7e-15 L delivered. Built from terms that are each
    nonnegative, it cannot.
    """

    _, _, exchange = _advance_circuit_in_state(
        fresh_gas_flow_l_min,
        delivered_concentration_percent,
        inspired_partial_pressure_fraction,
        simulation_step_s,
    )

    assert exchange.exhausted_agent_l >= 0.0


def _has_the_sign_of(change_l: float, gradient: float) -> bool:
    """Whether a change has the gradient's sign or is zero; a zero gradient admits only zero."""

    if gradient > 0.0:
        return change_l >= 0.0

    if gradient < 0.0:
        return change_l <= 0.0

    return change_l == 0.0


@_PATIENT_CASES
@pytest.mark.parametrize("simulation_step_s", (FINE_STEP_S, 1.0, COARSE_STEP_S))
@pytest.mark.parametrize(("driving_fraction", "held_fraction"), GRADIENT_STATES)
def test_a_compartment_never_reports_uptake_as_a_return_at_an_admitted_flow(
    primitive: PatientPrimitive,
    driving_fraction: Fraction,
    held_fraction: Fraction,
    simulation_step_s: float,
) -> None:
    """A change has the gradient's sign or is zero, and the amount never crosses its equilibrium.

    The patient compartments' counterpart of the circuit test above
    (`PL-XWFP`). Written `d + (i - d) * exp(-dt/tau)` on the fraction, each
    closed form rounded at the scale of the driving fraction, and where
    `dt/tau` was small the amount could land below where it started while the
    input was above it: uptake reported as a return, in 100 and 94 of the
    walk's 930 cases, all at flows from 1e-30 to 3e-13 L/min. Anchored at the
    amount held, with the gap term taken by `expm1`, the result is the start
    plus a term of the gradient's sign for a step closing up to half the gap,
    and the equilibrium plus a term of the opposite sign beyond it
    (`core/exponential_approach.py`). The amount is held to the interval
    between its start and its equilibrium as well, which either form keeps
    with nothing clamped: a full approach that landed an ulp past the
    capacity would be a write the tissue refuses, and it lands on the
    capacity instead.
    """

    for flow_l_min in GRADIENT_FLOWS_L_MIN:
        compartment = primitive.build(flow_l_min, held_fraction)
        held_agent_l = primitive.stored_agent_l(compartment)
        equilibrium_agent_l = primitive.capacity_l(compartment) * driving_fraction

        agent_moved_l = primitive.step(compartment, driving_fraction, simulation_step_s)
        stored_agent_l = primitive.stored_agent_l(compartment)

        assert _has_the_sign_of(agent_moved_l, driving_fraction - held_fraction), (
            f"{primitive.name} reports {agent_moved_l!r} L moved at {flow_l_min:g} L/min "
            f"over {simulation_step_s:g} s, driven from {held_fraction} by {driving_fraction}"
        )
        assert agent_moved_l == stored_agent_l - held_agent_l
        assert (
            min(held_agent_l, equilibrium_agent_l)
            <= stored_agent_l
            <= max(held_agent_l, equilibrium_agent_l)
        ), (
            f"{primitive.name} holds {stored_agent_l!r} L at {flow_l_min:g} L/min, outside "
            f"its start {held_agent_l!r} L and its equilibrium {equilibrium_agent_l!r} L"
        )


@_PATIENT_CASES
@pytest.mark.parametrize("simulation_step_s", (FINE_STEP_S, 1.0, COARSE_STEP_S))
@pytest.mark.parametrize(
    "driving_fraction", (DRIVING_FRACTION, Fraction(0.0)), ids=("filling", "washing-out")
)
@pytest.mark.parametrize("held_amount_l", ROUND_TRIP_MOVED_AMOUNTS_L)
def test_a_compartment_holding_a_written_amount_never_reports_uptake_as_a_return(
    primitive: PatientPrimitive,
    held_amount_l: float,
    driving_fraction: Fraction,
    simulation_step_s: float,
) -> None:
    """The amount is what is anchored, so an amount no fraction reproduces is advanced from itself.

    The walk above loads each compartment through its fraction, so every
    amount it holds is one the round trip returns. These are written, as a
    test or a notebook writes them, and the round trip returns each one ulp
    away: formed on the fraction and re-formed as `capacity * fraction`, a
    closed form would report that ulp as agent moved at zero flow, of
    whichever sign the rounding gave it. Formed on the amount, the change is
    exactly zero at zero flow, has the gradient's sign or is zero at every
    other, and leaves the amount between what was held and the equilibrium
    (`core/exponential_approach.py`).
    """

    for flow_l_min in (0.0, *GRADIENT_FLOWS_L_MIN):
        compartment = primitive.build(flow_l_min, LOADED_FRACTION)
        compartment.compartment.agent_amount_l = held_amount_l
        capacity_l = primitive.capacity_l(compartment)
        equilibrium_agent_l = capacity_l * driving_fraction

        assert capacity_l * (held_amount_l / capacity_l) != held_amount_l

        agent_moved_l = primitive.step(compartment, driving_fraction, simulation_step_s)
        stored_agent_l = primitive.stored_agent_l(compartment)

        if flow_l_min == 0.0:
            assert agent_moved_l == 0.0
        assert _has_the_sign_of(agent_moved_l, equilibrium_agent_l - held_amount_l), (
            f"{primitive.name} reports {agent_moved_l!r} L moved at {flow_l_min:g} L/min "
            f"over {simulation_step_s:g} s, holding {held_amount_l!r} L driven by "
            f"{driving_fraction}"
        )
        assert agent_moved_l == stored_agent_l - held_amount_l
        assert (
            min(held_amount_l, equilibrium_agent_l)
            <= stored_agent_l
            <= max(held_amount_l, equilibrium_agent_l)
        ), (
            f"{primitive.name} holds {stored_agent_l!r} L at {flow_l_min:g} L/min, outside "
            f"the {held_amount_l!r} L written and its equilibrium {equilibrium_agent_l!r} L"
        )


@pytest.mark.parametrize("fresh_gas_flow_l_min", CANCELLING_FLOWS_L_MIN)
@pytest.mark.parametrize("simulation_step_s", (FINE_STEP_S, 1.0, COARSE_STEP_S))
@pytest.mark.parametrize(
    ("delivered_concentration_percent", "inspired_partial_pressure_fraction"), CIRCUIT_STATES
)
def test_the_circuit_balance_closes_within_the_rounding_of_what_the_step_moves(
    fresh_gas_flow_l_min: float,
    simulation_step_s: float,
    delivered_concentration_percent: Percent,
    inspired_partial_pressure_fraction: Fraction,
) -> None:
    """What was delivered less what was exhausted is what the circuit gained.

    The half of `PL-YT8N` a fix of the sign alone could lose. Measured in
    exact rationals, so the measurement rounds nothing, against four roundings
    of the largest amount the step involves - delivered, exhausted or held -
    which every case here closes within. `-expm1(-dt/tau)` in the exhaust
    alone, with the fraction still updated by `exp(-dt/tau)`, misses it by up
    to 5.1e-16 L in the `washing-in` state, where the circuit holds 6e-6 L:
    six hundred thousand of those roundings (measured 2026-10-11).
    """

    circuit, held_fraction_before, exchange = _advance_circuit_in_state(
        fresh_gas_flow_l_min,
        delivered_concentration_percent,
        inspired_partial_pressure_fraction,
        simulation_step_s,
    )
    held_fraction_after = circuit.inspired_partial_pressure_fraction

    residual_l = abs(
        fractions.Fraction(exchange.delivered_agent_l)
        - fractions.Fraction(exchange.exhausted_agent_l)
        - fractions.Fraction(circuit.circuit_volume_l)
        * (fractions.Fraction(held_fraction_after) - fractions.Fraction(held_fraction_before))
    )
    largest_amount_l = max(
        exchange.delivered_agent_l,
        exchange.exhausted_agent_l,
        circuit.circuit_volume_l * max(held_fraction_before, held_fraction_after),
    )

    assert residual_l <= 4 * ulp(largest_amount_l)
