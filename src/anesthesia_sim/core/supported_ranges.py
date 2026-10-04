"""The closed intervals the shipped model is supported over, and the guards
that refuse a setting outside them.

Four of the five bound a *setting*. The three flows among them are checked
once, where a flow is built as its type - `FreshGasFlow`, `AlveolarVentilation`
and `CardiacOutput`, below - and every signature and record field that holds a
flow past that point takes the type, so the check is made nowhere else and no
way in has to remember it (`PL-0YYV`); the fourth, the delivered
concentration, is checked when a caller changes it. The fifth bounds the
*run* - how much elapsed simulated time the model is claimed to represent a
patient over - and is checked as each step is taken, because a run length is
reached rather than set. It is also checked where a run is *handed* a point on
that span instead of reaching it - a state built part-way through a run, a run
definition's opening or its reach - because there the value handed in is what
is wrong. It is otherwise the same kind of statement as the four, and lives
here for that reason.

`docs/MODEL.md` § "Supported input ranges" is the specification; this module
is where the numbers live, so that every path that can change a setting -
core, controller, interface, notebook, test - is bounded by the same guard
instead of relying on the interface's sliders to stay inside the domain.

**Why the model declares these and not the interface.** The sliders' maxima
look like presentation choices, and they were: until this module existed the
only statement of the supported range was `app/simulation_view.py`, and
`AgentUptakeSystem.set_cardiac_output(1000.0)` was accepted and simulated.

What makes them the model's own is **physiological applicability, not
numerical error** (`PL-X9KD`). The previous statement here was that the shipped
operator split's first-order coefficient grew with the flows, so far enough
outside these intervals a displayed number was wrong by a margin the interface
could not show. That method is retired: the exact propagator solves the
governing equations at any flows whatever, so a cardiac output of 1000 L/min
now yields an *arithmetically correct* answer. It is a correct answer to a
question physiology does not ask. These intervals are the range over which the
lumped three-group compartment structure, the reference adult's fixed
volumes and the constant-coefficient partition model are claimed to represent a
patient at all; outside them the equations still solve and their solution
stands for nothing. `docs/MODEL.md` § "Supported input ranges" argues each
interval.

That the reference gates are driven at this envelope's corner is a consequence
of declaring it, not evidence for it: the trajectories are built from these
constants, so they would follow the interval wherever it was put.

**Refused, not clamped**, for the reason `BreathingCircuit` gives for the
vaporizer maximum it enforces the same way: a silently clamped setting would
simulate, display, and chart a value the caller did not ask for.

The fourth control, delivered concentration, is bounded here only by the
0-to-1 fraction every concentration obeys; its real limit is the vaporizer's
calibrated maximum, which is agent-specific and therefore lives on
`BreathingCircuit` as instance state rather than as a constant here.

**Each flow is a type, built only through its guard** (`PL-0YYV`, slice 1 of
`PL-51B7`). `FreshGasFlow`, `AlveolarVentilation` and `CardiacOutput` are
`float` subclasses whose constructors call the guards below, for the reasons
`core/simulation_step.py` gives for `SimulationStep`: a `NewType` is erased at
run time and proves nothing about a range, and a frozen record would put a
field access into every equation. Each is the number itself in the
arithmetic, and arithmetic on one returns a plain `float`, so a quantity
derived from a flow - a tissue's share of cardiac output, the litres per
second the equations read - carries no proof it was never given. Checked by
hand at each way in, the three were checked by every compartment and by no
settings record, and a `RunDefinition` built from one ran a cardiac output of
1000 L/min (`PL-HSFV`); a record whose fields take the types cannot be built
holding one. `mypy` reads `src/` and not `tests/`, and passes a value typed
`Any`, so each place a flow is *stored* - a compartment's constructor and
setter, and `UptakeEquationSettings` - calls `require_fresh_gas_flow`,
`require_alveolar_ventilation` or `require_cardiac_output` first, which refuse
a bare `float` as the programming error it is; the layers that forward a flow,
`AgentUptakeSystem` and `app/controller.py`, take the type and check nothing.

**The case instant and the step count are types too** (`PL-CN5S`, slice 2 of
`PL-51B7`). `CaseInstant` is a `float` subclass built only through
`require_supported_case_instant`, for the reasons the flows are, and every
record field that holds an instant of the case and every method that moves a
run to one takes it: `RunDefinition`'s opening, reach and keyframes,
`SimulationState.elapsed_s`, the marks in `app/bookmarks.py`, and the instant a
branch is taken at. The instants a run is only *read* at - `RunDefinition`'s
`state_at` and a drawn window's bounds - stay a `float`, because the run's own
opening and reach, both checked instants, bound them and refuse what falls
outside: that is a relation between the instant and the run, which belongs to
the run. `StepCount` is an `int` subclass checking what a count can be checked
for alone, that it is whole and nonnegative. How many steps a run may complete
depends on the step it takes them at, so `SimulationState` keeps checking the
pair. Each is refused as a bare value at run time where it is stored or a run
is moved to it, by `require_case_instant` and `require_step_count`.

**Fresh gas flow has a second bound of the same shape, and it is not here**
(`PL-8PS6`). What a *machine* can deliver - its flowmeters, its minimum-flow
floor, whether it supports minimal- or closed-circuit flow - differs between
machines and is read from a validated machine profile under `data/machines/`
into `BreathingCircuit.deliverable_fresh_gas_flow_range`, for the reason the
vaporizer maximum lives there. The interval below is the model's and only the
model's: the range the lumped compartment structure is claimed to represent a
patient over. The effective limit on the control is the intersection of the
two, and each refuses in its own words.

Keeping them apart is a safety property rather than a tidiness one. Merged,
a second profile whose flowmeter reaches 15 L/min would widen the domain the
reference gates were driven over without any statement in this module
changing - a number produced outside everything that was verified, and
indistinguishable on screen from one inside it. The converse fails the same
way: a machine with no true off position, floored at 0.5 L/min, would either
be unrepresentable or would move the model's floor for every other machine.
The shipped `reference_circle_system` profile declares no range at all, so
this interval is the only bound today; `docs/MODEL.md` § "Supported input
ranges" carries both claims and what separates them.

The step that would cross the run-length bound is refused on
`SimulationState`, which counts the steps a run takes, rather than on a
compartment: a compartment advanced alone has no run length to be past the
end of. It refuses the step that would cross the boundary rather than raising
after crossing it, so a run that stops here stands on a completed step at a
simulated time inside the supported span.

Two more guards refuse a point on the span that is handed in rather than
reached: `require_supported_step_count` for a `SimulationState` built
part-way through a run, and `require_supported_case_instant`, which every
`CaseInstant` is built through, for the instants a run opens at, is moved to
and is marked at. A branch is both, built where its parent stood, so these are
what refuse one taken past the span before anything reads it (`PL-BMY5`,
`PL-73ZN`). The first is built on the same `maximum_step_count`
as the step's guard, so the count a run stops on at the limit is exactly the
last one a state may be built at, whatever the step. That count is decided on
the simulated time it lands at, so the instant a run stops on is one the
second accepts and the instant one step later is one it refuses (`PL-8H2R`).

Widening any interval is a safety-critical change and not a convenience, but
the work it now takes is different: argue that the compartment structure still
represents a patient over the wider range, re-run the reference gates at the
new corner, and revise `docs/MODEL.md` §§ "Supported input ranges" and
"Independent-solution test" together. What it no longer implies is a
re-derivation of the displayed resolution or of the supported simulation step.
Those two used to hang off the splitting coefficient measured here, and that
chain is cut: neither is derived from anything measured over this envelope.
"""

