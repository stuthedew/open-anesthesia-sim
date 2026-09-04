"""Choose which recorded samples a chart trace should draw.

Pure selection logic, independent of Flet and of the scientific core: every
function here returns *indices into a caller-supplied sequence* and performs
no unit conversion, no interpolation, and no invention of values. A drawn
point is therefore always a recorded sample, never a synthesized one.

Why this exists: the simulation records a sample every `SIMULATION_STEP_S`
(0.1 s), so an hour-long run holds 36 000 samples per trace, while the chart
is a few hundred pixels wide and shows a bounded time window. Handing every
recorded sample to the chart makes the render payload grow without bound for
as long as the simulation runs. Bounding the payload means drawing a subset.

Choosing that subset is a presentation-correctness problem, not merely a
performance one: a subset that drops a transient shows the learner a curve
the simulation never produced. `select_envelope_indices` therefore uses
min/max envelope decimation, which keeps both extremes of every bucket, so
no peak or trough can be decimated away regardless of the reduction ratio.
Plain stride sampling ("every Nth sample") is rejected for that reason even
though the current model's traces are smooth enough that it would usually
look the same.

The last recorded sample is always selected. The right-hand end of every
drawn trace is thus the same value the numeric readouts show, so the graph
and the readouts can never disagree about the current state.

**A bounded selection is not enough; the selection must also be stable.**
`chart_series.redraw_series` writes the chosen samples into chart points the
client already holds, and Flet patches every coordinate that changes. What
reaches the client each frame is therefore the count of points whose chosen
sample *moved*, not the count of points drawn. Bucketing by position within
the visible slice makes every boundary a function of how many samples the
slice currently holds, so one more sample shifts every boundary and every
drawn point takes a different sample than it held last frame — a full
rewrite, every frame, forever.

PL-Q197 measured the consequence on the real serializing connection: a
steady-state frame sent about 24 patch operations for the first 30 s of a
run and about 2 700 immediately after, a 150-fold step landing exactly where
`MAX_CHART_POINTS_PER_SERIES` starts decimating. The client was CPU-saturated
by roughly 18 000 tree mutations per second while the Python process sat at
under half a core, and input stopped being serviced.

Buckets are therefore anchored to *absolute* sample indices — position in the
run, not position in the visible slice — via `index_offset`. A bucket lying
wholly inside the window holds the same samples on every frame, so its two
chosen extremes never move and the client is told nothing about them. Only
the newest, still-filling bucket and the always-selected final sample change
from one frame to the next.

Holding that anchor as the window grows requires the bucket width to change
in steps rather than continuously, since a width recomputed per frame would
move every boundary again. `_stable_bucket_width` doubles, so the width is
constant across long stretches of a run and the whole selection is rebuilt
only on the handful of frames where it changes — about eight times over a
five-minute run. The cost of the ladder is that the point budget is not
always fully spent: between two rungs the selection uses somewhere from half
the budget to all of it. That is a deliberate trade of resolution the display
cannot resolve anyway, in exchange for a redraw the client can keep up with.
One rebuild per bucket width survives, and it is a floor rather than an
oversight. Once the window is full it slides along a fixed grid, so it spans
alternately `k` and `k+1` boundaries; the count of chosen samples must
therefore change, and any change shifts every later point one position along
a positional list. Removing it would mean either snapping the axis onto
bucket boundaries, which makes a smooth scroll jerk, or decimating from
before `min_x` and trusting the chart to clip points it was never given a
reason to draw. Neither is worth what it buys: measured, the surviving
rebuild costs about 2 200 operations once per bucket against about 20 on
every other frame, roughly 800 operations per second at the ceiling — some
twenty times below the rate that saturated the client.
"""

from bisect import bisect_left
from collections.abc import Callable, Sequence

__all__ = ["first_index_at_or_after", "select_envelope_indices"]


def first_index_at_or_after[SampleT](
    samples: Sequence[SampleT], window_start_s: float, time_of: Callable[[SampleT], float]
) -> int:
    """Index of the first sample at or after the start of the visible window.

    Binary search rather than a scan, so locating the window costs the same
    whether the run is a minute or a day old. That matters here: a linear
    step in the per-frame render path would reintroduce the unbounded growth
    that bounding the payload is meant to remove.

    Args:
        samples: Recorded samples ordered by ascending time. Simulation time
            advances by a fixed step, so this always holds.
        window_start_s: Start of the visible chart window in seconds.
        time_of: Reads the elapsed time in seconds from one sample.

    Returns:
        Index of the first sample at or after `window_start_s`, or
        `len(samples)` when every sample precedes it.
    """

    return bisect_left(samples, window_start_s, key=time_of)


