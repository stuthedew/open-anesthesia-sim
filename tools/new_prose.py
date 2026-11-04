"""Print each long docstring, comment and document paragraph that a branch changed in the simulator.

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

**Which document prose is printed.** In `docs/MODEL.md` and `README.md`, the
documents that `doc_check.PROVENANCE_DOCUMENTS` holds to the specialist
standard, a unit is a paragraph or a table row, as `docket.markdown` reads the
blocks. A paragraph inside a list item or a block quote is a unit of its own. A
table row is a unit because one cell can carry a whole essay. A fence, an HTML
comment and a heading are not prose to review. The same `MIN_WORDS` applies
(`PL-ZT47`).

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

**Who reads each unit.** `.claude/rules/plain-writing.md` holds a table that
names the readers of each kind of text: what each knows, what each does not
know, and what each will do with the text. The table's first column names files
in code spans, where a span ending in "/" is a directory. The report lists the
readers of every file it prints a unit from, and each unit names its readers,
so the reviewer judges a unit against the reader it is for (`PL-R7Q6`). A unit
whose file no row names stops the report with exit 1, because a review with no
reader is the failure `PL-H76S` found.

**The reviewer's prompt is printed first.** `PROMPT` is the prompt's one
home, so the session hands the reviewer this tool's whole output and copies
nothing by hand. `tools/rejected_prose.py` prints the same prompt before the
paragraphs the owner rejected, which is how a change to it is tested
(`PL-FYGJ`). Where no unit changed, the prompt is not printed.

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

**`--compare` sets each passage the branch changed beside the text it
replaced, and lists the facts the branch removed** (`PL-JP8X`). A passage is
the units that one hunk of the diff reaches, widened to whole paragraphs,
table rows, docstrings or comments on both sides, and hunks parted only by
blank lines make one passage. It is printed with its words on the default
branch and now, whatever its length, unless only its spacing changed. A whole
section is not the passage, because `docs/MODEL.md` § "Displayed precision"
runs to about 8,000 words, where a growth of 50 would not show. Then, for each
file, it lists each equation, "no test yet" declaration, code span, citation,
number, item id and date that the file held at the fork and holds fewer times
now, read as `tools/model_rewrite.py` reads a fact. A Python file's facts are
read from its prose alone, on the rows where it stands. Facts are counted per
file, so a fact moved to another section, such as the note for developers,
prints nothing, and one the branch added to an item file is marked `moved`.
On `PL-ZDZ0` a passage grew from 163 words to about 210 and no review round
said so, and a trial copy editor rewrote a "no test yet" declaration as
"untested" (`PL-J1ZM`). This mode reads the working tree, and exits as the
default mode does.
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.arming import SOURCE, TESTS, imports_product  # noqa: E402
from docket.lines import split_lines  # noqa: E402
from docket.markdown import PARAGRAPH, TABLE, headings, tables  # noqa: E402
from docket.markdown import read as read_markdown  # noqa: E402
from docket.python import UNTOKENIZABLE, docstrings, refusal  # noqa: E402
from docket.release import code_spans  # noqa: E402
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
from model_rewrite import (  # noqa: E402
    Gone,
    added_facts,
    added_to_items,
    gone_facts,
    pair_restated,
    report_gone,
)

#: The fewest words a unit needs to be printed. `PL-Y55Q` drew its line between
#: short and long units here.
MIN_WORDS = 30
#: The documents whose paragraphs are reviewed as well, as repository paths.
DOCUMENTS = frozenset(path.as_posix() for path in doc_check.PROVENANCE_DOCUMENTS)

#: The rule whose table names the readers of each kind of text.
RULE = ROOT / ".claude" / "rules" / "plain-writing.md"
#: The prompt that the close-out's fresh reviewer is given before the units.
#: This file is its one home, and `tools/rejected_prose.py` tests each change
#: to it against the paragraphs the owner rejected (`PL-FYGJ`).
PROMPT = ROOT / "docs" / "prose-review" / "prompt.md"
#: The header of that table, which is how the tool finds it in the rule.
READER_HEADER = (
    "Kind of text",
    "Reader",
    "What they know",
    "What they do not know",
    "What they will do with it",
)

#: How many lines of code to print above and below each unit, so the reviewer
#: can see what an "it" or a name points at without opening the file.
CONTEXT_ROWS = 4


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


@dataclass(frozen=True)
class Reader:
    """One row of the plain-writing rule's reader table."""

    #: The files the row names, where one ending in "/" is a directory.
    paths: tuple[str, ...]
    who: str
    knows: str
    does_not_know: str
    will_do: str

    def reads(self, path: str) -> bool:
        """Whether the row names the file at `path`, itself or by its directory."""
        return any(
            path == named or (named.endswith("/") and path.startswith(named))
            for named in self.paths
        )


