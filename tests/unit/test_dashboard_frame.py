"""Tests of what the dashboard shows, run without a GUI toolkit.

`app/dashboard_frame.py` holds the dashboard's presentation-correctness claims:
which word names the run's state, which banner takes priority over which, what
each readout and setting says, and what the captions and the new-case question
say. Every test here runs with no display and no widget, which is the reason
that module exists.

These tests are the Flet suite's tests rewritten against the functions in
`app/dashboard_frame.py`. That suite's Qt port is now
`tests/integration/simulation_view/`. Where a claim survived the port,
its test keeps the same name. The verify lines, and the citations in
`docs/INTERFACE.md` and `docs/VERIFICATION.md`, that name those tests therefore
still point at a test that checks the same
thing (`PL-25KS`).

Snapshots come from one of two places. One is a real `SimulationController`
advanced at the shipped step size. The other is `_snapshot`, a fixture that
takes MAC and MAC-awake from the named agent's data file. A test therefore
cannot pair one agent's concentrations with another agent's divisor.

Claims about the off-scale notice, the count of undrawn marks and the time-axis
caption need the frame that the chart drew. For those, a fake controller
(`_FakeController`) is asked for its `drawn_window` and returns exactly the
samples that the fixture wrote. The test then checks how the frame treats those
samples, not where the sampler placed its columns.
"""

import inspect
import json
import math
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from importlib.resources import files
from pathlib import Path
from typing import Any

import pytest

from anesthesia_sim.app import dashboard_frame
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
    PreviewRequest,
    RunInput,
    assemble_chart_frame,
    trace_style,
)
from anesthesia_sim.app.chart_time_base import ChartTimeBase, time_base_for_span
from anesthesia_sim.app.control_record import CONTROL_INPUT_UNITS, ControlChange, ControlInput
from anesthesia_sim.app.control_timeline import ControlAdjustment, group_adjustments
from anesthesia_sim.app.controller import (
    BranchedCase,
    CompartmentAgentAmounts,
    HereForkPoint,
    MarkForkPoint,
    PreviewOfAnotherCase,
    ResumePoint,
    RunStatus,
    SettingPreview,
    SimulationController,
    SimulationSnapshot,
)
from anesthesia_sim.app.dashboard_frame import (
    ACCOUNTING_HEADING,
    ACCOUNTING_UNIT_CAPTION,
    BRANCH_AGENT_LOCK_TEXT,
    COMPARING_AGENT_LOCK_TEXT,
    COMPARTMENT_PANELS,
    CONTROL_MARK_LEGEND_LABEL,
    CONTROL_TIMELINE_CAPTION,
    CONTROL_TIMELINE_HEADING,
    DEFAULT_MAXIMUM_TARGET_MAC,
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
    OFF_SCALE_NOTICE_TEMPLATE,
    PREVIEW_OFF_SCALE_NOTICE_TEMPLATE,
    READOUT_PANELS,
    READOUT_RESERVATIONS,
    READOUT_ROW_LADDER,
    REFUSED_RESET_EXIT_TEMPLATE,
    REFUSED_RESET_WAY_OUT_TEXT,
    RENDER_INTERVAL_S,
    RESET_EXIT_TEXT,
    RESET_LABEL,
    RUNNING_AGENT_LOCK_TEXT,
    SIMULATION_TICK_INTERVAL_MS,
    STATUS_FAILED_TEXT,
    STATUS_PAUSED_TEXT,
    STATUS_RUNNING_TEXT,
    TIME_BOOKMARK_HEADING,
    USE_DISCLAIMER_TEXT,
    WIDEST_COMPARTMENT_SECONDARY,
    WIDEST_COMPARTMENT_VALUE,
    WIDEST_READOUT_SECONDARY,
    WIDEST_READOUT_VALUE,
    WITHHELD_ACCOUNTING,
    WITHHELD_DELIVERED_LINE_TEXT,
    WITHHELD_MAC_MULTIPLE_TEXT,
    BookmarkPanel,
    BranchAtStake,
    ComparedRuns,
    Emphasis,
    ForkOffer,
    ForkPoint,
    HaltDisposition,
    Notice,
    Readout,
    RunMarks,
    above_the_axis_top,
    accounting,
    bookmark_panel,
    branch_at_stake,
    case_marks,
    clock_playback_line,
    compared_panel_heading,
    compared_run_line,
    compared_run_notice,
    comparing_fork_lock_text,
    delivered_line,
    fork_offer,
    halt_disposition,
    halt_notice,
    halt_run_notice,
    height_entry_maximum_mac,
    held_window_notice,
    input_frame_wait_ms,
    kept_fork_selection,
    mac_awake_caption,
    mac_reference_caption,
    new_case_question,
    no_traces_shown,
    notice,
    off_scale_lines,
    off_scale_notice,
    offered_range,
    pinned_run_label,
    preview_label,
    readout_columns,
    readout_row_width,
    readouts,
    refused_branch_notice,
    refused_preview_notice,
    refused_reset_exit,
    refused_setting_notice,
    rejected_step_accounting,
    run_label,
    run_notice,
    run_statement,
    setting_readouts,
    slider_position,
    slider_value,
    spoken_reading,
    status_word,
    substance_heading,
    time_axis_caption,
    timeline_panel,
    transport,
    trunk_reset_question,
    unmarked_changes_lines,
    wash_in_state,
    wash_in_state_lines,
    withheld_readouts,
)
from anesthesia_sim.app.failures import FailureKind
from anesthesia_sim.app.formatting import (
    CHART_AXIS_TOP_MAC,
    CONCENTRATION_DISPLAY_DECIMALS,
    CONCENTRATION_DISPLAY_RESOLUTION_PERCENT,
    FLOW_DISPLAY_DECIMALS,
    MAC_UNIT_SUFFIX,
    ChartCeiling,
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
    playback_rate_for,
)
from anesthesia_sim.app.run_series import (
    COMPARTMENT_QUANTITIES,
    COMPARTMENT_STATE_INDEX,
    DrawnWindow,
    RecordedQuantity,
)
from anesthesia_sim.app.wash_in import WashInReading, read_wash_in
from anesthesia_sim.core import uptake_system
from anesthesia_sim.core.agent_simulation_validation import (
    AgentSimulationValidationResult,
    AgentSimulationValidator,
)
from anesthesia_sim.core.concentration import Fraction, MacMultiple, MacPercent, Percent
from anesthesia_sim.core.exceptions import (
    AgentSimulationValidationError,
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
)
from anesthesia_sim.core.governing_equations import STATE_SIZE, UNIT_STATE
from anesthesia_sim.core.mac import mac_for_patient
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
from anesthesia_sim.core.parameters import (
    AGENT_DATA_FILENAMES,
    MacAwakeReference,
    load_agent_parameters,
    load_reference_adult_parameters,
    parse_breathing_circuit_parameters,
)
from anesthesia_sim.core.rounding import WHOLE_COUNT_TOLERANCE
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
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

    elapsed_s: int
    substances: Mapping[str, Mapping[RecordedQuantity, float]]


def _sample(
    elapsed_s: int,
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

    A lone run is given no name. `SimulationView._run_name` states that
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
    reached_crossings: frozenset[tuple[RecordedQuantity, float]] = frozenset(),
    opened_at_s: int = 0,
    elapsed_s: int = 0,
    stopped_at_cap: bool = False,
    run_failed: bool = False,
) -> BookmarkStandings:
    """Return one run's standings on that set, by default for a run that has just opened."""

    return marks.standings(
        reached_crossings=reached_crossings,
        opened_at_s=CaseInstant(opened_at_s),
        elapsed_s=CaseInstant(elapsed_s),
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
    rejected_accounting: AgentSimulationValidationResult | None = None,
    failure_kind: FailureKind | None = None,
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
        history = (_sample(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id=agent_id),)

    run_mac = mac_for_patient(load_agent_parameters(agent_id), load_reference_adult_parameters())

    if agent_mac_percent is None:
        agent_mac_percent = run_mac.percent

    if agent_mac_awake is None:
        agent_mac_awake = load_agent_parameters(agent_id).mac_awake

    latest = history[-1]
    compartments = latest.substances[agent_id]

    return SimulationSnapshot(
        is_running=is_running,
        elapsed_s=CaseInstant(latest.elapsed_s),
        began_at_s=CaseInstant(0),
        opened_with=(),
        agent_id=agent_id,
        agent_display_name=agent_display_name,
        max_delivered_concentration_percent=Percent(max_delivered_concentration_percent),
        agent_mac_percent=MacPercent(agent_mac_percent),
        agent_mac_age_years=run_mac.age_years,
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
        reaching_alveolar_ventilation_l_min=AlveolarVentilation(5.5),
        delivered_agent_l=delivered_agent_l,
        agent_vapour_per_liquid=load_agent_parameters(agent_id).vapour_volume_per_liquid_volume,
        exhausted_agent_l=exhausted_agent_l,
        # No frame here draws a compartment's amount, so this helper puts the
        # whole stored total in the circuit. That keeps the record and the total
        # in agreement, as they always are in a snapshot from the controller.
        compartment_agent_amounts=CompartmentAgentAmounts(
            {
                quantity: stored_agent_l if quantity is RecordedQuantity.CIRCUIT else 0.0
                for quantity in COMPARTMENT_QUANTITIES
            }
        ),
        stored_agent_l=stored_agent_l,
        unaccounted_agent_l=1.5e-13,
        agent_accounting_passes_validation=passes_validation,
        control_timeline=control_timeline,
        bookmarks=BookmarkSet() if bookmarks is None else bookmarks,
        bookmark_halt=None,
        bookmark_standings=_unreached(BookmarkSet() if bookmarks is None else bookmarks),
        supported_limit_reason=supported_limit_reason,
        failure_reason=failure_reason,
        # A failure given without its kind is one the test injects, which the
        # simulator does not raise on purpose.
        failure_kind=(
            failure_kind
            if failure_kind is not None or failure_reason is None
            else FailureKind.UNEXPECTED
        ),
        rejected_accounting=rejected_accounting,
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
            states=tuple(_state_of(sample, substance_id) for sample in inside),
            # The fake's run is ventilated throughout, at the snapshot's rate.
            alveolar_ventilations_l_min=tuple(
                self.snapshot_value.alveolar_ventilation_l_min for _ in inside
            ),
        )


def _fake_controller(
    history: tuple[_Sample, ...] | None = None, **snapshot_fields: Any
) -> _FakeController:
    """Build a fake whose snapshot and history describe the same run."""

    snapshot = _snapshot(history=history, **snapshot_fields)

    if history is None:
        history = (_sample(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id=snapshot.agent_id),)

    return _FakeController(snapshot, history)


def _frame(
    controller: Any,
    *,
    shown: Sequence[RecordedQuantity] = COMPARTMENT_QUANTITIES,
    time_base: ChartTimeBase | None = None,
    adjustments: tuple[ControlAdjustment, ...] = (),
    held_start_s: CaseInstant | None = None,
) -> ChartFrame:
    """Return the frame one tick would draw for one run, under "Fit run" unless told otherwise."""

    return assemble_chart_frame(
        (RunInput(run_label(FIRST_RUN), controller, controller.snapshot(), adjustments),),
        time_base,
        shown,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=held_start_s,
    )


def _reading(snapshot: Any) -> WashInReading:
    """Return the F_A/F_I reading of one snapshot, worked out here from its two fractions."""

    return read_wash_in(
        snapshot.alveolar_partial_pressure_fraction, snapshot.inspired_partial_pressure_fraction
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
        held_start_s=None,
    )


def _run_history(sample_count: int, substance_id: str = _DEFAULT_AGENT) -> tuple[_Sample, ...]:
    """A run of `sample_count` samples at the real one-second simulation step."""

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
    elapsed_s: int, control: ControlInput, previous_value: float, new_value: float, adjustment: int
) -> ControlChange:
    return ControlChange(
        elapsed_s=CaseInstant(elapsed_s),
        adjustment=adjustment,
        control=control,
        previous_value=previous_value,
        new_value=new_value,
        unit=CONTROL_INPUT_UNITS[control],
    )


def _advance_to(controller: SimulationController, elapsed_s: int) -> None:
    """Step a started controller to `elapsed_s` by the one-second step."""

    while controller.snapshot().elapsed_s < elapsed_s:
        controller.advance()


def _paused_run_with_history(elapsed_s: int = 60) -> SimulationController:
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


def test_the_shipped_tick_is_the_100_ms_that_the_playback_tests_restate() -> None:
    """The run loop wakes every 100 ms of real time, as a whole number of milliseconds.

    `tests/unit/test_playback.py` and `tests/reference/test_control_resolution.py`
    restate this value as `TICK_INTERVAL_MS = 100`, because neither loads this
    module. This test checks the shipped constant against the same value, so a
    change to the constant fails here. The interval is an `int`, so that the
    simulated time a tick owes a run is a whole number of milliseconds at
    every playback rate.
    """

    assert type(SIMULATION_TICK_INTERVAL_MS) is int
    assert SIMULATION_TICK_INTERVAL_MS == 100


def test_a_tick_is_a_tenth_of_the_one_second_step() -> None:
    """At real time a run takes one step on every tenth tick.

    A tick owes a run its own length of simulated time at 1x, and a step is
    one second. So ten ticks owe exactly one step, and a press of Pause or a
    change of rate is acted on within a tenth of a second.
    """

    assert SIMULATION_STEP_S == 1
    assert 10 * SIMULATION_TICK_INTERVAL_MS == SIMULATION_STEP_S * 1_000


def test_a_frame_is_two_ticks() -> None:
    """The display redraws once for every two ticks of the run loop.

    The render interval is written as its own number, in seconds, and the
    tick in milliseconds. This test checks the relation between the two.
    """

    assert RENDER_INTERVAL_S * 1_000 == 2 * SIMULATION_TICK_INTERVAL_MS


@pytest.mark.parametrize(
    ("frame_cost_ms", "wait_ms"),
    [(0.0, 100), (40.0, 60), (40.2, 60), (50.0, 50), (104.0, 104), (103.5, 104)],
    ids=["free", "cheap", "cheap, rounded up", "half the interval", "slow", "slow, rounded up"],
)
def test_an_input_frame_waits_out_the_interval_or_its_own_cost(
    frame_cost_ms: float, wait_ms: int
) -> None:
    """The wait after a dial input's frame keeps frames 100 ms apart, or idle as long as they drew.

    Nielsen Norman Group gives 0.1 s as the limit for a user to feel that
    they are directly manipulating what is on screen, so a frame that costs
    less than half of it is followed by the rest of the 100 ms. A frame that
    costs more is followed by a pause as long as itself, so drawing never
    takes more than half of the thread (`PL-NKFD`). Each expected wait is
    worked out by hand from that rule and rounded up to a whole millisecond.
    """

    assert input_frame_wait_ms(frame_cost_ms) == wait_ms


def test_two_input_frames_start_the_interval_or_twice_the_cost_apart() -> None:
    """From one frame's start to the next is 100 ms, or twice the frame's cost, whichever is longer.

    The costs run across the 50 ms at which the two bounds meet. The
    comparison allows the rounding up to a whole millisecond and nothing
    more.
    """

    for tenths in range(0, 3001):
        cost_ms = tenths / 10
        start_to_start_ms = cost_ms + input_frame_wait_ms(cost_ms)
        expected_ms = max(100.0, 2 * cost_ms)
        # The wait is rounded up to a whole millisecond, so the start-to-start
        # time can exceed the rule's by less than 1 ms and never fall short.
        assert expected_ms <= start_to_start_ms < expected_ms + 1, cost_ms


@pytest.mark.parametrize("frame_cost_ms", [-1.0, math.nan, math.inf])
def test_an_input_frame_s_wait_refuses_a_cost_no_clock_can_measure(frame_cost_ms: float) -> None:
    """A negative, missing or infinite cost is refused rather than turned into a wait."""

    with pytest.raises(ValueError, match="frame's cost"):
        input_frame_wait_ms(frame_cost_ms)


