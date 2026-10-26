"""Define the step range that the coupled system supports, and a type that holds only such a step.

A run's step is one value: the number of simulated seconds by which each call to
`AgentUptakeSystem.advance()` moves the run forward. It used to be a bare `float`, and each
entry point that took one checked it by hand. An entry point that lacked the check accepted a
step that nothing had checked. Each such entry point was found as a separate defect, and
`PL-0GJC` counts them. `SimulationStep` checks the step once, when it is chosen. A function that
takes a `SimulationStep` says so in its signature, and `mypy --strict` rejects a bare `float`
passed to it.

**It is the run's step, not a compartment's.** The supported range has a ceiling,
`MAXIMUM_SIMULATION_STEP_S`, and a floor, `MINIMUM_SIMULATION_STEP_S`. The ceiling limits how
long the coupled system holds its settings constant, so it is a property of the step that the
whole system takes. A compartment stepped on its own therefore takes a plain `float`, and it
gives a correct result for a step longer than the ceiling. The floor is different. Rounding
error grows as the step shrinks, in a compartment stepped alone just as in a run. So each
compartment's own `advance` refuses a step below the floor (`PL-WP52`). It also refuses a step
longer than the supported run length (`PL-YT3T`). `require_compartment_step` makes both checks.
It is in `core/supported_ranges.py`, which also holds the run length.

**Why a `float` subclass rather than either of the other shapes used in `core/`.** A `NewType`
is a label that the type checker uses and the interpreter discards. `concentration.py` uses a
`NewType` only for `MacMultiple`. Calling a `NewType` returns its argument unchanged. So a
`NewType` suits a unit, where every float is a valid value, but not a range. A frozen dataclass
rejects a bad value as well as this type does, and `tissue.py` uses that shape for its states.
But a dataclass would put `.seconds` into every equation that multiplies by the step. A `float`
subclass is checked when it is built, and in arithmetic it is the number itself. That
arithmetic returns a plain `float`, so a quantity derived from the step does not carry the
step's guarantee by mistake.

**What the type cannot cover, and the check that does.** `mypy` checks `src/` but not `tests/`.
It also accepts a value typed `Any`. So a bare `float` can still arrive at runtime. The run has
three entry points, and each one calls `require_simulation_step` first. They are
`SimulationState`, at every write to its step field (`PL-8W1W`); `AgentUptakeSystem.advance()`;
and `PlaybackRate.steps_per_tick()`. `require_simulation_step` treats anything that is not a
`SimulationStep` as a programming error and refuses it. A value built as a different checked
quantity gets an error that calls it a swapped argument. The error does not tell the caller to
build a step from that value (`PL-848D`). Every function behind these entry points takes the
step as already checked.
"""

from __future__ import annotations

from anesthesia_sim.core.checked_number import CheckedQuantity, require_not_another_quantity, shown
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.validation import require_positive_finite

