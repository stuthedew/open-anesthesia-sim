"""The simulation controller, which is the boundary between the user interface and the core.

`SimulationController` owns the run, pause and reset state. It applies the settings a user
chooses to the scientific core, and it exposes read-only `SimulationSnapshot`s for the view
to render. It performs no physiological calculations of its own and holds no default values
of its own. Every setting the user has not specified comes from the core, which builds it
from the versioned data files.

The vocabularies used to *address* a run are not defined here. This module imports them like
any other dependency. `app/control_record.py` defines what a run can be set to and what a
setting change records. `app/run_series.py` defines what a trace names and what one drawn
frame reads (`PL-RD3B`). Neither module imports this one, so code that reads either of them
does not also depend on the controller.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, fields, replace
from math import isfinite

from anesthesia_sim.app.bookmarks import (
    BookmarkCrossing,
    BookmarkSet,
    BookmarkStandings,
    MacTarget,
    MarkStanding,
    TimeBookmark,
)
from anesthesia_sim.app.control_record import CONTROL_INPUT_UNITS, ControlChange, ControlInput

# This module imports `mac_multiple` rather than writing an inverse transform here,
# and the import matters. `mac_multiple` contains the whole arithmetic of the second
# display unit in one place. So a target held in multiples of MAC is compared with a
# compartment through the same divisor through which the readout beside it is drawn. Converting
# the *target* down into a partial-pressure fraction here would make a second copy of
# that arithmetic. `CLAUDE.md` treats a correct number reached through the wrong
# divisor as a safety failure, not a rounding error. This module uses nothing else
# from `app/formatting.py`, because it builds no strings.
from anesthesia_sim.app.formatting import mac_multiple
from anesthesia_sim.app.run_series import (
    COMPARTMENT_FRACTION_NAMES,
    COMPARTMENT_STATE_INDEX,
    DrawnWindow,
    RecordedQuantity,
)
from anesthesia_sim.core.concentration import (
    Fraction,
    MacMultiple,
    MacPercent,
    Percent,
    fraction_from_percent,
)
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
)
from anesthesia_sim.core.governing_equations import (
    TissueGroupEquationSettings,
    UptakeEquationSettings,
)
from anesthesia_sim.core.numerical_envelope import CompartmentVolume
from anesthesia_sim.core.parameters import MacAwakeReference, load_agent_parameters
from anesthesia_sim.core.run_definition import Keyframe, RunDefinition, RunSegment
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import SimulationStep
from anesthesia_sim.core.supported_ranges import (
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
    StepCount,
    require_case_instant,
    require_supported_run_length,
)
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


@dataclass(frozen=True, slots=True)
class RunStatus:
    """Whether the run is advancing and, if not, why: the three facts that describe a halt.

    `SimulationController.status()` builds one from the controller's own
    run-state fields and the run-length guard. It builds no compartment
    value, so a caller can read it for a run whose `snapshot()` raises.
    `RunView.present_halt` needs that, because the snapshot's own
    `Fraction`s are among the values that can cause a halt (`PL-7DJK`).
    `RunSettings` extends this class, and `SimulationSnapshot` extends
    `RunSettings`. So `dashboard_frame.status_word`, `transport` and
    `notice` accept any of the three, and a frame that drew reads the three
    facts from the snapshot it drew from.
    """

    is_running: bool
    """Whether the run is advancing. `False` for a pause and for both halts."""
    supported_limit_reason: str | None
    """Why the run is stopped at a declared limit of the model's domain, or
    `None` if it is not.

    A non-`None` value means the run is at the supported run length, where
    the core would reject the next step. The run may have stepped there,
    been forked there, or been reset to a fork there (`PL-5291`).
    `is_running` is `False`, but this state is neither a pause nor a
    failure. Nothing was miscalculated and no step was rolled back. Every
    value in the snapshot comes from a completed step, at a simulated time
    inside the supported span. What has ended is the claim that a further
    step would represent a patient.

    This field is separate from `failure_reason` because the interface must
    not present the two states alike. If the simulator stopped exactly where
    `docs/MODEL.md` says it should, telling a reader that it broke would
    misrepresent a correct model as a defective one. The reverse mistake
    would be worse. Both fields are `None` for a run that is merely paused.
    """
    failure_reason: str | None
    """Why the run stopped abnormally, or `None` if it did not.

    A non-`None` value means that a step, a setting, or a value the
    interface built raised an error, and the session is halted.
    `is_running` is `False`, but this state is not the same as a user
    pause, and the interface must not present it as one.

    Every other field in the snapshot still comes from a completed step.
    `AgentUptakeSystem.advance()` rolls a failed step back, and elapsed
    time advances only after that call returns. So a halted session reports
    the last step that finished, at the simulation time it finished at,
    rather than a step abandoned partway through.
    """


@dataclass(frozen=True, slots=True)
class RunSettings(RunStatus):
    """The agent and the four settings in force on the run, which the setting controls show.

    `SimulationController.settings()` builds one from the agent the run was
    given and the settings its compartments hold. Each value is a checked
    type, a string the controller holds, or one of the accepted range's two
    floats. It builds no compartment value, so like `RunStatus` it can be
    read for a run whose `snapshot()` raises. `dashboard_frame.setting_readouts`
    accepts it, and that lets `RunView.present_halt` write every dial from
    the values the run holds. Without it, a dial dragged into a halt kept
    the value from before the drag printed beside it, because no frame
    followed to rewrite it (`PL-85LJ`). `RunRecord` extends this class, and
    `SimulationSnapshot` extends `RunRecord`, so a frame that drew reads the
    settings from the snapshot it drew from.
    """

    agent_id: str
    agent_display_name: str
    max_delivered_concentration_percent: Percent
    agent_mac_percent: MacPercent
    """The running agent's 1 MAC, as a percent of one atmosphere.

    Exposed because the interface displays every compartment in multiples
    of it as well as in percent, so it is the divisor of a clinically
    meaningful displayed value rather than only the starting position of
    the vaporizer dial. It travels in the snapshot, beside the
    concentrations it scales and the agent it belongs to, so a readout
    cannot be produced from one agent's concentration and another agent's
    MAC — which would be the correct number under the wrong label that
    `CLAUDE.md` treats as a safety failure.

    `docs/MODEL.md` § "MAC multiples as a display unit" states what the
    quotient asserts, and § "Delivery-limit and MAC parameters" holds the
    value's provenance.
    """
    fresh_gas_flow_l_min: FreshGasFlow
    accepted_fresh_gas_flow_range_l_min: tuple[float, float]
    """The lowest and highest fresh gas flow this run's circuit accepts, in L/min.

    The value is `BreathingCircuit.accepted_fresh_gas_flow_range_l_min`, read
    from the circuit in force. It is the model's envelope narrowed to the
    declared range of the mounted machine. It travels beside the flow for the
    same reason that `max_delivered_concentration_percent` travels beside the
    dial. The control that offers the setting reads its bounds from here, so
    it offers no flow that this machine rejects (`PL-7CRY`).
    """
    delivered_concentration_percent: Percent
    alveolar_ventilation_l_min: AlveolarVentilation
    cardiac_output_l_min: CardiacOutput

    @property
    def delivered_partial_pressure_fraction(self) -> Fraction:
        """The delivered fraction of an atmosphere, derived from the percent dialled.

        The snapshot carries the dial as the circuit holds it, which is the
        percent it was set to. So the dial is drawn from the value that was
        dialled, not from a fraction multiplied back to a percent (`PL-NJPB`).
        """

        return fraction_from_percent(self.delivered_concentration_percent)


@dataclass(frozen=True, slots=True)
class RunRecord(RunSettings):
    """The run's settings and every change made to them.

    Like `status()` and `settings()`, `SimulationController.record()` builds
    one without computing any compartment value. So it can be read for any
    run on every render tick, which is its purpose. `SimulationView.render_tick`
    draws a frame whenever a displayed run's record differs from the one its
    view last wrote. A run can change without anything asking for a frame,
    for example when it halts on a mark or reaches the supported run length
    inside `RunView.step_tick`. Such a run is redrawn on the next tick, and
    that code path does not have to remember to ask (`PL-X7D5`, `PL-T995`).
    `SimulationSnapshot` extends this class, so a frame that drew states the
    record it drew from.
    """

    control_timeline: tuple[ControlChange, ...]
    """Every setting change this run has seen, oldest first.

    Empty for a run nobody has touched, and cleared with the rest of the
    run by `reset()` and by a change of agent. A setting the core refused
    is absent: it never took effect, so it is not part of the run.
    """

    def run_record(self) -> RunRecord:
        """Return this record as a plain `RunRecord`, without any field a subclass adds.

        Dataclass equality compares only instances of the same class, so a
        snapshot never equals the record it extends. A view stores the result
        to compare with `SimulationController.record()` later.
        """

        return RunRecord(**{field.name: getattr(self, field.name) for field in fields(RunRecord)})


@dataclass(frozen=True, slots=True)
class SimulationSnapshot(RunRecord):
    """Read-only simulation data exposed to the user interface.

    A `RunRecord` with everything else the interface draws. The inherited
    fields come first: the run state, the settings and the setting changes.
    The rest follow. Only `SimulationController.snapshot()` builds one in
    `src/`, and it passes every field by keyword, so no caller relies on the
    field order.
    """

    elapsed_s: CaseInstant
    began_at_s: CaseInstant
    """The case instant at which this run began: zero on a trunk, the fork on a branch.

    It is on the case's own time axis, like `elapsed_s`, and it is the value
    that `SimulationController.began_at_s` returns. It travels beside the
    elapsed time it bounds because `has_recorded_run` reads the two together.
    A branch is built already standing at its fork, so an elapsed time above
    zero says nothing about whether anyone has touched it (`PL-7TBQ`).
    """
    agent_mac_awake: MacAwakeReference
    """The running agent's population MAC-awake, as a fraction of its MAC.

    It travels as one object rather than as two loose floats. It travels
    beside `agent_mac_percent` for the reason that field gives. The chart's
    reference band is `fraction_of_mac` times that divisor, so pairing one
    agent's MAC-awake with another agent's MAC would draw a correct number
    at the wrong height on a labelled axis.

    The interface reads this value, and `core/` does not. No governing
    equation uses MAC-awake, just as none uses `mac_percent`. `docs/MODEL.md`
    § "MAC-awake as a chart reference" states what the band asserts, which
    trace it is read against, and why it is not a time to wake-up.
    """
    circuit_volume_l: CompartmentVolume
    # The six compartment values below all belong to the agent `agent_id`
    # names. They are flat named floats rather than a mapping keyed by
    # substance, which is the shape the recorded run took at `PL-W3DD`. The
    # difference is deliberate, not unfinished (`PL-TCD1`, decided 2026-09-13).
    #
    # `ROADMAP.md` § "Designed for forking" already drew the line and named
    # this structure on the declined side of it: "What is deliberately *not*
    # designed for in advance: per-compartment agent amounts in the snapshot
    # ... The distinction is whether retrofitting invalidates recorded runs or
    # merely adds a field." A snapshot is one instant's transient state, so
    # reshaping it when a second substance arrives invalidates nothing. The
    # recorded row was the opposite case and was rightly reshaped first.
    #
    # What was actually wrong was that a frame described the run in two
    # vocabularies. The chart named the substance it drew, and the numbers
    # beside it did not. The fix is to name the substance in both places.
    # These values travel with `agent_id` and `agent_display_name` above, for
    # the same reason `agent_mac_percent` does. `dashboard_frame.substance_heading`
    # labels the readout row with the substance, and `run_view` places that
    # label, so a reader does not have to carry it over from the agent selector.
    #
    # When the model holds N substances present at the same time (`ROADMAP.md`
    # Phase 1, ahead of planned item 6), a mapping is the right shape, and it
    # replaces this block.
    inspired_partial_pressure_fraction: Fraction
    alveolar_partial_pressure_fraction: Fraction
    mixed_venous_partial_pressure_fraction: Fraction
    vessel_rich_partial_pressure_fraction: Fraction
    muscle_partial_pressure_fraction: Fraction
    fat_partial_pressure_fraction: Fraction
    delivered_agent_l: float
    exhausted_agent_l: float
    stored_agent_l: float
    unaccounted_agent_l: float
    agent_accounting_absolute_error_l: float
    agent_accounting_passes_validation: bool
    bookmarks: BookmarkSet
    """The instants and the heights this run is marked at, in two collections.

    This field is the opposite kind of thing to `control_timeline`, which
    `RunRecord` carries. The timeline records what was done to the run. This
    field is the set of questions still being asked of the run. Nothing here
    has happened yet, and nothing here changes a run.

    The bookmarks survive events that clear the timeline. `reset()` and
    `set_agent` both keep them, for the same reason they keep the settings,
    and a branch opens with a copy of its trunk's bookmarks. `app/bookmarks.py`
    gives the argument for each case. Whether a run has *reached* a mark is
    the subject of `PL-CTD7`, and this field does not report it.
    """
    bookmark_halt: BookmarkCrossing | None
    """The marks the run is halted on, or `None` if it is not halted on any.

    It is set on the step that crossed the marks and cleared by the run's
    next step, so a reader sees it exactly while the run stands on the
    crossing. `is_running` is `False` alongside it, and the state is an
    ordinary pause. Start resumes the run, and resuming does not count the
    crossing it halted on again (`MacTarget.crossed_between`).

    `instant_s` is the completed step's own instant. So it lies on the run's
    `simulation_step_s` grid, not on the coarser grid that a tick boundary
    can reach. That precision is the whole of what `PL-CTD7` provides, and
    `docs/MODEL.md` § "Halting on a marked crossing" states it.
    """
    bookmark_standings: BookmarkStandings
    """Where the run stands on each mark in `bookmarks`, keyed by the mark.

    This is the other half of the question that `bookmarks` asks. That field
    holds what the learner marked, and this one holds where the run stands
    on each mark. There are five possible results rather than two. "Not
    reached", "not reached yet" and "already behind the clock" are different
    claims, and a row that merged them would tell a learner to wait for
    something that cannot arrive. `bookmarks.MarkStanding` gives the argument
    for each result. It also explains why a marked instant and a marked height
    are described in different words.
    """

    @property
    def has_recorded_run(self) -> bool:
        """Whether this run holds anything that starting over would destroy.

        True once the run has advanced past its own beginning or has recorded
        a setting change. False for a run that has been built and not yet
        touched, which is the state that a fresh session, a fresh branch and
        `reset()` all leave.

        It exists so that the interface can tell a destructive act from a
        harmless one. `set_agent` always begins a new run. Where there is a run
        to lose, that cannot be undone. Where there is none, it changes nothing.
        A confirmation that appeared in both cases would state something untrue
        in the second case. By the time it mattered in the first case, users
        would have learned to answer it without reading.

        Elapsed time and the timeline are read together because either alone
        misses a case. A run paused at its opening instant with the vaporizer
        already turned has a recorded input and no elapsed time. A run advanced
        with nothing touched has the reverse.

        **Elapsed time counts from `began_at_s`, not from zero** (`PL-7TBQ`).
        A branch uses the case's clock, so it opens at its fork with
        `elapsed_s` already past zero. When elapsed time was compared with
        zero, every branch held a run to lose from the moment it was made, and
        again after every reset. The comparison is exact at the fork. The
        branch's clock is its step count times its step length. Every way of
        creating a fork rejects an instant that is not a whole number of steps,
        so the clock stands exactly on the fork instant.
        """

        return self.elapsed_s > self.began_at_s or bool(self.control_timeline)


@dataclass(frozen=True, slots=True)
class ResumePoint:
    """Everything a branch needs in order to have opened where it did.

    These seven values mean something only together. So they travel as one
    object, not as seven attributes that a later edit could set one at a
    time. `RunSegment` makes the same argument about its own two halves. A
    branch rebuilt from six of these values and a stale seventh would open
    at a state its settings never produced, or on an accounting period that
    never happened.

    `SimulationController.reset()` also reads this object. Reset returns a
    run to its own beginning. A branch begins at the fork, not at the case's
    induction, which the branch does not hold and cannot recover.

    **`fork` and `segment.opening` are two instants, not one** (`PL-B8MK`).
    They coincide for a fork taken at a control event. That was the only
    kind of fork before bookmarks could halt a run. A control event *is* a
    keyframe, so the stretch the branch opened inside begins exactly where
    the branch does. A bookmark's instant need not be a keyframe, and
    recording a keyframe there would change the trunk's own later results.
    So a bookmark fork opens its run definition at the keyframe where the
    parent's stretch begins, while the branch stands at the fork itself.
    Both are instants on the case's own time axis, the single axis left by
    `PL-ZMRT`. What is no longer true is that they are equal.

    Attributes:
        segment: The parent stretch this branch opened inside, carrying both
            the settings in force and the keyframe they start from. That
            keyframe is where the branch's own run definition opens, which is
            at or before the fork.
        fork: The instant at which the branch was taken, and the canonical
            state the parent held there. For a fork at a control event, this
            is the parent's own keyframe. For a fork at a bookmark, it is one
            propagation from that keyframe. Its instant is where the branch
            began. The branch's clock and its live system stand there, a
            reset returns there, and `drawn_window` stops drawing there on
            the left.
        step_count: How many steps the case had completed at the fork, so
            that the branch's clock continues the case's clock rather than
            restarting. `docs/MODEL.md` § "Supported run length" is measured
            against this count.
        simulation_step_s: The step length the case has used, or `None` for
            a fork from a run that has not stepped. A branch keeps its
            parent's step length, and `SimulationState` rejects a different
            one.
        accounting_anchor_l: The amount of agent present when the *case's*
            accounting period started. It is carried rather than derived
            again, and `AgentUptakeSystem.resume_at` explains why deriving
            it is unsafe.
        stepped_from: The instant one step before the fork and the parent's
            canonical state there, or `None` for a fork at the case's
            opening, where no step ends. Together with `fork`, it gives the
            step that the branch is standing on when it opens. Each time the
            branch's standings are read, the branch asks that step which marks
            it crossed, using the marks as they are at that moment. So a mark
            added after the fork is treated as it would have been had it
            existed before the fork (`PL-1ZQ4`). The parent's state is stored
            here because the branch cannot evaluate it. A branch taken at a
            control event opens its run definition at the fork, which is
            after this instant.
        crossing: What the step ending at the fork crossed, checked against
            the marks as they were when the fork was taken. It is `None` when
            the step crossed no mark or when no step ends at the fork. Every
            way of opening a branch computes it in the same way, including a
            fork at a control event (`PL-1ZQ4`, case 3). The branch reports
            that it opened on this crossing (`SimulationSnapshot.bookmark_halt`).
            It is stored here, rather than computed again, for the same reason
            as the other attributes. `_open_at` is the code path of a reset as
            well as of a fork, and a reset puts the branch back on the
            identical record (`PL-3K9B`, case G). The standings do not read
            this attribute. They ask `stepped_from` and `fork` again.
    """

    segment: RunSegment
    fork: Keyframe
    step_count: StepCount
    simulation_step_s: SimulationStep | None
    accounting_anchor_l: float
    stepped_from: Keyframe | None
    crossing: BookmarkCrossing | None


@dataclass(frozen=True, slots=True)
class MarkForkPoint:
    """A marked instant that a run has passed, and the instant where a branch taken there opens.

    These two numbers are in general not equal, which is why they travel
    together (`PL-W4XQ`). A mark that lies inside a step is reached at the
    end of that step. So `bookmark.instant_s` is where the learner placed the
    mark, and `fork_s` is the step instant where a branch stands. For a typed
    45.3 s at the 0.1 s step, they are 45.3 and 45.300000000000004. Code that
    labels the offer reads `fork_s`, the instant the action will use. Code
    that takes the offer passes back `bookmark`, the mark itself. So neither
    has a float to get wrong.

    Attributes:
        bookmark: The mark, as the run holds it.
        fork_s: Where a branch taken at the mark opens. This is the end of
            the step that reaches the mark, `TimeBookmark.steps_to_reach`
            steps into the case.
    """

    bookmark: TimeBookmark
    fork_s: CaseInstant


@dataclass(frozen=True, slots=True)
class HereForkPoint:
    """Where a paused run stands, as a place to branch, and whether a mark stopped it there.

    `SimulationController.here_fork_point` returns this (`PL-Y2SL`). The
    instant is the clock's, and the clock stands on whole steps. So the
    instant shown to a reader and the instant at which `resumed_here` forks
    are the same number. Nothing here is a typed value that a caller could
    get wrong.

    Attributes:
        fork_s: The instant where the run stands, which is where a branch
            taken here opens.
        stopped_on_mark: Whether the run halted here on a marked crossing
            (`SimulationSnapshot.bookmark_halt`) rather than being paused
            here, so that a label can say which.
    """

    fork_s: CaseInstant
    stopped_on_mark: bool


class SimulationController:
    """Own the run controls and the read-only history for one app session."""

    def __init__(
        self,
        agent_id: str = "sevoflurane",
        circuit_volume_l: CompartmentVolume | None = None,
        fresh_gas_flow_l_min: FreshGasFlow | None = None,
        delivered_concentration_percent: Percent | None = None,
        alveolar_ventilation_l_min: AlveolarVentilation | None = None,
        cardiac_output_l_min: CardiacOutput | None = None,
    ) -> None:
        """Build a session, taking every unspecified setting from the core.

        Each argument is an explicit override. `None` means "use the value
        the core built from the versioned data files" — the reference
        patient's cited alveolar ventilation and cardiac output, the
        circuit's own volume and fresh gas flow, and the agent's own 1 MAC.
        The controller holds no copy of those defaults, so correcting a
        cited value in a data file changes what the app actually runs.
        """

        self._is_running = False
        self._failure_reason: str | None = None
        self._failed_frame_reason: str | None = None
        self._recorded_supported_limit_reason: str | None = None
        # These fields record what this run has done with the marks, as opposed
        # to what is marked. Both are the run's product rather than the
        # learner's question. So both are cleared wherever a new run begins:
        # in `_build_state`, which `set_agent` also calls, and in `reset()`.
        # `_bookmarks` below survives all of these. `_stand_on` is the one
        # exception, and it does not carry anything over. A branch opens
        # *standing on* the crossing at which it was forked. That crossing is
        # where the branch is, not something an earlier run did.
        self._bookmark_halt: BookmarkCrossing | None = None
        self._reached_instants_s: frozenset[CaseInstant] = frozenset()
        self._reached_crossings: frozenset[tuple[RecordedQuantity, float]] = frozenset()
        # `_bookmarks` is set here and not in `_build_state`, deliberately.
        # `set_agent` also calls `_build_state`. A mark is the learner's question rather
        # than the run's product, so it outlives the run, as a setting does. A
        # MAC target is held as a multiple of whichever agent is running. So it
        # means the same thing after an agent change as before it, and that is
        # the comparison a learner who changes agent is making.
        self._bookmarks = BookmarkSet()
        self._build_state(
            agent_id=agent_id,
            circuit_volume_l=circuit_volume_l,
            fresh_gas_flow_l_min=fresh_gas_flow_l_min,
            delivered_concentration_percent=delivered_concentration_percent,
            alveolar_ventilation_l_min=alveolar_ventilation_l_min,
            cardiac_output_l_min=cardiac_output_l_min,
        )

    def _forget_reached_marks(self) -> None:
        """Clear what *this run* did with the marks, keeping the marks themselves.

        Called wherever a new run begins. A mark is the learner's question,
        and it survives. Whether a run halted on a mark is that run's product,
        and it does not survive. A standing carried across a reset would
        report a crossing that the run now on screen never made.

        A branch's reset clears these fields here, and then `_open_at` puts
        the branch back on its fork. A fork runs the same sequence. The
        crossing a branch opens on is where the branch stands, not something
        an earlier run did. So that crossing comes back with the state it
        belongs to.
        """

        self._bookmark_halt = None
        self._reached_instants_s = frozenset()
        self._reached_crossings = frozenset()

    def _build_state(
        self,
        agent_id: str,
        circuit_volume_l: CompartmentVolume | None,
        fresh_gas_flow_l_min: FreshGasFlow | None,
        delivered_concentration_percent: Percent | None,
        alveolar_ventilation_l_min: AlveolarVentilation | None,
        cardiac_output_l_min: CardiacOutput | None,
    ) -> None:
        """(Re)build dynamic state from scratch for a chosen agent.

        Every argument is an override applied on top of the state that
        `AgentUptakeSystem.for_agent()` already built from the data files.
        A `None` leaves that data-file value in place, including the
        agent's own 1 MAC delivered concentration. A requested delivered
        concentration above the agent's real vaporizer maximum is rejected
        by the core rather than clamped here.
        """

        agent_parameters = load_agent_parameters(agent_id)
        uptake_system = AgentUptakeSystem.for_agent(agent_id)

        if circuit_volume_l is not None:
            uptake_system.circuit.set_circuit_volume(circuit_volume_l)

        if fresh_gas_flow_l_min is not None:
            uptake_system.set_fresh_gas_flow(fresh_gas_flow_l_min)

        if delivered_concentration_percent is not None:
            uptake_system.set_delivered_concentration_percent(delivered_concentration_percent)

        if alveolar_ventilation_l_min is not None:
            uptake_system.set_alveolar_ventilation(alveolar_ventilation_l_min)

        if cardiac_output_l_min is not None:
            uptake_system.set_cardiac_output(cardiac_output_l_min)

        self._agent_id = agent_id
        self._agent_display_name = agent_parameters.display_name
        self._agent_mac_percent = agent_parameters.mac_percent
        self._agent_mac_awake = agent_parameters.mac_awake
        self._state = SimulationState(uptake_system=uptake_system)
        # The run records one substance, which is this run's agent. `set_agent`
        # calls this method and builds a new history under the new agent's id.
        # So a run's recorded substance is always the one that produced its states.
        self._run_definition = RunDefinition(
            uptake_system.equation_settings(),
            uptake_system.state_vector(),
            opened_at_s=CaseInstant(0.0),
        )
        self._note_recorded_settings()
        # A run built here is a trunk, so it opens at the case's own zero.
        # `resumed_at()` sets this field, and a branch built there opens its
        # run definition at the fork instead. Both are on the same time axis,
        # so nothing here converts between them.
        self._opened_from: ResumePoint | None = None
        self._clear_control_timeline()

        # Every compartment above is newly constructed, so no state survives
        # from a run that failed: a stale failure reason would halt a
        # session that has nothing wrong with it. A stale limit reason would
        # do the same to a run that has taken no steps at all.
        self._failure_reason = None
        self._failed_frame_reason = None
        self._recorded_supported_limit_reason = None

    def _clear_control_timeline(self) -> None:
        """Drop the recorded timeline, for a run that is starting over."""

        self._control_timeline: tuple[ControlChange, ...] = ()
        self._adjustment_count = 0
        self._open_adjustment_control: ControlInput | None = None
        self._open_adjustment = 0

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def has_failed(self) -> bool:
        """Whether the session is halted by a failure rather than paused."""

        return self._failure_reason is not None

    @property
    def agent_id(self) -> str:
        """The agent of this run, read from the run's settings and not from any compartment.

        The snapshot carries the same id. This property is for a caller that
        cannot get the snapshot. `RunView` uses it to set the agent selector
        back to the running agent on a run whose snapshot raises (`PL-V2HC`).
        """

        return self._agent_id

    def fail(self, reason: str) -> None:
        """Halt the session because something raised, recording why.

        This differs from `pause()`, which is a user decision that the run
        resumes from. A failure means that a step or a setting raised. The
        core rolls a failed step back, so the state left behind is the last
        completed step rather than a partial one. Resuming is still not
        offered. The run reached a state from which the model could not step,
        so a resumed run would fail again on its first tick. Offering Start
        would present that as a working control. Only a fresh run clears the
        failure, through `reset()` or `set_agent()`.
        """

        self._is_running = False

        # The first failure is the one that explains the rest, so a later
        # raise (e.g. from the render loop reacting to the same broken
        # state) must not overwrite it.
        if self._failure_reason is None:
            self._failure_reason = reason

    def record_failed_frame(self, reason: str) -> None:
        """Stop the run because the frame it is drawn in raised, recording why.

        The frame is shared by every run on the dashboard, so a raise there is
        attributable to none of them (`SimulationView._halt_every_run`). This
        records that the frame failed. It says nothing about whether the model
        failed, so the interface also calls `fail()` or
        `halt_at_supported_limit()`, as the raise deserves.

        A run with this record offers no branch at all (`PL-T2Q2`). A branch
        opened from it would be drawn by the same frame, beside this run, and
        would halt on the next one. The first reason is kept, as `fail()`
        keeps its own. Only a fresh run clears it, via `reset()` or
        `set_agent()`.

        Args:
            reason: What the frame raised, as `dashboard_frame.halt_disposition`
                words it.
        """

        self._is_running = False

        if self._failed_frame_reason is None:
            self._failed_frame_reason = reason

    @property
    def fork_refusal(self) -> str | None:
        """Why no branch at all may be taken from this run, or None where one may.

        Two reasons rule out every way of taking a branch. Either this run is
        itself a branch, or the frame it is drawn in has failed
        (`record_failed_frame`). Each method that takes a branch raises from
        this same check. So `BranchedCase` offers no fork point while a reason
        is set, and the offer and the methods cannot disagree. A method may
        still reject a particular fork for its own reason, which
        `here_fork_point` and the methods' docstrings name.
        """

        refusal_as_a_branch = self._refusal_as_a_branch()

        if refusal_as_a_branch is not None:
            return refusal_as_a_branch

        if self._failed_frame_reason is not None:
            return (
                f"the frame this run is drawn in failed ({self._failed_frame_reason}), and a "
                "branch would be drawn in the same frame and halt on it; reset the run first"
            )

        return None

    @property
    def has_reached_supported_limit(self) -> bool:
        """Whether the run stands at a declared limit of the model's domain."""

        return self.supported_limit_reason is not None

    @property
    def supported_limit_reason(self) -> str | None:
        """Why the run stands at the supported run length, or `None` if it does not.

        The reason is read from the run itself, never from a flag alone
        (`PL-5291`). A run stands at the limit when the core would reject its
        next step. This property asks the state exactly that, so the reason
        here is the one the rejected step would give, word for word. Three
        routes put a run there: stepping onto the last supported step, a fork
        taken on that step, and a branch reset to such a fork. Only the first
        route ever rejected a step. So a flag set only by the rejection left
        the other two routes looking like an ordinary pause. Start was
        offered, no limit notice appeared, and the marks panel said that an
        unreached mark was still ahead of a run that could not step.

        A reason that `halt_at_supported_limit` recorded takes precedence over
        the derived one, for two reasons. It came first, and the domain limit
        it carries may have been raised on a path that the state cannot be
        asked about.
        """

        if self._recorded_supported_limit_reason is not None:
            return self._recorded_supported_limit_reason

        return self._reason_the_next_step_would_be_refused()

    def _reason_the_next_step_would_be_refused(self) -> str | None:
        """Return the reason `SimulationState.advance` would give for rejecting the next step.

        The result is `None` when the next step would not be rejected.

        This method calls the core's own guard rather than restating its rule.
        So the controller and the stepper cannot disagree about which count is
        the last supported one. `maximum_step_count` decides that once, on the
        product of the count and the step length (`PL-8H2R`). The message is
        the guard's own. A run that has not stepped has no step length to
        measure the span in, so it is at no limit.
        """

        simulation_step_s = self._state.simulation_step_s

        if simulation_step_s is None:
            return None

        try:
            require_supported_run_length(self._state.step_count, simulation_step_s)
        except SimulationDomainLimitError as refusal:
            return str(refusal)

        return None

    def halt_at_supported_limit(self, reason: str) -> None:
        """Stop the run because a raise reached the end of the supported domain.

        This differs from `fail()`, which records that something went wrong,
        and from `pause()`, which the run resumes from. Here nothing went
        wrong, and there is nothing to resume *to*. The core rejected a step
        before taking it. So the run stands on a completed step, at a
        simulated time at which the model is claimed to represent a patient,
        and the next step would be rejected in the same way.

        Resuming is therefore not offered, for the reason `fail()` gives: a
        Start button that does nothing is a control presenting itself as
        working. `reset()` or `set_agent()` starts a new run. The only
        difference from a failure is what the interface says about it, and
        that difference is required, not cosmetic. See
        `SimulationSnapshot.supported_limit_reason`.

        A run that steps onto the limit never needs this method. `advance`
        halts it on the step that arrives there, and `supported_limit_reason`
        reads the limit from the state (`PL-5291`). This method records a
        `SimulationDomainLimitError` that the interface caught on some other
        path, such as a setting change through `run_view.halt`, which the
        state cannot be asked about. The first reason is kept, as in
        `fail()`, so a later raise at the same boundary cannot overwrite the
        one that explains it. For the same reason, it takes precedence over
        the derived reason.
        """

        self._is_running = False

        if self._recorded_supported_limit_reason is None:
            self._recorded_supported_limit_reason = reason

    def set_agent(self, agent_id: str) -> None:
        """Start fresh with a different agent at that agent's own 1 MAC.

        The delivered-concentration fraction is reset to the new agent's
        mac_percent rather than carrying over the old agent's raw percentage,
        since the same percent number corresponds to a different clinical
        depth for each agent (e.g. 2% is 1 MAC of sevoflurane but only about
        a third of a MAC of desflurane). Circuit, flow, ventilation, and
        cardiac output settings are preserved.

        The bookmarks are preserved with them, and the way a MAC target is
        stored makes that safe. A target is held as a multiple of whichever
        agent is running. So 0.8 ×MAC stays 0.8 ×MAC of the new agent, rather
        than becoming the old agent's absolute concentration under a new
        divisor. A learner who changes agent wants to see the same multiple
        reached at a different time. So a target that survives the change is
        the comparison, not a leftover.

        Switching agent mid-run, with accounting for the residual washout, is
        a separate and harder feature (see ROADMAP.md's anesthesia-machine
        milestone). This method never attempts it and always begins a new run.
        Because it begins a new run, it also clears a failed session, the
        same way `reset()` does.

        Because it begins a new run, it also *destroys* the current one, and
        that cannot be undone. The recorded history, the control-input
        timeline and the simulated time the run reached are all lost, and
        nothing here or anywhere else keeps a copy. So a caller must not call
        this method in response to a gesture that looks like choosing a view.
        `docs/MODEL.md` § "Agent-change behavior" states what the interface
        owes a user before this call. `SimulationSnapshot.has_recorded_run` tells
        the interface whether this call would lose anything.

        **A branch rejects this call** (`PL-TFX5`). A branch inherits its
        parent's agent rather than choosing it again. Changing agent is already
        an explicit new case, and a branch that could change agent would be a
        second case disguised as a comparison. Without the rejection, the
        branch would be converted silently and completely. `_build_state`
        clears `opened_from`, so the run would stop being a branch. `reset()`
        would stop returning it to its fork. `resumed_at` would start accepting
        it as a trunk, which would make a branch of a branch by an indirect
        route. A `BranchedCase` would go on listing it among the branches of a
        case it is no longer part of. Each of those is a mode change with
        nothing on screen to say so. A learner who wants a different agent
        starts a new case, which is what `PL-R3KB` made that gesture mean.

        Raises:
            SimulationConfigurationError: This run is a branch. Or the
                snapshot that the settings are carried over from rejects a
                value (`snapshot`). The snapshot is read before the run is
                paused, so the rejection changes nothing (`PL-V2HC`).
        """

        if self._opened_from is not None:
            raise SimulationConfigurationError(
                f"this run is a branch opened at {self._opened_from.fork.instant_s} s, and a "
                "branch carries the agent of the case it continues; changing agent begins a "
                "new case, so change it on the run this branch came from or start a new one"
            )

        current = self.snapshot()
        self.pause()

        self._forget_reached_marks()
        self._build_state(
            agent_id=agent_id,
            circuit_volume_l=current.circuit_volume_l,
            fresh_gas_flow_l_min=current.fresh_gas_flow_l_min,
            delivered_concentration_percent=None,
            alveolar_ventilation_l_min=current.alveolar_ventilation_l_min,
            cardiac_output_l_min=current.cardiac_output_l_min,
        )

    def status(self) -> RunStatus:
        """Whether this run is advancing and, if not, why, built without any compartment value.

        `RunView.present_halt` reads this where it presents a halt.
        `snapshot()` builds every compartment's fraction, and a rejection of
        one of those fractions is one of the halts to present. A halt
        described from a fresh snapshot was not described at all when the
        snapshot itself raised (`PL-7DJK`). The three fields come from the
        controller's own run state and from the run-length guard. The guard
        reads the step count and the step length, which are both checked types
        that the state holds, and it builds no `Fraction`.
        """

        return RunStatus(
            is_running=self._is_running,
            supported_limit_reason=self.supported_limit_reason,
            failure_reason=self._failure_reason,
        )

    def settings(self) -> RunSettings:
        """The agent and the four settings in force, built without any compartment value.

        `RunView.present_halt` calls this when it writes a setting control on a run whose
        `snapshot()` raises. The run holds the setting that a drag applied. So the control is
        written from this value, not left on the value from before the drag (`PL-85LJ`). The
        controller holds the agent and its MAC itself. The vaporizer maximum comes from the
        circuit, and it is the value the core enforces (`PL-1MGB`). The four settings come from
        the compartments. Each one is a checked type, built when it was set.
        """

        system = self._state.uptake_system
        circuit = system.circuit

        return RunSettings(
            is_running=self._is_running,
            supported_limit_reason=self.supported_limit_reason,
            failure_reason=self._failure_reason,
            agent_id=self._agent_id,
            agent_display_name=self._agent_display_name,
            max_delivered_concentration_percent=circuit.max_delivered_concentration_percent,
            agent_mac_percent=self._agent_mac_percent,
            fresh_gas_flow_l_min=circuit.fresh_gas_flow_l_min,
            accepted_fresh_gas_flow_range_l_min=circuit.accepted_fresh_gas_flow_range_l_min,
            delivered_concentration_percent=circuit.delivered_concentration_percent,
            alveolar_ventilation_l_min=system.alveoli.alveolar_ventilation_l_min,
            cardiac_output_l_min=system.patient.cardiac_output_l_min,
        )

    def record(self) -> RunRecord:
        """The settings in force and every change made to them, built without any compartment value.

        This method runs on every render tick of every displayed run.
        `SimulationView` compares its result with the record that the run's view last
        wrote, and draws a frame where the two differ (`PL-X7D5`). So it builds
        nothing beyond what `settings()` builds, and it reads the timeline the
        controller holds. That means it cannot raise for a value that a frame
        would reject.
        """

        settings = self.settings()

        return RunRecord(
            **{field.name: getattr(settings, field.name) for field in fields(RunSettings)},
            control_timeline=self._control_timeline,
        )

    def snapshot(self) -> SimulationSnapshot:
        """Build a fresh, read-only view of current simulation state.

        Raises:
            SimulationConfigurationError: If a compartment's partial-pressure
                quotient is outside 0 to 1. Each quotient is built here as a
                `Fraction` under the compartment's name
                (`run_series.COMPARTMENT_FRACTION_NAMES`). The compartment
                holds an amount, and the quotient read from it carries no
                proof of its range. The interface halts the run on this
                rejection and describes the halt from `record()`, which
                cannot raise it (`PL-7DJK`). No supported setting produces
                such a quotient (`core/concentration.py`).
        """

        system = self._state.uptake_system
        circuit = system.circuit
        alveoli = system.alveoli
        patient = system.patient
        accounting = system.agent_simulation_validation

        return SimulationSnapshot(
            is_running=self._is_running,
            elapsed_s=self._state.elapsed_s,
            began_at_s=self.began_at_s,
            agent_id=self._agent_id,
            agent_display_name=self._agent_display_name,
            max_delivered_concentration_percent=circuit.max_delivered_concentration_percent,
            agent_mac_percent=self._agent_mac_percent,
            agent_mac_awake=self._agent_mac_awake,
            circuit_volume_l=circuit.circuit_volume_l,
            fresh_gas_flow_l_min=circuit.fresh_gas_flow_l_min,
            accepted_fresh_gas_flow_range_l_min=circuit.accepted_fresh_gas_flow_range_l_min,
            delivered_concentration_percent=circuit.delivered_concentration_percent,
            alveolar_ventilation_l_min=alveoli.alveolar_ventilation_l_min,
            cardiac_output_l_min=patient.cardiac_output_l_min,
            inspired_partial_pressure_fraction=circuit.inspired_partial_pressure_fraction,
            alveolar_partial_pressure_fraction=Fraction(
                alveoli.partial_pressure_fraction,
                name=COMPARTMENT_FRACTION_NAMES[RecordedQuantity.ALVEOLAR],
            ),
            mixed_venous_partial_pressure_fraction=Fraction(
                patient.mixed_venous_partial_pressure_fraction,
                name=COMPARTMENT_FRACTION_NAMES[RecordedQuantity.MIXED_VENOUS],
            ),
            vessel_rich_partial_pressure_fraction=Fraction(
                patient.vessel_rich.partial_pressure_fraction,
                name=COMPARTMENT_FRACTION_NAMES[RecordedQuantity.VESSEL_RICH],
            ),
            muscle_partial_pressure_fraction=Fraction(
                patient.muscle.partial_pressure_fraction,
                name=COMPARTMENT_FRACTION_NAMES[RecordedQuantity.MUSCLE],
            ),
            fat_partial_pressure_fraction=Fraction(
                patient.fat.partial_pressure_fraction,
                name=COMPARTMENT_FRACTION_NAMES[RecordedQuantity.FAT],
            ),
            delivered_agent_l=accounting.delivered_agent_l,
            exhausted_agent_l=accounting.exhausted_agent_l,
            stored_agent_l=accounting.currently_stored_agent_l,
            unaccounted_agent_l=accounting.unaccounted_agent_l,
            agent_accounting_absolute_error_l=accounting.absolute_error_l,
            agent_accounting_passes_validation=accounting.passes_validation,
            control_timeline=self._control_timeline,
            bookmarks=self._bookmarks,
            bookmark_halt=self._bookmark_halt,
            bookmark_standings=self.bookmark_standings(),
            supported_limit_reason=self.supported_limit_reason,
            failure_reason=self._failure_reason,
        )

    # ------------------------------------------------------------- bookmarks
    #
    # There are four methods and no `marks` setter, so the collections can
    # change only through the operations that `BookmarkSet` validates. A
    # setter would let a caller pass in a set built anywhere. The invariant
    # that matters is that each instant and each crossing is marked only once.
    # With a setter, that invariant would be enforced only by whichever caller
    # happened to remember it.
    #
    # Each rejection comes out of `app/bookmarks.py` unchanged rather than
    # being reworded here. The message names the value that failed, and a
    # second sentence wrapped around it would put two accounts of one
    # rejection on screen.

    @property
    def bookmarks(self) -> BookmarkSet:
        """Return the instants and the heights at which this run is marked.

        No part of this set is built from a compartment value. It is the same set that
        `snapshot()` carries as `SimulationSnapshot.bookmarks`. A halt reads it here,
        because a halt cannot rely on a snapshot (`bookmark_standings`, `PL-YHR3`).
        """

        return self._bookmarks

    def add_time_bookmark(self, bookmark: TimeBookmark) -> None:
        """Mark an instant of the case.

        Raises:
            SimulationConfigurationError: If the instant is already marked.
        """

        self._bookmarks = self._bookmarks.with_time_bookmark(bookmark)

    def remove_time_bookmark(self, bookmark: TimeBookmark) -> None:
        """Remove the mark at the instant of `bookmark`.

        Raises:
            SimulationConfigurationError: If no bookmark is at that instant.
        """

        self._bookmarks = self._bookmarks.without_time_bookmark(bookmark)
        self._forget_unmarked()

    def add_mac_target(self, target: MacTarget) -> None:
        """Mark a height on one compartment.

        Raises:
            SimulationConfigurationError: If that compartment, height and
                direction is already marked.
        """

        self._bookmarks = self._bookmarks.with_mac_target(target)

    def remove_mac_target(self, target: MacTarget) -> None:
        """Remove the mark on the crossing that `target` names.

        Raises:
            SimulationConfigurationError: If no target names it.
        """

        self._bookmarks = self._bookmarks.without_mac_target(target)
        self._forget_unmarked()

    def _forget_unmarked(self) -> None:
        """Drop what the run did with marks the learner has since removed.

        A removed mark has no row to draw a standing beside, and no place in a
        halt that the interface is reporting. Leaving either behind would name
        a mark that is no longer listed. That is the kind of stale state that
        `.claude/rules/expert-review.md` asks to be designed out rather than
        warned about. A halt that crossed two marks keeps the one that is
        still marked. A halt left naming no mark is cleared completely,
        because `BookmarkCrossing` rejects a step that crossed nothing.
        """

        instants = {bookmark.instant_s for bookmark in self._bookmarks.time_bookmarks}
        crossings = {target.crossing_key for target in self._bookmarks.mac_targets}

        self._reached_instants_s &= frozenset(instants)
        self._reached_crossings &= frozenset(crossings)

        if self._bookmark_halt is None:
            return

        kept_times = tuple(
            bookmark
            for bookmark in self._bookmark_halt.time_bookmarks
            if bookmark.instant_s in instants
        )
        kept_targets = tuple(
            target for target in self._bookmark_halt.mac_targets if target.crossing_key in crossings
        )

        self._bookmark_halt = (
            BookmarkCrossing(self._bookmark_halt.instant_s, kept_times, kept_targets)
            if kept_times or kept_targets
            else None
        )

    @property
    def run_segments(self) -> tuple[RunSegment, ...]:
        """The stretches of constant settings this run has had, oldest first.

        This is the run's own record, as opposed to `snapshot().control_timeline`,
        which records what a *reader* is shown. This record carries the
        settings the equations were assembled from. The timeline carries the
        actions a user took, in the units the interface displays. The two agree
        about when the run changed and, deliberately, about nothing else.

        The property returns the frozen segments rather than the run definition
        itself, so a caller can read the run without being able to advance it.
        A run definition that advanced independently of the run would return
        results for instants the run never reached. Saving, replay and forking
        read this property, and `ROADMAP.md` items 9 to 12 describe them.

        **These instants are on the case's time axis**, as is everything else
        this class exposes: `snapshot().elapsed_s`, the control timeline's
        stamps, and `drawn_window`'s instants. A branch's run definition opens
        at a keyframe of the case rather than at a zero of its own. So a
        keyframe read here needs no conversion to be placed on the case's axis,
        and a caller has no offset to add. `PL-ZMRT` decided this. Before it,
        this property was the one reader that returned instants in a second
        frame of reference.

        **The first of these segments does not in general begin where the
        branch began** (`PL-B8MK`). A branch taken at a control event opens its
        run definition at the fork. A branch taken at a bookmark opens it at the
        keyframe before the fork, because recording a keyframe at the fork
        would change the trunk's own later results. A caller that wants the
        run's own beginning reads `began_at_s`. This tuple describes what the
        *definition* holds.
        """

        return self._run_definition.segments

    @property
    def opened_from(self) -> ResumePoint | None:
        """Where this run was opened from, or `None` for a trunk.

        This object holds a branch's whole provenance. So the source of a
        displayed value stays traceable to the run that the branch continues.
        `CLAUDE.md`'s safety-critical standard requires that of any clinically
        meaningful output.
        """

        return self._opened_from

    @property
    def began_at_s(self) -> CaseInstant:
        """The case instant at which this run began: induction, or the run's fork.

        It is zero on a trunk and the fork instant on a branch. Like everything
        else this class returns, it is on the case's own time axis. It bounds
        a run on the left. `drawn_window` clips there, `app/bookmarks.py`
        reads it to decide that a mark is unreachable, and
        `SimulationSnapshot.has_recorded_run` counts a run's own progress from
        it. That last use is why the snapshot carries it too.

        **It is not `run_segments[0].opening.instant_s`. This property exists
        to stop callers inferring it from there** (`PL-B8MK`). A branch taken
        at a control event opens its run definition at the fork, so the two
        agree. A branch taken at a bookmark opens its run definition at the
        keyframe *before* the fork, because recording a keyframe at the fork
        would change the trunk's own later results. A caller that took the
        first segment's opening as the run's beginning would place such a
        branch earlier than it exists. It would draw the branch across an
        interval that the branch never lived.
        """

        return CaseInstant(0.0) if self._opened_from is None else self._opened_from.fork.instant_s

    def resumed_at(self, instant_s: CaseInstant) -> SimulationController:
        """Open a second live run at this run's canonical state at `instant_s`.

        This is the seam that `PL-J2TD` exists for. A branch has to become
        something a learner can *manage*, not just a second curve, and managing
        it means advancing it. The result is an ordinary paused
        `SimulationController`, standing at the state this run passed through
        at `instant_s`. It advances by the same path every run takes.
        `advance()` is not overridden, and no second way to move a run forward
        is introduced.

        **It opens at a keyframe, because that is this method's scope**
        (`PL-54V0`). `instant_s` must be an instant at which this run holds a
        keyframe, which means its start or a recorded setting change. Any other
        instant is rejected, but not because it cannot be reproduced. A marked
        instant is branched at through `resumed_at_mark`, and the instant where
        a paused run stands is branched at through `resumed_here`. Both fork
        between two keyframes and reproduce this run element-wise, by opening
        the branch's run definition at the keyframe before the fork
        (`_open_at`). No method offers any other instant, so a learner first
        marks it or pauses the run on it. No method *restarts* a run definition
        at the fork from the canonical state there. That would replace one
        propagation over an interval with two propagations over its halves.
        The result is a different rounding of the same exact solution, measured
        at up to 5.3e-13 in an accumulator, and `PL-Z3W6` requires a branch to
        reproduce its parent element-wise.

        **The branch's clock continues the case's clock**, because a branch is
        one patient's case under a second management, not a second patient.
        Three things follow, and each is a correctness property rather than a
        convenience. First, the 24 h supported run length is enforced on the
        step count. A branch that restarted the count would get a fresh
        envelope. A fork at 23 h could then be advanced to 47 h of case time
        with every guard passing. That is exactly the regime in which, as
        `core/supported_ranges.py` argues, the omitted metabolism dominates.
        Second, the clock, every control-change stamp and the chart's axis all
        read `snapshot().elapsed_s`, and `format_elapsed` says that they "state
        one quantity one way". A branch counting from zero would place the
        patient at the wrong point on the uptake curve in all three places at
        once. Third, elapsed time stays one multiplication, `(k + n)` steps
        times the step length, rather than the fork instant plus the branch's
        own elapsed time. `docs/MODEL.md` § "Simulated time is a count of
        steps, not a running total" is the rule against that sum.

        **The run definition opens at the fork rather than at a zero of its
        own**, so the branch's clock and its run definition's instants are one
        quantity, and nothing converts between them (`PL-ZMRT`). § "The
        canonical evaluation rule" requires this. When asked for a case
        instant, the branch forms its interval from the same two floats its
        parent used. A run definition shifted to its own zero would depend on a
        subtraction that does not always round-trip. Opening *at the fork* is a
        property of this method, not of every branch. `resumed_here` and
        `resumed_at_mark` open at the keyframe before the fork, on the same
        axis and with the same guarantee. `_open_at` and `docs/MODEL.md`
        § "What this requires of a branch" explain this.

        **The settings are replayed from the control timeline, and then
        checked.** A branch is built through the ordinary constructor, so the
        circuit volume is applied before any state is. `set_circuit_volume`
        conserves agent by rewriting the inspired fraction. So a volume set
        afterwards would silently move the branch off its parent's keyframe.
        The four live controls come from the recorded changes, which hold the
        values the compartments actually took, in the compartments' own units.
        The replay is then checked against the segment's own settings rather
        than trusted. Since `PL-SM5V`, those settings hold the same litres per
        minute, so the two compare exactly. The check matters because a branch
        that assembled a system matrix its parent never used would diverge from
        its first step, within the tolerance that keeps the two records
        together. The agent's displayed references are checked as well. A
        rejection names each value that differs rather than a cause, because
        the rebuild reads the data files again as well as the timeline
        (`_disagreements_with`).

        Args:
            instant_s: The case instant to open at, in seconds. It must be an
                instant at which this run holds a keyframe.

        Returns:
            A paused `SimulationController` standing at that state, carrying
            this run's agent, patient and circuit, with an empty control
            timeline of its own and a copy of this run's bookmarks.

        Raises:
            TypeError: `instant_s` is not a `CaseInstant`, so nothing has
                checked it against the supported run length
                (`core/supported_ranges.py`).
            SimulationConfigurationError: If any of the following is true. `instant_s`
                is not an instant at which this run holds a keyframe. This run
                is itself a branch, because a branch of a branch is rejected
                rather than silently flattened (`PL-TFX5`). The frame this run
                is drawn in has failed (`fork_refusal`). The fork instant is not
                a whole number of this run's steps. Or the rebuilt branch holds
                an equation setting or agent reference that this run did not
                hold at the fork. The error names each differing setting or
                reference with both of its values.
        """

        return self._branch_from(self._resume_point_at(instant_s))

    def resumed_here(self) -> SimulationController:
        """Open a second live run where this paused run stands, stopped on a mark or not.

        This method serves the decision point a learner is looking at
        (`PL-Y2SL`). A learner who has paused to think can try something else
        from that instant in one action, without marking it first (project
        owner, 2026-10-12). It is also the way to branch at a bookmark halt,
        which is a pause that a mark caused. So it provides what `ROADMAP.md`'s
        v0.5.0 Definition of done asks for when it says "a branch taken at any
        recorded control event **or bookmark**" (`PL-B8MK`). `resumed_at`
        describes everything a branch is: a paused controller that carries this
        run's agent, patient and circuit and advances by the path every run
        takes. The only difference here is where the branch may be taken.

        **It takes no instant, so a caller has no instant to get wrong.** The
        clock names the fork, which is the step the run is standing on, and
        supplies nothing else. The state at the fork comes from
        `RunDefinition.state_at`, the canonical path that every branching
        method forks from, not from the live system. If this method took a
        float instead, a caller could ask for a branch at an instant the run
        has not reached. A caller could also ask at the instant a learner
        *marked* rather than at the step instant where the run actually
        stopped. Those are not the same number, because a mark that lies inside
        a step halts the run at the step's end. This is the only way to branch
        at a MAC target, which has no instant to name.

        **It rejects a run that is advancing, a failed run, a run at its own
        opening, and a run at the supported run length**, each for its own
        reason. The position of a running run moves with every step, so an
        instant read from it is stale before it can be used. A failure is not
        a pause (`RunStatus.failure_reason`), and a branch that opened where a
        failed run stands would resume what `fail` says must not be resumed. A
        run standing at its opening has recorded nothing to branch from, and
        `resumed_at` already opens there. A run at the supported run length is
        stopped rather than paused (`RunStatus.supported_limit_reason`). No
        step is left to take, so a branch opened there could never be run. On
        a dashboard that shows one comparison at a time, only the trunk's
        Reset, which discards the case, would take that branch off the chart.
        The methods that still fork at the limit, at a keyframe or a mark on
        the limit, are kept because of what `PL-5291` decided about such a
        branch.

        **The trunk is not changed.** No keyframe is recorded where the run
        stands. The branch's run definition opens at the keyframe where the
        parent's own stretch opens, while the branch's clock and its live
        system stand at the fork. See `_open_at`. See also `docs/MODEL.md`
        § "What this requires of a branch" for which of that section's two
        conditions this relaxes, and why the element-wise guarantee survives.
        The obvious route is to record the keyframe instead. That keeps the
        branch exact against its parent, but it changes the parent's own later
        results: 48 of 54 elements differ from the same case built without the
        mark. So pausing or marking a run would change it.

        **The crossing that the branch opens on is computed again from the
        step** (`_crossing_of_step`), as `resumed_at_mark` computes it. It is
        not read from a halt's record. The record names what was marked when
        the run stopped. So a mark added inside the halting step, while the run
        stood on it, was missing from the record and was treated as before the
        branch. The same mark reached through `resumed_at_mark` was treated as
        passed (`PL-2N43`). When both methods check the marks as they are now,
        they give one account of one step.

        Returns:
            A paused `SimulationController` standing where this run stands,
            carrying this run's agent, patient and circuit, with an empty
            control timeline of its own and a copy of this run's bookmarks.

        Raises:
            SimulationConfigurationError: If any of the following is true. This run is
                advancing, has failed, or stands at its opening or at the
                supported run length. This run is itself a branch, because a
                branch of a branch is rejected rather than silently flattened.
                Or the rebuilt branch holds an equation setting or agent
                reference that this run did not hold at the fork. The error
                names each differing setting or reference with both of its
                values.
        """

        return self._branch_from(self._resume_point_here())

    @property
    def here_fork_point(self) -> HereForkPoint | None:
        """Where `resumed_here` would open a branch, or None where it would reject the call.

        The result comes from the same check that `resumed_here` raises from
        (`_refusal_here`). So an offer drawn from this property and the method
        that takes it cannot disagree about whether there is a place to branch.
        The property works on a branch as on a trunk, and returns None on a
        branch, for the reason every branching method rejects a branch.
        `BranchedCase.here_fork_point` reads the trunk's value.
        """

        if self._refusal_here() is not None:
            return None

        return HereForkPoint(self._state.elapsed_s, self._bookmark_halt is not None)

    def resumed_at_mark(self, bookmark: TimeBookmark) -> SimulationController:
        """Open a second live run at the step that reached `bookmark`, stopped there or not.

        This is the third way to branch (`PL-W4XQ`), and it is the action that
        time bookmarks were requested for. A learner paused at 3 h marks 1 h
        and goes back to it to try something else there. The mark may have
        been set before the run passed it, so that it stopped the run. Or it
        may have been set after the clock was already past it, so that no step
        ever crossed it. This method treats both cases alike, because the state
        at a reached instant is the run definition evaluated there. The run did
        not have to be standing on that instant to hold it.

        **It is the halt fork, taken later.** The fork is the end of the step
        that reaches the mark (`TimeBookmark.steps_to_reach`), which is the
        instant where a halt stops the run. The state is
        `RunDefinition.state_at` evaluated there. The branch's run definition
        opens at the keyframe at or before the fork. So a mark the run is
        halted on forks at the same place, and from the same state, as
        `resumed_here`. A mark set behind the clock forks where the halt would
        have stopped the run, had the mark been set in time. Nothing is
        recorded on this run, so it stays the case it would have been without
        the mark (`docs/MODEL.md` § "What this requires of a branch").

        **The crossing that the branch opens on is reconstructed**, because a
        step that halted nothing kept no record of what it crossed
        (`_crossing_of_step`). It is the result of `BookmarkSet.crossings_between`
        for that one step, using the marks as they are now and each
        compartment read canonically at both ends of the step. So the rule that
        halts a running case is the same rule that names this crossing. A mark
        that lies inside the step, which the branch opens just after, is still
        treated as passed rather than as before the branch (`PL-3K9B`, case B).

        **It takes the mark, not an instant**, for the same reason that
        `resumed_here` takes nothing. A float would let a caller name the
        instant a learner typed, which in general is not the step instant at
        which the run reached the mark. A mark at the case's opening is the one
        mark that no step reaches. The run stands on it from the start, so it
        forks at the opening keyframe with no crossing, as `resumed_at` would
        there.

        Args:
            bookmark: The mark to branch at. It is matched on its instant, in
                the same way `BookmarkSet.without_time_bookmark` matches, so a
                caller that holds the mark without its label still names it.

        Returns:
            A paused `SimulationController` standing at the step that reached
            the mark, carrying this run's agent, patient and circuit, with an
            empty control timeline of its own and a copy of this run's
            bookmarks.

        Raises:
            SimulationConfigurationError: If any of the following is true. This run holds
                no time bookmark at that instant. This run has not passed the
                mark, so the case holds no state there yet. A mark ahead of the
                clock stops a running case when it is reached, and
                `resumed_here` then takes the fork. This run is itself a
                branch, because a branch of a branch is rejected rather than
                silently flattened. Or the rebuilt branch holds an equation
                setting or agent reference that this run did not hold at the
                fork. The error names each differing setting or reference with
                both of its values.
        """

        return self._branch_from(self._resume_point_at_mark(bookmark))

    @property
    def mark_fork_points(self) -> tuple[MarkForkPoint, ...]:
        """The time bookmarks this run has passed, and where a branch taken at each one opens.

        These are the marks whose standing is `MarkStanding.PASSED`. They are
        read from the standings rather than decided again, so this list and
        the bookmark panel's rows cannot disagree about which marks are behind
        the clock. They are listed earliest first, the order that
        `BranchedCase.fork_points_s` keeps.

        Like `run_segments`, this property works on a branch as on a trunk.
        On a branch, `resumed_at_mark` rejects the fork, for the reason every
        branching method rejects a branch. `BranchedCase.mark_fork_points`
        reads the trunk's value.
        """

        return tuple(
            MarkForkPoint(bookmark, self._instant_after(self._steps_to_reach(bookmark)))
            for bookmark in sorted(
                self._passed_time_bookmarks(), key=lambda bookmark: bookmark.instant_s
            )
        )

    def _branch_from(self, resume_point: ResumePoint) -> SimulationController:
        """Build the branch `resume_point` describes, leaving this run untouched.

        Every branching method uses this: `resumed_at`, `resumed_at_mark` and
        `resumed_here`. The only thing that separates them is where a branch
        may be taken. What a branch *is* is defined once, here.
        """

        fork_at_s = resume_point.fork.instant_s
        circuit = self._state.uptake_system.circuit
        alveoli = self._state.uptake_system.alveoli
        patient = self._state.uptake_system.patient

        branch = SimulationController(
            agent_id=self._agent_id,
            circuit_volume_l=circuit.circuit_volume_l,
            # The timeline's `ControlChange` is typed `float`, so a setting read
            # back from it is built into its checked type here. A value that
            # already has that type is checked again, which does no harm. The
            # record holds only values the core accepted, so none can be rejected.
            fresh_gas_flow_l_min=FreshGasFlow(
                self._setting_at(
                    ControlInput.FRESH_GAS_FLOW, fork_at_s, circuit.fresh_gas_flow_l_min
                )
            ),
            delivered_concentration_percent=Percent(
                self._setting_at(
                    ControlInput.DELIVERED, fork_at_s, circuit.delivered_concentration_percent
                )
            ),
            alveolar_ventilation_l_min=AlveolarVentilation(
                self._setting_at(
                    ControlInput.ALVEOLAR_VENTILATION, fork_at_s, alveoli.alveolar_ventilation_l_min
                )
            ),
            cardiac_output_l_min=CardiacOutput(
                self._setting_at(
                    ControlInput.CARDIAC_OUTPUT, fork_at_s, patient.cardiac_output_l_min
                )
            ),
        )

        disagreements = self._disagreements_with(branch, resume_point.segment.settings)

        if disagreements:
            raise SimulationConfigurationError(
                f"a branch at {fork_at_s} s would be rebuilt from values this run did not "
                "hold there, which would make it a second case rather than a second "
                f"management of this one: {'; '.join(disagreements)} "
                '(docs/ARCHITECTURE.md, "What a branch is, and what it shares with its parent")'
            )

        # The branch inherits the marks but not the timeline. The two are
        # treated in opposite ways for the same reason. The timeline is this
        # run's record of what was done to *it*. Reproducing it on a branch
        # would claim actions the learner never took on the branch. A mark is a
        # question about what is still to come, and a comparison is two
        # managements answering one question. If the learner had to enter the
        # marks again, a typed 0.85 against a 0.8 would leave two branches
        # apparently compared at one height but actually compared at two, with
        # nothing on screen to say so.
        #
        # A mark that lies before the fork is copied with the rest. It cannot
        # be reached from here on, but it is not dropped. Dropping it would make
        # the trunk's list and the branch's list disagree about where the case
        # is marked, which is harder for a comparison to explain. Showing that
        # such a mark is unreachable, where it is listed, belongs to `PL-CTD7`,
        # with the rest of the reached / not-reached outcome set.
        branch._bookmarks = self._bookmarks

        branch._open_at(resume_point, branch._state.uptake_system.equation_settings())

        return branch

    def _disagreements_with(
        self, branch: SimulationController, settings_at_fork: UptakeEquationSettings
    ) -> tuple[str, ...]:
        """Return each value that `branch` was rebuilt with but this run did not have at the fork.

        A branch is rebuilt rather than copied. Its live controls are replayed from the
        recorded timeline, and its agent, patient and circuit are read again from the data
        files. So this method names every value that came out different, with both of its
        values, and does not name a cause. A data file edited between the two builds fails
        the check even though the timeline is correct. A message that blamed the timeline
        would send its reader into the one part that worked (`PL-NC62`).

        Two groups are compared. The first is the equation settings: every field of them and
        of each tissue group. Those fields are everything that their equality compares, so a
        setting added to either class is named here without an edit. The second is the
        agent's three displayed references, which no equation reads: its name, its MAC and
        its MAC-awake. The MAC is the divisor of every MAC multiple on screen. A branch
        rebuilt under another MAC would show one concentration as two different multiples
        beside its parent. The vaporizer maximum is not compared as a displayed reference.
        The equation settings already carry it, and it is read from the circuit (`PL-1MGB`).

        Each value is written by its `repr`. For a float, that is the shortest text that
        reads back as the same float. For a string, it is the string in quotes. So two
        values that differ never print alike, even when they differ only in the last bit.
        Any rounding would print two such values identically.
        """

        replayed = branch._state.uptake_system.equation_settings()
        compared: list[tuple[str, object, object]] = [
            *(
                (field.name, getattr(settings_at_fork, field.name), getattr(replayed, field.name))
                for field in fields(UptakeEquationSettings)
                if field.name != "tissues"
            ),
            *(
                (
                    f"{group_in_run.name} {field.name}",
                    getattr(group_in_run, field.name),
                    getattr(group_on_branch, field.name),
                )
                for group_in_run, group_on_branch in zip(
                    settings_at_fork.tissues, replayed.tissues, strict=True
                )
                for field in fields(TissueGroupEquationSettings)
            ),
            ("agent_display_name", self._agent_display_name, branch._agent_display_name),
            ("agent_mac_percent", self._agent_mac_percent, branch._agent_mac_percent),
            *(
                (
                    f"agent_mac_awake {field.name}",
                    getattr(self._agent_mac_awake, field.name),
                    getattr(branch._agent_mac_awake, field.name),
                )
                for field in fields(MacAwakeReference)
            ),
        ]

        return tuple(
            f"{name} is {in_run!r} in this run and {on_branch!r} on the branch"
            for name, in_run, on_branch in compared
            if in_run != on_branch
        )

    def _open_at(self, resume_point: ResumePoint, settings: UptakeEquationSettings) -> None:
        """Put this run at `resume_point`'s state, on its clock and its accounting.

        This is a separate method because `reset()` needs exactly the same
        step. Returning a branch to its own beginning means returning it to
        the fork. The case's induction cannot supply that, because the branch
        does not hold it.

        It writes state and never settings, which is why `reset()` can use it.
        Reset preserves settings by contract. So a branch that is reset after
        its learner has dialled something new stands at the fork state under
        the new settings. A reset trunk does the same with its own initial
        state. `_branch_from` checks the replayed settings against the
        segment, because that check is about the *replay*, and there is no
        replay here. The caller passes in the settings in force rather than
        this method reading them. Reading them is the one step on which a
        reset can be rejected, and `reset()` reads them before it clears
        anything (`PL-M4M0`). `_branch_from` reads them from the branch it has
        just built, which nothing but a setter has written to.

        **The run definition always opens at the parent's stretch, under the
        parent's settings** (`PL-B8MK`). Whatever the learner has dialled since
        is recorded as a change at the fork rather than written into the
        opening. That keeps the branch propagating from the same keyframe that
        its parent propagates from, which is the whole of the element-wise
        guarantee. `record_change` already drops a call whose settings are the
        ones in force. So in the reproducing case, which is every fork and
        every reset that changed nothing, the branch records no change and
        opens exactly as it did before this item.

        **Choosing the opening from the settings instead would make the result
        depend on the order of two reversible actions**, which is why it is
        not done that way. "Dial, dial back, reset" and "dial, reset, dial
        back" leave the same branch: the same settings, the same live state
        and the same snapshot. Choosing the opening at reset time would give
        the second sequence the fork rather than the keyframe. That branch
        would restart from two propagations where the parent took one, and it
        would stop reproducing the parent. This was measured on 2026-09-20:
        40 of 45 elements differed across five probes, the worst by 1.21e-15,
        with nothing on screen to say so. Recording the change instead lets
        `record_change`'s own collapse rule notice the dial-back. The fork
        segment ends up with the settings that the stretch before it already
        had, so it is removed entirely, and the branch is back where it started.
        """

        segment = resume_point.segment
        system = self._state.uptake_system

        # The state comes from the canonical path, never from reading back the
        # seeded system. A compartment stores an amount and derives its
        # fraction from its own capacity, so the round trip is not exact. Over
        # the range a case covers, 11.7% of alveolar fractions come back one
        # unit in the last place away. The element-wise reproduction that
        # `ROADMAP.md` item 12 requires would fail on exactly those entries.
        # For a fork at a control event, the state is the parent's keyframe.
        # For a fork at a bookmark, it is one propagation from that keyframe.
        # `ResumePoint.fork` holds it in either case.
        system.resume_at(resume_point.fork.state, initial_agent_l=resume_point.accounting_anchor_l)

        self._state = SimulationState(
            uptake_system=system,
            step_count=resume_point.step_count,
            simulation_step_s=resume_point.simulation_step_s,
        )
        # The run definition opens on the parent's own stretch, with its
        # keyframe and its settings, at that keyframe's own instant on the
        # case's time axis. That keeps the clock and the definition's reach
        # one quantity.
        self._run_definition = RunDefinition(
            segment.settings, segment.opening.state, opened_at_s=segment.opening.instant_s
        )
        # The branch has reached the fork, because it is standing there. Where
        # the run definition opened earlier, the stretch in between belongs to
        # the *parent*, and the branch never lived it. So `drawn_window` clips
        # it away. The reach is how far the branch may be evaluated, not where
        # it may be drawn from.
        self._run_definition.advance_to(resume_point.fork.instant_s)
        # Then record whatever the learner has dialled since. That is nothing
        # on a fork and may be anything on a reset. It is recorded at the fork
        # rather than written into the opening, so the parent's stretch stays
        # the parent's. The keyframe this records carries
        # `_canonical_state_at(fork)`, which is the same expression that
        # `resume_point.fork.state` came from.
        self._run_definition.record_change(settings)
        self._note_recorded_settings()
        self._opened_from = resume_point
        self._clear_control_timeline()
        self._stand_on(resume_point.crossing)

    def _stand_on(self, crossing: BookmarkCrossing | None) -> None:
        """Record the crossing that this run opens on as the place where it stopped.

        A branch forked at a crossing is *standing on* it. That crossing is
        where the branch is, not something its parent did. A run that opens on
        a crossing and reports that it stopped on nothing describes a different
        run (`PL-3K9B`). So the crossing becomes the branch's `bookmark_halt`,
        just as a halt does on a trunk.

        **What the branch has done with the marks is not seeded from the
        crossing** (`PL-1ZQ4`). At every read, the standings ask the step the
        branch opened on again, using the marks as they are at that moment
        (`_crossings_stood_on`). So a mark added to the branch after it opened
        is treated as it would have been had it existed at the fork. Seeding
        the reached sets here as well would give a second, older result for
        the same question. That older result is the approach this replaced,
        and it named only the marks that existed at the fork.

        `_open_at` calls this method, and `_open_at` is the code path of a
        reset as well as of a fork. So a branch reset onto its own fork stands
        on the same record it opened on.

        Args:
            crossing: The marked crossing that this run opens on, or `None`
                when the step ending at its fork crossed no mark or no step
                ends there.
        """

        self._bookmark_halt = crossing
        # A reset does not restore a mark that was removed from this branch
        # before the reset. The crossing is a record of a step, and
        # `_forget_unmarked` stops that record from naming a row that the
        # panel no longer draws.
        self._forget_unmarked()

    def _resume_point_at(self, instant_s: CaseInstant) -> ResumePoint:
        """Return everything a branch opening at `instant_s` needs, or reject it and say why.

        Raises:
            TypeError: `instant_s` is not a `CaseInstant`.
            SimulationConfigurationError: If any of the following is true. This run is a
                branch, or its frame has failed (`fork_refusal`). `instant_s`
                is not one of this run's keyframes. Or the instant is not a
                whole number of this run's steps.
        """

        self._require_forkable()
        require_case_instant("instant_s", instant_s)

        openings = [segment.opening.instant_s for segment in self._run_definition.segments]

        for segment in self._run_definition.segments:
            if segment.opening.instant_s == instant_s:
                break
        else:
            # The reason is this method's scope, not arithmetic. The other two
            # branching methods fork between keyframes and reproduce the run
            # exactly (`PL-54V0`). So a message that blamed the propagation
            # would teach a constraint that the code beside it disproves.
            raise SimulationConfigurationError(
                f"this run holds no keyframe at {instant_s} s, and resumed_at opens at one: the "
                f"run's opening or a recorded setting change, which this run holds at {openings} "
                "s. A marked instant is branched at with resumed_at_mark once the run has passed "
                "it, and the instant a paused run stands at with resumed_here"
            )

        # Here the fork *is* the stretch's opening, which makes a control event
        # the simple case: one instant does both jobs. The step ending there is
        # asked what it crossed, as every other branching method asks it. A
        # keyframe is not a mark, but the step that reached it may have crossed
        # one. If this branch opened on no crossing while `resumed_here` opened
        # on the step's crossing, one instant would be described in two ways
        # (`PL-1ZQ4`, case 3).
        return self._resume_point(segment, segment.opening)

    def _resume_point_here(self) -> ResumePoint:
        """Return everything a branch opening where this run stands needs, or reject it and say why.

        The fork is the clock, `SimulationState.elapsed_s`, because the clock
        is where the run is. The clock equals `_instant_after` of the step
        count, bit for bit. On a halt, the clock is also the crossing's own
        instant, because `BookmarkSet.crossings_between` stamps a crossing
        with the instant at which its step ended. Taking the fork from the
        clock means this method does not rely on that agreement.

        Raises:
            SimulationConfigurationError: `_refusal_here` names a reason. Or
                the fork instant is not a whole number of this run's steps,
                which cannot happen for an instant read from the clock.
        """

        refusal = self._refusal_here()

        if refusal is not None:
            raise SimulationConfigurationError(refusal)

        fork_s = self._state.elapsed_s
        fork = Keyframe(fork_s, self._run_definition.state_at(fork_s))

        return self._resume_point(self._run_definition.segment_at(fork_s), fork)

    def _refusal_here(self) -> str | None:
        """Why a branch where this run stands is rejected, or None where it is not.

        `here_fork_point` and `resumed_here` both read this one check, so the
        offer and the method cannot disagree. The docstring of `resumed_here`
        gives the reason for each rejection, and the messages say what to do
        instead.
        """

        refusal_to_fork = self.fork_refusal

        if refusal_to_fork is not None:
            return refusal_to_fork

        if self._is_running:
            return (
                "this run is going, so where it stands moves with every step and an instant read "
                "off it is gone before it can be branched at; pause it, and resumed_here branches "
                "where it then stands"
            )

        if self._failure_reason is not None:
            return (
                f"this run stopped at {self._state.elapsed_s} s on a failure, not a pause "
                f"({self._failure_reason}), so where it stands is not a place to branch; a "
                "setting change or a mark it passed before is still branched at with resumed_at "
                "or resumed_at_mark"
            )

        if self.has_reached_supported_limit:
            return (
                f"this run stands at {self._state.elapsed_s} s, the supported run length, "
                "where no step is left to take, so a branch opened where it stands could not be "
                "run; a setting change or a mark it passed before is still branched at with "
                "resumed_at or resumed_at_mark"
            )

        if self._state.step_count == 0:
            return (
                "this run stands at its opening and has recorded nothing to branch from; "
                "resumed_at opens a branch at the opening"
            )

        return None

    def _keyframe_before(self, step_count: StepCount) -> Keyframe | None:
        """Where the step ending after `step_count` steps began, or None where no step ends there.

        The result is the instant one step earlier and this run's canonical
        state there. So both ends of the step are read from
        `RunDefinition.state_at`, as a fork reads them. No step reaches the
        case's opening.

        Args:
            step_count: How many steps the case had completed at the step's
                end. It is never fewer than the count this run opened on,
                because a branch is never asked about a step it did not take.
        """

        if step_count == 0:
            return None

        before_s = self._instant_after(StepCount(step_count - 1))

        return Keyframe(before_s, self._run_definition.state_at(before_s))

    def _crossing_of_step(
        self, stepped_from: Keyframe | None, stepped_to: Keyframe
    ) -> BookmarkCrossing | None:
        """The marks that the step from `stepped_from` to `stepped_to` crossed, using current marks.

        The result is computed again from the rule that `advance` halts by,
        for that one step, with each compartment read canonically at both
        ends. It is not read from any record. A step that halted nothing kept
        no record. A halt's record names only what was marked when the run
        stopped, so a mark added inside the halting step afterwards would be
        missing from it (`PL-2N43`). Every branching method asks about the
        step ending at its fork through this method. The standings also use
        it, for the step a run opened on or stands on (`PL-1ZQ4`). The reading
        at the end of the step is the state a branch opens from. So the
        branch's first step begins where this step ends, and the branch does
        not cross again a height that this step arrived at.

        Args:
            stepped_from: Where the step began, or None where no step ends at
                `stepped_to`, so nothing was crossed.
            stepped_to: Where the step ended.
        """

        if stepped_from is None or self._bookmarks.is_empty:
            return None

        return self._bookmarks.crossings_between(
            before_s=stepped_from.instant_s,
            after_s=stepped_to.instant_s,
            before=self._compartment_mac_multiples(stepped_from.state),
            after=self._compartment_mac_multiples(stepped_to.state),
        )

    def _resume_point_at_mark(self, bookmark: TimeBookmark) -> ResumePoint:
        """Return everything a branch opening at the step that reached `bookmark` needs.

        Raises:
            SimulationConfigurationError: If any of the following is true. This run is a
                branch, or its frame has failed (`fork_refusal`). It holds no
                time bookmark at that instant. It has not passed the mark. Or
                the fork instant is not a whole number of this run's steps,
                which cannot happen for an instant built from a step count.
        """

        self._require_forkable()
        held = self._bookmarks.held_time_bookmark(bookmark)

        if held not in self._passed_time_bookmarks():
            raise SimulationConfigurationError(
                f"this run's clock stands at {self._state.elapsed_s} s, short of the mark at "
                f"{held.instant_s} s, so the case holds no state there to branch from: a mark is "
                "branched at once the run has passed it, or, standing on the step that crosses "
                "it, with resumed_here"
            )

        step_count = self._steps_to_reach(held)
        fork_s = self._instant_after(step_count)
        fork = Keyframe(fork_s, self._run_definition.state_at(fork_s))

        return self._resume_point(self._run_definition.segment_at(fork_s), fork)

    def _passed_time_bookmarks(self) -> tuple[TimeBookmark, ...]:
        """Return the time bookmarks that this run's standings show as passed.

        These are the marks that the run's clock is at or past. The method reads
        `bookmark_standings` instead of comparing times here. So a mark is offered for a
        fork exactly when its row shows it as passed.
        """

        standings = self.bookmark_standings()

        return tuple(
            bookmark
            for bookmark in self._bookmarks.time_bookmarks
            if standings.of_time_bookmark(bookmark) is MarkStanding.PASSED
        )

    def _steps_to_reach(self, passed: TimeBookmark) -> StepCount:
        """How many of this run's steps reach `passed`, a mark that the run is at or past.

        A run that has not stepped stands at its opening. So the only mark it
        can have passed is a mark at the opening, which no step reaches.
        """

        simulation_step_s = self._state.simulation_step_s

        if simulation_step_s is None:
            return StepCount(0)

        return passed.steps_to_reach(simulation_step_s)

    def _instant_after(self, step_count: StepCount) -> CaseInstant:
        """The case instant where this run stands once `step_count` steps are complete.

        It forms the same product as `SimulationState.elapsed_s`, in the same
        way. So an instant derived here is, bit for bit, the one the
        clock reads after that many steps, and it passes `_resume_point`'s
        whole-step check.
        """

        simulation_step_s = self._state.simulation_step_s

        if simulation_step_s is None:
            return CaseInstant(0.0)

        return CaseInstant(step_count * simulation_step_s)

    def _require_forkable(self) -> None:
        """Refuse a fork from a run that is a branch, or whose frame has failed.

        Raises:
            SimulationConfigurationError: This run is a branch, or the frame
                it is drawn in has failed (`fork_refusal`). A branch of a
                branch is excluded on purpose, not merely unimplemented
                (`PL-TFX5`). Refusing it here also covers a caller that holds
                a branch directly, which `BranchedCase` cannot control.
        """

        refusal = self.fork_refusal

        if refusal is not None:
            raise SimulationConfigurationError(refusal)

    def _refusal_as_a_branch(self) -> str | None:
        """Why a fork from this run is refused because the run is a branch, or None for a trunk.

        This is the first of `fork_refusal`'s two reasons. It is kept separate
        because its message is about the run's place in the case rather than
        about its frame.
        """

        if self._opened_from is None:
            return None

        return (
            f"this run is itself a branch opened at {self._opened_from.fork.instant_s} s, "
            "and a branch of a branch is refused rather than silently flattened; branch "
            "from the trunk instead"
        )

    def _resume_point(self, segment: RunSegment, fork: Keyframe) -> ResumePoint:
        """Return a branch's whole provenance: the stretch it opens inside and where it stands.

        **The crossing is computed here, once, for every branching method**
        (`PL-1ZQ4`). Whichever method named the fork, the step ending at the
        fork is asked what it crossed. So a branch taken at a control event,
        at a mark, or where the run stands opens on one account of one step.
        When each method passed in its own result, `resumed_at` passed none.
        A branch opened at a keyframe where the trunk was halted then treated
        the halt's marks as lying before the branch.

        Args:
            segment: The stretch of this run that holds `fork`. Its opening is
                the keyframe where the branch's own run definition opens.
            fork: The instant at which the branch is taken, and this run's
                canonical state there.

        Raises:
            SimulationConfigurationError: The fork instant is not a whole
                number of this run's steps, so a branch could not continue the
                case's step count exactly.
        """

        simulation_step_s = self._state.simulation_step_s

        if simulation_step_s is None:
            step_count = StepCount(0)
        else:
            step_count = StepCount(round(fork.instant_s / simulation_step_s))

            if step_count * simulation_step_s != fork.instant_s:
                raise SimulationConfigurationError(
                    f"{fork.instant_s} s is not a whole number of this run's "
                    f"{simulation_step_s} s steps, so a branch could not continue the case's "
                    "step count exactly"
                )

        stepped_from = self._keyframe_before(step_count)

        return ResumePoint(
            segment=segment,
            fork=fork,
            step_count=step_count,
            simulation_step_s=simulation_step_s,
            accounting_anchor_l=(
                self._state.uptake_system.agent_simulation_validator.initial_agent_l
            ),
            stepped_from=stepped_from,
            crossing=self._crossing_of_step(stepped_from, fork),
        )

    def _setting_at(self, control: ControlInput, instant_s: float, current: float) -> float:
        """What `control` was set to at `instant_s`, from this run's recorded changes.

        The value is in the units that the compartments hold and the timeline
        records, which makes the replay exact. `ControlChange` stores the value
        the core accepted rather than the one a caller asked for.

        There are three cases, and a reader would most easily miss the second.
        If the control changed at or before the instant, the latest such
        change gives the value. If the control changed only *after* the
        instant, it was until then at the value that change replaced, so the
        first such entry's `previous_value` is the result. A control that never
        changed has had its current value for the whole run.
        """

        for change in reversed(self._control_timeline):
            if change.control is control and change.elapsed_s <= instant_s:
                return change.new_value

        for change in self._control_timeline:
            if change.control is control:
                return change.previous_value

        return current

    def drawn_window(self, start_s: float, stop_s: float, columns: int) -> DrawnWindow:
        """The states to plot across an axis, evaluated from the run definition.

        The chart reads its states here. Before the run stopped keeping
        samples of itself, the chart read a recorded window instead (`PL-2FM6`).

        **The axis is a viewport, and the run fills it.** Both bounds come from
        the axis that the caller has just set, and that axis may legitimately
        extend past the run. `chart_time_base.following_window` keeps
        `live_headroom_s` of empty axis to the right of the newest instant.
        `fitted_window` returns the chosen rung's full width however short the
        run is. Both do this deliberately, so that the width a trace is drawn
        at is fixed and its slope means the same thing at every moment of every
        run. So the drawn range is clipped to the part of the axis that the run
        covers. That clipping is not the coercion `CLAUDE.md` forbids. Nothing
        is substituted or defaulted, and `DrawnWindow.times_s` says exactly
        which instants came back. So a caller can see where the run ends,
        rather than being given a value for an instant the run never reached.
        The run definition itself rejects a request for those instants, and
        rightly so. See `evaluate_anchored`.

        **The column spacing comes from the axis, not from the clipped
        range.** That keeps the grid anchored. The span is a property of the
        selected time base, so it is constant. The evaluated instants
        therefore stay in place as the window follows the run, and only the
        newest column is new. Deriving the spacing from the clipped range
        instead would move every column on every frame early in a run. That is
        the defect `RunDefinition.evaluate_anchored` exists to avoid.

        Args:
            start_s: Left edge of the axis, in simulated seconds.
            stop_s: Right edge of the axis, in simulated seconds. It must not
                be before `start_s`.
            columns: The number of grid columns the axis is divided into, at
                least two. The points actually drawn are these columns plus
                the control events inside the window and the two ends of the
                drawn range. So this value bounds the grid, not the number of
                points.

        Returns:
            The states at the drawn instants, bound to this run's agent.

        Raises:
            SimulationConfigurationError: If `columns` is below two, either
                bound is not finite, or `stop_s` precedes `start_s`.
        """

        if columns < 2:
            raise SimulationConfigurationError(
                f"an axis is divided into at least two columns, not {columns}"
            )

        if not isfinite(start_s) or not isfinite(stop_s):
            raise SimulationConfigurationError(
                f"an axis runs between finite instants, not ({start_s}, {stop_s})"
            )

        if stop_s < start_s:
            raise SimulationConfigurationError(
                f"an axis from {start_s} s to {stop_s} s ends before it begins"
            )

        spacing_s = (stop_s - start_s) / (columns - 1)
        # The axis and the run definition use one clock, so nothing is
        # converted here. The range is only clipped to the span the run
        # actually holds. The lower clip is where this run *began*, not zero.
        # A branch begins at its fork, and the axis may legitimately extend to
        # the left of the fork. `RunDefinition` rejects an instant from before
        # a run existed, rather than returning a value from its nearest keyframe.
        first_s = max(start_s, self.began_at_s)
        last_s = min(stop_s, self._run_definition.reached_s)

        if last_s < first_s:
            # The axis and the run do not overlap. Two ordinary states cause
            # this, and neither is an error. One is an axis entirely ahead of
            # a run at the very start of the run. The other is an axis entirely
            # to the left of a branch's fork, which a learner sees before the
            # branch point scrolls into view. An empty window draws nothing,
            # which is not the same as drawing a zero.
            return DrawnWindow(substance_id=self._agent_id, times_s=(), states=())

        # An axis of zero width is one instant, and it is still drawn. Both
        # bounds coincide, so no grid column can fall strictly between them,
        # and the spacing substituted here cannot place one there.
        window = self._run_definition.evaluate_anchored(
            first_s, last_s, spacing_s if spacing_s > 0.0 else 1.0
        )

        return DrawnWindow(
            substance_id=self._agent_id, times_s=window.times_s, states=window.states
        )

    def start(self) -> None:
        """Start or resume the run, refusing a session that cannot continue.

        Raising an error rather than quietly declining is deliberate. If a
        start were silently ignored, the interface would show a stopped run
        with no sign that starting it did nothing. That is the hidden mode
        `CLAUDE.md` forbids.

        Two states are refused, for the same reason but with different
        meanings. A failed session would raise again on its first tick. A
        session standing at the supported run length would have its first
        step refused by the core. Neither can be resumed. Each error says
        which state it is, so a caller reporting the refusal does not have to
        guess.
        """

        if self._failure_reason is not None:
            raise SimulationExecutionError(
                f"cannot resume a failed simulation ({self._failure_reason}); reset it first"
            )

        supported_limit_reason = self.supported_limit_reason

        if supported_limit_reason is not None:
            raise SimulationDomainLimitError(
                f"this run has reached the supported run length "
                f"({supported_limit_reason}); reset it to start a new run"
            )

        if not self._is_running:
            self._keep_crossings_stood_on()

        self._is_running = True

    def pause(self) -> None:
        self._is_running = False

    def reset(self) -> None:
        """Stop the run, clear any failure or limit, and clear dynamic state.

        Settings are preserved. So are the bookmarks, which are the learner's
        questions rather than the run's product. A reset is for running the
        same case again, and it is the same case the learner was asking about.
        This method and `set_agent` are the ways out of a failed session, and
        out of a session standing at the supported run length. Every
        compartment goes back to its initial state and the step count goes
        back to zero, so nothing carries over from the run that could not
        continue.

        **A branch goes back to its fork rather than to zero**, because that
        is where the branch began. A branch does not hold the case's induction
        state. Clearing the branch to an empty system would put the patient at zero
        agent, at a case time when the model says the patient is loaded. That
        is a plausible state that never happened. `CLAUDE.md`'s safety-critical
        standard prefers an obvious failure to that outcome. The branch's clock
        goes back to the fork instant too, so the case's supported run length
        is spent from where the branch actually starts. A branch forked on the
        limit itself has no run length left to spend. So a reset leaves it
        standing there, stopped, rather than offering a Start that the core
        would refuse (`PL-5291`).

        Raises:
            SimulationConfigurationError: If the settings record on which the run
                definition opens cannot be built from the values the
                compartments hold. That happens when the tissue flows no
                longer sum to the cardiac output. Since `PL-HQF5` and
                `PL-Z0HN`, only a perfusion fraction written in a way that
                bypasses its guard can make them disagree. The error is raised
                before anything is cleared, so the run is exactly as it was.
                It is still running if it was, and its state, run definition,
                timeline and any recorded failure are unchanged. The interface
                halts the run on this error (`RunView._handle_reset`), because
                the record refused here is the one the next step would be
                refused on (`PL-M4M0`).
        """

        # Read the settings record before anything is cleared, because building it
        # is the one step here that the core can refuse (see above). The
        # record holds no dynamic value, so the record read here is the one the
        # cleared system would give afterwards (`PL-M4M0`).
        settings = self._state.uptake_system.equation_settings()

        self.pause()
        self._failure_reason = None
        self._failed_frame_reason = None
        self._recorded_supported_limit_reason = None
        self._forget_reached_marks()
        self._state.reset()
        uptake_system = self._state.uptake_system

        if self._opened_from is not None:
            # A branch's beginning is the fork. The branch cannot return to the
            # case's induction, because it never held that state. Resetting to
            # a cleared system would put the patient at zero agent at a case
            # time when the model says the patient is loaded. That is a
            # plausible state that never happened, not the start of anything.
            self._open_at(self._opened_from, settings)
            return

        self._run_definition = RunDefinition(
            settings, uptake_system.state_vector(), opened_at_s=CaseInstant(0.0)
        )
        self._note_recorded_settings()
        self._clear_control_timeline()

    # There is deliberately no `set_circuit_volume` here (`PL-GYH2`). The
    # circuit volume is a fixed model parameter, not a control. It is set once,
    # when this controller builds the system, and no interface control changes
    # it after that. The setter that used to be here was public and unbounded.
    # So it gave every caller of the app layer a way to set a circuit volume
    # outside anything `docs/MODEL.md` verifies, for a control that no teaching
    # case has asked for. `BreathingCircuit.set_circuit_volume` stays, because
    # it is the only way `_build_state()` can pass the parameter to the circuit.
    # What was removed is the app-level passthrough, not the core primitive.
    # `docs/MODEL.md` § "What is not bounded this way" gives the argument.

    def set_fresh_gas_flow(self, fresh_gas_flow_l_min: FreshGasFlow) -> None:
        system = self._state.uptake_system
        previous_value = system.circuit.fresh_gas_flow_l_min
        system.set_fresh_gas_flow(fresh_gas_flow_l_min)
        self._record_control_change(
            ControlInput.FRESH_GAS_FLOW,
            previous_value,
            system.circuit.fresh_gas_flow_l_min,
            restore=lambda: system.set_fresh_gas_flow(previous_value),
        )

    def set_delivered_concentration_percent(self, delivered_concentration_percent: Percent) -> None:
        system = self._state.uptake_system
        previous_value = system.circuit.delivered_concentration_percent
        system.set_delivered_concentration_percent(delivered_concentration_percent)
        self._record_control_change(
            ControlInput.DELIVERED,
            previous_value,
            system.circuit.delivered_concentration_percent,
            restore=lambda: system.set_delivered_concentration_percent(previous_value),
        )

    def set_alveolar_ventilation(self, alveolar_ventilation_l_min: AlveolarVentilation) -> None:
        system = self._state.uptake_system
        previous_value = system.alveoli.alveolar_ventilation_l_min
        system.set_alveolar_ventilation(alveolar_ventilation_l_min)
        self._record_control_change(
            ControlInput.ALVEOLAR_VENTILATION,
            previous_value,
            system.alveoli.alveolar_ventilation_l_min,
            restore=lambda: system.set_alveolar_ventilation(previous_value),
        )

    def set_cardiac_output(self, cardiac_output_l_min: CardiacOutput) -> None:
        system = self._state.uptake_system
        previous_value = system.patient.cardiac_output_l_min
        system.set_cardiac_output(cardiac_output_l_min)
        self._record_control_change(
            ControlInput.CARDIAC_OUTPUT,
            previous_value,
            system.patient.cardiac_output_l_min,
            restore=lambda: system.set_cardiac_output(previous_value),
        )

    def begin_control_adjustment(self) -> None:
        """Declare that the changes that follow are a new user adjustment.

        The interface calls this when a drag begins. Without it, a slider
        dragged twice would be indistinguishable from one dragged once. Both
        arrive as a series of changes to the same control, and only the input
        device knows where one action ended and the next began. Inferring the
        boundary from the timing of the entries would need a threshold. No
        threshold survives the playback multiplier that v0.4.0 adds, because
        the same drag spans more simulated time the faster the run is played.

        This method records nothing on its own and changes no simulation
        state. It only closes whichever adjustment is open, so the next change
        starts a new one. A change that arrives with no adjustment open, such
        as a key press on a slider, a programmatic call or a test, therefore
        becomes an adjustment of its own. That is the honest reading of a
        single discrete input. It is also why the grouping degrades safely,
        rather than wrongly, when this method is never called.
        """

        self._open_adjustment_control = None

    def _note_recorded_settings(self) -> None:
        """Remember the core's settings as the run definition now records them.

        Called after every write to `_run_definition` that can change its
        settings: where a run is built, where a branch opens, at Reset and at
        a recorded control change. `_require_core_settings_recorded` compares
        against what this stores.
        """

        self._recorded_settings_key = self._state.uptake_system.settings_key()

    def _require_core_settings_recorded(self) -> None:
        """Refuse a step once the core's settings differ from the run's record.

        The readouts come from the steps, which run at whatever the core
        holds. The chart comes from the run definition, which holds only the
        settings this controller recorded. So a setting written to the core
        without going through this controller, such as `AgentUptakeSystem.set_cardiac_output`
        or a compartment's own setter, would make the two show different
        runs. This check stops the run before the first step at the
        unrecorded setting instead (`PL-XRN8`). Nothing in `app/` writes to
        the core that way. The check is there so that a future caller fails
        here, visibly, rather than drawing a chart that disagrees with the
        values beside it.

        Where the settings now on the core are inconsistent, building the
        settings record refuses them first, with the more specific message
        that names the values that disagree.

        Reset starts a new run from the settings the core holds, so it clears
        the refusal.

        A setting changed through this controller is not checked here.
        `_record_control_change` records the whole settings record, so the
        run definition then matches the core again, whatever else had moved.
        Checking before the write would also refuse a perfusion fraction
        written in a way that bypasses its guard, before `_record_control_change`
        could write the setting back. `PL-VCP4`'s tests check that write-back.

        Raises:
            SimulationConfigurationError: If the settings on the core fail the
                settings record's own checks.
            SimulationExecutionError: If they pass those checks but differ
                from the settings the run definition records.
        """

        system = self._state.uptake_system

        if system.settings_key() == self._recorded_settings_key:
            return

        system.equation_settings()

        raise SimulationExecutionError(
            "A setting was changed on the simulation core without "
            "SimulationController recording it, so the chart, which is drawn "
            "from the recorded settings, would no longer match the values "
            "shown. Change settings through SimulationController. Reset starts "
            "a new run from the settings the core now holds."
        )

    def _record_control_change(
        self,
        control: ControlInput,
        previous_value: float,
        new_value: float,
        *,
        restore: Callable[[], None],
    ) -> None:
        """Record one setting change, after the core has accepted it.

        This is called *after* the forwarding setter returns, so a refused
        setting records nothing. The core raises before this line is reached,
        and the exception reaches the interface. The core left the run
        unchanged, and the run keeps a timeline that says so.

        **The settings record can refuse a value that its compartment
        accepted** (`PL-VCP4`). A compartment checks only its own field, but
        the record checks the fields against each other. Building the record
        can then fail after the setter has already written the new value. So
        `restore` writes the previous value back through the same setter
        before the error is raised. The compartment, the run's definition
        and the timeline then all hold the previous setting, and the
        interface is right to say that the simulation is unchanged.
        `restore` cannot fail, because it writes a value that was in force.

        No write that its own guard checks can now lead the record to refuse.
        The record's one cross-field check is that the tissue flows sum to the
        cardiac output. Every flow is formed from the output when it is read
        (`PL-HQF5`), and a tissue's perfusion fraction cannot change once its
        patient has checked that the fractions sum to 1 (`PL-Z0HN`). Before
        those two items, a flow set directly on a tissue, or a changed
        fraction, led the record to refuse every later setting change. The
        write-back stays, because a fraction written in a way that bypasses
        its guard still leads to a refusal, and the tests produce one that way.

        Both values are read from the compartment that holds them, not taken
        from the caller's argument. The core rejects an out-of-range setting
        rather than clamping it, so the two are equal today. But if that ever
        stopped being true, a record of what was *asked for* would silently
        become a record of something the run never used. This timeline's whole
        claim is that applying it again reproduces the run.

        Two kinds of change are deliberately not recorded. In both, the model
        saw nothing:

        - a value equal to the one already in place, which a slider emits
          freely as a drag returns to a position; and
        - a change replaced by another within the same simulation step. Only
          the value in place when `advance()` runs is integrated. So a dial
          moved from 2% to 3% to 4% between two steps is, for the run, one
          change from 2% to 4%. Collapsing such changes makes the timeline a
          record of the run rather than of the mouse. If the collapse ends on
          the value the step began with, the entry is removed entirely,
          because nothing about the run differs.
        """

        if new_value == previous_value:
            return

        # Build the record before recording anything, because building it is
        # the only step here that the core can refuse (see the docstring).
        try:
            settings = self._state.uptake_system.equation_settings()
        except SimulationConfigurationError:
            restore()
            raise

        # Update the run definition first, because it is the run. The timeline
        # below records the actions a reader sees, and every conditional that follows
        # is about how those actions are grouped and displayed. Both records are
        # updated here rather than in the four setters, because this is the one
        # place that means "the core accepted a setting change".
        self._run_definition.record_change(settings)
        self._note_recorded_settings()

        if control is not self._open_adjustment_control:
            self._adjustment_count += 1
            self._open_adjustment_control = control
            self._open_adjustment = self._adjustment_count

        # Two changes to one control inside a single step are one action. The
        # model integrated only the last value, so recording both would
        # describe settings the run was never computed under. Changes are
        # compared by their instant. Now that there is no sample index to stand
        # in for a step, the instant is what identifies a step (`PL-2FM6`).
        #
        # **The loop searches back across this instant rather than reading
        # only the newest entry** (`PL-TFX5`). Looking only at `[-1]` collapses
        # a control moved twice in a row. It misses the same control moved
        # twice with another control's move between them. So when two dials
        # were nudged and both put back, interleaved, four entries remained at
        # an instant at which the run did not change. Meanwhile
        # `RunDefinition.record_change` correctly recorded nothing, because it
        # compares whole settings with the previous stretch and so does not
        # depend on order. The two records then disagreed about when the run
        # changed, which is the one thing they are supposed to agree about. And
        # `resumed_at` refuses to fork at a recorded control event with no
        # keyframe behind it. This case can happen while the run is paused,
        # when `advance()` does nothing and every control a learner touches
        # carries the same instant.
        for index in reversed(range(len(self._control_timeline))):
            entry = self._control_timeline[index]

            if entry.elapsed_s != self._state.elapsed_s:
                break

            if entry.control is not control:
                continue

            if entry.previous_value == new_value:
                self._control_timeline = (
                    *self._control_timeline[:index],
                    *self._control_timeline[index + 1 :],
                )
                return

            self._control_timeline = (
                *self._control_timeline[:index],
                replace(entry, new_value=new_value),
                *self._control_timeline[index + 1 :],
            )
            return

        self._control_timeline = (
            *self._control_timeline,
            ControlChange(
                elapsed_s=self._state.elapsed_s,
                adjustment=self._open_adjustment,
                control=control,
                previous_value=previous_value,
                new_value=new_value,
                unit=CONTROL_INPUT_UNITS[control],
            ),
        )

    def _compartment_mac_multiples(
        self, state: tuple[float, ...]
    ) -> Mapping[RecordedQuantity, MacMultiple]:
        """Every compartment a target could name, read from `state`, in the unit a target uses.

        Each compartment is converted once, through `formatting.mac_multiple`
        and this run's own `agent_mac_percent`. That is the same divisor
        through which the readout for that compartment is drawn. So a target and the number the
        learner is looking at cannot come to mean different things.

        `COMPARTMENT_STATE_INDEX` pairs each quantity with its position, so no
        second list is written here. It is already the one place where a trace
        could come to carry another compartment's values. A crossing tested
        against the wrong compartment is the same defect as a trace drawn from
        the wrong one. Each entry is built as a `Fraction` under the
        compartment's name, because the vector returns the quotients that the
        compartments derive from the amounts they hold (`PL-7DJK`).

        Args:
            state: A state vector in `governing_equations`' order. It is the
                live system's vector for a step that `advance` is taking. Or
                it is from `RunDefinition.state_at`, for a step that
                `_crossing_of_step` asks about after the fact, for a fork or
                for the standings.

        Raises:
            SimulationConfigurationError: If a compartment's quotient is
                outside 0 to 1, naming the compartment.
        """

        return {
            quantity: mac_multiple(
                Fraction(state[index], name=COMPARTMENT_FRACTION_NAMES[quantity]),
                self._agent_mac_percent,
            )
            for quantity, index in COMPARTMENT_STATE_INDEX.items()
        }

    def bookmark_standings(self) -> BookmarkStandings:
        """Return the standing of each of this run's marks, without using a compartment value.

        The snapshot carries these standings. A halt also reads them directly, from this
        method (`SimulationView._restate_bookmark_panel`). When a halt comes from a failed
        frame, `snapshot()` may refuse as well, so the halt cannot read the standings
        from a snapshot. Every input below comes from the run's own record: the
        instants and heights it reached, its opening instant, its clock, the run-length
        guard and the failure. None of these inputs builds a `Fraction`. So this method
        cannot raise for a value that a frame would refuse (`PL-YHR3`).

        **Both reasons for which `start` refuses to resume are passed on, because
        each one means the run can go no further** (`PL-N3N5`). A standing says
        whether a mark can still be reached, and only this controller knows that.
        The controller keeps the two reasons as `supported_limit_reason` and
        `_failure_reason`. `start` checks exactly these two to decide that the run
        cannot be resumed at all. When only the run-length cap was passed on and
        the failure was not, every mark on a failed run was shown as one the run
        had not reached *yet*, although its next step would raise as its last one
        did.

        **The marks the run crossed include those crossed by two particular
        steps, checked against the marks as they are now** (`PL-1ZQ4`,
        project owner 2026-10-17, ratified). The two steps are the step a
        branch opened on and, while the run is stopped, the step it stopped
        on. A mark that lies inside either step counts as crossed by that step.
        The marks are the ones that exist at this call, not the ones that
        existed when the step was taken. So a mark added after the step has the
        same standing on the trunk and on every branch, whichever came first,
        the mark or the branch.
        """

        stood_on = self._crossings_stood_on()

        return self._bookmarks.standings(
            reached_instants_s=self._reached_instants_s.union(
                *(_reached_instants(crossing) for crossing in stood_on)
            ),
            reached_crossings=self._reached_crossings.union(
                *(_reached_heights(crossing) for crossing in stood_on)
            ),
            opened_at_s=self.began_at_s,
            elapsed_s=self._state.elapsed_s,
            stopped_at_cap=self.has_reached_supported_limit,
            run_failed=self._failure_reason is not None,
        )

    def _crossings_stood_on(self) -> tuple[BookmarkCrossing, ...]:
        """What the step this run opened on and the step it stands on crossed, using current marks.

        There are two steps, and the second applies only while the run is
        stopped:

        - **The step a branch opened on.** It is checked at every read,
          however far the branch has run since. The branch opens standing on
          it (`ResumePoint.stepped_from`), as a fork at a halt always has.
        - **The step at whose end a stopped run's clock stands.** This applies
          whether the run is paused or halted, at its cap or not, and on a
          trunk or a branch. A run that is advancing stands on no step,
          because its position moves with every step. A failed run is left out
          too, because a failure is not a pause (`RunStatus.failure_reason`)
          and `resumed_here` refuses to branch there. `start` keeps what this
          step crossed when the run leaves it (`_keep_crossings_stood_on`). So
          a mark shown as reached while the run stood on its step is still
          shown as reached once the run moves on.

        A trunk treats a mark the same way as a branch opened on the same step,
        because both ask about the same step through `_crossing_of_step`, from
        the same canonical states at both ends.
        """

        if self._bookmarks.is_empty:
            return ()

        steps: list[tuple[Keyframe | None, Keyframe]] = []
        standing_on_fork = False

        if self._opened_from is not None:
            steps.append((self._opened_from.stepped_from, self._opened_from.fork))
            standing_on_fork = self._state.step_count == self._opened_from.step_count

        if not self._is_running and self._failure_reason is None and not standing_on_fork:
            elapsed_s = self._state.elapsed_s
            steps.append(
                (
                    self._keyframe_before(self._state.step_count),
                    Keyframe(elapsed_s, self._run_definition.state_at(elapsed_s)),
                )
            )

        return tuple(
            crossing
            for stepped_from, stepped_to in steps
            if (crossing := self._crossing_of_step(stepped_from, stepped_to)) is not None
        )

    def _keep_crossings_stood_on(self) -> None:
        """Record what the step this run stands on crossed, as the run leaves it.

        `start` calls this method. While the run is stopped,
        `_crossings_stood_on` reports the step it stands on. Once the run is
        advancing, that step is behind it. So what the step crossed is added
        to what the run has done, as `_halt_on` does with a halt's crossing.
        Without this, a target added while the run stood on its step would be
        shown as reached until Start and as not reached after it, although
        nothing about the target or the step had changed.
        """

        for crossing in self._crossings_stood_on():
            self._reached_instants_s |= _reached_instants(crossing)
            self._reached_crossings |= _reached_heights(crossing)

    def advance(self, simulation_step_s: SimulationStep) -> None:
        """Do nothing while paused; otherwise advance state, record history, and halt on a crossing.

        The run definition's reach is moved after the step rather than before
        it. So a step the core refuses, for a domain limit or a numerical
        failure, leaves the run definition describing a run that stopped where
        the state did. The run definition's `advance_to` records no state. The
        settings already imply the states, which are recovered from them on
        demand.

        **The crossing test is here because this is where one step happens**
        (`PL-CTD7`). The interface advances a whole tick's worth of steps
        between frames: `multiplier x tick_interval_s / simulation_step_s`
        steps, which is 300 at 300x. A test applied once per frame would place
        the halt up to `multiplier x simulation_step_s` past the value the
        learner marked. That is 30 simulated seconds at 300x and 0.1 s at 1x,
        against a `docs/MODEL.md` tolerance stated in hundredths of a
        percentage point. The same bookmark would then silently stop the run
        at a different concentration depending on the playback speed. That is
        the presentation-correctness failure `CLAUDE.md` treats as
        safety-critical. It would also put two branches that were nominally
        taken "at 0.8 xMAC" at two different states. Because the test runs on
        every step, the halt lands on the crossing step itself. That is finer
        than any instant a live control change can reach (`app/playback.py`,
        `PL-NBWP`).

        **A crossing pauses the run**, and that makes the halt genuinely useful
        rather than a courtesy. No step is taken while paused, and the setters
        apply unconditionally. So "halt at 0.8 xMAC, then turn the vaporizer
        off" takes effect at the instant the learner was looking at. Without
        the pause, it would take effect at the next tick boundary, up to 30
        simulated seconds later. The pause is an ordinary one. `start()`
        resumes the run, and resuming does not count the crossing it halted on again,
        because the next step's `before` reading is the halting step's own
        reading (`MacTarget.crossed_between`). Nothing is armed or disarmed, so
        there is no per-target state for a learner to get wrong.

        The remaining steps of the tick that halted do nothing, because of the
        guard at the top of this method. So the burst of steps stops on the
        crossing step rather than running on to the frame boundary.

        The readings are taken only when something is marked, so an unmarked
        run costs nothing extra. A marked run costs two `state_vector()` reads
        and six divisions per step.

        **The run halts on the step that brings it to the supported run
        length, not on the rejected step after it** (`PL-5291`). The core
        refuses the step *from* the last supported count. A run stopped only
        by that refusal would stand on that count, between the arriving step
        and the refused one, shown as running. If Pause landed there, it would
        be shown as paused with Start offered. Yet no step is left to take.
        Halting on arrival, as `_halt_on` does on a crossing, keeps
        `is_running` false whenever `supported_limit_reason` is set. That is
        the contract `SimulationSnapshot.supported_limit_reason` states. The
        values the run stops on come from the same completed step either way.
        What changes is when the stop is reported.
        """

        if not self._is_running:
            return

        self._require_core_settings_recorded()

        # Taking a step means the run is no longer standing on the crossing it
        # last halted at, whether or not this step then completes.
        self._bookmark_halt = None

        if self._bookmarks.is_empty:
            self._state.advance(simulation_step_s)
            self._run_definition.advance_to(self._state.elapsed_s)
        else:
            before_s = self._state.elapsed_s
            before = self._compartment_mac_multiples(self._state.uptake_system.state_vector())

            self._state.advance(simulation_step_s)
            # The clock and the run definition's reach are one quantity on one
            # time axis, on a branch as well as on a trunk. So the reach is the
            # clock, and no offset appears here or anywhere else.
            # `docs/MODEL.md` § "The canonical evaluation rule" now requires
            # this. When a branch is asked for an instant of the case, it
            # computes its interval from the same two floats its parent used,
            # not from a difference that may not round-trip.
            self._run_definition.advance_to(self._state.elapsed_s)

            crossing = self._bookmarks.crossings_between(
                before_s=before_s,
                after_s=self._state.elapsed_s,
                before=before,
                after=self._compartment_mac_multiples(self._state.uptake_system.state_vector()),
            )

            if crossing is not None:
                self._halt_on(crossing)

        self._halt_on_arrival_at_supported_limit()

    def _halt_on_arrival_at_supported_limit(self) -> None:
        """Pause the run where the step just taken was the last supported one.

        Nothing is recorded. `supported_limit_reason` reads the limit from the
        state, and the run stands at the limit from this step on. Only
        `_is_running` changes. It is the one fact that the state does not
        carry and that the snapshot's contract needs. A limit reason shown
        beside a live Pause button would be a stopped run presenting itself as
        running.
        """

        if self._reason_the_next_step_would_be_refused() is not None:
            self._is_running = False

    def _halt_on(self, crossing: BookmarkCrossing) -> None:
        """Pause the run on the step that crossed these marks, and record it.

        Args:
            crossing: What the step just taken passed through.
        """

        self._is_running = False
        self._bookmark_halt = crossing
        self._reached_instants_s |= _reached_instants(crossing)
        self._reached_crossings |= _reached_heights(crossing)


