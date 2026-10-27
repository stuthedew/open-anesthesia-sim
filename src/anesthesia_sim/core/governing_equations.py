"""The governing equations of `docs/MODEL.md`, assembled as one system matrix.

This file is a transcription and nothing else. Every entry that
`build_system_matrix` writes is one term of one balance equation in that
document's "Governing equations" section. The entries are written in the order
in which the document states them. So a reader who knows the standard variables
can check the model against the code without a lookup table between them. The
arithmetic that solves the system is in `matrix_exponential.py`. That module
contains no physiology, and this file contains no numerical methods.

## Why the whole system is one matrix

Every setting is held constant across a simulation step, so within that step
the six compartment fractions obey a linear, time-invariant system

$$
\\frac{dy}{dt} = Ay + b .
$$

Writing the constant $`b`$ as a column multiplied by one extra state whose
value is always 1 turns the affine system into a linear one, $`dy/dt = Ay`$.
Then $`\\exp(A\\,\\Delta t)`$ is its **exact** propagator, at any step size. So
assembling $`A`$ is the whole of the model, and nothing downstream of it
approximates anything.

This module exists for that property. The operator split that it replaced
solved five pairwise exchanges exactly and applied them one after another.
That method is first-order accurate in the step rather than exact. It was
replaced because it spread the alveolar balance's two terms across two
non-adjacent sub-steps, and never formed the pulmonary uptake term at all.
Here that balance is one row, and its two terms are two entries in that row.

## The state vector

Six of the nine states are the modelled fractions, in the order in which
`docs/MODEL.md` introduces them: inspired gas, alveolar gas, mixed venous
blood, then the three tissue groups. Two more states accumulate the agent that
crosses the system boundary, and the last state is the constant.

$`F_I`$ is the fraction in the breathing circuit. The literature's gas-phase
cascade is $`F_D \\rightarrow F_I \\rightarrow F_A`$: delivered, inspired,
alveolar. Within this model's boundary there is one ideal, perfectly mixed
circuit, with no dead space and no separate inspiratory and expiratory limbs.
So the gas the patient inspires *is* the circuit gas, and the circuit's
fraction and the inspired fraction are identically the same quantity. The
state is named for the clinical quantity rather than for its container,
because $`F_A/F_I`$ is the curve that this simulator exists to let a learner
produce. The container is still the circuit, and `circuit.py` still owns it.

## Why delivered and exhausted agent are states rather than a side calculation

`docs/MODEL.md`'s mass-balance identity is

    initial agent + delivered agent = exhausted agent + currently stored agent

and it is checked after every step, at a tolerance tight enough to halt a run.
Delivered agent is $`\\dot V_F F_D \\Delta t`$, which needs no special
treatment. Exhausted agent is $`\\dot V_F \\int F_I \\, dt`$. Because $`F_I`$
follows the coupled trajectory, that integral has no closed form of its own.
The previous implementation used the integral of a *circuit-alone* wash-in.
That integral was consistent with the sub-step that produced it, and would not
be consistent with anything here.

When the integral is carried as a state, it is exact for the same reason that
the fractions are. The accounting residual is then at the level of rounding
error rather than of the numerical method's error. Delivered and exhausted
agent take two rows, for the `docs/MODEL.md` § "External delivery" and
"Circuit exhaust" equations respectively, and each row is written as its
equation.

**The two remaining reported transfers are recovered rather than accumulated,
and deliberately.** A net ventilatory transfer and a net pulmonary uptake are
*signed*, because agent returns from blood to alveolar gas during washout. So
rows for them would carry negative off-diagonal entries. Those entries would
break the Metzler property that `matrix_exponential.py` needs in order to
guarantee that no compartment is driven negative. Instead, both transfers are
derived from the balances, with no approximation. Pulmonary uptake over a step
is the change in the agent stored in the patient. The ventilatory transfer is
that change plus the change in the agent stored in the alveolar gas. This
holds because, by the alveolar equation itself, $`\\Delta M_A`$ is the
difference between the two transfers. `uptake_system.py` computes them in that
way.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from math import isfinite

from anesthesia_sim.core.concentration import (
    Fraction,
    Percent,
    fraction_from_percent,
    require_percent,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.matrix_exponential import Matrix
from anesthesia_sim.core.numerical_envelope import (
    CompartmentVolume,
    PartitionCoefficient,
    require_coefficient,
    require_compartment_volume,
)
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    AlveolarVentilation,
    CardiacOutput,
    FreshGasFlow,
    require_alveolar_ventilation,
    require_cardiac_output,
    require_fresh_gas_flow,
)
from anesthesia_sim.core.units import SECONDS_PER_MINUTE
from anesthesia_sim.core.validation import (
    require_nonnegative_finite,
    require_positive_finite,
    require_within_vaporizer_maximum,
)

INSPIRED_FRACTION = 0
"""$`F_I`$, the breathing circuit's fraction, which is what the patient inspires."""

