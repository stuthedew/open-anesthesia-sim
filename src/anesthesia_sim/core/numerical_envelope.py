"""The volumes and partition coefficients on which core's arithmetic has been shown correct.

Every compartment volume and every partition coefficient in `core/` is built as
one of the two types below. Each type refuses a value outside its declared
interval, the *numerical envelope*, when it is built. So a record or function
that takes one does not check it again (`.claude/rules/core-domain.md`
§ "A quantity with a check of its own is a type, checked once").

**The envelope is not a supported range.** A supported range in
`core/supported_ranges.py` states where the model is claimed to represent a
patient. The envelope states only where the arithmetic has been shown to give
the right answer. It is set far outside every shipped value, so no real
parameter set meets it. A value inside it can still describe no patient: a
10 mL lung is not a lung. `docs/MODEL.md` § "The numerical envelope" states the
two claims side by side.

**What the envelope guarantees.** The intervals are closed, and every value in
them is positive and finite. So every product and quotient of two of them is
positive and finite too, and many decades inside the range of a `float`. The
extremes of a product or a quotient of positive inputs over a box lie at the
box's corners. A volume times a coefficient lies between 1e-5 and 1e8 L, and a
volume over a coefficient between 1e-6 and 1e7 L. Before `PL-QX2G` the inputs
were bounded only as positive and finite. A tissue of 1e-300 L with a
tissue:blood coefficient of 1e-30 then raised a bare `ZeroDivisionError` in
`TissueGroupEquationSettings.washin_rate_s`. A tissue of 1e307 L with a
tissue:gas coefficient of 1e-307 had an ordinary capacity of 1 L and an infinite
time constant, so it never moved.

**What decided the bounds: the squarings that the step's propagator needs.**
`core/matrix_exponential.py` scales each interval down by repeated halving,
then squares the result back up. Each squaring can double the rounding error,
so the number of squarings sets the accuracy. The fastest rate in the system
matrix sets the number of squarings. That rate is largest when a small volume
meets a large flow, and in the alveolar balance a large blood:gas coefficient
multiplies the cardiac output. At every corner of the envelope, with every flow
at zero or at the top of its supported range, the 0.1 s step needs at most 19
squarings. That was measured on 2026-10-25 over 2,560 corners. Nineteen is the
number that the shipped parameters already need over the 24-hour horizon
(`MAXIMUM_SQUARINGS` in `core/matrix_exponential.py`). So no step inside the
envelope is computed less accurately than a propagator that a shipped run
already forms. The step is never refused either: 19 leaves a factor of 2**13
below the cap of 32. `docs/MODEL.md` § "The numerical envelope" gives the
measurement against a 70-digit evaluation and what it means for a long run.

**The tissue:blood coefficient is a partition coefficient too, and is checked
where it is formed.** It is the quotient of the tissue:gas and blood:gas
coefficients, so two coefficients inside the envelope can form one far outside
it. A tissue:gas coefficient of 1e-3 over a blood:gas coefficient of 1e4 makes a
tissue:blood coefficient of 1e-7. In a 1e-3 L tissue, the wash-in rate was then
1.6e9 per second, and the 0.1 s step needed the full 32 squarings (measured
2026-10-25). `tissue_blood_partition_coefficient` below
is the one place that forms the quotient, and it builds the result as a
`PartitionCoefficient`. Each record that holds both factors calls it when
either factor is written, because the quotient is a relation between two
fields.
"""

from __future__ import annotations

