---
id: PL-0Z35
title: Five app/ comments and docstrings state facts the code no longer bears out: qt_widgets' declare_interface_colours says only the agent selector and transport buttons are ever disabled (ForkPanel disables three more), qt_chart says a control mark is the only vertical line (gridlines and fork marks are vertical too) and that TraceLegend has three rows (it has four), theme's CONTROL_MARK_STROKE_WIDTH comment says it is finer than every reference stroke (all are 1.5), and chart_frame's CHART_COLUMN_BUDGET_PER_SERIES claims a bound by MAX_CHART_CONTROL_MARKS nobody has checked (found rewriting src/ prose for PL-1K5X)
priority: P3
effort: S
status: done
classes: docs
feature: stale-source-claims
touches: src/anesthesia_sim/app/qt_widgets.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/chart_frame.py
added: 2026-10-25
closed: 2026-10-25
pr: 1817
payoff: a contributor changing the chart's legend, strokes or disabled controls is told what the code does now, not what it did before
verify: ! grep -qF 'only controls that are ever disabled are the agent selector' src/anesthesia_sim/app/qt_widgets.py && ! grep -qF 'three legend rows' src/anesthesia_sim/app/qt_chart.py && ! grep -qF 'The mark is finer than either reference' src/anesthesia_sim/app/theme.py
---

**Problem.** Five app/ comments and docstrings state facts the code no longer bears out: qt_widgets' declare_interface_colours says only the agent selector and transport buttons are ever disabled (ForkPanel disables three more), qt_chart says a control mark is the only vertical line (gridlines and fork marks are vertical too) and that TraceLegend has three rows (it has four), theme's CONTROL_MARK_STROKE_WIDTH comment says it is finer than every reference stroke (all are 1.5), and chart_frame's CHART_COLUMN_BUDGET_PER_SERIES claims a bound by MAX_CHART_CONTROL_MARKS nobody has checked (found rewriting src/ prose for PL-1K5X)

**Reproduced 2026-10-25.** `grep` on `main` at `b6ff4443` finds three of the five claims as filed: `qt_widgets.py` line 303 ("only controls that are ever disabled are the agent selector"), `qt_chart.py` line 1723 ("The chart's three legend rows") and `theme.py` line 445 ("The mark is finer than either reference"). The other two are in the comments above `_VERTICAL_LINE_ANGLE_DEG` and `CHART_COLUMN_BUDGET_PER_SERIES`.

**Why it matters.** A contributor changing which controls can be disabled, or the chart's legend or strokes, reads these comments as the record of what holds now. `declare_interface_colours` is part of how disabled controls stay legible (`.claude/rules/ui-color.md`), so a false list of disabled controls points the next change at the wrong widgets.

**Done when.** Each of the five statements is true of the code or is removed. Where the bound in `CHART_COLUMN_BUDGET_PER_SERIES`'s comment cannot be shown, the comment says it is unmeasured. No behaviour changes.

**Fixed 2026-10-25.** Four of the five claims were corrected. The fifth, the
vertical-line comment above `_VERTICAL_LINE_ANGLE_DEG`, already named
gridlines, control marks and fork marks on `main`, so it needed no change. The
claim about `CHART_COLUMN_BUDGET_PER_SERIES` was measurably false rather than
unmeasured: `RunDefinition._anchored_columns` adds one event column for every
setting change inside the window, and `MAX_CHART_CONTROL_MARKS` caps only the
marks drawn. The comment now says so. The comment above `LEGEND_SWATCH_WIDTH`
in `app/theme.py` repeated the stale count of three legend rows and named a
function that no longer exists, `_build_band_legend_item`. It now says four
rows and names `_BandSwatch`.
