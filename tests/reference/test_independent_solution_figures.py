"""The counts behind the independent-solution test's limits match `docs/VERIFICATION.md`.

`docs/VERIFICATION.md` § "Independent-solution test" argues that its two
limits, set when a run could take a step of 0.1 s, still cover a run in
one-second steps. The argument counts rounding as `run_rounding` in
`core/rounding.py` does: the number of steps times two raised to the number
of squarings that each step's matrix exponential needs. This module computes
those counts for the runs the comparison drives, and checks the figures that
the section prints from them. It also checks what the section says about the
random runs: how often their controls move, and that they reach each zero
setting.

Each test reads its figures from the section as printed, with a narrow
pattern for the sentence that states them, as
`tests/reference/test_supported_input_range_figures.py` does. So a change to
the model that moves a figure fails here, and so does an edit to the text
that changes a figure without changing what it was computed from.

The squarings are counted by `_squarings` in
`tests/unit/test_numerical_envelope.py`, which applies the rule that
`core/matrix_exponential.py` documents without calling that module's code.
The runs are the ones `tests/reference/test_coupled_dynamics.py` drives.
"""

import sys
from functools import cache
from pathlib import Path

import pytest

from anesthesia_sim.core.governing_equations import build_system_matrix
from anesthesia_sim.core.rounding import run_rounding
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import StepCount

# The squaring counter lives with the unit test that first needed it. Its
# directory is put on the path, as pytest does when it collects that
# directory, so both tests use the one function.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "unit"))

from test_coupled_dynamics import (
    AGENT_IDS,
    ALL_GATE_TRAJECTORIES,
    HORIZONS_S,
    MIN_ALVEOLAR_VENTILATION_L_MIN,
    MIN_CARDIAC_OUTPUT_L_MIN,
    MIN_FRESH_GAS_FLOW_L_MIN,
    RANDOMISED_PHASE_MAX_STEPS,
    RANDOMISED_TRAJECTORY_SEEDS,
    Phase,
    _default_operating_point,
    _envelope_corner_held,
    _randomised_trajectory,
    _shipped_system,
    _unperfused_load_then_dial_off,
    _ventilator_start,
)
from test_numerical_envelope import _squarings
from test_supported_input_range_figures import DOCS, _one, _section

#: The step that a run could take before the step was fixed at one second, in
#: seconds. The limits were set from runs at this step and two finer ones.
EARLIER_STEP_S = 0.1


@cache
def _section_text() -> str:
    return _section(DOCS / "VERIFICATION.md", "### Independent-solution test")


def _printed(pattern: str) -> tuple[str, ...]:
    """The figures of the one sentence in the section that `pattern` matches."""

    return _one(pattern, _section_text())


def _count(printed: str) -> int:
    """A count as the section prints it, with a space between groups of three digits."""

    return int(printed.replace(" ", ""))


def _phase_squarings(agent_id: str, phase: Phase, step_s: float) -> int:
    """The squarings that one step of `phase` needs at a step of `step_s` seconds."""

    settings = _shipped_system(agent_id, phase.point).equation_settings()

    return _squarings(build_system_matrix(settings), step_s)


def _rounding_count(agent_id: str, phases: tuple[Phase, ...], step_s: float) -> int:
    """Steps times two raised to their squarings, summed over a run, as `run_rounding` counts."""

    steps_per_second = round(1 / step_s)

    return sum(
        phase.duration_s * steps_per_second * 2 ** _phase_squarings(agent_id, phase, step_s)
        for phase in phases
    )


