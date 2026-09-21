"""What the dashboard claims, held without a toolkit.

`app/dashboard_frame.py` is where the dashboard's presentation-correctness
claims live - which word states the run's state, which banner outranks
which, what each readout and setting says, what the captions and the
new-case question say - and every test here runs with no display and no
widget, which is the point of that module. The tests are the Flet suite's
(`tests/unit/test_simulation_view.py`) re-expressed against the frame
functions, under the same names where the claim survives the port, so the
verify lines and `docs/MODEL.md` citations that name them keep pointing at
a test that holds the same thing (`PL-25KS`).

Snapshots come either from a real `SimulationController` stepped at the
shipped step, or from `_snapshot`, a fixture whose MAC and MAC-awake resolve
from the named agent's data file so a test cannot pair one agent's
concentrations with another agent's divisor. Where a claim needs the frame
the chart drew - the off-scale notice, the undrawn-mark count, the
time-axis caption - `_FakeController` answers `drawn_window` with exactly
the samples the fixture wrote, so the test asserts the frame's reading of
those samples rather than the sampler's column placement.
"""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import pytest

from anesthesia_sim.app.bookmarks import (
    BookmarkSet,
    BookmarkStandings,
    MacTarget,
    MarkStanding,
    TimeBookmark,
)
from anesthesia_sim.app.chart_frame import (
    MAX_CHART_CONTROL_MARKS,
    ChartFrame,
    RunInput,
    assemble_chart_frame,
    trace_style,
)
from anesthesia_sim.app.chart_time_base import ChartTimeBase, time_base_for_span
from anesthesia_sim.app.control_record import CONTROL_INPUT_UNITS, ControlChange, ControlInput
from anesthesia_sim.app.control_timeline import ControlAdjustment, group_adjustments
from anesthesia_sim.app.controller import ResumePoint, SimulationController, SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_UNIT_CAPTION,
    BRANCH_AGENT_LOCK_TEXT,
    COMPARING_AGENT_LOCK_TEXT,
    COMPARING_FORK_LOCK_TEXT,
    CONTROL_MARK_LEGEND_LABEL,
    CONTROL_TIMELINE_CAPTION,
    EMPTY_METRIC_QUALIFIER,
    EMPTY_METRIC_SECONDARY_VALUE,
    INTERPRETATION_DISCLAIMER_TEXT,
    MAC_TARGET_HEADING,
    MARK_STANDING_COMPARED_TEXT,
    MARK_STANDING_JOINER,
    MARK_STANDING_TEXT,
    MARK_STILL_RUNNING_TEXT,
    MAX_DISPLAYED_RUNS,
    MAX_LISTED_ADJUSTMENTS,
    NEW_CASE_CARRYOVER_TEMPLATE,
    NEW_CASE_IS_NOT_A_VIEW_TEXT,
    NO_CONTROL_CHANGES_TEXT,
    READOUT_PANELS,
    READOUT_RESERVATIONS,
    READOUT_ROW_LADDER,
    RENDER_INTERVAL_S,
    RUNNING_AGENT_LOCK_TEXT,
    SIMULATION_STEP_S,
    SIMULATION_TICK_INTERVAL_S,
    STATUS_FAILED_TEXT,
    STATUS_PAUSED_TEXT,
    STATUS_RUNNING_TEXT,
    TIME_BOOKMARK_HEADING,
    USE_DISCLAIMER_TEXT,
    WIDEST_COMPARTMENT_SECONDARY,
    WIDEST_COMPARTMENT_VALUE,
    WIDEST_READOUT_SECONDARY,
    WIDEST_READOUT_VALUE,
    BookmarkPanel,
    Emphasis,
    HaltDisposition,
    RunMarks,
    accounting,
    bookmark_panel,
    delivered_fraction,
    fork_offer,
    format_mac_target,
    format_time_bookmark,
    halt_disposition,
    mac_awake_caption,
    mac_reference_caption,
    new_case_question,
    no_traces_shown,
    notice,
    off_scale_notice,
    readout_columns,
    readout_row_width,
    readouts,
    refused_setting_notice,
    run_label,
    setting_readouts,
    slider_position,
    slider_value,
    status_word,
    substance_heading,
    time_axis_caption,
    timeline_panel,
    transport,
    wash_in_state,
)
from anesthesia_sim.app.formatting import (
    CHART_AXIS_TOP_MAC,
    CONCENTRATION_DISPLAY_DECIMALS,
    FLOW_DISPLAY_DECIMALS,
    MAC_UNIT_SUFFIX,
    format_case_discard_warning,
    format_chart_time_label,
    format_elapsed,
    format_mac_awake_reference,
    format_mac_multiple,
    format_mac_reference,
    format_percent,
    format_playback_rate,
    format_time_base,
    format_wash_in_ratio,
    render_mac_multiple,
)
from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    PlaybackRate,
)
from anesthesia_sim.app.run_series import (
    COMPARTMENT_QUANTITIES,
    COMPARTMENT_STATE_INDEX,
    DrawnWindow,
    RecordedQuantity,
)
from anesthesia_sim.core.concentration import Fraction, MacMultiple, Percent
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
)
from anesthesia_sim.core.governing_equations import STATE_SIZE, UNIT_STATE
from anesthesia_sim.core.parameters import (
    AGENT_DATA_FILENAMES,
    MacAwakeReference,
    load_agent_parameters,
)
from anesthesia_sim.core.run_definition import DisplayState
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
)
from anesthesia_sim.core.uptake_system import MAXIMUM_SIMULATION_STEP_S

#: The agent every fixture here runs unless it says otherwise. Named once
#: because the snapshot and the recorded run have to agree on it.
_DEFAULT_AGENT = "sevoflurane"

#: The plot width every frame here is assembled for. Wide enough that no
#: fixture is thinned, so a drawn point is a fixture sample.
_PLOT_WIDTH_PX = 900.0


@dataclass(frozen=True, slots=True)
class _Sample:
    """One instant of one substance's six compartments, as a fixture writes it."""

    elapsed_s: float
    substances: Mapping[str, Mapping[RecordedQuantity, float]]


def _sample(
    elapsed_s: float,
    circuit: float,
    alveolar: float,
    venous: float,
    vessel_rich: float,
    muscle: float,
    fat: float,
    substance_id: str = _DEFAULT_AGENT,
) -> _Sample:
    return _Sample(
        elapsed_s=elapsed_s,
        substances={
            substance_id: {
                RecordedQuantity.CIRCUIT: circuit,
                RecordedQuantity.ALVEOLAR: alveolar,
                RecordedQuantity.MIXED_VENOUS: venous,
                RecordedQuantity.VESSEL_RICH: vessel_rich,
                RecordedQuantity.MUSCLE: muscle,
                RecordedQuantity.FAT: fat,
            }
        },
    )


def _state_of(sample: _Sample, substance_id: str) -> tuple[float, ...]:
    """One recorded sample as a state vector, in `governing_equations`' order."""

    values = sample.substances[substance_id]
    state = [0.0] * STATE_SIZE

    for quantity, position in COMPARTMENT_STATE_INDEX.items():
        state[position] = values[quantity]

    state[UNIT_STATE] = 1.0

    return tuple(state)


def _panel(marks: BookmarkSet) -> BookmarkPanel:
    """That set's panel on one run, with every mark standing as still reachable."""

    return bookmark_panel(marks, _one_run(_unreached(marks)))


def _one_run(standings: BookmarkStandings) -> tuple[RunMarks, ...]:
    """A lone run's marks, which is what a panel test wants unless it is comparing.

    A lone run is given no name - `SimulationView._rename_runs` states the
    rule and `run_label` is where the word comes from when there is one - so
    the label here is the one the dashboard would pass and no row draws it.
    """

    return (RunMarks(run_label(0), standings),)


def _two_runs(trunk: BookmarkStandings, branch: BookmarkStandings) -> tuple[RunMarks, ...]:
    """A trunk and a branch drawn together, in the order the dashboard adds them.

    `SimulationView.add_run` appends, and Reset truncates back to the first
    run, so the trunk is always run 1 and a branch is always run 2.
    """

    return (RunMarks(run_label(0), trunk), RunMarks(run_label(1), branch))


def _unreached(marks: BookmarkSet) -> BookmarkStandings:
    """Standings for a run that has reached none of its marks and can still reach all.

    Which is what a panel test wants by default: the rows carry the mark's own
    value, and the standing is the one that adds no words to them.
    """

    return _standings(marks)


def _standings(
    marks: BookmarkSet,
    *,
    reached_instants_s: frozenset[float] = frozenset(),
    reached_crossings: frozenset[tuple[RecordedQuantity, float]] = frozenset(),
    opened_at_s: float = 0.0,
    elapsed_s: float = 0.0,
    stopped_at_cap: bool = False,
    run_failed: bool = False,
) -> BookmarkStandings:
    """One run's standings on that set, defaulting to a run that has just opened.

    The cap is the model's own rather than a number written here, so a test
    that means "not at the cap" cannot come to disagree with the run length
    `core/supported_ranges.py` supports.
    """

    return marks.standings(
        reached_instants_s=reached_instants_s,
        reached_crossings=reached_crossings,
        opened_at_s=opened_at_s,
        elapsed_s=elapsed_s,
        run_length_cap_s=MAXIMUM_ELAPSED_SIMULATION_TIME_S,
        stopped_at_cap=stopped_at_cap,
        run_failed=run_failed,
    )


