"""The frame-cost harness still runs, and still reports the three stages it names.

The harness itself is a measurement, and a measurement has no pass mark - so
nothing here asserts a duration. What it asserts is the decidable half: that
the thing still drives a real dashboard, that its cadence arithmetic agrees
with the shipped constants, and that it refuses a configuration whose
timings would not be a measurement.

That is the whole reason the harness is kept rather than rewritten a sixth
time (`PL-ZG5J`). A harness that has silently stopped compiling against
`SimulationView.present` is worth less than none, because the session that
finds it broken writes a new one and the method is lost again. These tests
are what fail instead.

Timings are excluded deliberately, not overlooked. A CI runner's speed is
not a property of this repository, so a threshold here would fire on the
runner rather than on the code - `CLAUDE.md`'s "a check that fires every run
without changing a decision is a defect in the check". What frame cost
*should* be is a judgment, and it belongs in the item that asks the
question.

Everything runs at 1x over a short warm-up, so the suite pays a frame rather
than the three seconds a real measurement takes.

`frame_cost` imports as a bare module because this directory holds no
`__init__.py`: pytest's default `prepend` import mode puts the first
package-less directory above a test file on `sys.path`, which is the same
mechanism the rest of `tests/` is collected under, and running the harness
as a script puts its own directory there. Adding an `__init__.py` here would
break both.
"""

import math

import pytest
from frame_cost import (
    DEFAULT_MULTIPLIER,
    FrameSample,
    Measurement,
    measure,
    report,
    steps_per_frame,
)

from anesthesia_sim.app.dashboard_frame import (
    RENDER_INTERVAL_S,
    SIMULATION_STEP_S,
    SIMULATION_TICK_INTERVAL_S,
)
from anesthesia_sim.core.exceptions import SimulationConfigurationError

#: Simulated seconds of warm-up. Long enough that the dashboard has history
#: to draw, short enough that this suite is not a benchmark.
_WARM_UP_S = 30.0

_FRAMES = 2

#: Every stage a `FrameSample` carries, including the control.
_STAGES = ("advance_s", "present_s", "paint_s", "settled_s")


@pytest.fixture(scope="module")
def measurement() -> Measurement:
    """One short run of the harness, shared by every test here."""

    return measure(multiplier=1, frames=_FRAMES, warm_up_s=_WARM_UP_S)


# ------------------------------------------------------- the cadence maths


def test_steps_per_frame_is_the_render_interval_at_the_playback_rate() -> None:
    """A frame advances as much simulated time as its real interval claims.

    Stated as the definition rather than as the arithmetic the harness uses,
    so that a change to either constant has to agree with what the rate
    means: `multiplier` simulated seconds per real second, over
    `RENDER_INTERVAL_S` real seconds, in steps of `SIMULATION_STEP_S`.
    """

    for multiplier in (1, 5, 20, 60, 300):
        simulated_s = multiplier * RENDER_INTERVAL_S

        assert steps_per_frame(multiplier) == round(simulated_s / SIMULATION_STEP_S)


def test_the_top_rate_advances_six_hundred_steps_a_frame() -> None:
    """The number the harness's own docstring and `PL-ZG5J` quote, pinned."""

    assert steps_per_frame(DEFAULT_MULTIPLIER) == 600


def test_a_frame_is_a_whole_number_of_simulation_ticks() -> None:
    """The render interval is a whole number of ticks, so a frame can be counted in them."""

    ticks = RENDER_INTERVAL_S / SIMULATION_TICK_INTERVAL_S

    assert math.isclose(ticks, round(ticks), rel_tol=0.0, abs_tol=1e-9)
    assert round(ticks) >= 1


def test_an_unoffered_playback_rate_is_refused() -> None:
    """The harness measures rates the interface offers, or none.

    Deferred to `app/playback.py` rather than re-checked here: a rate this
    application cannot play is a cadence nobody sees, so measuring it would
    produce a real number about no configuration.
    """

    with pytest.raises(SimulationConfigurationError):
        steps_per_frame(7)


# ---------------------------------------------------------- the harness runs


def test_the_harness_reports_one_sample_per_frame(measurement: Measurement) -> None:
    assert len(measurement.samples) == _FRAMES
    assert all(isinstance(sample, FrameSample) for sample in measurement.samples)


def test_every_stage_is_timed_and_finite(measurement: Measurement) -> None:
    """Each stage produced a real, non-negative duration.

    A stage missing, negative or infinite means the harness stopped
    measuring what it names - which is the failure this suite exists to
    catch, and the one a reader of the numbers could not see.
    """

    for sample in measurement.samples:
        for stage in _STAGES:
            seconds = getattr(sample, stage)

            assert math.isfinite(seconds)
            assert seconds >= 0.0


def test_the_frame_total_is_its_three_stages_and_excludes_the_control(
    measurement: Measurement,
) -> None:
    """`settled_s` is the control for the paint, so it is not part of the frame."""

    for sample in measurement.samples:
        assert math.isclose(sample.interface_s, sample.present_s + sample.paint_s)
        assert math.isclose(sample.total_s, sample.advance_s + sample.interface_s)


def test_the_measurement_records_the_configuration_it_ran(measurement: Measurement) -> None:
    """What was measured travels with the numbers rather than with whoever ran it."""

    assert measurement.multiplier == 1
    assert measurement.steps_per_frame == steps_per_frame(1)
    assert measurement.budget_s == RENDER_INTERVAL_S
    assert measurement.warm_up_s == _WARM_UP_S


def test_the_median_and_the_worst_come_from_the_samples(measurement: Measurement) -> None:
    for stage in _STAGES:
        timings = [getattr(sample, stage) for sample in measurement.samples]

        assert measurement.worst_s(stage) == max(timings)
        assert min(timings) <= measurement.median_s(stage) <= max(timings)


# -------------------------------------------------------------- the report


def test_the_report_names_every_stage_and_the_configuration(measurement: Measurement) -> None:
    """A reader of the output can tell what was measured without reading the source."""

    printed = report(measurement)

    for expected in ("advance", "present", "paint", "interface", "frame", "Control"):
        assert expected in printed

    assert f"{measurement.multiplier}x real time" in printed
    assert f"{measurement.steps_per_frame} steps" in printed
    assert "not a frame rate" in printed


# ------------------------------------------- the configurations it refuses


@pytest.mark.parametrize(("frames", "warm_up_s"), [(0, 1.0), (-1, 1.0), (1, -1.0)])
def test_a_configuration_that_would_measure_nothing_is_refused(
    frames: int, warm_up_s: float
) -> None:
    with pytest.raises(ValueError):
        measure(multiplier=1, frames=frames, warm_up_s=warm_up_s)
