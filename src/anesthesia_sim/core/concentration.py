"""The dimensionless forms one concentration is written in, and the crossings
between them.

This module is the implementation of `docs/MODEL.md` § "Concentrations", and
takes its subject from that section rather than from the word in its own name:
the section defines the model's fraction, the percent of an atmosphere the same
quantity is quoted in, and the multiple of 1 MAC the interface rescales it to.
All three are here for that reason (`PL-6KNM`, `PL-BQ46`).

§ "Concentrations" states that every model concentration is a dimensionless
partial-pressure-equivalent fraction from 0 through 1. Two other places do not
use that convention and cannot: a vaporizer dial and a MAC are quoted in
percent of an atmosphere, which is how the agent data files carry them and how
the interface shows them. So one quantity arrives in two forms, differing by a
factor of 100, and every crossing between them is a place where a correct
number can acquire the wrong meaning.

**What the types buy, and what they do not.** `Fraction` and `Percent` are
`float` subclasses, each checked against its range when it is built - 0
through 1 for a fraction, 0 through 100 for a percent - and `MacMultiple` is a
`NewType` over `float`. `mypy` refuses any one of the three where another is
wanted and refuses a bare `float` for any of them, and a value built as a
`Fraction` or a `Percent` is the proof that its range was checked, so nothing
that holds one checks it again. What either may be built from, an `int` or a
`float` and nothing else, and how either holds a zero, without a sign, are
decided once for every checked type in `core/checked_number.py` (`PL-LLMN`). That is the pattern
`.claude/rules/core-domain.md` § "A quantity with a check of its own is a
type, checked once" states, applied here by `PL-4R3W`: until then both were
`NewType`s, which the interpreter erases, and their ranges were checked by hand
at each of the twelve places a value entered. Four limits are worth stating,
because each of them is a way this could be read as promising more than it
does:

- **Arithmetic erases them.** `Fraction(0.5) * 2.0` and `f + f` are both plain
  `float`, at run time as under `mypy`. A computed value carries no proof, so
  it is checked where it is built into the type again - which is why
  `AgentUptakeSystem._write_state_vector` builds each fraction a step computes
  as a `Fraction`, under the name of the compartment that will hold it, and why
  the governing equations are not annotated and could not usefully be.
- **`mypy` reads `src/` and not `tests/`, and passes a value typed `Any`.** So
  each place that holds one - a compartment's setter, the driving fraction a
  compartment's own closed form takes, `BreathingCircuit` built or set, the
  `BreathingCircuitState` a rollback restores it from,
  `UptakeEquationSettings`, and the `AgentParameters` an agent's data file is
  parsed into - first calls `require_fraction` or `require_percent`, which
  refuse with `TypeError` anything not built as the type, a bare `float`
  included. What only carries a value onward checks nothing.
- **They cannot catch a wrong magnitude.** `Percent(0.02)` and `Percent(2.0)`
  are 0.02% and 2%, and both are valid percents. What is caught is a *missing
  conversion*: a `Fraction` handed where a `Percent` is wanted is refused by
  `mypy` and, since `PL-4R3W`, by `require_percent` at run time too, which says
  to convert it rather than rebuild it. Rebuilding it is refused as well:
  `mypy` passes `Percent(fraction)`, a `Fraction` being a `float`, so each
  constructor refuses a value of the other type with `TypeError` and the same
  advice. A percent built from a fraction's *value* - a bare `float` that held
  one - is not caught by anything: every fraction is also a valid percent,
  under 1% and so below every agent's vaporizer maximum, and
  `require_within_vaporizer_maximum` passes it. That is why the dial's writers
  are few and each one passes a value already in percent. `PL-WVSK` measured
  the band when the dial was held as a fraction, before `PL-NJPB`. And the
  run-time refusal stands only where a concentration is held or built: the two
  conversions below, and the formatters built on them, take what they are
  given, so a `Percent` handed to `percent_from_fraction` is refused by `mypy`
  alone.
- **A dial at 100% can carry a computed fraction just past 1, and the type
  refuses it.** Measured 2026-10-04 (`PL-4R3W`): no supported setting computes
  a fraction outside 0 to 1 on either path - the highest anywhere was
  0.18000000000002825, desflurane at its 18% maximum - but a circuit built
  without an agent defaults its vaporizer maximum to 100% (`BreathingCircuit`),
  and a state standing at a 100% dial and propagated exactly stood at
  1.000000000099652 after 24 h, and at 1.0000000002869551 at the worst of its
  minutes on the way, which is the shift's documented cost
  (`core/matrix_exponential.py`, "What it costs"). The stepped path already
  halted there before this type existed, in ten of the twelve corners measured.
  The display path, which builds each plotted value as a `Fraction`
  (`app/chart_frame.py`), now refuses it as well instead of formatting it as
  100.00%, and how that halt is shown is `PL-7DJK`'s. A 100% dial is outside
  `docs/MODEL.md` § "Supported input ranges" and reachable from no
  application path, so this is the type's documented limit and not a reason
  to leave a range unchecked.

**Why one module rather than a convention.** Before `PL-WVSK` the factor 100
was written out twelve times across six modules. Six of the twelve were on the
path to a displayed clinical value - the readouts, the MAC multiples, the
plotted points, and the delivered-concentration slider in both directions -
and two more quoted a refused dial setting back to the reader. `CLAUDE.md`
treats the correct number under the wrong units as a safety failure in its own
right, so twelve hand-written conversions were twelve chances at one.
"""

