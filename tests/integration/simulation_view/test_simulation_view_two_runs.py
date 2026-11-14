"""The dashboard, driven headless against real runs.

These tests cover two runs side by side.

`simulation_view_support.py` describes the whole suite.
"""

import pytest
from PySide6.QtCore import QPoint, QRect
from PySide6.QtWidgets import QApplication, QLabel

from anesthesia_sim.app.chart_frame import COMPARED_COMPARTMENT_CAP
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import NO_TRACES_SHOWN_TEXT, SIMULATION_STEP_S
from anesthesia_sim.app.formatting import format_elapsed, format_flow, format_playback_rate
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES, RecordedQuantity
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.view_registry import CONCENTRATION_CHART
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.layout.tree import AreaId
from anesthesia_sim.layout.workspace import WorkspaceName
from tests.integration.simulation_view.simulation_view_support import (
    _LAPTOP_WIDTH_PX,
    _SHOWN_VIEWS,
    _advance,
    _advance_to,
    _branched_case,
    _concentration,
    _delete_shown_views,
    _dials,
    _interface_strings,
    _set_fresh_gas_flow,
    _set_trace_shown,
    _settle,
    _shown_view,
    _steps,
    _take_fork,
    _visible_strings,
    _wash_in,
)

# ------------------------------------------------------------- two runs


def test_two_run_views_drive_two_controllers(application: QApplication) -> None:
    """`PL-B9PY`: two runs, two controllers, and neither shows the other's numbers.

    A regression here would look like one branch's readouts shown over the
    other branch's numbers. That is the wrong-patient-context failure that
    `CLAUDE.md`'s safety-critical standard names.
    """

    lean = SimulationController()
    generous = SimulationController()
    view = _shown_view(application, lean, generous)
    lean_run, generous_run = view.runs

    _set_fresh_gas_flow(lean_run, 1.0)
    _set_fresh_gas_flow(generous_run, 6.0)

    lean.start()
    generous.start()
    _advance_to(lean, 120.0)
    _advance_to(generous, 60.0)
    view.present(False)

    assert lean.snapshot().fresh_gas_flow_l_min == pytest.approx(1.0)
    assert generous.snapshot().fresh_gas_flow_l_min == pytest.approx(6.0)

    lean_flow = _dials(lean_run)._fresh_gas_flow_slider
    generous_flow = _dials(generous_run)._fresh_gas_flow_slider
    assert lean_flow.value_label.text() == format_flow(1.0)
    assert generous_flow.value_label.text() == format_flow(6.0)
    assert lean_run._elapsed_time_text.text() == format_elapsed(120.0)
    assert generous_run._elapsed_time_text.text() == format_elapsed(60.0)

    chart = _concentration(view).chart
    lean_times, lean_percents = chart.drawn_points(0, RecordedQuantity.ALVEOLAR)
    generous_times, generous_percents = chart.drawn_points(1, RecordedQuantity.ALVEOLAR)

    assert lean_percents and generous_percents
    assert lean_times[-1] == pytest.approx(120.0)
    assert generous_times[-1] == pytest.approx(60.0)
    assert lean_percents[-1] != pytest.approx(generous_percents[-1])


def test_each_run_draws_only_its_own_recorded_values(application: QApplication) -> None:
    """The pairing hazard, doubled: a line must carry its run and its compartment.

    The model is linear in partial pressure, so a run at twice the dial
    reaches exactly twice every compartment at every instant. So a line that
    carries the wrong run's values is visible in the drawn points, rather
    than having to be inferred.
    """

    single = SimulationController()
    double = SimulationController()
    double.set_delivered_concentration_percent(Percent(4.0))
    single.start()
    double.start()
    _advance(single, 60.0)
    _advance(double, 60.0)
    view = _shown_view(application, single, double)
    chart = _concentration(view).chart

    frame = chart.frame
    assert frame is not None
    # The check covers every compartment that the cap leaves drawn, because
    # "each run draws its own values" has to be true for each of them. The
    # cap itself has its own test, for `PL-8PSW`.
    assert frame.visible

    for quantity in frame.visible:
        single_times, single_percents = chart.drawn_points(0, quantity)
        double_times, double_percents = chart.drawn_points(1, quantity)

        assert single_percents, f"{quantity} drew nothing on the first run"
        assert single_times == pytest.approx(double_times)
        assert double_percents == pytest.approx(tuple(2.0 * p for p in single_percents), rel=1e-9)


