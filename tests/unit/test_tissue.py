import copy
import pickle
from dataclasses import astuple, replace
from math import exp, inf, nan

import pytest

from anesthesia_sim.core.concentration import Fraction
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.tissue import TissueGroup


def _build_tissue(*, blood_flow_l_min: float = 1.0) -> TissueGroup:
    return TissueGroup(
        name="test",
        volume_l=2.0,
        perfusion_fraction=0.2,
        blood_gas_partition_coefficient=0.5,
        tissue_gas_partition_coefficient=2.0,
        blood_flow_l_min=blood_flow_l_min,
    )


def test_rejects_empty_tissue_name() -> None:
    with pytest.raises(SimulationConfigurationError, match="^name must be a nonempty string$"):
        TissueGroup(
            name=" ",
            volume_l=2.0,
            perfusion_fraction=0.2,
            blood_gas_partition_coefficient=0.5,
            tissue_gas_partition_coefficient=2.0,
        )


def test_rejects_perfusion_fraction_above_one() -> None:
    with pytest.raises(
        SimulationConfigurationError, match="^perfusion_fraction must not exceed 1$"
    ):
        TissueGroup(
            name="test",
            volume_l=2.0,
            perfusion_fraction=1.1,
            blood_gas_partition_coefficient=0.5,
            tissue_gas_partition_coefficient=2.0,
        )


def test_rejects_agent_amount_above_tissue_capacity() -> None:
    with pytest.raises(
        SimulationConfigurationError,
        match="^agent_amount_l exceeds the tissue capacity for a concentration fraction of 1$",
    ):
        TissueGroup(
            name="test",
            volume_l=2.0,
            perfusion_fraction=0.2,
            blood_gas_partition_coefficient=0.5,
            tissue_gas_partition_coefficient=2.0,
            agent_amount_l=4.1,
        )


def test_an_agent_amount_past_capacity_is_refused_at_the_write() -> None:
    """An assignment straight onto the amount meets the constructor's refusal, and writes nothing.

    The tissue's counterpart of `tests/unit/test_alveolar.py`'s test of the
    same name: until `PL-544D` `TissueGroup` guarded no write at all, so an
    amount past `capacity_l` was stored and its quotient refused only when the
    snapshot built the `Fraction`. The write is refused in the constructor's
    own words and leaves the field holding what it held; `dataclasses.replace`
    and a copy write through the same `__setattr__`; an amount at the capacity
    itself is written.
    """

    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.4))
    held = tissue.agent_amount_l
    past_capacity = tissue.capacity_l * 1.0000001
    refused = "^agent_amount_l exceeds the tissue capacity for a concentration fraction of 1$"

    with pytest.raises(SimulationConfigurationError, match=refused):
        tissue.agent_amount_l = past_capacity

    assert tissue.agent_amount_l == held

    for not_an_amount in (-0.1, float("inf"), float("nan")):
        with pytest.raises(SimulationConfigurationError, match="agent_amount_l"):
            tissue.agent_amount_l = not_an_amount

        assert tissue.agent_amount_l == held

    with pytest.raises(SimulationConfigurationError, match=refused):
        replace(tissue, agent_amount_l=past_capacity)

    smuggled = copy.copy(tissue)
    object.__setattr__(smuggled, "agent_amount_l", past_capacity)

    with pytest.raises(SimulationConfigurationError, match=refused):
        copy.copy(smuggled)

    tissue.agent_amount_l = tissue.capacity_l

    assert tissue.partial_pressure_fraction == 1.0


TOO_SMALL_FOR_THE_AGENT_HELD = (
    r"^{field} of 0.5 is too small for the 2.0 L of agent the test tissue holds: it would "
    r"leave room for 1.0 L at a partial pressure of one atmosphere \(docs/MODEL.md, "
    r'"Tissue compartments"\)$'
)


