"""Shared numeric-range guards used by every core compartment's field
writes and setters, so invalid state is rejected at the same boundary
everywhere instead of trusted or coerced silently. Four of the guards check a
relation between two values rather than a property of one value. They are here
for the same reason. Every record that holds such a pair refuses it with the same
message. `require_within_vaporizer_maximum` keeps a dial at or below its
vaporizer's maximum (`PL-BBMG`). `require_room_for_the_agent_held` and
`require_within_the_capacity` keep an agent amount within its compartment's
capacity. The first checks a change to the capacity, and the second checks a
change to the amount (`PL-19Y0`, `PL-XVCV`). `require_a_capacity` checks that a
volume and a partition coefficient multiply to a capacity that is positive and
finite (`PL-8LQZ`, `PL-FNH3`).

A concentration's own range is not checked here. Until `PL-4R3W`, guards in this
module checked a fraction's 0 to 1 and a percent's 0 to 100, at each of the twelve
places a value entered. `PL-4R3W` made `Fraction` and `Percent` types that can be
built only through those checks (`core/concentration.py`). What is left here is the
check of sign and finiteness that every other quantity shares, and the four
relations above.

Every guard raises `SimulationConfigurationError` for a value it refuses, because
the value was rejected before it changed anything. A refusal partway through a step
means something different. It means the numerics broke down, not that the caller
passed a bad value. `AgentUptakeSystem.advance()` turns such a refusal into
`SimulationNumericalError`, because it is the only frame that knows a step was in
progress. It is also the only frame that can undo the step, and it does. The
refusal comes after earlier compartments have already been written, so `advance()`
rolls the step back before it raises the numerical error. Since `PL-4R3W`, that
refusal comes from a computed fraction that is refused when it is built as a
`Fraction`. The `Fraction` constructor raises the same exception for the same
reason. See `core/exceptions.py` for why the hierarchy is kept separate from
`ValueError`.

A value that is not a number at all, such as a `bool`, a `Decimal` or a string, is
refused before any of these checks. `require_a_number` raises a `TypeError` for it
(`core/checked_number.py`, `PL-3800`). Such a value is a programming error in the
caller rather than a refused value, so the error is not an
`AnesthesiaSimulationError`. `require_within_vaporizer_maximum` takes two
`Percent`s, and `require_a_number` already checked each of them when it was built.

**What `name` has to carry.** Each guard raises a message of the form
`f"{name} ..."`, and nothing else in it identifies the value. So `name` is all that
a reader is told about *which* value was refused. That reader usually sees a banner
rather than a traceback. `app/dashboard_frame.py` shows a refused setting's message
verbatim, and `AgentUptakeSystem.advance()` wraps a refused step into the
halted-run notice. A bare parameter name identifies the value only where just one
object can raise it. Where several objects can, the caller puts the owner's name in
front. It uses the instance's own `name` where the instance has one, as in
`f"{self.name} volume_l"`. `governing_equations.py`'s `TissueGroupEquationSettings`
does this for its volume and flow. Where the instance has no `name`, the caller uses
the compartment's domain word, as in `"alveolar ..."` and `"venous ..."`. `PL-SPN6`
records what the bare name cost. After `PL-9SH6`, the alveolar compartment, the
venous pool and all three tissue groups raised the same message for a refused
fraction. So when a resumed run was refused, the message could not say which of the
five had refused it. The caller builds the prefix at the call site, rather than
passing it to a parameter here. Then the sentence a reader will see can be read in
the line that raises it. `Fraction`'s `name` follows the same convention where a
fraction is built (`core/concentration.py`).
"""

import sys
from math import isfinite

from anesthesia_sim.core.checked_number import require_a_number, shown
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError


