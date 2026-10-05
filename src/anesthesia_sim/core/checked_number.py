"""What a checked type is built from, how it holds a zero, and how a refusal names a value.

`Fraction` and `Percent` (`core/concentration.py`), the three flows,
`FreshGasFlow`, `AlveolarVentilation` and `CardiacOutput`, and the case
instant, `CaseInstant` (`core/supported_ranges.py`), are each a `float`
subclass checked against its own range when it is built, so that holding one
is the proof the check ran (`.claude/rules/core-domain.md` § "A quantity with
a check of its own is a type, checked once"). Before a range can be read, the
value handed in has to be a number at all, and this module decides that once,
for all of them, together with the one thing a held zero needs.

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
`core/validation.py`, with `SimulationStep` built on one of them, are
`PL-3800`'s: each has the same holes, and is brought here as its item lands.
"""

from __future__ import annotations

import sys


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


def require_a_number(name: str, value: object) -> None:
    """Require an `int` or a `float`, before any comparison reads the value.

    Admits those two types and their subclasses, so a `numpy.float64`, an
    `IntEnum` member or a value already built as a checked type passes, and a
    `bool`, a `numpy.bool_`, a `Decimal` and a `str` do not. A `bool` is an
    `int` to Python and is refused all the same: `True` is not a setting. An
    `IntEnum` member is an `int` its caller chose to name, and is admitted as
    the `int` it is; `src/` defines no such enum.

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
