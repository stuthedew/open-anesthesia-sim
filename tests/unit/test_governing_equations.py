"""Check the system matrix entry by entry against the equations it transcribes.

`build_system_matrix` is the whole model, so its main risk is a mistyped
index or sign. A matrix that is wrong in one entry still produces a smooth,
plausible trajectory. The reference gates would catch the error only as a
number that disagrees with the oracle, without saying where the error is.

So every expected value below is written out from `docs/MODEL.md`
§ "Governing equations", independently of the module under test. The settings
are chosen so that no two rates share a value, and so a transposed index
cannot pass. The propagator depends on three structural properties: the
matrix is Metzler, the unit state is constant, and the compartments conserve
agent. These are asserted separately, because they are true for every
parameter set and not only for these numbers.
"""

import copy
import io
import pickle
from dataclasses import fields
from math import inf, nan, nextafter
from types import SimpleNamespace
from typing import NamedTuple

import numpy
import pytest

from anesthesia_sim.core.concentration import Percent, fraction_from_percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    DELIVERED_AGENT_L,
    EXHAUSTED_AGENT_L,
    FIRST_TISSUE_FRACTION,
    INSPIRED_FRACTION,
    MAXIMUM_CUMULATIVE_AGENT_L,
    STATE_SIZE,
    TISSUE_GROUP_COUNT,
    UNIT_STATE,
    VENOUS_FRACTION,
    TissueGroupEquationSettings,
    UptakeEquationSettings,
    build_system_matrix,
    require_canonical_state,
)
from anesthesia_sim.core.matrix_exponential import matrix_exponential
from anesthesia_sim.core.numerical_envelope import CompartmentVolume, PartitionCoefficient
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
    AlveolarVentilation,
    CardiacOutput,
    FreshGasFlow,
)
from anesthesia_sim.core.units import SECONDS_PER_MINUTE

# These values are deliberately unlike each other and unlike the reference
# adult's. Every volume, flow and coefficient below is distinct, so an entry
# written into the wrong row or column lands on a value that nothing else has.
CIRCUIT_VOLUME_L = CompartmentVolume(6.0)
ALVEOLAR_VOLUME_L = CompartmentVolume(2.5)
VENOUS_VOLUME_L = CompartmentVolume(3.5)
FRESH_GAS_FLOW_L_MIN = FreshGasFlow(4.2)
ALVEOLAR_VENTILATION_L_MIN = AlveolarVentilation(6.6)
CARDIAC_OUTPUT_L_MIN = CardiacOutput(7.8)
FRESH_GAS_FLOW_L_S = FRESH_GAS_FLOW_L_MIN / SECONDS_PER_MINUTE
ALVEOLAR_VENTILATION_L_S = ALVEOLAR_VENTILATION_L_MIN / SECONDS_PER_MINUTE
CARDIAC_OUTPUT_L_S = CARDIAC_OUTPUT_L_MIN / SECONDS_PER_MINUTE
BLOOD_GAS = PartitionCoefficient(0.65)
DELIVERED_PERCENT = Percent(2.0)
DELIVERED_FRACTION = fraction_from_percent(DELIVERED_PERCENT)
MAX_DELIVERED_PERCENT = Percent(8.0)
"""Sevoflurane's vaporizer maximum, which the `PL-BBMG` reproduction exceeded."""

TISSUES = (
    ("vessel_rich", CompartmentVolume(6.0), 5.85, PartitionCoefficient(1.7)),
    ("muscle", CompartmentVolume(33.0), 1.482, PartitionCoefficient(2.9)),
    ("fat", CompartmentVolume(14.5), 0.468, PartitionCoefficient(51.0)),
)
"""(name, volume_l, blood_flow_l_min, tissue:blood coefficient) for each group.

The three flows sum to `CARDIAC_OUTPUT_L_MIN`, as the venous balance requires
and `UptakeEquationSettings` now checks. They are otherwise unlike each other
and unlike every other constant here, so a transposed index cannot pass.
"""


# The end of a shared guard's refusal message, which names the refused value
# and the reason (`PL-T137`). The guard's own tests pin each reason. The tests
# here pin the field name.
REFUSAL_REASON = r", and [^ ]+ is (?:not finite|not greater than zero|negative)$"


def _settings(**overrides: object) -> UptakeEquationSettings:
    fields: dict[str, object] = {
        "circuit_volume_l": CIRCUIT_VOLUME_L,
        "alveolar_volume_l": ALVEOLAR_VOLUME_L,
        "venous_volume_l": VENOUS_VOLUME_L,
        "fresh_gas_flow_l_min": FRESH_GAS_FLOW_L_MIN,
        "alveolar_ventilation_l_min": ALVEOLAR_VENTILATION_L_MIN,
        "cardiac_output_l_min": CARDIAC_OUTPUT_L_MIN,
        "blood_gas_partition_coefficient": BLOOD_GAS,
        "delivered_concentration_percent": DELIVERED_PERCENT,
        "max_delivered_concentration_percent": MAX_DELIVERED_PERCENT,
        "tissues": tuple(
            TissueGroupEquationSettings(
                name=name,
                volume_l=volume_l,
                blood_flow_l_min=blood_flow_l_min,
                tissue_blood_partition_coefficient=tissue_blood,
            )
            for name, volume_l, blood_flow_l_min, tissue_blood in TISSUES
        ),
    }
    fields.update(overrides)

    return UptakeEquationSettings(**fields)  # type: ignore[arg-type]


class Flow(NamedTuple):
    """One flow field, with its checked type, its supported range and a reproduced bad value.

    The range is the closed interval that the type admits. The bad value is
    the one that `PL-HSFV` found a record holding on 2026-10-04.
    """

    field: str
    flow_type: type[float]
    minimum: float
    maximum: float
    reproduced_l_min: float


