"""Tests for `tools/glyph_check.py`, the renderable-character checker.

The failure this tool exists for is silent and survives a green suite: `→`
(U+2192) has no glyph in the Flutter client and drew as a replacement box in
the control-change list on 2026-09-04, while every string assertion in this
repository compared text the same font-less Python process had produced
(`PL-8XPQ`). So each rule has a test that puts an unrenderable character into a
tree and asserts the tool notices, and a matching test that asserts a correct
tree stays quiet. A checker that fires on correct work gets disabled, which is
the same as not having it.

Fixtures build a miniature `src/anesthesia_sim/` holding only what the rule
under test is about. The shipped tree is checked once, at the end, through the
same entry point `make check` runs - which is what keeps the miniature from
drifting into a shape the tool handles and the real source does not.

Nothing here renders anything, and the tool does not either. It decides whether
a character is on a list somebody put it on after looking at it; whether an
unlisted character *would* render is deliberately not decidable here, and the
tool refuses rather than guesses.
"""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path

import glyph_check

REPO_ROOT = Path(__file__).resolve().parents[2]

#: A view using only characters `CONFIRMED` records, including the em dash the
#: halted-run banner draws and the middle dot the control-change list uses.
CLEAN_VIEW = '''"""Miniature view."""

BANNER = "Stopped — simulation error"


def describe(before: float, after: float) -> str:
    """Render one control change."""
    return f"{before:.2f}% · {after:.2f}%"
'''


def _tree(tmp_path: Path, *, app: str = CLEAN_VIEW, core: str = "", data: object = None) -> Path:
    """Write a miniature `src/anesthesia_sim/` and return its root."""

    for tree, source in ((glyph_check.PYTHON_TREES[0], app), (glyph_check.PYTHON_TREES[1], core)):
        target = tmp_path / tree / "module.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source, encoding="utf-8")

    data_dir = tmp_path / glyph_check.DATA_TREE
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "agent.json").write_text(
        json.dumps({"display_name": "Sevoflurane"} if data is None else data), encoding="utf-8"
    )
    return tmp_path


def test_a_tree_using_only_confirmed_characters_is_quiet(tmp_path: Path) -> None:
    """The correct form: every non-ASCII character is one somebody rendered."""

    assert glyph_check.problems(_tree(tmp_path)) == []


def test_the_arrow_that_failed_is_refused(tmp_path: Path) -> None:
    """`PL-8XPQ` itself, in the form a later change would reintroduce it.

    The whole point is that nothing else in this repository goes red on it.
    """

    found = glyph_check.problems(_tree(tmp_path, app=CLEAN_VIEW.replace("·", "→")))

    assert len(found) == 1
    assert "U+2192 RIGHTWARDS ARROW" in found[0]
    assert "module.py:8" in found[0]


def test_a_core_error_message_is_covered_because_the_view_prints_it_verbatim(
    tmp_path: Path,
) -> None:
    """`core/` raises the text the view displays, so its strings are displayed strings.

    `SimulationView._apply_setting` renders `f"Setting refused — {error}"` from
    a `SimulationConfigurationError`, so a character the client cannot draw
    reaches a reader with one more step in front of it than an `app/` literal.
    """

    core = 'def refuse(value: float) -> str:\n    return f"flow {value} is outside ⚠"\n'

    found = glyph_check.problems(_tree(tmp_path, core=core))

    assert len(found) == 1
    assert "U+26A0 WARNING SIGN" in found[0]
    assert "module.py:2" in found[0]


def test_a_display_name_in_a_data_file_is_covered(tmp_path: Path) -> None:
    """`display_name` reaches the readouts, and a data edit touches no Python."""

    found = glyph_check.problems(_tree(tmp_path, data={"display_name": "Sevoflurane→"}))

    assert len(found) == 1
    assert "U+2192 RIGHTWARDS ARROW" in found[0]
    assert "agent.json" in found[0]


def test_documentation_is_exempt_wherever_it_sits(tmp_path: Path) -> None:
    """A docstring never reaches a reader, and an attribute docstring is one.

    Testing the bare-expression-statement shape rather than the first statement
    of a scope is what keeps `§` - which appears only in attribute docstrings
    in `app/controller.py` and in two `core/` modules - out of a list that is
    supposed to mean *this was rendered and seen*.
    """

    app = (
        '"""A module docstring with an arrow → in it."""\n\n'
        "class Snapshot:\n"
        "    agent_mac_percent: float\n"
        '    """An attribute docstring citing docs/MODEL.md § "MAC multiples"."""\n'
    )

    assert glyph_check.problems(_tree(tmp_path, app=app)) == []


def test_an_f_string_literal_part_is_read_around_the_interpolation(tmp_path: Path) -> None:
    """The character that failed sat in an f-string, between two placeholders."""

    app = 'def describe(a: float, b: float) -> str:\n    return f"{a:.2f}% ⇒ {b:.2f}%"\n'

    found = glyph_check.problems(_tree(tmp_path, app=app))

    assert len(found) == 1
    assert "U+21D2" in found[0]


def test_a_character_is_reported_once_per_string_however_often_it_repeats(tmp_path: Path) -> None:
    """One line per string per character, so a repeated character is not a wall of noise."""

    app = 'LABEL = "→ → → →"\n'

    assert len(glyph_check.problems(_tree(tmp_path, app=app))) == 1


def test_a_missing_tree_is_an_error_rather_than_an_empty_pass(tmp_path: Path) -> None:
    """A check whose input silently vanishes reports a pass it did not measure.

    That is the shape `PL-JRS3` found in `tools/agent_identity_check.py` on a
    ported tree, and it is the reason this states the absence instead.
    """

    found = glyph_check.problems(tmp_path)

    assert len(found) == 3
    assert all("measured nothing there" in message for message in found)


def test_every_confirmed_entry_records_its_evidence() -> None:
    """An entry means *somebody rendered this and looked at it*, and says so.

    Without the reason the list degrades into whatever previous characters
    happened to survive review, which is the state this tool replaced.
    """

    for code_point, evidence in glyph_check.CONFIRMED.items():
        assert len(evidence) > 40, code_point
        assert unicodedata.name(chr(code_point)) in evidence


def test_the_shipped_tree_passes() -> None:
    """The miniature fixtures above are only worth what this line is.

    Same entry point `make check` runs, against the real `src/`.
    """

    assert glyph_check.problems(REPO_ROOT) == []