ALVEOLAR_FRACTION = 1
"""$`F_A`$, the alveolar gas fraction. Arterial blood equilibrates with it."""

VENOUS_FRACTION = 2
"""$`F_v`$, the mixed venous partial-pressure-equivalent fraction."""

FIRST_TISSUE_FRACTION = 3
"""$`F_i`$ for the first tissue group. The groups occupy consecutive states."""

DELIVERED_AGENT_L = 6
"""Cumulative agent delivered from the vaporizer over the propagated interval."""

EXHAUSTED_AGENT_L = 7
"""Cumulative agent leaving through the circuit exhaust over that interval."""

UNIT_STATE = 8
"""The constant 1, which turns `dy/dt = Ay + b` into `dy/dt = Ay`.

Its row is empty, so it is constant by construction rather than by convention.
No step can perturb the forcing term that the other rows read from it. That
holds in floating point as well as in the algebra. `matrix_exponential` writes
the propagator row for an empty row as the identity's row before its
squarings, and the squarings then keep that row exact to the last bit. The
shift that makes the propagator nonnegative used to return the diagonal entry
as $`1+\\delta`$, which the squarings raised to $`(1+\\delta)^{2^{s}}`$
(`PL-2MD9`). Every propagator that the module returns has this exact row,
because a propagator that would need more squarings than `MAXIMUM_SQUARINGS`
is refused rather than returned.
"""

STATE_SIZE = 9
"""How many states the propagator carries."""

TISSUE_GROUP_COUNT = 3
"""Vessel-rich, muscle and fat: the three groups `patient.py` builds."""

_FRACTION_STATE_NAMES = (
    (INSPIRED_FRACTION, "inspired fraction F_I"),
    (ALVEOLAR_FRACTION, "alveolar fraction F_A"),
    (VENOUS_FRACTION, "mixed venous fraction F_v"),
    *(
        (FIRST_TISSUE_FRACTION + offset, f"tissue group {offset + 1} fraction F_{offset + 1}")
        for offset in range(TISSUE_GROUP_COUNT)
    ),
)
"""Each state position that holds a fraction, with the name that its refusal message gives.

The names describe the position in the state vector, because that is all that
`require_canonical_state` knows. The tissue groups are numbered in the order of
their states. Their names, such as "fat", belong to `patient.py`.
"""

_ACCUMULATOR_STATE_NAMES = (
    (DELIVERED_AGENT_L, "delivered agent in L"),
    (EXHAUSTED_AGENT_L, "exhausted agent in L"),
)
"""The two states that hold an amount of agent, with the name a refusal of each gives."""

MAXIMUM_CUMULATIVE_AGENT_L = (
    MAXIMUM_FRESH_GAS_FLOW_L_MIN * MAXIMUM_ELAPSED_SIMULATION_TIME_S / SECONDS_PER_MINUTE
)
"""The most agent that a case can deliver or exhaust, in litres: 14 400 L.

Agent enters with the fresh gas at the delivered fraction and leaves through the
exhaust at the circuit's fraction. Neither fraction exceeds 1, so neither total
can pass the fresh gas volume of a whole case at the fastest supported flow.
That is 10 L/min for 1 440 min. A larger total describes no case, and the
accumulator rows would carry it to `inf` (`PL-0WFJ`, found at review).
"""

CARDIAC_OUTPUT_TOLERANCE_L_S = 1e-12
CARDIAC_OUTPUT_RELATIVE_TOLERANCE = 1e-9
"""How far the tissue flows may sum away from cardiac output.

Blood leaving the tissue groups is all of the blood that returns to the venous
pool. `docs/MODEL.md`'s venous balance is
$`dF_v/dt = (\\sum_i Q_i F_i - QF_v)/V_v`$. So if $`\\sum_i Q_i`$ did not equal
$`Q`$, the model would put agent into that pool at one rate and take it out at
another. It would then create or destroy agent at a steady rate for as long as
the mismatch lasted.

`patient.py` already requires the perfusion *fractions* to sum to one, which
is the same statement about the same quantity. It is checked again here
because these settings are assembled separately from those compartments, and
this is the object from which the equations are actually built. The check sits
one call away from the arithmetic it protects, rather than in the class that
usually supplies the values. The absolute tolerance is what lets a zero cardiac
output pass, which `docs/MODEL.md` § "Supported input ranges" requires.
"""

