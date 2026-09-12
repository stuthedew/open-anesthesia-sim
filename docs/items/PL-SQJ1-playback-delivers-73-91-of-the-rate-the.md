---
id: PL-SQJ1
title: Playback delivers 73-91% of the rate the dropdown displays: 300x measured at 220x, 1x at 0.9x, so the clock on screen runs slower than its label
priority: P2
effort: M
status: needs-decision
classes: ux, perf
feature: presentation-safety
touches: src/anesthesia_sim/app/playback.py, src/anesthesia_sim/app/simulation_view.py
added: 2026-09-08
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