def _snapshot(
    is_running: bool = False,
    passes_validation: bool = True,
    history: tuple[_Sample, ...] | None = None,
    agent_id: str = _DEFAULT_AGENT,
    agent_display_name: str = "Sevoflurane",
    max_delivered_concentration_percent: float = 8.0,
    agent_mac_percent: float | None = None,
    agent_mac_awake: MacAwakeReference | None = None,
    control_timeline: tuple[ControlChange, ...] = (),
    bookmarks: BookmarkSet | None = None,
    failure_reason: str | None = None,
    supported_limit_reason: str | None = None,
    delivered_agent_l: float = 0.012345,
    exhausted_agent_l: float = 0.002345,
    stored_agent_l: float = 0.01,
) -> SimulationSnapshot:
    """Build a snapshot, defaulting MAC and MAC-awake from the named agent's data file.

    Both resolve from the data file rather than from a literal so that a
    test naming an agent cannot pair that agent's concentrations with
    another agent's MAC, which is the presentation failure the MAC readouts
    have to be proof against. The six compartment fractions are read from
    the last sample of `history` under the agent the snapshot names.
    """

    if history is None:
        history = (_sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id=agent_id),)

    if agent_mac_percent is None:
        agent_mac_percent = load_agent_parameters(agent_id).mac_percent

    if agent_mac_awake is None:
        agent_mac_awake = load_agent_parameters(agent_id).mac_awake

    latest = history[-1]
    compartments = latest.substances[agent_id]

    return SimulationSnapshot(
        is_running=is_running,
        elapsed_s=latest.elapsed_s,
        agent_id=agent_id,
        agent_display_name=agent_display_name,
        max_delivered_concentration_percent=Percent(max_delivered_concentration_percent),
        agent_mac_percent=Percent(agent_mac_percent),
        agent_mac_awake=agent_mac_awake,
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=4.0,
        delivered_partial_pressure_fraction=Fraction(0.08),
        alveolar_ventilation_l_min=4.0,
        cardiac_output_l_min=5.0,
        inspired_partial_pressure_fraction=Fraction(compartments[RecordedQuantity.CIRCUIT]),
        alveolar_partial_pressure_fraction=Fraction(compartments[RecordedQuantity.ALVEOLAR]),
        mixed_venous_partial_pressure_fraction=Fraction(
            compartments[RecordedQuantity.MIXED_VENOUS]
        ),
        vessel_rich_partial_pressure_fraction=Fraction(compartments[RecordedQuantity.VESSEL_RICH]),
        muscle_partial_pressure_fraction=Fraction(compartments[RecordedQuantity.MUSCLE]),
        fat_partial_pressure_fraction=Fraction(compartments[RecordedQuantity.FAT]),
        delivered_agent_l=delivered_agent_l,
        exhausted_agent_l=exhausted_agent_l,
        stored_agent_l=stored_agent_l,
        unaccounted_agent_l=1.5e-13,
        agent_accounting_absolute_error_l=1.5e-13,
        agent_accounting_passes_validation=passes_validation,
        control_timeline=control_timeline,
        bookmarks=BookmarkSet() if bookmarks is None else bookmarks,
        bookmark_halt=None,
        bookmark_standings=_unreached(BookmarkSet() if bookmarks is None else bookmarks),
        supported_limit_reason=supported_limit_reason,
        failure_reason=failure_reason,
    )


class _FakeController:
    """A run whose drawn window is exactly the samples the fixture wrote.

    The real controller evaluates its definition at instants it chooses; a
    fake has no definition, and inventing one would make every frame test
    here assert the sampler's column placement rather than the reading
    under test. Only `snapshot()`, `drawn_window()` and `opened_from` are
    answered, because those are the three things `assemble_chart_frame` asks
    a run for.
    """

    def __init__(
        self,
        snapshot: SimulationSnapshot,
        history: tuple[_Sample, ...],
        opened_from: ResumePoint | None = None,
    ) -> None:
        self.snapshot_value = snapshot
        self.history_value = history
        #: Where this run forked, or `None` for one that is not a branch.
        #: A frame marks the fork, so the fake has to be able to be one.
        self.opened_from = opened_from

    def snapshot(self) -> SimulationSnapshot:
        return self.snapshot_value

    def drawn_window(self, start_s: float, stop_s: float, columns: int) -> DrawnWindow:
        inside = [sample for sample in self.history_value if start_s <= sample.elapsed_s <= stop_s]

        if len(inside) > columns:
            step = (len(inside) - 1) / (columns - 1)
            inside = [inside[round(column * step)] for column in range(columns)]

        substance_id = next(iter(self.history_value[0].substances))

        return DrawnWindow(
            substance_id=substance_id,
            times_s=tuple(sample.elapsed_s for sample in inside),
            states=tuple(DisplayState(_state_of(sample, substance_id)) for sample in inside),
        )


def _fake_controller(
    history: tuple[_Sample, ...] | None = None, **snapshot_fields: Any
) -> _FakeController:
    """A fake whose snapshot and history come from one run, built together."""

    snapshot = _snapshot(history=history, **snapshot_fields)

    if history is None:
        history = (_sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id=snapshot.agent_id),)

    return _FakeController(snapshot, history)


def _frame(
    controller: Any,
    *,
    shown: Sequence[RecordedQuantity] = COMPARTMENT_QUANTITIES,
    time_base: ChartTimeBase | None = None,
    adjustments: tuple[ControlAdjustment, ...] = (),
) -> ChartFrame:
    """The frame one tick would draw for one run, under "Fit run" unless told otherwise."""

    return assemble_chart_frame(
        (RunInput(run_label(0), controller, controller.snapshot(), adjustments),),
        time_base,
        shown,
        plot_width_px=_PLOT_WIDTH_PX,
    )


def _run_history(sample_count: int, substance_id: str = _DEFAULT_AGENT) -> tuple[_Sample, ...]:
    """A run of `sample_count` samples at the real 0.1 s simulation step."""

    return tuple(
        _sample(
            index * SIMULATION_STEP_S,
            0.08 * (1.0 - 0.5**index),
            0.07 * (1.0 - 0.5**index),
            0.06 * (1.0 - 0.5**index),
            0.05 * (1.0 - 0.5**index),
            0.04 * (1.0 - 0.5**index),
            0.03 * (1.0 - 0.5**index),
            substance_id=substance_id,
        )
        for index in range(sample_count)
    )


def _control_change(
    elapsed_s: float,
    control: ControlInput,
    previous_value: float,
    new_value: float,
    adjustment: int,
) -> ControlChange:
    return ControlChange(
        elapsed_s=elapsed_s,
        adjustment=adjustment,
        control=control,
        previous_value=previous_value,
        new_value=new_value,
        unit=CONTROL_INPUT_UNITS[control],
    )


def _advance_to(controller: SimulationController, elapsed_s: float) -> None:
    """Step a started controller to `elapsed_s` at the shipped step size."""

    while controller.snapshot().elapsed_s < elapsed_s - SIMULATION_STEP_S / 2.0:
        controller.advance(SIMULATION_STEP_S)


def _paused_run_with_history(elapsed_s: float = 60.0) -> SimulationController:
    """A real, paused run holding both elapsed time and a recorded input.

    Both halves deliberately: `SimulationSnapshot.has_recorded_run` reads
    the two together, and a fixture carrying only one would leave the other
    unexercised by every test built on it.
    """

    controller = SimulationController()
    controller.start()
    _advance_to(controller, elapsed_s=elapsed_s)
    controller.set_fresh_gas_flow(2.0)
    controller.pause()

    return controller


def _readouts_by_name(snapshot: SimulationSnapshot) -> dict[str, tuple[str, str, str]]:
    """Each readout's (qualifier, value, secondary), keyed by its name."""

    return {
        readout.name: (readout.qualifier, readout.value, readout.secondary)
        for readout in readouts(snapshot, DEFAULT_PLAYBACK_RATE)
    }


def _settings_by_control(snapshot: SimulationSnapshot) -> dict[ControlInput, Any]:
    return {setting.control: setting for setting in setting_readouts(snapshot)}


# --- cadence constants --------------------------------------------------------


def test_the_shipped_step_is_within_the_maximum_simulation_step() -> None:
    """The interface may not run the model outside its supported domain.

    `SIMULATION_STEP_S` is the dashboard's cadence and
    `MAXIMUM_SIMULATION_STEP_S` is `core/`'s declared control-resolution
    tolerance; they are separate decisions that happen to coincide today,
    and this is what stops them from parting company unnoticed. The
    relation is `<=` rather than equality on purpose: a numerical method
    that supported a coarser step would not make a coarser step a good
    render cadence.
    """

    assert SIMULATION_STEP_S <= MAXIMUM_SIMULATION_STEP_S


def test_a_tick_is_one_simulation_step_of_real_time() -> None:
    """The equality every displayed playback rate is derived through.

    A tick advances `steps_per_tick` steps, and calling that "N times real
    time" is true only because one tick is one step long.
    """

    assert SIMULATION_TICK_INTERVAL_S == SIMULATION_STEP_S


def test_a_frame_is_two_control_grid_steps_at_every_rate() -> None:
    """The premise of the argument `PL-NBWP` was settled on.

    A reader sees the run at half the resolution they can act on it at, at
    every rate the ladder offers; `docs/MODEL.md` § "Supported simulation
    step" argues from this ratio, so it is held here rather than derived.
    """

    assert RENDER_INTERVAL_S == 2.0 * SIMULATION_TICK_INTERVAL_S


def test_the_dashboard_displays_at_most_two_runs() -> None:
    """`ROADMAP.md` § "v0.5.0 - the case you can branch": never more than two.

    The constructor's refusal is `SimulationView`'s and is tested with the
    widget; the number itself is the frame's, and `PL-HLD5`'s two-level
    encoding (run on line width, under a cap of two compartments) has
    nothing left to draw a third run with.
    """

    assert MAX_DISPLAYED_RUNS == 2


# --- status word, notice banner, transport ------------------------------------


@pytest.mark.parametrize(
    ("is_running", "expected_status", "expected_emphasis", "start_enabled", "pause_enabled"),
    [
        (True, "Running", Emphasis.ACCENT, False, True),
        (False, "Paused", Emphasis.MUTED, True, False),
    ],
)
def test_refresh_view_reflects_running_state(
    is_running: bool,
    expected_status: str,
    expected_emphasis: Emphasis,
    start_enabled: bool,
    pause_enabled: bool,
) -> None:
    snapshot = _snapshot(is_running=is_running)

    assert status_word(snapshot).text == expected_status
    assert status_word(snapshot).emphasis is expected_emphasis
    assert transport(snapshot).start_enabled is start_enabled
    assert transport(snapshot).pause_enabled is pause_enabled


def test_refresh_view_reports_a_failed_run_as_stopped_not_paused() -> None:
    snapshot = _snapshot(failure_reason="SimulationNumericalError: the step could not be completed")

    assert status_word(snapshot).text == "Stopped — simulation error"
    assert status_word(snapshot).emphasis is Emphasis.WARNING

    banner = notice(snapshot, None)

    assert banner is not None
    assert "the step could not be completed" in banner
    # PL-026: the numbers beside the banner are the last completed step,
    # because the core rolls a failed step back. The reader has to be told
    # that much - a banner that only says something went wrong leaves them
    # to guess whether the values are a solution of the model or debris.
    assert "last completed step" in banner
    assert "rolled back" in banner
    assert banner == (
        "Simulation stopped — SimulationNumericalError: the step could not be completed. "
        "The values shown are the last completed step; the step that failed was rolled "
        "back and changed nothing. Reset to start a new run."
    )


def test_refresh_view_does_not_offer_to_resume_a_failed_run() -> None:
    enablement = transport(_snapshot(failure_reason="SimulationNumericalError: boom"))

    assert enablement.start_enabled is False
    assert enablement.pause_enabled is False


def test_refresh_view_shows_no_notice_for_an_ordinary_run() -> None:
    for is_running in (True, False):
        snapshot = _snapshot(is_running=is_running)

        assert notice(snapshot, None) is None
        assert status_word(snapshot).text in {"Running", "Paused"}


