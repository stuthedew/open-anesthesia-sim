"""The dashboard, driven headless against real runs.

These tests cover a run that stops itself (`PL-T995`).

`simulation_view_support.py` describes the whole suite.
"""

import time
from collections.abc import Callable, Mapping
from dataclasses import replace
from typing import Final, NoReturn

import pytest
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QComboBox, QWidget

from anesthesia_sim.app import run_presentation as run_presentation_module
from anesthesia_sim.app import run_view as run_view_module
from anesthesia_sim.app import simulation_view as simulation_view_module
from anesthesia_sim.app.bookmarks import TimeBookmark
from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.controller import (
    BranchedCase,
    RunSettings,
    SimulationController,
    SimulationSnapshot,
)
from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_FAILED_TEXT,
    ACCOUNTING_REJECTED_DETAIL_TEXT,
    BRANCH_RUN_INDEX,
    COMPARING_AGENT_LOCK_TEXT,
    HALT_FORK_LABEL_TEMPLATE,
    NO_CONTROL_CHANGES_TEXT,
    READOUT_PANELS,
    REFUSED_RESET_WAY_OUT_TEXT,
    RESET_EXIT_TEXT,
    SIMULATION_STEP_S,
    STATUS_FAILED_TEXT,
    STATUS_MARK_HALT_TEXT,
    STATUS_SUPPORTED_LIMIT_TEXT,
    TRUNK_RUN_INDEX,
    WITHHELD_CONCENTRATION_TEXT,
    WITHHELD_ELAPSED_TIME_TEXT,
    WITHHELD_MAC_MULTIPLE_TEXT,
    delivered_line,
    halt_notice,
    notice,
    readouts,
    setting_readouts,
    slider_position,
    substance_heading,
)
from anesthesia_sim.app.formatting import (
    FLOW_DISPLAY_DECIMALS,
    format_elapsed,
    format_mac_reference,
    format_playback_rate,
    format_subtitle,
)
from anesthesia_sim.app.playback import DEFAULT_PLAYBACK_RATE
from anesthesia_sim.app.qt_widgets import ParameterSlider
from anesthesia_sim.app.run_series import (
    COMPARTMENT_QUANTITIES,
    COMPARTMENT_STATE_INDEX,
    DrawnWindow,
    RecordedQuantity,
)
from anesthesia_sim.app.run_view import RunView
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.theme import AGENT_COLOR_SCHEMES
from anesthesia_sim.app.view_registry import AGENT_ACCOUNTING
from anesthesia_sim.app.views import AccountingView
from anesthesia_sim.core import supported_ranges as supported_ranges_module
from anesthesia_sim.core.agent_simulation_validation import (
    AgentSimulationValidationResult,
    AgentSimulationValidator,
)
from anesthesia_sim.core.circuit import BreathingCircuit
from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    SimulationConfigurationError,
    SimulationDomainLimitError,
)
from anesthesia_sim.core.supported_ranges import CardiacOutput, CaseInstant
from anesthesia_sim.layout.tree import AreaId
from tests.integration.simulation_view.simulation_view_support import (
    _CARDIAC_OUTPUT_REFUSED_ON_A_STOPPED_RUN,
    _CLOCK_INDEX,
    _REFUSED_ON_A_STOPPED_RUN_TEMPLATE,
    _SETTING_CONTROLS,
    _WINDOW_HEIGHT_PX,
    _accounting_of,
    _accounting_panel,
    _accounting_reading,
    _advance,
    _branched_case,
    _case_view,
    _concentration,
    _dashboard_of,
    _dials,
    _drag,
    _failing_assembly,
    _fork_panel,
    _fresh_run,
    _identity_controls,
    _no_setting,
    _paused_run_with_history,
    _read_the_alveolar_quotient_as,
    _real_step_failure,
    _select_agent,
    _set_fresh_gas_flow,
    _setting_row,
    _settle,
    _shown_view,
    _StepFailingController,
    _steps,
    _take_fork,
    _widest_chord_px,
    _widget_attributes,
    _widget_state,
    _with_stale_tissue_flows,
    _with_the_tissue_fractions_put_back,
    _withheld_accounting,
)

# ------------------------------------------ a run that stops itself (PL-T995)
#
# These tests drive the run through the dashboard's own timers and the Start
# button. A test that steps the controller and presents by hand would draw the
# very frame that this path never asked for.

#: How long a real-timer test waits for its condition before it fails rather
#: than hangs. It is ample beside the half second of play that each test needs.
_REAL_TIMER_BUDGET_S = 10.0

#: Half a second of 1x play past the 60 s at which `_branched_case` pauses, so
#: the step timer reaches it in five ticks.
_TIMED_STOP_S = 60.5


def _render_ticks(view: SimulationView) -> list[None]:
    """A list the dashboard's render timer appends to each time it fires, after `render_tick`."""

    fired: list[None] = []
    view._render_timer.timeout.connect(lambda: fired.append(None))

    return fired


def _run_the_timers_until(condition: Callable[[], bool], what: str) -> None:
    """Let the dashboard's own timers fire until `condition` is true, or fail naming `what`."""

    deadline = time.monotonic() + _REAL_TIMER_BUDGET_S

    while not condition():
        if time.monotonic() > deadline:
            raise AssertionError(
                f"{_REAL_TIMER_BUDGET_S:g} s of the real timers passed without {what}"
            )

        QTest.qWait(10)


def _play_until_it_stops(view: SimulationView, trunk: SimulationController) -> None:
    """Press Start, let the timers play until the trunk stops itself, then one render tick more."""

    ticks = _render_ticks(view)
    view.start_simulation_timer()

    try:
        view.runs[0]._start_button.click()
        _run_the_timers_until(lambda: not trunk.is_running, "the trunk stopping itself")
        ticks.clear()
        _run_the_timers_until(lambda: bool(ticks), "a render tick after the trunk stopped")
    finally:
        view.stop_timers()


