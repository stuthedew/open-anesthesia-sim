"""The governing equations of `docs/MODEL.md`, assembled as one system matrix.

This file is a transcription and nothing else. Every entry `build_system_matrix`
writes is one term of one balance equation in that document's "Governing
equations" section, and the entries are written in the order the document
states them, so a reader who knows the standard variables can check the model
against the code without a lookup table between them. The arithmetic that
solves the system is in `matrix_exponential.py`; it carries no physiology, and
this file carries no numerics.

## Why the whole system is one matrix

Every setting is held constant across a simulation step, so within that step
the six compartment fractions obey a linear, time-invariant system

$$
\\frac{dy}{dt} = Ay + b .
$$

Carrying the constant $`b`$ against one extra state whose value is always 1
turns the affine system into a linear one, $`dy/dt = Ay`$, and then
$`\\exp(A\\,\\Delta t)`$ is its **exact** propagator, at any step size. So
assembling $`A`$ is the whole of the model, and nothing downstream of it
approximates anything.

That is the property this module exists for. The operator split it replaced
solved five pairwise exchanges exactly and composed them in sequence, which is
first-order accurate in the step rather than exact, and - the reason it was
replaced - spread the alveolar balance's two terms across two non-adjacent
sub-steps and never formed the pulmonary uptake term at all. Here that balance
is one row, and its two terms are two entries of it.

## The state vector

Six of the nine states are the modelled fractions, in the order
`docs/MODEL.md` introduces them: inspired gas, alveolar gas, mixed venous
blood, then the three tissue groups. Two more accumulate the agent crossing
the system boundary, and the last is the constant.

$`F_I`$ is the fraction in the breathing circuit. The literature's gas-phase
cascade is $`F_D \\rightarrow F_I \\rightarrow F_A`$ - delivered, inspired,
alveolar - and under this model's boundary (one ideal, perfectly mixed
circuit; no dead space; no separate inspiratory and expiratory limbs) the gas
the patient inspires *is* the circuit gas, so the circuit's fraction and the
inspired fraction are identically the same quantity. The state is named for
the clinical quantity rather than for its container, because $`F_A/F_I`$ is
the curve this simulator exists to let a learner produce; the container is
still the circuit, and `circuit.py` still owns it.

## Why delivered and exhausted agent are states rather than a side calculation

`docs/MODEL.md`'s mass-balance identity is

    initial agent + delivered agent = exhausted agent + currently stored agent

and it is checked after every step, at a tolerance tight enough to halt a run.
Delivered agent is $`\\dot V_F F_D \\Delta t`$, which needs no help. Exhausted
agent is $`\\dot V_F \\int F_I \\, dt`$, and $`F_I`$ follows the coupled
trajectory, so that integral has no closed form of its own - the previous
implementation used the integral of a *circuit-alone* wash-in, which was
consistent with the sub-step that produced it and would not be consistent with
anything here.

Carried as a state, the integral is exact for the same reason the fractions
are, and the accounting residual then sits at rounding rather than at the
numerical method's error. Two rows, `docs/MODEL.md` § "External delivery" and
"Circuit exhaust" equations respectively, and each reads as such.

**The two remaining reported transfers are recovered rather than accumulated,
and deliberately.** A net ventilatory transfer and a net pulmonary uptake are
*signed* - agent returns from blood to alveolar gas during washout - so rows
for them would carry negative off-diagonal entries, which is precisely the
Metzler property `matrix_exponential.py` needs in order to guarantee that no
compartment is driven negative. Both fall out of the balances instead, with no
approximation: pulmonary uptake over a step is the change in stored patient
agent, and the ventilatory transfer is that plus the change in stored alveolar
agent, because $`\\Delta M_A`$ is the difference of the two by the alveolar
equation itself. `uptake_system.py` forms them there.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from anesthesia_sim.core.concentration import Fraction, Percent, fraction_from_percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.matrix_exponential import Matrix
from anesthesia_sim.core.supported_ranges import (
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
    require_percent,
    require_positive_finite,
)

INSPIRED_FRACTION = 0
"""$`F_I`$, the breathing circuit's fraction, which is what the patient inspires."""

ALVEOLAR_FRACTION = 1
"""$`F_A`$, the alveolar gas fraction. Arterial blood equilibrates with it."""

