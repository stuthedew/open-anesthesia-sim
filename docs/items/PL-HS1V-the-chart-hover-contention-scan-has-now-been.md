---
id: PL-HS1V
title: The chart-hover contention scan has now been rebuilt from scratch three times - PL-MN4J, PL-JVHL and PL-0RZ0 - and PL-QYBW's axis decision will want it a fourth
priority: P2
effort: M
status: ready
classes: infra, test
feature: compartment-trace-legibility
touches: tests, tools
added: 2026-09-20
payoff: the next hover design round scores its answer against a scan that already exists, instead of a fourth session rebuilding the same 324,000-position replica from scratch
verify: grep -rq 'hover_contention' tests tools
recurrences: 2026-09-22 PL-1N5B
---

**Problem.** The chart-hover contention scan has now been rebuilt from scratch three times - PL-MN4J, PL-JVHL and PL-0RZ0 - and PL-QYBW's axis decision will want it a fourth

Three sessions have now written the same scan into a scratch file and thrown it
away: `PL-MN4J` (whether the box names the run), `PL-JVHL` (the run flip, whose
own table of five targeting rules is the largest of the three) and `PL-0RZ0`
(the compartment flip, 2026-09-20). Each rebuilt the same four things - the
branched sevoflurane case with a keyframe at the fork, the pixel mapping from
`start_s`/`axis_top_percent` and `theme.CHART_HEIGHT`, a replica of
`nearest_trace_point`'s selection fast enough to walk 324,000 pointer
positions, and a check that the replica agrees with the real function.

`PL-QYBW` (the shared percent axis compressing the slow compartments) is a
`needs-decision` design round whose whole question is what the compression
costs a reader, so it wants the same scan a fourth time, and any targeting
change made under `PL-0RZ0` wants it again to score the result.

**What would make it worth building, and what would not.** The decidable half
is the scan: given a frame, a plot size and a radius, which traces are in
reach at each pixel, which is aimed at, and what a 2 px move changes. That
answers identically every run and is exactly what `CLAUDE.md`'s
deterministic-tooling section says to move out of the model. The judgment half
- which cases to score, which metric answers the question, what the number
means - stays in the session and must not be scripted.

Two constraints a design has to meet. `tools/` is standard library only, so the
numpy replica three sessions have used cannot go there as written: either a
slower pure-stdlib scan scoped to the cases that matter, or it lives under
`tests/` where the project virtualenv is available. And it measures the
simulator, so whichever bar applies is worth settling before it is built rather
than after.

**Why it matters.** Three sessions have each paid the same setup cost and left
nothing behind, and a fourth is already scheduled: `PL-QYBW`'s axis decision
wants the same scan, and any targeting change made under `PL-1K9G` wants it
again to score the result. That is `CLAUDE.md`'s deterministic-tooling test met
squarely - the work recurs, the answer is deterministic, and it is being
re-derived at full context every time. The judgment half stays in the session
and must not be scripted: which cases to score, which metric answers the
question, and what the number means are the design work.

**Reproduced 2026-09-20.** Nothing under `tools/` or `tests/` names the scan:
`grep -rq 'hover_contention' tests tools` finds nothing, and the only reader of
`nearest_trace_point` outside `src/` is `tests/unit/test_chart_frame.py`, which
tests the function rather than scanning a frame with it.

**Done when.** A scan a session can run - given a frame, a plot size and a
radius, which traces are in reach at each pixel, which is aimed at, and what a
2 px move changes - lives under `tests/` or `tools/` rather than in a scratch
file, with the standard-library constraint on `tools/` settled rather than
assumed, and a test holding its agreement with `nearest_trace_point` itself.


## Rebuilt a fourth time, 2026-09-22, by `PL-1K9G` - kept here this time

`PL-1K9G` (which instant a hover labels a value with) needed the same scan to
decide whether a trace's column should be chosen by time alone, and rebuilt it
from scratch exactly as this brief predicted. Rather than lose it with the
container again, both scripts are below as they ran, with `PL-1K9G`'s numbers
reproducible from them. What they add over the first three, and what a tool
built from them would still owe:

- **Both rules side by side** - the retired two-dimensional nearest point and
  the shipped time rule - with every metric computed for both, so a change is
  scored before and after in one run. A tool would take the rules as
  parameters rather than as two hard-coded branches.
