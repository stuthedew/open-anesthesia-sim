"""Unit tests for the playback rate: a rate is steps per tick, never a step.

The one safety property this module has to hold is that playing a run
faster changes how many steps a tick takes and nothing about a step. These
tests pin the conversion in both directions - that a supported rate lands
on the step count it claims, and that a rate which would need a fractional
step is refused rather than rounded into one.
"""

import dataclasses

import pytest

from anesthesia_sim.app.playback import (
    DEFAULT_PLAYBACK_RATE,
    SUPPORTED_PLAYBACK_RATES,
    PlaybackRate,
    playback_rate_for,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError

#: The intervals the interface ships, restated here rather than imported from
#: `app/simulation_view.py`, which needs Flet. `test_simulation_view.py` holds
#: the shipped constants to these values, so a change there fails there.
TICK_INTERVAL_S = 0.1
SIMULATION_STEP_S = 0.1


@pytest.mark.parametrize("rate", SUPPORTED_PLAYBACK_RATES, ids=lambda rate: f"{rate.multiplier}x")
def test_a_supported_rate_is_that_many_steps_per_tick(rate: PlaybackRate) -> None:
    """At the shipped intervals a tick is one step, so the two numbers agree.

    Not a tautology: the derivation runs through the tick interval and the
    step size, and it is only because a tick is exactly one step of real
    time that the multiplier and the step count coincide. Asserting the
    coincidence is what would fail if either interval were re-tuned without
    the other, which is the moment "60x real time" would stop being true.
    """

    assert (
        rate.steps_per_tick(tick_interval_s=TICK_INTERVAL_S, simulation_step_s=SIMULATION_STEP_S)
        == rate.multiplier
    )


#: The simulated seconds between the instants a live control change can first
#: act at, per rate. A tick advances its whole burst uninterrupted, so this is
#: the steps that burst takes times the step, and it is what `PL-NBWP` made the
#: module docstring and `docs/MODEL.md` § "Supported simulation step" publish.
#:
#: Written out rather than computed from the multipliers, which would restate
#: the implementation and pass whatever it did. These are the numbers a reader
#: is told, so they are the numbers to fail against.
PUBLISHED_CONTROL_GRID_S = {1: 0.1, 5: 0.5, 20: 2.0, 60: 6.0, 300: 30.0}


@pytest.mark.parametrize("rate", SUPPORTED_PLAYBACK_RATES, ids=lambda rate: f"{rate.multiplier}x")
def test_the_control_grid_at_each_rate_is_the_one_two_documents_publish(rate: PlaybackRate) -> None:
    """The resolution claim, held where the rate ladder can move it.

    Two documents state that a setting changed while the run plays first
    acts at a tick boundary, and give the resulting grid per rate against a
    measured cost in percentage points of a displayed compartment. Adding a
    rung to the ladder, or re-tuning either interval, changes those numbers
    and nothing else would notice: the prose would keep asserting the old
    grid while the interface offered a different one, which is the failure
    `PL-NBWP` exists to have fixed once.

    Exact equality is deliberate and is not fragile here. Every product of
    the shipped step and a supported multiplier is exact in binary, so a
    tolerance would only hide the case this is guarding - a rung whose grid
    is a number nobody has published.
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
    """The other direction: a grid published for a rung nobody can select.

    Removing a rung and leaving its row in the table would tell a reader
    the interface resolves control timing at a rate it does not offer.
    """

    assert set(PUBLISHED_CONTROL_GRID_S) == {rate.multiplier for rate in SUPPORTED_PLAYBACK_RATES}


def test_the_slowest_supported_rate_is_real_time() -> None:
    """Nothing slower than real time is offered, and the default is it."""

    assert min(rate.multiplier for rate in SUPPORTED_PLAYBACK_RATES) == 1
    assert DEFAULT_PLAYBACK_RATE.multiplier == 1
    assert DEFAULT_PLAYBACK_RATE in SUPPORTED_PLAYBACK_RATES


def test_the_supported_rates_are_distinct_and_ordered() -> None:
    """A duplicated rate would put two identical options in one dropdown."""

    multipliers = [rate.multiplier for rate in SUPPORTED_PLAYBACK_RATES]

    assert multipliers == sorted(multipliers)
    assert len(set(multipliers)) == len(multipliers)


def test_the_fastest_supported_rate_plays_a_three_hour_case_in_minutes() -> None:
    """The bar `PL-SN2C` sets, asserted rather than asserted about.

    Context-sensitive emergence is the payload of this class of simulator
    and it needs a case long enough to have one. Three hours in at most
    five minutes of real time is what makes it watchable; the shipped
    ladder has to contain a rate that reaches it, whatever else it
    contains.
    """

    three_hours_s = 3.0 * 60.0 * 60.0
    fastest = max(rate.multiplier for rate in SUPPORTED_PLAYBACK_RATES)

    assert three_hours_s / fastest <= 5.0 * 60.0


def test_the_step_size_is_an_input_to_the_conversion_and_never_an_output() -> None:
    """Halving the step doubles the steps per tick; it never halves the rate.

    The whole of the item's safety argument in one assertion. A run played
    at 60x takes six hundred 0.1 s steps a second and never six 10 s ones,
    so two learners comparing the same case at different speeds are
    comparing the same arithmetic.
    """

    rate = PlaybackRate(60)

    assert rate.steps_per_tick(tick_interval_s=0.1, simulation_step_s=0.1) == 60
    assert rate.steps_per_tick(tick_interval_s=0.1, simulation_step_s=0.05) == 120
    assert rate.steps_per_tick(tick_interval_s=0.2, simulation_step_s=0.1) == 120


def test_a_rate_needing_a_fractional_step_is_refused() -> None:
    """Refused, never rounded: rounding would play at a rate nobody displayed.

    A tick that "took 1.5 steps" has only two implementations, and both are
    the failure this module exists to prevent - a step of a different size,
    or a run advancing at a rate other than the one on screen.
    """

    with pytest.raises(SimulationConfigurationError, match="not a whole number of steps"):
        PlaybackRate(3).steps_per_tick(tick_interval_s=0.05, simulation_step_s=0.1)


def test_a_rate_that_would_take_no_step_at_all_is_refused() -> None:
    """A tick shorter than a step cannot advance the run and must say so."""

    with pytest.raises(SimulationConfigurationError):
        PlaybackRate(1).steps_per_tick(tick_interval_s=0.01, simulation_step_s=0.1)


@pytest.mark.parametrize("multiplier", [0, -1, -60])
def test_a_multiplier_below_real_time_is_refused(multiplier: int) -> None:
    """Zero would stop the run through a control that says it is playing."""

    with pytest.raises(SimulationConfigurationError, match="at least 1"):
        PlaybackRate(multiplier)


@pytest.mark.parametrize("multiplier", [1.0, 60.5, "60", None, True])
def test_a_multiplier_that_is_not_a_whole_number_is_refused(multiplier: object) -> None:
    """Including `True`, which `isinstance(x, int)` alone would accept.

    A bool reaching here would be a wiring mistake - a flag passed where a
    rate was meant - and `True` would silently become real time, which is a
    plausible-looking answer to a question nobody asked.
    """

    with pytest.raises(SimulationConfigurationError):
        PlaybackRate(multiplier)  # type: ignore[arg-type]


@pytest.mark.parametrize("interval", [0.0, -0.1, float("nan"), float("inf")])
def test_an_unusable_interval_is_refused(interval: float) -> None:
    """A non-positive or non-finite interval has no step count to give."""

    with pytest.raises(SimulationConfigurationError):
        PlaybackRate(1).steps_per_tick(tick_interval_s=interval, simulation_step_s=0.1)

    with pytest.raises(SimulationConfigurationError):
        PlaybackRate(1).steps_per_tick(tick_interval_s=0.1, simulation_step_s=interval)


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
