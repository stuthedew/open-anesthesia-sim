---
id: PL-PGZF
title: PL-GS3R made the chart's column budget follow the window width, so assemble_chart_frame costs 8.4 ms at 150 columns and 15.4 ms at 1601 - PL-CNCF measured only the fixed 150-column budget, and 15.4 ms is essentially a whole 60 fps frame
status: untriaged
added: 2026-09-16
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
