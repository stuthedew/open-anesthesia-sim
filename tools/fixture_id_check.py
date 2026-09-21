"""Refuse a `PL-` literal the store could never have minted, or a second spelling
of the grammar that decides what one is.

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

## The second rule: a pattern that restates the grammar

The paragraph above is the argument, and for two months nothing enforced it on
anything but this file. Five tools wrote their own: `PL-[A-Z0-9]{4}` in
`generator_check.py` and twice in `doc_check.py`, `PL-[A-Z0-9]{3,4}` in
`item_reads.py` and `dead_ends.py`, `PL-[0-9A-Z]{3,4}` in `pr_body_check.py`.
Every one was looser than the store in the alphabet - all five admit the vowels
the store cannot mint - and the four spelled `{4}` were *tighter* in the length,
blind to the 43 historical three-digit ids. That is not symmetrical damage:
`generator_check.citations` could not read 219 citation edges, and the signal it
prints for `docs/MODEL.md` said 6 items where 7 was the answer (`PL-KYW3`).

None of it was reachable by the literal rule above, which is why it stood:
`CANDIDATE_RE` needs an alphanumeric after `PL-` and a character class opens
with `[`. So the pattern is the thing judged, and the signature is the **counted
quantifier**: `{4}` or `{3,4}` after a character class is a second copy of
`store.ID_LENGTH` with a second copy of the alphabet in front of it. An
open-ended `PL-[A-Za-z0-9]+` claims to know nothing about the grammar and is
left alone - including `CANDIDATE_RE` itself, which is loose on purpose and judges
what it finds with `ID_RE` afterwards. Drawing the rule at the quantifier rather
than at "a regex after `PL-`" is what makes it exact enough to fail the build:
measured 2026-09-21 over every text file in the repository, it matches the six
repaired sites and nothing else outside `docs/items/`, which is not scanned.

## What is scanned, and what is deliberately not

**Python, everywhere.** What the module *uses*, never what it says about
itself: an `ast` walk over string values and keyword-argument names, with
docstrings dropped before it runs, so an id *discussed* in writing needs
nothing and a comment never reaches the tree at all. A name malformed on
purpose - the rejection tests need one, and a `glob("PL-K*.md")` pattern is
not an id - says so with a `not-an-id` marker anywhere in the lines it spans.
That marker is inline rather than a list kept here, because a list can name a
literal the tree no longer holds and nothing would ever say so.

**`.claude/`, line by line, for everything that is not Python.** No `ast` is
available for markdown or shell, so this half is a text scan and its rule has to
be exact without one. It is, and only here: measured 2026-09-21, every `PL-`
token under `.claude/` failing the grammar was a defect - 2 of 2, both
`PL-A1B2`. `.claude/` is the resident instruction set a session reads to learn
the conventions, so a malformed id in it is a template, not a discussion.

**Keyword-argument names, translated back to the filename they become.** An id
cannot be an identifier - `PL-8888` is not one - so a helper keyed by an id
takes `PL_8888_open` and puts the hyphens back, which is what
`tests/unit/test_doc_check.py` did until `PL-L609`. The value scan is blind to
that by construction: no `PL-` token appears in the source at all. So a
keyword name is translated `_` to `-` and handed to the same `malformed()`
every literal goes through, rather than given a grammar of its own.

The scope is `ast.keyword.arg` and not identifiers at large, and that is the
whole of what keeps `PL_PREFIX` and every other ordinary constant out of it: a
constant is a name being bound, a keyword is a parameter being passed, and
nothing in this repository is both. Measured 2026-09-21 under the 3.14
interpreter, so nothing was skipped for syntax: of 8,098 keyword arguments,
21 carry an uppercase letter at all and 17 of those are Qt's `ignoreBounds`,
`rateLimit` and `userData`, none of which can yield a `PL-` token. The
remaining four were the fixture this rule was written for.

**What it still cannot see, stated rather than left to be found.** A helper
that does *not* put the hyphens back - one writing `f"{name}.md"` from
`PL_8888_open` - produces a filename no store could write, and this stays
quiet on it: the token is mintable once translated. That is a filename shape
rather than an id grammar, and what is judged here is ids.

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

#: A `PL-` that opens a *restatement* of the grammar rather than naming an item:
#: the prefix, an optional non-capturing group, then a character class or class
#: escape closed by a counted quantifier. The counted quantifier is what makes
#: this exact rather than a guess - `{4}` or `{3,4}` is a second copy of
#: `store.ID_LENGTH`, where `PL-\S+` and `PL-[A-Za-z0-9]+` claim to know
#: nothing about the grammar and are left alone. Measured 2026-09-21 over every
#: text file in the repository: the rule matches the six sites `PL-KYW3`
#: repaired and nothing else outside `docs/items/`, which is not scanned.
GRAMMAR_RE = re.compile(r"PL-(?:\(\?:)?(?:\[[^\]]*\]|\\[dwsDWS])\{\d+(?:,\d*)?\}")

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


#: The two rules, and the key each finding is grouped under for reporting.
#: They are reported separately because their remedies have nothing in common:
#: "rename it to an id the store could mint" is wrong advice for a pattern.
LITERAL = "literal"
GRAMMAR = "grammar"


class Offender(NamedTuple):
    """One malformed id or restated grammar, and enough to go and find it."""

    path: Path
    line: int
    token: str
    rule: str = LITERAL

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


def restated(value: str) -> Iterator[str]:
    """Every second spelling of the id grammar in `value`.

    Scoped to what a module *runs* - see `scan_python` - and so never to prose:
    a docstring or comment explaining the pattern is discussion, and this file's
    own header would be its first finding otherwise. The literal half is scanned
    in `.claude/` text as well because an example there gets copied into an item;
    a regular expression is not copied that way, so this half has no text pass.
    """
    for found in GRAMMAR_RE.finditer(value):
        yield found.group(0)


def keyword_names(node: ast.AST) -> Iterator[tuple[int, int, str]]:
    """Every keyword-argument name, spelled as the filename it would become.

    See the module docstring for why this half exists and why it is scoped to
    `ast.keyword.arg`. The translation mirrors the one helper that made the
    form convenient, so what is judged is the id the caller meant rather than
    the identifier they were obliged to write.

    `**{...}` sets `arg` to `None` and names no keyword at all; its keys are
    ordinary string literals, which `values` above already reads. Skipping
    them here is what stops one literal being reported twice.
    """
    for child in ast.walk(node):
        if isinstance(child, ast.keyword) and child.arg:
            end = child.end_lineno or child.lineno
            yield child.lineno, end, child.arg.replace("_", "-")


def scan_python(path: Path) -> list[Offender]:
    """Malformed ids among the string values one module uses, and its keyword names.

    Sorted by line rather than left in walk order. Two passes over one tree
    would otherwise print a file's keyword findings after all of its literal
    ones, and a reader fixing them top to bottom would be sent back up the
    file - the ordering `collect` promises was incidental before and is held
    here now that there is a second pass to interleave.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    tree = without_docstrings(ast.parse("\n".join(lines), filename=str(path)))
    offenders: list[Offender] = []
    for start, end, value in (*values(tree), *keyword_names(tree)):
        span = "\n".join(lines[start - 1 : end])
        if MARKER in span:
            continue
        for token in malformed(value):
            offenders.append(Offender(path, start, token, LITERAL))
        for token in restated(value):
            offenders.append(Offender(path, start, token, GRAMMAR))
    return sorted(offenders, key=lambda offender: offender.line)


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


