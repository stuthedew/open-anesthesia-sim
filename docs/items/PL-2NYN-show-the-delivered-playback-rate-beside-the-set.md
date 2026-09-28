---
id: PL-2NYN
title: Show the delivered playback rate beside the set one when fewer than 95% of ticks fire over a trailing 50-tick window, so a host that cannot service the 100 ms tick is disclosed on screen
priority: P3
effort: M
status: ready
classes: feature
feature: presentation-safety
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_formatting.py, tests/integration/test_qt_widgets.py, docs/MODEL.md
added: 2026-09-27
payoff: a learner on a host that cannot keep the 100 ms tick sees the rate the clock actually runs at, not a label it is not meeting
verify: grep -q 'def test_the_rate_text_names_the_delivered_rate_below_95_percent_of_ticks' tests/unit/test_formatting.py
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
held by tests with a fake clock; `docs/MODEL.md` § "Interface boundary" says
what the disclosure means.