def require_positive_finite(name: str, value: float) -> None:
    """Require a finite numeric value greater than zero.

    The value is required to be a number first, by `require_a_number`
    (`core/checked_number.py`), as every checked type requires of what it is
    built from: until `PL-3800` `True` passed as the 1 it is to Python, so
    `BreathingCircuit(circuit_volume_l=True)` held a 1 L circuit, a `Decimal`
    was held as given and entered the arithmetic as one, and a `str` was
    refused in `math.isfinite`'s words, naming neither the field nor its
    constraint. Then an `int` outside the range a `float` holds is refused by
    name (`_require_within_the_float_range`), where `isfinite` raised
    `OverflowError` converting it. What is left is the test this guard has
    always made, on a value it can now read.

    Raises:
        TypeError: `value` is not an `int` or a `float`, or is a `bool`. A
            programming error in the caller rather than a refused setting, as
            `require_a_number` says.
        SimulationConfigurationError: `value` is an `int` outside the range a
            `float` holds, named with the value, or is zero, negative, a NaN
            or an infinity, named by the property it failed; naming the value
            in that sentence too is `PL-T137`'s.
    """

    require_a_number(name, value)
    _require_within_the_float_range(name, value)

    if not isfinite(value) or value <= 0.0:
        raise SimulationConfigurationError(f"{name} must be positive and finite")


def require_nonnegative_finite(name: str, value: float) -> None:
    """Require a finite numeric value greater than or equal to zero.

    Built as `require_positive_finite` is, and for the same reasons: a number
    first, an `int` outside the float range refused by name, then the test on
    the value itself. Zero is admitted, as the supported zero it is - the
    fresh gas turned off, an unperfused tissue, no agent yet - and so is minus
    zero, which equals it.

    Raises:
        TypeError: `value` is not an `int` or a `float`, or is a `bool`, as
            `require_a_number` says.
        SimulationConfigurationError: `value` is an `int` outside the range a
            `float` holds, or is negative, a NaN or an infinity.
    """

    require_a_number(name, value)
    _require_within_the_float_range(name, value)

    if not isfinite(value) or value < 0.0:
        raise SimulationConfigurationError(f"{name} must be nonnegative and finite")


def _require_within_the_float_range(name: str, value: float) -> None:
    """Refuse an `int` outside the closed range a `float` holds, naming it.

    `math.isfinite` converts an `int` to a `float` before it answers, and
    raises `OverflowError` for one it cannot, so an `int` past the float range
    escaped both guards above as Python's own exception, naming neither the
    field nor the bound, and `SimulationStep(10**400)` was refused that way
    rather than as a step (`PL-3800`, folding `PL-21V4`'s step half). The
    other guards in `core/` have a supported range to refuse such an `int`
    against (`core/supported_ranges.py`); these two have only the sign, so
    the bound is the `float`'s own, `sys.float_info.max` either side of zero.

    Python compares an `int` against a `float` exactly, so the interval here
    converts nothing. A `float` is inside it or is an infinity or a NaN, which
    the guard's own test refuses, so it passes through unread; an `int` at or
    inside the bound passes as it always did. The few `int`s just above the
    bound that `float` would round down to it were admitted by `isfinite` and
    are refused here with the rest, as the `int`s past the largest float they
    are: the rule is the closed interval, with no rounding in it.
    """

    if isinstance(value, int) and not -sys.float_info.max <= value <= sys.float_info.max:
        raise SimulationConfigurationError(
            f"{name} of {shown(value)} is outside the range a float holds, "
            f"-{sys.float_info.max!r} to {sys.float_info.max!r}"
        )


