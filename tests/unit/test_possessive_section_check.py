"""What `tools/possessive_section_check.py` reports, and what it leaves alone.

The asymmetry is the whole design, so both halves are held here: a quotation
that matches a heading is a section citation and is reported, and one that
matches nothing may be a faithful quotation of a sentence and is not.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))

import possessive_section_check

MODEL = """# Model

## Known limitations

The venous pool is lumped, which is stated here rather than inferred.
"""


def _repo(tmp_path: Path, notes: str) -> Path:
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    (docs / "MODEL.md").write_text(MODEL, encoding="utf-8")
    (docs / "WORKING_NOTES.md").write_text(notes, encoding="utf-8")
    return tmp_path


def test_a_possessive_quotation_of_a_heading_is_reported(tmp_path: Path) -> None:
    root = _repo(tmp_path, '`docs/MODEL.md`\'s "Known limitations" says what is lumped.\n')
    found = possessive_section_check.sites(root, [])
    assert len(found) == 1
    assert 'docs/MODEL.md` § "Known limitations"' in found[0]


def test_a_possessive_quotation_of_a_sentence_is_left_alone(tmp_path: Path) -> None:
    """Correct as written: it quotes prose, and `§` would call it a section."""
    root = _repo(tmp_path, '`docs/MODEL.md`\'s "The venous pool is lumped" is the claim.\n')
    assert possessive_section_check.sites(root, []) == []


def test_a_possessive_quotation_of_a_bold_lead_sentence_is_left_alone(tmp_path: Path) -> None:
    """`PL-FKH6` (c): a bold marker is a sentence as well as a title.

    `CLAUDE.md`'s bullets open on bold lead sentences, and quoting one with the
    possessive was told to use `§` - a gate refusing a quotation that was
    right. Only a `#` heading is a title and nothing else, so only that is
    reported.
    """
    root = _repo(tmp_path, '`docs/MODEL.md`\'s "Capture, always" is the rule.\n')
    (root / "docs" / "MODEL.md").write_text(
        "# Model\n\n- **Capture, always.** Record what is found.\n", encoding="utf-8"
    )

    assert possessive_section_check.sites(root, []) == []


def test_the_section_mark_form_is_already_right_and_is_not_reported(tmp_path: Path) -> None:
    root = _repo(tmp_path, '`docs/MODEL.md` § "Known limitations" says what is lumped.\n')
    assert possessive_section_check.sites(root, []) == []


def test_an_example_inside_a_fence_is_not_a_citation(tmp_path: Path) -> None:
    """An item whose subject is the citation form quotes it in a fenced block."""
    notes = 'How it is written:\n\n```text\n`docs/MODEL.md`\'s "Known limitations"\n```\n'
    root = _repo(tmp_path, notes)
    assert possessive_section_check.sites(root, []) == []


def test_a_source_file_this_run_cannot_parse_is_declined_not_skipped(tmp_path: Path) -> None:
    """CI's floor section runs this under 3.11, which cannot parse all of `src/`.

    Two files went unread there with nothing said, and no gate held a
    possessive citation in either to the `§` form (`PL-MB3F`). The syntax is
    invalid under every interpreter, so the test holds wherever it runs.
    """
    root = _repo(tmp_path, "Nothing cited.\n")
    (root / "thing.py").write_text(
        '"""`docs/MODEL.md`\'s "Known limitations" says what is lumped."""\n\ndef f(:\n',
        encoding="utf-8",
    )
    declined: list[str] = []
    assert possessive_section_check.sites(root, declined) == []
    assert len(declined) == 1
    assert declined[0].startswith("thing.py:3: Python ")
    assert "cannot parse this file" in declined[0]


def test_a_decline_is_printed_and_does_not_fail_the_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The printed block is the half of the fix a reader sees; a decline is not a finding."""
    root = _repo(tmp_path, "Nothing cited.\n")
    (root / "thing.py").write_text("def f(:\n", encoding="utf-8")
    assert possessive_section_check.main([str(root)]) == 0
    out = capsys.readouterr().out
    assert "none names a section" in out
    assert "Not checked (1;" in out
    assert "  thing.py:1: Python " in out
