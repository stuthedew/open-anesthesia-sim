#!/usr/bin/env python3
"""Hold `src/anesthesia_sim/` to the import boundaries declared in `BOUNDARIES`.

A boundary names a package - or a dotted module prefix within one - the tree
it is confined within, and the modules permitted to import it, which may be no
module at all. Four invariants are declared today, and they are confined for
unrelated reasons.

**Pydantic, to one module.** `core/parameters.py` pairs each `_...Payload`
Pydantic model with a public, frozen, Pydantic-independent dataclass, and
`_StrictPayload`'s docstring says what that pairing buys: *the rest of `core/`
never imports Pydantic.* A payload validates one JSON document and is
discarded; what every other module holds is a plain dataclass.

**The wall clock and the process generator, to nothing under `core/`.**
`CLAUDE.md` requires simulation time to be explicit state and never the wall
clock, and `docs/MODEL.md` "The reproducibility guarantee" states that a run is
a function of its inputs and of the number of steps taken and of nothing else.
A compartment reaching for `time`, `datetime`, `random`, `secrets` or `uuid`
breaks that promise by an amount the machine chooses rather than the model.

**The UI toolkit, and the numerics that arrive with it, out of `core/`; the
toolkit the interface left, out of everything.** `CLAUDE.md`'s first
architecture rule keeps simulation code independent of the toolkit. `PySide6`,
`pyqtgraph` and `numpy` - the three packages the Qt port (`ROADMAP.md` §
"v0.4.26 - the interface moves to Qt") brought in - are permitted in no module
under `core/`, declared before any of them existed in the tree so that the
first commit letting one into a compartment would fail rather than the port
being measured after the fact. Flet is two distributions with two root packages
- `flet` and `flet_charts` - and both are permitted in no module under `src/`
at all: the port is complete (`PL-25KS`), and `PL-7SVX`'s rule is that nothing
under `src/` may import Flet again. While the port ran, the two Flet
allowances were the tool's own checklist for it - the unused-allowance error
fired as each module stopped importing one, so the entry went in the same
commit - and the last entries took the allowances with them (`PL-9KDK`).

**The interface, out of `core/`.** `docs/ARCHITECTURE.md` § "Layering" draws
one direction - `data/` loaded by `core/`, `core/` read by `app/` - and the
interface reads immutable snapshots from the model, which knows nothing of what
displays it. `anesthesia_sim.app` is permitted in no module under `core/`. It
is the first boundary inside this package rather than around a dependency, and
a comment in `tests/unit/test_formatting.py` credited this tool with it for as
long as the tool read only root packages, to which `anesthesia_sim.app` and
`anesthesia_sim.core` are both `anesthesia_sim` (`PL-YXFF`).

Nothing measured any of them. The first two held on 2026-09-04 - `pydantic`
appeared in exactly two lines of that one file, and no module under `core/`
imported a clock, a generator or an identifier minted from either - and the
Flet count was true on 2026-09-14 while `ROADMAP.md` credited this tool with
enforcing it and nothing did. Any later change could import one and every gate
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
reach the run. The toolkit boundaries follow the clock's shape - `app/` is
where a widget legitimately belongs - except the two Flet packages, which are
confined out of the whole package, because no module has a reason to import a
toolkit the interface has left.

**Every import counts, including one guarded by `TYPE_CHECKING`.** Such an
import creates no runtime dependency, so a narrower check could pass it. It is
reported because the property being defended is about the types a module's API
mentions, not only about what it loads: a compartment annotated with a payload
model has coupled itself to the validation library whether or not the import
executes.

**A boundary matches every dotted name an import makes available.** `import
a.b` makes `a.b` available; `from X import a, b` makes `X`, `X.a` and `X.b`,
so `from anesthesia_sim import app` is caught as surely as
`from anesthesia_sim.app import formatting`. A name reaches a boundary when it
equals the boundary's package or continues it past a dot, so
`anesthesia_sim.app_metadata` is not `anesthesia_sim.app`, and one statement
is one finding however many of its names match.

**Relative imports are resolved, not skipped.** `from ..app import formatting`
under `core/` reaches `anesthesia_sim.app`. The old reading - that a relative
import cannot name a package outside the tree - holds for a root package and
for nothing inside one, which is where the layering boundary lives. The
importing module's package is read from its path under `src/`, and the
resolution is importlib's own: `package.rsplit(".", level - 1)[0]`.

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

**Read with `ast`, never imported.** `app/simulation_view.py` imports PySide6
and `core/parameters.py` imports Pydantic, neither of which exists in a bare
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

#: The directory a module's dotted name is read from: `src/anesthesia_sim/core/x.py`
#: is `anesthesia_sim.core.x`, whose relative imports resolve against
#: `anesthesia_sim.core`.
SOURCE_ROOT = "src"


@dataclass(frozen=True)
class Boundary:
    """One package, or a dotted module prefix within one, confined to a named set of modules."""

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
        package="subprocess",
        tree="src/anesthesia_sim",
        allowed=("src/anesthesia_sim/app_metadata.py",),
        why=(
            "`app_metadata.py` asks git which build is running, so that a header that "
            "would otherwise read the same string for every build between two releases "
            "can name the commit (PL-YKF8). That is the package's first read of anything "
            "outside its own inputs, and the habit is what this confines: a module that "
            "shells out has taken a dependency on the machine, and in `core/` that would "
            "break the same promise `time` and `datetime` below protect - `docs/MODEL.md` "
            '"The reproducibility guarantee", that a run is a function of its inputs and '
            "of the number of steps taken and of nothing else. The one allowance reads no "
            "simulation state, reaches nothing under `core/`, and fails closed to the "
            "bare version"
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
    Boundary(
        package="secrets",
        tree="src/anesthesia_sim/core",
        allowed=(),
        why=(
            "the same guarantee as `random`, and strictly worse, because the escape `random` "
            "leaves open is closed here. `secrets` draws from `random.SystemRandom`, whose "
            "`seed()` is a documented stub - *Not used for a system random number generator* "
            "- and whose `getstate()` raises `NotImplementedError`. A caller therefore cannot "
            "make a run that reaches it reproducible by any means at all, where a seeded "
            "`random.Random` at least could be"
        ),
    ),
    Boundary(
        package="uuid",
        tree="src/anesthesia_sim/core",
        allowed=(),
        why=(
            "both halves of the guarantee, in one import. `uuid4()` is `os.urandom(16)` in a "
            "wrapper, so it is the unseedable generator above; `uuid1()` is a UUID from the "
            "current time and the host's hardware address, so it is the wall clock and it "
            "makes the result differ between machines as well as between runs. An identifier "
            "a compartment mints for itself is not an input to the run; one the run needs "
            "arrives with the other inputs, where a caller can hold it fixed"
        ),
    ),
    Boundary(
        package="flet",
        tree="src/anesthesia_sim",
        allowed=(),
        why=(
            "the port is complete and nothing under `src/` may import Flet: `PL-25KS` "
            "moved the dashboard to PySide6 and deleted the last module importing this "
            "package, and `PL-7SVX`'s rule - landed with that port - is that it does not "
            "come back. `CLAUDE.md`'s first architecture rule keeps simulation code "
            "independent of the UI toolkit, and the interface has left this one. While "
            'the port ran, `ROADMAP.md` § "v0.4.26 - the interface moves to Qt" reasoned '
            "from the count of modules importing Flet, and this entry named them: its "
            "unused-allowance error was the checklist that took each name out in the "
            "commit that freed it (PL-9KDK)"
        ),
    ),
    Boundary(
        package="flet_charts",
        tree="src/anesthesia_sim",
        allowed=(),
        why=(
            "the other half of Flet - `flet-charts` is its own distribution with its own "
            "root package, which the Flet chart module imported without importing `flet`, "
            "so a boundary on `flet` alone would leave a route back in (PL-9KDK, found by "
            "declaring it). Same rule as the entry above: the chart is on pyqtgraph and "
            "the dashboard on PySide6 (PL-25KS), and no module under `src/` may import "
            "this package again (PL-7SVX)"
        ),
    ),
    Boundary(
        package="PySide6",
        tree="src/anesthesia_sim/core",
        allowed=(),
        why=(
            'the toolkit the interface moves to (`ROADMAP.md` § "v0.4.26 - the interface '
            'moves to Qt"), held to the same rule as the one it replaces: `CLAUDE.md` keeps '
            "simulation code independent of the UI toolkit, and a compartment that imports "
            "a widget library has taken a dependency on a display it does not have. "
            "Declared before the first `PySide6` import exists in the tree, so the port's "
            "first commit is measured against it rather than the rule being written after "
            "the port decided where things went (PL-9KDK)"
        ),
    ),
    Boundary(
        package="pyqtgraph",
        tree="src/anesthesia_sim/core",
        allowed=(),
        why=(
            "the plotting library the chart moves to, and a widget library by another "
            "name - it imports Qt at module load. What `core/` produces is a history of "
            "modelled quantities; how a history is drawn is the interface's question, and "
            "`app/chart_frame.py` is where the seam between the two sits"
        ),
    ),
    Boundary(
        package="numpy",
        tree="src/anesthesia_sim/core",
        allowed=(),
        why=(
            "it arrives under pyqtgraph as the chart's array type, not as the model's. "
            '`docs/WORKING_NOTES.md` "Decided: no numpy" (2026-09-05) measured that the '
            "model's read path and its append-dominated write path gain nothing from it, "
            'and `docs/MODEL.md` "The reproducibility guarantee" rests on a pure-Python '
            "propagator whose every operation is `math` and `float`. Confining it out of "
            "`core/` keeps that a decision the tree enforces rather than one the port's "
            "dependency list quietly reopens; widening it means re-arguing that note, and "
            "the entry to add here would carry the argument"
        ),
    ),
    Boundary(
        package="anesthesia_sim.app",
        tree="src/anesthesia_sim/core",
        allowed=(),
        why=(
            'the layering `docs/ARCHITECTURE.md` § "Layering" draws runs one way: `core/` '
            "is read by `app/`, and the model knows nothing of what displays it. A "
            "compartment importing from the interface has taken a dependency on the "
            "display, and on whatever the interface module itself imports, which "
            "`CLAUDE.md`'s first architecture rule keeps out of simulation code. "
            "`PL-X9KD` cut one such route, the displayed decimal count reaching back into "
            "`core/`; a comment in `tests/unit/test_formatting.py` credited this tool with "
            "the rule while it read only root packages and declared none (PL-YXFF)"
        ),
    ),
)


@dataclass(frozen=True)
class Imported:
    """One import statement found in one module, and every dotted name it makes available."""

    names: tuple[str, ...]
    line: int
    statement: str

    def reaches(self, package: str) -> bool:
        """Does any name equal `package`, or continue it past a dot?"""
        return any(name == package or name.startswith(package + ".") for name in self.names)


@dataclass(frozen=True)
class Violation:
    """A module importing a package its boundary confines elsewhere."""

    boundary: Boundary
    path: str
    imported: Imported


def _dynamic_name(node: ast.Call) -> str | None:
    """The module a dynamic import names, where the name is a literal.

    Returns `None` for anything undecidable by reading the source: a computed
    name, a keyword-only call, or a relative name, which resolves against a
    `package` argument this does not evaluate.
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
    return first.value or None


