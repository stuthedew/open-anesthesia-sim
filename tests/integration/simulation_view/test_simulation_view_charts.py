"""The dashboard, driven headless against real runs.

These tests cover the charts.

`simulation_view_support.py` describes the whole suite.
"""

import pytest
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.chart_time_base import (
    FIT_RUN_KEY,
    SELECTABLE_TIME_BASES,
    time_base_for_span,
)
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.formatting import (
    format_elapsed,
    format_mac_awake_reference,
    format_mac_reference,
    format_time_base,
    format_wash_in_ratio,
)
from anesthesia_sim.app.run_series import RecordedQuantity
from anesthesia_sim.app.view_registry import CONCENTRATION_CHART, PARAMETER_CONTROLS
from anesthesia_sim.app.wash_in import read_wash_in
from anesthesia_sim.core.concentration import MacPercent
from anesthesia_sim.core.parameters import AGENT_DATA_FILENAMES, load_agent_parameters
from anesthesia_sim.core.supported_ranges import FreshGasFlow
from anesthesia_sim.layout.tree import AreaId
from tests.integration.simulation_view.simulation_view_support import (
    _advance,
    _chosen_time_base,
    _concentration,
    _failing_assembly,
    _paused_run_with_history,
    _select_agent,
    _select_time_base,
    _settle,
    _shown_view,
    _wash_in,
)

# ------------------------------------------------ the charts, integrated


def test_the_chart_defaults_to_fitting_the_whole_run(application: QApplication) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 1200.0)
    view = _shown_view(application, controller)
    frame = _concentration(view).chart.frame

    assert _concentration(view).time_base_selector.currentData() == FIT_RUN_KEY
    assert _chosen_time_base(view) is None
    assert frame is not None
    assert frame.fitted is True
    assert frame.start_s == 0.0
    assert frame.stop_s >= 1200.0


def test_the_time_base_selector_offers_fit_run_and_the_settled_widths(
    application: QApplication,
) -> None:
    combo = _concentration(_shown_view(application, SimulationController())).time_base_selector

    assert [combo.itemData(index) for index in range(combo.count())] == [
        FIT_RUN_KEY,
        *(str(time_base.span_s) for time_base in SELECTABLE_TIME_BASES),
    ]
    assert [combo.itemText(index) for index in range(combo.count())] == [
        "Fit run",
        *(format_time_base(time_base.span_s) for time_base in SELECTABLE_TIME_BASES),
    ]


def test_selecting_a_time_base_makes_the_window_exactly_that_wide(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)

    for time_base in SELECTABLE_TIME_BASES:
        _select_time_base(view, str(time_base.span_s))
        frame = _concentration(view).chart.frame

        assert frame is not None
        assert frame.fitted is False
        assert frame.stop_s - frame.start_s == pytest.approx(time_base.span_s)
        assert _chosen_time_base(view) == time_base_for_span(time_base.span_s)


def test_a_run_shorter_than_the_selected_time_base_shows_whole(application: QApplication) -> None:
    """`PL-SSBP`: a chosen width wider than the run draws the run from zero."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)

    _select_time_base(view, "900.0")
    frame = _concentration(view).chart.frame

    assert frame is not None
    assert frame.start_s == 0.0
    assert frame.stop_s == 900.0
    assert _concentration(view).chart.drawn_points(0, RecordedQuantity.ALVEOLAR)[0][0] == (
        pytest.approx(0.0)
    )


def test_both_plots_are_labelled_from_the_same_ticks(application: QApplication) -> None:
    """One frame, both charts: the ticks cannot disagree because there is one list."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 1800.0)
    view = _shown_view(application, controller)

    assert _wash_in(view).chart.frame is _concentration(view).chart.frame
    assert _wash_in(view).chart.axis_ticks("bottom") == _concentration(view).chart.axis_ticks(
        "bottom"
    )


