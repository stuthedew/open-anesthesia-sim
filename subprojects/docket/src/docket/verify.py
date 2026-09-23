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
import os
import re
import shlex
import subprocess
import tempfile
import time
import warnings
from collections import Counter
from collections.abc import Collection, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from . import vcs
from .config import Config
from .model import CLOSED_STATUSES, WITHDRAWN_MARKER, Item, parse_front_matter
from .store import ID_PATTERN

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
# files`, which covered 11 of the 56, and `tools/ignore_check.py` runs the
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
# after `from pytest import mark` is read too - the reason the assertion check
# matches a bare `raises`. `unittest.skip` reads the standard library's
# decorators, `skipIf` and `skipUnless` included. A widening owes the count a
# narrowing does, in the other direction. Replayed on 2026-09-22 over `main`'s
# 1,115 non-merge commits, of 1,232, the list before these two matched no
# added line at all, and the two add exactly one: the `@pytest.mark.skipif`
# that `tests/unit/test_stop_hook_patch.py` puts on a test needing `bash`. It
# is real - an environment guard rather than a test silenced to reach green,
# which is a reviewer's call and is now put in front of one. No prose line
# matched in any suffix the check reads, `.toml`, `.cfg` and `.ini` included.
#
# Still unread, and absent from that history too: `pytest.importorskip`,
# `unittest.expectedFailure`, `self.skipTest`, a raised `unittest.SkipTest` and
# `collect_ignore` in a `conftest.py` (`PL-DNZ0`). A deselection in `addopts`
# is configuration: in `pyproject.toml`, one of `gate_paths`' defaults, the
# gate check reads it, and in a `.cfg` or `.ini` file nothing does.
SUPPRESSIONS = (
    "typing.no_type_check",
    "xfail",
    "pytest.skip",
    "@skip",
    "mark.skip",
    "unittest.skip",
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
#: `@skipif`, `mark.skip` finds `mark.skipif` and `unittest.skip` finds
#: `skipIf` and `skipUnless`, each of which is the thing this looks for rather
#: than a collision with it.
_SUPPRESSION_RE = re.compile(
    "|".join(
        (r"\b" if text[0].isalnum() or text[0] == "_" else "") + re.escape(text)
        for text in SUPPRESSIONS
    )
)

#: Where a suppression can genuinely live, for `no suppression added`. The
#: sibling assertion check below narrows the same way and to a narrower set,
#: and the difference is the reasoning rather than an oversight: an assertion
#: is a *statement*, so only a file Python executes holds one, while a
#: suppression is also *configured*. `xfail_strict = false` under
#: `[tool.pytest.ini_options]` turns every expected failure back into a pass,
#: and a `.pyi` stub carries a file-level ignore directive, neither of which
#: changes a line of `.py`. So this list is that one plus the files that
#: configure a run, and reusing `ASSERTION_BEARING_SUFFIX` here would have
#: carried the sibling's rule past the argument that earned it.
#:
#: Counted before it was written, because this narrows a check whose safe
#: direction is reporting: over 1,109 commits of this repository, the added
#: lines `_SUPPRESSION_RE` matches are 69 in `.py` and 41 in `.md`, and **no
#: other suffix carries one at all**. So the tuple reports every match the
#: history has ever held, and what it stops reading is 41 lines of prose -
#: a release note, an item brief, or the `ROADMAP.md` version row that
#: REJECTed every release cut (`PL-5MFL`, `PL-BHBZ`).
SUPPRESSION_BEARING_SUFFIXES = (".py", ".pyi", ".toml", ".cfg", ".ini")


#: The suffixes whose non-code spans are stripped below - narrower than
#: `SUPPRESSION_BEARING_SUFFIXES`, and deliberately so. In a `.cfg` or `.ini`
#: a quote is an ordinary character in a value and an inline `#` is part of
#: that value under `configparser`'s defaults, so the same strip would delete
#: configuration rather than prose. Counted rather than assumed: across 1,004
#: non-merge commits every line the pattern has ever matched is `.py`, and no
#: `.toml`, `.cfg` or `.ini` line has matched it in either direction - so a
#: rule for them would be the widest one the hazard could motivate rather than
#: the narrowest that removes it.
QUOTING_SUFFIXES = (".py", ".pyi")

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
#: the markup is the only evidence left on the line.
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
NON_CODE_RE = re.compile(
    r'"""(?:[^"\\]|\\.|"(?!""))*"""'  # a triple-quoted span opening and closing on one line
    r"|'''(?:[^'\\]|\\.|'(?!''))*'''"
    r'|"(?:[^"\\\n]|\\.)*"'
    r"|'(?:[^'\\\n]|\\.)*'"
    r"|`[^`]*`"  # a backtick span: prose markup, and never Python
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
    as one. That is the same defect `PL-7TYC` removed from the sibling
    assertion check and it was left standing here, on the one check `--self`
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

    An unreadable diff header yields `""`, which stays on the reporting side
    exactly as `is_assertion_line` keeps it: where the file cannot be
    identified, the line is printed rather than guessed at - and unstripped
    for the same reason, since the strip is what a known Python file earns.
    """
    if path and not path.endswith(SUPPRESSION_BEARING_SUFFIXES):
        return False
    if path.endswith(QUOTING_SUFFIXES):
        line = strip_non_code(line)
    return bool(_SUPPRESSION_RE.search(line))


#: Only a file Python executes can hold an assertion, so a removed line from
#: anything else is prose whatever words it uses. This is the larger half of
#: the narrowing by count: every close-out edits its own item's `.md`, and
#: every release edits `ROADMAP.md`, so the documentation tree is where a
#: substring grep over the word `assert` met a session most often.
ASSERTION_BEARING_SUFFIX = ".py"

#: What an assertion *statement* looks like on the line that opens it.
#: `assert` is a keyword, so it opens its statement: even one wrapped across
#: five lines carries the keyword on the first, which is the line a
#: whole-statement deletion puts in the diff - so anchoring gives up none of
#: the wrapped forms, which is what the item asked to be checked rather than
#: assumed. The second alternative is the call form, which the keyword anchor
#: cannot see because the name runs on: `unittest`'s `assertEqual`, `mock`'s
#: `assert_called_once_with`, `numpy.testing`'s `assert_allclose`.
#:
#: The third asserts by *expectation* and carries the word nowhere:
#: `with pytest.raises(ValueError):` says the block inside must fail, which is
#: how this project pins every guard that *rejects* an input - so the
#: assertions the two alternatives above cannot see are disproportionately the
#: safety ones (`PL-QJQL`). `with` opens its statement exactly as `assert`
#: does, so the same anchor carries it, and here the anchor is load-bearing
#: rather than symmetry: `raises` and `warns` are ordinary English verbs which
#: this tree's own prose uses, so unanchored they reintroduce what `PL-7TYC`
#: spent a narrowing removing. Two details of that alternative are deliberate
#: for the same reason. `[^#]*` keeps the match out of a trailing comment, so
#: an unrelated `with open(path):` whose comment mentions the word is not an
#: assertion; and the `(` follows the name directly, because `ruff format`
#: never separates a callable from its parenthesis while prose does - "the
#: guard raises (ValueError)" is a sentence, not a call.
ASSERTION_RE = re.compile(
    r"(?:^|[:;])\s*assert\b"  # `assert x`, and the one-liner `if cond: assert x`
    r"|\bassert[A-Za-z0-9_]*\s*\("  # assertEqual(, assert_called_once_with(
    r"|(?:^|[:;])\s*(?:async\s+)?with\b[^#]*\b(?:raises|warns)\("  # with pytest.raises(...)
)

#: Positions the word occupies where no assertion is being made. A comment and
#: a decorator cannot assert; a `def` names a helper rather than calling one,
#: and removing that definition removes its call sites too, which the call
#: form above catches; an import moves a name without evaluating it.
NOT_AN_ASSERTION_RE = re.compile(r"^\s*(?:#|@|def\s|async\s+def\s|import\s|from\s)")


def is_assertion_line(path: str, line: str) -> bool:
    """Whether a removed line was an assertion, in a file this interpreter cannot parse.

    **The fallback, no longer the check.** `no existing assertion removed`
    reads statements with `ast` (`removed_assertions`, `PL-4W2L`). This reads
    only a file some version of which the running interpreter cannot parse -
    `bin/docket` runs on the bare `python3`, which can be older than the
    project's own - and the file is named on the page as read this way. What
    follows is the history of the predicate as it was when it was the check,
    kept because the counts are what its shape rests on.

    The check used to ask `"assert" in line`, which is true of a comment, a
    docstring, a release note, an item's brief, a variable called
    `removed_assertions` and of the matcher itself - so a correct close-out
    that touched any of them was REJECTed by an integrity check that is
    supposed to be unarguable, which is the second of `CLAUDE.md`'s
    compounding-friction tests: a refusal that fires on correct work trains a
    reader to skim the block where a real weakening is printed (`PL-7TYC`).

    Counted rather than reasoned about, because the safe direction here is
    *reporting* and a tightening has to earn it. The predicate is wrong if it
    suppresses a real assertion, so that is what was counted, three ways, with
    `ast` as the oracle rather than a reading:

    - over 867 commits of this repository's history, 200 removed lines carrying
      the word stop being reported and **none** of them is an assertion;
    - across the test trees, where the check is aimed, 271 of 5,574 lines stop
      being reported and **none** of them is an assertion - 229 prose, 37
      comments, 5 definitions or imports;
    - in non-test source the exposure the item measured falls from 91 lines to
      4, one of which is a genuine `assert` that is meant to be reported.

    It still errs toward reporting where it cannot tell: three of those four
    are docstring lines that a reflow happened to start with the word
    `assert`, and they stay on the page rather than being guessed at.

    `PL-QJQL` widened it once, in the opposite direction and on the same
    evidence, because a narrowing and a widening are the same claim about what
    an assertion is. `with pytest.raises(...)` asserts without carrying the
    word, so the 227 of them in this tree - every compartment-rejection guard
    among them - could be deleted whole and reported as none removed. Counted
    the same way before the alternative was added, with `ast` as the oracle:
    227 lines in the tree and 60 removed lines across 902 commits of history
    start being reported, and **every one** of the 287 is a genuine
    `with raises/warns(...)` statement, so the widening refuses no work this
    repository has ever done.

    Two shapes a line cannot carry are left to the parser, which reads both:
    the parenthesized multi-manager form, where `with (` opens the statement
    and the `pytest.raises(...)` item sits on a line of its own with no `with`
    on it (`PL-XQGH`), and an edit on a continuation line of a wrapped
    assertion, which carries none of the three shapes at all. In a file read
    this way both are still missed, and the page says the file was read so.
    """
    if path and not path.endswith(ASSERTION_BEARING_SUFFIX):
        return False
    if NOT_AN_ASSERTION_RE.match(line):
        return False
    return bool(ASSERTION_RE.search(line))


#: The context managers that assert by expectation, matched on the name they
#: are called by - `pytest.raises`, or `raises` after `from pytest import
#: raises` - which is the spelling the line predicate above has always read.
EXPECTING = ("raises", "warns")

#: How the parser splits source into lines, which is not `str.splitlines`: a
#: form feed or a line separator inside a string is one line to the parser and
#: two to `splitlines`, and a column offset read against the wrong split points
#: into the wrong text.
PARSER_LINE_RE = re.compile(r"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+\Z")


@dataclass(frozen=True)
class Assertion:
    """One assertion as `ast` reads it, which is the unit the check compares.

    `form` is what makes it that assertion: its kind and the `ast.dump` of the
    expression that asserts. A dump carries no position, spacing, quoting,
    wrapping or comment, so reformatting an assertion, wrapping it or moving it
    within its file leaves the form as it was - and any edit to what it
    asserts changes it, on whichever line of a wrapped statement the edit
    falls. An `assert`'s message is left out, because the message asserts
    nothing.
    """

    form: str
    #: The classes and functions around it, joined as pytest joins a node id -
    #: `TestX::test_y` - or "" at module level. Context for the report only:
    #: moving an assertion between functions is not a change.
    where: str
    #: Its source as written: the whole statement for an `assert`, the call
    #: for the other two kinds. `falsifies:` is matched against this.
    source: str
    #: The same on one line, as the report prints it.
    shown: str


@dataclass(frozen=True)
class AssertionReading:
    """What one version of one file asserts, and the classes and functions it defines."""

    assertions: tuple[Assertion, ...] = ()
    defines: frozenset[str] = frozenset()

    def forms(self) -> Counter[str]:
        return Counter(assertion.form for assertion in self.assertions)


def _called(func: ast.expr) -> str:
    """The name a call is made by: `f` for `f(...)`, `m` for `x.y.m(...)`."""
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _segment(lines: Sequence[str], node: ast.expr | ast.stmt) -> str:
    """`ast.get_source_segment`, over lines split once rather than once per call.

    The standard library's re-splits the whole source on every call, character
    by character, which is quadratic in a test file's assertions: a 3,000-line
    test module holds a thousand of them. Column offsets are UTF-8 byte
    offsets, which is why each line is encoded before it is cut.
    """
    first, last = node.lineno - 1, (node.end_lineno or node.lineno) - 1
    start, end = node.col_offset, node.end_col_offset or 0
    if first == last:
        return lines[first].encode()[start:end].decode(errors="replace")
    head = lines[first].encode()[start:].decode(errors="replace")
    tail = lines[last].encode()[:end].decode(errors="replace")
    return "".join([head, *lines[first + 1 : last], tail])


def read_assertions(source: str) -> AssertionReading:
    """Every assertion `source` holds, as `ast` reads it.

    Three kinds, which are the three shapes the line predicate above matched:
    an `assert` statement, a call whose name begins `assert` - `assertEqual`,
    `assert_called_once_with`, `assert_allclose` - and a `raises` or `warns`
    item of a `with`, which asserts by expectation and carries the word
    nowhere. The third is read wherever the formatter puts it, which a line
    could not do: in the parenthesized multi-manager form the item sits on a
    line of its own with no `with` on it (`PL-XQGH`).

    Raises what `ast.parse` raises - `SyntaxError`, or `ValueError` for a null
    byte - and `RecursionError` for an expression too deep to dump, so that the
    caller can read the file another way and say that it did.
    """
    with warnings.catch_warnings():
        # Compiling warns on an invalid escape sequence. That is the file's
        # linter's to report, and a verify report is the wrong page for it.
        warnings.simplefilter("ignore")
        tree = ast.parse(source)
    lines = PARSER_LINE_RE.findall(source)
    found: list[Assertion] = []
    defines: set[str] = set()

    def keep(
        kind: str, asserting: ast.AST, written: ast.expr | ast.stmt, where: str, prefix: str = ""
    ) -> None:
        text = _segment(lines, written)
        found.append(
            Assertion(f"{kind}:{ast.dump(asserting)}", where, text, prefix + " ".join(text.split()))
        )

    # An explicit stack rather than recursion, and children pushed reversed so
    # they come off in source order: the report lists what it found in the
    # order a reader meets it in the file.
    stack: list[tuple[ast.AST, str]] = [(tree, "")]
    while stack:
        node, where = stack.pop()
        if isinstance(node, ast.Assert):
            keep("assert", node.test, node, where)
        elif isinstance(node, ast.Call) and _called(node.func).startswith("assert"):
            keep("call", node, node, where)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                expr = item.context_expr
                if isinstance(expr, ast.Call) and _called(expr.func) in EXPECTING:
                    keep("with", expr, expr, where, "with ")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            where = f"{where}::{node.name}" if where else node.name
            defines.add(where)
        stack.extend((child, where) for child in reversed(list(ast.iter_child_nodes(node))))
    return AssertionReading(tuple(found), frozenset(defines))


@dataclass(frozen=True)
class FileAbsence:
    """The existing assertions one file lost to the item's own commits."""

    #: The file as the base names it. A commit that renamed it is followed, as
    #: `git show` follows it for every other check here, so a renamed test
    #: module is compared with its old self rather than charged in full.
    path: str
    #: Its name after the item's commits, where one of them renamed it.
    renamed_to: str
    #: Each form gone, and how many of the base's copies of it went, in the
    #: order the base's copy of the file holds them.
    charged: tuple[tuple[str, int], ...]
    #: The base's copy, and the copy after the last of the item's commits to
    #: touch the file - what the report pairs nothing between.
    before: AssertionReading
    after: AssertionReading


@dataclass(frozen=True)
class AssertionAudit:
    """What the item's own commits did to the assertions the base holds."""

    absent: tuple[FileAbsence, ...] = ()
    #: Files a version of which this interpreter could not parse, and why.
    #: Each is read line by line instead, and named on the page as read so.
    unparsed: tuple[tuple[str, str], ...] = ()
    #: The removed lines from those files that `is_assertion_line` flags and
    #: that the base's copy holds, as `(path, line)`.
    lines: tuple[tuple[str, str], ...] = ()
    #: Why nothing could be read, where that is the answer. The check refuses
    #: on it: "could not look" is not "looked, found nothing".
    unread: str = ""


def _short(spec: str) -> str:
    """The revision half of a `<rev>:<path>` spec, a full object id abbreviated."""
    revision = spec.partition(":")[0]
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
        result = subprocess.run(
            ["git", "cat-file", "--batch"],
            cwd=root,
            input="".join(f"{spec}\n" for spec in ordered).encode(),
            capture_output=True,
            timeout=600,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    out, at = result.stdout, 0
    found: dict[str, tuple[str, bytes] | None] = {}
    for spec in ordered:
        end = out.find(b"\n", at)
        if end < 0:
            return None
        fields = out[at:end].split()
        at = end + 1
        if fields[-1:] in ([b"missing"], [b"ambiguous"]):
            found[spec] = None
            continue
        if len(fields) != 3 or not fields[2].isdigit():
            return None
        size = int(fields[2])
        body = out[at : at + size]
        at += size + 1  # git ends every object with a newline
        # A tree or a submodule at the path is not a file an assertion lives in.
        found[spec] = (fields[0].decode(), body) if fields[1] == b"blob" else None
    return found


@dataclass(frozen=True)
class _FileStep:
    """One commit's change to one file, as the fold reads it."""

    key: str
    #: The file in each parent, as a blob spec, or "" where that parent has none.
    before: tuple[str, ...]
    #: The file after the commit, or "" where the commit deleted it.
    after: str


def _changed_python(listing: str, statuses: bool) -> list[tuple[str, str]]:
    """`(old, new)` for each `.py` file in a `-z` listing, "" for a side that is not one."""
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
        pair = (old if old.endswith(".py") else "", new if new.endswith(".py") else "")
        if any(pair):
            pairs.append(pair)
    return pairs


def _file_steps(
    root: Path, base: str, commits: tuple[str, ...]
) -> tuple[list[_FileStep], dict[str, str], str]:
    """The item's changes to `.py` files, oldest first, and what each file is keyed by.

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
        status, listing = _run(["git", "show", "-s", "--format=%H %P", *commits], root)
        if status != 0:
            return [], {}, f"the parents of {len(commits)} commit(s) could not be read"
        parents_of = {
            fields[0]: tuple(fields[1:])
            for fields in (line.split() for line in listing.splitlines())
            if fields
        }
        revisions = [(commit, parents_of.get(commit, ())) for commit in reversed(commits)]
    else:
        status, fork = _run(["git", "merge-base", base, "HEAD"], root)
        if status != 0:
            return [], {}, f"{base} and HEAD share no commit to compare from"
        revisions = [("HEAD", (fork.strip(),))]
    steps: list[_FileStep] = []
    keys: dict[str, str] = {}
    for revision, parents in revisions:
        if revision == "HEAD":
            args = ["git", "diff", "-z", "-M", "--name-status", parents[0], "HEAD"]
        elif len(parents) > 1:
            args = ["git", "diff-tree", "-z", "-r", "-c", "--name-only", "--no-commit-id", revision]
        else:
            args = ["git", "diff-tree", "-z", "-r", "-M", "--name-status", "--root"]
            args += ["--no-commit-id", revision]
        status, listing = _run(args, root)
        if status != 0:
            return [], {}, f"the files {revision[:12]} changed could not be listed"
        for old, new in _changed_python(listing, statuses="--name-status" in args):
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


def removed_assertions(
    root: Path, base: str, commits: tuple[str, ...], removed_lines: Sequence[tuple[str, str]]
) -> AssertionAudit:
    """The assertions the base holds that the item's own commits leave absent.

    What `no existing assertion removed` decides, and all it decides: an
    assertion present in the base's copy of a `.py` file - an `assert`
    statement's test, a call whose name begins `assert`, or a `raises` or
    `warns` item of a `with` - is absent, as `ast` reads it, after the item's
    commits (project owner, 2026-09-22, ratified, over refusing only an
    assertion that left its test and over patching the line matcher that came
    before this, `PL-4W2L`). Whether a changed assertion is stronger, weaker or
    restated is the judgment half, and every rule over the shape of an edit
    has been a guess at it; `falsifies:` is how a commission declares one.

    Each file is parsed before and after each of the item's commits, and the
    forms each commit removed and added are folded per file across them -
    `PL-VP40`'s fold at statement altitude, so an assertion cut in one commit
    and restored in the next is no change. A form is then charged only where
    the base's copy of the file holds it, and only as many copies as are gone
    after the item's commits: an assertion a sibling commit added on the same
    branch was never an existing one, however the commits naming this id
    treat it (`PL-2DTK`).

    `removed_lines` is `_net_line_changes`' removed half, read only for a file
    this interpreter cannot parse - `bin/docket` runs on the bare `python3`,
    which can be older than the project's own. There the line predicate reads
    it, the base's copy still decides what existed, and the file is named.
    """
    steps, keys, unread = _file_steps(root, base, commits)
    if unread:
        return AssertionAudit(unread=unread)
    status, _ = _run(["git", "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}"], root)
    if status != 0:
        return AssertionAudit(
            unread=f"{base} does not name a commit to read the base's copies from"
        )
    order = list(dict.fromkeys(step.key for step in steps))
    blobs = _blobs(
        root,
        {spec for step in steps for spec in (*step.before, step.after) if spec}
        | {f"{base}:{key}" for key in order},
    )
    if blobs is None:
        return AssertionAudit(unread="git could not be asked for the files' contents")

    parsed: dict[str, AssertionReading] = {}  # by object id: one version, one parse
    unparsed: dict[str, str] = {}

    def reading(key: str, spec: str) -> AssertionReading:
        held = blobs.get(spec) if spec else None
        if held is None:
            return AssertionReading()
        oid, body = held
        if oid not in parsed:
            try:
                parsed[oid] = read_assertions(body.decode("utf-8-sig"))
            except UnicodeDecodeError:
                unparsed.setdefault(key, f"its copy at {_short(spec)} is not UTF-8")
                parsed[oid] = AssertionReading()
            except (SyntaxError, ValueError, RecursionError) as error:
                where = f", line {error.lineno}" if isinstance(error, SyntaxError) else ""
                unparsed.setdefault(
                    key,
                    f"this interpreter cannot parse its copy at {_short(spec)} "
                    f"({getattr(error, 'msg', None) or type(error).__name__}{where})",
                )
                parsed[oid] = AssertionReading()
        return parsed[oid]

    removed: dict[str, Counter[str]] = {key: Counter() for key in order}
    added: dict[str, Counter[str]] = {key: Counter() for key in order}
    last: dict[str, str] = {}
    for step in steps:
        parents = [reading(step.key, spec).forms() for spec in step.before]
        now = reading(step.key, step.after).forms()
        for form in set(now).union(*parents):
            removed[step.key][form] += max(0, min(p[form] for p in parents) - now[form])
            added[step.key][form] += max(0, now[form] - max(p[form] for p in parents))
        last[step.key] = step.after

    absent: list[FileAbsence] = []
    for key in order:
        before, after = reading(key, f"{base}:{key}"), reading(key, last[key])
        if key in unparsed:
            continue
        held, kept, net = before.forms(), after.forms(), removed[key] - added[key]
        charged = tuple(
            (form, min(net[form], held[form] - kept[form]))
            for form in dict.fromkeys(a.form for a in before.assertions)
            if net[form] and held[form] > kept[form]
        )
        if charged:
            renamed = last[key].partition(":")[2]
            absent.append(
                FileAbsence(
                    key, renamed if renamed not in ("", key) else "", charged, before, after
                )
            )

    lines: list[tuple[str, str]] = []
    for key in unparsed:
        held_lines = blobs.get(f"{base}:{key}")
        existing = Counter(
            held_lines[1].decode("utf-8", errors="replace").splitlines() if held_lines else ()
        )
        for path, line in removed_lines:
            if keys.get(path, path) == key and is_assertion_line(path, line) and existing[line]:
                existing[line] -= 1
                lines.append((path, line))
    return AssertionAudit(tuple(absent), tuple(unparsed.items()), tuple(lines))


#: How many functions the report prints, and how many assertions on each side
#: of one. The counts on the check's own line are never capped.
SHOWN_FUNCTIONS, SHOWN_PER_SIDE, SHOWN_WIDTH = 5, 5, 140


def _clip(text: str) -> str:
    return text if len(text) <= SHOWN_WIDTH else text[: SHOWN_WIDTH - 3] + "..."


def _absence_lines(absence: FileAbsence, counted: Collection[str]) -> list[tuple[str, list[str]]]:
    """Each function an absence reaches, with what left it and what arrived.

    Grouped by function and paired by nobody: the check names what left each
    function and what arrived in it, and a reader who can tell a restatement
    from a weakening matches them up. `PL-K4R5` measured why the pairing is not
    the check's to make - 15 of 20 changed strings had more than one candidate.
    What stayed is counted rather than printed, since it pairs with itself.
    """
    was = Counter((a.where, a.form) for a in absence.before.assertions)
    now = Counter((a.where, a.form) for a in absence.after.assertions)
    groups: dict[str, list[str]] = {}
    for where, form in was:
        if form in counted and was[where, form] > now[where, form]:
            groups.setdefault(where, [])
    out: list[tuple[str, list[str]]] = []
    for where in groups:
        left = [
            a.shown
            for a in absence.before.assertions
            if a.where == where and a.form in counted and was[where, a.form] > now[where, a.form]
        ]
        arrived = [
            a.shown
            for a in absence.after.assertions
            if a.where == where and now[where, a.form] > was[where, a.form]
        ]
        stayed = sum(min(count, now[place]) for place, count in was.items() if place[0] == where)
        body = [f"    was  {_clip(text)}" for text in left[:SHOWN_PER_SIDE]]
        if len(left) > SHOWN_PER_SIDE:
            body.append(f"    and {len(left) - SHOWN_PER_SIDE} more that left")
        if where and where not in absence.after.defines:
            body.append(f"    now  no `{where}` in the file")
        else:
            body += [f"    now  {_clip(text)}" for text in arrived[:SHOWN_PER_SIDE]]
            if len(arrived) > SHOWN_PER_SIDE:
                body.append(f"    and {len(arrived) - SHOWN_PER_SIDE} more that arrived")
            if not arrived:
                body.append("    now  nothing in its place")
        if stayed:
            body.append(f"    ({stayed} unchanged)")
        label = f"{absence.path}::{where}" if where else f"{absence.path} (module level)"
        if absence.renamed_to:
            label += f", now {absence.renamed_to}"
        out.append((label, body))
    return out


def assertion_check(
    audit: AssertionAudit, declared: str, self_declared: str, base: str
) -> tuple[Check, int]:
    """`no existing assertion removed`, from an audit - and how many `falsifies:` folded.

    A charged form folds where the declaration is a substring of a base copy's
    source, which keeps every declaration written against the line matcher
    matching: a statement's source holds its opening line. It stays on the
    page as declared rather than counted, so the removal reads as a
    commissioned act and not an unexplained one (`PL-K82G`).
    """
    name = "no existing assertion removed"
    if audit.unread:
        return Check(name, False, f"not read: {audit.unread}"), 0
    counted = folded = 0
    shown: list[str] = []
    declared_lines: list[str] = []
    groups: list[tuple[str, list[str]]] = []
    for absence in audit.absent:
        kept: set[str] = set()
        for form, count in absence.charged:
            copies = [a for a in absence.before.assertions if a.form == form]
            if declared and any(declared in a.source or declared in a.shown for a in copies):
                folded += count
                declared_lines.append(f"declared falsified, not counted: {_clip(copies[0].shown)}")
            else:
                counted += count
                kept.add(form)
        groups += _absence_lines(absence, kept) if kept else []
    for label, body in groups[:SHOWN_FUNCTIONS]:
        shown += [label, *body]
    if len(groups) > SHOWN_FUNCTIONS:
        shown.append(f"and {len(groups) - SHOWN_FUNCTIONS} more function(s)")
    by_line = 0
    for path, line in audit.lines:
        if declared and declared in line:
            folded += 1
            declared_lines.append(f"declared falsified, not counted: {line.strip()}")
        else:
            by_line += 1
            if by_line <= SHOWN_FUNCTIONS:
                shown.append(f"{path}: {line.strip()}")
    shown += [f"read line by line, not parsed: {path} - {why}" for path, why in audit.unparsed]
    parts = [f"{counted} assertion(s)"] if counted else []
    parts += [f"{by_line} line(s) in a file read line by line"] if by_line else []
    detail = ", ".join(parts) or "none"
    if folded:
        detail += f", {folded} declared falsified" + (" by this closure" if self_declared else "")
    if counted:
        shown.append(
            "which of these restates, tightens or loosens what it asserted is not decided "
            "here, so nothing is paired; `falsifies:` on the base's copy is what declares one"
        )
    if self_declared and folded:
        # The whole worth of `falsifies:` is that the base declared it, so the
        # one case where the branch's own line is honoured names itself on the
        # page it is honoured on (`PL-ZMGR`).
        declared_lines.append(
            f"the declaration above is this closure's own: {base} holds the item at "
            "`status: needs-decision`, so which assertions the answer falsifies was "
            "this branch's to say"
        )
    return Check(name, not (counted or by_line), detail, tuple(shown + declared_lines)), folded


RESIDUAL = (
    "Not proven: whether a new test asserts the value the model should produce "
    "or merely the value it currently produces. A test can exercise the right "
    "line and assert the wrong thing. Read the new test bodies."
)

# Pytest's own exit codes, which are what make "ran and matched nothing"
# separable from "ran and something failed": 0 passed, 1 tests failed, 5 no
# tests were collected. Only 5 is needed here, and only pytest promises it.
NO_TESTS_COLLECTED = 5

# A status no process can return, so a caller can tell a command killed at the
# timeout from one that ran and failed. A shell reports an exit status in
# 0-255 and a signal death as a small negative number, so a value outside both
# collides with neither.
#
# It needs a status of its own because 1 is what a failing test returns.
# Without one, a command killed part-way through is indistinguishable from one
# that ran its assertions and correctly failed, and `already_passing` reports
# that reading to a reader as fact - the "could not look" rendered as "looked,
# found nothing" that the rest of this module exists to refuse (`PL-T940`).
TIMED_OUT = 1000

# What an exit status may be read to mean is one contract, written where the
# field is documented - `subprojects/docket/README.md` § "What a `verify:` exit status proves, and
# to whom" (`PL-6TP8`) - and every reader of a status in this module and in
# `checks.py` names the clause it applies. In short: 0 says the command's
# assertion holds, and says nothing about the work being right; any other
# status says the assertion did not hold *or was never evaluated*, and only
# three never-evaluated cases are decidable from the run - `TIMED_OUT`, 127,
# and `NO_TESTS_COLLECTED` above. A red prerequisite clause is not one of them
# (`a && b` exits 1 either way), and work finished under a different name from
# the one a `grep` pins is not decidable by anything that reads a status.

# Matched as text because the command is a shell line, not a parsed argv:
# `pytest`, `uv run pytest`, `python -m pytest` and a compound command whose
# last clause is one of those all reach here as a string. Word-bounded so that
# a file named `test_pytest_helpers.py` in the arguments is not mistaken for
# the runner - `_` is a word character, so no boundary falls before that
# `pytest`.
PYTEST_RE = re.compile(r"\bpytest\b")


def selects_no_test(command: str, status: int) -> bool:
    """Whether a command ran and matched no test, rather than failing.

    The two are the same shell exit as far as anything reading a status is
    concerned - non-zero - and they mean opposite things. A command that fails
    ran an assertion and the assertion did not hold, which is what an unstarted
    item's command is supposed to do. A command that selects no test asserted
    nothing at all: `-k` matched no name, pytest deselected the file and
    exited 5, and the same 5 comes back after the work as before it unless a
    test name happens to match. Nothing distinguishes such an item from a
    finished one, and nothing ever will on its own.

    The claim is made only about a command that names pytest, because pytest
    is what promises 5 means "collected nothing". A shell exit of 5 from
    anything else means whatever that program decided it means, and reading it
    as an empty selection would be guessing - the error this check exists to
    stop, made by the check itself.

    False negatives are accepted and are silent, which is the state today: a
    suite invoked through a wrapper that does not spell `pytest`, or a
    compound command whose last clause masks the status, is not classified.
    A false positive would put a wrong sentence in front of a reader, so the
    test is deliberately the narrow one.
    """
    return status == NO_TESTS_COLLECTED and bool(PYTEST_RE.search(command))


# The one `docket` subcommand a `verify:` command must never name. Matched as
# text for the same reason as `PYTEST_RE` above - a `verify:` line is a shell
# command rather than a parsed argv, so `bin/docket verify`, `uv run docket
# verify` and a compound command whose third clause is one of those all arrive
# here as a string. `docket` takes no options before its subcommand, so the two
# words are adjacent in every spelling of it.
#
# Matched against `_outside_quotes` rather than the raw line, which is what
# keeps the shape this rule leaves allowed from tripping it: `grep -q 'docket
# verify' docs/items/` reads the store rather than running it, and the pattern
# is the only place the words appear.
DOCKET_VERIFY_RE = re.compile(r"\bdocket\s+verify\b")
SINGLE_QUOTED_RE = re.compile(r"'[^']*'")
DOUBLE_QUOTED_RE = re.compile(r'"[^"]*"')


def _outside_quotes(command: str) -> str:
    """The command with quoted literals blanked, leaving what the shell would run.

    Single quotes suppress every expansion, so their contents are always
    literal text - `grep -q 'docket verify'` reads the store rather than
    running it. Double quotes do not: `$(...)` and backticks still run inside
    them, so a double-quoted span is blanked only when it carries neither.
    Blanking it unconditionally hid `test -z "$(bin/docket check)"`, which is a
    command being run rather than a string being matched.
    """
    text = SINGLE_QUOTED_RE.sub(" ", command)
    return DOUBLE_QUOTED_RE.sub(
        lambda m: m.group() if ("$(" in m.group() or "`" in m.group()) else " ", text
    )


#: The shell lines that exit 0 against every tree there has ever been. Exact
#: spellings rather than a parse, because that is the half of "does this command
#: discriminate" a script may answer: whether `true` can fail is a fact about
#: the shell, while whether `grep -q 'delete just that one ref' <file>` can is a
#: fact about the file it reads, and guessing at the second is the judgment half
#: `CLAUDE.md` reserves for a person. The path spellings are here because they
#: are the same program under another name, and `:` because it is the shell
#: built-in whose whole purpose is to succeed.
NEVER_FAILS = frozenset({"true", "/bin/true", "/usr/bin/true", ":", "exit 0"})

#: A trailing `#` comment, outside quotes. Stripped before the comparison so
#: that `true  # placeholder, PL-K7QX` is read as the `true` it is.
TRAILING_COMMENT_RE = re.compile(r"#.*$")


def never_fails(command: str) -> bool:
    """Whether this `verify:` command exits 0 whatever tree it is run against.

    A `verify:` command is a specification of what would prove the item done,
    so one that cannot fail specifies nothing: `docket verify` would ACCEPT a
    branch that did none of the work, and the landed replay would report the
    item as a candidate for closing forever. It is also the placeholder a
    session reaches for while triaging in bulk - three items were given
    `verify: true` on one branch on 2026-09-20, and the store had no way to say
    so until CI ran the commands.

    Decidable from the field alone, which is why it is here rather than behind
    `--verify`: nothing about the tree can make `true` return anything else, so
    the expensive tier has nothing to add. The rule is exact-match against
    `NEVER_FAILS` and deliberately nothing cleverer - a command whose *effect*
    is a no-op, like a `grep` for a string that is not in the file it reads, is
    only answerable by running it, and that question stays where it is
    (`PL-J3WK`).

    One normalization each side: a trailing comment is stripped, and a trailing
    `;` is, because neither changes what the line does.
    """
    stripped = TRAILING_COMMENT_RE.sub("", _outside_quotes(command))
    return " ".join(stripped.strip().rstrip(";").split()) in NEVER_FAILS


def reenters_verify(command: str) -> bool:
    """Whether this `verify:` command runs the command that would be running it.

    `docket verify` executes an item's own `verify:` field, so an item whose
    command names it re-enters `verify_item` once per level and never stops.
    Unlike the landed replay, which asks its question once and can be told not
    to ask again, there is no level at which this one is finished: the command
    *is* the deliverable, so every level has the same work to do. Each level
    also gets a fresh timeout rather than a share of one, so what ends the
    recursion is the process table rather than the clock.

    Refused on the item rather than at the run, because the run is where it
    cannot be reported: the outer command hangs, and nothing in its output
    names the item that caused it.

    `docket check` is deliberately not matched, and the asymmetry is the whole
    of the rule. It executes a `verify:` only under `--verify`, and a nested run
    is told not to ask, so `bin/docket check && grep -q ...` - the shape the
    older commands record, before `PL-6TP8` retired the clause ahead of the
    `grep` - is bounded at one level and proves what it claims.
    """
    return bool(DOCKET_VERIFY_RE.search(_outside_quotes(command)))


# The other subcommand that executes a `verify:`, and the reason it is treated
# differently. Re-entering it is bounded, so it is not refused; what is worth
# saying is that a nested run cannot answer the one question such a command is
# usually written to ask.
DOCKET_CHECK_RE = re.compile(r"\bdocket\s+check\b")

# What ends the pipeline a command sits in. A single `|` inside the span before
# one of these is a pipe reading the command's output; `&&`, `||` and `;` all
# start a new command, so a `|` after one of them belongs to something else.
PIPELINE_END_RE = re.compile(r"&&|\|\||;")


def reads_check_output(command: str) -> str:
    """How this command consumes `docket check`'s output, or "" if it does not.

    The distinction is between reading the exit status and reading the text.
    `docket check && grep -q ...` asks whether the store validates, which a
    nested run answers correctly and which ten open items rely on. Piping the
    output into a `grep` asks what the run *said*, and that is the question a
    nested run is specifically unable to answer: it is told not to replay the
    open items' commands, so the landed advisory it would be grepped for is
    never printed. Such a command matches nothing whether the work is done or
    not, and an inverted grep passes on the strength of it.

    An advisory rather than an error, because "reads the output" is a judgment
    about a shell line rather than an exact rule, and `CLAUDE.md` reserves hard
    failure for the exact ones. The returned string is the shape found, so the
    advisory can name it.
    """
    bare = _outside_quotes(command)
    for match in DOCKET_CHECK_RE.finditer(bare):
        before, after = bare[: match.start()], bare[match.end() :]
        if before.count("$(") > before.count(")") or before.count("`") % 2:
            return "captures its output in a command substitution"
        end = PIPELINE_END_RE.search(after)
        if "|" in (after[: end.start()] if end else after):
            return "pipes its output into another command"
    return ""


# Every word of a clause, and the shape a path is written in. The second is
# deliberately loose: it runs over the *raw* clause, quoted spans included, so
# a path inside a `python3 -c "..."` body or a `grep` pattern is a candidate
# like any other. Nothing is decided from the shape alone - a candidate only
# matters where it matches a path the branch actually changed - so a loose
# pattern costs a wasted comparison and a strict one costs a missed replay.
WORD_RE = re.compile(r"\S+")
PATH_TOKEN_RE = re.compile(r"[A-Za-z0-9_.][A-Za-z0-9_./+-]*")

# What a clause *runs*, as against what it reads, and this distinction is the
# whole of `command_paths`. `python3 tools/doc_check.py check` names a path and
# reads nothing: the path is the program, and the clause is the health half of
# a command whose discriminating half is somewhere else. 54 of the 168 open
# commands carrying that gate would otherwise replay behind any edit to it.
# A path handed to something else - `grep -q … docs/MODEL.md`, `pytest
# tests/unit/test_x.py` - is what the clause reads, and is what can change the
# command's outcome while nobody touches the item.
#
# The first word of a clause is its program. These come before it and are not.
SHELL_PREFIXES = frozenset({"!", "(", "{", "then", "do", "else"})

#: Programs whose first non-flag argument is a script they execute, so that
#: argument is a program too. Every other command takes its arguments as data.
#: A wrapped interpreter - `uv run python3 tools/x.py` - is not recognised, so
#: its script counts as read: that widens the scope rather than narrowing it,
#: which is the direction this reader errs in everywhere.
INTERPRETERS = frozenset({"python", "python3", "bash", "sh", "zsh", "dash", "node", "perl", "ruby"})

#: Interpreter flags after which what follows is code rather than a script.
INLINE_CODE = frozenset({"-c", "-m"})


def _blanked(command: str) -> str:
    """`_outside_quotes`, with each blanked span keeping its own length.

    The same rule about which quotes hide a command, in the shape a slice can
    use. `_outside_quotes` collapses a quoted span to one space, which is right
    for searching it and wrong for reading offsets back off it: everything
    after the span shifts. `command_paths` splits on the blanked text and then
    reads each clause out of the *raw* command, so the two have to agree
    character for character.
    """

    def blank(match: re.Match[str]) -> str:
        return " " * len(match.group())

    text = SINGLE_QUOTED_RE.sub(blank, command)
    return DOUBLE_QUOTED_RE.sub(
        lambda m: m.group() if ("$(" in m.group() or "`" in m.group()) else blank(m), text
    )


def _programs(words: Sequence[tuple[int, str]]) -> set[int]:
    """The offsets of the words this clause runs rather than reads."""
    index = 0
    while index < len(words) and words[index][1] in SHELL_PREFIXES:
        index += 1
    if index >= len(words):
        return set()
    offsets = {words[index][0]}
    if words[index][1] in INTERPRETERS:
        for offset, word in words[index + 1 :]:
            if word in INLINE_CODE:  # what follows is code, not a script
                break
            if word.startswith("-"):
                continue
            offsets.add(offset)
            break
    return offsets


def command_paths(command: str) -> frozenset[str]:
    """Every path this `verify:` command reads, as against the programs it runs.

    A command's outcome can change without its item being touched, and this is
    what says which edits could do it: a branch that edits `docs/MODEL.md`
    changes the answer of every open command that greps it, while editing none
    of their items. Six recorded breaks were that case, and each was reported
    only by the whole-store sweep after the merge (`PL-XMNC`).

    Read clause by clause, split on `&&`, `||` and `;` outside quotes, because
    only the discriminating clauses count. `|` does not split: the command
    after a pipe reads the previous one's output rather than a file of its own.

    Deliberately textual, and deliberately loose. Nothing here is asked of the
    filesystem, so a path a branch is *creating* is matched like any other -
    `test -f CONTRIBUTING.md` is one of the six, and the file existed nowhere
    until the branch that broke it. What comes back is candidates rather than
    a claim that any of them is a path; the caller compares them against paths
    the branch really changed, which is where a token that is not one falls
    out for free.

    What it cannot read it over-reports rather than skipping. A quoted span is
    scanned for paths even though the clause may only be matching the text; a
    wrapped interpreter's script counts as read. Both put an extra command in
    a replay, which costs a second; the other direction costs the finding.
    """
    blanked = _blanked(command)
    spans: list[tuple[int, int]] = []
    cut = 0
    for match in PIPELINE_END_RE.finditer(blanked):
        spans.append((cut, match.start()))
        cut = match.end()
    spans.append((cut, len(blanked)))

    found: set[str] = set()
    for start, end in spans:
        words = [(start + m.start(), m.group()) for m in WORD_RE.finditer(blanked[start:end])]
        run = _programs(words)
        for match in PATH_TOKEN_RE.finditer(command[start:end]):
            if start + match.start() not in run:
                found.add(match.group())
    return frozenset(found)


#: Command words whose answer is a fact about the world rather than about the
#: tree: the first element is `git` followed by one of its network subcommands,
#: the rest stand alone. Kept as command words rather than substrings because
#: a `verify:` may legitimately *search* for one - see `reaches_outside_tree`.
GIT_NETWORK_SUBCOMMANDS = frozenset({"ls-remote", "fetch", "push", "pull", "clone"})
NETWORK_COMMANDS = frozenset({"curl", "wget", "gh", "ssh", "scp", "rsync", "nc"})


def reaches_outside_tree(command: str) -> bool:
    """Whether this `verify:` command's answer depends on more than the tree.

    `already_passing` reads exit 0 as a fact about the tree, and that holds
    only where the command is a function of the tree. A command that asks the
    remote is not: its answer is a fact about the world at the moment it ran,
    so it can flip from failing to passing with no commit behind it, and the
    commits the whole-store replay then names are innocent of it. Five items
    have ever recorded one, four of them the same release-tag line - the work
    they record is the project owner's and the remote is the only place it is
    visible, so there is no hermetic substitute to prefer (`PL-205P`).

    `comments=True`, so a trailing `# …` is stripped as a shell would strip it
    rather than scanned for verbs.

    **Tokenized rather than searched, which is the whole difficulty.** A
    `verify:` may carry a network verb as a *search string* and be perfectly
    hermetic: `PL-K2C8`'s is `grep -q 'git push origin --delete'
    .claude/skills/docket/SKILL.md && …`, which reads one file and no socket.
    `shlex.split` collapses that quoted argument into a single token, so it
    never matches the bare `git` this looks for, where a substring scan calls
    it non-hermetic and silently downgrades a finding that should stay an
    error.

    **Wrong in the safe direction by construction.** An unparseable command -
    unbalanced quotes, which `shlex` raises on - answers `False`, and so does
    anything this does not recognize. False means hermetic, which means the
    finding keeps today's severity; only a command this is sure about is
    softened. A predicate that guessed the other way would quietly turn real
    findings into advisories, which is the failure worth being asymmetric
    about.

    The subcommand must follow `git` immediately, so `git -C some/path
    ls-remote` reads as hermetic. That is the safe direction again rather than
    an oversight: no recorded command has ever taken that shape, and widening
    the scan to "a network subcommand appears anywhere after a `git`" would
    catch `git log --grep fetch`, which touches nothing.

    What it deliberately does not attempt: deciding whether a command *should*
    reach the remote, or whether reaching it is correct. That is the judgment
    half, and it stays with the reader.
    """
    try:
        tokens = shlex.split(command, comments=True)
    except ValueError:  # unbalanced quotes; unparseable is not a licence to soften
        return False
    for position, token in enumerate(tokens):
        if token in NETWORK_COMMANDS:
            return True
        if (
            token == "git"
            and tokens[position + 1 : position + 2]
            and (tokens[position + 1] in GIT_NETWORK_SUBCOMMANDS)
        ):
            return True
    return False


def reads_any(command: str, paths: Collection[str]) -> bool:
    """Whether this command reads any of `paths`.

    A directory named by the command covers everything under it - `grep -rq …
    docs/items/` reads an item file the branch added - which is `_within`'s
    containment rule, the same one an item's `touches` is judged by.

    Containment is offered only to a candidate carrying a `/`, and the rest
    must match a changed path exactly. A bare word is far more often part of a
    pattern than a directory: `grep -q 'src' …` would otherwise put the command
    behind every edit under `src/`, while `grep -q … Makefile` still matches
    the file it names.
    """
    named = command_paths(command)
    directories = tuple(candidate for candidate in named if "/" in candidate)
    return any(path in named or _within(path, directories) for path in paths)


#: Appended to a commission check's detail when it is reporting rather than
#: refusing. Short, because it repeats on up to four lines of one report; the
#: reasoning is in `verify_item`'s docstring, which is where a reader who wants
#: it will look.
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
) -> tuple[int, str]:
    """Run a command, returning its exit status and combined output.

    Two kinds of command come through here, and both are meant to. Some
    callers read history with `git`, named rather than given an absolute
    path for the same reason as `vcs._run_git`: the path differs by
    environment. The other two run a command recorded in the store - an
    item's `verify:` field, and the configured check command - as written
    and through a shell, because running the recorded command verbatim is
    the entire job. Both were trusted enough to be committed to the
    repository, so there is no untrusted input to guard against here; the
    guard that matters is review of what gets committed.

    **A git read through here has to read the status it gets back**, because
    the output is stdout and stderr together: discard the status and git's
    complaint arrives as data. That is how a base that did not resolve came
    back from `changed_paths` as three changed paths (`PL-9RFP`). The reads
    left here are the ones with a use for a failure, such as `git show
    <base>:<path>` exiting 128 for a file the base does not hold. A read with no
    such use goes through `_git`, which cannot hand its failure back as an
    answer.
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
        return TIMED_OUT, str(error)
    except (OSError, subprocess.SubprocessError) as error:
        return 1, str(error)
    return result.returncode, (result.stdout or "") + (result.stderr or "")


class GitUnanswered(Exception):
    """A git read the audit rests on that git did not answer, and git's reason."""


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

    Any non-zero exit is a failure, which is narrower than `vcs._run_git` on
    purpose. There, `rev-parse --verify` and `merge-base` exit 1 to say no, and
    that is an answer. None of the reads here has a no to give: `log`, `diff`,
    `show` and `status` exit 0 whenever they answered at all.

    The reason is git's first line on stderr, which names the revision it
    could not read. Only stdout is returned, so none of stderr can reach a
    caller as output.
    """
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            # The bound these reads had while they went through `_run`.
            timeout=1800,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        raise GitUnanswered(f"`git {args[0]}` could not run: {error}") from error
    if result.returncode != 0:
        said = next((line.strip() for line in result.stderr.splitlines() if line.strip()), "")
        raise GitUnanswered(
            f"`git {args[0]}` exited {result.returncode}: {said or 'with nothing on stderr'}"
        )
    return result.stdout


def item_commits(root: Path, base: str, identifier: str) -> tuple[str, ...]:
    """Commits on this branch whose subject carries the item's id.

    One commit per item is what `docs/worker.md` asks of a worker, and this is
    what that rule buys. A batch branch carries several items' work, so
    checking one item against the branch's whole diff would fail every time
    and say nothing. Scoped to its own commits, each item is judged on what it
    actually changed - which is also what lets a reviewer take four items and
    reject the fifth.

    Raises `GitUnanswered` where the log cannot be read. Returning nothing
    would send the audit to the whole branch diff instead. Returning what came
    back, as this did until `PL-9RFP`, handed git's three-line complaint about
    the base on as three commit hashes.
    """
    output = _git(["log", "--format=%H", f"--grep={identifier}", f"{base}..HEAD"], root)
    return tuple(line.strip() for line in output.splitlines() if line.strip())


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
    """
    if commits:
        committed = _git(["show", "--name-only", "--format=", *commits], root)
    else:
        committed = _git(["diff", "--name-only", f"{base}...HEAD"], root)
    working = _git(["status", "--porcelain"], root)
    paths = {line.strip() for line in committed.splitlines() if line.strip()}
    for line in working.splitlines():
        entry = line[3:].strip() if len(line) > 3 else ""
        if " -> " in entry:  # a rename touches both names
            before, _, after = entry.partition(" -> ")
            paths.update({before.strip(), after.strip()})
        elif entry:
            paths.add(entry)
    return tuple(sorted(paths))


def _within(path: str, allowed: tuple[str, ...]) -> bool:
    candidate = path.strip().strip("/")
    for entry in allowed:
        target = entry.strip().strip("/")
        if target and (candidate == target or candidate.startswith(target + "/")):
            return True
    return False


def _diff_text(root: Path, base: str, commits: tuple[str, ...]) -> str:
    # Through `_git`, so a diff git would not produce raises instead of
    # reading as one that added no suppression and removed no assertion.
    if commits:
        return _git(["show", "--format=", *commits], root)
    return _git(["diff", f"{base}...HEAD"], root)


#: The post-image path out of a `diff --git a/x b/x` header. A header this
#: cannot read yields `""`, which `is_assertion_line` reads as "could be code"
#: rather than as "is not" - an unreadable header stays on the reporting side.
DIFF_HEADER_RE = re.compile(r"^diff --git a/(?:.*) b/(?P<path>.*)$")


def _net_line_changes(
    root: Path, base: str, commits: tuple[str, ...]
) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """The lines the work added and removed, with cancelling pairs folded out per file.

    Each line comes back paired with the path it came from. The fold below was
    already keyed by file; what changed is that the key stops being discarded,
    because whether a removed line can be an assertion at all depends on
    whether Python executes the file (`PL-7TYC`).

    `git show` over an item's commits concatenates one patch per commit rather
    than producing the branch's net change, because an item's commits need not
    be contiguous and `git diff <first>^ <last>` would sweep in whatever
    another item committed in between - which is why the per-commit form is
    there. So a line a branch added in one commit and removed in the next
    appeared in both lists, and both checks reading them - "no suppression
    added" and "no existing assertion removed" - reported work the branch had
    already undone. The error ran in the safe direction, which is why it
    survived: nothing that reaches `HEAD` escapes either check. What it cost was
    the report's credibility, because the cancelling commit is not in the output
    and so the worker cannot argue with it (`PL-VP40`).

    Cancelling an added line against an identical removed line within the same
    file is exactly as precise as what consumes this - the suppression check,
    and the assertion check's fallback for a file it cannot parse, both of
    which read a line's text rather than the tree it parses to - and it costs
    no extra git call. The assertion check proper makes the same fold over
    parsed statements instead (`removed_assertions`). Counting rather than
    de-duplicating is what keeps it safe: a file whose patches remove one
    `# type: ignore` and add two still reports one added. A line merely *moved*
    within a file cancels too, which is the right answer to both questions -
    the suppression was already there, and the assertion still is.

    Per file, never across: an assertion deleted from one file and an identical
    one added to another is two facts, not a move, and is reported as both.

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
    for line in diff.splitlines():
        if line.startswith("diff --git "):
            current = line
            header = DIFF_HEADER_RE.match(line)
            path = header.group("path") if header else ""
            continue
        # The `+++`/`---` header lines are excluded by the second test, exactly
        # as they were before the fold.
        if line.startswith("+") and line[1:2] != "+":
            side = 0
        elif line.startswith("-") and line[1:2] != "-":
            side = 1
        else:
            continue
        if current not in per_file:
            per_file[current] = (path, (Counter(), Counter()))
        per_file[current][1][side][line[1:]] += 1
    added: list[tuple[str, str]] = []
    removed: list[tuple[str, str]] = []
    for where, (added_here, removed_here) in per_file.values():
        # `Counter.__sub__` keeps only positive counts, which is multiset
        # difference: the fold each check wants.
        added.extend((where, text) for text in (added_here - removed_here).elements())
        removed.extend((where, text) for text in (removed_here - added_here).elements())
    return added, removed


def _store_at(root: Path, base: str, items_dir: str) -> tuple[str, ...] | None:
    """The item filenames the base ref holds, or `None` where its store cannot be read."""
    status, listing = _run(["git", "ls-tree", "--name-only", f"{base}:{items_dir}"], root)
    if status != 0:
        return None
    return tuple(line.strip() for line in listing.splitlines() if line.strip())


#: A `pr:` line as `cmd_record` writes it, and nothing else. Anchored at both
#: ends so that `pr: 495 and also something` is not read as one.
PR_LINE_RE = re.compile(r"^pr:\s*\d+\s*$")

#: One `recurrences:` entry as the store spells it: the date a capture was
#: filed and its id, optionally followed by the withdrawal `bin/docket withdraw`
#: writes. The withdrawn form is admitted here so that a *later* append past a
#: withdrawn entry is still recognisable as an append - without it, one
#: withdrawal would make every subsequent capture on that item read as
#: tampering (`PL-34BG`).
RECURRENCE_ENTRY = (
    rf"\d{{4}}-\d{{2}}-\d{{2}} \S+(?: {re.escape(WITHDRAWN_MARKER)} \d{{4}}-\d{{2}}-\d{{2}} \S+)?"
)

#: A `recurrences:` line as `cmd_new` writes it: those entries,
#: comma-separated. Anchored at both ends for the reason `PR_LINE_RE` is, and
#: spelling the whole value rather than a prefix so that a line carrying one
#: real entry and one invented clause is not read as one.
RECURRENCE_LINE_RE = re.compile(
    rf"^recurrences:\s*{RECURRENCE_ENTRY}(?:,\s*{RECURRENCE_ENTRY})*\s*$"
)


def sanctioned_queue_edit(root: Path, base: str, commits: tuple[str, ...], path: str) -> str:
    """Whether an out-of-`touches` edit to the queue is one the workflow asked for.

    Two of them are, and both are mechanically distinguishable from an item
    being tampered with - which is what makes exempting them safe rather than
    a hole. Returns the kind for the report to name, or `""` for an ordinary
    edit that stays outside the commission.

    **`"capture"`** - a file this branch *added*, whose front matter says
    `status: untriaged`. `CLAUDE.md` requires a finding not fixed in the
    session to be captured before the session ends, and requires every commit
    subject to lead with the current item's id; doing both puts the new item
    file on a commit `item_commits` attributes to the item being verified, and
    the audit then reported a `REJECT` for following the instructions
    (`PL-66PR`). A capture cannot weaken anything: the file did not exist on
    the base, so there is no prior content for it to have changed.

    **`"pr"`** - an existing item file whose whole diff is added `pr:` lines.
    That is what `bin/docket record` writes, and the `docket` skill's close-out
    says to let it ride the commit already being made rather than composing one
    for it. `verify` read those writes as paths outside the commission and
    rejected the close-out that followed the instruction (`PL-ZYQC`). The
    number is dictated by the merge history rather than chosen, and `record`
    refuses to overwrite a different one, so there is nothing here a worker
    could use to change what a check measures.

    **`"recurrence"`** - an existing item file whose whole diff is its
    `recurrences:` line arriving, or that line growing by entries on its right.
    `bin/docket new` writes it onto the item a capture matched, so a worker
    that captures a finding - which `CLAUDE.md` requires unconditionally -
    edits an item it was never commissioned to touch, exactly as `record`'s
    backfill does. The value is dictated rather than chosen: today's date and
    the id of the capture the session just made. It buys nothing a worker could
    want either, since the field only makes an item *named* as a generator-tier
    candidate for a human to confirm, and cannot move a band, a status or
    anything a check measures (`PL-X5JR`).

    The growth case is the one that needs care, because extending a line reads
    as a removal and a removal is what the `pr` rule is allowed to be exact
    about. So it is matched rather than forgiven: the one removed line and the
    one added line must both be whole `recurrences:` values, and the added one
    must begin with the removed one - which is an append and cannot be an edit
    of what was already recorded.

    Nothing else is exempt. An item file this branch edited in any other way -
    a `status`, a `touches`, a `verify:` command - is still outside `touches`
    and still fails, which is the case the audit exists for and the reason
    this reads the diff rather than the path.
    """
    scope = ["git", "show", "--format=", *commits] if commits else ["git", "diff", f"{base}...HEAD"]
    status, diff = _run([*scope, "--", path], root)
    if status != 0 or not diff.strip():
        return ""
    added, removed, created = [], [], False
    for line in diff.splitlines():
        if line.startswith("new file mode"):
            created = True
        elif line.startswith("+++") or line.startswith("---"):
            continue
        elif line.startswith("+"):
            added.append(line[1:])
        elif line.startswith("-"):
            removed.append(line[1:])
    if removed:
        return "recurrence" if _recurrences_grew(added, removed) else ""
    if created:
        return "capture" if any(line.strip() == "status: untriaged" for line in added) else ""
    if added and all(PR_LINE_RE.match(line) for line in added):
        return "pr"
    return "recurrence" if added and all(RECURRENCE_LINE_RE.match(line) for line in added) else ""


def _recurrences_grew(added: list[str], removed: list[str]) -> bool:
    """Whether the only change is one `recurrences:` line gaining entries on its right.

    The append `cmd_new` makes on the second and later filings, and the only
    shape of removal this exemption admits. Both lines have to be whole
    `recurrences:` values and the new one has to start with the old one, so an
    entry that was already recorded cannot be altered or dropped under cover of
    the append.

    **And what the old line grew by has to be a new entry, not a suffix on the
    last one.** Withdrawing the final entry appends ` withdrawn DATE PL-XXXX`
    to it, which starts with the old line exactly as an append does - so
    without this the one edit that *cancels* evidence would be exempted by the
    rule written for the edit that adds it. A withdrawal is a deliberate act
    with something to gain, so it declares the file it touches like any other
    work (`PL-34BG`).
    """
    if len(added) != 1 or len(removed) != 1:
        return False
    before, after = removed[0].rstrip(), added[0].rstrip()
    if not RECURRENCE_LINE_RE.match(before) or not RECURRENCE_LINE_RE.match(after):
        return False
    return after.startswith(before) and after[len(before) :].lstrip().startswith(",")


@dataclass(frozen=True)
class Commission:
    """What the *base* holds for an item - the work as it was commissioned.

    Two readings and a reason neither could be taken. `falsifies` is the
    declared exemption to "no existing assertion removed"; `status` rides
    beside it because it is what says whose the decision was, and it is read
    from the same place for the same reason - a session can set its own item's
    status on its branch, and cannot set the base's (`PL-ZMGR`).
    """

    falsifies: str = ""
    status: str = ""
    #: Why nothing could be read. Non-empty only where the two above are empty
    #: *because nothing was looked at*, which is the distinction a caller
    #: needs: an empty `falsifies` otherwise means "read it, it declares
    #: nothing".
    unread: str = ""


def commissioned_falsification(root: Path, base: str, items_dir: str, item: Item) -> Commission:
    """The `falsifies:` declaration the *base* holds for this item, and the status beside it.

    `unread` is non-empty only where nothing could be looked at, so an empty
    `Commission` carrying no `unread` means the commission was read and
    declares nothing. Keeping "could not look" apart from "looked, found
    nothing" is the same distinction `front_matter_check` makes below, for the
    same reason: folding is suppressed identically by both, and only one of
    them is a finding.

    **Read from the base rather than from the working tree**, which is the
    whole of what makes the field worth having. `PL-K82G` argued the field was
    safe because `front_matter_check` refuses a branch that edits its own
    item's front matter - true of a delegated review, and not of the self-audit
    the close-out actually runs, where that guard is an advisory by design
    (the close-out sets `status: done` in the same commit as the work). A
    session could otherwise write the declaration beside the deletion it
    excuses and fold its own integrity check. Reading the base holds the
    property in both modes and needs no second guard: a line added on the
    branch changes what a *later* branch is measured against, and nothing about
    the branch that writes it.

    A base holding no copy of this item is not a failure to read - the item is
    new on the branch, which is what every capture looks like. It declares
    nothing, and the caller says so only where the branch claims otherwise.
    Its `status` comes back empty for the same reason, which is also what stops
    an item captured *and* closed on one branch from reaching the exemption
    `self_declared_falsification` grants: there is no base copy to have left
    the decision to it.
    """
    if not item.path:
        return Commission(unread="the item names no file, so no commission could be read")
    held = _store_at(root, base, items_dir)
    if held is None:
        return Commission(unread=f"no item store at {base}:{items_dir} to read the commission from")
    was = next((held_name for held_name in held if held_name.startswith(f"{item.identifier}-")), "")
    if not was:
        return Commission()
    status, before = _run(["git", "show", f"{base}:{items_dir}/{was}"], root)
    if status != 0:
        return Commission(unread=f"{base}:{items_dir}/{was} could not be read")
    fields, _ = parse_front_matter(before)
    return Commission(
        falsifies=fields.get("falsifies", "").strip(), status=fields.get("status", "").strip()
    )


def self_declared_falsification(commission: Commission, item: Item) -> str:
    """The branch's own `falsifies:`, where the commission left the answer to it.

    Empty in every other case, and the emptiness is the point: a `falsifies:`
    line a branch writes beside the deletion it excuses is the worker's own
    word for it, which is why `commissioned_falsification` reads the base at
    all.

    **The one commission that cannot declare in advance.** A `ready` item's
    work is settled before the branch opens, so a reviewer can write the field
    first and `PL-K82G`'s rule holds without exception. A `needs-decision`
    item's cannot: the answer is the session's to make, and which assertions
    become false depends on which answer it makes. `PL-G6J5` asked whether an
    advisory should be re-based or retired, the count said retire, and the
    close-out that deleted the advisory and its 29 assertions printed `FAIL no
    existing assertion removed` with every other guard green. The guard fired
    by construction on a whole class of correct close-outs, which is the shape
    `CLAUDE.md` calls a check being routed around.

    **The gate is the base's status, never the branch's**, and that is what
    stops the exemption being self-granted. The base's copy reading
    `status: needs-decision` *is* the standing statement that the question is
    open and the answer is the session's; a session cannot write that on its
    own branch and walk through, because it is read from the same base copy the
    field would otherwise be. A `ready` item is untouched, so a delegated
    worker still cannot add `falsifies:` to excuse deleting tests - which is
    the property relaxing the check for every self-audited branch would have
    given away (project owner, 2026-09-19, ratified, over adding the assertion
    check to the four guards `--self` already relaxes).

    Two further conditions, each narrowing it to the case that has no other
    route:

    - **The branch must be closing the item.** A `needs-decision` item still
      open is mid-decision, and a declaration written then is not yet an
      answer. Both closed statuses count, `dropped` as well as `done`: the
      store has no third word for a closure, and neither is self-grantable
      while the base's status is what opens the door.
    - **The base must declare nothing.** Where it does, the commission already
      said what becomes untrue and the ordinary path applies unchanged - there
      is nothing this exemption exists to repair.
    """
    if not item.falsifies or commission.unread or commission.falsifies:
        return ""
    if commission.status != "needs-decision" or item.status not in CLOSED_STATUSES:
        return ""
    return item.falsifies


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

    The base copy is found by id rather than by name, because `store.write_item`
    renames the file when the title changes - and the title is front matter, so
    looking the current name up would miss the one edit that moves the file out
    from under the guard watching it.
    """
    name = "item front matter unchanged"
    if not item.path:
        return Check(
            name,
            False,
            "the item names no file, so there was nothing to compare",
            advisory=advisory,
        )
    try:
        after = (root / items_dir / item.path).read_text(encoding="utf-8")
    except OSError:
        return Check(
            name, False, f"no item file to read at {items_dir}/{item.path}", advisory=advisory
        )
    held = _store_at(root, base, items_dir)
    if held is None:
        return Check(
            name,
            False,
            f"no item store at {base}:{items_dir} to compare against",
            advisory=advisory,
        )
    was = next((held_name for held_name in held if held_name.startswith(f"{item.identifier}-")), "")
    if not was:
        return Check(name, True, f"a new item file - {base} holds no copy to differ from")
    status, before = _run(["git", "show", f"{base}:{items_dir}/{was}"], root)
    if status != 0:
        return Check(name, False, f"{base}:{items_dir}/{was} could not be read", advisory=advisory)
    old, _ = parse_front_matter(before)
    new, _ = parse_front_matter(after)
    changed = tuple(sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k)))
    detail = ", ".join(changed) if changed else "unchanged"
    if changed and advisory:
        detail += COMMISSION_NOTE
    return Check(name, not changed, detail, advisory=advisory)


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


def other_items_named(root: Path, commits: tuple[str, ...], identifier: str) -> tuple[str, ...]:
    """The other items' ids the audited commits name in their subjects.

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

    Raises `GitUnanswered` where the subjects cannot be read. Otherwise git's
    complaint would be searched for ids, and finding none would read as the
    commits naming this item alone.
    """
    if not commits:
        return ()
    output = _git(["show", "-s", "--format=%s", *commits], root)
    found = {match.group(0) for match in re.finditer(ID_PATTERN, output)}
    return tuple(sorted(found - {identifier}))


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
    suppression added, no assertion removed, the item's own command passes,
    and the project's own checks pass. That line is the whole design. A
    session may legitimately re-scope its own commission; it may not weaken
    the thing that measures it, and it may not skip the test.

    Two of the four have a **declared** exemption, which is not a relaxation
    of that line but the reason it can stay absolute. Each turns on the item
    as the *base* holds it - the commission - rather than on the branch, so
    neither is anything a session can grant itself mid-work:

    - `falsifies:` names an assertion the item was commissioned to make
      untrue, and a matching removal folds out of the assertion check and is
      printed beside it (`PL-K82G`). One commission cannot write the field in
      advance and takes it from the branch instead: a `needs-decision` item's
      answer is the session's to make, so which assertions it falsifies is not
      known until it is made. There the *base's status* is the gate, which a
      branch can no more set than it can the field -
      `self_declared_falsification` holds the line and says on the page that it
      did (`PL-ZMGR`).
    - A `dropped` item, or one carrying `not-delegable:`, has no command to
      run by construction, and the command check reports which applies
      (`PL-L4KX`).

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
    `project_check` and the reviewer's reading of the diff carry that.

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
    # item from delegation in the first place.
    #
    # Advisory unconditionally rather than under `self_audit`, because what
    # excuses the command is a fact about the item and not about who is asking.
    # And it does not stop early: that no command was recorded says nothing
    # about whether the diff stayed inside `touches` or whether an assertion
    # went missing, which is the half a hard stop was throwing away.
    exemption = ""
    if item.status == "dropped":
        exemption = "a dropped item built nothing, so no command can prove it"
    elif item.not_delegable:
        exemption = f"the item records why no command can prove it - {item.not_delegable}"
    if not item.verify:
        if not exemption:
            report.checks.append(Check("has a `verify:` command", False, "none recorded"))
            report.stopped_early = True
            return report
        report.checks.append(
            Check("has a `verify:` command", False, f"none recorded: {exemption}", advisory=True)
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
    candidates = [p for p in paths if not _within(p, item.touches) and Path(p).name != own_file]
    # A queue edit the workflow itself asked for is separated from the rest
    # rather than excused silently: the audit says which paths it declined to
    # count and why, so a reader can disagree with the exemption (`PL-66PR`,
    # `PL-ZYQC`). Only paths under the store are even considered.
    sanctioned = {
        path: kind
        for path in candidates
        if _within(path, (config.items_dir,))
        and (kind := sanctioned_queue_edit(root, base, commits, path))
    }
    outside = [path for path in candidates if path not in sanctioned]
    if outside:
        detail = f"{len(outside)} path(s) outside"
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
            detail += " or a sanctioned queue edit ({})".format(
                ", ".join(f"{count} {kind}" for kind, count in sorted(kinds.items()))
            )
    report.checks.append(
        Check(
            "diff stayed inside `touches`",
            not outside,
            detail + (COMMISSION_NOTE if outside and self_audit else ""),
            tuple(outside)
            + tuple(f"{path} - {kind}, not counted" for path, kind in sanctioned.items()),
            advisory=self_audit,
        )
    )

    # Said once, beside the check whose reach it widens. Silent when the
    # commits name this item alone, which is the delegated case and the one
    # the scoping was built for.
    others = other_items_named(root, commits, item.identifier)
    if others:
        report.checks.append(
            Check(
                "the audited diff is this item's alone",
                False,
                f"{len(commits)} commit(s) also name {', '.join(others)}, so the paths "
                "above are the batch's rather than this item's",
                advisory=True,
            )
        )

    protected = [p for p in paths if _within(p, config.protected_paths)]
    report.checks.append(
        Check(
            "no protected path modified",
            not protected,
            (", ".join(protected) + COMMISSION_NOTE)
            if protected and self_audit
            else (", ".join(protected) if protected else "none touched"),
            advisory=self_audit,
        )
    )

    gates = [p for p in paths if _within(p, config.gate_paths)]
    report.checks.append(
        Check(
            "the checks themselves are unedited",
            not gates,
            (", ".join(gates) + COMMISSION_NOTE)
            if gates and self_audit
            else (", ".join(gates) if gates else "none touched"),
            advisory=self_audit,
        )
    )

    # One diff read for both checks, where there were two.
    added, removed = _net_line_changes(root, base, commits)
    suppressed = [line.strip() for path, line in added if is_suppression_line(path, line)]
    report.checks.append(
        Check(
            "no suppression added",
            not suppressed,
            f"{len(suppressed)} line(s)" if suppressed else "none",
            tuple(suppressed[:5]),
        )
    )

    # Read at statement altitude rather than line by line (`PL-4W2L`). An
    # assertion the base holds that the item's commits leave absent is the one
    # fact decided; everything a line matcher used to guess from the shape of
    # an edit - a reflow, a call site gaining an argument, a changed string -
    # is either no change at all to the parser or a change put in front of the
    # reader unpaired. What the check still cannot decide is intent, so an
    # assertion the item was commissioned to *falsify* is declared, in the
    # item, before the work (`PL-K82G`).
    audit = removed_assertions(root, base, commits, removed)
    commission = commissioned_falsification(root, base, config.items_dir, item)
    unread = commission.unread
    # The one declaration read from the branch rather than from the base, and
    # only where the base's own copy left the answer to this session
    # (`PL-ZMGR`). Empty on every other branch, so `declared` is the base's
    # word in the ordinary case exactly as before.
    self_declared = self_declared_falsification(commission, item)
    declared = commission.falsifies or self_declared
    check, folded = assertion_check(audit, declared, self_declared, base)
    report.checks.append(check)

    # Said only where there is something to say, so an ordinary branch - which
    # declares nothing and has nothing to declare - sees no extra line. Each
    # case is a declaration that did not do what it looks like it did, and all
    # three are advisory: none of them folds anything, so whatever the diff
    # removed is already being refused by the check above.
    if item.falsifies and unread:
        claim = (
            f"this branch declares `falsifies: {item.falsifies}`, but {unread}, "
            "so nothing was folded"
        )
    elif item.falsifies and not declared:
        # The second sentence is the actionable half, and it was missing
        # (`PL-YZJD`). The first says the declaration did not count and why the
        # rule exists; a session reading only that concludes it made an
        # avoidable procedural slip and looks for the step it skipped. There is
        # none: by the time this branch exists the window has shut, so the
        # sentence has to name the pass that could still have written the line.
        claim = (
            f"`{item.falsifies}` is declared on this branch and not in {base}'s copy of the "
            "item, so nothing was folded: the declaration is the commission's, written "
            "before the work, and one added beside the deletion it excuses is the worker's "
            f"own word for it. Nothing on this branch could have changed that - the line had "
            f"to reach {base} before this branch's first commit, so triage is the only pass "
            "that can write it"
        )
    elif declared and not folded:
        source = "this closure declares" if self_declared else f"{base} declares"
        claim = (
            f"{source} `{declared}` falsified, but no assertion matching it was "
            "removed - the item is describing work this branch did not do"
        )
    else:
        claim = ""
    if claim:
        report.checks.append(
            Check("the `falsifies:` declaration holds", False, claim, advisory=True)
        )

    report.checks.append(
        front_matter_check(root, base, config.items_dir, item, advisory=self_audit)
    )

    # An exempt item reached here with no command; the advisory above already
    # said which exemption applied, and there is nothing left to run.
    if not item.verify:
        return report

    if os.environ.get(VERIFY_GUARD):
        report.checks.append(
            Check(
                "`verify:` command passes",
                False,
                item.verify,
                (
                    "not run: this command re-enters `docket verify`, which is what is "
                    "running it. Each level would run the command again, so the "
                    "recursion ends at the process table rather than at an answer.",
                ),
            )
        )
        return report

    status, output = _run([item.verify], root, shell=True, env={**os.environ, VERIFY_GUARD: "1"})
    lines = () if status == 0 else tuple(output.strip().splitlines()[-4:])
    # A rejection either way, and for opposite reasons, so the report says
    # which. "The command failed" sends a reviewer to look for the missing
    # work; "the command selected no test" sends them to the command, which is
    # where the fault is - the work may well be finished and unprovable.
    if selects_no_test(item.verify, status):
        lines = (
            "this command selects no test (pytest exit 5, nothing collected), so it "
            "proves neither that the work is done nor that it is missing",
        ) + lines
    report.checks.append(Check("`verify:` command passes", status == 0, item.verify, lines))
    return report


def project_check(root: Path, config: Config) -> Check:
    """Run the project's own full check once, whoever is asking.

    Shared evidence rather than per-item evidence: it says the tree is sound,
    which is a property of the tree. Every report a batch produces carries the
    same result because it is the same result.
    """
    status, output = _run([config.check_command], root, shell=True)
    return Check(
        "the project's own checks pass",
        status == 0,
        config.check_command,
        () if status == 0 else tuple(output.strip().splitlines()[-4:]),
    )


def verify(
    root: Path, item: Item, config: Config, base: str, self_audit: bool = False
) -> Verification:
    """Run every check against one item's branch, project-wide check included."""
    report = verify_item(root, item, config, base, base_warning(root, base), self_audit)
    if not report.stopped_early:
        report.checks.append(project_check(root, config))
    return report


def verify_batch(
    root: Path, items: Sequence[Item], config: Config, base: str, self_audit: bool = False
) -> list[Verification]:
    """Verify several items, running the project's own check exactly once.

    The item's own command still runs per item, because that is what makes
    each one individually acceptable or rejectable - a batch that could only
    be taken or refused whole would hand the reviewer back the all-or-nothing
    choice that one-commit-per-item exists to remove.
    """
    note = base_warning(root, base)
    reports = [verify_item(root, item, config, base, note, self_audit) for item in items]
    outstanding = [report for report in reports if not report.stopped_early]
    if outstanding:
        shared = project_check(root, config)
        for report in outstanding:
            report.checks.append(shared)
    return reports


# `docket check` runs the commands below, and open items carry `verify:`
# commands ending in `bin/docket check`. Without a guard the outer run would
# re-enter itself once per such candidate, and each re-entry would do it
# again. The child is told not to ask, which is the whole fix: it still
# validates the store, it just does not recurse into this one question.
LANDED_GUARD = "DOCKET_SKIP_LANDED"

# The same problem for the other command that executes a `verify:`, and it
# cannot take the same answer. `already_passing` declines its question and is
# still useful, because the question is about the store; `verify_item` cannot
# decline, because the command is the thing being asked about. So a nested run
# reports the re-entry as a failed check, which is the honest reading: the
# command was not run, and the item is therefore not verified.
#
# `checks.py` refuses such a command outright, so this is what stands between a
# store nobody has checked yet and a recursion the process table ends.
VERIFY_GUARD = "DOCKET_IN_VERIFY"

# Long enough for a project's own suite, short enough that one wedged command
# cannot hang `make check`. The timeout bounds a single command, so the figure
# that has to fit under it is the worst case rather than the total, and the
# total is paid concurrently in any case.
#
# No measurement is recorded here any more, deliberately. Two were, and both
# went stale inside a fortnight: a number hand-copied into a comment cannot
# know that the queue doubled under it, and the comment kept asserting a cost
# the run had left behind - 6.9s at worst where the run had reached 27.4s
# (`PL-9NKK`). Re-writing it would buy the same fortnight again. So `check`
# prints the count, the pool's wall clock, the serial total and the worst case
# on every run instead, which is that reading taken now rather than in
# September; `PL-LXR3` and `PL-9NKK` hold the dated ones, where a measurement
# keeps its date and stays true.
LANDED_TIMEOUT = 120.0


def landed_workers() -> int:
    """How many candidate commands to run at once.

    Each is a subprocess that spends most of its life on interpreter startup
    and imports rather than on the CPU, so more of them than there are cores is
    the right shape: the knee sits at the core count and the tail beyond it is
    the startup overlap, which is why this doubles rather than matching. Held
    on two measurements a day apart, on four cores, over stores of 49 and 78
    candidates - eight workers beat four in both, and beat sixteen and
    twenty-four in the second.

    Capped because the win is already spent by then and an uncapped pool on a
    large machine would put dozens of pytest processes on one working tree for
    no measured gain. The second measurement is what shows the cap is still
    right rather than merely inherited: at 78 candidates sixteen workers and
    twenty-four were both *slower* than eight, so the pool has stopped gaining
    from width and the cap is now binding on nothing.

    The two runs are in `PL-LXR3` and `PL-9NKK`, with their dates, rather than
    quoted here - `LANDED_TIMEOUT` above carries why. What this shape costs
    today is on `check`'s own headline, taken from the run in front of you.
    """
    return min(8, (os.cpu_count() or 1) * 2)


# Statuses worth asking about. `done` and `dropped` are settled, and an
# untriaged capture has not promised to do anything yet.
LANDED_STATUSES = ("ready", "needs-decision")

# Statuses asked about only when the run is narrowed to what a branch changed.
#
# A `blocked` item's command rots in silence, and the cost lands on somebody
# else: `PL-N092`'s command was `doc_check check && ! grep -q '…' README.md`,
# and when `PL-WB5K` deleted that file on 2026-09-05 `grep` began exiting 2,
# which `!` inverts to success. From that moment the command passed on a tree
# where none of the work had been done - the "would ACCEPT a branch that did
# none of it" case - and it sat that way for a day, invisible, because the item
# was blocked. Unblocking it reddened the very pull request that unblocked it.
#
# Sweeping these with the store was the obvious repair and is the wrong one:
# the replay is the most expensive thing `docket check` does, and widening the
# pool permanently would buy a finding about work nobody can start. So the
# question is asked exactly where it is cheap and timely - on a branch that
# edited the item, which is the one place a session is already looking at it
# and where `changed_items` has computed the set for free (`PL-RC0M`,
# recommending this over both widening the sweep and leaving the rot).
SCOPED_ONLY_STATUSES = ("blocked",)

# An outlier test lived here - a command 30x above the pool's median was named
# as the one the check waited for - and it was retired 2026-09-19 on a count,
# not on taste (`PL-G6J5`).
#
# The ratio was set against a store whose typical `verify:` was a `grep`: 46
# commands, 0.65 s median, one full-suite `--cov` run at 88x. The typical
# command is now `uv run pytest <file>`, and measured on the same store on
# 2026-09-19 the median is **3.65 s** across 179 commands. At 30x that puts the
# bar at 109.5 s against a `LANDED_TIMEOUT` of 120 s - and a command over the
# limit is killed and excluded from the median, so once the median passes 4.0 s
# the test cannot fire on anything at all. It already fires on nothing: zero of
# thirteen real branch scopes taken from the last twenty-five merges, and
# nothing on the whole store, which holds a 67.4 s command.
#
# Widening the denominator to the store's median, which is what `PL-G6J5` was
# filed to propose, was measured and refuted: also zero of thirteen.
#
# The silence is the right answer rather than a tuning failure. 1458 s of
# serial work across eight workers is a 182 s floor against 204 s elapsed, so
# no single command is what the run waits for - the queue is. `_note_cost`
# reports that, every run, and names the costliest command against the limit
# whether or not it is an outlier.
#
# Those are one run of three taken that day, and the container's load moves
# them: serial 1204-1458 s, slowest 48.9-67.4 s, wall 166-204 s. The figures
# above are the heaviest run, which is the conservative end for this argument -
# the floor is 150-182 s against 166-204 s elapsed either way, the slowest
# command is far under it in all three, and a median falling with the pool only
# lowers the bar the pool's own maximum then fails to reach. Read them as a
# scale rather than as constants; `PL-FZ58` is where the total is tracked.


@dataclass(frozen=True)
class SlowCommand:
    """One item's `verify:` command, and what it cost the run that executed it."""

    identifier: str
    seconds: float


@dataclass(frozen=True)
class LandedReport:
    """What running every open item's own `verify:` command found, or why nothing did.

    The question `verify` asks of a branch, asked of the store instead: not
    "did this worker do what the item commissioned" but "does the item's own
    evidence of doneness already hold, while the item is still open".

    One run, two findings, because both are about a command that specifies
    nothing and both are free once the commands have been executed. `passing`
    is the command that already holds. `vacuous` is the command that never
    ran an assertion at all - `-k` matched no test name, so pytest collected
    nothing and exited 5. The second is invisible without asking, which is
    the whole reason it is asked: 5 is not 0, so a command that selects
    nothing reads to `passing` as one that correctly fails, and stays that
    way for as long as the item is open.

    Passing proves less than it looks like it proves, and the type is shaped
    around saying so. It is consistent with two different findings - the work
    landed and nobody set `status: done`, or the command does not discriminate
    and would have passed before the work too - and no reading of an exit
    status can separate them. So this reports candidates and never a verdict,
    which is why nothing here sets a status or raises an error.

    The decidable parts of the same question are not here at all, and that is
    the point of where they live. A command recorded against more than one open
    item cannot be proving any single one of them done, and one that exits 0
    against every tree proves nothing about any - both are answered by reading
    the store, so `checks.py` refuses them on a bare `docket check` and nothing
    that reaches here can still be in either state (`PL-J3WK`). This field once
    carried the shared half as a subset of `passing`, which meant the finding
    arrived only in CI and only for the items that happened to pass.

    `blocked` is the other decidable part, and for the mirror reason. It is the
    subset of `passing` whose items nobody can start, so the first reading -
    the work landed and nobody closed the item - is not available: what a
    passing command means there is that the command does not discriminate. It
    is only ever populated on a narrowed run, because `SCOPED_ONLY_STATUSES`
    is only asked about there.

    `external` is the third carved-out subset, and it is carved out for a
    reason about the *commit* rather than about the item. `passing` means "the
    tree satisfies this command"; that reading holds only while the command is
    a function of the tree. One that asks the remote answers about the world at
    the moment it ran, so it flips with no commit behind it and the commits a
    whole-store replay then names had nothing to do with it. Those ids are
    named here so `checks.py` can soften them, and they are taken out of
    `blocked` for the same reason - see `reaches_outside_tree` and `PL-205P`.

    `declined` carries the meaning it does everywhere else here: the check did
    not run, and a caller must not read the empty `passing` - or the empty
    `vacuous` - as a clean result.

    `timed_out` and `unavailable` are the same refusal made per item rather
    than for the whole run. A command killed at the limit, or one the shell
    could not find, produced no evidence about its item, so it appears in
    neither finding above and is left out of `considered` - which is rendered
    to a reader as "checked", and would otherwise count a command that was
    not. They are reported rather than merely subtracted: an item that
    silently left the count would be the same failure in a quieter form.
    """

    passing: tuple[str, ...] = ()
    #: The subset of `passing` whose items are at a `SCOPED_ONLY_STATUSES`
    #: status, so the "work landed" reading is unavailable and only the
    #: non-discriminating one is left (`PL-RC0M`).
    blocked: tuple[str, ...] = ()
    #: The subset of `passing` whose command reaches past the tree, so its exit
    #: status is a fact about the world at the moment it ran rather than about
    #: this commit. It can flip with no commit behind it, which is why it is
    #: carried apart and rendered as an advisory: see `reaches_outside_tree`
    #: and `PL-205P`. It takes precedence over `blocked`, whose "the command
    #: does not discriminate" certainty does not survive a command that could
    #: simply have been answered by a changed world.
    external: tuple[str, ...] = ()
    #: Open items whose command matched no test, so it asserted nothing. Unlike
    #: `passing` this is a verdict rather than a candidate: `selects_no_test`
    #: only says so where pytest's own exit code says so.
    vacuous: tuple[str, ...] = ()
    #: Open items whose command was killed at `limit` before it could answer.
    timed_out: tuple[str, ...] = ()
    #: Open items whose command the shell could not find, where others could be
    #: run. Where none could, the whole run declines instead.
    unavailable: tuple[str, ...] = ()
    #: Candidates whose command ran to completion - not how many were offered.
    considered: int = 0
    #: The per-command limit these results were produced under, so a report can
    #: name the number a reader would have to change.
    limit: float = LANDED_TIMEOUT
    #: The pool's own wall clock - what a session actually waited through.
    elapsed: float = 0.0
    #: What the same commands would have cost one after another. `elapsed` is
    #: what a session waits through and this is what the queue actually asks
    #: for, and the two diverge as the store grows: concurrency holds the first
    #: roughly flat while the second climbs with every item triaged to `ready`.
    #: Reported because the flat number is the one that hides the growth.
    serial: float = 0.0
    #: The costliest command that ran, held to no threshold. It answers "how
    #: close is any one command to `limit`", which always has an answer, rather
    #: than "did an outlier arrive", which the retired ratio test asked and
    #: which this store answers no to even with a 67 s command in it
    #: (`PL-G6J5`).
    slowest: SlowCommand | None = None
    #: How wide the pool that produced these numbers was. Carried because
    #: `serial` cannot be read without it: what the remaining commands cost a
    #: run is their total divided across the workers, and a report that knows
    #: the total but not the divisor can only guess (`PL-FRGP`).
    workers: int = 0
    #: What this run was narrowed to, empty when it swept the whole store. Set
    #: whenever `scoped_to` was given, on every path out - including a decline
    #: and a scope holding nothing to run - because a narrowed run reporting no
    #: findings is otherwise indistinguishable from a store with none, which is
    #: this module's cardinal error read one level up (`PL-SDHR`).
    scope: str = ""
    declined: str = ""

    @property
    def known(self) -> bool:
        return not self.declined


def items_reading(items: Sequence[Item], paths: Collection[str]) -> frozenset[str]:
    """Open items whose `verify:` command reads one of the paths a branch changed.

    The second half of a pull request's replay scope. `vcs.changed_items` gives
    the first - the items whose own file the branch edited - and on its own it
    replays the command a branch *writes* and never the command it
    *invalidates*, which is the case every recorded break was (`PL-XMNC`).

    Closed items are left out. A closed `verify:` is a record of what was run
    on a tree that no longer exists rather than an assertion about this one, so
    replaying it would report a break in something already finished.
    """
    if not paths:
        return frozenset()
    return frozenset(
        item.identifier
        for item in items
        if item.is_open and item.verify and reads_any(item.verify, paths)
    )


def already_passing(
    root: Path,
    items: Sequence[Item],
    *,
    statuses: tuple[str, ...] = LANDED_STATUSES,
    scoped_only_statuses: tuple[str, ...] = SCOPED_ONLY_STATUSES,
    timeout: float = LANDED_TIMEOUT,
    workers: int | None = None,
    scoped_to: Collection[str] | None = None,
    reading: Collection[str] = (),
    scope_base: str = "",
) -> LandedReport:
    """Run every open item's `verify:` command, and report what running it showed.

    Two findings from the one run: the commands that already pass, and the
    commands that selected no test and so asserted nothing. Both are ways an
    item can be open while its own evidence of doneness proves nothing, and
    neither is visible without executing the command.

    An item is closed by hand, so work that merges without its `status` being
    set leaves the item `ready` forever: it keeps its place in `next`, it is
    counted open by `wave` and `gate`, and the next session re-derives work
    that is already on `main`. Four instances are known, and in all four the
    item's own command passed on the merged tree while the file still read
    `ready`.

    Running the commands is the signal rather than reading commit subjects,
    which was measured and rejected: of the thirteen open items whose id led a
    commit subject on `main`, eleven were capture or triage commits, and an
    advisory wrong five times in six is one every session learns to skim.

    The commands run concurrently, because `make check` pays this and the bill
    grows with the queue: every item triaged to `ready` adds its command's
    runtime permanently, so the serial cost rises as the store gets healthier.
    Nothing about the answer changes - each command still runs, in the working
    tree, against the current state - so this is wall clock only, which is why
    it was preferred to caching a result or asking fewer items (`PL-LXR3`).

    Two conditions decline rather than answer, both for the reason
    `merged_pull_requests` declines on a shallow clone - an empty result that
    means "could not look" must never render as "looked, found nothing":

    - the guard is set, so this is a nested run and the outer one is asking;
    - nothing ran to completion, which is what a bare checkout with no
      virtualenv looks like from here, and what a box too loaded to finish a
      command inside the limit looks like too. Every command returning "not
      found", or every one killed at the limit, is indistinguishable from a
      clean store unless it is reported as a refusal.

    Where only some commands could not answer the run still reports, and names
    them in `timed_out` and `unavailable` rather than counting them checked.

    A `blocked` item is asked about only on a narrowed run, which is the whole
    of `PL-RC0M`'s answer: its command can rot for as long as the item waits,
    and the pull request that unblocks it is the one that then goes red. The
    two rejected repairs were sweeping blocked items with the store - the
    replay is already this check's largest cost, and that widens it forever to
    ask about work nobody can start - and leaving the rot, which is a guard
    reporting the store sound while holding a command that proves nothing. A
    branch that edits the item is where the question is both cheap and timely,
    and `scoped_to` is exactly that set.

    `scoped_to` narrows the run to those ids, and exists because the cost of
    sweeping the whole store is paid on every push to every open pull request
    while the answer is about the store rather than about the commit. It is
    `PL-P3B6`'s argument one step further: that item took the replay off `make
    check` because a pre-commit gate cannot have changed whether some *other*
    item's work merged, and a pull request cannot either. So CI scopes on
    `pull_request` and sweeps everything on `push` to the default branch, where
    the question is a fact about that branch. Measured 2026-09-05: 87 s of the
    quality job's 152 s for 111 commands, against nine items changed by the
    branch that measured it.

    What a branch can have changed is *two* sets, and reading it as one was the
    defect: the items it edited, and the items whose command reads a file it
    edited. Only the first was ever in scope, so a command was replayed on the
    pull request that wrote it and never on the pull request that invalidated
    it - and all six recorded breaks were the second case, each reported only
    by the whole-store sweep once it was already on `main`. `items_reading`
    computes the second set and `reading` is the caller's word for which ids
    came from it, carried so the cost line can say which of the two produced
    its count (`PL-XMNC`).

    A passing command that reads past the tree is reported in `external` rather
    than suppressed, because the finding is real and these are precisely the
    items nobody remembers to close - four of the five ever recorded are the
    release-tag line, one per release. What changes is only where it lands:
    `checks.py` renders it as an advisory a session sees on every run, instead
    of an error on the default branch's run that nothing watches (`PL-205P`).

    A scoped run says so in `scope`, and every path out of here carries it -
    including the one where the scope holds nothing to run. A narrowed run
    reporting nothing is indistinguishable from a whole store with nothing to
    report unless it says which it was, which is the same rule the declines
    below follow.

    Cost is reported rather than judged. `elapsed`, `serial` and `slowest` say
    what the run came to and which command came closest to `limit`; nothing
    here decides whether any of it is too much. An outlier test used to - a
    command 30x the pool's median was named as the one the check waited for -
    and it was retired 2026-09-19 once measurement showed it firing on nothing:
    zero of thirteen real branch scopes and nothing on the whole store, whose
    slowest command is 67.4 s. The constants' own block above carries the
    numbers and why the silence is the right answer (`PL-G6J5`).

    What this reads from a status, and what it does not (`PL-6TP8`): exit 0 is
    the finding; `TIMED_OUT`, 127 and pytest's 5 are refusals, reported per
    item; and every other non-zero exit is read as nothing at all - not as
    "the item is legitimately open", which a red prerequisite clause makes
    indistinguishable from it. So `considered` counts a command as checked for
    the one direction this can answer, and a plain failure appears in no
    finding by design rather than by omission.
    """
    # Built before the guard returns, so a declined run still says what it
    # would have covered. "Nothing was checked" and "nothing was checked, and
    # it would have been nine items rather than the store" are different
    # sentences to whoever reads the log.
    # `reading` is the half of `scoped_to` that is in scope for the other
    # reason, and the sentence names both: "9 items" on a branch that changed
    # nine item files and one that changed one item file and a `docs/MODEL.md`
    # eight commands grep are different runs, and a reader acting on the
    # finding needs to know which they are looking at.
    widened = set(reading) & set(scoped_to or ())
    scope = (
        ""
        if scoped_to is None
        else (
            (
                f"{len(scoped_to)} item(s) in scope: {len(scoped_to) - len(widened)} this "
                f"branch changed and {len(widened)} whose `verify:` command reads a file it "
                "changed"
                if widened
                else f"{len(scoped_to)} item(s) this branch changed"
            )
            + (f" against {scope_base}" if scope_base else "")
        )
    )
    if os.environ.get(LANDED_GUARD):
        return LandedReport(
            declined="a `verify:` command re-entered `docket check`, which cannot "
            "ask this question about itself",
            scope=scope,
        )
    # `scoped_only_statuses` widens the pool only on a narrowed run, so the
    # order here matters: the filter below removes everything the branch did
    # not touch, which is what keeps a blocked item off the whole-store sweep.
    asked = statuses + (scoped_only_statuses if scoped_to is not None else ())
    candidates = [item for item in items if item.status in asked and item.verify]
    if scoped_to is not None:
        candidates = [item for item in candidates if item.identifier in scoped_to]
    if not candidates:
        return LandedReport(scope=scope)

    child = {**os.environ, LANDED_GUARD: "1", VERIFY_GUARD: "1"}

    with tempfile.TemporaryDirectory(prefix="docket-landed-") as scratch:

        def probe(item: Item) -> tuple[int, float]:
            # Coverage keeps its data in one file per run and reads it back to
            # decide `--cov-fail-under`, so two `--cov` commands sharing the
            # tree's default `.coverage` would race and one could fail on data
            # the other truncated - a wrong answer introduced by running them
            # at once rather than found by it. A path per child removes that by
            # construction, and stops these probe runs overwriting the coverage
            # data the tree's own suite wrote. Pytest's cache is left shared:
            # it is only read by selectors no recorded command uses, so a lost
            # entry cannot change an exit status.
            env = {**child, "COVERAGE_FILE": str(Path(scratch) / f"coverage.{item.identifier}")}
            started = time.monotonic()
            status, _ = _run([item.verify], root, shell=True, timeout=timeout, env=env)
            # Wall clock rather than CPU: what a session waits through is the
            # question, and it is measured under the pool's own contention
            # rather than standalone for the same reason. `dominant` reads the
            # ratio between these rather than any one of them, which is what
            # makes contention cancel instead of having to be corrected for.
            return status, time.monotonic() - started

        # `map` yields in the order it was given, which the findings below rely
        # on: they are reported as lists of ids, and an order that varied run to
        # run would make a stable store look like a changing one.
        started = time.monotonic()
        width = workers or landed_workers()
        with ThreadPoolExecutor(max_workers=width) as pool:
            results = list(pool.map(probe, candidates))
        elapsed = time.monotonic() - started

    passing: list[str] = []
    vacuous: list[str] = []
    timed_out: list[str] = []
    unavailable: list[str] = []
    for item, (status, _) in zip(candidates, results, strict=True):
        # The two statuses that mean "no answer" are taken first, because both
        # are otherwise read as one: 127 is not 0 and neither is `TIMED_OUT`,
        # so either would fall through to `selects_no_test` and then out of
        # every finding, leaving the item counted as checked and nothing said.
        if status == TIMED_OUT:
            timed_out.append(item.identifier)
        elif status == 127:  # the shell could not find the command at all
            unavailable.append(item.identifier)
        elif status == 0:
            passing.append(item.identifier)
        elif selects_no_test(item.verify, status):
            vacuous.append(item.identifier)

    checked = len(candidates) - len(timed_out) - len(unavailable)
    if not checked:
        # Nothing ran to completion, so an empty `passing` is a fact about this
        # machine rather than about the store - a bare checkout with no
        # virtualenv, or a box too loaded to finish anything inside the limit.
        # Both are the refusal the class docstring describes, and the counts go
        # in the sentence because the two want different repairs.
        why = [f"{len(unavailable)} not found by the shell"] if unavailable else []
        if timed_out:
            why.append(f"{len(timed_out)} killed at the {timeout:g}s limit")
        return LandedReport(
            declined="no `verify:` command ran to completion here "
            f"({', '.join(why)}), so finding none passing would say only that the "
            "toolchain is missing or the limit too low",
            scope=scope,
        )

    # Only the commands that ran to completion. A killed one did not take its
    # duration - it was stopped at the limit - and one the shell could not find
    # returns instantly, so either would move the totals below without having
    # cost what it appears to.
    answered = [
        (item, seconds)
        for (item, (_, seconds)) in zip(candidates, results, strict=True)
        if item.identifier not in timed_out and item.identifier not in unavailable
    ]
    serial = sum(seconds for _, seconds in answered)
    worst = max(answered, key=lambda pair: pair[1], default=None)
    slowest = SlowCommand(worst[0].identifier, worst[1]) if worst else None

    # Reported apart from `passing` because only one of that finding's two
    # readings is available here: an item nobody can start has not had its work
    # land, so a passing command can only mean the command does not
    # discriminate. `checks.py` words the two separately for that reason.
    scoped_only = {item.identifier for item in candidates if item.status in scoped_only_statuses}
    # Computed before `blocked` and subtracted from it. A blocked item is
    # reported as certainly non-discriminating, and that certainty rests on the
    # work not having landed - which a command reading the remote can no longer
    # establish, since the world may simply have moved (`PL-205P`).
    recorded = {item.identifier: item.verify for item in candidates}
    external = tuple(
        identifier for identifier in passing if reaches_outside_tree(recorded.get(identifier) or "")
    )
    outside = set(external)
    blocked = tuple(
        identifier
        for identifier in passing
        if identifier in scoped_only and identifier not in outside
    )

    return LandedReport(
        passing=tuple(passing),
        blocked=blocked,
        external=external,
        vacuous=tuple(vacuous),
        timed_out=tuple(timed_out),
        unavailable=tuple(unavailable),
        considered=checked,
        limit=timeout,
        elapsed=elapsed,
        serial=serial,
        slowest=slowest,
        workers=width,
        scope=scope,
    )
