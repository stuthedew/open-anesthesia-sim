"""Unit tests for M4 chart sample selection.

The properties under test are presentation-correctness properties, not
cosmetic ones: a selection that drops the newest sample makes the graph
disagree with the numeric readouts, and one that drops an extreme shows a
curve the simulation never produced.

Two of them are cost properties, and they are asserted as *counts of samples
read* rather than as durations, for the reason the rest of this project
asserts counts: a timing assertion is flaky on shared hardware, while the
number of reads is exact and is the quantity the cost is proportional to.
"""

import math

import pytest

from anesthesia_sim.app.chart_downsampling import (
    FINEST_CACHED_BUCKET_SAMPLES,
    M4Aggregate,
    M4AggregateCache,
    first_index_at_or_after,
    merge_m4_aggregates,
)


class _CountingCache(M4AggregateCache):
    """A cache that records how many recorded values its scans read.

    Subclassed rather than instrumented from outside because the property
    both cost tests state - that no recorded sample is visited twice - is a
    statement about where the work happens, and `_scan` is the only place
    this class ever touches a recorded value.
    """

    def __init__(self) -> None:
        super().__init__()
        self.scanned = 0

    def _scan(self, start: int, stop: int) -> M4Aggregate | None:
        self.scanned += stop - start

        return super()._scan(start, stop)


def _reference_aggregate(values: list[float | None], start: int, stop: int) -> M4Aggregate | None:
    """M4's Definition 2 read straight off the values, for comparison.

    Deliberately the naive reading - filter to the defined samples, take the
    first, the last, the lowest and the highest - so that the cached answer
    is checked against the definition rather than against another version of
    itself.
    """

    defined = [(index, values[index]) for index in range(start, stop) if values[index] is not None]

    if not defined:
        return None

    lowest = min(defined, key=lambda pair: (pair[1], pair[0]))
    highest = max(defined, key=lambda pair: (pair[1], -pair[0]))

    return M4Aggregate(
        first_index=defined[0][0],
        last_index=defined[-1][0],
        lowest_index=lowest[0],
        highest_index=highest[0],
        lowest_value=lowest[1],
        highest_value=highest[1],
    )


def test_first_index_at_or_after_finds_window_start() -> None:
    times_s = [0.0, 0.1, 0.2, 0.3, 0.4]

    assert first_index_at_or_after(times_s, 0.0) == 0
    assert first_index_at_or_after(times_s, 0.2) == 2
    assert first_index_at_or_after(times_s, 0.25) == 3


def test_first_index_at_or_after_handles_window_outside_the_samples() -> None:
    times_s = [1.0, 2.0, 3.0]

    assert first_index_at_or_after(times_s, 0.0) == 0
    assert first_index_at_or_after(times_s, 99.0) == 3
    assert first_index_at_or_after([], 5.0) == 0


def test_an_aggregate_lists_its_tuples_once_each_in_time_order() -> None:
    """A rising bucket's lowest value is its first sample, and is drawn once."""

    rising = M4AggregateCache.of([1.0, 2.0, 3.0, 4.0]).aggregate(0, 4)

    assert rising is not None
    assert (rising.first_index, rising.last_index) == (0, 3)
    assert (rising.lowest_index, rising.highest_index) == (0, 3)
    assert rising.indices == (0, 3)

    dipping = M4AggregateCache.of([2.0, 9.0, 0.0, 2.0]).aggregate(0, 4)

    assert dipping is not None
    assert dipping.indices == (0, 1, 2, 3)


def test_merging_two_groups_matches_aggregating_them_together() -> None:
    """The monoid M4 is cached on: adjacent groups combine without a rescan."""

    values = [3.0, 1.0, 4.0, 1.0, 5.0, 9.0, 2.0, 6.0]
    cache = M4AggregateCache.of(values)
    earlier = cache.aggregate(0, 4)
    later = cache.aggregate(4, 8)

    assert earlier is not None
    assert later is not None
    assert merge_m4_aggregates(earlier, later) == cache.aggregate(0, 8)


def test_merging_keeps_the_earlier_position_when_two_samples_tie() -> None:
    """Ties resolve the same way whichever order the ladder was built in."""

    tied = M4AggregateCache.of([1.0, 5.0, 1.0, 5.0]).aggregate(0, 4)

    assert tied is not None
    assert tied.lowest_index == 0
    assert tied.highest_index == 1


def test_aggregates_merge_without_revisiting_samples() -> None:
    """Maintaining the ladder reads every sample once, whatever its height.

    This is what makes the cache affordable to keep: the finest tier reads
    each sample as its own bucket closes, and every tier above it is built
    by merging the tier below - arithmetic on six numbers, with no read back
    into the run. A ladder that rebuilt each tier from the samples would
    cost a factor of its own height on every recorded sample, five times a
    second, for as long as the simulation runs.

    Asserted as an equality rather than a bound. The count is the samples
    lying in buckets that have completed; the trailing partial bucket has
    not been read at all, because reading it before it is final would be
    work thrown away on the next sample.
    """

    cache = _CountingCache()
    sample_count = 40 * FINEST_CACHED_BUCKET_SAMPLES + 7

    for index in range(sample_count):
        cache.record((index * 37 % 101) / 100.0)

    completed = sample_count - sample_count % FINEST_CACHED_BUCKET_SAMPLES

    assert cache.scanned == completed
    # The ladder is five tiers deep at this length, so the equality above is
    # about merging rather than about there being nothing to merge.
    assert cache.aggregate(0, sample_count) is not None