TISSUE_BLOOD_FLOW_STATED_DECIMALS = 6
"""The decimal places, in L/min, to which the tissue-flow error rounds the summed flows.

The sum of the stored flows carries floating-point noise in its last digits,
such as 6.000000000000001 L/min at a cardiac output set to 6.0. No dial set
that precision, and a banner must not claim it. The rounding does not affect
the comparison above. Only the figure that the message prints is rounded, to a
microlitre per minute. That is three orders of magnitude below any dial step
and nine above the noise (`PL-M4M0`).
"""


def require_canonical_state(state: object) -> None:
    """Reject a state vector that the equations cannot be applied to.

    Two kinds of object open from a state that a run passed through: a
    `RunDefinition`, and the live system into which a branch resumes. This
    docstring calls each of them a sink. This function is the entry guard that
    both sinks share, so the two cannot come to disagree about what a state
    is. The guard lives here because each condition below is a statement about
    the state vector that this module defines, not about either caller.

    **The first check tests structure, not the type's name.** A value from the
    display path carries the same nine numbers in the same order as a
    canonical state, so nothing in its contents tells them apart. What does
    tell them apart is that the display path wraps its results in something
    that is not a tuple. `docs/MODEL.md` § "The canonical evaluation rule"
    argues for exactly this test. Even a sink that never thought to check
    rejects a value that is structurally not a state, and only such a value.
    A structural test also works for wrappers that this module has never
    heard of. `core/run_definition.py` rejects `DisplayState` by name before
    it calls this function, because that module knows the type. The message
    raised here is what a sink outside that module still gets.

    `state` is typed as `object` rather than as the tuple, deliberately. The
    values that this function rejects are exactly the ones that a caller
    believed were states. A signature that accepted only a state would put
    the check where it could never fire.

    **The guard also checks each value's physical range.** Each of the six
    fractions must lie from 0 to 1. Each of the two amounts of agent must lie
    from 0 to `MAXIMUM_CUMULATIVE_AGENT_L`. The live system's compartments
    refuse any other value, so a sink that opened from one would draw a state
    that the system can never hold. A `RunDefinition` opened from a fat
    fraction of 1.7 once returned fractions above one and below zero from
    `state_at`, with no error (`PL-0WFJ`). Each fraction is built as a
    `Fraction`, so the range and its message come from that one type.

    Raises:
        SimulationConfigurationError: `state` is not a tuple, is not
            `STATE_SIZE` long, holds a non-finite value, holds a fraction
            outside 0 to 1 or an amount of agent outside 0 to
            `MAXIMUM_CUMULATIVE_AGENT_L`, or does not hold exactly one at the
            `UNIT_STATE` position. The last condition is what makes every
            forcing term in `build_system_matrix` mean what it says. A state
            holding any other value there would scale the whole delivery term
            without changing any setting that a reader can see. A refusal of a
            fraction or an amount names its position and what it holds, such
            as "state[1] (alveolar fraction F_A)".
    """

    if not isinstance(state, tuple):
        raise SimulationConfigurationError(
            f"a {type(state).__name__} is not a state vector; a state that is stored, "
            "exported, replayed or forked from is taken from RunDefinition.state_at, "
            "whose answers compose their arithmetic in the canonical order"
        )

    if len(state) != STATE_SIZE:
        raise SimulationConfigurationError(
            f"a state has {len(state)} entries but the equations carry {STATE_SIZE}"
        )

    for index, value in enumerate(state):
        if not isfinite(value):
            raise SimulationConfigurationError(f"state[{index}] is {value}, which is not finite")

    for index, role in _FRACTION_STATE_NAMES:
        Fraction(state[index], name=f"state[{index}] ({role})")

    for index, role in _ACCUMULATOR_STATE_NAMES:
        require_nonnegative_finite(f"state[{index}] ({role})", state[index])

        if state[index] > MAXIMUM_CUMULATIVE_AGENT_L:
            raise SimulationConfigurationError(
                f"state[{index}] ({role}) of {state[index]!r} L is more than the "
                f"{MAXIMUM_CUMULATIVE_AGENT_L!r} L that a case can deliver or exhaust at the "
                "fastest supported fresh gas flow over the supported run length"
            )

    if state[UNIT_STATE] != 1.0:
        raise SimulationConfigurationError(
            f"state[{UNIT_STATE}] is the constant one the forcing terms are read against, "
            f"not {state[UNIT_STATE]}"
        )


