"""A blood flow reaches a tissue group, the venous pool and the equations only as a checked type.

A tissue group's blood flow is its perfusion fraction of the cardiac output,
$`Q_i = f_iQ`$ (`docs/MODEL.md` § "Tissue groups"). Three places in `core/`
took that flow as a bare `float` and checked by hand only that it was finite
and not negative (`PL-GKG4`). The first tests here replay that report. They
pass each place a bare number and expect a refusal. Two of the numbers are
ones that no cardiac output and perfusion fraction could give. The later tests
check the two types that replaced the hand checks, `PerfusionFraction` and
`BloodFlow` (`core/blood_flow.py`).
"""

import copy
import pickle
import sys
from math import inf, nan, nextafter

import pytest

from anesthesia_sim.core.blood_flow import BloodFlow, PerfusionFraction
from anesthesia_sim.core.concentration import Fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import TissueGroupEquationSettings
from anesthesia_sim.core.numerical_envelope import CompartmentVolume, PartitionCoefficient
from anesthesia_sim.core.supported_ranges import CardiacOutput, FreshGasFlow
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

# The numbers that the report named, and one ordinary flow. The smallest positive
# `float` and the largest were both accepted. A flow of 3.75 L/min is the reference
# adult's vessel-rich flow at 5 L/min, and it is refused too when it arrives as a
# bare number, because nothing then shows that a cardiac output inside its range
# produced it.
BARE_FLOWS_L_MIN = (5e-324, 3.75, sys.float_info.max)


@pytest.mark.parametrize("blood_flow_l_min", BARE_FLOWS_L_MIN)
def test_a_tissue_group_s_time_constant_refuses_a_blood_flow_given_as_a_bare_number(
    blood_flow_l_min: float,
) -> None:
    """`PL-GKG4`'s first place: `TissueGroup.time_constant_s` checked the flow by hand."""

    patient = AgentUptakeSystem.for_agent("sevoflurane").patient

    with pytest.raises(TypeError, match="BloodFlow"):
        patient.muscle.time_constant_s(
            blood_flow_l_min,  # type: ignore[arg-type]
            patient.blood_gas_partition_coefficient,
        )


@pytest.mark.parametrize("blood_flow_l_min", BARE_FLOWS_L_MIN)
def test_the_venous_pool_s_time_constant_refuses_a_flow_given_as_a_bare_number(
    blood_flow_l_min: float,
) -> None:
    """`PL-GKG4`'s second place: `VenousBloodCompartment.time_constant_s` did the same."""

    venous_blood = AgentUptakeSystem.for_agent("sevoflurane").patient.venous_blood

    with pytest.raises(TypeError, match="CardiacOutput"):
        venous_blood.time_constant_s(blood_flow_l_min)  # type: ignore[arg-type]


@pytest.mark.parametrize("blood_flow_l_min", BARE_FLOWS_L_MIN)
def test_a_tissue_group_s_equation_settings_refuse_a_blood_flow_given_as_a_bare_number(
    blood_flow_l_min: float,
) -> None:
    """`PL-GKG4`'s third place: `TissueGroupEquationSettings` stored the flow it was given."""

    with pytest.raises(TypeError, match="BloodFlow"):
        TissueGroupEquationSettings(
            name="muscle",
            volume_l=CompartmentVolume(33.0),
            blood_flow_l_min=blood_flow_l_min,  # type: ignore[arg-type]
            tissue_blood_partition_coefficient=PartitionCoefficient(2.0),
        )


def _muscle() -> TissueGroup:
    """A 2 L group with a tissue:gas coefficient of 2, so its capacity is 4 L."""

    return TissueGroup(
        name="muscle",
        volume_l=CompartmentVolume(2.0),
        perfusion_fraction=PerfusionFraction(0.2),
        tissue_gas_partition_coefficient=PartitionCoefficient(2.0),
    )


@pytest.mark.parametrize("accepted", [5e-324, 0.06, 0.76, nextafter(1.0, 0.0), 1.0, 1])
def test_a_perfusion_fraction_above_zero_and_at_most_one_is_built_as_its_number(
    accepted: float,
) -> None:
    """The range is above 0 and at most 1 (`docs/MODEL.md` § "Tissue groups").

    Both ends are written out here. The smallest positive `float` is the
    first value above 0, and 1 is a group that receives the whole cardiac
    output. An `int` 1 is stored as the `float` it equals.
    """

    built = PerfusionFraction(accepted)

    assert type(built) is PerfusionFraction
    assert built == accepted
    assert type(built * 2.0) is float


