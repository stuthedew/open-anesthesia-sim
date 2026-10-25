"""Time one frame of the running dashboard, split into simulation, assembly and paint.

To run it, use `uv run python tests/benchmarks/frame_cost.py`. It takes about
three seconds and measures the one-run dashboard that the application opens
with. Add `--runs 2` to measure the trunk and the branch that taking a fork
draws on one chart. That takes about four seconds.

**Why this is written down rather than re-derived.** `PL-YSZN`, `PL-KP7H`,
`PL-R2YM` and `PL-SQJ1` were each answered by a throwaway harness, and
`PL-0VM7`, `PL-Q197` and `PL-R460` each built one and discarded it. The
numbers survived in the items, but the *method* did not, and the method is
subtle enough to get wrong. This is the fifth writing of it and the first one
kept (`PL-ZG5J`).

**What a frame is here.** The running application has a step timer for each
run it draws (`app/run_view.py`) and one render timer
(`app/simulation_view.py`). Every run ticks every `SIMULATION_TICK_INTERVAL_S`
real seconds, and on each tick it takes `PlaybackRate.steps_per_tick` steps of
`SIMULATION_STEP_S`. The display redraws every `RENDER_INTERVAL_S` real
seconds. So a *frame* is one render interval's worth of both:
`RENDER_INTERVAL_S / SIMULATION_TICK_INTERVAL_S` ticks of every run's
simulation, then one presentation. At 300x that is 600 steps per run against a
200 ms budget. A second run doubles the steps without widening the budget.
Both numbers are derived here from the shipped constants, never written in, so
a change of cadence moves this measurement with it.

**The three stages, and why a harness gets the third one wrong.**

1. The simulation: `controller.advance(SIMULATION_STEP_S)`, once per step of
   every run.
2. The assembly: `SimulationView.present(False)`, which assembles the frame and
   hands it to the widgets.
3. The paint: `QApplication.processEvents()`.

Stage 3 is not bookkeeping. `qt_chart.ChartPlot.draw` consists entirely of
`setData`, `setPos` and `setTicks` calls. It schedules a repaint and
rasterizes nothing. So `present` returns before the frame has been drawn, and
the frame is complete only once the event loop dispatches the paint event.
This harness was run at its defaults on 2026-09-19 in the web container, with
one run, taking medians over three invocations. It measured advance 12.0 ms,
present 15.3 ms and paint 13.1 ms, so the interface costs 28.4 ms of a 40.4 ms
frame. A two-stage harness would have reported that interface at 15.3 ms. That
is 46% low, in the flattering direction. The control described below rules out
the other reading, that stage 3 is the event loop rather than the frame.

**Two runs on one chart** (`PL-WPDB`). These used the same defaults, on
2026-10-01 in the web container, with medians over three invocations of each,
alternated. One run: advance 12.8 ms, present 16.8 ms, paint 14.2 ms, a 44.2 ms
frame, 22% of the budget. Two runs: advance 25.1 ms, present 30.2 ms, paint
13.7 ms, a 68.9 ms frame, 34% of the budget. The second run doubles the
simulation and nearly doubles the assembly, because it brings its own readouts
and control timeline. The paint stays level, but it rasterizes a different
chart. Comparing runs caps the chart at two compartments per run
(`COMPARED_COMPARTMENT_CAP`), so it draws four curves where one run draws six,
with wider pens. The level paint is measured with the chart in view, which
`_bring_chart_into_view` arranges. Opening the dashboard over a case, so that
the branch control is drawn and refreshed, moved the one-run frame by less than
the spread between invocations. The harness on `main` read 44.2 ms in the same
container. So what moved the frame from 2026-09-19's 40.4 ms is the container
or the tree since then, not the case.

Under Flet, the same third position was taken by `page.update()`, against a
session whose connection serialized each outbound message. That was the subtle
part then, for the same reason that the paint is now. The stage that the
toolkit charges for is never the one that the code makes obvious.

`settled_s` is the control for stage 3: a second `processEvents()` call with
nothing pending. It comes back near zero, which shows that the paint is this
frame's rasterization rather than fixed event-loop overhead. Read it on every
invocation. If the paint stops being distinguishable from it, either the
measurement or the chart has changed.

**What this does not measure.** It is not a wall-clock frame rate. Nothing
here sleeps, so the stages run back to back rather than at the cadence that
the timers impose. An invocation of this harness is not a claim about what a
reader sees. It does not measure the first frame either, which reads the
plot's laid-out width and is deliberately warmed away. Nor does it measure an
unwarmed run. Cost grows with recorded history, so the warm-up is part of the
configuration and is printed with the result.

**Deliberately not a check, and deliberately not under `tools/`.** The harness
produces timings, which call for judgment rather than a pass or a fail.
`CLAUDE.md` is explicit that a check which cannot decide is worse than none.
The standard-library-only rule applies to `tools/` and `.claude/hooks/`, not to
everything runnable. Those are the directories that a bare `python3` invokes
outside the project virtualenv, which is why
`tests/unit/test_tools_portability.py` enforces the rule on them by path. This
harness imports PySide6 and the package itself, so it could only ever run under
the virtualenv. `test_frame_cost.py` beside it is the decidable half. It checks
that the harness still runs and still reports three stages, and it asserts
nothing about the numbers.
"""

