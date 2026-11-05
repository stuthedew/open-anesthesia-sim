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
