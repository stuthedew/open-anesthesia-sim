r"""The $`F_A/F_I`$ ratio that the uptake literature plots, and the range where it is valid.

This module is pure arithmetic over two modelled fractions. It imports no
interface toolkit. Nothing here reads simulation state, builds a control, or
formats a string.

The ratio has its own module so that it can be read, cited and tested without
loading the dashboard that draws it. `CLAUDE.md`'s safety-critical standard
requires this, because the ratio is a clinically meaningful displayed value
derived from two other values. `docs/INTERFACE.md` § "F_A/F_I as a displayed ratio"
specifies the quantity, and this module implements that specification, as
`app/formatting.py` implements § "Displayed precision". Its
tests are in `tests/unit/test_wash_in.py`.

$`F_A`$ is the modelled alveolar fraction, and $`F_I`$ is the modelled
*inspired* fraction. In this model $`F_I`$ is identical to the
breathing-circuit fraction, $`F_C \equiv F_I`$. That holds because the model
contains one ideal, perfectly mixed circuit with no dead space and no separate
inspiratory and expiratory limbs (`docs/MODEL.md` § "What the model represents"). A
breathing system with several limbs would break that identity, and would make
this ratio wrong too. $`F_I`$ is not the vaporizer dial setting. The circuit
fraction only approaches the dial setting, over the circuit's own time constant.

**Three rules decide when the quotient is a number that this application will
show: a minimum denominator, a maximum of one, and ventilation running.** All
three exist because a plausible-looking number is worse here than no number at
all.

1. *The denominator must be at least one displayed unit.* $`F_I`$ is zero
   before any agent reaches the circuit. It is exactly zero at the start of
   every run, and for the whole of a run in which the vaporizer is never
   opened, so the quotient there is $`0/0`$. It also falls below one
   displayed unit during a washout, once the vaporizer is closed, while the
   patient still holds agent. Rather than treat $`0/0`$ as a
   special case, the rule forms the ratio exactly when the concentration
   readout shows the inspired fraction as a number, `0.01%` or more. It forms
   none when the readout shows `<0.01%` or `0.00%`. The rule reads the
   readout's own rounding, so every inspired value the readout shows either
   always gives a ratio or never does (`PL-FSXD`). A test result is compared
   with a specification limit the same way in pharmaceutical and materials
   testing, rounded to the limit's last decimal place first
   (`docs/INTERFACE.md` § "F_A/F_I as a displayed ratio" cites the
   sources).
2. *The quotient must not exceed one.* The condition $`F_A \le F_I`$ is
   exactly the uptake regime. Alveolar gas gives agent up to the blood, so the
   alveolar fraction stays below the inspired fraction and reaches it only at
   equilibrium. Above one, the alveolar fraction exceeds the inspired one,
   and the number is no longer a wash-in fraction. With ventilation running,
   the patient is then returning agent to the circuit. The caption beside the
   plot names the condition and not a cause (`PL-7PBB`). The curve claims to
   be the textbook wash-in graph, so drawing such a number on it would teach a
   wash-in that went past completion. The rule allows
   `WASH_IN_ROUNDING_ALLOWANCE` above one for rounding, and nothing more,
   because rounding alone can put an equilibrium's quotient a hair above one
   (`PL-N559`).
3. *Alveolar ventilation must be running.* The model moves agent between the
   circuit and the alveoli only through the term $`\dot V_A (F_I - F_A)`$
   (`build_system_matrix` in `core/governing_equations.py`). At zero alveolar
   ventilation that term is zero, so nothing the ratio does is uptake from the
   circuit. The ratio still moves. Fresh gas washes the circuit toward the
   dial, and blood takes agent from the alveoli or returns it. Drawn on the
   wash-in curve, that movement would read as the alveoli filling, though no
   agent reaches them (`PL-49D5`). So a state that a step at zero alveolar
   ventilation reached has no ratio to draw, and the caption beside the plot
   says that ventilation is zero. The rule reads the ventilation of the step
   that reached the state, because that step made it. The state at the second
   ventilation is stopped was reached with ventilation running, so the trace
   ends at that second. Zero is compared exactly, for the reason
   `core/__init__.py` § "Zero flow is tested with `== 0.0`, never against a
   tolerance" gives.

A reading applies rule 1 first, because without a denominator there is no
ratio to say anything about. It applies rule 3 next, because at zero
ventilation a ratio above one is no more elimination than one below it is
uptake. Rule 2 comes last.

`WASH_IN_EQUILIBRIUM_RATIO` is the boundary that rule 2 uses. It is a
*modelled* value, not a plotting choice, because it is where net uptake stops.
That is why the chart draws it as a labelled reference line and ends the trace
on it, rather than at the top of a frame.

No rule invents a value, substitutes a default, or clamps a value into range.
Where the ratio is outside its domain, this module returns no number to draw
and says which rule excluded it (`read_wash_in_with_ventilation`). The
interface can then
state the cause instead of drawing a number it cannot stand behind. For the
same reason, one call returns both the number and whether it is inside its
domain. A caption saying that the inspired concentration is too low to divide
by, beside a trace that is still drawing, would be two displays disagreeing
about the same instant.
"""

