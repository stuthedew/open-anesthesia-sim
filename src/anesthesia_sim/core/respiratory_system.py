"""Couples the breathing circuit, alveolar compartment, and patient
compartments into one steppable system, and builds that system from agent
and reference-patient parameter files via `for_agent()`.

This class currently also re-exposes some patient- and machine-level
setters (e.g. cardiac output, delivered concentration) that arguably
belong on the compartments they forward to rather than here; see the
"near-term to-dos" open thread in docs/WORKING_NOTES.md for a scoped
cleanup of this class's boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import exp

from anesthesia_sim.core.agent_simulation_validation import (
    AgentSimulationValidationResult,
    AgentSimulationValidator,
)
from anesthesia_sim.core.alveolar import AlveolarCompartment
from anesthesia_sim.core.circuit import BreathingCircuit, FreshGasExchange
from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationNumericalError
from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.patient import PatientCompartments
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
class RespiratoryStepResult:
    """Validation and transfer results from one complete step."""

    fresh_gas_exchange: FreshGasExchange
    circuit_to_alveolar_agent_l: float
    patient_agent_change_l: float
    agent_accounting: AgentSimulationValidationResult


@dataclass(slots=True)
class RespiratorySystem:
    """Coupled circuit, alveolar gas, and patient compartments."""

    circuit: BreathingCircuit
    alveoli: AlveolarCompartment
    patient: PatientCompartments
    agent_simulation_validator: AgentSimulationValidator = field(
        default_factory=AgentSimulationValidator
    )

    def __post_init__(self) -> None:
        self.agent_simulation_validator.reset(initial_agent_l=self.total_stored_agent_l)

    @classmethod
    def default(cls) -> RespiratorySystem:
        """Build the default v0.1.0 sevoflurane system."""

        return cls.for_agent("sevoflurane")

    @classmethod
    def for_agent(cls, agent_id: str) -> RespiratorySystem:
        """Build a system for any built-in agent (see `AGENT_DATA_FILENAMES`).

        The circuit carries that agent's own vaporizer maximum, and starts
        at its own 1 MAC rather than at `BreathingCircuit`'s agent-unaware
        default, so a system built here can never begin at a dial position
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

    def advance(self, simulation_step_s: float) -> RespiratoryStepResult:
        """Advance one conservative, validated simulation step.

        Raises:
            SimulationConfigurationError: `simulation_step_s` is not a
                positive finite number, or is larger than
                `MAXIMUM_SIMULATION_STEP_S`. Checked before anything is
                changed, so the system is untouched and the caller can
                retry with a valid step.
            SimulationNumericalError: the step began but could not be
                completed — a compartment guard rejected a value produced
                by the step itself, typically because the step was large
                enough for the operator split to drive an amount negative
                or a fraction outside zero through one. Compartment state
                is left partway through the step and must not be read as a
                simulation result; the caller must stop the run rather
                than continue from it.
        """

        require_supported_simulation_step(simulation_step_s)

        try:
            return self._advance_step(simulation_step_s)
        except SimulationConfigurationError as error:
            # A guard reached here means the step produced a state the
            # model cannot represent, not that the caller passed a bad
            # value: the arguments were already checked above. Restating
            # it as a numerical error is what lets a caller tell "your
            # setting was refused, nothing changed" apart from "the run is
            # no longer trustworthy". The original guard is kept as the
            # cause so the failing invariant stays traceable.
            raise SimulationNumericalError(
                f"the simulation step of {simulation_step_s} s could not be completed: {error}"
            ) from error

    def _advance_step(self, simulation_step_s: float) -> RespiratoryStepResult:
        """Apply one step's transfers, assuming the step size is valid."""

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

        return RespiratoryStepResult(
            fresh_gas_exchange=fresh_gas_exchange,
            circuit_to_alveolar_agent_l=(circuit_to_alveolar_agent_l),
            patient_agent_change_l=(patient_agent_change_l),
            agent_accounting=accounting_check,
        )

    def reset(self) -> None:
        """Clear dynamic state and restart agent accounting."""

        self.circuit.reset()
        self.alveoli.reset()
        self.patient.reset()
        self.agent_simulation_validator.reset()

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
