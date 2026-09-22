"""What one frame of the chart claims, held without a toolkit.

`app/chart_frame.py` is where the chart's presentation-correctness claims
live - which compartment a curve carries, where the references stand, which
instants are drawn, what a hover says - and every test here runs with no
display and no plotting library, which is the point of that module.
"""

from dataclasses import replace
from math import hypot
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
    RunFrame,
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
    run_trace_style,
    trace_style,
    wash_in_axis_ticks,
    wash_in_stretches,
)
from anesthesia_sim.app.chart_time_base import TIME_BASE_LADDER, time_base_for_span
from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.control_timeline import ControlAdjustment
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import run_label
from anesthesia_sim.app.formatting import (
    chart_axis_top_percent,
    chart_grid_interval_percent,
    format_mac_multiple,
    format_percent,
)
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.app.theme import COMPARED_RUN_WIDTH_STEP, ONE_MAC_LINE_DASH_PATTERN
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S

_STEP_S = 0.1
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
        run_label(run_index),
        controller,
        controller.snapshot(),
        tuple(
            ControlAdjustment(ControlInput.DELIVERED, at_s, at_s, 0.02, 0.04, "fraction", 1)
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
    """`docs/MODEL.md` § "The six compartment traces": pattern in px, width in px."""

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
    """`PL-NV9W` and `PL-8M05`: the two compartments a clinician would set beside a monitor."""

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
        # agree to floating-point composition, not exactly.
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
        [_input(controller, -50.0, *inside, 5000.0)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
    )
    run = frame.runs[0]

    assert run.control_marks_s == inside[-MAX_CHART_CONTROL_MARKS:]
    assert run.undrawn_control_marks == 6


def test_chart_columns_is_one_per_pixel_boundary_and_never_below_the_floor() -> None:
    """`PL-GS3R`: the count follows the plot, not the span, and a fraction rounds up."""

    for width in (0.0, 1.0, 100.0, 149.0):
        assert chart_columns(width) == CHART_COLUMN_BUDGET_PER_SERIES

    assert chart_columns(150.0) == 151
    assert chart_columns(1000.0) == 1001
    assert chart_columns(1000.4) == 1002

    for width in (-1.0, float("nan"), float("inf")):
        with pytest.raises(ValueError, match="pixels wide"):
            chart_columns(width)


def test_no_chord_is_wider_than_one_pixel_of_time() -> None:
    """The guarantee `docs/MODEL.md` § "What the chart draws" states, at every rung.

    A frame drawn for a plot `_PLOT_WIDTH_PX` wide divides the axis into at
    least that many intervals, so consecutive drawn instants are never more
    than `span / width` apart - one pixel of time - whichever width the
    reader chose. Held on the drawn instants themselves rather than on the
    column count alone, because the instants are what the plot rules between.
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
    """A frame drawn for no stated width would be drawn at the floor, silently."""

    controller = _run(10.0)

    with pytest.raises(ValueError, match="pixels wide"):
        assemble_chart_frame([_input(controller)], None, COMPARTMENT_QUANTITIES, plot_width_px=-1.0)


# ------------------------------------------------------------------ the axes


@pytest.mark.parametrize("mac_percent", [2.0, 1.15, 6.0])
def test_the_percent_axis_is_labelled_at_exactly_the_values_it_rules(mac_percent: float) -> None:
    top = chart_axis_top_percent(mac_percent)
    interval = chart_grid_interval_percent(mac_percent)
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
    controller.set_delivered_partial_pressure_fraction(0.02)
    controller.start()
    _advance(controller, 600.0)
    # Shutting the vaporizer lets the circuit fall below the alveoli: the
    # patient returns agent, which is elimination and not wash-in.
    controller.set_delivered_partial_pressure_fraction(0.0)
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
    fractions = {
        quantity: fractions_by_name.get(quantity.value, tuple(0.0 for _ in times_s))
        for quantity in COMPARTMENT_QUANTITIES
    }

    return RunFrame(
        label=run_label(0),
        branch_point_s=None,
        agent_id="sevoflurane",
        agent_display_name="Sevoflurane",
        mac_percent=2.0,
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
        mac_percent=2.0,
        axis_top_percent=6.0,
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
    """`docs/MODEL.md` § "The chart's hover readout": the worked example, verbatim."""

    run = _run_frame((1208.0,), alveolar=(0.0143,))

    assert format_trace_hover(run, RecordedQuantity.ALVEOLAR, 0, 1) == (
        "Modelled sevoflurane · 20m8s\nAlveolar (end-tidal-equivalent)\n1.43%   0.71 ×MAC"
    )
    assert format_wash_in_hover(run, run.wash_in[0], 0, 1) == (
        f"Modelled sevoflurane · 20m8s\n{WASH_IN_HOVER_LABEL}\n0.71"
    )


def test_the_hover_names_the_run_only_while_more_than_one_is_drawn() -> None:
    """`docs/MODEL.md` § "The hover and the run it belongs to": on line 1, conditional.

    The run goes in the line the specification already calls run context, and
    only while there is a second run to tell it apart from - the same
    condition the width channel carries in `run_trace_style`.
    """

    first = _run_frame((1208.0,), alveolar=(0.0143,))
    second = replace(first, label=run_label(1))

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
    """A readout claiming to compare while naming no run is what this prevents."""

    run = _run_frame((1208.0,), alveolar=(0.0143,))

    for count in (0, -1):
        with pytest.raises(ValueError, match="at least one run"):
            format_trace_hover(run, RecordedQuantity.ALVEOLAR, 0, count)

        with pytest.raises(ValueError, match="at least one run"):
            format_wash_in_hover(run, run.wash_in[0], 0, count)


def test_two_runs_within_the_hover_radius_answer_under_their_own_names() -> None:
    """The regression `PL-MN4J` was filed for, end to end from the pointer.

    Where two runs' points for one compartment are both inside the radius,
    every one of them answers (`PL-JVHL`) and each value is attributed to
    the run it belongs to (`PL-MN4J`). Measured on a branched sevoflurane
    case, the two runs' fat points sit inside the 12 px radius over 100% of
    the shared axis, and 43.8-81.4% of those hovers print different values,
    so an unattributed value is the correct number under the wrong
    management.
    """

    first = _run_frame((1208.0,), alveolar=(0.0143,))
    second = replace(_run_frame((1208.0,), alveolar=(0.0145,)), label=run_label(1))
    frame = replace(_frame(first), runs=(first, second))

    # Both runs' alveolar points are well inside the radius of this pointer.
    nearer_second = nearest_trace_point(frame, 1208.0, 1.45, 4.0, 0.0167, 12.0)
    nearer_first = nearest_trace_point(frame, 1208.0, 1.43, 4.0, 0.0167, 12.0)

    assert nearer_second is not None
    assert nearer_first is not None
    assert abs(1.45 - 1.43) / 0.0167 < 12.0, "the two points must contend for this to test anything"

    # Which point is marginally nearer settles nothing: one box, both runs,
    # each named, in drawing order.
    assert nearer_second.readout == nearer_first.readout
    assert tuple(reading.run for reading in nearer_second.readings) == (0, 1)
    assert nearer_second.readout.splitlines() == [
        "Modelled sevoflurane",
        "Alveolar (end-tidal-equivalent)",
        "Run 1 \u00b7 20m8s   1.43%   0.71 \u00d7MAC",
        "Run 2 \u00b7 20m8s   1.45%   0.73 \u00d7MAC",
    ]

    # The values differ, which is what makes the attribution load-bearing.
    assert nearer_second.readout.splitlines()[2] != nearer_second.readout.splitlines()[3]


def test_a_small_pointer_movement_never_swaps_which_run_the_hover_answers() -> None:
    """`PL-JVHL`: every run inside the radius answers, so nothing turns on the nearer point.

    The geometry is the one the item measured, reduced to the two fat traces
    it turns on. Reference adult on sevoflurane, trunk held at 1 MAC, branch
    forked at 10 min with the vaporizer turned off, a 60-minute axis 900 px
    wide and `theme.CHART_HEIGHT` tall, so 4.00 s/px and 0.0167 %/px: at
    3492 s the run still carrying agent reads 0.03% and the one 48 minutes
    into emergence reads 0.01%, which the percent axis - scaled by the
    alveolar peak - puts 1.2 px apart. Both points are inside the 12 px
    radius across the whole hoverable band, and the rule that kept the
    single globally nearest point flipped which run answered on 75.4-99.9%
    of the fat axis.
    """

    reach = dict(seconds_per_pixel=4.0, percent_per_pixel=0.0167, radius_pixels=12.0)
    times_s = tuple(3400.0 + 4.0 * column for column in range(50))
    still_carrying = _run_frame(times_s, fat=tuple(0.00033 for _ in times_s))
    emerging = replace(_run_frame(times_s, fat=tuple(0.00009 for _ in times_s)), label=run_label(1))
    frame = replace(
        _frame(still_carrying, visible=(RecordedQuantity.FAT,)), runs=(still_carrying, emerging)
    )
    on_trunk = still_carrying.percents(RecordedQuantity.FAT)[0]
    on_branch = emerging.percents(RecordedQuantity.FAT)[0]
    midpoint = (on_trunk + on_branch) / 2.0
    # Under 1.5 px apart; the item measured the real case at 0.2-1.4 px, which
    # is why nothing a reader can see distinguishes these two traces.
    assert abs(on_trunk - on_branch) / 0.0167 < 2.0
    # Pixel offsets from the midpoint of the two traces at 3492 s, two at a
    # time, which is the hand movement the item measured.
    offsets = tuple(range(-12, 13, 2))

    def hover(x_px: int, y_px: int) -> tuple[int, ...]:
        target = nearest_trace_point(frame, 3492.0 + x_px * 4.0, midpoint + y_px * 0.0167, **reach)

        return () if target is None else tuple(reading.run for reading in target.readings)

    def contending(x_px: int, y_px: int) -> bool:
        """Whether both runs' fat points are inside the radius of this pointer."""

        return all(
            nearest_trace_point(
                replace(frame, runs=(run,)), 3492.0 + x_px * 4.0, midpoint + y_px * 0.0167, **reach
            )
            is not None
            for run in (still_carrying, emerging)
        )

    def marginally_nearer(y_px: int) -> int:
        """Which run the retired rule would have answered for: the nearer point's."""

        percent = midpoint + y_px * 0.0167

        return 0 if abs(percent - on_trunk) < abs(percent - on_branch) else 1

    contended = [(x, y) for x in offsets for y in offsets if contending(x, y)]
    assert len(contended) > len(offsets) ** 2 // 2, "the geometry must contend to test anything"
    # The geometry is the ambiguous one: the retired rule does flip across it.
    assert {marginally_nearer(y) for _, y in contended} == {0, 1}

    for x_px, y_px in contended:
        assert hover(x_px, y_px) == (0, 1)

        for neighbour in ((x_px + 2, y_px), (x_px, y_px + 2)):
            if contending(*neighbour):
                assert hover(*neighbour) == hover(x_px, y_px)

    # Both values are reached, and they differ - which is what made the flip
    # consequential rather than cosmetic.
    readout = nearest_trace_point(frame, 3492.0, midpoint, **reach)
    assert readout is not None
    assert readout.readout.splitlines()[2:] == [
        "Run 1 · 58m12s   0.03%   0.02 ×MAC",
        "Run 2 · 58m12s   0.01%   <0.01 ×MAC",
    ]


def _contended_muscle_and_fat() -> tuple[ChartFrame, dict[str, float]]:
    """The geometry `PL-0RZ0` measured, reduced to the pair it turns on.

    Reference adult on sevoflurane, a 60-minute axis 900 px wide and
    `theme.CHART_HEIGHT` tall, so 4.00 s/px and 0.0167 %/px: at 20 minutes on
    the branched case the trunk's muscle reads 0.19% and its fat 0.01%, which
    the percent axis - scaled by the alveolar peak - puts 10.7 px apart, well
    inside the 12 px radius. Muscle and fat are the pair a reader comparing
    two runs picks most often, and the pair whose values differ most: a median
    17.1-17.9x across the measured cases, every flip twofold or more.
    """

    times_s = tuple(1160.0 + 4.0 * column for column in range(20))
    still_carrying = _run_frame(
        times_s, muscle=tuple(0.0019 for _ in times_s), fat=tuple(0.00012 for _ in times_s)
    )
    emerging = replace(
        _run_frame(
            times_s, muscle=tuple(0.0009 for _ in times_s), fat=tuple(0.00008 for _ in times_s)
        ),
        label=run_label(1),
    )
    frame = replace(
        _frame(still_carrying, visible=(RecordedQuantity.MUSCLE, RecordedQuantity.FAT)),
        runs=(still_carrying, emerging),
    )

    return frame, dict(seconds_per_pixel=4.0, percent_per_pixel=0.0167, radius_pixels=12.0)


def test_two_compartments_within_one_hover_radius_answer_under_their_own_names() -> None:
    """`PL-0RZ0`: every compartment inside the radius answers, so nothing turns on the nearer trace.

    The rule `PL-JVHL` settled for the run, one axis over. It left distance to
    pick the compartment, on the reasoning that a reader aims at a curve;
    `PL-0RZ0` measured two or more compartments inside the radius over
    15.2-45.7% of the two-run chart's hoverable area, a 2 px move changing
    which one answered on 6.6-13.6% of contended pointer pairs, and the two
    winning points a median 0.9 px apart - so there was no aim to respect and
    the box did not move when the answer changed.
    """

    frame, reach = _contended_muscle_and_fat()
    still_carrying, emerging = frame.runs
    on_muscle = still_carrying.percents(RecordedQuantity.MUSCLE)[0]
    on_fat = still_carrying.percents(RecordedQuantity.FAT)[0]
    # The contention this tests: the two traces are inside one radius of each
    # other, so no pointer position lies on one and not the other.
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
        """Whether every one of the four traces has a drawn point inside this pointer's radius.

        Asked trace by trace, each on a frame drawing only itself, so that the
        rule under test cannot be what decides the question put to it.
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
        """Which compartment the retired rule would have answered for: the nearer trace's."""

        percent = midpoint + y_px * 0.0167

        return (
            RecordedQuantity.MUSCLE
            if abs(percent - on_muscle) < abs(percent - on_fat)
            else RecordedQuantity.FAT
        )

    contended = [(x, y) for x in offsets for y in offsets if contending(x, y)]
    assert len(contended) > len(offsets) ** 2 // 4, "the geometry must contend to test anything"
    # The geometry is the ambiguous one: the retired rule does flip across it.
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

    # Every value is reached, each under its own compartment and run, and the
    # two compartments differ by the severalfold the item measured.
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
    """`_hover_context`'s rule reaches the compartment lines: one run drawn is not a comparison.

    The single-run chart draws all six compartments and has the same exposure
    - `PL-0RZ0` measured two or more inside the radius over 37.0% of its
    hoverable area - so this form fires there too, where naming the only run
    would imply a comparison that is not on screen.
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
    """The instant the retired rule answered one trace at: its drawn point nearest in pixels.

    The counterfactual the `PL-1K9G` tests are held against, so that a
    geometry which stops exercising the retired rule's failure fails as a
    geometry rather than passing as a fix.
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
    """The drawn instant nearest `time_s` in time, ties to the earlier: what the pointer names."""

    return min(run.times_s, key=lambda drawn_s: (abs(drawn_s - time_s), drawn_s))


def test_every_compartment_of_one_run_answers_at_one_instant() -> None:
    """`PL-1K9G`: the pointer names the instant, and every trace of a run answers at it.

    The retired rule kept each trace's drawn point nearest the pointer in
    pixels, so a steep trace and a flat one inside one radius answered at
    different columns - the pointer's height deciding which - and one box
    labelled two compartments of one run with two instants. Measured on the
    single-run chart, 70.1% of the boxes holding two or more of one run's
    readings mixed instants, up to 72 s apart on the 60-minute axis and 15
    minutes apart on the 12-hour one, and 91.9% of those printed digits the
    same compartments do not print at one shared instant.

    The geometry is that shape reduced to two traces: vessel-rich flat and
    mixed venous rising two pixels a column through it, at the 60-minute
    axis's 4.00 s/px and 0.0167 %/px. The pointer is a quarter of a column
    past 20m, which is the instant it names, and three pixels above the flat
    trace - where the steep one's nearest point is three columns on.
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

    # The geometry is one the retired rule split: its two traces answered
    # twelve seconds apart under this pointer.
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

    # And no height at which anything answers moves it.
    for y_px in range(-12, 13):
        moved = nearest_trace_point(frame, time_s, above_flat + y_px * 0.0167, **reach)

        if moved is not None:
            assert {reading.time_s for reading in moved.readings} == {1200.0}


@pytest.mark.parametrize("compared", [False, True], ids=["one run", "two runs"])
def test_a_vertical_hand_movement_never_moves_the_instant_a_hover_reports(compared: bool) -> None:
    """`PL-1K9G` on real runs: the instant a value is labelled with is the pointer's time alone.

    Under the retired rule a purely vertical 2 px movement moved it on 44.9%
    of such movements on the single-run chart, and moved the printed value on
    35.1% - by up to 0.13 percentage points on the 60-minute axis and 0.39 on
    the 12-hour one, with nothing else in the box moving. Swept here across
    the dial change at ten minutes and the live end at twenty, where the fast
    compartments are steepest, at every other pixel of height and at three
    points between each pair of columns, one of them the exact midpoint: every
    run that answers does so at its own drawn instant nearest the pointer in
    time, whatever the pointer's height.
    """

    trunk = _run(600.0)
    trunk.begin_control_adjustment()
    trunk.set_delivered_partial_pressure_fraction(Fraction(0.03))
    _advance(trunk, 600.0)
    controllers = [trunk]

    if compared:
        branch = BranchedCase(trunk).fork_at(600.0)
        branch.start()
        branch.begin_control_adjustment()
        branch.set_delivered_partial_pressure_fraction(Fraction(0.0))
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

    # The region is one where the retired rule labelled values with an
    # instant the pointer's time does not name.
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
    """The radius still decides whether a trace answers - measured at the instant the pointer names.

    A steep trace passes within the radius of a pointer beside it at an
    instant several columns away, and the retired rule answered with that
    point. Answering from the named instant's point whatever its distance was
    the other way to make the instant a function of the pointer's time, and
    it was measured and refused: where this rule declines, it would have hung
    the dot and the box a median 13.5 px and up to 42.5 px from the pointer on
    the 60-minute axis, and up to 146 px on the 12-hour one - a value the
    reader is nowhere near, reported as the one under the pointer.
    """

    reach = dict(seconds_per_pixel=4.0, percent_per_pixel=0.0167, radius_pixels=12.0)
    times_s = tuple(1160.0 + 4.0 * column for column in range(18))
    # Twenty pixels a column: the near-vertical step a dial change draws.
    run = _run_frame(times_s, circuit=tuple(0.0005 + column * 0.00334 for column in range(18)))
    frame = _frame(run, visible=(RecordedQuantity.CIRCUIT,))
    circuit = run.percents(RecordedQuantity.CIRCUIT)
    time_s = 1201.0

    # Level with the step three columns on: 2.75 px from that point, which the
    # retired rule answered with, and 60 px above the point at 20m.
    assert _retired_nearest_instant(run, RecordedQuantity.CIRCUIT, time_s, circuit[13], reach) == (
        1212.0
    )
    assert nearest_trace_point(frame, time_s, circuit[13], **reach) is None

    # On the trace at the instant the pointer names, it answers there.
    on_trace = nearest_trace_point(frame, time_s, circuit[10], **reach)

    assert on_trace is not None
    assert (on_trace.anchor.time_s, on_trace.anchor.value) == (1200.0, circuit[10])


def test_the_wash_in_hover_answers_at_the_instant_the_pointer_names() -> None:
    """`PL-1K9G` on the wash-in plot, which measured its distance in the same two dimensions.

    One trace per run, so no box there could mix one run's instants - but a
    purely vertical 2 px movement moved the one instant it reports on
    23.9-44.4% of such movements across the measured cases, the printed ratio
    with it on 7.7-20.6%. A run's stretches are one set of drawn instants, so
    the pointer names one of them across the gap between two stretches too.
    """

    reach = dict(seconds_per_pixel=4.0, ratio_per_pixel=0.00575, radius_pixels=12.0)
    # Rising two pixels a column, as early wash-in does on the 60-minute axis.
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

    # In the gap, nearer in time to the late stretch: it answers, at its first point.
    in_gap = nearest_wash_in_point(frame, 92.0, 0.80, **reach)

    assert in_gap is not None
    assert (in_gap.anchor.time_s, in_gap.anchor.value) == (100.0, 0.80)


def test_a_run_that_draws_no_instant_answers_no_hover_and_silences_no_other() -> None:
    """A run with nothing drawn has no instant to name, so it answers nothing; the rest still do.

    `SimulationController.drawn_window` always draws both ends of the range a
    run covers, so no assembled frame holds such a run; it is held here
    because the bisection that names the instant would otherwise read one
    before the first column of an empty run, on both plots.
    """

    drawn = _run_frame((1208.0,), alveolar=(0.0143,))
    empty = replace(drawn, label=run_label(1), times_s=(), wash_in=(WashInStretch((), (), False),))
    frame = replace(_frame(drawn), runs=(empty, drawn))

    target = nearest_trace_point(frame, 1208.0, 1.43, 4.0, 0.0167, 12.0)
    wash_in = nearest_wash_in_point(frame, 1208.0, 0.71, 4.0, 0.00575, 12.0)

    assert target is not None and tuple(reading.run for reading in target.readings) == (1,)
    assert wash_in is not None and tuple(reading.run for reading in wash_in.readings) == (1,)


def test_the_hover_keeps_the_below_resolution_forms_and_the_readout_row_s_glosses() -> None:
    """`docs/MODEL.md`'s measured table: fat at 48.3 s is `<0.01%`, never `3.52e-05`."""

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
        f"{format_percent(fraction)}   {format_mac_multiple(fraction, Percent(2.0))}"
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
    # One second and one hundredth of a percent per pixel: a 12 px reach.
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

    # Between two columns, on the 1 MAC line: no drawn point is near, and a
    # reference never answers.
    assert nearest_trace_point(frame, 150.0, 2.0, **reach) is None
    # Beyond reach in pixels, however close in seconds.
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
    # On the equilibrium line, away from the trace: the reference is silent.
    assert nearest_wash_in_point(frame, 100.0, 1.0, **reach) is None


def test_a_run_out_of_reach_leaves_the_three_line_form_standing() -> None:
    """Answering for every run in reach is not answering for every run drawn.

    The second run's alveolar point is 30 px away, so one run answers and the
    readout is the three-line form `docs/MODEL.md` derives - still naming the
    run, because two are drawn (`PL-MN4J`).
    """

    first = _run_frame((1208.0,), alveolar=(0.0143,))
    second = replace(_run_frame((1208.0,), alveolar=(0.0193,)), label=run_label(1))
    frame = replace(_frame(first), runs=(first, second))

    target = nearest_trace_point(frame, 1208.0, 1.43, 4.0, 0.0167, 12.0)

    assert target is not None
    assert (1.93 - 1.43) / 0.0167 > 12.0, "the second run must be out of reach to test anything"
    assert tuple(reading.run for reading in target.readings) == (0,)
    assert target.readout == format_trace_hover(first, RecordedQuantity.ALVEOLAR, 0, 2)
    assert target.readout.splitlines()[0] == "Modelled sevoflurane · Run 1 · 20m8s"


def test_a_compared_hover_states_each_run_s_own_instant() -> None:
    """Two runs answer at their own drawn points, which need not be the same instant.

    Both runs sit on the shared anchored grid, but each adds the columns its
    own control events fall on, so the points nearest one pointer can be up
    to one grid column apart - 4 s here. One instant above a column of values
    would assert a simultaneity the readings do not have.
    """

    first = _run_frame((1208.0,), alveolar=(0.0143,))
    second = replace(_run_frame((1204.0,), alveolar=(0.0143,)), label=run_label(1))
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
        replace(_run_frame((1208.0,), alveolar=(0.0143 + 0.0001 * index,)), label=run_label(index))
        for index in range(3)
    )
    frame = replace(_frame(runs[0]), runs=runs)

    target = nearest_trace_point(frame, 1208.0, 1.44, 4.0, 0.0167, 12.0)

    assert target is not None
    assert tuple(reading.run for reading in target.readings) == (0, 1, 2)
    assert [line.split()[1] for line in target.readout.splitlines()[2:]] == ["1", "2", "3"]