def reader_table(text: str) -> list[Reader]:
    """Every row of the reader table in the rule's `text`, in order.

    Raises `ValueError` where `text` holds no table with `READER_HEADER`, or a
    row of that table has the wrong number of cells.
    """
    for table in tables(split_lines(text)):
        if table.header != READER_HEADER:
            continue
        found = []
        for index, row in table.rows:
            if len(row) != len(READER_HEADER):
                raise ValueError(f"row {index + 1} of the reader table has {len(row)} cells")
            kind, who, knows, does_not_know, will_do = row
            paths = tuple(span["content"].strip() for span in code_spans(kind))
            found.append(Reader(paths, who, knows, does_not_know, will_do))
        return found
    raise ValueError(f"no table headed {' | '.join(READER_HEADER)}")


def readers_of(table: Sequence[Reader], path: str) -> list[Reader]:
    """The rows of `table` that name the file at `path`, in table order."""
    return [reader for reader in table if reader.reads(path)]


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


def document_units(path: str, source: str) -> list[Unit]:
    """Every paragraph and table row in the Markdown `source`, in the order they start.

    A table's delimiter row, the second line of the table, holds no prose and
    is left out.
    """
    lines = split_lines(source)
    found: list[Unit] = []
    for block in read_markdown(lines).blocks:
        if block.kind == PARAGRAPH:
            text = "\n".join(line.strip() for line in lines[block.start : block.end])
            found.append(Unit(path, "paragraph", block.start + 1, block.end, text))
        elif block.kind == TABLE:
            for index in range(block.start, block.end):
                if index != block.start + 1:
                    row = index + 1
                    found.append(Unit(path, "table row", row, row, lines[index].strip()))
    return found


def units_of(path: str, source: str) -> list[Unit]:
    """The prose units of the file at `path`: a document's paragraphs, or a Python file's."""
    if path in DOCUMENTS:
        return document_units(path, source)
    return prose_units(path, source)


def changed_units(path: str, source: str, rows: set[int] | None) -> list[Unit]:
    """The units of `MIN_WORDS` or more in `source` that a changed row falls inside.

    `rows` is `None` where the whole file is new, as `changed_rows` returns it.
    """
    return [
        unit
        for unit in units_of(path, source)
        if unit.words >= MIN_WORDS
        and (rows is None or any(unit.first <= row <= unit.last for row in rows))
    ]


def may_review(path: str) -> bool:
    """Whether the file at `path` is a reviewed document, or a Python file under `src/` or `tests/`.

    A Python file is then the simulator's only where `is_simulator_file` says so.
    """
    if path in DOCUMENTS:
        return True
    return PurePosixPath(path).suffix == ".py" and path.startswith((SOURCE, TESTS))


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
        document = path in DOCUMENTS
        if not may_review(path):
            continue
        if not committed and not (root / path).is_file():
            continue
        try:
            if committed:
                source = read_git(["show", f"HEAD:{path}"], root)
            else:
                source = (root / path).read_text(encoding="utf-8")
            if not document and not is_simulator_file(path, ast.parse(source, filename=path)):
                continue
            to = ["HEAD"] if committed else []
            rows = changed_rows(read_git(["diff", "-U0", fork, *to, "--", path], root))
            units.extend(changed_units(path, source, rows))
        except UNTOKENIZABLE as error:
            unread.append(f"{path}: {refusal(error)}")
    return Found(against, units, unread)


