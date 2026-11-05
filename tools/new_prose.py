"""Print the prose a branch changed, inside the section around it, for the copy editor.

Close-out step 8 in `.claude/skills/docket/modes/close-out.md` saves this
tool's output to a file and hands that file to the copy editor,
`.claude/agents/copy-editor.md`, through `tools/copy_edit.py`. The copy editor
loads none of this repository's instructions, so the output opens with the text
of `.claude/rules/plain-writing.md`, and the copy editor reads that one file and
nothing else. Each tool call that the copy editor makes costs another turn at
its full context. On its first branch the copy editor read 29 passages in four
reads of this tool's output and 179,031 tokens (`PL-PRCS`, `PL-22T5`).

**Which files are read.** A Markdown or Python file is read when a row of the
rule's reader table names the file or its directory (`PL-22T5`). A changed file
that holds a passage to review and that no row names is listed under "Not
reviewed", because nobody has said who reads it.

**What a unit is.** In a Python file, a unit is a docstring, a run of comment
lines, or any other string literal. `docket.python.docstrings` decides which
strings are docstrings, `doc_check._python_comments` joins comment lines into
runs, and an f-string counts as one unit. In a Markdown file, a unit is a
paragraph or a table row, as `docket.markdown` reads the blocks once the YAML
front matter is blanked row for row. A paragraph inside a list item or a block
quote is a unit of its own. A table row is a unit because one cell can carry a
whole essay. A fence, an HTML comment and a heading are not prose to review
(`PL-ZT47`).

**Which lines changed.** The tool reads the diff as `tools/diff_mutation.py`
reads it, from the commit where the branch forked from the default branch to
the working tree, including files that git does not track yet. A file that is
new on the branch has every line changed.

**What is reviewed.** Each passage that `changed_passages` finds is reviewed,
whatever its length, when `reviewable` accepts one of its units now (project
owner, 2026-11-04, ratified, over `PL-PRCS`'s floor of 30 words). Short units
were awkward in 25% of `PL-Y55Q`'s blind verdicts, and many of the messages a
learner reads are short, so a short passage needs the review too (`PL-HGZS`).
In a Markdown file, the copy editor reads the passage's whole section, from the
heading above it to the next heading. It may rewrite the passage and the one
unit on each side of it inside that section, so it can fold new text into the
paragraph beside it. It may not rewrite the rest of the section, because
`docs/MODEL.md` § "Displayed precision" runs to about 8,000 words, and a
one-sentence fix there would become a rewrite of all of them. That limit is a
placeholder for the owner to overrule (`PL-22T5`). Two passages that would
share a unit are reviewed as one. In a Python file, each changed unit is
reviewed alone, with `CONTEXT_ROWS` rows of code on each side.

**Who reads each passage.** `.claude/rules/plain-writing.md` holds a table that
names the readers of each kind of text: what each knows, what each does not
know, and what each will do with the text. The table's first column names files
in code spans, where a span ending in "/" is a directory. A string literal is
reviewed only where a reader row for string literals names its file, and a
docstring or comment only where another row does, so an interface notice and
the docstring beside it are judged for different readers (`PL-Q98K`). The
report lists the readers of every file it prints a passage from, and names
under each passage the readers to judge it for (`PL-R7Q6`).

The tool exits 0 when it read the diff, whether or not it printed a passage,
and exits 1 when the diff could not be read or the default branch is unknown. A
changed file that will not parse is named in a "Not read" line, so a partial
result is never given as a whole one.

**`--draft FILE --kind WORDS` prepares a reply or a pull request body for review
before it is sent.** It prints the rule, the reader rows whose first cell
contains WORDS, and the whole file as passage 1 (`PL-J1ZM` part 3). It exits 1
when no row's first cell contains WORDS.

**`--section FILE --heading TEXT` prints one Markdown section as passage 1,
with every row open to rewrite.** A changed passage may be rewritten only with
the unit beside it, so a fact that two paragraphs of a section both give, or a
paragraph in the wrong place, needs a review of the whole section. A section
runs from its heading to the next heading of the same or a higher level, so it
holds its subsections. The section rewrites that wait on the copy editor, and
the copy editor's own tests, use this mode (project owner, 2026-11-04,
`PL-HGZS`). It exits 1 when the file is not Markdown, no row of the reader
table names it, or the heading text does not name one section.

**A whole document is reviewed in two parts** (project owner, 2026-11-04,
`PL-HGZS`), and `tools/copy_edit.py` runs both. The first is a structure read,
from `structure_reports`, with every row marked `|`: the copy editor lists the
facts given in two places, the passages in the wrong place and the sections out
of order, and rewrites nothing. A document longer than `REQUEST_LIMIT_WORDS`
is read a chapter at a time, as `chapters` splits it. Once the findings are
applied, the second part line-edits each section alone, from `part_reports`.
There a section is its own rows, from its heading to the next heading of any
level, so no row is edited twice.

**`--count` prints only how many units need a review, for `bin/docket arm`.**
`arm` holds a branch that waits on the owner's review until step 8's review is
recorded as a `Prose-review:` trailer, and it runs this tool through
`docket.toml`'s `prose_count_command` (`PL-W04Z`). This mode counts the units
that `reviewable` accepts, rather than passages. It reads the committed
branch, from the fork to `HEAD`, because `arm` judges commits and not the
working tree.
`--count REV` names the commit that carries the newest `Prose-review:` trailer.
A unit then counts only when its text is not a unit of the same file at `REV`, so
a code fix after the review needs no second review, while a new or reworded
unit does. Comparing texts rather than diffing from `REV` keeps out the prose
that a merge of the default branch brings in, because that prose is not in the
branch's own diff from the fork. The count is one line holding a whole number.
It exits 2, printing the unread files to standard error, when a changed file
will not parse, because a count that skipped a file is not a count.

**`--compare` sets each passage the branch changed beside the text it
replaced, and lists the facts the branch removed** (`PL-JP8X`). A passage is
the units that one hunk of the diff touches, widened to whole paragraphs,
table rows, docstrings or comments on both sides. Hunks parted only by blank
lines make one passage. It is printed with its word count on the default branch
and now, whatever its length, unless only its spacing changed. A whole section is
not the passage, because a growth of 50 words would not show in a section as
long as `docs/MODEL.md` § "Displayed precision". Then, for each file, it
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
import re
import sys
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.digits import whole_number  # noqa: E402
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

#: The kind of a unit that is a string literal in code, other than a docstring.
STRING_KIND = "string"
#: The fewest words a string literal needs to be reviewed. A string of one word,
#: such as `"utf-8"`, `"mL/h"` or a dictionary key, is a value that the code
#: reads, and a rewrite of it would change what the program does. Every other
#: unit is reviewed when it holds a word at all (project owner, 2026-11-04,
#: ratified, over `PL-PRCS`'s floor of 30 words for every unit).
STRING_MIN_WORDS = 2
#: The words that mark a reader row as one for string literals. Such a row
#: applies only to string units, and every other row applies to every other kind,
#: so an interface notice and the docstring beside it get different readers.
STRING_ROW_WORDS = "string literals"
#: The rule whose table names the readers of each kind of text.
RULE = ROOT / ".claude" / "rules" / "plain-writing.md"
#: The copy editor's agent definition, whose body is its prompt. This file is
#: the prompt's one home, and `tools/rejected_prose.py` tests each change to it
#: against the paragraphs the owner rejected or named gold standards (`PL-FYGJ`,
#: `PL-556C`, `PL-22T5`).
PROMPT = ROOT / ".claude" / "agents" / "copy-editor.md"
#: The line between the writing rule and the prose in every request. The copy
#: editor's instructions name it, and `tools/copy_edit.py` finds the passages
#: below it.
RULE_END = "The writing rule ends here, and the prose to review follows."
#: A whole document is reviewed in two parts: a structure read, and then a line
#: edit of each section alone (project owner, 2026-11-04, `PL-HGZS`). These
#: lines open the prose of a structure read's request, and the copy editor's
#: instructions say what to do with each. A document of at most
#: `REQUEST_LIMIT_WORDS` words is read whole. A longer one is read a chapter
#: at a time, and each chapter read ends with a reverse outline, which
#: `tools/copy_edit.py` hands to one read of the whole document's outline.
STRUCTURE_READ = (
    "Structure read. One whole document follows, as passage 1. Every row is marked |, "
    "so rewrite none of it."
)
CHAPTER_READ = (
    "Structure read of one chapter. One chapter of a longer document follows, as passage "
    "1. Every row is marked |, so rewrite none of it, and end with its outline."
)
OUTLINE_READ = (
    "Structure read of an outline. The reverse outlines of every chapter of one document "
    "follow, in order, as passage 1. Report only what crosses chapters."
)
#: The most words one request of a document's review holds, for a structure
#: read or a line edit. A longer document is read a chapter at a time, a longer
#: chapter is split into its subsections, and a longer section with none is cut
#: into runs of whole blocks. The figure covers the largest section that the
#: copy editor had read during its debugging on 2026-11-04 (5,801 words,
#: `PL-HGZS`). A model reads a long request less closely even when it finds the
#: passage it needs (Du et al., 2025, https://arxiv.org/abs/2510.05381), so a
#: higher figure trades close reading for fewer requests, and a lower one the
#: reverse.
REQUEST_LIMIT_WORDS = 6000
#: The header of that table, which is how the tool finds it in the rule.
READER_HEADER = (
    "Kind of text",
    "Reader",
    "What they know",
    "What they do not know",
    "What they will do with it",
)

#: How many lines of code to print above and below each docstring, comment or
#: string literal, so the copy editor can see what an "it" or a name points at
#: without opening the file. Above a docstring, the line it most needs is the
#: `def` or `class` it describes. On 2026-11-04 that line was within 2 rows
#: above 82.9% of the 7,943 docstrings in `src/`, `tests/`, `tools/` and
#: docket's code, within 3 rows above 97.3%, and within 8 above 99.2%. The jump
#: at 3 rows comes from signatures that wrap, which put the docstring 3 rows
#: below the `def`. Three rows therefore show the `def` as often as 4 do, and
#: the fourth row is a margin that costs one line on each side. Comments were
#: not measured, because a comment has no single line it describes. Each extra
#: row lengthens the file the copy editor reads (`PL-BXD5`).
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

    def covers(self, kind: str) -> bool:
        """Whether the row is for units of `kind`: string literals, or every other kind."""
        for_strings = STRING_ROW_WORDS in self.kind.casefold()
        return for_strings == (kind == STRING_KIND)


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


def readers_of(table: Sequence[Reader], path: str, kind: str | None = None) -> list[Reader]:
    """The rows of `table` that name the file at `path`, in table order.

    With `kind`, only the rows for units of that kind, as `Reader.covers` decides.
    """
    return [
        reader for reader in table if reader.reads(path) and (kind is None or reader.covers(kind))
    ]


def read_by(table: Sequence[Reader], units: Iterable[Unit]) -> list[Unit]:
    """The units in `units` that a row of `table` is for, by their file and their kind."""
    return [unit for unit in units if readers_of(table, unit.path, unit.kind)]


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


def string_text(node: ast.Constant | ast.JoinedStr) -> str:
    """The words of a string literal, with each `{...}` field of an f-string as written."""
    if isinstance(node, ast.Constant):
        return str(node.value)
    return "".join(
        str(part.value) if isinstance(part, ast.Constant) else "{" + ast.unparse(part.value) + "}"
        for part in node.values
        if isinstance(part, ast.Constant | ast.FormattedValue)
    )


def string_units(path: str, source: str) -> list[Unit]:
    """Return every string literal in `source` that is not a docstring, in the order they start.

    An f-string is one unit, and the string pieces inside it are not units of
    their own. Strings that Python joins because they stand side by side are
    one literal, and so one unit. Raises one of `UNTOKENIZABLE` when Python
    cannot parse `source`.
    """
    tree = ast.parse(source, filename=path)
    skipped = {id(node) for node in docstrings(tree)}
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            skipped.update(id(inner) for inner in ast.walk(node) if inner is not node)
    found = [
        Unit(path, STRING_KIND, node.lineno, node.end_lineno or node.lineno, string_text(node))
        for node in ast.walk(tree)
        if id(node) not in skipped
        and (
            isinstance(node, ast.JoinedStr)
            or (isinstance(node, ast.Constant) and isinstance(node.value, str))
        )
    ]
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
    """Return the prose units of the file at `path`.

    A document's units are its paragraphs. A Python file's units are its
    docstrings, comments and string literals, in the order they start.
    `read_by` decides which of them a review reads.
    """
    if is_document(path):
        return document_units(path, source)
    return sorted(
        prose_units(path, source) + string_units(path, source), key=lambda unit: unit.first
    )


def reviewable(unit: Unit) -> bool:
    """Whether the copy editor reviews `unit` when the branch changes it.

    A string literal needs `STRING_MIN_WORDS` words, and any other unit one.
    """
    return unit.words >= (STRING_MIN_WORDS if unit.kind == STRING_KIND else 1)


def changed_units(path: str, source: str, rows: set[int] | None) -> list[Unit]:
    """The units in `source` that `reviewable` accepts and that a changed row falls inside.

    `rows` is `None` where the whole file is new, as `changed_rows` returns it.
    """
    return [
        unit
        for unit in units_of(path, source)
        if reviewable(unit)
        and (rows is None or any(unit.first <= row <= unit.last for row in rows))
    ]


def may_review(path: str) -> bool:
    """Whether the file at `path` holds prose units, as a Markdown or Python file does."""
    return PurePosixPath(path).suffix in {".md", ".py"}


@dataclass
class Found:
    """The units the branch changed in the files that the reader table names."""

    against: str
    units: list[Unit]
    #: Each changed Python file that would not parse, with Python's reason.
    unread: list[str]


def branch_prose(
    root: Path, base: str, table: Sequence[Reader] | None = None, *, committed: bool = False
) -> Found:
    """The units changed between the fork from `base` and the working tree.

    Only a file that a row of `table` names is read, and `table` defaults to the
    reader table in the rule. With `committed`, the units are those changed
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
            units.extend(read_by(table, changed_units(path, source, rows)))
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


