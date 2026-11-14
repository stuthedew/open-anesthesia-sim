"""Set each passage of prose a branch changed beside its old text, and list the facts it removed.

Close-out step 8 in `.claude/skills/docket/modes/close-out.md` runs
`python3 tools/new_prose.py --compare` (`PL-JP8X`). The writing session reads
the report to put back a fact that an edit dropped by mistake, and to check
that a passage which grew gives its reader something they act on.

**Which files are read.** A Markdown or Python file is read when a row of the
reader table in `.claude/rules/plain-writing.md` names the file or its
directory (`PL-22T5`). A row whose reader is in `UNEDITED_READERS` is ignored,
so item briefs, the workflow's files, commit messages and replies are never
compared.

**What a unit is.** In a Python file, a unit is a docstring, a run of comment
lines, or any other string literal. `docket.python.docstrings` decides which
strings are docstrings, `doc_check._python_comments` joins comment lines into
runs, and an f-string counts as one unit. In a Markdown file, a unit is a
paragraph or a table row, as `docket.markdown` reads the blocks once the YAML
front matter is blanked row for row. A paragraph inside a list item or a block
quote is a unit of its own. A table row is a unit because one cell can carry a
whole essay. A fence, an HTML comment and a heading are not prose (`PL-ZT47`).
A string literal counts only where a reader row for string literals names its
file, and a docstring or comment only where another row does (`PL-Q98K`).

**What `--compare` prints.** A passage is the units that one hunk of the diff
touches, widened to whole paragraphs, table rows, docstrings or comments on
both sides. Hunks parted only by blank lines make one passage. It is printed
with its word count on the default branch and now, whatever its length, unless
only its spacing changed. A whole section is not the passage, because a growth
of 50 words would not show in a section as long as `docs/MODEL.md` §
"Displayed precision". Then, for each file, it lists each equation, "no test
yet" declaration, code span, citation, number, item id and date that the file
held at the fork and holds fewer times now, read as `tools/model_rewrite.py`
reads a fact. A Python file's facts are read from its prose alone, on the rows
where it stands. Facts are counted per file, so a fact moved to another
section, such as the note for developers, prints nothing. A fact that the file
lost and the branch added to an item file is marked `moved`. On `PL-ZDZ0` a
passage grew from 163 words to about 210 and no review round said so, and a
trial rewrite turned a "no test yet" declaration into "untested" (`PL-J1ZM`).

The tool reads the diff from the commit where the branch forked from the
default branch to the working tree, including files that git does not track
yet. It exits 0 when it read the diff, whether or not it printed a passage,
and exits 1 when the diff could not be read or the default branch is unknown.
A changed file that will not parse is named in a "Not read" line, so a partial
result is never given as a whole one.
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections.abc import Iterable, Sequence
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
from docket.vcs import GitUnanswered, default_base, listed_paths, read_git, resolved  # noqa: E402

import doc_check  # noqa: E402
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
#: The words that mark a reader row as one for string literals. Such a row
#: applies only to string units, and every other row applies to every other kind,
#: so an interface notice and the docstring beside it get different readers.
STRING_ROW_WORDS = "string literals"
#: The rule whose table names the readers of each kind of text.
RULE = ROOT / ".claude" / "rules" / "plain-writing.md"
#: The header of that table, which is how the tool finds it in the rule.
READER_HEADER = (
    "Kind of text",
    "Reader",
    "What they know",
    "What they do not know",
    "What they will do with it",
)


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


#: The readers whose texts the comparison leaves out: the readers of item
#: briefs, the workflow's files, commit messages and replies. The project owner
#: took these texts out of the prose review on 2026-11-10, and the comparison
#: kept that scope when the review was removed (`PL-GL45`). The strings are the
#: "Reader" cells of the rule's table, so a reworded cell fails
#: `tests/unit/test_new_prose.py` instead of bringing those texts back in.
UNEDITED_READERS = (
    "A later session, or the owner reading the history",
    "The project owner, an anesthesiologist and intensive-care physician",
)


def whole_rule_table() -> list[Reader]:
    """Every row of the plain-writing rule's reader table, including the unedited readers."""
    return reader_table(RULE.read_text(encoding="utf-8"))


