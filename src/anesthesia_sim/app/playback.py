"""Playback rate: how many simulation steps the run loop takes per tick.

A run's trajectory is a function of its inputs and of the number of steps
taken, and of nothing else (`docs/MODEL.md` § "The reproducibility
guarantee"). For a run nobody touches, playing it faster is therefore a
*scheduling* change and never a modelling one: the same steps are taken, in
the same order, at the same size — more of them per wakeup of the loop. This
module is the one place that converts the rate a reader selects into that
number of steps.

For a run in which a control moves, the rate is not free, and until
`PL-NBWP` the sentence above said it was without the qualification. What it
costs is below, under "What the rate does change".

**Why the interface needs this at all.** At one step per tick the
simulation advances in real time, and the two compartments that make
uptake and distribution worth teaching cannot be watched. Sevoflurane's
muscle group has a time constant of about 135 min at the reference
settings and fat about 42 h, so reaching three muscle time constants takes
nearly seven hours in front of the application, and context-sensitive
emergence — why a three-hour case wakes differently from a twenty-minute
one — is unreachable (`PL-SN2C`).

**The step size is never what changes, and that is the safety property
this module exists to hold.** A larger step would be a *view* control
altering the numbers: two learners comparing the same case at different
speeds would read different values, and the displayed digits would stop
meaning what `docs/MODEL.md` § "Displayed precision" derives them from.
The step is fixed for determinism rather than for accuracy, so a faster
playback that moved it would not be a slightly coarser answer — it would
be a different run. Steps per tick is the only quantity here that varies;
`simulation_step_s` is an input to the conversion and never an output of
it.

**What the rate does change is the grid a live control action can land
on.** A tick advances its whole burst with nothing between the steps, so
simulated time is a staircase: it stands still for one real tick interval
and then jumps by `multiplier × tick_interval_s`. A setting changed while
the run is playing therefore first acts at a tick boundary, which spaces
the reachable simulated instants `multiplier × 0.1` s apart — 0.1 s at 1×,
and 0.5, 2, 6 and 30 s at 5×, 20×, 60× and 300×.

Nothing arrives *late*, and the distinction decides what a reader may
conclude. `ControlChange.elapsed_s` is `SimulationState.elapsed_s` at the
moment of the call and the new setting acts over the step beginning there,
at every rate, so the recorded timeline is exact to the step and no
displayed value is stale against it. What coarsens is only which instants
can be chosen. `docs/MODEL.md` § "Supported simulation step" measures what
one grid step of that costs a displayed compartment, which at 300× on an
abrupt manoeuvre is percentage points rather than the hundredths the 1×
tolerance is stated in.

**A control change timed to the step is available at every rate: pause,
change, resume.** `SimulationView._run_simulation_timer` takes no steps
while the run is paused and this application's setters apply
unconditionally, so a setting changed while paused acts from the step the
run resumes on. That is the route when *when* a change happened is the
point of the exercise; the ladder below is for watching a trajectory
rather than for timing one.

**The rate is stated as a multiple of real time, because that is what a
reader can check.** "60x real time" is a claim about the clock on screen,
and it is true only if the loop's tick interval, the simulation step and
the steps taken per tick agree. Deriving the step count *from* the claimed
multiple — rather than choosing a step count and labelling it afterwards —
is what makes the label unable to drift from the loop. A rate that does
not land on a whole number of steps is refused rather than rounded: a
tick that took 59.5 steps would either take a step of a different size or
silently play at a rate other than the one displayed, and both are the
failure this module is here to prevent.
"""

import math
from dataclasses import dataclass
from typing import Final

from anesthesia_sim.core.exceptions import SimulationConfigurationError

#: How far the derived step count may sit from a whole number and still be
#: treated as that whole number. The conversion is a ratio of two float
#: intervals, so an exact comparison would refuse a configuration that is
#: correct and merely inexact in binary; this is loose enough to absorb that
#: and far too tight to absorb a genuinely fractional rate, the nearest of
#: which is half a step out.
STEP_COUNT_TOLERANCE: Final = 1e-9