SUPPORTED_FLOWS = (
    Flow(
        "fresh_gas_flow_l_min",
        FreshGasFlow,
        MINIMUM_FRESH_GAS_FLOW_L_MIN,
        MAXIMUM_FRESH_GAS_FLOW_L_MIN,
        500.0,
    ),
    Flow(
        "alveolar_ventilation_l_min",
        AlveolarVentilation,
        MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
        200.0,
    ),
    Flow(
        "cardiac_output_l_min",
        CardiacOutput,
        MINIMUM_CARDIAC_OUTPUT_L_MIN,
        MAXIMUM_CARDIAC_OUTPUT_L_MIN,
        1000.0,
    ),
)

FLOW_IDS = [flow.field for flow in SUPPORTED_FLOWS]


def _settings_with_flow(field: str, value: float) -> UptakeEquationSettings:
    """Return `_settings` with one flow changed, scaling the tissue flows with cardiac output.

    The venous balance requires the tissue flows to sum to cardiac output. So
    changing cardiac output alone would be refused for the mismatch rather
    than for the range. Instead, each tissue keeps its share of the output.
    """

    if field != "cardiac_output_l_min":
        return _settings(**{field: value})

    return _settings(
        cardiac_output_l_min=value,
        tissues=tuple(
            TissueGroupEquationSettings(
                name=name,
                volume_l=volume_l,
                blood_flow_l_min=blood_flow_l_min / CARDIAC_OUTPUT_L_MIN * value,
                tissue_blood_partition_coefficient=tissue_blood,
            )
            for name, volume_l, blood_flow_l_min, tissue_blood in TISSUES
        ),
    )


@pytest.mark.parametrize("flow", SUPPORTED_FLOWS, ids=FLOW_IDS)
def test_accepts_each_flow_at_both_ends_of_its_supported_range(flow: Flow) -> None:
    """The intervals are closed, and a record may store either end (`PL-HSFV`).

    Both ends occur in measured cases. One reference trajectory keeps cardiac
    output at zero through its loading phase. The envelope corner that every
    reference gate drives sits on all three maxima at once.
    """

    for value in (flow.minimum, flow.maximum):
        settings = _settings_with_flow(flow.field, flow.flow_type(value))

        assert getattr(settings, flow.field) == value
        assert isinstance(getattr(settings, flow.field), flow.flow_type)


@pytest.mark.parametrize("flow", SUPPORTED_FLOWS, ids=FLOW_IDS)
def test_rejects_a_flow_outside_its_supported_range(flow: Flow) -> None:
    """A flow outside its range is refused before any record can store it (`PL-HSFV`).

    On 2026-10-04, `RunDefinition` propagated a record rebuilt with a cardiac
    output of 1000 L/min, a hundred times the supported maximum. The record
    checked only that the tissue flows summed to cardiac output, and the range
    guards ran only in the compartments. Each flow field now takes a type that
    only its guard builds (`PL-0YYV`). So the guard refuses the value, in its
    own words, at the first float past the maximum just as at a hundred times
    the maximum. The record is never built, and `_settings_with_flow` is never
    entered. In the test below, a value does get as far as the record.
    """

    past_each_end = (nextafter(flow.maximum, inf), nextafter(flow.minimum, -inf))

    for value in (*past_each_end, flow.reproduced_l_min, nan, inf):
        with pytest.raises(SimulationConfigurationError, match="supported input range"):
            _settings_with_flow(flow.field, flow.flow_type(value))


@pytest.mark.parametrize("flow", SUPPORTED_FLOWS, ids=FLOW_IDS)
def test_rejects_a_flow_handed_in_as_a_bare_float(flow: Flow) -> None:
    """A flow never built as its type is refused by the record, in range or not (`PL-0YYV`).

    The record is where a flow is stored, so it performs the runtime half of
    the type check. A caller that forgot the type, such as a notebook, a test
    or a deserializer, is told which type to build and where. Its float is not
    range-checked again here. The value is the record's own and inside the
    range, so what is refused is the missing check and not the number.
    """

    held = getattr(_settings(), flow.field)

    with pytest.raises(TypeError, match=f"not built as {flow.flow_type.__name__}"):
        _settings(**{flow.field: float(held)})


# --- The dial against the vaporizer maximum (PL-BBMG) ------------------------
#
# This is the one bound in the record that is a relation rather than a range.
# A dial setting can be delivered only up to the maximum of the vaporizer in
# use. So the record carries the maximum beside the dial setting, and it
# refuses a dial above the maximum through the guard that the circuit calls.


def test_rejects_a_dial_above_the_vaporizer_maximum() -> None:
    """`PL-BBMG`, reproduced 2026-10-04: 20% sevoflurane against an 8% maximum built a record.

    The record stored the dial setting alone and bounded it only at 100, the
    limit every percent obeys. So the record that a run is built from accepted
    a dial setting that the circuit refuses. The record now refuses it, in the
    circuit's own sentence. It also refuses the first float above the maximum.
    """

    with pytest.raises(
        SimulationConfigurationError,
        match=r"delivered_concentration_percent exceeds the vaporizer maximum "
        r"\(20% requested, 8% maximum\)",
    ):
        _settings(delivered_concentration_percent=Percent(20.0))

    with pytest.raises(SimulationConfigurationError, match="exceeds the vaporizer maximum"):
        _settings(delivered_concentration_percent=Percent(nextafter(MAX_DELIVERED_PERCENT, inf)))


