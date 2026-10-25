"""Every name a field guard in `core/` compares with must be a field of its class.

Seven classes in `core/` check a field when it is written, in a `__setattr__`
that compares the name being written with a string, such as
`if name == "circuit_volume_l":`. The string is a second copy of the field's
name, which the dataclass already declares. If the field is renamed and the
string is not, the guard's branch never matches again. The field then accepts
any value, a negative volume included, and nothing raises (`PL-6YKY`).

So these tests read each guard's source and check that every name it compares
with is a field of its class. A comparison the reader cannot resolve to
strings fails the test too, so a new shape of guard cannot pass unread.
"""

from __future__ import annotations

import ast
import dataclasses
import importlib
from pathlib import Path

import pytest

from anesthesia_sim import core

CORE = Path(core.__file__).resolve().parent

#: The classes in `core/` that guard their fields in `__setattr__`, counted
#: 2026-10-25. The test fails if it finds fewer, so a guard it stopped
#: finding cannot pass by being skipped.
GUARDED_CLASSES = {
    "agent_simulation_validation.AgentSimulationValidator",
    "alveolar.AlveolarCompartment",
    "blood.VenousBloodCompartment",
    "circuit.BreathingCircuit",
    "patient.PatientCompartments",
    "simulation.SimulationState",
    "tissue.TissueGroup",
}


def _strings(node: ast.expr, constants: dict[str, ast.expr]) -> list[str] | None:
    """Return the strings `node` stands for, or `None` where it is not only strings.

    `node` is a string, a tuple, list or set of strings, a `frozenset` of
    one of those, or the name of a module-level constant holding one of them.
    """

    if isinstance(node, ast.Name) and node.id in constants:
        return _strings(constants[node.id], {})

    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "frozenset"
        and len(node.args) == 1
        and not node.keywords
    ):
        return _strings(node.args[0], {})

    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]

    if isinstance(node, ast.Tuple | ast.List | ast.Set):
        found = [_strings(element, {}) for element in node.elts]

        if all(item is not None for item in found):
            return [text for item in found if item is not None for text in item]

    return None


def _methods(node: ast.ClassDef) -> list[ast.FunctionDef]:
    """Return the class's own methods, those under an `if` included and nested classes left out."""

    found = []
    pending: list[ast.stmt] = list(node.body)

    while pending:
        statement = pending.pop(0)

        if isinstance(statement, ast.FunctionDef):
            found.append(statement)
        elif isinstance(statement, ast.If):
            pending.extend(statement.body + statement.orelse)

    return found


def guarded_names(source: str) -> dict[str, list[str]]:
    """Return, for each class whose `__setattr__` compares the name written, the names it compares.

    Raises:
        ValueError: a guard compares the name written with something that is
            not a string or a constant holding strings, so this cannot say
            which field it guards.
    """

    tree = ast.parse(source)
    constants = {
        target.id: statement.value
        for statement in tree.body
        if isinstance(statement, ast.Assign)
        for target in statement.targets
        if isinstance(target, ast.Name)
    }
    guards: dict[str, list[str]] = {}

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue

        for method in _methods(node):
            if method.name != "__setattr__":
                continue

            written = method.args.args[1].arg
            names = guards.setdefault(node.name, [])

            for compare in ast.walk(method):
                if not (
                    isinstance(compare, ast.Compare)
                    and isinstance(compare.left, ast.Name)
                    and compare.left.id == written
                ):
                    continue

                for operator, comparator in zip(compare.ops, compare.comparators, strict=True):
                    if not isinstance(operator, ast.Eq | ast.NotEq | ast.In | ast.NotIn):
                        continue

                    strings = _strings(comparator, constants)

                    if strings is None:
                        raise ValueError(
                            f"{node.name}.__setattr__ line {compare.lineno} compares "
                            f"{written} with {ast.unparse(comparator)}, which is not a string"
                        )

                    names.extend(strings)

    return guards


def names_that_are_not_fields(module: object, source: str) -> list[str]:
    """Return one line for each guarded name that is not a field of its class."""

    lines = []

    for class_name, names in guarded_names(source).items():
        fields = {field.name for field in dataclasses.fields(getattr(module, class_name))}
        lines.extend(
            f"{class_name} guards {name!r}, which is not one of its fields"
            for name in names
            if name not in fields
        )

    return lines


def test_every_name_a_core_field_guard_compares_with_is_a_field() -> None:
    found = set()
    unknown = []

    for path in sorted(CORE.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        module = importlib.import_module(f"anesthesia_sim.core.{path.stem}")
        guards = guarded_names(source)
        found.update(f"{path.stem}.{name}" for name, names in guards.items() if names)
        unknown.extend(names_that_are_not_fields(module, source))

    assert unknown == []
    assert found >= GUARDED_CLASSES


GUARD = """
from dataclasses import dataclass

GROUPS = frozenset(("first", "second"))


@dataclass
class Probe:
    volume_l: float
    first: float = 0.0
    second: float = 0.0

    def __setattr__(self, name, value):
        if name == "{volume}":
            pass
        elif name in GROUPS:
            pass
        super().__setattr__(name, value)
"""


def _probe(volume: str) -> tuple[object, str]:
    source = GUARD.replace("{volume}", volume)
    namespace: dict[str, object] = {}
    exec(compile(source, "<probe>", "exec"), namespace)
    return type("ProbeModule", (), namespace), source


def test_a_guard_on_a_name_that_is_a_field_passes() -> None:
    module, source = _probe("volume_l")

    assert guarded_names(source) == {"Probe": ["volume_l", "first", "second"]}
    assert names_that_are_not_fields(module, source) == []


def test_a_guard_left_on_a_renamed_field_is_named() -> None:
    module, source = _probe("volume")

    assert names_that_are_not_fields(module, source) == [
        "Probe guards 'volume', which is not one of its fields"
    ]


def test_a_guard_compared_with_something_other_than_a_string_cannot_pass_unread() -> None:
    source = GUARD.replace('"{volume}"', "FIELD_NAME")

    with pytest.raises(ValueError, match="compares name with FIELD_NAME, which is not a string"):
        guarded_names(source)
