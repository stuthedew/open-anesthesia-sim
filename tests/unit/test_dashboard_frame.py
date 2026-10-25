"""Tests of what the dashboard shows, run without a GUI toolkit.

`app/dashboard_frame.py` holds the dashboard's presentation-correctness
claims. They say which word states the run's state, which banner takes
priority over which, what each readout and setting says, and what the
captions and the new-case question say. Every test here runs with no display
and no widget, which is the reason that module exists. The tests are the
Flet suite's tests (`tests/unit/test_simulation_view.py`) rewritten against
the frame functions. Where a claim survived the port, its test keeps the same
name. The verify lines and `docs/MODEL.md` citations that name those tests
therefore still point at a test that checks the same thing (`PL-25KS`).

Snapshots come from one of two places. One is a real `SimulationController`
stepped at the shipped step. The other is `_snapshot`, a fixture that takes
MAC and MAC-awake from the named agent's data file. A test therefore cannot
pair one agent's concentrations with another agent's divisor. Some claims
need the frame that the chart drew: the off-scale notice, the count of
undrawn marks, and the time-axis caption. For those, `_FakeController`
returns exactly the samples the fixture wrote when asked for its
`drawn_window`. The test then checks how the frame treats those samples, not
where the sampler placed its columns.
"""

import json
import math
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from importlib.resources import files
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
from anesthesia_sim.app.controller import (
    BranchedCase,
    HereForkPoint,
    MarkForkPoint,
    ResumePoint,
    RunStatus,
    SimulationController,
    SimulationSnapshot,
)
from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_HEADING,
    ACCOUNTING_UNIT_CAPTION,
    BRANCH_AGENT_LOCK_TEXT,
    COMPARING_AGENT_LOCK_TEXT,
    CONTROL_MARK_LEGEND_LABEL,
    CONTROL_TIMELINE_CAPTION,
    CONTROL_TIMELINE_HEADING,
    EMPTY_METRIC_QUALIFIER,
    EMPTY_METRIC_SECONDARY_VALUE,
    HALT_FORK_LABEL_TEMPLATE,
    HERE_FORK_LABEL_TEMPLATE,
    INTERPRETATION_DISCLAIMER_TEXT,
    MAC_TARGET_HEADING,
    MARK_FORK_LABEL_TEMPLATE,
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
    REFUSED_RESET_AFTER_FAILURE_EXIT_TEMPLATE,
    REFUSED_RESET_EXIT_TEMPLATE,
    REFUSED_RESET_WAY_OUT_TEXT,
    RENDER_INTERVAL_S,
    RESET_EXIT_TEXT,
    RESET_LABEL,
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
    BranchAtStake,
    ComparedRuns,
    Emphasis,
    ForkOffer,
    ForkPoint,
    HaltDisposition,
    RunMarks,
    accounting,
    bookmark_panel,
    branch_at_stake,
    compared_panel_heading,
    compared_run_line,
    compared_run_notice,
    comparing_fork_lock_text,
    delivered_line,
    fork_offer,
    halt_disposition,
    halt_notice,
    mac_awake_caption,
    mac_reference_caption,
    new_case_question,
    no_traces_shown,
    notice,
    off_scale_lines,
    off_scale_notice,
    offered_range,
    readout_columns,
    readout_row_width,
    readouts,
    refused_reset_exit,
    refused_setting_notice,
    run_label,
    run_statement,
    setting_readouts,
    slider_position,
    slider_value,
    status_word,
    substance_heading,
    time_axis_caption,
    timeline_panel,
    transport,
    trunk_reset_question,
    unmarked_changes_lines,
    wash_in_state,
    wash_in_state_lines,
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
    format_subtitle,
    format_supported_run_length,
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
from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.concentration import Fraction, MacMultiple, MacPercent, Percent
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
    parse_breathing_circuit_parameters,
)
from anesthesia_sim.core.run_definition import DisplayState
from anesthesia_sim.core.simulation_step import MAXIMUM_SIMULATION_STEP_S, MINIMUM_SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import (
    MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    MAXIMUM_ELAPSED_SIMULATION_TIME_S,
    MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
    MINIMUM_CARDIAC_OUTPUT_L_MIN,
    MINIMUM_FRESH_GAS_FLOW_L_MIN,
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
)
from anesthesia_sim.layout.run_identity import RunId, SessionToken

# The identities that a dashboard gives to the first runs it places, in
# order. They render as "Run 1", "Run 2" and "Run 3". A run is named from its
# identity, not from where it is drawn (`PL-7Z84`).
TEST_SESSION = SessionToken("0" * 32)
RUN_IDS = tuple(RunId(TEST_SESSION, number) for number in (1, 2, 3))
FIRST_RUN, SECOND_RUN = RUN_IDS[:2]
COMPARED = ComparedRuns(run_label(FIRST_RUN), run_label(SECOND_RUN))

#: The agent every fixture here runs unless it says otherwise. It is named
#: once because the snapshot and the recorded run have to agree on it.
_DEFAULT_AGENT = "sevoflurane"

#: The plot width every frame here is assembled for. It is wide enough that
#: no fixture is thinned, so every drawn point is a sample the fixture wrote.
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
    """Return one recorded sample as a state vector, in the order `governing_equations` uses."""

    values = sample.substances[substance_id]
    state = [0.0] * STATE_SIZE

    for quantity, position in COMPARTMENT_STATE_INDEX.items():
        state[position] = values[quantity]

    state[UNIT_STATE] = 1.0

    return tuple(state)


def _panel(marks: BookmarkSet) -> BookmarkPanel:
    """Return the panel for that set of marks on one run, with every mark still reachable."""

    return bookmark_panel(marks, _one_run(_unreached(marks)))


def _one_run(standings: BookmarkStandings) -> tuple[RunMarks, ...]:
    """Return a lone run's marks, which a panel test wants unless it compares runs.

    A lone run is given no name. `SimulationView._rename_runs` states that
    rule, and `run_label` supplies the name when a run has one. The label here
    is therefore the one the dashboard would pass, and no row draws it.
    """

    return (RunMarks(run_label(FIRST_RUN), standings),)


def _two_runs(trunk: BookmarkStandings, branch: BookmarkStandings) -> tuple[RunMarks, ...]:
    """A trunk and a branch drawn together, in the order the dashboard adds them.

    `SimulationView.add_run` appends, and Reset truncates back to the first
    run, so the trunk is always run 1 and a branch is always run 2.
    """

    return (RunMarks(run_label(FIRST_RUN), trunk), RunMarks(run_label(SECOND_RUN), branch))


