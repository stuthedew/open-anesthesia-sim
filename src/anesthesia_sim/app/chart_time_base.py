"""How wide the chart's visible window is, and how that window is ruled.

Pure arithmetic over durations, independent of Flet and of the scientific
core. Nothing here reads simulation state, builds a control, or formats a
string: given a run length and a choice, it answers with a width, a pair of
axis bounds and a list of tick positions, and `app/simulation_view.py` draws
them.

**It is a view control and reaches no model state.** Choosing a time base
changes which part of the recorded run is drawn and nothing else - no step is
resized, no sample is discarded, no calculation is re-run. A case watched at
15 minutes and the same case watched at 12 hours are the same run, sample for
sample, which is what keeps `CLAUDE.md`'s determinism requirement untouched by
anything in this module.

**Why the widths are a fixed ladder rather than a free zoom.** `PL-012`
settled it and `PL-SSBP` builds it: the selected duration is the *width* of
the window, so seconds-per-pixel is a property of the choice rather than of
how long the run has been going. A window that grew continuously with the run
would change every trace's apparent slope while the underlying rate did not,
which is a misleading visual encoding of exactly the quantity - rate of rise -
that uptake and distribution are taught by. Discrete steps also make one step
a meaningful change rather than a nudge: each rung is at least half again as
wide as the one below it, and mostly twice.

**Why the ladder reaches below what the selector offers.** The project owner
settled the selectable list at 15 minutes to 12 hours (2026-09-04). "Fit run"
is the default mode and has to answer at ten seconds as well as at ten hours,
so the ladder carries three rungs under that floor: fitting a thirty-second
run to a fifteen-minute axis would draw the whole of induction into the
leftmost 3% of the plot, which is the moment a learner is most likely to be
watching. Those three rungs are reachable by fitting and not by choosing,
because choosing one would be zooming into a span with nothing in it.

**Nothing here assumes twelve hours is the end of the list.** The ladder is
data, and `fit_to_run` continues past its widest rung by doubling rather than
by refusing, so a run longer than any declared width still shows whole. That
matters for the mode's honesty as much as for its reach: "Fit run" that
silently showed the most recent twelve hours of a fourteen-hour case would be
a display asserting something false about what the reader is looking at.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

__all__ = [
    "CHART_LIVE_HEADROOM_FRACTION",
    "FIT_RUN_KEY",
    "SELECTABLE_TIME_BASES",
    "TIME_BASE_LADDER",
    "ChartTimeBase",
    "fit_to_run",
    "fitted_window",
    "following_window",
    "tick_times",
    "time_base_for_span",
]

# How much of the window is kept clear to the right of the newest sample while
# the window is following the run. Proportional rather than a fixed number of
# seconds, so the newest point sits the same distance in from the frame's edge
# at every width - ten seconds of clearance is a fifth of a one-minute axis and
# invisible on a twelve-hour one. It is small enough that the width a reader
# selected is still very nearly the width they are reading.
CHART_LIVE_HEADROOM_FRACTION: Final = 0.02

# What the selector's "Fit run" entry is keyed by. A sentinel rather than a
# width, because fitting is a *rule* for choosing the width each frame and not
# one of the widths it chooses among.
FIT_RUN_KEY: Final = "fit"

# The narrowest width the selector offers. Below this the ladder exists only
# for fitting; see the module docstring.
SELECTABLE_TIME_BASE_FLOOR_S: Final = 900.0


@dataclass(frozen=True, slots=True)
class ChartTimeBase:
    """One rung of the ladder: a window width and the interval it is ruled at.

    The two travel together deliberately. `PL-012` required the gridline
    interval to be derived from the width rather than fixed, because the
    fixed 60 s interval it replaced would rule a twelve-hour axis into 720
    lines and a solid grey block. Pairing them in one record is what makes
    the derivation a fact about the rung rather than a calculation each
    caller repeats: every width on the ladder is ruled into four to six
    intervals, which is the range that reads as a grid rather than as either
    a bare axis or a hatch.
    """

    span_s: float
    """The width of the visible window, in simulated seconds."""

    tick_interval_s: float
    """The interval between gridlines and axis labels, in simulated seconds."""

    @property
    def live_headroom_s(self) -> float:
        """Clearance kept to the right of the newest sample while following.

        `following_window` only. Fitting takes none, and that is not an
        oversight: a fitted window is at least as wide as the run by
        construction, so the clearance is already there, and charging the
        headroom against the fit as well would push a run of exactly fifteen
        minutes onto the thirty-minute rung and draw it across half the plot.
        """

        return self.span_s * CHART_LIVE_HEADROOM_FRACTION


# Every width the chart can take, narrowest first. Widths and their intervals
# are declared rather than computed because both are readability judgments -
# how much of a case a reader wants in one view, and how many lines rule it
# legibly - and neither follows from arithmetic. The three rungs below
# `SELECTABLE_TIME_BASE_FLOOR_S` are reachable only by fitting.
TIME_BASE_LADDER: Final = (
    ChartTimeBase(span_s=60.0, tick_interval_s=15.0),
    ChartTimeBase(span_s=120.0, tick_interval_s=30.0),
    ChartTimeBase(span_s=300.0, tick_interval_s=60.0),
    ChartTimeBase(span_s=900.0, tick_interval_s=180.0),
    ChartTimeBase(span_s=1800.0, tick_interval_s=300.0),
    ChartTimeBase(span_s=3600.0, tick_interval_s=600.0),
    ChartTimeBase(span_s=7200.0, tick_interval_s=1800.0),
    ChartTimeBase(span_s=14400.0, tick_interval_s=3600.0),
    ChartTimeBase(span_s=28800.0, tick_interval_s=7200.0),
    ChartTimeBase(span_s=43200.0, tick_interval_s=7200.0),
)

# What the selector lists, alongside "Fit run": fifteen minutes to twelve
# hours, as the project owner settled on 2026-09-04.
SELECTABLE_TIME_BASES: Final = tuple(
    time_base for time_base in TIME_BASE_LADDER if time_base.span_s >= SELECTABLE_TIME_BASE_FLOOR_S
)


def fit_to_run(run_length_s: float) -> ChartTimeBase:
    """The narrowest width that shows a run of this length whole.

    Half of the "Fit run" mode, which is the default; `fitted_window` is the
    other half. `min_x` stays pinned at zero under it, so the width returned
    here is what decides whether the whole run is on the plot, and it is
    always wide enough that it is.

    Past the widest declared rung the ladder is continued by doubling both
    the width and its interval, rather than by returning the widest rung and
    showing part of the run. Doubling preserves the four-to-six intervals
    every declared rung is ruled into, so a fitted twenty-four-hour axis is
    ruled like a twelve-hour one.

    Args:
        run_length_s: How much simulated time the run has recorded, in
            seconds.

    Returns:
        The rung to draw the run against.

    Raises:
        ValueError: If `run_length_s` is negative or not finite. A run
            length is elapsed simulated time and neither is a length; the
            alternative to raising is an axis drawn against a width nobody
            can account for, which `CLAUDE.md`'s standard prefers a failure
            to.
    """

    if not math.isfinite(run_length_s) or run_length_s < 0.0:
        raise ValueError(f"run length must be finite and non-negative, got {run_length_s!r}")

    for time_base in TIME_BASE_LADDER:
        if time_base.span_s >= run_length_s:
            return time_base

    widest = TIME_BASE_LADDER[-1]
    span_s = widest.span_s
    tick_interval_s = widest.tick_interval_s

    while span_s < run_length_s:
        span_s *= 2.0
        tick_interval_s *= 2.0

    return ChartTimeBase(span_s=span_s, tick_interval_s=tick_interval_s)


def time_base_for_span(span_s: float) -> ChartTimeBase:
    """The declared rung of this width.

    What a selection arriving from the interface is resolved through. It
    raises on a width the ladder does not carry rather than falling back to
    a nearby one: a value that is not on the ladder means the control and
    `TIME_BASE_LADDER` have diverged, which is a defect to surface rather
    than a user error to absorb - the options *are* the ladder.

    Args:
        span_s: The width to look up, in simulated seconds.

    Returns:
        The rung of exactly that width.

    Raises:
        ValueError: If no rung has that width.
    """

    for time_base in TIME_BASE_LADDER:
        if time_base.span_s == span_s:
            return time_base

    raise ValueError(f"no chart time base spans {span_s!r} s")


def fitted_window(time_base: ChartTimeBase) -> tuple[float, float]:
    """The axis bounds of the "Fit run" mode: the whole run, pinned at zero.

    The other half of `fit_to_run`, and trivial by design. It is a named
    rule rather than an expression at the call site because *which* end is
    pinned is the whole difference between the two modes, and a mode
    difference that lives in an inline `max()` is one nobody can find.

    Args:
        time_base: The rung `fit_to_run` chose for this run.

    Returns:
        `(min_x, max_x)` in simulated seconds.
    """

    return 0.0, time_base.span_s


def following_window(time_base: ChartTimeBase, newest_sample_s: float) -> tuple[float, float]:
    """The axis bounds a chosen width shows while it follows the run.

    The width is exactly `time_base.span_s` at every point of every run,
    which is the property the whole design rests on: a trace's slope on the
    plot is then a fixed multiple of its rate, comparable between two moments
    of one run and between two runs. Early in a run the window does not
    shrink to the samples recorded so far - it stays its full width with the
    run occupying the left of it, so a run shorter than the chosen width
    still shows whole - because shrinking it would make the axis rescale
    continuously, which is the encoding `PL-012` rejected.

    Once the run outgrows the width the window slides, keeping the newest
    sample `time_base.live_headroom_s` in from the right edge. Nothing here
    decides *whether* to follow: this is the live-following case, which is
    the only one the interface currently offers. Panning away from the right
    edge, and saying unmistakably that it has happened, is a separate item.

    Args:
        time_base: The rung the reader selected.
        newest_sample_s: Simulated time of the newest recorded sample.

    Returns:
        `(min_x, max_x)` in simulated seconds, exactly `span_s` apart.

    Raises:
        ValueError: If `newest_sample_s` is negative or not finite.
    """

    if not math.isfinite(newest_sample_s) or newest_sample_s < 0.0:
        raise ValueError(
            f"newest sample time must be finite and non-negative, got {newest_sample_s!r}"
        )

    start_s = max(0.0, newest_sample_s + time_base.live_headroom_s - time_base.span_s)

    return start_s, start_s + time_base.span_s


def tick_times(start_s: float, stop_s: float, interval_s: float) -> tuple[float, ...]:
    """Where the gridlines and axis labels fall inside one window.

    Multiples of the interval measured from the run's own start, never from
    the window's left edge. That is what keeps a gridline standing at the
    same simulated time as the window slides underneath it: ticks derived
    from the edge would drift with it, so the grid would crawl and every
    label would be rewritten on every frame.

    Args:
        start_s: Left edge of the window, in simulated seconds.
        stop_s: Right edge of the window, in simulated seconds.
        interval_s: Spacing between ticks, in simulated seconds.

    Returns:
        The tick positions inside `[start_s, stop_s]`, earliest first.

    Raises:
        ValueError: If `interval_s` is not a positive finite number, or if
            the window's edges are not finite and ordered.
    """

    if not math.isfinite(interval_s) or interval_s <= 0.0:
        raise ValueError(f"tick interval must be positive and finite, got {interval_s!r}")

    if not math.isfinite(start_s) or not math.isfinite(stop_s) or stop_s < start_s:
        raise ValueError(f"window must be finite and ordered, got ({start_s!r}, {stop_s!r})")

    first = math.ceil(start_s / interval_s)
    last = math.floor(stop_s / interval_s)

    return tuple(index * interval_s for index in range(first, last + 1))
