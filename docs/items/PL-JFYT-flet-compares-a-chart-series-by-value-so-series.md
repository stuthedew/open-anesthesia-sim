---
id: PL-JFYT
title: Flet compares a chart series by value, so 'series in chart.data_series' and list.index answer for the first of an equal pair - invisible while one run drew each compartment once
status: untriaged
added: 2026-09-14
---

**Problem.** Flet compares a chart series by value, so 'series in chart.data_series' and list.index answer for the first of an equal pair - invisible while one run drew each compartment once

Found while building `PL-B9PY`'s two-run tests, 2026-09-14. Two `RunView`s
drawing the same recorded history produce two `fch.LineChartData` objects with
identical points, and `list.index` returned the *same* index for both, so an
assertion about the drawing order read as "these two lines are at the same
position" rather than failing loudly. The tests were rewritten to compare by
`id()`; nothing in the shipped code searches the list by value today.

**Why it matters.** It is a silent-wrong-answer shape rather than a crash. Any
`series in chart.data_series` test passes as soon as *some* equal series is on
the chart, which is exactly the assertion a reviewer would read as "this run's
line is drawn". Several tests already written that way were correct only
because one run drew each compartment exactly once, so no two series were ever
equal - a property this decomposition removes. `PL-8PSW` (overlay two branches
on one time axis) is the item that will make two-run drawing routine, so this
is worth settling before the assertions multiply.

**Where.** `tests/unit/test_simulation_view.py`, wherever a series is looked
for in `_concentration_chart.data_series` or `_wash_in_chart.data_series`;
`src/anesthesia_sim/app/simulation_view.py`'s `_chart_data_series` and
`_wash_in_chart_data_series` are what build the lists.

**Measured, so this is not a guess.** Against the shipped `flet-charts`,
`fch.LineChartData` is a dataclass and carries a generated
`LineChartData.__eq__` - `dataclasses.is_dataclass` is true and
`type(series).__eq__.__qualname__` is `LineChartData.__eq__`, over
`flet.controls.base_control.BaseControl` and `object`. Two freshly built
series with the same colour and stroke width compare equal while not being
identical, and `[a, b].index(b)` returns `0`.

**Open question.** Whether the right answer is a test helper that searches by
identity, a note in `chart_series.py` that a chart series must never be looked
up by value, or both - and whether the same hazard reaches the *other* Flet
control lists a frame assembles.

**Done when.** No assertion in the view tests can pass because a *different*
run's line happened to be equal to the one it asked about, and the reason is
recorded where the next person writing such an assertion will read it.