def test_the_two_plots_share_one_frame_while_they_show_the_same_window(
    application: QApplication,
) -> None:
    """Each plot owns its window (`PL-L59K`), and plots at one window draw one frame (`PL-9LNF`)."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _shown_view(application, controller)
    wash_in = _wash_in(view)

    for key in (FIT_RUN_KEY, "900.0", "43200.0"):
        _select_time_base(view, key)
        wash_in.time_base_selector.setCurrentIndex(wash_in.time_base_selector.findData(key))

        assert wash_in.chart.frame is _concentration(view).chart.frame

    _select_time_base(view, "900.0")
    frame = wash_in.chart.frame

    assert frame is not None
    assert frame is not _concentration(view).chart.frame
    assert frame.time_base == time_base_for_span(43200.0)
    assert format_time_base(43200.0) in wash_in.time_axis_caption.text()


def test_the_time_axis_caption_on_screen_states_the_span_and_the_mode(
    application: QApplication,
) -> None:
    """The width is a mode (`PL-012`), so the caption says which and how wide."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 7200.0)
    view = _shown_view(application, controller)
    frame = _concentration(view).chart.frame
    assert frame is not None

    assert "whole run so far" in _concentration(view).time_axis_caption.text()
    assert (
        f"{format_time_base(frame.time_base.span_s)} shown"
        in _concentration(view).time_axis_caption.text()
    )
    assert "simulated seconds" not in _concentration(view).time_axis_caption.text()

    _select_time_base(view, "7200.0")

    assert _concentration(view).time_axis_caption.text() == "2 hours shown"


def test_choosing_a_time_base_changes_nothing_the_run_recorded(application: QApplication) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 20.0)
    view = _shown_view(application, controller)
    recorded = (controller.snapshot().elapsed_s, controller.run_segments)

    for key in (*(str(time_base.span_s) for time_base in SELECTABLE_TIME_BASES), FIT_RUN_KEY):
        _select_time_base(view, key)

        assert (controller.snapshot().elapsed_s, controller.run_segments) == recorded


def test_the_time_base_is_never_disabled(application: QApplication) -> None:
    controller = SimulationController()
    view = _shown_view(application, controller)
    controller.start()
    view.present(False)

    assert view.runs[0]._agent_dropdown.isEnabled() is False
    assert _concentration(view).time_base_selector.isEnabled() is True


def test_a_window_pick_whose_frame_fails_leaves_the_control_on_the_window_drawn(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The control names the window on the plot, not one that never drew (`PL-G3K7`, `PL-L59K`)."""

    controller = _paused_run_with_history(1800.0)
    view = _shown_view(application, controller)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _select_time_base(view, "900.0")

    frame = _concentration(view).chart.frame
    assert frame is not None
    assert frame.fitted is True
    assert _concentration(view).time_base_selector.currentData() == FIT_RUN_KEY


def test_a_frame_is_assembled_and_checked_with_no_chart_shown(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Assembling a frame checks the runs, so a frame is assembled whatever the Areas hold.

    This is `PL-L59K`. With every chart replaced, no View asks for a window. A
    frame is still assembled at "Fit run". So a run state that the assembly
    rejects still halts every run, rather than going unnoticed until a chart
    is shown again.
    """

    view = _shown_view(application, _paused_run_with_history(60.0))

    for area in (AreaId(1), AreaId(3)):
        view.layout_container.choose_view(area, PARAMETER_CONTROLS)

    _settle(application)
    assert view.layout_container.frame_requests() == {}
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)

    assert all(run.controller.has_failed for run in view.runs)


def test_a_chart_s_window_returns_with_the_chart_after_its_area_shows_another_view(
    application: QApplication,
) -> None:
    """A chart's window is the View's own state, saved when the reader replaces it (`PL-L59K`).

    The time-base control sits in the chart View. So a reader closes the
    control only by choosing another View for the chart's Area. Meanwhile the
    F_A/F_I plot keeps its own window. A concentration chart brought back to
    that Area shows the window that the reader chose.
    """

    controller = _paused_run_with_history(1800.0)
    view = _shown_view(application, controller)
    _select_time_base(view, "1800.0")

    view.layout_container.choose_view(AreaId(1), PARAMETER_CONTROLS)
    _settle(application)
    view.present(False)

    frame = _wash_in(view).chart.frame
    assert frame is not None
    assert frame.fitted is True

    view.layout_container.choose_view(AreaId(1), CONCENTRATION_CHART)
    view.present(False)

    assert _chosen_time_base(view) == time_base_for_span(1800.0)
    assert _concentration(view).time_base_selector.currentData() == "1800.0"
    assert format_time_base(1800.0) in _concentration(view).time_axis_caption.text()


def test_reset_leaves_the_selected_time_base_alone(application: QApplication) -> None:
    view = _shown_view(application, SimulationController())

    _select_time_base(view, "1800.0")
    view.runs[0]._reset_button.click()

    assert _chosen_time_base(view) == time_base_for_span(1800.0)
    assert _concentration(view).time_base_selector.currentData() == "1800.0"


