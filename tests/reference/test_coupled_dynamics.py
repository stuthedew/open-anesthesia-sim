"""Check the coupled six-state solution against an independent integration.

Mass balance cannot detect a wrong rate. Every internal transfer is applied
as an equal-and-opposite pair, so the accounting residual stays at ~2e-15 L
whatever the transfer rates are — including rates that move the alveolar
fraction by tenths of a percentage point. Conservation is necessary and
nowhere near sufficient, and this module is the check that closes the gap:
it re-derives the governing equations of `docs/MODEL.md` from the parameter
files, integrates them with a from-scratch fourth-order Runge–Kutta, and
requires the shipped operator split to agree with that solution.

The independence rule is what makes this verification rather than a
tautology, so `test_oracle_imports_no_solver_from_core` enforces it
mechanically rather than leaving it to review: the oracle below may import
the parameter loaders and nothing else from `anesthesia_sim`. Re-deriving an
equation from the specification is evidence; calling the implementation
under test and comparing it against itself is not.

Promoted from `tools/review-verification/verify_physics.py` (PL-023), where
the same oracle was written for the v0.2.0 architecture review but ran only
by hand.
"""

from __future__ import annotations

import ast
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import pytest

from anesthesia_sim.core.parameters import load_agent_parameters, load_reference_adult_parameters
from anesthesia_sim.core.respiratory_system import RespiratorySystem

SECONDS_PER_MINUTE = 60.0

AGENT_IDS = ("sevoflurane", "isoflurane", "desflurane")

# Simulated horizons, chosen for what each one exercises: 60 s is circuit
# and alveolar wash-in while the tissues are still empty, 600 s is the
# vessel-rich group approaching its own equilibrium, and 3600 s is far
# enough in for muscle and fat to carry a meaningful load.
HORIZONS_S = (60.0, 600.0, 3600.0)

# The historical operating point, kept because the pinned reference states
# below are its solution. 5% is the highest concentration all three shipped
# vaporizers can deliver (isoflurane's maximum), so one dial setting serves
# every agent.
DELIVERED_FRACTION = 0.05
FRESH_GAS_FLOW_L_MIN = 4.0
CIRCUIT_VOLUME_L = 6.0

# The interface's own slider limits, restated here rather than imported for
# the same reason as SHIPPED_STEP_S below — this reference test does not
# depend on the application layer. `test_envelope_limits_match_the_interface`
# is what keeps the restatement true: without it, moving a slider limit would
# silently shrink the domain this gate covers, which is the defect PL-042
# exists to fix.
#
# The floors matter as much as the maxima and are checked with them. The worst
# trajectory this gate drives reaches zero cardiac output, so flooring that
# slider above zero would take the bound's own worst case out of the reachable
# domain without failing anything. `docs/MODEL.md` § "Supported input ranges"
# records that zero is supported on all four controls, deliberately (PL-629Z).
MAX_FRESH_GAS_FLOW_L_MIN = 10.0
MAX_ALVEOLAR_VENTILATION_L_MIN = 12.0
MAX_CARDIAC_OUTPUT_L_MIN = 10.0
MIN_FRESH_GAS_FLOW_L_MIN = 0.0
MIN_ALVEOLAR_VENTILATION_L_MIN = 0.0
MIN_CARDIAC_OUTPUT_L_MIN = 0.0
MIN_DELIVERED_CONCENTRATION_PERCENT = 0.0


@dataclass(frozen=True)
class OperatingPoint:
    """A point in the space of settings the interface can produce.

    Frozen so it can key the reference-solution cache; the four fields are
    exactly the sliders that enter the governing equations. Circuit volume is
    not among them: it is a slider, but it scales the circuit equation alone
    and does not change the coupling between compartments, which is where the
    splitting error lives.
    """

    delivered_fraction: float
    fresh_gas_flow_l_min: float
    alveolar_ventilation_l_min: float
    cardiac_output_l_min: float


@dataclass(frozen=True)
class Phase:
    """One leg of a trajectory: settings held for a fixed duration.

    A run of the application is a sequence of these — the settings hold
    until someone moves a slider — so a gate driven by a phase list covers
    what the application actually produces, where one held `OperatingPoint`
    covers only the runs in which nothing is ever changed.
    """

    duration_s: float
    point: OperatingPoint


def _default_operating_point() -> OperatingPoint:
    """The point the pinned reference states were computed at."""

    patient = load_reference_adult_parameters()

    return OperatingPoint(
        delivered_fraction=DELIVERED_FRACTION,
        fresh_gas_flow_l_min=FRESH_GAS_FLOW_L_MIN,
        alveolar_ventilation_l_min=patient.default_alveolar_ventilation_l_min,
        cardiac_output_l_min=patient.default_cardiac_output_l_min,
    )


