"""What one frame of the running dashboard costs, split into simulation, assembly and paint.

Run it: `uv run python tests/benchmarks/frame_cost.py`, about three seconds.

**Why this is written down rather than re-derived.** `PL-YSZN`, `PL-KP7H`,
`PL-R2YM` and `PL-SQJ1` were each answered by a throwaway harness, and
`PL-0VM7`, `PL-Q197` and `PL-R460` each built one and discarded it. The
numbers survived in the items; the *method* did not, and it is the method
that is subtle enough to get wrong. This is the fifth writing of it and the
first one kept (`PL-ZG5J`).

**What a frame is here.** The running application holds two timers
(`app/simulation_view.py`): the simulation ticks every
`SIMULATION_TICK_INTERVAL_S` real seconds, taking
`PlaybackRate.steps_per_tick` steps of `SIMULATION_STEP_S`, and the display
redraws every `RENDER_INTERVAL_S` real seconds. So a *frame* is one render
interval's worth of both: `RENDER_INTERVAL_S / SIMULATION_TICK_INTERVAL_S`
ticks of simulation, then one presentation. At 300x that is 600 steps against
a 200 ms budget. Both numbers are derived from the shipped constants here,
never written in, so a cadence change moves this measurement with it.

**The three stages, and why the third is what a harness gets wrong.**

1. `controller.advance(SIMULATION_STEP_S)`, once per step - the simulation.
2. `SimulationView.present(False)` - assembling the frame and handing it to
   the widgets.
3. `QApplication.processEvents()` - the paint.

Stage 3 is not bookkeeping. `qt_chart.ChartPlot.draw` is `setData`, `setPos`
and `setTicks` throughout: it schedules a repaint and rasterizes nothing, so
`present` returns before the frame has been drawn and the frame is complete
only once the event loop dispatches the paint event. This harness at its
defaults, 2026-09-19 in the web container, medians over three runs: advance
12.0 ms, present 15.3 ms, paint 13.1 ms, so the interface costs 28.4 ms of a
40.4 ms frame. A two-stage harness would have reported that interface at
15.3 ms - 46% low, in the flattering direction - and the control below is
what rules out the alternative reading, that stage 3 is the event loop
rather than the frame.

Under Flet the same third position was held by `page.update()` against a
session whose connection serialized each outbound message; that was the
subtle part then, for the same reason it is the paint now. The stage the
toolkit charges for is never the one the code makes obvious.

`_settled` is the control for stage 3: a second `processEvents()` with
nothing owed. It comes back near zero, which is what says the 15.5 ms is
this frame's rasterization rather than fixed event-loop overhead. Read it on
every run - a paint that stops being distinguishable from it means either
the measurement or the chart has changed.

**What this does not measure.** Not a wall-clock frame rate: nothing here
sleeps, so the stages run back to back rather than at the cadence the timers
impose, and a run of this harness is not a claim about what a reader sees.
Not the first frame either, which reads the plot's laid-out width and is
warmed away deliberately. Not an unwarmed run: cost grows with recorded
history, so the warm-up is part of the configuration and is printed with the
result.

**Deliberately not a check, and deliberately not under `tools/`.** It
produces timings, which are a judgment rather than a pass/fail, and
`CLAUDE.md` is explicit that a check which cannot decide is worse than none.
The standard-library-only rule is a property of `tools/` and
`.claude/hooks/` - the directories a bare `python3` invokes outside the
project virtualenv, which is what `tests/unit/test_tools_portability.py`
holds to it by path - rather than of anything runnable, and this imports
PySide6 and the package itself, so it could only ever run under the
virtualenv. `test_frame_cost.py` beside it is the decidable half: that the
harness still runs and still reports three stages, asserting nothing about
the numbers.
"""

import argparse
import math
import os
import statistics
import sys
from dataclasses import dataclass
from time import perf_counter

from PySide6.QtWidgets import QApplication

