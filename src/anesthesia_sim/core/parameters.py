"""Load and validate agent and reference-patient parameter files.

Public types (`AgentParameters`, `ReferenceAdultParameters`) are plain,
frozen dataclasses with no dependency on the validation library, so the
rest of the core never imports Pydantic. The `_AgentPayload`/
`_ReferenceAdultPayload` Pydantic models exist only to validate
`data/agents/*.json` and `data/patients/*.json` on load and are never
exposed outside this module; `parse_agent_parameters()` and
`parse_reference_adult_parameters()` are the seam between the two.

Every payload model is strict: it inherits `_StrictPayload`, which forbids
keys the schema does not declare, so a misspelled or obsolete key in a data
file fails the load instead of being silently discarded.

Raises inside the Pydantic validators below are deliberately bare
`ValueError`s: Pydantic collects those into a `ValidationError`, and a
project exception raised there would not be collected the same way. Every
raise this module makes to a *caller* is a `SimulationConfigurationError`,
so `core/` presents one exception hierarchy at its boundary.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from math import isfinite
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict, field_validator, model_validator
from pydantic import ValidationError as PydanticValidationError

from anesthesia_sim.core.exceptions import SimulationConfigurationError

SUPPORTED_SCHEMA_VERSION = 1
FLOW_FRACTION_TOLERANCE = 1e-12


@dataclass(frozen=True, slots=True)
class SourceReference:
    """Provenance for one scientific or physiologic parameter set."""

    citation: str
    url: str
    note: str


@dataclass(frozen=True, slots=True)
class MacAwakeReference:
    """Population MAC-awake for one agent, as a fraction of that agent's MAC.

    MAC-awake is the concentration at which half of a population responds to
    verbal command — a different endpoint from MAC, which is immobility to
    surgical incision — so this is a second, lower reference and never a
    restatement of the first.

    **Stored as a fraction, never as a percent of one atmosphere.** The
    published sources express MAC-awake as a ratio to MAC (Katoh 1993
    explicitly "as a ratio to age-adjusted MAC"), and the fraction is the only
    form that stays correct if `mac_percent` changes or is ever made
    age-aware. Recording the absolute percent instead would silently bind the
    value to whichever MAC its own population was measured against:
    desflurane's 2.60% is anchored to a MAC of 7.25% and this project stores
    6.0%, so the absolute figure divided by the stored MAC reads 0.433 against
    a published 0.36. `docs/MODEL.md` § "MAC-awake as a chart reference"
    carries that.

    `mac_reference_basis` is prose rather than a number because the two
    denominators are not the same kind of thing — Katoh's is each patient's
    own age-adjusted MAC, Chortkoff's a single population figure — and a
    fraction with no stated denominator is the "correct number with the wrong
    context" failure `CLAUDE.md` names.
    """

    fraction_of_mac: float
    standard_deviation_fraction_of_mac: float
    mac_reference_basis: str


@dataclass(frozen=True, slots=True)
class AgentParameters:
    """Validated partition parameters for one volatile anesthetic.

    Built by `parse_agent_parameters()` from `_AgentPayload`, which validates
    the file and is discarded. The two carry overlapping field names on
    purpose; `_StrictPayload` says why that is a boundary rather than
    duplication.
    """

    schema_version: int
    id: str
    display_name: str
    blood_gas_partition_coefficient: float
    vessel_rich_tissue_gas_partition_coefficient: float
    muscle_tissue_gas_partition_coefficient: float
    fat_tissue_gas_partition_coefficient: float
    max_delivered_concentration_percent: float
    mac_percent: float
    mac_awake: MacAwakeReference
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
    """Validated physiologic defaults for the v0.1.0 reference adult.

    Built by `parse_reference_adult_parameters()` from
    `_ReferenceAdultPayload`, which validates the file and is discarded; see
    `_StrictPayload` for why the pair exists.
    """

    schema_version: int
    id: str
    display_name: str
    weight_kg: float
    alveolar_gas_volume_l: float
    venous_pool_volume_l: float
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


def _validate_nonempty_string(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("must be a nonempty string")

    return value


def _validate_schema_version(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("schema_version must be an integer")

    if value != SUPPORTED_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported schema_version: {value}; expected {SUPPORTED_SCHEMA_VERSION}"
        )

    return value


def _validate_positive_finite(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("must be a number")

    numeric_value = float(value)

    if not isfinite(numeric_value) or numeric_value <= 0.0:
        raise ValueError("must be positive and finite")

    return numeric_value


def _validate_positive_fraction(value: object) -> float:
    numeric_value = _validate_positive_finite(value)

    if numeric_value > 1.0:
        raise ValueError("must not exceed 1")

    return numeric_value


def _validate_positive_percent(value: object) -> float:
    numeric_value = _validate_positive_finite(value)

    if numeric_value > 100.0:
        raise ValueError("must not exceed 100")

    return numeric_value


NonEmptyString = Annotated[str, BeforeValidator(_validate_nonempty_string)]
SchemaVersion = Annotated[int, BeforeValidator(_validate_schema_version)]
PositiveFinite = Annotated[float, BeforeValidator(_validate_positive_finite)]
PositiveFraction = Annotated[float, BeforeValidator(_validate_positive_fraction)]
PositivePercent = Annotated[float, BeforeValidator(_validate_positive_percent)]


class _StrictPayload(BaseModel):
    """Base for every parameter-file schema: the load-time half of the pair.

    **Why a `_...Payload` exists beside a public dataclass.** Each payload
    model below is paired with a public, frozen, Pydantic-independent type -
    `_AgentPayload` with `AgentParameters`, `_ReferenceAdultPayload` with
    `ReferenceAdultParameters` - and the pairing is deliberate rather than
    duplication that nobody got round to removing (PL-007). Two things follow
    from it, and neither survives merging the two:

    - *The rest of `core/` never imports Pydantic.* A payload is a load-time
      artifact: it validates one JSON document and is then discarded by
      `parse_agent_parameters()` / `parse_reference_adult_parameters()`, which
      are the seam. What every other module holds is the plain dataclass. Put
      the validators on the public type instead and the validation library
      becomes a dependency of the compartments, the controller and the tests.
    - *The two shapes are not the same shape.* A payload mirrors the file;
      the public type has the form the model wants. `_AgentPayload` nests
      three coefficients under `tissue_gas_partition_coefficients` where
      `AgentParameters` carries them flat and adds the tissue:blood ratios it
      derives from them; `_ReferenceAdultPayload` nests six values under
      `tissue_groups` where `ReferenceAdultParameters` carries them flat. The
      seam functions are that mapping. Fields that look copied are the subset
      where the file's shape and the model's happen to agree.

    So a change that collapses a pair is not a simplification: it couples
    `core/` to the validation library, and it lets the JSON layout dictate
    the type the simulation reads.

    **Strictness.** Pydantic's default is to discard an unknown key
    silently, which in this repository means a data file can document one
    model while the app runs another: a renamed field, a units-suffixed
    variant, a typo'd duplicate, or a field from a schema version this
    loader does not implement all load clean and take no effect. A
    misspelling that *removes* a required key is already caught as a missing
    field; this closes the other half.

    Every payload model below inherits from this rather than setting
    `model_config` itself, so a seventh model added later is strict by
    default instead of by being remembered. Two tests in
    `tests/unit/test_parameters.py` walk this class's subclasses: one
    enforces that strictness, the other that each subclass carries a
    docstring, so a payload added later arrives explained rather than
    looking like duplication to whoever meets it next.

    The first bullet above is checked rather than asserted:
    `tools/import_boundary_check.py`, in `make check`, fails the build on a
    `pydantic` import anywhere under `src/anesthesia_sim/` other than this
    module, and names this module as the sole exception. Before it, the
    claim was prose that nothing re-measured - so a leak into a compartment
    would have left this paragraph reading as verified while being false,
    which is worse than the coupling it describes (PL-Y0RZ).
    """

    model_config = ConfigDict(extra="forbid")


class _SourcePayload(_StrictPayload):
    """Load-time schema for one `sources` entry, discarded into `SourceReference`."""

    citation: NonEmptyString
    url: NonEmptyString
    note: NonEmptyString


def _validate_sources_nonempty(value: list[_SourcePayload]) -> list[_SourcePayload]:
    if not value:
        raise ValueError("sources must contain at least one reference")

    return value


Sources = Annotated[list[_SourcePayload], BeforeValidator(_validate_sources_nonempty)]


class _TissueGasPartitionCoefficientsPayload(_StrictPayload):
    """The file's nesting for three coefficients `AgentParameters` holds flat."""

    vessel_rich: PositiveFinite
    muscle: PositiveFinite
    fat: PositiveFinite