import struct
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from anesthesia_sim.app.formatting import (
    CONCENTRATION_DISPLAY_RESOLUTION_PERCENT,
    reaches_concentration_display_resolution,
)
from anesthesia_sim.core.concentration import Fraction, Percent, fraction_from_percent
from anesthesia_sim.core.rounding import WASH_IN_ROUNDING_ALLOWANCE
from anesthesia_sim.core.supported_ranges import AlveolarVentilation

__all__ = [
    "WASH_IN_DENOMINATOR_FLOOR_FRACTION",
    "WASH_IN_EQUILIBRIUM_RATIO",
    "WashInDomain",
    "WashInReading",
    "is_ventilated",
    "is_wash_in",
    "read_wash_in",
    "read_wash_in_with_ventilation",
    "wash_in_quotient",
    "wash_in_ratio",
]


def _smallest_fraction_shown_as_one_display_step() -> Fraction:
    """Return the smallest fraction that the concentration readout shows as `0.01%` or more.

    The readout rounds, so the boundary is about half a display step, near
    0.005%. Its exact value depends on how the binary fraction rounds, so it
    is found by asking the readout rather than written down. The search halves
    the interval between two adjacent doubles. It starts from zero, which the
    readout shows as `0.00%`, and from one whole display step, which it shows
    as `0.01%`. Positive doubles sort in the same order as their bit patterns,
    so the search runs over the integers those patterns spell and ends after
    at most 64 halvings, on the boundary to the last bit.
    """

    def bits(value: float) -> int:
        packed: int = struct.unpack("<q", struct.pack("<d", value))[0]
        return packed

    def value_of(pattern: int) -> float:
        unpacked: float = struct.unpack("<d", struct.pack("<q", pattern))[0]
        return unpacked

    below = bits(0.0)
    reaching = bits(fraction_from_percent(Percent(CONCENTRATION_DISPLAY_RESOLUTION_PERCENT)))

    while reaching - below > 1:
        middle = (below + reaching) // 2

        if reaches_concentration_display_resolution(Fraction(value_of(middle))):
            reaching = middle
        else:
            below = middle

    return Fraction(value_of(reaching))


#: The smallest inspired fraction from which the ratio may be formed. This is
#: rule 1 of the module docstring.
#:
#: The value is derived rather than chosen. It is the smallest fraction that
#: the concentration readout shows as `0.01%` or more
#: (`reaches_concentration_display_resolution`). So a change to the readout's
#: resolution or its rounding moves this value with it, and no second constant
#: is left behind to go stale. Until `PL-FSXD` the limit was one whole display
#: step, 0.01%, so an inspired fraction from 0.005% up to 0.01% was shown as
#: `0.01%` beside a plot that formed no ratio from it.
WASH_IN_DENOMINATOR_FLOOR_FRACTION: Final = _smallest_fraction_shown_as_one_display_step()

#: The ratio at which $`F_A = F_I`$. With ventilation running, net uptake from
#: the circuit stops there, so it is the wash-in curve's asymptote and rule 2
#: of the module docstring. Above this ratio the alveolar fraction exceeds the
#: inspired one, and the ratio is not a wash-in fraction (`PL-7PBB`).
WASH_IN_EQUILIBRIUM_RATIO: Final = 1.0


class WashInDomain(StrEnum):
    """Whether $`F_A/F_I`$ is a wash-in fraction, and if not, why not.

    There are four outcomes rather than a `None`, because the interface has
    to say *which* outcome a blank stretch of curve stands for: an inspired
    concentration too low to divide by, an alveolar concentration above the
    inspired, or ventilation at zero. A reader told only that the trace
    stopped would have no way to tell them apart.
    """

    WASH_IN = "wash_in"
    """Inside the domain: the quotient is a wash-in fraction from 0 to 1."""

    NO_INSPIRED_AGENT = "no_inspired_agent"
    """The denominator is below `WASH_IN_DENOMINATOR_FLOOR_FRACTION`."""

    ELIMINATION = "elimination"
    """The alveolar fraction exceeds the inspired fraction, so the ratio is not a wash-in fraction.

    With ventilation running, agent then comes back to the circuit, which is
    the case the name describes. Text written from this member still names
    the condition and not elimination (`PL-7PBB`). A state reached at zero
    alveolar ventilation is `VENTILATION_STOPPED` instead, whatever its ratio,
    where the reading knows the ventilation (`read_wash_in_with_ventilation`).
    """

    VENTILATION_STOPPED = "ventilation_stopped"
    """The step that reached the state ran at zero alveolar ventilation (rule 3).

    No agent moved between the circuit and the alveoli in that step, so the
    ratio is not a wash-in fraction, whichever side of one it is on.
    """