def test_the_dashboard_displays_at_most_two_runs() -> None:
    """`ROADMAP.md` § "Completed: v0.5.0 - the case you can branch": never more than two.

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

    assert status_word(snapshot, stopped_on_mark=False).text == expected_status
    assert status_word(snapshot, stopped_on_mark=False).emphasis is expected_emphasis
    assert transport(snapshot).start_enabled is start_enabled
    assert transport(snapshot).pause_enabled is pause_enabled


def test_a_run_a_mark_stopped_is_not_worded_as_the_user_s_own_pause() -> None:
    """A paused run that a mark stopped says so, and a failure or the run length still outranks it.

    The fork control's "stopped on your mark" was the only cue that a mark had
    paused the run, and it is withdrawn while two runs are compared
    (`PL-QBQX`). So the status word carries the cue itself. The expected words
    are written here rather than read from the module, so a change to them
    fails this test.
    """

    paused = RunStatus(
        is_running=False,
        supported_limit_reason=None,
        failure_reason=None,
        failure_kind=None,
        rejected_accounting=None,
    )
    failed = replace(paused, failure_reason="TypeError: boom", failure_kind=FailureKind.UNEXPECTED)
    at_limit = replace(paused, supported_limit_reason="this run has reached 86400 s")

    on_mark = status_word(paused, stopped_on_mark=True)

    assert on_mark.text == "Paused — stopped on your mark"
    assert on_mark.emphasis is Emphasis.MUTED
    assert status_word(paused, stopped_on_mark=False).text == "Paused"
    assert status_word(failed, stopped_on_mark=True).text == "Stopped — simulation error"
    assert (
        status_word(at_limit, stopped_on_mark=True).text == "Stopped — supported run length reached"
    )
    assert status_word(at_limit, stopped_on_mark=True).emphasis is Emphasis.MUTED


def test_refresh_view_reports_a_failed_run_as_stopped_not_paused() -> None:
    snapshot = _snapshot(
        failure_reason="SimulationNumericalError: the step could not be completed",
        failure_kind=FailureKind.NUMERICAL,
    )

    assert status_word(snapshot, stopped_on_mark=False).text == "Stopped — simulation error"
    assert status_word(snapshot, stopped_on_mark=False).emphasis is Emphasis.WARNING

    banner = notice(snapshot, None)

    assert banner is not None
    # The exception's own message is written for a developer, so it goes to
    # the details under the banner and not into the banner (`PL-XWCH`).
    assert "the step could not be completed" not in banner
    assert "SimulationNumericalError" not in banner
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
        "Simulation stopped — the model produced a value it cannot hold, such as a negative "
        "amount of agent. This is a fault in the simulator, not a change in the patient. "
        "The values shown are the last completed step. Reset to start a new run."
    )


def test_refresh_view_does_not_offer_to_resume_a_failed_run() -> None:
    enablement = transport(_snapshot(failure_reason="SimulationNumericalError: boom"))

    assert enablement.start_enabled is False
    assert enablement.pause_enabled is False


def test_a_halt_no_frame_was_drawn_for_is_worded_as_one_rather_than_as_a_failed_step() -> None:
    """`halt_notice` is the banner `show_presentation` writes, with no frame on screen for it.

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
        '(docs/VERIFICATION.md, "Concentrations")'
    )
    status = RunStatus(
        is_running=False,
        supported_limit_reason=None,
        failure_reason=reason,
        failure_kind=FailureKind.CONFIGURATION,
        rejected_accounting=None,
    )

    banner = halt_notice(status)

    assert banner is not None
    assert banner.startswith(
        "Simulation stopped — one part of the simulator gave another "
        "a value that it does not accept. "
        "This is a fault in the simulator, not a change in the patient. "
    )
    assert reason not in banner
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


def test_an_undrawn_halt_after_the_run_started_over_says_its_readouts_are_withheld() -> None:
    """After a Reset or an agent change, the last frame drawn belongs to the discarded run.

    `RunView.show_presentation` then withholds the readouts. So the banner must not
    say that they show the last frame drawn, as it did until the adversarial
    review of `PL-J5GC`. The supported run length keeps its wording, because a
    run that has just started over has not reached it.
    """

    failed = RunStatus(
        is_running=False,
        supported_limit_reason=None,
        failure_reason="RuntimeError: boom",
        failure_kind=FailureKind.UNEXPECTED,
        rejected_accounting=None,
    )

    banner = halt_notice(failed, started_over=True)

    assert banner == (
        "Simulation stopped — an unexpected error occurred in the simulator, and its cause "
        "is not known. This is a fault in the simulator, not a change in the patient. "
        "No frame has been drawn since the run "
        "started over: the readouts and the charts are withheld, and the run itself stands "
        "at its last completed step. Reset to start a new run."
    )
    assert halt_notice(failed) != banner

    at_limit = RunStatus(
        is_running=False,
        supported_limit_reason="supported run length",
        failure_reason=None,
        failure_kind=None,
        rejected_accounting=None,
    )

    assert halt_notice(at_limit, started_over=True) == halt_notice(at_limit)


def test_a_halt_is_stated_from_the_run_status_alone() -> None:
    """A `RunStatus`, which carries no compartment value, decides the three halt widgets.

    `show_presentation` reads `SimulationController.record()` rather than a
    snapshot, because the snapshot's own `Fraction`s are among the values
    that can cause a halt (`PL-7DJK`). So `status_word`, `transport` and
    `halt_notice` each accept a bare status. A record and a snapshot are each
    a status, so every caller that draws a frame stays unchanged.
    """

    limit = "this run has reached 86400 s of simulated time"
    failed = RunStatus(
        is_running=False,
        supported_limit_reason=None,
        failure_reason="TypeError: boom",
        failure_kind=FailureKind.UNEXPECTED,
        rejected_accounting=None,
    )
    at_limit = RunStatus(
        is_running=False,
        supported_limit_reason=limit,
        failure_reason=None,
        failure_kind=None,
        rejected_accounting=None,
    )
    paused = RunStatus(
        is_running=False,
        supported_limit_reason=None,
        failure_reason=None,
        failure_kind=None,
        rejected_accounting=None,
    )
    running = RunStatus(
        is_running=True,
        supported_limit_reason=None,
        failure_reason=None,
        failure_kind=None,
        rejected_accounting=None,
    )

    assert isinstance(_snapshot(), RunStatus)
    assert status_word(failed, stopped_on_mark=False).text == "Stopped — simulation error"
    assert (
        status_word(at_limit, stopped_on_mark=False).text
        == "Stopped — supported run length reached"
    )
    assert status_word(paused, stopped_on_mark=False).text == "Paused"
    assert status_word(running, stopped_on_mark=False).text == "Running"
    assert (transport(failed).start_enabled, transport(failed).pause_enabled) == (False, False)
    assert (transport(at_limit).start_enabled, transport(at_limit).pause_enabled) == (False, False)
    assert (transport(running).start_enabled, transport(running).pause_enabled) == (False, True)
    assert halt_notice(failed) is not None
    assert "an unexpected error occurred" in (halt_notice(failed) or "")
    assert "TypeError: boom" not in (halt_notice(failed) or "")
    # Nothing is wrong with the state in which a run stops at the supported
    # run length. The next frame therefore draws, and one wording serves both.
    assert halt_notice(at_limit) == notice(at_limit, None)
    assert halt_notice(paused) is None
    assert halt_notice(running) is None


def test_a_run_is_stated_alike_from_its_record_and_from_the_snapshot_it_extends() -> None:
    """A run is stated the same way whether a frame drew it or only the controller's record exists.

    `RunView.show_presentation` is the only writer of the run-state widgets.
    Its statement is built from the snapshot a frame drew from, and from
    `SimulationController.record()` where no frame can draw (`PL-X7D5`). The
    statement reads only what the two share. A halt therefore states every
    widget that a frame would, using the same functions the frame uses.
    """

    controller = _paused_run_with_history()
    record = controller.record()
    adjustments = group_adjustments(record.control_timeline)

    from_snapshot, from_record = (
        run_statement(
            stated,
            adjustments,
            is_branch=False,
            comparing=False,
            banner=None,
            stopped_on_mark=False,
        )
        for stated in (controller.snapshot(), record)
    )

    assert from_snapshot == from_record
    assert from_record.agent_id == "sevoflurane"
    assert from_record.agent_name == "Sevoflurane"
    assert from_record.subtitle == format_subtitle("Sevoflurane")
    assert from_record.substance_heading == "Modelled concentrations: Sevoflurane"
    assert from_record.status == status_word(record, stopped_on_mark=False)
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
        record,
        adjustments,
        is_branch=True,
        comparing=True,
        banner="the banner the caller worded",
        stopped_on_mark=True,
    )

    assert statement.transport == transport(record, is_branch=True, comparing=True)
    assert statement.transport.selector_lock_reason == BRANCH_AGENT_LOCK_TEXT
    assert statement.timeline == timeline_panel(adjustments)
    assert statement.banner == "the banner the caller worded"
    assert statement.status.text == "Paused — stopped on your mark"


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
    refusal = RunStatus(
        is_running=False,
        supported_limit_reason=None,
        failure_reason=this_refusal,
        failure_kind=FailureKind.CONFIGURATION,
        rejected_accounting=None,
    )
    earlier = RunStatus(
        is_running=False,
        supported_limit_reason=None,
        failure_reason="SimulationNumericalError: boom",
        failure_kind=FailureKind.NUMERICAL,
        rejected_accounting=None,
    )
    running = RunStatus(
        is_running=True,
        supported_limit_reason=None,
        failure_reason=None,
        failure_kind=None,
        rejected_accounting=None,
    )

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
    assert after_failure == (
        f"Reset was refused — one part of the simulator gave another "
        f"a value that it does not accept. {way_out}"
    )
    assert this_refusal not in after_failure

    drawn = notice(refusal, None, refused_reset=first)
    undrawn = halt_notice(refusal, refused_reset=first)
    kept = notice(earlier, None, refused_reset=after_failure)

    assert drawn is not None and drawn.endswith(first)
    assert drawn.startswith(
        "Simulation stopped — one part of the simulator gave another "
        "a value that it does not accept. This is a fault "
        "in the simulator, not a change in the patient. The values shown are"
    )
    assert "perfused at" not in drawn
    assert undrawn is not None and undrawn.endswith(first)
    assert "No frame of the stopped run could be drawn" in undrawn
    assert kept is not None and kept.endswith(after_failure)
    assert kept.startswith(
        "Simulation stopped — the model produced a value it cannot hold, such as a negative "
        "amount of agent. This is a fault in the simulator, not a change in the patient. "
        ""
    )
    for banner in (drawn, undrawn, kept):
        assert RESET_EXIT_TEXT not in banner
    # Reset is the way out whenever it was not what was refused.
    assert (notice(refusal, None) or "").endswith(RESET_EXIT_TEXT)
    assert (halt_notice(refusal) or "").endswith(RESET_EXIT_TEXT)
    # And a run that is not stopped has no banner for an exit to end.
    assert notice(running, None, refused_reset=first) is None
    assert halt_notice(running, refused_reset=first) is None


def test_a_setting_refused_on_a_stopped_run_is_stated_with_that_run_s_way_out() -> None:
    """A stopped run states a refused dial in place of its exit, followed by its own way out.

    A stopped run refuses every dial (`PL-3B34`), and a stopped run outranks a
    refused setting, so the refusal is stated inside the stopped run's banner.
    The supported run length sends the reader to a branch at an earlier
    instant or to Reset, but names the branch only while one can be taken. A
    failure keeps Reset as its way out, even where a branch could be taken.
    After a refused Reset, closing the application is the only way out, so the
    refusal follows that exit. A running run's refusal is unchanged. The
    expected sentences are literals rather than the module's constants.
    """

    refused = "Setting refused — the cardiac output setting cannot be changed on a stopped run"
    failed = RunStatus(
        is_running=False,
        supported_limit_reason=None,
        failure_reason="SimulationNumericalError: boom",
        failure_kind=FailureKind.NUMERICAL,
        rejected_accounting=None,
    )
    at_limit = RunStatus(
        is_running=False,
        supported_limit_reason="reached 86400 s of simulated time",
        failure_reason=None,
        failure_kind=None,
        rejected_accounting=None,
    )
    running = RunStatus(
        is_running=True,
        supported_limit_reason=None,
        failure_reason=None,
        failure_kind=None,
        rejected_accounting=None,
    )
    refused_reset = (
        "Reset was refused for this reason. No setting can repair this, because only a fault "
        "in the simulator causes it. Close and reopen the application to start a new run."
    )
    reset_keeps = "Reset to start a new run, which keeps every setting."
    branch_or_reset = (
        "To try a different setting, branch at an earlier instant, where each dial starts at "
        "what it was set to then, or Reset to start a new run, which keeps every setting."
    )

    assert notice(failed, refused) == (
        "Simulation stopped — the model produced a value it cannot hold, such as a negative "
        "amount of agent. This is a fault in the simulator, not a change in the patient. "
        f"The values shown are the last completed step. {refused}. {reset_keeps}"
    )
    assert notice(failed, refused, branch_offered=True) == notice(failed, refused)
    assert halt_notice(failed, refused) == (
        "Simulation stopped — the model produced a value it cannot hold, such as a negative "
        "amount of agent. This is a fault in the simulator, not a change in the patient. "
        "No frame of the stopped run "
        "could be drawn: the readouts and every chart that still has a plot show the last "
        "frame drawn before it stopped. The run itself stands at its last completed step. "
        f"{refused}. {reset_keeps}"
    )
    assert notice(failed, refused, refused_reset=refused_reset) == (
        "Simulation stopped — the model produced a value it cannot hold, such as a negative "
        "amount of agent. This is a fault in the simulator, not a change in the patient. "
        "The values shown are the last "
        f"completed step. {refused_reset} {refused}."
    )
    limit_banner = notice(at_limit, refused, branch_offered=True)
    assert limit_banner is not None
    assert limit_banner.endswith(f"inside the supported span. {refused}. {branch_or_reset}")
    assert halt_notice(at_limit, refused, branch_offered=True) == limit_banner
    # While no branch can be taken, the run at the supported run length names Reset alone.
    no_branch = notice(at_limit, refused)
    assert no_branch is not None
    assert no_branch.endswith(f"inside the supported span. {refused}. {reset_keeps}")
    assert halt_notice(at_limit, refused, branch_offered=False) == no_branch
    assert halt_notice(at_limit, refused) == no_branch
    reset_refused_at_limit = notice(at_limit, refused, refused_reset=refused_reset)
    assert reset_refused_at_limit is not None
    assert reset_refused_at_limit.endswith(f"inside the supported span. {refused_reset} {refused}.")
    assert halt_notice(at_limit, refused, refused_reset=refused_reset) == reset_refused_at_limit
    assert (notice(at_limit, None) or "").endswith(
        "inside the supported span. Reset to start a new run."
    )
    assert notice(running, refused) == (
        f"{refused}. The simulation is unchanged and still running its previous setting."
    )


def test_refresh_view_shows_no_notice_for_an_ordinary_run() -> None:
    for is_running in (True, False):
        snapshot = _snapshot(is_running=is_running)

        assert notice(snapshot, None) is None
        assert status_word(snapshot, stopped_on_mark=False).text in {"Running", "Paused"}


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

    assert (
        status_word(snapshot, stopped_on_mark=False).text
        == "Stopped — supported run length reached"
    )
    assert status_word(snapshot, stopped_on_mark=False).emphasis is not Emphasis.WARNING

    banner = notice(snapshot, None)

    assert banner is not None
    assert f"supported run length of {format_supported_run_length()}" in banner


#: 24 hours less 1 h 40 min, in seconds, worked out by hand: 86,400 - 6,000. The banner
#: opens 20 s of real time before the stop at 300x, which is 6,000 s of simulated time
#: (WCAG 2.2 SC 2.2.1's 20 s at the fastest playback rate).
_FIRST_SECOND_OF_THE_APPROACH_S = 80_400


def test_the_interface_says_the_run_is_approaching_its_supported_length() -> None:
    """A run 1 h 40 min from the 24-hour stop says so, before it gets there (`PL-H2K2`).

    Before this change the run advanced with no word until the step at 24
    hours was refused. The halt then arrived with no warning and could read
    as a fault. The banner is drawn muted, because nothing is wrong with the
    run. Each expected string was worked out by hand from the times above.
    """

    def banner_at(elapsed_s: int) -> Notice | None:
        snapshot = replace(_snapshot(is_running=True), elapsed_s=CaseInstant(elapsed_s))
        return run_notice(snapshot, None, elapsed_s=snapshot.elapsed_s)

    assert banner_at(_FIRST_SECOND_OF_THE_APPROACH_S - 1) is None
    assert banner_at(_FIRST_SECOND_OF_THE_APPROACH_S) == Notice(
        "This run stops in 1h40m of simulated time, at the supported run length of 24 hours.",
        Emphasis.MUTED,
    )
    assert banner_at(86_399) == Notice(
        "This run stops in 1s of simulated time, at the supported run length of 24 hours.",
        Emphasis.MUTED,
    )