# The largest simulation step `AgentUptakeSystem.advance()` accepts.
#
# It is not a bound on the arithmetic, and re-deriving it (`PL-X9KD`) found no
# such bound. The propagator is the exact solution of the governing equations
# over whatever interval it is given. Its floating-point evaluation was
# measured across the settings envelope for every step from 1e-3 s to 3600 s.
# Its error is 1e-14 to 2e-12, as an absolute difference in concentration
# fraction, not a relative error. That error does not grow with the step.
# It is U-shaped in the step, because the only error mechanism left is
# rounding, which accumulates once per step and so gets *worse* as the step
# shrinks. The first step at which any displayed digit is wrong by a whole
# count is around 1e13 s. No numerical ceiling that a caller can reach exists.
#
# What a longer step costs is control resolution. Every setting is held
# constant across a step, so a control change takes effect at the next step
# boundary and is delayed by up to one whole step. That delay is exactly
# proportional to the step, with no threshold anywhere in it, so no step size
# is the one at which control timing "becomes invisible". This constant is
# therefore a declared tolerance rather than a derived limit, and is recorded
# here as one.
#
# The tolerance it declares was measured on 2026-09-06 in percentage points
# (pp) of one atmosphere. It is stated in those units rather than in counts of
# any readout. At this step, the case-opening manoeuvre displaces every
# displayed compartment by at most 6.7e-3 pp, with desflurane the worst agent.
# That manoeuvre is dialling from off to 1 MAC at the reference adult's own
# flows. One standard deviation of a single measured partition coefficient
# displaces a compartment by 9e-4 to 6.8e-2 pp (Yasuda 1989; see docs/MODEL.md
# "Displayed precision"). So an ordinary control action is timed well inside
# the model's own parameter uncertainty. That is the criterion, and no count
# of display decimals enters it.
#
# This tolerance does *not* cover an abrupt manoeuvre, and that is stated here
# rather than left to be found. A ventilator start at this step displaces the
# alveolar reading by up to 1.4e-1 pp for the duration of its transient, about
# twice one parameter SD. Holding that inside one SD needs a step near 0.05 s.
#
# That choice was put to the project owner and decided on 2026-09-06: the
# value stays here and the timing is accepted (PL-NBCJ). Moving to 0.05 s
# would double the propagations per simulated second and force the
# interface's tick structure to be revisited. By then, PL-NBWP had also
# narrowed what the change would buy to 1x playback alone. Above 1x, the
# interface's own control grid is `multiplier x 0.1` s, which dominates the
# step outright. So this is a declared tolerance that has been argued, not a
# default that nobody revisited. Timing the ventilator start to about twice
# one parameter SD is its accepted cost, not an oversight. docs/MODEL.md
# "Supported simulation step" carries the measurements and the whole of the
# decision.
#
# Both figures are per step of delay, and a *caller* decides how many steps of
# delay a control change waits (PL-NBWP). So they are what a caller sees when
# it advances one step per control opportunity. The shipped interface is such
# a caller only at 1x playback. It advances a whole tick's worth of steps
# between control opportunities, so its own resolution is that many times
# coarser than this one: 30 s, and up to about 10 pp, at 300x, measured over
# the same manoeuvres. That is a property of the caller's loop and not of this
# constant, which is why the number here does not change. But the constant is
# a lower bound on the interface's resolution, not a statement of it. A reader
# who takes it for the interface's resolution thinks the interface is several
# hundred times finer than it is. The whole per-rate table is in docs/MODEL.md
# "Supported simulation step" beside this one, and app/playback.py states
# which grid the interface actually offers.
#
# Every figure quoted above, and this constant's own value, is re-measured from
# the parameter files at each run by tests/reference/test_control_resolution.py.
# Until PL-ZVS7, only this comment and docs/MODEL.md recorded them. So changing
# the model would have left both documents asserting a tolerance that the code
# no longer met, while make check still passed.
MAXIMUM_SIMULATION_STEP_S = 0.1

