"""Integration tests for moving a chart's window back through the run, and following it again.

`PL-Z7LY` lets a reader step a chart's window one gridline earlier or later at
a chosen width. A window moved earlier holds still while the run goes on, and
the chart says what it shows and where the run is now. Following the run again
takes one click. These tests drive the buttons on the built dashboard, and they
work out each expected window edge from the ladder's gridline interval rather
than from the frame under test.

The transitions the brief names are each tested: a pause and a resume, a Reset,
an agent change, a branch taken while the window is held, and a second run on
the chart.
"""

import pytest
from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.chart_frame import ChartFrame
from anesthesia_sim.app.chart_time_base import (
    CHART_LIVE_HEADROOM_FRACTION,
    ChartWindow,
    time_base_for_span,
)
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.views import ConcentrationView, WashInView
from tests.integration.simulation_view.simulation_view_support import (
    _advance,
    _branched_case,
    _case_view,
    _concentration,
    _select_agent,
    _select_time_base,
    _settle,
    _shown_view,
    _take_fork,
    _wash_in,
)

# The fifteen-minute width is ruled every 3 minutes (`TIME_BASE_LADDER`).
_SPAN_S = 900
_GRID_S = 180


def _following_start_s(newest_s: int) -> float:
    """The left edge of a fifteen-minute window following a run at `newest_s`, worked out here."""

    return max(0.0, newest_s + _SPAN_S * CHART_LIVE_HEADROOM_FRACTION - _SPAN_S)


def _frame(chart_view: ConcentrationView | WashInView) -> ChartFrame:
    frame = chart_view.chart.frame
    assert frame is not None

    return frame


def _held_view(application: QApplication, controller: SimulationController) -> SimulationView:
    """A dashboard at 50 minutes, with the concentration chart at 15 minutes, stepped back once."""

    controller.start()
    _advance(controller, 3000)
    view = _shown_view(application, controller)
    _select_time_base(view, "900.0")
    _concentration(view)._window.earlier_button.click()

    return view


def test_a_step_earlier_holds_the_window_a_gridline_interval_back(
    application: QApplication,
) -> None:
    """The window moves back to a gridline at least one interval back, and says it is held."""

    view = _held_view(application, SimulationController())
    chart_view = _concentration(view)
    frame = _frame(chart_view)

    # At 3000 s the following window starts at 2118 s. One 180 s interval back
    # is 1938 s, and the gridline at or before it is 10 intervals.
    assert _following_start_s(3000) == 2118.0
    assert (frame.start_s, frame.stop_s) == (1800.0, 2700.0)
    assert frame.held_start_s == 1800
    assert chart_view.frame_request() is not None
    assert chart_view.frame_request().window == ChartWindow(  # type: ignore[union-attr]
        time_base_for_span(900.0), frame.held_start_s
    )
    assert chart_view.chart.time_axis_title.endswith("held: not following the run")
    assert not chart_view._window.held_row.isHidden()
    assert chart_view._window.held_text.text() == "Showing 30m to 45m. The run is now at 50m."
    assert chart_view._window.earlier_button.isEnabled()
    assert chart_view._window.later_button.isEnabled()


def test_a_held_window_stays_put_while_the_run_goes_on(application: QApplication) -> None:
    """New samples do not move a held window, and the line says how far the run has gone."""

    controller = SimulationController()
    view = _held_view(application, controller)
    _advance(controller, 600)
    view.present(False)
    chart_view = _concentration(view)
    frame = _frame(chart_view)

    assert (frame.start_s, frame.stop_s) == (1800.0, 2700.0)
    assert chart_view._window.held_text.text() == "Showing 30m to 45m. The run is now at 1h."


def test_steps_later_reach_the_run_and_follow_it_again(application: QApplication) -> None:
    """A step later that reaches the run's own window follows the run, and the notice goes."""

    view = _held_view(application, SimulationController())
    chart_view = _concentration(view)
    chart_view._window.earlier_button.click()

    assert _frame(chart_view).start_s == 1620.0

    chart_view._window.later_button.click()

    assert _frame(chart_view).start_s == 1800.0

    chart_view._window.later_button.click()

    assert _frame(chart_view).start_s == 1980.0
    assert _frame(chart_view).held

    # The next step, to 2160 s, is past the following window's edge at 2118 s.
    chart_view._window.later_button.click()
    frame = _frame(chart_view)

    assert not frame.held
    assert frame.start_s == pytest.approx(_following_start_s(3000))
    assert chart_view._window.held_row.isHidden()
    assert not chart_view._window.later_button.isEnabled()
    assert chart_view.chart.time_axis_title.endswith("15 minutes shown")


def test_follow_the_run_returns_in_one_click(application: QApplication) -> None:
    view = _held_view(application, SimulationController())
    chart_view = _concentration(view)
    chart_view._window.earlier_button.click()
    chart_view._window.earlier_button.click()

    chart_view._window.follow_button.click()
    frame = _frame(chart_view)

    assert not frame.held
    assert frame.start_s == pytest.approx(_following_start_s(3000))
    assert chart_view._window.held_row.isHidden()


