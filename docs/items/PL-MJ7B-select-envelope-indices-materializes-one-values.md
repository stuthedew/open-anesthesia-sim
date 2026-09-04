---
id: PL-MJ7B
title: select_envelope_indices materializes one values list per trace per frame, and removing it is a constant-factor win the item that asked for it read as an asymptotic one
priority: P3
effort: S
status: done
classes: perf
touches: src/anesthesia_sim/app/chart_downsampling.py, tests/unit/test_chart_downsampling.py
added: 2026-09-04
closed: 2026-09-04
pr: 309
verify: uv run pytest tests/unit/test_chart_downsampling.py && grep -q 'def test_the_envelope_scan_reads_each_sample_once' tests/unit/test_chart_downsampling.py
---

**Problem.** `chart_series.redraw_series` builds `values = [value_for(sample)
for sample in visible]` once per trace per frame — six lists the length of
the visible window, five times a second, allocated only to be read by
`chart_downsampling.select_envelope_indices` and discarded. `PL-0VM7`'s
Approach asked for this to go, on the grounds that the cost is "unbounded if
a future window is a week wide". That reasoning does not hold, which is why
the change was not made with the rest of the item.

**Why it matters.** Two separate things, and only the first is real.

Measured 2026-09-04 against the saturated 3 001-sample window
(`MAX_CHART_WINDOW_S / SIMULATION_STEP_S`), per frame across all six traces:

| | Per trace | Six traces |
| --- | ---: | ---: |
| Before: `values` list, extremes re-read from it | 0.192 ms | 1.14 ms |
| `values` list, bucket extremes cached in locals | 0.170 ms | — |
| No `values` list, bucket extremes cached in locals | 0.137 ms | 0.85 ms |

So the whole change is worth about 0.29 ms a frame, 0.14% of the 200 ms
frame at `RENDER_INTERVAL_S`. Real, and free of any correctness cost — the
three selections agree index for index.

What it is *not* is the fix its stated motivation asks for. Min/max envelope
decimation has to read every sample of every bucket to find that bucket's
extremes, so the scan is O(window) whether a list is materialized or not.
Removing the list changes the constant, never the exponent. A week-wide
window is 6 048 000 samples scanned six times a frame at 5 Hz: infeasible
under either version by three orders of magnitude. What that case needs is
bucket extremes maintained incrementally as samples are appended — O(1) per
recorded sample, O(buckets) per frame — which is the tiered store `PL-011`
carries, and which `SimulationController.history_window()` (added by
`PL-0VM7`) is already the interface for.

**Where.**

1. `src/anesthesia_sim/app/chart_downsampling.py` — the bucket loop re-read
   `values[lowest]` and `values[highest]` on every comparison.
2. `src/anesthesia_sim/app/chart_series.py` — `redraw_series` builds the
   list, and uses it again to write each drawn point's `y`.

**Decision (project owner, 2026-09-04): take the split.** Cache the bucket
extremes; keep the `values` list.

Caching is internal to `select_envelope_indices`: no signature changes, no
test call site changes, and it was most of the win. Removing the list would
have meant making the function generic over a sample sequence and an
accessor — the shape `first_index_at_or_after` in the same module already
has — and rewriting its eighteen test call sites, for the remaining 0.14% of
a frame. `chart_downsampling.py` is `src/`, held to the specialist standard,
and a pure function over a value sequence is the simpler of the two
signatures; that is not a trade worth making for a display that cannot
resolve the difference.

**Closed 2026-09-04.** The bucket loop carries its two running extremes as
values as well as as indices, so a comparison costs no read of its own. The
scan now reads each sample exactly once where it read about 2.8 — measured
5 625 reads over a 2 000-sample window before, 2 000 after — and the frame's
decimation across six traces went from 1.14 ms to 1.04 ms.

The read count rather than the duration is what
`test_the_envelope_scan_reads_each_sample_once` asserts, through a
`Sequence[float]` that counts its own `__getitem__` calls: a timing
assertion is flaky on shared hardware, while the count is exact and is the
quantity the cost is proportional to. It is an equality rather than a bound
— a loop that reads a sample twice is one carrying its extremes somewhere
other than in a local, and no version of this scan needs to. The same test
holds the selection identical to the one the old loop returned, because a
read count says nothing about which samples were chosen.

The `values` list stays, and the week-wide window remains `PL-011`'s.
