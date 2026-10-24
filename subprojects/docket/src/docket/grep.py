"""What a `verify:` command's `grep` clause reads: its words, read once, and a phrase it cannot see.

Two questions are asked of a `grep` clause, and both read it here. Whether it
is one of the shapes a `verify:` command may take (`PL-1P5V`) is
`checks.verify_shape_refusal`'s; whether its exit status can mean what its
author meant is the replay's and `docket verify`'s. `read_grep` is the one
reading of its words - which are options, which is the pattern and which are
the files - so the two cannot disagree about any of them.

The second question has one case decidable from the tree (`PL-RR1N`). `grep`
reads one line at a time, so a phrase the document wraps across a line break -
a paragraph's soft break (CommonMark 0.31.2 § 6.7), a comment carried onto the
next line - is on no line it reads. A `grep -q` for that phrase then fails
whether or not the work is done, which reads as work not started, and a
`! grep -q` passes while the phrase is still there, which reads as a removal
made. `PL-FG9D`'s finished work read as absent the first way on 2026-09-20,
and `PL-Z4WL`'s `! grep -q 'has no planned-milestone line of its'` passed the
second way at its own close-out on 2026-09-15, its fix having quoted the
phrase across two lines of `ROADMAP.md`. `wrapped` finds the case: a phrase on
no line of any file the clause reads, but in one of them once each statement's
lines are read as one, the way a reader reads them.

Standard library only, and it imports only `lines`, `markdown` and `shell`.
"""

from __future__ import annotations

import fnmatch
import glob
import os
import re
from bisect import bisect_right
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

from . import markdown
from .lines import file_text, split_lines
from .shell import Word, shell_words

#: The `grep` options an admitted clause may carry. Each changes only *what*
#: matches - a fixed string, an extended pattern, a whole tree, either case -
#: and `q` is required, so the clause answers with its exit status and prints
#: nothing into the replay. The rest change what the status means: `-v` passes
#: on nearly any file, `-c`, `-l`, `-L` and `-o` report something other than
#: whether the line is there, and `-e` and `-f` put the pattern where this does
#: not read it.
GREP_FLAGS = frozenset("qFEri")

#: The characters a basic and an extended pattern give a meaning of their own
#: (POSIX.1-2017 XBD 9.3 and 9.4). `wrapped` reads a pattern holding none of
#: them but `.` - which matches any character but a line end, and so cannot
#: carry a match from one line to the next - and leaves every other one alone.
_BASIC_SPECIAL = frozenset(".[]*^$\\")
_EXTENDED_SPECIAL = _BASIC_SPECIAL | frozenset("+?(){}|")

#: A comment's or a quotation's marker at a line's start, outside Markdown,
#: which holds a carried-on statement rather than belonging to its words: `#`
#: with the `:` Sphinx gives an attribute's comment, `//`, and `>`.
_COMMENT_MARKER = re.compile(r"#+:?|//+|>")


@dataclass(frozen=True)
class GrepClause:
    """One admitted `grep -q` clause, as `grep` reads it."""

    #: Whether `!` stands ahead of it.
    negated: bool
    #: The single-letter options, `q` always among them.
    letters: frozenset[str]
    #: Each `--include=` (true) or `--exclude=` (false) glob, in the order given,
    #: since the last one to match a file decides it.
    filters: tuple[tuple[bool, str], ...]
    pattern: str
    #: Each file operand as the shell hands it over, a glob still unexpanded.
    paths: tuple[Word, ...]


