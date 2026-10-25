"""The dimensionless forms in which one concentration is written, and the
conversions between them.

This module implements `docs/MODEL.md` § "Concentrations". Its scope comes from
that section rather than from the word in the module's name. The section
defines three forms of one quantity: the model's fraction, the percent of an
atmosphere in which the same quantity is quoted, and the multiple of 1 MAC to
which the interface rescales it. All three live here for that reason
(`PL-6KNM`, `PL-BQ46`).

§ "Concentrations" states that every model concentration is a dimensionless
partial-pressure-equivalent fraction from 0 through 1. Two other quantities do
not use that convention and cannot use it. A vaporizer dial and a MAC are
quoted in percent of an atmosphere. The agent data files store them that way,
and the interface shows them that way. So one quantity arrives in two forms
that differ by a factor of 100. Every conversion between the two forms is a
place where a correct number can take on the wrong meaning.

**What the types guarantee, and what they do not.** `Fraction` and `Percent`
are `float` subclasses. Each is checked against its range when it is built: 0
through 1 for a fraction, and 0 through 100 for a percent. `MacMultiple` is a
`NewType` over `float`. `mypy` rejects any one of the three where another is
expected, and rejects a bare `float` for any of them. A value built as a
`Fraction` or a `Percent` is proof that its range was checked, so no code that
receives one checks its range again. `core/checked_number.py` decides two things once
for every checked type (`PL-LLMN`). The first is what a value may be built
from: an `int` or a `float`, and nothing else. The second is how a zero is
stored: without a sign. This is the pattern that `.claude/rules/core-domain.md`
§ "A quantity with a check of its own is a type, checked once" describes, and
`PL-4R3W` applied it here. Before `PL-4R3W`, both were `NewType`s, which the
interpreter erases, and their ranges were checked by hand at each of the
twelve places where a value entered. Four limits are worth stating, because
each is a way in which the types could be taken to promise more than they do:

- **Arithmetic erases them.** `Fraction(0.5) * 2.0` and `f + f` are both plain
  `float`, both at run time and under `mypy`. A computed value carries no
  proof, so it is checked again where it is built into the type. That is why
  `AgentUptakeSystem._write_state_vector` builds each fraction that a step
  computes as a `Fraction`, under the name of the compartment that will store
  it. It is also why the governing equations are not annotated with these
  types, and could not usefully be.
- **`mypy` checks `src/` and not `tests/`, and accepts a value typed `Any`.**
  So each place that stores one of these values first calls
  `require_fraction` or `require_percent`. Those functions reject with
  `TypeError` anything not built as the type, a bare `float` included. The
  places are a compartment's setter, the driving fraction that a compartment's
  own closed form takes, `BreathingCircuit` when it is built or set, the
  `BreathingCircuitState` from which a rollback restores it,
  `UptakeEquationSettings`, and the `AgentParameters` into which an agent's
  data file is parsed. Since `PL-1DP1`, each of the two conversions below
  makes the same call. Code that only passes a value onward checks nothing.
- **They cannot catch a wrong magnitude.** `Percent(0.02)` and `Percent(2.0)`
  are 0.02% and 2%, and both are valid percents. What the types catch is a
  *missing conversion*. A `Fraction` passed where a `Percent` is expected is
  rejected by `mypy`. Since `PL-4R3W`, `require_percent` also rejects it at
  run time, with a message that says to convert it rather than rebuild it.
  Rebuilding it is rejected as well. `mypy` accepts `Percent(fraction)`,
  because a `Fraction` is a `float`, so each constructor rejects a value of
  the other type with `TypeError` and the same advice. Each constructor also
  rejects a value built as any other checked quantity, such as a step, a
  flow, an instant or a count. It reports that value as a swapped argument,
  not as a missed conversion. To do this, every constructor reads the one
  record of the checked types (`core/checked_number.py`, `PL-979Z`).
  `require_fraction` and `require_percent` also reject such a value where a
  concentration is stored (`PL-CX2C`). Nothing catches a percent built from
  a fraction's *value*, that is, from a bare `float` that held a fraction.
  Every fraction is also a valid percent, in the band below 1%. That band is
  below every agent's vaporizer maximum, so
  `require_within_vaporizer_maximum` accepts the value. That is why the dial
  has few writers, and why each of them passes a value that is already in
  percent. `PL-WVSK` measured the band of values that pass as either form
  when the dial was still stored as a fraction, before `PL-NJPB`. The run-time check applies where a
  concentration is stored or built. Since `PL-SWD1`, it also applies at the
  two conversions below, on which the formatters are built. Each conversion
  rejects a value that is already in the form it returns, before its
  arithmetic runs. Converted again, that value would be a hundred times off,
  under the type that is meant to prove it was checked. Each conversion also
  rejects a value built as any other checked quantity, as the constructors
  do. Until `PL-1DP1`, the conversions accepted a bare `float` as given,
  because a number that nobody built carries no form by which to reject it.
  For the same reason, neither conversion could tell how to convert it.
  `percent_from_fraction(0.5)` was a `Percent` of 50.0 whether the 0.5 was a
  fraction or a 0.5% dial, and `format_percent(0.5)` printed `50.00%` for
  both. So each conversion now checks its argument as every place above
  does, through `require_percent` or `require_fraction`. A bare `float` is
  rejected, and the message names the constructor that should build it
  (project owner, 2026-10-12, ratified, over keeping the number as given,
  which `PL-4R3W` chose). The number that the arithmetic produces is checked
  against its range where the result is built.
- **A dial at 100% can produce a computed fraction just above 1, and the type
  rejects it.** `PL-4R3W` measured this on 2026-10-04. No supported setting
  computes a fraction outside 0 to 1 on either path. The highest value
  anywhere was 0.18000000000002825, for desflurane at its 18% maximum. But a
  circuit built without an agent sets its vaporizer maximum to 100% by
  default (`BreathingCircuit`). A state at a 100% dial, propagated exactly,
  reached 1.000000000099652 after 24 h, and 1.0000000002869551 at its worst
  minute along the way. That excess is the documented cost of the shift
  (`core/matrix_exponential.py`, "What it costs"). The stepped path already
  halted there before this type existed, in ten of the twelve corners
  measured. The display path builds each plotted value as a `Fraction` when
  the frame is assembled (`app/chart_frame.py`). It now rejects such a value
  too, naming the compartment, instead of formatting it as 100.00%. The
  interface then halts the run before any frame is drawn. It reports the
  halt from the controller's run state, not from a snapshot that could fail
  in the same way (`PL-7DJK`). A 100% dial is outside `docs/MODEL.md`
  § "Supported input ranges", and no application path can reach it. So this
  is the type's documented limit, and not a reason to leave a range
  unchecked.

**Why one module rather than a convention.** Before `PL-WVSK`, the factor 100
was written out twelve times across six modules. Six of the twelve were on the
path to a displayed clinical value: the readouts, the MAC multiples, the
plotted points, and the delivered-concentration slider in both directions. Two
more quoted a refused dial setting back to the reader. `CLAUDE.md` treats the
correct number with the wrong units as a safety failure in its own right, so
twelve hand-written conversions were twelve chances of such a failure.
"""

