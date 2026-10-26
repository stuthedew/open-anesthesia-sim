"""Each volume and partition coefficient is refused outside the numerical envelope.

`core/numerical_envelope.py` declares where core's arithmetic has been checked
against a high-precision evaluation (`PL-QX2G`). Before that item, a volume or a
partition coefficient was checked only as positive and finite. A tissue of
1e-300 L with a tissue:blood coefficient of 1e-30 then raised a bare
`ZeroDivisionError`. A tissue of 1e307 L with a tissue:gas coefficient of
1e-307 had an infinite time constant, so its own closed-form step never moved
it.

These tests probe each envelope at both edges and one representable value past
each. They check the tissue:blood quotient, which can fall outside the envelope
even when both of its coefficients are inside it. They also pin the measurement
that set the bounds: at every corner of the envelope, the 0.1 s step needs no
more squarings than a shipped run needs over 24 hours.
"""

import re
from dataclasses import replace
from decimal import Decimal, getcontext
from itertools import product
from math import ceil, inf, isfinite, log2, nan, nextafter
from typing import NamedTuple

import pytest

from anesthesia_sim.core.blood import VenousBloodCompartment
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    STATE_SIZE,
    TissueGroupEquationSettings,
    UptakeEquationSettings,
    build_system_matrix,
)
from anesthesia_sim.core.matrix_exponential import (
    MAXIMUM_SERIES_ARGUMENT_NORM,
    Matrix,
    matrix_exponential,
)
from anesthesia_sim.core.numerical_envelope import (
    MAXIMUM_PARTITION_COEFFICIENT,
    MAXIMUM_VOLUME_L,
    MINIMUM_PARTITION_COEFFICIENT,
    MINIMUM_VOLUME_L,
    CompartmentVolume,
    PartitionCoefficient,
    require_compartment_volume,
    tissue_blood_partition_coefficient,
)
from anesthesia_sim.core.parameters import (
    load_reference_adult_parameters,
    load_reference_circle_system_parameters,
    load_sevoflurane_parameters,
)
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    AlveolarVentilation,
    CardiacOutput,
    FreshGasFlow,
)
from anesthesia_sim.core.tissue import TissueGroup
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

LONGEST_STEP_S = 0.1
"""The 0.1 s step that the interface takes, the longest that a run supports."""

MOST_SQUARINGS = 19
"""The most squarings that the 0.1 s step needs at any envelope corner, measured on 2026-10-25.

It is also the most that the shipped parameters need over the 24-hour
horizon. `docs/MODEL.md` § "The numerical envelope" states both counts.
"""


class Envelope(NamedTuple):
    """One checked type and the closed interval it is built inside."""

    checked: type[CompartmentVolume] | type[PartitionCoefficient]
    minimum: float
    maximum: float
    unit: str
    name: str


ENVELOPES = (
    Envelope(CompartmentVolume, 1e-2, 1e4, " L", "volume_l"),
    Envelope(PartitionCoefficient, 1e-3, 1e4, "", "partition_coefficient"),
)
"""The bounds as `PL-QX2G` chose them, written here so that a change to the constants fails."""


def _refusal(envelope: Envelope, value: float) -> str:
    return (
        f"^{re.escape(envelope.name)} of {re.escape(repr(value))} is outside the numerical "
        f"envelope of "
        f"{envelope.minimum:g} to {envelope.maximum:g}{envelope.unit}, the range over which "
        "core's arithmetic has been checked against a high-precision evaluation "
        r'\(docs/MODEL\.md, "The numerical envelope"\)$'
    )


def test_the_declared_bounds_are_the_ones_the_measurement_chose() -> None:
    assert (MINIMUM_VOLUME_L, MAXIMUM_VOLUME_L) == (ENVELOPES[0].minimum, ENVELOPES[0].maximum)
    assert (MINIMUM_PARTITION_COEFFICIENT, MAXIMUM_PARTITION_COEFFICIENT) == (
        ENVELOPES[1].minimum,
        ENVELOPES[1].maximum,
    )


