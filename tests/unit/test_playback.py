"""Unit tests for the playback rate: a rate is steps per tick, never a step.

The one safety property that this module must enforce is that playing a
run faster changes how many steps a tick takes, and nothing about a step.
These tests pin the conversion in both directions. A supported rate lands on
the step count it claims, and a rate that would need a fractional step is
refused rather than rounded to a whole one.
"""

import dataclasses
from math import nextafter

import pytest

from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    PlaybackRate,
    playback_rate_for,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError
from anesthesia_sim.core.simulation_step import MINIMUM_SIMULATION_STEP_S, SimulationStep

#: The intervals that the interface ships. They are restated here rather than
#: imported from `app/simulation_view.py`, which needs Flet.
#: `test_simulation_view.py` checks the shipped constants against these values,
#: so a change there fails there.
TICK_INTERVAL_S = 0.1
SIMULATION_STEP_S = SimulationStep(0.1)


@pytest.mark.parametrize("rate", SUPPORTED_PLAYBACK_RATES, ids=lambda rate: f"{rate.multiplier}x")
def test_a_supported_rate_is_that_many_steps_per_tick(rate: PlaybackRate) -> None:
    """At the shipped intervals a tick is one step, so the two numbers agree.

    This is not a tautology. The derivation runs through the tick interval
    and the step size. The multiplier and the step count coincide only
    because a tick is exactly one step of real time. Asserting the
    coincidence is what would fail if either interval were re-tuned without
    the other. That is the moment when "60x real time" would stop being true.
    """

    assert (
        rate.steps_per_tick(tick_interval_s=TICK_INTERVAL_S, simulation_step_s=SIMULATION_STEP_S)
        == rate.multiplier
    )


#: For each rate, the simulated seconds between the instants at which a live
#: control change can first act. A tick advances its whole burst without
#: interruption, so this is the number of steps in that burst times the step.
#: It is the grid that `PL-NBWP` made the module docstring and `docs/MODEL.md`
#: § "Supported simulation step" publish.
#:
#: The values are written out rather than computed from the multipliers,
#: because computing them would restate the implementation and pass whatever
#: it did. These are the numbers a reader is told, so they are the numbers to
#: fail against.
PUBLISHED_CONTROL_GRID_S = {1: 0.1, 5: 0.5, 20: 2.0, 60: 6.0, 300: 30.0}


@pytest.mark.parametrize("rate", SUPPORTED_PLAYBACK_RATES, ids=lambda rate: f"{rate.multiplier}x")
def test_the_control_grid_at_each_rate_is_the_one_two_documents_publish(rate: PlaybackRate) -> None:
    """Check the published timing claim, in the place where the rate ladder can change it.

    Two documents state that a setting changed while the run plays first
    acts at a tick boundary. They give the resulting grid for each rate,
    against a measured cost in percentage points of a displayed compartment.
    Adding a rung to the ladder, or re-tuning either interval, changes those
    numbers, and nothing else would notice. The prose would keep asserting
    the old grid while the interface offered a different one. `PL-NBWP`
    fixed that failure once, and this test keeps it fixed.

    Exact equality is deliberate and is not fragile here. Every product of
    the shipped step and a supported multiplier is exact in binary. A
    tolerance would only hide the case that this test guards against: a rung
    whose grid is a number nobody has published.
    """

    steps = rate.steps_per_tick(
        tick_interval_s=TICK_INTERVAL_S, simulation_step_s=SIMULATION_STEP_S
    )

    assert rate.multiplier in PUBLISHED_CONTROL_GRID_S, (
        f"{rate.multiplier}x is offered but its control grid is published nowhere; "
        "add it to app/playback.py and docs/MODEL.md 'Supported simulation step' first"
    )
    assert steps * SIMULATION_STEP_S == PUBLISHED_CONTROL_GRID_S[rate.multiplier]


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


