"""The dashboard, driven headless against real runs.

These tests cover the readouts, including one readout block at a laptop's width.

`simulation_view_support.py` describes the whole suite.
"""

from collections.abc import Sequence

import pytest
from PySide6.QtWidgets import QApplication, QLabel

from anesthesia_sim.app import control_timeline as control_timeline_module
from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.chart_frame import (
    COMPARED_COMPARTMENT_CAP,
    HOVER_INSTANT_RESOLUTION_S,
    format_trace_hover,
)
from anesthesia_sim.app.control_record import ControlChange
from anesthesia_sim.app.control_timeline import ControlAdjustment
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import (
    INTERPRETATION_DISCLAIMER_TEXT,
    NO_TRACES_SHOWN_TEXT,
    READOUT_PANELS,
    TRUNK_RUN_INDEX,
    ComparedRuns,
    comparing_fork_lock_text,
)
from anesthesia_sim.app.formatting import format_elapsed, format_mac_multiple, format_percent
from anesthesia_sim.app.qt_chart import TraceLegend
from anesthesia_sim.app.qt_widgets import ReadoutRow
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.app.theme import AGENT_SELECTOR_WIDTH, CHART_HEIGHT
from anesthesia_sim.app.unconditional_set import UnconditionalValue
from anesthesia_sim.app.view_registry import CONCENTRATION_CHART, PARAMETER_CONTROLS
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.supported_ranges import FreshGasFlow
from anesthesia_sim.layout.tree import AreaId
from tests.integration.simulation_view.simulation_view_support import (
    _ALVEOLAR_METRIC_QUALIFIER,
    _LAPTOP_WIDTH_PX,
    _TALL_WINDOW_HEIGHT_PX,
    _advance,
    _branched_case,
    _case_view,
    _concentration,
    _failing_assembly,
    _fork_panel,
    _interface_strings,
    _offered_fork_instants,
    _readout_value,
    _set_trace_shown,
    _settle,
    _shown_view,
    _take_fork,
    _wash_in,
)

# ------------------------------------------------------- the readouts


def test_the_readouts_say_they_are_model_outputs_beside_the_values(
    application: QApplication,
) -> None:
    """`PL-2K1R`: the interpretation line sits on the readout section's heading row.

    The line appears once, beside the values it qualifies, rather than at the
    foot of the page, where a repeated disclaimer stops being read.
    """

    run = _shown_view(application, SimulationController()).runs[0]

    assert run._interpretation_text.text() == INTERPRETATION_DISCLAIMER_TEXT
    heading_row = run._interpretation_text.parentWidget()
    assert heading_row is not None
    assert run._compartment_substance_text.parentWidget() is heading_row
    assert run._readout_row.parentWidget() in (heading_row, heading_row.parentWidget()), (
        "the interpretation line is not in the section that holds the readout row"
    )


def test_the_hover_readout_states_the_agent_compartment_and_both_units(
    application: QApplication,
) -> None:
    """`PL-YVHK`: a hover over a drawn point names what it is, in both units.

    The test goes through the dashboard rather than the bare chart, so the
    readout comes from the shipped composition. It checks against the frame
    the dashboard drew, so the readout is the state at which the run was
    evaluated, not a position between two states. A drawn instant belongs to
    a grid column rather than to a step. So the time the readout states is
    the instant rounded to the hover's own resolution, not the column's raw
    time.

    The window is tall enough for the plot's preferred height. At the fixed
    test size the plot is at its least height, where the circuit trace lies
    inside the hover's radius of the alveolar point too, and the readout then
    names both (`PL-CBYS`).
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller, height_px=_TALL_WINDOW_HEIGHT_PX)
    chart = _concentration(view).chart
    assert chart.height() >= CHART_HEIGHT
    frame = chart.frame
    assert frame is not None
    run = frame.runs[0]
    index = len(run.times_s) // 2
    time_s = run.times_s[index]
    fraction = run.fractions[RecordedQuantity.ALVEOLAR][index]

    readout = chart.readout_at(time_s, run.percents(RecordedQuantity.ALVEOLAR)[index])

    assert readout is not None
    assert readout == format_trace_hover(run, RecordedQuantity.ALVEOLAR, index, len(frame.runs))
    context, what, value = readout.splitlines()
    instant_s = round(time_s / HOVER_INSTANT_RESOLUTION_S) * HOVER_INSTANT_RESOLUTION_S
    assert "sevoflurane" in context
    assert format_elapsed(instant_s) in context
    assert "Alveolar" in what
    assert _ALVEOLAR_METRIC_QUALIFIER in what
    assert format_percent(fraction) in value
    assert format_mac_multiple(fraction, controller.snapshot().agent_mac_percent) in value


def test_hiding_a_trace_changes_only_what_is_drawn(application: QApplication) -> None:
    """Unchecking a compartment takes its curve off and touches nothing else."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 120.0)
    view = _shown_view(application, controller)
    # The first frame is drawn before the plot, at its least height in this
    # Workspace, has its settled width: 979 px, against 990 px from the next
    # frame on. So the curves are compared from the second frame (`PL-2NNM`).
    application.processEvents()
    view.present(False)
    run = view.runs[0]
    chart = _concentration(view).chart
    snapshot = controller.snapshot()
    before = {
        quantity: chart.drawn_points(0, quantity)
        for quantity in COMPARTMENT_QUANTITIES
        if quantity is not RecordedQuantity.FAT
    }

    _set_trace_shown(application, view, RecordedQuantity.FAT, False)

    assert chart.drawn_points(0, RecordedQuantity.FAT) == ((), ())

    for quantity, (times, percents) in before.items():
        redrawn_times, redrawn_percents = chart.drawn_points(0, quantity)

        assert redrawn_times == pytest.approx(times)
        assert redrawn_percents == pytest.approx(percents)

    assert _readout_value(run, RecordedQuantity.CIRCUIT) == format_percent(
        snapshot.inspired_partial_pressure_fraction
    )
    assert _readout_value(run, RecordedQuantity.MUSCLE) == format_percent(
        snapshot.muscle_partial_pressure_fraction
    )
    assert _readout_value(run, RecordedQuantity.FAT) == format_percent(
        snapshot.fat_partial_pressure_fraction
    )


