"""Proving that delegated work stayed inside the commission it was given.

A passing check proves the check passed. It does not prove the work is
correct, because a check can be satisfied by the wrong route: weakening an
assertion, adding a suppression, editing the gate itself, or doing the item
correctly and changing three unrelated files on the way past. Every one of
those produces a green build.

So this module verifies two things that together are worth more than either
alone - that the item's own command passes, and that the diff which produced
it stayed inside the paths the item declared. The second is the half that
makes review cheap: without it, accepting delegated work means reading the
diff, which is the cost delegation exists to avoid.

What it deliberately does not do is decide whether the work is *right*. A new
test can exercise the intended line and assert the wrong value, and no check
here can tell. The report says so in as many words rather than presenting a
clean result as a guarantee, because a tool that implied otherwise would be
worse than no tool.

Commands are shelled out, never imported. This package is standard-library
only and runs without a virtualenv; the commands it runs belong to the
project, and that separation is what keeps a bare checkout able to use it.
"""

from __future__ import annotations

import ast
import configparser
import json
import re
import shlex
import subprocess
import tomllib
import warnings
from collections import Counter
from collections.abc import Callable, Collection, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TypeVar

from . import done, vcs
from .config import Config
from .lines import ENCODING, file_text, split_lines
from .model import (
    FrontMatterDeclines,
    Item,
    _front_matter_pairs,
    is_under,
    parse_front_matter,
    pr_number,
    recurrence_entry_reads,
    split_list,
)
from .python import (
    SOURCE_SUFFIXES,
    UNPARSABLE,
    UNTOKENIZABLE,
    LogicalLine,
    places,
    read_logical_lines,
    refusal,
)
from .release import CODE_SPAN_PATTERN
from .vcs import RECORDS

# Suppressions matched as text. `noqa` is deliberately absent: a project whose
# ruff configuration does not enable a rule carries `noqa` directives that
# suppress nothing, so flagging the text would fire on inert directives and
# still miss one written against a rule that *is* enabled. Whether a `noqa`
# matters is a question for the linter's own `RUF100`, not for a substring
# search, and answering it here would be guessing at the judgment half.
#
# `# type: ignore` was dropped for a measured form of that same argument
# (`PL-G21K`). Replayed over `main`'s 1,004 non-merge commits - the ones a
# diff replay reads, out of 1,121 - it is the only entry that has ever matched
# a real directive: 56 of them, every one carrying an explicit error code, and
# not one a disabled test, which is the hazard this check names. The other
# four matched a real directive zero times in that history.
#
# Whether an ignore is load-bearing is the only question worth asking about
# one; a substring search cannot answer it, and the tool that can already
# does. `strict = true` enables `warn_unused_ignores` over `[tool.mypy]
# files`, which covered 11 of the 56, and `tools/type_ignore_check.py` runs the
# same setting over the two test trees `files` excludes, which covers the
# other 45 (`PL-J5NN`). What no tool polices is a *live* ignore added to
# silence an error the work itself introduced - and this check did not police
# it either, having flagged all 56 alike when 56 were legitimate.
#
# The four that remained cost nothing at that zero rate, so they stayed: a
# count of zero cannot tell deterrence from absence, which is why retiring the
# check outright was refused. What that zero did not mean was coverage of the
# hazard. `@pytest.mark.skip` and `@pytest.mark.skipif` - the two commonest
# ways a pytest test is disabled - matched neither `@skip`, whose `@` must sit
# against the name, nor `pytest.skip`, whose halves `.mark.` separates, so the
# check reported `none` with a disabled test in the diff (`PL-5B88`).
#
# `mark.skip` closes that, written without its `pytest.` so that `@mark.skip`
# after `from pytest import mark` is read too. `unittest.skip` reads the standard library's
# decorators, `skipIf` and `skipUnless` included. A widening owes the count a
# narrowing does, in the other direction. Replayed on 2026-09-22 over `main`'s
# 1,115 non-merge commits, of 1,232, the list before these two matched no
# added line at all, and the two add exactly one: the `@pytest.mark.skipif`
# that `tests/unit/test_stop_hook_patch.py` puts on a test needing `bash`. It
# is real - an environment guard rather than a test silenced to reach green,
# which is a reviewer's call and is now put in front of one. No prose line
# matched in any suffix the check reads, `.toml`, `.cfg` and `.ini` included.
#
# The last six finish the family, drawn from the frameworks' documented ways to
# skip, fail or ignore a test (`PL-DNZ0`): `importorskip`, which skips a module
# whose import fails; `expectedFailure`, unittest's `xfail`; `skipTest`, its
# imperative skip; `SkipTest`, the exception both frameworks skip on when it is
# raised; and the two ways a `conftest.py` drops a file from collection - the
# `collect_ignore` list, `collect_ignore_glob` included, and the
# `pytest_ignore_collect` hook, whose words run the other way. Replayed on
# 2026-09-25 over `main`'s 1,237 non-merge commits, of 1,354, the six match no
# added line in any suffix the check reads: the names stood only on three
# comment lines above this list, which `strip_non_code` blanks, and the list
# before them still matches the one `bash` guard. `importorskip` is the one with
# a common legitimate use, an optional dependency, and is put in front of a
# reviewer as that guard is. A deselection in `addopts` is configuration: in
# `pyproject.toml`, one of `gate_paths`' defaults, the gate check reads it, and
# in a `.cfg` or `.ini` file nothing does.
#
# The hook is read as its definition, `def pytest_ignore_collect`, because only
# a definition in a `conftest.py` drops a file. A test that calls the hook to
# check it drops nothing, and `PL-GQCQ`'s close-out was refused on three such
# calls, which `--self` cannot waive (`PL-3G9M`). Replayed on 2026-10-25 over
# `main`'s 2,005 non-merge commits, of 2,122, the bare name matched four added
# lines, all on `PL-GQCQ`'s branch, and the definition matches one of them, the
# hook it really added. The space in the entry matches any run of whitespace.
SUPPRESSIONS = (
    "typing.no_type_check",
    "xfail",
    "pytest.skip",
    "@skip",
    "mark.skip",
    "unittest.skip",
    "importorskip",
    "expectedFailure",
    "skipTest",
    "SkipTest",
    "collect_ignore",
    "def pytest_ignore_collect",
)

#: The same list as something a line can be matched against, anchored on the
#: left where the entry begins with a word character. Every entry names a
#: *token*, and a bare substring search finds one inside a longer word:
#: `xfail` sits inside pytest's own `--maxfail`, so a diff line listing that
#: option read as a suppression and rejected correct work (`PL-VHVJ`). The
#: anchor is conditional because `@skip` opens on a character that is not a
#: word character - `\b` before one of those asserts the opposite of what is
#: wanted and would match only where a word character precedes it.
#:
#: Left only. The right-hand side is deliberately open, so `@skip` still finds
#: `@skipif`, `mark.skip` finds `mark.skipif`, `unittest.skip` finds `skipIf`
#: and `skipUnless`, and `collect_ignore` finds `collect_ignore_glob`, each of
#: which is the thing this looks for rather than a collision with it.
# regex: one search for any of the listed tokens, each with a word boundary on
# its left only where it opens with a word character. `in` cannot test that
# boundary.
_SUPPRESSION_RE = re.compile(
    "|".join(
        (r"\b" if text[0].isalnum() or text[0] == "_" else "")
        + re.escape(text).replace(r"\ ", r"\s+")
        for text in SUPPRESSIONS
    )
)

#: Where a suppression can genuinely live, for `no suppression added`. A
#: suppression is written in Python and also *configured*. `xfail_strict =
#: false` under `[tool.pytest.ini_options]` turns every expected failure back
#: into a pass, and a `.pyi` stub carries a file-level ignore directive,
#: neither of which changes a line of `.py`. So this list is `.py` plus the
#: files that configure a run.
#:
#: Counted before it was written, because this narrows a check whose safe
#: direction is reporting: over 1,109 commits of this repository, the added
#: lines `_SUPPRESSION_RE` matches are 69 in `.py` and 41 in `.md`, and **no
#: other suffix carries one at all**. So the tuple reports every match the
#: history has ever held, and what it stops reading is 41 lines of prose -
#: a release note, an item brief, or the `ROADMAP.md` version row that
#: REJECTed every release cut (`PL-5MFL`, `PL-BHBZ`).
SUPPRESSION_BEARING_SUFFIXES = (*SOURCE_SUFFIXES, ".toml", ".cfg", ".ini")


#: The suffixes whose non-code spans are stripped below, which are Python
#: source's own, `python.SOURCE_SUFFIXES` (`PL-H716`). They are narrower than
#: `SUPPRESSION_BEARING_SUFFIXES`, and deliberately so. In a `.cfg` or `.ini`
#: a quote is an ordinary character in a value and an inline `#` is part of
#: that value under `configparser`'s defaults, so the same strip would delete
#: configuration rather than prose. Counted rather than assumed: across 1,004
#: non-merge commits every line the pattern has ever matched is `.py`, and no
#: `.toml`, `.cfg` or `.ini` line has matched it in either direction - so a
#: rule for them would be the widest one the hazard could motivate rather than
#: the narrowest that removes it.
QUOTING_SUFFIXES = SOURCE_SUFFIXES

#: The spans of a Python line that carry text rather than code. Alternation is
#: ordered and the scan runs left to right, so a `#` inside a string is taken
#: as part of the string and a quote inside a comment as part of the comment;
#: neither can open the other.
#:
#: The backtick alternative is not redundant with the string one, which is the
#: detail that makes this work on the file it was written for. Python 3 has no
#: backtick syntax, so a backtick is always inside a string or a comment
#: already - but a diff hands this *one line* of a multi-line docstring, whose
#: delimiters are on other lines, so the string alternative cannot see it and
#: the markup is the only evidence left on the line. It is docket's one reading
#: of a span, `release.CODE_SPAN_PATTERN`, so a reST-style ``literal`` is
#: blanked whole rather than read as two empty spans around a bare token
#: (`PL-9L39`). It steps over a backslash escape and a backtick run no closer
#: matches as CommonMark's scan does, and blanks them with the spans (`PL-T3GW`).
#:
#: **The comment alternative is safe only because `SUPPRESSIONS` now holds no
#: comment-form marker**, and that coupling is why `PL-G21K`'s two halves were
#: worked together. `PL-STC4` called this half undecidable, correctly, while
#: `# type: ignore` was on the list: ignoring comments would have deleted the
#: only marker that ever fired. `test_no_suppression_marker_is_comment_shaped`
#: fails if one is put back.
#:
#: An unterminated span - the opening line of a wrapped string, which is what
#: a diff supplies - matches nothing and is left whole, so the line is
#: reported rather than guessed at.
# regex: a lexer's table of the string, comment and code-span tokens on one
# line of a diff. `tokenize` refuses a line that opens a string it does not
# close, which a diff supplies, so it cannot read these lines.
NON_CODE_RE = re.compile(
    r'"""(?:[^"\\]|\\.|"(?!""))*"""'  # a triple-quoted span opening and closing on one line
    r"|'''(?:[^'\\]|\\.|'(?!''))*'''"
    r'|"(?:[^"\\\n]|\\.)*"'
    r"|'(?:[^'\\\n]|\\.)*'"
    rf"|{CODE_SPAN_PATTERN}"  # a backtick span: prose markup, and never Python
    r"|#.*"  # a comment, which the alternatives above keep out of a string
)


def strip_non_code(line: str) -> str:
    """`line` with its quoted, backtick and comment spans blanked out.

    Blanked rather than deleted, so that removing a span cannot join what sits
    either side of it into one token: `mark("xfail")` becomes `mark( )` and
    never `mark()`.
    """
    return NON_CODE_RE.sub(" ", line)