def test_the_step_size_is_an_input_to_the_conversion_and_never_an_output() -> None:
    """Halving the step doubles the steps per tick, and it never halves the rate.

    This one assertion carries the whole of the item's safety argument. A run
    played at 60x takes six hundred 0.1 s steps a second, never six 10 s
    steps. So two learners comparing the same case at different speeds are
    comparing the same arithmetic.
    """

    rate = PlaybackRate(60)

    assert rate.steps_per_tick(tick_interval_s=0.1, simulation_step_s=SimulationStep(0.1)) == 60
    assert rate.steps_per_tick(tick_interval_s=0.1, simulation_step_s=SimulationStep(0.05)) == 120
    assert rate.steps_per_tick(tick_interval_s=0.2, simulation_step_s=SimulationStep(0.1)) == 120


def test_a_rate_needing_a_fractional_step_is_refused() -> None:
    """The rate is refused, never rounded, because rounding would play at a rate nobody displayed.

    A tick that "took 1.5 steps" has only two possible implementations, and
    both are the failure this module exists to prevent. One is a step of a
    different size. The other is a run advancing at a rate other than the one
    on screen.
    """

    with pytest.raises(SimulationConfigurationError, match="not a whole number of steps"):
        PlaybackRate(3).steps_per_tick(tick_interval_s=0.05, simulation_step_s=SimulationStep(0.1))


def test_a_rate_that_would_take_no_step_at_all_is_refused() -> None:
    """A tick shorter than a step cannot advance the run and must say so."""

    with pytest.raises(SimulationConfigurationError):
        PlaybackRate(1).steps_per_tick(tick_interval_s=0.01, simulation_step_s=SimulationStep(0.1))


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


@pytest.mark.parametrize("interval", [0.0, -0.1, float("nan"), float("inf")])
def test_an_unusable_interval_is_refused(interval: float) -> None:
    """A non-positive or non-finite interval has no step count to give."""

    with pytest.raises(SimulationConfigurationError, match="tick_interval_s"):
        PlaybackRate(1).steps_per_tick(
            tick_interval_s=interval, simulation_step_s=SimulationStep(0.1)
        )

    with pytest.raises(SimulationConfigurationError):
        PlaybackRate(1).steps_per_tick(
            tick_interval_s=0.1, simulation_step_s=SimulationStep(interval)
        )


@pytest.mark.parametrize("interval", [True, "0.1"])
def test_a_tick_interval_that_is_not_a_number_is_refused(interval: object) -> None:
    """The interval passes the same number check as every core quantity (`PL-F9TC`).

    `True` was accepted as an interval of 1 s before the check was read from
    `core.validation`.
    """

    with pytest.raises(TypeError, match="tick_interval_s"):
        PlaybackRate(1).steps_per_tick(
            tick_interval_s=interval,  # type: ignore[arg-type]
            simulation_step_s=SimulationStep(0.1),
        )


@pytest.mark.parametrize(
    "simulation_step_s", [5e-324, nextafter(MINIMUM_SIMULATION_STEP_S, 0.0), 0.2]
)
def test_a_step_outside_the_supported_range_is_refused(simulation_step_s: float) -> None:
    """The step that a tick counts in is a run's step, so it has the run's bounds.

    5e-324 s reached `round()` as an infinite step count and raised a bare
    `OverflowError`, outside the simulator's own exceptions (`PL-YZ17`).
    """

    with pytest.raises(SimulationConfigurationError, match="supported step"):
        PlaybackRate(1).steps_per_tick(
            tick_interval_s=0.1, simulation_step_s=SimulationStep(simulation_step_s)
        )


def test_a_step_count_too_large_to_count_is_refused() -> None:
    """An enormous tick gives an infinite count, which is refused rather than rounded."""

    with pytest.raises(SimulationConfigurationError, match="than can be counted"):
        PlaybackRate(300).steps_per_tick(
            tick_interval_s=1e307, simulation_step_s=SimulationStep(0.1)
        )


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
