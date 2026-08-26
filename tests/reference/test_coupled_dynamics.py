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
from collections.abc import Callable
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
# is what keeps the restatement true: without it, raising a slider would
# silently shrink the domain this gate covers, which is the defect PL-042
# exists to fix.
MAX_FRESH_GAS_FLOW_L_MIN = 10.0
MAX_ALVEOLAR_VENTILATION_L_MIN = 12.0
MAX_CARDIAC_OUTPUT_L_MIN = 10.0


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


def _default_operating_point() -> OperatingPoint:
    """The point the pinned reference states were computed at."""

    patient = load_reference_adult_parameters()

    return OperatingPoint(
        delivered_fraction=DELIVERED_FRACTION,
        fresh_gas_flow_l_min=FRESH_GAS_FLOW_L_MIN,
        alveolar_ventilation_l_min=patient.default_alveolar_ventilation_l_min,
        cardiac_output_l_min=patient.default_cardiac_output_l_min,
    )


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
        delivered_fraction=load_agent_parameters(agent_id).max_delivered_concentration_percent
        / 100.0,
        fresh_gas_flow_l_min=MAX_FRESH_GAS_FLOW_L_MIN,
        alveolar_ventilation_l_min=MAX_ALVEOLAR_VENTILATION_L_MIN,
        cardiac_output_l_min=MAX_CARDIAC_OUTPUT_L_MIN,
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
# The measured worst over the whole settings envelope is 1.21e-3 s^-1
# (desflurane, an 18% dial with all three flow sliders at maximum, mixed
# venous at about 85 s). This bound allows 1.24 times that.
#
# The margin is deliberately narrow, and narrower than the factor of two an
# earlier revision of this bound used, because the two things a wider margin
# would buy are both already covered:
#
#   - Parameter revision does not need headroom here. Any change to an agent
#     or patient parameter moves the reference solution and fails
#     `test_independent_solution_matches_pinned_reference_states`, which
#     already forces the re-derivation and review a revision should have.
#   - Envelope variation does not need headroom either, now that the bound
#     follows a measurement over the envelope rather than over one operating
#     point. That gap is what made the previous bound wrong: set from one
#     point at 2.5e-4, it was exceeded by a factor of about 2.4 at settings
#     three sliders could reach, and never failed because nothing ran there.
#
# What the margin does cover is float and platform variation, and a
# composition change that stays first order. Keeping it narrow also keeps the
# gate honest about displayed precision: at the shipped 0.1 s step this bound
# is 1.5e-4 in fraction, i.e. 0.015 percentage points, against a displayed
# resolution of 0.01. `docs/MODEL.md` § "Displayed precision" states that the
# last displayed digit is uncertain by about one count at the corner of the
# envelope; a much wider gate would let that claim quietly become false while
# still passing.
#
# `test_shipped_split_error_is_first_order_in_step` is what keeps the bound
# meaningful: it confirms the error really does scale as C·Δt, so bounding C
# at one step size bounds it at every supported step size.
SPLITTING_ERROR_BOUND_PER_STEP_SECOND = 1.5e-3

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


def _shipped_system(agent_id: str, point: OperatingPoint) -> RespiratorySystem:
    """The implementation under test, configured at one operating point."""

    system = RespiratorySystem.for_agent(agent_id)
    system.circuit.set_circuit_volume(CIRCUIT_VOLUME_L)
    system.set_fresh_gas_flow(point.fresh_gas_flow_l_min)
    system.set_alveolar_ventilation(point.alveolar_ventilation_l_min)
    system.set_cardiac_output(point.cardiac_output_l_min)
    system.set_delivered_concentration(point.delivered_fraction)

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


def _worst_coefficient_over_run(
    agent_id: str, duration_s: float, point: OperatingPoint
) -> tuple[float, float, str]:
    """Return the largest splitting coefficient anywhere in the trajectory.

    Sampling endpoints is not enough here: the worst disagreement in the
    envelope occurs at about 85 s, in the wash-in transient, which no
    endpoint at 60 s, 600 s or 3600 s looks at. Stepping the two solutions in
    lockstep and taking the maximum costs nothing extra — the RK4 integration
    is the expense and it happens either way — and bounds the coefficient
    over the whole run rather than at three instants.

    Returns (coefficient, simulated time of the worst, state label).
    """

    system = _shipped_system(agent_id, point)
    derivative = _build_derivative(agent_id, point)
    reference = [0.0] * 6
    oracle_steps_per_shipped_step = round(SHIPPED_STEP_S / ORACLE_STEP_S)

    worst_error = 0.0
    worst_time_s = 0.0
    worst_label = STATE_LABELS[0]

    for index in range(round(duration_s / SHIPPED_STEP_S)):
        system.advance(SHIPPED_STEP_S)

        for _ in range(oracle_steps_per_shipped_step):
            reference = _rk4_step(derivative, reference, ORACLE_STEP_S)

        error, label = _worst_state_error(_shipped_states(system), tuple(reference))

        if error > worst_error:
            worst_error = error
            worst_time_s = (index + 1) * SHIPPED_STEP_S
            worst_label = label

    return worst_error / SHIPPED_STEP_S, worst_time_s, worst_label


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

    coefficient, at_s, state_label = _worst_coefficient_over_run(
        agent_id, ENVELOPE_HORIZON_S, _envelope_corner(agent_id)
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


def test_envelope_limits_match_the_interface() -> None:
    """The restated slider maxima are still the interface's own.

    Without this, raising a slider would silently shrink the domain the gate
    covers and nothing would fail — which is exactly how the bound came to be
    narrower than the reachable settings in the first place.
    """

    from anesthesia_sim.app import simulation_view

    assert (MAX_FRESH_GAS_FLOW_L_MIN, MAX_ALVEOLAR_VENTILATION_L_MIN, MAX_CARDIAC_OUTPUT_L_MIN) == (
        simulation_view.MAX_FRESH_GAS_FLOW_L_MIN,
        simulation_view.MAX_ALVEOLAR_VENTILATION_L_MIN,
        simulation_view.MAX_CARDIAC_OUTPUT_L_MIN,
    ), (
        "the interface's slider limits have changed; re-run the envelope "
        "sweep, update these constants and the bound, and re-derive the "
        "measured figures in docs/MODEL.md"
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_shipped_split_error_is_first_order_in_step(agent_id: str) -> None:
    """Halving the step halves the error, as a first-order split requires.

    Without this, the bound in the test above would constrain the error at
    one step size only. With it, the bound is a statement about the
    coefficient C in C·Δt, and therefore about every supported step size.
    """

    duration_s = 600.0
    point = _default_operating_point()
    reference = _reference_state(agent_id, duration_s, point)
    errors = [
        _worst_state_error(_run_shipped(agent_id, duration_s, step_s, point), reference)[0]
        for step_s in (0.1, 0.05, 0.025)
    ]

    if max(errors) < EXACT_SOLUTION_FLOOR:
        # The composition has been replaced by something exact for this
        # linear system (a matrix exponential, say). There is then no
        # first-order error left to measure, and no order to confirm.
        return

    ratios = [errors[index] / errors[index + 1] for index in range(len(errors) - 1)]

    assert all(1.9 < ratio < 2.1 for ratio in ratios), (
        f"{agent_id} splitting error does not halve with the step: errors "
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