def test_one_compartment_selection_applies_to_every_run(application: QApplication) -> None:
    """`PL-HLD5`: unchecking a compartment takes it off the chart for both runs at once."""

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    _advance(first, 60.0)
    _advance(second, 60.0)
    view = _shown_view(application, first, second)
    chart = _concentration(view).chart
    # One of the two compartments that the cap leaves drawn. So the test
    # checks that the selection applies to both runs, not that the cap
    # removes a trace.
    quantity = RecordedQuantity.ALVEOLAR

    _set_trace_shown(application, view, quantity, False)

    assert chart.drawn_points(0, quantity) == ((), ())
    assert chart.drawn_points(1, quantity) == ((), ())

    _set_trace_shown(application, view, quantity, True)

    assert chart.drawn_points(0, quantity)[0]
    assert chart.drawn_points(1, quantity)[0]


def test_two_runs_cap_the_chart_at_two_compartments_and_say_so(application: QApplication) -> None:
    """`PL-8PSW`: the cap limits the selection, the boxes agree with it, and it is stated.

    The cap is what frees the line width to carry the run. So it is the half
    of the encoding that must stay true whatever a reader does. That includes
    checking a third compartment, which takes the oldest selection off rather
    than being silently ignored.
    """

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    _advance(first, 60.0)
    _advance(second, 60.0)
    single = _shown_view(application, first)

    assert _concentration(single).legend.shown == COMPARTMENT_QUANTITIES
    assert _concentration(single).capped_traces_text.isHidden() is True

    view = _shown_view(application, first, second)
    chart = _concentration(view).chart
    frame = chart.frame

    assert frame is not None
    # With two runs, the selection is reduced from six compartments to the top
    # two of the compartment table.
    assert _concentration(view).legend.shown == (
        RecordedQuantity.CIRCUIT,
        RecordedQuantity.ALVEOLAR,
    )
    assert frame.visible == (RecordedQuantity.CIRCUIT, RecordedQuantity.ALVEOLAR)
    assert _concentration(view).capped_traces_text.isHidden() is False
    assert str(COMPARED_COMPARTMENT_CAP) in _concentration(view).capped_traces_text.text()

    _set_trace_shown(application, view, RecordedQuantity.FAT, True)

    # The third check is honoured and the oldest selection makes room for it,
    # so the boxes never name more curves than the plot draws.
    assert len(_concentration(view).legend.shown) == COMPARED_COMPARTMENT_CAP
    assert RecordedQuantity.FAT in _concentration(view).legend.shown
    assert _concentration(view).chart.frame is not None
    assert _concentration(view).chart.frame.visible == _concentration(view).legend.shown

    for quantity in COMPARTMENT_QUANTITIES:
        drawn = bool(chart.drawn_points(0, quantity)[0])

        assert drawn is (quantity in _concentration(view).legend.shown)


def test_the_window_fits_the_longer_of_two_runs(application: QApplication) -> None:
    """One window, wide enough for both, or one run is compared half-drawn."""

    short = SimulationController()
    long = SimulationController()
    short.start()
    long.start()
    _advance_to(short, 60.0)
    _advance_to(long, 600.0)
    view = _shown_view(application, short, long)
    frame = _concentration(view).chart.frame

    assert frame is not None
    assert frame.stop_s >= 600.0
    assert _wash_in(view).chart.frame is frame
    assert _concentration(view).chart.drawn_points(1, RecordedQuantity.ALVEOLAR)[0][-1] == (
        pytest.approx(600.0)
    )


