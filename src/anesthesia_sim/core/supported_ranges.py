"""The closed intervals the shipped model is supported over, and the guards
that refuse a setting outside them.

`docs/MODEL.md` § "Supported input ranges" is the specification; this module
is where the numbers live, so that every path that can change a setting -
core, controller, interface, notebook, test - is bounded by the same guard
instead of relying on the interface's sliders to stay inside the domain.

**Why the model declares these and not the interface.** The sliders' maxima
look like presentation choices, and they were: until this module existed the
only statement of the supported range was `app/simulation_view.py`, and
`RespiratorySystem.set_cardiac_output(1000.0)` was accepted and simulated.
What makes them the model's own is that the shipped operator split is first
order, so its error is `C * dt` with the coefficient `C` measured over the
trajectories *these* ranges produce, and every claim `docs/MODEL.md` makes
about the last displayed digit is that error at the shipped 0.1 s step. `C`
grows with the flows, and roughly in proportion: on the worst trajectory the
four controls can reach, doubling all three flows doubles it, and cardiac
output alone at 1000 L/min multiplies it by 40 - which turns the displayed
resolution's "uncertain by about two counts" into 91 counts, an alveolar
readout wrong in its first decimal while presenting itself as settled. So
outside these intervals the number is not merely unverified; it is wrong by a
margin the interface cannot show. `docs/MODEL.md` § "Supported input ranges"
records the measurements.

**Refused, not clamped**, for the reason `BreathingCircuit` gives for the
vaporizer maximum it enforces the same way: a silently clamped setting would
simulate, display, and chart a value the caller did not ask for.

The fourth control, delivered concentration, is bounded here only by the
0-to-1 fraction every concentration obeys; its real limit is the vaporizer's
calibrated maximum, which is agent-specific and therefore lives on
`BreathingCircuit` as instance state rather than as a constant here.

Widening any interval is a safety-critical change and not a convenience:
re-measure the splitting coefficient over the new domain, re-derive the
displayed resolution and the supported simulation step from it, and revise
`docs/MODEL.md` §§ "Supported input ranges", "Independent-solution test",
"Supported simulation step" and "Displayed precision" together.
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
# would not imply flooring ventilation. They are load-bearing rather than
# incidental - the splitting coefficient's own worst case is measured on a
# trajectory that holds cardiac output at zero, so raising that floor would
# take the bound's worst case out of the domain it is measured over.
# `docs/MODEL.md` § "Supported input ranges" argues why zero is supported on
# all three (PL-629Z).


def _require_supported(name: str, value: float, minimum: float, maximum: float) -> None:
    """Require a finite value inside one control's closed supported interval.

    One check rather than a finiteness guard followed by a range guard, so
    that every rejection - negative, NaN, infinite, or merely too large -
    carries the same message naming the interval the caller has to return to.
    """

    if not isfinite(value) or not minimum <= value <= maximum:
        raise SimulationConfigurationError(
            f"{name} of {value} is outside the supported input range of "
            f"{minimum} to {maximum} L/min, which is the domain the model's "
            f"error bound is measured over (docs/MODEL.md, "
            f'"Supported input ranges")'
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