def test_a_stop_or_a_refusal_outranks_the_approaching_limit_banner() -> None:
    """A stopped run or a refused setting describes the run now, so it leads the banner.

    The refused setting is drawn as a warning, because the reader's setting was
    not applied. The stop at the limit is drawn muted, as its status word is.
    """

    approaching = replace(_snapshot(is_running=True), elapsed_s=CaseInstant(86_000))
    refused = run_notice(approaching, "Setting refused — too high", elapsed_s=approaching.elapsed_s)
    at_limit = replace(
        _snapshot(supported_limit_reason="reached 86400 s"), elapsed_s=CaseInstant(86_400)
    )
    stopped = run_notice(at_limit, None, elapsed_s=at_limit.elapsed_s)
    failed = replace(
        approaching,
        failure_reason="RuntimeError: boom",
        failure_kind=FailureKind.UNEXPECTED,
        is_running=False,
    )

    assert refused is not None
    assert refused.text.startswith("Setting refused — too high.")
    assert refused.emphasis is Emphasis.WARNING
    assert stopped is not None
    assert stopped.text.startswith("Simulation stopped — this run reached the supported run")
    assert stopped.emphasis is Emphasis.MUTED
    assert run_notice(failed, None, elapsed_s=failed.elapsed_s) == Notice(
        notice(failed, None), Emphasis.WARNING
    )


def test_a_refusal_made_before_the_warning_does_not_hide_the_countdown() -> None:
    """A refused setting stays on screen until a setting is accepted, so it can hold the banner.

    A refusal made at hour 10 is still shown at hour 23. The countdown then
    follows it in the same banner, or the stop would arrive unannounced. The
    expected remaining time is worked out by hand: 86 400 s less 80 400 s is
    6 000 s, which the clock writes as 1h40m.
    """

    approaching = replace(_snapshot(is_running=True), elapsed_s=CaseInstant(80_400))

    banner = run_notice(approaching, "Setting refused — too high", elapsed_s=approaching.elapsed_s)

    assert banner == Notice(
        "Setting refused — too high. The simulation is unchanged and still running its "
        "previous setting. This run stops in 1h40m of simulated time, at the supported "
        "run length of 24 hours.",
        Emphasis.WARNING,
    )


def test_a_countdown_keeps_one_topic_while_its_time_left_changes() -> None:
    """A screen reader is told a banner when its topic changes, so a countdown is read once.

    The countdown's text changes every second, and its topic does not, with or
    without a refusal in front of it (`PL-J7Z5`). A refusal joining the
    countdown is a new topic, because the banner now asks the reader to act. A
    banner with no countdown has no topic of its own, so its text is its topic.
    """

    def banner_at(elapsed_s: int, refused: str | None = None) -> Notice:
        snapshot = replace(_snapshot(is_running=True), elapsed_s=CaseInstant(elapsed_s))
        banner = run_notice(snapshot, refused, elapsed_s=snapshot.elapsed_s)
        assert banner is not None
        return banner

    approach = (_FIRST_SECOND_OF_THE_APPROACH_S, 86_000, 86_399)
    countdown = [banner_at(elapsed_s) for elapsed_s in approach]
    refused = [banner_at(elapsed_s, "Setting refused — too high") for elapsed_s in approach]
    before_the_countdown = banner_at(1_000, "Setting refused — too high")

    assert len({banner.text for banner in countdown}) == 3
    assert len({banner.topic for banner in countdown}) == 1
    assert len({banner.text for banner in refused}) == 3
    assert len({banner.topic for banner in refused}) == 1
    assert countdown[0].topic is not None
    assert refused[0].topic not in {None, countdown[0].topic}
    assert before_the_countdown.topic is None


def test_a_halt_banner_takes_the_emphasis_of_what_stopped_the_run() -> None:
    """With no frame drawn, a failure is a warning and the run-length stop is not (`PL-0889`)."""

    at_limit = _snapshot(supported_limit_reason="reached 86400 s")
    failed = _snapshot(failure_reason="RuntimeError: boom")

    assert halt_run_notice(at_limit) == Notice(halt_notice(at_limit), Emphasis.MUTED)
    assert halt_run_notice(failed) == Notice(halt_notice(failed), Emphasis.WARNING)
    assert halt_run_notice(_snapshot()) is None


def test_a_refused_reset_on_a_run_stopped_at_the_limit_is_drawn_as_a_warning() -> None:
    """A Reset that was refused is a request not carried out, so its banner is a warning too."""

    at_limit = replace(
        _snapshot(supported_limit_reason="reached 86400 s"), elapsed_s=CaseInstant(86_400)
    )
    refused_reset = "Reset was refused: no run can be built."

    drawn = run_notice(at_limit, None, elapsed_s=at_limit.elapsed_s, refused_reset=refused_reset)
    halted = halt_run_notice(at_limit, refused_reset=refused_reset)

    assert drawn == Notice(notice(at_limit, None, refused_reset=refused_reset), Emphasis.WARNING)
    assert halted == Notice(halt_notice(at_limit, refused_reset=refused_reset), Emphasis.WARNING)


def test_a_refusal_on_a_run_stopped_at_the_limit_is_drawn_as_a_warning() -> None:
    """The stop is muted, but a banner that says a setting was refused is a warning.

    A dial moved on a run stopped at the supported run length is refused, and
    the stop's banner then states the refusal. What the reader asked for was
    not done, so the banner takes the alert colour, drawn frame or not.
    """

    at_limit = replace(
        _snapshot(supported_limit_reason="reached 86400 s"), elapsed_s=CaseInstant(86_400)
    )
    refused = "Setting refused — the run has stopped"

    drawn = run_notice(at_limit, refused, elapsed_s=at_limit.elapsed_s)
    halted = halt_run_notice(at_limit, refused)

    assert drawn == Notice(notice(at_limit, refused), Emphasis.WARNING)
    assert halted == Notice(halt_notice(at_limit, refused), Emphasis.WARNING)


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
        "This model leaves out metabolism, and its fat flow is uncertain. How far the "
        "slow part of the trace can stray from a patient grows as a run goes on, so the "
        "model is not claimed to represent a patient past this span. The values shown "
        "are the last completed step, inside the supported span. Reset to start a new run."
    )


def test_the_supported_limit_notice_says_why_the_model_is_not_claimed_past_the_span() -> None:
    """The notice's reason for stopping the run is true for every agent, not only sevoflurane.

    The banner used to say that past the supported span, the omitted metabolism
    and the fat perfusion "dominate the trace". That is wrong pharmacology for
    desflurane and isoflurane, which are barely metabolized. It also
    contradicts `core/supported_ranges.py`, which says that nothing breaks at
    hour 25 and that the error grows progressively. The phrase "fat perfusion"
    could also be taken to describe the patient's physiology, when the
    recorded limitation is the model's stored fat flow (`PL-KHXB`).

    The banner may not say instead that the model is "not validated" past the
    span. A reader would take that to mean it is validated inside it, which
    `docs/VERIFICATION.md` § "Published wash-in and elimination validation test"
    does not claim. Nor may it call the fat flow wrong: the two human sources
    that `docs/MODEL.md` § "Known limitations" weighs disagree about which way it errs. What
    is true for every agent is that both limitations are present from the
    start and their cost grows with the run.
    """

    banner = notice(
        _snapshot(
            is_running=False,
            supported_limit_reason="this run has reached 86400 s of simulated time",
        ),
        None,
    )

    assert banner is not None
    assert "leaves out metabolism" in banner
    assert "fat flow is uncertain" in banner
    assert "grows as a run goes on" in banner
    assert "not claimed to represent a patient past this span" in banner
    assert "dominate" not in banner
    assert "perfusion" not in banner
    assert "validated" not in banner


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
        failure_kind=FailureKind.NUMERICAL,
        supported_limit_reason="this run has reached 86400 s of simulated time",
    )
    banner = notice(snapshot, None)

    assert status_word(snapshot, stopped_on_mark=False).text == "Stopped — simulation error"
    assert banner is not None
    assert "the model produced a value it cannot hold" in banner
    assert "supported run length" not in banner


def test_a_refused_branch_is_not_worded_as_a_refused_setting() -> None:
    """A branch the case refused changed no setting, so its notice does not say so (`PL-3JTH`)."""

    refused = refused_branch_notice(SimulationConfigurationError("the reason the case gave"))

    assert refused == "Branch not opened — the reason the case gave"


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
    """A stopped run describes everything on screen, and a refusal describes one control.

    So the banner opens with the stopped run. Since `PL-3B34` the refusal is
    stated inside that banner, in place of its exit. It is never given the
    wording of a refusal on a run that is still going.
    """

    refused = refused_setting_notice(SimulationConfigurationError("a value the core refused"))
    failed = _snapshot(
        failure_reason="SimulationNumericalError: boom", failure_kind=FailureKind.NUMERICAL
    )
    at_limit = _snapshot(supported_limit_reason="this run has reached 86400 s of simulated time")

    failure_banner = notice(failed, refused)
    limit_banner = notice(at_limit, refused)

    assert failure_banner is not None
    assert failure_banner.startswith(
        "Simulation stopped — the model produced a value it cannot hold, such as a negative "
        "amount of agent. "
    )
    assert limit_banner is not None
    assert limit_banner.startswith(
        "Simulation stopped — this run reached the supported run length of "
    )
    for banner in (failure_banner, limit_banner):
        assert "Setting refused — a value the core refused. " in banner
        assert "still running its previous setting" not in banner


def test_a_refused_preview_outranks_a_refused_setting_and_says_the_release_still_applies() -> None:
    """A refused preview is about the dial held now, and its banner says what the release does.

    The release of that dial applies the held value, so the banner must not
    say, as a refused setting's banner does, that the run keeps its previous
    setting (`PL-412F`). A setting refused before the drag returns to the
    banner once the drag ends. A stopped run outranks both, and its banner
    says nothing of the preview.
    """

    preview = refused_preview_notice(PreviewOfAnotherCase("the reason the preview gave"))
    setting = refused_setting_notice(SimulationConfigurationError("a value the core refused"))
    running = _snapshot(is_running=True)
    at_limit = _snapshot(supported_limit_reason="this run has reached 86400 s of simulated time")

    assert preview == (
        "Preview not drawn — the reason the preview gave. "
        "Releasing the dial still applies the new setting."
    )
    assert notice(running, setting, refused_preview=preview) == preview
    assert run_notice(running, setting, elapsed_s=0, refused_preview=preview) == Notice(
        preview, Emphasis.WARNING
    )
    assert notice(running, setting) == (
        "Setting refused — a value the core refused. "
        "The simulation is unchanged and still running its previous setting."
    )
    limit_banner = notice(at_limit, None, refused_preview=preview)
    assert limit_banner is not None
    assert limit_banner.startswith(
        "Simulation stopped — this run reached the supported run length of "
    )
    assert "Preview not drawn" not in limit_banner


def test_a_preview_of_another_case_puts_the_dial_and_the_remedy_in_the_banner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The controller's refusal of a preview reaches the banner in the user's words (`PL-412F`).

    A preview rebuilds the run and reads the patient file again. A patient
    file edited after the run began therefore gives the preview another
    patient, and the controller refuses it. The banner names the dial, the
    possible causes and what to do, and says that the release still applies
    the new setting. The values that differ go to the refusal's note, for the
    failure log. The banner's text is typed by hand.
    """

    controller = SimulationController()
    on_file = load_reference_adult_parameters()
    edited = replace(on_file, muscle_volume_l=CompartmentVolume(on_file.muscle_volume_l + 1.0))
    monkeypatch.setattr(uptake_system, "load_reference_adult_parameters", lambda: edited)

    with pytest.raises(PreviewOfAnotherCase) as refusal:
        controller.preview_settings(SettingPreview(ControlInput.FRESH_GAS_FLOW, 6.0))

    assert refused_preview_notice(refusal.value) == (
        "Preview not drawn — the fresh gas flow preview would not start from the values "
        "this run holds, so it would predict a different case. The simulator's data may "
        "have changed since this run began, or the simulator may have a fault. Reopen the "
        "simulator and run the case again to preview a setting. If this notice comes back, "
        "the cause is a fault in the simulator. Releasing the dial still applies the new "
        "setting."
    )
    (note,) = refusal.value.__notes__
    assert note.startswith(
        "a preview would be drawn from values this run does not hold, so it would predict a "
        "different case: muscle volume_l is "
    )


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
    stopped exactly where `docs/INTERFACE.md` § "What happens when a run reaches the limit"
    says it must. Only a test would notice.
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
        history=(_sample(12, 0.02345, 0.01234, 0.00456, 0.00789, 0.00321, 0.00012),)
    )
    by_name = _readouts_by_name(snapshot)
    settings = _settings_by_control(snapshot)

    assert by_name["Simulated time"][1] == "12s"
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
    _advance_to(controller, 120)

    assert controller.snapshot().fat_partial_pressure_fraction > 0.0
    assert _readouts_by_name(controller.snapshot())["Fat"][1] == "<0.01%"
    # At the same instant, the alveolar reading is an ordinary value at the
    # documented resolution. The marker therefore appears only for a value
    # that is genuinely below the resolution, and is not a formatting quirk.
    # The run opens at sevoflurane's 1.80% (Mapleson 1996's MAC at age 40).
    assert _readouts_by_name(controller.snapshot())["Alveolar"][1] == "0.55%"

    _advance_to(controller, 1_200)

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

    `docs/INTERFACE.md` § "Minimum displayed outputs" requires "alveolar or
    end-tidal-equivalent concentration". Dead space, airway sampling delay,
    shunt and V/Q mismatch are all listed in `docs/MODEL.md` § "Known
    limitations". The value
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

    # Each fraction is a round multiple of sevoflurane's 1.80% MAC at age 40.
    snapshot = _snapshot(history=(_sample(60, 0.018, 0.0144, 0.0072, 0.0054, 0.0009, 5e-5),))
    by_name = _readouts_by_name(snapshot)

    assert sum(1 for _, _, secondary in by_name.values() if "MAC" in secondary) == 6
    assert by_name["Circuit"][2] == "1.00 ×MAC"
    assert by_name["Alveolar"][2] == "0.80 ×MAC"
    assert by_name["Mixed venous"][2] == "0.40 ×MAC"
    assert by_name["Vessel-rich group"][2] == "0.30 ×MAC"
    assert by_name["Muscle"][2] == "0.05 ×MAC"
    assert by_name["Fat"][2] == "<0.01 ×MAC"


def test_each_mac_readout_uses_its_own_agent_divisor() -> None:
    """6.6% is 3.67 MAC of sevoflurane and 1 MAC of desflurane, both at age 40.

    A divisor left over from a previously selected agent would produce a
    plausible number under the correct label, which is the presentation
    failure `CLAUDE.md` treats as a safety failure rather than a cosmetic
    one. Every MAC line is read from the snapshot's own divisor.
    """

    sevoflurane = _snapshot(history=(_sample(60, 0.066, 0.066, 0.066, 0.066, 0.066, 0.066),))

    # 6.6 / 1.8 = 3.667
    assert _readouts_by_name(sevoflurane)["Alveolar"][2] == "3.67 ×MAC"

    desflurane = _snapshot(
        agent_id="desflurane",
        agent_display_name="Desflurane",
        max_delivered_concentration_percent=18.0,
        history=(_sample(60, 0.066, 0.066, 0.066, 0.066, 0.066, 0.066, substance_id="desflurane"),),
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


def test_the_clock_line_names_a_delivered_rate_beside_the_set_one() -> None:
    """While the computer falls behind, the clock line keeps the set rate and adds the delivered.

    The expected line is worked out by hand: 80% of 300x is 240x (`PL-2NYN`).
    """

    assert clock_playback_line(playback_rate_for(300), 0.8) == "about 240\u00d7 of 300\u00d7"
    assert clock_playback_line(playback_rate_for(300)) == "300\u00d7 real time"


@pytest.mark.parametrize("rate", SUPPORTED_PLAYBACK_RATES)
def test_a_withheld_row_keeps_the_clock_s_playback_line(rate: PlaybackRate) -> None:
    """The withheld row and the live row word the clock's second line alike (`PL-J791`)."""

    withheld = withheld_readouts(rate)

    assert withheld[0].secondary == format_playback_rate(rate.multiplier)
    assert [readout.secondary for readout in withheld[1:]] == [WITHHELD_MAC_MULTIPLE_TEXT] * 6


