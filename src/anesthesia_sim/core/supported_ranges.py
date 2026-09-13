"""The closed intervals the shipped model is supported over, and the guards
that refuse a setting outside them.

Four of the five bound a *setting* and are checked when a caller changes it.
The fifth bounds the *run* - how much elapsed simulated time the model is
claimed to represent a patient over - and is checked as each step is taken,
because a run length is reached rather than set. It is otherwise the same
kind of statement as the four, and lives here for that reason.

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

The run-length bound is enforced on `SimulationState`, which is the only
object that knows how far a run has gone, rather than on a compartment: a
compartment advanced alone has no run length to be past the end of. It
refuses the step that would cross the boundary rather than raising after
crossing it, so a run that stops here stands on a completed step at a
simulated time inside the supported span.

Widening any interval is a safety-critical change and not a convenience, but
the work it now takes is different: argue that the compartment structure still
represents a patient over the wider range, re-run the reference gates at the
new corner, and revise `docs/MODEL.md` §§ "Supported input ranges" and
"Independent-solution test" together. What it no longer implies is a
re-derivation of the displayed resolution or of the supported simulation step.
Those two used to hang off the splitting coefficient measured here, and that
chain is cut: neither is derived from anything measured over this envelope.
"""

from math import floor, isfinite

from anesthesia_sim.core.exceptions import SimulationConfigurationError, SimulationDomainLimitError

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

# How long a run may be, as elapsed simulated time. Unlike the three above
# this bounds the *run* rather than a setting, and it is reached mid-run
# rather than refused at entry, so `require_supported_run_length` below
# refuses the step that would cross it instead of a value a caller passed.
#
# **It is a validity limit, and it was a memory one.** The 30-day figure it
# replaces was set on 2026-08-25 to size a concentration history that no
# longer exists, and carried forward as though it described the model. It did
# not: what bounds a run is the same question the three intervals above answer
# for the flows - how far the shipped structure and parameter set are claimed
# to represent a patient - and for elapsed time that is answered by what this
# model leaves out.
#
# **The omission that binds is metabolism**, which `docs/MODEL.md`
# § "Known limitations" records and § "Published wash-in and elimination validation test"
# already draws the consequence of: it rejects the Yasuda papers' own
# multi-day elimination curves as a comparison, because over days the missing
# metabolism is no longer negligible and neither is the fat group's flow,
# which the same document records as about twice the reachable resting
# measurement. Sevoflurane is the binding agent - 2% to 5% of the absorbed
# dose is metabolized, against far less for isoflurane and desflurane - and
# its metabolism starts immediately rather than late, fluoride and HFIP
# appearing in plasma within minutes of the start of administration. What
# makes omitting it safe over a case is that the same review finds metabolism
# "does not contribute to the termination of clinical drug effect": true while
# ventilation and perfusion dominate the trace, and progressively false once
# the only thing still moving is the slow tail this model gives no sink to.
#   Kharasch ED. Biotransformation of sevoflurane. Anesth Analg
#   1995;81(6 Suppl):S27-38. PMID 7486145,
#   doi:10.1097/00000539-199512001-00005.
# A review, so tier 2 under `docs/MODEL.md` § "Source hierarchy" - cited for
# the magnitude and timing of the omission, never as the authority for a
# value. Nothing here is computed from it: 24 hours is a declared envelope
# argued against that omission, not a number derived from a metabolic rate.
#
# **Why 24 hours.** It clears every anesthetic this simulator exists to teach
# by a wide margin; it is about 0.6 of the fat group's roughly 42 h time
# constant, so the fat compartment is still visibly loading and the
# slow-compartment demonstration survives, where a cap of a few hours would
# truncate the one thing the fat trace exists to show; and it sits inside the
# regime the source above calls clinically negligible for metabolism, near the
# outer edge of the 0.35-to-9.5 MAC-hour exposure range over which that
# omission's size has been measured at all.
#
# **The fat time constant is a floor here, not a multiplier.** Many multiples
# of the slowest mode is the regime this project already declines to validate
# over, so a cap argued as "several fat time constants" would select for the
# part of the trace that is most nearly all omission. It bounds the cap from
# below - shorter than about one of them and the fat trace stops teaching -
# and says nothing about how far above it a run may go.
#
# **A declared envelope rather than a discovered cliff**, exactly as
# `docs/MODEL.md` § "What a setting outside the range costs" says of the three
# intervals above: nothing breaks at hour 25, and the equations solve as
# exactly there as anywhere. What stops at the boundary is the claim that the
# solution stands for a patient. Moving it is a safety-critical change and
# takes the same work: argue the wider span against what the model omits, and
# revise `docs/MODEL.md` § "Supported input ranges" with it.
#
# Volatile sedation in intensive care runs for days and is a real teaching
# target, and it is precisely the regime this model is wrong in. Reaching it
# is a model extension - metabolism first - and not a raise of this number.
MAXIMUM_ELAPSED_SIMULATION_TIME_S = 86_400.0

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


def maximum_step_count(simulation_step_s: float) -> int:
    """How many steps of this size fit inside the supported run length.

    Whole steps only, and the boundary is included: a run may complete
    exactly this many steps, and the last of them lands on
    `MAXIMUM_ELAPSED_SIMULATION_TIME_S` or the largest simulated time below
    it that a whole number of steps can reach. That matches the closed
    intervals the three flows above declare - an endpoint is supported, not
    the first refused value.

    **Derived once from the step rather than compared against a running
    total**, which is what makes the boundary reproducible. `docs/MODEL.md`
    § "Simulated time is a count of steps, not a running total" is the
    guarantee this rests on: elapsed time is one multiplication, so a run
    given identical inputs reaches this count at the same step on every
    machine. A halt decided by accumulating tenths of a second would land a
    step earlier or later depending on the order of the additions that got
    there, which would put the boundary a regression test pins in a
    different place per platform - and would break deterministic replay at
    exactly the point the test exists to hold.
    """

    return floor(MAXIMUM_ELAPSED_SIMULATION_TIME_S / simulation_step_s)


def require_supported_run_length(step_count: int, simulation_step_s: float) -> None:
    """Require room for one more step inside the supported run length.

    Refuses the step that would carry the run past
    `MAXIMUM_ELAPSED_SIMULATION_TIME_S`, leaving the run standing on the
    last simulated time the model is claimed to represent a patient at.

    `SimulationDomainLimitError` rather than `SimulationConfigurationError`:
    no value handed in is wrong and there is nothing for the caller to
    correct, so "fix it and carry on" is not available - the run has to
    stop. It is a `SimulationExecutionError` subclass for that reason, so a
    caller that knows only the base class stops the run, which is the safe
    default. A caller that catches this type specifically knows the run
    stopped because the model declined to extrapolate rather than because a
    step failed, and `docs/MODEL.md` § "Supported run length" requires that
    the two not be presented alike: nothing was miscalculated here, and
    every displayed value is a completed step's.
    """

    if step_count >= maximum_step_count(simulation_step_s):
        raise SimulationDomainLimitError(
            f"this run has reached {step_count * simulation_step_s:g} s of simulated time, "
            f"which is the supported run length of {MAXIMUM_ELAPSED_SIMULATION_TIME_S:g} s "
            f"({MAXIMUM_ELAPSED_SIMULATION_TIME_S / 3600:g} h); beyond it this model's "
            f"omitted metabolism and its fat perfusion dominate the trace, so it is not "
            f'claimed to represent a patient (docs/MODEL.md, "Supported run length")'
        )