- **Four sub-pixel phases per pixel column** (`PHASES`, overridable from the
  environment), because while the window is pinned at zero the grid columns sit
  exactly on pixel boundaries, and a whole-pixel walk samples that one
  alignment only.
- **The cross-check against the shipped function** at random pointer
  positions; `--check-new` selects which rule is held against it. This is the
  half of the done-when above that is already written.
- **Two long-axis cases** (a two-hour run on its 2-hour and on the 12-hour
  axis) beside `PL-0RZ0`'s branched geometry, because steep segments are where
  targeting rules diverge most.
- **numpy**, so neither is `tools/` material as written, and this brief's
  standard-library question stays open. Both read `chart_frame._hover_value`,
  a private name a tool should not reach for.

Run from the repository root with `uv run python`; `scan_wash_in.py` imports
`scan_1k9g.py` from beside it.

`scan_1k9g.py`:

```python
"""PL-1K9G: which drawn column a trace answers a hover at, under two rules.

Shipped (2-D): each (run, compartment) answers at its drawn point nearest the
pointer in pixel distance, if that is inside the radius.

Candidate (time): each run answers at its drawn column nearest the pointer in
time, ties to the earlier; each compartment answers there if that point is
inside the radius.

Run with `uv run python scan_1k9g.py [--check-new]`.
"""

from __future__ import annotations

import random
import sys
from bisect import bisect_left, bisect_right
from dataclasses import dataclass

import numpy as np

from anesthesia_sim.app import chart_frame as cf
from anesthesia_sim.app.chart_frame import RunInput, assemble_chart_frame, nearest_trace_point
from anesthesia_sim.app.chart_time_base import time_base_for_span
from anesthesia_sim.app.control_timeline import AdjustmentGrouping
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.dashboard_frame import run_label
from anesthesia_sim.app.run_series import COMPARTMENT_QUANTITIES
from anesthesia_sim.app.run_series import RecordedQuantity as Q
from anesthesia_sim.core.concentration import Fraction

STEP_S = 0.1
WIDTH_PX = 900
HEIGHT_PX = 360
RADIUS = 12.0
# Four sub-pixel phases per pixel column, so nothing below is an artefact of
# where the anchored grid happens to fall against the pixel grid.
import os

PHASES = tuple(float(p) for p in os.environ.get("PHASES", "0.125,0.375,0.625,0.875").split(","))


def advance(controller: SimulationController, seconds: float) -> None:
    for _ in range(round(seconds / STEP_S)):
        controller.advance(STEP_S)


def dial(controller: SimulationController, delivered: float) -> None:
    controller.begin_control_adjustment()
    controller.set_delivered_partial_pressure_fraction(Fraction(delivered))


def frame_of(controllers, shown, span_s):
    grouping = AdjustmentGrouping()
    runs = []

    for controller in controllers:
        snapshot = controller.snapshot()
        runs.append(
            RunInput(
                run_label(len(runs)), controller, snapshot, grouping.of(snapshot.control_timeline)
            )
        )

    return assemble_chart_frame(runs, time_base_for_span(span_s), shown, plot_width_px=WIDTH_PX)


def build_cases():
    """PL-0RZ0's geometry, plus two long-axis cases where traces are steep."""

    trunk = SimulationController(agent_id="sevoflurane")
    trunk.start()
    advance(trunk, 600.0)
    dial(trunk, trunk.snapshot().delivered_partial_pressure_fraction * 1.5)
    advance(trunk, 600.0)
    case = BranchedCase(trunk)
    branches = {}

    for name, delivered in (("2 MAC", 0.04), ("1.25 MAC", 0.025), ("vaporizer off", 0.0)):
        branch = case.fork_at(600.0)
        branch.start()
        dial(branch, delivered)
        advance(branch, 600.0)
        branches[name] = branch

    cases = [
        ("one run, 60 min axis", "all six", frame_of((trunk,), COMPARTMENT_QUANTITIES, 3600.0))
    ]
    pairs = (
        ("muscle + fat", (Q.MUSCLE, Q.FAT)),
        ("mixed venous + vessel rich", (Q.MIXED_VENOUS, Q.VESSEL_RICH)),
        ("alveolar + fat", (Q.ALVEOLAR, Q.FAT)),
    )

    for name, branch in branches.items():
        for pair_name, pair in pairs:
            cases.append(
                (
                    f"two runs, branch {name}, 60 min axis",
                    pair_name,
                    frame_of((trunk, branch), pair, 3600.0),
                )
            )

    # Long axes, where a dial change is a near-vertical step: a two-hour case
    # (1 MAC, x1.5 at 10 min, vaporizer off at 60 min) on its fitted 2 h axis
    # and on the 12 h one.
    long_run = SimulationController(agent_id="sevoflurane")
    long_run.start()
    advance(long_run, 600.0)
    dial(long_run, long_run.snapshot().delivered_partial_pressure_fraction * 1.5)
    advance(long_run, 3000.0)
    dial(long_run, 0.0)
    advance(long_run, 3600.0)
    cases.append(
        (
            "one run, 2 h case, 2 h axis",
            "all six",
            frame_of((long_run,), COMPARTMENT_QUANTITIES, 7200.0),
        )
    )
    cases.append(
        (
            "one run, 2 h case, 12 h axis",
            "all six",
            frame_of((long_run,), COMPARTMENT_QUANTITIES, 43200.0),
        )
    )

    return cases


@dataclass
class Trace:
    run: int
    quantity: Q
    times: np.ndarray
    percents: np.ndarray
    codes: np.ndarray  # one integer per distinct printed value string
    strings: list[str]


def traces_of(frame) -> list[Trace]:
    traces = []
    table: dict[str, int] = {}

    for run_index, run in enumerate(frame.runs):
        for quantity in frame.visible:
            strings = [cf._hover_value(run, quantity, k) for k in range(len(run.times_s))]
            codes = np.array([table.setdefault(s, len(table)) for s in strings])
            traces.append(
                Trace(
                    run_index,
                    quantity,
                    np.array(run.times_s),
                    np.array(run.percents(quantity)),
                    codes,
                    strings,
                )
            )

    return traces


def time_nearest(times: np.ndarray, t: float) -> int:
    """The drawn column nearest `t` in time, ties to the earlier."""

    i = bisect_left(times, t)

    if i == 0:
        return 0

    if i == len(times):
        return len(times) - 1

    return i - 1 if t - times[i - 1] <= times[i] - t else i


def scan(frame):
    s_per_px = (frame.stop_s - frame.start_s) / WIDTH_PX
    p_per_px = frame.axis_top_percent / HEIGHT_PX
    reach_s = RADIUS * s_per_px
    traces = traces_of(frame)
    last_px = max(float(t.times[-1]) for t in traces) / s_per_px + RADIUS + 1
    xs = np.array(
        [
            frame.start_s + (px + phase) * s_per_px
            for px in range(int(last_px) + 1)
            for phase in PHASES
        ]
    )
    ys = (np.arange(HEIGHT_PX) + 0.5) * p_per_px
    n_x, n_y = len(xs), len(ys)
    old_ans = {}
    old_col = {}
    new_ans = {}
    new_col = {}

    for trace in traces:
        oa = np.zeros((n_x, n_y), dtype=bool)
        oc = np.full((n_x, n_y), -1, dtype=np.int64)
        na = np.zeros((n_x, n_y), dtype=bool)
        nc = np.full((n_x, n_y), -1, dtype=np.int64)
        times, percents = trace.times, trace.percents

        for i, t in enumerate(xs):
            lo = bisect_left(times, t - reach_s)
            hi = bisect_right(times, t + reach_s)

            if lo < hi:
                dx = (t - times[lo:hi]) / s_per_px
                dy = (ys[:, None] - percents[None, lo:hi]) / p_per_px
                distance = np.sqrt(dx[None, :] ** 2 + dy**2)
                k = np.argmin(distance, axis=1)
                nearest = distance[np.arange(n_y), k]
                inside = nearest <= RADIUS
                oa[i] = inside
                oc[i] = np.where(inside, lo + k, -1)

            c = time_nearest(times, t)
            d = np.sqrt(((t - times[c]) / s_per_px) ** 2 + ((ys - percents[c]) / p_per_px) ** 2)
            inside = d <= RADIUS
            na[i] = inside
            nc[i] = np.where(inside, c, -1)

        key = (trace.run, trace.quantity)
        old_ans[key], old_col[key], new_ans[key], new_col[key] = oa, oc, na, nc

    return traces, xs, ys, s_per_px, p_per_px, old_ans, old_col, new_ans, new_col


def pct(numerator, denominator):
    return float("nan") if denominator == 0 else 100.0 * numerator / denominator


def report(label, pair, frame, results):
    traces, xs, ys, s_per_px, p_per_px, old_ans, old_col, new_ans, new_col = results
    by_key = {(t.run, t.quantity): t for t in traces}
    keys = list(by_key)
    row = {"case": label, "compartments": pair, "s/px": s_per_px}

    # M1: adjacent drawn columns printing different values, over the whole trace.
    adjacent = sum(len(t.codes) - 1 for t in traces)
    differing = sum(int(np.count_nonzero(t.codes[1:] != t.codes[:-1])) for t in traces)
    row["adjacent pairs"] = adjacent
    row["adjacent differ %"] = pct(differing, adjacent)
    row["adjacent differ by trace"] = {
        f"{t.quantity.value}/r{t.run}": round(
            pct(int(np.count_nonzero(t.codes[1:] != t.codes[:-1])), len(t.codes) - 1), 1
        )
        for t in traces
    }

    hoverable = np.zeros_like(next(iter(old_ans.values())))
    for key in keys:
        hoverable |= old_ans[key]
    row["hoverable positions"] = int(hoverable.sum())

    # M2: two readings of one run at different instants in one box (old rule).
    mixed = np.zeros_like(hoverable)
    visible = np.zeros_like(hoverable)
    runs = sorted({t.run for t in traces})
    for run in runs:
        run_keys = [k for k in keys if k[0] == run]
        for a in range(len(run_keys)):
            for b in range(a + 1, len(run_keys)):
                ka, kb = run_keys[a], run_keys[b]
                both = old_ans[ka] & old_ans[kb]
                ca, cb = old_col[ka], old_col[kb]
                differ = both & (ca != cb)
                mixed |= differ
                ta, tb = by_key[ka], by_key[kb]
                safe_a = np.where(differ, ca, 0)
                safe_b = np.where(differ, cb, 0)
                shows = differ & (
                    (ta.codes[safe_a] != ta.codes[safe_b]) | (tb.codes[safe_b] != tb.codes[safe_a])
                )
                visible |= shows
    multi_same_run = np.zeros_like(hoverable)
    for run in runs:
        run_keys = [k for k in keys if k[0] == run]
        count = sum(old_ans[k].astype(np.int64) for k in run_keys)
        multi_same_run |= count >= 2
    row["2+ readings of one run %"] = pct(int(multi_same_run.sum()), int(hoverable.sum()))
    row["of those, at mixed instants %"] = pct(int(mixed.sum()), int(multi_same_run.sum()))
    row["of mixed, digits differ %"] = pct(int(visible.sum()), int(mixed.sum()))

    # M2 under the new rule: must be zero by construction.
    new_mixed = 0
    for run in runs:
        run_keys = [k for k in keys if k[0] == run]
        for a in range(len(run_keys)):
            for b in range(a + 1, len(run_keys)):
                ka, kb = run_keys[a], run_keys[b]
                new_mixed += int((new_ans[ka] & new_ans[kb] & (new_col[ka] != new_col[kb])).sum())
    row["new: mixed instants"] = new_mixed

    # M3: a purely vertical 2 px move with the trace answering at both ends.
    for rule, ans, col in (("old", old_ans, old_col), ("new", new_ans, new_col)):
        pairs = flips = value_flips = 0
        for key in keys:
            both = ans[key][:, :-2] & ans[key][:, 2:]
            moved = both & (col[key][:, :-2] != col[key][:, 2:])
            codes = by_key[key].codes
            lower = np.where(moved, col[key][:, :-2], 0)
            upper = np.where(moved, col[key][:, 2:], 0)
            pairs += int(both.sum())
            flips += int(moved.sum())
            value_flips += int((moved & (codes[lower] != codes[upper])).sum())
        row[f"{rule}: vertical 2px pairs"] = pairs
        row[f"{rule}: instant moves %"] = pct(flips, pairs)
        row[f"{rule}: printed value moves %"] = pct(value_flips, pairs)
        row[f"{rule}: of instant moves, value moves %"] = pct(value_flips, flips)

    # M4: reachability, per trace.
    retained = {}
    reachable_old = {}
    reachable_new = {}
    columns_old = {}
    columns_new = {}
    extra = 0
    for key in keys:
        trace = by_key[key]
        o, n = old_ans[key], new_ans[key]
        extra += int((n & ~o).sum())
        retained[f"{key[1].value}/r{key[0]}"] = round(pct(int((o & n).sum()), int(o.sum())), 1)
        drawn = int(len(trace.times))
        reachable_old[f"{key[1].value}/r{key[0]}"] = round(
            pct(len(set(old_col[key][o].tolist())), drawn), 1
        )
        reachable_new[f"{key[1].value}/r{key[0]}"] = round(
            pct(len(set(new_col[key][n].tolist())), drawn), 1
        )
        # Pixel columns (any phase, any height) at which the trace answers,
        # over the pixel columns the trace is drawn across.
        px_of = np.arange(len(xs)) // len(PHASES)
        first_px = int(trace.times[0] / s_per_px)
        last_px = int(trace.times[-1] / s_per_px)
        drawn_px = set(range(first_px, last_px + 1))
        columns_old[f"{key[1].value}/r{key[0]}"] = round(
            pct(len(set(px_of[o.any(axis=1)].tolist()) & drawn_px), len(drawn_px)), 1
        )
        columns_new[f"{key[1].value}/r{key[0]}"] = round(
            pct(len(set(px_of[n.any(axis=1)].tolist()) & drawn_px), len(drawn_px)), 1
        )
    row["new answers where old does not"] = extra
    row["old answering area kept under new %"] = retained
    row["drawn instants reachable, old %"] = reachable_old
    row["drawn instants reachable, new %"] = reachable_new
    row["pixel columns answered, old %"] = columns_old
    row["pixel columns answered, new %"] = columns_new

    # M5: what the reader sees change, over positions the old rule answers.
    same = instant_only = value_too = lost = 0
    old_sets = np.zeros(hoverable.shape, dtype=np.int64)
    new_sets = np.zeros(hoverable.shape, dtype=np.int64)
    for bit, key in enumerate(keys):
        old_sets |= old_ans[key].astype(np.int64) << bit
        new_sets |= new_ans[key].astype(np.int64) << bit
    same_set = hoverable & (old_sets == new_sets)
    column_moved = np.zeros_like(hoverable)
    value_moved = np.zeros_like(hoverable)
    for key in keys:
        both = old_ans[key] & new_ans[key]
        moved = both & (old_col[key] != new_col[key])
        codes = by_key[key].codes
        column_moved |= moved
        value_moved |= moved & (
            codes[np.where(moved, old_col[key], 0)] != codes[np.where(moved, new_col[key], 0)]
        )
    row["readout identical %"] = pct(int((same_set & ~column_moved).sum()), int(hoverable.sum()))
    row["same traces, an instant moved %"] = pct(
        int((same_set & column_moved).sum()), int(hoverable.sum())
    )
    row["same traces, a printed value moved %"] = pct(
        int((same_set & value_moved).sum()), int(hoverable.sum())
    )
    row["a trace stops answering %"] = pct(
        int((hoverable & (old_sets != new_sets)).sum()), int(hoverable.sum())
    )
    row["nothing answers under new %"] = pct(
        int((hoverable & (new_sets == 0)).sum()), int(hoverable.sum())
    )

    # Magnitudes. Instant spread inside one box, per run (old rule), in drawn
    # columns and seconds; and how far a vertical 2 px move shifts the instant.
    spreads = []
    for run in runs:
        run_keys = [k for k in keys if k[0] == run]
        if len(run_keys) < 2:
            continue
        cols = np.stack([np.where(old_ans[k], old_col[k], -1) for k in run_keys])
        times = by_key[run_keys[0]].times
        present = cols >= 0
        count = present.sum(axis=0)
        hi = np.where(present, cols, -(10**9)).max(axis=0)
        lo = np.where(present, cols, 10**9).min(axis=0)
        sel = (count >= 2) & (hi != lo)
        if sel.any():
            spreads.extend((times[hi[sel]] - times[lo[sel]]).tolist())
    if spreads:
        a = np.array(spreads)
        row["mixed-instant spread s (median/p95/max)"] = (
            float(np.median(a)),
            float(np.percentile(a, 95)),
            float(a.max()),
        )
    shifts = []
    rel = []
    pp = []
    for key in keys:
        trace = by_key[key]
        both = old_ans[key][:, :-2] & old_ans[key][:, 2:]
        moved = both & (old_col[key][:, :-2] != old_col[key][:, 2:])
        lower = old_col[key][:, :-2][moved]
        upper = old_col[key][:, 2:][moved]
        shifts.extend(np.abs(trace.times[upper] - trace.times[lower]).tolist())
        changed = trace.codes[lower] != trace.codes[upper]
        a, b = trace.percents[lower][changed], trace.percents[upper][changed]
        pp.extend(np.abs(a - b).tolist())
        rel.extend((np.maximum(a, b) / np.maximum(np.minimum(a, b), 1e-12)).tolist())
    if shifts:
        a = np.array(shifts)
        row["vertical-move instant shift s (median/p95/max)"] = (
            float(np.median(a)),
            float(np.percentile(a, 95)),
            float(a.max()),
        )
    if pp:
        a = np.array(pp)
        r = np.array(rel)
        row["vertical-move value change pp (median/p95/max)"] = (
            round(float(np.median(a)), 4),
            round(float(np.percentile(a, 95)), 4),
            round(float(a.max()), 4),
        )
        row["vertical-move value ratio (median/p95/max)"] = (
            round(float(np.median(r)), 3),
            round(float(np.percentile(r, 95)), 3),
            round(float(r.max()), 3),
        )
    # Rule B (old eligibility, time-nearest column): how far the reported point
    # would sit from the pointer where rule A declines to answer.
    far = []
    for key in keys:
        trace = by_key[key]
        lost = old_ans[key] & ~new_ans[key]
        if not lost.any():
            continue
        ii, jj = np.nonzero(lost)
        for i, j in zip(ii[::7], jj[::7]):
            c = time_nearest(trace.times, xs[i])
            far.append(
                float(
                    np.hypot(
                        (xs[i] - trace.times[c]) / s_per_px, (ys[j] - trace.percents[c]) / p_per_px
                    )
                )
            )
    if far:
        a = np.array(far)
        row["rule B: reported point from pointer px where A declines (median/p95/max)"] = (
            round(float(np.median(a)), 1),
            round(float(np.percentile(a, 95)), 1),
            round(float(a.max()), 1),
        )
    return row


def cross_check(frame, results, rng, which):
    """Hold the scan's selection against the shipped function at random positions."""

    traces, xs, ys, s_per_px, p_per_px, old_ans, old_col, new_ans, new_col = results
    ans, col = (old_ans, old_col) if which == "old" else (new_ans, new_col)
    by_key = {(t.run, t.quantity): t for t in traces}
    mismatches = 0

    for _ in range(400):
        i = rng.randrange(len(xs))
        j = rng.randrange(len(ys))
        target = nearest_trace_point(frame, float(xs[i]), float(ys[j]), s_per_px, p_per_px, RADIUS)
        shipped = (
            set() if target is None else {(r.run, r.quantity, r.time_s) for r in target.readings}
        )
        scanned = {
            (key[0], key[1], float(by_key[key].times[col[key][i, j]]))
            for key in by_key
            if ans[key][i, j]
        }
        mismatches += shipped != scanned

    return mismatches


def main():
    which = "new" if "--check-new" in sys.argv else "old"
    rng = random.Random(20260922)
    rows = []

    for label, pair, frame in build_cases():
        results = scan(frame)
        mismatches = cross_check(frame, results, rng, which)
        row = report(label, pair, frame, results)
        row[f"cross-check mismatches vs shipped ({which} rule)"] = mismatches
        rows.append(row)

        for key, value in row.items():
            print(f"{key}: {value if not isinstance(value, float) else round(value, 2)}")
        print()
        sys.stdout.flush()


if __name__ == "__main__":
    main()
```