@pytest.mark.parametrize("envelope", ENVELOPES, ids=lambda envelope: envelope.checked.__name__)
def test_every_volume_and_partition_coefficient_is_refused_outside_its_numerical_envelope(
    envelope: Envelope,
) -> None:
    """Both edges are inside, and the representable value just past each is refused.

    The interval is closed, so each edge builds the type and keeps its value
    exactly. `math.nextafter` gives the nearest `float` beyond each edge, which
    is the smallest step past it that a caller could pass.
    """

    for edge in (envelope.minimum, envelope.maximum):
        built = envelope.checked(edge)

        assert type(built) is envelope.checked
        assert built == edge

    below = nextafter(envelope.minimum, 0.0)
    above = nextafter(envelope.maximum, inf)

    for past in (below, above):
        with pytest.raises(SimulationConfigurationError, match=_refusal(envelope, past)):
            envelope.checked(past)


@pytest.mark.parametrize("value", [0.0, -0.0, -1.0, nan, inf, -inf])
@pytest.mark.parametrize("envelope", ENVELOPES, ids=lambda envelope: envelope.checked.__name__)
def test_zero_a_negative_value_and_a_non_finite_value_are_outside_every_envelope(
    envelope: Envelope, value: float
) -> None:
    with pytest.raises(SimulationConfigurationError, match=_refusal(envelope, value)):
        envelope.checked(value)


@pytest.mark.parametrize("envelope", ENVELOPES, ids=lambda envelope: envelope.checked.__name__)
def test_a_refusal_names_the_value_by_the_name_its_caller_gives(envelope: Envelope) -> None:
    named = envelope._replace(name="fat volume_l")

    with pytest.raises(SimulationConfigurationError, match=_refusal(named, 1e-300)):
        envelope.checked(1e-300, name="fat volume_l")


def test_a_volume_is_not_built_from_a_partition_coefficient_or_the_reverse() -> None:
    """The two types share a range from 1e-2 to 1e4, so only the type tells them apart."""

    with pytest.raises(TypeError, match=r"^volume_l of 2\.0 was built as PartitionCoefficient"):
        CompartmentVolume(PartitionCoefficient(2.0))

    with pytest.raises(
        TypeError, match=r"^partition_coefficient of 2\.0 was built as CompartmentVolume"
    ):
        PartitionCoefficient(CompartmentVolume(2.0))


# The tissue:blood coefficient is a quotient, checked where it is formed.


def test_a_tissue_blood_coefficient_at_either_edge_is_formed() -> None:
    lowest = tissue_blood_partition_coefficient(
        PartitionCoefficient(1e-3), PartitionCoefficient(1.0), name="fat"
    )
    highest = tissue_blood_partition_coefficient(
        PartitionCoefficient(1e4), PartitionCoefficient(1.0), name="fat"
    )

    assert type(lowest) is PartitionCoefficient
    assert (lowest, highest) == (1e-3, 1e4)


@pytest.mark.parametrize(("tissue_gas", "blood_gas"), [(1e-3, 2.0), (1e-3, 1e4), (1e4, 0.5)])
def test_a_tissue_blood_coefficient_outside_the_envelope_is_refused_with_both_factors_named(
    tissue_gas: float, blood_gas: float
) -> None:
    """Two coefficients inside the envelope can form a quotient outside it.

    A tissue:gas coefficient of 1e-3 over a blood:gas coefficient of 1e4 is a
    tissue:blood coefficient of 1e-7. In a 1e-3 L tissue receiving nearly all of
    the cardiac output, that made a wash-in rate of 1.6e9 per second, and the
    step needed the full 32 squarings.
    """

    quotient = re.escape(repr(tissue_gas / blood_gas))

    with pytest.raises(
        SimulationConfigurationError,
        match=(
            rf"^fat tissue_blood_partition_coefficient of {quotient} is outside the numerical "
            r"envelope of 0\.001 to 10000, .*; it is the tissue:gas coefficient of "
            rf"{re.escape(repr(tissue_gas))} divided by the blood:gas coefficient of "
            rf"{re.escape(repr(blood_gas))}$"
        ),
    ):
        tissue_blood_partition_coefficient(
            PartitionCoefficient(tissue_gas),
            PartitionCoefficient(blood_gas),
            name="fat tissue_blood_partition_coefficient",
        )


def test_a_tissue_blood_quotient_refuses_a_factor_never_built_as_a_coefficient() -> None:
    """A bare `float` factor was never checked against the envelope, so it is refused by name."""

    with pytest.raises(
        TypeError, match=r"^fat tissue:gas factor of 34\.0 was not built as Partition"
    ):
        tissue_blood_partition_coefficient(34.0, PartitionCoefficient(0.65), name="fat")  # type: ignore[arg-type]

    with pytest.raises(
        TypeError, match=r"^fat blood:gas factor of 0\.65 was not built as Partition"
    ):
        tissue_blood_partition_coefficient(PartitionCoefficient(34.0), 0.65, name="fat")  # type: ignore[arg-type]


