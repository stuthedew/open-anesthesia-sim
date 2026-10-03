#!/usr/bin/env python3
"""Hold every number in `src/anesthesia_sim/` to one named home.

A number the simulator uses is written once, as the value of a module-level
name, and read through that name everywhere else - or it lives in a data file
under `data/`, which `core/parameters.py` validates and this never reads. Two
copies of one value agree only until somebody edits one of them, and nothing
held the copies equal until they disagreed: seven items were that one
mechanism before anything refused it (`PL-40SJ`).

**Two rules, each exact.**

- *No bare literal.* A numeric literal - int, float or complex, never a
  `bool`, which subclasses int - fails anywhere under the tree unless it sits
  in the value of a module-level assignment. The whole right-hand side counts,
  so a table of declared values such as `app/chart_time_base.py`'s
  `TIME_BASE_LADDER` is one home rather than a dozen literals. A class-body
  default is not module-level and fails: `AlveolarCompartment`'s and
  `BreathingCircuit`'s restate values the data files hold (`PL-H8QP`).
- *One definition per name.* A module-level name bound to a number is defined
  in one module and imported by the rest. Two modules each declaring the same
  constant is the second copy arriving with a name already on it, which the
  first rule exempts. Equal values under different names are not refused:
  `SECONDS_PER_MINUTE` and `MINUTES_PER_HOUR` are both 60.0 and are different
  quantities, and which quantity a number is cannot be read off the tree.

**What it would have caught.** `PL-017`: the controller's constructor
defaults typed the reference patient's values, cardiac output 5.0 among them.
`PL-4YY1` and `PL-8DJ7`: `BreathingCircuit`'s field defaults typed the circuit
volume 6.0 and the fresh gas flow 4.0, outside every data file and provenance
row. `PL-DJYF`: `AlveolarCompartment`'s typed the gas volume 2.5 and the
ventilation 4.0 that `data/patients/reference_adult.json` already held. Those
four are the first rule. `PL-QRBB`: `SECONDS_PER_MINUTE` declared in five
`core/` modules. `PL-TCW5`: `FLOW_FRACTION_TOLERANCE = 1e-12` defined twice,
so the two perfusion-sum guards could drift apart. Those two are the second.
`PL-T5J5` is the one it would not have caught: its eight copies of the 24 h
run length were in tests, which this does not read, and `PL-0Z0F` is the
test-side half. `PL-06M7` cleared seven `3600`s through `core/units.py` before
this landed, as its first instance.

**What it does not catch, deliberately.** A value derived twice has no
literal to find - `PL-8H2R`'s step count and time bound were two calculations
of one limit - so that stays design judgment and types. Prose restating a
number belongs to the provenance checks (`PL-4FBP`, `PL-G424`), and a
precision inside a format spec, `:.2f`, is part of a string this never reads.

**0, 1 and 2 are exempt, and so are -1 and -2**, which parse as a negated
constant. 0 and 1 are identities and counting bounds. 2 is counted rather than
assumed: of the 27 twos in the tree when this landed, 17 halved, doubled or
squared (`/ 2`, `// 2`, `* 2`, `** 2`) and the other 10 were indices or grid
positions, and none was a domain quantity, so the exemption hid nothing. A
2 that is a quantity - two agents, a two-minute interval - deserves a name
anyway, and the exemption is what a reviewer reads past to find it.

**The baseline only shrinks.** `BASELINE` holds every bare literal the tree
carried when this landed, keyed by file, enclosing scope and value rather than
by line, so an edit above a literal moves nothing. A literal beyond its entry
fails as new. An entry the tree no longer fills fails as stale, naming the
count to lower it to, so a literal removed is a literal that cannot quietly
come back: the ratchet `tools/ignore_check.py` is for `type: ignore`, and
`check_colors_live_in_the_theme` in `tools/contrast_check.py` is this rule for
colours.

**It names a constant, and never decides one.** Where a new literal equals a
module-level constant - including one derived by arithmetic in its own module,
so `core/units.py`'s `SECONDS_PER_HOUR` - the report names it as "the same
value as": whether it is the same quantity is the reader's call. A site under
`core/` is offered only constants under `core/`, which is the layering
`docs/ARCHITECTURE.md` § "Layering" states and `import_boundary_check.py`
enforces.

**A tree with no Python files is an error, not a pass,** and a file that does
not parse is reported as not checked and fails: a check that read nothing must
not report that it found nothing.

**Read with `ast`, never imported**, standard library only. The source uses
3.14 syntax, so both gates run this through `uv run python`.
"""

