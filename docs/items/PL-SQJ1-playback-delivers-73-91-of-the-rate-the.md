---
id: PL-SQJ1
title: Playback delivers 73-91% of the rate the dropdown displays: 300x measured at 220x, 1x at 0.9x, so the clock on screen runs slower than its label
priority: P2
effort: M
status: ready
classes: ux, perf
feature: presentation-safety
touches: src/anesthesia_sim/app/playback.py, src/anesthesia_sim/app/simulation_view.py, docs/MODEL.md
added: 2026-09-08
verify: ! grep -qF '_run_simulation_timer' src/anesthesia_sim/app/playback.py && grep -qF '2026-09-27' src/anesthesia_sim/app/playback.py && grep -qF 'delivered rate' docs/MODEL.md
---

**Problem.** `app/playback.py` states that "the rate is stated as a multiple of
real time, because that is what a reader can check", and refuses any rate that
does not land on a whole number of steps rather than "silently play at a rate
other than the one displayed". Measured 2026-09-08, running the view's own
`_run_simulation_timer` and `_run_render_timer` under asyncio for 8 real
seconds each, it plays at a rate other than the one displayed anyway — for a
different reason, which that guard does not cover:

| Displayed | Delivered | Of nominal | Input delay median | p90 | max |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1x | 0.9x | 91% | 0.5 ms | 14.5 ms | 36.5 ms |
| 5x | 4.1x | 82% | 0.7 ms | 43.4 ms | 72.4 ms |
| 20x | 15.4x | 77% | 0.9 ms | 56.5 ms | 138.7 ms |
| 60x | 44.2x | 74% | 2.7 ms | 59.6 ms | 184.1 ms |
| 300x | 219.9x | 73% | 0.6 ms | 49.4 ms | 169.0 ms |

Input delay is how long a callback that is ready to run waits for the event
loop. Flet dispatches control handlers inline on that loop, so it is the delay
between a reader's click and the handler for it starting.

**Why this is not simply the documented behavior.** `_run_simulation_timer`
already says a host that wakes the loop late leaves the run behind the wall
clock "and it stays behind", and that this makes the run slower and never
different — which is the reproducibility guarantee and is intact here. Nothing
below is a correctness failure of the model. What is at issue is the *label*:
the dropdown reads "300x real time" and the simulated clock advances at 220x,
so a reader timing a wash-in against their own watch reads a case that takes
36% longer than the interface says it will. `CLAUDE.md` counts a correct
number under a wrong label as a presentation failure, and `playback.py` treats
the rate as a claim a reader can check.

The shortfall is a consequence rather than a cause: `PL-YSZN` measures where
the loop's time goes. Cutting the frame cost raises the delivered rate without
touching this item.

**First step.** Decide what the interface owes a reader here — nothing, a
qualification on the label, or a measured "delivering ~220x" readout — and
whether the answer changes once `PL-YSZN`'s frame cost comes down. Re-measure
on the owner's own machine first: this was taken on a 4-vCPU shared container
and the shortfall is a property of the host, not of the code.

**Why it matters.** `CLAUDE.md` counts a correct number under a wrong label as a
presentation failure, and `app/playback.py` explicitly treats the rate as "a
multiple of real time, because that is what a reader can check". A reader timing
a wash-in against their own watch at the 300x setting gets a case that takes 36%
longer than the interface says it will, which is exactly the check the module
invites them to make. Nothing about the model is wrong - the run is slower and
never different, so reproducibility holds - but the dropdown is making a claim
the application does not keep.

**Decision needed.** What the interface owes a reader here: nothing, a
qualification on the label, or a measured "delivering ~220x" readout beside the
setting. Each is defensible and they imply different work.

**Answered 2026-09-27.** Nothing on screen changes: the label is left as it is
and the reasoning recorded, in `playback.py`'s docstring and in
`docs/MODEL.md` § "Interface boundary" (project owner, 2026-09-27, ratified,
over building the detect-and-disclose guard now, and over qualifying the
label). The guard - the delivered rate shown beside the set one when fewer
than 95% of ticks fire over a 50-tick window - is filed by the build thread as
a `feature` item outside the gate, on the design under option 3 below. The
re-measurement on the QTimer path, the three options and the method are under
"Design round 2026-09-27: recommendations" below; the done-when's first clause
is the one taken, and its re-measurement on the owner's machine stands. Status
`ready`; `touches` widened to `docs/MODEL.md`.

**Re-measure before deciding, and on the right machine.** The figures above were
taken on a 4-vCPU shared container; the shortfall is a property of the host. The
frame cost they are a consequence of is also about to change - `PL-CNCF` puts
6.2 ms of every frame in `controller.drawn_window`, and the PySide6 port removes
the 26-45 ms `page.update()` term entirely - so the shortfall this item
describes may be largely gone by the time it is worked. Decide after the port
has a running dashboard, not before.