def _unreached(marks: BookmarkSet) -> BookmarkStandings:
    """Standings for a run that has reached none of its marks and can still reach all.

    A panel test wants these standings by default. The rows show each mark's
    own value, and this standing adds no words to them.
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
    """Return one run's standings on that set, by default for a run that has just opened."""

    return marks.standings(
        reached_instants_s=reached_instants_s,
        reached_crossings=reached_crossings,
        opened_at_s=opened_at_s,
        elapsed_s=elapsed_s,
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
    accepted_fresh_gas_flow_range_l_min: tuple[float, float] = (
        MINIMUM_FRESH_GAS_FLOW_L_MIN,
        MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    ),
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

    Both come from the data file rather than from a literal. A test that
    names an agent therefore cannot pair that agent's concentrations with
    another agent's MAC. That pairing is the presentation failure the MAC
    readouts must prevent. The six compartment fractions are read from the
    last sample of `history`, under the agent that the snapshot names. The
    run is a trunk that began at induction, as `_unreached` assumes of its
    marks.
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
        elapsed_s=CaseInstant(latest.elapsed_s),
        began_at_s=CaseInstant(0.0),
        agent_id=agent_id,
        agent_display_name=agent_display_name,
        max_delivered_concentration_percent=Percent(max_delivered_concentration_percent),
        agent_mac_percent=MacPercent(agent_mac_percent),
        agent_mac_awake=agent_mac_awake,
        circuit_volume_l=6.0,
        fresh_gas_flow_l_min=FreshGasFlow(3.0),
        accepted_fresh_gas_flow_range_l_min=accepted_fresh_gas_flow_range_l_min,
        delivered_concentration_percent=Percent(2.5),
        alveolar_ventilation_l_min=AlveolarVentilation(5.5),
        cardiac_output_l_min=CardiacOutput(6.5),
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

    The real controller evaluates its run definition at instants it chooses.
    A fake has no definition. Inventing one would make every frame test here
    check where the sampler placed its columns, rather than the behaviour
    under test. The fake provides only `snapshot()`, `drawn_window()` and
    `opened_from`, because those are the three things that
    `assemble_chart_frame` asks a run for.
    """

    def __init__(
        self,
        snapshot: SimulationSnapshot,
        history: tuple[_Sample, ...],
        opened_from: ResumePoint | None = None,
    ) -> None:
        self.snapshot_value = snapshot
        self.history_value = history
        #: Where this run forked, or `None` for a run that is not a branch.
        #: A frame marks the fork, so the fake must be able to act as a branch.
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
    """Build a fake whose snapshot and history describe the same run."""

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
    """Return the frame one tick would draw for one run, under "Fit run" unless told otherwise."""

    return assemble_chart_frame(
        (RunInput(run_label(FIRST_RUN), controller, controller.snapshot(), adjustments),),
        time_base,
        shown,
        plot_width_px=_PLOT_WIDTH_PX,
    )


def _compared_frame(*controllers: Any) -> ChartFrame:
    """Return the frame one tick would draw for several runs, named as the dashboard names them."""

    return assemble_chart_frame(
        tuple(
            RunInput(run_label(RUN_IDS[index]), controller, controller.snapshot(), ())
            for index, controller in enumerate(controllers)
        ),
        None,
        COMPARTMENT_QUANTITIES,
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
        elapsed_s=CaseInstant(elapsed_s),
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
    """A real, paused run that has both elapsed time and a recorded input.

    The fixture has both on purpose. `SimulationSnapshot.has_recorded_run`
    checks the two together, and a fixture with only one would leave the
    other untested by every test built on it.
    """

    controller = SimulationController()
    controller.start()
    _advance_to(controller, elapsed_s=elapsed_s)
    controller.set_fresh_gas_flow(FreshGasFlow(2.0))
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

    `SIMULATION_STEP_S` is the dashboard's cadence. `MAXIMUM_SIMULATION_STEP_S`
    is the control-resolution tolerance that `core/` declares. They are
    separate decisions that happen to be equal today, and this test stops
    them from drifting apart unnoticed. The test uses `<=` rather than
    equality on purpose. A numerical method that supported a coarser step
    would not make a coarser step a good render cadence. The test also checks
    the other end of the domain, `MINIMUM_SIMULATION_STEP_S` (`PL-YZ17`),
    although no cadence a display would want comes near it.
    """

    assert SIMULATION_STEP_S <= MAXIMUM_SIMULATION_STEP_S
    assert SIMULATION_STEP_S >= MINIMUM_SIMULATION_STEP_S


def test_a_tick_is_one_simulation_step_of_real_time() -> None:
    """Check the equality from which every displayed playback rate is derived.

    A tick advances `steps_per_tick` steps, and calling that "N times real
    time" is true only because one tick is one step long.
    """

    assert SIMULATION_TICK_INTERVAL_S == SIMULATION_STEP_S


def test_a_frame_is_two_control_grid_steps_at_every_rate() -> None:
    """Check the premise on which the argument in `PL-NBWP` was settled.

    At every rate the ladder offers, a reader sees the run at half the
    resolution at which they can act on it. `docs/MODEL.md` § "Supported
    simulation step" argues from this ratio, so this test checks the ratio
    directly rather than deriving it.
    """

    assert RENDER_INTERVAL_S == 2.0 * SIMULATION_TICK_INTERVAL_S


def test_the_dashboard_displays_at_most_two_runs() -> None:
    """`ROADMAP.md` § "v0.5.0 - the case you can branch": never more than two.

    The constructor's refusal belongs to `SimulationView` and is tested with
    the widget. The number itself belongs to the frame. `PL-HLD5`'s two-level
    encoding shows the run as line width, under a cap of two compartments, so
    it has nothing left with which to draw a third run.
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
    # PL-026: the numbers beside the banner come from the last completed
    # step, because the core rolls a failed step back. The reader must be
    # told that much. A banner that only says something went wrong leaves
    # them to guess whether the values are a solution of the model or debris.
    # Whether a step was rolled back is for the failure's own message to say,
    # as the message of `SimulationNumericalError` does. The banner does not
    # say it for every failure, because a setting that raised and a displayed
    # value the interface refused did not fail a step (`PL-7DJK`).
    assert "last completed step" in banner
    assert "rolled back" not in banner
    assert banner == (
        "Simulation stopped — SimulationNumericalError: the step could not be completed. "
        "The values shown are the last completed step. Reset to start a new run."
    )


def test_refresh_view_does_not_offer_to_resume_a_failed_run() -> None:
    enablement = transport(_snapshot(failure_reason="SimulationNumericalError: boom"))

    assert enablement.start_enabled is False
    assert enablement.pause_enabled is False


def test_a_halt_no_frame_was_drawn_for_is_worded_as_one_rather_than_as_a_failed_step() -> None:
    """`halt_notice` is the banner `present_halt` writes, with no frame on screen for it.

    A displayed value that the interface refused reaches a reader this way.
    The frame refuses the value again on every attempt, so this banner is the
    last one written. The banner says what is true of that screen: it shows
    the frame drawn before the stop, not the step at which the run stopped.
    It blames no step. The drawn banner's old wording sent the reader to a
    step that had been rolled back, when no step had failed (`PL-7DJK`).
    """

    reason = (
        "SimulationConfigurationError: alveolar partial_pressure_fraction of 1.0000001 is "
        "outside 0 to 1, the range a fraction of one atmosphere takes "
        '(docs/MODEL.md, "Concentrations")'
    )
    status = RunStatus(is_running=False, supported_limit_reason=None, failure_reason=reason)

    banner = halt_notice(status)

    assert banner is not None
    assert banner.startswith(f"Simulation stopped — {reason}.")
    assert "No frame of the stopped run could be drawn" in banner
    assert "the last frame drawn before it stopped" in banner
    assert "rolled back" not in banner
    assert "step that failed" not in banner
    assert banner.endswith("Reset to start a new run.")

    drawn = notice(status, None)

    assert drawn is not None
    assert drawn != banner
    assert "rolled back" not in drawn
    assert "The values shown are the last completed step" in drawn


def test_a_halt_is_stated_from_the_run_status_alone() -> None:
    """A `RunStatus`, which carries no compartment value, decides the three halt widgets.

    `present_halt` reads `SimulationController.record()` rather than a
    snapshot, because the snapshot's own `Fraction`s are among the values
    that can cause a halt (`PL-7DJK`). So `status_word`, `transport` and
    `halt_notice` each accept a bare status. A record and a snapshot are each
    a status, so every caller that draws a frame stays unchanged.
    """

    limit = "this run has reached 86400 s of simulated time"
    failed = RunStatus(
        is_running=False, supported_limit_reason=None, failure_reason="TypeError: boom"
    )
    at_limit = RunStatus(is_running=False, supported_limit_reason=limit, failure_reason=None)
    paused = RunStatus(is_running=False, supported_limit_reason=None, failure_reason=None)
    running = RunStatus(is_running=True, supported_limit_reason=None, failure_reason=None)

    assert isinstance(_snapshot(), RunStatus)
    assert status_word(failed).text == "Stopped — simulation error"
    assert status_word(at_limit).text == "Stopped — supported run length reached"
    assert status_word(paused).text == "Paused"
    assert status_word(running).text == "Running"
    assert (transport(failed).start_enabled, transport(failed).pause_enabled) == (False, False)
    assert (transport(at_limit).start_enabled, transport(at_limit).pause_enabled) == (False, False)
    assert (transport(running).start_enabled, transport(running).pause_enabled) == (False, True)
    assert halt_notice(failed) is not None
    assert "TypeError: boom" in (halt_notice(failed) or "")
    # Nothing is wrong with the state in which a run stops at the supported
    # run length. The next frame therefore draws, and one wording serves both.
    assert halt_notice(at_limit) == notice(at_limit, None)
    assert halt_notice(paused) is None
    assert halt_notice(running) is None


def test_a_run_is_stated_alike_from_its_record_and_from_the_snapshot_it_extends() -> None:
    """A run is stated the same way whether a frame drew it or only the controller's record exists.

    `RunView._write_statement` is the only writer of the run-state widgets.
    It is called with the snapshot a frame drew from, and with
    `SimulationController.record()` where no frame can draw (`PL-X7D5`). The
    statement reads only what the two share. A halt therefore states every
    widget that a frame would, using the same functions the frame uses.
    """

    controller = _paused_run_with_history()
    record = controller.record()
    adjustments = group_adjustments(record.control_timeline)

    from_snapshot, from_record = (
        run_statement(stated, adjustments, is_branch=False, comparing=False, banner=None)
        for stated in (controller.snapshot(), record)
    )

    assert from_snapshot == from_record
    assert from_record.agent_id == "sevoflurane"
    assert from_record.agent_name == "Sevoflurane"
    assert from_record.subtitle == format_subtitle("Sevoflurane")
    assert from_record.substance_heading == "Modelled concentrations: Sevoflurane"
    assert from_record.status == status_word(record)
    assert from_record.status.text == "Paused"
    assert from_record.transport == transport(record)
    assert from_record.timeline == timeline_panel(adjustments)
    assert from_record.timeline.entries != NO_CONTROL_CHANGES_TEXT
    assert from_record.banner is None


def test_a_run_statement_carries_the_locks_and_the_banner_it_is_given() -> None:
    """The statement carries what only the caller knows, exactly as given, and guesses nothing.

    Whether the run is a branch, and whether a second run is drawn, are facts
    that only the view knows. Which banner wording applies depends on whether
    a frame was drawn, and only the caller knows that (`halt_notice`,
    `notice`).
    """

    record = _paused_run_with_history().record()
    adjustments = group_adjustments(record.control_timeline)

    statement = run_statement(
        record, adjustments, is_branch=True, comparing=True, banner="the banner the caller worded"
    )

    assert statement.transport == transport(record, is_branch=True, comparing=True)
    assert statement.transport.selector_lock_reason == BRANCH_AGENT_LOCK_TEXT
    assert statement.timeline == timeline_panel(adjustments)
    assert statement.banner == "the banner the caller worded"


def test_a_refused_reset_names_the_way_out_in_the_banner() -> None:
    """Failure wordings name Reset as the way out, so a refused Reset's banner names another.

    `SimulationController.reset()` can refuse before it clears anything. When
    it does, the view halts the run through the failed-step path (`PL-M4M0`).
    The failure wording would then end by sending the reader to the control
    that was just refused. So the exit sentence says that Reset was refused,
    and names a way out that is open on every run. No setting can repair the
    refusal, because only a perfusion fraction written past its guard builds
    the record that Reset refuses (`PL-HQF5`, `PL-Z0HN`). So the exit sentence
    says that no setting can repair it, and sends the reader to close and
    reopen the application. Until `PL-01GY` the exit sentence named the
    setting that the refusal names, but that setting's dial no longer rebuilds
    the record. Starting a new case is not open on every run, because it uses
    the agent selector, which a comparison locks and which a branch does not
    have.

    The banner's reason decides which of two wordings states the refusal. A
    controller keeps the first failure it was given. On a run that had already
    failed for another reason, the exit sentence must carry the refusal
    itself. On a run that had not failed, or that this same refusal already
    stopped, the exit sentence points at the banner's reason, so a Reset pressed twice is stated
    once.
    """

    error = SimulationConfigurationError(
        "the tissue groups are perfused at 5.0 L/min in total but cardiac output is 6.0 L/min; "
        "the venous balance returns what the tissues receive, so the two must agree"
    )
    this_refusal = f"SimulationConfigurationError: {error}"
    refusal = RunStatus(is_running=False, supported_limit_reason=None, failure_reason=this_refusal)
    earlier = RunStatus(
        is_running=False,
        supported_limit_reason=None,
        failure_reason="SimulationNumericalError: boom",
    )
    running = RunStatus(is_running=True, supported_limit_reason=None, failure_reason=None)

    first = refused_reset_exit(error, recorded_failure_reason=None)
    pressed_again = refused_reset_exit(error, recorded_failure_reason=this_refusal)
    after_failure = refused_reset_exit(error, recorded_failure_reason=earlier.failure_reason)

    way_out = (
        "No setting can repair this, because only a fault in the simulator causes it. "
        "Close and reopen the application to start a new run."
    )
    assert first == f"Reset was refused for this reason. {way_out}"
    assert first == REFUSED_RESET_EXIT_TEMPLATE.format(way_out=REFUSED_RESET_WAY_OUT_TEXT)
    assert pressed_again == first
    assert after_failure == f"Reset was refused — {this_refusal}. {way_out}"
    assert after_failure == REFUSED_RESET_AFTER_FAILURE_EXIT_TEMPLATE.format(
        reason=this_refusal, way_out=REFUSED_RESET_WAY_OUT_TEXT
    )

    drawn = notice(refusal, None, refused_reset=first)
    undrawn = halt_notice(refusal, refused_reset=first)
    kept = notice(earlier, None, refused_reset=after_failure)

    assert drawn is not None and drawn.endswith(first)
    assert drawn.startswith(f"Simulation stopped — {refusal.failure_reason}. The values shown are")
    assert drawn.count("perfused at") == 1
    assert undrawn is not None and undrawn.endswith(first)
    assert "No frame of the stopped run could be drawn" in undrawn
    assert kept is not None and kept.endswith(after_failure)
    assert kept.startswith("Simulation stopped — SimulationNumericalError: boom. ")
    for banner in (drawn, undrawn, kept):
        assert RESET_EXIT_TEXT not in banner
    # Reset is the way out whenever it was not what was refused.
    assert (notice(refusal, None) or "").endswith(RESET_EXIT_TEXT)
    assert (halt_notice(refusal) or "").endswith(RESET_EXIT_TEXT)
    # And a run that is not stopped has no banner for an exit to end.
    assert notice(running, None, refused_reset=first) is None
    assert halt_notice(running, refused_reset=first) is None


def test_refresh_view_shows_no_notice_for_an_ordinary_run() -> None:
    for is_running in (True, False):
        snapshot = _snapshot(is_running=is_running)

        assert notice(snapshot, None) is None
        assert status_word(snapshot).text in {"Running", "Paused"}


def test_refresh_view_reports_the_supported_run_length_as_stopped_not_failed() -> None:
    """A correct stop is shown as a stop, which is the reason the field is separate.

    A run that reaches the limit has done everything right. The core refused
    the next step before taking it, nothing was miscalculated, and nothing was
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
    assert f"supported run length of {format_supported_run_length()}" in banner


def test_the_supported_run_length_notice_does_not_describe_a_failure() -> None:
    """No step failed and none was rolled back, so neither may be claimed.

    A notice that describes an event that did not happen fails the
    presentation half of the safety-critical standard: it puts the correct
    number under the wrong label. This notice points the reader at the
    model's own limits rather than at an imagined defect.
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
    # The banner says *why* the limit is where it is. A boundary given with no
    # reason looks like an arbitrary restriction, not the edge of the model.
    assert "metabolism" in banner
    assert "last completed step" in banner
    assert banner == (
        "Simulation stopped — this run reached the supported run length of "
        f"{format_supported_run_length()}. "
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

    The run is untouched and must not be marked failed. The refusal is
    therefore worded as a notice about one control, over a run that goes on
    unchanged (`PL-YK2V`). `halt_disposition` is never called for it.
    `RunView._apply_setting` decides which exceptions reach that function,
    and that is tested with the widget.
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
    """Start is offered only if the controller accepts it, Pause only while running, Reset always.

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

    A regression in the routing would not break the halt, because the run
    would still stop. It would only put "simulation error" over a model that
    stopped exactly where `docs/MODEL.md` says it must. Only a test would
    notice.
    """

    error = SimulationDomainLimitError("this run has reached 86400 s of simulated time")

    assert halt_disposition(error) == (
        HaltDisposition.SUPPORTED_LIMIT,
        "this run has reached 86400 s of simulated time",
    )


def test_halt_run_still_treats_an_unrecognised_exception_as_a_failure() -> None:
    """Only the narrow, named case is a supported limit, so anything else is a failure."""

    assert halt_disposition(ValueError("mass balance violated")) == (
        HaltDisposition.FAILURE,
        "ValueError: mass balance violated",
    )


def test_a_settings_raise_outside_the_project_hierarchy_halts_the_run() -> None:
    """`PL-YK2V`: a `TypeError` from a future refactor stops the run like a modelling failure.

    It is recorded with its type. The reader is looking at a display that
    can no longer be trusted to describe the run, so the reason must be
    readable.
    """

    assert halt_disposition(TypeError("a future refactor changed a signature")) == (
        HaltDisposition.FAILURE,
        "TypeError: a future refactor changed a signature",
    )


def test_a_settings_execution_error_halts_the_run_instead_of_reading_as_refused() -> None:
    """`PL-V6M0`: `SimulationExecutionError` means the run cannot continue safely.

    That is the opposite of a refused setting, so the error takes the failure
    channel with the rest of the hierarchy.
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
    assert settings[ControlInput.FRESH_GAS_FLOW].value_text == "3.0 L/min"
    assert settings[ControlInput.DELIVERED].value_text == "2.50%"
    assert settings[ControlInput.ALVEOLAR_VENTILATION].value_text == "5.5 L/min"
    assert settings[ControlInput.CARDIAC_OUTPUT].value_text == "6.5 L/min"


def test_the_snapshot_fixture_settings_are_all_distinct() -> None:
    """No two of the fixture's settings in one unit share a value.

    A readout that showed one setting's number under another setting's label
    passes any test in which the two settings are equal. The shipped defaults
    put the fresh gas flow and the alveolar ventilation both at 4.0 L/min.
    This fixture once did the same, so swapping the two in `setting_readouts`
    passed every unit test (`PL-5V5F`). Its dial also sat at sevoflurane's
    8.0% vaporizer maximum.

    The flows share litres per minute, and the dial, its maximum and the MAC
    share percent. A swap inside either group is the one a reader could not
    see from the unit, so the values inside each group must differ.
    """

    snapshot = _snapshot()
    flows_l_min = (
        snapshot.fresh_gas_flow_l_min,
        snapshot.alveolar_ventilation_l_min,
        snapshot.cardiac_output_l_min,
    )
    percents = (
        snapshot.delivered_concentration_percent,
        snapshot.max_delivered_concentration_percent,
        snapshot.agent_mac_percent,
    )

    assert len(set(flows_l_min)) == len(flows_l_min), flows_l_min
    assert len(set(percents)) == len(percents), percents


def test_metric_placeholders_match_the_formatter_before_a_run() -> None:
    """The value shown before a run must not go stale when the display resolution changes."""

    empty = format_percent(Fraction(0.0))

    for readout in readouts(SimulationController().snapshot(), DEFAULT_PLAYBACK_RATE)[1:]:
        assert readout.value == empty


def test_a_real_run_displays_a_filling_compartment_as_below_resolution() -> None:
    """End to end: real model, real step, real units, displayed string.

    The PL-040 decision turns on the fat compartment. Two minutes into a
    1 MAC sevoflurane run, fat holds some agent, but its reading is less than
    0.01%. The display must say so rather than round it to an empty
    compartment. By twenty minutes the reading has risen into the resolved
    range.
    """

    controller = SimulationController()
    controller.start()
    _advance_to(controller, 120.0)

    assert controller.snapshot().fat_partial_pressure_fraction > 0.0
    assert _readouts_by_name(controller.snapshot())["Fat"][1] == "<0.01%"
    # At the same instant, the alveolar reading is an ordinary value at the
    # documented resolution. The marker therefore appears only for a value
    # that is genuinely below the resolution, and is not a formatting quirk.
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
    end-tidal-equivalent concentration". Dead space, airway sampling delay,
    shunt and V/Q mismatch are all listed in "Known limitations". The value
    this readout shows is therefore not end-tidal in any patient, and
    end-tidal is the name of a measurement (`PL-NV9W`). The widget draws the
    gloss smaller than the name, and that is tested with the widget.
    """

    by_name = _readouts_by_name(_snapshot())

    assert _ALVEOLAR_METRIC_NAME in by_name
    assert by_name[_ALVEOLAR_METRIC_NAME][0] == _ALVEOLAR_METRIC_QUALIFIER
    assert by_name["Circuit"][0] == "inspired"


def test_every_compartment_is_readable_in_mac_multiples() -> None:
    """PL-DHV7's own acceptance criterion: the second unit is on every compartment.

    A MAC multiple on the vessel-rich, muscle and fat readouts is what makes
    a wash-in comparable across agents. "Simulated time" uses that line for
    the playback rate instead. Each of the six compartments carries a MAC
    multiple.
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
    one. Every MAC line is read from the snapshot's own divisor.
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

    `PL-SN2C` requires the multiplier beside the elapsed-time readout, not
    merely somewhere on the page. It must show at 1x too. The same formatter
    that writes the selector's options must state it.
    """

    clock = readouts(_snapshot(), rate)[0]

    assert clock.name == "Simulated time"
    assert clock.secondary == format_playback_rate(rate.multiplier)


def test_the_clock_panel_reads_in_the_chart_axis_form_past_an_hour() -> None:
    """`PL-Q4M4`: the clock and the axis state the same quantity in the same form."""

    clock = readouts(
        _snapshot(history=(_sample(5400.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),)), DEFAULT_PLAYBACK_RATE
    )[0]

    assert clock.value == "1h30m"
    assert clock.value == format_chart_time_label(5400.0)


def test_the_readout_row_names_the_substance_its_numbers_belong_to() -> None:
    """`PL-TCD1`: one frame uses one vocabulary, and the heading follows the agent.

    The heading is stated the same way from a snapshot and from the record
    that a halt is written from, because it names an agent and no
    compartment value (`PL-1YDD`).
    """

    assert substance_heading(_snapshot()) == "Modelled concentrations: Sevoflurane"
    assert (
        substance_heading(SimulationController(agent_id="desflurane").record())
        == "Modelled concentrations: Desflurane"
    )
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

    A readout with no gloss, and the clock with no MAC multiple, still keep
    those lines open. A widget that draws the four lines therefore never
    collapses one. The widest reflow step places all seven panels side by
    side.
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

    The clock just before the supported run length gives the widest value
    line, because every component of the compound form is present, with
    tenths. The longest playback rate gives the widest second line. Both are derived
    from the formatters rather than measured, so a change to either form
    moves the reservation with it.
    """

    assert WIDEST_READOUT_VALUE == format_elapsed(MAXIMUM_ELAPSED_SIMULATION_TIME_S - 0.1)
    assert len(WIDEST_READOUT_VALUE) >= len(format_percent(Fraction(1.0)))
    assert WIDEST_READOUT_SECONDARY == max(
        (format_playback_rate(rate.multiplier) for rate in SUPPORTED_PLAYBACK_RATES), key=len
    )
    assert len(WIDEST_READOUT_SECONDARY) >= len(
        format_mac_multiple(Fraction(1e-9), MacPercent(2.0))
    )


# --- the four setting controls -----------------------------------------------


def test_the_sliders_span_the_supported_input_ranges() -> None:
    """The interface offers exactly the domain the model declares.

    The test checks equality at both ends. A slider that reaches past a
    supported maximum offers the reader a setting that `core/` refuses. A
    slider that stops short silently narrows the reachable domain below the
    values at which the reference gates were run (`PL-0MLQ`). Here the fresh
    gas flow slider spans the model's whole envelope, because the shipped
    machine profile declares no deliverable range. A profile that declares a
    range narrows it
    (`test_the_fresh_gas_flow_control_narrows_to_a_declared_machine_range`).
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
        ControlInput.FRESH_GAS_FLOW: lambda flow: controller.set_fresh_gas_flow(FreshGasFlow(flow)),
        ControlInput.ALVEOLAR_VENTILATION: lambda flow: controller.set_alveolar_ventilation(
            AlveolarVentilation(flow)
        ),
        ControlInput.CARDIAC_OUTPUT: lambda flow: controller.set_cardiac_output(
            CardiacOutput(flow)
        ),
        ControlInput.DELIVERED: lambda percent: controller.set_delivered_concentration_percent(
            Percent(percent)
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


def _controller_on_a_machine_declaring(
    monkeypatch: pytest.MonkeyPatch,
    minimum_l_min: float | None,
    maximum_l_min: float | None,
    *,
    opening_flow_l_min: float = 4.0,
) -> SimulationController:
    """A controller whose machine profile declares a deliverable fresh gas flow range.

    The shipped profile declares no range. This fixture therefore builds the
    run from that file with the range added and nothing else changed, and
    parses it as the loader does. It hands the result to
    `AgentUptakeSystem.for_agent()` by replacing the loader that method calls.
    `tests/unit/test_circuit.py` uses the same route to give it another
    profile, until `PL-2FZ9` lets a run name its machine. A range of two
    `None`s keeps the shipped profile's undeclared range. The shipped profile
    opens the run at 4.0 L/min, so each range here contains that flow.
    `opening_flow_l_min` sets a different opening flow in its place.
    """

    payload = json.loads(
        files("anesthesia_sim.data.machines")
        .joinpath("reference_circle_system.json")
        .read_text(encoding="utf-8")
    )
    payload["default_fresh_gas_flow_l_min"] = opening_flow_l_min

    if minimum_l_min is not None and maximum_l_min is not None:
        payload["deliverable_fresh_gas_flow_range"] = {
            "minimum_l_min": minimum_l_min,
            "maximum_l_min": maximum_l_min,
        }

    machine = parse_breathing_circuit_parameters(payload)
    monkeypatch.setattr(uptake_system, "load_reference_circle_system_parameters", lambda: machine)

    return SimulationController()


def test_the_fresh_gas_flow_control_narrows_to_a_declared_machine_range(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A machine that cannot set what the model supports is not offered it (`PL-7CRY`).

    The profile declares 0.5 to 8.0 L/min, which is inside the model's
    envelope at both ends, so the control narrows at both ends. The settings
    are read from a real controller rather than a fixture snapshot, so the
    path is the one the interface runs: profile, circuit, snapshot, control.
    The test checks that each end is exact, not merely inside the range. The
    run accepts both ends and refuses the step past each one, in the
    machine's words, so the control is no narrower than the machine either.
    The other two flows keep the model's envelope, because no machine
    property limits them.
    """

    controller = _controller_on_a_machine_declaring(monkeypatch, 0.5, 8.0)
    settings = _settings_by_control(controller.snapshot())
    fresh_gas_flow = settings[ControlInput.FRESH_GAS_FLOW]
    step = slider_value(1, fresh_gas_flow.decimals)

    assert (fresh_gas_flow.minimum, fresh_gas_flow.maximum) == (0.5, 8.0)

    for endpoint in (fresh_gas_flow.minimum, fresh_gas_flow.maximum):
        controller.set_fresh_gas_flow(FreshGasFlow(endpoint))

    for beyond in (fresh_gas_flow.minimum - step, fresh_gas_flow.maximum + step):
        with pytest.raises(SimulationConfigurationError, match="outside what this machine"):
            controller.set_fresh_gas_flow(FreshGasFlow(beyond))

    assert (
        settings[ControlInput.ALVEOLAR_VENTILATION].minimum,
        settings[ControlInput.ALVEOLAR_VENTILATION].maximum,
        settings[ControlInput.CARDIAC_OUTPUT].minimum,
        settings[ControlInput.CARDIAC_OUTPUT].maximum,
    ) == (
        MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MINIMUM_CARDIAC_OUTPUT_L_MIN,
        MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    )


def test_a_declared_range_off_the_display_grid_offers_only_settings_inside_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A slider's ends are the steps just inside the range, never steps rounded past it.

    A machine with a minimum of 0.25 L/min is a plausible profile. At the
    flow control's one decimal place, the step nearest that minimum is
    0.2 L/min, which the machine refuses. Rounding half to even takes 8.75 to
    8.8 in the same way at the top. So the slider's minimum is the first step
    above, 0.3, and its maximum is the last step below, 8.7. Each is taken
    through the slider's own round trip, and the run accepts it.
    """

    controller = _controller_on_a_machine_declaring(monkeypatch, 0.25, 8.75)
    fresh_gas_flow = _settings_by_control(controller.snapshot())[ControlInput.FRESH_GAS_FLOW]
    decimals = fresh_gas_flow.decimals

    assert (fresh_gas_flow.minimum, fresh_gas_flow.maximum) == (0.3, 8.7)

    for endpoint in (fresh_gas_flow.minimum, fresh_gas_flow.maximum):
        controller.set_fresh_gas_flow(
            FreshGasFlow(slider_value(slider_position(endpoint, decimals), decimals))
        )

    for rounded_past in (0.2, 8.8):
        with pytest.raises(SimulationConfigurationError, match="outside what this machine"):
            controller.set_fresh_gas_flow(FreshGasFlow(rounded_past))


def test_a_control_with_no_step_inside_its_range_fails_rather_than_offering_a_refused_one() -> None:
    """A control with no step to offer raises, rather than collapsing onto a step outside the range.

    A machine range that is narrower than one 0.1 L/min step and contains no
    step is implausible, and no shipped profile has one. The profile format
    allows it, though, and the alternative is a plausible-looking control
    whose only setting the run refuses. A raise during a refresh is stated as
    a halt (`SimulationView.present`). A raise while the dashboard is being
    built stops the dashboard from opening.
    """

    with pytest.raises(
        ValueError,
        match=re.escape(
            "Fresh gas flow can offer no setting: no 0.1 L/min step lies inside 0.52 to 0.58 L/min"
        ),
    ):
        setting_readouts(_snapshot(accepted_fresh_gas_flow_range_l_min=(0.52, 0.58)))


def test_the_no_step_refusal_is_pinned_whole() -> None:
    """Pin the whole sentence the "Simulation stopped" banner shows for a control with no step.

    The test above matches only the start of the sentence, so the source the
    sentence cites could change unseen (`PL-79PK`).
    """

    with pytest.raises(ValueError) as refusal:
        setting_readouts(_snapshot(accepted_fresh_gas_flow_range_l_min=(0.52, 0.58)))

    assert str(refusal.value) == (
        "Fresh gas flow can offer no setting: no 0.1 L/min step lies inside 0.52 to 0.58 "
        'L/min, the range the run accepts (docs/MODEL.md, "Supported input ranges")'
    )


@pytest.mark.parametrize(
    ("minimum_l_min", "maximum_l_min", "opening_flow_l_min", "refusal"),
    (
        # This flow lies between two 0.1 L/min steps. The slider would sit at
        # 2.2, because `slider_position` rounds half to even, and the readout
        # would print 2.2 while the run used 2.25.
        (
            None,
            None,
            2.25,
            "Fresh gas flow is 2.25 L/min, which the slider cannot show: it offers 0.1 L/min "
            "steps from 0.0 to 10.0 L/min, so a machine profile must open the run on one of "
            "those steps (docs/MODEL.md, \"The model's envelope and a machine's deliverable "
            'range are two claims")',
        ),
        # This flow is the minimum of a range declared off the grid. The run
        # accepts 0.25, but the slider's minimum is the step just inside, 0.3,
        # and the readout would print 0.2 beside it.
        (
            0.25,
            8.75,
            0.25,
            "Fresh gas flow is 0.25 L/min, which the slider cannot show: it offers 0.1 L/min "
            "steps from 0.3 to 8.7 L/min, so a machine profile must open the run on one of "
            "those steps (docs/MODEL.md, \"The model's envelope and a machine's deliverable "
            'range are two claims")',
        ),
    ),
)
def test_an_opening_fresh_gas_flow_off_the_slider_grid_is_refused(
    monkeypatch: pytest.MonkeyPatch,
    minimum_l_min: float | None,
    maximum_l_min: float | None,
    opening_flow_l_min: float,
    refusal: str,
) -> None:
    """A profile cannot open the run at a flow its slider and readout cannot both show (`PL-1KQ9`).

    The run accepts each of these flows, so the core opens the run there. The
    controls refuse the flow when the dashboard builds them, because a slider
    position is a printed value (`PL-25KS`, decision D4). A slider standing
    at a neighbouring step, beside a rounded readout, would show a flow the
    run is not using. The whole sentence is pinned, because the reader sees
    it in place of a dashboard.
    """

    controller = _controller_on_a_machine_declaring(
        monkeypatch, minimum_l_min, maximum_l_min, opening_flow_l_min=opening_flow_l_min
    )

    assert controller.snapshot().fresh_gas_flow_l_min == opening_flow_l_min

    with pytest.raises(ValueError) as refused:
        setting_readouts(controller.snapshot())

    assert str(refused.value) == refusal


@pytest.mark.parametrize(
    ("minimum_l_min", "maximum_l_min", "opening_flow_l_min"),
    (
        (None, None, 2.3),
        (None, None, 0.1),
        (None, None, 10.0),
        (0.25, 8.75, 0.3),
        (0.25, 8.75, 8.7),
    ),
)
def test_an_opening_fresh_gas_flow_on_the_slider_grid_opens(
    monkeypatch: pytest.MonkeyPatch,
    minimum_l_min: float | None,
    maximum_l_min: float | None,
    opening_flow_l_min: float,
) -> None:
    """A run opens at a flow on one of the slider's steps, including each end of the offered range.

    The slider stands on the stated flow and the readout prints it. That is
    the property the refusal above protects.
    """

    controller = _controller_on_a_machine_declaring(
        monkeypatch, minimum_l_min, maximum_l_min, opening_flow_l_min=opening_flow_l_min
    )
    fresh_gas_flow = _settings_by_control(controller.snapshot())[ControlInput.FRESH_GAS_FLOW]

    assert fresh_gas_flow.value == opening_flow_l_min
    assert (
        slider_value(
            slider_position(fresh_gas_flow.value, fresh_gas_flow.decimals), fresh_gas_flow.decimals
        )
        == opening_flow_l_min
    )
    assert fresh_gas_flow.value_text == f"{opening_flow_l_min:.1f} L/min"


@pytest.mark.parametrize(
    ("control", "controller_settings", "refusal"),
    (
        # This value lies between two 0.1 L/min steps. The slider would sit at
        # 5.2, because `slider_position` rounds half to even, and the readout
        # would print 5.2 while the run used 5.25.
        (
            ControlInput.ALVEOLAR_VENTILATION,
            {"alveolar_ventilation_l_min": AlveolarVentilation(5.25)},
            "Alveolar ventilation is 5.25 L/min, which the slider cannot show: it offers "
            "0.1 L/min steps from 0.0 to 12.0 L/min, so a patient profile must open the run "
            'on one of those steps (docs/MODEL.md, "Supported input ranges")',
        ),
        (
            ControlInput.CARDIAC_OUTPUT,
            {"cardiac_output_l_min": CardiacOutput(5.25)},
            "Cardiac output is 5.25 L/min, which the slider cannot show: it offers "
            "0.1 L/min steps from 0.0 to 10.0 L/min, so a patient profile must open the run "
            'on one of those steps (docs/MODEL.md, "Supported input ranges")',
        ),
    ),
)
def test_an_opening_ventilation_or_cardiac_output_off_the_slider_grid_is_refused(
    control: ControlInput, controller_settings: dict[str, Any], refusal: str
) -> None:
    """A run cannot open at a ventilation or cardiac output its slider cannot show (`PL-96SQ`).

    The patient profile states both opening values. The core checks only
    that they are positive and finite, so it accepts 5.25 L/min and opens
    the run. The controls reject that value, as they reject an off-grid
    fresh gas flow (`PL-1KQ9`). Otherwise the slider would sit at 5.2,
    beside a readout showing 5.2, while the run used 5.25. This test opens
    the run through the controller's explicit setting rather than a patient
    file. That is enough, because the check reads the setting in force,
    whatever stated it.
    """

    controller = SimulationController(**controller_settings)

    assert {
        ControlInput.ALVEOLAR_VENTILATION: controller.snapshot().alveolar_ventilation_l_min,
        ControlInput.CARDIAC_OUTPUT: controller.snapshot().cardiac_output_l_min,
    }[control] == 5.25

    with pytest.raises(ValueError) as refused:
        setting_readouts(controller.snapshot())

    assert str(refused.value) == refusal


@pytest.mark.parametrize(
    ("control", "controller_settings"),
    (
        (
            ControlInput.ALVEOLAR_VENTILATION,
            {"alveolar_ventilation_l_min": AlveolarVentilation(5.3)},
        ),
        (
            ControlInput.ALVEOLAR_VENTILATION,
            {"alveolar_ventilation_l_min": AlveolarVentilation(12.0)},
        ),
        (ControlInput.CARDIAC_OUTPUT, {"cardiac_output_l_min": CardiacOutput(5.3)}),
        (ControlInput.CARDIAC_OUTPUT, {"cardiac_output_l_min": CardiacOutput(10.0)}),
    ),
)
def test_an_opening_ventilation_or_cardiac_output_on_the_slider_grid_opens(
    control: ControlInput, controller_settings: dict[str, Any]
) -> None:
    """A run opens at a ventilation or cardiac output on a slider step, including the range's top.

    The readout shows the stated value. That is the property that the
    rejection in the test above protects.
    """

    controller = SimulationController(**controller_settings)
    [stated] = controller_settings.values()
    readout = _settings_by_control(controller.snapshot())[control]

    assert readout.value == stated
    assert readout.value_text == f"{stated:.1f} L/min"


@pytest.mark.parametrize(
    ("minimum", "maximum", "decimals", "offered"),
    (
        # Whole steps are offered as they are, which is every shipped range.
        (0.0, 10.0, FLOW_DISPLAY_DECIMALS, (0.0, 10.0)),
        (0.0, 8.0, CONCENTRATION_DISPLAY_DECIMALS, (0.0, 8.0)),
        # These ends are steps, although their products with 100 are not
        # whole floats: 0.07 * 100 is 7.000000000000001 and 0.29 * 100 is
        # 28.999999999999996. Neither end may be moved inward off itself.
        (0.07, 0.29, CONCENTRATION_DISPLAY_DECIMALS, (0.07, 0.29)),
        # Each of these ends is one unit in the last place outside a step, and
        # its product with 10 rounds onto that step. The step is outside the
        # range, so it is not offered.
        (math.nextafter(1.7, math.inf), 9.0, FLOW_DISPLAY_DECIMALS, (1.8, 9.0)),
        (0.5, math.nextafter(0.9, -math.inf), FLOW_DISPLAY_DECIMALS, (0.5, 0.8)),
        # Ends between steps move inward, never outward.
        (0.05, 9.95, FLOW_DISPLAY_DECIMALS, (0.1, 9.9)),
        (0.25, 8.75, FLOW_DISPLAY_DECIMALS, (0.3, 8.7)),
        # A one-step range, and a range holding no step at all.
        (2.0, 2.0, FLOW_DISPLAY_DECIMALS, (2.0, 2.0)),
        (0.52, 0.58, FLOW_DISPLAY_DECIMALS, None),
    ),
)
def test_offered_range_keeps_both_ends_inside_the_range(
    minimum: float, maximum: float, decimals: int, offered: tuple[float, float] | None
) -> None:
    """The slider's ends are steps, inside the range, and as wide as the range allows."""

    assert offered_range(minimum, maximum, decimals) == offered


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

    The test covers both resolutions: one decimal place for the three flows,
    and two for the delivered percent. A position is a count of the display resolution, so
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

    "Fresh gas flow" alone is the label on a flowmeter bank, and a flowmeter
    measures only the carrier gas. In the model's circuit balance, this flow
    is the whole stream leaving the vaporizer. The two differ by 22% at
    desflurane's 18% dial (`PL-71CF`). The widget sets the gloss's size and
    italic style.
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
    """Two ceilings that used to be the same one, and had to become separate (`PL-CC23`).

    The delivered dial tracks the real vaporizer cap. The chart's ceiling is
    the same MAC multiple for every agent. For desflurane the two numbers
    are equal but the reasons differ. For isoflurane the two numbers visibly
    differ.
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
    """The dial, the one control a reader sets, is shown in the units of the traces it fills."""

    delivered = _settings_by_control(_snapshot())[ControlInput.DELIVERED]

    assert delivered.value_text == format_percent(Fraction(0.025))
    assert delivered.secondary == format_mac_multiple(Fraction(0.025), MacPercent(2.0))
    assert delivered.secondary == "1.25 ×MAC"


def test_the_delivered_line_prints_the_dial_in_both_units() -> None:
    """The readout heading repeats the dial in the dial's own two units (`PL-NWTM`).

    2.5% sevoflurane over its 2.0% MAC is 1.25 ×MAC, worked here by hand
    rather than read back from the readout under test.
    """

    delivered = _settings_by_control(_snapshot())[ControlInput.DELIVERED]

    assert delivered_line(delivered) == "Delivered 2.50% (1.25 ×MAC)"


def test_the_delivered_line_refuses_a_flow_readout() -> None:
    """A flow has no MAC line, and printing it as the dial would show a flow as a concentration."""

    flow = _settings_by_control(_snapshot())[ControlInput.FRESH_GAS_FLOW]

    with pytest.raises(ValueError, match="not from fresh_gas_flow's"):
        delivered_line(flow)


def test_the_end_to_end_mac_path_reaches_the_panel_from_a_real_run() -> None:
    """Patient inputs, model selection, calculation, units, formatting, display."""

    controller = SimulationController(agent_id="desflurane")
    controller.start()

    for _ in range(600):
        controller.advance(SIMULATION_STEP_S)

    snapshot = controller.snapshot()

    assert snapshot.agent_mac_percent == 6.0
    assert _readouts_by_name(snapshot)["Alveolar"][2] == format_mac_multiple(
        snapshot.alveolar_partial_pressure_fraction, MacPercent(6.0)
    )
    # The dial starts at the agent's own 1 MAC, so after a minute of wash-in
    # the alveolar compartment is above zero and below that 1 MAC.
    alveolar_mac = snapshot.alveolar_partial_pressure_fraction * 100.0 / 6.0
    assert 0.0 < alveolar_mac < 1.0
    assert _settings_by_control(snapshot)[ControlInput.DELIVERED].secondary == "1.00 ×MAC"


@pytest.mark.parametrize(
    ("agent_id", "fraction_text", "mac_multiple_text"),
    [
        ("sevoflurane", "0.98%", "0.49 ×MAC"),
        ("isoflurane", "0.42%", "0.35 ×MAC"),
        ("desflurane", "3.59%", "0.60 ×MAC"),
    ],
)
def test_each_agents_alveolar_readout_at_five_minutes_is_pinned_as_displayed(
    agent_id: str, fraction_text: str, mac_multiple_text: str
) -> None:
    """The alveolar readout's text after 5 minutes at each agent's own 1 MAC (`PL-QJXS`).

    The end-to-end test above takes its expected text from the formatter it
    tests, so a wrong value that is formatted correctly passes it. These
    strings were read from the display on 2026-10-17, on a fresh run at the
    data files' default settings. They pin the model's own output, so they
    catch a later change to the calculation, the agent's data or the
    formatting. They are not a comparison with measured data, which is what
    `tests/reference/` holds.
    """

    controller = SimulationController(agent_id=agent_id)
    controller.start()

    for _ in range(3000):
        controller.advance(SIMULATION_STEP_S)

    snapshot = controller.snapshot()
    _, value, secondary = _readouts_by_name(snapshot)["Alveolar"]

    assert snapshot.elapsed_s == 300.0
    assert (value, secondary) == (fraction_text, mac_multiple_text)


def test_the_delivered_dial_is_held_in_percent_and_read_as_a_fraction() -> None:
    """The dial is stored as a percent, and the model reads it as a fraction (`PL-NJPB`)."""

    controller = SimulationController()

    controller.set_delivered_concentration_percent(Percent(6.5))

    assert controller.snapshot().delivered_concentration_percent == 6.5
    assert controller.snapshot().delivered_partial_pressure_fraction == pytest.approx(0.065)
    assert _settings_by_control(controller.snapshot())[ControlInput.DELIVERED].value_text == (
        "6.50%"
    )


# --- the accounting panel ------------------------------------------------------


def test_refresh_view_reports_valid_agent_accounting() -> None:
    """Amounts show one decimal of a litre (`PL-TG60`), and each residual shows a power of ten."""

    panel = accounting(_snapshot(passes_validation=True))

    assert panel.status.text == "Valid"
    assert panel.status.emphasis is Emphasis.ACCENT
    assert "still accounts for all delivered agent" in panel.detail
    assert panel.amounts == (
        "Delivered: <0.1 L\n"
        "Exhausted: <0.1 L\n"
        "Stored: <0.1 L\n"
        "Unaccounted: <1e-12 L\n"
        "Absolute error: <1e-12 L"
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

    assert timeline_panel(adjustments).entries == "12s · Fresh gas flow 4.0 L/min -> 2.0 L/min"


def test_the_list_reads_most_recent_first() -> None:
    """A fixed panel has to show the change the reader has just made."""

    adjustments = group_adjustments(
        (
            _control_change(10.0, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),
            _control_change(20.0, ControlInput.CARDIAC_OUTPUT, 5.0, 3.0, adjustment=2),
        )
    )
    lines = timeline_panel(adjustments).entries.splitlines()

    assert lines[0].startswith("20s")
    assert lines[1].startswith("10s")


def test_a_run_with_no_changes_says_so_rather_than_showing_an_empty_panel() -> None:
    panel = timeline_panel(())

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
    panel = timeline_panel(adjustments)

    assert len(panel.entries.splitlines()) == MAX_LISTED_ADJUSTMENTS == 12
    assert "3 earlier change(s) not listed" in panel.overflow


def test_changes_the_chart_cannot_mark_are_counted_rather_than_dropped() -> None:
    """The plot follows the panel's rule: changes it cannot mark are counted, not dropped.

    A chart that stops marking changes without saying so implies that no more
    changes happened. The count appears on the chart whose window it covers,
    not in the run's control-change panel, because each chart has its own
    window (`PL-L59K`).
    """

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
    assert unmarked_changes_lines(frame) == ("2 control change(s) in this window not marked",)
    assert "not marked" not in timeline_panel(adjustments).overflow


def test_each_run_s_unmarked_changes_line_is_named_while_runs_are_compared() -> None:
    """The count is in a chart the runs share, so it names the run it counts for (`PL-25DD`)."""

    timeline = tuple(
        _control_change(
            float(index), ControlInput.FRESH_GAS_FLOW, 4.0, 4.0 - index * 0.01, adjustment=index + 1
        )
        for index in range(MAX_CHART_CONTROL_MARKS + 2)
    )
    adjustments = group_adjustments(timeline)
    busy = _fake_controller(history=_run_history(600), control_timeline=timeline)
    quiet = _fake_controller(history=_run_history(600))
    frame = assemble_chart_frame(
        (
            RunInput(run_label(FIRST_RUN), busy, busy.snapshot(), adjustments),
            RunInput(run_label(SECOND_RUN), quiet, quiet.snapshot(), ()),
        ),
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
    )

    assert unmarked_changes_lines(frame) == (
        "Run 1 — 2 control change(s) in this window not marked",
        None,
    )


def test_a_chart_whose_window_marks_every_change_says_nothing_about_marks() -> None:
    frame = _frame(_fake_controller(history=_run_history(600)))

    assert frame.runs[0].undrawn_control_marks == 0
    assert unmarked_changes_lines(frame) == (None,)


def test_the_unlisted_count_stands_alone_in_the_overflow_line() -> None:
    adjustments = group_adjustments(
        tuple(
            _control_change(
                float(index), ControlInput.CARDIAC_OUTPUT, 5.0, 4.0, adjustment=index + 1
            )
            for index in range(MAX_LISTED_ADJUSTMENTS + 1)
        )
    )

    assert timeline_panel(adjustments).overflow == "1 earlier change(s) not listed"


def test_the_interface_says_a_control_mark_is_an_input_not_a_measurement() -> None:
    """The panel and the legend both say a mark is a setting, never a reading.

    The widget's tests check that these strings reach the assembled
    interface. This test checks the words themselves.
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
        "Sevoflurane", MacPercent(2.0)
    )
    assert mac_reference_caption(_frame(_fake_controller())) == "1 MAC sevoflurane = 2.0%"

    desflurane = _fake_controller(
        agent_id="desflurane",
        agent_display_name="Desflurane",
        max_delivered_concentration_percent=18.0,
    )

    assert mac_reference_caption(_frame(desflurane)) == format_mac_reference(
        "Desflurane", MacPercent(6.0)
    )


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
    """The failure mode that PL-CC23's fixed ceiling introduces, and the guard against it.

    A clipped trace is drawn as a horizontal line at the top of the plot, and
    a horizontal line looks like a plateau. The plot therefore says that the
    trace is clipped, rather than relying on the reader to notice.
    """

    # 8% circuit is 4 MAC of sevoflurane, against a 6% (3 MAC) ceiling.
    # Alveolar at 5% stays below the ceiling. That makes this a test of
    # *which* compartments are named, not only of whether any is named.
    history = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1.0, 0.08, 0.05, 0.01, 0.01, 0.0, 0.0),
    )
    text = off_scale_notice(_frame(_fake_controller(history=history)), 0)

    assert text is not None
    assert "Circuit" in text
    assert "Alveolar" not in text
    # The notice must say where the unclipped number is. Otherwise it reports
    # a problem and leaves the reader without the value.
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


