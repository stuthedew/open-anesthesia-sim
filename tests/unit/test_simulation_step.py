"""Tests of the one step that a run takes: one second, which no caller chooses (`PL-SZ6G`).

Until `PL-SZ6G` the step was a checked type, `SimulationStep`, that a caller
built from a value between 1 ms and 0.1 s. These tests pin what replaced it.
The step is one constant, each entry point of a run takes no step argument, and
a run's clock after a count of steps is that count of whole seconds.
"""

import inspect

import pytest

from anesthesia_sim.core import simulation_step
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.supported_ranges import CaseInstant
from anesthesia_sim.core.uptake_system import AgentUptakeSystem


def test_the_step_is_one_whole_second() -> None:
    """The step is the `int` 1, so a count of steps is a count of seconds.

    The expected value is written here as a literal. `docs/VERIFICATION.md`
    § "Supported simulation step" states it, and the control-resolution figures
    in `tests/reference/test_control_resolution.py` are measured at it. A `bool`
    equals 1 in Python and a `float` 1.0 does too, so the type is checked
    separately.
    """

    assert type(SIMULATION_STEP_S) is int
    assert SIMULATION_STEP_S == 1


def test_the_step_module_offers_no_other_step() -> None:
    """Nothing in the step's module builds or checks a step of another length.

    The names that built and checked a caller's step are gone, so no caller
    can ask for a step that the control-resolution figures were not measured
    at. A compartment stepped on its own still takes a `float` step, which
    `require_compartment_step` in `core/supported_ranges.py` checks.
    """

    public_names = {name for name in vars(simulation_step) if not name.startswith("_")}

    assert public_names - {"annotations", "Final"} == {"SIMULATION_STEP_S"}


@pytest.mark.parametrize("advance", [SimulationState.advance, AgentUptakeSystem.advance])
def test_neither_way_of_stepping_a_run_takes_a_step_length(advance: object) -> None:
    """`advance` has no parameter but `self`, on the run's state and on the uptake system."""

    assert list(inspect.signature(advance).parameters) == ["self"]  # type: ignore[arg-type]


def test_a_step_length_handed_to_a_run_is_refused_before_anything_changes() -> None:
    """A caller that still passes a step gets Python's own `TypeError`, and the run is unchanged."""

    state = SimulationState()
    vector_before = state.uptake_system.state_vector()

    with pytest.raises(TypeError):
        state.advance(0.1)  # type: ignore[call-arg]

    with pytest.raises(TypeError):
        state.uptake_system.advance(1)  # type: ignore[call-arg]

    assert state.step_count == 0
    assert state.uptake_system.state_vector() == vector_before


@pytest.mark.parametrize("steps", [1, 2, 3, 600])
def test_the_clock_after_a_count_of_steps_is_that_many_whole_seconds(steps: int) -> None:
    """After `steps` steps the clock reads exactly `steps` seconds, as an `int`-based instant.

    Three steps of the 0.1 s step that this replaced read
    0.30000000000000004 s, which is the rounded product that `PL-SZ6G`
    removed. The expected value here is the count itself.
    """

    state = SimulationState()

    for _ in range(steps):
        state.advance()

    assert type(state.elapsed_s) is CaseInstant
    assert isinstance(state.elapsed_s, int)
    assert state.elapsed_s == steps
