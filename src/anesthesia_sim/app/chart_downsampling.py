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
"""

from bisect import bisect_left
from collections.abc import Callable, Sequence

__all__ = [
    "first_index_at_or_after",
    "select_envelope_indices",
]


def first_index_at_or_after[SampleT](
    samples: Sequence[SampleT],
    window_start_s: float,
    time_of: Callable[[SampleT], float],
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


def select_envelope_indices(
    values: Sequence[float],
    max_points: int,
) -> list[int]:
    """Select at most `max_points` sample indices, preserving every extreme.

    Splits `values` into equal-width buckets of consecutive samples and keeps
    the minimum and the maximum of each bucket, plus the first and last
    sample. Because both extremes of every bucket survive, the drawn trace
    spans the full range the samples actually covered: decimation can flatten
    the *shape* of a transient but cannot hide that it occurred.

    Bucketing is by sample index rather than by elapsed time. The two are
    equivalent while the simulation step is fixed, and index bucketing bounds
    the returned count exactly rather than leaving empty time buckets.

    Args:
        values: Recorded values for one trace, in sample order.
        max_points: Maximum number of indices to return. Must be at least 4,
            so that the two reserved endpoints leave at least one bucket.

    Returns:
        Ascending, duplicate-free indices into `values`, at most `max_points`
        of them. Index `0` and index `len(values) - 1` are always included
        when `values` is non-empty. Returns every index when `values` already
        fits within `max_points`.

    Raises:
        ValueError: If `max_points` is less than 4.
    """

    if max_points < 4:
        raise ValueError("max_points must be at least 4")

    sample_count = len(values)

    if sample_count <= max_points:
        return list(range(sample_count))

    # Two slots are reserved for the exact first and last samples; each
    # bucket contributes at most two more (its minimum and its maximum).
    bucket_count = (max_points - 2) // 2

    selected = {0, sample_count - 1}

    for bucket in range(bucket_count):
        start = (bucket * sample_count) // bucket_count
        stop = ((bucket + 1) * sample_count) // bucket_count

        if start >= stop:
            continue

        lowest = start
        highest = start

        for index in range(start + 1, stop):
            value = values[index]

            if value < values[lowest]:
                lowest = index

            if value > values[highest]:
                highest = index

        selected.add(lowest)
        selected.add(highest)

    return sorted(selected)