def is_suppression_line(path: str, line: str) -> bool:
    """Whether an added line could suppress anything, for `no suppression added`.

    The check used to ask the line alone, so a line *about* a suppression read
    as one. That is the same defect `PL-7TYC` removed from the assertion check
    this module once ran, and it was left standing here, on a check `--self`
    may never relax - which makes it the check least able to afford a false
    positive, since a `REJECT` on it says in the tool's strongest terms that
    the branch weakened a test (`PL-BHBZ`).

    A release cut is what met it every time. `ROADMAP.md`'s version table
    narrates the defects each release fixed, so its rows quote the tokens
    `SUPPRESSIONS` holds; dropping the `current baseline` mark from the
    departing row edits one cell, and a whole-line diff re-adds the whole row
    (`PL-5MFL`).

    Prose *inside* a file Python executes is the half no suffix list can
    reach, and this module is where it bites hardest: a file that names the
    tokens it matches trips its own check, so the close-out that added the
    suffix list `REJECT`ed on six of its own docstring lines and could not be
    cleared from inside its branch (`PL-0KQP`, `PL-STC4`). `strip_non_code`
    removes the three carriers that were counted - a quoted span, a backtick
    span, a comment - and across 1,004 non-merge commits those three hold every
    one of the 19 non-directive lines the pattern has ever matched, while
    matching no line it did not match before. Replayed on `#783` itself, the
    six lines it `REJECT`ed on go to none.

    An unreadable diff header yields `""`, which stays on the reporting side:
    where the file cannot be
    identified, the line is printed rather than guessed at - and unstripped
    for the same reason, since the strip is what a known Python file earns.

    **A line, so a Python file is no longer read with it** (`PL-CFWP`). A
    marker split by a backslash or inside brackets - `@pytest.mark.\\` over
    `skip(...)` - holds no entry on either of its lines, so the check read
    `none`. A Python file is read as logical lines instead
    (`added_suppressions`), and a configuration file as the values its
    format's reader gives, since a TOML array, a TOML multi-line string and a
    `configparser` value all continue across lines too (`PL-PNZB`). This
    reads what neither reader could: a file some version of which the
    tokenizer or its format's reader refuses, which the page names
    (`PL-TC2D`).
    """
    if path and not path.endswith(SUPPRESSION_BEARING_SUFFIXES):
        return False
    if path.endswith(QUOTING_SUFFIXES):
        line = strip_non_code(line)
    return bool(_SUPPRESSION_RE.search(line))


def is_suppression_statement(line: LogicalLine) -> bool:
    """Whether a logical line's code holds an entry of `SUPPRESSIONS`.

    Its strings are already blanked and its comments are not in it, which are
    the three spans `strip_non_code` removes from a line - here read by the
    tokenizer rather than guessed at from one line, where a string opened on
    another line could not be seen.
    """
    return bool(_SUPPRESSION_RE.search(line.code))


def _statements(value: object, path: str = "") -> Iterator[str]:
    """Each line of a configuration value under its dotted key, `key.path = line`.

    A table's keys extend the path and an array's elements keep it, so an
    array re-wrapped is the same statements and an element moved from one
    key's array to another's is a different one (`PL-PNZB`). A string is a
    statement per line, each stripped, since no entry of `SUPPRESSIONS` spans
    a line break or ends in whitespace; what the reader made of a line-ending
    backslash or an indented continuation is what the pattern reads. The key
    stays in each statement because it can be the suppression itself
    (`xfail_strict`), so a key whose value is empty is still one.
    """
    if isinstance(value, dict) and value:
        for key, held in value.items():
            yield from _statements(held, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list) and value:
        for held in value:
            yield from _statements(held, path)
    elif path:
        text = ("true" if value else "false") if isinstance(value, bool) else str(value)
        lines = [line for line in (line.strip() for line in split_lines(text)) if line]
        for line in lines or [""]:
            yield f"{path} = {line}".rstrip()


def _toml_statements(text: str) -> tuple[str, ...]:
    """A TOML file's statements, as `tomllib` reads it."""
    return tuple(_statements(tomllib.loads(text)))


def _ini_statements(text: str) -> tuple[str, ...]:
    """A `.cfg` or `.ini` file's statements, as `configparser` reads it.

    Its defaults but two. No interpolation, so a value is the text the file
    holds. And no defaults section: `default_section` is given a name no
    header can spell, since `[]` is no header, so a `[DEFAULT]` section's keys
    are read as its own rather than copied into every section beside it.
    """
    parser = configparser.ConfigParser(interpolation=None, default_section="")
    parser.read_string(text)
    sections = {name: dict(parser.items(name, raw=True)) for name in parser.sections()}
    return tuple(_statements(sections))


#: The configuration files among `SUPPRESSION_BEARING_SUFFIXES`, each read as
#: the values its format's own reader gives rather than as diff lines
#: (`PL-PNZB`). TOML continues an array across lines and trims a line-ending
#: backslash inside a multi-line string, and `configparser` takes an indented
#: line for more of the value above it, so in both a physical line can be a
#: fragment of a value.
#:
#: Each suffix maps to its reader's name as the page prints it, what the reader
#: makes of a copy, and what it raises in refusing one. `UnicodeDecodeError`
#: is a `ValueError`, and a TOML array nested a few hundred deep exhausts the
#: stack in `tomllib` itself, measured under 3.13 and 3.14.
CONFIGURATION_READERS: dict[
    str, tuple[str, Callable[[str], tuple[str, ...]], tuple[type[Exception], ...]]
] = {
    ".toml": ("tomllib", _toml_statements, (ValueError, RecursionError)),
    ".cfg": ("configparser", _ini_statements, (configparser.Error, ValueError)),
    ".ini": ("configparser", _ini_statements, (configparser.Error, ValueError)),
}


def _parse(source: str) -> ast.Module:
    with warnings.catch_warnings():
        # Compiling warns on an invalid escape sequence. That is the file's
        # linter's to report, and a verify report is the wrong page for it.
        warnings.simplefilter("ignore")
        return ast.parse(source)


def _parses(source: str) -> bool:
    """`True`, or one of `UNPARSABLE` raised: whether a page must name the file."""
    _parse(source)
    return True


def _short(spec: str) -> str:
    """The revision half of a `<rev>:<path>` spec, a full object id abbreviated."""
    revision = spec.partition(":")[0]
    # regex: a full object id is a token with a fixed shape, 40 to 64 hexadecimal digits.
    return revision[:12] if re.fullmatch(r"[0-9a-f]{40,64}", revision) else revision


def _blobs(root: Path, specs: Collection[str]) -> dict[str, tuple[str, bytes] | None] | None:
    """Each `<rev>:<path>` as git holds it - its object id and bytes - or `None`
    where that revision holds no file there; `None` overall where git could not
    be asked, which the caller reports rather than reading as "no file".

    One `git cat-file --batch` for the lot, where a `git show` each would be a
    process per version of every file an item touches - `vcs.GitRunner`'s blob
    batch removed the same fan-out from session start (`PL-0J9K`).
    """
    ordered = sorted(specs)
    if not ordered:
        return {}
    if any("\n" in spec for spec in ordered):  # the protocol's own delimiter
        return None
    try:
        # Encoded as `vcs.GitRunner._blob` encodes a spec, by the codec git's
        # output is decoded with, so a path read from git names the same bytes.
        asked = "".join(f"{spec}\n" for spec in ordered).encode(ENCODING)
    except UnicodeEncodeError:
        return None
    call = vcs.call_git(["cat-file", "--batch"], root, stdin=asked, timeout=vcs.LONG_GIT_TIMEOUT)
    if call.code != 0:
        return None
    out, at = call.stdout, 0
    found: dict[str, tuple[str, bytes] | None] = {}
    for spec in ordered:
        end = out.find(b"\n", at)
        if end < 0:
            return None
        try:
            header = vcs.batch_header(out[at:end])
        except ValueError:
            return None
        at = end + 1
        if header is None:
            found[spec] = None
            continue
        oid, kind, size = header
        body = out[at : at + size]
        at += size + 1  # git ends every object with a newline
        # A tree or a submodule at the path is not a file a suppression lives in.
        found[spec] = (oid, body) if kind == "blob" else None
    return found


@dataclass(frozen=True)
class _FileStep:
    """One commit's change to one file, as the fold reads it."""

    key: str
    #: The file in each parent, as a blob spec, or "" where that parent has none.
    before: tuple[str, ...]
    #: The file after the commit, or "" where the commit deleted it.
    after: str


def _changed_python(
    listing: str, statuses: bool, suffixes: tuple[str, ...]
) -> list[tuple[str, str]]:
    """`(old, new)` for each file `suffixes` names in a `-z` listing, "" for a side it does not."""
    fields = listing.split("\0")
    pairs: list[tuple[str, str]] = []
    at = 0
    while at < len(fields):
        if not fields[at]:
            at += 1
            continue
        if not statuses:
            old = new = fields[at]
            at += 1
        else:
            status = fields[at]
            if status[:1] in "RC":  # a rename or copy names both sides
                old, new = fields[at + 1 : at + 3] if at + 2 < len(fields) else ("", "")
                old = "" if status[:1] == "C" else old
                at += 3
            else:
                path = fields[at + 1] if at + 1 < len(fields) else ""
                old = "" if status[:1] == "A" else path
                new = "" if status[:1] == "D" else path
                at += 2
        pair = (old if old.endswith(suffixes) else "", new if new.endswith(suffixes) else "")
        if any(pair):
            pairs.append(pair)
    return pairs


def _file_steps(
    root: Path, base: str, commits: tuple[str, ...], suffixes: tuple[str, ...]
) -> tuple[list[_FileStep], dict[str, str], str]:
    """The item's changes to the files `suffixes` names, oldest first, and their keys.

    Returns the steps, every path they name mapped to its file's key - the
    name the file had before the item's first commit touched it - and a
    reason where the commits could not be read at all.

    A merge commit is read against every parent at once, as `git show` reads
    one: what it removed is what every parent held and it does not, and what
    it added is what no parent held. Against its first parent alone, merging
    the base in would charge the item with every removal the base had taken
    since the branch forked.
    """
    if commits:
        try:
            listing = _git(["show", "-s", "--format=%H %P", *commits], root)
        except GitUnanswered:
            return [], {}, f"the parents of {len(commits)} commit(s) could not be read"
        parents_of = {
            fields[0]: tuple(fields[1:])
            for fields in (line.split() for line in split_lines(listing))
            if fields
        }
        revisions = [(commit, parents_of.get(commit, ())) for commit in reversed(commits)]
    else:
        fork = vcs.call_git(["merge-base", base, "HEAD"], root).answer
        if not fork.strip():
            return [], {}, f"{base} and HEAD share no commit to compare from"
        revisions = [("HEAD", (fork.strip(),))]
    steps: list[_FileStep] = []
    keys: dict[str, str] = {}
    for revision, parents in revisions:
        if revision == "HEAD":
            args = ["diff", "-z", "-M", "--name-status", parents[0], "HEAD"]
        elif len(parents) > 1:
            args = ["diff-tree", "-z", "-r", "-c", "--name-only", "--no-commit-id", revision]
        else:
            args = ["diff-tree", "-z", "-r", "-M", "--name-status", "--root"]
            args += ["--no-commit-id", revision]
        # Through `_git` rather than `_run`: a `-z` path can hold a raw `\r`,
        # which `_run`'s text mode read as a line end, and `_run` mixes stderr
        # into a listing that must carry nothing but paths (`PL-0R4M`).
        try:
            listing = _git(args, root)
        except GitUnanswered:
            return [], {}, f"the files {revision[:12]} changed could not be listed"
        for old, new in _changed_python(listing, "--name-status" in args, suffixes):
            key = keys.get(old or new, old or new)
            keys.update({path: key for path in (old, new) if path})
            steps.append(
                _FileStep(
                    key,
                    tuple(f"{parent}:{old}" if old else "" for parent in parents) or ("",),
                    f"{revision}:{new}" if new else "",
                )
            )
    return steps, keys, ""


_Read = TypeVar("_Read")


def _versions(order: Sequence[str], steps: Sequence[_FileStep]) -> dict[str, list[str]]:
    """Every version of each file the steps reach, before and after each, as a blob spec.

    In the order the steps reach them, so the copy a refusal names is the
    earliest one refused, as it was when each version was read as it came.
    """
    versions: dict[str, dict[str, None]] = {key: {} for key in order}
    for step in steps:
        versions[step.key].update(dict.fromkeys(s for s in (*step.before, step.after) if s))
    return {key: list(specs) for key, specs in versions.items()}


def _read_versions(
    blobs: Mapping[str, tuple[str, bytes] | None],
    specs: Sequence[str],
    reader: Callable[[str], _Read],
    refusals: tuple[type[Exception], ...],
    read: dict[str, _Read],
) -> tuple[str, Exception] | None:
    """Read each version `specs` names with `reader`, into `read` by object id.

    The first version `reader` refuses and its error, or `None` once it has
    read them all. A file is read one way across all its versions or not at
    all, because what one reader makes of a version is not comparable with
    what another makes of the next.
    """
    for spec in specs:
        held = blobs.get(spec)
        if held is None or held[0] in read:
            continue
        try:
            read[held[0]] = reader(held[1].decode("utf-8-sig"))
        except refusals as error:
            return spec, error
    return None


