"""Verify the shipped numerics against an independently written solution.

This script does not import any solver from `core/`. It re-derives the
governing equations of `docs/MODEL.md` from the loaded parameter files,
integrates them with a from-scratch RK4, and compares. It then builds a
from-scratch matrix exponential to show what the same system costs when
solved as one coupled whole rather than split into pairwise exchanges.

Nothing here is a fix. The RK4 oracle has since been promoted into
`tests/reference/test_coupled_dynamics.py` with pinned vectors, which is the
remedy for finding P2-1 (PL-023) and runs on every CI run. This script stays
as the exploratory version: it is where the matrix-exponential comparison
below lives, and it runs at horizons and step sizes that would be too slow
for the test suite.

Run:  uv run python tools/review-verification/verify_physics.py
"""

from __future__ import annotations

import math
from collections.abc import Callable

from _report import CONFIRMED, REGRESSED, Report, main_guard

from anesthesia_sim.core.parameters import (
    load_agent_parameters,
    load_reference_adult_parameters,
)
from anesthesia_sim.core.respiratory_system import RespiratorySystem

SECONDS_PER_MINUTE = 60.0
AGENTS = ("sevoflurane", "isoflurane", "desflurane")

# The operating point every comparison below runs at. 5% is the highest
# concentration all three shipped vaporizers can deliver (isoflurane's
# maximum), so one operating point serves every agent; anything higher is
# now rejected by the core rather than simulated (PL-015). The governing
# equations are linear in the delivered fraction, so the level sets the
# scale of the reported errors, not the conclusions.
DELIVERED_FRACTION = 0.05

# RK4 is fourth order, so this lands ~1e-12 - four orders below the
# splitting error being measured, and 100x faster than a finer step.
REFERENCE_STEP_S = 0.01
FRESH_GAS_FLOW_L_MIN = 4.0
CIRCUIT_VOLUME_L = 6.0

Derivative = Callable[[list[float]], list[float]]


def build_derivative(agent_id: str) -> Derivative:
    """Build dy/dt for the MODEL.md system, independent of `core/` solvers.

    State order is (F_C, F_A, F_v, F_vrg, F_mus, F_fat). Only the parameter
    loaders are reused; every equation below is written out from the
    specification rather than called from the implementation under test.
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

    fresh_gas_l_s = FRESH_GAS_FLOW_L_MIN / SECONDS_PER_MINUTE
    ventilation_l_s = patient.default_alveolar_ventilation_l_min / SECONDS_PER_MINUTE
    cardiac_output_l_s = patient.default_cardiac_output_l_min / SECONDS_PER_MINUTE

    def derivative(y: list[float]) -> list[float]:
        circuit, alveolar, venous = y[0], y[1], y[2]
        tissue_fractions = y[3:]

        # Circuit: fresh-gas exchange plus ventilatory exchange with alveoli.
        d_circuit = fresh_gas_l_s / CIRCUIT_VOLUME_L * (DELIVERED_FRACTION - circuit) - (
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


def rk4(derivative: Derivative, duration_s: float, step_s: float) -> list[float]:
    """Integrate from an empty system with classical fourth-order RK."""

    y = [0.0] * 6

    for _ in range(round(duration_s / step_s)):
        k1 = derivative(y)
        k2 = derivative([a + step_s / 2 * b for a, b in zip(y, k1, strict=True)])
        k3 = derivative([a + step_s / 2 * b for a, b in zip(y, k2, strict=True)])
        k4 = derivative([a + step_s * b for a, b in zip(y, k3, strict=True)])
        y = [
            a + step_s / 6 * (b + 2 * c + 2 * d + e)
            for a, b, c, d, e in zip(y, k1, k2, k3, k4, strict=True)
        ]

    return y


def run_shipped(agent_id: str, duration_s: float, step_s: float) -> list[float]:
    """Advance the implementation under test to the same simulated time."""

    system = RespiratorySystem.for_agent(agent_id)
    system.circuit.set_circuit_volume(CIRCUIT_VOLUME_L)
    system.set_fresh_gas_flow(FRESH_GAS_FLOW_L_MIN)
    system.set_delivered_concentration(DELIVERED_FRACTION)

    for _ in range(round(duration_s / step_s)):
        system.advance(step_s)

    patient = system.patient

    return [
        system.circuit.circuit_concentration_fraction,
        system.alveoli.concentration_fraction,
        patient.mixed_venous_fraction,
        patient.vessel_rich.partial_pressure_fraction,
        patient.muscle.partial_pressure_fraction,
        patient.fat.partial_pressure_fraction,
    ]


def max_error(left: list[float], right: list[float]) -> float:
    return max(abs(a - b) for a, b in zip(left, right, strict=True))


# --------------------------------------------------------------------------
# Matrix exponential of the same system, written from scratch.
# --------------------------------------------------------------------------

Matrix = list[list[float]]


def build_system_matrix(agent_id: str) -> Matrix:
    """Assemble the 7x7 augmented matrix A for dy/dt = Ay + b.

    The seventh row/column carries the constant fresh-gas forcing term, so
    the affine system becomes a single linear one and `exp(A*dt)` is its
    exact propagator.
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

    fresh_gas_l_s = FRESH_GAS_FLOW_L_MIN / SECONDS_PER_MINUTE
    ventilation_l_s = patient.default_alveolar_ventilation_l_min / SECONDS_PER_MINUTE
    cardiac_output_l_s = patient.default_cardiac_output_l_min / SECONDS_PER_MINUTE

    matrix: Matrix = [[0.0] * 7 for _ in range(7)]

    matrix[0][0] = -(fresh_gas_l_s + ventilation_l_s) / CIRCUIT_VOLUME_L
    matrix[0][1] = ventilation_l_s / CIRCUIT_VOLUME_L
    matrix[0][6] = fresh_gas_l_s * DELIVERED_FRACTION / CIRCUIT_VOLUME_L

    matrix[1][0] = ventilation_l_s / alveolar_volume_l
    matrix[1][1] = -(ventilation_l_s + cardiac_output_l_s * blood_gas) / alveolar_volume_l
    matrix[1][2] = cardiac_output_l_s * blood_gas / alveolar_volume_l

    matrix[2][2] = -cardiac_output_l_s / venous_volume_l

    for index, (volume_l, perfusion, tissue_blood) in enumerate(tissues):
        flow_l_s = cardiac_output_l_s * perfusion
        rate = flow_l_s / (volume_l * tissue_blood)
        matrix[3 + index][1] = rate
        matrix[3 + index][3 + index] = -rate
        matrix[2][3 + index] = flow_l_s / venous_volume_l

    return matrix