from __future__ import annotations

import argparse
import ast
import operator
from collections import Counter, defaultdict
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

#: The tree held to both rules.
TREE = "src/anesthesia_sim"

#: The layer whose sites may read only constants defined inside it.
CORE = "src/anesthesia_sim/core/"

#: Values a bare literal may take anywhere. See the module docstring on 2.
EXEMPT: frozenset[int] = frozenset({-2, -1, 0, 1, 2})

#: How many constants one finding names before summarising the rest.
SUGGESTED = 3

#: Every bare literal in the tree when this landed, after `PL-06M7` cleared
#: its seven `3600`s: file, then `(enclosing scope, value)`, then how many. It
#: may only shrink. Most of `app/` is layout geometry in pixels and layout
#: units, which a name would make easier to change consistently; the `core/`
#: class defaults are the second copies `PL-H8QP` describes.
BASELINE: dict[str, dict[tuple[str, str], int]] = {
    "src/anesthesia_sim/app/chart_frame.py": {
        ("nearest_wash_in_point", "3"): 1,
        ("percent_axis_ticks", "1e-09"): 1,
    },
    "src/anesthesia_sim/app/dashboard_frame.py": {
        ("slider_position", "10.0"): 1,
        ("slider_value", "10.0"): 1,
    },
    "src/anesthesia_sim/app/qt_chart.py": {
        ("TraceLegend.__init__", "6"): 1,
        ("_GridLines.place", "90"): 1,
        ("_HoverReadout.__init__", "60"): 1,
        ("_HoverReadout.show", "0.75"): 1,
        ("_branch_point_mark", "90"): 1,
        ("_control_mark_pool", "90"): 1,
        ("_legend_entry", "6"): 1,
        ("_legend_row", "16"): 1,
        ("_legend_row", "6"): 1,
    },
    "src/anesthesia_sim/app/qt_widgets.py": {
        ("BookmarkDialog._build_layout", "3"): 7,
        ("BookmarkDialog._build_layout", "4"): 2,
        ("BookmarkDialog._build_layout", "5"): 2,
        ("BookmarkDialog._build_layout", "6"): 1,
        ("ForkPanel.__init__", "8"): 2,
    },
    "src/anesthesia_sim/app/run_view.py": {
        ("RunView.build_parameter_controls", "12"): 1,
        ("RunView.build_readout_section", "12"): 1,
        ("RunView.build_readout_section", "4"): 1,
        ("RunView.build_sidebar_panels", "4"): 1,
        ("RunView.build_transport_row", "8"): 1,
    },
    "src/anesthesia_sim/app/simulation_view.py": {
        ("SimulationView._build_chart_column", "6"): 1,
        ("SimulationView._build_chart_column", "8"): 1,
        ("SimulationView._build_page", "12"): 5,
    },
    "src/anesthesia_sim/core/alveolar.py": {
        ("AlveolarCompartment", "2.5"): 1,
        ("AlveolarCompartment", "4.0"): 1,
    },
    "src/anesthesia_sim/core/circuit.py": {
        ("BreathingCircuit", "100.0"): 1,
        ("BreathingCircuit", "6.0"): 1,
    },
    "src/anesthesia_sim/core/parameters.py": {("_validate_positive_percent", "100.0"): 1},
}

Number = int | float | complex

_ARITHMETIC: dict[type[ast.operator], Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}


@dataclass(frozen=True)
class Literal:
    """One bare numeric literal, with its sign folded in."""

    path: str
    line: int
    scope: str
    value: Number

    @property
    def key(self) -> tuple[str, str]:
        return (self.scope, repr(self.value))


@dataclass(frozen=True)
class Constant:
    """A module-level name bound to a number."""

    path: str
    line: int
    name: str
    value: Number


@dataclass(frozen=True)
class Module:
    """What one file contributes to each rule."""

    literals: tuple[Literal, ...]
    constants: tuple[Constant, ...]


def _number(node: ast.AST) -> Number | None:
    """The value of a numeric literal node, or `None` for anything else."""
    if not isinstance(node, ast.Constant) or isinstance(node.value, bool):
        return None
    value = node.value
    return value if isinstance(value, (int, float, complex)) else None


