"""List what a rewrite of the specification still cites and what it has dropped, and move sections.

The specification is `docs/MODEL.md` and the documents split from it, which
`product_paths.SPECIFICATION_DOCS` lists (`PL-P3GZ`). `PL-ZT47` made
`docs/MODEL.md` readable for a clinician in fourteen section parts. Each part
moved the decision history out to the item files and then rewrote the
phrasing, and had to lose no equation, unit, value or citation. This tool
answers the two questions such a rewrite asks of the tree, in whichever
document of the specification holds the section. It also makes the move that
splits a document.

- `ids HEADING...` prints each line of the named sections that cites an item
  id outside the declared-none form ``no test yet (`PL-XXXX`)``.
  `tools/doc_check.py` requires that form, so its ids stay. A section runs from
  its heading to the next heading of the same or a higher level, so it holds
  its subsections. Exits 1 when it prints a line, 0 when the sections cite no
  other id, and 2 when a heading is not in the document.
- `lost` compares the specification at the commit where the branch forked from
  the default branch with the working tree. It reads the documents as one
  text, so a fact moved from one of them to another prints nothing. It prints
  each equation, code span, number and citation that the fork held more often
  than the working tree does, with the document and line where the fork held
  it. The declared-none form is a
  fact of its own, so "no test yet (`PL-XXXX`)" rewritten as "untested" reads
  as lost. A fact the branch added to a file under the item store is marked
  `moved`. A number is read with its
  sign, its exponent and its unit, so a changed unit or mantissa reads as a
  lost value, and the ordinal of a numbered list is not read. Facts are
  counted and not placed, so two values swapped within a sentence print
  nothing, which the diff still shows. Item ids and dates are counted
  apart, because they are the history the part removes on purpose. It then
  prints each equation, code span, citation and number that the working tree
  holds more often than the fork, with the line where it now stands, so a
  value the rewrite added or restated in a new place is shown too. A dropped
  number and an added number with the same value and unit, in the same
  section, are marked `restated`, so 4e-4 rewritten as 0.04% reads as one
  value in a new form. A percent is read as a fraction of one for this, and a
  unit as `tools/doc_check.py` reads it. A fact moved within the document, such
  as to a section's note for developers, prints nothing, because each fact is
  counted across the whole document. Exits 0 whenever it read both versions,
  since whether a dropped number was history or a value is a judgment for the
  session. Exits 1 when git could not answer.

- `move --to DOCUMENT HEADING...` cuts the named `##` sections out of
  `docs/MODEL.md`, or the document `--from` names, and appends them unchanged
  to `DOCUMENT`, which must already hold its title. It then re-points each
  citation of a moved section, as `repoint` does. Exits 2, changing nothing,
  when a heading names no one section.
- `repoint --to DOCUMENT` re-points citations after a move, in every tracked
  text file but a closed item and a release note. A citation that names the
  old document and quotes a heading or a sentence that only the new one holds
  gets the new document's path. Inside the two documents, a section mark with
  no document before it gets the other document's path where its section is
  now there. It prints each file it changed, and each citation whose words
  neither document holds, which a person reads. It also prints each quotation
  that follows a mention of one document and names a section only the other
  has, because one path before two section names is right for the first
  alone. Running it twice changes nothing more.

The pull request of each section part accounts for every line `lost` prints.
When each line is history or a kept duplicate and nothing was added, no value,
equation, code span or citation of the specification changed, and the change
merges on green unless a sentence's meaning needs the owner's judgment
(project owner, 2026-11-02, ratified, `PL-ZTZF`).
"""

from __future__ import annotations

import argparse
import math
import re
import sys
from collections import Counter
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.config import load  # noqa: E402
from docket.lines import split_lines  # noqa: E402
from docket.markdown import PROSE, Heading, headings  # noqa: E402
from docket.store import CITED_ID_RE  # noqa: E402
from docket.vcs import (  # noqa: E402
    RECORDS,
    GitUnanswered,
    default_base,
    listed_paths,
    read_git,
    resolved,
)

import doc_check  # noqa: E402
from product_paths import MODEL_DOC, SPECIFICATION_DOCS  # noqa: E402

