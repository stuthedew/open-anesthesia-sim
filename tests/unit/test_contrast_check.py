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

from itertools import combinations
from pathlib import Path

import contrast_check
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

THEME_SOURCE = '''"""Miniature theme."""

PANEL = "#FFFFFF"
INK = "#243B53"
FAINT = "#AAAAAA"
TRACE_ONE = INK
TRACE_TWO = "#DC2626"

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
    """`CIRCUIT_COLOR = PRIMARY` is how half the real trace colors are defined.

    Same-module since PL-2CS8 moved them into the theme; the resolution being
    tested is the same one, and it is what keeps an aliased trace in the
    palette rather than silently absent.
    """
    palette = contrast_check.read_palette(_repo(tmp_path))

    assert palette["INK"] == "#243B53"
    assert palette["TRACE_ONE"] == "#243B53", "a name reference was not resolved"
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


# --- dichromacy simulation, and the trace separation it is there for ---------


def test_the_neutral_axis_survives_every_dichromacy_simulation() -> None:
    """Brettel's reduced surface contains the neutral axis, so greys are fixed.

    The one property of the projection that is exact rather than approximate,
    which makes it the right thing to hold the transcribed coefficients to: a
    mistyped digit anywhere in the nine of a matrix, or a swapped row, moves a
    grey off itself. Asserted across the range rather than at one value
    because the two half-planes meet at this axis, so a grey also exercises
    the plane-selection branch on its boundary.
    """
    for level in range(0, 256, 5):
        grey = f"#{level:02X}{level:02X}{level:02X}"
        for model in contrast_check.DICHROMACY_TRANSFORMS:
            assert contrast_check.simulate_dichromacy(grey, model) == grey, (
                f"{model} moved the neutral grey {grey}"
            )


@pytest.mark.parametrize("model", ["protanopia", "deuteranopia"])
@pytest.mark.parametrize("primary", ["#FF0000", "#00FF00"])
def test_the_red_green_axis_collapses_for_a_protanope_and_a_deuteranope(
    model: str, primary: str
) -> None:
    """Both primaries land in the yellow region, which is the deficiency itself.

    A protanope and a deuteranope are missing one of the two long-wavelength
    pigments, so the red-green opponent signal is gone and both primaries
    project onto the yellow-blue axis the remaining pigments still carry. In
    sRGB that reads as a near-equal red and green channel over a much smaller
    blue one. This is the behaviour the simulation exists to model, so a
    transform that left red red would be wrong in the way that matters here
    even if it were arithmetically self-consistent.
    """
    simulated = contrast_check.simulate_dichromacy(primary, model)
    red, green, blue = (int(simulated[index : index + 2], 16) for index in (1, 3, 5))

    assert abs(red - green) < 0.25 * max(red, green), f"{primary} kept a red-green difference"
    assert blue < 0.25 * max(red, green), f"{primary} did not lose its blue channel"


@pytest.mark.parametrize("bad", ["", "#12345", "not a color", "#GGGGGG"])
def test_a_malformed_color_is_refused_by_the_simulation_too(bad: str) -> None:
    """Same contract as `relative_luminance`: refuse rather than guess."""
    with pytest.raises(ValueError):
        contrast_check.simulate_dichromacy(bad, "protanopia")


def test_an_unknown_vision_model_is_refused() -> None:
    """A typo would otherwise silently pick one deficiency and report another."""
    with pytest.raises(ValueError, match="protanopia"):
        contrast_check.simulate_dichromacy("#DC2626", "protanomaly")


def test_as_seen_leaves_a_color_alone_under_normal_vision() -> None:
    """The uniform path over `VISION_MODELS` needs the identity to be one of them."""
    assert contrast_check.as_seen("#DC2626", "normal") == "#DC2626"
    assert contrast_check.VISION_MODELS[0] == "normal"


def test_every_trace_contrast_clears_the_floor_in_all_four_vision_models() -> None:
    """PL-GVXP. The floor a normal-vision check cannot see all of.

    `ALVEOLAR_COLOR` failed as displayed, at 2.93:1. `MUSCLE_COLOR` passed as
    displayed, at 3.19:1, and failed at 2.98:1 simulated for deuteranopia -
    which is the case that argues for measuring four models rather than one,
    because nothing about the shipped colour said it was close.
    """
    palette = contrast_check.read_palette(REPO_ROOT)

    for name in contrast_check.TRACES:
        for model in contrast_check.VISION_MODELS:
            ratio = contrast_check.contrast_ratio(
                contrast_check.as_seen(palette[name], model), palette["PANEL"]
            )
            assert round(ratio, contrast_check.DISPLAY_DECIMALS) >= contrast_check.TRACE_FLOOR, (
                f"{name} is {ratio:.2f} against the panel under {model}"
            )


def test_a_trace_below_the_floor_in_one_model_alone_is_an_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, declare
) -> None:
    """The regression guard for the case that motivated the check.

    A trace that clears the floor as displayed and misses it under one
    simulated dichromacy has to fail, or the extra three models are decoration.
    `#D97706` is the muscle colour this item replaced, at 3.19:1 as displayed
    and 2.98:1 for a deuteranope.
    """
    declare(())
    root = _repo(tmp_path, view=VIEW_SOURCE + '\nMUSCLE_COLOR = "#D97706"\n')
    monkeypatch.setattr(contrast_check, "TRACES", ("MUSCLE_COLOR",))

    report = contrast_check.analyze(root)

    assert report.errors
    assert [(name, model) for name, model, _ in report.below_trace_floor] == [
        ("MUSCLE_COLOR", "deuteranopia")
    ]


def test_a_trace_clearing_the_floor_everywhere_is_quiet(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, declare
) -> None:
    """The shipped replacement, so the guard above is not passing by accident."""
    declare(())
    root = _repo(tmp_path, view=VIEW_SOURCE + '\nMUSCLE_COLOR = "#D17206"\n')
    monkeypatch.setattr(contrast_check, "TRACES", ("MUSCLE_COLOR",))

    assert contrast_check.analyze(root).below_trace_floor == ()


def test_no_two_trace_contrasts_reach_the_non_text_minimum() -> None:
    """The finding the line styles exist for, pinned so it cannot quietly change.

    Not an aspiration that failed: it is unreachable. The 3:1 floor above caps
    every trace's luminance, and six traces cannot then be more than
    `separation_ceiling_above_floor` apart pairwise. A future palette that
    appeared to clear 3:1 here would mean the arithmetic had been broken rather
    than the problem solved, so this asserts the ceiling holds as well as the
    measured worst pair.
    """
    palette = contrast_check.read_palette(REPO_ROOT)
    ceiling = contrast_check.separation_ceiling_above_floor(
        len(contrast_check.TRACES), contrast_check.TRACE_FLOOR
    )

    assert ceiling < contrast_check.AA_NON_TEXT
    for first, second in combinations(contrast_check.TRACES, 2):
        for model in contrast_check.VISION_MODELS:
            ratio = contrast_check.contrast_ratio(
                contrast_check.as_seen(palette[first], model),
                contrast_check.as_seen(palette[second], model),
            )
            assert ratio < contrast_check.AA_NON_TEXT, (
                f"{first}/{second} reads {ratio:.2f} under {model}, which the bounded "
                "luminance axis does not admit"
            )


def test_the_worst_trace_contrast_pair_is_the_one_docs_model_records() -> None:
    """`docs/MODEL.md` prints this matrix, and a stale table there misleads.

    The whole section argues from the closest pair. Pinning it here means a
    colour edit that changes which pair is closest fails the suite instead of
    leaving the document asserting a pair that is no longer the worst.
    """
    palette = contrast_check.read_palette(REPO_ROOT)
    worst = min(
        (
            contrast_check.contrast_ratio(
                contrast_check.as_seen(palette[first], model),
                contrast_check.as_seen(palette[second], model),
            ),
            first,
            second,
        )
        for first, second in combinations(contrast_check.TRACES, 2)
        for model in contrast_check.VISION_MODELS
    )

    assert round(worst[0], 2) == 1.01
    assert (worst[1], worst[2]) == ("VESSEL_RICH_COLOR", "FAT_COLOR")


def test_the_separation_ceiling_falls_once_every_trace_must_clear_the_panel() -> None:
    """The bound `docs/MODEL.md` and `.claude/rules/ui-color.md` both quote.

    Holding a trace to 3:1 against a white panel caps its luminance at 0.30,
    which shortens the axis six traces spread along: 1.84 unconstrained, 1.48
    with the floor. The direction is the point - the floor makes colour a
    *weaker* channel, not a stronger one.
    """
    unconstrained = contrast_check.separation_ceiling(6)
    constrained = contrast_check.separation_ceiling_above_floor(6, contrast_check.AA_NON_TEXT)

    assert round(unconstrained, 2) == 1.84
    assert round(constrained, 2) == 1.48
    assert constrained < unconstrained
    # A floor of 1:1 admits every color, so the two definitions must agree.
    assert contrast_check.separation_ceiling_above_floor(6, 1.0) == pytest.approx(unconstrained)


@pytest.mark.parametrize("count, floor", [(1, 3.0), (6, 0.5)])
def test_a_constrained_ceiling_refuses_arguments_it_cannot_answer(count: int, floor: float) -> None:
    """One trace has no pair, and a contrast ratio has no value below 1:1."""
    with pytest.raises(ValueError):
        contrast_check.separation_ceiling_above_floor(count, floor)


def test_the_two_agent_fills_iso_5360_makes_inseparable_stay_measured() -> None:
    """`docs/MODEL.md` prints these four numbers, and once printed them wrongly.

    ISO 5360 fixes isoflurane's purple and desflurane's blue, so the pair is
    not this project's to re-pick and the mitigation is that the agent name is
    always drawn alongside. What is this project's to keep honest is the claim
    about how bad the pair is: the document said the simulated ratios fell to
    1.1-1.4, and measured they run 1.06 to 1.48 - wrong at both ends, and wrong
    in direction for protanopia, where the pair separates rather than
    collapsing. The conclusion did not change, which is exactly why nobody
    re-measured it for a year.
    """
    palette = contrast_check.read_palette(REPO_ROOT)
    measured = {
        model: round(
            contrast_check.contrast_ratio(
                contrast_check.as_seen(palette["isoflurane.fill"], model),
                contrast_check.as_seen(palette["desflurane.fill"], model),
            ),
            2,
        )
        for model in contrast_check.VISION_MODELS
    }

    assert measured == {
        "normal": 1.09,
        "protanopia": 1.48,
        "deuteranopia": 1.06,
        "tritanopia": 1.11,
    }


# --- colors live in the theme (PL-2CS8) -------------------------------------


def test_a_color_declared_in_the_view_is_refused(tmp_path: Path) -> None:
    """The convention PL-2CS8 established, held by the tool rather than by habit."""
    root = _repo(tmp_path, view=VIEW_SOURCE + '\nSTRAY = "#123456"\n')

    misplaced = contrast_check.check_colors_live_in_the_theme(root)

    assert any("STRAY" in message for message in misplaced)
    assert any("theme.py" in message for message in misplaced)


def test_a_view_color_aliasing_a_theme_name_is_refused_too(tmp_path: Path) -> None:
    """Resolution runs against the theme first, so an alias cannot slip through.

    `STRAY = INK` carries no `#` of its own; only resolving it against the
    theme's palette shows it is a color at all.
    """
    root = _repo(tmp_path, view=VIEW_SOURCE + "\nSTRAY = INK\n")

    assert any(
        "STRAY" in message for message in contrast_check.check_colors_live_in_the_theme(root)
    )


def test_a_non_color_string_in_the_view_is_left_alone(tmp_path: Path) -> None:
    """`NOT_A_COLOUR = "solid"` is a dash style, and the rule is about colors."""
    assert contrast_check.check_colors_live_in_the_theme(_repo(tmp_path)) == ()


def test_a_misplaced_color_fails_the_build(tmp_path: Path, declare) -> None:
    """An advisory would not hold a convention; this has to be an error."""
    declare(())
    root = _repo(tmp_path, view=VIEW_SOURCE + '\nSTRAY = "#123456"\n')

    report = contrast_check.analyze(root)

    assert report.errors
    assert "Colors declared outside the theme" in contrast_check.format_report(report, matrix=False)


def test_the_shipped_view_declares_no_color() -> None:
    """The real tree, which is what PL-2CS8 actually changed."""
    assert contrast_check.check_colors_live_in_the_theme(REPO_ROOT) == ()
