"""What the source checks under `tools/` share: a scoped walk, a ratcheting baseline and a `main`.

`fact_home_check.py` and `literal_home_check.py` each walk a module recording
the function or class around what they find, and each hold what they find to
a baseline keyed by file that only shrinks. `core_vocabulary_check.py`,
`import_boundary_check.py`, `literal_home_check.py` and
`source_tier_counts.py` each read a `--root` the same way. Each tool wrote
these for itself, and pylint's duplicate-code check found the copies
(`PL-VWXL`). This module is their one home.

Standard library only and floor-parseable, like every tool under `tools/`.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Protocol, TypeVar

#: What a tool found at one site; each tool has its own record of a site.
Found = TypeVar("Found")

#: A baseline: for each file, the count allowed for each key.
Baseline = Mapping[str, Mapping[tuple[str, str], int]]


class ScopedVisitor(ast.NodeVisitor):
    """An `ast` walk that knows the dotted scope it is in.

    `scope` names each function and class around the node being visited,
    outermost first. A subclass that needs to see a function or class before
    its body overrides `enter`.
    """

    def __init__(self) -> None:
        self.scope: list[str] = []

    def enter(self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> None:
        """Called with each function and class before its body is visited."""

    def _scoped(self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> None:
        self.enter(node)
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    visit_FunctionDef = _scoped
    visit_AsyncFunctionDef = _scoped
    visit_ClassDef = _scoped


@dataclass(frozen=True)
class Overflow(Generic[Found]):
    """A file and key found more often than the baseline allows."""

    path: str
    key: tuple[str, str]
    allowed: int
    found: tuple[Found, ...]


@dataclass(frozen=True)
class Stale:
    """A baseline entry the tree no longer fills."""

    path: str
    key: tuple[str, str]
    allowed: int
    found: int
    missing: bool


def overflows(
    sites: Iterable[tuple[tuple[str, tuple[str, str]], Sequence[Found]]], baseline: Baseline
) -> list[Overflow[Found]]:
    """Return each file and key with more sites than the baseline allows, in the order given."""

    over = []

    for (path, key), listed in sites:
        allowed = baseline.get(path, {}).get(key, 0)

        if len(listed) > allowed:
            over.append(Overflow(path, key, allowed, tuple(listed)))

    return over


def stale_entries(
    root: Path, baseline: Baseline, found: Mapping[str, Counter[tuple[str, str]]], unread: set[str]
) -> list[Stale]:
    """Return each baseline entry above what its file now holds.

    A file in `unread` is skipped, because a file that did not parse has no
    count to compare. A file that no longer exists holds nothing.
    """

    stale = []

    for path, entries in baseline.items():
        if path in unread:
            continue

        missing = not (root / path).is_file()

        for key, allowed in entries.items():
            count = 0 if missing else found.get(path, Counter())[key]

            if count < allowed:
                stale.append(Stale(path, key, allowed, count, missing))

    return stale


def stale_lines(entries: Sequence[Stale], describe: Callable[[tuple[str, str]], str]) -> list[str]:
    """Return the report's lines for stale baseline entries, each naming what to do.

    `describe` turns an entry's key into the words that name it, such as
    `git in _branch`.
    """

    if not entries:
        return []

    lines = ["", "Baselined but no longer there - lower the entry, so the count stays a ratchet:"]

    for entry in entries:
        if entry.missing:
            remedy = "the file no longer exists; delete its entries"
        elif entry.found:
            remedy = f"set it to {entry.found}"
        else:
            remedy = "delete it"

        lines.append(
            f"  {entry.path}, {describe(entry.key)}: baseline {entry.allowed}, "
            f"found {entry.found} - {remedy}"
        )

    return lines


class _Report(Protocol):
    @property
    def errors(self) -> int: ...


Report = TypeVar("Report", bound=_Report)


def run_report(
    argv: Sequence[str] | None,
    description: str,
    analyze: Callable[[Path], Report],
    format_report: Callable[[Report], str],
) -> int:
    """Run a check over the repository a `--root` names, print its report, and return its status.

    With no `--root`, the repository is the one holding `tools/`. The status
    is 1 when the report counts an error and 0 otherwise.
    """

    root = repository_root(argv, description)
    report = analyze(root)
    print(format_report(report))
    return 1 if report.errors else 0


def repository_root(argv: Sequence[str] | None, description: str) -> Path:
    """Return the repository a `--root` argument names, or the one holding `tools/`."""

    parser = argparse.ArgumentParser(description=description.partition("\n")[0])
    parser.add_argument("--root", type=Path, default=None, help="path to the repository")
    args = parser.parse_args(argv)
    return (args.root or Path(__file__).resolve().parent.parent).resolve()