**Done when.** The delivered rate is re-measured on the owner's machine against
the ported interface, and the label is either left alone with the reasoning
recorded, qualified, or joined by a delivered-rate readout.

## Narrowed by PL-C4W8's Gate 2 staleness sweep, 2026-09-21

**The measurement is dead; the question may not be.** The 73-91% figure and
the 26-45 ms `page.update()` term were both taken against Flet's asyncio timer
dispatch, and the 2026-09-15 PySide6 port (`ae8fc7bc`) removed that mechanism
entirely. `SimulationView._run_simulation_timer`, which this brief reasons
about throughout, no longer exists: `simulation_view.py` now builds a
`QTimer(self)` with `Qt.TimerType.PreciseTimer` and starts it from
`start_simulation_timer`. So nothing above this section may be cited as a
current measurement of anything.

What survives is the *concern*, unverified: does the QTimer path deliver the
labelled multiplier? That is exactly what this brief itself said to settle
"after the port has a running dashboard, not before", and the port has one.
Re-measure against the QTimer plumbing before doing anything else here; do not
carry the old percentages forward.

**Found alongside it:** `src/anesthesia_sim/app/playback.py:54` still cites
`SimulationView._run_simulation_timer` in live prose. That is drift in a live
document rather than in a closed brief, and it is filed rather than repaired
here because it is outside this item's `touches`.

## Design round 2026-09-27: recommendations

Recommendations, not decisions: the thread that records the project owner's
answer marks each `(project owner, DATE, ratified)` or replaces it.

**Re-measured 2026-09-27 on the QTimer path**, which the staleness sweep asked
for before anything else. Method: the real `SimulationView` in a shown
`QMainWindow` on the offscreen platform, run started, both timers running as
`main.py` runs them, `RunView.step_tick` and `SimulationView.render_tick`
wrapped to time each call, elapsed simulated time read before and after a
wall-clock window. 4-vCPU shared container, tree `aeb00392`:

| Set | Wall | Delivered | Of nominal | Tick period median / p90 / max | Tick cost median / max | Frame cost median / max |
| ---: | ---: | ---: | ---: | --- | --- | --- |
| 1× | 8 s | 1.0× | 99.5% | 100.2 / 100.5 / 100.8 ms | 0.2 / 1.2 ms | 5.5 / 10.4 ms |
| 5× | 8 s | 5.0× | 99.7% | 100.0 / 100.5 / 101.1 ms | 0.2 / 1.2 ms | 6.8 / 10.7 ms |
| 20× | 8 s | 19.8× | 98.9% | 99.9 / 100.7 / 100.8 ms | 0.5 / 1.3 ms | 7.9 / 41.0 ms |
| 60× | 8 s | 59.6× | 99.4% | 100.0 / 100.6 / 101.9 ms | 1.1 / 13.1 ms | 7.8 / 16.4 ms |
| 300× | 8 s | 296.9× | 99.0% | 99.9 / 100.7 / 101.0 ms | 4.6 / 26.4 ms | 8.5 / 9.8 ms |
| 300× | 30 s | 299.6× | 99.9% | 99.9 / 100.7 / 103.6 ms | 4.5 / 7.9 ms | 8.6 / 26.6 ms |

With the render timer stopped the figures are 98.7-100% at every rung, so
what remains is not the paint. The 0.1-1.3% is the measurement's own edge -
the first tick fires one interval after start, so 78-79 ticks arrive in 8 s
where 80 are expected and 297 in 30 s where 300 are - rather than the loop:
the tick period holds at 100 ms to within 4 ms at its worst.

**So the shortfall in the title is gone, and the mechanism that produced it
went with the toolkit.** Flet dispatched both cadences on one asyncio loop
behind a serializing `page.update()`; Qt's `PreciseTimer` fires the step slot
on its interval whatever the paint costs, and at 300× the burst is 4.6 ms of a
100 ms interval. The label is a claim the loop now keeps.

**What can still make it false, and by how much.** `step_tick` takes a fixed
burst and makes no step up (`run_view.py`, decision D7), so a tick the loop
could not service is lost and the delivered rate is the nominal one times the
fraction of ticks that fired. Qt coalesces a timeout the loop was holding
through rather than queueing it, so the loss is exactly the intervals during
which something held the loop past 100 ms. Nothing did in 70 s of measurement
here; the worst single frame was 41 ms. A host that does hold it - a paint
several times slower than this container's worst, or something else on the
loop - delivers less, and nothing on screen says so.

**Q. What the interface owes.** Three options and their trade.

