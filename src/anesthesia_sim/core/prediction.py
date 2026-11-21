"""The states a case would pass through under one settings record, past the second a run reached.

A preview shows what a run would do if a setting were applied now. The run
has stored no state for those seconds (`core/stored_states.py`), so this
module computes them. It is the only module in `core/` that returns a state
which no step of a run wrote, and no reader of a second that a run has
reached may use it (`PL-Z6C8`).

**A prediction takes the same one-second steps as a run.** It forms the
propagator of one step as the run does, `matrix_exponential` of the system
matrix over `SIMULATION_STEP_S`, and applies it once for each second. So it
returns a state for every whole second, and a chart can draw a predicted
trace by the rule it draws a run's trace by, including the second of each
peak between two columns. `predicted_states_at` returns the states at chosen
seconds only, each reached from the one before by one propagator over the
gap. A preview uses it past its first hour, where a one-second prediction
would cost a step for each second and show nothing more (`PL-Z6C8`).

**A predicted state agrees with the state the run later stores only to
within rounding.** A run's step reads each compartment's fraction back from
the amount of agent that the compartment holds, and that division can move a
fraction by one unit in its last place before the step propagates it
(`PL-MH9J`). A prediction propagates the fractions themselves. Over 24 hours
of one-second steps, a stepped fraction and the same fraction propagated from
the state at the last setting change differed by at most 9.7e-11 of the
fraction (`PL-SZ6G`, measured 2026-11-21).

The delivered and the exhausted agent in a predicted state are plain sums.
A run keeps a compensation term beside each of those totals
(`core/agent_simulation_validation.py`), and a prediction keeps none, because
nothing shows a predicted total.
"""

from __future__ import annotations

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.governing_equations import (
    UptakeEquationSettings,
    build_system_matrix,
    require_canonical_state,
)
from anesthesia_sim.core.matrix_exponential import Matrix, matrix_exponential, propagate
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import CaseInstant, require_case_instant


def predicted_states(
    settings: UptakeEquationSettings,
    opening: tuple[float, ...],
    opened_at_s: CaseInstant,
    last_s: CaseInstant,
) -> tuple[tuple[float, ...], ...]:
    """Return the state at each second from `opened_at_s` to `last_s`, under `settings`.

    Args:
        settings: The settings the case continues under.
        opening: The state at `opened_at_s`, in `governing_equations`' state
            order. A preview passes the state that the run stored for the
            second it has reached.
        opened_at_s: The second of the case that `opening` belongs to.
        last_s: The last second to predict. It is a `CaseInstant`, so it does
            not lie past the supported run length, and no state is predicted
            for a time the model is not claimed to cover.

    Returns:
        One state for each second, in order of time. The first is `opening`
        itself, so the prediction meets the run. Each later state is the one
        before it after one step.

    Raises:
        TypeError: `opened_at_s` or `last_s` is not a `CaseInstant`.
        SimulationConfigurationError: `opening` is not a state that the
            equations can be applied to (`require_canonical_state`), or
            `last_s` is before `opened_at_s`.
    """

    require_canonical_state(opening)
    require_case_instant("opened_at_s", opened_at_s)
    require_case_instant("last_s", last_s)

    if last_s < opened_at_s:
        raise SimulationConfigurationError(
            f"a prediction from {opened_at_s} s to {last_s} s ends before it begins"
        )

    step = matrix_exponential(build_system_matrix(settings), SIMULATION_STEP_S)
    states = [opening]

    for _ in range(opened_at_s, last_s, SIMULATION_STEP_S):
        states.append(propagate(step, states[-1]))

    return tuple(states)


def predicted_states_at(
    settings: UptakeEquationSettings,
    opening: tuple[float, ...],
    opened_at_s: CaseInstant,
    seconds: tuple[CaseInstant, ...],
) -> tuple[tuple[float, ...], ...]:
    """Return the state at each of `seconds` under `settings`, each reached from the one before.

    Each state is the state before it, or `opening` for the first, advanced
    by one propagator over the gap between their seconds. A gap is a whole
    number of seconds, and one propagator over it gives the state that as many
    one-second steps would give, to within rounding. So this returns the same
    states as `predicted_states` at those seconds, without computing the
    seconds between them. A preview uses it past the first hour, where no
    compartment turns between two chart columns (`PL-Z6C8`). The propagator
    of each distinct gap is formed once.

    Args:
        settings: The settings the case continues under.
        opening: The state at `opened_at_s`, in `governing_equations`' state
            order.
        opened_at_s: The second of the case that `opening` belongs to.
        seconds: The seconds to predict, each a `CaseInstant`, in ascending
            order and each after `opened_at_s`.

    Returns:
        One state for each of `seconds`, in the same order.

    Raises:
        TypeError: `opened_at_s` or one of `seconds` is not a `CaseInstant`.
        SimulationConfigurationError: `opening` is not a state that the
            equations can be applied to (`require_canonical_state`), a second
            is not after the one before it, or `opened_at_s`, or the
            propagator over a gap cannot be formed (`matrix_exponential`).
    """

    require_canonical_state(opening)
    require_case_instant("opened_at_s", opened_at_s)

    matrix = build_system_matrix(settings)
    propagators: dict[int, Matrix] = {}
    states: list[tuple[float, ...]] = []
    state, previous_s = opening, int(opened_at_s)

    for second in seconds:
        require_case_instant("second", second)

        if second <= previous_s:
            raise SimulationConfigurationError(
                f"a prediction at {second} s follows {previous_s} s: each second "
                "predicted must come after the one before it and after the opening"
            )

        gap_s = second - previous_s

        if gap_s not in propagators:
            propagators[gap_s] = matrix_exponential(matrix, gap_s * SIMULATION_STEP_S)

        state = propagate(propagators[gap_s], state)
        states.append(state)
        previous_s = second

    return tuple(states)