`scan_wash_in.py`:

```python
"""PL-1K9G: the wash-in plot's hover under the 2-D rule and the time rule."""

import random
import sys
from bisect import bisect_left

import numpy as np

sys.path.insert(0, ".")
from scan_1k9g import RADIUS, WIDTH_PX, build_cases, time_nearest  # noqa: E402

from anesthesia_sim.app.chart_frame import WASH_IN_AXIS_MAXIMUM, nearest_wash_in_point  # noqa: E402
from anesthesia_sim.app.formatting import format_wash_in_ratio  # noqa: E402

HEIGHT_PX = 200  # theme.WASH_IN_CHART_HEIGHT
PHASES = (0.125, 0.375, 0.625, 0.875)


def points_of(run):
    """Every drawn wash-in point of one run, in stretch order, ascending in time."""

    times, ratios = [], []
    for stretch in run.wash_in:
        times.extend(stretch.times_s)
        ratios.extend(stretch.ratios)
    return np.array(times), np.array(ratios)


def main(which):
    seen = set()
    rng = random.Random(7)
    for label, _, frame in build_cases():
        key = (label, len(frame.runs))
        if key in seen:
            continue
        seen.add(key)
        s = (frame.stop_s - frame.start_s) / WIDTH_PX
        r = WASH_IN_AXIS_MAXIMUM / HEIGHT_PX
        ys = (np.arange(HEIGHT_PX) + 0.5) * r
        pairs = flips = vflips = area_old = area_new = extra = 0
        for run_index, run in enumerate(frame.runs):
            times, ratios = points_of(run)
            if not len(times):
                continue
            codes = np.array([hash(format_wash_in_ratio(v)) for v in ratios])
            last = times[-1] / s + RADIUS + 1
            xs = [frame.start_s + (px + ph) * s for px in range(int(last) + 1) for ph in PHASES]
            oa = np.zeros((len(xs), HEIGHT_PX), bool)
            oc = np.full(oa.shape, -1)
            na = np.zeros(oa.shape, bool)
            nc = np.full(oa.shape, -1)
            for i, t in enumerate(xs):
                d = np.sqrt(
                    ((t - times[None, :]) / s) ** 2 + ((ys[:, None] - ratios[None, :]) / r) ** 2
                )
                k = np.argmin(d, axis=1)
                inside = d[np.arange(HEIGHT_PX), k] <= RADIUS
                oa[i], oc[i] = inside, np.where(inside, k, -1)
                c = time_nearest(times, t)
                dn = np.sqrt(((t - times[c]) / s) ** 2 + ((ys - ratios[c]) / r) ** 2)
                na[i], nc[i] = dn <= RADIUS, np.where(dn <= RADIUS, c, -1)
            for ans, col, rule in ((oa, oc, "old"), (na, nc, "new")):
                both = ans[:, :-2] & ans[:, 2:]
                moved = both & (col[:, :-2] != col[:, 2:])
                if rule == "old":
                    pairs += int(both.sum())
                    flips += int(moved.sum())
                    vflips += int(
                        (
                            moved
                            & (
                                codes[np.where(moved, col[:, :-2], 0)]
                                != codes[np.where(moved, col[:, 2:], 0)]
                            )
                        ).sum()
                    )
                else:
                    assert not moved.any(), "the time rule moved an instant vertically"
            area_old += int(oa.sum())
            area_new += int((oa & na).sum())
            extra += int((na & ~oa).sum())
            reach_new = len(set(nc[na].tolist())) / len(times)
            # hold the scan's time rule against the shipped function
            if which == "new":
                bad = 0
                for _ in range(300):
                    i, j = rng.randrange(len(xs)), rng.randrange(HEIGHT_PX)
                    target = nearest_wash_in_point(frame, xs[i], float(ys[j]), s, r, RADIUS)
                    got = (
                        None
                        if target is None
                        else next((x.time_s for x in target.readings if x.run == run_index), None)
                    )
                    want = float(times[nc[i, j]]) if na[i, j] else None
                    bad += got != want
                print(f"  cross-check run {run_index}: {bad} mismatches of 300")
            print(
                f"{label} run {run_index}: stretches {len(run.wash_in)}, drawn instants reachable under new {100 * reach_new:.1f}%"
            )
        print(
            f"{label}: vertical 2 px pairs {pairs}, instant moves {100 * flips / max(pairs, 1):.1f}%, printed ratio moves {100 * vflips / max(pairs, 1):.1f}%; old area kept {100 * area_new / max(area_old, 1):.1f}%; new-only area {extra}"
        )


main("new" if "--check-new" in sys.argv else "old")
```
