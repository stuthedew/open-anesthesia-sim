"""Print the prose a branch changed, inside the section around it, for the copy editor.

Close-out step 8 in `.claude/skills/docket/modes/close-out.md` saves this
tool's output to a file and hands that file to the copy-editor agent,
`.claude/agents/copy-editor.md`. The agent loads none of this repository's
instructions, so the output opens with the text of
`.claude/rules/plain-writing.md`, and the agent reads that one file and
nothing else. Each tool call a subagent makes costs another turn at its full
context. On its first branch the agent read 29 passages in four reads of
this tool's output and 179,031 tokens (`PL-PRCS`, `PL-22T5`).

**Which files are read.** A Markdown or Python file is read when a row of the
rule's reader table names it, itself or by its directory, so the table decides
what is reviewed (`PL-22T5`). A changed file that holds a passage to review
and that no row names is listed under "Not reviewed", because nobody has said
who reads it.

**What a unit is.** In a Python file, a unit is a docstring, as
`docket.python.docstrings` decides, or a run of comment lines, as
`doc_check._python_comments` joins them. In a Markdown file, it is a paragraph
or a table row, as `docket.markdown` reads the blocks once the YAML front
matter is blanked row for row. A paragraph inside a list item or a block quote
is a unit of its own. A table row is a unit because one cell can carry a whole
essay. A fence, an HTML comment and a heading are not prose to review
(`PL-ZT47`).

**Which lines changed.** The diff runs from the commit where the branch forked
from the default branch to the working tree, and includes files that git does
not track yet, as `tools/diff_mutation.py` reads it. A file that is new on the
branch has every line changed.

**What is reviewed.** Each passage that `changed_passages` finds is reviewed
when it has `MIN_WORDS` words or more now. In `PL-Y55Q`'s blind re-measure,
short units were awkward in 25% of verdicts and long ones in 61%, so the long
ones are where a review pays (project owner, 2026-10-18, ratified, `PL-PRCS`).
In a Markdown file, the copy editor reads the passage's whole section, from the
heading above it to the next heading. It may rewrite the passage and the one
unit on each side of it inside that section, so it can fold new text into the
paragraph beside it. It may not rewrite the rest of the section, because
`docs/MODEL.md` § "Displayed precision" runs to about 8,000 words, and a
one-sentence fix there would become a rewrite of all of them. That limit is a
placeholder for the owner to overrule (`PL-22T5`). Two passages that would
share a unit are reviewed as one. In a Python file, each long unit is reviewed
alone, with `CONTEXT_ROWS` rows of code on each side.

**Who reads each passage.** `.claude/rules/plain-writing.md` holds a table that
names the readers of each kind of text: what each knows, what each does not
know, and what each will do with the text. The table's first column names files
in code spans, where a span ending in "/" is a directory. The report lists the
readers of every file it prints a passage from, and each passage names its
readers, so the copy editor judges it for the reader it is for (`PL-R7Q6`).

Exits 0 when it read the diff, whether or not it printed a passage. A changed
file that will not parse is named in a "Not read" line, so a partial result is
never given as a whole one. Exits 1 when the diff could not be read or the
default branch is unknown.

**`--draft FILE --kind WORDS` prepares a reply or a pull request body for review
before it is sent.** It prints the rule, the reader rows whose first cell
contains WORDS, and the whole file as passage 1 (`PL-J1ZM` part 3). It exits 1
when no row's first cell contains WORDS.

**`--count` prints only how many units need a review, for `bin/docket arm`.**
`arm` holds a branch that waits on the owner's review until step 8's review is
recorded as a `Prose-review:` trailer, and it runs this through `docket.toml`'s
`prose_count_command` (`PL-W04Z`). It counts long units rather than passages,
so a passage of several short paragraphs is reviewed and not counted. This
mode reads the committed branch, from the fork to `HEAD`, because `arm` judges
commits and not the working tree.
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
the units that one hunk of the diff touches, widened to whole paragraphs,
table rows, docstrings or comments on both sides. Hunks parted only by blank
lines make one passage. It is printed with its words on the default branch and
now, whatever its length, unless only its spacing changed. A whole section is
not the passage, because `docs/MODEL.md` § "Displayed precision" runs to about
8,000 words, where a growth of 50 words would not show. Then, for each file, it
lists each equation, "no test yet" declaration, code span, citation, number,
item id and date that the file held at the fork and holds fewer times now, read
as `tools/model_rewrite.py` reads a fact. A Python file's facts are read from
its prose alone, on the rows where it stands. Facts are counted per file, so a
fact moved to another section, such as the note for developers, prints
nothing. A fact that the file lost and the branch added to an item file is
marked `moved`. On `PL-ZDZ0` a passage grew from 163 words to about 210 and no
review round said so, and a trial copy editor rewrote a "no test yet"
declaration as "untested" (`PL-J1ZM`). This mode reads the working tree, and
exits as the default mode does.
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.lines import split_lines  # noqa: E402
from docket.markdown import PARAGRAPH, TABLE, Heading, headings, tables  # noqa: E402
from docket.markdown import read as read_markdown  # noqa: E402
from docket.model import FRONT_MATTER_RE  # noqa: E402
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
#: The rule whose table names the readers of each kind of text.
RULE = ROOT / ".claude" / "rules" / "plain-writing.md"
#: The copy editor's agent definition, whose body is its prompt. This file is
#: the prompt's one home, and `tools/rejected_prose.py` tests each change to it
#: against the paragraphs the owner rejected or named gold standards (`PL-FYGJ`,
#: `PL-556C`, `PL-22T5`).
PROMPT = ROOT / ".claude" / "agents" / "copy-editor.md"
#: The header of that table, which is how the tool finds it in the rule.
READER_HEADER = (
    "Kind of text",
    "Reader",
    "What they know",
    "What they do not know",
    "What they will do with it",
)

#: How many lines of code to print above and below a Python unit, so the copy
#: editor can see what an "it" or a name points at without opening the file.
#: A higher number lengthens the file the copy editor reads. `PL-PRCS` set it
#: at 4 and recorded no reason for that number (`PL-22T5`).
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

    #: The row's first cell, which names the kind of text in words.
    kind: str
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
            found.append(Reader(kind, paths, who, knows, does_not_know, will_do))
        return found
    raise ValueError(f"no table headed {' | '.join(READER_HEADER)}")


def readers_of(table: Sequence[Reader], path: str) -> list[Reader]:
    """The rows of `table` that name the file at `path`, in table order."""
    return [reader for reader in table if reader.reads(path)]


def rule_table() -> list[Reader]:
    """The reader table of the plain-writing rule at `RULE`."""
    return reader_table(RULE.read_text(encoding="utf-8"))


def is_document(path: str) -> bool:
    """Whether the file at `path` is Markdown, whose units are paragraphs and table rows."""
    return PurePosixPath(path).suffix == ".md"


def blank_front_matter(source: str) -> str:
    """`source` with the YAML front matter that opens it turned into blank lines, row for row.

    `docket.markdown` would otherwise read the front matter's closing `---` as
    the underline of a heading.
    """
    match = FRONT_MATTER_RE.match(source)
    if match is None:
        return source
    return "\n" * source[: match.start(2)].count("\n") + match.group(2)


def markdown_lines(source: str) -> list[str]:
    """The lines of the Markdown `source`, with its front matter blank."""
    return split_lines(blank_front_matter(source))


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
    lines = markdown_lines(source)
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
    if is_document(path):
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
    """Whether the file at `path` holds prose units, as a Markdown or Python file does."""
    return PurePosixPath(path).suffix in {".md", ".py"}


@dataclass
class Found:
    """The long units the branch changed in the files that the reader table names."""

    against: str
    units: list[Unit]
    #: Each changed Python file that would not parse, with Python's reason.
    unread: list[str]


def branch_prose(
    root: Path, base: str, table: Sequence[Reader] | None = None, *, committed: bool = False
) -> Found:
    """The long units changed between the fork from `base` and the working tree.

    Only a file that a row of `table` names is read, and `table` defaults to the
    reader table in the rule. With `committed`, it returns the units changed
    between the fork and `HEAD`, read from the commits alone, so an uncommitted
    edit counts for nothing.
    """
    table = rule_table() if table is None else table
    fork, against = doc_check._diff_from(root, base)
    if committed:
        listing = changed_path_args("diff", "--name-only", "--diff-filter=d", fork, "HEAD", "--")
        paths = sorted(set(listed_paths(read_git(listing, root))))
    else:
        paths = doc_check._changed_paths(root, fork)
    units: list[Unit] = []
    unread: list[str] = []
    for path in paths:
        if not may_review(path) or not readers_of(table, path):
            continue
        if not committed and not (root / path).is_file():
            continue
        try:
            if committed:
                source = read_git(["show", f"HEAD:{path}"], root)
            else:
                source = (root / path).read_text(encoding="utf-8")
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
    sections = (
        (headings(markdown_lines(before)), headings(markdown_lines(after)))
        if is_document(path)
        else ([], [])
    )
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
    if is_document(path):
        return blank_front_matter(source)
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


def compare(root: Path, base: str, table: Sequence[Reader] | None = None) -> Comparison:
    """The passages the branch changed and the facts it removed, from the fork to the working tree.

    Only a file that a row of `table` names is read, and `table` defaults to the
    reader table in the rule. A passage counts as changed when its words differ,
    so text reflowed onto other lines is not a change.
    """
    table = rule_table() if table is None else table
    fork, against = doc_check._diff_from(root, base)
    moved = added_to_items(root, fork)
    found = Comparison(base, against, [], {}, [])
    for path in doc_check._changed_paths(root, fork):
        if not may_review(path) or not readers_of(table, path):
            continue
        before = text_at(root, fork, path)
        after = (root / path).read_text(encoding="utf-8") if (root / path).is_file() else None
        try:
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
            f"{len(found.passages)} passages of the reviewed files changed their prose, "
            f"against {found.against}. Each is the paragraphs, docstrings or comments the "
            "branch changed, with their words before and after.",
            "",
        ]
        out += [f"  {passage_line(passage, found.base)}" for passage in found.passages]
    else:
        out.append(f"No passage of the reviewed files changed its prose, against {found.against}.")
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


def describe(readers: Iterable[Reader]) -> list[str]:
    """The full row of each of `readers`, a few lines each."""
    out: list[str] = []
    for reader in readers:
        out += [
            f"  - {reader.who}.",
            f"    Knows: {reader.knows}",
            f"    Does not know: {reader.does_not_know}",
            f"    Will: {reader.will_do}",
        ]
    return out


def reader_lines(table: Sequence[Reader], paths: Iterable[str]) -> list[str]:
    """For each file in `paths`, in order and once, the full row of each of its readers."""
    out: list[str] = []
    for path in dict.fromkeys(paths):
        out += ["", f"Readers of {path}:", *describe(readers_of(table, path))]
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


@dataclass(frozen=True)
class Review:
    """A changed passage as the copy editor gets it: the rows it may rewrite and those it reads."""

    path: str
    #: The heading of the document section it stands in, "" before the first
    #: heading and in a Python file.
    section: str
    #: The units it may rewrite, in order: the changed units, and in a document
    #: the unit beside them on each side inside their section.
    editable: tuple[Unit, ...]
    #: The first and last rows it reads: a document's whole section, or a
    #: Python unit with `CONTEXT_ROWS` rows of code on each side.
    first: int
    last: int
    #: The words of the changed units at the fork, `None` where a Python unit
    #: shared its passage with another, and now.
    words_before: int | None
    words_after: int
    #: Whether the branch added the passage.
    new: bool

    @property
    def top(self) -> int:
        return self.editable[0].first

    @property
    def bottom(self) -> int:
        return max(unit.last for unit in self.editable)


def section_bounds(marks: Sequence[Heading], row: int, total: int) -> tuple[int, int]:
    """The first and last rows of the section holding `row`, from its heading to the next.

    `marks` are the file's headings, and `total` its number of rows. Before the
    first heading, the section starts at row 1.
    """
    first, last = 1, total
    for mark in marks:
        if mark.line < row:
            first = mark.line + 1
        else:
            last = mark.line
            break
    return first, last


def reviews_of(path: str, before: str | None, after: str, patch: str) -> list[Review]:
    """A review of each passage that `patch` changed in `after` and that has `MIN_WORDS` words now.

    `before` is the file at the fork, `None` where the branch added it, and
    `patch` is the `-U0` diff between the two.
    """
    passages = [
        passage
        for passage in changed_passages(path, before, after, patch)
        if passage.words_after >= MIN_WORDS
    ]
    total = len(split_lines(after))
    if not is_document(path):
        return [
            Review(
                path,
                "",
                (unit,),
                max(1, unit.first - CONTEXT_ROWS),
                min(total, unit.last + CONTEXT_ROWS),
                passage.words_before if len(passage.after) == 1 else None,
                unit.words,
                not passage.before,
            )
            for passage in passages
            for unit in passage.after
            if unit.words >= MIN_WORDS
        ]
    units = units_of(path, after)
    marks = headings(markdown_lines(after))
    spans: list[tuple[int, int, int, int, list[Passage]]] = []
    for passage in passages:
        first = section_bounds(marks, passage.after[0].first, total)[0]
        last = section_bounds(marks, passage.after[-1].first, total)[1]
        low, high = units.index(passage.after[0]), units.index(passage.after[-1])
        if low and units[low - 1].first >= first:
            low -= 1
        if high + 1 < len(units) and units[high + 1].last <= last:
            high += 1
        if spans and spans[-1][1] >= low:
            held_low, held_high, held_first, _, group = spans[-1]
            spans[-1] = (held_low, max(held_high, high), held_first, last, [*group, passage])
        else:
            spans.append((low, high, first, last, [passage]))
    return [
        Review(
            path,
            group[0].section,
            tuple(units[low : high + 1]),
            first,
            last,
            sum(passage.words_before for passage in group),
            sum(passage.words_after for passage in group),
            not any(passage.before for passage in group),
        )
        for low, high, first, last, group in spans
    ]


@dataclass
class Reviewed:
    """The passages the branch changed, as the copy editor gets them, and the files left out."""

    base: str
    against: str
    reviews: list[Review]
    #: Each changed file that a row names and that would not parse, with Python's reason.
    unread: list[str]
    #: Each changed file holding a passage to review that no row of the reader table names.
    unnamed: list[str]


def branch_reviews(root: Path, base: str, table: Sequence[Reader]) -> Reviewed:
    """A review of each long passage changed between the fork from `base` and the working tree."""
    fork, against = doc_check._diff_from(root, base)
    found = Reviewed(base, against, [], [], [])
    for path in doc_check._changed_paths(root, fork):
        if not may_review(path) or not (root / path).is_file():
            continue
        named = bool(readers_of(table, path))
        try:
            reviews = reviews_of(
                path,
                text_at(root, fork, path),
                (root / path).read_text(encoding="utf-8"),
                read_git(["diff", "-U0", fork, "--", path], root),
            )
        except UNTOKENIZABLE as error:
            if named:
                found.unread.append(f"{path}: {refusal(error)}")
            continue
        if named:
            found.reviews += reviews
        elif reviews:
            found.unnamed.append(path)
    return found


def review_header(number: int, review: Review, base: str, table: Sequence[Reader]) -> str:
    """The review's numbered header: its rows, its words before and now, and its readers."""
    if review.new:
        words = f"new, {review.words_after} words"
    elif review.words_before is None:
        words = f"{review.words_after} words now"
    else:
        change = review.words_after - review.words_before
        more = f"{change} more" if change > 0 else f"{-change} fewer" if change else "no change"
        words = f"{review.words_before} words on {base}, {review.words_after} now, {more}"
    who = "; ".join(reader.who for reader in readers_of(table, review.path))
    return (
        f"[{number}] {review.path}, rows {review.top}-{review.bottom}. "
        f"Changed text: {words}. For: {who}"
    )


