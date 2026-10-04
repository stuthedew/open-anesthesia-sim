"""The run's step as a type: checked once when it is built, and required at each
of the run's entry points (`PL-0GJC`).

The refusals each entry point used to make of an out-of-range step are now the
constructor's, and the tests that pinned them at each entry point still do,
because they build the step at the call. What is pinned here is the type
itself, and the one thing an entry point still refuses: a step nothing built.
"""

import copy
import pickle
from math import inf, nan, nextafter

import pytest

from anesthesia_sim.app.playback import PlaybackRate
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import (
    MAXIMUM_SIMULATION_STEP_S,
    MINIMUM_SIMULATION_STEP_S,
    SimulationStep,
)
from anesthesia_sim.core.supported_ranges import StepCount
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


@pytest.mark.parametrize("seconds", [MINIMUM_SIMULATION_STEP_S, 0.02304, MAXIMUM_SIMULATION_STEP_S])
def test_a_supported_step_is_the_number_it_was_built_from(seconds: float) -> None:
    """Both bounds are supported, and the step is the float itself, unrounded."""

    step = SimulationStep(seconds)

    assert isinstance(step, float)
    assert step == seconds
    assert float(step).hex() == seconds.hex()


@pytest.mark.parametrize(
    ("seconds", "refusal"),
    [
        (0.0, "positive and finite"),
        (-0.1, "positive and finite"),
        (nan, "positive and finite"),
        (inf, "positive and finite"),
        (5e-324, "smallest supported step"),
        (nextafter(MINIMUM_SIMULATION_STEP_S, 0.0), "smallest supported step"),
        (nextafter(MAXIMUM_SIMULATION_STEP_S, inf), "largest supported step"),
        (30.0, "largest supported step"),
    ],
)
def test_a_step_outside_the_supported_range_cannot_be_built(seconds: float, refusal: str) -> None:
    """The one place a step is checked, at each edge of the range and past it.

    `5e-324` is the step `PL-YZ17` was filed for: the run length divided by it
    overflows, and it reached `maximum_step_count` as a bare `OverflowError`.
    """

    with pytest.raises(SimulationConfigurationError, match=refusal):
        SimulationStep(seconds)


def test_arithmetic_on_a_step_is_a_plain_float() -> None:
    """What a step is multiplied into is not itself a checked step.

    The elapsed time a count of steps reaches is the product of the count and
    the step, and it is no step at all; were it a `SimulationStep`, a reader
    of a signature could take it for one the constructor had checked.
    """

    step = SimulationStep(0.1)

    assert type(step * 600) is float
    assert type(600 * step) is float
    assert type(step / 2) is float
    assert type(step + step) is float


def test_a_copied_or_pickled_step_is_still_a_step() -> None:
    """A state copied for a branch, or saved, keeps a step that is still checked.

    Each of these rebuilds the step through the constructor rather than around
    it, so a copy cannot carry an unchecked value under the type's name.
    """

    step = SimulationStep(0.1)

    for copied in (copy.copy(step), copy.deepcopy(step), pickle.loads(pickle.dumps(step))):
        assert type(copied) is SimulationStep
        assert copied == step


def test_a_bare_float_step_is_refused_at_each_run_entry() -> None:
    """A step nobody built is refused before anything moves, at all four entries.

    `mypy` refuses a bare `float` at each of these in `src/`, but it does not
    read `tests/`, and it passes a value typed `Any`. This is the runtime half:
    a `TypeError`, because passing the wrong type is a programming error rather
    than a setting the simulator rejected (`core/exceptions.py`). The value is
    a supported step, so what is refused is the type and nothing else.
    """

    bare_step_s = 0.1

    with pytest.raises(TypeError, match="not a SimulationStep"):
        SimulationState(step_count=StepCount(0), simulation_step_s=bare_step_s)  # type: ignore[arg-type]

    state = SimulationState()
    vector_before = state.uptake_system.state_vector()

    with pytest.raises(TypeError, match="not a SimulationStep"):
        state.advance(bare_step_s)  # type: ignore[arg-type]

    assert state.step_count == 0
    assert state.simulation_step_s is None
    assert state.uptake_system.state_vector() == vector_before

    system = AgentUptakeSystem.default()
    vector_before = system.state_vector()

    with pytest.raises(TypeError, match="not a SimulationStep"):
        system.advance(bare_step_s)  # type: ignore[arg-type]

    assert system.state_vector() == vector_before

    with pytest.raises(TypeError, match="not a SimulationStep"):
        PlaybackRate(1).steps_per_tick(
            tick_interval_s=0.1,
            simulation_step_s=bare_step_s,  # type: ignore[arg-type]
        )