def _unparsable(spec: str, error: Exception) -> str:
    """Why this interpreter could not read the copy of a file at `spec`, as the page says it.

    `UnicodeDecodeError` is a `ValueError`, so a caller catching what a parse
    raises catches it too.
    """
    if isinstance(error, UnicodeDecodeError):
        return f"its copy at {_short(spec)} is not UTF-8"
    where = f", line {error.lineno}" if isinstance(error, SyntaxError) else ""
    return (
        f"this interpreter cannot parse its copy at {_short(spec)} "
        f"({getattr(error, 'msg', None) or type(error).__name__}{where})"
    )


def _untokenizable(why: str, spec: str, error: Exception) -> str:
    """Why a file is read line by line: the parser's refusal, if any, then the tokenizer's."""
    refused = f"the tokenizer refused its copy at {_short(spec)}"
    if why:
        return f"{why}; {refused} too ({refusal(error)})"
    return f"{refused} ({refusal(error)}), though this interpreter parses every copy"


def _unread_values(reader: str, spec: str, error: Exception) -> str:
    """Why a configuration file is read line by line: its format's reader refused a copy."""
    if isinstance(error, UnicodeDecodeError):
        return f"its copy at {_short(spec)} is not UTF-8"
    return f"{reader} refused its copy at {_short(spec)} ({' '.join(str(error).split())})"


@dataclass(frozen=True)
class SuppressionAudit:
    """What the item's own commits added that could suppress a test."""

    #: Each logical line of a Python file, each statement of a configuration
    #: file, and each line of a file read line by line, that the commits added
    #: and that holds a suppression - as the report prints it, in the order
    #: the files and their lines come.
    found: tuple[str, ...] = ()
    #: Files a version of which the tokenizer, or the configuration format's
    #: own reader, refused, and why. Each is read line by line instead, and
    #: named on the page as read so.
    unparsed: tuple[tuple[str, str], ...] = ()
    #: Why nothing could be read, where that is the answer. The check refuses
    #: on it: "could not look" is not "looked, found nothing".
    unread: str = ""
    #: Python files the tokenizer read whole and a version of which this
    #: interpreter could not parse, and why: read as every other file is, and
    #: named on the page, since a newer interpreter's tokenizer can split a
    #: formatted string differently (`PL-TC2D`).
    tokenized: tuple[tuple[str, str], ...] = ()


def added_suppressions(
    root: Path, base: str, commits: tuple[str, ...], added_lines: Sequence[tuple[str, str]]
) -> SuppressionAudit:
    """The suppressions the item's own commits added, each read whole (`PL-CFWP`).

    A suppression is written in a statement, and Python continues a statement
    across physical lines, so a diff line holds a fragment of one: `@pytest.mark.\\`
    over `skip(reason="flaky")` matched on neither line, and the check said
    `none`. Each Python file is read whole - every
    version before and after each of the item's commits, through
    `_file_steps` - and split into logical lines. The lines each commit added
    and removed are folded per file across the commits, as `PL-VP40` folds
    diff lines, and `SUPPRESSIONS` is matched against the code of each one the
    commits leave added. So a statement re-wrapped or re-indented without a
    token changing, or given a new comment, adds nothing, while a token changed
    on any line of a wrapped marker - an argument, or the trailing comma a
    formatter adds when it wraps - adds the whole statement, as an edit to a
    one-line marker always did.

    The logical lines are the tokenizer's, so a file this interpreter cannot
    parse is read the same way and named as read so (`PL-TC2D`); each version
    is parsed only to say that.

    **Each is counted in the definition it applies to** (`PL-W6ZD`), the one
    `python.places` gives it: a decorator the one it decorates, any other
    statement the one holding it. Counted by its tokens alone, a marker moved
    from `test_a` onto `test_b` was one statement removed from the file and
    the same one added, and the fold cancelled the two while a test that ran
    no longer did. A test moved whole takes its marker with it and is no
    change; one renamed takes it to a name that did not hold it, which reads
    as added - the side this check fails toward.

    **A configuration file is read the same way, through its format's own
    reader** (`PL-PNZB`). A diff line of one can be a fragment of a value,
    as a Python line can be of a statement: a TOML array re-wrapped one
    element to a line was refused as a suppression added, and `no:xfail`
    split by a line-ending backslash inside a multi-line string, or moved
    from one key's continued value to another's, passed as `none`. So every
    version of a `.toml` file is read with `tomllib`, and of a `.cfg` or
    `.ini` file with `configparser`, each value split into statements
    (`_statements`) and folded as the logical lines are. A comment is no
    value either reader returns, so it is no statement, as in Python.

    `added_lines` is `_net_line_changes`' added half, read for every file
    neither reader read whole: one some version of which the tokenizer or
    its format's reader refuses, which is named.
    """
    suffixes = QUOTING_SUFFIXES + tuple(CONFIGURATION_READERS)
    steps, keys, unread = _file_steps(root, base, commits, suffixes)
    if unread:
        return SuppressionAudit(unread=unread)
    order = list(dict.fromkeys(step.key for step in steps))
    blobs = _blobs(root, {spec for step in steps for spec in (*step.before, step.after) if spec})
    if blobs is None:
        return SuppressionAudit(unread="git could not be asked for the files' contents")

    versions = _versions(order, steps)
    read: dict[str, tuple[tuple[str, str, bool], ...]] = {}  # by object id: one version, one read
    # Per file as well, so a copy is read by the one reader its file's name calls for.
    values: dict[str, dict[str, tuple[str, ...]]] = {}
    parsed: dict[str, bool] = {}
    tokenized: dict[str, str] = {}
    unparsed: dict[str, str] = {}
    for key in order:
        if not key.endswith(QUOTING_SUFFIXES):
            name, reader, refusals = CONFIGURATION_READERS["." + key.rpartition(".")[2]]
            values[key] = {}
            declined = _read_versions(blobs, versions[key], reader, refusals, values[key])
            if declined is not None:
                unparsed[key] = _unread_values(name, *declined)
            continue
        refused = _read_versions(blobs, versions[key], _suppression_statements, UNTOKENIZABLE, read)
        unparsable = _read_versions(blobs, versions[key], _parses, UNPARSABLE, parsed)
        why = _unparsable(*unparsable) if unparsable else ""
        if refused is not None:
            unparsed[key] = _untokenizable(why, *refused)
        elif why:
            tokenized[key] = why

    # Each statement of one version: what the fold counts, what the page
    # shows, and whether it holds a suppression.
    def statements_of(key: str, spec: str) -> list[tuple[str, str, bool]]:
        held = blobs.get(spec) if spec else None
        if held is None or key in unparsed:
            return []
        if key in values:
            return [
                (text, text, bool(_SUPPRESSION_RE.search(text))) for text in values[key][held[0]]
            ]
        return list(read[held[0]])

    removed: dict[str, Counter[str]] = {key: Counter() for key in order}
    added: dict[str, Counter[str]] = {key: Counter() for key in order}
    last: dict[str, str] = {}
    for step in steps:
        parents = [
            Counter(counted for counted, _, _ in statements_of(step.key, spec))
            for spec in step.before
        ]
        now = Counter(counted for counted, _, _ in statements_of(step.key, step.after))
        for tokens in set(now).union(*parents):
            removed[step.key][tokens] += max(0, min(p[tokens] for p in parents) - now[tokens])
            added[step.key][tokens] += max(0, now[tokens] - max(p[tokens] for p in parents))
        last[step.key] = step.after

    found: list[str] = []
    for key in order:
        net = added[key] - removed[key]
        for counted, shown, suppresses in statements_of(key, last[key]):
            if suppresses and net[counted] > 0:
                net[counted] -= 1
                found.append(shown)
    read_whole = {key for key in order if key not in unparsed}
    found += [
        line.strip()
        for path, line in added_lines
        if keys.get(path, path) not in read_whole and is_suppression_line(path, line)
    ]
    return SuppressionAudit(
        tuple(found), tuple(unparsed.items()), tokenized=tuple(tokenized.items())
    )


def _suppression_statements(source: str) -> tuple[tuple[str, str, bool], ...]:
    """Each logical line of `source` as `added_suppressions` folds it.

    What the fold counts, what the page shows, and whether it suppresses. The
    count joins the definition `python.places` gives the statement to its
    tokens with a NUL, which no definition's name holds, so the two cannot run
    together however the tokens read.

    Raises one of `UNTOKENIZABLE` where the tokenizer refuses the file.
    """
    lines = read_logical_lines(source)
    return tuple(
        (f"{place}\0{line.tokens}", line.shown, is_suppression_statement(line))
        for line, place in zip(lines, places(lines), strict=True)
    )


def suppression_check(audit: SuppressionAudit) -> Check:
    """`no suppression added`, from an audit."""
    name = "no suppression added"
    if audit.unread:
        return Check(name, False, f"not read: {audit.unread}")
    shown = _capped(audit.found)
    shown += [f"read line by line, not parsed: {path} - {why}" for path, why in audit.unparsed]
    shown += [_tokenized(path, why) for path, why in audit.tokenized]
    detail = f"{len(audit.found)} line(s)" if audit.found else "none"
    return Check(name, not audit.found, detail, tuple(shown))


def _tokenized(path: str, why: str) -> str:
    """The page's line naming a file read through the tokenizer rather than parsed."""
    return f"read through the tokenizer, not parsed: {path} - {why}"


#: How many lines a check prints under itself. The counts on the check's own
#: line are never capped, and a capped list ends by counting what it left out,
#: so the count and the lines under it reconcile (`PL-7NKD`).
SHOWN_LINES = 5


def _capped(lines: Sequence[str]) -> list[str]:
    """The first `SHOWN_LINES` of `lines`, then one line counting the rest.

    A bounded display says it is bounded. A block printing five lines under a
    count of six left the reader unable to tell which line was missing, and
    reading it back took a `git show` per commit (`PL-7NKD`).
    """
    shown = list(lines[:SHOWN_LINES])
    if len(lines) > SHOWN_LINES:
        shown.append(f"and {len(lines) - SHOWN_LINES} more line(s)")
    return shown


RESIDUAL = (
    "Not proven: whether a new test asserts the value the model should produce "
    "or merely the value it currently produces. A test can exercise the right "
    "line and assert the wrong thing. Read the new test bodies."
)

# A status no process can return, so a caller can tell a command killed at the
# timeout from one that ran and failed. A shell reports an exit status in
# 0-255 and a signal death as a small negative number, so a value outside both
# collides with neither. It needs a status of its own because 1 is what a
# failing check returns.
TIMED_OUT = 1000


COMMISSION_NOTE = " - reported, not refused: this is a self-audit, not a delegated review"


@dataclass(frozen=True)
class Check:
    """One thing that was looked at, and what was found."""

    name: str
    passed: bool
    detail: str = ""
    lines: tuple[str, ...] = ()
    #: Whether a failure here refuses the work or merely reports it. Set only
    #: in self-audit mode, and only on the four checks that are about the
    #: *commission* rather than about the work's integrity - see
    #: `verify_item`. An advisory check still prints what it found, with the
    #: reason it is not refusing, because a guard that quietly stops applying
    #: is worse than one that fires wrongly.
    advisory: bool = False
    #: Whether this is one of the four checks about the *commission* - the
    #: diff's scope, a protected path, a gate path, the item's own front
    #: matter - rather than about the work's integrity. `advisory` says whether
    #: a failure refuses; this says which kind of check failed, which is how a
    #: bare run on a session's own branch can say that `--self` was the
    #: question it meant to ask (`PL-PFK1`).
    commission: bool = False

    @property
    def blocks(self) -> bool:
        """Whether this result refuses the work."""
        return not self.passed and not self.advisory

    def describe(self) -> str:
        if self.passed:
            mark = "PASS"
        else:
            mark = "FAIL" if not self.advisory else "NOTE"
        head = f"  {mark}  {self.name}"
        if self.detail:
            head += f" - {self.detail}"
        return "\n".join([head, *(f"          {line}" for line in self.lines)])


@dataclass
class Verification:
    """Every check run against one item, and whether it may be accepted."""

    item: Item
    base: str
    #: What is wrong with the base itself, when something is. A scope check is
    #: only as good as the ref it subtracts, and a stale one produces a report
    #: that is wrong in the direction of looking alarming - other branches'
    #: files, named as this item's overreach.
    base_note: str = ""
    checks: list[Check] = field(default_factory=list)
    #: Whether the per-item checks stopped before they had all run. An item
    #: with no command, or with nothing between its base and `HEAD`, has
    #: nothing further to look at, and the project-wide check says nothing
    #: about it either way.
    stopped_early: bool = False

    @property
    def passed(self) -> bool:
        return not any(check.blocks for check in self.checks)

    def describe(self) -> str:
        lines = [f"{self.item.identifier} {self.item.title}", f"  against {self.base}"]
        if self.base_note:
            lines.append(f"  {self.base_note}")
        lines.append("")
        lines.extend(check.describe() for check in self.checks)
        lines.append("")
        lines.append("  ACCEPT" if self.passed else "  REJECT")
        lines.append(f"  {RESIDUAL}")
        return "\n".join(lines)