def test_accepts_a_dial_at_the_vaporizer_maximum_and_the_vaporizer_off() -> None:
    """The maximum is a dial position the machine has, and zero is washout."""

    for dialled in (MAX_DELIVERED_PERCENT, Percent(0.0)):
        settings = _settings(delivered_concentration_percent=dialled)

        assert settings.delivered_concentration_percent == dialled
        assert settings.max_delivered_concentration_percent == MAX_DELIVERED_PERCENT


@pytest.mark.parametrize("maximum", [0.0, -0.0], ids=repr)
def test_rejects_a_vaporizer_maximum_no_vaporizer_has(maximum: float) -> None:
    """The maximum is checked as `BreathingCircuit` checks its own: a positive percent.

    The record itself refuses zero of either sign. A value outside 0 to 100
    cannot be built as the `Percent` that the record takes.
    `tests/unit/test_concentration.py` pins that refusal on the constructor
    (`PL-4R3W`).
    """

    with pytest.raises(
        SimulationConfigurationError,
        match="^max_delivered_concentration_percent must be positive and finite" + REFUSAL_REASON,
    ):
        _settings(
            delivered_concentration_percent=Percent(0.0),
            max_delivered_concentration_percent=Percent(maximum),
        )


def test_a_record_cannot_be_built_without_a_vaporizer_maximum() -> None:
    """The field has no default, so a record that states no maximum is refused outright.

    `BreathingCircuit` defaults its maximum to 100% for a circuit built without
    an agent. A record that defaulted the same way would leave open the gap
    that `PL-BBMG` closes by adding this field.
    """

    held = _settings()
    without_a_maximum = {
        field.name: getattr(held, field.name)
        for field in fields(UptakeEquationSettings)
        if field.name != "max_delivered_concentration_percent"
    }

    with pytest.raises(TypeError, match="max_delivered_concentration_percent"):
        UptakeEquationSettings(**without_a_maximum)


PICKLE_PROTOCOLS = range(pickle.HIGHEST_PROTOCOL + 1)


class _ForgingPickler(pickle.Pickler):
    """Write one record as pickle writes it, with one saved field value replaced.

    The record is written in the exact form that the chosen pickle protocol
    uses, so loading it takes the same path that a saved file would take. Only
    the saved state differs, in the way that a hand edit of a saved run would
    change it.
    """

    def __init__(
        self, buffer: io.BytesIO, protocol: int, target: object, field: str, value: object
    ) -> None:
        super().__init__(buffer, protocol=protocol)
        self._protocol = protocol
        self._target = target
        self._field = field
        self._value = value

    def reducer_override(self, obj: object) -> object:
        if obj is not self._target:
            return NotImplemented

        constructor, arguments, state = obj.__reduce_ex__(self._protocol)[:3]
        names = [field.name for field in fields(obj)]  # type: ignore[arg-type]
        forged = list(state)
        forged[names.index(self._field)] = self._value

        return constructor, arguments, forged


def _forged_pickle(
    record: object, protocol: int, field: str, value: object, outer: object = None
) -> bytes:
    """Return `outer` (or `record` itself) pickled with `record`'s `field` saved as `value`."""

    buffer = io.BytesIO()
    _ForgingPickler(buffer, protocol, record, field, value).dump(record if outer is None else outer)

    return buffer.getvalue()


@pytest.mark.parametrize("protocol", PICKLE_PROTOCOLS)
def test_a_settings_record_survives_pickling_and_copying_unchanged(protocol: int) -> None:
    """A record restored through its checks still equals the record that was saved."""

    held = _settings()

    assert pickle.loads(pickle.dumps(held, protocol=protocol)) == held
    assert (
        pickle.loads(_forged_pickle(held, protocol, "cardiac_output_l_min", CARDIAC_OUTPUT_L_MIN))
        == held
    )
    assert copy.copy(held) == held
    assert copy.deepcopy(held) == held


FORGED_RECORDS = (
    pytest.param("cardiac_output_l_min", 1000.0, TypeError, "cardiac_output_l_min", id="bare-1000"),
    pytest.param("fresh_gas_flow_l_min", nan, TypeError, "fresh_gas_flow_l_min", id="nan-fgf"),
    pytest.param(
        "max_delivered_concentration_percent",
        Percent(1.0),
        SimulationConfigurationError,
        "delivered_concentration_percent",
        id="dial-above-maximum",
    ),
)


@pytest.mark.parametrize("protocol", PICKLE_PROTOCOLS)
@pytest.mark.parametrize(("field", "value", "error", "match"), FORGED_RECORDS)
def test_an_unpickled_settings_record_is_rebuilt_through_its_checks(
    protocol: int, field: str, value: object, error: type[Exception], match: str
) -> None:
    """Unpickling used to restore a record through `__setstate__` without any check (`PL-S11T`).

    Before the fix, a saved record loaded even though its state held cardiac
    output as a bare 1000.0. Its tissue flows still summed to the cardiac
    output that the record had been built with. A `RunDefinition` opened under
    that record advanced. A saved fresh gas flow of NaN loaded too. Each forged
    value is now rejected on load with the constructor's own exception, at
    every pickle protocol.
    """

    with pytest.raises(error, match=match):
        pickle.loads(_forged_pickle(_settings(), protocol, field, value))


@pytest.mark.parametrize("protocol", PICKLE_PROTOCOLS)
def test_an_unpickled_tissue_group_record_is_rebuilt_through_its_checks(protocol: int) -> None:
    """A tissue group's saved blood flow of NaN is refused on load, inside its settings record."""

    held = _settings()

    with pytest.raises(SimulationConfigurationError, match="vessel_rich blood_flow_l_min"):
        pickle.loads(_forged_pickle(held.tissues[0], protocol, "blood_flow_l_min", nan, held))


