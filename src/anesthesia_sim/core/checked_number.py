"""What a checked type is built from, how it holds a zero, and how a refusal names a value.

`Fraction` and `Percent` (`core/concentration.py`), the run's step,
`SimulationStep` (`core/simulation_step.py`), the three flows,
`FreshGasFlow`, `AlveolarVentilation` and `CardiacOutput`, the case instant,
`CaseInstant`, and the completed-step count, `StepCount`
(`core/supported_ranges.py`), are each a `float` or an `int` subclass checked
against its own range when it is built, so that holding one is the proof the
check ran (`.claude/rules/core-domain.md` § "A quantity with a check of its
own is a type, checked once"). Before a range can be read, the value handed in
has to be a number at all, and not one already checked as another quantity,
and this module decides both once, for all of them, together with the one
thing a held zero needs.

**A number is an `int` or a `float`, and nothing else** (`PL-LLMN`). Until
that item each constructor read its value straight into `math.isfinite` and a
comparison, which admit more than a number and refuse the rest in Python's own
words, measured 2026-10-04 on `main` at `8f24fe78`:

- `True` was admitted, as the `int` Python makes of it: `FreshGasFlow(True)`
  was a fresh gas flow of 1.0 L/min and `Fraction(True)` a fraction of 1.0, a
  programming slip become a plausible setting, which is the silent coercion
  `CLAUDE.md`'s safety-critical standard forbids. `numpy.True_` is not a
  `bool` and was admitted the same way, which is why this admits two types
  rather than refusing one.
- A `Decimal` was admitted and compared exactly - `Decimal('2.5')` built a
  flow of 2.5 L/min - and `Decimal('sNaN')` escaped as a `ValueError` from
  `math.isfinite`. A `Decimal` is refused rather than converted, as a `str`
  is, because a caller holding one has stopped working in binary floating
  point, and converting it here would hide where.
- A `str` was refused with `math.isfinite`'s `TypeError: must be real number,
  not str`, naming neither the setting nor the range.

So `require_a_number` runs first, and refuses what is not an `int` or a
`float` with a `TypeError` naming the setting, the value and its type, as
`has type int64, not int or float` for a NumPy integer, which is not the
`int` its name suggests. A
`TypeError` because it is a programming error in the caller rather than a
refused setting, as `require_fraction` and `require_fresh_gas_flow` say of a
value never built as its type; nothing the interface does reaches it, since a
slider's value is an `int` position over a power of ten and the data-file
loaders admit only an `int` or a `float`. Subclasses of either are admitted
with them: a `numpy.float64` is a `float`, and an `IntEnum` member an `int`.
Every other NumPy scalar - `numpy.float32`, `numpy.int64` - is refused, and
its caller converts it, so that a value rounded in a narrower format never
reads as the number it was.

**One checked quantity is never built from another** (`PL-979Z`). A checked
type is a subclass of `float` or `int`, so `require_a_number` admits a value
already built as one, and until that item each constructor then checked its
number against a second range and, wherever the two ranges overlap, held the
wrong quantity under the right type, measured 2026-10-05 on `main` at
`b67dace8`: `CaseInstant(StepCount(600))` was an instant of 600 s,
`CaseInstant(FreshGasFlow(5.0))` one of 5 s, `FreshGasFlow(CaseInstant(5.0))`
a flow of 5 L/min, `SimulationStep(Fraction(0.05))` a step of 0.05 s and
`Percent(FreshGasFlow(2.0))` a dial at 2%, and `mypy --strict` passed each
call, a checked `float` being a `float`. Only `Fraction` and `Percent` refused
each other. Where one was stored, `require_case_instant` and
`require_step_count` named a value built as any of six types, reading a tuple
`core/supported_ranges.py` kept, the flows' `_require_built` named the other
two flows alone, and the step's check named none; `core/simulation_step.py`
could not import that tuple back without a cycle, and the two concentrations
were not in it. So every checked type
is now a `CheckedQuantity`, and `require_not_another_quantity` is the first
question each constructor asks of what it is handed, and each stored-value
check of what is not already its own type: a value that is a `CheckedQuantity`
but not the type in hand was built as another quantity, and is refused by
name before any comparison reads its number. The record of which types are
checked is the class hierarchy itself, read with one `isinstance` - a type is
a checked quantity because it says so where it is defined, with no list to
keep in step and no import between the three modules - so a checked type
added later refuses, and is refused, from the day it is written. The same
type is admitted, so an instant is rebuilt from an instant as before; and
`Fraction` and `Percent` keep their own refusal of each other, which says to
convert rather than to rebuild, since that pair is a missed conversion and
not a swapped argument. The stored-value checks - `require_case_instant`,
`require_step_count`, `require_simulation_step`, the flows' `require_*`, and
`require_fraction` and `require_percent` - read the same record and refuse in
the same words (`PL-848D`, `PL-CX2C`).

**Minus zero is held as zero** (`PL-LLMN`). `-0.0` equals zero and is inside
every closed interval here, so refusing it would refuse the supported zero -
the fresh gas turned off, apnoea, circulatory arrest - which arithmetic reaches
as minus zero whenever a zero is multiplied by a negative. Held as given, it
prints with its sign: `format_flow` gave `-0.0 L/min` and `format_percent`
`-0.00%`, a sign no flow and no concentration has. `negative_zero_as_zero` is
what each constructor hands `float.__new__`, so no checked type can hold a
signed zero, and the formatters need no rule of their own.

`CaseInstant` was brought here by `PL-7N8P`, after `PL-LLMN` had found the
same holes in it, and `StepCount`, built from an `int` alone, refuses what is
not one in the same form since `PL-LLMN`. The sign-and-finiteness guards in
`core/validation.py`, `require_positive_finite` and
`require_nonnegative_finite`, with `SimulationStep` built on the first, had
the same holes and were brought here by `PL-3800`. Having no supported range
to refuse an `int` past the float range against, they refuse it by name as
outside the range a `float` holds, where `math.isfinite` raised
`OverflowError` converting it (`core/validation.py`). Neither guard builds a
type, so neither asks whether its value was built as another quantity: a
checked flow handed in as a circuit volume is a swapped argument no range can
tell from a number, and is outside what this module decides.
"""

