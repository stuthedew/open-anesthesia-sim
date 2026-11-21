"""What a closed item records to show that its work was done, and the one check of it.

The project owner chose on 2026-11-21 that what shows an item's work depends
on the kind of work, and that it is checked once, on the branch that closes
the item, and never again (`PL-LFJZ`). Before that every item carried a shell
command in `verify:`, written at triage and re-run for as long as the item
was open.

An item that changes code records the tests that show its work in `tests:`,
as pytest node ids, when it closes (`PL-FN11`). A test named at triage is a
guess at a name: `PL-0M32` and `PL-6TN8` each closed late because the work
shipped a test under another name. A named test also decays after the close.
Of 1,060 closed items whose command named a test, 109 named one that a later
change renamed or removed, so the names are read on the closing branch only.

An item that deletes code or changes only a document keeps one search for
fixed text in `verify:`, as `grep -qF 'words' path` for words the work adds
or `! grep -qF 'words' path` for words it removes (`PL-N046`). docket reads
the files itself and runs no shell. It reads the words with every run of
spaces and line breaks as one space, so a phrase that a document wraps over
two lines is found, where `grep` read it on neither line (`PL-RR1N`).

An item whose work is a result written into its own brief records neither.
The paragraph that states the result opens with a bold label carrying a date,
such as `**Answered 2026-11-20.**`, and that paragraph is the record
(`PL-NY7Q`).

`closing_faults` is the reading of the first two. `bin/docket check` asks it about the
closures the checkout introduces, and `bin/docket verify` about the item it
audits.

Standard library only. It reads the working tree, and asks `vcs` for what a
file held where the branch left the default base.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Collection, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from .fences import without_fences
from .lines import ENCODING
from .model import RELEASE_TRAIN, Item
from .python import UNTOKENIZABLE, places, read_logical_lines, refusal
from .shell import argv
from .vcs import ForkTexts, Runner, texts_at_fork

#: A pytest node id as `tests:` holds one: a Python file, then the names that
#: lead to the test, outermost first. A parameter set (`[...]`) is left out,
#: because the entry names the test function and every set of it.
NODE_RE = re.compile(r"(?P<path>[^\s:\[\]]+\.py)(?P<names>(?:::[A-Za-z_][A-Za-z0-9_]*)+)")


@dataclass(frozen=True)
class Node:
    """One entry of `tests:`: the file, and the test's name as `python.places` spells it."""

    path: str
    name: str


def read_node(entry: str) -> Node | None:
    """The file and test that one `tests:` entry names, or `None` where it is no node id."""
    match = NODE_RE.fullmatch(entry)
    if match is None:
        return None
    return Node(path=match["path"], name=match["names"][2:])


def node_refusal(entry: str) -> str:
    """Why `entry` cannot stand in `tests:`, or `""` where it can."""
    if read_node(entry) is not None:
        return ""
    if "[" in entry:
        return f"`{entry}` names one parameter set; name the test function, which covers every set"
    return (
        f"`{entry}` is not a pytest node id; write the test file, then `::` and the test's "
        "name, with its class between them where it has one"
    )


def test_code(source: str, name: str) -> str | None:
    """The code of the test `name` in `source`, or `None` where `source` defines no such test.

    Its statements as the tokenizer reads them, decorators included, so that a
    changed comment or a re-wrapped line is the same test. Raises one of
    `UNTOKENIZABLE` where the tokenizer refuses `source`.
    """
    lines = read_logical_lines(source)
    held = [
        line.tokens
        for line, place in zip(lines, places(lines), strict=True)
        if place == name or place.startswith(f"{name}::")
    ]
    return "\n".join(held) if held else None


def test_faults(
    entries: Sequence[str], read: Callable[[str], str | None], fork: ForkTexts
) -> tuple[list[str], list[str]]:
    """What is wrong with each test `entries` names, and what could not be read.

    `read` gives a path's text in the working tree, or `None` where it is no
    file, and may raise `ValueError` for text it cannot decode. A test shows
    the work where the tree defines it and the branch added or changed it,
    measured against `fork`.
    """
    faults: list[str] = []
    unread: list[str] = []
    for entry in entries:
        node = read_node(entry)
        if node is None:
            continue  # `checks` refuses the entry's form for every item, closing or not
        try:
            text = read(node.path)
            here = None if text is None else test_code(text, node.name)
        except UNTOKENIZABLE as error:
            unread.append(f"{node.path} could not be read ({refusal(error)})")
            continue
        if text is None:
            faults.append(f"`{entry}` names a file the tree does not hold")
            continue
        if here is None:
            faults.append(f"`{entry}` names a test that {node.path} does not define")
            continue
        before = fork.texts.get(node.path)
        if before is None:
            continue
        try:
            there = test_code(before, node.name)
        except UNTOKENIZABLE as error:
            unread.append(f"{node.path} at {fork.fork[:12]} could not be read ({refusal(error)})")
            continue
        if there == here:
            faults.append(
                f"`{entry}` names a test this branch neither added nor changed, so it "
                "passed before the work and shows nothing about it"
            )
    return faults, unread


@dataclass(frozen=True)
class TextSearch:
    """One search for fixed text, as a closing item's `verify:` spells it."""

    #: Whether the words must be absent, which `!` ahead of `grep` says.
    absent: bool
    words: str
    #: Each file to read, from the repository's root. A `*` matches within one directory.
    paths: tuple[str, ...]