# --- attributing a shared column's lines to the run that produced them ----------


def test_a_lone_run_s_shared_line_is_left_unnamed() -> None:
    """A lone run's line gets no name, because there is no other run to tell it apart from.

    The panels follow the same rule.
    """

    frame = _frame(_fake_controller(history=_run_history(40)))

    assert compared_run_line("Now: F_A/F_I = 0.50", frame, 0) == "Now: F_A/F_I = 0.50"


def test_a_compared_run_s_shared_line_opens_with_the_run_s_own_name() -> None:
    """The line opens with the name the legend and the run's panel use, rather than ending with it.

    Both lines that this function composes sit in a column the runs share.
    The run name is the only thing that tells two otherwise identical
    openings apart. A name placed after a wrapped sentence is one the reader
    must hunt for (`PL-25DD`).
    """

    frame = _compared_frame(
        _fake_controller(history=_run_history(40)), _fake_controller(history=_run_history(40))
    )

    assert compared_run_line("Now: F_A/F_I = 0.50", frame, 0) == "Run 1 — Now: F_A/F_I = 0.50"
    assert compared_run_line("Now: F_A/F_I = 0.61", frame, 1) == "Run 2 — Now: F_A/F_I = 0.61"


def test_the_shared_line_takes_its_name_from_the_frame_that_drew_the_value() -> None:
    """The name and the line come from the same frame.

    So no caller can pair one run's name with another run's line.
    """

    frame = _compared_frame(
        _fake_controller(history=_run_history(40)), _fake_controller(history=_run_history(40))
    )

    for index, run in enumerate(frame.runs):
        assert compared_run_line("line", frame, index).startswith(f"{run.label} ")