def test_refresh_view_reports_the_supported_run_length_as_stopped_not_failed() -> None:
    """The whole point of the separate field: a correct stop reads as one.

    A run that reaches 24 hours has done everything right - the core refused
    the next step before taking it, nothing was miscalculated, nothing was
    rolled back. Presenting that as "simulation error" would spend the one
    signal this interface has for a real fault on a model that is working.
    """

    snapshot = _snapshot(
        is_running=False, supported_limit_reason="this run has reached 86400 s of simulated time"
    )

    assert status_word(snapshot).text == "Stopped — supported run length reached"
    assert status_word(snapshot).emphasis is not Emphasis.WARNING

    banner = notice(snapshot, None)

    assert banner is not None
    assert "supported run length of 24 hours" in banner


def test_the_supported_run_length_notice_does_not_describe_a_failure() -> None:
    """No step failed and none was rolled back, so neither may be claimed.

    A notice describing an event that did not happen is the presentation
    half of the safety-critical standard - the correct number under the
    wrong label - and it points the reader at the model's own limits rather
    than at an imagined defect.
    """

    banner = notice(
        _snapshot(
            is_running=False,
            supported_limit_reason="this run has reached 86400 s of simulated time",
        ),
        None,
    )

    assert banner is not None
    assert "rolled back" not in banner
    assert "error" not in banner.lower()
    assert "failed" not in banner.lower()
    # It says *why* the limit is where it is: a boundary with no reason reads
    # as an arbitrary restriction rather than as the edge of the model.
    assert "metabolism" in banner
    assert "last completed step" in banner
    assert banner == (
        "Simulation stopped — this run reached the supported run length of 24 hours. "
        "Beyond it this model's omitted metabolism and its fat perfusion dominate the "
        "trace, so it is not claimed to represent a patient. The values shown are the "
        "last completed step, inside the supported span. Reset to start a new run."
    )


def test_refresh_view_does_not_offer_to_resume_a_run_at_the_supported_limit() -> None:
    """The controller would refuse this Start, so the button must not offer it."""

    enablement = transport(
        _snapshot(
            is_running=False,
            supported_limit_reason="this run has reached 86400 s of simulated time",
        )
    )

    assert enablement.start_enabled is False


def test_a_failure_outranks_the_supported_run_length_in_the_notice() -> None:
    """Where both are somehow recorded, the more serious statement wins."""

    snapshot = _snapshot(
        is_running=False,
        failure_reason="SimulationNumericalError: boom",
        supported_limit_reason="this run has reached 86400 s of simulated time",
    )
    banner = notice(snapshot, None)

    assert status_word(snapshot).text == "Stopped — simulation error"
    assert banner is not None
    assert "boom" in banner


def test_a_refused_setting_is_still_a_notice_and_not_a_halt() -> None:
    """A `SimulationConfigurationError` means the core rejected a value and changed nothing.

    The run is untouched and must not be marked failed, so the refusal is
    worded as a notice about one control over a run that goes on unchanged
    (`PL-YK2V`). `halt_disposition` is never consulted for it: which
    exceptions reach that function is `RunView._apply_setting`'s, tested
    with the widget.
    """

    refused = refused_setting_notice(SimulationConfigurationError("a value the core refused"))

    assert refused == "Setting refused — a value the core refused"
    assert notice(_snapshot(is_running=True), refused) == (
        "Setting refused — a value the core refused. "
        "The simulation is unchanged and still running its previous setting."
    )


def test_a_stopped_run_outranks_a_refused_setting_in_the_notice() -> None:
    """A stopped run describes everything on screen; a refusal describes one control."""

    refused = refused_setting_notice(SimulationConfigurationError("a value the core refused"))
    failed = _snapshot(failure_reason="SimulationNumericalError: boom")
    at_limit = _snapshot(supported_limit_reason="this run has reached 86400 s of simulated time")

    failure_banner = notice(failed, refused)
    limit_banner = notice(at_limit, refused)

    assert failure_banner is not None and "boom" in failure_banner
    assert limit_banner is not None and "supported run length" in limit_banner
    assert "Setting refused" not in failure_banner
    assert "Setting refused" not in limit_banner


def test_the_transport_is_enabled_by_state_in_all_four_states() -> None:
    """Start only where the controller would accept it; Pause only while running; Reset always.

    The selector is locked exactly while running, because choosing an agent
    discards the case and the selector returns on Pause (`PL-61WW`).
    """

    limit = "this run has reached 86400 s of simulated time"
    paused = transport(_snapshot(is_running=False))
    running = transport(_snapshot(is_running=True))
    failed = transport(_snapshot(failure_reason="SimulationNumericalError: boom"))
    at_limit = transport(_snapshot(supported_limit_reason=limit))

    assert (paused.start_enabled, paused.pause_enabled) == (True, False)
    assert (running.start_enabled, running.pause_enabled) == (False, True)
    assert (failed.start_enabled, failed.pause_enabled) == (False, False)
    assert (at_limit.start_enabled, at_limit.pause_enabled) == (False, False)
    assert all(state.reset_enabled for state in (paused, running, failed, at_limit))
    assert [state.selector_locked for state in (paused, running, failed, at_limit)] == [
        False,
        True,
        False,
        False,
    ]


# --- halt routing ---------------------------------------------------------------


def test_halt_run_routes_the_supported_run_length_away_from_failure() -> None:
    """A halt stops the run for every exception and mislabels none.

    A regression in the routing would not break the halt - the run still
    stops - it would only put "simulation error" over a model that stopped
    exactly where `docs/MODEL.md` says it must. Nothing but a test notices.
    """

    error = SimulationDomainLimitError("this run has reached 86400 s of simulated time")

    assert halt_disposition(error) == (
        HaltDisposition.SUPPORTED_LIMIT,
        "this run has reached 86400 s of simulated time",
    )


def test_halt_run_still_treats_an_unrecognised_exception_as_a_failure() -> None:
    """The narrow case is the named one, so anything else falls through safely."""

    assert halt_disposition(ValueError("mass balance violated")) == (
        HaltDisposition.FAILURE,
        "ValueError: mass balance violated",
    )


def test_a_settings_raise_outside_the_project_hierarchy_halts_the_run() -> None:
    """`PL-YK2V`: a `TypeError` from a future refactor stops the run like a modelling failure.

    It is recorded with its type, because the reader is looking at a
    display that can no longer be trusted to describe the run and the
    reason has to be readable.
    """

    assert halt_disposition(TypeError("a future refactor changed a signature")) == (
        HaltDisposition.FAILURE,
        "TypeError: a future refactor changed a signature",
    )


def test_a_settings_execution_error_halts_the_run_instead_of_reading_as_refused() -> None:
    """`PL-V6M0`: `SimulationExecutionError` is the run being unable to continue safely.

    The opposite of a refused setting, so it takes the failure channel with
    the rest of the hierarchy.
    """

    assert halt_disposition(SimulationExecutionError("the run cannot continue safely")) == (
        HaltDisposition.FAILURE,
        "SimulationExecutionError: the run cannot continue safely",
    )


def test_a_settings_domain_limit_reaches_the_supported_limit_channel() -> None:
    """The milder half of `PL-V6M0`: a domain limit is neither a failure nor a refusal."""

    disposition, reason = halt_disposition(
        SimulationDomainLimitError("this run has reached 86400 s of simulated time")
    )

    assert disposition is HaltDisposition.SUPPORTED_LIMIT
    assert reason == "this run has reached 86400 s of simulated time"


# --- the seven readouts -------------------------------------------------------


def test_refresh_view_formats_every_concentration_metric() -> None:
    snapshot = _snapshot(
        history=(_sample(12.5, 0.02345, 0.01234, 0.00456, 0.00789, 0.00321, 0.00012),)
    )
    by_name = _readouts_by_name(snapshot)
    settings = _settings_by_control(snapshot)

    assert by_name["Simulated time"][1] == "12.5s"
    assert by_name["Circuit"][1] == "2.34%"
    assert by_name["Alveolar"][1] == "1.23%"
    assert by_name["Mixed venous"][1] == "0.46%"
    assert by_name["Vessel-rich group"][1] == "0.79%"
    assert by_name["Muscle"][1] == "0.32%"
    assert by_name["Fat"][1] == "0.01%"
    assert settings[ControlInput.FRESH_GAS_FLOW].value_text == "4.0 L/min"
    assert settings[ControlInput.DELIVERED].value_text == "8.00%"
    assert settings[ControlInput.ALVEOLAR_VENTILATION].value_text == "4.0 L/min"
    assert settings[ControlInput.CARDIAC_OUTPUT].value_text == "5.0 L/min"


def test_metric_placeholders_match_the_formatter_before_a_run() -> None:
    """The pre-run reading must not outlive a change to the resolution."""

    empty = format_percent(Fraction(0.0))

    for readout in readouts(SimulationController().snapshot(), DEFAULT_PLAYBACK_RATE)[1:]:
        assert readout.value == empty


def test_a_real_run_displays_a_filling_compartment_as_below_resolution() -> None:
    """End to end: real model, real step, real units, displayed string.

    Fat is the compartment the PL-040 decision turns on. Two minutes into a
    1 MAC sevoflurane run it holds agent but less than 0.01% of it, so the
    display must say so rather than round it to an empty compartment; by
    twenty minutes it has risen into the resolved range.
    """

    controller = SimulationController()
    controller.start()
    _advance_to(controller, 120.0)

    assert controller.snapshot().fat_partial_pressure_fraction > 0.0
    assert _readouts_by_name(controller.snapshot())["Fat"][1] == "<0.01%"
    # The alveolar reading over the same interval is an ordinary value at
    # the documented resolution, so the marker is specific to what is
    # genuinely below it rather than a formatting quirk.
    assert _readouts_by_name(controller.snapshot())["Alveolar"][1] == "0.61%"

    _advance_to(controller, 1_200.0)

    assert _readouts_by_name(controller.snapshot())["Fat"][1] == "0.01%"


# The exact strings the alveolar readout must carry, restated rather than
# imported. An import would move both sides of the assertion together, which
# is precisely the edit these tests exist to catch.
_ALVEOLAR_METRIC_NAME = "Alveolar"
_ALVEOLAR_METRIC_QUALIFIER = "end-tidal-equivalent"
_FRESH_GAS_FLOW_LABEL = "Fresh gas flow"
_FRESH_GAS_FLOW_QUALIFIER = "common gas outlet"


