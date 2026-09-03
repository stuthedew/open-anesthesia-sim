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
from math import exp

from anesthesia_sim.core.agent_simulation_validation import (
    AgentSimulationValidationResult,
    AgentSimulationValidator,
    AgentSimulationValidatorState,
)
from anesthesia_sim.core.alveolar import AlveolarCompartment, AlveolarCompartmentState
from anesthesia_sim.core.circuit import BreathingCircuit, BreathingCircuitState, FreshGasExchange
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationNumericalError
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.patient import PatientCompartments, PatientCompartmentsState
from anesthesia_sim.core.validation import require_positive_finite

SECONDS_PER_MINUTE = 60.0

# The largest simulation step the shipped operator split is supported over.
# Above it `advance()` refuses the step instead of returning a number, which
# is what docs/MODEL.md's "Selected method (as implemented)" requires of a
# step outside the split's applicability domain.
#
# This is deliberately *not* the step at which the split breaks down. That is
# two orders of magnitude away and agent-dependent by a factor of four - on
# the worst reachable trajectory the capacity guard `advance()` reports as
# `SimulationNumericalError` first fires at 12 s for isoflurane, 25 s for
# sevoflurane and 50 s for desflurane - so it bounds nothing a reader could
# rely on. What this value bounds is the error:
# the split is first order, so its disagreement with the true simultaneous
# solution is C*dt with C at most 2.29e-3 s^-1 over the reachable input
# domain (docs/MODEL.md, "Independent-solution test"), and every claim
# docs/MODEL.md's "Displayed precision" makes about the last displayed digit -
# a fifth of a count in ordinary use, one count at the envelope corner, about
# two counts on the worst trajectory the sliders can reach - is that error
# measured at exactly this step. Doubling the step doubles all three, and each
# claim then reads false. So this is the largest step at which what the
# interface shows is still what the model can support, and the interface runs
# at it: `app.simulation_view.SIMULATION_STEP_S`.
#
# Raising it is a safety-critical change to every displayed value, not a
# convenience: re-measure the coefficient, re-derive the displayed resolution
# with it, and revise both sections together.
MAXIMUM_SIMULATION_STEP_S = 0.1


def require_supported_simulation_step(simulation_step_s: float) -> None:
    """Require a step the operator split has a measured error bound for.

    The guard belongs to the coupled system rather than to a compartment. A
    compartment advanced alone is an exact exponential with no splitting
    error at any step, and `tests/unit/test_circuit.py` steps a bare circuit
    60 s precisely to show that; it is composing those exact solutions in
    sequence that costs first-order accuracy, and only the composition has a
    step size it can be outside of.
    """

    require_positive_finite("simulation_step_s", simulation_step_s)

    if simulation_step_s > MAXIMUM_SIMULATION_STEP_S:
        raise SimulationConfigurationError(
            f"simulation_step_s of {simulation_step_s} s is outside the "
            f"operator split's applicability domain, which ends at "
            f"{MAXIMUM_SIMULATION_STEP_S} s"
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
                by the step itself, typically because the step was large
                enough for the operator split to drive an amount negative
                or a fraction outside zero through one. The step has been
                rolled back, so what the system holds is the last
                completed step; the run must stop rather than continue
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
        """Apply one step's transfers, assuming the step size is valid.

        Writes each compartment as it goes and does not clean up after
        itself: `advance()` is what makes a failure partway through safe,
        and this is not called from anywhere else.
        """

        fresh_gas_exchange = self.circuit.advance_fresh_gas(simulation_step_s)

        circuit_to_alveolar_agent_l = self._exchange_circuit_and_alveoli(simulation_step_s)

        patient_agent_change_l = self.patient.advance(
            arterial_fraction=(self.alveoli.concentration_fraction),
            simulation_step_s=simulation_step_s,
        )

        self.alveoli.apply_blood_uptake(patient_agent_change_l)

        self.agent_simulation_validator.record_external_agent_transfer(
            delivered_agent_l=(fresh_gas_exchange.delivered_agent_l),
            exhausted_agent_l=(fresh_gas_exchange.exhausted_agent_l),
        )

        accounting_check = self.agent_simulation_validation

        self.agent_simulation_validator.require_valid_agent_accounting(accounting_check)

        return UptakeStepResult(
            fresh_gas_exchange=fresh_gas_exchange,
            circuit_to_alveolar_agent_l=(circuit_to_alveolar_agent_l),
            patient_agent_change_l=(patient_agent_change_l),
            agent_accounting=accounting_check,
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

    def _exchange_circuit_and_alveoli(self, simulation_step_s: float) -> float:
        """Exchange agent exactly between two mixed gas volumes."""

        ventilation_l_min = self.alveoli.alveolar_ventilation_l_min

        if ventilation_l_min == 0.0:
            return 0.0

        initial_alveolar_amount_l = self.alveoli.agent_amount_l
        circuit_volume_l = self.circuit.circuit_volume_l
        alveolar_volume_l = self.alveoli.gas_volume_l
        total_gas_volume_l = circuit_volume_l + alveolar_volume_l

        equilibrium_fraction = (
            self.circuit.agent_amount_l + self.alveoli.agent_amount_l
        ) / total_gas_volume_l

        concentration_difference = (
            self.circuit.circuit_concentration_fraction - self.alveoli.concentration_fraction
        )

        ventilation_l_s = ventilation_l_min / SECONDS_PER_MINUTE
        exchange_rate_s = ventilation_l_s * (1.0 / circuit_volume_l + 1.0 / alveolar_volume_l)
        remaining_difference = concentration_difference * exp(-exchange_rate_s * simulation_step_s)

        next_circuit_fraction = (
            equilibrium_fraction + (alveolar_volume_l / total_gas_volume_l) * remaining_difference
        )
        next_alveolar_fraction = (
            equilibrium_fraction - (circuit_volume_l / total_gas_volume_l) * remaining_difference
        )

        self.circuit.set_agent_amount(circuit_volume_l * next_circuit_fraction)
        self.alveoli.set_concentration_fraction(next_alveolar_fraction)

        return self.alveoli.agent_amount_l - initial_alveolar_amount_l
