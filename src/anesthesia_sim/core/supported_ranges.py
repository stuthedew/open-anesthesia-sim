"""The closed intervals the shipped model is supported over, and the guards that enforce them.

This module declares five intervals. Four of them bound a *setting*, and three
of those four are flows: `FreshGasFlow`, `AlveolarVentilation` and
`CardiacOutput`, below. Each flow is checked once, when it is built as its
type. Every signature and record field that holds a flow after that point
takes the type, so no other code makes the check and no entry point has to
remember it (`PL-0YYV`). The fourth setting, the delivered concentration, is
checked when a caller changes it.

The fifth interval bounds the *run*: how much elapsed simulated time the model
is claimed to represent a patient over. It is checked as each step is taken,
because a run reaches its length rather than having it set. It is also checked
where a run is *handed* a point on that span instead of reaching it: a state
built part-way through a run, or a run definition's opening or its reach.
There, the value handed in is what is wrong. Otherwise the run length is the
same kind of statement as the four settings, and it lives here for that
reason.

`docs/MODEL.md` § "Supported input ranges" is the specification. This module
holds the numbers, so that every path that can change a setting is bounded by
the same guard, rather than relying on the interface's sliders to stay inside
the domain. Those paths are the core, the controller, the interface, a
notebook and a test.

**Why the model declares these and not the interface.** The sliders' maxima
look like presentation choices, and they once were. Until this module existed,
`app/simulation_view.py` was the only statement of the supported range, and
`AgentUptakeSystem.set_cardiac_output(1000.0)` was accepted and simulated.

The intervals belong to the model because of **physiological applicability,
not numerical error** (`PL-X9KD`). This module used to give a different
reason. The shipped operator split had a first-order coefficient that grew
with the flows, so far enough outside these intervals a displayed number was
wrong by a margin that the interface could not show. That method is retired.
The exact propagator solves the governing equations at any flows at all, so a
cardiac output of 1000 L/min now gives an *arithmetically correct* result. It
is a correct result to a question that physiology does not ask. These
intervals are the range over which three things are claimed to represent a
patient at all: the lumped three-group compartment structure, the reference
adult's fixed volumes, and the constant-coefficient partition model. Outside
them the equations still solve, but their solution represents no patient.
`docs/MODEL.md` § "Supported input ranges" argues each interval.

The reference gates are driven at this envelope's corner. That follows from
declaring the envelope, and it is not evidence for it. The gate trajectories
are built from these constants, so they would follow the interval wherever it
was put.

**Refused, not clamped.** `BreathingCircuit` enforces the vaporizer maximum
the same way, for the same reason: a silently clamped setting would simulate,
display and chart a value that the caller did not ask for.

The fourth control, the delivered concentration, is bounded here only by the
0-to-1 range of a fraction, which every concentration obeys. Its real limit is
the vaporizer's calibrated maximum. That maximum is agent-specific, so it
lives on `BreathingCircuit` as instance state rather than as a constant here.

**Each flow is a type, built only through its guard** (`PL-0YYV`, slice 1 of
`PL-51B7`). `FreshGasFlow`, `AlveolarVentilation` and `CardiacOutput` are
`float` subclasses whose constructors call the guards below. The reasons are
the ones `core/simulation_step.py` gives for `SimulationStep`: a `NewType` is
erased at run time and proves nothing about a range, and a frozen record would
put a field access into every equation. Each flow is the number itself in the
arithmetic. Arithmetic on one returns a plain `float`, so a quantity derived
from a flow does not claim a range check that it never passed. A tissue's
share of cardiac output and the litres per second that the equations use are
examples.

When the three flows were checked by hand at each entry point, every
compartment checked them and no settings record did. A `RunDefinition` built
from such a record ran a cardiac output of 1000 L/min (`PL-HSFV`). A record
whose fields take the types cannot be built holding such a value. `mypy`
checks `src/` and not `tests/`, and it accepts a value typed `Any`. So each
place that *stores* a flow first calls `require_fresh_gas_flow`,
`require_alveolar_ventilation` or `require_cardiac_output`, which refuse a
bare `float` as the programming error it is. For a compartment, that place is
the write to its flow field, whoever makes it. `BreathingCircuit`,
`AlveolarCompartment` and `PatientCompartments` each refuse the write in
`__setattr__` before the field changes. So the constructor, the setter and an
assignment that bypasses both all meet one check, and no snapshot can copy a
flow that nobody built (`PL-LBQY`, which found that such an assignment was
caught only by the next step). `UptakeEquationSettings` checks its three flows
as it is built. The layers that forward a flow, `AgentUptakeSystem` and
`app/controller.py`, take the type and check nothing.

**The case instant and the step count are types too** (`PL-CN5S`, slice 2 of
`PL-51B7`). `CaseInstant` is a `float` subclass built only through
`require_supported_case_instant`, for the same reasons as the flows. It is
built from the same inputs as they are: an `int` or a `float` and nothing
else, with minus zero stored as zero (`core/checked_number.py`, `PL-7N8P`).
Whatever opens, moves, keyframes, marks or branches a run takes a
`CaseInstant`. That covers `RunDefinition`'s opening, reach and keyframes, the
marks in `app/bookmarks.py`, and the instant at which a branch is taken.
`SimulationState.elapsed_s` returns one. The control record's instants are
still annotated `float` (`PL-RCYZ`). The instants at which a run is only
*read* stay a `float`: `RunDefinition`'s `state_at` and a drawn window's
bounds. The run's own opening and reach, which are both checked instants,
bound these instants and refuse what falls outside. That check is a relation
between the instant and the run, so it belongs to the run.

`StepCount` is an `int` subclass. It checks what a count can be checked for
on its own: that it is whole and nonnegative. How many steps a run may
complete depends on the step at which it takes them, so `SimulationState`
keeps checking the pair. A bare value is refused at run time in two places.
`require_case_instant` refuses it where `Keyframe`, `TimeBookmark` or
`BookmarkCrossing` stores an instant, or where a run is opened at or moved to
one. `require_step_count` refuses it where `SimulationState` stores its
count. Code that only passes either value on checks nothing. A value built as
another checked quantity is refused as the swapped argument it is. Both the
constructor and the stored-value check refuse it, through the one record of
the checked types in `core/checked_number.py` (`PL-979Z`).

**Fresh gas flow has a second bound of the same shape, and it is not here**
(`PL-8PS6`). What a *machine* can deliver differs between machines: its
flowmeters, its minimum flow, and whether it supports minimal-flow or
closed-circuit flow. That bound is read from a validated machine profile under
`data/machines/` into `BreathingCircuit.deliverable_fresh_gas_flow_range`, for
the same reason that the vaporizer maximum lives there. The interval below
belongs to the model alone: it is the range over which the lumped compartment
structure is claimed to represent a patient. The effective limit on the
control is the intersection of the two intervals, and each refuses a value in
its own words.

Keeping the two bounds apart is a matter of safety, not tidiness. If they were
merged, a second profile whose flowmeter goes up to 15 L/min would widen the
domain over which the reference gates were driven, without any statement in
this module changing. The result would be a number produced outside
everything that was verified, and indistinguishable on screen from one inside
it. The converse fails the same way. Take a machine with no true off position,
whose minimum flow is 0.5 L/min. It would either be impossible to represent,
or it would move the model's lower bound for every other machine. The shipped
`reference_circle_system` profile declares no range at all, so this interval
is the only bound today. `docs/MODEL.md` § "Supported input ranges" carries
both claims and what separates them.

`SimulationState` counts the steps a run takes, and it is what refuses the
step that would cross the run-length bound. A compartment does not, because a
compartment advanced alone has no run length to go past the end of.
`SimulationState` refuses the step that would cross the boundary rather than
raising after crossing it. So a run that stops here ends on a completed step,
at a simulated time inside the supported span.

Two more guards refuse a point on the span that is handed in rather than
reached. `require_supported_step_count` covers a `SimulationState` built
part-way through a run. `require_supported_case_instant`, through which every
`CaseInstant` is built, covers the instants at which a run opens, to which it
is moved, and at which it is marked. A branch is both kinds, because it is
built where its parent stood. So these two guards refuse a branch taken past
the span before anything uses it (`PL-BMY5`, `PL-73ZN`).
`require_supported_step_count` is built on the same `maximum_step_count`
as the step's guard. So, whatever the step, the count on which a run stops at
the limit is exactly the last count at which a state may be built. That count
is decided by the simulated time it lands at. So
`require_supported_case_instant` accepts the instant at which a run stops, and
refuses the instant one step later (`PL-8H2R`).

Widening any interval is a safety-critical change, not a convenience, but the
work it takes has changed. Argue that the compartment structure still
represents a patient over the wider range. Re-run the reference gates at the
new corner. Revise `docs/MODEL.md` §§ "Supported input ranges" and
"Independent-solution test" together. Widening no longer requires re-deriving
the displayed resolution or the supported simulation step. Both used to
depend on the splitting coefficient measured here, and that link is cut:
neither is now derived from anything measured over this envelope.
"""