from __future__ import annotations

import sys
from math import floor, isfinite

from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationDomainLimitError
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.units import SECONDS_PER_HOUR

# Fresh gas flow into the breathing circuit.
MINIMUM_FRESH_GAS_FLOW_L_MIN = 0.0
MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10.0

# Alveolar (not minute) ventilation.
MINIMUM_ALVEOLAR_VENTILATION_L_MIN = 0.0
MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12.0

# Cardiac output, which is also every tissue's and the venous compartment's
# blood flow through their perfusion fractions.
MINIMUM_CARDIAC_OUTPUT_L_MIN = 0.0
MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10.0

# How long a run may be, as elapsed simulated time. Unlike the three above
# this bounds the *run* rather than a setting, and it is reached mid-run
# rather than refused at entry, so `require_supported_run_length` below
# refuses the step that would cross it instead of a value a caller passed.
# Where a caller does pass a point on it - a step count, or an instant a run
# opens at, is moved to or is marked at - `require_supported_step_count` and
# `require_supported_case_instant`, through `CaseInstant`, refuse that value.
#
# **It is a validity limit, and it was a memory one.** The 30-day figure it
# replaces was set on 2026-08-25 to size a concentration history that no
# longer exists, and carried forward as though it described the model. It did
# not: what bounds a run is the same question the three intervals above answer
# for the flows - how far the shipped structure and parameter set are claimed
# to represent a patient - and for elapsed time that is answered by what this
# model leaves out.
#
# **The omission that binds is metabolism**, which `docs/MODEL.md`
# § "Known limitations" records and § "Published wash-in and elimination validation test"
# already draws the consequence of: it rejects the Yasuda papers' own
# multi-day elimination curves as a comparison, because over days the missing
# metabolism is no longer negligible and neither is the fat group's flow,
# which the same document weighs against two human sources that disagree
# about its direction (about twice a resting depot measurement; at or a
# little below what human washout fits imply). Inside the span the tail is
# already missing its largest measured term - the fourth compartment human
# washout needs and this model lacks, the largest from about the third hour
# of elimination - which § "Supported run length" records; that bounds what
# the late tail is worth, not how long a run may be. Sevoflurane is the binding
# agent - 2% to 5% of the absorbed dose is metabolized, against far less for
# isoflurane and desflurane - and its metabolism starts immediately rather than
# late, fluoride and HFIP appearing in plasma within minutes of the start of
# administration. What makes omitting it safe over a case is that the same
# review finds metabolism "does not contribute to the termination of clinical
# drug effect": true while ventilation and perfusion dominate the trace, and
# progressively false once the only thing still moving is the slow tail this
# model gives no sink to.
#   Kharasch ED. Biotransformation of sevoflurane. Anesth Analg
#   1995;81(6 Suppl):S27-38. PMID 7486145,
#   doi:10.1097/00000539-199512001-00005.
# A review, so tier 2 under `docs/MODEL.md` § "Source hierarchy" - cited for
# the magnitude and timing of the omission, never as the authority for a
# value. Nothing here is computed from it: 24 hours is a declared envelope
# argued against that omission, not a number derived from a metabolic rate.
#
# **Why 24 hours.** It clears every anesthetic this simulator exists to teach
# by a wide margin; it is about 0.6 of the fat group's roughly 42 h time
# constant, so the fat compartment is still visibly loading and the
# slow-compartment demonstration survives, where a cap of a few hours would
# truncate the one thing the fat trace exists to show; and it sits inside the
# regime the source above calls clinically negligible for metabolism, near the
# outer edge of the 0.35-to-9.5 MAC-hour exposure range over which that
# omission's size has been measured at all.
#
# **The fat time constant is a floor here, not a multiplier.** Many multiples
# of the slowest mode is the regime this project already declines to validate
# over, so a cap argued as "several fat time constants" would select for the
# part of the trace that is most nearly all omission. It bounds the cap from
# below - shorter than about one of them and the fat trace stops teaching -
# and says nothing about how far above it a run may go.
#
# **A declared envelope rather than a discovered cliff**, exactly as
# `docs/MODEL.md` § "What a setting outside the range costs" says of the three
# intervals above: nothing breaks at hour 25, and the equations solve as
# exactly there as anywhere. What stops at the boundary is the claim that the
# solution stands for a patient. Moving it is a safety-critical change and
# takes the same work: argue the wider span against what the model omits, and
# revise `docs/MODEL.md` § "Supported input ranges" with it.
#
# Volatile sedation in intensive care runs for days and is a real teaching
# target, and it is precisely the regime this model is wrong in. Reaching it
# is a model extension - metabolism first - and not a raise of this number.
MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86_400.0