def require_within_vaporizer_maximum(
    name: str,
    delivered_concentration_percent: Percent,
    max_delivered_concentration_percent: Percent,
    *,
    maximum_written: bool = False,
) -> None:
    """Require a vaporizer dial at or below the maximum the vaporizer in use delivers.

    This guard checks a relation between two values rather than a property of one
    number. Whether a dial setting can be delivered depends on a maximum, and that
    maximum belongs to the agent's vaporizer rather than to the model. So no type can
    carry the bound in the way `core/supported_ranges.py` carries the model's own
    bounds. The bound is checked where a record holds the dial and the maximum side by
    side. Two records hold both: `BreathingCircuit`, which owns the dial, and
    `UptakeEquationSettings`, from which a run is built. Both call this function, so
    both refuse with the same sentence and the relation is written once (`PL-BBMG`).

    Rejecting rather than clamping is deliberate: a silently clamped dial
    position would simulate, display, and chart a concentration the caller
    did not ask for, which is the plausible-but-wrong clinical value
    `CLAUDE.md` forbids. Zero is always allowed - it is the vaporizer turned
    off, which is how washout begins - and so is the maximum itself.

    Both arguments are `Percent`s. The `Percent` constructor is what refuses a `nan`,
    because no comparison refuses it. Callers check that each argument was built as a
    `Percent` (`require_percent`, `core/concentration.py`) before they call this
    function. This function compares the two values and checks nothing else.

    The refusal is worded for whichever value was written, and `name` is that value's
    name. Pass `maximum_written=True` when the value written was the maximum. Then a
    maximum lowered below the dial is refused as the maximum, not as a dial that nobody
    moved (`PL-XVCV`). A record that holds both values and checks them together, as
    `UptakeEquationSettings` does, leaves `maximum_written` as `False`. Its refusal is
    then worded for the dial.

    Raises:
        SimulationConfigurationError: the dial is above the maximum. The
            message quotes both values in percent, the unit the dial shows.
    """

    if delivered_concentration_percent <= max_delivered_concentration_percent:
        return

    if maximum_written:
        raise SimulationConfigurationError(
            f"{name} of {max_delivered_concentration_percent:g}% is below the "
            f"{delivered_concentration_percent:g}% the dial is set to, and a vaporizer maximum "
            "must be at or above its dial"
        )

    raise SimulationConfigurationError(
        f"{name} exceeds the vaporizer maximum "
        f"({delivered_concentration_percent:g}% requested, "
        f"{max_delivered_concentration_percent:g}% maximum)"
    )


def require_room_for_the_agent_held(
    name: str,
    value: float,
    capacity_l: float,
    agent_amount_l: float,
    compartment: str,
    section: str,
) -> None:
    """Refuse a volume or partition coefficient too small for the agent its compartment holds.

    A compartment's partial pressure is the amount of agent it holds divided by
    its capacity. Its capacity is the amount of agent it would hold at a
    partial pressure of one atmosphere. The capacity is the compartment's
    volume, multiplied by its partition coefficient when the compartment is
    blood or tissue (`docs/MODEL.md` § "Tissue compartments" gives the
    tissue's). With the amount fixed, shrinking either factor raises the
    partial pressure. Once the capacity is less than the amount held, the
    partial pressure is above one atmosphere. Each compartment rejects an
    amount written above its capacity. Until `PL-19Y0`, nothing rejected the
    converse. An alveolar volume of 1e-6 L, written while the compartment held
    0.098 L of sevoflurane, was accepted. The next step began from an alveolar
    partial pressure near 98,000 atmospheres. It ended with every fraction
    plausible and wrong, and with the accounting passing: inspired read 6.71%
    where an ordinary step reads 5.81% (`PL-544D`, found at review; measured
    2026-10-17). So the alveolar compartment, the venous pool and each tissue
    group call this function whenever either factor is written. They pass the
    capacity that writing `value` would leave, which only the caller knows how
    to compute. The breathing circuit calls it when
    `BreathingCircuit.set_circuit_volume` changes the volume (`PL-84G1`).

    Raises:
        SimulationConfigurationError: `agent_amount_l` is above `capacity_l`.
            The message names the value written, the agent held, and the room
            the value would leave for it.
    """

    if agent_amount_l > capacity_l:
        raise SimulationConfigurationError(
            f"{name} of {shown(value)} is too small for the {agent_amount_l!r} L of agent "
            f"the {compartment} holds: it would leave room for {capacity_l!r} L at a "
            f'partial pressure of one atmosphere (docs/MODEL.md, "{section}")'
        )