def test_only_the_first_panel_is_the_clock_and_the_rest_name_their_compartments() -> None:
    """`ReadoutPanel` alone says which panel is the clock (`PL-J791`)."""

    assert [panel.is_clock for panel in READOUT_PANELS] == [True, *[False] * 6]
    assert [panel.compartment() for panel in COMPARTMENT_PANELS] == [
        RecordedQuantity.CIRCUIT,
        RecordedQuantity.ALVEOLAR,
        RecordedQuantity.MIXED_VENOUS,
        RecordedQuantity.VESSEL_RICH,
        RecordedQuantity.MUSCLE,
        RecordedQuantity.FAT,
    ]
    with pytest.raises(
        ValueError,
        match=re.escape("the 'Simulated time' panel is the clock and shows no compartment"),
    ):
        READOUT_PANELS[0].compartment()


def test_no_module_under_app_asks_which_panel_is_the_clock_for_itself() -> None:
    """Six places once asked `panel.quantity is None`, and a missed one fails nothing (`PL-J791`).

    Only `ReadoutPanel` reads its own field to answer it.
    """

    app = Path(dashboard_frame.__file__).parent
    owner = inspect.getsource(dashboard_frame.ReadoutPanel)
    asking = []
    for path in sorted(app.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        if path.name == "dashboard_frame.py":
            text = text.replace(owner, "")
        # regex: one comparison in either polarity, searched for through source text.
        if re.search(r"quantity is (not )?None", text):
            asking.append(path.name)

    assert asking == []


def test_the_clock_panel_reads_in_the_chart_axis_form_past_an_hour() -> None:
    """`PL-Q4M4`: the clock and the axis state the same quantity in the same form."""

    clock = readouts(
        _snapshot(history=(_sample(5400, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),)), DEFAULT_PLAYBACK_RATE
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

    The clock one second before the supported run length gives the widest
    value line, because every component of the compound form is present. The
    widest second line is a delivered rate (`PL-2NYN`). At 1% of 1x it is
    0.010x, which keeps a trailing zero as its second significant figure, so
    the line has 18 characters. "about 3.0x of 300x" ties with it, and the
    slowest rate is counted first. A rate below 1% names the bound, as
    "below 0.010x of 1x", and no fraction gives a longer line. Each line is
    longer than every plain label, whose longest is "300x real time".
    """

    assert WIDEST_READOUT_VALUE == format_elapsed(MAXIMUM_ELAPSED_SIMULATION_TIME_S - 1)
    assert len(WIDEST_READOUT_VALUE) >= len(format_percent(Fraction(1.0)))
    assert WIDEST_READOUT_SECONDARY == "about 0.010\u00d7 of 1\u00d7"
    assert all(
        len(clock_playback_line(rate, fraction)) <= len(WIDEST_READOUT_SECONDARY)
        for rate in SUPPORTED_PLAYBACK_RATES
        for fraction in (1e-12, 1e-6, 0.0033, 0.0099)
    )
    assert len(WIDEST_READOUT_SECONDARY) > max(
        len(format_playback_rate(rate.multiplier)) for rate in SUPPORTED_PLAYBACK_RATES
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
        'L/min, the range the run accepts (docs/INTERFACE.md, "Supported input ranges")'
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
            "those steps (docs/INTERFACE.md, \"The model's envelope and a machine's deliverable "
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
            "those steps (docs/INTERFACE.md, \"The model's envelope and a machine's deliverable "
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
            'on one of those steps (docs/INTERFACE.md, "Supported input ranges")',
        ),
        (
            ControlInput.CARDIAC_OUTPUT,
            {"cardiac_output_l_min": CardiacOutput(5.25)},
            "Cardiac output is 5.25 L/min, which the slider cannot show: it offers "
            "0.1 L/min steps from 0.0 to 10.0 L/min, so a patient profile must open the run "
            'on one of those steps (docs/INTERFACE.md, "Supported input ranges")',
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

    assert _settings_by_control(snapshot)[ControlInput.DELIVERED].name == "Desflurane vaporizer"


def test_the_slider_tracks_the_dial_maximum_and_the_chart_no_longer_does() -> None:
    """Two ceilings that used to be the same one, and had to become separate (`PL-CC23`).

    The delivered dial tracks the real vaporizer cap. The chart's ceiling is
    the same MAC multiple for every agent. For desflurane the ceiling, 3 x
    6.6% = 19.8%, sits a little above the 18% dial. For isoflurane it sits
    well below the 5% dial, at 3 x 1.17% = 3.51%. The MACs are Mapleson
    1996's at age 40.
    """

    desflurane = _fake_controller(
        agent_id="desflurane",
        agent_display_name="Desflurane",
        max_delivered_concentration_percent=18.0,
    )

    assert _settings_by_control(desflurane.snapshot())[ControlInput.DELIVERED].maximum == 18.0
    assert _frame(desflurane).axis_top_percent == pytest.approx(19.8)
    assert _frame(desflurane).axis_top_percent == pytest.approx(CHART_AXIS_TOP_MAC * 6.6)

    isoflurane = _fake_controller(
        agent_id="isoflurane",
        agent_display_name="Isoflurane",
        max_delivered_concentration_percent=5.0,
    )

    assert _settings_by_control(isoflurane.snapshot())[ControlInput.DELIVERED].maximum == 5.0
    assert _frame(isoflurane).axis_top_percent == pytest.approx(3.51), (
        "1.17% MAC x 3, not the 5% dial"
    )


def test_the_dial_is_readable_in_the_unit_its_compartments_are() -> None:
    """The dial, the one control a reader sets, is shown in the units of the traces it fills."""

    delivered = _settings_by_control(_snapshot())[ControlInput.DELIVERED]

    assert delivered.value_text == format_percent(Fraction(0.025))
    assert delivered.secondary == format_mac_multiple(Fraction(0.025), MacPercent(1.8))
    assert delivered.secondary == "1.39 ×MAC"


def test_the_delivered_line_prints_the_dial_in_both_units() -> None:
    """The readout heading repeats the dial in the dial's own two units (`PL-NWTM`).

    2.5% sevoflurane over its 1.80% MAC at age 40 is 1.389 ×MAC, worked here
    by hand rather than read back from the readout under test.
    """

    delivered = _settings_by_control(_snapshot())[ControlInput.DELIVERED]

    assert delivered_line(delivered) == "Vaporizer 2.50% (1.39 ×MAC)"


def test_the_delivered_line_is_labelled_as_the_vaporizer_setting() -> None:
    """The line says it is the vaporizer's setting, never a bare "Delivered" (`PL-M4WT`).

    Labelled "Delivered 2.50%", a user could take it for a modelled
    concentration or, at low fresh gas flow, for the inspired one. The
    withheld line keeps the same label.
    """

    delivered = _settings_by_control(_snapshot())[ControlInput.DELIVERED]

    assert delivered_line(delivered).startswith("Vaporizer ")
    assert WITHHELD_DELIVERED_LINE_TEXT.startswith("Vaporizer ")


def test_the_delivered_line_refuses_a_flow_readout() -> None:
    """A flow has no MAC line, and printing it as the dial would show a flow as a concentration."""

    flow = _settings_by_control(_snapshot())[ControlInput.FRESH_GAS_FLOW]

    with pytest.raises(ValueError, match="not from fresh_gas_flow's"):
        delivered_line(flow)


def test_the_end_to_end_mac_path_reaches_the_panel_from_a_real_run() -> None:
    """Patient inputs, model selection, calculation, units, formatting, display."""

    controller = SimulationController(agent_id="desflurane")
    controller.start()

    for _ in range(60 // SIMULATION_STEP_S):
        controller.advance()

    snapshot = controller.snapshot()

    # Mapleson 1996 (PMID 8777094), Abstract: desflurane's MAC at age 40 is 6.6%.
    assert snapshot.agent_mac_percent == 6.6
    assert snapshot.agent_mac_age_years == 40
    assert _readouts_by_name(snapshot)["Alveolar"][2] == format_mac_multiple(
        snapshot.alveolar_partial_pressure_fraction, MacPercent(6.6)
    )
    # The dial starts at the agent's own 1 MAC, so after a minute of wash-in
    # the alveolar compartment is above zero and below that 1 MAC.
    alveolar_mac = snapshot.alveolar_partial_pressure_fraction * 100.0 / 6.6
    assert 0.0 < alveolar_mac < 1.0
    assert _settings_by_control(snapshot)[ControlInput.DELIVERED].secondary == "1.00 ×MAC"


@pytest.mark.parametrize(
    ("agent_id", "fraction_text", "mac_multiple_text"),
    [
        ("sevoflurane", "0.88%", "0.49 ×MAC"),
        ("isoflurane", "0.41%", "0.35 ×MAC"),
        ("desflurane", "3.94%", "0.60 ×MAC"),
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

    The percents were read again on 2026-11-22, when the dial's opening 1 MAC
    moved from De Wolf et al.'s 2.0%, 1.2% and 6.0% to Mapleson 1996's 1.80%,
    1.17% and 6.6% at age 40 (`PL-LBVN`). The model is linear in the dial
    setting, so each MAC multiple stayed where it was, and each percent moved
    by the ratio of the two MACs: 0.98% x 0.90, 0.42% x 0.975 and 3.59% x
    1.10, to the display's rounding.
    """

    controller = SimulationController(agent_id=agent_id)
    controller.start()

    for _ in range(300):
        controller.advance()

    snapshot = controller.snapshot()
    _, value, secondary = _readouts_by_name(snapshot)["Alveolar"]

    assert snapshot.elapsed_s == 300
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
    """Amounts show one decimal of a litre (`PL-TG60`), and the residual shows a power of ten."""

    panel = accounting(_snapshot(passes_validation=True))

    assert panel.status.text == "Valid"
    assert panel.status.emphasis is Emphasis.ACCENT
    assert "still accounts for all delivered agent" in panel.detail
    assert panel.amounts == (
        "Delivered: <0.1 L\nExhausted: <0.1 L\nStored: <0.1 L\nUnaccounted: <10⁻¹² L"
    )


def test_the_accounting_panel_prints_the_residual_once() -> None:
    """The residual is one line, "Unaccounted", for a negative residual too (`PL-XFWG`).

    The panel prints a residual only as the power of ten it lies below, without its
    sign. An absolute-error line would then repeat the unaccounted line word for
    word, so the panel prints the residual once (project owner, 2026-10-03,
    ratified). -5.601e-14 L lies below 10⁻¹³, worked out by hand, and is negative
    so that a line printing its magnitude would read the same as one printing it.
    """

    panel = accounting(replace(_snapshot(), unaccounted_agent_l=-5.601e-14))
    lines = panel.amounts.splitlines()

    assert [line.split(": ")[0] for line in lines] == [
        "Delivered",
        "Exhausted",
        "Stored",
        "Unaccounted",
    ]
    assert [line for line in lines if line.endswith("<10⁻¹³ L")] == ["Unaccounted: <10⁻¹³ L"]


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


def test_the_accounting_panel_reports_the_failure_after_an_accounting_halt() -> None:
    """After a step fails its accounting check, the panel shows that step's verdict and totals.

    The core rolls the failed step back. So the snapshot's own accounting is the
    restored step's, which passed, and the panel used to read "Valid" under a
    banner saying the accounting had failed. That banner quoted the rejected
    step's totals beside the panel's different restored ones (`PL-HF4B`). The
    snapshot now carries the rejected step's check, and the panel shows it. The
    expected amounts are worked out by hand from the transfers below: 4.24 L
    delivered, 2.53 L exhausted and 1.1 L stored leave 0.61 L unaccounted.
    """

    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=4.24, exhausted_agent_l=2.53)

    with pytest.raises(AgentSimulationValidationError) as raised:
        validator.require_valid_agent_accounting(currently_stored_agent_l=1.1)

    rejected = raised.value.check
    assert rejected is not None
    halted = _snapshot(
        passes_validation=True,
        delivered_agent_l=3.991974,
        exhausted_agent_l=2.06,
        stored_agent_l=1.9319,
        failure_reason=f"AgentSimulationValidationError: {raised.value}",
        failure_kind=FailureKind.ACCOUNTING,
        rejected_accounting=rejected,
    )

    panel = accounting(halted)

    assert panel.status.text == "Validation failed"
    assert panel.status.emphasis is Emphasis.WARNING
    assert "rolled back" in panel.detail
    assert panel.amounts.splitlines()[:3] == [
        "Delivered: 4.2 L",
        "Exhausted: 2.5 L",
        "Stored: 1.1 L",
    ]
    assert accounting(replace(halted, rejected_accounting=None)).status.text == "Valid", (
        "the restored step passed its check, so only the rejected check can fail the panel"
    )

    banner = notice(halted, None)

    assert banner is not None
    assert "the agent accounting check failed" in banner
    assert "e+00" not in banner, "the totals are for the log, and the panel shows them"
    assert "except the agent accounting panel, which shows the rejected step" in banner


def test_the_panel_after_an_accounting_halt_shows_the_rejected_step_s_residuals_in_litres() -> None:
    """The unaccounted and absolute-error lines show the rejected step's residual in litres.

    The check also records a relative error, which is a ratio and has no unit. In the
    test above, the residual and the relative error lie between the same two powers of
    ten. So a panel that showed the ratio on either line would still pass that test.
    Here they lie between different powers of ten. The expected lines are worked out by
    hand. 40.0 L delivered, 20.0 L exhausted and 14.0 L stored leave 6.0 L unaccounted,
    which is less than 1e+01 L. The relative error is 6.0 / 40.0 = 0.15, which is less
    than 1e+00 (test-strength review of `PL-J5GC`).
    """

    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=40.0, exhausted_agent_l=20.0)

    with pytest.raises(AgentSimulationValidationError) as raised:
        validator.require_valid_agent_accounting(currently_stored_agent_l=14.0)

    rejected = raised.value.check
    assert rejected is not None

    assert rejected_step_accounting(rejected).amounts.splitlines()[3:] == ["Unaccounted: <10¹ L"]