@pytest.mark.parametrize("protocol", PICKLE_PROTOCOLS)
def test_an_unpickled_settings_record_refuses_tissue_rows_of_another_type(protocol: int) -> None:
    """A saved row that only looks like a tissue group is refused, so its checks cannot be skipped.

    The review of `PL-S11T` found this gap. Three namespaces loaded as a
    record's tissue rows. They carried the right flows, a volume of 1e-300 L
    and a coefficient of 1e-30. `build_system_matrix` then returned a matrix
    that was not finite.
    """

    held = _settings()
    lookalikes = tuple(
        SimpleNamespace(
            name=tissue.name,
            volume_l=1e-300,
            blood_flow_l_min=tissue.blood_flow_l_min,
            blood_flow_l_s=tissue.blood_flow_l_s,
            tissue_blood_partition_coefficient=1e-30,
            washin_rate_s=inf,
        )
        for tissue in held.tissues
    )

    with pytest.raises(TypeError, match="not a SimpleNamespace"):
        pickle.loads(_forged_pickle(held, protocol, "tissues", lookalikes))


def test_a_settings_record_is_not_restored_from_a_state_of_another_shape() -> None:
    """A state other than the list of field values that `dataclass` writes is refused."""

    restored = object.__new__(UptakeEquationSettings)

    with pytest.raises(
        TypeError,
        match="^UptakeEquationSettings is restored from a list of its field values, not a dict$",
    ):
        restored.__setstate__({"cardiac_output_l_min": CARDIAC_OUTPUT_L_MIN})


def test_the_matrix_is_square_and_the_right_size() -> None:
    matrix = build_system_matrix(_settings())

    assert len(matrix) == STATE_SIZE
    assert all(len(row) == STATE_SIZE for row in matrix)


def test_the_inspired_row_is_the_circuit_balance() -> None:
    """dF_I/dt = (V_F/V_C)(F_D - F_I) - (V_A/V_C)(F_I - F_A)."""

    row = build_system_matrix(_settings())[INSPIRED_FRACTION]

    assert row[INSPIRED_FRACTION] == pytest.approx(
        -(FRESH_GAS_FLOW_L_S + ALVEOLAR_VENTILATION_L_S) / CIRCUIT_VOLUME_L
    )
    assert row[ALVEOLAR_FRACTION] == pytest.approx(ALVEOLAR_VENTILATION_L_S / CIRCUIT_VOLUME_L)
    assert row[UNIT_STATE] == pytest.approx(
        FRESH_GAS_FLOW_L_S * DELIVERED_FRACTION / CIRCUIT_VOLUME_L
    )
    assert row[VENOUS_FRACTION] == 0.0
    assert all(row[FIRST_TISSUE_FRACTION + offset] == 0.0 for offset in range(TISSUE_GROUP_COUNT))


def test_the_alveolar_row_is_the_alveolar_balance() -> None:
    """dF_A/dt = [ V_A(F_I - F_A) - Q*lambda_bg(F_A - F_v) ] / V_A."""

    row = build_system_matrix(_settings())[ALVEOLAR_FRACTION]
    pulmonary_blood_flow_l_s = CARDIAC_OUTPUT_L_S * BLOOD_GAS

    assert row[INSPIRED_FRACTION] == pytest.approx(ALVEOLAR_VENTILATION_L_S / ALVEOLAR_VOLUME_L)
    assert row[ALVEOLAR_FRACTION] == pytest.approx(
        -(ALVEOLAR_VENTILATION_L_S + pulmonary_blood_flow_l_s) / ALVEOLAR_VOLUME_L
    )
    assert row[VENOUS_FRACTION] == pytest.approx(pulmonary_blood_flow_l_s / ALVEOLAR_VOLUME_L)
    assert row[UNIT_STATE] == 0.0


def test_the_pulmonary_uptake_rate_is_formed() -> None:
    """The matrix forms the rate `docs/MODEL.md` specifies, which the operator split never formed.

    The document gives the pulmonary uptake rate as Q*lambda_bg(F_A - F_v)
    (`PL-Y5BV`). The alveolar row's own entries are that expression divided by
    the alveolar volume. Asserting the identity here turns "it is in there
    somewhere" into a check.
    """

    row = build_system_matrix(_settings())[ALVEOLAR_FRACTION]
    alveolar_fraction, venous_fraction = 0.031, 0.019

    uptake_contribution = (
        -(row[ALVEOLAR_FRACTION] * alveolar_fraction + row[VENOUS_FRACTION] * venous_fraction)
        - (ALVEOLAR_VENTILATION_L_S / ALVEOLAR_VOLUME_L) * alveolar_fraction
    )

    assert uptake_contribution * ALVEOLAR_VOLUME_L == pytest.approx(
        CARDIAC_OUTPUT_L_S * BLOOD_GAS * (alveolar_fraction - venous_fraction)
    )


def test_the_venous_row_is_the_venous_balance() -> None:
    """dF_v/dt = ( sum_i Q_i F_i - Q F_v ) / V_v."""

    row = build_system_matrix(_settings())[VENOUS_FRACTION]

    assert row[VENOUS_FRACTION] == pytest.approx(-CARDIAC_OUTPUT_L_S / VENOUS_VOLUME_L)

    for offset, (_, _, blood_flow_l_min, _) in enumerate(TISSUES):
        assert row[FIRST_TISSUE_FRACTION + offset] == pytest.approx(
            blood_flow_l_min / SECONDS_PER_MINUTE / VENOUS_VOLUME_L
        )

    assert row[INSPIRED_FRACTION] == 0.0
    assert row[ALVEOLAR_FRACTION] == 0.0
    assert row[UNIT_STATE] == 0.0