def read_grep(words: Sequence[Word]) -> GrepClause | str:
    """The `grep -q` or `! grep -q` clause `words` spell, or why they spell none admitted.

    The reason is a predicate for the sentence "its `verify:` ...", naming the
    first thing found that no admitted shape uses, as `checks._grep_refusal`
    reports it.
    """
    clause = " ".join(word.text for word in words)
    negated = False
    if words[0].bang:
        if words[0].text != "!" or words[0].quoted or len(words) < 2:
            return f"carries `!` in `{clause}`, where only `! grep` admits one"
        words = words[1:]
        negated = True
    if any(word.bang for word in words):
        return f"carries `!` in `{clause}`, where only `! grep` admits one"
    if words[0].text != "grep":
        return f"runs `{clause}`, which is neither a `grep` clause nor the whole-suite coverage run"
    letters: set[str] = set()
    filters: list[tuple[bool, str]] = []
    index = 1
    while index < len(words) and words[index].text.startswith("-"):
        option = words[index].text
        if words[index].quoted and not option.startswith(("--include=", "--exclude=")):
            return f"gives a pattern grep reads as an option: `{option}` wants `--` ahead of it"
        index += 1
        if option == "--":
            break
        if option.startswith(("--include=", "--exclude=")) and option.split("=", 1)[1]:
            filters.append((option.startswith("--include="), option.split("=", 1)[1]))
            continue
        refused = (
            option
            if option.startswith("--")
            else next((f"-{letter}" for letter in option[1:] if letter not in GREP_FLAGS), "")
        )
        if refused or option == "-":
            return f"gives `grep` the option `{refused or option}`, which no admitted shape uses"
        letters.update(option[1:])
    if "q" not in letters:
        return f"runs `{clause}` without `-q`, so it answers in output as well as status"
    if {"F", "E"} <= letters:
        return "gives `grep` both `-F` and `-E`, which it refuses with exit 2"
    if filters and "r" not in letters:
        return "gives `--include` or `--exclude` to a `grep` that does not recurse"
    operands = words[index:]
    if len(operands) < 2:
        return f"runs `{clause}`, which names no file to read"
    pattern, paths = operands[0], operands[1:]
    if pattern.globbed:
        return f"leaves the pattern in `{clause}` unquoted, where the shell may expand it"
    if not pattern.text:
        return "gives `grep` an empty pattern, which matches every line"
    for path in paths:
        if path.text.startswith("-"):
            return f"puts `{path.text}` after the pattern, where grep reads it as an option"
        if path.text.startswith("/") or ".." in path.text.split("/"):
            return f"reads `{path.text}`, which is outside the repository"
    return GrepClause(negated, frozenset(letters), tuple(filters), pattern.text, tuple(paths))


@dataclass(frozen=True)
class Wrap:
    """A `grep` clause's phrase that its file holds only across a line break (`PL-RR1N`)."""

    phrase: str
    #: Whether `!` stands ahead of the clause, which turns "cannot see it" from
    #: a failure into a pass.
    negated: bool
    #: The file holding the phrase, as the clause reaches it from the root.
    path: str
    #: The first and last line the phrase spans, counted from 1.
    first: int
    last: int

    def describe(self) -> str:
        """What the clause does about the phrase, as a clause of a sentence."""
        lines = f"lines {self.first}-{self.last}"
        if self.negated:
            return (
                f"`{self.phrase}` is still in {self.path}, across {lines}, so its `! grep` "
                "passes while the phrase is there"
            )
        return (
            f"`{self.phrase}` is in {self.path} only across {lines}, so its `grep` "
            "fails whether or not the work is done"
        )


@dataclass(frozen=True)
class _Reading:
    """One file as `wrapped` reads it: as `grep` does, and a statement to a line."""

    #: The file's text, which `grep` searches a line at a time.
    text: str
    #: Each statement of two or more lines, its lines' words joined by one
    #: space, and a line end between two statements so no match spans them.
    joined: str
    #: Where each statement starts in `joined`, and the index of its first line.
    starts: tuple[int, ...]
    firsts: tuple[int, ...]
    #: Where each line of each statement starts within it.
    offsets: tuple[tuple[int, ...], ...]


#: A file read once per run, by its path from the root: `None` where it could
#: not be read, which holds no line `grep` could read either.
Cache: TypeAlias = dict[str, _Reading | None]