def _max_dial(agent_id: str) -> float:
    """The agent's own vaporizer maximum, as a fraction."""

    return load_agent_parameters(agent_id).max_delivered_concentration_percent / 100.0


def _envelope_corner(agent_id: str) -> OperatingPoint:
    """The corner of the settings envelope, where the split is worst.

    Established by sweeping all four axes rather than assumed: fresh gas flow
    and alveolar ventilation both increase the coefficient monotonically to
    their slider maxima; cardiac output has an interior *minimum* near
    5 L/min and rises toward both ends, with the upper end the larger; and the
    equations are linear in the delivered fraction, so the agent's own
    vaporizer maximum is its worst dial. The measurements are recorded in
    `docs/MODEL.md` § "Independent-solution test".

    Monotonicity is measured, not proved. A change to the governing equations
    could move the maximum off this corner, which is why the sweep is worth
    re-running rather than trusting when the model changes.
    """

    return OperatingPoint(
        delivered_fraction=_max_dial(agent_id),
        fresh_gas_flow_l_min=MAX_FRESH_GAS_FLOW_L_MIN,
        alveolar_ventilation_l_min=MAX_ALVEOLAR_VENTILATION_L_MIN,
        cardiac_output_l_min=MAX_CARDIAC_OUTPUT_L_MIN,
    )


def _ventilator_start(agent_id: str) -> tuple[Phase, ...]:
    """Prime the circuit with the ventilator off, then start ventilating.

    A manoeuvre the interface offers and a user performs: the vaporizer is
    open and fresh gas is running while alveolar ventilation is still zero,
    so the circuit fills to the dial setting against lungs that cannot take
    any of it. Starting ventilation then presents the largest circuit-to-
    alveolar gradient the machine can produce, at the largest ventilation it
    can produce.

    Five minutes is far longer than the circuit needs: at 10 L/min into 6 L
    its time constant is 36 s, so the first phase ends saturated and the
    scenario does not depend on exactly how long it ran.
    """

    return (
        Phase(
            300.0,
            OperatingPoint(
                _max_dial(agent_id),
                MAX_FRESH_GAS_FLOW_L_MIN,
                MIN_ALVEOLAR_VENTILATION_L_MIN,
                MAX_CARDIAC_OUTPUT_L_MIN,
            ),
        ),
        Phase(
            300.0,
            OperatingPoint(
                _max_dial(agent_id),
                MAX_FRESH_GAS_FLOW_L_MIN,
                MAX_ALVEOLAR_VENTILATION_L_MIN,
                MAX_CARDIAC_OUTPUT_L_MIN,
            ),
        ),
    )


def _unperfused_load_then_dial_off(agent_id: str) -> tuple[Phase, ...]:
    """Fill circuit and lungs with no circulation, then restore it and dial off.

    This is the worst trajectory the four sliders can produce, and it is worst
    for a reason that is structural rather than clinical: holding cardiac
    output at zero lets circuit and alveoli saturate at the dial setting while
    every blood and tissue compartment stays empty, which is the furthest apart
    the six states can be driven. Turning perfusion on and the vaporizer off in
    the same move then makes every compartment's equilibrium the opposite of
    where it sits, so all six transients run at once and the split is under the
    most strain it can be put under.

    Zero cardiac output is a supported input, decided and recorded rather than
    inherited: `docs/MODEL.md` § "Supported input ranges" gives the reasons,
    of which the operative one is that reducing cardiac output accelerates
    alveolar wash-in and zero is that lesson's clearest case. So this
    trajectory is inside the domain the gate must cover, not an edge case
    tolerated at its boundary.

    The gate does not rest on it alone even so: `_ventilator_start` above
    reaches 1.52e-3 s^-1 without it, two thirds of this scenario's 2.29e-3
    s^-1, so a later decision to floor the slider would leave a gate that
    still means something while the bound was re-measured.

    Ten minutes of loading is enough to saturate: extending it to twenty
    changes the measured coefficient by 4e-5 relative.
    """

    return (
        Phase(
            600.0,
            OperatingPoint(
                _max_dial(agent_id),
                MAX_FRESH_GAS_FLOW_L_MIN,
                MAX_ALVEOLAR_VENTILATION_L_MIN,
                MIN_CARDIAC_OUTPUT_L_MIN,
            ),
        ),
        Phase(
            300.0,
            OperatingPoint(
                MIN_DELIVERED_CONCENTRATION_PERCENT / 100.0,
                MAX_FRESH_GAS_FLOW_L_MIN,
                MAX_ALVEOLAR_VENTILATION_L_MIN,
                MAX_CARDIAC_OUTPUT_L_MIN,
            ),
        ),
    )