def test_each_tissue_row_is_that_group_s_balance() -> None:
    """dF_i/dt = Q_i / (V_i lambda_ib) * (F_A - F_i), driven by alveolar gas."""

    matrix = build_system_matrix(_settings())

    for offset, (_, volume_l, blood_flow_l_min, tissue_blood) in enumerate(TISSUES):
        state = FIRST_TISSUE_FRACTION + offset
        row = matrix[state]
        washin_rate_s = blood_flow_l_min / SECONDS_PER_MINUTE / (volume_l * tissue_blood)

        assert row[ALVEOLAR_FRACTION] == pytest.approx(washin_rate_s)
        assert row[state] == pytest.approx(-washin_rate_s)

        # Arterial blood is flow-limited, so a tissue is driven by the
        # alveolar fraction and by nothing else. It is not driven by the
        # circuit, by mixed venous blood or by another tissue group.
        assert row[INSPIRED_FRACTION] == 0.0
        assert row[VENOUS_FRACTION] == 0.0
        assert row[UNIT_STATE] == 0.0

        for other in range(TISSUE_GROUP_COUNT):
            if FIRST_TISSUE_FRACTION + other != state:
                assert row[FIRST_TISSUE_FRACTION + other] == 0.0


def test_the_delivery_and_exhaust_rows_are_the_conservation_equations() -> None:
    """dM_delivered/dt = V_F F_D, and dM_exhausted/dt = V_F F_I."""

    matrix = build_system_matrix(_settings())

    assert matrix[DELIVERED_AGENT_L][UNIT_STATE] == pytest.approx(
        FRESH_GAS_FLOW_L_S * DELIVERED_FRACTION
    )
    assert matrix[EXHAUSTED_AGENT_L][INSPIRED_FRACTION] == pytest.approx(FRESH_GAS_FLOW_L_S)

    # Neither accumulator feeds anything back: their columns are empty, so
    # they are outputs of the trajectory rather than part of it.
    for row in matrix:
        assert row[DELIVERED_AGENT_L] == 0.0
        assert row[EXHAUSTED_AGENT_L] == 0.0


def test_the_unit_state_never_changes() -> None:
    """The unit state's row is empty, so a step cannot perturb the forcing term."""

    assert build_system_matrix(_settings())[UNIT_STATE] == (0.0,) * STATE_SIZE


def test_the_matrix_is_metzler() -> None:
    """Every off-diagonal entry is a transfer rate, and every diagonal entry is a total loss.

    This is the precondition `matrix_exponential` requires in order to
    guarantee an entrywise nonnegative propagator, which keeps a compartment
    from being driven below zero. The test asserts it here, rather than
    leaving it to that module's own guard, so that a failure names the
    equation that broke it.
    """

    matrix = build_system_matrix(_settings())

    for row_index, row in enumerate(matrix):
        for column_index, value in enumerate(row):
            if row_index == column_index:
                assert value <= 0.0, f"diagonal {row_index} is {value}"
            else:
                assert value >= 0.0, f"off-diagonal ({row_index}, {column_index}) is {value}"


def test_the_compartments_neither_create_nor_lose_agent() -> None:
    """The mass-balance identity, in the derivative form the matrix states it.

    Summing each compartment's balance weighted by its capacity must leave
    exactly the two external terms: agent in at V_F*F_D and out at V_F*F_I.
    Every internal transfer has to cancel against its equal and opposite
    partner, so a rate written into one row and not into the other shows up
    here as a leak, whatever its value.
    """

    matrix = build_system_matrix(_settings())
    capacities = [
        CIRCUIT_VOLUME_L,
        ALVEOLAR_VOLUME_L,
        VENOUS_VOLUME_L * BLOOD_GAS,
        *(volume_l * tissue_blood * BLOOD_GAS for _, volume_l, _, tissue_blood in TISSUES),
    ]

    for column in range(STATE_SIZE):
        stored_rate = sum(
            capacity * matrix[state][column] for state, capacity in enumerate(capacities)
        )
        external_rate = matrix[DELIVERED_AGENT_L][column] - matrix[EXHAUSTED_AGENT_L][column]

        assert stored_rate == pytest.approx(external_rate, abs=1e-15), (
            f"agent is created or lost through state {column}"
        )


@pytest.mark.parametrize("flow", SUPPORTED_FLOWS, ids=FLOW_IDS)
def test_a_zero_flow_is_a_zero_rate_and_needs_no_branch(flow: Flow) -> None:
    """`docs/MODEL.md`'s three zero-flow cases, expressed as arithmetic.

    Each case says that a transfer stops. Under the operator split, each case
    needed an early return, because its closed form divided by the flow. Here
    the flow is a factor of the matrix entry, and zero is simply zero.

    Every tissue flow is cardiac output times that group's perfusion fraction,
    so a stopped heart stops all three tissue flows. `_settings_with_flow`
    scales them, because zeroing cardiac output without the tissue flows is
    the inconsistency that the settings refuse.
    """

    zeroed = flow.field
    matrix = build_system_matrix(_settings_with_flow(zeroed, flow.flow_type(0.0)))

    assert all(all(value == value for value in row) for row in matrix)

    if zeroed == "alveolar_ventilation_l_min":
        assert matrix[INSPIRED_FRACTION][ALVEOLAR_FRACTION] == 0.0
        assert matrix[ALVEOLAR_FRACTION][INSPIRED_FRACTION] == 0.0
        # docs/MODEL.md says the circuit equation reduces here to the v0.0.2
        # circuit equation: fresh-gas wash-in alone.
        assert matrix[INSPIRED_FRACTION][INSPIRED_FRACTION] == pytest.approx(
            -FRESH_GAS_FLOW_L_S / CIRCUIT_VOLUME_L
        )

    if zeroed == "cardiac_output_l_min":
        assert matrix[ALVEOLAR_FRACTION][VENOUS_FRACTION] == 0.0
        assert matrix[VENOUS_FRACTION][VENOUS_FRACTION] == 0.0

    if zeroed == "fresh_gas_flow_l_min":
        assert matrix[DELIVERED_AGENT_L][UNIT_STATE] == 0.0
        assert matrix[EXHAUSTED_AGENT_L][INSPIRED_FRACTION] == 0.0