def _hold_as_exact_floats(record: object, fields: tuple[str, ...]) -> None:
    """Replace each named field of a frozen settings record with the exact `float` it equals.

    Both propagator caches key on a settings record by value. That is safe only if two
    equal records build the same propagator bit for bit. A `numpy.float64` or another
    `float` subclass compares and hashes equal to the plain `float`. But CPython's `sum`
    adds values of exact type `float` with Neumaier compensation, and adds a subclass
    without it. So the matrix exponential built from a subclass differed in 39 of its 81
    entries at 7 s (`PL-5BD7`, measured 2026-10-05). An `int` is stored as the `float` it
    equals, for the same reason. Each field has passed `require_nonnegative_finite`, so it
    is an `int` or a `float` within the range a `float` can represent, and `float()`
    changes no value. The fields that hold a checked type are not passed here: the flows,
    the concentrations, and since `PL-QX2G` the volumes and partition coefficients
    (`core/numerical_envelope.py`). Each of those fields has the same type in every
    record, so it cannot be stored in two ways.
    """

    for field in fields:
        object.__setattr__(record, field, float(getattr(record, field)))


def _restore_through_checks(record: object, state: object) -> None:
    """Restore an unpickled settings record by building it again through its constructor.

    Unpickling a frozen settings record creates an empty object and passes the
    saved field values to `__setstate__`. The `__setstate__` that `dataclass`
    generates writes each value straight into its slot, so `__post_init__`
    never runs. A saved record whose state held a cardiac output of 1000.0 as
    a bare `float` and a fresh gas flow of NaN loaded without error, and a
    `RunDefinition` opened under it advanced (`PL-S11T`, measured 2026-10-25).
    `CheckedQuantity.__reduce__` (`core/checked_number.py`) protects a flow
    pickled as its checked type, but not a field whose saved state holds a
    bare number.

    So each record's `__setstate__` calls this function. It builds a new record
    from the saved values, which runs every check the constructor runs, and
    copies the checked fields into the restored object. A state the
    constructor would refuse is refused on load with the constructor's own
    exception. Every pickle protocol, `copy.copy` and `copy.deepcopy` restore
    the record through `__setstate__`, and so does a pickle written before
    this function existed. A `__reduce__` that called the constructor would
    change only how a record is written from now on. A saved or edited state
    in the form `dataclass` writes would still load through `__setstate__`.

    This protects against a saved value that is wrong, not against a pickle
    built to attack. A pickle can call any function that can be imported, so
    one can still write a record's slots directly. A pickle is trusted input.

    The state holds the field values in field order, without their names, as
    `dataclass` writes it. So a record saved before a change to the order of
    the fields would load into the wrong fields wherever the values still pass
    the checks.

    Raises:
        TypeError: the state is not a sequence of the record's field values,
            or a value is not of its field's checked type.
        SimulationConfigurationError: the constructor refuses a value.
    """

    if not isinstance(state, (list, tuple)):
        raise TypeError(
            f"a {type(record).__name__} is restored from a list of its field values, "
            f"not a {type(state).__name__}"
        )

    checked = type(record)(*state)

    for field in fields(checked):  # type: ignore[arg-type]
        object.__setattr__(record, field.name, getattr(checked, field.name))