def test_the_accounting_panel_refuses_names_and_amounts_that_differ_in_number(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A missing amount line raises, rather than leaving the last name off the panel."""

    validator = AgentSimulationValidator()
    validator.record_external_agent_transfer(delivered_agent_l=40.0, exhausted_agent_l=20.0)
    check = validator.check_agent_accounting(currently_stored_agent_l=14.0)
    monkeypatch.setattr(
        "anesthesia_sim.app.dashboard_frame.ACCOUNTING_AMOUNT_NAMES",
        ("Delivered", "Exhausted", "Stored"),
    )

    with pytest.raises(ValueError, match=r"^zip\(\) argument 2 is longer than argument 1$"):
        rejected_step_accounting(check)


def test_the_withheld_accounting_panel_states_no_verdict_and_no_amount() -> None:
    """After the run starts over, the panel shows no verdict and no amount until a frame is drawn.

    `RunView.show_presentation` shows this panel on a halt when no frame has been drawn
    since a Reset or an agent change. The integration tests compare the panel with
    this same constant, so only this test states the text that the panel must show.
    A verdict or an amount here would describe the discarded run (blind and
    adversarial reviews of `PL-J5GC`).
    """

    assert WITHHELD_ACCOUNTING.status.text == "—"
    assert WITHHELD_ACCOUNTING.status.emphasis is Emphasis.MUTED
    assert WITHHELD_ACCOUNTING.detail == "No frame has been drawn since the run started over."
    assert WITHHELD_ACCOUNTING.amounts.splitlines() == [
        "Delivered: —",
        "Exhausted: —",
        "Stored: —",
        "Unaccounted: —",
    ]


def test_the_accounting_unit_caption_names_litres_of_agent_gas_and_its_condition() -> None:
    """Litres of agent *gas* is not the unit anyone consumes agent in (`PL-TG60`).

    A volume of gas also needs its temperature and pressure (`PL-HQPF`).
    """

    assert ACCOUNTING_UNIT_CAPTION == (
        "Litres of equivalent pure agent gas,\nat 20 °C and 1 atm.\n"
        "Amounts in the body read high,\nas they are gas at body temperature."
    )


# --- the control-change panel ----------------------------------------------------


def test_the_list_states_what_was_changed_and_to_what() -> None:
    adjustments = group_adjustments(
        (_control_change(12, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),)
    )

    assert timeline_panel(adjustments).entries == "12s · Fresh gas flow 4.0 L/min -> 2.0 L/min"


def test_the_list_reads_most_recent_first() -> None:
    """A fixed panel has to show the change the reader has just made."""

    adjustments = group_adjustments(
        (
            _control_change(10, ControlInput.FRESH_GAS_FLOW, 4.0, 2.0, adjustment=1),
            _control_change(20, ControlInput.CARDIAC_OUTPUT, 5.0, 3.0, adjustment=2),
        )
    )
    lines = timeline_panel(adjustments).entries.splitlines()

    assert lines[0].startswith("20s")
    assert lines[1].startswith("10s")


def test_a_run_with_no_changes_says_so_rather_than_showing_an_empty_panel() -> None:
    panel = timeline_panel(())

    assert panel.entries == NO_CONTROL_CHANGES_TEXT
    assert panel.entries == "No settings changed yet in this run."
    assert panel.summary == ""


def test_changes_the_panel_cannot_list_are_counted_rather_than_dropped() -> None:
    """A list that quietly stops asserts that nothing earlier happened."""

    adjustments = group_adjustments(
        tuple(
            _control_change(
                index, ControlInput.FRESH_GAS_FLOW, 4.0, 4.0 - index * 0.1, adjustment=index + 1
            )
            for index in range(MAX_LISTED_ADJUSTMENTS + 3)
        )
    )
    panel = timeline_panel(adjustments)

    assert len(panel.entries.splitlines()) == MAX_LISTED_ADJUSTMENTS == 12
    assert panel.summary == "15 change(s); 3 earlier change(s) not listed"


def test_changes_the_chart_cannot_mark_are_counted_rather_than_dropped() -> None:
    """The plot follows the panel's rule: changes it cannot mark are counted, not dropped.

    A chart that stops marking changes without saying so implies that no more
    changes happened. The count appears on the chart whose window it covers,
    not in the run's control-change panel, because each chart has its own
    window (`PL-L59K`).
    """

    timeline = tuple(
        _control_change(
            index, ControlInput.FRESH_GAS_FLOW, 4.0, 4.0 - index * 0.01, adjustment=index + 1
        )
        for index in range(MAX_CHART_CONTROL_MARKS + 2)
    )
    adjustments = group_adjustments(timeline)
    frame = _frame(
        _fake_controller(history=_run_history(60), control_timeline=timeline),
        adjustments=adjustments,
    )

    assert frame.runs[0].undrawn_control_marks == 2
    assert unmarked_changes_lines(frame) == ("2 control change(s) in this window not marked",)
    assert "not marked" not in timeline_panel(adjustments).summary


def test_each_run_s_unmarked_changes_line_is_named_while_runs_are_compared() -> None:
    """The count is in a chart the runs share, so it names the run it counts for (`PL-25DD`)."""

    timeline = tuple(
        _control_change(
            index, ControlInput.FRESH_GAS_FLOW, 4.0, 4.0 - index * 0.01, adjustment=index + 1
        )
        for index in range(MAX_CHART_CONTROL_MARKS + 2)
    )
    adjustments = group_adjustments(timeline)
    busy = _fake_controller(history=_run_history(60), control_timeline=timeline)
    quiet = _fake_controller(history=_run_history(60))
    frame = assemble_chart_frame(
        (
            RunInput(run_label(FIRST_RUN), busy, busy.snapshot(), adjustments),
            RunInput(run_label(SECOND_RUN), quiet, quiet.snapshot(), ()),
        ),
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
    )

    assert unmarked_changes_lines(frame) == (
        "Run 1 — 2 control change(s) in this window not marked",
        None,
    )


def test_a_chart_whose_window_marks_every_change_says_nothing_about_marks() -> None:
    frame = _frame(_fake_controller(history=_run_history(60)))

    assert frame.runs[0].undrawn_control_marks == 0
    assert unmarked_changes_lines(frame) == (None,)


def test_the_summary_counts_every_change_and_the_earlier_ones_not_listed() -> None:
    adjustments = group_adjustments(
        tuple(
            _control_change(index, ControlInput.CARDIAC_OUTPUT, 5.0, 4.0, adjustment=index + 1)
            for index in range(MAX_LISTED_ADJUSTMENTS + 1)
        )
    )

    assert timeline_panel(adjustments).summary == "13 change(s); 1 earlier change(s) not listed"


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

    controller = _fake_controller(history=_run_history(1_200))
    caption = time_axis_caption(_frame(controller, time_base=time_base_for_span(7_200.0)))

    assert caption == "2 hours shown"
    assert "simulated seconds" not in caption


def test_the_caption_says_when_the_span_was_chosen_by_the_run_rather_than_the_reader() -> None:
    """Under "Fit run" the width is derived, and nothing else on screen says so."""

    controller = _fake_controller(history=_run_history(1_200))
    fitted = _frame(controller)

    assert "whole run so far" in time_axis_caption(fitted)
    assert f"{format_time_base(fitted.time_base.span_s)} shown" in time_axis_caption(fitted)
    assert time_axis_caption(fitted) == "whole run so far, 30 minutes shown"

    chosen = _frame(controller, time_base=time_base_for_span(43_200.0))

    assert "whole run so far" not in time_axis_caption(chosen)


def test_a_held_window_says_it_is_not_following_and_where_the_run_is_now() -> None:
    """`PL-Z7LY`: a held window shows the past while the readouts show the present.

    The axis title says the window is held, and the line above the plot
    names the window's edges as the axis labels them and the run's instant
    as the clock states it. At 50 minutes a fifteen-minute window held at
    30 minutes shows 30 to 45 minutes.
    """

    controller = _fake_controller(history=_run_history(3_001))
    held = _frame(controller, time_base=time_base_for_span(900.0), held_start_s=CaseInstant(1800))

    assert held.held
    assert time_axis_caption(held) == "15 minutes shown, held: not following the run"
    assert held_window_notice(held) == "Showing 30m to 45m. The run is now at 50m."

    following = _frame(controller, time_base=time_base_for_span(900.0))

    assert not following.held
    assert time_axis_caption(following) == "15 minutes shown"
    assert held_window_notice(following) is None


def test_a_hold_that_reaches_the_run_s_own_window_follows_the_run() -> None:
    """At 50 minutes the following fifteen-minute window starts at 35m18s, so 36m is not held."""

    controller = _fake_controller(history=_run_history(3_001))
    frame = _frame(controller, time_base=time_base_for_span(900.0), held_start_s=CaseInstant(2160))

    assert not frame.held
    assert held_window_notice(frame) is None
    assert frame.start_s == pytest.approx(3_000 + 900 * 0.02 - 900)


def test_fit_run_cannot_be_held() -> None:
    controller = _fake_controller(history=_run_history(3_001))

    with pytest.raises(ValueError, match=re.escape('needs a chosen width, not "Fit run"')):
        _frame(controller, held_start_s=CaseInstant(1800))


def test_the_display_names_the_mac_the_readouts_were_divided_by() -> None:
    """The divisor is the one free parameter, so the display carries it, per agent."""

    assert mac_reference_caption(_frame(_fake_controller())) == format_mac_reference(
        "Sevoflurane", MacPercent(1.8), age_years=40
    )
    assert mac_reference_caption(_frame(_fake_controller())) == "1 MAC sevoflurane (age 40) = 1.8%"

    desflurane = _fake_controller(
        agent_id="desflurane",
        agent_display_name="Desflurane",
        max_delivered_concentration_percent=18.0,
    )

    assert mac_reference_caption(_frame(desflurane)) == "1 MAC desflurane (age 40) = 6.6%"


@pytest.mark.parametrize("agent_id", AGENT_DATA_FILENAMES)
def test_the_band_states_the_fraction_and_the_divisor_it_was_drawn_from(agent_id: str) -> None:
    """Both of the band's free parameters are named, from the running agent's own file."""

    frame = _frame(SimulationController(agent_id=agent_id))
    agent = load_agent_parameters(agent_id)

    assert mac_awake_caption(frame) == format_mac_awake_reference(
        agent.display_name,
        fraction_of_mac=agent.mac_awake.fraction_of_mac,
        standard_deviation_fraction_of_mac=agent.mac_awake.standard_deviation_fraction_of_mac,
        mac_percent=agent.mac_at_age_40_percent,
    )


def test_the_wash_in_trace_draws_nothing_before_agent_reaches_the_circuit() -> None:
    """0/0 is not a point, and an empty circuit is where every run starts."""

    state = wash_in_state(_reading(_snapshot(history=_run_history(1))), 0)

    assert state == "Not defined: the inspired concentration is too low to divide by."


def test_the_wash_in_caption_names_no_cause_once_a_washout_empties_the_circuit() -> None:
    """After the vaporizer is closed, the caption says only that F_I is too low to divide by.

    The run takes 8% sevoflurane at 10 L/min for 30 s. Then the vaporizer is
    closed and ventilation stopped, so the fresh gas washes the circuit out
    while the patient keeps agent in the alveoli. By 300 s the inspired
    concentration is below 0.01%, the smallest that the ratio is divided by,
    and the alveolar concentration is above it. The caption used to say here
    that no agent had reached the circuit, which this run shows to be false
    (`PL-P3ZL`). The limit and the sentence are written out from
    `docs/INTERFACE.md` § "A point is drawn only inside two boundaries".
    """

    controller = SimulationController()
    controller.set_fresh_gas_flow(FreshGasFlow(10.0))
    controller.set_delivered_concentration_percent(Percent(8.0))
    controller.start()
    _advance_to(controller, 30)
    controller.pause()
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))
    controller.set_delivered_concentration_percent(Percent(0.0))
    controller.start()
    _advance_to(controller, 300)
    snapshot = controller.snapshot()

    # The premises: the circuit is below the limit, and the patient still holds agent.
    assert snapshot.inspired_partial_pressure_fraction < 0.0001
    assert snapshot.alveolar_partial_pressure_fraction > 0.0001
    assert wash_in_state_lines(_frame(controller)) == (
        "Not defined: the inspired concentration is too low to divide by.",
    )


def test_the_wash_in_trace_stops_when_alveolar_exceeds_inspired() -> None:
    """Elimination is not wash-in, and the plot says so rather than drawing it."""

    history = (*_run_history(20), _sample(20, 0.010, 0.030, 0.02, 0.02, 0.01, 0.01))
    state = wash_in_state(_reading(_snapshot(history=history)), 0)

    assert state == ("Alveolar exceeds inspired, so the ratio is not a wash-in fraction.")


def test_a_ratio_above_one_with_ventilation_stopped_names_no_elimination() -> None:
    """With ventilation stopped, the caption claims no agent leaving the patient.

    A run takes up sevoflurane at 4%, then alveolar ventilation is set to zero
    and the vaporizer to 0.5%. No agent then moves between the lungs and the
    circuit, so the alveolar fraction stays high while fresh gas brings the
    inspired fraction down to 0.5%, and the ratio passes 1. The patient is
    eliminating nothing (`PL-7PBB`). The caption names the zero ventilation,
    which rule 3 of `app/wash_in.py` applies before the ratio's own boundary
    (`PL-49D5`).
    """

    controller = SimulationController(agent_id="sevoflurane")
    controller.set_delivered_concentration_percent(Percent(4.0))
    controller.start()
    _advance_to(controller, 600)
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))
    controller.set_delivered_concentration_percent(Percent(0.5))
    _advance_to(controller, 900)

    snapshot = controller.snapshot()

    # The premises: the circuit is above the limit, and alveolar exceeds it.
    assert snapshot.inspired_partial_pressure_fraction >= 1e-4
    assert snapshot.alveolar_partial_pressure_fraction > snapshot.inspired_partial_pressure_fraction
    assert _reading(snapshot).plotted_ratio is None
    assert wash_in_state_lines(_frame(controller)) == (
        "Alveolar ventilation was zero over the last simulated second, so the ratio is not a "
        "wash-in fraction.",
    )


def _drawn_wash_in_seconds(frame: ChartFrame) -> list[float]:
    """Return every second at which the frame's one run draws a wash-in point."""

    return [time_s for stretch in frame.runs[0].wash_in for time_s in stretch.times_s]


@pytest.mark.parametrize(
    "dial_while_stopped_percent", [0.5, None], ids=["dial-lowered", "dial-unchanged"]
)
def test_no_wash_in_point_is_drawn_while_alveolar_ventilation_is_zero(
    dial_while_stopped_percent: float | None,
) -> None:
    """The plot draws nothing for the seconds a step at zero ventilation reached (`PL-49D5`).

    A run takes up sevoflurane at 4% for ten minutes. Alveolar ventilation is
    set to zero at 600 s and back to 5 L/min at 900 s. With the dial lowered
    to 0.5%, fresh gas washes the circuit out and the ratio climbs past 1.
    With the dial left at 4%, blood takes agent from the alveoli and the ratio
    falls. Before the fix, both stretches were drawn as wash-in. The expected
    seconds come from the settings this test made, not from the plot. The
    state at 600 s was reached with ventilation running, so the trace ends
    there. The state at 900 s was reached at zero ventilation, so the trace
    starts again after it.
    """

    controller = SimulationController(agent_id="sevoflurane")
    controller.set_delivered_concentration_percent(Percent(4.0))
    controller.start()
    _advance_to(controller, 600)
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))

    if dial_while_stopped_percent is not None:
        controller.set_delivered_concentration_percent(Percent(dial_while_stopped_percent))

    _advance_to(controller, 900)
    stopped_frame = _frame(controller)

    assert wash_in_state_lines(stopped_frame) == (
        "Alveolar ventilation was zero over the last simulated second, so the ratio is not a "
        "wash-in fraction.",
    )

    drawn_s = _drawn_wash_in_seconds(stopped_frame)

    assert max(drawn_s) == 600
    assert not [time_s for time_s in drawn_s if 600 < time_s <= 900]

    if dial_while_stopped_percent is None:
        controller.set_alveolar_ventilation(AlveolarVentilation(5.0))
        _advance_to(controller, 1200)
        resumed_frame = _frame(controller)
        resumed_s = _drawn_wash_in_seconds(resumed_frame)

        assert not [time_s for time_s in resumed_s if 600 < time_s <= 900]
        assert max(resumed_s) == 1200
        assert wash_in_state_lines(resumed_frame)[0].startswith(
            "Now: F<sub>A</sub>/F<sub>I</sub> = "
        )


def test_the_caption_reads_the_ventilation_that_reached_the_state_not_the_one_just_set() -> None:
    """Setting ventilation to zero changes the caption at the next step, as it changes the trace.

    The state the run stands on was reached with ventilation running, so its
    ratio is still a wash-in fraction and the trace's last point is drawn. The
    caption agrees with that point until a step at zero ventilation is taken.
    """

    controller = SimulationController(agent_id="sevoflurane")
    controller.set_delivered_concentration_percent(Percent(4.0))
    controller.start()
    _advance_to(controller, 600)
    controller.pause()
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))
    paused_frame = _frame(controller)

    assert wash_in_state_lines(paused_frame)[0].startswith("Now: F<sub>A</sub>/F<sub>I</sub> = ")
    assert max(_drawn_wash_in_seconds(paused_frame)) == 600

    controller.start()
    _advance_to(controller, 601)

    assert wash_in_state_lines(_frame(controller)) == (
        "Alveolar ventilation was zero over the last simulated second, so the ratio is not a "
        "wash-in fraction.",
    )


def test_restoring_ventilation_on_a_paused_run_keeps_the_caption_true_of_the_state_shown() -> None:
    """A paused run standing on an apnoeic state keeps its caption until a step is taken.

    The caption speaks of the state the run stands on, which was reached at
    zero ventilation, so it stays true while the control already shows
    ventilation restored (blind review of `PL-49D5`, pass 1). One step later
    the state was reached with ventilation running, and its ratio is drawn.
    """

    stopped_caption = (
        "Alveolar ventilation was zero over the last simulated second, so the ratio is not a "
        "wash-in fraction.",
    )
    controller = SimulationController(agent_id="sevoflurane")
    controller.set_delivered_concentration_percent(Percent(4.0))
    controller.start()
    _advance_to(controller, 600)
    controller.set_alveolar_ventilation(AlveolarVentilation(0.0))
    _advance_to(controller, 700)
    controller.pause()
    controller.set_alveolar_ventilation(AlveolarVentilation(5.0))
    paused_frame = _frame(controller)

    assert wash_in_state_lines(paused_frame) == stopped_caption
    assert max(_drawn_wash_in_seconds(paused_frame)) == 600

    controller.start()
    _advance_to(controller, 701)
    stepped_frame = _frame(controller)

    assert wash_in_state_lines(stepped_frame)[0].startswith("Now: F<sub>A</sub>/F<sub>I</sub> = ")
    assert max(_drawn_wash_in_seconds(stepped_frame)) == 701