def test_a_compared_hover_refuses_to_name_one_agent_over_another_run_s_value() -> None:
    """The agent is named once, above the values, so the runs must share it.

    `assemble_chart_frame` already refuses such a frame - one MAC ruler is
    drawn across every run - so this is the second guard rather than the
    first, on the one line that turns a per-run qualifier into a shared one.
    """

    run = _run_frame((1208.0,), alveolar=(0.0143,))
    other = replace(run, agent_display_name="Desflurane", label=run_label(1))

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
        label=run_label(1),
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
    """`PL-HLD5`: compartment on style and colour, run on width, read locally.

    The first is widened rather than the second narrowed because a branch
    reproduces its parent up to the fork, so the two curves coincide there
    and the narrower has to be the one drawn on top - and because nothing is
    then drawn thinner than the single-run chart draws it, which is what
    keeps every trace's contrast against the panel where it was measured.
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
    """A width for a run that is not there would be a width nothing on screen carries."""

    for run_index, run_count in ((1, 1), (-1, 2), (2, 2), (0, 0)):
        with pytest.raises(ValueError, match="runs on the chart"):
            run_trace_style(RecordedQuantity.ALVEOLAR, run_index, run_count)


def test_one_run_draws_every_compartment_the_reader_left_shown() -> None:
    """The cap is what frees the width channel, so it binds only once it is needed."""

    assert compared_compartments(COMPARTMENT_QUANTITIES, 1) == (COMPARTMENT_QUANTITIES, 0)


def test_two_runs_cap_the_drawn_compartments_and_count_what_they_removed() -> None:
    """Two compartments times two runs is four curves, and the rest are counted."""

    drawn, undrawn = compared_compartments(COMPARTMENT_QUANTITIES, 2)

    assert len(drawn) == COMPARED_COMPARTMENT_CAP
    assert undrawn == len(COMPARTMENT_QUANTITIES) - COMPARED_COMPARTMENT_CAP
    # Table order, not the order a reader clicked, so the drawn pair is the
    # same pair whichever route reached the selection.
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
    assert tuple(run.label for run in frame.runs) == (run_label(0), run_label(1))


def test_a_branch_carries_its_fork_and_a_trunk_carries_none() -> None:
    """The one instant two compared runs stop being the same run is marked."""

    trunk = _run(60.0)
    trunk.begin_control_adjustment()
    trunk.set_fresh_gas_flow(3.0)
    _advance(trunk, 60.0)
    case = BranchedCase(trunk)
    branch = case.fork_at(60.0)
    frame = assemble_chart_frame(
        (_input(trunk), _input(branch, run_index=1)),
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
    )

    assert frame.runs[0].branch_point_s is None
    assert frame.runs[1].branch_point_s == pytest.approx(60.0)


def test_a_bookmark_branch_is_marked_at_its_fork_and_not_at_its_definition_s_opening() -> None:
    """The one instant two runs stop being the same run, when it is not a keyframe.

    A bookmark branch's run definition opens at the keyframe *before* the
    fork, so a frame taking the definition's own opening for the branch point
    would draw the line where the trunk was still the only run - the fork at a
    time it did not happen, which is what the assembly's own comment guards
    against. `opened_from.elapsed_s` is the fork whichever door the branch
    came through.
    """

    trunk = SimulationController()
    trunk.add_time_bookmark(TimeBookmark(45.3, "the decision point"))
    trunk.start()
    _advance(trunk, 30.0)
    trunk.begin_control_adjustment()
    trunk.set_fresh_gas_flow(3.0)

    for _ in range(round(60.0 / _STEP_S)):
        trunk.advance(_STEP_S)

        if trunk.snapshot().bookmark_halt is not None:
            break

    fork_s = trunk.snapshot().elapsed_s
    case = BranchedCase(trunk)
    branch = case.fork_at_halt()

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
    trunk.set_fresh_gas_flow(3.0)
    _advance(trunk, 1800.0)
    case = BranchedCase(trunk)
    branch = case.fork_at(60.0)
    _advance(branch, 1800.0)
    frame = assemble_chart_frame(
        (_input(trunk), _input(branch, run_index=1)),
        time_base_for_span(900.0),
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
    )

    assert frame.start_s > 60.0
    assert frame.runs[1].branch_point_s is None