def fact_text(path: str, source: str | None, *, strings: bool = False) -> str:
    """Return the text whose facts are counted, a whole document or a Python file's prose.

    A Python file's prose keeps the rows it stands on, and every other row is
    blank, so each fact stays on its own row of the file and no number in code
    is read. When `strings` is true, the file's string literals count as prose
    too, so a refusal message that loses the value it names is reported.
    """
    if source is None:
        return ""
    if is_document(path):
        return blank_front_matter(source)
    rows = [""] * len(split_lines(source))
    units = prose_units(path, source) + (string_units(path, source) if strings else [])
    for unit in units:
        for offset, line in enumerate(unit.text.split("\n")[: unit.last - unit.first + 1]):
            at = unit.first - 1 + offset
            rows[at] = f"{rows[at]} {line}" if rows[at] else line
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
            found.passages += [
                passage
                for passage in changed_passages(path, before, after, patch)
                if read_by(table, passage.before + passage.after)
            ]
            strings = bool(readers_of(table, path, STRING_KIND))
            old_facts = fact_text(path, before, strings=strings)
            new_facts = fact_text(path, after, strings=strings)
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


def row_line(number: int, mark: str, text: str) -> str:
    """One row of a passage as the copy editor gets it, with its number, mark and text.

    The mark is `>` for a row the copy editor may rewrite and `|` for a row it
    only reads. `read_row` reads the row back.
    """
    return f"{number:>5} {mark} {text}"


