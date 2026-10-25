"""The breathing circuit, modelled as an ideal, well-mixed gas volume.

The circuit receives fresh gas at a set delivered concentration. On every step
it exchanges agent with the alveolar compartment (`alveolar.py`).

"Ideal" means that the walls do nothing. Agent enters with the fresh gas and
leaves with the exhaust, and no plastic or rubber component holds any of it.
In a real circuit the components do hold agent. The amount is measurable, and
it follows the order of the agents' solubility. So this simplification is
closest to true for desflurane and furthest from true for halothane.
`docs/MODEL.md` "Known limitations" gives the measurement and the reason the
simplification is kept (`PL-LS3H`).

The circuit also owns the vaporizer delivery limit
(`max_delivered_concentration_percent`), because it owns the delivered
concentration itself. Enforcing the limit here means that every path that can
change the delivered concentration (core, controller or UI) is bounded by the
same guard. No path relies on the presentation layer to bound it. A run is
built from `UptakeEquationSettings` rather than from the circuit. So
`UptakeEquationSettings` carries the same maximum beside its dial setting, and
it rejects a setting above the maximum through the same guard,
`require_within_vaporizer_maximum` in `core/validation.py` (`PL-BBMG`). Fresh
gas flow is bounded here for the same reason, against the model's own
supported range in `core/supported_ranges.py`.

**Fresh gas flow has two bounds, and they make two different claims**
(`PL-8PS6`). `core/supported_ranges.py` declares the range of flows over which
the compartment model is claimed to represent a patient. This module calls that
range the model's envelope. A machine profile declares the range of flows that
the machine's flowmeters can physically set (`deliverable_fresh_gas_flow_range`,
which is `None` where the profile declares none). The effective limit is the
intersection of the two ranges, and each bound rejects a flow in its own name.
The bounds are kept separate for two reasons. A machine whose flowmeter runs to
15 L/min must not widen the range over which anything was verified. A machine
that will not go below 0.5 L/min must not raise the model's lower bound for
every other machine. `BreathingCircuit.accepted_fresh_gas_flow_range_l_min`
states the intersection in one place, and the interface's fresh gas flow
control offers the range that this property states (`PL-7CRY`).
"""

from dataclasses import dataclass, field
from math import expm1, inf
from typing import TYPE_CHECKING

from anesthesia_sim.core.checked_number import shown
from anesthesia_sim.core.concentration import (
    Fraction,
    Percent,
    fraction_from_percent,
    require_fraction,
    require_percent,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.numerical_envelope import CompartmentVolume, require_compartment_volume
from anesthesia_sim.core.simulation_step import require_at_least_the_smallest_step
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
    FreshGasFlow,
    require_fresh_gas_flow,
)
from anesthesia_sim.core.units import SECONDS_PER_MINUTE
from anesthesia_sim.core.validation import (
    require_nonnegative_finite,
    require_positive_finite,
    require_room_for_the_agent_held,
    require_within_the_capacity,
    require_within_vaporizer_maximum,
)

TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN = FreshGasFlow(4.0)
"""The fresh gas flow a run opens at when its machine profile states none.

This value is a teaching default. It is not a clinical recommendation, and it is
not a property of any machine. No surveyed workstation publishes a startup
fresh gas flow (`docs/machine-survey.md` § "(a2) Default fresh gas flow"). So
`default_fresh_gas_flow_l_min` is optional in a `data/machines/` profile.
`docs/machine-abstraction.md` § "Three homes, and why the shipped constants
move" decides that the opening flow is a condition of the run rather than of
the machine (`PL-QW19`). `AgentUptakeSystem.for_agent()` opens a run at this
flow when the profile is silent.

No source is this value's authority. Its authority is the rationale that
`data/machines/reference_circle_system.json` records in its `provenance_gap`
for storing the same value: the value was chosen so that a learner sees the
machine lag as a distinct phase of the early rise. `docs/MODEL.md` carries the
provenance row for this value. `test_the_flow_default_matches_the_shipped_machine_file`
in `tests/unit/test_circuit.py` fails if this value and the file's value ever
differ.
"""