def test_the_hidden_traces_advisory_is_present_always_and_shown_only_when_nothing_is_drawn(
    application: QApplication,
) -> None:
    """A plot missing all six is a blank panel, and a blank panel looks like a failure."""

    view = _shown_view(application, SimulationController())

    assert _concentration(view).hidden_traces_text.isHidden() is True
    assert NO_TRACES_SHOWN_TEXT in _interface_strings(view)

    for quantity in COMPARTMENT_QUANTITIES:
        _set_trace_shown(application, view, quantity, False)

    assert _concentration(view).hidden_traces_text.isHidden() is False
    frame = _concentration(view).chart.frame
    assert frame is not None
    assert frame.visible == ()

    _set_trace_shown(application, view, RecordedQuantity.ALVEOLAR, True)

    assert _concentration(view).hidden_traces_text.isHidden() is True


def test_the_compartment_selection_outlives_the_legend_that_renders_it(
    application: QApplication,
) -> None:
    """The dashboard owns the selection, so the legend can go without taking it (`PL-VN6M`).

    The legend sits in the concentration chart's View. A reader closes the
    legend by choosing another View for its Area (`.claude/rules/ui-areas.md`,
    test 2). When the legend's boxes held the selection, the dashboard read
    the selection back from them. So a deleted legend left no selection from
    which to assemble the next frame. Here the chart's View is replaced, which
    deletes the legend. The dashboard still draws the reader's choice on the
    F_A/F_I plot's frame. It also still takes a branch and a Reset. Each of
    those fits the selection to the new run count, with no legend left to
    show the selection to. A chart View brought back, and a legend connected
    afterwards, follow the selection as the first ones did.
    """

    view = _case_view(application, _branched_case())
    legend = _concentration(view).legend

    _set_trace_shown(application, view, RecordedQuantity.FAT, False)
    _set_trace_shown(application, view, RecordedQuantity.MUSCLE, False)

    chosen = view.compartment_selection

    assert chosen.shown == legend.shown
    assert RecordedQuantity.FAT not in chosen.shown

    deleted: list[bool] = []
    legend.destroyed.connect(lambda: deleted.append(True))
    view.layout_container.choose_view(AreaId(1), PARAMETER_CONTROLS)
    _settle(application)

    assert deleted, "the legend was not deleted, so nothing here outlived it"

    presented = view.presented_frames
    view.present(False)

    # `present` turns an exception into a halt rather than letting it escape.
    # So the count is what tells a drawn frame apart from a refused one.
    assert view.presented_frames == presented + 1, "no frame could be drawn without the legend"
    assert view.compartment_selection == chosen

    frame = _wash_in(view).chart.frame

    assert frame is not None
    assert frame.visible == chosen.shown

    _take_fork(view, 60.0)

    assert len(view.runs) == 2
    assert view.runs[1]._run_name_text.isHidden() is False, "the fork stopped part way"
    assert view.compartment_selection == chosen.with_run_count(2)

    compared = _wash_in(view).chart.frame

    assert compared is not None
    assert compared.visible == view.compartment_selection.shown

    view.runs[0]._reset_button.click()
    _settle(application)

    assert len(view.runs) == 1
    assert view.compartment_selection == chosen.with_run_count(2).with_run_count(1)

    view.layout_container.choose_view(AreaId(1), CONCENTRATION_CHART)
    view.present(False)

    assert _concentration(view).legend.shown == view.compartment_selection.shown
    assert _concentration(view).chart.drawn_points(0, RecordedQuantity.FAT) == ((), ())

    renderer = TraceLegend()
    renderer.show_selection(view.compartment_selection)
    view.compartment_selection_changed.connect(renderer.show_selection)
    renderer.compartment_requested.connect(view._handle_compartment_request)

    assert renderer.shown == view.compartment_selection.shown

    renderer.set_compartment_shown(RecordedQuantity.FAT, True)
    application.processEvents()

    assert RecordedQuantity.FAT in view.compartment_selection.shown
    assert renderer.shown == view.compartment_selection.shown

    drawn = _concentration(view).chart.frame

    assert drawn is not None
    assert drawn.visible == renderer.shown