#: A display equation's body: the lines of a ```math fence.
MATH_FENCE_RE = re.compile(r"^```math[ \t]*\n(.*?)^```", re.M | re.S)
#: An inline equation, written $`...`$ as GitHub renders one.
INLINE_MATH_RE = re.compile(r"\$`([^`\n]+)`\$")
#: A code span, once the inline equations are removed.
CODE_RE = re.compile(r"`([^`\n]+)`")
#: A date, which the history carries and a specification rarely needs.
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
#: A pull request or issue number, which is history too.
PULL_RE = re.compile(r"#\d+\b")
#: A digital object identifier, a PubMed id, a web address, or a page locator. A
#: sentence's closing full stop is not part of an identifier or an address.
SOURCE_LOCATOR_RE = re.compile(
    r"\b10\.\d{4,9}/[^\s)\]>,;]*[^\s)\]>,;.]"
    r"|\bPMID:?\s*\d+"
    r"|https?://[^\s)\]>]*[^\s)\]>.,;]"
    r"|\bpp?\.\s?\d+(?:[-–]\d+)?"
)
#: A number as written in prose: its sign, thousands separators, decimals and
#: exponent, and the unit after it from `doc_check.PROSE_UNITS`, so that
#: "1.32 L" changed to "1.32 mL" reads as a different value.
PROSE_NUMBER_RE = re.compile(
    r"(?<![\w.])[−+-]?\d+(?:[.,]\d+)*(?:[eE][−+-]?\d+)?"
    r"(?:[  ]?×?(?:" + doc_check.PROSE_UNITS + r")(?![\w/]))?"
    r"(?![\w])"
)
#: A number that `PROSE_NUMBER_RE` found, split into its numeral and its unit.
NUMBER_PARTS_RE = re.compile(
    r"(?P<numeral>[−+-]?\d+(?:[.,]\d+)*(?:[eE][−+-]?\d+)?)[ \u00a0]?×?(?P<unit>.*)"
)
#: The heading level of a section of `docs/MODEL.md`. A restated number is
#: paired with the dropped one only inside the same section of this level.
SECTION_LEVEL = 2
#: The marker of a numbered list item, whose ordinal is not a value.
LIST_ORDINAL_RE = re.compile(r"^[ \t]*\d+\.(?=[ \t])", re.M)

#: The kinds `lost` prints one by one, in the order it prints them. A
#: declaration is the form ``no test yet (`PL-XXXX`)``, which
#: `tools/doc_check.py` requires where a member has no test, so its id is not
#: history to remove.
FACT_KINDS = ("equation", "declaration", "code", "citation", "number")
#: The kinds `lost` only counts, because removing them is the point.
HISTORY_KINDS = ("item id", "date")


@dataclass(frozen=True)
class Cited:
    """A line of a section that cites item ids outside the declared-none form."""

    line: int
    ids: tuple[str, ...]
    text: str


def section_lines(lines: Sequence[str], title: str) -> list[tuple[int, int]] | None:
    """The index ranges of every section whose heading reads `title`, or `None` if none does."""
    found = headings(lines)
    spans: list[tuple[int, int]] = []
    for heading in found:
        if heading.title != title:
            continue
        end = next(
            (h.line for h in found if h.line > heading.line and h.level <= heading.level),
            len(lines),
        )
        spans.append((heading.line, end))
    return spans or None


def cited_ids(lines: Sequence[str], start: int, end: int) -> list[Cited]:
    """Each line from `start` to `end` citing an item id outside the declared-none form.

    The declared-none form may wrap across lines, so the span is read as one
    text and each id is placed on its line afterwards.
    """
    text = "".join(f"{line}\n" for line in lines[start:end])
    declared = [
        (match.start(1), match.end(1))
        for match in doc_check.TEST_ENTITY.declares_none.finditer(text)
    ]
    by_line: dict[int, list[str]] = {}
    for match in CITED_ID_RE.finditer(text):
        if any(first <= match.start() < last for first, last in declared):
            continue
        row = start + text.count("\n", 0, match.start())
        by_line.setdefault(row, []).append(match.group())
    return [
        Cited(row + 1, tuple(dict.fromkeys(ids)), lines[row].strip())
        for row, ids in sorted(by_line.items())
    ]


