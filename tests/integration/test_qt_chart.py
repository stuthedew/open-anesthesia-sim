"""Tests of the pyqtgraph chart, drawn headless against a real run.

`app/qt_chart.py` moves pyqtgraph items to match a `ChartFrame`. These tests
read the items back, and the painted pixels, and check both against the frame
and against the run's own snapshot. They render under the `offscreen`
platform plugin that `tests/conftest.py` selects. That plugin is what lets a
session in the web container see a chart change at all (`PL-2QMK`).

The assertions are chosen to be durable rather than exact to the pixel. They
check which curve carries which compartment, where a reference line is drawn,
that the gridlines sit under the data, and that a hover says what the frame
says. A pixel snapshot would break across Qt versions and font stacks, and
would check nothing that a reader interprets.
"""

import gc
import weakref
from collections import Counter
from collections.abc import Iterator
from math import ceil, floor

import numpy as np
import pytest
from PySide6.QtCore import QDeadlineTimer, QEvent, QPoint, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontInfo, QImage, QMouseEvent, QPainter, QPalette, QPen
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QCheckBox, QLabel, QWidget

from anesthesia_sim.app.chart_frame import (
    CHART_COLUMN_BUDGET_PER_SERIES,
    COMPARED_COMPARTMENT_CAP,
    COMPARTMENT_TRACES,
    MAX_CHART_CONTROL_MARKS,
    WASH_IN_HOVER_LABEL,
    WASH_IN_TERMINUS_CEILING,
    ChartFrame,
    PreviewRequest,
    RunInput,
    assemble_chart_frame,
    chart_columns,
    format_compared_trace_hover,
    format_trace_hover,
    trace_style,
)
from anesthesia_sim.app.chart_time_base import time_base_for_span
from anesthesia_sim.app.compartment_selection import (
    INITIAL_COMPARTMENT_SELECTION,
    CompartmentSelection,
)
from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.control_timeline import AdjustmentGrouping, ControlAdjustment
from anesthesia_sim.app.controller import BranchedCase, SettingPreview, SimulationController
from anesthesia_sim.app.dashboard_frame import (
    MAX_DISPLAYED_RUNS,
    PREVIEW_TIME_AXIS_CAPTION_TEMPLATE,
    run_label,
)
from anesthesia_sim.app.formatting import (
    ChartCeiling,
    format_chart_time_label,
    mac_awake_band_percent,
    mac_axis_ticks,
)
from anesthesia_sim.app.qt_chart import (
    CONTROL_MARK_LEGEND_LABEL,
    EQUILIBRIUM_LEGEND_LABEL,
    HOVER_RADIUS_PIXELS,
    WASH_IN_TRACE_LEGEND_LABEL,
    ConcentrationChart,
    TraceLegend,
    WashInChart,
    WashInLegend,
    dashed_pen,
    trace_pen,
)
from anesthesia_sim.app.qt_widgets import FlowLayout
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.app.stylesheets import foreground_stylesheet
from anesthesia_sim.app.theme import (
    CHART_HEIGHT,
    CHART_LEAST_HEIGHT,
    COMPARED_RUN_WIDTH_STEP,
    CONTROL_MARK_COLOR,
    CONTROL_MARK_DASH_PATTERN,
    CONTROL_MARK_STROKE_WIDTH,
    EQUILIBRIUM_LINE_COLOR,
    EQUILIBRIUM_LINE_DASH_PATTERN,
    EQUILIBRIUM_LINE_STROKE_WIDTH,
    GRIDLINE,
    INK,
    MAC_AWAKE_BAND_COLOR,
    MAC_AWAKE_BAND_EDGE_STROKE_WIDTH,
    MAC_AWAKE_BAND_FILL_OPACITY,
    MUTED,
    PANEL,
    WASH_IN_COLOR,
    WASH_IN_STROKE_WIDTH,
)
from anesthesia_sim.app.wash_in import WASH_IN_EQUILIBRIUM_RATIO
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.parameters import load_agent_parameters
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CaseInstant, FreshGasFlow
from anesthesia_sim.layout.run_identity import RunId, SessionToken

# These are the identities that a dashboard gives the first runs it places, in
# order. They render as "Run 1", "Run 2" and "Run 3". A run is named from its
# identity rather than from where it is drawn (`PL-7Z84`).
TEST_SESSION = SessionToken("0" * 32)
RUN_IDS = tuple(RunId(TEST_SESSION, number) for number in (1, 2, 3))
FIRST_RUN, SECOND_RUN = RUN_IDS[:2]


@pytest.fixture(scope="module")
def application() -> Iterator[QApplication]:
    existing = QApplication.instance()

    yield existing if isinstance(existing, QApplication) else QApplication([])


def _advance(controller: SimulationController, seconds: int) -> None:
    for _ in range(seconds // SIMULATION_STEP_S):
        controller.advance()


def _run_with_a_dial_change(
    agent_id: str = "sevoflurane", *, switched_from: str | None = None
) -> SimulationController:
    """Return a run of ten minutes at 1 MAC, a dial change, and ten more, for a mark and a kink.

    With `switched_from`, the controller first runs one minute of that agent
    and is then switched to `agent_id`. The run is then the one the switch
    built, not a fresh one (`PL-JPS2`).
    """

    controller = SimulationController(agent_id=switched_from or agent_id)

    if switched_from is not None:
        controller.start()
        _advance(controller, 60)
        controller.set_agent(agent_id)

    controller.start()
    _advance(controller, 600)
    controller.begin_control_adjustment()
    controller.set_delivered_concentration_percent(
        Percent(controller.snapshot().delivered_concentration_percent * 1.5)
    )
    _advance(controller, 600)

    return controller


_PLOT_WIDTH_PX = 900.0


def _frame(
    *controllers: SimulationController,
    shown=COMPARTMENT_QUANTITIES,
    span_s=None,
    plot_width_px: float = _PLOT_WIDTH_PX,
) -> ChartFrame:
    grouping = AdjustmentGrouping()
    runs = []

    for controller in controllers:
        snapshot = controller.snapshot()
        runs.append(
            RunInput(
                run_label(RUN_IDS[len(runs)]),
                controller,
                snapshot,
                grouping.of(snapshot.control_timeline),
            )
        )

    return assemble_chart_frame(
        runs,
        None if span_s is None else time_base_for_span(span_s),
        shown,
        plot_width_px=plot_width_px,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )


def _shown(application: QApplication, chart: ConcentrationChart | WashInChart, height: int):
    chart.resize(900, height)
    chart.show()
    application.processEvents()

    return chart


def _pixels_along(chart, y_value: float, frame: ChartFrame) -> Counter[str]:
    """Count the colours painted along one horizontal line of the plot, three rows deep."""

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
        # This is the end-to-end link: for every compartment, the curve's newest
        # point is the number that the readout row prints beneath it.
        assert percents[-1] == pytest.approx(readouts[quantity] * 100.0, abs=1e-6)


def test_a_hidden_trace_is_not_drawn_and_is_current_when_shown_again(
    application: QApplication,
) -> None:
    controller = _run_with_a_dial_change()
    chart = _shown(application, ConcentrationChart(), 480)
    legend = TraceLegend()
    legend.show_selection(
        CompartmentSelection((RecordedQuantity.ALVEOLAR, RecordedQuantity.CIRCUIT), 1)
    )
    chart.draw(_frame(controller, shown=legend.shown))

    assert chart.drawn_points(0, RecordedQuantity.FAT) == ((), ())
    assert chart.drawn_points(0, RecordedQuantity.ALVEOLAR)[0]
    assert chart.readout_at(*_a_drawn_point(chart, RecordedQuantity.FAT, frame=None)) is None

    _advance(controller, 60)
    legend.show_selection(INITIAL_COMPARTMENT_SELECTION)
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
    _advance(short, 60)
    long = _run_with_a_dial_change()
    frame = _frame(short, long)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)

    assert chart.drawn_points(0, RecordedQuantity.ALVEOLAR)[0][-1] == pytest.approx(60.0)
    assert chart.drawn_points(1, RecordedQuantity.ALVEOLAR)[0][-1] == pytest.approx(1200.0)
    assert chart.control_mark_times(1) == (pytest.approx(600.0),)
    assert chart.control_mark_times(0) == ()


# ---------------------------------------------------------- the axes, ruled


def test_the_mac_axis_labels_every_gridline_and_the_percent_axis_is_round(
    application: QApplication,
) -> None:
    """Every gridline stands at a MAC label, and the percent axis is labelled in whole percent.

    Isoflurane's MAC at age 40 is 1.17% (Mapleson 1996, PMID 8777094,
    abstract), so its standard top is 3.51%. The gridlines stand at each half
    MAC, worked here by hand, and the percent labels at 0, 1, 2 and 3%, not
    at the half-MAC values 0.585, 1.17 and 1.755 (`PL-BNMZ`).
    """

    controller = _run_with_a_dial_change("isoflurane")
    frame = _frame(controller)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)

    assert chart.horizontal_gridlines() == pytest.approx([index * 0.5 * 1.17 for index in range(7)])
    assert chart.axis_ticks("left") == ((0.0, "0"), (1.0, "1"), (2.0, "2"), (3.0, "3"))
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


@pytest.mark.parametrize(
    ("make", "height", "names"),
    [
        (ConcentrationChart, 480, ("left", "right", "bottom")),
        (WashInChart, 300, ("left", "bottom")),
    ],
)
def test_every_tick_label_is_painted_whole_inside_the_chart(
    application: QApplication, make, height: int, names: tuple[str, ...]
) -> None:
    """The top label of each axis sits on the plot's top edge, and was cut in half (`PL-571L`).

    The lower half of a "6" can read as a "0", so a user could misjudge the scale.
    """

    frame = _frame(_run_with_a_dial_change(), span_s=900.0)
    chart = _shown(application, make(), height)
    chart.draw(frame)
    application.processEvents()
    bounds = QRectF(chart.rect())

    for name in names:
        labels = chart.tick_label_rects(name)
        assert labels, f"the {name} axis painted no label"
        cut = [text for text, rect in labels if not bounds.contains(rect)]
        assert cut == [], f"the {name} axis's labels {cut} reach outside the chart"


# ------------------------------------------------------------ the references


