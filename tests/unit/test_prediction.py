"""A preview's prediction starts at the run's stored state and steps one second at a time.

The expected states come from a sevoflurane run stepped by the simulation
itself, which is a separate route from the prediction under test: the run
reads each fraction back from the amount of agent in its compartment, and the
prediction propagates the fractions directly (`core/prediction.py`).
`tests/unit/test_generated_runs.py` holds predictions to an exact solution
worked out in decimal arithmetic.
"""

import pytest
from test_numerical_envelope import _squarings

from anesthesia_sim.core.concentration import Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    FRACTION_STATE_NAMES,
    UptakeEquationSettings,
    build_system_matrix,
)
from anesthesia_sim.core.prediction import predicted_states, predicted_states_at
from anesthesia_sim.core.rounding import propagator_rounding, run_rounding
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import CaseInstant, StepCount
from anesthesia_sim.core.uptake_system import AgentUptakeSystem

DIAL_DOWN_AT_S = 300
"""The second at which the run's dial moves from its opening setting to 0.8%."""

REACHED_S = 600
"""The second the prediction opens at, five minutes after the dial moved."""

LAST_S = 1_800
"""The last second compared: twenty minutes of prediction past the reach."""


def _stepped_run(last_s: int) -> tuple[SimulationState, UptakeEquationSettings]:
    """Step sevoflurane to `last_s`, turning the dial down to 0.8% at `DIAL_DOWN_AT_S`.

    Return the run and the settings it held after the dial moved. The dial
    moves before the prediction opens, so the run's later seconds are stepped
    under the settings the prediction is given.
    """

    system = AgentUptakeSystem.for_agent("sevoflurane")
    run = SimulationState(uptake_system=system)

    for second in range(1, last_s + 1):
        run.advance()

        if second == DIAL_DOWN_AT_S:
            system.set_delivered_concentration_percent(Percent(0.8))

    return run, system.equation_settings()


def test_the_prediction_opens_at_the_stored_state_and_ends_at_the_last_second() -> None:
    run, settings = _stepped_run(REACHED_S)
    opening = run.stored_states.state_at(CaseInstant(REACHED_S))

    predicted = predicted_states(settings, opening, CaseInstant(REACHED_S), CaseInstant(LAST_S))

    assert predicted[0] is opening
    assert len(predicted) == LAST_S - REACHED_S + 1


def test_a_prediction_over_no_seconds_is_the_opening_alone() -> None:
    run, settings = _stepped_run(REACHED_S)
    opening = run.stored_states.state_at(CaseInstant(REACHED_S))

    assert predicted_states(settings, opening, CaseInstant(REACHED_S), CaseInstant(REACHED_S)) == (
        opening,
    )


def test_each_predicted_second_matches_the_second_the_run_stepped() -> None:
    """Twenty minutes of prediction stay within rounding of the run that stepped the same seconds.

    Each fraction is compared with the run's stored state for the same
    second. A prediction that took a step of any other length, or that was off
    by one second, would differ by the change in a fraction over one second.
    On this run the smallest such change is 5.5e-11 of 1 atm, in the inspired
    fraction near the end, and the limit is at most 3.1e-13. The largest
    difference measured on 2026-11-21 was 6.9e-18.

    The limit is numerical. The prediction and the run each lie within
    `run_rounding` of the exact solution, as a share of the largest fraction
    in the run, so the two lie within twice that of each other. The run also
    reads each fraction back from an amount once per step, which moves it by
    at most one unit in its last place, and that is far below the
    propagator's bound of ten units for one step.
    """

    run, settings = _stepped_run(LAST_S)
    stored = [run.stored_states.state_at(CaseInstant(second)) for second in range(LAST_S + 1)]
    scale = max(
        float(settings.delivered_concentration_percent) / 100.0,
        *(state[index] for state in stored for index, _ in FRACTION_STATE_NAMES),
    )

    predicted = predicted_states(
        settings, stored[REACHED_S], CaseInstant(REACHED_S), CaseInstant(LAST_S)
    )

    squarings = _squarings(build_system_matrix(settings), SIMULATION_STEP_S)

    for offset, predicted_state in enumerate(predicted):
        limit = 2.0 * run_rounding(squarings, StepCount(offset)) * scale
        stepped_state = stored[REACHED_S + offset]

        for index, _ in FRACTION_STATE_NAMES:
            difference = abs(predicted_state[index] - stepped_state[index])

            assert difference <= limit, (offset, index, difference, limit)


def test_a_prediction_ending_before_it_opens_is_refused() -> None:
    run, settings = _stepped_run(REACHED_S)
    opening = run.stored_states.state_at(CaseInstant(REACHED_S))

    with pytest.raises(
        SimulationConfigurationError, match="a prediction from 600 s to 599 s ends before it begins"
    ):
        predicted_states(settings, opening, CaseInstant(REACHED_S), CaseInstant(REACHED_S - 1))


