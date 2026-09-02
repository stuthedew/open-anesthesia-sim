"""SimulationController: the boundary between the UI and the scientific
core. Owns run/pause/reset state, applies user-facing settings to the
core, and exposes read-only `SimulationSnapshot`s for the view to render.
Contains no physiological calculations of its own, and holds no default
values of its own: every unspecified setting comes from the core, which
builds it from the versioned data files.
"""

from dataclasses import dataclass

from anesthesia_sim.core.exceptions import SimulationExecutionError
from anesthesia_sim.core.parameters import load_agent_parameters
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


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
    circuit_time_constant_s: float
    delivered_agent_l: float
    exhausted_agent_l: float
    stored_agent_l: float
    unaccounted_agent_l: float
    agent_accounting_absolute_error_l: float
    agent_accounting_passes_validation: bool
    concentration_history: tuple[SimulationHistorySample, ...]
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
        self._state = SimulationState(uptake_system=uptake_system)
        self._concentration_history: list[SimulationHistorySample] = [self._build_history_sample()]

        # Every compartment above is newly constructed, so no state survives
        # from a run that failed: a stale failure reason would halt a
        # session that has nothing wrong with it.
        self._failure_reason = None

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
            circuit_time_constant_s=circuit.time_constant_s,
            delivered_agent_l=accounting.delivered_agent_l,
            exhausted_agent_l=accounting.exhausted_agent_l,
            stored_agent_l=accounting.currently_stored_agent_l,
            unaccounted_agent_l=accounting.unaccounted_agent_l,
            agent_accounting_absolute_error_l=(accounting.absolute_error_l),
            agent_accounting_passes_validation=(accounting.passes_validation),
            concentration_history=tuple(self._concentration_history),
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

    def set_circuit_volume(self, circuit_volume_l: float) -> None:
        """Change volume without creating or losing stored agent.

        The conservation and the capacity guard are the circuit's own
        (PL-006). This forwards because circuit volume is not one of the four
        live inputs `AgentUptakeSystem` exposes; it reaches the compartment
        that owns it, as the system's docstring says such a setting should.
        """

        self._state.uptake_system.circuit.set_circuit_volume(circuit_volume_l)

    def set_fresh_gas_flow(self, fresh_gas_flow_l_min: float) -> None:
        self._state.uptake_system.set_fresh_gas_flow(fresh_gas_flow_l_min)

    def set_delivered_concentration(self, delivered_concentration_fraction: float) -> None:
        self._state.uptake_system.set_delivered_concentration(delivered_concentration_fraction)

    def set_alveolar_ventilation(self, alveolar_ventilation_l_min: float) -> None:
        self._state.uptake_system.set_alveolar_ventilation(alveolar_ventilation_l_min)

    def set_cardiac_output(self, cardiac_output_l_min: float) -> None:
        self._state.uptake_system.set_cardiac_output(cardiac_output_l_min)

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