def test_pausing_and_resuming_keeps_the_window_held(application: QApplication) -> None:
    controller = SimulationController()
    view = _held_view(application, controller)

    controller.pause()
    view.present(False)

    assert _frame(_concentration(view)).start_s == 1800.0

    controller.start()
    _advance(controller, 300)
    view.present(False)

    assert _frame(_concentration(view)).start_s == 1800.0
    assert _frame(_concentration(view)).held


def test_a_reset_while_held_follows_the_new_run_and_does_not_hold_it_later(
    application: QApplication,
) -> None:
    """A Reset discards the history the window held, so the chart follows the new run.

    The held edge is dropped, not kept for later. Kept, the window would jump
    back to 30 minutes once the new run passed it, which no reader asked for.
    """

    controller = SimulationController()
    view = _held_view(application, controller)
    run = view.runs[0]
    run._reset_button.click()

    # A run with no setting changed is reset without a question.
    if run._reset_dialog is not None:
        run._reset_dialog.discard_button.click()

    _settle(application)
    view.present(False)

    assert not _frame(_concentration(view)).held
    assert _concentration(view)._window.held_row.isHidden()

    controller.start()
    _advance(controller, 3000)
    view.present(False)
    frame = _frame(_concentration(view))

    assert not frame.held
    assert frame.start_s == pytest.approx(_following_start_s(3000))


def test_an_agent_change_while_held_follows_the_new_case(application: QApplication) -> None:
    """An agent change starts a new case, so the window follows it rather than a discarded past."""

    view = _held_view(application, SimulationController())
    run = view.runs[0]
    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()
    _settle(application)
    view.present(False)
    frame = _frame(_concentration(view))

    assert frame.runs[0].agent_id == "desflurane"
    assert not frame.held
    assert frame.start_s == 0.0
    assert _concentration(view)._window.held_row.isHidden()


def test_a_branch_taken_while_held_keeps_the_window_with_both_runs_on_it(
    application: QApplication,
) -> None:
    """A branch adds a second run to the chart and leaves the reader's held window where it was."""

    case = _branched_case(3000)
    view = _case_view(application, case)
    _select_time_base(view, "900.0")
    chart_view = _concentration(view)
    chart_view._window.earlier_button.click()

    assert _frame(chart_view).start_s == 1800.0

    _take_fork(view, 0.0)
    _settle(application)
    view.present(False)
    frame = _frame(chart_view)

    assert len(frame.runs) == 2
    assert frame.held
    assert (frame.start_s, frame.stop_s) == (1800.0, 2700.0)


def test_neither_arrow_moves_a_fitted_window_and_fit_run_ends_a_hold(
    application: QApplication,
) -> None:
    view = _held_view(application, SimulationController())
    chart_view = _concentration(view)

    _select_time_base(view, "fit")
    frame = _frame(chart_view)

    assert frame.fitted and not frame.held
    assert not chart_view._window.earlier_button.isEnabled()
    assert not chart_view._window.later_button.isEnabled()
    assert chart_view._window.held_row.isHidden()

    # Choosing the width again shows the window that follows the run.
    _select_time_base(view, "900.0")

    assert not _frame(chart_view).held


def test_nothing_earlier_is_offered_before_the_run_starts(application: QApplication) -> None:
    """A run shorter than the width is drawn from zero, so there is nothing earlier to show."""

    controller = SimulationController()
    controller.start()
    _advance(controller, 300)
    view = _shown_view(application, controller)
    _select_time_base(view, "900.0")
    chart_view = _concentration(view)

    assert _frame(chart_view).start_s == 0.0
    assert not chart_view._window.earlier_button.isEnabled()
    assert not chart_view._window.later_button.isEnabled()


def test_the_wash_in_plot_holds_its_own_window(application: QApplication) -> None:
    """Each chart's window is its own (`PL-L59K`), so a hold on one leaves the other following."""

    view = _held_view(application, SimulationController())
    wash_in = _wash_in(view)
    wash_in.time_base_selector.setCurrentIndex(wash_in.time_base_selector.findData("900.0"))

    assert not _frame(wash_in).held
    assert _frame(_concentration(view)).held

    wash_in._window.earlier_button.click()

    assert _frame(wash_in).start_s == 1800.0
    assert wash_in.chart.time_axis_title.endswith("held: not following the run")


def test_a_held_window_is_not_saved(application: QApplication) -> None:
    """A View built again from its saved state follows the run, so no stale window reopens."""

    view = _held_view(application, SimulationController())
    saved = _concentration(view).save_state()

    assert set(saved) == {"state_version", "time_base_s", "ceiling_mac"}
    assert saved["time_base_s"] == 900.0
