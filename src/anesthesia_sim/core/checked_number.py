"""Check what a checked type is built from, store minus zero as zero, and show values in errors.

Several types in this package are a `float` or an `int` subclass that checks its
value against its own range when it is built. They are `Fraction` and
`Percent` (`core/concentration.py`), the run's step, `SimulationStep`
(`core/simulation_step.py`), the three flows, `FreshGasFlow`,
`AlveolarVentilation` and `CardiacOutput`, the case instant, `CaseInstant`,
and the completed-step count, `StepCount` (`core/supported_ranges.py`). The
compartment volumes and partition coefficients are `CompartmentVolume` and
`PartitionCoefficient` (`core/numerical_envelope.py`). So
having a value of one of these types proves that its check ran
(`.claude/rules/core-domain.md` § "A quantity with a check of its own is a
type, checked once"). Before the range can be checked, two other questions
need an answer. The value must be a number at all, and it must not already be
checked as another quantity. This module answers both questions once, for all
of these types. It also does the one thing that a stored zero needs.

**A number is an `int` or a `float`, and nothing else** (`PL-LLMN`). Before
that item, each constructor passed its value straight to `math.isfinite` and a
comparison. Those accept more than numbers, and they reject everything else in
Python's own words. This was measured on 2026-10-04 on `main` at `8f24fe78`:

- `True` was accepted, as the `int` that Python makes of it.
  `FreshGasFlow(True)` was a fresh gas flow of 1.0 L/min, and `Fraction(True)`
  was a fraction of 1.0. A programming slip became a plausible setting. That
  is the silent coercion that `CLAUDE.md`'s safety-critical standard forbids.
  `numpy.True_` is not a `bool`, and it was accepted the same way. That is why
  this module accepts two types rather than rejecting one.
- A `Decimal` was accepted and compared exactly: `Decimal('2.5')` built a flow
  of 2.5 L/min. `Decimal('sNaN')` escaped as a `ValueError` from
  `math.isfinite`. A `Decimal` is now rejected rather than converted, as a
  `str` is. A caller holding a `Decimal` has stopped working in binary
  floating point, and converting it here would hide where that happened.
- A `str` was rejected with `math.isfinite`'s `TypeError: must be real number,
  not str`. That message named neither the setting nor the range.

So `require_a_number` runs first. It rejects anything that is not an `int` or
a `float` with a `TypeError` that names the setting, the value and its type.
For a NumPy integer the message says `has type int64, not int or float`,
because a NumPy integer is not the `int` its name suggests. The error is a
`TypeError` because it is a programming error in the caller, not a rejected
setting. `require_fraction` and `require_fresh_gas_flow` give the same reason
for their `TypeError` on a value that was never built as their type. Nothing the interface does can
trigger this error. A slider's value is an `int` position over a power of ten,
and the data-file loaders accept only an `int` or a `float`. Subclasses of
`int` and `float` are accepted too: a `numpy.float64` is a `float`, and an
`IntEnum` member is an `int`. Every other NumPy scalar, such as
`numpy.float32` or `numpy.int64`, is rejected, and its caller must convert
it. That way a value rounded in a narrower format is never mistaken for the
number it was before rounding.

**One checked quantity is never built from another** (`PL-979Z`). A checked
type is a subclass of `float` or `int`, so `require_a_number` accepts a value
already built as one. Before that item, each constructor then checked that
number against its own, second range. Wherever the two ranges overlap, it
stored the wrong quantity under the right type. This was measured on
2026-10-05 on `main` at `b67dace8`. `CaseInstant(StepCount(600))` was an
instant of 600 s, and `CaseInstant(FreshGasFlow(5.0))` was one of 5 s.
`FreshGasFlow(CaseInstant(5.0))` was a flow of 5 L/min,
`SimulationStep(Fraction(0.05))` was a step of 0.05 s, and
`Percent(FreshGasFlow(2.0))` was a dial at 2%. `mypy --strict` passed each
call, because a checked `float` is a `float`. Only `Fraction` and `Percent`
rejected each other. The checks on a stored value were uneven.
`require_case_instant` and `require_step_count` named a value built as any of
six types, read from a tuple kept in `core/supported_ranges.py`. The flows'
`_require_built` named only the other two flows, and the step's check named
none. `core/simulation_step.py` could not import that tuple without an import
cycle, and the two concentrations were not in it.

So every checked type is now a `CheckedQuantity`.
`require_not_another_quantity` is the first check that each constructor makes
on its argument. Each stored-value check also makes it first, on a value that
is not already its own type. A value that is a `CheckedQuantity` but not the
type being built was built as another quantity. It is rejected by name before
any comparison uses its number. The record of which types are checked is the
class hierarchy itself, read with one `isinstance`. A type is a checked
quantity because its own definition says so. There is no list to keep in step,
and no import between the three modules. So a checked type added later rejects
values built as other checked types, and they reject values built as it, from
the day it is written. A value
of the same type is accepted, so an instant can be rebuilt from an instant as
before. `Fraction` and `Percent` keep their own rejection of each other. Their
message says to convert rather than to rebuild, because mixing up that pair is
a missed conversion and not a swapped argument. The stored-value checks are
`require_case_instant`, `require_step_count`, `require_simulation_step`, the
flows' `require_*`, and `require_fraction` and `require_percent`. They read
the same record and reject in the same words (`PL-848D`, `PL-CX2C`).

**Minus zero is stored as zero** (`PL-LLMN`). `-0.0` equals zero and lies
inside every closed interval here. Rejecting it would therefore reject the
supported zero: the fresh gas turned off, apnoea, or circulatory arrest.
Arithmetic produces minus zero whenever a zero is multiplied by a negative
number. Stored as given, minus zero prints with its sign: `format_flow` gave
`-0.0 L/min` and `format_percent` gave `-0.00%`, a minus sign that no flow
and no concentration has. Each constructor hands `float.__new__` the result of
`negative_zero_as_zero`. So no checked type can store a signed zero, and the
formatters need no rule of their own.

`PL-7N8P` brought `CaseInstant` here, after `PL-LLMN` had found the same gaps
in it. `StepCount` is built from an `int` alone, and since `PL-LLMN` it
rejects anything that is not an `int`, with an error of the same form. The sign and
finiteness guards in `core/validation.py`, `require_positive_finite` and
`require_nonnegative_finite`, had the same gaps, and `SimulationStep` is built
on the first of them. `PL-3800` brought both guards here. They have no
supported range against which to reject an `int` too large for a `float`. So
they reject it by name, as outside the range a `float` can represent. Before,
`math.isfinite` raised `OverflowError` while converting it
(`core/validation.py`). Neither guard builds a type, so neither asks whether
its value was built as another quantity. A checked flow passed in as a circuit
volume is a swapped argument that no range can tell from a plain number.
Catching it is outside what this module decides.
"""