def _held_default_settings(agent_id: str) -> tuple[Phase, ...]:
    """The reference point, held for the whole run: a trajectory that never turns."""

    del agent_id  # the reference point is the same for every agent

    return (Phase(ENVELOPE_HORIZON_S, _default_operating_point()),)


# The trajectories the gate drives, found by sweeping the corners of both
# phases' settings and then each axis separately around the winner. What the
# sweep showed, and why these two are the ones kept:
#
#   - The worst is always the first transition after the loading phase
#     saturates. Repeating the cycle three or six times does not raise the
#     peak at all, and shortening the phases lowers it, so the coefficient is
#     bounded rather than accumulating over a run.
#   - Inserting a third phase between the two never beat the pair; the best
#     middle phases were the ones that simply held the loading corner longer.
#   - Every axis is monotone toward the corner used, except cardiac output in
#     the loading phase, which is worst at zero — the opposite end from the
#     constant-setting corner, where it is worst at the maximum.
#
# Monotonicity is measured, not proved, so a change to the governing
# equations could move the maximum off these trajectories and the sweep is
# worth re-running rather than trusting.
SETTING_CHANGE_SCENARIOS = (
    ("ventilator start", _ventilator_start),
    ("unperfused load then dial off", _unperfused_load_then_dial_off),
)


# Long enough to contain the worst disagreement anywhere in the envelope: at
# the corner it occurs at about 85 s, during the wash-in transient, and the
# measured coefficient is unchanged whether the run stops at 600 s, 1800 s or
# 3600 s. The envelope gate therefore runs to 600 s and takes the maximum over
# the whole trajectory rather than sampling endpoints.
ENVELOPE_HORIZON_S = 600.0

# The step the interface runs at (`app.simulation_view.SIMULATION_STEP_S`),
# restated rather than imported so that this reference test stays
# independent of the application layer.
SHIPPED_STEP_S = 0.1

# The oracle's own step. RK4 is fourth order and this system is smooth and
# slow, so its truncation error here is already at the double-precision
# floor: measured against an RK4 run at 0.005 s, a 0.05 s run differs by
# 2.6e-16 across all six states, which is ten orders of magnitude below the
# splitting error under test. Deliberately not 0.1 s, so that agreement can
# never be an artifact of the two solvers sharing a step size.
ORACLE_STEP_S = 0.05

# The tolerance is a bound on the first-order splitting coefficient rather
# than a number fitted to today's run: `docs/MODEL.md` documents the shipped
# composition as a first-order (Lie/Godunov) split, so its error scales as
# C·Δt, and the gate bounds C.
#
# The measured worst over the whole reachable domain is 2.29e-3 s^-1
# (desflurane, in the alveolar fraction about 13 s after a setting change;
# see `_unperfused_load_then_dial_off`). This bound allows 1.22 times that.
#
# The domain is *trajectories*, not operating points, and that is what the
# previous bound got wrong. Held settings measure the split only where it
# never turns; the four sliders turn, and turning one is what puts the split
# under strain, because a setting change leaves the state far from the
# equilibrium of the settings now in force. Driving the same envelope corner
# through a setting change is 1.9 times worse than holding it — 2.29e-3
# against 1.21e-3 — and an ordinary ventilator start at the corner already
# reaches 1.52e-3, above the 1.5e-3 this bound replaces. That gate never
# failed only because no run it drove ever changed a setting.
#
# The margin is deliberately narrow, and narrower than the factor of two an
# earlier revision of this bound used, because the two things a wider margin
# would buy are both already covered:
#
#   - Parameter revision does not need headroom here. Any change to an agent
#     or patient parameter moves the reference solution and fails
#     `test_independent_solution_matches_pinned_reference_states`, which
#     already forces the re-derivation and review a revision should have.
#   - Domain variation does not need headroom either, now that the bound
#     follows a measurement over the settings envelope *and* over setting
#     changes rather than over one held operating point.
#
# What the margin does cover is float and platform variation, and a
# composition change that stays first order. Keeping it narrow also keeps the
# gate honest about displayed precision: at the shipped 0.1 s step this bound
# is 2.8e-4 in fraction, i.e. 0.028 percentage points, against a displayed
# resolution of 0.01. `docs/MODEL.md` § "Displayed precision" states that the
# last displayed digit is uncertain by about two counts at the worst reachable
# trajectory; a wider gate would let that claim quietly become false while
# still passing.
#
# `test_shipped_split_error_is_first_order_in_step` is what keeps the bound
# meaningful: it confirms the error really does scale as C·Δt — across a
# setting change as well as at held settings — so bounding C at one step size
# bounds it at every supported step size.
SPLITTING_ERROR_BOUND_PER_STEP_SECOND = 2.8e-3

