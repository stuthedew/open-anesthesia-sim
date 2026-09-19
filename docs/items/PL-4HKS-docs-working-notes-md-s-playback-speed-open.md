---
id: PL-4HKS
title: docs/WORKING_NOTES.md's playback-speed open thread reasons from pre-Qt-port numbers - a 0.011 ms step and 15 ms of chart-point construction - and names PL-010 as unspent headroom, but PL-009 is dropped, PL-010 is done, and the step now costs 0.025 ms
status: untriaged
feature: frame-cost-harness
added: 2026-09-19
---

**Problem.** docs/WORKING_NOTES.md's playback-speed open thread reasons from pre-Qt-port numbers - a 0.011 ms step and 15 ms of chart-point construction - and names PL-010 as unspent headroom, but PL-009 is dropped, PL-010 is done, and the step now costs 0.025 ms

**Why it matters.** `ROADMAP.md` still wants a playback multiplier, and this
section is the only place the project records what one would *cost*. Every
number in it predates the Qt port and one predates `PL-R460`'s exact
propagator, so a scoping round that reads it would size the feature against a
toolkit and a solver that are both gone - and it would reach the wrong
conclusion in the direction nobody checks, because the recorded step is 2.3x
cheaper than the real one and the recorded bottleneck no longer exists.

Four specific statements, found while closing `PL-V1F4`:

- **"Stepping the model is nearly free (~0.011 ms per step, flat)."** Measured
  2026-09-19 in the web container: 14.86 ms for 600 `controller.advance`
  calls, so 0.025 ms per step. `PL-R460` is why - v0.4.23 took the exact step
  at ~27 us against the split's ~18 us - so the figure is stale for a recorded
  reason rather than a mysterious one.
- **"A frame currently costs ~17 ms of which ~15 ms is chart-point
  construction."** Chart-point construction was Flet's per-point control
  objects, which the port removed. Measured the same day on an hour-warmed run
  at 300x: `SimulationView.present(False)` 18.8 ms and
  `QApplication.processEvents()` 15.5 ms, so a frame costs 34.3 ms and the
  paint is 45% of it.
- **"PL-010 (point reuse, measured 20x cheaper) is the headroom to spend."**
  `PL-010` closed `done`. There is no headroom there to spend.
- **The heading names `PL-009`, which is `dropped`.** An "Open thread" section
  whose item is closed is the one shape a reader cannot distinguish from live
  work.

**First step.** Decide whether the section is rewritten against current numbers
or removed. `PL-009` being dropped argues for removal; `ROADMAP.md` still
wanting the feature argues for a rewrite. Whoever lands `PL-ZG5J`'s harness
gets the numbers for the rewrite for free, which is why both carry
`feature: frame-cost-harness`.

**Done when.** `docs/WORKING_NOTES.md` no longer states a frame cost, a
per-step cost or an available optimization that the Qt port or a closed item
has overtaken, and its playback-speed section either cites a live item or is
gone.

**The numbers this rewrite needs now come from one command** (`PL-ZG5J`,
closed 2026-09-19). `uv run python tests/benchmarks/frame_cost.py` prints the
frame split for any rate on the interface's ladder in about three seconds, so
the section can cite a measurement a reader can reproduce rather than a figure
copied out of an item. On this container at 300x, medians over three runs:
`advance` 12.0 ms for the frame's 600 steps - 0.020 ms a step - `present`
15.3 ms and the paint 13.1 ms, for a 40.4 ms frame against the 200 ms render
budget. Note what that does to the section's argument as well as to its
figures: the pre-port thread treats chart-point construction as the cost to
attack, and under Qt the interface's 28.4 ms is split roughly evenly between
assembling the frame and painting it, so headroom found in one half buys half
of what the old reasoning assumed.
