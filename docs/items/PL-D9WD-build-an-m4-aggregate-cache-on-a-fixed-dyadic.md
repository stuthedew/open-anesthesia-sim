---
id: PL-D9WD
title: Build an M4 aggregate cache on a fixed dyadic grid
priority: P2
effort: M
status: done
classes: perf
feature: teachable-case
milestone: v0.3.9
touches: src/anesthesia_sim/app/chart_downsampling.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_chart_downsampling.py, tests/unit/test_run_history.py, tests/unit/test_simulation_view.py, tests/integration/test_chart_patching.py, docs/MODEL.md
added: 2026-09-04
closed: 2026-09-04
pr: 311
verify: uv run pytest tests/unit/test_chart_downsampling.py && grep -q 'def test_aggregates_merge_without_revisiting_samples' tests/unit/test_chart_downsampling.py
---

**Problem.** Decimation rescans every sample in the visible window on every
frame, so per-frame cost is O(window) rather than O(points drawn). Measured
2026-09-04: 8.9 ms at a 15 min window, 15.9 ms at 1 h, 62.6 ms at 4 h, and
207.7 ms at 12 h — more than the whole 200 ms frame budget. `PL-SSBP`'s
settled scale list runs to 12 hours, and `PL-Z7LY` lets the user pan back
across the whole record at any of them, so the rescan has to go.

**Why it matters.** It is what makes the settled scale list reachable at all:
without it the 12 h scale stalls the interface outright, and `PL-Z7LY`'s pan
across the whole record multiplies that by every position the user can scroll
to. It is also the structure that bounds memory once the allowed simulation
duration is extended (`PL-011`), so one mechanism answers the read cost, the
scale range and the retention policy together rather than three designs
meeting later and disagreeing.

It carries a correctness weight beyond speed. What a chart draws when it
cannot draw every sample is a presentation-correctness claim, and this item
decides it for every scale at once: whether a transient can vanish, whether a
drawn point is a recorded sample, and whether zooming out shows the same run
or a smoothed impression of it. Deciding that once, against a published
guarantee and with the departures written down, is worth more than settling
it per scale as each is added.

**Approach, agreed with the project owner 2026-09-04.** Precompute the M4
aggregates once per bucket and keep them, on a grid **anchored to absolute
sample index** — tier *t* holds buckets of 2^t samples. The viewport
*selects* a tier; it never defines one.

That anchoring is the whole point and is not a detail. M4 as published groups
by the viewport (`w` equidistant spans, one per pixel column), so a cache
built that way would rederive everything whenever the viewport moved, which
is `PL-Q197`'s defect one level up. `PL-Q197` already moved
`select_envelope_indices` onto an absolute anchor, which is what makes a
completed bucket's aggregates final and therefore cacheable at all.

**Why maintaining it is cheap.** M4's four aggregates form a monoid over
adjacent groups: `min(A∪B) = min(minA, minB)`, likewise `max`, while `first`
is `first(A)` and `last` is `last(B)` when A precedes B. So tier *t+1* is
built by merging pairs of tier-*t* buckets and never revisits a raw sample.
O(1) amortized per simulation step, and every tier above the finest is
effectively free. The paper reaches the same conclusion for the streaming
case: "we can apply the M4 aggregation for online aggregation, i.e., derive
the four extremum tuples in O(n) and in a single pass over the input stream"
(§7, Online Aggregation and Streaming).

**What M4 actually guarantees, from the source.** Jugel, Jerzak,
Hackenbroich and Markl, "M4: A Visualization-Oriented Time Series Data
Aggregation", *PVLDB* 7(10):797-808, 2014 — read in full 2026-09-04, so the
following is from the paper rather than from a summary of it.

- **Definition 2**: a width-based M4 aggregation selects, per group, the
  tuples at `min(v)`, `max(v)`, `min(t)` and `max(t)` — the minimum, the
  maximum, the first and the last.
- **Theorem 1**: `vis_wh(G_M4(T)) = vis_wh(T)`. Any two-colour line
  visualization of a series equals that of a reduced series containing at
  least the four extrema of every group. It rests on two stated lemmas — a
  rasterized line has no gaps, and an inner-column line sets no foreground
  pixel outside its column.
