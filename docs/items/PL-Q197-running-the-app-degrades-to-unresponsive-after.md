---
id: PL-Q197
title: Running the app degrades to unresponsive after about a minute: sliders move but stop updating values
status: untriaged
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/main.py, src/anesthesia_sim/app/chart_series.py
added: 2026-09-04
---

**Problem.** Reported by the project owner, 2026-09-04, running `make run`
(`uv run anesthesia-sim`) on their local terminal. On a fresh launch the app
behaves: sliders move and the value beside each one updates as it moves. Over
roughly a minute of runtime the app becomes progressively laggy, and by about
one minute in it stops responding to input. The process does not crash or
hang — the simulation keeps advancing, but at a crawl. Sliders still move
under the pointer at that point, and their associated value readouts no longer
update.

Two symptoms that may or may not be one fault, and separating them is the
first job:

- **Progressive slowdown.** Frame/tick rate falls off continuously with
  runtime rather than stepping down at a threshold — consistent with something
  accumulating per tick (chart series history, control/event lists, retained
  Flet controls, or an unbounded redraw whose cost is proportional to elapsed
  simulation time) rather than with a fixed cost.
- **Input stops taking effect.** The slider still moves (that is Flet's own
  client-side drag) but its bound value stops updating, which points at the
  change handler either not being dispatched or being starved behind queued UI
  work, rather than at the slider itself.

**Why it matters.** The app becomes unusable within a minute of a session
starting, which is shorter than any teaching case. It also crosses the
safety-critical presentation line: a slider whose position no longer matches
the value driving the model shows a control setting the simulation is not
using, which is a displayed value that misrepresents simulation state. A user
would reasonably read the slider position as the current setting.

**Where.** Not yet diagnosed — no investigation was run in the capture
session. Starting points, in order:

1. `src/anesthesia_sim/app/simulation_view.py` — the tick/update loop, what it
   calls `update()` on per tick, and whether the whole view or only changed
   controls are repainted.
2. `src/anesthesia_sim/app/chart_series.py` — whether plotted history is
   bounded or grows without limit, and whether the full series is rebuilt and
   re-sent each tick.
3. `src/anesthesia_sim/app/main.py` — timer/async scheduling, and whether ticks
   can overlap or queue up when one runs long.

Worth measuring before changing anything: wall-clock per tick against elapsed
runtime, and the number of retained data points and Flet controls at 10s / 30s
/ 60s. A linear or quadratic curve there names the cause directly.

**Done when.** The app sustains input responsiveness and its target tick rate
over a run long enough to cover a teaching case, with a regression test that
would have caught the growth — a bound on retained series length and per-tick
work that a test can assert without a GUI, since the degradation is in the
app layer rather than in `core/`.
