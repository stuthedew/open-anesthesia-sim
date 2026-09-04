r"""Choose which recorded samples a chart trace should draw, by M4.

Pure selection logic, independent of Flet and of the scientific core: every
public entry point here returns *indices into the recorded run* and performs
no unit conversion, no interpolation, and no invention of values. A drawn
point is therefore always a recorded sample, never a synthesized one.

Why this exists: the simulation records a sample every `SIMULATION_STEP_S`
(0.1 s), so an hour-long run holds 36 000 samples per trace, while the chart
is a few hundred pixels wide and shows a bounded time window. Handing every
recorded sample to the chart makes the render payload grow without bound for
as long as the simulation runs. Bounding the payload means drawing a subset.

Choosing that subset is a presentation-correctness problem, not merely a
performance one: a subset that drops a transient shows the learner a curve
the simulation never produced.

## The algorithm, and what it is taken from

`M4AggregateCache` implements **M4** as published — Jugel U, Jerzak Z,
Hackenbroich G, Markl V, "M4: A Visualization-Oriented Time Series Data
Aggregation", *Proceedings of the VLDB Endowment* 7(10):797-808, 2014, held
in `docs/references/` and summarized in that directory's `README.md`. Its
Definition 2 fixes what an M4 group contributes: the tuples at `min(v)`,
`max(v)`, `min(t)` and `max(t)` — the group's lowest value, its highest
value, its first sample and its last. Theorem 1 proves that a two-colour
line visualization of a series reduced that way equals the visualization of
the whole series.

Naming the algorithm is not decoration. This project's discipline is that a
displayed value is traceable to what produced it, and "the chart implements
M4 (Jugel et al. 2014)" is auditable against a paper on disk in a way that
"something M4-like" is not. What the code does and what the citation claims
therefore have to agree, which is why the departure below is stated rather
than glossed.

## Where this departs from Theorem 1, and why

**Theorem 1's exactness is conditional on the grouping**, and this chart does
not meet the condition. §6: "at nh = w, i.e., at any factor k of w, M4
provides perfect (error-free) visualizations. Any grouping with nh = k*w and
k in N+ also includes the min, max, first, and last tuples for nh = w." The
guarantee holds when the number of groups drawn is an *integer multiple* of
the chart's pixel-column count — not merely when it is finer than it.

Groups here are anchored to **absolute sample index**: bucket boundaries fall
on multiples of a power-of-two width counted from the first sample of the
run, never on divisions of the viewport. A grid anchored that way cannot also
be an integer multiple of an arbitrary chart width, and a grid that adapted to
the chart width would move on every resize and every scroll — which is the
instability `PL-Q197` was opened for and which the section below records the
cost of. So this implementation buys **stability at the cost of Theorem 1's
exactness condition**, landing in the paper's general case rather than its
perfect one. It is a trade, and it is the right one here; it is not exactness,
and nothing in this package may claim it is.

**What the missing guarantee actually costs is small for this data.** §4.3
names three error classes for aggregation that keeps fewer than four tuples
per group: E1, a missing line where a pixel column holds no selected tuple;
E2, a false line bridging an empty column; and E3, an undesired pixel from a
false inter-column line drawn between two consecutive extrema. E1 and E2 are
driven by "time series that have a very heterogeneous time distribution, i.e.,
notable gaps". This simulation records one sample every `SIMULATION_STEP_S`
exactly and has no gaps at all, so **E1 and E2 are structurally impossible
here** and only E3 remains.

Every later improvement moves the drawn chart *toward* Theorem 1 — a larger
column budget, fewer traces sharing the client's patch budget, a cheaper
transport. That convergence is the reason all four tuples are drawn rather
than the minimum and maximum alone: §4.3 states that min/max-only errors "are
independent of the resolution of the desired raster image, i.e., of the chosen
number of groups", so a min/max chart carries a defect no extra resolution
removes.

## Why the aggregates are cached, and why caching them is cheap

Recomputing the extremes of every visible bucket on every frame costs one pass
over the visible window, so a frame's cost grows with the width of the window
shown rather than with the number of points drawn. Measured 2026-09-04 over
six traces: 4.5 ms at a 15 minute window, 18.5 ms at an hour, 117 ms at four
hours and 350 ms at twelve — past the whole 200 ms frame budget, for a chart
that draws a few hundred points at every one of those widths.

M4's four aggregates form a monoid over adjacent groups. For groups A before
B: `min(A u B) = min(min A, min B)`, likewise the maximum, while the first
tuple is A's and the last is B's. So an aggregate over a wide bucket is built
by merging the two half-width buckets beneath it and never revisits a raw
sample, and a bucket that is full is final and can be kept. The paper reaches
the same conclusion for the streaming case (§7, Online Aggregation and
Streaming): "we can apply the M4 aggregation for online aggregation, i.e.,
derive the four extremum tuples in O(n) and in a single pass over the input
stream."

`M4AggregateCache` therefore holds a dyadic ladder of completed buckets: tier
`t` holds buckets of `FINEST_CACHED_BUCKET_SAMPLES * 2**t` consecutive
samples. Recording one sample costs O(1) amortized, since each tier completes
half as often as the one below it. Reading a window costs one aggregate per
drawn column, each of which is a cached bucket or a merge of O(log n) of them.
The viewport *selects* a tier; it never defines one.

## Stability: why the grid is anchored to the run and not to the window

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
the per-trace budget starts decimating. The client was CPU-saturated by
roughly 18 000 tree mutations per second while the Python process sat at
under half a core, and input stopped being serviced.

Buckets are therefore anchored to *absolute* sample indices — position in the
run, not position in the visible slice. A bucket lying wholly inside the
window holds the same samples on every frame, so its four chosen tuples never
move and the client is told nothing about them. Only the newest, still-filling
bucket changes from one frame to the next.

Holding that anchor as the window grows requires the bucket width to change in
steps rather than continuously, since a width recomputed per frame would move
every boundary again. `_stable_bucket_width` doubles, so the width is constant
across long stretches of a run and the whole selection is rebuilt only on the
handful of frames where it changes. The cost of the ladder is that the column
budget is not always fully spent: between two rungs the selection uses
somewhere from half the budget to all of it. That is a deliberate trade of
resolution the display cannot resolve anyway, in exchange for a redraw the
client can keep up with.

One rebuild per bucket width survives, and it is a floor rather than an
oversight. Once the window is full it slides along a fixed grid, so it spans
alternately `k` and `k+1` boundaries; the count of chosen samples must
therefore change, and any change shifts every later point one position along
a positional list. Removing it would mean either snapping the axis onto bucket
boundaries, which makes a smooth scroll jerk, or decimating from before
`min_x` and trusting the chart to clip points it was never given a reason to
draw. Neither is worth what it buys.
"""