def read_text_search(command: str) -> TextSearch | str:
    """The one search `command` spells, or why it is not one, as a predicate for "its `verify:`"."""
    words = argv(command)
    if words is None:
        return (
            "is not one command of plain words; a closing item keeps one "
            "`grep -qF 'words' path` or `! grep -qF 'words' path`"
        )
    absent = words[0] == "!"
    rest = words[1:] if absent else words
    if rest[:2] != ("grep", "-qF"):
        return (
            f"runs `{' '.join(rest[:2])}`, where a closing item keeps one "
            "`grep -qF 'words' path` or `! grep -qF 'words' path`. Where the command "
            "names a test, record the test in `tests:` and remove the command with "
            "`--verify ''`"
        )
    operands = rest[3:] if rest[2:3] == ("--",) else rest[2:]
    if len(operands) < 2:
        return "names no file to read after the words"
    text, paths = operands[0], operands[1:]
    if not text.split():
        return "searches for no words"
    for path in paths:
        if path.startswith(("-", "/")) or ".." in path.split("/") or "**" in path:
            return f"reads `{path}`, which is not a file under the repository's root"
    if not absent and any(path.endswith(".py") for path in paths):
        return (
            "searches a Python file for text the work adds; work that adds code is shown "
            "by a test, named in `tests:`, and a changed comment or docstring by "
            "`! grep -qF` for the words it replaced"
        )
    return TextSearch(absent=absent, words=text, paths=paths)


def _spaced(text: str) -> str:
    """`text` with each run of spaces and line breaks as one space."""
    return " ".join(text.split())


def search_faults(command: str, root: Path) -> list[str]:
    """What is wrong with the search a closing item's `verify:` holds, read on this tree."""
    search = read_text_search(command)
    if isinstance(search, str):
        return [f"its `verify:` {search}"]
    wanted = _spaced(search.words)
    faults: list[str] = []
    holding: list[str] = []
    for pattern in search.paths:
        files = sorted(path for path in root.glob(pattern) if path.is_file())
        if not files:
            faults.append(
                f"its `verify:` reads `{pattern}`, which the tree does not hold, so it "
                "cannot say whether the words are there"
            )
        for path in files:
            if wanted in _spaced(path.read_text(encoding=ENCODING, errors="replace")):
                holding.append(path.relative_to(root).as_posix())
    if search.absent and holding:
        faults.append(
            f"its `verify:` says the words `{search.words}` are gone, and "
            f"{', '.join(holding)} still holds them"
        )
    if not search.absent and not holding and not faults:
        faults.append(
            f"its `verify:` says the work adds the words `{search.words}`, and "
            f"{', '.join(search.paths)} does not hold them"
        )
    return faults


#: A bold label that carries a date and opens a paragraph, such as
#: `**Answered 2026-11-20.**` or `**Counted 2026-11-21**`. The label may run
#: on past the date, and the bold may close anywhere on the line.
DATED_LABEL_RE = re.compile(r"^\*\*[A-Z][^*\n]*\b\d{4}-\d{2}-\d{2}\b[^*\n]*\*\*", re.MULTILINE)


def dated_record(body: str) -> bool:
    """Whether a brief holds a paragraph that opens with a dated bold label (`PL-NY7Q`).

    An item whose work is a count, a measurement or a decision writes its
    result into its own brief, and that paragraph is the record of the work.
    """
    return DATED_LABEL_RE.search(without_fences(body)) is not None


def shows_its_work(item: Item) -> bool:
    """Whether a closed item records what shows its work, or why nothing can."""
    return bool(item.tests or item.verify or item.not_delegable) or dated_record(item.body)


@dataclass(frozen=True)
class ClosingReport:
    """What is wrong with what each closing item records, by id, or why that was not read."""

    faults: dict[str, tuple[str, ...]] = field(default_factory=dict)
    declined: str = ""


def _tree_text(root: Path) -> Callable[[str], str | None]:
    def read(path: str) -> str | None:
        target = root / path
        return target.read_text(encoding=ENCODING) if target.is_file() else None

    return read


def closing_faults(item: Item, root: Path, fork: ForkTexts) -> tuple[list[str], list[str]]:
    """What is wrong with what `item` records to show its work, and what could not be read.

    A release item keeps the command it has, because `bin/docket release`
    writes the version and the notes. An item recording `not-delegable:` has
    said why no search can show its work, so its command is not read either.
    """
    faults, unread = test_faults(item.tests, _tree_text(root), fork)
    if item.verify and item.resource != RELEASE_TRAIN and not item.not_delegable:
        faults += search_faults(item.verify, root)
    return faults, unread


def node_paths(items: Collection[Item]) -> set[str]:
    """Every file the `tests:` of `items` name."""
    return {
        node.path
        for item in items
        for entry in item.tests
        if (node := read_node(entry)) is not None
    }


def read_closing(
    root: Path, closing: Collection[Item], *, base: str = "", runner: Runner | None = None
) -> ClosingReport:
    """Read once what each item in `closing` records, on the branch that closes it.

    `closing` is the items this checkout closes and the default base does not
    yet hold closed. A merged closure is not among them, so nothing here is
    read again after the merge.
    """
    if not closing:
        return ClosingReport()
    fork = texts_at_fork(root, node_paths(closing), base=base, runner=runner)
    if not fork.fork:
        return ClosingReport(declined=fork.declined)
    faults: dict[str, tuple[str, ...]] = {}
    unread: list[str] = [fork.declined] if fork.declined else []
    for item in closing:
        found, missed = closing_faults(item, root, fork)
        unread += missed
        if found:
            faults[item.identifier] = tuple(found)
    return ClosingReport(faults=faults, declined="; ".join(unread))