def test_halting_one_run_leaves_the_other_advancing(application: QApplication) -> None:
    """An exception from one run's step says nothing about the other run."""

    halted = SimulationController()
    untouched = SimulationController()
    halted.start()
    untouched.start()
    view = _shown_view(application, halted, untouched)

    view.runs[0]._halt_run(ValueError("mass balance violated"))

    assert halted.snapshot().failure_reason == "ValueError: mass balance violated"
    assert halted.is_running is False
    assert untouched.has_failed is False
    assert untouched.has_reached_supported_limit is False
    assert untouched.is_running is True

    _steps(view.runs[1], 1)

    assert untouched.snapshot().elapsed_s == SIMULATION_STEP_S


def test_a_frame_that_cannot_be_drawn_halts_every_run(application: QApplication) -> None:
    """The render loop draws every run, so an exception from it belongs to no single run."""

    first = SimulationController()
    second = SimulationController()
    first.start()
    second.start()
    view = _shown_view(application, first, second)

    view._halt_every_run(ValueError("the frame could not be built"))

    assert first.snapshot().failure_reason == "ValueError: the frame could not be built"
    assert second.snapshot().failure_reason == "ValueError: the frame could not be built"
    assert first.is_running is False
    assert second.is_running is False


def test_the_interface_walk_reaches_the_axis_titles_and_the_accessible_names(
    application: QApplication,
) -> None:
    """The whole-interface walk covers what the Flet walk covered: axis titles too.

    The hedge and wake-time tests guarantee only what the walk reaches. The
    plots' axis titles and the legend boxes' accessible names are standing
    text that a reader or a screen reader meets, so both are on the walk
    (`PL-25KS`).
    """

    from anesthesia_sim.app.chart_frame import COMPARTMENT_TRACES
    from anesthesia_sim.app.dashboard_frame import TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE

    view = _shown_view(application, SimulationController())
    strings = set(view.interface_strings())

    assert {"% of 1 atm", "simulated time", "×MAC", "F_A/F_I"} <= strings
    assert {
        TRACE_TOGGLE_ACCESSIBLE_NAME_TEMPLATE.format(label=style.label)
        for style in COMPARTMENT_TRACES
    } <= strings


def test_the_dashboard_carries_the_educational_disclaimer(application: QApplication) -> None:
    """`PL-GMM7`: the educational disclaimer is on the dashboard, verbatim.

    `test_the_educational_disclaimer_says_what_the_tool_is_not` pins the
    words. This test checks that the dashboard places them where a reader
    meets them, at the foot of the page. So the string on which the project's
    regulatory posture rests cannot silently leave the screen.
    """

    from anesthesia_sim.app.dashboard_frame import USE_DISCLAIMER_TEXT

    view = _shown_view(application, SimulationController())

    assert USE_DISCLAIMER_TEXT in view.visible_strings()