# regex: a row is a right-aligned number, a one-character mark and free text,
# a flat shape that only `row_line` writes and that no parser reads.
ROW_RE = re.compile(r" *([0-9]+) ([>|])(?: (.*))?")
# regex: the span "rows FIRST-LAST" that `rows_span` writes into a passage
# header or a section title, a flat token inside free text.
ROWS_SPAN_RE = re.compile(r", rows ([0-9]+)-([0-9]+)")


def read_row(line: str) -> tuple[int, str, str] | None:
    """The number, mark and text of a row that `row_line` wrote, or `None` for any other line."""
    match = ROW_RE.fullmatch(line)
    if match is None:
        return None
    return int(match.group(1)), match.group(2), match.group(3) or ""


def rows_span(where: str, first: int, last: int) -> str:
    """`where` and its rows, in the form that passage headers and section titles use."""
    return f"{where}, rows {first}-{last}"


def read_span(line: str) -> tuple[int, int] | None:
    """The first and last row of the first span that `rows_span` wrote into `line`."""
    match = ROWS_SPAN_RE.search(line)
    return None if match is None else (int(match.group(1)), int(match.group(2)))


def respan(line: str, first: int, last: int) -> str:
    """`line`, a passage header or a section title, with its span set to `first` to `last`."""
    return ROWS_SPAN_RE.sub(lambda _: rows_span("", first, last), line, count=1)