@dataclass(frozen=True, slots=True)
class DeliverableFreshGasFlowRange:
    """The fresh gas flows that one anesthesia machine can actually set.

    This range is a property of the machine, not of the model. It is what the
    machine's flowmeters, its minimum-flow limit and its fresh gas delivery
    allow, read from a validated machine profile under `data/machines/`. The
    range over which the *model* is claimed to hold is a different statement,
    and it lives in `core/supported_ranges.py`. The two are kept apart
    deliberately. `PL-8PS6` is the finding, and the module docstring above says
    what merging them would cost.

    Both ends are inclusive, matching every interval that
    `core/supported_ranges.py` declares. So a machine's own lowest and highest
    flows are settings it can reach, not the first values it rejects.

    Raises:
        SimulationConfigurationError: an end is not finite, the minimum is
            negative, or the minimum is above the maximum. A machine cannot
            deliver a negative flow, and an inverted range would reject every
            setting while looking like a declared capability.
    """

    minimum_l_min: float
    maximum_l_min: float

    def __post_init__(self) -> None:
        require_nonnegative_finite("minimum_l_min", self.minimum_l_min)
        require_nonnegative_finite("maximum_l_min", self.maximum_l_min)

        if self.minimum_l_min > self.maximum_l_min:
            raise SimulationConfigurationError(
                "deliverable_fresh_gas_flow_range has a minimum above its maximum "
                f"({self.minimum_l_min} L/min minimum, {self.maximum_l_min} L/min maximum)"
            )


def _accepted_fresh_gas_flow_range_l_min(
    machine_range: DeliverableFreshGasFlowRange | None,
) -> tuple[float, float]:
    """Return the model's envelope narrowed to `machine_range`, or the envelope if it is `None`.

    `BreathingCircuit.accepted_fresh_gas_flow_range_l_min` calls this function
    for the range that the circuit holds. `_require_the_two_flow_claims_overlap`
    calls it for a range that is about to be written. So the intersection is
    computed in one place.
    """

    if machine_range is None:
        return (MINIMUM_FRESH_GAS_FLOW_L_MIN, MAXIMUM_FRESH_GAS_FLOW_L_MIN)

    return (
        max(MINIMUM_FRESH_GAS_FLOW_L_MIN, machine_range.minimum_l_min),
        min(MAXIMUM_FRESH_GAS_FLOW_L_MIN, machine_range.maximum_l_min),
    )


def _require_a_machine_range(machine_range: object) -> None:
    """Reject a machine range that is not `None` or a `DeliverableFreshGasFlowRange`.

    The range's constructor checks its two ends. So holding a range of that
    type proves that its ends were checked, as holding a `Percent` proves that
    a dial setting was checked. Until `PL-19Y0`, anything else (a tuple of the
    two flows, for example) was rejected only when the first attribute read on
    it failed, with Python's error message rather than the simulator's.

    Raises:
        TypeError: `machine_range` is neither `None` nor a
            `DeliverableFreshGasFlowRange`. This is a programming error in the
            caller rather than a rejected setting, as `require_a_number`
            explains (`core/checked_number.py`).
    """

    if machine_range is not None and not isinstance(machine_range, DeliverableFreshGasFlowRange):
        raise TypeError(
            f"deliverable_fresh_gas_flow_range of {shown(machine_range)} has type "
            f"{type(machine_range).__name__}, not DeliverableFreshGasFlowRange or None: build "
            "it from the machine profile's two flows, which its constructor checks "
            "(core/circuit.py)"
        )


def _require_the_two_flow_claims_overlap(
    machine_range: DeliverableFreshGasFlowRange | None,
) -> None:
    """Reject a machine that can deliver no flow inside the model's envelope.

    The check is made wherever the range is written, including the
    constructor's write. So the problem is found at once, not one rejected
    setting at a time. Consider a profile whose flowmeters start above
    `MAXIMUM_FRESH_GAS_FLOW_L_MIN`. It cannot be simulated at all. Every flow it
    can set is outside the model's envelope, and every flow the model supports
    is outside the machine's range. Each separate rejection would be correct,
    but none of them would say that the pair of ranges is the problem. The test
    is whether the intersection (`_accepted_fresh_gas_flow_range_l_min`) is
    empty, so the intersection rule is written in one place.

    Raises:
        SimulationConfigurationError: the machine's declared range and the
            model's envelope do not overlap. Nothing is written.
    """

    if machine_range is None:
        return

    lowest_accepted, highest_accepted = _accepted_fresh_gas_flow_range_l_min(machine_range)

    if lowest_accepted > highest_accepted:
        raise SimulationConfigurationError(
            "this machine can deliver no fresh gas flow the model is claimed over: "
            f"it delivers {machine_range.minimum_l_min} to "
            f"{machine_range.maximum_l_min} L/min and the model supports "
            f"{MINIMUM_FRESH_GAS_FLOW_L_MIN} to {MAXIMUM_FRESH_GAS_FLOW_L_MIN} L/min "
            f'(docs/MODEL.md, "Supported input ranges")'
        )