from anesthesia_sim.app.controller import SimulationController
from anesthesia_sim.app.dashboard_frame import (
    RENDER_INTERVAL_S,
    SIMULATION_STEP_S,
    SIMULATION_TICK_INTERVAL_S,
)
from anesthesia_sim.app.playback import playback_rate_for
from anesthesia_sim.app.simulation_view import SimulationView

#: The size the dashboard is measured at, matching
#: `tests/integration/test_qt_rendering.py`'s. It is a parameter of the
#: measurement rather than a detail: a frame is assembled from the plot's
#: laid-out width, so the chart's pixel width is what sets how many points
#: `present` downsamples to and hands the toolkit to paint. Declared here
#: rather than imported from that module, because the two are separate
#: decisions that happen to agree.
WINDOW_WIDTH_PX = 1600
WINDOW_HEIGHT_PX = 1000

#: The rate the interface's own ladder tops out at, and the only rung where
#: frame cost is in question - `app/playback.py`'s `SUPPORTED_PLAYBACK_RATES`.
DEFAULT_MULTIPLIER = 300

#: Frames measured. Twenty is enough for a median to be stable across runs
#: here and cheap enough that the harness stays a three-second command.
DEFAULT_FRAMES = 20

#: How much simulated run the dashboard holds before the first measured
#: frame. An hour, because cost grows with recorded history and an unwarmed
#: run measures the cheapest case the application ever has.
DEFAULT_WARM_UP_MINUTES = 60

_SECONDS_PER_MINUTE = 60.0
_MILLISECONDS_PER_SECOND = 1000.0


@dataclass(frozen=True, slots=True)
class FrameSample:
    """What one frame's three stages cost, in seconds.

    Attributes:
        advance_s: Every `controller.advance` call this frame takes.
        present_s: `SimulationView.present(False)` - assembling the frame.
        paint_s: The `processEvents()` that dispatches the repaint `present`
            scheduled.
        settled_s: A second `processEvents()` with nothing owed. The control
            for `paint_s`, not a stage of the frame.
    """

    advance_s: float
    present_s: float
    paint_s: float
    settled_s: float

    @property
    def interface_s(self) -> float:
        """Assembly and paint together - what the frame costs that is not the simulation."""

        return self.present_s + self.paint_s

    @property
    def total_s(self) -> float:
        """The whole frame, excluding the control."""

        return self.advance_s + self.interface_s


@dataclass(frozen=True, slots=True)
class Measurement:
    """A run of the harness: its configuration, and one sample per measured frame.

    Attributes:
        multiplier: The playback rate measured, in simulated seconds per
            real second.
        steps_per_frame: Simulation steps one frame advances at that rate.
        budget_s: Real seconds a frame has, which is `RENDER_INTERVAL_S`.
        warm_up_s: Simulated seconds run before the first measured frame.
        samples: One per measured frame, in order.
    """

    multiplier: int
    steps_per_frame: int
    budget_s: float
    warm_up_s: float
    samples: tuple[FrameSample, ...]

    def median_s(self, stage: str) -> float:
        """The median of one stage across the measured frames.

        Args:
            stage: An attribute or property of `FrameSample` - one of
                `advance_s`, `present_s`, `paint_s`, `settled_s`,
                `interface_s` or `total_s`.

        Returns:
            Seconds.
        """

        return statistics.median(float(getattr(sample, stage)) for sample in self.samples)

    def worst_s(self, stage: str) -> float:
        """The slowest measured frame for one stage, in seconds."""

        return max(float(getattr(sample, stage)) for sample in self.samples)


