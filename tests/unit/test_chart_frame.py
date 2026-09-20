"""What one frame of the chart claims, held without a toolkit.

`app/chart_frame.py` is where the chart's presentation-correctness claims
live - which compartment a curve carries, where the references stand, which
instants are drawn, what a hover says - and every test here runs with no
display and no plotting library, which is the point of that module.
"""

from dataclasses import replace
from types import MappingProxyType

import pytest

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


def test_the_hover_answers_the_nearest_drawn_point_within_reach_and_nothing_else() -> None:
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
    assert (on_alveolar.quantity, on_alveolar.anchor.time_s, on_alveolar.anchor.value) == (
        RecordedQuantity.ALVEOLAR,
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
    assert shown is not None and shown.quantity is RecordedQuantity.CIRCUIT

    hidden = nearest_trace_point(_frame(run, (RecordedQuantity.ALVEOLAR,)), 100.0, 2.0, **reach)
    assert hidden is None


def test_the_wash_in_hover_answers_its_own_stretches_in_its_own_units() -> None:
    run = _run_frame((0.0, 100.0, 200.0))
    frame = _frame(run)
    reach = dict(seconds_per_pixel=1.0, ratio_per_pixel=0.002, radius_pixels=12.0)

    target = nearest_wash_in_point(frame, 101.0, 0.705, **reach)
    assert target is not None
    assert target.quantity is RecordedQuantity.WASH_IN_RATIO
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
        format_compared_trace_hover(((run, 0), (other, 0)), RecordedQuantity.ALVEOLAR)

    with pytest.raises(ValueError, match="must be on the same agent"):
        format_compared_wash_in_hover(((run, run.wash_in[0], 0), (other, other.wash_in[0], 0)))


def test_a_compared_hover_is_answered_for_at_least_one_run() -> None:
    with pytest.raises(ValueError, match="at least one run"):
        format_compared_trace_hover((), RecordedQuantity.ALVEOLAR)

    with pytest.raises(ValueError, match="at least one run"):
        format_compared_wash_in_hover(())


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
    assert target.quantity is RecordedQuantity.WASH_IN_RATIO
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
