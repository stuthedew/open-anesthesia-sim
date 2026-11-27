"""Everything on screen that belongs to one run at one moment, as one value.

Every widget that shows one run is written from one `RunPresentation`.
`RunView.show_presentation` writes the run's own panel from it: the status
word, the transport, the agent identity, the delivered line, the
control-change panel, the banner and the readouts. The Views in
`app/views.py` write the run's panels in the Areas from the same value: the
four dials, the accounting panel, the compartment schematic and the agent
cost panel. Two functions here build that value, and neither loads a GUI
toolkit. `drawn_run` builds it from the snapshot that a frame drew from.
`halted_run` builds it from the run's record when no frame is drawn.
`tests/unit/test_run_presentation.py` tests both with no widget.

A halt is not a second writer. It is a `RunPresentation` whose values are kept
or withheld, and each writer writes it exactly as it writes a drawn one
(`PL-RF2S`). Before this module, a frame and a halt each wrote the
widgets themselves, and each wrote a different part of them. A value that the
halt left out stayed on screen from the run before, under a heading that named
the run after it. Four fixes each added the missed widget to the halt, and to a
test's list of widgets (`PL-X7D5`, `PL-J5GC`, `PL-5JTH`, `PL-GTH6`). The next
widget was missed in the same way (`PL-B8DL`, `PL-0G2P`).

**A halt keeps or withholds the values that only a frame can compute.** The
readouts, the schematic, the delivered agent and the accounting panel are
compartment values, and a halt builds none, because the halt may be the
refusal of one of them (`PL-7DJK`). `RunValues` holds the four together.
`halted_run` uses the `RunValues` of the last frame that drew, unless the run
has started over since that frame. Then the kept values describe a run that
was discarded, and `halted_run` uses `withheld_values` in their place. All
four are kept or withheld as one value, so no one of them can be left behind.

**A chart's frame is kept or withheld by the same rule** (`PL-RF2S`). A
chart window's frame is assembled from every displayed run, so it is kept
only while every run is the one it was drawn from: the same runs, in the same
order, none of them started over since. `KeptFrames` records which runs and
cases the last drawn frames belong to, and `shown_without_a_frame` compares
that with the runs as they stand now. Otherwise the frame is withheld, and the
chart shows an empty plot with the reason. A run's banner on a halt says
whether the charts are withheld (`RunPanelState.charts_withheld`), so it
never says that a chart shows the last frame while the chart is empty.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from enum import StrEnum
from types import MappingProxyType

from anesthesia_sim.app.agent_cost import WITHHELD_DELIVERED, DeliveredShown, delivered_shown
from anesthesia_sim.app.chart_frame import ChartFrame
from anesthesia_sim.app.chart_time_base import ChartWindow
from anesthesia_sim.app.compartment_schematic import (
    WITHHELD_SCHEMATIC,
    SchematicShown,
    schematic_shown,
)
from anesthesia_sim.app.compartment_selection import CompartmentSelection
from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.control_timeline import ControlAdjustment
from anesthesia_sim.app.controller import RunRecord, SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import (
    READOUT_PANELS,
    WITHHELD_ACCOUNTING,
    WITHHELD_DELIVERED_LINE_TEXT,
    Accounting,
    NewCaseQuestion,
    Notice,
    Readout,
    RunStatement,
    SettingReadout,
    accounting,
    clock_playback_line,
    compared_run_notice,
    delivered_line,
    failure_details,
    halt_run_notice,
    new_case_question,
    readouts,
    rejected_step_accounting,
    run_notice,
    run_statement,
    setting_readouts,
    withheld_readouts,
)
from anesthesia_sim.app.failures import failure_log_path
from anesthesia_sim.app.formatting import format_mac_reference
from anesthesia_sim.app.playback import PlaybackRate
from anesthesia_sim.layout.run_identity import RunId


class ValuesStanding(StrEnum):
    """Where a presentation's compartment values came from.

    Attributes:
        DRAWN: They were computed from the snapshot this presentation was
            built from.
        KEPT: No frame can be drawn, and they are the values of the last
            frame that drew. The run has not started over since that frame.
        WITHHELD: No frame can be drawn, and the run has started over since
            the last frame that drew. Each value is replaced by a placeholder
            that keeps its unit.
    """

    DRAWN = "drawn"
    KEPT = "kept"
    WITHHELD = "withheld"


@dataclass(frozen=True, slots=True)
class RunValues:
    """The compartment values of one run at one instant: everything only a frame can compute.

    The readouts, the schematic, the delivered agent and the accounting
    panel are built together from one snapshot, kept together, and withheld
    together. So they always describe the same state of the same run
    (`PL-RNYV`, `PL-B396`).

    Attributes:
        readouts: The seven readout panels, in `READOUT_PANELS` order.
        schematic: The compartment schematic.
        delivered: The agent cost panel's delivered agent.
        accounting: The agent-accounting panel.
    """

    readouts: tuple[Readout, ...]
    schematic: SchematicShown
    delivered: DeliveredShown
    accounting: Accounting


@dataclass(frozen=True, slots=True)
class KeptValues:
    """The values of the last frame that drew, and the case they belong to.

    Attributes:
        case: `RunPanelState.case` as it stood when the values were drawn.
        values: The values that frame drew.
    """

    case: int
    values: RunValues


@dataclass(frozen=True, slots=True)
class NotBuilt:
    """Why one part of a presentation could not be built for a run.

    Two parts can fail while the run can still be stated. One is the four
    setting controls with the delivered line, which `setting_readouts`
    refuses for a control that can offer no accepted setting. The other is
    the 1 MAC line. Both also fail for a record whose MAC was not built as
    `MacPercent`. The exception is carried in the presentation, so that
    `RunView.show_presentation` can put the status word, the transport and
    the banner on screen before it raises the exception (`PL-25KS`,
    `PL-7DJK`, `PL-85LJ`).

    Attributes:
        error: The exception that building the part raised.
    """

    error: Exception


@dataclass(frozen=True, slots=True)
class RunPanelState:
    """What a run's panel holds that the run's controller does not.

    `RunView` reads these from itself and from the dashboard at the moment it
    builds a presentation.

    Attributes:
        run_id: The run's identity.
        name: What the run is called while a second run is drawn, or None.
        case: A count of the times the run has started over, by a Reset or
            an agent change. `halted_run` compares it with `KeptValues.case`.
        playback_rate: The rate at which the run is played.
        is_branch: As `dashboard_frame.transport` takes it.
        comparing: As `dashboard_frame.transport` takes it.
        branch_offered: As `dashboard_frame.notice` takes it.
        rejected_setting_notice: The notice for a setting the run refused,
            or None.
        refused_preview_notice: The banner for the preview of a held dial
            that the run refused, as `dashboard_frame.notice` takes it, or
            None (`PL-412F`).
        refused_reset_notice: The notice for a Reset the run refused, or None.
        refused_reset_reason: The message of the error with which a Reset
            was refused, for the failure's details, or None.
        pending_agent_name: The agent that an open new-case question
            proposes, or None while no such question is open.
        reset_question: The open Reset question, restated from the runs as
            they stand now, or None while no Reset question is open.
        charts_withheld: Whether the charts withhold their frame on a tick
            that draws none, because the runs they show are not the runs
            their last frame was drawn from (`kept_frames_match`). A halt's
            banner then says that the charts are withheld.
        delivered_fraction: The fraction of the set rate that the run is
            delivering while the clock line should name it, as
            `playback.TickPace.disclosed_fraction` returns it, or None
            (`PL-2NYN`). A halted run is not playing, so `halted_run` does not
            read it.
    """

    run_id: RunId
    name: str | None
    case: int
    playback_rate: PlaybackRate
    is_branch: bool
    comparing: bool
    branch_offered: bool
    rejected_setting_notice: str | None
    refused_preview_notice: str | None
    refused_reset_notice: str | None
    refused_reset_reason: str | None
    pending_agent_name: str | None
    reset_question: NewCaseQuestion | None
    charts_withheld: bool
    delivered_fraction: float | None = None


@dataclass(frozen=True, slots=True)
class RunPresentation:
    """Everything one run's panel shows at one moment.

    Attributes:
        run_id: The run the values belong to.
        name: What the run is called while a second run is drawn, or None.
        case: How many times the run had started over, by a Reset or an agent
            change, when this presentation was built (`RunPanelState.case`).
        record: The run's record that this presentation states.
            `RunView.owes_a_frame` compares it with the controller's record.
        statement: The run-state widgets: the agent, the status word, the
            transport and the control-change panel.
        notice: The banner, with its text naming the run while a second run
            is drawn, and the emphasis it is drawn with. None for no banner.
        one_mac: The line stating 1 MAC of the running agent, or why it
            could not be built. 1 MAC is the divisor of every ×MAC number in
            `values` and `dials`.
        standing: Where `values` came from.
        values: The compartment values.
        dials: The four setting controls, or why they or the delivered line
            could not be built.
        delivered_line: The delivered concentration's line beside the 1 MAC
            line. When `dials` holds no controls, the line withholds both of
            its values and keeps their units (`PL-SV2Q`).
        new_case: The open new-case question, restated for the snapshot this
            presentation was drawn from. It is None when no such question is
            open, and on a halt. A halted run does not step, so the figures
            in the question from the last frame are still correct.
        reset_question: The open Reset question, restated for the runs as
            they stand at this frame (`PL-WM5P`). It is None while no such
            question is open, and on a halt, for the same reason as
            `new_case`.
        failure_details: The details under a failed run's banner, for a
            report of the fault (`dashboard_frame.failure_details`), or None
            while the run has not failed.
    """

    run_id: RunId
    name: str | None
    case: int
    record: RunRecord
    statement: RunStatement
    notice: Notice | None
    failure_details: str | None
    one_mac: str | NotBuilt
    standing: ValuesStanding
    values: RunValues
    dials: tuple[SettingReadout, ...] | NotBuilt
    delivered_line: str
    new_case: NewCaseQuestion | None
    reset_question: NewCaseQuestion | None


def drawn_values(snapshot: SimulationSnapshot, playback_rate: PlaybackRate) -> RunValues:
    """Return the compartment values of one snapshot.

    Raises:
        TypeError: As `readouts`, `schematic_shown` and `delivered_shown`
            raise it.
        ValueError: As those three raise it.
    """

    return RunValues(
        readouts=readouts(snapshot, playback_rate),
        schematic=schematic_shown(snapshot),
        delivered=delivered_shown(snapshot),
        accounting=accounting(snapshot),
    )


def withheld_values(playback_rate: PlaybackRate) -> RunValues:
    """Return every compartment value withheld, for a run that started over with no frame since.

    Each value was last drawn for the run before the Reset or the agent
    change. After an agent change, each concentration is the old agent's and
    each ×MAC number was divided by the old agent's MAC, while the heading
    and the 1 MAC line already name the new agent (`PL-6RJ0`, `PL-J5GC`).
    Every field of `RunValues` is replaced here. A field added to
    `RunValues` must be given a withheld form here before this function can
    build the value.
    """

    return RunValues(
        readouts=withheld_readouts(playback_rate),
        schematic=WITHHELD_SCHEMATIC,
        delivered=WITHHELD_DELIVERED,
        accounting=WITHHELD_ACCOUNTING,
    )


def drawn_run(
    snapshot: SimulationSnapshot, adjustments: Sequence[ControlAdjustment], state: RunPanelState
) -> RunPresentation:
    """Return what a run's panel shows for the snapshot that a frame drew from.

    Every value is computed here, before `RunView.show_presentation` writes any. So a
    value that cannot be computed leaves the whole panel on its earlier
    state, and never some widgets on this snapshot and some on the last.

    Args:
        snapshot: The run's state this tick.
        adjustments: `snapshot.control_timeline` grouped into acts, as
            `RunView.adjustments` groups it.
        state: What the run's panel holds.

    Returns:
        The presentation, with its values drawn from `snapshot`.

    Raises:
        TypeError: As `drawn_values` raises it.
        ValueError: As `drawn_values` raises it. An exception raised while
            building the dials or the 1 MAC line is not raised here. It is
            returned in `dials` or in `one_mac`.
    """

    values = drawn_values(snapshot, state.playback_rate)

    if state.delivered_fraction is not None:
        values = replace(
            values,
            readouts=_at_playback_rate(
                values.readouts, state.playback_rate, state.delivered_fraction
            ),
        )

    new_case = (
        None
        if state.pending_agent_name is None
        else new_case_question(snapshot, state.pending_agent_name, len(adjustments))
    )

    return _presentation(
        snapshot,
        adjustments,
        state,
        banner=run_notice(
            snapshot,
            state.rejected_setting_notice,
            elapsed_s=snapshot.elapsed_s,
            refused_reset=state.refused_reset_notice,
            branch_offered=state.branch_offered,
            refused_preview=state.refused_preview_notice,
        ),
        stopped_on_mark=snapshot.stopped_on_mark,
        standing=ValuesStanding.DRAWN,
        values=values,
        new_case=new_case,
        reset_question=state.reset_question,
    )


def halted_run(
    record: RunRecord,
    adjustments: Sequence[ControlAdjustment],
    state: RunPanelState,
    kept: KeptValues,
) -> RunPresentation:
    """Return what is shown for a run when no frame is drawn for it.

    This is called in two cases. On a halt, it gives what the run's own
    panel and every View show for the stopped run. Just after a run's dial
    is dragged, the dashboard also hands every View the runs with no frame
    (`SimulationView.present`), and that run has not stopped. The Views
    write only the run's name, its agent, its dials and its values, and all
    four are right in either case. The status word here never says that a
    mark stopped the run, and the banner is the one for a halt, which is
    empty for a run that has not stopped. Only the run's own panel writes
    those two, and it is given this value only on a halt
    (`RunView.show_halt`).

    Nothing here builds a compartment value. One of the halts this function
    shows is the refusal of a compartment value, and showing that halt must
    not raise the same refusal again (`PL-7DJK`).

    The values are `kept.values`, the ones the last frame drew, while the
    run is still the one that frame drew. When the run has started over
    since, they are withheld. After a step whose accounting failed its
    check, the accounting panel shows that step's check, which the record
    carries. The clock's playback line is taken from `state` whether the
    values are kept or withheld, because a reader can change the rate on a
    halted run (`PL-P58M`).

    Args:
        record: `SimulationController.record()`.
        adjustments: `record.control_timeline` grouped into acts.
        state: What the run's panel holds.
        kept: The values of the last frame that drew.

    Returns:
        The presentation, with its values kept or withheld.
    """

    started_over = kept.case != state.case

    if started_over:
        standing = ValuesStanding.WITHHELD
        values = withheld_values(state.playback_rate)
    else:
        standing = ValuesStanding.KEPT
        values = replace(
            kept.values, readouts=_at_playback_rate(kept.values.readouts, state.playback_rate)
        )

    if record.rejected_accounting is not None:
        values = replace(values, accounting=rejected_step_accounting(record.rejected_accounting))

    return _presentation(
        record,
        adjustments,
        state,
        banner=halt_run_notice(
            record,
            state.rejected_setting_notice,
            refused_reset=state.refused_reset_notice,
            branch_offered=state.branch_offered,
            started_over=started_over,
            charts_withheld=state.charts_withheld,
        ),
        # Every halt shown from this value has failed the run or stopped it at
        # the supported run length, and both of those status words outrank a
        # mark's. Whether a mark stopped the run is worked out from the
        # compartment states, which this function does not build. A run that
        # has not stopped can be standing on a mark, but only the run's own
        # panel shows the status word from this value, and only on a halt.
        stopped_on_mark=False,
        standing=standing,
        values=values,
        new_case=None,
        reset_question=None,
    )


def _compared_banner(banner: Notice | None, run_name: str | None) -> Notice | None:
    """Return the banner with its text naming the run while a second run is drawn.

    The emphasis is the banner's own, so naming the run never changes its
    colour. A run with nothing to say keeps no banner, named or not. The
    topic is the unnamed banner's, so a banner that stands while a branch is
    taken or closed is not read to a screen reader again (`PL-J7Z5`).
    """

    if banner is None:
        return None

    return replace(
        banner,
        text=compared_run_notice(banner.text, run_name),
        topic=banner.text if banner.topic is None else banner.topic,
    )


def _at_playback_rate(
    kept: tuple[Readout, ...], playback_rate: PlaybackRate, delivered_fraction: float | None = None
) -> tuple[Readout, ...]:
    """Return readouts with the clock's playback line restated at `playback_rate`.

    `delivered_fraction` is as `dashboard_frame.clock_playback_line` takes it.
    """

    return tuple(
        replace(readout, secondary=clock_playback_line(playback_rate, delivered_fraction))
        if panel.is_clock
        else readout
        for panel, readout in zip(READOUT_PANELS, kept, strict=True)
    )


def _presentation(
    record: RunRecord,
    adjustments: Sequence[ControlAdjustment],
    state: RunPanelState,
    *,
    banner: Notice | None,
    stopped_on_mark: bool,
    standing: ValuesStanding,
    values: RunValues,
    new_case: NewCaseQuestion | None,
    reset_question: NewCaseQuestion | None,
) -> RunPresentation:
    """Build the presentation's run-state parts from `record`, around `values`.

    An exception raised while building the dials, the delivered line or
    the 1 MAC line is returned in that part. So a halt is still shown when
    one of them cannot be built from the record. The delivered line is then
    the withheld one, so that no earlier run's setting stays on screen
    (`PL-SV2Q`).
    """

    statement = run_statement(
        record,
        adjustments,
        is_branch=state.is_branch,
        comparing=state.comparing,
        banner=banner,
        stopped_on_mark=stopped_on_mark,
    )
    dials: tuple[SettingReadout, ...] | NotBuilt
    one_mac: str | NotBuilt

    try:
        dials = setting_readouts(record)
        line = _delivered_line(dials)
    except Exception as error:
        dials = NotBuilt(error)
        line = WITHHELD_DELIVERED_LINE_TEXT

    try:
        one_mac = format_mac_reference(
            record.agent_display_name,
            record.agent_mac_percent,
            age_years=record.agent_mac_age_years,
        )
    except Exception as error:
        one_mac = NotBuilt(error)

    return RunPresentation(
        run_id=state.run_id,
        name=state.name,
        case=state.case,
        record=record.run_record(),
        statement=statement,
        notice=_compared_banner(statement.banner, state.name),
        failure_details=failure_details(
            record.run_record(),
            failure_log_path(),
            run_name=state.name,
            refused_reset_reason=state.refused_reset_reason,
        ),
        one_mac=one_mac,
        standing=standing,
        values=values,
        dials=dials,
        delivered_line=line,
        new_case=new_case,
        reset_question=reset_question,
    )


def _delivered_line(dials: tuple[SettingReadout, ...]) -> str:
    """Return the delivered concentration's line from the delivered dial's readout."""

    (delivered,) = (dial for dial in dials if dial.control is ControlInput.DELIVERED)

    return delivered_line(delivered)


@dataclass(frozen=True, slots=True)
class ShownFrame:
    """What one chart window shows on one tick: a frame drawn now, a kept frame, or none.

    Attributes:
        standing: Where `frame` came from. `DRAWN`: it was assembled this
            tick. `KEPT`: no frame can be drawn, and every displayed run is
            still the run that the last drawn frame was assembled from.
            `WITHHELD`: no frame can be drawn, and a run has started over, or
            the runs changed, since the last drawn frame.
        frame: The frame to show. None when the frame is withheld. Also None
            when it is kept but the last drawn frames held none for this
            window, such as a window chosen while every frame fails. The
            chart then keeps the plot it holds, which shows another window
            under a control that names that window (`PL-G3K7`).
        selection: The compartment selection that `frame` was assembled
            from, which the legend shows. For a withheld frame it is the
            selection in force.
    """

    standing: ValuesStanding
    frame: ChartFrame | None
    selection: CompartmentSelection


@dataclass(frozen=True, slots=True)
class KeptFrames:
    """The frames of the last tick that drew, and which runs and cases they were assembled from.

    Attributes:
        cases: Each run the frames were assembled from, in drawing order, as
            its `run_id` and its `RunPresentation.case`.
        selection: The compartment selection the frames were assembled from.
        frames: The frame drawn for each window.
    """

    cases: tuple[tuple[RunId, int], ...]
    selection: CompartmentSelection
    frames: Mapping[ChartWindow, ChartFrame]


def run_cases(runs: Sequence[RunPresentation]) -> tuple[tuple[RunId, int], ...]:
    """Return which runs these are, and how often each had started over, in drawing order."""

    return tuple((run.run_id, run.case) for run in runs)


def kept_frames(
    frames: Mapping[ChartWindow, ChartFrame],
    runs: Sequence[RunPresentation],
    selection: CompartmentSelection,
) -> KeptFrames:
    """Return the frames that a tick drew, to keep for a tick that draws none.

    Args:
        frames: The frame drawn for each window.
        runs: The presentations built from the snapshots the frames were
            assembled from, one for each run the frames draw, in drawing order.
        selection: The compartment selection the frames were assembled from.
    """

    return KeptFrames(run_cases(runs), selection, MappingProxyType(dict(frames)))


def kept_on_a_halt(kept: KeptFrames | None) -> KeptFrames | None:
    """Return the kept frames that a halt may go on showing, or None where it may show none.

    A frame drawn while a reader held a dial carries that run's preview: the
    trajectory the run would take under the setting being dragged. A halted
    run refuses every setting, so after the halt the preview predicts a
    future that cannot happen. The frame is assembled with the preview's
    window, so the preview cannot simply be left out of it. So every frame
    is dropped, each chart is withheld, and the banner says so (blind review
    of `PL-RF2S`, pass 3).

    Args:
        kept: The frames of the last tick that drew, or None.
    """

    if kept is None:
        return None

    if any(run.preview is not None for frame in kept.frames.values() for run in frame.runs):
        return None

    return kept


def kept_frames_match(kept: KeptFrames | None, cases: tuple[tuple[RunId, int], ...]) -> bool:
    """Whether the kept frames were drawn from these runs, in this order, with none started over.

    `shown_without_a_frame` keeps a chart's last frame only when this
    returns True, and a halt's banner says that the charts are withheld
    when it returns False (`RunPanelState.charts_withheld`). So the banner
    and the charts are decided by one rule.

    Args:
        kept: The frames of the last tick that drew, or None when no frame
            has been drawn for the runs the Views show.
        cases: Each run the charts show now, in drawing order, as its
            `run_id` and how often it has started over (`run_cases`).
    """

    return kept is not None and kept.cases == cases


def shown_drawn(frame: ChartFrame, selection: CompartmentSelection) -> ShownFrame:
    """Return a frame drawn this tick, from `selection`, as a chart shows it."""

    return ShownFrame(ValuesStanding.DRAWN, frame, selection)


def shown_without_a_frame(
    kept: KeptFrames | None,
    window: ChartWindow,
    runs: Sequence[RunPresentation],
    selection: CompartmentSelection,
) -> ShownFrame:
    """Return what one chart window shows on a tick that draws no frame.

    The last drawn frame is kept while it describes the runs as they stand:
    the same runs, in the same order, and none started over since
    (`RunPresentation.case`). Otherwise it is withheld. A frame drawn before
    a Reset or an agent change shows the discarded run's traces, and after an
    agent change its 1 MAC line and MAC-awake band are the old agent's. A
    frame drawn before a run was removed shows that run's traces and names it
    in the legend. So in both cases no part of it may stay on the plot.

    Args:
        kept: The frames of the last tick that drew, or None when no frame
            has been drawn for the runs the Views show.
        window: The window the chart asks for.
        runs: The presentations of the runs the chart shows now, in drawing
            order.
        selection: The compartment selection in force.

    Returns:
        The kept frame for `window`, or a withheld one.
    """

    if kept is None or not kept_frames_match(kept, run_cases(runs)):
        return ShownFrame(ValuesStanding.WITHHELD, None, selection)

    return ShownFrame(ValuesStanding.KEPT, kept.frames.get(window), kept.selection)