@pytest.mark.parametrize(
    "refused", [0.0, -0.0, -5e-324, -0.2, nextafter(1.0, 2.0), 1.1, inf, -inf, nan, 10**400]
)
def test_a_perfusion_fraction_outside_its_range_is_refused_by_name_and_value(
    refused: float,
) -> None:
    """Zero, a negative value, a value above 1 and a value that is not finite are each refused.

    Zero is refused because a group with no share of the cardiac output is
    not one of the model's three groups. The first `float` on either side of
    the range is refused, so the limits are 0 and 1 and no nearby number. The
    message names the group's field, the value and where the range is stated.
    """

    with pytest.raises(SimulationConfigurationError) as raised:
        PerfusionFraction(refused, name="muscle perfusion_fraction")

    assert str(raised.value) == (
        f"muscle perfusion_fraction of {refused!r} is not above 0 and at most 1, the range of "
        "the fraction of the cardiac output that reaches a tissue group "
        '(docs/MODEL.md, "Tissue groups")'
    )


@pytest.mark.parametrize(
    ("not_a_number", "named"), [(True, "bool"), ("0.2", "str"), (None, "NoneType")]
)
def test_a_perfusion_fraction_is_built_only_from_an_int_or_a_float(
    not_a_number: object, named: str
) -> None:
    """A `bool` or a `str` is a programming error, refused before the range is read."""

    with pytest.raises(
        TypeError, match=f"^perfusion_fraction of .* has type {named}, not int or float"
    ):
        PerfusionFraction(not_a_number)  # type: ignore[arg-type]


def test_a_partial_pressure_fraction_is_not_a_perfusion_fraction() -> None:
    """Both lie between 0 and 1, so only the type tells a swapped argument from a fraction."""

    with pytest.raises(
        TypeError,
        match="^perfusion_fraction of 0.2 was built as Fraction, which is not PerfusionFraction",
    ):
        PerfusionFraction(Fraction(0.2))

    with pytest.raises(
        TypeError, match="^fraction of 0.2 was built as PerfusionFraction, which is not Fraction"
    ):
        Fraction(PerfusionFraction(0.2))


def test_a_blood_flow_is_the_perfusion_fraction_of_the_cardiac_output() -> None:
    """$`Q_i = f_iQ`$: a quarter of 8 L/min is 2 L/min, and the product is a `BloodFlow`.

    The expected values are worked by hand. Each factor is exact in binary,
    so each product is exact. Arithmetic on the flow gives a plain `float`,
    which carries no proof.
    """

    flow = BloodFlow(CardiacOutput(8.0), PerfusionFraction(0.25))

    assert type(flow) is BloodFlow
    assert flow == 2.0
    assert type(flow / 60.0) is float
    assert BloodFlow(CardiacOutput(5.0), PerfusionFraction(0.5)) == 2.5


def test_a_blood_flow_lies_between_zero_and_the_largest_cardiac_output() -> None:
    """The flow's limits follow from its two factors, so no guard states them again.

    The limits are written out here: zero at circulatory arrest, and
    10 L/min, the largest supported cardiac output, when one group receives
    all of it. The smallest fraction of 1 L/min is the smallest positive
    `float`, which is also a flow.
    """

    assert BloodFlow(CardiacOutput(0.0), PerfusionFraction(1.0)) == 0.0
    assert BloodFlow(CardiacOutput(10.0), PerfusionFraction(1.0)) == 10.0
    assert BloodFlow(CardiacOutput(1.0), PerfusionFraction(5e-324)) == 5e-324