def facts(text: str) -> Iterable[tuple[str, str, int]]:
    """Each fact in a Markdown `text` as its kind, its text and its 1-based line.

    An equation is read first, then a declaration, then the code spans, and all
    three before the numbers, so a number inside an equation or a code span,
    and the id inside a declaration, counts once, as part of it. A declaration
    that wraps is read with each gap as one space.
    """
    starts = [0]
    starts += [index + 1 for index, character in enumerate(text) if character == "\n"]

    def line_of(offset: int) -> int:
        low, high = 0, len(starts)
        while high - low > 1:
            middle = (low + high) // 2
            if starts[middle] <= offset:
                low = middle
            else:
                high = middle
        return low + 1

    blank = list(text)

    def take(match: re.Match[str]) -> None:
        for index in range(match.start(), match.end()):
            if blank[index] != "\n":
                blank[index] = " "

    for match in MATH_FENCE_RE.finditer(text):
        yield "equation", match.group(1).strip(), line_of(match.start(1))
        take(match)
    scanned = "".join(blank)
    for match in INLINE_MATH_RE.finditer(scanned):
        yield "equation", match.group(1), line_of(match.start())
        take(match)
    scanned = "".join(blank)
    for match in doc_check.TEST_ENTITY.declares_none.finditer(scanned):
        yield "declaration", " ".join(match.group().split()), line_of(match.start())
        take(match)
    scanned = "".join(blank)
    for match in CODE_RE.finditer(scanned):
        if CITED_ID_RE.fullmatch(match.group(1)):
            yield "item id", match.group(1), line_of(match.start())
        else:
            yield "code", match.group(1), line_of(match.start())
        take(match)
    scanned = "".join(blank)
    for match in CITED_ID_RE.finditer(scanned):
        yield "item id", match.group(), line_of(match.start())
        take(match)
    for pattern, kind in ((DATE_RE, "date"), (SOURCE_LOCATOR_RE, "citation")):
        scanned = "".join(blank)
        for match in pattern.finditer(scanned):
            yield kind, match.group(), line_of(match.start())
            take(match)
    for pattern in (PULL_RE, LIST_ORDINAL_RE):
        scanned = "".join(blank)
        for match in pattern.finditer(scanned):
            take(match)
    scanned = "".join(blank)
    for match in PROSE_NUMBER_RE.finditer(scanned):
        yield "number", match.group(), line_of(match.start())


@dataclass(frozen=True)
class Gone:
    """A fact the fork's document held more often than the working tree's."""

    kind: str
    text: str
    #: How many more times the fork held it.
    times: int
    #: The fork's line where it first stood, and that line's text.
    line: int
    context: str
    moved: bool
    #: The added number that states the same value in another form, if any.
    restated_as: str = ""


def gone_facts(before: str, after: str, added: str) -> list[Gone]:
    """The facts of `before` that `after` holds fewer times, each marked when `added` holds it."""
    first: dict[tuple[str, str], int] = {}
    counted: Counter[tuple[str, str]] = Counter()
    for kind, fact, line in facts(before):
        counted[(kind, fact)] += 1
        first.setdefault((kind, fact), line)
    counted.subtract((kind, fact) for kind, fact, _ in facts(after))
    elsewhere = {(kind, fact) for kind, fact, _ in facts(added)}
    lines = split_lines(before)
    return [
        Gone(
            kind,
            fact,
            times,
            first[(kind, fact)],
            lines[first[(kind, fact)] - 1].strip(),
            (kind, fact) in elsewhere,
        )
        for (kind, fact), times in counted.items()
        if times > 0
    ]


@dataclass(frozen=True)
class Added:
    """A fact the working tree's document holds more often than the fork's."""

    kind: str
    text: str
    #: How many more times the working tree holds it.
    times: int
    #: The working tree's line where it first stands, and that line's text.
    line: int
    context: str
    #: The dropped number whose value this one states in another form, if any.
    restates: str = ""


def added_facts(before: str, after: str) -> list[Added]:
    """The facts of `FACT_KINDS` that `after` holds more often than `before`.

    A rewrite that adds a value, or restates one in a new place, changes what
    the specification says as surely as one that drops a value. `gone_facts`
    shows only the second, so this is its mirror.
    """
    first: dict[tuple[str, str], int] = {}
    counted: Counter[tuple[str, str]] = Counter()
    for kind, fact, line in facts(after):
        if kind not in FACT_KINDS:
            continue
        counted[(kind, fact)] += 1
        first.setdefault((kind, fact), line)
    counted.subtract((kind, fact) for kind, fact, _ in facts(before) if kind in FACT_KINDS)
    lines = split_lines(after)
    return [
        Added(kind, fact, times, first[(kind, fact)], lines[first[(kind, fact)] - 1].strip())
        for (kind, fact), times in counted.items()
        if times > 0
    ]


def number_value(number: str) -> tuple[float, str | None] | None:
    """A number's value and unit, with a percent read as a fraction of one.

    The unit is normalized by `doc_check._prose_figure`, so "10 percent" and
    "10%" hold one value, and both hold the value of a bare "0.1". A comma is
    read as a thousands separator. A numeral whose comma is not one, such as
    "1,5", returns `None`, so it is never paired. So does a numeral with two
    decimal points, such as the WCAG success criterion "1.4.11", which is a
    section number and not a value.
    """
    parts = NUMBER_PARTS_RE.fullmatch(number)
    if parts is None:
        return None
    numeral = parts["numeral"].replace("−", "-")
    whole = numeral.lstrip("+-").partition(".")[0]
    if "," in numeral and any(len(group) != 3 for group in whole.split(",")[1:]):
        return None
    if numeral.count(".") > 1:
        return None
    value, unit = doc_check._prose_figure(numeral.replace(",", ""), parts["unit"] or None)
    if unit == "%":
        return value / 100, None
    return value, unit


