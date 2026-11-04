"""List what a section rewrite of `docs/MODEL.md` still cites, and what it has dropped.

`PL-ZT47` makes `docs/MODEL.md` readable for a clinician in fourteen section
parts. Each part moves the decision history out to the item files and then
rewrites the phrasing, and must not lose an equation, a unit, a value or a
citation. This tool answers the two questions that part asks of the tree.

- `ids HEADING...` prints each line of the named sections that cites an item
  id outside the declared-none form ``no test yet (`PL-XXXX`)``.
  `tools/doc_check.py` requires that form, so its ids stay. A section runs from
  its heading to the next heading of the same or a higher level, so it holds
  its subsections. Exits 1 when it prints a line, 0 when the sections cite no
  other id, and 2 when a heading is not in the document.
- `lost` compares the document at the commit where the branch forked from the
  default branch with the working tree. It prints each equation, code span,
  number and citation that the fork held more often than the working tree
  does, with the line where the fork held it. The declared-none form is a
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
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.config import load  # noqa: E402
from docket.lines import split_lines  # noqa: E402
from docket.markdown import Heading, headings  # noqa: E402
from docket.store import CITED_ID_RE  # noqa: E402
from docket.vcs import GitUnanswered, default_base, listed_paths, read_git, resolved  # noqa: E402

import doc_check  # noqa: E402
from product_paths import MODEL_DOC  # noqa: E402

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
    "1,5", returns `None`, so it is never paired.
    """
    parts = NUMBER_PARTS_RE.fullmatch(number)
    if parts is None:
        return None
    numeral = parts["numeral"].replace("−", "-")
    whole = numeral.lstrip("+-").partition(".")[0]
    if "," in numeral and any(len(group) != 3 for group in whole.split(",")[1:]):
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


def report_ids(lines: Sequence[str], titles: Sequence[str]) -> tuple[int, list[str]]:
    """The exit status and the lines `ids` prints for the sections named by `titles`."""
    out: list[str] = []
    missing = [title for title in titles if section_lines(lines, title) is None]
    if missing:
        return 2, [f'{MODEL_DOC}: no heading reads "{title}"' for title in missing]
    seen: set[int] = set()
    for title in titles:
        for start, end in section_lines(lines, title) or []:
            for cited in cited_ids(lines, start, end):
                if cited.line in seen:
                    continue
                seen.add(cited.line)
                out.append(f"{MODEL_DOC}:{cited.line}: {', '.join(cited.ids)}: {cited.text[:100]}")
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


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.partition("\n")[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository to run in")
    commands = parser.add_subparsers(dest="command", required=True)
    ids = commands.add_parser("ids", help="item ids the named sections still cite")
    ids.add_argument("headings", nargs="+", metavar="HEADING", help="a heading's text, no hashes")
    lost = commands.add_parser("lost", help="facts the document held at the fork and not now")
    lost.add_argument("--base", help="branch to diff against; the default branch by default")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.command == "ids":
        lines = split_lines((root / MODEL_DOC).read_text(encoding="utf-8"))
        status, out = report_ids(lines, args.headings)
        print(
            "\n".join(out)
            if out
            else "The named sections cite no item id outside the declared-none form."
        )
        return status
    base = args.base or default_base(root)
    if args.base is None and not resolved(base):
        print(
            f"model_rewrite: no answer: the default branch is unknown ({base!r} is a guess)",
            file=sys.stderr,
        )
        return 1
    try:
        fork, against = doc_check._diff_from(root, base)
        before = read_git(["show", f"{fork}:{MODEL_DOC}"], root)
        added = added_to_items(root, fork)
    except (GitUnanswered, OSError) as error:
        print(f"model_rewrite: no answer: {error!r}", file=sys.stderr)
        return 1
    after = (root / MODEL_DOC).read_text(encoding="utf-8")
    gone, more = pair_restated(
        before, after, gone_facts(before, after, added), added_facts(before, after)
    )
    print("\n".join(report_gone(gone, against) + report_added(more)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