# This is the smallest simulation step that `AgentUptakeSystem.advance()` accepts
# (PL-YZ17). It is also the smallest step that a compartment stepped on its own
# accepts (PL-WP52).
#
# Unlike the ceiling above, this bound is numerical. The exact step has no
# truncation error at any step size, so what a finer step costs is rounding.
# Each step adds its change to the value already stored. The finer the step,
# the smaller that change is beside the stored value, so the same rounding
# error is a larger share of the change. This was measured on 2026-10-03 over
# 10 000 steps, starting 60 s into the default sevoflurane wash-in. The change
# in the alveolar, vessel-rich, muscle and fat fractions was wrong by at most
# 3e-12 of itself at 1 ms, 7e-9 at 1 us, 1e-4 at 1e-10 s and a third at
# 1e-14 s. Nothing raised an error at any of these steps. The growth has no
# knee. So, as with the ceiling, no step is the one at which the result
# "becomes wrong", and this constant is declared rather than derived.
#
# It is declared at the finest step at which the solution has been shown to match
# the shipped one. That step is the bottom of the step sweep that PL-X9KD took. A
# test beside the step-refinement gate in tests/reference/test_sevo_patient.py
# drives the gate at this step, and pins this constant to the value at which
# its figures were measured. Nothing runs finer: apart from the tests of this floor itself,
# the finest step any test takes is 0.02304 s.
#
# It also keeps the run's own arithmetic exact. At this step the supported run
# length is 86 400 000 steps, well below 2**53, the limit below which a float
# represents every whole count exactly. Below a step of about 9.6e-12 s, a
# day's count passes that limit, and `elapsed_s` would round the count before
# multiplying. Below about 4.8e-304 s, the run length divided by the step
# overflows. `maximum_step_count` met that as an `OverflowError`, from outside
# the simulator's own exceptions.
#
# A compartment stepped on its own shows the same growth. This was measured on
# 2026-10-19 over 10 000 steps of each of three compartments: a tissue group (time
# constant 480 s), the venous pool (7.8 s) and the breathing circuit (60 s). The
# change in each compartment was wrong by at most 3e-13 of its own size at 1 ms,
# 3e-11 at 1 us and 3e-5 at 1e-10 s. At 1e-14 s it was 4% wrong for the pool and
# the circuit. The tissue did not move at all, so its whole change was lost
# (PL-WP52). The floor therefore applies to each compartment's own `advance` too,
# but the ceiling does not.
#
# Lowering it is a measurement rather than an edit: drive the gate at the new
# floor and re-measure the figures above. docs/MODEL.md "Supported simulation
# step" carries the measurement in full.
MINIMUM_SIMULATION_STEP_S = 1e-3


def require_at_least_the_smallest_step(name: str, simulation_step_s: float) -> None:
    """Require a positive finite step no shorter than `MINIMUM_SIMULATION_STEP_S`.

    This function checks the floor and not the ceiling, `MAXIMUM_SIMULATION_STEP_S`. A
    compartment stepped on its own calls it, through `require_compartment_step` in
    `core/supported_ranges.py`. A compartment needs the floor, because rounding error grows as
    its step shrinks. It does not need the run's ceiling, because it may take a step longer than
    the ceiling (`PL-WP52`). `require_supported_simulation_step` calls this function too, so the
    run and the compartments refuse a step below the floor with the same message.

    `name` is the step's name. Where several objects can raise the error, `name` starts with the
    name of the object that owns the step, as `core/validation.py` explains for `name`.

    Raises:
        TypeError: the step is not an `int` or a `float`, or is a `bool`, as
            `require_a_number` says.
        SimulationConfigurationError: the step is not positive and finite, is
            an `int` outside the range a `float` holds, or is shorter than
            `MINIMUM_SIMULATION_STEP_S`.
    """

    require_positive_finite(name, simulation_step_s)

    if simulation_step_s < MINIMUM_SIMULATION_STEP_S:
        raise SimulationConfigurationError(
            f"{name} of {simulation_step_s} s is shorter than the "
            f"smallest supported step of {MINIMUM_SIMULATION_STEP_S} s, below which "
            "rounding is a growing share of what each step changes "
            '(docs/MODEL.md, "Supported simulation step")'
        )