def test_a_halt_on_a_mark_is_told_apart_from_a_pause_during_a_comparison(
    application: QApplication,
) -> None:
    """While two runs are compared, a run that a mark stopped is not shown as the learner's Pause.

    The fork control's "stopped on your mark" is withdrawn while two runs are
    compared, and it was the only cue that a mark had stopped the run. A MAC
    target's row reads "reached" from its first crossing, so a later crossing
    changes nothing there either. So a run that a mark stopped read "Paused",
    like a pause that nobody made (`PL-QBQX`). Its status word now says that a
    mark stopped it. The learner's own Pause, and the branch that never ran,
    still read "Paused". The expected words are written here rather than read
    from the module, so a change to them fails this test.
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(_TIMED_STOP_S), "the decision point"))
    view = _case_view(application, case)
    _take_fork(view, 0.0)
    assert len(view.runs) == 2
    trunk, branch = view.runs

    trunk._start_button.click()

    while case.trunk.is_running:
        _steps(trunk, 1)

    view.present(False)

    assert case.trunk.snapshot().bookmark_halt is not None, "the trunk stopped, but not on its mark"
    assert _fork_panel(view).here_button.isHidden() is True
    assert trunk._status_text.text() == "Paused — stopped on your mark"
    assert branch._status_text.text() == "Paused"

    trunk._start_button.click()
    _steps(trunk, 1)
    trunk._pause_button.click()
    view.present(False)

    assert case.trunk.snapshot().bookmark_halt is None
    assert trunk._status_text.text() == "Paused"


def test_a_branch_opened_on_a_mark_crossing_is_not_said_to_be_stopped_by_it(
    application: QApplication,
) -> None:
    """A branch at its fork carries its parent's crossing, but no step of its own stopped it.

    A branch opens standing on the step that reached its fork, so that
    step's crossing is the branch's halt record (`PL-3K9B`). The step was the
    trunk's, though. A status word that read the halt record alone told the
    learner that a mark had stopped a run that never ran, which is the
    misreading `PL-QBQX` set out to remove. The expected words are written
    here rather than read from the module, so a change to them fails this
    test.
    """

    case = _branched_case()
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(_TIMED_STOP_S), "the decision point"))
    view = _case_view(application, case)
    (trunk,) = view.runs

    trunk._start_button.click()

    while case.trunk.is_running:
        _steps(trunk, 1)

    view.present(False)
    _take_fork(view, _TIMED_STOP_S)
    assert len(view.runs) == 2
    branch = view.runs[1]
    view.present(False)

    assert branch.controller.snapshot().bookmark_halt is not None, (
        "the branch does not carry the crossing it opened on, so this test checks nothing"
    )
    assert trunk._status_text.text() == "Paused — stopped on your mark"
    assert branch._status_text.text() == "Paused"


def test_a_run_that_halts_on_a_mark_under_its_own_timers_is_redrawn(
    application: QApplication,
) -> None:
    """A halt inside `step_tick` asks for no frame, and the next render tick draws one anyway.

    The halt changes the run's record, and the tick compares that record with
    what the run's view last wrote (`PL-X7D5`). Before that change, the tick
    drew only while a run was running or a frame was owed. So until the
    learner pressed something, the screen showed "Running" with Pause offered,
    the clock one step short, and no offer to branch where the run stood
    (`PL-T995`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    case.trunk.add_time_bookmark(TimeBookmark(CaseInstant(_TIMED_STOP_S), "the decision point"))

    _play_until_it_stops(view, case.trunk)

    halt = case.trunk.snapshot().bookmark_halt
    assert halt is not None, "the trunk stopped, but not on its mark"
    run = view.runs[0]
    stood_at = format_elapsed(halt.instant_s)

    assert run._status_text.text() == STATUS_MARK_HALT_TEXT
    assert run._readout_row.panels[_CLOCK_INDEX].value_label.text() == stood_at
    assert run._pause_button.isEnabled() is False
    assert run._start_button.isEnabled() is True
    assert _fork_panel(view).here_button.isHidden() is False
    assert _fork_panel(view).here_button.text() == HALT_FORK_LABEL_TEMPLATE.format(instant=stood_at)


def test_a_run_that_arrives_at_the_supported_run_length_under_its_own_timers_is_redrawn(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The other stop that `step_tick` makes without an exception is drawn the same way.

    `SimulationController.advance` halts a run on the step that lands it on
    the supported run length, and raises nothing. So `RunView._halt_run`, the
    one branch of `step_tick` that asked for a frame, is never reached
    (`PL-T995`). The span is shortened to end half a second past the trunk's
    pause. The timers would take a day to reach the real span, and stepping a
    run to one step short of it takes about 27 s. `maximum_step_count` is the
    one count from which the controller and the core both read the span, so
    the two agree on the shortened span. Where a run stops on the real span is
    tested by
    `test_a_run_standing_on_the_supported_run_length_reads_as_stopped_from_the_arriving_step`.
    """

    case = _branched_case()
    view = _case_view(application, case)
    last_step = round(_TIMED_STOP_S / SIMULATION_STEP_S)
    monkeypatch.setattr(
        supported_ranges_module, "maximum_step_count", lambda simulation_step_s: last_step
    )

    _play_until_it_stops(view, case.trunk)

    assert case.trunk.has_reached_supported_limit is True
    run = view.runs[0]

    assert run._status_text.text() == STATUS_SUPPORTED_LIMIT_TEXT
    assert run._readout_row.panels[_CLOCK_INDEX].value_label.text() == format_elapsed(_TIMED_STOP_S)
    assert run._pause_button.isEnabled() is False
    assert run._start_button.isEnabled() is False
    assert run._notice_text.notice() is not None


def test_a_frame_that_keeps_failing_is_attempted_once_not_every_tick(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The halt stores the record it shows, so the comparison does not halt the run on every tick.

    A frame that raises halts every run, and the screen then shows the halt.
    If a run's record were stored only where a frame is drawn, the failed run
    would differ from its view's record on every later tick. The tick would
    then assemble, fail and halt again five times a second for as long as the
    dashboard stayed open (`PL-X7D5`). The two attempts are the tick's own
    attempt and the one retry that `SimulationView._halt_every_run` makes.
    """

    case = _branched_case()
    view = _case_view(application, case)
    attempts: list[None] = []

    def failing_assembly(*args: object, **kwargs: object) -> NoReturn:
        attempts.append(None)
        raise RuntimeError("this frame could not be assembled")

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", failing_assembly)
    ticks = _render_ticks(view)
    view.start_simulation_timer()

    try:
        case.trunk.start()
        _run_the_timers_until(lambda: case.trunk.has_failed, "the failing frame halting the run")
        attempted = len(attempts)
        ticks.clear()
        _run_the_timers_until(lambda: len(ticks) >= 5, "five render ticks after the halt")
    finally:
        view.stop_timers()

    assert attempted == 2
    assert len(attempts) == attempted, "the failed frame was attempted again on a later tick"
    assert view.runs[0]._status_text.text() == STATUS_FAILED_TEXT


def test_a_halt_is_shown_when_the_snapshot_itself_is_refused(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt shown from a fresh snapshot is not shown at all when the snapshot itself refused.

    `snapshot()` builds every compartment's fraction. So an alveolar quotient
    above 1 refuses the snapshot and, through it, the frame. The test gets
    that quotient by replacing what the compartment returns. No supported
    setting produces one (`core/concentration.py`), and a write larger than
    the capacity is refused (`PL-544D`). `show_presentation` used to read a
    fresh snapshot for the status word, the transport and the banner
    (`PL-7DJK`). So the same refusal escaped the render tick, with the
    controller failed and the screen showing "Running", Pause offered and no
    banner. The three are now written from `SimulationController.record()`,
    which builds no compartment value. The banner says that no frame of the
    stopped run could be drawn, not that a step was rolled back.
    """

    controller = SimulationController()
    controller.start()
    view = _shown_view(application, controller)
    view.render_tick()

    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)

    view.render_tick()

    reason = (
        "SimulationConfigurationError: alveolar partial_pressure_fraction of 1.0000001 is "
        "outside 0 to 1"
    )
    status = controller.status()

    assert controller.is_running is False
    assert controller.has_failed is True
    assert status.failure_reason is not None
    assert status.failure_reason.startswith(reason)

    with pytest.raises(SimulationConfigurationError, match="alveolar partial_pressure_fraction"):
        controller.snapshot()

    run = view.runs[0]

    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.startswith(f"Simulation stopped — {reason}")
    assert "No frame of the stopped run could be drawn" in notice
    assert "rolled back" not in notice
    assert run._pause_button.isEnabled() is False
    assert run._start_button.isEnabled() is False


def test_an_agent_change_on_a_halted_run_restates_the_halt(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """A pick on a run halted by its own snapshot gets that halt, not an exception Qt prints.

    Inside a slot, `_handle_agent_change` reads the snapshot to choose between
    doing nothing, starting a new case and asking a question. On a run whose
    snapshot refuses (`PL-7DJK`), the read raised there. So the toolkit
    printed the traceback, and the pick was accepted with nothing on screen
    responding to it. No dialog appeared, and the selector named an agent
    that the run does not use (`PL-V2HC`). Now the exception from the read
    halts the run, and the halt is restated. That is the halt the run is
    already in, and the controller keeps its first reason. The selector is
    put back to the running agent, which the controller names because the
    snapshot cannot. Reset is still the way out that the banner names.
    """

    controller = SimulationController()
    controller.start()
    view = _shown_view(application, controller)
    view.render_tick()
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)
    view.render_tick()
    run = view.runs[0]
    reason = (
        "SimulationConfigurationError: alveolar partial_pressure_fraction of 1.0000001 is "
        "outside 0 to 1"
    )
    assert run._status_text.text() == "Stopped — simulation error"
    capfd.readouterr()

    _select_agent(run, "desflurane")

    assert "Traceback" not in capfd.readouterr().err
    assert run._new_case_dialog is None
    assert run._agent_dropdown.currentData() == "sevoflurane"
    assert controller.agent_id == "sevoflurane"
    status = controller.status()
    assert status.failure_reason is not None
    assert status.failure_reason.startswith(reason)
    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.startswith(f"Simulation stopped — {reason}")
    assert run._start_button.isEnabled() is False
    assert run._reset_button.isEnabled() is True


def test_a_slider_moved_on_a_run_whose_snapshot_refuses_halts_it(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """A dragged slider's immediate labels come from the snapshot, so its refusal halts the run.

    After a coalesced change, `_apply_setting` rewrites this run's own labels from a
    snapshot that it reads after applying the setting. Before `PL-HJKN`, that read
    happened outside the `try` block that applied the setting. So on a paused run whose
    snapshot refuses (`PL-7DJK`), the drag was accepted and the read raised an exception
    that escaped the slot. The dial moved, and the status word showed "Paused" over a
    run that no frame could draw. The toolkit printed an error, but nothing on screen
    reported it (`PL-V2HC`). The read now halts the run and shows the halt from the
    controller's status. In this test, the read is the first place where the halt is
    shown, because a paused run draws no frame that could refuse.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]
    assert run._status_text.text() == "Paused"
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)
    capfd.readouterr()

    _set_fresh_gas_flow(run, 4.0)

    assert "Traceback" not in capfd.readouterr().err
    reason = (
        "SimulationConfigurationError: alveolar partial_pressure_fraction of 1.0000001 is "
        "outside 0 to 1"
    )
    status = controller.status()
    assert controller.has_failed is True
    assert status.failure_reason is not None
    assert status.failure_reason.startswith(reason)
    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.startswith(f"Simulation stopped — {reason}")
    assert run._pause_button.isEnabled() is False
    assert run._start_button.isEnabled() is False


def test_a_drag_that_halts_the_run_leaves_its_label_on_the_dial(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """The value printed beside a dial dragged into a halt is the value the dial and the run hold.

    `_apply_setting` applies the setting. Then the snapshot read that would
    rewrite the labels halts the run instead, and no frame is drawn. The
    value label is written only through `set_setting`. So it kept the value
    from before the drag, beside a dial set at the new value: "2.0 L/min"
    beside a dial at 4.0, with the circuit holding 4.0, until Reset
    (`PL-85LJ`, found at `PL-V2HC`'s review). The halt now writes every dial
    from `SimulationController.record()`, which builds no compartment value,
    so the label, the dial and the run agree.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]
    dial = _dials(run)._fresh_gas_flow_slider
    assert dial.value_label.text() == "2.0 L/min"
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)
    capfd.readouterr()

    _set_fresh_gas_flow(run, 4.0)

    assert "Traceback" not in capfd.readouterr().err
    assert controller.has_failed is True
    assert run._status_text.text() == "Stopped — simulation error"
    assert controller.settings().fresh_gas_flow_l_min == 4.0
    assert dial.value() == 4.0
    assert dial.value_label.text() == "4.0 L/min"


def test_a_halt_is_stated_before_its_dials_are_written(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The status word, the transport and the banner are on screen before a dial is written.

    `show_presentation` writes the dials through `dashboard_frame.setting_readouts`.
    That function raises for a control that can offer no setting, such as a
    fresh gas flow range narrower than the dial's 0.1 L/min step. No shipped
    machine declares such a range. The circuit does not refuse one when it is
    built: `_require_the_two_flow_claims_overlap` in `core/circuit.py`
    refuses only an empty overlap, so a narrow range reaches
    `setting_readouts`. When the dials were written before the banner, that
    exception left the halt half shown: the status word and the transport
    were written, but no banner was. The exception also escaped the slot
    (found at `PL-85LJ`'s review). The dials now come last, so the three
    signs of the halt are on screen before the exception. The exception
    still escapes rather than being hidden.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]
    monkeypatch.setattr(
        BreathingCircuit,
        "accepted_fresh_gas_flow_range_l_min",
        property(lambda circuit: (0.21, 0.29)),
    )
    controller.fail("RuntimeError: step exploded")

    with pytest.raises(ValueError, match="can offer no setting"):
        run.show_presentation(run.presentation())

    assert run._status_text.text() == "Stopped — simulation error"
    assert run._start_button.isEnabled() is False
    assert run._pause_button.isEnabled() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert "Simulation stopped" in notice
    assert "step exploded" in notice
    assert run.owes_a_frame is False


def test_a_halt_after_an_agent_change_names_one_agent(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A run halted on the first frame after an agent change names that agent everywhere.

    A run that has recorded nothing switches agent at once on a pick, so the
    frame that follows is the first to show the new agent. When that frame
    fails, `show_presentation` is the only writer. It used to write the dials but
    nothing of the agent's identity. The screen showed "Delivered desflurane"
    under a subtitle, a chip and a heading that still named sevoflurane, in
    sevoflurane's colours (`PL-1YDD`). `show_presentation` now writes every
    identity widget from the controller's record.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    scheme = AGENT_COLOR_SCHEMES["desflurane"]

    _select_agent(run, "desflurane")

    assert controller.agent_id == "desflurane"
    assert controller.has_failed is True
    assert run._status_text.text() == STATUS_FAILED_TEXT
    assert _dials(run)._delivered_concentration_slider.name_label.text() == "Delivered desflurane"
    assert run._subtitle_text.text() == format_subtitle("Desflurane")
    assert run._running_agent_text.text() == "Desflurane"
    assert run._compartment_substance_text.text() == "Modelled concentrations: Desflurane"
    assert run._agent_dropdown.currentData() == "desflurane"

    for control in _identity_controls(run):
        assert scheme.fill in control.styleSheet(), control
        assert scheme.foreground in control.styleSheet(), control


def test_a_halt_after_an_agent_change_shows_no_mac_multiple_beside_another_agent_s_1_mac(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`PL-6RJ0`: every ×MAC number on screen was divided by the 1 MAC the line states.

    A halt writes the 1 MAC line and the delivered line from the controller's
    record, while only a frame writes the cards. So a halt on the first frame
    after an agent change left the cards holding sevoflurane's multiples,
    divided by 2.0%. Before `PL-6RJ0`, the 1 MAC line above them stated
    desflurane's 6.0%. Its first fix wrote the line together with the cards,
    so the line then stated sevoflurane's 2.0% beside a delivered line divided
    by 6.0%. The line now
    follows the record on both the frame path and the halt path, and the halt
    withholds the cards' multiples.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    drawn = controller.snapshot()
    sevoflurane_line = format_mac_reference(drawn.agent_display_name, drawn.agent_mac_percent)
    cards_before = [panel.value_label.text() for panel in run._readout_row.panels]

    assert run._one_mac_text.text() == sevoflurane_line

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    _select_agent(run, "desflurane")

    record = controller.record()
    assert controller.agent_id == "desflurane"
    assert controller.has_failed is True
    assert run._one_mac_text.text() == format_mac_reference(
        record.agent_display_name, record.agent_mac_percent
    )
    assert run._one_mac_text.text() == "1 MAC desflurane = 6.0%"
    # No card keeps sevoflurane's percent under the desflurane heading, or its multiple
    # under desflurane's 1 MAC (`PL-J5GC`). The clock is withheld with the cards, because
    # it states their instant (adversarial review of `PL-J5GC`).
    clock = run_view_module._CLOCK_PANEL_INDEX
    assert cards_before[clock] == "0s"
    assert run._readout_row.panels[clock].value_label.text() == "\u2014"

    for index, panel in enumerate(run._readout_row.panels):
        if index != clock:
            assert panel.value_label.text() == "\u2014%"
            assert panel.secondary_label.text() == "\u2014 \u00d7MAC"

    monkeypatch.undo()
    view_frame = run._readout_row.panels
    run.show_presentation(run.presentation(controller.snapshot()))

    assert all(panel.secondary_label.text() != "\u2014 \u00d7MAC" for panel in view_frame), (
        "the first frame that draws writes every card's multiple again"
    )


def test_a_halt_on_the_first_frame_still_states_the_1_mac_line(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`PL-6RJ0`: the 1 MAC line is an unconditional value, so the halt path writes it too.

    The cards were built from the run's first snapshot. Their multiples were
    therefore divided by the MAC of the run's own agent, and the cards keep them.
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    run._one_mac_text.setText("")
    monkeypatch.setattr(controller, "_failure_reason", "the first frame failed")

    run.show_presentation(run.presentation())

    record = controller.record()
    assert run._one_mac_text.text() == format_mac_reference(
        record.agent_display_name, record.agent_mac_percent
    )
    assert all(
        panel.secondary_label.text() != "\u2014 \u00d7MAC" for panel in run._readout_row.panels
    )


def test_a_drag_that_halts_the_run_lists_the_record_the_run_holds(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The control-change panel of a run halted by a drag lists the changes the run holds.

    `_paused_run_with_history` leaves the fresh gas flow change it records
    open, so dragging the dial back to where it started takes that change off
    the record. On a run whose snapshot refuses, the drag halts the run and
    no frame is drawn. The panel then went on listing the change that the run
    no longer held (`PL-DTJQ`). The halt now writes the panel from the
    controller's record. It writes no undrawn marks, because no frame was
    drawn.
    """

    controller = _paused_run_with_history()
    run = _shown_view(application, controller).runs[0]
    assert run._control_timeline_text.text() != NO_CONTROL_CHANGES_TEXT
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)

    _set_fresh_gas_flow(run, 4.0)

    assert controller.has_failed is True
    assert run._status_text.text() == STATUS_FAILED_TEXT
    assert controller.record().control_timeline == ()
    assert run._control_timeline_text.text() == NO_CONTROL_CHANGES_TEXT
    assert run._control_timeline_overflow_text.isHidden() is True


#: The widget attributes of a `RunView` that may show different content on a
#: run drawn by a frame and on the same run halted with every frame failing.
#: Each is mapped to the reason it may differ. The test below requires every
#: other widget attribute, including one added later, to show the same content
#: on both runs. That requirement keeps `RunView.show_presentation` the one
#: writer of a run's state, with no list of widgets for somebody to maintain.
#: A widget left out of `show_presentation` still shows the last frame's run on
#: a halt, and the test fails there (`PL-X7D5`).
#:
#: The list is checked in both directions, as `FOREGROUND_NOT_DECLARED` is. An
#: entry that names no widget attribute fails. So does an entry whose widget
#: shows the same content on the two runs, because nothing then needs the
#: exemption. The accounting panel's status and detail lines are frame
#: widgets, but they are not listed. Both runs below show "Valid" there, so
#: the comparison checks them like any other widget.
FRAME_WIDGETS: dict[str, str] = {
    "_readout_row": (
        "the readouts and the clock they were read with, from the compartment "
        "values of the snapshot a frame drew from. The clock stays with its "
        "readouts, so no row pairs one instant's clock with another's values. "
        "The playback line under the clock is run state, and the test below "
        "compares it on its own (`PL-P58M`)."
    ),
    "<accounting panel>._agent_amounts_text": (
        "the accounting panel's amounts, which are the snapshot's mass balance "
        "and so compartment values."
    ),
    "<accounting panel>._agent_accounting_status_text": (
        "the verdict on those amounts, which only a frame states. A halt that no frame "
        "has drawn since the run started over withholds it with the amounts, because it "
        "judged the discarded run (blind and adversarial reviews of `PL-J5GC`)."
    ),
    "<accounting panel>._agent_accounting_detail_text": (
        "the sentence under the verdict, which a halt withholds with it."
    ),
    "_notice_text": (
        "the banner. `show_presentation` writes it on both paths, worded for "
        "whether a frame drew: `halt_notice` says no frame has been drawn, and "
        "`notice` says the values shown are the last completed step. "
        "The test below holds each to its own wording."
    ),
}


def _stated(widget: QWidget, attributes: set[int]) -> tuple[tuple[object, ...], ...]:
    """One widget attribute as a reader sees it, with each widget under it that no attribute names.

    A combo box's popup is left out. It belongs to the toolkit, and it shows
    what the combo's own entries say.
    """

    states = [_widget_state(widget)]

    if isinstance(widget, QComboBox):
        return tuple(states)

    for child in widget.children():
        if isinstance(child, QWidget) and id(child) not in attributes:
            states.extend(_stated(child, attributes))

    return tuple(states)


def test_every_run_state_widget_reads_alike_on_a_drawn_run_and_a_halted_one(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A halt shows the run on every widget a frame would, by default rather than by a list.

    The run is drawn. Then, with every frame failing, it is changed in every
    way that a run-state widget shows, so the halt is the only writer of what
    the screen says. There are three changes. A new agent starts a new case
    with no control changes. The delivered dial is renamed. The frame fails
    the run. That screen is compared, widget attribute by widget attribute,
    with the same run once a frame draws it. It is one state, written once
    from the halt's presentation and once from the frame's. Before both went
    through one writer, the halt wrote four widgets and a dial row. The agent
    identity and the control-change panel went on showing the run that the
    last frame drew (`PL-1YDD`, `PL-DTJQ`, `PL-X7D5`).

    Every widget attribute is compared unless `FRAME_WIDGETS` names it. So a
    widget added to `RunView` later is checked here without being listed.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    controller.pause()
    view = _shown_view(application, controller)
    run = view.runs[0]
    assert _concentration(view).off_scale.lines[0].isHidden() is False, (
        "no trace is above the axis to go stale"
    )
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()

    assert controller.agent_id == "desflurane"
    assert controller.has_failed is True
    # The playback line is in `_readout_row`, which `FRAME_WIDGETS` exempts,
    # so it is compared on its own below (`PL-P58M`).
    run._playback_rate_dropdown.setCurrentIndex(run._playback_rate_dropdown.findData(5))
    halted_playback_line = run._playback_rate_text.text()
    attributes = _widget_attributes(run)
    named = {id(widget) for widget in attributes.values()}
    halted = {name: _stated(widget, named) for name, widget in attributes.items()}
    halted_banner = run._notice_text.notice()

    monkeypatch.undo()
    view.present(False)

    drawn = {name: _stated(widget, named) for name, widget in attributes.items()}
    differing = {name for name in attributes if halted[name] != drawn[name]}

    assert sorted(set(FRAME_WIDGETS) - set(attributes)) == [], (
        "FRAME_WIDGETS names a widget RunView no longer holds - remove the entry"
    )
    assert sorted(differing - set(FRAME_WIDGETS)) == [], (
        "these widgets read differently on a halted run and on the same run drawn: write "
        "them in RunView.show_presentation, or name them in FRAME_WIDGETS with the reason "
        "only a frame can state them"
    )
    assert sorted(set(FRAME_WIDGETS) - differing) == [], (
        "these widgets read alike on a halted run and a drawn one now, so their exemption "
        "is stale - remove the entry"
    )
    # The agent change started the run over, so the halt's banner says the readouts are
    # withheld rather than showing the last frame (adversarial review of `PL-J5GC`).
    assert halted_banner == halt_notice(controller.record(), started_over=True)
    assert run._notice_text.notice() == notice(controller.snapshot(), None)
    assert halted_playback_line == run._playback_rate_text.text() == format_playback_rate(5)


#: The groups of run-screen widgets that state one value together with the
#: labels, divisors and verdicts that qualify it. Each group lists its members
#: by the names `_widget_attributes` gives them. The test below requires every
#: member of a group to describe one step of the run: the step that each
#: scenario names for that group (`PL-J5GC`).
#:
#: In the readouts group, `_readout_row` stands for its six compartment cards,
#: each with its percent and its ×MAC line, and for the clock's value line. The
#: heading names the substance of those cards, the 1 MAC line states the divisor
#: of their ×MAC lines, and the clock states their instant. Until the adversarial
#: review of `PL-J5GC` the clock was left out, and a halt after a Reset kept the
#: discarded run's instant. The playback line under the clock is a setting of the
#: view, so it is not a member.
VALUE_GROUPS: dict[str, tuple[str, ...]] = {
    "readouts": ("_readout_row", "_compartment_substance_text", "_one_mac_text"),
    "settings": (
        "<setting controls>._fresh_gas_flow_slider",
        "<setting controls>._delivered_concentration_slider",
        "<setting controls>._alveolar_ventilation_slider",
        "<setting controls>._cardiac_output_slider",
        "<setting row>.not_shown_text",
        "_delivered_text",
    ),
    "accounting": (
        "<accounting panel>._agent_accounting_status_text",
        "<accounting panel>._agent_accounting_detail_text",
        "<accounting panel>._agent_amounts_text",
    ),
}

_NAMES_THE_AGENT = (
    "names the run's agent. `show_presentation` writes it from the same record as "
    "`_compartment_substance_text`, and the test above holds it to that record"
)
_HOLDS_OTHER_WIDGETS = "holds other widgets, and each of them is listed under its own name"
_STATES_THE_RECORD = (
    "states the run's record or status, which the test above holds to the record on both paths"
)

#: Every other widget attribute of a `RunView`, each with the reason it is in no
#: group. The two tables together are checked against `_widget_attributes` in
#: both directions, as `FRAME_WIDGETS` is. So a widget added to `RunView` later
#: fails the test below until it is put in a group or listed here.
UNGROUPED_WIDGETS: dict[str, str] = {
    "_run_name_text": "names the run while a second run is drawn, from `set_run_name`",
    "_status_text": _STATES_THE_RECORD,
    "_notice_text": (
        "the banner, which says which step the values on screen describe. `notice` and "
        "`halt_notice` word it, and their own tests check the wording"
    ),
    "_subtitle_text": _NAMES_THE_AGENT,
    "_agent_header_badge": _NAMES_THE_AGENT,
    "_agent_dropdown": _NAMES_THE_AGENT,
    "_running_agent_text": _NAMES_THE_AGENT,
    "_running_agent_display": _HOLDS_OTHER_WIDGETS,
    "_running_agent_lock_text": "says why the agent cannot be changed, and states no value",
    "_start_button": _STATES_THE_RECORD,
    "_pause_button": _STATES_THE_RECORD,
    "_reset_button": _STATES_THE_RECORD,
    "_playback_rate_dropdown": "the playback rate, a setting of the view, not of the run",
    "_interpretation_text": "a standing disclaimer, the same on every run",
    "<setting controls>": _HOLDS_OTHER_WIDGETS,
    "<accounting panel>": _HOLDS_OTHER_WIDGETS,
    "<accounting panel>._accounting_heading_text": (
        "the panel's heading, which names the run while a second run is drawn"
    ),
    "_control_timeline_heading_text": "a standing heading",
    "_control_timeline_text": _STATES_THE_RECORD,
    "_control_timeline_overflow_text": _STATES_THE_RECORD,
    "_transport_row": _HOLDS_OTHER_WIDGETS,
    "_readout_section": _HOLDS_OTHER_WIDGETS,
    "_control_record_panel": _HOLDS_OTHER_WIDGETS,
}

#: What a reader sees of each group in `VALUE_GROUPS`, member by member.
_GroupReadings = dict[str, dict[str, object]]


def _shown_readouts(run: RunView) -> dict[str, object]:
    shown: dict[str, object] = {
        "heading": run._compartment_substance_text.text(),
        "1 MAC": run._one_mac_text.text(),
    }

    for index, panel in enumerate(run._readout_row.panels):
        if index == _CLOCK_INDEX:
            shown["clock"] = panel.value_label.text()
        else:
            shown[f"card {index}"] = (panel.value_label.text(), panel.secondary_label.text())

    return shown


def _shown_settings(run: RunView) -> dict[str, object]:
    """What a reader sees of a run's settings: each dial, or the line in their place.

    The dials are counted across the whole dashboard, so a dial that the
    View no longer lists but has not deleted is still read.
    """

    row = _setting_row(run)
    shown: dict[str, object] = {}

    if row.controls is None:
        shown["no dials"] = (
            [dial.name_label.text() for dial in _dashboard_of(run).findChildren(ParameterSlider)],
            row.not_shown_text.isHidden(),
            row.not_shown_text.text(),
        )
    else:
        assert row.not_shown_text.isHidden()
        shown.update(
            {
                f"dial {index}": (
                    slider.name_label.text(),
                    slider.qualifier_label.text(),
                    slider.slider.minimum(),
                    slider.slider.maximum(),
                    slider.slider.value(),
                    slider.value_label.text(),
                    slider.secondary_label.text(),
                )
                for index, slider in enumerate(row.controls.sliders)
            }
        )

    shown["delivered line"] = run._delivered_text.text()

    return shown


def _shown_accounting(run: RunView) -> dict[str, object]:
    return _accounting_reading(_accounting_panel(run))


_SHOWN_GROUPS: Final[Mapping[str, Callable[[RunView], dict[str, object]]]] = {
    "readouts": _shown_readouts,
    "settings": _shown_settings,
    "accounting": _shown_accounting,
}


def _readouts_of(step: RunSettings, *, cards_withheld: bool = False) -> dict[str, object]:
    """The readouts group as it should appear for one step, built by the functions the view calls.

    Args:
        step: The step whose agent the heading and the 1 MAC line name. Unless
            the cards are withheld, it is a snapshot, and the cards show its values.
        cards_withheld: True where the scenario requires every card and the clock to
            withhold their values, because no frame has been drawn since the run
            started over.
    """

    expected: dict[str, object] = {
        "heading": substance_heading(step),
        "1 MAC": format_mac_reference(step.agent_display_name, step.agent_mac_percent),
    }

    if cards_withheld:
        cards = [(WITHHELD_CONCENTRATION_TEXT, WITHHELD_MAC_MULTIPLE_TEXT)] * len(READOUT_PANELS)
        cards[_CLOCK_INDEX] = (WITHHELD_ELAPSED_TIME_TEXT, "")
    else:
        assert isinstance(step, SimulationSnapshot)
        cards = [
            (readout.value, readout.secondary) for readout in readouts(step, DEFAULT_PLAYBACK_RATE)
        ]

    for index, (value, secondary) in enumerate(cards):
        if index == _CLOCK_INDEX:
            expected["clock"] = value
        else:
            expected[f"card {index}"] = (value, secondary)

    return expected


def _settings_of(step: RunSettings) -> dict[str, object]:
    """The settings group as one step states it, built by the functions the view calls."""

    settings = setting_readouts(step)
    expected: dict[str, object] = {
        f"dial {index}": (
            setting.name,
            setting.qualifier,
            slider_position(setting.minimum, setting.decimals),
            slider_position(setting.maximum, setting.decimals),
            slider_position(setting.value, setting.decimals),
            setting.value_text,
            setting.secondary,
        )
        for index, setting in enumerate(settings)
    }
    (delivered,) = (setting for setting in settings if setting.control is ControlInput.DELIVERED)
    expected["delivered line"] = delivered_line(delivered)

    return expected


def _no_settings() -> dict[str, object]:
    """The settings group of a run whose dials cannot be built (`PL-SV2Q`).

    The dashboard holds no dial, one line says so in their place, and the
    delivered line withholds both of its values. Both texts are written out
    by hand.
    """

    return {
        "no dials": ([], False, "This run's setting controls cannot be shown."),
        "delivered line": "Delivered \u2014% (\u2014 \u00d7MAC)",
    }


#: The amounts that the panel should show for the failing check from `_a_failing_check`.
#: They are written by hand. 40.0 L delivered, less 20.0 L exhausted and 14.0 L stored,
#: leaves 6.0 L unaccounted. The panel does not show the unaccounted amount or the
#: absolute error exactly. It shows the next power of ten above each one, so both lines
#: show "<1e+01 L".
_REJECTED_CHECK_AMOUNTS: Final = (
    "Delivered: 40.0 L\nExhausted: 20.0 L\nStored: 14.0 L\n"
    "Unaccounted: <1e+01 L\nAbsolute error: <1e+01 L"
)


def _a_failing_check() -> AgentSimulationValidationResult:
    """Return a failing accounting check with totals that no run in these tests reaches.

    A run at the default settings has delivered about 0.4 L of agent at 5 minutes.
    So a panel that pairs this check's verdict with the restored step's amounts shows
    different numbers from a panel that shows this check's own amounts. The restored
    step is the one that the run returns to when the core rolls a rejected step back.
    The validator builds the check from these totals, the same way that it builds the
    check for a step.
    """

    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=40.0, exhausted_agent_l=20.0)

    return validator.check_agent_accounting(currently_stored_agent_l=14.0)


def _rejected_accounting() -> dict[str, object]:
    """The accounting group for the step that `_reject_the_next_accounting_check` rejects."""

    return {
        "verdict": ACCOUNTING_FAILED_TEXT,
        "detail": ACCOUNTING_REJECTED_DETAIL_TEXT,
        "amounts": _REJECTED_CHECK_AMOUNTS,
    }


def _reject_the_next_accounting_check(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make the next step's accounting check fail, once, with the check from `_a_failing_check`.

    For one call, `require_valid_agent_accounting` evaluates that check instead of the
    step's own check. So the step raises the real `AgentSimulationValidationError`,
    built by the real code, and the core rolls the step back. The failure is injected
    because no supported setting makes the accounting fail. The injected check's totals
    differ from the restored step's totals by enough to change what the panel shows.
    Until the test-strength pass of `PL-J5GC`, the injected check used the step's own
    totals, and one 0.1 s step changed no amount that the panel shows. So a panel that
    showed the restored step's amounts with the rejected verdict still passed the test.
    """

    real_require = AgentSimulationValidator.require_valid_agent_accounting
    rejected = _a_failing_check()
    armed = [True]

    def failed_check(
        validator: AgentSimulationValidator, currently_stored_agent_l: float
    ) -> AgentSimulationValidationResult:
        return rejected

    def require_once(
        validator: AgentSimulationValidator, currently_stored_agent_l: float
    ) -> AgentSimulationValidationResult:
        if not armed:
            return real_require(validator, currently_stored_agent_l)

        armed.clear()

        with pytest.MonkeyPatch.context() as once:
            once.setattr(AgentSimulationValidator, "check_agent_accounting", failed_check)
            return real_require(validator, currently_stored_agent_l)

    monkeypatch.setattr(AgentSimulationValidator, "require_valid_agent_accounting", require_once)


def _a_drawn_frame(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """A run that a frame drew. Every group describes the step that the frame drew."""

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    controller.pause()
    run = _shown_view(application, controller).runs[0]
    step = _fresh_run(600.0, delivered_concentration_percent=Percent(8.0)).snapshot()

    return run, {
        "readouts": _readouts_of(step),
        "settings": _settings_of(step),
        "accounting": _accounting_of(step),
    }


def _a_halt_after_an_agent_change(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """A run whose agent changed when no frame could be drawn (`PL-6RJ0`).

    The heading, the 1 MAC line and the dials describe the new case. The cards, the
    clock and the accounting panel withhold the old agent's values, because the new
    case has no frame yet, and the old case's values would sit under the new agent's
    name. Until the blind review of `PL-J5GC`, the accounting panel kept the old
    case's verdict and amounts, and until its adversarial review the clock kept the
    old case's 10 minutes.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    controller.pause()
    run = _shown_view(application, controller).runs[0]
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()

    assert controller.has_failed is True
    new_case = SimulationController("desflurane").record()

    return run, {
        "readouts": _readouts_of(new_case, cards_withheld=True),
        "settings": _settings_of(new_case),
        "accounting": _withheld_accounting(),
    }


def _a_halt_after_an_agent_change_whose_dials_cannot_be_written(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """An agent change after which no frame can be drawn, on a run whose dials cannot be written.

    `show_presentation` writes the new agent's heading and 1 MAC line, and raises the
    refusal from `setting_readouts` last. Until the blind review of `PL-J5GC`, the old
    agent's values were withheld only after that, so the exception left every card
    showing the old agent's percent and ×MAC number under the new agent's heading. No
    dial can be built from any state here. The dial row and the delivered line used
    to keep the old agent's 8.00% and 4.00 ×MAC (`PL-SV2Q`). Now the dashboard holds
    no dial, and the delivered line withholds its values.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    controller.pause()
    run = _shown_view(application, controller).runs[0]
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    monkeypatch.setattr(run_presentation_module, "setting_readouts", _no_setting)

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()

    assert controller.has_failed is True
    new_case = SimulationController("desflurane").record()

    _settle(application)

    return run, {
        "readouts": _readouts_of(new_case, cards_withheld=True),
        "settings": _no_settings(),
        "accounting": _withheld_accounting(),
    }


def _a_dial_write_refused_after_the_cards(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """A frame that wrote the cards for a new agent, then could not write the dials.

    `show_presentation` writes the cards first, and raises the refusal from
    `setting_readouts` last. The 1 MAC line used to be written with the dials,
    so it went on naming the old agent above the new agent's cards
    (`PL-6RJ0`). `setting_readouts` refuses every state in this scenario, so
    no dial can be built from any state, and the banner names the refusal.
    The dashboard holds no dial, and the delivered line withholds its values
    (`PL-SV2Q`).
    """

    controller = SimulationController()
    run = _shown_view(application, controller).runs[0]
    monkeypatch.setattr(run_presentation_module, "setting_readouts", _no_setting)

    _select_agent(run, "desflurane")

    assert controller.has_failed is True
    new_case = SimulationController("desflurane").snapshot()
    _settle(application)

    return run, {
        "readouts": _readouts_of(new_case),
        "settings": _no_settings(),
        "accounting": _accounting_of(new_case),
    }


def _a_dial_moved_on_a_failed_run(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """A run whose step failed, then had its cardiac output dial moved (`PL-3B34`).

    The run cannot step again, so every group describes its last completed step, and
    the dials show the settings that step ran under.
    """

    failure = _real_step_failure()
    controller = _StepFailingController(failure)
    controller._pending_error = None
    controller.start()
    _advance(controller, 300.0)
    run = _shown_view(application, controller).runs[0]
    controller._pending_error = failure

    _steps(run, 1)
    assert controller.has_failed is True
    _drag(_dials(run)._cardiac_output_slider, 10.0, FLOW_DISPLAY_DECIMALS)

    step = _fresh_run(300.0).snapshot()

    return run, {
        "readouts": _readouts_of(step),
        "settings": _settings_of(step),
        "accounting": _accounting_of(step),
    }


def _a_dial_moved_at_the_supported_run_length(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """A run stopped at a shortened supported run length, then had its cardiac output dial moved.

    The supported run length here ends at 300 s, as `maximum_step_count` reads it,
    for the reason that
    `test_a_run_that_arrives_at_the_supported_run_length_under_its_own_timers_is_redrawn`
    gives. Every group describes the step the run stopped on (`PL-3B34`).
    """

    last_step = round(300.0 / SIMULATION_STEP_S)
    monkeypatch.setattr(
        supported_ranges_module, "maximum_step_count", lambda simulation_step_s: last_step
    )
    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    assert controller.has_reached_supported_limit is True
    run = _case_view(application, BranchedCase(controller)).runs[0]

    _drag(_dials(run)._cardiac_output_slider, 10.0, FLOW_DISPLAY_DECIMALS)

    step = _fresh_run(300.0).snapshot()

    return run, {
        "readouts": _readouts_of(step),
        "settings": _settings_of(step),
        "accounting": _accounting_of(step),
    }


def _an_accounting_halt(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """A run halted because a step's accounting check failed (`PL-HF4B`).

    The core rolls the step back. So the readouts and the dials describe the last
    completed step, and the accounting panel describes the rejected step: its
    verdict and the totals that the verdict judged.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    run = _shown_view(application, controller).runs[0]
    _reject_the_next_accounting_check(monkeypatch)

    _steps(run, 1)

    assert controller.has_failed is True
    step = _fresh_run(300.0).snapshot()

    return run, {
        "readouts": _readouts_of(step),
        "settings": _settings_of(step),
        "accounting": _rejected_accounting(),
    }


def _an_accounting_halt_that_no_frame_draws(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """A run halted by a failed accounting check, whose next frame cannot be drawn.

    Until the adversarial review of `PL-J5GC`, only a frame wrote the accounting
    panel. So the panel kept the last frame's "Valid" under a banner that named
    the failed check. The readouts and the dials describe the last completed
    step, which is also the step the last frame drew.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    run = _shown_view(application, controller).runs[0]
    _reject_the_next_accounting_check(monkeypatch)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    _steps(run, 1)

    assert controller.status().rejected_accounting is not None
    step = _fresh_run(300.0).snapshot()

    return run, {
        "readouts": _readouts_of(step),
        "settings": _settings_of(step),
        "accounting": _rejected_accounting(),
    }


def _a_halt_after_a_reset_that_no_frame_draws(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """A Reset after a drawn accounting halt, on a run whose frames can no longer be drawn.

    The last frame drew the accounting halt at 300 s, with "Validation failed" and
    the rejected step's totals. Reset starts the run over at 0 s and clears the
    rejected check, and then no frame draws. Until the adversarial review of
    `PL-J5GC`, only an agent change was detected as starting the run over. So the
    clock, every card and the accounting panel went on describing the run that
    Reset discarded. The heading and the dials describe the restarted run, which
    keeps every setting.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    run = _shown_view(application, controller).runs[0]
    _reject_the_next_accounting_check(monkeypatch)
    _steps(run, 1)
    assert _accounting_panel(run)._agent_accounting_status_text.text() == ACCOUNTING_FAILED_TEXT
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    run._reset_button.click()

    assert controller.has_failed is True
    assert controller.status().rejected_accounting is None
    restarted = SimulationController().record()

    return run, {
        "readouts": _readouts_of(restarted, cards_withheld=True),
        "settings": _settings_of(restarted),
        "accounting": _withheld_accounting(),
    }


def _a_frame_after_a_reset_that_followed_an_accounting_halt(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """Return a view that drew an accounting halt, then a frame after a Reset.

    Reset starts a new run at 0 s and keeps every setting, and the frame draws that
    run. So every group of readings describes a run that has taken no step, and the
    accounting panel shows what a fresh run's panel shows. If Reset kept the rejected
    check, every frame of the new run would show "Validation failed" and the discarded
    step's totals, under a banner that names no failure. Until the test-strength pass
    of `PL-J5GC`, no test checked that Reset clears the rejected check.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    run = _shown_view(application, controller).runs[0]
    _reject_the_next_accounting_check(monkeypatch)
    _steps(run, 1)
    assert controller.status().rejected_accounting is not None

    run._reset_button.click()

    assert controller.has_failed is False
    restarted = SimulationController().snapshot()

    return run, {
        "readouts": _readouts_of(restarted),
        "settings": _settings_of(restarted),
        "accounting": _accounting_of(restarted),
    }


def _a_frame_after_an_agent_change_that_followed_an_accounting_halt(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """Return a view that drew an accounting halt, then a frame after a change to desflurane.

    The change of agent starts a new case, and the frame draws that case. So every
    group of readings describes a desflurane run that has taken no step. Until the
    test-strength pass of `PL-J5GC`, no test checked that a new case clears the
    rejected check. `_a_frame_after_a_reset_that_followed_an_accounting_halt` says
    why that matters.
    """

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    run = _shown_view(application, controller).runs[0]
    _reject_the_next_accounting_check(monkeypatch)
    _steps(run, 1)
    assert controller.status().rejected_accounting is not None

    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()

    assert controller.has_failed is False
    new_case = SimulationController("desflurane").snapshot()

    return run, {
        "readouts": _readouts_of(new_case),
        "settings": _settings_of(new_case),
        "accounting": _accounting_of(new_case),
    }


def _a_halt_after_a_frame_drawn_for_a_new_agent(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """Return a view that drew a frame after an agent change, then failed to draw the next one.

    After a Reset or an agent change, a halt withholds values until a frame is drawn
    (`RunView.show_presentation`). If drawing a frame did not end the withholding, the halt
    would withhold values that do describe the run on screen (`PL-J5GC`). Here the frame
    drawn after the change wrote every card and the clock for the new case, so the run has
    not started over since that frame. The halt keeps what that frame wrote, and every
    group of readings describes the new case at its opening.
    """

    controller = SimulationController()
    controller.start()
    controller.set_delivered_concentration_percent(Percent(8.0))
    _advance(controller, 600.0)
    controller.pause()
    view = _shown_view(application, controller)
    run = view.runs[0]
    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    dialog.discard_button.click()
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)

    assert controller.has_failed is True
    new_case = SimulationController("desflurane").snapshot()

    return run, {
        "readouts": _readouts_of(new_case),
        "settings": _settings_of(new_case),
        "accounting": _accounting_of(new_case),
    }


def _a_halt_after_frames_drawn_later_than_the_first(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> tuple[RunView, _GroupReadings]:
    """Return a view that opened at 0 s, drew frames at 300 s and 600 s, then failed to draw.

    Every other scenario builds its dashboard after the run has advanced, so the
    values that the dashboard opened with are also the last frame's. Here they
    differ. A halt keeps the values of the last frame drawn, which is the frame at
    600 s. A panel that kept the first frame of the case would show the opening's
    cards and "Delivered: 0.0 L" under a banner that calls them the last frame drawn
    (`PL-RF2S`).
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    _advance(controller, 300.0)
    view.present(False)
    _advance(controller, 300.0)
    view.present(False)
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)

    view.present(False)

    assert controller.has_failed is True
    step = _fresh_run(600.0).snapshot()

    return run, {
        "readouts": _readouts_of(step),
        "settings": _settings_of(step),
        "accounting": _accounting_of(step),
    }


_ONE_STATE_SCENARIOS: Final[
    Mapping[str, Callable[[QApplication, pytest.MonkeyPatch], tuple[RunView, _GroupReadings]]]
] = {
    "drawn frame": _a_drawn_frame,
    "halt after an agent change": _a_halt_after_an_agent_change,
    "halt after an agent change, dials unwritable": (
        _a_halt_after_an_agent_change_whose_dials_cannot_be_written
    ),
    "dial write refused after the cards": _a_dial_write_refused_after_the_cards,
    "dial moved on a failed run": _a_dial_moved_on_a_failed_run,
    "dial moved at the supported run length": _a_dial_moved_at_the_supported_run_length,
    "accounting halt": _an_accounting_halt,
    "accounting halt, no frame drawn": _an_accounting_halt_that_no_frame_draws,
    "halt after a Reset, no frame drawn": _a_halt_after_a_reset_that_no_frame_draws,
    "frame after a Reset that followed an accounting halt": (
        _a_frame_after_a_reset_that_followed_an_accounting_halt
    ),
    "frame after an agent change that followed an accounting halt": (
        _a_frame_after_an_agent_change_that_followed_an_accounting_halt
    ),
    "halt after a frame drawn for a new agent": _a_halt_after_a_frame_drawn_for_a_new_agent,
    "halt after frames drawn later than the first": (
        _a_halt_after_frames_drawn_later_than_the_first
    ),
}


@pytest.mark.parametrize("scenario", list(_ONE_STATE_SCENARIOS))
def test_every_value_and_its_qualifiers_on_screen_come_from_one_state(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, scenario: str
) -> None:
    """Each value on the run screen and what qualifies it describe one step of the run.

    Every widget has had one writer since `PL-X7D5` and `PL-WM5P`, and the test
    above compares each widget on a halted screen with itself on a drawn one. Two
    widgets that disagree on one screen pass that test. A ×MAC number divided by
    another agent's 1 MAC (`PL-6RJ0`), a dial showing a setting no step ran under
    (`PL-3B34`) and a "Valid" verdict beside a banner that reports a failed check
    (`PL-HF4B`) each passed it.

    So each scenario names, for each group in `VALUE_GROUPS`, the step that all of
    the group's members must describe. It takes that step from a run built without
    the control or failure under test, and builds each member's text from it with
    the function the view calls. Those functions are not under test here. What is
    under test is the step that each group is written from (`PL-J5GC`).
    """

    run, expected = _ONE_STATE_SCENARIOS[scenario](application, monkeypatch)
    attributes = _widget_attributes(run)
    grouped = [member for members in VALUE_GROUPS.values() for member in members]

    assert sorted(set(grouped) & set(UNGROUPED_WIDGETS)) == [], (
        "these widgets are in a group and also listed as in none - keep one"
    )
    assert sorted(set(attributes) - set(grouped) - set(UNGROUPED_WIDGETS)) == [], (
        "these widgets are in no group and not listed in UNGROUPED_WIDGETS: put each in "
        "the group whose value it states or qualifies, or list it with the reason it is "
        "in none"
    )
    listed = set(grouped) | set(UNGROUPED_WIDGETS)

    if _setting_row(run).controls is None:
        # The View shows no dial for this run, so no dial is there to list.
        listed = {name for name in listed if not name.startswith(_SETTING_CONTROLS)}

    assert sorted(listed - set(attributes)) == [], (
        "these entries name a widget RunView no longer holds - remove them"
    )
    assert sorted(expected) == sorted(VALUE_GROUPS)

    shown = {group: _SHOWN_GROUPS[group](run) for group in expected}

    assert shown == expected


@pytest.mark.parametrize("scenario", list(_ONE_STATE_SCENARIOS))
def test_an_accounting_view_chosen_after_each_scenario_shows_the_same_step(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, scenario: str
) -> None:
    """An accounting View chosen after a halt shows the step that the first View shows.

    A reader can choose the accounting View for another Area at any time,
    and that View builds its own panel for the run. Suppose a halt handed
    the runs only to the Views that already existed. A View chosen after the
    halt would then stay empty, or show the last frame's "Valid", beside a
    banner that reports the failed check or that the run started over. Until
    the test-strength pass of `PL-J5GC`, no test opened a panel after a
    halt. In the scenarios whose frames fail, the halt alone draws the new
    View (`PL-RF2S`).
    """

    run, expected = _ONE_STATE_SCENARIOS[scenario](application, monkeypatch)
    dashboard = _dashboard_of(run)

    dashboard.layout_container.choose_view(AreaId(3), AGENT_ACCOUNTING)
    _settle(application)
    # Area 3 comes before the sidebar's Area in reading order.
    chosen, first = (v for v in dashboard.layout_container.views() if isinstance(v, AccountingView))

    assert chosen is not first
    assert [_accounting_reading(panel) for panel in chosen.panels] == [expected["accounting"]]
    assert [_accounting_reading(panel) for panel in first.panels] == [expected["accounting"]]


def test_a_halt_whose_dials_cannot_be_built_shows_no_earlier_setting(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """After an agent change whose dials cannot be built, no earlier setting stays on screen.

    The run held sevoflurane at 8.00%, which is 4.00 ×MAC. The learner changes
    to desflurane while every frame fails and no dial can be built. The dial
    row and the delivered line used to keep "8.00%" and "4.00 ×MAC", beside a
    1 MAC line that named desflurane (`PL-SV2Q`). The dashboard now holds no
    dial for the run, one line says so in the dials' place, and the delivered
    line withholds both of its values. Both texts are written out by hand.

    The dials can then be built again, and a frame draws. The four dials are
    back, showing the settings of a desflurane run built directly, and the
    line in their place is gone.
    """

    run, _ = _a_halt_after_an_agent_change_whose_dials_cannot_be_written(application, monkeypatch)
    _settle(application)
    dashboard = run.parent()
    assert isinstance(dashboard, SimulationView)

    dials = [
        (dial.name_label.text(), dial.value_label.text(), dial.secondary_label.text())
        for dial in dashboard.findChildren(ParameterSlider)
    ]

    row = _setting_row(run)

    assert run._one_mac_text.text() == "1 MAC desflurane = 6.0%"
    assert dials == []
    assert row.controls is None
    assert row.not_shown_text.text() == "This run's setting controls cannot be shown."
    assert row.not_shown_text.text() in dashboard.visible_strings()
    assert run._delivered_text.text() != "Delivered 8.00% (4.00 \u00d7MAC)"
    assert run._delivered_text.text() == "Delivered \u2014% (\u2014 \u00d7MAC)"

    monkeypatch.undo()
    dashboard.present(False)
    _settle(application)
    in_force = setting_readouts(SimulationController("desflurane").record())

    assert _setting_row(run) is row
    assert row.controls is not None, "the dials were not built again"
    assert [
        (dial.name_label.text(), dial.value_label.text(), dial.secondary_label.text())
        for dial in dashboard.findChildren(ParameterSlider)
    ] == [(setting.name, setting.value_text, setting.secondary) for setting in in_force]
    assert row.not_shown_text.isHidden() is True
    assert "This run's setting controls cannot be shown." not in dashboard.visible_strings()


@pytest.mark.parametrize(
    ("scenario", "way_out"),
    [
        ("dial moved on a failed run", "Reset to start a new run, which keeps every setting."),
        (
            "dial moved at the supported run length",
            "To try a different setting, branch at an earlier instant, where each dial starts at "
            "what it was set to then, or Reset to start a new run, which keeps every setting.",
        ),
    ],
)
def test_a_setting_changed_on_a_halted_run_is_not_shown_as_the_setting_its_values_ran_under(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, scenario: str, way_out: str
) -> None:
    """A dial moved on a stopped run springs back, records nothing, and the banner says why.

    No step runs after a stop, so a new setting would sit beside values that it never
    produced. The moved dial used to be applied (`PL-3B34`). The cardiac output then showed
    10.0 L/min beside concentrations computed at 5.0 L/min. The record also claimed a
    change at the instant of the stop, and that change never acted on the patient.

    A run stops either at the supported run length or on a failure, and the banner
    names a different way out for each (project owner, 2026-10-26). The supported run
    length is the expected end of a long run, so its way out is a branch at an earlier
    instant, which can take the new setting. A failure is a fault, so Reset remains its
    way out.

    The halt that the run shows when no frame can be drawn (`show_presentation`) gives
    the same refusal and the same way out. Until the test-strength pass of
    `PL-J5GC`, no test checked that banner after a refused dial.

    Each scenario builds its run. It takes the dial settings that the run should show
    from a run that never stopped.
    """

    run, expected = _ONE_STATE_SCENARIOS[scenario](application, monkeypatch)

    assert _shown_settings(run) == expected["settings"]
    assert run.controller.record().control_timeline == ()
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.endswith(f"{_CARDIAC_OUTPUT_REFUSED_ON_A_STOPPED_RUN}. {way_out}")

    run.show_presentation(run.presentation())

    halted = run._notice_text.notice()
    assert halted is not None
    assert halted.endswith(f"{_CARDIAC_OUTPUT_REFUSED_ON_A_STOPPED_RUN}. {way_out}")


def test_a_setting_refused_at_the_supported_run_length_names_a_branch_only_while_one_can_be_taken(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The way out given for a refused dial changes once a branch can no longer be taken.

    A dial moved on a run at the supported run length is refused, and the banner
    names a branch at an earlier instant as the way to a new setting. Once a
    branch is on the chart, the branch control is locked, so naming it would send
    the reader to a control that is not there. Until the blind review of
    `PL-3B34`, the banner chose its way out from the run's status alone and went
    on naming the branch. A dashboard built with no case has no branch control,
    so its banner never names one. Until the adversarial review of `PL-J5GC`, it
    did. The supported run length here ends at 300 s, for the reason that
    `_a_dial_moved_at_the_supported_run_length` gives.
    """

    last_step = round(300.0 / SIMULATION_STEP_S)
    monkeypatch.setattr(
        supported_ranges_module, "maximum_step_count", lambda simulation_step_s: last_step
    )
    refused = f"{_CARDIAC_OUTPUT_REFUSED_ON_A_STOPPED_RUN}. "
    reset_alone = refused + "Reset to start a new run, which keeps every setting."

    caseless = SimulationController()
    caseless.start()
    _advance(caseless, 300.0)
    caseless_run = _shown_view(application, caseless).runs[0]
    _drag(_dials(caseless_run)._cardiac_output_slider, 10.0, FLOW_DISPLAY_DECIMALS)

    no_control = caseless_run._notice_text.notice()
    assert no_control is not None
    assert no_control.endswith(reset_alone)

    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    assert controller.has_reached_supported_limit is True
    view = _case_view(application, BranchedCase(controller))
    trunk = view.runs[0]

    _drag(_dials(trunk)._cardiac_output_slider, 10.0, FLOW_DISPLAY_DECIMALS)

    alone = trunk._notice_text.notice()
    assert alone is not None
    assert alone.endswith(
        refused + "To try a different setting, branch at an earlier instant, where each dial "
        "starts at what it was set to then, or Reset to start a new run, which keeps every "
        "setting."
    )

    _take_fork(view, 0.0)

    assert len(view.runs) == 2
    compared = trunk._notice_text.notice()
    assert compared is not None
    assert compared.endswith(reset_alone)


def test_a_setting_refused_after_the_dashboard_failed_at_the_supported_run_length_names_reset(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A trunk with a failed dashboard offers no branch, so a dial's refusal names only Reset.

    Here the frame itself raises the supported-limit error. The run stops at the
    supported run length rather than failing, and it records that its dashboard failed.
    Its `fork_refusal` then gives a reason, and the case offers no branch, because the
    same dashboard would draw the branch (`PL-T2Q2`). So the way out that a dial's
    refusal names must not be a branch. Until the test-strength pass of `PL-J5GC`, no
    test checked that `RunView._branch_offered` reads `fork_refusal`. This test sets the
    supported run length to 300 s, for the reason that
    `_a_dial_moved_at_the_supported_run_length` gives.
    """

    last_step = round(300.0 / SIMULATION_STEP_S)
    monkeypatch.setattr(
        supported_ranges_module, "maximum_step_count", lambda simulation_step_s: last_step
    )
    controller = SimulationController()
    controller.start()
    _advance(controller, 300.0)
    view = _case_view(application, BranchedCase(controller))
    trunk = view.runs[0]

    def limit(*args: object, **kwargs: object) -> NoReturn:
        raise SimulationDomainLimitError("this run has reached 300 s of simulated time")

    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", limit)
    view.present(False)

    assert controller.has_failed is False
    assert controller.has_reached_supported_limit is True
    assert controller.fork_refusal is not None

    _drag(_dials(trunk)._cardiac_output_slider, 10.0, FLOW_DISPLAY_DECIMALS)

    banner = trunk._notice_text.notice()
    assert banner is not None
    assert banner.endswith(
        f"{_CARDIAC_OUTPUT_REFUSED_ON_A_STOPPED_RUN}. "
        "Reset to start a new run, which keeps every setting."
    )


@pytest.mark.parametrize(
    "scenario", ["halt after an agent change", "halt after a Reset, no frame drawn"]
)
def test_a_halt_that_no_frame_draws_after_the_run_started_over_says_its_readouts_are_withheld(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, scenario: str
) -> None:
    """The banner says the readouts are withheld, not that they show the last frame.

    This test covers a halt when no frame has been drawn since the run started over.
    Until the adversarial review of `PL-J5GC`, the banner said that the chart and
    the readouts showed the last frame drawn before the run stopped. That frame
    belongs to the run before the restart, and the readouts are withheld. The
    chart still shows it, because only a frame writes the chart.
    """

    run, _ = _ONE_STATE_SCENARIOS[scenario](application, monkeypatch)

    banner = run._notice_text.notice()
    assert banner is not None
    assert (
        "No frame has been drawn since the run started over: the readouts are withheld, "
        "the chart still shows the run before it started over, and the run itself stands at "
        "its last completed step."
    ) in banner


def test_an_accounting_error_with_a_check_of_the_wrong_type_still_halts_the_run(
    application: QApplication,
) -> None:
    """A check of the wrong type raises `TypeError`, but only after the run has failed.

    `rejected_check` raises `TypeError` for a check that is not a validation
    result. Until the blind review of `PL-HF4B`, `RunView.halt` read the check
    before it failed the run. The `TypeError` then cancelled the halt, and the
    run went on stepping under a screen that read "Running".
    """

    controller = SimulationController()
    controller.start()
    run = _shown_view(application, controller).runs[0]

    with pytest.raises(TypeError):
        run.halt(AgentSimulationValidationError("accounting failed", check="not a check"))

    assert controller.has_failed is True
    assert controller.is_running is False


def test_a_halted_run_shows_the_new_playback_rate(
    application: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`PL-P58M`: a halted run shows one playback rate, the one the reader just chose.

    The clock's second line sits in the readout row. A halt does not write
    that row, because its readouts are compartment values that only a frame
    can state. Until `PL-P58M`, a rate chosen on a halted run reached the
    dropdown but not the clock, so the screen showed 5x in one place and 1x
    in the other.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]
    monkeypatch.setattr(simulation_view_module, "assemble_chart_frame", _failing_assembly)
    view.present(False)

    assert controller.has_failed is True
    assert run._playback_rate_text.text() == format_playback_rate(1)

    dropdown = run._playback_rate_dropdown
    dropdown.setCurrentIndex(dropdown.findData(5))

    assert dropdown.currentText() == format_playback_rate(5)
    assert run._playback_rate_text.text() == format_playback_rate(5)


def test_a_confirmation_answered_after_the_snapshot_refuses_restates_the_halt(
    application: QApplication, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    """A confirmation answered after the snapshot rejects a value shows the halt, not a refusal.

    The question is asked from a snapshot read when the selector was used.
    By the time the reader answers, the run's snapshot may reject a value.
    `set_agent` carries the settings over from the snapshot. So without the
    gate, the exception from `set_agent` reached `_apply_setting` as a refused
    setting. It was recorded in `_rejected_setting_notice`, even though the run
    had halted for the same reason (`PL-V2HC`, found at review).
    `_start_new_case` now reads the snapshot first, outside `_apply_setting`,
    and the dialog's gated slot halts the run for the exception (`PL-HJKN`).
    The test checks that the halt is shown, nothing is recorded as refused, the
    dialog is gone and the run keeps its agent.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller)
    run = view.runs[0]
    _select_agent(run, "desflurane")
    dialog = run._new_case_dialog
    assert dialog is not None
    _read_the_alveolar_quotient_as(monkeypatch, 1.0000001)
    capfd.readouterr()

    dialog.discard_button.click()

    assert "Traceback" not in capfd.readouterr().err
    reason = (
        "SimulationConfigurationError: alveolar partial_pressure_fraction of 1.0000001 is "
        "outside 0 to 1"
    )
    status = controller.status()
    assert controller.has_failed is True
    assert status.failure_reason is not None
    assert status.failure_reason.startswith(reason)
    assert controller.agent_id == "sevoflurane"
    assert run._rejected_setting_notice is None
    assert run._new_case_dialog is None
    assert run._agent_dropdown.currentData() == "sevoflurane"
    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.startswith(f"Simulation stopped — {reason}")


def test_a_reset_the_core_refuses_halts_the_run_visibly(application: QApplication) -> None:
    """A Reset the core refuses stops the run through the failed-step path, and clears nothing.

    `SimulationController.reset()` refuses a settings record that the run's
    definition cannot open on. Tissue flows that no longer sum to the cardiac
    output make such a record, and tissue fractions written past their guard
    leave the flows that way (`_with_stale_tissue_flows`). Before `PL-M4M0`,
    the refusal escaped the Reset slot after `pause()` had run and the state
    had been cleared. So the run was left half reset. The compartments and
    the clock were at zero, the old definition and timeline were kept, no
    failure was recorded, and `case_restarted` was never emitted. Meanwhile
    the screen showed "Running" and offered Pause. The core now refuses
    before it clears anything, and the view halts the run on the refusal.
    The refusal is recorded as the failure and shown by the status word, the
    transport and the banner. The banner's way out says that no setting can
    repair the refusal, instead of naming the Reset that was just refused
    (`PL-01GY`). Nothing changed, so the frame that follows draws the run
    where it was.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    restarts: list[None] = []
    run.case_restarted.connect(lambda: restarts.append(None))
    run._start_button.click()
    _steps(run, 5)
    before = controller.snapshot()
    segments = controller.run_segments
    presented = view.presented_frames
    _with_stale_tissue_flows(controller, 6.0)

    run._reset_button.click()

    reason = (
        "SimulationConfigurationError: the tissue groups are perfused at 6.0 L/min in total "
        "but cardiac output is 5.0 L/min; the venous balance returns what the tissues "
        "receive, so the two must agree"
    )
    status = controller.status()
    after = controller.snapshot()

    assert controller.is_running is False
    assert controller.has_failed is True
    assert status.failure_reason == reason
    assert restarts == []
    assert after.elapsed_s == before.elapsed_s > 0.0
    assert controller.run_segments == segments
    assert run._status_text.text() == "Stopped — simulation error"
    assert run._start_button.isEnabled() is False
    assert run._pause_button.isEnabled() is False
    assert view.presented_frames == presented + 1
    assert run._elapsed_time_text.text() != "0s"
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice == (
        f"Simulation stopped — {reason}. The values shown are the last completed step. "
        f"Reset was refused for this reason. {REFUSED_RESET_WAY_OUT_TEXT}"
    )
    assert RESET_EXIT_TEXT not in notice


def test_a_second_refused_reset_states_the_refusal_once(application: QApplication) -> None:
    """Pressing the refused Reset again leaves the banner as it was: one reason, not two.

    The first press records the refusal as the failure. So on the second
    press the run already has a recorded reason, but that reason is this same
    refusal. The exit text that repeats the refusal is meant for a run that
    failed for some other reason. Stated twice, the one refusal looked like
    two faults (`PL-M4M0`).
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    run._start_button.click()
    _steps(run, 5)
    _with_stale_tissue_flows(controller, 6.0)
    run._reset_button.click()
    first = run._notice_text.notice()
    assert first is not None

    run._reset_button.click()

    notice = run._notice_text.notice()
    assert notice == first
    assert notice.count("perfused at") == 1
    assert notice.endswith(f"Reset was refused for this reason. {REFUSED_RESET_WAY_OUT_TEXT}")


def test_a_reset_refused_on_a_failed_run_keeps_the_failure_and_states_the_refusal(
    application: QApplication,
) -> None:
    """The first failure stays the banner's reason, so the exit carries the refusal itself.

    `SimulationController.fail` keeps the first reason it was given, which is
    correct. The values on screen are the last completed step before that
    first failure stopped the run. So the refusal is stated where it can be,
    in the way out, which says that Reset was refused and why (`PL-M4M0`).
    """

    controller = _StepFailingController(_real_step_failure())
    controller.set_cardiac_output(CardiacOutput(6.0))
    view = _shown_view(application, controller)
    run = view.runs[0]
    controller.start()
    _steps(run, 3)
    failure = controller.status().failure_reason
    assert failure is not None and failure.startswith("SimulationNumericalError: ")
    _with_stale_tissue_flows(controller, 5.0)

    run._reset_button.click()

    assert controller.status().failure_reason == failure
    assert run._status_text.text() == "Stopped — simulation error"
    assert run._start_button.isEnabled() is False
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.startswith(f"Simulation stopped — {failure}.")
    assert notice.endswith(
        "Reset was refused — SimulationConfigurationError: the tissue groups are perfused at "
        "5.0 L/min in total but cardiac output is 6.0 L/min; the venous balance returns what "
        f"the tissues receive, so the two must agree. {REFUSED_RESET_WAY_OUT_TEXT}"
    )


def test_a_refused_reset_takes_once_the_record_is_repaired_and_no_dial_lifts_its_exit(
    application: QApplication,
) -> None:
    """After a refused Reset, a moved dial is refused, and only a successful Reset clears the run.

    A refused Reset leaves the run failed, and a failed run refuses every dial
    (`PL-3B34`). So a moved dial leaves the refused-Reset exit on the banner,
    with the dial's refusal after it, and the cardiac output stays at the
    reference adult's 5.0 L/min (`data/patients/reference_adult.json`). Until
    `PL-3B34`, an accepted setting took the exit off the banner (`PL-M4M0`), and
    until `PL-HQF5` the cardiac output change repaired the stale flows. No
    shipped code repairs a fraction that was written by bypassing its guard, so
    the test puts the fractions back, and then Reset succeeds.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    restarts: list[None] = []
    run.case_restarted.connect(lambda: restarts.append(None))
    run._start_button.click()
    _steps(run, 5)
    _with_stale_tissue_flows(controller, 6.0)
    run._reset_button.click()
    assert controller.has_failed is True

    run._handle_fresh_gas_flow_change(3.0)

    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.endswith(
        f"{REFUSED_RESET_WAY_OUT_TEXT} "
        f"{_REFUSED_ON_A_STOPPED_RUN_TEMPLATE.format(setting='fresh gas flow')}."
    )

    _with_the_tissue_fractions_put_back(controller)
    run._handle_cardiac_output_change(6.0)

    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.startswith("Simulation stopped — SimulationConfigurationError: the tissue groups")
    assert notice.endswith(
        f"{REFUSED_RESET_WAY_OUT_TEXT} {_CARDIAC_OUTPUT_REFUSED_ON_A_STOPPED_RUN}."
    )
    assert controller.settings().cardiac_output_l_min == 5.0
    assert controller.record().control_timeline == ()

    run._reset_button.click()

    assert restarts == [None]
    assert controller.has_failed is False
    assert controller.is_running is False
    assert controller.snapshot().elapsed_s == 0.0
    assert run._status_text.text() == "Paused"
    assert run._start_button.isEnabled() is True
    assert run._notice_text.isHidden() is True


def test_a_refused_reset_names_no_setting_and_sends_the_reader_to_restart(
    application: QApplication,
) -> None:
    """No dial can repair the record that caused the Reset to be refused, so the banner names none.

    Every tissue flow is formed from the cardiac output (`PL-HQF5`), so a new
    output scales them all by one factor, and their sum still disagrees with the
    output. Until `PL-01GY` the banner said to change the setting the refusal
    names, which is the cardiac output. This test moves that dial on the run
    whose Reset was refused. The failed run refuses the dial (`PL-3B34`), so the
    exit is still on the banner and the refusal follows it, and the next Reset is
    refused again. The expected sentences are written here as literals rather
    than read from the constants.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    restarts: list[None] = []
    run.case_restarted.connect(lambda: restarts.append(None))
    run._start_button.click()
    _steps(run, 5)
    _with_stale_tissue_flows(controller, 6.0)
    way_out = (
        "Reset was refused for this reason. No setting can repair this, because only a "
        "fault in the simulator causes it. Close and reopen the application to start a "
        "new run."
    )

    run._reset_button.click()

    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.endswith(way_out)
    assert "Change the setting" not in notice

    run._handle_cardiac_output_change(6.0)

    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.endswith(f"{way_out} {_CARDIAC_OUTPUT_REFUSED_ON_A_STOPPED_RUN}.")

    run._reset_button.click()

    assert restarts == []
    assert controller.has_failed is True
    assert controller.snapshot().elapsed_s > 0.0
    notice = run._notice_text.notice()
    assert notice is not None
    assert notice.endswith(f"{way_out} {_CARDIAC_OUTPUT_REFUSED_ON_A_STOPPED_RUN}.")


def test_a_run_halted_on_tissue_flows_set_past_its_patient_shows_the_output_its_last_step_ran_at(
    application: QApplication,
) -> None:
    """The cardiac output on screen is the one at which the values beside it were computed.

    Before `PL-KFNP`, a cardiac output could be assigned to the patient
    directly, bypassing `set_cardiac_output`. The run then halted at the next
    step, or at the Reset that `PL-M4M0` refuses. The readout and the dial
    showed the assigned output beside compartment values and a chart computed
    at the old flows (`PL-J39J`). The patient now refuses that assignment.
    Since `PL-HQF5` stale flows can be reached only by writing the tissue
    fractions past their guard (`_with_stale_tissue_flows`), and that changes
    no cardiac output.
    The patient keeps the output at which its last completed step ran. The
    settings record at the stale flows is refused before any step runs at
    them. So the readout, the dial, the values beside them and the run's
    definition, from which the chart is drawn, all show that output. The
    banner's sentence names the two figures that disagree.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    run._start_button.click()
    _steps(run, 5)
    before = controller.snapshot()
    ran_under = controller._state.uptake_system.equation_settings()

    with pytest.raises(SimulationConfigurationError, match="set_cardiac_output"):
        controller._state.uptake_system.patient.cardiac_output_l_min = CardiacOutput(6.0)

    _with_stale_tissue_flows(controller, 6.0)

    _steps(run, 1)

    after = controller.snapshot()
    notice = run._notice_text.notice()

    assert controller.has_failed is True
    assert ran_under.cardiac_output_l_min == 5.0
    assert controller.run_segments[-1].settings == ran_under
    assert after.elapsed_s == before.elapsed_s > 0.0
    assert after.alveolar_partial_pressure_fraction == before.alveolar_partial_pressure_fraction
    assert (
        after.mixed_venous_partial_pressure_fraction
        == before.mixed_venous_partial_pressure_fraction
    )
    assert _dials(run)._cardiac_output_slider.value_label.text() == "5.0 L/min"
    assert _dials(run)._cardiac_output_slider.value() == 5.0
    assert notice is not None
    assert "perfused at 6.0 L/min in total but cardiac output is 5.0 L/min" in notice
    assert "The values shown are the last completed step." in notice

    run._reset_button.click()

    assert controller.run_segments[-1].settings == ran_under
    assert _dials(run)._cardiac_output_slider.value_label.text() == "5.0 L/min"
    assert _dials(run)._cardiac_output_slider.value() == 5.0


def test_a_run_whose_core_setting_moved_past_its_controller_halts_on_the_last_recorded_step(
    application: QApplication,
) -> None:
    """A setting the run never recorded halts the run before chart and readouts differ (`PL-XRN8`).

    The readouts come from the steps and the chart from the run definition.
    A cardiac output written onto the core past `SimulationController` would
    step at 6.0 L/min while the chart was drawn at 5.0, so the run halts on
    the step before, and the banner says why.
    """

    controller = SimulationController()
    view = _shown_view(application, controller)
    run = view.runs[0]
    run._start_button.click()
    _steps(run, 5)
    before = controller.snapshot()

    controller._state.uptake_system.set_cardiac_output(CardiacOutput(6.0))

    _steps(run, 1)

    after = controller.snapshot()
    notice = run._notice_text.notice()

    assert controller.has_failed is True
    assert after.elapsed_s == before.elapsed_s > 0.0
    assert after.alveolar_partial_pressure_fraction == before.alveolar_partial_pressure_fraction
    assert controller.run_segments[-1].settings.cardiac_output_l_min == 5.0
    assert notice is not None
    assert "without SimulationController recording it" in notice


def test_a_refused_branch_reset_halts_the_branch_and_names_the_same_way_out(
    application: QApplication,
) -> None:
    """The same halt on a branch's own run, naming the same way out.

    `_open_at` records the settings in force at the fork, and `reset()` reads
    them before the branch is put back there (`PL-M4M0`). The comparison stays
    open, and the trunk is untouched. The way out is the one every run has,
    closing and reopening the application, because a branch cannot start a
    case of its own (`PL-TFX5`).
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)
    branch = view.runs[BRANCH_RUN_INDEX]
    branch._start_button.click()
    _steps(branch, 4)
    before = branch.snapshot()
    _with_stale_tissue_flows(branch.controller, 6.0)

    branch._reset_button.click()
    _settle(application)

    assert len(view.runs) == 2
    assert len(case.branches) == 1
    assert branch.controller.has_failed is True
    assert branch.snapshot().elapsed_s == before.elapsed_s > 60.0
    assert branch._status_text.text() == "Stopped — simulation error"
    notice = branch._notice_text.notice()
    assert notice is not None
    assert notice.endswith(f"Reset was refused for this reason. {REFUSED_RESET_WAY_OUT_TEXT}")
    assert view.runs[TRUNK_RUN_INDEX].controller.has_failed is False


def test_a_refused_trunk_reset_while_comparing_names_the_one_door_open(
    application: QApplication,
) -> None:
    """Beside a branch the selector is locked, so the banner names a way out open on every run.

    A comparison replaces the trunk's agent selector with the
    `COMPARING_AGENT_LOCK_TEXT` chip, and the branch's Reset leaves the
    comparison open. So a banner that named a new case pointed at a control
    the screen had hidden. The only control left enabled was the trunk's
    Reset, the one just refused (`PL-M4M0`). The exit names closing and
    reopening the application instead (`PL-01GY`). Once the record builds
    again, the trunk's Reset succeeds and ends the comparison, as the fork
    panel says it does.
    """

    case = _branched_case()
    view = _case_view(application, case)
    _take_fork(view, 60.0)
    trunk = view.runs[TRUNK_RUN_INDEX]
    _with_stale_tissue_flows(trunk.controller, 6.0)

    trunk._reset_button.click()
    _settle(application)

    assert len(view.runs) == 2
    assert trunk.controller.has_failed is True
    assert trunk._agent_dropdown.isHidden() is True
    assert trunk._running_agent_lock_text.text() == COMPARING_AGENT_LOCK_TEXT
    notice = trunk._notice_text.notice()
    assert notice is not None
    assert notice.endswith(f"Reset was refused for this reason. {REFUSED_RESET_WAY_OUT_TEXT}")

    _with_the_tissue_fractions_put_back(trunk.controller)
    trunk._handle_cardiac_output_change(6.0)
    trunk._reset_button.click()
    _settle(application)

    assert trunk.controller.has_failed is False
    assert trunk.snapshot().elapsed_s == 0.0
    assert len(view.runs) == 1


def _refusing_a_drawn_column(
    controller: SimulationController, quantity: RecordedQuantity, value: float
) -> None:
    """Make the controller's next drawn window carry `value` in `quantity`'s last column.

    This is the one way to get a drawn fraction outside 0 to 1, because no
    supported setting computes one (`core/concentration.py`). A drawn window
    is an evaluation of the closed form. So the value is written into the
    window that the controller returns, not into any compartment.
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


def test_a_frame_that_refuses_a_drawn_value_moves_no_trace(application: QApplication) -> None:
    """Every drawn value is built before any is drawn, so a refusal leaves the chart as it was.

    Values used to be built as the toolkit converted them, trace by trace.
    Then a column refused in the muscle trace left the circuit, alveolar,
    mixed venous and vessel-rich traces redrawn from the failed frame. The
    muscle and fat traces were left on the frame before it. So six traces
    showed two instants, under a banner that blamed a step that never failed
    (`PL-7DJK`). Now `assemble_chart_frame` refuses before a frame exists.
    The run halts, the halt names the compartment, and no trace moves. The
    value used here is the one that reproduced the defect.
    """

    controller = SimulationController()
    controller.start()
    view = _shown_view(application, controller)
    for _ in range(50):
        controller.advance(SIMULATION_STEP_S)
    view.render_tick()
    chart = _concentration(view).chart
    before = {quantity: chart.drawn_points(0, quantity) for quantity in COMPARTMENT_QUANTITIES}

    _refusing_a_drawn_column(controller, RecordedQuantity.MUSCLE, 1.0000000000001568)
    for _ in range(50):
        controller.advance(SIMULATION_STEP_S)

    view.render_tick()

    status = controller.status()
    run = view.runs[0]

    assert controller.has_failed is True
    assert status.failure_reason is not None
    assert status.failure_reason.startswith(
        "SimulationConfigurationError: muscle partial_pressure_fraction of 1.0000000000001568 "
        "is outside 0 to 1"
    )
    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert "muscle partial_pressure_fraction of 1.0000000000001568" in notice
    assert "No frame of the stopped run could be drawn" in notice
    assert run._pause_button.isEnabled() is False
    assert run._start_button.isEnabled() is False
    assert {
        quantity: chart.drawn_points(0, quantity) for quantity in COMPARTMENT_QUANTITIES
    } == before


@pytest.mark.parametrize("value", [float("nan"), float("inf")], ids=["nan", "inf"])
def test_a_non_finite_drawn_value_halts_the_run_naming_its_compartment(
    application: QApplication, value: float
) -> None:
    """A NaN or an infinity halts the run, and the notice names the compartment (`PL-TCNT`).

    The chart draws with pyqtgraph's `skipFiniteCheck`, so pyqtgraph no
    longer looks for such a value itself. Its documentation leaves the
    result undefined if one arrives. Instead, the value is rejected before
    the frame is built. So the run stops visibly, the notice names the fat
    compartment, and no trace moves.
    """

    controller = SimulationController()
    controller.start()
    view = _shown_view(application, controller)
    for _ in range(50):
        controller.advance(SIMULATION_STEP_S)
    view.render_tick()
    chart = _concentration(view).chart
    before = {quantity: chart.drawn_points(0, quantity) for quantity in COMPARTMENT_QUANTITIES}

    _refusing_a_drawn_column(controller, RecordedQuantity.FAT, value)
    for _ in range(50):
        controller.advance(SIMULATION_STEP_S)

    view.render_tick()

    status = controller.status()
    run = view.runs[0]

    assert controller.has_failed is True
    assert status.failure_reason is not None
    assert status.failure_reason.startswith(
        f"SimulationConfigurationError: fat partial_pressure_fraction of {value} is outside 0 to 1"
    )
    assert run._status_text.text() == "Stopped — simulation error"
    notice = run._notice_text.notice()
    assert notice is not None
    assert f"fat partial_pressure_fraction of {value}" in notice
    assert {
        quantity: chart.drawn_points(0, quantity) for quantity in COMPARTMENT_QUANTITIES
    } == before


def test_two_runs_that_come_to_be_on_different_agents_halt_visibly(
    application: QApplication,
) -> None:
    """The same failure through a real refusal rather than a patched one.

    `assemble_chart_frame` refuses two runs on two agents on every attempt,
    so the halt it causes can never be drawn as a frame. Each run still says
    that it stopped, and why, from its own snapshot.
    """

    first = SimulationController()
    second = SimulationController()
    view = _shown_view(application, first, second)
    second.set_agent("desflurane")
    first.start()

    view.render_tick()

    for controller in (first, second):
        assert controller.is_running is False
        assert controller.has_failed is True
        reason = controller.snapshot().failure_reason
        assert reason is not None
        assert reason.startswith("ValueError")

    for run in view.runs:
        assert run._status_text.text() == "Stopped — simulation error"
        notice = run._notice_text.notice()
        assert notice is not None
        assert "ValueError" in notice


def test_a_resize_while_paused_redraws_the_frame_for_the_new_width(
    application: QApplication,
) -> None:
    """`PL-GS3R`: no chord wider than a pixel, at the width the plot has now.

    A frame is assembled for the width it is drawn on, so the frame on screen
    is right for that width only. On a paused run with no frame owed, nothing
    would redraw after a resize. The columns drawn for the narrow plot would
    then stay on the wide plot, at twice the chord.
    """

    controller = _paused_run_with_history()
    view = _shown_view(application, controller, width_px=800)
    presented = view.presented_frames

    view.resize(1600, _WINDOW_HEIGHT_PX)
    application.processEvents()

    assert _widest_chord_px(view) > 1, "the resize did not widen the plot under the old frame"

    view.render_tick()

    assert view.presented_frames == presented + 1
    assert _widest_chord_px(view) <= 1

    view.render_tick()

    assert view.presented_frames == presented + 1, "the tick kept drawing with nothing owed"
