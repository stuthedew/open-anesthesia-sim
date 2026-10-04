"""What one frame of the running dashboard costs, split into simulation, assembly and paint.

Run it: `uv run python tests/benchmarks/frame_cost.py`, about three seconds,
for the one-run dashboard the application opens with. Add `--runs 2` for the
trunk and branch that taking a fork draws on one chart, about four.

**Why this is written down rather than re-derived.** `PL-YSZN`, `PL-KP7H`,
`PL-R2YM` and `PL-SQJ1` were each answered by a throwaway harness, and
`PL-0VM7`, `PL-Q197` and `PL-R460` each built one and discarded it. The
numbers survived in the items; the *method* did not, and it is the method
that is subtle enough to get wrong. This is the fifth writing of it and the
first one kept (`PL-ZG5J`).

**What a frame is here.** The running application holds a step timer for
each run it draws (`app/run_view.py`) and one render timer
(`app/simulation_view.py`): every run ticks every
`SIMULATION_TICK_INTERVAL_S` real seconds, taking
`PlaybackRate.steps_per_tick` steps of `SIMULATION_STEP_S`, and the display
redraws every `RENDER_INTERVAL_S` real seconds. So a *frame* is one render
interval's worth of both: `RENDER_INTERVAL_S / SIMULATION_TICK_INTERVAL_S`
ticks of every run's simulation, then one presentation. At 300x that is 600
steps a run against a 200 ms budget, and a second run doubles the steps
without widening the budget. Both numbers are derived from the shipped
constants here, never written in, so a cadence change moves this measurement
with it.

**The three stages, and why the third is what a harness gets wrong.**

1. `controller.advance(SIMULATION_STEP_S)`, once per step of every run - the
   simulation.
2. `SimulationView.present(False)` - assembling the frame and handing it to
   the widgets.
3. `QApplication.processEvents()` - the paint.

Stage 3 is not bookkeeping. `qt_chart.ChartPlot.draw` is `setData`, `setPos`
and `setTicks` throughout: it schedules a repaint and rasterizes nothing, so
`present` returns before the frame has been drawn and the frame is complete
only once the event loop dispatches the paint event. This harness at its
defaults, 2026-09-19 in the web container, one run, medians over three
invocations: advance 12.0 ms, present 15.3 ms, paint 13.1 ms, so the
interface costs 28.4 ms of a 40.4 ms frame. A two-stage harness would have
reported that interface at 15.3 ms - 46% low, in the flattering direction -
and the control below is what rules out the alternative reading, that stage
3 is the event loop rather than the frame.

**Two runs on one chart** (`PL-WPDB`). The same defaults, 2026-10-01 in the
web container, medians over three invocations of each, alternated. One run:
advance 12.8 ms, present 16.8 ms, paint 14.2 ms, a 44.2 ms frame, 22% of the
budget. Two runs: advance 25.1 ms, present 30.2 ms, paint 13.7 ms, a 68.9 ms
frame, 34% of it. The second run doubles the simulation and nearly doubles
the assembly, bringing its own readouts and control timeline with it. The
paint holds level, but it rasterizes a different chart: comparing caps it at
two compartments a run (`COMPARED_COMPARTMENT_CAP`), so it draws four curves
where one run draws six, at wider pens. The level paint is measured with the
chart in view, which `_bring_chart_into_view` arranges. Opening the
dashboard over a case, so the branch control is drawn and refreshed, moved
the one-run frame by less than the spread between invocations: `main`'s
harness read 44.2 ms in the same container, so what moved it from
2026-09-19's 40.4 ms is the container or the tree since then, not the case.

Under Flet the same third position was held by `page.update()` against a
session whose connection serialized each outbound message; that was the
subtle part then, for the same reason it is the paint now. The stage the
toolkit charges for is never the one the code makes obvious.

`settled_s` is the control for stage 3: a second `processEvents()` with
nothing owed. It comes back near zero, which is what says the paint is this
frame's rasterization rather than fixed event-loop overhead. Read it on
every invocation - a paint that stops being distinguishable from it means
either the measurement or the chart has changed.

**What this does not measure.** Not a wall-clock frame rate: nothing here
sleeps, so the stages run back to back rather than at the cadence the timers
impose, and an invocation of this harness is not a claim about what a reader
sees.
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

#: Runs drawn: the one the application opens with. A second is the branch a
#: learner takes, and `--runs` measures it, up to `MAX_DISPLAYED_RUNS`.
DEFAULT_RUNS = 1


@dataclass(frozen=True, slots=True)
class FrameSample:
    """What one frame's three stages cost, in seconds.

    Attributes:
        advance_s: Every `controller.advance` call this frame takes, across
            every run the dashboard draws.
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
        runs: How many runs the dashboard drew, counted on the dashboard
            rather than taken from the request, so the figure names what
            was measured.
        steps_per_frame: Simulation steps one frame advances each run at
            that rate.
        budget_s: Real seconds a frame has, which is `RENDER_INTERVAL_S`.
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


