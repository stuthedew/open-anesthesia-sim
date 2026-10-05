"""An instruction set's dated assertions, and how old each one has become.

A project's instructions assert facts about a world that changes - a network
policy, what a tool does, what a check catches, which agent is running - and
nothing expires any of them. A rule that is long costs attention; a rule that
was true when it was written and is false two years later gets *obeyed*. Every
size gauge a project keeps is blind to that, because it measures how much text
there is rather than how old what the text claims has become.

**It computes; it decides nothing.** Which assertions are due for re-checking
is arithmetic on dates. Whether an aged assertion is still *true* is judgment,
and none of it is attempted here - the same split `notes.py` keeps, and the
one `CLAUDE.md` names when it says to find the decidable part and leave the
rest prose.

No path is hardcoded. The files are named by the project through
`Config.instruction_paths`, whose default is empty, so a project that declares
none is unaffected and this package keeps no notion of the repository it grew
in.

**The unit is the sentence, dated by the newest date in it, and that choice
is what lets the report reach zero.** Counted per date *occurrence*, a record
re-verified by appending a second date would keep reporting its first one
forever, and an advisory that cannot be discharged costs the next advisory its
reader (`checks.py` makes the same argument about the selector that named
thirty-one items). Newest-date-per-sentence gives every kind of dated text one
discharge that is also honest: re-read the claim, and write today beside it.
A measured fact is re-measured and re-dated; a *record* - what the project
owner decided, and when - keeps its original date and gains a re-verification
one, so nothing has to be falsified to clear it.

**A sentence, not the line, because the record wraps** (`PL-B1D0`). A
paragraph goes on across its soft breaks, so "(measured 2026-06-01,
re-verified" on one line and "2026-10-04)." on the next is one record, and read
a line at a time it was two assertions, the first already old: `CLAUDE.md`
carried two such records on 2026-10-04, and its line 229 would have been
reported stale on 2026-12-16, when its newest date made it 86 days old. Not the
whole paragraph either, which would date a long rule by the newest of every
record inside it and hide the old ones. The paragraphs are
`markdown.statement_lines`', the one reading of where a Markdown statement ends
(`PL-R417`), and the sentences `SENTENCE_BREAK`'s. Re-reading the instruction
set this way on 2026-10-04 moved seven of its date occurrences, every one onto
a newer date, and split no line's dates between two sentences.

Measured on this repository on 2026-09-21: 74 date occurrences on 71 lines
across 17 of the 22 files in its instruction set, the oldest 21 days old.
"""

from __future__ import annotations

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .markdown import statement_lines
from .roadmap import SENTENCE_BREAK

ISO_DATE_RE = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
"""An ISO date written out in prose: `2026-09-21`.

Bounded at both ends, so a timestamp (`2026-09-21T09:00`) and a version-like
run of digits do not match something they merely begin with. Four digits
beginning `20` rather than `\\d{4}`, because a bare `1999-01-01` in an
instruction file is far likelier to be an example than a claim about now.
"""


@dataclass(frozen=True)
class Assertion:
    """One sentence of instruction text carrying a date, and the date it carries."""

    file: str
    #: The line holding the newest date, which is where a reader re-dates it.
    line: int
    #: The newest date in the sentence. See the module docstring: this is what
    #: makes "re-verified <today>" a discharge rather than a second entry.
    when: date
    #: The sentence itself, on one line. Clipped by whoever reports it, not here -
    #: a caller printing one entry per screen and a caller printing five on
    #: one line want different widths, and the reading is the same either way.
    text: str

    def age(self, today: date) -> int:
        """Days since the newest date in the sentence.

        Negative where the sentence is dated in the future, which a project does
        deliberately: this repository dates a cutover setting one day ahead so
        the set it grandfathers is closed at what the store held when the rule
        began working. A future date is simply not yet due, which is what a
        negative age already says to any threshold comparison.
        """
        return (today - self.when).days


def _dates(text: str) -> list[tuple[date, int]]:
    """Every readable date in `text`, with its offset, in the order they are written.

    A match that is not a real date - `2026-13-45`, the day a month does not
    have - is dropped rather than raised on. The regex admits it because it
    only counts digits, and an instruction file is prose: something shaped
    like a date and not being one is a typo, and refusing to read the whole
    file over it would take the audit down instead of the sentence.
    """
    found: list[tuple[date, int]] = []
    for match in ISO_DATE_RE.finditer(text):
        year, month, day = match.groups()
        try:
            found.append((date(int(year), int(month), int(day)), match.start()))
        except ValueError:
            continue
    return found


def _sentences(text: str) -> Iterator[tuple[int, int]]:
    """Each sentence of one statement's text, as its offsets."""
    start = 0
    for stop in SENTENCE_BREAK.finditer(text):
        yield start, stop.end()
        start = stop.end()
    if text[start:].strip():
        yield start, len(text)


def parse(name: str, text: str) -> list[Assertion]:
    """The dated sentences of one instruction file, outside its fenced blocks.

    Dates inside a fence are skipped, and the reason is discharge rather than
    precision. This repository's `.claude/skills/docket/modes/capture.md` carries
    a worked `bin/docket new "... standing in the queue on 2026-09-21"` - a
    template for writing an item title, not a claim about the world. Naming it
    would put an entry in the report that a reader cannot honestly clear, since
    clearing it means editing an example to say something it does not mean, and a
    permanent undischargeable entry is exactly what stops a report reaching zero.
    One such line on 2026-09-21, of 74 date occurrences.

    `fences` decides where a fence is, so a triple-backtick code span wrapped to
    a line's start opens none, and an opener nothing closes hides no date below
    it (`PL-92MY`).
    """
    lines = text.splitlines()
    assertions: list[Assertion] = []
    for first, end in statement_lines(lines):
        statement = "\n".join(lines[first:end])
        for start, stop in _sentences(statement):
            found = _dates(statement[start:stop])
            if not found:
                continue
            when, offset = max(found)
            line = first + 1 + statement.count("\n", 0, start + offset)
            words = " ".join(statement[start:stop].split())
            assertions.append(Assertion(file=name, line=line, when=when, text=words))
    return assertions


def _markdown_under(root: Path, paths: Sequence[str]) -> list[str]:
    """Every `.md` at or beneath the named files and directories, once each.

    A file entry is taken as it stands; a directory entry is walked. Sorted
    and de-duplicated, so a project naming both a directory and a file inside
    it reads that file once and the report comes out in a stable order.
    """
    names: list[str] = []
    for entry in paths:
        path = root / entry
        if path.is_file():
            names.append(entry)
        elif path.is_dir():
            names += (
                found.relative_to(root).as_posix()
                for found in path.rglob("*.md")
                if found.is_file()
            )
    return sorted(dict.fromkeys(names))


def read(root: Path, paths: Sequence[str]) -> tuple[Assertion, ...]:
    """Every dated assertion in the project's instruction set.

    A file that cannot be read is skipped rather than raised on, for the
    reason `notes.read` gives: the setting is optional, a project may delete
    or move an instruction file, and a checkout may be truncated. In all three
    the honest answer is that those lines were not found, which an absent
    entry says. Raising would take a grooming pass down over a file nobody
    was asking about.
    """
    assertions: list[Assertion] = []
    for name in _markdown_under(root, paths):
        try:
            text = (root / name).read_text(encoding="utf-8")
        except OSError:
            continue
        assertions += parse(name, text)
    return tuple(assertions)