def test_the_alveolar_readout_is_labelled_end_tidal_equivalent() -> None:
    """The hedge is a safety requirement, not a wording preference.

    `docs/MODEL.md` § "Minimum displayed outputs" requires "alveolar or
    end-tidal-equivalent concentration": dead space, airway sampling delay,
    shunt and V/Q mismatch are all in "Known limitations", so what this
    readout holds is not end-tidal in any patient, and end-tidal is the name
    of a measurement (`PL-NV9W`). The gloss being drawn smaller than the
    name is the widget's and is tested with it.
    """

    by_name = _readouts_by_name(_snapshot())

    assert _ALVEOLAR_METRIC_NAME in by_name
    assert by_name[_ALVEOLAR_METRIC_NAME][0] == _ALVEOLAR_METRIC_QUALIFIER
    assert by_name["Circuit"][0] == "inspired"


def test_every_compartment_is_readable_in_mac_multiples() -> None:
    """PL-DHV7's own acceptance criterion: the second unit is on every compartment.

    A MAC multiple on the vessel-rich, muscle and fat readouts is what makes
    a wash-in comparable across agents. "Simulated time" holds the line
    with the playback rate instead; the six compartments each carry one.
    """

    snapshot = _snapshot(history=(_sample(60.0, 0.02, 0.016, 0.008, 0.006, 0.001, 5e-5),))
    by_name = _readouts_by_name(snapshot)

    assert sum(1 for _, _, secondary in by_name.values() if "MAC" in secondary) == 6
    assert by_name["Circuit"][2] == "1.00 ×MAC"
    assert by_name["Alveolar"][2] == "0.80 ×MAC"
    assert by_name["Mixed venous"][2] == "0.40 ×MAC"
    assert by_name["Vessel-rich group"][2] == "0.30 ×MAC"
    assert by_name["Muscle"][2] == "0.05 ×MAC"
    assert by_name["Fat"][2] == "<0.01 ×MAC"


def test_each_mac_readout_uses_its_own_agent_divisor() -> None:
    """6% is 3 MAC of sevoflurane and 1 MAC of desflurane.

    A divisor left over from a previously selected agent would produce a
    plausible number under the correct label, which is the presentation
    failure `CLAUDE.md` treats as a safety failure rather than a cosmetic
    one; every MAC line is read from the snapshot's own divisor.
    """

    sevoflurane = _snapshot(history=(_sample(60.0, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06),))

    assert _readouts_by_name(sevoflurane)["Alveolar"][2] == "3.00 ×MAC"

    desflurane = _snapshot(
        agent_id="desflurane",
        agent_display_name="Desflurane",
        max_delivered_concentration_percent=18.0,
        history=(_sample(60.0, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, substance_id="desflurane"),),
    )

    assert _readouts_by_name(desflurane)["Alveolar"][2] == "1.00 ×MAC"
    assert _readouts_by_name(desflurane)["Fat"][2] == "1.00 ×MAC"


@pytest.mark.parametrize("rate", SUPPORTED_PLAYBACK_RATES, ids=lambda rate: f"{rate.multiplier}x")
def test_the_playback_rate_is_drawn_under_the_clock_it_governs(rate: PlaybackRate) -> None:
    """A rate is a mode, and the clock is where it would be misread.

    `PL-SN2C` requires the multiplier beside the elapsed-time readout - not
    merely somewhere on the page, and not only when it is not 1x - stated by
    the same formatter the selector's options use.
    """

    clock = readouts(_snapshot(), rate)[0]

    assert clock.name == "Simulated time"
    assert clock.secondary == format_playback_rate(rate.multiplier)


def test_the_clock_panel_reads_in_the_chart_axis_form_past_an_hour() -> None:
    """`PL-Q4M4`: the clock and the axis state one quantity one way."""

    clock = readouts(
        _snapshot(history=(_sample(5400.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),)), DEFAULT_PLAYBACK_RATE
    )[0]

    assert clock.value == "1h30m"
    assert clock.value == format_chart_time_label(5400.0)


def test_the_readout_row_names_the_substance_its_numbers_belong_to() -> None:
    """`PL-TCD1`: one frame, one vocabulary, following the agent."""

    assert substance_heading(_snapshot()) == "Modelled concentrations: Sevoflurane"
    assert (
        substance_heading(
            _snapshot(
                agent_id="desflurane",
                agent_display_name="Desflurane",
                max_delivered_concentration_percent=18.0,
            )
        )
        == "Modelled concentrations: Desflurane"
    )


def test_every_readout_holds_its_gloss_and_second_unit_lines_open() -> None:
    """Seven panels on one baseline (`PL-8M05`): every line is a non-empty string.

    A readout with no gloss and the clock with no MAC multiple still hold
    their lines, so a widget drawing the four lines never collapses one.
    The widest reflow step seats all seven side by side.
    """

    panels = readouts(_snapshot(), DEFAULT_PLAYBACK_RATE)

    assert len(panels) == len(READOUT_PANELS) == 7
    for panel in panels:
        assert panel.name, "a readout with no name"
        assert panel.qualifier, "a readout that does not hold its gloss line open"
        assert panel.value
        assert panel.secondary, "a readout that does not hold its second-unit line open"

    assert panels[3].qualifier == EMPTY_METRIC_QUALIFIER
    assert EMPTY_METRIC_QUALIFIER == EMPTY_METRIC_SECONDARY_VALUE == " "
    assert max(READOUT_ROW_LADDER) == len(panels)


def test_the_widest_readout_strings_are_the_formatters_own_extremes() -> None:
    """`PL-3355`: a panel reserves width for the widest value it can show.

    The clock just before the supported run length is the widest value
    line - every component of the compound form present, with tenths - and
    the longest playback rate is the widest second line. Both are derived
    from the formatters rather than measured, so a change to either form
    moves the reservation with it.
    """

    assert WIDEST_READOUT_VALUE == format_elapsed(MAXIMUM_ELAPSED_SIMULATION_TIME_S - 0.1)
    assert WIDEST_READOUT_VALUE == "23h59m59.9s"
    assert len(WIDEST_READOUT_VALUE) >= len(format_percent(Fraction(1.0)))
    assert WIDEST_READOUT_SECONDARY == max(
        (format_playback_rate(rate.multiplier) for rate in SUPPORTED_PLAYBACK_RATES), key=len
    )
    assert len(WIDEST_READOUT_SECONDARY) >= len(format_mac_multiple(Fraction(1e-9), Percent(2.0)))


# --- the four setting controls -----------------------------------------------


def test_the_sliders_span_the_supported_input_ranges() -> None:
    """The interface offers exactly the domain the model declares.

    Equality in both directions: a slider reaching past a supported maximum
    hands the reader a setting `core/` refuses, and one stopping short
    silently narrows the reachable domain below what the reference gates
    were driven at (`PL-0MLQ`).
    """

    settings = _settings_by_control(SimulationController().snapshot())

    assert (
        settings[ControlInput.FRESH_GAS_FLOW].minimum,
        settings[ControlInput.FRESH_GAS_FLOW].maximum,
        settings[ControlInput.ALVEOLAR_VENTILATION].minimum,
        settings[ControlInput.ALVEOLAR_VENTILATION].maximum,
        settings[ControlInput.CARDIAC_OUTPUT].minimum,
        settings[ControlInput.CARDIAC_OUTPUT].maximum,
    ) == (
        MINIMUM_FRESH_GAS_FLOW_L_MIN,
        MAXIMUM_FRESH_GAS_FLOW_L_MIN,
        MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MINIMUM_CARDIAC_OUTPUT_L_MIN,
        MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    )


def test_every_slider_endpoint_is_a_setting_the_core_accepts() -> None:
    """Dragging a slider to either end must never raise out of `core/`.

    Each endpoint is taken through the integer slider's own round trip
    before it reaches the controller, so what is applied is exactly what
    the slider can produce. The delivered dial is included because its
    maximum is the agent's own vaporizer limit, which is instance state and
    cannot be compared against a constant.
    """

    controller = SimulationController()
    setters: dict[ControlInput, Callable[[float], None]] = {
        ControlInput.FRESH_GAS_FLOW: controller.set_fresh_gas_flow,
        ControlInput.ALVEOLAR_VENTILATION: controller.set_alveolar_ventilation,
        ControlInput.CARDIAC_OUTPUT: controller.set_cardiac_output,
        ControlInput.DELIVERED: lambda percent: controller.set_delivered_partial_pressure_fraction(
            delivered_fraction(percent)
        ),
    }

    for setting in setting_readouts(controller.snapshot()):
        for endpoint in (setting.minimum, setting.maximum):
            applied = slider_value(slider_position(endpoint, setting.decimals), setting.decimals)

            try:
                setters[setting.control](applied)
            except SimulationConfigurationError as error:
                pytest.fail(
                    f"the core refused {applied}, an endpoint of a slider the interface "
                    f"offers: {error}"
                )


def test_slider_drag_labels_match_the_readouts_beside_them() -> None:
    """One quantity must not be displayed at two resolutions at once.

    The slider steps at the readout's own decimals and in the readout's own
    unit, so the position a reader drags to and the text beside it are one
    number at one resolution (`PL-25KS`, decision D4).
    """

    settings = _settings_by_control(SimulationController().snapshot())

    assert settings[ControlInput.DELIVERED].decimals == CONCENTRATION_DISPLAY_DECIMALS
    assert settings[ControlInput.DELIVERED].unit == "%"

    for control in (
        ControlInput.FRESH_GAS_FLOW,
        ControlInput.ALVEOLAR_VENTILATION,
        ControlInput.CARDIAC_OUTPUT,
    ):
        assert settings[control].decimals == FLOW_DISPLAY_DECIMALS
        assert settings[control].unit == "L/min"

    # The flow readouts these labels must agree with.
    assert settings[ControlInput.FRESH_GAS_FLOW].value_text == "4.0 L/min"
    assert settings[ControlInput.ALVEOLAR_VENTILATION].value_text == "4.0 L/min"
    assert settings[ControlInput.CARDIAC_OUTPUT].value_text == "5.0 L/min"


def test_a_slider_position_round_trips_to_the_value_printed_beside_it() -> None:
    """The value applied to the model is exactly the value printed beside the slider.

    At both resolutions: one decimal for the three flows, two for the
    delivered percent. A position is a count of the display resolution, so
    the value it decodes to formats to itself.
    """

    assert slider_position(2.4, CONCENTRATION_DISPLAY_DECIMALS) == 240
    assert slider_value(240, CONCENTRATION_DISPLAY_DECIMALS) == 2.4
    assert slider_position(0.7, FLOW_DISPLAY_DECIMALS) == 7
    assert slider_value(7, FLOW_DISPLAY_DECIMALS) == 0.7

    for decimals in (FLOW_DISPLAY_DECIMALS, CONCENTRATION_DISPLAY_DECIMALS):
        for position in range(0, 1_801, 7):
            value = slider_value(position, decimals)

            assert slider_position(value, decimals) == position
            assert f"{value:.{decimals}f}" == f"{slider_value(position, decimals):.{decimals}f}"