def _fat(blood_gas: float, tissue_gas: float) -> TissueGroup:
    return TissueGroup(
        name="fat",
        volume_l=CompartmentVolume(14.5),
        perfusion_fraction=0.06,
        blood_gas_partition_coefficient=PartitionCoefficient(blood_gas),
        tissue_gas_partition_coefficient=PartitionCoefficient(tissue_gas),
    )


def test_a_tissue_group_refuses_coefficients_whose_quotient_leaves_the_envelope() -> None:
    with pytest.raises(SimulationConfigurationError, match=r"^fat tissue_blood_partition_coeff"):
        _fat(blood_gas=1e4, tissue_gas=1e-3)


def test_a_later_write_of_either_coefficient_is_checked_against_the_other() -> None:
    """The quotient is a relation between two fields, so the second write checks it.

    Writing a blood:gas coefficient of 1e4 against the tissue:gas coefficient of 1.10
    gives a quotient of 1.1e-4. Writing a tissue:gas coefficient of 1e4 against the
    blood:gas coefficient of 0.65 gives 1.5e4. Each write is refused, and neither
    coefficient changes.
    """

    group = _fat(blood_gas=0.65, tissue_gas=1.10)

    with pytest.raises(SimulationConfigurationError, match=r"^fat tissue_blood_partition_coeff"):
        group.blood_gas_partition_coefficient = PartitionCoefficient(1e4)

    with pytest.raises(SimulationConfigurationError, match=r"^fat tissue_blood_partition_coeff"):
        group.tissue_gas_partition_coefficient = PartitionCoefficient(1e4)

    assert (group.blood_gas_partition_coefficient, group.tissue_gas_partition_coefficient) == (
        0.65,
        1.10,
    )


def test_an_agent_whose_tissue_blood_coefficient_leaves_the_envelope_is_refused() -> None:
    sevoflurane = load_sevoflurane_parameters()

    quotient = re.escape(repr(1e-3 / 10.0))

    with pytest.raises(
        SimulationConfigurationError,
        match=rf"^fat_tissue_blood_partition_coefficient of {quotient} ",
    ):
        replace(
            sevoflurane,
            blood_gas_partition_coefficient=PartitionCoefficient(10.0),
            fat_tissue_gas_partition_coefficient=PartitionCoefficient(1e-3),
            vessel_rich_tissue_gas_partition_coefficient=PartitionCoefficient(10.0),
            muscle_tissue_gas_partition_coefficient=PartitionCoefficient(10.0),
        )


def test_the_tissue_blood_coefficient_a_run_reads_is_the_checked_quotient() -> None:
    sevoflurane = load_sevoflurane_parameters()
    fat = sevoflurane.fat_tissue_blood_partition_coefficient

    assert type(fat) is PartitionCoefficient
    # 34.0 / 0.65, the shipped fat:gas and blood:gas coefficients
    # (data/agents/sevoflurane.json), divided here rather than read back.
    assert fat == 34.0 / 0.65


# The two defects the item reproduced, now refused when their inputs are built.


def test_a_tissue_whose_wash_in_rate_divided_by_zero_is_refused_when_it_is_built() -> None:
    """A volume of 1e-300 L times a coefficient of 1e-30 underflowed to zero (`PL-QX2G`).

    Before the fix, `TissueGroupEquationSettings("fat", 1e-300, 1.0,
    1e-30).washin_rate_s` raised a bare `ZeroDivisionError`. Neither input can
    be built now, and a bare `float` is refused where the record stores it.
    """

    with pytest.raises(SimulationConfigurationError, match=r"^volume_l of 1e-300 is outside"):
        CompartmentVolume(1e-300)

    with pytest.raises(
        SimulationConfigurationError, match=r"^partition_coefficient of 1e-30 is outside"
    ):
        PartitionCoefficient(1e-30)

    with pytest.raises(TypeError, match=r"^fat volume_l of 1e-300 was not built as"):
        TissueGroupEquationSettings("fat", 1e-300, 1.0, 1e-30)  # type: ignore[arg-type]


