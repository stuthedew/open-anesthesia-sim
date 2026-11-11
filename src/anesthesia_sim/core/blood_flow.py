"""A tissue group's blood flow, and the perfusion fraction it is built from.

A tissue group receives a fixed fraction of the cardiac output, its perfusion
fraction $`f_i`$. Its blood flow is that fraction of the cardiac output,
$`Q_i = f_iQ`$ (`docs/MODEL.md` § "Tissue groups"). This module gives each of
the two a checked type, as `core/supported_ranges.py` gives the cardiac output
one (`.claude/rules/core-domain.md` § "A quantity with a check of its own is a
type, checked once").

`PerfusionFraction` is checked against its own range when it is built.
`BloodFlow` has no number to check. It is built only by multiplying a
`CardiacOutput` by a `PerfusionFraction`, so it lies between zero and that
cardiac output, and nothing else produces one.

Until these types existed, a blood flow was a bare `float`. Three places each
checked by hand that it was finite and not negative: a tissue group's time
constant, the venous pool's time constant and a tissue group's equation
settings. Each accepted a flow of 5e-324 L/min and a flow of 1.8e308 L/min,
which no cardiac output inside its supported range can give (`PL-GKG4`).
"""

from __future__ import annotations

from anesthesia_sim.core.checked_number import (
    CheckedQuantity,
    require_a_number,
    require_not_another_quantity,
    shown,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import CardiacOutput, require_cardiac_output

# A perfusion fraction is above zero and at most this value. At 1, one group
# receives the whole cardiac output.
MAXIMUM_PERFUSION_FRACTION = 1.0


class PerfusionFraction(float, CheckedQuantity):
    """The fraction of the cardiac output that reaches one tissue group, $`f_i`$.

    It is above 0 and at most 1, and it is checked against that range when it
    is built. It compares and computes as the `float` it was built from, and a
    product of it is a plain `float`. Whether three fractions sum to 1 is a
    relation between them, so the patient that holds the three checks it
    (`PatientCompartments`).

    `name` is what an error message calls the value. Three tissue groups each
    hold a fraction, so the caller that builds one supplies the name, as
    `CompartmentVolume` explains (`core/numerical_envelope.py`).

    Raises:
        TypeError: the fraction was built as another checked quantity, such as
            a partial-pressure `Fraction` or a flow. That is a swapped
            argument. Also raised when the fraction is not an `int` or a
            `float`, or is a `bool` (`core/checked_number.py`).
        SimulationConfigurationError: the fraction is zero or negative, above
            1, or not finite.
    """

    __slots__ = ()

    def __new__(
        cls, perfusion_fraction: float, *, name: str = "perfusion_fraction"
    ) -> PerfusionFraction:
        require_not_another_quantity(name, perfusion_fraction, cls)
        require_a_number(name, perfusion_fraction)

        if not 0.0 < perfusion_fraction <= MAXIMUM_PERFUSION_FRACTION:
            raise SimulationConfigurationError(
                f"{name} of {shown(perfusion_fraction)} is not above 0 and at most "
                f"{MAXIMUM_PERFUSION_FRACTION:g}, the range of the fraction of the cardiac "
                'output that reaches a tissue group (docs/MODEL.md, "Tissue groups")'
            )

        return super().__new__(cls, perfusion_fraction)


class BloodFlow(float, CheckedQuantity):
    """A tissue group's blood flow $`Q_i = f_iQ`$ in L/min, built only from $`Q`$ and $`f_i`$.

    The flow is the product of a cardiac output and a perfusion fraction, and
    this constructor is the only place that forms it. Both factors are checked
    types, so the flow lies between zero and the cardiac output it was built
    from, and no supported-range guard checks it again. It compares and
    computes as a `float`, and a product or quotient of it is a plain `float`.

    The flow can be far smaller than any flow a patient has. A perfusion
    fraction of 5e-324 gives a flow of 5e-324 L/min at a cardiac output of
    1 L/min. That flow is accepted, because zero flow is supported and the
    model is continuous down to it. A time constant computed from such a flow
    is `inf`, as it is at zero flow (`TissueGroup.time_constant_s`).

    The flow does not store its two factors. So a pickle or a copy rebuilds it
    as the whole of a cardiac output equal to the flow. That gives the same
    number and runs both checks. A saved flow that was edited to lie outside
    the cardiac output's range is refused on load.

    Raises:
        TypeError: `cardiac_output_l_min` was not built as a `CardiacOutput`,
            or `perfusion_fraction` was not built as a `PerfusionFraction`. A
            bare `float` is refused for either, whatever its value.
    """

    __slots__ = ()

    def __new__(
        cls, cardiac_output_l_min: CardiacOutput, perfusion_fraction: PerfusionFraction
    ) -> BloodFlow:
        require_cardiac_output(cardiac_output_l_min)
        require_perfusion_fraction("perfusion_fraction", perfusion_fraction)

        return super().__new__(cls, cardiac_output_l_min * perfusion_fraction)

    def __reduce__(self) -> tuple[type[BloodFlow], tuple[CardiacOutput, PerfusionFraction]]:
        """Rebuild the flow through its constructor, as the whole of an equal cardiac output."""

        return (
            type(self),
            (CardiacOutput(float(self)), PerfusionFraction(MAXIMUM_PERFUSION_FRACTION)),
        )


def _require_built(
    name: str, value: object, built_type: type[CheckedQuantity], built_from: str
) -> None:
    """Refuse a value that was not built as `built_type`, and say how to build it.

    A value built as another checked quantity is a swapped argument. It is
    named as that quantity first, and the message does not say to rebuild it
    (`require_not_another_quantity`, `core/checked_number.py`).
    """

    if isinstance(value, built_type):
        return

    require_not_another_quantity(name, value, built_type)

    raise TypeError(
        f"{name} of {shown(value)} was not built as {built_type.__name__}, it is "
        f"{type(value).__name__}: build it as {built_type.__name__}({built_from}), which "
        'checks it once (docs/MODEL.md, "Tissue groups")'
    )


def require_perfusion_fraction(name: str, perfusion_fraction: object) -> None:
    """Require a perfusion fraction that was built as a `PerfusionFraction`, and so checked.

    `mypy` checks the type before the code runs. This function checks it at
    run time, for the callers that `mypy` does not check: a test, a notebook,
    or a value typed `Any`. It checks the type and not the range, which the
    constructor has already checked. It runs where a fraction is stored, in
    `TissueGroup` and `ReferenceAdultParameters`, and where a `BloodFlow` is
    built from one.

    Raises:
        TypeError: `perfusion_fraction` is not a `PerfusionFraction`. A bare
            `float` is refused too, whatever its value.
    """

    _require_built(name, perfusion_fraction, PerfusionFraction, "...")


def require_blood_flow(name: str, blood_flow_l_min: object) -> None:
    """Require a blood flow that was built as a `BloodFlow`, from a cardiac output and a fraction.

    It is the run-time check of the type, as `require_perfusion_fraction`
    explains. It runs where a tissue group's flow is stored, in
    `TissueGroupEquationSettings`, and where a tissue group's own closed form
    takes one.

    Raises:
        TypeError: `blood_flow_l_min` is not a `BloodFlow`. A bare `float` and
            a `CardiacOutput` are both refused, whatever their value.
    """

    _require_built(name, blood_flow_l_min, BloodFlow, "cardiac_output_l_min, perfusion_fraction")
