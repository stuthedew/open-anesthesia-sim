"""Unit tests for `app/chart_time_base.py`, the chart's window width.

These tests check the ladder of widths, the two window rules and the tick
placement without constructing a Flet interface. What the *interface* does with
them is tested in `tests/unit/test_simulation_view.py`: which control selects a
width, what the axis labels show, and what the caption claims.

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

    instants = [0.0, 0.1, 59.9, 60.0, 60.1, 899.9, 900.0, 900.1, 43_200.0, 43_200.1, 86_400.0]

    for newest_instant_s in instants:
        time_base = fit_to_run(CaseInstant(newest_instant_s))
        window_start_s, window_stop_s = fitted_window(time_base)

        assert window_start_s == 0.0
        assert window_stop_s >= newest_instant_s


def test_fitting_takes_the_narrowest_width_that_holds_the_run() -> None:
    """A wider width would squeeze the run into part of the plot for no reason."""

    assert fit_to_run(CaseInstant(0.0)).span_s == 60.0
    assert fit_to_run(CaseInstant(60.0)).span_s == 60.0
    assert fit_to_run(CaseInstant(60.1)).span_s == 120.0
    assert fit_to_run(CaseInstant(900.0)).span_s == 900.0
    assert fit_to_run(CaseInstant(3_600.0)).span_s == 3_600.0
    assert fit_to_run(CaseInstant(43_200.0)).span_s == 43_200.0


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
    beyond = fit_to_run(CaseInstant(widest.span_s * 1.5))

    assert beyond.span_s == widest.span_s * 2.0
    # The span and the tick interval double together. So the wider axis has as
    # many intervals as the widest declared rung, and it is ruled like every
    # declared rung.
    assert beyond.span_s / beyond.tick_interval_s == widest.span_s / widest.tick_interval_s
    # A run that ends exactly on a doubled width fits it, as a run that ends
    # exactly on a declared rung fits that rung, and is not doubled again.
    assert fit_to_run(CaseInstant(widest.span_s * 2.0)).span_s == widest.span_s * 2.0


def test_a_chosen_width_is_held_exactly_at_every_point_of_a_run() -> None:
    """The whole design rests on this property.

    Seconds-per-pixel is constant, so a trace's slope means the same thing
    at the start of a run and an hour in. A window that grew with the run
    would change every apparent rate while no modelled rate moved, which is
    the misleading encoding `PL-012` rejected.
    """

    for time_base in SELECTABLE_TIME_BASES:
        for newest_instant_s in (0.0, 1.0, time_base.span_s, MAXIMUM_ELAPSED_SIMULATION_TIME_S):
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

    for newest_instant_s in (0.0, 10.0, 400.0, 880.0):
        window_start_s, window_stop_s = following_window(time_base, CaseInstant(newest_instant_s))

        assert window_start_s == 0.0
        assert window_stop_s == 900.0


def test_a_chosen_width_follows_the_run_once_it_is_outgrown() -> None:
    """Once the run outgrows the width, the window slides to keep the newest instant in view."""

    time_base = time_base_for_span(900.0)
    headroom_s = 900.0 * CHART_LIVE_HEADROOM_FRACTION
    window_start_s, window_stop_s = following_window(time_base, CaseInstant(5_000.0))

    assert window_stop_s == pytest.approx(5_000.0 + headroom_s)
    assert window_start_s == pytest.approx(5_000.0 + headroom_s - 900.0)


def test_fitting_charges_no_headroom_so_a_run_stays_on_its_own_rung() -> None:
    """A fifteen-minute run belongs on the fifteen-minute rung.

    If the fit also added the live headroom, the run would move onto the
    thirty-minute rung and fill only half the plot. That would happen one step
    before the run reaches that width anyway.
    """

    assert fit_to_run(CaseInstant(900.0)) is time_base_for_span(900.0)


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


@pytest.mark.parametrize(
    "newest_instant_s", [-1.0, -0.001, math.nan, math.inf, MAXIMUM_ELAPSED_SIMULATION_TIME_S + 0.1]
)
def test_a_window_cannot_be_given_an_instant_off_the_case_s_axis(newest_instant_s: float) -> None:
    """An axis drawn against a width nobody can account for is worse than none.

    `CLAUDE.md`'s standard prefers an obvious failure to a plausible-looking
    displayed value, and every drawn time is placed against the window's width.
    Both windows take a `CaseInstant`. So an instant before induction, one that
    is not finite, or one past the supported run length is rejected where the
    instant is built, and neither window checks it again (`PL-9DF9`).
    """

    with pytest.raises(SimulationConfigurationError, match="outside the supported run length"):
        CaseInstant(newest_instant_s)


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

    assert preview_window(base, CaseInstant(3600.0)) == pytest.approx((2700.0, 4500.0))
    # Early in a run the window stops at zero, and the reach sits left of the middle.
    assert preview_window(base, CaseInstant(300.0)) == pytest.approx((0.0, 1800.0))
    assert preview_window(base, CaseInstant(900.0)) == pytest.approx((0.0, 1800.0))


def test_a_preview_window_refuses_a_reach_not_built_as_an_instant() -> None:
    with pytest.raises(TypeError):
        preview_window(time_base_for_span(1800.0), 300.0)  # type: ignore[arg-type]