def passage_number(line: str) -> int | None:
    """The number of the passage that `line` heads, or `None` where `line` is not a header.

    Every header opens with the passage's number in brackets, then its span.
    """
    number, bracket, rest = line.removeprefix("[").partition("] ")
    if not line.startswith("[") or not bracket or read_span(rest) is None:
        return None
    return whole_number(number)


def passage_place(line: str) -> str | None:
    """The file and section that the passage header `line` names before its span, or `None`."""
    if passage_number(line) is None:
        return None
    rest = line.partition("] ")[2]
    match = ROWS_SPAN_RE.search(rest)
    return None if match is None else rest[: match.start()]


#: What opens the line that heads the readers of a file, or of a kind of text.
READERS_OF = "Readers of "


def readers_heading(name: str) -> str:
    """The line that heads the readers of `name`, a file or a kind of text, in a request."""
    return f"{READERS_OF}{name}:"


def read_readers_heading(line: str) -> str | None:
    """The name in a line that `readers_heading` wrote, or `None` for any other line."""
    if not (line.startswith(READERS_OF) and line.endswith(":")):
        return None
    return line.removeprefix(READERS_OF).removesuffix(":")


def excerpt(lines: Sequence[str], unit: Unit) -> Iterator[str]:
    """The unit's rows marked `>`, with `CONTEXT_ROWS` rows of code each side marked `|`."""
    start = max(1, unit.first - CONTEXT_ROWS)
    end = min(len(lines), unit.last + CONTEXT_ROWS)
    for row in range(start, end + 1):
        yield row_line(row, ">" if unit.first <= row <= unit.last else "|", lines[row - 1])


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
        out += ["", readers_heading(path), *describe(readers_of(table, path))]
    return out