def test_the_references_stand_at_the_running_agent_s_own_values_and_follow_it(
    application: QApplication,
) -> None:
    """Each run is switched into its agent, and the chart draws that agent's own references.

    The first two assertions check the chart against the snapshot it was drawn
    from. They cannot detect a band that a switch left at the previous agent's
    values, because the snapshot stores the same wrong values. So the last two
    take the expected values from the agent's own data file and work out the
    band's edges here (`PL-JPS2`).
    """

    chart = _shown(application, ConcentrationChart(), 480)

    for agent_id, switched_from in (
        ("sevoflurane", "desflurane"),
        ("desflurane", "sevoflurane"),
        ("isoflurane", "sevoflurane"),
    ):
        controller = _run_with_a_dial_change(agent_id, switched_from=switched_from)
        snapshot = controller.snapshot()
        chart.draw(_frame(controller))
        mac_awake = snapshot.agent_mac_awake
        own = load_agent_parameters(agent_id)
        fraction = own.mac_awake.fraction_of_mac
        spread = own.mac_awake.standard_deviation_fraction_of_mac

        assert chart.one_mac_line() == snapshot.agent_mac_percent
        assert chart.mac_awake_band() == pytest.approx(
            mac_awake_band_percent(
                fraction_of_mac=mac_awake.fraction_of_mac,
                standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
                mac_percent=snapshot.agent_mac_percent,
            )
        )
        assert chart.one_mac_line() == own.mac_at_age_40_percent
        assert chart.mac_awake_band() == pytest.approx(
            (
                (fraction - spread) * own.mac_at_age_40_percent,
                (fraction + spread) * own.mac_at_age_40_percent,
            )
        )


def test_the_references_and_the_ruling_are_painted_and_the_ruling_sits_underneath(
    application: QApplication,
) -> None:
    """This rendering check shows that the 1 MAC line is visible on the gridline it lies on.

    pyqtgraph's own grid paints over the plot, and it erased the line (2026-09-14).
    """

    controller = _run_with_a_dial_change()
    frame = _frame(controller)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)
    application.processEvents()

    along_one_mac = _pixels_along(chart, frame.one_mac_percent, frame)
    assert along_one_mac[MUTED.lower()] > 100, along_one_mac

    bare_gridline = frame.mac_ticks[-2][0]
    along_gridline = _pixels_along(chart, bare_gridline, frame)
    assert along_gridline[GRIDLINE.lower()] > 100, along_gridline
    assert set(along_gridline) <= {GRIDLINE.lower(), PANEL.lower()} | _antialiased(along_gridline)


def _antialiased(counts: Counter[str]) -> set[str]:
    """Return the colours that appear on only a few pixels, such as a trace crossing the row."""

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


def test_the_plot_reports_the_width_a_frame_is_drawn_for(application: QApplication) -> None:
    """`PL-GS3R`: the width the chart reports is the width its time axis actually spans.

    So a frame assembled for that width divides the axis into at least that
    many intervals. The twelve-hour time base is then drawn with a chord of
    one pixel, rather than the 290 s chord that a fixed budget of 150 columns
    gave.
    """

    controller = _run_with_a_dial_change()
    chart = _shown(application, ConcentrationChart(), 480)
    width = chart.plot_width_px()
    frame = _frame(controller, span_s=43_200.0, plot_width_px=width)
    chart.draw(frame)
    left, _ = chart.plot_pixel(frame.start_s, 0.0)
    right, _ = chart.plot_pixel(frame.stop_s, 0.0)

    assert 0.0 < width < 900.0
    assert frame.columns == chart_columns(width) > CHART_COLUMN_BUDGET_PER_SERIES
    assert right - left == pytest.approx(width, abs=2.0)
    assert (frame.stop_s - frame.start_s) / (frame.columns - 1) <= 43_200.0 / width


def test_marks_beyond_the_pool_are_the_oldest_left_unmarked(application: QApplication) -> None:
    controller = _run_with_a_dial_change()
    snapshot = controller.snapshot()
    crowded = tuple(
        ControlAdjustment(
            ControlInput.FRESH_GAS_FLOW, CaseInstant(at_s), CaseInstant(at_s), 6.0, 2.0, 1
        )
        for at_s in range(10, 10 + 5 * (MAX_CHART_CONTROL_MARKS + 3), 5)
    )
    frame = assemble_chart_frame(
        [RunInput(run_label(FIRST_RUN), controller, snapshot, crowded)],
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)

    assert len(chart.control_mark_times(0)) == MAX_CHART_CONTROL_MARKS
    assert chart.control_mark_times(0)[0] == pytest.approx(crowded[3].started_at_s)
    assert frame.runs[0].undrawn_control_marks == 3

    # A quieter frame hides the pooled marks that the crowded frame used.
    chart.draw(_frame(controller))
    assert chart.control_mark_times(0) == (pytest.approx(600.0),)


# ------------------------------------------------------------- the wash-in plot


def test_the_wash_in_trace_ends_on_the_equilibrium_line_with_a_terminus_dot(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 600)
    controller.set_delivered_concentration_percent(Percent(0.0))
    _advance(controller, 300)
    frame = _frame(controller)
    chart = _shown(application, WashInChart(), 300)
    chart.draw(frame)

    (stretch,) = chart.drawn_stretches(0)
    last_time, last_ratio = stretch[-1]
    assert WASH_IN_EQUILIBRIUM_RATIO < last_ratio <= WASH_IN_TERMINUS_CEILING
    assert chart.terminus_points(0) == (pytest.approx((last_time, last_ratio)),)

    # A run that is still climbing has no terminus, and the dot from the
    # previous frame is gone.
    chart.draw(_frame(_run_with_a_dial_change()))
    assert chart.terminus_points(0) == ()
    assert len(chart.drawn_stretches(0)) == 1


def test_one_second_after_ventilation_is_restored_the_ratio_is_drawn_as_a_dot(
    application: QApplication,
) -> None:
    """The first state reached with ventilation running again is drawn, though it is one point.

    The stretch that starts again after an apnoea has one point for one
    second. The caption beside the plot reads that point, and a line needs
    two points. So the point is drawn as a dot, and the plot and the caption
    agree (`PL-49D5`, domain review). The expected ratio is formed by the test
    from the run's two fractions.
    """

    controller = SimulationController()
    controller.set_delivered_concentration_percent(Percent(4.0))
    controller.start()
    _advance(controller, 600)
    ventilation = controller.snapshot().alveolar_ventilation_l_min
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))
    _advance(controller, 300)
    controller.set_alveolar_ventilation(ventilation)
    _advance(controller, 1)
    snapshot = controller.snapshot()
    ratio = (
        snapshot.alveolar_partial_pressure_fraction / snapshot.inspired_partial_pressure_fraction
    )
    chart = _shown(application, WashInChart(), 300)

    chart.draw(_frame(controller))

    *_, restarted = chart.drawn_stretches(0)
    assert restarted == (pytest.approx((901.0, ratio)),)
    assert chart.terminus_points(0)[-1] == pytest.approx((901.0, ratio))


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

    assert readout == format_trace_hover(run, RecordedQuantity.VESSEL_RICH, index, len(frame.runs))
    assert readout is not None
    assert readout.startswith("Modelled sevoflurane · ")
    assert readout.splitlines()[1] == "Vessel-rich group"
    assert readout.splitlines()[2].endswith(" ×MAC")
    assert "%" in readout.splitlines()[2]


def _fat_lines(readout: str) -> list[str]:
    """Return the fat values that a hover box reports, normalised across the readout's two forms.

    When every reading is of one compartment, the box names that compartment
    once, as a heading. When the readings span compartments, each value line
    starts with its own compartment. Both forms say the same thing about fat.
    This function lets a test assert that a hand movement left the fat values
    unchanged while the box gained a line for a compartment that came into
    reach.
    """

    lines = readout.splitlines()
    marker = "Fat \u00b7 "

    if lines[1] == "Fat":
        return lines[2:]

    return [line.removeprefix(marker) for line in lines[1:] if line.startswith(marker)]


def test_the_hover_answers_for_every_run_in_reach_on_a_real_branched_case(
    application: QApplication,
) -> None:
    """End-to-end test of `PL-JVHL`, from a branched run to the rendered readout.

    This is the case that the rule was decided from. A trunk stays at its
    dialled setting, and a branch forks at 10 min with the vaporizer turned
    off. The percent axis, fixed at 3 MAC (`CHART_AXIS_TOP_MAC`), compresses
    the two runs' fat traces to within a pixel or two of each other. A pointer
    on either run's fat point gets a readout for both runs, each value under
    its own run's name. A pointer two pixels lower gets the identical readout.
    A pointer two pixels higher gets the same fat values, plus a line for a
    compartment that has come within reach.
    """

    trunk = _run_with_a_dial_change()
    case = BranchedCase(trunk)
    branch = case.fork_at(CaseInstant(600))
    branch.start()
    branch.begin_control_adjustment()
    branch.set_delivered_concentration_percent(Percent(0.0))
    _advance(branch, 600)

    shown = (RecordedQuantity.ALVEOLAR, RecordedQuantity.FAT)
    frame = _frame(*case.runs, shown=shown)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)
    assert frame.visible == shown, "the cap must leave fat drawn for this to test anything"

    first, second = frame.runs
    # Take each run's own last drawn column. They are not the same column,
    # because a branch opens at its fork and draws its own control events. But
    # both runs have reached the same instant, and that is where they are
    # compared.
    time_s = first.times_s[-1]
    assert second.times_s[-1] == time_s
    on_trunk = first.percents(RecordedQuantity.FAT)[-1]
    on_branch = second.percents(RecordedQuantity.FAT)[-1]
    _, trunk_row = chart.plot_pixel(time_s, on_trunk)
    _, branch_row = chart.plot_pixel(time_s, on_branch)
    _, floor_row = chart.plot_pixel(time_s, 0.0)
    _, ceiling_row = chart.plot_pixel(time_s, frame.axis_top_percent)
    percent_per_pixel = frame.axis_top_percent / abs(floor_row - ceiling_row)
    # The two stored concentrations differ, but lie inside one hover radius of
    # each other. Here they are inside a single pixel. That is the contention
    # the item measured, and the reason the retired rule was settled by
    # arithmetic that no reader could see.
    assert on_trunk != on_branch
    assert abs(trunk_row - branch_row) < HOVER_RADIUS_PIXELS

    readout = chart.readout_at(time_s, on_trunk)

    assert readout is not None
    assert readout == chart.readout_at(time_s, on_branch)
    assert readout == format_compared_trace_hover(
        (
            (first, RecordedQuantity.FAT, len(first.times_s) - 1),
            (second, RecordedQuantity.FAT, len(second.times_s) - 1),
        ),
        len(frame.runs),
    )
    lines = readout.splitlines()
    assert lines[:2] == ["Modelled sevoflurane", "Fat"]
    assert [line.split("\u00b7")[0].strip() for line in lines[2:]] == [first.label, second.label]
    assert lines[2] != lines[3], "the two runs must read differently for this to matter"

    # Two pixels of hand movement used to swap the readout. Moving down the
    # axis changes nothing at all.
    assert chart.readout_at(time_s, on_trunk - 2.0 * percent_per_pixel) == readout

    # Moving up the axis, the box gains a line. `PL-0RZ0` made the readout
    # include every compartment within reach. By this instant the branch's
    # vaporizer has been off for ten minutes, so its alveolar trace has washed
    # down to within the hover radius of fat. That is the compression that
    # `PL-QYBW` names, now displayed rather than resolved by arithmetic the
    # reader cannot see. What the box says about fat is unchanged, which is the
    # property that `PL-JVHL` added this test for.
    above = chart.readout_at(time_s, on_trunk + 2.0 * percent_per_pixel)

    assert above is not None
    assert _fat_lines(above) == lines[2:]
    assert above == format_compared_trace_hover(
        (
            (second, RecordedQuantity.ALVEOLAR, len(second.times_s) - 1),
            (first, RecordedQuantity.FAT, len(first.times_s) - 1),
            (second, RecordedQuantity.FAT, len(second.times_s) - 1),
        ),
        len(frame.runs),
    )