def text_at(root: Path, rev: str, path: str) -> str | None:
    """The file at `path` as commit `rev` holds it, or `None` where `rev` holds no such file."""
    if not listed_paths(read_git(["ls-tree", "-z", "--name-only", rev, "--", path], root)):
        return None
    return read_git(["show", f"{rev}:{path}"], root)


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
        before = text_at(root, since, path)
        if before is None:
            continue
        try:
            reviewed[path] = {unit.text for unit in units_of(path, before)}
        except UNTOKENIZABLE:
            pass
    return [unit for unit in found.units if unit.text not in reviewed[unit.path]]


@dataclass(frozen=True)
class Passage:
    """A run of prose the branch changed, beside the prose it replaced at the fork."""

    path: str
    #: The heading of the document section it stands in, "" before the first
    #: heading and in a Python file.
    section: str
    before: tuple[Unit, ...]
    after: tuple[Unit, ...]

    @property
    def words_before(self) -> int:
        return sum(unit.words for unit in self.before)

    @property
    def words_after(self) -> int:
        return sum(unit.words for unit in self.after)

    def rows(self) -> str:
        """The rows it spans now, or at the fork where nothing of it is left."""
        units = self.after or self.before
        return f"rows {units[0].first}-{max(unit.last for unit in units)}"


def touched(units: Sequence[Unit], first: int, count: int) -> set[int]:
    """The indices of `units` that a hunk's range of `count` rows from row `first` reaches.

    An empty range stands after row `first`, as git writes it, so it reaches
    only a unit that holds both that row and the next.
    """
    if not count:
        return {at for at, unit in enumerate(units) if unit.first <= first < unit.last}
    last = first + count - 1
    return {at for at, unit in enumerate(units) if unit.first <= last and unit.last >= first}


def changed_passages(path: str, before: str | None, after: str | None, patch: str) -> list[Passage]:
    """Each run of prose that `patch` changes, widened to whole units on both sides.

    `patch` is a `-U0` diff from `before` to `after`. Two hunks make one
    passage where the rows between them hold only blank lines and rows of
    the units they reach, so a paragraph split in two, or edited in two places,
    is one passage. A hunk that reaches no unit, such as a change to code, is
    left out. A file new on the branch, or removed by it, is one passage.
    """
    old = units_of(path, before) if before is not None else []
    new = units_of(path, after) if after is not None else []
    if before is None or after is None:
        return [Passage(path, "", tuple(old), tuple(new))] if old or new else []
    lines = split_lines(after)
    sections = (headings(split_lines(before)), headings(lines)) if path in DOCUMENTS else ([], [])
    groups: list[tuple[set[int], set[int], int]] = []
    for hunk in doc_check.HUNK_RE.finditer(patch):
        start, size = int(hunk.group(3)), int(hunk.group(4) or 1)
        reached_old = touched(old, int(hunk.group(1)), int(hunk.group(2) or 1))
        reached_new = touched(new, start, size)
        if not reached_old and not reached_new:
            continue
        top, bottom = (start, start + size - 1) if size else (start + 1, start)
        if groups:
            held_old, held_new, end = groups[-1]
            covered = {
                row
                for at in held_new | reached_new
                for row in range(new[at].first, new[at].last + 1)
            }
            gap = range(end + 1, top)
            if held_old & reached_old or all(
                row in covered or not lines[row - 1].strip() for row in gap
            ):
                groups[-1] = (held_old | reached_old, held_new | reached_new, bottom)
                continue
        groups.append((reached_old, reached_new, bottom))
    found = []
    for reached_old, reached_new, _ in groups:
        passage = Passage(
            path,
            "",
            tuple(old[at] for at in sorted(reached_old)),
            tuple(new[at] for at in sorted(reached_new)),
        )
        if (
            " ".join(unit.text for unit in passage.before).split()
            == " ".join(unit.text for unit in passage.after).split()
        ):
            continue
        marks, units = (
            (sections[1], passage.after) if passage.after else (sections[0], passage.before)
        )
        titles = [mark.title for mark in marks if mark.line < units[0].first]
        found.append(Passage(path, titles[-1] if titles else "", passage.before, passage.after))
    return found


