"""The breathing circuit: an ideal, well-mixed gas volume that receives
delivered fresh gas at a set concentration and exchanges agent with the
alveolar compartment (`alveolar.py`) on every step.

The circuit also owns the vaporizer delivery limit
(`max_delivered_concentration_fraction`), because it owns the delivered
concentration itself: enforcing the limit here means every path that can
change that value — core, controller, or UI — is bounded by the same
guard, rather than relying on the presentation layer to bound it.
"""

from dataclasses import dataclass
from math import exp, inf

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.validation import (
    require_concentration_fraction,
    require_nonnegative_finite,
    require_positive_finite,
)

SECONDS_PER_MINUTE = 60.0


@dataclass(frozen=True, slots=True)
class FreshGasExchange:
    """External agent entering and leaving during one circuit step."""

    delivered_agent_l: float
    exhausted_agent_l: float


@dataclass(slots=True)
class BreathingCircuit:
    """Ideal, well-mixed breathing circuit with constant volume.

    `max_delivered_concentration_fraction` is the vaporizer's calibrated
    dial maximum for the agent in use. It defaults to 1.0, meaning "no
    device limit declared", which is only appropriate for a circuit built
    without an agent (a bare unit test of circuit physics). Every
    agent-aware path builds the circuit through
    `RespiratorySystem.for_agent()`, which sets the real limit from the
    agent data file.
    """

    circuit_volume_l: float = 6.0
    fresh_gas_flow_l_min: float = 4.0
    delivered_concentration_fraction: float = 0.08
    circuit_concentration_fraction: float = 0.0
    max_delivered_concentration_fraction: float = 1.0

    def __post_init__(self) -> None:
        require_positive_finite("circuit_volume_l", self.circuit_volume_l)
        require_nonnegative_finite("fresh_gas_flow_l_min", self.fresh_gas_flow_l_min)
        require_concentration_fraction(
            "max_delivered_concentration_fraction", self.max_delivered_concentration_fraction
        )
        require_positive_finite(
            "max_delivered_concentration_fraction", self.max_delivered_concentration_fraction
        )
        require_concentration_fraction(
            "delivered_concentration_fraction", self.delivered_concentration_fraction
        )
        self._require_deliverable(self.delivered_concentration_fraction)
        require_concentration_fraction(
            "circuit_concentration_fraction", self.circuit_concentration_fraction
        )

    def _require_deliverable(self, delivered_concentration_fraction: float) -> None:
        """Reject a concentration the vaporizer in use cannot produce.

        Rejecting rather than clamping is deliberate: a silently clamped
        dial position would simulate, display, and chart a concentration
        the caller did not ask for, which is the plausible-but-wrong
        clinical value `CLAUDE.md` forbids. Zero is always allowed — it is
        the vaporizer turned off, which is how washout begins.
        """

        if delivered_concentration_fraction > self.max_delivered_concentration_fraction:
            raise SimulationConfigurationError(
                "delivered_concentration_fraction exceeds the vaporizer maximum "
                f"({delivered_concentration_fraction * 100.0:g}% requested, "
                f"{self.max_delivered_concentration_fraction * 100.0:g}% maximum)"
            )

    @property
    def agent_amount_l(self) -> float:
        """Return equivalent agent gas stored in the circuit."""

        return self.circuit_volume_l * self.circuit_concentration_fraction

    @property
    def time_constant_s(self) -> float:
        """Return the fresh-gas wash-in time constant."""

        if self.fresh_gas_flow_l_min == 0.0:
            return inf

        return SECONDS_PER_MINUTE * self.circuit_volume_l / self.fresh_gas_flow_l_min

    def set_circuit_volume(self, circuit_volume_l: float) -> None:
        require_positive_finite("circuit_volume_l", circuit_volume_l)
        self.circuit_volume_l = circuit_volume_l

    def set_fresh_gas_flow(self, fresh_gas_flow_l_min: float) -> None:
        require_nonnegative_finite("fresh_gas_flow_l_min", fresh_gas_flow_l_min)
        self.fresh_gas_flow_l_min = fresh_gas_flow_l_min

    def set_delivered_concentration(self, delivered_concentration_fraction: float) -> None:
        """Set the vaporizer dial, rejecting anything it cannot deliver."""

        require_concentration_fraction(
            "delivered_concentration_fraction", delivered_concentration_fraction
        )
        self._require_deliverable(delivered_concentration_fraction)
        self.delivered_concentration_fraction = delivered_concentration_fraction

    def set_agent_amount(self, agent_amount_l: float) -> None:
        """Set circuit state using equivalent agent gas amount."""

        require_nonnegative_finite("agent_amount_l", agent_amount_l)

        if agent_amount_l > self.circuit_volume_l:
            raise SimulationConfigurationError("agent_amount_l exceeds circuit capacity")

        self.circuit_concentration_fraction = agent_amount_l / self.circuit_volume_l

    def advance_fresh_gas(self, simulation_step_s: float) -> FreshGasExchange:
        """Advance exact circuit wash-in and report external exchange."""

        require_positive_finite("simulation_step_s", simulation_step_s)

        if self.fresh_gas_flow_l_min == 0.0:
            return FreshGasExchange(delivered_agent_l=0.0, exhausted_agent_l=0.0)

        initial_fraction = self.circuit_concentration_fraction
        delivered_fraction = self.delivered_concentration_fraction
        fraction_remaining = exp(-simulation_step_s / self.time_constant_s)

        next_fraction = (
            delivered_fraction + (initial_fraction - delivered_fraction) * fraction_remaining
        )

        fresh_gas_flow_l_s = self.fresh_gas_flow_l_min / SECONDS_PER_MINUTE

        delivered_agent_l = fresh_gas_flow_l_s * delivered_fraction * simulation_step_s

        integrated_circuit_fraction_s = delivered_fraction * simulation_step_s + (
            initial_fraction - delivered_fraction
        ) * self.time_constant_s * (1.0 - fraction_remaining)

        exhausted_agent_l = fresh_gas_flow_l_s * integrated_circuit_fraction_s

        self.circuit_concentration_fraction = next_fraction

        return FreshGasExchange(
            delivered_agent_l=delivered_agent_l, exhausted_agent_l=exhausted_agent_l
        )

    def advance(self, simulation_step_s: float) -> None:
        """Preserve the original v0.0.2 circuit interface."""

        self.advance_fresh_gas(simulation_step_s)

    def reset(self) -> None:
        """Clear circuit agent while preserving settings."""

        self.circuit_concentration_fraction = 0.0
