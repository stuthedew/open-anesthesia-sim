"""Print each long docstring and comment that a branch added or changed in the simulator.

The close-out step in `.claude/skills/docket/modes/close-out.md` hands this
tool's output to one fresh reviewer, who reads each unit against
`.claude/rules/plain-writing.md` and returns rewrites. The reviewer opens no
files, because everything it needs is printed here. Each tool call a subagent
makes costs another turn at its full starting context, so a reviewer that reads
nothing costs about one turn (`PL-PRCS`).

**Which prose is printed.** A unit is a docstring, as `docket.python.docstrings`
decides, or a run of comment lines, as `doc_check._python_comments` joins them.
A unit is printed when it has `MIN_WORDS` words or more and a line the branch
changed falls inside it. In `PL-Y55Q`'s blind re-measure, short units were
awkward in 25% of verdicts and long ones in 61%, so the long ones are where a
review pays (project owner, 2026-10-18, ratified, `PL-PRCS`).

**Which files are the simulator's.** A Python file under `src/`, or a Python
file under `tests/` that imports the product package, by `docket.arming`'s
`imports_product`, the rule that `tools/workflow_paths_check.py` applies to the
lane boundary. A support module that imports the product, such as a reference
gate under `tests/reference/`, is included, because that check also places it
on the simulator's side. The owner chose simulator branches only over every
branch and over no step (2026-10-18, ratified, `PL-PRCS`).

**Which lines changed.** The diff runs from the commit where the branch forked
from the default branch to the working tree, and includes files that git does
not track yet, as `tools/diff_mutation.py` reads it. A file that is new on the
branch has every line changed.

Exits 0 when it read the diff, whether or not it printed a unit. A changed file
that will not parse is named in a "Not read" line, so a partial answer is never
given as a whole one. Exits 1 when the diff could not be read or the default
branch is unknown.

**`--count` prints only how many units need a review, for `bin/docket arm`.**
`arm` holds a simulator branch until step 8's review is recorded as a
`Prose-review:` trailer, and it runs this through `docket.toml`'s
`prose_count_command` (`PL-W04Z`). This mode reads the committed branch, from
the fork to `HEAD`, because `arm` judges commits and not the working tree.
`--count REV` names the commit that carries the newest record. A unit then
counts only when its text is not a unit of the same file at `REV`, so a code
fix after the review needs no second review, while a new or reworded long unit
does. Comparing texts rather than diffing from `REV` keeps out the prose that a
merge of the default branch brings in, because that prose is not in the
branch's own diff from the fork. The count is one line holding a whole number.
Exits 2, printing the unread files to standard error, when a changed file will
not parse, because a count that skipped a file is not a count.
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.arming import TESTS, imports_product  # noqa: E402
from docket.lines import split_lines  # noqa: E402
from docket.python import UNTOKENIZABLE, docstrings, refusal  # noqa: E402
from docket.vcs import (  # noqa: E402
    GitUnanswered,
    changed_path_args,
    default_base,
    listed_paths,
    read_git,
    resolved,
)

import doc_check  # noqa: E402
from diff_mutation import changed_rows  # noqa: E402

#: The fewest words a unit needs to be printed. `PL-Y55Q` drew its line between
#: short and long units here.
MIN_WORDS = 30
#: How many lines of code to print above and below each unit, so the reviewer
#: can see what an "it" or a name points at without opening the file.
CONTEXT_ROWS = 4
#: The simulator's source tree. A test file is the simulator's by its imports.
SOURCE = "src/"


@dataclass(frozen=True)
class Unit:
    """One docstring or run of comment lines, with its file and the rows it spans."""

    path: str
    kind: str
    first: int
    last: int
    text: str

    @property
    def words(self) -> int:
        return len(self.text.split())


def is_simulator_file(path: str, tree: ast.Module) -> bool:
    """Whether the Python file at `path`, parsed as `tree`, is the simulator's."""
    return path.startswith(SOURCE) or (path.startswith(TESTS) and imports_product(tree))


def prose_units(path: str, source: str) -> list[Unit]:
    """Every docstring and comment run in `source`, in the order they start.

    Raises one of `UNTOKENIZABLE` where Python refuses `source`.
    """
    found = [
        Unit(path, "docstring", node.lineno, node.end_lineno or node.lineno, node.value)
        for node in docstrings(ast.parse(source, filename=path))
        if isinstance(node.value, str)
    ]
    for row, text in doc_check._python_comments(source.encode("utf-8")):
        found.append(Unit(path, "comment", row, row + text.count("\n"), text))
    return sorted(found, key=lambda unit: unit.first)


def changed_units(path: str, source: str, rows: set[int] | None) -> list[Unit]:
    """The units of `MIN_WORDS` or more in `source` that a changed row falls inside.

    `rows` is `None` where the whole file is new, as `changed_rows` returns it.
    """
    return [
        unit
        for unit in prose_units(path, source)
        if unit.words >= MIN_WORDS
        and (rows is None or any(unit.first <= row <= unit.last for row in rows))
    ]