def section_at(found: Sequence[Heading], line: int) -> str:
    """The title of the section that holds 1-based `line`, or "" before the first one.

    `found` is the document's headings, in order, as `headings` returns them.
    """
    title = ""
    for heading in found:
        if heading.line >= line:
            break
        if heading.level <= SECTION_LEVEL:
            title = heading.title
    return title


def pair_restated(
    before: str, after: str, gone: Sequence[Gone], added: Sequence[Added]
) -> tuple[list[Gone], list[Added]]:
    """Mark each dropped number that an added number restates with the same value.

    A pair needs the same value and unit, the same count, and the same section
    in both versions. The section bound keeps a value dropped in one section
    from being hidden by an equal value added to another. A number already
    moved to an item file is not paired. Two values count as the same when
    they differ by less than one part in 10^12. That allows for the rounding
    error of dividing a percent by 100, such as 0.07% against 7e-4.
    """
    fork_heads, now_heads = headings(split_lines(before)), headings(split_lines(after))
    gone_out, added_out = list(gone), list(added)
    taken: set[int] = set()
    for at, dropped in enumerate(gone_out):
        if dropped.kind != "number" or dropped.moved:
            continue
        value = number_value(dropped.text)
        if value is None:
            continue
        section = section_at(fork_heads, dropped.line)
        for index, new in enumerate(added_out):
            if index in taken or new.kind != "number" or new.times != dropped.times:
                continue
            other = number_value(new.text)
            if (
                other is None
                or other[1] != value[1]
                or not math.isclose(other[0], value[0], rel_tol=1e-12, abs_tol=0.0)
                or section_at(now_heads, new.line) != section
            ):
                continue
            taken.add(index)
            gone_out[at] = replace(dropped, restated_as=new.text)
            added_out[index] = replace(new, restates=dropped.text)
            break
    return gone_out, added_out


def added_to_items(root: Path, fork: str) -> str:
    """The lines the branch added to the item store, from the fork to the working tree.

    A line counts as added when the file did not hold it at the fork, so a new
    item file, tracked or not, counts whole.
    """
    store = PurePosixPath(load(root).items_dir)
    added: list[str] = []
    for path in doc_check._changed_paths(root, fork):
        if PurePosixPath(path).parent != store or not (root / path).is_file():
            continue
        held: set[str] = set()
        if listed_paths(read_git(["ls-tree", "-z", "--name-only", fork, "--", path], root)):
            held = set(split_lines(read_git(["show", f"{fork}:{path}"], root)))
        now = split_lines((root / path).read_text(encoding="utf-8"))
        added += [line for line in now if line not in held]
    return "\n".join(added)


def report_ids(
    lines: Sequence[str], titles: Sequence[str], path: str = MODEL_DOC
) -> tuple[int, list[str]]:
    """The exit status and the lines `ids` prints for the sections of `path` named by `titles`."""
    out: list[str] = []
    missing = [title for title in titles if section_lines(lines, title) is None]
    if missing:
        return 2, [f'{path}: no heading reads "{title}"' for title in missing]
    seen: set[int] = set()
    for title in titles:
        for start, end in section_lines(lines, title) or []:
            for cited in cited_ids(lines, start, end):
                if cited.line in seen:
                    continue
                seen.add(cited.line)
                out.append(f"{path}:{cited.line}: {', '.join(cited.ids)}: {cited.text[:100]}")
    return (1 if out else 0), out


def report_gone(gone: Sequence[Gone], against: str, path: str = MODEL_DOC) -> list[str]:
    """The lines `lost` prints for the file at `path`: the facts by kind, then the history."""
    facts_gone = [item for item in gone if item.kind in FACT_KINDS]
    moved = sum(item.moved for item in facts_gone)
    restated = sum(bool(item.restated_as) for item in facts_gone)
    out = [
        f"{path} against {against}: {len(facts_gone)} equations, declarations, code spans, "
        f"citations and numbers are held fewer times than at the fork, and {moved} of them "
        f"were added to an item file. {restated} of them are restated in another form with "
        "the same value."
    ]
    for kind in FACT_KINDS:
        rows = sorted((item for item in facts_gone if item.kind == kind), key=lambda g: g.line)
        if not rows:
            continue
        out += ["", f"{kind} ({len(rows)})"]
        for item in rows:
            times = f" x{item.times}" if item.times > 1 else ""
            if item.restated_as:
                fact = f"restated {item.text}{times} as {item.restated_as}"
            else:
                fact = f"{'moved' if item.moved else 'gone '} {item.text}{times}"
            out.append(f"  {fact}  (fork line {item.line}: {item.context[:90]})")
    for kind in HISTORY_KINDS:
        texts = sorted({item.text for item in gone if item.kind == kind})
        if texts:
            out += ["", f"{kind}s no longer cited ({len(texts)}): {', '.join(texts)}"]
    return out


