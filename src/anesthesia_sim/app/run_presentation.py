"""Everything one run's panel shows at one moment, as one value that one call writes.

`RunView.show_presentation` is the only code that writes a run's widgets, and it writes all
of them from one `RunPresentation`. Two functions here build that value, and
neither loads a GUI toolkit. `drawn_run` builds it from the snapshot that a
frame drew from. `halted_run` builds it from the run's record when no frame
can be drawn. `tests/unit/test_run_presentation.py` tests both with no widget.

Before this module, a frame and a halt each wrote the widgets themselves, and
each wrote a different part of them. A value that the halt left out stayed on
screen from the run before, under a heading that named the run after it. Four
fixes each added the missed widget to the halt, and to a test's list of
widgets (`PL-X7D5`, `PL-J5GC`, `PL-5JTH`, `PL-GTH6`). The next widget was
missed in the same way (`PL-B8DL`, `PL-0G2P`). Here a halt is not a second
writer. It is a `RunPresentation` whose values are kept or withheld, and
`RunView.show_presentation` writes it exactly as it writes a drawn one (`PL-RF2S`).

**A halt keeps or withholds the values that only a frame can compute.** The
readouts, the schematic, the delivered agent and the accounting panel are
compartment values, and a halt builds none, because the halt may be the
refusal of one of them (`PL-7DJK`). `RunValues` holds the four together.
`halted_run` returns the `RunValues` of the last frame that drew, unless the
run has started over since that frame. Then the kept values describe a run
that was discarded, and `halted_run` returns `withheld_values` in their place.
All four are kept or withheld as one value, so no one of them can be left
behind.
"""

from collections.abc import Sequence
from dataclasses import dataclass, replace
from enum import StrEnum

from anesthesia_sim.app.agent_cost import WITHHELD_DELIVERED, DeliveredShown, delivered_shown
from anesthesia_sim.app.compartment_schematic import (
    WITHHELD_SCHEMATIC,
    SchematicShown,
    schematic_shown,
)
from anesthesia_sim.app.control_record import ControlInput
from anesthesia_sim.app.control_timeline import ControlAdjustment
from anesthesia_sim.app.controller import RunRecord, SimulationSnapshot
from anesthesia_sim.app.dashboard_frame import (
    READOUT_PANELS,
    WITHHELD_ACCOUNTING,
    Accounting,
    NewCaseQuestion,
    Readout,
    RunStatement,
    SettingReadout,
    accounting,
    compared_run_notice,
    delivered_line,
    halt_notice,
    new_case_question,
    notice,
    readouts,
    rejected_step_accounting,
    run_statement,
    setting_readouts,
    withheld_readouts,
)
from anesthesia_sim.app.formatting import format_mac_reference, format_playback_rate
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
            the last frame that drew. Each value is replaced by a mark that
            keeps its unit.
    """

    DRAWN = "drawn"
    KEPT = "kept"
    WITHHELD = "withheld"


@dataclass(frozen=True, slots=True)
class RunValues:
    """The compartment values of one run at one instant: everything only a frame can compute.

    The four are built together from one snapshot, kept together, and
    withheld together. So the readouts, the schematic, the delivered agent
    and the accounting panel always describe the same state of the same run
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
        refused_reset_notice: The notice for a Reset the run refused, or None.
        pending_agent_name: The agent that an open new-case question
            proposes, or None while no such question is open.
    """

    run_id: RunId
    name: str | None
    case: int
    playback_rate: PlaybackRate
    is_branch: bool
    comparing: bool
    branch_offered: bool
    rejected_setting_notice: str | None
    refused_reset_notice: str | None
    pending_agent_name: str | None


@dataclass(frozen=True, slots=True)
class RunPresentation:
    """Everything one run's panel shows at one moment.

    Attributes:
        run_id: The run the values belong to.
        name: What the run is called while a second run is drawn, or None.
        case: `RunPanelState.case` when this presentation was built.
        record: The run's record that this presentation states.
            `RunView.owes_a_frame` compares it with the controller's record.
        statement: The run-state widgets: the agent, the status word, the
            transport and the control-change panel.
        notice: The banner's text, naming the run while a second run is
            drawn, or None for no banner.
        one_mac: The line stating 1 MAC of the running agent, or why it
            could not be built. 1 MAC is the divisor of every ×MAC number in
            `values` and `dials`.
        standing: Where `values` came from.
        values: The compartment values.
        dials: The four setting controls, or why they or the delivered line
            could not be built.
        delivered_line: The delivered concentration's line beside the 1 MAC
            line, or None when `dials` holds no controls.
        new_case: The open new-case question, restated for the snapshot this
            presentation was drawn from. It is None when no such question is
            open, and on a halt. A halted run does not step, so the figures
            in the question from the last frame are still correct.
    """

    run_id: RunId
    name: str | None
    case: int
    record: RunRecord
    statement: RunStatement
    notice: str | None
    one_mac: str | NotBuilt
    standing: ValuesStanding
    values: RunValues
    dials: tuple[SettingReadout, ...] | NotBuilt
    delivered_line: str | None
    new_case: NewCaseQuestion | None


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
    new_case = (
        None
        if state.pending_agent_name is None
        else new_case_question(snapshot, state.pending_agent_name, len(adjustments))
    )

    return _presentation(
        snapshot,
        adjustments,
        state,
        banner=notice(
            snapshot,
            state.rejected_setting_notice,
            refused_reset=state.refused_reset_notice,
            branch_offered=state.branch_offered,
        ),
        stopped_on_mark=snapshot.stopped_on_mark,
        standing=ValuesStanding.DRAWN,
        values=values,
        new_case=new_case,
    )


def halted_run(
    record: RunRecord,
    adjustments: Sequence[ControlAdjustment],
    state: RunPanelState,
    kept: KeptValues,
) -> RunPresentation:
    """Return what a run's panel shows for a stopped run when no frame can be drawn.

    Nothing here builds a compartment value. One of the halts this function
    states is the refusal of a compartment value, and stating that halt must
    not raise the same refusal again (`PL-7DJK`).

    The values are `kept.values`, the ones the last frame drew, while the
    run is still the one that frame drew. When the run has started over
    since, they are withheld. After a step whose accounting failed its
    check, the accounting panel shows that step's check, which the record
    carries. The clock's playback line is restated from `state` in either
    case, because a reader can change the rate on a halted run (`PL-P58M`).

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
        banner=halt_notice(
            record,
            state.rejected_setting_notice,
            refused_reset=state.refused_reset_notice,
            branch_offered=state.branch_offered,
            started_over=started_over,
        ),
        # Every halt stated here has failed the run or stopped it at the
        # supported run length, and both of those status words outrank a
        # mark's. Whether a mark stopped the run is worked out from the
        # compartment states, which this function does not build.
        stopped_on_mark=False,
        standing=standing,
        values=values,
        new_case=None,
    )


