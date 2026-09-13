#!/usr/bin/env python3
"""Hold `src/anesthesia_sim/core/` to the vocabulary `docs/MODEL.md` establishes.

`.claude/rules/core-domain.md` asks that a clinician who knows uptake and
distribution recognise the physiology in `core/` without a translation step.
That bar is a judgment and stays one. Three consequences of it are not, and
this decides those three:

1. **Every Code cell in `docs/MODEL.md` § "Symbols" resolves.** The column
   claims to name "the one expression in `core/` that denotes each symbol". A
   cell naming an attribute that no longer exists is a map to a tree that has
   moved, and the reader it misleads is the one who reached for the map because
   the code did not read like the domain.
2. **A retired name never comes back.** `PL-9SH6` gave the
   partial-pressure-equivalent fraction one accessor name across every
   compartment; `RETIRED_NAMES` below is what it replaced, so the vocabulary it
   closed stays closed.
3. **A partition-coefficient identifier names both phases, in order.** The
   primary literature does not hold a convention here - Baker and Farmery's
   2011 review calls one quantity the tissue-gas, the tissue-blood and the
   blood tissue partition coefficient in a single chapter - so a reader cannot
   supply a missing phase from recall, and cannot tell a coefficient from its
   own reciprocal by looking. `docs/MODEL.md` § "Symbols" carries the citation.

**What this must never decide: whether a name is the one a reader who knows the
domain would guess.** That is the whole point of the convention and a tool that
guessed at it would be worse than no tool, because its output would look
authoritative. All three rules above are mechanical - resolvable, absent,
well-formed - and each reports a name rather than an opinion about one.

**A fourth rule was considered and refused.** A unit-suffix check over every
float-valued name in `core/` passes today, so it would be a pure ratchet
against a closed suffix vocabulary somebody would have to maintain against
every legitimate new kind. `CLAUDE.md` is explicit that where the benefit is
unclear the answer is no. Reconsider if a suffix regression is ever observed.

**Why `core/` and not the whole package.** The convention is declared for
`core/` - `.claude/rules/core-domain.md` is path-scoped to exactly this tree -
and the agent data files reach it anyway: every partition key under
`src/anesthesia_sim/data/agents/` has an identically named payload field in
`core/parameters.py`, so the stored vocabulary is checked at the seam it
crosses. Keeping `tests/` out is not an oversight either. This file's own test
suite has to be able to write a retired name into a fixture, and a rule that
forbade that could not be tested at all.

**Matching is on the whole identifier, never on a substring**, and the two
names that would otherwise be caught are the reason. `require_concentration_fraction`
in `core/validation.py` is the [0, 1] guard every renamed setter calls;
`BreathingCircuit.circuit_volume_l` is the stutter `PL-9SH6` deliberately left
alone. Neither is a retired accessor, both contain one's text, and `PL-6KNM`
and `PL-KZS3` are where each is decided. A substring rule would fail today
against two names nobody has agreed to change, which is the shape of a check
that gets suppressed rather than obeyed.

**Read with `ast`, never imported.** `core/parameters.py` imports Pydantic,
which does not exist in a bare checkout. This file stays standard-library-only
so `tests/unit/test_tools_portability.py` keeps covering it, but it is invoked
through `uv run python` because the source it parses targets the version
`.python-version` pins rather than the 3.11 floor - `ast.parse`'s
`feature_version` only ever narrows the syntax accepted, so it cannot teach an
older parser a newer language. That is why these rules are here rather than in
`tools/doc_check.py`, which `make check` and the CI floor section both invoke
under a bare `python3`.

**A tree or a table that matches nothing is an error, not a pass.** Renaming
`core/` or the Symbols heading would otherwise leave every rule inspecting
nothing and reporting success, which is the silent-void failure a check of this
kind exists to remove.
"""

from __future__ import annotations

import argparse
import ast
import re
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TypeVar

#: The tree whose vocabulary is governed, relative to the repository root.
CORE_TREE = "src/anesthesia_sim/core"

#: The specification the symbol map is read from.
MODEL_DOC = "docs/MODEL.md"