@dataclass(frozen=True, slots=True)
class TissueGroupEquationSettings:
    """One tissue group's parameters, as its balance equation needs them.

    The blood flow is stored in litres per minute and read in litres per
    second, for the reason that `UptakeEquationSettings` gives for its own
    flows.

    The volume and the partition coefficient are checked types, built only
    inside the numerical envelope (`core/numerical_envelope.py`). So the
    product in `washin_rate_s` is positive and finite for every record. Before
    `PL-QX2G` both were checked only as positive and finite, and a volume of
    1e-300 L with a coefficient of 1e-30 made that product underflow to zero.

    Raises:
        TypeError: the volume was not built as a `CompartmentVolume`, or the
            coefficient as a `PartitionCoefficient`.
        SimulationConfigurationError: the blood flow is negative or not
            finite. The flow is checked here so that a matrix is never
            assembled from a parameter set that could not describe a tissue.
    """

    name: str
    volume_l: CompartmentVolume
    blood_flow_l_min: float
    tissue_blood_partition_coefficient: PartitionCoefficient

    def __post_init__(self) -> None:
        require_compartment_volume(f"{self.name} volume_l", self.volume_l)
        require_nonnegative_finite(f"{self.name} blood_flow_l_min", self.blood_flow_l_min)
        require_coefficient(
            f"{self.name} tissue_blood_partition_coefficient",
            self.tissue_blood_partition_coefficient,
        )
        _hold_as_exact_floats(self, ("blood_flow_l_min",))

    def __setstate__(self, state: object) -> None:
        """Restore an unpickled or copied record through the constructor's checks (`PL-S11T`)."""

        _restore_through_checks(self, state)

    @property
    def blood_flow_l_s(self) -> float:
        """Return $`Q_i`$ in litres per second, the unit its balance equation is written in."""

        return self.blood_flow_l_min / SECONDS_PER_MINUTE

    @property
    def washin_rate_s(self) -> float:
        """Return $`Q_i / (V_i\\lambda_{i:b})`$, the reciprocal of $`\\tau_i`$.

        `docs/MODEL.md` § "Tissue uptake and return" gives the tissue time
        constant as $`\\tau_i = V_i\\lambda_{i:b}/Q_i`$, which is undefined at
        zero flow. This property is its reciprocal, which is zero at zero flow
        instead. An unperfused tissue exchanges nothing, as the document's
        zero-flow case says. Writing the rate this way lets the matrix express
        that case without a branch.
        """

        return self.blood_flow_l_s / (self.volume_l * self.tissue_blood_partition_coefficient)


