"""What a closed item records to show that its work was done, and the one check of it.

The project owner chose on 2026-11-21 that what shows an item's work depends
on the kind of work, and that it is checked once, on the branch that closes
the item, and never again (`PL-LFJZ`). Before that every item carried a shell
command in `verify:`, written at triage and re-run for as long as the item
was open.

An item that changes code records the tests that show its work in `tests:`,
as pytest node ids, when it closes (`PL-FN11`). A test counts as changed
where its own code changed, or a table, fixture or helper in its file that it
uses (`PL-YKQP`). A test named at triage is a
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

import keyword
import re
from collections.abc import Callable, Collection, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from .fences import without_fences
from .lines import ENCODING
from .model import RELEASE_TRAIN, Item
from .python import UNTOKENIZABLE, LogicalLine, places, read_logical_lines, refusal
from .shell import argv
from .vcs import ForkTexts, Runner, texts_at_fork


@dataclass(frozen=True)
class Node:
    """One entry of `tests:`: the file, and the test's name as `python.places` spells it."""

    path: str
    name: str


def read_node(entry: str) -> Node | None:
    """The file and test that one `tests:` entry names, or `None` where it is no node id.

    A pytest node id is a Python file, then `::` and the names that lead to
    the test, outermost first. A parameter set (`[...]`) is no part of one
    here, because the entry names the test function and every set of it.
    """
    path, _, names = entry.partition("::")
    if not path.endswith(".py") or ":" in path or any(c.isspace() for c in path):
        return None
    if not all(part.isidentifier() for part in names.split("::")):
        return None
    return Node(path=path, name=names)


def node_refusal(entry: str) -> str:
    """Why `entry` cannot stand in `tests:`, or `""` where it can."""
    if read_node(entry) is not None:
        return ""
    if "[" in entry:
        return (
            f"`{entry}` names one parameter set; name the test function, which covers every "
            "set and counts as changed where a table it reads changed"
        )
    return (
        f"`{entry}` is not a pytest node id; write the test file, then `::` and the test's "
        "name, with its class between them where it has one"
    )


def test_code(source: str, name: str) -> str | None:
    """The code of the test `name` in `source`, or `None` where `source` defines no such test.

    Its statements as the tokenizer reads them, decorators included, so that a
    changed comment or a re-wrapped line is the same test. The code also holds
    the statements of each class around the test that belong to no method, such
    as a decorator on the class, and every module-level statement and
    definition the test uses (`PL-YKQP`). A test can gain a case without a
    change to its own lines. A case added to a table that `parametrize` reads,
    or a changed fixture or helper in the same file, is such a change, so a
    test that uses one counts as changed. Uses are followed from definition to
    definition within the file, so a table built from a changed constant counts
    too. Code in another file, such as a fixture in `conftest.py`, is not read.

    Raises one of `UNTOKENIZABLE` where the tokenizer refuses `source`.
    """
    lines = read_logical_lines(source)
    found = places(lines)
    enclosing = name.split("::")
    scopes = {"::".join(enclosing[:depth]) for depth in range(1, len(enclosing))}
    own = [
        line
        for line, place in zip(lines, found, strict=True)
        if place == name or place.startswith(f"{name}::") or place in scopes
    ]
    if not any(place == name for place in found):
        return None
    units = _module_units(lines, found, enclosing)
    used: list[_Unit] = []
    wanted = set().union(*(_mentions(line) for line in own))
    seen: set[str] = set()
    while wanted - seen:
        word = (wanted - seen).pop()
        seen.add(word)
        for unit in units:
            if word in unit.binds and unit not in used:
                used.append(unit)
                wanted |= unit.mentions
    used.sort(key=lambda unit: unit.at)
    return "\n".join([*(line.tokens for line in own), *(unit.code for unit in used)])


@dataclass(frozen=True)
class _Unit:
    """One module-level statement or definition of a test file, as `test_code` follows it."""

    #: Where it opens, which orders the units as the file does.
    at: int
    #: The names it defines or assigns at module level.
    binds: frozenset[str]
    #: The names its code mentions, which it may use.
    mentions: frozenset[str]
    #: Its code as the tokenizer reads it, which is what is compared.
    code: str


#: The operators that assign to the names before them.
_ASSIGNS = frozenset(
    {"=", "+=", "-=", "*=", "/=", "//=", "%=", "@=", "&=", "|=", "^=", ">>=", "<<=", "**="}
)


def _mentions(line: LogicalLine) -> set[str]:
    """Every name `line` mentions, keywords left out."""
    return {
        piece.code
        for piece in line.pieces
        if piece.code.isidentifier() and not keyword.iskeyword(piece.code)
    }