def test_a_legend_click_draws_one_frame_over_the_cap_too(application: QApplication) -> None:
    """A click is a discrete action, so it draws once and at once (`PL-R2YM`).

    The test checks this on one run, and then on two runs. With two runs the
    click goes over the cap, and the selection, not the legend, decides
    which compartment makes room.
    """

    view = _case_view(application, _branched_case())
    presented = view.presented_frames

    _set_trace_shown(application, view, RecordedQuantity.FAT, False)

    assert view.presented_frames == presented + 1

    _take_fork(view, 60.0)
    before = view.compartment_selection
    presented = view.presented_frames

    assert len(before.shown) == COMPARED_COMPARTMENT_CAP

    _set_trace_shown(application, view, RecordedQuantity.FAT, True)

    assert view.presented_frames == presented + 1
    assert view.compartment_selection == before.with_compartment(RecordedQuantity.FAT, True)

    frame = _concentration(view).chart.frame

    assert frame is not None
    assert frame.visible == view.compartment_selection.shown
    assert RecordedQuantity.FAT in frame.visible


def test_a_legend_click_whose_frame_fails_keeps_the_legend_on_the_frame_drawn(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The legend names the curves on the plot even when the frame a click asked for fails.

    A click used to set the selection, hand it to the legend and then ask for
    a frame. So when that frame failed to assemble, the boxes showed the new
    selection over a plot still drawing the old one: fat was unchecked beside
    a fat trace (`PL-G3K7`). The legend is now given the selection that a
    frame was assembled from, once both plots have drawn that frame. A box
    whose request nobody acts on goes back to the selection the legend last
    showed.
    """

    controller = SimulationController()
    controller.start()
    view = _shown_view(application, controller)
    drawn = _concentration(view).chart.frame
    assert drawn is not None
    assert RecordedQuantity.FAT in drawn.visible
    presented = view.presented_frames
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _set_trace_shown(application, view, RecordedQuantity.FAT, False)

    assert controller.has_failed is True
    assert view.presented_frames == presented
    assert _concentration(view).chart.frame is drawn
    assert _concentration(view).legend.shown == drawn.visible


def test_a_trace_above_the_axis_is_reported_on_the_run_that_drew_it(
    application: QApplication,
) -> None:
    """The off-scale notice is a per-run advisory, written from the drawn frame.

    Sevoflurane's 8% dial is 4 MAC against a 3 MAC ceiling: after ten
    minutes the circuit is above the axis and the alveolar trace is inside
    it, so the notice names one and not the other.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    view = _shown_view(application, controller)
    line = _concentration(view).off_scale.lines[0]

    assert line.isHidden() is False
    assert "Circuit" in line.text()
    assert "Alveolar" not in line.text()
    assert "readouts above" in line.text()

    _set_trace_shown(application, view, RecordedQuantity.CIRCUIT, False)

    assert line.isHidden() is True


def test_the_control_timeline_is_not_regrouped_when_it_has_not_grown(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`PL-1PSX`: a frame in which nobody touched a control pays nothing for the record."""

    controller = SimulationController()
    controller.start()

    for index in range(4):
        controller.begin_control_adjustment()
        controller.set_fresh_gas_flow(FreshGasFlow(4.0 - (index + 1) * 0.1))
        _advance(controller, 1.0)

    view = _shown_view(application, controller)

    regroups = 0
    real = control_timeline_module.group_adjustments

    def counted(recorded: Sequence[ControlChange]) -> tuple[ControlAdjustment, ...]:
        nonlocal regroups
        regroups += 1
        return real(recorded)

    monkeypatch.setattr(control_timeline_module, "group_adjustments", counted)

    view.present(False)
    view.present(False)
    view.present(False)

    assert regroups == 0
    # The panel is still written from the grouping, so this is a cache
    # serving the right answer rather than a frame that stopped drawing.
    assert view.runs[0]._control_timeline_text.text().splitlines()[0].startswith("3s")


def test_a_1366_px_window_opens_one_run_s_readout_row_on_seven_columns(
    application: QApplication,
) -> None:
    """The record column takes the sidebar's share, so the readout row has room for seven.

    The test checks against the width the row itself reserves, not a pixel
    figure. So it states the requirement for whatever font renders the
    panels: the row is as wide as seven panels need, and it seats all seven
    across. With the record at the box layout's 3:1 share, the row was 3 px
    short of seven and opened on four (`PL-Z4K6`, `PL-J8K2` Q3).
    """

    view = _shown_view(application, SimulationController(), width_px=_LAPTOP_WIDTH_PX)
    _settle(application)
    row = view.runs[0]._readout_row

    assert row.width() >= row.width_for(len(READOUT_PANELS))
    assert row.columns() == len(READOUT_PANELS)


_SMALL_LAPTOP_WIDTH_PX = 1280


def _seven_or_four_across(row: ReadoutRow) -> None:
    """Check that the row seats seven across where seven fit, and four otherwise.

    At 1280 px the row is within a few pixels of the width that seven across
    needs, so the arrangement depends on the font. Seven across needed 1005 px
    with this container's offscreen font and 1068 px with the CI runner's on
    2026-11-14. Either way, four always fit, so all seven readouts stay on
    screen on at most two lines (`PL-LKX7`).
    """

    assert row.width() >= row.width_for(4)
    expected = len(READOUT_PANELS) if row.width() >= row.width_for(len(READOUT_PANELS)) else 4
    assert row.columns() == expected


def test_a_1280_px_window_opens_one_run_s_readout_row_on_seven_or_four_columns(
    application: QApplication,
) -> None:
    """A 1280 px window shows one run's seven readouts on one line or two, never more.

    `docs/INTERFACE.md` § "The readout row's width condition" states this
    outcome. As in the 1366 px test, the check reads the width that the row
    itself reserves, so it holds for whatever font draws the panels.
    """

    view = _shown_view(application, SimulationController(), width_px=_SMALL_LAPTOP_WIDTH_PX)
    _settle(application)

    _seven_or_four_across(view.runs[0]._readout_row)


def test_a_1280_px_window_opens_two_compared_runs_readout_row_on_seven_or_four_columns(
    application: QApplication,
) -> None:
    """Two compared runs at 1280 px share one readout row, on one line or two.

    In compare mode each run's transport row also carries its delivered
    concentration, which can widen the column the readouts sit in. The shared
    row must still follow the same rule at this width.
    """

    view = _case_view(application, _branched_case(), width_px=_SMALL_LAPTOP_WIDTH_PX)
    _take_fork(view, 60.0)
    _settle(application)
    trunk, branch = view.runs

    assert branch._readout_row.isHidden()
    _seven_or_four_across(trunk._readout_row)


def test_two_runs_share_one_readout_block_whose_values_name_their_runs(
    application: QApplication,
) -> None:
    """Each compartment's panel carries both runs' values, and each value says whose.

    `docs/INTERFACE.md` § "Minimum displayed outputs" pairs the two values under
    one compartment name, so a second run adds lines to the block rather
    than a second row of seven panels. The names are restated as literals
    rather than read from `run_label`, which the legend also reads.
    """

    view = _case_view(application, _branched_case(), width_px=_LAPTOP_WIDTH_PX)
    _take_fork(view, 60.0)
    _settle(application)
    trunk, branch = view.runs
    row = trunk._readout_row

    assert branch._readout_row.isHidden()
    assert row.columns() == len(READOUT_PANELS)

    for panel, compared in zip(row.panels, branch._readout_row.panels, strict=True):
        assert panel.isAncestorOf(compared.value_label), panel.name_label.text()
        assert panel.isAncestorOf(compared.secondary_label), panel.name_label.text()
        assert panel.name_label.text() == compared.name_label.text()
        assert panel.run_name_label.text() == "Run 1"
        assert compared.run_name_label.text() == "Run 2"
        assert panel.run_name_label.isVisible()
        assert compared.run_name_label.isVisible()


def test_dropping_a_branch_takes_its_values_out_of_the_shared_block(
    application: QApplication,
) -> None:
    """The trunk's Reset ends the comparison, and its panels go back to one run's values."""

    view = _case_view(application, _branched_case(), width_px=_LAPTOP_WIDTH_PX)
    labels_alone = [len(panel.findChildren(QLabel)) for panel in view.runs[0]._readout_row.panels]
    _take_fork(view, 60.0)
    _settle(application)

    view.runs[0]._reset_button.click()
    _settle(application)
    (trunk,) = view.runs

    assert [len(panel.findChildren(QLabel)) for panel in trunk._readout_row.panels] == labels_alone
    assert all(panel.run_name_label.isHidden() for panel in trunk._readout_row.panels)
    assert trunk.build_readout_section().isAncestorOf(trunk._delivered_text)
    assert trunk.build_transport_row().isAncestorOf(trunk._agent_header_badge)
    assert trunk._running_agent_display.maximumWidth() == AGENT_SELECTOR_WIDTH
    assert trunk._delivered_text.isVisible()
    assert trunk._agent_header_badge.isVisible()


def test_a_branch_taken_after_a_dropped_one_is_named_by_a_new_number(
    application: QApplication,
) -> None:
    """A run's name comes from its identity, so a later branch is never the dropped one's name.

    Named by drawing position, the second branch to stand beside the trunk was
    "Run 2" again, the same name as the branch the trunk's Reset dropped. A
    Workspace pinned to that dropped branch would then find a run of its name
    and show the new branch's values as if they were the old one's
    (`PL-7Z84`). The trunk keeps its identity through its own Reset.
    """

    view = _case_view(application, _branched_case(), width_px=_LAPTOP_WIDTH_PX)
    _take_fork(view, 60.0)
    _settle(application)
    first_trunk, dropped_branch = (run.run_id for run in view.runs)

    view.runs[TRUNK_RUN_INDEX]._reset_button.click()
    _settle(application)
    (restarted_at_s,) = _offered_fork_instants(view)
    _take_fork(view, restarted_at_s)
    _settle(application)
    trunk, branch = view.runs

    assert trunk.run_id == first_trunk
    assert branch.run_id not in (first_trunk, dropped_branch)
    assert [panel.run_name_label.text() for panel in trunk._readout_row.panels] == ["Run 1"] * len(
        trunk._readout_row.panels
    )
    assert [panel.run_name_label.text() for panel in branch._readout_row.panels] == ["Run 3"] * len(
        branch._readout_row.panels
    )
    assert _fork_panel(view).lock_text.text() == comparing_fork_lock_text(
        ComparedRuns("Run 1", "Run 3")
    )
    assert _wash_in(view).legend._run_names == ("Run 1", "Run 3")


def test_two_compared_runs_take_one_line_each_above_one_shared_heading(
    application: QApplication,
) -> None:
    """Each compared run's controls and delivered concentration share one line, one control high.

    With two runs, each run's transport row and readout heading used to sit
    one above the other. The four lines left the chart about 200 px on the
    1366 by 700 laptop reference (`PL-JG82`). Now the rows are folded
    together. A run's line carries its own delivered concentration, and the
    agent chip puts its caption on the same line as the agent's name. The
    values both runs share are stated once, on the heading line above the
    paired readouts (`PL-QLZ5`). Those values are the substance, the agent's
    1 MAC and the version-and-model badge. The playback-rate selector is the
    tallest control on a run's line, so its height is the limit for one line.
    """

    view = _case_view(application, _branched_case(), width_px=_LAPTOP_WIDTH_PX)
    _take_fork(view, 60.0)
    _settle(application)
    trunk, branch = view.runs
    heading = trunk.build_readout_section()

    for run in view.runs:
        line = run.build_transport_row()

        assert line.isAncestorOf(run._delivered_text)
        assert run._delivered_text.isVisible()
        assert run._delivered_text.text() == "Delivered 2.00% (1.00 ×MAC)"
        assert run._running_agent_display.isVisible()
        assert line.height() <= run._playback_rate_dropdown.height(), "the line is two high"

    assert trunk._running_agent_display.width() == branch._running_agent_display.width()
    assert not branch.build_readout_section().isVisible()
    assert heading.isAncestorOf(trunk._agent_header_badge)
    assert trunk._agent_header_badge.isVisible()
    assert not branch._agent_header_badge.isVisible()
    assert trunk._compartment_substance_text.isVisible()
    assert trunk._one_mac_text.text() == "1 MAC sevoflurane = 2.0%"
    assert trunk._one_mac_text.isVisible()

    for value in (UnconditionalValue.ADMINISTERED_SUBSTANCE, UnconditionalValue.ONE_MAC):
        assert branch.unconditional_widgets()[value] is trunk.unconditional_widgets()[value]