from __future__ import annotations

import sys


class CheckedQuantity:
    """A quantity that can only be built through its own check, so having one proves the check ran.

    This class is the base of every checked type, and it does nothing more. It
    adds no slot, no `__new__` and no arithmetic. So `FreshGasFlow` is still the
    `float` it was, and `StepCount` is still the `int`. In each type's bases,
    this class comes after the number type, not before it. The reason is how
    `mypy` types a container or a branch that holds two checked types: it uses
    their nearest common base. With this class first, that base was this class
    rather than `float`. `mypy` then rejected assigning a flow, read from a
    dictionary of the three flows, to a `float` variable
    (`app/dashboard_frame.py`'s `value`, measured while building `PL-979Z`).
    The class records which types are checked, in each type's own definition.
    So `require_not_another_quantity` can tell a value built as another checked
    quantity from a value that was never built as one, with one `isinstance`.
    No list of types is kept anywhere else (`PL-979Z`).
    """

    __slots__ = ()

    def __reduce__(self) -> tuple[type[CheckedQuantity], tuple[float | int]]:
        """Rebuild the value through its own type's constructor, at every pickle protocol.

        At protocols 0 and 1, a `float` or `int` subclass is pickled through
        `copyreg._reduce_ex`. Without this method, loading it calls `float.__new__` or
        `int.__new__` directly, so the type's own `__new__`, which runs the range check,
        never runs. A hand-edited protocol-0 pickle loaded a `Fraction` of 1.5 and a
        `StepCount` of -5 (`PL-5D1Z`, measured 2026-10-05). Protocol 2 and later,
        `copy.copy` and `copy.deepcopy` already called the type itself. This method
        makes every protocol call it, so a value edited outside its range is refused on
        load with the constructor's own exception. A `Fraction` or `Percent` is rebuilt
        under its type's default `name`, because neither stores the name it was built
        with.
        """

        number: float | int = int(self) if isinstance(self, int) else float(self)  # type: ignore[arg-type]

        return (type(self), (number,))