from array import array
from bisect import bisect_left
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from math import isnan
from typing import Final, Self

__all__ = [
    "FINEST_CACHED_BUCKET_SAMPLES",
    "M4Aggregate",
    "M4AggregateCache",
    "first_index_at_or_after",
    "merge_m4_aggregates",
]


#: Samples in one bucket of the cache's finest tier, and so the grain the
#: dyadic ladder starts at.
#:
#: A floor rather than a ladder reaching down to single samples, because tiers
#: below it would cost memory proportional to the run for aggregates no window
#: is ever coarse enough to read. What it costs instead is bounded: a window
#: whose own bucket width falls below this floor is read by scanning its raw
#: values, and such a window holds at most about sixteen samples per column
#: budgeted, so the scan is a constant rather than a function of run length.
#: A bucket boundary inside a wider window costs at most this many raw reads
#: at each end for the same reason.
#:
#: A power of two, because the ladder doubles.
FINEST_CACHED_BUCKET_SAMPLES: Final = 32


def first_index_at_or_after(times_s: Sequence[float], window_start_s: float) -> int:
    """Index of the first sample at or after the start of the visible window.

    Binary search rather than a scan, so locating the window costs the same
    whether the run is a minute or a day old. That matters here: a linear
    step in the per-frame render path would reintroduce the unbounded growth
    that bounding the payload is meant to remove.

    Args:
        times_s: Recorded sample times in seconds, ascending. Simulation time
            advances by a fixed step, so this always holds.
        window_start_s: Start of the visible chart window in seconds.

    Returns:
        Index of the first sample at or after `window_start_s`, or
        `len(times_s)` when every sample precedes it.
    """

    return bisect_left(times_s, window_start_s)