def wrapped(root: Path, command: str, cache: Cache | None = None) -> tuple[Wrap, ...]:
    """Each `grep` clause of `command` whose phrase its files hold only across a line break.

    A clause is read when its pattern is a phrase: a fixed string (`-F`), or a
    pattern holding no character a pattern gives a meaning to but `.`, with a
    space for a line break to fall on. `-i` is read as `grep` reads it. A
    regular expression is left alone, since what it matches across a line
    break is a different question, as is a clause `read_grep` refuses.

    It is found when no line of any file the clause reads holds the phrase -
    so the clause fails, or under `!` passes - and one of them holds it once
    each statement is read as one line: a Markdown paragraph with its soft
    breaks and lazy continuations, its list items' and block quotes' markers
    read past, through `docket.markdown`, and in any other file a run of
    lines that share a comment marker, or carry none. A fence is a literal and
    is not joined. The files are the ones `grep` would read: globs expanded as
    the shell expands them, and with `-r` each directory walked as `grep`
    walks it, `--include` and `--exclude` read on each file's base name and
    symbolic links below the command line passed by.

    `cache`, where given, holds each file read across calls, so a run asking
    about every open item reads each file once.
    """
    reading = shell_words(command)
    if reading.refusal is not None:
        return ()
    store: Cache = {} if cache is None else cache
    found: list[Wrap] = []
    for clause in reading.clauses:
        words = [token for token in clause.tokens if isinstance(token, Word)]
        parsed = read_grep(words) if words else "no words"
        if isinstance(parsed, str):
            continue
        phrase = _phrase(parsed)
        if phrase is None:
            continue
        files = [(name, _read(root, name, store)) for name in _files(root, parsed)]
        readings = [(name, read) for name, read in files if read is not None]
        if any(phrase.search(read.text) for _, read in readings):
            continue
        for name, read in readings:
            match = phrase.search(read.joined)
            if match is None:
                continue
            statement = bisect_right(read.starts, match.start()) - 1
            offsets = read.offsets[statement]
            within = match.start() - read.starts[statement]
            first = bisect_right(offsets, within) - 1
            last = bisect_right(offsets, within + len(match.group()) - 1) - 1
            line = read.firsts[statement]
            found.append(
                Wrap(parsed.pattern, parsed.negated, name, line + first + 1, line + last + 1)
            )
            break
    return tuple(found)


def _phrase(clause: GrepClause) -> re.Pattern[str] | None:
    """The clause's pattern as a phrase a line break could split, or `None` where it is not one."""
    fixed = "F" in clause.letters
    special = _EXTENDED_SPECIAL if "E" in clause.letters else _BASIC_SPECIAL
    if not fixed and any(character in special - {"."} for character in clause.pattern):
        return None
    if not any(character.isspace() for character in clause.pattern):
        return None
    body = "".join(
        "[^\n]" if character == "." and not fixed else re.escape(character)
        for character in clause.pattern
    )
    return re.compile(body, re.IGNORECASE if "i" in clause.letters else 0)


def _files(root: Path, clause: GrepClause) -> list[str]:
    """The files `clause` reads, by their paths from `root`, in the order `grep` reads them.

    A glob is expanded as bash expands it, in order, and handed over as written
    where it matches nothing - a file `grep` cannot open, so it reads nothing.
    """
    found: list[str] = []
    for word in clause.paths:
        names = sorted(glob.glob(word.text, root_dir=root)) if word.globbed else [word.text]
        for name in names:
            path = root / name
            if path.is_dir():
                if "r" in clause.letters:
                    found.extend(_walk(root, path, clause.filters))
            elif path.is_file():
                found.append(name)
    return found