def test_the_references_answer_no_hover_and_clear_space_answers_none(
    application: QApplication,
) -> None:
    controller = _run_with_a_dial_change()
    frame = _frame(controller)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)
    run = frame.runs[0]
    # Halfway between two drawn columns, on the 1 MAC line, the reference line
    # is under the pointer and no drawn point is.
    between = (run.times_s[10] + run.times_s[11]) / 2.0

    assert chart.readout_at(between, frame.one_mac_percent) is None
    assert chart.readout_at(run.times_s[10], frame.axis_top_percent * 0.95) is None
    # The MAC-awake band, at its centre, and the dial change's mark, high above
    # every trace, answer no hover either.
    band_centre = sum(frame.mac_awake_band_percent) / 2.0
    (mark_s,) = run.control_marks_s
    assert chart.readout_at(between, band_centre) is None
    assert chart.readout_at(mark_s, frame.axis_top_percent * 0.95) is None


def test_the_hover_answers_while_the_run_is_playing(application: QApplication) -> None:
    controller = _run_with_a_dial_change()
    assert controller.is_running
    frame = _frame(controller)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)

    assert (
        chart.readout_at(*_a_drawn_point(chart, RecordedQuantity.ALVEOLAR, frame=frame)) is not None
    )


# The longest that `_wait_for_hover` waits for the hover to respond. It is
# Qt's own default for `QTRY_COMPARE`, the idiom that function copies. The
# wait ends as soon as the hover matches, so a fast run pays none of it. A
# limit of 1000 ms failed under a load average of about 30 on four cores
# (`PL-FPLQ`).
_HOVER_WAIT_MS = 5000

# How long the hide test watches for a hover to come back after the pointer
# leaves. It is sixty times the hover's own cooldown of 1/60 s, which is the
# longest the hover holds a pointer position before responding to it. Unlike
# `_HOVER_WAIT_MS`, this hold always runs to its end, so raising it would
# lengthen that test.
_HOVER_HOLD_MS = 1000


def _move_pointer(chart: ConcentrationChart | WashInChart, pixel: QPoint) -> None:
    """Move the pointer onto one pixel of the chart, as the platform delivers a move.

    The move is sent to the widget under that pixel rather than through
    `QTest.mouseMove`, which moves the platform cursor. The offscreen platform
    gives that cursor move to a window it finds at the screen position, and a
    chart that an earlier test left shown may be there first.
    """

    under = chart.childAt(pixel)
    local = QPointF(under.mapFrom(chart, pixel))
    move = QMouseEvent(
        QEvent.Type.MouseMove,
        local,
        under.mapToGlobal(local),
        Qt.MouseButton.NoButton,
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
    )
    QApplication.sendEvent(under, move)


def _wait_for_hover(chart: ConcentrationChart | WashInChart, text: str | None) -> None:
    """Run the event loop until the hover says `text` or `_HOVER_WAIT_MS` has passed.

    It waits the way `QTRY_COMPARE` does. A move inside the hover's cooldown
    is handled when the cooldown ends, from a timer rather than inside the
    move, and the caller asserts what the hover then says. No `draw` follows,
    which is how a paused run behaves.
    """

    deadline = QDeadlineTimer(_HOVER_WAIT_MS)

    while chart.hover_text() != text and not deadline.hasExpired():
        QTest.qWait(10)


def test_the_hover_answers_the_point_under_the_pointer(application: QApplication) -> None:
    """`PL-TCR5`: with the run paused, a real pointer move shows the readout at the pointer.

    `readout_at` calls the lookup directly, so it could not detect either way
    this went wrong. First, a second slot on the scene's signal responded
    before the proxy had stored the position. So the first move showed
    nothing, and each later move showed the point under the move before it.
    With the run paused, no `draw` followed to correct it. Second,
    pyqtgraph's scene drops a move that comes less than 10 ms after the last
    move it passed on, so a fast pointer's last move got no response. Reading
    every move instead, through `pg.SignalProxy`, starved the hover. That
    proxy restarts its timer on every move, so a pointer that kept moving got
    no response until it stopped.
    """

    controller = _run_with_a_dial_change()
    controller.pause()
    assert not controller.is_running
    frame = _frame(controller)
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)
    # Labelling the axes can widen one and move the plot, so the layout is
    # settled before a pixel is read off it.
    application.processEvents()
    run = frame.runs[0]
    # At all three instants, the circuit trace is more than 30 px away from the
    # other five traces, so each readout shows that point alone. The instants
    # differ, so the readouts differ too.
    count = len(run.times_s)

    def pixel(index: int) -> QPoint:
        return QPoint(
            *chart.plot_pixel(run.times_s[index], run.percents(RecordedQuantity.CIRCUIT)[index])
        )

    earlier, third, later = count // 4, 3 * count // 5, 3 * count // 4

    def answer(index: int) -> str:
        return format_trace_hover(run, RecordedQuantity.CIRCUIT, index, 1)

    def answers_under(index: int) -> set[str]:
        """Return the readout of each point within a pixel of `index`'s column.

        Columns are rounded down to whole seconds, so neighbouring points can
        be a pixel or less apart, and a pointer cannot tell them apart. Which
        of them the hover names then depends on where the platform's fonts put
        the plot's left edge.
        """

        column = pixel(index).x()

        return {answer(j) for j in range(count) if abs(pixel(j).x() - column) <= 1}

    def wait_for_any(texts: set[str]) -> None:
        deadline = QDeadlineTimer(_HOVER_WAIT_MS)

        while chart.hover_text() not in texts and not deadline.hasExpired():
            QTest.qWait(10)

    assert not answers_under(earlier) & answers_under(later)
    assert not answers_under(earlier) & answers_under(third)

    for index in (earlier, later):
        _move_pointer(chart, pixel(index))
        wait_for_any(answers_under(index))

        assert chart.hover_text() in answers_under(index)

    # Send two moves with nothing between them, as a fast pointer's last two
    # moves often are. The hover shows the point where the pointer stopped.
    _move_pointer(chart, pixel(earlier))
    _move_pointer(chart, pixel(third))
    wait_for_any(answers_under(third))

    assert chart.hover_text() in answers_under(third)

    # Off the plot, over the axis, the box disappears rather than keeping the
    # last point's readout.
    _move_pointer(chart, QPoint(1, 1))
    _wait_for_hover(chart, None)

    assert chart.hover_text() is None

    # A pointer that keeps moving gets readouts while it moves, not only once
    # it stops: about one readout per cooldown. The moves are sent back to
    # back, with the event loop run between them. The sweep stops at the
    # third readout, or after `_HOVER_WAIT_MS`. A fixed sweep of 200 ms would
    # need three timer deliveries inside it, and under load a single delivery
    # has taken more than 1000 ms (`PL-FPLQ`). A hover that answered only
    # once the pointer stopped would answer none of these moves while they
    # arrive faster than its cooldown, however long the sweep ran.
    answered: set[str] = set()
    sweep = QDeadlineTimer(_HOVER_WAIT_MS)
    index = earlier

    while len(answered) < 3 and not sweep.hasExpired():
        _move_pointer(chart, pixel(index))
        application.processEvents()
        shown = chart.hover_text()

        if shown is not None:
            answered.add(shown)

        index = earlier if index == later else index + 1

    assert len(answered) >= 3, f"a moving pointer was answered {len(answered)} times"

    # The wash-in plot builds its hover on the same mechanism.
    wash_in = _shown(application, WashInChart(), 300)
    wash_in.draw(frame)
    application.processEvents()
    stretch = run.wash_in[0]
    index = len(stretch.times_s) // 2
    time_s, ratio = stretch.times_s[index], stretch.ratios[index]
    under_pointer = wash_in.readout_at(time_s, ratio)
    assert under_pointer is not None

    _move_pointer(wash_in, QPoint(*wash_in.plot_pixel(time_s, ratio)))
    _wait_for_hover(wash_in, under_pointer)

    assert wash_in.hover_text() == under_pointer


#: How far the hover box may cross the plot's edge, in pixels. The box and the
#: plot are mapped in floating point, and a box placed on an edge measures as
#: outside it by less than 0.05 px, which `test_qt_rendering.py` measured
#: (`PL-J0F7`).
_BOX_EDGE_TOLERANCE_PX = 0.5


#: The width of a narrow chart, in pixels. The concentration View is never
#: narrower than 420 px, and a chart of this width leaves a plot about 360 px
#: wide, on which the longest time-axis title takes two lines.
_NARROW_CHART_WIDTH_PX = 420

#: A desktop font larger than the container's 12 px. Apple's Human Interface
#: Guidelines give 13 pt as the default size of macOS text, in the macOS text
#: styles table of
#: https://developer.apple.com/design/human-interface-guidelines/typography
#: (read 2026-11-23). How Qt maps those points to its pixels on a Mac has no
#: source that this session could read, so 13 px stands in for that font.
_LARGER_FONT_PX = 13