# Every floor is zero, and each is named separately because each is a separate
# decision that could change on its own: flooring cardiac output above zero
# would not imply flooring ventilation. Zero is supported on all three because
# each names a real clinical state the simulator exists to teach - apnoea,
# circulatory arrest, the fresh gas turned off - and `docs/MODEL.md` §
# "Supported input ranges" argues each (PL-629Z).
#
# The reason previously given here was different and is retired with the
# operator split (`PL-X9KD`): that the splitting coefficient's worst case was
# measured on a zero-cardiac-output trajectory, so raising the floor would take
# the bound's worst case out of its own domain. There is no such coefficient
# now, and the gate trajectory that measures worst is the ventilator start,
# which needs no zero-perfusion phase.


def _require_supported(name: str, value: float, minimum: float, maximum: float) -> None:
    """Require a finite value inside one control's closed supported interval.

    One check rather than a finiteness guard followed by a range guard, so
    that every rejection - negative, NaN, infinite, or merely too large -
    carries the same message naming the interval the caller has to return to.
    """

    if not isfinite(value) or not minimum <= value <= maximum:
        raise SimulationConfigurationError(
            f"{name} of {value} is outside the supported input range of "
            f"{minimum} to {maximum} L/min, which is the domain this "
            f"compartment model is claimed to represent a patient over "
            f'(docs/MODEL.md, "Supported input ranges")'
        )