def require_within_the_capacity(
    name: str, agent_amount_l: float, capacity_l: float, compartment: str, section: str
) -> None:
    """Refuse an agent amount larger than the capacity of the compartment it is written to.

    This guard is the converse of `require_room_for_the_agent_held`, seen from the
    amount's side. That guard refuses a volume or a partition coefficient that is
    written too small for the amount already held. This guard refuses an amount that
    is written too large for the capacity. Either way the partial pressure would be
    above one atmosphere. Both guards name the value, the capacity and the
    `docs/MODEL.md` section, so the single relation is refused in the same terms from
    either side (`PL-XVCV`).
    The caller checks first that the amount is a nonnegative finite number.

    Raises:
        SimulationConfigurationError: `agent_amount_l` is above `capacity_l`.
    """

    if agent_amount_l > capacity_l:
        raise SimulationConfigurationError(
            f"{name} of {shown(agent_amount_l)} L is more than the {capacity_l!r} L the "
            f"{compartment} holds at a partial pressure of one atmosphere "
            f'(docs/MODEL.md, "{section}")'
        )


def require_a_capacity(
    name: str,
    value: float,
    volume_l: float,
    capacity_per_litre: float,
    compartment: str,
    section: str,
) -> None:
    """Refuse a volume or partition coefficient that would leave the capacity zero or not finite.

    A blood or tissue compartment's capacity is its volume times its partition
    coefficient. Its partial pressure is the agent it holds divided by that capacity.
    Each factor is checked as positive and finite when it is written, but their product
    can still leave that range. A volume and a coefficient of 1e-200 multiply to 0.0,
    and every partial pressure read from that compartment then divided by zero
    (`PL-8LQZ`). A volume and a coefficient of 1e200 multiply to `inf`, and the venous
    pool's closed-form solution then computed an equilibrium of `inf` times 0.0 and
    stored `nan` (`PL-FNH3`). So the compartment calls this function, with both
    factors, whenever either factor is written and the other is already set. `value`
    is the factor being written, and `name` is its name.

    Raises:
        SimulationConfigurationError: the product of `volume_l` and
            `capacity_per_litre` is zero or not finite. The message names
            the value written and both factors.
    """

    capacity_l = volume_l * capacity_per_litre

    if not isfinite(capacity_l) or capacity_l <= 0.0:
        raise SimulationConfigurationError(
            f"{name} of {shown(value)} would make the {compartment}'s capacity "
            f"{capacity_l!r} L, its volume of {volume_l!r} L times its partition coefficient "
            f"of {capacity_per_litre!r}. A capacity must be positive and finite, because "
            f'every partial pressure is read by dividing by it (docs/MODEL.md, "{section}")'
        )


def require_a_capacity_with_room_for_the_agent(
    name: str,
    value: float,
    volume_l: float,
    capacity_per_litre: float,
    agent_amount_l: float | None,
    compartment: str,
    section: str,
) -> None:
    """Refuse a volume or partition coefficient that leaves a blood or tissue capacity unusable.

    A blood or tissue compartment makes the same two checks whenever its
    volume or its partition coefficient is written. Its capacity is the product
    of the two. `require_a_capacity` rejects a capacity that is zero or not
    finite. `require_room_for_the_agent_held` rejects one too small for the
    agent already held. The venous pool and each tissue group call this
    function, so the pair of checks is written once (`PL-VWXL`). `value` is the
    factor being written, and `name` is its name.

    `agent_amount_l` is `None` while the compartment holds no amount yet. The
    constructor, a copy and a pickle all write the amount last. So the first
    writes of the volume and the coefficient have no agent to make room for.

    Raises:
        SimulationConfigurationError: the capacity is zero or not finite, or
            is less than `agent_amount_l`.
    """

    require_a_capacity(name, value, volume_l, capacity_per_litre, compartment, section)

    if agent_amount_l is not None:
        require_room_for_the_agent_held(
            name, value, volume_l * capacity_per_litre, agent_amount_l, compartment, section
        )