def test_reading_a_window_costs_the_same_however_wide_it_is() -> None:
    """`PL-D9WD`: a twelve-hour scale must cost what a fifteen-minute one does.

    Decimation without a cache rescans the visible window on every frame, so
    the per-frame cost is a function of the width shown: measured
    2026-09-04 over six traces, 4.5 ms at fifteen minutes and 350 ms at
    twelve hours, against a 200 ms frame budget.

    With the cache, a window is read as completed buckets plus the unaligned
    remainder at each of its two ends, and only that remainder touches a
    recorded value. The bound below is therefore a constant of the grain,
    and it does not contain the window width or the run length at all.
    """

    cache = _CountingCache()

    for index in range(200_000):
        cache.record(math.sin(index / 900.0))

    reads: list[int] = []

    for width in (5_000, 20_000, 80_000, 200_000):
        cache.scanned = 0
        drawn = cache.select_indices(200_000 - width, 200_000, column_budget=150)
        reads.append(cache.scanned)

        assert drawn, "the window drew nothing, so the read count proves nothing"

    assert max(reads) <= 4 * FINEST_CACHED_BUCKET_SAMPLES, reads


def test_a_cached_aggregate_matches_the_definition_over_every_range() -> None:
    """Every range of a run, against M4's Definition 2 read off the values."""

    values: list[float | None] = [
        None if index % 23 == 5 else float((index * 41) % 97) for index in range(300)
    ]
    cache = M4AggregateCache.of(values)

    for start in range(0, 300, 7):
        for stop in range(start, 301, 11):
            assert cache.aggregate(start, stop) == _reference_aggregate(values, start, stop), (
                start,
                stop,
            )


def test_recording_a_nan_is_refused() -> None:
    """A broken model output must not become a silent gap in the trace."""

    with pytest.raises(ValueError, match="must not be a NaN"):
        M4AggregateCache().record(float("nan"))


def test_an_undefined_sample_contributes_no_tuple() -> None:
    """A sample the quantity is undefined at is skipped, not substituted."""

    cache = M4AggregateCache.of([1.0, None, 5.0, None])
    aggregate = cache.aggregate(0, 4)

    assert aggregate is not None
    assert (aggregate.first_index, aggregate.last_index) == (0, 2)
    assert (aggregate.lowest_index, aggregate.highest_index) == (0, 2)
    assert math.isnan(cache.value(1))


def test_a_range_with_no_defined_sample_has_no_aggregate() -> None:
    cache = M4AggregateCache.of([None] * 100)

    assert cache.aggregate(0, 100) is None
    assert cache.select_indices(0, 100, column_budget=8) == []


def test_selection_returns_every_sample_when_they_already_fit() -> None:
    cache = M4AggregateCache.of([0.0, 1.0, 2.0, 3.0])

    assert cache.select_indices(0, 4, column_budget=4) == [0, 1, 2, 3]
    assert cache.select_indices(0, 4, column_budget=10) == [0, 1, 2, 3]
    assert M4AggregateCache.of([]).select_indices(0, 0, column_budget=8) == []
    assert M4AggregateCache.of([1.5]).select_indices(0, 1, column_budget=8) == [0]


def test_selection_rejects_a_budget_with_no_room_to_bucket() -> None:
    cache = M4AggregateCache.of([0.0, 1.0, 2.0, 3.0, 4.0])

    with pytest.raises(ValueError, match="at least 2"):
        cache.select_indices(0, 5, column_budget=1)


def test_selection_rejects_a_window_outside_the_recorded_run() -> None:
    cache = M4AggregateCache.of([0.0, 1.0, 2.0])

    with pytest.raises(ValueError, match="within the recorded run"):
        cache.select_indices(0, 4, column_budget=8)

    with pytest.raises(ValueError, match="within the recorded run"):
        cache.select_indices(2, 1, column_budget=8)


def test_selection_respects_the_column_budget() -> None:
    """The budget bounds columns; points follow at up to four per column."""

    cache = M4AggregateCache.of([float(index % 7) for index in range(3000)])

    for column_budget in (2, 3, 10, 51, 150):
        indices = cache.select_indices(0, 3000, column_budget)

        assert len(indices) <= 4 * column_budget
        assert indices == sorted(set(indices))


def test_selection_always_keeps_the_windows_own_endpoints() -> None:
    """The graph's right-hand end and the numeric readouts cannot disagree."""

    cache = M4AggregateCache.of([float(index % 13) for index in range(5000)])

    for start, stop in ((0, 5000), (17, 4999), (3333, 5000)):
        indices = cache.select_indices(start, stop, column_budget=20)

        assert indices[0] == start
        assert indices[-1] == stop - 1


