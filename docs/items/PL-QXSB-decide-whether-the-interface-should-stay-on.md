---
id: PL-QXSB
title: Decide whether the interface should stay on Flet: every route inside it has now been measured, and the remaining lever is fewer controls
status: needs-decision
priority: P2
effort: M
classes: perf, ux
feature: teachable-case
touches: src/anesthesia_sim/app, ROADMAP.md, docs/ARCHITECTURE.md
added: 2026-09-08
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