@dataclass(frozen=True, slots=True)
class PlaybackRate:
    """How much faster than real time a run is played.

    Attributes:
        multiplier: Simulated seconds advanced per second of real time. `1`
            is real time; nothing slower than real time is offered, because
            the model resolves nothing below the 0.1 s step and a slower
            playback would only redraw the same values for longer.
    """

    multiplier: int

    def __post_init__(self) -> None:
        if not isinstance(self.multiplier, int) or isinstance(self.multiplier, bool):
            raise SimulationConfigurationError(
                f"a playback multiplier is a whole number of simulated seconds per real "
                f"second, not {self.multiplier!r}"
            )

        if self.multiplier < 1:
            raise SimulationConfigurationError(
                f"a playback multiplier is at least 1 (real time), not {self.multiplier}"
            )

    def steps_per_tick(self, *, tick_interval_s: float, simulation_step_s: float) -> int:
        """How many steps one tick takes to play at this rate.

        A tick of `tick_interval_s` real seconds must advance
        `multiplier * tick_interval_s` simulated seconds, and each step
        advances `simulation_step_s` of them.

        Args:
            tick_interval_s: Real seconds the run loop waits between
                wakeups. Must be positive.
            simulation_step_s: Simulated seconds one step advances. Must be
                positive, and is returned to the caller unchanged in every
                case — this method decides how many steps a tick takes and
                never how large one is.

        Returns:
            The whole number of steps, at least one.

        Raises:
            SimulationConfigurationError: If either interval is not
                positive, or if this rate does not land on a whole number
                of steps at these intervals. Refusing is the point: the
                alternatives are a step of a different size or a run
                playing at a rate other than the one displayed.
        """

        if tick_interval_s <= 0.0 or not math.isfinite(tick_interval_s):
            raise SimulationConfigurationError(
                f"tick_interval_s must be a positive number of real seconds, "
                f"not {tick_interval_s!r}"
            )

        if simulation_step_s <= 0.0 or not math.isfinite(simulation_step_s):
            raise SimulationConfigurationError(
                f"simulation_step_s must be a positive number of simulated seconds, "
                f"not {simulation_step_s!r}"
            )

        exact = self.multiplier * tick_interval_s / simulation_step_s
        steps = round(exact)

        if steps < 1 or not math.isclose(exact, steps, rel_tol=STEP_COUNT_TOLERANCE):
            raise SimulationConfigurationError(
                f"playing at {self.multiplier}x real time with a {tick_interval_s} s tick "
                f"and a {simulation_step_s} s step needs {exact} steps per tick, which is "
                "not a whole number of steps; the step size is fixed, so this rate cannot "
                "be played exactly"
            )

        return steps


#: The rates the interface offers, slowest first.
#:
#: Each is a round number a reader can hold, and the ladder is chosen by
#: what one wants to *watch* rather than by arithmetic regularity. In about
#: three minutes of real time: 1x shows three minutes of case, 5x fifteen
#: minutes, 20x an hour, 60x a three-hour case end to end, and 300x fifteen
#: hours - past three time constants of the muscle group (about 6.75 h),
#: which is the compartment `PL-SN2C` exists to make reachable. 60x and
#: 300x also state themselves in a phrase: one simulated minute per second,
#: and five.
#:
#: Nothing faster is offered. Fat's time constant is about 42 h, so no rate
#: that leaves the chart legible reaches three of them, and a ladder that
#: implied otherwise would be promising a run the reader cannot follow.
#:
#: Each rung also buys its speed with control resolution, at `multiplier x
#: 0.1` simulated seconds: 0.1, 0.5, 2, 6 and 30 s. Adding a rung therefore
#: adds a row to `docs/MODEL.md` § "Supported simulation step", and
#: `test_the_control_grid_at_each_rate_is_the_one_two_documents_publish`
#: fails until it has been written.
SUPPORTED_PLAYBACK_RATES: Final[tuple[PlaybackRate, ...]] = (
    PlaybackRate(1),
    PlaybackRate(5),
    PlaybackRate(20),
    PlaybackRate(60),
    PlaybackRate(300),
)

#: Real time. A run opens playing at the rate its clock claims, so a reader
#: who never touches the control is never in a mode they did not choose.
DEFAULT_PLAYBACK_RATE: Final = SUPPORTED_PLAYBACK_RATES[0]


def playback_rate_for(multiplier: int) -> PlaybackRate:
    """The supported rate with this multiplier.

    Args:
        multiplier: Simulated seconds per real second, as one of
            `SUPPORTED_PLAYBACK_RATES` carries it.

    Returns:
        The matching supported rate.

    Raises:
        SimulationConfigurationError: If no supported rate has that
            multiplier. An unoffered rate reaching the loop means the
            control and this list have diverged, which is a defect to
            surface rather than a value to accept.
    """

    for rate in SUPPORTED_PLAYBACK_RATES:
        if rate.multiplier == multiplier:
            return rate

    offered = ", ".join(str(rate.multiplier) for rate in SUPPORTED_PLAYBACK_RATES)

    raise SimulationConfigurationError(
        f"{multiplier!r} is not one of the playback rates this interface offers ({offered})"
    )
