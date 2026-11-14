"""The dashboard, driven headless against real runs.

These tests cover the new-case flow.

`simulation_view_support.py` describes the whole suite.
"""

import pytest
from PySide6.QtWidgets import QApplication, QDialog

from anesthesia_sim.app.control_timeline import group_adjustments
from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import (
    KEEP_CURRENT_CASE_TEMPLATE,
    NEW_CASE_CARRYOVER_TEMPLATE,
    NEW_CASE_IS_NOT_A_VIEW_TEXT,
    START_NEW_CASE_TEMPLATE,
    new_case_question,
)
from anesthesia_sim.app.formatting import format_case_discard_warning, format_elapsed
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from tests.integration.simulation_view.simulation_view_support import (
    _advance_to,
    _dials,
    _paused_run_with_history,
    _select_agent,
    _settle,
    _shown_view,
)

# ---------------------------------------------------- the new-case flow


def test_agent_dropdown_handler_switches_the_real_controller(application: QApplication) -> None:
    """A never-started run has nothing to lose, so the switch is immediate."""

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")

    assert controller.snapshot().agent_id == "desflurane"
    assert run._agent_dropdown.currentData() == "desflurane"
    assert "Desflurane" in run._subtitle_text.text()
    assert run._new_case_dialog is None


def test_a_recorded_run_is_not_discarded_before_the_reader_has_answered(
    application: QApplication,
) -> None:
    """`PL-R3KB`: selecting an agent rebuilds nothing until it is confirmed."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    run_before = (controller.snapshot().elapsed_s, controller.run_segments)
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")

    after = controller.snapshot()
    assert after.agent_id == before.agent_id
    assert after.elapsed_s == before.elapsed_s
    assert (controller.snapshot().elapsed_s, controller.run_segments) == run_before
    assert run._new_case_dialog is not None
    assert run._new_case_dialog.isVisible() is True
    # The selector shows the agent that is actually running, not the one
    # being offered, for as long as the question is open.
    assert run._agent_dropdown.currentData() == before.agent_id


def test_an_open_new_case_question_follows_a_running_run(application: QApplication) -> None:
    """The question states what the new case discards as the run stands now (`PL-WM5P`).

    Before the fix, the question was written only once, when it opened, so
    its figure for the run time about to be discarded fell behind the clock.
    Since `PL-TPBH` the run's own ticks hold while the question is open, so
    the test moves the controller directly. The rewrite is kept as a guard
    against any later path that moves a run under an open question.
    """

    controller = _paused_run_with_history(60.0)
    controller.start()
    view = _shown_view(application, controller)
    run = view.runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    opened_warning = dialog.body_labels[1].text()

    _advance_to(controller, 120.0)
    view.present(False)
    snapshot = controller.snapshot()
    question = new_case_question(snapshot, "Desflurane", len(run.adjustments(snapshot)))

    assert dialog.body_labels[1].text() == question.body[1] != opened_warning
    assert format_elapsed(snapshot.elapsed_s) in dialog.body_labels[1].text()
    assert [label.text() for label in dialog.body_labels] == list(question.body)


def test_a_declined_agent_change_leaves_the_run_and_the_selector_untouched(
    application: QApplication,
) -> None:
    """Declining costs nothing: the run, its history and the selector stay as they were."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    run_before = (controller.snapshot().elapsed_s, controller.run_segments)
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    assert dialog.keep_button.text() == KEEP_CURRENT_CASE_TEMPLATE.format(agent="sevoflurane")
    dialog.keep_button.click()

    after = controller.snapshot()
    assert after.agent_id == "sevoflurane"
    assert after.elapsed_s == before.elapsed_s
    assert after.control_timeline == before.control_timeline
    assert (controller.snapshot().elapsed_s, controller.run_segments) == run_before
    assert run._agent_dropdown.currentData() == "sevoflurane"
    assert "Sevoflurane" in run._subtitle_text.text()
    assert dialog.isVisible() is False
    assert run._new_case_dialog is None


def test_a_confirmed_agent_change_starts_the_new_case(application: QApplication) -> None:
    """Confirming does what the selector used to do on its own."""

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    assert dialog.discard_button.text() == START_NEW_CASE_TEMPLATE.format(agent="desflurane")
    dialog.discard_button.click()

    after = controller.snapshot()
    assert after.agent_id == "desflurane"
    assert after.elapsed_s == 0.0
    assert after.control_timeline == ()
    assert run._agent_dropdown.currentData() == "desflurane"
    assert _dials(run)._delivered_concentration_slider.name_label.text() == "Delivered desflurane"
    assert dialog.isVisible() is False
    assert run._new_case_dialog is None


