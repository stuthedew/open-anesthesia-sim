"""Check the transcription entry by entry against the equations it transcribes.

`build_system_matrix` is the whole model, so the risk it carries is a
mistyped index or a sign: a matrix that is wrong in one entry still produces
a smooth, plausible trajectory, and the reference gates would catch it only
as a number that disagrees with the oracle without saying where.

So every expected value below is written out from `docs/MODEL.md`'s
"Governing equations" independently of the module under test, at settings
chosen so that no two rates share a value and a transposed index cannot pass.
The structural properties the propagator depends on - that the matrix is
Metzler, that the unit state is constant, that the compartments conserve
agent - are asserted separately, because those hold for every parameter set
rather than for these numbers.
"""

import pytest

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    DELIVERED_AGENT_L,
    EXHAUSTED_AGENT_L,
    FIRST_TISSUE_FRACTION,
    INSPIRED_FRACTION,
    STATE_SIZE,
    TISSUE_GROUP_COUNT,
    UNIT_STATE,
    VENOUS_FRACTION,
    TissueGroupEquationSettings,
    UptakeEquationSettings,
    build_system_matrix,
)

# Deliberately unlike each other and unlike the reference adult's: every
# volume, flow and coefficient below is distinct, so an entry written into
# the wrong row or column lands on a value nothing else has.
CIRCUIT_VOLUME_L = 6.0
ALVEOLAR_VOLUME_L = 2.5
VENOUS_VOLUME_L = 3.5
FRESH_GAS_FLOW_L_S = 0.07
ALVEOLAR_VENTILATION_L_S = 0.11
CARDIAC_OUTPUT_L_S = 0.13
BLOOD_GAS = 0.65
DELIVERED_FRACTION = 0.02

TISSUES = (
    ("vessel_rich", 6.0, 0.0975, 1.7),
    ("muscle", 33.0, 0.0247, 2.9),
    ("fat", 14.5, 0.0078, 51.0),
)
"""(name, volume_l, blood_flow_l_s, tissue:blood coefficient) for each group.

The three flows sum to `CARDIAC_OUTPUT_L_S`, as the venous balance requires
and `UptakeEquationSettings` now checks. They are otherwise unlike each other
and unlike every other constant here, so a transposed index cannot pass.
"""


def _settings(**overrides: object) -> UptakeEquationSettings:
    fields: dict[str, object] = {
        "circuit_volume_l": CIRCUIT_VOLUME_L,
        "alveolar_volume_l": ALVEOLAR_VOLUME_L,
        "venous_volume_l": VENOUS_VOLUME_L,
        "fresh_gas_flow_l_s": FRESH_GAS_FLOW_L_S,
        "alveolar_ventilation_l_s": ALVEOLAR_VENTILATION_L_S,
        "cardiac_output_l_s": CARDIAC_OUTPUT_L_S,
        "blood_gas_partition_coefficient": BLOOD_GAS,
        "delivered_concentration_fraction": DELIVERED_FRACTION,
        "tissues": tuple(
            TissueGroupEquationSettings(
                name=name,
                volume_l=volume_l,
                blood_flow_l_s=blood_flow_l_s,
                tissue_blood_partition_coefficient=tissue_blood,
            )
            for name, volume_l, blood_flow_l_s, tissue_blood in TISSUES
        ),
    }
    fields.update(overrides)

    return UptakeEquationSettings(**fields)  # type: ignore[arg-type]


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
    """The rate `docs/MODEL.md` specifies, which the operator split never formed.

    `PL-Y5BV`: the document gives the pulmonary uptake rate as
    Q*lambda_bg(F_A - F_v), and the alveolar row's own entries are that
    expression divided by the alveolar volume. Asserting the identity here is
    what turns "it is in there somewhere" into a check.
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

    for offset, (_, _, blood_flow_l_s, _) in enumerate(TISSUES):
        assert row[FIRST_TISSUE_FRACTION + offset] == pytest.approx(
            blood_flow_l_s / VENOUS_VOLUME_L
        )

    assert row[INSPIRED_FRACTION] == 0.0
    assert row[ALVEOLAR_FRACTION] == 0.0
    assert row[UNIT_STATE] == 0.0


def test_each_tissue_row_is_that_group_s_balance() -> None:
    """dF_i/dt = Q_i / (V_i lambda_ib) * (F_A - F_i), driven by alveolar gas."""

    matrix = build_system_matrix(_settings())

    for offset, (_, volume_l, blood_flow_l_s, tissue_blood) in enumerate(TISSUES):
        state = FIRST_TISSUE_FRACTION + offset
        row = matrix[state]
        washin_rate_s = blood_flow_l_s / (volume_l * tissue_blood)

        assert row[ALVEOLAR_FRACTION] == pytest.approx(washin_rate_s)
        assert row[state] == pytest.approx(-washin_rate_s)

        # Arterial blood is flow-limited, so a tissue is driven by the
        # alveolar fraction and by nothing else - not by the circuit, not by
        # mixed venous blood, and not by another tissue group.
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
    """Its row is empty, so the forcing term cannot be perturbed by a step."""

    assert build_system_matrix(_settings())[UNIT_STATE] == (0.0,) * STATE_SIZE


def test_the_matrix_is_metzler() -> None:
    """Every off-diagonal entry is a transfer rate, every diagonal a total loss.

    This is the precondition `matrix_exponential` requires in order to
    guarantee an entrywise nonnegative propagator, which is what keeps a
    compartment from being driven below zero. It is asserted here rather than
    left to that module's own guard so that a failure names the equation that
    broke it.
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


