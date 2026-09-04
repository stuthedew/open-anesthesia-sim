---
id: PL-CG7J
title: Add per-trace show/hide controls to the chart, as Gas Man has
status: ready
priority: P2
effort: S
classes: ux
feature: teachable-case
verify: uv run pytest tests/unit/test_simulation_view.py && grep -q 'def test_a_hidden_trace_is_not_drawn' tests/unit/test_simulation_view.py
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/chart_series.py
added: 2026-09-04
---

**Problem.** Gas Man's graph pane carries a checkbox per trace — CKT(I),
ALV(A), VRG(R), MUS(M), FAT(F) — so a learner can isolate one compartment or
compare two. The project owner's reference screenshot (2026-09-04) shows all
five checked; the point is that they need not be. This simulator draws all
six traces unconditionally, with no way to look at one.

**Why it matters, twice over.**

*Educationally*, it is the difference between a chart that shows everything
and one that answers a question. "Why does fat lag muscle" is a two-trace
comparison, and it is unreadable against four other lines crossing it. This
is the reference implementation's own affordance, not an invention.

*And it is the largest lever on render cost that does not trade fidelity.*
PL-Q197 established that what reaches the client each frame is about two
patch operations per drawn point whose chosen sample moved, and PL-YDKJ
measured that no transport inside Flet avoids that. Cost is therefore linear
in the number of traces drawn: a learner looking at two compartments instead
of six cuts it by a factor of three, and every other lever — fewer points, a
coarser bucket — costs resolution. This one costs nothing, because a trace
nobody is looking at is not a fidelity loss.

**Where.** `simulation_view.py` owns the `_plotted_series` table pairing each
trace to the quantity it draws, and that table is the natural place to filter:
`chart_series.redraw_visible_window` already takes the sequence of pairs to
redraw, so a hidden trace is one that is not passed. Removing it from the
chart's own series list is what stops the client holding its points at all —
leaving it in place with zero points would keep the control and redraw it
empty, which is a different and worse thing.

**Care needed.** The trace-to-compartment pairing is a
presentation-correctness property that
`test_chart_traces_stay_bound_to_their_own_compartment` holds, and filtering
the table is exactly the operation that could break it — a filter that
reorders or misaligns would draw one compartment's values on another's line.
The filter must preserve pairing, and the test must cover the filtered case.
A hidden trace must also disappear from any legend, so the chart never labels
a line it is not drawing.

**Done when.** Each of the six traces can be shown or hidden, hiding one
removes its points from the client rather than blanking them, the pairing
test covers a filtered table, and the legend agrees with what is drawn.