def _evaluate(node: ast.AST, known: Mapping[str, Number]) -> Number | None:
    """A module-level value as a number, where arithmetic on literals and names decides it."""
    literal = _number(node)
    if literal is not None:
        return literal
    if isinstance(node, ast.Name):
        return known.get(node.id)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        operand = _evaluate(node.operand, known)
        if operand is None:
            return None
        return -operand if isinstance(node.op, ast.USub) else operand
    if isinstance(node, ast.BinOp) and type(node.op) in _ARITHMETIC:
        left = _evaluate(node.left, known)
        right = _evaluate(node.right, known)
        if left is None or right is None:
            return None
        try:
            result = _ARITHMETIC[type(node.op)](left, right)
        except (ArithmeticError, TypeError, ValueError):
            return None
        if isinstance(result, (int, float, complex)) and not isinstance(result, bool):
            return result
    return None


class _Literals(ast.NodeVisitor):
    """Collects bare numeric literals with the dotted scope that encloses each."""

    def __init__(self, path: str) -> None:
        self.path = path
        self.scope: list[str] = []
        self.found: list[Literal] = []

    def _scoped(self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> None:
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    visit_FunctionDef = _scoped
    visit_AsyncFunctionDef = _scoped
    visit_ClassDef = _scoped

    def visit_UnaryOp(self, node: ast.UnaryOp) -> None:
        operand = _number(node.operand)
        if isinstance(node.op, ast.USub) and operand is not None:
            self._record(node.operand, -operand)
            return
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        value = _number(node)
        if value is not None:
            self._record(node, value)

    def _record(self, node: ast.AST, value: Number) -> None:
        if value in EXEMPT:
            return
        scope = ".".join(self.scope) or "<module>"
        self.found.append(Literal(self.path, getattr(node, "lineno", 0), scope, value))


def read_module(source: str, path: str) -> Module:
    """Both rules' view of one file.

    Args:
        source: The module's text.
        path: Its repository-relative path, which every finding carries.

    Raises:
        SyntaxError: The text does not parse.
    """
    tree = ast.parse(source, filename=path)
    visitor = _Literals(path)
    constants: list[Constant] = []
    known: dict[str, Number] = {}
    for statement in tree.body:
        if not isinstance(statement, (ast.Assign, ast.AnnAssign)) or statement.value is None:
            visitor.visit(statement)
            continue
        # The value is the home; a target or an annotation is not.
        for child in ast.iter_child_nodes(statement):
            if child is not statement.value:
                visitor.visit(child)
        value = _evaluate(statement.value, known)
        if value is None:
            continue
        targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
        for target in targets:
            if isinstance(target, ast.Name):
                known[target.id] = value
                constants.append(Constant(path, statement.lineno, target.id, value))
    return Module(tuple(visitor.found), tuple(constants))


@dataclass(frozen=True)
class Overflow:
    """A file, scope and value found more often than the baseline allows."""

    path: str
    key: tuple[str, str]
    allowed: int
    found: tuple[Literal, ...]


@dataclass(frozen=True)
class Stale:
    """A baseline entry the tree no longer fills."""

    path: str
    key: tuple[str, str]
    allowed: int
    found: int
    missing: bool


@dataclass(frozen=True)
class Report:
    """Everything one run decided."""

    scanned: int
    literals: int
    allowed: int
    overflows: tuple[Overflow, ...]
    stale: tuple[Stale, ...]
    redefined: tuple[tuple[str, tuple[Constant, ...]], ...]
    unparsed: tuple[tuple[str, str], ...]
    constants: tuple[Constant, ...]

    @property
    def errors(self) -> int:
        return (
            len(self.overflows)
            + len(self.stale)
            + len(self.redefined)
            + len(self.unparsed)
            + (self.scanned == 0)
        )


def _sources(root: Path, tree: str) -> Iterator[Path]:
    """Every Python file under the tree, in a stable order."""
    yield from sorted((root / tree).rglob("*.py"))


def analyze(
    root: Path, baseline: Mapping[str, Mapping[tuple[str, str], int]] = BASELINE, tree: str = TREE
) -> Report:
    """Evaluate both rules against the source on disk."""
    found: dict[str, Counter[tuple[str, str]]] = {}
    sites: dict[tuple[str, tuple[str, str]], list[Literal]] = defaultdict(list)
    constants: list[Constant] = []
    unparsed: list[tuple[str, str]] = []
    scanned = 0

    for source in _sources(root, tree):
        scanned += 1
        relative = source.relative_to(root).as_posix()
        try:
            module = read_module(source.read_text(encoding="utf-8"), relative)
        except (SyntaxError, UnicodeDecodeError, ValueError) as error:
            unparsed.append((relative, str(error)))
            continue
        found[relative] = Counter(literal.key for literal in module.literals)
        for literal in module.literals:
            sites[(relative, literal.key)].append(literal)
        constants.extend(module.constants)

    overflows: list[Overflow] = []
    for (path, key), literals in sites.items():
        allowed = baseline.get(path, {}).get(key, 0)
        if len(literals) > allowed:
            overflows.append(Overflow(path, key, allowed, tuple(literals)))

    unread = {path for path, _ in unparsed}
    stale: list[Stale] = []
    for path, entries in baseline.items():
        if path in unread:
            continue
        missing = not (root / path).is_file()
        for key, allowed in entries.items():
            count = 0 if missing else found.get(path, Counter())[key]
            if count < allowed:
                stale.append(Stale(path, key, allowed, count, missing))

    by_name: dict[str, list[Constant]] = defaultdict(list)
    for constant in constants:
        by_name[constant.name].append(constant)
    redefined = tuple(
        (name, tuple(definitions))
        for name, definitions in sorted(by_name.items())
        if len({definition.path for definition in definitions}) > 1
    )

    return Report(
        scanned=scanned,
        literals=sum(sum(counts.values()) for counts in found.values()),
        allowed=sum(sum(entries.values()) for entries in baseline.values()),
        overflows=tuple(overflows),
        stale=tuple(stale),
        redefined=redefined,
        unparsed=tuple(unparsed),
        constants=tuple(constants),
    )


def same_value(literal: Literal, constants: Sequence[Constant]) -> list[Constant]:
    """The constants a finding may name: equal in value and importable from its site.

    Same module first, then by path. A site under `core/` is offered nothing
    from outside it, since `core/` imports nothing from `app/`.
    """
    candidates = [
        constant
        for constant in constants
        if constant.value == literal.value
        and (not literal.path.startswith(CORE) or constant.path.startswith(CORE))
    ]
    return sorted(candidates, key=lambda c: (c.path != literal.path, c.path, c.line))


def _suggestion(literal: Literal, constants: Sequence[Constant]) -> str | None:
    matches = same_value(literal, constants)
    if not matches:
        return None
    named = [f"`{c.name}` in {c.path}" for c in matches[:SUGGESTED]]
    rest = len(matches) - SUGGESTED
    listed = ", ".join(named) + (f" and {rest} more" if rest > 0 else "")
    return f"the same value as {listed}; read it if that is the quantity meant"


def format_report(report: Report, tree: str = TREE) -> str:
    """Render a report the way `bin/docket check` renders one: verdict first."""
    lines = [
        f"literal homes: {report.scanned} modules read, {report.literals} bare literals "
        f"against a baseline of {report.allowed}, {report.errors} errors"
    ]

    if report.scanned == 0:
        lines.append("")
        lines.append(f"No Python files under {tree}/ - the check read nothing.")
        lines.append("  A moved or renamed package leaves both rules passing over nothing.")

    if report.unparsed:
        lines.append("")
        lines.append("Not checked - these files do not parse, so their numbers are unknown:")
        for path, error in report.unparsed:
            lines.append(f"  {path}: {error}")

    if report.overflows:
        lines.append("")
        lines.append("A bare number where a named one belongs:")
        for overflow in report.overflows:
            scope, value = overflow.key
            for literal in overflow.found:
                lines.append(f"  {literal.path}:{literal.line}: {value} in {scope}")
                suggestion = _suggestion(literal, report.constants)
                if suggestion:
                    lines.append(f"    {suggestion}")
            if overflow.allowed:
                lines.append(
                    f"    the baseline allows {overflow.allowed} of these in {scope}, "
                    f"and {len(overflow.found)} are there"
                )
        lines.append(
            "  Name it once, as a module-level constant where the quantity belongs, and "
            "read the name; the baseline does not grow."
        )

    if report.stale:
        lines.append("")
        lines.append(
            "Baselined but no longer there - lower the entry, so the count stays a ratchet:"
        )
        for entry in report.stale:
            scope, value = entry.key
            if entry.missing:
                remedy = "the file no longer exists; delete its entries"
            elif entry.found:
                remedy = f"set it to {entry.found}"
            else:
                remedy = "delete it"
            lines.append(
                f"  {entry.path}, {value} in {scope}: baseline {entry.allowed}, "
                f"found {entry.found} - {remedy}"
            )

    if report.redefined:
        lines.append("")
        lines.append("A numeric constant defined in more than one module:")
        for name, definitions in report.redefined:
            where = ", ".join(f"{d.path}:{d.line} = {d.value!r}" for d in definitions)
            lines.append(f"  {name}: {where}")
        lines.append(
            "  Keep one definition and import it everywhere else; two agree only until "
            "one is edited (PL-TCW5, PL-QRBB)."
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