def _bring_chart_into_view(view: SimulationView) -> None:
    """Scroll the dashboard's page until the concentration chart is wholly in the window.

    The event loop paints only what is in view, so a chart below the fold
    is measured as nearly free to paint: a plausible number for a paint that
    did not happen. At this window a second run's readouts push the chart
    below the fold. Measured 2026-10-01, the one-run chart spans y 520-880
    of the 1000 px page viewport and the two-run chart 848-1208, and the
    two-run paint read 5.5 ms against one run's 14.9 ms until the chart was
    scrolled into view. A reader comparing two runs scrolls to the chart, so
    that is the frame measured. Where the chart is already in view, as the
    one-run dashboard's is at this size, nothing moves.

    Raises:
        ValueError: If the dashboard does not hold exactly one scrolling
            page and one concentration chart, since which to scroll would
            then be a guess.
        RuntimeError: If the chart is still not wholly in view, as it
            would not be in a window shorter than the chart.
    """

    (page,) = view.findChildren(QScrollArea)
    (chart,) = view.findChildren(ConcentrationChart)
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

    The dashboard is opened as `main.py` opens it: a case over a fresh
    trunk, and the view over that trunk with the case beside it, so the
    branch control is drawn and refreshed every frame as it is in the
    application. It is then sized to the fixed window below rather than
    maximized, because the chart's pixel width is part of the configuration,
    shown, left to settle its layout, and presented. That first frame reads
    the plot's laid-out width, so it is drawn before the measured frames
    rather than among them.

    Each run past the first is a branch the case takes at induction before
    the warm-up, added to the shown dashboard by `SimulationView.add_run`,
    the route the branch control takes. The page is then scrolled to bring
    the chart into view (`_bring_chart_into_view` says why) and presented
    once more before the measured frames. A branch taken at induction holds
    as much recorded run as the trunk, so this is the dearest two-run frame
    at a given warm-up: a branch taken later is drawn only from its fork
    instant.

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
        ValueError: If `frames` is below one, `warm_up_s` is negative, or
            `runs` is a count the dashboard cannot draw. The last is checked
            before the warm-up, which a dashboard refusing the extra run
            would otherwise pay for first.
        SimulationConfigurationError: If the rate is not one the interface
            offers, per `steps_per_frame`.
        RuntimeError: If a run did not advance by exactly the steps this
            harness asked for. A halted or capped run makes
            `controller.advance` a no-op that returns immediately, which
            would report the simulation as free - a plausible number for a
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

    # What the dashboard draws, and so what each frame advances: in the
    # application every displayed run's own step timer advances it.
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
    """One stage's cost as a millisecond string.

    Two decimals throughout, including on the control, which is the one
    reading that is meant to be near zero: rounding it to the one decimal
    the stages would carry prints `0.1 ms` where the distinction being drawn
    is between that and 15 ms.
    """

    return f"{seconds * MILLISECONDS_PER_SECOND:.2f} ms"


def report(measurement: Measurement) -> str:
    """The measurement as the paragraph a session would otherwise write by hand."""

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
