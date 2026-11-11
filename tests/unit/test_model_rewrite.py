"""`tools/model_rewrite.py` must list the ids a section still cites, and every fact a rewrite drops.

Each section part of `PL-ZT47` moves decision history out of `docs/MODEL.md`
and rewrites the rest. `ids` is how a part knows the history is out, and its
`verify:` runs it. `lost` is how the part sees every equation, code span,
citation and number the rewrite no longer carries or newly carries. A fact this
tool fails to list is a fact nobody accounts for, and a section part with
nothing left unaccounted merges without the owner's read (`PL-ZTZF`).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from model_rewrite import (
    added_facts,
    cited_ids,
    facts,
    gone_facts,
    main,
    number_value,
    pair_restated,
    report_added,
    report_gone,
    report_ids,
)

DOCUMENT = """\
# Model

## Hazards

The run is named (`PL-B2B2`), and this row has no test yet (`PL-C3C3`).
A wrapped form also counts: no test
yet (`PL-D4D4`), and so does PL-F5F5 written bare.

### A subsection

It cites `PL-G6G6`.

## Equations

Fresh gas enters at $`\\dot V_{FGF}`$ of 6 L/min, measured 2026-10-03 in #1808.

```math
F_A = 1 - e^{-t/\\tau}
```

See `tests/unit/test_alveolar.py` and doi 10.1213/00000539-199103000-00007, pp. 161-162.
"""


def _lines() -> list[str]:
    return DOCUMENT.splitlines()


def test_ids_skips_the_declared_none_form_even_when_it_wraps() -> None:
    lines = _lines()
    found = cited_ids(lines, 2, 12)

    assert [(cited.line, cited.ids) for cited in found] == [
        (5, ("PL-B2B2",)),
        (7, ("PL-F5F5",)),
        (11, ("PL-G6G6",)),
    ]


def test_a_section_holds_its_subsections_and_stops_at_its_sibling() -> None:
    status, out = report_ids(_lines(), ["Hazards"])

    assert status == 1
    assert [line.split(": ")[1] for line in out] == ["PL-B2B2", "PL-F5F5", "PL-G6G6"]
    assert report_ids(_lines(), ["Equations"]) == (0, [])


def test_a_heading_the_document_does_not_hold_exits_2() -> None:
    status, out = report_ids(_lines(), ["Equations", "Nowhere"])

    assert status == 2
    assert out == ['docs/MODEL.md: no heading reads "Nowhere"']


def test_facts_reads_each_kind_once() -> None:
    """A number inside an equation is the equation's; a pull request number is not a fact."""
    found = {(kind, text) for kind, text, _ in facts(DOCUMENT)}

    assert ("equation", "\\dot V_{FGF}") in found
    assert ("equation", "F_A = 1 - e^{-t/\\tau}") in found
    assert ("code", "tests/unit/test_alveolar.py") in found
    assert ("item id", "PL-B2B2") in found
    assert ("item id", "PL-F5F5") in found
    assert ("declaration", "no test yet (`PL-C3C3`)") in found
    assert ("declaration", "no test yet (`PL-D4D4`)") in found
    assert ("item id", "PL-C3C3") not in found
    assert ("date", "2026-10-03") in found
    assert ("citation", "10.1213/00000539-199103000-00007") in found
    assert ("citation", "pp. 161-162") in found
    numbers = {text for kind, text in found if kind == "number"}
    assert numbers == {"6 L/min"}


def test_a_declaration_rewritten_as_untested_reads_as_lost() -> None:
    """A trial copy editor rewrote this form as "are untested", which the document check misses.

    `tools/doc_check.py` reads only the declared-none form as a member that has
    no test, so the rewrite loses a fact, not history (`PL-J1ZM`).
    """
    before = "These rows have no test\nyet (`PL-C3C3`).\n"

    gone = gone_facts(before, "These rows are untested.\n", "")

    assert [(item.kind, item.text, item.line) for item in gone] == [
        ("declaration", "no test yet (`PL-C3C3`)", 1)
    ]


