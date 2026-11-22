"""Unit tests for `app/chart_time_base.py`, the chart's window width.

These tests check the ladder of widths, the two window rules and the tick
placement without constructing the Qt interface. What the *interface* does with
them is tested in `tests/integration/simulation_view/test_simulation_view_charts.py`: which control
selects a width, what the axis labels show, and what the caption claims.

`PL-012` decided the window's design, and `PL-SSBP` built it. Three of the
window's requirements are properties rather than examples: the window is exactly
as wide as the time base at every moment of every run, "Fit run" always contains
the run, and the gridline interval is derived from the width rather than fixed.
These tests therefore check all three over the whole ladder, not at one chosen
width.
"""

import math

import pytest

from anesthesia_sim.app.chart_time_base import (
    CHART_LIVE_HEADROOM_FRACTION,
    SELECTABLE_TIME_BASE_FLOOR_S,
    SELECTABLE_TIME_BASES,
    TIME_BASE_LADDER,
    ChartTimeBase,
    drawn_seconds,
    extreme_seconds,
    extreme_seconds_with_gaps,
    fit_to_run,
    fitted_window,
    following_window,
    preview_window,
    tick_times,
    time_base_for_span,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.supported_ranges import MAXIMUM_ELAPSED_SIMULATION_TIME_S, CaseInstant


def test_the_ladder_climbs_and_never_nudges() -> None:
    """Each rung is a meaningfully wider view, not a slightly wider one.

    The project owner's requirement (2026-09-04): discrete steps,
    geometrically spaced, so choosing the next one is a decision rather than
    a drag. Each rung is at least half again as wide as the one before it,
    and most rungs are twice as wide.
    """

    for narrower, wider in zip(TIME_BASE_LADDER, TIME_BASE_LADDER[1:], strict=False):
        assert wider.span_s >= narrower.span_s * 1.5


def test_every_rung_is_ruled_into_between_four_and_six_intervals() -> None:
    """The gridline interval is derived from the width, and legibly.

    `PL-012` requires the interval to be derived from the width. The fixed
    60 s interval that it replaced would divide the twelve-hour rung into 720
    lines. The bounds of four to six intervals keep the result a readable grid,
    rather than a bare axis or a dense hatch, at every width the chart can take.
    """

    for time_base in TIME_BASE_LADDER:
        intervals = time_base.span_s / time_base.tick_interval_s

        assert intervals == int(intervals), f"{time_base} does not divide evenly"
        assert 4 <= intervals <= 6, f"{time_base} is ruled into {intervals} intervals"


def test_the_selector_offers_fifteen_minutes_to_twelve_hours() -> None:
    """The project owner settled on this list on 2026-09-04.

    The ladder has rungs narrower than the narrowest selectable width so that
    "Fit run" can use them. Those rungs are deliberately not offered. So this
    test pins both halves: what is listed, and that no narrower rung is listed.
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

    A reader trusts the mode's name to describe what they are looking at. So
    the test checks containment at the ladder's boundaries and past its widest
    rung, rather than at a convenient length.
    """

    instants = [0, 1, 59, 60, 61, 899, 900, 901, 43_200, 43_201, 86_400]

    for newest_instant_s in instants:
        time_base = fit_to_run(CaseInstant(newest_instant_s))
        window_start_s, window_stop_s = fitted_window(time_base)

        assert window_start_s == 0.0
        assert window_stop_s >= newest_instant_s


def test_fitting_takes_the_narrowest_width_that_holds_the_run() -> None:
    """A wider width would squeeze the run into part of the plot for no reason."""

    assert fit_to_run(CaseInstant(0)).span_s == 60.0
    assert fit_to_run(CaseInstant(60)).span_s == 60.0
    assert fit_to_run(CaseInstant(61)).span_s == 120.0
    assert fit_to_run(CaseInstant(900)).span_s == 900.0
    assert fit_to_run(CaseInstant(3_600)).span_s == 3_600.0
    assert fit_to_run(CaseInstant(43_200)).span_s == 43_200.0


def test_fitting_past_the_widest_rung_doubles_rather_than_giving_up() -> None:
    """The ladder is not allowed to assume twelve hours is the end of it.

    `PL-SSBP`'s brief says that the list will grow toward days and weeks, and
    that nothing in the design should assume otherwise. Returning the widest
    rung instead would leave "Fit run" quietly showing the most recent twelve
    hours of a longer case, so the mode would be asserting something false.
    The supported run length is 24 h, so the one doubling a case can reach
    today is from the twelve-hour rung to twenty-four hours.
    """

    widest = TIME_BASE_LADDER[-1]
    widest_span_s = int(widest.span_s)
    beyond = fit_to_run(CaseInstant(widest_span_s * 3 // 2))

    assert beyond.span_s == widest.span_s * 2.0
    # The span and the tick interval double together. So the wider axis has as
    # many intervals as the widest declared rung, and it is ruled like every
    # declared rung.
    assert beyond.span_s / beyond.tick_interval_s == widest.span_s / widest.tick_interval_s
    # A run that ends exactly on a doubled width fits it, as a run that ends
    # exactly on a declared rung fits that rung, and is not doubled again.
    assert fit_to_run(CaseInstant(widest_span_s * 2)).span_s == widest.span_s * 2.0


def test_a_chosen_width_is_held_exactly_at_every_point_of_a_run() -> None:
    """The whole design rests on this property.

    Seconds-per-pixel is constant, so a trace's slope means the same thing
    at the start of a run and an hour in. A window that grew with the run
    would change every apparent rate while no modelled rate moved, which is
    the misleading encoding `PL-012` rejected.
    """

    for time_base in SELECTABLE_TIME_BASES:
        for newest_instant_s in (0, 1, int(time_base.span_s), MAXIMUM_ELAPSED_SIMULATION_TIME_S):
            window_start_s, window_stop_s = following_window(
                time_base, CaseInstant(newest_instant_s)
            )

            assert window_stop_s - window_start_s == pytest.approx(time_base.span_s)


def test_a_run_shorter_than_the_chosen_width_still_shows_whole() -> None:
    """A run shorter than the chosen width still shows whole, as `PL-SSBP`'s "Done when" requires.

    That is why the window does not shrink to the part of the run simulated so
    far. The axis stays at its full width, with the run occupying the left part
    of it.
    """

    time_base = time_base_for_span(900.0)

    for newest_instant_s in (0, 10, 400, 880):
        window_start_s, window_stop_s = following_window(time_base, CaseInstant(newest_instant_s))

        assert window_start_s == 0.0
        assert window_stop_s == 900.0


def test_a_chosen_width_follows_the_run_once_it_is_outgrown() -> None:
    """Once the run outgrows the width, the window slides to keep the newest instant in view."""

    time_base = time_base_for_span(900.0)
    headroom_s = 900.0 * CHART_LIVE_HEADROOM_FRACTION
    window_start_s, window_stop_s = following_window(time_base, CaseInstant(5_000))

    assert window_stop_s == pytest.approx(5_000.0 + headroom_s)
    assert window_start_s == pytest.approx(5_000.0 + headroom_s - 900.0)


def test_fitting_charges_no_headroom_so_a_run_stays_on_its_own_rung() -> None:
    """A fifteen-minute run belongs on the fifteen-minute rung.

    If the fit also added the live headroom, the run would move onto the
    thirty-minute rung and fill only half the plot. That would happen one step
    before the run reaches that width anyway.
    """

    assert fit_to_run(CaseInstant(900)) is time_base_for_span(900.0)


def test_ticks_stand_at_absolute_times_rather_than_at_the_window_s_edge() -> None:
    """A gridline must not crawl as the window slides underneath it.

    Ticks measured from the window's left edge would move with the window. The
    grid would drift, and every label would be rewritten on every frame. The
    axis-label guard in `simulation_view.py` exists to avoid that per-frame churn.
    """

    assert tick_times(0.0, 900.0, 180.0) == (0.0, 180.0, 360.0, 540.0, 720.0, 900.0)
    assert tick_times(100.0, 1_000.0, 180.0) == (180.0, 360.0, 540.0, 720.0, 900.0)
    assert tick_times(181.0, 359.0, 180.0) == ()


def test_ticks_include_a_window_edge_that_falls_exactly_on_one() -> None:
    """Both ends of the window are inclusive, so the fitted window's own ends are ticks."""

    assert tick_times(180.0, 540.0, 180.0) == (180.0, 360.0, 540.0)


@pytest.mark.parametrize("newest_instant_s", [-1, MAXIMUM_ELAPSED_SIMULATION_TIME_S + 1])
def test_a_window_cannot_be_given_an_instant_off_the_case_s_axis(newest_instant_s: int) -> None:
    """An axis drawn against a width nobody can account for is worse than none.

    `CLAUDE.md`'s standard prefers an obvious failure to a plausible-looking
    displayed value, and every drawn time is placed against the window's width.
    Both windows take a `CaseInstant`. So an instant before induction or one
    past the supported run length is rejected where the instant is built, and
    neither window checks it again (`PL-9DF9`).
    """

    with pytest.raises(SimulationConfigurationError, match="outside the supported run length"):
        CaseInstant(newest_instant_s)


@pytest.mark.parametrize(
    "newest_instant_s", [-0.001, 2.0, math.nan, math.inf, MAXIMUM_ELAPSED_SIMULATION_TIME_S + 0.1]
)
def test_a_window_cannot_be_given_an_instant_between_two_seconds(newest_instant_s: float) -> None:
    """An instant is a whole number of seconds, so a `float` is refused whatever its value.

    A run stands only on whole seconds. A `float` instant, even a whole one
    such as 2.0, or one that is not finite, is refused where the instant is
    built, before its range is checked (`PL-SZ6G`).
    """

    with pytest.raises(TypeError, match="has type float, not int"):
        CaseInstant(newest_instant_s)  # type: ignore[arg-type]


@pytest.mark.parametrize("newest_instant_s", [math.inf, math.nan, 900.0])
def test_fitting_refuses_an_instant_not_built_as_one(newest_instant_s: float) -> None:
    """An infinite instant would double the width forever, so it is refused instead."""

    with pytest.raises(TypeError, match="newest_instant_s of .* was not built as CaseInstant"):
        fit_to_run(newest_instant_s)  # type: ignore[arg-type]


@pytest.mark.parametrize("interval_s", [0.0, -60.0, math.nan, math.inf])
def test_tick_placement_refuses_an_interval_that_would_not_rule_anything(interval_s: float) -> None:
    """A non-positive interval would give an axis with no gridlines, or an infinite loop."""

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


def test_the_headroom_is_a_fraction_of_the_width_rather_than_a_fixed_gap() -> None:
    """Ten seconds of clearance is a fifth of one rung and invisible on another."""

    for time_base in TIME_BASE_LADDER:
        assert time_base.live_headroom_s == time_base.span_s * CHART_LIVE_HEADROOM_FRACTION


def test_a_time_base_carries_its_own_interval() -> None:
    """Keeping a width and its tick interval in one record stops them drifting apart."""

    time_base = ChartTimeBase(span_s=900.0, tick_interval_s=180.0)

    assert time_base.span_s == 900.0
    assert time_base.tick_interval_s == 180.0


def test_a_preview_window_keeps_the_width_and_centres_the_reach() -> None:
    base = time_base_for_span(1800.0)

    assert preview_window(base, CaseInstant(3600)) == pytest.approx((2700.0, 4500.0))
    # Early in a run the window stops at zero, and the reach sits left of the middle.
    assert preview_window(base, CaseInstant(300)) == pytest.approx((0.0, 1800.0))
    assert preview_window(base, CaseInstant(900)) == pytest.approx((0.0, 1800.0))


def test_a_preview_window_refuses_a_reach_not_built_as_an_instant() -> None:
    with pytest.raises(TypeError):
        preview_window(time_base_for_span(1800.0), 300.0)  # type: ignore[arg-type]


def test_a_window_draws_its_ends_its_grid_columns_and_each_setting_change() -> None:
    """Columns fall on multiples of the spacing counted from the case's zero, not the window's."""

    # A window from 7 s to 50 s with columns 10 s apart, and settings changed at 5, 23 and 50 s.
    # The change at 5 s lies outside the window. The change at 50 s is the window's end.
    assert drawn_seconds(7, 50, 10, events_s=(5, 23, 50)) == (7, 10, 20, 23, 30, 40, 50)


def test_a_window_of_one_second_draws_that_second_once() -> None:
    assert drawn_seconds(30, 30, 10, events_s=(30,)) == (30,)


def test_a_window_whose_columns_are_one_second_apart_draws_every_second() -> None:
    assert drawn_seconds(3, 8, 1, events_s=()) == (3, 4, 5, 6, 7, 8)


@pytest.mark.parametrize(("first_s", "last_s", "spacing_s"), [(0, 10, 0), (0, 10, -1), (10, 9, 1)])
def test_a_window_with_no_spacing_or_that_ends_before_it_begins_is_refused(
    first_s: int, last_s: int, spacing_s: int
) -> None:
    with pytest.raises(ValueError, match=r"spacing|ends before it begins"):
        drawn_seconds(first_s, last_s, spacing_s, events_s=())


# One value for each second from 100 s to 112 s. The trace rises to a peak of
# 9.0 at 103 s, falls to a trough of 1.0 at 107 s and rises again.
TRACE_FROM_100_S = (2.0, 4.0, 7.0, 9.0, 8.0, 5.0, 3.0, 1.0, 2.5, 4.5, 6.0, 6.5, 7.0)


def test_a_peak_and_a_trough_between_two_drawn_seconds_are_both_found() -> None:
    assert extreme_seconds(100, TRACE_FROM_100_S, (100, 112)) == {103, 107}


def test_each_stretch_is_searched_on_its_own() -> None:
    """Columns at 100, 105 and 112 s leave the peak in one stretch and the trough in the next."""

    assert extreme_seconds(100, TRACE_FROM_100_S, (100, 105, 112)) == {103, 107}
    # With a column on the peak, only the trough is left to find.
    assert extreme_seconds(100, TRACE_FROM_100_S, (100, 103, 112)) == {107}
    # With a column on each, nothing is.
    assert extreme_seconds(100, TRACE_FROM_100_S, (100, 103, 107, 112)) == set()


def test_a_trace_that_only_rises_or_only_falls_across_a_stretch_adds_nothing() -> None:
    rising = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6)
    falling = tuple(reversed(rising))

    assert extreme_seconds(0, rising, (0, 3, 6)) == set()
    assert extreme_seconds(0, falling, (0, 3, 6)) == set()


def test_a_value_that_only_equals_an_end_of_its_stretch_adds_nothing() -> None:
    """The end is already drawn at that value, so the line already reaches it."""

    level = (5.0, 5.0, 5.0, 5.0, 5.0)
    back_to_the_start = (5.0, 3.0, 4.0, 5.0, 2.0)

    assert extreme_seconds(0, level, (0, 4)) == set()
    # The highest value inside is 5.0 at 3 s, which the left end already draws.
    # The lowest inside is 3.0 at 1 s, which is above the right end's 2.0.
    assert extreme_seconds(0, back_to_the_start, (0, 4)) == set()


def test_a_peak_held_for_several_seconds_is_drawn_at_its_first_second() -> None:
    flat_topped = (1.0, 6.0, 8.0, 8.0, 8.0, 4.0, 2.0)

    assert extreme_seconds(40, flat_topped, (40, 46)) == {42}


def test_neighbouring_drawn_seconds_have_nothing_between_them_to_search() -> None:
    assert extreme_seconds(100, TRACE_FROM_100_S, tuple(range(100, 113))) == set()
    assert extreme_seconds(100, TRACE_FROM_100_S, (100,)) == set()
    assert extreme_seconds(100, TRACE_FROM_100_S, ()) == set()


def test_a_trace_with_a_value_at_every_second_is_searched_as_extreme_seconds_searches_it() -> None:
    drawn = (100, 105, 112)

    assert extreme_seconds_with_gaps(100, TRACE_FROM_100_S, drawn) == {103, 107}
    assert extreme_seconds_with_gaps(100, TRACE_FROM_100_S, drawn) == extreme_seconds(
        100, TRACE_FROM_100_S, drawn
    )


def test_a_second_with_no_value_is_neither_returned_nor_compared_with() -> None:
    """A second with no value is left out of the search, and no value stands in for it (`PL-DN13`).

    Each trace below holds one value for each second from 0 s to 6 s, with
    the stretch's ends drawn at 0 s and 6 s.
    """

    # A gap inside: the trough of 1.0 at 4 s is below both ends, and the
    # second with no value at 2 s is never returned.
    assert extreme_seconds_with_gaps(0, (5.0, 4.0, None, 3.0, 1.0, 2.0, 6.0), (0, 6)) == {4}
    # The left end has no value. The lowest value inside, 2.0 at 1 s, is
    # compared with the right end alone, and the highest, 7.0 at 5 s, too.
    assert extreme_seconds_with_gaps(0, (None, 2.0, 3.0, 4.0, 5.0, 7.0, 6.0), (0, 6)) == {1, 5}
    # A value inside that is below the one end with a value, but not above
    # it, adds only the low second.
    assert extreme_seconds_with_gaps(0, (None, 2.0, 3.0, 4.0, 5.0, 5.5, 6.0), (0, 6)) == {1}


def test_a_stretch_whose_ends_have_no_value_returns_its_highest_and_lowest_inside() -> None:
    assert extreme_seconds_with_gaps(0, (None, 0.3, 0.9, None, 0.1, 0.5, None), (0, 6)) == {2, 4}


def test_a_stretch_with_no_value_inside_returns_nothing() -> None:
    assert extreme_seconds_with_gaps(0, (1.0, None, None, None, 2.0), (0, 4)) == set()
    assert extreme_seconds_with_gaps(0, (None, None, None, None, None), (0, 4)) == set()


def test_a_one_second_stretch_after_two_adjacent_drawn_seconds_is_still_searched() -> None:
    """Two adjacent drawn seconds hold nothing between them, and the next stretch is searched.

    The drawn seconds are 0, 1 and 3, so the stretch from 1 s to 3 s holds
    one second. Its value of 0.2 at 2 s is below both ends, so 2 s is
    returned. A search that stopped at the first pair with nothing inside,
    or that skipped a stretch holding only one second, would return nothing.
    """

    assert extreme_seconds_with_gaps(0, (0.9, 0.8, 0.2, 0.7), (0, 1, 3)) == {2}


def test_a_value_inside_equal_to_an_end_is_not_returned() -> None:
    """A value inside a stretch is returned only where it lies outside each end, not level with one.

    The highest value inside, 0.9 at 1 s, equals the left end, and the
    lowest, 0.4 at 2 s, equals the right end. Neither lies outside both
    ends, so nothing is returned.
    """

    assert extreme_seconds_with_gaps(0, (0.9, 0.9, 0.4, 0.4), (0, 3)) == set()


def test_a_trace_that_starts_after_zero_is_searched_only_between_the_drawn_seconds() -> None:
    """The search reads only the seconds between two drawn seconds, wherever the trace starts.

    The trace starts at 100 s and runs to 103 s, and the drawn seconds are
    100 s and 102 s. The one second inside, 101 s, holds 0.5, below both
    ends, so 101 s is returned. The 0.1 at 103 s lies past the stretch and
    is not searched.
    """

    assert extreme_seconds_with_gaps(100, (0.6, 0.5, 0.7, 0.1), (100, 102)) == {101}