def rule_table() -> list[Reader]:
    """The rows of the plain-writing rule's reader table for the texts the comparison reads.

    A row for one of `UNEDITED_READERS` is left out, so the tool compares no
    passage for those readers alone.
    """
    return [reader for reader in whole_rule_table() if reader.who not in UNEDITED_READERS]


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
    `read_by` decides which of them the comparison reads.
    """
    if is_document(path):
        return document_units(path, source)
    return sorted(
        prose_units(path, source) + string_units(path, source), key=lambda unit: unit.first
    )


def may_review(path: str) -> bool:
    """Whether the file at `path` holds prose units, as a Markdown or Python file does."""
    return PurePosixPath(path).suffix in {".md", ".py"}


def text_at(root: Path, rev: str, path: str) -> str | None:
    """The file at `path` as commit `rev` holds it, or `None` where `rev` holds no such file."""
    if not listed_paths(read_git(["ls-tree", "-z", "--name-only", rev, "--", path], root)):
        return None
    return read_git(["show", f"{rev}:{path}"], root)


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


def enclosing_titles(marks: Sequence[Heading], row: int) -> list[str]:
    """The titles of the headings in `marks` that enclose the 1-based `row`, innermost first."""
    chain: list[str] = []
    level = None
    for mark in reversed([mark for mark in marks if mark.line < row]):
        if level is None or mark.level < level:
            chain.append(mark.title)
            level = mark.level
    return chain


def paired_sections(path: str, before: str, after: str, passages: list[Passage]) -> list[Passage]:
    """`passages` from one Markdown file, merged where a section heading is new on one side.

    `changed_passages` names a passage after the nearest heading on its own
    side. Where a rewrite adds subheadings that the base lacks, text moved
    between them reads as growth under one and a cut under the next, as
    `PL-J37P`'s rewrite of "Displayed precision" did (`PL-TTBF`). So a passage
    whose heading stands on one side only is moved up to the nearest heading
    that encloses it and stands on both sides, and every passage moved to that
    heading, with any passage already under it, becomes one passage. Where no
    enclosing heading stands on both sides, the whole file is the section that
    both sides share, so two or more such passages become one passage for the
    file. A single such passage keeps its own heading, because nothing was
    moved between it and another passage.
    """
    sides = (headings(markdown_lines(before)), headings(markdown_lines(after)))
    titles = ({mark.title for mark in sides[0]}, {mark.title for mark in sides[1]})
    placed: list[tuple[Passage, str | None]] = []
    for passage in passages:
        new_side = bool(passage.after)
        units = passage.after if new_side else passage.before
        chain = enclosing_titles(sides[new_side], units[0].first)
        other = titles[not new_side]
        if not chain or chain[0] in other:
            placed.append((passage, None))
        else:
            placed.append((passage, next((title for title in chain if title in other), "")))
    lifted = [section for _, section in placed if section is not None]
    if lifted.count("") == 1:
        placed = [(passage, None if section == "" else section) for passage, section in placed]
    targets = {section for _, section in placed if section is not None}
    found: list[Passage] = []
    merged: dict[str, int] = {}
    for passage, section in placed:
        key = passage.section if section is None else section
        if key not in targets:
            found.append(passage)
            continue
        if key not in merged:
            merged[key] = len(found)
            found.append(Passage(path, key, (), ()))
        held = found[merged[key]]
        found[merged[key]] = Passage(
            path,
            key,
            tuple(sorted(held.before + passage.before, key=lambda unit: unit.first)),
            tuple(sorted(held.after + passage.after, key=lambda unit: unit.first)),
        )
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
            passages = changed_passages(path, before, after, patch)
            if is_document(path) and before is not None and after is not None:
                passages = paired_sections(path, before, after, passages)
            found.passages += [
                passage for passage in passages if read_by(table, passage.before + passage.after)
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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to run in")
    parser.add_argument("--base", help="branch to diff against; the default branch by default")
    parser.add_argument(
        "--compare",
        action="store_true",
        required=True,
        help="print each changed passage's words on the base and now, and each fact the "
        "branch removed",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        table = rule_table()
        base = args.base or default_base(root)
        if args.base is None and not resolved(base):
            print(
                f"new_prose: no answer: the default branch is unknown ({base!r} is a guess)",
                file=sys.stderr,
            )
            return 1
        print(compare_report(compare(root, base, table)))
    except ValueError as error:
        print(f"new_prose: no answer: {RULE.name}: {error}", file=sys.stderr)
        return 1
    except (GitUnanswered, OSError) as error:
        print(f"new_prose: no answer: {error!r}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