def _report(offenders: list[Offender], root: Path, rule: str) -> str:
    """One rule's findings, listed, with the remedy that rule actually has."""
    listed = "\n".join(f"    {offender.render(root)}" for offender in offenders)
    if rule == LITERAL:
        return (
            f"fixture-id: {len(offenders)} `PL-` literal(s) outside the alphabet the store mints "
            f"(Crockford base32 minus the vowels, four characters, or three digits):\n"
            f"{listed}\n"
            f"  `ID_PATTERN` matches none of these, so a fixture carrying one exercises nothing "
            f"and any assertion resting on it passes vacuously - and an example carrying one is "
            f"copied.\n"
            f"  Rename it to an id the store could mint, or, where the literal is deliberately "
            f"not an id, say so with a `{MARKER}` comment on one of the lines it spans."
        )
    return (
        f"fixture-id: {len(offenders)} second spelling(s) of the id grammar:\n"
        f"{listed}\n"
        f"  A counted quantifier here is a copy of `store.ID_LENGTH` and of the alphabet beside "
        f"it, and the copies drift: every one of these was looser than the store, so a tool and "
        f"`bin/docket check` disagreed about what an id is (`PL-KYW3`).\n"
        f"  Import it instead - `from docket.store import ID_PATTERN` after inserting "
        f"`subprojects/docket/src` on `sys.path` - and interpolate it, the way `docket`'s own "
        f"`vcs.py` and `roadmap.py` do. Where the pattern is deliberately not the store's, say "
        f"so with a `{MARKER}` comment on one of the lines it spans."
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Refuse a `PL-` literal the store could not mint, or a second spelling of "
        "its id grammar."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root to scan")
    args = parser.parse_args(argv)

    offenders = collect(args.root)
    if not offenders:
        print(
            "fixture-id: every `PL-` literal is one the store could mint, "
            "and the id grammar is spelled once"
        )
        return 0

    for rule in (LITERAL, GRAMMAR):
        found = [offender for offender in offenders if offender.rule == rule]
        if found:
            print(_report(found, args.root, rule), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
