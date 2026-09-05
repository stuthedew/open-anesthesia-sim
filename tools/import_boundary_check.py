#!/usr/bin/env python3
"""Hold `src/anesthesia_sim/` to the import boundaries declared in `BOUNDARIES`.

A boundary names a package, the tree it is confined within, and the modules
permitted to import it - which may be no module at all. Two invariants are
declared today, and they are confined for unrelated reasons.

**Pydantic, to one module.** `core/parameters.py` pairs each `_...Payload`
Pydantic model with a public, frozen, Pydantic-independent dataclass, and
`_StrictPayload`'s docstring says what that pairing buys: *the rest of `core/`
never imports Pydantic.* A payload validates one JSON document and is
discarded; what every other module holds is a plain dataclass.

**The wall clock and the process generator, to nothing under `core/`.**
`CLAUDE.md` requires simulation time to be explicit state and never the wall
clock, and `docs/MODEL.md` "The reproducibility guarantee" states that a run is
a function of its inputs and of the number of steps taken and of nothing else.
A compartment reaching for `time`, `datetime` or `random` breaks that promise
by an amount the machine chooses rather than the model.

Nothing measured either. Both held on 2026-09-04 - `pydantic` appeared in
exactly two lines of that one file, and no module under `core/` imported a
clock or a generator - but any later change could import one and every gate
would stay green. The failure that makes this worth a tool is not the coupling
on its own: it is that the docstring and the guarantee asserting the property
would go on asserting it, reading as verified when it is not. `CLAUDE.md` names
this shape - a claim answerable by reading the tree belongs in a script rather
than in prose nobody re-measures.

**What this decides.** Whether a module outside a boundary's allowed list
imports that boundary's package, whether an allowance still names a file that
exists, and whether an allowance is still used.

**What it must never decide.** Which packages *ought* to be confined, or which
module ought to hold the exception. Those are judgments; they live in
`BOUNDARIES` below, written by a person with the reason beside them, and this
file only evaluates them.

**Why the trees differ, and the asymmetry is the point.** The Pydantic
boundary covers `app/` as well as `core/`: the pairs exist for `core/`, but
nothing supplies a reason to exempt the interface, which consumes parameters
through the same seam functions as already-validated frozen dataclasses, so an
import there would be a new coupling buying nothing. One allowed-module list
also makes the rule statable in a sentence - *exactly one module in this
package imports Pydantic* - which is a rule a reader can hold, where "forbidden
here, permitted there" is a rule they have to look up. The clock boundary stops
at `core/` for the opposite reason: `app/` is where a clock legitimately
belongs, and the same guarantee says so - *the interface schedules its ticks
with the wall clock*, and what it must not do is let a tick's real duration
reach the run.

**Every import counts, including one guarded by `TYPE_CHECKING`.** Such an
import creates no runtime dependency, so a narrower check could pass it. It is
reported because the property being defended is about the types a module's API
mentions, not only about what it loads: a compartment annotated with a payload
model has coupled itself to the validation library whether or not the import
executes.

**Dynamic imports are read, within a stated limit.** `import_module("pydantic")`
and `__import__("pydantic")` are caught when the name is a literal, because a
boundary that a one-line refactor can step around silently is the same
false-green this file exists to remove. A *computed* name cannot be decided by
reading the source, and this makes no attempt to guess at one: the guard is
against an accident, not against evasion.

**A tree that matches no source files is an error, not a pass.** Renaming or
moving the package would otherwise leave the walk with nothing to inspect and
the check reporting success - the exact silent-void failure a boundary check is
supposed to prevent.

**Read with `ast`, never imported.** `app/simulation_view.py` imports Flet and
`core/parameters.py` imports Pydantic, neither of which exists in a bare
checkout - which is where this has to run, standard library only, the promise
every tool here makes.
"""

from __future__ import annotations

import argparse
import ast
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

#: Call names whose first literal string argument names a module.
_DYNAMIC_IMPORTERS = frozenset({"import_module", "__import__"})


@dataclass(frozen=True)
class Boundary:
    """One package confined to a named set of modules, and why."""

    package: str
    tree: str
    allowed: tuple[str, ...]
    why: str