def unit_lines(number: int, unit: Unit, rows: Iterable[str], table: Sequence[Reader]) -> list[str]:
    """The unit's numbered header, naming its readers from `table`, then its `rows`."""
    who = "; ".join(reader.who for reader in readers_of(table, unit.path, unit.kind))
    return [
        "",
        f"[{number}] {rows_span(unit.path, unit.first, unit.last)}, "
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
    """A review of each changed passage in `after` with a unit that `reviewable` accepts now.

    `before` is the file at the fork, `None` where the branch added it, and
    `patch` is the `-U0` diff between the two.
    """
    passages = [
        passage
        for passage in changed_passages(path, before, after, patch)
        if any(reviewable(unit) for unit in passage.after)
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
            if reviewable(unit)
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
            found.reviews += [
                review
                for review in reviews
                if readers_of(table, review.path, review.editable[0].kind)
            ]
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
    who = "; ".join(
        reader.who for reader in readers_of(table, review.path, review.editable[0].kind)
    )
    return (
        f"[{number}] {rows_span(review.path, review.top, review.bottom)}. "
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
        yield row_line(row, ">" if inside else "|", lines[row - 1])


def report(root: Path, found: Reviewed, table: Sequence[Reader]) -> str:
    """The readers, each section once with its numbered passages, then each file left out."""
    out: list[str] = []
    if found.reviews:
        out.append(
            f"{len(found.reviews)} passages changed, against "
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
            out += ["", f"{rows_span(where, first, last)}:"]
            out += section_rows(texts[path], first, last, numbered, found.base, table)
    else:
        out.append(
            f"No passage changed in a file that the reader table names, against {found.against}."
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
            readers_heading(kind),
            *describe(readers),
            "",
            f"[1] {rows_span(path.name, 1, len(lines))}. Draft: {words} words. "
            f"For: {'; '.join(reader.who for reader in readers)}",
            *(row_line(row, ">", line) for row, line in enumerate(lines, start=1)),
        ]
    )


def whole_bounds(lines: Sequence[str], heading: str | None) -> tuple[int, int]:
    """The first and last rows of the section headed `heading`, or of the whole document.

    A section runs from its heading to the row before the next heading of the
    same or a higher level, so it holds its subsections. Where `heading` is
    `None`, the rows are the whole document below any front matter. Trailing
    blank rows are left out. Raises `ValueError` where no heading, or more than
    one, has the text `heading`.
    """
    marks = headings(lines)
    first, last = 1, len(lines)
    if heading is None:
        while first <= last and not lines[first - 1].strip():
            first += 1
    else:
        found = [index for index, mark in enumerate(marks) if mark.title == heading.strip()]
        if len(found) != 1:
            rows = ", ".join(str(marks[index].line + 1) for index in found)
            raise ValueError(
                f"{len(found)} headings read {heading!r}" + (f", at rows {rows}" if rows else "")
            )
        mark = marks[found[0]]
        first = mark.line + 1
        later = (other for other in marks[found[0] + 1 :] if other.level <= mark.level)
        last = next((other.line for other in later), len(lines))
    while last > first and not lines[last - 1].strip():
        last -= 1
    return first, last


@dataclass(frozen=True)
class Part:
    """One section's own rows in a document, with its heading's text and its first and last row.

    `title` is empty for the rows above the document's first heading.
    """

    title: str
    first: int
    last: int


def own_parts(lines: Sequence[str]) -> list[Part]:
    """Each section's own rows, in order, for a line edit of one section at a time.

    A section's own rows run from its heading to the row before the next heading
    of any level, so no row is in two parts. The rows above the first heading,
    below any front matter, are a part of their own. Trailing blank rows are
    left out, and so is a part that holds only its heading and blank rows,
    since it has no prose to edit.
    """
    marks = headings(lines)
    starts = [(mark.title, mark.line + 1, mark.end) for mark in marks]
    top, _ = whole_bounds(lines, None)
    if not starts or top < starts[0][1]:
        starts.insert(0, ("", top, top - 1))
    found: list[Part] = []
    for index, (title, first, heading_end) in enumerate(starts):
        last = starts[index + 1][1] - 1 if index + 1 < len(starts) else len(lines)
        while last > first and not lines[last - 1].strip():
            last -= 1
        if any(lines[row - 1].strip() for row in range(heading_end + 1, last + 1)):
            found.append(Part(title, first, last))
    return found


def readers_or_refusal(path: str, table: Sequence[Reader]) -> list[Reader]:
    """The rows of `table` that name the Markdown file at `path`.

    Raises `ValueError` where the file is not Markdown or no row names it.
    """
    if not is_document(path):
        raise ValueError(f"{path} is not a Markdown file")
    readers = readers_of(table, path)
    if not readers:
        raise ValueError(f"no row of the reader table names {path}")
    return readers


def whole_passage(
    path: str,
    shown: Sequence[str],
    lines: Sequence[str],
    span: tuple[int, int],
    title: str | None,
    mark: str,
    table: Sequence[Reader],
) -> list[str]:
    """The readers list, and passage 1 with rows `span` of the file at `path` marked `mark`.

    `title` names the section, or is `None` for the whole document. `lines` are
    the rows with the front matter blank, for the word count, and `shown` the
    rows as the file holds them.
    """
    first, last = span
    words = sum(len(line.split()) for line in lines[first - 1 : last])
    if title is None:
        what, where = "document", path
    else:
        what = "section"
        where = f'{path} § "{title.strip()}"' if title else path
    readers = readers_of(table, path)
    return [
        *reader_lines(table, [path]),
        "",
        f"[1] {rows_span(where, first, last)}. Whole {what}: {words} words. "
        f"For: {'; '.join(reader.who for reader in readers)}",
        *(row_line(row, mark, shown[row - 1]) for row in range(first, last + 1)),
    ]


def section_report(root: Path, path: str, heading: str, table: Sequence[Reader]) -> str:
    """The section of the Markdown file at `path` headed `heading`, as passage 1.

    Every row is marked `>`, so the copy editor may rewrite the section as a
    whole: merge paragraphs that repeat a fact, and move a passage to where its
    reader looks for it (project owner, 2026-11-04, `PL-HGZS`). Raises
    `ValueError` where the file is not Markdown, no row of `table` names it, or
    `heading` does not name one section.
    """
    readers_or_refusal(path, table)
    source = (root / path).read_text(encoding="utf-8")
    lines = markdown_lines(source)
    span = whole_bounds(lines, heading)
    return "\n".join(
        [
            "One whole section follows, as passage 1. Every row is marked >, and you may "
            "rewrite all of them. Edit the section as a whole, then paragraph by paragraph, "
            "for the readers below.",
            *whole_passage(path, split_lines(source), lines, span, heading, ">", table),
        ]
    )


def part_reports(root: Path, path: str, table: Sequence[Reader]) -> list[tuple[Part, str]]:
    """Each section's own rows in the Markdown file at `path`, as separate requests.

    These requests are the second part of a document's review. Once the
    structure read's findings are applied, each section is line-edited alone,
    because the copy editor reads a short request more closely than a long one
    (project owner, 2026-11-04, `PL-HGZS`). A section longer than
    `REQUEST_LIMIT_WORDS` is cut into runs by `fits`. In each request, every row
    of the part is marked `>`. Raises `ValueError` where the file is not
    Markdown or no row of `table` names it.
    """
    readers_or_refusal(path, table)
    source = (root / path).read_text(encoding="utf-8")
    lines = markdown_lines(source)
    shown = split_lines(source)
    return [
        (
            part,
            "\n".join(
                [
                    "One section follows, as passage 1, without its subsections. Every row is "
                    "marked >, and you may rewrite all of them. Edit the section as a whole, "
                    "then paragraph by paragraph, for the readers below.",
                    *whole_passage(
                        path, shown, lines, (part.first, part.last), part.title, ">", table
                    ),
                ]
            ),
        )
        for whole in own_parts(lines)
        for part in fits(lines, whole, REQUEST_LIMIT_WORDS)
    ]


def words_in(lines: Sequence[str], part: Part) -> int:
    """How many words the rows of `part` hold."""
    return sum(len(line.split()) for line in lines[part.first - 1 : part.last])


def has_prose(lines: Sequence[str], marks: Sequence[Heading], part: Part) -> bool:
    """Whether `part` holds a row with text that is not a heading."""
    heading_rows = {row for mark in marks for row in range(mark.line + 1, mark.end + 1)}
    rows = range(part.first, part.last + 1)
    return any(lines[row - 1].strip() and row not in heading_rows for row in rows)


def trimmed(lines: Sequence[str], title: str, first: int, last: int) -> Part:
    """The part from row `first` to row `last`, less its trailing blank rows."""
    while last > first and not lines[last - 1].strip():
        last -= 1
    return Part(title, first, last)


def fits(lines: Sequence[str], part: Part, limit: int) -> list[Part]:
    """`part` as it is, or its runs of whole blocks where it holds more than `limit` words.

    A section with no subsection to split at can still be longer than one
    request should be. It is cut at blank rows outside a fenced block, into
    runs of at most `limit` words unless one block alone holds more. Each run's
    title says which run of how many it is.
    """
    if words_in(lines, part) <= limit:
        return [part]
    runs: list[tuple[int, int]] = []
    start, words, fence = part.first, 0, ""
    for row in range(part.first, part.last + 1):
        line = lines[row - 1]
        opening = line.lstrip()[:3]
        if opening in ("```", "~~~") and len(line) - len(line.lstrip()) < 4:
            fence = "" if fence == opening else (fence or opening)
        if not line.strip() and not fence and words > limit // 2 and row > start:
            ahead = sum(len(lines[later - 1].split()) for later in range(row, part.last + 1))
            block_end = next(
                (later for later in range(row + 1, part.last + 1) if not lines[later - 1].strip()),
                part.last + 1,
            )
            block = sum(len(lines[later - 1].split()) for later in range(row, block_end))
            if words + block > limit and ahead:
                runs.append((start, row - 1))
                start, words = row + 1, 0
                continue
        words += len(line.split())
    runs.append((start, part.last))
    pieces = [trimmed(lines, part.title, first, last) for first, last in runs if first <= last]
    if len(pieces) == 1:
        return pieces
    return [
        Part(f"{part.title} (run {index} of {len(pieces)})", piece.first, piece.last)
        for index, piece in enumerate(pieces, start=1)
    ]


def chapters(lines: Sequence[str], limit: int | None = None) -> list[Part]:
    """The pieces a structure read takes one at a time, the whole document or its chapters.

    By default, `limit` is `REQUEST_LIMIT_WORDS`. A document of at most `limit`
    words is one piece. A longer one splits at the next level of heading inside
    it: its rows above the first heading at that level make one piece, and each
    section at that level makes another. A piece still longer than `limit`
    splits the same way. A section with no subsection left is cut into runs of
    whole blocks by `fits`. Where the rows above the first subsection hold only
    a heading, they go with that subsection, so every row of the document
    belongs to one piece.
    """
    limit = REQUEST_LIMIT_WORDS if limit is None else limit
    marks = headings(lines)
    top, bottom = whole_bounds(lines, None)

    def split(part: Part, head: int) -> list[Part]:
        # `head` is the row of the part's own heading, or the row before the
        # part where it has none. The part's rows above `head` hold only the
        # headings of sections that had no text of their own.
        if not has_prose(lines, marks, part):
            return []
        if words_in(lines, part) <= limit:
            return [part]
        inner = [mark for mark in marks if head < mark.line + 1 <= part.last]
        if not inner:
            return fits(lines, part, limit)
        level = min(mark.level for mark in inner)
        kids = [mark for mark in inner if mark.level == level]
        found = split(trimmed(lines, part.title, part.first, kids[0].line), head)
        for index, kid in enumerate(kids):
            last = kids[index + 1].line if index + 1 < len(kids) else part.last
            # A heading with no text of its own goes with its first subsection,
            # so that the structure read still sees it.
            first = part.first if index == 0 and not found else kid.line + 1
            found += split(trimmed(lines, kid.title, first, last), kid.end)
        return found

    return split(trimmed(lines, "", top, bottom), top - 1)


def structure_reports(root: Path, path: str, table: Sequence[Reader]) -> list[tuple[Part, str]]:
    """The first part of a document's review: its structure read, as one request or one per chapter.

    Every row is marked `|`, because a structure read rewrites nothing: it
    finds facts given twice, passages in the wrong place and sections out of
    order, and the line edit of each section follows once its findings are
    applied (project owner, 2026-11-04, `PL-HGZS`). A document that `chapters`
    keeps whole is one request that opens with `STRUCTURE_READ`. Otherwise each
    chapter is a request that opens with `CHAPTER_READ`. Raises `ValueError`
    where the file is not Markdown or no row of `table` names it.
    """
    readers_or_refusal(path, table)
    source = (root / path).read_text(encoding="utf-8")
    lines = markdown_lines(source)
    shown = split_lines(source)
    pieces = chapters(lines)
    whole = len(pieces) == 1
    return [
        (
            piece,
            "\n".join(
                [
                    STRUCTURE_READ if whole else CHAPTER_READ,
                    *whole_passage(
                        path,
                        shown,
                        lines,
                        (piece.first, piece.last),
                        None if whole else piece.title,
                        "|",
                        table,
                    ),
                ]
            ),
        )
        for piece in pieces
    ]


def outline_report(path: str, table: Sequence[Reader], outlines: Sequence[tuple[Part, str]]) -> str:
    """The reverse outlines of the chapters of the file at `path`, as passage 1 of one request.

    Each chapter read of a long document ends with its outline, one line for
    each paragraph's point and facts. One read of them all then finds what
    crosses chapters: a fact two chapters give, a paragraph in the wrong
    chapter, and chapters out of order (`PL-HGZS`). Each outline row is
    indented, so that no row is mistaken for a passage header.
    """
    readers = readers_of(table, path)
    body: list[str] = []
    for part, outline in outlines:
        section = f' § "{part.title}"' if part.title else ""
        body += [f"Chapter: {path}{section}, rows {part.first}-{part.last}"]
        body += [f"  {line}" for line in split_lines(outline.strip()) if line.strip()]
    return "\n".join(
        [
            OUTLINE_READ,
            *reader_lines(table, [path]),
            "",
            f"[1] {path}, the outlines of its {len(outlines)} chapters. "
            f"For: {'; '.join(reader.who for reader in readers)}",
            *body,
        ]
    )


def with_rule(text: str) -> str:
    """`text` after the plain-writing rule, which the copy editor does not otherwise have."""
    rule = RULE.read_text(encoding="utf-8").rstrip("\n")
    return f"{rule}\n\n{RULE_END}\n\n{text}"


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
    modes.add_argument(
        "--section",
        metavar="FILE",
        help="print the section of the Markdown file FILE that --heading names as one "
        "passage that the copy editor may rewrite whole",
    )
    parser.add_argument(
        "--heading",
        help="with --section, the exact text of the heading whose section to print, "
        "subsections included",
    )
    args = parser.parse_args(argv)
    if (args.draft is None) != (args.kind is None):
        parser.error("--draft and --kind go together")
    if (args.heading is None) != (args.section is None):
        parser.error(
            "--section and --heading go together; review a whole document with "
            "tools/copy_edit.py --structure FILE, then --sections FILE"
        )
    root = args.root.resolve()
    try:
        table = rule_table()
        if args.section is not None:
            try:
                whole = section_report(root, args.section, args.heading, table)
            except ValueError as error:
                print(f"new_prose: no answer: {error}", file=sys.stderr)
                return 1
            print(with_rule(whole))
            return 0
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