#: The section holding it, and the column naming the implementation.
SYMBOLS_HEADING = "Symbols"
CODE_COLUMN = "Code"
SYMBOL_COLUMN = "Symbol"

#: What `docs/MODEL.md` writes where the model defines a symbol the
#: implementation does not materialize. The cell must then say what the code
#: reads in its place, which is the sentence this requires be present.
EM_DASH = "—"

#: `ClassName.accessor`, as the Code column writes it: inside a code span.
_CODE_REFERENCE = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)`")

#: The token every partition-coefficient identifier is built around.
_COEFFICIENT = "partition_coefficient"


@dataclass(frozen=True)
class RetiredName:
    """One accessor name that must not come back, and what replaced it."""

    name: str
    replacement: str


#: The specification for rule 2, transcribed from `PL-9SH6`'s own table. Every
#: entry is an accessor `core/` used to carry for the dimensionless
#: partial-pressure-equivalent fraction that `docs/MODEL.md` § "Concentrations"
#: defines. Three of them - `concentration_fraction`,
#: `partial_pressure_fraction` as it was, and `delivered_concentration_fraction`
#: - each denoted more than one symbol at once, which is the defect the rename
#: removed: a reader met one name on three classes and had to open each to learn
#: which $`F`$ it was.
#:
#: Retiring a further name means adding it here with its replacement. Nothing
#: infers this list - it cannot be derived from the tree, because a name that
#: has been removed leaves nothing behind to read.
RETIRED_NAMES: tuple[RetiredName, ...] = (
    RetiredName("concentration_fraction", "partial_pressure_fraction"),
    RetiredName("delivered_concentration_fraction", "delivered_partial_pressure_fraction"),
    RetiredName("circuit_concentration_fraction", "inspired_partial_pressure_fraction"),
    RetiredName("mixed_venous_fraction", "mixed_venous_partial_pressure_fraction"),
    RetiredName("venous_outflow_fraction", "venous_outflow_partial_pressure_fraction"),
    RetiredName("tissue_return_fraction", "tissue_return_partial_pressure_fraction"),
    RetiredName("arterial_fraction", "arterial_partial_pressure_fraction"),
)

#: The specification for rule 3: the phases a partition coefficient may name,
#: ordered along the path agent takes into the patient. A coefficient names the
#: phase further from the gas phase first, which is the order its symbol writes
#: - $`\lambda_{i:b}`$ is `tissue_blood_partition_coefficient` - so an
#: identifier and the ratio it denotes cannot disagree.
#:
#: The ordering is what makes "in order" decidable, and it is what refuses a
#: reciprocal: `gas_blood_partition_coefficient` names two declared phases and
#: is still wrong, because it is the reciprocal of the one this model stores.
#: Nothing else here would catch that, and it is precisely the confusion the
#: literature invites.
#:
#: A new phase - oil, rubber, soda lime - is one entry, added with the source
#: for the coefficient it appears in.
PHASES: tuple[str, ...] = ("gas", "blood", "tissue")


@dataclass(frozen=True)
class ClassDefinition:
    """One class found in `core/`, and every attribute name it carries."""

    name: str
    path: str
    line: int
    members: frozenset[str]


@dataclass(frozen=True)
class Identifier:
    """One identifier occurrence, for the rules that read names alone."""

    name: str
    path: str
    line: int


@dataclass(frozen=True)
class SymbolCell:
    """One row of `docs/MODEL.md` § "Symbols", as far as this rule reads it."""

    line: int
    symbol: str
    code: str


@dataclass(frozen=True)
class Unresolved:
    """A Code cell this cannot resolve, and the reason in a reader's terms."""

    cell: SymbolCell
    reference: str
    reason: str


@dataclass(frozen=True)
class RetiredUse:
    """A retired name found in `core/`."""

    retired: RetiredName
    identifier: Identifier


@dataclass(frozen=True)
class Malformed:
    """A partition-coefficient identifier that does not name both phases in order."""

    identifier: Identifier
    reason: str


def _self_attributes(function: ast.AST) -> Iterator[str]:
    """Every `self.<name>` a method assigns.

    A dataclass declares most of `core/`'s state in the class body, but an
    attribute a `__post_init__` or a setter writes is an attribute all the
    same, and a Code cell naming one is correct. Excluding them would make
    this accuse a name that is really there, which costs more than the
    handful of lines it saves.
    """
    for node in ast.walk(function):
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            targets = [node.target]
        for target in targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
            ):
                yield target.attr


def class_definitions(source: str, path: str) -> Iterator[ClassDefinition]:
    """Every class in one module, with the attribute names it carries.

    A member is a declared field, a class-level assignment, a method - which
    covers every `@property`, since the decorator does not change the name -
    or an attribute one of those methods assigns to `self`.
    """
    tree = ast.parse(source, filename=path)
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        members: set[str] = set()
        for statement in node.body:
            if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
                members.add(statement.target.id)
            elif isinstance(statement, ast.Assign):
                for target in statement.targets:
                    if isinstance(target, ast.Name):
                        members.add(target.id)
            elif isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef)):
                members.add(statement.name)
                members.update(_self_attributes(statement))
        yield ClassDefinition(node.name, path, node.lineno, frozenset(members))


def identifiers(source: str, path: str) -> Iterator[Identifier]:
    """Every identifier one module binds or reads, in source order.

    Names in docstrings, comments and string literals are deliberately absent.
    A docstring recording that an accessor used to be called something else is
    history worth keeping, and a rule that forbade writing the old name down
    would forbid explaining the rename.
    """
    tree = ast.parse(source, filename=path)
    found: list[Identifier] = []
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Name):
            names = [node.id]
        elif isinstance(node, ast.Attribute):
            names = [node.attr]
        elif isinstance(node, ast.arg):
            names = [node.arg]
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names = [node.name]
        elif isinstance(node, ast.keyword) and node.arg is not None:
            names = [node.arg]
        elif isinstance(node, ast.alias):
            names = [node.asname or node.name.split(".")[-1]]
        for name in names:
            found.append(Identifier(name, path, getattr(node, "lineno", 0)))
    yield from sorted(found, key=lambda entry: (entry.line, entry.name))


def symbol_cells(text: str) -> tuple[SymbolCell, ...]:
    """The Symbols table's rows, or nothing if the section or table is absent.

    Nothing here guesses at a table it cannot find: `analyze` reports an empty
    result as an error rather than passing over it.
    """
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == f"## {SYMBOLS_HEADING}":
            start = index + 1
            break
    if start is None:
        return ()

    rows: list[list[str]] = []
    numbers: list[int] = []
    for offset, line in enumerate(lines[start:], start=start):
        stripped = line.strip()
        if stripped.startswith("## "):
            break
        if not stripped.startswith("|"):
            continue
        rows.append([cell.strip() for cell in stripped.strip("|").split("|")])
        numbers.append(offset + 1)
    if len(rows) < 3:
        return ()

    header = rows[0]
    if CODE_COLUMN not in header or SYMBOL_COLUMN not in header:
        return ()
    code_index = header.index(CODE_COLUMN)
    symbol_index = header.index(SYMBOL_COLUMN)

    cells: list[SymbolCell] = []
    for row, number in zip(rows[2:], numbers[2:], strict=True):
        if len(row) <= max(code_index, symbol_index):
            continue
        cells.append(SymbolCell(number, row[symbol_index], row[code_index]))
    return tuple(cells)


def _resolve(cell: SymbolCell, defined: dict[str, list[ClassDefinition]]) -> Iterator[Unresolved]:
    """Whether one Code cell names something `core/` actually has."""
    references = _CODE_REFERENCE.findall(cell.code)
    declared_absent = cell.code.startswith(EM_DASH)

    if declared_absent:
        #: An em dash alone says the symbol is not materialized and stops
        #: there, which leaves the reader looking for an attribute that was
        #: never going to exist. The convention is that the cell says what the
        #: code reads instead.
        if not cell.code.lstrip(EM_DASH).strip():
            yield Unresolved(
                cell,
                cell.code,
                f"is an em dash with nothing after it; a symbol the implementation does "
                f"not materialize must say what `{CORE_TREE}/` reads in its place",
            )
            return
    elif len(references) != 1:
        yield Unresolved(
            cell,
            cell.code or "(empty)",
            f"names {len(references)} `ClassName.accessor` expressions; the {CODE_COLUMN} "
            f"column names the one expression that denotes each symbol",
        )
        return

    for class_name, accessor in references:
        definitions = defined.get(class_name, [])
        if not definitions:
            yield Unresolved(
                cell, f"{class_name}.{accessor}", f"no class named {class_name} in {CORE_TREE}/"
            )
        elif len(definitions) > 1:
            where = ", ".join(f"{item.path}:{item.line}" for item in definitions)
            yield Unresolved(
                cell,
                f"{class_name}.{accessor}",
                f"{class_name} is defined more than once ({where}), so the cell names no "
                f"one expression",
            )
        elif accessor not in definitions[0].members:
            yield Unresolved(
                cell,
                f"{class_name}.{accessor}",
                f"{class_name} at {definitions[0].path}:{definitions[0].line} has no attribute, "
                f"property or field called {accessor}",
            )


def _phase_pair(name: str) -> str | None:
    """Why `name` is not `<phase>_<phase>_{_COEFFICIENT}`, or `None` if it is.

    Whatever precedes the two phases is a qualifier naming *which* instance -
    `fat_tissue_gas_partition_coefficient` is the fat group's - and is
    deliberately unconstrained: it says nothing about which phases the ratio
    is between, which is the only thing this rule is about.
    """
    prefix = name.split(_COEFFICIENT)[0]
    words = [word for word in prefix.split("_") if word]
    if len(words) < 2:
        return (
            f"names {len(words)} of the two phases it is a ratio between; a partition "
            f"coefficient is written <phase>_<phase>_{_COEFFICIENT}"
        )
    outer, inner = words[-2], words[-1]
    if outer not in PHASES or inner not in PHASES:
        unknown = [word for word in (outer, inner) if word not in PHASES]
        named = " and ".join(unknown)
        is_are = "are not declared phases" if len(unknown) > 1 else "is not a declared phase"
        return (
            f"names {named}, which {is_are}; the declared phases are {', '.join(PHASES)}. Add "
            f"the phase to PHASES with the source for the coefficient it appears in, or name "
            f"the two phases this ratio is actually between"
        )
    if PHASES.index(outer) <= PHASES.index(inner):
        expected = f"{inner}_{outer}_{_COEFFICIENT}"
        return (
            f"names {outer} before {inner}, which is the reciprocal of the coefficient this "
            f"model stores; phases are written outward from the gas phase "
            f"({' then '.join(reversed(PHASES))}), so this is {expected}"
        )
    return None


@dataclass(frozen=True)
class Report:
    """Everything one run decided."""

    modules: int
    cells: int
    unresolved: tuple[Unresolved, ...]
    retired: tuple[RetiredUse, ...]
    malformed: tuple[Malformed, ...]
    #: Set where a rule found nothing to inspect, which passes vacuously.
    empty_tree: bool
    empty_table: bool

    @property
    def errors(self) -> int:
        return (
            len(self.unresolved)
            + len(self.retired)
            + len(self.malformed)
            + int(self.empty_tree)
            + int(self.empty_table)
        )


_Finding = TypeVar("_Finding")


def _first_per_module(
    findings: Sequence[_Finding], locate: Callable[[_Finding], Identifier]
) -> tuple[_Finding, ...]:
    """Keep the first occurrence of each name in each module, in source order."""
    seen: set[tuple[str, str]] = set()
    kept: list[_Finding] = []
    for finding in findings:
        identifier = locate(finding)
        key = (identifier.path, identifier.name)
        if key not in seen:
            seen.add(key)
            kept.append(finding)
    return tuple(kept)


def _sources(root: Path) -> list[Path]:
    return sorted((root / CORE_TREE).rglob("*.py"))


def analyze(
    root: Path, retired_names: Sequence[RetiredName] = RETIRED_NAMES, phases: Iterable[str] = PHASES
) -> Report:
    """Evaluate all three rules against the tree and the specification on disk."""
    del phases  # Read through the module constant; named here for the docstring's sake.

    defined: dict[str, list[ClassDefinition]] = {}
    found_retired: list[RetiredUse] = []
    malformed: list[Malformed] = []
    retired_by_name = {entry.name: entry for entry in retired_names}

    sources = _sources(root)
    for path in sources:
        relative = path.relative_to(root).as_posix()
        source = path.read_text(encoding="utf-8")
        for definition in class_definitions(source, relative):
            defined.setdefault(definition.name, []).append(definition)
        for identifier in identifiers(source, relative):
            retired = retired_by_name.get(identifier.name)
            if retired is not None:
                found_retired.append(RetiredUse(retired, identifier))
            if _COEFFICIENT in identifier.name:
                reason = _phase_pair(identifier.name)
                if reason is not None:
                    malformed.append(Malformed(identifier, reason))

    cells = symbol_cells((root / MODEL_DOC).read_text(encoding="utf-8"))
    unresolved = [problem for cell in cells for problem in _resolve(cell, defined)]

    return Report(
        modules=len(sources),
        cells=len(cells),
        unresolved=tuple(unresolved),
        #: One finding per module per name. An identifier repeated on twenty
        #: lines is one defect with twenty call sites, and printing all twenty
        #: buries the other rules' output; the module and the first line are
        #: what a reader needs to start fixing it.
        retired=_first_per_module(found_retired, lambda use: use.identifier),
        malformed=_first_per_module(malformed, lambda problem: problem.identifier),
        empty_tree=not sources,
        empty_table=not cells,
    )


def format_report(report: Report) -> str:
    """Render a report the way `bin/docket check` renders one: verdict first."""
    lines = [
        f"core vocabulary: {report.cells} symbol cells, {report.modules} modules read, "
        f"{report.errors} errors"
    ]

    if report.empty_tree:
        lines.append("")
        lines.append(f"No Python files under {CORE_TREE}/ - all three rules inspected nothing:")
        lines.append("  A moved or renamed package leaves this check passing over an empty tree.")

    if report.empty_table:
        lines.append("")
        lines.append(f'No readable table under {MODEL_DOC} "## {SYMBOLS_HEADING}":')
        lines.append(
            f"  The section, its table, or its {SYMBOL_COLUMN}/{CODE_COLUMN} columns were "
            f"renamed, so the symbol map is unchecked."
        )

    if report.unresolved:
        lines.append("")
        lines.append(f'{MODEL_DOC} "## {SYMBOLS_HEADING}" names code that does not resolve:')
        for problem in report.unresolved:
            lines.append(f"  {MODEL_DOC}:{problem.cell.line}: {problem.cell.symbol}")
            lines.append(f"    {problem.reference}: {problem.reason}")
        lines.append(
            f"  The {CODE_COLUMN} column maps the specification onto the implementation; a cell "
            f"naming an attribute that is gone maps it onto a tree that has moved."
        )

    if report.retired:
        lines.append("")
        lines.append(f"A retired accessor name is back in {CORE_TREE}/:")
        for use in report.retired:
            lines.append(f"  {use.identifier.path}:{use.identifier.line}: {use.identifier.name}")
            lines.append(f"    retired by PL-9SH6 in favour of {use.retired.replacement}")
        lines.append(
            '  One quantity, one name: `docs/MODEL.md` § "Concentrations" defines every '
            "model concentration as the same kind of thing, so a second name for it sends the "
            "reader to the class body to find out which."
        )

    if report.malformed:
        lines.append("")
        lines.append("A partition-coefficient identifier does not name both phases in order:")
        for malformed in report.malformed:
            lines.append(
                f"  {malformed.identifier.path}:{malformed.identifier.line}: "
                f"{malformed.identifier.name}"
            )
            lines.append(f"    {malformed.reason}")
        lines.append(
            "  The literature does not hold a convention here - Baker and Farmery 2011 name one "
            "quantity tissue-gas, tissue-blood and blood tissue in a single chapter - so a "
            "reader cannot supply a missing phase, or spot a reciprocal, from recall."
        )

    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=None, help="path to the repository")
    args = parser.parse_args(argv)

    root = (args.root or Path(__file__).resolve().parent.parent).resolve()
    report = analyze(root)
    print(format_report(report))
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
