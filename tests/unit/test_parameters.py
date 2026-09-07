import importlib.resources
import json
from copy import deepcopy
from typing import Any

import doc_check
import pytest
from pydantic import BaseModel, model_validator
from pydantic import ValidationError as PydanticValidationError

from anesthesia_sim.core import parameters as parameters_module
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.parameters import (
    AGENT_DATA_FILENAMES,
    SOURCE_TIERS,
    load_agent_parameters,
    load_reference_adult_parameters,
    load_sevoflurane_parameters,
    parse_agent_parameters,
    parse_reference_adult_parameters,
)


def _valid_agent_payload() -> dict[str, object]:
    return {
        "schema_version": 2,
        "id": "test-agent",
        "display_name": "Test Agent",
        "blood_gas_partition_coefficient": 0.5,
        "tissue_gas_partition_coefficients": {"vessel_rich": 1.0, "muscle": 2.0, "fat": 10.0},
        "max_delivered_concentration_percent": 8.0,
        "mac_percent": 2.0,
        "mac_awake": {
            "fraction_of_mac": 0.34,
            "standard_deviation_fraction_of_mac": 0.05,
            "mac_reference_basis": "test basis only",
        },
        "sources": [
            {
                "citation": "Test citation",
                "url": "https://example.com/source",
                "tier": "primary",
                "adopted": True,
                "note": "Test source only",
            }
        ],
    }


def _valid_patient_payload() -> dict[str, object]:
    return {
        "schema_version": 2,
        "id": "test-patient",
        "display_name": "Test Patient",
        "weight_kg": 70.0,
        "alveolar_gas_volume_l": 2.5,
        "venous_pool_volume_l": 1.222,
        "default_alveolar_ventilation_l_min": 4.0,
        "default_cardiac_output_l_min": 5.0,
        "tissue_groups": {
            "vessel_rich": {"volume_l": 6.0, "perfusion_fraction": 0.76},
            "muscle": {"volume_l": 33.0, "perfusion_fraction": 0.18},
            "fat": {"volume_l": 14.5, "perfusion_fraction": 0.06},
        },
        "sources": [
            {
                "citation": "Test citation",
                "url": "https://example.com/source",
                "tier": "primary",
                "adopted": True,
                "note": "Test source only",
            }
        ],
    }


def test_payload_model_rejects_empty_string() -> None:
    payload = _valid_agent_payload()
    payload["id"] = " "

    with pytest.raises(PydanticValidationError, match="must be a nonempty string"):
        parameters_module._AgentPayload.model_validate(payload)


def test_payload_model_rejects_noninteger_schema_version() -> None:
    payload = _valid_agent_payload()
    payload["schema_version"] = 1.0

    with pytest.raises(PydanticValidationError, match="schema_version must be an integer"):
        parameters_module._AgentPayload.model_validate(payload)


def test_payload_model_rejects_nonnumeric_positive_finite_value() -> None:
    payload = _valid_agent_payload()
    payload["blood_gas_partition_coefficient"] = "not a number"

    with pytest.raises(PydanticValidationError, match="must be a number"):
        parameters_module._AgentPayload.model_validate(payload)


def test_payload_model_rejects_positive_fraction_above_one() -> None:
    payload = _valid_patient_payload()
    tissue_groups = payload["tissue_groups"]

    assert isinstance(tissue_groups, dict)
    vessel_rich = tissue_groups["vessel_rich"]

    assert isinstance(vessel_rich, dict)
    vessel_rich["perfusion_fraction"] = 1.1

    with pytest.raises(PydanticValidationError, match="must not exceed 1"):
        parameters_module._ReferenceAdultPayload.model_validate(payload)


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
    """Directional check against the shared Gas Man source table (De Wolf et al. 2012)."""

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
    with pytest.raises(SimulationConfigurationError, match="unknown agent_id"):
        load_agent_parameters("halothane")


def test_rejects_agent_file_with_mismatched_id(monkeypatch: Any) -> None:
    monkeypatch.setitem(parameters_module.AGENT_DATA_FILENAMES, "sevoflurane", "isoflurane.json")

    with pytest.raises(SimulationConfigurationError, match="expected 'sevoflurane'"):
        load_agent_parameters("sevoflurane")