@pytest.mark.parametrize(
    "zeroed", ["fresh_gas_flow_l_s", "alveolar_ventilation_l_s", "cardiac_output_l_s"]
)
def test_a_zero_flow_is_a_zero_rate_and_needs_no_branch(zeroed: str) -> None:
    """`docs/MODEL.md`'s three zero-flow cases, expressed as arithmetic.

    Each says a transfer stops. Under the operator split each needed an early
    return, because its closed form divided by the flow; here the flow is a
    factor of the matrix entry and zero is simply zero.
    """

    overrides: dict[str, object] = {zeroed: 0.0}

    if zeroed == "cardiac_output_l_s":
        # Every tissue flow is cardiac output times that group's perfusion
        # fraction, so a stopped heart stops all three with it. Zeroing the
        # one without the others is the inconsistency the settings refuse.
        overrides["tissues"] = tuple(
            TissueGroupEquationSettings(
                name=name,
                volume_l=volume_l,
                blood_flow_l_s=0.0,
                tissue_blood_partition_coefficient=tissue_blood,
            )
            for name, volume_l, _, tissue_blood in TISSUES
        )

    matrix = build_system_matrix(_settings(**overrides))

    assert all(all(value == value for value in row) for row in matrix)

    if zeroed == "alveolar_ventilation_l_s":
        assert matrix[INSPIRED_FRACTION][ALVEOLAR_FRACTION] == 0.0
        assert matrix[ALVEOLAR_FRACTION][INSPIRED_FRACTION] == 0.0
        # The v0.0.2 circuit equation, which docs/MODEL.md says this reduces
        # to: fresh-gas wash-in alone.
        assert matrix[INSPIRED_FRACTION][INSPIRED_FRACTION] == pytest.approx(
            -FRESH_GAS_FLOW_L_S / CIRCUIT_VOLUME_L
        )

    if zeroed == "cardiac_output_l_s":
        assert matrix[ALVEOLAR_FRACTION][VENOUS_FRACTION] == 0.0
        assert matrix[VENOUS_FRACTION][VENOUS_FRACTION] == 0.0

    if zeroed == "fresh_gas_flow_l_s":
        assert matrix[DELIVERED_AGENT_L][UNIT_STATE] == 0.0
        assert matrix[EXHAUSTED_AGENT_L][INSPIRED_FRACTION] == 0.0