def test_a_zero_tissue_flow_leaves_that_group_alone() -> None:
    """`Q_i = 0` implies `dM_i/dt = 0`, and does not divide by anything."""

    unperfused_fat = tuple(
        TissueGroupEquationSettings(
            name=name,
            volume_l=volume_l,
            blood_flow_l_min=0.0 if name == "fat" else blood_flow_l_min,
            tissue_blood_partition_coefficient=tissue_blood,
        )
        for name, volume_l, blood_flow_l_min, tissue_blood in TISSUES
    )
    # Cardiac output falls with the flow that stopped, because the venous
    # balance returns exactly what the tissues receive.
    matrix = build_system_matrix(
        _settings(
            tissues=unperfused_fat,
            cardiac_output_l_min=CardiacOutput(
                sum(tissue.blood_flow_l_min for tissue in unperfused_fat)
            ),
        )
    )
    fat = FIRST_TISSUE_FRACTION + 2

    assert matrix[fat] == (0.0,) * STATE_SIZE
    assert matrix[VENOUS_FRACTION][fat] == 0.0
    assert matrix[FIRST_TISSUE_FRACTION][ALVEOLAR_FRACTION] > 0.0


@pytest.mark.parametrize(
    ("field", "value", "checked_type", "message"),
    [
        (
            "circuit_volume_l",
            0.0,
            CompartmentVolume,
            "^circuit_volume_l of 0.0 is outside the numerical envelope of 0.01 to 10000 L,",
        ),
        (
            "alveolar_volume_l",
            -1.0,
            CompartmentVolume,
            "^alveolar_volume_l of -1.0 is outside the numerical envelope of 0.01 to 10000 L,",
        ),
        (
            "venous_volume_l",
            float("inf"),
            CompartmentVolume,
            "^venous_volume_l of inf is outside the numerical envelope of 0.01 to 10000 L,",
        ),
        (
            "blood_gas_partition_coefficient",
            0.0,
            PartitionCoefficient,
            "^blood_gas_partition_coefficient of 0.0 is outside the numerical envelope of "
            "0.001 to 10000,",
        ),
        # A case with a dial past 100% was here until `PL-4R3W`. Such a dial
        # can no longer be built as the `Percent` that the record takes, so it
        # never reaches the record. `test_concentration.py` pins that refusal
        # on the constructor.
    ],
)
def test_rejects_a_parameter_set_that_could_not_describe_a_patient(
    field: str,
    value: float,
    checked_type: type[CompartmentVolume] | type[PartitionCoefficient],
    message: str,
) -> None:
    """A volume or coefficient outside the envelope is refused, and so is a bare float.

    Since `PL-QX2G` the record takes checked types, so the value is refused when its type is
    built. The record refuses the same value handed in as a bare float, naming the type.
    """

    with pytest.raises(SimulationConfigurationError, match=message):
        _settings(**{field: checked_type(value, name=field)})

    with pytest.raises(
        TypeError,
        match=f"^{field} of {value!r} was not built as {checked_type.__name__}, it is float",
    ):
        _settings(**{field: value})


def test_rejects_tissue_flows_that_do_not_sum_to_cardiac_output() -> None:
    """The venous pool returns exactly what the tissues receive.

    A mismatch would fill that pool at one rate and drain it at another. So
    the model would create or destroy agent at a steady rate for as long as
    the mismatch lasted. It would do so silently, because every fraction would
    stay smooth and in range. `patient.py` states the same requirement as
    perfusion fractions that sum to one. This test checks that the equations
    enforce it on the object they are actually built from.

    The mismatched output is inside the supported range, so the mismatch is
    the only thing refused. An output of 1.5 times the reference output is
    past the range, so it would now be refused for that reason first
    (`PL-HSFV`).
    """

    with pytest.raises(
        SimulationConfigurationError, match="the venous balance returns what the tissues receive"
    ):
        _settings(cardiac_output_l_min=CardiacOutput(CARDIAC_OUTPUT_L_MIN * 1.2))


def test_a_tissue_flow_mismatch_is_stated_in_litres_per_minute() -> None:
    """The refusal names both flows in the unit every dial and readout shows, as they were set.

    The comparison is made in litres per second, the unit the balances are
    written in. The message used to name the flows in that unit too, 0.13 L/s
    against 0.156 L/s here, while every setting, readout and other refusal
    names a flow in L/min. The message reaches a reader through the
    stopped-run banner, because the record is refused at the next step and at
    Reset (`PL-M4M0`). So the message named values that the screen never
    shows. The expected figures are literal rather than summed the way the
    code sums them. A sum of the stored flows carries the float's noise in its
    last digits, 0.7000000000000001 for the three flows below, and a banner
    must not claim a precision that no dial set.
    """

    with pytest.raises(SimulationConfigurationError) as raised:
        _settings(cardiac_output_l_min=CardiacOutput(CARDIAC_OUTPUT_L_MIN * 1.2))

    message = str(raised.value)

    assert "perfused at 7.8 L/min in total but cardiac output is 9.36 L/min" in message
    assert "L/s" not in message

    with pytest.raises(SimulationConfigurationError) as raised:
        _settings(
            cardiac_output_l_min=CardiacOutput(1.0),
            tissues=tuple(
                TissueGroupEquationSettings(
                    name=name,
                    volume_l=volume_l,
                    blood_flow_l_min=blood_flow_l_min,
                    tissue_blood_partition_coefficient=tissue_blood,
                )
                for (name, volume_l, _, tissue_blood), blood_flow_l_min in zip(
                    TISSUES, (0.1, 0.2, 0.4), strict=True
                )
            ),
        )

    assert "perfused at 0.7 L/min in total but cardiac output is 1.0 L/min" in str(raised.value)