import argparse
import math
import os
import statistics
import sys
from dataclasses import dataclass
from time import perf_counter

from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QScrollArea

from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import (
    MAX_DISPLAYED_RUNS,
    RENDER_INTERVAL_S,
    SIMULATION_STEP_S,
    SIMULATION_TICK_INTERVAL_S,
)
from anesthesia_sim.app.playback import playback_rate_for
from anesthesia_sim.app.qt_chart import ConcentrationChart
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.core.units import MILLISECONDS_PER_SECOND, SECONDS_PER_MINUTE

#: The window size at which the dashboard is measured, matching the size in
#: `tests/integration/test_qt_rendering.py`. It is a parameter of the
#: measurement rather than a detail. A frame is assembled from the plot's
#: laid-out width, so the chart's pixel width sets how many points `present`
#: downsamples to and hands the toolkit to paint. The size is declared here
#: rather than imported from that module, because the two are separate
#: decisions that happen to agree.
WINDOW_WIDTH_PX = 1600
WINDOW_HEIGHT_PX = 1000

#: The highest rate on the interface's own ladder of playback rates, which is
#: `app/playback.py`'s `SUPPORTED_PLAYBACK_RATES`. It is the only rate at which
#: frame cost is in question.
DEFAULT_MULTIPLIER = 300

#: The number of frames measured. Twenty is enough for the median to be stable
#: across runs here, and cheap enough that the harness stays a three-second
#: command.
DEFAULT_FRAMES = 20

#: How many minutes of simulated run the dashboard holds before the first
#: measured frame. It is an hour, because cost grows with recorded history, and
#: an unwarmed run measures the cheapest case the application ever has.
DEFAULT_WARM_UP_MINUTES = 60

#: The number of runs drawn: the one run that the application opens with. A
#: second run is the branch a learner takes, and `--runs` measures it, up to
#: `MAX_DISPLAYED_RUNS`.
DEFAULT_RUNS = 1


@dataclass(frozen=True, slots=True)
class FrameSample:
    """The cost of one frame's three stages, in seconds.

    Attributes:
        advance_s: The time for every `controller.advance` call that this frame
            makes, across every run the dashboard draws.
        present_s: The time for `SimulationView.present(False)`, which
            assembles the frame.
        paint_s: The time for the `processEvents()` call that dispatches the
            repaint that `present` scheduled.
        settled_s: The time for a second `processEvents()` call with nothing
            pending. It is the control for `paint_s`, not a stage of the frame.
    """

    advance_s: float
    present_s: float
    paint_s: float
    settled_s: float

    @property
    def interface_s(self) -> float:
        """Assembly and paint together: the part of the frame's cost that is not the simulation."""

        return self.present_s + self.paint_s

    @property
    def total_s(self) -> float:
        """The whole frame, excluding the control."""

        return self.advance_s + self.interface_s