from anesthesia_sim.core.checked_number import (
    CheckedQuantity,
    require_a_number,
    require_not_another_quantity,
    shown,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError

# The smallest compartment volume, in litres, that core accepts.
#
# This floor is the bound that the measurement in the module docstring sets.
# At the alveolar volume, with a blood:gas coefficient of
# `MAXIMUM_PARTITION_COEFFICIENT` and a cardiac output of 10 L/min, the fastest
# rate is 1.67e5 per second, and the 0.1 s step needs 19 squarings. The first
# floor considered, 1e-3 L, needed 22 squarings there, so its error bound was
# eight times larger. The floor is 122 times below the smallest shipped volume,
# the reference adult's venous pool of 1.222 L. A patient profile with smaller
# volumes would bring smaller flows with it, which this measurement does not
# include. A profile within a decade of this floor would need the measurement
# taken again at its own flows.
MINIMUM_VOLUME_L = 1e-2

# The largest compartment volume, in litres, that core accepts.
#
# A large volume slows the system, and no squaring count depends on it. So this
# ceiling bounds only the products and quotients. It is about 300 times above
# the largest shipped volume, the reference adult's muscle group of 33 L.
MAXIMUM_VOLUME_L = 1e4

# The smallest partition coefficient that core accepts.
#
# It applies to a blood:gas, a tissue:gas and a tissue:blood coefficient alike.
# The smallest tissue:blood coefficient makes the fastest tissue wash-in rate.
# At this floor and a 1e-2 L tissue, the 0.1 s step needs 15 squarings, four
# fewer than the alveolar corner that sets `MINIMUM_VOLUME_L`. The floor is 420
# times below the smallest shipped coefficient, desflurane's blood:gas
# coefficient of 0.42.
MINIMUM_PARTITION_COEFFICIENT = 1e-3

# The largest partition coefficient that core accepts.
#
# A large blood:gas coefficient makes the fastest alveolar rate, which is why
# this ceiling and `MINIMUM_VOLUME_L` were chosen together. The ceiling is about
# 140 times above the largest shipped coefficient, isoflurane's fat:gas
# coefficient of 70.0.
MAXIMUM_PARTITION_COEFFICIENT = 1e4

_ENVELOPE_SECTION = '(docs/MODEL.md, "The numerical envelope")'


def _require_within_envelope(
    name: str, value: float, minimum: float, maximum: float, unit: str
) -> None:
    """Require a number inside one closed numerical envelope.

    `require_a_number` runs first, so a `bool`, a `Decimal` or a `str` is
    refused in the simulator's own words. Then a single closed-interval
    comparison refuses NaN, both infinities, zero, a negative value and a value
    outside the interval, all with one message. That is the shape of
    `_require_supported` in `core/supported_ranges.py`, whose docstring says why.

    Raises:
        TypeError: `value` is not an `int` or a `float`, or is a `bool`.
        SimulationConfigurationError: `value` is outside `minimum` to
            `maximum`, or is not finite.
    """

    require_a_number(name, value)

    if not minimum <= value <= maximum:
        raise SimulationConfigurationError(
            f"{name} of {shown(value)} is outside the numerical envelope of {minimum:g} to "
            f"{maximum:g}{unit}, the range on which core's arithmetic has been shown to "
            f"give the right answer {_ENVELOPE_SECTION}"
        )


class CompartmentVolume(float, CheckedQuantity):
    """The volume of one modelled compartment, in litres, checked against the envelope when built.

    It holds the breathing circuit's volume, the alveolar gas volume, the venous
    pool's volume and each tissue group's volume. It compares and computes as
    the `float` it was built from. A product or quotient of it is a plain
    `float`, which carries no proof of any range.

    `name` is what an error message calls the value. Several compartments each
    hold a volume, so the caller that builds one supplies the name, as
    `Fraction` takes one (`core/concentration.py`). A pickle rebuilds the value
    under the default name, as `CheckedQuantity.__reduce__` says.

    Raises:
        TypeError: the volume was built as another checked quantity, such as a
            partition coefficient or a flow. That is a swapped argument. Or the
            volume is not an `int` or a `float`, or is a `bool`
            (`core/checked_number.py`).
        SimulationConfigurationError: the volume is outside `MINIMUM_VOLUME_L`
            to `MAXIMUM_VOLUME_L`, or is not finite.
    """

    __slots__ = ()

    def __new__(cls, volume_l: float, *, name: str = "volume_l") -> CompartmentVolume:
        require_not_another_quantity(name, volume_l, cls)
        _require_within_envelope(name, volume_l, MINIMUM_VOLUME_L, MAXIMUM_VOLUME_L, " L")

        return super().__new__(cls, volume_l)


class PartitionCoefficient(float, CheckedQuantity):
    """A dimensionless partition coefficient, checked against the envelope when built.

    It holds a blood:gas, a tissue:gas or a tissue:blood coefficient. The three
    share one envelope, because each multiplies or divides a volume or a flow in
    the same way. It compares and computes as the `float` it was built from,
    and a product or quotient of it is a plain `float`. `name` works as it does
    for `CompartmentVolume`.

    Raises:
        TypeError: the coefficient was built as another checked quantity, or is
            not an `int` or a `float`, or is a `bool`, as `CompartmentVolume`
            says.
        SimulationConfigurationError: the coefficient is outside
            `MINIMUM_PARTITION_COEFFICIENT` to `MAXIMUM_PARTITION_COEFFICIENT`,
            or is not finite.
    """

    __slots__ = ()

    def __new__(
        cls, coefficient: float, *, name: str = "partition_coefficient"
    ) -> PartitionCoefficient:
        require_not_another_quantity(name, coefficient, cls)
        _require_within_envelope(
            name, coefficient, MINIMUM_PARTITION_COEFFICIENT, MAXIMUM_PARTITION_COEFFICIENT, ""
        )

        return super().__new__(cls, coefficient)


def tissue_blood_partition_coefficient(
    tissue_gas: PartitionCoefficient, blood_gas: PartitionCoefficient, *, name: str
) -> PartitionCoefficient:
    """Return $`\\lambda_{i:b} = \\lambda_{i:g}/\\lambda_{b:g}`$, built as a `PartitionCoefficient`.

    This is the one place in `core/` that forms the quotient. `TissueGroup`
    and `AgentParameters` both read it from here, so the two cannot form it
    differently. The quotient of two coefficients inside the envelope can lie
    outside it, and the module docstring says why that matters. So the result
    is built as the type, and a quotient outside the envelope is refused with
    both factors named.

    Raises:
        TypeError: either factor was not built as a `PartitionCoefficient`.
        SimulationConfigurationError: the quotient is outside the envelope.
    """

    require_coefficient(f"{name} tissue:gas factor", tissue_gas)
    require_coefficient(f"{name} blood:gas factor", blood_gas)

    quotient = tissue_gas / blood_gas

    try:
        return PartitionCoefficient(quotient, name=name)
    except SimulationConfigurationError as error:
        raise SimulationConfigurationError(
            f"{error}; it is the tissue:gas coefficient of {tissue_gas!r} divided by the "
            f"blood:gas coefficient of {blood_gas!r}"
        ) from error


def _require_built(name: str, value: object, envelope_type: type[CheckedQuantity]) -> None:
    """Refuse a value that was not built as `envelope_type`, naming what to do instead.

    This is `_require_built` in `core/supported_ranges.py`, for the two types
    here. A value built as another checked quantity is named as that quantity,
    and the caller is not told to rebuild it.
    """

    if isinstance(value, envelope_type):
        return

    require_not_another_quantity(name, value, envelope_type)

    raise TypeError(
        f"{name} of {shown(value)} was not built as {envelope_type.__name__}, it is "
        f"{type(value).__name__}: build it as {envelope_type.__name__}(...) where it is "
        f"set, which checks it against the numerical envelope once {_ENVELOPE_SECTION}"
    )


def require_compartment_volume(name: str, volume_l: object) -> None:
    """Require a volume that was built as a `CompartmentVolume`, and so checked.

    This is the run-time half of the type, for the callers that `mypy` does not
    check: a test, a notebook, or a value typed `Any`. It checks the type and
    not the range, which the constructor has already checked. It runs where a
    volume is stored: in each compartment's `__setattr__`, and in the two
    equation-settings records in `core/governing_equations.py` as they are
    built.

    Raises:
        TypeError: `volume_l` is not a `CompartmentVolume`, a bare `float`
            included, whatever its value.
    """

    _require_built(name, volume_l, CompartmentVolume)


def require_coefficient(name: str, coefficient: object) -> None:
    """Require a coefficient that was built as a `PartitionCoefficient`, and so checked.

    It is the run-time half of the type, and runs where a coefficient is
    stored, as `require_compartment_volume` says for a volume.

    Raises:
        TypeError: `coefficient` is not a `PartitionCoefficient`, a bare
            `float` included, whatever its value.
    """

    _require_built(name, coefficient, PartitionCoefficient)
