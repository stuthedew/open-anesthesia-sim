from copy import deepcopy
from typing import Any

import pytest
from pydantic import BaseModel, model_validator
from pydantic import ValidationError as PydanticValidationError

from anesthesia_sim.core import parameters as parameters_module
from anesthesia_sim.core.parameters import (
    load_agent_parameters,
    load_reference_adult_parameters,
    load_sevoflurane_parameters,
    parse_agent_parameters,
    parse_reference_adult_parameters,
)


def _valid_agent_payload() -> dict[str, object]:
    return {
        "schema_version": 1,
        "id": "test-agent",
        "display_name": "Test Agent",
        "blood_gas_partition_coefficient": 0.5,
        "tissue_gas_partition_coefficients": {
            "vessel_rich": 1.0,
            "muscle": 2.0,
            "fat": 10.0,
        },
        "max_delivered_concentration_percent": 8.0,
        "mac_percent": 2.0,
        "sources": [
            {
                "citation": "Test citation",
                "url": "https://example.com/source",
                "note": "Test source only",
            }
        ],
    }


def _valid_patient_payload() -> dict[str, object]:
    return {
        "schema_version": 1,
        "id": "test-patient",
        "display_name": "Test Patient",
        "weight_kg": 70.0,
        "alveolar_gas_volume_l": 2.5,
        "venous_blood_volume_l": 1.0,
        "default_alveolar_ventilation_l_min": 4.0,
        "default_cardiac_output_l_min": 5.0,
        "tissue_groups": {
            "vessel_rich": {
                "volume_l": 6.0,
                "perfusion_fraction": 0.76,
            },
            "muscle": {
                "volume_l": 33.0,
                "perfusion_fraction": 0.18,
            },
            "fat": {
                "volume_l": 14.5,
                "perfusion_fraction": 0.06,
            },
        },
        "sources": [
            {
                "citation": "Test citation",
                "url": "https://example.com/source",
                "note": "Test source only",
            }
        ],
    }


def test_loads_built_in_sevoflurane_parameters() -> None:
    agent = load_sevoflurane_parameters()

    assert agent.id == "sevoflurane"
    assert agent.display_name == "Sevoflurane"
    assert agent.blood_gas_partition_coefficient == 0.65
    assert agent.vessel_rich_tissue_gas_partition_coefficient == 1.1
    assert agent.muscle_tissue_gas_partition_coefficient == 2.4
    assert agent.fat_tissue_gas_partition_coefficient == 34.0
    assert agent.max_delivered_concentration_percent == 8.0
    assert agent.mac_percent == 2.0
    assert len(agent.sources) >= 1


def test_derives_tissue_blood_coefficients() -> None:
    agent = load_sevoflurane_parameters()

    assert agent.vessel_rich_tissue_blood_partition_coefficient == pytest.approx(1.1 / 0.65)
    assert agent.muscle_tissue_blood_partition_coefficient == pytest.approx(2.4 / 0.65)
    assert agent.fat_tissue_blood_partition_coefficient == pytest.approx(34.0 / 0.65)


def test_loads_built_in_isoflurane_parameters() -> None:
    agent = load_agent_parameters("isoflurane")

    assert agent.id == "isoflurane"
    assert agent.display_name == "Isoflurane"
    assert agent.blood_gas_partition_coefficient == 1.3
    assert agent.vessel_rich_tissue_gas_partition_coefficient == 2.1
    assert agent.muscle_tissue_gas_partition_coefficient == 4.5
    assert agent.fat_tissue_gas_partition_coefficient == 70.0
    assert agent.max_delivered_concentration_percent == 5.0
    assert agent.mac_percent == 1.2
    assert len(agent.sources) >= 1


def test_loads_built_in_desflurane_parameters() -> None:
    agent = load_agent_parameters("desflurane")

    assert agent.id == "desflurane"
    assert agent.display_name == "Desflurane"
    assert agent.blood_gas_partition_coefficient == 0.42
    assert agent.vessel_rich_tissue_gas_partition_coefficient == 0.54
    assert agent.muscle_tissue_gas_partition_coefficient == 0.97
    assert agent.fat_tissue_gas_partition_coefficient == 13.0
    assert agent.max_delivered_concentration_percent == 18.0
    assert agent.mac_percent == 6.0
    assert len(agent.sources) >= 1


def test_desflurane_is_less_soluble_than_sevoflurane_which_is_less_soluble_than_isoflurane() -> (
    None
):
    """Directional check against the shared Gas Man source table (Stadler et al. 2012)."""

    desflurane = load_agent_parameters("desflurane")
    sevoflurane = load_agent_parameters("sevoflurane")
    isoflurane = load_agent_parameters("isoflurane")

    assert (
        desflurane.blood_gas_partition_coefficient
        < sevoflurane.blood_gas_partition_coefficient
        < isoflurane.blood_gas_partition_coefficient
    )
    assert (
        desflurane.fat_tissue_gas_partition_coefficient
        < sevoflurane.fat_tissue_gas_partition_coefficient
        < isoflurane.fat_tissue_gas_partition_coefficient
    )


def test_rejects_unknown_agent_id() -> None:
    with pytest.raises(ValueError, match="unknown agent_id"):
        load_agent_parameters("halothane")


def test_rejects_agent_file_with_mismatched_id(monkeypatch: Any) -> None:
    monkeypatch.setitem(
        parameters_module.AGENT_DATA_FILENAMES,
        "sevoflurane",
        "isoflurane.json",
    )

    with pytest.raises(ValueError, match="expected 'sevoflurane'"):
        load_agent_parameters("sevoflurane")