def report_added(added: Sequence[Added]) -> list[str]:
    """The lines `lost` prints after the dropped facts: each fact the working tree added."""
    restating = sum(bool(item.restates) for item in added)
    out = [
        "",
        f"{len(added)} equations, declarations, code spans, citations and numbers are held "
        "more times than "
        f"at the fork. {restating} of them restate a dropped number with the same value.",
    ]
    for kind in FACT_KINDS:
        rows = sorted((item for item in added if item.kind == kind), key=lambda a: a.line)
        if not rows:
            continue
        out += ["", f"added {kind} ({len(rows)})"]
        for item in rows:
            times = f" x{item.times}" if item.times > 1 else ""
            restates = f" restating {item.restates}" if item.restates else ""
            out.append(
                f"  added {item.text}{times}{restates}  (line {item.line}: {item.context[:90]})"
            )
    return out


def joined(documents: Sequence[tuple[str, str]]) -> tuple[str, list[tuple[int, str]]]:
    """The `documents`, each a path and its text, as one text, and where each starts in it.

    `lost` counts each fact across the whole specification, so a fact moved
    from one of its documents to another prints nothing. Each start is the
    1-based line of the joined text at which a document opens, with its path.
    """
    parts: list[str] = []
    starts: list[tuple[int, str]] = []
    line = 1
    for path, text in documents:
        whole = text if text.endswith("\n") else f"{text}\n"
        starts.append((line, path))
        parts.append(whole)
        line += whole.count("\n")
    return "".join(parts), starts


def placed(line: int, starts: Sequence[tuple[int, str]]) -> tuple[str, int]:
    """The document that holds `line` of a joined text, and the line's number in that document."""
    first, path = starts[0]
    for start, name in starts:
        if start <= line:
            first, path = start, name
    return path, line - first + 1


def specification_at_fork(root: Path, fork: str) -> list[tuple[str, str]]:
    """Each document of the specification that the commit `fork` holds, with its text there."""
    held: list[tuple[str, str]] = []
    for document in SPECIFICATION_DOCS:
        if listed_paths(read_git(["ls-tree", "-z", "--name-only", fork, "--", document], root)):
            held.append((document, read_git(["show", f"{fork}:{document}"], root)))
    return held


def specification_now(root: Path) -> list[tuple[str, str]]:
    """Each document of the specification in the working tree, with its text."""
    return [
        (document, (root / document).read_text(encoding="utf-8"))
        for document in SPECIFICATION_DOCS
        if (root / document).is_file()
    ]


def move_sections(root: Path, source: str, destination: str, titles: Sequence[str]) -> list[str]:
    """Move the sections of `source` named by `titles` to the end of `destination`, unchanged.

    Each section goes with its subsections, in the order `source` holds them.
    `destination` must exist, with its title and opening lines already written.
    Returns the titles that `source` does not hold as a section of
    `SECTION_LEVEL`, and moves nothing when there is one.
    """
    lines = split_lines((root / source).read_text(encoding="utf-8"))
    spans: list[tuple[int, int]] = []
    missing: list[str] = []
    found = [heading for heading in headings(lines) if heading.level == SECTION_LEVEL]
    for title in titles:
        held = [heading for heading in found if heading.title == title]
        if len(held) != 1:
            missing.append(title)
            continue
        spans += section_lines(lines, title) or []
    if missing:
        return missing
    spans.sort()
    taken = [line for start, end in spans for line in lines[start:end]]
    kept = [
        line
        for index, line in enumerate(lines)
        if not any(start <= index < end for start, end in spans)
    ]
    target = root / destination
    opening = target.read_text(encoding="utf-8")
    if not opening.endswith("\n\n"):
        opening = opening.rstrip("\n") + "\n\n"
    target.write_text(opening + "".join(f"{line}\n" for line in taken), encoding="utf-8")
    (root / source).write_text("".join(f"{line}\n" for line in kept), encoding="utf-8")
    return []