@pytest.mark.parametrize("height_px", [700, 900, 1100])
@pytest.mark.parametrize("workspace", ["Default", "Induction", "Maintenance"])
def test_the_region_and_the_use_disclaimer_stay_in_the_viewport(
    application: QApplication, workspace: str, height_px: int
) -> None:
    """The region and the use disclaimer stay in view, however the page scrolls (`PL-NNML`).

    The whole page used to scroll. Measured offscreen on 2026-10-20 at
    1366 px wide, it was 1087 px tall in the Default Workspace and 1505 px in
    Induction and Maintenance. So at these window heights the disclaimer at
    its foot was below the visible part, and scrolling down to it moved the
    region off the top. Now only the part between them scrolls. The test
    checks the window in three states: when it opens, when the scrolling part
    is scrolled to its end, and after a branch is taken, which scrolls to the
    chart. The disclaimer is found by its text, so the test also runs against
    the code before the fix.
    """

    from anesthesia_sim.app.dashboard_frame import USE_DISCLAIMER_TEXT
    from anesthesia_sim.layout.shipped import shipped_workspaces

    case = _branched_case()
    _delete_shown_views(application)
    view = SimulationView((case.trunk,), case=case, workspaces=shipped_workspaces())
    _SHOWN_VIEWS.append(view)
    view.resize(_LAPTOP_WIDTH_PX, height_px)
    view.show()
    application.processEvents()
    view.present(False)
    view.tab_strip.activate(view.workspaces.position_of(WorkspaceName(workspace)))
    _settle(application)
    (disclaimer,) = (
        label for label in view.findChildren(QLabel) if label.text() == USE_DISCLAIMER_TEXT
    )

    def assert_in_view(step: str) -> None:
        window = view.rect()

        for name, widget in (("region", view.unconditional_region), ("disclaimer", disclaimer)):
            placed = QRect(widget.mapTo(view, QPoint(0, 0)), widget.size())
            assert widget.isVisible(), f"{step}: the {name} is hidden"
            assert window.contains(placed), (
                f"{step}: the {name} at {placed} is not inside the {window} window"
            )

    assert_in_view("on opening")

    bar = view._page_scroll.verticalScrollBar()
    bar.setValue(bar.maximum())
    application.processEvents()
    assert_in_view("scrolled to the end")

    _take_fork(view, 60.0)
    _settle(application)
    assert len(view.runs) == 2
    assert_in_view("after taking a branch")


def test_a_value_hidden_from_the_reader_is_not_counted_as_shown(application: QApplication) -> None:
    """A View the reader cannot see is not counted as shown, and a replaced one is gone.

    A plot paints its axis titles itself, so they reach the walk through
    `View.painted_strings` rather than through a label (`PL-TH35`). Each title
    is visible only while the View that paints it is. The walk once counted
    the axis titles as on screen whatever happened to the plot (`PL-904Y`).
    Choosing another View for the chart's Area deletes the chart's View and
    keeps only its saved state, so its strings are no longer held at all, and
    a test that nothing says something still reaches every View that exists.
    The disclaimer is outside the Areas, so it stays visible. The expected
    strings are the concentration plot's axis title and a caption, written
    out here rather than read from the View.
    """

    from anesthesia_sim.app.dashboard_frame import USE_DISCLAIMER_TEXT
    from anesthesia_sim.app.view_registry import WASH_IN

    view = _shown_view(application, SimulationController())
    in_the_chart = {"% of 1 atm", "Clinical references:"}

    assert in_the_chart <= _visible_strings(view)

    chart = _concentration(view)
    chart.hide()

    assert in_the_chart.isdisjoint(_visible_strings(view))
    assert in_the_chart <= _interface_strings(view)

    chart.show()
    view.layout_container.choose_view(AreaId(1), WASH_IN)
    _settle(application)

    assert in_the_chart.isdisjoint(_interface_strings(view))
    assert USE_DISCLAIMER_TEXT in _visible_strings(view)

    view.layout_container.choose_view(AreaId(1), CONCENTRATION_CHART)
    _settle(application)

    assert in_the_chart <= _visible_strings(view)


def test_a_hidden_advisory_and_a_closed_combo_entry_are_held_but_not_shown(
    application: QApplication,
) -> None:
    """Being in the tree and being visible to the reader are two different things (`PL-904Y`).

    The no-traces advisory stays hidden until every trace is off, and a combo
    shows only its current entry. Both strings are in the tree, so a test
    that a string is never said still reaches them. Neither is shown to the
    reader.
    """

    view = _shown_view(application, SimulationController())
    held = _interface_strings(view)
    visible = _visible_strings(view)

    assert NO_TRACES_SHOWN_TEXT in held
    assert NO_TRACES_SHOWN_TEXT not in visible
    assert format_playback_rate(1) in visible
    assert format_playback_rate(60) in held
    assert format_playback_rate(60) not in visible
