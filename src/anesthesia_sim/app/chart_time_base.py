"""How wide the chart's visible window is, and how that window is ruled.

This module does pure arithmetic over simulated time. It is independent of any
toolkit and of the scientific core. Nothing here reads simulation state, builds
a control, or formats a string. Given the newest instant on the chart and a
choice, it returns a width, a pair of axis bounds and a list of tick positions,
and `app/qt_chart.py` draws them.

**It is a view control and changes no model state.** Choosing a time base
changes only which part of the run is drawn. No step is resized, no state is
discarded, and no calculation is re-run. A case watched at 15 minutes and the
same case watched at 12 hours are the same run, step for step. So nothing in
this module can affect `CLAUDE.md`'s determinism requirement.

**Why the widths are a fixed ladder rather than a free zoom.** `PL-012` made
the decision and `PL-SSBP` builds it. The selected duration is the *width* of
the window, so seconds-per-pixel depends on the choice rather than on how long
the run has been going. If the window grew continuously with the run, every
trace's apparent slope would change while the underlying rate did not. That
would be a misleading visual encoding of rate of rise, which is exactly the
quantity that uptake and distribution are taught by. Discrete steps also make
one step a meaningful change rather than a nudge. Each rung is at least half
again as wide as the one below it, and most are twice as wide.

**Why the ladder reaches below what the selector offers.** The project owner
set the selectable list at 15 minutes to 12 hours (2026-09-04). "Fit run" is
the default mode and has to work at ten seconds as well as at ten hours. So the
ladder carries three rungs below 15 minutes. Fitting a thirty-second run to a
fifteen-minute axis would draw the whole of induction into the leftmost 3% of
the plot, and induction is the moment a learner is most likely to be watching.
Those three rungs can be reached by fitting but not by choosing, because
choosing one would zoom into a span with nothing in it.

**Nothing here assumes twelve hours is the end of the list.** The ladder is
data. `fit_to_run` continues past its widest rung by doubling rather than by
refusing, so a case that has run past every declared width still shows whole.
That matters for the mode's honesty as much as for its reach. If "Fit run"
silently showed the most recent twelve hours of a fourteen-hour case, the
display would be asserting something false about what the reader is looking at.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

from anesthesia_sim.core.supported_ranges import CaseInstant, require_case_instant

__all__ = [
    "CHART_LIVE_HEADROOM_FRACTION",
    "FIT_RUN_KEY",
    "SELECTABLE_TIME_BASES",
    "TIME_BASE_LADDER",
    "ChartTimeBase",
    "fit_to_run",
    "fitted_window",
    "following_window",
    "saved_time_base",
    "saved_time_base_value",
    "tick_times",
    "time_base_for_span",
]

# The fraction of the window kept clear to the right of the newest instant while
# the window is following the run. It is proportional rather than a fixed number
# of seconds, so the newest point sits the same distance in from the frame's edge
# at every width. Ten seconds of clearance would be a fifth of a one-minute axis
# and invisible on a twelve-hour one. The fraction is small enough that the width
# a reader selected is still very nearly the width they are reading.
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
        """Clearance kept to the right of the newest instant while following the run.

        Only `following_window` uses it. Fitting takes no clearance, and that
        is not an oversight. A fitted window is at least as wide as the run by
        construction, so the clearance is already there. Charging the headroom
        against the fit as well would push a run of exactly fifteen minutes
        onto the thirty-minute rung and draw it across half the plot.
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


def fit_to_run(newest_instant_s: CaseInstant) -> ChartTimeBase:
    """Return the narrowest width that shows the case whole, from induction to its newest instant.

    This function is half of the "Fit run" mode, which is the default.
    `fitted_window` is the other half. Under that mode `min_x` stays pinned at
    the case's zero. So the width returned here decides whether the whole case
    is on the plot, and it is always wide enough that it is.

    **It is given an instant, not a length.** The window starts at induction
    rather than at the opening of any one run, so its width has to reach the
    newest instant on the case's axis. On a trunk, that instant is also the
    run's length. On a branch it is not. A branch forked at 900 s and advanced
    60 s stands at 960 s, and a width fitted to its 60 s would end the axis
    before the branch began (`PL-59WB`).

    Past the widest declared rung, the ladder is continued by doubling both
    the width and its interval. The function does not return the widest rung
    and show only part of the run. Doubling keeps the four to six intervals
    that every declared rung is divided into, so a fitted twenty-four-hour
    axis is ruled like a twelve-hour one.

    Args:
        newest_instant_s: The instant at which the furthest-advanced run on
            the chart stands, in seconds on the case's axis. It is the same
            value that `following_window` is given. It is a `CaseInstant`, so
            it is finite and inside the supported run length (`PL-9DF9`).

    Returns:
        The rung to draw the case against.

    Raises:
        TypeError: If `newest_instant_s` was not built as a `CaseInstant`.
            This is the one function here that checks the instant again. Its
            doubling loop would never end for an infinite instant, and a NaN
            would return the widest rung without containing the run, so a
            caller that the type checker does not read gets a refusal rather
            than a hang.
    """

    require_case_instant("newest_instant_s", newest_instant_s)

    for time_base in TIME_BASE_LADDER:
        if time_base.span_s >= newest_instant_s:
            return time_base

    widest = TIME_BASE_LADDER[-1]
    span_s = widest.span_s
    tick_interval_s = widest.tick_interval_s

    while span_s < newest_instant_s:
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


