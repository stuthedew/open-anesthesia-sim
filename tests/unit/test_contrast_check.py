"""Tests for `tools/contrast_check.py`, the color-contrast checker.

Two jobs, tested separately.

The **arithmetic** is a published formula, so it is validated against published
values rather than against itself: black on white is exactly 21:1 by
construction, and `#767676` and `#949494` on white are the greys the WCAG
literature names as sitting on the 4.5:1 and 3:1 thresholds. A contrast
implementation that agrees only with its own author is the failure mode here -
every number this tool prints about the interface is downstream of these three.

The **checking** exists to catch drift nobody remembered to look for, so each
check has a test that breaks the palette and asserts the tool notices, and a
matching test that asserts the correct form stays quiet. A checker that fires
on correct work gets disabled, which is the same as not having it.

Fixtures build a miniature `src/anesthesia_sim/app/` with two modules, and the
requirement table is substituted per test so a fixture names only what it is
about. The real palette is checked once, at the end, by the same entry point
`make check` runs.
"""

from __future__ import annotations

from pathlib import Path

import contrast_check
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

THEME_SOURCE = '''"""Miniature theme."""

PANEL = "#FFFFFF"
INK = "#243B53"
FAINT = "#AAAAAA"

AGENT_COLOR_SCHEMES = {
    "demoflurane": AgentColorScheme(
        fill="#00629B",
        foreground="#FFFFFF",
        standard_color_name="Blue",
    ),
}
'''

VIEW_SOURCE = '''"""Miniature view."""

import flet as ft

from anesthesia_sim.app.theme import INK, PANEL

TRACE_ONE = INK
TRACE_TWO = "#DC2626"
NOT_A_COLOUR = "solid"
'''


def _repo(tmp_path: Path, *, theme: str = THEME_SOURCE, view: str = VIEW_SOURCE) -> Path:
    """Build a miniature repository holding only the two color-defining modules."""
    app = tmp_path / "src" / "anesthesia_sim" / "app"
    app.mkdir(parents=True)
    (app / "theme.py").write_text(theme, encoding="utf-8")
    (app / "simulation_view.py").write_text(view, encoding="utf-8")
    return tmp_path


def _requirement(foreground: str, background: str, minimum: float) -> contrast_check.Requirement:
    return contrast_check.Requirement(
        foreground=foreground,
        background=background,
        minimum=minimum,
        criterion="1.4.3",
        why="a fixture",
    )


@pytest.fixture
def declare(monkeypatch: pytest.MonkeyPatch):
    """Substitute the requirement table and the shortfall list for one test."""

    def _declare(
        requirements: tuple[contrast_check.Requirement, ...],
        shortfalls: dict[tuple[str, str], str] | None = None,
    ) -> None:
        monkeypatch.setattr(contrast_check, "REQUIREMENTS", requirements)
        monkeypatch.setattr(contrast_check, "KNOWN_SHORTFALLS", shortfalls or {})

    return _declare


# --- the arithmetic, against published values -------------------------------


def test_black_on_white_is_exactly_twenty_one_to_one() -> None:
    """The definition's upper bound, which falls out of the formula exactly."""
    assert contrast_check.contrast_ratio("#000000", "#FFFFFF") == pytest.approx(21.0)


def test_a_color_against_itself_is_one_to_one() -> None:
    assert contrast_check.contrast_ratio("#18A999", "#18A999") == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("color", "expected"),
    [("#767676", 4.54), ("#949494", 3.03), ("#FFFFFF", 1.0), ("#000000", 21.0)],
)
def test_published_reference_greys_on_white(color: str, expected: float) -> None:
    """`#767676` and `#949494` are the documented AA text and non-text thresholds."""
    assert contrast_check.contrast_ratio(color, "#FFFFFF") == pytest.approx(expected, abs=0.01)


def test_the_ratio_does_not_depend_on_argument_order() -> None:
    forward = contrast_check.contrast_ratio("#176B87", "#FFFFFF")
    backward = contrast_check.contrast_ratio("#FFFFFF", "#176B87")
    assert forward == pytest.approx(backward)


def test_relative_luminance_spans_the_unit_interval() -> None:
    assert contrast_check.relative_luminance("#000000") == pytest.approx(0.0)
    assert contrast_check.relative_luminance("#FFFFFF") == pytest.approx(1.0)


@pytest.mark.parametrize("bad", ["#FFF", "", "not-a-color", "#1234567"])
def test_a_malformed_color_is_refused_rather_than_guessed(bad: str) -> None:
    """Prefer an obvious failure to a plausible number from a misread constant."""
    with pytest.raises(ValueError):
        contrast_check.relative_luminance(bad)


def test_the_separation_ceiling_is_the_root_of_the_luminance_span() -> None:
    """Two traces can span the whole range; six cannot each clear a third of it."""
    assert contrast_check.separation_ceiling(2) == pytest.approx(21.0)
    assert contrast_check.separation_ceiling(6) == pytest.approx(1.8384, abs=0.001)
    assert contrast_check.separation_ceiling(6) < contrast_check.AA_NON_TEXT


def test_a_separation_ceiling_needs_two_traces() -> None:
    with pytest.raises(ValueError):
        contrast_check.separation_ceiling(1)


# --- reading the palette ----------------------------------------------------


def test_the_palette_resolves_names_as_well_as_literals(tmp_path: Path) -> None:
    """`CIRCUIT_COLOR = PRIMARY` is how half the real trace colors are defined."""
    palette = contrast_check.read_palette(_repo(tmp_path))

    assert palette["INK"] == "#243B53"
    assert palette["TRACE_ONE"] == "#243B53", "a cross-module reference was not resolved"
    assert palette["TRACE_TWO"] == "#DC2626"