def require_supported_fresh_gas_flow(fresh_gas_flow_l_min: float) -> None:
    """Require a fresh gas flow inside the range the model is claimed over.

    This is the *model's* claim and the whole of what it checks. What the
    machine in front of the patient can actually deliver is a separate
    statement, held on `BreathingCircuit` and refused separately, so a caller
    reaching this guard directly is bounded by the envelope alone (`PL-8PS6`).

    Raises:
        SimulationConfigurationError: the flow is not finite, or is outside
            `MINIMUM_FRESH_GAS_FLOW_L_MIN` to `MAXIMUM_FRESH_GAS_FLOW_L_MIN`.
    """

    _require_supported(
        "fresh_gas_flow_l_min",
        fresh_gas_flow_l_min,
        MINIMUM_FRESH_GAS_FLOW_L_MIN,
        MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    )


def require_supported_alveolar_ventilation(alveolar_ventilation_l_min: float) -> None:
    """Require an alveolar ventilation inside the range the model is claimed over."""

    _require_supported(
        "alveolar_ventilation_l_min",
        alveolar_ventilation_l_min,
        MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    )


def require_supported_cardiac_output(cardiac_output_l_min: float) -> None:
    """Require a cardiac output inside the range the model is claimed over."""

    _require_supported(
        "cardiac_output_l_min",
        cardiac_output_l_min,
        MINIMUM_CARDIAC_OUTPUT_L_MIN,
        MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    )


class FreshGasFlow(float):
    """A fresh gas flow in L/min, checked against the supported range when built.

    It compares and computes as the `float` it was built from. A product or
    quotient of it is a plain `float`: the litres per second the circuit
    balance reads, or the circuit's wash-in time constant, is not a flow and
    is not presented as a checked one. The machine's own bound on this
    control is not checked here, since it is the device's and not the
    model's; `BreathingCircuit` checks it where the flow is set (`PL-8PS6`).

    Raises:
        SimulationConfigurationError: the flow is not finite, or is outside
            `MINIMUM_FRESH_GAS_FLOW_L_MIN` to `MAXIMUM_FRESH_GAS_FLOW_L_MIN`,
            the model's envelope (`docs/MODEL.md`, "Supported input ranges").
    """

    __slots__ = ()

    def __new__(cls, fresh_gas_flow_l_min: float) -> FreshGasFlow:
        require_supported_fresh_gas_flow(fresh_gas_flow_l_min)

        return super().__new__(cls, fresh_gas_flow_l_min)


class AlveolarVentilation(float):
    """An alveolar ventilation in L/min, checked against the supported range when built.

    It compares and computes as the `float` it was built from, and a product
    or quotient of it is a plain `float`, as `FreshGasFlow` says.

    Raises:
        SimulationConfigurationError: the ventilation is not finite, or is
            outside `MINIMUM_ALVEOLAR_VENTILATION_L_MIN` to
            `MAXIMUM_ALVEOLAR_VENTILATION_L_MIN`, the model's envelope
            (`docs/MODEL.md`, "Supported input ranges").
    """

    __slots__ = ()

    def __new__(cls, alveolar_ventilation_l_min: float) -> AlveolarVentilation:
        require_supported_alveolar_ventilation(alveolar_ventilation_l_min)

        return super().__new__(cls, alveolar_ventilation_l_min)