def _run(
    args: list[str],
    root: Path,
    *,
    shell: bool = False,
    timeout: float = 1800,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run a command, returning its exit status, its stdout and its stderr.

    What comes through here is a command recorded in the store - an item's
    `verify:` field, and the configured check command - run as written and
    through a shell, because running the recorded command verbatim is the
    entire job. Both were trusted enough to be committed to the repository, so
    there is no untrusted input to guard against here; the guard that matters
    is review of what gets committed.

    **Git does not come through here.** A git read that discarded the status
    had git's complaint arrive as data: that is how a base that did not
    resolve came back from `changed_paths` as three changed paths
    (`PL-9RFP`). Every git read goes
    through `vcs.call_git` - `_git` where a failure ends the audit - so it is
    classified, decoded and bounded as `vcs` reads the same question
    (`PL-S9JK`).
    """
    try:
        result = subprocess.run(
            " ".join(args) if shell else args,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            shell=shell,
            env=env,
        )
    except subprocess.TimeoutExpired as error:
        # Ahead of the clause below rather than folded into it: `TimeoutExpired`
        # is a `SubprocessError`, so the ordering is the whole of what keeps a
        # killed command distinguishable from a failed one.
        return TIMED_OUT, "", str(error)
    except (OSError, subprocess.SubprocessError) as error:
        return 1, "", str(error)
    return result.returncode, result.stdout or "", result.stderr or ""


#: How many lines of each stream `failure_evidence` keeps.
EVIDENCE_LINES = 4


def failure_evidence(stdout: str, stderr: str) -> tuple[str, ...]:
    """The last few non-blank lines of a failed command's stdout, then of its stderr.

    Each stream keeps its own tail. A check writes its finding to stdout - pytest's
    `FAILED` line, a ruff or mypy report - and what runs around the check writes
    to stderr: `make check` runs `uv sync` before pytest, and `make` reports the
    exit status after it. While the two streams were joined and the last four
    lines kept, stderr filled three of them, and the one stdout line kept was
    pytest's count, so a REJECT for a failing test never named the test
    (`PL-P66B`). Filtering out the `uv` lines would not have done it: any stderr
    written before the failure takes the same place.
    """
    return tuple(
        line
        for stream in (stdout, stderr)
        for line in [part for part in split_lines(stream) if part.strip()][-EVIDENCE_LINES:]
    )


#: Raised by `_git`; `vcs`'s, so a reader of `verify` and one of `vcs` catch one class.
GitUnanswered = vcs.GitUnanswered


def _git(args: list[str], root: Path) -> str:
    """Git's standard output for a read the audit rests on, or `GitUnanswered`.

    Raised rather than returned, because every caller of this has the same
    answer to a failure and none of them has a value it could return instead.
    An empty list of paths is a branch that changed nothing, and an empty diff
    is one that added no suppression. Returning either for a read that never
    happened is how the commission audit came to report git's usage text as
    three edits, and to pass both integrity checks on a diff it never saw
    (`PL-9RFP`). Nothing here has to remember to check a status, and a caller
    that forgets to catch fails loudly instead of answering.

    `vcs.read_git`, so a read here is classified, decoded and bounded as
    `vcs._run_git` reads the same question (`PL-S9JK`): the reason is git's
    first line on stderr, which names the revision it could not read, and only
    stdout is returned, so none of stderr can reach a caller as output. Decoded
    as written, so a raw `\r` in a subject or a `-z` path stays in its record;
    the two patch reads translate theirs (`PL-0R4M`).
    """
    return vcs.read_git(args, root, timeout=vcs.LONG_GIT_TIMEOUT)


def item_commits(root: Path, base: str, identifier: str) -> tuple[str, ...]:
    """Commits on this branch whose subject leads with the item's id.

    One commit per item is what `docs/worker.md` asks of a worker, and this is
    what that rule buys. A batch branch carries several items' work, so
    checking one item against the branch's whole diff would fail every time
    and say nothing. Scoped to its own commits, each item is judged on what it
    actually changed - which is also what lets a reviewer take four items and
    reject the fifth.

    **Read through `vcs.leading_ids`, the one reading of which ids a subject
    claims** (`PL-2BWP`). This read `git log --grep`, which matches the id
    anywhere in the message, while `other_items_named` and the claim record
    read the subject's leading run - so a commit citing the id in its body, as
    `PL-HC8P`'s capture commit cited `PL-PVW2`, was the item's to one reader of
    the same branch and not to the other.

    Raises `GitUnanswered` where the log cannot be read. Returning nothing
    would send the audit to the whole branch diff instead. Returning what came
    back, as this did until `PL-9RFP`, handed git's three-line complaint about
    the base on as three commit hashes.
    """
    # NUL-terminated, so a record is split only where git ended it.
    output = _git(["log", "-z", "--format=%H%x09%s", f"{base}..HEAD"], root)
    wanted = identifier.upper()
    commits: list[str] = []
    for record in output.split("\0"):
        commit, _, subject = record.strip().partition("\t")
        if commit and wanted in vcs.leading_ids(subject):
            commits.append(commit)
    return tuple(commits)


def changed_paths(root: Path, base: str, commits: tuple[str, ...] = ()) -> tuple[str, ...]:
    """Every path the work has touched, committed or not.

    The working tree is included because a worker that has not committed
    everything has still changed it, and a scope check that only saw commits
    would pass a branch with an uncommitted edit to the scientific core
    sitting in it. Uncommitted work belongs to no item in particular, so it is
    attributed to whichever item is being verified rather than excused.

    Raises `GitUnanswered` where either half cannot be read, a base that does
    not resolve among them. The empty tuple is a branch that changed nothing,
    so no value this could return would say "unread" (`PL-9RFP`).

    **Both halves read `-z`, the one form in which git quotes no path**
    (`PL-8HSX`). The committed half asks for it through `changed_path_args`,
    and the uncommitted half is `vcs.uncommitted_paths`, which `working_paths`
    reads too (`PL-QNHZ`). A quoted path starts with `"`, so `is_under` matches
    it against nothing protected. Git quotes a path outside ASCII while
    `core.quotePath` is on, and one holding a tab, newline, `"` or `\\` however
    that is set. Measured on git 2.43.0, 2026-09-25, a committed
    `src/anesthesia_sim/core/café.py` and an uncommitted
    `src/anesthesia_sim/core/a b.py` each passed as "none touched" before
    every read asked for `-z`. The untracked files come from `ls-files
    --others`, which `status.showUntrackedFiles=no` in a user's git config does
    not hide, and which lists each file in an untracked directory.
    """
    if commits:
        committed = _git(vcs.changed_path_args("show", "--name-only", "--format=", *commits), root)
    else:
        committed = _git(vcs.changed_path_args("diff", "--name-only", f"{base}...HEAD"), root)
    return tuple(sorted({*vcs.listed_paths(committed), *vcs.uncommitted_paths(root, _git)}))


def _diff_text(root: Path, base: str, commits: tuple[str, ...]) -> str:
    # Through `_git`, so a diff git would not produce raises instead of
    # reading as one that added no suppression. A patch's `+` and `-` lines are
    # file lines, so their line ends are translated (`PL-0R4M`).
    if commits:
        return file_text(_git(["show", "--format=", *commits], root))
    return file_text(_git(["diff", f"{base}...HEAD"], root))


#: The post-image path out of a `diff --git a/x b/x` header. Git quotes either
#: side that holds a byte it will not print, so the quoted post-image is read
#: first and its quoting taken off by `vcs.unquoted_path` (`PL-MR8Z`). A
#: header this cannot read yields `""`, which `is_suppression_line` reads as
#: "could be code" rather than as "is not" - an unreadable header stays on the
#: reporting side.
# regex: git writes either side of the header quoted or bare, and two paths
# joined by a space can be split only by these four forms.
DIFF_HEADER_RE = re.compile(
    r'^diff --git (?:"a/(?:[^"\\]|\\.)*"|a/.*) (?P<quoted>"b/(?:[^"\\]|\\.)*")$'
    r"|^diff --git a/(?:.*) b/(?P<path>.*)$"
)

#: A merge's file header in the combined diff `git show` writes for one, and
#: the path git names, quoted as a two-way header's is (`PL-W6ZD`).
COMBINED_HEADERS = ("diff --cc ", "diff --combined ")


def _combined_header_path(line: str) -> str | None:
    """The path a merge's `COMBINED_HEADERS` line names, as written, or `None` for another line."""
    for header in COMBINED_HEADERS:
        if line.startswith(header):
            return line.removeprefix(header)
    return None


def _header_path(header: re.Match[str] | None) -> str:
    """The post-image path a `DIFF_HEADER_RE` match names, unquoted, or `""`."""
    if header is None:
        return ""
    if quoted := header.group("quoted"):
        return vcs.unquoted_path(quoted).removeprefix("b/")
    return header.group("path")


def _net_line_changes(root: Path, base: str, commits: tuple[str, ...]) -> list[tuple[str, str]]:
    """The lines the work added, with lines it also removed folded out per file.

    Each line comes back paired with the path it came from, because whether an
    added line can be a suppression at all depends on the kind of file it is
    in (`PL-7TYC`).

    `git show` over an item's commits concatenates one patch per commit rather
    than producing the branch's net change, because an item's commits need not
    be contiguous and `git diff <first>^ <last>` would sweep in whatever
    another item committed in between - which is why the per-commit form is
    there. So a line a branch added in one commit and removed in the next was
    read as added, and "no suppression added" reported work the branch had
    already undone. The error ran in the safe direction, which is why it
    survived: nothing that reaches `HEAD` escapes the check. What it cost was
    the report's credibility, because the cancelling commit is not in the output
    and so the worker cannot argue with it (`PL-VP40`).

    Cancelling an added line against an identical removed line within the same
    file is exactly as precise as what consumes this: the suppression check's
    fallback for a Python file the tokenizer refuses, or a configuration file
    its format's reader refuses, which reads a line's text rather than the
    statement it belongs to. It costs no extra git call. The check proper makes
    the same fold over statements instead (`added_suppressions`). Counting
    rather than de-duplicating is what keeps it safe: a file whose patches
    remove one marker and add two still reports one added. A line merely
    *moved* within a file cancels too, since the suppression was already there.

    Per file, never across: a marker deleted from one file and an identical one
    added to another is two facts, not a move, and the added one is reported.

    **A merge's patch is a combined diff, and is read as one** (`PL-W6ZD`).
    `git show` writes it under `diff --cc`, each line prefixed by one column
    per parent, and read as a two-way patch `++xfail_strict = false`, a line
    neither parent held, was taken for a `+++` header and dropped, while a
    line one parent brought was charged to the merge. A line is now added or
    removed where every column says so, counted per column and the counts'
    least kept, which is `_file_steps`' reading of a merge against every
    parent at once: added where no parent held it, removed where every one
    did. A file's header lines run to its first hunk, whose header says how
    many columns there are.

    Lines come back in the order the diff presented their files, so two runs
    over one branch report the same sample.
    """
    diff = _diff_text(root, base, commits)
    # Insertion-ordered by first appearance of each file, which is what makes
    # the returned order - and so the five lines the report prints - stable.
    # The path sits beside the two counters rather than in front of them, so
    # that `side` still indexes a homogeneous pair.
    per_file: dict[str, tuple[str, tuple[Counter[str], Counter[str]]]] = {}
    current = ""
    path = ""
    # A combined section's columns, one per parent, each the lines added and
    # removed against that parent; none before its first hunk, or in a
    # two-way section.
    combined = False
    columns: list[tuple[Counter[str], Counter[str]]] = []
    # Whether a two-way section has reached its first hunk. The lines before
    # it are the file's header, `---` and `+++` among them; every `+` or `-`
    # line after it is content, a removed `--1` or an added `++2` included.
    in_hunk = False

    def fold() -> None:
        if not columns:
            return
        held = per_file.setdefault(current, (path, (Counter(), Counter())))[1]
        for side in (0, 1):
            agreed = columns[0][side].copy()
            for column in columns[1:]:
                agreed &= column[side]  # the least count of each line
            held[side].update(agreed)

    for line in split_lines(diff):
        if line.startswith("diff "):
            fold()
            combined, columns, in_hunk = False, [], False
        if line.startswith("diff --git "):
            path = _header_path(DIFF_HEADER_RE.match(line))
            # A quoted header is keyed by the path it names, as a merge's is
            # below, so the fold runs across both spellings of one file.
            current = f"diff --git a/{path} b/{path}" if path and line.endswith('"') else line
            continue
        if (merged := _combined_header_path(line)) is not None:
            path = vcs.unquoted_path(merged)
            # Keyed as the file's two-way patches are, so the fold runs across both.
            current, combined = f"diff --git a/{path} b/{path}" if path else line, True
            continue
        if combined:
            if line.startswith("@@@"):
                width = len(line) - len(line.lstrip("@")) - 1
                columns = columns or [(Counter(), Counter()) for _ in range(width)]
            elif columns:
                text = line[len(columns) :]
                for column, mark in zip(columns, line[: len(columns)], strict=False):
                    if mark in "+-":
                        column[0 if mark == "+" else 1][text] += 1
            continue
        if not in_hunk:
            in_hunk = line.startswith("@@")
            continue
        if line.startswith("+"):
            side = 0
        elif line.startswith("-"):
            side = 1
        else:
            continue
        if current not in per_file:
            per_file[current] = (path, (Counter(), Counter()))
        per_file[current][1][side][line[1:]] += 1
    fold()
    added: list[tuple[str, str]] = []
    for where, (added_here, removed_here) in per_file.values():
        # `Counter.__sub__` keeps only positive counts, which is multiset
        # difference: the fold the check wants.
        added.extend((where, text) for text in (added_here - removed_here).elements())
    return added


def _store_at(root: Path, base: str, items_dir: str) -> dict[str, str] | None:
    """Each item id the base ref holds, mapped to its file, or `None` where git did not list it.

    `vcs._items_at`, the one listing of a ref's item files (`PL-86H3`). A
    store git lists as empty is read as unread too, since a tree holds no
    empty directory and the base with no store is the case this declines on.
    """
    try:
        held = vcs._items_at(base, root, items_dir, _git)
    except vcs.GitUnanswered:
        return None
    return held or None


def _listed_copy(root: Path, spec: str) -> str | None:
    """The file at `<rev>:<path>` that `_store_at` listed, or `None` where git did not give it.

    Absent counts as unread here, though `vcs.git_answer` reads `git show`'s
    exit 128 on a blob as "not there": the caller has just listed the file, so
    a copy git will not show is a read that failed, not an item the base lacks.
    """
    call = vcs.call_git(["show", spec], root)
    text = call.answer
    return text if call.code == 0 and vcs.answered(text) else None


def sanctioned_queue_edit(root: Path, base: str, commits: tuple[str, ...], path: str) -> str:
    """Whether an out-of-`touches` queue edit, or a body record, is one the workflow asked for.

    Four kinds are, and each is mechanically distinguishable from the work
    being tampered with - which is what makes exempting them safe rather than
    a hole. Returns the kind for the report to name, or `""` for an ordinary
    edit that stays outside the commission.

    **The three in the store are read off the item, never off the diff's
    lines.** Each change the scope made to the file - each commit against its
    first parent, or the branch against its fork point where no commit names
    the item - is read before and after it by the reader every other command
    reads an item with, and every change has to be one of the kinds; a file
    whose changes are of two kinds is reported under both. Read a line at a
    time, a diff line looked like a front-matter line wherever it fell: a
    `pr:` line inserted between a value and the indented line continuing it
    passed as the `pr` write while it cut the value's tail into `pr`, a brief
    quoting `status: untriaged` inside a fence passed as a capture at any
    status, and a removed thematic break, which a diff shows as `----`, was
    skipped as a file header (`PL-24MT`).

    **`"capture"`** - a file the change *created*, whose status as the item's
    reader reads it is `untriaged`. `CLAUDE.md` requires a finding not fixed
    in the session to be captured before the session ends, and requires every
    commit subject to lead with the current item's id; doing both puts the new
    item file on a commit `item_commits` attributes to the item being
    verified, and the audit then reported a `REJECT` for following the
    instructions (`PL-66PR`). A capture cannot weaken anything: the file did
    not exist on the base, so there is no prior content for it to have
    changed.

    **`"pr"`** - an existing item file that reads as it did with a `pr:`
    field added, which `_pr_recorded` decides: every other field the same and
    in the same order, the body the same, and the number a number. That is
    what `bin/docket record N` writes onto the closures a branch introduces
    while its pull request is open (`PL-HMZZ`), and the `docket`
    skill's close-out says to let it ride the closure commit, or the push that
    follows it, rather than composing one for it. `verify` read those writes
    as paths outside the commission and rejected the close-out that followed
    the instruction (`PL-ZYQC`). The number is the pull request's own, which
    its required check holds the field to, and `record` never replaces the
    number on a landed closure, so there is nothing here a worker could use to
    change what a check measures.

    **`"recurrence"`** - an existing item file whose `recurrences:` value
    arrived, or grew by entries on its right, and nothing else changed.
    `bin/docket new` writes it onto the item a capture matched, so a worker
    that captures a finding - which `CLAUDE.md` requires unconditionally -
    edits an item it was never commissioned to touch, exactly as `record`'s
    write does. The value is dictated rather than chosen: today's date and
    the id of the capture the session just made. It buys nothing a worker could
    want either, since the field only makes an item *named* as a generator-tier
    candidate for a human to confirm, and cannot move a band, a status or
    anything a check measures (`PL-X5JR`).

    The growth case is the one that needs care, because extending a value can
    also rewrite what it recorded. So it is matched on the value: the change
    must leave every other field and the body as they were and add whole
    entries after the ones already recorded - which is an append and cannot be
    an edit of what was there. Matched on one diff line, an append to a value
    continued on an indented line read as an edit, since the line it grew
    carries no key (`PL-J503`).

    **`"record"`** - a pull request's body the branch added: `<N>.md` directly
    under `RECORDS`, which the base does not hold and whose copy at `HEAD`
    carries `pr: N` and a `recovered:` line. `tools/pr_body_check.py
    --recover` writes it for a squash commit that reached the default branch
    with no body, and the release step runs it and lets the files ride the
    release's pull request (`PL-3PH2`). A `recorded:` line stands in for
    `recovered:`: `--record` wrote one on every pull request's branch while
    `PL-979D`'s per-pull-request record stood, and a branch opened before
    `PL-3PH2` retired it may still carry one. It is the one kind outside the
    store, and the one read off the base and `HEAD` rather than change by
    change: a file the branch rewrites would read, commit by commit, as an
    edit to a file already there. Like a capture it cannot weaken anything,
    since the base holds no prior content for it to have changed. A file the
    base holds is a merged pull request's history, and a file there under
    another name, or with neither line, is not the write the workflow asked
    for.

    Nothing else is exempt. An item file this branch edited in any other way -
    a `status`, a `touches`, a `verify:` command - is still outside `touches`
    and still fails, which is the case the audit exists for and the reason
    this reads each change rather than the path. Nor is a `pr` or recurrence
    write onto a copy whose front matter the reader declined part of, since
    neither can vouch for lines nobody read (`_declines`, `PL-4DM0`).

    **Nor is a path with an uncommitted change** (`PL-W6ZD`). Every kind is
    read off a commit's change, or the base and `HEAD`, so a change no commit
    holds is one nothing here read: a `status: done` left uncommitted beside a
    committed `pr:` write answered `pr`, while `changed_paths`, which reads
    the working tree, listed the path. Such a path is outside `touches`
    whatever its commits wrote, as an uncommitted capture or record already
    was, since neither has a commit to read.
    """
    if path in vcs.uncommitted_paths(root, _git):
        return ""
    if is_under(path, (RECORDS,)):
        return "record" if _added_record(root, base, path) else ""
    kinds = [_queue_kind(before, after) for before, after in _changes(root, base, commits, path)]
    return " and ".join(dict.fromkeys(kinds)) if kinds and all(kinds) else ""


def _changes(
    root: Path, base: str, commits: tuple[str, ...], path: str
) -> list[tuple[str | None, str | None]]:
    """Each change the scope made to `path`, as the file read before it and after it.

    Each commit is read against its first parent, and the branch against its
    fork point where no commit names the item. A commit that left the file
    alone is passed over, and `None` stands for no file on that side. Empty
    where git could not be asked or a copy is not UTF-8, which leaves the file
    as no kind and so outside `touches`.
    """
    if commits:
        steps = [(f"{commit}^:{path}", f"{commit}:{path}") for commit in commits]
    else:
        fork = vcs.call_git(["merge-base", base, "HEAD"], root).answer
        if not fork.strip():
            return []
        steps = [(f"{fork.strip()}:{path}", f"HEAD:{path}")]
    blobs = _blobs(root, {spec for step in steps for spec in step})
    if blobs is None:
        return []
    changes: list[tuple[str | None, str | None]] = []
    for before_spec, after_spec in steps:
        before, after = blobs.get(before_spec), blobs.get(after_spec)
        if before == after:
            continue
        try:
            changes.append(
                (
                    None if before is None else before[1].decode("utf-8"),
                    None if after is None else after[1].decode("utf-8"),
                )
            )
        except UnicodeDecodeError:
            return []
    return changes


def _queue_kind(before: str | None, after: str | None) -> str:
    """Which of `sanctioned_queue_edit`'s kinds one change to an item file is, or `""`.

    `None` is no file on that side: a change that created the file can only be
    a capture, and one that deleted it is none of them.
    """
    if after is None:
        return ""
    if before is None:
        return "capture" if _captured(after) else ""
    if _pr_recorded(before, after):
        return "pr"
    return "recurrence" if _recurrences_grew(before, after) else ""


def _captured(text: str) -> bool:
    """Whether `text`, a file the change created, is an item at `status: untriaged`.

    Its status as `parse_item` reads it, so a brief quoting a `status:
    untriaged` line inside a fence is prose, as it is to every other reader of
    the item, and the file is at whatever its front matter says (`PL-24MT`).
    """
    # Set aside on purpose: a `status:` written as a block arrives empty, which
    # reads as no capture, and a capture declining any other field is one
    # `docket check` refuses by name.
    fields, _body, _declined = parse_front_matter(text)
    return fields.get("status") == "untriaged"


def _declines(
    parsed: tuple[list[tuple[str, str]], tuple[str, ...], tuple[str, ...], tuple[str, ...], str],
) -> bool:
    """Whether `_front_matter_pairs` declined any of the front matter it read.

    A block list or block scalar arrives as its key with an empty value, and a
    line continuing nothing as written beside the fields, so two copies that
    differ only inside a declined block compare equal: a `touches` block list
    gaining an entry, or a folded `reason:` rewritten, beside an added `pr:`
    passed as the `pr` write (`PL-4DM0`). Neither exemption can vouch for lines
    its reader never read, so a copy holding any of the three is no sanctioned
    edit, and the path stays outside the commission. `docket check` refuses
    each form by name as well, so this costs a well-formed store nothing.
    """
    _pairs, block_lists, block_scalars, unread, _body = parsed
    return bool(FrontMatterDeclines(block_lists, block_scalars, unread))


def _pr_recorded(before: str, after: str) -> bool:
    """Whether `after` is `before` with a `pr:` field added and nothing else changed.

    What `bin/docket record N` writes, read as `_recurrences_grew` reads its
    append: both copies through `_front_matter_pairs`, so a value is whole
    whichever lines carry it. A `pr:` line inserted between a value and the
    indented line continuing it reads as what it does there - the value cut
    short and its tail folded into `pr` - and a body changed beside it, a
    thematic break removed included, is an edit to the brief (`PL-24MT`).
    Every other field has to read the same and stand in the same order, and
    the body the same; neither copy may hold anything the reader declined
    (`_declines`); `before` holds no `pr`, since `record` never replaces the
    number on a landed closure; and `after` holds one, a number as
    `model.pr_number` reads it, so `pr: 0` and `pr: 07`, which `docket check`
    refuses, are not what `record` wrote (`PL-JT7Y`).
    """
    was, now = _front_matter_pairs(before), _front_matter_pairs(after)
    if was is None or now is None or _declines(was) or _declines(now) or was[1:] != now[1:]:
        return False
    if any(key == "pr" for key, _value in was[0]):
        return False
    numbers = [value for key, value in now[0] if key == "pr"]
    return (
        len(numbers) == 1
        and pr_number(numbers[0]) is not None
        and [pair for pair in now[0] if pair[0] != "pr"] == was[0]
    )


def _recurrences_grew(before: str, after: str) -> bool:
    """Whether `after` is `before` with whole entries added after its recorded `recurrences:`.

    The append `cmd_new` makes, and the only change this exemption admits. Both
    copies are read as `parse_item` reads them - `_front_matter_pairs`, whose
    fold is the one definition of where a value ends, and `split_list` - so
    the value is whole whichever lines carry it (`PL-J503`). Every other field
    and the body have to read the same on both sides, neither copy may hold
    anything the reader declined (`_declines`), and the entries already
    recorded have to stand first and unaltered, so an entry cannot be altered
    or dropped under cover of the append.

    **And what the value grew by has to be a new entry, not a suffix on the
    last one.** Withdrawing the final entry appends ` withdrawn DATE PL-XXXX`
    to it, which leaves it the same entry growing on its right - so a rule
    reading text would exempt the one edit that *cancels* evidence under the
    rule written for the edit that adds it. A withdrawal is a deliberate act
    with something to gain, so it declares the file it touches like any other
    work (`PL-34BG`). Comparing entries rather than text is what refuses it:
    the last entry changed, so the recorded ones do not stand unaltered.
    """
    was, now = _front_matter_pairs(before), _front_matter_pairs(after)
    if was is None or now is None or _declines(was) or _declines(now):
        return False
    pairs_was, *_, body_was = was
    pairs_now, *_, body_now = now
    if body_was != body_now:
        return False
    if [p for p in pairs_was if p[0] != "recurrences"] != [
        p for p in pairs_now if p[0] != "recurrences"
    ]:
        return False
    recorded = [value for key, value in pairs_was if key == "recurrences"]
    values = [value for key, value in pairs_now if key == "recurrences"]
    if len(recorded) > 1 or len(values) != 1:
        return False
    entries_was = split_list(recorded[0]) if recorded else ()
    entries_now = split_list(values[0])
    return (
        len(entries_now) > len(entries_was)
        and entries_now[: len(entries_was)] == entries_was
        and all(recurrence_entry_reads(entry) for entry in entries_now)
    )


def _added_record(root: Path, base: str, path: str) -> bool:
    """Whether `path` is a body record the branch added, as the `record` kind states it.

    The base is its tip rather than the fork point, so a record that merged
    before its branch went on reads as the history it now is. It is asked
    through `_git`, so a read git did not answer ends the audit rather than
    reading as a record the base lacks (`PL-9RFP`). `HEAD` holding no copy is
    an answer, not a failure: the record is uncommitted or deleted, and stays
    outside `touches` like any other such path.
    """
    folder, _, name = path.rpartition("/")
    # Named for its pull request's number, as `tools/pr_body_check.py` writes it
    # and `model.pr_number` reads one, so `07.md` names no record (`PL-JT7Y`).
    number = pr_number(name.removesuffix(".md")) if name.endswith(".md") else None
    if f"{folder}/" != RECORDS or number is None:
        return False
    if _git(["ls-tree", "-z", "--name-only", base, "--", path], root).strip("\0"):
        return False
    text = vcs.call_git(["show", f"HEAD:{path}"], root).answer
    if not text:
        return False
    # Set aside on purpose: a field written as a block arrives empty, so a
    # `pr:` or a date written as one makes the file no record here, which
    # leaves it outside `touches` like any other path.
    fields, _body, _declined = parse_front_matter(text)
    dated = any(fields.get(key, "").strip() for key in ("recovered", "recorded"))
    return pr_number(fields.get("pr", "").strip()) == number and dated


def worker_run_record(root: Path, base: str, folder: str, identifier: str, path: str) -> bool:
    """Whether `path` is the headless runner's record of a run on the item under review.

    `tools/headless_worker.py` commits one JSON record per run to the worker's
    branch, under the folder `docket.toml` names as `worker_runs_dir`, and
    `docs/maintainer.md` makes `verify` the first step of reviewing that
    branch. Counted as work outside `touches`, the record turned every worker
    branch into a `REJECT` (`PL-4WFK`). So a file is sanctioned here when it
    sits directly in that folder, ends in `.json`, is committed, is absent
    from the base's tip, and its copy at `HEAD` is a JSON object whose `item`
    names the item being verified. The record names its item itself, so this
    reads that field rather than working the item out from the file name.

    Like a body record it cannot weaken anything: the base holds no prior
    content for it to have changed, and nothing reads the record to decide
    what a check measures. A record for another item, a nested file, a file
    the base holds, and an uncommitted record each stay outside `touches`. A
    read git did not answer ends the audit, as `_added_record`'s does.
    """
    if not folder or path in vcs.uncommitted_paths(root, _git):
        return False
    parent, _, name = path.rpartition("/")
    if parent != folder.strip().strip("/") or not name.endswith(".json"):
        return False
    if _git(["ls-tree", "-z", "--name-only", base, "--", path], root).strip("\0"):
        return False
    text = vcs.call_git(["show", f"HEAD:{path}"], root).answer
    try:
        record = json.loads(text) if text else None
    except json.JSONDecodeError:
        return False
    return isinstance(record, dict) and record.get("item") == identifier


@dataclass(frozen=True)
class Commission:
    """What the *base* holds for an item - the work as it was commissioned.

    **One rule decides which copy of an item, the base's or the branch's, each
    contract field is read from, and it is keyed on what kind of statement the
    field is, never on the field** (`PL-B8HZ`; project owner, 2026-09-25,
    ratified, over reading every field from the base's copy with
    `needs-decision` as the one exception). Six items arrived one field at a
    time before it was stated - branch-side reads gave false `ACCEPT`s
    (`PL-KSV2`, `PL-PZ6T`) and base-side reads false `REJECT`s (`PL-ZMGR`,
    `PL-K4R5`, `PL-YZJD`, `PL-TKFD`) - so a new field is placed by one
    question, and the copy follows from the answer:

    1. **What the work did** - `status`, `closed`, `reason`, `pr`. An
       *outcome*, read from the branch's copy, because the close-out is what
       writes it, and it excuses nothing: a drop claims no work for a command
       to prove (`PL-L4KX`, `PL-BX1C`).
    2. **What the work was to satisfy, written before it existed** -
       `verify:` and `touches:`. A *prediction*: a command naming a test not
       yet written, a path list naming files not yet created. The base's copy
       is the commission and is what the branch is measured against. The
       branch's copy is a *correction* of the prediction - it is the evidence
       the audit runs and reads, and it is printed as a correction beside the
       base's with the base's own result, never substituted silently. A
       delegated audit refuses the correction outright, through
       `front_matter_check`.
    3. **What the work may waive** - `not-delegable:`. A *waiver* removes a
       refusal: `not-delegable:` excuses the command check. A waiver waives
       only what the base holds, so the base's copy is the only word on it.
       Where the base holds nothing to waive - no commissioned command - the
       check has nothing to refuse and says why (`PL-KSV2`). `falsifies:`
       was the other waiver, and went with the assertion check it folded
       (`PL-CZXN`).

    In one sentence: a correction supplies evidence and is honoured and
    printed; a waiver removes a refusal and is the base's; an outcome is the
    branch's and excuses nothing. Each reader in `_check_item` names the kind
    it applies.

    Counted before the kinds were split, because one copy for every field was
    the shape first asked for. Of 1,437 close-outs on `main`, 163 rewrote a
    `verify:` the base already held, and every one was a correction - a grep
    target reworded, a test that never existed under the commissioned name, a
    moved file - so reading `verify:` from the base and refusing where its
    command fails would have refused 163 correct close-outs and caught
    nothing. A wrong correction leaves every integrity check
    running over the diff; a wrong waiver switches one off. That is why the
    two kinds cannot share a copy, and why "one copy" was the wrong altitude
    for the rule.

    The front matter is held whole, parsed once, so a field a later reader
    needs is taken from here without a new attribute.
    """

    #: The base's front matter as it holds it. Empty where the base holds no
    #: copy of the item, which is what every capture looks like, and where
    #: nothing could be read - `unread` says which.
    fields: Mapping[str, str] = field(default_factory=dict)
    #: Why nothing could be read. Non-empty only where `fields` is empty
    #: *because nothing was looked at*, which is the distinction a caller
    #: needs: an empty `verify` otherwise means "read it, it commissions no
    #: command".
    unread: str = ""

    @property
    def held(self) -> bool:
        """Whether the base holds a copy of the item at all."""
        return bool(self.fields)

    @property
    def verify(self) -> str:
        """The prediction: the command the base commissioned to prove the work."""
        return self.fields.get("verify", "").strip()

    @property
    def touches(self) -> tuple[str, ...]:
        """The prediction: the paths the base commissioned the work to stay inside."""
        return split_list(self.fields.get("touches", ""))


def read_commission(root: Path, base: str, items_dir: str, item: Item) -> Commission:
    """The *base's* copy of the item, parsed once, for every reader that takes a field from it.

    `unread` is non-empty only where nothing could be looked at, so an empty
    `Commission` carrying no `unread` means the commission was read and holds
    nothing. Keeping "could not look" apart from "looked, found nothing" is
    the same distinction `front_matter_check` makes below, for the same
    reason: a waiver is withheld identically by both, and only one of them is
    a finding.

    **Read from the base rather than from the working tree**, which is the
    whole of what makes a waiver worth having. `front_matter_check` refuses a
    branch that edits its own item's front matter in a delegated review, but
    in the self-audit the close-out runs that guard is an advisory by design
    (the close-out sets `status: done` in the same commit as the work). A
    session could otherwise write a `not-delegable:` reason beside the
    deletion of its command and skip the command check (`PL-KSV2`). Reading
    the base holds the property in both modes and needs no second guard: a
    line added on the branch changes what a *later* branch is measured
    against, and nothing about the branch that writes it.

    A base holding no copy of this item is not a failure to read - the item is
    new on the branch, which is what every capture looks like. Its `verify`
    comes back empty, and the emptiness is what lets such an item close on a
    `not-delegable:` reason: no command was commissioned for the branch to
    have removed.
    """
    if not item.path:
        return Commission(unread="the item names no file, so no commission could be read")
    held = _store_at(root, base, items_dir)
    if held is None:
        return Commission(unread=f"no item store at {base}:{items_dir} to read the commission from")
    was = held.get(item.identifier, "")
    if not was:
        return Commission()
    before = _listed_copy(root, f"{base}:{was}")
    if before is None:
        return Commission(unread=f"{base}:{was} could not be read")
    fields, _body, declined = parse_front_matter(before)
    if declined:
        return Commission(unread=f"{base}:{was} declines {declined}")
    return Commission(fields=fields)


def front_matter_check(
    root: Path, base: str, items_dir: str, item: Item, advisory: bool = False
) -> Check:
    """Whether the branch edited the front matter of its own item.

    A worker adds a `**Worked.**` or `**Blocked.**` note to an item's body and
    changes nothing above the fence. Marking work done, re-scoping `touches`,
    or rewriting the `verify:` command it was measured against are the
    reviewer's, and a branch that did any of them is reporting on a commission
    other than the one it was given.

    Returns the `Check` rather than the keys that differ, because what broke
    this was a third outcome with nowhere to go. `Item.path` is a filename
    inside the store, so the repository path wanted here is `items_dir` joined
    to it; built without the join, every `git show` asked for a path no ref has
    ever held, and the miss came back as the same empty set a clean comparison
    returns. The check then printed `PASS  item front matter unchanged` on
    every branch there has ever been, the ones that marked their own item done
    included (`PL-20PT`). So a comparison that could not be made is a refusal
    here: "could not look" and "looked, found nothing" are what the rest of
    this module exists to keep apart.

    A base holding no store at all is refused for that reason too, rather than
    read as a store of entirely new items - `vcs.stranded` declines the mirror
    case on the same argument, that an answer identical for every item is a
    misconfiguration reporting itself as a finding.

    The base copy is found by id rather than by name, because a title edit can
    move the file: a `git mv` pass brings the slug back into line with the new
    title (`PL-YTDN`), and a write through `store.write_item` lands it under a
    second name. The title is front matter, so looking the current name up
    would miss the one edit that moves the file out from under the guard
    watching it.
    """
    name = "item front matter unchanged"
    if not item.path:
        return Check(
            name,
            False,
            "the item names no file, so there was nothing to compare",
            advisory=advisory,
            commission=True,
        )
    try:
        after = (root / items_dir / item.path).read_text(encoding="utf-8")
    except OSError:
        return Check(
            name,
            False,
            f"no item file to read at {items_dir}/{item.path}",
            advisory=advisory,
            commission=True,
        )
    held = _store_at(root, base, items_dir)
    if held is None:
        return Check(
            name,
            False,
            f"no item store at {base}:{items_dir} to compare against",
            advisory=advisory,
            commission=True,
        )
    was = held.get(item.identifier, "")
    if not was:
        return Check(
            name, True, f"a new item file - {base} holds no copy to differ from", commission=True
        )
    before = _listed_copy(root, f"{base}:{was}")
    if before is None:
        return Check(
            name, False, f"{base}:{was} could not be read", advisory=advisory, commission=True
        )
    old, _body, was_declined = parse_front_matter(before)
    new, _body, now_declined = parse_front_matter(after)
    if was_declined or now_declined:
        # A declined block arrives empty on both sides, so an edit inside it
        # compared as no change (`PL-4DM0`'s shape, `PL-JTP1`).
        copy, declined = (base, was_declined) if was_declined else ("this checkout", now_declined)
        return Check(
            name,
            False,
            f"{copy}'s copy declines {declined}, so the front matter could not be compared",
            advisory=advisory,
            commission=True,
        )
    changed = tuple(sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k)))
    detail = ", ".join(changed) if changed else "unchanged"
    if changed and advisory:
        detail += COMMISSION_NOTE
    return Check(name, not changed, detail, advisory=advisory, commission=True)


