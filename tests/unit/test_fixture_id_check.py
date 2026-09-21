"""Tests for `tools/fixture_id_check.py`, the id-grammar checker.

The failure this tool exists for is silent and survives a green suite. An id
outside `store.ID_ALPHABET` parses as an ordinary `id:` field and behaves like
any other fixture right up to the moment something applies `ID_PATTERN` to it -
and then it matches nothing, so an assertion that it is *absent* from a listing
passes whether the implementation works or not. `test_roadmap.py` spent
seventeen days asserting a placement rule against an id the parser could never
have placed (`PL-GXPP`).

So the shape here is the one `test_glyph_check.py` uses: each rule puts a
literal into a miniature tree and asserts the tool notices, with a matching test
that a correct tree stays quiet. A checker that fires on correct work gets
switched off, which is the same as not having it - and the two false-positive
sources this tool has are both regressions below: an f-string's format spec
(`PL-K{n:03d}` mints a four-character id, not a two-character one) and the
`GPL-3.0` in a licence string.

**This file is inside the tool's own scan**, so every deliberately malformed
fixture below is a named constant carrying the `not-an-id` marker the tool
documents. Named rather than inline for that reason and not only for reading:
the marker has to sit inside the literal's own span, and gathering them here
puts every malformed literal in the file in one place a reader can check
against. That is the escape hatch exercised by its own test rather than
described, and a failure to place one shows up as `make check` failing here.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import fixture_id_check
from docket.store import ID_RE

REPO_ROOT = Path(__file__).resolve().parents[2]

#: Ids the store can mint, and ids it cannot. The second tuple is the whole of
#: what this file asserts the grammar *rejects*.
MINTABLE = ("PL-K7QX", "PL-001", "PL-8888", "PL-XXXX")
UNMINTABLE = ("PL-AAAA", "PL-STUV", "PL-DEMO", "PL-1", "PL-K7QX1")  # not-an-id

#: A module whose only `PL-` mention is in a comment, which never reaches the
#: tree at all.
COMMENT_ONLY = """# `PL-AAAA` is outside the alphabet.  # not-an-id
X = 1
"""

#: Module- and function-level prose. Dropped before the walk runs, for the same
#: reason a comment is exempt: `docket/model.py` explains `PL-NOPE` in its own
#: docstring, and `tools/generator_check.py` explains `PL-AAAA` beside the
#: placeholder it chose instead.
DOCSTRINGS = '''"""Module prose naming PL-AAAA."""  # not-an-id


def f() -> None:
    """Prose naming PL-STUV."""
'''

CLASS_DOCSTRING = '''class C:  # not-an-id
    """Prose naming PL-AAAA."""

    x = 1
'''

#: `f"PL-B1B{n}"` mints `PL-B1B0`, which is mintable.
PLAIN_HOLE = """def f(n: int) -> str:  # not-an-id
    return f"PL-B1B{n}"
"""

#: `f"PL-K{n:03d}"` mints `PL-K000`. Reading the hole as one character would
#: report `PL-K`, the false positive both test trees would hit on every run.
WIDTH_HOLE = """def f(n: int) -> str:  # not-an-id
    return f"PL-K{n:03d}"
"""

#: The width is read, not assumed: this one mints seven characters.
WIDE_HOLE = """def f(n: int) -> str:  # not-an-id
    return f"PL-B1B{n:03d}"