def _set_font(application: QApplication, family: str | None, pixel_size: int | None) -> None:
    """Set the application's font family, or its size in pixels, or both."""

    font = QFont(application.font())

    if family is not None:
        font.setFamily(family)

    if pixel_size is not None:
        font.setPixelSize(pixel_size)

    application.setFont(font)

    # Qt substitutes another family without an error when the one asked for
    # is missing, and the case would then measure a font it does not name.
    if family is not None:
        assert QFontInfo(application.font()).family() == family


def _widened(rect: QRectF) -> QRectF:
    """Return a rectangle grown on every side by `_BOX_EDGE_TOLERANCE_PX`."""

    tolerance = _BOX_EDGE_TOLERANCE_PX

    return rect.adjusted(-tolerance, -tolerance, tolerance, tolerance)


def _hover_on_the_corner(chart: ConcentrationChart) -> QRectF:
    """Hover one pixel in from the plot's lower-left corner and return the box it shows.

    There the pointer is over the plot rather than on its axes, and at the
    start of a run every trace is within reach, so the box is the tallest
    one the plot shows.
    """

    x_px, y_px = chart.plot_pixel(0.0, 0.0)
    _move_pointer(chart, QPoint(x_px + 1, y_px - 1))
    deadline = QDeadlineTimer(_HOVER_WAIT_MS)
    while chart.hover_text() is None and not deadline.hasExpired():
        QTest.qWait(10)
    readout = chart.hover_text()
    assert readout is not None, "no hover answered at the plot's corner"
    assert len(readout.splitlines()) == 1 + len(COMPARTMENT_TRACES), readout
    assert 1 + len(COMPARTMENT_TRACES) > 1 + MAX_DISPLAYED_RUNS * COMPARED_COMPARTMENT_CAP
    box = chart.hover_box()
    assert box is not None

    return box


#: The least share of an edge of the hover box that must be painted in its
#: border for the edge to count as drawn. Measured on 2026-11-23, an edge that
#: the plot's edge cut off was 0% to 16% drawn, and an edge drawn whole was
#: 100% drawn in every case of the test below. The share leaves room for a
#: trace or a tick drawn across the edge.
_DRAWN_EDGE_SHARE = 0.9


def _edge_drawn_share(image: QImage, box: QRectF, edge_y: float) -> float:
    """Return the share of one horizontal edge of the box that is painted darker than the panel.

    The border is drawn in `MUTED` with antialiasing, so where an edge falls
    between two rows of pixels it shows in both, lighter than `MUTED`. So
    each column counts as drawn where either of the two rows nearest the
    edge is darker than the panel the box is filled with.
    """

    panel = QColor(PANEL).lightness()
    rows = {floor(edge_y - 0.5), floor(edge_y)}
    columns = range(ceil(box.left()) + 2, floor(box.right()) - 2)
    drawn = sum(
        1
        for x in columns
        if any(image.pixelColor(x, y).lightness() < panel - _BORDER_LIGHTNESS_MARGIN for y in rows)
    )

    return drawn / len(columns)


#: How much darker than the panel a pixel must be to count as border, in
#: levels of lightness out of 255. Measured on 2026-11-23, the darker of the
#: two rows nearest a drawn edge was 70 to 129 levels darker than the panel,
#: and a cut-off edge showed the panel itself, 0 levels darker.
_BORDER_LIGHTNESS_MARGIN = 20


@pytest.mark.parametrize(
    ("family", "pixel_size"),
    [(None, None), ("DejaVu Sans", None), (None, _LARGER_FONT_PX)],
    ids=["platform font", "CI font", "13 px font"],
)
@pytest.mark.parametrize(
    "width_px", [int(_PLOT_WIDTH_PX), _NARROW_CHART_WIDTH_PX], ids=["wide", "narrow"]
)
def test_the_tallest_hover_box_is_drawn_whole_at_the_least_height(
    application: QApplication, family: str | None, pixel_size: int | None, width_px: int
) -> None:
    """No value line of the tallest hover box is cut off at the chart's least height (`PL-HXSD`).

    The tallest box the concentration plot shows names the agent and then all
    six compartments. It appears where every trace is inside the hover radius,
    as at the start of a run, when all six are at zero. Two compared runs show
    fewer lines, because a compared chart draws at most two compartments.

    The box was drawn inside the plot, which cut it off at the plot's edge.
    The plot is shorter than the box in three cases: a narrow chart, where
    the time axis's longest title takes two lines, and a 13-pixel font, wide
    or narrow. Measured on 2026-11-23 before the fix, the box was 113 px and
    the plot 101 px on a plot 400 px wide, and 120 px and 112 px at 13 px.
    The box now keeps inside the plot wherever it fits there, and otherwise
    moves up over the time axis until all of it is inside the chart. The test
    runs in the container's font and in DejaVu Sans, the font the CI runners
    draw in.
    """

    old_font = application.font()
    _set_font(application, family, pixel_size)

    try:
        controller = SimulationController(agent_id="desflurane")
        _advance(controller, 120)
        controller.pause()
        frame = _frame(controller, span_s=900.0)
        chart = ConcentrationChart()
        chart.show_time_window(PREVIEW_TIME_AXIS_CAPTION_TEMPLATE.format(span="15 minutes"))
        chart.resize(width_px, chart.minimumSizeHint().height())
        chart.show()
        application.processEvents()
        chart.draw(frame)
        chart.grab()
        application.processEvents()
        assert chart.height() == CHART_LEAST_HEIGHT

        if width_px == _NARROW_CHART_WIDTH_PX:
            assert len(chart.time_axis_lines) > 1, chart.time_axis_lines

        box = _hover_on_the_corner(chart)
        whole = QRectF(0.0, 0.0, chart.width(), chart.height())
        assert _widened(whole).contains(box), f"the box {box} leaves the chart {whole}"

        # Where the box is placed is not where it is drawn, if something clips
        # it. Its rectangle stayed whole while the plot cut off its last line.
        # So the test reads the painted pixels of its top and bottom edges.
        image = chart.painted()
        for name, edge_y in (("top", box.top()), ("bottom", box.bottom())):
            share = _edge_drawn_share(image, box, edge_y)
            assert share >= _DRAWN_EDGE_SHARE, f"the box's {name} edge is {share:.0%} drawn"

        area = chart.plot_area()

        if area.height() >= box.height():
            assert _widened(area).contains(box), (
                f"the box {box} leaves the plot {area}, which has room for it"
            )

        if width_px == _NARROW_CHART_WIDTH_PX or pixel_size is not None:
            # The case the fix is for: the plot is shorter than the box.
            assert area.height() < box.height(), (area, box)
    finally:
        application.setFont(old_font)


#: How many drawn points the side-edge test skips between two it hovers. Each
#: hover waits for the box, so hovering all 156 points in the middle of the
#: plot would take minutes.
_SIDE_EDGE_POINT_STRIDE = 7


def test_no_hover_box_runs_past_the_side_of_a_narrow_chart(application: QApplication) -> None:
    """A box beside a point near the middle of a narrow plot stays whole inside the chart.

    The box goes to the right of a point in the left half and to the left of
    a point in the right half. On a narrow chart a box is wider than half the
    plot, so a box beside a point near the middle ran past the chart's side
    and lost its value column or its compartment name. The review of
    `PL-HXSD`'s change found it. The box now goes to the other side of the
    point where it does not fit, and is moved across into the chart where it
    fits on neither side. The test hovers drawn points across the whole
    width of a narrow chart, in the CI runners' font, which draws the widest
    lines.
    """

    old_font = application.font()
    _set_font(application, "DejaVu Sans", None)

    try:
        controller = SimulationController(agent_id="desflurane")
        controller.start()
        _advance(controller, 600)
        controller.pause()
        frame = _frame(controller, span_s=900.0)
        chart = ConcentrationChart()
        chart.resize(_NARROW_CHART_WIDTH_PX, CHART_HEIGHT)
        chart.show()
        application.processEvents()
        chart.draw(frame)
        chart.grab()
        application.processEvents()
        area = chart.plot_area()
        whole = QRectF(0.0, 0.0, chart.width(), chart.height())
        # The points in the middle fifth of the plot, where a box beside a
        # point has the least room on either side.
        points = [
            point
            for quantity in frame.visible
            for point in zip(*chart.drawn_points(0, quantity), strict=True)
            if area.contains(QPointF(*chart.plot_pixel(*point)))
            and abs(chart.plot_pixel(*point)[0] - area.center().x()) < area.width() / 10
        ][::_SIDE_EDGE_POINT_STRIDE]
        widths = []
        outside = []

        for time_s, percent in points:
            pixel = QPoint(*chart.plot_pixel(time_s, percent))
            # Off the plot first, so that the box measured is the one this
            # point raised, not the previous point's.
            _leave(chart, pixel)
            _wait_for_hover(chart, None)
            _move_pointer(chart, pixel)
            deadline = QDeadlineTimer(_HOVER_WAIT_MS)
            while chart.hover_box() is None and not deadline.hasExpired():
                QTest.qWait(10)
            box = chart.hover_box()
            assert box is not None, f"no hover answered at {time_s} s"
            widths.append(box.width())

            if not _widened(whole).contains(box):
                outside.append((time_s, percent, box))

        # A box wider than half the plot, or no box could run past the side.
        assert max(widths) > area.width() / 2, (max(widths), area.width())
        assert not outside, f"{len(outside)} of {len(widths)} boxes leave {whole}: {outside[:3]}"
    finally:
        application.setFont(old_font)


def test_a_box_on_show_is_placed_again_when_the_font_changes(application: QApplication) -> None:
    """A font change places the box on show again, as a resize does (`PL-HXSD`).

    The box takes the new font, and so a new height. A box placed above its
    point keeps its top, so without being placed again it grew down over the
    point, until the pointer next moved. The review of `PL-HXSD`'s change
    found it.
    """

    old_font = application.font()

    try:
        controller = SimulationController(agent_id="desflurane")
        controller.start()
        _advance(controller, 600)
        controller.pause()
        frame = _frame(controller, span_s=900.0)
        chart = ConcentrationChart()
        chart.resize(int(_PLOT_WIDTH_PX), CHART_HEIGHT)
        chart.show()
        application.processEvents()
        chart.draw(frame)
        chart.grab()
        application.processEvents()
        area = chart.plot_area()
        # A point low on the plot, so the box goes above it in either font.
        time_s, percent = min(
            (
                point
                for point in zip(*chart.drawn_points(0, RecordedQuantity.FAT), strict=True)
                if area.contains(QPointF(*chart.plot_pixel(*point)))
                and point[0] > frame.start_s + 60.0
            ),
            key=lambda point: point[1],
        )
        x_px, y_px = chart.plot_pixel(time_s, percent)
        _move_pointer(chart, QPoint(x_px, y_px))
        _wait_for_hover(chart, chart.readout_at(time_s, percent))
        before = chart.hover_box()
        assert before is not None
        assert before.bottom() <= y_px + _BOX_EDGE_TOLERANCE_PX, (before, y_px)

        _set_font(application, None, _LARGER_FONT_PX)
        application.processEvents()
        after = chart.hover_box()

        assert after is not None
        assert after.height() > before.height(), (before, after)
        assert after.bottom() <= y_px + _BOX_EDGE_TOLERANCE_PX, (after, y_px)
    finally:
        application.setFont(old_font)


