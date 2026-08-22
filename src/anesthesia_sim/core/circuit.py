from dataclasses import dataclass
from math import exp, inf, isfinite

SECONDS_PER_MINUTE = 60.0


def _require_positive_finite(name: str, value: float) -> None:
    if not isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be positive and finite")


def _require_nonnegative_finite(name: str, value: float) -> None:
    if not isfinite(value) or value < 0:
        raise ValueError(f"{name} must be nonnegative and finite")


def _require_concentration_fraction(name: str, value: float) -> None:
    if not isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")


@dataclass(slots=True)
class BreathingCircuit:
    """Ideal, well-mixed breathing circuit with constant volume."""

    circuit_volume_l: float = 6.0
    fresh_gas_flow_l_min: float = 4.0
    delivered_concentration_fraction: float = 0.08
    circuit_concentration_fraction: float = 0.0

    def __post_init__(self) -> None:
        _require_positive_finite("circuit_volume_l", self.circuit_volume_l)
        _require_nonnegative_finite(
            "fresh_gas_flow_l_min",
            self.fresh_gas_flow_l_min,
        )
        _require_concentration_fraction(
            "delivered_concentration_fraction",
            self.delivered_concentration_fraction,
        )
        _require_concentration_fraction(
            "circuit_concentration_fraction",
            self.circuit_concentration_fraction,
        )

    @property
    def time_constant_s(self) -> float:
        """Return the circuit wash-in time constant in seconds."""

        if self.fresh_gas_flow_l_min == 0.0:
            return inf

        return SECONDS_PER_MINUTE * self.circuit_volume_l / self.fresh_gas_flow_l_min

    def set_circuit_volume(self, circuit_volume_l: float) -> None:
        _require_positive_finite("circuit_volume_l", circuit_volume_l)
        self.circuit_volume_l = circuit_volume_l

    def set_fresh_gas_flow(self, fresh_gas_flow_l_min: float) -> None:
        _require_nonnegative_finite(
            "fresh_gas_flow_l_min",
            fresh_gas_flow_l_min,
        )
        self.fresh_gas_flow_l_min = fresh_gas_flow_l_min

    def set_delivered_concentration(
        self,
        delivered_concentration_fraction: float,
    ) -> None:
        _require_concentration_fraction(
            "delivered_concentration_fraction",
            delivered_concentration_fraction,
        )
        self.delivered_concentration_fraction = delivered_concentration_fraction

    def advance(self, simulation_step_s: float) -> None:
        """Advance concentration exactly for constant inputs over one step."""

        _require_positive_finite("simulation_step_s", simulation_step_s)

        if self.fresh_gas_flow_l_min == 0.0:
            return

        fraction_remaining = exp(-simulation_step_s / self.time_constant_s)
        difference_from_delivered = (
            self.circuit_concentration_fraction - self.delivered_concentration_fraction
        )
        self.circuit_concentration_fraction = (
            self.delivered_concentration_fraction + difference_from_delivered * fraction_remaining
        )

    def reset(self) -> None:
        """Empty the modeled agent while preserving circuit settings."""

        self.circuit_concentration_fraction = 0.0