# Below this the split would no longer be first order because it would no
# longer be a split — see `test_shipped_split_error_is_first_order_in_step`.
EXACT_SOLUTION_FLOOR = 1e-12

# Names this module is allowed to import from `anesthesia_sim`: the two
# parameter loaders the oracle needs, the system under test, and the view
# module whose slider limits define the envelope.
#
# `simulation_view` is on this list for one assertion — that the limits
# restated above are still the interface's — and the rule the list enforces
# is unaffected by it: what must never be imported is a solver, because
# comparing the implementation against itself proves nothing. A module of
# display constants is not that. The oracle itself
# (`_build_derivative`) still uses the parameter loaders alone.
ALLOWED_PACKAGE_IMPORTS = frozenset(
    {
        "load_agent_parameters",
        "load_reference_adult_parameters",
        "RespiratorySystem",
        "simulation_view",
    }
)

# State order for every vector in this module:
# (F_C circuit, F_A alveolar, F_v mixed venous, F_vrg, F_mus, F_fat).
STATE_LABELS = ("circuit", "alveolar", "mixed venous", "vessel rich", "muscle", "fat")

# The independent solution itself, pinned so that a later edit to the oracle
# or to a parameter file cannot quietly move the reference the shipped core
# is measured against. A failure here is not a failure of the core: it says
# the oracle or its inputs changed, and the new values must be re-derived
# and reviewed before they are pinned again.
PINNED_REFERENCE_STATES: dict[tuple[str, float], tuple[float, ...]] = {
    ("sevoflurane", 60.0): (
        2.012708952804e-02,
        8.338562820476e-03,
        6.195570404808e-04,
        1.235733944889e-03,
        2.709125178553e-05,
        1.453719164539e-06,
    ),
    ("sevoflurane", 600.0): (
        4.025760559915e-02,
        3.123874611989e-02,
        2.079197729425e-02,
        2.729299644645e-02,
        1.577328503137e-03,
        8.683198239241e-05,
    ),
    ("sevoflurane", 3600.0): (
        4.422039687838e-02,
        3.847294104360e-02,
        3.143196126019e-02,
        3.835681352007e-02,
        1.247902658888e-02,
        8.045341692331e-04,
    ),
    ("isoflurane", 60.0): (
        1.979275146964e-02,
        6.441936303286e-03,
        5.335500872761e-04,
        1.045457731264e-03,
        2.353350586342e-05,
        1.150313301100e-06,
    ),
    ("isoflurane", 600.0): (
        3.621765712693e-02,
        2.308068766848e-02,
        1.529469912545e-02,
        2.008177817553e-02,
        1.215446550205e-03,
        6.105232823475e-05,
    ),
    ("isoflurane", 3600.0): (
        4.060474208595e-02,
        3.125284339208e-02,
        2.551995533573e-02,
        3.110339539171e-02,
        1.033137432265e-02,
        6.121306232910e-04,
    ),
    ("desflurane", 60.0): (
        2.028550884796e-02,
        9.292959011639e-03,
        8.572600142666e-04,
        1.714238180046e-03,
        4.700857162940e-05,
        2.669526827988e-06,
    ),
    ("desflurane", 600.0): (
        4.319496696587e-02,
        3.708234760364e-02,
        2.635985307152e-02,
        3.427474978569e-02,
        2.972407088435e-03,
        1.757698256264e-04,
    ),
    ("desflurane", 3600.0): (
        4.644343377577e-02,
        4.291955929134e-02,
        3.625893454198e-02,
        4.282995338758e-02,
        2.018382284900e-02,
        1.530341647925e-03,
    ),
}

Derivative = Callable[[list[float]], list[float]]