def fact_text(path: str, source: str | None) -> str:
    """The text whose facts are counted: a document whole, or a Python file's prose.

    A Python file's prose keeps the rows it stands on, and every other row is
    blank, so each fact is placed on the file's own row and no number in code
    is read.
    """
    if source is None:
        return ""
    if path in DOCUMENTS:
        return source
    rows = [""] * len(split_lines(source))
    for unit in prose_units(path, source):
        for offset, line in enumerate(unit.text.split("\n")[: unit.last - unit.first + 1]):
            rows[unit.first - 1 + offset] = line
    return "\n".join(rows)


@dataclass
class Comparison:
    """Each changed passage beside its form at the fork, and each file's removed facts."""

    base: str
    against: str
    passages: list[Passage]
    gone: dict[str, list[Gone]]
    unread: list[str]


def compare(root: Path, base: str) -> Comparison:
    """The passages the branch changed and the facts it removed, from the fork to the working tree.

    A passage counts as changed when its words differ, so text reflowed onto
    other lines is not a change.
    """
    fork, against = doc_check._diff_from(root, base)
    moved = added_to_items(root, fork)
    found = Comparison(base, against, [], {}, [])
    for path in doc_check._changed_paths(root, fork):
        if not may_review(path):
            continue
        before = text_at(root, fork, path)
        after = (root / path).read_text(encoding="utf-8") if (root / path).is_file() else None
        try:
            if path not in DOCUMENTS and not any(
                text is not None and is_simulator_file(path, ast.parse(text, filename=path))
                for text in (before, after)
            ):
                continue
            patch = read_git(["diff", "-U0", fork, "--", path], root)
            found.passages += changed_passages(path, before, after, patch)
            old_facts, new_facts = fact_text(path, before), fact_text(path, after)
        except UNTOKENIZABLE as error:
            found.unread.append(f"{path}: {refusal(error)}")
            continue
        gone = gone_facts(old_facts, new_facts, moved)
        found.gone[path] = pair_restated(
            old_facts, new_facts, gone, added_facts(old_facts, new_facts)
        )[0]
    return found


def passage_line(passage: Passage, base: str) -> str:
    """One line naming a changed passage, with its words at the fork and now."""
    where = passage.path
    if passage.section:
        where += f' § "{passage.section}"'
    before, after = passage.words_before, passage.words_after
    if not passage.before:
        return f"{where}, {passage.rows()}: new, {after} words"
    if not passage.after:
        return f"{where}, {passage.rows()} on {base}: removed, {before} words"
    change = after - before
    more = f"{change} more" if change > 0 else f"{-change} fewer" if change else "the same count"
    return f"{where}, {passage.rows()}: {before} words on {base}, {after} now, {more}"


def compare_report(found: Comparison) -> str:
    """The changed passages and their words, each file's removed facts, and the files not read."""
    out: list[str] = []
    if found.passages:
        out += [
            f"{len(found.passages)} passages of the simulator's files changed their prose, "
            f"against {found.against}. Each is the paragraphs, docstrings or comments the "
            "branch changed, with their words before and after.",
            "",
        ]
        out += [f"  {passage_line(passage, found.base)}" for passage in found.passages]
    else:
        out.append(
            f"No passage of the simulator's files changed its prose, against {found.against}."
        )
    for path, gone in found.gone.items():
        if gone:
            out += ["", *report_gone(gone, found.against, path)]
    if found.gone and not any(found.gone.values()):
        out += ["", f"These files hold every fact they held on {found.base}, as often."]
    if found.unread:
        out += ["", "Not read, because Python would not parse the file:"]
        out += [f"  {line}" for line in found.unread]
    return "\n".join(out)