"""

#: Implicit concatenation, which the parser folds into one node reported at the
#: line its *first* fragment opens. `tests/unit/test_workflow_paths_check.py`
#: has two of this shape, with the offending token four lines below.
CONCATENATED = """BRIEF = (  # not-an-id
    "---\\n"
    "id: PL-STUV\\n"
    "---\\n"
)
"""

CONCATENATED_MARKED = """BRIEF = (  # not-an-id
    "---\\n"
    "id: PL-STUV\\n"  # not-an-id
    "---\\n"
)
"""

#: `PL-3BZS`: the placeholder set `citation-drift.md` taught a session to copy.
CLAUDE_PLACEHOLDERS = "Placeholders:\n`PL-K7QX`, `PL-A1B2`.\n"  # not-an-id

#: A hook prints to a reader exactly as a document does. The marker is a Python
#: comment *outside* the literal here, and not inside it as the source fixtures
#: above can afford: this content is line-scanned rather than parsed, so a
#: marker written into it would exempt the very line the test asserts is found.
CLAUDE_HOOK = 'echo "see PL-A1B2"\n'  # not-an-id

CLAUDE_MARKED = """`PL-A1B2` is unmintable. <!-- not-an-id -->
"""

#: Prose *about* malformed ids, which is the norm under `docs/`.
DOCS_BRIEF = "It renamed `PL-STUV` and `PL-AAAA`.\n"  # not-an-id
ROADMAP_LINE = "`PL-M01` is the literal that was quoted.\n"  # not-an-id


def _write(root: Path, relative: str, body: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _tokens(root: Path) -> list[str]:
    return [offender.token for offender in fixture_id_check.collect(root)]


# --- the grammar is the store's ---------------------------------------------


def test_the_tool_judges_with_the_stores_own_pattern() -> None:
    """A looser grammar here would certify a literal `ID_PATTERN` cannot see.

    That is worse than no check at all: the gate would be green while the
    guarantee it stands for was void. So the tool imports `ID_RE` rather than
    restating the alphabet, and this asserts the two agree rather than that
    either has a particular shape.
    """
    for candidate in MINTABLE:
        assert ID_RE.match(candidate), candidate
        assert list(fixture_id_check.malformed(candidate)) == []

    for candidate in UNMINTABLE:
        assert not ID_RE.match(candidate), candidate
        assert list(fixture_id_check.malformed(candidate)) == [candidate]


# --- Python: values, and only values ----------------------------------------


def test_a_malformed_literal_in_a_value_is_reported_with_its_line(tmp_path: Path) -> None:
    _write(tmp_path, "pkg/thing.py", f'ITEM = "{UNMINTABLE[1]}"\n')

    (offender,) = fixture_id_check.collect(tmp_path)

    assert offender.line == 1
    assert offender.token == UNMINTABLE[1]
    assert offender.render(tmp_path).startswith("pkg/thing.py:1")


def test_a_mintable_literal_is_quiet(tmp_path: Path) -> None:
    _write(tmp_path, "pkg/thing.py", 'ITEM = "PL-K7QX"\nOLD = "PL-001"\n')

    assert fixture_id_check.collect(tmp_path) == []


def test_a_comment_is_not_scanned(tmp_path: Path) -> None:
    """A comment never reaches the tree, so prose about a bad id needs nothing."""
    _write(tmp_path, "pkg/thing.py", COMMENT_ONLY)

    assert fixture_id_check.collect(tmp_path) == []


def test_a_docstring_is_not_scanned(tmp_path: Path) -> None:
    _write(tmp_path, "pkg/thing.py", DOCSTRINGS)

    assert fixture_id_check.collect(tmp_path) == []


def test_a_class_docstring_is_dropped_too(tmp_path: Path) -> None:
    _write(tmp_path, "pkg/thing.py", CLASS_DOCSTRING)

    assert fixture_id_check.collect(tmp_path) == []


# --- f-strings: the hole stands for what it will mint ------------------------


def test_an_f_string_is_judged_as_the_id_it_will_mint(tmp_path: Path) -> None:
    """Yielding the fragments instead would report `PL-B1B` - three characters -
    and a false positive that obvious is one nobody leaves switched on."""
    _write(tmp_path, "pkg/thing.py", PLAIN_HOLE)

    assert fixture_id_check.collect(tmp_path) == []


def test_a_format_spec_contributes_its_declared_width(tmp_path: Path) -> None:
    _write(tmp_path, "pkg/thing.py", WIDTH_HOLE)

    assert fixture_id_check.collect(tmp_path) == []


def test_a_format_spec_that_overruns_the_alphabet_is_still_caught(tmp_path: Path) -> None:
    """The width is read, not assumed."""
    _write(tmp_path, "pkg/thing.py", WIDE_HOLE)

    assert _tokens(tmp_path) == ["PL-B1B000"]  # not-an-id


# --- the escape hatch --------------------------------------------------------


def test_the_marker_exempts_a_deliberately_malformed_literal(tmp_path: Path) -> None:
    """The rejection tests need one, and a glob pattern is not an id at all."""
    _write(
        tmp_path,
        "pkg/thing.py",
        'BAD = "PL-STUV"  # not-an-id\nPATTERN = "PL-K*.md"  # not-an-id: a glob\n',
    )

    assert fixture_id_check.collect(tmp_path) == []


def test_the_marker_is_read_across_a_literals_whole_span(tmp_path: Path) -> None:
    """`PL-7922`: the marker sits on a line the folded node does not report."""
    _write(tmp_path, "pkg/thing.py", CONCATENATED_MARKED)

    assert fixture_id_check.collect(tmp_path) == []


def test_a_span_with_no_marker_anywhere_is_still_reported(tmp_path: Path) -> None:
    """Widening the marker's reach must not make it match by accident."""
    _write(tmp_path, "pkg/thing.py", CONCATENATED)

    assert _tokens(tmp_path) == [UNMINTABLE[1]]


