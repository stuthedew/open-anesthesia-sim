from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from math import isfinite
from typing import cast

SUPPORTED_SCHEMA_VERSION = 1
FLOW_FRACTION_TOLERANCE = 1e-12


@dataclass(frozen=True, slots=True)
class SourceReference:
    """Provenance for one scientific or physiologic parameter set."""

    citation: str
    url: str
    note: str


@dataclass(frozen=True, slots=True)
class AgentParameters:
    """Validated partition parameters for one volatile anesthetic."""

    schema_version: int
    id: str
    display_name: str
    blood_gas_partition_coefficient: float
    vessel_rich_tissue_gas_partition_coefficient: float
    muscle_tissue_gas_partition_coefficient: float
    fat_tissue_gas_partition_coefficient: float
    sources: tuple[SourceReference, ...]

    @property
    def vessel_rich_tissue_blood_partition_coefficient(self) -> float:
        """Derive tissue:blood from tissue:gas / blood:gas; not stored redundantly."""

        return (
            self.vessel_rich_tissue_gas_partition_coefficient / self.blood_gas_partition_coefficient
        )

    @property
    def muscle_tissue_blood_partition_coefficient(self) -> float:
        """Derive tissue:blood from tissue:gas / blood:gas; not stored redundantly."""

        return self.muscle_tissue_gas_partition_coefficient / self.blood_gas_partition_coefficient

    @property
    def fat_tissue_blood_partition_coefficient(self) -> float:
        """Derive tissue:blood from tissue:gas / blood:gas; not stored redundantly."""

        return self.fat_tissue_gas_partition_coefficient / self.blood_gas_partition_coefficient


@dataclass(frozen=True, slots=True)
class ReferenceAdultParameters:
    """Validated physiologic defaults for the v0.1.0 reference adult."""

    schema_version: int
    id: str
    display_name: str
    weight_kg: float
    alveolar_gas_volume_l: float
    venous_blood_volume_l: float
    default_alveolar_ventilation_l_min: float
    default_cardiac_output_l_min: float
    vessel_rich_volume_l: float
    vessel_rich_perfusion_fraction: float
    muscle_volume_l: float
    muscle_perfusion_fraction: float
    fat_volume_l: float
    fat_perfusion_fraction: float
    sources: tuple[SourceReference, ...]

    @property
    def total_perfusion_fraction(self) -> float:
        """Sum tissue-group perfusion fractions; must equal 1 within tolerance."""

        return (
            self.vessel_rich_perfusion_fraction
            + self.muscle_perfusion_fraction
            + self.fat_perfusion_fraction
        )