class _MacAwakePayload(_StrictPayload):
    """Load-time schema for one agent's `mac_awake`, discarded into `MacAwakeReference`."""

    fraction_of_mac: PositiveFraction
    standard_deviation_fraction_of_mac: PositiveFraction
    mac_reference_basis: NonEmptyString

    @model_validator(mode="after")
    def _band_must_lie_strictly_between_zero_and_one_mac(self) -> _MacAwakePayload:
        """Reject a band that reaches zero or 1 MAC.

        Both edges are drawn, so both are values a reader acts on. A lower
        edge at or below zero is not a concentration, and an upper edge at or
        above 1 MAC would put the awakening reference on top of the
        anesthetizing one — which is not a rendering nuisance but a
        contradiction of what MAC-awake is, and would erase the very decrement
        the two references exist to show.
        """

        lower = self.fraction_of_mac - self.standard_deviation_fraction_of_mac
        upper = self.fraction_of_mac + self.standard_deviation_fraction_of_mac

        if lower <= 0.0:
            raise ValueError(
                "fraction_of_mac minus standard_deviation_fraction_of_mac must be positive "
                f"({self.fraction_of_mac} - {self.standard_deviation_fraction_of_mac})"
            )

        if upper >= 1.0:
            raise ValueError(
                "fraction_of_mac plus standard_deviation_fraction_of_mac must be below 1 MAC "
                f"({self.fraction_of_mac} + {self.standard_deviation_fraction_of_mac})"
            )

        return self


