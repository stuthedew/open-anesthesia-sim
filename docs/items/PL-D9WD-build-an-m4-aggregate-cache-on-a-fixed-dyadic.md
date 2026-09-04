---
id: PL-D9WD
title: Build an M4 aggregate cache on a fixed dyadic grid
status: ready
priority: P2
effort: M
classes: perf
feature: teachable-case
verify: uv run pytest tests/unit/test_chart_downsampling.py && grep -q 'def test_aggregates_merge_without_revisiting_samples' tests/unit/test_chart_downsampling.py
touches: src/anesthesia_sim/app/chart_downsampling.py, src/anesthesia_sim/app/chart_series.py, src/anesthesia_sim/app/controller.py
added: 2026-09-04
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

**So separate what is stored from what is drawn.** Store all four aggregates
per bucket, each with the sample index it came from: storage is not the
binding constraint (~80 MB for a simulated week against 1.60 GB of raw
samples), and storing them keeps every later option open. *Drawing* all four
doubles the point count, and `PL-Q197` established that the client is patched
at about two operations per drawn point that moves, so drawn points are the
scarce resource and not bytes. The draw-time subset is therefore a separate
decision from the cache's contents, and the paper supports taking it
seriously: §6 finds min/max "on average ... higher data efficiency than all
aggregation based techniques, including M4", precisely because M4 spends four
tuples per group where min/max spends two.

**Decided by the project owner, 2026-09-04: cache all four, draw min and max
to start.** The two drawn per bucket stay what `select_envelope_indices`
already selects, so nothing about the rendered chart changes when the cache
lands — this item is a performance change, not a visual one. Moving to all
four later is a draw-time switch with no migration, because the aggregates
are already stored. Revisit it if E3 is ever actually observed on a trace.

**Carrying the sample index is a correctness requirement, not an
optimization.** `chart_downsampling.py` guarantees a drawn point is always a
recorded sample and never a synthesized one. An extreme stored as a value and
replayed at a bucket boundary would be synthesized, and that guarantee would
have to be withdrawn — which would change what every drawn point claims.

**Note the current code is MinMax, not M4.** `select_envelope_indices`
selects min and max per bucket plus the window's global first and last, so it
is the paper's MinMax with endpoint handling, and E3 applies to it today.

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
