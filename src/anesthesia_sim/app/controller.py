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
from typing import Final

from anesthesia_sim.core.exceptions import SimulationExecutionError
from anesthesia_sim.core.parameters import MacAwakeReference, load_agent_parameters
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


class ControlInput(StrEnum):
    """A setting the user can change during a run, under a stable identifier.

    The *value* of each member is what a recorded run stores, so it is
    chosen from the domain rather than from whatever the accessor happens
    to be called this release. `PL-9SH6` and `PL-3TLK` rename two of the
    forwarding setters in v0.4.1 - `set_delivered_concentration` becomes a
    `_partial_pressure_fraction` form, and the circuit fraction becomes
    `inspired_` - and a timeline that had stored accessor names would carry
    retired ones in the history of every run recorded before the rename.
    The member names may follow the code; the strings may not.

    `DELIVERED` is the vaporizer dial: the concentration delivered into the
    circuit, which is not the same quantity as the inspired concentration
    the circuit reaches. Naming it for the dial would have tied it to one
    machine's control rather than to the quantity the model applies.
    """

    FRESH_GAS_FLOW = "fresh_gas_flow"
    DELIVERED = "delivered"
    ALVEOLAR_VENTILATION = "alveolar_ventilation"
    CARDIAC_OUTPUT = "cardiac_output"
    CIRCUIT_VOLUME = "circuit_volume"


# The unit each control's recorded values are in, declared once and carried
# onto every entry that records one. Two properties are wanted at the same
# time and neither alone is enough: a single table is auditable at a glance
# and cannot drift between the recorder and the reader (the reason
# `chart_series.PlottedSeries` is one table rather than six call sites),
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
    ControlInput.CIRCUIT_VOLUME: "L",
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
    sample_index: int
    """Index into the run's `concentration_history` the change took effect at.

    The change applies to every step computed *after* this sample, so this
    is the last sample recorded under the previous value. It is stored
    rather than derived from `elapsed_s` because the two must not be able
    to disagree: a mark placed on the chart from a recomputed index would
    drift from the sample the model actually changed at.
    """
    adjustment: int
    """Which user adjustment this change belongs to. See the class docstring."""
    control: ControlInput
    previous_value: float
    new_value: float
    unit: str
    """The unit both values are in, from `CONTROL_INPUT_UNITS`."""


@dataclass(frozen=True, slots=True)
class SimulationHistorySample:
    """Read-only concentrations recorded at one simulation time."""

    elapsed_s: float
    circuit_concentration_fraction: float
    alveolar_concentration_fraction: float
    mixed_venous_concentration_fraction: float
    vessel_rich_partial_pressure_fraction: float
    muscle_partial_pressure_fraction: float
    fat_partial_pressure_fraction: float