def _module_units(
    lines: Sequence[LogicalLine], found: Sequence[str], test: Sequence[str]
) -> list[_Unit]:
    """The definitions and module-level statements a test at `test` may use, itself left out.

    `test` is the test's name and the classes that hold it, outermost first. A
    definition is one unit with its decorators and its body: a top-level one,
    or a method of a class that holds the test. A statement that no definition
    holds is a unit of its own, and binds the names it assigns or imports. Each
    name of an import is a unit of its own, so that adding a name to an import
    line changes nothing for a test that uses another name on it.
    """
    units: list[_Unit] = []
    held: dict[str, list[int]] = {}
    for at, place in enumerate(found):
        if place:
            key = _unit_place(place.split("::"), test)
            if key:
                held.setdefault(key, []).append(at)
            continue
        line = lines[at]
        imports = _imported(line)
        if imports:
            units += [_Unit(at, frozenset({bound}), frozenset(), code) for bound, code in imports]
        else:
            units.append(_Unit(at, _assigned(line), frozenset(_mentions(line)), line.tokens))
    for key, ats in held.items():
        code = [lines[at] for at in ats]
        mentions = set().union(*(_mentions(line) for line in code))
        bound = frozenset({key.rsplit("::", 1)[-1]})
        units.append(_Unit(ats[0], bound, frozenset(mentions), "\n".join(c.tokens for c in code)))
    return units


def _unit_place(place: Sequence[str], test: Sequence[str]) -> str:
    """The definition a line at `place` belongs to as a unit, or `""` where it is the test's own.

    That is the top-level definition holding it, or the method holding it of a
    class that holds the test. The test itself, and the lines of its classes
    that belong to no method, are the test's own code.
    """
    depth = 0
    while depth < len(test) - 1 and depth < len(place) - 1 and place[depth] == test[depth]:
        depth += 1
    key = list(place[: depth + 1])
    return "" if key == list(test[: len(key)]) else "::".join(key)


def _imported(line: LogicalLine) -> list[tuple[str, str]]:
    """Each name an `import` statement binds, with what it binds it to; none for another line."""
    words = [piece.code for piece in line.pieces]
    if words[0] not in ("import", "from") or "import" not in words:
        return []
    cut = words.index("import")
    source = " ".join(words[:cut])
    names = [word for word in words[cut + 1 :] if word not in ("(", ")")]
    found: list[tuple[str, str]] = []
    while names:
        comma = names.index(",") if "," in names else len(names)
        part, names = names[:comma], names[comma + 1 :]
        if not part:
            continue
        bound = part[-1] if "as" in part else part[0]
        found.append((bound, f"{source} import {' '.join(part)}"))
    return found


def _assigned(line: LogicalLine) -> frozenset[str]:
    """The names a module-level statement assigns, as the targets before its last `=` name them.

    A name counts where it stands outside brackets and after no dot, so that
    `TABLE[key] = value` assigns `TABLE`, and `TABLE: dict[str, int] = {}`
    assigns `TABLE` and not `dict`. Any other statement assigns nothing here.
    """
    words = [piece.code for piece in line.pieces]
    depth, last = 0, -1
    for at, word in enumerate(words):
        if word in ("(", "[", "{"):
            depth += 1
        elif word in (")", "]", "}"):
            depth -= 1
        elif depth == 0 and word in _ASSIGNS:
            last = at
    if last < 0:
        return frozenset()
    bound: set[str] = set()
    depth = 0
    for at, word in enumerate(words[:last]):
        if word in ("(", "[", "{"):
            depth += 1
        elif word in (")", "]", "}"):
            depth -= 1
        elif depth == 0 and word == ":":
            break
        elif depth == 0 and word.isidentifier() and not keyword.iskeyword(word):
            if at == 0 or words[at - 1] != ".":
                bound.add(word)
    return frozenset(bound)


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
                f"`{entry}` names a test this branch neither added nor changed, nor any "
                "table, fixture or helper in its file that it uses, so it passed before "
                "the work and shows nothing about it"
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


def true_before_the_work(command: str, root: Path, own: Path) -> str:
    """Why an open item's search is true before its work, as a predicate for "its `verify:`".

    The result is empty where the search is not yet true, or `command` is not
    a search. `own` is the file of the item that keeps the search: that file
    holds the search itself, so a search of it is always true. A search that
    is true before the work shows nothing when the item closes.
    """
    search = read_text_search(command)
    if isinstance(search, str):
        return ""
    if any(own.resolve() == path.resolve() for glob in search.paths for path in root.glob(glob)):
        return (
            "reads the item's own file, which holds the search itself, so the search "
            "shows nothing about the work"
        )
    if search_faults(command, root):
        return ""
    return (
        "is already true on this tree, so it shows nothing about the work. An open "
        "item keeps a search that its work makes true"
    )


#: A bold label that carries a date and opens a paragraph, such as
#: `**Answered 2026-11-20.**` or `**Counted 2026-11-21**`. The label may run
#: on past the date, and the bold may close anywhere on the line.
# regex: a search through an item brief's free prose for a line that opens with
# bold text holding a date. `docket.markdown` reads blocks and not the bold
# inside a line, and the date may stand anywhere in the label.
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


def keeps_its_command(item: Item) -> bool:
    """Whether `item` may keep a `verify:` that is not a search for fixed text.

    A release item keeps the command it has, because `bin/docket release`
    writes the version and the notes. An item that records `not-delegable:`
    has said why no search can show its work. Nothing reads either command.
    """
    return item.resource == RELEASE_TRAIN or bool(item.not_delegable)


def closing_faults(item: Item, root: Path, fork: ForkTexts) -> tuple[list[str], list[str]]:
    """What is wrong with what `item` records to show its work, and what could not be read."""
    faults, unread = test_faults(item.tests, _tree_text(root), fork)
    if item.verify and not keeps_its_command(item):
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
