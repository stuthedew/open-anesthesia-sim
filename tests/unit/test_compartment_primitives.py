"""The contract that every compartment closed form in `core/` meets.

`core/__init__.py` states the contract. Calling `advance()` on a compartment
applies that compartment's own closed form for a constant stated input. It is
not how a run advances. The closed form is also exact at zero flow on its own:
the one `== 0.0` branch is in `time_constant_s`, and there is none in the
closed form. Both halves are properties rather than claims, so this module
tests them across all three primitives at once rather than once per
compartment. What is being tested is the rule. A fourth primitive added to
`core/` without joining `PRIMITIVES` below is the omission that this module
exists to make visible (`PL-74R0`, `PL-79YX`).

**Every constant here was chosen by watching the tests with the guard
removed.** Before `PL-79YX`, deleting either zero-flow branch in
`TissueGroup.advance()` or `VenousBloodCompartment.advance()` left the whole
suite green. So did the first draft of this module. At a loaded fraction of
0.25 against a driving fraction of 1.0, the unguarded path was bit exact,
because `d + (i - d)` is exact wherever `i` and `d` are within a factor of two
of each other. The *ordinary* case was not exact: a compartment well below the
fraction that drives it. That is why `LOADED_FRACTION` is small. The branches
have been gone since `PL-XWFP`. The two closed forms were rewritten so that,
for a step that closes up to half the gap, each is anchored at the amount the
compartment holds. Zero flow is among those steps
(`core/exponential_approach.py`). If the form anchored at the driving fraction
is ever written back, the same loaded fraction is what makes the no-op test
below fail.
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

# The fraction that each compartment is loaded to, and the constant input that
# drives each one. Together they describe a compartment at the very start of a
# wash-in.
#
# The loaded fraction is small compared with the driving fraction, not
# comparable to it, and that choice matters. `d + (i - d) * 1.0` is what a
# closed form anchored at the driving fraction reduces to at zero flow. It
# returns `i` bit for bit only while the two are within a factor of two. At
# these values that form lands one rounding away instead, so the no-op test
# below can fail if the form is ever written back. Every closed form here
# reduces to `i + (d - i) * 0.0` instead, which is `i` at any values. The
# circuit's form has done so since `PL-YT8N`, and the patient compartments'
# forms since `PL-XWFP`.
#
# The two fractions are unequal for a second reason. When the loaded and
# driving fractions agree, a step that did nothing and a step that drove the
# compartment all the way to its input give the same measurement.
#
# The driving input is written as a percent because the circuit's input is its
# vaporizer dial, which is set in percent (`PL-NJPB`). The fraction that drives
# the two patient compartments is derived from it, so the same number drives
# all three.
LOADED_FRACTION = Fraction(1e-6)
DRIVING_PERCENT = Percent(100.0)
DRIVING_FRACTION = fraction_from_percent(DRIVING_PERCENT)

# A closed form must give the same result over one coarse step as over many fine ones.
COARSE_STEP_S = 60.0
FINE_STEP_S = 0.1
FINE_STEP_COUNT = 600

# Flows walked upwards from zero. The first is the smallest positive double, so
# if the exact branch and the general path ever disagree in a band above zero,
# this walk falls inside that band.
NEARLY_ZERO_FLOWS_L_MIN = (5e-324, 1e-300, 1e-30)

# Two flows that the model accepts and at which the circuit's time constant,
# `60 * circuit_volume_l / flow`, overflows to `inf`. For a 6 L circuit, every
# flow below about 2e-306 L/min overflows (`PL-B26Y`). At the first flow, the
# agent delivered rounds to zero, so the bound below limits the exhaust to
# exactly zero. The second flow, 2**-1023 L/min, still delivers a subnormal
# amount, so a wrong exhaust could break the bound by being too large.
OVERFLOWING_FLOWS_L_MIN = (5e-324, 1.1125369292536007e-308)

# The rounding bound, as a fraction, that every comparison near zero flow uses.
# A closed form anchored at the driving fraction reduces to `d + (i - d)` at
# zero flow. The rounding of that expression is set by the scale of the
# driving fraction, not by the compartment's own scale. So the rounding is
# relatively large for a compartment far below the input that drives it. Until
# `PL-XWFP`, this rounding was the distance by which the two patient
# compartments landed from their zero-flow branches. No primitive now lands any distance from its
# zero-flow result, so for each primitive this value is a bound rather than the
# actual distance. The real-flow test below shows that a real flow exceeds the
# bound, so the bound is a real claim and not a tolerance that no result comes
# near. In litres, the bound is a compartment's capacity times this fraction.
ZERO_FLOW_ROUNDING_FRACTION = ulp(DRIVING_FRACTION)

# The first decade at which every primitive's flow moves more agent over one
# fine step than that rounding could hide. This was measured on 2026-10-12,
# with all three closed forms anchored at what they hold. Each primitive first
# moves any agent at all where its own gap term stops rounding to zero. The
# circuit starts moving at 3.8e-19 L/min, the tissue at 3.9e-19 and the venous
# pool at 4.9e-20. On this module's grid of one and three times each decade,
# that is at 1e-18 and 1e-19. From there, the amount moved grows in proportion
# to the flow. It passes the rounding at 1e-12 L/min for the circuit (measured
# 2026-10-11), 3e-12 for the tissue and 3e-13 for the venous pool. These flows
# are far below any flow a learner can set, so an epsilon at any value a reader
# might choose would freeze them.
FIRST_DIVERGING_FLOW_L_MIN = 1e-11

# The flows at which the circuit's exhaust came out below zero, by as much as
# 3.3e-16 L, while the exhaust was written as what was delivered less what the
# circuit kept. They run from 1e-15 to 1e-6 L/min, walked here by decade
# (`PL-YT8N`).
CANCELLING_FLOWS_L_MIN = tuple(10.0**-exponent for exponent in range(15, 5, -1))

# The circuit states that the walk starts from. `washing-in` is the state in
# which the negative exhaust was found. The two empty states tell a fix that
# makes the sign right by construction apart from a fix that only adds
# precision. One version computed `1 - exp(-dt/tau)` with `expm1` throughout
# but still wrote the exhaust as delivered less kept. In that version, a
# circuit filling from empty kept nearly all it was given and still exhausted
# -1.9e-34 L at 1e-15 L/min under a 100% dial, and -3.9e-34 L at 1e-13 L/min
# under a 2% dial, each over 0.1 s (measured 2026-10-11).
CIRCUIT_STATES = (
    pytest.param(DRIVING_PERCENT, LOADED_FRACTION, id="washing-in"),
    pytest.param(DRIVING_PERCENT, Fraction(0.0), id="empty"),
    pytest.param(Percent(2.0), Fraction(0.0), id="empty-at-2%"),
    pytest.param(Percent(0.0), Fraction(0.02), id="washing-out"),
)

# The walk that `PL-XWFP` records. It covers flows from 1e-30 to 3 L/min at one
# and three times each decade, three steps, and five states. Each state is a
# driving fraction and the fraction the compartment holds. When each form was
# written `d + (i - d) * exp(-dt/tau)` on the fraction, the tissue form
# reported a change with the sign opposite to its gradient in 100 of the walk's
# 930 cases, and the venous form did so in 94. All of those cases were at flows
# from 1e-30 to 3e-13 L/min, and the largest change was -3.2e-18 L (measured
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

# Amounts, less than both capacities above, that the round trip through a
# fraction, `capacity * (amount / capacity)`, returns one ulp away. This holds
# through the 6.0 L tissue capacity and the 0.7943 L venous capacity alike
# (found 2026-10-12). No call to `set_partial_pressure_fraction` stores these
# amounts, because it stores that product. A test or a notebook that writes the
# amount directly does store them (`PL-19Y0`). A closed form written on the
# fraction and then converted back to an amount would move each of them at any
# flow, zero included, in whichever direction the rounding fell.
ROUND_TRIP_MOVED_AMOUNTS_L = (
    0.40250137443750783,
    0.437154095683643,
    0.3998343256124454,
    0.42401107649955255,
)


@dataclass(frozen=True, slots=True)
class CompartmentPrimitive:
    """One compartment closed form, and what it takes to exercise it.

    `build` takes the flow through the compartment and returns the compartment
    loaded to `LOADED_FRACTION`, so that one table drives both the step-size
    test and the zero-flow walk.

    `step` returns the agent that the step moved, in litres, as the
    compartment itself reports it. For the two patient compartments, that is
    the signed change in the amount stored. For the circuit, it is the
    external exchange. The two are different quantities, but the same
    assertion applies to both: at zero flow, each must be exactly zero. A
    `nan` exhaust would fail that assertion on the circuit's quantity.
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
    """A patient compartment, and the blood flow at which its closed form is evaluated.

    Neither patient compartment has stored a flow since `PL-HQF5`, so the flow
    that a case walks is carried beside the compartment and passed to each
    call.
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

    `build` takes the flow and the fraction the compartment holds. `step`
    takes the compartment, the driving fraction and the step, and returns the
    change that the compartment reports. `PRIMITIVES` fixes both fractions,
    because its walks compare one state across the three primitives. The
    gradient walk below instead takes five states across the two primitives
    that store an amount.
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

    A first-order sub-step would give a different result here.
    `PatientCompartments.advance()`, the composition that `PL-74R0` deleted,
    put its mixed venous fraction 25% apart across exactly this comparison.
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
    """`docs/MODEL.md` states the no-flow case as an equality, so the test asserts equality.

    The compartment must hold exactly the loaded amount and report exactly
    zero agent moved, not a value within a tolerance of either. No closed form
    has a zero-flow branch. Each is exact at zero flow on its own: the
    circuit's since `PL-YT8N`, and the patient compartments' since `PL-XWFP`.
    Each is exact because it is anchored at what the compartment holds, and
    its gap term is a product with `expm1` of zero. If each form is written
    anchored at the driving fraction, as `d + (i - d) * exp(-dt/tau)`, it
    fails here, one rounding of `d + (i - d)` from where it started. The
    circuit held 6.000000000172534e-06 L where it had held 6e-06 (measured
    2026-10-05). A 6 L tissue group held the same 6.000000000172534e-06 L
    (measured 2026-10-12). Their zero-flow branches prevented that error until
    the form changed.
    Before `PL-B26Y`, the circuit's exhausted-agent integral became `nan`.
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
    """Show why the one remaining guard is `== 0.0` and not a tolerance.

    As the flow is walked down to the smallest positive double, each closed
    form lands exactly on its zero-flow result. The flows are real, but the
    agent they move over 0.1 s is below the resolution of the amount the
    compartment holds. The amount is therefore unchanged, not merely nearly
    unchanged. Nothing changes across 294 orders of magnitude, so there is no
    band of nearly-zero flows for an epsilon to catch. An epsilon would
    instead create the discontinuity it appears to remove, by freezing flows
    that the model says still move.

    The one-rounding bound stays beside the equality. It is the distance at
    which the form anchored at the driving fraction landed. Until `PL-XWFP`,
    the two patient compartments landed that distance from the results of
    their zero-flow branches. That rounding occurs at all only at loaded
    fractions like these. Asserting
    equality alone is what the item's own 2026-09-02 walk did. That walk used
    a loaded fraction comparable to the driving one, where `d + (i - d)`
    happens to be exact, so the question never arose.

    The agent that each step reports moving is checked against the same
    rounding bound, including the circuit's external exchange. The patient
    compartments report exactly none. The circuit reports the agent that such
    a flow delivers and exhausts. Until `PL-B26Y`, the walk compared only what
    each compartment stored and discarded what the step returned, so the
    circuit's `nan` exhaust at the smallest of these flows passed the walk.
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
    """A real flow moves more agent than the rounding bound, so the walk above is not vacuous.

    Without this test, a primitive frozen below some epsilon, or one that had
    stopped responding to flow entirely, would pass every other assertion in
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
    """A flow that the model accepts gets a finite exhaust, not a `nan` (`PL-B26Y`).

    The exhaust is the flow times the inspired fraction, integrated over the
    step. The inspired fraction stays between its starting value and the dial,
    so the exhaust lies between zero and the flow times the step times the
    larger of the two. The closed form used to carry the time constant as a
    factor, `tau * (1 - exp(-dt/tau))`. At these flows that factor is
    `inf * 0.0`, so the exhaust came back `nan` from either state. Since
    `PL-YT8N`, the closed form computes no time constant at all.
    """

    circuit = _build_circuit(fresh_gas_flow_l_min)
    circuit.set_inspired_partial_pressure_fraction(inspired_partial_pressure_fraction)
    larger_fraction = max(inspired_partial_pressure_fraction, DRIVING_FRACTION)
    # The product is grouped the same way the closed form groups the agent it
    # delivers, so the bound is exact rather than one rounding away, on either
    # side, from what it bounds.
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
    """Step a 6 L circuit once from a state, and return it, its start fraction and the exchange."""

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

    When the exhaust was written as what was delivered less what the circuit
    kept, it was the difference of two amounts. Wherever the circuit kept
    nearly all it was given, those amounts agreed to more digits than a double
    holds, so the difference took the sign of the rounding. One case was
    -3.3e-16 L at 1e-12 L/min over 0.1 s in the `washing-in` state, beside
    1.7e-15 L delivered. Built from terms that are each nonnegative, the
    exhaust cannot be negative.
    """

    _, _, exchange = _advance_circuit_in_state(
        fresh_gas_flow_l_min,
        delivered_concentration_percent,
        inspired_partial_pressure_fraction,
        simulation_step_s,
    )

    assert exchange.exhausted_agent_l >= 0.0


def _has_the_sign_of(change_l: float, gradient: float) -> bool:
    """Return whether a change has the gradient's sign or is zero.

    A zero gradient allows only a zero change.
    """

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

    This is the patient compartments' counterpart of the circuit test above
    (`PL-XWFP`). When each closed form was written `d + (i - d) * exp(-dt/tau)`
    on the fraction, it rounded at the scale of the driving fraction. Where
    `dt/tau` was small, the amount could land below where it started while the
    input was above it. That reported uptake as a return, in 100 and 94 of the
    walk's 930 cases, all at flows from 1e-30 to 3e-13 L/min. Anchored at the
    amount held, with the gap term computed by `expm1`, the result is the
    start plus a term of the gradient's sign, for a step that closes up to
    half the gap. Beyond half the gap, it is the equilibrium plus a term of the
    opposite sign (`core/exponential_approach.py`). The test also requires the
    amount to stay in the interval between its start and its equilibrium,
    which each of the two forms keeps without any clamping. A full approach that landed
    an ulp past the capacity would be a write that the tissue refuses, and the
    amount lands on the capacity instead.
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
    amount it holds is one that the round trip returns unchanged. These
    amounts are written directly, as a test or a notebook writes them, and the
    round trip returns each one ulp away. A closed form computed on the
    fraction and converted back as `capacity * fraction` would report that ulp
    as agent moved at zero flow, with whichever sign the rounding gave it.
    Computed on the amount, the change is exactly zero at zero flow, and has
    the gradient's sign or is zero at every other flow. It also leaves the
    amount between what was held and the equilibrium
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

    This is the half of `PL-YT8N` that a fix of the sign alone could lose. The
    balance is measured in exact rationals, so the measurement itself rounds
    nothing. It is compared against four roundings of the largest amount that
    the step involves: delivered, exhausted or held. Every case here closes
    within that bound. Using `-expm1(-dt/tau)` in the exhaust alone, while the
    fraction is still updated by `exp(-dt/tau)`, leaves an error of up to
    5.1e-16 L in the balance in the `washing-in` state, where the circuit
    holds 6e-6 L. That error is six hundred thousand of those roundings
    (measured 2026-10-11).
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