def _stable_bucket_width(sample_count: int, bucket_budget: int) -> int:
    """Smallest power-of-two bucket width the visible window fits inside.

    Widths advance by doubling rather than being fitted exactly to
    `sample_count`, because an exactly fitted width would change on every
    frame and move every bucket boundary with it — the instability the
    module docstring describes. A doubling ladder changes width on a
    handful of frames per run instead.

    A window of `sample_count` samples starting at an arbitrary absolute
    index straddles at most one boundary more than its own length implies,
    so the partial bucket at each end is counted here rather than being
    discovered as an overrun of the point budget.

    Args:
        sample_count: Number of samples in the visible window.
        bucket_budget: Greatest number of buckets whose two extremes each
            still fit within the caller's point budget. Must be at least 2;
            a window straddling an anchored boundary needs two buckets'
            worth of budget, so one is not enough for the loop below to
            terminate, and the caller handles that case instead.

    Returns:
        Bucket width in samples: a power of two, at least 1.
    """

    width = 1

    while -(-sample_count // width) + 1 > bucket_budget:
        width *= 2

    return width


def select_envelope_indices(
    values: Sequence[float], max_points: int, index_offset: int = 0
) -> list[int]:
    """Select at most `max_points` sample indices, preserving every extreme.

    Splits the run into equal-width buckets of consecutive samples and keeps
    the minimum and the maximum of each bucket that the window overlaps, plus
    the first and last sample of the window. Because both extremes of every
    bucket survive, the drawn trace spans the full range the samples actually
    covered: decimation can flatten the *shape* of a transient but cannot
    hide that it occurred.

    Bucket boundaries fall on multiples of the bucket width in *absolute*
    sample index, which is what makes the selection stable from frame to
    frame; see the module docstring for why that is a correctness-relevant
    property of the rendered chart and not only a performance one. Bucketing
    is by sample index rather than by elapsed time. The two are equivalent
    while the simulation step is fixed, and index bucketing bounds the
    returned count exactly rather than leaving empty time buckets.

    Args:
        values: Recorded values for one trace, in sample order.
        max_points: Maximum number of indices to return. Must be at least 4,
            so that the two reserved endpoints leave at least one bucket.
        index_offset: Absolute index, within the whole recorded run, of
            `values[0]`. Bucket boundaries are anchored to it, so a window
            sliding along an unchanged run keeps choosing the same samples.
            Must not be negative.

    Returns:
        Ascending, duplicate-free indices into `values`, at most `max_points`
        of them. Index `0` and index `len(values) - 1` are always included
        when `values` is non-empty. Returns every index when `values` already
        fits within `max_points`.

    Raises:
        ValueError: If `max_points` is less than 4, or `index_offset` is
            negative.
    """

    if max_points < 4:
        raise ValueError("max_points must be at least 4")

    if index_offset < 0:
        raise ValueError("index_offset must not be negative")

    sample_count = len(values)

    if sample_count <= max_points:
        return list(range(sample_count))

    # Two slots are reserved for the exact first and last samples; each
    # bucket contributes at most two more (its minimum and its maximum).
    bucket_budget = (max_points - 2) // 2

    if bucket_budget < 2:
        # A window can straddle an anchored boundary, so anchoring costs one
        # bucket more than the window's own length implies. A budget of one
        # cannot pay for that, which leaves no width that fits and would spin
        # `_stable_bucket_width` forever. Such a budget is degenerate anyway —
        # a `max_points` of 4 or 5 — so it falls back to a single bucket over
        # the whole window: both extremes and both endpoints are still
        # selected, and the count still fits.
        bucket_spans = [(0, sample_count)]
    else:
        width = _stable_bucket_width(sample_count, bucket_budget)
        first_bucket = index_offset // width
        last_bucket = (index_offset + sample_count - 1) // width
        # Clamped to the window, so the buckets at each end contribute the
        # extremes of the part that is actually visible.
        bucket_spans = [
            (
                max(bucket * width - index_offset, 0),
                min((bucket + 1) * width - index_offset, sample_count),
            )
            for bucket in range(first_bucket, last_bucket + 1)
        ]

    selected = {0, sample_count - 1}

    for start, stop in bucket_spans:
        if start >= stop:
            continue

        lowest = highest = start
        # The two running extremes are carried as values as well as as
        # indices, so a comparison costs no read of its own. Reading
        # `values[lowest]` and `values[highest]` back on every step made
        # this scan about 2.8 reads per sample where one is enough; the
        # scan itself stays proportional to the window, because visiting
        # every sample of every bucket is what makes an envelope an
        # envelope (PL-MJ7B). `test_the_envelope_scan_reads_each_sample_once`
        # holds the constant at one.
        lowest_value = highest_value = values[start]

        for index in range(start + 1, stop):
            value = values[index]

            if value < lowest_value:
                lowest = index
                lowest_value = value

            if value > highest_value:
                highest = index
                highest_value = value

        selected.add(lowest)
        selected.add(highest)

    return sorted(selected)
