r"""The $`F_A/F_I`$ ratio the uptake literature plots, and where it holds.

Pure arithmetic over two modelled fractions, independent of Flet and of the
scientific core. Nothing here reads simulation state, builds a control, or
formats a string.

Why it is its own module. `docs/MODEL.md` § "F_A/F_I as a displayed ratio"
is where the quantity is specified, and this is where that specification
terminates - the same relationship `app/formatting.py` has to § "Displayed
precision". The ratio is a clinically meaningful displayed value derived
from two others, so `CLAUDE.md`'s safety-critical standard requires it to be
readable, citable and testable without loading the dashboard that draws it.
`tests/unit/test_wash_in.py` is what pins it.

**What the numerator and the denominator are.** $`F_A`$ is the modelled
alveolar fraction and $`F_I`$ the modelled *inspired* fraction, which in
this model is the breathing-circuit fraction: the identity $`F_C \equiv
F_I`$ holds because the model contains one ideal, perfectly mixed circuit
with no dead space and no separate inspiratory and expiratory limbs
(`docs/MODEL.md` § "Model boundary"). It is not the vaporizer dial, which
the circuit only approaches over its own time constant. A multi-limb
breathing system would break the identity, and this ratio with it.

**Two rules bound where the quotient is a number this application will
show**, and both exist because a plausible-looking number is worse here
than nothing at all:

1. *The denominator must be at least one displayed unit.* $`F_I`$ is zero
   before any agent reaches the circuit - exactly zero at the start of every
   run, and for the whole of a run whose vaporizer is never opened - so the
   quotient is $`0/0`$ there. Rather than special-casing that one point, the
   floor is the smallest inspired concentration the interface itself reports
   as non-zero, so the ratio is never formed from a denominator the display
   shows as `0.00%`.
2. *The quotient must not exceed one.* $`F_A \le F_I`$ is exactly the uptake
   regime: alveolar gas gives agent up to blood, so the alveolar fraction
   stays below the inspired one and reaches it only at equilibrium. Above
   one the tissues are returning agent faster than it is being delivered -
   elimination, not wash-in - and the number is no longer a wash-in
   fraction, whatever its arithmetic. Drawing it on a curve whose whole
   claim is "this is the textbook wash-in graph" would teach a wash-in that
   went past completion.

Neither rule invents a value, substitutes a default, or clamps one into
range: where the ratio is outside its domain, `read_wash_in` returns no
number to draw and says which rule excluded it, so the interface can state
the reason rather than draw a number it cannot stand behind. Both answers
come out of one call for that reason - a caption saying "no agent in the
circuit yet" beside a trace that is drawing would be the two disagreeing
about the same instant.
"""

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from anesthesia_sim.app.formatting import CONCENTRATION_DISPLAY_RESOLUTION_PERCENT

__all__ = [
    "WASH_IN_DENOMINATOR_FLOOR_FRACTION",
    "WASH_IN_PLOTTED_MAXIMUM",
    "WashInDomain",
    "WashInReading",
    "read_wash_in",
    "wash_in_ratio",
]

#: Smallest inspired fraction the ratio may be formed from.
#:
#: Derived rather than chosen, for the reason `formatting.py` derives the MAC
#: resolution from the percent one: it is
#: `CONCENTRATION_DISPLAY_RESOLUTION_PERCENT` expressed as a fraction, so
#: re-deriving the displayed resolution moves this with it instead of leaving
#: a second constant behind to go stale. Rule 1 of the module docstring.
WASH_IN_DENOMINATOR_FLOOR_FRACTION: Final = CONCENTRATION_DISPLAY_RESOLUTION_PERCENT / 100.0

#: Largest ratio this application plots as a wash-in fraction. Rule 2 of the
#: module docstring: it is the equilibrium value, and above it the run is
#: eliminating agent rather than taking it up.
WASH_IN_PLOTTED_MAXIMUM: Final = 1.0


class WashInDomain(StrEnum):
    """Whether $`F_A/F_I`$ is a wash-in fraction, and if not, why not.

    Three outcomes rather than a `None`, because the interface has to say
    *which* of them a blank stretch of curve is: "no agent has reached the
    circuit yet" and "the patient is now returning agent" are opposite
    situations, and a reader told only that the trace stopped would have no
    way to tell them apart.
    """

    WASH_IN = "wash_in"
    """Inside the domain: the quotient is a wash-in fraction from 0 to 1."""

    NO_INSPIRED_AGENT = "no_inspired_agent"
    """The denominator is below `WASH_IN_DENOMINATOR_FLOOR_FRACTION`."""

    ELIMINATION = "elimination"
    """Alveolar exceeds inspired: agent is coming back, not going in."""


@dataclass(frozen=True, slots=True)
class WashInReading:
    """What one pair of modelled fractions gives the wash-in display.

    Attributes:
        domain: Which of `WashInDomain`'s three cases this pair falls in.
        plotted_ratio: The dimensionless quotient where it is a wash-in
            fraction, and `None` in the other two cases. It is never a
            clamped or substituted value: outside the domain there is no
            number to draw, which is the whole point of the pair.
    """

    domain: WashInDomain
    plotted_ratio: float | None


def wash_in_ratio(
    alveolar_concentration_fraction: float, inspired_concentration_fraction: float
) -> float | None:
    """Divide alveolar by inspired, where the denominator supports it.

    The arithmetic alone, with rule 1 of the module docstring and nothing
    else: the result may exceed one, and a caller plotting it as a wash-in
    fraction wants `plotted_wash_in_ratio` instead.

    Args:
        alveolar_concentration_fraction: $`F_A`$, as a fraction of one
            atmosphere.
        inspired_concentration_fraction: $`F_I`$, as a fraction of one
            atmosphere. This model's inspired fraction is its circuit
            fraction; see the module docstring.

    Returns:
        The dimensionless quotient, or `None` when the inspired fraction is
        below `WASH_IN_DENOMINATOR_FLOOR_FRACTION`.
    """

    if inspired_concentration_fraction < WASH_IN_DENOMINATOR_FLOOR_FRACTION:
        return None

    return alveolar_concentration_fraction / inspired_concentration_fraction


def read_wash_in(
    alveolar_concentration_fraction: float, inspired_concentration_fraction: float
) -> WashInReading:
    """Read F_A/F_I at one moment: the plottable value, and its domain.

    One call rather than a value function and a domain function, so the
    trace and the sentence beside it are produced from one evaluation of
    one rule and cannot come to disagree.

    Args:
        alveolar_concentration_fraction: $`F_A`$, as a fraction of one
            atmosphere.
        inspired_concentration_fraction: $`F_I`$, as a fraction of one
            atmosphere.

    Returns:
        The reading, whose `plotted_ratio` is a number exactly when its
        `domain` is `WashInDomain.WASH_IN`.
    """

    ratio = wash_in_ratio(alveolar_concentration_fraction, inspired_concentration_fraction)

    if ratio is None:
        return WashInReading(WashInDomain.NO_INSPIRED_AGENT, None)

    if ratio > WASH_IN_PLOTTED_MAXIMUM:
        return WashInReading(WashInDomain.ELIMINATION, None)

    return WashInReading(WashInDomain.WASH_IN, ratio)