def _require_deliverable_flow(
    fresh_gas_flow_l_min: FreshGasFlow, machine_range: DeliverableFreshGasFlowRange | None
) -> None:
    """Reject a fresh gas flow that the machine in front of the patient cannot set.

    This is the second of the two bounds on the flow control. The flow has
    already passed the first: a `FreshGasFlow` was checked against the
    *model's* envelope when it was built, and this function checks the
    *machine's* range. The two bounds are enforced separately, and each rejects
    a flow in its own words, so that a reader of the error can tell which claim
    was violated. A flow this machine cannot reach is a fact about the device.
    A flow outside the envelope means that the model is not claimed to
    represent a patient at that flow. Merging the bounds would let a machine
    with a wider flowmeter silently widen the model's envelope (`PL-8PS6`).

    A profile that declares no range sets no bound here, which is the shipped
    behavior. `reference_circle_system` records the range as unknown rather
    than as a number, so the envelope alone applies, exactly as it did before
    this field existed.

    The function rejects the flow rather than clamping it, for the reason that
    `require_within_vaporizer_maximum` gives in `core/validation.py`. A
    silently clamped flow would be simulated, displayed and charted at a value
    the caller did not ask for.

    Raises:
        SimulationConfigurationError: the flow is outside the machine's
            declared deliverable range. Nothing is written.
    """

    if machine_range is None:
        return

    if not machine_range.minimum_l_min <= fresh_gas_flow_l_min <= machine_range.maximum_l_min:
        raise SimulationConfigurationError(
            f"fresh_gas_flow_l_min of {fresh_gas_flow_l_min} is outside what this "
            f"machine can deliver, {machine_range.minimum_l_min} to "
            f"{machine_range.maximum_l_min} L/min; the model's supported input range "
            f"of {MINIMUM_FRESH_GAS_FLOW_L_MIN} to {MAXIMUM_FRESH_GAS_FLOW_L_MIN} L/min "
            f"is not what refused it (the machine's range is declared in its "
            f"data/machines/ profile, the model's in docs/MODEL.md, "
            f'"Supported input ranges")'
        )


@dataclass(frozen=True, slots=True)
class FreshGasExchange:
    """The agent that enters with fresh gas and leaves with the exhaust in one step."""

    delivered_agent_l: float
    exhausted_agent_l: float


@dataclass(frozen=True, slots=True)
class BreathingCircuitState:
    """The circuit's run state: the values that one simulation step can change.

    Circuit volume, fresh gas flow, the vaporizer dial and its maximum are
    deliberately left out, and so is the machine's deliverable flow range. The
    user owns these settings, and the range is a property of the machine in
    front of the patient. None of them is state that the trajectory carries. No
    step writes them, and a rollback that restored them would silently undo a
    setting that had been accepted.

    The record captures the fraction rather than the amount, and that choice
    depends on the volume staying fixed. Since PL-006, `set_circuit_volume()`
    conserves agent by rewriting the fraction, so the fraction and the amount
    agree only while the volume is fixed. They agree here, because no step
    changes the volume. If a step ever did change it (a bellows model, for
    example), the record would have to capture the volume too. Otherwise the
    restored fraction would put back a different amount of agent than the step
    started with.

    The record checks the fraction's type when it is built. So
    `BreathingCircuit.restore_state()`, which must not raise, is never handed a
    fraction that `set_inspired_partial_pressure_fraction()` would reject
    (`PL-4R3W`).

    Raises:
        TypeError: the fraction was not built as a `Fraction`, the type that
            checks it against 0 to 1 (`core/concentration.py`).
    """

    inspired_partial_pressure_fraction: Fraction

    def __post_init__(self) -> None:
        require_fraction(
            "inspired_partial_pressure_fraction", self.inspired_partial_pressure_fraction
        )


