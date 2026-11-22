"""Unit tests for the playback rate: a rate is how often a run steps, never a step.

The one safety property that this module must enforce is that playing a run
faster changes how many one-second steps are taken per second of real time,
and nothing about a step. These tests pin the conversion from a rate and a
tick interval to steps: the simulated time each tick owes, the steps that are
due on each tick, and the grid of instants that a live control change can
reach.
"""

import dataclasses

import pytest

from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    MAXIMUM_STEPS_PER_TICK,
    SUPPORTED_PLAYBACK_RATES,
    OwedSimulatedTime,
    PlaybackRate,
    playback_rate_for,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError

#: The tick interval that the interface ships, in milliseconds of real time.
#: It is restated here rather than imported from `app/dashboard_frame.py`, so
#: that a change there fails `tests/unit/test_dashboard_frame.py`, which checks
#: the shipped constant against this value.
TICK_INTERVAL_MS = 100

#: One real second of ticks at the shipped interval.
TICKS_PER_REAL_SECOND = 10

#: For each rate, the steps taken on each of ten consecutive ticks from a
#: fresh start. Each row is worked out by hand: a tick owes `multiplier x 100`
#: ms, and one step is taken for each whole 1 000 ms owed. At 1x the tenth
#: tick brings the owed time to 1 000 ms. At 5x every second tick does.
STEPS_ON_EACH_OF_TEN_TICKS = {
    1: (0, 0, 0, 0, 0, 0, 0, 0, 0, 1),
    5: (0, 1, 0, 1, 0, 1, 0, 1, 0, 1),
    20: (2,) * 10,
    60: (6,) * 10,
    300: (30,) * 10,
}


@pytest.mark.parametrize("rate", SUPPORTED_PLAYBACK_RATES, ids=lambda rate: f"{rate.multiplier}x")
def test_a_supported_rate_takes_its_steps_on_the_ticks_worked_out_by_hand(
    rate: PlaybackRate,
) -> None:
    """Each tick takes the steps that the hand-worked row gives for it."""

    owed = OwedSimulatedTime()
    steps = tuple(
        owed.steps_due(rate, tick_interval_ms=TICK_INTERVAL_MS)
        for _ in range(TICKS_PER_REAL_SECOND)
    )

    assert steps == STEPS_ON_EACH_OF_TEN_TICKS[rate.multiplier]


@pytest.mark.parametrize("rate", SUPPORTED_PLAYBACK_RATES, ids=lambda rate: f"{rate.multiplier}x")
def test_one_real_second_of_ticks_advances_the_run_by_the_multiplier(rate: PlaybackRate) -> None:
    """Ten 100 ms ticks take `multiplier` one-second steps, which is what the label claims.

    "60x real time" is a claim about the clock on screen. It is true when a
    real second of ticks advances the run by 60 simulated seconds, and nothing
    is left owed at the end of that second.
    """

    owed = OwedSimulatedTime()
    steps = sum(
        owed.steps_due(rate, tick_interval_ms=TICK_INTERVAL_MS)
        for _ in range(TICKS_PER_REAL_SECOND)
    )

    assert steps == rate.multiplier
    assert owed.owed_ms == 0


def test_a_change_of_rate_keeps_the_part_of_a_second_already_owed() -> None:
    """The remainder is simulated time, so it carries over when the rate changes.

    Three ticks at 1x owe 300 ms. One tick at 5x adds 500 ms, which is still
    less than a step. The next 5x tick brings the total to 1 300 ms, so one
    step is due and 300 ms stay owed.
    """

    owed = OwedSimulatedTime()

    for _ in range(3):
        assert owed.steps_due(PlaybackRate(1), tick_interval_ms=TICK_INTERVAL_MS) == 0

    assert owed.steps_due(PlaybackRate(5), tick_interval_ms=TICK_INTERVAL_MS) == 0
    assert owed.steps_due(PlaybackRate(5), tick_interval_ms=TICK_INTERVAL_MS) == 1
    assert owed.owed_ms == 300


def test_a_tick_that_owes_one_and_a_half_steps_takes_one_step_then_two() -> None:
    """A rate that owes a fraction of a step per tick is played exactly, not refused or rounded.

    15x with a 100 ms tick owes 1 500 ms per tick. The steps alternate between
    one and two, and four ticks take six steps.
    """

    owed = OwedSimulatedTime()
    steps = [owed.steps_due(PlaybackRate(15), tick_interval_ms=TICK_INTERVAL_MS) for _ in range(4)]

    assert steps == [1, 2, 1, 2]


def test_clearing_the_owed_time_owes_nothing() -> None:
    """A run that starts over owes no part of a second from the run before it."""

    owed = OwedSimulatedTime()
    owed.steps_due(PlaybackRate(1), tick_interval_ms=TICK_INTERVAL_MS)

    assert owed.owed_ms == 100

    owed.clear()

    assert owed.owed_ms == 0


