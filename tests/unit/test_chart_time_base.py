"""Unit tests for `app/chart_time_base.py`, the chart's window width.

The ladder, the two window rules and the tick placement, checked without
constructing a Flet interface. What the *interface* does with them - which
control selects a width, what the axis labels read, what the caption claims -
is in `tests/unit/test_simulation_view.py`.

`PL-012` decided this design and `PL-SSBP` built it. Three of its
requirements are properties rather than examples, so they are asserted over
the whole ladder rather than at a chosen rung: the window is exactly as wide
as the time base at every moment of every run, "Fit run" always contains the
run, and the gridline interval is derived from the width rather than fixed.
"""

import math

import pytest

from anesthesia_sim.app.chart_time_base import (
    CHART_LIVE_HEADROOM_FRACTION,
    SELECTABLE_TIME_BASE_FLOOR_S,
    SELECTABLE_TIME_BASES,
    TIME_BASE_LADDER,
    ChartTimeBase,
    fit_to_run,
    fitted_window,
    following_window,
    tick_times,
    time_base_for_span,
)


def test_the_ladder_climbs_and_never_nudges() -> None:
    """Each rung is a meaningfully wider view, not a slightly wider one.

    The project owner's requirement (2026-09-04): discrete steps,
    geometrically spaced, so choosing the next one is a decision rather than
    a drag. Half again is the floor the ladder is built to; most steps
    double.
    """

    for narrower, wider in zip(TIME_BASE_LADDER, TIME_BASE_LADDER[1:], strict=False):
        assert wider.span_s >= narrower.span_s * 1.5


def test_every_rung_is_ruled_into_between_four_and_six_intervals() -> None:
    """The gridline interval is derived from the width, and legibly.

    `PL-012`'s requirement is that it be derived at all - the fixed 60 s
    interval it replaced would rule the twelve-hour rung into 720 lines.
    The bounds are what makes the derivation a grid rather than either a
    bare axis or a hatch, at every width the chart can take.
    """

    for time_base in TIME_BASE_LADDER:
        intervals = time_base.span_s / time_base.tick_interval_s

        assert intervals == int(intervals), f"{time_base} does not divide evenly"
        assert 4 <= intervals <= 6, f"{time_base} is ruled into {intervals} intervals"


def test_the_selector_offers_fifteen_minutes_to_twelve_hours() -> None:
    """The list the project owner settled on 2026-09-04.

    The ladder reaches below the floor for "Fit run"'s sake and those rungs
    are deliberately not offered, so this pins both halves: what is listed,
    and that nothing below the floor is.
    """

    assert [time_base.span_s for time_base in SELECTABLE_TIME_BASES] == [
        900.0,
        1800.0,
        3600.0,
        7200.0,
        14400.0,
        28800.0,
        43200.0,
    ]
    assert all(
        time_base.span_s >= SELECTABLE_TIME_BASE_FLOOR_S for time_base in SELECTABLE_TIME_BASES
    )


def test_fitting_a_run_always_contains_it() -> None:
    """ "Fit run" that showed part of the run would be a false claim.

    The mode's name is what a reader trusts about what they are looking at,
    so containment is asserted across the ladder's boundaries and past its
    widest rung rather than at a convenient length.
    """

    lengths = [0.0, 0.1, 59.9, 60.0, 60.1, 899.9, 900.0, 900.1, 43_200.0, 43_200.1, 500_000.0]

    for run_length_s in lengths:
        time_base = fit_to_run(run_length_s)
        window_start_s, window_stop_s = fitted_window(time_base)

        assert window_start_s == 0.0
        assert window_stop_s >= run_length_s


def test_fitting_takes_the_narrowest_width_that_holds_the_run() -> None:
    """A wider one would draw the run into part of the plot for no reason."""

    assert fit_to_run(0.0).span_s == 60.0
    assert fit_to_run(60.0).span_s == 60.0
    assert fit_to_run(60.1).span_s == 120.0
    assert fit_to_run(900.0).span_s == 900.0
    assert fit_to_run(3_600.0).span_s == 3_600.0
    assert fit_to_run(43_200.0).span_s == 43_200.0


def test_fitting_past_the_widest_rung_doubles_rather_than_giving_up() -> None:
    """The ladder is not allowed to assume twelve hours is the end of it.

    `PL-SSBP`'s brief: the list grows toward days and weeks later, and
    nothing in the design should assume otherwise. Returning the widest rung
    instead would leave "Fit run" quietly showing the most recent twelve
    hours of a longer case, which is the mode asserting something false.
    """

    widest = TIME_BASE_LADDER[-1]
    beyond = fit_to_run(widest.span_s * 3.0)

    assert beyond.span_s == widest.span_s * 4.0
    # Doubled together, so the wider axis is ruled like every declared rung.
    assert beyond.span_s / beyond.tick_interval_s == widest.span_s / widest.tick_interval_s


def test_a_chosen_width_is_held_exactly_at_every_point_of_a_run() -> None:
    """The property the whole design rests on.

    Seconds-per-pixel is constant, so a trace's slope means the same thing
    at the start of a run and an hour in. A window that grew with the run
    would change every apparent rate while no modelled rate moved, which is
    the misleading encoding `PL-012` rejected.
    """

    for time_base in SELECTABLE_TIME_BASES:
        for newest_sample_s in (0.0, 1.0, time_base.span_s, time_base.span_s * 10.0):
            window_start_s, window_stop_s = following_window(time_base, newest_sample_s)

            assert window_stop_s - window_start_s == pytest.approx(time_base.span_s)