def shown(value: object) -> str:
    """Return a value as an error message shows it: its `repr`, or, for a huge `int`, its length.

    `repr` keeps a string's quotes, so `'2.5'` is shown as the string it was.
    For an `int` of more than `sys.get_int_max_str_digits()` digits (4,300
    unless set otherwise), `repr` raises `ValueError`. So an error message that
    printed such an `int` used to escape the simulator's own exceptions while
    the message was being built. `PL-5F76` closed that escape for the step
    count, and `PL-LLMN` closes it the same way for the flows and the
    concentrations.
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

    Each checked type's constructor makes this check first on its argument.
    Each stored-value check makes it first on a value that is not already its
    type. A value that is a `CheckedQuantity` but not `building` was checked as
    another quantity. Building `building` from it would check its number
    against a second range. Wherever the two ranges overlap, the result would
    be the wrong quantity under the right type, such as a count of 600 steps
    taken as an instant of 600 s. A value of `building` itself passes, so a
    type can be rebuilt from a value of its own kind. A value built as no
    checked type also passes, on to whatever checks its number next:
    `require_a_number` or the stored-value check.

    The error message names the parameter, the value, the type the value was
    built as and the type being built. It does not suggest rebuilding from the
    value, because that rebuild is the error being rejected. Instead it asks
    for the value the parameter should hold, and it says explicitly not to
    build from this one.

    Args:
        name: What the value is called where it is passed in, for the error
            message, in the same form that `require_a_number` takes.
        value: What was handed in.
        building: The checked type being built, or required where a value
            of it is stored.

    Raises:
        TypeError: `value` was built as a checked quantity other than
            `building`. This is a programming error in the caller rather than
            a rejected setting, so it is not an `AnesthesiaSimulationError`
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

    This accepts those two types and their subclasses. So a `numpy.float64`,
    an `IntEnum` member or a value already built as a checked type passes, and
    a `bool`, a `numpy.bool_`, a `Decimal` and a `str` do not. Whether a
    checked value is the type being built or another quantity is decided by
    `require_not_another_quantity`, which each constructor calls before this
    one. Python treats a `bool` as an `int`, but a `bool` is rejected anyway,
    because `True` is not a setting. An `IntEnum` member is an `int` that its
    caller chose to name, so it is accepted as that `int`. `src/` defines no
    such enum.

    Args:
        name: What the value is called where it is passed in, for the error
            message. This is the parameter's name, prefixed with its owner
            where several objects can raise the error, as
            `core/validation.py` says of `name`.
        value: What was handed in.

    Raises:
        TypeError: `value` is not an `int` or a `float`, or is a `bool`. This
            is a programming error in the caller rather than a rejected
            setting, so it is not an `AnesthesiaSimulationError`
            (`core/exceptions.py`).
    """

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} of {value!r} has type {type(value).__name__}, not int or float: "
            "build it from an int or a float, which is then checked against its range "
            "(core/checked_number.py)"
        )


def negative_zero_as_zero(value: float) -> float:
    """Return the number a checked type stores for `value`, with minus zero turned into zero.

    `-0.0 == 0.0`, so a comparison cannot tell the two apart, and a range check
    accepts both. `float.__new__` would keep the sign, and a formatter would
    print it. A zero of either sign, including the `int` zero, is returned as
    `0.0`. Every other value is returned exactly as it was given, bit for bit,
    because the type promises to store what it was built from.
    """

    return 0.0 if value == 0 else value
