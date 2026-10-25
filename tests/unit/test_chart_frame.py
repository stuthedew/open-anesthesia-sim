"""Tests of what one frame of the chart claims, checked without a GUI toolkit.

`app/chart_frame.py` is where the chart's presentation-correctness claims
live. They include which compartment a curve shows, where the reference
lines sit, which instants are drawn, and what a hover says. Every test here
runs with no display and no plotting library, which is the purpose of that
module.
"""

from dataclasses import replace
from math import hypot, inf, nextafter
from types import MappingProxyType

import pytest

from anesthesia_sim.app.bookmarks import TimeBookmark
from anesthesia_sim.app.chart_frame import (
    CHART_COLUMN_BUDGET_PER_SERIES,
    COMPARED_COMPARTMENT_CAP,
    COMPARTMENT_TRACES,
    HOVER_INSTANT_RESOLUTION_S,
    MAX_CHART_CONTROL_MARKS,
    WASH_IN_HOVER_LABEL,
    WASH_IN_TERMINUS_CEILING,
    ChartFrame,
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
    nearest_trace_point,
    nearest_wash_in_point,
    percent_axis_ticks,
    resample_owed,
    run_trace_style,
    trace_style,
    wash_in_axis_ticks,
    wash_in_stretches,
)
from anesthesia_sim.app.chart_time_base import TIME_BASE_LADDER, time_base_for_span
from anesthesia_sim.app.control_record import CONTROL_INPUT_UNITS, ControlInput
from anesthesia_sim.app.control_timeline import ControlAdjustment
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import run_label
from anesthesia_sim.app.formatting import (
    chart_axis_top_percent,
    chart_grid_interval_percent,
    format_mac_multiple,
    format_percent,
)
from anesthesia_sim.app.run_series import (
    COMPARTMENT_FRACTION_NAMES,
    COMPARTMENT_QUANTITIES,
    COMPARTMENT_STATE_INDEX,
    DrawnWindow,
    RecordedQuantity,
)
from anesthesia_sim.app.theme import COMPARED_RUN_WIDTH_STEP, ONE_MAC_LINE_DASH_PATTERN
from anesthesia_sim.core.concentration import Fraction, MacPercent, Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, SimulationStep
from anesthesia_sim.core.supported_ranges import CaseInstant, FreshGasFlow
from anesthesia_sim.layout.run_identity import RunId, SessionToken

# The identities a dashboard gives the first runs it places, in order, which
# render as "Run 1", "Run 2" and "Run 3". A run is named from its identity
# rather than from where it is drawn (`PL-7Z84`).
TEST_SESSION = SessionToken("0" * 32)
RUN_IDS = tuple(RunId(TEST_SESSION, number) for number in (1, 2, 3))
FIRST_RUN, SECOND_RUN = RUN_IDS[:2]


_STEP_S = SimulationStep(0.1)
_PLOT_WIDTH_PX = 900.0


def _advance(controller: SimulationController, seconds: float) -> None:
    for _ in range(round(seconds / _STEP_S)):
        controller.advance(_STEP_S)


def _run(seconds: float, agent_id: str = "sevoflurane") -> SimulationController:
    controller = SimulationController(agent_id=agent_id)
    controller.start()
    _advance(controller, seconds)

    return controller