1. **Leave the label; record why.** The claim holds on the shipped path,
   measured. `playback.py`'s docstring replaces its dead
   `SimulationView._run_simulation_timer` citation (line 54; `playback.py` is
   in this item's `touches`, so that drift rides here) with the QTimer path
   and this measurement, and `docs/MODEL.md` § "Interface boundary" says what
   the rate is a statement about: the setting, kept to within 1% on the
   measured host; the clock is exact at every rate; a host that cannot
   service a 100 ms tick delivers less, and nothing on screen says so. Size
   S. Leaves the residual silent.
2. **Qualify the label** - "up to 300×". True always, but it withdraws the
   check the module invites and says nothing about how far. Refused: it
   trades a precise claim that holds for a vague one, which is false
   uncertainty, the mirror of the false precision the standard forbids.
3. **Detect and disclose.** Count missed ticks from a monotonic clock read in
   `step_tick` for diagnosis only - steps per tick never change, and
   simulated time stays a count of steps, so D7 holds - over a trailing
   window of 50 ticks; when fewer than 95% fired, the rate text under the
   clock (`_playback_rate_text`, which `docs/MODEL.md` requires wherever
   simulated time is drawn) names the delivered rate beside the set one, in
   `MUTED` rather than `WARNING` since nothing is wrong with the model, and
   returns to the plain label once the window recovers. The 5% threshold sits
   above the 1% this measurement cannot separate from its own edges and below
   what a reader hand-timing a wash-in against a watch could notice at any
   rung. Size M: a clock read and a ring counter in `RunView`, a formatter in
   `app/formatting.py`, tests with a fake clock, the `docs/MODEL.md`
   paragraph.

**Recommendation: option 1 now, with option 3 filed by the build thread as a
`feature` item outside the gate.** The defect this item was filed for does not
reproduce on the shipped path, so what remains is a guard against a host
nobody has measured. `CLAUDE.md` asks to "Prefer an obvious failure/error
state to displaying a plausible-looking number when correctness cannot be
established", which would demand the guard if the number a reader acts on
could be wrong; that number is the clock, which is exact at every rate, and
the rate label is the setting. Filing the guard keeps it from being lost and
keeps an M build out of Gate 2. If the owner wants the guard now, option 3 is
built under this item and nothing is filed. Either way the done-when's
"re-measured on the owner's machine" stands: run the script below on the Mac,
and a delivered rate under 99% there reopens this recommendation.

**Method, kept so the next re-measurement does not rebuild it** (`PL-ZG5J`'s
lesson). Run with `QT_QPA_PLATFORM=offscreen uv run python measure_rate.py
30` from the repository root, or without the platform variable on a desktop:

```python
import os, sys, time, statistics
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow
from anesthesia_sim.app.controller import BranchedCase, SimulationController
from anesthesia_sim.app.qt_widgets import (
    WINDOW_SCREEN_FRACTION,
    declare_application_colours,
    initial_window_geometry,
)
from anesthesia_sim.app.simulation_view import SimulationView
from anesthesia_sim.app.playback import playback_rate_for

WALL_S = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
app = QApplication([])
declare_application_colours(app)
for multiplier in (1, 5, 20, 60, 300):
    case = BranchedCase(SimulationController())
    view = SimulationView((case.trunk,), case=case)
    window = QMainWindow()
    window.setCentralWidget(view)
    window.setGeometry(
        initial_window_geometry(
            app.primaryScreen().availableGeometry(),
            window.minimumSizeHint(),
            WINDOW_SCREEN_FRACTION,
        )
    )
    window.show()
    view.present(False)
    app.processEvents()
    run = view.runs[0]
    run._playback_rate = playback_rate_for(multiplier)
    ticks, cost = [], []
    original = run.step_tick

    def timed():
        t = time.perf_counter()
        ticks.append(t)
        original()
        cost.append(time.perf_counter() - t)

    run._step_timer.timeout.disconnect()
    run._step_timer.timeout.connect(timed)
    run.controller.start()
    before = run.controller.snapshot().elapsed_s
    view.start_simulation_timer()
    t0 = time.perf_counter()
    QTimer.singleShot(int(WALL_S * 1000), app.quit)
    app.exec()
    wall = time.perf_counter() - t0
    view.stop_timers()
    run.controller.pause()
    delivered = (run.controller.snapshot().elapsed_s - before) / wall
    periods = [b - a for a, b in zip(ticks, ticks[1:])]
    print(
        f"{multiplier}x: delivered {delivered:.1f}x = {100 * delivered / multiplier:.1f}% of nominal, "
        f"{len(ticks)} ticks, period median {1000 * statistics.median(periods):.1f} ms "
        f"max {1000 * max(periods):.1f} ms, tick cost median {1000 * statistics.median(cost):.1f} ms"
    )
    window.close()
    window.deleteLater()
    app.processEvents()
```

**For the build under option 1.** Add `docs/MODEL.md` to `touches`; the
done-when's first clause ("left alone with the reasoning recorded") is the one
taken.