def test_a_font_too_large_for_the_least_height_makes_the_chart_taller(
    application: QApplication,
) -> None:
    """A font that makes the tallest box taller than the least height grows the chart (`PL-HXSD`).

    A reader who enlarges the desktop's text makes the box taller. The box
    could then be cut off at the chart's edge, however it is moved. So the
    chart's least height follows the box's height wherever that is the
    taller of the two. The font changes after the chart is built, as it
    does when the reader changes it while the app runs.
    """

    old_font = application.font()

    try:
        controller = SimulationController(agent_id="desflurane")
        _advance(controller, 120)
        controller.pause()
        frame = _frame(controller, span_s=900.0)
        chart = ConcentrationChart()
        chart.show()
        application.processEvents()
        assert chart.minimumSizeHint().height() == CHART_LEAST_HEIGHT

        # Twice the container's 12 px, the enlargement to which WCAG 2.2
        # Success Criterion 1.4.4 asks text to resize without loss of content.
        _set_font(application, None, 24)
        application.processEvents()
        least_px = chart.minimumSizeHint().height()
        assert least_px > CHART_LEAST_HEIGHT

        chart.resize(int(_PLOT_WIDTH_PX), least_px)
        application.processEvents()
        chart.draw(frame)
        chart.grab()
        application.processEvents()
        box = _hover_on_the_corner(chart)
        assert box.height() > CHART_LEAST_HEIGHT
        whole = QRectF(0.0, 0.0, chart.width(), chart.height())
        assert _widened(whole).contains(box), f"the box {box} leaves the chart {whole}"
    finally:
        application.setFont(old_font)


def _leave(chart: ConcentrationChart | WashInChart, pixel: QPoint) -> None:
    """Take the pointer off the chart from over one pixel, as the platform reports it.

    It sends a `Leave` to the widget under that pixel and no move, because a
    `Leave` is all that a pointer leaving a widget sends it.
    """

    QApplication.sendEvent(chart.childAt(pixel), QEvent(QEvent.Type.Leave))


def _two_points(
    chart: ConcentrationChart | WashInChart, frame: ChartFrame
) -> tuple[QPoint, QPoint]:
    """Return two chart pixels over drawn points of the frame's run, with different readouts.

    On the compartment chart, the points are on the circuit trace, where
    `test_the_hover_answers_the_point_under_the_pointer` finds it clear of the
    other five traces. On the wash-in plot, they are two points of the first
    stretch.
    """

    run = frame.runs[0]

    if isinstance(chart, ConcentrationChart):
        count = len(run.times_s)
        circuit = run.percents(RecordedQuantity.CIRCUIT)
        earlier, later = count // 4, 3 * count // 4

        return (
            QPoint(*chart.plot_pixel(run.times_s[earlier], circuit[earlier])),
            QPoint(*chart.plot_pixel(run.times_s[later], circuit[later])),
        )

    stretch = run.wash_in[0]
    earlier, later = len(stretch.times_s) // 4, len(stretch.times_s) // 2

    return (
        QPoint(*chart.plot_pixel(stretch.times_s[earlier], stretch.ratios[earlier])),
        QPoint(*chart.plot_pixel(stretch.times_s[later], stretch.ratios[later])),
    )


def test_the_hover_hides_when_the_pointer_leaves_and_a_later_frame_does_not_bring_it_back(
    application: QApplication,
) -> None:
    """`PL-LTKL`: on both plots, the box disappears when the pointer leaves, and stays hidden.

    A pointer leaving the plot sends it no move, only a `Leave`, and only a
    move used to hide the box. So the box stayed up at the last point, and
    each later frame showed that point again. While the run played, each frame
    showed a new instant, so a modelled value climbed with the run for a
    pointer that had gone. A move still waiting out the cooldown when the
    pointer leaves is discarded too. Otherwise the end of the cooldown would
    show the box again.
    """

    controller = _run_with_a_dial_change()
    assert controller.is_running
    frame = _frame(controller)
    charts = (
        _shown(application, ConcentrationChart(), 480),
        _shown(application, WashInChart(), 300),
    )

    for chart in charts:
        chart.draw(frame)

    # Labelling the axes can widen one and move the plot, so the layout is
    # settled before a pixel is read off it.
    application.processEvents()

    for chart in charts:
        first, second = _two_points(chart, frame)
        _move_pointer(chart, first)
        answered = chart.hover_text()
        assert answered is not None, "the hover must have answered for this to test it"
        _move_pointer(chart, second)
        assert chart.hover_text() == answered, "the second move must be held for this to test it"

        _leave(chart, second)

        assert chart.hover_text() is None

    # After the longest time that a held move waits for a response, neither
    # box has come back.
    shown: set[str] = set()
    held = QDeadlineTimer(_HOVER_HOLD_MS)

    while not held.hasExpired():
        QTest.qWait(10)
        shown.update(text for chart in charts if (text := chart.hover_text()) is not None)

    assert not shown

    # A following frame does not bring a box back either, after the run has
    # played on.
    _advance(controller, 30)
    following = _frame(controller)

    for chart in charts:
        chart.draw(following)

        assert chart.hover_text() is None

    application.processEvents()

    # A pointer that comes back gets a readout again, so leaving did not
    # switch the hover off.
    for chart in charts:
        back, _ = _two_points(chart, following)
        _move_pointer(chart, back)

        assert chart.hover_text() is not None


def test_a_chart_let_go_is_freed_at_once_rather_than_by_the_collector(
    application: QApplication,
) -> None:
    """`PL-TCR5`: a chart that nothing references any more is freed when its last reference goes.

    Its hover once stored the chart's own method as a callback, which made a
    reference cycle. So a released chart was freed only when the cycle
    collector next ran. That can happen in the middle of the chart's own
    paint, and in CI it did, as a segmentation fault in
    `QPainter::resetTransform`. The collector is off in this test, so only the
    reference count can free the chart.
    """

    controller = _run_with_a_dial_change()
    frame = _frame(controller)
    stretch = frame.runs[0].wash_in[0]
    run = frame.runs[0]
    collecting = gc.isenabled()
    gc.disable()

    try:
        chart = _shown(application, ConcentrationChart(), 480)
        chart.draw(frame)
        application.processEvents()
        time_s, percent = run.times_s[150], run.percents(RecordedQuantity.CIRCUIT)[150]
        _move_pointer(chart, QPoint(*chart.plot_pixel(time_s, percent)))
        _wait_for_hover(chart, format_trace_hover(run, RecordedQuantity.CIRCUIT, 150, 1))
        assert chart.hover_text() is not None, "the hover must have answered for this to test it"
        concentration = weakref.ref(chart)
        del chart

        wash_in = _shown(application, WashInChart(), 300)
        wash_in.draw(frame)
        application.processEvents()
        index = len(stretch.times_s) // 2
        _move_pointer(
            wash_in, QPoint(*wash_in.plot_pixel(stretch.times_s[index], stretch.ratios[index]))
        )
        _wait_for_hover(wash_in, wash_in.readout_at(stretch.times_s[index], stretch.ratios[index]))
        assert wash_in.hover_text() is not None, "the hover must have answered for this to test it"
        ratio = weakref.ref(wash_in)
        del wash_in

        assert concentration() is None
        assert ratio() is None
    finally:
        if collecting:
            gc.enable()


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
            # Qt states a dash pattern in pen widths, and the table states it in pixels.
            assert pen.dashPattern() == pytest.approx(
                [length / style.stroke_width for length in style.dash_pattern]
            )