def test_an_agent_chosen_in_the_selector_runs_as_a_fresh_run_of_that_agent(
    application: QApplication,
) -> None:
    """A switch made through the selector computes with the new agent alone (`PL-QJXS`).

    `tests/integration/test_controller.py` compares `set_agent` with a fresh
    run of the new agent for every pair of agents. This test takes the path a
    reader takes: the selector, the new-case dialog and a presented frame. So
    a view that changed agent by some route other than `set_agent`, or wrote
    a control's old value into the new run, fails here.

    The expected run is built directly with desflurane and the same four
    settings, each different from its default. The comparison is exact,
    because both runs take the same steps from the same state.
    """

    settings = {
        "circuit_volume_l": CompartmentVolume(4.5),
        "fresh_gas_flow_l_min": FreshGasFlow(2.5),
        "alveolar_ventilation_l_min": AlveolarVentilation(5.5),
        "cardiac_output_l_min": CardiacOutput(6.5),
    }
    controller = SimulationController(agent_id="sevoflurane", **settings)
    controller.start()
    _advance_to(controller, 90.0)
    controller.pause()
    view = _shown_view(application, controller)
    run = view.runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()
    view.present(False)

    fresh = SimulationController(agent_id="desflurane", **settings)

    for each in (controller, fresh):
        each.start()
        _advance_to(each, 300.0)

    assert fresh.snapshot().alveolar_partial_pressure_fraction > 0.0
    assert controller.snapshot() == fresh.snapshot()


def test_the_dismissal_that_follows_a_confirmed_switch_does_not_undo_it(
    application: QApplication,
) -> None:
    """A dialog reports its close after the button that closed it.

    That report reaches the branch that handles a decline. Without the guard
    in `_resolve_new_case`, that branch would undo the case that had just
    started.
    """

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.accept()

    run._resolve_new_case(False)

    assert controller.snapshot().agent_id == "desflurane"
    assert run._agent_dropdown.currentData() == "desflurane"


def test_dismissing_the_confirmation_keeps_the_current_case(application: QApplication) -> None:
    """A dialog closed by anything but its buttons has chosen nothing."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.reject()

    assert controller.snapshot().agent_id == before.agent_id
    assert controller.snapshot().elapsed_s == before.elapsed_s
    assert run._agent_dropdown.currentData() == before.agent_id
    assert run._new_case_dialog is None


@pytest.mark.parametrize("answer", ["keep", "discard"])
def test_an_answered_confirmation_is_gone_from_the_view_and_its_strings(
    application: QApplication, answer: str
) -> None:
    """A question that has been answered is not part of the interface.

    The dialog is deleted once its `finished` signal has been read. Otherwise
    every confirmation ever asked would stay a child of the run, with its
    title in `interface_strings` and its widgets in every walk of the tree
    (`PL-25KS`).
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    title = dialog.windowTitle()
    assert title in view.interface_strings()

    (dialog.keep_button if answer == "keep" else dialog.discard_button).click()
    _settle(application)

    assert run.findChildren(QDialog) == []
    assert title not in view.interface_strings()
    assert controller.snapshot().agent_id == ("sevoflurane" if answer == "keep" else "desflurane")


def test_a_selection_while_a_confirmation_is_open_does_not_retarget_its_answer(
    application: QApplication,
) -> None:
    """The open dialog names one agent, and its answer starts that agent and no other.

    A second selection while the question is open is reverted and gets no
    dialog. Before the guard, it opened a second dialog and changed the
    pending agent, so the first dialog's discard started the second agent.
    """

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    first = run._new_case_dialog
    assert first is not None

    _select_agent(run, "isoflurane")

    assert run._new_case_dialog is first
    assert run.findChildren(QDialog) == [first]
    assert run._agent_dropdown.currentData() == "sevoflurane"

    first.discard_button.click()

    assert controller.snapshot().agent_id == "desflurane"


def test_reselecting_the_running_agent_discards_nothing_and_asks_nothing(
    application: QApplication,
) -> None:
    """A selector opened and closed on the same option reports a selection."""

    controller = _paused_run_with_history()
    before = controller.snapshot()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "sevoflurane")

    after = controller.snapshot()
    assert after.agent_id == before.agent_id
    assert after.elapsed_s == before.elapsed_s
    assert after.control_timeline == before.control_timeline
    assert run._new_case_dialog is None


def test_the_dialog_quotes_the_time_and_the_changes_the_panel_shows(
    application: QApplication,
) -> None:
    """What is about to be lost is stated in the run's own displayed terms."""

    controller = _paused_run_with_history(elapsed_s=125.0)
    snapshot = controller.snapshot()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    warning = dialog.body_labels[1].text()

    assert warning == format_case_discard_warning(
        "Sevoflurane", snapshot.elapsed_s, len(group_adjustments(snapshot.control_timeline))
    )
    assert format_elapsed(snapshot.elapsed_s) in warning


def test_the_dialog_names_both_agents_and_what_survives_the_switch(
    application: QApplication,
) -> None:
    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    body = [label.text() for label in dialog.body_labels]

    assert dialog.title_label.text() == "Start a new desflurane case?"
    assert body[0] == NEW_CASE_IS_NOT_A_VIEW_TEXT
    assert "sevoflurane" in body[1]
    assert body[2] == NEW_CASE_CARRYOVER_TEMPLATE.format(agent="desflurane")
    assert dialog.isModal() is True


def test_the_open_confirmations_buttons_carry_both_outcomes_and_default_to_keeping(
    application: QApplication,
) -> None:
    """The press a reader makes without reading keeps their case."""

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None

    assert dialog.discard_button.text() == "Discard and start desflurane"
    assert dialog.keep_button.text() == "Keep the sevoflurane case"
    assert dialog.keep_button.isDefault() is True
    assert dialog.discard_button.isDefault() is False
