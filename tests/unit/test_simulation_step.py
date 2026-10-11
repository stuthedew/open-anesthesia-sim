"""The run's step as a type: checked once when it is built, and required at each
of the run's entry points (`PL-0GJC`).

The refusals each entry point used to make of an out-of-range step are now the
constructor's, and the tests that pinned them at each entry point still do,
because they build the step at the call. What is pinned here is the type
itself, and the one thing an entry point still refuses: a step nothing built.
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
    """The one place a step is checked, at each edge of the range and past it.

    `5e-324` is the step `PL-YZ17` was filed for: the run length divided by it
    overflows, and it reached `maximum_step_count` as a bare `OverflowError`.
    """

    with pytest.raises(SimulationConfigurationError, match=refusal):
        SimulationStep(seconds)


def test_a_step_refuses_a_bool_a_decimal_and_an_overflowing_int_in_its_own_words() -> None:
    """A step is built from an int or a float and nothing else, inside the range a float holds.

    The guard the step is built on, `require_positive_finite`, reads the value
    first since `PL-3800`. Until then `True` passed as the 1 it is to Python
    and was refused as a step of 1 s rather than as no step at all;
    `Decimal('0.05')` was converted and held as a 0.05 s step; a string was
    refused in `math.isfinite`'s words; and `SimulationStep(10**400)` escaped
    as `OverflowError` from `isfinite` converting it (`PL-21V4`), outside the
    simulator's own exceptions, so a caller catching the
    `SimulationConfigurationError` the docstring promised did not catch it.
    Each is refused by the guard and the type alike, in the same words; an
    `int` inside the float range is still refused against the step's own
    range, as any step outside it is.
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
    """Named as the quantity it was built as, and not told to rebuild as the step.

    A `CaseInstant(0.1)` arriving where the step belongs is a swapped
    argument. Until `PL-848D` the refusal prescribed `SimulationStep(0.1)`,
    which would have the caller build a 0.1 s step from an instant, passing
    every check and holding the wrong quantity, so the message names the type
    the value was built as and prescribes nothing. Every checked quantity is
    one record (`core/checked_number.py`), so a count, a flow and both forms
    of a concentration are refused in the same words.
    """

    with pytest.raises(TypeError) as raised:
        require_simulation_step(other)

    assert str(raised.value) == (
        f"simulation_step_s of {other!r} was built as {type(other).__name__}, which is not "
        "SimulationStep: it is another quantity, so build SimulationStep from the value that "
        "simulation_step_s should hold, not from this one (core/checked_number.py)"
    )