def test_the_wash_in_reading_is_the_value_the_trace_ends_at() -> None:
    """The sentence beside the plot and the plot cannot disagree."""

    controller = _fake_controller(history=_run_history(40))
    drawn_ratio = _frame(controller).runs[0].wash_in[-1].ratios[-1]
    state = wash_in_state(_reading(controller.snapshot()), 0)

    assert format_wash_in_ratio(drawn_ratio) in state
    assert state == f"Now: F<sub>A</sub>/F<sub>I</sub> = {format_wash_in_ratio(drawn_ratio)}"


def test_the_wash_in_state_counts_the_stretches_the_plot_could_not_draw() -> None:
    """A pool that overflowed is displayed rather than silent."""

    state = wash_in_state(_reading(_snapshot(history=_run_history(40))), 3)

    assert state.endswith(" (3 earlier stretch(es) not drawn)")
    assert not wash_in_state(_reading(_snapshot(history=_run_history(40))), 0).endswith(
        "not drawn)"
    )


def test_a_wash_in_state_with_undrawn_stretches_keeps_its_reading_before_the_count() -> None:
    """The count of undrawn stretches is added after the state, never in place of it.

    Each of the three states is checked against a literal. A state with no
    ratio can follow earlier stretches, as it does after a washout, so its
    sentence names no cause that a count of earlier stretches would
    contradict (`PL-P3ZL`).
    """

    in_domain = read_wash_in(0.0071, 0.01)
    eliminating = read_wash_in(0.02, 0.01)
    no_ratio = read_wash_in(0.002, 0.00005)

    assert wash_in_state(in_domain, 2) == (
        "Now: F<sub>A</sub>/F<sub>I</sub> = 0.71 (2 earlier stretch(es) not drawn)"
    )
    assert wash_in_state(eliminating, 2) == (
        "Alveolar exceeds inspired, so the ratio is not a wash-in fraction. "
        "(2 earlier stretch(es) not drawn)"
    )
    assert wash_in_state(no_ratio, 2) == (
        "Not defined: the inspired concentration is too low to divide by. "
        "(2 earlier stretch(es) not drawn)"
    )


def test_a_trace_above_the_fixed_axis_is_reported_rather_than_left_to_look_flat() -> None:
    """The failure mode that PL-CC23's fixed ceiling introduces, and the guard against it.

    A clipped trace is drawn as a horizontal line at the top of the plot, and
    a horizontal line looks like a plateau. The plot therefore says that the
    trace is clipped, rather than relying on the reader to notice.
    """

    # 8% circuit is 4.44 MAC of sevoflurane, against a 5.4% (3 MAC) ceiling.
    # Alveolar at 5% stays below the ceiling. That makes this a test of
    # *which* compartments are named, not only of whether any is named.
    history = (
        _sample(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1, 0.08, 0.05, 0.01, 0.01, 0.0, 0.0),
    )
    text = off_scale_notice(_frame(_fake_controller(history=history)), 0)

    assert text is not None
    assert "Circuit" in text
    assert "Alveolar" not in text
    # The notice must say where the unclipped number is. Otherwise it reports
    # a problem and leaves the reader without the value.
    assert "readouts above" in text
    # The top is named in percent and in MAC, the two units the axes are
    # labelled in (`PL-DVDY`): 3 x 1.8% is 5.40%, worked by hand.
    assert "5.40% (3.00 ×MAC)" in text
    assert text == (
        "Above the top of the plot: Circuit. The axis stops at 5.40% (3.00 ×MAC) and these "
        "traces are cut off there — their values are in the readouts above, which are "
        "not clipped."
    )


def test_a_trace_above_the_standard_top_is_inside_the_high_top_and_above_the_low_one() -> None:
    """The notice reads the top the chart draws at, not the standard one (`PL-K1VH`).

    8% circuit is 4.44 MAC of sevoflurane (1.8% at age 40): above the 3 MAC
    top, inside the 4.5 MAC top. Alveolar at 3% is 1.67 MAC, inside the
    standard top and above the 1.5 MAC top, 2.7%. Each figure is worked by
    hand.
    """

    history = (
        _sample(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1, 0.08, 0.03, 0.01, 0.01, 0.0, 0.0),
    )
    frame = _frame(_fake_controller(history=history))
    low = off_scale_notice(replace(frame, ceiling=ChartCeiling.LOW), 0)

    assert off_scale_notice(replace(frame, ceiling=ChartCeiling.HIGH), 0) is None
    assert low is not None
    assert low.startswith(
        "Above the top of the plot: Circuit, Alveolar. The axis stops at 2.70% (1.50 ×MAC)"
    )
    assert "Alveolar" not in (off_scale_notice(frame, 0) or "")


def test_the_off_scale_notice_stays_silent_for_a_run_inside_the_axis() -> None:
    """An advisory that fires on an ordinary run is one nobody reads."""

    history = (
        _sample(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1, 0.02, 0.018, 0.015, 0.014, 0.01, 0.005),
    )

    assert off_scale_notice(_frame(_fake_controller(history=history)), 0) is None


def test_a_trace_exactly_at_the_ceiling_is_not_reported_off_scale() -> None:
    """Desflurane is where a naive comparison would report noise as a defect.

    Its ceiling is 3 x 6.6%, which in binary floating point is
    19.799999999999997 rather than 19.8, so a trace sitting exactly at 3 MAC
    is arithmetically *above* the axis by 4e-15. Isoflurane was the example
    while its MAC was 1.2%.
    """

    at_ceiling = (
        _sample(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id="desflurane"),
        _sample(1, 0.198, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id="desflurane"),
    )
    controller = _fake_controller(
        agent_id="desflurane",
        agent_display_name="Desflurane",
        max_delivered_concentration_percent=18.0,
        history=at_ceiling,
    )

    assert off_scale_notice(_frame(controller), 0) is None

    # ...and the tolerance is not so wide that it swallows a real excursion:
    # 19.82% clears the ceiling by more than the readouts can resolve.
    above_ceiling = (
        _sample(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id="desflurane"),
        _sample(1, 0.1982, 0.0, 0.0, 0.0, 0.0, 0.0, substance_id="desflurane"),
    )
    controller = _fake_controller(
        agent_id="desflurane",
        agent_display_name="Desflurane",
        max_delivered_concentration_percent=18.0,
        history=above_ceiling,
    )

    assert off_scale_notice(_frame(controller), 0) is not None


def test_a_hidden_trace_is_not_named_as_off_scale() -> None:
    """The notice must not point at a trace the reader has taken off the chart."""

    history = (
        _sample(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1, 0.08, 0.01, 0.01, 0.01, 0.0, 0.0),
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
        _sample(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1, 0.02, 0.018, 0.015, 0.014, 0.01, 0.005),
    )
    above = (_sample(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), _sample(1, 0.08, 0.01, 0.01, 0.01, 0.0, 0.0))
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
        _sample(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        _sample(1, 0.02, 0.018, 0.015, 0.014, 0.01, 0.005),
    )
    above = (_sample(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), _sample(1, 0.08, 0.01, 0.01, 0.01, 0.0, 0.0))
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

    assert wash_in_state_lines(frame) == tuple(
        compared_run_line(
            wash_in_state(_reading(snapshot), frame.runs[index].undrawn_wash_in_stretches),
            frame,
            index,
        )
        for index, snapshot in enumerate(snapshots)
    )


def test_a_wash_in_state_line_states_the_count_of_its_run_s_undrawn_stretches() -> None:
    """A run with stretches the window left undrawn says how many, in its own line."""

    controller = _fake_controller(history=_run_history(40))
    frame = _compared_frame(controller, _fake_controller(history=_run_history(40)))
    frame = replace(
        frame, runs=(replace(frame.runs[0], undrawn_wash_in_stretches=3), frame.runs[1])
    )
    reading = _reading(controller.snapshot())

    assert wash_in_state(reading, 3) != wash_in_state(reading, 0)
    assert wash_in_state_lines(frame)[0] == compared_run_line(wash_in_state(reading, 3), frame, 0)


def test_each_run_s_wash_in_state_line_states_its_own_run_s_reading() -> None:
    """Two runs at different F_A/F_I each get their own reading, under their own name.

    Before `PL-RF2S` the lines were built from the frame and a separate tuple
    of snapshots paired by position, so a line could carry another run's
    reading. The expected text is built from each run's own snapshot.
    """

    early = _fake_controller(history=_run_history(5))
    late = _fake_controller(history=_run_history(40))
    frame = _compared_frame(early, late)
    lines = wash_in_state_lines(frame)

    assert lines[0] != lines[1]
    assert lines == (
        compared_run_line(wash_in_state(_reading(early.snapshot()), 0), frame, 0),
        compared_run_line(wash_in_state(_reading(late.snapshot()), 0), frame, 1),
    )
    assert lines[0].startswith(run_label(RUN_IDS[0]))
    assert lines[1].startswith(run_label(RUN_IDS[1]))


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

    controller = _fake_controller(history=_run_history(60))

    assert no_traces_shown(_frame(controller)) is False
    assert no_traces_shown(_frame(controller, shown=())) is True
    assert no_traces_shown(_frame(controller, shown=(RecordedQuantity.ALVEOLAR,))) is False


def test_the_cap_notice_appears_exactly_while_a_second_run_is_drawn() -> None:
    """The two-compartment cap applies only while two runs are drawn, and the notice says so then.

    A lone run draws every compartment, so a notice there would describe a
    limit that is not on screen. With two runs, the notice names the cap of
    two and where every compartment's value can still be read. Every word of
    the expected notice is a literal here.
    """

    lone = _frame(_fake_controller(history=_run_history(40)))
    compared = _compared_frame(
        _fake_controller(history=_run_history(40)), _fake_controller(history=_run_history(40))
    )

    assert dashboard_frame.compartment_cap_notice(lone) is None
    assert dashboard_frame.compartment_cap_notice(compared) == (
        "Two runs are shown, so the chart draws at most 2 compartments at once. "
        "Every compartment's value is in the readouts above, for both runs."
    )


def test_each_legend_entry_names_its_compartment_and_line_style_and_then_its_run() -> None:
    """A legend entry names a compartment and its line style, and adds the run while two are drawn.

    The words are those of the table in `docs/INTERFACE.md` § "The six
    compartment traces: what separates them", so a reader can learn each style
    from the legend alone. While a second run is drawn, each entry names the
    compartment first and the run second.
    """

    expected = {
        RecordedQuantity.CIRCUIT: "Circuit (solid)",
        RecordedQuantity.ALVEOLAR: "Alveolar (long dash)",
        RecordedQuantity.MIXED_VENOUS: "Mixed venous (short dash)",
        RecordedQuantity.VESSEL_RICH: "Vessel-rich (even dash)",
        RecordedQuantity.MUSCLE: "Muscle (dotted)",
        RecordedQuantity.FAT: "Fat (dash-dot)",
    }

    for quantity, words in expected.items():
        assert dashboard_frame.trace_legend_label(trace_style(quantity)) == words

    assert dashboard_frame.compared_trace_legend_label(
        "Alveolar (long dash)", run_label(SECOND_RUN)
    ) == ("Alveolar (long dash), Run 2")


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

    branch = BranchedCase(_paused_run_with_history()).fork_at(CaseInstant(60))

    assert branch_at_stake("Run 2", branch.began_at_s, branch.snapshot(), 0) is None


def test_a_branch_run_past_its_fork_is_at_stake_with_both_instants() -> None:
    """How far the branch has run is stated as the instant its clock reads.

    The test uses a branch actually stepped to that instant.
    """

    branch = BranchedCase(_paused_run_with_history()).fork_at(CaseInstant(60))
    branch.start()
    _advance_to(branch, elapsed_s=90)
    branch.pause()

    assert branch_at_stake("Run 2", branch.began_at_s, branch.snapshot(), 0) == BranchAtStake(
        name="Run 2", began_at_s=60.0, elapsed_s=90.0, adjustment_count=0
    )


def test_a_branch_whose_snapshot_refuses_is_at_stake_with_no_instant_stated() -> None:
    """A branch that cannot be read is not known to hold nothing, so the question is still asked."""

    assert branch_at_stake("Run 2", CaseInstant(60), None, 0) == BranchAtStake(
        name="Run 2", began_at_s=60.0, elapsed_s=None, adjustment_count=0
    )


def test_the_trunk_reset_question_names_both_runs_and_what_the_trunk_keeps() -> None:
    """Every line of the question is a literal here, so the test, not the code, owns the wording.

    The keep button is named for the branch, because the branch is what the
    reader keeps by declining. The trunk is not touched either way.
    """

    question = trunk_reset_question(
        "Run 1", (BranchAtStake("Run 2", CaseInstant(60), CaseInstant(330), 2),)
    )

    assert question.title == "Reset Run 1 and discard Run 2?"
    assert question.body == (
        "Run 1's Reset starts the case over, and a branch cannot outlive the run it was "
        "taken from.",
        "Run 2 — branched at 1m and run to 5m30s, 2 recorded control changes — will be "
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


def test_each_reading_is_named_with_its_compartment_and_that_it_is_modelled() -> None:
    """`PL-N5JB`: a line of a readout panel, heard on its own, still says what it is.

    The expected names are written out here, from the strings each panel
    shows, and not read from `spoken_reading`'s templates. The gloss follows
    the name, because "Circuit" alone could be taken for the vaporizer setting.
    """

    clock_panel, circuit_panel, alveolar_panel, mixed_venous_panel = READOUT_PANELS[:4]
    circuit = Readout("Circuit", "inspired", "2.00%", "1.11 ×MAC", circuit_panel)
    alveolar = Readout("Alveolar", "end-tidal-equivalent", "1.20%", "0.67 ×MAC", alveolar_panel)
    mixed_venous = Readout(
        "Mixed venous", EMPTY_METRIC_QUALIFIER, "0.80%", "0.44 ×MAC", mixed_venous_panel
    )
    clock = Readout("Simulated time", EMPTY_METRIC_QUALIFIER, "1m30s", "1× real time", clock_panel)

    assert spoken_reading(circuit, circuit.value, None) == "Circuit, inspired, modelled: 2.00%"
    assert (
        spoken_reading(alveolar, alveolar.value, None)
        == "Alveolar, end-tidal-equivalent, modelled: 1.20%"
    )
    assert (
        spoken_reading(alveolar, alveolar.secondary, None)
        == "Alveolar, end-tidal-equivalent, modelled: 0.67 ×MAC"
    )
    assert (
        spoken_reading(alveolar, alveolar.value, "Run 2")
        == "Run 2, Alveolar, end-tidal-equivalent, modelled: 1.20%"
    )
    assert spoken_reading(mixed_venous, mixed_venous.value, None) == "Mixed venous, modelled: 0.80%"
    assert spoken_reading(clock, clock.value, None) == "Simulated time: 1m30s"
    assert spoken_reading(clock, clock.secondary, "Run 1") == "Run 1, Simulated time: 1× real time"


def test_a_withheld_reading_is_named_in_words_not_by_its_dash() -> None:
    """`PL-N5JB`: a withheld value is shown as a dash, and a screen reader is told it in words.

    The expected words are written out here. Each withheld line must say that
    the value is not shown, and the readings of the other panels stay as drawn.
    """

    clock, circuit, alveolar, *_ = withheld_readouts(DEFAULT_PLAYBACK_RATE)

    assert spoken_reading(circuit, circuit.value, None) == (
        "Circuit, inspired, modelled: percent not shown"
    )
    assert spoken_reading(alveolar, alveolar.secondary, None) == (
        "Alveolar, end-tidal-equivalent, modelled: multiple of MAC not shown"
    )
    assert spoken_reading(clock, clock.value, "Run 2") == "Run 2, Simulated time: not shown"
    assert spoken_reading(clock, clock.secondary, None) == (
        f"Simulated time: {clock_playback_line(DEFAULT_PLAYBACK_RATE)}"
    )
    for readout in (clock, circuit, alveolar):
        for reading in (readout.value, readout.secondary):
            assert "\u2014" not in spoken_reading(readout, reading, None)


def test_every_compartment_readout_is_marked_modelled_and_the_clock_is_not() -> None:
    """`PL-N5JB`: live and withheld readouts both say which panels hold model outputs."""

    compartments = ["Circuit", "Alveolar", "Mixed venous", "Vessel-rich group", "Muscle", "Fat"]

    for panels in (
        readouts(_snapshot(), DEFAULT_PLAYBACK_RATE),
        withheld_readouts(DEFAULT_PLAYBACK_RATE),
    ):
        assert [panel.name for panel in panels if panel.modelled] == compartments
        assert [panel.name for panel in panels if not panel.modelled] == ["Simulated time"]


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
# a mark's standing, meaning its status. A run detects when it reaches a mark
# (`PL-CTD7`). So a row says "reached" for a target the run halted on, or for
# one inside the step the run stands on or opened on
# (`MarkStanding.REACHED`). Other wording describes a mark the clock has
# passed, one the run can no longer reach, and one on a run that failed. A
# mark the run can still reach adds no words to its row.


def _marks() -> BookmarkSet:
    """One mark of each kind, both named."""

    return (
        BookmarkSet()
        .with_time_bookmark(TimeBookmark(CaseInstant(600), "intubation"))
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
    opened_at_s: int = 0,
    elapsed_s: int = 0,
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
    panel = _panel(BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600))))

    assert panel.times.rows == (format_elapsed(600.0),)