@pytest.mark.parametrize(
    ("field", "value", "error", "message"),
    [
        pytest.param(
            "name",
            "",
            SimulationConfigurationError,
            "^name must be a nonempty string$",
            id="empty-name",
        ),
        pytest.param(
            "name",
            "  ",
            SimulationConfigurationError,
            "^name must be a nonempty string$",
            id="blank-name",
        ),
        pytest.param("name", 5, TypeError, "^name of 5 has type int, not str$", id="int-name"),
        pytest.param(
            "volume_l",
            0.0,
            SimulationConfigurationError,
            "^volume_l must be positive and finite$",
            id="zero-volume",
        ),
        pytest.param(
            "volume_l",
            -1.0,
            SimulationConfigurationError,
            "^volume_l must be positive and finite$",
            id="negative-volume",
        ),
        pytest.param(
            "volume_l",
            nan,
            SimulationConfigurationError,
            "^volume_l must be positive and finite$",
            id="nan-volume",
        ),
        pytest.param("volume_l", "2", TypeError, "^volume_l of '2' has type str", id="str-volume"),
        pytest.param(
            "volume_l",
            0.5,
            SimulationConfigurationError,
            TOO_SMALL_FOR_THE_AGENT_HELD.format(field="volume_l"),
            id="volume-under-the-agent-held",
        ),
        pytest.param(
            "perfusion_fraction",
            0.0,
            SimulationConfigurationError,
            "^perfusion_fraction must be positive and finite$",
            id="zero-perfusion-fraction",
        ),
        pytest.param(
            "perfusion_fraction",
            7.0,
            SimulationConfigurationError,
            "^perfusion_fraction must not exceed 1$",
            id="perfusion-fraction-above-one",
        ),
        pytest.param(
            "perfusion_fraction",
            nan,
            SimulationConfigurationError,
            "^perfusion_fraction must be positive and finite$",
            id="nan-perfusion-fraction",
        ),
        pytest.param(
            "blood_gas_partition_coefficient",
            0.0,
            SimulationConfigurationError,
            "^blood_gas_partition_coefficient must be positive and finite$",
            id="zero-blood-gas-coefficient",
        ),
        pytest.param(
            "blood_gas_partition_coefficient",
            inf,
            SimulationConfigurationError,
            "^blood_gas_partition_coefficient must be positive and finite$",
            id="infinite-blood-gas-coefficient",
        ),
        pytest.param(
            "tissue_gas_partition_coefficient",
            0.0,
            SimulationConfigurationError,
            "^tissue_gas_partition_coefficient must be positive and finite$",
            id="zero-tissue-gas-coefficient",
        ),
        pytest.param(
            "tissue_gas_partition_coefficient",
            0.5,
            SimulationConfigurationError,
            TOO_SMALL_FOR_THE_AGENT_HELD.format(field="tissue_gas_partition_coefficient"),
            id="tissue-gas-coefficient-under-the-agent-held",
        ),
        pytest.param(
            "blood_flow_l_min",
            -1.0,
            SimulationConfigurationError,
            "^blood_flow_l_min must be nonnegative and finite$",
            id="negative-blood-flow",
        ),
        pytest.param(
            "blood_flow_l_min",
            inf,
            SimulationConfigurationError,
            "^blood_flow_l_min must be nonnegative and finite$",
            id="infinite-blood-flow",
        ),
        pytest.param(
            "blood_flow_l_min",
            True,
            TypeError,
            "^blood_flow_l_min of True has type bool",
            id="bool-blood-flow",
        ),
        pytest.param(
            "volume",
            1.0,
            AttributeError,
            "^'TissueGroup' object has no attribute 'volume'",
            id="misspelt-field",
        ),
    ],
)
def test_a_direct_write_is_held_to_the_constructors_checks(
    field: str, value: object, error: type[Exception], message: str
) -> None:
    """An assignment past the constructor and the setters is refused as they refuse it.

    Until `PL-19Y0` only the agent amount was checked at the write
    (`PL-544D`), so `perfusion_fraction = 7.0` and `volume_l = -1.0` were each
    accepted on a built tissue. A volume or a tissue:gas coefficient is also
    held to the agent the tissue holds, since either shrinks the capacity the
    partial pressure is the amount over: 0.5 under the 2.0 L held would put
    this tissue at two atmospheres. A name that is no field passes the guard
    to the slots, which refuse it, so a misspelt write cannot leave the field
    it meant unchanged while appearing to succeed. Nothing is written when a
    value is refused.
    """

    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.5))
    held = astuple(tissue)

    with pytest.raises(error, match=message):
        setattr(tissue, field, value)

    assert astuple(tissue) == held


