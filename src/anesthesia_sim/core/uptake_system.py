"""Couples the breathing circuit, alveolar compartment, and patient
compartments into one steppable system, and builds that system from the agent,
reference-patient and apparatus parameter files via `for_agent()`.

Named for uptake rather than for anatomy. What this module owns is agent
moving from the circuit through the alveoli into blood and tissue, which is
what "uptake" names in inhaled-anesthetic pharmacology. Only `alveoli` is
respiratory in the clinical sense: `circuit` is anesthesia-machine equipment,
and `patient` holds the vessel-rich, muscle and fat compartments.

The distinction is not cosmetic. `total_stored_agent_l` sums all of them and
feeds the conservation check that can halt a run, and at steady state most of
that agent is in fat and muscle - so a reader who took the previous name
"RespiratorySystem" at face value would read that quantity as agent in the
lungs, and be wrong by a large factor on an accounting quantity (PL-006).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from anesthesia_sim.core.agent_simulation_validation import (
    AgentSimulationValidationResult,
    AgentSimulationValidator,
    AgentSimulationValidatorState,
)
from anesthesia_sim.core.alveolar import AlveolarCompartment, AlveolarCompartmentState
from anesthesia_sim.core.circuit import (
    TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN,
    BreathingCircuit,
    BreathingCircuitState,
    FreshGasExchange,
)
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationNumericalError
from anesthesia_sim.core.governing_equations import (
    ALVEOLAR_FRACTION,
    DELIVERED_AGENT_L,
    EXHAUSTED_AGENT_L,
    FIRST_TISSUE_FRACTION,
    INSPIRED_FRACTION,
    STATE_SIZE,
    UNIT_STATE,
    VENOUS_FRACTION,
    TissueGroupEquationSettings,
    UptakeEquationSettings,
    build_system_matrix,
    require_canonical_state,
)
from anesthesia_sim.core.matrix_exponential import Matrix, matrix_exponential, propagate
from anesthesia_sim.core.parameters import (
    load_agent_parameters,
    load_reference_adult_parameters,
    load_reference_circle_system_parameters,
)
from anesthesia_sim.core.patient import PatientCompartments, PatientCompartmentsState
from anesthesia_sim.core.simulation_step import SimulationStep, require_simulation_step
from anesthesia_sim.core.supported_ranges import AlveolarVentilation, CardiacOutput, FreshGasFlow
from anesthesia_sim.core.validation import require_nonnegative_finite


@dataclass(frozen=True, slots=True)
class UptakeStepResult:
    """Validation and transfer results from one complete step."""

    fresh_gas_exchange: FreshGasExchange
    circuit_to_alveolar_agent_l: float
    patient_agent_change_l: float
    agent_accounting: AgentSimulationValidationResult


@dataclass(frozen=True, slots=True)
class AgentUptakeSystemState:
    """Every dynamic value one simulation step can change.

    The counterpart of `UptakeStepResult`: that reports what a step
    did, this records what it would have to undo. Each entry is captured by
    the compartment that owns it rather than read out of it here, so that a
    dynamic field added to a compartment later without a matching capture
    is a local omission in one file rather than a partial restore that
    looks complete. `advance()` says what it is for.
    """

    circuit: BreathingCircuitState
    alveoli: AlveolarCompartmentState
    patient: PatientCompartmentsState
    agent_simulation_validator: AgentSimulationValidatorState


@dataclass(slots=True)
class AgentUptakeSystem:
    """Coupled circuit, alveolar gas, and patient compartments.

    The four forwarding setters below are this system's control surface, and
    what defines the set is that they are the live user-controllable inputs:
    fresh gas flow and delivered concentration are machine controls, alveolar
    ventilation and cardiac output are patient state, and the four are
    exactly the sliders the interface exposes. They forward rather than
    validate - each compartment keeps its own guard - so what they add is one
    place a caller can reach every setting that may change during a run
    without having to know which compartment holds it.

    A setting outside that set is reached through the compartment that owns
    it. Circuit volume is `system.circuit.set_circuit_volume()`, because it
    is a property of the rig rather than something a clinician turns mid-run,
    and adding it here would make this set mean nothing in particular.
    """

    circuit: BreathingCircuit
    alveoli: AlveolarCompartment
    patient: PatientCompartments
    agent_simulation_validator: AgentSimulationValidator = field(
        default_factory=AgentSimulationValidator
    )
    _propagator: Matrix | None = field(default=None, init=False, repr=False, compare=False)
    _propagator_key: tuple[float, ...] | None = field(
        default=None, init=False, repr=False, compare=False
    )
    """The step and the raw compartment values the cached propagator was built for.

    Not captured by `capture_state()` and not restored: a propagator is a
    function of the settings, which a step never writes and a rollback never
    changes, so the cache is still correct for whatever the rollback left.
    """

    def __post_init__(self) -> None:
        self.agent_simulation_validator.reset(initial_agent_l=self.total_stored_agent_l)

    @classmethod
    def default(cls) -> AgentUptakeSystem:
        """Build the default v0.1.0 sevoflurane system."""

        return cls.for_agent("sevoflurane")

    @classmethod
    def for_agent(cls, agent_id: str) -> AgentUptakeSystem:
        """Build a system for any built-in agent (see `AGENT_DATA_FILENAMES`).

        The circuit carries that agent's own vaporizer maximum, and starts
        at that agent's own 1 MAC rather than with the vaporizer off, which
        is all `BreathingCircuit` can default to without knowing which agent
        is in use. So a system built here can never begin at a dial position
        the corresponding real device does not have. The MAC start is
        guaranteed to be within the maximum by the cross-field check in
        `core/parameters.py`.

        Its volume and fresh gas flow are passed explicitly from
        `data/machines/reference_circle_system.json` rather than left to
        `BreathingCircuit`'s field defaults, so that every scientific constant
        a run uses comes from a cited data file (`PL-4YY1`). The alveolar
        compartment's two are passed the same way and for the same reason.

        The flow is the one of them a profile may leave out, because no
        surveyed machine publishes a startup fresh gas flow (`PL-QW19`). A run
        built from such a profile opens at
        `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`: a code constant rather than a
        file value, named here rather than reached by leaving the argument
        out, so that this path still says where its number came from. Its
        docstring gives its authority, and a test holds it equal to the
        shipped profile's own value.

        That file's deliverable fresh gas flow range travels the same route,
        and today it is `None`: the shipped profile declares no range, because
        none was reachable for any surveyed machine, so the model's envelope
        in `core/supported_ranges.py` remains the only bound on the flow. What
        the route buys is that a profile which *does* declare one narrows the
        flow this system will accept without touching that envelope
        (`PL-8PS6`).

        The two flows the files state are parsed into their checked types
        here, where the compartments are built from them, and the patient's
        cardiac output in `PatientCompartments.from_parameters` (`PL-0YYV`).
        `core/parameters.py` checks each for sign and finiteness alone and
        holds no copy of the ranges, so a file naming a flow outside its
        supported range is refused here, in the words a refused control uses,
        before any compartment holds it.

        Raises:
            SimulationConfigurationError: a file's flow is outside its
                supported range, or the profile's deliverable range excludes
                the flow the run opens at.
        """

        agent = load_agent_parameters(agent_id)
        patient_parameters = load_reference_adult_parameters()
        circuit_parameters = load_reference_circle_system_parameters()
        opening_fresh_gas_flow_l_min = (
            TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN
            if circuit_parameters.default_fresh_gas_flow_l_min is None
            else FreshGasFlow(circuit_parameters.default_fresh_gas_flow_l_min)
        )

        return cls(
            circuit=BreathingCircuit(
                circuit_volume_l=circuit_parameters.circuit_volume_l,
                fresh_gas_flow_l_min=opening_fresh_gas_flow_l_min,
                delivered_concentration_percent=agent.mac_percent,
                max_delivered_concentration_percent=agent.max_delivered_concentration_percent,
                deliverable_fresh_gas_flow_range=(
                    circuit_parameters.deliverable_fresh_gas_flow_range
                ),
            ),
            alveoli=AlveolarCompartment(
                gas_volume_l=patient_parameters.alveolar_gas_volume_l,
                alveolar_ventilation_l_min=AlveolarVentilation(
                    patient_parameters.default_alveolar_ventilation_l_min
                ),
            ),
            patient=PatientCompartments.from_parameters(agent=agent, patient=patient_parameters),
        )

    @property
    def total_stored_agent_l(self) -> float:
        """Return agent currently stored in every compartment."""

        return (
            self.circuit.agent_amount_l
            + self.alveoli.agent_amount_l
            + self.patient.total_agent_amount_l
        )

    @property
    def agent_simulation_validation(self) -> AgentSimulationValidationResult:
        """Check that all delivered agent is still accounted for."""

        return self.agent_simulation_validator.check_agent_accounting(
            currently_stored_agent_l=self.total_stored_agent_l
        )

    def set_fresh_gas_flow(self, fresh_gas_flow_l_min: FreshGasFlow) -> None:
        self.circuit.set_fresh_gas_flow(fresh_gas_flow_l_min)

    def set_delivered_concentration_percent(self, delivered_concentration_percent: Percent) -> None:
        self.circuit.set_delivered_concentration_percent(delivered_concentration_percent)

    def set_alveolar_ventilation(self, alveolar_ventilation_l_min: AlveolarVentilation) -> None:
        self.alveoli.set_alveolar_ventilation(alveolar_ventilation_l_min)

    def set_cardiac_output(self, cardiac_output_l_min: CardiacOutput) -> None:
        self.patient.set_cardiac_output(cardiac_output_l_min)

    def advance(self, simulation_step_s: SimulationStep) -> UptakeStepResult:
        """Advance one conservative, validated simulation step, or none.

        The step is all-or-nothing. `_advance_step()` applies five
        sub-exchanges in sequence, and a guard can reject the fifth after
        the first four have already written their compartments; so this
        method captures every dynamic value first and restores it on any
        exit that is not a completed step, leaving the system bit-identical
        to what it was on entry.

        The rollback is on the unwind path rather than in an `except`
        clause, so "any exit" means any: a `BaseException` — the reachable
        one being `KeyboardInterrupt`, since `_advance_step()` contains no
        `await` for a cancellation to arrive at — unwinds through it like
        anything else. Enumerating exception types instead left exactly
        that hole, measured before this changed: raising a `BaseException`
        after the circuit had been written left
        `inspired_partial_pressure_fraction` at 0.0020183972008138854 against
        0.0020003856996684967 before the step, which is the partly applied
        step this method exists to prevent, surviving in the live system
        (PL-BNPY).

        That matters because a partly applied step is not a solution of
        anything. Its numbers are an artifact of the order the operators
        ran in — the fifth having run against the second's output — rather
        than evidence of where the model broke down, and `CLAUDE.md`
        prefers an obvious failure to a plausible-looking number. Rolling
        back leaves the last completed step, which *is* a solution, so a
        caller that halts still holds state it can display and reason
        about. The diagnosis goes in the raised message instead, where it
        names the invariant and the step size a reader can act on.

        Rolling back does not make the run resumable: the model reached a
        state it could not step from, so the same step would fail again.
        The caller must stop.

        Raises:
            TypeError: `simulation_step_s` is not a `SimulationStep`, so
                nothing has checked it against the supported range
                (`core/simulation_step.py`). Checked before anything is
                changed, so the system is untouched.
            SimulationNumericalError: the step began and could not be
                completed — a value the step itself produced was refused, a
                fraction where `_write_state_vector` builds it as a
                `Fraction`, under the name of the compartment that would have
                held it. The exact propagator cannot reach this
                for any step size, because its matrix is Metzler and the
                propagator therefore entrywise nonnegative; it is cover for a
                model extension whose matrix is not a pure transfer system.
                The step has been rolled back, so what the system holds is the
                last completed step; the run must stop rather than continue
                from it.
        """

        require_simulation_step(simulation_step_s)

        state_before_step = self.capture_state()
        step_completed = False

        try:
            result = self._advance_step(simulation_step_s)
            step_completed = True

            return result
        except SimulationConfigurationError as error:
            # A guard reached here means the step produced a state the
            # model cannot represent, not that the caller passed a bad
            # value: the arguments were already checked above. Restating
            # it as a numerical error is what lets a caller tell "your
            # setting was refused, nothing changed" apart from "the run is
            # no longer trustworthy". The original guard is kept as the
            # cause so the failing invariant stays traceable.
            #
            # This is the only exception type restated. Everything else -
            # `AgentSimulationValidationError` from the accounting check, a
            # `TypeError` from some future refactor - propagates unchanged,
            # because neither is a guard rejecting a value, and rewriting an
            # accounting failure as a plain `SimulationNumericalError` would
            # erase the more specific type a caller may key on. They need
            # the same rollback all the same, which is what `finally` gives
            # them without a clause each.
            raise SimulationNumericalError(
                f"the simulation step of {simulation_step_s} s could not be completed "
                "and was rolled back, leaving the state the last completed step "
                f"produced: {error}"
            ) from error
        finally:
            # The flag rather than the exception is what decides this. A
            # rollback keyed on catching something can only undo what it
            # thought to catch, and the failure this closes was the one
            # nobody enumerates: `BaseException`. Keyed on "did the step
            # finish", the answer is right for every way out of the block,
            # including the ones that have not been invented yet.
            if not step_completed:
                self.restore_state(state_before_step)

    def capture_state(self) -> AgentUptakeSystemState:
        """Record every dynamic value, for `advance()` to roll back to."""

        return AgentUptakeSystemState(
            circuit=self.circuit.capture_state(),
            alveoli=self.alveoli.capture_state(),
            patient=self.patient.capture_state(),
            agent_simulation_validator=(self.agent_simulation_validator.capture_state()),
        )

    def restore_state(self, state: AgentUptakeSystemState) -> None:
        """Restore state previously captured by `capture_state()`.

        Every compartment restores by direct field assignment, so this
        cannot raise. That is a requirement rather than an accident: it
        runs while a failure is already being handled, and a rollback that
        could fail partway would leave exactly the partial state it exists
        to prevent.
        """

        self.circuit.restore_state(state.circuit)
        self.alveoli.restore_state(state.alveoli)
        self.patient.restore_state(state.patient)
        self.agent_simulation_validator.restore_state(state.agent_simulation_validator)

    def _advance_step(self, simulation_step_s: SimulationStep) -> UptakeStepResult:
        """Advance every compartment at once, by one exact propagation.

        Writes each compartment as it goes and does not clean up after
        itself: `advance()` is what makes a failure partway through safe,
        and this is not called from anywhere else.

        The three reported transfers come out of the same solution rather
        than out of separate calculations. Delivered and exhausted agent are
        states of the system, so the propagator integrates them along the
        trajectory it is producing. Patient uptake is the change in stored
        patient agent, which by the tissue and venous balances *is* the
        integral of the pulmonary uptake rate; and the ventilatory transfer
        is that plus the change in stored alveolar agent, because the
        alveolar balance says alveolar agent changes by exactly the
        difference of the two. `governing_equations.py` carries why they are
        recovered here instead of accumulated as rows of their own.
        """

        alveolar_agent_before_l = self.alveoli.agent_amount_l
        patient_agent_before_l = self.patient.total_agent_amount_l

        advanced = propagate(self._propagator_for(simulation_step_s), self.state_vector())

        self._write_state_vector(advanced)

        fresh_gas_exchange = FreshGasExchange(
            delivered_agent_l=advanced[DELIVERED_AGENT_L],
            exhausted_agent_l=advanced[EXHAUSTED_AGENT_L],
        )

        patient_agent_change_l = self.patient.total_agent_amount_l - patient_agent_before_l
        circuit_to_alveolar_agent_l = (
            self.alveoli.agent_amount_l - alveolar_agent_before_l + patient_agent_change_l
        )

        self.agent_simulation_validator.record_external_agent_transfer(
            delivered_agent_l=fresh_gas_exchange.delivered_agent_l,
            exhausted_agent_l=fresh_gas_exchange.exhausted_agent_l,
        )

        accounting_check = self.agent_simulation_validator.require_valid_agent_accounting(
            currently_stored_agent_l=self.total_stored_agent_l
        )

        return UptakeStepResult(
            fresh_gas_exchange=fresh_gas_exchange,
            circuit_to_alveolar_agent_l=circuit_to_alveolar_agent_l,
            patient_agent_change_l=patient_agent_change_l,
            agent_accounting=accounting_check,
        )

    def equation_settings(self) -> UptakeEquationSettings:
        """Read the governing equations' parameters out of the compartments.

        Public because it is what a run's definition is written in:
        `core/run_definition.py` records one of these per setting change and
        rebuilds the same matrix from it, so a stretch of a run is replayed from
        the settings the compartments actually held rather than from a second
        copy kept alongside them.

        Flows are passed on in the litres per minute the compartments hold,
        which is what a clinician sets, and converted by nothing: the settings
        derive the litres per second `docs/MODEL.md` § "Governing equations"
        are written in, so the value a run records is the value that was set
        (`PL-SM5V`). The delivered concentration is passed on in the percent it
        was dialled, for the same reason, and the settings derive the fraction
        (`PL-NJPB`). The vaporizer maximum goes with it, read off the circuit
        that owns it, so the record refuses what the circuit refuses and a
        stretch of a run says which limit its dial was set under (`PL-BBMG`).
        """

        patient = self.patient
        venous_blood = patient.venous_blood

        return UptakeEquationSettings(
            circuit_volume_l=self.circuit.circuit_volume_l,
            alveolar_volume_l=self.alveoli.gas_volume_l,
            venous_volume_l=venous_blood.volume_l,
            fresh_gas_flow_l_min=self.circuit.fresh_gas_flow_l_min,
            alveolar_ventilation_l_min=self.alveoli.alveolar_ventilation_l_min,
            cardiac_output_l_min=patient.cardiac_output_l_min,
            blood_gas_partition_coefficient=venous_blood.blood_gas_partition_coefficient,
            delivered_concentration_percent=self.circuit.delivered_concentration_percent,
            max_delivered_concentration_percent=self.circuit.max_delivered_concentration_percent,
            tissues=tuple(
                TissueGroupEquationSettings(
                    name=tissue.name,
                    volume_l=tissue.volume_l,
                    blood_flow_l_min=tissue.blood_flow_l_min,
                    tissue_blood_partition_coefficient=tissue.tissue_blood_partition_coefficient,
                )
                for tissue in patient.tissues
            ),
        )

    def _propagator_for(self, simulation_step_s: SimulationStep) -> Matrix:
        """Return `exp(A * simulation_step_s)`, rebuilding it if a setting moved.

        The cache is keyed on the settings themselves rather than invalidated
        by the setters, and the key is the same object the matrix is built
        from. A setter that forgot to invalidate would be a silently wrong
        clinical value at every subsequent step, with no guard anywhere in its
        path; keyed by value there is nothing to forget, and a setting reached
        through a compartment rather than through this class's own control
        surface is caught just the same.

        The comparison is the price. It is a handful of floats per step
        against a matrix exponential per settings change, and settings are
        constant for all but a few steps of a run.

        **What is compared is `_propagator_cache_key()`, not
        `equation_settings()`** (`PL-R460`). The two answer the same question -
        the key is a bijection of the settings, so equal keys mean equal
        settings - but the settings object costs four frozen dataclasses and
        about twenty validation guards to build, and it was being rebuilt at
        full cost on every step to answer a question whose answer is "no" on
        all but a few steps of a run. Measured at 7.1 us of a 33.5 us step.

        **The guards still run whenever they can discover anything.** They are
        skipped only where the key is unchanged, which is where the values are
        the ones `equation_settings()` already validated when this propagator
        was built. Any change to any of them - through a setter or written
        straight onto a compartment - moves the key, and the rebuild below
        validates before it builds.
        """

        key = self._propagator_cache_key(simulation_step_s)

        if self._propagator is None or self._propagator_key != key:
            settings = self.equation_settings()
            propagator = matrix_exponential(build_system_matrix(settings), simulation_step_s)
            self._propagator = propagator
            self._propagator_key = key

            return propagator

        return self._propagator

    def _propagator_cache_key(self, simulation_step_s: SimulationStep) -> tuple[float, ...]:
        """Return the step and every compartment value the settings record holds.

        One entry per field of `UptakeEquationSettings`, in its order, read
        straight off the compartments and converted by nothing.
        `test_the_propagator_cache_key_covers_every_equation_setting` holds the
        two in step against `dataclasses.fields()`, so a field added to the
        settings without an entry here fails rather than reintroducing the
        stale propagator this key exists to make unrepresentable. The
        vaporizer maximum is the one entry the matrix never reads; it is here
        because it is in the record, which keeps the key a bijection of the
        settings, and it costs at most one rebuild per run, where a run's
        maximum differs from the last run's (`PL-BBMG`).

        Flows are the litres per minute the compartments hold, which is what
        the settings hold too since `PL-SM5V`, and the delivered concentration
        is the percent the circuit holds, as the settings have since
        `PL-NJPB`, so equal settings and an equal key compare the same numbers.

        `TissueGroupEquationSettings.name` is the one settings field with no
        entry, because `build_system_matrix()` never reads it - the group's
        position in the tuple is what places its rows.
        `test_the_system_matrix_does_not_depend_on_a_tissue_group_s_name` is
        what keeps that true.
        """

        patient = self.patient
        venous_blood = patient.venous_blood

        return (
            simulation_step_s,
            self.circuit.circuit_volume_l,
            self.alveoli.gas_volume_l,
            venous_blood.volume_l,
            self.circuit.fresh_gas_flow_l_min,
            self.alveoli.alveolar_ventilation_l_min,
            patient.cardiac_output_l_min,
            venous_blood.blood_gas_partition_coefficient,
            self.circuit.delivered_concentration_percent,
            self.circuit.max_delivered_concentration_percent,
            *(
                value
                for tissue in patient.tissues
                for value in (
                    tissue.volume_l,
                    tissue.blood_flow_l_min,
                    tissue.tissue_blood_partition_coefficient,
                )
            ),
        )

    def state_vector(self) -> tuple[float, ...]:
        """Read the trajectory out of the compartments, in equation order.

        Public alongside `equation_settings` and for the same reason: it is the
        state a `RunDefinition` opens from (`core/run_definition.py`).

        The two accumulator states start each step at zero, so after one
        propagation they hold that step's own delivered and exhausted agent
        rather than a running total. The running totals belong to
        `AgentSimulationValidator`, which already owns an accounting period
        and can be reset independently of the trajectory.
        """

        state = [0.0] * STATE_SIZE

        state[INSPIRED_FRACTION] = self.circuit.inspired_partial_pressure_fraction
        state[ALVEOLAR_FRACTION] = self.alveoli.partial_pressure_fraction
        state[VENOUS_FRACTION] = self.patient.mixed_venous_partial_pressure_fraction

        for offset, tissue in enumerate(self.patient.tissues):
            state[FIRST_TISSUE_FRACTION + offset] = tissue.partial_pressure_fraction

        state[UNIT_STATE] = 1.0

        return tuple(state)

    def resume_at(self, state: tuple[float, ...], initial_agent_l: float) -> None:
        """Stand this system at `state`, on an accounting period anchored at `initial_agent_l`.

        The write counterpart of `state_vector()`, and how a branch's system
        comes to stand where its parent stood. `state` is a canonical state -
        `RunDefinition.state_at`'s answer, or the `Keyframe` it was composed
        from - so a branch opens from the trajectory the parent actually
        passed through rather than from a re-derivation of it. Nothing here
        advances anything: the system is positioned, and it is stepped after
        that by the ordinary `advance()`, which is the only path that moves a
        run forward.

        **The two cumulative totals are the case's, and they are carried
        rather than derived.** `state_vector()` reports each step's own
        delivered and exhausted agent, because the propagator integrates them
        over the interval it is given; a keyframe's are cumulative from the
        start of the *case*, which for a branch's keyframes is earlier than
        the run holding them - a branch opens carrying its parent's running
        totals. Writing those in continues the
        parent's mass-balance readout across the fork instead of restarting it
        at zero, which a learner comparing two managements of one case needs,
        since the agent the patient has received is the case's and not the
        branch's.

        `initial_agent_l` is the anchor of that same accounting period - what
        the *parent's* period started from - for the reason `reset()` gives
        about not resting a check on an invariant it does not establish. The
        alternative, deriving the anchor as the value that would make
        `docs/MODEL.md`'s mass-balance identity close exactly, is what this
        deliberately does not do: the canonical path's own conservation
        residual has no reason to fall on the positive side, and measured on a
        900 s sevoflurane run with two setting changes it puts the derived
        anchor at -6.9e-14 L, a negative initial amount `AgentSimulationValidator`
        rightly refuses. Carried rather than derived, that residual stays where
        it belongs - inside the check, at 6.9e-14 L against the 1e-12 L
        absolute tolerance - instead of being absorbed into the anchor where
        nothing would report it.

        The system is left untouched if any guard fires, by the route
        `advance()` uses and for the same reason: `_write_state_vector` writes
        one compartment at a time, so a fraction the model cannot represent is
        refused after earlier compartments have already been written.

        The cached propagator is neither rebuilt nor cleared, because
        `_propagator_cache_key()` reads only the settings the system matrix is
        assembled from and this writes none of them.

        Raises:
            SimulationConfigurationError: `state` did not come from the
                canonical path, is not `STATE_SIZE` long, holds a non-finite
                value, or does not carry exactly one in `UNIT_STATE`;
                `initial_agent_l` or either cumulative total is negative or not
                finite; or a fraction is outside 0 to 1, which is refused
                under the name of the compartment that would hold it.
        """

        require_canonical_state(state)
        require_nonnegative_finite("initial_agent_l", initial_agent_l)
        require_nonnegative_finite("delivered_agent_l", state[DELIVERED_AGENT_L])
        require_nonnegative_finite("exhausted_agent_l", state[EXHAUSTED_AGENT_L])

        state_before = self.capture_state()
        resumed = False

        try:
            self._write_state_vector(state)
            self.agent_simulation_validator.reset(initial_agent_l=initial_agent_l)
            self.agent_simulation_validator.record_external_agent_transfer(
                delivered_agent_l=state[DELIVERED_AGENT_L],
                exhausted_agent_l=state[EXHAUSTED_AGENT_L],
            )
            resumed = True
        finally:
            if not resumed:
                self.restore_state(state_before)

    def _write_state_vector(self, state: tuple[float, ...]) -> None:
        """Write an advanced trajectory back into the compartments.

        Each fraction is built as a `Fraction`, under the name of the
        compartment that will hold it, and handed to that compartment's own
        setter, so a fraction the model could not represent is refused -
        naming the compartment - rather than stored (`PL-SPN6`, `PL-4R3W`).
        `advance()` restates such a refusal as `SimulationNumericalError` and
        rolls the step back, which is the required behavior: an exact solution
        of the equations cannot leave the physical range, so a value that does
        is evidence the run is no longer trustworthy rather than a number to
        display.

        This is also where a step's fractions are built, and so checked,
        rather than carried: the state vector is nine bare floats, six of
        them concentrations and three of them not, and the positions are what
        separate them. `core/concentration.py` says what the type does and
        does not guarantee.

        **It checks the vector's shape not at all**, which is safe for its two
        callers and for no third. `_advance_step` hands it what `propagate`
        returned from this system's own state, and `resume_at` hands it a
        state `require_canonical_state` has already refused on length,
        finiteness and the constant. A caller reaching here with anything else
        gets an `IndexError` from a short vector, a silent truncation from a
        long one, and no complaint at all about a wrong `UNIT_STATE` - none of
        which is how the rest of `core/` refuses a value. So `resume_at` is
        the entry point for a state this system did not itself produce.
        """

        self.circuit.set_inspired_partial_pressure_fraction(
            Fraction(state[INSPIRED_FRACTION], name="inspired_partial_pressure_fraction")
        )
        self.alveoli.set_partial_pressure_fraction(
            Fraction(state[ALVEOLAR_FRACTION], name="alveolar partial_pressure_fraction")
        )
        self.patient.venous_blood.set_partial_pressure_fraction(
            Fraction(state[VENOUS_FRACTION], name="venous partial_pressure_fraction")
        )

        for offset, tissue in enumerate(self.patient.tissues):
            tissue.set_partial_pressure_fraction(
                Fraction(
                    state[FIRST_TISSUE_FRACTION + offset],
                    name=f"{tissue.name} partial_pressure_fraction",
                )
            )

    def reset(self) -> None:
        """Clear dynamic state and restart agent accounting.

        The anchor is read back out of the compartments rather than left to
        the validator's own zero default, so this says what `__post_init__`
        says: an accounting period starts from whatever the system holds.
        The two agree today - the three resets above clear every store, so
        the expression below is exactly `0.0` - and they keep agreeing if a
        compartment is ever added that resets to something other than empty.

        The default does not. Anchored at zero against compartments holding
        anything, the identity is short by that amount at every subsequent
        check, so the residual check halts a run that is in fact perfectly
        accounted for - and reports `AgentSimulationValidationError`, which
        blames the numerics for what is an anchoring defect. That is the
        safe direction to fail in, and still the wrong answer; a check must
        not rest on an invariant it does not itself establish (PL-VYXP).
        """

        self.circuit.reset()
        self.alveoli.reset()
        self.patient.reset()
        self.agent_simulation_validator.reset(initial_agent_l=self.total_stored_agent_l)