@dataclass
class Found:
    """What the branch changed in the simulator's prose, and what could not be read."""

    against: str
    units: list[Unit]
    #: Each changed Python file that would not parse, with Python's reason.
    unread: list[str]


def branch_prose(root: Path, base: str, *, committed: bool = False) -> Found:
    """The long units changed between the fork from `base` and the working tree.

    With `committed`, the units changed between the fork and `HEAD`, read from
    the commits alone, so an uncommitted edit counts for nothing.
    """
    fork, against = doc_check._diff_from(root, base)
    if committed:
        listing = changed_path_args("diff", "--name-only", "--diff-filter=d", fork, "HEAD", "--")
        paths = sorted(set(listed_paths(read_git(listing, root))))
    else:
        paths = doc_check._changed_paths(root, fork)
    units: list[Unit] = []
    unread: list[str] = []
    for path in paths:
        if PurePosixPath(path).suffix != ".py":
            continue
        if not (path.startswith(SOURCE) or path.startswith(TESTS)):
            continue
        if not committed and not (root / path).is_file():
            continue
        try:
            if committed:
                source = read_git(["show", f"HEAD:{path}"], root)
            else:
                source = (root / path).read_text(encoding="utf-8")
            if not is_simulator_file(path, ast.parse(source, filename=path)):
                continue
            to = ["HEAD"] if committed else []
            rows = changed_rows(read_git(["diff", "-U0", fork, *to, "--", path], root))
            units.extend(changed_units(path, source, rows))
        except UNTOKENIZABLE as error:
            unread.append(f"{path}: {refusal(error)}")
    return Found(against, units, unread)


def unreviewed(root: Path, found: Found, since: str | None) -> list[Unit]:
    """The units in `found` whose text is not a unit of the same file at commit `since`.

    With no `since`, every unit. A file that `since` does not hold, or holds in
    a form Python refuses, has no units there, so all of its units count.
    """
    if since is None:
        return list(found.units)
    reviewed: dict[str, set[str]] = {}
    for path in {unit.path for unit in found.units}:
        reviewed[path] = set()
        if not listed_paths(read_git(["ls-tree", "-z", "--name-only", since, "--", path], root)):
            continue
        try:
            before = read_git(["show", f"{since}:{path}"], root)
            reviewed[path] = {unit.text for unit in prose_units(path, before)}
        except UNTOKENIZABLE:
            pass
    return [unit for unit in found.units if unit.text not in reviewed[unit.path]]


def excerpt(lines: Sequence[str], unit: Unit) -> Iterator[str]:
    """The unit's rows marked `>`, with `CONTEXT_ROWS` rows of code each side marked `|`."""
    start = max(1, unit.first - CONTEXT_ROWS)
    end = min(len(lines), unit.last + CONTEXT_ROWS)
    for row in range(start, end + 1):
        mark = ">" if unit.first <= row <= unit.last else "|"
        yield f"{row:>5} {mark} {lines[row - 1]}"


def report(root: Path, found: Found) -> str:
    """The units with their excerpts, then each file that was not read."""
    out: list[str] = []
    if found.units:
        out.append(
            f"{len(found.units)} docstrings and comments of {MIN_WORDS} words or more changed "
            f"in the simulator's files, against {found.against}. Rows marked > are the unit; "
            "rows marked | are the code around it."
        )
        texts: dict[str, list[str]] = {}
        for number, unit in enumerate(found.units, start=1):
            if unit.path not in texts:
                texts[unit.path] = split_lines((root / unit.path).read_text(encoding="utf-8"))
            out += [
                "",
                f"[{number}] {unit.path}, rows {unit.first}-{unit.last}, "
                f"{unit.kind}, {unit.words} words",
                *excerpt(texts[unit.path], unit),
            ]
    else:
        out.append(
            f"No docstring or comment of {MIN_WORDS} words or more changed in the simulator's "
            f"files, against {found.against}."
        )
    if found.unread:
        out += ["", "Not read, because Python would not parse the file:"]
        out += [f"  {line}" for line in found.unread]
    return "\n".join(out)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to run in")
    parser.add_argument("--base", help="branch to diff against; the default branch by default")
    parser.add_argument(
        "--count",
        nargs="?",
        const="",
        metavar="REV",
        help="print only how many committed units need a review, for `bin/docket arm`, "
        "leaving out units already at commit REV where one is given",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    base = args.base or default_base(root)
    if args.base is None and not resolved(base):
        print(
            f"new_prose: no answer: the default branch is unknown ({base!r} is a guess)",
            file=sys.stderr,
        )
        return 1
    try:
        if args.count is not None:
            found = branch_prose(root, base, committed=True)
            if found.unread:
                for line in found.unread:
                    print(f"new_prose: not read: {line}", file=sys.stderr)
                return 2
            print(len(unreviewed(root, found, args.count or None)))
        else:
            print(report(root, branch_prose(root, base)))
    except (GitUnanswered, OSError) as error:
        print(f"new_prose: no answer: {error!r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
