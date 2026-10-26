"""Playback rate: how many simulation steps the run loop takes per tick.

A run's trajectory depends on its inputs and on the number of steps taken,
and on nothing else (`docs/MODEL.md` § "The reproducibility guarantee").
For a run nobody touches, playing it faster is therefore a *scheduling*
change and never a modelling one. The same steps are taken, in the same
order, at the same size, with more of them per wakeup of the loop. This
module is the one place that converts the rate a reader selects into that
number of steps.

For a run in which a control moves, the rate has a cost. Until `PL-NBWP`,
the paragraph above said that it had none, without this qualification. The
cost is described below, under "What the rate does change".

**Why the interface needs this at all.** At one step per tick the
simulation advances in real time, and the two compartments that make
uptake and distribution worth teaching cannot be watched. Sevoflurane's
muscle group has a time constant of about 135 min at the reference
settings, and fat has one of about 42 h. So reaching three muscle time
constants takes nearly seven hours in front of the application.
Context-sensitive emergence, which is why a three-hour case wakes
differently from a twenty-minute one, cannot be reached at all
(`PL-SN2C`).

**The step size never changes, and this module exists to enforce that
safety property.** A larger step would let a *view* control alter the
numbers. Two learners comparing the same case at different speeds would
see different values, and the displayed digits would stop meaning what
`docs/MODEL.md` § "Displayed precision" derives them from. The step is
fixed for determinism rather than for accuracy. So a faster playback that
changed the step would not give a slightly coarser answer. It would give a
different run. Steps per tick is the only quantity here that varies.
`simulation_step_s` is an input to the conversion and never an output of
it.

**What the rate does change is the grid of instants at which a live
control action can take effect.** A tick runs its whole burst of steps
with nothing between them, so simulated time moves as a staircase. It
stays still for one real tick interval and then jumps by
`multiplier × tick_interval_s`. A setting changed while the run is playing
therefore first acts at a tick boundary. The simulated instants it can
reach are then `multiplier × 0.1` s apart: 0.1 s at 1×, and 0.5, 2, 6 and
30 s at 5×, 20×, 60× and 300×.

Nothing arrives *late*, and that distinction decides what a reader may
conclude. `ControlChange.elapsed_s` is `SimulationState.elapsed_s` at the
moment of the call, and the new setting acts over the step that begins
there, at every rate. So the recorded timeline is exact to the step, and
no displayed value is stale against it. Only the choice of instants
becomes coarser. `docs/MODEL.md` § "Supported simulation step" measures
what one grid step of that coarsening costs a displayed compartment. At
300× on an abrupt manoeuvre, the cost is percentage points rather than
the hundredths in which the 1× tolerance is stated.

**A control change timed to the step is available at every rate: pause,
change, resume.** `RunView.step_tick` takes no steps while the run is
paused, and this application's setters apply unconditionally. So a setting
changed while paused acts from the step on which the run resumes. That is
the route to use when *when* a change happened is the point of the
exercise. The ladder of rates below is for watching a trajectory, not for
timing one.

**The rate is stated as a multiple of real time, because a reader can
check that.** "60x real time" is a claim about the clock on screen. It is
true only if the loop's tick interval, the simulation step and the steps
taken per tick agree. This module derives the step count *from* the
claimed multiple, rather than choosing a step count and labelling it
afterwards, so the label cannot drift from the loop. A rate that does not
give a whole number of steps is refused rather than rounded. A tick of
59.5 steps would either take a step of a different size or silently play
at a rate other than the one displayed. Both are the failure this module
is here to prevent.

**The claim was measured on the shipped loop, and it is true** (`PL-SQJ1`,
2026-09-27). `RunView._step_timer` is a `QTimer` of type `PreciseTimer` on
`SIMULATION_TICK_INTERVAL_S`. It fires `step_tick` on its interval
however long painting takes. The measurement ran with the real dashboard
shown on the offscreen platform and both timers running as `main.py` runs
them. Every rung from 1x to 300x delivered 99.0 to 99.9% of its nominal rate over
8 to 30 s of wall clock. The tick period stayed at 100 ms to within 4 ms at
its worst. The shortfall that remains comes from the measurement itself,
because the first tick fires one interval after the start. The 73 to 91%
that the item was filed on came from Flet, the earlier toolkit, whose
single asyncio loop serialized both cadences behind `page.update()`. That
shortfall went away with the toolkit. What can still make the label false
is the host, not the loop. `step_tick` takes a fixed burst and never takes
extra steps to catch up. Qt coalesces a timeout that fell due while the loop
was busy, rather than queueing it. So a host that holds the loop past one
interval loses that tick, and the run delivers the nominal rate times the
fraction of ticks that fired. Nothing on screen says so today. The label
is left as it is, and this paragraph records why (project owner,
2026-09-27, ratified, over qualifying the label and over building the
disclosure now). `PL-2NYN` is the guard that would name the delivered rate
beside the set one when fewer than 95% of ticks fire.
"""

import math
from dataclasses import dataclass
from typing import Final

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import SimulationStep, require_simulation_step
from anesthesia_sim.core.validation import require_positive_finite

#: How far the derived step count may be from a whole number and still be
#: treated as that whole number. The conversion is a ratio of two float
#: intervals, so an exact comparison would refuse a configuration that is
#: correct and merely inexact in binary. This tolerance is loose enough to
#: absorb that error. It is far too tight to absorb a truly fractional rate,
#: because the nearest such rate is half a step away from a whole number.
STEP_COUNT_TOLERANCE: Final = 1e-9

