"""A notes file's threads, as a map from item id to the sections that name it.

A project may keep a running cross-session log beside its queue: threads that
outlive their items, span several, or have none. The file earns its keep only
if a session reaching one of its threads is told so, and the instruction such
a file usually carries - read it if your task touches an open thread - cannot
be followed, because evaluating the condition means reading the file. This
module removes that circularity by answering the decidable half from the
headings.

**It computes; it decides nothing.** Whether a thread is still true, still
relevant, or worth the read is not derivable from the file, so none of it is
attempted. What is derivable is which sections name an id, and that is all
this returns - a pointer with a line number, for a session that has already
chosen its work.

The two kinds of mention are kept apart because they carry different weight
and a reader needs to tell them apart. An id in the **heading** is what the
thread is about; an id in the **body** is a thread that mentions it in
passing. Measured on this repository's own notes file on 2026-09-14: 31 of the
106 ids it cites appear in a heading, so heading-only would have said nothing
at all for 75 of them - and silence is indistinguishable from "no thread
concerns your item", which is the failure being fixed rather than a cheaper
version of it. Reading bodies too matched 105 of the 106, and stayed precise:
74 ids reach exactly one thread, 23 reach two, 7 reach three, and the one
cross-cutting id reaches six.

No path is hardcoded. The file is named by the project through
`Config.notes_file`, whose default is empty, so a project without one is
unaffected and this package keeps no notion of the repository it grew in.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .roadmap import HEADING_RE
from .store import ID_PATTERN

THREAD_HEADING_LEVEL = 2
"""The heading level a thread is written at: `##`.

Fixed rather than configurable. A notes file's `#` is its title and its `###`
are subsections of a thread, so the level that means "a thread" is the same
wherever this convention is used, and a knob here would be one more thing to
get wrong for no reader's benefit.
"""

_ID_RE = re.compile(ID_PATTERN)

_OPEN_HEADING_RE = re.compile(r"^\s*open\b", re.IGNORECASE)
"""The leading word that says a thread is still open: `Open thread:`, `Open:`.

Anchored at the start and bounded at the end, so `Opening the vaporizer`
does not match a word it merely begins with, and the status words this
convention uses instead - `Settled:`, `Decided:`, `Measured`, `Built`,
`Shelved`, `Aspirational`, `Long-term` - do not match at all.
"""


@dataclass(frozen=True)
class Thread:
    """One `##` section of the notes file, and the ids it names."""

    title: str
    line: int
    about: tuple[str, ...]
    mentions: tuple[str, ...]

    def concerns(self, identifier: str) -> bool:
        return identifier in self.about or identifier in self.mentions

    @property
    def cites(self) -> tuple[str, ...]:
        """Every id the section names, heading first and in reading order.

        The two kinds are stored apart because a reader weighs them
        differently. A caller asking whether the thread's items have *all*
        closed weighs them the same, and would otherwise re-derive the union
        at each call site.
        """
        return self.about + self.mentions

    @property
    def declares_open(self) -> bool:
        """Whether the heading's own leading word says the thread is open.

        Read from the first word and from nowhere else. A body says "still
        open" while arguing the opposite often enough that scanning one turns
        a decidable question into a guess, and the heading is both the half
        its writer maintains and the half a reader skimming the file sees.

        This reports what the file says about itself, which is a claim rather
        than a fact - and that is the point. It is worth something only
        against evidence the file does not control.
        """
        return _OPEN_HEADING_RE.match(self.title) is not None


def read(path: Path) -> tuple[Thread, ...]:
    """Return every thread in the file, or nothing if there is no file.

    A missing file is not an error. The setting is optional, a project may
    delete its notes file, and a checkout may be truncated - in all three the
    honest answer is that no thread was found, which is what an empty result
    says. Raising instead would make `docket show` fail on an item that is
    perfectly fine.
    """

    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ()

    threads: list[Thread] = []
    title = ""
    line_number = 0
    about: list[str] = []
    body: list[str] = []

    def flush() -> None:
        if not title:
            return
        named = dict.fromkeys(about)
        threads.append(
            Thread(
                title=title,
                line=line_number,
                about=tuple(named),
                mentions=tuple(i for i in dict.fromkeys(body) if i not in named),
            )
        )

    for number, line in enumerate(text.splitlines(), start=1):
        heading = HEADING_RE.match(line)
        if heading is not None and len(heading.group("hashes")) == THREAD_HEADING_LEVEL:
            flush()
            title = heading.group("title")
            line_number = number
            about = _ID_RE.findall(title)
            body = []
        elif title:
            body.extend(_ID_RE.findall(line))

    flush()
    return tuple(threads)


def concerning(threads: tuple[Thread, ...], identifier: str) -> tuple[Thread, ...]:
    """Return the threads naming this id, the ones it is *about* first.

    Ordered rather than filtered: a thread whose heading names the id is the
    one to read first, and where several match, the reader should not have to
    work out which is which from the line numbers.
    """

    matched = [thread for thread in threads if thread.concerns(identifier)]
    return tuple(sorted(matched, key=lambda thread: (identifier not in thread.about, thread.line)))
