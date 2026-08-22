from copy import deepcopy

import pytest

from anesthesia_sim.core.parameters import (
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
    assert len(agent.sources) >= 1


def test_derives_tissue_blood_coefficients() -> None:
    agent = load_sevoflurane_parameters()

    assert agent.vessel_rich_tissue_blood_partition_coefficient == pytest.approx(1.1 / 0.65)
    assert agent.muscle_tissue_blood_partition_coefficient == pytest.approx(2.4 / 0.65)
    assert agent.fat_tissue_blood_partition_coefficient == pytest.approx(34.0 / 0.65)


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
