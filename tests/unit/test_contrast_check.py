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


VIEW_WITH_SYMBOLS = '''"""Miniature view holding each kind of name a description can cite."""

import flet as ft

from anesthesia_sim.app.theme import INK, PANEL

TRACE_ONE = INK


class SimulationView:
    def __init__(self) -> None:
        self._status_text = ft.Text("Paused", color=INK)

    def mount(self) -> None:
        pass

    async def _run_render_timer(self) -> None:
        pass
'''


def _repo(tmp_path: Path, *, theme: str = THEME_SOURCE, view: str = VIEW_SOURCE) -> Path:
    """Build a miniature repository holding only the two color-defining modules."""
    app = tmp_path / "src" / "anesthesia_sim" / "app"
    app.mkdir(parents=True)
    (app / "theme.py").write_text(theme, encoding="utf-8")
    (app / "simulation_view.py").write_text(view, encoding="utf-8")
    return tmp_path


def _requirement(
    foreground: str, background: str, minimum: float, why: str = "a fixture"
) -> contrast_check.Requirement:
    return contrast_check.Requirement(
        foreground=foreground, background=background, minimum=minimum, criterion="1.4.3", why=why
    )


def _either(
    foregrounds: tuple[str, ...], background: str, minimum: float, why: str = "a fixture"
) -> contrast_check.EitherRequirement:
    return contrast_check.EitherRequirement(
        foregrounds=foregrounds, background=background, minimum=minimum, criterion="1.4.11", why=why
    )