from __future__ import annotations

from typing import Final, NewType, Self

from anesthesia_sim.core.checked_number import (
    CheckedQuantity,
    negative_zero_as_zero,
    require_a_number,
    require_not_another_quantity,
    shown,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError

PERCENT_PER_UNIT_FRACTION: Final = 100.0
"""The factor between a fraction and a percent, written once.

A percent *is* a fraction of one atmosphere multiplied by a hundred. So this
factor is a definition rather than a measured constant, and it carries no
provenance note.
"""


class Fraction(float, CheckedQuantity):
    """A dimensionless partial-pressure-equivalent fraction from 0 through 1,
    checked against that range when built.

    This is the model's own convention, and the only form that the governing
    equations in `core/` use. `docs/MODEL.md` § "Concentrations" defines it. It
    compares and computes as the `float` it was built from, and arithmetic on
    it returns a plain `float`, as the module docstring says.

    `name` is the label that an error message gives the value. It is all that a
    reader of the halted-run notice learns about which value was rejected. Five
    compartments and the circuit each store a fraction. So where more than one
    of them could be the rejected value, the caller supplies the name, such as
    `"alveolar partial_pressure_fraction"`.
    `AgentUptakeSystem._write_state_vector` does this for each compartment it
    writes (`PL-SPN6`). The default name is the type's own word.

    A fraction built from minus zero stores zero, which is the concentration it
    represents, so `format_percent` never prints a fraction with a sign. A
    value that is not an `int` or a `float` is rejected before the range is
    checked (`core/checked_number.py`, `PL-LLMN`). The closed-range test
    rejects NaN without a separate check, because a NaN compares false against
    either bound. The test also compares an `int` beyond the float range
    exactly. When such an `int` is too long to print, the message gives its
    length instead (`shown`).

    Raises:
        TypeError: the value is a `Percent`. That is a missed conversion
            rather than a rejected value, so the message says to convert it,
            as `require_fraction` does. Also raised when the value was built
            as any other checked quantity, such as a step, a flow, an instant
            or a count, which is a swapped argument (`core/checked_number.py`,
            `PL-979Z`). Also raised when the value is not an `int` or a
            `float`, or is a `bool`. Each of these is a programming error in
            the caller.
        SimulationConfigurationError: the value is not finite, or is outside
            0 to 1. The message gives the value under `name`.
    """

    __slots__ = ()

    def __new__(cls, fraction: float, *, name: str = "fraction") -> Fraction:
        if isinstance(fraction, Percent):
            raise _percent_where_a_fraction_belongs(name, fraction)

        require_not_another_quantity(name, fraction, cls)
        require_a_number(name, fraction)

        if not 0.0 <= fraction <= 1.0:
            raise SimulationConfigurationError(
                f"{name} of {shown(fraction)} is outside 0 to 1, the range a fraction of one "
                'atmosphere takes (docs/MODEL.md, "Concentrations")'
            )

        return super().__new__(cls, negative_zero_as_zero(fraction))


class Percent(float, CheckedQuantity):
    """The same quantity as a percent of one atmosphere, from 0 through 100,
    checked against that range when built.

    A vaporizer dial reads in this form, and the agent data files store values
    in it, a MAC among them. No governing equation takes a percent. A MAC is
    stored as a percent because every shipped agent has a MAC below 100%. That
    is an instance, not a rule. Nitrous oxide's MAC was measured at 1.04 atm
    (Hornbein TF et al., Anesth Analg 1982;61(7):553-556; retrieved from
    PubMed, PMID 7201254, and verified against the abstract 2026-10-05), and
    `ROADMAP.md` plans that agent for v0.8.0. `core/parameters.py`'s
    `PositivePercent` already rejects its MAC at load. `app/chart_frame.py`'s
    `assemble_chart_frame` builds the top of the chart's axis, three MACs, as a
    `Percent`, so it rejects any agent whose MAC is above 33.3%. A dial's real
    limit is the vaporizer maximum of the agent in use. That limit is not this
    type's range but a relation between two percents, and it is checked where
    both are stored (`core/validation.py`'s `require_within_vaporizer_maximum`).
    A percent compares and computes as the `float` it was built from, and
    arithmetic on it returns a plain `float`.

    `name` labels the value in an error message, as it does for `Fraction`. A
    percent also stores minus zero as zero, and rejects a value that is not a
    number, as `Fraction` does.

    Raises:
        TypeError: the value is a `Fraction`, for the reason that `Fraction`
            gives about a `Percent`. Also raised when the value was built as
            any other checked quantity, which is a swapped argument, as
            `Fraction` says. Also raised when the value is not an `int` or a
            `float`, or is a `bool`.
        SimulationConfigurationError: the value is not finite, or is outside
            0 to 100. The message gives the value under `name`.
    """

    __slots__ = ()

    def __new__(cls, percent: float, *, name: str = "percent") -> Self:
        if isinstance(percent, Fraction):
            raise _fraction_where_a_percent_belongs(name, percent)

        require_not_another_quantity(name, percent, cls)
        require_a_number(name, percent)

        if not 0.0 <= percent <= PERCENT_PER_UNIT_FRACTION:
            raise SimulationConfigurationError(
                f"{name} of {shown(percent)} is outside 0 to 100, the range a percent of one "
                'atmosphere takes (docs/MODEL.md, "Concentrations")'
            )

        return super().__new__(cls, negative_zero_as_zero(percent))


class MacPercent(Percent):
    """An agent's 1 MAC as a percent of one atmosphere, held as a `Percent` that is above zero.

    Every MAC multiple the interface shows is divided by the MAC. The MAC is
    also the number in the `1 MAC = x%` reference beside the chart. A MAC of
    zero would leave every multiple undefined. So the check that a MAC is
    above zero is made once, when one of these is built. The check sets no
    other lower bound. A MAC far smaller than any real agent's, such as
    0.01%, still prints as `1 MAC = 0.0%`, and one near the smallest float
    makes the multiples overflow. The shipped MACs are 1.2% to 6.0%.
    `AgentParameters` holds the agent's MAC as a `MacPercent`, and each
    formatter in `app/formatting.py` that divides by a MAC takes one
    (`PL-F9TC`). Before that, `AgentParameters` refused a zero MAC through
    `require_positive_finite`, and `app/formatting.py` tested
    `mac_percent > 0` again in five functions.

    It is built from a number, as `Percent` is. It refuses a value already
    built as a `Percent`, as every checked type refuses a value built as
    another type. A dial setting and a MAC are both percents, and neither
    should pass for the other unnoticed. The upper end of the range is
    `Percent`'s 100%, which `Percent` says is an instance rather than a rule.

    Raises:
        TypeError: for the reasons `Percent` gives, or the value was built as
            a `Percent`.
        SimulationConfigurationError: for the reasons `Percent` gives, or the
            value is zero. The message gives the value under `name`.
    """

    __slots__ = ()

    def __new__(cls, percent: float, *, name: str = "mac_percent") -> Self:
        built = super().__new__(cls, percent, name=name)

        if built == 0.0:
            raise SimulationConfigurationError(
                f"{name} of {shown(built)} is not a MAC: a MAC is above 0%, because every "
                "MAC multiple shown divides by it"
            )

        return built


MacMultiple = NewType("MacMultiple", float)
"""The same quantity measured against the running agent's 1 MAC instead of an atmosphere.

`docs/MODEL.md` § "Concentrations" defines it as $`100F/\\mathrm{MAC}_\\%`$, and
§ "MAC multiples as a display unit" states what the quotient does and does not
assert. It is dimensionless like `Fraction`, but it is **not** a `Fraction`. A
`Fraction` is a share of an atmosphere, and a `MacMultiple` is a multiple of a
per-agent divisor. The two are small numbers of the same magnitude, so neither
looks wrong in place of the other. Sevoflurane at 1 MAC is `Fraction(0.02)`,
while its MAC-awake is `MacMultiple(0.34)`. A MAC-awake band drawn at 0.02 of
MAC instead of 0.34 is a clinical reference in the wrong place, with nothing on
screen to say so (`PL-BQ46`).

It has no upper bound, deliberately, because a compartment may sit above 1 MAC.
The one value that is bounded is `MacAwakeReference.fraction_of_mac`, which
must stay below 1 MAC. `core/parameters.py`'s payload validator enforces that
bound, not this type, which checks nothing. That is why `MacMultiple` stays a
`NewType` while `Fraction` and `Percent` became checked types (`PL-4R3W`). A
type built through a range check needs a range. This one has only a lower
bound, which no computation that produces it can cross. There is one type
rather than two because a ratio to MAC and a multiple of MAC are the same kind
of quantity, differing only in range. A second `NewType` for a range would be
the duplication that this one exists to remove.

Nothing in `core/` computes one. `app/formatting.py`'s `mac_multiple()` does
all of the arithmetic. The type lives here because `core/parameters.py`
*stores* one, and because this module declares the forms of one concentration.
"""


def _percent_where_a_fraction_belongs(name: str, percent: Percent) -> TypeError:
    """Return the error for a `Percent` passed where a `Fraction` belongs.

    It is written once for the two places that raise it: `require_fraction`,
    when it is passed a percent, and `Fraction`, when it is asked to rebuild
    one.
    """

    return TypeError(
        f"{name} of {percent!r} is a Percent, not a Fraction: convert it with "
        "fraction_from_percent, since a Fraction built from a percent's value holds a "
        "concentration a hundred times too large"
    )


def _fraction_where_a_percent_belongs(name: str, fraction: Fraction) -> TypeError:
    """Return the error for a `Fraction` passed where a `Percent` belongs.

    It mirrors `_percent_where_a_fraction_belongs`, for `require_percent` and `Percent`.
    """

    return TypeError(
        f"{name} of {fraction!r} is a Fraction, not a Percent: convert it with "
        "percent_from_fraction, since a Percent built from a fraction's value holds a "
        "concentration a hundred times too small"
    )


def require_fraction(name: str, fraction: object) -> None:
    """Require a value that was built as a `Fraction`, and so checked.

    This is the run-time half of the type, for callers that `mypy` does not
    check: a test, a notebook, or a value typed `Any`. It checks the type and
    not the range, because the constructor has already checked the range. It
    runs wherever a fraction is stored: in each compartment's setter, on the
    driving fraction that a compartment's own closed form takes, in
    `BreathingCircuit` when it is built or set, and in the
    `BreathingCircuitState` from which a rollback restores it. Since `PL-1DP1`
    it also runs in `percent_from_fraction`, where the display reads a
    fraction. So a bare `float` is rejected once, before anything changes.
    Until `PL-4R3W`, a range check with the same name in `core/validation.py`
    ran at each of those places, so the same range was checked again at every
    one. This type check replaced it.

    The error message names a `Percent` as one, and says to convert it rather
    than rebuild it. A `Fraction` built from a percent's value would hold a
    concentration a hundred times too large. That is the missing conversion
    that this module's types exist to reject, and `Fraction` rejects the
    rebuild with the same message. `require_not_another_quantity`, which
    `Fraction` also calls, names a value built as any other checked quantity,
    such as a step, a flow, an instant or a count, and gives no advice
    (`core/checked_number.py`). Until `PL-CX2C`, a `SimulationStep(0.05)`
    passed in as a fraction was told to build `Fraction(...)` from it. That
    rebuild would have stored a step's value as a concentration. The value is
    printed through `shown`, so a bare `int` too long for `repr` is named by
    its length instead of escaping as a `ValueError`.

    Args:
        name: What the value is at the place where it is passed in, for the
            message. Whether a fraction is the alveolar or the venous one
            depends on where it is stored, not on its type, so the caller
            supplies the name.
        fraction: The value that was passed in.

    Raises:
        TypeError: `fraction` is not a `Fraction`. That includes a bare
            `float`, whatever its value. This is a programming error in the
            caller rather than a rejected setting, so it is not an
            `AnesthesiaSimulationError` (`core/exceptions.py`).
    """

    if isinstance(fraction, Fraction):
        return

    if isinstance(fraction, Percent):
        raise _percent_where_a_fraction_belongs(name, fraction)

    require_not_another_quantity(name, fraction, Fraction)

    raise TypeError(
        f"{name} of {shown(fraction)} was not built as Fraction, it is "
        f"{type(fraction).__name__}: build it as Fraction(...) where it is computed, which "
        'checks it against 0 to 1 once (docs/MODEL.md, "Concentrations")'
    )


def require_percent(name: str, percent: object) -> None:
    """Require a value that was built as a `Percent`, and so checked.

    This is the run-time half of the type, as `require_fraction` is for a
    fraction. It runs wherever a percent is stored: in `BreathingCircuit` when
    it is built or set, in `UptakeEquationSettings`, and in the
    `AgentParameters` that store an agent's MAC and vaporizer maximum. Since
    `PL-1DP1` it also runs in `fraction_from_percent`, where the governing
    equations read the dial. It is the one check that rejects a fraction
    reaching the dial at run time, and not only under `mypy`.

    The error message names a `Fraction` as one, and says to convert it rather
    than rebuild it. A `Percent` built from a fraction's value would hold a
    concentration a hundred times too small. It would also be below every
    agent's vaporizer maximum, so no later check would reject it. `Percent`
    rejects the rebuild with the same message. Since `PL-CX2C`, any other
    checked quantity is named as a swapped argument, as `require_fraction`
    describes. Before then, a `FreshGasFlow(2.0)` passed in as the dial was
    told to build `Percent(...)` from it.

    Args:
        name: What the value is at the place where it is passed in, such as
            the dial or its maximum, for the message.
        percent: The value that was passed in.

    Raises:
        TypeError: `percent` is not a `Percent`, for the reason that
            `require_fraction` gives. That includes a bare `float`, whatever
            its value.
    """

    if isinstance(percent, Percent):
        return

    if isinstance(percent, Fraction):
        raise _fraction_where_a_percent_belongs(name, percent)

    require_not_another_quantity(name, percent, Percent)

    raise TypeError(
        f"{name} of {shown(percent)} was not built as Percent, it is "
        f"{type(percent).__name__}: build it as Percent(...) where it is set, which checks "
        'it against 0 to 100 once (docs/MODEL.md, "Concentrations")'
    )


def require_mac_percent(name: str, mac_percent: object) -> None:
    """Require a value that was built as a `MacPercent`, and so checked.

    This is the runtime half of the type, as `require_percent` is for a
    percent. It runs where a MAC is held, in `AgentParameters`. It also runs
    where a MAC is used as a divisor, in the formatters of
    `app/formatting.py` (`PL-F9TC`).

    Args:
        name: What the value is where it is handed in, for the message.
        mac_percent: What was handed in.

    Raises:
        TypeError: `mac_percent` is not a `MacPercent`. That includes a bare
            `float` and a `Percent`, whatever its value, because neither was
            checked as a MAC.
    """

    if isinstance(mac_percent, MacPercent):
        return

    if isinstance(mac_percent, Fraction):
        raise _fraction_where_a_percent_belongs(name, mac_percent)

    if not isinstance(mac_percent, Percent):
        require_not_another_quantity(name, mac_percent, MacPercent)

    raise TypeError(
        f"{name} of {shown(mac_percent)} was not built as MacPercent, it is "
        f"{type(mac_percent).__name__}: build it as MacPercent(...) where the agent's MAC "
        "is read, which checks once that it is above 0% and at most 100%"
    )


def fraction_from_percent(percent: Percent) -> Fraction:
    """Convert a percent of one atmosphere to the model's fraction.

    It does not check the range. The percent's range was checked when the
    percent was built. The quotient is built as a `Fraction`, which cannot
    reject it. Division rounds monotonically and 100 divided by the factor
    gives exactly 1, so a percent from 0 through 100 gives a fraction from 0
    through 1 (`PL-4R3W` measured a million of them). The argument is checked
    before the arithmetic runs, because after the division `Fraction` sees only
    the plain `float` that the division produced, and accepts it. A `Fraction`
    is rejected first, with its own advice. It is already the form that this
    function returns, so dividing it would store a concentration a hundred
    times too small, under the type that is meant to prove it was checked.
    `fraction_from_percent(Fraction(0.5))` was a `Fraction` of 0.005
    (`PL-SWD1`). Here converting is itself the error, so the remedy that
    `require_percent` gives, to convert, does not apply. Every other check is `require_percent`'s,
    made here as it is wherever a percent is stored (`PL-1DP1`). A value built
    as any other checked quantity is named as a swapped argument
    (`core/checked_number.py`, `PL-979Z`). A value never built as a `Percent`,
    such as a bare `float`, a `bool` or a `str`, is told to build one where its
    form is known. That is where it is checked as a number and against its
    range. Until `PL-1DP1`, a bare `float` was accepted as given, as the module
    docstring records. Until `PL-LLMN`, `True` divided by a hundred was a
    fraction of 0.01.

    Raises:
        TypeError: `percent` is a `Fraction`, and the message says to use it
            as the fraction it is. Also raised when `percent` is anything else
            not built as a `Percent`, which is rejected as `require_percent`
            rejects it. That includes a bare `float`, whatever its value.
    """

    if isinstance(percent, Fraction):
        raise TypeError(
            f"percent of {percent!r} is already a Fraction, not a Percent to convert: dividing "
            "it by a hundred would hold a concentration a hundred times too small, so use it as "
            "the Fraction it is (core/concentration.py)"
        )

    require_percent("percent", percent)

    return Fraction(percent / PERCENT_PER_UNIT_FRACTION)


def percent_from_fraction(fraction: Fraction) -> Percent:
    """Convert the model's fraction to a percent of one atmosphere.

    This is the display direction. The pair is not one function with a flag,
    because a reader has to be able to see which way a call converts.

    The product is built as a `Percent`. For a `Fraction` argument, that
    constructor cannot reject the product, because multiplication rounds
    monotonically and 1 gives exactly 100. The argument is checked before the arithmetic runs, in
    the order that `fraction_from_percent` uses. First, a `Percent` is
    rejected. It is already the form that this function returns, so
    multiplying it would store a concentration a hundred times too large.
    `percent_from_fraction(Percent(0.5))` was a `Percent` of 50.0, which showed
    a 0.5% dial as 50% (`PL-SWD1`). Then come `require_fraction`'s checks, as at
    every place where a fraction is stored (`PL-1DP1`). They reject a value
    built as any other checked quantity (`PL-979Z`). They also reject a value
    never built as a `Fraction`, a bare `float` included, and tell the caller
    to build one where the value is computed. Until `PL-1DP1`, a bare `float`
    was accepted as given. So `percent_from_fraction(0.5)` was a `Percent` of
    50.0 whether the 0.5 was a fraction or a 0.5% dial. Only an impossible
    value, a negative one from a caller that `mypy` does not check, was
    rejected, by the range check where the product was built (`PL-4R3W`).
    Until `PL-LLMN`, `True` times a hundred was a percent of 100, inside the
    range, and `format_percent(True)` printed `100.00%`. A number of unknown
    form is now rejected in the same way, before anything is built on it. No
    `Fraction` holds an impossible value, and a number that was never built as
    one proves nothing about what it is.

    Raises:
        TypeError: `fraction` is a `Percent`, and the message says to use it
            as the percent it is. Also raised when `fraction` is anything else
            not built as a `Fraction`, which is rejected as `require_fraction`
            rejects it. That includes a bare `float`, whatever its value.
    """

    if isinstance(fraction, Percent):
        raise TypeError(
            f"fraction of {fraction!r} is already a Percent, not a Fraction to convert: "
            "multiplying it by a hundred would hold a concentration a hundred times too large, "
            "so use it as the Percent it is (core/concentration.py)"
        )

    require_fraction("fraction", fraction)

    return Percent(fraction * PERCENT_PER_UNIT_FRACTION)