#: The file types `repoint` reads for a citation of a document.
REPOINTED_SUFFIXES = frozenset({".py", ".md", ".toml", ".yml", ".yaml", ".sh", ".json", ".cff"})
#: Records of what was true when they were written, which `repoint` leaves
#: alone, as `tools/doc_check.py` leaves a closed item's citations.
RECORD_DIRS = (
    RECORDS,
    "docs/releases/",
    "docs/hook-blocks/",
    "docs/worker-runs/",
    "docs/prose-review/",
)
#: What stands between a document and a quotation that claims the document
#: holds the words: nothing, a possessive, a section mark, a comma, a colon, a
#: parenthesis, or "under" or "section".
# regex: a citation's connective in a Python string, a comment, a JSON note or
# an item brief. No one parser reads all four, and `tools/doc_check.py` reads
# the same connectives with a pattern (`CITATION_CONNECTIVE`).
CLAIMING_GAP_RE = re.compile(
    r"`?(?:['’]s(?:\s+own)?)?\s*(?:[,:(]|§{1,2}|under|section)?\s*", re.IGNORECASE
)
#: The start of a wrapped line inside a quotation: its indentation, and the
#: marker that a Python comment (`#` or `#:`) or a quoted paragraph (`>`)
#: repeats on each line.
# regex: a line break with the next line's indentation and comment marker, to
# put a wrapped quotation on one line. A string method would need one pass for
# each of the three markers.
WRAP_RE = re.compile(r"\n[ \t]*(?:#+:?|>)?[ \t]*")


def citation_after(document: str) -> re.Pattern[str]:
    """A mention of `document` followed closely by a quotation, in any kind of file.

    The code and the tests cite a section in several forms: after a section
    mark, a possessive, a comma or nothing, in a code span or bare, and with
    double or single quotation marks. So this reads the mention, then at most
    forty characters that end no sentence, then the quotation. A quotation
    opens on a letter, a digit or a code span, so the closing mark of a string
    literal that holds the path opens none.
    """
    # regex: a path, a short gap and a quotation, read in Python, Markdown, JSON
    # and TOML alike. The Markdown reader in `tools/doc_check.py` reads only a
    # document, a brief and a docstring, which is why the first run of this
    # move missed the citations in string literals and comments.
    return re.compile(
        r"(?P<document>" + re.escape(document) + r")"
        r"(?P<gap>`?(?:['’]s)?+(?:[^\"'\n.;]|\.(?!\s)|" + WRAP_RE.pattern + r"){0,40}?)"
        r"(?:\"(?P<double>[\w`][^\"]{2,400}?)\"|'(?P<single>[\w`][^'\n]{2,200}?)')"
    )


@dataclass(frozen=True)
class Repointed:
    """What `repoint` did in the tree, and the citations it could not place."""

    #: Each file changed, with how many citations in it were re-pointed.
    changed: dict[str, int]
    #: Each citation of the source whose quotation neither document holds.
    unplaced: list[str]


def _tracked_texts(root: Path) -> Iterator[str]:
    """Each tracked file `repoint` reads: text, and no record or closed item."""
    store = load(root).items_dir.strip("/") + "/"
    live = {path.as_posix() for path, _ in doc_check._live_item_briefs(root)}
    for path in listed_paths(read_git(["ls-files", "-z"], root)):
        name = PurePosixPath(path)
        if name.suffix not in REPOINTED_SUFFIXES and name.name != "Makefile":
            continue
        if path.startswith(RECORD_DIRS) or (path.startswith(store) and path not in live):
            continue
        if (root / path).is_file():
            yield path