def base_warning(root: Path, base: str) -> str:
    """What to say when the ref being compared against is not what it looks like.

    Empty when the base is current, which is the common case and says nothing.
    """
    behind = vcs.behind_remote(root, base)
    if not behind:
        return ""
    return (
        f"WARNING: {base} is {behind} commit(s) behind origin/{base}, so paths "
        "reported outside `touches` may be other branches' merged work rather "
        f"than this item's. Re-run with --base origin/{base}."
    )


def other_items_named(
    root: Path, commits: tuple[str, ...], identifier: str
) -> tuple[tuple[str, ...], int]:
    """The other items' ids the audited commits lead with, and how many commits carry one.

    `item_commits` selects by id so that a batch branch is judged per item -
    "a reviewer can take four items and reject the fifth", as its own
    docstring puts it. `CLAUDE.md` then requires a commit closing several
    items to lead with **all** of them, so on a batch branch every subject
    names every id and the selection is the whole branch whichever id is
    asked about. The per-item scoping does not happen, and every path check
    below is really being run against the batch (`PL-4LT9`).

    Reported rather than repaired, because the repair is a judgment this
    cannot make: the paths are legitimately declared *somewhere*, and which
    item commissioned which is not recoverable from the diff. Naming the other
    ids is what lets a reader see that the scope being audited is wider than
    the item, which is the whole of what went wrong silently before.

    An id counts only where it *leads* a subject, read through
    `vcs.leading_ids`, the one reading of which ids a subject claims: a
    subject citing another item mid-sentence is a citation, not a batch. Any
    id in the text used to count, and the note printed every audited commit as
    naming it, so `PL-19T3`'s closure, one of whose four subjects cited
    `PL-9RFP` in passing, read as four commits also naming `PL-9RFP`
    (`PL-WM46`). The count returned is of the commits that lead with another
    id, never of every commit audited.

    Raises `GitUnanswered` where the subjects cannot be read. Otherwise git's
    complaint would be searched for ids, and finding none would read as the
    commits naming this item alone.
    """
    if not commits:
        return (), 0
    # NUL-separated, so a subject is split only where git ended it.
    output = _git(["show", "-s", "--format=%s%x00", *commits], root)
    found: set[str] = set()
    carrying = 0
    for subject in output.split("\0"):
        others = set(vcs.leading_ids(subject)) - {identifier}
        found |= others
        carrying += bool(others)
    return tuple(sorted(found)), carrying