def test_the_fresh_gas_flow_control_names_the_common_gas_outlet() -> None:
    """The gloss is a safety requirement, not a wording preference.

    "Fresh gas flow" alone is what a flowmeter bank is labelled, and a
    flowmeter reads the carrier gas only; the model's circuit balance makes
    this the whole post-vaporizer stream, 22% apart at desflurane's 18%
    dial (`PL-71CF`). The gloss's size and italic are the widget's.
    """

    setting = _settings_by_control(_snapshot())[ControlInput.FRESH_GAS_FLOW]

    assert setting.name == _FRESH_GAS_FLOW_LABEL
    assert setting.qualifier, "the fresh-gas-flow control carries no gloss"
    assert setting.qualifier == _FRESH_GAS_FLOW_QUALIFIER


def test_the_other_three_controls_carry_no_gloss() -> None:
    """A gloss is drawn only where a name would otherwise be misread."""

    settings = _settings_by_control(_snapshot())

    for control in (
        ControlInput.DELIVERED,
        ControlInput.ALVEOLAR_VENTILATION,
        ControlInput.CARDIAC_OUTPUT,
    ):
        assert settings[control].qualifier == ""

    assert settings[ControlInput.ALVEOLAR_VENTILATION].name == "Alveolar ventilation"
    assert settings[ControlInput.CARDIAC_OUTPUT].name == "Cardiac output"


def test_refresh_view_updates_delivered_concentration_label_for_current_agent() -> None:
    """Regression: this label was once hardcoded to "Delivered sevoflurane"."""

    snapshot = _snapshot(agent_id="desflurane", agent_display_name="Desflurane")

    assert _settings_by_control(snapshot)[ControlInput.DELIVERED].name == "Delivered desflurane"


def test_the_slider_tracks_the_dial_maximum_and_the_chart_no_longer_does() -> None:
    """Two ceilings that used to be one, and had to stop being one (`PL-CC23`).

    The delivered dial tracks the real vaporizer cap; the chart's ceiling is
    the same MAC multiple for every agent. Desflurane is where the numbers
    coincide and the reasons do not; isoflurane is where they visibly part.
    """

    desflurane = _fake_controller(
        agent_id="desflurane",
        agent_display_name="Desflurane",
        max_delivered_concentration_percent=18.0,
    )

    assert _settings_by_control(desflurane.snapshot())[ControlInput.DELIVERED].maximum == 18.0
    assert _frame(desflurane).axis_top_percent == pytest.approx(18.0)
    assert _frame(desflurane).axis_top_percent == pytest.approx(CHART_AXIS_TOP_MAC * 6.0)

    isoflurane = _fake_controller(
        agent_id="isoflurane",
        agent_display_name="Isoflurane",
        max_delivered_concentration_percent=5.0,
    )

    assert _settings_by_control(isoflurane.snapshot())[ControlInput.DELIVERED].maximum == 5.0
    assert _frame(isoflurane).axis_top_percent == pytest.approx(3.6), (
        "1.2% MAC x 3, not the 5% dial"
    )


def test_the_dial_is_readable_in_the_unit_its_compartments_are() -> None:
    """The one control a reader sets, in the units of the traces it fills."""

    delivered = _settings_by_control(_snapshot())[ControlInput.DELIVERED]

    assert delivered.value_text == format_percent(Fraction(0.08))
    assert delivered.secondary == format_mac_multiple(Fraction(0.08), Percent(2.0))
    assert delivered.secondary == "4.00 ×MAC"


def test_the_end_to_end_mac_path_reaches_the_panel_from_a_real_run() -> None:
    """Patient inputs, model selection, calculation, units, formatting, display."""

    controller = SimulationController(agent_id="desflurane")
    controller.start()

    for _ in range(600):
        controller.advance(SIMULATION_STEP_S)

    snapshot = controller.snapshot()

    assert snapshot.agent_mac_percent == 6.0
    assert _readouts_by_name(snapshot)["Alveolar"][2] == format_mac_multiple(
        snapshot.alveolar_partial_pressure_fraction, Percent(6.0)
    )
    # The dial starts at the agent's own 1 MAC, so after a minute of wash-in
    # the alveolar compartment is somewhere below it and above nothing.
    alveolar_mac = snapshot.alveolar_partial_pressure_fraction * 100.0 / 6.0
    assert 0.0 < alveolar_mac < 1.0
    assert _settings_by_control(snapshot)[ControlInput.DELIVERED].secondary == "1.00 ×MAC"


def test_delivered_concentration_slider_converts_percent_to_fraction() -> None:
    controller = SimulationController()

    controller.set_delivered_partial_pressure_fraction(delivered_fraction(6.5))

    assert controller.snapshot().delivered_partial_pressure_fraction == pytest.approx(0.065)
    assert _settings_by_control(controller.snapshot())[ControlInput.DELIVERED].value_text == (
        "6.50%"
    )


# --- the accounting panel ------------------------------------------------------


def test_refresh_view_reports_valid_agent_accounting() -> None:
    """The three amounts at one decimal of a litre (`PL-TG60`); the residuals in exponent form."""

    panel = accounting(_snapshot(passes_validation=True))

    assert panel.status.text == "Valid"
    assert panel.status.emphasis is Emphasis.ACCENT
    assert "still accounts for all delivered agent" in panel.detail
    assert panel.amounts == (
        "Delivered: <0.1 L\n"
        "Exhausted: <0.1 L\n"
        "Stored: <0.1 L\n"
        "Unaccounted: 1.500e-13 L\n"
        "Absolute error: 1.500e-13 L"
    )


def test_the_accounting_panel_prints_amounts_at_one_decimal_of_a_litre() -> None:
    """Six decimals of an exhaust total asserted a resolution the parameters do not support."""

    panel = accounting(
        _snapshot(delivered_agent_l=3.991974, exhausted_agent_l=2.06, stored_agent_l=1.9319)
    )

    assert panel.amounts.splitlines()[:3] == [
        "Delivered: 4.0 L",
        "Exhausted: 2.1 L",
        "Stored: 1.9 L",
    ]


def test_refresh_view_reports_failed_agent_accounting() -> None:
    panel = accounting(_snapshot(passes_validation=False))

    assert panel.status.text == "Validation failed"
    assert panel.status.emphasis is Emphasis.WARNING
    assert "unaccounted agent" in panel.detail


def test_the_accounting_unit_caption_names_litres_of_agent_gas() -> None:
    """Litres of agent *gas* is not the unit anyone consumes agent in (`PL-TG60`)."""

    assert ACCOUNTING_UNIT_CAPTION == "Litres of equivalent pure agent gas"


# --- the control-change panel ----------------------------------------------------


def test_the_list_states_what_was_changed_and_to_what() -> None:
    adjustments = group_adjustments(
        (_control_change(12.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),)
    )

    assert timeline_panel(adjustments, 0).entries == "12s · Fresh gas flow 4.0 L/min -> 2.0 L/min"


def test_the_list_reads_most_recent_first() -> None:
    """A fixed panel has to show the change the reader has just made."""

    adjustments = group_adjustments(
        (
            _control_change(10.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),
            _control_change(20.0, ControlInput.CARDIAC_OUTPUT, 5.0, 3.0, adjustment=2),
        )
    )
    lines = timeline_panel(adjustments, 0).entries.splitlines()

    assert lines[0].startswith("20s")
    assert lines[1].startswith("10s")


def test_a_run_with_no_changes_says_so_rather_than_showing_an_empty_panel() -> None:
    panel = timeline_panel((), 0)

    assert panel.entries == NO_CONTROL_CHANGES_TEXT
    assert panel.entries == "No settings changed yet in this run."
    assert panel.overflow == ""


def test_changes_the_panel_cannot_list_are_counted_rather_than_dropped() -> None:
    """A list that quietly stops asserts that nothing earlier happened."""

    adjustments = group_adjustments(
        tuple(
            _control_change(
                float(index),
                ControlInput.FRESH_GAS_FLOW,
                4.0,
                4.0 - index * 0.1,
                adjustment=index + 1,
            )
            for index in range(MAX_LISTED_ADJUSTMENTS + 3)
        )
    )
    panel = timeline_panel(adjustments, 0)

    assert len(panel.entries.splitlines()) == MAX_LISTED_ADJUSTMENTS == 12
    assert "3 earlier change(s) not listed" in panel.overflow


def test_changes_the_chart_cannot_mark_are_counted_rather_than_dropped() -> None:
    """Same rule for the plot: a chart that stops annotating is a claim."""

    timeline = tuple(
        _control_change(
            float(index), ControlInput.FRESH_GAS_FLOW, 4.0, 4.0 - index * 0.01, adjustment=index + 1
        )
        for index in range(MAX_CHART_CONTROL_MARKS + 2)
    )
    adjustments = group_adjustments(timeline)
    frame = _frame(
        _fake_controller(history=_run_history(600), control_timeline=timeline),
        adjustments=adjustments,
    )

    assert frame.runs[0].undrawn_control_marks == 2
    assert "2 not marked on the chart" in (
        timeline_panel(adjustments, frame.runs[0].undrawn_control_marks).overflow
    )


def test_the_two_overflow_counts_are_joined_on_one_line() -> None:
    adjustments = group_adjustments(
        tuple(
            _control_change(
                float(index), ControlInput.CARDIAC_OUTPUT, 5.0, 4.0, adjustment=index + 1
            )
            for index in range(MAX_LISTED_ADJUSTMENTS + 1)
        )
    )

    assert timeline_panel(adjustments, 4).overflow == (
        "1 earlier change(s) not listed; 4 not marked on the chart"
    )


def test_the_interface_says_a_control_mark_is_an_input_not_a_measurement() -> None:
    """The panel and the legend both say a mark is a setting, never a reading.

    That these strings reach the assembled interface is the widget's claim,
    tested with it; this holds the words themselves.
    """

    assert CONTROL_TIMELINE_CAPTION == (
        "What was changed during this run, most recent first. Settings only — not a measurement."
    )
    assert CONTROL_MARK_LEGEND_LABEL == "Control change (vertical, fine dash)"


# --- the chart captions ---------------------------------------------------------


def test_the_axis_caption_states_the_span_the_chart_is_showing() -> None:
    """`PL-012` required the caption to name the span actually drawn."""

    controller = _fake_controller(history=_run_history(12_000))
    caption = time_axis_caption(_frame(controller, time_base=time_base_for_span(7_200.0)))

    assert caption == "2 hours shown"
    assert "simulated seconds" not in caption