@dataclass(frozen=True, slots=True)
class Measurement:
    """One invocation of the harness: its configuration, and one sample per measured frame.

    Attributes:
        multiplier: The playback rate measured, in simulated seconds per
            real second.
        runs: How many runs the dashboard drew. This is counted on the
            dashboard rather than taken from the request, so that the figure
            names what was measured.
        steps_per_frame: The simulation steps that one frame advances each run
            at that rate.
        budget_s: The real seconds a frame has, which is `RENDER_INTERVAL_S`.
        warm_up_s: Simulated seconds every run ran before the first
            measured frame.
        samples: One per measured frame, in order.
    """

    multiplier: int
    runs: int
    steps_per_frame: int
    budget_s: float
    warm_up_s: float
    samples: tuple[FrameSample, ...]

    def median_s(self, stage: str) -> float:
        """The median of one stage across the measured frames.

        Args:
            stage: An attribute or property of `FrameSample`: one of
                `advance_s`, `present_s`, `paint_s`, `settled_s`,
                `interface_s` or `total_s`.

        Returns:
            The median, in seconds.
        """

        return statistics.median(float(getattr(sample, stage)) for sample in self.samples)

    def worst_s(self, stage: str) -> float:
        """The slowest measured frame for one stage, in seconds."""

        return max(float(getattr(sample, stage)) for sample in self.samples)


def steps_per_frame(multiplier: int) -> int:
    """How many simulation steps one rendered frame advances at this playback rate.

    The count is derived from the three shipped cadence constants rather than
    written down. So a change to the tick interval, the render interval or the
    step moves the measurement rather than silently invalidating it.

    Args:
        multiplier: Simulated seconds per real second, as carried by one of
            `app/playback.py`'s `SUPPORTED_PLAYBACK_RATES`.

    Returns:
        Steps per frame, at least one.

    Raises:
        SimulationConfigurationError: If the multiplier is not one the
            interface offers, or does not give a whole number of steps at the
            shipped intervals. Such a multiplier is refused rather than
            rounded, for the reason that `app/playback.py` gives: a fractional
            rate measured as a whole one measures a cadence that the
            application never runs.
    """

    rate = playback_rate_for(multiplier)
    per_tick = rate.steps_per_tick(
        tick_interval_s=SIMULATION_TICK_INTERVAL_S, simulation_step_s=SIMULATION_STEP_S
    )
    ticks = round(RENDER_INTERVAL_S / SIMULATION_TICK_INTERVAL_S)

    return per_tick * ticks


def _application() -> QApplication:
    """Return the `QApplication` to measure under, reusing one that pytest has already built.

    `QT_QPA_PLATFORM` is set here rather than at import, which is where
    `tests/conftest.py` sets it for the test tree. Qt resolves the platform
    plugin when the application is constructed, so setting the variable
    immediately before that construction is early enough. This was measured on
    2026-09-19 against an environment with the variable unset. If it is left
    unset, Qt picks `xcb` on Linux, and `QApplication` aborts the process where
    no display is attached. That is every CI runner and every web-container
    session.

    The function uses `setdefault`, so that a developer on a desktop who wants to
    watch the frames keeps the platform they chose, and so that a pytest run
    keeps the platform that conftest set.
    """

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    existing = QApplication.instance()

    return existing if isinstance(existing, QApplication) else QApplication(sys.argv[:1])