def section_rows(
    lines: Sequence[str],
    first: int,
    last: int,
    numbered: Mapping[int, Review],
    base: str,
    table: Sequence[Reader],
) -> Iterator[str]:
    """Rows `first` to `last` of `lines`, each review's header above its rows, marked `>`."""
    starts = {review.top: number for number, review in numbered.items()}
    for row in range(first, last + 1):
        if row in starts:
            yield review_header(starts[row], numbered[starts[row]], base, table)
        inside = any(review.top <= row <= review.bottom for review in numbered.values())
        yield f"{row:>5} {'>' if inside else '|'} {lines[row - 1]}"


def report(root: Path, found: Reviewed, table: Sequence[Reader]) -> str:
    """The readers, each section once with its numbered passages, then each file left out."""
    out: list[str] = []
    if found.reviews:
        out.append(
            f"{len(found.reviews)} passages of {MIN_WORDS} words or more changed, against "
            f"{found.against}. Each has a numbered header. The rows marked > under it are the "
            "rows you may rewrite: the changed text, and in a Markdown file the paragraph or "
            "table row on each side of it. Rows marked | are there to be read: the rest of the "
            "section, from its heading to the next, or the code around a Python docstring or "
            "comment. Judge each passage for the readers its header names, as the list below "
            "describes them."
        )
        out += reader_lines(table, (review.path for review in found.reviews))
        sections: dict[tuple[str, int, int], dict[int, Review]] = {}
        for number, review in enumerate(found.reviews, start=1):
            sections.setdefault((review.path, review.first, review.last), {})[number] = review
        texts: dict[str, list[str]] = {}
        for (path, first, last), numbered in sections.items():
            if path not in texts:
                texts[path] = split_lines((root / path).read_text(encoding="utf-8"))
            section = next(iter(numbered.values())).section
            where = f'{path} § "{section}"' if section else path
            out += ["", f"{where}, rows {first}-{last}:"]
            out += section_rows(texts[path], first, last, numbered, found.base, table)
    else:
        out.append(
            f"No passage of {MIN_WORDS} words or more changed in a file that the reader table "
            f"names, against {found.against}."
        )
    if found.unnamed:
        out += ["", f"Not reviewed, because no row of the reader table in {RULE.name} names it:"]
        out += [f"  {path}" for path in found.unnamed]
    if found.unread:
        out += ["", "Not read, because Python would not parse the file:"]
        out += [f"  {line}" for line in found.unread]
    return "\n".join(out)