def test_the_caption_says_when_the_span_was_chosen_by_the_run_rather_than_the_reader() -> None:
    """Under "Fit run" the width is derived, and nothing else on screen says so."""

    controller = _fake_controller(history=_run_history(12_000))
    fitted = _frame(controller)

    assert "whole run so far" in time_axis_caption(fitted)
    assert f"{format_time_base(fitted.time_base.span_s)} shown" in time_axis_caption(fitted)
    assert time_axis_caption(fitted) == "whole run so far, 30 minutes shown"

    chosen = _frame(controller, time_base=time_base_for_span(43_200.0))

    assert "whole run so far" not in time_axis_caption(chosen)


def test_the_display_names_the_mac_the_readouts_were_divided_by() -> None:
    """The divisor is the one free parameter, so the display carries it, per agent."""

    assert mac_reference_caption(_frame(_fake_controller())) == format_mac_reference(
        "Sevoflurane", 2.0
    )
    assert mac_reference_caption(_frame(_fake_controller())) == "1 MAC sevoflurane = 2.0%"

    desflurane = _fake_controller(
        agent_id="desflurane",
        agent_display_name="Desflurane",
        max_delivered_concentration_percent=18.0,
    )

    assert mac_reference_caption(_frame(desflurane)) == format_mac_reference("Desflurane", 6.0)


@pytest.mark.parametrize("agent_id", AGENT_DATA_FILENAMES)
def test_the_band_states_the_fraction_and_the_divisor_it_was_drawn_from(agent_id: str) -> None:
    """Both of the band's free parameters are named, from the running agent's own file."""

    snapshot = SimulationController(agent_id=agent_id).snapshot()
    agent = load_agent_parameters(agent_id)

    assert mac_awake_caption(snapshot) == format_mac_awake_reference(
        agent.display_name,
        fraction_of_mac=agent.mac_awake.fraction_of_mac,
        standard_deviation_fraction_of_mac=agent.mac_awake.standard_deviation_fraction_of_mac,
        mac_percent=agent.mac_percent,
    )


def test_the_wash_in_trace_draws_nothing_before_agent_reaches_the_circuit() -> None:
    """0/0 is not a point, and an empty circuit is where every run starts."""

    state = wash_in_state(_snapshot(history=_run_history(1)), 0)

    assert "Not defined" in state
    assert "no agent has reached the circuit" in state
    assert state == "Not defined: no agent has reached the circuit yet."


def test_the_wash_in_trace_stops_when_alveolar_exceeds_inspired() -> None:
    """Elimination is not wash-in, and the plot says so rather than drawing it."""

    history = (*_run_history(20), _sample(2.0, 0.010, 0.030, 0.02, 0.02, 0.01, 0.01))
    state = wash_in_state(_snapshot(history=history), 0)

    assert "alveolar exceeds inspired" in state
    assert "elimination" in state
    assert state == (
        "Past equilibrium: alveolar exceeds inspired — the patient is returning agent, "
        "which is elimination and not wash-in."
    )


def test_the_wash_in_reading_is_the_value_the_trace_ends_at() -> None:
    """The sentence beside the plot and the plot cannot disagree."""

    controller = _fake_controller(history=_run_history(40))
    drawn_ratio = _frame(controller).runs[0].wash_in[-1].ratios[-1]
    state = wash_in_state(controller.snapshot(), 0)

    assert format_wash_in_ratio(drawn_ratio) in state
    assert state == f"Now: F_A/F_I = {format_wash_in_ratio(drawn_ratio)}"


def test_the_wash_in_state_counts_the_stretches_the_plot_could_not_draw() -> None:
    """A pool that overflowed is displayed rather than silent."""

    state = wash_in_state(_snapshot(history=_run_history(40)), 3)

    assert state.endswith(" (3 earlier stretch(es) not drawn)")
    assert not wash_in_state(_snapshot(history=_run_history(40)), 0).endswith("not drawn)")


def test_a_trace_above_the_fixed_axis_is_reported_rather_than_left_to_look_flat() -> None:
    """The failure mode PL-CC23's fixed ceiling introduces, and its guard.

    A clipped trace draws as a horizontal line at the top of the plot, and a
    horizontal line reads as a plateau, so the plot says so rather than
    relying on the reader noticing.
    """

    # 8% circuit is 4 MAC of sevoflurane, against a 6% (3 MAC) ceiling.
    # Alveolar at 5% stays inside it, which is what makes this a test of
    # *which* compartments are named rather than only that something was.
    history = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1.0, 0.08, 0.05, 0.01, 0.01, 0.0, 0.0),
    )
    text = off_scale_notice(_frame(_fake_controller(history=history)), 0)

    assert text is not None
    assert "Circuit" in text
    assert "Alveolar" not in text
    # The notice has to say where the unclipped number is, or it reports a
    # problem and leaves the reader without the value.
    assert "readouts above" in text
    assert "3.00 ×MAC" in text
    assert text == (
        "Above the top of the plot: Circuit. The axis stops at 3.00 ×MAC and these "
        "traces are cut off there — their values are in the readouts above, which are "
        "not clipped."
    )


def test_the_off_scale_notice_stays_silent_for_a_run_inside_the_axis() -> None:
    """An advisory that fires on an ordinary run is one nobody reads."""

    history = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1.0, 0.02, 0.018, 0.015, 0.014, 0.01, 0.005),
    )

    assert off_scale_notice(_frame(_fake_controller(history=history)), 0) is None


def test_a_trace_exactly_at_the_ceiling_is_not_reported_off_scale() -> None:
    """Isoflurane is where a naive comparison would report noise as a defect.

    Its ceiling is 3 x 1.2%, which in binary floating point is
    3.5999999999999996 rather than 3.6, so a trace sitting exactly at 3 MAC
    is arithmetically *above* the axis by 4e-16.
    """

    at_ceiling = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id="isoflurane"),
        _sample(1.0, 0.036, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id="isoflurane"),
    )
    controller = _fake_controller(
        agent_id="isoflurane", agent_display_name="Isoflurane", history=at_ceiling
    )

    assert off_scale_notice(_frame(controller), 0) is None

    # ...and the tolerance is not so wide that it swallows a real excursion:
    # 3.62% clears the ceiling by more than the readouts can resolve.
    above_ceiling = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id="isoflurane"),
        _sample(1.0, 0.0362, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id="isoflurane"),
    )
    controller = _fake_controller(
        agent_id="isoflurane", agent_display_name="Isoflurane", history=above_ceiling
    )

    assert off_scale_notice(_frame(controller), 0) is not None


def test_a_hidden_trace_is_not_named_as_off_scale() -> None:
    """The notice must not point at a trace the reader has taken off the chart."""

    history = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1.0, 0.08, 0.01, 0.01, 0.01, 0.0, 0.0),
    )
    controller = _fake_controller(history=history)
    without_circuit = tuple(
        quantity for quantity in COMPARTMENT_QUANTITIES if quantity is not RecordedQuantity.CIRCUIT
    )

    assert off_scale_notice(_frame(controller), 0) is not None
    assert off_scale_notice(_frame(controller, shown=without_circuit), 0) is None


def test_the_chart_says_so_when_no_compartment_is_drawn() -> None:
    """A blank plot reads as a display that has failed, not as an empty view."""

    controller = _fake_controller(history=_run_history(600))

    assert no_traces_shown(_frame(controller)) is False
    assert no_traces_shown(_frame(controller, shown=())) is True
    assert no_traces_shown(_frame(controller, shown=(RecordedQuantity.ALVEOLAR,))) is False


# --- the new-case question ------------------------------------------------------


def test_the_confirmation_quotes_the_time_and_the_changes_the_panel_shows() -> None:
    """What is about to be lost is stated in the run's own displayed terms."""

    snapshot = _paused_run_with_history().snapshot()
    adjustment_count = len(group_adjustments(snapshot.control_timeline))
    question = new_case_question(snapshot, "Desflurane", adjustment_count)

    assert question.body[1] == format_case_discard_warning(
        "Sevoflurane", snapshot.elapsed_s, adjustment_count
    )
    assert format_elapsed(snapshot.elapsed_s) in question.body[1]


def test_the_confirmation_names_both_agents_and_what_survives_the_switch() -> None:
    """A reader deciding this needs the agent they are leaving and the one they would start."""

    snapshot = _paused_run_with_history().snapshot()
    question = new_case_question(snapshot, "Desflurane", 1)

    assert question.title == "Start a new desflurane case?"
    assert question.body[0] == NEW_CASE_IS_NOT_A_VIEW_TEXT
    assert "sevoflurane" in question.body[1]
    assert question.body[2] == NEW_CASE_CARRYOVER_TEMPLATE.format(agent="desflurane")
    assert len(question.body) == 3


def test_the_carry_over_sentence_names_only_settings_the_reader_can_set() -> None:
    """`PL-0Q1T`: a list of what a discard costs, in things the reader chose.

    The circuit volume does carry over, so naming it was true - and
    lopsided: `PL-GYH2` retired the only setter that could have changed it.
    Asserted as the property rather than against the string.
    """

    sentence = NEW_CASE_CARRYOVER_TEMPLATE.lower()

    assert "circuit volume" not in sentence
    for setting in ("fresh gas flow", "alveolar ventilation", "cardiac output"):
        assert setting in sentence


def test_the_confirmations_trailing_action_is_the_one_that_keeps_the_case() -> None:
    """The press a reader makes without reading must not destroy the run.

    The labels name their outcomes; which button is filled, last and the
    default is the dialog's and is tested with it.
    """

    question = new_case_question(_paused_run_with_history().snapshot(), "Desflurane", 1)

    assert question.discard_label == "Discard and start desflurane"
    assert question.keep_label == "Keep the sevoflurane case"


# --- layout and the interpretation line -----------------------------------------


def test_readout_columns_are_the_widest_rung_whose_panels_fit() -> None:
    """Seven across where seven panels fit, else four, two, one (`PL-8M05`).

    The rungs are fixed and the widths are not: a panel 100 px wide with
    10 px between neighbours needs 760 px for seven, 430 for four and 210
    for two, and the count steps down one pixel below each. One column is
    the floor, even for a row narrower than a single panel.
    """

    equal = (100.0,) * 7

    assert READOUT_ROW_LADDER == (7, 4, 2, 1)
    assert [
        readout_columns(width, equal, 10.0)
        for width in (0.0, 99.0, 100.0, 209.0, 210.0, 429.0, 430.0, 759.0, 760.0, 1_700.0)
    ] == [1, 1, 1, 1, 2, 2, 4, 4, 7, 7]
    assert readout_columns(700.0, equal, 0.0) == 7
    assert readout_columns(699.0, equal, 0.0) == 4
    assert readout_columns(-1.0, equal, 10.0) == 1