def test_an_opening_that_is_not_a_state_is_refused() -> None:
    _, settings = _stepped_run(0)

    with pytest.raises(SimulationConfigurationError, match="a list is not a state vector"):
        predicted_states(
            settings,
            [0.0] * 8 + [1.0],  # type: ignore[arg-type]
            CaseInstant(0),
            CaseInstant(10),
        )


@pytest.mark.parametrize("argument", ["opened_at_s", "last_s"])
def test_a_second_not_built_as_a_case_instant_is_refused(argument: str) -> None:
    run, settings = _stepped_run(0)
    opening = run.stored_states.state_at(CaseInstant(0))
    seconds: dict[str, object] = {"opened_at_s": CaseInstant(0), "last_s": CaseInstant(10)}
    seconds[argument] = 10 if argument == "last_s" else 0

    with pytest.raises(TypeError, match="CaseInstant"):
        predicted_states(settings, opening, **seconds)  # type: ignore[arg-type]


CHOSEN_SECONDS = (630, 660, 690, 1_000, 1_043, 1_086, 1_800)
"""Seconds past the reach with gaps of 30, 43, 310 and 714 s, ending at `LAST_S`."""


def test_a_prediction_at_chosen_seconds_matches_the_seconds_the_run_stepped() -> None:
    """Each state predicted at a chosen second is within rounding of the run's stored state there.

    The expected states are the run's own, stepped one second at a time, which
    is a separate route from one propagator over each gap. A prediction off by
    one second at any gap would differ from the run by the change in a
    fraction over one second. At these seconds that change is at least 8.9e-10
    of 1 atm, and the limit is at most 2.7e-13 (measured 2026-11-21).

    The limit is numerical. A propagator over a gap of n seconds takes more
    squarings than one over a second, and each gap's propagator rounds within
    `propagator_rounding` of its squarings. So the prediction lies within the
    sum of those bounds of the exact solution, and the run within
    `run_rounding` of its one-second steps. Both are shares of the largest
    fraction in the run.
    """

    run, settings = _stepped_run(LAST_S)
    stored = [run.stored_states.state_at(CaseInstant(second)) for second in range(LAST_S + 1)]
    scale = max(
        float(settings.delivered_concentration_percent) / 100.0,
        *(state[index] for state in stored for index, _ in FRACTION_STATE_NAMES),
    )
    matrix = build_system_matrix(settings)

    predicted = predicted_states_at(
        settings,
        stored[REACHED_S],
        CaseInstant(REACHED_S),
        tuple(CaseInstant(second) for second in CHOSEN_SECONDS),
    )

    assert len(predicted) == len(CHOSEN_SECONDS)
    prediction_rounding = 0.0
    previous_s = REACHED_S

    for second, predicted_state in zip(CHOSEN_SECONDS, predicted, strict=True):
        prediction_rounding += propagator_rounding(_squarings(matrix, second - previous_s))
        previous_s = second
        run_bound = run_rounding(
            _squarings(matrix, SIMULATION_STEP_S), StepCount(second - REACHED_S)
        )
        limit = (prediction_rounding + run_bound) * scale

        for index, _ in FRACTION_STATE_NAMES:
            difference = abs(predicted_state[index] - stored[second][index])

            assert difference <= limit, (second, index, difference, limit)


def test_a_prediction_at_no_seconds_is_empty() -> None:
    run, settings = _stepped_run(REACHED_S)
    opening = run.stored_states.state_at(CaseInstant(REACHED_S))

    assert predicted_states_at(settings, opening, CaseInstant(REACHED_S), ()) == ()


@pytest.mark.parametrize(
    ("seconds", "message"),
    [
        ((600,), "a prediction at 600 s follows 600 s"),
        ((700, 650), "a prediction at 650 s follows 700 s"),
        ((700, 700), "a prediction at 700 s follows 700 s"),
    ],
)
def test_a_chosen_second_that_does_not_come_after_the_one_before_is_refused(
    seconds: tuple[int, ...], message: str
) -> None:
    run, settings = _stepped_run(REACHED_S)
    opening = run.stored_states.state_at(CaseInstant(REACHED_S))

    with pytest.raises(SimulationConfigurationError, match=f"^{message}"):
        predicted_states_at(
            settings,
            opening,
            CaseInstant(REACHED_S),
            tuple(CaseInstant(second) for second in seconds),
        )


def test_a_chosen_second_not_built_as_a_case_instant_is_refused() -> None:
    run, settings = _stepped_run(REACHED_S)
    opening = run.stored_states.state_at(CaseInstant(REACHED_S))

    with pytest.raises(TypeError, match="CaseInstant"):
        predicted_states_at(
            settings,
            opening,
            CaseInstant(REACHED_S),
            (700,),  # type: ignore[arg-type]
        )
