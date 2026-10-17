"""Shared numeric-range guards used by every core compartment's field
writes and setters, so invalid state is rejected at the same boundary
everywhere instead of trusted or coerced silently. Two of them,
`require_within_vaporizer_maximum` and `require_room_for_the_agent_held`,
are relations between values rather than properties of one, and are here for
the same reason: the records that hold each pair refuse it in one sentence
(`PL-BBMG`, `PL-19Y0`).

A concentration's own range is not here. A fraction's 0 to 1 and a percent's 0
to 100 were checked by guards in this module, at each of the twelve places a
value entered, until `PL-4R3W` made `Fraction` and `Percent` types built only
through those checks (`core/concentration.py`), so what is left here is the
sign and finiteness every other quantity shares and the one relation.

Every guard raises `SimulationConfigurationError` for a value it refuses: it
was rejected before it changed anything. A refusal reached partway through a step means
something different — the numerics broke down rather than the caller
passing a bad value — and `AgentUptakeSystem.advance()` is what turns it
into `SimulationNumericalError`, because it is the only frame that knows a
step was in progress. It is also the only one that can undo that step, and
does: the refusal fires after earlier compartments have already been
written, so the step is rolled back before the numerical error is raised.
Since `PL-4R3W` that refusal is a computed fraction refused where it is built
as a `Fraction`, which raises the same exception for the same reason. See
`core/exceptions.py` for why the hierarchy is kept separate from
`ValueError`.

What is not a number at all - a `bool`, a `Decimal`, a string - is refused
before any of that, with the `TypeError` `require_a_number` raises
(`core/checked_number.py`, `PL-3800`): a programming error in the caller
rather than a refused value, so not an `AnesthesiaSimulationError`.
`require_within_vaporizer_maximum` takes two `Percent`s, each already built
through it.

**What `name` has to carry.** Each guard raises `f"{name} ..."` and nothing
else, so `name` is the whole of what a reader is told about *which* value was
refused — and that reader is usually looking at a banner rather than a
traceback, since `app/dashboard_frame.py` renders a refused setting verbatim
and `AgentUptakeSystem.advance()` wraps a refused step into the halted-run
notice. A bare parameter name identifies the value only where one object can
raise it. Where several can, the caller prefixes the owner: the instance's own
`name` where it has one — `f"{self.name} volume_l"`, as
`governing_equations.py`'s `TissueGroupEquationSettings` does for its volume
and flow — and the compartment's domain word where it does not, `"alveolar
..."` and `"venous ..."`. `PL-SPN6` is what the bare name cost: `PL-9SH6` left
the alveolar compartment, the venous pool and all three tissue groups raising
one string for a refused fraction, so a refused resume could not say which of
the five had refused. The prefix is built at the call site rather than from a
parameter here, so the sentence a reader will see is readable in the line that
raises it, and `Fraction`'s `name` carries the same convention where a fraction
is built (`core/concentration.py`).
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
) -> None:
    """Require a vaporizer dial at or below the maximum the vaporizer in use delivers.

    The one guard here that is a relation rather than a property of a number.
    A dial is deliverable only against a maximum, and the maximum is the
    agent's vaporizer's rather than the model's, so no type can carry the
    bound the way `core/supported_ranges.py` carries the model's own: it is
    checked where the two are held side by side. Two records hold them -
    `BreathingCircuit`, which owns the dial, and `UptakeEquationSettings`,
    which a run is built from - and both call this, so both refuse in the
    same sentence and the relation is written once (`PL-BBMG`).

    Rejecting rather than clamping is deliberate: a silently clamped dial
    position would simulate, display, and chart a concentration the caller
    did not ask for, which is the plausible-but-wrong clinical value
    `CLAUDE.md` forbids. Zero is always allowed - it is the vaporizer turned
    off, which is how washout begins - and so is the maximum itself.

    Both arguments are `Percent`s, whose constructor is what refuses a `nan`,
    since no comparison does, and its callers check that each was built as one
    (`require_percent`, `core/concentration.py`) before calling this; it
    compares the two and checks nothing else.

    Raises:
        SimulationConfigurationError: the dial is above the maximum. The
            message quotes both in the percent the dial reads.
    """

    if delivered_concentration_percent > max_delivered_concentration_percent:
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

    A compartment's partial pressure is the agent it holds divided by its
    capacity, the agent it would hold at a partial pressure of one atmosphere:
    its volume, times its partition coefficient where it is blood or tissue
    (`docs/MODEL.md` § "Tissue compartments" gives the tissue's). Shrinking
    either factor under a fixed amount raises the partial pressure, and below
    the amount held it puts it above one atmosphere. Each compartment refuses
    an amount written above its capacity, and until `PL-19Y0` nothing refused
    the converse: an alveolar volume of 1e-6 L written under 0.098 L of
    sevoflurane was accepted, and the next step began from an alveolar partial
    pressure near 98,000 atmospheres and ended with every fraction plausible
    and wrong - inspired 6.71% where an ordinary step reads 5.81% - and the
    accounting passing (`PL-544D`, found at review; measured 2026-10-17). So
    the alveolar compartment, the venous pool and each tissue group call this
    as either factor is written, with the capacity that writing `value` would
    leave, which only the caller knows how to form.

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