@dataclass(frozen=True, slots=True)
class M4Aggregate:
    """The four M4 extremum tuples of one group of consecutive samples.

    Definition 2 of Jugel et al. 2014, as the four *positions* they were
    recorded at rather than as four values. Carrying the index is a
    correctness requirement and not an optimization: this package guarantees
    that every drawn point is a recorded sample, so a drawn extreme has to
    name the sample it came from and be drawn at that sample's own time. An
    extreme kept as a value alone and replayed at a bucket boundary would be
    a synthesized point, and the guarantee would have to be withdrawn.

    The two extreme *values* are carried alongside their indices so that
    merging two adjacent groups is arithmetic on this object alone, with no
    read back into the recorded run. That is what makes maintaining the
    ladder O(1) amortized per recorded sample.

    Attributes:
        first_index: Position of the group's earliest sample - `min(t)`.
        last_index: Position of the group's latest sample - `max(t)`.
        lowest_index: Position of the group's lowest value - `min(v)`. On
            ties, the earliest position holding it.
        highest_index: Position of the group's highest value - `max(v)`. On
            ties, the earliest position holding it.
        lowest_value: The value at `lowest_index`.
        highest_value: The value at `highest_index`.
    """

    first_index: int
    last_index: int
    lowest_index: int
    highest_index: int
    lowest_value: float
    highest_value: float

    @property
    def indices(self) -> tuple[int, ...]:
        """The group's four tuples as ascending, duplicate-free positions.

        Fewer than four whenever two of them are the same sample, which is
        the ordinary case on a monotone stretch: the lowest value of a rising
        bucket *is* its first sample. Deduplicating here rather than at the
        chart keeps a drawn point from being written twice.
        """

        return tuple(
            sorted({self.first_index, self.lowest_index, self.highest_index, self.last_index})
        )


def merge_m4_aggregates(earlier: M4Aggregate, later: M4Aggregate) -> M4Aggregate:
    """Combine the aggregates of two adjacent groups into one.

    The monoid the cache is built on: for groups A immediately before B,
    `min(A u B) = min(min A, min B)`, likewise the maximum, while the first
    tuple is A's and the last is B's. Nothing is read back out of the
    recorded run, which is what makes a tier of the ladder cost nothing
    beyond the tier below it.

    Ties keep the earlier position, so the answer does not depend on the
    order the ladder happened to be built in.

    Args:
        earlier: Aggregate of the earlier group. Its samples must all
            precede `later`'s; the caller owns that ordering, and the two
            groups must be adjacent for the result to describe a contiguous
            group.
        later: Aggregate of the immediately following group.

    Returns:
        The aggregate of the two groups taken together.
    """

    if later.lowest_value < earlier.lowest_value:
        lowest_index, lowest_value = later.lowest_index, later.lowest_value
    else:
        lowest_index, lowest_value = earlier.lowest_index, earlier.lowest_value

    if later.highest_value > earlier.highest_value:
        highest_index, highest_value = later.highest_index, later.highest_value
    else:
        highest_index, highest_value = earlier.highest_index, earlier.highest_value

    return M4Aggregate(
        first_index=earlier.first_index,
        last_index=later.last_index,
        lowest_index=lowest_index,
        highest_index=highest_index,
        lowest_value=lowest_value,
        highest_value=highest_value,
    )


