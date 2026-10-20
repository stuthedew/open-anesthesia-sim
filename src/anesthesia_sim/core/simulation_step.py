"""The step a run is taken at: the range the coupled system supports, and a
type that cannot hold a step outside it.

A run's step is one fact: the simulated seconds that each call to
`AgentUptakeSystem.advance()` moves. It used to be a bare `float`, checked by hand
at each entry point that took one. An entry point that the check had not reached
then took a step that nothing had checked, and each such entry point was found as
a separate defect (`PL-0GJC` counts them). `SimulationStep` checks the step once,
when it is chosen. A function that takes one says so in its signature, where
`mypy --strict` refuses a bare `float`.

**It is the run's step, not a compartment's.** The supported range has a ceiling,
`MAXIMUM_SIMULATION_STEP_S`, and a floor, `MINIMUM_SIMULATION_STEP_S`. The ceiling
is how long the coupled system holds its settings constant, so it is a property of
the step that the whole system takes. A compartment stepped on its own therefore
takes a plain `float`, and a step longer than the ceiling is correct for it. The
floor is different. Rounding error grows as the step shrinks, in a compartment
stepped alone just as in a run. So each compartment's own `advance` refuses a step
below the floor, through `require_at_least_the_smallest_step` (`PL-WP52`).

**Why a `float` subclass rather than either neighbour in `core/`.** A
`NewType`, which `concentration.py` keeps for `MacMultiple` alone, is a
label the type checker reads and the interpreter discards: calling one returns
its argument unchanged, so it suits a unit, where every float is a valid
value, and not a range. A frozen dataclass, the shape `tissue.py`'s states
take, refuses as well as this does but puts `.seconds` into every equation
that multiplies by the step. A `float` subclass is checked when it is built
and is the number itself in the arithmetic, and that arithmetic returns a
plain `float`, so a quantity derived from the step does not carry the step's
guarantee by mistake.

**What the type cannot reach, and the check that does.** `mypy` reads `src/`
but not `tests/`, and it passes a value typed `Any`, so a bare `float` can
still arrive at runtime. Each of the run's entry points calls
`require_simulation_step` first. The entry points are `SimulationState`, at every
write to its step field (`PL-8W1W`), `AgentUptakeSystem.advance()` and
`PlaybackRate.steps_per_tick()`. `require_simulation_step` refuses anything that
is not a `SimulationStep` as a programming error. When the value was built as a
different checked quantity, it names the value as a swapped argument rather than
telling the caller to rebuild a step from it (`PL-848D`). Every function behind
these entry points takes the step as already checked.
"""

from __future__ import annotations

from anesthesia_sim.core.checked_number import CheckedQuantity, require_not_another_quantity, shown
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.validation import require_positive_finite

# The largest simulation step `AgentUptakeSystem.advance()` accepts.
#
# It is not a bound on the arithmetic, and re-deriving it (`PL-X9KD`) did not
# find one. The propagator is the exact solution of the governing equations
# over whatever interval it is given, and its floating-point evaluation is
# measured across the settings envelope at 1e-14 to 2e-12 in fraction for every
# step from 1e-3 s to 3600 s - not growing with the step but U-shaped in it,
# because the only mechanism left is rounding, which accumulates once per step
# and so gets *worse* as the step shrinks. The first step at which any displayed
# digit is wrong by a whole count is around 1e13 s. No numerical ceiling
# reachable by a caller exists.
#
# What a longer step costs is control resolution. Every setting is held
# constant across a step, so a control change takes effect at the next step
# boundary and is displaced later by up to one whole step. That displacement is
# exactly proportional to the step, with no threshold anywhere in it, so no step
# size is the one at which control timing "becomes invisible" - which means this
# constant is a declared tolerance rather than a derived limit, and is recorded
# here as one.
#
# The tolerance it declares, measured 2026-09-06 in percentage points of one
# atmosphere and stated in those units rather than in counts of any readout:
# at this step the case-opening manoeuvre - dialling from off to 1 MAC at the
# reference adult's own flows - displaces every displayed compartment by at most
# 6.7e-3 pp, desflurane binding. One standard deviation of a single measured
# partition coefficient displaces one by 9e-4 to 6.8e-2 pp (Yasuda 1989; see
# docs/MODEL.md "Displayed precision"). So an ordinary control action is timed
# well inside the model's own parameter uncertainty, which is the criterion,
# and it is a criterion no display decimal count enters.
#
# What that does *not* cover, stated rather than left to be found: an abrupt
# manoeuvre is not held inside it. A ventilator start at this step displaces the
# alveolar reading by up to 1.4e-1 pp for the duration of its transient, about
# twice one parameter SD. Holding that inside one SD needs a step near 0.05 s.
#
# That was put to the project owner and decided on 2026-09-06: the value stays
# here and the timing is accepted (PL-NBCJ). Moving to 0.05 s would double the
# propagations per simulated second and force the interface's tick structure to
# be revisited, and PL-NBWP had by then narrowed what it would buy to 1x
# playback alone - above 1x the interface's own control grid is `multiplier x
# 0.1` s and dominates the step outright. So this is a declared tolerance that
# has been argued rather than a default nobody revisited, and the ventilator
# start being timed to about twice one parameter SD is the accepted cost of it
# rather than an oversight. docs/MODEL.md "Supported simulation step" carries
# the measurements and the whole of the decision.
#
# Both figures are per step of delay, and a *caller* decides how many steps of
# delay a control change waits (PL-NBWP). They are therefore what a caller
# advancing one step per control opportunity sees, which the shipped interface
# is only at 1x playback: it advances a whole tick's worth of steps between
# opportunities, so its own resolution is that many times this one - 30 s and
# up to about 10 pp at 300x, measured over the same manoeuvres. That is a
# property of the caller's loop and not of this constant, which is why the
# number here does not move; but the constant is a floor on the interface's
# resolution rather than a statement of it, and a reader who takes it for the
# latter is reading it as several hundred times better than it is. The whole
# per-rate table is in docs/MODEL.md "Supported simulation step" beside this
# one, and app/playback.py states which grid the interface actually offers.
#
# Every figure quoted above, and this constant's own value, is re-measured from
# the parameter files at each run by tests/reference/test_control_resolution.py.
# Until PL-ZVS7 they were held by this comment and by docs/MODEL.md and by
# nothing else, so moving the model would have left both documents asserting a
# tolerance the code no longer held, with make check passing.
MAXIMUM_SIMULATION_STEP_S = 0.1