def test_a_capacity_at_the_agent_held_is_written_and_a_copy_is_held_to_it_too() -> None:
    """The capacity bound is closed, and `replace`, a copy and a pickle meet the same checks.

    A volume or a tissue:gas coefficient giving a capacity equal to the agent
    held is a partial pressure of exactly one atmosphere, and is written; the
    coefficient's capacity is formed with the volume, not the blood:gas
    coefficient, which this tissue holds at a quarter of its tissue:gas
    one. `dataclasses.replace` builds a
    new tissue through its constructor's writes, and a copy and a pickle
    restore the fields one at a time through `__setattr__`, so a perfusion
    fraction planted past the guard is refused when either is made rather than
    carried into the new tissue (`PL-19Y0`).
    """

    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.5))
    refused = "^perfusion_fraction must not exceed 1$"

    with pytest.raises(SimulationConfigurationError, match=refused):
        replace(tissue, perfusion_fraction=7.0)

    smuggled = copy.copy(tissue)
    object.__setattr__(smuggled, "perfusion_fraction", 7.0)

    with pytest.raises(SimulationConfigurationError, match=refused):
        copy.copy(smuggled)

    with pytest.raises(SimulationConfigurationError, match=refused):
        pickle.loads(pickle.dumps(smuggled))

    tissue.volume_l = 1.0

    assert tissue.partial_pressure_fraction == 1.0

    tissue.volume_l = 2.0
    tissue.tissue_gas_partition_coefficient = 1.0

    assert tissue.partial_pressure_fraction == 1.0


def test_a_refused_blood_flow_leaves_the_flow_as_it_was() -> None:
    """`set_blood_flow` refuses through the write's own guard, and writes nothing (`PL-19Y0`)."""

    tissue = _build_tissue()

    with pytest.raises(
        SimulationConfigurationError, match="^blood_flow_l_min must be nonnegative and finite$"
    ):
        tissue.set_blood_flow(-1.0)

    assert tissue.blood_flow_l_min == 1.0


def test_capacity_uses_volume_and_tissue_gas_coefficient() -> None:
    tissue = _build_tissue()

    assert tissue.capacity_l == 4.0


def test_derives_tissue_blood_partition_coefficient() -> None:
    tissue = _build_tissue()

    assert tissue.tissue_blood_partition_coefficient == 4.0


def test_one_time_constant_reaches_expected_fraction() -> None:
    tissue = _build_tissue()

    tissue.advance(
        arterial_partial_pressure_fraction=Fraction(1.0), simulation_step_s=tissue.time_constant_s
    )

    assert tissue.partial_pressure_fraction == pytest.approx(1.0 - exp(-1.0))


def test_a_larger_or_more_soluble_tissue_has_a_longer_time_constant() -> None:
    """`docs/MODEL.md` § "Directional tissue-capacity test".

    Increasing either $V_i$ or $\\lambda_{i:b}$, with flow held constant, must
    lengthen the tissue time constant.

    Three otherwise identical groups at one blood flow isolate the two
    factors: the second raises the volume alone, and the third raises the
    tissue:gas coefficient alone, which raises $\\lambda_{i:b}$ because the
    blood:gas coefficient is held fixed. The intermediate assertions state
    that each variant moved only its own factor and that flow really is held
    constant, so a change to the fixture cannot leave the directional claims
    below passing for the wrong reason.
    """

    baseline = _build_tissue()
    larger = TissueGroup(
        name="larger",
        volume_l=3.0,
        perfusion_fraction=0.2,
        blood_gas_partition_coefficient=0.5,
        tissue_gas_partition_coefficient=2.0,
        blood_flow_l_min=1.0,
    )
    more_soluble = TissueGroup(
        name="more soluble",
        volume_l=2.0,
        perfusion_fraction=0.2,
        blood_gas_partition_coefficient=0.5,
        tissue_gas_partition_coefficient=3.0,
        blood_flow_l_min=1.0,
    )

    assert baseline.blood_flow_l_min == larger.blood_flow_l_min == more_soluble.blood_flow_l_min

    assert larger.volume_l > baseline.volume_l
    assert larger.tissue_blood_partition_coefficient == (
        baseline.tissue_blood_partition_coefficient
    )

    assert more_soluble.volume_l == baseline.volume_l
    assert more_soluble.tissue_blood_partition_coefficient > (
        baseline.tissue_blood_partition_coefficient
    )

    assert larger.time_constant_s > baseline.time_constant_s
    assert more_soluble.time_constant_s > baseline.time_constant_s