def _walk(root: Path, directory: Path, filters: tuple[tuple[bool, str], ...]) -> Iterator[str]:
    """Each file `grep -r` reads under `directory`, by its path from `root`, in a fixed order.

    GNU grep 3.11's rules: a symbolic link below the command line is not
    followed, the last `--include` or `--exclude` to match a file's base name
    decides it, and one no filter matches is read unless the first filter is
    an `--include`.

    **The disk, and not `vcs.tracked_files`, on purpose** (`PL-J4YY`). `grep -r`
    reads an untracked file, an ignored one and another checkout beneath the
    directory alike, and this is the model of that command: read from the
    tracked list instead, `wrapped` would explain a `grep` reading other files
    than the one whose exit status it is explaining. So it is a home of its own
    in `tools/fact_home_check.py`'s `HOMES`, rather than a second reader of
    which files the repository holds.
    """
    for parent, directories, names in os.walk(directory):
        directories.sort()
        for name in sorted(names):
            path = Path(parent) / name
            if path.is_symlink():
                continue
            decided = [
                include for include, pattern in filters if fnmatch.fnmatchcase(name, pattern)
            ]
            if decided[-1] if decided else not (filters and filters[0][0]):
                yield path.relative_to(root).as_posix()


def _read(root: Path, name: str, cache: Cache) -> _Reading | None:
    """`name` as `grep` reads it and as a reader reads it, or `None` where it cannot be read.

    Bytes that are not UTF-8 are kept rather than refused, as `grep -q` keeps
    reading a file it takes for binary, so a phrase in the text around them is
    found where `grep` finds it.
    """
    if name in cache:
        return cache[name]
    try:
        raw = (root / name).read_bytes()
    except OSError:
        cache[name] = None
        return None
    text = file_text(raw.decode("utf-8", "surrogateescape"))
    lines = split_lines(text)
    statements = _paragraphs(lines) if Path(name).suffix == ".md" else _runs(lines)
    joined: list[str] = []
    starts: list[int] = []
    firsts: list[int] = []
    offsets: list[tuple[int, ...]] = []
    at = 0
    for first, words in statements:
        starts.append(at)
        firsts.append(first)
        offsets.append(tuple(_offsets(words)))
        sentence = " ".join(words)
        joined.append(sentence)
        at += len(sentence) + 1
    read = _Reading(text, "\n".join(joined), tuple(starts), tuple(firsts), tuple(offsets))
    cache[name] = read
    return read


def _offsets(words: Sequence[str]) -> Iterator[int]:
    """Where each line's words start once a statement's lines are joined by one space."""
    at = 0
    for line in words:
        yield at
        at += len(line) + 1


def _paragraphs(lines: Sequence[str]) -> Iterator[tuple[int, list[str]]]:
    """Each Markdown statement of two or more lines: its first line, and each line's words.

    `markdown.statement_lines` says where each statement starts and ends, and
    `markdown.unmarked` blanks the block quote's `>` and the list item's marker
    a line's words sit behind.
    """
    words = markdown.unmarked(lines)
    for start, end in markdown.statement_lines(lines):
        if end - start > 1:
            yield start, [words[index].strip() for index in range(start, end)]


def _runs(lines: Sequence[str]) -> Iterator[tuple[int, list[str]]]:
    """Each run of two or more lines outside Markdown that a blank line or a new marker ends.

    A line's words are what follows its indent and its comment or quotation
    marker, so a comment carried onto the next line joins it; a line holding
    only a marker is blank. Code and a docstring's lines carry no marker and
    join each other, which only a phrase written across them could match.
    """
    run: list[str] = []
    first, kind = 0, ""
    for index, line in enumerate([*lines, ""]):
        text = line.strip()
        marker = _COMMENT_MARKER.match(text)
        if marker:
            text = text[marker.end() :].strip()
        this = marker.group()[0] if marker else ""
        if not text or (run and this != kind):
            if len(run) > 1:
                yield first, run
            run = []
        if text:
            if not run:
                first, kind = index, this
            run.append(text)