#: For each rate, the longest simulated time between two instants at which a
#: live control change can first act. It is the grid that the module docstring
#: of `app/playback.py` and `docs/MODEL.md` § "Supported simulation step"
#: publish.
#:
#: The values are written out rather than computed from the multipliers,
#: because computing them would restate the implementation and pass whatever
#: it did. These are the numbers a reader is told, so they are the numbers to
#: fail against.
PUBLISHED_CONTROL_GRID_S = {1: 1, 5: 1, 20: 2, 60: 6, 300: 30}


@pytest.mark.parametrize("rate", SUPPORTED_PLAYBACK_RATES, ids=lambda rate: f"{rate.multiplier}x")
def test_the_control_grid_at_each_rate_is_the_one_two_documents_publish(rate: PlaybackRate) -> None:
    """Check the published timing claim, in the place where the rate ladder can change it.

    Two documents state the grid of instants that a setting changed during
    play can reach at each rate, against a measured cost in percentage points
    of a displayed compartment. Adding a rung to the ladder, or changing the
    tick interval, changes those numbers, and nothing else would notice
    (`PL-NBWP`).
    """

    assert rate.multiplier in PUBLISHED_CONTROL_GRID_S, (
        f"{rate.multiplier}x is offered but its control grid is published nowhere; "
        "add it to app/playback.py and docs/MODEL.md 'Supported simulation step' first"
    )
    assert (
        rate.control_grid_s(tick_interval_ms=TICK_INTERVAL_MS)
        == PUBLISHED_CONTROL_GRID_S[rate.multiplier]
    )


@pytest.mark.parametrize("rate", SUPPORTED_PLAYBACK_RATES, ids=lambda rate: f"{rate.multiplier}x")
def test_the_control_grid_is_the_most_steps_any_tick_takes(rate: PlaybackRate) -> None:
    """The published grid agrees with the loop: no tick takes more steps than the grid states.

    The grid is checked here against the steps that the accumulator hands
    out over a real second of ticks, which is a second route to the same
    number.
    """

    owed = OwedSimulatedTime()
    most_steps = max(
        owed.steps_due(rate, tick_interval_ms=TICK_INTERVAL_MS)
        for _ in range(TICKS_PER_REAL_SECOND)
    )

    assert rate.control_grid_s(tick_interval_ms=TICK_INTERVAL_MS) == max(most_steps, 1)


def test_every_published_control_grid_belongs_to_an_offered_rate() -> None:
    """Check the other direction: no grid is published for a rung that nobody can select.

    Removing a rung but leaving its row in the table would tell a reader that
    the interface resolves control timing at a rate it does not offer.
    """

    assert set(PUBLISHED_CONTROL_GRID_S) == {rate.multiplier for rate in SUPPORTED_PLAYBACK_RATES}


def test_the_slowest_supported_rate_is_real_time() -> None:
    """Nothing slower than real time is offered, and real time is the default."""

    assert min(rate.multiplier for rate in SUPPORTED_PLAYBACK_RATES) == 1
    assert DEFAULT_PLAYBACK_RATE.multiplier == 1
    assert DEFAULT_PLAYBACK_RATE in SUPPORTED_PLAYBACK_RATES


def test_the_supported_rates_are_distinct_and_ordered() -> None:
    """A duplicated rate would put two identical options in one dropdown."""

    multipliers = [rate.multiplier for rate in SUPPORTED_PLAYBACK_RATES]

    assert multipliers == sorted(multipliers)
    assert len(set(multipliers)) == len(multipliers)


def test_the_fastest_supported_rate_plays_a_three_hour_case_in_minutes() -> None:
    """Assert the bar that `PL-SN2C` sets, rather than only describing it.

    Context-sensitive emergence is the payload of this class of simulator,
    and it needs a case long enough for something to emerge. Playing three
    hours in at most five minutes of real time is what makes such a case
    watchable. The shipped ladder must contain a rate that reaches that bar,
    whatever else it contains.
    """

    three_hours_s = 3.0 * 60.0 * 60.0
    fastest = max(rate.multiplier for rate in SUPPORTED_PLAYBACK_RATES)

    assert three_hours_s / fastest <= 5.0 * 60.0


def test_a_faster_rate_takes_more_steps_and_never_a_longer_one() -> None:
    """Doubling the rate doubles the simulated time a tick owes, in whole one-second steps.

    This assertion carries the item's safety argument. A run played at 60x
    takes sixty one-second steps for each real second, never six 10 s steps.
    So two learners comparing the same case at different speeds are comparing
    the same arithmetic.
    """

    assert PlaybackRate(60).simulated_ms_per_tick(tick_interval_ms=100) == 6_000
    assert PlaybackRate(120).simulated_ms_per_tick(tick_interval_ms=100) == 12_000
    assert PlaybackRate(60).simulated_ms_per_tick(tick_interval_ms=200) == 12_000