class CardiacOutput(float):
    """A cardiac output in L/min, checked against the supported range when built.

    It compares and computes as the `float` it was built from. Every tissue's
    blood flow is a perfusion fraction of it and the venous pool's is all of
    it, and each of those is a plain `float` that no supported-range guard
    bounds: a tissue cannot receive more than a checked cardiac output, and
    `UptakeEquationSettings` holds the three to summing to it.

    Raises:
        SimulationConfigurationError: the output is not finite, or is outside
            `MINIMUM_CARDIAC_OUTPUT_L_MIN` to `MAXIMUM_CARDIAC_OUTPUT_L_MIN`,
            the model's envelope (`docs/MODEL.md`, "Supported input ranges").
    """

    __slots__ = ()

    def __new__(cls, cardiac_output_l_min: float) -> CardiacOutput:
        require_supported_cardiac_output(cardiac_output_l_min)

        return super().__new__(cls, cardiac_output_l_min)


def _require_built(name: str, value: object, flow_type: type[float]) -> None:
    """Refuse a flow that was not built as `flow_type`, naming what to do instead.

    One message for the three flows, as `_require_supported` is one message
    for their ranges: the refusal names the parameter, the value and the
    type it has, the type it should have been built as, and where the range
    it would then be checked against is argued. A value built as one of the
    other two flow types is named as that and not told to rebuild, because a
    fresh gas flow arriving where a cardiac output belongs is a swapped
    argument, and rebuilding it as a `CardiacOutput` would check and store
    the wrong quantity under the right type.
    """

    if isinstance(value, flow_type):
        return

    if isinstance(value, (FreshGasFlow, AlveolarVentilation, CardiacOutput)):
        raise TypeError(
            f"{name} of {value!r} was built as {type(value).__name__}, which is not "
            f"{flow_type.__name__}: it was set from another flow, so build "
            f"{flow_type.__name__} from this flow's own value where it is set"
        )

    raise TypeError(
        f"{name} of {value!r} was not built as {flow_type.__name__}, it is "
        f"{type(value).__name__}: build it as {flow_type.__name__}(...) where it is set, "
        'which checks it against the supported range once (docs/MODEL.md, "Supported input '
        'ranges")'
    )


def require_fresh_gas_flow(fresh_gas_flow_l_min: object) -> None:
    """Require a fresh gas flow that was built as a `FreshGasFlow`, and so checked.

    The runtime half of the type, for the callers `mypy` does not read: a
    test, a notebook, or a value typed `Any`. It checks the type and not the
    range, which the constructor has already checked, and it runs where a flow
    is stored - `BreathingCircuit`, built or set, and `UptakeEquationSettings`
    - rather than at each layer that forwards one, so a bare `float` is
    refused once, before anything changes.

    Raises:
        TypeError: `fresh_gas_flow_l_min` is not a `FreshGasFlow` - a bare
            `float` included, whatever its value. This is a programming error
            in the caller rather than a rejected setting, so it is not an
            `AnesthesiaSimulationError` (`core/exceptions.py`).
    """

    _require_built("fresh_gas_flow_l_min", fresh_gas_flow_l_min, FreshGasFlow)


def require_alveolar_ventilation(alveolar_ventilation_l_min: object) -> None:
    """Require an alveolar ventilation built as an `AlveolarVentilation`, and so checked.

    The runtime half of the type, run where a ventilation is stored -
    `AlveolarCompartment`, built or set, and `UptakeEquationSettings` - as
    `require_fresh_gas_flow` explains.

    Raises:
        TypeError: `alveolar_ventilation_l_min` is not an
            `AlveolarVentilation` - a bare `float` included, whatever its
            value.
    """

    _require_built("alveolar_ventilation_l_min", alveolar_ventilation_l_min, AlveolarVentilation)


def require_cardiac_output(cardiac_output_l_min: object) -> None:
    """Require a cardiac output that was built as a `CardiacOutput`, and so checked.

    The runtime half of the type, run where a cardiac output is stored -
    `PatientCompartments`, built or set, and `UptakeEquationSettings` - as
    `require_fresh_gas_flow` explains.

    Raises:
        TypeError: `cardiac_output_l_min` is not a `CardiacOutput` - a bare
            `float` included, whatever its value.
    """

    _require_built("cardiac_output_l_min", cardiac_output_l_min, CardiacOutput)