def multiply(left: Matrix, right: Matrix) -> Matrix:
    size = len(left)

    return [
        [sum(left[row][k] * right[k][col] for k in range(size)) for col in range(size)]
        for row in range(size)
    ]


def matrix_exponential(matrix: Matrix, step_s: float) -> Matrix:
    """exp(matrix * step_s) by scaling and squaring with a Taylor series."""

    size = len(matrix)
    norm = max(sum(abs(value) for value in row) for row in matrix) * step_s
    squarings = max(0, math.ceil(math.log2(norm)) + 4) if norm > 0 else 0
    scaled_step = step_s / (2**squarings)

    scaled = [[value * scaled_step for value in row] for row in matrix]
    result: Matrix = [[float(row == col) for col in range(size)] for row in range(size)]
    term = [row[:] for row in result]

    for order in range(1, 25):
        term = multiply(term, scaled)
        term = [[value / order for value in row] for row in term]
        result = [[result[row][col] + term[row][col] for col in range(size)] for row in range(size)]

    for _ in range(squarings):
        result = multiply(result, result)

    return result


def propagate(propagator: Matrix, state: list[float]) -> list[float]:
    return [sum(propagator[row][col] * state[col] for col in range(7)) for row in range(7)]


# --------------------------------------------------------------------------


def main() -> int:
    report = Report("Physics verification - independent solutions vs. the shipped core")
    report.start()

    # --- 1. Does the shipped split reproduce the documented equations? ---
    worst_error = 0.0
    worst_where = ""

    for agent_id in AGENTS:
        derivative = build_derivative(agent_id)

        for duration_s in (60.0, 600.0, 3600.0):
            reference = rk4(derivative, duration_s, REFERENCE_STEP_S)
            shipped = run_shipped(agent_id, duration_s, 0.1)
            error = max_error(shipped, reference)

            if error > worst_error:
                worst_error = error
                worst_where = f"{agent_id} at {duration_s:.0f} s"

    report.record(
        "P2-2",
        "shipped split reproduces the MODEL.md equations",
        CONFIRMED if worst_error < 1e-4 else REGRESSED,
        f"worst max-abs error {worst_error:.3e} ({worst_where}), tolerance 1e-04",
    )

    # --- 2. Is the convergence order actually first, as documented? ---
    derivative = build_derivative("sevoflurane")
    reference = rk4(derivative, 600.0, REFERENCE_STEP_S)
    errors = [
        max_error(run_shipped("sevoflurane", 600.0, step_s), reference)
        for step_s in (0.1, 0.05, 0.025, 0.0125)
    ]
    ratios = [errors[i] / errors[i + 1] for i in range(len(errors) - 1)]
    first_order = all(1.9 < ratio < 2.1 for ratio in ratios)

    report.record(
        "P2-3",
        "splitting error is first order (halving dt halves error)",
        CONFIRMED if first_order else REGRESSED,
        "errors " + ", ".join(f"{e:.2e}" for e in errors) + "\n"
        "ratios " + ", ".join(f"{r:.3f}" for r in ratios),
    )

    # --- 3. What would solving the whole system at once cost instead? ---
    report.note("")
    report.note("Architecture evidence - one matrix exponential vs. the pairwise split:")
    report.note("")
    report.note(f"{'agent':<14}{'horizon':>9}{'expm':>13}{'split':>13}{'ratio':>11}")

    exact_enough = True

    for agent_id in AGENTS:
        matrix = build_system_matrix(agent_id)

        for duration_s in (60.0, 3600.0):
            exact = propagate(matrix_exponential(matrix, duration_s), [0.0] * 6 + [1.0])[:6]

            propagator = matrix_exponential(matrix, 0.1)
            state = [0.0] * 6 + [1.0]

            for _ in range(round(duration_s / 0.1)):
                state = propagate(propagator, state)

            expm_error = max_error(state[:6], exact)
            split_error = max_error(run_shipped(agent_id, duration_s, 0.1), exact)
            exact_enough = exact_enough and expm_error < 1e-12

            report.note(
                f"{agent_id:<14}{duration_s:>8.0f}s{expm_error:>13.2e}"
                f"{split_error:>13.2e}{split_error / expm_error:>11.1e}"
            )

    report.note("")
    report.record(
        "ARCH",
        "system is linear, so expm is exact where splitting is not",
        CONFIRMED if exact_enough else REGRESSED,
        "expm stepping stays at machine precision; the split does not",
    )

    return report.finish()


if __name__ == "__main__":
    main_guard(main())
