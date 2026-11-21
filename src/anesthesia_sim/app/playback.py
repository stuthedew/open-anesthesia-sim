"""Playback rate: how many one-second steps the run loop takes on each tick.

A run's trajectory depends on its inputs and on the number of steps taken,
and on nothing else (`docs/MODEL.md` § "The reproducibility guarantee").
For a run nobody touches, playing it faster is therefore a *scheduling*
change and never a modelling one. The same steps are taken, in the same
order, at the same size, and more of them are taken per second of real
time. This module is the one place that converts the rate a reader selects
into steps.

For a run in which a control moves, the rate has a cost, which is described
below under "What the rate does change" (`PL-NBWP`).

**Why the interface needs this at all.** At real time, the two compartments
that make uptake and distribution worth teaching cannot be watched.
Sevoflurane's muscle group has a time constant of about 135 min at the
reference settings, and fat has one of about 42 h. So reaching three muscle
time constants takes nearly seven hours in front of the application.
Context-sensitive emergence, which is why a three-hour case wakes
differently from a twenty-minute one, cannot be reached at all
(`PL-SN2C`).

**The step never changes, and it is not this module's to choose.** A run
steps by `SIMULATION_STEP_S`, one second, at every rate
(`core/simulation_step.py`). A larger step at a faster rate would let a
*view* control alter the numbers. Two learners comparing the same case at
different speeds would then see different values. The number of steps taken
per tick is the only quantity here that varies.

**How a tick becomes steps.** The run loop wakes every
`SIMULATION_TICK_INTERVAL_MS` of real time, which is shorter than one step
at real time. So each tick adds `multiplier x tick interval` of simulated
time to what playback owes the run, in whole milliseconds, and the run takes
one step for each whole second owed (`OwedSimulatedTime`). The part of a
second left over is carried to the next tick. At 1x the run takes one step
on every tenth tick, and at 5x one step on every second tick. At 20x, 60x
and 300x it takes 2, 6 and 30 steps on every tick. Every quantity in that
sum is a whole number, so no rounding rule is needed, and over any stretch
of ticks the run has advanced `multiplier` simulated seconds for each real
second, to within one step.

**What the rate does change is the grid of instants at which a live control
action can take effect.** A setting changed while the run is playing first
acts on the next step that the loop takes. At 1x and 5x that step begins at
the next whole second. At a faster rate a tick takes several steps with
nothing between them, so the instants that a change can reach are one
tick's steps apart: 2, 6 and 30 s at 20x, 60x and 300x
(`PlaybackRate.control_grid_s`).

Nothing arrives *late*, and that distinction decides what a reader may
conclude. `ControlChange.elapsed_s` is `SimulationState.elapsed_s` at the
moment of the call, and the new setting acts over the step that begins
there, at every rate. So the recorded timeline is exact, and no displayed
value is stale against it. Only the choice of instants becomes coarser.
`docs/MODEL.md` § "Supported simulation step" measures what one grid step
of that coarsening costs a displayed compartment. At 300x on an abrupt
manoeuvre, the cost is about ten percentage points.

**Pause, change, resume places a change on a chosen whole second at every
rate.** `RunView.step_tick` takes no steps while the run is paused, and this
application's setters apply unconditionally. So a setting changed while
paused acts from the step on which the run resumes. That is the route to
use when *when* a change happened is the point of the exercise. No route
places a change between two whole seconds, because the run holds no instant
there.

**The rate is stated as a multiple of real time, because a reader can
check that.** "60x real time" is a claim about the clock on screen. This
module derives the steps *from* the claimed multiple and the tick interval,
rather than choosing a step count and labelling it afterwards, so the label
cannot drift from the loop.

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
is the host, not the loop. A tick adds a fixed amount of owed time, and
`step_tick` never adds more to catch up. Qt coalesces a timeout that fell due while the loop
was busy, rather than queueing it. So a host that holds the loop past one
interval loses that tick, and the run delivers the nominal rate times the
fraction of ticks that fired. Nothing on screen says so today. The label
is left as it is, and this paragraph records why (project owner,
2026-09-27, ratified, over qualifying the label and over building the
disclosure now). `PL-2NYN` is the guard that would name the delivered rate
beside the set one when fewer than 95% of ticks fire.

That measurement was made when a tick took a fixed number of 0.1 s steps.
The timer and the loss of a late tick are unchanged since `PL-SZ6G`, which
changed only what each tick does.
"""

from dataclasses import dataclass
from typing import Final

from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import SIMULATION_STEP_S
from anesthesia_sim.core.units import MILLISECONDS_PER_SECOND

#: The largest number of steps that one tick may take. A tick runs all of its
#: steps before the interface can respond, so an unbounded count would hang the
#: interface without raising an error (`PL-T6P0`). The bound is set by time,
#: because a tick that outlasts its own interval freezes the interface and
#: plays slower than its label. The shipped tick is 0.1 s of real time, and one
#: step of the running controller measured about 53 microseconds on 2026-10-26.
#: So a tick has room for about 1 900 steps. This bound allows 1 000, about
#: 53 ms, which leaves the rest of the tick for drawing. The fastest offered
#: rate, 300x, takes 30 steps per tick.
#: `test_the_most_steps_one_tick_may_take_covers_every_rate` fails if a faster
#: rate would need more steps than this bound.
MAXIMUM_STEPS_PER_TICK: Final = 1_000