def test_each_column_is_held_to_the_widest_panel_it_holds_and_not_to_the_clocks() -> None:
    """The clock's wide reservation costs its own column and no other (`PL-3355`).

    A clock 195 px wide beside six compartments of 135 px, with 6 px between
    columns: seven across needs 195 + 6 x 135 + 6 x 6 = 1041 px, not
    7 x 195 + 36 = 1401; four across puts the clock and the fifth panel in
    one column, so the row needs 195 + 3 x 135 + 18 = 618 px; two across
    needs 195 + 135 + 6 = 336; one needs the clock's 195.
    """

    widths = (195.0, 135.0, 135.0, 135.0, 135.0, 135.0, 135.0)

    assert readout_row_width(7, widths, 6.0) == 1041.0
    assert readout_row_width(4, widths, 6.0) == 618.0
    assert readout_row_width(2, widths, 6.0) == 336.0
    assert readout_row_width(1, widths, 6.0) == 195.0
    assert [readout_columns(width, widths, 6.0) for width in (1041.0, 1040.0, 618.0, 617.0)] == [
        7,
        4,
        4,
        2,
    ]

    with pytest.raises(ValueError, match="at least one column"):
        readout_row_width(0, widths, 6.0)


def test_the_reservations_give_the_clock_its_elapsed_form_and_the_compartments_theirs() -> None:
    """One reservation per panel, the clock's the widest elapsed form (`PL-3355`)."""

    assert len(READOUT_RESERVATIONS) == len(READOUT_PANELS)
    assert READOUT_RESERVATIONS[0] == (WIDEST_READOUT_VALUE, WIDEST_READOUT_SECONDARY)
    assert set(READOUT_RESERVATIONS[1:]) == {
        (WIDEST_COMPARTMENT_VALUE, WIDEST_COMPARTMENT_SECONDARY)
    }
    assert WIDEST_COMPARTMENT_VALUE == format_percent(Fraction(1.0))
    assert WIDEST_COMPARTMENT_SECONDARY.endswith(MAC_UNIT_SUFFIX)


def test_the_interface_says_the_readouts_are_model_outputs_not_measurements() -> None:
    """`PL-2K1R`: the interpretation line, distinct from the use disclaimer.

    Short, beside the values it qualifies, and saying what the value *is*
    rather than what the reader must not do. Its placement on the readout
    section's heading row is the widget's claim.
    """

    assert INTERPRETATION_DISCLAIMER_TEXT == "Model outputs — not measurements."


def test_the_educational_disclaimer_says_what_the_tool_is_not() -> None:
    """`PL-GMM7`: the one string that carries the project's regulatory posture, verbatim.

    Coverage cannot hold it - the line executes whenever the dashboard is
    built - so the words are pinned here, and
    `test_the_dashboard_carries_the_educational_disclaimer` holds that the
    dashboard places them.
    """

    assert USE_DISCLAIMER_TEXT == (
        "Educational simulation only. This idealized model is not a clinical prediction, "
        "monitoring, or dosing tool."
    )


# ----------------------------------------------------------- bookmark panel
#
# What the two listings claim, and the one thing they must not claim: that a
# mark has been *reached*. Detection is `PL-CTD7` and is not built, so a row
# implying a crossing would put an unbuilt guarantee on screen (`PL-LPLD`).


def _marks() -> BookmarkSet:
    """One mark of each kind, both named."""

    return (
        BookmarkSet()
        .with_time_bookmark(TimeBookmark(600.0, "intubation"))
        .with_mac_target(MacTarget(RecordedQuantity.VESSEL_RICH, MacMultiple(0.8), "wash-in"))
    )


def test_an_unmarked_run_lists_each_collection_as_empty_in_its_own_words() -> None:
    panel = bookmark_panel(BookmarkSet(), _one_run(_unreached(BookmarkSet())))

    assert panel.times.rows == ()
    assert panel.targets.rows == ()
    assert panel.times.empty_text != panel.targets.empty_text


def test_the_two_collections_carry_their_own_headings() -> None:
    panel = bookmark_panel(BookmarkSet(), _one_run(_unreached(BookmarkSet())))

    assert panel.times.heading == TIME_BOOKMARK_HEADING
    assert panel.targets.heading == MAC_TARGET_HEADING


def test_a_marked_instant_is_listed_at_the_clock_the_run_states() -> None:
    panel = bookmark_panel(_marks(), _one_run(_unreached(_marks())))

    assert panel.times.rows == (f"{format_elapsed(600.0)} – intubation",)


def test_an_unnamed_instant_is_listed_under_its_own_time() -> None:
    panel = _panel(BookmarkSet().with_time_bookmark(TimeBookmark(600.0)))

    assert panel.times.rows == (format_elapsed(600.0),)


def test_a_target_names_its_compartment_and_its_height() -> None:
    row = bookmark_panel(_marks(), _one_run(_unreached(_marks()))).targets.rows[0]

    assert row.startswith("Vessel-rich 0.80 ×MAC")


def test_a_target_is_named_by_the_table_that_names_its_trace() -> None:
    # One table rather than a second list of compartment words, so a row and
    # the curve it is read against cannot come to disagree.
    for quantity in COMPARTMENT_QUANTITIES:
        target = MacTarget(quantity, MacMultiple(0.8))

        assert format_mac_target(target, MarkStanding.STILL_RUNNING).startswith(
            trace_style(quantity).label
        )


def test_a_target_is_rendered_by_the_renderer_the_readouts_use() -> None:
    # A target listed at `0.8 x MAC` beside a readout showing `0.80 x MAC`
    # would read as two quantities where there is one, so both go through
    # `render_mac_multiple` rather than through two spellings of one rule.
    height = MacMultiple(0.8)
    target = MacTarget(RecordedQuantity.ALVEOLAR, height)

    assert render_mac_multiple(height) == "0.80 ×MAC"
    assert render_mac_multiple(height) in format_mac_target(target, MarkStanding.STILL_RUNNING)


def test_a_target_row_is_the_compartment_then_the_height() -> None:
    target = MacTarget(RecordedQuantity.FAT, MacMultiple(0.5))

    assert format_mac_target(target, MarkStanding.STILL_RUNNING) == "Fat 0.50 \u00d7MAC"


def test_two_heights_on_one_compartment_are_told_apart_on_the_row() -> None:
    lower = MacTarget(RecordedQuantity.FAT, MacMultiple(0.5))
    higher = MacTarget(RecordedQuantity.FAT, MacMultiple(0.8))

    assert format_mac_target(lower, MarkStanding.STILL_RUNNING) != format_mac_target(
        higher, MarkStanding.STILL_RUNNING
    )


def test_marks_are_listed_oldest_first() -> None:
    # The opposite of the control-change list, deliberately: that is a record
    # a reader chases the newest entry of, and this is a standing set they add
    # to and scan, so a row that moves is one they have to find again.
    marks = (
        BookmarkSet()
        .with_time_bookmark(TimeBookmark(120.0, "first"))
        .with_time_bookmark(TimeBookmark(600.0, "second"))
    )

    rows = bookmark_panel(marks, _one_run(_unreached(marks))).times.rows

    assert rows[0].endswith("first")
    assert rows[1].endswith("second")


def test_a_mark_the_run_can_still_reach_adds_no_words_to_its_row() -> None:
    # Conditional text rather than standing text
    # (`.claude/rules/ui-reader.md`): a standing repeated on every row would
    # be chrome, and the rows whose state a reader has to know are the ones
    # where something has happened.
    panel = bookmark_panel(_marks(), _one_run(_unreached(_marks())))
    everything = " ".join((*panel.times.rows, *panel.targets.rows)).lower()

    for claim in ("reached", "crossed", "halted", "stopped", MARK_STILL_RUNNING_TEXT):
        assert claim not in everything


def test_a_mark_the_run_halted_on_says_so_on_its_row() -> None:
    target = MacTarget(RecordedQuantity.FAT, MacMultiple(0.5))

    assert "reached" in format_mac_target(target, MarkStanding.REACHED)


def test_a_mark_on_a_failed_run_says_the_run_stopped_rather_than_saying_nothing() -> None:
    """`PL-N3N5`, at the row a learner reads it off.

    A failed run's marks drew as silence - `STILL_RUNNING` renders as nothing
    at all on an unattributed row - so the one run on screen said the mark was
    still ahead of it by saying nothing about it, beside its own panel reading
    "Stopped - simulation error". The word has to name the failure rather than
    the cap: they stop a run for opposite reasons, and only one of them is a
    statement about what the model supports.
    """

    bookmark = TimeBookmark(600.0, "check")
    target = MacTarget(RecordedQuantity.FAT, MacMultiple(0.5))
    said = MARK_STANDING_TEXT[MarkStanding.NOT_REACHED_BEFORE_FAILURE]

    assert said
    assert said in format_time_bookmark(bookmark, MarkStanding.NOT_REACHED_BEFORE_FAILURE)
    assert said in format_mac_target(target, MarkStanding.NOT_REACHED_BEFORE_FAILURE)
    assert said != MARK_STANDING_TEXT[MarkStanding.NOT_REACHED_WITHIN_CAP]


def test_every_standing_a_run_can_report_has_a_word_to_draw_it_with() -> None:
    """A member added without an entry is a `KeyError` at the moment of drawing.

    `_with_standing` indexes the table, so the failure lands in the panel of a
    running app rather than in anything a reviewer reads - which is why the
    enum is walked here rather than the table.
    """

    for standing in MarkStanding:
        assert standing in MARK_STANDING_TEXT


def test_a_mark_the_clock_has_gone_past_is_worded_apart_from_one_the_run_halted_on() -> None:
    """`PL-3K9B`: two claims, so two words.

    "Passed" is where the clock stands, re-read every time the row is drawn.
    "Reached" is what the run did, and a clock taken backwards - a rewind, a
    truncation at a mark - would revoke it while the mark went on being
    perfectly reachable.
    """

    bookmark = TimeBookmark(600.0)
    target = MacTarget(RecordedQuantity.FAT, MacMultiple(0.5))

    passed = format_time_bookmark(bookmark, MarkStanding.PASSED)

    assert "passed" in passed
    assert "reached" not in passed
    assert passed != format_time_bookmark(bookmark, MarkStanding.REACHED)
    assert "reached" in format_mac_target(target, MarkStanding.REACHED)


def test_the_two_unreachable_outcomes_are_worded_apart() -> None:
    # "Not reached" alone would be true of both, and would tell a learner that
    # a bookmark standing before this branch's fork might arrive if they kept
    # running. `CLAUDE.md`'s safety-critical standard is what rules that out:
    # the model can decide it outright, so a row must not imply otherwise.
    bookmark = TimeBookmark(600.0)
    at_the_cap = format_time_bookmark(bookmark, MarkStanding.NOT_REACHED_WITHIN_CAP)
    inherited = format_time_bookmark(bookmark, MarkStanding.BEFORE_THIS_BRANCH)

    assert at_the_cap != inherited
    assert "run length" in at_the_cap
    assert "branch" in inherited