def test_rejects_a_tissue_group_count_the_model_does_not_have() -> None:
    """The venous balance sums over exactly these groups, so the count is fixed.

    A fourth group added to the data files without the equations knowing
    about it would be perfused by the venous row and return to nothing.
    """

    one_group = (
        TissueGroupEquationSettings(
            name="vessel_rich",
            volume_l=CompartmentVolume(6.0),
            blood_flow_l_min=CARDIAC_OUTPUT_L_MIN,
            tissue_blood_partition_coefficient=PartitionCoefficient(1.7),
        ),
    )

    with pytest.raises(
        SimulationConfigurationError,
        match=f"^the model has {TISSUE_GROUP_COUNT} tissue groups but 1 were given$",
    ):
        _settings(tissues=one_group)


@pytest.mark.parametrize(
    ("field", "value", "error", "message"),
    [
        (
            "volume_l",
            0.0,
            TypeError,
            "^muscle volume_l of 0.0 was not built as CompartmentVolume, it is float",
        ),
        (
            "blood_flow_l_min",
            -0.1,
            SimulationConfigurationError,
            "^muscle blood_flow_l_min must be nonnegative and finite" + REFUSAL_REASON,
        ),
        (
            "tissue_blood_partition_coefficient",
            0.0,
            TypeError,
            "^muscle tissue_blood_partition_coefficient of 0.0 was not built as "
            "PartitionCoefficient, it is float",
        ),
    ],
)
def test_rejects_a_tissue_group_that_could_not_describe_a_tissue(
    field: str, value: float, error: type[Exception], message: str
) -> None:
    """A tissue group refuses a value that could not describe a tissue.

    Since `PL-QX2G` the volume and the coefficient are checked types, so the record refuses
    either one passed as a bare float. `CompartmentVolume(0.0)` and `PartitionCoefficient(0.0)`
    are refused when they are built, which the test below checks.
    """

    fields: dict[str, object] = {
        "name": "muscle",
        "volume_l": CompartmentVolume(33.0),
        "blood_flow_l_min": 0.023,
        "tissue_blood_partition_coefficient": PartitionCoefficient(2.9),
    }
    fields[field] = value

    with pytest.raises(error, match=message):
        TissueGroupEquationSettings(**fields)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("checked_type", "name", "message"),
    [
        (
            CompartmentVolume,
            "muscle volume_l",
            "^muscle volume_l of 0.0 is outside the numerical envelope of 0.01 to 10000 L,",
        ),
        (
            PartitionCoefficient,
            "muscle tissue_blood_partition_coefficient",
            "^muscle tissue_blood_partition_coefficient of 0.0 is outside the numerical "
            "envelope of 0.001 to 10000,",
        ),
    ],
)
def test_a_tissue_volume_or_coefficient_of_zero_cannot_be_built(
    checked_type: type[CompartmentVolume] | type[PartitionCoefficient], name: str, message: str
) -> None:
    """A zero volume or coefficient never reaches a tissue group's record (`PL-QX2G`)."""

    with pytest.raises(SimulationConfigurationError, match=message):
        checked_type(0.0, name=name)


def test_equal_settings_compare_equal_so_the_propagator_cache_is_keyed_by_value() -> None:
    """`AgentUptakeSystem` reuses a propagator only while this stays true.

    The cache checks whether the settings it was built for are the settings
    now in force. If two structurally identical settings compared unequal, the
    propagator would be rebuilt every step, which is slow but safe. If two
    *different* settings compared equal, the run would keep propagating with
    the wrong matrix, which is not safe. The test asserts both directions.
    """

    assert _settings() == _settings()
    assert _settings() != _settings(delivered_concentration_percent=Percent(3.0))

    fatter = tuple(
        TissueGroupEquationSettings(
            name=name,
            volume_l=CompartmentVolume(volume_l * (2.0 if name == "fat" else 1.0)),
            blood_flow_l_min=blood_flow_l_min,
            tissue_blood_partition_coefficient=tissue_blood,
        )
        for name, volume_l, blood_flow_l_min, tissue_blood in TISSUES
    )

    assert _settings() != _settings(tissues=fatter)


def test_the_system_matrix_does_not_depend_on_a_tissue_group_s_name() -> None:
    """This lets the propagator cache key leave out a tissue group's name (`PL-R460`).

    The key that `AgentUptakeSystem` compares at each step carries one float
    per settings field. `TissueGroupEquationSettings.name` is the one field
    with no entry, because a group's rows are placed by its position in the
    tuple, not by its name. If the matrix ever depended on the name, two runs
    that differ only in a group's name would share a propagator, and one of
    them would be wrong.
    """

    renamed = tuple(
        TissueGroupEquationSettings(
            name=f"renamed-{index}",
            volume_l=tissue.volume_l,
            blood_flow_l_min=tissue.blood_flow_l_min,
            tissue_blood_partition_coefficient=tissue.tissue_blood_partition_coefficient,
        )
        for index, tissue in enumerate(_settings().tissues)
    )

    assert build_system_matrix(_settings(tissues=renamed)) == build_system_matrix(_settings())


