"""SimulationController: the boundary between the UI and the scientific
core. Owns run/pause/reset state, applies user-facing settings to the
core, and exposes read-only `SimulationSnapshot`s for the view to render.
Contains no physiological calculations of its own, and holds no default
values of its own: every unspecified setting comes from the core, which
builds it from the versioned data files.

The vocabularies a run is *addressed* by are not here and are imported like
anything else: `app/control_record.py` for what a run can be set to and what
a setting change records, `app/run_series.py` for what a trace names and
what one drawn frame reads (`PL-RD3B`). Neither imports this module, so a
reader of either is not reading the boundary as well.
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

# `mac_multiple` rather than an inverse transform written here, and the import
# is the point: it is the whole arithmetic of the second display unit in one
# place, so a target held in multiples of MAC is compared against a compartment
# through the same divisor the readout beside it is drawn through. Converting
# the *target* down into a partial-pressure fraction here would be a second
# copy of that arithmetic, and `CLAUDE.md` treats a correct number reached
# through the wrong divisor as a safety failure rather than a rounding one.
# Nothing else about `app/formatting.py` is reached: no string is built here.
from anesthesia_sim.app.formatting import mac_multiple
from anesthesia_sim.app.run_series import (
    COMPARTMENT_FRACTION_NAMES,
    COMPARTMENT_STATE_INDEX,
    DrawnWindow,
    RecordedQuantity,
)
from anesthesia_sim.core.concentration import Fraction, MacMultiple, Percent, fraction_from_percent
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
)
from anesthesia_sim.core.governing_equations import (
    TissueGroupEquationSettings,
    UptakeEquationSettings,
)
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
    """Whether the run is going, and why it is not: the three facts a halt is stated from.

    `SimulationController.status()` builds one from the controller's own
    run-state fields and the run-length guard, and builds no compartment
    value for it, so it can be read of a run whose `snapshot()` refuses -
    which is what `RunView.present_halt` needs, since the snapshot's own
    `Fraction`s are among the values a halt can be for (`PL-7DJK`).
    `RunSettings` extends it, and `SimulationSnapshot` extends that, so
    `dashboard_frame.status_word`, `transport` and `notice` take any of the
    three, and a frame that drew reads the three off the snapshot it drew
    from.
    """

    is_running: bool
    """Whether the run is advancing. `False` for a pause and for both halts."""
    supported_limit_reason: str | None
    """Why the run stands at a declared limit of the model's domain, or
    `None` if it does not.

    A non-`None` value means the run stands at the supported run length,
    where the core would refuse the next step - whether it stepped there,
    was forked there, or was reset to a fork there (`PL-5291`). `is_running`
    is `False`, and this is neither a pause nor a failure: nothing was
    miscalculated, no step was rolled back, and every value in the snapshot
    is a completed step's at a simulated time inside the supported span.
    What ended is the claim that a further step would stand for a patient.

    It is separate from `failure_reason` because the interface must not
    present the two alike. Telling a reader the simulator broke, when it
    stopped exactly where `docs/MODEL.md` says it should, misrepresents a
    correct model as a defective one - and the reverse would be worse.
    Both are `None` for a run that is merely paused.
    """
    failure_reason: str | None
    """Why the run stopped abnormally, or `None` if it did not.

    A non-`None` value means a step, a setting or a value the interface
    built raised and the session is halted: `is_running` is `False`, but
    this is not the same state as a user pause, and the interface must not
    present it as one.

    Every other field in the snapshot is nonetheless a completed step's.
    `AgentUptakeSystem.advance()` rolls a failed step back, and elapsed
    time advances only after it returns, so a halted session reports the
    last step that finished — at the simulation time it finished at —
    rather than one abandoned partway through.
    """


@dataclass(frozen=True, slots=True)
class RunSettings(RunStatus):
    """The agent and the four settings in force on the run: what a setting control is written from.

    `SimulationController.settings()` builds one from the agent the run was
    given and the settings its compartments hold - every one a checked type,
    a string the controller holds or the accepted range's two floats - and
    builds no compartment value for
    it, so it can be read of a run whose `snapshot()` refuses, as
    `RunStatus` can. `dashboard_frame.setting_readouts` takes it, which is
    what lets `RunView.present_halt` write every dial from what the run
    holds: a dial dragged into a halt otherwise kept the value before the
    drag printed beside it, since no frame followed to rewrite it
    (`PL-85LJ`). `RunRecord` extends it, and `SimulationSnapshot` extends
    that, so a frame that drew reads the settings off the snapshot it drew
    from.
    """

    agent_id: str
    agent_display_name: str
    max_delivered_concentration_percent: Percent
    agent_mac_percent: Percent
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

    `BreathingCircuit.accepted_fresh_gas_flow_range_l_min`, read off the
    circuit in force: the model's envelope narrowed to the mounted machine's
    declared range. It travels beside the flow for the reason
    `max_delivered_concentration_percent` travels beside the dial: the
    control offering the setting reads its bounds from here, so it offers
    no flow this machine refuses (`PL-7CRY`).
    """
    delivered_concentration_percent: Percent
    alveolar_ventilation_l_min: AlveolarVentilation
    cardiac_output_l_min: CardiacOutput

    @property
    def delivered_partial_pressure_fraction(self) -> Fraction:
        """The delivered fraction of an atmosphere, derived from the percent dialled.

        The snapshot carries the dial as the circuit holds it, the percent it
        was set to, so the dial is drawn from what was dialled rather than
        from a fraction multiplied back (`PL-NJPB`).
        """

        return fraction_from_percent(self.delivered_concentration_percent)


@dataclass(frozen=True, slots=True)
class RunRecord(RunSettings):
    """What the run holds and has been given: its settings, and every change made to them.

    `SimulationController.record()` builds one from no compartment value, as
    `status()` and `settings()` do, so it can be read of any run on every
    render tick. That is what it is for: `SimulationView.render_tick` draws a
    frame whenever a displayed run's record differs from the one its view
    last wrote, so a run that changes without a frame being asked for - one
    that halts on a mark or arrives at the supported run length inside
    `RunView.step_tick` - is redrawn on the next tick, without that path
    having to remember to ask (`PL-X7D5`, `PL-T995`). `SimulationSnapshot`
    extends it, so a frame that drew states the record it drew from.
    """

    control_timeline: tuple[ControlChange, ...]
    """Every setting change this run has seen, oldest first.

    Empty for a run nobody has touched, and cleared with the rest of the
    run by `reset()` and by a change of agent. A setting the core refused
    is absent: it never took effect, so it is not part of the run.
    """

    def run_record(self) -> RunRecord:
        """This record and nothing a subclass adds: what a snapshot states of its run's record.

        Dataclass equality compares like classes only, so a snapshot never
        equals the record it extends. A view stores this to compare against
        `SimulationController.record()` later.
        """

        return RunRecord(**{field.name: getattr(self, field.name) for field in fields(RunRecord)})


