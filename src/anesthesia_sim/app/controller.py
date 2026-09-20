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

from collections.abc import Mapping
from dataclasses import dataclass, replace
from math import isfinite

from anesthesia_sim.app.bookmarks import (
    BookmarkCrossing,
    BookmarkSet,
    BookmarkStandings,
    MacTarget,
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
from anesthesia_sim.app.run_series import COMPARTMENT_STATE_INDEX, DrawnWindow, RecordedQuantity
from anesthesia_sim.core.concentration import Fraction, MacMultiple, Percent
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
)
from anesthesia_sim.core.parameters import MacAwakeReference, load_agent_parameters
from anesthesia_sim.core.run_definition import Keyframe, RunDefinition, RunSegment
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.supported_ranges import MAXIMUM_ELAPSED_SIMULATION_TIME_S
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


@dataclass(frozen=True, slots=True)
class SimulationSnapshot:
    """Read-only simulation data exposed to the user interface."""

    is_running: bool
    elapsed_s: float
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
    fresh_gas_flow_l_min: float
    delivered_partial_pressure_fraction: Fraction
    alveolar_ventilation_l_min: float
    cardiac_output_l_min: float
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
    control_timeline: tuple[ControlChange, ...]
    """Every setting change this run has seen, oldest first.

    Empty for a run nobody has touched, and cleared with the rest of the
    run by `reset()` and by a change of agent. A setting the core refused
    is absent: it never took effect, so it is not part of the run.
    """
    bookmarks: BookmarkSet
    """The instants and the heights this run is marked at, in two collections.

    The opposite kind of thing to `control_timeline` above, and travelling
    beside it so the difference is visible: the timeline is a record of what
    was done to the run, and this is the set of questions still being asked of
    it. Nothing here has happened yet, and nothing here changes a run.

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
    the learner marked, and this is how far the run has got with each of them.
    Four answers rather than two, because "not reached" and "not reached yet"
    are different claims and a row that conflates them tells a learner to wait
    for something that cannot arrive — `bookmarks.MarkStanding` carries the
    argument for each.
    """
    supported_limit_reason: str | None
    """Why the run stopped at a declared limit of the model's domain, or
    `None` if it did not.

    A non-`None` value means the run reached the supported run length and
    the core refused the next step. `is_running` is `False`, and this is
    neither a pause nor a failure: nothing was miscalculated, no step was
    rolled back, and every value in this snapshot is a completed step's at
    a simulated time inside the supported span. What ended is the claim
    that a further step would stand for a patient.

    It is separate from `failure_reason` because the interface must not
    present the two alike. Telling a reader the simulator broke, when it
    stopped exactly where `docs/MODEL.md` says it should, misrepresents a
    correct model as a defective one - and the reverse would be worse.
    Both are `None` for a run that is merely paused.
    """
    failure_reason: str | None
    """Why the run stopped abnormally, or `None` if it did not.

    A non-`None` value means a step or a setting raised and the session is
    halted: `is_running` is `False`, but this is not the same state as a
    user pause, and the interface must not present it as one.

    Every other field in this snapshot is nonetheless a completed step's.
    `AgentUptakeSystem.advance()` rolls a failed step back, and elapsed
    time advances only after it returns, so a halted session reports the
    last step that finished — at the simulation time it finished at —
    rather than one abandoned partway through.
    """

    @property
    def has_recorded_run(self) -> bool:
        """Whether this run holds anything that starting over would destroy.

        True once the run has advanced past its first sample or has recorded
        a setting change; false for a run that has been built and not yet
        touched, which is the state both a fresh session and `reset()` leave.

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
        """

        return self.elapsed_s > 0.0 or bool(self.control_timeline)