def _bring_chart_into_view(view: SimulationView) -> None:
    """Scroll the dashboard's page until the concentration chart is wholly in the window.

    The event loop paints only what is in view. So a chart below the fold is
    measured as nearly free to paint, which is a plausible number for a paint
    that did not happen. At this window size, a second run's readouts push the
    chart below the fold. In a measurement on 2026-10-01, the one-run chart
    spans y 520-880 of the 1000 px page viewport, and the two-run chart spans
    848-1208. The two-run paint read 5.5 ms against one run's 14.9 ms until the
    chart was scrolled into view. A reader comparing two runs scrolls to the
    chart, so that is the frame measured. Where the chart is already in view, as
    the one-run dashboard's chart is at this size, nothing moves.

    Raises:
        ValueError: If the dashboard does not contain exactly one concentration
            chart, and exactly one scroll area around it, because the area to
            scroll would then be a guess. The control-change record also
            scrolls within itself, but it does not contain the chart.
        RuntimeError: If the chart is still not wholly in view, as would happen
            in a window shorter than the chart.
    """

    (chart,) = view.findChildren(ConcentrationChart)
    (page,) = (area for area in view.findChildren(QScrollArea) if area.isAncestorOf(chart))
    page.ensureWidgetVisible(chart, 0, 0)
    viewport = page.viewport()
    top = chart.mapTo(viewport, QPoint(0, 0)).y()

    if top < 0 or top + chart.height() > viewport.height():
        raise RuntimeError(
            f"the concentration chart spans y {top} to {top + chart.height()} of a "
            f"{viewport.height()} px page, so part of it is out of view and its paint "
            "would be measured as cheaper than it is"
        )


def measure(
    *,
    multiplier: int = DEFAULT_MULTIPLIER,
    frames: int = DEFAULT_FRAMES,
    warm_up_s: float = DEFAULT_WARM_UP_MINUTES * SECONDS_PER_MINUTE,
    runs: int = DEFAULT_RUNS,
) -> Measurement:
    """Drive a real dashboard frame by frame and time each frame's three stages.

    The dashboard is opened as `main.py` opens it: a case over a fresh trunk,
    and the view over that trunk with the case beside it. So the branch control
    is drawn and refreshed every frame, as it is in the application. The view is
    then sized to the fixed window below rather than maximized, because the
    chart's pixel width is part of the configuration. It is then shown, left to
    settle its layout, and presented. That first frame reads the plot's laid-out
    width, so it is drawn before the measured frames rather than among them.

    Each run after the first is a branch that the case takes at induction,
    before the warm-up. It is added to the shown dashboard by
    `SimulationView.add_run`, which is the route the branch control takes. The
    page is then scrolled to bring the chart into view
    (`_bring_chart_into_view` says why) and presented once more before the
    measured frames. A branch taken at induction holds as much recorded run as
    the trunk, so this is the most expensive two-run frame at a given warm-up. A
    branch taken later is drawn only from its fork instant.

    Args:
        multiplier: The playback rate to measure, in simulated seconds per
            real second.
        frames: How many frames to time. At least one.
        warm_up_s: Simulated seconds every run runs before the first
            measured frame. Not negative.
        runs: How many runs the dashboard draws, from one to
            `MAX_DISPLAYED_RUNS`.

    Returns:
        The configuration and one `FrameSample` per measured frame.

    Raises:
        ValueError: If `frames` is less than one, `warm_up_s` is negative, or
            `runs` is a count that the dashboard cannot draw. The run count is
            checked before the warm-up. Otherwise the warm-up would be paid for
            first, and only then would the dashboard refuse the extra run.
        SimulationConfigurationError: If the rate is not one the interface
            offers, as `steps_per_frame` checks.
        RuntimeError: If a run did not advance by exactly the steps that this
            harness asked for. A halted or capped run makes
            `controller.advance` a no-op that returns immediately. That would
            report the simulation as free, which is a plausible number for a
            measurement that did not happen.
    """

    if frames < 1:
        raise ValueError(f"a measurement times at least one frame, not {frames}")

    if warm_up_s < 0.0:
        raise ValueError(f"warm_up_s is a length of simulated run, not {warm_up_s}")

    if not 1 <= runs <= MAX_DISPLAYED_RUNS:
        raise ValueError(f"a dashboard draws between 1 and {MAX_DISPLAYED_RUNS} runs, not {runs}")

    per_frame = steps_per_frame(multiplier)
    application = _application()
    case = BranchedCase(SimulationController())
    # The trunk's first fork point is its opening, at induction.
    induction_s = case.fork_points_s[0]

    for _ in range(runs - 1):
        case.fork_at(induction_s)

    for controller in case.runs:
        controller.start()

        for _ in range(round(warm_up_s / SIMULATION_STEP_S)):
            controller.advance(SIMULATION_STEP_S)

    view = SimulationView((case.trunk,), case=case)
    view.resize(WINDOW_WIDTH_PX, WINDOW_HEIGHT_PX)
    view.show()
    application.processEvents()
    view.present(False)
    application.processEvents()

    for branch in case.branches:
        view.add_run(branch)

    application.processEvents()
    _bring_chart_into_view(view)
    view.present(False)
    application.processEvents()

    # The runs that the dashboard draws are the runs that each frame advances.
    # In the application, every displayed run is advanced by its own step timer.
    drawn = tuple(run.controller for run in view.runs)
    samples = []

    try:
        for _ in range(frames):
            started = perf_counter()

            for controller in drawn:
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

    for index, controller in enumerate(drawn):
        elapsed_s = controller.snapshot().elapsed_s

        if not math.isclose(elapsed_s, expected_s, rel_tol=0.0, abs_tol=SIMULATION_STEP_S / 2):
            raise RuntimeError(
                f"run {index + 1} of {len(drawn)} advanced {elapsed_s} simulated seconds where "
                f"this measurement asked for {expected_s}; a run that is halted or past its "
                f"supported length takes no steps, so the timings above are not a measurement "
                f"of the simulation"
            )

    return Measurement(
        multiplier=multiplier,
        runs=len(drawn),
        steps_per_frame=per_frame,
        budget_s=RENDER_INTERVAL_S,
        warm_up_s=warm_up_s,
        samples=tuple(samples),
    )