def verify_item(
    root: Path, item: Item, config: Config, base: str, base_note: str = "", self_audit: bool = False
) -> Verification:
    """Run the checks that are about this item, and no others.

    Split from `verify` for the one reason that matters when several items are
    reviewed together: everything here is genuinely per-item - the item's own
    command, its declared scope, its commits - while the project's own check
    proves a property of the tree and proves it identically however many items
    are being looked at. Running it once per item made a six-item batch take
    over two minutes, five of those runs re-proving a proved thing, and a
    reviewer who waits that long stops running the command at all.

    **`self_audit` is the session auditing its own branch, and it is a
    different question from the one this command was built for.** Everything
    here assumes a *delegated* worker: someone given a commission who might,
    deliberately or not, exceed it. Against that reader every guard below is
    right and absolute. A session running the close-out audit on its own work
    is not that reader - it **is** the reviewer - and against it four of the
    guards fire by construction on the path the project's own instructions
    prescribe:

    - `docs/worker.md` and `CLAUDE.md` require a capture and require every
      commit subject to lead with the item's id, which puts other items'
      files in the diff (`PL-66PR`, `PL-ZYQC` exempt the two sanctioned
      shapes; a triage pass edits far more than those).
    - `feature: worker-instructions` holds 33 items whose declared work *is*
      editing a `.claude` file, and `gate_paths` covers `.claude` (`PL-69JZ`).
    - An item non-delegable *because* it touches `core/` is one a session
      works itself, so `protected_paths` is expected on its branch.
    - The close-out sets `status: done` and `closed:` in the same commit as
      the work, which is exactly the front matter the guard watches
      (`PL-B5YN`).

    So in self-audit the four **commission** checks report as advisories -
    still printed, still naming every path, with the reason they are not
    refusing - while the four **integrity** checks stay absolute: no
    suppression added and the item's own command passes, here, and, once for
    the branch in `verify`, the unit tests catch a mutation of each changed
    line and the project's own checks pass. That line is the whole design. A
    session may legitimately re-scope its own commission; it may not weaken
    the thing that measures it, and it may not skip the test.

    The command check has a **declared** exemption, which is not a relaxation
    of that line but the reason it can stay absolute. Which copy of the item
    each field behind it is read from follows one rule, stated on
    `Commission`: an outcome is the branch's and excuses nothing, a prediction
    is measured against the base's with the branch's correction run and
    printed, a waiver is the base's (`PL-B8HZ`).

    - A `dropped` item, or one carrying `not-delegable:`, has no command to
      run by construction, and the command check reports which applies
      (`PL-L4KX`). A dropped item that still carries one has it printed and
      not run, since it names work the drop says will not be done
      (`PL-BX1C`). The drop is an outcome, read off the *branch's* copy as it
      has to be: it is what the close-out writes, and it grants nothing - it
      claims no work. A delegated audit refuses a worker's drop through the
      front-matter check; `--self` only reports it. The reason is a waiver
      and is held to the base's copy: it excuses a command the base never
      commissioned, never one the branch deleted, so it cannot be written
      beside the deletion to skip the test (`PL-KSV2`).
    - `verify:` and `touches:` are predictions, and the branch's copy of each
      is honoured as a correction rather than substituted silently. The
      command the branch records decides its check, with the base's command
      run and its exit printed under it where the two differ (`PL-PZ6T`),
      and the diff is measured against the base's `touches` with a path only
      the branch's own widening declares named as that.

    Without them the absolute checks had no passing route on close-outs the
    project's own instructions prescribe, and a session meeting one could only
    game the fold or push through a red integrity check. Either sets the
    precedent the split exists to prevent.

    The alternative was to relax the guards for everyone, which would have
    made the delegated audit - the case the command exists for - quietly
    weaker. `PL-69JZ` had already been routed around instead: `bin/docket
    triage` tells a groomer that a `touches` naming a gate path makes the item
    non-delegable, "because `docket verify` fails any diff that edits the
    checks, so offering the work would mean refusing it once done". That is a
    defect absorbed into policy, and this is the repair.

    What this reads from the item's own command (`PL-6TP8`): exit 0 is the
    commission's assertion holding, and every other status is a `REJECT` with
    the reason on the line where the run can name it - re-entered `docket
    verify`, selected no test, killed at the limit, or the command's own last
    lines. Unlike `already_passing` this may not decline: the command is the
    thing being asked about, so "could not run it" rejects the work rather than
    abstaining. What exit 0 does not prove is that the work is right;
    `mutation_check`, `project_check` and the reviewer's reading of the diff
    carry that.

    **A read git did not answer ends the audit, and never passes it**
    (`PL-9RFP`). Every check here is a claim about what the branch changed,
    so an audit that could not read the change has nothing to report. Before
    this, a base that did not resolve came back as git's error text: the
    commission check named that text as an edit, and both integrity checks
    passed on a diff they never saw. So a self-audit whose command passed
    would ACCEPT having read nothing.
    """
    report = Verification(item=item, base=base, base_note=base_note)
    try:
        return _check_item(report, root, item, config, base, self_audit)
    except GitUnanswered as silence:
        report.checks.append(
            Check(
                "the diff could be read",
                False,
                "git did not answer the read below, so no later check ran",
                (str(silence),),
            )
        )
        report.stopped_early = True
        return report