@pytest.mark.parametrize(
    ("cardiac_output_l_min", "perfusion_fraction", "refused"),
    [
        (
            5.0,
            PerfusionFraction(0.2),
            "^cardiac_output_l_min of 5.0 was not built as CardiacOutput",
        ),
        (CardiacOutput(5.0), 0.2, "^perfusion_fraction of 0.2 was not built as PerfusionFraction"),
        (
            PerfusionFraction(0.2),
            CardiacOutput(5.0),
            "^cardiac_output_l_min of 0.2 was built as PerfusionFraction, which is not "
            "CardiacOutput",
        ),
        (
            FreshGasFlow(5.0),
            PerfusionFraction(0.2),
            "^cardiac_output_l_min of 5.0 was built as FreshGasFlow, which is not CardiacOutput",
        ),
        (
            CardiacOutput(5.0),
            Fraction(0.2),
            "^perfusion_fraction of 0.2 was built as Fraction, which is not PerfusionFraction",
        ),
    ],
    ids=[
        "bare-cardiac-output",
        "bare-fraction",
        "swapped",
        "fresh-gas-flow-as-cardiac-output",
        "partial-pressure-fraction",
    ],
)
def test_a_blood_flow_is_built_from_a_cardiac_output_and_a_perfusion_fraction_and_nothing_else(
    cardiac_output_l_min: object, perfusion_fraction: object, refused: str
) -> None:
    """A bare number, a swapped pair and another checked quantity are each refused (`PL-GKG4`).

    No call builds a `BloodFlow` from one number, so no flow exists that a
    supported cardiac output did not produce.
    """

    with pytest.raises(TypeError, match=refused):
        BloodFlow(cardiac_output_l_min, perfusion_fraction)  # type: ignore[arg-type]

    with pytest.raises(TypeError):
        BloodFlow(2.0)  # type: ignore[call-arg, arg-type]


def test_a_cardiac_output_is_not_a_tissue_group_s_blood_flow() -> None:
    """A tissue group refuses the whole cardiac output where its own flow belongs."""

    with pytest.raises(
        TypeError,
        match="^muscle blood_flow_l_min of 5.0 was built as CardiacOutput, which is not BloodFlow",
    ):
        _muscle().time_constant_s(
            CardiacOutput(5.0),  # type: ignore[arg-type]
            PartitionCoefficient(0.5),
        )


@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
def test_a_blood_flow_survives_a_pickle_and_a_copy_as_the_same_flow(protocol: int) -> None:
    """A restored flow is a `BloodFlow` holding the number it was saved with, bit for bit.

    The flow is rebuilt through its constructor, as the whole of a cardiac
    output equal to it. 5 L/min times 0.06 is not exact in binary, so a
    restore that formed the product a second way would show here.
    """

    flow = BloodFlow(CardiacOutput(5.0), PerfusionFraction(0.06))

    for restored in (
        pickle.loads(pickle.dumps(flow, protocol=protocol)),
        copy.copy(flow),
        copy.deepcopy(flow),
    ):
        assert type(restored) is BloodFlow
        assert restored.hex() == flow.hex()


def test_a_flow_too_small_for_a_finite_time_constant_leaves_a_tissue_unchanged() -> None:
    """A flow of 5e-324 L/min is accepted, and the tissue it perfuses does not change.

    `PL-GKG4` reported that this flow was accepted as a bare number. It is
    still a flow that can be built, as the smallest perfusion fraction of
    1 L/min, because zero flow is supported and the model is continuous down
    to it. The time constant, 60 x 2 L x 4 / 5e-324 L/min, is about 1e326 s,
    which is larger than any `float`, so it is `inf` as at zero flow. Stepped
    alone for 24 hours towards a fraction of 1, the 4 L tissue takes up
    4 L x 86 400 s / 1e326 s, about 4e-321 L. That is worked out here from the
    flow and not from the time constant. The code leaves the tissue unchanged,
    which is wrong by less than the 5e-296 L that `time_constant_s` states.
    """

    tissue = _muscle()
    blood_gas = PartitionCoefficient(0.5)
    flow = BloodFlow(CardiacOutput(1.0), PerfusionFraction(5e-324))
    exact_change_l = 4.0 * (86_400.0 * 5e-324 / (60.0 * 2.0 * 4.0))

    assert tissue.time_constant_s(flow, blood_gas) == inf
    assert tissue.advance(Fraction(1.0), 86_400.0, flow, blood_gas) == 0.0
    assert tissue.agent_amount_l == 0.0
    assert 0.0 < exact_change_l < 5e-296