def _reached_instants(crossing: BookmarkCrossing) -> frozenset[CaseInstant]:
    """The marked instants that `crossing` reached, in the form the standings match on."""

    return frozenset(bookmark.instant_s for bookmark in crossing.time_bookmarks)


def _reached_heights(crossing: BookmarkCrossing) -> frozenset[tuple[RecordedQuantity, float]]:
    """The marked heights that `crossing` reached, each given by its `MacTarget.crossing_key`."""

    return frozenset(target.crossing_key for target in crossing.mac_targets)


class BranchedCase:
    """One case, held as the run that happened and the branches taken from it.

    `SimulationController.resumed_at` makes a branch, and this class makes a
    *case* of the runs that result. That relationship is what v0.5.0 exists to
    assert: two curves on one axis are one patient under two managements, not
    two patients. Without an object that holds the relationship, the
    controllers returned by two `resumed_at` calls are indistinguishable from
    two unrelated sessions. Each knows the instant it opened at
    (`opened_from`), but none knows that the others opened from the same run.

    **The case is flat by construction, not by refusal** (`PL-TFX5`, project
    owner, 2026-08-25). It has one trunk with N branches. Sub-forks of forks
    are deliberately excluded, because they multiply without bound and offer
    little over branching again from the trunk. Every fork here is taken
    from the trunk, so this class cannot express a branch of a branch at all,
    rather than declining one. `resumed_at` still refuses one, because a
    caller that holds a branch can call it directly. The two guards answer
    different questions. That one says *this run* cannot be forked. This one
    says there is no second generation to fork from. An interface in which
    the error cannot be expressed is the stronger of the two. The weaker
    guard is kept as well, because it covers the route around this class.

    **Two branches may be taken at the same instant, deliberately.** That is
    the comparison the milestone is named for, one decision point and two
    managements, so nothing here makes a fork point unique.

    **It computes nothing and advances nothing.** Running, pausing, settings
    and stepping stay on the controllers, one per run. This class holds which
    runs there are and how they are related, so a view can loop over them and
    a reader can attribute a curve to one of them. It does not depend on Flet,
    for the same reason that the rest of `app/` outside the view does not.
    """

    def __init__(self, trunk: SimulationController) -> None:
        """Hold `trunk` as the run every branch of this case is taken from.

        Raises:
            SimulationConfigurationError: `trunk` is itself a branch. A case
                built on a branch would be a second generation disguised as a
                trunk. Its forks would be sub-forks, which this project
                excluded on purpose rather than leaving unimplemented. The
                refusal rests on that reason alone. It once also rested on
                such a case offering instants measured from another case's
                fork. `PL-ZMRT` retired that reason, because every run's
                instants are now on the case's axis. A later reader would
                remove a guard defended by an argument that has stopped being
                true.
        """

        if trunk.opened_from is not None:
            raise SimulationConfigurationError(
                f"a case is rooted in a trunk, and this run is a branch opened at "
                f"{trunk.opened_from.fork.instant_s} s; branches of branches are excluded "
                "rather than unimplemented, so build the case on the run the branch came from"
            )

        self._trunk = trunk
        self._branches: tuple[SimulationController, ...] = ()

    @property
    def trunk(self) -> SimulationController:
        """The run the case actually took, and the only one a fork is taken from."""

        return self._trunk

    @property
    def branches(self) -> tuple[SimulationController, ...]:
        """The branches taken from the trunk, in the order they were taken.

        They are listed oldest first, in the order of the actions rather than
        of the fork instants. A learner may fork late, then go back and fork
        early. A list sorted again by instant would renumber the branch the
        learner was looking at. Two branches taken at one instant keep the
        order they were made in.
        """

        return self._branches

    @property
    def runs(self) -> tuple[SimulationController, ...]:
        """Every run of this case: the trunk first, then `branches`.

        A view loops over this tuple. The trunk comes first because it is the
        run that happened, and every branch departs from it. So a reader who
        goes through the list in order meets the case before its alternatives.
        """

        return (self._trunk, *self._branches)

    @property
    def fork_points_s(self) -> tuple[CaseInstant, ...]:
        """The case instants at which a fork may be taken, earliest first.

        These are the trunk's keyframes: its opening at induction, and every
        setting change the model was actually stepped under. That is what
        `PL-TFX5` means by "any recorded control-input-timeline event", and it
        is the scope of `fork_at`. `fork_at` rejects any other instant. The
        reason is not that a branch could not reproduce the trunk there. It is
        that another method covers that instant (`PL-54V0`). A marked instant
        goes through `fork_at_mark`, from `mark_fork_points`. The place where
        the paused trunk stands goes through `fork_here`, from
        `here_fork_point`.

        Induction is included rather than filtered out. A fork at zero is a
        second management of the whole case, which is a comparison a learner
        may legitimately want. It is a strange one to offer under a control
        labelled "branch here", but that is for the interface to judge, not
        for this list to decide in advance.

        A **bookmark** is not one of these instants and does not become one
        (`PL-B8MK`). Making it one would mean recording a keyframe where the
        run halted. That keeps the branch exact against its parent, but it
        changes the parent's own later results, so marking a run would change
        it. A fork at a mark is taken through `fork_here` or `fork_at_mark`
        instead. Neither needs a keyframe, so neither adds an instant to this
        list.

        **The tuple is empty while the trunk refuses every fork** (`PL-T2Q2`).
        On a trunk, that means its frame has failed
        (`SimulationController.fork_refusal`). A trunk that failed on its own
        step keeps its keyframes here. Each keyframe is a state the run
        computed before the failure, and a branch from one is drawn normally.
        """

        if self._trunk.fork_refusal is not None:
            return ()

        return tuple(segment.opening.instant_s for segment in self._trunk.run_segments)

    @property
    def mark_fork_points(self) -> tuple[MarkForkPoint, ...]:
        """The marked instants at which a fork may be taken: every time bookmark the trunk passed.

        This is the list for `fork_at_mark`, as `fork_points_s` is the list for
        `fork_at`. It is ordered earliest first, and each entry carries the
        instant where a branch taken there opens (`PL-W4XQ`). It changes as
        the case does. A mark joins it when the trunk's clock reaches the
        mark, or when the mark is set behind the clock. A mark leaves it only
        when the learner removes the mark or the trunk starts over. That is
        the same lifetime as the keyframes beside it. It is not the lifetime
        of `here_fork_point`, which ends when the trunk starts again.

        Like `fork_points_s`, it is empty while the trunk refuses every fork.
        """

        if self._trunk.fork_refusal is not None:
            return ()

        return self._trunk.mark_fork_points

    @property
    def here_fork_point(self) -> HereForkPoint | None:
        """Where the paused trunk stands, as `fork_here`'s place to branch, or None.

        This is the trunk's `SimulationController.here_fork_point`. It is None
        while the trunk is advancing, has failed, or stands at its opening or
        at the supported run length (`PL-Y2SL`). It ends when the trunk starts
        again, whereas the entries in `fork_points_s` and `mark_fork_points`
        stay until the case changes.
        """

        return self._trunk.here_fork_point

    def fork_at(self, instant_s: CaseInstant) -> SimulationController:
        """Take a branch from the trunk at `instant_s`, and keep it.

        The trunk is left exactly as it was, because `resumed_at` reads it and
        writes nothing. So the case gains a run rather than trading one run
        for another, which makes this a comparison instead of an undo.

        Args:
            instant_s: The case instant to branch at, in seconds, from
                `fork_points_s`.

        Returns:
            The new branch, paused at the trunk's state at that instant,
            carrying the trunk's agent and patient. It is also appended to
            `branches`, so a caller that discards the return value has not
            lost it.

        Raises:
            TypeError: `instant_s` is not a `CaseInstant`.
            SimulationConfigurationError: `instant_s` is not one of
                `fork_points_s`, which is empty once the trunk's frame has
                failed. Or `instant_s` is not a whole number of the trunk's
                steps. Or the branch rebuilt there would not hold what the
                trunk held. `resumed_at` raises these errors and names which
                case applies.
        """

        return self._kept(self._trunk.resumed_at(instant_s))

    def fork_here(self) -> SimulationController:
        """Take a branch from the trunk where it is paused, stopped on a mark or not, and keep it.

        This branches at the decision point where a learner paused, in one
        action (`PL-Y2SL`). On a bookmark halt, it is also the second half of
        `ROADMAP.md`'s v0.5.0 Definition of done, "a branch taken at any
        recorded control event **or bookmark**", where `fork_at` is the first
        half. It takes no instant, because the fork is the step the trunk is
        standing on. `SimulationController.resumed_here` explains why that is
        the interface, rather than a wider `fork_at`.

        Returns:
            The new branch, paused at the trunk's state where the trunk
            stands, carrying the trunk's agent and patient. It is also
            appended to `branches`, so a caller that discards the return value
            has not lost it. The trunk is left standing where it was.

        Raises:
            SimulationConfigurationError: The trunk is advancing, has failed,
                or stands at its opening or at the supported run length. Or
                the branch rebuilt there would not hold what the trunk held.
                `resumed_here` raises these errors and names which case
                applies.
        """

        return self._kept(self._trunk.resumed_here())

    def fork_at_mark(self, bookmark: TimeBookmark) -> SimulationController:
        """Take a branch from the trunk at a time bookmark it has passed, and keep it.

        This is the return to a mark that the owner described (`PL-W4XQ`). A
        learner paused at 3 h marks 1 h and goes back to try something else
        there. It takes the mark from `mark_fork_points` rather than an
        instant. `SimulationController.resumed_at_mark` explains why. It also
        explains why the branch is the one that the halt would have given.

        Args:
            bookmark: The mark to branch at, from `mark_fork_points`.

        Returns:
            The new branch, paused at the step that reached the mark, carrying
            the trunk's agent and patient. It is also appended to `branches`,
            so a caller that discards the return value has not lost it. The
            trunk is left exactly as it was.

        Raises:
            SimulationConfigurationError: The trunk's frame has failed. Or the
                trunk holds no time bookmark at that instant, or has not passed
                it. Or the branch rebuilt there would not hold what the trunk
                held. `resumed_at_mark` raises these errors and names which
                case applies.
        """

        return self._kept(self._trunk.resumed_at_mark(bookmark))

    def _kept(self, branch: SimulationController) -> SimulationController:
        """Add `branch` to this case and return it."""

        self._branches = (*self._branches, branch)

        return branch
