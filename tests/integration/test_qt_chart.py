"""The pyqtgraph chart, drawn headless against a real run.

`app/qt_chart.py` moves pyqtgraph items to match a `ChartFrame`; these
tests read the items back, and the painted pixels, and hold both against
the frame and against the run's own snapshot. They render under the
`offscreen` platform plugin `tests/conftest.py` selects, which is what lets
a session in the web container see a chart change at all (`PL-2QMK`).

What is asserted is chosen for durability rather than pixel-exactness: which
curve carries which compartment, where a reference stands, that the ruling
sits under the data, that a hover says what the frame says. A pixel snapshot
would be brittle across Qt versions and font stacks and would hold nothing
a reader interprets.
"""

from collections import Counter
from collections.abc import Iterator

import pytest
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.chart_frame import (
    COMPARTMENT_TRACES,
    MAX_CHART_CONTROL_MARKS,
    WASH_IN_HOVER_LABEL,
    WASH_IN_TERMINUS_CEILING,
    ChartFrame,
    RunInput,
    assemble_chart_frame,
    format_trace_hover,
)
from anesthesia_sim.app.chart_time_base import time_base_for_span
from anesthesia_sim.app.control_timeline import AdjustmentGrouping, ControlAdjustment
from anesthesia_sim.app.controller import (
    COMPARTMENT_QUANTITIES,
    ControlInput,
    RecordedQuantity,
    SimulationController,
)
from anesthesia_sim.app.formatting import (
    chart_grid_interval_percent,
    format_chart_time_label,
    mac_awake_band_percent,
    mac_axis_ticks,
)
from anesthesia_sim.app.qt_chart import ConcentrationChart, TraceLegend, WashInChart, trace_pen
from anesthesia_sim.app.theme import GRIDLINE, MUTED, PANEL
from anesthesia_sim.app.wash_in import WASH_IN_EQUILIBRIUM_RATIO

_STEP_S = 0.1


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


def _advance(controller: SimulationController, seconds: float) -> None:
    for _ in range(round(seconds / _STEP_S)):
        controller.advance(_STEP_S)


def _run_with_a_dial_change(agent_id: str = "sevoflurane") -> SimulationController:
    """Ten minutes at 1 MAC, then a dial change, then ten more: a mark and a kink."""

    controller = SimulationController(agent_id=agent_id)
    controller.start()
    _advance(controller, 600.0)
    controller.begin_control_adjustment()
    controller.set_delivered_partial_pressure_fraction(
        controller.snapshot().delivered_partial_pressure_fraction * 1.5
    )
    _advance(controller, 600.0)

    return controller


def _frame(
    *controllers: SimulationController, shown=COMPARTMENT_QUANTITIES, span_s=None
) -> ChartFrame:
    grouping = AdjustmentGrouping()
    runs = []

    for controller in controllers:
        snapshot = controller.snapshot()
        runs.append(RunInput(controller, snapshot, grouping.of(snapshot.control_timeline)))

    return assemble_chart_frame(runs, None if span_s is None else time_base_for_span(span_s), shown)


def _shown(application: QApplication, chart: ConcentrationChart | WashInChart, height: int):
    chart.resize(900, height)
    chart.show()
    application.processEvents()

    return chart


def _pixels_along(chart, y_value: float, frame: ChartFrame) -> Counter[str]:
    """The colours painted along one horizontal line of the plot, three rows deep."""

    image = chart.painted()
    left_x, y = chart.plot_pixel(frame.start_s, y_value)
    right_x, _ = chart.plot_pixel(frame.stop_s, y_value)
    counts: Counter[str] = Counter()

    for row in (y - 1, y, y + 1):
        counts.update(image.pixelColor(x, row).name() for x in range(left_x + 2, right_x - 2))

    return counts


# ------------------------------------------------------------- the traces