def _build_derivative(agent_id: str, point: OperatingPoint) -> Derivative:
    """Build dy/dt for the `docs/MODEL.md` system, from the specification.

    Only the parameter loaders are reused. Every equation below is written
    out from `docs/MODEL.md` § "Governing equations" rather than called from
    the implementation under test, which is what makes agreement evidence.
    """

    agent = load_agent_parameters(agent_id)
    patient = load_reference_adult_parameters()
    blood_gas = agent.blood_gas_partition_coefficient

    tissues = (
        (
            patient.vessel_rich_volume_l,
            patient.vessel_rich_perfusion_fraction,
            agent.vessel_rich_tissue_gas_partition_coefficient / blood_gas,
        ),
        (
            patient.muscle_volume_l,
            patient.muscle_perfusion_fraction,
            agent.muscle_tissue_gas_partition_coefficient / blood_gas,
        ),
        (
            patient.fat_volume_l,
            patient.fat_perfusion_fraction,
            agent.fat_tissue_gas_partition_coefficient / blood_gas,
        ),
    )

    alveolar_volume_l = patient.alveolar_gas_volume_l
    venous_volume_l = patient.venous_blood_volume_l

    fresh_gas_l_s = point.fresh_gas_flow_l_min / SECONDS_PER_MINUTE
    ventilation_l_s = point.alveolar_ventilation_l_min / SECONDS_PER_MINUTE
    cardiac_output_l_s = point.cardiac_output_l_min / SECONDS_PER_MINUTE
    delivered_fraction = point.delivered_fraction

    def derivative(state: list[float]) -> list[float]:
        circuit, alveolar, venous = state[0], state[1], state[2]
        tissue_fractions = state[3:]

        # Circuit: fresh-gas exchange plus ventilatory exchange with alveoli.
        d_circuit = fresh_gas_l_s / CIRCUIT_VOLUME_L * (delivered_fraction - circuit) - (
            ventilation_l_s / CIRCUIT_VOLUME_L * (circuit - alveolar)
        )

        # Alveoli: ventilation in, pulmonary uptake out.
        d_alveolar = (
            ventilation_l_s * (circuit - alveolar)
            - cardiac_output_l_s * blood_gas * (alveolar - venous)
        ) / alveolar_volume_l

        # Tissues: perfusion-limited, driven by arterial (= alveolar).
        d_tissues: list[float] = []
        tissue_outflow = 0.0

        for (volume_l, perfusion, tissue_blood), fraction in zip(
            tissues, tissue_fractions, strict=True
        ):
            flow_l_s = cardiac_output_l_s * perfusion
            d_tissues.append(flow_l_s / (volume_l * tissue_blood) * (alveolar - fraction))
            tissue_outflow += flow_l_s * fraction

        # Venous pool: flow-weighted tissue return, mixed at cardiac output.
        d_venous = (tissue_outflow - cardiac_output_l_s * venous) / venous_volume_l

        return [d_circuit, d_alveolar, d_venous, *d_tissues]

    return derivative


def _rk4_step(derivative: Derivative, state: list[float], step_s: float) -> list[float]:
    """One step of classical fourth-order Runge-Kutta."""

    first = derivative(state)
    second = derivative([a + step_s / 2 * b for a, b in zip(state, first, strict=True)])
    third = derivative([a + step_s / 2 * b for a, b in zip(state, second, strict=True)])
    fourth = derivative([a + step_s * b for a, b in zip(state, third, strict=True)])

    return [
        a + step_s / 6 * (b + 2 * c + 2 * d + e)
        for a, b, c, d, e in zip(state, first, second, third, fourth, strict=True)
    ]


def _integrate_rk4(derivative: Derivative, duration_s: float, step_s: float) -> tuple[float, ...]:
    """Integrate from an empty system with classical fourth-order RK."""

    state = [0.0] * 6

    for _ in range(round(duration_s / step_s)):
        state = _rk4_step(derivative, state, step_s)

    return tuple(state)


@cache
def _reference_state(agent_id: str, duration_s: float, point: OperatingPoint) -> tuple[float, ...]:
    """Return the independent solution, computed once per (agent, horizon, point)."""

    return _integrate_rk4(_build_derivative(agent_id, point), duration_s, ORACLE_STEP_S)


def _empty_shipped_system(agent_id: str) -> RespiratorySystem:
    """The implementation under test, empty and at its own defaults."""

    system = RespiratorySystem.for_agent(agent_id)
    system.circuit.set_circuit_volume(CIRCUIT_VOLUME_L)

    return system


def _apply_operating_point(system: RespiratorySystem, point: OperatingPoint) -> None:
    """Move every slider to `point`, leaving compartment contents untouched.

    This is what the interface does when a slider moves mid-run, and it is
    the only thing that happens at a phase boundary: the settings change,
    the state does not.
    """

    system.set_fresh_gas_flow(point.fresh_gas_flow_l_min)
    system.set_alveolar_ventilation(point.alveolar_ventilation_l_min)
    system.set_cardiac_output(point.cardiac_output_l_min)
    system.set_delivered_concentration(point.delivered_fraction)