def test_a_number_keeps_its_sign_exponent_and_unit_and_a_list_ordinal_is_not_one() -> None:
    """Each change below alters a value, so each must read as a lost fact."""
    before = (
        "A residual of 9.262e-14 L and 1.67e5 steps.\n"
        "A shift of −2.29 SD in 1.32 L, at 6L.\n"
        "1. Fat spans 4 px.\n"
        "2. It reaches 3 MAC.\n"
    )
    after = (
        "A residual of 9.999e-14 L and 1.92e5 steps.\n"
        "A shift of 2.29 SD in 1.32 mL, at 6 mL.\n"
        "1. Fat spans 4 px.\n"
        "2. It reaches 3.\n"
        "3. A third point.\n"
    )

    gone = {item.text for item in gone_facts(before, after, "")}

    assert gone == {"9.262e-14 L", "1.67e5", "−2.29", "1.32 L", "6L", "3 MAC"}


def test_gone_facts_counts_what_the_rewrite_holds_fewer_times_and_marks_the_moved() -> None:
    after = DOCUMENT.replace("of 6 L/min, measured 2026-10-03 in #1808.", "of 6 L/min.").replace(
        "```math\nF_A = 1 - e^{-t/\\tau}\n```\n", ""
    )
    added = "Measured 2026-10-03 at 6 L/min."

    gone = {(item.kind, item.text): item for item in gone_facts(DOCUMENT, after, added)}

    assert set(gone) == {("equation", "F_A = 1 - e^{-t/\\tau}"), ("date", "2026-10-03")}
    assert gone[("date", "2026-10-03")].moved
    assert not gone[("equation", "F_A = 1 - e^{-t/\\tau}")].moved
    assert gone[("equation", "F_A = 1 - e^{-t/\\tau}")].line == 18


def test_lost_lists_a_fact_the_rewrite_added() -> None:
    """A value the rewrite adds, or restates once more, is listed with its new line.

    Before `PL-ZTZF`, `lost` read only what the fork held more often, so a
    rewrite that added "8 L/min" to a sentence printed nothing. A changed value
    shows on both sides: the old one as dropped and the new one as added.
    """
    after = DOCUMENT.replace("of 6 L/min,", "of 7 L/min,").replace(
        "## Hazards\n", "## Hazards\n\nFresh gas runs at 8 L/min and `F_A` is read twice.\n"
    )

    added = {(item.kind, item.text): item for item in added_facts(DOCUMENT, after)}

    assert set(added) == {("number", "8 L/min"), ("number", "7 L/min"), ("code", "F_A")}
    assert added[("number", "8 L/min")].line == 5
    assert added[("number", "7 L/min")].context.startswith("Fresh gas enters at")
    assert {item.text for item in gone_facts(DOCUMENT, after, "")} == {"6 L/min"}
    assert added_facts(DOCUMENT, DOCUMENT) == []


def test_a_fact_moved_to_the_note_for_developers_prints_nothing() -> None:
    """A section's note for developers is where `PL-TZ7R` sends numerical detail.

    `lost` counts each fact across the whole document, so a value that moves
    from a paragraph to the note at the end of its section is neither dropped
    nor added, and the section part accounts for nothing.
    """
    after = DOCUMENT.replace(" of 6 L/min, measured 2026-10-03 in #1808.", ".").replace(
        "pp. 161-162.\n",
        "pp. 161-162.\n\n**For developers.** The flow is 6 L/min, measured 2026-10-03 in #1808.\n",
    )

    assert after != DOCUMENT
    assert gone_facts(DOCUMENT, after, "") == []
    assert added_facts(DOCUMENT, after) == []


@pytest.mark.parametrize(
    ("written", "value"),
    [
        ("0.5%", (0.005, None)),
        ("5e-3", (0.005, None)),
        ("0.04 %", (0.0004, None)),
        ("10 percent", (0.1, None)),
        ("1,000", (1000.0, None)),
        ("−2.29", (-2.29, None)),
        ("6 l/min", (6.0, "L/min")),
        ("2 min", (120.0, "s")),
        ("1.5 MAC", (1.5, "MAC")),
    ],
)
def test_number_value_reads_a_percent_as_a_fraction_and_a_unit_as_doc_check_does(
    written: str, value: tuple[float, str | None]
) -> None:
    read = number_value(written)

    assert read is not None
    assert read[1] == value[1]
    assert read[0] == pytest.approx(value[0], rel=1e-12)


def test_a_comma_that_is_not_a_thousands_separator_is_never_paired() -> None:
    assert number_value("1,5") is None


def test_a_section_number_with_two_decimal_points_is_never_paired() -> None:
    """WCAG's "1.4.11" crashed `lost` on a rewrite that restated it (`PL-XT53`)."""

    assert number_value("1.4.11") is None