def test_each_curve_is_drawn_from_its_own_compartment_and_ends_at_the_readout(
    application: QApplication,
) -> None:
    controller = _run_with_a_dial_change()
    frame = _frame(controller)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)
    snapshot = controller.snapshot()
    readouts = {
        RecordedQuantity.CIRCUIT: snapshot.inspired_partial_pressure_fraction,
        RecordedQuantity.ALVEOLAR: snapshot.alveolar_partial_pressure_fraction,
        RecordedQuantity.MIXED_VENOUS: snapshot.mixed_venous_partial_pressure_fraction,
        RecordedQuantity.VESSEL_RICH: snapshot.vessel_rich_partial_pressure_fraction,
        RecordedQuantity.MUSCLE: snapshot.muscle_partial_pressure_fraction,
        RecordedQuantity.FAT: snapshot.fat_partial_pressure_fraction,
    }

    for quantity in COMPARTMENT_QUANTITIES:
        times, percents = chart.drawn_points(0, quantity)

        assert times == pytest.approx(frame.runs[0].times_s)
        assert percents == pytest.approx(frame.runs[0].percents(quantity))
        # The end-to-end binding: the curve's newest point is the number the
        # readout row prints beneath it, for every compartment.
        assert percents[-1] == pytest.approx(readouts[quantity] * 100.0, abs=1e-6)


def test_a_hidden_trace_is_not_drawn_and_is_current_when_shown_again(
    application: QApplication,
) -> None:
    controller = _run_with_a_dial_change()
    chart = _shown(application, ConcentrationChart(), 480)
    legend = TraceLegend()
    legend.set_shown([RecordedQuantity.ALVEOLAR, RecordedQuantity.CIRCUIT])
    chart.draw(_frame(controller, shown=legend.shown))

    assert chart.drawn_points(0, RecordedQuantity.FAT) == ((), ())
    assert chart.drawn_points(0, RecordedQuantity.ALVEOLAR)[0]
    assert chart.readout_at(*_a_drawn_point(chart, RecordedQuantity.FAT, frame=None)) is None

    _advance(controller, 60.0)
    legend.set_shown(COMPARTMENT_QUANTITIES)
    frame = _frame(controller, shown=legend.shown)
    chart.draw(frame)

    assert chart.drawn_points(0, RecordedQuantity.FAT)[1] == pytest.approx(
        frame.runs[0].percents(RecordedQuantity.FAT)
    )


def _a_drawn_point(chart: ConcentrationChart, quantity: RecordedQuantity, *, frame):
    drawn = chart.frame if frame is None else frame
    assert drawn is not None
    run = drawn.runs[0]
    index = len(run.times_s) // 2

    return run.times_s[index], run.percents(quantity)[index]


def test_two_runs_draw_on_one_axis_that_fits_the_longer(application: QApplication) -> None:
    short = SimulationController()
    short.start()
    _advance(short, 60.0)
    long = _run_with_a_dial_change()
    frame = _frame(short, long)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)

    assert chart.drawn_points(0, RecordedQuantity.ALVEOLAR)[0][-1] == pytest.approx(60.0)
    assert chart.drawn_points(1, RecordedQuantity.ALVEOLAR)[0][-1] == pytest.approx(1200.0)
    assert chart.control_mark_times(1) == (pytest.approx(600.0),)
    assert chart.control_mark_times(0) == ()


# ---------------------------------------------------------- the axes, ruled


def test_both_axes_are_labelled_where_they_are_ruled(application: QApplication) -> None:
    controller = _run_with_a_dial_change("isoflurane")
    frame = _frame(controller)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)
    interval = chart_grid_interval_percent(frame.mac_percent)

    left = chart.axis_ticks("left")
    assert left == frame.percent_ticks
    assert [position for position, _ in left] == pytest.approx(
        [index * interval for index in range(len(left))]
    )
    assert chart.axis_ticks("right") == mac_axis_ticks(frame.axis_top_percent, frame.mac_percent)
    assert chart.axis_ticks("bottom") == tuple(
        (tick, format_chart_time_label(tick)) for tick in frame.tick_times_s
    )
    assert all(label[-1] in "smh0" for _, label in chart.axis_ticks("bottom"))


def test_the_wash_in_axis_is_ruled_at_quarters_and_the_window_is_the_chart_s(
    application: QApplication,
) -> None:
    frame = _frame(_run_with_a_dial_change(), span_s=900.0)
    chart = _shown(application, WashInChart(), 300)
    chart.draw(frame)

    assert [label for _, label in chart.axis_ticks("left")] == [
        "0.00",
        "0.25",
        "0.50",
        "0.75",
        "1.00",
    ]
    assert chart.axis_ticks("bottom") == tuple(
        (tick, format_chart_time_label(tick)) for tick in frame.tick_times_s
    )
    assert chart.equilibrium_line() == WASH_IN_EQUILIBRIUM_RATIO