def draft_report(path: Path, kind: str, table: Sequence[Reader]) -> str | None:
    """The draft at `path` as passage 1, for each row of `table` whose first cell holds `kind`.

    Returns `None` where no row's first cell holds `kind`, ignoring case.
    """
    readers = [reader for reader in table if kind.casefold() in reader.kind.casefold()]
    if not readers:
        return None
    lines = split_lines(path.read_text(encoding="utf-8"))
    words = sum(len(line.split()) for line in lines)
    return "\n".join(
        [
            "One draft follows, as passage 1. Every row is marked >, and you may rewrite all "
            "of them. Judge it for the readers below, as the list describes them.",
            "",
            f"Readers of {kind}:",
            *describe(readers),
            "",
            f"[1] {path.name}, rows 1-{len(lines)}. Draft: {words} words. "
            f"For: {'; '.join(reader.who for reader in readers)}",
            *(f"{row:>5} > {line}" for row, line in enumerate(lines, start=1)),
        ]
    )


def with_rule(text: str) -> str:
    """`text` after the plain-writing rule, which the copy editor does not otherwise have."""
    rule = RULE.read_text(encoding="utf-8").rstrip("\n")
    return f"{rule}\n\nThe writing rule ends here, and the prose to review follows.\n\n{text}"


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
    modes.add_argument(
        "--draft",
        type=Path,
        metavar="FILE",
        help="print the reply or pull request body in FILE as one passage, for the readers "
        "that --kind names",
    )
    parser.add_argument(
        "--kind",
        help="with --draft, words from the first cell of the reader rows the draft is for, "
        "such as 'replies' or 'pull request'",
    )
    args = parser.parse_args(argv)
    if (args.draft is None) != (args.kind is None):
        parser.error("--draft and --kind go together")
    root = args.root.resolve()
    try:
        table = rule_table()
        if args.draft is not None:
            text = draft_report(args.draft, args.kind, table)
            if text is None:
                print(
                    f"new_prose: no answer: no row of the reader table in {RULE.name} has "
                    f"{args.kind!r} in its first cell",
                    file=sys.stderr,
                )
                return 1
            print(with_rule(text))
            return 0
        base = args.base or default_base(root)
        if args.base is None and not resolved(base):
            print(
                f"new_prose: no answer: the default branch is unknown ({base!r} is a guess)",
                file=sys.stderr,
            )
            return 1
        if args.compare:
            print(compare_report(compare(root, base, table)))
        elif args.count is not None:
            found = branch_prose(root, base, table, committed=True)
            if found.unread:
                for line in found.unread:
                    print(f"new_prose: not read: {line}", file=sys.stderr)
                return 2
            print(len(unreviewed(root, found, args.count or None)))
        else:
            reviewed = branch_reviews(root, base, table)
            text = report(root, reviewed, table)
            print(with_rule(text) if reviewed.reviews else text)
    except ValueError as error:
        print(f"new_prose: no answer: {RULE.name}: {error}", file=sys.stderr)
        return 1
    except (GitUnanswered, OSError) as error:
        print(f"new_prose: no answer: {error!r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