def _check_item(
    report: Verification, root: Path, item: Item, config: Config, base: str, self_audit: bool
) -> Verification:
    """The checks `verify_item` documents, appended to `report` as each runs.

    Separate so that a git read that did not answer is caught in one place,
    whichever check it came from, including a check added later. The report
    is passed in rather than built here because the checks that ran before
    the failure did run, and the reader is owed them.
    """
    commits = item_commits(root, base, item.identifier)
    paths = changed_paths(root, base, commits)

    # "No command recorded" means the test was skipped, except in the two
    # states where the store has already decided that no command can exist. A
    # `dropped` item built nothing, so there is nothing for a command to prove;
    # a `not-delegable` reason is what `docket check` accepts *instead of* a
    # command, in those words. Refusing both here made the two tools disagree
    # about the same item - `check` clean, `verify --self` REJECT - and left the
    # close-out the skill prescribes with no passing state at all, since writing
    # a `verify:` onto a closed item is separately refused (`PL-L4KX`,
    # `PL-JZ1D`).
    #
    # Read off the store rather than taken on the session's word, and neither
    # state is free to reach for: a drop is a closure that owes a `reason` and a
    # `closed` date, and a `not-delegable` line is the thing that withholds the
    # item from delegation in the first place. `Commission` states which copy
    # each is read from. The drop is an *outcome* and is the branch's: the
    # close-out is what writes it, and it claims no work for a command to
    # prove. The reason is a *waiver* and waives only what the base holds: it
    # excuses a command the commission never held, and never one the branch
    # removed. Read off the branch alone, it let a close-out delete its failing
    # command, write a reason beside the deletion and ACCEPT with the command
    # never run - and a reason can say who should do the work rather than that
    # nothing can prove it (`PL-KSV2`). A base that cannot be read excuses
    # nothing, since the waiver turns on what it holds.
    #
    # Advisory unconditionally rather than under `self_audit`, because what
    # excuses the command is a fact about the item and not about who is asking.
    # And it does not stop early: that no command was recorded says nothing
    # about whether the diff stayed inside `touches` or whether a suppression
    # arrived, which is the half a hard stop was throwing away.
    commission = read_commission(root, base, config.items_dir, item)
    exemption, missing = "", "none recorded"
    unexcused: tuple[str, ...] = ()
    if item.status == "dropped":
        exemption = "a dropped item built nothing, so no command can prove it"
    elif item.not_delegable and commission.unread:
        missing += (
            f": the `not-delegable:` reason excuses a command only where {base} "
            f"commissioned none, and {commission.unread}"
        )
    elif item.not_delegable and commission.verify:
        missing += (
            f": this branch deleted the command {base} commissions, so the "
            "`not-delegable:` reason beside the deletion is the branch's own word "
            "for skipping it"
        )
        unexcused = (
            f"{base} commissions: {commission.verify}",
            "restore it, or give the command that proves the work; where none can, "
            f"that is {base}'s copy to say, not this branch's",
        )
    elif item.not_delegable:
        exemption = f"the item records why no command can prove it - {item.not_delegable}"
    elif not item.is_open and done.dated_record(item.body):
        exemption = "the item's brief holds a dated paragraph that states its result"
    if not item.verify and not item.tests:
        if item.is_open and not unexcused:
            # The tests that show the work are named when the item closes
            # (`PL-FN11`), so an open item's branch has nothing to read yet.
            exemption = exemption or (
                "the item is still open, and the tests that show its work are named when "
                "it closes, where `docket check` reads them"
            )
        if not exemption:
            report.checks.append(Check(SHOWS_ITS_WORK, False, missing, unexcused))
            report.stopped_early = True
            return report
        report.checks.append(
            Check(SHOWS_ITS_WORK, False, f"none recorded: {exemption}", advisory=True)
        )

    # An empty diff is not verified work. Every path check below would pass on
    # nothing at all, and the report would read ACCEPT for a branch carrying no
    # change - which a mistyped or stale base makes easy to reach, and which is
    # exactly where a confident green does the most harm.
    if not paths:
        report.checks.append(
            Check(
                "there is something to verify",
                False,
                f"nothing to verify: no change between {base} and HEAD"
                + (f", and no commit naming {item.identifier}" if not commits else ""),
            )
        )
        report.stopped_early = True
        return report

    # The item's own file is always in scope: a worker is asked to append a
    # `**Worked.**` note to it, and `path` is a bare filename rather than a
    # repository path, so it is matched by basename.
    own_file = Path(item.path).name if item.path else ""
    # `touches:` is a *prediction*, and the base's copy is the commission the
    # diff is measured against where the base holds one. The branch's copy is
    # its correction: the declaration itself where the base commissions no
    # scope, and a widening named on the page where it does, so a path only the
    # branch's own widening declares is reported as that rather than passing
    # silently (`PL-B8HZ`). A delegated audit refuses the widening as an edit
    # to the front matter; `--self` reports it, as it reports every commission
    # check.
    scope = commission.touches or item.touches
    candidates = [p for p in paths if not is_under(p, scope) and Path(p).name != own_file]
    # An edit the workflow itself asked for is separated from the rest rather
    # than excused silently: the audit says which paths it declined to count
    # and why, so a reader can disagree with the exemption (`PL-66PR`,
    # `PL-ZYQC`). Only paths under the store, the body files (`PL-3PH2`) and
    # the worker run records (`PL-4WFK`) are even considered.
    sanctioned = {
        path: kind
        for path in candidates
        if (
            kind := sanctioned_queue_edit(root, base, commits, path)
            if is_under(path, (config.items_dir, RECORDS))
            else "run record"
            if worker_run_record(root, base, config.worker_runs_dir, item.identifier, path)
            else ""
        )
    }
    outside = [path for path in candidates if path not in sanctioned]
    # Said, since a write the workflow asks for reads as sanctioned once it is
    # committed, and the page would otherwise not say why it is not (`PL-W6ZD`).
    unsanctioned = {
        path
        for path in set(vcs.uncommitted_paths(root, _git)).intersection(outside)
        if is_under(path, (config.items_dir, RECORDS, config.worker_runs_dir))
    }
    widened = [path for path in outside if commission.touches and is_under(path, item.touches)]
    if outside:
        detail = f"{len(outside)} path(s) outside"
        if widened:
            detail += (
                f", {len(widened)} of them declared only by this branch's own widening of `touches`"
            )
    else:
        # Say what is true rather than what is shaped like an answer. `commits`
        # is empty when no commit on the branch names this item, and the paths
        # then come from the branch diff and the working tree - so the `or 1`
        # here reported "1 commit(s)" for a branch carrying none, at the one
        # moment a session most needs a truthful answer about what it has
        # committed. The wording matches the empty-diff check above, which
        # already says "no commit naming <id>" (`PL-NB4D`).
        if commits:
            detail = f"{len(paths)} path(s) in {len(commits)} commit(s), all declared"
        else:
            detail = f"{len(paths)} path(s), no commit naming {item.identifier}, all declared"
        if sanctioned:
            kinds = Counter(sanctioned.values())
            detail += " or a sanctioned edit ({})".format(
                ", ".join(f"{count} {kind}" for kind, count in sorted(kinds.items()))
            )
    report.checks.append(
        Check(
            "diff stayed inside `touches`",
            not outside,
            detail + (COMMISSION_NOTE if outside and self_audit else ""),
            tuple(
                f"{path} - declared by this branch's `touches` and not by {base}'s copy"
                if path in widened
                else f"{path} - uncommitted, and only a commit's change can be a sanctioned edit"
                if path in unsanctioned
                else path
                for path in outside
            )
            + tuple(f"{path} - {kind}, not counted" for path, kind in sanctioned.items()),
            advisory=self_audit,
            commission=True,
        )
    )

    # Said once, beside the check whose reach it widens. Silent when the
    # commits name this item alone, which is the delegated case and the one
    # the scoping was built for.
    others, carrying = other_items_named(root, commits, item.identifier)
    if others:
        report.checks.append(
            Check(
                "the audited diff is this item's alone",
                False,
                f"{carrying} of {len(commits)} commit(s) also lead with {', '.join(others)}, "
                "so the paths above are the batch's rather than this item's",
                advisory=True,
            )
        )

    protected = [p for p in paths if is_under(p, config.protected_paths)]
    report.checks.append(
        Check(
            "no protected path modified",
            not protected,
            (", ".join(protected) + COMMISSION_NOTE)
            if protected and self_audit
            else (", ".join(protected) if protected else "none touched"),
            advisory=self_audit,
            commission=True,
        )
    )

    gates = [p for p in paths if is_under(p, config.gate_paths)]
    report.checks.append(
        Check(
            "the checks themselves are unedited",
            not gates,
            (", ".join(gates) + COMMISSION_NOTE)
            if gates and self_audit
            else (", ".join(gates) if gates else "none touched"),
            advisory=self_audit,
            commission=True,
        )
    )

    # Each Python file is read as statements rather than lines, and as lines
    # only where its statements could not be read (`PL-CFWP`). Whether the
    # branch's tests still catch a change is not read from the diff at all:
    # `mutation_check` runs mutants of the changed lines, once per run, beside
    # the project's own check (`PL-CZXN`).
    added = _net_line_changes(root, base, commits)
    report.checks.append(suppression_check(added_suppressions(root, base, commits, added)))

    report.checks.append(
        front_matter_check(root, base, config.items_dir, item, advisory=self_audit)
    )

    # What a closed item records is read against the branch, as `docket check`
    # reads it: the tests it names, or its one search for fixed text
    # (`PL-FN11`, `PL-N046`). No command is run.
    if item.status == "done" and (item.tests or item.verify):
        fork = vcs.texts_at_fork(root, done.node_paths([item]), base=base)
        faults, unread = done.closing_faults(item, root, fork)
        if fork.declined and item.tests:
            unread.insert(0, fork.declined)
        report.checks.append(
            Check(
                RECORD_SHOWS_WORK,
                not faults and not unread,
                ", ".join(item.tests) or item.verify,
                (*faults, *(f"not read: {reason}" for reason in unread)),
            )
        )
    return report