def describe_count(count: int) -> str:
    """A count as a refusal names it: in digits, or, past the digits CPython
    will print (`sys.get_int_max_str_digits`, 4,300 unless set otherwise), as
    more than that many.

    Printing such a count raises `ValueError`, so a refusal that printed it
    escaped the simulator's own exceptions while it was being written
    (`PL-5F76`).
    """

    try:
        return str(count)
    except ValueError:
        sign = "-" if count < 0 else ""

        return f"{sign}<more than {sys.get_int_max_str_digits():,} digits>"


def _shown(value: object) -> str:
    """A value as a refusal names it: an `int` through `describe_count`, since
    its `repr` raises past the digits CPython will print, and anything else by
    its `repr`."""

    return describe_count(value) if isinstance(value, int) else repr(value)


class StepCount(int):
    """How many steps a run has completed, checked whole and nonnegative when built.

    That is what a count can be checked for on its own. How many steps a run
    may complete depends on the step it takes them at, so the supported range
    belongs to the pair, and `SimulationState` checks the two together through
    `require_supported_step_count`: a relation between two fields is the
    record's to check, as `.claude/rules/core-domain.md` says.

    It compares and computes as the `int` it was built from, and arithmetic on
    it returns a plain `int`, so the count after one more step is built as a
    `StepCount` again where it is stored (`SimulationState.advance`).

    Raises:
        SimulationConfigurationError: `step_count` is not an `int`, is a
            `bool`, which is not a count, or is negative.
    """

    __slots__ = ()

    def __new__(cls, step_count: int) -> StepCount:
        if isinstance(step_count, bool) or not isinstance(step_count, int) or step_count < 0:
            raise SimulationConfigurationError(
                f"step_count must be a whole, nonnegative number of steps, not {_shown(step_count)}"
            )

        return super().__new__(cls, step_count)


def require_step_count(step_count: object) -> None:
    """Require a count that was built as a `StepCount`, and so checked.

    The runtime half of the type, for the callers `mypy` does not read, as
    `require_fresh_gas_flow` explains. It runs where a count is stored, which
    is `SimulationState` when it is built; every count the state stores after
    that it builds as a `StepCount` itself.

    Raises:
        TypeError: `step_count` is not a `StepCount` - a bare `int` included,
            whatever its value. This is a programming error in the caller
            rather than a rejected setting, so it is not an
            `AnesthesiaSimulationError` (`core/exceptions.py`).
    """

    if not isinstance(step_count, StepCount):
        shown = _shown(step_count)

        raise TypeError(
            f"step_count of {shown} was not built as StepCount, it is "
            f"{type(step_count).__name__}: build it as StepCount({shown}) where the count is "
            "taken, which checks once that it is a whole, nonnegative number of steps"
        )


def maximum_step_count(simulation_step_s: SimulationStep) -> int:
    """How many steps of this size fit inside the supported run length.

    Whole steps only, and the boundary is included: a run may complete
    exactly this many steps, and the last of them lands on
    `MAXIMUM_ELAPSED_SIMULATION_TIME_S` or the largest simulated time below
    it that a whole number of steps can reach. That matches the closed
    intervals the three flows above declare - an endpoint is supported, not
    the first refused value.

    **Decided on the product, not the quotient** (`PL-8H2R`). The count is
    the largest whose simulated time - `SimulationState.elapsed_s`, the count
    times the step, rounded once - is no later than the limit, so the step's
    guard and the case-instant guard read one span. The quotient alone puts
    it a step either side at some computed steps: at `768 / 1_000_000 * 100`
    s it rounds up to a count whose last step lands at 86400.00000000001 s,
    and at 0.02304 s down to one short of the step that lands on 86400.0 s.
    So the floored quotient is only the first guess, kept where its product
    is inside the span and the next count's is not. Otherwise the answer is
    bracketed - no steps at all lands inside, and counts past the guess are
    tried at doubling distances until one lands past - and the bracket is
    halved. That is well defined because the product never falls as the
    count rises, and it ends however small the step, where a count walked
    one at a time need not: below about 1e-11 s a whole run of counts
    rounds to one product.

    **Derived once from the step rather than compared against a running
    total**, which is what makes the boundary reproducible. `docs/MODEL.md`
    § "Simulated time is a count of steps, not a running total" is the
    guarantee this rests on: elapsed time is one multiplication, so a run
    given identical inputs reaches this count at the same step on every
    machine. A halt decided by accumulating tenths of a second would land a
    step earlier or later depending on the order of the additions that got
    there, which would put the boundary a regression test pins in a
    different place per platform - and would break deterministic replay at
    exactly the point the test exists to hold.
    """

    def lands_inside(step_count: int) -> bool:
        return step_count * simulation_step_s <= MAXIMUM_ELAPSED_SIMULATION_TIME_S

    estimate = floor(MAXIMUM_ELAPSED_SIMULATION_TIME_S / simulation_step_s)

    if lands_inside(estimate) and not lands_inside(estimate + 1):
        return estimate

    inside, past, stride = 0, estimate, 1

    while lands_inside(past):
        inside, past, stride = past, past + stride, 2 * stride

    while past - inside > 1:
        middle = (inside + past) // 2

        if lands_inside(middle):
            inside = middle
        else:
            past = middle

    return inside


