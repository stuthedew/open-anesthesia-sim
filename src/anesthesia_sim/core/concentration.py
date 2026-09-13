"""The two conventions one concentration is written in, and the only crossing
between them.

`docs/MODEL.md` § "Concentrations" states that every model concentration is a
dimensionless partial-pressure-equivalent fraction from 0 through 1. Two other
places do not use that convention and cannot: a vaporizer dial and a MAC are
quoted in percent of an atmosphere, which is how the agent data files carry
them and how the interface shows them. So one quantity arrives in two forms,
differing by a factor of 100, and every crossing between them is a place where
a correct number can acquire the wrong meaning.

**What the types buy, and what they do not.** `Fraction` and `Percent` are
`NewType`s over `float`, so `mypy` refuses a `Percent` where a `Fraction` is
wanted and refuses a bare `float` for either. That is the whole of the
guarantee. Three limits are worth stating because each of them is a way this
could be read as promising more than it does:

- **Arithmetic erases them.** Measured 2026-09-13 under this project's `mypy`:
  `Fraction(0.5) * 2.0` and `f + f` are both plain `float`. A `NewType` marks a
  value where it is *passed*, never where it is *computed*, so it can only ever
  guard a boundary - which is why the governing equations are not annotated and
  could not usefully be.
- **They are erased at runtime too.** `Fraction(x)` is `x`; nothing checks
  anything. `core/validation.py`'s `require_concentration_fraction` is what
  rejects a value outside [0, 1], and it is unaffected by any of this.
- **They cannot catch a wrong magnitude.** `Fraction(0.0005)` and
  `Fraction(0.05)` are 0.05% and 5%, and both type-check. `PL-WVSK` measured
  that band: it is bounded above by the agent's own vaporizer maximum, because
  `BreathingCircuit._require_deliverable` refuses anything above it. What is
  caught here is a *missing conversion*, which is the error that produces those
  two values from one slider reading.

**Why one module rather than a convention.** Before `PL-WVSK` the factor 100
was written out twelve times across six modules. Six of the twelve were on the
path to a displayed clinical value - the readouts, the MAC multiples, the
plotted points, and the delivered-concentration slider in both directions -
and two more quoted a refused dial setting back to the reader. `CLAUDE.md`
treats the correct number under the wrong units as a safety failure in its own
right, so twelve hand-written conversions were twelve chances at one.
"""

from typing import Final, NewType

Fraction = NewType("Fraction", float)
"""A dimensionless partial-pressure-equivalent fraction from 0 through 1.

The model's own convention, and the only one `core/`'s governing equations
carry. `docs/MODEL.md` § "Concentrations" is the definition.
"""

Percent = NewType("Percent", float)
"""The same quantity as a percent of one atmosphere, from 0 through 100.

What a vaporizer dial reads, what a MAC is published as, and what the agent
data files store. No governing equation takes one.
"""

PERCENT_PER_UNIT_FRACTION: Final = 100.0
"""The factor between the two, written once.

A percent *is* a fraction of one atmosphere scaled by a hundred, so this is a
definition rather than a measured constant and carries no provenance note.
"""


def fraction_from_percent(percent: Percent) -> Fraction:
    """Convert a percent of one atmosphere to the model's fraction.

    Does not validate: a fraction reaching a compartment is checked by
    `core/validation.py`'s `require_concentration_fraction`, and a percent
    read from a data file is checked by `core/parameters.py`'s
    `PositivePercent`. Putting a third check here would mean a caller could
    not tell which one had refused.
    """

    return Fraction(percent / PERCENT_PER_UNIT_FRACTION)


def percent_from_fraction(fraction: Fraction) -> Percent:
    """Convert the model's fraction to a percent of one atmosphere.

    The display direction, and the reason this pair is not one function with a
    flag: which way a call goes is the thing a reader has to be able to see.
    """

    return Percent(fraction * PERCENT_PER_UNIT_FRACTION)