def test_loads_reference_adult_parameters() -> None:
    patient = load_reference_adult_parameters()

    assert patient.id == "reference_adult_70kg"
    assert patient.weight_kg == 70.0
    assert patient.alveolar_gas_volume_l == 2.5
    assert patient.venous_blood_volume_l == 1.0
    assert patient.default_alveolar_ventilation_l_min == 4.0
    assert patient.default_cardiac_output_l_min == 5.0
    assert patient.vessel_rich_volume_l == 6.0
    assert patient.muscle_volume_l == 33.0
    assert patient.fat_volume_l == 14.5
    assert patient.total_perfusion_fraction == pytest.approx(1.0)
    assert len(patient.sources) >= 1


def test_rejects_unknown_schema_version() -> None:
    payload = _valid_agent_payload()
    payload["schema_version"] = 2

    with pytest.raises(ValueError, match="unsupported schema_version"):
        parse_agent_parameters(payload)


def test_rejects_nonfinite_partition_coefficient() -> None:
    payload = _valid_agent_payload()
    payload["blood_gas_partition_coefficient"] = float("nan")

    with pytest.raises(
        ValueError,
        match="blood_gas_partition_coefficient",
    ):
        parse_agent_parameters(payload)


def test_rejects_max_delivered_concentration_percent_over_100() -> None:
    payload = _valid_agent_payload()
    payload["max_delivered_concentration_percent"] = 150.0

    with pytest.raises(
        ValueError,
        match="max_delivered_concentration_percent",
    ):
        parse_agent_parameters(payload)


def test_rejects_nonpositive_max_delivered_concentration_percent() -> None:
    payload = _valid_agent_payload()
    payload["max_delivered_concentration_percent"] = 0.0

    with pytest.raises(
        ValueError,
        match="max_delivered_concentration_percent",
    ):
        parse_agent_parameters(payload)


def test_rejects_mac_percent_over_100() -> None:
    payload = _valid_agent_payload()
    payload["mac_percent"] = 150.0

    with pytest.raises(ValueError, match="mac_percent"):
        parse_agent_parameters(payload)


def test_rejects_nonpositive_mac_percent() -> None:
    payload = _valid_agent_payload()
    payload["mac_percent"] = 0.0

    with pytest.raises(ValueError, match="mac_percent"):
        parse_agent_parameters(payload)


def test_rejects_mac_percent_exceeding_max_delivered_concentration_percent() -> None:
    payload = _valid_agent_payload()
    payload["max_delivered_concentration_percent"] = 8.0
    payload["mac_percent"] = 9.0

    with pytest.raises(ValueError, match="mac_percent"):
        parse_agent_parameters(payload)


def test_mac_cross_check_is_a_model_validator_not_a_field_validator() -> None:
    """Regression (PL-016): the only cross-field agent check must fail closed.

    As a `field_validator` reading `info.data`, the guard saw
    `max_delivered_concentration_percent` only because that field happened
    to be declared first. Reordering the two fields turned it into a
    silent no-op, so a file declaring 40% MAC on a 5% vaporizer would load
    clean — and `RespiratorySystem.for_agent()` starts every run at 1 MAC.
    A model validator runs after every field is populated, so declaration
    order cannot reach it.
    """

    decorators = parameters_module._AgentPayload.__pydantic_decorators__

    assert "_mac_percent_must_not_exceed_vaporizer_max" in decorators.model_validators
    assert "_mac_percent_must_not_exceed_vaporizer_max" not in decorators.field_validators


def test_mac_cross_check_fires_with_the_fields_declared_in_either_order() -> None:
    """Run the shipped guard against a model declaring the two fields in
    the order that previously defeated it.
    """

    guard = parameters_module._AgentPayload.__dict__["_mac_percent_must_not_exceed_vaporizer_max"]
    payload = {"mac_percent": 40.0, "max_delivered_concentration_percent": 5.0}

    for first, second in (
        ("mac_percent", "max_delivered_concentration_percent"),
        ("max_delivered_concentration_percent", "mac_percent"),
    ):
        probe = type(
            "AgentPayloadFieldOrderProbe",
            (BaseModel,),
            {
                "__annotations__": {first: float, second: float},
                "guard": model_validator(mode="after")(guard),
            },
        )

        assert list(probe.model_fields) == [first, second]

        with pytest.raises(PydanticValidationError, match="mac_percent"):
            probe.model_validate(payload)


def test_every_shipped_agent_can_deliver_its_own_one_mac() -> None:
    """`for_agent()` starts at 1 MAC, so no shipped file may declare a MAC
    its own vaporizer cannot reach.
    """

    for agent_id in ("sevoflurane", "isoflurane", "desflurane"):
        agent = load_agent_parameters(agent_id)

        assert agent.mac_percent <= agent.max_delivered_concentration_percent


def test_rejects_perfusion_fractions_that_do_not_sum_to_one() -> None:
    payload = _valid_patient_payload()
    tissue_groups = deepcopy(payload["tissue_groups"])

    assert isinstance(tissue_groups, dict)
    fat = tissue_groups["fat"]

    assert isinstance(fat, dict)
    fat["perfusion_fraction"] = 0.05
    payload["tissue_groups"] = tissue_groups

    with pytest.raises(
        ValueError,
        match="perfusion fractions must sum to 1",
    ):
        parse_reference_adult_parameters(payload)


def test_rejects_missing_provenance() -> None:
    payload = _valid_agent_payload()
    payload["sources"] = []

    with pytest.raises(
        ValueError,
        match="sources must contain at least one reference",
    ):
        parse_agent_parameters(payload)