def _require_mapping(value: object, name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")

    if not all(isinstance(key, str) for key in value):
        raise ValueError(f"{name} must use string keys")

    return cast(dict[str, object], value)


def _require_sequence(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be an array")

    return cast(list[object], value)


def _require_nonempty_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")

    return value


def _require_schema_version(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("schema_version must be an integer")

    if value != SUPPORTED_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported schema_version: {value}; expected {SUPPORTED_SCHEMA_VERSION}"
        )

    return value


def _require_positive_finite(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")

    numeric_value = float(value)

    if not isfinite(numeric_value) or numeric_value <= 0.0:
        raise ValueError(f"{name} must be positive and finite")

    return numeric_value


def _require_positive_fraction(value: object, name: str) -> float:
    numeric_value = _require_positive_finite(value, name)

    if numeric_value > 1.0:
        raise ValueError(f"{name} must not exceed 1")

    return numeric_value


def _parse_source(value: object, name: str) -> SourceReference:
    source = _require_mapping(value, name)

    return SourceReference(
        citation=_require_nonempty_string(
            source.get("citation"),
            f"{name}.citation",
        ),
        url=_require_nonempty_string(
            source.get("url"),
            f"{name}.url",
        ),
        note=_require_nonempty_string(
            source.get("note"),
            f"{name}.note",
        ),
    )


def _parse_sources(value: object) -> tuple[SourceReference, ...]:
    source_values = _require_sequence(value, "sources")

    if not source_values:
        raise ValueError("sources must contain at least one reference")

    return tuple(
        _parse_source(source, f"sources[{index}]") for index, source in enumerate(source_values)
    )


def parse_agent_parameters(payload: object) -> AgentParameters:
    """Validate an agent-data payload and return immutable parameters."""

    root = _require_mapping(payload, "agent")
    tissue_coefficients = _require_mapping(
        root.get("tissue_gas_partition_coefficients"),
        "tissue_gas_partition_coefficients",
    )

    return AgentParameters(
        schema_version=_require_schema_version(root.get("schema_version")),
        id=_require_nonempty_string(root.get("id"), "id"),
        display_name=_require_nonempty_string(
            root.get("display_name"),
            "display_name",
        ),
        blood_gas_partition_coefficient=_require_positive_finite(
            root.get("blood_gas_partition_coefficient"),
            "blood_gas_partition_coefficient",
        ),
        vessel_rich_tissue_gas_partition_coefficient=(
            _require_positive_finite(
                tissue_coefficients.get("vessel_rich"),
                "tissue_gas_partition_coefficients.vessel_rich",
            )
        ),
        muscle_tissue_gas_partition_coefficient=(
            _require_positive_finite(
                tissue_coefficients.get("muscle"),
                "tissue_gas_partition_coefficients.muscle",
            )
        ),
        fat_tissue_gas_partition_coefficient=(
            _require_positive_finite(
                tissue_coefficients.get("fat"),
                "tissue_gas_partition_coefficients.fat",
            )
        ),
        sources=_parse_sources(root.get("sources")),
    )


def parse_reference_adult_parameters(
    payload: object,
) -> ReferenceAdultParameters:
    """Validate a reference-adult payload and return immutable parameters."""

    root = _require_mapping(payload, "patient")
    tissue_groups = _require_mapping(
        root.get("tissue_groups"),
        "tissue_groups",
    )
    vessel_rich = _require_mapping(
        tissue_groups.get("vessel_rich"),
        "tissue_groups.vessel_rich",
    )
    muscle = _require_mapping(
        tissue_groups.get("muscle"),
        "tissue_groups.muscle",
    )
    fat = _require_mapping(
        tissue_groups.get("fat"),
        "tissue_groups.fat",
    )

    parameters = ReferenceAdultParameters(
        schema_version=_require_schema_version(root.get("schema_version")),
        id=_require_nonempty_string(root.get("id"), "id"),
        display_name=_require_nonempty_string(
            root.get("display_name"),
            "display_name",
        ),
        weight_kg=_require_positive_finite(
            root.get("weight_kg"),
            "weight_kg",
        ),
        alveolar_gas_volume_l=_require_positive_finite(
            root.get("alveolar_gas_volume_l"),
            "alveolar_gas_volume_l",
        ),
        venous_blood_volume_l=_require_positive_finite(
            root.get("venous_blood_volume_l"),
            "venous_blood_volume_l",
        ),
        default_alveolar_ventilation_l_min=_require_positive_finite(
            root.get("default_alveolar_ventilation_l_min"),
            "default_alveolar_ventilation_l_min",
        ),
        default_cardiac_output_l_min=_require_positive_finite(
            root.get("default_cardiac_output_l_min"),
            "default_cardiac_output_l_min",
        ),
        vessel_rich_volume_l=_require_positive_finite(
            vessel_rich.get("volume_l"),
            "tissue_groups.vessel_rich.volume_l",
        ),
        vessel_rich_perfusion_fraction=_require_positive_fraction(
            vessel_rich.get("perfusion_fraction"),
            "tissue_groups.vessel_rich.perfusion_fraction",
        ),
        muscle_volume_l=_require_positive_finite(
            muscle.get("volume_l"),
            "tissue_groups.muscle.volume_l",
        ),
        muscle_perfusion_fraction=_require_positive_fraction(
            muscle.get("perfusion_fraction"),
            "tissue_groups.muscle.perfusion_fraction",
        ),
        fat_volume_l=_require_positive_finite(
            fat.get("volume_l"),
            "tissue_groups.fat.volume_l",
        ),
        fat_perfusion_fraction=_require_positive_fraction(
            fat.get("perfusion_fraction"),
            "tissue_groups.fat.perfusion_fraction",
        ),
        sources=_parse_sources(root.get("sources")),
    )

    if abs(parameters.total_perfusion_fraction - 1.0) > FLOW_FRACTION_TOLERANCE:
        raise ValueError("tissue perfusion fractions must sum to 1")

    return parameters


def _load_packaged_json(package: str, filename: str) -> object:
    resource = files(package).joinpath(filename)

    with resource.open("r", encoding="utf-8") as stream:
        payload: object = json.load(stream)

    return payload


def load_sevoflurane_parameters() -> AgentParameters:
    """Load and validate the built-in sevoflurane definition."""

    payload = _load_packaged_json(
        "anesthesia_sim.data.agents",
        "sevoflurane.json",
    )
    return parse_agent_parameters(payload)


def load_reference_adult_parameters() -> ReferenceAdultParameters:
    """Load and validate the built-in v0.1.0 reference adult."""

    payload = _load_packaged_json(
        "anesthesia_sim.data.patients",
        "reference_adult.json",
    )
    return parse_reference_adult_parameters(payload)