@dataclass(frozen=True, slots=True)
class SimulationSnapshot(RunRecord):
    """Read-only simulation data exposed to the user interface.

    A `RunRecord` with everything else the interface draws: the run-state
    fields, the settings and the setting changes come first, inherited, and
    the rest follows.
    Built by keyword in `SimulationController.snapshot()` and nowhere else
    in `src/`, so the field order is nothing a caller relies on.
    """

    elapsed_s: CaseInstant
    began_at_s: CaseInstant
    """The case instant this run itself began at: zero on a trunk, its fork on a branch.

    On the case's own axis like `elapsed_s`, and the value
    `SimulationController.began_at_s` gives. It travels beside the elapsed time
    it bounds because `has_recorded_run` reads the two together: a branch is
    built already standing at its fork, so elapsed time above zero says nothing
    about whether anyone has touched it (`PL-7TBQ`).
    """
    agent_mac_awake: MacAwakeReference
    """The running agent's population MAC-awake, as a fraction of its MAC.

    Travels whole rather than as two loose floats, and beside
    `agent_mac_percent` for the same reason that field gives: the chart's
    reference band is `fraction_of_mac` times that divisor, so pairing one
    agent's MAC-awake with another agent's MAC would draw a correct number
    at the wrong height on a labelled axis.

    The interface reads it, `core/` does not: no governing equation consumes
    MAC-awake, exactly as none consumes `mac_percent`. `docs/MODEL.md`
    § "MAC-awake as a chart reference" states what the band asserts, which
    trace it is read against, and why it is not a time to wake-up.
    """
    circuit_volume_l: float
    # The six compartment values, and they are `agent_id`'s. Flat named
    # floats rather than a mapping keyed by substance, which is what the
    # recorded run became at `PL-W3DD` - and the asymmetry is deliberate
    # rather than unfinished (`PL-TCD1`, decided 2026-09-13).
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
    # vocabularies - the chart named the substance it drew and the numbers
    # beside it did not. That is fixed by saying so: these travel with
    # `agent_id` and `agent_display_name` above, for the same reason
    # `agent_mac_percent` does, and `dashboard_frame.substance_heading`
    # labels the readout row with the substance, placed there by `run_view`,
    # rather than leaving a reader to carry it over from the agent selector.
    #
    # When the model holds N simultaneously present substances - `ROADMAP.md`
    # Phase 1, ahead of planned item 6 - a mapping is the right shape and this
    # block is where it goes.
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

    The opposite kind of thing to `control_timeline`, which `RunRecord`
    carries: the timeline is a record of what was done to the run, and this
    is the set of questions still being asked of it. Nothing here has
    happened yet, and nothing here changes a run.

    It survives what the timeline does not — `reset()` and `set_agent` both
    keep it, for the reason they keep the settings — and a branch opens
    carrying its trunk's copy. `app/bookmarks.py` holds the argument for each,
    and whether a run has *reached* a mark is `PL-CTD7` rather than anything
    this snapshot answers.
    """
    bookmark_halt: BookmarkCrossing | None
    """The marks the run is halted on, or `None` if it is not halted on any.

    Set on the step that crossed them and cleared by the next step the run
    takes, so a reader meets it exactly while the run stands on the crossing.
    `is_running` is `False` alongside it and this is an ordinary pause: Start
    resumes, and the crossing just halted on is not crossed again by doing so
    (`MacTarget.crossed_between`).

    `instant_s` is the completed step's own instant, so it sits on the run's
    `simulation_step_s` grid rather than on the coarser grid a tick boundary
    can reach — which is the whole of what `PL-CTD7` buys, and what
    `docs/MODEL.md` § "Halting on a marked crossing" states.
    """
    bookmark_standings: BookmarkStandings
    """Where each mark in `bookmarks` stands on this run, keyed by the mark.

    The other half of the same question `bookmarks` asks: that field is what
    the learner marked, and this is where the run stands on each of them.
    Five answers rather than two, because "not reached", "not reached yet" and
    "already behind the clock" are different claims and a row that conflates
    them tells a learner to wait for something that cannot arrive —
    `bookmarks.MarkStanding` carries the argument for each, and the reason a
    marked instant and a marked height are answered in different words.
    """

    @property
    def has_recorded_run(self) -> bool:
        """Whether this run holds anything that starting over would destroy.

        True once the run has advanced past its own beginning or has recorded
        a setting change; false for a run that has been built and not yet
        touched, which is the state a fresh session, a fresh branch and
        `reset()` all leave.

        It exists so the interface can tell a destructive act from a harmless
        one. `set_agent` always begins a new run, which is unrecoverable where
        there is a run to lose and is nothing at all where there is not, and a
        confirmation that fires in both cases states something untrue in the
        second and has been answered without reading by the time it matters in
        the first.

        Elapsed time and the timeline are read together because either alone
        misses a case: a run paused at its first sample with the vaporizer
        already turned has a recorded input and no elapsed time, and a run
        advanced with nothing touched has the reverse.

        **Elapsed time counts from `began_at_s`, not from zero** (`PL-7TBQ`).
        A branch's clock is the case's, so it opens at its fork with
        `elapsed_s` already past zero, and read against zero every branch held
        a run to lose from the moment it was made, and again after every reset.
        The comparison is exact at the fork: the branch's clock is its step
        count times its step, and every door to a fork refuses an instant that
        is not a whole number of steps, so the clock stands exactly on it.
        """

        return self.elapsed_s > self.began_at_s or bool(self.control_timeline)


@dataclass(frozen=True, slots=True)
class ResumePoint:
    """Everything a branch needs in order to have opened where it did.

    Seven things that only mean anything together, so they travel together
    rather than as seven attributes a later edit could set one of - the
    argument `RunSegment` already makes about its own two halves. A branch
    rebuilt from six of these and a stale seventh would open at a state its
    settings never produced, or on an accounting period that never happened.

    It is also what `SimulationController.reset()` reads. Reset returns a run
    to its own beginning, and a branch's beginning is the fork rather than the
    case's induction, which the branch does not hold and cannot recover.

    **`fork` and `segment.opening` are two instants, not one** (`PL-B8MK`).
    They coincide for a fork taken at a control event, which is the only fork
    that existed before bookmarks could halt a run: a control event *is* a
    keyframe, so the stretch the branch opened inside begins exactly where the
    branch does. A bookmark's instant has no reason to be a keyframe, and
    recording one there would move the trunk's own later answers - so a
    bookmark fork opens its definition at the keyframe the parent's stretch
    begins at while standing at the fork itself. Both are the case's own
    instants, on the one axis `PL-ZMRT` left; what is no longer true is that
    they are equal.

    Attributes:
        segment: The parent stretch this branch opened inside, carrying both
            the settings in force and the keyframe they start from. That
            keyframe is where the branch's own run definition opens, which is
            at or before the fork.
        fork: The instant the branch was taken at and the canonical state the
            parent held there - the parent's own keyframe for a fork at a
            control event, and one propagation from it for a fork at a
            bookmark. Its instant is where the branch began: where the
            branch's clock and its live system stand, what a reset returns
            to, and where `drawn_window` stops drawing to the left.
        step_count: How many steps the case had completed at the fork, so
            the branch's clock continues the case's rather than restarting.
            `docs/MODEL.md` § "Supported run length" is measured against this.
        simulation_step_s: The step the case has been taken at, or `None` for
            a fork from a run that has not stepped. A branch keeps its
            parent's cadence; `SimulationState` refuses a different one.
        accounting_anchor_l: The agent the *case's* accounting period started
            from, carried rather than re-derived. `AgentUptakeSystem.resume_at`
            says why deriving it is unsafe.
        stepped_from: The instant one step before the fork and the parent's
            canonical state there, or `None` for a fork at the case's opening,
            which no step ends at. With `fork` it is the step the branch opens
            standing on. The branch asks that step which marks it crossed each
            time its standings are read, against the marks as they stand then,
            so a mark added after the fork reads as it would have read had it
            been there before (`PL-1ZQ4`). The parent's state is held here
            because the branch cannot evaluate it: a branch taken at a control
            event opens its definition at the fork, after this instant.
        crossing: What the step ending at the fork crossed, asked of the marks
            as they stood when the fork was taken, or `None` where it crossed
            none or no step ends there. Every door asks it the same way, a
            control event's included (`PL-1ZQ4`, case 3). It is what the
            branch reports having opened on (`SimulationSnapshot.bookmark_halt`),
            and it is here rather than asked again for the reason the other
            members are: `_open_at` is a reset's path as well as a fork's, and
            a reset stands the branch back on the identical record
            (`PL-3K9B`, case G). The standings do not read it; they ask
            `stepped_from` and `fork` again.
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
    """A marked instant a run has passed, and the instant a branch taken there opens at.

    Two numbers that are not in general one, which is why they travel
    together (`PL-W4XQ`). A mark lying inside a step is reached at the step's
    end, so `bookmark.instant_s` is where the learner marked and `fork_s` is
    the step instant a branch stands at: 45.3 and 45.300000000000004 for a
    typed 45.3 s at the 0.1 s step. A reader labelling the offer reads
    `fork_s`, the instant the act will take, and a reader taking it hands back
    `bookmark`, the mark itself, so neither has a float to get wrong.

    Attributes:
        bookmark: The mark, as the run holds it.
        fork_s: Where a branch taken at it opens: the end of the step that
            reaches it, `TimeBookmark.steps_to_reach` steps into the case.
    """

    bookmark: TimeBookmark
    fork_s: CaseInstant


@dataclass(frozen=True, slots=True)
class HereForkPoint:
    """Where a paused run stands, as a place to branch, and whether a mark stopped it there.

    `SimulationController.here_fork_point`'s answer (`PL-Y2SL`). The instant
    is the clock's, and the clock stands on whole steps, so the instant a
    reader is shown and the instant `resumed_here` forks at are one number;
    nothing here is a typed value for a caller to get wrong.

    Attributes:
        fork_s: The instant the run stands at, which is where a branch taken
            here opens.
        stopped_on_mark: Whether the run halted here on a marked crossing,
            `SimulationSnapshot.bookmark_halt`, rather than being paused here,
            so a label can say which.
    """

    fork_s: CaseInstant
    stopped_on_mark: bool