#: The check that what a closed item records shows its work on the branch.
RECORD_SHOWS_WORK = "the recorded tests or search show the work"
#: The check that an item records something to show its work: the tests it
#: added, in `tests:`, or a command, in `verify:` (`PL-FN11`).
SHOWS_ITS_WORK = "records what shows its work"
#: The mutation check's name on the page.
MUTATION_CHECK = "the unit tests catch a mutation of each changed line"
#: How long the mutation run may take before the check says it has no answer.
#: On four cores on 2026-10-24 a run spent about five minutes before its first
#: mutant, eight minutes on 186 mutants, and 36 minutes on 340, the largest
#: batch of the 40 merges since 2026-10-01 that changed a mutated function.
#: Two hours leaves room for a larger one, and for a busier machine, while a
#: run that never ends still ends the check.
MUTATION_TIMEOUT_S = 7200.0


@dataclass(frozen=True)
class MutationVerdict:
    """What `mutation_command` printed, in the shape its contract names.

    `uncaught` and `undecided` hold one entry per mutant of a changed line, as
    the command wrote it for a reader; an entry may run over several lines.
    `caught` counts the mutants the tests caught. `notes` says what the run did
    not measure.
    """

    caught: int
    uncaught: tuple[str, ...]
    undecided: tuple[str, ...]
    notes: tuple[str, ...]


def read_verdict(text: str) -> MutationVerdict:
    """The verdict `text` holds, or `ValueError` where it is not the shape the contract names.

    Refused rather than read as far as it goes: a verdict missing its
    `uncaught` list would otherwise read as one in which every mutant was
    caught.
    """
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("the output is not a JSON object")
    caught = data.get("caught")
    if not isinstance(caught, int) or isinstance(caught, bool) or caught < 0:
        raise ValueError("`caught` is not a count")
    lists: dict[str, tuple[str, ...]] = {}
    for key in ("uncaught", "undecided", "notes"):
        value = data.get(key)
        if not isinstance(value, list) or not all(isinstance(entry, str) for entry in value):
            raise ValueError(f"`{key}` is not a list of strings")
        lists[key] = tuple(value)
    return MutationVerdict(caught, lists["uncaught"], lists["undecided"], lists["notes"])


def mutation_check(root: Path, config: Config, base: str) -> Check:
    """Whether the unit tests catch a mutation of each line the branch changed (`PL-CZXN`).

    This replaced the check that no existing assertion was removed, which read
    the diff's text to decide whether the branch weakened its tests. It refused rewrites the
    work was meant to make, and sessions waived about 15 of its 17 refusals
    since 2026-10-01, which teaches a reader to skim past a `REJECT`. A mutant
    asks the question by behaviour instead: alter a line the branch changed,
    and see whether a test fails (project owner, 2026-10-19, ratified, over
    making the old check an advisory and over keeping it). Nothing here reads
    the diff, so no reading of its text can be wrong.

    `mutation_command` owns what a mutant is and when the tests caught one,
    because the mutation tool is the project's. The package appends the base
    as the last argument, and the command owes exit 0 and one JSON object:
    `caught`, a count, and `uncaught`, `undecided` and `notes`, each a list of
    strings. The check passes only where `uncaught` and `undecided` are both
    empty. A command that exits non-zero, runs past `MUTATION_TIMEOUT_S`, or
    prints anything else has given no answer, and the check refuses, because
    "could not measure" is not "measured, and all caught".

    Run once per `verify` run, beside `project_check`, because the answer is a
    property of the branch and not of one item. Empty by default, which turns
    the check into a note saying nothing measured the tests: docket names no
    mutation tool, so the project supplies one.
    """
    if not config.mutation_command:
        return Check(
            MUTATION_CHECK,
            False,
            "not run: `docket.toml` sets no `mutation_command`, so nothing measured whether "
            "the tests catch a change to the branch's lines",
            advisory=True,
        )
    command = f"{config.mutation_command} {shlex.quote(base)}"
    status, out, err = _run([command], root, shell=True, timeout=MUTATION_TIMEOUT_S)
    if status == TIMED_OUT:
        return Check(
            MUTATION_CHECK,
            False,
            f"no answer: `{command}` did not finish in {MUTATION_TIMEOUT_S / 60:.0f} minutes",
        )
    if status != 0:
        return Check(
            MUTATION_CHECK,
            False,
            f"no answer: `{command}` exited {status}",
            failure_evidence(out, err),
        )
    try:
        verdict = read_verdict(out)
    except ValueError as error:
        return Check(
            MUTATION_CHECK,
            False,
            f"no answer: `{command}` printed no verdict the check can read ({error})",
            failure_evidence(out, err),
        )
    if verdict.uncaught:
        detail = f"{len(verdict.uncaught)} mutant(s) of changed lines not caught"
        if verdict.undecided:
            detail += f", and {len(verdict.undecided)} undecided"
    elif verdict.undecided:
        detail = (
            f"no answer for {len(verdict.undecided)} mutant(s) of changed lines, so whether "
            "the tests catch them is not known"
        )
    elif verdict.caught:
        detail = f"{verdict.caught} mutant(s) caught, and none on a changed line missed"
    else:
        detail = "no mutant of a changed line to run"
    lines = [
        line
        for entry in (*verdict.uncaught, *verdict.undecided, *verdict.notes)
        for line in split_lines(entry)
    ]
    return Check(
        MUTATION_CHECK, not verdict.uncaught and not verdict.undecided, detail, tuple(lines)
    )


def project_check(root: Path, config: Config) -> Check:
    """Run the project's own full check once, whoever is asking.

    Shared evidence rather than per-item evidence: it says the tree is sound,
    which is a property of the tree. Every report a batch produces carries the
    same result because it is the same result.
    """
    status, out, err = _run([config.check_command], root, shell=True)
    return Check(
        "the project's own checks pass",
        status == 0,
        config.check_command,
        () if status == 0 else failure_evidence(out, err),
    )


def verify(
    root: Path, item: Item, config: Config, base: str, self_audit: bool = False
) -> Verification:
    """Run every check against one item's branch, the branch-wide two included."""
    report = verify_item(root, item, config, base, base_warning(root, base), self_audit)
    if not report.stopped_early:
        report.checks.append(mutation_check(root, config, base))
        report.checks.append(project_check(root, config))
    return report


def verify_batch(
    root: Path, items: Sequence[Item], config: Config, base: str, self_audit: bool = False
) -> list[Verification]:
    """Verify several items, running the mutation run and the project's own check once each.

    The item's own command still runs per item, because that is what makes
    each one individually acceptable or rejectable - a batch that could only
    be taken or refused whole would hand the reviewer back the all-or-nothing
    choice that one-commit-per-item exists to remove.
    """
    note = base_warning(root, base)
    reports = [verify_item(root, item, config, base, note, self_audit) for item in items]
    outstanding = [report for report in reports if not report.stopped_early]
    if outstanding:
        shared = (mutation_check(root, config, base), project_check(root, config))
        for report in outstanding:
            report.checks.extend(shared)
    return reports