# --- the licence false positive ---------------------------------------------


def test_a_licence_identifier_is_not_an_id(tmp_path: Path) -> None:
    """`GPL-3.0` and `LGPL-2.1` end in `PL-3` and `PL-2`, neither mintable.

    Latent while only Python values were scanned and live the moment the text
    scan runs: `docs/ARCHITECTURE.md` and four briefs carry one. The lookbehind
    can only ever drop a false positive, because a genuine id is always preceded
    by a quote, a backtick, a space or a path separator.
    """
    _write(tmp_path, "pkg/thing.py", 'LICENCE = "GPL-3.0-or-later"\nOTHER = "LGPL-2.1"\n')
    _write(tmp_path, ".claude/rules/licensing.md", "pyqtgraph ships under GPL-3.0.\n")

    assert fixture_id_check.collect(tmp_path) == []


# --- .claude: prose is scanned, because there the rule is exact --------------


def test_a_claude_document_is_scanned_line_by_line(tmp_path: Path) -> None:
    """`PL-3BZS`: `citation-drift.md` taught `PL-A1B2` as a placeholder to copy."""
    _write(tmp_path, ".claude/rules/citation-drift.md", CLAUDE_PLACEHOLDERS)

    (offender,) = fixture_id_check.collect(tmp_path)

    assert offender.line == 2
    assert offender.token == "PL-A1B2"  # not-an-id


def test_a_claude_shell_hook_is_scanned_too(tmp_path: Path) -> None:
    """A hook prints to the reader exactly as a document does, so it is in scope.

    Covered by extension being absent rather than present: everything under
    `.claude/` that is not Python gets the line scan, so the next kind of file
    added there arrives guarded rather than needing a list updated.
    """
    _write(tmp_path, ".claude/hooks/digest.sh", CLAUDE_HOOK)

    assert _tokens(tmp_path) == ["PL-A1B2"]  # not-an-id


def test_prose_outside_claude_is_not_scanned(tmp_path: Path) -> None:
    """`docs/` is the measurement pointing the other way.

    There, prose *about* malformed ids is the norm - `PL-GXPP`'s brief names
    seventeen of them and `ROADMAP.md` quotes one in a release note - so a check
    firing on two thirds prose is one nobody leaves switched on. Under
    `.claude/`, every such token measured on 2026-09-21 was a defect, 2 of 2.
    """
    _write(tmp_path, "docs/items/PL-GXPP-fixtures.md", DOCS_BRIEF)
    _write(tmp_path, "ROADMAP.md", ROADMAP_LINE)

    assert fixture_id_check.collect(tmp_path) == []


def test_a_claude_document_takes_the_marker_as_well(tmp_path: Path) -> None:
    _write(tmp_path, ".claude/rules/thing.md", CLAUDE_MARKED)

    assert fixture_id_check.collect(tmp_path) == []


# --- the shipped tree, through the entry point `make check` runs -------------


def test_the_repository_carries_no_malformed_id() -> None:
    """The miniature fixtures above cannot drift away from the real tree.

    Run as a subprocess through `main`, so the exit code and the message a
    reader would actually see are what is asserted - not just `collect`.
    """
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "fixture_id_check.py")],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "could mint" in result.stdout


def test_the_failure_names_the_file_the_line_and_the_remedy(tmp_path: Path) -> None:
    """A gate that says only *that* something is wrong costs a search every run."""
    _write(tmp_path, "pkg/thing.py", f'ITEM = "{UNMINTABLE[1]}"\n')

    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "fixture_id_check.py"), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert f"pkg/thing.py:1 {UNMINTABLE[1]}" in result.stderr
    assert "not-an-id" in result.stderr
