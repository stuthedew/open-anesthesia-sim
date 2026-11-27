"""Tests of what one frame of the chart claims, checked without a GUI toolkit.

`app/chart_frame.py` is where the chart's presentation-correctness claims
live. They include which compartment a curve shows, where the reference
lines sit, which instants are drawn, and what a hover says. Every test here
runs with no display and no plotting library, which is the purpose of that
module.
"""

from dataclasses import dataclass, replace
from functools import cache
from math import hypot, inf, nextafter
from pathlib import Path
from types import MappingProxyType

import pytest
from test_numerical_envelope import _squarings

from anesthesia_sim.app.bookmarks import TimeBookmark
from anesthesia_sim.app.chart_frame import (
    CHART_COLUMN_BUDGET_PER_SERIES,
    COMPARED_COMPARTMENT_CAP,
    COMPARTMENT_TRACES,
    MAX_CHART_CONTROL_MARKS,
    WASH_IN_HOVER_LABEL,
    WASH_IN_HOVER_PAST_EQUILIBRIUM_TEXT,
    WASH_IN_TERMINUS_CEILING,
    ChartFrame,
    PreviewRequest,
    RunCount,
    RunFrame,
    RunIndex,
    RunInput,
    WashInStretch,
    assemble_chart_frame,
    chart_columns,
    compared_compartments,
    format_compared_trace_hover,
    format_compared_wash_in_hover,
    format_trace_hover,
    format_wash_in_hover,
    latest_values_lines,
    nearest_trace_point,
    nearest_wash_in_point,
    percent_axis_ticks,
    preview_stroke_width,
    preview_trace_style,
    resample_owed,
    run_trace_style,
    trace_style,
    wash_in_axis_ticks,
    wash_in_stretches,
)
from anesthesia_sim.app.chart_time_base import TIME_BASE_LADDER, grid_spacing_s, time_base_for_span
from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.control_timeline import ControlAdjustment
from anesthesia_sim.app.controller import (
    PREVIEW_EXACT_S,
    BranchedCase,
    SettingPreview,
    SimulationController,
    _with_later_crossings,
)
from anesthesia_sim.app.dashboard_frame import (
    concentration_chart_description,
    concentration_chart_name,
    run_label,
)
from anesthesia_sim.app.failures import FailureKind
from anesthesia_sim.app.formatting import (
    ChartCeiling,
    chart_axis_top_percent,
    format_elapsed,
    format_mac_multiple,
    format_percent,
    format_wash_in_ratio,
    mac_awake_band_percent,
    mac_axis_ticks,
)
from anesthesia_sim.app.run_series import (
    COMPARTMENT_FRACTION_NAMES,
    COMPARTMENT_QUANTITIES,
    COMPARTMENT_STATE_INDEX,
    DrawnWindow,
    RecordedQuantity,
    RecordedSeries,
)
from anesthesia_sim.app.theme import (
    CHART_HEIGHT,
    COMPARED_RUN_WIDTH_STEP,
    MINIMUM_TRACE_STROKE_WIDTH,
    ONE_MAC_LINE_DASH_PATTERN,
)
from anesthesia_sim.app.wash_in import is_wash_in, read_wash_in, wash_in_ratio
from anesthesia_sim.core.concentration import Fraction, MacPercent, Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    FIRST_TISSUE_FRACTION,
    FRACTION_STATE_NAMES,
    INSPIRED_FRACTION,
    VENOUS_FRACTION,
    build_system_matrix,
)
from anesthesia_sim.core.mac import mac_for_patient
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.prediction import predicted_states
from anesthesia_sim.core.rounding import propagator_rounding, run_rounding
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import CaseInstant, FreshGasFlow, StepCount
from anesthesia_sim.core.uptake_system import AgentUptakeSystem
from anesthesia_sim.layout.run_identity import RunId, SessionToken

# The identities a dashboard gives the first runs it places, in order, which
# render as "Run 1", "Run 2" and "Run 3". A run is named from its identity
# rather than from where it is drawn (`PL-7Z84`).
TEST_SESSION = SessionToken("0" * 32)
RUN_IDS = tuple(RunId(TEST_SESSION, number) for number in (1, 2, 3))
FIRST_RUN, SECOND_RUN = RUN_IDS[:2]


_PLOT_WIDTH_PX = 900.0

#: The frames below are sevoflurane's, so they divide by sevoflurane's stored
#: 1 MAC. A frame that names sevoflurane and divides by another MAC would
#: print MAC multiples that the interface never shows for it, and the worked
#: examples in `docs/INTERFACE.md` were copied from such a frame (`PL-JP7P`).
_SEVOFLURANE = load_agent_parameters("sevoflurane")
_SEVOFLURANE_MAC = MacPercent(float(_SEVOFLURANE.mac_at_age_40_percent))
_SEVOFLURANE_AXIS_TOP = chart_axis_top_percent(_SEVOFLURANE_MAC, ChartCeiling.STANDARD)

#: The percent that one pixel of the concentration plot spans, for
#: sevoflurane: the fixed axis top of 3 MAC over the plot's height, which is
#: 5.4% over 360 px, or 0.015 %/px.
_PERCENT_PER_PIXEL = float(_SEVOFLURANE_AXIS_TOP) / CHART_HEIGHT

_INTERFACE_PATH = Path(__file__).resolve().parents[2] / "docs" / "INTERFACE.md"
_HOVER_SECTION_HEADING = "### The chart's hover readout: what the tooltip may show"


def _hover_worked_examples() -> list[list[str]]:
    """Each fenced example in `docs/INTERFACE.md`'s hover section, as its lines.

    The tests below compare the hover with these examples as the document
    prints them, so that an example and the hover cannot drift apart. Each
    example used to be typed out again here, and the copies divided by a
    1 MAC of 2.0% that sevoflurane no longer has (`PL-JP7P`).
    """

    text = _INTERFACE_PATH.read_text(encoding="utf-8")
    start = text.index(f"\n{_HOVER_SECTION_HEADING}\n")
    end = text.index("\n### ", start + 1)
    blocks = text[start:end].split("\n```\n")

    # The text alternates between prose and fenced blocks, so every second
    # piece after the first is an example.
    return [block.splitlines() for block in blocks[1::2]]


#: The second at which the hover examples' alveolar values are taken, and the
#: second at which the trunk is branched, both in simulated seconds.
_HOVER_EXAMPLE_S = 1208
_FORK_S = 600

#: The instants of the contended muscle and fat columns: twenty columns 4 s
#: apart around 20 min, as a 60-minute axis 900 px wide draws them.
_CONTENDED_TIMES_S = tuple(1160 + 4 * column for column in range(20))


@dataclass(frozen=True)
class _CaseAtTwentyMinutes:
    """The fractions that the hover examples print, from runs of the model.

    The trunk is the default sevoflurane case, opened at the stored 1 MAC with
    the default flows. At 10 min it is branched twice. One branch turns the
    vaporizer off, as in a case's emergence. The other raises the dial to
    1.9%, which keeps its alveolar point inside the hover radius of the
    trunk's. The examples in `docs/INTERFACE.md` were once typed from a run at
    a 2.0% dial labelled as 1 MAC, and these runs replace them (`PL-JP7P`).
    """

    trunk_alveolar: float
    raised_alveolar: float
    trunk_muscle: tuple[float, ...]
    trunk_fat: tuple[float, ...]
    emerging_muscle: tuple[float, ...]
    emerging_fat: tuple[float, ...]


@cache
def _case_at_twenty_minutes() -> _CaseAtTwentyMinutes:
    trunk = AgentUptakeSystem.for_agent("sevoflurane")
    for _ in range(_FORK_S):
        trunk.advance()
    emerging = AgentUptakeSystem.for_agent("sevoflurane")
    raised = AgentUptakeSystem.for_agent("sevoflurane")
    for branch, dial_percent in ((emerging, 0.0), (raised, 1.9)):
        branch.restore_state(trunk.capture_state())
        branch.set_delivered_concentration_percent(Percent(dial_percent))
    alveolar: dict[str, float] = {}
    columns: dict[str, list[float]] = {"tm": [], "tf": [], "em": [], "ef": []}
    for second in range(_FORK_S + 1, _CONTENDED_TIMES_S[-1] + 1):
        for system in (trunk, emerging, raised):
            system.advance()
        if second == _HOVER_EXAMPLE_S:
            alveolar["trunk"] = trunk.alveoli.partial_pressure_fraction
            alveolar["raised"] = raised.alveoli.partial_pressure_fraction
        if second in _CONTENDED_TIMES_S:
            columns["tm"].append(trunk.patient.muscle.partial_pressure_fraction)
            columns["tf"].append(trunk.patient.fat.partial_pressure_fraction)
            columns["em"].append(emerging.patient.muscle.partial_pressure_fraction)
            columns["ef"].append(emerging.patient.fat.partial_pressure_fraction)

    return _CaseAtTwentyMinutes(
        trunk_alveolar=alveolar["trunk"],
        raised_alveolar=alveolar["raised"],
        trunk_muscle=tuple(columns["tm"]),
        trunk_fat=tuple(columns["tf"]),
        emerging_muscle=tuple(columns["em"]),
        emerging_fat=tuple(columns["ef"]),
    )


