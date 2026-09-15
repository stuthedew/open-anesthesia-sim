"""SimulationController: the boundary between the UI and the scientific
core. Owns run/pause/reset state, applies user-facing settings to the
core, and exposes read-only `SimulationSnapshot`s for the view to render.
Contains no physiological calculations of its own, and holds no default
values of its own: every unspecified setting comes from the core, which
builds it from the versioned data files.
"""

from collections.abc import Mapping
from dataclasses import dataclass, replace
from enum import StrEnum
from math import isfinite
from types import MappingProxyType
from typing import Final

from anesthesia_sim.app.wash_in import wash_in_ratio
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.exceptions import (
    SimulationConfigurationError,
    SimulationDomainLimitError,
    SimulationExecutionError,
)
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    FIRST_TISSUE_FRACTION,
    INSPIRED_FRACTION,
    VENOUS_FRACTION,
)
from anesthesia_sim.core.parameters import MacAwakeReference, load_agent_parameters
from anesthesia_sim.core.run_definition import DisplayState, RunDefinition, RunSegment
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


class ControlInput(StrEnum):
    """A setting the user can change during a run, under a stable identifier.

    The *value* of each member is what a recorded run stores, so it is
    chosen from the domain rather than from whatever the accessor happens
    to be called this release. That separation has now been paid for:
    `PL-3TLK` and `PL-9SH6` renamed both of the forwarding setters these
    members stand for - `set_delivered_concentration` became
    `set_delivered_partial_pressure_fraction`, and the circuit fraction
    became `inspired_partial_pressure_fraction` - and a timeline that had
    stored accessor names would now carry two retired ones in the history
    of every run recorded before the rename. The member names followed the
    code; the strings did not move.

    `DELIVERED` is the vaporizer dial: the concentration delivered into the
    circuit, which is not the same quantity as the inspired concentration
    the circuit reaches. Naming it for the dial would have tied it to one
    machine's control rather than to the quantity the model applies.

    These are the four live controls and there is no fifth. A
    `CIRCUIT_VOLUME` member was recorded here until `PL-GYH2` established
    the circuit volume as a fixed model parameter rather than a control:
    it was written only by `SimulationController.set_circuit_volume`, an
    app-layer setter no interface control ever reached, and retiring the
    setter left an identifier for a change a run can no longer undergo.
    Removing the member costs no recorded history, because a timeline is
    held in memory and cleared with the run that recorded it; it is never
    persisted, so no stored run carries the string.
    """

    FRESH_GAS_FLOW = "fresh_gas_flow"
    DELIVERED = "delivered"
    ALVEOLAR_VENTILATION = "alveolar_ventilation"
    CARDIAC_OUTPUT = "cardiac_output"


# The unit each control's recorded values are in, declared once and carried
# onto every entry that records one. Two properties are wanted at the same
# time and neither alone is enough: a single table is auditable at a glance
# and cannot drift between the recorder and the reader (the reason
# `chart_frame.COMPARTMENT_TRACES` is one table rather than six call sites),
# while a unit carried *on* the entry makes each recorded change
# self-describing, so a displayed line reads its unit from the change that
# produced it rather than from a lookup a later edit could desynchronise.
# `CLAUDE.md`'s safety-critical standard asks for explicit units and for a
# displayed value traceable to them; this is both halves.
#
# The values are the model's own units, not the interface's. The delivered
# concentration is stored as the fraction the core is set with, so
# re-applying a recorded timeline is a sequence of setter calls with the
# numbers already in them - the reconstruction property this item exists
# for - and the percent a reader sees is that fraction converted once, at
# the display, by the same formatter every other concentration goes
# through.
CONTROL_INPUT_UNITS: Final[Mapping[ControlInput, str]] = {
    ControlInput.FRESH_GAS_FLOW: "L/min",
    ControlInput.DELIVERED: "fraction of 1 atm",
    ControlInput.ALVEOLAR_VENTILATION: "L/min",
    ControlInput.CARDIAC_OUTPUT: "L/min",
}