def _resolve(module: str | None, level: int, package: str | None) -> str | None:
    """The absolute module a `from` statement names, relative or not.

    importlib's own rule. `None` where it cannot be decided: a relative import
    read without the importing module's package, or one climbing past the top
    of it, which would fail at import time anyway.
    """
    if not level:
        return module
    if not package:
        return None
    bits = package.rsplit(".", level - 1)
    if len(bits) < level:
        return None
    return f"{bits[0]}.{module}" if module else bits[0]


def module_imports(
    source: str, filename: str = "<unknown>", package: str | None = None
) -> tuple[Imported, ...]:
    """Every import one module makes, by any form this can decide.

    Args:
        source: The module's text.
        filename: Reported in a `SyntaxError` if the text does not parse.
        package: The importing module's package, `anesthesia_sim.core` for
            `core/x.py`, against which relative imports resolve. Without it
            they cannot be decided and are omitted.

    Returns:
        One entry per import statement, in source order, each carrying every
        dotted name the statement makes available.
    """
    tree = ast.parse(source, filename=filename)
    found: list[Imported] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.append(Imported((alias.name,), node.lineno, f"import {alias.name}"))
        elif isinstance(node, ast.ImportFrom):
            module = _resolve(node.module, node.level, package)
            if module is None:
                continue
            members = [alias.name for alias in node.names if alias.name != "*"]
            names = (module, *(f"{module}.{member}" for member in members))
            written = "." * node.level + (node.module or "")
            imported = ", ".join(alias.name for alias in node.names)
            found.append(Imported(names, node.lineno, f"from {written} import {imported}"))
        elif isinstance(node, ast.Call):
            name = _dynamic_name(node)
            if name is not None:
                found.append(Imported((name,), node.lineno, f"a dynamic import of {name!r}"))
    return tuple(sorted(found, key=lambda entry: (entry.line, entry.statement)))


def _package_of(root: Path, path: Path) -> str | None:
    """The package a module's relative imports resolve against, read from its path."""
    try:
        parts = path.relative_to(root / SOURCE_ROOT).parts
    except ValueError:
        return None
    return ".".join(parts[:-1]) or None


@dataclass(frozen=True)
class Report:
    """Everything one run decided."""

    #: Distinct modules read, so nesting trees do not inflate it.
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
    #: Distinct modules, not module-reads: two boundaries over nesting trees
    #: read the same file, and a count that grew when a boundary was added
    #: rather than when the source did would stop being evidence of how much
    #: source is guarded, which is the only thing it is for.
    read: set[str] = set()

    for boundary in boundaries:
        allowed = set(boundary.allowed)
        used: set[str] = set()
        found_any = False

        for path in _sources(root, boundary.tree):
            found_any = True
            relative = path.relative_to(root).as_posix()
            read.add(relative)
            imports = module_imports(
                path.read_text(encoding="utf-8"),
                filename=str(path),
                package=_package_of(root, path),
            )
            hits = [entry for entry in imports if entry.reaches(boundary.package)]
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
        scanned=len(read),
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