RESTATED = """\
# Model

## Step size

The step test allows a relative difference of 5e-3, and it ran at 0.07%.

## Hazards

Fresh gas runs at 6 L/min.
"""


def test_a_number_restated_with_the_same_value_in_its_section_is_paired() -> None:
    """4e-4 rewritten as 0.04% is one value in a new form, so it is marked `restated`.

    0.07% and 7e-4 differ by about 1e-19 in floating point after the percent
    is divided by 100, so the pair also shows that the comparison allows for
    that rounding.
    """
    after = RESTATED.replace("of 5e-3,", "of 0.5%,").replace("at 0.07%.", "at 7e-4.")

    gone, added = pair_restated(
        RESTATED, after, gone_facts(RESTATED, after, ""), added_facts(RESTATED, after)
    )

    assert {(item.text, item.restated_as) for item in gone} == {("5e-3", "0.5%"), ("0.07%", "7e-4")}
    assert {(item.text, item.restates) for item in added} == {("0.5%", "5e-3"), ("7e-4", "0.07%")}


@pytest.mark.parametrize(
    "after",
    [
        # The same value, added to another section.
        RESTATED.replace("of 5e-3,", "of,").replace("at 6 L/min.", "at 6 L/min, within 0.5%."),
        # A different value.
        RESTATED.replace("of 5e-3,", "of 0.6%,"),
        # The same number in another unit.
        RESTATED.replace("of 5e-3,", "of 5e-3 L,"),
    ],
)
def test_a_dropped_number_is_not_paired_across_sections_values_or_units(after: str) -> None:
    gone, added = pair_restated(
        RESTATED, after, gone_facts(RESTATED, after, ""), added_facts(RESTATED, after)
    )

    assert [item.text for item in gone] == ["5e-3"]
    assert not any(item.restated_as for item in gone)
    assert not any(item.restates for item in added)


def test_lost_prints_a_restated_number_beside_its_new_form() -> None:
    after = RESTATED.replace("of 5e-3,", "of 0.5%,")
    gone, added = pair_restated(
        RESTATED, after, gone_facts(RESTATED, after, ""), added_facts(RESTATED, after)
    )

    out = report_gone(gone, "main") + report_added(added)

    assert "1 of them are restated in another form with the same value." in out[0]
    assert any(line.startswith("  restated 5e-3 as 0.5%  (fork line 5:") for line in out)
    assert any("1 of them restate a dropped number with the same value." in line for line in out)
    assert any(line.startswith("  added 0.5% restating 5e-3  (line 5:") for line in out)


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def test_lost_reads_the_fork_and_a_new_item_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _git(tmp_path, "init", "-q", "-b", "main")
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git(tmp_path, "config", key, value)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/MODEL.md").write_text(DOCUMENT, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "seed")
    _git(tmp_path, "checkout", "-qb", "work")
    rewritten = DOCUMENT.replace(", pp. 161-162", "").replace("of 6 L/min", "of")
    (tmp_path / "docs/MODEL.md").write_text(rewritten, encoding="utf-8")
    (tmp_path / "docs/items").mkdir()
    (tmp_path / "docs/items/PL-B2B2-x.md").write_text("Moved: 6 L/min.\n", encoding="utf-8")

    assert main(["--root", str(tmp_path), "lost", "--base", "main"]) == 0
    out = capsys.readouterr().out
    assert "2 equations, declarations, code spans, citations and numbers" in out
    assert "1 of them were added to an item file" in out
    assert "  gone  pp. 161-162  (fork line 21:" in out
    assert "  moved 6 L/min  (fork line 15:" in out
    assert "0 equations, declarations, code spans, citations and numbers are held more times" in out


#: A document whose first section points at its second, which `move` takes.
SPLIT_DOCUMENT = """\
# Model

## Hazards

The readout shows 6 L/min (§ "Equations" below), as `PL-B2B2` decided.

## Equations

Fresh gas enters at 6 L/min, per § "Hazards" above and § "Wash-in".

### Wash-in

```math
F_A = 1 - e^{-t/\\tau}
```
"""

CITING_MODULE = '''\
"""A module that cites both documents' sections.

See `docs/MODEL.md` § "Wash-in" and `docs/MODEL.md` § "Hazards".
"""

MESSAGE = 'refused (docs/MODEL.md, "Equations")'
STALE = 'refused (docs/MODEL.md, "A heading nobody wrote")'
'''