_STEP_MS: Final = SIMULATION_STEP_S * MILLISECONDS_PER_SECOND


@dataclass(frozen=True, slots=True)
class PlaybackRate:
    """How much faster than real time a run is played.

    Attributes:
        multiplier: Simulated seconds advanced per second of real time. `1`
            is real time. Nothing slower than real time is offered, because
            the run holds no instant between two whole seconds, and a slower
            playback would only redraw the same values for longer.

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

    def simulated_ms_per_tick(self, *, tick_interval_ms: int) -> int:
        """Return the simulated time that one tick owes a run at this rate, in milliseconds.

        A tick of `tick_interval_ms` real milliseconds owes the run
        `multiplier` times as much simulated time.

        Args:
            tick_interval_ms: Real milliseconds between two wakeups of the
                run loop, as a whole number of at least 1.

        Raises:
            TypeError: If `tick_interval_ms` is not an `int`, or is a `bool`.
            SimulationConfigurationError: If the tick interval is less than
                1 ms. Also if one tick at this rate would owe more than
                `MAXIMUM_STEPS_PER_TICK` steps, because the interface cannot
                respond until a tick's steps are done (`PL-T6P0`).
        """

        if not isinstance(tick_interval_ms, int) or isinstance(tick_interval_ms, bool):
            raise TypeError(
                "tick_interval_ms must be a whole number of milliseconds, not "
                f"{type(tick_interval_ms).__name__}"
            )

        if tick_interval_ms < 1:
            raise SimulationConfigurationError(
                f"a tick interval is at least 1 ms, not {tick_interval_ms} ms"
            )

        owed_ms = self.multiplier * tick_interval_ms

        if owed_ms > MAXIMUM_STEPS_PER_TICK * _STEP_MS:
            raise SimulationConfigurationError(
                f"playing at {self.multiplier}x real time with a {tick_interval_ms} ms tick "
                f"needs {owed_ms / _STEP_MS:g} steps of {SIMULATION_STEP_S} s per tick, more "
                f"than the {MAXIMUM_STEPS_PER_TICK} one tick may take, because the "
                "interface cannot respond until a tick's steps are done"
            )

        return owed_ms

    def control_grid_s(self, *, tick_interval_ms: int) -> int:
        """Return the longest simulated time between two instants a live control change can reach.

        A change made while the run plays acts on the next step the loop
        takes. The steps of one tick run with nothing between them. So the
        grid is one step where a tick owes one step or less, and otherwise
        the most steps that one tick takes. With the shipped 100 ms tick it
        is 1 s at 1x and 5x, and 2, 6 and 30 s at 20x, 60x and 300x.
        `docs/MODEL.md` § "Supported simulation step" states what one grid
        step costs a displayed compartment at each rate.

        Raises:
            TypeError: As `simulated_ms_per_tick` raises.
            SimulationConfigurationError: As `simulated_ms_per_tick` raises.
        """

        owed_ms = self.simulated_ms_per_tick(tick_interval_ms=tick_interval_ms)
        # Ceiling division on whole numbers. A tick that owes 1.5 steps takes
        # one step and two steps in turn, so its grid is two steps.
        most_steps_in_one_tick = -(-owed_ms // _STEP_MS)

        return max(most_steps_in_one_tick, 1) * SIMULATION_STEP_S


@dataclass(slots=True)
class OwedSimulatedTime:
    """The simulated time that playback owes one run and has not yet stepped.

    Each tick adds the time it owes, and the run takes one step for each
    whole step owed. The remainder is always less than one step, and it is
    carried to the next tick. The amount is held in whole milliseconds, so
    the sum is exact at every rate and tick interval.

    The amount is scheduling state, not model state. It decides only on
    which tick a step is taken. The run's trajectory depends on the number
    of steps taken and on nothing else, so two runs that hold different
    remainders and take the same steps hold the same states.

    Attributes:
        owed_ms: The simulated time owed and not yet stepped, in
            milliseconds. It is at least zero and less than one step.
    """

    owed_ms: int = 0

    def steps_due(self, rate: PlaybackRate, *, tick_interval_ms: int) -> int:
        """Add one tick's simulated time at `rate`, and return how many steps are now due.

        The steps returned are no longer owed after the call, so the caller
        takes all of them.

        Raises:
            TypeError: As `PlaybackRate.simulated_ms_per_tick` raises.
            SimulationConfigurationError: As
                `PlaybackRate.simulated_ms_per_tick` raises. Nothing is added
                in that case.
        """

        owed_ms = self.owed_ms + rate.simulated_ms_per_tick(tick_interval_ms=tick_interval_ms)
        steps, self.owed_ms = divmod(owed_ms, _STEP_MS)

        return steps

    def clear(self) -> None:
        """Owe nothing, as at the start of a run."""

        self.owed_ms = 0


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
#: Each rung faster than 5x also pays for its speed in control resolution
#: (`PlaybackRate.control_grid_s`): 1, 1, 2, 6 and 30 s. So adding a rung also
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