#: The most steps one tick may take. A tick runs its whole burst before the
#: interface can respond, so a count with no bound is a hang with no error
#: (`PL-T6P0`). The shipped loop takes at most 300 steps per tick: the fastest
#: offered rate, 300x, with a tick one 0.1 s step long. Even at the smallest
#: step that `core/simulation_step.py` supports, 1 ms, that rate and tick need
#: 30 000 steps. This bound leaves a margin of about three over that, and
#: `test_the_most_steps_one_tick_may_take_covers_every_rate_at_the_smallest_step`
#: fails if a faster rate or a slower tick would need more.
MAXIMUM_STEPS_PER_TICK: Final = 100_000


@dataclass(frozen=True, slots=True)
class PlaybackRate:
    """How much faster than real time a run is played.

    Attributes:
        multiplier: Simulated seconds advanced per second of real time. `1`
            is real time. Nothing slower than real time is offered, because
            the model resolves nothing shorter than the 0.1 s step, and a
            slower playback would only redraw the same values for longer.

    Raises:
        SimulationConfigurationError: If `multiplier` is not a whole number,
            is a `bool`, or is less than 1.
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

    def steps_per_tick(self, *, tick_interval_s: float, simulation_step_s: SimulationStep) -> int:
        """Return how many steps one tick takes to play at this rate.

        A tick of `tick_interval_s` real seconds must advance
        `multiplier * tick_interval_s` simulated seconds, and each step
        advances `simulation_step_s` of them.

        Args:
            tick_interval_s: Real seconds the run loop waits between
                wakeups. Must be positive.
            simulation_step_s: Simulated seconds that one step advances, as
                the `SimulationStep` the run uses. It is left unchanged in
                every case. This method decides how many steps a tick takes,
                and never how large a step is.

        Returns:
            The whole number of steps, at least one.

        Raises:
            TypeError: If `tick_interval_s` is not an `int` or a `float`, or
                is a `bool`. Also if `simulation_step_s` is not a
                `SimulationStep`, so nothing has checked it against `core`'s
                supported range (`core/simulation_step.py`).
            SimulationConfigurationError: If the tick interval is not
                positive and finite, as `core.validation.require_positive_finite`
                checks (`PL-F9TC`). Also if the step count that these give is
                more than `MAXIMUM_STEPS_PER_TICK`. An enormous tick used to
                raise a bare `OverflowError` once the count could not be
                counted (`PL-YZ17`), and a large count that could be counted
                was returned, so the run loop would have stepped for ever
                (`PL-T6P0`). Also if
                this rate does not land on a whole number of steps at these
                intervals. The refusal is deliberate. The alternatives are a
                step of a different size, or a run that plays at a rate other
                than the one displayed.
        """

        require_positive_finite("tick_interval_s", tick_interval_s)
        require_simulation_step(simulation_step_s)

        exact = self.multiplier * tick_interval_s / simulation_step_s

        # The count is compared after rounding, so a ratio that lands a rounding
        # error above the bound, and would be returned as the bound, is not
        # refused. An infinite ratio cannot be rounded and is refused first.
        if not math.isfinite(exact) or round(exact) > MAXIMUM_STEPS_PER_TICK:
            raise SimulationConfigurationError(
                f"playing at {self.multiplier}x real time with a {tick_interval_s} s tick "
                f"and a {simulation_step_s} s step needs {exact:g} steps per tick, more "
                f"than the {MAXIMUM_STEPS_PER_TICK} one tick may take, because the "
                "interface cannot respond until a tick's steps are done"
            )

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
#: Each is a round number that a reader can remember, and the ladder is
#: chosen by what a reader wants to *watch* rather than by arithmetic
#: regularity. In about three minutes of real time, 1x shows three minutes
#: of case, 5x fifteen minutes, 20x an hour, 60x a three-hour case end to
#: end, and 300x fifteen hours. Fifteen hours is past three time constants
#: of the muscle group (about 6.75 h), and the muscle group is the
#: compartment that `PL-SN2C` exists to make reachable. 60x and 300x can
#: also be said in a phrase: one simulated minute per second, and five.
#:
#: Nothing faster is offered. Fat's time constant is about 42 h, so no rate
#: that keeps the chart legible reaches three of them. A ladder that implied
#: otherwise would promise a run that the reader cannot follow.
#:
#: Each rung also pays for its speed in control resolution, at `multiplier x
#: 0.1` simulated seconds: 0.1, 0.5, 2, 6 and 30 s. So adding a rung also
#: adds a row to `docs/MODEL.md` § "Supported simulation step", and
#: `test_the_control_grid_at_each_rate_is_the_one_two_documents_publish`
#: fails until that row has been written.
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
    """Return the supported rate with this multiplier.

    Args:
        multiplier: Simulated seconds per real second, as one of
            `SUPPORTED_PLAYBACK_RATES` carries it.

    Returns:
        The matching supported rate.

    Raises:
        SimulationConfigurationError: If no supported rate has that
            multiplier. A rate that is not offered but reaches the loop
            means that the control and this list have diverged. That is a
            defect to surface rather than a value to accept.
    """

    for rate in SUPPORTED_PLAYBACK_RATES:
        if rate.multiplier == multiplier:
            return rate

    offered = ", ".join(str(rate.multiplier) for rate in SUPPORTED_PLAYBACK_RATES)

    raise SimulationConfigurationError(
        f"{multiplier!r} is not one of the playback rates this interface offers ({offered})"
    )