from __future__ import annotations

import sys


class CheckedQuantity:
    """A quantity built only through its own check, so that holding one is the proof the check ran.

    The base of every checked type, and nothing more: it adds no slot, no
    `__new__` and no arithmetic, so `FreshGasFlow` is the `float` it was and
    `StepCount` the `int`, with this class after the number in each one's
    bases. After, not before: `mypy` takes the nearest common base of two
    checked types as the type of a container or a branch holding both, and
    with this class first that base was this class rather than `float`, which
    refused a `float` variable assigned a flow read from a dictionary of the
    three (`app/dashboard_frame.py`'s `value`, measured building `PL-979Z`).
    What it records is which types are checked, at the type's own definition,
    so that `require_not_another_quantity` tells a value built as another
    checked quantity from one nobody built with one `isinstance` and no list
    of types kept anywhere else (`PL-979Z`).
    """

    __slots__ = ()


def shown(value: object) -> str:
    """A value as a refusal names it: its `repr`, or an `int` too long to print by how long it is.

    `repr` keeps a string's quotes, so `'2.5'` reads as the string it was.
    `repr` of an `int` of more than `sys.get_int_max_str_digits()` digits
    (4,300 unless set otherwise) raises `ValueError`, so a refusal that printed
    one escaped the simulator's own exceptions while its message was being
    built - the count's escape `PL-5F76` closed, and the flows' and the
    concentrations' `PL-LLMN` closes the same way.
    """

    if isinstance(value, int) and not isinstance(value, bool):
        try:
            return str(value)
        except ValueError:
            sign = "-" if value < 0 else ""

            return f"{sign}<more than {sys.get_int_max_str_digits():,} digits>"

    return repr(value)


def require_not_another_quantity(name: str, value: object, building: type[CheckedQuantity]) -> None:
    """Refuse a value built as a checked quantity other than `building`, before its number is read.

    The first question a checked type's constructor asks of what it is handed,
    and the first a stored-value check asks of what is not already its type:
    a value that is a `CheckedQuantity` but not `building` was checked as
    another quantity, and building `building` from it would check its number
    against a second range and, wherever the two overlap, hold the wrong
    quantity under the right type - a count of 600 steps as an instant of
    600 s. A value of `building` itself passes, so a type is rebuilt from its
    own kind; a value built as no checked type passes too, to whatever reads
    its number next, `require_a_number` or the stored-value refusal.

    The refusal names the parameter, the value, the type it was built as and
    the type in hand, and prescribes no rebuild from the value, since that
    rebuild is the error being refused: what it asks for is the value the
    parameter should hold, and it says in as many words not to build from
    this one.

    Args:
        name: What the value is where it is handed in, for the message, as
            `require_a_number` takes it.
        value: What was handed in.
        building: The checked type being built, or required where a value
            of it is stored.

    Raises:
        TypeError: `value` was built as a checked quantity other than
            `building`. A programming error in the caller rather than a
            refused setting, so not an `AnesthesiaSimulationError`
            (`core/exceptions.py`).
    """

    if isinstance(value, CheckedQuantity) and not isinstance(value, building):
        raise TypeError(
            f"{name} of {shown(value)} was built as {type(value).__name__}, which is not "
            f"{building.__name__}: it is another quantity, so build {building.__name__} from "
            f"the value that {name} should hold, not from this one (core/checked_number.py)"
        )


def require_a_number(name: str, value: object) -> None:
    """Require an `int` or a `float`, before any comparison reads the value.

    Admits those two types and their subclasses, so a `numpy.float64`, an
    `IntEnum` member or a value already built as a checked type passes, and a
    `bool`, a `numpy.bool_`, a `Decimal` and a `str` do not. Whether a checked
    value is the type in hand or another quantity is
    `require_not_another_quantity`'s question, which each constructor asks
    before this one. A `bool` is an `int` to Python and is refused all the
    same: `True` is not a setting. An `IntEnum` member is an `int` its caller
    chose to name, and is admitted as the `int` it is; `src/` defines no such
    enum.

    Args:
        name: What the value is where it is handed in, for the message - the
            parameter's name, prefixed with its owner where several objects
            can raise it, as `core/validation.py` says of `name`.
        value: What was handed in.

    Raises:
        TypeError: `value` is not an `int` or a `float`, or is a `bool`. A
            programming error in the caller rather than a refused setting, so
            not an `AnesthesiaSimulationError` (`core/exceptions.py`).
    """

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} of {value!r} has type {type(value).__name__}, not int or float: "
            "build it from an int or a float, which is then checked against its range "
            "(core/checked_number.py)"
        )


def negative_zero_as_zero(value: float) -> float:
    """The number a checked type holds for `value`: the same number, with minus zero as zero.

    `-0.0 == 0.0`, so a comparison cannot tell them apart and a range check
    admits both; `float.__new__` would keep the sign and a formatter would
    print it. A zero of either sign, the `int` zero included, is returned as
    `0.0`; every other value is returned as it was given, bit for bit, since
    the type's promise is to hold what it was built from.
    """

    return 0.0 if value == 0 else value
