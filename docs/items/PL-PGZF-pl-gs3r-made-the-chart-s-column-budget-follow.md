---
id: PL-PGZF
title: PL-GS3R made the chart's column budget follow the window width, so assemble_chart_frame costs 8.4 ms at 150 columns and 15.4 ms at 1601 - PL-CNCF measured only the fixed 150-column budget, and 15.4 ms is essentially a whole 60 fps frame
priority: P3
effort: M
status: ready
classes: perf
feature: chart-readout
touches: src/anesthesia_sim/app/chart_frame.py, docs/WORKING_NOTES.md
added: 2026-09-16
verify: grep -qF 'measured at the window-following budget' docs/WORKING_NOTES.md && python3 tools/doc_check.py check
---

**Problem.** PL-GS3R made the chart's column budget follow the window width, so assemble_chart_frame costs 8.4 ms at 150 columns and 15.4 ms at 1601 - PL-CNCF measured only the fixed 150-column budget, and 15.4 ms is essentially a whole 60 fps frame

**Where it was measured.** Incidentally, by `PL-3SQT`, which needed a frame
cost as the denominator for its numpy argument and is not otherwise about
this. These are its `assemble_chart_frame` figures - this item is now the only
place they are written down - best of three repeats of ten, one
20-minute sevoflurane run with one dial change, all six compartment traces
shown, `QT_QPA_PLATFORM=offscreen`, 4-core Xeon @ 2.80 GHz, Python 3.14.7:

| plot width | columns | drawn instants | `assemble_chart_frame` |
| --- | --- | --- | --- |
| 149 px | 150 | 102 | 8.39 ms |
| 900 px | 901 | 601 | 11.80 ms |
| 1600 px | 1601 | 1069 | 15.42 ms |

**Why it may be a finding rather than a number.** `PL-CNCF` measured
`controller.drawn_window` at 6.2 ms against the *fixed* 150-column budget;
`PL-GS3R` then made the budget `max(150, ceil(plot_width_px) + 1)`, so the
cost now follows the window and nothing has measured the top of that range.
A maximised window on a wide display is the ordinary case rather than the
pathological one.

**What this item is not.** It is not a claim that the interface drops frames:
this is assembly rather than paint, measured in a container with no GPU, and
the render cadence is not asserted here. `PL-R460` and `PL-CNCF` are the
neighbours; triage may well fold this into one of them rather than keep it.

**Why it matters.** The number is not the finding; the *gap in what is
measured* is. `PL-CNCF` measured `controller.drawn_window` at 6.2 ms against a
column budget that was a constant, and its figure is the one this project
quotes when it reasons about frame cost. `PL-GS3R` then made the budget
`max(150, ceil(plot_width_px) + 1)`, which turned a measured constant into an
unmeasured function of the window, and nobody measured the other end of it. A
maximised window on a wide display is the ordinary case rather than the
pathological one, so the quoted figure now describes the *narrowest* window a
learner will ever use.

Two consequences follow, and only the second is about speed. The first is
provenance: `docs/WORKING_NOTES.md`'s frame-cost thread is cited when the
chart's design is argued, and it is now silently about a tree whose budget
behaves differently. The second is that 15.4 ms of *assembly* leaves no margin
inside a 16.7 ms frame for the paint it precedes - but that is a hypothesis
here, not a measurement, because these figures are `QT_QPA_PLATFORM=offscreen`
on a 4-core container with no GPU.

**Triaged `P3`, and kept separate from `PL-CNCF` rather than folded in.** The
two name different functions in different modules - `controller.drawn_window`
in `app/controller.py` against `assemble_chart_frame` in `app/chart_frame.py` -
and `PL-CNCF` carries `docs/MODEL.md` and `core/run_score.py` in its `touches`
where this carries neither. Folding would make one item whose `verify:` cannot
speak for both halves. `PL-R460` is closed and is not a candidate at all.

**Done when.** The cost across the budget's actual range is written into
`docs/WORKING_NOTES.md` beside the existing frame-cost thread, carrying the
phrase `measured at the window-following budget` so the old fixed-budget
figures cannot be read as current, and the item closes on a recorded
conclusion about whether the margin is adequate. A recorded "it is" closes this
as legitimately as a speed-up would.

**What the environment decides, and what it does not.** The assembly half is
measurable anywhere - `assemble_chart_frame` imports no toolkit and the figures
in the table above were taken offscreen. What a container cannot settle is the
*margin*, because paint here is a software rasteriser with no GPU, which
`PL-QXSB` found reports 18-28 ms even for a frame where nothing changed. So a
session can take the numbers and state the assembly cost as fact; asserting
that the interface does or does not drop frames needs the project owner's own
hardware, as `PL-X9T3` did. Either is a legitimate close, provided the item
says which it did - this is deliberately not a requirement to reach real
hardware before closing.

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Partly overtaken, and one of its
framings is wrong.** `PL-ZG5J` closed 2026-09-19 and landed
`tests/benchmarks/frame_cost.py`, which measures a whole frame - assembly and
paint - at `WINDOW_WIDTH_PX = 1600`, the top of the budget this item said
nothing had measured: "advance 12.0 ms, present 15.3 ms, paint 13.1 ms, so the
interface costs 28.4 ms of a 40.4 ms frame". It measures `SimulationView.present`
rather than `assemble_chart_frame`, and takes no width argument, so it is one
point rather than the range.

What is left is the write-back: no figure for `assemble_chart_frame` across the
budget's range, and no margin conclusion, sits beside the fixed-budget thread
in `docs/WORKING_NOTES.md` - which still reads "150 columns" at `:1450`.

**Correction to the framing.** "15.4 ms is essentially a whole 60 fps frame …
no margin inside a 16.7 ms frame" does not describe this program:
`dashboard_frame.py:110` sets `RENDER_INTERVAL_S = 0.2`, a 200 ms render
budget, and that value landed with the Qt port the day before this was filed.
The brief disclaims asserting a cadence, so this is framing rather than a
premise - but re-derive the margin against 200 ms rather than 16.7 ms.