@dataclass(frozen=True, slots=True)
class UptakeEquationSettings:
    """Everything that the governing equations need and a step does not change,
    plus the vaporizer maximum that bounds the dial.

    The record is frozen and compared by value, because `uptake_system.py` uses
    it as the key under which its propagator is cached. Two steps taken under
    equal settings must reuse one propagator, and a step taken under any
    different setting must not. The key is the same object from which the
    matrix is built. That makes a stale propagator impossible to represent,
    rather than merely unlikely. A run also stores one of these records for
    each stretch of unchanged settings (`core/run_definition.py`). A stretch
    that cannot show that its dial setting was deliverable is incomplete. That
    is why the record carries one field that the matrix never reads, described
    below.

    **Flows are stored in the litres per minute to which they were set, and
    read in litres per second.** `docs/MODEL.md` § "Governing equations" writes
    every flow term per second. So each flow has a per-second property, and
    `build_system_matrix` reads only those properties. That keeps the
    conversion out of every equation. The value as set is what is stored, for
    two reasons. A run also records this object for each stretch
    (`core/run_definition.py`), and the conversion does not reverse exactly. A
    cardiac output of 1.9 L/min, divided by sixty and multiplied back, is
    1.8999999999999997, and settings rebuilt from that value differ in all
    three tissue flows (`PL-SM5V`). `docs/MODEL.md` § "Time" states which of
    the two values is the one recorded.

    **The delivered concentration is stored as the percent that was dialled,
    and read as a fraction**, for the same reason (`PL-NJPB`). The equations
    read $`F_D`$ through `delivered_partial_pressure_fraction`. A fraction
    multiplied by a hundred does not give back the percent it came from for
    126 of the 801 settings that a 0 to 8% dial makes in 0.01% steps. So a
    fraction stored here would not give back what was set. `docs/MODEL.md`
    § "Concentrations" states this rule.

    **Each flow is a checked type, so no record can store a flow outside its
    supported range** (`PL-HSFV`, `PL-0YYV`). A run is built from this record.
    A record built anywhere other than `AgentUptakeSystem.equation_settings`
    passes through no compartment. The flows used to be bare floats, and only
    the compartments checked their ranges. So a `RunDefinition` opened under a
    cardiac output of 1000 L/min and simulated it. The three flow fields take
    `FreshGasFlow`, `AlveolarVentilation` and `CardiacOutput`, which cannot be
    built outside their ranges (`core/supported_ranges.py`). So nothing here
    checks a range again, and a bare `float` is rejected as the programming
    error it is. A tissue group's flow needs no range of its own. Each tissue
    flow is nonnegative and together they sum to cardiac output, so none can
    exceed it.

    **The dial is bounded by the vaporizer maximum stored beside it**
    (`PL-BBMG`). The limit on the delivered concentration is the maximum of
    the agent's vaporizer, not a constant of the model, so no type can enforce
    it. A dial setting is deliverable only relative to a maximum, so the check
    belongs to a record that stores both. This is the point at which
    `.claude/rules/core-domain.md` stops the checked-type pattern. Until
    `PL-BBMG`, this record stored the dial alone and bounded it only at 100,
    the upper limit of every percent. So `dataclasses.replace` could rebuild a
    record at 20% sevoflurane, although the vaporizer maximum was 8%. That
    record opened a run, which returned a precise-looking trace. The record
    now carries `max_delivered_concentration_percent`, which is required and
    has no default. It rejects a dial above that maximum through
    `require_within_vaporizer_maximum`, the guard that `BreathingCircuit`
    calls, so the two reject it with the same message. The field has no
    default because `BreathingCircuit` sets its maximum to 100% by default for
    a circuit built without an agent. A record with the same default would
    reopen, under a new field, the gap that this field closes. The matrix
    never reads the maximum. `AgentUptakeSystem` copies it from the circuit
    into every record it builds. So the maximum also enters the propagator
    cache key, with the rest of the record. Both values are `Percent`s,
    checked against 0 to 100 when they were built (`core/concentration.py`).
    So this record checks their type, and does not check that range again
    (`PL-4R3W`). What it still checks is the relation between them, and that
    the maximum is above zero.

    **Each volume and the blood:gas coefficient is a checked type too**
    (`PL-QX2G`). `CompartmentVolume` and `PartitionCoefficient` are built only
    inside the numerical envelope (`core/numerical_envelope.py`). Inside it,
    every rate in `build_system_matrix` is finite, and the step's propagator
    needs at most 19 squarings. Before `PL-QX2G` the volumes were checked only
    as positive and finite. So a record could hold an alveolar volume that no
    step accepts, and the volume was refused only when the propagator was
    computed (`PL-2MD9`, `PL-3PRZ`).

    Raises:
        SimulationConfigurationError: the vaporizer maximum is zero, the
            delivered concentration is above the vaporizer maximum, the
            number of tissue groups is not the three that `patient.py`
            builds, or the tissue flows do not sum to cardiac output.
        TypeError: a flow was not built as its checked type from
            `core/supported_ranges.py`, a volume as a `CompartmentVolume`, or
            the blood:gas coefficient as a `PartitionCoefficient`
            (`core/numerical_envelope.py`). Also raised when the delivered
            concentration or the vaporizer maximum was not built as a
            `Percent` from `core/concentration.py`, or when the record was
            built without a vaporizer maximum, or when a tissue group is not a
            `TissueGroupEquationSettings`.
    """

    circuit_volume_l: CompartmentVolume
    alveolar_volume_l: CompartmentVolume
    venous_volume_l: CompartmentVolume
    fresh_gas_flow_l_min: FreshGasFlow
    alveolar_ventilation_l_min: AlveolarVentilation
    cardiac_output_l_min: CardiacOutput
    blood_gas_partition_coefficient: PartitionCoefficient
    delivered_concentration_percent: Percent
    max_delivered_concentration_percent: Percent
    tissues: tuple[TissueGroupEquationSettings, ...]

    def __post_init__(self) -> None:
        # Store `tissues` as a tuple, whatever sequence the record was built from, so that
        # every record can be a cache key (`PL-5BD7`). Every other field holds a checked
        # type, so equal values in a field always have the same type.
        object.__setattr__(self, "tissues", tuple(self.tissues))
        require_compartment_volume("circuit_volume_l", self.circuit_volume_l)
        require_compartment_volume("alveolar_volume_l", self.alveolar_volume_l)
        require_compartment_volume("venous_volume_l", self.venous_volume_l)
        require_fresh_gas_flow(self.fresh_gas_flow_l_min)
        require_alveolar_ventilation(self.alveolar_ventilation_l_min)
        require_cardiac_output(self.cardiac_output_l_min)
        require_coefficient("blood_gas_partition_coefficient", self.blood_gas_partition_coefficient)
        require_percent(
            "max_delivered_concentration_percent", self.max_delivered_concentration_percent
        )
        require_positive_finite(
            "max_delivered_concentration_percent", self.max_delivered_concentration_percent
        )
        require_percent("delivered_concentration_percent", self.delivered_concentration_percent)
        require_within_vaporizer_maximum(
            "delivered_concentration_percent",
            self.delivered_concentration_percent,
            self.max_delivered_concentration_percent,
        )
        if len(self.tissues) != TISSUE_GROUP_COUNT:
            raise SimulationConfigurationError(
                f"the model has {TISSUE_GROUP_COUNT} tissue groups but "
                f"{len(self.tissues)} were given"
            )

        # Each row's own constructor checks its volume, flow and coefficient. An object
        # of another type that only looks like a row would skip those checks, and a
        # saved state could hold one (`PL-S11T`, found at review).
        for tissue in self.tissues:
            if not isinstance(tissue, TissueGroupEquationSettings):
                raise TypeError(
                    f"each tissue group is a TissueGroupEquationSettings, not a "
                    f"{type(tissue).__name__}"
                )

        tissue_blood_flow_l_s = sum(tissue.blood_flow_l_s for tissue in self.tissues)

        if abs(tissue_blood_flow_l_s - self.cardiac_output_l_s) > (
            CARDIAC_OUTPUT_TOLERANCE_L_S
            + CARDIAC_OUTPUT_RELATIVE_TOLERANCE * self.cardiac_output_l_s
        ):
            # The message states the flows in litres per minute, the unit in
            # which they were set. Every dial, readout and other error message
            # shows a clinician that unit. The comparison stays in litres per
            # second, the unit in which the balances are written. The message
            # reaches a reader through the stopped-run banner, and when it
            # gave L/s figures, it named values that the screen never shows.
            # The sum is rounded for the message only, for the reason that
            # `TISSUE_BLOOD_FLOW_STATED_DECIMALS` gives (`PL-M4M0`).
            tissue_blood_flow_l_min = round(
                sum(tissue.blood_flow_l_min for tissue in self.tissues),
                TISSUE_BLOOD_FLOW_STATED_DECIMALS,
            )

            raise SimulationConfigurationError(
                f"the tissue groups are perfused at {tissue_blood_flow_l_min} L/min in total "
                f"but cardiac output is {self.cardiac_output_l_min} L/min; the venous balance "
                "returns what the tissues receive, so the two must agree"
            )

    def __setstate__(self, state: object) -> None:
        """Restore an unpickled or copied record through the constructor's checks (`PL-S11T`)."""

        _restore_through_checks(self, state)

    @property
    def delivered_partial_pressure_fraction(self) -> Fraction:
        """Return $`F_D`$, the delivered fraction, as the circuit balance reads it."""

        return fraction_from_percent(self.delivered_concentration_percent)

    @property
    def fresh_gas_flow_l_s(self) -> float:
        """Return $`\\dot V_F`$ in litres per second, as the circuit balance reads it."""

        return self.fresh_gas_flow_l_min / SECONDS_PER_MINUTE

    @property
    def alveolar_ventilation_l_s(self) -> float:
        """Return $`\\dot V_A`$ in litres per second, as the gas-phase balances read it."""

        return self.alveolar_ventilation_l_min / SECONDS_PER_MINUTE

    @property
    def cardiac_output_l_s(self) -> float:
        """Return $`Q`$ in litres per second, as the alveolar and venous balances read it."""

        return self.cardiac_output_l_min / SECONDS_PER_MINUTE