def test_a_tissue_whose_time_constant_overflowed_is_refused_when_it_is_built() -> None:
    """A 1e307 L tissue at a tissue:gas coefficient of 1e-307 overflowed its time constant.

    Its capacity was an ordinary 1 L, but `time_constant_s` evaluated
    `60 * 1e307` first and overflowed to `inf` (`PL-QX2G`). So
    `TissueGroup.advance`, the tissue's own closed-form step, never moved it.
    """

    with pytest.raises(SimulationConfigurationError, match=r"^volume_l of 1e\+307 is outside"):
        CompartmentVolume(1e307)

    with pytest.raises(
        SimulationConfigurationError, match=r"^partition_coefficient of 1e-307 is outside"
    ):
        PartitionCoefficient(1e-307)


def test_every_product_and_quotient_at_the_envelope_s_corners_is_finite_and_positive() -> None:
    """A product or quotient of positive inputs takes its extremes at the corners of their ranges.

    Each corner puts every input at one end of its interval. So a tissue group
    and a venous pool built at each corner, and perfused at the largest
    supported cardiac output, bound every capacity, time constant and wash-in
    rate that the envelope admits.
    """

    volumes = (MINIMUM_VOLUME_L, MAXIMUM_VOLUME_L)
    coefficients = (MINIMUM_PARTITION_COEFFICIENT, MAXIMUM_PARTITION_COEFFICIENT)
    flow_l_min = MAXIMUM_CARDIAC_OUTPUT_L_MIN

    for volume, coefficient in product(volumes, coefficients):
        pool = VenousBloodCompartment(
            volume_l=CompartmentVolume(volume),
            blood_gas_partition_coefficient=PartitionCoefficient(coefficient),
        )
        tissue = TissueGroup(
            name="corner",
            volume_l=CompartmentVolume(volume),
            perfusion_fraction=1.0,
            blood_gas_partition_coefficient=PartitionCoefficient(1.0),
            tissue_gas_partition_coefficient=PartitionCoefficient(coefficient),
        )
        settings = TissueGroupEquationSettings(
            "corner", CompartmentVolume(volume), flow_l_min, PartitionCoefficient(coefficient)
        )

        for value in (
            pool.capacity_l,
            pool.time_constant_s(flow_l_min),
            tissue.capacity_l,
            tissue.time_constant_s(flow_l_min),
            settings.washin_rate_s,
        ):
            assert isfinite(value)
            assert value > 0.0


# The measurement that set the bounds.


def _settings(
    volumes: tuple[float, float, float], blood_gas: float, tissues: tuple[tuple[float, float], ...]
) -> UptakeEquationSettings:
    """Settings at the widest supported flows, with cardiac output split as the patient file's."""

    circuit_l, alveolar_l, venous_l = volumes
    patient = load_reference_adult_parameters()
    fractions = (
        patient.vessel_rich_perfusion_fraction,
        patient.muscle_perfusion_fraction,
        patient.fat_perfusion_fraction,
    )
    flows = [MAXIMUM_CARDIAC_OUTPUT_L_MIN * fraction for fraction in fractions]
    flows[-1] = MAXIMUM_CARDIAC_OUTPUT_L_MIN - flows[0] - flows[1]

    return UptakeEquationSettings(
        circuit_volume_l=CompartmentVolume(circuit_l),
        alveolar_volume_l=CompartmentVolume(alveolar_l),
        venous_volume_l=CompartmentVolume(venous_l),
        fresh_gas_flow_l_min=FreshGasFlow(MAXIMUM_FRESH_GAS_FLOW_L_MIN),
        alveolar_ventilation_l_min=AlveolarVentilation(MAXIMUM_ALVEOLAR_VENTILATION_L_MIN),
        cardiac_output_l_min=CardiacOutput(MAXIMUM_CARDIAC_OUTPUT_L_MIN),
        blood_gas_partition_coefficient=PartitionCoefficient(blood_gas),
        delivered_concentration_percent=Percent(2.0),
        max_delivered_concentration_percent=Percent(8.0),
        tissues=tuple(
            TissueGroupEquationSettings(
                name, CompartmentVolume(volume), flow, PartitionCoefficient(tissue_blood)
            )
            for name, (volume, tissue_blood), flow in zip(
                ("vessel_rich", "muscle", "fat"), tissues, flows, strict=True
            )
        ),
    )