def test_the_palette_reads_the_agent_schemes(tmp_path: Path) -> None:
    palette = contrast_check.read_palette(_repo(tmp_path))

    assert palette["demoflurane.fill"] == "#00629B"
    assert palette["demoflurane.foreground"] == "#FFFFFF"


def test_the_palette_ignores_strings_that_are_not_colors(tmp_path: Path) -> None:
    """`NOT_A_COLOUR = "solid"` is a line-style name, not something to measure."""
    assert "NOT_A_COLOUR" not in contrast_check.read_palette(_repo(tmp_path))


# --- the checks -------------------------------------------------------------


def test_a_pair_that_meets_its_minimum_is_quiet(tmp_path: Path, declare) -> None:
    declare((_requirement("INK", "PANEL", contrast_check.AA_TEXT),))

    report = contrast_check.analyze(_repo(tmp_path))

    assert not report.errors
    assert report.results[0].meets


def test_a_pair_below_its_minimum_is_an_error(tmp_path: Path, declare) -> None:
    """`#AAAAAA` on white is 2.32:1 - the regression this tool exists to catch."""
    declare((_requirement("FAINT", "PANEL", contrast_check.AA_TEXT),))

    report = contrast_check.analyze(_repo(tmp_path))

    assert report.errors
    assert [result.requirement.foreground for result in report.unexpected] == ["FAINT"]
    assert "Below the required ratio" in contrast_check.format_report(report, matrix=False)


def test_a_declared_shortfall_does_not_fail_the_build(tmp_path: Path, declare) -> None:
    declare(
        (_requirement("FAINT", "PANEL", contrast_check.AA_TEXT),), {("FAINT", "PANEL"): "PL-DEMO"}
    )

    report = contrast_check.analyze(_repo(tmp_path))

    assert not report.errors
    assert "PL-DEMO" in contrast_check.format_report(report, matrix=False)


def test_a_shortfall_that_starts_passing_is_an_error(tmp_path: Path, declare) -> None:
    """The list cannot rot: fixing a shortfall forces its entry out."""
    declare((_requirement("INK", "PANEL", contrast_check.AA_TEXT),), {("INK", "PANEL"): "PL-DEMO"})

    report = contrast_check.analyze(_repo(tmp_path))

    assert report.errors
    assert report.repaired
    assert "remove the entry" in contrast_check.format_report(report, matrix=False)


def test_a_renamed_constant_is_an_error_rather_than_a_skipped_check(
    tmp_path: Path, declare
) -> None:
    """A requirement naming a color nobody defines would otherwise pass unread."""
    declare((_requirement("DELETED_COLOR", "PANEL", contrast_check.AA_TEXT),))

    report = contrast_check.analyze(_repo(tmp_path))

    assert report.errors
    assert report.missing == ("DELETED_COLOR",)
    assert "absent from the palette" in contrast_check.format_report(report, matrix=False)


def test_the_verdict_is_judged_at_the_precision_it_is_printed_at(tmp_path: Path, declare) -> None:
    """`#767676` on white is 4.5422 - it must not read as 4.54 and fail 4.5."""
    theme = THEME_SOURCE.replace('FAINT = "#AAAAAA"', 'FAINT = "#767676"')
    declare((_requirement("FAINT", "PANEL", contrast_check.AA_TEXT),))

    report = contrast_check.analyze(_repo(tmp_path, theme=theme))

    assert not report.errors


# --- the real palette -------------------------------------------------------


def test_the_shipped_palette_holds(capsys: pytest.CaptureFixture[str]) -> None:
    """The check `make check` runs, run here so a red palette fails the suite too."""
    assert contrast_check.main(["--root", str(REPO_ROOT)]) == 0
    assert "0 errors" in capsys.readouterr().out


def test_the_run_status_text_is_checked_against_the_page_background() -> None:
    """The regression guard for PL-X0RG: this table once assumed the wrong surface.

    `mount()` puts the run-status word in a top-level `Column` with no
    background of its own, so it is drawn on `BACKGROUND`, not `PANEL`. The
    first version of this table asserted it against `PANEL` - the lighter of
    the two - which measured a pair that does not exist and let the real one
    pass unread. `BACKGROUND` is darker, so it is the binding surface wherever
    a color appears on both, and `MUTED` failed there by more than the panel
    measurement showed.
    """
    declared = {
        (requirement.foreground, requirement.background)
        for requirement in contrast_check.REQUIREMENTS
    }

    for foreground in ("MUTED", "ACCENT", "WARNING"):
        assert (foreground, "BACKGROUND") in declared, (
            f"{foreground} is a run-status color drawn on the page background; "
            "a requirement naming only PANEL checks a pair that is not on screen"
        )


def test_muted_clears_the_text_minimum_on_both_surfaces() -> None:
    """PL-X0RG. It was 4.28 on the panel and 3.98 on the page background."""
    palette = contrast_check.read_palette(REPO_ROOT)

    for surface in ("PANEL", "BACKGROUND"):
        ratio = contrast_check.contrast_ratio(palette["MUTED"], palette[surface])
        assert round(ratio, 2) >= contrast_check.AA_TEXT, f"MUTED on {surface} is {ratio:.2f}"


def test_every_known_shortfall_names_an_item_that_exists() -> None:
    """A shortfall excused by an id nobody filed is an excuse, not a plan."""
    filed = {
        path.name.split("-")[0] + "-" + path.name.split("-")[1]
        for path in (REPO_ROOT / "docs" / "items").glob("PL-*.md")
    }

    for pair, item in contrast_check.KNOWN_SHORTFALLS.items():
        assert item in filed, f"{pair[0]} on {pair[1]} is excused by {item}, which is not filed"