VENOUS_FRACTION = 2
"""$`F_v`$, the mixed venous partial-pressure-equivalent fraction."""

FIRST_TISSUE_FRACTION = 3
"""$`F_i`$ for the first tissue group; the groups occupy consecutive states."""

DELIVERED_AGENT_L = 6
"""Cumulative agent delivered from the vaporizer over the propagated interval."""

EXHAUSTED_AGENT_L = 7
"""Cumulative agent leaving through the circuit exhaust over that interval."""

UNIT_STATE = 8
"""The constant 1, which turns `dy/dt = Ay + b` into `dy/dt = Ay`.

Its row is empty, so it is constant by construction rather than by convention,
and no step can perturb the forcing term the other rows read from it. That
holds in floating point as well as in the algebra, because `matrix_exponential`
writes an empty row's propagator row as the identity's before its squarings,
which then keep it to the last bit; the shift that makes the propagator
nonnegative had returned it as $`1+\\delta`$, raised by the squarings to
$`(1+\\delta)^{2^{s}}`$ (`PL-2MD9`). Every propagator the module returns
carries it, since one needing more squarings than `MAXIMUM_SQUARINGS` is
refused rather than returned.
"""

STATE_SIZE = 9
"""How many states the propagator carries."""

TISSUE_GROUP_COUNT = 3
"""Vessel-rich, muscle and fat: the three groups `patient.py` builds."""

CARDIAC_OUTPUT_TOLERANCE_L_S = 1e-12
CARDIAC_OUTPUT_RELATIVE_TOLERANCE = 1e-9
"""How far the tissue flows may sum away from cardiac output.

Blood leaving the tissue groups is the whole of what returns to the venous
pool: `docs/MODEL.md`'s venous balance is
$`dF_v/dt = (\\sum_i Q_i F_i - QF_v)/V_v`$, so a $`\\sum_i Q_i`$ that did not
equal $`Q`$ would put agent into that pool at one rate and take it out at
another, and the model would create or destroy agent at a steady rate for as
long as the mismatch stood.

`patient.py` already requires the perfusion *fractions* to sum to one, which
is the same statement about the same quantity. It is checked again here
because these settings are assembled separately from those compartments and
this is the object the equations are actually built from - a check that lives
one call away from the arithmetic it protects, rather than in the class that
usually supplies it. The absolute floor is what lets a zero cardiac output
pass, which `docs/MODEL.md` § "Supported input ranges" requires.
"""


