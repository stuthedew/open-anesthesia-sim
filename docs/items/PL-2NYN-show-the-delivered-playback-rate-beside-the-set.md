---
id: PL-2NYN
title: Show the delivered playback rate beside the set one when fewer than 95% of ticks fire over a trailing 50-tick window, so a host that cannot service the 100 ms tick is disclosed on screen
priority: P3
effort: M
status: done
classes: feature
feature: presentation-safety
milestone: v0.6.22
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_formatting.py, tests/integration/test_qt_widgets.py, docs/INTERFACE.md, docs/MODEL.md
added: 2026-09-27
closed: 2026-11-23
pr: 2272
payoff: a learner on a host that cannot keep the 100 ms tick sees the rate the clock actually runs at, not a label it is not meeting
tests: tests/integration/simulation_view/test_simulation_view_loops.py::test_a_computer_that_falls_behind_shows_the_delivered_rate_beside_the_set_one
---

**Problem.** Show the delivered playback rate beside the set one when fewer than 95% of ticks fire over a trailing 50-tick window, so a host that cannot service the 100 ms tick is disclosed on screen

**Filed 2026-09-27 by the build thread that closed `PL-SQJ1`**, on the design
that item's design round put as option 3 and the project owner ratified
filing rather than building (project owner, 2026-09-27, ratified, over
building the guard under `PL-SQJ1` and over qualifying the label). A
`feature` item, so it sits outside the debt gate.

**Why it matters.** The rate label under the clock is a claim a reader can
check against a watch, and `app/playback.py` derives the steps per tick from
it so the label cannot drift from the loop. Measured 2026-09-27 on the QTimer
path the claim holds to within 1% at every rung on a 4-vCPU container. What
can still make it false is the host: `RunView.step_tick` takes a fixed burst
and makes no step up (decision D7), and Qt coalesces a timeout the loop was
holding through rather than queueing it, so a host that holds the loop past
100 ms loses ticks and delivers the nominal rate times the fraction of ticks
that fired - and nothing on screen says so. Nobody has measured such a host;
this is a guard against one.

**Design.**

- Read a monotonic clock in `RunView.step_tick` for diagnosis only. Steps per
  tick never change and simulated time stays a count of steps, so D7 holds and
  the run is unchanged by the guard.
- Count ticks fired against ticks expected over a trailing window of 50 ticks
  (5 s at the 100 ms interval).
- When fewer than 95% fired, the rate text under the clock
  (`_playback_rate_text`, which `docs/MODEL.md` requires wherever simulated
  time is drawn) names the delivered rate beside the set one - "300x set,
  about 220x delivered" - in `MUTED` rather than `WARNING`, since nothing is
  wrong with the model; it returns to the plain label once the window
  recovers.
- The 5% threshold sits above the 1% the 2026-09-27 measurement could not
  separate from its own edges (the first tick fires one interval after start)
  and below what a reader hand-timing a wash-in against a watch could notice
  at any rung.
- Size M: the clock read and a ring counter in `RunView`, a formatter in
  `app/formatting.py`, tests with a fake clock covering the threshold on both
  sides and the recovery, and a `docs/MODEL.md` paragraph beside the one
  `PL-SQJ1` wrote.

**Reopens `PL-SQJ1`'s recommendation** if the delivered rate measured on the
owner's own machine, with the script kept in `PL-SQJ1`'s brief, is under 99%.

**Done when.** A host that misses ticks shows the delivered rate beside the set
one, in the terms above, and a host that does not shows the plain label, both
held by tests with a fake clock; `docs/INTERFACE.md` § "Interface boundary" says
what the disclosure means.

**Checked 2026-11-22** against `d4e8200`: still applies. `RunView.step_tick` in `src/anesthesia_sim/app/run_view.py` reads no clock, and the module docstring of `src/anesthesia_sim/app/playback.py` still names this item as the guard that has not been built. One sentence of the design is out of date. Since #2180 (`PL-SZ6G`), each tick adds a fixed amount of owed simulated time and takes one one-second step for each whole second owed, so at 1x and 5x most ticks take no step. The time a tick adds is what never changes, not the steps per tick. The guard counts ticks, so the design still works. The paragraph it adds belongs in `docs/INTERFACE.md`, where #2109 moved the interface sections, and the done-when already names that file.

**Closed 2026-11-23.** `TickPace` in `src/anesthesia_sim/app/playback.py` measures the fraction of ticks that ran over the last 50, and `RunView.step_tick` records each tick's time from `time.monotonic`. Below 95% the clock line reads, for example, "about 240× of 300×", rounded to two significant figures, and it returns to the plain label at 97%. The 2-point deadband follows the alarm deadband practice described in the ISA's AutoQuiz on alarm deadband (https://blog.isa.org/autoquiz-alarm-deadband-setting) and in exida's summary of ISA-18.2 clause 10.5.5.2 (https://www.exida.com/Blog/why-should-i-use-an-alarm-deadband), both read in this session. Qt's documentation for `QTimer` (https://doc.qt.io/qt-6/qtimer.html) says that it emits one timeout for several that fell due while the application was busy, which is why late ticks are counted as lost. The measurement restarts on a pause, a hold, a start-over and a rate change. The 50-tick window and the 2 significant figures are stated in `docs/INTERFACE.md` § "What the reader chooses: traces, window and playback rate", and § "Interface boundary" now lists the measurement among what the interface may do. Files checked in the docs sweep: `docs/INTERFACE.md`, `docs/MODEL.md` (it says nothing about tick delivery, so nothing changed), `docs/VERIFICATION.md` (nothing about tick delivery), `README.md` (nothing), and the module docstrings of `app/playback.py` and `app/run_view.py`, which no longer call the guard unbuilt.

**Regression record.** On main at `5d07192e`, the recorded test fails before it reaches an assertion: `AttributeError: <module 'anesthesia_sim.app.run_view' ...> has no attribute 'monotonic'`, because the view read no clock. A variant that needs no new interface: on the same commit, `clock_playback_line(playback_rate_for(300))` returns `'300× real time'`, and that function takes no other argument, so the line could only ever state the set rate.