def test_selection_keeps_a_transient_spike() -> None:
    values = [0.5] * 4000
    values[1234] = 9.0
    values[2345] = -9.0
    cache = M4AggregateCache.of(values)

    indices = cache.select_indices(0, 4000, column_budget=20)

    assert 1234 in indices
    assert 2345 in indices


def test_selection_spans_the_full_value_range() -> None:
    values = [float((index * 31) % 89) for index in range(4000)]
    cache = M4AggregateCache.of(values)

    selected = [values[index] for index in cache.select_indices(0, 4000, column_budget=32)]

    assert min(selected) == min(values)
    assert max(selected) == max(values)


def test_selection_matches_a_hand_computed_case() -> None:
    # Ten samples, budget 6: the width ladder takes the first power of two at
    # which the window spans no more than six buckets even when it straddles
    # a boundary, which is 2 (five buckets plus the straddle allowance). The
    # buckets are [0,2), [2,4), [4,6), [6,8), [8,10) and each contributes its
    # first, last, lowest and highest.
    #
    # Bucket [0,2) holds 4.0 and 1.0: first 0, last 1, lowest 1, highest 0 ->
    # {0, 1}. [2,4) holds 2.0, 8.0 -> {2, 3}. [4,6) holds 3.0, 5.0 -> {4, 5}.
    # [6,8) holds 2.0, 0.0 -> {6, 7}. [8,10) holds 1.0, 3.0 -> {8, 9}.
    values = [4.0, 1.0, 2.0, 8.0, 3.0, 5.0, 2.0, 0.0, 1.0, 3.0]

    assert M4AggregateCache.of(values).select_indices(0, 10, column_budget=6) == list(range(10))


def test_selection_holds_its_choices_as_the_run_grows() -> None:
    """PL-Q197: a selection re-derived per frame moves every drawn point.

    Buckets are anchored to absolute sample index, so appending samples
    leaves every completed bucket choosing the sample it already chose. Only
    the newest, still-filling bucket moves. Before that anchoring, a run of
    this length re-chose every one of its ~300 slots on every frame, and the
    ~1 800 resulting coordinate patches across six traces saturated the
    Flutter client.

    The sample counts below step by two, which is one render tick at
    `RENDER_INTERVAL_S` over `SIMULATION_STEP_S`, and stay inside one rung of
    the width ladder so that no frame here is a deliberate rebuild.
    """

    cache = M4AggregateCache.of([0.08 * (1.0 - 0.999**index) for index in range(4000)])
    previous: list[int] | None = None
    worst_moved = 0

    for sample_count in range(3000, 3040, 2):
        indices = cache.select_indices(0, sample_count, column_budget=150)

        if previous is not None:
            shared = min(len(indices), len(previous))
            worst_moved = max(
                worst_moved,
                sum(
                    1
                    for new, old in zip(indices[:shared], previous[:shared], strict=True)
                    if new != old
                ),
            )

        previous = indices

    assert worst_moved <= 4, f"{worst_moved} drawn points moved in one render tick"


def test_selection_is_anchored_to_the_run_not_the_window() -> None:
    """Two windows over the same run agree about the samples they share.

    This is the property that makes a *scrolling* window cheap as well as a
    growing one: sliding the window does not re-choose the samples that
    remain inside it.
    """

    cache = M4AggregateCache.of([float((index * 37) % 101) for index in range(4000)])

    from_3072 = set(cache.select_indices(3072, 4000, column_budget=150))
    from_3104 = set(cache.select_indices(3104, 4000, column_budget=150))

    # Endpoints are the two windows' own, so they are excused; everything
    # chosen for its own sake inside the overlap must agree.
    overlap = {sample for sample in from_3072 if 3104 < sample < 3999}

    assert overlap, "the windows shared no interior choices; the test proves nothing"
    assert overlap <= from_3104


def test_selection_is_deterministic() -> None:
    cache = M4AggregateCache.of([float((index * 17) % 53) for index in range(5000)])

    assert cache.select_indices(0, 5000, 128) == cache.select_indices(0, 5000, 128)


def test_selection_handles_a_flat_trace() -> None:
    cache = M4AggregateCache.of([2.5] * 500)

    indices = cache.select_indices(0, 500, column_budget=10)

    assert indices[0] == 0
    assert indices[-1] == 499
    assert all(cache.value(index) == 2.5 for index in indices)


def test_selection_never_draws_an_undefined_sample() -> None:
    """A gap in a quotient's domain contributes no point, at any budget."""

    values: list[float | None] = [
        None if 400 <= index < 900 else float(index % 11) for index in range(2000)
    ]
    cache = M4AggregateCache.of(values)

    for column_budget in (2, 8, 150, 4000):
        indices = cache.select_indices(0, 2000, column_budget)

        assert not any(400 <= index < 900 for index in indices)
        assert all(not math.isnan(cache.value(index)) for index in indices)