@pytest.mark.parametrize("multiplier", [0, -1, -60])
def test_a_multiplier_below_real_time_is_refused(multiplier: int) -> None:
    """Zero would stop the run through a control that says it is playing."""

    with pytest.raises(SimulationConfigurationError, match="at least 1"):
        PlaybackRate(multiplier)


@pytest.mark.parametrize("multiplier", [1.0, 60.5, "60", None, True])
def test_a_multiplier_that_is_not_a_whole_number_is_refused(multiplier: object) -> None:
    """The refused values include `True`, which `isinstance(x, int)` alone would accept.

    A bool reaching here would be a wiring mistake, such as a flag passed
    where a rate was meant. `True` would silently become real time, which is
    a plausible-looking answer to a question nobody asked.
    """

    with pytest.raises(SimulationConfigurationError):
        PlaybackRate(multiplier)  # type: ignore[arg-type]


@pytest.mark.parametrize("interval_ms", [0, -100])
def test_a_tick_interval_below_one_millisecond_is_refused(interval_ms: int) -> None:
    """A tick that takes no real time owes the run nothing, so it is refused."""

    with pytest.raises(SimulationConfigurationError, match="at least 1 ms"):
        PlaybackRate(1).simulated_ms_per_tick(tick_interval_ms=interval_ms)


@pytest.mark.parametrize("interval_ms", [True, 100.0, "100", None])
def test_a_tick_interval_that_is_not_a_whole_number_is_refused(interval_ms: object) -> None:
    """The interval is a whole number of milliseconds, so that the owed time stays exact.

    A `float` interval would bring back the rounded sum that whole
    milliseconds remove. `True` is refused although Python counts it as 1.
    """

    with pytest.raises(TypeError, match="tick_interval_ms"):
        PlaybackRate(1).simulated_ms_per_tick(tick_interval_ms=interval_ms)  # type: ignore[arg-type]


def test_a_refused_tick_adds_nothing_to_the_owed_time() -> None:
    """A tick whose interval is refused leaves the owed time as it was."""

    owed = OwedSimulatedTime(owed_ms=300)

    with pytest.raises(SimulationConfigurationError):
        owed.steps_due(PlaybackRate(1), tick_interval_ms=0)

    assert owed.owed_ms == 300


def test_a_tick_past_the_most_steps_one_tick_may_take_is_refused() -> None:
    """A tick runs all its steps before the interface can respond, so its count has a bound.

    A 100 ms tick at 10 001x would owe 1 000.1 steps, which is more than the
    bound of 1 000 (`PL-T6P0`).
    """

    assert MAXIMUM_STEPS_PER_TICK == 1_000

    with pytest.raises(SimulationConfigurationError, match="more than the 1000 one tick"):
        PlaybackRate(10_001).simulated_ms_per_tick(tick_interval_ms=TICK_INTERVAL_MS)


def test_a_tick_at_the_most_steps_one_tick_may_take_is_played() -> None:
    """A tick that owes exactly 1 000 steps, the bound itself, is played."""

    owed = OwedSimulatedTime()

    assert owed.steps_due(PlaybackRate(10_000), tick_interval_ms=TICK_INTERVAL_MS) == 1_000


def test_the_most_steps_one_tick_may_take_covers_every_rate() -> None:
    """Every offered rate plays at the shipped tick, and the fastest takes 30 steps per tick.

    If a faster rate would need more steps than the bound, this test fails.
    The bound can then be reconsidered before a learner ever meets the
    refusal.
    """

    for rate in SUPPORTED_PLAYBACK_RATES:
        rate.simulated_ms_per_tick(tick_interval_ms=TICK_INTERVAL_MS)

    fastest = max(SUPPORTED_PLAYBACK_RATES, key=lambda rate: rate.multiplier)

    assert fastest.control_grid_s(tick_interval_ms=TICK_INTERVAL_MS) == 30


def test_a_rate_is_looked_up_by_multiplier() -> None:
    for rate in SUPPORTED_PLAYBACK_RATES:
        assert playback_rate_for(rate.multiplier) is rate


def test_an_unoffered_rate_raises_rather_than_falling_back() -> None:
    """A rate the control cannot produce means the control and the list differ.

    Defaulting to real time here would turn that defect into a mode change
    the reader did not make and the display would not explain.
    """

    with pytest.raises(SimulationConfigurationError, match="not one of the playback rates"):
        playback_rate_for(7)


def test_a_rate_is_immutable() -> None:
    """The loop reads the rate every tick, so a mutated one would be silent."""

    with pytest.raises(dataclasses.FrozenInstanceError):
        DEFAULT_PLAYBACK_RATE.multiplier = 60  # type: ignore[misc]