@pytest.mark.parametrize(
    ("agent_id", "vaporizer_maximum_percent", "mac_at_age_40_percent"),
    [
        # The vaporizer maxima are the shipped files' 8%, 5% and 18%. The MACs are
        # Mapleson 1996's at age 40 (PMID 8777094, Abstract): 1.80%, 1.17% and 6.6%.
        ("sevoflurane", 8.0, 1.8),
        ("isoflurane", 5.0, 1.17),
        ("desflurane", 18.0, 6.6),
    ],
)
def test_every_agent_reaches_the_default_target_ceiling(
    agent_id: str, vaporizer_maximum_percent: float, mac_at_age_40_percent: float
) -> None:
    """The target control's first ceiling is one every agent's vaporizer can reach.

    Desflurane reaches the least, 18 / 6.6 = 2.73 MAC, so a ceiling of 3 MAC
    would offer a target that no desflurane run could cross (`PL-LBVN`).
    """

    snapshot = SimulationController(agent_id=agent_id).snapshot()

    assert snapshot.max_delivered_concentration_percent == vaporizer_maximum_percent
    assert snapshot.agent_mac_percent == mac_at_age_40_percent
    assert vaporizer_maximum_percent / mac_at_age_40_percent >= DEFAULT_MAXIMUM_TARGET_MAC


@pytest.mark.parametrize(
    ("reachable_mac", "expected_maximum_mac"),
    [
        # Each vaporizer maximum over its agent's MAC, worked by hand: 8 / 1.8,
        # 5 / 1.17 and 18 / 6.6. Desflurane's 2.727 would round to nearest as
        # 2.73, which no desflurane run can reach (`PL-LBVN`).
        (8.0 / 1.8, 4.44),
        (5.0 / 1.17, 4.27),
        (18.0 / 6.6, 2.72),
        # Isoflurane at its former 1.2% MAC, 4.1667, which rounded up to 4.17.
        (5.0 / 1.2, 4.16),
        (DEFAULT_MAXIMUM_TARGET_MAC, 2.5),
        # A value one float below 4.17 is 4.17 that rounding pushed down, not
        # a height short of it.
        (math.nextafter(4.17, 0.0), 4.17),
    ],
)
def test_the_height_maximum_rounds_down_to_a_height_the_agent_can_reach(
    reachable_mac: float, expected_maximum_mac: float
) -> None:
    maximum_mac = height_entry_maximum_mac(reachable_mac)

    assert maximum_mac == pytest.approx(expected_maximum_mac)
    assert maximum_mac <= reachable_mac + WHOLE_COUNT_TOLERANCE


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
        .with_time_bookmark(TimeBookmark(CaseInstant(120), "first"))
        .with_time_bookmark(TimeBookmark(CaseInstant(600), "second"))
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
    """`PL-N3N5`, checked at the row a user reads.

    A failed run's marks used to be drawn with no words, because
    `STILL_RUNNING` renders as nothing at all on an unattributed row. So the
    one run on screen implied, by saying nothing, that the mark was still
    ahead of it, beside its own panel reading "Stopped - simulation error".
    The word must name the failure rather than the cap. The two stop a run
    for opposite reasons, and only one of them is a statement about what the
    model supports.
    """

    bookmark = TimeBookmark(CaseInstant(600), "check")
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

    bookmark = TimeBookmark(CaseInstant(600))
    target = MacTarget(RecordedQuantity.FAT, MacMultiple(0.5))

    passed = _time_row(bookmark, elapsed_s=600)
    reached = _target_row(target, reached=True)

    assert "passed" in passed
    assert "reached" not in passed
    assert "reached" in reached
    assert "passed" not in reached


def test_the_two_unreachable_outcomes_are_worded_apart() -> None:
    # "Not reached" alone would be true of both. It would also tell a user
    # that a bookmark before this branch's fork might arrive if they kept
    # running. `CLAUDE.md`'s safety-critical standard rules that out: the
    # model can decide the question outright, so a row must not imply
    # otherwise.
    bookmark = TimeBookmark(CaseInstant(600))
    at_the_cap = _time_row(bookmark, stopped_at_cap=True)
    inherited = _time_row(bookmark, opened_at_s=900, elapsed_s=900)

    assert at_the_cap != inherited
    assert "run length" in at_the_cap
    assert "branch" in inherited


def test_the_panel_reads_the_marks_the_snapshot_carries() -> None:
    controller = SimulationController()
    controller.add_time_bookmark(TimeBookmark(CaseInstant(600), "intubation"))

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

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(30), "check"))
    passed = _standings(marks, elapsed_s=120)

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
    said nothing at all. A branch that stopped at a mark the user set
    therefore looked the same on screen as a Pause. The one sign that a run
    had stopped where it was asked to existed for a lone run, and vanished as
    soon as a second run was drawn.
    """

    target = MacTarget(RecordedQuantity.ALVEOLAR, MacMultiple(0.5))
    marks = BookmarkSet().with_mac_target(target)
    trunk = _standings(marks, elapsed_s=60)
    branch = _standings(
        marks, opened_at_s=60, elapsed_s=175, reached_crossings=frozenset({target.crossing_key})
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

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(30), "check"))
    trunk = _standings(marks, elapsed_s=60)
    branch = _standings(marks, opened_at_s=60, elapsed_s=60)

    (row,) = bookmark_panel(marks, _two_runs(trunk, branch)).times.rows

    assert f"{run_label(FIRST_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.PASSED]}" in row
    assert row.endswith(
        f"{run_label(SECOND_RUN)} {MARK_STANDING_COMPARED_TEXT[MarkStanding.BEFORE_THIS_BRANCH]}"
    )


def test_the_inherited_standing_can_reach_a_drawn_row() -> None:
    """`PL-LHBY`: `BEFORE_THIS_BRANCH` had no screen it could appear on.

    The standing exists so that a user is not told something false about a
    mark that a branch carries but cannot reach. The panel used to read the
    reference run, which is the trunk. The trunk opens at zero, and no instant
    lies before that. The word was unreachable by construction rather than by
    accident, so this test checks the word itself rather than only the row
    that carries it.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(30)))
    trunk = _standings(marks, elapsed_s=60)
    branch = _standings(marks, opened_at_s=60, elapsed_s=60)

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
    """`PL-3K9B`'s wording guarantee, checked where a user actually compares runs.

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
#: A mark is a whole number of seconds and a step is one second. So the
#: instant the user marked is the instant at which a branch taken there
#: opens, and no control event of the offers below stands at it.
_PASSED_MARK = MarkForkPoint(TimeBookmark(CaseInstant(45), "the decision point"), CaseInstant(45))


_INDUCTION_POINT = ForkPoint(CaseInstant(0), "0s", None)
_SETTING_CHANGE_POINT = ForkPoint(CaseInstant(60), "1m", None)
_MARK_POINT = ForkPoint(CaseInstant(60), "1m, on your mark", TimeBookmark(CaseInstant(60), "check"))


def test_the_first_offer_that_holds_a_point_selects_its_first_point() -> None:
    """Before any offer, and after an offer of no points, nobody has chosen: the first is selected.

    The point selected before does not matter then, because an offer of no
    points comes from a trunk whose frame failed, and the selector was empty.
    """

    points = (_INDUCTION_POINT, _SETTING_CHANGE_POINT)

    assert kept_fork_selection(None, None, points) == _INDUCTION_POINT
    assert kept_fork_selection((), None, points) == _INDUCTION_POINT
    assert kept_fork_selection((), _SETTING_CHANGE_POINT, points) == _INDUCTION_POINT
    assert kept_fork_selection(None, None, ()) is None
    assert kept_fork_selection((), _SETTING_CHANGE_POINT, ()) is None


def test_a_selected_point_is_kept_while_the_offer_still_holds_it() -> None:
    """The selection follows its point to a new place in the list, found by equality."""

    before = (_INDUCTION_POINT, _SETTING_CHANGE_POINT)
    after = (_INDUCTION_POINT, ForkPoint(CaseInstant(30), "30s", None), _SETTING_CHANGE_POINT)
    rebuilt = ForkPoint(CaseInstant(60), "1m", None)

    assert kept_fork_selection(before, _SETTING_CHANGE_POINT, after) == _SETTING_CHANGE_POINT
    assert kept_fork_selection(before, rebuilt, after) == _SETTING_CHANGE_POINT
    assert kept_fork_selection(before, _INDUCTION_POINT, after) == _INDUCTION_POINT


def test_a_selected_point_that_leaves_the_offer_is_cleared_and_stays_clear() -> None:
    """Induction is never put in place of a point the user chose (`PL-J12Z`).

    A setting change and a mark at the same instant are two points, so a
    selected mark that is removed is cleared even while the setting change at
    its instant stays on offer.
    """

    with_mark = (_INDUCTION_POINT, _SETTING_CHANGE_POINT, _MARK_POINT)
    without_mark = (_INDUCTION_POINT, _SETTING_CHANGE_POINT)

    assert kept_fork_selection(with_mark, _MARK_POINT, without_mark) is None
    assert kept_fork_selection(without_mark, None, without_mark) is None
    assert kept_fork_selection(without_mark, None, with_mark) is None
    assert kept_fork_selection(with_mark, _SETTING_CHANGE_POINT, (_INDUCTION_POINT,)) is None


def test_fork_offer_labels_every_keyframe_the_trunk_holds() -> None:
    """Each instant from `BranchedCase.fork_points_s` is one entry, labelled by `format_elapsed`.

    Induction is offered rather than filtered out. A fork at zero is a second
    way of managing the whole case. Dropping it would leave a case that has
    recorded nothing with an empty selector beside a live button. Every entry
    here is a recorded control event, taken through `fork_at`, so no entry
    carries a mark.
    """

    offer = fork_offer(
        (CaseInstant(0), CaseInstant(60), CaseInstant(185)), marks=(), comparing=None, here=None
    )

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
        fork_offer((CaseInstant(0),), comparing=None, here=None)  # type: ignore[call-arg]


def test_fork_offer_is_refused_while_a_comparison_is_shown_and_says_the_way_out() -> None:
    """The display is capped at two runs and there is no run selector yet.

    A refused control that does not say how to lift the refusal is a dead end
    rather than a mode. So the reason names the Reset that ends the
    comparison, by the run that Reset belongs to. The test below checks that
    naming.
    """

    offer = fork_offer((CaseInstant(0), CaseInstant(60)), marks=(), comparing=COMPARED, here=None)

    assert offer.locked is True
    assert offer.lock_reason == comparing_fork_lock_text(COMPARED)


def test_fork_offer_names_the_pin_only_beside_a_branch_that_can_be_taken() -> None:
    """A pinned Workspace says before the press that a branch will not be drawn there (`PL-RXR8`).

    The notice is written out here rather than read from the template. It is
    given while a branch is offered and the Workspace is pinned. It is not
    given while the Workspace is unpinned, while two runs are open, because
    the lock caption then names the pin, or while nothing is offered, because
    there is no press for it to come before.
    """

    points = (CaseInstant(0), CaseInstant(60))
    expected = (
        "This Workspace is pinned to Run 1, so it will not draw a branch taken here "
        "beside it. Unpin it from the Workspace's tab to compare the two runs here."
    )

    pinned = fork_offer(points, marks=(), comparing=None, here=None, pinned_to="Run 1")
    unpinned = fork_offer(points, marks=(), comparing=None, here=None, pinned_to=None)
    comparing = fork_offer(points, marks=(), comparing=COMPARED, here=None, pinned_to="Run 1")
    nothing_offered = fork_offer((), marks=(), comparing=None, here=None, pinned_to="Run 1")
    only_here = fork_offer(
        (),
        marks=(),
        comparing=None,
        here=HereForkPoint(CaseInstant(45), stopped_on_mark=False),
        pinned_to="Run 1",
    )

    assert pinned.pinned_notice == expected
    assert unpinned.pinned_notice == ""
    assert comparing.pinned_notice == ""
    assert nothing_offered.pinned_notice == ""
    assert only_here.pinned_notice == expected


def test_the_comparison_lock_names_a_control_the_user_can_press() -> None:
    """`PL-WG73`: "Reset the case to end this one" named no control on screen.

    The old assertion checked only the bare word "Reset", and it passed while
    the sentence pointed at a "case" that nothing on screen is labelled with.
    A user can act on a run's name and the word on its transport button.
    So the test checks both named controls as the pair in which the screen
    draws them.

    **Each clause is checked against the run it is about, rather than the
    whole sentence against both names.** A sentence could name both controls
    correctly but pair each with the other's outcome. That would send the
    user to the same wrong button as the sentence this replaced, and a
    test that reads the whole string cannot tell the two apart. So the way
    out is checked on its own. It names the trunk's Reset, it does not
    mention the branch at all, and it says that the press costs the case
    starting over.

    The clause after it is about the branch's Reset, and names what that
    button does *instead*. A user reaches for that Reset, because it
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

    offer = fork_offer((CaseInstant(0), CaseInstant(60)), marks=(), comparing=None, here=None)

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

    here = HereForkPoint(CaseInstant(45), stopped_on_mark=False)

    offer = fork_offer((CaseInstant(0), CaseInstant(60)), marks=(), comparing=None, here=here)

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
    The frame is given no marked instant at all, so it cannot label
    the button with one. The frame is not told which kind of mark stopped the
    trunk either. One label serves a marked instant and a marked height
    alike, because the bookmark panel's row states which marks were crossed.
    """

    halted_s = 45
    halted = HereForkPoint(CaseInstant(halted_s), stopped_on_mark=True)
    paused = HereForkPoint(CaseInstant(halted_s), stopped_on_mark=False)

    on_the_mark = fork_offer((CaseInstant(0),), marks=(), comparing=None, here=halted).here_label
    on_a_pause = fork_offer((CaseInstant(0),), marks=(), comparing=None, here=paused).here_label

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
        here = HereForkPoint(CaseInstant(45), stopped_on_mark)

        offer = fork_offer(
            (CaseInstant(0), CaseInstant(60)), marks=(), comparing=COMPARED, here=here
        )

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
        fork_offer((CaseInstant(0),), marks=(), comparing=None, here=None, refusal=refusal).refusal
        == refusal
    )
    assert (
        fork_offer(
            (CaseInstant(0),), marks=(), comparing=COMPARED, here=None, refusal=refusal
        ).refusal
        is None
    )


def test_fork_offer_lists_each_passed_mark_among_the_keyframes_by_instant() -> None:
    """`PL-W4XQ`: the marks the trunk has passed are offered beside the control events.

    Both kinds go in one list, earliest first, because both stay on offer
    until the case itself changes. A user paused at 3 h who marks 1 h
    finds the mark where it falls on the clock, between the decision points
    on either side of it. The list is sorted here rather than trusted to
    arrive in order, so the marks are placed by instant whatever order they
    are passed in.
    """

    early = MarkForkPoint(TimeBookmark(CaseInstant(30)), CaseInstant(30))
    late = MarkForkPoint(TimeBookmark(CaseInstant(120), "what if"), CaseInstant(120))

    offer = fork_offer(
        (CaseInstant(0), CaseInstant(60), CaseInstant(185)),
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
    """A mark is reached on a whole second, and the entry names that instant.

    `BranchedCase.fork_at_mark` opens the branch at `MarkForkPoint.fork_s`, so
    that is the instant the entry must carry. It is also the instant the
    user marked, because a mark never lies inside a step (`PL-SZ6G`). A
    label naming any other time would be the wrong label on a correct value,
    which `CLAUDE.md`'s safety-critical standard counts as a failure of the
    value. The words are restated rather than built from the template, so an
    edit to the template cannot move both sides at once.
    """

    offer = fork_offer((CaseInstant(0),), marks=(_PASSED_MARK,), comparing=None, here=None)
    entry = offer.points[-1]

    assert entry.label == "45s, on your mark"
    assert entry.instant_s == 45
    assert entry.instant_s == _PASSED_MARK.fork_s == _PASSED_MARK.bookmark.instant_s


def test_a_control_event_is_listed_before_a_mark_at_the_same_instant() -> None:
    """A control event and a mark at the same instant get two entries, control event first.

    A mark set at the instant of a recorded control event gets an entry of
    its own, and `fork_offer` does not merge the two. Both entries open the
    same branch, because every way of branching at one instant names the
    same provenance and runs under what the dial says (`PL-ZR49`). The
    entries keep the order in which `fork_offer` receives its two lists,
    the control events and then the marks. So one case is always listed the
    same way. The case's opening, at 0 s, is the boundary case, because no
    step reaches a mark there. A branch at that mark opens at the opening
    keyframe, and the mark is listed after that keyframe.
    """

    at_opening = MarkForkPoint(TimeBookmark(CaseInstant(0)), CaseInstant(0))
    on_the_change = MarkForkPoint(TimeBookmark(CaseInstant(60), "the change"), CaseInstant(60))

    offer = fork_offer(
        (CaseInstant(0), CaseInstant(60)),
        marks=(at_opening, on_the_change),
        comparing=None,
        here=None,
    )

    assert offer.points == (
        ForkPoint(CaseInstant(0), format_elapsed(0.0), None),
        ForkPoint(
            CaseInstant(0),
            MARK_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(0.0)),
            at_opening.bookmark,
        ),
        ForkPoint(CaseInstant(60), format_elapsed(60.0), None),
        ForkPoint(
            CaseInstant(60),
            MARK_FORK_LABEL_TEMPLATE.format(instant=format_elapsed(60.0)),
            on_the_change.bookmark,
        ),
    )


def test_each_entry_carries_the_door_it_is_taken_through() -> None:
    """A control event's entry carries no mark, and a mark's entry carries the mark itself.

    A control event is taken at its instant. A mark's entry carries the mark
    rather than an instant, because `fork_at_mark` takes the mark and finds
    the step itself. A caller that passed back the entry's instant instead
    would ask `fork_at` for 45 s, and `fork_at` refuses that because no
    keyframe is there. The mark is the same object the case
    listed, name and all, so nothing between the frame and the press builds
    it again.
    """

    offer = fork_offer(
        (CaseInstant(0), CaseInstant(60)), marks=(_PASSED_MARK,), comparing=None, here=None
    )
    control_events = [point for point in offer.points if point.mark is None]
    marks = [point for point in offer.points if point.mark is not None]

    assert [point.instant_s for point in control_events] == [0.0, 60.0]
    assert len(marks) == 1
    assert marks[0].mark is _PASSED_MARK.bookmark


def test_a_locked_offer_stays_locked_whatever_marks_the_trunk_has_passed() -> None:
    """The cap limits branches, so a passed mark opens no way around the lock.

    The lock, its reason, the control at the paused point and the refusal are
    exactly as they are with no marks at all. The marks are entries in the
    control that the lock replaces, not a further control the cap could miss.
    """

    here = HereForkPoint(CaseInstant(45), stopped_on_mark=True)
    refusal = "Setting refused: no keyframe at 30.0 s"
    keyframes = (CaseInstant(0), CaseInstant(60))

    unmarked = fork_offer(keyframes, marks=(), comparing=COMPARED, here=here, refusal=refusal)
    marked = fork_offer(
        keyframes, marks=(_PASSED_MARK,), comparing=COMPARED, here=here, refusal=refusal
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


def test_a_pinned_run_of_an_earlier_session_is_named_without_its_number() -> None:
    """`PL-7H9X`: an open run can carry the number of a run pinned in an earlier session."""

    earlier = RunId(SessionToken("f" * 32), 1)

    assert pinned_run_label(earlier, TEST_SESSION) == "a run from an earlier session"
    # A run of this session keeps its name, whether it is open or has closed.
    assert pinned_run_label(RunId(TEST_SESSION, 1), TEST_SESSION) == "Run 1"
    assert pinned_run_label(RunId(TEST_SESSION, 3), TEST_SESSION) == "Run 3"


@pytest.mark.parametrize(
    ("session", "type_name"),
    [("0" * 32, "str"), (None, "NoneType"), (RunId(TEST_SESSION, 1), "RunId")],
)
def test_a_pinned_run_is_named_only_in_a_session_given_by_its_token(
    session: object, type_name: str
) -> None:
    with pytest.raises(TypeError, match=f"a session is a SessionToken, not {type_name}$"):
        pinned_run_label(RunId(TEST_SESSION, 1), session)  # type: ignore[arg-type]


@pytest.mark.parametrize("position", [0, 1, True])
def test_a_run_is_not_named_from_a_drawing_position(position: object) -> None:
    """A drawing position names whichever run is drawn there, so it is refused (`PL-7Z84`)."""

    with pytest.raises(TypeError, match="a run is named from its RunId"):
        run_label(position)  # type: ignore[arg-type]


# --- the preview of a dragged setting ------------------------------------------


def test_a_preview_label_names_the_control_the_value_and_that_it_is_not_applied() -> None:
    """The words are the slider's own, so the plot and the control cannot disagree (`PL-5B1N`)."""

    assert (
        preview_label(ControlInput.FRESH_GAS_FLOW, 6.0, "Sevoflurane", None)
        == "Preview: Fresh gas flow 6.0 L/min, not applied"
    )
    assert (
        preview_label(ControlInput.DELIVERED, 3.5, "Sevoflurane", "Run 2")
        == "Run 2 preview: Sevoflurane vaporizer 3.50%, not applied"
    )
    assert (
        preview_label(ControlInput.CARDIAC_OUTPUT, 8.0, "Isoflurane", None)
        == "Preview: Cardiac output 8.0 L/min, not applied"
    )