def require_supported_simulation_step(simulation_step_s: float) -> None:
    """Require a step inside the range over which the coupled system is supported.

    The ceiling belongs to the coupled system rather than to a compartment. It limits how long
    the settings are held constant, and that is a property of the step that the whole system
    takes. The floor is the lower end of the range over which the solution has been verified.
    `require_at_least_the_smallest_step` checks the floor. Each compartment's own `advance` also
    calls that function, through `require_compartment_step` (`PL-WP52`).

    The step must first be a number, and `require_positive_finite` (`core/validation.py`) checks
    this. It refuses a `bool`, a `Decimal` or a string with `require_a_number`'s `TypeError`. It
    refuses an `int` past the float range by name (`PL-3800`). Before that change,
    `SimulationStep(True)` was refused as though it were a step of 1 s, and `Decimal('0.05')` was
    converted and kept as a step. `SimulationStep(10**400)` raised `OverflowError` from
    `math.isfinite`, which is not one of the simulator's own exceptions (`PL-21V4`).

    Raises:
        TypeError: the step is not an `int` or a `float`, or is a `bool`. This is a
            programming error in the caller rather than a refused step, as
            `require_a_number` says.
        SimulationConfigurationError: the step is not positive and finite, is
            an `int` outside the range a `float` holds, is shorter than
            `MINIMUM_SIMULATION_STEP_S`, or exceeds
            `MAXIMUM_SIMULATION_STEP_S`. Nothing is calculated in any of these
            cases, so a caller can retry inside the supported range with the
            run it already has.
    """

    require_at_least_the_smallest_step("simulation_step_s", simulation_step_s)

    if simulation_step_s > MAXIMUM_SIMULATION_STEP_S:
        raise SimulationConfigurationError(
            f"simulation_step_s of {simulation_step_s} s is longer than the "
            f"largest supported step of {MAXIMUM_SIMULATION_STEP_S} s, over which "
            "settings are held constant"
        )


class SimulationStep(float, CheckedQuantity):
    """A run's step in seconds, checked against the supported range when built.

    It compares and computes as the `float` it was built from. A product or
    quotient of it is a plain `float`: the elapsed time a count of steps
    reaches is not itself a step, and is not presented as a checked one.

    Raises:
        TypeError: `seconds` was built as another checked quantity, such as
            an instant, a flow or a fraction. That is a swapped argument, and
            it is refused before the range is checked
            (`core/checked_number.py`, `PL-979Z`). Or `seconds` is not an
            `int` or a `float`, or is a `bool`, as
            `require_supported_simulation_step` states.
        SimulationConfigurationError: the step is not positive and finite, is
            an `int` outside the range a `float` holds, is shorter than
            `MINIMUM_SIMULATION_STEP_S`, or exceeds
            `MAXIMUM_SIMULATION_STEP_S`, as `require_supported_simulation_step`
            states.
    """

    __slots__ = ()

    def __new__(cls, seconds: float) -> SimulationStep:
        require_not_another_quantity("simulation_step_s", seconds, cls)
        require_supported_simulation_step(seconds)

        return super().__new__(cls, seconds)


def require_simulation_step(simulation_step_s: object) -> None:
    """Require a step that was built as a `SimulationStep`, and so checked.

    This is the runtime half of the type, for the callers that `mypy` does not
    check: a test, a notebook, or a value typed `Any`. It checks the type and
    not the range, which the constructor has already checked.

    `require_not_another_quantity` (`core/checked_number.py`) runs before
    this refusal, as it runs first in the constructor. It names a value built
    as another checked quantity, such as an instant, a count, a flow or a concentration, as that
    quantity, and does not tell the caller to rebuild it. Until `PL-848D`, a
    `CaseInstant(0.1)` handed in as the step was told to build
    `SimulationStep(0.1)` from it. That would hold a 0.1 s step built from an
    instant, which is the swap this refusal exists to catch.

    The value prints through `shown`. So a bare `int` too long for `repr` is
    named by its length, rather than escaping as `ValueError` while the
    refusal is written.

    Raises:
        TypeError: `simulation_step_s` is not a `SimulationStep` - a bare
            `float` included, whatever its value. This is a programming error
            in the caller rather than a rejected setting, so it is not an
            `AnesthesiaSimulationError` (`core/exceptions.py`).
    """

    if isinstance(simulation_step_s, SimulationStep):
        return

    require_not_another_quantity("simulation_step_s", simulation_step_s, SimulationStep)

    raise TypeError(
        f"simulation_step_s of {shown(simulation_step_s)} was not built as SimulationStep, "
        f"it is {type(simulation_step_s).__name__}: build it as SimulationStep(...) where "
        "the step is chosen, which checks it against the supported range once "
        '(docs/MODEL.md, "Supported simulation step")'
    )