# ------------------------------------------------------------ the references


def test_the_references_stand_at_the_running_agent_s_own_values_and_follow_it(
    application: QApplication,
) -> None:
    chart = _shown(application, ConcentrationChart(), 480)

    for agent_id in ("sevoflurane", "desflurane"):
        controller = _run_with_a_dial_change(agent_id)
        snapshot = controller.snapshot()
        chart.draw(_frame(controller))
        mac_awake = snapshot.agent_mac_awake

        assert chart.one_mac_line() == snapshot.agent_mac_percent
        assert chart.mac_awake_band() == pytest.approx(
            mac_awake_band_percent(
                fraction_of_mac=mac_awake.fraction_of_mac,
                standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
                mac_percent=snapshot.agent_mac_percent,
            )
        )


def test_the_references_and_the_ruling_are_painted_and_the_ruling_sits_underneath(
    application: QApplication,
) -> None:
    """A rendering check: the 1 MAC line is visible on the gridline it stands on.

    pyqtgraph's own grid paints over the plot and erased it (2026-09-14).
    """

    controller = _run_with_a_dial_change()
    frame = _frame(controller)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)
    application.processEvents()

    along_one_mac = _pixels_along(chart, frame.one_mac_percent, frame)
    assert along_one_mac[MUTED.lower()] > 100, along_one_mac

    bare_gridline = frame.percent_ticks[-2][0]
    along_gridline = _pixels_along(chart, bare_gridline, frame)
    assert along_gridline[GRIDLINE.lower()] > 100, along_gridline
    assert set(along_gridline) <= {GRIDLINE.lower(), PANEL.lower()} | _antialiased(along_gridline)


def _antialiased(counts: Counter[str]) -> set[str]:
    """Colours that appear on only a few pixels: a trace crossing the row."""

    return {colour for colour, count in counts.items() if count < 40}


# ----------------------------------------------------------- the control marks


def test_a_recorded_change_is_marked_on_both_plots_at_its_own_time(
    application: QApplication,
) -> None:
    frame = _frame(_run_with_a_dial_change())
    chart = _shown(application, ConcentrationChart(), 480)
    wash_in = _shown(application, WashInChart(), 300)
    chart.draw(frame)
    wash_in.draw(frame)

    assert chart.control_mark_times(0) == (pytest.approx(600.0),)
    assert wash_in.control_mark_times(0) == (pytest.approx(600.0),)


def test_marks_beyond_the_pool_are_the_oldest_left_unmarked(application: QApplication) -> None:
    controller = _run_with_a_dial_change()
    snapshot = controller.snapshot()
    crowded = tuple(
        ControlAdjustment(ControlInput.FRESH_GAS_FLOW, at_s, at_s, 6.0, 2.0, "L/min", 1)
        for at_s in range(10, 10 + 5 * (MAX_CHART_CONTROL_MARKS + 3), 5)
    )
    frame = assemble_chart_frame(
        [RunInput(controller, snapshot, crowded)], None, COMPARTMENT_QUANTITIES
    )
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)

    assert len(chart.control_mark_times(0)) == MAX_CHART_CONTROL_MARKS
    assert chart.control_mark_times(0)[0] == pytest.approx(crowded[3].started_at_s)
    assert frame.runs[0].undrawn_control_marks == 3

    # A quieter frame parks what the crowded one used.
    chart.draw(_frame(controller))
    assert chart.control_mark_times(0) == (pytest.approx(600.0),)


# ------------------------------------------------------------- the wash-in plot


def test_the_wash_in_trace_ends_on_the_equilibrium_line_with_a_terminus_dot(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 600.0)
    controller.set_delivered_partial_pressure_fraction(0.0)
    _advance(controller, 300.0)
    frame = _frame(controller)
    chart = _shown(application, WashInChart(), 300)
    chart.draw(frame)

    (stretch,) = chart.drawn_stretches(0)
    last_time, last_ratio = stretch[-1]
    assert WASH_IN_EQUILIBRIUM_RATIO < last_ratio <= WASH_IN_TERMINUS_CEILING
    assert chart.terminus_points(0) == (pytest.approx((last_time, last_ratio)),)

    # Still climbing: no terminus, and the dot from the frame before is gone.
    chart.draw(_frame(_run_with_a_dial_change()))
    assert chart.terminus_points(0) == ()
    assert len(chart.drawn_stretches(0)) == 1