- **Exactness is conditional on the grouping.** §6: "at nh = w, i.e., at any
  factor k of w, M4 provides perfect (error-free) visualizations. Any
  grouping with nh = k·w and k ∈ N+ also includes the min, max, first, and
  last tuples for nh = w." So the guarantee holds when the number of buckets
  drawn is an **integer multiple** of the chart's pixel-column count — not
  merely when it is finer.

**Consequence for the dyadic grid, stated plainly rather than glossed.** A
grid anchored to absolute sample index cannot also guarantee an integer
multiple of an arbitrary chart width, and a grid that adapted to chart width
would move on every resize — reintroducing exactly what `PL-Q197` removed.
This design therefore buys **stability at the cost of Theorem 1's exactness
guarantee**, landing in the paper's general case (DSSIM > 0.9) rather than
its perfect one. That is the right trade here and it should be recorded as a
trade, not claimed as exactness.

**How much the missing guarantee actually costs us — less than the paper
implies.** §4.3 names three error classes for min/max-only aggregation: E1, a
missing line where a pixel column holds no selected tuple; E2, a false line
bridging an empty column; E3, an undesired pixel from a false inter-column
line between consecutive extrema. E1 and E2 are driven by "time series that
have a very heterogeneous time distribution, i.e., notable gaps". This
simulation records one sample every `SIMULATION_STEP_S` exactly, with no gaps
ever, so **E1 and E2 are structurally impossible here**; only E3 remains.
That does not make first and last worthless — it means the gap between
min/max and full M4 is narrower for this data than for the paper's industrial
series.

**What drawing all four costs, stated plainly.** `PL-Q197` established that
the client is patched at about two operations per drawn point that moves, so
drawn points are the scarce resource here and bytes are not. M4 spends up to
four tuples per group where min/max spends two — §6 measures exactly that,
finding min/max has "on average ... higher data efficiency than all
aggregation based techniques, including M4". At a fixed traffic budget,
choosing M4 therefore **halves the number of columns**.

The arithmetic, using PL-Q197's measured cost: a rebuild is about
`2 x points x traces` operations, so `48 x buckets` for M4 across six traces
against `24 x buckets` for min/max. The ~2 200-operation rebuild measured
today buys roughly 46 M4 columns, or 92 min/max ones.

**Forty-six columns is too coarse, and the way out is fewer traces rather
than fewer aggregates.** Cost is linear in traces drawn, so `PL-CG7J`
(per-trace show/hide, which Gas Man has) is what returns the resolution: two
traces instead of six buys ~138 columns at the same traffic. That promotes
`PL-CG7J` from a nice feature to part of how this chart affords resolution at
all, and the two should be sequenced together rather than independently.

**A budget in columns, not points.** `MAX_CHART_POINTS_PER_SERIES` is
currently a per-trace *point* ceiling, which was the right parameter for
min/max and is the wrong one for M4: the algorithm is parameterised by `w`,
the number of groups, and its point count is a consequence of up to four
tuples per group after deduplication. The constant should be renamed and
re-expressed as a column budget when this lands, so the code reads in the
paper's own terms rather than in the ones the superseded algorithm used.

**Decided by the project owner, 2026-09-04: implement actual M4 — cache all
four and draw all four.** This reverses a weaker recommendation made earlier
the same day (draw min and max, keep first and last cached against a later
need), and the reversal is right for a reason the paper states outright.

§4.3, on the errors min/max-only aggregation produces: *"Note that these
errors are independent of the resolution of the desired raster image, i.e.,
of the chosen number of groups."* Min/max is not M4 with fewer points. It is
a different algorithm carrying a defect that **no amount of extra resolution
removes**, so the earlier recommendation traded a permanent error class for a
point count — a trade that only ever looks favourable while the error is
unobserved.

Two further reasons the drawn set should be the real one:

- **Provenance.** This project's whole discipline is that a displayed value
  is traceable to what produced it. "The chart implements M4 (Jugel et al.
  2014)" is auditable against a paper held in `docs/references/`. "Something
  M4-like, with min/max only" is auditable against nothing, and the
  difference is invisible in the rendered output — which is exactly the kind
  of claim that decays into a wrong one over a few years.
- **It converges and min/max does not.** Every later improvement — a larger
  budget, fewer traces drawn (`PL-CG7J`), a cheaper transport (`PL-YDKJ`) —
  moves an M4 chart toward Theorem 1's exactness. None of them moves a
  min/max chart anywhere, per the quotation above.

