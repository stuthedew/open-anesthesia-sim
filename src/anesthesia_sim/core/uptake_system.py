"""Couples the breathing circuit, alveolar compartment, and patient
compartments into one steppable system, and builds that system from agent
and reference-patient parameter files via `for_agent()`.

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
from anesthesia_sim.core.circuit import BreathingCircuit, BreathingCircuitState, FreshGasExchange
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
)
from anesthesia_sim.core.matrix_exponential import Matrix, matrix_exponential, propagate
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.patient import PatientCompartments, PatientCompartmentsState
from anesthesia_sim.core.validation import require_positive_finite

SECONDS_PER_MINUTE = 60.0

# The largest simulation step `advance()` accepts.
#
# It is not a bound on the arithmetic, and re-deriving it (`PL-X9KD`) did not
# find one. The propagator is the exact solution of the governing equations
# over whatever interval it is given, and its floating-point evaluation is
# measured across the settings envelope at 1e-14 to 2e-12 in fraction for every
# step from 1e-3 s to 3600 s - not growing with the step but U-shaped in it,
# because the only mechanism left is rounding, which accumulates once per step
# and so gets *worse* as the step shrinks. The first step at which any displayed
# digit is wrong by a whole count is around 1e13 s. No numerical ceiling
# reachable by a caller exists.
#
# What a longer step costs is control resolution. Every setting is held
# constant across a step, so a control change takes effect at the next step
# boundary and is displaced later by up to one whole step. That displacement is
# exactly proportional to the step, with no threshold anywhere in it, so no step
# size is the one at which control timing "becomes invisible" - which means this
# constant is a declared tolerance rather than a derived limit, and is recorded
# here as one.
#
# The tolerance it declares, measured 2026-09-06 in percentage points of one
# atmosphere and stated in those units rather than in counts of any readout:
# at this step the case-opening manoeuvre - dialling from off to 1 MAC at the
# reference adult's own flows - displaces every displayed compartment by at most
# 6.7e-3 pp, desflurane binding. One standard deviation of a single measured
# partition coefficient displaces one by 9e-4 to 6.8e-2 pp (Yasuda 1989; see
# docs/MODEL.md "Displayed precision"). So an ordinary control action is timed
# well inside the model's own parameter uncertainty, which is the criterion,
# and it is a criterion no display decimal count enters.
#
# What that does *not* cover, stated rather than left to be found: an abrupt
# manoeuvre is not held inside it. A ventilator start at this step displaces the
# alveolar reading by up to 1.4e-1 pp for the duration of its transient, about
# twice one parameter SD. Holding that inside one SD needs a step near 0.05 s.
#
# That was put to the project owner and decided on 2026-09-06: the value stays
# here and the timing is accepted (PL-NBCJ). Moving to 0.05 s would double the
# propagations per simulated second and force the interface's tick structure to
# be revisited, and PL-NBWP had by then narrowed what it would buy to 1x
# playback alone - above 1x the interface's own control grid is `multiplier x
# 0.1` s and dominates the step outright. So this is a declared tolerance that
# has been argued rather than a default nobody revisited, and the ventilator
# start being timed to about twice one parameter SD is the accepted cost of it
# rather than an oversight. docs/MODEL.md "Supported simulation step" carries
# the measurements and the whole of the decision.
#
# Both figures are per step of delay, and a *caller* decides how many steps of
# delay a control change waits (PL-NBWP). They are therefore what a caller
# advancing one step per control opportunity sees, which the shipped interface
# is only at 1x playback: it advances a whole tick's worth of steps between
# opportunities, so its own resolution is that many times this one - 30 s and
# up to about 10 pp at 300x, measured over the same manoeuvres. That is a
# property of the caller's loop and not of this constant, which is why the
# number here does not move; but the constant is a floor on the interface's
# resolution rather than a statement of it, and a reader who takes it for the
# latter is reading it as several hundred times better than it is. The whole
# per-rate table is in docs/MODEL.md "Supported simulation step" beside this
# one, and app/playback.py states which grid the interface actually offers.
#
# Every figure quoted above, and this constant's own value, is re-measured from
# the parameter files at each run by tests/reference/test_control_resolution.py.
# Until PL-ZVS7 they were held by this comment and by docs/MODEL.md and by
# nothing else, so moving the model would have left both documents asserting a
# tolerance the code no longer held, with make check passing.
MAXIMUM_SIMULATION_STEP_S = 0.1


def require_supported_simulation_step(simulation_step_s: float) -> None:
    """Require a step the model's control resolution is stated for.

    The guard belongs to the coupled system rather than to a compartment,
    because the interval settings are held constant over is a property of the
    step the whole system takes.

    Raises:
        SimulationConfigurationError: the step is not positive and finite, or
            exceeds `MAXIMUM_SIMULATION_STEP_S`. Nothing is calculated either
            way, so a caller can retry inside the supported range with the run
            it already has.
    """

    require_positive_finite("simulation_step_s", simulation_step_s)

    if simulation_step_s > MAXIMUM_SIMULATION_STEP_S:
        raise SimulationConfigurationError(
            f"simulation_step_s of {simulation_step_s} s is longer than the "
            f"largest supported step of {MAXIMUM_SIMULATION_STEP_S} s, over which "
            "settings are held constant"
        )


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
    _propagator_key: tuple[UptakeEquationSettings, float] | None = field(
        default=None, init=False, repr=False, compare=False
    )
    """The settings and step the cached propagator was built for.

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
        """

        agent = load_agent_parameters(agent_id)
        patient_parameters = load_reference_adult_parameters()

        return cls(
            circuit=BreathingCircuit(
                delivered_concentration_fraction=(agent.mac_percent / 100.0),
                max_delivered_concentration_fraction=(
                    agent.max_delivered_concentration_percent / 100.0
                ),
            ),
            alveoli=AlveolarCompartment(
                gas_volume_l=(patient_parameters.alveolar_gas_volume_l),
                alveolar_ventilation_l_min=(patient_parameters.default_alveolar_ventilation_l_min),
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
            currently_stored_agent_l=(self.total_stored_agent_l)
        )

    def set_fresh_gas_flow(self, fresh_gas_flow_l_min: float) -> None:
        self.circuit.set_fresh_gas_flow(fresh_gas_flow_l_min)

    def set_delivered_concentration(self, delivered_concentration_fraction: float) -> None:
        self.circuit.set_delivered_concentration(delivered_concentration_fraction)

    def set_alveolar_ventilation(self, alveolar_ventilation_l_min: float) -> None:
        self.alveoli.set_alveolar_ventilation(alveolar_ventilation_l_min)

    def set_cardiac_output(self, cardiac_output_l_min: float) -> None:
        self.patient.set_cardiac_output(cardiac_output_l_min)

    def advance(self, simulation_step_s: float) -> UptakeStepResult:
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
        `circuit_concentration_fraction` at 0.0020183972008138854 against
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
            SimulationConfigurationError: `simulation_step_s` is not a
                positive finite number, or is larger than
                `MAXIMUM_SIMULATION_STEP_S`. Checked before anything is
                changed, so the system is untouched and the caller can
                retry with a valid step.
            SimulationNumericalError: the step began and could not be
                completed — a compartment guard rejected a value produced
                by the step itself. The exact propagator cannot reach this
                for any step size, because its matrix is Metzler and the
                propagator therefore entrywise nonnegative; it is cover for a
                model extension whose matrix is not a pure transfer system.
                The step has been rolled back, so what the system holds is the
                last completed step; the run must stop rather than continue
                from it.
        """

        require_supported_simulation_step(simulation_step_s)

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

    def _advance_step(self, simulation_step_s: float) -> UptakeStepResult:
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
            delivered_agent_l=(fresh_gas_exchange.delivered_agent_l),
            exhausted_agent_l=(fresh_gas_exchange.exhausted_agent_l),
        )

        accounting_check = self.agent_simulation_validator.require_valid_agent_accounting(
            currently_stored_agent_l=(self.total_stored_agent_l)
        )

        return UptakeStepResult(
            fresh_gas_exchange=fresh_gas_exchange,
            circuit_to_alveolar_agent_l=(circuit_to_alveolar_agent_l),
            patient_agent_change_l=(patient_agent_change_l),
            agent_accounting=accounting_check,
        )

    def equation_settings(self) -> UptakeEquationSettings:
        """Read the governing equations' parameters out of the compartments.

        Public because it is what a run's definition is written in:
        `core/run_definition.py` records one of these per setting change and
        rebuilds the same matrix from it, so a stretch of a run is replayed from
        the settings the compartments actually held rather than from a second
        copy kept alongside them.

        Flows are converted to litres per second here, once, because that is
        the unit `docs/MODEL.md`'s "Governing equations" are written in and
        the compartments hold the litres per minute a clinician sets.
        """

        patient = self.patient
        venous_blood = patient.venous_blood

        return UptakeEquationSettings(
            circuit_volume_l=self.circuit.circuit_volume_l,
            alveolar_volume_l=self.alveoli.gas_volume_l,
            venous_volume_l=venous_blood.volume_l,
            fresh_gas_flow_l_s=(self.circuit.fresh_gas_flow_l_min / SECONDS_PER_MINUTE),
            alveolar_ventilation_l_s=(self.alveoli.alveolar_ventilation_l_min / SECONDS_PER_MINUTE),
            cardiac_output_l_s=(patient.cardiac_output_l_min / SECONDS_PER_MINUTE),
            blood_gas_partition_coefficient=(venous_blood.blood_gas_partition_coefficient),
            delivered_concentration_fraction=(self.circuit.delivered_concentration_fraction),
            tissues=tuple(
                TissueGroupEquationSettings(
                    name=tissue.name,
                    volume_l=tissue.volume_l,
                    blood_flow_l_s=(tissue.blood_flow_l_min / SECONDS_PER_MINUTE),
                    tissue_blood_partition_coefficient=(tissue.tissue_blood_partition_coefficient),
                )
                for tissue in patient.tissues
            ),
        )

    def _propagator_for(self, simulation_step_s: float) -> Matrix:
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
        """

        settings = self.equation_settings()
        key = (settings, simulation_step_s)

        if self._propagator is None or self._propagator_key != key:
            propagator = matrix_exponential(build_system_matrix(settings), simulation_step_s)
            self._propagator = propagator
            self._propagator_key = key

            return propagator

        return self._propagator

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

        state[INSPIRED_FRACTION] = self.circuit.circuit_concentration_fraction
        state[ALVEOLAR_FRACTION] = self.alveoli.concentration_fraction
        state[VENOUS_FRACTION] = self.patient.mixed_venous_fraction

        for offset, tissue in enumerate(self.patient.tissues):
            state[FIRST_TISSUE_FRACTION + offset] = tissue.partial_pressure_fraction

        state[UNIT_STATE] = 1.0

        return tuple(state)

    def _write_state_vector(self, state: tuple[float, ...]) -> None:
        """Write an advanced trajectory back into the compartments.

        Each compartment's own validated setter is used, so a fraction the
        model could not represent is refused by the compartment that owns it
        rather than stored. `advance()` restates such a refusal as
        `SimulationNumericalError` and rolls the step back, which is the
        required behavior: an exact solution of the equations cannot leave
        the physical range, so a value that does is evidence the run is no
        longer trustworthy rather than a number to display.
        """

        self.circuit.set_circuit_concentration_fraction(state[INSPIRED_FRACTION])
        self.alveoli.set_concentration_fraction(state[ALVEOLAR_FRACTION])
        self.patient.venous_blood.set_concentration_fraction(state[VENOUS_FRACTION])

        for offset, tissue in enumerate(self.patient.tissues):
            tissue.set_partial_pressure_fraction(state[FIRST_TISSUE_FRACTION + offset])

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