def _at_playback_rate(
    kept: tuple[Readout, ...], playback_rate: PlaybackRate
) -> tuple[Readout, ...]:
    """Return kept readouts with the clock's playback line restated at `playback_rate`."""

    return tuple(
        replace(readout, secondary=format_playback_rate(playback_rate.multiplier))
        if panel.quantity is None
        else readout
        for panel, readout in zip(READOUT_PANELS, kept, strict=True)
    )


def _presentation(
    record: RunRecord,
    adjustments: Sequence[ControlAdjustment],
    state: RunPanelState,
    *,
    banner: str | None,
    stopped_on_mark: bool,
    standing: ValuesStanding,
    values: RunValues,
    new_case: NewCaseQuestion | None,
) -> RunPresentation:
    """Build the presentation's run-state parts from `record`, around `values`.

    An exception raised while building the dials, the delivered line or
    the 1 MAC line is returned in that part. So a halt whose record refuses
    one of them is still stated.
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
    line: str | None
    one_mac: str | NotBuilt

    try:
        dials = setting_readouts(record)
        line = _delivered_line(dials)
    except Exception as error:
        dials = NotBuilt(error)
        line = None

    try:
        one_mac = format_mac_reference(record.agent_display_name, record.agent_mac_percent)
    except Exception as error:
        one_mac = NotBuilt(error)

    return RunPresentation(
        run_id=state.run_id,
        name=state.name,
        case=state.case,
        record=record.run_record(),
        statement=statement,
        notice=compared_run_notice(statement.banner, state.name),
        one_mac=one_mac,
        standing=standing,
        values=values,
        dials=dials,
        delivered_line=line,
        new_case=new_case,
    )


def _delivered_line(dials: tuple[SettingReadout, ...]) -> str:
    """Return the delivered concentration's line from the delivered dial's readout."""

    (delivered,) = (dial for dial in dials if dial.control is ControlInput.DELIVERED)

    return delivered_line(delivered)
