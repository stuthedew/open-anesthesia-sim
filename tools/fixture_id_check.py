"""Refuse a `PL-` literal the store could never have minted.

`read_items` takes the `id` field verbatim, so `PL-STUV` parses and behaves
like any other item right up to the moment it reaches something that applies
`store.ID_PATTERN` - and then it matches nothing at all. A test asserting that
an id is absent from a listing, excluded from a pick, or unrecognised in prose
then passes against a broken implementation as readily as a correct one.
`test_roadmap.py` asserted for seventeen days that a prose mention is placed
nowhere while naming an id the parser could never have placed; breaking the
placement rule left it green (`PL-GXPP`, 261 substitutions across 9 files).

The other half is that an example is copied. `tools/generator_check.py` printed
`root-cause-of: PL-AAAA, PL-BBBB, PL-CCCC` as the line for a session to paste,
and `docket check` rejected all three (`PL-DPY6`); `.claude/rules/citation-drift.md`
documented `PL-A1B2` as one of the project's illustrative placeholders, which is
the same defect in the document a session reads to learn what a placeholder *is*
(`PL-3BZS`). Neither file was reachable by any guard: the rule lived in
`subprojects/docket/tests/test_store.py` and globbed that directory only
(`PL-7922`, which moved it here).

**Why a tool rather than a wider glob on the test it came from.** A pytest test
could reach the same trees. The argument is consistency: every repo-wide grammar
or structure guard in this project is already a `tools/` script with its own
`tests/unit/test_*.py` - `branch_id_check.py`, `rules_paths_check.py`,
`workflow_paths_check.py`, `core_vocabulary_check.py`, `glyph_check.py` - and a
failure here names the file, the line and the token where an assertion dump
would not. The test it replaced is gone rather than kept beside it, because two
spellings of one grammar drift, which is why `store.py` exports `ID_PATTERN`
unanchored instead of letting each reader write its own. What that gives up,
stated rather than left to be found: an extracted `subprojects/docket/` carries
no fixture-id guard of its own until it takes a copy.

**It reads the grammar with `docket`'s own parser rather than its own.** A check
matching ids more loosely than `store.ID_RE` would certify a literal that
`ID_PATTERN` still cannot see, which is worse than no check at all - the gate
would be green while the guarantee it stands for was void. So `ID_RE` is
imported from the module under protection, and a change to the alphabet moves
both together.

## What is scanned, and what is deliberately not

**Python, everywhere.** Values only: an `ast` walk, with docstrings dropped
before it runs, so an id *discussed* in writing needs nothing and a comment
never reaches the tree at all. A literal malformed on purpose - the rejection
tests need one, and a `glob("PL-K*.md")` pattern is not an id - says so with a
`not-an-id` marker anywhere in the lines its literal spans. That marker is
inline rather than a list kept here, because a list can name a literal the tree
no longer holds and nothing would ever say so.

**`.claude/`, line by line, for everything that is not Python.** No `ast` is
available for markdown or shell, so this half is a text scan and its rule has to
be exact without one. It is, and only here: measured 2026-09-21, every `PL-`
token under `.claude/` failing the grammar was a defect - 2 of 2, both
`PL-A1B2`. `.claude/` is the resident instruction set a session reads to learn
the conventions, so a malformed id in it is a template, not a discussion.

**What it cannot see, stated rather than left to be found.** An id spelled with
underscores so that it can be a keyword argument - `_items(root,
PL_AAAA_open=...)` in `tests/unit/test_doc_check.py`, whose helper writes
`PL-AAAA-open.md` - is the same defect and passes here, because widening the
candidate to `PL_` would reject ordinary constant names like `PL_PREFIX` for a
reason that has nothing to do with ids. Four instances existed and `PL-7922`
renamed them; the mechanism gap is `PL-L609`.

**`docs/`, `ROADMAP.md` and the item store are out of scope, and that is the
same measurement pointing the other way.** There, prose *about* malformed ids is
the norm rather than the exception - `PL-GXPP`'s brief alone names seventeen,
`ROADMAP.md:86` quotes the bad literal in a release note, and `PL-3BZS` counted
9 non-conforming mentions outside the two test trees of which 6 are correct as
they stand. A check that fires on two thirds prose is one nobody leaves switched
on. Marking each of them would be the same judgment, moved into the tree and
paid for forever.

Standard library only, like every tool here. It is invoked through `uv run
python` rather than a bare `python3`, and is absent from the floor sections of
`Makefile` and `.github/workflows/quality.yml`, because it parses `tests/` and
`src/` with `ast` and those target 3.14 - `ast.parse`'s `feature_version` only
ever narrows the syntax accepted, so it cannot teach a 3.11 parser a newer
language. The file itself stays floor-parseable and virtualenv-free, which is
what `tests/unit/test_tools_portability.py` holds it to.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.store import ID_RE  # noqa: E402

#: A token that *looks* like an id, to be judged against `ID_RE`.
#:
#: The lookbehind is load-bearing rather than tidiness: without it `GPL-3.0` and
#: `LGPL-2.1` read as `PL-3` and `PL-2`, neither of which the store could mint.
#: Latent while only Python values were scanned, and live the moment a text scan
#: runs - `docs/ARCHITECTURE.md` carries three between them. A genuine id is
#: always preceded by a quote, a backtick, a space or a path separator, so the
#: lookbehind can only ever drop a false positive.
CANDIDATE_RE = re.compile(r"(?<![A-Za-z0-9])PL-[A-Za-z0-9]+")

#: `f"PL-B1B{n:03d}"` mints `PL-B1B000`, so a hole has to stand for the digits
#: it will be given. This reads the width out of an explicit format spec; one
#: character is the default. Dropping the holes instead would report `PL-B1B` as
#: three characters, and a check with a false positive that obvious is one
#: nobody leaves switched on.
SPEC_WIDTH_RE = re.compile(r"0(\d+)d\Z")

#: The marker that exempts a literal. Read across every line the literal spans,
#: never its opening line alone: the parser folds implicitly concatenated
#: strings into one node reported at the line the *first* fragment opens, so on
#: a multi-line literal the marker could not otherwise be placed where it is
#: looked for. `tests/unit/test_workflow_paths_check.py` has two of that shape.
MARKER = "not-an-id"

DOCSTRING_HOLDERS = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)

#: Never walked: neither is repository source, and both can hold anything.
SKIP_DIRS = frozenset(
    {".git", ".venv", "__pycache__", ".ruff_cache", ".mypy_cache", "node_modules"}
)

#: The one tree whose prose is scanned. See the module docstring for why it is
#: this tree and not `docs/`.
TEXT_ROOT = ".claude"


class Offender(NamedTuple):
    """One malformed id, and enough to go and find it."""

    path: Path
    line: int
    token: str

    def render(self, root: Path) -> str:
        return f"{self.path.relative_to(root)}:{self.line} {self.token}"


def _hole_width(hole: ast.FormattedValue) -> int:
    """How many characters one `{...}` will contribute, read from its format spec."""
    spec = hole.format_spec
    if isinstance(spec, ast.JoinedStr):
        literal = "".join(
            part.value
            for part in spec.values
            if isinstance(part, ast.Constant) and isinstance(part.value, str)
        )
        found = SPEC_WIDTH_RE.search(literal)
        if found:
            return int(found.group(1))
    return 1


def _rendered(node: ast.JoinedStr) -> str:
    """One f-string as the id it will mint, holes filled with their characters."""
    parts: list[str] = []
    for part in node.values:
        if isinstance(part, ast.Constant) and isinstance(part.value, str):
            parts.append(part.value)
        elif isinstance(part, ast.FormattedValue):
            parts.append("0" * _hole_width(part))
    return "".join(parts)


def values(node: ast.AST) -> Iterator[tuple[int, int, str]]:
    """Every string the module *uses*, with the first and last line it spans.

    An f-string short-circuits its own children: its fragments are pieces of the
    value yielded for the whole, and yielding them again is what would turn
    every `f"PL-B1B{n}"` into a finding.
    """
    if isinstance(node, ast.JoinedStr):
        yield node.lineno, node.end_lineno or node.lineno, _rendered(node)
        return
    if isinstance(node, ast.Constant):
        if isinstance(node.value, str):
            yield node.lineno, node.end_lineno or node.lineno, node.value
        return
    for child in ast.iter_child_nodes(node):
        yield from values(child)


def without_docstrings(tree: ast.Module) -> ast.Module:
    """The same tree with every docstring dropped, so prose is not scanned."""
    for node in ast.walk(tree):
        if not isinstance(node, DOCSTRING_HOLDERS) or not node.body:
            continue
        first = node.body[0]
        if (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
        ):
            node.body = node.body[1:]
    return tree


def malformed(value: str) -> Iterator[str]:
    """Every token in `value` that looks like an id and is not one."""
    for found in CANDIDATE_RE.finditer(value):
        if not ID_RE.match(found.group(0)):
            yield found.group(0)


def scan_python(path: Path) -> list[Offender]:
    """Malformed ids among the string values one module uses."""
    lines = path.read_text(encoding="utf-8").splitlines()
    tree = without_docstrings(ast.parse("\n".join(lines), filename=str(path)))
    offenders: list[Offender] = []
    for start, end, value in values(tree):
        span = "\n".join(lines[start - 1 : end])
        if MARKER in span:
            continue
        for token in malformed(value):
            offenders.append(Offender(path, start, token))
    return offenders


def scan_text(path: Path) -> list[Offender]:
    """Malformed ids anywhere in one document, judged line by line.

    Nothing is exempt but the marker, because there is no parser here to tell a
    value from prose - which is the whole reason this half runs over one tree
    rather than over `docs/`.
    """
    offenders: list[Offender] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if MARKER in line:
            continue
        for token in malformed(line):
            offenders.append(Offender(path, number, token))
    return offenders


def _walk(root: Path) -> Iterator[Path]:
    """Every file under `root`, skipping the directories nothing should parse."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if SKIP_DIRS.intersection(path.parts):
            continue
        yield path


def collect(root: Path) -> list[Offender]:
    """Every malformed id in the repository, in the order a reader would fix them."""
    offenders: list[Offender] = []
    for path in _walk(root):
        if path.suffix == ".py":
            offenders.extend(scan_python(path))
        elif TEXT_ROOT in path.parts:
            try:
                offenders.extend(scan_text(path))
            except UnicodeDecodeError:
                continue
    return offenders


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refuse a `PL-` literal the store could not mint.")
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to scan")
    args = parser.parse_args(argv)

    offenders = collect(args.root)
    if not offenders:
        print("fixture-id: every `PL-` literal is one the store could mint")
        return 0

    listed = "\n".join(f"    {offender.render(args.root)}" for offender in offenders)
    print(
        f"fixture-id: {len(offenders)} `PL-` literal(s) outside the alphabet the store mints "
        f"(Crockford base32 minus the vowels, four characters, or three digits):\n"
        f"{listed}\n"
        f"  `ID_PATTERN` matches none of these, so a fixture carrying one exercises nothing and "
        f"any assertion resting on it passes vacuously - and an example carrying one is copied.\n"
        f"  Rename it to an id the store could mint, or, where the literal is deliberately not an "
        f"id, say so with a `{MARKER}` comment on one of the lines it spans.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