def require_supported_run_length(step_count: StepCount, simulation_step_s: SimulationStep) -> None:
    """Require room for one more step inside the supported run length.

    Refuses the step that would carry the run past
    `MAXIMUM_ELAPSED_SIMULATION_TIME_S`, leaving the run standing on the
    last simulated time the model is claimed to represent a patient at.

    `SimulationDomainLimitError` rather than `SimulationConfigurationError`:
    no value handed in is wrong and there is nothing for the caller to
    correct, so "fix it and carry on" is not available - the run has to
    stop. It is a `SimulationExecutionError` subclass for that reason, so a
    caller that knows only the base class stops the run, which is the safe
    default. A caller that catches this type specifically knows the run
    stopped because the model declined to extrapolate rather than because a
    step failed, and `docs/MODEL.md` § "Supported run length" requires that
    the two not be presented alike: nothing was miscalculated here, and
    every displayed value is a completed step's.
    """

    if step_count >= maximum_step_count(simulation_step_s):
        # A count past the largest float has no time to print: multiplying it
        # by the step raises `OverflowError` (`PL-5F76`).
        try:
            reached = f"{step_count * simulation_step_s:g} s of simulated time"
        except OverflowError:
            reached = f"{describe_count(step_count)} steps of {simulation_step_s} s"

        raise SimulationDomainLimitError(
            f"this run has reached {reached}, "
            f"which is the supported run length of {MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s "
            f"({MAXIMUM_ELAPSED_SIMULATION_TIME_S / SECONDS_PER_HOUR:g} h); beyond it "
            f"this model's omitted metabolism and its fat perfusion dominate the trace, "
            f'so it is not claimed to represent a patient (docs/MODEL.md, "Supported run '
            f'length")'
        )


def require_supported_step_count(step_count: StepCount, simulation_step_s: SimulationStep) -> None:
    """Require `step_count` to be no more steps than the supported run length allows.

    The question a run *handed* a position asks, where
    `require_supported_run_length` is the one a run *taking* a step asks,
    and the two differ at exactly one count: `maximum_step_count` is a
    legal place to stand and an illegal one to step from. Both read that one
    derivation, so a state built at the count a run stops on at the limit is
    accepted and the next count is not, at every step size - a run reached
    by stepping and one built at the same count cannot disagree about
    whether it is inside the span. Agreeing with the step's guard is what
    keeps a branch taken where its parent stopped from being refused; and
    because that count is decided on the time it lands at, this guard also
    accepts a count exactly where `require_supported_case_instant` accepts
    the count times the step (`PL-8H2R`).

    `SimulationConfigurationError` rather than `SimulationDomainLimitError`,
    the reverse of the step's guard and for its reason: here a value handed
    in is wrong. No supported run stood past the span, so a state built
    there is refused before a snapshot, a readout or a chart axis can
    present it as one (`PL-BMY5`).

    Like `maximum_step_count`, it takes the step as a `SimulationStep`, which
    was checked against the supported range when it was built, and the count
    as a `StepCount`, which was checked whole and nonnegative when it was
    built, so what is left to check here is the pair.

    Raises:
        SimulationConfigurationError: `step_count` is more than
            `maximum_step_count(simulation_step_s)`.
    """

    limit = maximum_step_count(simulation_step_s)

    if step_count > limit:
        raise SimulationConfigurationError(
            f"a run of {describe_count(step_count)} steps of {simulation_step_s} s is past the "
            f"supported run length of {MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s "
            f"({MAXIMUM_ELAPSED_SIMULATION_TIME_S / SECONDS_PER_HOUR:g} h), which allows "
            f"at most {limit} steps of that size; past it this model is not claimed to "
            f'represent a patient (docs/MODEL.md, "Supported run length")'
        )


