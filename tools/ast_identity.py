"""Say whether each file's code is the same at two revisions, docstrings and comments aside.

A release cut states that nothing computational moved under `src/`. Where the
simulator's tree objects are identical at both ends, that is proved by the
hashes. Where one moved, the fallback was to read the diff and judge each
changed line to be a comment, which is the judgment the safety-critical
standard says a clinical claim must not rest on. v0.5.2 was the first cut where
that happened, for a docstring-only change, and `PL-JYTJ` proved it with a
script that compared the two files' syntax trees and was then lost
(`PL-VHHB`).

This is that comparison, kept. For each Python file it parses both versions,
removes every docstring, and compares `ast.dump` of the two trees. A comment
never reaches the tree, and `ast.dump` leaves out line and column numbers, so
equal dumps mean no executable statement changed. A docstring is removed
rather than replaced, so a docstring added or deleted reads as unchanged too.
A file that is not Python is compared as text.

`python3 tools/ast_identity.py OLD NEW PATH...` takes two revisions and one or
more paths. A path that names a directory stands for every file under it at
either revision. It prints one line per file and exits 0 when every file's
code is unchanged, 1 when any changed, was added or was removed, and 2 when a
revision cannot be read or a Python file does not parse. The simulator's source
targets the project's own Python release, which may be newer than the system
`python3`, so run it under `uv run python` when it compares `src/`.

It decides only the decidable half. A docstring is where a unit, a model
version or a provenance note is recorded, so whether a docstring-only change
is safe is still the reader's call, and the release mode asks for that reading
beside this verdict. Nothing under `src/` reads `__doc__` on 2026-10-25, so a
docstring there changes no behaviour. A program that did read it would change
with a change this tool calls unchanged.

Standard library only, like every tool here. Git is read through
`docket.vcs.read_git`, the one runner `tools/fact_home_check.py` allows.
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.vcs import GitUnanswered, listed_paths, read_git  # noqa: E402

#: The verdict for each file, as the line for it prints it.
SAME = "unchanged"
SAME_BUT_DOCSTRINGS = "unchanged apart from docstrings and comments"
CHANGED = "changed"
ADDED = "added"
REMOVED = "removed"
TEXT_SAME = "unchanged, compared as text"
TEXT_CHANGED = "changed, compared as text"

#: The verdicts under which a file's code did not move.
UNMOVED = frozenset({SAME, SAME_BUT_DOCSTRINGS, TEXT_SAME})

#: The nodes whose first statement, when it is a string, Python takes as a docstring.
_DOCUMENTED = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def without_docstrings(source: str, name: str) -> str:
    """`ast.dump` of `source` with every docstring removed.

    `name` is used only in the `SyntaxError` a file that does not parse raises.
    A body left empty by the removal is left empty: the dump is compared, never
    compiled.
    """

    tree = ast.parse(source, filename=name)
    for node in ast.walk(tree):
        if not isinstance(node, _DOCUMENTED):
            continue
        body = node.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            del body[0]
    return ast.dump(tree)


def verdict(old: str | None, new: str | None, path: str) -> str:
    """What changed in the file at `path`, given its text at each revision or None where absent."""

    if old is None and new is None:
        raise ValueError(f"{path} is at neither revision")
    if old is None:
        return ADDED
    if new is None:
        return REMOVED
    if not path.endswith(".py"):
        return TEXT_SAME if old == new else TEXT_CHANGED
    if old == new:
        return SAME
    if without_docstrings(old, path) == without_docstrings(new, path):
        return SAME_BUT_DOCSTRINGS
    return CHANGED


def files_at(revision: str, paths: Sequence[str], root: Path) -> set[str]:
    """Every file the revision holds at or under each of `paths`."""

    listing = read_git(["ls-tree", "-r", "-z", "--name-only", revision, "--", *paths], root)
    return set(listed_paths(listing))


def text_at(revision: str, path: str, root: Path) -> str:
    """The file's text at the revision, which the caller has seen it holds."""

    return read_git(["show", f"{revision}:{path}"], root)


def compare(old: str, new: str, paths: Sequence[str], root: Path) -> list[tuple[str, str]]:
    """Each file under `paths` at either revision, with its verdict, in path order."""

    before = files_at(old, paths, root)
    after = files_at(new, paths, root)
    return [
        (
            path,
            verdict(
                text_at(old, path, root) if path in before else None,
                text_at(new, path, root) if path in after else None,
                path,
            ),
        )
        for path in sorted(before | after)
    ]


def main(argv: Sequence[str] | None = None, root: Path = ROOT) -> int:
    """Print each file's verdict, and exit 0 only when no file's code moved."""

    parser = argparse.ArgumentParser(
        description="say whether each file's code is the same at two revisions, docstrings aside"
    )
    parser.add_argument("old", metavar="OLD", help="the earlier revision, such as a release tag")
    parser.add_argument("new", metavar="NEW", help="the later revision, such as HEAD")
    parser.add_argument("paths", metavar="PATH", nargs="+", help="a file or a directory")
    args = parser.parse_args(argv)

    try:
        for revision in (args.old, args.new):
            read_git(["rev-parse", "--verify", f"{revision}^{{commit}}"], root)
        results = compare(args.old, args.new, args.paths, root)
    except GitUnanswered as silence:
        print(f"ast_identity: git could not read {args.old} or {args.new}: {silence}")
        return 2
    except SyntaxError as unparsed:
        print(
            f"ast_identity: Python {sys.version.split()[0]} cannot parse {unparsed.filename}"
            f" ({unparsed.msg}), so nothing about it is claimed; run under `uv run python`"
            " if the project's own interpreter can"
        )
        return 2
    if not results:
        print(f"ast_identity: no file under {' '.join(args.paths)} at {args.old} or {args.new}")
        return 2

    moved = [path for path, said in results if said not in UNMOVED]
    for path, said in results:
        print(f"{path}: {said}")
    if moved:
        print(f"{len(moved)} of {len(results)} files moved between {args.old} and {args.new}")
        return 1
    print(f"no code moved in {len(results)} files between {args.old} and {args.new}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