def test_a_run_shorter_than_the_chosen_width_still_shows_whole() -> None:
    """`PL-SSBP`'s "Done when", and the reason the window does not shrink.

    The axis stays its full width with the run occupying the left of it,
    rather than shrinking to the samples recorded so far.
    """

    time_base = time_base_for_span(900.0)

    for newest_sample_s in (0.0, 10.0, 400.0, 880.0):
        window_start_s, window_stop_s = following_window(time_base, newest_sample_s)

        assert window_start_s == 0.0
        assert window_stop_s == 900.0


def test_a_chosen_width_follows_the_run_once_it_is_outgrown() -> None:
    """Past the width the window slides, keeping the newest sample in view."""

    time_base = time_base_for_span(900.0)
    headroom_s = 900.0 * CHART_LIVE_HEADROOM_FRACTION
    window_start_s, window_stop_s = following_window(time_base, 5_000.0)

    assert window_stop_s == pytest.approx(5_000.0 + headroom_s)
    assert window_start_s == pytest.approx(5_000.0 + headroom_s - 900.0)


def test_fitting_charges_no_headroom_so_a_run_stays_on_its_own_rung() -> None:
    """A fifteen-minute run belongs on the fifteen-minute rung.

    Charging the live headroom against the fit as well would push it onto
    the thirty-minute rung and draw the whole run across half the plot, one
    step before the run reaches that width anyway.
    """

    assert fit_to_run(900.0) is time_base_for_span(900.0)


def test_ticks_stand_at_absolute_times_rather_than_at_the_window_s_edge() -> None:
    """A gridline must not crawl as the window slides underneath it.

    Ticks measured from the left edge would move with it, so the grid would
    drift and every label would be rewritten on every frame - the per-frame
    churn the axis-label guard in `simulation_view.py` exists to avoid.
    """

    assert tick_times(0.0, 900.0, 180.0) == (0.0, 180.0, 360.0, 540.0, 720.0, 900.0)
    assert tick_times(100.0, 1_000.0, 180.0) == (180.0, 360.0, 540.0, 720.0, 900.0)
    assert tick_times(181.0, 359.0, 180.0) == ()


def test_ticks_include_a_window_edge_that_falls_exactly_on_one() -> None:
    """Both ends are inclusive; the fitted window's own ends are ticks."""

    assert tick_times(180.0, 540.0, 180.0) == (180.0, 360.0, 540.0)


@pytest.mark.parametrize("run_length_s", [-1.0, -0.001, math.nan, math.inf])
def test_fitting_refuses_a_run_length_that_is_not_one(run_length_s: float) -> None:
    """An axis drawn against a width nobody can account for is worse than none.

    `CLAUDE.md`'s standard prefers an obvious failure to a plausible-looking
    displayed value, and the window's width is what every drawn time is read
    against.
    """

    with pytest.raises(ValueError, match="finite and non-negative"):
        fit_to_run(run_length_s)


@pytest.mark.parametrize("newest_sample_s", [-1.0, math.nan, math.inf])
def test_following_refuses_a_sample_time_that_is_not_one(newest_sample_s: float) -> None:
    """Same rule on the other window: a bad edge is a failure, not a default."""

    with pytest.raises(ValueError, match="finite and non-negative"):
        following_window(time_base_for_span(900.0), newest_sample_s)


@pytest.mark.parametrize("interval_s", [0.0, -60.0, math.nan, math.inf])
def test_tick_placement_refuses_an_interval_that_would_not_rule_anything(interval_s: float) -> None:
    """A non-positive interval is an unruled axis or an infinite loop."""

    with pytest.raises(ValueError, match="positive and finite"):
        tick_times(0.0, 900.0, interval_s)


def test_tick_placement_refuses_a_window_that_runs_backwards() -> None:
    """An inverted window means the two edges came from different frames."""

    with pytest.raises(ValueError, match="finite and ordered"):
        tick_times(900.0, 0.0, 180.0)


def test_a_width_the_ladder_does_not_carry_is_refused_rather_than_rounded() -> None:
    """A selection off the ladder is a defect in the control, not a user error.

    Falling back to the nearest width would draw the chart at a span the
    control does not claim and nothing on the display would say so.
    """

    with pytest.raises(ValueError, match="no chart time base spans"):
        time_base_for_span(1_000.0)


def test_a_time_base_is_immutable() -> None:
    """A width that could be edited in place would outlive the frame that set it."""

    with pytest.raises(AttributeError):
        TIME_BASE_LADDER[0].span_s = 1.0  # type: ignore[misc]


def test_the_headroom_is_a_fraction_of_the_width_rather_than_a_fixed_gap() -> None:
    """Ten seconds of clearance is a fifth of one rung and invisible on another."""

    for time_base in TIME_BASE_LADDER:
        assert time_base.live_headroom_s == time_base.span_s * CHART_LIVE_HEADROOM_FRACTION


def test_a_time_base_carries_its_own_interval() -> None:
    """The pairing is what stops a width and its ruling drifting apart."""

    time_base = ChartTimeBase(span_s=900.0, tick_interval_s=180.0)

    assert time_base.span_s == 900.0
    assert time_base.tick_interval_s == 180.0
