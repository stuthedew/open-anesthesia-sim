r"""The $`F_A/F_I`$ ratio that the uptake literature plots, and the range where it is valid.

This module is pure arithmetic over two modelled fractions. It is independent
of Flet and of the scientific core. Nothing here reads simulation state, builds
a control, or formats a string.

The ratio has its own module for this reason. `docs/MODEL.md` § "F_A/F_I as a
displayed ratio" specifies the quantity, and this module implements that
specification. `app/formatting.py` has the same relationship to § "Displayed
precision". The ratio is a clinically meaningful displayed value derived from
two other values. So `CLAUDE.md`'s safety-critical standard requires that it
can be read, cited and tested without loading the dashboard that draws it.
`tests/unit/test_wash_in.py` holds the tests that pin down its behaviour.

**What the numerator and the denominator are.** $`F_A`$ is the modelled
alveolar fraction. $`F_I`$ is the modelled *inspired* fraction, which in this
model is the breathing-circuit fraction. The identity $`F_C \equiv
F_I`$ is true because the model contains one ideal, perfectly mixed circuit. That
circuit has no dead space and no separate inspiratory and expiratory limbs
(`docs/MODEL.md` § "Model boundary"). $`F_I`$ is not the vaporizer dial
setting. The circuit fraction only approaches the dial setting, over the
circuit's own time constant. A breathing system with several limbs would break
the identity, and would make this ratio wrong too.

**Two rules decide when the quotient is a number that this application will
show.** Both rules exist because a plausible-looking number is worse here than
no number at all.

1. *The denominator must be at least one displayed unit.* $`F_I`$ is zero
   before any agent reaches the circuit. It is exactly zero at the start of
   every run, and for the whole of a run in which the vaporizer is never
   opened. So the quotient there is $`0/0`$. The rule does not treat that one
   point as a special case. Instead, the minimum denominator is the smallest
   inspired concentration that the interface itself reports as non-zero. So
   the ratio is never formed from a denominator that the display shows as
   `0.00%`.
2. *The quotient must not exceed one.* The condition $`F_A \le F_I`$ is
   exactly the uptake regime. Alveolar gas gives agent up to the blood, so the
   alveolar fraction stays below the inspired fraction and reaches it only at
   equilibrium. Above one, the tissues are returning agent faster than it is
   being delivered. That is elimination, not wash-in, and the number is no
   longer a wash-in fraction, whatever its arithmetic. The curve claims to be
   the textbook wash-in graph. Drawing such a number on it would teach a
   wash-in that went past completion.
   The rule allows `WASH_IN_ROUNDING_ALLOWANCE` above one for rounding, and
   nothing more, because rounding alone can put an equilibrium's quotient a hair
   above one (`PL-N559`).

`WASH_IN_EQUILIBRIUM_RATIO` is the second boundary. It is a *modelled* value,
not a plotting choice, because it is where net uptake stops. That is why the
chart draws it as a labelled reference line and ends the trace on it, rather
than at the top of a frame.

Neither rule invents a value, substitutes a default, or clamps a value into
range. Where the ratio is outside its domain, `read_wash_in` returns no number
to draw and says which rule excluded it. The interface can then state the
reason instead of drawing a number it cannot stand behind. For the same reason,
the number and the domain come out of one call. A caption saying "no agent in
the circuit yet" beside a trace that is still drawing would be two displays
disagreeing about the same instant.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from anesthesia_sim.app.formatting import CONCENTRATION_DISPLAY_RESOLUTION_PERCENT
from anesthesia_sim.core.concentration import Percent, fraction_from_percent

__all__ = [
    "WASH_IN_DENOMINATOR_FLOOR_FRACTION",
    "WASH_IN_EQUILIBRIUM_RATIO",
    "WASH_IN_ROUNDING_ALLOWANCE",
    "WashInDomain",
    "WashInReading",
    "is_wash_in",
    "read_wash_in",
    "wash_in_ratio",
]

#: The smallest inspired fraction from which the ratio may be formed.
#:
#: The value is derived rather than chosen, for the same reason that
#: `formatting.py` derives the MAC resolution from the percent resolution. It
#: is `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT` expressed as a fraction. So a
#: change to the displayed resolution moves this value with it, and no second
#: constant is left behind to go stale. This is rule 1 of the module docstring.
WASH_IN_DENOMINATOR_FLOOR_FRACTION: Final = fraction_from_percent(
    Percent(CONCENTRATION_DISPLAY_RESOLUTION_PERCENT)
)

#: The ratio at which net uptake stops: $`F_A = F_I`$. It is the wash-in
#: curve's asymptote and rule 2 of the module docstring. Above this ratio the
#: run is eliminating agent rather than taking it up.
WASH_IN_EQUILIBRIUM_RATIO: Final = 1.0

#: How far above `WASH_IN_EQUILIBRIUM_RATIO` a quotient may round and still
#: be read as wash-in at equilibrium (`PL-N559`).
#:
#: With cardiac output at zero there is no uptake, so the exact solution has
#: $`F_A`$ rise to $`F_I`$ and stop there. The stepped run does not land
#: exactly on that point. It settles onto a floating-point fixed point within
#: about 1e-13 of it, relative, and every later step returns that same state.
#: In some runs the fixed point has $`F_A`$ above $`F_I`$. Isoflurane at
#: 10 L/min settles at a quotient of 1 + 2.2e-14, and without this allowance
#: the plot told the learner that the patient was returning agent. On
#: 2026-10-26 nine agent and fresh gas flow combinations were stepped at 0.1 s
#: for 24 h, and one for 96 h. The largest quotient was 1 + 2.2e-14, and none
#: grew after the run reached its fixed point. Twenty-one runs on the
#: canonical path to 24 h reached at most 1 + 9.6e-14.
#:
#: The allowance of 1e-9 is about 10,000 times the largest of those. A
#: quotient that small above one is genuinely elimination only by an amount
#: far below the two decimals the interface prints. The project owner chose
#: this route on 2026-10-26, over giving the propagator an exact fixed point,
#: which would have changed every run's last digits.
WASH_IN_ROUNDING_ALLOWANCE: Final = 1e-9


class WashInDomain(StrEnum):
    """Whether $`F_A/F_I`$ is a wash-in fraction, and if not, why not.

    There are three outcomes rather than a `None`, because the interface has
    to say *which* outcome a blank stretch of curve stands for. "No agent has
    reached the circuit yet" and "the patient is now returning agent" are
    opposite situations. A reader told only that the trace stopped would have
    no way to tell them apart.
    """

    WASH_IN = "wash_in"
    """Inside the domain: the quotient is a wash-in fraction from 0 to 1."""

    NO_INSPIRED_AGENT = "no_inspired_agent"
    """The denominator is below `WASH_IN_DENOMINATOR_FLOOR_FRACTION`."""

    ELIMINATION = "elimination"
    """The alveolar fraction exceeds the inspired fraction: agent is coming back, not going in."""


@dataclass(frozen=True, slots=True)
class WashInReading:
    """The wash-in display's reading of one pair of modelled fractions.

    Attributes:
        domain: Which of `WashInDomain`'s three cases this pair falls in.
        plotted_ratio: The dimensionless quotient where it is a wash-in
            fraction, and `None` in the other two cases. It is never a
            clamped or substituted value. Outside the domain there is no
            number to draw, and saying so is the purpose of the pair.
    """

    domain: WashInDomain
    plotted_ratio: float | None


def wash_in_ratio(
    alveolar_partial_pressure_fraction: float, inspired_partial_pressure_fraction: float
) -> float | None:
    """Divide the alveolar fraction by the inspired fraction, where the denominator allows it.

    This function does the arithmetic alone and applies rule 1 of the module
    docstring and nothing else. So the result may exceed one. A caller that
    plots the result as a wash-in fraction should call `read_wash_in` instead.

    Args:
        alveolar_partial_pressure_fraction: $`F_A`$, as a fraction of one
            atmosphere.
        inspired_partial_pressure_fraction: $`F_I`$, as a fraction of one
            atmosphere. This model's inspired fraction is its circuit
            fraction, as the module docstring explains.

    Returns:
        The dimensionless quotient, or `None` when the inspired fraction is
        below `WASH_IN_DENOMINATOR_FLOOR_FRACTION`.
    """

    if inspired_partial_pressure_fraction < WASH_IN_DENOMINATOR_FLOOR_FRACTION:
        return None

    return alveolar_partial_pressure_fraction / inspired_partial_pressure_fraction


def is_wash_in(ratio: float) -> bool:
    """Return whether a computed quotient is inside the uptake regime.

    This is the second boundary of the domain that the module docstring
    states, written as a predicate. The chart and `read_wash_in` both use it,
    so they classify a quotient by the same rule rather than each carrying its
    own copy of the comparison.

    Args:
        ratio: A quotient from `wash_in_ratio`.

    Returns:
        `True` when the quotient is at or below `WASH_IN_EQUILIBRIUM_RATIO`
        plus `WASH_IN_ROUNDING_ALLOWANCE`.
    """

    return ratio <= WASH_IN_EQUILIBRIUM_RATIO + WASH_IN_ROUNDING_ALLOWANCE


def read_wash_in(
    alveolar_partial_pressure_fraction: float, inspired_partial_pressure_fraction: float
) -> WashInReading:
    """Read F_A/F_I at one moment, returning the value to plot and its domain.

    This is one call rather than a value function and a domain function. So
    the trace and the sentence beside it come from one evaluation of one rule,
    and they cannot come to disagree.

    Args:
        alveolar_partial_pressure_fraction: $`F_A`$, as a fraction of one
            atmosphere.
        inspired_partial_pressure_fraction: $`F_I`$, as a fraction of one
            atmosphere.

    Returns:
        The reading, whose `plotted_ratio` is a number exactly when its
        `domain` is `WashInDomain.WASH_IN`.
    """

    ratio = wash_in_ratio(alveolar_partial_pressure_fraction, inspired_partial_pressure_fraction)

    if ratio is None:
        return WashInReading(WashInDomain.NO_INSPIRED_AGENT, None)

    if not is_wash_in(ratio):
        return WashInReading(WashInDomain.ELIMINATION, None)

    return WashInReading(WashInDomain.WASH_IN, ratio)