def test_the_panel_reads_the_marks_the_snapshot_carries() -> None:
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(600.0, "intubation"))

    panel = bookmark_panel(
        controller.snapshot().bookmarks, _one_run(controller.snapshot().bookmark_standings)
    )

    assert panel.times.rows == (f"{format_elapsed(600.0)} – intubation",)


# ---------------------------------- one mark, two runs, and whose answer it is


def test_two_runs_that_answer_a_mark_alike_state_it_once_and_name_no_run() -> None:
    """`PL-LHBY`, `PL-4KZD`: an unattributed clause is a claim about the case.

    So it may be drawn only where it holds of every run on screen. That is
    what makes a lone run's row the degenerate case of the compared one
    rather than a second path through the panel - a lone run agrees with
    itself - and it is why a quiet row does not grow a run name per run it is
    quiet on.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(30.0, "check"))
    passed = _standings(marks, elapsed_s=120.0)

    (row,) = bookmark_panel(marks, _two_runs(passed, passed)).times.rows

    assert MARK_STANDING_TEXT[MarkStanding.PASSED] in row
    assert run_label(0) not in row
    assert run_label(1) not in row


def test_two_runs_still_running_for_a_mark_add_no_words_to_its_row() -> None:
    # The same rule at the standing that draws as silence: a comparison whose
    # runs have both yet to reach a mark has nothing to report about it, and
    # a run name on every quiet row would be the standing chrome
    # `.claude/rules/ui-reader.md` rules out.
    marks = _marks()
    unreached = _unreached(marks)

    panel = bookmark_panel(marks, _two_runs(unreached, unreached))
    everything = " ".join((*panel.times.rows, *panel.targets.rows))

    assert run_label(0) not in everything
    assert MARK_STILL_RUNNING_TEXT not in everything


def test_a_branch_that_halted_on_a_target_the_trunk_is_still_running_for_says_so() -> None:
    """`PL-LHBY`, the silent negative, reproduced offscreen against `4c282700`.

    A MAC target the branch halts on while the trunk is still running for it.
    Drawn from the reference run the row said nothing at all, so a branch
    stopping at a mark the learner set was indistinguishable on screen from a
    Pause - the one indication that a run stopped where it was asked to
    existed for a lone run and vanished as soon as a second was drawn.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5))
    marks = BookmarkSet().with_mac_target(target)
    trunk = _standings(marks, elapsed_s=60.0)
    branch = _standings(
        marks, opened_at_s=60.0, elapsed_s=174.7, reached_crossings=frozenset({target.crossing_key})
    )

    (row,) = bookmark_panel(marks, _two_runs(trunk, branch)).targets.rows

    # Pinned whole rather than by `in`, which holds the shape of the row and
    # not merely its contents: the mark stated once however many runs are
    # shown, the runs in drawing order, and each clause naming its run before
    # its answer. Every one of those is a way of attributing an answer to the
    # wrong run that still reads plausibly on the screen.
    assert row == (
        f"Alveolar 0.50 ×MAC"
        f"{MARK_STANDING_JOINER}{run_label(0)} {MARK_STILL_RUNNING_TEXT}"
        f"{MARK_STANDING_JOINER}{run_label(1)}"
        f" {MARK_STANDING_COMPARED_TEXT[MarkStanding.REACHED]}"
    )


def test_a_bookmark_the_branch_opened_after_is_not_drawn_as_the_trunk_left_it() -> None:
    """`PL-LHBY`, the false positive, and the worse half of the pair.

    An inherited instant the branch provably cannot reach read as the trunk's
    `passed`, so the screen asserted of the displayed branch something the
    model can decide is false - which `CLAUDE.md`'s safety-critical standard
    treats as a failure of the displayed value, the correct standing under
    the wrong run being the wrong standing.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(30.0, "check"))
    trunk = _standings(marks, elapsed_s=60.0)
    branch = _standings(marks, opened_at_s=60.0, elapsed_s=60.0)

    (row,) = bookmark_panel(marks, _two_runs(trunk, branch)).times.rows

    assert f"{run_label(0)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.PASSED]}" in row
    assert row.endswith(
        f"{run_label(1)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.BEFORE_THIS_BRANCH]}"
    )


def test_the_inherited_standing_can_reach_a_drawn_row() -> None:
    """`PL-LHBY`: `BEFORE_THIS_BRANCH` had no screen it could appear on.

    It exists so a learner is not told something false about a mark a branch
    carries but cannot reach, and the panel read the reference run - which is
    the trunk, opened at zero, and no instant stands before that. The
    vocabulary was unreachable by construction rather than by accident, so
    this asserts the word itself rather than only the row that carries it.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(30.0))
    trunk = _standings(marks, elapsed_s=60.0)
    branch = _standings(marks, opened_at_s=60.0, elapsed_s=60.0)

    (row,) = bookmark_panel(marks, _two_runs(trunk, branch)).times.rows

    assert MARK_STANDING_TEXT[MarkStanding.BEFORE_THIS_BRANCH] in row


def test_every_standing_a_run_can_report_has_a_word_on_an_attributed_row() -> None:
    """The compared table's own walk, and it asks for more than the plain one.

    `MARK_STANDING_TEXT` may draw a standing as silence, because an
    unattributed row states one answer and silence is unambiguous there.
    Beside a named run it is not: a clause that rendered as a bare run name
    would leave the reader to decide whether that run had no answer or had
    not been asked. So every member owes a word here, which is what a new
    member added without one would fail on.
    """

    for standing in MarkStanding:
        assert MARK_STANDING_COMPARED_TEXT[standing]


def test_no_two_standings_share_a_word_on_an_attributed_row() -> None:
    """`PL-3K9B`'s wording guarantee, held where a learner actually compares.

    "Passed" and "reached" are two words because they are two claims, and the
    two unreachable outcomes are worded apart so that neither reads as the
    other. Both were pinned on `MARK_STANDING_TEXT` alone - the form a lone
    run draws - and the row where the distinction earns its keep is the
    two-run row, which draws from this table instead.
    """

    said = tuple(MARK_STANDING_COMPARED_TEXT[standing] for standing in MarkStanding)

    assert len(set(said)) == len(said)


def test_the_attributed_standing_words_describe_the_mark_and_not_the_transport() -> None:
    """`MARK_ATTRIBUTION_TEMPLATE` makes the run the grammatical subject.

    So a standing borrowing one of the transport's own words would assert
    what the clock is doing rather than where the mark stands - and this
    interface says what the clock is doing a few lines away, in
    `STATUS_RUNNING_TEXT` and its neighbours, on that run's own panel. The
    entry this catches is `STILL_RUNNING`, whose attributed form read "still
    running" and so contradicted the panel beside it on every paused run,
    while claiming more than `MarkStanding.STILL_RUNNING` is licensed to: it
    says the run *can still reach* the mark and has not yet, which is about
    the mark rather than about the clock.
    """

    transport = (STATUS_RUNNING_TEXT, STATUS_PAUSED_TEXT, STATUS_FAILED_TEXT)

    for standing in MarkStanding:
        said = MARK_STANDING_COMPARED_TEXT[standing].lower()

        for word in transport:
            assert word.lower() not in said


def test_a_panel_drawn_for_no_run_is_refused() -> None:
    # An obvious failure rather than a plausible-looking panel: the case's
    # marks listed under standings nobody had answered would be rows a reader
    # could read a standing off.
    with pytest.raises(ValueError, match="at least one run"):
        bookmark_panel(_marks(), ())


# ------------------------------------- the branch control and its three locks


def test_fork_offer_labels_every_keyframe_the_trunk_holds() -> None:
    """`BranchedCase.fork_points_s` in, `format_elapsed` out, one label per instant.

    Induction is offered rather than filtered out: a fork at zero is a
    second management of the whole case, and dropping it would leave a case
    that has recorded nothing with an empty selector beside a live button.
    """

    offer = fork_offer((0.0, 60.0, 185.0), comparing=False)

    assert offer.points_s == (0.0, 60.0, 185.0)
    assert offer.labels == tuple(format_elapsed(instant_s) for instant_s in offer.points_s)
    assert offer.locked is False
    assert offer.lock_reason == ""
    assert offer.refusal is None


def test_fork_offer_is_refused_while_a_comparison_is_shown_and_says_the_way_out() -> None:
    """The display is capped at two runs and there is no run selector yet.

    A refused control that does not say how to un-refuse itself is a dead
    end rather than a mode, so the reason names Reset.
    """

    offer = fork_offer((0.0, 60.0), comparing=True)

    assert offer.locked is True
    assert offer.lock_reason == COMPARING_FORK_LOCK_TEXT
    assert "Reset" in COMPARING_FORK_LOCK_TEXT


def test_a_standing_refusal_shows_only_while_the_control_is_offered() -> None:
    """A refusal describes a press of a control that is no longer on screen.

    The lock and the refusal are two lines of two severities rather than one
    line of two meanings, so the question is not which wins but whether a
    message about a vanished control should still be standing. It should
    not.
    """

    refusal = "Setting refused: no keyframe at 30.0 s"

    assert fork_offer((0.0,), comparing=False, refusal=refusal).refusal == refusal
    assert fork_offer((0.0,), comparing=True, refusal=refusal).refusal is None


def test_the_agent_selector_is_shown_only_on_a_paused_lone_trunk() -> None:
    """Three reasons replace it with the chip, and a paused single run is none of them."""

    offered = transport(_snapshot(is_running=False))

    assert offered.selector_locked is False
    assert offered.selector_lock_reason == ""


@pytest.mark.parametrize(
    ("is_running", "is_branch", "comparing", "expected"),
    [
        (True, False, False, RUNNING_AGENT_LOCK_TEXT),
        (False, False, True, COMPARING_AGENT_LOCK_TEXT),
        (False, True, False, BRANCH_AGENT_LOCK_TEXT),
        (True, False, True, COMPARING_AGENT_LOCK_TEXT),
        (True, True, True, BRANCH_AGENT_LOCK_TEXT),
        (True, True, False, BRANCH_AGENT_LOCK_TEXT),
    ],
)
def test_the_chip_names_the_lock_that_lasts_longest(
    is_running: bool, is_branch: bool, comparing: bool, expected: str
) -> None:
    """A reader acts on the reason, so it has to be one the named gesture can lift.

    A branch's selector never returns - `set_agent` refuses a branch - a
    comparison's returns on Reset, and a running run's returns on Pause.
    Naming the shortest lock that happens to hold would send a reader to
    Pause for something Pause cannot lift.
    """

    locked = transport(_snapshot(is_running=is_running), is_branch=is_branch, comparing=comparing)

    assert locked.selector_locked is True
    assert locked.selector_lock_reason == expected