def test_a_shared_line_for_a_run_the_frame_does_not_hold_is_refused() -> None:
    """A line that cannot be attributed to a run fails, rather than silently losing its name."""

    single = _frame(_fake_controller(history=_run_history(40)))

    with pytest.raises(IndexError):
        compared_run_line("Now: F_A/F_I = 0.50", single, 1)


def test_each_run_s_off_scale_line_is_named_while_runs_are_compared() -> None:
    """A chart writes one line per run from its frame, named while runs are compared (`PL-L59K`)."""

    inside = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1.0, 0.02, 0.018, 0.015, 0.014, 0.01, 0.005),
    )
    above = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1.0, 0.08, 0.01, 0.01, 0.01, 0.0, 0.0),
    )
    lone = _frame(_fake_controller(history=above))
    compared = _compared_frame(_fake_controller(history=above), _fake_controller(history=inside))

    assert off_scale_lines(lone) == (off_scale_notice(lone, 0),)
    assert off_scale_lines(lone)[0] is not None
    assert off_scale_lines(compared) == (
        compared_run_line(off_scale_notice(compared, 0) or "", compared, 0),
        None,
    )


def test_off_scale_notice_refuses_a_negative_run_index() -> None:
    """A run index of -1 is rejected rather than treated as the last run (`PL-7694`).

    Python treats `frame.runs[-1]` as the last run. Here run 1 stays inside
    the axis and run 2 rises above it. An index of -1 that reached the frame
    would therefore report run 2's clipped circuit trace under the name of
    whichever run the caller meant. `compared_run_line` takes the same index
    and rejects it for the same reason.
    """

    inside = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1.0, 0.02, 0.018, 0.015, 0.014, 0.01, 0.005),
    )
    above = (
        _sample(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1.0, 0.08, 0.01, 0.01, 0.01, 0.0, 0.0),
    )
    compared = _compared_frame(_fake_controller(history=inside), _fake_controller(history=above))

    # Check that the frame is as described: the last run is the one off scale.
    assert off_scale_notice(compared, 0) is None
    assert off_scale_notice(compared, 1) is not None

    with pytest.raises(ValueError, match="a run index is a position among the chart's runs"):
        off_scale_notice(compared, -1)

    with pytest.raises(ValueError, match="a run index is a position among the chart's runs"):
        compared_run_line("line", compared, -1)