def test_loads_reference_adult_parameters() -> None:
    patient = load_reference_adult_parameters()

    assert patient.id == "reference_adult_70kg"
    assert patient.weight_kg == 70.0
    assert patient.alveolar_gas_volume_l == 2.5
    assert patient.venous_pool_volume_l == 1.222
    assert patient.default_alveolar_ventilation_l_min == 4.0
    assert patient.default_cardiac_output_l_min == 5.0
    assert patient.vessel_rich_volume_l == 6.0
    assert patient.muscle_volume_l == 33.0
    assert patient.fat_volume_l == 14.5
    assert patient.total_perfusion_fraction == pytest.approx(1.0)
    assert len(patient.sources) >= 1


def test_rejects_unknown_schema_version() -> None:
    payload = _valid_agent_payload()
    payload["schema_version"] = 3

    with pytest.raises(SimulationConfigurationError, match="unsupported schema_version"):
        parse_agent_parameters(payload)


def test_rejects_nonfinite_partition_coefficient() -> None:
    payload = _valid_agent_payload()
    payload["blood_gas_partition_coefficient"] = float("nan")

    with pytest.raises(SimulationConfigurationError, match="blood_gas_partition_coefficient"):
        parse_agent_parameters(payload)


def test_rejects_max_delivered_concentration_percent_over_100() -> None:
    payload = _valid_agent_payload()
    payload["max_delivered_concentration_percent"] = 150.0

    with pytest.raises(SimulationConfigurationError, match="max_delivered_concentration_percent"):
        parse_agent_parameters(payload)


def test_rejects_nonpositive_max_delivered_concentration_percent() -> None:
    payload = _valid_agent_payload()
    payload["max_delivered_concentration_percent"] = 0.0

    with pytest.raises(SimulationConfigurationError, match="max_delivered_concentration_percent"):
        parse_agent_parameters(payload)


def test_rejects_mac_percent_over_100() -> None:
    payload = _valid_agent_payload()
    payload["mac_percent"] = 150.0

    with pytest.raises(SimulationConfigurationError, match="mac_percent"):
        parse_agent_parameters(payload)


def test_rejects_nonpositive_mac_percent() -> None:
    payload = _valid_agent_payload()
    payload["mac_percent"] = 0.0

    with pytest.raises(SimulationConfigurationError, match="mac_percent"):
        parse_agent_parameters(payload)


def test_rejects_mac_percent_exceeding_max_delivered_concentration_percent() -> None:
    payload = _valid_agent_payload()
    payload["max_delivered_concentration_percent"] = 8.0
    payload["mac_percent"] = 9.0

    with pytest.raises(SimulationConfigurationError, match="mac_percent"):
        parse_agent_parameters(payload)


