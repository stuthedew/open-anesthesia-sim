"""Couple the breathing circuit, alveolar and patient compartments into one steppable system.

The module also builds that system from the agent, reference-patient and
apparatus parameter files, through `for_agent()`.

The module is named for uptake rather than for anatomy. It owns the movement of
agent from the circuit through the alveoli into blood and tissue, and that
movement is what "uptake" means in inhaled-anesthetic pharmacology. Only
`alveoli` is respiratory in the clinical sense. `circuit` is anesthesia-machine
equipment, and `patient` holds the vessel-rich, muscle and fat compartments.

The distinction matters. `total_stored_agent_l` sums all of these compartments
and feeds the conservation check that can halt a run. At steady state, most of
that agent is in fat and muscle. So a reader who took the previous name,
"RespiratorySystem", at face value would treat that quantity as agent in the
lungs, and would be wrong by a large factor on an accounting quantity (PL-006).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

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

_PART_FIELDS = ("circuit", "alveoli", "patient", "agent_simulation_validator")
"""The fields of `AgentUptakeSystem` that hold its parts, each written once, when it is built."""


@dataclass(frozen=True, slots=True)
class UptakeStepResult:
    """Validation and transfer results from one complete step."""

    fresh_gas_exchange: FreshGasExchange
    circuit_to_alveolar_agent_l: float
    patient_agent_change_l: float
    agent_accounting: AgentSimulationValidationResult


@dataclass(frozen=True, slots=True)
class AgentUptakeSystemState:
    """Every dynamic value that one simulation step can change.

    This record is the counterpart of `UptakeStepResult`. That record reports
    what a step did, and this one records what a failed step would have to
    undo. The compartment that owns each entry captures it, rather than this
    module reading it out. So if a dynamic field is added to a compartment
    later without a matching capture, the omission is local to one file. It
    does not become a partial restore that looks complete. `advance()` explains
    what this record is for.
    """

    circuit: BreathingCircuitState
    alveoli: AlveolarCompartmentState
    patient: PatientCompartmentsState
    agent_simulation_validator: AgentSimulationValidatorState


@dataclass(slots=True)
class AgentUptakeSystem:
    """Coupled circuit, alveolar gas, and patient compartments.

    The four forwarding setters below are this system's control surface. They
    form a set because they are the inputs that a user can change during a run.
    Fresh gas flow and delivered concentration are machine controls, alveolar
    ventilation and cardiac output are patient state, and the four are exactly
    the sliders that the interface exposes. The setters forward each value
    rather than validate it, because each compartment keeps its own guard. What
    they add is one place where a caller can reach every setting that may
    change during a run, without having to know which compartment holds it.

    A setting outside that set is reached through the compartment that owns
    it. Circuit volume is set through `system.circuit.set_circuit_volume()`,
    because it is a property of the equipment rather than something a
    clinician changes during a run. Adding it here would make the set mean
    nothing in particular.
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
    """The step and the raw compartment values that the cached propagator was built for.

    `capture_state()` does not capture this key, and a rollback does not restore
    it. A propagator is a function of the settings. A step never writes the
    settings and a rollback never changes them, so the cache is still correct
    for whatever state the rollback left.
    """

    def __post_init__(self) -> None:
        """Anchor the agent accounting to what the parts hold when the system is built.

        The accounting identity compares the agent stored in the parts with
        the anchor set here, plus the agent delivered since and minus the agent
        exhausted since. So the anchor describes these particular parts.
        `__setattr__` refuses a part written onto the built system, so the
        anchor always describes the parts the system holds (`PL-N7MM`). The
        system does not refuse agent written straight into a part's own store,
        bypassing the part's methods. The accounting check finds such agent at
        the next step or the next read of the accounting.
        """

        self.agent_simulation_validator.reset(initial_agent_l=self.total_stored_agent_l)

    if not TYPE_CHECKING:  # pragma: no branch - TYPE_CHECKING is False at run time
        # This guard is hidden from `mypy` on purpose, as
        # `AlveolarCompartment.__setattr__` is. When a class defines `__setattr__`,
        # `mypy` lets code assign to any attribute name, and checks the value only
        # against the type of the method's `value` parameter. So with this guard
        # visible, a misspelt field written in `src/` would pass `--strict` and fail
        # only at run time, against the slots. With the guard hidden, `mypy` checks
        # the dataclass's fields and their types as before. The guard's own lines
        # are checked by their tests rather than by `mypy` (`PL-LBQY`).

        def __setattr__(self, name: str, value: object) -> None:
            """Write a field, refusing a part written onto a system that already has one.

            The system's parts are its circuit, its alveoli, its patient and
            its accounting validator. Each is written once, when the system is
            built, and the parts are built together for one agent. A part
            written later can break that match in two ways. If the new part
            holds agent that the anchor did not count, the next step's
            accounting check halts the run. The check then reports a numerical
            failure when the real cause was a swapped part (`reset`'s docstring
            describes the same failure). If the new part holds no agent but was
            built for another agent, no check finds it at all. Nothing in
            `src/` replaces a part, so the write is refused outright. In both
            cases the refusal names the cause at the moment of the write. A
            different part means a different system, so build a new one with
            the constructor (`PL-N7MM`). `dataclasses.replace` is not a way to
            do that. The copy it builds shares every part it is not given with
            the original, including the validator. The copy's constructor then
            re-anchors that shared validator.

            A tissue group or the venous pool written onto the patient is one
            level down, inside the patient, so this method does not check it.
            The patient checks a new group against its perfusion fractions.
            The accounting check covers the agent that a new group or pool
            holds. It also covers agent written straight into a part's own
            store.

            The constructor, a copy and a pickle write each part onto a system
            that has none yet, so those writes are accepted. The cached
            propagator and its key are not parts. `_propagator_for` writes them
            at any step, and they are keyed by the settings they were built
            from.

            Raises:
                SimulationConfigurationError: `name` names a part, and the
                    system already has that part. Nothing is written.
            """

            if name in _PART_FIELDS and hasattr(self, name):
                raise SimulationConfigurationError(
                    f"the system's {name} cannot be replaced once the system is built, "
                    "because its agent accounting is anchored to the agent its parts held "
                    "when it was built: build a new AgentUptakeSystem from the new part"
                )

            super().__setattr__(name, value)

        def __delattr__(self, name: str) -> None:
            """Refuse to delete any field.

            The check in `__setattr__` applies only to a system that already
            has the part. So a part that was deleted and then written again
            would bypass it. No field of a built system is ever meant to be
            absent, so every deletion is refused.

            Raises:
                SimulationConfigurationError: always.
            """

            raise SimulationConfigurationError(
                f"the system's {name} cannot be deleted, because a value written after it "
                "would bypass the checks made when the system is built: build a new system"
            )

    @classmethod
    def default(cls) -> AgentUptakeSystem:
        """Build the default v0.1.0 sevoflurane system."""

        return cls.for_agent("sevoflurane")

    @classmethod
    def for_agent(cls, agent_id: str) -> AgentUptakeSystem:
        """Build a system for any built-in agent (see `AGENT_DATA_FILENAMES`).

        The circuit carries that agent's own vaporizer maximum. It starts at
        that agent's own 1 MAC, not with the vaporizer off. Off is the only
        setting `BreathingCircuit` can default to without knowing which agent
        is in use. So a system built here can never begin at a dial position
        that the corresponding real device does not have. The cross-field check
        in `core/parameters.py` guarantees that the 1 MAC start is within the
        maximum.

        The circuit's volume and fresh gas flow are passed from
        `data/machines/reference_circle_system.json`, so that every scientific
        constant a run uses comes from a cited data file (`PL-4YY1`). The
        alveolar compartment's volume and ventilation are passed the same way,
        for the same reason. Neither class has a default for its volume, so
        neither can be built without one (`PL-M85T`).

        Of these values, the flow is the only one that a profile may leave out,
        because no surveyed machine publishes a startup fresh gas flow
        (`PL-QW19`). A run built from such a profile opens at
        `TEACHING_DEFAULT_FRESH_GAS_FLOW_L_MIN`. That is a code constant, not a
        file value. This method names it instead of leaving the argument out,
        so that this path still says where its number came from. The
        constant's docstring gives its authority, and a test keeps it equal to
        the shipped profile's own value.

        The machine file's deliverable fresh gas flow range is passed the same
        way. Today it is `None`. The shipped profile declares no range, because
        no range was reachable for any surveyed machine. So the model's
        envelope in `core/supported_ranges.py` remains the only bound on the
        flow. Passing the range means that a profile which *does* declare one
        narrows the flow this system will accept, without changing that
        envelope (`PL-8PS6`).

        This method parses the two flows that the files state into their
        checked types here, where the compartments are built from them. The
        patient's cardiac output is parsed in
        `PatientCompartments.from_parameters` (`PL-0YYV`). `core/parameters.py`
        checks each flow only for sign and finiteness, and holds no copy of the
        ranges. So a file that names a flow outside its supported range is
        rejected here, before any compartment holds it. The error uses the same
        words as the error for a rejected control.

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
                delivered_concentration_percent=Percent(agent.mac_percent),
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
        """Return the total agent currently stored across all compartments."""

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
        """Advance the system by one conservative, validated step, or leave it unchanged.

        The step is all-or-nothing. `_advance_step()` computes the whole step
        in one exact propagation, but it then writes the result into the
        compartments one at a time. A fraction's guard can reject a value after
        earlier compartments have already been written. The accounting check
        runs last, after every compartment has been written and the step's
        delivered and exhausted agent have been recorded in the validator.
        So this method captures every dynamic value first. It restores those
        values on any exit that is not a completed step, which leaves the
        system bit-identical to what it was on entry.

        The rollback is on the unwind path rather than in an `except` clause,
        so "any exit" really means any exit. A `BaseException` unwinds through
        the rollback like any other exception. The one that can actually arrive is
        `KeyboardInterrupt`, because `_advance_step()` contains no `await` at
        which a cancellation could arrive. Listing exception types instead
        left exactly that gap, and the gap was measured before this changed.
        Raising a `BaseException` after the circuit had been written left
        `inspired_partial_pressure_fraction` at 0.0020183972008138854, against
        0.0020003856996684967 before the step. That is the partly applied step
        that this method exists to prevent, surviving in the live system
        (PL-BNPY).

        This matters because a partly applied step is not a solution of
        anything. It holds the new step's values in the compartments already
        written and the old step's values in the rest. Its numbers are not
        evidence of where the model broke down, and `CLAUDE.md`
        prefers an obvious failure to a plausible-looking number. Rolling back
        leaves the last completed step, which *is* a solution. So a caller that
        halts still holds a state that it can display and reason about. The
        diagnosis goes in the raised message instead. There it names the
        invariant and the step size, which a reader can act on.

        Rolling back does not make the run resumable. The model reached a state
        that it could not step from, so the same step would fail again. The
        caller must stop.

        **This method also handles a settings record that the step cannot build. It raises
        that failure as a `SimulationNumericalError`, as it does for the failures described
        above.** When a setting has changed since the last step, `_advance_step` builds the
        settings record through `_propagator_for`. The record rejects tissue blood flows that
        do not sum to the cardiac output. No guarded way of changing a setting can leave the
        flows in that state. Each flow is the tissue's perfusion fraction of the patient's
        cardiac output (`PL-HQF5`). The patient rejects fractions that do not sum to 1, and a
        tissue rejects a second write of its fraction (`PL-Z0HN`). So this check is a
        safeguard, and only a write that bypasses those guards can reach it. The mismatch is
        not rejected before the step as a `SimulationConfigurationError`. That type promises
        the caller that the run is still worth continuing (`core/exceptions.py`), and a run
        whose record cannot be built is not. The same record is rejected on every later step,
        and by anything else that builds it, including a Reset. As a `SimulationNumericalError`,
        the failure tells the caller that the run has to stop. The message gives the tissues'
        total flow and the cardiac output, both in litres per minute, the unit in which the
        cardiac output was set (`PL-M4M0`).

        Raises:
            TypeError: `simulation_step_s` is not a `SimulationStep`, so
                nothing has checked it against the supported range
                (`core/simulation_step.py`). This is checked before anything
                changes, so the system is untouched.
            SimulationNumericalError: the step began and could not be
                completed. There are two causes. The first is that a value the
                step itself produced was rejected: a fraction that
                `_write_state_vector` builds as a `Fraction`, rejected under the
                name of the compartment that would have held it. The exact
                propagator cannot take a fraction below 0 for any step size,
                because its matrix is Metzler, so every entry of the propagator
                is nonnegative. A rounding error can carry a fraction above 1
                only where a fraction is already at 1. That needs a 100% dial,
                which no supported setting reaches (`core/concentration.py`).
                Otherwise this cause is a safeguard for a model extension whose
                matrix is not a pure transfer system. The second cause is that
                the settings record, from which the step builds its propagator,
                could not be built, as described above. The step has been
                rolled back, so the system holds the last completed step. The
                run must stop rather than continue from it.
        """

        require_simulation_step(simulation_step_s)

        state_before_step = self.capture_state()
        step_completed = False

        try:
            result = self._advance_step(simulation_step_s)
            step_completed = True

            return result
        except SimulationConfigurationError as error:
            # If a guard's error reaches this point, the step produced a state
            # that the model cannot represent. The caller did not pass a bad value,
            # because the arguments were already checked above. Restating the
            # error as a numerical error lets a caller tell "your setting was
            # rejected, nothing changed" apart from "the run is no longer
            # trustworthy". The guard's original error is kept as the cause, so
            # the failing invariant stays traceable.
            #
            # This is the only exception type that is restated. Everything
            # else propagates unchanged, such as `AgentSimulationValidationError`
            # from the accounting check or a `TypeError` from some future
            # refactor. Neither of those is a guard rejecting a value.
            # Rewriting an accounting failure as a plain
            # `SimulationNumericalError` would erase the more specific type
            # that a caller may rely on. These exceptions still need the same
            # rollback, and `finally` gives it to them without a separate
            # clause for each.
            raise SimulationNumericalError(
                f"the simulation step of {simulation_step_s} s could not be completed "
                "and was rolled back, leaving the state the last completed step "
                f"produced: {error}"
            ) from error
        finally:
            # The flag, not the exception, decides whether to roll back. A
            # rollback triggered by catching an exception can undo only the
            # cases it was written to catch. The failure that this closes was
            # the one nobody lists: `BaseException`. When the rollback depends
            # on whether the step finished, the decision is right for every
            # way out of the block, including ways that have not been invented
            # yet.
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
        """Restore the state previously captured by `capture_state()`.

        No compartment's restore can reject what `capture_state()` captured,
        so this method cannot raise, apart from the one exception below. The
        alveolar compartment, the venous pool and each tissue group write
        their amounts in a way that bypasses their write guards. The circuit
        and the validator write theirs through guards that cannot reject a
        captured state (`PL-19Y0`). This is a requirement, not an accident.
        The method runs while a failure is already being handled, and a
        rollback that could fail partway would leave exactly the partial state
        that it exists to prevent.

        The one exception is a circuit whose volume has shrunk since the
        capture to less than the agent that the circuit held at the capture.
        The circuit refuses to put that agent back
        (`BreathingCircuit.restore_state`, `PL-QG52`). The circuit is restored
        first, so its refusal leaves every compartment untouched. No rollback
        inside `advance()` or `resume_at()` can reach this case, because
        nothing there changes the volume.
        """

        self.circuit.restore_state(state.circuit)
        self.alveoli.restore_state(state.alveoli)
        self.patient.restore_state(state.patient)
        self.agent_simulation_validator.restore_state(state.agent_simulation_validator)

    def _advance_step(self, simulation_step_s: SimulationStep) -> UptakeStepResult:
        """Advance every compartment at once, by one exact propagation.

        The method writes each compartment as it goes and does not clean up
        after itself. `advance()` is what makes a failure partway through safe,
        and nothing else calls this method.

        The three reported transfers come from the same solution rather than
        from separate calculations. Delivered and exhausted agent are states of
        the system, so the propagator integrates them along the trajectory it
        produces. Patient uptake is the change in stored patient agent. By the
        tissue and venous balances, that change *is* the integral of the
        pulmonary uptake rate. The ventilatory transfer is the patient uptake
        plus the change in stored alveolar agent. That is because the alveolar
        balance says that alveolar agent changes by exactly the ventilatory
        transfer minus the patient uptake. `governing_equations.py` explains why these transfers are
        recovered here instead of being accumulated as rows of their own.
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

        The method is public because a run's definition is made of the records
        it returns. `core/run_definition.py` records one of these settings
        records per setting change and rebuilds the same matrix from it. So a stretch
        of a run is replayed from the settings that the compartments actually
        held, rather than from a second copy kept beside them.

        Flows are passed on in litres per minute, the unit that the compartments
        hold and that a clinician sets. Nothing here converts them. The
        settings record derives the litres per second in which `docs/MODEL.md`
        § "Governing equations" is written. So the value that a run records is
        the value that was set (`PL-SM5V`). For the same reason, the delivered
        concentration is passed on in the percent to which it was dialled, and
        the settings record derives the fraction (`PL-NJPB`). The vaporizer
        maximum is passed on with it, read from the circuit that owns it. So
        the record rejects what the circuit rejects, and a stretch of a run
        records which limit its dial was set under (`PL-BBMG`).
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
            blood_gas_partition_coefficient=patient.blood_gas_partition_coefficient,
            delivered_concentration_percent=self.circuit.delivered_concentration_percent,
            max_delivered_concentration_percent=self.circuit.max_delivered_concentration_percent,
            tissues=tuple(
                TissueGroupEquationSettings(
                    name=tissue.name,
                    volume_l=tissue.volume_l,
                    blood_flow_l_min=tissue.blood_flow_l_min_at(patient.cardiac_output_l_min),
                    tissue_blood_partition_coefficient=(
                        tissue.tissue_blood_partition_coefficient_for(
                            patient.blood_gas_partition_coefficient
                        )
                    ),
                )
                for tissue in patient.tissues
            ),
        )

    def _propagator_for(self, simulation_step_s: SimulationStep) -> Matrix:
        """Return `exp(A * simulation_step_s)`, rebuilding it if a setting changed.

        The cache is keyed on the settings themselves rather than cleared by
        the setters, and the key is the same object the matrix is built from.
        If the setters cleared the cache, a setter that forgot to clear it
        would give a silently wrong clinical value at every later step, with no
        guard anywhere in its path. With a key compared by value, there is
        nothing to forget. A setting changed through a compartment, rather than
        through this class's own control surface, is caught just the same.

        The cost of this design is the comparison: a handful of floats compared
        on every step, against one matrix exponential for each settings change.
        The settings are constant for all but a few steps of a run.

        **What is compared is `_propagator_cache_key()`, not
        `equation_settings()`** (`PL-R460`). Comparing either gives the same
        result, because the key is a bijection of the settings: equal keys mean
        equal settings. But building the settings object costs four frozen
        dataclasses and about twenty validation guards. It was being rebuilt at
        full cost on every step, to answer a question whose answer is "no" on
        all but a few steps of a run. That rebuild was measured at 7.1 us of a
        33.5 us step.

        **The guards still run whenever they could find a problem.** They are
        skipped only while the key is unchanged. In that case the values are
        the ones that `equation_settings()` already validated when this
        propagator was built. Any change to any of the values, through a setter
        or written directly onto a compartment, changes the key, and the
        rebuild below validates before it builds.
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
        """Return the step, followed by `settings_key()`."""

        return (simulation_step_s, *self.settings_key())

    def settings_key(self) -> tuple[float, ...]:
        """Return every compartment value that the settings record holds, for comparison by value.

        Equal keys mean equal `equation_settings()`. Building the key costs
        about a quarter as much as building the record: 2.2 us against 9.1 us,
        measured 2026-10-25. On 2026-10-18 it was 1.8 us against 11.0 us. The
        difference comes from the checked tissue:blood coefficient, which is now
        formed on each read (`PL-QX2G`). The key's lower cost is why the
        propagator cache compares the key rather than the record. It is also why
        `SimulationController` can call this method before every step, to check
        whether the core still holds the settings that its run definition
        recorded (`PL-XRN8`).

        The key has one entry per field of `UptakeEquationSettings`, in the
        same order. Each entry is read directly from the compartments and is
        not converted. `test_the_propagator_cache_key_covers_every_equation_setting`
        keeps the key and the settings matched by checking against
        `dataclasses.fields()`. If a field is added to the settings without an
        entry here, that test fails. So a new field cannot silently bring back
        the stale propagator that this key exists to make impossible. The
        vaporizer maximum is the one entry that the matrix never reads. It is
        included because it is in the record, so that the key and the settings
        still match one to one. Including it costs at most one rebuild of the
        propagator per run, when a run's maximum differs from the previous
        run's (`PL-BBMG`).

        The key's flows are in litres per minute. The settings have also held
        flows in litres per minute since `PL-SM5V`. The tissue flows are
        computed by the same `TissueGroup.blood_flow_l_min_at` call as the
        settings' tissue flows (`PL-HQF5`). The delivered concentration is the
        percent that the circuit holds, which the settings have also used since
        `PL-NJPB`. So equal settings and an equal key compare the same numbers.

        `TissueGroupEquationSettings.name` is the one settings field with no
        entry, because `build_system_matrix()` never reads it. The group's
        position in the tuple decides which rows of the matrix are its rows.
        `test_the_system_matrix_does_not_depend_on_a_tissue_group_s_name` keeps
        that true.
        """

        patient = self.patient
        venous_blood = patient.venous_blood

        return (
            self.circuit.circuit_volume_l,
            self.alveoli.gas_volume_l,
            venous_blood.volume_l,
            self.circuit.fresh_gas_flow_l_min,
            self.alveoli.alveolar_ventilation_l_min,
            patient.cardiac_output_l_min,
            patient.blood_gas_partition_coefficient,
            self.circuit.delivered_concentration_percent,
            self.circuit.max_delivered_concentration_percent,
            *(
                value
                for tissue in patient.tissues
                for value in (
                    tissue.volume_l,
                    tissue.blood_flow_l_min_at(patient.cardiac_output_l_min),
                    tissue.tissue_blood_partition_coefficient_for(
                        patient.blood_gas_partition_coefficient
                    ),
                )
            ),
        )

    def state_vector(self) -> tuple[float, ...]:
        """Read the trajectory out of the compartments, in equation order.

        The method is public, like `equation_settings`, and for the same
        reason. Its result is the state that a `RunDefinition` opens from
        (`core/run_definition.py`).

        The two accumulator states start each step at zero. So after one
        propagation they hold that step's own delivered and exhausted agent,
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
        """Place this system at `state`, with its accounting anchored at `initial_agent_l`.

        This is the write counterpart of `state_vector()`. It is how a branch's
        system comes to stand where its parent stood. `state` is a canonical
        state: the result of `RunDefinition.state_at`, or the `Keyframe` that
        result was composed from. So a branch opens from the trajectory that the
        parent actually passed through, rather than from a re-derivation of it.
        Nothing here advances anything. The system is positioned, and after
        that it is stepped by the ordinary `advance()`, which is the only path
        that moves a run forward.

        **The two cumulative totals belong to the case, and they are carried
        over rather than derived.** `state_vector()` reports each step's own
        delivered and exhausted agent, because the propagator integrates them
        over the interval it is given. A keyframe's totals are cumulative from
        the start of the *case*. For a branch's keyframes, the start of the case
        is earlier than the start of the run that holds them, because a branch
        opens carrying its parent's running totals. Writing those totals in
        continues the parent's mass-balance readout across the fork, instead of
        restarting it at zero. A learner comparing two managements of one case
        needs that, because the agent the patient has received belongs to the
        case and not to the branch.

        `initial_agent_l` is the anchor of that same accounting period: the
        amount that the *parent's* period started from. It is passed in rather
        than derived, for the reason that `reset()` gives: a check must not
        rest on an invariant that it does not establish. Deriving it would mean
        taking the anchor as the value that makes `docs/MODEL.md`'s
        mass-balance identity close exactly. This method deliberately does not
        do that, because the canonical path's own conservation residual has no
        reason to fall on the positive side. On a 900 s sevoflurane run with
        two setting changes, the derived anchor was measured at -6.9e-14 L.
        That is a negative initial amount, which `AgentSimulationValidator`
        rightly rejects. When the anchor is carried over rather than derived,
        that residual stays where it belongs: inside the check, at 6.9e-14 L
        against the 1e-12 L absolute tolerance. It is not absorbed into the
        anchor, where nothing would report it.

        If any guard fires, the system is left untouched, through the same
        rollback that `advance()` uses. `require_canonical_state` checks every
        fraction before anything is written, so a fraction out of range is
        refused first. A later refusal, such as the validator rejecting the
        carried-over accounting, comes after the compartments have been
        written, and the rollback undoes those writes.

        The cached propagator is neither rebuilt nor cleared, because
        `_propagator_cache_key()` reads only the settings that the system matrix
        is built from, and this method writes none of them.

        Raises:
            SimulationConfigurationError: `state` did not come from the
                canonical path, is not `STATE_SIZE` long, holds a non-finite
                value, holds a fraction outside 0 to 1 or a cumulative total
                outside 0 to `MAXIMUM_CUMULATIVE_AGENT_L`, or does not carry
                exactly one at the `UNIT_STATE` position. All of these are
                `require_canonical_state`'s checks, which a `RunDefinition`
                applies to its opening state too. The error is also raised when
                `initial_agent_l` is negative or not finite.
        """

        require_canonical_state(state)
        require_nonnegative_finite("initial_agent_l", initial_agent_l)

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
        compartment that will hold it, and passed to that compartment's own
        setter. So a fraction that the model could not represent is rejected,
        with an error that names the compartment, rather than stored
        (`PL-SPN6`, `PL-4R3W`). `advance()` restates such a rejection as
        `SimulationNumericalError` and rolls the step back, which is the
        required behavior. An exact solution of the equations cannot leave the
        physical range. So a value that does leave it is evidence that the run
        is no longer trustworthy, not a number to display.

        This method is also where a step's fractions are built, and so checked,
        rather than passed through unchecked. The state vector is nine bare
        floats. Six of them are concentrations and three are not, and only
        their positions tell them apart. `core/concentration.py` says what the
        type does and does not guarantee.

        **The method does not check the vector's shape at all.** That is safe
        for its two callers, and it would not be safe for a third.
        `_advance_step` passes it what `propagate` returned from this system's
        own state. `resume_at` passes it a state that `require_canonical_state`
        has already checked for length, finiteness, range and the constant
        entry. A caller that reached this method with anything else would get
        an `IndexError` from a short vector, a silent truncation from a long
        one, and no error at all for a wrong `UNIT_STATE`. None of these is how
        the rest of `core/` rejects a value. So `resume_at` is the entry point
        for a state that this system did not produce itself.
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

        The accounting anchor is read back from the compartments rather than
        left at the validator's own default of zero. So this method does what
        `__post_init__` does: an accounting period starts from whatever the
        system holds. Today the read-back anchor equals the zero default. The
        circuit, alveolar and patient resets clear every store, so the anchor
        expression that follows them is exactly `0.0`. Reading the anchor back
        keeps this method in agreement with `__post_init__` even if a
        compartment is ever added that resets to something other than empty.

        The zero default would not keep that agreement. Anchored at zero while the compartments
        hold some agent, the mass-balance identity would be short by that
        amount at every later check. The residual check would then halt a run
        that is in fact correctly accounted for. It would report
        `AgentSimulationValidationError`, which blames the numerics for what is
        an anchoring defect. That is the safe direction in which to fail, but it
        is still the wrong result. A check must not rest on an invariant that it
        does not itself establish (PL-VYXP).
        """

        self.circuit.reset()
        self.alveoli.reset()
        self.patient.reset()
        self.agent_simulation_validator.reset(initial_agent_l=self.total_stored_agent_l)