@dataclass(frozen=True, slots=True)
class ControlChange:
    """One setting change the running model actually saw.

    Recorded per change rather than per user gesture, because the model
    integrates whatever value is in place at each step: a dial swept from
    2% to 4% across eight steps is eight different settings the run was
    computed under, and a record that kept only the endpoint would not
    reproduce the run it claims to describe.

    `adjustment` is what makes that faithful record readable. It groups the
    changes a user made as one act - one drag of one slider - so a reader
    sees one adjustment where the model saw eight settings. It is assigned
    from the input boundary the interface reports rather than guessed from
    the timing of the entries, so two separate turns of the same dial are
    two adjustments however close together they fall.
    """

    elapsed_s: float
    """Simulated time the change took effect, in seconds."""
    adjustment: int
    """Which user adjustment this change belongs to. See the class docstring."""
    control: ControlInput
    previous_value: float
    new_value: float
    unit: str
    """The unit both values are in, from `CONTROL_INPUT_UNITS`."""


class RecordedQuantity(StrEnum):
    """One quantity the interface draws, under a stable identifier.

    What a chart trace is bound to, and the key a drawn window is read by.
    Members are named for the compartment or the quantity rather than for
    whichever field or accessor currently spells it, for the reason
    `ControlInput`'s are: `PL-3TLK` and `PL-9SH6` renamed two of the fields
    these read from, and a key that had followed the code would have had to
    be renamed with them while meaning the same thing throughout. `CIRCUIT`
    is the one to look at - the field behind it is now
    `inspired_partial_pressure_fraction`, and this key did not move.

    `WASH_IN_RATIO` is the one derived member. It is not a compartment state
    but the quotient `app/wash_in.py` specifies, named here so that the plot
    drawing it is addressed the same way every other trace is - and it is
    deliberately absent from `COMPARTMENT_STATE_INDEX`, which is what keeps
    it from being read as a state the equations carry.
    """

    CIRCUIT = "circuit"
    ALVEOLAR = "alveolar"
    MIXED_VENOUS = "mixed_venous"
    VESSEL_RICH = "vessel_rich"
    MUSCLE = "muscle"
    FAT = "fat"
    WASH_IN_RATIO = "wash_in_ratio"


#: The compartment quantities the interface draws for each substance, in the
#: order it lists them.
#:
#: Every `RecordedQuantity` except `WASH_IN_RATIO`, which is not a compartment
#: state: it is the quotient `app/wash_in.py` forms from two of these, so
#: including it here would present a derived value as one the equations carry.
#: Written out rather than filtered from the enum, so that adding a member
#: forces a decision here instead of silently joining the compartments.
COMPARTMENT_QUANTITIES: Final = (
    RecordedQuantity.CIRCUIT,
    RecordedQuantity.ALVEOLAR,
    RecordedQuantity.MIXED_VENOUS,
    RecordedQuantity.VESSEL_RICH,
    RecordedQuantity.MUSCLE,
    RecordedQuantity.FAT,
)

#: Which core state each drawn quantity reads, by position in the state vector.
#:
#: **The whole of the run's pairing is here**, one entry per compartment, and
#: it is the one place a trace could come to carry another compartment's
#: values. It replaces the same pairing `_build_history_sample` held while the
#: chart was drawn from recorded samples (`PL-2FM6`): the chart now evaluates
#: the run definition instead, so what a trace needs is a position in
#: `governing_equations`' state order rather than a compartment accessor.
#:
#: The three tissue groups are consecutive from `FIRST_TISSUE_FRACTION` in
#: `PatientCompartmentsState.tissues`' own order, which
#: `AgentUptakeSystem.state_vector` writes them in. That order is an
#: assumption this table makes about another module, so
#: `tests/integration/test_controller.py`'s
#: `test_each_recorded_quantity_carries_the_compartment_it_names` holds it
#: against the core's own attributes rather than restating it.
#:
#: `WASH_IN_RATIO` is absent deliberately: it is not a state but the quotient
#: `app/wash_in.py` forms from two of these, so giving it a position here
#: would present a derived value as one the equations carry.
COMPARTMENT_STATE_INDEX: Final[Mapping[RecordedQuantity, int]] = MappingProxyType(
    {
        RecordedQuantity.CIRCUIT: INSPIRED_FRACTION,
        RecordedQuantity.ALVEOLAR: ALVEOLAR_FRACTION,
        RecordedQuantity.MIXED_VENOUS: VENOUS_FRACTION,
        RecordedQuantity.VESSEL_RICH: FIRST_TISSUE_FRACTION,
        RecordedQuantity.MUSCLE: FIRST_TISSUE_FRACTION + 1,
        RecordedQuantity.FAT: FIRST_TISSUE_FRACTION + 2,
    }
)


