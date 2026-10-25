---
id: PL-0Z35
title: Five app/ comments and docstrings state facts the code no longer bears out: qt_widgets' declare_interface_colours says only the agent selector and transport buttons are ever disabled (ForkPanel disables three more), qt_chart says a control mark is the only vertical line (gridlines and fork marks are vertical too) and that TraceLegend has three rows (it has four), theme's CONTROL_MARK_STROKE_WIDTH comment says it is finer than every reference stroke (all are 1.5), and chart_frame's CHART_COLUMN_BUDGET_PER_SERIES claims a bound by MAX_CHART_CONTROL_MARKS nobody has checked (found rewriting src/ prose for PL-1K5X)
status: untriaged
feature: stale-source-claims
added: 2026-10-25
---

**Problem.** Five app/ comments and docstrings state facts the code no longer bears out: qt_widgets' declare_interface_colours says only the agent selector and transport buttons are ever disabled (ForkPanel disables three more), qt_chart says a control mark is the only vertical line (gridlines and fork marks are vertical too) and that TraceLegend has three rows (it has four), theme's CONTROL_MARK_STROKE_WIDTH comment says it is finer than every reference stroke (all are 1.5), and chart_frame's CHART_COLUMN_BUDGET_PER_SERIES claims a bound by MAX_CHART_CONTROL_MARKS nobody has checked (found rewriting src/ prose for PL-1K5X)