from __future__ import annotations

from math import floor

from anesthesia_sim.core.checked_number import (
    CheckedQuantity,
    negative_zero_as_zero,
    require_a_number,
    require_not_another_quantity,
    shown,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationDomainLimitError
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.units import SECONDS_PER_HOUR

# Fresh gas flow into the breathing circuit.
MINIMUM_FRESH_GAS_FLOW_L_MIN = 0.0
MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10.0

# Alveolar (not minute) ventilation.
MINIMUM_ALVEOLAR_VENTILATION_L_MIN = 0.0
MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12.0

# Cardiac output. Through their perfusion fractions, it also sets the blood
# flow of every tissue and of the venous compartment.
MINIMUM_CARDIAC_OUTPUT_L_MIN = 0.0
MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10.0

# How long a run may be, as elapsed simulated time. Unlike the three intervals
# above, this one bounds the *run* rather than a setting. A run reaches it
# mid-run, so nothing refuses it at entry. Instead,
# `require_supported_run_length` below refuses the step that would cross it,
# rather than a value that a caller passed. A caller can also pass a point on
# this span: a step count, or an instant at which a run opens, to which it is
# moved, or at which it is marked. Then `require_supported_step_count`, or
# `require_supported_case_instant` through `CaseInstant`, refuses that value.
#
# **It is a validity limit. It used to be a memory limit.** The 30-day figure
# it replaces was set on 2026-08-25 to size a concentration history that no
# longer exists. That figure was then carried forward as though it described
# the model, which it did not. What bounds a run is the question that the
# three intervals above answer for the flows: how far the shipped structure
# and parameter set are claimed to represent a patient. For elapsed time, what
# this model leaves out answers that question.
#
# **The omission that limits the run is metabolism.** `docs/MODEL.md`
# § "Known limitations" records it, and
# § "Published wash-in and elimination validation test"
# already draws its consequence: it rejects the Yasuda papers' own multi-day
# elimination curves as a comparison. Over days, the missing metabolism is no
# longer negligible, and neither is the fat group's flow. The same document
# weighs that flow against two human sources that disagree about which way it
# is wrong: it is about twice a resting depot measurement, and at or a little
# below what fits to human washout imply. Even inside the span, the tail
# already lacks its largest measured term. That term is the fourth
# compartment that human washout needs and this model lacks, and it is the
# largest term from about the third hour of elimination.
# § "Supported run length" records this. It limits what the late tail is
# worth, not how long a run may be.
#
# Sevoflurane is the agent that sets the limit. Between 2% and 5% of its
# absorbed dose is metabolized, against far less for isoflurane and
# desflurane. Its metabolism also starts at once rather than late: fluoride
# and HFIP appear in plasma within minutes of the start of administration.
# The review cited below gives these figures. Omitting metabolism is safe
# over a case because the same review finds that metabolism "does not
# contribute to the termination of clinical drug effect". That holds while
# ventilation and perfusion dominate the trace. It becomes progressively false
# once the only thing still moving is the slow tail, for which this model has
# no sink.
#   Kharasch ED. Biotransformation of sevoflurane. Anesth Analg
#   1995;81(6 Suppl):S27-38. PMID 7486145,
#   doi:10.1097/00000539-199512001-00005.
# It is a review, so it is tier 2 under `docs/MODEL.md` § "Source hierarchy".
# It is cited for the magnitude and timing of the omission, never as the
# authority for a value. Nothing here is computed from it. The 24 hours is a
# declared envelope argued against that omission, not a number derived from a
# metabolic rate.
#
# **Why 24 hours.** There are two reasons. First, it is longer than every
# anesthetic this simulator exists to teach, by a wide margin. Second, it is
# about 0.6 of sevoflurane's fat time constant of roughly 42 h. A first-order
# compartment has gone a little over two fifths of the way to equilibrium at
# that fraction. So the fat compartment is still visibly loading, and the
# slow-compartment demonstration survives. A cap of a few hours would cut off
# the one thing the fat trace exists to show.
#
# **The span is not inside the measured exposure range** (`PL-MLPT`). The
# review above measured how sevoflurane's metabolism scales with dose only
# from 0.35 to 9.5 MAC-hours. The cap bounds elapsed time, not exposure. Every
# agent's dial opens at its 1 MAC, and a run held near 1 MAC accumulates about
# one MAC-hour per hour. So such a run leaves the measured range at about 9.5
# hours, and reaches about 24 MAC-hours at the cap. A run held at a higher
# setting reaches more. From the point where a run leaves that range, even the
# size of the omission is unmeasured. The 24 hours rests on the argument above
# that the omission grows progressively and without a cliff, not on that range.
#
# **The fat time constant sets a floor on the cap here, not a unit to
# multiply.** This project already declines to validate over many multiples
# of the slowest mode. So a cap argued as "several fat time constants" would
# favour the part of the trace that is most nearly all omission. The floor is
# a fraction of the time constant, not a whole one: the cap must be long
# enough that the fat compartment is still visibly loading when the run
# stops, and 24 hours meets it. The floor says nothing about how far above it
# a run may go.
#
# **This is a declared envelope, not a discovered cliff**, exactly as
# `docs/MODEL.md` § "What a setting outside the range costs" says of the three
# intervals above. Nothing breaks at hour 25, and the equations solve as
# exactly there as anywhere else. What stops at the boundary is the claim that
# the solution represents a patient. Moving the boundary is a safety-critical
# change and takes the same work as widening those intervals: argue the wider
# span against what the model omits, and revise `docs/MODEL.md`
# § "Supported input ranges" with it.
#
# Volatile sedation in intensive care runs for days and is a real teaching
# target, but it is exactly the regime in which this model is wrong. Reaching
# it needs a model extension, starting with metabolism, not a larger value
# here.
MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86_400.0

# Every minimum is zero. Each is named separately because each is a separate
# decision that could change on its own: raising the cardiac output minimum
# above zero would not imply raising the ventilation minimum. Zero is
# supported for all three flows because each zero is a real clinical state
# that the simulator exists to teach: apnoea, circulatory arrest, and the
# fresh gas turned off. `docs/MODEL.md` § "Supported input ranges" argues each
# (PL-629Z).
#
# This comment used to give a different reason, which was retired with the
# operator split (`PL-X9KD`). The reason was that the splitting coefficient's
# worst case was measured on a zero-cardiac-output trajectory, so raising the
# minimum would move the bound's worst case out of its own domain. There is no
# such coefficient now. The gate trajectory with the worst measurement is now
# the ventilator start, which needs no zero-perfusion phase.


def _require_supported(name: str, value: float, minimum: float, maximum: float) -> None:
    """Require a number inside one control's closed supported interval.

    First, `require_a_number` (`core/checked_number.py`) requires the value to
    be a number. So a `bool`, a `Decimal` or a `str` is refused in the
    simulator's own words before any comparison uses it (`PL-LLMN`). Then a
    single comparison follows, rather than a finiteness guard and then a range
    guard. So every rejection carries the same message, which names the
    interval the caller has to return to, whether the value is negative, NaN,
    infinite or merely too large. The closed-interval comparison refuses NaN on
    its own, because a NaN compares false against either bound. It also
    compares an `int` beyond the float range exactly, whereas `math.isfinite`
    would raise `OverflowError` while converting it. The message prints such an
    `int` through `shown`, as the refusal of a count does.

    Raises:
        TypeError: `value` is not an `int` or a `float`, or is a `bool`.
        SimulationConfigurationError: `value` is not finite, or is outside
            `minimum` to `maximum`.
    """

    require_a_number(name, value)

    if not minimum <= value <= maximum:
        raise SimulationConfigurationError(
            f"{name} of {shown(value)} is outside the supported input range of "
            f"{minimum} to {maximum} L/min, which is the domain this "
            f"compartment model is claimed to represent a patient over "
            f'(docs/MODEL.md, "Supported input ranges")'
        )


def require_supported_fresh_gas_flow(fresh_gas_flow_l_min: float) -> None:
    """Require a fresh gas flow inside the range the model is claimed over.

    This function checks the *model's* claim and nothing else. What the
    machine in front of the patient can actually deliver is a separate
    statement. `BreathingCircuit` stores that statement and refuses a flow
    outside it separately. So a caller that calls this guard directly is
    bounded by the model's envelope alone (`PL-8PS6`).

    Raises:
        TypeError: the flow is not an `int` or a `float`, or is a `bool`
            (`core/checked_number.py`).
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
    """Require an alveolar ventilation inside the range the model is claimed over.

    Raises:
        TypeError: the ventilation is not an `int` or a `float`, or is a
            `bool`, as `require_supported_fresh_gas_flow` says.
        SimulationConfigurationError: the ventilation is not finite, or is
            outside `MINIMUM_ALVEOLAR_VENTILATION_L_MIN` to
            `MAXIMUM_ALVEOLAR_VENTILATION_L_MIN`.
    """

    _require_supported(
        "alveolar_ventilation_l_min",
        alveolar_ventilation_l_min,
        MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    )


def require_supported_cardiac_output(cardiac_output_l_min: float) -> None:
    """Require a cardiac output inside the range the model is claimed over.

    Raises:
        TypeError: the output is not an `int` or a `float`, or is a `bool`,
            as `require_supported_fresh_gas_flow` says.
        SimulationConfigurationError: the output is not finite, or is outside
            `MINIMUM_CARDIAC_OUTPUT_L_MIN` to `MAXIMUM_CARDIAC_OUTPUT_L_MIN`.
    """

    _require_supported(
        "cardiac_output_l_min",
        cardiac_output_l_min,
        MINIMUM_CARDIAC_OUTPUT_L_MIN,
        MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    )


class FreshGasFlow(float, CheckedQuantity):
    """A fresh gas flow in L/min, checked against the supported range when built.

    It compares and computes as the `float` it was built from, with one
    exception. Built from minus zero, it stores zero, which is the flow it
    represents, so no readout prints a flow with a sign
    (`core/checked_number.py`). A product or quotient of it is a plain
    `float`. The litres per second that the circuit balance uses, or the
    circuit's wash-in time constant, is not a flow and is not presented as a
    checked one. The machine's own bound on this control is not checked here,
    because that bound belongs to the device and not to the model.
    `BreathingCircuit` checks it where the flow is set (`PL-8PS6`).

    Raises:
        TypeError: the flow was built as another checked quantity, such as a
            cardiac output, an instant or a step. That is a swapped argument,
            and it is refused before the range is checked. Or the flow is not
            an `int` or a `float`, or is a `bool`. Either case is a
            programming error in the caller rather than a refused setting
            (`core/checked_number.py`).
        SimulationConfigurationError: the flow is not finite, or is outside
            `MINIMUM_FRESH_GAS_FLOW_L_MIN` to `MAXIMUM_FRESH_GAS_FLOW_L_MIN`,
            the model's envelope (`docs/MODEL.md`, "Supported input ranges").
    """

    __slots__ = ()

    def __new__(cls, fresh_gas_flow_l_min: float) -> FreshGasFlow:
        require_not_another_quantity("fresh_gas_flow_l_min", fresh_gas_flow_l_min, cls)
        require_supported_fresh_gas_flow(fresh_gas_flow_l_min)

        return super().__new__(cls, negative_zero_as_zero(fresh_gas_flow_l_min))


class AlveolarVentilation(float, CheckedQuantity):
    """An alveolar ventilation in L/min, checked against the supported range when built.

    It compares and computes as the `float` it was built from, and it stores
    minus zero as zero. A product or quotient of it is a plain `float`.
    `FreshGasFlow` explains all three points.

    Raises:
        TypeError: the ventilation was built as another checked quantity, or
            is not an `int` or a `float`, or is a `bool`, as `FreshGasFlow`
            says.
        SimulationConfigurationError: the ventilation is not finite, or is
            outside `MINIMUM_ALVEOLAR_VENTILATION_L_MIN` to
            `MAXIMUM_ALVEOLAR_VENTILATION_L_MIN`, the model's envelope
            (`docs/MODEL.md`, "Supported input ranges").
    """

    __slots__ = ()

    def __new__(cls, alveolar_ventilation_l_min: float) -> AlveolarVentilation:
        require_not_another_quantity("alveolar_ventilation_l_min", alveolar_ventilation_l_min, cls)
        require_supported_alveolar_ventilation(alveolar_ventilation_l_min)

        return super().__new__(cls, negative_zero_as_zero(alveolar_ventilation_l_min))


class CardiacOutput(float, CheckedQuantity):
    """A cardiac output in L/min, checked against the supported range when built.

    It compares and computes as the `float` it was built from, and it stores
    minus zero as zero, as `FreshGasFlow` explains. Every tissue's blood flow
    is a perfusion fraction of it, and the venous pool's blood flow is all of
    it. Each of those flows is a plain `float` that no supported-range guard
    bounds. None needs one: a tissue cannot receive more than a checked
    cardiac output, and `UptakeEquationSettings` enforces that the three
    tissue flows sum to it.

    Raises:
        TypeError: the output was built as another checked quantity, or is
            not an `int` or a `float`, or is a `bool`, as `FreshGasFlow` says.
        SimulationConfigurationError: the output is not finite, or is outside
            `MINIMUM_CARDIAC_OUTPUT_L_MIN` to `MAXIMUM_CARDIAC_OUTPUT_L_MIN`,
            the model's envelope (`docs/MODEL.md`, "Supported input ranges").
    """

    __slots__ = ()

    def __new__(cls, cardiac_output_l_min: float) -> CardiacOutput:
        require_not_another_quantity("cardiac_output_l_min", cardiac_output_l_min, cls)
        require_supported_cardiac_output(cardiac_output_l_min)

        return super().__new__(cls, negative_zero_as_zero(cardiac_output_l_min))


def _require_built(name: str, value: object, flow_type: type[CheckedQuantity]) -> None:
    """Refuse a flow that was not built as `flow_type`, naming what to do instead.

    The three flows share this one message, as they share
    `_require_supported`'s one message for their ranges. The refusal names
    the parameter, the value and its type, the type it should have been built
    as, and where the range it would then be checked against is argued.

    `require_not_another_quantity` (`core/checked_number.py`) runs before
    this refusal, as it runs first in each flow's constructor. It names a
    value built as another checked quantity as that quantity, and does not
    tell the caller to rebuild it. Such a quantity is one of the other two flows, the step, a
    count, an instant or a concentration. A fresh gas flow arriving where a
    cardiac output belongs is a swapped argument. Rebuilding it as a
    `CardiacOutput` would check and store the wrong quantity under the right
    type. Until `PL-848D`, only the other two flows were named, and a
    `StepCount` handed in as a flow was told to build the flow from it.

    The value prints through `shown`. So a bare `int` too long for `repr` is
    named by its length, rather than escaping as `ValueError` while the
    refusal is written.
    """

    if isinstance(value, flow_type):
        return

    require_not_another_quantity(name, value, flow_type)

    raise TypeError(
        f"{name} of {shown(value)} was not built as {flow_type.__name__}, it is "
        f"{type(value).__name__}: build it as {flow_type.__name__}(...) where it is set, "
        'which checks it against the supported range once (docs/MODEL.md, "Supported input '
        'ranges")'
    )


def require_fresh_gas_flow(fresh_gas_flow_l_min: object) -> None:
    """Require a fresh gas flow that was built as a `FreshGasFlow`, and so checked.

    This is the runtime half of the type, for the callers that `mypy` does
    not check: a test, a notebook, or a value typed `Any`. It checks the type
    and not the range, which the constructor has already checked. It runs
    where a flow is stored, rather than at each layer that forwards one, so a
    bare `float` is refused once, before anything changes. A flow is stored
    in two places. The first is every write to
    `BreathingCircuit.fresh_gas_flow_l_min`, where the circuit's
    `__setattr__` refuses a bare value before the field changes. That holds
    whether the constructor, `set_fresh_gas_flow` or an assignment that
    bypasses both makes the write (`PL-LBQY`). The second is
    `UptakeEquationSettings`, as it is built.

    Raises:
        TypeError: `fresh_gas_flow_l_min` is not a `FreshGasFlow` - a bare
            `float` included, whatever its value. This is a programming error
            in the caller rather than a rejected setting, so it is not an
            `AnesthesiaSimulationError` (`core/exceptions.py`).
    """

    _require_built("fresh_gas_flow_l_min", fresh_gas_flow_l_min, FreshGasFlow)


def require_alveolar_ventilation(alveolar_ventilation_l_min: object) -> None:
    """Require an alveolar ventilation built as an `AlveolarVentilation`, and so checked.

    This is the runtime half of the type, as `require_fresh_gas_flow`
    explains. It runs where a ventilation is stored. That is every write to
    `AlveolarCompartment.alveolar_ventilation_l_min`, where the compartment's
    `__setattr__` refuses a bare value before the field changes, and
    `UptakeEquationSettings`.

    Raises:
        TypeError: `alveolar_ventilation_l_min` is not an
            `AlveolarVentilation` - a bare `float` included, whatever its
            value.
    """

    _require_built("alveolar_ventilation_l_min", alveolar_ventilation_l_min, AlveolarVentilation)


def require_cardiac_output(cardiac_output_l_min: object) -> None:
    """Require a cardiac output that was built as a `CardiacOutput`, and so checked.

    This is the runtime half of the type, as `require_fresh_gas_flow`
    explains. It runs where a cardiac output is stored. That is every write
    to `PatientCompartments.cardiac_output_l_min`, where the patient's
    `__setattr__` refuses a bare value before the field changes, and
    `UptakeEquationSettings`.

    Raises:
        TypeError: `cardiac_output_l_min` is not a `CardiacOutput` - a bare
            `float` included, whatever its value.
    """

    _require_built("cardiac_output_l_min", cardiac_output_l_min, CardiacOutput)


def describe_count(count: int) -> str:
    """Return a count in the form a refusal message gives it.

    The count is given in digits. Beyond the number of digits that CPython
    will print (`sys.get_int_max_str_digits`, 4,300 unless set otherwise), it
    is given as more than that many digits.

    Printing such a count raises `ValueError`. So a refusal that printed it
    escaped the simulator's own exceptions while the refusal was being
    written (`PL-5F76`). `shown` in `core/checked_number.py` is the rule for
    every refused value, including the concentrations. This function is its
    name for a count.
    """

    return shown(count)


class StepCount(int, CheckedQuantity):
    """How many steps a run has completed, checked whole and nonnegative when built.

    Whole and nonnegative is what a count can be checked for on its own. How
    many steps a run may complete depends on the step at which it takes them.
    So the supported range belongs to the pair, and `SimulationState` checks
    the two together through `require_supported_step_count`. As
    `.claude/rules/core-domain.md` says, a relation between two fields is for
    the record that holds them to check.

    It compares and computes as the `int` it was built from. Arithmetic on it
    returns a plain `int`, so the count after one more step is built as a
    `StepCount` again where it is stored (`SimulationState.advance`).

    A value that is not an `int` at all is refused with a `TypeError`, as the
    flows refuse a value that is not a number (`core/checked_number.py`). A
    `float`, a `str` or a `bool` where a count belongs is a programming error
    in the caller, not a count that the simulator declined. `2.0` is whole but
    is refused with them, because a `float` handed in is a sign that something
    computed it as a time. A `bool` is an `int` to Python, and it is refused
    all the same, because `True` is not a count of steps. `PL-LLMN` moved the
    `bool` case from the configuration error below to this `TypeError`.

    Raises:
        TypeError: `step_count` is not an `int`, or is a `bool`. A value built
            as another checked quantity, every one of which is a `float`, is
            named as a swapped argument rather than as a value that is not an
            `int`. Every checked type names such a value that way
            (`core/checked_number.py`, `PL-979Z`).
        SimulationConfigurationError: `step_count` is negative.
    """

    __slots__ = ()

    def __new__(cls, step_count: int) -> StepCount:
        require_not_another_quantity("step_count", step_count, cls)

        if isinstance(step_count, bool) or not isinstance(step_count, int):
            raise TypeError(
                f"step_count of {shown(step_count)} has type {type(step_count).__name__}, not "
                "int: build it from the count itself, which is then checked whole and nonnegative"
            )

        if step_count < 0:
            raise SimulationConfigurationError(
                f"step_count must be a whole, nonnegative number of steps, not {shown(step_count)}"
            )

        return super().__new__(cls, step_count)


def require_step_count(step_count: object) -> None:
    """Require a count that was built as a `StepCount`, and so checked.

    This is the runtime half of the type, for the callers that `mypy` does
    not check, as `require_fresh_gas_flow` explains. It runs where a count is
    stored, which is at every write to `SimulationState`'s count field
    (`PL-8W1W`). The state builds every count it stores as a `StepCount`
    itself. `require_not_another_quantity` (`core/checked_number.py`) runs
    before this refusal, as it runs first in the constructor. It names a value built as another
    checked quantity as that quantity, and does not tell the caller to
    rebuild it. A step or an instant arriving where a count belongs is a
    swapped argument, and no `StepCount` built from it would correct that.

    Raises:
        TypeError: `step_count` is not a `StepCount` - a bare `int` included,
            whatever its value. This is a programming error in the caller
            rather than a rejected setting, so it is not an
            `AnesthesiaSimulationError` (`core/exceptions.py`).
    """

    if isinstance(step_count, StepCount):
        return

    require_not_another_quantity("step_count", step_count, StepCount)

    raise TypeError(
        f"step_count of {shown(step_count)} was not built as StepCount, it is "
        f"{type(step_count).__name__}: build it as StepCount(...) where the count is taken, "
        "which checks once that it is a whole, nonnegative number of steps"
    )


def maximum_step_count(simulation_step_s: SimulationStep) -> int:
    """How many steps of this size fit inside the supported run length.

    The count is of whole steps only, and the boundary is included. A run may
    complete exactly this many steps. The last of them lands on
    `MAXIMUM_ELAPSED_SIMULATION_TIME_S`, or on the largest simulated time
    below it that a whole number of steps can reach. This matches the closed
    intervals that the three flows above declare: an endpoint is supported,
    and is not the first refused value.

    **The count is decided on the product, not the quotient** (`PL-8H2R`). It
    is the largest count whose simulated time is no later than the limit.
    That simulated time is `SimulationState.elapsed_s`: the count times the
    step, rounded once. So the step's guard and the case-instant guard use
    the same span. For some computed steps, the quotient alone would put the
    count one step too high or too low. At a step of
    `768 / 1_000_000 * 100` s it rounds up to a count whose last step lands
    at 86400.00000000001 s. At 0.02304 s it rounds down to one short of the
    step that lands on 86400.0 s. So the floored quotient is only the first
    guess. It is kept when its product is inside the span and the next
    count's product is not. Otherwise the function brackets the answer and
    then halves the bracket. The lower end of the bracket starts at no steps
    at all, which always lands inside. Counts past the guess are tried at
    doubling distances until one lands past the limit, which gives the upper
    end. This search is well defined because the product never falls as the
    count rises. It also ends however small the step is, which a count walked
    one at a time need not do: below about 1e-11 s, a whole run of
    consecutive counts rounds to one product.

    **The count is derived once from the step, not compared against a running
    total**, and that is what makes the boundary reproducible. It rests on
    the guarantee in `docs/MODEL.md`
    § "Simulated time is a count of steps, not a running total": elapsed time
    is one multiplication, so a run given identical inputs reaches this count
    at the same step on every machine. A halt decided by adding up tenths of
    a second would land a step earlier or later, depending on the order of
    the additions. The boundary that a regression test pins would then fall
    in a different place on each platform. That would also break
    deterministic replay at exactly the point the test exists to protect.
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

    It refuses the step that would carry the run past
    `MAXIMUM_ELAPSED_SIMULATION_TIME_S`. The run is left at the last
    simulated time at which the model is claimed to represent a patient.

    It raises `SimulationDomainLimitError` rather than
    `SimulationConfigurationError`. No value handed in is wrong, and there is
    nothing for the caller to correct, so "fix it and carry on" is not
    available: the run has to stop. For that reason the error is a
    `SimulationExecutionError` subclass, so a caller that knows only the base
    class stops the run, which is the safe default. A caller that catches
    this type specifically knows that the run stopped because the model
    declined to extrapolate, not because a step failed. `docs/MODEL.md`
    § "Supported run length" requires that the two cases not be presented
    alike: nothing was miscalculated here, and every displayed value comes
    from a completed step.
    """

    if step_count >= maximum_step_count(simulation_step_s):
        # A count beyond the largest float has no time to print, because
        # multiplying it by the step raises `OverflowError` (`PL-5F76`).
        try:
            reached = f"{step_count * simulation_step_s:g} s of simulated time"
        except OverflowError:
            reached = f"{describe_count(step_count)} steps of {simulation_step_s} s"

        raise SimulationDomainLimitError(
            f"this run has reached {reached}, "
            f"which is the supported run length of {MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s "
            f"({MAXIMUM_ELAPSED_SIMULATION_TIME_S / SECONDS_PER_HOUR:g} h); this model "
            f"is not validated past it, because it omits metabolism and its fat flow "
            f'differs from measurement (docs/MODEL.md, "Supported run length")'
        )


def require_supported_step_count(step_count: StepCount, simulation_step_s: SimulationStep) -> None:
    """Require `step_count` to be no more steps than the supported run length allows.

    This guard checks a run that is *handed* a position, and
    `require_supported_run_length` checks a run that is *taking* a step. The
    two differ at exactly one count, `maximum_step_count`: a run may stand
    there but may not step from there. Both guards use that one derivation.
    So at every step size, a state built at the count on which a run stops at
    the limit is accepted, and the next count is not. A run reached by
    stepping and a run built at the same count therefore cannot disagree
    about whether they are inside the span. Because this guard agrees with
    the step's guard, a branch taken where its parent stopped is not refused.
    And because that count is decided by the time it lands at, this guard
    accepts a count exactly when `require_supported_case_instant` accepts the
    count times the step (`PL-8H2R`).

    It raises `SimulationConfigurationError` rather than
    `SimulationDomainLimitError`. That is the reverse of the step's guard, and
    for the reason that guard gives: here a value handed in is wrong. No
    supported run ever stood past the span, so a state built there is refused
    before a snapshot, a readout or a chart axis can present it as a
    supported run (`PL-BMY5`).

    Like `maximum_step_count`, it takes the step as a `SimulationStep`, which
    was checked against the supported range when it was built. It takes the
    count as a `StepCount`, which was checked as whole and nonnegative when it
    was built. So only the pair is left to check here.

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

    The case's axis is simulated time since induction, and a branch shares it
    with its parent. So this guard bounds where an instant falls, not how
    long whatever holds the instant has lasted. As `docs/MODEL.md`
    § "Supported run length" says, a branch spends what is left of its
    parent's span rather than a span of its own. Like every interval here,
    this one is closed at both ends. So an instant of exactly
    `MAXIMUM_ELAPSED_SIMULATION_TIME_S` is accepted, and that is where a run
    at the shipped 0.1 s step stops. At any step, the instant at which a run
    stops is accepted and the instant one step later is refused, because
    `maximum_step_count` decides the last step by the time it lands at
    (`PL-8H2R`).

    Every `CaseInstant` is built through this function. So it guards each
    instant that a run is handed rather than reaches, once, where the instant
    is built. These instants are a `RunDefinition`'s opening, the reach to
    which it is moved, a marked instant, and the instant at which a branch is
    taken. A branch takes its opening from its parent. The function raises
    `SimulationConfigurationError` for the reason
    `require_supported_step_count` gives (`PL-73ZN`).

    First, `require_a_number` (`core/checked_number.py`) requires the instant
    to be a number, as `_require_supported` does for a flow. Until `PL-7N8P`,
    a `bool` was accepted as an instant of 1 s on the case's axis, a
    `Decimal` was converted and stored, and a string or a signalling NaN was
    refused in `math.isfinite`'s words. Then comes the single closed-interval
    comparison, with no finiteness guard before it. So a NaN, an infinity and
    an `int` beyond the float range are each refused against the run length
    in this function's words. Before, `math.isfinite` raised `OverflowError`
    while converting such an `int`. An `int` too long to print is named by
    its length, through `shown`.

    Raises:
        TypeError: `instant_s` is not an `int` or a `float`, or is a `bool`.
            This is a programming error in the caller rather than a refused
            instant, as `require_a_number` says.
        SimulationConfigurationError: `instant_s` is not finite, or is
            outside 0 to `MAXIMUM_ELAPSED_SIMULATION_TIME_S`.
    """

    require_a_number("instant_s", instant_s)

    if not 0.0 <= instant_s <= MAXIMUM_ELAPSED_SIMULATION_TIME_S:
        raise SimulationConfigurationError(
            f"a case instant of {shown(instant_s)} s is outside the supported run length of "
            f"0 to {MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s "
            f"({MAXIMUM_ELAPSED_SIMULATION_TIME_S / SECONDS_PER_HOUR:g} h), the span this "
            f'model is claimed to represent a patient over (docs/MODEL.md, "Supported run '
            f'length")'
        )


class CaseInstant(float, CheckedQuantity):
    """An instant of the case in seconds, checked against the supported run length when built.

    The instant is simulated time since induction. A branch shares that axis
    with its parent, so one number means the same instant on every run of a
    case. It compares and computes as the `float` it was built from. A sum or
    a difference of it is a plain `float`. So the instant one step later, or
    the width of a window, does not claim a range check that it never passed.
    It is built as a `CaseInstant` again where something stores it as an instant
    (`SimulationState.elapsed_s`).

    Like each flow, it is built from an `int` or a `float` and nothing else,
    never from a value built as another checked quantity, and it stores minus
    zero as zero (`core/checked_number.py`, `PL-7N8P`, `PL-979Z`).

    Raises:
        TypeError: the instant was built as another checked quantity, such as
            a count of steps, a flow or a step. That is a swapped argument,
            and it is refused before the run length is checked
            (`core/checked_number.py`). Or the instant is not an `int` or a
            `float`, or is a `bool`, as `require_supported_case_instant`
            states.
        SimulationConfigurationError: the instant is not finite, or is
            outside 0 to `MAXIMUM_ELAPSED_SIMULATION_TIME_S`, as
            `require_supported_case_instant` states.
    """

    __slots__ = ()

    def __new__(cls, instant_s: float) -> CaseInstant:
        require_not_another_quantity("instant_s", instant_s, cls)
        require_supported_case_instant(instant_s)

        return super().__new__(cls, negative_zero_as_zero(instant_s))


def require_case_instant(name: str, instant_s: object) -> None:
    """Require an instant that was built as a `CaseInstant`, and so checked.

    This is the runtime half of the type, for the callers that `mypy` does
    not check, as `require_fresh_gas_flow` explains. It runs where an instant
    is stored, in `Keyframe`, `TimeBookmark` and `BookmarkCrossing`. It also
    runs where a run is opened at or moved to an instant: in `RunDefinition`,
    when it is built or advanced, and in the branch that
    `SimulationController.resumed_at` takes. A function that only compares an
    instant, or forwards one, takes the type and checks nothing.

    `require_not_another_quantity` (`core/checked_number.py`) runs before
    this refusal, as it runs first in the constructor. It names a value built
    as another checked quantity as that quantity, and does not tell the
    caller to rebuild it. A count of 600 steps arriving where an instant belongs is a swapped
    argument, and a `CaseInstant` built from it would hold an instant of
    600 s.

    Args:
        name: The name of the parameter through which the instant was handed
            in, for the message. Whether an instant is an opening, a reach, a
            mark or a fork depends on where it is handed in, not on its type,
            so the caller supplies the name.
        instant_s: The value that was handed in.

    Raises:
        TypeError: `instant_s` is not a `CaseInstant` - a bare `float`
            included, whatever its value. This is a programming error in the
            caller rather than a rejected setting, so it is not an
            `AnesthesiaSimulationError` (`core/exceptions.py`).
    """

    if isinstance(instant_s, CaseInstant):
        return

    require_not_another_quantity(name, instant_s, CaseInstant)

    raise TypeError(
        f"{name} of {shown(instant_s)} was not built as CaseInstant, it is "
        f"{type(instant_s).__name__}: "
        "build it as CaseInstant(...) where the instant is chosen, which checks it against "
        'the supported run length once (docs/MODEL.md, "Supported run length")'
    )