def test_each_run_s_wash_in_state_line_counts_its_own_undrawn_stretches() -> None:
    controllers = (
        _fake_controller(history=_run_history(40)),
        _fake_controller(history=_run_history(40)),
    )
    frame = _compared_frame(*controllers)
    snapshots = tuple(controller.snapshot() for controller in controllers)

    assert wash_in_state_lines(frame, snapshots) == tuple(
        compared_run_line(
            wash_in_state(snapshot, frame.runs[index].undrawn_wash_in_stretches), frame, index
        )
        for index, snapshot in enumerate(snapshots)
    )


def test_wash_in_state_lines_refuse_snapshots_that_do_not_match_the_frame() -> None:
    """A line from another run's snapshot would put one run's F_A/F_I under another's name."""

    controller = _fake_controller(history=_run_history(40))
    frame = _frame(controller)

    with pytest.raises(ValueError, match="2 snapshot"):
        wash_in_state_lines(frame, (controller.snapshot(), controller.snapshot()))


def test_a_lone_run_s_banner_is_left_unnamed() -> None:
    """The panels and both legends follow this rule, so a run name never becomes standing text."""

    assert compared_run_notice("Simulation stopped — it failed.", None) == (
        "Simulation stopped — it failed."
    )


def test_a_compared_run_s_banner_opens_with_the_run_s_own_name() -> None:
    """Each of the three notices says something about a run but names no run (`PL-TSZM`)."""

    assert compared_run_notice("Simulation stopped — it failed.", "Run 2") == (
        "Run 2: Simulation stopped — it failed."
    )
    assert compared_run_notice(
        "Setting refused — above the vaporizer maximum. The simulation is unchanged "
        "and still running its previous setting.",
        "Run 1",
    ) == (
        "Run 1: Setting refused — above the vaporizer maximum. The simulation is "
        "unchanged and still running its previous setting."
    )


def test_the_banner_s_name_is_separated_by_a_colon_not_a_second_em_dash() -> None:
    """Every notice already opens with `label — detail`, so a prefixed em dash would look like it.

    `COMPARED_RUN_LINE_TEMPLATE` may use an em dash, because the lines it
    names, such as "Now: F_A/F_I" and "Above the top of the plot:", have no
    em dash of their own. The notices do have one. Two em dashes at different
    depths would make "Run 2" look like the banner's own label, with
    "Simulation stopped" as its detail (`PL-TSZM`).
    """

    named = compared_run_notice("Simulation stopped — it failed.", "Run 2")

    assert named is not None
    assert named.startswith("Run 2: ")
    assert named.count("—") == 1


def test_a_run_with_nothing_to_say_gets_no_banner_named_or_not() -> None:
    """A hidden banner stays hidden: an attribution is not a reason to show one."""

    assert compared_run_notice(None, "Run 2") is None
    assert compared_run_notice(None, None) is None


def test_a_banner_for_a_run_whose_name_is_empty_is_refused() -> None:
    """A bare leading colon looks like a formatting fault, and like a run whose name is blank."""

    with pytest.raises(ValueError, match="cannot be empty"):
        compared_run_notice("Simulation stopped — it failed.", "")


def test_a_lone_run_s_panel_headings_are_left_unnamed() -> None:
    """A lone run has no other run to be told apart from, so the sidebar gains no fixed text."""

    assert compared_panel_heading(ACCOUNTING_HEADING, None) == "Agent accounting validation"
    assert compared_panel_heading(CONTROL_TIMELINE_HEADING, None) == "Control changes"