def require_canonical_state(state: object) -> None:
    """Refuse a state vector the equations could not be read against.

    The entry guard every sink that opens from a state a run passed through
    shares - a `RunDefinition`, and the live system a branch resumes into -
    so that the two cannot come to disagree about what a state is. It lives
    here because each condition below is a statement about the state vector
    this module defines rather than about either caller.

    **The first refusal is structural, not by type name.** A drawn value
    carries the same nine numbers in the same order as a canonical one, so
    nothing about its contents distinguishes them; what does is that the
    display path wraps its answers in something that is not a tuple.
    `docs/MODEL.md` § "The canonical evaluation rule" argues for exactly this
    test - only a value that is structurally not a state is refused by a sink
    that thought to check nothing - and a structural test holds for wrappers
    this module has never heard of. `core/run_definition.py` names
    `DisplayState` before delegating here, because it is the module that can;
    the message below is what a sink outside that module can still say.

    `state` is typed as `object` rather than as the tuple, deliberately. The
    values this refuses are exactly the ones a caller believed were states,
    so a signature that could only be given a state would put the check
    somewhere it can never fire.

    Raises:
        SimulationConfigurationError: `state` is not a tuple, is not
            `STATE_SIZE` long, holds a non-finite value, or does not carry
            exactly one in `UNIT_STATE`. The last is what makes every forcing
            term in `build_system_matrix` mean what it says: a state carrying
            anything else there would scale the whole of the delivery term
            without changing any setting a reader can see.
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

    if state[UNIT_STATE] != 1.0:
        raise SimulationConfigurationError(
            f"state[{UNIT_STATE}] is the constant one the forcing terms are read against, "
            f"not {state[UNIT_STATE]}"
        )


@dataclass(frozen=True, slots=True)
class TissueGroupEquationSettings:
    """One tissue group's parameters, as its balance equation needs them.

    The blood flow is held in litres per minute and read in litres per second,
    for the reason `UptakeEquationSettings` gives for its own flows.

    Raises:
        SimulationConfigurationError: any value is outside its domain - the
            volume and the partition coefficient must be positive and finite,
            and the blood flow nonnegative and finite. Checked here so that a
            matrix is never assembled from a parameter set that could not
            describe a tissue.
    """

    name: str
    volume_l: float
    blood_flow_l_min: float
    tissue_blood_partition_coefficient: float

    def __post_init__(self) -> None:
        require_positive_finite(f"{self.name} volume_l", self.volume_l)
        require_nonnegative_finite(f"{self.name} blood_flow_l_min", self.blood_flow_l_min)
        require_positive_finite(
            f"{self.name} tissue_blood_partition_coefficient",
            self.tissue_blood_partition_coefficient,
        )

    @property
    def blood_flow_l_s(self) -> float:
        """Return $`Q_i`$ in litres per second, the unit its balance equation is written in."""

        return self.blood_flow_l_min / SECONDS_PER_MINUTE

    @property
    def washin_rate_s(self) -> float:
        """Return $`Q_i / (V_i\\lambda_{i:b})`$, the reciprocal of $`\\tau_i`$.

        `docs/MODEL.md` § "Tissue uptake and return" gives the tissue time
        constant as $`\\tau_i = V_i\\lambda_{i:b}/Q_i`$, undefined at zero flow. This is
        its reciprocal, which is zero there instead - an unperfused tissue
        exchanges nothing, which is what the document's zero-flow case says,
        and expressing it this way is what lets the matrix state that case
        without a branch.
        """

        return self.blood_flow_l_s / (self.volume_l * self.tissue_blood_partition_coefficient)


@dataclass(frozen=True, slots=True)
class UptakeEquationSettings:
    """Everything the governing equations need that a step does not change.

    Frozen and compared by value, because `uptake_system.py` uses it as the
    key its propagator is cached against: two steps taken under equal settings
    must reuse one propagator, and a step taken under any different setting
    must not. Deriving the key from the same object the matrix is built from is
    what makes a stale propagator unrepresentable rather than merely unlikely.

    **Flows are held in the litres per minute they were set to, and read in
    litres per second.** `docs/MODEL.md` § "Governing equations" writes every
    flow term per second, so each flow has a per-second property and
    `build_system_matrix` reads only those, which keeps the conversion out of
    every equation. The value as set is what is stored because this object is
    also what a run records, one per stretch (`core/run_definition.py`), and
    the conversion does not run backwards: a cardiac output of 1.9 L/min,
    divided by sixty and multiplied back, is 1.8999999999999997, and settings
    rebuilt from that differ in all three tissue flows (`PL-SM5V`).
    `docs/MODEL.md` § "Time" states which of the two is the record.

    **The delivered concentration is held in the percent it was dialled, and
    read as a fraction**, for the same reason (`PL-NJPB`). The equations read
    $`F_D`$ through `delivered_partial_pressure_fraction`, and a fraction times
    a hundred misses the percent it came from for 126 of the 801 settings a 0
    to 8% dial makes at 0.01% steps, so a fraction stored here would not give
    back what was set. `docs/MODEL.md` § "Concentrations" states it.

    **Each flow is a checked type, so no record can hold one outside its
    supported range** (`PL-HSFV`, `PL-0YYV`). A run is built from this record,
    and a record built anywhere but `AgentUptakeSystem.equation_settings`
    passes through no compartment, so while the flows were bare floats
    range-checked by each compartment a `RunDefinition` opened under a cardiac
    output of 1000 L/min and simulated it. The three flow fields take
    `FreshGasFlow`, `AlveolarVentilation` and `CardiacOutput`, which cannot be
    built outside their ranges (`core/supported_ranges.py`), so nothing here
    checks a range again, and a bare `float` is refused as the programming
    error it is. A tissue group's flow needs no range of its own: each is
    nonnegative and together they sum to cardiac output, so none can exceed
    it. The delivered concentration is bounded at 100% and no lower, because
    its limit is the agent's vaporizer maximum, which this record does not
    carry (`PL-BBMG`).

    Raises:
        SimulationConfigurationError: a volume or the blood:gas partition
            coefficient is not positive and finite, the delivered
            concentration is not a percent in [0, 100], the number of tissue
            groups is not the three `patient.py` builds, or the tissue flows
            do not sum to cardiac output.
        TypeError: a flow was not built as its checked type, in
            `core/supported_ranges.py`.
    """

    circuit_volume_l: float
    alveolar_volume_l: float
    venous_volume_l: float
    fresh_gas_flow_l_min: FreshGasFlow
    alveolar_ventilation_l_min: AlveolarVentilation
    cardiac_output_l_min: CardiacOutput
    blood_gas_partition_coefficient: float
    delivered_concentration_percent: Percent
    tissues: tuple[TissueGroupEquationSettings, ...]

    def __post_init__(self) -> None:
        require_positive_finite("circuit_volume_l", self.circuit_volume_l)
        require_positive_finite("alveolar_volume_l", self.alveolar_volume_l)
        require_positive_finite("venous_volume_l", self.venous_volume_l)
        require_fresh_gas_flow(self.fresh_gas_flow_l_min)
        require_alveolar_ventilation(self.alveolar_ventilation_l_min)
        require_cardiac_output(self.cardiac_output_l_min)
        require_positive_finite(
            "blood_gas_partition_coefficient", self.blood_gas_partition_coefficient
        )
        require_percent("delivered_concentration_percent", self.delivered_concentration_percent)

        if len(self.tissues) != TISSUE_GROUP_COUNT:
            raise SimulationConfigurationError(
                f"the model has {TISSUE_GROUP_COUNT} tissue groups but "
                f"{len(self.tissues)} were given"
            )

        tissue_blood_flow_l_s = sum(tissue.blood_flow_l_s for tissue in self.tissues)

        if abs(tissue_blood_flow_l_s - self.cardiac_output_l_s) > (
            CARDIAC_OUTPUT_TOLERANCE_L_S
            + CARDIAC_OUTPUT_RELATIVE_TOLERANCE * self.cardiac_output_l_s
        ):
            raise SimulationConfigurationError(
                f"the tissue groups are perfused at {tissue_blood_flow_l_s} L/s in total "
                f"but cardiac output is {self.cardiac_output_l_s} L/s; the venous balance "
                "returns what the tissues receive, so the two must agree"
            )

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
    above each is the equation; the lines under it are its terms, one entry
    each. `docs/MODEL.md` § "Selected method (as implemented)" is the step this
    matrix is assembled for, and names this module as where $`A`$ comes from.

    Both citations are in the section-mark form, and quote the section title
    verbatim: `tools/doc_check.py` looks for that text in the file named, so a
    rename fails the gate instead of silently orphaning the pointer
    (`PL-VZL0`, `PL-V13T`, `PL-316G`).

    Every off-diagonal entry is a transfer rate and is nonnegative; every
    diagonal is minus the total rate leaving that state. That makes the result
    a Metzler matrix, which is the precondition
    `matrix_exponential.matrix_exponential` requires and the reason its
    propagator cannot drive a compartment negative.

    Zero flow needs no special case anywhere here. A rate of zero is an entry
    of zero, and the exact propagator of a system with a zero rate is the one
    that transfers nothing along it - which is what `docs/MODEL.md` requires at
    zero ventilation, zero cardiac output and zero tissue flow, and which the
    previous implementation needed three early returns to express.
    """

    matrix = [[0.0] * STATE_SIZE for _ in range(STATE_SIZE)]

    fresh_gas_l_s = settings.fresh_gas_flow_l_s
    ventilation_l_s = settings.alveolar_ventilation_l_s
    cardiac_output_l_s = settings.cardiac_output_l_s
    blood_gas = settings.blood_gas_partition_coefficient
    # Short locals here are the convention rather than an omission, and
    # `delivered_fraction` is deliberately among them (`PL-BDNB`). Each matrix
    # row below sits under a comment writing the equation in the
    # specification's own symbols, so the reader has $`F_D`$ in view at the row
    # rather than carrying this binding down the module; and the full
    # `delivered_partial_pressure_fraction` would wrap the two rows that read
    # it, which is the case `.claude/rules/core-domain.md` settles the other
    # way — where a naming choice makes the model harder to see, the model wins.
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
    # The pulmonary uptake rate docs/MODEL.md specifies, Q*lambda_bg(F_A - F_v),
    # is the second and third entries of this row. It was never formed at all
    # under the operator split (PL-Y5BV).
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