def _stable_bucket_width(sample_count: int, column_budget: int) -> int:
    """Smallest power-of-two bucket width the visible window fits inside.

    Widths advance by doubling rather than being fitted exactly to
    `sample_count`, because an exactly fitted width would change on every
    frame and move every bucket boundary with it - the instability the
    module docstring describes. A doubling ladder changes width on a
    handful of frames per run instead.

    A window of `sample_count` samples starting at an arbitrary absolute
    index straddles at most one boundary more than its own length implies,
    so the partial bucket at each end is counted here rather than being
    discovered as an overrun of the budget.

    Args:
        sample_count: Number of samples in the visible window.
        column_budget: Greatest number of buckets the window may be drawn
            as. Must be at least 2; a window straddling an anchored boundary
            needs two buckets' worth of budget, so one would leave no width
            that fits and the loop below would not terminate.

    Returns:
        Bucket width in samples: a power of two, at least 1.
    """

    width = 1

    while -(-sample_count // width) + 1 > column_budget:
        width *= 2

    return width


def _merged(earlier: M4Aggregate | None, later: M4Aggregate | None) -> M4Aggregate | None:
    """Merge two aggregates where both exist, treating absence as identity.

    A group can legitimately hold no aggregate at all: a series whose value
    is undefined over some stretch of the run contributes no tuple there,
    and the chart must draw nothing rather than draw a substitute. Absence
    is therefore the monoid's identity element rather than an error.
    """

    if earlier is None:
        return later

    if later is None:
        return earlier

    return merge_m4_aggregates(earlier, later)


class M4AggregateCache:
    """M4 aggregates of one recorded series, on a fixed dyadic grid.

    One instance holds one plotted quantity of one run - the alveolar
    fraction, say - as the values themselves plus a ladder of completed
    buckets over them. Tier `t` holds buckets of
    `FINEST_CACHED_BUCKET_SAMPLES * 2**t` consecutive samples, anchored to
    absolute position in the run, so a bucket that is full is final and is
    never recomputed. The module docstring says why the anchor is the run
    rather than the viewport, and what that costs against Theorem 1.

    **Append-only, and every read is bounded by an explicit stop.** A bucket
    only enters the ladder once every sample in it has been recorded, and a
    query decomposes its range into completed buckets lying wholly inside it
    plus a scan of the raw values at each end. Nothing a query reads can
    therefore change while the run advances, which is what lets a caller
    hold a window over a live run without copying it: the alternative, a
    trace drawn half from one instant and half from the next, is the stale-
    state presentation failure `CLAUDE.md` treats as a safety failure.

    Not a general time-series store: it assumes samples arrive in recording
    order, one per simulation step, and it is indexed by position in the run
    rather than by time. `SimulationController` owns the mapping from
    position to simulated time.
    """

    __slots__ = ("_tiers", "_values")

    def __init__(self) -> None:
        self._values = array("d")
        # Completed buckets only, innermost list per tier. A tier appears
        # once its first bucket has filled, so `len(self._tiers)` is the
        # ladder's current height rather than a configured maximum.
        self._tiers: list[list[M4Aggregate | None]] = []

    @classmethod
    def of(cls, values: Iterable[float | None]) -> Self:
        """Build a cache holding a run that has already been recorded.

        For tests and for a caller replaying a stored run. A live run is
        built by `record` as it advances, which is the path that has to stay
        cheap.

        Args:
            values: The series' recorded values in sample order, with `None`
                where the quantity was undefined at that sample.

        Returns:
            A cache holding exactly those samples.
        """

        cache = cls()

        for value in values:
            if value is None:
                cache.record_undefined()
            else:
                cache.record(value)

        return cache

    def __len__(self) -> int:
        """How many samples have been recorded, defined or not."""

        return len(self._values)

    def record(self, value: float) -> None:
        """Record one sample's value, extending the ladder that summarizes it.

        O(1) amortized: a bucket at tier `t` completes once every
        `FINEST_CACHED_BUCKET_SAMPLES * 2**t` samples, so the total work per
        recorded sample is bounded by the sum of a halving series. No sample
        is ever visited twice - the finest tier reads each once as its bucket
        closes, and every tier above merges the tier below.

        Args:
            value: The quantity's value at this sample.

        Raises:
            ValueError: If `value` is a NaN. A NaN is how this cache marks a
                sample the quantity is undefined at, so accepting one here
                would silently convert a broken model output into a gap in
                the trace - a plausible-looking chart standing for a
                computation that failed.
        """

        if isnan(value):
            raise ValueError("a recorded value must not be a NaN; use record_undefined()")

        self._append(value)

    def record_undefined(self) -> None:
        """Record that the quantity has no value at this sample.

        The position is still consumed, so indices stay aligned with the
        run's other series and with its recorded times. Nothing is drawn
        there: the sample contributes no tuple to any aggregate, and a group
        holding only such samples has no aggregate at all. `app/wash_in.py`
        states the domain that makes this necessary for the ratio trace - a
        quotient outside its domain has no number the interface may show,
        and substituting one is exactly what this project forbids.
        """

        self._append(float("nan"))

    def value(self, index: int) -> float:
        """The recorded value at one position in the run.

        Args:
            index: Absolute position within the run.

        Returns:
            The recorded value, or a NaN where the quantity was undefined
            at that sample. Callers draw only indices a selection returned,
            and a selection never returns an undefined position.
        """

        return self._values[index]

    def aggregate(self, start: int, stop: int) -> M4Aggregate | None:
        """The four M4 tuples of the samples in `[start, stop)`.

        Answered from completed buckets wherever the range covers them, so
        the cost is O(log n) merges plus at most
        `2 * FINEST_CACHED_BUCKET_SAMPLES` raw reads for the unaligned ends -
        a bound that does not grow with the run or with the width of the
        range. A range narrower than one finest-tier bucket is read from the
        raw values alone, which is bounded by the same constant.

        Args:
            start: First position in the range, absolute within the run.
            stop: One past the last position. A range that is empty, or
                that holds no defined sample, has no aggregate.

        Returns:
            The aggregate, or `None` when the range holds no defined sample.
        """

        if start >= stop:
            return None

        grain = FINEST_CACHED_BUCKET_SAMPLES
        aligned_start = -(-start // grain) * grain
        aligned_stop = (stop // grain) * grain

        if aligned_start >= aligned_stop:
            # The range does not span a whole bucket of the finest tier, so
            # there is nothing cached inside it to read.
            return self._scan(start, stop)

        merged = self._scan(start, aligned_start)

        for block in self._cached_blocks(aligned_start // grain, aligned_stop // grain):
            merged = _merged(merged, block)

        return _merged(merged, self._scan(aligned_stop, stop))

    def select_indices(self, start: int, stop: int, column_budget: int) -> list[int]:
        """Select the samples an M4 chart draws for the window `[start, stop)`.

        The window is divided into buckets of a stable power-of-two width -
        anchored to the run, not to the window - and each contributes its
        four M4 tuples. Because both extremes of every bucket survive, the
        drawn trace spans the full range the samples actually covered:
        decimation can flatten the *shape* of a transient but cannot hide
        that it occurred. Because the first and last tuples survive too, the
        window's own first and last samples are always drawn, so the right-
        hand end of a trace is the same sample the numeric readouts show and
        the two can never disagree.

        Args:
            start: First position of the visible window, absolute within the
                run.
            stop: One past the window's last position.
            column_budget: Greatest number of buckets the window may be
                drawn as - the `w` M4 is parameterised by. The number of
                *points* is a consequence of it: at most four per bucket
                before duplicates are removed, and two on the monotone
                stretches that make up most of a run.

        Returns:
            Ascending, duplicate-free absolute positions, every one of them
            a sample with a defined value. Empty when the window is.

        Raises:
            ValueError: If `column_budget` is below 2, or the window is not
                a range within the recorded run.
        """

        if column_budget < 2:
            raise ValueError("column_budget must be at least 2")

        if start < 0 or stop > len(self._values) or start > stop:
            raise ValueError("the window must be a range within the recorded run")

        sample_count = stop - start

        if sample_count == 0:
            return []

        if sample_count <= column_budget:
            # Fewer samples than columns: every one of them is its own
            # bucket, and M4 over a single sample selects that sample.
            return [index for index in range(start, stop) if not isnan(self._values[index])]

        width = _stable_bucket_width(sample_count, column_budget)
        selected: set[int] = set()

        for bucket in range(start // width, (stop - 1) // width + 1):
            # Clamped to the window, so the buckets at each end contribute
            # the tuples of the part that is actually visible.
            aggregate = self.aggregate(max(bucket * width, start), min((bucket + 1) * width, stop))

            if aggregate is not None:
                selected.update(aggregate.indices)

        return sorted(selected)

    def _append(self, value: float) -> None:
        """Store one sample and close any bucket it completes."""

        self._values.append(value)
        grain = FINEST_CACHED_BUCKET_SAMPLES
        recorded = len(self._values)

        if recorded % grain:
            return

        self._promote(0, self._scan(recorded - grain, recorded))

    def _promote(self, tier: int, aggregate: M4Aggregate | None) -> None:
        """File a completed bucket, and every wider bucket it completes.

        A tier's buckets pair up into the tier above, so filing an
        odd-numbered bucket completes nothing and filing an even-numbered
        one completes exactly one bucket a tier up. The loop therefore
        climbs only as far as the trailing zeros of the run length carry it,
        which is what makes recording a sample O(1) amortized.
        """

        while True:
            if tier == len(self._tiers):
                self._tiers.append([])

            completed = self._tiers[tier]
            completed.append(aggregate)

            if len(completed) % 2:
                return

            aggregate = _merged(completed[-2], completed[-1])
            tier += 1

    def _cached_blocks(self, first: int, stop: int) -> list[M4Aggregate | None]:
        """The widest completed buckets that tile `[first, stop)` exactly.

        Both bounds are counted in finest-tier buckets rather than in
        samples. Greedy from the left: at each step take the widest tier
        whose bucket both starts here and ends within the range, which is
        the ordinary dyadic decomposition and yields O(log n) blocks.

        Every block it names is complete, because the range is measured in
        buckets that have themselves completed.
        """

        blocks: list[M4Aggregate | None] = []
        position = first

        while position < stop:
            tier = 0

            while (
                tier + 1 < len(self._tiers)
                and position % (2 << tier) == 0
                and position + (2 << tier) <= stop
            ):
                tier += 1

            blocks.append(self._tiers[tier][position >> tier])
            position += 1 << tier

        return blocks

    def _scan(self, start: int, stop: int) -> M4Aggregate | None:
        """Aggregate `[start, stop)` from the raw values, reading each once.

        The one place a recorded value is visited, and it visits each at
        most once: the two running extremes are carried as values as well as
        as positions, so a comparison costs no read of its own. Reading them
        back out of the array on every step made the equivalent scan about
        2.8 reads per sample where one is enough (`PL-MJ7B`).
        """

        values = self._values
        first_index = -1

        for index in range(start, stop):
            if not isnan(values[index]):
                first_index = index
                break

        if first_index < 0:
            return None

        last_index = lowest_index = highest_index = first_index
        lowest_value = highest_value = values[first_index]

        for index in range(first_index + 1, stop):
            value = values[index]

            if isnan(value):
                continue

            last_index = index

            if value < lowest_value:
                lowest_index = index
                lowest_value = value
            elif value > highest_value:
                highest_index = index
                highest_value = value

        return M4Aggregate(
            first_index=first_index,
            last_index=last_index,
            lowest_index=lowest_index,
            highest_index=highest_index,
            lowest_value=lowest_value,
            highest_value=highest_value,
        )