def steps_per_frame(multiplier: int) -> int:
    """How many simulation steps one rendered frame advances at this playback rate.

    Derived from the three shipped cadence constants rather than written
    down, so that a change to the tick interval, the render interval or the
    step moves the measurement rather than silently invalidating it.

    Args:
        multiplier: Simulated seconds per real second, as one of
            `app/playback.py`'s `SUPPORTED_PLAYBACK_RATES` carries it.

    Returns:
        Steps per frame, at least one.

    Raises:
        SimulationConfigurationError: If the multiplier is not one the
            interface offers, or does not land on a whole number of steps
            at the shipped intervals. Refused rather than rounded, for the
            reason `app/playback.py` gives: a fractional rate measured as a
            whole one measures a cadence the application never runs.
    """

    rate = playback_rate_for(multiplier)
    per_tick = rate.steps_per_tick(
        tick_interval_s=SIMULATION_TICK_INTERVAL_S, simulation_step_s=SIMULATION_STEP_S
    )
    ticks = round(RENDER_INTERVAL_S / SIMULATION_TICK_INTERVAL_S)

    return per_tick * ticks


def _application() -> QApplication:
    """The `QApplication` to measure under, reusing one pytest has already built.

    `QT_QPA_PLATFORM` is set here rather than at import, which is where
    `tests/conftest.py` sets it for the test tree: Qt resolves the platform
    plugin when the application is constructed, so immediately before that
    construction is early enough, measured 2026-09-19 against an environment
    with the variable unset. Left unset, Qt picks `xcb` on Linux and
    `QApplication` aborts the process where no display is attached - which is
    every CI runner and every web-container session.

    `setdefault`, so a developer on a desktop who wants to watch the frames
    keeps the platform they chose, and so a pytest run keeps conftest's.
    """

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    existing = QApplication.instance()

    return existing if isinstance(existing, QApplication) else QApplication(sys.argv[:1])


def measure(
    *,
    multiplier: int = DEFAULT_MULTIPLIER,
    frames: int = DEFAULT_FRAMES,
    warm_up_s: float = DEFAULT_WARM_UP_MINUTES * _SECONDS_PER_MINUTE,
) -> Measurement:
    """Drive a real dashboard frame by frame and time each frame's three stages.

    The setup is the one `main.py` performs, in its order: build the
    controller and the view, size and show it, let the layout settle, then
    present. The first presentation reads the plot's laid-out width, so it
    happens before the warm-up rather than inside the measurement.

    Args:
        multiplier: The playback rate to measure, in simulated seconds per
            real second.
        frames: How many frames to time. At least one.
        warm_up_s: Simulated seconds to run before the first measured
            frame. Not negative.

    Returns:
        The configuration and one `FrameSample` per measured frame.

    Raises:
        ValueError: If `frames` is below one or `warm_up_s` is negative.
        SimulationConfigurationError: If the rate is not one the interface
            offers, per `steps_per_frame`.
        RuntimeError: If the run did not advance by exactly the steps this
            harness asked for. A halted or capped run makes
            `controller.advance` a no-op that returns immediately, which
            would report the simulation as free - a plausible number for a
            measurement that did not happen.
    """

    if frames < 1:
        raise ValueError(f"a measurement times at least one frame, not {frames}")

    if warm_up_s < 0.0:
        raise ValueError(f"warm_up_s is a length of simulated run, not {warm_up_s}")

    per_frame = steps_per_frame(multiplier)
    application = _application()
    controller = SimulationController()
    controller.start()

    for _ in range(round(warm_up_s / SIMULATION_STEP_S)):
        controller.advance(SIMULATION_STEP_S)

    view = SimulationView((controller,))
    view.resize(WINDOW_WIDTH_PX, WINDOW_HEIGHT_PX)
    view.show()
    application.processEvents()
    view.present(False)
    application.processEvents()

    samples = []

    try:
        for _ in range(frames):
            started = perf_counter()

            for _ in range(per_frame):
                controller.advance(SIMULATION_STEP_S)

            advanced = perf_counter()
            view.present(False)
            presented = perf_counter()
            application.processEvents()
            painted = perf_counter()
            application.processEvents()
            settled = perf_counter()

            samples.append(
                FrameSample(
                    advance_s=advanced - started,
                    present_s=presented - advanced,
                    paint_s=painted - presented,
                    settled_s=settled - painted,
                )
            )
    finally:
        view.close()

    expected_s = warm_up_s + frames * per_frame * SIMULATION_STEP_S
    elapsed_s = controller.snapshot().elapsed_s

    if not math.isclose(elapsed_s, expected_s, rel_tol=0.0, abs_tol=SIMULATION_STEP_S / 2):
        raise RuntimeError(
            f"the run advanced {elapsed_s} simulated seconds where this measurement asked "
            f"for {expected_s}; a run that is halted or past its supported length takes no "
            f"steps, so the timings above are not a measurement of the simulation"
        )

    return Measurement(
        multiplier=multiplier,
        steps_per_frame=per_frame,
        budget_s=RENDER_INTERVAL_S,
        warm_up_s=warm_up_s,
        samples=tuple(samples),
    )