def _shipped_system(agent_id: str, point: OperatingPoint) -> RespiratorySystem:
    """The implementation under test, configured at one operating point."""

    system = _empty_shipped_system(agent_id)
    _apply_operating_point(system, point)

    return system


def _shipped_states(system: RespiratorySystem) -> tuple[float, ...]:
    """Read the six displayed states, in STATE_LABELS order."""

    patient = system.patient

    return (
        system.circuit.circuit_concentration_fraction,
        system.alveoli.concentration_fraction,
        patient.mixed_venous_fraction,
        patient.vessel_rich.partial_pressure_fraction,
        patient.muscle.partial_pressure_fraction,
        patient.fat.partial_pressure_fraction,
    )


def _run_shipped(
    agent_id: str, duration_s: float, step_s: float, point: OperatingPoint
) -> tuple[float, ...]:
    """Advance the implementation under test to the same simulated time."""

    system = _shipped_system(agent_id, point)

    for _ in range(round(duration_s / step_s)):
        system.advance(step_s)

    return _shipped_states(system)


def _oracle_step_for(shipped_step_s: float) -> float:
    """Half the step under test.

    Halving keeps the two solvers off a shared step size — agreement then
    cannot be an artifact of them taking the same stride — while leaving the
    oracle's own truncation error ten orders of magnitude below the splitting
    error being measured. At the shipped 0.1 s step this is `ORACLE_STEP_S`,
    so a trajectory driven here and a pinned reference state above are
    integrated identically.
    """

    return shipped_step_s / 2.0


def _worst_coefficient_over_phases(
    agent_id: str, phases: Sequence[Phase], shipped_step_s: float = SHIPPED_STEP_S
) -> tuple[float, float, str]:
    """Return the largest splitting coefficient anywhere in the trajectory.

    Both solutions are driven through the same phase list, and both apply a
    phase's settings at the same instant: the shipped system by the setters
    the interface calls, the oracle by rebuilding its derivative. What is
    compared is therefore the split alone, not two different piecewise
    schedules.

    Sampling endpoints is not enough here, and neither is one held setting.
    The worst disagreement is always inside a transient — at held settings it
    is the wash-in one, at about 85 s; across a setting change it is the one
    the change itself starts, about 13 s later. Stepping the two solutions in
    lockstep and taking the maximum costs nothing extra, since the RK4
    integration is the expense and it happens either way.

    Returns (coefficient, simulated time of the worst, state label).
    """

    system = _empty_shipped_system(agent_id)
    reference = [0.0] * 6
    oracle_step_s = _oracle_step_for(shipped_step_s)
    oracle_steps_per_shipped_step = round(shipped_step_s / oracle_step_s)

    worst_error = 0.0
    worst_time_s = 0.0
    worst_label = STATE_LABELS[0]
    step_index = 0

    for phase in phases:
        _apply_operating_point(system, phase.point)
        derivative = _build_derivative(agent_id, phase.point)

        for _ in range(round(phase.duration_s / shipped_step_s)):
            system.advance(shipped_step_s)

            for _ in range(oracle_steps_per_shipped_step):
                reference = _rk4_step(derivative, reference, oracle_step_s)

            step_index += 1
            error, label = _worst_state_error(_shipped_states(system), tuple(reference))

            if error > worst_error:
                worst_error = error
                worst_time_s = step_index * shipped_step_s
                worst_label = label

    return worst_error / shipped_step_s, worst_time_s, worst_label


def _worst_state_error(left: tuple[float, ...], right: tuple[float, ...]) -> tuple[float, str]:
    """Return the largest absolute difference and the state it is in."""

    differences = [abs(a - b) for a, b in zip(left, right, strict=True)]
    worst = max(differences)

    return worst, STATE_LABELS[differences.index(worst)]


