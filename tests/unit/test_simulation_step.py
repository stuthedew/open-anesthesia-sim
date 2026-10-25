"""Tests of the run's step as a type, checked once when it is built (`PL-0GJC`).

Each of the run's entry points requires the type. Each entry point used to
refuse an out-of-range step itself, and the constructor now makes those
refusals. The tests that pinned them at each entry point still pin them,
because they build the step at the call. These tests pin the type itself, and
the one thing an entry point still refuses: a step that nothing built.
"""

import copy
import pickle
import sys
from decimal import Decimal
from math import inf, nan, nextafter

import numpy
import pytest

from anesthesia_sim.app.playback import PlaybackRate
from anesthesia_sim.core.concentration import Fraction, Percent
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation import SimulationState
from anesthesia_sim.core.simulation_step import (
    MAXIMUM_SIMULATION_STEP_S,
    MINIMUM_SIMULATION_STEP_S,
    SimulationStep,
    require_simulation_step,
    require_supported_simulation_step,
)
from anesthesia_sim.core.supported_ranges import (
    AlveolarVentilation,
    CardiacOutput,
    CaseInstant,
    FreshGasFlow,
    StepCount,
)
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
    """The constructor, the one place a step is checked, refuses a step past either edge.

    The cases sit just past each edge of the range and further past it.
    `5e-324` is the step `PL-YZ17` was filed for. The run length divided by it
    overflows, and the overflow reached `maximum_step_count` as a bare
    `OverflowError`.
    """

    with pytest.raises(SimulationConfigurationError, match=refusal):
        SimulationStep(seconds)


def test_a_step_refuses_a_bool_a_decimal_and_an_overflowing_int_in_its_own_words() -> None:
    """A step is built from an int or a float and nothing else, inside the range a float holds.

    Since `PL-3800`, the guard that the step is built on,
    `require_positive_finite`, first checks that the value is a number. Before that,
    `True` passed as the 1 that it equals in Python, and was refused as a step
    of 1 s rather than as no step at all. `Decimal('0.05')` was converted and
    stored as a 0.05 s step. A string was refused in `math.isfinite`'s words.
    And `SimulationStep(10**400)` escaped as an `OverflowError` when `isfinite`
    converted it (`PL-21V4`). That exception is outside the simulator's own
    exceptions, so a caller catching the `SimulationConfigurationError` that
    the docstring promised did not catch it. The guard and the type now refuse
    each of these in the same words. An `int` inside the float range is still
    checked against the step's own range, and refused outside it, as any step
    is.
    """

    for value in (True, numpy.True_, Decimal("0.05"), Decimal("sNaN"), "0.05"):
        for build in (require_supported_simulation_step, SimulationStep):
            with pytest.raises(TypeError) as raised:
                build(value)  # type: ignore[arg-type]

            message = str(raised.value)

            assert message.startswith(
                f"simulation_step_s of {value!r} has type {type(value).__name__}"
            )
            assert "not int or float" in message

    with pytest.raises(SimulationConfigurationError) as by_the_type:
        SimulationStep(10**400)

    with pytest.raises(SimulationConfigurationError) as by_the_guard:
        require_supported_simulation_step(10**400)

    assert str(by_the_type.value) == str(by_the_guard.value)
    assert str(by_the_guard.value) == (
        f"simulation_step_s of {10**400} is outside the range a float holds, "
        f"-{sys.float_info.max!r} to {sys.float_info.max!r}"
    )

    with pytest.raises(SimulationConfigurationError, match="largest supported step"):
        SimulationStep(10**300)


def test_arithmetic_on_a_step_is_a_plain_float() -> None:
    """The result of arithmetic on a step is not itself a checked step.

    The elapsed time after a count of steps is the count times the step, and
    it is not a step at all. If it were a `SimulationStep`, a reader of a
    signature could take it for a step that the constructor had checked.
    """

    step = SimulationStep(0.1)

    assert type(step * 600) is float
    assert type(600 * step) is float
    assert type(step / 2) is float
    assert type(step + step) is float


def test_a_copied_or_pickled_step_is_still_a_step() -> None:
    """A state copied for a branch, or saved, keeps a step that is still checked.

    Each of these rebuilds the step through the constructor rather than
    bypassing it, so a copy cannot carry an unchecked value under the type's
    name.
    """

    step = SimulationStep(0.1)

    for copied in (copy.copy(step), copy.deepcopy(step), pickle.loads(pickle.dumps(step))):
        assert type(copied) is SimulationStep
        assert copied == step


def test_a_bare_float_step_is_refused_at_each_run_entry() -> None:
    """A step that nobody built is refused at all four entry points, before anything changes.

    `mypy` refuses a bare `float` at each of these in `src/`, but it does not
    read `tests/`, and it passes a value typed `Any`. This test checks the
    runtime half. It expects a `TypeError`, because passing the wrong type is a
    programming error rather than a setting the simulator rejected
    (`core/exceptions.py`). The value is a supported step, so what is refused
    is the type and nothing else.
    """

    bare_step_s = 0.1

    with pytest.raises(TypeError) as raised:
        SimulationState(step_count=StepCount(0), simulation_step_s=bare_step_s)  # type: ignore[arg-type]

    assert str(raised.value) == (
        "simulation_step_s of 0.1 was not built as SimulationStep, it is float: build it as "
        "SimulationStep(...) where the step is chosen, which checks it against the supported "
        'range once (docs/MODEL.md, "Supported simulation step")'
    )

    state = SimulationState()
    vector_before = state.uptake_system.state_vector()

    with pytest.raises(TypeError, match="was not built as SimulationStep"):
        state.advance(bare_step_s)  # type: ignore[arg-type]

    assert state.step_count == 0
    assert state.simulation_step_s is None
    assert state.uptake_system.state_vector() == vector_before

    system = AgentUptakeSystem.default()
    vector_before = system.state_vector()

    with pytest.raises(TypeError, match="was not built as SimulationStep"):
        system.advance(bare_step_s)  # type: ignore[arg-type]

    assert system.state_vector() == vector_before

    with pytest.raises(TypeError, match="was not built as SimulationStep"):
        PlaybackRate(1).steps_per_tick(
            tick_interval_s=0.1,
            simulation_step_s=bare_step_s,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "other",
    [
        CaseInstant(0.1),
        StepCount(600),
        FreshGasFlow(4.0),
        AlveolarVentilation(4.0),
        CardiacOutput(5.0),
        Fraction(0.5),
        Percent(2.0),
    ],
    ids=lambda other: type(other).__name__,
)
def test_another_quantity_handed_in_as_the_step_is_refused_as_a_swapped_argument(
    other: object,
) -> None:
    """The refusal names the value's own quantity and does not say to rebuild it as a step.

    A `CaseInstant(0.1)` arriving where the step belongs is a swapped
    argument. Until `PL-848D`, the refusal prescribed `SimulationStep(0.1)`.
    That advice would have the caller build a 0.1 s step from an instant,
    which passes every check and holds the wrong quantity. So the message now
    names the type that the value was built as, and prescribes nothing. Every
    checked quantity is marked as one in a single record
    (`core/checked_number.py`), so a count, a flow and both forms of a
    concentration are refused in the same words.
    """

    with pytest.raises(TypeError) as raised:
        require_simulation_step(other)

    assert str(raised.value) == (
        f"simulation_step_s of {other!r} was built as {type(other).__name__}, which is not "
        "SimulationStep: it is another quantity, so build SimulationStep from the value that "
        "simulation_step_s should hold, not from this one (core/checked_number.py)"
    )