def require_supported_case_instant(instant_s: float) -> None:
    """Require an instant on the case's axis inside the supported run length.

    The case's axis is simulated time since induction, which a branch shares
    with its parent, so this bounds where an instant falls and not how long
    whatever holds it has lasted: a branch spends what is left of its parent's
    span rather than a span of its own, as `docs/MODEL.md` § "Supported run
    length" says. Closed at
    both ends like every interval here, so an instant of exactly
    `MAXIMUM_ELAPSED_SIMULATION_TIME_S` is accepted, and that is where a run
    at the shipped 0.1 s step stops. At any step, the instant a run stops on
    is accepted and the instant one step later is refused, because
    `maximum_step_count` decides the last step on the time it lands at
    (`PL-8H2R`).

    Every `CaseInstant` is built through it, so it guards each instant a run
    is handed rather than reaches - a `RunDefinition`'s opening, which a
    branch takes from its parent, the reach it is moved to, a marked instant
    and the instant a branch is taken at - once, where the instant is built.
    It raises `SimulationConfigurationError` for the reason
    `require_supported_step_count` gives (`PL-73ZN`).

    Raises:
        SimulationConfigurationError: `instant_s` is not finite, or is
            outside 0 to `MAXIMUM_ELAPSED_SIMULATION_TIME_S`.
    """

    if not isfinite(instant_s) or not 0.0 <= instant_s <= MAXIMUM_ELAPSED_SIMULATION_TIME_S:
        raise SimulationConfigurationError(
            f"a case instant of {instant_s} s is outside the supported run length of 0 to "
            f"{MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s "
            f"({MAXIMUM_ELAPSED_SIMULATION_TIME_S / SECONDS_PER_HOUR:g} h), the span this "
            f'model is claimed to represent a patient over (docs/MODEL.md, "Supported run '
            f'length")'
        )


class CaseInstant(float):
    """An instant of the case in seconds, checked against the supported run length when built.

    Simulated time since induction, which is the axis a branch shares with
    its parent, so one number means the same instant on every run of a case.
    It compares and computes as the `float` it was built from, and a sum or a
    difference of it is a plain `float`: the instant one step on, or the width
    of a window, carries no proof it was never given, and is built as a
    `CaseInstant` where something holds it as an instant
    (`SimulationState.elapsed_s`).

    Raises:
        SimulationConfigurationError: the instant is not finite, or is
            outside 0 to `MAXIMUM_ELAPSED_SIMULATION_TIME_S`, as
            `require_supported_case_instant` states.
    """

    __slots__ = ()

    def __new__(cls, instant_s: float) -> CaseInstant:
        require_supported_case_instant(instant_s)

        return super().__new__(cls, instant_s)


def require_case_instant(name: str, instant_s: object) -> None:
    """Require an instant that was built as a `CaseInstant`, and so checked.

    The runtime half of the type, for the callers `mypy` does not read, as
    `require_fresh_gas_flow` explains. It runs where an instant is stored -
    `Keyframe`, `TimeBookmark` and `BookmarkCrossing` - and where a run is
    opened at or moved to one: `RunDefinition`, built or advanced, and the
    branch `SimulationController.resumed_at` takes. A function that only
    compares an instant, or forwards one, takes the type and checks nothing.

    Args:
        name: The parameter the instant was handed in as, for the message. An
            instant is an opening, a reach, a mark or a fork by where it is
            handed in rather than by its type, so the name is the caller's.
        instant_s: What was handed in.

    Raises:
        TypeError: `instant_s` is not a `CaseInstant` - a bare `float`
            included, whatever its value. This is a programming error in the
            caller rather than a rejected setting, so it is not an
            `AnesthesiaSimulationError` (`core/exceptions.py`).
    """

    if not isinstance(instant_s, CaseInstant):
        shown = _shown(instant_s)

        raise TypeError(
            f"{name} of {shown} was not built as CaseInstant, it is {type(instant_s).__name__}: "
            f"build it as CaseInstant({shown}) where the instant is chosen, which checks it "
            'against the supported run length once (docs/MODEL.md, "Supported run length")'
        )