@dataclass(frozen=True, slots=True)
class SimulationSnapshot:
    """Read-only simulation data exposed to the user interface."""

    is_running: bool
    elapsed_s: float
    agent_id: str
    agent_display_name: str
    max_delivered_concentration_percent: float
    agent_mac_percent: float
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
    delivered_concentration_fraction: float
    alveolar_ventilation_l_min: float
    cardiac_output_l_min: float
    circuit_concentration_fraction: float
    alveolar_concentration_fraction: float
    mixed_venous_concentration_fraction: float
    vessel_rich_partial_pressure_fraction: float
    muscle_partial_pressure_fraction: float
    fat_partial_pressure_fraction: float
    delivered_agent_l: float
    exhausted_agent_l: float
    stored_agent_l: float
    unaccounted_agent_l: float
    agent_accounting_absolute_error_l: float
    agent_accounting_passes_validation: bool
    concentration_history: tuple[SimulationHistorySample, ...]
    control_timeline: tuple[ControlChange, ...]
    """Every setting change this run has seen, oldest first.

    Empty for a run nobody has touched, and cleared with the rest of the
    run by `reset()` and by a change of agent. A setting the core refused
    is absent: it never took effect, so it is not part of the run.
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


class SimulationController:
    """Own run controls and read-only history for one app session."""

    def __init__(
        self,
        agent_id: str = "sevoflurane",
        circuit_volume_l: float | None = None,
        fresh_gas_flow_l_min: float | None = None,
        delivered_concentration_fraction: float | None = None,
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
        self._build_state(
            agent_id=agent_id,
            circuit_volume_l=circuit_volume_l,
            fresh_gas_flow_l_min=fresh_gas_flow_l_min,
            delivered_concentration_fraction=delivered_concentration_fraction,
            alveolar_ventilation_l_min=alveolar_ventilation_l_min,
            cardiac_output_l_min=cardiac_output_l_min,
        )

    def _build_state(
        self,
        agent_id: str,
        circuit_volume_l: float | None,
        fresh_gas_flow_l_min: float | None,
        delivered_concentration_fraction: float | None,
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

        if delivered_concentration_fraction is not None:
            uptake_system.set_delivered_concentration(delivered_concentration_fraction)

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
        self._concentration_history: list[SimulationHistorySample] = [self._build_history_sample()]
        self._clear_control_timeline()

        # Every compartment above is newly constructed, so no state survives
        # from a run that failed: a stale failure reason would halt a
        # session that has nothing wrong with it.
        self._failure_reason = None

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
        """

        self.pause()
        current = self.snapshot()

        self._build_state(
            agent_id=agent_id,
            circuit_volume_l=current.circuit_volume_l,
            fresh_gas_flow_l_min=current.fresh_gas_flow_l_min,
            delivered_concentration_fraction=None,
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
            max_delivered_concentration_percent=(self._max_delivered_concentration_percent),
            agent_mac_percent=self._agent_mac_percent,
            agent_mac_awake=self._agent_mac_awake,
            circuit_volume_l=circuit.circuit_volume_l,
            fresh_gas_flow_l_min=circuit.fresh_gas_flow_l_min,
            delivered_concentration_fraction=(circuit.delivered_concentration_fraction),
            alveolar_ventilation_l_min=(alveoli.alveolar_ventilation_l_min),
            cardiac_output_l_min=patient.cardiac_output_l_min,
            circuit_concentration_fraction=(circuit.circuit_concentration_fraction),
            alveolar_concentration_fraction=(alveoli.concentration_fraction),
            mixed_venous_concentration_fraction=(patient.mixed_venous_fraction),
            vessel_rich_partial_pressure_fraction=(patient.vessel_rich.partial_pressure_fraction),
            muscle_partial_pressure_fraction=(patient.muscle.partial_pressure_fraction),
            fat_partial_pressure_fraction=(patient.fat.partial_pressure_fraction),
            delivered_agent_l=accounting.delivered_agent_l,
            exhausted_agent_l=accounting.exhausted_agent_l,
            stored_agent_l=accounting.currently_stored_agent_l,
            unaccounted_agent_l=accounting.unaccounted_agent_l,
            agent_accounting_absolute_error_l=(accounting.absolute_error_l),
            agent_accounting_passes_validation=(accounting.passes_validation),
            concentration_history=tuple(self._concentration_history),
            control_timeline=self._control_timeline,
            failure_reason=self._failure_reason,
        )

    def start(self) -> None:
        """Start or resume the run, refusing to resume a failed session.

        Raising rather than quietly declining is deliberate: silently
        ignoring a start would leave the interface showing a stopped run
        with no indication that starting it did nothing, which is the
        hidden mode `CLAUDE.md` forbids.
        """

        if self._failure_reason is not None:
            raise SimulationExecutionError(
                f"cannot resume a failed simulation ({self._failure_reason}); reset it first"
            )

        self._is_running = True

    def pause(self) -> None:
        self._is_running = False

    def reset(self) -> None:
        """Stop the run, clear any failure, and clear dynamic state.

        Settings are preserved. This is the only way out of a failed
        session: every compartment goes back to its initial state, so
        nothing carries over from the run that could not continue.
        """

        self.pause()
        self._failure_reason = None
        self._state.reset()
        self._concentration_history = [self._build_history_sample()]
        self._clear_control_timeline()

    def set_circuit_volume(self, circuit_volume_l: float) -> None:
        """Change volume without creating or losing stored agent.

        The conservation and the capacity guard are the circuit's own
        (PL-006). This forwards because circuit volume is not one of the four
        live inputs `AgentUptakeSystem` exposes; it reaches the compartment
        that owns it, as the system's docstring says such a setting should.
        """

        circuit = self._state.uptake_system.circuit
        previous_value = circuit.circuit_volume_l
        circuit.set_circuit_volume(circuit_volume_l)
        self._record_control_change(
            ControlInput.CIRCUIT_VOLUME, previous_value, circuit.circuit_volume_l
        )

    def set_fresh_gas_flow(self, fresh_gas_flow_l_min: float) -> None:
        circuit = self._state.uptake_system.circuit
        previous_value = circuit.fresh_gas_flow_l_min
        self._state.uptake_system.set_fresh_gas_flow(fresh_gas_flow_l_min)
        self._record_control_change(
            ControlInput.FRESH_GAS_FLOW, previous_value, circuit.fresh_gas_flow_l_min
        )

    def set_delivered_concentration(self, delivered_concentration_fraction: float) -> None:
        circuit = self._state.uptake_system.circuit
        previous_value = circuit.delivered_concentration_fraction
        self._state.uptake_system.set_delivered_concentration(delivered_concentration_fraction)
        self._record_control_change(
            ControlInput.DELIVERED, previous_value, circuit.delivered_concentration_fraction
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

        if control is not self._open_adjustment_control:
            self._adjustment_count += 1
            self._open_adjustment_control = control
            self._open_adjustment = self._adjustment_count

        sample_index = len(self._concentration_history) - 1

        if self._control_timeline:
            latest = self._control_timeline[-1]

            if latest.control is control and latest.sample_index == sample_index:
                if latest.previous_value == new_value:
                    self._control_timeline = self._control_timeline[:-1]
                    return

                self._control_timeline = (
                    *self._control_timeline[:-1],
                    replace(latest, new_value=new_value),
                )
                return

        self._control_timeline = (
            *self._control_timeline,
            ControlChange(
                elapsed_s=self._state.elapsed_s,
                sample_index=sample_index,
                adjustment=self._open_adjustment,
                control=control,
                previous_value=previous_value,
                new_value=new_value,
                unit=CONTROL_INPUT_UNITS[control],
            ),
        )

    def advance(self, simulation_step_s: float) -> None:
        """No-op while paused; otherwise advance state and record history."""

        if not self._is_running:
            return

        self._state.advance(simulation_step_s)
        self._concentration_history.append(self._build_history_sample())

    def _build_history_sample(self) -> SimulationHistorySample:
        system = self._state.uptake_system

        return SimulationHistorySample(
            elapsed_s=self._state.elapsed_s,
            circuit_concentration_fraction=(system.circuit.circuit_concentration_fraction),
            alveolar_concentration_fraction=(system.alveoli.concentration_fraction),
            mixed_venous_concentration_fraction=(system.patient.mixed_venous_fraction),
            vessel_rich_partial_pressure_fraction=(
                system.patient.vessel_rich.partial_pressure_fraction
            ),
            muscle_partial_pressure_fraction=(system.patient.muscle.partial_pressure_fraction),
            fat_partial_pressure_fraction=(system.patient.fat.partial_pressure_fraction),
        )