def _milliseconds(seconds: float) -> str:
    """Format one stage's cost as a string in milliseconds.

    Every reading uses two decimals, including the control, which is the one
    reading that is meant to be near zero. Rounding the control to the one
    decimal that the stages would carry prints `0.1 ms`, where the distinction
    being drawn is between that and 15 ms.
    """

    return f"{seconds * MILLISECONDS_PER_SECOND:.2f} ms"


def report(measurement: Measurement) -> str:
    """Format the measurement as the paragraph that a session would otherwise write by hand."""

    budget = measurement.budget_s
    total = measurement.median_s("total_s")
    rows = (
        ("advance (simulation)", "advance_s"),
        ("present (assembly)", "present_s"),
        ("paint (event loop)", "paint_s"),
    )
    runs = f"{measurement.runs} run" if measurement.runs == 1 else f"{measurement.runs} runs"
    lines = [
        f"Frame cost at {measurement.multiplier}x real time, {runs} on the dashboard, "
        f"{len(measurement.samples)} frames, warmed to "
        f"{measurement.warm_up_s / SECONDS_PER_MINUTE:g} min of simulated run.",
        f"{measurement.steps_per_frame} steps advanced per frame in each run, against a "
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
        A process exit status, which is always 0, because a measurement has no
        verdict to fail on. Only the harness itself can fail, and it raises an
        exception when it does.
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
    parser.add_argument(
        "--runs",
        type=int,
        choices=range(1, MAX_DISPLAYED_RUNS + 1),
        default=DEFAULT_RUNS,
        help=f"runs the dashboard draws, the trunk and its branches (default {DEFAULT_RUNS})",
    )
    arguments = parser.parse_args(argv)

    print(
        report(
            measure(
                multiplier=arguments.rate,
                frames=arguments.frames,
                warm_up_s=arguments.warm_up_minutes * SECONDS_PER_MINUTE,
                runs=arguments.runs,
            )
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
