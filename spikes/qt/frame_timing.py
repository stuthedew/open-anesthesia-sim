"""Rolling frame-cost statistics for the Qt spike, in the split `PL-YSZN` used.

`PL-X9T3` asks for "the same three-stage split `PL-YSZN` used on Flet, so the
numbers are comparable rather than merely favourable". This module is what
produces them. It holds no Qt and no simulation state: it takes durations and
answers with a median and a p90 over a bounded window, which is the whole of
what a comparison against `PL-YSZN`'s table needs.

**Why a rolling window rather than a running mean.** A mean over the whole run
cannot show a frame cost that changes - and the question the spike is asked is
exactly whether it changes, with the point count, with the playback rate, and
with a slider being dragged. A window of the last `WINDOW_FRAMES` frames
answers "what does a frame cost *now*", which is what a reader watching the
display is comparing against what they see.

**p90 is nearest-rank, and it is stated rather than assumed.** With a window
this small the interpolated and nearest-rank definitions differ by a frame's
worth of ordering, and a figure that has to be read beside Flet's "20-30 ms
p90" is worth defining where it is computed. `percentile` below is the whole
definition.

**These are wall-clock durations of Python work.** `time.perf_counter` is
monotonic and the highest resolution the interpreter offers, so it is right
for an interval; it is not a claim about CPU time, and a frame that lost the
GIL or the scheduler is charged for the wait. That is the honest measure for
"how long did the frame take", which is the question, and it is the same
measure `PL-YSZN` used on Flet.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from math import ceil
from time import perf_counter
from types import TracebackType
from typing import Final

#: How many frames each stage keeps. At the spike's 5 Hz render cadence this
#: is a 24-second window - long enough that one slow frame does not move the
#: median, short enough that changing the playback rate or the chart source
#: shows up within a few seconds of doing it.
WINDOW_FRAMES: Final = 120


def percentile(sorted_samples: list[float], fraction: float) -> float:
    """The nearest-rank percentile of an ascending list.

    Nearest-rank rather than interpolated: every value it can return is a
    frame that actually happened, which is what makes "p90 is 4.1 ms" a
    statement about a frame rather than about an average of two.

    Args:
        sorted_samples: Ascending samples. Must not be empty.
        fraction: The percentile as a fraction, `0.9` for p90.

    Returns:
        The sample at the nearest rank at or above `fraction`.
    """

    rank = max(1, ceil(fraction * len(sorted_samples)))

    return sorted_samples[rank - 1]


@dataclass(slots=True)
class Stage:
    """One measured stage of a frame, and the last `WINDOW_FRAMES` of it.

    Attributes:
        label: What the stage is called on the instrument panel.
        flet_counterpart: The stage of `PL-YSZN`'s Flet table this one is the
            analogue of, or the empty string where Flet had no analogue.
            Carried here rather than written into the panel's layout so that
            the mapping between the two measurements is stated once, beside
            the numbers it governs - the comparison is the point of the
            measurement, and a mapping a reader has to reconstruct is one
            they will reconstruct differently.
        samples: Durations in milliseconds, oldest first, bounded to
            `WINDOW_FRAMES`.
    """

    label: str
    flet_counterpart: str
    samples: deque[float] = field(default_factory=lambda: deque(maxlen=WINDOW_FRAMES))

    def record(self, seconds: float) -> None:
        """Add one frame's duration, in seconds."""

        self.samples.append(seconds * 1000.0)

    @property
    def last_ms(self) -> float:
        """The most recent frame's duration, in milliseconds; 0 with no frames."""

        return self.samples[-1] if self.samples else 0.0

    @property
    def median_ms(self) -> float:
        """The window's median duration, in milliseconds; 0 with no frames."""

        if not self.samples:
            return 0.0

        return percentile(sorted(self.samples), 0.5)

    @property
    def p90_ms(self) -> float:
        """The window's p90 duration, in milliseconds; 0 with no frames."""

        if not self.samples:
            return 0.0

        return percentile(sorted(self.samples), 0.9)


class StageClock:
    """A context manager that charges its block to one stage.

    Used rather than a pair of `perf_counter` calls because a stage whose
    start and stop are written separately can be left unbalanced by an early
    return, and a stage that silently stops being recorded reads as a stage
    that became free.
    """

    __slots__ = ("_stage", "_started")

    def __init__(self, stage: Stage) -> None:
        self._stage = stage
        self._started = 0.0

    def __enter__(self) -> StageClock:
        self._started = perf_counter()

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._stage.record(perf_counter() - self._started)


@dataclass(slots=True)
class FrameCost:
    """Every stage the spike measures, in the order a frame performs them.

    The first three are `PL-YSZN`'s split, mapped onto a toolkit that has no
    diff: `advance` is the same call in both, `refresh` is the Flet view's
    per-frame Python work, and `handoff` is what `page.update()` was - the
    call that tells the toolkit the frame changed. The difference the spike
    exists to show is that Flet spent 98% of `page.update()` walking the
    control tree to find out *what* changed, and Qt's `handoff` does no such
    walk.

    `paint` has no Flet counterpart in `PL-YSZN` at all. Flet's rendering
    happens in a separate Flutter process, which that measurement could not
    reach; here it is a method call on a widget in this process, so it can be
    timed. `latency` is `PL-X9T3`'s second question - how long a callback
    ready to run waits - measured as the render timer's own lateness.
    """

    advance: Stage = field(default_factory=lambda: Stage("advance", "controller.advance"))
    refresh: Stage = field(default_factory=lambda: Stage("refresh", "_refresh_view"))
    handoff: Stage = field(default_factory=lambda: Stage("handoff", "page.update"))
    paint: Stage = field(default_factory=lambda: Stage("paint", ""))
    latency: Stage = field(default_factory=lambda: Stage("timer lateness", ""))

    def stages(self) -> tuple[Stage, ...]:
        """Every stage, in the order the instrument panel lists them."""

        return (self.advance, self.refresh, self.handoff, self.paint, self.latency)

    def reset(self) -> None:
        """Discard every recorded frame.

        Called when something that changes what a frame costs changes - the
        playback rate, the chart source, the time base - so that the window
        describes the configuration on screen rather than a mixture of two.
        A statistic averaged across a settings change is the stale-state
        failure `CLAUDE.md` names, in the one place on this window whose
        whole job is to be read as a number.
        """

        for stage in self.stages():
            stage.samples.clear()