def build_system_matrix(settings: UptakeEquationSettings) -> Matrix:
    """Assemble $`A`$, so that $`\\exp(A\\Delta t)`$ advances the model exactly.

    Each block below is one equation of `docs/MODEL.md` § "Governing
    equations", written in that document's own order and symbols. The comment
    above each block is the equation, and each line under the comment writes
    one of its terms as one matrix entry. `docs/MODEL.md` § "Selected method
    (as implemented)" describes the step for which this matrix is assembled,
    and names this module as the source of $`A`$.

    Both citations use the section-mark form, and quote the section title
    exactly. `tools/doc_check.py` looks for that text in the named file. So
    renaming the section fails the check, instead of silently leaving the
    citation pointing at nothing (`PL-VZL0`, `PL-V13T`, `PL-316G`).

    Every off-diagonal entry is a transfer rate and is nonnegative. Every
    diagonal entry is minus the total rate leaving that state. That makes the
    result a Metzler matrix. `matrix_exponential.matrix_exponential` requires
    that property, and it is the reason that the propagator cannot drive a
    compartment negative.

    Zero flow needs no special case anywhere here. A rate of zero is an entry
    of zero, and the exact propagator of a system with a zero rate transfers
    nothing along that path. That is what `docs/MODEL.md` requires at zero
    ventilation, zero cardiac output and zero tissue flow. The previous
    implementation needed three early returns to express it.
    """

    matrix = [[0.0] * STATE_SIZE for _ in range(STATE_SIZE)]

    fresh_gas_l_s = settings.fresh_gas_flow_l_s
    ventilation_l_s = settings.alveolar_ventilation_l_s
    cardiac_output_l_s = settings.cardiac_output_l_s
    blood_gas = settings.blood_gas_partition_coefficient
    # Short local names here are the convention rather than an omission, and
    # `delivered_fraction` is deliberately one of them (`PL-BDNB`). Each matrix
    # row below sits under a comment that writes the equation in the
    # specification's own symbols. So the reader sees $`F_D`$ at the row, and
    # does not have to carry this name down the module. The full name
    # `delivered_partial_pressure_fraction` would also make the two rows that
    # read it wrap onto a second line. `.claude/rules/core-domain.md` decides
    # that case against the long name: where a naming choice makes the model
    # harder to see, the model wins.
    delivered_fraction = settings.delivered_partial_pressure_fraction

    pulmonary_blood_flow_l_s = cardiac_output_l_s * blood_gas

    # Breathing circuit, the inspired fraction:
    #     dF_I/dt = (V_F/V_C)(F_D - F_I) - (V_A/V_C)(F_I - F_A)
    circuit_volume_l = settings.circuit_volume_l
    matrix[INSPIRED_FRACTION][INSPIRED_FRACTION] = (
        -(fresh_gas_l_s + ventilation_l_s) / circuit_volume_l
    )
    matrix[INSPIRED_FRACTION][ALVEOLAR_FRACTION] = ventilation_l_s / circuit_volume_l
    matrix[INSPIRED_FRACTION][UNIT_STATE] = fresh_gas_l_s * delivered_fraction / circuit_volume_l

    # Alveolar gas:
    #     dF_A/dt = [ V_A(F_I - F_A) - Q*lambda_bg(F_A - F_v) ] / V_A
    #
    # The pulmonary uptake rate that docs/MODEL.md specifies,
    # Q*lambda_bg(F_A - F_v), is the second and third entries of this row. The
    # operator split never formed it at all (PL-Y5BV).
    alveolar_volume_l = settings.alveolar_volume_l
    matrix[ALVEOLAR_FRACTION][INSPIRED_FRACTION] = ventilation_l_s / alveolar_volume_l
    matrix[ALVEOLAR_FRACTION][ALVEOLAR_FRACTION] = (
        -(ventilation_l_s + pulmonary_blood_flow_l_s) / alveolar_volume_l
    )
    matrix[ALVEOLAR_FRACTION][VENOUS_FRACTION] = pulmonary_blood_flow_l_s / alveolar_volume_l

    # Venous blood:
    #     dF_v/dt = ( sum_i Q_i F_i - Q F_v ) / V_v
    venous_volume_l = settings.venous_volume_l
    matrix[VENOUS_FRACTION][VENOUS_FRACTION] = -cardiac_output_l_s / venous_volume_l

    # Tissue uptake and return, for each group i:
    #     dF_i/dt = Q_i / (V_i lambda_ib) * (F_A - F_i)
    #
    # Arterial blood is flow-limited, so F_a is F_A and the driving fraction is
    # read from the alveolar state directly.
    for offset, tissue in enumerate(settings.tissues):
        state = FIRST_TISSUE_FRACTION + offset
        washin_rate_s = tissue.washin_rate_s

        matrix[state][ALVEOLAR_FRACTION] = washin_rate_s
        matrix[state][state] = -washin_rate_s

        # ...and this group's contribution to the venous balance above.
        matrix[VENOUS_FRACTION][state] = tissue.blood_flow_l_s / venous_volume_l

    # External delivery:
    #     dM_delivered/dt = V_F * F_D
    matrix[DELIVERED_AGENT_L][UNIT_STATE] = fresh_gas_l_s * delivered_fraction

    # Circuit exhaust, which leaves at the current mixed-circuit fraction:
    #     dM_exhausted/dt = V_F * F_I
    matrix[EXHAUSTED_AGENT_L][INSPIRED_FRACTION] = fresh_gas_l_s

    # The unit state's row stays empty: the constant does not evolve.

    return tuple(tuple(row) for row in matrix)