class _AgentPayload(_StrictPayload):
    """Load-time schema for `data/agents/*.json`, discarded into `AgentParameters`.

    See `_StrictPayload` for why the pair exists and is not duplication.
    """

    schema_version: SchemaVersion
    id: NonEmptyString
    display_name: NonEmptyString
    blood_gas_partition_coefficient: PositiveFinite
    tissue_gas_partition_coefficients: _TissueGasPartitionCoefficientsPayload
    max_delivered_concentration_percent: PositivePercent
    mac_percent: PositivePercent
    mac_awake: _MacAwakePayload
    sources: Sources

    @model_validator(mode="after")
    def _mac_percent_must_not_exceed_vaporizer_max(self) -> _AgentPayload:
        """Reject an agent whose 1 MAC its own vaporizer cannot deliver.

        This is a `model_validator`, not a `field_validator` reading
        `info.data`: a field validator only sees fields declared before it,
        so reordering the two fields above would silently turn the check
        into a no-op. The MAC start in `AgentUptakeSystem.for_agent()`
        depends on this holding.
        """

        if self.mac_percent > self.max_delivered_concentration_percent:
            raise ValueError(
                "mac_percent must not exceed max_delivered_concentration_percent "
                f"({self.mac_percent} > {self.max_delivered_concentration_percent})"
            )

        return self


class _TissueGroupPayload(_StrictPayload):
    """The file's nesting for one tissue group; `ReferenceAdultParameters` is flat."""

    volume_l: PositiveFinite
    perfusion_fraction: PositiveFraction


class _TissueGroupsPayload(_StrictPayload):
    """The file's nesting for the three tissue groups, flattened by the seam."""

    vessel_rich: _TissueGroupPayload
    muscle: _TissueGroupPayload
    fat: _TissueGroupPayload


class _ReferenceAdultPayload(_StrictPayload):
    """Load-time schema for `data/patients/*.json`, discarded into `ReferenceAdultParameters`.

    See `_StrictPayload` for why the pair exists and is not duplication.
    """

    schema_version: SchemaVersion
    id: NonEmptyString
    display_name: NonEmptyString
    weight_kg: PositiveFinite
    alveolar_gas_volume_l: PositiveFinite
    venous_pool_volume_l: PositiveFinite
    default_alveolar_ventilation_l_min: PositiveFinite
    default_cardiac_output_l_min: PositiveFinite
    tissue_groups: _TissueGroupsPayload
    sources: Sources

    @field_validator("tissue_groups")
    @classmethod
    def _perfusion_fractions_must_sum_to_one(
        cls, value: _TissueGroupsPayload
    ) -> _TissueGroupsPayload:
        total = (
            value.vessel_rich.perfusion_fraction
            + value.muscle.perfusion_fraction
            + value.fat.perfusion_fraction
        )

        if abs(total - 1.0) > FLOW_FRACTION_TOLERANCE:
            raise ValueError("tissue perfusion fractions must sum to 1")

        return value


