---
id: PL-QXSB
title: Decide whether the interface should stay on Flet: every route inside it has now been measured, and the remaining lever is fewer controls
status: done
priority: P2
effort: M
classes: perf, ux
feature: teachable-case
touches: src/anesthesia_sim/app, ROADMAP.md, docs/ARCHITECTURE.md
verify: python3 tools/doc_check.py check && grep -qF 'Decided, 2026-09-10: leave Flet' docs/items/PL-QXSB-decide-whether-the-interface-should-stay-on.md
added: 2026-09-08
closed: 2026-09-10
---

**Problem.** Decide whether the interface should stay on Flet: every route inside it has now been measured, and the remaining lever is fewer controls

**Raised by the project owner, 2026-09-08**, after `PL-KP7H` and `PL-R2YM`
landed: "It shouldn't be this laggy." The instinct is right, and there is now
one number that says so rather than a feeling.

**The floor, which is the whole argument.** Hide every compartment trace and
the concentration chart holds 54 point controls; the rest of the dashboard is
a few dozen more. `page.update()` on that page costs **10.3 ms** — and an
*idle* update, with nothing changed since the last one, costs the same 10.3 ms
(`PL-YSZN`). Five times a second, a dashboard of roughly a hundred controls
spends a tenth of a second per second of Python discovering that nothing
moved. That is not an application problem and no amount of drawing fewer
points reaches it.

**Where it goes.** `cProfile` puts 64% of a frame in
`flet/controls/object_patch.py`'s `_compare_dataclasses` — about 7 800
recursive dataclass comparisons and 92 000 `getattr` calls per frame, over
~2 080 point controls, producing a patch of 3-5 KiB. Cost is linear in
controls *present* at about 24.5 us each and indifferent to how many changed.
Flet's update model does work proportional to the size of the whole interface
on every frame; a live scientific chart puts thousands of objects into that
interface.