def repoint(
    root: Path, source: str, destination: str, paths: Iterable[str] | None = None
) -> Repointed:
    """Re-point each citation of a section that moved from `source` to `destination`.

    Run it after `move_sections`. It reads both documents as they now stand, so
    running it twice changes nothing more.

    A citation that names `source` and then quotes it is re-pointed in two
    cases. The first is when the quotation names a heading of `destination`
    and no heading of `source`. The second is when it names no heading of
    either, `destination` holds its words and `source` does not. A quotation
    that neither document holds, and that follows `source` directly or after a
    section mark, a possessive or a comma, is returned as unplaced, for a
    person to read.

    Inside the two documents, a section mark with no document before it used
    to name a section of the same file. Where the section is now a heading of
    the other document only, the mark gets that document's path before it, and
    loses a following "above" or "below".

    `paths` is the files to read, and every tracked text file by default. A
    closed item and a release note are records, and are not read.
    """
    texts = {name: (root / name).read_text(encoding="utf-8") for name in (source, destination)}
    heads = {name: doc_check._headings(text) for name, text in texts.items()}
    bodies = {name: doc_check._comparable_statements(text) for name, text in texts.items()}
    changed: dict[str, int] = {}
    unplaced: list[str] = []
    pattern = citation_after(source)

    def moved(quoted: str) -> bool | None:
        """Whether the quotation's home is now `destination`; `None` when it has none."""
        term = doc_check._normalized(WRAP_RE.sub(" ", quoted))
        if "..." in term or "…" in term:
            return False
        if doc_check._cites_heading(term, heads[source]):
            return False
        if doc_check._cites_heading(term, heads[destination]):
            return True
        words = doc_check._comparable(doc_check._without_emphasis(term)).rstrip(" .,;:")
        if words in bodies[source]:
            return False
        return True if words in bodies[destination] else None

    def cross_references(name: str, text: str) -> list[tuple[int, int, str]]:
        """The edits that name the other document before a mark whose section moved there."""
        other = destination if name == source else source
        prose = doc_check.without_fences(text)
        edits: list[tuple[int, int, str]] = []
        for match in doc_check._statement_matches(doc_check.CITATION_RE, prose, PROSE):
            before = match.string[max(match.pos, match.start() - 200) : match.start() + 1]
            if match["term"] is None or doc_check.QUALIFIED_RE.search(before):
                continue
            term = doc_check._normalized(match["term"])
            if doc_check._cites_heading(term, heads[name]) or not doc_check._cites_heading(
                term, heads[other]
            ):
                continue
            edits.append((match.start(), match.start(), f"`{other}` "))
            direction = doc_check.DIRECTION_RE.match(match.string, match.end(), match.endpos)
            if direction:
                edits.append((direction.start(), direction.end(), ""))
        return edits

    # The two documents are read even where git does not track one yet.
    read = list(_tracked_texts(root) if paths is None else paths)
    for path in dict.fromkeys([*read, source, destination]):
        try:
            text = (root / path).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        edits: list[tuple[int, int, str]] = []
        for match in pattern.finditer(text):
            quoted = match["double"] or match["single"]
            home = moved(quoted)
            if home:
                edits.append((match.start("document"), match.end("document"), destination))
            elif home is None and CLAIMING_GAP_RE.fullmatch(match["gap"]) and len(quoted) < 120:
                row = text.count("\n", 0, match.start()) + 1
                unplaced.append(f"{path}:{row}: {' '.join(quoted.split())[:80]}")
        count = len(edits)
        if path in texts:
            crossed = cross_references(path, text)
            count += sum(1 for _, _, new in crossed if new)
            edits += crossed
        if not edits:
            continue
        for start, end, new in sorted(edits, reverse=True):
            text = text[:start] + new + text[end:]
        (root / path).write_text(text, encoding="utf-8")
        changed[path] = count
    return Repointed(changed, unplaced)


#: A quotation that may name a section, in double or single quotation marks.
# regex: a quotation in any kind of text file, as `citation_after` reads one.
# It opens on a letter, a digit or a code span, so a possessive's apostrophe
# opens none.
LATER_QUOTATION_RE = re.compile(
    r"\"([\w`][^\"\n]{2,200}?(?:\n[^\"\n]{0,200}?){0,2}?)\"|(?<![\w])'([\w`][^'\n]{2,120}?)'(?![\w])"
)


def _mentions(text: str, documents: Sequence[str]) -> list[tuple[int, str]]:
    """Where `text` names each of `documents`, in order, as the offset and the path."""
    found: list[tuple[int, str]] = []
    for document in documents:
        start = text.find(document)
        while start != -1:
            found.append((start, document))
            start = text.find(document, start + len(document))
    return sorted(found)


def _to_paragraph_end(span: str) -> str:
    """`span` up to its first blank line, or its first line that holds only a comment marker."""
    lines = span.split("\n")
    kept = len(lines[0])
    for line in lines[1:]:
        if line.strip().rstrip(":").strip("#") == "":
            return span[:kept]
        kept += 1 + len(line)
    return span