@dataclass(frozen=True, slots=True)
class WashInReading:
    """The wash-in display's reading of one pair of modelled fractions.

    Attributes:
        domain: Which of `WashInDomain`'s four cases this pair falls in.
        plotted_ratio: The dimensionless quotient where it is a wash-in
            fraction, and `None` in the other three cases. It is never a
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
    plots the result as a wash-in fraction should call
    `read_wash_in_with_ventilation` instead.

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


def wash_in_quotient(
    alveolar_partial_pressure_fraction: float,
    inspired_partial_pressure_fraction: float,
    *,
    ventilated: bool,
) -> float | None:
    """Return the quotient that the wash-in plot compares at one state, by rules 1 and 3.

    It is `wash_in_ratio`'s quotient where a ventilated step reached the
    state. It is `None` where the inspired fraction is too small to divide by,
    or where a step at zero alveolar ventilation reached the state. It may
    exceed one, because the plot compares a quotient past equilibrium to
    choose the column at which a stretch meets the line. Each drawn column's
    quotient (`DrawnWindow.wash_in_quotients`) and each second's in the search
    for columns between two drawn ones (`controller._with_extremes`) are
    formed here. So the two agree about which seconds have a quotient.

    Args:
        alveolar_partial_pressure_fraction: $`F_A`$, as a fraction of one
            atmosphere.
        inspired_partial_pressure_fraction: $`F_I`$, as a fraction of one
            atmosphere.
        ventilated: Whether the step that reached the state ran with alveolar
            ventilation above zero (`is_ventilated`).
    """

    if not ventilated:
        return None

    return wash_in_ratio(alveolar_partial_pressure_fraction, inspired_partial_pressure_fraction)


def is_wash_in(ratio: float) -> bool:
    """Return whether a computed quotient is inside the uptake regime.

    The function writes rule 2 of the module docstring as a predicate. That
    rule sets the upper boundary of the ratio's domain. The chart and
    `read_wash_in` both use this function, so they classify a quotient by the
    same rule rather than each carrying its own copy of the comparison.

    Args:
        ratio: A quotient from `wash_in_ratio`.

    Returns:
        `True` when the quotient is at or below `WASH_IN_EQUILIBRIUM_RATIO`
        plus `WASH_IN_ROUNDING_ALLOWANCE`.
    """

    return ratio <= WASH_IN_EQUILIBRIUM_RATIO + WASH_IN_ROUNDING_ALLOWANCE


def is_ventilated(alveolar_ventilation_l_min: AlveolarVentilation) -> bool:
    """Return whether a step ran with alveolar ventilation above zero.

    The function writes rule 3 of the module docstring as a predicate. The
    chart's columns and the caption's reading both use it, so they cannot
    disagree about which states had ventilation.

    Args:
        alveolar_ventilation_l_min: The alveolar ventilation of the step that
            reached the state, in L/min.

    Returns:
        `False` at exactly zero, and `True` otherwise.
    """

    return alveolar_ventilation_l_min != 0.0


def read_wash_in(
    alveolar_partial_pressure_fraction: float, inspired_partial_pressure_fraction: float
) -> WashInReading:
    """Read F_A/F_I from two fractions alone, by rules 1 and 2, returning the value and its domain.

    This is one call rather than a value function and a domain function. So
    the trace and the sentence beside it come from one evaluation of one rule,
    and they cannot come to disagree.

    It does not know the ventilation, so it cannot apply rule 3. Its result is
    the plot's reading only for a state that a ventilated step reached. A
    reader of a run's state calls `read_wash_in_with_ventilation`.

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


def read_wash_in_with_ventilation(
    alveolar_partial_pressure_fraction: float,
    inspired_partial_pressure_fraction: float,
    alveolar_ventilation_l_min: AlveolarVentilation,
) -> WashInReading:
    """Read F_A/F_I at one stored second by all three rules, returning the value and its domain.

    The rules apply in the order the module docstring gives: rule 1, then
    rule 3, then rule 2.

    Args:
        alveolar_partial_pressure_fraction: $`F_A`$, as a fraction of one
            atmosphere.
        inspired_partial_pressure_fraction: $`F_I`$, as a fraction of one
            atmosphere.
        alveolar_ventilation_l_min: The alveolar ventilation of the step that
            reached the state, in L/min (`RunDefinition.reaching_segment_at`).

    Returns:
        The reading, whose `plotted_ratio` is a number exactly when its
        `domain` is `WashInDomain.WASH_IN`.
    """

    reading = read_wash_in(alveolar_partial_pressure_fraction, inspired_partial_pressure_fraction)

    if reading.domain is WashInDomain.NO_INSPIRED_AGENT or is_ventilated(
        alveolar_ventilation_l_min
    ):
        return reading

    return WashInReading(WashInDomain.VENTILATION_STOPPED, None)