def test_mac_cross_check_is_a_model_validator_not_a_field_validator() -> None:
    """Regression (PL-016): the only cross-field agent check must fail closed.

    As a `field_validator` reading `info.data`, the guard saw
    `max_delivered_concentration_percent` only because that field happened
    to be declared first. Reordering the two fields turned it into a
    silent no-op, so a file declaring 40% MAC on a 5% vaporizer would load
    clean — and `AgentUptakeSystem.for_agent()` starts every run at 1 MAC.
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

    with pytest.raises(SimulationConfigurationError, match="perfusion fractions must sum to 1"):
        parse_reference_adult_parameters(payload)


def test_rejects_missing_provenance() -> None:
    payload = _valid_agent_payload()
    payload["sources"] = []

    with pytest.raises(
        SimulationConfigurationError, match="sources must contain at least one reference"
    ):
        parse_agent_parameters(payload)


def test_rejects_unknown_top_level_agent_key() -> None:
    """A typo'd duplicate of a real key must fail, not be silently dropped.

    This is the exact shape the review harness reproduced as P1-4: the
    correctly spelled key is still present, so nothing is *missing* and the
    load would otherwise succeed while the misspelled edit took no effect.
    """

    payload = _valid_agent_payload()
    payload["blood_gas_partitition_coefficient"] = 9.9

    with pytest.raises(SimulationConfigurationError, match="blood_gas_partitition_coefficient"):
        parse_agent_parameters(payload)


def test_rejects_unknown_nested_agent_key() -> None:
    payload = _valid_agent_payload()
    coefficients = deepcopy(payload["tissue_gas_partition_coefficients"])

    assert isinstance(coefficients, dict)
    coefficients["muscel"] = 2.4
    payload["tissue_gas_partition_coefficients"] = coefficients

    with pytest.raises(SimulationConfigurationError, match="muscel"):
        parse_agent_parameters(payload)


def test_rejects_unknown_key_in_a_source_entry() -> None:
    payload = _valid_agent_payload()
    sources = deepcopy(payload["sources"])

    assert isinstance(sources, list)
    first = sources[0]

    assert isinstance(first, dict)
    first["doi"] = "10.1000/example"
    payload["sources"] = sources

    with pytest.raises(SimulationConfigurationError, match="doi"):
        parse_agent_parameters(payload)


def test_rejects_unknown_top_level_patient_key() -> None:
    payload = _valid_patient_payload()
    payload["height_cm"] = 175.0

    with pytest.raises(SimulationConfigurationError, match="height_cm"):
        parse_reference_adult_parameters(payload)


def test_rejects_unknown_tissue_group_name() -> None:
    """An unmodeled compartment must fail rather than be quietly ignored.

    A file naming a `brain` group documents a four-compartment model while
    the app runs three, and the perfusion-fraction sum check would not
    catch it: the three modeled fractions still total 1.
    """

    payload = _valid_patient_payload()
    tissue_groups = deepcopy(payload["tissue_groups"])

    assert isinstance(tissue_groups, dict)
    tissue_groups["brain"] = {"volume_l": 1.4, "perfusion_fraction": 0.0}
    payload["tissue_groups"] = tissue_groups

    with pytest.raises(SimulationConfigurationError, match="brain"):
        parse_reference_adult_parameters(payload)


def test_rejects_unknown_key_inside_a_tissue_group() -> None:
    payload = _valid_patient_payload()
    tissue_groups = deepcopy(payload["tissue_groups"])

    assert isinstance(tissue_groups, dict)
    fat = tissue_groups["fat"]

    assert isinstance(fat, dict)
    fat["volume_ml"] = 14500.0
    payload["tissue_groups"] = tissue_groups

    with pytest.raises(SimulationConfigurationError, match="volume_ml"):
        parse_reference_adult_parameters(payload)


def test_every_payload_model_documents_why_it_exists() -> None:
    """The pair reads as duplication until something says it is not (PL-007).

    Each `_...Payload` is paired with a public, Pydantic-independent
    dataclass, and the design is correct: it is what keeps the validation
    library out of the rest of `core/`, and the two shapes differ - the
    payload mirrors the file's nesting, the public type is flat. A reader who
    does not find that written down is liable to "simplify" the pair away,
    which would couple the compartments to Pydantic and let the JSON layout
    dictate the type the simulation reads.

    Walked rather than listed, for the reason the strictness test above is
    walked: the seventh payload model added later should arrive documented by
    default rather than by being remembered. What the docstring *says* is not
    checkable and is not checked here; that it exists is.
    """

    strict_base = parameters_module._StrictPayload

    assert strict_base.__doc__, "the base carries the rationale the subclasses point at"

    for model in strict_base.__subclasses__():
        assert model.__doc__, (
            f"{model.__name__} has no docstring: a reader landing on it cannot tell "
            "why it exists beside its public dataclass"
        )


def test_every_payload_model_forbids_unknown_keys() -> None:
    """Strictness must hold for models added later, not just today's six.

    Inheriting `_StrictPayload` is what makes a new payload model strict by
    default; this walks the subclass tree so that a model which opts back
    out — or one declared against `BaseModel` directly — is caught here
    rather than by a data file loading wrong in the field.
    """

    # Reaching for the private base is the point: it is the guard under test.
    strict_base = parameters_module._StrictPayload
    subclasses = strict_base.__subclasses__()

    assert len(subclasses) == 7, "a payload model was added or removed; update this count"

    for model in subclasses:
        assert model.model_config.get("extra") == "forbid", model.__name__

    declared_payload_models = {
        name
        for name, value in vars(parameters_module).items()
        if name.endswith("Payload")
        and isinstance(value, type)
        and issubclass(value, BaseModel)
        and value is not strict_base
    }

    assert declared_payload_models == {model.__name__ for model in subclasses}, (
        "a payload model does not inherit _StrictPayload"
    )


def test_every_agent_carries_a_mac_awake_fraction_below_its_mac() -> None:
    """MAC-awake is a lower endpoint than MAC, for every shipped agent.

    Awakening happens at a lower concentration than immobility to incision,
    so a stored band reaching 1 MAC is a data error rather than an unusual
    agent. Checked against the shipped files, not a synthetic payload,
    because that is what the chart actually draws.
    """

    for agent_id in AGENT_DATA_FILENAMES:
        agent = load_agent_parameters(agent_id)
        mac_awake = agent.mac_awake

        assert 0.0 < mac_awake.fraction_of_mac < 1.0
        assert 0.0 < mac_awake.standard_deviation_fraction_of_mac
        assert 0.0 < mac_awake.fraction_of_mac - mac_awake.standard_deviation_fraction_of_mac
        assert mac_awake.fraction_of_mac + mac_awake.standard_deviation_fraction_of_mac < 1.0
        assert mac_awake.mac_reference_basis.strip()


def test_rejects_a_mac_awake_band_reaching_zero() -> None:
    """A lower edge at or below zero is not a concentration."""

    payload = _valid_agent_payload()
    payload["mac_awake"] = {
        "fraction_of_mac": 0.05,
        "standard_deviation_fraction_of_mac": 0.05,
        "mac_reference_basis": "test basis only",
    }

    with pytest.raises(SimulationConfigurationError, match="must be positive"):
        parse_agent_parameters(payload)


def test_rejects_a_mac_awake_band_reaching_one_mac() -> None:
    """An upper edge at 1 MAC would erase the decrement the chart exists to show.

    The band and the 1 MAC line are drawn so the gap between them reads as
    the decrement required for arousal. A band touching the anesthetizing
    reference is not a rendering nuisance; it contradicts what MAC-awake is.
    """

    payload = _valid_agent_payload()
    payload["mac_awake"] = {
        "fraction_of_mac": 0.96,
        "standard_deviation_fraction_of_mac": 0.05,
        "mac_reference_basis": "test basis only",
    }

    with pytest.raises(SimulationConfigurationError, match="below 1 MAC"):
        parse_agent_parameters(payload)


def test_rejects_a_mac_awake_fraction_above_one() -> None:
    """The stored value is a fraction of MAC, so it cannot exceed one."""

    payload = _valid_agent_payload()
    payload["mac_awake"] = {
        "fraction_of_mac": 2.6,
        "standard_deviation_fraction_of_mac": 0.05,
        "mac_reference_basis": "test basis only",
    }

    with pytest.raises(SimulationConfigurationError, match="mac_awake"):
        parse_agent_parameters(payload)


def test_rejects_a_mac_awake_block_missing_its_reference_basis() -> None:
    """A fraction with no stated denominator is the wrong-context failure.

    `_StrictPayload` also forbids an *extra* key here, so a file recording
    the denominator under a name the loader does not know fails rather than
    silently dropping it.
    """

    payload = _valid_agent_payload()
    payload["mac_awake"] = {"fraction_of_mac": 0.34, "standard_deviation_fraction_of_mac": 0.05}

    with pytest.raises(SimulationConfigurationError, match="mac_reference_basis"):
        parse_agent_parameters(payload)

    payload["mac_awake"] = {
        "fraction_of_mac": 0.34,
        "standard_deviation_fraction_of_mac": 0.05,
        "mac_reference_basis": "test basis only",
        "mac_awake_percent": 0.68,
    }

    with pytest.raises(SimulationConfigurationError, match="mac_awake_percent"):
        parse_agent_parameters(payload)


def test_no_agent_file_stores_mac_awake_as_a_percent() -> None:
    """The stored form is the fraction, and only the fraction.

    A shipped file that also carried an absolute percent would give a later
    reader two values to choose between, one of which is anchored to a MAC
    this project does not use. `_StrictPayload` already refuses the key; this
    states the intent so a schema change has to argue with it.
    """

    for agent_id, filename in AGENT_DATA_FILENAMES.items():
        document = json.loads(
            (importlib.resources.files("anesthesia_sim.data.agents").joinpath(filename)).read_text(
                encoding="utf-8"
            )
        )

        assert set(document["mac_awake"]) == {
            "fraction_of_mac",
            "standard_deviation_fraction_of_mac",
            "mac_reference_basis",
        }, agent_id


def test_rejects_a_source_tier_outside_the_vocabulary() -> None:
    payload = _valid_agent_payload()
    sources = deepcopy(payload["sources"])

    assert isinstance(sources, list)
    first = sources[0]
    assert isinstance(first, dict)
    first["tier"] = "tier 1"
    payload["sources"] = sources

    with pytest.raises(SimulationConfigurationError, match="tier must be one of"):
        parse_agent_parameters(payload)


def test_rejects_a_source_entry_that_declares_no_tier() -> None:
    payload = _valid_agent_payload()
    sources = deepcopy(payload["sources"])

    assert isinstance(sources, list)
    first = sources[0]
    assert isinstance(first, dict)
    del first["tier"]
    payload["sources"] = sources

    with pytest.raises(SimulationConfigurationError, match="tier"):
        parse_agent_parameters(payload)


@pytest.mark.parametrize("adopted", ["true", "false", 1, 0, None])
def test_rejects_a_nonboolean_adopted_flag(adopted: object) -> None:
    """`"adopted": "false"` is truthy, so a coercing loader would invert it.

    The field is a provenance claim about a safety-critical value, and the
    two wrong readings are not symmetric: reading an unadopted primary as
    adopted is the failure `docs/MODEL.md` § "Source hierarchy" exists to
    prevent, and it is the one a loose truthiness test produces.
    """

    payload = _valid_agent_payload()
    sources = deepcopy(payload["sources"])

    assert isinstance(sources, list)
    first = sources[0]
    assert isinstance(first, dict)
    first["adopted"] = adopted
    payload["sources"] = sources

    with pytest.raises(SimulationConfigurationError, match="must be true or false"):
        parse_agent_parameters(payload)


def test_provenance_gap_is_absent_by_default() -> None:
    assert parse_agent_parameters(_valid_agent_payload()).provenance_gap is None
    assert parse_reference_adult_parameters(_valid_patient_payload()).provenance_gap is None


def test_an_explicit_null_provenance_gap_reads_the_same_as_an_absent_one() -> None:
    """A data file may write the key out as `null`, which is not an empty gap.

    The omitted key never reaches the validator at all - Pydantic applies the
    default instead - so the two spellings take different paths to the same
    answer, and only this one exercises the validator's `None` branch.
    """

    payload = _valid_patient_payload()
    payload["provenance_gap"] = None

    assert parse_reference_adult_parameters(payload).provenance_gap is None


def test_carries_a_recorded_provenance_gap_through_to_the_public_type() -> None:
    payload = _valid_patient_payload()
    payload["provenance_gap"] = "No primary source has been adopted for any of these."

    parsed = parse_reference_adult_parameters(payload)

    assert parsed.provenance_gap == "No primary source has been adopted for any of these."


@pytest.mark.parametrize("gap", ["", "   "])
def test_rejects_an_empty_provenance_gap(gap: str) -> None:
    """An empty string is a gap recorded in form and not in substance."""

    payload = _valid_patient_payload()
    payload["provenance_gap"] = gap

    with pytest.raises(SimulationConfigurationError, match="must be a nonempty string"):
        parse_reference_adult_parameters(payload)


def test_doc_check_holds_the_same_source_tier_vocabulary() -> None:
    """The two copies exist because `doc_check.py` runs without the virtualenv.

    It cannot import this package, so the vocabulary is written twice on
    purpose; this is what stops the two drifting apart silently, which would
    let a tier the loader rejects pass `make check` or the reverse.
    """

    assert tuple(doc_check.SOURCE_TIERS) == tuple(SOURCE_TIERS)


def test_every_shipped_source_declares_a_tier_and_an_adoption() -> None:
    loaded = [load_agent_parameters(agent_id) for agent_id in AGENT_DATA_FILENAMES]
    parameter_sets: list[Any] = [*loaded, load_reference_adult_parameters()]

    for parameters in parameter_sets:
        assert parameters.sources
        for source in parameters.sources:
            assert source.tier in SOURCE_TIERS, (parameters.id, source.citation)
            assert isinstance(source.adopted, bool), (parameters.id, source.citation)


def test_the_reference_patient_records_its_provenance_gap() -> None:
    """It adopts no primary measurement for any of its eleven parameters.

    `PL-6Q8N` established that, and the gap is the reason the tier alone
    cannot carry this rule: the file cites five primary measurements, every
    one of them explicitly not adopted, so a check reading tiers would report
    it as primary-sourced.
    """

    patient = load_reference_adult_parameters()

    assert not any(source.tier == "primary" and source.adopted for source in patient.sources)
    assert patient.provenance_gap is not None
    assert patient.provenance_gap.strip()