# This is the smallest simulation step that `AgentUptakeSystem.advance()` accepts
# (PL-YZ17). It is also the smallest step that a compartment stepped on its own
# accepts (PL-WP52).
#
# Unlike the ceiling above, this bound is numerical. The exact step has no
# truncation error at any step size, so what a finer step costs is rounding:
# each step adds what it changed to what was already stored, and the finer the
# step, the smaller that change is beside the store it is added to, so the same
# rounding is a larger share of it. Measured 2026-10-03 over 10 000 steps from
# 60 s into the default sevoflurane wash-in, what the alveolar, vessel-rich,
# muscle and fat fractions changed by is wrong by at most 3e-12 of itself at
# 1 ms, 7e-9 at 1 us, 1e-4 at 1e-10 s and a third at 1e-14 s, and nothing
# raises at any of them. The growth has no knee, so - as with the ceiling - no
# step is the one at which the answer "becomes wrong", and this constant is
# declared rather than derived.
#
# It is declared at the finest step at which the solution has been shown to match
# the shipped one. That step is the bottom of the step sweep that PL-X9KD took. A
# test beside the step-refinement gate in tests/reference/test_sevo_patient.py
# drives the gate at this step, and pins this constant to the value its figures
# were measured at. Nothing runs finer: apart from the tests of this floor itself,
# the finest step any test takes is 0.02304 s.
#
# It also keeps the run's own arithmetic exact. At this step the supported run
# length is 86 400 000 steps, well inside the 2**53 below which a float holds
# every whole count. Below about 9.6e-12 s a day's count passes that and
# `elapsed_s` would round it before multiplying, and below about 4.8e-304 s the
# run length divided by the step overflows, which `maximum_step_count` met as
# an `OverflowError` from outside the simulator's own exceptions.
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

    This function checks the floor and not the ceiling,
    `MAXIMUM_SIMULATION_STEP_S`. A compartment stepped on its own calls it. Rounding
    error grows as the compartment's step shrinks, but the compartment may take a
    step longer than the run's ceiling (`PL-WP52`).
    `require_supported_simulation_step` calls it too, so the run and the
    compartments refuse a step below the floor with the same message. `name` is the
    step's name. Where several objects can raise the error, `name` starts with the
    step's owner, as `core/validation.py` says of `name`.

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
    """Require a step inside the interval the coupled system is supported over.

    The ceiling belongs to the coupled system rather than to a compartment,
    because it is how long settings are held constant for, which is a property
    of the step the whole system takes. The floor is where the solution has
    been verified. It is checked by `require_at_least_the_smallest_step`, which
    each compartment's own `advance` also calls (`PL-WP52`).

    The step must first be a number. `require_positive_finite`
    (`core/validation.py`) checks this. It refuses a `bool`, a `Decimal` or a
    string with `require_a_number`'s `TypeError`, and it refuses an `int` past
    the float range by name (`PL-3800`). Before that change,
    `SimulationStep(True)` was refused as a step of 1 s, `Decimal('0.05')` was
    converted and held as a step, and `SimulationStep(10**400)` escaped as
    `OverflowError` from `math.isfinite`, outside the simulator's own
    exceptions (`PL-21V4`).

    Raises:
        TypeError: the step is not an `int` or a `float`, or is a `bool`. A
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
        TypeError: `seconds` was built as another checked quantity - an
            instant, a flow, a fraction - which is a swapped argument and is
            refused before the range is read (`core/checked_number.py`,
            `PL-979Z`); or it is not an `int` or a `float`, or is a `bool`,
            as `require_supported_simulation_step` states.
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

    The runtime half of the type, for the callers `mypy` does not read: a test,
    a notebook, or a value typed `Any`. It checks the type and not the range,
    which the constructor has already checked. A value built as another
    checked quantity - an instant, a count, a flow, a concentration - is named
    as that and not told to rebuild, by `require_not_another_quantity`, which
    the constructor asks first as well (`core/checked_number.py`): until
    `PL-848D` a `CaseInstant(0.1)` handed in as the step was told to build
    `SimulationStep(0.1)` from it, which would hold a 0.1 s step built from
    an instant, the swap this refusal exists to catch. The value prints
    through `shown`, so a bare `int` too long for `repr` is named by its
    length rather than escaping as `ValueError` while the refusal is written.

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