def test_equal_settings_form_the_same_propagator_bit_for_bit_whatever_built_them() -> None:
    """A record stores plain floats and a tuple, so equal records make one cache key (`PL-5BD7`).

    Both propagator caches key on the record by value. A `numpy.float64`
    volume compares and hashes equal to the plain `float`. But CPython's `sum`
    adds values of exact type `float` with compensation, and adds a subclass
    without it. So before the record stored its fields as exact floats, the
    propagator built from a subclass differed in 39 of 81 entries at 7 s. A
    list of tissue groups was accepted, and it could not be hashed. The
    expected propagator here is the one built from plain floats and a tuple,
    which is what every record built by `AgentUptakeSystem.equation_settings`
    stores. Since `PL-QX2G` a volume or coefficient reaches the record only as
    its checked type, so a `numpy.float64` is built into that type first.
    """

    plain = _settings()
    built_otherwise = _settings(
        circuit_volume_l=CompartmentVolume(numpy.float64(CIRCUIT_VOLUME_L)),
        alveolar_volume_l=CompartmentVolume(numpy.float64(ALVEOLAR_VOLUME_L)),
        venous_volume_l=CompartmentVolume(numpy.float64(VENOUS_VOLUME_L)),
        blood_gas_partition_coefficient=PartitionCoefficient(numpy.float64(BLOOD_GAS)),
        tissues=[
            TissueGroupEquationSettings(
                name=tissue.name,
                volume_l=CompartmentVolume(numpy.float64(tissue.volume_l)),
                blood_flow_l_min=numpy.float64(tissue.blood_flow_l_min),
                tissue_blood_partition_coefficient=PartitionCoefficient(
                    numpy.float64(tissue.tissue_blood_partition_coefficient)
                ),
            )
            for tissue in plain.tissues
        ],
    )

    assert type(built_otherwise.tissues) is tuple
    assert type(built_otherwise.circuit_volume_l) is CompartmentVolume
    assert all(type(tissue.volume_l) is CompartmentVolume for tissue in built_otherwise.tissues)
    assert all(type(tissue.blood_flow_l_min) is float for tissue in built_otherwise.tissues)
    assert hash(built_otherwise) == hash(plain)

    for interval_s in (0.84, 7.0, 600.0):
        assert matrix_exponential(build_system_matrix(built_otherwise), interval_s) == (
            matrix_exponential(build_system_matrix(plain), interval_s)
        )


def _empty_state_with(position: int, value: float) -> tuple[float, ...]:
    """An empty canonical state with `value` at `position`."""

    state = [0.0] * STATE_SIZE
    state[UNIT_STATE] = 1.0
    state[position] = value

    return tuple(state)


@pytest.mark.parametrize(
    "position",
    [
        INSPIRED_FRACTION,
        ALVEOLAR_FRACTION,
        VENOUS_FRACTION,
        *(FIRST_TISSUE_FRACTION + offset for offset in range(TISSUE_GROUP_COUNT)),
    ],
)
@pytest.mark.parametrize("value", [-0.3, nextafter(0.0, -1.0), nextafter(1.0, 2.0), 1.7])
def test_require_canonical_state_refuses_a_fraction_outside_zero_to_one(
    position: int, value: float
) -> None:
    """A value outside 0 to 1 is refused at each of the six fraction positions (`PL-0WFJ`).

    The live system's compartments refuse these values, so a `RunDefinition` that opened from
    one would draw a state that the system can never hold. The values include the nearest
    floats outside each bound.
    """

    with pytest.raises(SimulationConfigurationError) as raised:
        require_canonical_state(_empty_state_with(position, value))

    assert str(raised.value).startswith(f"state[{position}] (")
    assert "is outside 0 to 1" in str(raised.value)


@pytest.mark.parametrize("position", [DELIVERED_AGENT_L, EXHAUSTED_AGENT_L])
def test_require_canonical_state_refuses_a_negative_amount_of_agent(position: int) -> None:
    """A cumulative amount of agent below zero describes a run that never happened."""

    with pytest.raises(SimulationConfigurationError) as raised:
        require_canonical_state(_empty_state_with(position, -1e-12))

    assert str(raised.value).startswith(f"state[{position}] (")
    assert "must be nonnegative" in str(raised.value)


def test_require_canonical_state_accepts_each_fraction_at_both_bounds() -> None:
    """Zero and one are physical fractions, so the range check must not refuse them."""

    for position in range(FIRST_TISSUE_FRACTION + TISSUE_GROUP_COUNT):
        require_canonical_state(_empty_state_with(position, 0.0))
        require_canonical_state(_empty_state_with(position, 1.0))


@pytest.mark.parametrize("position", [DELIVERED_AGENT_L, EXHAUSTED_AGENT_L])
def test_require_canonical_state_refuses_more_agent_than_a_case_can_move(position: int) -> None:
    """A total above what a whole case can move at the fastest fresh gas flow is refused.

    This was found at review. Set to the largest float, each total once passed the check, and
    `state_at(600.0)` returned `inf` for each. The bound itself is accepted, and the next float
    above it is not.
    """

    assert MAXIMUM_CUMULATIVE_AGENT_L == 14_400.0

    require_canonical_state(_empty_state_with(position, MAXIMUM_CUMULATIVE_AGENT_L))

    with pytest.raises(SimulationConfigurationError) as raised:
        require_canonical_state(
            _empty_state_with(position, nextafter(MAXIMUM_CUMULATIVE_AGENT_L, inf))
        )

    role = {DELIVERED_AGENT_L: "delivered", EXHAUSTED_AGENT_L: "exhausted"}[position]
    assert str(raised.value) == (
        f"state[{position}] ({role} agent in L) of 14400.000000000002 L is more than the "
        "14400.0 L that a case can deliver or exhaust at the fastest supported fresh gas "
        "flow over the supported run length"
    )