def test_a_compared_run_s_panel_heading_closes_with_the_run_s_own_name() -> None:
    """The kind of record comes first and the run last, which is the legend's order, not the line's.

    A reader finds a panel by the kind of record it holds. Once a branch is
    drawn, four panels stack in the sidebar, two of each kind. So the kind
    comes first, and the run name tells two panels of the same kind apart. A
    compared legend entry puts the compartment first in exactly the same way
    (`PL-C3GS`).
    """

    assert (
        compared_panel_heading(ACCOUNTING_HEADING, run_label(SECOND_RUN))
        == "Agent accounting validation — Run 2"
    )
    assert (
        compared_panel_heading(CONTROL_TIMELINE_HEADING, run_label(FIRST_RUN))
        == "Control changes — Run 1"
    )


def test_a_panel_heading_is_named_without_knowing_which_panel_it_is() -> None:
    """Any heading works, so the next view that gets its own area takes the same attribution."""

    assert (
        compared_panel_heading("Bookmarked states", run_label(FIRST_RUN))
        == "Bookmarked states — Run 1"
    )


def test_the_chart_says_so_when_no_compartment_is_drawn() -> None:
    """A blank plot looks like a display that has failed, not like an empty view."""

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

    The circuit volume does carry over, so naming it was true. It was also
    lopsided, because `PL-GYH2` retired the only setter that could have
    changed it. The test checks the property rather than the exact string.
    """

    sentence = NEW_CASE_CARRYOVER_TEMPLATE.lower()

    assert "circuit volume" not in sentence
    for setting in ("fresh gas flow", "alveolar ventilation", "cardiac output"):
        assert setting in sentence


def test_the_confirmations_trailing_action_is_the_one_that_keeps_the_case() -> None:
    """The press a reader makes without reading must not destroy the run.

    The labels name their outcomes. The dialog decides which button is
    filled, placed last and made the default, and that is tested with the
    dialog.
    """

    question = new_case_question(_paused_run_with_history().snapshot(), "Desflurane", 1)

    assert question.discard_label == "Discard and start desflurane"
    assert question.keep_label == "Keep the sevoflurane case"


# --- the trunk's Reset question -------------------------------------------------


def test_a_branch_holding_nothing_is_not_at_stake() -> None:
    """`PL-W5WX`: a branch just taken holds nothing, so the trunk's Reset asks nothing about it.

    A branch opens at its fork, so its elapsed time is greater than zero
    from the start. What it holds is counted from the fork (`PL-7TBQ`).
    """

    branch = BranchedCase(_paused_run_with_history()).fork_at(CaseInstant(60.0))

    assert branch_at_stake("Run 2", branch.began_at_s, branch.snapshot(), 0) is None


def test_a_branch_run_past_its_fork_is_at_stake_with_both_instants() -> None:
    """How far the branch has run is stated as the instant its clock reads.

    The test uses a branch actually stepped to that instant.
    """

    branch = BranchedCase(_paused_run_with_history()).fork_at(CaseInstant(60.0))
    branch.start()
    _advance_to(branch, elapsed_s=90.0)
    branch.pause()

    assert branch_at_stake("Run 2", branch.began_at_s, branch.snapshot(), 0) == BranchAtStake(
        name="Run 2", began_at_s=60.0, elapsed_s=90.0, adjustment_count=0
    )


def test_a_branch_whose_snapshot_refuses_is_at_stake_with_no_instant_stated() -> None:
    """A branch that cannot be read is not known to hold nothing, so the question is still asked."""

    assert branch_at_stake("Run 2", CaseInstant(60.0), None, 0) == BranchAtStake(
        name="Run 2", began_at_s=60.0, elapsed_s=None, adjustment_count=0
    )


def test_the_trunk_reset_question_names_both_runs_and_what_the_trunk_keeps() -> None:
    """Every line of the question is a literal here, so the test, not the code, owns the wording.

    The keep button is named for the branch, because the branch is what the
    reader keeps by declining. The trunk is not touched either way.
    """

    question = trunk_reset_question("Run 1", (BranchAtStake("Run 2", 60.0, 330.5, 2),))

    assert question.title == "Reset Run 1 and discard Run 2?"
    assert question.body == (
        "Run 1's Reset starts the case over, and a branch cannot outlive the run it was "
        "taken from.",
        "Run 2 — branched at 1m and run to 5m30.5s, 2 recorded control changes — will be "
        "discarded along with its chart history. This cannot be undone.",
        "Run 1 goes back to induction with its settings and bookmarks kept.",
    )
    assert question.discard_label == "Reset and discard Run 2"
    assert question.keep_label == "Keep Run 2"


def test_a_trunk_reset_question_about_no_branch_is_refused() -> None:
    """A Reset that discards nothing asks nothing, so asking about no branch is an error."""

    with pytest.raises(ValueError, match="none was given"):
        trunk_reset_question("Run 1", ())


# --- layout and the interpretation line -----------------------------------------


def test_readout_columns_are_the_widest_rung_whose_panels_fit() -> None:
    """Seven columns where seven panels fit, otherwise four, two or one (`PL-8M05`).

    The rungs are fixed, but the widths are not. A panel 100 px wide, with
    10 px between neighbours, needs 760 px for seven, 430 for four and 210
    for two. The count steps down one pixel below each of those widths. The
    minimum is one column, even for a row narrower than a single panel.
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
    """The clock's wide reservation widens its own column and no other (`PL-3355`).

    Take a clock 195 px wide beside six compartments of 135 px, with 6 px
    between columns. Seven across needs 195 + 6 x 135 + 6 x 6 = 1041 px, not
    7 x 195 + 36 = 1401. Four across puts the clock and the fifth panel in
    one column, so the row needs 195 + 3 x 135 + 18 = 618 px. Two across
    needs 195 + 135 + 6 = 336. One column needs the clock's 195.
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
    """One reservation per panel, and the clock's is the widest elapsed form (`PL-3355`)."""

    assert len(READOUT_RESERVATIONS) == len(READOUT_PANELS)
    assert READOUT_RESERVATIONS[0] == (WIDEST_READOUT_VALUE, WIDEST_READOUT_SECONDARY)
    assert set(READOUT_RESERVATIONS[1:]) == {
        (WIDEST_COMPARTMENT_VALUE, WIDEST_COMPARTMENT_SECONDARY)
    }
    assert WIDEST_COMPARTMENT_VALUE == format_percent(Fraction(1.0))
    assert WIDEST_COMPARTMENT_SECONDARY.endswith(MAC_UNIT_SUFFIX)


def test_the_interface_says_the_readouts_are_model_outputs_not_measurements() -> None:
    """`PL-2K1R`: the interpretation line, distinct from the use disclaimer.

    The line is short, sits beside the values it qualifies, and says what the
    value *is* rather than what the reader must not do. The widget's tests
    check that it is placed on the readout section's heading row.
    """

    assert INTERPRETATION_DISCLAIMER_TEXT == "Model outputs — not measurements."


def test_the_educational_disclaimer_says_what_the_tool_is_not() -> None:
    """`PL-GMM7`: the one string that carries the project's regulatory posture, verbatim.

    Coverage cannot protect it, because the line executes whenever the
    dashboard is built. So the words are pinned here, and
    `test_the_dashboard_carries_the_educational_disclaimer` checks that the
    dashboard places them.
    """

    assert USE_DISCLAIMER_TEXT == (
        "Educational simulation only. This idealized model is not a clinical prediction, "
        "monitoring, or dosing tool."
    )


# ----------------------------------------------------------- bookmark panel
#
# These tests cover what the two listings claim, and what each row says about
# a mark's standing. A run detects when it reaches a mark (`PL-CTD7`). So a
# row says "reached" for a target the run halted on, or one inside the step
# the run stands on or opened on (`MarkStanding.REACHED`). Other words describe
# a mark the clock has passed, one the run can no longer reach, and one on a run
# that failed. A mark the run can still reach adds no words to its row.


def _marks() -> BookmarkSet:
    """One mark of each kind, both named."""

    return (
        BookmarkSet()
        .with_time_bookmark(TimeBookmark(CaseInstant(600.0), "intubation"))
        .with_mac_target(MacTarget(RecordedQuantity.VESSEL_RICH, MacMultiple(0.8), "wash-in"))
    )


def _target_row(target: MacTarget, *, reached: bool = False, run_failed: bool = False) -> str:
    """The row a lone run draws for `target`, given what that run has done.

    The row is built through `bookmark_panel`, the only path a drawn row
    takes (`PL-08CR`). The standing is computed from the run's facts rather
    than passed in, so a test here pins the words on the path a reader sees.
    """

    marks = BookmarkSet().with_mac_target(target)
    crossings: frozenset[tuple[RecordedQuantity, float]] = (
        frozenset({target.crossing_key}) if reached else frozenset()
    )
    standings = _standings(marks, reached_crossings=crossings, run_failed=run_failed)

    return bookmark_panel(marks, _one_run(standings)).targets.rows[0]


def _time_row(
    bookmark: TimeBookmark,
    *,
    opened_at_s: float = 0.0,
    elapsed_s: float = 0.0,
    stopped_at_cap: bool = False,
    run_failed: bool = False,
) -> str:
    """The row a lone run draws for `bookmark`, given where its clock stands.

    Like `_target_row`, it goes through `bookmark_panel`. A bookmark at or
    behind the clock is passed. A bookmark before the run's own opening is
    inherited. A bookmark still ahead takes the cap's word, the failure's
    word, or no word.
    """

    marks = BookmarkSet().with_time_bookmark(bookmark)
    standings = _standings(
        marks,
        opened_at_s=opened_at_s,
        elapsed_s=elapsed_s,
        stopped_at_cap=stopped_at_cap,
        run_failed=run_failed,
    )

    return bookmark_panel(marks, _one_run(standings)).times.rows[0]


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
    panel = _panel(BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600.0))))

    assert panel.times.rows == (format_elapsed(600.0),)


def test_a_target_names_its_compartment_and_its_height() -> None:
    row = bookmark_panel(_marks(), _one_run(_unreached(_marks()))).targets.rows[0]

    assert row.startswith("Vessel-rich 0.80 ×MAC")


def test_a_target_is_named_by_the_table_that_names_its_trace() -> None:
    # One table is used rather than a second list of compartment words, so a
    # row and the curve it is read against cannot drift apart.
    for quantity in COMPARTMENT_QUANTITIES:
        target = MacTarget(quantity, MacMultiple(0.8))

        assert _target_row(target).startswith(trace_style(quantity).label)


def test_a_target_is_rendered_by_the_renderer_the_readouts_use() -> None:
    # A target listed at `0.8 x MAC` beside a readout showing `0.80 x MAC`
    # would look like two quantities where there is one. So both go through
    # `render_mac_multiple` rather than through two spellings of one rule.
    height = MacMultiple(0.8)
    target = MacTarget(RecordedQuantity.ALVEOLAR, height)

    assert render_mac_multiple(height) == "0.80 ×MAC"
    assert render_mac_multiple(height) in _target_row(target)


def test_a_target_row_is_the_compartment_then_the_height() -> None:
    target = MacTarget(RecordedQuantity.FAT, MacMultiple(0.5))

    assert _target_row(target) == "Fat 0.50 \u00d7MAC"


def test_two_heights_on_one_compartment_are_told_apart_on_the_row() -> None:
    lower = MacTarget(RecordedQuantity.FAT, MacMultiple(0.5))
    higher = MacTarget(RecordedQuantity.FAT, MacMultiple(0.8))

    assert _target_row(lower) != _target_row(higher)


def test_marks_are_listed_oldest_first() -> None:
    # This order is deliberately the opposite of the control-change list. In
    # that record a reader looks for the newest entry. The marks are a lasting
    # set that the reader adds to and scans, and a row that moves is one they
    # have to find again.
    marks = (
        BookmarkSet()
        .with_time_bookmark(TimeBookmark(CaseInstant(120.0), "first"))
        .with_time_bookmark(TimeBookmark(CaseInstant(600.0), "second"))
    )

    rows = bookmark_panel(marks, _one_run(_unreached(marks))).times.rows

    assert rows[0].endswith("first")
    assert rows[1].endswith("second")


def test_a_mark_the_run_can_still_reach_adds_no_words_to_its_row() -> None:
    # This is conditional text rather than standing text
    # (`.claude/rules/ui-reader.md`). If every row carried words for its
    # standing, those words would be standing text, which is decoration. The
    # rows whose state a reader needs to know are the ones where something has
    # happened.
    panel = bookmark_panel(_marks(), _one_run(_unreached(_marks())))
    everything = " ".join((*panel.times.rows, *panel.targets.rows)).lower()

    for claim in ("reached", "crossed", "halted", "stopped", MARK_STILL_RUNNING_TEXT):
        assert claim not in everything


def test_a_mark_the_run_halted_on_says_so_on_its_row() -> None:
    target = MacTarget(RecordedQuantity.FAT, MacMultiple(0.5))

    assert "reached" in _target_row(target, reached=True)