def _painted_runs(pen: QPen) -> list[int]:
    """Paint `pen` as a horizontal line and return the on and off run lengths, in pixels.

    The line is painted with antialiasing off on a white image, and the row
    through its centre is scanned from the line's start, where Qt begins the
    pattern's first dash.
    """

    width, height = 600, 20
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor("#ffffff"))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
    painter.setPen(pen)
    painter.drawLine(QPointF(0.0, height / 2), QPointF(float(width), height / 2))
    painter.end()

    row = [image.pixelColor(x, height // 2) != QColor("#ffffff") for x in range(width)]

    runs: list[int] = []
    current, length = row[0], 0
    for painted in row:
        if painted == current:
            length += 1
        else:
            runs.append(length)
            current, length = painted, 1

    return runs


def test_each_dashed_pen_paints_its_dash_pattern(application: QApplication) -> None:
    """`PL-88MK`: each dash and gap is painted at the length the table gives.

    Qt's default square cap extends every dash by half the pen's width at each
    end. On a 3 px compartment pen, that turned a 10/4 pattern into 13 on
    and 1 off, so the dashed traces looked almost solid. The dash pattern is
    the only thing that tells some compartments apart for a reader with a
    colour-vision deficiency. Comparing the numbers that `dashPattern()` returns
    cannot detect the cap, so this test paints each pen and measures the pixels.
    """

    pens = [(style.dash_pattern, trace_pen(style)) for style in COMPARTMENT_TRACES]
    pens.append(
        (
            CONTROL_MARK_DASH_PATTERN,
            dashed_pen(CONTROL_MARK_COLOR, CONTROL_MARK_STROKE_WIDTH, CONTROL_MARK_DASH_PATTERN),
        )
    )

    for pattern, pen in pens:
        if pattern is None:
            continue
        runs = _painted_runs(pen)
        # Whole periods only: the last run is cut by the image's edge.
        whole = len(pattern) * ((len(runs) - 1) // len(pattern))

        assert whole >= 2 * len(pattern)
        assert runs[:whole] == [round(length) for length in pattern] * (whole // len(pattern))


def test_the_time_axis_title_states_the_window_and_breaks_only_after_a_comma(
    application: QApplication,
) -> None:
    """`PL-K4CZ`: the time axis's title states the window, on one line where the axis has room.

    The window had a line of its own above the plot, which took the plot's
    height at 1366 by 768. On a narrow plot the title breaks after a comma,
    so the span keeps its unit, and it is one line again once the plot is
    wide.
    """

    chart = ConcentrationChart()
    window = "15 minutes shown, centred on now during the preview"
    chart.show_time_window(window)
    chart.resize(1200, 400)
    chart.show()
    application.processEvents()

    assert chart.time_axis_title == "simulated time, " + window
    assert chart.time_axis_lines == (chart.time_axis_title,)

    chart.resize(300, 400)
    application.processEvents()
    lines = chart.time_axis_lines

    assert len(lines) > 1
    assert all(line.endswith(",") for line in lines[:-1])
    assert any("15 minutes shown," in line for line in lines)
    assert " ".join(lines) == chart.time_axis_title
    assert chart.axis_titles()[1] == chart.time_axis_title

    chart.resize(1200, 400)
    application.processEvents()

    assert chart.time_axis_lines == (chart.time_axis_title,)

    # A new title with as many lines as the old one is centred again under
    # the plot, and not left where the old, shorter title began.
    chart.show_time_window("15 minutes shown")
    application.processEvents()

    assert chart.time_axis_lines == ("simulated time, 15 minutes shown",)
    assert abs(chart.time_axis_title_offset_px) <= 1

    chart.show_time_window(window)
    application.processEvents()

    assert len(chart.time_axis_lines) == 1
    assert abs(chart.time_axis_title_offset_px) <= 1
    chart.close()


@pytest.mark.parametrize(
    "chart_kind", [ConcentrationChart, WashInChart], ids=["concentration chart", "wash-in plot"]
)
def test_deleting_a_chart_s_window_leaves_its_time_axis_title_writing_nothing(
    application: QApplication,
    capfd: pytest.CaptureFixture[str],
    chart_kind: type[ConcentrationChart] | type[WashInChart],
) -> None:
    """A chart whose window is deleted prints no traceback from its time axis title (`PL-9RZJ`).

    The title is fitted again whenever the time axis changes geometry. After a
    frame is drawn and then withheld, Qt reports a geometry change on the
    axis while the axis itself is being deleted, after its Python side is
    gone. Before the fix, that report printed `RuntimeError: ... Internal
    C++ object (AxisItem) already deleted` to the error stream. PySide prints
    an exception raised in a slot and goes on, so no test failed while it
    happened.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 60)
    window = QWidget()
    chart = chart_kind(window)
    window.resize(900, 400)
    chart.resize(900, 400)
    window.show()
    application.processEvents()
    chart.draw(_frame(controller))
    application.processEvents()
    chart.withhold()
    application.processEvents()
    capfd.readouterr()

    window.deleteLater()
    application.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    application.processEvents()

    assert "Traceback" not in capfd.readouterr().err


def test_each_clinical_reference_entry_states_its_value_and_the_band_s_words_wrap(
    application: QApplication,
) -> None:
    """`PL-K4CZ`: the 1 MAC and MAC-awake entries carry their values, and the band's wraps.

    The values had a line each above the legend, which took the plot's height
    at 1366 by 768. In a legend wide enough, the band's entry is one line.
    In a narrow one its words wrap inside the legend, so the entry neither
    runs past the right edge nor raises the legend's least width.
    """

    legend = TraceLegend()
    one_mac = "1 MAC sevoflurane = 1.8%"
    mac_awake = "MAC-awake sevoflurane = 0.34 ×MAC (0.61%), band ±1 SD 0.52–0.70%"
    legend.show_references(one_mac, mac_awake)
    legend.resize(2000, legend.heightForWidth(2000))
    legend.show()
    application.processEvents()
    band = next(
        label for label in legend.findChildren(QLabel) if label.text() == legend.band_mark.label
    )
    one_line = band.height()

    assert legend.one_mac_text == one_mac + ", reference adult (alveolar, wide dash)"
    assert (
        legend.band_mark.label == mac_awake + "; population, read against vessel-rich group trace"
    )
    assert band.heightForWidth(band.width()) == one_line

    narrow = legend.minimumSizeHint().width()
    legend.resize(narrow, legend.heightForWidth(narrow))
    application.processEvents()
    entry = band.parentWidget()

    assert entry is not None
    assert band.height() > one_line
    assert entry.geometry().right() < legend.width()
    assert narrow < band.sizeHint().width()
    # The words break only after a comma or a semicolon, so no value is
    # parted from its unit and no range from either of its edges.
    lines = band.text().split("\n")

    assert len(lines) > 1
    assert all(line.endswith((",", ";")) for line in lines[:-1])
    assert "MAC-awake sevoflurane = 0.34 ×MAC (0.61%)," in lines
    assert any(line.startswith("band ±1 SD 0.52–0.70%;") for line in lines)
    assert (
        legend.band_mark.label == mac_awake + "; population, read against vessel-rich group trace"
    )
    legend.close()


def test_the_band_legend_swatch_is_ruled_on_both_edges_like_the_chart_mark(
    application: QApplication,
) -> None:
    """A legend that shows one mark while the chart draws another leads the reader to misread it.

    The swatch is how a reader learns which mark means what. A swatch with a
    line on its upper edge only would bring back the line-not-band reading
    that `PL-90Y6` removed from the chart, and the reader would carry it into
    every later glance at the plot. The test checks the swatch twice. It checks
    the pen and brush that the swatch says it paints with. It also checks the
    pixels it painted: the top and bottom rows in the edge colour, and the
    rows between them in the fill colour at its opacity over the widget's own
    background.
    """

    legend = TraceLegend()
    legend.show()
    application.processEvents()
    mark = legend.band_mark

    assert mark.label == "MAC-awake; population, read against vessel-rich group trace"
    assert mark.edge_pen.color().name() == MAC_AWAKE_BAND_COLOR.lower()
    assert mark.edge_pen.widthF() == MAC_AWAKE_BAND_EDGE_STROKE_WIDTH
    assert mark.edge_pen.dashPattern() == []
    assert mark.fill.color().name() == MAC_AWAKE_BAND_COLOR.lower()
    # QColor stores alpha in sixteen bits, so the opacity comes back at that resolution.
    assert mark.fill.color().alphaF() == pytest.approx(MAC_AWAKE_BAND_FILL_OPACITY, abs=1 / 65535)

    swatch = legend.band_swatch
    image = swatch.grab().toImage()
    x = image.width() // 2
    top = image.pixelColor(x, 0)
    bottom = image.pixelColor(x, image.height() - 1)
    middle = image.pixelColor(x, image.height() // 2)
    ground = swatch.palette().color(QPalette.ColorRole.Window)
    edge = mark.edge_pen.color()

    assert top.name() == edge.name()
    assert bottom.name() == edge.name()

    for channel in ("red", "green", "blue"):
        blended = (
            getattr(ground, channel)() * (1.0 - MAC_AWAKE_BAND_FILL_OPACITY)
            + getattr(edge, channel)() * MAC_AWAKE_BAND_FILL_OPACITY
        )

        assert getattr(middle, channel)() == pytest.approx(blended, abs=1.0)

    legend.close()


def test_the_legend_is_the_visibility_control(application: QApplication) -> None:
    """A click is a request, and the boxes show the owner's response to it (`PL-VN6M`).

    The test takes the place of `SimulationView`. It stores the selection,
    applies each request to it, and passes the result back. After every click,
    the legend shows the selection that the owner stores.
    """

    legend = TraceLegend()
    selection = INITIAL_COMPARTMENT_SELECTION
    changes: list[tuple[RecordedQuantity, ...]] = []

    def answer(quantity: RecordedQuantity, shown: bool) -> None:
        nonlocal selection
        selection = selection.with_compartment(quantity, shown)
        legend.show_selection(selection)
        changes.append(legend.shown)

    legend.compartment_requested.connect(answer)

    assert legend.shown == COMPARTMENT_QUANTITIES

    for quantity in COMPARTMENT_QUANTITIES:
        if quantity is not RecordedQuantity.MUSCLE:
            legend.set_compartment_shown(quantity, False)

    assert legend.shown == (RecordedQuantity.MUSCLE,)
    assert changes and changes[-1] == (RecordedQuantity.MUSCLE,)
    assert len(changes) == len(COMPARTMENT_QUANTITIES) - 1
    assert selection.shown == legend.shown


def _box(legend: TraceLegend, quantity: RecordedQuantity) -> QCheckBox:
    """Return the box a reader clicks for one compartment, found by its accessible name."""

    from anesthesia_sim.app.dashboard_frame import TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE

    name = TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE.format(label=trace_style(quantity).label)

    return next(box for box in legend.findChildren(QCheckBox) if box.accessibleName() == name)


def test_a_click_nobody_answers_leaves_the_legend_showing_what_it_was_handed(
    application: QApplication,
) -> None:
    """The boxes store no state of their own, so a request that nobody handles changes nothing.

    This matters for a legend whose owner is gone, or has not yet connected.
    There, a box left as the reader clicked it would name a curve that no
    frame draws. The click is still sent, once. The box, its swatch and its
    words return to the selection last shown.
    """

    legend = TraceLegend()
    requests: list[tuple[RecordedQuantity, bool]] = []
    legend.compartment_requested.connect(lambda quantity, shown: requests.append((quantity, shown)))
    box = _box(legend, RecordedQuantity.FAT)
    inked = box.styleSheet()

    box.click()

    assert requests == [(RecordedQuantity.FAT, False)]
    assert box.isChecked()
    assert legend.shown == COMPARTMENT_QUANTITIES
    assert box.styleSheet() == inked
    assert legend._swatches[RecordedQuantity.FAT]._filled


def test_a_selection_handed_to_the_legend_is_shown_and_requests_nothing(
    application: QApplication,
) -> None:
    """`PL-B1R9`: the owner's own change is not sent back to it as if a reader had made it.

    A selection that the owner passes down is the owner's to draw a frame
    for. It may come from a click the owner handled, or from a second run that
    limits the selection to the cap. When it was echoed back as a request, the
    cap's reduction drew a frame from a set of runs only half updated for the
    new run. The fork that caused the reduction then drew its own frame.
    """

    legend = TraceLegend()
    requests: list[tuple[RecordedQuantity, bool]] = []
    legend.compartment_requested.connect(lambda quantity, shown: requests.append((quantity, shown)))
    reduced = INITIAL_COMPARTMENT_SELECTION.with_run_count(2)

    # A new legend shows the opening selection on one run, with no compared row.
    assert legend.shown == COMPARTMENT_QUANTITIES
    assert legend._compared_caption.isHidden() is True

    legend.show_run_names((run_label(FIRST_RUN), run_label(SECOND_RUN)))
    legend.show_selection(reduced)

    assert requests == []
    assert legend.shown == reduced.shown == (RecordedQuantity.CIRCUIT, RecordedQuantity.ALVEOLAR)
    assert legend._run_count == 2
    assert legend.branch_mark is not None
    assert len(legend.compared_marks) == len(reduced.shown) * reduced.run_count
    assert legend._compared_caption.isHidden() is False

    # The legend key of a compartment that the cap removed shows the removal in
    # both channels other than colour, so it cannot be read as a curve on the plot.
    fat = _box(legend, RecordedQuantity.FAT)

    assert not fat.isChecked()
    assert legend._swatches[RecordedQuantity.FAT]._filled is False
    assert fat.styleSheet() == foreground_stylesheet(MUTED)
    assert _box(legend, RecordedQuantity.CIRCUIT).styleSheet() == foreground_stylesheet(INK)

    legend.show_selection(reduced.with_run_count(1))

    assert requests == []
    assert legend.branch_mark is None
    assert legend.compared_marks == ()


def _legend_rows(legend: QWidget) -> list[FlowLayout]:
    """Return the legend's rows, top to bottom, each one a wrapping row."""

    layout = legend.layout()
    assert layout is not None
    rows = []

    for index in range(layout.count()):
        item = layout.itemAt(index)
        assert item is not None
        row = item.layout()
        assert isinstance(row, FlowLayout), "a legend row that cannot wrap"
        rows.append(row)

    return rows


def _entries_inside(legend: QWidget, rows: list[FlowLayout]) -> None:
    for row in rows:
        for index in range(row.count()):
            item = row.itemAt(index)
            assert item is not None
            widget = item.widget()

            # A hidden entry is not laid out and keeps whatever geometry it
            # was built with, so it cannot be outside the legend.
            # `FlowLayout._laid_items` is what skips it.
            if widget is not None and widget.isHidden():
                continue

            geometry = item.geometry()

            assert geometry.x() >= 0
            assert geometry.right() < legend.width(), "a legend entry laid beyond the legend"


def test_the_legend_rows_wrap_under_a_narrow_chart_and_stand_on_one_line_under_a_wide_one(
    application: QApplication,
) -> None:
    """The six compartment entries wrap rather than forcing the chart column to their total width.

    The Flet legend rows wrapped. On one unbreakable line, the compartments
    row alone forced the chart column to 1220 px wide and pushed the sidebar
    off a 1400 px window. The caption stays first and the entries follow it.
    """

    legend = TraceLegend()
    references, compartments, compared, record = _legend_rows(legend)
    one_line = compartments.minimumSize().height()

    # The per-run row is hidden entirely while one run is drawn, because the
    # compartment row above already names every drawn curve completely.
    assert compared.count() > 0
    assert legend.compared_marks == ()

    assert compartments.heightForWidth(1400) == one_line
    assert compartments.heightForWidth(500) > one_line
    assert legend.minimumSizeHint().width() == max(
        row.minimumSize().width() for row in _legend_rows(legend)
    )

    narrow = 500
    legend.resize(narrow, legend.heightForWidth(narrow))
    legend.show()
    application.processEvents()

    assert legend.width() == narrow
    _entries_inside(legend, [compartments, references, record])
    caption = compartments.itemAt(0)
    assert caption is not None
    caption_label = caption.widget()
    assert isinstance(caption_label, QLabel)
    assert caption_label.text() == "Compartments:"
    entry_lines = {
        compartments.itemAt(index).geometry().y()  # type: ignore[union-attr]
        for index in range(1, compartments.count())
    }
    assert caption_label.geometry().y() == min(entry_lines)
    assert len(entry_lines) > 1, "the compartments row did not wrap at 500 px"

    wide = 1400
    legend.resize(wide, legend.heightForWidth(wide))
    application.processEvents()

    assert {
        compartments.itemAt(index).geometry().y()  # type: ignore[union-attr]
        for index in range(compartments.count())
    } == {caption_label.geometry().y()}
    _entries_inside(legend, [compartments, references, record])
    legend.close()


def test_the_wash_in_legend_row_wraps_too(application: QApplication) -> None:
    legend = WashInLegend()
    (row,) = _legend_rows(legend)
    one_line = row.minimumSize().height()

    assert row.heightForWidth(1400) == one_line
    assert row.heightForWidth(300) > one_line

    legend.resize(300, legend.heightForWidth(300))
    legend.show()
    application.processEvents()
    _entries_inside(legend, [row])
    legend.close()


def test_the_wash_in_legend_names_its_three_marks_in_the_plot_s_own_pens(
    application: QApplication,
) -> None:
    """The wash-in row says what the wash-in plot draws, in the pens it draws it with.

    The trace is solid at its own stroke width, the equilibrium line is in its
    wide dash, and the control mark is upright in its fine dash. Each swatch
    uses the plot's own pen, so the legend cannot describe a line that the
    plot does not draw (`PL-THXF`). The words state the line style too.
    """

    legend = WashInLegend()
    legend.show()
    application.processEvents()
    trace, equilibrium, mark = legend.marks

    assert not legend.grab().toImage().isNull()

    assert [entry.label for entry in legend.marks] == [
        WASH_IN_TRACE_LEGEND_LABEL,
        EQUILIBRIUM_LEGEND_LABEL,
        CONTROL_MARK_LEGEND_LABEL,
    ]
    # This uses `isVisible` rather than `isHidden`. The per-run and fork
    # entries are hidden by their wrapper, and a label inside a hidden parent
    # has no hidden flag of its own.
    assert {label.text() for label in legend.findChildren(QLabel) if label.isVisible()} == {
        WASH_IN_TRACE_LEGEND_LABEL,
        EQUILIBRIUM_LEGEND_LABEL,
        CONTROL_MARK_LEGEND_LABEL,
    }

    assert trace.pen.color().name() == WASH_IN_COLOR.lower()
    assert trace.pen.widthF() == WASH_IN_STROKE_WIDTH
    assert trace.pen.dashPattern() == []
    assert not trace.vertical

    assert equilibrium.pen.color().name() == EQUILIBRIUM_LINE_COLOR.lower()
    assert equilibrium.pen.widthF() == EQUILIBRIUM_LINE_STROKE_WIDTH
    assert equilibrium.pen.dashPattern() == pytest.approx(
        [length / EQUILIBRIUM_LINE_STROKE_WIDTH for length in EQUILIBRIUM_LINE_DASH_PATTERN]
    )
    assert not equilibrium.vertical

    assert mark.pen.color().name() == CONTROL_MARK_COLOR.lower()
    assert mark.pen.widthF() == CONTROL_MARK_STROKE_WIDTH
    assert mark.pen.dashPattern() == pytest.approx(
        [length / CONTROL_MARK_STROKE_WIDTH for length in CONTROL_MARK_DASH_PATTERN]
    )
    assert mark.vertical


def test_every_compartment_box_carries_the_name_assistive_technology_announces(
    application: QApplication,
) -> None:
    """The Flet legend's semantics label survives the port as the box's accessible name.

    The words beside a box describe the line ("Circuit (solid)"). A screen
    reader should instead announce the action that the box performs. That is
    the string the Flet build carried, and the port must not lose it
    (`PL-25KS`).
    """

    from anesthesia_sim.app.dashboard_frame import TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE

    legend = TraceLegend()
    boxes = legend.findChildren(QCheckBox)
    names = {box.accessibleName() for box in boxes}

    assert names == {
        TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE.format(label=style.label)
        for style in COMPARTMENT_TRACES
    }


def _dashes_px(pen) -> list[float]:
    """Return a pen's dash pattern converted back to display pixels.

    Qt states a dash pattern in units of the pen's width, so widening a pen
    changes the numbers it reports while drawing the same dashes. The
    compartment's pattern is declared in pixels
    (`chart_frame.COMPARTMENT_TRACES`), and pixels are what two runs of one
    compartment have to agree on.
    """

    return [length * pen.widthF() for length in pen.dashPattern()]


#: Each compartment's legend words: its name and its line style, from the table
#: in `docs/INTERFACE.md` § "The six compartment traces: what separates them".
COMPARTMENT_LEGEND_WORDS = {
    RecordedQuantity.CIRCUIT: "Circuit (solid)",
    RecordedQuantity.ALVEOLAR: "Alveolar (long dash)",
    RecordedQuantity.MIXED_VENOUS: "Mixed venous (short dash)",
    RecordedQuantity.VESSEL_RICH: "Vessel-rich group (even dash)",
    RecordedQuantity.MUSCLE: "Muscle (dotted)",
    RecordedQuantity.FAT: "Fat (dash-dot)",
}


def test_two_runs_on_one_axis_are_told_apart_by_line_width_and_named_in_text(
    application: QApplication,
) -> None:
    """`PL-8PSW`: the whole encoding, on a real fork, on both plots and in both legends.

    The test checks four claims, and a misreading of any one of them would be
    a clinical error. First, the compartment keeps its line style and colour
    exactly as the single-run chart draws them, so no channel means two
    different things on either side of the mode change. Second, the run is
    shown by line width, at two levels, with the *first* run the wider. The
    two curves coincide exactly before the fork (`PL-Z3W6`), so the narrower
    one has to be drawn on top, or one run is invisible over that stretch.
    Third, every drawn curve's legend entry names both its compartment and
    its run, because `docs/INTERFACE.md` § "Minimum displayed outputs" requires
    the run to be named in text, and colour is already used for the
    compartment. Fourth, the fork itself is marked, since it is the one
    instant at which the two runs stop being the same run.
    """

    trunk = _run_with_a_dial_change()
    case = BranchedCase(trunk)
    branch = case.fork_at(CaseInstant(600))
    branch.start()
    branch.begin_control_adjustment()
    branch.set_fresh_gas_flow(FreshGasFlow(1.0))
    _advance(branch, 600)

    frame = _frame(*case.runs)
    chart = _shown(application, ConcentrationChart(), 480)
    wash_in = _shown(application, WashInChart(), 200)
    chart.draw(frame)
    wash_in.draw(frame)
    legend = TraceLegend()
    wash_in_legend = WashInLegend()
    legend.show_run_names(tuple(run.label for run in frame.runs))
    legend.show_selection(INITIAL_COMPARTMENT_SELECTION.with_run_count(len(frame.runs)))
    wash_in_legend.show_run_names(tuple(run.label for run in frame.runs))

    # The cap allows two compartments, which is what leaves line width free to show the run.
    assert len(frame.runs) == 2
    assert len(frame.visible) == COMPARED_COMPARTMENT_CAP

    for quantity in frame.visible:
        style = trace_style(quantity)
        first = chart.drawn_pen(0, quantity)
        second = chart.drawn_pen(1, quantity)

        # The compartment is unchanged on both runs: same colour, and the
        # same dashes in pixels, which is the unit the table declares.
        assert first.color().name() == style.color.lower()
        assert second.color().name() == style.color.lower()
        assert _dashes_px(first) == pytest.approx(_dashes_px(second))
        assert _dashes_px(second) == pytest.approx(list(style.dash_pattern or []))

        # The run is shown by width, and only the first run's width changed.
        assert second.widthF() == style.stroke_width
        assert first.widthF() == style.stroke_width + COMPARED_RUN_WIDTH_STEP
        assert first.widthF() != second.widthF()

    # The wash-in plot uses the same channel. It draws one trace per run in one
    # colour, so it would otherwise put two identical curves on one axis.
    assert wash_in.drawn_pen(1).widthF() == WASH_IN_STROKE_WIDTH
    assert wash_in.drawn_pen(0).widthF() == WASH_IN_STROKE_WIDTH + COMPARED_RUN_WIDTH_STEP

    # The fork is marked on the run that opened at it, and on no other.
    assert chart.branch_point_time(0) is None
    assert chart.branch_point_time(1) == pytest.approx(600.0)
    assert wash_in.branch_point_time(1) == pytest.approx(600.0)

    # Every drawn curve has a legend entry that names both its compartment and
    # its run, drawn in the curve's own pen, so the legend cannot describe a
    # line the plot is not drawing. The expected words are written out here,
    # never built by the functions that write the legend. The run at index i
    # was given `RUN_IDS[i]`, so it is called "Run" followed by i + 1
    # (`docs/INTERFACE.md` § "Naming the run in a comparison").
    marks = legend.compared_marks

    assert len(marks) == len(frame.visible) * len(frame.runs)

    for mark in marks:
        assert not mark.vertical

    def words(quantity: RecordedQuantity, index: int) -> str:
        return f"{COMPARTMENT_LEGEND_WORDS[quantity]}, Run {index + 1}"

    named = {mark.label for mark in marks}
    expected = {
        words(quantity, index) for quantity in frame.visible for index in range(len(frame.runs))
    }

    assert named == expected

    for quantity in frame.visible:
        for index in range(len(frame.runs)):
            entry = next(mark for mark in marks if mark.label == words(quantity, index))
            drawn = chart.drawn_pen(index, quantity)

            assert entry.pen.color().name() == drawn.color().name()
            assert entry.pen.widthF() == drawn.widthF()
            assert _dashes_px(entry.pen) == pytest.approx(_dashes_px(drawn))

    # The wash-in legend names each run too, each beside its own curve's pen,
    # since the width is all that tells the two curves apart.
    wash_in_marks = wash_in_legend.compared_marks

    assert len(wash_in_marks) == len(frame.runs)

    for index in range(len(frame.runs)):
        entry = next(
            mark
            for mark in wash_in_marks
            if mark.label == f"F<sub>A</sub>/F<sub>I</sub> (solid), Run {index + 1}"
        )
        drawn = wash_in.drawn_pen(index)

        assert entry.pen.color().name() == drawn.color().name()
        assert entry.pen.widthF() == drawn.widthF()

    # Both legends name the branch point beside a vertical line.
    for branch_mark in (legend.branch_mark, wash_in_legend.branch_mark):
        assert branch_mark is not None
        assert branch_mark.label == "Branch point (vertical, solid)"
        assert branch_mark.vertical


# ------------------------------------------------------ the preview of a dragged setting


def _previewing_frame(
    controller: SimulationController,
    value: float,
    control: ControlInput = ControlInput.FRESH_GAS_FLOW,
) -> ChartFrame:
    snapshot = controller.snapshot()

    return assemble_chart_frame(
        [
            RunInput(
                run_label(FIRST_RUN),
                controller,
                snapshot,
                (),
                preview=PreviewRequest(
                    SettingPreview(control, value), "Preview: Fresh gas flow 6.0 L/min, not applied"
                ),
            )
        ],
        time_base_for_span(1800.0),
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
        ceiling=ChartCeiling.STANDARD,
    )


def test_both_plots_draw_a_preview_thinner_inside_its_labelled_region(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 300)
    frame = _previewing_frame(controller, 6.0)
    preview = frame.runs[0].preview
    assert preview is not None
    chart = _shown(application, ConcentrationChart(), 480)
    wash_in = _shown(application, WashInChart(), 240)
    chart.draw(frame)
    wash_in.draw(frame)

    for style in COMPARTMENT_TRACES:
        times, percents = chart.preview_points(0, style.quantity)
        pen = chart.preview_pen(0, style.quantity)

        assert times == pytest.approx(preview.times_s)
        assert percents == pytest.approx(preview.percents(style.quantity))
        assert pen.color().name() == QColor(style.color).name()
        assert pen.widthF() == max(2, style.stroke_width - 1)
        assert pen.style() == chart.drawn_pen(0, style.quantity).style()

    for plot in (chart, wash_in):
        assert plot.preview_region(0) == pytest.approx(preview.region_s)
        assert plot.preview_label(0) == preview.label

    drawn = [point for stretch in wash_in.preview_stretches(0) for point in stretch]
    assert drawn
    assert all(preview.region_s[0] <= time_s <= preview.region_s[1] for time_s, _ in drawn)
    assert wash_in.preview_pen(0).widthF() == WASH_IN_STROKE_WIDTH - 1


def test_every_curve_is_handed_the_frame_s_own_values_as_float64_arrays(
    application: QApplication,
) -> None:
    """Each curve gets numpy arrays equal, bit for bit, to what the frame holds (`PL-TCNT`).

    pyqtgraph's performance guidance asks for `numpy.ndarray`s rather than
    lists, and allows `skipFiniteCheck` for data known to be finite. The
    chart follows both. The comparison is exact, not approximate. The chart
    used to hand pyqtgraph `list(...)` of these same values, and pyqtgraph
    copied them into `float64` arrays. So exact equality with the frame
    shows that no drawn point changed. The test checks every curve, for the
    run and for the preview, on both plots, so that no curve is left on the
    old path.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300)
    frame = _previewing_frame(controller, 6.0)
    run = frame.runs[0]
    preview = run.preview
    assert preview is not None
    assert run.wash_in
    assert preview.wash_in
    chart = _shown(application, ConcentrationChart(), 480)
    wash_in = _shown(application, WashInChart(), 240)
    chart.draw(frame)
    wash_in.draw(frame)
    chart_items = chart._runs[0]
    wash_in_items = wash_in._runs[0]
    handed = [
        *(
            (chart_items.curves[quantity], run.times_s, run.percents(quantity))
            for quantity in COMPARTMENT_QUANTITIES
        ),
        *(
            (chart_items.preview_curves[quantity], preview.times_s, preview.percents(quantity))
            for quantity in COMPARTMENT_QUANTITIES
        ),
        *(
            (curve, stretch.times_s, stretch.ratios)
            for curve, stretch in zip(wash_in_items.stretches, run.wash_in, strict=False)
        ),
        *(
            (curve, stretch.times_s, stretch.ratios)
            for curve, stretch in zip(
                wash_in_items.preview_stretches, preview.wash_in, strict=False
            )
        ),
    ]

    for curve, times_s, values in handed:
        x, y = curve.getData()

        assert type(x) is np.ndarray
        assert type(y) is np.ndarray
        assert x.dtype == np.float64
        assert y.dtype == np.float64
        assert x.tolist() == list(times_s)
        assert y.tolist() == list(values)
        assert curve.opts["skipFiniteCheck"] is True


def test_a_predicted_wash_in_that_stops_ends_in_a_dot_as_the_run_s_does(
    application: QApplication,
) -> None:
    """Previewing the dial at 0% ends the predicted F_A/F_I, and a dot marks the end.

    Without the dot, a predicted stretch that stops would look like one that
    runs on out of view. The run's own trace marks a stop with a dot, so the
    prediction does too (found by the blind review of `PL-5B1N`).
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300)
    frame = _previewing_frame(controller, 0.0, ControlInput.DELIVERED)
    preview = frame.runs[0].preview
    assert preview is not None
    wash_in = _shown(application, WashInChart(), 240)

    wash_in.draw(frame)

    ended = [
        (stretch.times_s[-1], stretch.ratios[-1])
        for stretch in preview.wash_in
        if stretch.ends_above_equilibrium and stretch.times_s
    ]
    assert ended
    # Flatten each side into one list, because pytest.approx rejects nested sequences
    # from pytest 9.2 on (`PL-R74V`). The test compares the lengths first. A missing
    # dot then fails the test, rather than shifting every later value onto the wrong partner.
    drawn = wash_in.preview_terminus_points(0)
    assert len(drawn) == len(ended)
    assert [value for point in drawn for value in point] == pytest.approx(
        [value for point in ended for value in point]
    )

    wash_in.draw(_previewing_frame(controller, 2.0, ControlInput.DELIVERED))

    assert wash_in.preview_terminus_points(0) == ()


def test_a_frame_with_no_preview_takes_the_preview_off_both_plots(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 300)
    chart = _shown(application, ConcentrationChart(), 480)
    wash_in = _shown(application, WashInChart(), 240)
    chart.draw(_previewing_frame(controller, 6.0))
    wash_in.draw(_previewing_frame(controller, 6.0))

    released = _frame(controller)
    chart.draw(released)
    wash_in.draw(released)

    assert all(chart.preview_points(0, q) == ((), ()) for q in COMPARTMENT_QUANTITIES)
    assert wash_in.preview_stretches(0) == ()
    for plot in (chart, wash_in):
        assert plot.preview_region(0) is None
        assert plot.preview_label(0) is None


def test_the_hover_does_not_answer_over_a_predicted_point(application: QApplication) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 300)
    frame = _previewing_frame(controller, 10.0)
    preview = frame.runs[0].preview
    assert preview is not None
    chart = _shown(application, ConcentrationChart(), 480)
    chart.draw(frame)
    index = len(preview.times_s) * 3 // 4

    assert (
        chart.readout_at(preview.times_s[index], preview.percents(RecordedQuantity.ALVEOLAR)[index])
        is None
    )