@dataclass(frozen=True, slots=True)
class ResumePoint:
    """Everything a branch needs in order to have opened where it did.

    Five things that only mean anything together, so they travel together
    rather than as five attributes a later edit could set one of - the
    argument `RunSegment` already makes about its own two halves. A branch
    rebuilt from four of these and a stale fifth would open at a state its
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
            bookmark. It is where the branch's clock and its live system
            stand.
        step_count: How many steps the case had completed at the fork, so
            the branch's clock continues the case's rather than restarting.
            `docs/MODEL.md` § "Supported run length" is measured against this.
        simulation_step_s: The step the case has been taken at, or `None` for
            a fork from a run that has not stepped. A branch keeps its
            parent's cadence; `SimulationState` refuses a different one.
        accounting_anchor_l: The agent the *case's* accounting period started
            from, carried rather than re-derived. `AgentUptakeSystem.resume_at`
            says why deriving it is unsafe.
    """

    segment: RunSegment
    fork: Keyframe
    step_count: int
    simulation_step_s: float | None
    accounting_anchor_l: float

    @property
    def elapsed_s(self) -> float:
        """The fork instant, in the case's own time.

        The instant the branch *began*, which is what every reader of this
        wants: where the clock stands, what a reset returns to, and where
        `drawn_window` stops drawing to the left. It is not in general the
        instant the branch's run definition opens at - see `fork` above.
        """

        return self.fork.instant_s