@pytest.mark.parametrize(("agent_id", "duration_s"), sorted(PINNED_REFERENCE_STATES))
def test_independent_solution_matches_pinned_reference_states(
    agent_id: str, duration_s: float
) -> None:
    """The oracle and its parameter inputs are both unchanged.

    This is also what lets the splitting bound below keep a narrow margin:
    any parameter revision fails here first and must be re-derived and
    reviewed, so the bound does not have to leave room for one.
    """

    assert _reference_state(agent_id, duration_s, _default_operating_point()) == pytest.approx(
        PINNED_REFERENCE_STATES[(agent_id, duration_s)], rel=1e-9, abs=1e-15
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
@pytest.mark.parametrize("duration_s", HORIZONS_S)
def test_shipped_split_matches_independent_solution(agent_id: str, duration_s: float) -> None:
    """Every state the interface displays is within the splitting bound.

    This is the check mass balance cannot make: a wrong transfer rate leaves
    the accounting residual untouched but moves these six numbers.
    """

    point = _default_operating_point()
    error, state_label = _worst_state_error(
        _run_shipped(agent_id, duration_s, SHIPPED_STEP_S, point),
        _reference_state(agent_id, duration_s, point),
    )
    bound = SPLITTING_ERROR_BOUND_PER_STEP_SECOND * SHIPPED_STEP_S

    assert error <= bound, (
        f"{agent_id} at {duration_s:.0f} s diverges from the independent "
        f"solution by {error:.3e} in the {state_label} fraction, above the "
        f"first-order splitting bound of {bound:.3e} at Δt = {SHIPPED_STEP_S} s"
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_shipped_split_is_bounded_across_the_settings_envelope(agent_id: str) -> None:
    """The bound holds at the corner of the envelope, not just at defaults.

    This is the check PL-042 added, and the reason it exists is that the gate
    above is not one: it runs at a single operating point, and the split is
    about five times worse at settings three sliders can reach. A release
    gate narrower than the reachable input domain is a verification claim
    broader than its evidence.

    The maximum is taken over the whole trajectory rather than at the
    endpoint, because the worst disagreement is in the wash-in transient.
    """

    coefficient, at_s, state_label = _worst_coefficient_over_phases(
        agent_id, (Phase(ENVELOPE_HORIZON_S, _envelope_corner(agent_id)),)
    )

    assert coefficient <= SPLITTING_ERROR_BOUND_PER_STEP_SECOND, (
        f"{agent_id} at the envelope corner reaches a splitting coefficient "
        f"of {coefficient:.3e} s^-1 in the {state_label} fraction at "
        f"{at_s:.1f} s, above the bound of "
        f"{SPLITTING_ERROR_BOUND_PER_STEP_SECOND:.3e} s^-1. If this is a "
        f"deliberate change, docs/MODEL.md's 'Independent-solution test' and "
        f"'Displayed precision' sections both quote the measured value and "
        f"must be re-derived with it."
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
@pytest.mark.parametrize(
    ("scenario_name", "build_phases"),
    SETTING_CHANGE_SCENARIOS,
    ids=[name for name, _ in SETTING_CHANGE_SCENARIOS],
)
def test_shipped_split_is_bounded_across_setting_changes(
    agent_id: str, scenario_name: str, build_phases: Callable[[str], tuple[Phase, ...]]
) -> None:
    """The bound holds on trajectories that turn, not only on held settings.

    The two gates above each hold one `OperatingPoint` for a whole run, so
    between them they cover only the runs in which nobody ever moves a
    slider. That is not what the application produces: the settings are four
    sliders, and moving one is precisely when the split is under strain,
    because the state is then far from the equilibrium of the settings now in
    force. Measured across a setting change the coefficient is 1.9 times its
    held-setting worst, which is more than the margin the previous bound
    carried — the gate could not see the case it was built to catch.

    This is the settings-envelope check one dimension over: the envelope
    widened *where* the run sits, this widens *what the run does*.
    """

    coefficient, at_s, state_label = _worst_coefficient_over_phases(
        agent_id, build_phases(agent_id)
    )

    assert coefficient <= SPLITTING_ERROR_BOUND_PER_STEP_SECOND, (
        f"{agent_id} on the '{scenario_name}' trajectory reaches a splitting "
        f"coefficient of {coefficient:.3e} s^-1 in the {state_label} fraction "
        f"at {at_s:.1f} s, above the bound of "
        f"{SPLITTING_ERROR_BOUND_PER_STEP_SECOND:.3e} s^-1. If this is a "
        f"deliberate change, docs/MODEL.md's 'Independent-solution test' and "
        f"'Displayed precision' sections both quote the measured value and "
        f"must be re-derived with it."
    )


def test_lockstep_oracle_step_matches_the_pinned_one() -> None:
    """A trajectory and a pinned reference state are integrated identically.

    `_oracle_step_for` halves whatever step is under test, which at the
    shipped step is `ORACLE_STEP_S` — the step every pinned reference state
    was computed at. Letting the two drift apart would move what the gates
    below measure while leaving the pinned states untouched, so the
    coincidence is checked rather than described.
    """

    assert _oracle_step_for(SHIPPED_STEP_S) == ORACLE_STEP_S


def test_envelope_limits_match_the_interface() -> None:
    """The restated slider limits are still the interface's own, both ends.

    Without this, moving a slider limit would silently shrink the domain the
    gate covers and nothing would fail — which is exactly how the bound came
    to be narrower than the reachable settings in the first place.

    The floors are checked alongside the maxima because the worst trajectory
    the gate drives reaches zero cardiac output: flooring that slider above
    zero would remove the bound's own worst case from the reachable domain,
    which is the same defect at the other end of the axis.
    """

    from anesthesia_sim.app import simulation_view

    assert (
        MAX_FRESH_GAS_FLOW_L_MIN,
        MAX_ALVEOLAR_VENTILATION_L_MIN,
        MAX_CARDIAC_OUTPUT_L_MIN,
        MIN_FRESH_GAS_FLOW_L_MIN,
        MIN_ALVEOLAR_VENTILATION_L_MIN,
        MIN_CARDIAC_OUTPUT_L_MIN,
        MIN_DELIVERED_CONCENTRATION_PERCENT,
    ) == (
        simulation_view.MAX_FRESH_GAS_FLOW_L_MIN,
        simulation_view.MAX_ALVEOLAR_VENTILATION_L_MIN,
        simulation_view.MAX_CARDIAC_OUTPUT_L_MIN,
        simulation_view.MIN_FRESH_GAS_FLOW_L_MIN,
        simulation_view.MIN_ALVEOLAR_VENTILATION_L_MIN,
        simulation_view.MIN_CARDIAC_OUTPUT_L_MIN,
        simulation_view.MIN_DELIVERED_CONCENTRATION_PERCENT,
    ), (
        "the interface's slider limits have changed; re-run the envelope and "
        "trajectory sweeps, update these constants and the bound, and "
        "re-derive the measured figures in docs/MODEL.md"
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
@pytest.mark.parametrize(
    ("trajectory_name", "build_phases"),
    (("held settings", _held_default_settings), *SETTING_CHANGE_SCENARIOS),
    ids=["held settings", *(name for name, _ in SETTING_CHANGE_SCENARIOS)],
)
def test_shipped_split_error_is_first_order_in_step(
    agent_id: str, trajectory_name: str, build_phases: Callable[[str], tuple[Phase, ...]]
) -> None:
    """Halving the step halves the error, as a first-order split requires.

    Without this, the bounds above would constrain the error at one step size
    only. With it, each bound is a statement about the coefficient C in C·Δt,
    and therefore about every supported step size.

    A setting change is a discontinuity in the coefficients of the governing
    equations, which is the one thing that could plausibly cost the split its
    order — so the trajectories that turn are checked here as well as at held
    settings, and the coefficient measured across a change is flat to four
    figures from 0.025 s up to 1.6 s.
    """

    phases = build_phases(agent_id)
    # The driver reports C = error / Δt; the claim under test is about the
    # error itself, so multiply the step back in rather than restating the
    # ratio in terms of C.
    errors = [
        _worst_coefficient_over_phases(agent_id, phases, step_s)[0] * step_s
        for step_s in (0.1, 0.05, 0.025)
    ]

    if max(errors) < EXACT_SOLUTION_FLOOR:
        # The composition has been replaced by something exact for this
        # linear system (a matrix exponential, say). There is then no
        # first-order error left to measure, and no order to confirm.
        return

    ratios = [errors[index] / errors[index + 1] for index in range(len(errors) - 1)]

    assert all(1.9 < ratio < 2.1 for ratio in ratios), (
        f"{agent_id} splitting error on the '{trajectory_name}' trajectory "
        "does not halve with the step: errors "
        + ", ".join(f"{error:.3e}" for error in errors)
        + " give ratios "
        + ", ".join(f"{ratio:.3f}" for ratio in ratios)
    )


def test_oracle_imports_no_solver_from_core() -> None:
    """Keep this file a verification rather than a tautology.

    The oracle must re-derive the model from parameters alone. Importing any
    solver from `core/` — a compartment's exact update, the coupled step
    itself — would make this module compare the implementation against
    itself and pass no matter how wrong the dynamics were.
    """

    module = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported_names = {
        alias.name
        for node in ast.walk(module)
        if isinstance(node, ast.ImportFrom)
        if (node.module or "").startswith("anesthesia_sim")
        for alias in node.names
    }

    assert imported_names <= ALLOWED_PACKAGE_IMPORTS, (
        "this module imports "
        f"{sorted(imported_names - ALLOWED_PACKAGE_IMPORTS)} from the package "
        "under test; the independent solution may use the parameter loaders "
        "only"
    )