**What has already been spent on it, which is the reason to ask now rather
than later.** `PL-001` and `PL-010` (stop rebuilding point objects per frame),
`PL-0VM7` (stop copying the run history per frame), `PL-Q197` (anchor
decimation to absolute sample index, after the Flutter client was pegged at
100% CPU), `PL-CG7J`, `PL-KP7H` (the per-point tooltip), `PL-R2YM` (coalesce a
drag's frames), `PL-YDKJ` (decided to accept the per-control chart). Seven
items and four releases against one cost. Each was correct and each bought
less than the one before.

**And every route inside Flet is now measured and closed.**

- **No array transport exists.** `PL-YDKJ` option 2: `flet.Canvas`'s
  `Path.PathElement` is `@value` rather than `@control`, which suggested a
  polyline would cross as one field. Flet's diff descends into value lists
  element by element, so a canvas costs the same ~2 operations per vertex.
- **Server-side rendering loses.** `PL-YDKJ` option 3, measured 2026-09-08:
  44.4 ms a frame in the mode this chart is in, and 34.8 ms at 2x even in the
  variant that needs a sweep display to be possible at all, against ~10 ms for
  the chart today. It also pulls numpy, against a recorded decision.
- **Concurrency does not apply.** The diff is GIL-bound Python object
  traversal, so threads only time-slice it. Subinterpreters
  (`concurrent.interpreters`, present in this project's Python 3.14) cannot
  share objects at all — `NotShareableError` is in the API — and the diff's
  entire job is walking control objects in the main interpreter's heap, so the
  expensive half structurally cannot move. Free-threaded CPython could overlap
  the *simulation* with the diff, and the simulation is 12% of a tick at 300x,
  so that is the ceiling on the whole idea.

So the remaining lever inside Flet is fewer controls, which `PL-YDKJ` accepted
and `CHART_COLUMN_BUDGET_PER_SERIES` documents. This item is the question that
lever does not answer.

**Why it matters.** Not because the application is unusable — it is not.
Because the cost is a *floor* rather than a slope, so it bounds every UI
ambition this project has left: roadmap item 33's interface pass, item 24's
settings panel, a second chart for a branched run (`v0.5.0`'s whole point),
more traces, a faster cadence. Each of those adds controls, and controls are
the thing being charged for on every frame whether they change or not. Seven
items have been spent discovering that, and each bought less than the last;
the eighth will buy less still. Deciding this deliberately, once, is cheaper
than meeting it again in every future UI item — and the answer may well be
"stay", which is worth having written down with a number beside it rather than
re-derived each time somebody notices the lag.

**Two other open items are the same question wearing different hats**, and
that is worth noticing: `PL-F0L8` (establish what accessibility Flet's
rendering backend can actually deliver) and `PL-2QMK` (no session in the web
container can visually confirm a chart change, because Flet's web renderer
fetches Flutter assets the egress proxy denies). Three open questions about
what this toolkit can deliver, and none of them asks whether it is the right
one.

**The case against, stated first because it is strong.** The application
works. `CLAUDE.md` says the simulator is the point and warns that the
apparatus is at permanent risk of becoming the work; a toolkit migration is
that risk in its most expensive available form, on a solo project whose
measure of success is still enjoying it in several years. Nothing is currently
blocked. "It feels laggy" is a real defect but it is not a correctness one,
and after this session's two fixes the Python side uses about 47 ms of a 200 ms
frame at 300x, with input-delay p90 around 20-30 ms.

**What a decision would need, and the shape of the work.** Not a migration — a
bake-off. Build the same six-trace live chart plus a dozen readouts at 5 Hz on
each candidate and measure four things: frame cost at the shipped point count,
frame cost at four times it (the ceiling question), packaged size, and whether
the rendered output can be asserted on headlessly, which is what `PL-2QMK`
would pay a lot for. Candidates worth costing, named rather than recommended:

1. **Stay, and make the control count a standing budget** — the honest null
   option, and it needs a number written down rather than a habit.
2. **Flet for the shell, something else for the chart alone.** Keeps the
   packaging and the existing dashboard; the chart is where the controls are.
3. **A Python-native toolkit built for this.** `pyqtgraph` on PySide/Qt exists
   precisely for live scientific plotting at high refresh rates; Dear PyGui and
   Kivy are the other desktop options. Cost: a different packaging story and
   the whole dashboard rewritten.
4. **A web front end over the existing Python core.** Cheaper than it sounds
   *only* because `core/` and `app/controller.py` import no Flet and
   `tools/import_boundary_check.py` enforces it, so the model and the run
   history already survive any of these unchanged. That boundary is what makes
   this question askable at all.

**Decision needed.** Whether to spend a bake-off on the four candidates
above, or to close this as "stay on Flet" with a written control budget and
stop re-opening the question. Both are legitimate answers and the second is
cheaper; what is not legitimate is leaving it unasked while every future UI
item pays the floor without knowing it is there.

**Done when** one of the two is recorded with its reasoning — either the
bake-off's numbers and a chosen direction, or an explicit decision to stay
with the control budget written into `docs/ARCHITECTURE.md` and the ceiling
`CHART_COLUMN_BUDGET_PER_SERIES` already documents generalised to the whole
page.

**First step.** Answer the decision above; it is the project owner's call,
which is why this is `needs-decision` rather than `ready`. If the answer is
the bake-off, candidates 1 and 2 are cheap to measure and settle most of it
without touching the dashboard.

## Qt investigated at the project owner's direction, 2026-09-08

"I think we should look into pyside or pyqt." Two of the four candidates
above, and the investigation settles more than expected.

**PyQt is ruled out by licensing rather than by preference.** This project is
Apache-2.0 (`pyproject.toml`, `LICENSE`). Riverbank's own PyPI page for PyQt6
6.11.0 states: "PyQt6 is released under the GPL v3 license and under a
commercial license." Linking Apache-2.0 code against GPLv3 PyQt means
redistributing the combined work under GPLv3 — relicensing this project — or
buying a commercial licence. That is a decision about what the project *is*,
not a toolkit trade-off, and nothing below depends on taking it.

**PySide6 does not have that problem.** `PySide6-Essentials` 6.11.2 and
`shiboken6` declare `LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only`; the LGPL
option lets an Apache-2.0 application link dynamically and keep its own
licence. `PySide6-Addons` (which carries QtCharts) declares the same.
`pyqtgraph` 0.14.0 is MIT and `numpy` is BSD-3-Clause. So the licence-clean
stack is **PySide6 + pyqtgraph**, and it is also the fast one.

### The measurement

PySide6 6.11.2 with pyqtgraph 0.14.0, offscreen, six traces plus twelve
numeric readouts — the shape of the real dashboard. Timed: `setData` on six
curves, the x-range move, and twelve `setText` calls. Median of 60 frames.

| Points per trace | Total points | Python-side frame |
| ---: | ---: | ---: |
| 282 — the shipped column budget | 1 692 | **0.51 ms** |
| 1 128 — four times it | 6 768 | 0.72 ms |
| 18 000 — a 30-minute case, every sample | 108 000 | 0.92 ms |
| 108 000 — a 3-hour case, every sample | 648 000 | 1.96 ms |

Against Flet's `page.update()` at 20.3 ms for the whole page at 300x, of which
the ~2 080 point controls are about half.

**Two things in that table, and the second is the larger.** It is roughly
twenty times cheaper at the point count actually shipped. And it *barely
scales*: 380 times the points costs four times the frame, because data crosses
as arrays rather than as one control object per point. Flet's cost is linear in
controls present; Qt's is not a function of them at all.

**It would raise the column ceiling.** 648 000 points in 1.96 ms means a
three-hour case could be drawn at a far finer resolution than the current
one. `CHART_COLUMN_BUDGET_PER_SERIES` and this item's own accepted ceiling
are machinery for a constraint that would slacken.

**Rewritten 2026-09-08 (`PL-8LXM`).** This paragraph read "it would make
decimation optional" and named `app/chart_downsampling.py`, M4 and `PL-8LXM`
as machinery that would stop existing. There is no decimation to make
optional: `PL-2FM6` deleted the sample store, and the chart evaluates the
run's score at the instants it plots. The argument survives as a statement
about how *many* columns are affordable, which is what the measurement
actually supports; it no longer bears on whether a selection rule is needed,
because there is no selection.

### What this measurement is not

**Paint cost is unmeasurable in this container** — no GPU, a software
rasteriser, and an offscreen platform plugin. Forcing a full repaint gave
18-28 ms *including for a frame where nothing changed*, which is `grab()` and
`processEvents` re-rendering the whole surface offscreen rather than what a
composited desktop pays. So the table measures the term `PL-YSZN` found to be
98% of a Flet frame, not the whole frame.

The structural claim is what carries, and it does not depend on the timing:
**Qt has no diff.** A widget is handed new data, marks itself dirty, and the
toolkit repaints the dirty region. Nothing walks the whole interface to find
out what changed, which is precisely what Flet's 10.3 ms idle floor is.

### Costs, measured where measurable

- **Installed size**: PySide6-Essentials 233 MB + numpy 33 MB + pyqtgraph
  7.7 MB against flet 5.5 MB + flet_web 73 MB. About 3.5x, trimmable because a
  packaged app ships selected Qt modules rather than all of them, but real for
  a download.
- **numpy enters**, required by pyqtgraph. `docs/WORKING_NOTES.md` § "Decided:
  no numpy" argued *fit* — that numpy has no append and would make `RunHistory`
  harder — and concluded no for compaction and chart storage. numpy underneath
  a plotting library is a different proposition, so this reopens that note's
  scope rather than contradicting its conclusion; it should be re-argued, not
  cited either way.
- **The dashboard is rewritten**: `app/simulation_view.py` (3 586 lines),
  `app/chart_series.py`, `app/theme.py`. What is *not* rewritten is why this is
  tractable at all — `core/` and `app/controller.py` import no Flet and
  `tools/import_boundary_check.py` enforces it, and `app/formatting.py`,
  `app/playback.py`, `app/chart_time_base.py` and `app/wash_in.py` are
  Flet-independent by the same discipline. The model, the run, the score and
  every unit conversion survive untouched.
- **Flet's web target is given up.** Nothing ships it today and `PL-2QMK` is
  about that renderer failing rather than about wanting it, but it is a
  capability lost.

### One thing it would buy that is not speed

`PL-2QMK` records that no session in the web container can visually confirm a
chart change. **Qt rendered offscreen in that very container — it is how this
benchmark ran.** Headless screenshot tests of the real interface become
ordinary rather than impossible, which is what `PL-90Y6`, `PL-3355`,
`PL-W8DQ`, `PL-GVXP` and the rest of `presentation-safety` are waiting on.
`PL-F0L8` (accessibility) is the other Flet-capability question; Qt's
`QAccessible` would need checking on its own terms rather than assumed.

### Recommendation

Not a migration, and no longer "stay on Flet with a control budget" either —
the measurement is strong enough that the null option is now the weaker one.
**A spike:** port the concentration chart and the readout row alone to
PySide6 + pyqtgraph, behind the existing controller, and run it on the owner's
own machine. It is bounded, it throws away cleanly, and it answers the two
things this container cannot — real paint cost on real hardware, and whether
the interface can be made to look the way it is meant to.

## Decided, 2026-09-10: leave Flet for PySide6 + pyqtgraph

**The project owner's call, on the evidence below.** This item asked whether to
spend a bake-off or close as "stay with a control budget". The bake-off was
spent - `PL-QXSB`'s own measurement, then `PL-55DH`'s spike, then `PL-X9T3`'s
run on the owner's machine - and the answer is to move.

**The premise this item was opened on is not the reason.** It was raised on "It
shouldn't be this laggy", and after `PL-2FM6` the owner reports the Flet build
as no longer noticeably slow. A migration argued from that symptom would be
arguing from something that is gone. All four surviving grounds are recorded in
`docs/WORKING_NOTES.md` under "Measured on real hardware"; in short:

1. **Input latency**, the axis "laggy" actually named: 0.85-2.46 ms p90 against
   Flet's 20-30 ms. An order of magnitude, and the mechanism rather than the
   hardware is what the gap is made of - Flet's event loop is blocked by the
   control-tree diff every frame and Qt has no diff to be blocked by.
2. **`PL-GS3R` is a safety decision that the toolkit decides.** Its cheapest
   route out of 0.26 MAC of chord error is more columns, measured at 49.4 ms of
   a 200 ms budget on Qt against about 78 ms for Flet's diff alone - untenable
   on Flet once this milestone's second chart doubles the control count.
3. **`PL-2QMK`**, exercised rather than argued: `spikes/qt/qt_spike.py
   --screenshot` writes a PNG of the running interface in the very container
   where Flet's renderer cannot load. Most of `presentation-safety` is waiting
   on that.
4. **Headroom**: 10-14% of the render budget at the shipped settings, for
   everything Flet spent 13-23% of it failing to finish.

**What is not claimed.** Qt does not make the point count stop mattering - the
whole frame scales at about 8.7 us per drawn point, and `paint` is the largest
single stage at 600 columns. What does not scale is the diff, because there is
none. `PL-C92D` still owes a re-measurement of Flet's own frame on the
post-`PL-2FM6` tree, and the `advance` and `refresh` rows of every comparison
here are architecture rather than toolkit until it lands.

**What survives the port untouched, which is why this is tractable at all**:
`core/` entire, `app/controller.py`, `app/formatting.py`,
`app/chart_time_base.py`, `app/playback.py`, `app/wash_in.py`,
`app/control_timeline.py`. `tools/import_boundary_check.py` enforces that
boundary and the spike proved it empirically - it drove the real
`SimulationController` with no adaptation whatsoever. What is rewritten is
`app/simulation_view.py` (3 619 lines), `app/chart_series.py` and `app/theme.py`.

**Costs accepted with the decision**: numpy enters as a pyqtgraph dependency,
reopening the scope of this file's "Decided: no numpy" note rather than
contradicting its conclusion; installed size roughly 3.5x, trimmable in a
packaged build; and Flet's web target is given up, which nothing ships today.

**Not yet scoped.** The port is a milestone-scale scope change and `ROADMAP.md`
is where that is decided, per `CLAUDE.md`'s rule against implementing beyond the
current milestone. This item records the direction; it does not authorise the
work, and the items that do it are written after the milestone is scoped.