@pytest.fixture
def declare(monkeypatch: pytest.MonkeyPatch):
    """Substitute the requirement table and the shortfall list for one test."""

    def _declare(
        requirements: tuple[contrast_check.AnyRequirement, ...],
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


def test_a_requirement_met_by_either_channel(tmp_path: Path, declare) -> None:
    """PL-GNN1. The badge case: an edge carried by the fill *or* by the border.

    Both halves matter. Passing on a candidate that is not the first is what a
    single-pair requirement could not express - it reported the sevoflurane
    badge as a shortfall while that badge's border stood at 10.70:1 against
    the page. Failing when every channel is weak is what stops the new kind
    becoming an excuse: an element nobody can perceive by any of its channels
    is a shortfall however many channels it declares.

    The fixture reproduces the shipped shape rather than inventing one.
    `demoflurane.foreground` is white on a white surface - 1.00:1, the
    near-invisible border isoflurane and desflurane really have - while the
    fill behind it stands at 6.52:1.
    """
    repo = _repo(tmp_path)
    declare(
        (
            _either(
                ("demoflurane.foreground", "demoflurane.fill"), "PANEL", contrast_check.AA_NON_TEXT
            ),
        )
    )

    carried = contrast_check.analyze(repo)

    assert not carried.errors
    assert carried.results[0].meets
    assert carried.results[0].rounded == 6.52, "the best channel decides it, not the first"

    declare((_either(("demoflurane.foreground", "FAINT"), "PANEL", contrast_check.AA_NON_TEXT),))

    weak = contrast_check.analyze(repo)

    assert weak.errors
    assert weak.results[0].rounded == 2.32, "the best of two weak channels is still the best"
    assert "demoflurane.foreground or FAINT on PANEL" in contrast_check.format_report(
        weak, matrix=False
    )


def test_a_two_channel_shortfall_is_excused_under_both_names(tmp_path: Path, declare) -> None:
    """A disjunction is keyed by what the report prints, so its entry is findable."""
    declare(
        (_either(("demoflurane.foreground", "FAINT"), "PANEL", contrast_check.AA_NON_TEXT),),
        {("demoflurane.foreground or FAINT", "PANEL"): "PL-DEMO"},
    )

    report = contrast_check.analyze(_repo(tmp_path))

    assert not report.errors
    assert "PL-DEMO" in contrast_check.format_report(report, matrix=False)


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


# --- citations into the code ------------------------------------------------


def test_the_symbol_reader_finds_every_kind_of_name_a_description_can_cite(tmp_path: Path) -> None:
    """Constants, classes, methods - sync and async - and `self.X` attributes."""
    symbols = contrast_check.read_symbols(_repo(tmp_path, view=VIEW_WITH_SYMBOLS))

    assert {"PANEL", "TRACE_ONE", "SimulationView", "mount", "_run_render_timer"} <= symbols
    assert "_status_text" in symbols, "an attribute a control is built into is citable"
    assert "_no_such_symbol" not in symbols


def test_a_citation_that_resolves_is_quiet(tmp_path: Path, declare) -> None:
    """A checker that fires on correct work gets disabled, which is worse than none."""
    declare((_requirement("INK", "PANEL", 4.5, why="the run-status word (`_status_text`)"),))

    assert contrast_check.check_citations(_repo(tmp_path, view=VIEW_WITH_SYMBOLS)) == ()


def test_a_cited_symbol_that_does_not_exist_is_an_error(tmp_path: Path, declare) -> None:
    """The regression guard for PL-GJDW: a renamed symbol must not fail silently."""
    declare((_requirement("INK", "PANEL", 4.5, why="drawn by `_renamed_away`"),))

    errors = contrast_check.check_citations(_repo(tmp_path, view=VIEW_WITH_SYMBOLS))

    assert len(errors) == 1
    assert "_renamed_away" in errors[0]


@pytest.mark.parametrize("cited", ["simulation_view.py:320", "simulation_view.py:248-257"])
def test_a_line_number_citation_is_refused(tmp_path: Path, declare, cited: str) -> None:
    """Both forms the table used to carry. PL-GJDW: every one of them had rotted."""
    declare((_requirement("INK", "PANEL", 4.5, why=f"the slider track ({cited})"),))

    errors = contrast_check.check_citations(_repo(tmp_path, view=VIEW_WITH_SYMBOLS))

    assert len(errors) == 1
    assert cited in errors[0]


def test_an_unresolved_citation_fails_the_run(tmp_path: Path, declare) -> None:
    """It is an error, not an advisory: `make check` has to stop on it."""
    declare((_requirement("INK", "PANEL", 4.5, why="drawn by `_renamed_away`"),))

    assert contrast_check.analyze(_repo(tmp_path, view=VIEW_WITH_SYMBOLS)).errors


@pytest.mark.parametrize("span", ["`docs/MODEL.md`", "`.claude/rules/ui-color.md`"])
def test_a_backticked_path_is_not_read_as_a_symbol(tmp_path: Path, declare, span: str) -> None:
    """Descriptions cite documents as well as code; only bare names are symbols."""
    declare((_requirement("INK", "PANEL", 4.5, why=f"required by {span}"),))

    assert contrast_check.check_citations(_repo(tmp_path, view=VIEW_WITH_SYMBOLS)) == ()


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
    declared = {requirement.key for requirement in contrast_check.REQUIREMENTS}

    for foreground in ("MUTED", "ACCENT_TEXT", "WARNING"):
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


def test_every_agent_badge_is_checked_as_fill_or_border() -> None:
    """PL-GNN1. Each badge is legible by a different one of its two channels.

    Sevoflurane by its border, isoflurane and desflurane by their fills. Three
    different accidents, which is the reason to declare both channels rather
    than pick whichever one happens to work today.

    The agents are read from the palette, not listed here, because the accident
    is the point: an agent added later whose fill is mid-tone and whose
    foreground is white is invisible by either channel, and nothing else in
    this file would notice that its badge had never been declared at all.
    """
    palette = contrast_check.read_palette(REPO_ROOT)
    declared = {
        requirement.key: requirement
        for requirement in contrast_check.REQUIREMENTS
        if isinstance(requirement, contrast_check.EitherRequirement)
    }
    # Read from the palette rather than named here, so that adding a fourth
    # agent to `theme.py` and declaring nothing for its badge fails this test
    # instead of passing unread.
    agents = sorted(name.removesuffix(".fill") for name in palette if name.endswith(".fill"))

    assert agents, "no agent schemes were read; this test would assert nothing"
    for agent in agents:
        key = (f"{agent}.fill or {agent}.foreground", "BACKGROUND")
        assert key in declared, f"{agent}'s badge is not declared as fill or border"
        best = max(
            contrast_check.contrast_ratio(palette[name], palette["BACKGROUND"])
            for name in declared[key].candidates
        )
        assert round(best, 2) >= contrast_check.AA_NON_TEXT, (
            f"{agent}'s badge is {best:.2f} by its best channel"
        )


def test_every_requirement_names_a_symbol_that_exists() -> None:
    """PL-GJDW. Fourteen line numbers were cited here and not one still landed.

    `test_the_shipped_palette_holds` covers this through `main`; it is asserted
    separately because the defect was in the descriptions rather than in the
    arithmetic, and a failure should say so.
    """
    assert contrast_check.check_citations(REPO_ROOT) == ()


def test_every_known_shortfall_names_an_item_that_exists() -> None:
    """A shortfall excused by an id nobody filed is an excuse, not a plan."""
    filed = {
        path.name.split("-")[0] + "-" + path.name.split("-")[1]
        for path in (REPO_ROOT / "docs" / "items").glob("PL-*.md")
    }

    for pair, item in contrast_check.KNOWN_SHORTFALLS.items():
        assert item in filed, f"{pair[0]} on {pair[1]} is excused by {item}, which is not filed"