from __future__ import annotations

from typing import Final, NewType

from anesthesia_sim.core.checked_number import negative_zero_as_zero, require_a_number, shown
from anesthesia_sim.core.exceptions import SimulationConfigurationError

PERCENT_PER_UNIT_FRACTION: Final = 100.0
"""The factor between the two, written once.

A percent *is* a fraction of one atmosphere scaled by a hundred, so this is a
definition rather than a measured constant and carries no provenance note.
"""


class Fraction(float):
    """A dimensionless partial-pressure-equivalent fraction from 0 through 1,
    checked against that range when built.

    The model's own convention, and the only one `core/`'s governing equations
    carry. `docs/MODEL.md` § "Concentrations" is the definition. It compares
    and computes as the `float` it was built from, and arithmetic on it returns
    a plain `float`, as the module docstring says.

    `name` is what a refusal calls the value, and it is the whole of what a
    reader of the halted-run notice is told about which value was refused.
    Five compartments and the circuit each hold a fraction, so where more than
    one could be the one refused, the caller names it -
    `"alveolar partial_pressure_fraction"`, as
    `AgentUptakeSystem._write_state_vector` does for each compartment it writes
    (`PL-SPN6`). It defaults to the type's own word.

    Built from minus zero it holds zero, the concentration it is, so
    `format_percent` never prints a fraction with a sign; what is not an `int`
    or a `float` is refused before the range is read (`core/checked_number.py`,
    `PL-LLMN`). The closed range refuses NaN on its own, since a NaN compares
    false against either bound, and compares an `int` past the float range
    exactly, naming one too long to print by how long it is (`shown`).

    Raises:
        TypeError: the value is a `Percent`, which is a conversion missed
            rather than a value refused, so it is told to convert, as
            `require_fraction` tells it; or it is not an `int` or a `float`,
            or is a `bool`, which is a programming error in the caller.
        SimulationConfigurationError: the value is not finite, or is outside
            0 to 1. The message gives the value under `name`.
    """

    __slots__ = ()

    def __new__(cls, fraction: float, *, name: str = "fraction") -> Fraction:
        if isinstance(fraction, Percent):
            raise _percent_where_a_fraction_belongs(name, fraction)

        require_a_number(name, fraction)

        if not 0.0 <= fraction <= 1.0:
            raise SimulationConfigurationError(
                f"{name} of {shown(fraction)} is outside 0 to 1, the range a fraction of one "
                'atmosphere takes (docs/MODEL.md, "Concentrations")'
            )

        return super().__new__(cls, negative_zero_as_zero(fraction))


