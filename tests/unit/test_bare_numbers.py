"""Every bare `float` or `int` at a public boundary in `core/` is on one list, with its reason.

A checked type, such as `CardiacOutput`, proves that its range check ran. A
bare `float` proves nothing, so whether it was checked depends on who reads the
call chain. An earlier item (`PL-ZGYX`) swept `core/` once for bare numbers and
built no standing check. Four items found more after it closed (`PL-LHCL`).

These tests read the source of every module in `core/`. They collect each
public parameter, dataclass field and return value whose annotation names
`float` or `int`, alone or inside another type such as `tuple[float, ...]`. An
annotation also counts as bare when it names an alias such as
`Matrix = tuple[tuple[float, ...], ...]` or a `NewType` over `float`, because
neither checks anything. Each bare number the tests find must appear in
`BARE_NUMBERS` below with the reason it is bare. A name is public unless it
starts with one underscore. A method such as `__new__` is public, because it
is how a caller builds the type.

A new bare number fails the first test until it is given a checked type or
listed. The count `MOST_BARE_NUMBERS` must equal the length of the list, so
adding an entry also means raising that count, where a reviewer sees it. One
item (`PL-LHCL`) gives the listed numbers checked types, one quantity at a time,
and removes each entry and lowers the count as it does.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable, Iterator
from pathlib import Path

import pytest

from anesthesia_sim import core

CORE = Path(core.__file__).resolve().parent

BARE_TYPES = frozenset({"float", "int"})

# The first three reasons are permanent. A number has to be bare where it is
# checked, and where a checked type hands back the plain number it stores.
THE_CHECK = (
    "This is the check itself: a checked type's constructor, or a guard, takes the bare "
    "number and refuses it or passes it."
)
PLAIN_NUMBER = (
    "The plain number that a checked type's constructor stores, or that loading the type "
    "from a pickle or a copy passes back to that constructor."
)
SHOWN_IN_A_REFUSAL = "A count that a refusal message shows, which may be the value refused."

# Each of the other reasons names a quantity that one item (`PL-LHCL`) has
# yet to give a checked type. An entry leaves the list when its quantity
# gets one. A reason says that something checks the number only where that
# check refused NaN or a value outside its range when it was run on 2026-11-11.
COMPARED_BY_A_GUARD = (
    "A number that a guard compares with another number or with a limit. The guard "
    "leaves the number's own check to its caller, so it accepts NaN. The amounts, "
    "capacities and concentrations that these guards take are still to get checked types "
    "(PL-LHCL)."
)
COMPARTMENT_STEP = (
    "A compartment's own step for its closed form. It is still to get a checked type (PL-LHCL)."
)
INSTANT_OR_WINDOW = (
    "An instant, an interval, or a window's bound, spacing or column count. It is still to "
    "get a checked type (PL-LHCL)."
)
STATE_VECTOR = (
    "A state vector of amounts and fractions. It is to get a checked type with the agent "
    "amounts (PL-LHCL)."
)
MATRIX = (
    "A matrix of plain floats: the system matrix, or a propagator built from it. Nothing "
    "checks its entries, so multiply returns NaN for a NaN operand. It is to get a checked "
    "type with the state vectors (PL-LHCL)."
)
STORED_PARAMETER = (
    "A stored parameter, a bound of a stored range, or a conversion of one. The loader "
    "checks a value read from a data file, and some records built directly do not: "
    "MacAwakeReference accepts NaN. It is still to get a checked type (PL-LHCL)."
)
CLOSED_FORM = (
    "An argument or result of the exponential closed form, which states its own valid "
    "inputs. It is to get a checked type with the amounts and steps it is called with "
    "(PL-LHCL)."
)
AGENT_AMOUNT = (
    "An agent amount in litres, or a total or error of amounts, on a compartment, the "
    "validator or a method. It is to get a checked type last, after a measurement of what "
    "a checked type costs at each step (PL-LHCL)."
)
UNCHECKED_AMOUNT = (
    "An agent amount on a state or result record that checks nothing, so the record can "
    "be built with NaN or a negative amount. It is to get a checked type with the other "
    "agent amounts (PL-LHCL)."
)
DERIVED = (
    "A value that the code computes from other values. Arithmetic on a checked type "
    "returns a plain float, so the result carries no proof. It is to get a type that only "
    "its derivation builds (PL-LHCL)."
)

LISTED: dict[str, dict[str, tuple[str, ...]]] = {
    THE_CHECK: {
        "agent_simulation_validation": (
            "AgentSimulationValidator.require_valid_agent_accounting(currently_stored_agent_l)",
        ),
        "blood_flow": ("PerfusionFraction.__new__(perfusion_fraction)",),
        "checked_number": ("negative_zero_as_zero(value)",),
        "concentration": (
            "Fraction.__new__(fraction)",
            "MacPercent.__new__(percent)",
            "Percent.__new__(percent)",
        ),
        "numerical_envelope": (
            "CompartmentVolume.__new__(volume_l)",
            "PartitionCoefficient.__new__(coefficient)",
        ),
        "simulation_step": (
            "SimulationStep.__new__(seconds)",
            "require_at_least_the_smallest_step(simulation_step_s)",
            "require_supported_simulation_step(simulation_step_s)",
        ),
        "supported_ranges": (
            "AlveolarVentilation.__new__(alveolar_ventilation_l_min)",
            "CardiacOutput.__new__(cardiac_output_l_min)",
            "CaseInstant.__new__(instant_s)",
            "FreshGasFlow.__new__(fresh_gas_flow_l_min)",
            "StepCount.__new__(step_count)",
            "require_compartment_step(simulation_step_s)",
            "require_supported_alveolar_ventilation(alveolar_ventilation_l_min)",
            "require_supported_cardiac_output(cardiac_output_l_min)",
            "require_supported_case_instant(instant_s)",
            "require_supported_fresh_gas_flow(fresh_gas_flow_l_min)",
        ),
        "validation": ("require_nonnegative_finite(value)", "require_positive_finite(value)"),
    },
    COMPARED_BY_A_GUARD: {
        "parameters": ("require_perfusion_fractions_sum_to_one(total_perfusion_fraction)",),
        "supported_ranges": (
            "require_held_within_input_ceiling(capacity_l)",
            "require_held_within_input_ceiling(held_l)",
            "require_within_input_ceiling(concentration)",
        ),
        "validation": (
            "require_a_capacity_with_room_for_the_agent(agent_amount_l)",
            "require_a_capacity_with_room_for_the_agent(capacity_per_litre)",
            "require_a_capacity_with_room_for_the_agent(value)",
            "require_a_capacity_with_room_for_the_agent(volume_l)",
            "require_room_for_the_agent_held(agent_amount_l)",
            "require_room_for_the_agent_held(capacity_l)",
            "require_room_for_the_agent_held(value)",
            "require_within_the_capacity(agent_amount_l)",
            "require_within_the_capacity(capacity_l)",
        ),
    },
    PLAIN_NUMBER: {
        "checked_number": (
            "CheckedQuantity.__reduce__ -> return",
            "negative_zero_as_zero -> return",
        )
    },
    SHOWN_IN_A_REFUSAL: {"supported_ranges": ("describe_count(count)",)},
    COMPARTMENT_STEP: {
        "blood": ("VenousBloodCompartment.advance(simulation_step_s)",),
        "circuit": (
            "BreathingCircuit.advance(simulation_step_s)",
            "BreathingCircuit.advance_fresh_gas(simulation_step_s)",
        ),
        "tissue": ("TissueGroup.advance(simulation_step_s)",),
    },
    INSTANT_OR_WINDOW: {
        "matrix_exponential": ("matrix_exponential(interval_s)",),
        "run_definition": (
            "RunDefinition.evaluate(columns)",
            "RunDefinition.evaluate(start_s)",
            "RunDefinition.evaluate(stop_s)",
            "RunDefinition.evaluate_anchored(spacing_s)",
            "RunDefinition.evaluate_anchored(start_s)",
            "RunDefinition.evaluate_anchored(stop_s)",
            "RunDefinition.reaching_segment_at(instant_s)",
            "RunDefinition.segment_at(instant_s)",
            "RunDefinition.state_at(instant_s)",
            "SampledWindow.times_s",
        ),
    },
    STATE_VECTOR: {
        "matrix_exponential": ("propagate -> return", "propagate(state)"),
        "run_definition": (
            "DisplayState.values",
            "Keyframe.state",
            "RunDefinition.__init__(initial_state)",
            "RunDefinition.state_at -> return",
        ),
        "uptake_system": (
            "AgentUptakeSystem.resume_at(state)",
            "AgentUptakeSystem.state_vector -> return",
        ),
    },
    MATRIX: {
        "governing_equations": ("build_system_matrix -> return",),
        "matrix_exponential": (
            "matrix_exponential -> return",
            "matrix_exponential(matrix)",
            "multiply -> return",
            "multiply(left)",
            "multiply(right)",
            "propagate(propagator)",
        ),
    },
    STORED_PARAMETER: {
        "circuit": (
            "BreathingCircuit.accepted_fresh_gas_flow_range_l_min -> return",
            "DeliverableFreshGasFlowRange.maximum_l_min",
            "DeliverableFreshGasFlowRange.minimum_l_min",
        ),
        "liquid_agent": (
            "LiquidDensity.g_ml",
            "LiquidDensity.measured_at_celsius",
            "LiquidDensity.standard_deviation_g_ml",
            "liquid_volume_ml -> return",
            "liquid_volume_ml(vapour_per_liquid)",
            "liquid_volume_ml(vapour_volume_l)",
            "vapour_volume_per_liquid_volume -> return",
            "vapour_volume_per_liquid_volume(molar_mass_g_mol)",
        ),
        "parameters": (
            "AgentParameters.molar_mass_g_mol",
            "AgentParameters.schema_version",
            "AgentParameters.vapour_volume_per_liquid_volume -> return",
            "BreathingCircuitParameters.default_fresh_gas_flow_l_min",
            "BreathingCircuitParameters.schema_version",
            "MacAwakeReference.fraction_of_mac",
            "MacAwakeReference.standard_deviation_fraction_of_mac",
            "ReferenceAdultParameters.default_alveolar_ventilation_l_min",
            "ReferenceAdultParameters.default_cardiac_output_l_min",
            "ReferenceAdultParameters.schema_version",
            "ReferenceAdultParameters.weight_kg",
            "SupportedSchemaVersions.current",
            "SupportedSchemaVersions.minimum",
            "mac_awake_band_fractions -> return",
            "mac_awake_band_fractions(fraction_of_mac)",
            "mac_awake_band_fractions(standard_deviation_fraction_of_mac)",
        ),
    },
    CLOSED_FORM: {
        "exponential_approach": (
            "exponential_approach -> return",
            "exponential_approach(equilibrium)",
            "exponential_approach(initial)",
            "exponential_approach(step_s)",
            "exponential_approach(time_constant_s)",
            "exponential_approach_in_time_constants -> return",
            "exponential_approach_in_time_constants(equilibrium)",
            "exponential_approach_in_time_constants(initial)",
            "exponential_approach_in_time_constants(time_constants_elapsed)",
        )
    },
    AGENT_AMOUNT: {
        "agent_simulation_validation": (
            "AgentSimulationValidator.check_agent_accounting(currently_stored_agent_l)",
            "AgentSimulationValidator.delivered_agent_l",
            "AgentSimulationValidator.delivered_compensation_l",
            "AgentSimulationValidator.exhausted_agent_l",
            "AgentSimulationValidator.exhausted_compensation_l",
            "AgentSimulationValidator.initial_agent_l",
            "AgentSimulationValidator.record_external_agent_transfer(delivered_agent_l)",
            "AgentSimulationValidator.record_external_agent_transfer(exhausted_agent_l)",
            "AgentSimulationValidator.reset(initial_agent_l)",
        ),
        "alveolar": ("AlveolarCompartment.agent_amount_l",),
        "blood": (
            "VenousBloodCompartment.advance -> return",
            "VenousBloodCompartment.agent_amount_l",
        ),
        "circuit": (
            "BreathingCircuit.agent_amount_l -> return",
            "BreathingCircuit.set_agent_amount(agent_amount_l)",
            "BreathingCircuitState.agent_amount_l -> return",
        ),
        "patient": ("PatientCompartments.total_agent_amount_l -> return",),
        "tissue": ("TissueGroup.advance -> return", "TissueGroup.agent_amount_l"),
        "uptake_system": (
            "AgentUptakeSystem.resume_at(initial_agent_l)",
            "AgentUptakeSystem.total_stored_agent_l -> return",
        ),
    },
    UNCHECKED_AMOUNT: {
        "agent_simulation_validation": (
            "AgentSimulationValidationResult.absolute_error_l",
            "AgentSimulationValidationResult.currently_stored_agent_l",
            "AgentSimulationValidationResult.delivered_agent_l",
            "AgentSimulationValidationResult.exhausted_agent_l",
            "AgentSimulationValidationResult.initial_agent_l",
            "AgentSimulationValidationResult.unaccounted_agent_l",
            "AgentSimulationValidatorState.delivered_agent_l",
            "AgentSimulationValidatorState.delivered_compensation_l",
            "AgentSimulationValidatorState.exhausted_agent_l",
            "AgentSimulationValidatorState.exhausted_compensation_l",
            "AgentSimulationValidatorState.initial_agent_l",
        ),
        "alveolar": ("AlveolarCompartmentState.agent_amount_l",),
        "blood": ("VenousBloodCompartmentState.agent_amount_l",),
        "circuit": ("FreshGasExchange.delivered_agent_l", "FreshGasExchange.exhausted_agent_l"),
        "tissue": ("TissueGroupState.agent_amount_l",),
        "uptake_system": (
            "UptakeStepResult.circuit_to_alveolar_agent_l",
            "UptakeStepResult.patient_agent_change_l",
        ),
    },
    DERIVED: {
        "agent_simulation_validation": ("AgentSimulationValidationResult.relative_error",),
        "alveolar": ("AlveolarCompartment.partial_pressure_fraction -> return",),
        "blood": (
            "VenousBloodCompartment.capacity_l -> return",
            "VenousBloodCompartment.partial_pressure_fraction -> return",
            "VenousBloodCompartment.time_constant_s -> return",
        ),
        "circuit": ("BreathingCircuit.time_constant_s -> return",),
        "governing_equations": (
            "TissueGroupEquationSettings.blood_flow_l_s -> return",
            "TissueGroupEquationSettings.washin_rate_s -> return",
            "UptakeEquationSettings.alveolar_ventilation_l_s -> return",
            "UptakeEquationSettings.cardiac_output_l_s -> return",
            "UptakeEquationSettings.fresh_gas_flow_l_s -> return",
        ),
        "parameters": ("ReferenceAdultParameters.total_perfusion_fraction -> return",),
        "patient": (
            "PatientCompartments.mixed_venous_partial_pressure_fraction -> return",
            "PatientCompartments.tissue_return_partial_pressure_fraction -> return",
            "PatientCompartments.total_perfusion_fraction -> return",
        ),
        "supported_ranges": ("maximum_step_count -> return",),
        "tissue": (
            "TissueGroup.capacity_l -> return",
            "TissueGroup.partial_pressure_fraction -> return",
            "TissueGroup.time_constant_s -> return",
            "TissueGroup.venous_outflow_partial_pressure_fraction -> return",
        ),
        "uptake_system": ("AgentUptakeSystem.settings_key -> return",),
    },
}

# Each key is `module.name`, and its value is the reason it is bare.
BARE_NUMBERS: dict[str, str] = {
    f"{module}.{name}": reason
    for reason, modules in LISTED.items()
    for module, names in modules.items()
    for name in names
}

# This count equals the length of `BARE_NUMBERS`. It was 173 on 2026-11-11,
# when the list was written. Giving a quantity a checked type lowers it. A
# change that raises it shows a reviewer that the change adds a bare number.
# The blood flow and the perfusion fraction took it to 164 (`PL-GKG4`).
MOST_BARE_NUMBERS = 164


def _names_a_bare_number(
    annotation: ast.expr | None, bare_names: frozenset[str] = BARE_TYPES
) -> bool:
    """Return whether an annotation names `float`, `int` or an alias of one anywhere in it.

    The names to look for (`bare_names`) are `float` and `int` unless the
    caller passes more. The walk passes those two and each alias found by
    searching the modules (`_bare_type_names`). A quoted annotation is parsed
    and read the same way. One that does not parse is treated as bare, so that
    a person looks at it instead of the test passing it.
    """

    if annotation is None:
        return False

    for node in ast.walk(annotation):
        if isinstance(node, ast.Name) and node.id in bare_names:
            return True

        if isinstance(node, ast.Attribute) and node.attr in bare_names:
            return True

        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            try:
                quoted = ast.parse(node.value, mode="eval").body
            except SyntaxError:
                return True

            if _names_a_bare_number(quoted, bare_names):
                return True

    return False


def _is_a_type_expression(value: ast.expr) -> bool:
    """Return whether a module-level value is written as a type.

    A type is a name, a subscript, a union or a `NewType`. A call such as
    `float("inf")` builds a number, so it is not a type.
    """

    if isinstance(value, (ast.Name, ast.Attribute, ast.Subscript)):
        return True

    if isinstance(value, ast.BinOp) and isinstance(value.op, ast.BitOr):
        return True

    if isinstance(value, ast.Call):
        called = value.func
        name = called.attr if isinstance(called, ast.Attribute) else getattr(called, "id", "")
        return name == "NewType"

    return False


def _aliases_in(source: str, bare_names: frozenset[str]) -> set[str]:
    """Return each module-level name that one module assigns to a type naming a bare number.

    Two examples are `Matrix = tuple[tuple[float, ...], ...]` and
    `MacMultiple = NewType("MacMultiple", float)`. Neither checks anything, so
    a parameter annotated with one is as bare as a `float`. A class is not an
    alias, because a checked type is a class whose constructor runs the check.
    """

    aliases: set[str] = set()

    for statement in _statements(ast.parse(source).body):
        if isinstance(statement, ast.TypeAlias):
            name, value = statement.name.id, statement.value
        elif (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
        ):
            name, value = statement.targets[0].id, statement.value
        elif (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.value is not None
        ):
            name, value = statement.target.id, statement.value
        else:
            continue

        if _is_a_type_expression(value) and _names_a_bare_number(value, bare_names):
            aliases.add(name)

    return aliases


def _bare_type_names(sources: Iterable[str]) -> frozenset[str]:
    """Return `float`, `int` and every alias of them that the given modules define.

    An alias may be written in terms of another alias, so the search repeats
    until it finds no new name. A name found in one module counts in all of
    them, because one module imports another's alias.
    """

    sources = tuple(sources)
    names = BARE_TYPES

    while True:
        wider = names.union(*(_aliases_in(source, names) for source in sources))

        if wider == names:
            return names

        names = wider


def _is_public(name: str) -> bool:
    """Return whether a name has no leading underscore, or is a method such as `__new__`."""

    return not name.startswith("_") or (name.startswith("__") and name.endswith("__"))


def _statements(body: list[ast.stmt]) -> Iterator[ast.stmt]:
    """Yield the statements of a module or class body, including those inside an `if` block.

    Each mutable record defines its `__setattr__` under `if not TYPE_CHECKING:`,
    so a walk that skipped `if` blocks would miss it.
    """

    for statement in body:
        if isinstance(statement, ast.If):
            yield from _statements(statement.body)
            yield from _statements(statement.orelse)
        else:
            yield statement


def _in_function(
    owner: str, function: ast.FunctionDef | ast.AsyncFunctionDef, bare_names: frozenset[str]
) -> Iterator[str]:
    """Yield a key for each bare parameter of a function, and one for a bare return value."""

    arguments = function.args
    parameters = [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]

    if arguments.vararg is not None:
        parameters.append(arguments.vararg)

    if arguments.kwarg is not None:
        parameters.append(arguments.kwarg)

    for parameter in parameters:
        if _names_a_bare_number(parameter.annotation, bare_names):
            yield f"{owner}{function.name}({parameter.arg})"

    if _names_a_bare_number(function.returns, bare_names):
        yield f"{owner}{function.name} -> return"


def bare_numbers_in(module: str, source: str, bare_names: frozenset[str] | None = None) -> set[str]:
    """Return a key for each bare number at a public boundary in one module's source.

    The keys take three forms: `module.Class.method(parameter)` for a
    parameter, `module.Class.field` for a field, and
    `module.function -> return` for a return value. The aliases that other
    modules define are passed in as `bare_names`. Without `bare_names`, the
    walk uses the aliases that this source defines.
    """

    if bare_names is None:
        bare_names = _bare_type_names([source])

    found: set[str] = set()

    for statement in _statements(ast.parse(source).body):
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _is_public(statement.name):
                found.update(_in_function(f"{module}.", statement, bare_names))
        elif isinstance(statement, ast.ClassDef) and _is_public(statement.name):
            owner = f"{module}.{statement.name}."

            for member in _statements(statement.body):
                if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if _is_public(member.name):
                        found.update(_in_function(owner, member, bare_names))
                elif (
                    isinstance(member, ast.AnnAssign)
                    and isinstance(member.target, ast.Name)
                    and _is_public(member.target.id)
                    and _names_a_bare_number(member.annotation, bare_names)
                ):
                    found.add(f"{owner}{member.target.id}")

    return found


def _bare_numbers_in_core() -> set[str]:
    sources = {path.stem: path.read_text(encoding="utf-8") for path in sorted(CORE.glob("*.py"))}
    bare_names = _bare_type_names(sources.values())
    found: set[str] = set()

    for module, source in sources.items():
        found |= bare_numbers_in(module, source, bare_names)

    return found


def test_every_bare_number_in_core_is_listed_with_its_reason() -> None:
    unlisted = sorted(_bare_numbers_in_core() - BARE_NUMBERS.keys())

    assert not unlisted, (
        "these public parameters, fields or returns in core/ are a bare float or int. Give each "
        "a checked type (.claude/rules/core-domain.md), or add it to LISTED in "
        f"tests/unit/test_bare_numbers.py with the reason it is bare: {unlisted}"
    )


def test_the_list_names_no_number_that_is_gone_or_typed() -> None:
    stale = sorted(BARE_NUMBERS.keys() - _bare_numbers_in_core())

    assert not stale, (
        "these entries of BARE_NUMBERS name nothing that is still a bare float or int in core/. "
        f"Remove them, and lower MOST_BARE_NUMBERS to the new length: {stale}"
    )


def test_the_count_is_the_length_of_the_list() -> None:
    assert len(BARE_NUMBERS) == MOST_BARE_NUMBERS, (
        f"BARE_NUMBERS has {len(BARE_NUMBERS)} entries and MOST_BARE_NUMBERS is "
        f"{MOST_BARE_NUMBERS}. After removing entries, lower MOST_BARE_NUMBERS to the new "
        "length. After adding an entry, raise it, so that a reviewer sees that the change "
        "adds a bare number."
    )


def test_every_entry_gives_a_reason() -> None:
    without = sorted(key for key, reason in BARE_NUMBERS.items() if not reason.strip())

    assert not without, f"these entries of BARE_NUMBERS give no reason: {without}"


# The signatures below are the bare numbers that past items reported, as the
# code stood when each was filed. Each is replayed through the walk, which must
# name it. One item (`PL-GKG4`) reported a blood flow checked by hand at three
# places. Another (`PL-8W1Q`) reported that a record loaded from a pickle or a
# copy skips its constructor's checks. `tests/unit/test_record_restores.py`
# will cover that load. The record it named (`Keyframe`) is here, and its
# `state` field is the bare number. A third (`PL-HSFV`) reported the settings
# record's flows, held as `float` until they were given a checked type
# (`PL-0YYV`).
PAST_ESCAPES = """
from dataclasses import dataclass