def saved_time_base(saved: object) -> ChartTimeBase | None:
    """Return the time base that a chart saved as `saved`, or None for "Fit run".

    `app/views.py` reads a chart View's saved state through this function. The
    saved form is `FIT_RUN_KEY` for "Fit run", or the width in seconds, as
    `saved_time_base_value` writes it. Only a width that the selector offers is
    accepted, because a chart can be set only to a width its control can show.

    Args:
        saved: The value read from the saved state.

    Returns:
        The `ChartTimeBase` of that width, or None for "Fit run".

    Raises:
        ValueError: If `saved` is neither `FIT_RUN_KEY` nor the width in
            seconds of one of `SELECTABLE_TIME_BASES`. A `bool` is rejected,
            even though Python treats True as 1.
    """

    if isinstance(saved, str) and saved == FIT_RUN_KEY:
        return None

    if not isinstance(saved, bool) and isinstance(saved, int | float):
        for time_base in SELECTABLE_TIME_BASES:
            if time_base.span_s == saved:
                return time_base

    raise ValueError(f"no chart time base the selector offers is saved as {saved!r}")


def saved_time_base_value(time_base: ChartTimeBase | None) -> str | float:
    """How a chart saves `time_base`: `FIT_RUN_KEY` for None ("Fit run"), else the width in seconds.

    `saved_time_base` reads the value back.
    """

    return FIT_RUN_KEY if time_base is None else time_base.span_s


def fitted_window(time_base: ChartTimeBase) -> tuple[float, float]:
    """The axis bounds of the "Fit run" mode: the whole case, pinned at induction.

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


def following_window(
    time_base: ChartTimeBase, newest_instant_s: CaseInstant
) -> tuple[float, float]:
    """Return the axis bounds that a chosen width shows while the window follows the run.

    The width is exactly `time_base.span_s` at every point of every run, and
    the whole design rests on that property. A trace's slope on the plot is
    then a fixed multiple of its rate, so it can be compared between two
    moments of one run and between two runs. Early in a run, the window does
    not shrink to the part of the run simulated so far. It stays at its full
    width with the run occupying the left part of it, so a run shorter than
    the chosen width still shows whole. Shrinking the window would make the
    axis rescale continuously, which is the encoding `PL-012` rejected.

    Once the run outgrows the width, the window slides and keeps the newest
    instant `time_base.live_headroom_s` in from the right edge. Nothing here
    decides *whether* to follow. This function handles the live-following
    case, which is the only one the interface currently offers. Panning away
    from the right edge, and showing unmistakably that it has happened, is a
    separate item.

    Args:
        time_base: The rung the reader selected.
        newest_instant_s: The instant at which the furthest-advanced run
            stands. It is a `CaseInstant`, checked where
            `assemble_chart_frame` reads it.

    Returns:
        `(min_x, max_x)` in simulated seconds, exactly `span_s` apart.
    """

    start_s = max(0.0, newest_instant_s + time_base.live_headroom_s - time_base.span_s)

    return start_s, start_s + time_base.span_s


def tick_times(start_s: float, stop_s: float, interval_s: float) -> tuple[float, ...]:
    """Where the gridlines and axis labels fall inside one window.

    Multiples of the interval measured from the case's zero, never from
    the window's left edge - and from the case's zero rather than from any one
    run's opening, so a trunk and a branch drawn on one axis are ruled by the
    same gridlines. `docs/MODEL.md` § "Minimum displayed outputs" states the
    same rule. That is what keeps a gridline standing at the
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