@pytest.mark.parametrize("agent_id", AGENT_IDS)
@pytest.mark.parametrize(("label", "trajectory"), ALL_GATE_TRAJECTORIES)
def test_each_run_is_at_most_0_8_times_as_exposed_to_rounding_as_at_the_earlier_step(
    agent_id: str, label: str, trajectory
) -> None:
    """A one-second step needs two or three squarings and a 0.1 s step none, so at most 0.8.

    `docs/VERIFICATION.md` § "Independent-solution test" gives this as the
    reason that the spread measured at steps of 0.1, 0.05 and 0.025 s still
    covers a one-second run: each run's bound in one-second steps is at most
    0.8 times its bound in 0.1 s steps.
    """

    assert SIMULATION_STEP_S == 1
    phases = trajectory(agent_id)

    for phase in phases:
        assert _phase_squarings(agent_id, phase, SIMULATION_STEP_S) in (2, 3), (agent_id, label)
        assert _phase_squarings(agent_id, phase, EARLIER_STEP_S) == 0, (agent_id, label)

    one_second = _rounding_count(agent_id, phases, SIMULATION_STEP_S)
    earlier = _rounding_count(agent_id, phases, EARLIER_STEP_S)

    (ceiling,) = _printed(
        r"bound in one-second steps is at most (\d\.\d) times its bound in 0\.1 s steps"
    )

    assert one_second <= float(ceiling) * earlier, (agent_id, label, one_second, earlier)


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_the_envelope_corner_and_the_held_hour_count_the_rounding_printed(agent_id: str) -> None:
    """The envelope corner counts 4 800 against 6 000, and the held hour 14 400 against 36 000.

    `docs/VERIFICATION.md` gives both pairs, as the count at the one-second
    step against the count at 0.1 s.
    """

    corner = _envelope_corner_held(agent_id)
    hour = (Phase(max(HORIZONS_S), _default_operating_point()),)

    corner_counts = _printed(r"three squarings, (\d \d{3}) by that count, against (\d \d{3}) steps")
    hour_counts = _printed(
        r"steps count (\d+ \d{3}) by `run_rounding`'s count, against (\d+ \d{3})"
    )

    assert _rounding_count(agent_id, corner, SIMULATION_STEP_S) == _count(corner_counts[0])
    assert _rounding_count(agent_id, corner, EARLIER_STEP_S) == _count(corner_counts[1])
    assert _rounding_count(agent_id, hour, SIMULATION_STEP_S) == _count(hour_counts[0])
    assert _rounding_count(agent_id, hour, EARLIER_STEP_S) == _count(hour_counts[1])


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_each_run_at_the_envelope_corner_has_the_derived_bound_printed(agent_id: str) -> None:
    """`run_rounding` bounds each of the three runs at the envelope corner at 1.1e-11.

    The three runs are the corner held, the ventilator start and the
    unperfused load. The last has a phase at zero cardiac output whose step
    needs one squaring fewer, so its 900 steps count as much rounding as the
    600 steps of the other two. `docs/VERIFICATION.md` prints the bound to
    two significant figures.
    """

    mantissa, exponent = _printed(
        r"The derived bound from `run_rounding` is \$`(\d\.\d)\\times10\^\{-(\d+)\}`\$ of a"
    )
    runs = (
        _envelope_corner_held(agent_id),
        _ventilator_start(agent_id),
        _unperfused_load_then_dial_off(agent_id),
    )

    for phases in runs:
        bound = sum(
            run_rounding(
                _phase_squarings(agent_id, phase, SIMULATION_STEP_S), StepCount(phase.duration_s)
            )
            for phase in phases
        )

        assert f"{bound:.1e}" == f"{mantissa}e-{exponent}", (agent_id, bound)


@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_the_random_runs_move_every_1_to_20_s_and_reach_each_zero_setting(agent_id: str) -> None:
    """Each random run lasts 600 s, holds each setting 1 to 20 s, and changes 48 to 53 times.

    Across the three seeds, every run of an agent together reaches zero fresh
    gas flow, zero alveolar ventilation and zero cardiac output, as
    `docs/VERIFICATION.md` says.
    """

    shortest, longest = map(int, _printed(r"moves the controls every (\d+) to (\d+) s"))
    fewest, most = map(int, _printed(r"settings (\d+) to (\d+) times takes as many steps"))
    assert (shortest, longest) == (1, RANDOMISED_PHASE_MAX_STEPS)
    runs = [_randomised_trajectory(agent_id, seed) for seed in RANDOMISED_TRAJECTORY_SEEDS]
    points = [phase.point for phases in runs for phase in phases]

    for phases in runs:
        assert sum(phase.duration_s for phase in phases) == 600
        assert fewest <= len(phases) - 1 <= most
        # The last phase is cut short by the end of the run, so only it may be
        # shorter than its draw. Every phase still lasts at least one step.
        assert all(shortest <= phase.duration_s <= longest for phase in phases)

    assert any(point.fresh_gas_flow_l_min == MIN_FRESH_GAS_FLOW_L_MIN for point in points)
    assert any(
        point.alveolar_ventilation_l_min == MIN_ALVEOLAR_VENTILATION_L_MIN for point in points
    )
    assert any(point.cardiac_output_l_min == MIN_CARDIAC_OUTPUT_L_MIN for point in points)
    assert (
        MIN_FRESH_GAS_FLOW_L_MIN == MIN_ALVEOLAR_VENTILATION_L_MIN == MIN_CARDIAC_OUTPUT_L_MIN == 0
    )