class SimulationController:
    """Own run controls and read-only history for one app session."""

    def __init__(
        self,
        agent_id: str = "sevoflurane",
        circuit_volume_l: float | None = None,
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
        # What this run has done with the marks, as opposed to what is marked.
        # Both are the run's product rather than the learner's question, so
        # both are cleared wherever a new run begins - `_build_state`, which
        # `set_agent` comes back through, and `reset()` - while `_bookmarks`
        # below survives all of it. `_stand_on` is the one exception, and it
        # is not a carry-over: a branch opens *standing on* the crossing it
        # was forked at, which is where it is rather than something an earlier
        # run did.
        self._bookmark_halt: BookmarkCrossing | None = None
        self._reached_instants_s: frozenset[CaseInstant] = frozenset()
        self._reached_crossings: frozenset[tuple[RecordedQuantity, float]] = frozenset()
        # Set here and not in `_build_state`, which is deliberate rather than
        # incidental: `_build_state` is also what `set_agent` comes back
        # through, and a mark is the learner's question rather than the run's
        # product, so it outlives the run the way a setting does. A MAC target
        # is held as a multiple of whichever agent is running, so it means the
        # same thing after the change as before it - which is the comparison a
        # learner changing agent is making.
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

        Called wherever a new run begins. A mark is the learner's question and
        survives; whether a run halted on one is that run's product and does
        not, because a standing carried across a reset would report a crossing
        that the run now on screen never took.

        A branch's reset clears through here and then stands on its fork again
        through `_open_at`, which is the same sequence a fork runs: the
        crossing a branch opens on is where the branch stands rather than what
        an earlier run did, so it comes back with the state it belongs to.
        """

        self._bookmark_halt = None
        self._reached_instants_s = frozenset()
        self._reached_crossings = frozenset()

    def _build_state(
        self,
        agent_id: str,
        circuit_volume_l: float | None,
        fresh_gas_flow_l_min: FreshGasFlow | None,
        delivered_concentration_percent: Percent | None,
        alveolar_ventilation_l_min: AlveolarVentilation | None,
        cardiac_output_l_min: CardiacOutput | None,
    ) -> None:
        """(Re)build dynamic state from scratch for a chosen agent.

        Every argument is an override applied on top of the state
        `AgentUptakeSystem.for_agent()` already built from the data files;
        a `None` leaves that data-file value in place, including the
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
        self._max_delivered_concentration_percent = (
            agent_parameters.max_delivered_concentration_percent
        )
        self._agent_mac_percent = agent_parameters.mac_percent
        self._agent_mac_awake = agent_parameters.mac_awake
        self._state = SimulationState(uptake_system=uptake_system)
        # One substance: the agent this run is of. `set_agent` comes back
        # through here and builds a new history under the new agent's id,
        # so a run's recorded substance is always the one its samples were
        # produced by.
        self._run_definition = RunDefinition(
            uptake_system.equation_settings(),
            uptake_system.state_vector(),
            opened_at_s=CaseInstant(0.0),
        )
        self._note_recorded_settings()
        # A run built here is a trunk, so it opens at the case's own zero.
        # `resumed_at()` is what sets this, and a branch built there opens its
        # definition at the fork instead - on the same axis, which is why
        # nothing here converts between the two.
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
        """The agent this run is of, read from the run's settings and from no compartment.

        The snapshot carries the same id, so this is for a reader that cannot
        have the snapshot: `RunView` puts the agent selector back to the
        running agent on a run whose snapshot refuses (`PL-V2HC`).
        """

        return self._agent_id

    def fail(self, reason: str) -> None:
        """Halt the session because something raised, recording why.

        Distinct from `pause()`, which is a user decision the run resumes
        from. A failure means a step or a setting raised, and while the
        core rolls a failed step back — so the state left behind is the
        last completed step rather than a partial one — resuming is still
        not offered. The run reached a state the model could not step
        from, so a resumed run would fail again on its first tick, and
        offering Start would present that as a working control. Only a
        fresh run clears it, via `reset()` or `set_agent()`.
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

        Two reasons refuse every door. This run is itself a branch, or the
        frame it is drawn in has failed (`record_failed_frame`). Each door
        raises from this same check, so `BranchedCase` offers no fork point
        where it is set, and the offer and the doors cannot disagree. A door
        may still refuse a particular fork for its own reason, which
        `here_fork_point` and the doors' docstrings name.
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

        Read from the run itself and never from a flag alone (`PL-5291`). A
        run stands at the limit when the core would refuse its next step, and
        that is what the state is asked, so the reason here is the one the
        refused step would give, word for word. Three routes put a run there
        - stepping onto the last supported step, a fork taken on it, and a
        branch reset to such a fork - and only the first ever refused a
        step, so a flag set by the refusal alone left the other two reading
        as an ordinary pause: Start offered, no limit notice, and the marks
        panel saying an unreached mark was still ahead of a run that could
        not step.

        A reason `halt_at_supported_limit` recorded outranks the derived one,
        because it was first and because the domain limit it carries may have
        been raised on a path the state cannot be asked about.
        """

        if self._recorded_supported_limit_reason is not None:
            return self._recorded_supported_limit_reason

        return self._reason_the_next_step_would_be_refused()

    def _reason_the_next_step_would_be_refused(self) -> str | None:
        """What `SimulationState.advance` would refuse the next step with, or `None`.

        The core's own guard is asked rather than its rule restated, so the
        controller and the stepper cannot disagree about which count is the
        last supported one - `maximum_step_count` decides that once, on the
        product of count and step (`PL-8H2R`) - and the message is the
        guard's own. A run that has not stepped has no cadence to measure
        the span in, and stands at nothing.
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

        Distinct from `fail()`, which records that something went wrong,
        and from `pause()`, which the run resumes from. Here nothing went
        wrong and there is nothing to resume *to*: the core refused a step
        before taking it, so the run stands on a completed step at a
        simulated time the model is claimed to represent a patient at, and
        the step after it would be refused identically.

        Resuming is therefore not offered, for the reason `fail()` gives -
        a Start that does nothing is a control presenting itself as
        working - and `reset()` or `set_agent()` is the way to a new run.
        What differs is only what the interface says about it, and that
        difference is required rather than cosmetic: see
        `SimulationSnapshot.supported_limit_reason`.

        A run that steps onto the limit never needs this: `advance` halts it
        on the arriving step, and `supported_limit_reason` reads the limit
        from the state (`PL-5291`). What is recorded here is a
        `SimulationDomainLimitError` the interface caught on some other path
        - a setting, through `run_view.halt` - which the state cannot be
        asked about. The first reason is kept, like `fail()`'s, so a later
        raise at the same boundary cannot overwrite the one that explains
        it, and it outranks the derived reason for the same reason.
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

        The bookmarks are preserved with them, and a MAC target is the reason
        that is safe: it is held as a multiple of whichever agent is running,
        so 0.8 ×MAC stays 0.8 ×MAC of the new agent rather than becoming the
        old agent's absolute concentration under a new divisor. Reaching the
        same multiple at a different time is what a learner changing agent is
        there to see, so a target that survived the change is the comparison
        rather than a leftover.

        Mid-run agent switching with residual washout accounting is a
        distinct, harder feature (see ROADMAP.md's anesthesia-machine
        milestone); this always begins a new run rather than attempting it.
        Because it begins a new run it also clears a failed session, the
        same way `reset()` does.

        And because it begins a new run it *destroys* one, irrecoverably:
        the recorded history, the control-input timeline and the simulated
        time the run reached all go, and nothing here or anywhere else keeps
        a copy. Calling this is therefore not something a caller may do on a
        gesture that reads as choosing a view. `docs/MODEL.md`
        § "Agent-change behavior" states what the interface owes a user
        first, and `SimulationSnapshot.has_recorded_run` is what tells it
        whether this call would cost anything.

        **A branch refuses it** (`PL-TFX5`). A branch inherits its parent's
        agent rather than re-choosing it, because changing agent is already an
        explicit new case and a branch that could change it would be a second
        case wearing a comparison's clothes. Without the refusal the
        conversion is silent and total: `_build_state` clears `opened_from`, so
        the run stops being a branch, `reset()` stops returning it to its fork,
        `resumed_at` starts accepting it as a trunk - a branch of a branch by
        the back door - and a `BranchedCase` goes on listing it among branches
        of a case it is no longer part of. Every one of those is a mode change
        with nothing on screen saying so. A learner who wants a different agent
        starts a new case, which is what `PL-R3KB` made that gesture mean.

        Raises:
            SimulationConfigurationError: This run is a branch; or the
                snapshot the settings are carried over from refuses a value
                (`snapshot`), read before the run is paused so that the
                refusal changes nothing (`PL-V2HC`).
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
        """Whether this run is going and why it is not, built from nothing a compartment holds.

        Read where a halt is presented (`RunView.present_halt`), because
        `snapshot()` builds every compartment's fraction and a refusal of one
        of those is among the halts to present: a halt stated from a fresh
        snapshot was not stated at all when the snapshot was what refused
        (`PL-7DJK`). The three fields are the controller's own run state and
        the run-length guard, which reads the step count and the step - both
        checked types the state holds - and builds no `Fraction`.
        """

        return RunStatus(
            is_running=self._is_running,
            supported_limit_reason=self.supported_limit_reason,
            failure_reason=self._failure_reason,
        )

    def settings(self) -> RunSettings:
        """The agent and the four settings in force, built from no compartment value.

        Read where a setting control is written on a run whose `snapshot()`
        refuses (`RunView.present_halt`): the setting a drag applied is what
        the run holds, and the control is written from here rather than left
        on the value before the drag (`PL-85LJ`). The agent, its MAC and its
        vaporizer maximum are the controller's own; the four settings are the
        compartments', each a checked type built when it was set.
        """

        system = self._state.uptake_system
        circuit = system.circuit

        return RunSettings(
            is_running=self._is_running,
            supported_limit_reason=self.supported_limit_reason,
            failure_reason=self._failure_reason,
            agent_id=self._agent_id,
            agent_display_name=self._agent_display_name,
            max_delivered_concentration_percent=self._max_delivered_concentration_percent,
            agent_mac_percent=self._agent_mac_percent,
            fresh_gas_flow_l_min=circuit.fresh_gas_flow_l_min,
            accepted_fresh_gas_flow_range_l_min=circuit.accepted_fresh_gas_flow_range_l_min,
            delivered_concentration_percent=circuit.delivered_concentration_percent,
            alveolar_ventilation_l_min=system.alveoli.alveolar_ventilation_l_min,
            cardiac_output_l_min=system.patient.cardiac_output_l_min,
        )

    def record(self) -> RunRecord:
        """The settings in force and every change made to them, built from no compartment value.

        Read on every render tick of every displayed run: `SimulationView`
        compares it against the record the run's view last wrote and draws a
        frame where the two differ (`PL-X7D5`). So it builds nothing
        `settings()` does not and reads the timeline the controller holds,
        which means it cannot raise for a value a frame would refuse.
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
                quotient is outside 0 to 1. Each is built as a `Fraction`
                here, under the compartment's name
                (`run_series.COMPARTMENT_FRACTION_NAMES`), because the
                compartment holds an amount and the quotient read from it
                carries no proof; the interface halts the run on the refusal
                and states the halt from `record()`, which cannot raise it
                (`PL-7DJK`). No supported setting reaches it
                (`core/concentration.py`).
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
            max_delivered_concentration_percent=self._max_delivered_concentration_percent,
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
    # Four methods and no `marks` setter, so the collections can only be
    # reached through the operations `BookmarkSet` validates. A setter would
    # let a caller hand over a set built anywhere, and the invariant that
    # matters - one instant is marked once, one crossing is marked once -
    # would then be enforced in whichever caller happened to remember it.
    #
    # Each refusal comes out of `app/bookmarks.py` unchanged rather than being
    # re-worded here: the message names the value that failed, and a second
    # sentence wrapped around it would put two accounts of one refusal on
    # screen.

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
        """Unmark the instant `bookmark` stands at.

        Raises:
            SimulationConfigurationError: If no bookmark stands there.
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
        """Unmark the crossing `target` names.

        Raises:
            SimulationConfigurationError: If no target names it.
        """

        self._bookmarks = self._bookmarks.without_mac_target(target)
        self._forget_unmarked()

    def _forget_unmarked(self) -> None:
        """Drop what the run did with marks the learner has since removed.

        An unmarked question has no row to draw a standing beside and no place
        in a halt the interface is reporting, so leaving either behind would
        name a mark that is no longer listed — the stale state
        `.claude/rules/expert-review.md` asks to be designed out rather than
        warned about. A halt that crossed two marks keeps the one still
        marked; a halt left naming nothing is cleared outright, because
        `BookmarkCrossing` refuses to describe a step that crossed nothing.
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

        The run's own record, as against `snapshot().control_timeline`, which
        is the record of what a *reader* is shown: one carries the settings
        the equations were assembled from, the other the acts a user made, in
        the units the interface displays. They agree about when the run
        changed and about nothing else, deliberately.

        Handed out as the frozen segments rather than as the run definition itself, so
        a caller can read the run without being able to advance it: a run definition
        whose reach moved independently of the run would answer for instants
        the run never reached. Save, replay and forking read this;
        `ROADMAP.md` items 9 to 12 are what they are.

        **These instants are the case's**, as is everything else this class
        exposes - `snapshot().elapsed_s`, the control timeline's stamps,
        `drawn_window`'s instants. A branch's definition opens at a keyframe
        of the case rather than at a zero of its own, so a keyframe read here
        needs no conversion to be placed on the case's axis and there is no
        offset for a caller to add. `PL-ZMRT` is where that was decided;
        before it, this was the one reader handing out instants in a second
        frame.

        **The first of these is not in general where the branch began**
        (`PL-B8MK`). A branch taken at a control event opens its definition at
        the fork; one taken at a bookmark opens it at the keyframe before the
        fork, because recording one at the fork would move the trunk's own
        later answers. `began_at_s` is what a reader wanting the run's own
        beginning asks - this tuple answers what the *definition* holds.
        """

        return self._run_definition.segments

    @property
    def opened_from(self) -> ResumePoint | None:
        """Where this run was opened from, or `None` for a trunk.

        A branch's whole provenance in one object, so that what a displayed
        value is a value *of* stays traceable to the run it continues, which
        `CLAUDE.md`'s safety-critical standard asks of any clinically
        meaningful output.
        """

        return self._opened_from

    @property
    def began_at_s(self) -> CaseInstant:
        """The case instant this run itself began at: induction, or its fork.

        Zero on a trunk and the fork instant on a branch, on the case's own
        axis like everything else this class hands out. It is what bounds a
        run to the left - what `drawn_window` clips at, what
        `app/bookmarks.py` reads to call a mark unreachable, and what
        `SimulationSnapshot.has_recorded_run` counts a run's own progress
        from, which is why the snapshot carries it too.

        **It is not `run_segments[0].opening.instant_s`, and inferring it from
        there is the mistake this property exists to remove** (`PL-B8MK`). A
        branch taken at a control event opens its definition at the fork, so
        the two agree; a branch taken at a bookmark opens its definition at
        the keyframe *before* the fork, because recording one at the fork
        would move the trunk's own later answers. A reader taking the first
        segment's opening for the run's beginning would place such a branch
        earlier than it exists and draw it across an interval it never lived.
        """

        return CaseInstant(0.0) if self._opened_from is None else self._opened_from.fork.instant_s

    def resumed_at(self, instant_s: CaseInstant) -> SimulationController:
        """Open a second live run at this run's canonical state at `instant_s`.

        The seam `PL-J2TD` exists for: a branch has to become something a
        learner can *manage* rather than a second curve, and managing it means
        advancing it. What comes back is an ordinary paused
        `SimulationController` that advances by the path every run takes -
        `advance()` is not overridden and no second way to move a run forward
        is introduced - standing at the state this run passed through at
        `instant_s`.

        **It opens at a keyframe, because that is this door's scope**
        (`PL-54V0`). `instant_s` must be an instant this run holds a keyframe
        for, which is its start and every recorded setting change. Anywhere
        else is refused, and not for want of a way to reproduce it: a marked
        instant is branched at through `resumed_at_mark` and the instant a
        paused run stands at through `resumed_here`, and both fork between two
        keyframes and reproduce this run element-wise, by opening the branch's
        definition at the keyframe before the fork (`_open_at`). Any other
        instant is offered by no door, so a learner marks it, or pauses the
        run on it, first. What no door does is *restart* a definition at
        the fork from the canonical state there, which replaces one propagation
        over an interval with two over its halves - a different rounding of the
        same exact solution, measured at up to 5.3e-13 in an accumulator -
        where `PL-Z3W6` requires a branch to reproduce its parent element-wise.

        **The branch's clock continues the case's**, because a branch is one
        patient's case under a second management rather than a second patient.
        Three things follow, and each is a correctness property rather than a
        convenience. The 24 h supported run length is enforced on the step
        count, so a branch that restarted it would be handed a fresh envelope -
        a fork at 23 h could be advanced to 47 h of case time with every guard
        passing, in exactly the regime `core/supported_ranges.py` argues the
        omitted metabolism dominates. The clock, every control-change stamp and
        the chart's axis all read `snapshot().elapsed_s`, which
        `format_elapsed` says they "state one quantity one way", so a branch
        counting from zero would place the patient at the wrong point on the
        uptake curve on all three at once. And elapsed time stays one
        multiplication - `(k + n)` steps times the step - rather than the fork
        instant plus the branch's own, which `docs/MODEL.md` § "Simulated time
        is a count of steps, not a running total" is the rule against.

        **The definition opens at the fork rather than at a zero of its own**,
        so the branch's clock and its definition's instants are one quantity
        and nothing converts between them (`PL-ZMRT`). That is what
        § "The canonical evaluation rule" requires: asked for a case instant,
        the branch forms its interval from the same two floats its parent did,
        where a definition re-based to its own zero would depend on a
        subtraction that does not always round-trip. Opening *at the fork* is
        this door's own property rather than every branch's: `resumed_here`
        and `resumed_at_mark` open at the keyframe before the fork, on the same
        axis and with the same guarantee, which `_open_at` and `docs/MODEL.md`
        § "What this requires of a branch" set out.

        **The settings are replayed from the control timeline, and then
        checked.** A branch is built through the ordinary constructor so that
        the circuit volume is applied before any state is - `set_circuit_volume`
        conserves agent by rewriting the inspired fraction, so a volume set
        afterwards would move the branch off its parent's keyframe silently -
        and the four live controls come from the recorded changes, which hold
        the values the compartments actually took in the units they hold them
        in. The replay is then checked against the segment's own settings
        rather than trusted - which hold those same litres per minute since
        `PL-SM5V`, so the two compare exactly - because a branch assembling a
        system matrix its parent never used would diverge from its first step inside
        the tolerance that holds the two records together. The agent's
        displayed references are checked beside them, and a refusal names each
        value that differs rather than a cause, because the rebuild re-reads
        the data files as well as the timeline (`_disagreements_with`).

        Args:
            instant_s: The case instant to open at, in seconds. Must be one
                this run holds a keyframe for.

        Returns:
            A paused `SimulationController` standing at that state, carrying
            this run's agent, patient and circuit, with an empty control
            timeline of its own and a copy of this run's bookmarks.

        Raises:
            TypeError: `instant_s` is not a `CaseInstant`, so nothing has
                checked it against the supported run length
                (`core/supported_ranges.py`).
            SimulationConfigurationError: `instant_s` is not an instant this
                run holds a keyframe for; this run is itself a branch, since a
                branch of a branch is refused rather than silently flattened
                (`PL-TFX5`); the frame this run is drawn in has failed
                (`fork_refusal`); the fork instant is not a whole number of this
                run's steps; or the rebuilt branch holds an equation setting or
                agent reference this run did not hold at the fork, each named
                with both of its values.
        """

        return self._branch_from(self._resume_point_at(instant_s))

    def resumed_here(self) -> SimulationController:
        """Open a second live run where this paused run stands, stopped on a mark or not.

        The door for the decision point a learner is looking at (`PL-Y2SL`):
        paused to think, they try something else from that instant in one
        act, without marking it first (project owner, 2026-10-12). It is also
        the door for a bookmark halt, which is a pause a mark made, and so
        what `ROADMAP.md`'s v0.5.0 Definition of done asks for when it says "a
        branch taken at any recorded control event **or bookmark**"
        (`PL-B8MK`). Everything a branch is - a paused controller carrying this
        run's agent, patient and circuit, advancing by the path every run
        takes - is what `resumed_at` describes; what differs is only where it
        may be taken.

        **It takes no instant, so there is none for a caller to get wrong.**
        The clock names the fork - the step the run is standing on - and
        supplies nothing else: the state there is `RunDefinition.state_at`'s,
        the canonical path every door forks from, and not the live system's.
        Offering this as a float instead would let a branch be asked for at an
        instant the run has not reached, or at the instant a learner *marked*
        rather than the step instant the run actually stopped on - which are
        not the same number, since a mark lying inside a step halts the run at
        the step's end. It is the one door for a MAC target, which has no
        instant to name.

        **It refuses a run that is going, a failed run, the run's own opening
        and the supported run length**, each for a reason of its own. Where a running run stands
        moves with every step, so an instant read off it is stale before it
        can be taken. A failure is not a pause (`RunStatus.failure_reason`),
        and a branch opening where it stands would resume what `fail` says is
        not resumed. A run standing at its opening has recorded nothing to
        branch from, and `resumed_at` already opens there. And a run at the
        supported run length is stopped rather than paused
        (`RunStatus.supported_limit_reason`): no step is left to take, so a
        branch opened there could never be run, and on a dashboard showing one
        comparison at a time only the trunk's Reset, which discards the case,
        would take it off the chart. The doors that still fork there - a
        keyframe or a mark on the limit - are kept for what `PL-5291` holds of
        such a branch.

        **The trunk is not touched.** No keyframe is recorded where the run
        stands: the branch's run definition opens at the keyframe the
        parent's own stretch opens at, while the branch's clock and its live
        system stand at the fork. See `_open_at`, and `docs/MODEL.md`
        § "What this requires of a branch" for which of that section's two
        conditions this relaxes and why the element-wise guarantee survives
        it. Recording the keyframe instead - the obvious route - leaves the
        branch exact against its parent and displaces that parent's own later
        answers, 48 of 54 elements against the same case built unmarked, so
        pausing or marking a run would change it.

        **The crossing the branch opens standing on is the step's, asked
        again** (`_crossing_of_step`), as `resumed_at_mark` asks it, and not
        read from a halt's record. The record names what was marked when the
        run stopped, so a mark added inside the halting step while the run
        stood on it was missing from it and read as before the branch, where
        the same mark reached through `resumed_at_mark` read as passed
        (`PL-2N43`). Asked of the marks as they stand, both doors give one
        account of one step.

        Returns:
            A paused `SimulationController` standing where this run stands,
            carrying this run's agent, patient and circuit, with an empty
            control timeline of its own and a copy of this run's bookmarks.

        Raises:
            SimulationConfigurationError: this run is going, has failed, or
                stands at its opening or at the supported run length; it is
                itself a branch, since a branch
                of a branch is refused rather than silently flattened; or the
                rebuilt branch holds an equation setting or agent reference
                this run did not hold at the fork, each named with both of its
                values.
        """

        return self._branch_from(self._resume_point_here())

    @property
    def here_fork_point(self) -> HereForkPoint | None:
        """Where `resumed_here` would open a branch, or None where it would refuse.

        Answered from the check the door raises from (`_refusal_here`), so an
        offer drawn from this and the door it is taken through cannot
        disagree about whether there is a place to branch. Answered on a
        branch as on a trunk, and None there, for the reason every door
        refuses a branch; `BranchedCase.here_fork_point` reads the trunk's.
        """

        if self._refusal_here() is not None:
            return None

        return HereForkPoint(self._state.elapsed_s, self._bookmark_halt is not None)

    def resumed_at_mark(self, bookmark: TimeBookmark) -> SimulationController:
        """Open a second live run at the step that reached `bookmark`, stopped there or not.

        The third door (`PL-W4XQ`), and the act a time bookmark was asked for:
        a learner paused at 3 h marks 1 h and goes back to it to try something
        else there. The mark may have been set before the run passed it and
        stopped it, or after the clock was already past it, when no step ever
        crossed it; this door answers both alike, because the state at a
        reached instant is the run's definition evaluated there and not
        something the run had to be standing on to hold.

        **It is the halt fork taken late.** The fork is the end of the step
        that reaches the mark (`TimeBookmark.steps_to_reach`), which is the
        instant a halt stops the run on; the state is `RunDefinition.state_at`
        there; the branch's definition opens at the keyframe at or before it.
        So a mark the run is halted on forks where `resumed_here` forks and
        from the same state, and a mark set behind the clock forks where the
        halt would have, had it been set in time. Nothing is recorded on this
        run, which is what leaves it the case it would have been unmarked
        (`docs/MODEL.md` § "What this requires of a branch").

        **The crossing the branch opens standing on is reconstructed**, since
        a step that halted nothing kept no record of what it crossed
        (`_crossing_of_step`). It is `BookmarkSet.crossings_between` asked
        about that one step, with the marks as they stand now and each
        compartment read canonically at either end, so the rule that halts a
        running case is the rule that names this crossing - and a mark lying
        inside the step, which the branch opens just past, still reads as
        passed rather than as before the branch (`PL-3K9B`, case B).

        **It takes the mark, not an instant**, for the reason
        `resumed_here` takes nothing: a float would let a caller name the
        instant a learner typed, which is not in general the step instant the
        run reached it at. A mark at the case's opening is the one no step
        reaches; the run stands on it from the start, so it forks at the
        opening keyframe with no crossing, as `resumed_at` there would.

        Args:
            bookmark: The mark to branch at, matched on its instant as
                `BookmarkSet.without_time_bookmark` matches, so a caller
                holding it without its label still names it.

        Returns:
            A paused `SimulationController` standing at the step that reached
            the mark, carrying this run's agent, patient and circuit, with an
            empty control timeline of its own and a copy of this run's
            bookmarks.

        Raises:
            SimulationConfigurationError: this run holds no time bookmark at
                that instant; it has not passed the mark, so the case holds no
                state there yet - a mark ahead of the clock stops a running
                case when it is reached, and `resumed_here` is then the
                fork; this run is itself a branch, since a branch of a branch
                is refused rather than silently flattened; or the rebuilt
                branch holds an equation setting or agent reference this run
                did not hold at the fork, each named with both of its values.
        """

        return self._branch_from(self._resume_point_at_mark(bookmark))

    @property
    def mark_fork_points(self) -> tuple[MarkForkPoint, ...]:
        """The time bookmarks this run has passed, each with where a branch taken there opens.

        The marks whose standing is `MarkStanding.PASSED`, read from the
        standings rather than decided again, so this list and the bookmark
        panel's rows cannot disagree about which marks are behind the clock.
        Earliest first, the order `BranchedCase.fork_points_s` keeps.

        Answered on a branch as on a trunk, the way `run_segments` is, and
        refused there by `resumed_at_mark` for the reason every door refuses
        a branch; `BranchedCase.mark_fork_points` reads the trunk's.
        """

        return tuple(
            MarkForkPoint(bookmark, self._instant_after(self._steps_to_reach(bookmark)))
            for bookmark in sorted(
                self._passed_time_bookmarks(), key=lambda bookmark: bookmark.instant_s
            )
        )

    def _branch_from(self, resume_point: ResumePoint) -> SimulationController:
        """Build the branch `resume_point` describes, leaving this run untouched.

        Shared by every door to a fork - `resumed_at`, `resumed_at_mark` and
        `resumed_here` - because where a branch may be taken is the only
        thing that separates them. What a branch *is* is stated once, here.
        """

        fork_at_s = resume_point.fork.instant_s
        circuit = self._state.uptake_system.circuit
        alveoli = self._state.uptake_system.alveoli
        patient = self._state.uptake_system.patient

        branch = SimulationController(
            agent_id=self._agent_id,
            circuit_volume_l=circuit.circuit_volume_l,
            # The timeline's `ControlChange` is typed `float`, so a setting read
            # back from it is built into its checked type here, a value already
            # of the type being re-checked harmlessly; the record holds values
            # the core accepted, so none can be refused.
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

        # The branch inherits the marks and not the timeline, and the two go
        # opposite ways for the same reason. The timeline is this run's record
        # - what was done to *it* - so reproducing it on a branch would claim
        # acts the learner never made on the branch. A mark is a question about
        # what is still to come, and a comparison is two managements answering
        # one question: made the learner re-enter them, a typed 0.85 against a
        # 0.8 would leave two branches nominally compared at one height and
        # actually compared at two, with nothing on screen saying so.
        #
        # A mark lying before the fork comes across with the rest. It is
        # unreachable going forward and is not dropped, because dropping it
        # would make the trunk's list and the branch's disagree about what the
        # case is marked at, which is a worse thing for a comparison to have to
        # explain. Saying so where such a mark is listed is `PL-CTD7`'s, with
        # the rest of the reached / not-reached outcome set.
        branch._bookmarks = self._bookmarks

        branch._open_at(resume_point, branch._state.uptake_system.equation_settings())

        return branch

    def _disagreements_with(
        self, branch: SimulationController, settings_at_fork: UptakeEquationSettings
    ) -> tuple[str, ...]:
        """Each value `branch` was rebuilt with that this run did not hold at the fork.

        A branch is rebuilt rather than copied: its live controls are replayed
        from the recorded timeline, and its agent, patient and circuit are
        re-read from the data files. So this names every value that came out
        different, with both of its values, and no cause: a data file edited
        between the two builds fails the check with the timeline blameless, and
        a message blaming the timeline would send its reader into the one part
        that worked (`PL-NC62`).

        Two groups are compared. The equation settings, every field of them and
        of each tissue group, which is everything their equality compares, so a
        setting added to either class is named here without an edit. And the
        agent's four displayed references, which no equation reads: the MAC is
        the divisor of every MAC multiple on screen, so a branch rebuilt under
        another would show one concentration as two multiples beside its parent.

        Each value is written by its `repr` - for a float the shortest text that
        reads back as the same float, for a string the string in quotes - so two
        values that differ never read alike, a difference in the last bit
        included, which any rounding would print identically on both sides.
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
            (
                "max_delivered_concentration_percent",
                self._max_delivered_concentration_percent,
                branch._max_delivered_concentration_percent,
            ),
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
        """Stand this run at `resume_point`'s state, on its clock and its accounting.

        Split out because `reset()` needs exactly this too: returning a branch
        to its own beginning is returning it to the fork, which the case's
        induction cannot supply because the branch does not hold it.

        It writes state and never settings, which is why `reset()` can use it:
        reset preserves settings by contract, so a branch reset after its
        learner has dialled something new stands at the fork state under the
        new settings - the same thing a reset trunk does with its own initial
        state. `_branch_from` is where the replayed settings are checked
        against the segment, because that check is about the *replay* and
        there is no replay here. The settings in force are handed in rather
        than read here, because reading them is the one thing a reset can be
        refused on, and `reset()` reads them before it clears anything
        (`PL-M4M0`); `_branch_from` reads them off the branch it just built,
        which nothing has written past a setter.

        **The definition always opens at the parent's stretch, under the
        parent's settings** (`PL-B8MK`), and whatever the learner has dialled
        since is recorded as a change at the fork rather than written into the
        opening. That is what keeps the branch propagating from the same
        keyframe its parent propagates from, which is the whole of the
        element-wise guarantee; and `record_change` already drops a call whose
        settings are the ones in force, so the reproducing case - every fork,
        and every reset that changed nothing - records nothing and opens
        exactly as it did before this item.

        **Deciding it from the settings instead makes the answer depend on the
        order of two reversible acts**, which is why it is not done that way.
        Dial, dial back, reset and dial, reset, dial back leave one branch: the
        same settings, the same live state, the same snapshot. Choosing the
        opening at reset time gives the second of them the fork rather than the
        keyframe, so it restarts from two propagations where the parent took
        one and stops reproducing - measured 2026-09-20 at 40 of 45 elements
        differing across five probes, worst 1.21e-15, with nothing on screen
        to say so. Recording the change instead leaves `record_change`'s own
        collapse rule to notice the dial-back: the fork segment lands back on
        the settings the stretch before it already had, so it goes entirely and
        the branch is where it started.
        """

        segment = resume_point.segment
        system = self._state.uptake_system

        # The state comes from the canonical path and never from the seeded
        # system read back: a compartment stores an amount and derives its
        # fraction from its own capacity, so the round trip is not the identity
        # - 11.7% of alveolar fractions over the range a case occupies come
        # back one unit in the last place away - and the element-wise
        # reproduction `ROADMAP.md` item 12 requires would fail on exactly
        # those entries. It is the parent's keyframe for a fork at a control
        # event and one propagation from that keyframe for a fork at a
        # bookmark, which `ResumePoint.fork` holds either way.
        system.resume_at(resume_point.fork.state, initial_agent_l=resume_point.accounting_anchor_l)

        self._state = SimulationState(
            uptake_system=system,
            step_count=resume_point.step_count,
            simulation_step_s=resume_point.simulation_step_s,
        )
        # The definition opens on the parent's own stretch - its keyframe, its
        # settings - at a keyframe's own instant on the case's axis, which is
        # what leaves the clock and the definition's reach one quantity.
        self._run_definition = RunDefinition(
            segment.settings, segment.opening.state, opened_at_s=segment.opening.instant_s
        )
        # The branch has reached the fork: it is standing there. Where the
        # definition opened earlier, the stretch between is the *parent's* and
        # the branch never lived it, so `drawn_window` clips it away - the
        # reach is what the branch may be evaluated to, not what it may be
        # drawn from.
        self._run_definition.advance_to(resume_point.fork.instant_s)
        # And then whatever the learner has dialled since, which is nothing on
        # a fork and may be anything on a reset. Recorded at the fork rather
        # than written into the opening, so the parent's stretch stays the
        # parent's: the keyframe this lays carries `_canonical_state_at(fork)`,
        # which is the identical expression `resume_point.fork.state` came
        # from.
        self._run_definition.record_change(settings)
        self._note_recorded_settings()
        self._opened_from = resume_point
        self._clear_control_timeline()
        self._stand_on(resume_point.crossing)

    def _stand_on(self, crossing: BookmarkCrossing | None) -> None:
        """Record the crossing this run opens standing on as where it stopped.

        A branch forked at a crossing is *standing on* it: that is where the
        branch is rather than something its parent did, and a run that opens
        on a crossing and reports having stopped on nothing describes a
        different run (`PL-3K9B`). So the crossing is the branch's
        `bookmark_halt`, as a halt is a trunk's.

        **What the branch has done with the marks is not seeded from it**
        (`PL-1ZQ4`). The standings ask the step the branch opened on again at
        every read, against the marks as they stand then
        (`_crossings_stood_on`), so a mark added to the branch after it opened
        reads as it would have read had it been there at the fork. Seeding the
        reached sets here as well would be a second, older answer to the same
        question, and the one this replaced: it named only the marks there at
        the fork.

        Called from `_open_at`, which is a reset's path as well as a fork's,
        so a branch reset onto its own fork stands on the same record it
        opened on.

        Args:
            crossing: The marked crossing this run opens standing on, or
                `None` where the step ending at its fork crossed no mark or
                no step ends there.
        """

        self._bookmark_halt = crossing
        # A mark unmarked on this branch before the reset is not put back by
        # it: the crossing is a record of a step, and `_forget_unmarked` is
        # what keeps that record from naming a row the panel no longer draws.
        self._forget_unmarked()

    def _resume_point_at(self, instant_s: CaseInstant) -> ResumePoint:
        """Everything a branch opening at `instant_s` needs, or a refusal saying why.

        Raises:
            TypeError: `instant_s` is not a `CaseInstant`.
            SimulationConfigurationError: this run is a branch or its frame
                has failed (`fork_refusal`); `instant_s` is not one of this
                run's keyframes; or the instant is not a whole
                number of this run's steps.
        """

        self._require_forkable()
        require_case_instant("instant_s", instant_s)

        openings = [segment.opening.instant_s for segment in self._run_definition.segments]

        for segment in self._run_definition.segments:
            if segment.opening.instant_s == instant_s:
                break
        else:
            # The door's scope is the reason, not arithmetic: the two other
            # doors fork between keyframes and reproduce the run exactly
            # (`PL-54V0`), so a message blaming the propagation would teach a
            # constraint the code beside it disproves.
            raise SimulationConfigurationError(
                f"this run holds no keyframe at {instant_s} s, and resumed_at opens at one: the "
                f"run's opening or a recorded setting change, which this run holds at {openings} "
                "s. A marked instant is branched at with resumed_at_mark once the run has passed "
                "it, and the instant a paused run stands at with resumed_here"
            )

        # The fork *is* the stretch's opening here, which is what makes a
        # control event the simple case: one instant doing both jobs. The
        # step ending there is asked what it crossed as every other door asks
        # it. A keyframe is not a mark, but the step that reached it may have
        # crossed one, and a branch opening on no crossing where `resumed_here`
        # opens on the step's would read one instant two ways (`PL-1ZQ4`,
        # case 3).
        return self._resume_point(segment, segment.opening)

    def _resume_point_here(self) -> ResumePoint:
        """Everything a branch opening where this run stands needs, or a refusal saying why.

        The fork is the clock - `SimulationState.elapsed_s`, which stands on
        `_instant_after` of the step count bit for bit - because the clock is
        where the run is. On a halt that is the crossing's own instant too,
        since `BookmarkSet.crossings_between` stamps a crossing with the
        instant its step ended at; taking it from the clock is what makes that
        agreement something this method does not rely on.

        Raises:
            SimulationConfigurationError: `_refusal_here` names a reason; or
                the fork instant is not a whole number of this run's steps,
                which the clock it is read from rules out.
        """

        refusal = self._refusal_here()

        if refusal is not None:
            raise SimulationConfigurationError(refusal)

        fork_s = self._state.elapsed_s
        fork = Keyframe(fork_s, self._run_definition.state_at(fork_s))

        return self._resume_point(self._run_definition.segment_at(fork_s), fork)

    def _refusal_here(self) -> str | None:
        """Why a branch where this run stands is refused, or None where it is not.

        The one check `here_fork_point` and `resumed_here` both read, so the
        offer and the door cannot disagree. `resumed_here` carries the reason
        for each refusal; the messages say what to do instead.
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

        The instant one step earlier and this run's canonical state there, so
        the step is read from `RunDefinition.state_at` at either end, as a
        fork reads it. The case's opening is reached by no step.

        Args:
            step_count: How many steps the case had completed at the step's
                end. It is never fewer than this run opened on, since a
                branch is never asked about a step it did not take.
        """

        if step_count == 0:
            return None

        before_s = self._instant_after(StepCount(step_count - 1))

        return Keyframe(before_s, self._run_definition.state_at(before_s))

    def _crossing_of_step(
        self, stepped_from: Keyframe | None, stepped_to: Keyframe
    ) -> BookmarkCrossing | None:
        """The marks the step from `stepped_from` to `stepped_to` crossed, as the marks stand now.

        Asked again of the rule `advance` halts by, about that one step, with
        each compartment read canonically at either end, rather than read
        from any record: a step that halted nothing kept none, and a halt's
        record names only what was marked when the run stopped, so a mark
        added inside the halting step afterwards would be missing from it
        (`PL-2N43`). Every door asks the step ending at its fork through
        here, and so do the standings, of the step a run opened on or stands
        on (`PL-1ZQ4`). The end reading is the state a branch opens from, so
        its first step begins where this one ends and a height arrived at here
        is not crossed again by it.

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
        """Everything a branch opening at the step that reached `bookmark` needs, or a refusal.

        Raises:
            SimulationConfigurationError: this run is a branch or its frame
                has failed (`fork_refusal`); it holds no time bookmark at that
                instant; it has not passed the mark; or
                the fork instant is not a whole number of this run's steps,
                which the step count it is built from rules out.
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
        """How many of this run's steps reach `passed`, a mark the run is at or past.

        A run that has not stepped stands at its opening, so the one mark it
        can have passed is one standing there, which no step reaches.
        """

        simulation_step_s = self._state.simulation_step_s

        if simulation_step_s is None:
            return StepCount(0)

        return passed.steps_to_reach(simulation_step_s)

    def _instant_after(self, step_count: StepCount) -> CaseInstant:
        """The case instant this run stands at once `step_count` steps are complete.

        `SimulationState.elapsed_s`'s own product, formed the same way, so an
        instant derived here is the one the clock reads after that many steps,
        bit for bit, and `_resume_point`'s whole-step check holds of it.
        """

        simulation_step_s = self._state.simulation_step_s

        if simulation_step_s is None:
            return CaseInstant(0.0)

        return CaseInstant(step_count * simulation_step_s)

    def _require_forkable(self) -> None:
        """Refuse a fork from a run that is a branch, or whose frame has failed.

        Raises:
            SimulationConfigurationError: this run is a branch, or the frame
                it is drawn in has failed (`fork_refusal`). A branch of a
                branch is excluded rather than unimplemented (`PL-TFX5`), and
                refusing it here covers the caller holding a branch directly,
                which `BranchedCase` cannot reach.
        """

        refusal = self.fork_refusal

        if refusal is not None:
            raise SimulationConfigurationError(refusal)

    def _refusal_as_a_branch(self) -> str | None:
        """Why a fork from this run is refused for its being a branch, or None for a trunk.

        The first of `fork_refusal`'s two reasons, kept apart because the
        message is about the run's place in the case rather than its frame.
        """

        if self._opened_from is None:
            return None

        return (
            f"this run is itself a branch opened at {self._opened_from.fork.instant_s} s, "
            "and a branch of a branch is refused rather than silently flattened; branch "
            "from the trunk instead"
        )

    def _resume_point(self, segment: RunSegment, fork: Keyframe) -> ResumePoint:
        """A branch's whole provenance: the stretch it opens inside and where it stands.

        **The crossing is asked here, once, for every door** (`PL-1ZQ4`). The
        step ending at the fork is asked what it crossed whichever door named
        the fork, so a branch taken at a control event, at a mark and where
        the run stands opens on one account of one step. While each door
        passed its own answer in, `resumed_at` passed none, and a keyframe
        the trunk was halted on opened a branch reading the halt's marks as
        before it.

        Args:
            segment: The stretch of this run holding `fork`, whose opening is
                the keyframe the branch's own definition opens at.
            fork: The instant the branch is taken at and this run's canonical
                state there.

        Raises:
            SimulationConfigurationError: the fork instant is not a whole
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

        In the units the compartments hold and the timeline records, which is
        what makes the replay exact - `ControlChange` stores the value the core
        accepted rather than the one a caller asked for.

        Three cases, and the second is the one a reader would miss: a control
        changed only *after* the instant asked for was, until then, at the
        value that change displaced, so the first such entry's
        `previous_value` is the answer. A control never changed at all has
        stood at its current value for the whole run.
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

        The chart's own read, and what the recorded-window read was before the run
        stopped keeping samples of itself (`PL-2FM6`).

        **The axis is a viewport, and the run is what fills it.** Both bounds
        are the axis the caller has just set, which legitimately reaches past
        the run: `chart_time_base.following_window` keeps
        `live_headroom_s` of empty axis to the right of the newest instant, and
        `fitted_window` returns the chosen rung's full width however short the
        run is - both deliberately, so the width a trace is drawn at is fixed
        and its slope means the same thing at every moment of every run. So
        the drawn range is clipped to the part of the axis the run covers.
        That is not the coercion `CLAUDE.md` forbids: nothing is substituted
        or defaulted, and `DrawnWindow.times_s` says exactly which instants
        came back, so a caller can see where the run ends rather than being
        told a value for an instant it never reached. Asking the run definition itself
        for those instants is refused, and rightly - see `evaluate_anchored`.

        **The column spacing comes from the axis, not from the clipped
        range**, which is what keeps the grid anchored: the span is a property
        of the selected time base and so is constant, so the evaluated
        instants stay put as the window follows the run and only the newest
        column is new. Deriving the spacing from the clipped range instead
        would move every column on every frame early in a run, which is the
        defect `RunDefinition.evaluate_anchored` exists to avoid.

        Args:
            start_s: Left edge of the axis, in simulated seconds.
            stop_s: Right edge of the axis, in simulated seconds. Not before
                `start_s`.
            columns: Grid columns the axis is divided into, at least two.
                The points actually drawn are these plus the control events
                inside the window and the two ends of the drawn range, so
                this bounds the grid rather than the point count.

        Returns:
            The states at the drawn instants, bound to the agent this run is
            of.

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
        # The axis and the definition are on one clock, so nothing is
        # converted here - only clipped to the span the run actually holds. The
        # lower clip is where this run *began* rather than zero: a branch
        # begins at its fork, the axis legitimately reaches to the left of
        # that, and `RunDefinition` refuses an instant before a run existed
        # rather than answering from the nearest keyframe it has.
        first_s = max(start_s, self.began_at_s)
        last_s = min(stop_s, self._run_definition.reached_s)

        if last_s < first_s:
            # The axis and the run do not overlap. Two ordinary states rather
            # than errors: an axis entirely ahead of a run at the very start of
            # one, and an axis entirely to the left of a branch's fork, which
            # is what a learner sees before the branch point scrolls into view.
            # An empty window draws nothing, which is not the same as drawing a
            # zero.
            return DrawnWindow(substance_id=self._agent_id, times_s=(), states=())

        # An axis of no width is one instant, and it is still drawn: both
        # bounds coincide, so no grid column can fall strictly between them
        # and the spacing substituted here cannot place one.
        window = self._run_definition.evaluate_anchored(
            first_s, last_s, spacing_s if spacing_s > 0.0 else 1.0
        )

        return DrawnWindow(
            substance_id=self._agent_id, times_s=window.times_s, states=window.states
        )

    def start(self) -> None:
        """Start or resume the run, refusing a session that cannot continue.

        Raising rather than quietly declining is deliberate: silently
        ignoring a start would leave the interface showing a stopped run
        with no indication that starting it did nothing, which is the
        hidden mode `CLAUDE.md` forbids.

        Two states refuse, for the same reason and with different meanings.
        A failed session would raise again on its first tick; a session
        standing at the supported run length would have its first step
        refused by the core. Neither can be resumed, and each says which it
        is, so a caller reporting the refusal does not have to guess.
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

        Settings are preserved, and so are the bookmarks, which are the
        learner's questions rather than the run's product: a reset is for
        taking the same case again, and it is the same case they were asking
        about. This and `set_agent` are the ways out of a failed
        session, and of one standing at the supported run length: every
        compartment goes back to its initial state and the step count goes
        back to zero, so nothing carries over from the run that could not
        continue.

        **A branch goes back to its fork rather than to zero**, because that
        is where a branch began. The case's induction is not a state a branch
        holds, so clearing to an empty system would stand the patient at no
        agent at a case time the model says they are loaded - a plausible
        state that never happened, which is the outcome `CLAUDE.md`'s
        safety-critical standard puts an obvious failure ahead of. Its clock
        goes back to the fork instant with it, so the case's supported run
        length is spent from where the branch actually starts - and a branch
        forked on the limit itself has none left to spend, so a reset leaves
        it standing there, stopped, rather than offering a Start the core
        would refuse (`PL-5291`).

        Raises:
            SimulationConfigurationError: If the settings record the run's
                definition opens on cannot be built from what the
                compartments hold. That happens when the tissue flows no
                longer sum to the cardiac output. Since `PL-HQF5` and
                `PL-Z0HN`, only a perfusion fraction written past its guard
                can make them disagree. Raised before anything is
                cleared, so the run is exactly as it was: still running if it
                was, its state, definition, timeline and any recorded failure
                untouched. The interface halts the run on it
                (`RunView._handle_reset`), since the record refused here is
                the one the next step would be refused on (`PL-M4M0`).
        """

        # Read before anything is cleared, because building this record is
        # the one thing here the core can refuse (above), and it holds no
        # dynamic value, so the one read here is the one the cleared system
        # would give after (`PL-M4M0`).
        settings = self._state.uptake_system.equation_settings()

        self.pause()
        self._failure_reason = None
        self._failed_frame_reason = None
        self._recorded_supported_limit_reason = None
        self._forget_reached_marks()
        self._state.reset()
        uptake_system = self._state.uptake_system

        if self._opened_from is not None:
            # A branch's beginning is the fork. The case's induction is not
            # available to return to - the branch never held it - so resetting
            # to a cleared system would put the patient at zero agent at a case
            # time the model says they are loaded, which is a plausible state
            # that never happened rather than the start of anything.
            self._open_at(self._opened_from, settings)
            return

        self._run_definition = RunDefinition(
            settings, uptake_system.state_vector(), opened_at_s=CaseInstant(0.0)
        )
        self._note_recorded_settings()
        self._clear_control_timeline()

    # No `set_circuit_volume` here, deliberately (`PL-GYH2`). The circuit
    # volume is a fixed model parameter rather than a control: it is set
    # once, when this controller builds the system, and no interface control
    # reaches it thereafter. The setter that used to sit here was public and
    # unbounded, so it offered every caller of the app layer a route to a
    # circuit volume outside anything `docs/MODEL.md` verifies, for a knob no
    # teaching case has asked for. `BreathingCircuit.set_circuit_volume`
    # stays, because `_build_state()` is how the parameter reaches the circuit at
    # all; what is removed is the app-level passthrough, not the core
    # primitive. `docs/MODEL.md` § "What is not bounded this way" carries the
    # argument.

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

        The interface calls this when a drag begins. Without it a slider
        dragged twice would be indistinguishable from one dragged once:
        both arrive as a run of changes to the same control, and only the
        input device knows where one act ended and the next began. Guessing
        it back from the timing of the entries would need a threshold, and
        no threshold survives the playback multiplier v0.4.0 adds - the same
        drag spans more simulated time the faster the run is played.

        It records nothing on its own and changes no simulation state: it
        only closes whichever adjustment is open, so the next change starts
        a new one. A change that arrives with no adjustment open - a
        keyboard press on a slider, a programmatic call, a test - therefore
        becomes an adjustment of its own, which is the honest reading of a
        single discrete input and the reason the grouping degrades safely
        rather than wrongly when this is never called.
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
        settings this controller recorded. So a setting written onto the core
        past this controller, such as `AgentUptakeSystem.set_cardiac_output`
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
        written past its guard before `_record_control_change` could write the
        setting back, which `PL-VCP4`'s tests hold.

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

        Called *after* the forwarding setter returns, which is what makes a
        refused setting record nothing: the core raises before this line is
        reached, the exception reaches the interface, and the run - which
        the core left untouched - keeps a timeline that says so.

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
        write-back stays, because a fraction written past its guard still
        leads to a refusal, and the tests reach it that way.

        Both values are read off the compartment that holds them rather
        than taken from the caller's argument. The core rejects an
        out-of-range setting rather than clamping it, so the two are equal
        today - but a record of what was *asked for* would silently become
        a record of something the run never used the day that stopped being
        true, and this timeline's whole claim is that re-applying it
        reproduces the run.

        Two changes are deliberately not recorded, and both are cases where
        the model saw nothing:

        - a value equal to the one already in place, which a slider emits
          freely as a drag re-enters a position; and
        - a change superseded within the same simulation step. Only the
          value standing when `advance()` runs is integrated, so a dial
          moved from 2% to 3% to 4% between two steps is one change from 2%
          to 4% as far as the run is concerned. Collapsing them is what
          makes the timeline a record of the run rather than of the mouse -
          and if the collapse lands back on the value the step began with,
          the entry goes entirely, because nothing about the run differs.
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

        # The definition first, because it is the run: the timeline below records
        # the acts a reader sees, and every branch under it is about how those
        # acts are grouped and displayed. Both are fed from here rather than
        # from the four setters, because this is the one place that means "the
        # core accepted a setting change".
        self._run_definition.record_change(settings)
        self._note_recorded_settings()

        if control is not self._open_adjustment_control:
            self._adjustment_count += 1
            self._open_adjustment_control = control
            self._open_adjustment = self._adjustment_count

        # Two changes to one control inside a single step are one act: the
        # model integrated only the last value, so recording both would
        # describe a run of settings it was never computed under. Compared on
        # the instant, which is what a step *is* now that there is no sample
        # index to stand in for one (`PL-2FM6`).
        #
        # **Searched back across this instant rather than read off the newest
        # entry** (`PL-TFX5`). Looking only at `[-1]` collapses a control moved
        # twice in a row and misses the same control moved twice with another
        # control's move between them - so two dials nudged and both put back,
        # interleaved, left four entries standing at an instant the run did not
        # change at, while `RunDefinition.record_change` - which compares whole
        # settings against the previous stretch and is therefore
        # order-independent - correctly recorded nothing. The two records then
        # disagreed about when the run changed, which is the one thing they are
        # supposed to agree about, and a recorded control event with no keyframe
        # behind it is one `resumed_at` refuses to fork at. Reachable while
        # paused, where `advance()` is a no-op and every control a learner
        # touches carries one instant.
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
        """Every compartment a target could name, read off `state`, in the unit a target is held in.

        One conversion per compartment, through `formatting.mac_multiple` and
        this run's own `agent_mac_percent` — the same divisor the readout for
        that compartment is drawn through, so a target and the number the
        learner is looking at cannot come to mean different things.

        `COMPARTMENT_STATE_INDEX` is what pairs each quantity with its
        position, rather than a second list written here: it is already the
        one place a trace could come to carry another compartment's values,
        and a crossing tested against the wrong compartment is the same defect
        as a trace drawn from one. Each entry is built as a `Fraction` under
        the compartment's name, since the vector reads back the quotients the
        compartments derive from the amounts they hold (`PL-7DJK`).

        Args:
            state: A state vector in `governing_equations`' order: the live
                system's, for a step `advance` is taking, or
                `RunDefinition.state_at`'s, for one `_crossing_of_step`
                asks about after the fact, for a fork or for the standings.

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

        **Both of `start`'s refusals are passed, because both end the run's
        reach** (`PL-N3N5`). A standing says whether a mark can still be
        reached, and this method is the only thing that knows: the two
        reasons live here, `supported_limit_reason` and `_failure_reason`,
        and `start` reads exactly these two to decide that the run cannot be
        resumed at all. Passing the cap and withholding the failure left
        every mark on a failed run reading as one the run had not reached
        *yet*, on a run whose next step would raise as its last one did.

        **What the run did is joined by the steps it opened on and stands on,
        asked now** (`PL-1ZQ4`, project owner 2026-10-17, ratified). A mark
        lying inside the step a branch opened on, or the step a stopped run
        stands on, reads as crossed by that step, against the marks as they
        stand at this read and not as they stood when the step was taken. So
        a mark added after the step reads alike on the trunk and on every
        branch, whichever order the mark and the branch came in.
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
        """What the step this run opened on and the step it stands on crossed, asked now.

        Two steps, and the second only while the run is stopped:

        - **The step a branch opened on**, at every read, however far the
          branch has run since. The branch opens standing on it
          (`ResumePoint.stepped_from`), as a fork at a halt always has.
        - **The step a stopped run's clock ends**, paused or halted, at its
          cap or not, on a trunk or a branch. A run that is going stands on
          no step, since where it stands moves with every step. A failed run
          is left out too, because a failure is not a pause
          (`RunStatus.failure_reason`) and `resumed_here` refuses to branch
          there. `start` keeps what this step crossed when the run leaves it
          (`_keep_crossings_stood_on`), so a mark read as reached while the
          run stood on its step still reads reached once the run moves on.

        A trunk reads a mark the way a branch opened on the same step reads
        it, because both ask the same step through `_crossing_of_step`, from
        the same canonical states at either end.
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

        Called by `start`. While the run is stopped, `_crossings_stood_on`
        answers for the step it stands on. Once it is going that step is
        behind it, so what the step crossed joins what the run has done, as
        a halt's crossing does in `_halt_on`. Without this, a target added
        while the run stood on its step would read reached until Start and
        not reached after it, though nothing about the target or the step
        had changed.
        """

        for crossing in self._crossings_stood_on():
            self._reached_instants_s |= _reached_instants(crossing)
            self._reached_crossings |= _reached_heights(crossing)

    def advance(self, simulation_step_s: SimulationStep) -> None:
        """No-op while paused; otherwise advance state, record history, and halt on a crossing.

        The run definition's reach is moved after the step rather than before it, so a
        step the core refuses - a domain limit, a numerical failure - leaves
        the run definition describing a run that stopped where the state did. Its
        `advance_to` records no state: the states are already implied by the
        settings, and are recovered from them on demand.

        **The crossing test is here because here is one step** (`PL-CTD7`).
        The interface advances a whole tick's worth of steps between frames -
        `multiplier x tick_interval_s / simulation_step_s` of them, 300 at
        300x - so a test applied once per frame would place the halt up to
        `multiplier x simulation_step_s` past the value the learner marked:
        30 simulated seconds at 300x, and 0.1 s at 1x, against a `docs/MODEL.md`
        tolerance stated in hundredths of a percentage point. The same
        bookmark would then stop the run at a different concentration
        depending on how fast it was being played, silently, which is the
        presentation-correctness failure `CLAUDE.md` treats as safety-critical
        - and it would put two branches nominally taken "at 0.8 xMAC" at two
        different states. Called per step, the halt lands on the crossing step
        itself, which is finer than any instant a live control change can
        reach (`app/playback.py`, `PL-NBWP`).

        **A crossing pauses the run**, and that is what makes the halt worth
        having rather than a courtesy. No step is taken while paused and the
        setters apply unconditionally, so "halt at 0.8 xMAC, then turn the
        vaporizer off" acts at the instant the learner was looking at instead
        of at the next tick boundary up to 30 simulated seconds later. The
        pause is an ordinary one: `start()` resumes, and the crossing just
        halted on is not crossed again by resuming, because the next step's
        `before` reading is the halting step's own
        (`MacTarget.crossed_between`). Nothing is armed and nothing is
        disarmed; there is no per-target state for a learner to get wrong.

        The remaining steps of the tick that halted are no-ops, through the
        guard at the top of this method, so the burst stops on the crossing
        step rather than running on to the frame boundary.

        The readings are taken only where something is marked, so an unmarked
        run pays nothing: a marked one pays two `state_vector()` reads and six
        divisions per step.

        **The run halts on the step that lands it on the supported run
        length, not on the one refused after it** (`PL-5291`). The core
        refuses the step *from* the last supported count, so a run stopped
        only by that refusal stands on that count between the arriving step
        and the refused one reading as running - or, where Pause lands
        there, as paused with Start offered - though no step is left to
        take. Halting on arrival, as `_halt_on` does on a crossing, keeps
        `is_running` false wherever `supported_limit_reason` is set, which is
        the contract `SimulationSnapshot.supported_limit_reason` states. The
        values the run stops on are the same completed step's either way;
        what moves is when the stop is said.
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
            # The clock and the definition's reach are one quantity on one
            # axis, on a branch as much as on a trunk, so the reach is the
            # clock and no offset is named here or anywhere. That is what
            # `docs/MODEL.md` § "The canonical evaluation rule" now requires:
            # a branch asked for an instant of the case computes its interval
            # from the same two floats its parent did, rather than from a
            # difference that may not round-trip.
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

        Nothing is recorded: `supported_limit_reason` reads the limit from the
        state, and the run stands at it from this step on. Only `_is_running`
        changes, because that is the one fact the state does not carry and
        the snapshot's contract needs - a limit reason beside a live Pause
        would be a stopped run presenting itself as running.
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
    """The marked instants `crossing` reached, as the standings match them."""

    return frozenset(bookmark.instant_s for bookmark in crossing.time_bookmarks)


def _reached_heights(crossing: BookmarkCrossing) -> frozenset[tuple[RecordedQuantity, float]]:
    """The marked heights `crossing` reached, by `MacTarget.crossing_key`."""

    return frozenset(target.crossing_key for target in crossing.mac_targets)


class BranchedCase:
    """One case, held as the run that happened and the branches taken from it.

    `SimulationController.resumed_at` makes a branch; this makes a *case* of
    the runs that result, which is the relationship v0.5.0 exists to assert -
    that two curves on one axis are one patient under two managements rather
    than two patients. Without something holding it, the controllers two
    `resumed_at` calls return are indistinguishable from two unrelated
    sessions: each knows the instant it opened at (`opened_from`), and none of
    them knows that the others opened from the same run.

    **Flat by construction rather than by refusal** (`PL-TFX5`, project owner,
    2026-08-25): one trunk with N branches, and sub-forks of forks deliberately
    out, because they multiply without bound and buy little over re-branching
    from the trunk. Every fork here is taken from the trunk, so a branch of a
    branch is not an operation this class can express rather than one it
    declines. `resumed_at` still refuses one, because a caller holding a branch
    can reach it directly, and the two guards answer different questions: that
    one says *this run* cannot be forked, this one says there is no second
    generation to fork from. An interface in which the error cannot be stated
    is the stronger of the two, which is why the weaker one is kept as well -
    it is what covers the route around this class.

    **Two branches may be taken at the same instant, deliberately.** That is
    the comparison the milestone is named for - one decision point, two
    managements - so nothing here makes a fork point unique.

    **It computes nothing and advances nothing.** Running, pausing, settings
    and stepping stay on the controllers, one per run; this holds which runs
    there are and how they are related, so a view can loop over them and a
    reader can attribute a curve to one. It is Flet-independent for the reason
    the rest of `app/` outside the view is.
    """

    def __init__(self, trunk: SimulationController) -> None:
        """Hold `trunk` as the run every branch of this case is taken from.

        Raises:
            SimulationConfigurationError: `trunk` is itself a branch. A case
                built on one would be a second generation wearing a trunk's
                clothes: its forks would be sub-forks, which this project
                excluded rather than left unimplemented. The refusal rests on
                that alone. It once also rested on such a case offering
                instants measured from another case's fork, which `PL-ZMRT`
                retired - every run's instants are the case's now - and a
                guard defended by an argument that has stopped being true is
                one a later reader removes.
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

        Oldest first, which is the order of the acts rather than of the fork
        instants: a learner may fork late, then go back and fork early, and a
        list re-sorted by instant would renumber the branch they were looking
        at. Two branches taken at one instant keep the order they were made in.
        """

        return self._branches

    @property
    def runs(self) -> tuple[SimulationController, ...]:
        """Every run of this case: the trunk first, then `branches`.

        What a view loops over. The trunk leads because it is the run that
        happened and every branch is a departure from it, so a reader meeting
        the list in order meets the case before the alternatives to it.
        """

        return (self._trunk, *self._branches)

    @property
    def fork_points_s(self) -> tuple[CaseInstant, ...]:
        """The case instants a fork may be taken at, earliest first.

        The trunk's keyframes: its opening at induction, and every setting
        change the model was actually stepped under. That is what `PL-TFX5`
        means by "any recorded control-input-timeline event", and it is
        `fork_at`'s scope: an instant that is neither is refused there, not
        because a branch could not reproduce the trunk at it but because it is
        another door's - a marked instant through `fork_at_mark`, from
        `mark_fork_points`, and where the paused trunk stands through
        `fork_here`, from `here_fork_point` (`PL-54V0`).

        Induction is included rather than filtered out. A fork at zero is a
        second management of the whole case, which is a comparison a learner
        may legitimately want; it is a strange one to offer under a control
        labelled "branch here", but that is the interface's judgment to make
        and not this list's to pre-empt.

        A **bookmark** is not one of these and does not become one
        (`PL-B8MK`). Making it one would mean recording a keyframe where the
        run halted, which leaves the branch exact against its parent and
        displaces that parent's own later answers - marking a run would change
        it. A fork at a mark is taken through `fork_here` or `fork_at_mark`
        instead, neither of which needs a keyframe, so neither adds an instant
        to this list.

        **Empty while the trunk refuses every fork** (`PL-T2Q2`), which on a
        trunk means its frame has failed (`SimulationController.fork_refusal`).
        A trunk that failed on its own step keeps its keyframes here, because
        each is a state the run computed before the failure and a branch from
        one is drawn normally.
        """

        if self._trunk.fork_refusal is not None:
            return ()

        return tuple(segment.opening.instant_s for segment in self._trunk.run_segments)

    @property
    def mark_fork_points(self) -> tuple[MarkForkPoint, ...]:
        """The marked instants a fork may be taken at: every time bookmark the trunk has passed.

        `fork_at_mark`'s list, as `fork_points_s` is `fork_at`'s, earliest
        first and each with the instant a branch taken there opens at
        (`PL-W4XQ`). It changes as the case does - a mark joins it when the
        trunk's clock reaches it or when one is set behind the clock, and
        leaves only when the learner unmarks it or the trunk starts over - which
        is the lifetime of the keyframes beside it, and not `here_fork_point`'s,
        which ends when the trunk starts again.

        Empty while the trunk refuses every fork, as `fork_points_s` is.
        """

        if self._trunk.fork_refusal is not None:
            return ()

        return self._trunk.mark_fork_points

    @property
    def here_fork_point(self) -> HereForkPoint | None:
        """Where the paused trunk stands, as `fork_here`'s place to branch, or None.

        The trunk's `SimulationController.here_fork_point`: None while it is
        going, has failed, or stands at its opening or at the supported run
        length (`PL-Y2SL`). It ends when
        the trunk starts again, where the entries in `fork_points_s` and
        `mark_fork_points` stay until the case changes.
        """

        return self._trunk.here_fork_point

    def fork_at(self, instant_s: CaseInstant) -> SimulationController:
        """Take a branch from the trunk at `instant_s`, and keep it.

        The trunk is left exactly as it was - `resumed_at` reads it and writes
        nothing - so the case gains a run rather than trading one for another,
        which is what makes this a comparison instead of an undo.

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
                failed, or is not a whole number of the trunk's steps;
                or the branch rebuilt there would not hold what the trunk held.
                `resumed_at` raises these and names which.
        """

        return self._kept(self._trunk.resumed_at(instant_s))

    def fork_here(self) -> SimulationController:
        """Take a branch from the trunk where it is paused, stopped on a mark or not, and keep it.

        The decision point a learner paused at, in one act (`PL-Y2SL`), and,
        on a bookmark halt, the other half of `ROADMAP.md`'s v0.5.0 Definition
        of done - "a branch taken at any recorded control event **or
        bookmark**" - where `fork_at` is the first half. It takes no instant,
        because the fork is the one the trunk is standing on;
        `SimulationController.resumed_here` says why that is the interface
        rather than a widened `fork_at`.

        Returns:
            The new branch, paused at the trunk's state where the trunk
            stands, carrying the trunk's agent and patient. It is also
            appended to `branches`, so a caller that discards the return value
            has not lost it. The trunk is left standing where it was.

        Raises:
            SimulationConfigurationError: the trunk is going, has failed, or
                stands at its opening or at the supported run length; or the
                branch rebuilt there would not hold what the trunk held.
                `resumed_here` raises these and names which.
        """

        return self._kept(self._trunk.resumed_here())

    def fork_at_mark(self, bookmark: TimeBookmark) -> SimulationController:
        """Take a branch from the trunk at a time bookmark it has passed, and keep it.

        The return the owner described a mark for (`PL-W4XQ`): paused at 3 h,
        a learner marks 1 h and goes back to try something else there. It
        takes the mark rather than an instant, from `mark_fork_points`;
        `SimulationController.resumed_at_mark` says why, and why the branch is
        the one the halt would have given.

        Args:
            bookmark: The mark to branch at, from `mark_fork_points`.

        Returns:
            The new branch, paused at the step that reached the mark, carrying
            the trunk's agent and patient. It is also appended to `branches`,
            so a caller that discards the return value has not lost it. The
            trunk is left exactly as it was.

        Raises:
            SimulationConfigurationError: the trunk's frame has failed; the
                trunk holds no time bookmark at that instant or has not passed
                it; or the branch rebuilt there
                would not hold what the trunk held. `resumed_at_mark` raises
                these and names which.
        """

        return self._kept(self._trunk.resumed_at_mark(bookmark))

    def _kept(self, branch: SimulationController) -> SimulationController:
        """Add `branch` to this case and hand it back."""

        self._branches = (*self._branches, branch)

        return branch