def _squarings(matrix: Matrix, interval_s: float) -> int:
    """Return how many squarings scale the shifted matrix to the series bound, computed here.

    `core/matrix_exponential.py` documents the rule. Shift the diagonal by the
    fastest rate, take the largest row sum times the interval, and halve it
    until it is at most `MAXIMUM_SERIES_ARGUMENT_NORM`. This is the same rule,
    computed independently of the module's own code.
    """

    shift = max(-matrix[index][index] for index in range(STATE_SIZE))
    norm = interval_s * max(
        sum(value + shift * (row == column) for column, value in enumerate(matrix_row))
        for row, matrix_row in enumerate(matrix)
    )

    if norm <= MAXIMUM_SERIES_ARGUMENT_NORM:
        return 0

    return ceil(log2(norm / MAXIMUM_SERIES_ARGUMENT_NORM))


def _corner_settings() -> list[UptakeEquationSettings]:
    volumes = (MINIMUM_VOLUME_L, MAXIMUM_VOLUME_L)
    coefficients = (MINIMUM_PARTITION_COEFFICIENT, MAXIMUM_PARTITION_COEFFICIENT)
    corners = []

    for circuit_l, alveolar_l, venous_l, blood_gas in product(
        volumes, volumes, volumes, coefficients
    ):
        for tissues in product(product(volumes, coefficients), repeat=3):
            # The tissue:gas coefficient is tissue:blood times blood:gas, and
            # it must lie inside the envelope too.
            if all(
                MINIMUM_PARTITION_COEFFICIENT
                <= tissue_blood * blood_gas
                <= MAXIMUM_PARTITION_COEFFICIENT
                for _, tissue_blood in tissues
            ):
                corners.append(_settings((circuit_l, alveolar_l, venous_l), blood_gas, tissues))

    return corners


def _shipped_settings() -> UptakeEquationSettings:
    sevoflurane = load_sevoflurane_parameters()
    patient = load_reference_adult_parameters()

    return _settings(
        (6.0, patient.alveolar_gas_volume_l, patient.venous_pool_volume_l),
        sevoflurane.blood_gas_partition_coefficient,
        (
            (
                patient.vessel_rich_volume_l,
                sevoflurane.vessel_rich_tissue_blood_partition_coefficient,
            ),
            (patient.muscle_volume_l, sevoflurane.muscle_tissue_blood_partition_coefficient),
            (patient.fat_volume_l, sevoflurane.fat_tissue_blood_partition_coefficient),
        ),
    )


def test_no_corner_needs_more_squarings_at_the_step_than_a_shipped_run_needs_over_a_day() -> None:
    """At every corner, the 0.1 s step's error bound is no larger than a shipped run's over 24 h.

    Each squaring can double the rounding error, so the number of squarings
    sets the accuracy (`core/matrix_exponential.py`, "What it costs"). The
    shipped sevoflurane system at the widest supported flows needs 19
    squarings over the 24-hour horizon. The stiffest corner, a 1e-2 L alveolar
    volume with a blood:gas coefficient of 1e4, needs 19 at the 0.1 s step. A
    lower volume bound of 1e-3 L needed 22 there (measured 2026-10-25).
    """

    corners = _corner_settings()
    most = max(_squarings(build_system_matrix(corner), LONGEST_STEP_S) for corner in corners)
    shipped_day = _squarings(
        build_system_matrix(_shipped_settings()), MAXIMUM_ELAPSED_SIMULATION_TIME_S
    )

    # Each tissue:blood edge pairs with one blood:gas edge, so 8 of 64 tissue
    # combinations survive at each blood:gas edge: 8 volumes x 2 x 8.
    assert len(corners) == 128
    assert (most, shipped_day) == (MOST_SQUARINGS, MOST_SQUARINGS)


def _decimal_exponential(matrix: Matrix, interval_s: str) -> list[list[Decimal]]:
    """`exp(matrix * interval_s)` at 50 significant digits, by an unshifted Taylor series.

    The argument is halved until its largest row sum is at most 1/16, the
    series is summed to 40 terms, and the result is squared back. At 50 digits
    neither the cancellation in the unshifted series nor the squarings come
    near the double-precision error being measured.
    """

    getcontext().prec = 50
    size = len(matrix)
    argument = [[Decimal(value) * Decimal(interval_s) for value in row] for row in matrix]
    halvings = 0

    while max(sum(abs(value) for value in row) for row in argument) > Decimal("0.0625"):
        argument = [[value / 2 for value in row] for row in argument]
        halvings += 1

    def multiply(left: list[list[Decimal]], right: list[list[Decimal]]) -> list[list[Decimal]]:
        return [
            [sum(left[i][k] * right[k][j] for k in range(size)) for j in range(size)]
            for i in range(size)
        ]

    total = [[Decimal(int(i == j)) for j in range(size)] for i in range(size)]
    term = [row[:] for row in total]

    for order in range(1, 41):
        term = [[value / order for value in row] for row in multiply(term, argument)]
        total = [
            [a + b for a, b in zip(r, s, strict=True)] for r, s in zip(total, term, strict=True)
        ]

    for _ in range(halvings):
        total = multiply(total, total)

    return total