def misattributed(
    root: Path, source: str, destination: str, paths: Iterable[str] | None = None
) -> list[str]:
    """Each quotation after a mention of one document that names a heading only the other has.

    `repoint` changes the path before the first quotation after it. A sentence
    that names one document and then two sections, such as "`docs/MODEL.md`
    § "A" and § "B"", keeps one path for both, which is wrong when the move
    parted them (`PL-CTXZ`, found by both blind review passes). No rule says
    where the second path belongs in the sentence, so each is listed for a
    person to read. A mark with no document before it, inside the two
    documents, is listed too where it follows a mention of the other one.
    """
    documents = (source, destination)
    heads = {
        name: doc_check._headings((root / name).read_text(encoding="utf-8")) for name in documents
    }
    found: list[str] = []
    for path in _tracked_texts(root) if paths is None else paths:
        try:
            text = (root / path).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        mentions = _mentions(text, documents)
        for index, (start, own) in enumerate(mentions):
            after = start + len(own)
            end = mentions[index + 1][0] if index + 1 < len(mentions) else len(text)
            span = _to_paragraph_end(text[after : min(end, after + 500)])
            other = destination if own == source else source
            for quoted in LATER_QUOTATION_RE.finditer(span):
                term = doc_check._normalized(WRAP_RE.sub(" ", quoted.group(1) or quoted.group(2)))
                if doc_check._cites_heading(term, heads[other]) and not doc_check._cites_heading(
                    term, heads[own]
                ):
                    row = text.count("\n", 0, after + quoted.start()) + 1
                    found.append(f"{path}:{row}: after {own}: {term[:80]}")
    return found


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to run in")
    commands = parser.add_subparsers(dest="command", required=True)
    ids = commands.add_parser("ids", help="item ids the named sections still cite")
    ids.add_argument("headings", nargs="+", metavar="HEADING", help="a heading's text, no hashes")
    lost = commands.add_parser("lost", help="facts the documents held at the fork and not now")
    lost.add_argument("--base", help="branch to diff against; the default branch by default")
    move = commands.add_parser("move", help="move sections to another document, then re-point")
    move.add_argument("--from", dest="source", default=MODEL_DOC, help="the document to cut from")
    move.add_argument("--to", dest="destination", required=True, help="an existing document")
    move.add_argument("headings", nargs="+", metavar="HEADING", help="a heading's text, no hashes")
    again = commands.add_parser("repoint", help="re-point citations of sections already moved")
    again.add_argument("--from", dest="source", default=MODEL_DOC, help="the document cut from")
    again.add_argument("--to", dest="destination", required=True, help="where the sections went")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.command == "ids":
        documents = {path: split_lines(text) for path, text in specification_now(root)}
        nowhere = [
            title
            for title in args.headings
            if all(section_lines(lines, title) is None for lines in documents.values())
        ]
        if nowhere:
            names = ", ".join(documents)
            print("\n".join(f'{names}: no heading reads "{title}"' for title in nowhere))
            return 2
        out: list[str] = []
        for path, lines in documents.items():
            titles = [title for title in args.headings if section_lines(lines, title)]
            out += report_ids(lines, titles, path)[1]
        print(
            "\n".join(out)
            if out
            else "The named sections cite no item id outside the declared-none form."
        )
        return 1 if out else 0
    if args.command in ("move", "repoint"):
        if not (root / args.destination).is_file():
            print(f"model_rewrite: {args.destination} does not exist; write its title first")
            return 2
        if args.command == "move":
            missing = move_sections(root, args.source, args.destination, args.headings)
            if missing:
                print(
                    "\n".join(f'{args.source}: no one section reads "{title}"' for title in missing)
                )
                return 2
        try:
            done = repoint(root, args.source, args.destination)
        except (GitUnanswered, OSError) as error:
            print(f"model_rewrite: no answer: {error!r}", file=sys.stderr)
            return 1
        total = sum(done.changed.values())
        print(f"Re-pointed {total} citations in {len(done.changed)} files:")
        print("\n".join(f"  {count:4d}  {path}" for path, count in sorted(done.changed.items())))
        if done.unplaced:
            print(
                f"\n{len(done.unplaced)} citations of {args.source} quote words that neither "
                "document holds. Read each:"
            )
            print("\n".join(f"  {line}" for line in done.unplaced))
        later = misattributed(root, args.source, args.destination)
        if later:
            print(
                f"\n{len(later)} quotations follow a mention of one document and name a "
                "section that only the other has. Read each, and name the right document "
                "before it:"
            )
            print("\n".join(f"  {line}" for line in later))
        return 0
    base = args.base or default_base(root)
    if args.base is None and not resolved(base):
        print(
            f"model_rewrite: no answer: the default branch is unknown ({base!r} is a guess)",
            file=sys.stderr,
        )
        return 1
    try:
        fork, against = doc_check._diff_from(root, base)
        before, fork_starts = joined(specification_at_fork(root, fork))
        added = added_to_items(root, fork)
    except (GitUnanswered, OSError) as error:
        print(f"model_rewrite: no answer: {error!r}", file=sys.stderr)
        return 1
    after, starts = joined(specification_now(root))
    gone, more = pair_restated(
        before, after, gone_facts(before, after, added), added_facts(before, after)
    )
    # Each line is reported in its own document, whose path opens the quoted text.
    gone = [
        replace(item, line=line, context=f"{path}: {item.context}")
        for item in gone
        for path, line in [placed(item.line, fork_starts)]
    ]
    more = [
        replace(item, line=line, context=f"{path}: {item.context}")
        for item in more
        for path, line in [placed(item.line, starts)]
    ]
    names = " and ".join(path for _, path in starts)
    print("\n".join(report_gone(gone, against, names) + report_added(more)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