**Carrying the sample index is a correctness requirement, not an
optimization.** `chart_downsampling.py` guarantees a drawn point is always a
recorded sample and never a synthesized one. An extreme stored as a value and
replayed at a bucket boundary would be synthesized, and that guarantee would
have to be withdrawn — which would change what every drawn point claims.

**Note the current code is MinMax, not M4.** `select_envelope_indices`
selects min and max per bucket plus the window's global first and last, so it
is the paper's MinMax with endpoint handling, and E3 applies to it today.
Under the decision above it is replaced rather than extended: per bucket, the
tuples at first, last, argmin and argmax, deduplicated and in ascending time
order. `PL-Q197`'s stability guards move with it — they assert a property of
the selection, not of min/max specifically — but the two tests pinning drawn
counts will need their bounds re-derived from a column budget.

**Where.**

1. `chart_downsampling.py` — the aggregate type, the merge, and tier
   selection for a requested window and point budget.
2. `controller.py` — maintaining the tiers as `advance()` records samples.
3. `chart_series.py` — reading a tier slice rather than rescanning raw
   samples.

**Blocks.** `PL-SSBP`'s scales past about an hour, `PL-Z7LY`'s pan across the
whole record, and `PL-011`'s retention policy, since raw samples can only be
evicted once a tier fine enough to serve the narrowest scale has consolidated
them.

**Depends on** `PL-0VM7`, which introduces the windowed read interface this
plugs into.

**Done when.** Per-frame render cost is independent of the width of the
visible window, a 12 h scale costs what a 15 min scale costs, the aggregates
are maintained incrementally rather than rescanned, every drawn point is
still a recorded sample with its own timestamp, and the departure from
Theorem 1's exactness condition is written down where a reader of the chart
code will find it.


**What landed, 2026-09-04.**

The ladder is `chart_downsampling.M4AggregateCache`: tier *t* holds buckets
of `FINEST_CACHED_BUCKET_SAMPLES * 2**t` samples, anchored to absolute
index, and only completed buckets enter it. A window is read as the
completed buckets tiling it plus a raw scan of the unaligned remainder at
each of its two ends, so the read is bounded by a constant of the grain and
contains neither the run length nor the window width.
`test_reading_a_window_costs_the_same_however_wide_it_is` asserts that as a
count of values read rather than as a duration.

**Three passes over the window made up the cost, not one.** The rescan was
81% of it; the other 19% would have kept the frame proportional to the width
shown whatever the cache did. So `RunHistory` replaces the controller's
`list[SimulationHistorySample]`, storing the run by quantity with one cache
each: the window stopped copying its samples out, each trace stopped
building a list of one field per sample, and the wash-in plot stopped
reclassifying every visible sample against its domain - the stretches of
that domain are now maintained as samples arrive.
`test_a_frame_never_materializes_the_window_as_rows` is what stops a row
walk being reintroduced, which is the likeliest regression here because rows
are the obvious shape to reach for.

Whole chart frame, six traces plus the wash-in plot, on this container:

| Window | Before | After |
| ---: | ---: | ---: |
| 5 min | 1.9 ms | 1.7 ms |
| 15 min | 5.6 ms | 2.8 ms |
| 1 h | 23.8 ms | 3.0 ms |
| 4 h | 138.9 ms | 3.4 ms |
| 12 h | 431.1 ms | 2.6 ms |

Recording costs 4.6 us per sample across all seven caches, which at the
0.1 s step is 46 us of CPU per second of simulated time.

**Memory fell rather than rose**, which the retention argument above did not
predict: 264 B per sample as a list of frozen dataclasses against 127 B as
seven caches with their ladders, measured over 200 000 samples. Columns of
doubles cost less than rows of objects by more than the ladder costs.

**The column arithmetic above over-predicted what M4 costs, and `PL-CG7J` is
not a prerequisite after all.** The brief reasoned that four tuples per
group against two would halve the columns affordable at a fixed traffic
budget, which would have made per-trace show/hide part of how the chart
affords resolution. Measured on the recording connection at a 150-column
budget, a steady frame sends 24 patch operations - the same 24 the min/max
envelope sent - and a compartment trace draws 182 points where the
300-point envelope drew about 190. The reason is in the algorithm rather
than in the measurement: M4's four tuples collapse to two on a monotone
stretch, since a rising bucket's lowest value *is* its first sample, and
these traces are monotone almost everywhere. `PL-CG7J` remains worth having
for its own sake and is no longer sequenced against this.