class Percent(float):
    """The same quantity as a percent of one atmosphere, from 0 through 100,
    checked against that range when built.

    What a vaporizer dial reads and what the agent data files store, a MAC
    among them. No governing equation takes one. A MAC is held as one because
    every agent shipped has one under 100%, and that is an instance rather
    than a rule: nitrous oxide's MAC was measured at 1.04 atm (Hornbein TF et
    al., Anesth Analg 1982;61(7):553-556; retrieved from PubMed, PMID 7201254,
    and verified against the abstract 2026-10-05), and `ROADMAP.md` plans that
    agent for v0.8.0. `core/parameters.py`'s `PositivePercent`
    refuses its MAC at load already, and `app/dashboard_frame.py`'s
    `off_scale_notice` builds its axis top, three MACs, as a `Percent`, which
    refuses any agent's MAC above 33.3%. A dial's real limit is
    the vaporizer maximum of the agent in use, which is not this type's range
    but a relation between two percents, and is checked where both are held
    (`core/validation.py`'s `require_within_vaporizer_maximum`). It compares
    and computes as the `float` it was built from, and arithmetic on it returns
    a plain `float`.

    `name` is what a refusal calls the value, as `Fraction` takes it, and it
    holds minus zero as zero and refuses what is not a number as `Fraction`
    does.

    Raises:
        TypeError: the value is a `Fraction`, for the reason `Fraction` gives
            about a `Percent`; or it is not an `int` or a `float`, or is a
            `bool`.
        SimulationConfigurationError: the value is not finite, or is outside
            0 to 100. The message gives the value under `name`.
    """

    __slots__ = ()

    def __new__(cls, percent: float, *, name: str = "percent") -> Percent:
        if isinstance(percent, Fraction):
            raise _fraction_where_a_percent_belongs(name, percent)

        require_a_number(name, percent)

        if not 0.0 <= percent <= PERCENT_PER_UNIT_FRACTION:
            raise SimulationConfigurationError(
                f"{name} of {shown(percent)} is outside 0 to 100, the range a percent of one "
                'atmosphere takes (docs/MODEL.md, "Concentrations")'
            )

        return super().__new__(cls, negative_zero_as_zero(percent))


MacMultiple = NewType("MacMultiple", float)
"""The same quantity against the running agent's 1 MAC instead of an atmosphere.

`docs/MODEL.md` § "Concentrations" defines it as $`100F/\\mathrm{MAC}_\\%`$ and
§ "MAC multiples as a display unit" states what the quotient does and does not
assert. It is dimensionless like `Fraction` and is **not** one: a `Fraction` is
of an atmosphere, a `MacMultiple` is of a per-agent divisor, and the two are
small numbers of the same magnitude, so neither reads as wrong in place of the
other. Sevoflurane at 1 MAC is `Fraction(0.02)` against a MAC-awake
`MacMultiple(0.34)`, and a MAC-awake band drawn at 0.02 of MAC instead of 0.34
is a clinical reference in the wrong place with nothing on screen saying so
(`PL-BQ46`).

Unbounded above, deliberately: a compartment may sit above 1 MAC, and the one
value that is bounded — `MacAwakeReference.fraction_of_mac`, which must stay
below 1 MAC — is held there by `core/parameters.py`'s payload validator rather
than by this type, which checks nothing. That is why it stays a `NewType`
where `Fraction` and `Percent` became checked types (`PL-4R3W`): a type built
through a range check needs a range, and this one has only a floor that no
computation it comes from can cross. One type rather than two because a ratio
to MAC and a multiple of MAC are one kind differing only in range, and a second
`NewType` for a range would be the multiplicity this one exists to remove.

Nothing in `core/` computes one; `app/formatting.py`'s `mac_multiple()` is the
whole arithmetic. The type is here because `core/parameters.py` *stores* one,
and because this module is where the forms of one concentration are declared.
"""


def _percent_where_a_fraction_belongs(name: str, percent: Percent) -> TypeError:
    """The refusal of a `Percent` handed where a `Fraction` belongs.

    Written once for the two places that make it: `require_fraction`, handed
    one, and `Fraction`, asked to rebuild one.
    """

    return TypeError(
        f"{name} of {percent!r} is a Percent, not a Fraction: convert it with "
        "fraction_from_percent, since a Fraction built from a percent's value holds a "
        "concentration a hundred times too large"
    )


def _fraction_where_a_percent_belongs(name: str, fraction: Fraction) -> TypeError:
    """The mirror of `_percent_where_a_fraction_belongs`, for `require_percent` and `Percent`."""

    return TypeError(
        f"{name} of {fraction!r} is a Fraction, not a Percent: convert it with "
        "percent_from_fraction, since a Percent built from a fraction's value holds a "
        "concentration a hundred times too small"
    )