def _milliseconds(seconds: float) -> str:
    """One stage's cost as a millisecond string.

    Two decimals throughout, including on the control, which is the one
    reading that is meant to be near zero: rounding it to the one decimal
    the stages would carry prints `0.1 ms` where the distinction being drawn
    is between that and 15 ms.
    """

    return f"{seconds * _MILLISECONDS_PER_SECOND:.2f} ms"


def report(measurement: Measurement) -> str:
    """The measurement as the paragraph a session would otherwise write by hand."""

    budget = measurement.budget_s
    total = measurement.median_s("total_s")
    rows = (
        ("advance (simulation)", "advance_s"),
        ("present (assembly)", "present_s"),
        ("paint (event loop)", "paint_s"),
    )
    lines = [
        f"Frame cost at {measurement.multiplier}x real time, "
        f"{len(measurement.samples)} frames, warmed to "
        f"{measurement.warm_up_s / _SECONDS_PER_MINUTE:g} min of simulated run.",
        f"{measurement.steps_per_frame} steps advanced per frame, against a "
        f"{_milliseconds(budget)} budget.",
        "",
        f"  {'stage':<22}{'median':>12}{'worst':>12}",
    ]
    lines += [
        f"  {label:<22}{_milliseconds(measurement.median_s(stage)):>12}"
        f"{_milliseconds(measurement.worst_s(stage)):>12}"
        for label, stage in rows
    ]
    lines += [
        f"  {'interface (2 + 3)':<22}{_milliseconds(measurement.median_s('interface_s')):>12}"
        f"{_milliseconds(measurement.worst_s('interface_s')):>12}",
        f"  {'frame':<22}{_milliseconds(total):>12}"
        f"{_milliseconds(measurement.worst_s('total_s')):>12}",
        "",
        f"Median frame is {total / budget:.0%} of the {_milliseconds(budget)} budget.",
        f"Control: a second processEvents costs "
        f"{_milliseconds(measurement.median_s('settled_s'))}, so the paint above is",
        "this frame's rasterization and not fixed event-loop overhead.",
        "Nothing here sleeps, so this is not a frame rate.",
    ]

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Measure one configuration and print the report.

    Args:
        argv: Command-line arguments, or None to read `sys.argv`.

    Returns:
        A process exit status: 0 always, since a measurement has no verdict
        to fail on. What can fail is the harness itself, and that raises.
    """

    parser = argparse.ArgumentParser(
        description="Time one dashboard frame's simulation, assembly and paint."
    )
    parser.add_argument(
        "--rate",
        type=int,
        default=DEFAULT_MULTIPLIER,
        help=f"playback multiplier to measure (default {DEFAULT_MULTIPLIER})",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=DEFAULT_FRAMES,
        help=f"frames to time (default {DEFAULT_FRAMES})",
    )
    parser.add_argument(
        "--warm-up-minutes",
        type=float,
        default=DEFAULT_WARM_UP_MINUTES,
        help=f"simulated run before the first measured frame (default {DEFAULT_WARM_UP_MINUTES})",
    )
    arguments = parser.parse_args(argv)

    print(
        report(
            measure(
                multiplier=arguments.rate,
                frames=arguments.frames,
                warm_up_s=arguments.warm_up_minutes * _SECONDS_PER_MINUTE,
            )
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