def test_a_mark_on_a_failed_run_says_the_run_stopped_rather_than_saying_nothing() -> None:
    """`PL-N3N5`, checked at the row a learner reads.

    A failed run's marks used to be drawn with no words, because
    `STILL_RUNNING` renders as nothing at all on an unattributed row. So the
    one run on screen implied, by saying nothing, that the mark was still
    ahead of it, beside its own panel reading "Stopped - simulation error".
    The word must name the failure rather than the cap. The two stop a run
    for opposite reasons, and only one of them is a statement about what the
    model supports.
    """

    bookmark = TimeBookmark(CaseInstant(600.0), "check")
    target = MacTarget(RecordedQuantity.FAT, MacMultiple(0.5))
    said = MARK_STANDING_TEXT[MarkStanding.NOT_REACHED_BEFORE_FAILURE]

    assert said
    assert said in _time_row(bookmark, run_failed=True)
    assert said in _target_row(target, run_failed=True)
    assert said != MARK_STANDING_TEXT[MarkStanding.NOT_REACHED_WITHIN_CAP]


def test_every_standing_a_run_can_report_has_a_word_to_draw_it_with() -> None:
    """An enum member added without a table entry raises `KeyError` at the moment of drawing.

    `_with_standing` indexes the table, so the failure would appear in the
    panel of a running app, not in anything a reviewer reads. That is why
    this test walks the enum rather than the table.
    """

    for standing in MarkStanding:
        assert standing in MARK_STANDING_TEXT


def test_a_mark_the_clock_has_gone_past_is_worded_apart_from_one_the_run_halted_on() -> None:
    """`PL-3K9B`: two claims, so two words.

    "Passed" describes where the clock stands, and it is re-read every time
    the row is drawn. "Reached" describes what the run did. A clock taken
    backwards, by a rewind or a truncation at a mark, would revoke "Reached"
    while the mark went on being perfectly reachable.

    A bookmark is never `REACHED` on a drawn row, because
    `_time_bookmark_standing` has no such case. So the two words are compared
    on the two rows that carry them: a bookmark the clock stands on, and a
    target the run crossed.
    """

    bookmark = TimeBookmark(CaseInstant(600.0))
    target = MacTarget(RecordedQuantity.FAT, MacMultiple(0.5))

    passed = _time_row(bookmark, elapsed_s=600.0)
    reached = _target_row(target, reached=True)

    assert "passed" in passed
    assert "reached" not in passed
    assert "reached" in reached
    assert "passed" not in reached


def test_the_two_unreachable_outcomes_are_worded_apart() -> None:
    # "Not reached" alone would be true of both. It would also tell a learner
    # that a bookmark before this branch's fork might arrive if they kept
    # running. `CLAUDE.md`'s safety-critical standard rules that out: the
    # model can decide the question outright, so a row must not imply
    # otherwise.
    bookmark = TimeBookmark(CaseInstant(600.0))
    at_the_cap = _time_row(bookmark, stopped_at_cap=True)
    inherited = _time_row(bookmark, opened_at_s=900.0, elapsed_s=900.0)

    assert at_the_cap != inherited
    assert "run length" in at_the_cap
    assert "branch" in inherited


def test_the_panel_reads_the_marks_the_snapshot_carries() -> None:
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600.0), "intubation"))

    panel = bookmark_panel(
        controller.snapshot().bookmarks, _one_run(controller.snapshot().bookmark_standings)
    )

    assert panel.times.rows == (f"{format_elapsed(600.0)} – intubation",)


# ---------------------------------- one mark, two runs, and whose answer it is


def test_two_runs_that_answer_a_mark_alike_state_it_once_and_name_no_run() -> None:
    """`PL-LHBY`, `PL-4KZD`: an unattributed clause is a claim about the case.

    So it may be drawn only where it is true of every run on screen. That rule
    makes a lone run's row the degenerate case of the compared row, not a
    second path through the panel, because a lone run agrees with itself. It
    is also why a quiet row does not gain a run name for each run it is quiet
    on.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(30.0), "check"))
    passed = _standings(marks, elapsed_s=120.0)

    (row,) = bookmark_panel(marks, _two_runs(passed, passed)).times.rows

    assert MARK_STANDING_TEXT[MarkStanding.PASSED] in row
    assert run_label(FIRST_RUN) not in row
    assert run_label(SECOND_RUN) not in row


def test_two_runs_still_running_for_a_mark_add_no_words_to_its_row() -> None:
    # The same rule applies to the standing that is drawn with no words. When
    # neither compared run has reached a mark yet, there is nothing to report
    # about it. A run name on every quiet row would be the standing text that
    # `.claude/rules/ui-reader.md` rules out.
    marks = _marks()
    unreached = _unreached(marks)

    panel = bookmark_panel(marks, _two_runs(unreached, unreached))
    everything = " ".join((*panel.times.rows, *panel.targets.rows))

    assert run_label(FIRST_RUN) not in everything
    assert MARK_STILL_RUNNING_TEXT not in everything


def test_a_branch_that_halted_on_a_target_the_trunk_is_still_running_for_says_so() -> None:
    """`PL-LHBY`, the silent negative, reproduced offscreen against `4c282700`.

    The case is a MAC target on which the branch halts while the trunk is
    still running for it. When the row was drawn from the reference run, it
    said nothing at all. A branch that stopped at a mark the learner set
    therefore looked the same on screen as a Pause. The one sign that a run
    had stopped where it was asked to existed for a lone run, and vanished as
    soon as a second run was drawn.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5))
    marks = BookmarkSet().with_mac_target(target)
    trunk = _standings(marks, elapsed_s=60.0)
    branch = _standings(
        marks, opened_at_s=60.0, elapsed_s=174.7, reached_crossings=frozenset({target.crossing_key})
    )

    (row,) = bookmark_panel(marks, _two_runs(trunk, branch)).targets.rows

    # The row is pinned whole rather than checked with `in`, so the test checks
    # the row's shape and not merely its contents. The mark is stated once
    # however many runs are shown, the runs appear in drawing order, and each
    # clause names its run before its answer. Breaking any one of those would
    # attribute an answer to the wrong run while still looking plausible on
    # screen.
    assert row == (
        f"Alveolar 0.50 ×MAC"
        f"{MARK_STANDING_JOINER}{run_label(FIRST_RUN)} {MARK_STILL_RUNNING_TEXT}"
        f"{MARK_STANDING_JOINER}{run_label(SECOND_RUN)}"
        f" {MARK_STANDING_COMPARED_TEXT[MarkStanding.REACHED]}"
    )


def test_a_bookmark_the_branch_opened_after_is_not_drawn_as_the_trunk_left_it() -> None:
    """`PL-LHBY`, the false positive, and the worse half of the pair.

    An inherited instant that the branch provably cannot reach was shown as
    the trunk's `passed`. The screen therefore claimed something about the
    displayed branch that the model can determine is false. `CLAUDE.md`'s
    safety-critical standard treats that as a failure of the displayed value,
    because the correct standing under the wrong run is the wrong standing.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(30.0), "check"))
    trunk = _standings(marks, elapsed_s=60.0)
    branch = _standings(marks, opened_at_s=60.0, elapsed_s=60.0)

    (row,) = bookmark_panel(marks, _two_runs(trunk, branch)).times.rows

    assert f"{run_label(FIRST_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.PASSED]}" in row
    assert row.endswith(
        f"{run_label(SECOND_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.BEFORE_THIS_BRANCH]}"
    )


def test_the_inherited_standing_can_reach_a_drawn_row() -> None:
    """`PL-LHBY`: `BEFORE_THIS_BRANCH` had no screen it could appear on.

    The standing exists so that a learner is not told something false about a
    mark that a branch carries but cannot reach. The panel used to read the
    reference run, which is the trunk. The trunk opens at zero, and no instant
    lies before that. The word was unreachable by construction rather than by
    accident, so this test checks the word itself rather than only the row
    that carries it.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(30.0)))
    trunk = _standings(marks, elapsed_s=60.0)
    branch = _standings(marks, opened_at_s=60.0, elapsed_s=60.0)

    (row,) = bookmark_panel(marks, _two_runs(trunk, branch)).times.rows

    assert MARK_STANDING_TEXT[MarkStanding.BEFORE_THIS_BRANCH] in row


def test_every_standing_a_run_can_report_has_a_word_on_an_attributed_row() -> None:
    """Walk the compared table, which demands more than the plain table does.

    `MARK_STANDING_TEXT` may draw a standing as silence, because an
    unattributed row states one answer and silence is unambiguous there.
    Beside a named run, silence is ambiguous. A clause that rendered as a bare
    run name would leave the reader to decide whether that run had no answer
    or had not been asked. So every member needs a word here, and a new
    member added without one fails this test.
    """

    for standing in MarkStanding:
        assert MARK_STANDING_COMPARED_TEXT[standing]


def test_no_two_standings_share_a_word_on_an_attributed_row() -> None:
    """`PL-3K9B`'s wording guarantee, checked where a learner actually compares runs.

    "Passed" and "reached" are two words because they are two claims. The two
    unreachable outcomes are worded differently so that neither can be
    mistaken for the other. Both were pinned only on `MARK_STANDING_TEXT`,
    the form a lone run draws. The distinction matters most on the two-run
    row, which draws from this table instead.
    """

    said = tuple(MARK_STANDING_COMPARED_TEXT[standing] for standing in MarkStanding)

    assert len(set(said)) == len(said)


def test_the_attributed_standing_words_describe_the_mark_and_not_the_transport() -> None:
    """`MARK_ATTRIBUTION_TEMPLATE` makes the run the grammatical subject.

    So a standing that borrowed one of the transport's own words would state
    what the clock is doing, not where the mark stands. This interface
    already says what the clock is doing a few lines away, in
    `STATUS_RUNNING_TEXT` and its neighbours, on that run's own panel. The
    entry this test catches is `STILL_RUNNING`. Its attributed form read
    "still running", which contradicted the panel beside it on every paused
    run. It also claimed more than `MarkStanding.STILL_RUNNING` means. That
    standing says the run *can still reach* the mark and has not reached it
    yet, which is about the mark rather than about the clock.
    """

    transport = (STATUS_RUNNING_TEXT, STATUS_PAUSED_TEXT, STATUS_FAILED_TEXT)

    for standing in MarkStanding:
        said = MARK_STANDING_COMPARED_TEXT[standing].lower()

        for word in transport:
            assert word.lower() not in said


def test_a_panel_drawn_for_no_run_is_refused() -> None:
    # Fail obviously rather than draw a plausible-looking panel. The case's
    # marks, listed under standings that no run had supplied, would be rows
    # from which a reader could read a standing.
    with pytest.raises(ValueError, match="at least one run"):
        bookmark_panel(_marks(), ())


# ------------------------------------- the branch control and its three locks


def _offered_instants(offer: ForkOffer) -> tuple[float, ...]:
    """Where each entry in the selector would open a branch, in the order offered."""

    return tuple(point.instant_s for point in offer.points)


def _offered_labels(offer: ForkOffer) -> tuple[str, ...]:
    """What each entry in the selector says, in the order offered."""

    return tuple(point.label for point in offer.points)


#: A mark the trunk has passed, as `BranchedCase.mark_fork_points` lists it.
#: 45.35 s lies inside the step that ends at 454 x 0.1 s. The instant the
#: learner marked and the instant at which a branch taken there opens are
#: therefore two different numbers, and a test can tell which one an entry
#: carries.
_MARK_INSIDE_A_STEP = MarkForkPoint(
    TimeBookmark(CaseInstant(45.35), "the decision point"), CaseInstant(454 * 0.1)
)


def test_fork_offer_labels_every_keyframe_the_trunk_holds() -> None:
    """Each instant from `BranchedCase.fork_points_s` is one entry, labelled by `format_elapsed`.

    Induction is offered rather than filtered out. A fork at zero is a second
    way of managing the whole case. Dropping it would leave a case that has
    recorded nothing with an empty selector beside a live button. Every entry
    here is a recorded control event, taken through `fork_at`, so no entry
    carries a mark.
    """

    offer = fork_offer((0.0, 60.0, 185.0), marks=(), comparing=None, here=None)

    assert _offered_instants(offer) == (0.0, 60.0, 185.0)
    assert _offered_labels(offer) == tuple(
        format_elapsed(instant_s) for instant_s in (0.0, 60.0, 185.0)
    )
    assert all(point.mark is None for point in offer.points)
    assert offer.locked is False
    assert offer.lock_reason == ""
    assert offer.refusal is None


def test_fork_offer_requires_the_marks_to_be_stated() -> None:
    """A caller that forgets the third way to branch is refused, rather than silently offering two.

    `marks` has no default. A call site written before `PL-W4XQ`, or one that
    never asked the case for its marks, therefore fails where it is written.
    It does not draw a selector that leaves out every passed mark with
    nothing on screen to say so.
    """

    with pytest.raises(TypeError, match="marks"):
        fork_offer((CaseInstant(0.0),), comparing=None, here=None)  # type: ignore[call-arg]