def _sources_to_tuple(sources: list[_SourcePayload]) -> tuple[SourceReference, ...]:
    return tuple(
        SourceReference(citation=source.citation, url=source.url, note=source.note)
        for source in sources
    )


def parse_agent_parameters(payload: object) -> AgentParameters:
    """Validate an agent-data payload and return immutable parameters."""

    try:
        model = _AgentPayload.model_validate(payload)
    except PydanticValidationError as error:
        raise SimulationConfigurationError(str(error)) from error

    coefficients = model.tissue_gas_partition_coefficients

    return AgentParameters(
        schema_version=model.schema_version,
        id=model.id,
        display_name=model.display_name,
        blood_gas_partition_coefficient=model.blood_gas_partition_coefficient,
        vessel_rich_tissue_gas_partition_coefficient=coefficients.vessel_rich,
        muscle_tissue_gas_partition_coefficient=coefficients.muscle,
        fat_tissue_gas_partition_coefficient=coefficients.fat,
        max_delivered_concentration_percent=(model.max_delivered_concentration_percent),
        mac_percent=model.mac_percent,
        mac_awake=MacAwakeReference(
            fraction_of_mac=model.mac_awake.fraction_of_mac,
            standard_deviation_fraction_of_mac=(model.mac_awake.standard_deviation_fraction_of_mac),
            mac_reference_basis=model.mac_awake.mac_reference_basis,
        ),
        sources=_sources_to_tuple(model.sources),
    )


def parse_reference_adult_parameters(payload: object) -> ReferenceAdultParameters:
    """Validate a reference-adult payload and return immutable parameters."""

    try:
        model = _ReferenceAdultPayload.model_validate(payload)
    except PydanticValidationError as error:
        raise SimulationConfigurationError(str(error)) from error

    tissue_groups = model.tissue_groups

    return ReferenceAdultParameters(
        schema_version=model.schema_version,
        id=model.id,
        display_name=model.display_name,
        weight_kg=model.weight_kg,
        alveolar_gas_volume_l=model.alveolar_gas_volume_l,
        venous_pool_volume_l=model.venous_pool_volume_l,
        default_alveolar_ventilation_l_min=model.default_alveolar_ventilation_l_min,
        default_cardiac_output_l_min=model.default_cardiac_output_l_min,
        vessel_rich_volume_l=tissue_groups.vessel_rich.volume_l,
        vessel_rich_perfusion_fraction=tissue_groups.vessel_rich.perfusion_fraction,
        muscle_volume_l=tissue_groups.muscle.volume_l,
        muscle_perfusion_fraction=tissue_groups.muscle.perfusion_fraction,
        fat_volume_l=tissue_groups.fat.volume_l,
        fat_perfusion_fraction=tissue_groups.fat.perfusion_fraction,
        sources=_sources_to_tuple(model.sources),
    )


def _load_packaged_json(package: str, filename: str) -> object:
    resource = files(package).joinpath(filename)

    with resource.open("r", encoding="utf-8") as stream:
        payload: object = json.load(stream)

    return payload


AGENT_DATA_FILENAMES: dict[str, str] = {
    "sevoflurane": "sevoflurane.json",
    "isoflurane": "isoflurane.json",
    "desflurane": "desflurane.json",
}


def load_agent_parameters(agent_id: str) -> AgentParameters:
    """Load and validate one built-in agent definition by id."""

    filename = AGENT_DATA_FILENAMES.get(agent_id)

    if filename is None:
        raise SimulationConfigurationError(
            f"unknown agent_id: {agent_id!r}; expected one of {sorted(AGENT_DATA_FILENAMES)}"
        )

    payload = _load_packaged_json("anesthesia_sim.data.agents", filename)
    parameters = parse_agent_parameters(payload)

    if parameters.id != agent_id:
        raise SimulationConfigurationError(
            f"{filename} declares id {parameters.id!r}, expected {agent_id!r}"
        )

    return parameters


def load_sevoflurane_parameters() -> AgentParameters:
    """Load and validate the built-in sevoflurane definition."""

    return load_agent_parameters("sevoflurane")


def load_reference_adult_parameters() -> ReferenceAdultParameters:
    """Load and validate the built-in v0.1.0 reference adult."""

    payload = _load_packaged_json("anesthesia_sim.data.patients", "reference_adult.json")
    return parse_reference_adult_parameters(payload)