# ------------------------------------------------------------------ the hover


def test_the_hover_reports_the_drawn_state_through_the_formatters(
    application: QApplication,
) -> None:
    controller = _run_with_a_dial_change()
    frame = _frame(controller)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)
    run = frame.runs[0]
    index = len(run.times_s) // 3
    time_s = run.times_s[index]

    readout = chart.readout_at(time_s, run.percents(RecordedQuantity.VESSEL_RICH)[index])

    assert readout == format_trace_hover(run, RecordedQuantity.VESSEL_RICH, index)
    assert readout is not None
    assert readout.startswith("Modelled sevoflurane · ")
    assert readout.splitlines()[1] == "Vessel-rich"
    assert readout.splitlines()[2].endswith(" ×MAC")
    assert "%" in readout.splitlines()[2]


def test_the_references_answer_no_hover_and_clear_space_answers_none(
    application: QApplication,
) -> None:
    controller = _run_with_a_dial_change()
    frame = _frame(controller)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)
    run = frame.runs[0]
    # Halfway between two drawn columns, on the 1 MAC line: the reference is
    # under the pointer and no drawn point is.
    between = (run.times_s[10] + run.times_s[11]) / 2.0

    assert chart.readout_at(between, frame.one_mac_percent) is None
    assert chart.readout_at(run.times_s[10], frame.axis_top_percent * 0.95) is None


def test_the_hover_answers_while_the_run_is_playing(application: QApplication) -> None:
    controller = _run_with_a_dial_change()
    assert controller.is_running
    frame = _frame(controller)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)

    assert (
        chart.readout_at(*_a_drawn_point(chart, RecordedQuantity.ALVEOLAR, frame=frame)) is not None
    )


def test_the_wash_in_hover_reports_the_ratio_in_its_own_units(application: QApplication) -> None:
    frame = _frame(_run_with_a_dial_change())
    chart = _shown(application, WashInChart(), 300)
    chart.draw(frame)
    stretch = frame.runs[0].wash_in[0]
    index = len(stretch.times_s) // 2

    readout = chart.readout_at(stretch.times_s[index], stretch.ratios[index])

    assert readout is not None
    assert readout.splitlines()[1] == WASH_IN_HOVER_LABEL
    assert readout.splitlines()[2] == f"{stretch.ratios[index]:.2f}"
    assert chart.readout_at(stretch.times_s[index], WASH_IN_EQUILIBRIUM_RATIO) is None


# ------------------------------------------------------------------ the legend


def test_the_legend_swatch_carries_the_trace_s_own_dash_pattern(application: QApplication) -> None:
    """`PL-THXF`: a dashed trace has a dashed swatch, from the one pen."""

    legend = TraceLegend()

    for style in COMPARTMENT_TRACES:
        pen = trace_pen(style)
        swatch = legend.swatch_pen(style.quantity)

        assert swatch.dashPattern() == pen.dashPattern()
        assert swatch.color().name() == style.color.lower()
        assert swatch.widthF() == style.stroke_width

        if style.dash_pattern is None:
            assert pen.dashPattern() == []
        else:
            # Qt states a pattern in pen widths; the table states it in pixels.
            assert pen.dashPattern() == pytest.approx(
                [length / style.stroke_width for length in style.dash_pattern]
            )


def test_the_legend_is_the_visibility_control(application: QApplication) -> None:
    legend = TraceLegend()
    changes: list[tuple[RecordedQuantity, ...]] = []
    legend.visibility_changed.connect(lambda: changes.append(legend.shown))

    assert legend.shown == COMPARTMENT_QUANTITIES

    legend.set_shown([RecordedQuantity.MUSCLE])

    assert legend.shown == (RecordedQuantity.MUSCLE,)
    assert changes and changes[-1] == (RecordedQuantity.MUSCLE,)