class TissueGroup:
    def blood_flow_l_min_at(self, cardiac_output_l_min: CardiacOutput) -> float: ...

    def time_constant_s(
        self, blood_flow_l_min: float, blood_gas_partition_coefficient: PartitionCoefficient
    ) -> float: ...


class VenousBloodCompartment:
    def time_constant_s(self, blood_flow_l_min: "float") -> float: ...


@dataclass(frozen=True, slots=True)
class TissueGroupEquationSettings:
    name: str
    volume_l: CompartmentVolume
    blood_flow_l_min: float
    tissue_blood_partition_coefficient: PartitionCoefficient


@dataclass(frozen=True, slots=True)
class Keyframe:
    instant_s: CaseInstant
    state: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class UptakeEquationSettings:
    fresh_gas_flow_l_min: float
    cardiac_output_l_min: float | None


def _private_helper(value: float) -> float: ...


def require_cardiac_output(cardiac_output_l_min: object) -> None: ...
"""


def test_the_walk_names_each_bare_number_that_a_past_item_reported() -> None:
    assert bare_numbers_in("past", PAST_ESCAPES) == {
        "past.TissueGroup.blood_flow_l_min_at -> return",
        "past.TissueGroup.time_constant_s(blood_flow_l_min)",
        "past.TissueGroup.time_constant_s -> return",
        "past.VenousBloodCompartment.time_constant_s(blood_flow_l_min)",
        "past.VenousBloodCompartment.time_constant_s -> return",
        "past.TissueGroupEquationSettings.blood_flow_l_min",
        "past.Keyframe.state",
        "past.UptakeEquationSettings.fresh_gas_flow_l_min",
        "past.UptakeEquationSettings.cardiac_output_l_min",
    }


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("def advance(step_s: SimulationStep) -> Fraction: ...", set()),
        ("def advance(*amounts_l: float) -> None: ...", {"m.advance(amounts_l)"}),
        ("def advance(*, step_s: int = 1) -> None: ...", {"m.advance(step_s)"}),
        ("def advance(**flows: dict[str, float]) -> None: ...", {"m.advance(flows)"}),
        ("def read() -> Sequence[int] | None: ...", {"m.read -> return"}),
        ("class _Hidden:\n    amount_l: float", set()),
        ("class Shown:\n    _amount_l: float", set()),
        (
            "class Shown:\n    if not TYPE_CHECKING:\n        def __new__(cls, value: float): ...",
            {"m.Shown.__new__(value)"},
        ),
        (
            "Matrix = tuple[tuple[float, ...], ...]\ndef multiply(left: Matrix) -> None: ...",
            {"m.multiply(left)"},
        ),
        (
            'Amount = NewType("Amount", float)\nclass Shown:\n    amount_l: Amount',
            {"m.Shown.amount_l"},
        ),
        (
            "Litres = float\nAmounts = tuple[Litres, ...]\ndef total(held: Amounts) -> None: ...",
            {"m.total(held)"},
        ),
        ("type Litres = float\ndef read() -> Litres: ...", {"m.read -> return"}),
        ("Count: TypeAlias = int\ndef read() -> Count | None: ...", {"m.read -> return"}),
        ("class Litres(float): ...\ndef read() -> Litres: ...", set()),
        ('Dose = NewType("Dose", Fraction)\ndef read() -> Dose: ...', set()),
        ('CEILING = float("inf")\ndef read() -> CEILING: ...', set()),
    ],
)
def test_the_walk_reads_each_form_of_parameter_and_skips_private_names(
    source: str, expected: set[str]
) -> None:
    assert bare_numbers_in("m", source) == expected


def test_the_walk_follows_an_alias_that_another_module_defines() -> None:
    bare_names = _bare_type_names(["Litres = float", "from units import Litres"])

    assert bare_numbers_in("m", "def read() -> Litres: ...", bare_names) == {"m.read -> return"}
    assert bare_numbers_in("m", "def read() -> units.Litres: ...", bare_names) == {
        "m.read -> return"
    }
    assert bare_numbers_in("m", "def read() -> Litres: ...") == set()