def test_the_step_at_the_stiffest_corner_agrees_with_a_high_precision_evaluation() -> None:
    """The stiffest corner's 0.1 s propagator is accepted, and is accurate to its stated bound.

    After `s` squarings the module bounds the error at about `2**s` times
    double precision's 2**-52. At 19 squarings that is 1.2e-10, and on
    2026-10-25 the worst entry measured 7.5e-11. The test allows three times
    the bound, because the module's own measurement found errors of 0.6 to 2.7
    times the bound (`MAXIMUM_SQUARINGS`).
    """

    # The shipped circuit, venous pool and tissue volumes, with a tissue:blood
    # coefficient of 1 so that each tissue:gas coefficient stays inside the envelope.
    stiffest = _settings(
        (6.0, MINIMUM_VOLUME_L, 1.222),
        MAXIMUM_PARTITION_COEFFICIENT,
        ((6.0, 1.0), (33.0, 1.0), (14.5, 1.0)),
    )
    matrix = build_system_matrix(stiffest)

    assert _squarings(matrix, LONGEST_STEP_S) == MOST_SQUARINGS

    propagator = matrix_exponential(matrix, LONGEST_STEP_S)
    exact = _decimal_exponential(matrix, "0.1")
    bound = 3 * 2.0**MOST_SQUARINGS * 2.0**-52

    worst = max(
        float(abs(Decimal(propagator[i][j]) - exact[i][j]) / exact[i][j])
        for i in range(STATE_SIZE)
        for j in range(STATE_SIZE)
        if exact[i][j] > Decimal("1e-300")
    )

    assert worst <= bound


# Each refusal names the value it refused, as `.claude/rules/sources-and-docstrings.md` asks.

AGENT_COEFFICIENTS = (
    "blood_gas_partition_coefficient",
    "vessel_rich_tissue_gas_partition_coefficient",
    "muscle_tissue_gas_partition_coefficient",
    "fat_tissue_gas_partition_coefficient",
)

PATIENT_VOLUMES = (
    "alveolar_gas_volume_l",
    "venous_pool_volume_l",
    "vessel_rich_volume_l",
    "muscle_volume_l",
    "fat_volume_l",
)


@pytest.mark.parametrize("field", AGENT_COEFFICIENTS)
def test_an_agent_refuses_a_bare_coefficient_by_its_field_name(field: str) -> None:
    with pytest.raises(TypeError, match=rf"^{field} of 0\.5 was not built as PartitionCoefficient"):
        replace(load_sevoflurane_parameters(), **{field: 0.5})


@pytest.mark.parametrize("field", PATIENT_VOLUMES)
def test_a_patient_refuses_a_bare_volume_by_its_field_name(field: str) -> None:
    with pytest.raises(TypeError, match=rf"^{field} of 2\.0 was not built as CompartmentVolume"):
        replace(load_reference_adult_parameters(), **{field: 2.0})


def test_a_machine_profile_and_a_circuit_refuse_a_bare_volume_by_name() -> None:
    with pytest.raises(TypeError, match=r"^circuit_volume_l of 6\.0 was not built as Compartment"):
        replace(load_reference_circle_system_parameters(), circuit_volume_l=6.0)

    circuit = AgentUptakeSystem.for_agent("sevoflurane").circuit

    with pytest.raises(TypeError, match=r"^circuit_volume_l of 3\.0 was not built as Compartment"):
        circuit.set_circuit_volume(3.0)  # type: ignore[arg-type]


def test_a_swapped_quantity_and_a_non_number_are_refused_by_name() -> None:
    """A flow stored as a volume is named as the flow it was built as, and a `str` by its type."""

    with pytest.raises(
        TypeError,
        match=r"^circuit_volume_l of 5\.0 was built as FreshGasFlow, which is not CompartmentVol",
    ):
        require_compartment_volume("circuit_volume_l", FreshGasFlow(5.0))

    with pytest.raises(TypeError, match=r"^fat volume_l of '2' has type str, not int or float"):
        CompartmentVolume("2", name="fat volume_l")  # type: ignore[arg-type]
