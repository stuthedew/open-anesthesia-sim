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
  does, with the line where the fork held it. A fact the branch added to a
  file under the item store is marked `moved`. Item ids and dates are counted
  apart, because they are the history the part removes on purpose. Exits 0
  whenever it read both versions, since whether a dropped number was history
  or a value is a judgment for the session and the owner. Exits 1 when git
  could not answer.

The pull request of each section part accounts for every line `lost` prints.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "subprojects" / "docket" / "src"))

from docket.config import load  # noqa: E402
from docket.lines import split_lines  # noqa: E402
from docket.markdown import headings  # noqa: E402
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
#: A number as written in prose, with its thousands separators and decimals.
PROSE_NUMBER_RE = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)*(?![\w])")

#: The kinds `lost` prints one by one, in the order it prints them.
FACT_KINDS = ("equation", "code", "citation", "number")
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

    An equation is read before the code spans, and both before the numbers, so
    a number inside an equation or a code span counts once, as part of it.
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
    scanned = "".join(blank)
    for match in PULL_RE.finditer(scanned):
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


def report_gone(gone: Sequence[Gone], against: str) -> list[str]:
    """The lines `lost` prints: the facts by kind, then the history it counts."""
    facts_gone = [item for item in gone if item.kind in FACT_KINDS]
    moved = sum(item.moved for item in facts_gone)
    out = [
        f"{MODEL_DOC} against {against}: {len(facts_gone)} equations, code spans, citations "
        f"and numbers are held fewer times than at the fork, and {moved} of them were added "
        "to an item file."
    ]
    for kind in FACT_KINDS:
        rows = sorted((item for item in facts_gone if item.kind == kind), key=lambda g: g.line)
        if not rows:
            continue
        out += ["", f"{kind} ({len(rows)})"]
        for item in rows:
            mark = "moved" if item.moved else "gone "
            times = f" x{item.times}" if item.times > 1 else ""
            out.append(f"  {mark} {item.text}{times}  (fork line {item.line}: {item.context[:90]})")
    for kind in HISTORY_KINDS:
        texts = sorted({item.text for item in gone if item.kind == kind})
        if texts:
            out += ["", f"{kind}s no longer cited ({len(texts)}): {', '.join(texts)}"]
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
    print("\n".join(report_gone(gone_facts(before, after, added), against)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