def test_a_zero_tissue_flow_leaves_that_group_alone() -> None:
    """`Q_i = 0` implies `dM_i/dt = 0`, and does not divide by anything."""

    unperfused_fat = tuple(
        TissueGroupEquationSettings(
            name=name,
            volume_l=volume_l,
            blood_flow_l_s=0.0 if name == "fat" else blood_flow_l_s,
            tissue_blood_partition_coefficient=tissue_blood,
        )
        for name, volume_l, blood_flow_l_s, tissue_blood in TISSUES
    )
    # Cardiac output falls with the flow that stopped, because the venous
    # balance returns exactly what the tissues receive.
    matrix = build_system_matrix(
        _settings(
            tissues=unperfused_fat,
            cardiac_output_l_s=sum(tissue.blood_flow_l_s for tissue in unperfused_fat),
        )
    )
    fat = FIRST_TISSUE_FRACTION + 2

    assert matrix[fat] == (0.0,) * STATE_SIZE
    assert matrix[VENOUS_FRACTION][fat] == 0.0
    assert matrix[FIRST_TISSUE_FRACTION][ALVEOLAR_FRACTION] > 0.0


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("circuit_volume_l", 0.0, "^circuit_volume_l must be positive and finite$"),
        ("alveolar_volume_l", -1.0, "^alveolar_volume_l must be positive and finite$"),
        ("venous_volume_l", float("inf"), "^venous_volume_l must be positive and finite$"),
        ("fresh_gas_flow_l_s", -0.1, "^fresh_gas_flow_l_s must be nonnegative and finite$"),
        (
            "alveolar_ventilation_l_s",
            float("nan"),
            "^alveolar_ventilation_l_s must be nonnegative and finite$",
        ),
        ("cardiac_output_l_s", -1.0, "^cardiac_output_l_s must be nonnegative and finite$"),
        (
            "blood_gas_partition_coefficient",
            0.0,
            "^blood_gas_partition_coefficient must be positive and finite$",
        ),
        (
            "delivered_concentration_fraction",
            1.5,
            "^delivered_concentration_fraction must be between 0 and 1$",
        ),
    ],
)
def test_rejects_a_parameter_set_that_could_not_describe_a_patient(
    field: str, value: float, message: str
) -> None:
    with pytest.raises(SimulationConfigurationError, match=message):
        _settings(**{field: value})


def test_rejects_tissue_flows_that_do_not_sum_to_cardiac_output() -> None:
    """The venous pool returns exactly what the tissues receive.

    A mismatch would fill that pool at one rate and drain it at another, so
    the model would create or destroy agent at a steady rate for as long as
    it stood - and it would do so silently, since every fraction would stay
    smooth and in range. `patient.py` states the same requirement as
    perfusion fractions summing to one; this is the equations checking the
    object they are actually built from.
    """

    with pytest.raises(
        SimulationConfigurationError, match="the venous balance returns what the tissues receive"
    ):
        _settings(cardiac_output_l_s=CARDIAC_OUTPUT_L_S * 1.5)


def test_rejects_a_tissue_group_count_the_model_does_not_have() -> None:
    """The venous balance sums over exactly these groups, so the count is fixed.

    A fourth group added to the data files without the equations knowing
    about it would be perfused by the venous row and return to nothing.
    """

    one_group = (
        TissueGroupEquationSettings(
            name="vessel_rich",
            volume_l=6.0,
            blood_flow_l_s=CARDIAC_OUTPUT_L_S,
            tissue_blood_partition_coefficient=1.7,
        ),
    )

    with pytest.raises(
        SimulationConfigurationError,
        match=f"^the model has {TISSUE_GROUP_COUNT} tissue groups but 1 were given$",
    ):
        _settings(tissues=one_group)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("volume_l", 0.0, "^muscle volume_l must be positive and finite$"),
        ("blood_flow_l_s", -0.1, "^muscle blood_flow_l_s must be nonnegative and finite$"),
        (
            "tissue_blood_partition_coefficient",
            0.0,
            "^muscle tissue_blood_partition_coefficient must be positive and finite$",
        ),
    ],
)
def test_rejects_a_tissue_group_that_could_not_describe_a_tissue(
    field: str, value: float, message: str
) -> None:
    fields: dict[str, object] = {
        "name": "muscle",
        "volume_l": 33.0,
        "blood_flow_l_s": 0.023,
        "tissue_blood_partition_coefficient": 2.9,
    }
    fields[field] = value

    with pytest.raises(SimulationConfigurationError, match=message):
        TissueGroupEquationSettings(**fields)  # type: ignore[arg-type]


def test_equal_settings_compare_equal_so_the_propagator_cache_is_keyed_by_value() -> None:
    """`AgentUptakeSystem` reuses a propagator only while this stays true.

    The cache asks whether the settings it built for are the settings now in
    force. If two structurally identical settings compared unequal the
    propagator would be rebuilt every step, which is slow but safe; if two
    *different* ones compared equal the run would keep propagating with the
    wrong matrix, which is not. Both directions are asserted.
    """

    assert _settings() == _settings()
    assert _settings() != _settings(delivered_concentration_fraction=0.03)

    fatter = tuple(
        TissueGroupEquationSettings(
            name=name,
            volume_l=volume_l * (2.0 if name == "fat" else 1.0),
            blood_flow_l_s=blood_flow_l_s,
            tissue_blood_partition_coefficient=tissue_blood,
        )
        for name, volume_l, blood_flow_l_s, tissue_blood in TISSUES
    )

    assert _settings() != _settings(tissues=fatter)