class SimulationController:
    """Own run controls and read-only history for one app session."""

    def __init__(
        self,
        agent_id: str = "sevoflurane",
        circuit_volume_l: float | None = None,
        fresh_gas_flow_l_min: float | None = None,
        delivered_partial_pressure_fraction: Fraction | None = None,
        alveolar_ventilation_l_min: float | None = None,
        cardiac_output_l_min: float | None = None,
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
        self._supported_limit_reason: str | None = None
        # What this run has done with the marks, as opposed to what is marked.
        # Both are the run's product rather than the learner's question, so
        # both are cleared wherever a new run begins - `_build_state`, which
        # `set_agent` comes back through, and `reset()` - while `_bookmarks`
        # below survives all of it.
        self._bookmark_halt: BookmarkCrossing | None = None
        self._reached_instants_s: frozenset[float] = frozenset()
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
            delivered_partial_pressure_fraction=delivered_partial_pressure_fraction,
            alveolar_ventilation_l_min=alveolar_ventilation_l_min,
            cardiac_output_l_min=cardiac_output_l_min,
        )

    def _forget_reached_marks(self) -> None:
        """Clear what *this run* did with the marks, keeping the marks themselves.

        Called wherever a new run begins. A mark is the learner's question and
        survives; whether a run halted on one is that run's product and does
        not, because a standing carried across a reset would report a crossing
        that the run now on screen never took.
        """

        self._bookmark_halt = None
        self._reached_instants_s = frozenset()
        self._reached_crossings = frozenset()

    def _build_state(
        self,
        agent_id: str,
        circuit_volume_l: float | None,
        fresh_gas_flow_l_min: float | None,
        delivered_partial_pressure_fraction: Fraction | None,
        alveolar_ventilation_l_min: float | None,
        cardiac_output_l_min: float | None,
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

        if delivered_partial_pressure_fraction is not None:
            uptake_system.set_delivered_partial_pressure_fraction(
                delivered_partial_pressure_fraction
            )

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
            uptake_system.equation_settings(), uptake_system.state_vector(), opened_at_s=0.0
        )
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
        self._supported_limit_reason = None

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

    @property
    def has_reached_supported_limit(self) -> bool:
        """Whether the run stopped at a declared limit of the model's domain."""

        return self._supported_limit_reason is not None

    def halt_at_supported_limit(self, reason: str) -> None:
        """Stop the run because it reached the end of the supported domain.

        Distinct from `fail()`, which records that something went wrong,
        and from `pause()`, which the run resumes from. Here nothing went
        wrong and there is nothing to resume *to*: the core refused the
        next step before taking it, so the run stands on a completed step
        at a simulated time the model is claimed to represent a patient at,
        and the step after it would be refused identically.

        Resuming is therefore not offered, for the reason `fail()` gives -
        a Start that does nothing is a control presenting itself as
        working - and `reset()` or `set_agent()` is the way to a new run.
        What differs is only what the interface says about it, and that
        difference is required rather than cosmetic: see
        `SimulationSnapshot.supported_limit_reason`.

        The first reason is kept, like `fail()`'s, so a later tick reaching
        the same boundary cannot overwrite the one that explains it.
        """

        self._is_running = False

        if self._supported_limit_reason is None:
            self._supported_limit_reason = reason

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
            SimulationConfigurationError: This run is a branch.
        """

        if self._opened_from is not None:
            raise SimulationConfigurationError(
                f"this run is a branch opened at {self._opened_from.elapsed_s} s, and a branch "
                "carries the agent of the case it continues; changing agent begins a new case, "
                "so change it on the run this branch came from or start a new one"
            )

        self.pause()
        current = self.snapshot()

        self._forget_reached_marks()
        self._build_state(
            agent_id=agent_id,
            circuit_volume_l=current.circuit_volume_l,
            fresh_gas_flow_l_min=current.fresh_gas_flow_l_min,
            delivered_partial_pressure_fraction=None,
            alveolar_ventilation_l_min=current.alveolar_ventilation_l_min,
            cardiac_output_l_min=current.cardiac_output_l_min,
        )

    def snapshot(self) -> SimulationSnapshot:
        """Build a fresh, read-only view of current simulation state."""

        system = self._state.uptake_system
        circuit = system.circuit
        alveoli = system.alveoli
        patient = system.patient
        accounting = system.agent_simulation_validation

        return SimulationSnapshot(
            is_running=self._is_running,
            elapsed_s=self._state.elapsed_s,
            agent_id=self._agent_id,
            agent_display_name=self._agent_display_name,
            max_delivered_concentration_percent=self._max_delivered_concentration_percent,
            agent_mac_percent=self._agent_mac_percent,
            agent_mac_awake=self._agent_mac_awake,
            circuit_volume_l=circuit.circuit_volume_l,
            fresh_gas_flow_l_min=circuit.fresh_gas_flow_l_min,
            delivered_partial_pressure_fraction=circuit.delivered_partial_pressure_fraction,
            alveolar_ventilation_l_min=alveoli.alveolar_ventilation_l_min,
            cardiac_output_l_min=patient.cardiac_output_l_min,
            inspired_partial_pressure_fraction=circuit.inspired_partial_pressure_fraction,
            alveolar_partial_pressure_fraction=(Fraction(alveoli.partial_pressure_fraction)),
            mixed_venous_partial_pressure_fraction=(
                Fraction(patient.mixed_venous_partial_pressure_fraction)
            ),
            vessel_rich_partial_pressure_fraction=(
                Fraction(patient.vessel_rich.partial_pressure_fraction)
            ),
            muscle_partial_pressure_fraction=(Fraction(patient.muscle.partial_pressure_fraction)),
            fat_partial_pressure_fraction=(Fraction(patient.fat.partial_pressure_fraction)),
            delivered_agent_l=accounting.delivered_agent_l,
            exhausted_agent_l=accounting.exhausted_agent_l,
            stored_agent_l=accounting.currently_stored_agent_l,
            unaccounted_agent_l=accounting.unaccounted_agent_l,
            agent_accounting_absolute_error_l=accounting.absolute_error_l,
            agent_accounting_passes_validation=accounting.passes_validation,
            control_timeline=self._control_timeline,
            bookmarks=self._bookmarks,
            bookmark_halt=self._bookmark_halt,
            bookmark_standings=self._bookmark_standings(),
            supported_limit_reason=self._supported_limit_reason,
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
        `drawn_window`'s instants. A branch's definition opens *at* the fork
        rather than at a zero of its own, so a keyframe read here needs no
        conversion to be placed on the case's axis and there is no offset for
        a caller to add. `PL-ZMRT` is where that was decided; before it, this
        was the one reader handing out instants in a second frame.
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
    def began_at_s(self) -> float:
        """The case instant this run itself began at: induction, or its fork.

        Zero on a trunk and the fork instant on a branch, on the case's own
        axis like everything else this class hands out. It is what bounds a
        run to the left - what `drawn_window` clips at, and what
        `app/bookmarks.py` reads to call a mark unreachable.

        **It is not `run_segments[0].opening.instant_s`, and inferring it from
        there is the mistake this property exists to remove** (`PL-B8MK`). A
        branch taken at a control event opens its definition at the fork, so
        the two agree; a branch taken at a bookmark opens its definition at
        the keyframe *before* the fork, because recording one at the fork
        would move the trunk's own later answers. A reader taking the first
        segment's opening for the run's beginning would place such a branch
        earlier than it exists and draw it across an interval it never lived.
        """

        return 0.0 if self._opened_from is None else self._opened_from.elapsed_s

    def resumed_at(self, elapsed_s: float) -> SimulationController:
        """Open a second live run at this run's canonical state at `elapsed_s`.

        The seam `PL-J2TD` exists for: a branch has to become something a
        learner can *manage* rather than a second curve, and managing it means
        advancing it. What comes back is an ordinary paused
        `SimulationController` that advances by the path every run takes -
        `advance()` is not overridden and no second way to move a run forward
        is introduced - standing at the state this run passed through at
        `elapsed_s`.

        **It opens at a keyframe or not at all.** `elapsed_s` must be an
        instant this run holds a keyframe for, which is its start and every
        recorded setting change. Restarting from the canonical state at any
        other instant replaces one propagation over an interval with two over
        its halves - a different rounding of the same exact solution, measured
        at up to 5.3e-13 in an accumulator - and `PL-Z3W6` requires a branch to
        reproduce its parent element-wise rather than within a tolerance. So an
        instant between two keyframes is refused rather than approximated.

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
        subtraction that does not always round-trip.

        **The settings are replayed from the control timeline, and then
        checked.** A branch is built through the ordinary constructor so that
        the circuit volume is applied before any state is - `set_circuit_volume`
        conserves agent by rewriting the inspired fraction, so a volume set
        afterwards would move the branch off its parent's keyframe silently -
        and the four live controls come from the recorded changes, which hold
        the values the compartments actually took in the units they hold them
        in. They are not recovered from the segment: that carries litres per
        second, and multiplying back by sixty does not round-trip for 7 of the
        101 cardiac outputs on a 0.1 L/min grid across the supported range
        (`PL-SM5V`). The replay is then checked against the segment's own
        settings rather than trusted, because a branch assembling a system
        matrix its parent never used would diverge from its first step inside
        the tolerance that holds the two records together.

        Args:
            elapsed_s: The case instant to open at, in seconds. Must be one
                this run holds a keyframe for.

        Returns:
            A paused `SimulationController` standing at that state, carrying
            this run's agent, patient and circuit, with an empty control
            timeline of its own and a copy of this run's bookmarks.

        Raises:
            SimulationConfigurationError: `elapsed_s` is not finite or is not
                an instant this run holds a keyframe for; this run is itself a
                branch, since a branch of a branch is refused rather than
                silently flattened (`PL-TFX5`); the fork instant is not a whole
                number of this run's steps; or the replayed settings do not
                reproduce the segment's.
        """

        return self._branch_from(self._resume_point_at(elapsed_s))

    def resumed_at_halt(self) -> SimulationController:
        """Open a second live run at the bookmark crossing this run is standing on.

        The other door to a branch, and the one `ROADMAP.md`'s v0.5.0
        Definition of done asks for when it says "a branch taken at any
        recorded control event **or bookmark**" (`PL-B8MK`). Everything a
        branch is - a paused controller carrying this run's agent, patient and
        circuit, advancing by the path every run takes - is what `resumed_at`
        describes; what differs is only where it may be taken.

        **It takes no instant, so there is none for a caller to get wrong.**
        Route two needs the run's state at the fork, and a halt is where a run
        has it: the run is standing on the crossing step with nothing computed
        past it. Offering this as a float instead would let a branch be asked
        for at a bookmark the run has not reached, or at the instant a learner
        *marked* rather than the step instant the run actually stopped on -
        which are not the same number, since a mark lying inside a step halts
        the run at the step's end. Preventing that is worth more than the
        flexibility, and widening the fork to any instant a run holds live
        state for is `PL-Z3W6`'s to ask for rather than this one's.

        **The trunk is not touched, which is the whole point of route two.**
        No keyframe is recorded where the run halted: the branch's run
        definition opens at the keyframe the parent's own stretch opens at,
        while the branch's clock and its live system stand at the fork. See
        `_open_at`, and `docs/MODEL.md` § "What this requires of a branch"
        for which of that section's two conditions this relaxes and why the
        element-wise guarantee survives it. Recording the keyframe instead -
        the obvious route - leaves the branch exact against its parent and
        displaces that parent's own later answers, 48 of 54 elements against
        the same case built unmarked, so marking a run would change it.

        Returns:
            A paused `SimulationController` standing at the halted instant,
            carrying this run's agent, patient and circuit, with an empty
            control timeline of its own and a copy of this run's bookmarks.

        Raises:
            SimulationConfigurationError: this run is not standing on a
                bookmark crossing, so there is no fork to take; this run is
                itself a branch, since a branch of a branch is refused rather
                than silently flattened; the halted instant is not a whole
                number of this run's steps; or the replayed settings do not
                reproduce the segment's.
        """

        return self._branch_from(self._resume_point_at_halt())

    def _branch_from(self, resume_point: ResumePoint) -> SimulationController:
        """Build the branch `resume_point` describes, leaving this run untouched.

        Shared by both doors to a fork - `resumed_at` and `resumed_at_halt` -
        because where a branch may be taken is the only thing that separates
        them. What a branch *is* is stated once, here.
        """

        elapsed_s = resume_point.elapsed_s
        circuit = self._state.uptake_system.circuit
        alveoli = self._state.uptake_system.alveoli
        patient = self._state.uptake_system.patient

        branch = SimulationController(
            agent_id=self._agent_id,
            circuit_volume_l=circuit.circuit_volume_l,
            fresh_gas_flow_l_min=self._setting_at(
                ControlInput.FRESH_GAS_FLOW, elapsed_s, circuit.fresh_gas_flow_l_min
            ),
            delivered_partial_pressure_fraction=Fraction(
                self._setting_at(
                    ControlInput.DELIVERED, elapsed_s, circuit.delivered_partial_pressure_fraction
                )
            ),
            alveolar_ventilation_l_min=self._setting_at(
                ControlInput.ALVEOLAR_VENTILATION, elapsed_s, alveoli.alveolar_ventilation_l_min
            ),
            cardiac_output_l_min=self._setting_at(
                ControlInput.CARDIAC_OUTPUT, elapsed_s, patient.cardiac_output_l_min
            ),
        )

        replayed = branch._state.uptake_system.equation_settings()

        if replayed != resume_point.segment.settings:
            raise SimulationConfigurationError(
                f"the settings replayed for a branch at {resume_point.elapsed_s} s are not the "
                "ones this run was computed under there, so the branch would solve equations "
                "its parent never did; the recorded timeline does not reproduce its own "
                "segments"
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

        branch._open_at(resume_point)

        return branch

    def _open_at(self, resume_point: ResumePoint) -> None:
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
        there is no replay here.

        **Where the definition opens is the fork's own question** (`PL-B8MK`),
        and it has two answers because a branch has two jobs. Under the
        settings its parent's stretch was computed with, the branch is
        reproducing that parent, and it does so by propagating from the same
        keyframe the parent propagates from - which is the stretch's opening,
        at or before the fork. Under any other settings it is a second
        management rather than a reproduction, and there is nothing to
        reproduce: it opens at the fork carrying the fork's own state, exactly
        as a reset trunk opens at its own initial state. That second case is
        `reset()`'s alone, and leaving it out would draw such a branch from
        the parent's keyframe propagated forward under settings the parent
        never used - a trace disagreeing with the readouts beside it, about
        one run.

        The two coincide for every fork at a control event, where the fork
        *is* the stretch's opening and the choice is between one keyframe and
        itself.
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
        # The definition opens under the settings the system actually holds,
        # which on a fork are the segment's - checked in `_branch_from` before
        # anything was written - and on `reset` are whatever the learner has
        # dialled since, because reset preserves settings and restores state.
        # It opens *at* a keyframe's own instant, on the case's axis, which is
        # what leaves the clock and the definition's reach one quantity.
        opens_at = (
            segment.opening if system.equation_settings() == segment.settings else resume_point.fork
        )
        self._run_definition = RunDefinition(
            system.equation_settings(), opens_at.state, opened_at_s=opens_at.instant_s
        )
        # The branch has reached the fork: it is standing there. Where the
        # definition opened earlier, the stretch between is the *parent's* and
        # the branch never lived it, so `drawn_window` clips it away - the
        # reach is what the branch may be evaluated to, not what it may be
        # drawn from.
        self._run_definition.advance_to(resume_point.fork.instant_s)
        self._opened_from = resume_point
        self._clear_control_timeline()

    def _resume_point_at(self, elapsed_s: float) -> ResumePoint:
        """Everything a branch opening at `elapsed_s` needs, or a refusal saying why.

        Raises:
            SimulationConfigurationError: this run is a branch; `elapsed_s` is
                not finite or is not one of this run's keyframes; or the
                instant is not a whole number of this run's steps.
        """

        self._require_forkable()

        if not isfinite(elapsed_s):
            raise SimulationConfigurationError(
                f"a run is opened at a finite instant, not {elapsed_s}"
            )

        openings = [segment.opening.instant_s for segment in self._run_definition.segments]

        for segment in self._run_definition.segments:
            if segment.opening.instant_s == elapsed_s:
                break
        else:
            raise SimulationConfigurationError(
                f"this run holds no keyframe at {elapsed_s} s, so opening there would restart "
                f"from two propagations where the run took one and would not reproduce it "
                f"element-wise; it holds keyframes at {openings} s"
            )

        # The fork *is* the stretch's opening here, which is what makes a
        # control event the simple case: one instant doing both jobs.
        return self._resume_point(segment, segment.opening)

    def _resume_point_at_halt(self) -> ResumePoint:
        """Everything a branch opening at this run's halt needs, or a refusal saying why.

        The fork instant is read from the clock rather than from the crossing,
        because the clock is where the state is. They are the same number -
        `BookmarkMarks.crossings_between` stamps a crossing with the instant
        the crossing step ended at, which is the instant the run then stands
        at - and taking it from the clock is what makes that agreement
        something this method does not have to rely on.

        Raises:
            SimulationConfigurationError: this run is a branch; it is not
                standing on a bookmark crossing; or the halted instant is not
                a whole number of this run's steps.
        """

        self._require_forkable()

        if self._bookmark_halt is None:
            raise SimulationConfigurationError(
                "this run is not standing on a bookmark crossing, so there is no marked "
                "instant to branch at; a fork at a mark is taken on the step that crossed "
                "it, which is where the run holds the state a branch opens from"
            )

        fork_at_s = self._state.elapsed_s

        return self._resume_point(
            self._run_definition.segment_at(fork_at_s),
            Keyframe(fork_at_s, self._run_definition.state_at(fork_at_s)),
        )

    def _require_forkable(self) -> None:
        """Refuse a fork from a run that is itself a branch.

        Raises:
            SimulationConfigurationError: this run is a branch. A branch of a
                branch is excluded rather than unimplemented (`PL-TFX5`), and
                refusing it here covers the caller holding a branch directly,
                which `BranchedCase` cannot reach.
        """

        if self._opened_from is not None:
            raise SimulationConfigurationError(
                f"this run is itself a branch opened at {self._opened_from.elapsed_s} s, and a "
                "branch of a branch is refused rather than silently flattened; branch from "
                "the trunk instead"
            )

    def _resume_point(self, segment: RunSegment, fork: Keyframe) -> ResumePoint:
        """A branch's whole provenance: the stretch it opens inside and where it stands.

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
            step_count = 0
        else:
            step_count = round(fork.instant_s / simulation_step_s)

            if step_count * simulation_step_s != fork.instant_s:
                raise SimulationConfigurationError(
                    f"{fork.instant_s} s is not a whole number of this run's "
                    f"{simulation_step_s} s steps, so a branch could not continue the case's "
                    "step count exactly"
                )

        return ResumePoint(
            segment=segment,
            fork=fork,
            step_count=step_count,
            simulation_step_s=simulation_step_s,
            accounting_anchor_l=(
                self._state.uptake_system.agent_simulation_validator.initial_agent_l
            ),
        )

    def _setting_at(self, control: ControlInput, elapsed_s: float, current: float) -> float:
        """What `control` was set to at `elapsed_s`, from this run's recorded changes.

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
            if change.control is control and change.elapsed_s <= elapsed_s:
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

        if self._supported_limit_reason is not None:
            raise SimulationDomainLimitError(
                f"this run has reached the supported run length "
                f"({self._supported_limit_reason}); reset it to start a new run"
            )

        self._is_running = True

    def pause(self) -> None:
        self._is_running = False

    def reset(self) -> None:
        """Stop the run, clear any failure or limit, and clear dynamic state.

        Settings are preserved, and so are the bookmarks, which are the
        learner's questions rather than the run's product: a reset is for
        taking the same case again, and it is the same case they were asking
        about. This is the only way out of a failed
        session, and out of one standing at the supported run length: every
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
        length is spent from where the branch actually starts.
        """

        self.pause()
        self._failure_reason = None
        self._supported_limit_reason = None
        self._forget_reached_marks()
        self._state.reset()
        uptake_system = self._state.uptake_system

        if self._opened_from is not None:
            # A branch's beginning is the fork. The case's induction is not
            # available to return to - the branch never held it - so resetting
            # to a cleared system would put the patient at zero agent at a case
            # time the model says they are loaded, which is a plausible state
            # that never happened rather than the start of anything.
            self._open_at(self._opened_from)
            return

        self._run_definition = RunDefinition(
            uptake_system.equation_settings(), uptake_system.state_vector(), opened_at_s=0.0
        )
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

    def set_fresh_gas_flow(self, fresh_gas_flow_l_min: float) -> None:
        circuit = self._state.uptake_system.circuit
        previous_value = circuit.fresh_gas_flow_l_min
        self._state.uptake_system.set_fresh_gas_flow(fresh_gas_flow_l_min)
        self._record_control_change(
            ControlInput.FRESH_GAS_FLOW, previous_value, circuit.fresh_gas_flow_l_min
        )

    def set_delivered_partial_pressure_fraction(
        self, delivered_partial_pressure_fraction: Fraction
    ) -> None:
        circuit = self._state.uptake_system.circuit
        previous_value = circuit.delivered_partial_pressure_fraction
        self._state.uptake_system.set_delivered_partial_pressure_fraction(
            delivered_partial_pressure_fraction
        )
        self._record_control_change(
            ControlInput.DELIVERED, previous_value, circuit.delivered_partial_pressure_fraction
        )

    def set_alveolar_ventilation(self, alveolar_ventilation_l_min: float) -> None:
        alveoli = self._state.uptake_system.alveoli
        previous_value = alveoli.alveolar_ventilation_l_min
        self._state.uptake_system.set_alveolar_ventilation(alveolar_ventilation_l_min)
        self._record_control_change(
            ControlInput.ALVEOLAR_VENTILATION, previous_value, alveoli.alveolar_ventilation_l_min
        )

    def set_cardiac_output(self, cardiac_output_l_min: float) -> None:
        patient = self._state.uptake_system.patient
        previous_value = patient.cardiac_output_l_min
        self._state.uptake_system.set_cardiac_output(cardiac_output_l_min)
        self._record_control_change(
            ControlInput.CARDIAC_OUTPUT, previous_value, patient.cardiac_output_l_min
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

    def _record_control_change(
        self, control: ControlInput, previous_value: float, new_value: float
    ) -> None:
        """Record one setting change, after the core has accepted it.

        Called *after* the forwarding setter returns, which is what makes a
        refused setting record nothing: the core raises before this line is
        reached, the exception reaches the interface, and the run - which
        the core left untouched - keeps a timeline that says so.

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

        # The definition first, because it is the run: the timeline below records
        # the acts a reader sees, and every branch under it is about how those
        # acts are grouped and displayed. Both are fed from here rather than
        # from the four setters, because this is the one place that means "the
        # core accepted a setting change".
        self._run_definition.record_change(self._state.uptake_system.equation_settings())

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

    def _compartment_mac_multiples(self) -> Mapping[RecordedQuantity, MacMultiple]:
        """Every compartment a target could name, in the unit a target is held in.

        One read of the state vector and one conversion per compartment,
        through `formatting.mac_multiple` and this run's own
        `agent_mac_percent` — the same divisor the readout for that
        compartment is drawn through, so a target and the number the learner
        is looking at cannot come to mean different things.

        `COMPARTMENT_STATE_INDEX` is what pairs each quantity with its
        position, rather than a second list written here: it is already the
        one place a trace could come to carry another compartment's values,
        and a crossing tested against the wrong compartment is the same defect
        as a trace drawn from one.
        """

        state = self._state.uptake_system.state_vector()

        return {
            quantity: mac_multiple(Fraction(state[index]), self._agent_mac_percent)
            for quantity, index in COMPARTMENT_STATE_INDEX.items()
        }

    def _bookmark_standings(self) -> BookmarkStandings:
        """Where each of this run's marks stands, for the snapshot to carry."""

        return self._bookmarks.standings(
            reached_instants_s=self._reached_instants_s,
            reached_crossings=self._reached_crossings,
            opened_at_s=self.began_at_s,
            run_length_cap_s=MAXIMUM_ELAPSED_SIMULATION_TIME_S,
            stopped_at_cap=self._supported_limit_reason is not None,
        )

    def advance(self, simulation_step_s: float) -> None:
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
        """

        if not self._is_running:
            return

        # Taking a step means the run is no longer standing on the crossing it
        # last halted at, whether or not this step then completes.
        self._bookmark_halt = None

        if self._bookmarks.is_empty:
            self._state.advance(simulation_step_s)
            self._run_definition.advance_to(self._state.elapsed_s)
            return

        before_s = self._state.elapsed_s
        before = self._compartment_mac_multiples()

        self._state.advance(simulation_step_s)
        # The clock and the definition's reach are one quantity on one axis, on
        # a branch as much as on a trunk, so the reach is the clock and no
        # offset is named here or anywhere. That is what `docs/MODEL.md`
        # § "The canonical evaluation rule" now requires: a branch asked for an
        # instant of the case computes its interval from the same two floats
        # its parent did, rather than from a difference that may not round-trip.
        self._run_definition.advance_to(self._state.elapsed_s)

        crossing = self._bookmarks.crossings_between(
            before_s=before_s,
            after_s=self._state.elapsed_s,
            before=before,
            after=self._compartment_mac_multiples(),
        )

        if crossing is None:
            return

        self._halt_on(crossing)

    def _halt_on(self, crossing: BookmarkCrossing) -> None:
        """Pause the run on the step that crossed these marks, and record it.

        Args:
            crossing: What the step just taken passed through.
        """

        self._is_running = False
        self._bookmark_halt = crossing
        self._reached_instants_s |= {bookmark.instant_s for bookmark in crossing.time_bookmarks}
        self._reached_crossings |= {target.crossing_key for target in crossing.mac_targets}


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
                f"{trunk.opened_from.elapsed_s} s; branches of branches are excluded rather "
                "than unimplemented, so build the case on the run the branch came from"
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
    def fork_points_s(self) -> tuple[float, ...]:
        """The case instants a fork may be taken at, earliest first.

        The trunk's keyframes: its opening at induction, and every setting
        change the model was actually stepped under. That is what `PL-TFX5`
        means by "any recorded control-input-timeline event" - the run holds a
        keyframe at exactly those instants, and a fork taken anywhere else
        would restart from two propagations where the run took one, which
        `SimulationController.resumed_at` refuses rather than approximates.

        Induction is included rather than filtered out. A fork at zero is a
        second management of the whole case, which is a comparison a learner
        may legitimately want; it is a strange one to offer under a control
        labelled "branch here", but that is the interface's judgment to make
        and not this list's to pre-empt.

        A **bookmark** is not one of these and does not become one
        (`PL-B8MK`). Making it one would mean recording a keyframe where the
        run halted, which leaves the branch exact against its parent and
        displaces that parent's own later answers - marking a run would change
        it. A fork at a mark is taken through `fork_at_halt` instead, which
        needs no keyframe and so adds no instant to this list.
        """

        return tuple(segment.opening.instant_s for segment in self._trunk.run_segments)

    def fork_at(self, elapsed_s: float) -> SimulationController:
        """Take a branch from the trunk at `elapsed_s`, and keep it.

        The trunk is left exactly as it was - `resumed_at` reads it and writes
        nothing - so the case gains a run rather than trading one for another,
        which is what makes this a comparison instead of an undo.

        Args:
            elapsed_s: The case instant to branch at, in seconds, from
                `fork_points_s`.

        Returns:
            The new branch, paused at the trunk's state at that instant,
            carrying the trunk's agent and patient. It is also appended to
            `branches`, so a caller that discards the return value has not
            lost it.

        Raises:
            SimulationConfigurationError: `elapsed_s` is not one of
                `fork_points_s`, is not finite, or is not a whole number of
                the trunk's steps. `resumed_at` raises these and names which.
        """

        return self._kept(self._trunk.resumed_at(elapsed_s))

    def fork_at_halt(self) -> SimulationController:
        """Take a branch from the trunk where a bookmark has halted it, and keep it.

        The other half of `ROADMAP.md`'s v0.5.0 Definition of done - "a branch
        taken at any recorded control event **or bookmark**" - where
        `fork_at` is the first half. It takes no instant, because the fork is
        the one the trunk is standing on; `SimulationController.resumed_at_halt`
        says why that is the interface rather than a widened `fork_at`.

        Returns:
            The new branch, paused at the trunk's state at the halted instant,
            carrying the trunk's agent and patient. It is also appended to
            `branches`, so a caller that discards the return value has not
            lost it. The trunk is left standing on its halt.

        Raises:
            SimulationConfigurationError: the trunk is not standing on a
                bookmark crossing, or the halted instant is not a whole number
                of the trunk's steps. `resumed_at_halt` raises these and names
                which.
        """

        return self._kept(self._trunk.resumed_at_halt())

    def _kept(self, branch: SimulationController) -> SimulationController:
        """Add `branch` to this case and hand it back."""

        self._branches = (*self._branches, branch)

        return branch