def require_fraction(name: str, fraction: object) -> None:
    """Require a value that was built as a `Fraction`, and so checked.

    The runtime half of the type, for the callers `mypy` does not read: a test,
    a notebook, or a value typed `Any`. It checks the type and not the range,
    which the constructor has already checked, and it runs where a fraction is
    held - each compartment's setter, the driving fraction a compartment's own
    closed form takes, `BreathingCircuit` when it is built or set, and the
    `BreathingCircuitState` a rollback restores it from - so a bare `float` is
    refused once, before anything changes. Until `PL-4R3W` a range
    check of the same name in `core/validation.py` stood at those places and
    was made again at each; this is the type's check that replaced it.

    A `Percent` is named as one and told to convert rather than to rebuild: a
    `Fraction` built from a percent's value holds a concentration a hundred
    times too large, which is the missing conversion this module's types exist
    to refuse, and `Fraction` refuses the rebuild with the same message.

    Args:
        name: What the value is where it is handed in, for the message. A
            fraction is the alveolar or the venous one by where it is held
            rather than by its type, so the name is the caller's.
        fraction: What was handed in.

    Raises:
        TypeError: `fraction` is not a `Fraction` - a bare `float` included,
            whatever its value. This is a programming error in the caller
            rather than a rejected setting, so it is not an
            `AnesthesiaSimulationError` (`core/exceptions.py`).
    """

    if isinstance(fraction, Fraction):
        return

    if isinstance(fraction, Percent):
        raise _percent_where_a_fraction_belongs(name, fraction)

    raise TypeError(
        f"{name} of {fraction!r} was not built as Fraction, it is {type(fraction).__name__}: "
        "build it as Fraction(...) where it is computed, which checks it against 0 to 1 once "
        '(docs/MODEL.md, "Concentrations")'
    )


def require_percent(name: str, percent: object) -> None:
    """Require a value that was built as a `Percent`, and so checked.

    The runtime half of the type, as `require_fraction` is for a fraction. It
    runs where a percent is held - `BreathingCircuit`, built or set,
    `UptakeEquationSettings`, and the `AgentParameters` holding an agent's MAC
    and vaporizer maximum - and it is the one check that refuses a fraction
    reaching the dial at run time as well as under `mypy`.

    A `Fraction` is named as one and told to convert rather than to rebuild: a
    `Percent` built from a fraction's value holds a concentration a hundred
    times too small, and is under every agent's vaporizer maximum, so nothing
    after this would refuse it. `Percent` refuses the rebuild with the same
    message.

    Args:
        name: What the value is where it is handed in - the dial, or its
            maximum - for the message.
        percent: What was handed in.

    Raises:
        TypeError: `percent` is not a `Percent` - a bare `float` included,
            whatever its value - for the reason `require_fraction` gives.
    """

    if isinstance(percent, Percent):
        return

    if isinstance(percent, Fraction):
        raise _fraction_where_a_percent_belongs(name, percent)

    raise TypeError(
        f"{name} of {percent!r} was not built as Percent, it is {type(percent).__name__}: "
        "build it as Percent(...) where it is set, which checks it against 0 to 100 once "
        '(docs/MODEL.md, "Concentrations")'
    )


def fraction_from_percent(percent: Percent) -> Fraction:
    """Convert a percent of one atmosphere to the model's fraction.

    Checks nothing of the range. The percent's range was checked when it was
    built, and the quotient is built as a `Fraction`, which cannot refuse it:
    division rounds monotonically and 100 divides to exactly 1, so a percent
    from 0 through 100 gives a fraction from 0 through 1 (`PL-4R3W` measured a
    million of them). What is handed in is required to be a number first, as
    the constructors require it, because the arithmetic runs before either
    constructor sees the value: `True` divided by a hundred was a fraction of
    0.01, and a `str` was refused as Python's unsupported operand (`PL-LLMN`).
    A `Fraction` handed in as the percent is `PL-SWD1`'s.

    Raises:
        TypeError: `percent` is not an `int` or a `float`, or is a `bool`
            (`core/checked_number.py`).
    """

    require_a_number("percent", percent)

    return Fraction(percent / PERCENT_PER_UNIT_FRACTION)


def percent_from_fraction(fraction: Fraction) -> Percent:
    """Convert the model's fraction to a percent of one atmosphere.

    The display direction, and the reason this pair is not one function with a
    flag: which way a call goes is the thing a reader has to be able to see.

    The product is built as a `Percent`, which cannot refuse it for a
    `Fraction`: multiplication rounds monotonically and 1 gives exactly 100.
    Handed a value that was never a `Fraction` - an impossible negative, from a
    caller `mypy` does not read - it refuses that value here, before anything
    can display it (`PL-4R3W`). What is handed in is required to be a number
    first, as `fraction_from_percent` says: `True` times a hundred was a
    percent of 100, inside the range, and `format_percent(True)` printed
    `100.00%` (`PL-LLMN`). A `Percent` handed in as the fraction is
    `PL-SWD1`'s.

    Raises:
        TypeError: `fraction` is not an `int` or a `float`, or is a `bool`
            (`core/checked_number.py`).
        SimulationConfigurationError: `fraction` times a hundred is outside 0
            to 100, which no `Fraction` can make.
    """

    require_a_number("fraction", fraction)

    return Percent(fraction * PERCENT_PER_UNIT_FRACTION)