def test_zero_flow_preserves_tissue_state() -> None:
    tissue = _build_tissue(blood_flow_l_min=0.0)
    tissue.set_partial_pressure_fraction(Fraction(0.25))

    amount_before = tissue.agent_amount_l
    amount_change = tissue.advance(
        arterial_partial_pressure_fraction=Fraction(1.0), simulation_step_s=60.0
    )

    assert tissue.time_constant_s == inf
    assert amount_change == 0.0
    assert tissue.agent_amount_l == amount_before
    assert tissue.partial_pressure_fraction == 0.25


def test_washout_returns_agent_to_blood() -> None:
    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.8))

    amount_change = tissue.advance(
        arterial_partial_pressure_fraction=Fraction(0.0), simulation_step_s=10.0
    )

    assert amount_change < 0.0
    assert 0.0 < tissue.partial_pressure_fraction < 0.8


def test_exact_update_is_independent_of_step_size() -> None:
    one_step = _build_tissue()
    many_steps = _build_tissue()

    one_step.advance(arterial_partial_pressure_fraction=Fraction(0.08), simulation_step_s=60.0)

    for _ in range(600):
        many_steps.advance(arterial_partial_pressure_fraction=Fraction(0.08), simulation_step_s=0.1)

    assert many_steps.agent_amount_l == pytest.approx(one_step.agent_amount_l, rel=1e-12)


def test_changing_flow_preserves_stored_agent() -> None:
    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.4))
    amount_before = tissue.agent_amount_l

    tissue.set_blood_flow(3.0)

    assert tissue.blood_flow_l_min == 3.0
    assert tissue.agent_amount_l == amount_before


def test_reset_clears_agent_and_preserves_parameters() -> None:
    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.4))

    tissue.reset()

    assert tissue.agent_amount_l == 0.0
    assert tissue.partial_pressure_fraction == 0.0
    assert tissue.volume_l == 2.0
    assert tissue.blood_flow_l_min == 1.0


@pytest.mark.parametrize("invalid_value", [0.0, -1.0, float("inf"), float("nan")])
def test_rejects_invalid_tissue_volume(invalid_value: float) -> None:
    with pytest.raises(SimulationConfigurationError, match="volume_l"):
        TissueGroup(
            name="test",
            volume_l=invalid_value,
            perfusion_fraction=0.2,
            blood_gas_partition_coefficient=0.5,
            tissue_gas_partition_coefficient=2.0,
        )


@pytest.mark.parametrize("factor", ["volume_l", "tissue_gas_partition_coefficient"])
def test_a_capacity_factor_that_is_not_a_number_is_refused_under_its_own_name(factor: str) -> None:
    """Each factor of the capacity refuses a non-number by its own name, at its own write.

    The tissue's counterpart of `tests/unit/test_alveolar.py`'s test of the
    same shape: `capacity_l` multiplies the volume by the coefficient, and
    while the amount's write read both before `__post_init__` had checked
    them, a `str` in either came back as the multiplication's own
    `TypeError`, naming neither, unless a `require_a_number` on each stood in
    (`PL-544D`, found at review). Since `PL-19Y0` each factor's own write
    checks it first.
    """

    fields: dict[str, object] = dict(
        name="test",
        volume_l=2.0,
        perfusion_fraction=0.2,
        blood_gas_partition_coefficient=0.5,
        tissue_gas_partition_coefficient=2.0,
    )
    fields[factor] = "2"

    with pytest.raises(TypeError, match=f"^{factor} of '2' has type str"):
        TissueGroup(**fields)  # type: ignore[arg-type]


def test_a_rollback_restores_the_captured_amount_past_the_capacity_guard() -> None:
    """`restore_state` writes what the tissue held, whatever the capacity has become.

    The tissue's counterpart of `tests/unit/test_alveolar.py`'s test of the
    same name (`PL-544D`, found at review): the volume is written past its own
    guard, which since `PL-19Y0` refuses it, the rollback writes the captured
    amount past the capacity guard, and the restored state is the one the step
    began from, over capacity, for the snapshot's `Fraction` to refuse.
    """

    tissue = _build_tissue()
    tissue.set_partial_pressure_fraction(Fraction(0.4))
    captured = tissue.capture_state()
    tissue.set_partial_pressure_fraction(Fraction(0.5))
    object.__setattr__(tissue, "volume_l", tissue.volume_l / 4)

    tissue.restore_state(captured)

    assert tissue.agent_amount_l == captured.agent_amount_l
    assert tissue.partial_pressure_fraction > 1.0