#: The specification. Each entry names a package, the tree it is confined
#: within, the modules permitted to import it - an empty `allowed` confines it
#: out of that tree entirely - and the reason the confinement is worth
#: enforcing. Adding a dependency that must not spread means adding it here;
#: widening one means adding a path to `allowed` and saying why in the same
#: commit.
BOUNDARIES: tuple[Boundary, ...] = (
    Boundary(
        package="pydantic",
        tree="src/anesthesia_sim",
        allowed=("src/anesthesia_sim/core/parameters.py",),
        why=(
            "the `_...Payload`/public-dataclass pairs in `core/parameters.py` exist so that "
            "the compartments, the controller, the interface and the tests hold plain frozen "
            "dataclasses rather than validation models; a payload validates one JSON document "
            "and is discarded at the seam (`parse_agent_parameters()`, "
            "`parse_reference_adult_parameters()`). `_StrictPayload`'s docstring asserts this, "
            "and PL-Y0RZ is why it is measured rather than remembered"
        ),
    ),
    Boundary(
        package="time",
        tree="src/anesthesia_sim/core",
        allowed=(),
        why=(
            "`CLAUDE.md` requires simulation time to be explicit state and never the wall "
            'clock, and `docs/MODEL.md` "The reproducibility guarantee" promises that a run '
            "is a function of its inputs and of the number of steps taken and of nothing "
            "else. A compartment that reads a clock makes two runs of identical inputs "
            "differ by whatever the machine was doing, which is not a quantity the model "
            "owns. The interface schedules its ticks with the wall clock, which is why the "
            "confinement is `core/` rather than the whole package; PL-J833 is why it is "
            "measured rather than remembered"
        ),
    ),
    Boundary(
        package="datetime",
        tree="src/anesthesia_sim/core",
        allowed=(),
        why=(
            "the same guarantee as `time`, by the other route into it: `datetime.now()` and "
            "`datetime.today()` read the same clock, and a `timedelta` derived from two of "
            "them is a duration nobody passed in. A timestamp a compartment takes for "
            "itself is not an input to the run, so no caller can hold it fixed and no "
            "recorded history can be reproduced from what the run records"
        ),
    ),
    Boundary(
        package="random",
        tree="src/anesthesia_sim/core",
        allowed=(),
        why=(
            "an unseeded generator breaks the same guarantee a clock does. `random`'s "
            "module-level functions share one process-global generator, so a compartment "
            "reaching for one takes its seed from whatever else in the process touched it "
            "first - reproducible neither across runs nor across machines. Stochastic "
            "behaviour, if the model ever wants it, arrives as a seed passed in with the "
            "other inputs, where a caller can hold it fixed"
        ),
    ),
)


@dataclass(frozen=True)
class Imported:
    """One import found in one module."""

    root: str
    line: int
    statement: str


@dataclass(frozen=True)
class Violation:
    """A module importing a package its boundary confines elsewhere."""

    boundary: Boundary
    path: str
    imported: Imported


def _dynamic_root(node: ast.Call) -> str | None:
    """The root package of a dynamic import written with a literal name.

    Returns `None` for anything undecidable by reading the source: a computed
    name, a keyword-only call, or a relative name, which cannot reach outside
    the package doing the importing.
    """
    function = node.func
    if isinstance(function, ast.Attribute):
        name = function.attr
    elif isinstance(function, ast.Name):
        name = function.id
    else:
        return None
    if name not in _DYNAMIC_IMPORTERS or not node.args:
        return None
    first = node.args[0]
    if not (isinstance(first, ast.Constant) and isinstance(first.value, str)):
        return None
    if first.value.startswith("."):
        return None
    return first.value.split(".")[0] or None


def module_imports(source: str, filename: str = "<unknown>") -> tuple[Imported, ...]:
    """Every root package one module imports, by any form this can decide.

    Args:
        source: The module's text.
        filename: Reported in a `SyntaxError` if the text does not parse.

    Returns:
        One entry per import site, in source order. Relative imports are
        omitted: they cannot name a package outside the tree being walked.
    """
    tree = ast.parse(source, filename=filename)
    found: list[Imported] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.append(
                    Imported(alias.name.split(".")[0], node.lineno, f"import {alias.name}")
                )
        elif isinstance(node, ast.ImportFrom):
            if node.level or node.module is None:
                continue
            found.append(
                Imported(node.module.split(".")[0], node.lineno, f"from {node.module} import ...")
            )
        elif isinstance(node, ast.Call):
            root = _dynamic_root(node)
            if root is not None:
                found.append(Imported(root, node.lineno, f"a dynamic import of {root!r}"))
    return tuple(sorted(found, key=lambda entry: (entry.line, entry.statement)))