def _advance(controller: SimulationController, seconds: int) -> None:
    for _ in range(seconds // SIMULATION_STEP_S):
        controller.advance()


def _run(seconds: int, agent_id: str = "sevoflurane") -> SimulationController:
    controller = SimulationController(agent_id=agent_id)
    controller.start()
    _advance(controller, seconds)

    return controller


def _input(controller: SimulationController, *marks_at_s: int, run_index: int = 0) -> RunInput:
    return RunInput(
        run_label(RUN_IDS[run_index]),
        controller,
        controller.snapshot(),
        tuple(
            ControlAdjustment(
                ControlInput.DELIVERED, CaseInstant(at_s), CaseInstant(at_s), 2.0, 4.0, 1
            )
            for at_s in marks_at_s
        ),
    )


def _snapshot_fractions(controller: SimulationController) -> dict[RecordedQuantity, float]:
    snapshot = controller.snapshot()

    return {
        RecordedQuantity.CIRCUIT: snapshot.inspired_partial_pressure_fraction,
        RecordedQuantity.ALVEOLAR: snapshot.alveolar_partial_pressure_fraction,
        RecordedQuantity.MIXED_VENOUS: snapshot.mixed_venous_partial_pressure_fraction,
        RecordedQuantity.VESSEL_RICH: snapshot.vessel_rich_partial_pressure_fraction,
        RecordedQuantity.MUSCLE: snapshot.muscle_partial_pressure_fraction,
        RecordedQuantity.FAT: snapshot.fat_partial_pressure_fraction,
    }


# --------------------------------------------------------------- the table


def test_every_compartment_has_exactly_one_trace_in_listed_order() -> None:
    assert tuple(style.quantity for style in COMPARTMENT_TRACES) == COMPARTMENT_QUANTITIES

    for quantity in COMPARTMENT_QUANTITIES:
        assert trace_style(quantity).quantity is quantity

    with pytest.raises(KeyError):
        trace_style(RecordedQuantity.WASH_IN_RATIO)


def test_the_six_line_styles_are_the_ones_the_model_document_tabulates() -> None:
    """Each trace matches its row in `docs/INTERFACE.md` § "The six compartment traces".

    The dash pattern and the width are both in px.
    """

    table = {
        RecordedQuantity.CIRCUIT: (None, 3, "solid"),
        RecordedQuantity.ALVEOLAR: ((10, 4), 3, "long dash"),
        RecordedQuantity.MIXED_VENOUS: ((4, 3), 2, "short dash"),
        RecordedQuantity.VESSEL_RICH: ((6, 6), 2, "even dash"),
        RecordedQuantity.MUSCLE: ((2, 3), 2, "dotted"),
        RecordedQuantity.FAT: ((12, 4, 2, 4), 2, "dash-dot"),
    }

    for style in COMPARTMENT_TRACES:
        assert (style.dash_pattern, style.stroke_width, style.line_style) == table[style.quantity]


def test_no_two_traces_are_separated_by_colour_alone() -> None:
    patterns = [style.dash_pattern for style in COMPARTMENT_TRACES]

    assert len(set(patterns)) == len(patterns)


def test_no_trace_dash_is_as_wide_as_the_one_mac_reference_line() -> None:
    widest_dash, widest_gap = ONE_MAC_LINE_DASH_PATTERN

    for style in COMPARTMENT_TRACES:
        if style.dash_pattern is None:
            continue

        assert max(style.dash_pattern[0::2]) < widest_dash, style.label
        assert max(style.dash_pattern[1::2]) < widest_gap, style.label


def test_the_hover_gloss_is_the_readout_row_s_required_hedge() -> None:
    """`PL-NV9W` and `PL-8M05`: only two compartments get a hover gloss.

    They are the two compartments that a clinician would compare with a monitor.
    """

    glosses = {style.quantity: style.gloss for style in COMPARTMENT_TRACES}

    assert glosses[RecordedQuantity.CIRCUIT] == "inspired"
    assert glosses[RecordedQuantity.ALVEOLAR] == "end-tidal-equivalent"
    assert all(
        glosses[quantity] is None
        for quantity in COMPARTMENT_QUANTITIES
        if quantity not in (RecordedQuantity.CIRCUIT, RecordedQuantity.ALVEOLAR)
    )


# ----------------------------------------------------------------- the frame


def test_every_trace_of_a_run_draws_the_same_instants_and_ends_at_the_readout() -> None:
    controller = _run(600)
    frame = assemble_chart_frame(
        [_input(controller)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    run = frame.runs[0]

    assert run.times_s[-1] == pytest.approx(controller.snapshot().elapsed_s)
    assert run.times_s == tuple(sorted(run.times_s))

    for quantity, shown in _snapshot_fractions(controller).items():
        assert len(run.fractions[quantity]) == len(run.times_s)
        # The score's evaluation and the compartment's own canonical state
        # agree only to within the rounding of composed floating-point steps.
        assert run.fractions[quantity][-1] == pytest.approx(shown, abs=1e-8)
        assert run.percents(quantity)[-1] == pytest.approx(shown * 100.0, abs=1e-6)


def test_the_frame_refuses_no_runs_and_runs_on_different_agents() -> None:
    with pytest.raises(ValueError, match="at least one run"):
        assemble_chart_frame(
            [],
            None,
            COMPARTMENT_QUANTITIES,
            plot_width_px=_PLOT_WIDTH_PX,
            held_start_s=None,
            ceiling=ChartCeiling.STANDARD,
        )

    with pytest.raises(ValueError, match="same agent"):
        assemble_chart_frame(
            [_input(_run(10)), _input(_run(10, "desflurane"))],
            None,
            COMPARTMENT_QUANTITIES,
            plot_width_px=_PLOT_WIDTH_PX,
            held_start_s=None,
            ceiling=ChartCeiling.STANDARD,
        )


def test_the_frame_refuses_a_newest_instant_not_built_as_one() -> None:
    """The window is placed from a checked instant, and the frame checks it once (`PL-9DF9`).

    `fit_to_run` and `following_window` only compare the instant. So a
    snapshot carrying a bare number past the supported run length must be
    rejected before either window is formed from it.
    """

    run = _input(_run(10))
    stale = replace(run, snapshot=replace(run.snapshot, elapsed_s=1e9))

    with pytest.raises(TypeError, match="newest_instant_s of 1000000000.0 was not built as"):
        assemble_chart_frame(
            [stale],
            None,
            COMPARTMENT_QUANTITIES,
            plot_width_px=_PLOT_WIDTH_PX,
            held_start_s=None,
            ceiling=ChartCeiling.STANDARD,
        )


def test_the_window_fits_the_longer_of_two_runs_and_both_draw_into_it() -> None:
    short, long = _run(60), _run(500)
    frame = assemble_chart_frame(
        [_input(short), _input(long)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert frame.fitted
    assert frame.start_s == 0.0
    assert frame.stop_s >= 500.0
    assert frame.runs[0].times_s[-1] == pytest.approx(60.0)
    assert frame.runs[1].times_s[-1] == pytest.approx(500.0)


def test_the_fitted_window_reaches_a_branch_s_newest_instant_rather_than_its_length() -> None:
    """ "Fit run" reaches the case's current instant, which for a branch is later than its length.

    A branch starts at its fork on the case's own time axis. Its current
    instant is therefore the fork plus the time it has run since: here 150 s,
    against 30 s of its own. The fitted window is pinned at induction, so its
    width has to reach that instant. If the window were fitted to the runs'
    lengths instead, it would end at the trunk's 120 s. It would then draw the
    branch's whole half-minute as one point at its fork (`PL-59WB`).
    """

    trunk = _run(120)
    trunk.begin_control_adjustment()
    trunk.set_fresh_gas_flow(FreshGasFlow(3.0))
    branch = BranchedCase(trunk).fork_at(CaseInstant(120))
    branch.start()
    _advance(branch, 30)
    newest_s = branch.snapshot().elapsed_s
    frame = assemble_chart_frame(
        (_input(trunk), _input(branch, run_index=1)),
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert (branch.began_at_s, newest_s) == pytest.approx((120.0, 150.0))
    assert frame.start_s == 0.0
    # The frame uses the narrowest rung that reaches the instant, not a coarser one.
    assert frame.time_base == next(base for base in TIME_BASE_LADDER if base.span_s >= newest_s)
    assert frame.runs[1].times_s[0] == pytest.approx(120.0)
    assert frame.runs[1].times_s[-1] == pytest.approx(newest_s)


def test_a_chosen_width_is_held_exactly_and_follows_the_run() -> None:
    controller = _run(1200)
    base = time_base_for_span(900.0)
    frame = assemble_chart_frame(
        [_input(controller)],
        base,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert not frame.fitted
    assert frame.time_base == base
    assert frame.stop_s - frame.start_s == pytest.approx(900.0)
    assert frame.start_s < 1200.0 < frame.stop_s
    assert frame.runs[0].times_s[0] >= frame.start_s
    assert frame.columns == chart_columns(900.0)
    assert all(tick % base.tick_interval_s == 0 for tick in frame.tick_times_s)


def test_hidden_traces_are_left_out_of_the_visible_set_but_still_evaluated() -> None:
    controller = _run(60)
    frame = assemble_chart_frame(
        [_input(controller)],
        None,
        [RecordedQuantity.FAT, RecordedQuantity.CIRCUIT],
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert frame.visible == (RecordedQuantity.CIRCUIT, RecordedQuantity.FAT)
    assert set(frame.runs[0].fractions) == set(COMPARTMENT_QUANTITIES)


def test_the_references_are_placed_from_the_running_agent_s_own_values() -> None:
    for agent_id in ("sevoflurane", "isoflurane", "desflurane"):
        controller = _run(10, agent_id)
        snapshot = controller.snapshot()
        frame = assemble_chart_frame(
            [_input(controller)],
            None,
            COMPARTMENT_QUANTITIES,
            plot_width_px=_PLOT_WIDTH_PX,
            held_start_s=None,
            ceiling=ChartCeiling.STANDARD,
        )

        assert frame.mac_percent == snapshot.agent_mac_percent
        assert frame.one_mac_percent == snapshot.agent_mac_percent
        assert frame.axis_top_percent == chart_axis_top_percent(
            snapshot.agent_mac_percent, ChartCeiling.STANDARD
        )
        lower, upper = frame.mac_awake_band_percent
        assert lower < upper < frame.one_mac_percent
        assert frame.mac_ticks[-1] == (pytest.approx(frame.axis_top_percent), "3.0")


def test_control_marks_are_the_most_recent_that_fit_and_the_rest_are_counted() -> None:
    controller = _run(1200)
    inside = tuple(range(10, 10 + 5 * (MAX_CHART_CONTROL_MARKS + 6), 5))
    frame = assemble_chart_frame(
        [_input(controller, *inside, 5000)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    run = frame.runs[0]

    assert run.control_marks_s == inside[-MAX_CHART_CONTROL_MARKS:]
    assert run.undrawn_control_marks == 6


def test_a_mark_before_a_sliding_window_s_start_is_neither_drawn_nor_counted() -> None:
    """A chosen width that has slid past an early adjustment leaves it off the plot.

    The mark at 100 s is before the 15-minute window's start once the run has
    reached 1 200 s, so it is not drawn and is not counted as an undrawn mark
    in this window either.
    """

    controller = _run(1200)
    frame = assemble_chart_frame(
        [_input(controller, 100, 600)],
        time_base_for_span(900.0),
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    run = frame.runs[0]

    assert frame.start_s > 100.0
    assert run.control_marks_s == (600,)
    assert run.undrawn_control_marks == 0


def test_a_change_at_the_instant_a_fitted_window_ends_is_marked() -> None:
    """A fitted window ends at the run's newest instant, and a change made then is drawn.

    "Fit run" keeps no space to the right of the run, so a run of exactly
    15 minutes is drawn on the 15-minute width, which ends at 900 s
    (`ChartTimeBase.live_headroom_s`). A setting changed at that instant is
    marked at the live end of the curve it moves.
    """

    frame = assemble_chart_frame(
        [_input(_run(900), 900)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert frame.stop_s == 900.0
    assert frame.runs[0].control_marks_s == (900,)
    assert frame.runs[0].undrawn_control_marks == 0


def test_chart_columns_is_one_per_pixel_boundary_and_never_below_the_floor() -> None:
    """`PL-GS3R`: the count follows the plot's width, not the span, and rounds a fraction up."""

    for width in (0.0, 1.0, 100.0, 149.0):
        assert chart_columns(width) == CHART_COLUMN_BUDGET_PER_SERIES

    assert chart_columns(150.0) == 151
    assert chart_columns(1000.0) == 1001
    assert chart_columns(1000.4) == 1002

    for width in (-1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError, match="pixels wide"):
            chart_columns(width)


def test_a_plot_owes_a_frame_only_when_it_needs_more_columns_than_it_drew() -> None:
    """`PL-9LNF`: a wider plot needs a resample, and a narrower or equal one does not.

    The expected values come from `chart_columns`'s stated rule of one column
    per pixel boundary. A frame sampled at 900 px has 901 columns. A plot of
    900 or 899.5 px therefore needs no more columns, and a plot of 900.5 px
    needs 902.
    """

    run = _run(1200)
    frame = assemble_chart_frame(
        [_input(run)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert frame.columns == 901
    assert resample_owed(None, 0.0) is True
    assert resample_owed(frame, 899.5) is False
    assert resample_owed(frame, 900.0) is False
    assert resample_owed(frame, 400.0) is False
    assert resample_owed(frame, 900.5) is True
    assert resample_owed(frame, 1800.0) is True

    with pytest.raises(ValueError, match="pixels wide"):
        resample_owed(frame, float("nan"))


def test_no_chord_is_wider_than_one_pixel_of_time() -> None:
    """Check the guarantee in `docs/INTERFACE.md` § "What the chart draws" at every rung.

    A frame drawn for a plot `_PLOT_WIDTH_PX` wide divides the axis into at
    least that many intervals. Where a pixel spans a second or more,
    consecutive drawn instants are therefore never more than `span / width`
    apart, which is one pixel of time. Where a pixel spans less than a second,
    they are one second apart, because a run stands only on whole seconds
    (`PL-SZ6G`). On this plot those are the three rungs narrower than 15
    minutes. The test checks the drawn instants themselves rather than only
    the column count, because the plot draws its line segments between those
    instants.
    """

    controller = _run(1200)

    for base in TIME_BASE_LADDER:
        frame = assemble_chart_frame(
            [_input(controller)],
            base,
            COMPARTMENT_QUANTITIES,
            plot_width_px=_PLOT_WIDTH_PX,
            held_start_s=None,
            ceiling=ChartCeiling.STANDARD,
        )
        pixel_s = base.span_s / _PLOT_WIDTH_PX
        times = frame.runs[0].times_s

        assert frame.columns - 1 >= _PLOT_WIDTH_PX
        assert frame.plot_width_px == _PLOT_WIDTH_PX
        assert len(times) > 1
        assert max(b - a for a, b in zip(times, times[1:], strict=False)) <= max(
            pixel_s, SIMULATION_STEP_S
        )


def test_a_frame_refuses_a_width_that_is_not_a_width() -> None:
    """A frame with no valid width would otherwise be drawn silently at the minimum column count."""

    controller = _run(10)

    with pytest.raises(ValueError, match="pixels wide"):
        assemble_chart_frame(
            [_input(controller)],
            None,
            COMPARTMENT_QUANTITIES,
            plot_width_px=-1.0,
            held_start_s=None,
            ceiling=ChartCeiling.STANDARD,
        )


# ------------------------------------------------------------------ the axes


@pytest.mark.parametrize(
    ("mac_percent", "ceiling", "expected_percent", "expected_mac"),
    [
        (1.8, ChartCeiling.LOW, "0.0 0.5 1.0 1.5 2.0 2.5", "0.00 0.25 0.50 0.75 1.00 1.25 1.50"),
        (1.8, ChartCeiling.STANDARD, "0 1 2 3 4 5", "0.0 0.5 1.0 1.5 2.0 2.5 3.0"),
        (1.8, ChartCeiling.HIGH, "0 1 2 3 4 5 6 7 8", "0.0 0.5 1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5"),
        (1.17, ChartCeiling.LOW, "0.0 0.5 1.0 1.5", "0.00 0.25 0.50 0.75 1.00 1.25 1.50"),
        (1.17, ChartCeiling.STANDARD, "0 1 2 3", "0.0 0.5 1.0 1.5 2.0 2.5 3.0"),
        (1.17, ChartCeiling.HIGH, "0 1 2 3 4 5", "0.0 0.5 1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5"),
        (6.6, ChartCeiling.LOW, "0 2 4 6 8", "0.00 0.25 0.50 0.75 1.00 1.25 1.50"),
        (6.6, ChartCeiling.STANDARD, "0 5 10 15", "0.0 0.5 1.0 1.5 2.0 2.5 3.0"),
        (6.6, ChartCeiling.HIGH, "0 5 10 15 20 25", "0.0 0.5 1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5"),
    ],
)
def test_each_axis_is_labelled_at_round_values_of_its_own_unit(
    mac_percent: float, ceiling: ChartCeiling, expected_percent: str, expected_mac: str
) -> None:
    """The percent axis carries round percentages, and the MAC axis round MAC multiples.

    Each expected list is worked by hand. The MACs are Mapleson 1996's at age
    40 (PMID 8777094, abstract). The percent step is the finest of 1, 2 and 5
    times a power of ten that gives no more intervals than the MAC axis has,
    so isoflurane at the standard top, 3.51%, is labelled 0 to 3 in whole
    percent rather than at its half-MAC values, 0.585 and 1.755 (`PL-BNMZ`).
    Each label sits at the value it names.
    """

    frame_top = chart_axis_top_percent(MacPercent(mac_percent), ceiling)
    mac_ticks = mac_axis_ticks(frame_top, MacPercent(mac_percent))
    percent_ticks = percent_axis_ticks(frame_top, len(mac_ticks) - 1)

    assert " ".join(label for _, label in percent_ticks) == expected_percent
    assert " ".join(label for _, label in mac_ticks) == expected_mac
    assert len(percent_ticks) <= len(mac_ticks)

    for position, label in percent_ticks:
        assert position == pytest.approx(float(label))

    for position, label in mac_ticks:
        assert position == pytest.approx(float(label) * mac_percent)


def test_the_frame_draws_both_axes_at_the_top_it_carries() -> None:
    """A frame redrawn at another top gives that top's axes, and nothing else changes.

    The axes must follow the field rather than be fixed when the frame is
    assembled, so that a frame and its axes cannot name two tops (`PL-K1VH`).
    Each expected value is the top times desflurane's 6.6% MAC, worked by
    hand.
    """

    controller = _run(10, "desflurane")
    frame = assemble_chart_frame(
        [_input(controller)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    low = replace(frame, ceiling=ChartCeiling.LOW)

    assert frame.ceiling is ChartCeiling.STANDARD
    assert frame.axis_top_percent == pytest.approx(19.8)
    assert low.axis_top_percent == pytest.approx(9.9)
    assert low.mac_ticks[-1] == (pytest.approx(9.9), "1.50")
    assert low.percent_ticks[-1] == (pytest.approx(8.0), "8")
    assert low.runs is frame.runs


def test_the_percent_axis_refuses_a_flat_axis_or_no_interval() -> None:
    with pytest.raises(ValueError, match="top_percent must be strictly positive, got 0.0"):
        percent_axis_ticks(0.0, 6)

    with pytest.raises(ValueError, match="most_intervals must be at least 1, got 0"):
        percent_axis_ticks(6.0, 0)


def test_a_top_that_is_a_whole_number_of_round_steps_is_labelled_at_the_top() -> None:
    """A round step that divides the top exactly is used, and the top itself gets a label.

    In both cases the top divided by the allowed intervals is already a round
    step. The rounding allowance must count that step as fitting, rather than
    move on to the next coarser step. It must also count the top as a whole
    number of steps, so that the label at the top is not dropped. A 2% MAC at
    the standard top of 3 MAC gives the first case: a 6% axis beside a MAC
    axis of six half-MAC intervals. Each expected list is worked by hand.
    """

    assert percent_axis_ticks(6.0, 6) == tuple((float(step), str(step)) for step in range(7))
    assert percent_axis_ticks(1.0, 2) == ((0.0, "0.0"), (0.5, "0.5"), (1.0, "1.0"))


def test_the_percent_axis_accepts_a_single_interval_and_a_top_below_one_percent() -> None:
    """The axis refuses only a top that is not above zero, or fewer than one interval.

    A top of 0.5% is a valid axis, and one interval is the fewest that the
    axis may be divided into. The expected list is worked by hand: the step
    is the whole top, and a step of 0.5 is printed with one decimal.
    """

    assert percent_axis_ticks(0.5, 1) == ((0.0, "0.0"), (0.5, "0.5"))


def test_the_wash_in_axis_is_labelled_at_quarter_fractions_up_to_equilibrium() -> None:
    assert wash_in_axis_ticks() == (
        (0.0, "0.00"),
        (0.25, "0.25"),
        (0.5, "0.50"),
        (0.75, "0.75"),
        (1.0, "1.00"),
    )


# ------------------------------------------------------------- the stretches


def test_wash_in_stretches_break_where_the_domain_does_and_end_on_the_crossing() -> None:
    quotients = [None, None, 0.2, 0.5, 0.9, 1.002, 1.3, 1.1, 0.95, 1.0]

    assert wash_in_stretches(quotients, WASH_IN_TERMINUS_CEILING) == [(2, 6), (8, 10)]


def test_a_crossing_above_the_ceiling_is_not_drawn() -> None:
    assert wash_in_stretches([0.5, 0.9, 1.3], WASH_IN_TERMINUS_CEILING) == [(0, 2)]
    assert wash_in_stretches([0.5, 0.9, 1.04], WASH_IN_TERMINUS_CEILING) == [(0, 3)]


def test_a_crossing_column_exactly_at_the_ceiling_is_drawn() -> None:
    """A crossing column whose quotient equals the ceiling is drawn, at either end of a stretch.

    The ceiling is the highest quotient that a crossing column may have.
    """

    ceiling = WASH_IN_TERMINUS_CEILING

    assert wash_in_stretches([0.5, 0.9, ceiling], ceiling) == [(0, 3)]
    assert wash_in_stretches([ceiling, 0.9, 0.5], ceiling) == [(0, 3)]


def test_a_stretch_that_returns_to_wash_in_starts_on_its_crossing_column() -> None:
    """A stretch extends back to the column where its curve crossed equilibrium, as it does ahead.

    The quotients are those of a run whose dial was closed and then opened
    again. The ratio rose above equilibrium, then fell back through it. The
    column at 1.02 is the crossing before the second stretch, so that stretch
    starts there, on the line. The column at 1.3 is above the ceiling, so the
    first stretch ends where its in-domain columns end. In the second case the
    window opens on the crossing column, and the stretch extends back to it
    too.
    """

    quotients = [0.9, 1.3, 1.02, 0.5, 0.6]

    assert wash_in_stretches(quotients, WASH_IN_TERMINUS_CEILING) == [(0, 1), (2, 5)]
    assert wash_in_stretches(quotients[2:], WASH_IN_TERMINUS_CEILING) == [(0, 3)]


def test_a_run_that_crosses_equilibrium_ends_its_stretch_with_a_terminus() -> None:
    controller = SimulationController()
    controller.set_delivered_concentration_percent(Percent(2.0))
    controller.start()
    _advance(controller, 600)
    # Turning the vaporizer off lets the circuit concentration fall below the
    # alveolar concentration. The patient then returns agent to the circuit,
    # which is elimination and not wash-in.
    controller.set_delivered_concentration_percent(Percent(0.0))
    _advance(controller, 300)
    frame = assemble_chart_frame(
        [_input(controller)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    run = frame.runs[0]

    assert len(run.wash_in) == 1
    stretch = run.wash_in[0]
    assert stretch.ends_above_equilibrium
    assert 1.0 < stretch.ratios[-1] <= WASH_IN_TERMINUS_CEILING
    assert all(ratio <= 1.0 for ratio in stretch.ratios[:-1])
    assert run.undrawn_wash_in_stretches == 0


def test_a_run_that_returns_to_wash_in_draws_two_stretches_and_only_the_first_ends() -> None:
    """Each stretch holds only its own columns, and only the stretch that stopped has a terminus.

    The run washes in at a 2% dial for 10 minutes, eliminates with the dial
    closed for 5 minutes, and washes in again at 4%. The first stretch ends on
    its crossing column. The second runs to the run's live end, which is not
    an ending, so it carries no terminus marker. Both stretches are checked
    against the wash-in domain and the time the dial was opened again, not
    against values read from the frame.
    """

    controller = SimulationController()
    controller.set_delivered_concentration_percent(Percent(2.0))
    controller.start()
    _advance(controller, 600)
    controller.set_delivered_concentration_percent(Percent(0.0))
    _advance(controller, 300)
    controller.set_delivered_concentration_percent(Percent(4.0))
    _advance(controller, 300)
    frame = assemble_chart_frame(
        [_input(controller)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    first, second = frame.runs[0].wash_in

    assert first.ends_above_equilibrium
    assert not second.ends_above_equilibrium
    # The dial was opened again at 900 s, and wash-in cannot resume before it.
    assert first.times_s[-1] < 900.0 < second.times_s[0]
    # Every point except a stretch's crossing column is inside the wash-in domain.
    assert all(is_wash_in(ratio) for ratio in first.ratios[:-1])
    assert all(is_wash_in(ratio) for ratio in second.ratios[1:])


@pytest.mark.parametrize(("time_base_s", "plot_width_px"), [(14400, 1200), (43200, 900)])
def test_a_wash_in_stretch_at_a_wide_time_base_ends_at_equilibrium(
    time_base_s: int, plot_width_px: float
) -> None:
    """A stretch that crossed equilibrium ends on the line at a wide time base (`PL-CJJ1`).

    The run is an hour at the default dial and then 20 minutes with the dial
    closed. On the 4-hour and 12-hour time bases the columns are many seconds
    apart, and the first column after the dial closed has a ratio far above
    the plot. Before the crossing second was drawn, the stretch stopped at
    0.99 with no terminus.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 3600)
    controller.set_delivered_concentration_percent(Percent(0.0))
    _advance(controller, 1200)
    frame = assemble_chart_frame(
        [_input(controller)],
        time_base_for_span(time_base_s),
        COMPARTMENT_QUANTITIES,
        plot_width_px=plot_width_px,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    (stretch,) = frame.runs[0].wash_in

    assert stretch.ends_above_equilibrium
    assert 1.0 < stretch.ratios[-1] <= WASH_IN_TERMINUS_CEILING


def test_the_wash_in_hover_withholds_the_ratio_at_an_elimination_terminus() -> None:
    """`PL-YH6Z`: the crossing column is drawn, but its quotient is not printed as wash-in.

    The crossing column, where the trace passes equilibrium, is the stretch's terminus.
    It is drawn so that the line meets the reference. Its quotient is above 1, which
    `read_wash_in` classes as elimination. Printing it under the label "Wash-in F_A/F_I"
    would suggest that wash-in can go past completion.
    """

    controller = SimulationController()
    controller.set_delivered_concentration_percent(Percent(2.0))
    controller.start()
    _advance(controller, 600)
    controller.set_delivered_concentration_percent(Percent(0.0))
    _advance(controller, 300)
    frame = assemble_chart_frame(
        [_input(controller)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    run = frame.runs[0]
    stretch = run.wash_in[0]
    terminus = len(stretch.ratios) - 1

    assert stretch.ends_above_equilibrium
    assert stretch.ratios[terminus] > 1.0

    single = format_wash_in_hover(run, stretch, terminus, 1).splitlines()
    compared = format_compared_wash_in_hover([(run, stretch, terminus)]).splitlines()

    assert single[1:] == [WASH_IN_HOVER_LABEL, WASH_IN_HOVER_PAST_EQUILIBRIUM_TEXT]
    assert compared[-1].endswith(WASH_IN_HOVER_PAST_EQUILIBRIUM_TEXT)
    assert format_wash_in_ratio(stretch.ratios[terminus]) not in compared[-1]

    # The column before the terminus is still wash-in, and still prints its number.
    assert format_wash_in_hover(run, stretch, terminus - 1, 1).splitlines()[2] == (
        format_wash_in_ratio(stretch.ratios[terminus - 1])
    )


# ----------------------------------------------------------------- the hover


def _run_frame(times_s: tuple[float, ...], **fractions_by_name: tuple[float, ...]) -> RunFrame:
    # Build the fractions as `assemble_chart_frame` does. A frame holds
    # `Fraction`s, each named for its compartment, so nothing drawn from the
    # frame can reject a value.
    fractions = {
        quantity: tuple(
            Fraction(fraction, name=COMPARTMENT_FRACTION_NAMES[quantity])
            for fraction in fractions_by_name.get(quantity.value, tuple(0.0 for _ in times_s))
        )
        for quantity in COMPARTMENT_QUANTITIES
    }

    return RunFrame(
        label=run_label(FIRST_RUN),
        branch_point_s=None,
        agent_id="sevoflurane",
        agent_display_name="Sevoflurane",
        mac_percent=_SEVOFLURANE_MAC,
        elapsed_s=times_s[-1],
        times_s=times_s,
        fractions=MappingProxyType(fractions),
        wash_in=(WashInStretch(times_s, tuple(0.71 for _ in times_s), False),),
        wash_in_now=read_wash_in(0.71, 1.0),
        undrawn_wash_in_stretches=0,
        control_marks_s=(),
        undrawn_control_marks=0,
    )


def _frame(
    run: RunFrame, visible: tuple[RecordedQuantity, ...] = COMPARTMENT_QUANTITIES
) -> ChartFrame:
    return ChartFrame(
        time_base=TIME_BASE_LADDER[5],
        fitted=True,
        held_start_s=None,
        newest_instant_s=CaseInstant(3600),
        start_s=0.0,
        stop_s=3600.0,
        tick_times_s=(0.0, 600.0),
        columns=CHART_COLUMN_BUDGET_PER_SERIES,
        plot_width_px=_PLOT_WIDTH_PX,
        mac_percent=_SEVOFLURANE_MAC,
        mac_age_years=40,
        ceiling=ChartCeiling.STANDARD,
        one_mac_percent=float(_SEVOFLURANE_MAC),
        mac_awake_band_percent=mac_awake_band_percent(
            fraction_of_mac=_SEVOFLURANE.mac_awake.fraction_of_mac,
            standard_deviation_fraction_of_mac=_SEVOFLURANE.mac_awake.standard_deviation_fraction_of_mac,
            mac_percent=_SEVOFLURANE_MAC,
        ),
        mac_awake=_SEVOFLURANE.mac_awake,
        visible=visible,
        undrawn_compartments=0,
        runs=(run,),
    )


# The traces shown in the text alternative's tests: three of the six, so that
# a sentence that named every compartment, or only the first, would differ.
_THREE_SHOWN = (RecordedQuantity.ALVEOLAR, RecordedQuantity.MUSCLE, RecordedQuantity.FAT)


def test_the_chart_s_text_alternative_gives_each_shown_trace_s_latest_value() -> None:
    """A screen reader hears each shown trace's last drawn value, in both units (`PL-T9RB`).

    Each expected value is worked out by hand from the fractions below and
    sevoflurane's 1 MAC of 1.8% at age 40. 1.12% is 0.622 of 1 MAC, which
    shows as 0.62. 0.06% is 0.033 of 1 MAC, which shows as 0.03. 0.002% is
    below both readouts' resolution of 0.01, so it shows as "<0.01". The
    instant is the last drawn point's, 600 s, which the clock writes as 10m.
    The earlier points carry other values, so a sentence read from the first
    point would differ.
    """

    run = _run_frame(
        (0.0, 300.0, 600.0),
        alveolar=(0.0, 0.009, 0.0112),
        muscle=(0.0, 0.0003, 0.0006),
        fat=(0.0, 0.00001, 0.00002),
    )
    frame = _frame(run, visible=_THREE_SHOWN)

    assert concentration_chart_description(frame).splitlines()[:3] == [
        "Line chart.",
        "Modelled sevoflurane at 10m: Alveolar (end-tidal-equivalent) 1.12%, 0.62 ×MAC; "
        "Muscle 0.06%, 0.03 ×MAC; Fat <0.01%, <0.01 ×MAC.",
        "1 MAC sevoflurane (age 40) = 1.8%",
    ]
    assert (
        concentration_chart_description(frame)
        .splitlines()[3]
        .startswith("MAC-awake sevoflurane = 0.34 ×MAC")
    )
    assert concentration_chart_name(frame) == (
        "Agent concentration and relative partial pressure over time, whole run so far, "
        "1 hour shown"
    )


def test_the_chart_s_text_alternative_names_each_run_and_says_when_nothing_is_drawn() -> None:
    """With two runs each sentence names its run, and with no trace or no frame the screen's words.

    A branch stands at its own instant, so each run's sentence gives its own.
    A window in which no run has a point gives no values. It does not say that
    no compartment is checked, because the reader has checked one.
    """

    trunk = _run_frame((0.0, 300.0, 600.0), alveolar=(0.0, 0.009, 0.0112))
    branch = replace(_run_frame((0.0, 300.0), alveolar=(0.0, 0.0145)), label=run_label(SECOND_RUN))
    compared = replace(_frame(trunk, visible=(RecordedQuantity.ALVEOLAR,)), runs=(trunk, branch))

    assert latest_values_lines(compared) == (
        "Modelled sevoflurane, Run 1, at 10m: Alveolar (end-tidal-equivalent) 1.12%, 0.62 ×MAC.",
        "Modelled sevoflurane, Run 2, at 5m: Alveolar (end-tidal-equivalent) 1.45%, 0.81 ×MAC.",
    )
    assert latest_values_lines(_frame(trunk, visible=())) == ()
    assert concentration_chart_description(_frame(trunk, visible=())).splitlines()[1] == (
        "No compartment traces are shown. Check a compartment above to draw it — "
        "the readouts and the run itself are unaffected."
    )
    assert concentration_chart_description(
        _frame(replace(trunk, times_s=()), visible=(RecordedQuantity.ALVEOLAR,))
    ).splitlines()[:2] == ["Line chart.", "1 MAC sevoflurane (age 40) = 1.8%"]
    assert concentration_chart_name(None) == (
        "Agent concentration and relative partial pressure over time"
    )
    assert concentration_chart_description(None) == (
        "Nothing is plotted, because no frame could be drawn for this chart."
    )


def test_the_hover_reads_as_the_specification_shows() -> None:
    """The hover matches the worked example in `docs/INTERFACE.md` § "The chart's hover readout"."""

    run = _run_frame(
        (float(_HOVER_EXAMPLE_S),), alveolar=(_case_at_twenty_minutes().trunk_alveolar,)
    )
    examples = _hover_worked_examples()
    one_run, named_run, wash_in = examples[0], examples[1], examples[-1]
    second = replace(run, label=run_label(SECOND_RUN))

    assert format_trace_hover(run, RecordedQuantity.ALVEOLAR, 0, 1).splitlines() == one_run
    assert format_trace_hover(second, RecordedQuantity.ALVEOLAR, 0, 2).splitlines() == named_run
    assert wash_in[1] == WASH_IN_HOVER_LABEL
    assert format_wash_in_hover(run, run.wash_in[0], 0, 1).splitlines() == wash_in


def _input_refusing_a_drawn_column(
    controller: SimulationController, quantity: RecordedQuantity, value: float
) -> RunInput:
    """Return `_input(controller)` with `value` written into `quantity`'s last drawn column.

    This is the only way to get a drawn fraction outside 0 to 1, because no
    supported setting computes one (`core/concentration.py`). A drawn window
    holds states that the run stored after checking them. The value is therefore written into
    the window that the controller returns, rather than into any compartment.
    """

    real_drawn_window = controller.drawn_window

    def drawn_window(start_s: float, stop_s: float, columns: int) -> DrawnWindow:
        window = real_drawn_window(start_s, stop_s, columns)
        states = list(window.states)
        values = list(states[-1])
        values[COMPARTMENT_STATE_INDEX[quantity]] = value
        states[-1] = tuple(values)

        return DrawnWindow(
            window.substance_id, window.times_s, tuple(states), window.alveolar_ventilations_l_min
        )

    controller.drawn_window = drawn_window  # type: ignore[method-assign]

    return _input(controller)


def test_a_drawn_fraction_past_one_atmosphere_is_refused_before_any_frame_exists() -> None:
    """Every value a frame draws is built as a `Fraction` when the frame is assembled.

    This is the fourth limit in `core/concentration.py`. A computed fraction
    that rounds past 1 is rejected, rather than clamped to 100.00% or drawn
    above the axis (`PL-4R3W`). No supported opening or dial can produce such a
    fraction (`PL-9B1M`). `assemble_chart_frame` rejects it
    before a `ChartFrame` exists. The toolkit is therefore never given a
    frame whose first traces convert and whose last trace fails. Such a frame
    once left four traces redrawn and two still showing the previous frame
    (`PL-7DJK`). The value used here is the one that reproduced that defect,
    in the muscle column.
    """

    run = _input_refusing_a_drawn_column(_run(60), RecordedQuantity.MUSCLE, 1.0000000000001568)

    with pytest.raises(
        SimulationConfigurationError,
        match=r"^muscle partial_pressure_fraction of 1\.0000000000001568 is outside 0 to 1",
    ):
        assemble_chart_frame(
            [run],
            None,
            COMPARTMENT_QUANTITIES,
            plot_width_px=_PLOT_WIDTH_PX,
            held_start_s=None,
            ceiling=ChartCeiling.STANDARD,
        )


def test_a_refused_drawn_value_names_its_compartment_as_a_step_would() -> None:
    """Each of the six fractions is named for its quantity, as `_write_state_vector` names it.

    The message "fraction of 1.0000000000000002" said which value was
    rejected but not which compartment. That broke the convention that
    `Fraction`'s docstring states (`PL-SPN6`).
    `run_series.COMPARTMENT_FRACTION_NAMES` is the one table from which the
    frame, the snapshot and the MAC multiples take their names (`PL-7DJK`).
    """

    for quantity in COMPARTMENT_QUANTITIES:
        run = _input_refusing_a_drawn_column(_run(60), quantity, nextafter(1.0, inf))

        with pytest.raises(
            SimulationConfigurationError,
            match=rf"^{COMPARTMENT_FRACTION_NAMES[quantity]} of 1\.0000000000000002 is outside",
        ):
            assemble_chart_frame(
                [run],
                None,
                COMPARTMENT_QUANTITIES,
                plot_width_px=_PLOT_WIDTH_PX,
                held_start_s=None,
                ceiling=ChartCeiling.STANDARD,
            )


@pytest.mark.parametrize("value", [float("nan"), inf, -inf], ids=["nan", "inf", "-inf"])
def test_a_non_finite_drawn_value_is_refused_naming_its_compartment(value: float) -> None:
    """No frame can hold a NaN or an infinity, so the chart may skip pyqtgraph's own scan.

    `app/qt_chart.py` draws every curve with `skipFiniteCheck`, and
    pyqtgraph leaves the result undefined for non-finite data (`PL-TCNT`).
    That is safe only if such a value is rejected before the frame is built.
    The error must name the compartment, as it does for a value above one
    atmosphere.
    """

    for quantity in COMPARTMENT_QUANTITIES:
        run = _input_refusing_a_drawn_column(_run(60), quantity, value)

        with pytest.raises(
            SimulationConfigurationError,
            match=rf"^{COMPARTMENT_FRACTION_NAMES[quantity]} of {value} is outside 0 to 1",
        ):
            assemble_chart_frame(
                [run],
                None,
                COMPARTMENT_QUANTITIES,
                plot_width_px=_PLOT_WIDTH_PX,
                held_start_s=None,
                ceiling=ChartCeiling.STANDARD,
            )


@pytest.mark.parametrize("ratio", [float("nan"), inf, -inf], ids=["nan", "inf", "-inf"])
def test_a_wash_in_stretch_refuses_a_non_finite_ratio(ratio: float) -> None:
    """A stretch holds only finite ratios, by construction (`PL-TCNT`).

    No supported run forms such a ratio, because both of its fractions are
    checked first. The stretch checks anyway. The chart skips pyqtgraph's
    finiteness check because of this guarantee, so the guarantee must not
    depend on the order of the steps in `_run_frame`.
    """

    with pytest.raises(
        SimulationConfigurationError,
        match=rf"^the wash-in ratio F_A/F_I at 8\.0 s is {ratio}, which is not finite$",
    ):
        WashInStretch((4.0, 8.0), (0.5, ratio), False)


def test_a_wash_in_stretch_refuses_instants_and_ratios_of_different_lengths() -> None:
    """A stretch holds one ratio for each drawn instant, so tuples of different lengths are refused.

    Every reader takes an instant and its ratio at the same index. A stretch
    whose tuples differ in length cannot be read that way, so it is refused
    when it is built rather than when it is drawn. The refusal is the
    `ValueError` that `zip(..., strict=True)` raises.
    """

    with pytest.raises(ValueError):
        WashInStretch((4.0, 8.0, 12.0), (0.5, 0.6), False)

    with pytest.raises(ValueError):
        WashInStretch((4.0, 8.0), (0.5, 0.6, 0.7), False)


@pytest.mark.parametrize(
    ("stretch", "dotted"),
    [
        (WashInStretch((), (), False), False),
        (WashInStretch((901.0,), (0.38,), False), True),
        (WashInStretch((901.0, 904.0), (0.38, 0.44), False), False),
        (WashInStretch((901.0, 904.0, 960.0), (0.38, 0.44, 1.02), True), True),
    ],
)
def test_a_stretch_has_an_end_dot_where_it_stopped_or_has_one_point(
    stretch: WashInStretch, dotted: bool
) -> None:
    """A stretch of one point is drawn as a dot, because a line needs two points.

    One second after ventilation is restored, the stretch that starts again
    has one point, and the caption beside the plot reads its ratio. Without
    the dot, the plot drew nothing there (`PL-49D5`, domain review). A
    stretch of two or more points that is still growing has no dot, and one
    that stopped past equilibrium has one.
    """

    assert stretch.has_end_dot is dotted


def test_a_frame_holds_built_fractions_so_nothing_drawn_from_it_builds_one() -> None:
    """The conversion, the hover and the cursor readouts use the `Fraction`s that the frame built.

    This checks, by type, what `RunFrame.fractions` promises. Every drawn
    value is a `Fraction`, and the axis top is a `Percent`. `percents`,
    `format_trace_hover` and `nearest_trace_point` therefore build nothing.
    None of them can be the first to reject a value after a frame has started
    to draw (`PL-7DJK`).
    """

    frame = assemble_chart_frame(
        [_input(_run(60))],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert isinstance(frame.axis_top_percent, Percent)

    for run in frame.runs:
        for quantity in COMPARTMENT_QUANTITIES:
            assert run.fractions[quantity]
            assert all(isinstance(fraction, Fraction) for fraction in run.fractions[quantity])
            assert all(isinstance(percent, Percent) for percent in run.percents(quantity))


def test_an_axis_top_past_one_atmosphere_is_refused_when_the_frame_is_assembled() -> None:
    """Three MACs of an agent whose MAC exceeds a third of an atmosphere is not a valid percent.

    No shipped agent has such a MAC (`Percent`'s docstring in
    `core/concentration.py`), so the test writes the MAC onto the snapshot.
    The axis top is built and named at assembly. The rejection therefore
    comes before the chart draws, rather than from the off-scale notice
    afterwards (`PL-7DJK`).
    """

    controller = _run(60)
    run = replace(
        _input(controller),
        snapshot=replace(controller.snapshot(), agent_mac_percent=MacPercent(40.0)),
    )

    with pytest.raises(
        SimulationConfigurationError, match=r"^axis_top_percent of 120\.0 is outside 0 to 100"
    ):
        assemble_chart_frame(
            [run],
            None,
            COMPARTMENT_QUANTITIES,
            plot_width_px=_PLOT_WIDTH_PX,
            held_start_s=None,
            ceiling=ChartCeiling.STANDARD,
        )


def test_the_hover_names_the_run_only_while_more_than_one_is_drawn() -> None:
    """The hover names the run on line 1, and only while more than one run is drawn.

    This follows `docs/INTERFACE.md` § "The hover and the run it belongs to". The
    run's name goes in the line that the specification already calls run
    context. It appears only while there is a second run to tell it apart
    from. That is the same condition that `run_trace_style` uses for its
    width channel.
    """

    first = _run_frame((1208.0,), alveolar=(0.0143,))
    second = replace(first, label=run_label(SECOND_RUN))

    assert format_trace_hover(first, RecordedQuantity.ALVEOLAR, 0, 1).splitlines()[0] == (
        "Modelled sevoflurane \u00b7 20m8s"
    )
    assert format_trace_hover(first, RecordedQuantity.ALVEOLAR, 0, 2).splitlines()[0] == (
        "Modelled sevoflurane \u00b7 Run 1 \u00b7 20m8s"
    )
    assert format_trace_hover(second, RecordedQuantity.ALVEOLAR, 0, 2).splitlines()[0] == (
        "Modelled sevoflurane \u00b7 Run 2 \u00b7 20m8s"
    )

    # The wash-in hover shares the context line, so it names the run too.
    assert format_wash_in_hover(second, second.wash_in[0], 0, 2).splitlines()[0] == (
        "Modelled sevoflurane \u00b7 Run 2 \u00b7 20m8s"
    )

    # Naming the run changes nothing else about the readout.
    assert (
        format_trace_hover(second, RecordedQuantity.ALVEOLAR, 0, 2).splitlines()[1:]
        == (format_trace_hover(first, RecordedQuantity.ALVEOLAR, 0, 1).splitlines()[1:])
    )


def test_a_hover_cannot_be_answered_for_a_chart_drawing_no_runs() -> None:
    """This prevents a readout that claims to compare runs while naming none."""

    run = _run_frame((1208.0,), alveolar=(0.0143,))

    for count in (0, -1):
        with pytest.raises(ValueError, match="at least one run"):
            format_trace_hover(run, RecordedQuantity.ALVEOLAR, 0, count)

        with pytest.raises(ValueError, match="at least one run"):
            format_wash_in_hover(run, run.wash_in[0], 0, count)


def test_two_runs_within_the_hover_radius_answer_under_their_own_names() -> None:
    """Test the regression that `PL-MN4J` was filed for, end to end from the pointer.

    Where two runs' points for one compartment are both inside the radius,
    the hover reports every one of them (`PL-JVHL`). It attributes each value
    to the run it belongs to (`PL-MN4J`). On a measured branched sevoflurane
    case, the two runs' fat points lie inside the 12 px radius over 100% of
    the shared axis, and 43.8-81.4% of those hovers print different values.
    An unattributed value can therefore be a correct number credited to the
    wrong run, and so to the wrong management.
    """

    case = _case_at_twenty_minutes()
    at_s = float(_HOVER_EXAMPLE_S)
    first = _run_frame((at_s,), alveolar=(case.trunk_alveolar,))
    second = replace(
        _run_frame((at_s,), alveolar=(case.raised_alveolar,)), label=run_label(SECOND_RUN)
    )
    frame = replace(_frame(first), runs=(first, second))
    first_percent = case.trunk_alveolar * 100.0
    second_percent = case.raised_alveolar * 100.0

    # Both runs' alveolar points are well inside the radius of this pointer.
    nearer_second = nearest_trace_point(frame, at_s, second_percent, 4.0, _PERCENT_PER_PIXEL, 12.0)
    nearer_first = nearest_trace_point(frame, at_s, first_percent, 4.0, _PERCENT_PER_PIXEL, 12.0)

    assert nearer_second is not None
    assert nearer_first is not None
    assert abs(second_percent - first_percent) / _PERCENT_PER_PIXEL < 12.0, (
        "the two points must contend for this to test anything"
    )

    # It does not matter which point is marginally nearer. Both pointer
    # positions give one box showing both runs, each named, in drawing order.
    assert nearer_second.readout == nearer_first.readout
    assert tuple(reading.run for reading in nearer_second.readings) == (0, 1)
    # The document's third example is this box.
    assert nearer_second.readout.splitlines() == _hover_worked_examples()[2]

    # The values differ, which is why the attribution matters.
    assert nearer_second.readout.splitlines()[2] != nearer_second.readout.splitlines()[3]


def test_a_small_pointer_movement_never_swaps_which_run_the_hover_answers() -> None:
    """`PL-JVHL`: every run inside the radius is reported, so nothing depends on the nearer point.

    The geometry is the one the item measured, reduced to the two fat traces
    that matter. The case is the reference adult on sevoflurane. The trunk is
    held at 1 MAC, and the branch forks at 10 min with the vaporizer turned
    off. The axis spans 60 minutes and is 900 px wide and
    `theme.CHART_HEIGHT` tall, which gives 4.00 s/px and 0.015 %/px. At
    3492 s, the run still carrying agent holds 0.028% and shows 0.03%, and the
    run 48 minutes into emergence holds 0.0053% and shows 0.01%. The percent
    axis is fixed at 3 MAC (`CHART_AXIS_TOP_MAC`), so these two points are
    1.5 px apart. Both points
    are inside the 12 px radius across the whole hoverable band. The old rule
    kept only the single nearest point overall, and it switched which run was
    reported on 75.4-99.9% of the fat axis.
    """

    reach = dict(seconds_per_pixel=4.0, percent_per_pixel=_PERCENT_PER_PIXEL, radius_pixels=12.0)
    times_s = tuple(3400.0 + 4.0 * column for column in range(50))
    still_carrying = _run_frame(times_s, fat=tuple(0.00028 for _ in times_s))
    emerging = replace(
        _run_frame(times_s, fat=tuple(0.000053 for _ in times_s)), label=run_label(SECOND_RUN)
    )
    frame = replace(
        _frame(still_carrying, visible=(RecordedQuantity.FAT,)), runs=(still_carrying, emerging)
    )
    on_trunk = still_carrying.percents(RecordedQuantity.FAT)[0]
    on_branch = emerging.percents(RecordedQuantity.FAT)[0]
    midpoint = (on_trunk + on_branch) / 2.0
    # The two traces are less than 2 px apart. The item measured the real
    # case at 0.2-1.4 px, which is why a reader cannot see which trace is which.
    assert abs(on_trunk - on_branch) / _PERCENT_PER_PIXEL < 2.0
    # Pixel offsets from the midpoint of the two traces at 3492 s, in steps of
    # two pixels, which is the hand movement the item measured.
    offsets = tuple(range(-12, 13, 2))

    def hover(x_px: int, y_px: int) -> tuple[int, ...]:
        target = nearest_trace_point(
            frame, 3492.0 + x_px * 4.0, midpoint + y_px * _PERCENT_PER_PIXEL, **reach
        )

        return () if target is None else tuple(reading.run for reading in target.readings)

    def contending(x_px: int, y_px: int) -> bool:
        """Return whether both runs' fat points are inside the radius of this pointer."""

        return all(
            nearest_trace_point(
                replace(frame, runs=(run,)),
                3492.0 + x_px * 4.0,
                midpoint + y_px * _PERCENT_PER_PIXEL,
                **reach,
            )
            is not None
            for run in (still_carrying, emerging)
        )

    def marginally_nearer(y_px: int) -> int:
        """Return the run that the retired rule would have reported: the nearer point's run."""

        percent = midpoint + y_px * _PERCENT_PER_PIXEL

        return 0 if abs(percent - on_trunk) < abs(percent - on_branch) else 1

    contended = [(x, y) for x in offsets for y in offsets if contending(x, y)]
    assert len(contended) > len(offsets) ** 2 // 2, "the geometry must contend to test anything"
    # The geometry is ambiguous: the retired rule does switch runs across it.
    assert {marginally_nearer(y) for _, y in contended} == {0, 1}

    for x_px, y_px in contended:
        assert hover(x_px, y_px) == (0, 1)

        for neighbour in ((x_px + 2, y_px), (x_px, y_px + 2)):
            if contending(*neighbour):
                assert hover(*neighbour) == hover(x_px, y_px)

    # Both values are reported, and they differ. That difference is what made
    # the switch between runs matter, rather than being cosmetic.
    readout = nearest_trace_point(frame, 3492.0, midpoint, **reach)
    assert readout is not None
    assert readout.readout.splitlines()[2:] == [
        "Run 1 · 58m12s   0.03%   0.02 ×MAC",
        "Run 2 · 58m12s   0.01%   <0.01 ×MAC",
    ]


def _contended_muscle_and_fat() -> tuple[ChartFrame, dict[str, float]]:
    """Return the geometry that `PL-0RZ0` measured, reduced to the pair of traces that matter.

    The case is the reference adult on sevoflurane, on a 60-minute axis
    900 px wide and `theme.CHART_HEIGHT` tall. That gives 4.00 s/px and
    0.015 %/px. The values come from the runs in `_case_at_twenty_minutes`:
    the trunk held at 1 MAC, and a branch of it with the vaporizer turned off
    at 10 min. At 20 minutes the trunk's muscle shows 0.14% and its fat 0.01%.
    The percent axis is fixed at 3 MAC (`CHART_AXIS_TOP_MAC`), so these points
    are about 9 px apart, inside the 12 px radius. Muscle and fat are the pair
    that a reader comparing two runs picks most often. They are also the pair
    whose values differ most: by a median of 17.1-17.9x across the measured
    cases, and by twofold or more at every switch.
    """

    case = _case_at_twenty_minutes()
    times_s = tuple(float(second) for second in _CONTENDED_TIMES_S)
    still_carrying = _run_frame(times_s, muscle=case.trunk_muscle, fat=case.trunk_fat)
    emerging = replace(
        _run_frame(times_s, muscle=case.emerging_muscle, fat=case.emerging_fat),
        label=run_label(SECOND_RUN),
    )
    frame = replace(
        _frame(still_carrying, visible=(RecordedQuantity.MUSCLE, RecordedQuantity.FAT)),
        runs=(still_carrying, emerging),
    )

    return frame, dict(
        seconds_per_pixel=4.0, percent_per_pixel=_PERCENT_PER_PIXEL, radius_pixels=12.0
    )


def test_two_compartments_within_one_hover_radius_answer_under_their_own_names() -> None:
    """`PL-0RZ0`: every compartment inside the radius is reported, not just the nearer trace.

    This is the rule that `PL-JVHL` settled for runs, applied to compartments.
    `PL-JVHL` left distance to pick the compartment, reasoning that a reader
    aims at a curve. `PL-0RZ0` then measured the two-run chart. Two or more
    compartments were inside the radius over 15.2-45.7% of its hoverable
    area. A 2 px move changed which compartment was reported on 6.6-13.6% of
    contended pointer pairs. The two winning points were a median 0.9 px
    apart. There was therefore no aim to respect, and the box did not move
    when the reported compartment changed.
    """

    frame, reach = _contended_muscle_and_fat()
    still_carrying, emerging = frame.runs
    on_muscle = still_carrying.percents(RecordedQuantity.MUSCLE)[0]
    on_fat = still_carrying.percents(RecordedQuantity.FAT)[0]
    # This is the contention under test. The two traces are within one radius
    # of each other, so no pointer position lies on one and not the other.
    assert 0.0 < (on_muscle - on_fat) / _PERCENT_PER_PIXEL < 12.0
    offsets = tuple(range(-12, 13, 2))
    midpoint = (on_muscle + on_fat) / 2.0

    def hover(x_px: int, y_px: int) -> tuple[tuple[RecordedQuantity, int], ...]:
        target = nearest_trace_point(
            frame, 1200.0 + x_px * 4.0, midpoint + y_px * _PERCENT_PER_PIXEL, **reach
        )

        return (
            ()
            if target is None
            else tuple((reading.quantity, reading.run) for reading in target.readings)
        )

    def contending(x_px: int, y_px: int) -> bool:
        """Return whether each of the four traces has a drawn point inside this pointer's radius.

        Each trace is checked on a frame that draws only that trace. The rule
        under test therefore cannot decide the question that is put to it.
        """

        return all(
            nearest_trace_point(
                replace(frame, visible=(quantity,), runs=(run,)),
                1200.0 + x_px * 4.0,
                midpoint + y_px * _PERCENT_PER_PIXEL,
                **reach,
            )
            is not None
            for quantity in (RecordedQuantity.MUSCLE, RecordedQuantity.FAT)
            for run in frame.runs
        )

    def marginally_nearer(y_px: int) -> RecordedQuantity:
        """Return the compartment that the retired rule would have reported, the nearer trace's."""

        percent = midpoint + y_px * _PERCENT_PER_PIXEL

        return (
            RecordedQuantity.MUSCLE
            if abs(percent - on_muscle) < abs(percent - on_fat)
            else RecordedQuantity.FAT
        )

    contended = [(x, y) for x in offsets for y in offsets if contending(x, y)]
    assert len(contended) > len(offsets) ** 2 // 4, "the geometry must contend to test anything"
    # The geometry is ambiguous: the retired rule does switch compartments across it.
    assert {marginally_nearer(y) for _, y in contended} == {
        RecordedQuantity.MUSCLE,
        RecordedQuantity.FAT,
    }

    for x_px, y_px in contended:
        # Both compartments, both runs, in the frame's own drawing order.
        assert hover(x_px, y_px) == (
            (RecordedQuantity.MUSCLE, 0),
            (RecordedQuantity.MUSCLE, 1),
            (RecordedQuantity.FAT, 0),
            (RecordedQuantity.FAT, 1),
        )

        for neighbour in ((x_px + 2, y_px), (x_px, y_px + 2)):
            if contending(*neighbour):
                assert hover(*neighbour) == hover(x_px, y_px)

    # Every value is reported, each under its own compartment and run. The two
    # compartments differ severalfold, as the item measured.
    target = nearest_trace_point(frame, 1200.0, midpoint, **reach)
    assert target is not None
    assert target.quantities == (RecordedQuantity.MUSCLE, RecordedQuantity.FAT)
    # The document's fourth example is this box.
    assert target.readout.splitlines() == _hover_worked_examples()[3]
    assert (
        emerging.percents(RecordedQuantity.MUSCLE)[0]
        > still_carrying.percents(RecordedQuantity.FAT)[0] * 5.0
    ), "the contending values must differ severalfold for this to matter"


@pytest.mark.parametrize("agent_id", ["sevoflurane", "isoflurane", "desflurane"])
def test_at_opening_settings_fat_first_hour_spans_under_4_px_at_1_mac_and_12_px_at_vaporizer_max(
    agent_id: str,
) -> None:
    """Hold the fat-trace figure in the hazard row on traces drawn on top of each other.

    `docs/VERIFICATION.md` names this test beside the row "reading one
    compartment's concentration as another's where two traces are drawn on
    top of each other". The row says the fat trace moves less than 4 px over
    its first hour at a 1 MAC dial and less than 12 px at the agent's
    vaporizer maximum, with the chart at its preferred height. Fat starts
    empty and only rises at a fixed dial, so its value at 60 min is the whole
    first hour's span.

    Each run is built directly: the reference adult at its opening
    ventilation, cardiac output and fresh gas flow, the dial held from t = 0,
    and one-second steps. The row states those settings, because raising any
    of them spreads the trace further: a blind review on 2026-11-22 measured
    up to 21.9 px at the vaporizer maximum with all three at their highest.

    The height used is `theme.CHART_HEIGHT`, the whole chart. The percent
    axis is a part of that height, so the pixel figure here is an upper bound
    on the one a reader sees. The 12 px is the
    hover radius (`HOVER_RADIUS_PIXELS` in `app/qt_chart.py`). Below it, every
    compartment in reach answers under its own name, which is what the row
    relies on. Measured on 2026-11-22: 1.5-3.7 px at a 1 MAC dial and
    6.3-10.0 px at the vaporizer maximum (`PL-8YBS`).
    """

    agent = load_agent_parameters(agent_id)
    mac = mac_for_patient(agent, load_reference_adult_parameters()).percent
    pixels_per_percent = CHART_HEIGHT / chart_axis_top_percent(mac, ChartCeiling.STANDARD)

    def fat_pixels_at_one_hour(dial_percent: float) -> float:
        system = AgentUptakeSystem.for_agent(agent_id)
        system.set_delivered_concentration_percent(Percent(dial_percent))
        for _ in range(3600):
            system.advance()
        (fat,) = (tissue for tissue in system.patient.tissues if tissue.name == "fat")

        return 100.0 * fat.partial_pressure_fraction * pixels_per_percent

    at_one_mac = fat_pixels_at_one_hour(mac)
    at_the_maximum = fat_pixels_at_one_hour(agent.max_delivered_concentration_percent)

    assert 0.0 < at_one_mac < 4.0
    assert at_one_mac < at_the_maximum < 12.0


def test_a_contended_hover_names_no_run_while_only_one_is_drawn() -> None:
    """`_hover_context`'s rule applies to the compartment lines: one drawn run is not a comparison.

    The single-run chart draws all six compartments and has the same
    exposure. `PL-0RZ0` measured two or more compartments inside the radius
    over 37.0% of its hoverable area. This form therefore appears there too.
    Naming the only run there would imply a comparison that is not on screen.
    """

    frame, reach = _contended_muscle_and_fat()
    alone = replace(frame, runs=frame.runs[:1])
    on_muscle = alone.runs[0].percents(RecordedQuantity.MUSCLE)[0]
    on_fat = alone.runs[0].percents(RecordedQuantity.FAT)[0]

    target = nearest_trace_point(alone, 1200.0, (on_muscle + on_fat) / 2.0, **reach)

    assert target is not None
    assert target.readout.splitlines() == [
        "Modelled sevoflurane",
        "Muscle · 20m   0.14%   0.08 ×MAC",
        "Fat · 20m   0.01%   <0.01 ×MAC",
    ]


def _retired_nearest_instant(
    run: RunFrame,
    quantity: RecordedQuantity,
    time_s: float,
    percent: float,
    reach: dict[str, float],
) -> float | None:
    """Return the instant the retired rule reported for one trace: its point nearest in pixels.

    This is the counterfactual against which the `PL-1K9G` tests are checked.
    A geometry that stops exercising the retired rule's failure then fails as
    a geometry, rather than passing as a fix.
    """

    distance, instant = min(
        (
            hypot(
                (drawn_s - time_s) / reach["seconds_per_pixel"],
                (drawn - percent) / reach["percent_per_pixel"],
            ),
            drawn_s,
        )
        for drawn_s, drawn in zip(run.times_s, run.percents(quantity), strict=True)
    )

    return instant if distance <= reach["radius_pixels"] else None


def _named_instant(run: RunFrame, time_s: float) -> float:
    """Return the drawn instant nearest `time_s`, which is the instant the pointer names.

    A tie goes to the earlier instant.
    """

    return min(run.times_s, key=lambda drawn_s: (abs(drawn_s - time_s), drawn_s))


def test_every_compartment_of_one_run_answers_at_one_instant() -> None:
    """`PL-1K9G`: the pointer names the instant, and every trace of a run is reported at it.

    The retired rule kept, for each trace, the drawn point nearest the
    pointer in pixels. A steep trace and a flat one inside one radius were
    therefore reported at different columns, and the pointer's height decided
    which. One box then labelled two compartments of one run with two
    different instants. On the single-run chart, 70.1% of the boxes holding
    two or more of one run's readings mixed instants. The instants were up to
    72 s apart on the 60-minute axis and up to 15 minutes apart on the 12-hour
    axis. 91.9% of those boxes printed digits that the same compartments do
    not show at one shared instant.

    The geometry here is that shape reduced to two traces. Vessel-rich is
    flat, and mixed venous rises through it by two pixels a column, at the
    60-minute axis's 4.00 s/px and 0.015 %/px. The pointer is a quarter of a
    column past 20m, which is the instant it names. It is three pixels above
    the flat trace, where the steep trace's nearest point is three columns
    later.
    """

    reach = dict(seconds_per_pixel=4.0, percent_per_pixel=_PERCENT_PER_PIXEL, radius_pixels=12.0)
    times_s = tuple(1160.0 + 4.0 * column for column in range(20))
    run = _run_frame(
        times_s,
        vessel_rich=tuple(0.0060 for _ in times_s),
        mixed_venous=tuple(0.0060 + (column - 12) * 0.000334 for column in range(20)),
    )
    frame = _frame(run, visible=(RecordedQuantity.MIXED_VENOUS, RecordedQuantity.VESSEL_RICH))
    time_s = 1201.0
    above_flat = run.percents(RecordedQuantity.VESSEL_RICH)[0] + 3 * _PERCENT_PER_PIXEL

    # The retired rule split this geometry. Under this pointer, it reported
    # the two traces twelve seconds apart.
    assert {
        _retired_nearest_instant(run, quantity, time_s, above_flat, reach)
        for quantity in frame.visible
    } == {1200.0, 1212.0}

    target = nearest_trace_point(frame, time_s, above_flat, **reach)

    assert target is not None
    assert tuple((reading.quantity, reading.time_s) for reading in target.readings) == (
        (RecordedQuantity.MIXED_VENOUS, 1200.0),
        (RecordedQuantity.VESSEL_RICH, 1200.0),
    )
    assert target.readout.splitlines() == [
        "Modelled sevoflurane",
        "Mixed venous · 20m   0.53%   0.30 ×MAC",
        "Vessel-rich · 20m   0.60%   0.33 ×MAC",
    ]

    # No pointer height at which the hover reports anything moves the instant.
    for y_px in range(-12, 13):
        moved = nearest_trace_point(frame, time_s, above_flat + y_px * _PERCENT_PER_PIXEL, **reach)

        if moved is not None:
            assert {reading.time_s for reading in moved.readings} == {1200.0}


@pytest.mark.parametrize("compared", [False, True], ids=["one run", "two runs"])
def test_a_vertical_hand_movement_never_moves_the_instant_a_hover_reports(compared: bool) -> None:
    """`PL-1K9G` on real runs: the instant that labels a value depends only on the pointer's time.

    Under the retired rule, a purely vertical 2 px movement changed the
    instant on 44.9% of such movements on the single-run chart. It changed the
    printed value on 35.1%, by up to 0.13 percentage points on the 60-minute
    axis and 0.39 on the 12-hour axis, while nothing else in the box moved.
    This test sweeps across the dial change at ten minutes and the live end at
    twenty minutes, where the fast compartments are steepest. It checks every
    other pixel of height, and three points between each pair of columns, one
    of them the exact midpoint. Every run that is reported is reported at its
    own drawn instant nearest the pointer in time, whatever the pointer's
    height.
    """

    trunk = _run(600)
    trunk.begin_control_adjustment()
    trunk.set_delivered_concentration_percent(Percent(3.0))
    _advance(trunk, 600)
    controllers = [trunk]

    if compared:
        branch = BranchedCase(trunk).fork_at(CaseInstant(600))
        branch.start()
        branch.begin_control_adjustment()
        branch.set_delivered_concentration_percent(Percent(0.0))
        _advance(branch, 600)
        controllers.append(branch)

    frame = assemble_chart_frame(
        [_input(controller, run_index=index) for index, controller in enumerate(controllers)],
        time_base_for_span(3600.0),
        (RecordedQuantity.ALVEOLAR, RecordedQuantity.FAT) if compared else COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    reach = dict(
        seconds_per_pixel=(frame.stop_s - frame.start_s) / _PLOT_WIDTH_PX,
        percent_per_pixel=frame.axis_top_percent / 360.0,
        radius_pixels=12.0,
    )
    assert reach["seconds_per_pixel"] == 4.0, "the sweep is the 60-minute axis the item measured"
    pointer_times_s = [
        drawn_s + offset_s
        for drawn_s in frame.runs[0].times_s
        if 560.0 <= drawn_s < 640.0 or 1160.0 <= drawn_s < 1200.0
        for offset_s in (1.0, 2.0, 3.0)
    ]
    heights = [y_px * reach["percent_per_pixel"] for y_px in range(0, 361, 2)]

    # In this region, the retired rule labelled values with an instant that
    # the pointer's time does not name.
    assert any(
        _retired_nearest_instant(run, quantity, time_s, percent, reach)
        not in (None, _named_instant(run, time_s))
        for time_s in pointer_times_s
        for percent in heights
        for run in frame.runs
        for quantity in frame.visible
    ), "the swept region must be one the retired rule mislabelled to test anything"

    answered = 0

    for time_s in pointer_times_s:
        named = [_named_instant(run, time_s) for run in frame.runs]

        for percent in heights:
            target = nearest_trace_point(frame, time_s, percent, **reach)

            if target is None:
                continue

            answered += 1

            for reading in target.readings:
                assert reading.time_s == named[reading.run]

    assert answered > len(pointer_times_s), "the sweep must be answered to test anything"


def test_a_trace_answers_only_where_its_point_at_the_named_instant_is_in_reach() -> None:
    """The radius still decides whether a trace is reported, measured at the named instant.

    A steep trace passes within the radius of a pointer beside it, at an
    instant several columns away. The retired rule reported that point. The
    other way to make the instant depend only on the pointer's time was to
    report the named instant's point whatever its distance. That option was
    measured and rejected. Where this rule reports nothing, that option would
    have placed the dot and the box a median 13.5 px and up to 42.5 px from
    the pointer on the 60-minute axis, and up to 146 px away on the 12-hour
    axis. It would have reported a value that the reader is nowhere near as
    the one under the pointer.
    """

    reach = dict(seconds_per_pixel=4.0, percent_per_pixel=_PERCENT_PER_PIXEL, radius_pixels=12.0)
    times_s = tuple(1160.0 + 4.0 * column for column in range(18))
    # The trace rises twenty pixels a column, like the near-vertical step that
    # a dial change draws.
    run = _run_frame(times_s, circuit=tuple(0.0005 + column * 0.00334 for column in range(18)))
    frame = _frame(run, visible=(RecordedQuantity.CIRCUIT,))
    circuit = run.percents(RecordedQuantity.CIRCUIT)
    time_s = 1201.0

    # The pointer is level with the trace three columns later. It is 2.75 px
    # from that point, which the retired rule reported, and 60 px above the
    # point at 20m.
    assert _retired_nearest_instant(run, RecordedQuantity.CIRCUIT, time_s, circuit[13], reach) == (
        1212.0
    )
    assert nearest_trace_point(frame, time_s, circuit[13], **reach) is None

    # With the pointer on the trace at the named instant, the hover reports
    # that point.
    on_trace = nearest_trace_point(frame, time_s, circuit[10], **reach)

    assert on_trace is not None
    assert (on_trace.anchor.time_s, on_trace.anchor.value) == (1200.0, circuit[10])


def test_the_wash_in_hover_answers_at_the_instant_the_pointer_names() -> None:
    """`PL-1K9G` on the wash-in plot, which also measured distance in both dimensions.

    The wash-in plot has one trace per run, so no box there could mix one
    run's instants. But a purely vertical 2 px movement changed its one
    reported instant on 23.9-44.4% of such movements across the measured
    cases. It changed the printed ratio on 7.7-20.6%. A run's stretches form
    one set of drawn instants, so the pointer names one of them even in the
    gap between two stretches.
    """

    reach = dict(seconds_per_pixel=4.0, ratio_per_pixel=0.00575, radius_pixels=12.0)
    # This stretch rises two pixels a column, as early wash-in does on the
    # 60-minute axis.
    early = WashInStretch(
        tuple(40.0 + 4.0 * column for column in range(10)),
        tuple(0.30 + 0.0115 * column for column in range(10)),
        False,
    )
    late = WashInStretch((100.0, 104.0, 108.0), (0.80, 0.80, 0.80), False)
    run = replace(_run_frame((40.0, 108.0)), wash_in=(early, late))
    frame = _frame(run)
    reported = []

    for y_px in range(-12, 13):
        target = nearest_wash_in_point(frame, 57.0, early.ratios[4] + y_px * 0.00575, **reach)

        if target is not None:
            reported.append(target.anchor.time_s)

    assert reported and set(reported) == {56.0}

    # In the gap, nearer in time to the late stretch, the hover reports the
    # late stretch's first point.
    in_gap = nearest_wash_in_point(frame, 92.0, 0.80, **reach)

    assert in_gap is not None
    assert (in_gap.anchor.time_s, in_gap.anchor.value) == (100.0, 0.80)


def test_a_run_that_draws_no_instant_answers_no_hover_and_silences_no_other() -> None:
    """A run with nothing drawn has no instant to name, so only the other runs are reported.

    `SimulationController.drawn_window` always draws both ends of the range a
    run covers, so no assembled frame contains such a run. The case is tested
    here anyway. Without a guard, the bisection that names the instant would
    read one position before the first column of an empty run, on both plots.
    """

    drawn = _run_frame((1208.0,), alveolar=(0.0143,))
    empty = replace(
        drawn, label=run_label(SECOND_RUN), times_s=(), wash_in=(WashInStretch((), (), False),)
    )
    frame = replace(_frame(drawn), runs=(empty, drawn))

    target = nearest_trace_point(frame, 1208.0, 1.43, 4.0, _PERCENT_PER_PIXEL, 12.0)
    wash_in = nearest_wash_in_point(frame, 1208.0, 0.71, 4.0, 0.00575, 12.0)

    assert target is not None and tuple(reading.run for reading in target.readings) == (1,)
    assert wash_in is not None and tuple(reading.run for reading in wash_in.readings) == (1,)


def test_the_hover_keeps_the_below_resolution_forms_and_the_readout_row_s_glosses() -> None:
    """As in `docs/INTERFACE.md`'s measured table, fat shows as `<0.01%`, never `3.52e-05`."""

    run = _run_frame((48.0,), fat=(3.52e-7,), circuit=(0.0262,), mixed_venous=(0.005,))

    assert format_trace_hover(run, RecordedQuantity.FAT, 0, 1).splitlines()[1:] == [
        "Fat",
        "<0.01%   <0.01 ×MAC",
    ]
    assert format_trace_hover(run, RecordedQuantity.CIRCUIT, 0, 1).splitlines()[1] == (
        "Circuit (inspired)"
    )
    assert format_trace_hover(run, RecordedQuantity.MIXED_VENOUS, 0, 1).splitlines()[1] == (
        "Mixed venous"
    )


def test_every_hover_number_is_the_formatter_s_at_the_snapshot_s_own_divisor() -> None:
    """The hover divides by the run's own 1 MAC, not by the agent's stored MAC at age 40.

    The run's 1.5% stands for a MAC adjusted for an older patient, so it
    differs from sevoflurane's stored 1.8%. A hover that read the stored value
    would print 0.68 ×MAC here instead of 0.82 ×MAC.
    """

    own_mac = MacPercent(1.5)
    run = replace(_run_frame((300.0,), vessel_rich=(0.0123,)), mac_percent=own_mac)
    fraction = Fraction(0.0123)

    assert own_mac != _SEVOFLURANE_MAC
    assert format_trace_hover(run, RecordedQuantity.VESSEL_RICH, 0, 1).splitlines()[2] == (
        f"{format_percent(fraction)}   {format_mac_multiple(fraction, own_mac)}"
    )
    assert format_mac_multiple(fraction, own_mac) == "0.82 ×MAC"


def test_the_hover_states_the_instant_at_the_clock_s_own_resolution() -> None:
    """A drawn instant is a whole second, and the hover prints it as the clock would."""

    run = _run_frame((410.0,), alveolar=(0.01,))

    assert format_trace_hover(run, RecordedQuantity.ALVEOLAR, 0, 1).splitlines()[0] == (
        "Modelled sevoflurane · 6m50s"
    )


@pytest.mark.parametrize("plot_width_px", [600.0, 873.0, 900.0, 1366.0, 2560.0])
@pytest.mark.parametrize("seconds", [8, 600])
def test_the_hover_value_belongs_to_the_instant_it_prints(
    plot_width_px: float, seconds: int
) -> None:
    """`PL-T5NJ`: the state printed beside an instant is the state at that instant.

    Columns used to sit wherever the plot's width put them, and the hover
    rounded the column's instant to a tenth of a second. Desflurane at 18% and
    10 L/min takes the circuit from 2.68% at 6.00 s to 2.70% at 6.04 s, so the
    hover at "6s" could print 2.70% while the readout row at 6 s showed 2.68%.
    Each drawn column now sits on a whole second. So the printed instant is
    the drawn one, and the run evaluated afresh at the printed instant gives
    the printed value.
    """

    controller = SimulationController(agent_id="desflurane")
    controller.set_delivered_concentration_percent(Percent(18.0))
    controller.set_fresh_gas_flow(FreshGasFlow(10.0))
    controller.start()
    _advance(controller, seconds)

    frame = assemble_chart_frame(
        [_input(controller)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=plot_width_px,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    run = frame.runs[0]
    near = [index for index, time_s in enumerate(run.times_s) if 5 <= time_s <= 7]

    assert len(near) >= 2

    for index, time_s in enumerate(run.times_s):
        printed_s = round(time_s)

        assert time_s == printed_s
        assert format_trace_hover(run, RecordedQuantity.CIRCUIT, index, 1).splitlines()[0] == (
            f"Modelled desflurane · {format_elapsed(printed_s)}"
        )

    for index in near:
        printed_s = round(run.times_s[index])
        at_printed = controller.drawn_window(printed_s, printed_s, 2).compartment_fractions(
            RecordedSeries("desflurane", RecordedQuantity.CIRCUIT)
        )

        assert format_trace_hover(run, RecordedQuantity.CIRCUIT, index, 1).splitlines()[2] == (
            f"{format_percent(Fraction(at_printed[0]))}   "
            f"{format_mac_multiple(Fraction(at_printed[0]), run.mac_percent)}"
        )


@pytest.mark.parametrize(
    ("raw_spacing_s", "expected_s"),
    [(43.2, 43), (3.6, 3), (2.0, 2), (1.07, 1), (1.0, 1), (0.9, 1), (0.873, 1), (0.0667, 1)],
)
def test_the_column_spacing_is_whole_seconds_and_widens_only_up_to_one_second(
    raw_spacing_s: float, expected_s: int
) -> None:
    """A spacing of a second or more is rounded down, and a smaller one is raised to one second.

    A run stands only on whole seconds, so no column can be drawn between two
    of them (`PL-SZ6G`).
    """

    spacing_s = grid_spacing_s(raw_spacing_s)

    assert type(spacing_s) is int
    assert spacing_s == expected_s
    assert spacing_s <= max(raw_spacing_s, 1)


def test_the_hover_answers_every_drawn_point_within_reach_and_nothing_else() -> None:
    run = _run_frame(
        (0.0, 100.0, 200.0),
        alveolar=(0.0, 0.010, 0.012),
        circuit=(0.0, 0.020, 0.020),
        fat=(0.0, 0.0001, 0.0002),
    )
    frame = _frame(run)
    # Each pixel is one second wide and one hundredth of a percent tall, and
    # the reach is 12 px.
    reach = dict(seconds_per_pixel=1.0, percent_per_pixel=0.01, radius_pixels=12.0)

    on_alveolar = nearest_trace_point(frame, 103.0, 1.02, **reach)
    assert on_alveolar is not None
    assert (on_alveolar.quantities, on_alveolar.anchor.time_s, on_alveolar.anchor.value) == (
        (RecordedQuantity.ALVEOLAR,),
        100.0,
        1.0,
    )
    assert tuple(reading.run for reading in on_alveolar.readings) == (0,)
    assert on_alveolar.readout == format_trace_hover(run, RecordedQuantity.ALVEOLAR, 1, 1)

    # The pointer is between two columns, on the 1 MAC line. No drawn point is
    # near, and a reference line is never reported.
    assert nearest_trace_point(frame, 150.0, 2.0, **reach) is None
    # A point beyond reach in pixels is not reported, however close it is in
    # seconds.
    assert nearest_trace_point(frame, 100.0, 1.2, **reach) is None


def test_a_hidden_trace_answers_no_hover() -> None:
    run = _run_frame((0.0, 100.0), alveolar=(0.0, 0.010), circuit=(0.0, 0.020))
    reach = dict(seconds_per_pixel=1.0, percent_per_pixel=0.01, radius_pixels=12.0)

    shown = nearest_trace_point(_frame(run), 100.0, 2.0, **reach)
    assert shown is not None and shown.quantities == (RecordedQuantity.CIRCUIT,)

    hidden = nearest_trace_point(_frame(run, (RecordedQuantity.ALVEOLAR,)), 100.0, 2.0, **reach)
    assert hidden is None


def test_the_wash_in_hover_answers_its_own_stretches_in_its_own_units() -> None:
    run = _run_frame((0.0, 100.0, 200.0))
    frame = _frame(run)
    reach = dict(seconds_per_pixel=1.0, ratio_per_pixel=0.002, radius_pixels=12.0)

    target = nearest_wash_in_point(frame, 101.0, 0.705, **reach)
    assert target is not None
    assert target.quantities == (RecordedQuantity.WASH_IN_RATIO,)
    assert (target.anchor.time_s, target.anchor.value) == (100.0, 0.71)
    assert target.readout.splitlines()[1:] == [WASH_IN_HOVER_LABEL, "0.71"]
    # On the equilibrium line, away from the trace, the reference line reports
    # nothing.
    assert nearest_wash_in_point(frame, 100.0, 1.0, **reach) is None


def test_a_point_exactly_one_radius_from_the_pointer_is_reported_on_both_plots() -> None:
    """The radius is how far a point may be and still be reported, so a point that far is reported.

    The pointer is level with the drawn point at 100 s and 12 s to its right.
    At one second per pixel, that is exactly 12 px, which is the radius. The
    next drawn instant is 100 s further on, so the pointer still names 100 s.
    A pointer the smallest possible step further right is out of reach.
    """

    run = _run_frame((0.0, 100.0, 200.0), alveolar=(0.0, 0.01, 0.01))
    frame = _frame(run, visible=(RecordedQuantity.ALVEOLAR,))
    beyond_s = nextafter(112.0, inf)

    on_trace = nearest_trace_point(frame, 112.0, 1.0, 1.0, 0.01, 12.0)
    on_wash_in = nearest_wash_in_point(frame, 112.0, 0.71, 1.0, 0.002, 12.0)

    assert on_trace is not None
    assert (on_trace.anchor.time_s, on_trace.anchor.value) == (100.0, 1.0)
    assert on_wash_in is not None
    assert (on_wash_in.anchor.time_s, on_wash_in.anchor.value) == (100.0, 0.71)
    assert nearest_trace_point(frame, beyond_s, 1.0, 1.0, 0.01, 12.0) is None
    assert nearest_wash_in_point(frame, beyond_s, 0.71, 1.0, 0.002, 12.0) is None


def test_a_pointer_past_a_run_s_last_drawn_instant_reads_that_instant_on_both_plots() -> None:
    """Past the last drawn point, the drawn instant nearest the pointer in time is the last one.

    "Fit run" can leave the axis wider than the run, so a pointer can rest in
    the empty space to the right of the live end. Here it is 3 px to the right
    of the last point.
    """

    run = _run_frame((0.0, 100.0, 200.0), alveolar=(0.0, 0.01, 0.012))
    frame = _frame(run, visible=(RecordedQuantity.ALVEOLAR,))

    on_trace = nearest_trace_point(frame, 203.0, 1.2, 1.0, 0.01, 12.0)
    on_wash_in = nearest_wash_in_point(frame, 203.0, 0.71, 1.0, 0.002, 12.0)

    assert on_trace is not None and on_trace.anchor.time_s == 200.0
    assert on_wash_in is not None and on_wash_in.anchor.time_s == 200.0


def test_a_pointer_midway_across_a_wash_in_gap_reads_the_earlier_stretch() -> None:
    """A pointer equally far in time from two stretches reads the earlier one.

    The first stretch ends on its crossing column at 60 s, and the next one
    starts on its crossing column at 80 s. A pointer at 70 s is 10 s from
    each. A tie between two columns of one stretch goes to the earlier column,
    and a tie between two stretches goes the same way. So the instant that the
    readout states depends only on where the pointer is.
    """

    early = WashInStretch((40.0, 50.0, 60.0), (0.97, 0.99, 1.02), True)
    late = WashInStretch((80.0, 90.0), (1.03, 0.98), False)
    run = replace(_run_frame((40.0, 90.0)), wash_in=(early, late))

    target = nearest_wash_in_point(_frame(run), 70.0, 1.025, 1.0, 0.002, 12.0)

    assert target is not None
    assert (target.anchor.time_s, target.anchor.value) == (60.0, 1.02)


def test_a_run_out_of_reach_leaves_the_three_line_form_standing() -> None:
    """Reporting every run in reach is not the same as reporting every run drawn.

    The second run's alveolar point is 30 px away, so only one run is
    reported. The readout is the three-line form that `docs/INTERFACE.md`
    § "What it shows" derives. It still names the run, because two runs are drawn (`PL-MN4J`).
    """

    first = _run_frame((1208.0,), alveolar=(0.0143,))
    second = replace(_run_frame((1208.0,), alveolar=(0.0193,)), label=run_label(SECOND_RUN))
    frame = replace(_frame(first), runs=(first, second))

    target = nearest_trace_point(frame, 1208.0, 1.43, 4.0, _PERCENT_PER_PIXEL, 12.0)

    assert target is not None
    assert (1.93 - 1.43) / _PERCENT_PER_PIXEL > 12.0, (
        "the second run must be out of reach to test anything"
    )
    assert tuple(reading.run for reading in target.readings) == (0,)
    assert target.readout == format_trace_hover(first, RecordedQuantity.ALVEOLAR, 0, 2)
    assert target.readout.splitlines()[0] == "Modelled sevoflurane · Run 1 · 20m8s"


def test_a_compared_hover_states_each_run_s_own_instant() -> None:
    """Two runs are reported at their own drawn points, which need not share an instant.

    Both runs lie on the shared anchored grid. Each run also adds the columns
    on which its own control events fall. The points nearest one pointer can
    therefore be up to one grid column apart, which is 4 s here. One instant
    above a column of values would claim a simultaneity that the readings do
    not have.
    """

    first = _run_frame((1208.0,), alveolar=(0.0143,))
    second = replace(_run_frame((1204.0,), alveolar=(0.0143,)), label=run_label(SECOND_RUN))
    frame = replace(_frame(first), runs=(first, second))

    target = nearest_trace_point(frame, 1208.0, 1.43, 4.0, _PERCENT_PER_PIXEL, 12.0)

    assert target is not None
    assert tuple(reading.time_s for reading in target.readings) == (1208.0, 1204.0)
    assert target.readout.splitlines() == [
        "Modelled sevoflurane",
        "Alveolar (end-tidal-equivalent)",
        "Run 1 · 20m8s   1.43%   0.79 ×MAC",
        "Run 2 · 20m4s   1.43%   0.79 ×MAC",
    ]


def test_a_compared_hover_answers_for_every_run_in_reach_however_many_there_are() -> None:
    """Nothing in the rule is a property of there being exactly two runs."""

    runs = tuple(
        replace(
            _run_frame((1208.0,), alveolar=(0.0143 + 0.0001 * index,)),
            label=run_label(RUN_IDS[index]),
        )
        for index in range(3)
    )
    frame = replace(_frame(runs[0]), runs=runs)

    target = nearest_trace_point(frame, 1208.0, 1.44, 4.0, _PERCENT_PER_PIXEL, 12.0)

    assert target is not None
    assert tuple(reading.run for reading in target.readings) == (0, 1, 2)
    assert [line.split()[1] for line in target.readout.splitlines()[2:]] == ["1", "2", "3"]


def test_the_frame_refuses_two_runs_whose_mac_is_stated_for_different_ages() -> None:
    """Two runs on one agent still need one MAC and one age, because they share one MAC axis.

    Every run uses the reference adult today, so the second run's age is
    written into its snapshot here. Once a patient's age is an input, two
    compared runs could differ in it, and the second run's traces would be
    read against the first run's 1 MAC line and age without this check.
    """

    first = _input(_run(10))
    older = _input(_run(10), run_index=1)
    older = replace(older, snapshot=replace(older.snapshot, agent_mac_age_years=70))

    with pytest.raises(
        ValueError,
        match=r"^every run on the chart must divide by the same MAC for the same age, because "
        r"they share one MAC axis and one 1 MAC line; given 1\.8% at age 40, 1\.8% at age 70$",
    ):
        assemble_chart_frame(
            [first, older],
            None,
            COMPARTMENT_QUANTITIES,
            plot_width_px=_PLOT_WIDTH_PX,
            held_start_s=None,
            ceiling=ChartCeiling.STANDARD,
        )


def test_a_compared_hover_refuses_to_name_one_agent_over_another_run_s_value() -> None:
    """The agent is named once, above the values, so the runs must share it.

    `assemble_chart_frame` already rejects such a frame, because one MAC ruler
    is drawn across every run. This check is therefore the second guard
    rather than the first. It guards the one line that turns a per-run
    qualifier into a shared one.
    """

    run = _run_frame((1208.0,), alveolar=(0.0143,))
    other = replace(run, agent_display_name="Desflurane", label=run_label(SECOND_RUN))

    with pytest.raises(ValueError, match="must be on the same agent"):
        format_compared_trace_hover(
            ((run, RecordedQuantity.ALVEOLAR, 0), (other, RecordedQuantity.ALVEOLAR, 0)), 2
        )

    with pytest.raises(ValueError, match="must be on the same agent"):
        format_compared_wash_in_hover(((run, run.wash_in[0], 0), (other, other.wash_in[0], 0)))


def test_a_compared_hover_is_answered_for_at_least_one_run() -> None:
    with pytest.raises(ValueError, match="at least one drawn point"):
        format_compared_trace_hover((), 1)

    with pytest.raises(ValueError, match="at least one run"):
        format_compared_wash_in_hover(())

    run = _run_frame((1208.0,), alveolar=(0.0143,))

    with pytest.raises(ValueError, match="a chart draws at least one run"):
        format_compared_trace_hover(((run, RecordedQuantity.ALVEOLAR, 0),), 0)


def test_a_compared_trace_readout_of_one_point_names_its_agent_compartment_and_run() -> None:
    """The compared form refuses an empty list of readings, so a single reading is valid input.

    The wash-in plot's compared form is already given a single reading
    (`test_the_wash_in_hover_withholds_the_ratio_at_an_elimination_terminus`).
    The expected lines are worked by hand: 1.43% over sevoflurane's 1.8% MAC
    is 0.79 ×MAC, and 1208 s is 20m8s.
    """

    run = _run_frame((1208.0,), alveolar=(0.0143,))

    assert format_compared_trace_hover(((run, RecordedQuantity.ALVEOLAR, 0),), 2).splitlines() == [
        "Modelled sevoflurane",
        "Alveolar (end-tidal-equivalent)",
        "Run 1 · 20m8s   1.43%   0.79 ×MAC",
    ]


def test_the_wash_in_hover_answers_every_run_in_reach_in_its_own_units() -> None:
    """The same rule on the wash-in plot, where there is no compartment to aim at."""

    first = _run_frame((0.0, 100.0, 200.0))
    second = replace(
        _run_frame((0.0, 100.0, 200.0)),
        label=run_label(SECOND_RUN),
        wash_in=(WashInStretch((0.0, 100.0, 200.0), (0.68, 0.68, 0.68), False),),
    )
    frame = replace(_frame(first), runs=(first, second))
    reach = dict(seconds_per_pixel=1.0, ratio_per_pixel=0.002, radius_pixels=12.0)

    target = nearest_wash_in_point(frame, 100.0, 0.695, **reach)

    assert target is not None
    assert target.quantities == (RecordedQuantity.WASH_IN_RATIO,)
    assert tuple(reading.run for reading in target.readings) == (0, 1)
    assert target.readout.splitlines() == [
        "Modelled sevoflurane",
        WASH_IN_HOVER_LABEL,
        "Run 1 · 1m40s   0.71",
        "Run 2 · 1m40s   0.68",
    ]


# ------------------------------------------- the run's channel, and the cap


def test_a_single_run_is_drawn_exactly_as_the_compartment_table_says() -> None:
    """The width channel does not exist until there is a second run to tell apart."""

    for style in COMPARTMENT_TRACES:
        assert run_trace_style(style.quantity, 0, 1) == style


def test_two_runs_differ_only_in_width_and_the_first_is_the_wider() -> None:
    """`PL-HLD5`: style and colour show the compartment, and width shows the run.

    The width only has to tell apart two adjacent curves of one compartment, so
    it is read locally rather than across the plot. The first run is widened,
    rather than the second narrowed, for two reasons. A branch reproduces its
    parent up to the fork, so the two curves coincide there, and the narrower
    one has to be drawn on top. Also, nothing is then drawn thinner than the
    single-run chart draws it. That keeps every trace's contrast against the
    panel at the width where the contrast was measured.
    """

    for style in COMPARTMENT_TRACES:
        first = run_trace_style(style.quantity, 0, 2)
        second = run_trace_style(style.quantity, 1, 2)

        assert second == style
        assert first.stroke_width == style.stroke_width + COMPARED_RUN_WIDTH_STEP
        assert first.color == second.color
        assert first.dash_pattern == second.dash_pattern
        assert first.line_style == second.line_style
        assert first.label == second.label


def test_a_style_is_refused_for_a_run_the_chart_is_not_drawing() -> None:
    """A width for a run that is not on the chart would describe nothing on screen."""

    for run_index, run_count in ((1, 1), (-1, 2), (2, 2), (0, 0)):
        with pytest.raises(ValueError, match="runs on the chart"):
            run_trace_style(RecordedQuantity.ALVEOLAR, run_index, run_count)


@pytest.mark.parametrize("count", [1, 2, 3])
def test_a_run_count_of_one_or_more_is_built_and_compares_as_its_int(count: int) -> None:
    built = RunCount(count)

    assert isinstance(built, RunCount)
    assert built == count


@pytest.mark.parametrize("count", [0, -1])
def test_a_run_count_below_one_is_refused(count: int) -> None:
    """A chart that draws no run has nothing to style, hover or name (`PL-7694`)."""

    with pytest.raises(ValueError, match=f"a chart draws at least one run, not {count}"):
        RunCount(count)


@pytest.mark.parametrize("index", [0, 1, 2])
def test_a_nonnegative_run_index_is_built_and_compares_as_its_int(index: int) -> None:
    built = RunIndex(index)

    assert isinstance(built, RunIndex)
    assert built == index


@pytest.mark.parametrize("index", [-1, -2])
def test_a_negative_run_index_is_refused(index: int) -> None:
    """Python treats -1 as the last run, so it would name the wrong run's values (`PL-7694`)."""

    with pytest.raises(ValueError, match=f"counted from 0, not {index}"):
        RunIndex(index)


@pytest.mark.parametrize("value", [True, False, 1.0, "1", None])
def test_a_run_count_or_index_that_is_not_an_int_is_refused(value: object) -> None:
    """A `bool` is an `int` to Python, and would make `True` one run or the second run."""

    with pytest.raises(TypeError, match="a run count is an int"):
        RunCount(value)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="a run index is an int"):
        RunIndex(value)  # type: ignore[arg-type]


def test_a_frame_s_run_count_is_the_checked_count_of_its_runs() -> None:
    frame = assemble_chart_frame(
        [_input(_run(60))],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert isinstance(frame.run_count, RunCount)
    assert frame.run_count == len(frame.runs) == 1


def test_one_run_draws_every_compartment_the_reader_left_shown() -> None:
    """The cap exists to free the width channel, so it applies only when that channel is needed."""

    assert compared_compartments(COMPARTMENT_QUANTITIES, 1) == (COMPARTMENT_QUANTITIES, 0)


def test_two_runs_cap_the_drawn_compartments_and_count_what_they_removed() -> None:
    """Two compartments times two runs is four curves, and the rest are counted."""

    drawn, undrawn = compared_compartments(COMPARTMENT_QUANTITIES, 2)

    assert len(drawn) == COMPARED_COMPARTMENT_CAP
    assert undrawn == len(COMPARTMENT_QUANTITIES) - COMPARED_COMPARTMENT_CAP
    # The drawn pair follows table order, not the order a reader clicked, so
    # it is the same pair whichever route reached the selection.
    assert drawn == COMPARTMENT_QUANTITIES[:COMPARED_COMPARTMENT_CAP]


def test_a_selection_already_inside_the_cap_is_left_alone() -> None:
    """Nothing is removed, and nothing is reported removed."""

    chosen = (RecordedQuantity.MUSCLE, RecordedQuantity.FAT)

    assert compared_compartments(chosen, 2) == (chosen, 0)
    assert compared_compartments((RecordedQuantity.FAT,), 2) == ((RecordedQuantity.FAT,), 0)
    assert compared_compartments((), 2) == ((), 0)


def test_a_frame_of_two_runs_draws_the_capped_set_and_says_what_it_left_out() -> None:
    """The cap is applied where the frame is assembled, not where a reader clicks."""

    first = _run(60)
    second = _run(60)
    frame = assemble_chart_frame(
        (_input(first), _input(second, run_index=1)),
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert frame.visible == COMPARTMENT_QUANTITIES[:COMPARED_COMPARTMENT_CAP]
    assert frame.undrawn_compartments == len(COMPARTMENT_QUANTITIES) - COMPARED_COMPARTMENT_CAP
    assert tuple(run.label for run in frame.runs) == (run_label(FIRST_RUN), run_label(SECOND_RUN))


def test_a_branch_carries_its_fork_and_a_trunk_carries_none() -> None:
    """The frame marks the one instant at which two compared runs stop being the same run."""

    trunk = _run(60)
    trunk.begin_control_adjustment()
    trunk.set_fresh_gas_flow(FreshGasFlow(3.0))
    _advance(trunk, 60)
    case = BranchedCase(trunk)
    branch = case.fork_at(CaseInstant(60))
    frame = assemble_chart_frame(
        (_input(trunk), _input(branch, run_index=1)),
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert frame.runs[0].branch_point_s is None
    assert frame.runs[1].branch_point_s == pytest.approx(60.0)


def test_a_bookmark_branch_is_marked_at_its_fork_and_not_at_its_definition_s_opening() -> None:
    """The frame marks the instant at which two runs diverge, even when that is not a keyframe.

    A bookmark branch's run definition opens at the keyframe *before* the
    fork. A frame that took the definition's own opening as the branch point
    would draw the line where the trunk was still the only run. That would
    put the fork at a time it did not happen, which the assembly's own
    comment guards against. `opened_from.fork.instant_s` is the fork's
    instant, whichever way the branch was created.
    """

    trunk = SimulationController()
    trunk.add_time_bookmark(TimeBookmark(CaseInstant(45), "the decision point"))
    trunk.start()
    _advance(trunk, 30)
    trunk.begin_control_adjustment()
    trunk.set_fresh_gas_flow(FreshGasFlow(3.0))

    for _ in range(60 // SIMULATION_STEP_S):
        trunk.advance()

        if trunk.snapshot().bookmark_halt is not None:
            break

    fork_s = trunk.snapshot().elapsed_s
    case = BranchedCase(trunk)
    branch = case.fork_here()

    assert fork_s == 45
    assert branch.run_segments[0].opened_at_s == 30 < fork_s

    frame = assemble_chart_frame(
        (_input(trunk), _input(branch, run_index=1)),
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert frame.runs[0].branch_point_s is None
    assert frame.runs[1].branch_point_s == fork_s


def test_a_fork_outside_the_drawn_window_is_not_marked_at_its_edge() -> None:
    """A mark pinned to the edge would put the fork at a time it did not happen."""

    trunk = _run(60)
    trunk.begin_control_adjustment()
    trunk.set_fresh_gas_flow(FreshGasFlow(3.0))
    _advance(trunk, 1800)
    case = BranchedCase(trunk)
    branch = case.fork_at(CaseInstant(60))
    _advance(branch, 1800)
    frame = assemble_chart_frame(
        (_input(trunk), _input(branch, run_index=1)),
        time_base_for_span(900.0),
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert frame.start_s > 60.0
    assert frame.runs[1].branch_point_s is None


def test_a_fork_on_either_edge_of_the_window_is_marked_there() -> None:
    """The window includes both of its edges, so a fork that falls on one is drawn.

    A branch taken at the trunk's newest instant forks on the right edge of a
    fitted window: both runs stand at 900 s, which is where that window ends.
    A chosen 15-minute width that follows a trunk at 1 200 s starts at 318 s.
    That is 1 200 s, plus 2% of the width as headroom (18 s), less the 900 s
    width. A branch taken at 318 s forks on that left edge.
    """

    trunk = _run(900)
    at_right = assemble_chart_frame(
        (_input(trunk), _input(BranchedCase(trunk).fork_at(CaseInstant(900)), run_index=1)),
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert at_right.stop_s == 900.0
    assert at_right.runs[1].branch_point_s == 900

    trunk = _run(1200)
    at_left = assemble_chart_frame(
        (_input(trunk), _input(BranchedCase(trunk).fork_at(CaseInstant(318)), run_index=1)),
        time_base_for_span(900.0),
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert at_left.start_s == 318.0
    assert at_left.runs[1].branch_point_s == 318


# ---------------------------------------------------- previewing a dragged setting

_PREVIEW_LABEL = "Preview: Fresh gas flow 6.0 L/min, not applied"


def _previewing(
    controller: SimulationController, control: ControlInput, value: float, run_index: int = 0
) -> RunInput:
    return replace(
        _input(controller, run_index=run_index),
        preview=PreviewRequest(SettingPreview(control, value), _PREVIEW_LABEL),
    )


def test_a_preview_matches_a_twin_run_that_applied_the_setting() -> None:
    """The preview is the trajectory the run takes if the dragged value is applied now.

    The expected values come from a twin run with the same history. The twin
    really applies the value and is advanced past it
    (`.claude/rules/test-oracles.md` rule 2). The preview is drawn from a
    second definition, so the two agree to within floating-point composition
    error, not bit for bit (`PL-5B1N`).
    """

    previewed, applied = _run(300), _run(300)
    base = time_base_for_span(1800.0)
    frame = assemble_chart_frame(
        [_previewing(previewed, ControlInput.FRESH_GAS_FLOW, 6.0)],
        base,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    applied.set_fresh_gas_flow(FreshGasFlow(6.0))
    _advance(applied, 600)
    preview = frame.runs[0].preview
    assert preview is not None
    truth = applied.drawn_window(frame.start_s, frame.stop_s, frame.columns)
    predicted = dict(
        zip(preview.times_s, preview.fractions[RecordedQuantity.ALVEOLAR], strict=True)
    )
    common = [
        (time_s, fraction)
        for time_s, fraction in zip(
            truth.times_s,
            truth.compartment_fractions(RecordedSeries("sevoflurane", RecordedQuantity.ALVEOLAR)),
            strict=True,
        )
        if time_s in predicted and time_s > 300.0
    ]

    assert len(common) > 100
    assert all(
        predicted[time_s] == pytest.approx(fraction, rel=1e-9) for time_s, fraction in common
    )
    # The run itself kept the setting in force: the preview applied nothing.
    assert previewed.settings().fresh_gas_flow_l_min != 6.0
    assert previewed.record().control_timeline == ()


def test_a_preview_past_its_first_hour_draws_the_second_its_ratio_crosses_equilibrium() -> None:
    """A predicted wash-in stretch that starts after the first hour starts on the line (`PL-CJJ1`).

    With the fresh gas at 1 L/min and the dial at 8% for 30 minutes, a
    preview of the dial at 0.5% predicts F_A/F_I falling back below 1 about
    two and a half hours later. Past its first hour a preview predicts only
    the grid seconds, which are 102 s apart on this axis, so the last second
    outside the wash-in domain lay between two columns and was not drawn. The
    expected second is found in a twin run that applies the setting and steps
    on (rule 2 of `.claude/rules/test-oracles.md`).
    """

    def started(controller: SimulationController) -> SimulationController:
        controller.set_fresh_gas_flow(FreshGasFlow(1.0))
        controller.set_delivered_concentration_percent(Percent(8.0))
        controller.start()
        _advance(controller, 1800)

        return controller

    previewed, applied = started(SimulationController()), started(SimulationController())
    preview = SettingPreview(ControlInput.DELIVERED, 0.5)
    window = previewed.preview_window(preview, 0.0, 1800.0 + 8 * 3600.0, 300)

    applied.set_delivered_concentration_percent(Percent(0.5))
    first_s, last_s = 1800 + PREVIEW_EXACT_S, 1800 + 4 * 3600
    _advance(applied, last_s - 1800)
    truth = applied.drawn_window(float(first_s), float(last_s), last_s - first_s)
    assert truth.times_s == tuple(range(first_s, last_s + 1))
    ratios = [
        wash_in_ratio(state[ALVEOLAR_FRACTION], state[INSPIRED_FRACTION]) for state in truth.states
    ]
    inside = [ratio is not None and is_wash_in(ratio) for ratio in ratios]
    entering_s = next(
        second
        for second, before, after in zip(truth.times_s, inside, inside[1:], strict=False)
        if not before and after
    )

    assert entering_s in window.times_s


@pytest.mark.parametrize(
    ("state_index", "peak_s"),
    [(ALVEOLAR_FRACTION, 302), (VENOUS_FRACTION, 379), (FIRST_TISSUE_FRACTION, 363)],
)
def test_a_preview_after_turning_the_dial_off_draws_each_peak_the_run_would_reach(
    state_index: int, peak_s: int
) -> None:
    """A preview of the dial at zero draws the alveolar, venous and vessel-rich peaks to come.

    With sevoflurane at 2% for five minutes and the dial then turned off, the
    alveolar fraction still rises for 2 s, the vessel-rich group's for 63 s
    and the venous blood's for 79 s. The expected peak seconds are found in a
    twin run that applies the setting and steps on (rule 2 of
    `.claude/rules/test-oracles.md`), and the parameters check that the twin
    still peaks there. Each peak lies between two grid seconds 30 s apart, so
    a preview drawn only at the grid seconds misses all three
    (`PL-BLZJ`, which this test was written for).

    The limit is numerical. The prediction and the twin's steps each lie
    within `run_rounding` of the exact solution, as a share of the dial's 2%,
    so the two lie within twice that of each other.
    """

    previewed, applied = _run(300), _run(300)
    preview = SettingPreview(ControlInput.DELIVERED, 0.0)
    settings = previewed.preview_settings(preview)

    window = previewed.preview_window(preview, 0.0, 1800.0, 60)

    applied.set_delivered_concentration_percent(Percent(0.0))
    _advance(applied, 900)
    truth = applied.drawn_window(300.0, 1200.0, 900)
    truth_by_second = dict(zip(truth.times_s, truth.states, strict=True))
    assert truth.times_s == tuple(range(300, 1201))
    assert max(truth.times_s, key=lambda t: truth_by_second[t][state_index]) == peak_s

    drawn = dict(zip(window.times_s, window.states, strict=True))
    assert peak_s % 30 != 0
    assert peak_s in drawn
    limit = (
        2.0
        * run_rounding(
            _squarings(build_system_matrix(settings), SIMULATION_STEP_S), StepCount(peak_s - 300)
        )
        * 0.02
    )
    assert abs(drawn[peak_s][state_index] - truth_by_second[peak_s][state_index]) <= limit


def test_a_preview_draws_a_crossing_between_its_exact_hour_and_its_first_later_column() -> None:
    """The pair that joins a preview's exact first hour to its later columns is searched too.

    With the fresh gas at 1 L/min and the dial at 8% for 1509 s, a preview of
    the dial at 0.5% predicts F_A/F_I last outside the wash-in domain 13 s
    after the exact hour ends, and the first later column is 42 s after it.
    The expected second comes from one-second predictions of the same
    settings and state.
    """

    controller = SimulationController()
    controller.set_fresh_gas_flow(FreshGasFlow(1.0))
    controller.set_delivered_concentration_percent(Percent(8.0))
    controller.start()
    _advance(controller, 1509)
    preview = SettingPreview(ControlInput.DELIVERED, 0.5)
    exact_s = 1509 + PREVIEW_EXACT_S
    states = predicted_states(
        controller.preview_settings(preview),
        controller._state.stored_states.state_at(CaseInstant(1509)),
        CaseInstant(1509),
        CaseInstant(exact_s + 600),
    )
    inside = [
        (ratio := wash_in_ratio(state[ALVEOLAR_FRACTION], state[INSPIRED_FRACTION])) is not None
        and is_wash_in(ratio)
        for state in states
    ]
    crossing_s = next(
        1509 + index
        for index, (before, after) in enumerate(zip(inside, inside[1:], strict=False))
        if 1509 + index > exact_s and not before and after
    )

    window = controller.preview_window(preview, 0.0, 1509.0 + 8 * 3600.0, 300)
    later_s = [second for second in window.times_s if second > exact_s]

    assert later_s[0] == crossing_s


def test_a_later_crossing_is_found_between_columns_two_seconds_apart_and_never_on_one() -> None:
    """`_with_later_crossings` searches every pair at least two seconds apart, and adds no column.

    The run and the preview are those of the test above, whose ratio last lies
    outside the wash-in domain at one second about two and a half hours on.
    Each state is taken from one-second predictions, so each pair below is cut
    from the curve itself. A pair two seconds apart whose middle second is the
    crossing must yield it. A pair whose left second is the crossing must
    return its columns unchanged, because that second is already drawn.
    """

    controller = SimulationController()
    controller.set_fresh_gas_flow(FreshGasFlow(1.0))
    controller.set_delivered_concentration_percent(Percent(8.0))
    controller.start()
    _advance(controller, 1800)
    settings = controller.preview_settings(SettingPreview(ControlInput.DELIVERED, 0.5))
    opening = controller._state.stored_states.state_at(CaseInstant(1800))
    states = predicted_states(settings, opening, CaseInstant(1800), CaseInstant(1800 + 4 * 3600))
    inside = [
        (ratio := wash_in_ratio(state[ALVEOLAR_FRACTION], state[INSPIRED_FRACTION])) is not None
        and is_wash_in(ratio)
        for state in states
    ]
    crossing_s = next(
        1800 + index
        for index, (before, after) in enumerate(zip(inside, inside[1:], strict=False))
        if index > PREVIEW_EXACT_S and not before and after
    )

    def state(second: int) -> tuple[float, ...]:
        return states[second - 1800]

    def later(*seconds: int) -> tuple[tuple[CaseInstant, ...], tuple[tuple[float, ...], ...]]:
        return tuple(CaseInstant(second) for second in seconds), tuple(map(state, seconds))

    middle_s, middle_states = later(crossing_s + 1, crossing_s + 60)
    found_s, found_states = _with_later_crossings(
        settings, CaseInstant(crossing_s - 1), state(crossing_s - 1), middle_s, middle_states
    )

    assert found_s == (crossing_s, crossing_s + 1, crossing_s + 60)
    assert found_states[0] == pytest.approx(state(crossing_s))

    left_s, left_states = later(crossing_s + 2, crossing_s + 60)

    assert _with_later_crossings(
        settings, CaseInstant(crossing_s), state(crossing_s), left_s, left_states
    ) == (left_s, left_states)


def test_a_preview_past_its_first_hour_draws_the_grid_seconds_and_its_right_edge_only() -> None:
    """On a 12-hour axis, the preview steps every second for an hour and draws each column after it.

    A preview of every second to the right edge took 0.26 s on this axis and
    stalled a held drag (`PL-Z6C8`). So past `PREVIEW_EXACT_S` the preview is
    predicted at the grid seconds and the right edge only. Within the first
    hour it still draws the alveolar peak 2 s after the dial is turned off,
    which no grid second holds. Each value drawn after the first hour is
    checked against a twin run that applies the setting and steps every
    second (rule 2 of `.claude/rules/test-oracles.md`).

    The limit is numerical: the prediction's rounding, one-second steps for
    an hour and one propagator over 43 s for each column after it, plus the
    twin's rounding over its one-second steps, as a share of the dial's 2%.
    """

    previewed, applied = _run(300), _run(300)
    preview = SettingPreview(ControlInput.DELIVERED, 0.0)
    settings = previewed.preview_settings(preview)

    window = previewed.preview_window(preview, 0.0, 43_200.0, 1_001)

    spacing_s = 43
    exact_end_s = 300 + PREVIEW_EXACT_S
    later_s = tuple(second for second in window.times_s if second > exact_end_s)
    first_column_s = (exact_end_s // spacing_s + 1) * spacing_s
    assert later_s == (*range(first_column_s, 43_200, spacing_s), 43_200)
    assert 302 in window.times_s

    applied.set_delivered_concentration_percent(Percent(0.0))
    checked_until_s = exact_end_s + 1_800
    _advance(applied, checked_until_s - 300)
    truth = applied.drawn_window(300.0, float(checked_until_s), checked_until_s - 299)
    truth_by_second = dict(zip(truth.times_s, truth.states, strict=True))
    drawn = dict(zip(window.times_s, window.states, strict=True))
    matrix = build_system_matrix(settings)
    one_second = _squarings(matrix, SIMULATION_STEP_S)
    column = propagator_rounding(_squarings(matrix, spacing_s))
    checked = [second for second in later_s if second <= checked_until_s]
    assert len(checked) == 42

    for count, second in enumerate(checked, start=1):
        limit = (
            run_rounding(one_second, StepCount(PREVIEW_EXACT_S))
            + column * (count + 1)
            + run_rounding(one_second, StepCount(second - 300))
        ) * 0.02

        for index, _ in FRACTION_STATE_NAMES:
            difference = abs(drawn[second][index] - truth_by_second[second][index])
            assert difference <= limit, (second, index, difference, limit)


def test_a_preview_at_the_run_s_own_setting_coincides_with_what_the_run_then_draws() -> None:
    controller = _run(300)
    held = controller.settings().delivered_concentration_percent
    base = time_base_for_span(1800.0)
    frame = assemble_chart_frame(
        [_previewing(controller, ControlInput.DELIVERED, held)],
        base,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    preview = frame.runs[0].preview
    assert preview is not None
    _advance(controller, 600)
    later = controller.drawn_window(frame.start_s, frame.stop_s, frame.columns)
    drawn = dict(
        zip(
            later.times_s,
            later.compartment_fractions(RecordedSeries("sevoflurane", RecordedQuantity.FAT)),
            strict=True,
        )
    )
    shared = [t for t in preview.times_s if t in drawn]

    assert len(shared) > 100
    assert all(
        fraction == pytest.approx(drawn[t], rel=1e-9)
        for t, fraction in zip(
            preview.times_s, preview.fractions[RecordedQuantity.FAT], strict=True
        )
        if t in drawn
    )

    # The predicted F_A/F_I is the run's own later ratio too, on the shared instants.
    later_frame = assemble_chart_frame(
        [_input(controller)],
        base,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    later_ratio = {
        t: ratio
        for stretch in later_frame.runs[0].wash_in
        for t, ratio in zip(stretch.times_s, stretch.ratios, strict=True)
    }
    predicted = [
        (t, ratio)
        for stretch in preview.wash_in
        for t, ratio in zip(stretch.times_s, stretch.ratios, strict=True)
        if t in later_ratio
    ]

    assert len(predicted) > 100
    assert all(ratio == pytest.approx(later_ratio[t], rel=1e-9) for t, ratio in predicted)


def test_a_preview_on_an_axis_that_ends_at_the_reach_predicts_nothing() -> None:
    """An axis with no time ahead of the run has no prediction to draw, not a single point.

    The controller's preview window (`SimulationController.preview_window`) is
    empty when the axis ends at or before the run's reach. The axis here ends
    exactly at the reach. So does an axis that ends inside the next step,
    because a prediction is drawn only at whole seconds. An axis one step
    longer gets a prediction that holds the reach and that step.
    """

    controller = _run(60)
    setting = SettingPreview(ControlInput.FRESH_GAS_FLOW, 6.0)

    assert controller.reached_s == 60
    assert controller.preview_window(setting, 0.0, 60.0, 600).times_s == ()
    assert controller.preview_window(setting, 0.0, 30.0, 600).times_s == ()
    assert controller.preview_window(setting, 0.0, 60.9, 600).times_s == ()
    assert controller.preview_window(setting, 0.0, 61.0, 600).times_s == (60, 61)


def test_a_preview_window_keeps_its_width_and_puts_the_reach_at_mid_plot() -> None:
    controller = _run(1200)
    base = time_base_for_span(900.0)
    following = assemble_chart_frame(
        [_input(controller)],
        base,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    previewing = assemble_chart_frame(
        [_previewing(controller, ControlInput.FRESH_GAS_FLOW, 6.0)],
        base,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert following.stop_s - following.start_s == pytest.approx(900.0)
    assert following.stop_s == pytest.approx(1200.0 + base.live_headroom_s)
    assert (previewing.start_s, previewing.stop_s) == pytest.approx((750.0, 1650.0))
    assert previewing.time_base == base


def test_a_preview_is_drawn_only_inside_its_region_and_carries_its_label() -> None:
    controller = _run(300)
    frame = assemble_chart_frame(
        [_previewing(controller, ControlInput.FRESH_GAS_FLOW, 6.0)],
        time_base_for_span(1800.0),
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    run = frame.runs[0]
    preview = run.preview
    assert preview is not None
    start_s, stop_s = preview.region_s

    assert start_s == pytest.approx(300.0)
    assert stop_s == pytest.approx(frame.stop_s)
    assert preview.times_s[0] == pytest.approx(start_s)
    assert all(start_s <= t <= stop_s for t in preview.times_s)
    assert all(t <= start_s for t in run.times_s)
    assert all(t >= start_s for stretch in preview.wash_in for t in stretch.times_s)
    assert preview.label == _PREVIEW_LABEL
    # The prediction meets the run where the run stands.
    assert preview.fractions[RecordedQuantity.ALVEOLAR][0] == pytest.approx(
        run.fractions[RecordedQuantity.ALVEOLAR][-1], rel=1e-12
    )


def test_a_frame_without_a_held_thumb_draws_no_preview() -> None:
    controller = _run(300)
    frame = assemble_chart_frame(
        [_input(controller)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert frame.runs[0].preview is None


def test_a_stopped_run_draws_no_preview_and_keeps_its_window() -> None:
    controller = _run(60)
    controller.fail("a failure the test injects", kind=FailureKind.UNEXPECTED)
    base = time_base_for_span(900.0)
    plain = assemble_chart_frame(
        [_input(controller)],
        base,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    frame = assemble_chart_frame(
        [_previewing(controller, ControlInput.FRESH_GAS_FLOW, 6.0)],
        base,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )

    assert frame.runs[0].preview is None
    assert (frame.start_s, frame.stop_s) == (plain.start_s, plain.stop_s)


def test_the_hover_never_answers_from_a_preview() -> None:
    controller = _run(300)
    frame = assemble_chart_frame(
        [_previewing(controller, ControlInput.DELIVERED, 8.0)],
        time_base_for_span(1800.0),
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    preview = frame.runs[0].preview
    assert preview is not None
    index = len(preview.times_s) // 2
    time_s = preview.times_s[index]
    percent = preview.percents(RecordedQuantity.ALVEOLAR)[index]

    # A pointer resting on a predicted point, well past the run's reach, gets no readout.
    assert time_s > 600.0
    assert nearest_trace_point(frame, time_s, percent, 1.0, 0.001, 12.0) is None


def test_a_preview_keeps_the_compartment_s_colour_and_dash_and_is_one_step_thinner() -> None:
    for style in COMPARTMENT_TRACES:
        for run_index, run_count in ((0, 1), (0, 2), (1, 2)):
            run = run_trace_style(style.quantity, run_index, run_count)
            preview = preview_trace_style(style.quantity, run_index, run_count)

            assert (preview.color, preview.dash_pattern) == (run.color, run.dash_pattern)
            assert preview.stroke_width == max(2, style.stroke_width - 1)
            assert preview.stroke_width >= MINIMUM_TRACE_STROKE_WIDTH


def test_no_compared_run_s_real_curve_is_thinner_than_a_preview_of_its_compartment() -> None:
    """In compare mode the other run's real curves can lie inside the preview region.

    The first run is drawn one step wider. A preview taken from its width
    would be wider than the second run's real curve of the same compartment,
    so the width cue would point the wrong way (found by the blind review of
    `PL-5B1N`).
    """

    for style in COMPARTMENT_TRACES:
        for previewing in (0, 1):
            preview = preview_trace_style(style.quantity, previewing, 2)

            for drawn in (0, 1):
                assert (
                    preview.stroke_width <= run_trace_style(style.quantity, drawn, 2).stroke_width
                )


def test_no_trace_and_no_preview_is_drawn_thinner_than_two_pixels() -> None:
    """A 1 px antialiased line renders under 3:1 against the panel.

    `docs/INTERFACE.md` § "The six compartment traces: what separates them" gives the reason.
    """

    assert MINIMUM_TRACE_STROKE_WIDTH == 2
    assert all(style.stroke_width >= 2 for style in COMPARTMENT_TRACES)
    assert preview_stroke_width(3) == 2
    assert preview_stroke_width(2) == 2
    assert preview_stroke_width(5) == 4


def test_a_compared_run_previews_from_its_own_reach_and_the_window_centres_on_it() -> None:
    trunk = _run(300)
    trunk.set_fresh_gas_flow(FreshGasFlow(3.0))
    _advance(trunk, 300)
    branch = BranchedCase(trunk).fork_at(CaseInstant(300))
    branch.start()
    _advance(branch, 60)
    base = time_base_for_span(1800.0)
    frame = assemble_chart_frame(
        (_input(trunk), _previewing(branch, ControlInput.CARDIAC_OUTPUT, 8.0, run_index=1)),
        base,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    preview = frame.runs[1].preview

    assert frame.runs[0].preview is None
    assert preview is not None
    assert preview.region_s[0] == pytest.approx(360.0)
    assert preview.times_s[0] == pytest.approx(360.0)
    assert (frame.start_s, frame.stop_s) == pytest.approx((0.0, 1800.0))