def test_fork_offer_is_refused_while_a_comparison_is_shown_and_says_the_way_out() -> None:
    """The display is capped at two runs and there is no run selector yet.

    A refused control that does not say how to lift the refusal is a dead end
    rather than a mode. So the reason names the Reset that ends the
    comparison, by the run that Reset belongs to. The test below checks that
    naming.
    """

    offer = fork_offer((0.0, 60.0), marks=(), comparing=COMPARED, here=None)

    assert offer.locked is True
    assert offer.lock_reason == comparing_fork_lock_text(COMPARED)


def test_the_comparison_lock_names_a_control_the_learner_can_press() -> None:
    """`PL-WG73`: "Reset the case to end this one" named no control on screen.

    The old assertion checked only the bare word "Reset", and it passed while
    the sentence pointed at a "case" that nothing on screen is labelled with.
    A learner can act on a run's name and the word on its transport button.
    So the test checks both named controls as the pair in which the screen
    draws them.

    **Each clause is checked against the run it is about, rather than the
    whole sentence against both names.** A sentence could name both controls
    correctly but pair each with the other's outcome. That would send the
    learner to the same wrong button as the sentence this replaced, and a
    test that reads the whole string cannot tell the two apart. So the way
    out is checked on its own. It names the trunk's Reset, it does not
    mention the branch at all, and it says that the press costs the case
    starting over.

    The clause after it is about the branch's Reset, and names what that
    button does *instead*. A learner reaches for that Reset, because it
    belongs to the run they are trying to end. Pressing it discards what that
    run has simulated since its fork, and leaves the lock exactly where it
    was.
    """

    way_out, _, instead = comparing_fork_lock_text(COMPARED).partition(";")

    assert f"{run_label(FIRST_RUN)}'s {RESET_LABEL}" in way_out
    assert run_label(SECOND_RUN) not in way_out
    assert "starts the case over" in way_out

    assert f"{run_label(SECOND_RUN)}'s {RESET_LABEL}" in instead
    assert run_label(FIRST_RUN) not in instead
    assert "where it branched" in instead


def test_fork_offer_offers_no_fork_here_while_the_trunk_is_going() -> None:
    """The second control is absent rather than present and inert (`PL-TYWQ`).

    The selector is unaffected. Pausing records no keyframe, so the control
    at the paused point and the selector never exchange rows.
    """

    offer = fork_offer((0.0, 60.0), marks=(), comparing=None, here=None)

    assert offer.here_offered is False
    assert offer.here_label == ""
    assert _offered_instants(offer) == (0.0, 60.0)


def test_fork_offer_offers_the_fork_here_while_the_trunk_is_paused() -> None:
    """`PL-Y2SL`: on any pause, the control appears and names the instant it will branch at.

    It is a separate control rather than a row in the selector, because the
    two offers last for different times. An entry in the selector stays until
    the case itself changes, but this control is gone on the trunk's next
    step. It carries a label, so the reader can see the instant a press will
    branch at without inferring it from the run clock.
    """

    here = HereForkPoint(CaseInstant(45.0), stopped_on_mark=False)

    offer = fork_offer((0.0, 60.0), marks=(), comparing=None, here=here)

    assert offer.here_offered is True
    assert offer.here_label == HERE_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(45.0))
    assert format_elapsed(45.0) in offer.here_label
    # The permanent list stays exactly as it was. The paused point adds no row
    # to it and removes none, so its entries do not change while a reader
    # looks away.
    assert _offered_instants(offer) == (0.0, 60.0)
    assert _offered_labels(offer) == tuple(format_elapsed(instant_s) for instant_s in (0.0, 60.0))


def test_the_fork_here_says_a_mark_stopped_the_trunk_when_one_did() -> None:
    """A halt keeps its ratified words, and a plain pause does not borrow them.

    The instant is the one at which the trunk stands, `HereForkPoint.fork_s`.
    For a mark inside a step, that is the step's end rather than the marked
    instant. The frame is given no marked instant at all, so it cannot label
    the button with one. The frame is not told which kind of mark stopped the
    trunk either. One label serves a marked instant and a marked height
    alike, because the bookmark panel's row states which marks were crossed.
    """

    halted_s = 45.4
    halted = HereForkPoint(CaseInstant(halted_s), stopped_on_mark=True)
    paused = HereForkPoint(CaseInstant(halted_s), stopped_on_mark=False)

    on_the_mark = fork_offer((0.0,), marks=(), comparing=None, here=halted).here_label
    on_a_pause = fork_offer((0.0,), marks=(), comparing=None, here=paused).here_label

    assert on_the_mark == HALT_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(halted_s))
    assert on_a_pause == HERE_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(halted_s))
    assert format_elapsed(halted_s) in on_the_mark
    assert "mark" not in on_a_pause


def test_the_fork_here_is_refused_with_the_rest_while_a_comparison_is_shown() -> None:
    """The cap limits branches, whichever control a branch would be taken through.

    A second branch, whichever control took it, would have to replace the
    shown one while the first went on living inside `BranchedCase`. So the
    transient control is removed along with the permanent one, rather than
    staying live only to be refused when pressed.
    `.claude/rules/expert-review.md` prefers the interface that prevents the
    error to the one that reports it.
    """

    for stopped_on_mark in (False, True):
        here = HereForkPoint(CaseInstant(45.0), stopped_on_mark)

        offer = fork_offer((0.0, 60.0), marks=(), comparing=COMPARED, here=here)

        assert offer.here_offered is False
        assert offer.here_label == ""
        assert offer.locked is True


def test_a_standing_refusal_shows_only_while_the_control_is_offered() -> None:
    """A refusal describes a press of a control that is no longer on screen.

    The lock and the refusal are two lines of different severity, not one
    line with two meanings. So the question is not which one wins, but
    whether a message about a vanished control should still be shown. It
    should not.
    """

    refusal = "Setting refused: no keyframe at 30.0 s"

    assert (
        fork_offer((0.0,), marks=(), comparing=None, here=None, refusal=refusal).refusal == refusal
    )
    assert (
        fork_offer((0.0,), marks=(), comparing=COMPARED, here=None, refusal=refusal).refusal is None
    )


def test_fork_offer_lists_each_passed_mark_among_the_keyframes_by_instant() -> None:
    """`PL-W4XQ`: the marks the trunk has passed are offered beside the control events.

    Both kinds go in one list, earliest first, because both stay on offer
    until the case itself changes. A learner paused at 3 h who marks 1 h
    finds the mark where it falls on the clock, between the decision points
    on either side of it. The list is sorted here rather than trusted to
    arrive in order, so the marks are placed by instant whatever order they
    are passed in.
    """

    early = MarkForkPoint(TimeBookmark(CaseInstant(30.0)), CaseInstant(30.0))
    late = MarkForkPoint(TimeBookmark(CaseInstant(120.0), "what if"), CaseInstant(120.0))

    offer = fork_offer(
        (CaseInstant(0.0), CaseInstant(60.0), CaseInstant(185.0)),
        marks=(late, early),
        comparing=None,
        here=None,
    )

    assert _offered_instants(offer) == (0.0, 30.0, 60.0, 120.0, 185.0)
    assert _offered_labels(offer) == (
        format_elapsed(0.0),
        MARK_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(30.0)),
        format_elapsed(60.0),
        MARK_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(120.0)),
        format_elapsed(185.0),
    )


def test_a_mark_s_entry_is_labelled_with_the_instant_its_branch_opens_at() -> None:
    """A mark inside a step is reached at the step's end, and the entry names that instant.

    `BranchedCase.fork_at_mark` opens the branch at `MarkForkPoint.fork_s`, so
    that is the instant the entry must carry. A label with the typed 45.35 s
    would name a time at which the branch does not open. That is the wrong
    label on a correct value, which `CLAUDE.md`'s safety-critical standard
    counts as a failure of the value. The words are restated rather than built from the
    template, so an edit to the template cannot move both sides at once.
    """

    offer = fork_offer((CaseInstant(0.0),), marks=(_MARK_INSIDE_A_STEP,), comparing=None, here=None)
    entry = offer.points[-1]

    assert entry.label == "45.4s, on your mark"
    assert format_elapsed(45.35) not in entry.label
    assert entry.instant_s == _MARK_INSIDE_A_STEP.fork_s
    assert entry.instant_s != _MARK_INSIDE_A_STEP.bookmark.instant_s


def test_a_control_event_is_listed_before_a_mark_at_the_same_instant() -> None:
    """Two entries rather than one, and always in this order.

    A mark set on a recorded control event is a different way to branch.
    `fork_at` opens at the keyframe, and `fork_at_mark` opens at the step that
    reaches the mark, standing on its crossing. So neither entry absorbs the
    other. Their order is the order in which the two lists are given, which
    keeps one case listed the same way every time. The case's own opening is
    the boundary case. A mark there is reached by no step and opens at the
    opening keyframe, and it is listed after that keyframe.
    """

    at_opening = MarkForkPoint(TimeBookmark(CaseInstant(0.0)), CaseInstant(0.0))
    on_the_change = MarkForkPoint(TimeBookmark(CaseInstant(60.0), "the change"), CaseInstant(60.0))

    offer = fork_offer(
        (CaseInstant(0.0), CaseInstant(60.0)),
        marks=(at_opening, on_the_change),
        comparing=None,
        here=None,
    )

    assert offer.points == (
        ForkPoint(CaseInstant(0.0), format_elapsed(0.0), None),
        ForkPoint(
            CaseInstant(0.0),
            MARK_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(0.0)),
            at_opening.bookmark,
        ),
        ForkPoint(CaseInstant(60.0), format_elapsed(60.0), None),
        ForkPoint(
            CaseInstant(60.0),
            MARK_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(60.0)),
            on_the_change.bookmark,
        ),
    )


def test_each_entry_carries_the_door_it_is_taken_through() -> None:
    """A control event's entry carries no mark, and a mark's entry carries the mark itself.

    A control event is taken at its instant. A mark's entry carries the mark
    rather than an instant, because `fork_at_mark` takes the mark and finds
    the step itself. A caller that passed back an entry's float instead would
    ask for 45.4 s where the learner marked 45.35 s, and `fork_at` refuses
    that because no keyframe is there. The mark is the same object the case
    listed, name and all, so nothing between the frame and the press builds
    it again.
    """

    offer = fork_offer(
        (CaseInstant(0.0), CaseInstant(60.0)),
        marks=(_MARK_INSIDE_A_STEP,),
        comparing=None,
        here=None,
    )
    control_events = [point for point in offer.points if point.mark is None]
    marks = [point for point in offer.points if point.mark is not None]

    assert [point.instant_s for point in control_events] == [0.0, 60.0]
    assert len(marks) == 1
    assert marks[0].mark is _MARK_INSIDE_A_STEP.bookmark


def test_a_locked_offer_stays_locked_whatever_marks_the_trunk_has_passed() -> None:
    """The cap limits branches, so a passed mark opens no way around the lock.

    The lock, its reason, the control at the paused point and the refusal are
    exactly as they are with no marks at all. The marks are entries in the
    control that the lock replaces, not a further control the cap could miss.
    """

    here = HereForkPoint(CaseInstant(45.0), stopped_on_mark=True)
    refusal = "Setting refused: no keyframe at 30.0 s"
    keyframes = (CaseInstant(0.0), CaseInstant(60.0))

    unmarked = fork_offer(keyframes, marks=(), comparing=COMPARED, here=here, refusal=refusal)
    marked = fork_offer(
        keyframes, marks=(_MARK_INSIDE_A_STEP,), comparing=COMPARED, here=here, refusal=refusal
    )

    for offer in (unmarked, marked):
        assert offer.locked is True
        assert offer.lock_reason == comparing_fork_lock_text(COMPARED)
        assert offer.here_offered is False
        assert offer.here_label == ""
        assert offer.refusal is None


def test_the_agent_selector_is_shown_only_on_a_paused_lone_trunk() -> None:
    """Three conditions replace the selector with the chip, and a paused lone run meets none."""

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
    """A reader acts on the reason, so it must name a lock that the named action can lift.

    A branch's selector never returns, because `set_agent` refuses a branch.
    A comparison's selector returns on Reset, and a running run's selector
    returns on Pause. Naming the shortest lock that happens to apply would
    send a reader to Pause for something Pause cannot lift.
    """

    locked = transport(_snapshot(is_running=is_running), is_branch=is_branch, comparing=comparing)

    assert locked.selector_locked is True
    assert locked.selector_lock_reason == expected


def test_a_run_is_named_by_its_number_in_its_session() -> None:
    """The name renders the identity's number, whatever position the run is drawn at."""

    assert run_label(RunId(TEST_SESSION, 1)) == "Run 1"
    assert run_label(RunId(TEST_SESSION, 3)) == "Run 3"
    assert run_label(RunId(SessionToken("f" * 32), 3)) == "Run 3"


@pytest.mark.parametrize("position", [0, 1, True])
def test_a_run_is_not_named_from_a_drawing_position(position: object) -> None:
    """A drawing position names whichever run is drawn there, so it is refused (`PL-7Z84`)."""

    with pytest.raises(TypeError, match="a run is named from its RunId"):
        run_label(position)  # type: ignore[arg-type]