def excerpt(lines: Sequence[str], unit: Unit) -> Iterator[str]:
    """The unit's rows marked `>`, with `CONTEXT_ROWS` rows of code each side marked `|`."""
    start = max(1, unit.first - CONTEXT_ROWS)
    end = min(len(lines), unit.last + CONTEXT_ROWS)
    for row in range(start, end + 1):
        mark = ">" if unit.first <= row <= unit.last else "|"
        yield f"{row:>5} {mark} {lines[row - 1]}"


def unread_by_anyone(table: Sequence[Reader], found: Found) -> list[str]:
    """Each file in `found` that holds a unit and that no row of `table` names."""
    return sorted({unit.path for unit in found.units if not readers_of(table, unit.path)})


def reader_lines(table: Sequence[Reader], paths: Iterable[str]) -> list[str]:
    """For each file in `paths`, in order and once, the full row of each of its readers."""
    out: list[str] = []
    for path in dict.fromkeys(paths):
        out += ["", f"Readers of {path}:"]
        for reader in readers_of(table, path):
            out += [
                f"  - {reader.who}.",
                f"    Knows: {reader.knows}",
                f"    Does not know: {reader.does_not_know}",
                f"    Will: {reader.will_do}",
            ]
    return out


def unit_lines(number: int, unit: Unit, rows: Iterable[str], table: Sequence[Reader]) -> list[str]:
    """The unit's numbered header, naming its readers from `table`, then its `rows`."""
    who = "; ".join(reader.who for reader in readers_of(table, unit.path))
    return [
        "",
        f"[{number}] {unit.path}, rows {unit.first}-{unit.last}, "
        f"{unit.kind}, {unit.words} words, for: {who}",
        *rows,
    ]


def report(root: Path, found: Found, table: Sequence[Reader]) -> str:
    """The readers, the units with their excerpts, then each file that was not read.

    Every file holding a unit must have a row in `table`; `unread_by_anyone`
    names those that do not, and `main` refuses to print the report while any
    does.
    """
    out: list[str] = []
    if found.units:
        out.append(
            f"{len(found.units)} docstrings, comments and document paragraphs of {MIN_WORDS} "
            f"words or more changed in the simulator's files, against {found.against}. Rows "
            "marked > are the unit; rows marked | are the lines around it. Judge each unit "
            "for the readers its header names, as the list below describes them."
        )
        out += reader_lines(table, (unit.path for unit in found.units))
        texts: dict[str, list[str]] = {}
        for number, unit in enumerate(found.units, start=1):
            if unit.path not in texts:
                texts[unit.path] = split_lines((root / unit.path).read_text(encoding="utf-8"))
            out += unit_lines(number, unit, excerpt(texts[unit.path], unit), table)
    else:
        out.append(
            f"No docstring, comment or document paragraph of {MIN_WORDS} words or more changed "
            f"in the simulator's files, against {found.against}."
        )
    if found.unread:
        out += ["", "Not read, because Python would not parse the file:"]
        out += [f"  {line}" for line in found.unread]
    return "\n".join(out)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to run in")
    parser.add_argument("--base", help="branch to diff against; the default branch by default")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--compare",
        action="store_true",
        help="print each changed passage's words on the base and now, and each fact the "
        "branch removed",
    )
    modes.add_argument(
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
        if args.compare:
            print(compare_report(compare(root, base)))
        elif args.count is not None:
            found = branch_prose(root, base, committed=True)
            if found.unread:
                for line in found.unread:
                    print(f"new_prose: not read: {line}", file=sys.stderr)
                return 2
            print(len(unreviewed(root, found, args.count or None)))
        else:
            table = reader_table(RULE.read_text(encoding="utf-8"))
            found = branch_prose(root, base)
            missing = unread_by_anyone(table, found)
            if missing:
                for path in missing:
                    print(
                        f"new_prose: no answer: no row of the reader table in {RULE.name} "
                        f"names {path}",
                        file=sys.stderr,
                    )
                return 1
            if found.units:
                print(PROMPT.read_text(encoding="utf-8"))
            print(report(root, found, table))
    except ValueError as error:
        print(f"new_prose: no answer: {RULE.name}: {error}", file=sys.stderr)
        return 1
    except (GitUnanswered, OSError) as error:
        print(f"new_prose: no answer: {error!r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