@dataclass(frozen=True, slots=True)
class RecordedSeries:
    """One recorded trace: one substance's values for one quantity.

    The address of one trace in a drawn window, and what a chart trace is
    bound to. One value rather than two loose arguments, because the binding
    is a presentation-correctness property rather than a lookup convenience:
    a trace drawn from another substance's values misstates the run exactly
    as one drawn from another compartment's does, and a pair that travels
    together cannot be half-rebound. `app/chart_frame.py`'s `_run_frame`
    builds one per drawn trace for that reason.
    """

    substance_id: str
    """Which substance's values, under the identifier the run records it by.

    A run records one substance today - the agent `SimulationController` is
    running - because `set_agent` starts a new run rather than adding to
    this one. Nitrous oxide is what makes a run's mapping wider than one
    entry; until then the shape is what carries the generality, not the data.
    """

    quantity: RecordedQuantity
    """Which of that substance's quantities. See `RecordedQuantity`."""


@dataclass(frozen=True, slots=True)
class DrawnWindow:
    """The states one frame draws, evaluated from the run's definition.

    What `SimulationController.drawn_window` answers with, and the whole of
    what the chart is drawn from. It replaces `HistoryWindow`, and the
    difference is what `PL-2FM6` is: a window over *recorded samples* asked
    which of them to draw and cost what the window spanned, where this one
    is the answer itself - the states at the instants the chart plots, and
    nothing else exists behind them.

    **A drawn value is not a recorded one, and the type says so.** Every
    state here is a `DisplayState`, which `core/run_definition.py` makes
    structurally not a state vector precisely so that a drawn value cannot
    become a keyframe, an export or a fork's opening state by having the
    right shape. `docs/MODEL.md` § "The canonical evaluation rule" is the
    guarantee; this class is one of the places it has to hold.

    Attributes:
        substance_id: Which substance every state here describes. Carried so
            a trace cannot be drawn from another substance's values: the
            frame that asks for the window names the agent its readouts were
            formatted from, and `compartment_fractions` refuses any other.
        times_s: The instants drawn, ascending, in simulated seconds.
        states: One state per instant.

    Raises:
        SimulationConfigurationError: If the two sequences differ in length,
            which would draw one trace against another's time axis.
    """

    substance_id: str
    times_s: tuple[float, ...]
    states: tuple[DisplayState, ...]

    def __post_init__(self) -> None:
        if len(self.times_s) != len(self.states):
            raise SimulationConfigurationError(
                f"a drawn window has {len(self.times_s)} instants and {len(self.states)} "
                "states; each state belongs to one instant"
            )

    def compartment_fractions(self, series: RecordedSeries) -> list[float]:
        """This trace's value at every drawn instant, as a fraction of 1 atm.

        Args:
            series: Which substance's quantity to read.
                `COMPARTMENT_STATE_INDEX` is the pairing, and it holds no
                entry for `RecordedQuantity.WASH_IN_RATIO`, which is a
                quotient rather than a state - use `wash_in_readings`.

        Returns:
            One fraction per entry of `times_s`, in the same order.

        Raises:
            SimulationConfigurationError: If `series` names a substance this
                window does not describe, or the derived wash-in ratio.
        """

        self._require_substance(series.substance_id)

        if series.quantity not in COMPARTMENT_STATE_INDEX:
            raise SimulationConfigurationError(
                f"{series.quantity} is not a compartment state; it is derived from two of "
                "them, and `wash_in_readings` is what forms it"
            )

        index = COMPARTMENT_STATE_INDEX[series.quantity]

        return [state.values[index] for state in self.states]

    def wash_in_quotients(self, substance_id: str) -> list[float | None]:
        """F_A/F_I at every drawn instant, or `None` where there is no quotient.

        `app/wash_in.py`'s rules ran once per *recorded sample* while the run
        kept a history, and the stretches they produced were maintained
        incrementally. With no history to maintain they become a property of
        the drawn column instead: the quotient is pure arithmetic over the two
        fractions this window already carries, so it is formed for what is
        being plotted rather than for samples behind it.

        That is a strengthening rather than a like-for-like move. A stretch
        boundary can now fall only on a drawn instant, so the point where the
        curve stops is a point the chart actually plots - where before it was
        a recorded sample the decimation might not have selected.

        The quotient rather than a `WashInReading` because the chart needs the
        number *outside* the domain too: a stretch is drawn one column past
        equilibrium so that it meets the reference line rather than stopping
        short of it, and choosing that column means comparing its ratio
        against the axis ceiling. `None` is `wash_in.wash_in_ratio`'s own
        answer for a denominator below the display floor, and it is the case
        with nothing to draw at all.

        Args:
            substance_id: Whose ratio. The quotient is formed from one
                substance's own two fractions.

        Returns:
            One entry per entry of `times_s`, in the same order.

        Raises:
            SimulationConfigurationError: If `substance_id` is not the one
                this window describes.
        """

        self._require_substance(substance_id)
        alveolar = COMPARTMENT_STATE_INDEX[RecordedQuantity.ALVEOLAR]
        circuit = COMPARTMENT_STATE_INDEX[RecordedQuantity.CIRCUIT]

        return [
            wash_in_ratio(state.values[alveolar], state.values[circuit]) for state in self.states
        ]

    def _require_substance(self, substance_id: str) -> None:
        """Refuse a read for a substance this window does not describe.

        The same guard the run's own store made before it was deleted, kept for the
        same reason: a trace drawn from another substance's values misstates
        the run exactly as one drawn from another compartment's does, and
        every value in it would be one the model really produced.
        """

        if substance_id != self.substance_id:
            raise SimulationConfigurationError(
                f"this window describes {self.substance_id!r}, so it cannot draw "
                f"{substance_id!r}; a run is of one agent"
            )


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

    Four things that only mean anything together, so they travel together
    rather than as four attributes a later edit could set one of - the
    argument `RunSegment` already makes about its own two halves. A branch
    rebuilt from three of these and a stale fourth would open at a state its
    settings never produced, or on an accounting period that never happened.

    It is also what `SimulationController.reset()` reads. Reset returns a run
    to its own beginning, and a branch's beginning is the fork rather than the
    case's induction, which the branch does not hold and cannot recover.

    Attributes:
        segment: The parent stretch this branch opened inside, carrying both
            the settings in force and the keyframe they start from. The
            keyframe's `elapsed_s` is the fork instant in the case's own time.
        step_count: How many steps the case had completed at that instant, so
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
    step_count: int
    simulation_step_s: float | None
    accounting_anchor_l: float

    @property
    def elapsed_s(self) -> float:
        """The fork instant, in the case's own time."""

        return self.segment.opening.instant_s


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
        self._build_state(
            agent_id=agent_id,
            circuit_volume_l=circuit_volume_l,
            fresh_gas_flow_l_min=fresh_gas_flow_l_min,
            delivered_partial_pressure_fraction=delivered_partial_pressure_fraction,
            alveolar_ventilation_l_min=alveolar_ventilation_l_min,
            cardiac_output_l_min=cardiac_output_l_min,
        )

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
            supported_limit_reason=self._supported_limit_reason,
            failure_reason=self._failure_reason,
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
            timeline of its own.

        Raises:
            SimulationConfigurationError: `elapsed_s` is not finite or is not
                an instant this run holds a keyframe for; this run is itself a
                branch, since a branch of a branch is refused rather than
                silently flattened (`PL-TFX5`); the fork instant is not a whole
                number of this run's steps; or the replayed settings do not
                reproduce the segment's.
        """

        resume_point = self._resume_point_at(elapsed_s)
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
        state. `resumed_at` is where the replayed settings are checked against
        the segment, because that check is about the *replay* and there is no
        replay here.
        """

        segment = resume_point.segment
        system = self._state.uptake_system

        # The state comes from the parent's keyframe and never from the seeded
        # system read back: a compartment stores an amount and derives its
        # fraction from its own capacity, so the round trip is not the identity
        # - 11.7% of alveolar fractions over the range a case occupies come
        # back one unit in the last place away - and the element-wise
        # reproduction `ROADMAP.md` item 12 requires would fail on exactly
        # those entries.
        system.resume_at(segment.opening.state, initial_agent_l=resume_point.accounting_anchor_l)

        self._state = SimulationState(
            uptake_system=system,
            step_count=resume_point.step_count,
            simulation_step_s=resume_point.simulation_step_s,
        )
        # The definition opens under the settings the system actually holds,
        # which on `resumed_at` are the segment's - checked there before
        # anything was written - and on `reset` are whatever the learner has
        # dialled since, because reset preserves settings and restores state.
        # It opens *at* the keyframe's own instant, on the case's axis, which
        # is what leaves the clock and the definition's reach one quantity.
        self._run_definition = RunDefinition(
            system.equation_settings(), segment.opening.state, opened_at_s=segment.opening.instant_s
        )
        self._opened_from = resume_point
        self._clear_control_timeline()

    def _resume_point_at(self, elapsed_s: float) -> ResumePoint:
        """Everything a branch opening at `elapsed_s` needs, or a refusal saying why.

        Raises:
            SimulationConfigurationError: this run is a branch; `elapsed_s` is
                not finite or is not one of this run's keyframes; or the
                instant is not a whole number of this run's steps.
        """

        if self._opened_from is not None:
            raise SimulationConfigurationError(
                f"this run is itself a branch opened at {self._opened_from.elapsed_s} s, and a "
                "branch of a branch is refused rather than silently flattened; branch from "
                "the trunk instead"
            )

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

        simulation_step_s = self._state.simulation_step_s

        if simulation_step_s is None:
            step_count = 0
        else:
            step_count = round(elapsed_s / simulation_step_s)

            if step_count * simulation_step_s != elapsed_s:
                raise SimulationConfigurationError(
                    f"{elapsed_s} s is not a whole number of this run's {simulation_step_s} s "
                    "steps, so a branch could not continue the case's step count exactly"
                )

        return ResumePoint(
            segment=segment,
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
        # lower clip is the run's *opening* rather than zero: a branch opens at
        # its fork, the axis legitimately reaches to the left of that, and
        # `RunDefinition` refuses an instant before a run existed rather than
        # answering from the nearest keyframe it has.
        first_s = max(start_s, self._run_definition.opened_at_s)
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

        Settings are preserved. This is the only way out of a failed
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

    def advance(self, simulation_step_s: float) -> None:
        """No-op while paused; otherwise advance state and record history.

        The run definition's reach is moved after the step rather than before it, so a
        step the core refuses - a domain limit, a numerical failure - leaves
        the run definition describing a run that stopped where the state did. Its
        `advance_to` records no state: the states are already implied by the
        settings, and are recovered from them on demand.
        """

        if not self._is_running:
            return

        self._state.advance(simulation_step_s)
        # The clock and the definition's reach are one quantity on one axis, on
        # a branch as much as on a trunk, so the reach is the clock and no
        # offset is named here or anywhere. That is what `docs/MODEL.md`
        # § "The canonical evaluation rule" now requires: a branch asked for an
        # instant of the case computes its interval from the same two floats
        # its parent did, rather than from a difference that may not round-trip.
        self._run_definition.advance_to(self._state.elapsed_s)


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

        A **bookmark** becomes one of these by the run halting at it: a halt
        leaves the run standing at that instant with nothing computed past it,
        so a keyframe recorded there moves no value the run has already
        produced. `docs/ARCHITECTURE.md` § "What a branch is" carries the
        measurement, and `PL-CTD7` is where the halt records it.
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

        branch = self._trunk.resumed_at(elapsed_s)
        self._branches = (*self._branches, branch)

        return branch