@dataclass(slots=True)
class BreathingCircuit:
    """Ideal, well-mixed breathing circuit with constant volume.

    The circuit's volume and its vaporizer maximum have no default, so every
    caller must state the values it means (`PL-M85T`). The other defaults do
    not depend on the agent. Agent-independent values are the only ones that a
    class holding no agent parameters can honestly claim to know. A circuit is
    built empty, at 4 L/min, with the vaporizer off. Zero is the one dial
    position that every vaporizer of every agent has. So it is the only
    delivered concentration this class can supply without borrowing some
    particular agent's number (PL-019).

    **`data/machines/reference_circle_system.json` is the authority for the
    volume and the flow, and this class is not.** Every shipped path builds the
    circuit through `AgentUptakeSystem.for_agent()`. That method passes the
    volume from the machine profile, and passes the flow from the profile when
    the profile states one. Until `PL-M85T`, the volume defaulted to 6.0 L. That
    default was a second copy of the file's value, and only a test kept the two
    equal (`PL-4YY1`). The flow default is `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`.
    `for_agent()` also opens a run at that flow when the profile states no
    startup flow (`PL-QW19`). `test_the_flow_default_matches_the_shipped_machine_file`
    in `tests/unit/test_circuit.py` fails if that default and the file ever
    disagree. The file also records why it keeps 6.0 L where the published Gas
    Man convention is 8 L. It also records that the 4 L/min has no published
    counterpart at all.

    `fresh_gas_flow_l_min` is the flow at the common gas outlet: the carrier
    gas plus the vapour that the vaporizer added. It is not the flowmeter
    setting, although a user may read it as one. The two differ by a factor of
    1/(1 - `delivered_partial_pressure_fraction`), which is 22% at
    desflurane's 18% dial maximum. `advance_fresh_gas()` uses this one field
    both as the rate at which agent arrives and as the rate at which mixed
    circuit gas leaves. Only the post-vaporizer total balances those two
    rates, so the field must hold that total. See `docs/MODEL.md`, "Breathing
    circuit".

    **The dial is stored as the percent it was set to, and the fraction is
    derived from it** (`PL-NJPB`). `delivered_concentration_percent` is the
    stored record. `delivered_partial_pressure_fraction`, which the governing
    equations use, is computed as `fraction_from_percent` of it on every read.
    If the fraction were stored instead, the setting could not be recovered as
    dialled. In binary floating point, a fraction times a hundred does not
    return the percent it came from for 126 of the 801 settings that a 0 to 8%
    dial makes in 0.01% steps. For example, 0.9% reads back as
    0.9000000000000001. The equations lose nothing, because the one division
    that the interface used to make is now made here. `PL-SM5V` chose the same
    rule for the flows, which are stored in L/min and used by the equations in
    L/s.

    `max_delivered_concentration_percent` is the vaporizer's calibrated
    dial maximum for the agent in use, in the unit of the dial it bounds. It
    has no default (`PL-M85T`). Before `PL-M85T`, it defaulted to 100%, which
    no agent's vaporizer delivers, so a circuit built without it accepted any
    dial setting. Every agent-aware path builds the circuit through
    `AgentUptakeSystem.for_agent()`. That method sets both the real limit and
    that agent's own starting dial from the agent data file. A test of circuit
    physics that wants no device limit passes 100% itself. With that maximum,
    a dial set to 100% can give a computed fraction one rounding error above 1.
    `Fraction` rejects that value when it is built, and `core/concentration.py`
    records this as the type's limit (`PL-4R3W`).

    `__setattr__` checks every field each time it is written, including the
    writes the constructor makes. So an assignment that bypasses the
    constructor and the setters is rejected, just as they would reject it
    (`PL-LBQY`, `PL-19Y0`). A percent, a fraction or a flow is checked for its
    type and not for its range. A `Percent`, a `Fraction` or a `FreshGasFlow`
    was checked against its range when it was built, so a value of that type
    already proves that it is in range (`PL-4R3W`, `PL-0YYV`).

    `deliverable_fresh_gas_flow_range` is the machine's counterpart of that
    dial maximum, but it may be `None`. `None` means "no machine range
    declared", and then the model's envelope in
    `core/supported_ranges.py` is the only bound on the flow. The shipped
    `reference_circle_system` profile declares no range. No operator's manual
    or manufacturer specification giving a deliverable range was reachable for
    any surveyed machine (`docs/machine-survey.md` § "(b8) Flow bounds,
    minimum oxygen flow, and the hypoxic guard"). So `None` here records that
    no claim is made. It does not mean the machine is known to be unlimited.
    The range is instance state for the same reason the vaporizer maximum is.
    It belongs to the device in front of the patient and differs between
    devices, whereas a module constant would be one number for every machine
    there will ever be (`PL-8PS6`). `accepted_fresh_gas_flow_range_l_min`
    combines the two bounds, the machine's range and the model's envelope. It
    is the one place that states their intersection.
    """

    circuit_volume_l: CompartmentVolume
    fresh_gas_flow_l_min: FreshGasFlow = TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN
    delivered_concentration_percent: Percent = Percent(0.0)
    inspired_partial_pressure_fraction: Fraction = Fraction(0.0)
    # This field is keyword-only, because a field with no default cannot follow
    # one with a default. The constructor still writes the fields in the order
    # listed, so the maximum is written after the dial. The maximum's check in
    # `__setattr__` reads the dial, so the dial must already be set.
    max_delivered_concentration_percent: Percent = field(kw_only=True)
    deliverable_fresh_gas_flow_range: DeliverableFreshGasFlowRange | None = None

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # This method is hidden from `mypy` on purpose. When a class defines
        # `__setattr__`, `mypy` lets code assign any attribute name on it, with
        # the type of the method's `value` parameter. So if `mypy` could see
        # this method, a misspelt field name written in `src/` would pass
        # `--strict` and then fail at run time against the slots. That would
        # happen only on the classes that define the method. With the method
        # hidden, `mypy` reads the dataclass's fields and their types as before.
        # This method is the run-time check for the callers that `mypy` does not
        # read. Its tests check its lines, because `mypy` does not (`PL-LBQY`,
        # found at review).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a field, rejecting a value that the circuit's constructor would reject.

            Each field is stored in one place, its slot, so its check is made
            here, once for every writer. The writers are the constructor, the
            setters, and any assignment that bypasses both, made by a caller
            that `mypy` does not read (a test, a notebook, or a value typed
            `Any`). Until `PL-LBQY`, such an assignment met no check. Until
            `PL-19Y0`, it met only a check of the fresh gas flow's type. So each
            of these was stored, for a snapshot to copy and for the readout
            beside the control to show: a sevoflurane dial of `Percent(50.0)`,
            above its 8% maximum; a zero circuit volume; and an inspired
            fraction of `1.5`. A copy, a pickle and `dataclasses.replace` also
            write through this method. This is a `slots=True` dataclass, and a
            copy or a pickle restores its state one field at a time through
            `__setattr__`. If the class had a `__dict__`, a copy would update
            that dictionary directly and bypass the check. When a value is
            rejected, nothing is written and the field keeps its old value. The
            constructor makes no check of its own.

            A rule that relates two fields belongs to the circuit, which holds
            both (`PL-BBMG`). The rule is first checked when the second of the
            two fields is written, and again whenever either field is written
            after that. The dial is checked against the vaporizer's maximum. The
            flow is checked against the machine's range, and the machine's range
            is checked against the model's envelope when the range is written
            (`PL-8PS6`). The constructor writes the dial before the maximum and
            the flow before the range. So during construction, the first field
            of each pair is written before its partner exists, and the partner's
            own write checks the pair.

            The circuit stores its agent as a fraction of its volume. So a
            volume written here changes the amount of agent with it, gaining or
            losing agent that no flow carried, and the next step's mass-balance
            check halts on the difference. `set_circuit_volume` is the write
            that conserves the agent.

            Raises:
                TypeError: `value` was not built as the field's type (a
                    `FreshGasFlow`, a `Percent`, a `Fraction`, or a
                    `DeliverableFreshGasFlowRange` or `None`), or the volume was
                    not built as a `CompartmentVolume`, which checks it against
                    the numerical envelope (`core/numerical_envelope.py`).
                SimulationConfigurationError: the vaporizer maximum is not
                    positive and finite. Or the dial is above
                    the maximum, whichever of the two is being written. Or the
                    flow is outside the machine's range, whichever of the two
                    is being written. Or the machine's range does not overlap
                    the model's envelope at all.
            """

            if name == "circuit_volume_l":
                require_compartment_volume(name, value)
            elif name == "fresh_gas_flow_l_min":
                require_fresh_gas_flow(value)

                if hasattr(self, "deliverable_fresh_gas_flow_range"):
                    _require_deliverable_flow(value, self.deliverable_fresh_gas_flow_range)
            elif name == "delivered_concentration_percent":
                require_percent(name, value)

                if hasattr(self, "max_delivered_concentration_percent"):
                    require_within_vaporizer_maximum(
                        name, value, self.max_delivered_concentration_percent
                    )
            elif name == "inspired_partial_pressure_fraction":
                require_fraction(name, value)
            elif name == "max_delivered_concentration_percent":
                require_percent(name, value)
                require_positive_finite(name, value)
                # If a maximum written onto a circuit already built is refused, it was
                # lowered below the dial, so the refusal is worded for the maximum. The
                # first write comes from a constructor, a copy or a pickle, just after the
                # dial is written. Its refusal is worded for the dial, and that message
                # names both values (`PL-XVCV`).
                rewritten = hasattr(self, "max_delivered_concentration_percent")
                require_within_vaporizer_maximum(
                    "max_delivered_concentration_percent"
                    if rewritten
                    else "delivered_concentration_percent",
                    self.delivered_concentration_percent,
                    value,
                    maximum_written=rewritten,
                )
            elif name == "deliverable_fresh_gas_flow_range":
                _require_a_machine_range(value)
                _require_the_two_flow_claims_overlap(value)
                _require_deliverable_flow(self.fresh_gas_flow_l_min, value)

            super().__setattr__(name, value)

    @property
    def accepted_fresh_gas_flow_range_l_min(self) -> tuple[float, float]:
        """The lowest and highest fresh gas flow this circuit accepts, in L/min.

        This is the intersection that the module docstring describes, computed
        in one place (`_accepted_fresh_gas_flow_range_l_min`). It is the
        model's envelope in `core/supported_ranges.py`, narrowed to the
        machine's `deliverable_fresh_gas_flow_range` where the machine's profile
        declares one, and the envelope alone where it declares none. Both ends
        are inclusive, as both bounds are. `set_fresh_gas_flow` accepts a flow
        inside this range. It rejects a flow outside it through the model's
        guard or the machine's guard, each in its own words. So this is the
        range that a control for this setting should offer, and the interface
        reads it for that purpose (`PL-7CRY`). A slider bounded by the envelope
        alone would offer flows that the mounted machine cannot set, inviting a
        rejection that the control could have made impossible.

        `_require_the_two_flow_claims_overlap` rejects a machine range that
        shares no flow with the envelope, wherever the range is written. So the
        first end of this range is never above the second (`PL-HJ7L`,
        `PL-19Y0`).
        """

        return _accepted_fresh_gas_flow_range_l_min(self.deliverable_fresh_gas_flow_range)

    @property
    def delivered_partial_pressure_fraction(self) -> Fraction:
        """The fraction of an atmosphere that the dial delivers, derived from its percent.

        `advance_fresh_gas()` and the governing equations read this value. It
        is derived on every read rather than stored beside the percent. So
        there is one record of the setting and nothing that could disagree with
        it (`PL-NJPB`).
        """

        return fraction_from_percent(self.delivered_concentration_percent)

    @property
    def agent_amount_l(self) -> float:
        """Return the agent stored in the circuit, in litres of equivalent agent gas."""

        return self.circuit_volume_l * self.inspired_partial_pressure_fraction

    @property
    def time_constant_s(self) -> float:
        """Return the fresh gas wash-in time constant, in seconds.

        The time constant is `circuit_volume_l / fresh_gas_flow_l_min`, which
        is in minutes, and this method converts it to seconds. At zero flow it
        returns `inf`. The time constant is based on the flow at the common gas
        outlet, not on a flowmeter setting. `advance_fresh_gas()` does not read
        it. That method computes
        the step's length in time constants from the volume of gas the step
        admits, which does not overflow at any flow.
        """

        if self.fresh_gas_flow_l_min == 0.0:
            return inf

        return SECONDS_PER_MINUTE * self.circuit_volume_l / self.fresh_gas_flow_l_min

    def set_circuit_volume(self, circuit_volume_l: CompartmentVolume) -> None:
        """Change the circuit's volume while conserving the agent in it.

        The circuit stores agent as a fraction of its volume, so changing the
        volume alone scales `agent_amount_l` with it. This was measured on the
        shipped code before this guard existed. A sevoflurane system stepped for
        60 s held 0.048288200 L in the circuit. `set_circuit_volume(3.0)` then
        left 0.024144100 L, so a setter destroyed 24.1 mL of equivalent agent
        gas. The next `advance(0.1)` raised `AgentSimulationValidationError`,
        which blamed the numerics for the setter's defect.

        The point is to conserve the agent here rather than in the caller
        (PL-006). Then `docs/MODEL.md`'s required invariants, "no compartment
        creates agent spontaneously" and "changing a setting does not reset
        stored state", still apply for every caller of this public method.
        Otherwise they would apply only for a caller that knew to read the
        amount out and put it back.

        Raises:
            TypeError: the volume was not built as a `CompartmentVolume`,
                which checks it against the numerical envelope
                (`core/numerical_envelope.py`).
            SimulationConfigurationError: the volume is too small to hold the
                agent already in the circuit. Both checks run, and the
                fraction that the new volume gives is built, before anything
                changes. So a rejected volume leaves the circuit exactly as it
                was.
        """

        require_compartment_volume("circuit_volume_l", circuit_volume_l)

        stored_agent_l = self.agent_amount_l

        require_room_for_the_agent_held(
            "circuit_volume_l",
            circuit_volume_l,
            circuit_volume_l,
            stored_agent_l,
            "breathing circuit",
            "Breathing circuit",
        )

        inspired_partial_pressure_fraction = Fraction(
            stored_agent_l / circuit_volume_l, name="inspired_partial_pressure_fraction"
        )
        self.circuit_volume_l = circuit_volume_l
        self.inspired_partial_pressure_fraction = inspired_partial_pressure_fraction

    def set_fresh_gas_flow(self, fresh_gas_flow_l_min: FreshGasFlow) -> None:
        """Set the fresh gas flow, rejecting a flow that the machine cannot deliver.

        The effective limit is the intersection of the model's supported
        range (`core/supported_ranges.py`) and the machine's deliverable
        range, where the profile declares one. The model's range was checked
        when the flow was built as a `FreshGasFlow`. So a flow outside both
        ranges is rejected there, against the envelope. The envelope is the
        stronger statement of the two, and it applies whichever machine is
        mounted. A flow that gets this far is checked by the write itself, in
        `__setattr__`. The write checks the type first, so that a value of the
        wrong type is rejected in the simulator's words rather than by the
        comparison with the machine's range. Then it checks the machine's
        range.

        Raises:
            SimulationConfigurationError: the flow is outside what this
                machine can deliver. Nothing is written when it is rejected.
            TypeError: `fresh_gas_flow_l_min` was not built as a
                `FreshGasFlow`. Nothing is written when it is rejected.
        """

        self.fresh_gas_flow_l_min = fresh_gas_flow_l_min

    def set_delivered_concentration_percent(self, delivered_concentration_percent: Percent) -> None:
        """Set the vaporizer dial in the percent it reads, rejecting what it cannot deliver.

        The write itself makes both checks, in `__setattr__`, so an assignment
        that bypasses this setter meets them too (`PL-19Y0`).

        Raises:
            TypeError: the dial was not built as a `Percent`, the type that
                checks it against 0 to 100 (`core/concentration.py`). A
                `Fraction` is rejected too, with a message that tells the
                caller to convert it. Nothing is written when it is rejected.
            SimulationConfigurationError: the dial is above
                `max_delivered_concentration_percent`. Nothing is written
                when it is rejected.
        """

        self.delivered_concentration_percent = delivered_concentration_percent

    def set_inspired_partial_pressure_fraction(
        self, inspired_partial_pressure_fraction: Fraction
    ) -> None:
        """Set the circuit's state from a fraction, as the coupled step produces it.

        This is the counterpart of `set_agent_amount()` for a caller that
        already holds a fraction. `AgentUptakeSystem` is that caller. The
        governing equations carry the gas phase as fractions, so going through
        the amount would multiply by the volume and then divide by it again for
        no benefit. The write itself, in `__setattr__`, checks the fraction's
        type.

        Raises:
            TypeError: the fraction was not built as a `Fraction`, the type
                that checks it against 0 to 1 (`core/concentration.py`).
                Nothing is written when it is rejected.
        """

        self.inspired_partial_pressure_fraction = inspired_partial_pressure_fraction

    def set_agent_amount(self, agent_amount_l: float) -> None:
        """Set the circuit's state from an amount of agent, in litres of equivalent gas.

        Raises:
            TypeError: the amount is not an `int` or a `float`.
            SimulationConfigurationError: the amount is negative or not
                finite, or it is more than the circuit volume. The circuit
                volume is the amount the circuit holds at a partial pressure of
                one atmosphere.
        """

        require_nonnegative_finite("circuit agent_amount_l", agent_amount_l)
        require_within_the_capacity(
            "circuit agent_amount_l",
            agent_amount_l,
            self.circuit_volume_l,
            "breathing circuit",
            "Gas compartments",
        )

        self.inspired_partial_pressure_fraction = Fraction(agent_amount_l / self.circuit_volume_l)

    def advance_fresh_gas(self, simulation_step_s: float) -> FreshGasExchange:
        """Advance the circuit's exact wash-in by one step and return the external exchange.

        This method is the circuit's own closed-form solution with no patient
        connected. It is not how a run advances. A connected patient adds a
        ventilation term, which `docs/MODEL.md` § "Breathing circuit" gives beside
        this one, and `AgentUptakeSystem.advance()` is the step that solves both.
        The package docstring in `core/__init__.py` explains the distinction. It
        also explains why zero flow needs no separate branch here.

        Raises:
            SimulationConfigurationError: `simulation_step_s` is not positive
                and finite, or is shorter than `MINIMUM_SIMULATION_STEP_S`
                (`core/simulation_step.py`, `PL-WP52`). Nothing changes when the
                step is refused.
        """

        require_at_least_the_smallest_step("circuit simulation_step_s", simulation_step_s)

        initial_fraction = self.inspired_partial_pressure_fraction
        delivered_fraction = self.delivered_partial_pressure_fraction
        fresh_gas_flow_l_s = self.fresh_gas_flow_l_min / SECONDS_PER_MINUTE

        # This is the volume of fresh gas that enters the circuit during the
        # step. The same volume of circuit gas leaves through the exhaust.
        # Divided by the circuit volume, it gives the step's length in time
        # constants, dt/tau. The code does not compute tau first, because tau
        # overflows to `inf` when the fresh gas flow is below about 2e-306 L/min
        # in a 6 L circuit (`PL-B26Y`).
        admitted_gas_l = fresh_gas_flow_l_s * simulation_step_s
        time_constants_elapsed = admitted_gas_l / self.circuit_volume_l

        # This is 1 - exp(-dt/tau), the share of the gas in the circuit at the
        # start of the step that fresh gas has replaced by the end. `-expm1`
        # keeps the result's significant digits when dt/tau is small. In that
        # case `1.0 - exp(...)` subtracted two numbers within an ulp of 1 and
        # lost those digits (`PL-YT8N`). `-expm1` also keeps the result between
        # 0 and dt/tau, which the exhaust calculation below needs.
        fraction_replaced = -expm1(-time_constants_elapsed)

        next_fraction = Fraction(
            initial_fraction + (delivered_fraction - initial_fraction) * fraction_replaced
        )

        delivered_agent_l = delivered_fraction * admitted_gas_l

        # The exhaust is the flow times $`\int F_I \mathrm{d}t`$ over the step.
        # Of the gas that leaves, `starting_gas_out_l` was in the circuit at
        # the start of the step and `fresh_gas_out_l` is fresh gas. The
        # inspired fraction stays between the circuit's starting fraction and
        # the dial's fraction. So every litre that leaves carries at least the
        # lower of the two fractions. The excess above that lower fraction is
        # carried by whichever gas started above it: the fresh gas in a
        # wash-in, and the circuit's own gas in a washout. So no term can be
        # negative. The exhaust used to be written as what was delivered minus
        # what the circuit kept. Wherever the circuit kept nearly all it was
        # given, that was the difference of two nearly equal amounts, and it
        # took the sign of the rounding error (`PL-YT8N`).
        starting_gas_out_l = self.circuit_volume_l * fraction_replaced
        fresh_gas_out_l = self.circuit_volume_l * (time_constants_elapsed - fraction_replaced)
        lower_fraction = min(initial_fraction, delivered_fraction)

        exhausted_agent_l = (
            lower_fraction * admitted_gas_l
            + (delivered_fraction - lower_fraction) * fresh_gas_out_l
            + (initial_fraction - lower_fraction) * starting_gas_out_l
        )

        self.inspired_partial_pressure_fraction = next_fraction

        return FreshGasExchange(
            delivered_agent_l=delivered_agent_l, exhausted_agent_l=exhausted_agent_l
        )

    def advance(self, simulation_step_s: float) -> None:
        """Preserve the original v0.0.2 circuit interface.

        This method keeps the old name and adds no behaviour. `docs/MODEL.md`
        § "Preserved circuit reference tests" requires the v0.0.2 analytic
        wash-in and washout tests to pass *unchanged*, and
        `tests/reference/test_circuit_wash_in.py` calls the circuit by this
        name. The v0.0.2 signature discarded the exchange that
        `advance_fresh_gas()` reports. A caller that needs the exchange calls
        `advance_fresh_gas()` instead.
        """

        self.advance_fresh_gas(simulation_step_s)

    def capture_state(self) -> BreathingCircuitState:
        """Record the run state, so that a failed step can be rolled back.

        The compartment captures its own state, rather than `AgentUptakeSystem`
        reading the state out of it. So if a dynamic field is added here later
        without a matching line below, the omission is local and easy to
        review.
        """

        return BreathingCircuitState(
            inspired_partial_pressure_fraction=self.inspired_partial_pressure_fraction
        )

    def restore_state(self, state: BreathingCircuitState) -> None:
        """Restore the run state previously captured by `capture_state()`.

        The method assigns the field directly rather than going through
        `set_agent_amount()`. The value came from a valid circuit, and the
        record rejected anything not built as a `Fraction` when the record was
        made. So there is nothing to check again. A rollback that could itself
        raise would leave exactly the partial state that the rollback exists to
        prevent.
        """

        self.inspired_partial_pressure_fraction = state.inspired_partial_pressure_fraction

    def reset(self) -> None:
        """Remove all agent from the circuit, keeping its settings."""

        self.inspired_partial_pressure_fraction = Fraction(0.0)