def test_the_preview_label_uses_the_words_the_slider_prints() -> None:
    controller = SimulationController()
    readouts = setting_readouts(controller.snapshot())

    for readout in readouts:
        assert preview_label(readout.control, readout.value, "Sevoflurane", None) == (
            f"Preview: {readout.name} {readout.value_text}, not applied"
        )


def test_the_axis_caption_says_when_the_window_is_centred_for_a_preview() -> None:
    """A previewing window shows neither the whole run nor its newest stretch."""

    controller = SimulationController()
    controller.start()

    for _ in range(600 // SIMULATION_STEP_S):
        controller.advance()

    frame = assemble_chart_frame(
        (
            RunInput(
                run_label(FIRST_RUN),
                controller,
                controller.snapshot(),
                (),
                preview=PreviewRequest(SettingPreview(ControlInput.FRESH_GAS_FLOW, 6.0), "x"),
            ),
        ),
        None,
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
    )
    caption = time_axis_caption(frame)

    assert "whole run so far" not in caption
    assert (
        caption
        == f"{format_time_base(frame.time_base.span_s)} shown, centred on now during the preview"
    )


def test_a_preview_above_the_axis_is_named_with_its_highest_predicted_value() -> None:
    """Sevoflurane at 8% on the dial is 4 MAC, above the 3 MAC axis, and a held thumb previews it.

    The readouts and the hover never show a preview's values. So the notice
    names each clipped prediction and its highest value in view. Otherwise,
    the clipped curve could be mistaken for a predicted plateau at the top of
    the axis (found by the blind review of `PL-5B1N`).
    """

    controller = SimulationController()
    controller.start()

    for _ in range(300 // SIMULATION_STEP_S):
        controller.advance()

    frame = assemble_chart_frame(
        (
            RunInput(
                run_label(FIRST_RUN),
                controller,
                controller.snapshot(),
                (),
                preview=PreviewRequest(SettingPreview(ControlInput.DELIVERED, 8.0), "x"),
            ),
        ),
        time_base_for_span(1800.0),
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
    )
    preview = frame.runs[0].preview
    assert preview is not None
    circuit_peak = max(preview.fractions[RecordedQuantity.CIRCUIT])
    notice = off_scale_notice(frame, 0)

    assert notice is not None
    assert "The preview goes above the top of the plot" in notice
    assert f"Circuit {format_mac_multiple(circuit_peak, frame.mac_percent)}" in notice
    assert "readouts above" not in notice


def test_a_run_and_its_preview_both_above_the_axis_are_named_in_two_sentences() -> None:
    """The run's sentence comes first and the preview's second, each naming every clipped trace."""

    controller = SimulationController()
    controller.set_delivered_concentration_percent(
        Percent(8.0, name="delivered_concentration_percent")
    )
    controller.set_fresh_gas_flow(FreshGasFlow(10.0))
    controller.start()

    for _ in range(2_400 // SIMULATION_STEP_S):
        controller.advance()

    frame = assemble_chart_frame(
        (
            RunInput(
                run_label(FIRST_RUN),
                controller,
                controller.snapshot(),
                (),
                preview=PreviewRequest(SettingPreview(ControlInput.FRESH_GAS_FLOW, 10.0), "x"),
            ),
        ),
        time_base_for_span(1800.0),
        COMPARTMENT_QUANTITIES,
        plot_width_px=_PLOT_WIDTH_PX,
        held_start_s=None,
    )
    run = frame.runs[0]
    preview = run.preview
    assert preview is not None
    ceiling = frame.axis_top_percent + CONCENTRATION_DISPLAY_RESOLUTION_PERCENT
    clipped = [
        trace_style(quantity).label
        for quantity in frame.visible
        if max(run.percents(quantity)) > ceiling
    ]
    peaks = [
        f"{trace_style(quantity).label} "
        f"{format_mac_multiple(max(preview.fractions[quantity]), frame.mac_percent)}"
        for quantity in frame.visible
        if max(preview.percents(quantity)) > ceiling
    ]
    assert len(clipped) >= 2
    assert len(peaks) >= 2
    # Sevoflurane's standard top is 3 x 1.8% = 5.40%, worked by hand (`PL-DVDY`).
    top = "5.40% (3.00 ×MAC)"

    assert off_scale_notice(frame, 0) == (
        OFF_SCALE_NOTICE_TEMPLATE.format(compartments=", ".join(clipped), top=top)
        + " "
        + PREVIEW_OFF_SCALE_NOTICE_TEMPLATE.format(top=top, peaks=", ".join(peaks))
    )


def test_only_the_delivered_dial_carries_a_second_line() -> None:
    """The flows have no second unit, so their secondary line is empty, not a placeholder."""

    readouts = setting_readouts(SimulationController().snapshot())

    for readout in readouts:
        if readout.control is not ControlInput.DELIVERED:
            assert readout.secondary == ""


def test_a_value_the_readouts_print_as_the_top_is_not_above_it() -> None:
    """Isoflurane's top, 3 x 1.2, is 3.5999999999999996 in binary (`PL-RNYV`).

    A tension of 3.6% prints as the top. It is not above the scale, so
    neither the chart's notice nor the schematic's mark may name it. A
    tension less than one display step above the top is not above it
    either, and one more than a step above it is.
    """

    top = 3 * 1.2

    assert top != 3.6
    assert above_the_axis_top(3.6, top) is False
    assert above_the_axis_top(3.605, top) is False
    # Exactly one display step above the top is still not above it: 0.01 - 0.0
    # is exactly 0.01 in binary, so this pins the comparison as strict.
    assert above_the_axis_top(CONCENTRATION_DISPLAY_RESOLUTION_PERCENT, 0.0) is False
    assert above_the_axis_top(3.62, top) is True
    assert above_the_axis_top(0.0, top) is False


# --- the case's marks, read from every run --------------------------------------------


def _reachable_height(agent_id: str) -> float:
    """The highest mark an agent's run accepts, worked out here from the agent's own file."""

    agent = load_agent_parameters(agent_id)

    return float(agent.max_delivered_concentration_percent) / float(agent.mac_at_age_40_percent)


def test_the_case_s_marks_are_stated_once_when_every_run_agrees() -> None:
    """Three runs that hold the same marks give one panel, each run's standings, and one bound."""

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600), "intubation"))
    settings = SimulationController().settings()
    labels = ("Run 1", "Run 2", "Run 3")
    standings = (_unreached(marks),) * 3

    shown = case_marks(labels, (marks,) * 3, standings, (settings,) * 3)

    assert shown.panel == bookmark_panel(
        marks, tuple(RunMarks(label, run) for label, run in zip(labels, standings, strict=True))
    )
    assert shown.reachable_height_mac == pytest.approx(_reachable_height("sevoflurane"))


def test_the_case_s_marks_are_refused_when_a_run_holds_other_marks() -> None:
    """A run holding a mark the others do not hold is refused, not dropped from the panel.

    Before `PL-RF2S` the set was read from the first run alone, so a third
    run's extra mark was left out of the panel without a word.
    """

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(600)))
    more = marks.with_time_bookmark(TimeBookmark(CaseInstant(900)))
    settings = SimulationController().settings()

    with pytest.raises(ValueError, match="Run 3 holds different marks from Run 1"):
        case_marks(
            ("Run 1", "Run 2", "Run 3"),
            (marks, marks, more),
            (_unreached(marks), _unreached(marks), _unreached(more)),
            (settings,) * 3,
        )


def test_the_case_s_marks_are_refused_when_two_runs_give_different_bounds() -> None:
    marks = BookmarkSet()
    sevoflurane = SimulationController(agent_id="sevoflurane").settings()
    desflurane = SimulationController(agent_id="desflurane").settings()

    assert _reachable_height("sevoflurane") != pytest.approx(_reachable_height("desflurane"))

    with pytest.raises(ValueError, match="Run 2 accepts marks up to"):
        case_marks(
            ("Run 1", "Run 2"), (marks, marks), (_unreached(marks),) * 2, (sevoflurane, desflurane)
        )


def test_the_case_s_marks_need_one_entry_per_run_in_each_list() -> None:
    marks = BookmarkSet()
    settings = SimulationController().settings()

    with pytest.raises(ValueError, match="one entry per run"):
        case_marks(("Run 1", "Run 2"), (marks,), (_unreached(marks),) * 2, (settings,) * 2)

    with pytest.raises(
        ValueError, match="^the case's marks are read from at least one run; none was given$"
    ):
        case_marks((), (), (), ())


def test_a_refused_bound_names_the_first_run_and_its_own_bound() -> None:
    """The refusal names the run that differs, and the first run with the first run's bound."""

    marks = BookmarkSet()
    sevoflurane = SimulationController(agent_id="sevoflurane").settings()
    desflurane = SimulationController(agent_id="desflurane").settings()

    with pytest.raises(ValueError) as refused:
        case_marks(
            ("Run 1", "Run 2"), (marks, marks), (_unreached(marks),) * 2, (sevoflurane, desflurane)
        )

    message = str(refused.value)
    _, named, after = message.partition("and Run 1 up to ")
    assert named, message
    assert float(after.split(" x MAC")[0]) == pytest.approx(_reachable_height("sevoflurane"))


def test_the_case_s_marks_name_each_run_whose_standing_differs() -> None:
    """Where two runs stand differently on a mark, the row names each run by its own label."""

    marks = BookmarkSet().with_time_bookmark(TimeBookmark(CaseInstant(30), "check"))
    settings = SimulationController().settings()
    passed = _standings(marks, elapsed_s=120)
    unreached = _standings(marks, elapsed_s=10)

    shown = case_marks(("Run 1", "Run 2"), (marks, marks), (passed, unreached), (settings,) * 2)

    (row,) = shown.panel.times.rows
    assert "Run 1" in row
    assert "Run 2" in row