def _split_repository(tmp_path: Path) -> Path:
    """A repository on a work branch, with the document, a title for its new half and a citer."""
    _git(tmp_path, "init", "-q", "-b", "main")
    for key, value in (("user.email", "t@example.com"), ("user.name", "T")):
        _git(tmp_path, "config", key, value)
    (tmp_path / "docs").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "docs/MODEL.md").write_text(SPLIT_DOCUMENT, encoding="utf-8")
    (tmp_path / "src/citing.py").write_text(CITING_MODULE, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "seed")
    _git(tmp_path, "checkout", "-qb", "work")
    (tmp_path / "docs/INTERFACE.md").write_text("# Interface\n\n", encoding="utf-8")
    return tmp_path


def test_move_takes_a_section_whole_and_repoints_each_citation_of_it(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The section moves with its subsection, and only citations of what moved change."""
    root = _split_repository(tmp_path)

    assert main(["--root", str(root), "move", "--to", "docs/INTERFACE.md", "Equations"]) == 0

    out = capsys.readouterr().out
    model = (root / "docs/MODEL.md").read_text(encoding="utf-8")
    interface = (root / "docs/INTERFACE.md").read_text(encoding="utf-8")
    assert "## Equations" not in model and "### Wash-in" not in model
    # The pointer to the moved section names its new document and loses "below".
    assert 'shows 6 L/min (`docs/INTERFACE.md` § "Equations"), as' in model
    # The moved text is unchanged but for its pointer to the section that stayed.
    moved = SPLIT_DOCUMENT[SPLIT_DOCUMENT.index("## Equations") :]
    assert interface == "# Interface\n\n" + moved.replace(
        '§ "Hazards" above', '`docs/MODEL.md` § "Hazards"'
    )
    citing = (root / "src/citing.py").read_text(encoding="utf-8")
    assert '`docs/INTERFACE.md` § "Wash-in" and `docs/MODEL.md` § "Hazards"' in citing
    assert "MESSAGE = 'refused (docs/INTERFACE.md, \"Equations\")'" in citing
    # A quotation that neither document holds stays, and is listed for a person to read.
    assert "STALE = 'refused (docs/MODEL.md, \"A heading nobody wrote\")'" in citing
    assert "src/citing.py:7: A heading nobody wrote" in out


def test_repoint_run_twice_changes_nothing_more(tmp_path: Path) -> None:
    root = _split_repository(tmp_path)
    assert main(["--root", str(root), "move", "--to", "docs/INTERFACE.md", "Equations"]) == 0
    after_move = {
        path: (root / path).read_text(encoding="utf-8")
        for path in ("docs/MODEL.md", "docs/INTERFACE.md", "src/citing.py")
    }

    assert main(["--root", str(root), "repoint", "--to", "docs/INTERFACE.md"]) == 0

    for path, text in after_move.items():
        assert (root / path).read_text(encoding="utf-8") == text


def test_lost_counts_a_fact_across_both_documents_of_the_specification(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A fact moved to the other document is not lost, and a fact cut from it is."""
    root = _split_repository(tmp_path)
    assert main(["--root", str(root), "move", "--to", "docs/INTERFACE.md", "Equations"]) == 0
    capsys.readouterr()

    assert main(["--root", str(root), "lost", "--base", "main"]) == 0
    out = capsys.readouterr().out
    assert "docs/MODEL.md and docs/INTERFACE.md against" in out
    assert ": 0 equations, declarations, code spans, citations and numbers are held fewer" in out

    interface = root / "docs/INTERFACE.md"
    interface.write_text(
        interface.read_text(encoding="utf-8").replace("enters at 6 L/min", "enters"),
        encoding="utf-8",
    )
    assert main(["--root", str(root), "lost", "--base", "main"]) == 0
    out = capsys.readouterr().out
    assert "  gone  6 L/min  (fork line 5: docs/MODEL.md: The readout shows" in out


def test_move_refuses_a_heading_the_document_does_not_hold(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _split_repository(tmp_path)

    assert main(["--root", str(root), "move", "--to", "docs/INTERFACE.md", "Absent"]) == 2

    assert 'docs/MODEL.md: no one section reads "Absent"' in capsys.readouterr().out
    assert (root / "docs/MODEL.md").read_text(encoding="utf-8") == SPLIT_DOCUMENT
