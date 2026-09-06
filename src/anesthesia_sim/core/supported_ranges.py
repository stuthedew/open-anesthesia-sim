"""The closed intervals the shipped model is supported over, and the guards
that refuse a setting outside them.

`docs/MODEL.md` § "Supported input ranges" is the specification; this module
is where the numbers live, so that every path that can change a setting -
core, controller, interface, notebook, test - is bounded by the same guard
instead of relying on the interface's sliders to stay inside the domain.

**Why the model declares these and not the interface.** The sliders' maxima
look like presentation choices, and they were: until this module existed the
only statement of the supported range was `app/simulation_view.py`, and
`AgentUptakeSystem.set_cardiac_output(1000.0)` was accepted and simulated.

What makes them the model's own is **physiological applicability, not
numerical error** (`PL-X9KD`). The previous statement here was that the shipped
operator split's first-order coefficient grew with the flows, so far enough
outside these intervals a displayed number was wrong by a margin the interface
could not show. That method is retired: the exact propagator solves the
governing equations at any flows whatever, so a cardiac output of 1000 L/min
now yields an *arithmetically correct* answer. It is a correct answer to a
question physiology does not ask. These intervals are the range over which the
lumped three-group compartment structure, the reference adult's fixed
volumes and the constant-coefficient partition model are claimed to represent a
patient at all; outside them the equations still solve and their solution
stands for nothing. `docs/MODEL.md` § "Supported input ranges" argues each
interval.

That the reference gates are driven at this envelope's corner is a consequence
of declaring it, not evidence for it: the trajectories are built from these
constants, so they would follow the interval wherever it was put.

**Refused, not clamped**, for the reason `BreathingCircuit` gives for the
vaporizer maximum it enforces the same way: a silently clamped setting would
simulate, display, and chart a value the caller did not ask for.

The fourth control, delivered concentration, is bounded here only by the
0-to-1 fraction every concentration obeys; its real limit is the vaporizer's
calibrated maximum, which is agent-specific and therefore lives on
`BreathingCircuit` as instance state rather than as a constant here.

Widening any interval is a safety-critical change and not a convenience, but
the work it now takes is different: argue that the compartment structure still
represents a patient over the wider range, re-run the reference gates at the
new corner, and revise `docs/MODEL.md` §§ "Supported input ranges" and
"Independent-solution test" together. What it no longer implies is a
re-derivation of the displayed resolution or of the supported simulation step.
Those two used to hang off the splitting coefficient measured here, and that
chain is cut: neither is derived from anything measured over this envelope.
"""

from math import isfinite

from anesthesia_sim.core.exceptions import SimulationConfigurationError

# Fresh gas flow into the breathing circuit.
MINIMUM_FRESH_GAS_FLOW_L_MIN = 0.0
MAXIMUM_FRESH_GAS_FLOW_L_MIN = 10.0

# Alveolar (not minute) ventilation.
MINIMUM_ALVEOLAR_VENTILATION_L_MIN = 0.0
MAXIMUM_ALVEOLAR_VENTILATION_L_MIN = 12.0

# Cardiac output, which is also every tissue's and the venous compartment's
# blood flow through their perfusion fractions.
MINIMUM_CARDIAC_OUTPUT_L_MIN = 0.0
MAXIMUM_CARDIAC_OUTPUT_L_MIN = 10.0

# Every floor is zero, and each is named separately because each is a separate
# decision that could change on its own: flooring cardiac output above zero
# would not imply flooring ventilation. Zero is supported on all three because
# each names a real clinical state the simulator exists to teach - apnoea,
# circulatory arrest, the fresh gas turned off - and `docs/MODEL.md` §
# "Supported input ranges" argues each (PL-629Z).
#
# The reason previously given here was different and is retired with the
# operator split (`PL-X9KD`): that the splitting coefficient's worst case was
# measured on a zero-cardiac-output trajectory, so raising the floor would take
# the bound's worst case out of its own domain. There is no such coefficient
# now, and the gate trajectory that measures worst is the ventilator start,
# which needs no zero-perfusion phase.


def _require_supported(name: str, value: float, minimum: float, maximum: float) -> None:
    """Require a finite value inside one control's closed supported interval.

    One check rather than a finiteness guard followed by a range guard, so
    that every rejection - negative, NaN, infinite, or merely too large -
    carries the same message naming the interval the caller has to return to.
    """

    if not isfinite(value) or not minimum <= value <= maximum:
        raise SimulationConfigurationError(
            f"{name} of {value} is outside the supported input range of "
            f"{minimum} to {maximum} L/min, which is the domain this "
            f"compartment model is claimed to represent a patient over "
            f'(docs/MODEL.md, "Supported input ranges")'
        )


def require_supported_fresh_gas_flow(fresh_gas_flow_l_min: float) -> None:
    """Require a fresh gas flow the model has a measured error bound for."""

    _require_supported(
        "fresh_gas_flow_l_min",
        fresh_gas_flow_l_min,
        MINIMUM_FRESH_GAS_FLOW_L_MIN,
        MAXIMUM_FRESH_GAS_FLOW_L_MIN,
    )


def require_supported_alveolar_ventilation(alveolar_ventilation_l_min: float) -> None:
    """Require an alveolar ventilation the model has a measured bound for."""

    _require_supported(
        "alveolar_ventilation_l_min",
        alveolar_ventilation_l_min,
        MINIMUM_ALVEOLAR_VENTILATION_L_MIN,
        MAXIMUM_ALVEOLAR_VENTILATION_L_MIN,
    )


def require_supported_cardiac_output(cardiac_output_l_min: float) -> None:
    """Require a cardiac output the model has a measured error bound for."""

    _require_supported(
        "cardiac_output_l_min",
        cardiac_output_l_min,
        MINIMUM_CARDIAC_OUTPUT_L_MIN,
        MAXIMUM_CARDIAC_OUTPUT_L_MIN,
    )