def _input(controller: SimulationController, *marks_at_s: float, run_index: int = 0) -> RunInput:
    return RunInput(
        run_label(RUN_IDS[run_index]),
        controller,
        controller.snapshot(),
        tuple(
            ControlAdjustment(
                ControlInput.DELIVERED,
                CaseInstant(at_s),
                CaseInstant(at_s),
                2.0,
                4.0,
                CONTROL_INPUT_UNITS[ControlInput.DELIVERED],
                1,
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
    """Each trace matches its row in `docs/MODEL.md` § "The six compartment traces".

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
    controller = _run(600.0)
    frame = assemble_chart_frame(
        [_input(controller)], None, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX
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
        assemble_chart_frame([], None, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX)

    with pytest.raises(ValueError, match="same agent"):
        assemble_chart_frame(
            [_input(_run(10.0)), _input(_run(10.0, "desflurane"))],
            None,
            COMPARTMENT_QUANTITIES,
            plot_width_px=_PLOT_WIDTH_PX,
        )


def test_the_frame_refuses_a_newest_instant_not_built_as_one() -> None:
    """The window is placed from a checked instant, and the frame checks it once (`PL-9DF9`).

    `fit_to_run` and `following_window` only compare the instant. So a
    snapshot carrying a bare number past the supported run length must be
    rejected before either window is formed from it.
    """

    run = _input(_run(10.0))
    stale = replace(run, snapshot=replace(run.snapshot, elapsed_s=1e9))

    with pytest.raises(TypeError, match="newest_instant_s of 1000000000.0 was not built as"):
        assemble_chart_frame([stale], None, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX)


def test_the_window_fits_the_longer_of_two_runs_and_both_draw_into_it() -> None:
    short, long = _run(60.0), _run(500.0)
    frame = assemble_chart_frame(
        [_input(short), _input(long)], None, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX
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

    trunk = _run(120.0)
    trunk.begin_control_adjustment()
    trunk.set_fresh_gas_flow(FreshGasFlow(3.0))
    branch = BranchedCase(trunk).fork_at(CaseInstant(120.0))
    branch.start()
    _advance(branch, 30.0)
    newest_s = branch.snapshot().elapsed_s
    frame = assemble_chart_frame(
        (_input(trunk), _input(branch, run_index=1)),
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
    )

    assert (branch.began_at_s, newest_s) == pytest.approx((120.0, 150.0))
    assert frame.start_s == 0.0
    # The frame uses the narrowest rung that reaches the instant, not a coarser one.
    assert frame.time_base == next(base for base in TIME_BASE_LADDER if base.span_s >= newest_s)
    assert frame.runs[1].times_s[0] == pytest.approx(120.0)
    assert frame.runs[1].times_s[-1] == pytest.approx(newest_s)


def test_a_chosen_width_is_held_exactly_and_follows_the_run() -> None:
    controller = _run(1200.0)
    base = time_base_for_span(900.0)
    frame = assemble_chart_frame(
        [_input(controller)], base, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX
    )

    assert not frame.fitted
    assert frame.time_base == base
    assert frame.stop_s - frame.start_s == pytest.approx(900.0)
    assert frame.start_s < 1200.0 < frame.stop_s
    assert frame.runs[0].times_s[0] >= frame.start_s
    assert frame.columns == chart_columns(900.0)
    assert all(tick % base.tick_interval_s == 0 for tick in frame.tick_times_s)


def test_hidden_traces_are_left_out_of_the_visible_set_but_still_evaluated() -> None:
    controller = _run(60.0)
    frame = assemble_chart_frame(
        [_input(controller)],
        None,
        [RecordedQuantity.FAT, RecordedQuantity.CIRCUIT],
        plot_width_px=_PLOT_WIDTH_PX,
    )

    assert frame.visible == (RecordedQuantity.CIRCUIT, RecordedQuantity.FAT)
    assert set(frame.runs[0].fractions) == set(COMPARTMENT_QUANTITIES)


def test_the_references_are_placed_from_the_running_agent_s_own_values() -> None:
    for agent_id in ("sevoflurane", "isoflurane", "desflurane"):
        controller = _run(10.0, agent_id)
        snapshot = controller.snapshot()
        frame = assemble_chart_frame(
            [_input(controller)], None, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX
        )

        assert frame.mac_percent == snapshot.agent_mac_percent
        assert frame.one_mac_percent == snapshot.agent_mac_percent
        assert frame.axis_top_percent == chart_axis_top_percent(snapshot.agent_mac_percent)
        lower, upper = frame.mac_awake_band_percent
        assert lower < upper < frame.one_mac_percent
        assert frame.mac_ticks[-1] == (pytest.approx(frame.axis_top_percent), "3.0")


def test_control_marks_are_the_most_recent_that_fit_and_the_rest_are_counted() -> None:
    controller = _run(1200.0)
    inside = tuple(float(at_s) for at_s in range(10, 10 + 5 * (MAX_CHART_CONTROL_MARKS + 6), 5))
    frame = assemble_chart_frame(
        [_input(controller, *inside, 5000.0)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
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

    controller = _run(1200.0)
    frame = assemble_chart_frame(
        [_input(controller, 100.0, 600.0)],
        time_base_for_span(900.0),
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
    )
    run = frame.runs[0]

    assert frame.start_s > 100.0
    assert run.control_marks_s == (600.0,)
    assert run.undrawn_control_marks == 0


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

    run = _run(1200.0)
    frame = assemble_chart_frame(
        [_input(run)], None, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX
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
    """Check the guarantee in `docs/MODEL.md` § "What the chart draws" at every rung.

    A frame drawn for a plot `_PLOT_WIDTH_PX` wide divides the axis into at
    least that many intervals. Consecutive drawn instants are therefore never
    more than `span / width` apart, which is one pixel of time, whichever
    width the reader chose. The test checks the drawn instants themselves
    rather than only the column count, because the plot draws its line
    segments between those instants.
    """

    controller = _run(1200.0)

    for base in TIME_BASE_LADDER:
        frame = assemble_chart_frame(
            [_input(controller)], base, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX
        )
        pixel_s = base.span_s / _PLOT_WIDTH_PX
        times = frame.runs[0].times_s

        assert frame.columns - 1 >= _PLOT_WIDTH_PX
        assert frame.plot_width_px == _PLOT_WIDTH_PX
        assert len(times) > 1
        assert max(b - a for a, b in zip(times, times[1:], strict=False)) <= pixel_s + 1e-9


def test_a_frame_refuses_a_width_that_is_not_a_width() -> None:
    """A frame with no valid width would otherwise be drawn silently at the minimum column count."""

    controller = _run(10.0)

    with pytest.raises(ValueError, match="pixels wide"):
        assemble_chart_frame([_input(controller)], None, COMPARTMENT_QUANTITIES, plot_width_px=-1.0)


# ------------------------------------------------------------------ the axes


@pytest.mark.parametrize("mac_percent", [2.0, 1.15, 6.0])
def test_the_percent_axis_is_labelled_at_exactly_the_values_it_rules(mac_percent: float) -> None:
    top = chart_axis_top_percent(MacPercent(mac_percent))
    interval = chart_grid_interval_percent(MacPercent(mac_percent))
    ticks = percent_axis_ticks(top, interval)

    assert ticks[0] == (0.0, "0")
    assert ticks[-1][0] == pytest.approx(top)

    for index, (position, label) in enumerate(ticks):
        assert position == pytest.approx(index * interval)
        assert float(label) == pytest.approx(position)


def test_the_percent_axis_refuses_a_flat_or_unruled_axis() -> None:
    with pytest.raises(ValueError, match="top_percent"):
        percent_axis_ticks(0.0, 1.0)

    with pytest.raises(ValueError, match="interval_percent"):
        percent_axis_ticks(6.0, 0.0)


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


def test_a_run_that_crosses_equilibrium_ends_its_stretch_with_a_terminus() -> None:
    controller = SimulationController()
    controller.set_delivered_concentration_percent(Percent(2.0))
    controller.start()
    _advance(controller, 600.0)
    # Turning the vaporizer off lets the circuit concentration fall below the
    # alveolar concentration. The patient then returns agent to the circuit,
    # which is elimination and not wash-in.
    controller.set_delivered_concentration_percent(Percent(0.0))
    _advance(controller, 300.0)
    frame = assemble_chart_frame(
        [_input(controller)], None, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX
    )
    run = frame.runs[0]

    assert len(run.wash_in) == 1
    stretch = run.wash_in[0]
    assert stretch.ends_above_equilibrium
    assert 1.0 < stretch.ratios[-1] <= WASH_IN_TERMINUS_CEILING
    assert all(ratio <= 1.0 for ratio in stretch.ratios[:-1])
    assert run.undrawn_wash_in_stretches == 0


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
        mac_percent=MacPercent(2.0),
        elapsed_s=times_s[-1],
        times_s=times_s,
        fractions=MappingProxyType(fractions),
        wash_in=(WashInStretch(times_s, tuple(0.71 for _ in times_s), False),),
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
        start_s=0.0,
        stop_s=3600.0,
        tick_times_s=(0.0, 600.0),
        columns=CHART_COLUMN_BUDGET_PER_SERIES,
        plot_width_px=_PLOT_WIDTH_PX,
        mac_percent=MacPercent(2.0),
        axis_top_percent=Percent(6.0),
        grid_interval_percent=1.0,
        percent_ticks=percent_axis_ticks(6.0, 1.0),
        mac_ticks=(),
        one_mac_percent=2.0,
        mac_awake_band_percent=(0.58, 0.78),
        visible=visible,
        undrawn_compartments=0,
        runs=(run,),
    )


def test_the_hover_reads_as_the_specification_shows() -> None:
    """The hover matches the worked example in `docs/MODEL.md` § "The chart's hover readout"."""

    run = _run_frame((1208.0,), alveolar=(0.0143,))

    assert format_trace_hover(run, RecordedQuantity.ALVEOLAR, 0, 1) == (
        "Modelled sevoflurane · 20m8s\nAlveolar (end-tidal-equivalent)\n1.43%   0.71 ×MAC"
    )
    assert format_wash_in_hover(run, run.wash_in[0], 0, 1) == (
        f"Modelled sevoflurane · 20m8s\n{WASH_IN_HOVER_LABEL}\n0.71"
    )


def _input_refusing_a_drawn_column(
    controller: SimulationController, quantity: RecordedQuantity, value: float
) -> RunInput:
    """Return `_input(controller)` with `value` written into `quantity`'s last drawn column.

    This is the only way to get a drawn fraction outside 0 to 1, because no
    supported setting computes one (`core/concentration.py`). A drawn window
    is an evaluation of the closed form. The value is therefore written into
    the window that the controller returns, rather than into any compartment.
    """

    real_drawn_window = controller.drawn_window

    def drawn_window(start_s: float, stop_s: float, columns: int) -> DrawnWindow:
        window = real_drawn_window(start_s, stop_s, columns)
        states = list(window.states)
        values = list(states[-1].values)
        values[COMPARTMENT_STATE_INDEX[quantity]] = value
        states[-1] = replace(states[-1], values=tuple(values))

        return DrawnWindow(window.substance_id, window.times_s, tuple(states))

    controller.drawn_window = drawn_window  # type: ignore[method-assign]

    return _input(controller)


def test_a_drawn_fraction_past_one_atmosphere_is_refused_before_any_frame_exists() -> None:
    """Every value a frame draws is built as a `Fraction` when the frame is assembled.

    This is the fourth limit in `core/concentration.py`. A computed fraction
    that rounds past 1 is rejected, rather than clamped to 100.00% or drawn
    above the axis (`PL-4R3W`). Only a 100% dial can produce such a fraction,
    and no supported setting reaches one. `assemble_chart_frame` rejects it
    before a `ChartFrame` exists. The toolkit is therefore never given a
    frame whose first traces convert and whose last trace fails. Such a frame
    once left four traces redrawn and two still showing the previous frame
    (`PL-7DJK`). The value used here is the one that reproduced that defect,
    in the muscle column.
    """

    run = _input_refusing_a_drawn_column(_run(60.0), RecordedQuantity.MUSCLE, 1.0000000000001568)

    with pytest.raises(
        SimulationConfigurationError,
        match=r"^muscle partial_pressure_fraction of 1\.0000000000001568 is outside 0 to 1",
    ):
        assemble_chart_frame([run], None, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX)


def test_a_refused_drawn_value_names_its_compartment_as_a_step_would() -> None:
    """Each of the six fractions is named for its quantity, as `_write_state_vector` names it.

    The message "fraction of 1.0000000000000002" said which value was
    rejected but not which compartment. That broke the convention that
    `Fraction`'s docstring states (`PL-SPN6`).
    `run_series.COMPARTMENT_FRACTION_NAMES` is the one table from which the
    frame, the snapshot and the MAC multiples take their names (`PL-7DJK`).
    """

    for quantity in COMPARTMENT_QUANTITIES:
        run = _input_refusing_a_drawn_column(_run(60.0), quantity, nextafter(1.0, inf))

        with pytest.raises(
            SimulationConfigurationError,
            match=rf"^{COMPARTMENT_FRACTION_NAMES[quantity]} of 1\.0000000000000002 is outside",
        ):
            assemble_chart_frame([run], None, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX)


def test_a_frame_holds_built_fractions_so_nothing_drawn_from_it_builds_one() -> None:
    """The conversion, the hover and the cursor readouts use the `Fraction`s that the frame built.

    This checks, by type, what `RunFrame.fractions` promises. Every drawn
    value is a `Fraction`, and the axis top is a `Percent`. `percents`,
    `format_trace_hover` and `nearest_trace_point` therefore build nothing.
    None of them can be the first to reject a value after a frame has started
    to draw (`PL-7DJK`).
    """

    frame = assemble_chart_frame(
        [_input(_run(60.0))], None, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX
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

    controller = _run(60.0)
    run = replace(
        _input(controller),
        snapshot=replace(controller.snapshot(), agent_mac_percent=MacPercent(40.0)),
    )

    with pytest.raises(
        SimulationConfigurationError, match=r"^axis_top_percent of 120\.0 is outside 0 to 100"
    ):
        assemble_chart_frame([run], None, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX)


def test_the_hover_names_the_run_only_while_more_than_one_is_drawn() -> None:
    """The hover names the run on line 1, and only while more than one run is drawn.

    This follows `docs/MODEL.md` § "The hover and the run it belongs to". The
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

    first = _run_frame((1208.0,), alveolar=(0.0143,))
    second = replace(_run_frame((1208.0,), alveolar=(0.0145,)), label=run_label(SECOND_RUN))
    frame = replace(_frame(first), runs=(first, second))

    # Both runs' alveolar points are well inside the radius of this pointer.
    nearer_second = nearest_trace_point(frame, 1208.0, 1.45, 4.0, 0.0167, 12.0)
    nearer_first = nearest_trace_point(frame, 1208.0, 1.43, 4.0, 0.0167, 12.0)

    assert nearer_second is not None
    assert nearer_first is not None
    assert abs(1.45 - 1.43) / 0.0167 < 12.0, "the two points must contend for this to test anything"

    # It does not matter which point is marginally nearer. Both pointer
    # positions give one box showing both runs, each named, in drawing order.
    assert nearer_second.readout == nearer_first.readout
    assert tuple(reading.run for reading in nearer_second.readings) == (0, 1)
    assert nearer_second.readout.splitlines() == [
        "Modelled sevoflurane",
        "Alveolar (end-tidal-equivalent)",
        "Run 1 \u00b7 20m8s   1.43%   0.71 \u00d7MAC",
        "Run 2 \u00b7 20m8s   1.45%   0.73 \u00d7MAC",
    ]

    # The values differ, which is why the attribution matters.
    assert nearer_second.readout.splitlines()[2] != nearer_second.readout.splitlines()[3]


def test_a_small_pointer_movement_never_swaps_which_run_the_hover_answers() -> None:
    """`PL-JVHL`: every run inside the radius is reported, so nothing depends on the nearer point.

    The geometry is the one the item measured, reduced to the two fat traces
    that matter. The case is the reference adult on sevoflurane. The trunk is
    held at 1 MAC, and the branch forks at 10 min with the vaporizer turned
    off. The axis spans 60 minutes and is 900 px wide and
    `theme.CHART_HEIGHT` tall, which gives 4.00 s/px and 0.0167 %/px. At
    3492 s, the run still carrying agent shows 0.03%, and the run 48 minutes
    into emergence shows 0.01%. The percent axis is fixed at 3 MAC
    (`CHART_AXIS_TOP_MAC`), so these two points are 1.2 px apart. Both points
    are inside the 12 px radius across the whole hoverable band. The old rule
    kept only the single nearest point overall, and it switched which run was
    reported on 75.4-99.9% of the fat axis.
    """

    reach = dict(seconds_per_pixel=4.0, percent_per_pixel=0.0167, radius_pixels=12.0)
    times_s = tuple(3400.0 + 4.0 * column for column in range(50))
    still_carrying = _run_frame(times_s, fat=tuple(0.00033 for _ in times_s))
    emerging = replace(
        _run_frame(times_s, fat=tuple(0.00009 for _ in times_s)), label=run_label(SECOND_RUN)
    )
    frame = replace(
        _frame(still_carrying, visible=(RecordedQuantity.FAT,)), runs=(still_carrying, emerging)
    )
    on_trunk = still_carrying.percents(RecordedQuantity.FAT)[0]
    on_branch = emerging.percents(RecordedQuantity.FAT)[0]
    midpoint = (on_trunk + on_branch) / 2.0
    # The two traces are less than 1.5 px apart. The item measured the real
    # case at 0.2-1.4 px, which is why a reader cannot see which trace is which.
    assert abs(on_trunk - on_branch) / 0.0167 < 2.0
    # Pixel offsets from the midpoint of the two traces at 3492 s, in steps of
    # two pixels, which is the hand movement the item measured.
    offsets = tuple(range(-12, 13, 2))

    def hover(x_px: int, y_px: int) -> tuple[int, ...]:
        target = nearest_trace_point(frame, 3492.0 + x_px * 4.0, midpoint + y_px * 0.0167, **reach)

        return () if target is None else tuple(reading.run for reading in target.readings)

    def contending(x_px: int, y_px: int) -> bool:
        """Return whether both runs' fat points are inside the radius of this pointer."""

        return all(
            nearest_trace_point(
                replace(frame, runs=(run,)), 3492.0 + x_px * 4.0, midpoint + y_px * 0.0167, **reach
            )
            is not None
            for run in (still_carrying, emerging)
        )

    def marginally_nearer(y_px: int) -> int:
        """Return the run that the retired rule would have reported: the nearer point's run."""

        percent = midpoint + y_px * 0.0167

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
    0.0167 %/px. At 20 minutes on the branched case, the trunk's muscle shows
    0.19% and its fat shows 0.01%. The percent axis is fixed at 3 MAC
    (`CHART_AXIS_TOP_MAC`), so these points are 10.7 px apart, well inside the
    12 px radius. Muscle and fat are the pair that a reader comparing two runs
    picks most often. They are also the pair whose values differ most: by a
    median of 17.1-17.9x across the measured cases, and by twofold or more at
    every switch.
    """

    times_s = tuple(1160.0 + 4.0 * column for column in range(20))
    still_carrying = _run_frame(
        times_s, muscle=tuple(0.0019 for _ in times_s), fat=tuple(0.00012 for _ in times_s)
    )
    emerging = replace(
        _run_frame(
            times_s, muscle=tuple(0.0009 for _ in times_s), fat=tuple(0.00008 for _ in times_s)
        ),
        label=run_label(SECOND_RUN),
    )
    frame = replace(
        _frame(still_carrying, visible=(RecordedQuantity.MUSCLE, RecordedQuantity.FAT)),
        runs=(still_carrying, emerging),
    )

    return frame, dict(seconds_per_pixel=4.0, percent_per_pixel=0.0167, radius_pixels=12.0)


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
    assert 0.0 < (on_muscle - on_fat) / 0.0167 < 12.0
    offsets = tuple(range(-12, 13, 2))
    midpoint = (on_muscle + on_fat) / 2.0

    def hover(x_px: int, y_px: int) -> tuple[tuple[RecordedQuantity, int], ...]:
        target = nearest_trace_point(frame, 1200.0 + x_px * 4.0, midpoint + y_px * 0.0167, **reach)

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
                midpoint + y_px * 0.0167,
                **reach,
            )
            is not None
            for quantity in (RecordedQuantity.MUSCLE, RecordedQuantity.FAT)
            for run in frame.runs
        )

    def marginally_nearer(y_px: int) -> RecordedQuantity:
        """Return the compartment that the retired rule would have reported, the nearer trace's."""

        percent = midpoint + y_px * 0.0167

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
    assert target.readout.splitlines() == [
        "Modelled sevoflurane",
        "Muscle · Run 1 · 20m   0.19%   0.10 ×MAC",
        "Muscle · Run 2 · 20m   0.09%   0.04 ×MAC",
        "Fat · Run 1 · 20m   0.01%   0.01 ×MAC",
        "Fat · Run 2 · 20m   0.01%   <0.01 ×MAC",
    ]
    assert (
        emerging.percents(RecordedQuantity.MUSCLE)[0]
        > still_carrying.percents(RecordedQuantity.FAT)[0] * 5.0
    ), "the contending values must differ severalfold for this to matter"


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
        "Muscle · 20m   0.19%   0.10 ×MAC",
        "Fat · 20m   0.01%   0.01 ×MAC",
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
    60-minute axis's 4.00 s/px and 0.0167 %/px. The pointer is a quarter of a
    column past 20m, which is the instant it names. It is three pixels above
    the flat trace, where the steep trace's nearest point is three columns
    later.
    """

    reach = dict(seconds_per_pixel=4.0, percent_per_pixel=0.0167, radius_pixels=12.0)
    times_s = tuple(1160.0 + 4.0 * column for column in range(20))
    run = _run_frame(
        times_s,
        vessel_rich=tuple(0.0060 for _ in times_s),
        mixed_venous=tuple(0.0060 + (column - 12) * 0.000334 for column in range(20)),
    )
    frame = _frame(run, visible=(RecordedQuantity.MIXED_VENOUS, RecordedQuantity.VESSEL_RICH))
    time_s = 1201.0
    above_flat = run.percents(RecordedQuantity.VESSEL_RICH)[0] + 3 * 0.0167

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
        "Mixed venous · 20m   0.53%   0.27 ×MAC",
        "Vessel-rich · 20m   0.60%   0.30 ×MAC",
    ]

    # No pointer height at which the hover reports anything moves the instant.
    for y_px in range(-12, 13):
        moved = nearest_trace_point(frame, time_s, above_flat + y_px * 0.0167, **reach)

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

    trunk = _run(600.0)
    trunk.begin_control_adjustment()
    trunk.set_delivered_concentration_percent(Percent(3.0))
    _advance(trunk, 600.0)
    controllers = [trunk]

    if compared:
        branch = BranchedCase(trunk).fork_at(CaseInstant(600.0))
        branch.start()
        branch.begin_control_adjustment()
        branch.set_delivered_concentration_percent(Percent(0.0))
        _advance(branch, 600.0)
        controllers.append(branch)

    frame = assemble_chart_frame(
        [_input(controller, run_index=index) for index, controller in enumerate(controllers)],
        time_base_for_span(3600.0),
        (RecordedQuantity.ALVEOLAR, RecordedQuantity.FAT) if compared else COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
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

    reach = dict(seconds_per_pixel=4.0, percent_per_pixel=0.0167, radius_pixels=12.0)
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

    target = nearest_trace_point(frame, 1208.0, 1.43, 4.0, 0.0167, 12.0)
    wash_in = nearest_wash_in_point(frame, 1208.0, 0.71, 4.0, 0.00575, 12.0)

    assert target is not None and tuple(reading.run for reading in target.readings) == (1,)
    assert wash_in is not None and tuple(reading.run for reading in wash_in.readings) == (1,)


def test_the_hover_keeps_the_below_resolution_forms_and_the_readout_row_s_glosses() -> None:
    """As in `docs/MODEL.md`'s measured table, fat at 48.3 s shows as `<0.01%`, never `3.52e-05`."""

    run = _run_frame((48.3,), fat=(3.52e-7,), circuit=(0.0262,), mixed_venous=(0.005,))

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
    run = _run_frame((300.0,), vessel_rich=(0.0123,))
    fraction = Fraction(0.0123)

    assert format_trace_hover(run, RecordedQuantity.VESSEL_RICH, 0, 1).splitlines()[2] == (
        f"{format_percent(fraction)}   {format_mac_multiple(fraction, MacPercent(2.0))}"
    )


def test_the_hover_states_the_instant_at_the_clock_s_own_resolution() -> None:
    assert HOVER_INSTANT_RESOLUTION_S == MAXIMUM_SIMULATION_STEP_S

    run = _run_frame((410.7383,), alveolar=(0.01,))

    assert format_trace_hover(run, RecordedQuantity.ALVEOLAR, 0, 1).splitlines()[0] == (
        "Modelled sevoflurane · 6m50.7s"
    )


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


def test_a_run_out_of_reach_leaves_the_three_line_form_standing() -> None:
    """Reporting every run in reach is not the same as reporting every run drawn.

    The second run's alveolar point is 30 px away, so only one run is
    reported. The readout is the three-line form that `docs/MODEL.md`
    derives. It still names the run, because two runs are drawn (`PL-MN4J`).
    """

    first = _run_frame((1208.0,), alveolar=(0.0143,))
    second = replace(_run_frame((1208.0,), alveolar=(0.0193,)), label=run_label(SECOND_RUN))
    frame = replace(_frame(first), runs=(first, second))

    target = nearest_trace_point(frame, 1208.0, 1.43, 4.0, 0.0167, 12.0)

    assert target is not None
    assert (1.93 - 1.43) / 0.0167 > 12.0, "the second run must be out of reach to test anything"
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

    target = nearest_trace_point(frame, 1208.0, 1.43, 4.0, 0.0167, 12.0)

    assert target is not None
    assert tuple(reading.time_s for reading in target.readings) == (1208.0, 1204.0)
    assert target.readout.splitlines() == [
        "Modelled sevoflurane",
        "Alveolar (end-tidal-equivalent)",
        "Run 1 · 20m8s   1.43%   0.71 ×MAC",
        "Run 2 · 20m4s   1.43%   0.71 ×MAC",
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

    target = nearest_trace_point(frame, 1208.0, 1.44, 4.0, 0.0167, 12.0)

    assert target is not None
    assert tuple(reading.run for reading in target.readings) == (0, 1, 2)
    assert [line.split()[1] for line in target.readout.splitlines()[2:]] == ["1", "2", "3"]


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
        [_input(_run(60.0))], None, COMPARTMENT_QUANTITIES, plot_width_px=_PLOT_WIDTH_PX
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

    first = _run(60.0)
    second = _run(60.0)
    frame = assemble_chart_frame(
        (_input(first), _input(second, run_index=1)),
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
    )

    assert frame.visible == COMPARTMENT_QUANTITIES[:COMPARED_COMPARTMENT_CAP]
    assert frame.undrawn_compartments == len(COMPARTMENT_QUANTITIES) - COMPARED_COMPARTMENT_CAP
    assert tuple(run.label for run in frame.runs) == (run_label(FIRST_RUN), run_label(SECOND_RUN))


def test_a_branch_carries_its_fork_and_a_trunk_carries_none() -> None:
    """The frame marks the one instant at which two compared runs stop being the same run."""

    trunk = _run(60.0)
    trunk.begin_control_adjustment()
    trunk.set_fresh_gas_flow(FreshGasFlow(3.0))
    _advance(trunk, 60.0)
    case = BranchedCase(trunk)
    branch = case.fork_at(CaseInstant(60.0))
    frame = assemble_chart_frame(
        (_input(trunk), _input(branch, run_index=1)),
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
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
    trunk.add_time_bookmark(TimeBookmark(CaseInstant(45.3), "the decision point"))
    trunk.start()
    _advance(trunk, 30.0)
    trunk.begin_control_adjustment()
    trunk.set_fresh_gas_flow(FreshGasFlow(3.0))

    for _ in range(round(60.0 / _STEP_S)):
        trunk.advance(_STEP_S)

        if trunk.snapshot().bookmark_halt is not None:
            break

    fork_s = trunk.snapshot().elapsed_s
    case = BranchedCase(trunk)
    branch = case.fork_here()

    assert branch.run_segments[0].opening.instant_s == 30.0 < fork_s

    frame = assemble_chart_frame(
        (_input(trunk), _input(branch, run_index=1)),
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
    )

    assert frame.runs[0].branch_point_s is None
    assert frame.runs[1].branch_point_s == fork_s


def test_a_fork_outside_the_drawn_window_is_not_marked_at_its_edge() -> None:
    """A mark pinned to the edge would put the fork at a time it did not happen."""

    trunk = _run(60.0)
    trunk.begin_control_adjustment()
    trunk.set_fresh_gas_flow(FreshGasFlow(3.0))
    _advance(trunk, 1800.0)
    case = BranchedCase(trunk)
    branch = case.fork_at(CaseInstant(60.0))
    _advance(branch, 1800.0)
    frame = assemble_chart_frame(
        (_input(trunk), _input(branch, run_index=1)),
        time_base_for_span(900.0),
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
    )

    assert frame.start_s > 60.0
    assert frame.runs[1].branch_point_s is None