@dataclass(frozen=True)
class Report:
    """Everything one run decided."""

    scanned: int
    violations: tuple[Violation, ...]
    unenforced: tuple[tuple[Boundary, str], ...]
    unused: tuple[tuple[Boundary, str], ...]
    empty: tuple[Boundary, ...]

    @property
    def errors(self) -> bool:
        return bool(self.violations or self.unenforced or self.unused or self.empty)


def _sources(root: Path, tree: str) -> Iterator[Path]:
    """Every Python file under one boundary's tree, in a stable order."""
    yield from sorted((root / tree).rglob("*.py"))


def analyze(root: Path, boundaries: Sequence[Boundary] = BOUNDARIES) -> Report:
    """Evaluate every declared boundary against the source on disk."""
    violations: list[Violation] = []
    unenforced: list[tuple[Boundary, str]] = []
    unused: list[tuple[Boundary, str]] = []
    empty: list[Boundary] = []
    scanned = 0

    for boundary in boundaries:
        allowed = set(boundary.allowed)
        used: set[str] = set()
        found_any = False

        for path in _sources(root, boundary.tree):
            found_any = True
            scanned += 1
            relative = path.relative_to(root).as_posix()
            imports = module_imports(path.read_text(encoding="utf-8"), filename=str(path))
            hits = [entry for entry in imports if entry.root == boundary.package]
            if not hits:
                continue
            if relative in allowed:
                used.add(relative)
                continue
            violations.extend(Violation(boundary, relative, entry) for entry in hits)

        if not found_any:
            empty.append(boundary)

        for candidate in boundary.allowed:
            if not (root / candidate).is_file():
                unenforced.append((boundary, candidate))
            elif candidate not in used:
                unused.append((boundary, candidate))

    return Report(
        scanned=scanned,
        violations=tuple(violations),
        unenforced=tuple(unenforced),
        unused=tuple(unused),
        empty=tuple(empty),
    )


def format_report(report: Report, boundaries: Sequence[Boundary] = BOUNDARIES) -> str:
    """Render a report the way `bin/docket check` renders one: verdict first."""
    error_count = (
        len(report.violations) + len(report.unenforced) + len(report.unused) + len(report.empty)
    )
    lines = [
        f"import boundaries: {len(boundaries)} declared, {report.scanned} modules read, "
        f"{error_count} errors"
    ]

    if report.empty:
        lines.append("")
        lines.append("Declared over a tree containing no Python files - the check is vacuous:")
        for boundary in report.empty:
            lines.append(f"  {boundary.package} in {boundary.tree}/")
        lines.append("  A moved or renamed package leaves the boundary passing over nothing.")

    if report.violations:
        lines.append("")
        lines.append("Imported where its boundary does not allow it:")
        for violation in report.violations:
            lines.append(
                f"  {violation.path}:{violation.imported.line}: {violation.imported.statement}"
            )
        for boundary in dict.fromkeys(violation.boundary for violation in report.violations):
            if boundary.allowed:
                allowed = ", ".join(boundary.allowed)
                lines.append(f"  {boundary.package} is allowed only in {allowed}, because")
            else:
                lines.append(
                    f"  {boundary.package} is permitted in no module under "
                    f"{boundary.tree}/, because"
                )
            lines.append(f"    {boundary.why}.")

    if report.unenforced:
        lines.append("")
        lines.append("Named in `allowed` but absent from the tree:")
        for boundary, path in report.unenforced:
            lines.append(f"  {path} ({boundary.package})")
        lines.append("  A renamed or deleted module leaves its allowance pointing at nothing.")

    if report.unused:
        lines.append("")
        lines.append("Allowed the import but no longer making it - remove the entry:")
        for boundary, path in report.unused:
            lines.append(f"  {path} no longer imports {boundary.package}")
        lines.append("  An exception outliving its reason is one nobody will question later.")

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