def test_the_mac_axis_and_references_follow_the_agent(application: QApplication) -> None:
    """The divisor line, the 1 MAC line and the right axis are the running agent's."""

    controller = SimulationController()
    view = _shown_view(application, controller)
    chart = _concentration(view).chart

    assert _concentration(view).mac_reference_text.text() == format_mac_reference(
        "Sevoflurane", MacPercent(2.0)
    )
    assert chart.one_mac_line() == 2.0
    assert chart.axis_ticks("right")[-1][1] == "3.0"
    assert chart.axis_ticks("right")[-1][0] == pytest.approx(6.0)

    _select_agent(view.runs[0], "desflurane")
    # Read from desflurane's own file, not from the switched run's snapshot,
    # which would agree with a band the switch failed to rebuild (`PL-JPS2`).
    mac_awake = load_agent_parameters("desflurane").mac_awake

    assert _concentration(view).mac_reference_text.text() == format_mac_reference(
        "Desflurane", MacPercent(6.0)
    )
    assert _concentration(view).mac_awake_reference_text.text() == format_mac_awake_reference(
        "Desflurane",
        fraction_of_mac=mac_awake.fraction_of_mac,
        standard_deviation_fraction_of_mac=mac_awake.standard_deviation_fraction_of_mac,
        mac_percent=MacPercent(6.0),
    )
    assert chart.one_mac_line() == 6.0
    assert chart.axis_ticks("right")[-1][1] == "3.0"
    assert chart.axis_ticks("right")[-1][0] == pytest.approx(18.0)


@pytest.mark.parametrize(
    ("previous_agent_id", "agent_id"),
    [
        (previous, chosen)
        for previous in AGENT_DATA_FILENAMES
        for chosen in AGENT_DATA_FILENAMES
        if previous != chosen
    ],
)
def test_the_mac_awake_band_after_a_switch_is_the_new_agents_own(
    application: QApplication, previous_agent_id: str, agent_id: str
) -> None:
    """After a switch, the band and its line of text use the chosen agent's own values.

    A switch keeps the controller. So a band the switch failed to rebuild
    would still hold the previous agent's fraction and spread, and the
    snapshot would agree with the chart. The expected values therefore come
    from the chosen agent's data file, and the test works out the band's
    edges itself (`PL-JPS2`). After a switch from sevoflurane, such a fault
    would draw desflurane's band at 1.74-2.34% instead of 1.78-2.54%.
    """

    view = _shown_view(application, SimulationController(agent_id=previous_agent_id))
    _select_agent(view.runs[0], agent_id)
    own = load_agent_parameters(agent_id)
    fraction = own.mac_awake.fraction_of_mac
    spread = own.mac_awake.standard_deviation_fraction_of_mac

    assert view.runs[0].controller.agent_id == agent_id
    assert _concentration(view).chart.mac_awake_band() == pytest.approx(
        ((fraction - spread) * own.mac_percent, (fraction + spread) * own.mac_percent)
    )
    assert _concentration(view).mac_awake_reference_text.text() == format_mac_awake_reference(
        own.display_name,
        fraction_of_mac=fraction,
        standard_deviation_fraction_of_mac=spread,
        mac_percent=own.mac_percent,
    )


def test_a_recorded_change_is_marked_on_the_chart_at_its_own_time(
    application: QApplication,
) -> None:
    """`PL-DR1Z`: the mark is drawn at the change's instant on both plots."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 600.0)
    controller.begin_control_adjustment()
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))
    _advance(controller, 600.0)
    view = _shown_view(application, controller)

    assert _concentration(view).chart.control_mark_times(0) == (pytest.approx(600.0),)
    assert _wash_in(view).chart.control_mark_times(0) == (pytest.approx(600.0),)
    assert view.runs[0]._control_timeline_text.text().startswith(format_elapsed(600.0))


def test_a_real_run_draws_the_ratio_of_its_own_recorded_compartments(
    application: QApplication,
) -> None:
    controller = SimulationController()
    controller.start()
    _advance(controller, 60.0)
    view = _shown_view(application, controller)
    snapshot = controller.snapshot()
    reading = read_wash_in(
        snapshot.alveolar_partial_pressure_fraction, snapshot.inspired_partial_pressure_fraction
    )
    assert reading.plotted_ratio is not None

    stretches = _wash_in(view).chart.drawn_stretches(0)
    assert stretches
    last_time, last_ratio = stretches[-1][-1]

    assert last_time == pytest.approx(snapshot.elapsed_s)
    assert last_ratio == pytest.approx(reading.plotted_ratio)
    assert format_wash_in_ratio(last_ratio) in _wash_in(view).states.lines[0].text()
